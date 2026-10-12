"""Database bootstrap: schema, CSV -> SQLite import, SQLite -> CSV export."""
import csv
import hashlib
import hmac
import os
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = BASE_DIR / "database.db"

SCHEMA = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS kasir (
    id_kasir TEXT PRIMARY KEY,
    nama TEXT NOT NULL,
    username TEXT UNIQUE NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('admin', 'kasir')),
    password_hash TEXT NOT NULL DEFAULT ''
);

CREATE TABLE IF NOT EXISTS produk (
    id_produk TEXT PRIMARY KEY,
    nama_produk TEXT NOT NULL,
    kategori TEXT NOT NULL,
    harga_beli INTEGER NOT NULL,
    harga_jual INTEGER NOT NULL,
    stok INTEGER NOT NULL,
    min_stok INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS transaksi (
    id_transaksi TEXT PRIMARY KEY,
    tanggal_waktu TEXT NOT NULL,
    id_kasir TEXT NOT NULL,
    metode_pembayaran TEXT NOT NULL,
    total_bayar INTEGER NOT NULL,
    FOREIGN KEY (id_kasir) REFERENCES kasir(id_kasir)
);

CREATE TABLE IF NOT EXISTS detail_transaksi (
    id_detail TEXT PRIMARY KEY,
    id_transaksi TEXT NOT NULL,
    id_produk TEXT NOT NULL,
    jumlah INTEGER NOT NULL,
    harga_satuan INTEGER NOT NULL,
    subtotal INTEGER NOT NULL,
    FOREIGN KEY (id_transaksi) REFERENCES transaksi(id_transaksi) ON DELETE CASCADE,
    FOREIGN KEY (id_produk) REFERENCES produk(id_produk)
);

CREATE TABLE IF NOT EXISTS biaya (
    id_biaya TEXT PRIMARY KEY,
    tanggal TEXT NOT NULL,
    kategori TEXT NOT NULL,
    keterangan TEXT NOT NULL,
    jumlah INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS shift_log (
    id_shift TEXT PRIMARY KEY,
    id_kasir TEXT NOT NULL,
    nama_shift TEXT NOT NULL,
    mulai TEXT NOT NULL,
    selesai TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'aktif',
    FOREIGN KEY (id_kasir) REFERENCES kasir(id_kasir)
);

CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);
"""

CSV_TABLES = ["kasir", "produk", "biaya", "transaksi", "detail_transaksi"]


def hash_password(password: str) -> str:
    """PBKDF2-SHA256, salted. Format: pbkdf2:sha256$iterations$salt$hash."""
    salt = os.urandom(16).hex()
    iterations = 260000
    digest = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), bytes.fromhex(salt), iterations
    ).hex()
    return f"pbkdf2:sha256${iterations}${salt}${digest}"


def verify_password(password: str, stored: str) -> bool:
    try:
        _algo, iterations, salt, digest = stored.split("$")
        candidate = hashlib.pbkdf2_hmac(
            "sha256", password.encode("utf-8"), bytes.fromhex(salt), int(iterations)
        ).hex()
        return hmac.compare_digest(candidate, digest)
    except (ValueError, AttributeError):
        return False


def connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db(reset: bool = False):
    if reset and DB_PATH.exists():
        DB_PATH.unlink()
    conn = connect()
    conn.executescript(SCHEMA)
    conn.commit()
    conn.close()


def import_csv_to_db(reset: bool = False):
    """Load every CSV in data/ into a fresh SQLite database."""
    init_db(reset=reset)
    conn = connect()
    conn.execute("PRAGMA foreign_keys = OFF")
    for table in reversed(CSV_TABLES):
        conn.execute(f"DELETE FROM {table}")

    for table in CSV_TABLES:
        path = DATA_DIR / f"{table}.csv"
        if not path.exists():
            continue
        with path.open(newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            headers = list(reader.fieldnames or [])
            if table == "kasir":
                headers.append("password_hash")
                rows = [
                    {**r, "password_hash": hash_password(r["username"] + "123")}
                    for r in reader
                ]
            else:
                rows = list(reader)
        if not rows:
            continue
        placeholders = ", ".join("?" for _ in headers)
        conn.executemany(
            f"INSERT INTO {table} ({', '.join(headers)}) VALUES ({placeholders})",
            [tuple(r[h] for h in headers) for r in rows],
        )
    conn.commit()
    conn.close()


def export_db_to_csv():
    """Write every CSV table back to data/ (password hashes never exported)."""
    DATA_DIR.mkdir(exist_ok=True)
    conn = connect()
    for table in CSV_TABLES:
        cur = conn.execute(f"SELECT * FROM {table}")
        headers = [d[0] for d in cur.description]
        if "password_hash" in headers:
            headers.remove("password_hash")
        with (DATA_DIR / f"{table}.csv").open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            for row in cur:
                writer.writerow([row[h] for h in headers])
    conn.close()


if __name__ == "__main__":
    import_csv_to_db(reset=True)
    print(f"DB ready: {DB_PATH}")
