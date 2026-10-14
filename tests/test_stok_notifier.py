"""Tests for the automatic low-stock notifier (stok_notifier.py)."""
import json

import pytest

import core
import stok_notifier
import whatsapp_alert


@pytest.fixture(autouse=True)
def isolated_state(tmp_path, monkeypatch):
    """Point the anti-spam ledger at a temp file so tests never touch data/."""
    monkeypatch.setattr(stok_notifier, "STATE_PATH", tmp_path / "state.json")
    yield


@pytest.fixture
def configured(monkeypatch):
    """Pretend WhatsApp is configured and capture sends."""
    sent = []
    monkeypatch.setattr(
        whatsapp_alert, "config_status", lambda: {"configured": True, "recipient": "x"}
    )
    monkeypatch.setattr(whatsapp_alert, "notify_restock", lambda p: sent.append(p))
    return sent


def produk(*pairs):
    return [
        {"id_produk": pid, "nama_produk": pid, "stok": stok, "min_stok": 5}
        for pid, stok in pairs
    ]


def test_alerts_when_stock_drops_to_threshold(configured):
    baru = stok_notifier.check_and_notify(produk(("P1", 20)))
    assert [p["id_produk"] for p in baru] == ["P1"]
    assert len(configured) == 1


def test_no_alert_above_threshold(configured):
    assert stok_notifier.check_and_notify(produk(("P1", 21))) == []
    assert configured == []


def test_alerts_only_once_until_stock_recovers(configured):
    stok_notifier.check_and_notify(produk(("P1", 19)))
    assert stok_notifier.check_and_notify(produk(("P1", 19))) == []
    assert len(configured) == 1


def test_re_alerts_after_recovery_then_drop(configured):
    stok_notifier.check_and_notify(produk(("P1", 10)))
    stok_notifier.check_and_notify(produk(("P1", 80)))
    baru = stok_notifier.check_and_notify(produk(("P1", 10)))
    assert [p["id_produk"] for p in baru] == ["P1"]
    assert len(configured) == 2


def test_state_survives_restart(configured):
    stok_notifier.check_and_notify(produk(("P1", 5)))
    assert stok_notifier.STATE_PATH.exists()
    assert "P1" in json.loads(stok_notifier.STATE_PATH.read_text())
    assert stok_notifier.check_and_notify(produk(("P1", 5))) == []


def test_skips_sending_when_not_configured(monkeypatch):
    monkeypatch.setattr(whatsapp_alert, "config_status", lambda: {"configured": False})
    assert stok_notifier.check_and_notify(produk(("P1", 3))) == []


def test_never_raises_on_failure(monkeypatch):
    monkeypatch.setattr(
        whatsapp_alert, "config_status", lambda: {"configured": True}
    )
    monkeypatch.setattr(
        whatsapp_alert, "notify_restock",
        lambda p: (_ for _ in ()).throw(RuntimeError("boom")),
    )
    assert stok_notifier.check_and_notify(produk(("P1", 3))) == []


def test_threshold_override_via_env(monkeypatch, configured):
    monkeypatch.setenv("STOK_MENIPIS_THRESHOLD", "50")
    assert stok_notifier.ambang() == 50
    assert [p["id_produk"] for p in stok_notifier.check_and_notify(produk(("P1", 40)))] == ["P1"]


def test_empty_product_list_is_safe(configured):
    assert stok_notifier.check_and_notify([]) == []
    assert stok_notifier.check_and_notify(None) == []


def test_core_menipis_sorted_by_stock():
    out = core.produk_stok_menipis(produk(("A", 15), ("B", 0), ("C", 20), ("D", 99)))
    assert [p["id_produk"] for p in out] == ["B", "A", "C"]


def test_message_separates_habis_and_menipis():
    msg = core.pesan_whatsapp_restock(produk(("A", 0), ("B", 7)))
    assert "*HABIS (stok 0):*" in msg and "A" in msg
    assert "*MENIPIS:*" in msg and "B" in msg
