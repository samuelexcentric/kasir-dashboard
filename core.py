"""Pure business logic – no Streamlit, no DB, no I/O."""
from datetime import datetime, timedelta
from typing import Any

SHIFTS = [
    ("Malam", 0, 8),
    ("Pagi", 8, 16),
    ("Siang", 16, 24),
]


def shift_aktif(dt: datetime) -> str:
    h = dt.hour
    for name, start, end in SHIFTS:
        if start <= h < end:
            return name
    return "Malam"  


def sisa_waktu_shift(mulai: datetime, sekarang: datetime | None = None) -> timedelta:
    if sekarang is None:
        sekarang = mulai
    for name, start, end in SHIFTS:
        if start <= mulai.hour < end:
            target_date = sekarang.date()
            if end == 24:
                target_date += timedelta(days=1)
                target_hour = 0
            else:
                target_hour = end
            
            finish = datetime.combine(target_date, datetime.min.time()).replace(hour=target_hour)
            
            if end < start and sekarang.hour >= start:
                finish += timedelta(days=1)
                
            return max(finish - sekarang, timedelta(0))
    return timedelta(0)


def shift_habis(mulai: datetime, sekarang: datetime | None = None) -> bool:
    return sisa_waktu_shift(mulai, sekarang) == timedelta(0)


def notifikasi_pulang(mulai: datetime, sekarang: datetime | None = None) -> str:
    name = shift_aktif(mulai)
    return (
        f"⏰ Shift {name} Anda telah habis. "
        "Silakan boleh pulang, lakukan handover kasir, dan ganti shift."
    )


def omzet_per_shift(transaksi: list[dict], tanggal: str) -> dict[str, int]:
    out = {"Malam": 0, "Pagi": 0, "Siang": 0}
    for t in transaksi:
        dt = datetime.strptime(t["tanggal_waktu"], "%Y-%m-%d %H:%M:%S")
        if dt.strftime("%Y-%m-%d") != tanggal:
            continue
        out[shift_aktif(dt)] += int(t["total_bayar"])
    return out


def hitung_hpp(detail: list[dict], produk: dict[str, dict]) -> int:
    total = 0
    for d in detail:
        p = produk.get(d["id_produk"])
        if p:
            total += int(p["harga_beli"]) * int(d["jumlah"])
    return total


def hitung_laba_kotor(omzet: int, hpp: int) -> int:
    return omzet - hpp


def hitung_laba_bersih(laba_kotor: int, biaya_op: int) -> int:
    return laba_kotor - biaya_op


def biaya_operasional(biaya: list[dict]) -> int:
    return sum(int(b["jumlah"]) for b in biaya if b["kategori"] != "Modal Awal")


def modal_awal(biaya: list[dict]) -> int:
    return sum(int(b["jumlah"]) for b in biaya if b["kategori"] == "Modal Awal")


def ringkasan_keuangan(
    omzet: int,
    detail: list[dict],
    produk: dict[str, dict],
    biaya: list[dict],
) -> dict[str, Any]:
    h = hitung_hpp(detail, produk)
    lk = hitung_laba_kotor(omzet, h)
    op = biaya_operasional(biaya)
    ma = modal_awal(biaya)
    lb = hitung_laba_bersih(lk, op)
    return {
        "omzet": omzet,
        "hpp": h,
        "laba_kotor": lk,
        "biaya_operasional": op,
        "modal_awal": ma,
        "laba_bersih": lb,
    }


STOK_LABELS = ["Aman", "Menipis", "Kritis"]


def stok_status(stok: int, min_stok: int) -> str:
    if stok > min_stok:
        return STOK_LABELS[0]
    if stok > 0:
        return STOK_LABELS[1]
    return STOK_LABELS[2]


def produk_perlu_restock(produk: list[dict]) -> list[dict]:
    """Return items where stok <= min_stok, sorted by stok ascending."""
    out = [p for p in produk if int(p["stok"]) <= int(p["min_stok"])]
    out.sort(key=lambda x: int(x["stok"]))
    return out


def pesan_whatsapp_restock(produk_restock: list[dict]) -> str:
    lines = [f"Stok menipis / habis:"]
    for p in produk_restock:
        lines.append(
            f"- {p['nama_produk']} ({p['id_produk']}): "
            f"sisa {p['stok']} (min {p['min_stok']})"
        )
    return "\n".join(lines)
