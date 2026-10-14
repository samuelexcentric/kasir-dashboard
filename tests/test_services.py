"""Data-access layer tests: transaksi insert, stock sync, CSV <-> DB roundtrip."""
from pathlib import Path

import pytest

import db_init
import services


@pytest.fixture
def fresh(tmp_path, monkeypatch):
    """Throwaway copy of data/ + database for each test."""
    import shutil

    src_data = Path(__file__).resolve().parent.parent / "data"
    data = tmp_path / "data"
    shutil.copytree(src_data, data)
    monkeypatch.setattr(db_init, "DATA_DIR", data)
    monkeypatch.setattr(db_init, "DB_PATH", tmp_path / "test.db")
    monkeypatch.setattr(services, "DATA_DIR", data)
    db_init.import_csv_to_db(reset=True)
    return data


def test_load_all_returns_five_tables(fresh):
    data = services.load_all()
    assert set(data) == {"produk", "kasir", "transaksi", "detail_transaksi", "biaya"}
    assert len(data["produk"]) == 50
    assert len(data["transaksi"]) == 250


def test_login_accepts_correct_password(fresh):
    user = services.login("admin", "admin123")
    assert user is not None
    assert user["role"] == "admin"
    assert "password_hash" not in user


def test_login_rejects_wrong_password(fresh):
    assert services.login("admin", "salah") is None
    assert services.login("tidakada", "apapun") is None


def test_buat_transaksi_appends_to_db_and_csv(fresh):
    before_trx = len(services.load_all()["transaksi"])
    before_dtl = len(services.load_all()["detail_transaksi"])

    result = services.buat_transaksi(
        id_kasir="KSR001",
        items=[{"id_produk": "P001", "jumlah": 2}],
        metode="Tunai",
        waktu="2026-10-07 10:00:00",
    )

    data = services.load_all()
    assert len(data["transaksi"]) == before_trx + 1
    assert len(data["detail_transaksi"]) == before_dtl + 1
    assert result["id_transaksi"] in set(data["transaksi"]["id_transaksi"])
    assert result["total_bayar"] == 2 * 3500


def test_buat_transaksi_decrements_stock(fresh):
    stok_before = int(services.load_all()["produk"].set_index("id_produk").loc["P001", "stok"])
    services.buat_transaksi(
        id_kasir="KSR001",
        items=[{"id_produk": "P001", "jumlah": 3}],
        metode="QRIS",
        waktu="2026-10-07 10:00:00",
    )
    stok_after = int(services.load_all()["produk"].set_index("id_produk").loc["P001", "stok"])
    assert stok_after == stok_before - 3


def test_buat_transaksi_rejects_insufficient_stock(fresh):
    with pytest.raises(ValueError, match="stok"):
        services.buat_transaksi(
            id_kasir="KSR001",
            items=[{"id_produk": "P001", "jumlah": 99999}],
            metode="Tunai",
            waktu="2026-10-07 10:00:00",
        )


def test_buat_transaksi_rejects_unknown_product(fresh):
    with pytest.raises(ValueError, match="produk"):
        services.buat_transaksi(
            id_kasir="KSR001",
            items=[{"id_produk": "P999", "jumlah": 1}],
            metode="Tunai",
            waktu="2026-10-07 10:00:00",
        )


def test_buat_transaksi_supports_multiple_items(fresh):
    result = services.buat_transaksi(
        id_kasir="KSR002",
        items=[
            {"id_produk": "P001", "jumlah": 2},
            {"id_produk": "P002", "jumlah": 1},
        ],
        metode="Debit",
        waktu="2026-10-07 11:00:00",
    )
    assert result["total_bayar"] == 2 * 3500 + 1 * 6000
    assert len(result["detail"]) == 2


def test_tambah_biaya_persists(fresh):
    n_before = len(services.load_all()["biaya"])
    services.tambah_biaya("2026-10-07", "Listrik", "Token", 100_000)
    data = services.load_all()
    assert len(data["biaya"]) == n_before + 1
    row = data["biaya"].iloc[-1]
    assert row["kategori"] == "Listrik" and int(row["jumlah"]) == 100_000


def test_csv_edit_reflected_in_load(fresh):
    """CSV -> web: editing CSV changes what the app reads after reload."""
    path = fresh / "produk.csv"
    text = path.read_text(encoding="utf-8").replace(
        "P001,Indomie Goreng,Makanan,2800,3500,100,10",
        "P001,Indomie Goreng,Makanan,2800,3500,777,10",
    )
    path.write_text(text, encoding="utf-8")
    stok = int(services.load_all()["produk"].set_index("id_produk").loc["P001", "stok"])
    assert stok == 777


def test_ringkasan_finansial_matches_core(fresh):
    data = services.load_all()
    ring = services.ringkasan_finansial(data)
    assert ring["omzet"] == int(data["transaksi"]["total_bayar"].sum())
    assert ring["laba_bersih"] == ring["laba_kotor"] - ring["biaya_operasional"]
    assert ring["modal_awal"] == 5_000_000


def test_update_stok_writes_new_level(fresh):
    hasil = services.update_stok({"P001": 0})
    assert hasil["diubah"] == 1
    assert hasil["detail"][0]["stok_baru"] == 0
    stok = int(services.load_all()["produk"].set_index("id_produk").loc["P001", "stok"])
    assert stok == 0


def test_update_stok_reports_no_change_for_same_value(fresh):
    stok_lama = int(
        services.load_all()["produk"].set_index("id_produk").loc["P001", "stok"]
    )
    hasil = services.update_stok({"P001": stok_lama})
    assert hasil["diubah"] == 0


def test_update_stok_rejects_unknown_product(fresh):
    with pytest.raises(ValueError, match="produk"):
        services.update_stok({"P999": 5})


def test_update_stok_rejects_negative(fresh):
    with pytest.raises(ValueError, match="negatif"):
        services.update_stok({"P001": -1})


def test_update_stok_multiple_products(fresh):
    hasil = services.update_stok({"P001": 3, "P002": 4})
    assert hasil["diubah"] == 2
    data = services.load_all()["produk"].set_index("id_produk")
    assert int(data.loc["P001", "stok"]) == 3
    assert int(data.loc["P002", "stok"]) == 4


def test_update_stok_empty_is_noop(fresh):
    assert services.update_stok({}) == {"diubah": 0, "detail": []}