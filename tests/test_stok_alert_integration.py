"""End-to-end: a real transaction that empties stock triggers a real HTTP alert.

Combines the data layer (services), the pure logic (core) and the WhatsApp
transport (whatsapp_alert) against a throwaway local HTTP server.
"""
import json
import shutil
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

import pytest

import core
import db_init
import services
import whatsapp_alert


class Handler(BaseHTTPRequestHandler):
    received = []

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        Handler.received.append(self.rfile.read(length))
        raw = json.dumps({"messages": [{"id": "wamid.E2E"}]}).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def log_message(self, *args):
        pass


@pytest.fixture
def store(tmp_path, monkeypatch):
    src_data = Path(__file__).resolve().parent.parent / "data"
    data = tmp_path / "data"
    shutil.copytree(src_data, data)
    monkeypatch.setattr(db_init, "DATA_DIR", data)
    monkeypatch.setattr(db_init, "DB_PATH", tmp_path / "test.db")
    monkeypatch.setattr(services, "DATA_DIR", data)
    db_init.import_csv_to_db(reset=True)
    return data


@pytest.fixture
def api(monkeypatch):
    Handler.received = []
    httpd = HTTPServer(("127.0.0.1", 0), Handler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    monkeypatch.setattr(
        whatsapp_alert, "GRAPH_BASE", f"http://127.0.0.1:{httpd.server_port}"
    )
    monkeypatch.setenv("WHATSAPP_TOKEN", "TKN")
    monkeypatch.setenv("WHATSAPP_PHONE_NUMBER_ID", "555")
    monkeypatch.setenv("WHATSAPP_RECIPIENT", "6289515780328")
    yield Handler.received
    httpd.shutdown()
    httpd.server_close()


def test_selling_last_units_triggers_real_whatsapp_alert(store, api):
    produk = services.load_all()["produk"].to_dict(orient="records")
    row = next(p for p in produk if p["id_produk"] == "P003")
    sisa = int(row["stok"])
    assert sisa > 0

    assert core.produk_baru_habis(produk) == []

    services.buat_transaksi(
        id_kasir="KSR001",
        items=[{"id_produk": "P003", "jumlah": sisa}],
        metode="Tunai",
        waktu="2026-10-13 10:00:00",
    )

    produk_after = services.load_all()["produk"].to_dict(orient="records")
    baru_habis = core.produk_baru_habis(produk_after)
    assert [p["id_produk"] for p in baru_habis] == ["P003"]

    result = whatsapp_alert.notify_restock(baru_habis)
    assert result["messages"][0]["id"] == "wamid.E2E"

    assert len(api) == 1
    payload = json.loads(api[0])
    assert payload["to"] == "6289515780328"
    assert payload["type"] == "text"
    assert "Roti Cokelat" in payload["text"]["body"]


def test_alert_is_not_sent_twice_for_same_product(store, api):
    produk = services.load_all()["produk"].to_dict(orient="records")
    sisa = int(next(p for p in produk if p["id_produk"] == "P003")["stok"])
    services.buat_transaksi(
        id_kasir="KSR001",
        items=[{"id_produk": "P003", "jumlah": sisa}],
        metode="Tunai",
        waktu="2026-10-13 10:00:00",
    )

    produk_after = services.load_all()["produk"].to_dict(orient="records")
    sudah = set()
    pertama = core.produk_baru_habis(produk_after, sudah)
    whatsapp_alert.notify_restock(pertama)
    sudah.update(p["id_produk"] for p in pertama)

    kedua = core.produk_baru_habis(produk_after, sudah)
    assert kedua == []
    assert whatsapp_alert.notify_restock(kedua) is None
    assert len(api) == 1
