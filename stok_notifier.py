"""Automatic low-stock WhatsApp alerts.

Called on every dashboard load, so a stock change is caught however it happened:
a sale on the Kasir page, a direct edit of data/produk.csv, or anything else
that ends up in the produk table.

De-duplication: each product is alerted once when it crosses into the low band.
The flag is cleared as soon as its stock climbs back above the threshold, so a
later drop alerts again. State lives in data/stok_notified.json so a browser
refresh or an app restart does not re-send the same message.
"""
from __future__ import annotations

import json
import os
from pathlib import Path

import core
import whatsapp_alert

STATE_PATH = Path(__file__).resolve().parent / "data" / "stok_notified.json"


def ambang() -> int:
    """Threshold from STOK_MENIPIS_THRESHOLD, else core's default (20)."""
    raw = os.environ.get("STOK_MENIPIS_THRESHOLD")
    if raw and raw.strip().isdigit():
        return int(raw.strip())
    return core.STOK_MENIPIS_DEFAULT


def _load_state() -> set[str]:
    try:
        data = json.loads(STATE_PATH.read_text())
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return set()
    if isinstance(data, list):
        return {str(x) for x in data}
    return set()


def _save_state(ids: set[str]) -> None:
    try:
        STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
        STATE_PATH.write_text(json.dumps(sorted(ids), indent=2))
    except OSError:
        pass


def _prune_recovered(produk: list[dict], notified: set[str]) -> set[str]:
    """Drop ids whose stock is back above the threshold, so they can re-alert."""
    limit = ambang()
    masih_menipis = {
        str(p["id_produk"]) for p in produk if int(p["stok"]) <= limit
    }
    return {pid for pid in notified if pid in masih_menipis}


def check_and_notify(produk: list[dict]) -> list[dict]:
    """Send one WhatsApp alert per newly-low product. Returns what was alerted.

    Never raises: a WhatsApp or filesystem failure must not take the dashboard
    down, so problems are swallowed and simply retried on the next load.
    """
    try:
        produk = list(produk or [])
        if not produk:
            return []

        notified = _prune_recovered(produk, _load_state())
        baru = core.produk_baru_menipis(produk, notified, ambang())
        if not baru:
            _save_state(notified)
            return []

        if not whatsapp_alert.config_status()["configured"]:
            return []

        whatsapp_alert.notify_restock(baru)
    except Exception:
        return []
    notified.update(str(p["id_produk"]) for p in baru)
    _save_state(notified)
    return baru
