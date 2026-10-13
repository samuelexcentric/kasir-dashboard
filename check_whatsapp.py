"""Command-line check for WhatsApp credentials.

Usage:
    python check_whatsapp.py                 # show which settings are present
    python check_whatsapp.py --send-test     # send a test text message
    python check_whatsapp.py --send-pdf      # send a sample financial PDF

Credentials come from the environment or .streamlit/secrets.toml, so this
checks exactly what the deployed app will use.
"""
from __future__ import annotations

import argparse
import sys

import whatsapp_alert


def mask(value: str | None) -> str:
    """Show only a short prefix, enough to confirm the right value was pasted."""
    if not value:
        return "(kosong)"
    if len(value) <= 8:
        return "*" * len(value)
    return f"{value[:4]}... (panjang {len(value)})"


def print_status() -> bool:
    status = whatsapp_alert.config_status()
    print("Status konfigurasi WhatsApp")
    print(f"  WHATSAPP_TOKEN           : {mask(whatsapp_alert._read_setting('token'))}")
    print(
        "  WHATSAPP_PHONE_NUMBER_ID : "
        f"{mask(whatsapp_alert._read_setting('phone_number_id'))}"
    )
    print(f"  WHATSAPP_RECIPIENT       : {mask(status['recipient'])}")
    if status["configured"]:
        print("\nOK - kredensial lengkap, siap kirim.")
        return True
    print(f"\nBELUM LENGKAP. Yang kurang: {', '.join(status['missing'])}")
    print("Isi lewat environment variable atau .streamlit/secrets.toml.")
    return False


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Cek kredensial WhatsApp Cloud API")
    parser.add_argument(
        "--send-test", action="store_true", help="kirim pesan teks percobaan"
    )
    parser.add_argument(
        "--send-pdf", action="store_true", help="kirim contoh PDF laporan"
    )
    args = parser.parse_args(argv)

    if not print_status():
        return 1

    try:
        if args.send_test:
            result = whatsapp_alert.send_text(
                whatsapp_alert.resolve_recipient(),
                "Tes koneksi Dashboard Kasir: WhatsApp aktif.",
            )
            print(f"\nPesan tes terkirim. id={result['messages'][0]['id']}")
        elif args.send_pdf:
            ringkasan = {
                "omzet": 120000,
                "hpp": 50000,
                "laba_kotor": 70000,
                "biaya_operasional": 10000,
                "modal_awal": 200000,
                "laba_bersih": 60000,
            }
            result = whatsapp_alert.send_financial_pdf(ringkasan)
            print(f"\nPDF contoh terkirim. id={result['messages'][0]['id']}")
        else:
            print("\nPakai --send-test atau --send-pdf untuk benar-benar mengirim.")
    except whatsapp_alert.WhatsAppError as exc:
        print(f"\nGAGAL: {exc}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
