# Kasir Dashboard POS

Streamlit POS application for cashier transactions, stock, finances, and shift summaries.

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

The app includes demo records under `data/`. Demo usernames: `admin`, `ani`, `budi`. Demo password rule: `<username>123`, e.g. `admin123`. Change these demo credentials before using real business data.

## Deploy on Streamlit Community Cloud

1. Push this project folder to a GitHub repository. Keep `app.py`, `requirements.txt`, `core.py`, `services.py`, `db_init.py`, `utils.py`, `.streamlit/config.toml`, and `data/` in the repository.
2. In Streamlit Community Cloud, create an app from the repository and select `app.py` as the entrypoint.
3. Choose Python 3.12 in Advanced settings.
4. Deploy.

This demo uses CSV files as its record source. Streamlit Community Cloud filesystems can be ephemeral, so CSV/SQLite edits may not survive restarts or redeploys. Use a hosted database for production data. Do not commit real customer records, credentials, or `.streamlit/secrets.toml`.

Google Sheets and WhatsApp delivery are not configured in this version. PDF export is generated in memory and does not require `wkhtmltopdf`.

## Repository conventions

- No emoji in project files.
- No `#` comments in code, except shell shebangs.

## Google Stitch design prompt

```text
Buat desain antarmuka (UI/UX) website Dashboard Kasir & Point of Sale (POS) modern, responsif, dan clean berbasis web (Streamlit / Modern Web App) dengan tema Dark Mode & Light Mode yang elegan.

Aplikasi ini ditujukan untuk 2 level pengguna:
1. Admin (Full Access: transaksi, stok, finansial, manajemen kasir & shift, ekspor laporan, pengaturan integrasi).
2. Pengguna/Kasir Biasa (View-only & Kasir Operasional: input transaksi kasir, cek sisa stok, melihat timer shift kerja aktif).

Fitur wajib: Login, POS transaksi, shift kasir, manajemen stok dan alert WhatsApp, riwayat transaksi berfilter, keuangan dan grafik, ekspor PDF, serta status integrasi CSV/Google Sheets.

Layout: sidebar kiri, konten utama kanan, header profil dan status shift. Visual modern dengan aksen emerald/blue dan grafik yang kontras.
```
