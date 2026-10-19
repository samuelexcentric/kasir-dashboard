"""Halaman Export PDF & WhatsApp."""
from __future__ import annotations

import pandas as pd
import streamlit as st

import components as ui
import services
import whatsapp_alert


def _nomor(nomor: str) -> str:
    """Rapikan nomor WhatsApp: 6289... -> +62 895-1578-0328."""
    d = "".join(ch for ch in str(nomor) if ch.isdigit())
    if d.startswith("62"):
        d = d[2:]
    if len(d) < 9:
        return str(nomor)
    return f"+62 {d[:3]}-{d[3:7]}-{d[7:]}"


def _periode(data: dict) -> str:
    """Rentang tanggal data transaksi, mis. '01 Okt – 06 Okt 2026'."""
    tgl = pd.to_datetime(data["transaksi"]["tanggal_waktu"])
    awal, akhir = tgl.min(), tgl.max()
    if awal.month == akhir.month:
        return f"{awal:%d}–{akhir:%d %b %Y}"
    return f"{awal:%d %b} – {akhir:%d %b %Y}"


def render(data: dict, role: str) -> None:
    ring = services.ringkasan_finansial(data)
    status = whatsapp_alert.config_status()
    periode = _periode(data)

    ui.page_header(
        "Export & Laporan",
        "Unduh laporan PDF atau kirim lewat WhatsApp.",
        aksi=periode,
    )

    k1, k2, k3 = st.columns(3)
    ui.kpi_ke(k1, "Omzet", ui.rupiah(ring["omzet"]), "mint", periode)
    ui.kpi_ke(k2, "Laba bersih", ui.rupiah(ring["laba_bersih"]), "lavender",
              "setelah biaya")
    ui.kpi_ke(k3, "Transaksi", ui.angka(len(data["transaksi"])), "peach",
              "total tercatat")

    kiri, kanan = st.columns(2, gap="large")

    with kiri:
        ui.judul_bagian("Laporan PDF", "ringkasan finansial")
        st.caption(
            "Berisi omzet, HPP, laba kotor, biaya operasional, modal awal, "
            "dan laba bersih."
        )
        if st.button("Buat PDF", type="primary", use_container_width=True):
            try:
                from utils import create_financial_pdf

                st.session_state["pdf_bytes"] = create_financial_pdf(ring)
                st.success("PDF siap diunduh")
            except Exception as e:
                st.error(f"PDF gagal: {e}")
        if st.session_state.get("pdf_bytes"):
            st.download_button(
                "Unduh laporan.pdf",
                data=st.session_state["pdf_bytes"],
                file_name="laporan.pdf",
                mime="application/pdf",
                use_container_width=True,
            )

    with kanan:
        nomor = status.get("recipient")
        ui.judul_bagian("Kirim WhatsApp", _nomor(nomor) if nomor else "belum diset")
        if not status["configured"]:
            ui.banner(
                "WhatsApp belum dikonfigurasi. Isi `whatsapp_token`, "
                "`whatsapp_phone_number_id`, dan `whatsapp_recipient` "
                "di secrets.",
                "info", "ℹ️",
            )
        else:
            st.caption("Laporan PDF yang sama akan dikirim ke nomor di atas.")
        if st.button("Kirim ke WhatsApp", use_container_width=True):
            try:
                whatsapp_alert.send_financial_pdf(ring)
                st.success(f"laporan.pdf terkirim ke {_nomor(nomor)}")
            except whatsapp_alert.WhatsAppError as e:
                st.error(f"Gagal kirim: {e}")

    ui.judul_bagian("Pratinjau isi PDF", "sama seperti PDF")
    baris = [
        ("Omzet", ring["omzet"]),
        ("HPP", ring["hpp"]),
        ("Laba kotor", ring["laba_kotor"]),
        ("Biaya operasional", ring["biaya_operasional"]),
        ("Modal awal", ring["modal_awal"]),
        ("Laba bersih", ring["laba_bersih"]),
    ]
    isi = "".join(
        f'<div class="lapor-baris{" tebal" if label == "Laba bersih" else ""}">'
        f"<span>{label}</span><b>{ui.rupiah(nilai)}</b></div>"
        for label, nilai in baris
    )
    ui.html(f'<div class="lapor">{isi}</div>')
