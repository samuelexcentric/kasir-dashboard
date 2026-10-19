"""Streamlit POS dashboard – kasir + admin."""
import datetime

import streamlit as st

import components as ui
import core
import page_export
import page_finansial
import page_kasir
import page_riwayat
import page_shift
import page_stok
import services
import stok_notifier
import theme

st.set_page_config(page_title="Dashboard Kasir", layout="wide", page_icon="🧾")
theme.apply()

if "user" not in st.session_state:
    st.session_state.user = None
    st.session_state.shift_start = None
    st.session_state.shift_notified = False


def login_page():
    kiri, tengah, kanan = st.columns([1, 1.1, 1])
    with tengah:
        ui.html("""
            <div class="login-kartu">
              <div class="login-ikon">🧾</div>
              <div class="login-judul">Dashboard Kasir</div>
              <div class="login-sub">Masuk untuk mulai berjualan.</div>
            </div>
            """)
        with st.form("login_form"):
            username = st.text_input("Username", placeholder="admin")
            password = st.text_input("Password", type="password",
                                     placeholder="••••••••")
            if st.form_submit_button("Masuk", type="primary",
                                     use_container_width=True):
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


def sidebar_nav(role: str) -> str:
    menu = ["Kasir", "Stok", "Riwayat", "Finansial", "Shift"]
    if role == "admin":
        menu.append("Export PDF")

    with st.sidebar:
        ui.html("""
            <div class="side-brand">
              <span class="side-logo">🧾</span>
              <div>
                <div class="side-nama">Dashboard Kasir</div>
                <div class="side-sub">Toko Kelontong</div>
              </div>
            </div>
            """)
        pilihan = st.radio("Menu", menu, label_visibility="collapsed")

        sisa = core.sisa_waktu_shift(
            st.session_state.shift_start, datetime.datetime.now()
        )
        habis = sisa <= datetime.timedelta(0)
        ui.html(f"""
            <div class="side-shift">
              <div class="side-shift-label">Shift aktif</div>
              <div class="side-shift-nama">
                {core.shift_aktif(datetime.datetime.now())}
              </div>
              <div class="side-shift-sisa">
                {'Waktu habis' if habis else 'Sisa ' + str(sisa).split('.')[0]}
              </div>
            </div>
            """)
        if habis and not st.session_state.shift_notified:
            st.session_state.shift_notified = True
            st.toast(core.notifikasi_pulang(st.session_state.shift_start))

        ui.html(f"""
            <div class="side-user">
              <span class="side-avatar">
                {st.session_state.user['nama'][:1].upper()}
              </span>
              <div>
                <div class="side-user-nama">{st.session_state.user['nama']}</div>
                <div class="side-user-role">{role}</div>
              </div>
            </div>
            """)
        if st.button("Keluar", use_container_width=True):
            logout()
    return pilihan


if st.session_state.user is None:
    login_page()
else:
    role = st.session_state.user["role"]
    pilihan = sidebar_nav(role)
    data = services.load_all()

    baru_menipis = stok_notifier.check_and_notify(
        data["produk"].to_dict(orient="records")
    )
    if baru_menipis:
        st.toast(
            f"Notifikasi WhatsApp terkirim: {len(baru_menipis)} produk "
            "stok menipis"
        )

    if pilihan == "Kasir":
        page_kasir.render(data)
    elif pilihan == "Stok":
        page_stok.render(data, role)
    elif pilihan == "Riwayat":
        page_riwayat.render(data)
    elif pilihan == "Finansial":
        page_finansial.render(data, role)
    elif pilihan == "Shift":
        page_shift.render(data)
    elif pilihan == "Export PDF" and role == "admin":
        page_export.render(data, role)
