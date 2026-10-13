"""WhatsApp Cloud API tests: text, media upload, document send, restock alert."""
import json

import pytest

import whatsapp_alert


class Recorder:
    """Fake HTTP layer capturing every call, no network."""

    def __init__(self, json_responses=None):
        self.json_calls = []
        self.multipart_calls = []
        self.json_responses = list(json_responses or [])

    def json_post(self, url, payload, headers):
        self.json_calls.append({"url": url, "payload": payload, "headers": headers})
        if self.json_responses:
            return self.json_responses.pop(0)
        return {"messages": [{"id": "wamid.TEST"}]}

    def multipart_post(self, url, fields, files, headers):
        self.multipart_calls.append(
            {"url": url, "fields": fields, "files": files, "headers": headers}
        )
        return {"id": "MEDIA123"}


@pytest.fixture
def recorder(monkeypatch):
    rec = Recorder()
    monkeypatch.setattr(whatsapp_alert, "_post_json", rec.json_post)
    monkeypatch.setattr(whatsapp_alert, "_post_multipart", rec.multipart_post)
    return rec


def test_send_text_posts_to_phone_number_endpoint(recorder):
    result = whatsapp_alert.send_text(
        to="6289515780328",
        body="Halo",
        token="TOKEN",
        phone_number_id="123456",
    )

    assert result["messages"][0]["id"] == "wamid.TEST"
    call = recorder.json_calls[0]
    assert call["url"] == "https://graph.facebook.com/v21.0/123456/messages"
    assert call["headers"]["Authorization"] == "Bearer TOKEN"
    assert call["payload"]["messaging_product"] == "whatsapp"
    assert call["payload"]["to"] == "6289515780328"
    assert call["payload"]["type"] == "text"
    assert call["payload"]["text"]["body"] == "Halo"


def test_send_text_rejects_empty_body(recorder):
    with pytest.raises(ValueError):
        whatsapp_alert.send_text("6289515780328", "   ", token="T", phone_number_id="1")
    assert recorder.json_calls == []


def test_send_text_requires_credentials(recorder):
    with pytest.raises(whatsapp_alert.WhatsAppConfigError):
        whatsapp_alert.send_text("6289515780328", "Halo", token="", phone_number_id="")
    assert recorder.json_calls == []


def test_upload_media_returns_media_id(recorder):
    media_id = whatsapp_alert.upload_media(
        data=b"%PDF-1.4 fake",
        filename="laporan.pdf",
        token="TOKEN",
        phone_number_id="123456",
    )

    assert media_id == "MEDIA123"
    call = recorder.multipart_calls[0]
    assert call["url"] == "https://graph.facebook.com/v21.0/123456/media"
    assert call["fields"]["messaging_product"] == "whatsapp"
    assert call["fields"]["type"] == "application/pdf"
    assert call["files"]["file"][0] == "laporan.pdf"
    assert call["files"]["file"][1] == b"%PDF-1.4 fake"


def test_send_document_uploads_then_sends_media_id(recorder):
    result = whatsapp_alert.send_document(
        to="6289515780328",
        data=b"%PDF-1.4 fake",
        filename="laporan.pdf",
        caption="Laporan harian",
        token="TOKEN",
        phone_number_id="123456",
    )

    assert result["messages"][0]["id"] == "wamid.TEST"
    assert len(recorder.multipart_calls) == 1
    call = recorder.json_calls[0]
    assert call["payload"]["type"] == "document"
    assert call["payload"]["document"]["id"] == "MEDIA123"
    assert call["payload"]["document"]["filename"] == "laporan.pdf"
    assert call["payload"]["document"]["caption"] == "Laporan harian"


def test_send_document_requires_pdf_bytes(recorder):
    with pytest.raises(ValueError):
        whatsapp_alert.send_document(
            "6289515780328", b"", "laporan.pdf", token="T", phone_number_id="1"
        )
    assert recorder.multipart_calls == []
    assert recorder.json_calls == []


def test_notify_restock_sends_formatted_message(recorder):
    produk = [
        {"id_produk": "P001", "nama_produk": "Indomie Goreng", "stok": 0, "min_stok": 10},
        {"id_produk": "P003", "nama_produk": "Roti Cokelat", "stok": 4, "min_stok": 5},
    ]

    result = whatsapp_alert.notify_restock(
        produk, to="6289515780328", token="TOKEN", phone_number_id="123456"
    )

    assert result["messages"][0]["id"] == "wamid.TEST"
    body = recorder.json_calls[0]["payload"]["text"]["body"]
    assert "Indomie Goreng" in body
    assert "P001" in body
    assert "Roti Cokelat" in body


def test_notify_restock_skips_when_nothing_low(recorder):
    result = whatsapp_alert.notify_restock(
        [], to="6289515780328", token="TOKEN", phone_number_id="123456"
    )

    assert result is None
    assert recorder.json_calls == []


def test_send_financial_pdf_builds_and_sends_document(recorder):
    summary = {
        "omzet": 120000,
        "hpp": 50000,
        "laba_kotor": 70000,
        "biaya_operasional": 10000,
        "modal_awal": 200000,
        "laba_bersih": 60000,
    }

    result = whatsapp_alert.send_financial_pdf(
        summary, to="6289515780328", token="TOKEN", phone_number_id="123456"
    )

    assert result["messages"][0]["id"] == "wamid.TEST"
    sent_bytes = recorder.multipart_calls[0]["files"]["file"][1]
    assert sent_bytes.startswith(b"%PDF-")
    assert recorder.json_calls[0]["payload"]["type"] == "document"


def test_error_message_never_leaks_token(monkeypatch):
    def boom(url, payload, headers):
        raise RuntimeError("HTTP 401 for url=" + url)

    monkeypatch.setattr(whatsapp_alert, "_post_json", boom)

    with pytest.raises(whatsapp_alert.WhatsAppError) as exc:
        whatsapp_alert.send_text("6289515780328", "Halo", token="SUPERSECRET", phone_number_id="1")

    assert "SUPERSECRET" not in str(exc.value)


def test_config_status_reports_missing_and_present(monkeypatch):
    monkeypatch.setattr(whatsapp_alert, "_read_setting", lambda key: None)
    status = whatsapp_alert.config_status()
    assert status["configured"] is False
    assert status["missing"] == ["token", "phone_number_id"]

    values = {"token": "T", "phone_number_id": "1", "recipient": "6289515780328"}
    monkeypatch.setattr(whatsapp_alert, "_read_setting", lambda key: values.get(key))
    status = whatsapp_alert.config_status()
    assert status["configured"] is True
    assert status["missing"] == []
    assert status["recipient"] == "6289515780328"


def test_resolve_recipient_prefers_explicit_argument(monkeypatch):
    monkeypatch.setattr(whatsapp_alert, "_read_setting", lambda key: "6281111111111")
    assert whatsapp_alert.resolve_recipient("6289999999999") == "6289999999999"
    assert whatsapp_alert.resolve_recipient(None) == "6281111111111"
