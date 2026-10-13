"""CLI credential checker: exit codes and secret masking."""
import check_whatsapp
import whatsapp_alert


def test_mask_never_reveals_full_secret():
    secret = "EAAG1234567890abcdefghij"
    masked = check_whatsapp.mask(secret)
    assert masked.startswith("EAAG")
    assert "1234567890" not in masked
    assert secret[-8:] not in masked
    assert str(len(secret)) in masked


def test_mask_handles_missing_value():
    assert check_whatsapp.mask(None) == "(kosong)"
    assert check_whatsapp.mask("") == "(kosong)"


def test_main_returns_error_when_not_configured(monkeypatch, capsys):
    monkeypatch.setattr(whatsapp_alert, "_read_setting", lambda key: None)
    code = check_whatsapp.main([])
    out = capsys.readouterr().out
    assert code == 1
    assert "BELUM LENGKAP" in out
    assert "token" in out


def test_main_reports_ok_without_sending(monkeypatch, capsys):
    values = {"token": "T", "phone_number_id": "1", "recipient": "6289"}
    monkeypatch.setattr(whatsapp_alert, "_read_setting", lambda key: values.get(key))
    monkeypatch.setattr(
        whatsapp_alert, "send_text", lambda *a, **k: (_ for _ in ()).throw(AssertionError)
    )
    code = check_whatsapp.main([])
    out = capsys.readouterr().out
    assert code == 0
    assert "siap kirim" in out
