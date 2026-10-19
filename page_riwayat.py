"""Halaman Riwayat: filter tanggal, KPI, tren omzet, daftar transaksi.

Semua angka dari data/transaksi.csv.
"""
from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

import components as ui

METODE_TINT = {"Tunai": "mint", "QRIS": "lavender", "Debit": "sky"}


def _tren(harian: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=harian["tanggal"], y=harian["total_bayar"],
            mode="lines+markers",
            line=dict(color="#7C6BB8", width=3, shape="spline"),
            marker=dict(size=6, color="#7C6BB8"),
            fill="tozeroy",
            fillcolor="rgba(124,107,184,0.12)",
            hovertemplate="%{x|%d %b %Y}<br>Rp %{y:,.0f}<extra></extra>",
        )
    )
    fig.update_layout(
        height=260,
        margin=dict(l=4, r=6, t=10, b=34),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        showlegend=False,
        xaxis=dict(
            showgrid=False,
            tickformat="%d %b",
            nticks=7,
            tickfont=dict(size=11, color="#6E6B7B"),
        ),
        yaxis=dict(
            showgrid=True, gridcolor="#F1EFF5", zeroline=False,
            tickformat=",.0f",
            tickfont=dict(size=11, color="#6E6B7B"),
        ),
        hoverlabel=dict(bgcolor="#FFFFFF", bordercolor="#EDE9F2",
                        font=dict(color="#3B3A47")),
    )
    return fig


def render(data: dict) -> None:
    trx = data["transaksi"].copy()
    trx["tanggal"] = pd.to_datetime(trx["tanggal_waktu"]).dt.date
    min_d, max_d = trx["tanggal"].min(), trx["tanggal"].max()

    ui.page_header(
        "Riwayat Transaksi",
        "Pantau penjualan dan tren omzet.",
        aksi=f"{len(trx)} transaksi",
    )

    pilihan = st.pills(
        "Rentang",
        ["7 hari", "30 hari", "Semua", "Pilih tanggal"],
        default="30 hari",
        label_visibility="collapsed",
    )

    if pilihan == "Pilih tanggal":
        d1, d2 = st.columns(2)
        start = d1.date_input("Dari", max_d - pd.Timedelta(days=30),
                              min_value=min_d, max_value=max_d)
        end = d2.date_input("Sampai", max_d, min_value=min_d, max_value=max_d)
    elif pilihan == "7 hari":
        start, end = max_d - pd.Timedelta(days=6), max_d
    elif pilihan == "30 hari":
        start, end = max_d - pd.Timedelta(days=29), max_d
    else:
        start, end = min_d, max_d

    filtered = trx[(trx["tanggal"] >= start) & (trx["tanggal"] <= end)]
    omzet = int(filtered["total_bayar"].sum())
    rata = int(omzet / len(filtered)) if len(filtered) else 0
    harian = filtered.groupby("tanggal")["total_bayar"].sum().reset_index()

    k1, k2, k3 = st.columns(3)
    ui.kpi_ke(k1, "Omzet", ui.rupiah(omzet), "mint", f"{start} → {end}")
    ui.kpi_ke(k2, "Transaksi", ui.angka(len(filtered)), "lavender",
              "dalam rentang")
    ui.kpi_ke(k3, "Rata-rata / transaksi", ui.rupiah(rata), "peach",
              "nilai keranjang")

    ui.judul_bagian("Tren omzet harian", f"{len(harian)} hari")
    if harian.empty:
        st.info("Tidak ada transaksi pada rentang ini.")
    else:
        st.plotly_chart(
            _tren(harian), use_container_width=True,
            config={"displayModeBar": False},
        )

    kiri, kanan = st.columns([1.4, 1], gap="large")

    with kiri:
        ui.judul_bagian("Transaksi terakhir", f"{min(12, len(filtered))} dari "
                                             f"{len(filtered)}")
        terbaru = filtered.sort_values("tanggal_waktu", ascending=False).head(12)
        for _, r in terbaru.iterrows():
            tint = METODE_TINT.get(str(r["metode_pembayaran"]), "netral")
            waktu = pd.to_datetime(r["tanggal_waktu"]).strftime("%d %b %Y · %H:%M")
            ui.html(
                f'<div class="trx-item">'
                f'<div>'
                f'<div class="trx-id">{r["id_transaksi"]}</div>'
                f'<div class="trx-meta">{waktu} · {r["id_kasir"]}</div>'
                f"</div>"
                f'<div class="trx-kanan">'
                f'<div class="trx-nilai">{ui.rupiah(r["total_bayar"])}</div>'
                f'<span class="pill pill-{tint}">{r["metode_pembayaran"]}</span>'
                f"</div></div>"
            )

    with kanan:
        ui.judul_bagian("Metode bayar", "komposisi")
        komposisi = (
            filtered.groupby("metode_pembayaran")["total_bayar"]
            .sum().sort_values(ascending=False)
        )
        ui.progress_list([
            (str(k), int(v), METODE_TINT.get(str(k), "ungu"), ui.rupiah(v))
            for k, v in komposisi.items()
        ])

        ui.judul_bagian("Omzet per kasir", "teratas")
        per_kasir = (
            filtered.groupby("id_kasir")["total_bayar"].sum()
            .sort_values(ascending=False).head(8)
        )
        ui.progress_list([
            (str(k), int(v), "ungu", ui.rupiah(v)) for k, v in per_kasir.items()
        ])

    with st.expander("Tabel lengkap"):
        st.dataframe(
            filtered.sort_values("tanggal_waktu", ascending=False),
            use_container_width=True, hide_index=True,
        )
