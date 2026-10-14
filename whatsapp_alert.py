"""WhatsApp Cloud API client: stock alerts and PDF report delivery.

Credentials are read from environment variables (UPPERCASE names) or from
Streamlit secrets (LOWERCASE names — st.secrets is case-sensitive):

    env:     WHATSAPP_TOKEN / WHATSAPP_PHONE_NUMBER_ID / WHATSAPP_RECIPIENT
    secrets: whatsapp_token / whatsapp_phone_number_id / whatsapp_recipient

Values are never logged or included in error messages.
"""
from __future__ import annotations

import json
import mimetypes
import os
import urllib.error
import urllib.request

import core

GRAPH_VERSION = "v21.0"
GRAPH_BASE = f"https://graph.facebook.com/{GRAPH_VERSION}"

_SETTING_KEYS = {
    "token": ("WHATSAPP_TOKEN", "whatsapp_token"),
    "phone_number_id": ("WHATSAPP_PHONE_NUMBER_ID", "whatsapp_phone_number_id"),
    "recipient": ("WHATSAPP_RECIPIENT", "whatsapp_recipient"),
}


class WhatsAppError(RuntimeError):
    """Any failure while talking to the WhatsApp Cloud API."""


class WhatsAppConfigError(WhatsAppError):
    """Missing token or phone number id."""


def _read_setting(key: str):
    env_name, secret_name = _SETTING_KEYS[key]
    value = os.environ.get(env_name)
    if value:
        return value.strip()
    try:
        import streamlit as st

        if secret_name in st.secrets:
            return str(st.secrets[secret_name]).strip()
    except Exception:
        pass
    return None


def config_status() -> dict:
    """Report which settings are present, without revealing their values."""
    values = {key: _read_setting(key) for key in _SETTING_KEYS}
    missing = [key for key in ("token", "phone_number_id") if not values.get(key)]
    return {
        "configured": not missing,
        "missing": missing,
        "recipient": values.get("recipient"),
    }


def resolve_recipient(to: str | None = None) -> str | None:
    return (to or _read_setting("recipient") or None)


def _require_credentials(token: str | None, phone_number_id: str | None):
    token = token or _read_setting("token")
    phone_number_id = phone_number_id or _read_setting("phone_number_id")
    if not token or not phone_number_id:
        raise WhatsAppConfigError(
            "Kredensial WhatsApp belum lengkap: butuh WHATSAPP_TOKEN dan "
            "WHATSAPP_PHONE_NUMBER_ID."
        )
    return token, phone_number_id


def _post_json(url: str, payload: dict, headers: dict) -> dict:
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json", **headers},
        method="POST",
    )
    return _open_json(request, url)


def _post_multipart(url: str, fields: dict, files: dict, headers: dict) -> dict:
    boundary = "----hermesWhatsappBoundary7d91f0"
    body = bytearray()
    for name, value in fields.items():
        body += f"--{boundary}\r\n".encode()
        body += f'Content-Disposition: form-data; name="{name}"\r\n\r\n'.encode()
        body += f"{value}\r\n".encode()
    for name, (filename, data) in files.items():
        content_type = (
            mimetypes.guess_type(filename)[0] or "application/octet-stream"
        )
        body += f"--{boundary}\r\n".encode()
        body += (
            f'Content-Disposition: form-data; name="{name}"; '
            f'filename="{filename}"\r\n'
        ).encode()
        body += f"Content-Type: {content_type}\r\n\r\n".encode()
        body += data
        body += b"\r\n"
    body += f"--{boundary}--\r\n".encode()

    request = urllib.request.Request(
        url,
        data=bytes(body),
        headers={
            "Content-Type": f"multipart/form-data; boundary={boundary}",
            **headers,
        },
        method="POST",
    )
    return _open_json(request, url)


def _guarded(description: str, call):
    """Run an API call, normalising every failure to WhatsAppError.

    The original exception text is deliberately dropped: it could echo request
    headers and leak the access token.
    """
    try:
        return call()
    except WhatsAppError:
        raise
    except Exception as exc:
        raise WhatsAppError(
            f"{description} gagal ({type(exc).__name__}). Periksa token, "
            "phone number id, dan koneksi internet."
        ) from None


def _open_json(request, url: str) -> dict:
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            raw = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", "replace")[:300]
        raise WhatsAppError(
            f"WhatsApp API menolak permintaan (HTTP {exc.code}). Detail: {detail}"
        ) from None
    except urllib.error.URLError as exc:
        raise WhatsAppError(
            f"Tidak bisa menghubungi WhatsApp API: {exc.reason}"
        ) from None
    if not raw.strip():
        return {}
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        raise WhatsAppError("Respons WhatsApp API tidak bisa dibaca.") from None


def send_text(
    to: str,
    body: str,
    token: str | None = None,
    phone_number_id: str | None = None,
) -> dict:
    """Send a plain text message. Returns the API response."""
    if not body or not body.strip():
        raise ValueError("Isi pesan tidak boleh kosong.")
    token, phone_number_id = _require_credentials(token, phone_number_id)
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": to,
        "type": "text",
        "text": {"preview_url": False, "body": body},
    }
    return _guarded(
        "Kirim pesan WhatsApp",
        lambda: _post_json(
            f"{GRAPH_BASE}/{phone_number_id}/messages",
            payload,
            {"Authorization": f"Bearer {token}"},
        ),
    )


def upload_media(
    data: bytes,
    filename: str,
    token: str | None = None,
    phone_number_id: str | None = None,
) -> str:
    """Upload a document and return its reusable media id."""
    if not data:
        raise ValueError("Isi dokumen tidak boleh kosong.")
    token, phone_number_id = _require_credentials(token, phone_number_id)
    content_type = mimetypes.guess_type(filename)[0] or "application/pdf"
    response = _post_multipart(
        f"{GRAPH_BASE}/{phone_number_id}/media",
        {"messaging_product": "whatsapp", "type": content_type},
        {"file": (filename, data)},
        {"Authorization": f"Bearer {token}"},
    )
    media_id = response.get("id")
    if not media_id:
        raise WhatsAppError("WhatsApp API tidak mengembalikan media id.")
    return media_id


def send_document(
    to: str,
    data: bytes,
    filename: str,
    caption: str = "",
    token: str | None = None,
    phone_number_id: str | None = None,
) -> dict:
    """Upload a document, then send it to a WhatsApp number."""
    if not data:
        raise ValueError("Isi dokumen tidak boleh kosong.")
    media_id = upload_media(
        data, filename, token=token, phone_number_id=phone_number_id
    )
    token, phone_number_id = _require_credentials(token, phone_number_id)
    document = {"id": media_id, "filename": filename}
    if caption:
        document["caption"] = caption
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": to,
        "type": "document",
        "document": document,
    }
    return _post_json(
        f"{GRAPH_BASE}/{phone_number_id}/messages",
        payload,
        {"Authorization": f"Bearer {token}"},
    )


def notify_restock(
    produk_restock: list[dict],
    to: str | None = None,
    token: str | None = None,
    phone_number_id: str | None = None,
) -> dict | None:
    """Send the low-stock alert. Returns None when nothing needs restocking."""
    if not produk_restock:
        return None
    recipient = resolve_recipient(to)
    if not recipient:
        raise WhatsAppConfigError(
            "Nomor tujuan WhatsApp belum diatur: isi WHATSAPP_RECIPIENT."
        )
    return send_text(
        recipient,
        core.pesan_whatsapp_restock(produk_restock),
        token=token,
        phone_number_id=phone_number_id,
    )


def send_financial_pdf(
    summary: dict,
    to: str | None = None,
    token: str | None = None,
    phone_number_id: str | None = None,
) -> dict:
    """Build the financial PDF in memory and send it as a WhatsApp document."""
    from utils import create_financial_pdf

    recipient = resolve_recipient(to)
    if not recipient:
        raise WhatsAppConfigError(
            "Nomor tujuan WhatsApp belum diatur: isi WHATSAPP_RECIPIENT."
        )
    pdf_bytes = create_financial_pdf(summary)
    return send_document(
        recipient,
        pdf_bytes,
        "laporan.pdf",
        caption="Laporan keuangan kasir",
        token=token,
        phone_number_id=phone_number_id,
    )
