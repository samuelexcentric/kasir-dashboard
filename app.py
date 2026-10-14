"""Streamlit POS dashboard – kasir + admin."""
import datetime
import time

import pandas as pd
import plotly.express as px
import streamlit as st

import core
import services
import stok_notifier
import whatsapp_alert

st.set_page_config(page_title="Dashboard Kasir", layout="wide")

if "user" not in st.session_state:
    st.session_state.user = None
    st.session_state.shift_start = None
    st.session_state.shift_notified = False


def login_page():
    st.title("Login Kasir")
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Masuk")
        if submitted:
            user = services.login(username, password)
            if user:
                st.session_state.user = user
                st.session_state.shift_start = datetime.datetime.now()
                st.session_state.shift_notified = False
                st.rerun()
            else:
                st.error("Username / password salah")


def logout():
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()


def shift_sidebar():
    st.sidebar.markdown(f"**{st.session_state.user['nama']}**")
    st.sidebar.caption(f"Role: {st.session_state.user['role']}")
    sisa = core.sisa_waktu_shift(
        st.session_state.shift_start, datetime.datetime.now()
    )
    st.sidebar.progress(1 - sisa / datetime.timedelta(hours=8))
    if sisa > datetime.timedelta(0):
        st.sidebar.caption(f"Sisa shift: {sisa}")
    else:
        if not st.session_state.shift_notified:
            st.session_state.shift_notified = True
            st.toast(core.notifikasi_pulang(st.session_state.shift_start))
        st.sidebar.error(core.notifikasi_pulang(st.session_state.shift_start))
    if st.sidebar.button("Logout"):
        logout()


def page_pos(data):
    st.subheader("Kasir – Transaksi Baru")
    if "keranjang" not in st.session_state:
        st.session_state.keranjang = []
    produk = data["produk"]
    with st.form("trx_form"):
        col1, col2, col3 = st.columns([3, 1, 1])
        nama = col1.selectbox(
            "Produk",
            produk["nama_produk"],
            index=None,
            placeholder="Pilih produk…",
        )
        qty = col2.number_input("Jumlah", min_value=1, step=1)
        metode = col3.selectbox("Bayar", ["Tunai", "QRIS", "Debit"])
        add = st.form_submit_button("Tambah ke keranjang")
        if add and nama:
            row = produk[produk["nama_produk"] == nama].iloc[0]
            if qty > row["stok"]:
                st.error(f"Stok {nama} tinggal {row['stok']}")
            else:
                st.session_state.keranjang.append(
                    {"id_produk": row["id_produk"], "nama": nama,
                     "jumlah": int(qty), "harga": int(row["harga_jual"]),
                     "metode": metode}
                )
                st.rerun()

    if st.session_state.keranjang:
        cart = pd.DataFrame(st.session_state.keranjang)
        st.dataframe(cart, use_container_width=True, hide_index=True)
        total = int((cart["jumlah"] * cart["harga"]).sum())
        st.metric("Total", f"Rp {total:,}")
        c1, c2 = st.columns(2)
        if c1.button("Bayar & Simpan", type="primary"):
            metode = cart["metode"].iloc[0]
            items = [
                {"id_produk": r["id_produk"], "jumlah": r["jumlah"]}
                for r in st.session_state.keranjang
            ]
            try:
                result = services.buat_transaksi(
                    st.session_state.user["id_kasir"], items, metode,
                    datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                )
                st.session_state.keranjang = []
                st.success(
                    f"Transaksi {result['id_transaksi']} tersimpan. "
                    f"Total Rp {result['total_bayar']:,}"
                )
                time.sleep(1)
                st.rerun()
            except ValueError as e:
                st.error(str(e))
        if c2.button("Kosongkan"):
            st.session_state.keranjang = []
            st.rerun()


def _form_edit_stok(data):
    """Admin-only: adjust stock levels without touching the CSV by hand."""
    limit = stok_notifier.ambang()
    with st.expander("Edit stok (admin)"):
        st.caption(
            f"Ubah stok di sini. Notifikasi WhatsApp otomatis terkirim saat "
            f"stok turun ke ≤ {limit}."
        )
        produk = data["produk"]
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
            if st.form_submit_button("Simpan stok"):
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


def page_stok(data, role):
    st.subheader("Stok Barang")

    if role == "admin":
        _form_edit_stok(data)

    produk = data["produk"].copy()
    produk["status"] = [
        core.stok_status(int(s), int(m))
        for s, m in zip(produk["stok"], produk["min_stok"])
    ]
    limit = stok_notifier.ambang()
    low = core.produk_stok_menipis(data["produk"].to_dict(orient="records"), limit)
    st.caption(
        f"Notifikasi WhatsApp otomatis dikirim saat stok ≤ {limit} "
        f"(ubah lewat STOK_MENIPIS_THRESHOLD)."
    )
    if low:
        st.warning(f"{len(low)} produk stoknya ≤ {limit} (perlu restock)")
        status = whatsapp_alert.config_status()
        if not status["configured"]:
            st.caption(
                "WhatsApp belum dikonfigurasi. Isi `whatsapp_token`, "
                "`whatsapp_phone_number_id`, dan `whatsapp_recipient` di secrets."
            )
        if st.button("Kirim peringatan WhatsApp"):
            try:
                whatsapp_alert.notify_restock(low)
                st.success(f"Peringatan restock terkirim ke {status['recipient']}")
            except whatsapp_alert.WhatsAppError as e:
                st.error(f"Gagal kirim: {e}")
        st.text_area(
            "Pratinjau pesan", core.pesan_whatsapp_restock(low),
            height=180, disabled=True,
        )
    else:
        st.success(f"Semua stok aman (di atas {limit})")
    st.dataframe(
        produk[["id_produk", "nama_produk", "kategori", "stok",
                "min_stok", "status"]],
        use_container_width=True, hide_index=True,
    )
    fig = px.bar(produk.nlargest(15, "stok"), x="nama_produk", y="stok",
                 color="status", title="15 produk stok terbanyak")
    st.plotly_chart(fig, use_container_width=True)


def page_riwayat(data):
    st.subheader("Riwayat Transaksi")
    trx = data["transaksi"].copy()
    trx["tanggal"] = pd.to_datetime(trx["tanggal_waktu"]).dt.date
    min_d, max_d = trx["tanggal"].min(), trx["tanggal"].max()
    d1, d2 = st.columns(2)
    start = d1.date_input("Dari", min_d, min_value=min_d, max_value=max_d)
    end = d2.date_input("Sampai", max_d, min_value=min_d, max_value=max_d)
    mask = (trx["tanggal"] >= start) & (trx["tanggal"] <= end)
    filtered = trx[mask]
    c1, c2, c3 = st.columns(3)
    c1.metric("Transaksi", len(filtered))
    c2.metric("Omzet", f"Rp {int(filtered['total_bayar'].sum()):,}")
    harian = filtered.groupby("tanggal")["total_bayar"].sum().reset_index()
    st.plotly_chart(
        px.line(harian, x="tanggal", y="total_bayar",
                title="Omzet harian"),
        use_container_width=True,
    )
    st.dataframe(filtered, use_container_width=True, hide_index=True)


def page_finansial(data, role):
    st.subheader("Finansial")
    ring = services.ringkasan_finansial(data)
    c1, c2, c3 = st.columns(3)
    c1.metric("Omzet", f"Rp {ring['omzet']:,}")
    c2.metric("HPP", f"Rp {ring['hpp']:,}")
    c3.metric("Laba kotor", f"Rp {ring['laba_kotor']:,}")
    c4, c5, c6 = st.columns(3)
    c4.metric("Biaya operasional", f"Rp {ring['biaya_operasional']:,}")
    c5.metric("Modal awal", f"Rp {ring['modal_awal']:,}")
    c6.metric("Laba bersih", f"Rp {ring['laba_bersih']:,}",
              delta_color="normal")

    if role == "admin":
        with st.expander("Tambah biaya / modal"):
            with st.form("biaya_form"):
                b1, b2 = st.columns(2)
                kategori = b1.selectbox(
                    "Kategori", ["Modal Awal", "Listrik", "Gaji", "Sewa",
                                 "Lainnya"])
                jumlah = b2.number_input("Jumlah (Rp)", min_value=0, step=1000)
                ket = st.text_input("Keterangan")
                if st.form_submit_button("Simpan"):
                    services.tambah_biaya(
                        datetime.date.today().isoformat(), kategori, ket,
                        int(jumlah))
                    st.success("Tersimpan")
                    st.rerun()

        st.subheader("Biaya")
        st.dataframe(data["biaya"], use_container_width=True, hide_index=True)


def page_pdf(data, role):
    st.subheader("Export PDF & WhatsApp")
    ring = services.ringkasan_finansial(data)
    status = whatsapp_alert.config_status()
    pdf_bytes = None
    if st.button("Buat PDF", type="primary"):
        try:
            from utils import create_financial_pdf
            pdf_bytes = create_financial_pdf(ring)
            st.session_state["pdf_bytes"] = pdf_bytes
            st.success("PDF siap diunduh")
        except Exception as e:
            st.error(f"PDF gagal: {e}")
    if st.session_state.get("pdf_bytes"):
        st.download_button(
            "Unduh laporan.pdf",
            data=st.session_state["pdf_bytes"],
            file_name="laporan.pdf",
            mime="application/pdf",
        )

    if not status["configured"]:
        st.caption(
            "Kirim WhatsApp butuh `whatsapp_token`, `whatsapp_phone_number_id`, "
            "dan `whatsapp_recipient` di secrets."
        )
    if st.button("Kirim ke WhatsApp"):
        try:
            whatsapp_alert.send_financial_pdf(ring)
            st.success(f"laporan.pdf terkirim ke {status['recipient']}")
        except whatsapp_alert.WhatsAppError as e:
            st.error(f"Gagal kirim: {e}")


def page_shift(data):
    st.subheader("Shift Kasir")
    st.write("Shift aktif: 00–08 Malam · 08–16 Pagi · 16–24 Siang")
    now = datetime.datetime.now()
    nama_shift = core.shift_aktif(now)
    sisa = core.sisa_waktu_shift(st.session_state.shift_start, now)
    st.metric(f"Shift {nama_shift} Anda", str(sisa) + " tersisa")
    if sisa == datetime.timedelta(0):
        st.error(core.notifikasi_pulang(st.session_state.shift_start))
    trx = data["transaksi"].copy()
    trx["tanggal"] = pd.to_datetime(trx["tanggal_waktu"]).dt.date
    omzet = core.omzet_per_shift(
        trx.to_dict(orient="records"), now.date().isoformat())
    st.bar_chart(pd.Series(omzet, name="Omzet hari ini"))


if st.session_state.user is None:
    login_page()
else:
    shift_sidebar()
    role = st.session_state.user["role"]
    st.title("Dashboard Kasir")
    data = services.load_all()

    _baru_menipis = stok_notifier.check_and_notify(
        data["produk"].to_dict(orient="records")
    )
    if _baru_menipis:
        st.toast(
            f"Notifikasi WhatsApp terkirim: {len(_baru_menipis)} produk stok menipis"
        )

    menu = ["Kasir", "Stok", "Riwayat", "Finansial", "Shift"]
    if role == "admin":
        menu.append("Export PDF")
    choice = st.sidebar.radio("Menu", menu)

    if choice == "Kasir":
        page_pos(data)
    elif choice == "Stok":
        page_stok(data, role)
    elif choice == "Riwayat":
        page_riwayat(data)
    elif choice == "Finansial":
        page_finansial(data, role)
        if role != "admin":
            st.caption("Mode lihat saja – edit biaya khusus admin")
    elif choice == "Shift":
        page_shift(data)
    elif choice == "Export PDF" and role == "admin":
        page_pdf(data, role)