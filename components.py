"""Komponen visual bersama, mengikuti bahasa desain Google Stitch.

Semua fungsi di sini hanya menghasilkan HTML/CSS; tidak ada logika bisnis.
Tujuannya supaya semua halaman punya header, kartu, badge, dan banner yang sama.
"""
from __future__ import annotations

import textwrap

import streamlit as st

TINT = ("mint", "lavender", "peach", "sky", "butter", "rose")


def html(teks: str, target=None) -> None:
    """Render HTML tanpa risiko dianggap blok kode markdown.

    Markdown memperlakukan baris yang menjorok 4 spasi sebagai code block, jadi
    HTML di-dedent dulu lalu spasi di awal/akhir dibuang. `target` bisa kolom
    atau container Streamlit; default ke halaman utama.
    """
    (target or st).markdown(
        textwrap.dedent(teks).strip(), unsafe_allow_html=True
    )


def rupiah(n) -> str:
    """Format angka jadi Rp 1.234.567."""
    try:
        return f"Rp {int(n):,}".replace(",", ".")
    except (TypeError, ValueError):
        return "Rp 0"


def angka(n) -> str:
    """Format angka ribuan tanpa Rp."""
    try:
        return f"{int(n):,}".replace(",", ".")
    except (TypeError, ValueError):
        return "0"


def page_header(judul: str, subjudul: str = "", aksi: str = "") -> None:
    """Header halaman: judul besar + subjudul abu, opsional label aksi di kanan."""
    aksi_html = (
        f'<div class="hdr-aksi">{aksi}</div>' if aksi else ""
    )
    html(
        f"""
        <div class="hdr">
          <div>
            <div class="hdr-judul">{judul}</div>
            <div class="hdr-sub">{subjudul}</div>
          </div>
          {aksi_html}
        </div>
        """
    )


def kpi(label: str, nilai: str, tint: str = "mint", catatan: str = "") -> str:
    """HTML kartu KPI pastel: label kecil, angka besar, catatan opsional."""
    catatan_html = f'<div class="kpi-catatan">{catatan}</div>' if catatan else ""
    return textwrap.dedent(
        f"""
        <div class="kpi tint-{tint}">
          <div class="kpi-label">{label}</div>
          <div class="kpi-nilai">{nilai}</div>
          {catatan_html}
        </div>
        """
    ).strip()


def kpi_ke(kolom, label: str, nilai: str, tint: str = "mint",
           catatan: str = "") -> None:
    """Render kartu KPI ke kolom/container tertentu."""
    html(kpi(label, nilai, tint, catatan), target=kolom)


def badge(teks: str, warna: str = "netral") -> str:
    """HTML badge pill kecil."""
    return f'<span class="pill pill-{warna}">{teks}</span>'


def banner(teks: str, jenis: str = "warning", ikon: str = "⚠️") -> None:
    """Banner peringatan/info selebar konten."""
    html(
        f"""
        <div class="banner banner-{jenis}">
          <span class="banner-ikon">{ikon}</span>
          <span>{teks}</span>
        </div>
        """
    )


def judul_bagian(teks: str, kanan: str = "") -> None:
    """Judul section + keterangan kecil di kanan."""
    kanan_html = f'<span class="bagian-kanan">{kanan}</span>' if kanan else ""
    html(f'<div class="bagian"><span>{teks}</span>{kanan_html}</div>')


def progress_list(baris: list[tuple]) -> None:
    """Daftar item dengan progress bar.

    baris: (nama, nilai, warna) atau (nama, nilai, warna, label_tampil).
    warna: 'ungu' atau 'mint'.
    """
    if not baris:
        st.caption("Belum ada data.")
        return
    maks = max(b[1] for b in baris) or 1
    item = []
    for b in baris:
        nama, nilai, warna = b[0], b[1], b[2]
        label = b[3] if len(b) > 3 else angka(nilai)
        persen = max(4, round(nilai / maks * 100))
        item.append(
            f'<div class="pl-item">'
            f'<div class="pl-atas">'
            f'<span class="pl-nama">{nama}</span>'
            f'<span class="pl-nilai">{label}</span>'
            f"</div>"
            f'<div class="pl-track">'
            f'<div class="pl-fill pl-{warna}" style="width:{persen}%"></div>'
            f"</div></div>"
        )
    html(f'<div class="pl">{"".join(item)}</div>')
