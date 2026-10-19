"""Tema pastel untuk dashboard kasir.

Satu tempat untuk semua warna & CSS. `apply()` dipanggil sekali di app.py
setelah st.set_page_config(), lalu seluruh halaman ikut tema ini tanpa perlu
diubah satu per satu.
"""
from __future__ import annotations

import streamlit as st

# --------------------------------------------------------------------------
# Palet
# --------------------------------------------------------------------------
PALETTE = {
    # tint lembut untuk latar kartu
    "mint": "#DFF3E9",
    "lavender": "#EAE4F8",
    "peach": "#FFE8D9",
    "sky": "#E1EEF9",
    "butter": "#FDF3D8",
    "rose": "#FBE4EA",
    # versi lebih pekat untuk garis aksen / teks di atas tint
    "mint_deep": "#5FA88B",
    "lavender_deep": "#7C6BB8",
    "peach_deep": "#D98A5B",
    "sky_deep": "#4A87B8",
    "butter_deep": "#B08D2E",
    "rose_deep": "#C2687F",
    # netral
    "ink": "#3B3A47",
    "ink_soft": "#6E6B7B",
    "line": "#EDE9F2",
    "canvas": "#FDFCFB",
}

# Urutan warna untuk chart supaya plotly ikut pastel
CHART_COLORS = [
    "#8FC7AE",  # mint
    "#A99BD9",  # lavender
    "#F0A882",  # peach
    "#8FB8DE",  # sky
    "#E3C878",  # butter
    "#E09BAB",  # rose
]

_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');

:root {
  --mint: %(mint)s;
  --lavender: %(lavender)s;
  --peach: %(peach)s;
  --sky: %(sky)s;
  --butter: %(butter)s;
  --rose: %(rose)s;
  --mint-deep: %(mint_deep)s;
  --lavender-deep: %(lavender_deep)s;
  --ink: %(ink)s;
  --ink-soft: %(ink_soft)s;
  --line: %(line)s;
  --radius: 16px;
  --shadow: 0 1px 2px rgba(59,58,71,.04), 0 8px 24px rgba(59,58,71,.05);
}

/* ---------- dasar ---------- */
html, body, [class*="css"], .stApp,
h1, h2, h3, h4, h5, h6, p, span, div, label, li, td, th, input, textarea, button {
  font-family: 'Plus Jakarta Sans', -apple-system, 'Segoe UI', system-ui, sans-serif !important;
  color: var(--ink);
}
/* Ikon Streamlit memakai ligature font Material — jangan ikut font teks,
   kalau tidak ikonnya muncul sebagai tulisan seperti "keyboard_arrow_right". */
[data-testid="stIconMaterial"],
[data-testid="stIconMaterial"] *,
span[data-testid="stIconMaterial"],
.material-symbols-rounded,
[class*="material-icons"] {
  font-family: 'Material Symbols Rounded', 'Material Icons' !important;
  font-feature-settings: 'liga' !important;
  letter-spacing: normal !important;
  text-transform: none !important;
}

/* Streamlit menyimpan font di variabel ini; samakan agar komponen internal ikut */
:root, .stApp, [data-testid="stAppViewContainer"] {
  --font: 'Plus Jakarta Sans', -apple-system, 'Segoe UI', system-ui, sans-serif;
  --heading-font: 'Plus Jakarta Sans', -apple-system, 'Segoe UI', system-ui, sans-serif;
  --body-font: 'Plus Jakarta Sans', -apple-system, 'Segoe UI', system-ui, sans-serif;
}

.stApp {
  background:
    radial-gradient(1200px 500px at 8% -8%, #F3EEFB 0%, rgba(243,238,251,0) 60%),
    radial-gradient(1000px 460px at 96% 2%, #E9F6F0 0%, rgba(233,246,240,0) 55%),
    #FDFCFB;
}

[data-testid="stHeader"] { background: transparent; }

.block-container {
  padding-top: 2.4rem;
  padding-bottom: 3rem;
  max-width: 1180px;
}

/* ---------- judul ---------- */
h1 {
  font-weight: 700 !important;
  letter-spacing: -.02em;
  color: var(--ink);
}
h2, h3 {
  font-weight: 600 !important;
  letter-spacing: -.01em;
  color: var(--ink);
}
/* garis bawah dekoratif di judul halaman */
h3 {
  padding-bottom: .55rem;
  border-bottom: 2px solid var(--line);
}

/* ---------- sidebar ---------- */
[data-testid="stSidebar"] {
  background: linear-gradient(180deg, #F7F3FD 0%, #F2F8F5 100%);
  border-right: 1px solid var(--line);
}
[data-testid="stSidebar"] .block-container { padding-top: 1.6rem; }

/* menu radio -> tombol pastel */
[data-testid="stSidebar"] [role="radiogroup"] { gap: .3rem; }
[data-testid="stSidebar"] [role="radiogroup"] label {
  padding: .5rem .7rem;
  border-radius: 12px;
  transition: background .15s ease, transform .15s ease;
}
[data-testid="stSidebar"] [role="radiogroup"] label:hover {
  background: rgba(255,255,255,.75);
}
[data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) {
  background: #FFFFFF;
  box-shadow: 0 1px 2px rgba(59,58,71,.06), 0 4px 14px rgba(124,107,184,.10);
  font-weight: 600;
}

/* ---------- metrik ---------- */
[data-testid="stMetric"] {
  background: #FFFFFF;
  border: 1px solid var(--line);
  border-radius: var(--radius);
  padding: 1rem 1.1rem;
  box-shadow: var(--shadow);
  height: 100%;
}
[data-testid="stMetric"] p, [data-testid="stMetric"] span, [data-testid="stMetric"] div {
  color: inherit;
}
[data-testid="stMetricLabel"] p {
  font-size: .78rem !important;
  font-weight: 600 !important;
  letter-spacing: .04em;
  text-transform: uppercase;
  color: var(--ink-soft) !important;
}
[data-testid="stMetricValue"] {
  font-size: 1.5rem !important;
  font-weight: 700 !important;
  letter-spacing: -.02em;
  color: var(--ink);
}
/* nilai utama sedikit lebih tegas dari labelnya */
[data-testid="stMetricValue"] > div { color: var(--ink) !important; }

/* warna tint berbeda per kolom supaya tidak monoton */
[data-testid="stHorizontalBlock"] > div:nth-child(6n+1) [data-testid="stMetric"] { background: var(--mint); border-color: transparent; }
[data-testid="stHorizontalBlock"] > div:nth-child(6n+2) [data-testid="stMetric"] { background: var(--lavender); border-color: transparent; }
[data-testid="stHorizontalBlock"] > div:nth-child(6n+3) [data-testid="stMetric"] { background: var(--peach); border-color: transparent; }
[data-testid="stHorizontalBlock"] > div:nth-child(6n+4) [data-testid="stMetric"] { background: var(--sky); border-color: transparent; }
[data-testid="stHorizontalBlock"] > div:nth-child(6n+5) [data-testid="stMetric"] { background: var(--butter); border-color: transparent; }
[data-testid="stHorizontalBlock"] > div:nth-child(6n+6) [data-testid="stMetric"] { background: var(--rose); border-color: transparent; }

/* ---------- tombol ---------- */
.stButton > button, .stDownloadButton > button, .stFormSubmitButton > button {
  border-radius: 12px;
  font-weight: 600;
  padding: .5rem 1.1rem;
  transition: transform .12s ease, box-shadow .12s ease, background .15s ease;
}
.stButton > button:hover, .stDownloadButton > button:hover, .stFormSubmitButton > button:hover {
  transform: translateY(-1px);
  box-shadow: 0 6px 18px rgba(59,58,71,.10);
}
/* tombol sekunder: pastel lembut */
.stButton > button[kind="secondary"],
.stFormSubmitButton > button[kind="secondary"],
.stDownloadButton > button {
  background: #FFFFFF;
  border: 1px solid var(--line);
  color: var(--ink);
}
/* tombol utama: lavender pekat, teks putih */
.stButton > button[kind="primary"],
.stFormSubmitButton > button[kind="primary"] {
  background: #7C6BB8;
  border: 1px solid #7C6BB8;
  color: #FFFFFF;
  box-shadow: 0 4px 14px rgba(124,107,184,.28);
}
.stButton > button[kind="primary"]:hover,
.stFormSubmitButton > button[kind="primary"]:hover {
  background: #6E5DA9;
  border-color: #6E5DA9;
}

/* ---------- input ---------- */
[data-baseweb="input"], [data-baseweb="select"] > div, [data-baseweb="textarea"] {
  border-radius: 12px !important;
  background: #FFFFFF !important;
  border-color: var(--line) !important;
}
[data-baseweb="input"]:focus-within,
[data-baseweb="select"] > div:focus-within {
  border-color: #A99BD9 !important;
  box-shadow: 0 0 0 3px rgba(169,155,217,.20) !important;
}

/* ---------- kartu generik: form, expander, dataframe ---------- */
[data-testid="stForm"] {
  background: #FFFFFF;
  border: 1px solid var(--line);
  border-radius: var(--radius);
  padding: 1.2rem 1.3rem;
  box-shadow: var(--shadow);
}

[data-testid="stExpander"] {
  background: #FFFFFF;
  border: 1px solid var(--line);
  border-radius: var(--radius);
  box-shadow: var(--shadow);
  overflow: hidden;
}
[data-testid="stExpander"] summary { font-weight: 600; padding: .85rem 1.1rem; }

[data-testid="stDataFrame"], [data-testid="stTable"] {
  border: 1px solid var(--line);
  border-radius: 14px;
  overflow: hidden;
  background: #FFFFFF;
  box-shadow: var(--shadow);
}

[data-testid="stPlotlyChart"] {
  background: #FFFFFF;
  border: 1px solid var(--line);
  border-radius: var(--radius);
  padding: .6rem .5rem;
  box-shadow: var(--shadow);
}

/* ---------- alert / toast ---------- */
[data-testid="stAlert"] {
  border-radius: 14px;
  border: 1px solid transparent;
}
[data-testid="stAlertContentSuccess"] { background: var(--mint); }
[data-testid="stAlertContentInfo"] { background: var(--sky); }
[data-testid="stAlertContentWarning"] { background: var(--butter); }
[data-testid="stAlertContentError"] { background: var(--rose); }

/* ---------- progress & caption ---------- */
.stProgress > div > div > div > div {
  background: linear-gradient(90deg, #8FC7AE, #A99BD9) !important;
  border-radius: 99px;
}
[data-testid="stCaptionContainer"] p { color: var(--ink-soft); }


/* ---------- halaman Kasir: katalog kartu ---------- */
.produk-kartu {
  background: #FFFFFF;
  border: 1px solid var(--line);
  border-radius: var(--radius);
  padding: .9rem .95rem .7rem;
  box-shadow: var(--shadow);
  margin-bottom: .55rem;
  transition: transform .14s ease, box-shadow .14s ease;
}
.produk-kartu:hover {
  transform: translateY(-2px);
  box-shadow: 0 2px 4px rgba(59,58,71,.05), 0 12px 28px rgba(59,58,71,.09);
}
/* tint tipis di kepala kartu sesuai kategori */
.produk-kartu.tint-mint    { background: linear-gradient(180deg, var(--mint) 0%, #FFFFFF 62%); }
.produk-kartu.tint-lavender{ background: linear-gradient(180deg, var(--lavender) 0%, #FFFFFF 62%); }
.produk-kartu.tint-peach   { background: linear-gradient(180deg, var(--peach) 0%, #FFFFFF 62%); }
.produk-kartu.tint-sky     { background: linear-gradient(180deg, var(--sky) 0%, #FFFFFF 62%); }
.produk-kartu.tint-butter  { background: linear-gradient(180deg, var(--butter) 0%, #FFFFFF 62%); }
.produk-kartu.tint-rose    { background: linear-gradient(180deg, var(--rose) 0%, #FFFFFF 62%); }

.produk-atas {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: .55rem;
}
.produk-ikon {
  font-size: 1.55rem;
  line-height: 1;
  background: #FFFFFF;
  border-radius: 12px;
  padding: .35rem .5rem;
  box-shadow: 0 1px 3px rgba(59,58,71,.08);
}
.produk-nama {
  font-weight: 600;
  font-size: .92rem;
  line-height: 1.25;
  color: var(--ink);
  min-height: 2.3em;
}
.produk-kategori {
  font-size: .74rem;
  color: var(--ink-soft);
  margin-bottom: .5rem;
}
.produk-bawah { display: flex; align-items: baseline; }
.produk-harga {
  font-weight: 700;
  font-size: 1rem;
  letter-spacing: -.01em;
  color: var(--ink);
}

/* badge stok */
.badge-stok {
  font-size: .68rem;
  font-weight: 700;
  letter-spacing: .02em;
  padding: .2rem .5rem;
  border-radius: 99px;
  white-space: nowrap;
}
.badge-aman    { background: var(--mint);     color: #2F6E52; }
.badge-menipis { background: var(--butter);   color: #8A6B14; }
.badge-habis   { background: var(--rose);     color: #A8455C; }

/* header katalog */
.katalog-info {
  display: flex;
  align-items: center;
  gap: .5rem;
  font-weight: 600;
  font-size: .95rem;
  margin: .6rem 0 .8rem;
}
.katalog-jumlah {
  font-size: .72rem;
  font-weight: 700;
  color: #6E5DA9;
  background: var(--lavender);
  padding: .15rem .5rem;
  border-radius: 99px;
}

/* ---------- keranjang ---------- */
.keranjang-judul {
  font-weight: 700;
  font-size: 1rem;
  padding-bottom: .5rem;
  margin-bottom: .8rem;
  border-bottom: 2px solid var(--line);
}
.keranjang-kosong {
  text-align: center;
  color: var(--ink-soft);
  font-size: .85rem;
  line-height: 1.6;
  background: #FFFFFF;
  border: 1px dashed var(--line);
  border-radius: var(--radius);
  padding: 2.2rem 1rem;
}
.keranjang-item {
  background: #FFFFFF;
  border: 1px solid var(--line);
  border-radius: 14px;
  padding: .7rem .85rem;
  margin-bottom: .35rem;
  box-shadow: 0 1px 2px rgba(59,58,71,.04);
}
.keranjang-nama {
  font-weight: 600;
  font-size: .86rem;
  line-height: 1.3;
  margin-bottom: .2rem;
}
.keranjang-meta { font-size: .76rem; color: var(--ink-soft); }

.keranjang-total {
  background: linear-gradient(135deg, var(--lavender) 0%, var(--mint) 100%);
  border-radius: var(--radius);
  padding: .9rem 1rem;
  margin: .8rem 0 .7rem;
  display: flex;
  align-items: baseline;
  justify-content: space-between;
}
.keranjang-total-label {
  font-size: .76rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: .04em;
  color: #4A4356;
}
.keranjang-total-nilai {
  font-size: 1.35rem;
  font-weight: 700;
  letter-spacing: -.02em;
  color: #3B3A47;
}

/* tombol kecil di keranjang (qty −/+) */
[data-testid="stVerticalBlock"] .stButton > button[kind="secondary"] {
  min-height: 2rem;
}


/* panel keranjang menempel saat katalog di-scroll */
[data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:last-child:has(.keranjang-judul) {
  position: sticky;
  top: .5rem;
  align-self: flex-start;
}
/* daftar item keranjang: scroll internal, scrollbar halus */
[data-testid="stVerticalBlockBorderWrapper"]:has(.keranjang-item) > div,
div:has(> [data-testid="stVerticalBlock"] .keranjang-item) {
  scrollbar-width: thin;
}
[data-testid="stColumn"]:last-child [data-testid="stVerticalBlockBorderWrapper"]::-webkit-scrollbar {
  width: 6px;
}
[data-testid="stColumn"]:last-child [data-testid="stVerticalBlockBorderWrapper"]::-webkit-scrollbar-thumb {
  background: #DDD6EC;
  border-radius: 99px;
}
/* stepper −/+ dibuat ringkas & simetris */
[data-testid="stColumn"]:last-child [data-testid="stHorizontalBlock"] .stButton > button {
  min-height: 2.1rem;
  padding: .2rem .4rem;
  border-radius: 10px;
  font-weight: 700;
}


/* ============ bahasa desain Stitch: header, KPI, pill, banner ============ */
.hdr {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
  margin: .2rem 0 1.1rem;
}
.hdr-judul {
  font-size: 1.62rem;
  font-weight: 800;
  letter-spacing: -.025em;
  line-height: 1.15;
  color: var(--ink);
}
.hdr-sub {
  font-size: .82rem;
  color: var(--ink-soft);
  margin-top: .2rem;
}
.hdr-aksi {
  font-size: .72rem;
  font-weight: 700;
  color: #6E5DA9;
  background: var(--lavender);
  padding: .3rem .7rem;
  border-radius: 99px;
  white-space: nowrap;
}

/* KPI card */
.kpi {
  border-radius: 18px;
  padding: 1rem 1.1rem;
  margin-bottom: .2rem;
  box-shadow: 0 1px 2px rgba(59,58,71,.05), 0 6px 18px rgba(59,58,71,.05);
  border: 1px solid rgba(255,255,255,.7);
}
.kpi-label {
  font-size: .7rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: .06em;
  color: #55505F;
  margin-bottom: .35rem;
}
.kpi-nilai {
  font-size: 1.42rem;
  font-weight: 800;
  letter-spacing: -.03em;
  line-height: 1.1;
  color: #2F2C3A;
  font-variant-numeric: tabular-nums;
}
.kpi-catatan {
  font-size: .72rem;
  color: #5B5668;
  margin-top: .3rem;
}
.kpi.tint-mint     { background: linear-gradient(150deg, #E7F7EF 0%, #D8F0E5 100%); }
.kpi.tint-lavender { background: linear-gradient(150deg, #F1ECFB 0%, #E6DEF8 100%); }
.kpi.tint-peach    { background: linear-gradient(150deg, #FFF1E7 0%, #FFE4D2 100%); }
.kpi.tint-sky      { background: linear-gradient(150deg, #EAF4FB 0%, #DCEDF8 100%); }
.kpi.tint-butter   { background: linear-gradient(150deg, #FFF9E8 0%, #FCF1CF 100%); }
.kpi.tint-rose     { background: linear-gradient(150deg, #FDEEF2 0%, #FBE0E8 100%); }

/* pill / badge */
.pill {
  display: inline-block;
  font-size: .68rem;
  letter-spacing: .01em;
  font-weight: 700;
  padding: .2rem .55rem;
  border-radius: 99px;
  white-space: nowrap;
  line-height: 1.5;
}
.pill-aman    { background: #D8F0E5; color: #2F6E52; }
.pill-menipis { background: #FCF1CF; color: #8A6B14; }
.pill-habis   { background: #FBE0E8; color: #A8455C; }
.pill-netral  { background: #F1EFF5; color: #5B5668; }
.pill-ungu    { background: #E6DEF8; color: #6E5DA9; }
.pill-mint     { background: #D8F0E5; color: #2F6E52; }
.pill-lavender { background: #E6DEF8; color: #6E5DA9; }
.pill-peach    { background: #FFE3CE; color: #8A4B22; }
.pill-sky      { background: #DCEBF7; color: #2F5C7A; }
.pill-butter   { background: #FCF1CF; color: #8A6B14; }
.pill-rose     { background: #FBE0E8; color: #A8455C; }

/* banner peringatan */
.banner {
  display: flex;
  align-items: center;
  gap: .65rem;
  border-radius: 14px;
  padding: .8rem 1rem;
  font-size: .84rem;
  font-weight: 500;
  line-height: 1.45;
  margin: .2rem 0 .9rem;
}
.banner-ikon { font-size: 1.05rem; }
.banner-warning { background: #FFF1E7; color: #8A4B22; border: 1px solid #FFE0C9; }
.banner-info    { background: #EAF4FB; color: #2F5C7A; border: 1px solid #D8E9F5; }
.banner-ok      { background: #E7F7EF; color: #2F6E52; border: 1px solid #D3EFE2; }

/* judul bagian */
.bagian {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  font-size: .95rem;
  font-weight: 700;
  color: var(--ink);
  margin: 1rem 0 .65rem;
}
.bagian-kanan {
  font-size: .72rem;
  font-weight: 600;
  color: var(--ink-soft);
}

/* progress list */
.pl { display: flex; flex-direction: column; gap: .62rem; }
.pl-atas {
  display: flex;
  justify-content: space-between;
  font-size: .78rem;
  margin-bottom: .22rem;
}
.pl-nama {
  color: #45404F;
  font-weight: 500;
  overflow-wrap: anywhere;
}
.pl-nilai { color: #6E6B7B; font-weight: 700; font-variant-numeric: tabular-nums; }
.pl-track {
  height: 7px;
  background: #F1EFF5;
  border-radius: 99px;
  overflow: hidden;
}
.pl-fill { height: 100%; border-radius: 99px; }
.pl-ungu,
.pl-lavender { background: linear-gradient(90deg, #A392D8 0%, #7C6BB8 100%); }
.pl-mint     { background: linear-gradient(90deg, #9FD3B8 0%, #5FA88B 100%); }
.pl-peach    { background: linear-gradient(90deg, #FFC49B 0%, #D98A5B 100%); }
.pl-sky      { background: linear-gradient(90deg, #9CC6E4 0%, #4A87B8 100%); }
.pl-butter   { background: linear-gradient(90deg, #EFD98F 0%, #B08D2E 100%); }
.pl-rose     { background: linear-gradient(90deg, #EFA9BC 0%, #C2687F 100%); }

/* pratinjau laporan (halaman export) */
.lapor {
  background: #FFFFFF;
  border: 1px solid var(--line);
  border-radius: 16px;
  padding: .35rem .2rem;
  box-shadow: 0 1px 2px rgba(59, 58, 71, .04);
}
.lapor-baris {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: .62rem 1rem;
  font-size: .86rem;
  color: var(--ink-soft);
  border-bottom: 1px solid #F4F1F8;
}
.lapor-baris:last-child { border-bottom: none; }
.lapor-baris b {
  color: var(--ink);
  font-variant-numeric: tabular-nums;
  font-weight: 700;
}
.lapor-baris.tebal {
  background: #FAF7FE;
  border-radius: 12px;
  color: var(--ink);
  font-weight: 600;
}
.lapor-baris.tebal b { color: #6E5DA9; }

/* chip pill native (st.pills) disamakan dengan desain */
[data-testid="stPills"] button {
  border-radius: 99px !important;
  font-size: .78rem !important;
  font-weight: 600 !important;
  padding: .28rem .85rem !important;
  min-height: 2rem !important;
  border: 1px solid var(--line) !important;
  background: #FFFFFF !important;
  color: #55505F !important;
}
[data-testid="stPills"] button[aria-checked="true"] {
  background: #7C6BB8 !important;
  border-color: #7C6BB8 !important;
  color: #FFFFFF !important;
  font-weight: 700 !important;
}
[data-testid="stPills"] button:hover {
  border-color: #C9BDE8 !important;
  background: #F7F3FD !important;
}
[data-testid="stPills"] button[aria-checked="true"]:hover {
  background: #6E5DA9 !important;
}

/* tombol primary: pill penuh seperti Stitch */
.stButton > button[kind="primary"],
.stFormSubmitButton > button[kind="primary"] {
  border-radius: 99px !important;
  font-weight: 700 !important;
  padding: .5rem 1.1rem !important;
}


/* stok */
.stok-ikon {
  font-size: 1.9rem;
  line-height: 1;
  margin: .45rem 0 .35rem;
}
.stok-meta {
  font-size: .7rem;
  color: #5B5668;
  margin-top: .15rem;
}
.restock-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: .5rem;
  font-size: .8rem;
  color: #45404F;
  padding: .42rem .6rem;
  border-radius: 10px;
  background: #FDF8F4;
  margin-bottom: .3rem;
}

/* transaksi */
.trx-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: .6rem;
  padding: .58rem .75rem;
  border-radius: 12px;
  background: #FFFFFF;
  border: 1px solid var(--line);
  margin-bottom: .38rem;
}
.trx-id {
  font-size: .82rem;
  font-weight: 700;
  color: var(--ink);
}
.trx-meta {
  font-size: .68rem;
  color: var(--ink-soft);
  margin-top: .1rem;
}
.trx-kanan { text-align: right; }
.trx-nilai {
  font-size: .86rem;
  font-weight: 800;
  color: #2F2C3A;
  font-variant-numeric: tabular-nums;
  margin-bottom: .12rem;
}

/* shift */
.shift-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: .6rem;
  padding: .6rem .8rem;
  border-radius: 13px;
  background: #FFFFFF;
  border: 1px solid var(--line);
  margin-bottom: .4rem;
}
.shift-item.aktif {
  background: linear-gradient(140deg, #F1ECFB 0%, #E6DEF8 100%);
  border-color: #D9CDF2;
}
.shift-nama { font-size: .85rem; font-weight: 700; color: var(--ink); }
.shift-jam { font-size: .7rem; color: var(--ink-soft); margin-top: .1rem; }


/* login */
.login-kartu { text-align: center; margin: 2.4rem 0 1.6rem; }
.login-ikon { font-size: 2.6rem; line-height: 1; }
.login-judul {
  font-size: 1.55rem;
  font-weight: 800;
  letter-spacing: -.03em;
  color: var(--ink);
  margin-top: .5rem;
}
.login-sub { font-size: .84rem; color: var(--ink-soft); margin-top: .25rem; }

/* sidebar */
.side-brand {
  display: flex;
  align-items: center;
  gap: .6rem;
  padding: .2rem 0 1.1rem;
}
.side-logo {
  width: 34px; height: 34px;
  display: grid; place-items: center;
  border-radius: 11px;
  background: linear-gradient(140deg, #F1ECFB 0%, #E6DEF8 100%);
  font-size: 1.05rem;
}
.side-nama { font-size: .92rem; font-weight: 800; color: var(--ink); }
.side-sub { font-size: .68rem; color: var(--ink-soft); }

.side-shift {
  border-radius: 13px;
  padding: .6rem .75rem;
  background: linear-gradient(140deg, #EAF4FB 0%, #DCEDF8 100%);
  margin: .3rem 0 .8rem;
}
.side-shift-label {
  font-size: .62rem;
  font-weight: 700;
  letter-spacing: .07em;
  text-transform: uppercase;
  color: #4A6C82;
}
.side-shift-nama { font-size: .88rem; font-weight: 800; color: #2F5C7A; }
.side-shift-sisa { font-size: .7rem; color: #4A6C82; margin-top: .1rem; }

.side-user {
  display: flex;
  align-items: center;
  gap: .55rem;
  padding: .55rem .7rem;
  border-radius: 13px;
  background: #FFFFFF;
  border: 1px solid var(--line);
  margin-bottom: .55rem;
}
.side-avatar {
  width: 30px; height: 30px;
  display: grid; place-items: center;
  border-radius: 99px;
  background: linear-gradient(140deg, #F1ECFB 0%, #E6DEF8 100%);
  font-size: .78rem;
  font-weight: 800;
  color: #6E5DA9;
}
.side-user-nama { font-size: .8rem; font-weight: 700; color: var(--ink); }
.side-user-role { font-size: .65rem; color: var(--ink-soft); text-transform: capitalize; }

/* radio sidebar jadi menu pill */
[data-testid="stSidebar"] [role="radiogroup"] { gap: .18rem !important; }
[data-testid="stSidebar"] [role="radiogroup"] > label {
  padding: .48rem .7rem !important;
  border-radius: 11px !important;
  transition: background .15s ease !important;
}
[data-testid="stSidebar"] [role="radiogroup"] > label:hover {
  background: #F7F3FD !important;
}
[data-testid="stSidebar"] [role="radiogroup"] > label:has(input:checked) {
  background: linear-gradient(140deg, #F1ECFB 0%, #E6DEF8 100%) !important;
}
[data-testid="stSidebar"] [role="radiogroup"] > label:has(input:checked) p {
  font-weight: 700 !important;
  color: #5F4E9C !important;
}
[data-testid="stSidebar"] [role="radiogroup"] p {
  font-size: .84rem !important;
  color: #4A4657 !important;
}
/* sembunyikan bulatan radio, sisakan label */
[data-testid="stSidebar"] [role="radiogroup"] label > div:first-child {
  display: none !important;
}


/* kartu produk: container Streamlit dijadikan kartu utuh (isi + tombol) */
[class*="st-key-kartu_"] {
  background: #FFFFFF;
  border: 1px solid var(--line);
  border-radius: 18px;
  padding: .8rem .8rem .7rem;
  box-shadow: 0 1px 2px rgba(59,58,71,.04), 0 6px 16px rgba(59,58,71,.05);
  transition: box-shadow .16s ease, transform .16s ease;
  height: 100%;
}
[class*="st-key-kartu_"]:hover {
  box-shadow: 0 2px 4px rgba(59,58,71,.06), 0 12px 26px rgba(59,58,71,.09);
  transform: translateY(-2px);
}
[class*="st-key-kartu_"] [data-testid="stMarkdownContainer"] p { margin: 0; }
[class*="st-key-kartu_"] .produk-atas {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: .4rem;
  margin-bottom: .45rem;
}
[class*="st-key-kartu_"] .produk-ikon {
  width: 34px; height: 34px;
  display: grid; place-items: center;
  border-radius: 11px;
  background: #F7F3FD;
  font-size: 1.05rem;
}
[class*="st-key-kartu_"] .produk-nama {
  font-size: .84rem;
  font-weight: 700;
  line-height: 1.32;
  color: var(--ink);
  min-height: 2.2em;
  margin-bottom: .15rem;
}
[class*="st-key-kartu_"] .produk-kategori {
  font-size: .68rem;
  color: var(--ink-soft);
  margin-bottom: .5rem;
}
[class*="st-key-kartu_"] .produk-harga {
  font-size: .95rem;
  font-weight: 800;
  letter-spacing: -.02em;
  color: #2F2C3A;
  font-variant-numeric: tabular-nums;
}
[class*="st-key-kartu_"] .stButton > button {
  border-radius: 10px !important;
  font-size: .76rem !important;
  font-weight: 700 !important;
  min-height: 2rem !important;
  padding: .25rem .5rem !important;
  margin-top: .45rem !important;
  background: #F7F3FD !important;
  border: 1px solid #E6DEF8 !important;
  color: #6E5DA9 !important;
}
[class*="st-key-kartu_"] .stButton > button:hover {
  background: #7C6BB8 !important;
  border-color: #7C6BB8 !important;
  color: #FFFFFF !important;
}
[class*="st-key-kartu_"] .stButton > button:disabled {
  background: #F5F4F7 !important;
  border-color: #EDE9F2 !important;
  color: #B4B0BD !important;
}

/* sembunyikan toolbar Deploy Streamlit */
[data-testid="stToolbar"], [data-testid="stDecoration"],
[data-testid="stStatusWidget"] { display: none !important; }


/* ringkasan di panel keranjang kosong */
.keranjang-ringkas {
  border-radius: 13px;
  padding: .65rem .8rem;
  background: linear-gradient(140deg, #F7F9FB 0%, #F2F6F9 100%);
  border: 1px solid #E7EEF4;
  margin-top: .3rem;
}
.kr-baris {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  font-size: .78rem;
  color: #4A4657;
  padding: .18rem 0;
}
.kr-baris b {
  font-size: .86rem;
  color: #2F2C3A;
  font-variant-numeric: tabular-nums;
}

/* ---------- pemisah ---------- */
hr { border-color: var(--line); }
</style>
"""


def css() -> str:
    """CSS siap pakai, sudah diisi nilai palet.

    Memakai replace (bukan %-format) supaya blok CSS yang mengandung tanda %
    seperti `100%` tidak perlu di-escape jadi `100%%`.
    """
    hasil = _CSS
    for kunci, nilai in PALETTE.items():
        hasil = hasil.replace(f"%({kunci})s", str(nilai))
    return hasil


def apply() -> None:
    """Pasang tema pastel: CSS halaman + warna default chart."""
    st.markdown(css(), unsafe_allow_html=True)

    try:
        import plotly.express as px

        px.defaults.color_discrete_sequence = CHART_COLORS
        px.defaults.template = "plotly_white"
    except ImportError:  # chart opsional, tema tetap jalan
        pass
