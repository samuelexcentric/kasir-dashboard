"""Halaman Stok mengikuti desain Stitch: banner peringatan + grid kartu + progress.

Semua angka dari data/produk.csv (via data["produk"]).
"""
from __future__ import annotations

import pandas as pd
import streamlit as st

import components as ui
import core
import services
import stok_notifier
import whatsapp_alert

IKON = {
    "Makanan": "🍜", "Minuman": "🥤", "Pakaian": "👕", "Alas Kaki": "👟",
    "Aksesoris": "⌚", "Tas": "🎒", "Elektronik": "🔌",
}
TINT = {
    "Makanan": "peach", "Minuman": "sky", "Pakaian": "lavender",
    "Alas Kaki": "mint", "Aksesoris": "butter", "Tas": "rose",
    "Elektronik": "sky",
}


def _form_edit_stok(produk: pd.DataFrame, limit: int) -> None:
    with st.expander("Edit stok (admin)"):
        st.caption(
            f"Ubah stok di sini. Notifikasi WhatsApp otomatis terkirim saat "
            f"stok turun ke ≤ {limit}."
        )
        pilihan = st.multiselect(
            "Produk yang diubah",
            options=produk["id_produk"].tolist(),
            format_func=lambda pid: (
                f"{produk.loc[produk['id_produk'] == pid, 'nama_produk'].iloc[0]}"
                f" ({pid}) – stok "
                f"{int(produk.loc[produk['id_produk'] == pid, 'stok'].iloc[0])}"
            ),
        )
        if not pilihan:
            st.caption("Pilih satu atau beberapa produk untuk mengubah stoknya.")
            return
        with st.form("edit_stok_form"):
            nilai = {}
            for pid in pilihan:
                row = produk[produk["id_produk"] == pid].iloc[0]
                nilai[pid] = st.number_input(
                    f"Stok baru – {row['nama_produk']} ({pid})",
                    min_value=0, step=1, value=int(row["stok"]),
                )
            if st.form_submit_button("Simpan stok", type="primary"):
                try:
                    hasil = services.update_stok(
                        {pid: int(v) for pid, v in nilai.items()}
                    )
                except ValueError as e:
                    st.error(str(e))
                else:
                    if hasil["diubah"]:
                        st.success(f"{hasil['diubah']} produk diperbarui.")
                    else:
                        st.info("Tidak ada perubahan.")
                    st.rerun()


def _kartu_stok(row: pd.Series, limit: int) -> None:
    tint = TINT.get(str(row["kategori"]), "sky")
    stok = int(row["stok"])
    if stok <= 0:
        teks, kelas = "Habis", "habis"
    elif stok <= limit:
        teks, kelas = f"Stok {stok}", "menipis"
    else:
        teks, kelas = f"Stok {stok}", "aman"

    ui.html(f"""
        <div class="produk-kartu tint-{tint}">
          <div class="produk-atas">
            <span class="pill pill-{kelas}">{teks}</span>
            <span class="pill pill-netral">{row['kategori']}</span>
          </div>
          <div class="stok-ikon">{IKON.get(str(row['kategori']), '📦')}</div>
          <div class="produk-nama">{row['nama_produk']}</div>
          <div class="stok-meta">
            min {int(row['min_stok'])} · {ui.rupiah(row['harga_jual'])}
          </div>
        </div>
        """)


def render(data: dict, role: str) -> None:
    produk = data["produk"].copy()
    limit = stok_notifier.ambang()
    produk["status"] = [
        core.stok_status(int(s), int(m))
        for s, m in zip(produk["stok"], produk["min_stok"])
    ]
    low = core.produk_stok_menipis(
        data["produk"].to_dict(orient="records"), limit
    )

    ui.page_header(
        "Stok Barang",
        "Manajemen inventaris & peringatan restock.",
        aksi=f"{len(produk)} SKU",
    )

    if role == "admin":
        _form_edit_stok(produk, limit)

    if low:
        ui.banner(
            f"<b>{len(low)} produk</b> stoknya ≤ {limit} — segera restock.",
            "warning", "⚠️",
        )
        status = whatsapp_alert.config_status()
        if not status["configured"]:
            st.caption(
                "WhatsApp belum dikonfigurasi. Isi `whatsapp_token`, "
                "`whatsapp_phone_number_id`, dan `whatsapp_recipient` di secrets."
            )
        else:
            if st.button("Kirim peringatan WhatsApp", type="primary"):
                try:
                    whatsapp_alert.notify_restock(low)
                    st.success(f"Peringatan restock terkirim ke {status['recipient']}")
                except whatsapp_alert.WhatsAppError as e:
                    st.error(f"Gagal kirim: {e}")
    else:
        ui.banner(f"Semua stok aman (di atas {limit}).", "ok", "✅")

    kiri, kanan = st.columns([2.05, 1], gap="large")

    with kiri:
        kategori_semua = ["Semua"] + sorted(produk["kategori"].dropna().unique())
        pilih = st.pills(
            "Kategori", kategori_semua, default="Semua",
            label_visibility="collapsed",
        )
        tampil = produk if not pilih or pilih == "Semua" else produk[
            produk["kategori"] == pilih
        ]
        urut = st.session_state.get("urut_stok", "Stok terendah")
        opsi_urut = ["Stok terendah", "Stok tertinggi", "Nama A–Z"]
        urut = st.segmented_control(
            "Urutkan", opsi_urut, default=urut, label_visibility="collapsed"
        ) or "Stok terendah"
        if urut == "Stok terendah":
            tampil = tampil.sort_values("stok")
        elif urut == "Stok tertinggi":
            tampil = tampil.sort_values("stok", ascending=False)
        else:
            tampil = tampil.sort_values("nama_produk")

        ui.judul_bagian("Daftar Produk", f"{len(tampil)} item")
        for mulai in range(0, len(tampil), 3):
            kolom = st.columns(3, gap="small")
            for k, (_, row) in zip(
                kolom, tampil.iloc[mulai : mulai + 3].iterrows()
            ):
                with k:
                    _kartu_stok(row, limit)

    with kanan:
        ui.judul_bagian("Stok terbanyak", "15 teratas")
        teratas = produk.nlargest(15, "stok")
        baris = [
            (str(r["nama_produk"])[:26], int(r["stok"]),
             "ungu" if i % 2 == 0 else "mint")
            for i, (_, r) in enumerate(teratas.iterrows())
        ]
        ui.progress_list(baris)

        ui.judul_bagian("Perlu restock", f"≤ {limit}")
        if low:
            for p in low[:8]:
                ui.html(
                    f'<div class="restock-item">'
                    f'<span>{p["nama_produk"]}</span>'
                    f'<span class="pill pill-menipis">{int(p["stok"])}</span>'
                    f"</div>"
                )
        else:
            st.caption("Tidak ada produk menipis.")

    with st.expander("Tabel lengkap & grafik"):
        st.dataframe(
            produk[["id_produk", "nama_produk", "kategori", "stok",
                    "min_stok", "status"]],
            use_container_width=True, hide_index=True,
        )
        st.bar_chart(produk.nlargest(15, "stok").set_index("nama_produk")["stok"])
