import csv
import sqlite3

import pytest

import db_init


TABLES = ["kasir", "produk", "transaksi", "detail_transaksi", "biaya", "shift_log", "settings"]


@pytest.fixture
def db(tmp_path, monkeypatch):
    """Point db_init at a throwaway database inside tmp_path."""
    db_path = tmp_path / "test.db"
    monkeypatch.setattr(db_init, "DB_PATH", db_path)
    return db_path


def table_names(db_path):
    conn = sqlite3.connect(db_path)
    rows = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
    ).fetchall()
    conn.close()
    return [r[0] for r in rows]


def count(db_path, table):
    conn = sqlite3.connect(db_path)
    n = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
    conn.close()
    return n


def test_init_db_creates_all_tables(db):
    db_init.init_db()
    names = table_names(db)
    for t in TABLES:
        assert t in names, f"table {t} missing"


def test_init_db_is_idempotent(db):
    db_init.init_db()
    db_init.init_db()
    assert table_names(db).count("produk") == 1


def test_import_csv_loads_all_sample_rows(db):
    db_init.import_csv_to_db(reset=True)
    assert count(db, "produk") == 50
    assert count(db, "transaksi") == 250
    assert count(db, "detail_transaksi") == 250
    assert count(db, "kasir") == 3
    assert count(db, "biaya") == 5


def test_import_csv_stores_hashed_passwords_not_plain(db):
    db_init.import_csv_to_db(reset=True)
    conn = sqlite3.connect(db)
    rows = conn.execute("SELECT username, password_hash FROM kasir").fetchall()
    conn.close()
    assert rows, "no kasir rows"
    for username, pw_hash in rows:
        assert pw_hash, f"missing password_hash for {username}"
        assert username not in pw_hash, f"plain password stored for {username}"


def test_export_db_to_csv_roundtrip(db, tmp_path, monkeypatch):
    db_init.import_csv_to_db(reset=True)
    export_dir = tmp_path / "export"
    export_dir.mkdir()
    monkeypatch.setattr(db_init, "DATA_DIR", export_dir)
    db_init.export_db_to_csv()
    with open(export_dir / "produk.csv", newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == 50
    assert "password_hash" not in rows[0], "password hash leaked into CSV"
