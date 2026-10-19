"""Halaman Finansial: 6 KPI kartu pastel + tabel biaya + tambah biaya.

Angka dari services.ringkasan_finansial (turunan CSV transaksi & biaya).
"""
from __future__ import annotations

import datetime

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

import components as ui
import services

URUTAN_BIAYA = ["Modal Awal", "Listrik", "Gaji", "Sewa", "Lainnya"]


def _donut(laba: int, hpp: int, biaya: int) -> go.Figure:
    fig = go.Figure(
        go.Pie(
            labels=["Laba bersih", "HPP", "Biaya operasional"],
            values=[max(laba, 0), max(hpp, 0), max(biaya, 0)],
            hole=.62,
            marker=dict(colors=["#A9D9C2", "#C9BDE8", "#FFD2B3"]),
            textinfo="none",
            hovertemplate="%{label}<br>Rp %{value:,.0f}<extra></extra>",
        )
    )
    fig.update_layout(
        height=232,
        margin=dict(l=0, r=0, t=6, b=6),
        showlegend=True,
        legend=dict(
            orientation="h", yanchor="bottom", y=-0.12, xanchor="center",
            x=0.5, font=dict(size=10, color="#6E6B7B"),
            bgcolor="rgba(0,0,0,0)",
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        annotations=[dict(
            text=f"<b>{ui.rupiah(laba)}</b><br><span style='font-size:10px'>"
                 "laba bersih</span>",
            showarrow=False, font=dict(size=13, color="#3B3A47"),
        )],
    )
    return fig


def render(data: dict, role: str) -> None:
    ring = services.ringkasan_finansial(data)
    omzet = int(ring["omzet"])
    hpp = int(ring["hpp"])
    laba_kotor = int(ring["laba_kotor"])
    biaya = int(ring["biaya_operasional"])
    modal = int(ring["modal_awal"])
    laba_bersih = int(ring["laba_bersih"])
    margin = round(laba_bersih / omzet * 100, 1) if omzet else 0

    ui.page_header(
        "Finansial",
        "Ringkasan omzet, biaya, dan laba.",
        aksi=f"margin {margin}%",
    )

    if role != "admin":
        ui.banner("Mode lihat saja — edit biaya khusus admin.", "info", "ℹ️")

    baris1 = st.columns(3)
    ui.kpi_ke(baris1[0], "Omzet", ui.rupiah(omzet), "mint", "total penjualan")
    ui.kpi_ke(baris1[1], "HPP", ui.rupiah(hpp), "lavender",
              "harga pokok penjualan")
    ui.kpi_ke(baris1[2], "Laba kotor", ui.rupiah(laba_kotor), "peach",
              "omzet − HPP")

    baris2 = st.columns(3)
    ui.kpi_ke(baris2[0], "Biaya operasional", ui.rupiah(biaya), "sky",
              "listrik, gaji, sewa")
    ui.kpi_ke(baris2[1], "Modal awal", ui.rupiah(modal), "butter",
              "setoran awal")
    ui.kpi_ke(baris2[2], "Laba bersih", ui.rupiah(laba_bersih), "rose",
              f"margin {margin}%")

    kiri, kanan = st.columns([1, 1.15], gap="large")

    with kiri:
        ui.judul_bagian("Komposisi", "dari omzet")
        st.plotly_chart(
            _donut(laba_bersih, hpp, biaya), use_container_width=True,
            config={"displayModeBar": False},
        )

    with kanan:
        ui.judul_bagian("Biaya per kategori", "total")
        biaya_df = data["biaya"].copy()
        if "kategori" in biaya_df and "jumlah" in biaya_df:
            per_kat = (
                biaya_df.groupby("kategori")["jumlah"].sum()
                .sort_values(ascending=False)
            )
            ui.progress_list([
                (str(k), int(v), "ungu", ui.rupiah(v))
                for k, v in per_kat.items()
            ])
        else:
            st.caption("Data biaya belum tersedia.")

    if role == "admin":
        with st.expander("Tambah biaya / modal"):
            with st.form("biaya_form"):
                b1, b2 = st.columns(2)
                kategori = b1.selectbox("Kategori", URUTAN_BIAYA)
                jumlah = b2.number_input("Jumlah (Rp)", min_value=0, step=1000)
                ket = st.text_input("Keterangan")
                if st.form_submit_button("Simpan", type="primary"):
                    services.tambah_biaya(
                        datetime.date.today().isoformat(), kategori, ket,
                        int(jumlah))
                    st.success("Tersimpan")
                    st.rerun()

    ui.judul_bagian("Rincian biaya", f"{len(data['biaya'])} catatan")
    tampil = data["biaya"].copy()
    if "jumlah" in tampil:
        st.dataframe(
            tampil.style.format({"jumlah": lambda v: ui.rupiah(v)}),
            use_container_width=True, hide_index=True,
        )
    else:
        st.dataframe(tampil, use_container_width=True, hide_index=True)
