from utils import create_financial_pdf


def test_create_financial_pdf_returns_pdf_document():
    document = create_financial_pdf(
        {
            "omzet": 120000,
            "hpp": 50000,
            "laba_kotor": 70000,
            "biaya_operasional": 10000,
            "modal_awal": 200000,
            "laba_bersih": 60000,
        }
    )

    assert document.startswith(b"%PDF-")
    assert document.endswith(b"%%EOF\n")
