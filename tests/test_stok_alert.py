"""Pure logic for out-of-stock detection and alert de-duplication."""
import core


def test_produk_stok_habis_only_returns_zero_stock():
    produk = [
        {"id_produk": "P001", "nama_produk": "A", "stok": 0, "min_stok": 10},
        {"id_produk": "P002", "nama_produk": "B", "stok": 3, "min_stok": 10},
        {"id_produk": "P003", "nama_produk": "C", "stok": 0, "min_stok": 5},
    ]
    habis = core.produk_stok_habis(produk)
    assert [p["id_produk"] for p in habis] == ["P001", "P003"]


def test_produk_stok_habis_handles_string_numbers():
    produk = [{"id_produk": "P001", "nama_produk": "A", "stok": "0", "min_stok": "10"}]
    assert len(core.produk_stok_habis(produk)) == 1


def test_produk_baru_habis_filters_already_notified():
    produk = [
        {"id_produk": "P001", "nama_produk": "A", "stok": 0, "min_stok": 10},
        {"id_produk": "P002", "nama_produk": "B", "stok": 0, "min_stok": 10},
    ]
    baru = core.produk_baru_habis(produk, sudah_dinotifikasi={"P001"})
    assert [p["id_produk"] for p in baru] == ["P002"]


def test_produk_baru_habis_returns_empty_when_all_notified():
    produk = [{"id_produk": "P001", "nama_produk": "A", "stok": 0, "min_stok": 10}]
    assert core.produk_baru_habis(produk, sudah_dinotifikasi={"P001"}) == []


def test_produk_baru_habis_without_history_returns_all():
    produk = [{"id_produk": "P001", "nama_produk": "A", "stok": 0, "min_stok": 10}]
    assert len(core.produk_baru_habis(produk)) == 1
