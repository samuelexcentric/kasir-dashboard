"""Integration tests for the real HTTP transport against a local server.

The other WhatsApp tests mock _post_json/_post_multipart, so the actual
urllib request building is never exercised. These tests spin up a throwaway
HTTP server and drive the client through real sockets.
"""
import json
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

import pytest

import whatsapp_alert


class Handler(BaseHTTPRequestHandler):
    received = []

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length)
        Handler.received.append(
            {
                "path": self.path,
                "auth": self.headers.get("Authorization"),
                "content_type": self.headers.get("Content-Type", ""),
                "body": body,
            }
        )
        if self.path.endswith("/media"):
            payload = {"id": "MEDIA_REAL"}
        else:
            payload = {"messages": [{"id": "wamid.REAL"}]}
        raw = json.dumps(payload).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def log_message(self, *args):
        pass


@pytest.fixture
def server(monkeypatch):
    Handler.received = []
    httpd = HTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    base = f"http://127.0.0.1:{httpd.server_port}"
    monkeypatch.setattr(whatsapp_alert, "GRAPH_BASE", base)
    yield Handler.received
    httpd.shutdown()
    httpd.server_close()


def test_send_text_over_real_http(server):
    result = whatsapp_alert.send_text(
        "6289515780328", "Halo nyata", token="TKN", phone_number_id="555"
    )

    assert result["messages"][0]["id"] == "wamid.REAL"
    assert len(server) == 1
    sent = server[0]
    assert sent["path"] == "/555/messages"
    assert sent["auth"] == "Bearer TKN"
    assert json.loads(sent["body"])["text"]["body"] == "Halo nyata"


def test_send_document_over_real_http(server):
    result = whatsapp_alert.send_document(
        "6289515780328",
        b"%PDF-1.4 real bytes",
        "laporan.pdf",
        caption="Laporan",
        token="TKN",
        phone_number_id="555",
    )

    assert result["messages"][0]["id"] == "wamid.REAL"
    assert len(server) == 2
    upload, message = server
    assert upload["path"] == "/555/media"
    assert "multipart/form-data" in upload["content_type"]
    assert b"%PDF-1.4 real bytes" in upload["body"]
    assert b'name="messaging_product"' in upload["body"]
    assert json.loads(message["body"])["document"]["id"] == "MEDIA_REAL"


def test_http_error_becomes_whatsapp_error(server, monkeypatch):
    def reject(self):
        raw = b'{"error": {"message": "Invalid token"}}'
        self.send_response(401)
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    monkeypatch.setattr(Handler, "do_POST", reject)

    with pytest.raises(whatsapp_alert.WhatsAppError) as exc:
        whatsapp_alert.send_text("6289", "Halo", token="SECRET_TOKEN", phone_number_id="1")

    assert "401" in str(exc.value)
    assert "SECRET_TOKEN" not in str(exc.value)
