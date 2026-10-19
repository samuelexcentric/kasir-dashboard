"""Halaman Kasir bergaya katalog kartu + panel keranjang (desain Stitch).

Data selalu dibaca dari CSV lewat `services.load_all()`; tidak ada angka contoh.
"""
from __future__ import annotations

import datetime

import pandas as pd
import streamlit as st

import components as ui
import services

KATEGORI_IKON = {
    "Makanan": "🍜",
    "Minuman": "🥤",
    "Pakaian": "👕",
    "Alas Kaki": "👟",
    "Aksesoris": "⌚",
    "Tas": "🎒",
    "Elektronik": "🔌",
}
KATEGORI_TINT = {
    "Makanan": "peach",
    "Minuman": "sky",
    "Pakaian": "lavender",
    "Alas Kaki": "mint",
    "Aksesoris": "butter",
    "Tas": "rose",
    "Elektronik": "sky",
}


def ikon(kategori: str) -> str:
    return KATEGORI_IKON.get(str(kategori), "📦")


def _keranjang() -> list[dict]:
    if "keranjang" not in st.session_state:
        st.session_state.keranjang = []
    return st.session_state.keranjang


def _badge(stok: int, ambang: int) -> tuple[str, str]:
    if stok <= 0:
        return "Habis", "habis"
    if stok <= ambang:
        return f"Stok {stok}", "menipis"
    return f"Stok {stok}", "aman"


def _tambah(produk: pd.DataFrame, id_produk: str) -> None:
    row = produk[produk["id_produk"] == id_produk]
    if row.empty:
        return
    row = row.iloc[0]
    stok = int(row["stok"])
    keranjang = _keranjang()
    sudah = next((i for i in keranjang if i["id_produk"] == id_produk), None)
    total = 1 + (sudah["jumlah"] if sudah else 0)
    if total > stok:
        st.session_state["notif_error"] = (
            f"Stok {row['nama_produk']} tinggal {stok}."
        )
        return
    if sudah:
        sudah["jumlah"] = total
    else:
        keranjang.append(
            {
                "id_produk": id_produk,
                "nama": str(row["nama_produk"]),
                "kategori": str(row["kategori"]),
                "jumlah": 1,
                "harga": int(row["harga_jual"]),
            }
        )


def _ubah_qty(id_produk: str, delta: int, produk: pd.DataFrame) -> None:
    keranjang = _keranjang()
    item = next((i for i in keranjang if i["id_produk"] == id_produk), None)
    if not item:
        return
    baru = item["jumlah"] + delta
    if baru <= 0:
        keranjang.remove(item)
        return
    stok = int(produk.loc[produk["id_produk"] == id_produk, "stok"].iloc[0])
    if baru > stok:
        st.session_state["notif_error"] = f"Stok tinggal {stok}."
        return
    item["jumlah"] = baru


def _hapus_item(id_produk: str) -> None:
    for i in list(_keranjang()):
        if i["id_produk"] == id_produk:
            _keranjang().remove(i)


def _kosongkan() -> None:
    st.session_state.keranjang = []


def _kartu(row: pd.Series, ambang: int) -> None:
    """Kartu produk: satu container bertingkat supaya tombol menempel di kartu."""
    tint = KATEGORI_TINT.get(str(row["kategori"]), "sky")
    teks, kelas = _badge(int(row["stok"]), ambang)
    habis = int(row["stok"]) <= 0
    with st.container(key=f"kartu_{row['id_produk']}"):
        ui.html(f"""
            <div class="produk-atas">
              <span class="produk-ikon">{ikon(row['kategori'])}</span>
              <span class="pill pill-{kelas}">{teks}</span>
            </div>
            <div class="produk-nama">{row['nama_produk']}</div>
            <div class="produk-kategori">{row['kategori']}</div>
            <div class="produk-harga">{ui.rupiah(row['harga_jual'])}</div>
            """)
        st.button(
            "Tambah",
            key=f"tambah_{row['id_produk']}",
            disabled=habis,
            use_container_width=True,
            on_click=_tambah,
            args=(st.session_state["_produk_df"], row["id_produk"]),
        )


def _ringkas_hari_ini() -> None:
    """Isi panel kanan saat keranjang kosong: ringkasan hari ini dari CSV."""
    try:
        data = services.load_all()
    except Exception:
        return
    trx = data["transaksi"].copy()
    trx["tanggal"] = pd.to_datetime(trx["tanggal_waktu"]).dt.date
    hari_ini = trx[trx["tanggal"] == pd.Timestamp.today().date()]
    if hari_ini.empty:
        hari_ini = trx.sort_values("tanggal_waktu").tail(5)

    omzet = int(hari_ini["total_bayar"].sum())
    jumlah = len(hari_ini)
    ui.html(f"""
        <div class="keranjang-ringkas">
          <div class="kr-baris">
            <span>Transaksi</span><b>{ui.angka(jumlah)}</b>
          </div>
          <div class="kr-baris">
            <span>Omzet</span><b>{ui.rupiah(omzet)}</b>
          </div>
        </div>
        """)
    ui.judul_bagian("Produk terlaris", "dari CSV")
    detail = data["detail_transaksi"].merge(
        data["produk"][["id_produk", "nama_produk"]], on="id_produk", how="left"
    )
    laris = (
        detail.groupby("nama_produk")["jumlah"].sum()
        .sort_values(ascending=False).head(5)
    )
    ui.progress_list([
        (str(k)[:22], int(v), "ungu" if i % 2 == 0 else "mint")
        for i, (k, v) in enumerate(laris.items())
    ])


def _panel_keranjang(produk: pd.DataFrame) -> None:
    keranjang = _keranjang()
    ui.html('<div class="keranjang-judul">Keranjang</div>')

    if not keranjang:
        ui.html(
            '<div class="keranjang-kosong">🧺<br>Belum ada item.<br>'
            "<span>Pilih produk di katalog.</span></div>"
        )
        _ringkas_hari_ini()
        return

    total = sum(i["jumlah"] * i["harga"] for i in keranjang)
    total_qty = sum(i["jumlah"] for i in keranjang)

    daftar = st.container(height=250, border=False)
    for item in list(keranjang):
        with daftar:
            k_teks, k_min, k_plus, k_hapus = st.columns([2.4, .55, .55, 1.05])
            ui.html(
                f"""
                <div class="keranjang-item">
                  <div class="keranjang-nama">{item['nama']}</div>
                  <div class="keranjang-meta">
                    {item['jumlah']} × {ui.rupiah(item['harga'])} =
                    <b>{ui.rupiah(item['jumlah'] * item['harga'])}</b>
                  </div>
                </div>
                """,
                target=k_teks,
            )
            k_min.button(
                "−", key=f"min_{item['id_produk']}", on_click=_ubah_qty,
                args=(item["id_produk"], -1, produk),
            )
            k_plus.button(
                "+", key=f"plus_{item['id_produk']}", on_click=_ubah_qty,
                args=(item["id_produk"], 1, produk),
            )
            k_hapus.button(
                "Hapus", key=f"del_{item['id_produk']}",
                on_click=_hapus_item, args=(item["id_produk"],),
            )

    ui.html(f"""
        <div class="keranjang-total">
          <div>
            <div class="keranjang-total-label">Total · {total_qty} item</div>
            <div class="keranjang-total-nilai">{ui.rupiah(total)}</div>
          </div>
          <span class="pill pill-ungu">Siap bayar</span>
        </div>
        """)

    metode = st.selectbox("Metode bayar", ["Tunai", "QRIS", "Debit"])
    c1, c2 = st.columns(2)
    if c1.button("Bayar & Simpan", type="primary", use_container_width=True):
        items = [
            {"id_produk": i["id_produk"], "jumlah": i["jumlah"]} for i in keranjang
        ]
        try:
            hasil = services.buat_transaksi(
                st.session_state.user["id_kasir"],
                items,
                metode,
                datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            )
        except ValueError as e:
            st.error(str(e))
        else:
            _kosongkan()
            st.session_state["notif_sukses"] = (
                f"Transaksi {hasil['id_transaksi']} tersimpan · "
                f"{ui.rupiah(hasil['total_bayar'])}"
            )
            st.rerun()
    if c2.button("Kosongkan", use_container_width=True):
        _kosongkan()
        st.rerun()


def render(data: dict) -> None:
    produk = data["produk"].copy()
    st.session_state["_produk_df"] = produk
    ambang = 20
    try:
        import stok_notifier

        ambang = stok_notifier.ambang()
    except Exception:
        pass

    ui.page_header(
        "Kasir",
        "Pilih produk, lalu selesaikan pembayaran.",
        aksi=f"{len(produk)} produk",
    )

    if pesan := st.session_state.pop("notif_sukses", None):
        st.success(pesan)
    if pesan := st.session_state.pop("notif_error", None):
        st.error(pesan)

    kiri, kanan = st.columns([1.55, 1], gap="large")

    with kiri:
        cari = st.text_input(
            "Cari produk", placeholder="🔍  Cari produk / barcode…",
            label_visibility="collapsed",
        )
        kategori_semua = ["Semua"] + sorted(produk["kategori"].dropna().unique())
        kategori = st.pills(
            "Kategori", kategori_semua, default="Semua",
            label_visibility="collapsed", wrap=True,
        )

        hasil = produk
        if cari:
            q = cari.strip().lower()
            hasil = hasil[
                hasil["nama_produk"].str.lower().str.contains(q, na=False)
                | hasil["id_produk"].str.lower().str.contains(q, na=False)
            ]
        if kategori and kategori != "Semua":
            hasil = hasil[hasil["kategori"] == kategori]

        ui.judul_bagian("Katalog Produk", f"{len(hasil)} produk")

        if hasil.empty:
            st.info("Tidak ada produk yang cocok.")
        else:
            for mulai in range(0, len(hasil), 3):
                kolom = st.columns(3, gap="small")
                for k, (_, row) in zip(
                    kolom, hasil.iloc[mulai : mulai + 3].iterrows()
                ):
                    with k:
                        _kartu(row, ambang)

    with kanan:
        _panel_keranjang(produk)
