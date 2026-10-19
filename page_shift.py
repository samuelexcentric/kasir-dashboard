"""Halaman Shift: status shift aktif, sisa waktu, dan omzet per shift."""
from __future__ import annotations

import datetime

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

import components as ui
import core

NAMA_SHIFT = [("Pagi", "08–16"), ("Siang", "16–24"), ("Malam", "00–08")]


def _bar(omzet: dict) -> go.Figure:
    nama = list(omzet.keys())
    nilai = [int(v) for v in omzet.values()]
    warna = ["#A9D9C2", "#C9BDE8", "#FFD2B3"][: len(nama)]
    fig = go.Figure(
        go.Bar(
            x=nama, y=nilai,
            marker=dict(color=warna, line=dict(width=0)),
            text=[ui.rupiah(v) for v in nilai],
            textposition="outside",
            textfont=dict(size=11, color="#6E6B7B"),
            hovertemplate="%{x}<br>Rp %{y:,.0f}<extra></extra>",
        )
    )
    fig.update_layout(
        height=250,
        margin=dict(l=6, r=6, t=26, b=28),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(
            showgrid=False, tickfont=dict(size=12, color="#55505F"),
            type="category",
        ),
        yaxis=dict(
            showgrid=True, gridcolor="#F1EFF5", visible=False,
            range=[0, max(max(nilai), 1) * 1.35],
        ),
        bargap=.45,
    )
    return fig


def render(data: dict) -> None:
    now = datetime.datetime.now()
    nama_shift = core.shift_aktif(now)
    mulai = st.session_state.shift_start
    sisa = core.sisa_waktu_shift(mulai, now)
    habis = sisa == datetime.timedelta(0)

    ui.page_header(
        "Shift Kasir",
        "Status shift berjalan dan rekap omzet.",
        aksi=nama_shift,
    )

    total_detik = max(0, int(sisa.total_seconds()))
    jam, sisa_detik = divmod(total_detik, 3600)
    menit = sisa_detik // 60

    if habis:
        ui.banner(core.notifikasi_pulang(mulai), "warning", "⏰")
    else:
        ui.banner(
            f"Shift <b>{nama_shift}</b> berjalan — sisa "
            f"<b>{jam} jam {menit} menit</b>.",
            "ok", "🕒",
        )

    k1, k2, k3 = st.columns(3)
    ui.kpi_ke(k1, "Shift aktif", nama_shift, "mint", "jadwal berjalan")
    ui.kpi_ke(k2, "Sisa waktu", f"{jam}j {menit}m" if not habis else "Selesai",
               "lavender", "dari 8 jam")
    ui.kpi_ke(k3, "Mulai shift", mulai.strftime("%H:%M") if mulai else "-",
              "peach", str(now.date()))

    kiri, kanan = st.columns([1.25, 1], gap="large")

    with kiri:
        ui.judul_bagian("Omzet per shift hari ini", str(now.date()))
        trx = data["transaksi"].copy()
        trx["tanggal"] = pd.to_datetime(trx["tanggal_waktu"]).dt.date
        omzet = core.omzet_per_shift(
            trx.to_dict(orient="records"), now.date().isoformat()
        )
        if omzet and sum(omzet.values()) > 0:
            st.plotly_chart(
                _bar(omzet), use_container_width=True,
                config={"displayModeBar": False},
            )
        else:
            ui.html(
                '<div class="keranjang-kosong">📉<br>Belum ada omzet hari ini.<br>'
                "<span>Transaksi akan muncul di sini.</span></div>"
            )

    with kanan:
        ui.judul_bagian("Jadwal shift", "3 shift")
        for nama, jam in NAMA_SHIFT:
            aktif = nama == nama_shift
            ui.html(f"""
                <div class="shift-item{' aktif' if aktif else ''}">
                  <div>
                    <div class="shift-nama">{nama}</div>
                    <div class="shift-jam">{jam}</div>
                  </div>
                  {'<span class="pill pill-ungu">aktif</span>' if aktif
                   else '<span class="pill pill-netral">terjadwal</span>'}
                </div>
                """)
