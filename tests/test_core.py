"""Core business-logic tests: finance, stock alerts, shift schedule."""
from datetime import datetime, timedelta

import pytest

import core


def test_hpp_sums_cost_of_goods_sold():
    detail = [
        {"id_produk": "P001", "jumlah": 2},
        {"id_produk": "P002", "jumlah": 1},
    ]
    produk = {"P001": {"harga_beli": 2800}, "P002": {"harga_beli": 4000}}
    assert core.hitung_hpp(detail, produk) == 2 * 2800 + 4000


def test_laba_kotor_is_omzet_minus_hpp():
    assert core.hitung_laba_kotor(13000, 9600) == 3400


def test_laba_bersih_subtracts_operational_costs():
    assert core.hitung_laba_bersih(3400, 2000) == 1400


def test_biaya_operasional_excludes_modal_awal():
    biaya = [
        {"kategori": "Modal Awal", "jumlah": 5_000_000},
        {"kategori": "Listrik", "jumlah": 200_000},
        {"kategori": "Gaji", "jumlah": 150_000},
    ]
    assert core.biaya_operasional(biaya) == 350_000


def test_modal_awal_isolated():
    biaya = [
        {"kategori": "Modal Awal", "jumlah": 5_000_000},
        {"kategori": "Listrik", "jumlah": 200_000},
    ]
    assert core.modal_awal(biaya) == 5_000_000


def test_modal_awal_not_subtracted_repeatedly():
    """laba bersih = omzet - HPP - biaya op; modal awal must not appear twice."""
    laba = core.ringkasan_keuangan(
        omzet=1_000_000,
        detail=[{"id_produk": "P001", "jumlah": 10}],
        produk={"P001": {"harga_beli": 50_000}},
        biaya=[{"kategori": "Modal Awal", "jumlah": 5_000_000},
               {"kategori": "Listrik", "jumlah": 100_000}],
    )
    assert laba["hpp"] == 500_000
    assert laba["laba_kotor"] == 500_000
    assert laba["biaya_operasional"] == 100_000
    assert laba["laba_bersih"] == 400_000
    assert laba["modal_awal"] == 5_000_000


@pytest.mark.parametrize(
    "stok,min_stok,expected",
    [
        (100, 10, "Aman"),
        (11, 10, "Aman"),
        (10, 10, "Menipis"),
        (5, 10, "Menipis"),
        (0, 10, "Kritis"),
    ],
)
def test_stok_status(stok, min_stok, expected):
    assert core.stok_status(stok, min_stok) == expected


def test_produk_perlu_restock_returns_low_items_sorted():
    produk = [
        {"id_produk": "P001", "nama_produk": "Kaos", "stok": 4, "min_stok": 10},
        {"id_produk": "P002", "nama_produk": "Topi", "stok": 50, "min_stok": 10},
        {"id_produk": "P003", "nama_produk": "Sandal", "stok": 0, "min_stok": 25},
    ]
    out = core.produk_perlu_restock(produk)
    assert [p["id_produk"] for p in out] == ["P003", "P001"]
    assert all(p["stok"] <= p["min_stok"] for p in out)


def test_pesan_whatsapp_mentions_products_and_quantity():
    produk = [{"id_produk": "P003", "nama_produk": "Sandal", "stok": 0, "min_stok": 25}]
    msg = core.pesan_whatsapp_restock(produk)
    assert "Sandal" in msg
    assert "0" in msg and "25" in msg


@pytest.mark.parametrize(
    "hour,expected",
    [
        (0, "Malam"), (7, "Malam"),
        (8, "Pagi"), (15, "Pagi"),
        (16, "Siang"), (23, "Siang"),
    ],
)
def test_shift_aktif(hour, expected):
    assert core.shift_aktif(datetime(2026, 10, 6, hour, 30)) == expected


def test_every_shift_is_exactly_8_hours():
    for name, start, end in core.SHIFTS:
        assert (end - start) % 24 == 8, f"{name} not 8 hours"


@pytest.mark.parametrize(
    "start_hour,now_hour,expected_hours",
    [
        (8, 8, 8),
        (8, 14, 2),
        (0, 3, 5),
        (16, 23, 1),
    ],
)
def test_sisa_waktu_shift(start_hour, now_hour, expected_hours):
    mulai = datetime(2026, 10, 6, start_hour, 0)
    sekarang = datetime(2026, 10, 6, now_hour, 0)
    assert core.sisa_waktu_shift(mulai, sekarang) == timedelta(hours=expected_hours)


def test_shift_habis_after_8_hours():
    mulai = datetime(2026, 10, 6, 8, 0)
    assert core.shift_habis(mulai, datetime(2026, 10, 6, 15, 59)) is False
    assert core.shift_habis(mulai, datetime(2026, 10, 6, 16, 0)) is True


def test_notifikasi_pulang_names_the_finished_shift():
    mulai = datetime(2026, 10, 6, 8, 0)
    sekarang = datetime(2026, 10, 6, 16, 0)
    msg = core.notifikasi_pulang(mulai, sekarang)
    assert "Pagi" in msg
    assert "pulang" in msg.lower()


def test_total_omzet_per_shift():
    transaksi = [
        {"tanggal_waktu": "2026-10-06 09:00:00", "total_bayar": 10000},
        {"tanggal_waktu": "2026-10-06 15:59:00", "total_bayar": 5000},
        {"tanggal_waktu": "2026-10-06 16:00:00", "total_bayar": 7000},
        {"tanggal_waktu": "2026-10-06 02:00:00", "total_bayar": 3000},
    ]
    out = core.omzet_per_shift(transaksi, "2026-10-06")
    assert out["Pagi"] == 15000
    assert out["Siang"] == 7000
    assert out["Malam"] == 3000
