from fpdf import FPDF


def create_financial_pdf(summary):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 18)
    pdf.cell(0, 12, "Laporan Kasir", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", size=12)
    for label, key in (
        ("Omzet", "omzet"),
        ("HPP", "hpp"),
        ("Laba kotor", "laba_kotor"),
        ("Biaya operasional", "biaya_operasional"),
        ("Modal awal", "modal_awal"),
        ("Laba bersih", "laba_bersih"),
    ):
        amount = int(summary.get(key, 0))
        pdf.cell(0, 9, f"{label}: Rp {amount:,}", new_x="LMARGIN", new_y="NEXT")
    return bytes(pdf.output())
