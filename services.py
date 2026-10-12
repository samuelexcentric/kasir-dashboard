"""Data-access layer: thin wrapper around db_init + pandas for UI."""
from pathlib import Path
import pandas as pd
import db_init

DATA_DIR = Path(__file__).resolve().parent / "data"


def _reload():
    """Ensure DB reflects CSV and CSV reflects DB (no password hash leak)."""
    db_init.import_csv_to_db(reset=False)
    db_init.export_db_to_csv()


def load_all() -> dict[str, pd.DataFrame]:
    _reload()
    return {
        "produk": pd.read_csv(DATA_DIR / "produk.csv"),
        "kasir": pd.read_csv(DATA_DIR / "kasir.csv"),
        "transaksi": pd.read_csv(DATA_DIR / "transaksi.csv"),
        "detail_transaksi": pd.read_csv(DATA_DIR / "detail_transaksi.csv"),
        "biaya": pd.read_csv(DATA_DIR / "biaya.csv"),
    }


def login(username: str, password: str):
    df = pd.read_csv(DATA_DIR / "kasir.csv")
    row = df[df["username"] == username]
    if row.empty:
        return None
    db_init.import_csv_to_db(reset=False)
    conn = db_init.connect()
    cur = conn.execute(
        "SELECT password_hash FROM kasir WHERE username = ?", (username,)
    )
    hash_row = cur.fetchone()
    conn.close()
    if hash_row and db_init.verify_password(password, hash_row["password_hash"]):
        return {
            "id_kasir": row.iloc[0]["id_kasir"],
            "nama": row.iloc[0]["nama"],
            "username": row.iloc[0]["username"],
            "role": row.iloc[0]["role"],
        }
    return None


def buat_transaksi(
    id_kasir: str,
    items: list[dict],
    metode: str,
    waktu: str,
) -> dict:
    """Create a transaction with one or more items.
    items: [{'id_produk': str, 'jumlah': int}, ...]
    Returns dict with transaction id, total, and detail list.
    """
    _reload()
    produk_df = pd.read_csv(DATA_DIR / "produk.csv")
    transaksi_df = pd.read_csv(DATA_DIR / "transaksi.csv")
    detail_df = pd.read_csv(DATA_DIR / "detail_transaksi.csv")

    for it in items:
        pid = it["id_produk"]
        qty = it["jumlah"]
        if pid not in set(produk_df["id_produk"]):
            raise ValueError(f"produk {pid} tidak ditemukan")
        stock = int(
            produk_df.loc[produk_df["id_produk"] == pid, "stok"].iloc[0]
        )
        if stock < qty:
            raise ValueError(f"stok tidak cukup untuk produk {pid}")

    new_trx_id = f"TRX{len(transaksi_df)+1:03d}"
    detail_start = len(detail_df) + 1
    total = 0
    detail_rows = []
    for idx, it in enumerate(items):
        pid = it["id_produk"]
        qty = it["jumlah"]
        price = int(
            produk_df.loc[produk_df["id_produk"] == pid, "harga_jual"].iloc[0]
        )
        subtotal = price * qty
        total += subtotal
        detail_rows.append(
            {
                "id_detail": f"DTL{detail_start+idx:03d}",
                "id_transaksi": new_trx_id,
                "id_produk": pid,
                "jumlah": qty,
                "harga_satuan": price,
                "subtotal": subtotal,
            }
        )

    new_trx = pd.DataFrame(
        {
            "id_transaksi": [new_trx_id],
            "tanggal_waktu": [waktu],
            "id_kasir": [id_kasir],
            "metode_pembayaran": [metode],
            "total_bayar": [total],
        }
    )
    new_trx.to_csv(DATA_DIR / "transaksi.csv", mode="a", header=False, index=False)
    pd.DataFrame(detail_rows).to_csv(
        DATA_DIR / "detail_transaksi.csv", mode="a", header=False, index=False
    )

    for it in items:
        pid = it["id_produk"]
        qty = it["jumlah"]
        mask = produk_df["id_produk"] == pid
        produk_df.loc[mask, "stok"] = (
            produk_df.loc[mask, "stok"].astype(int) - qty
        )
    produk_df.to_csv(DATA_DIR / "produk.csv", index=False)

    return {
        "id_transaksi": new_trx_id,
        "total_bayar": total,
        "detail": detail_rows,
    }


def tambah_biaya(tanggal: str, kategori: str, keterangan: str, jumlah: int):
    _reload()
    biaya_df = pd.read_csv(DATA_DIR / "biaya.csv")
    new_id = f"BYR{len(biaya_df)+1:03d}"
    new_row = pd.DataFrame(
        {
            "id_biaya": [new_id],
            "tanggal": [tanggal],
            "kategori": [kategori],
            "keterangan": [keterangan],
            "jumlah": [jumlah],
        }
    )
    pd.concat([biaya_df, new_row], ignore_index=True).to_csv(
        DATA_DIR / "biaya.csv", index=False
    )


def ringkasan_finansial(data: dict[str, pd.DataFrame]) -> dict:
    """Compute financial summary from loaded dataframes."""
    transaksi = data["transaksi"]
    detail = data["detail_transaksi"]
    produk = data["produk"]
    biaya = data["biaya"]

    omzet = transaksi["total_bayar"].sum()

    produk_lookup = {
        row["id_produk"]: row for _, row in produk.iterrows()
    }
    hpp = 0
    for _, d in detail.iterrows():
        p = produk_lookup[d["id_produk"]]
        hpp += int(p["harga_beli"]) * int(d["jumlah"])

    laba_kotor = omzet - hpp
    biaya_op = biaya[biaya["kategori"] != "Modal Awal"]["jumlah"].sum()
    modal = biaya[biaya["kategori"] == "Modal Awal"]["jumlah"].sum()
    laba_bersih = laba_kotor - biaya_op

    return {
        "omzet": int(omzet),
        "hpp": int(hpp),
        "laba_kotor": int(laba_kotor),
        "biaya_operasional": int(biaya_op),
        "modal_awal": int(modal),
        "laba_bersih": int(laba_bersih),
    }


if __name__ == "__main__":
    print("load_all keys:", list(load_all().keys()))
    print("login admin:", login("admin", "admin123"))
