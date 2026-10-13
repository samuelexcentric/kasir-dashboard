# Kasir Dashboard POS

Streamlit POS application for cashier transactions, stock, finances, and shift summaries.

Repository: https://github.com/samuelexcentric/kasir-dashboard

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
2. Open https://share.streamlit.io and sign in with GitHub.
3. Choose **Create app** and pick `samuelexcentric/kasir-dashboard`, branch `main`, main file `app.py`.
4. Choose Python 3.12 in Advanced settings.
5. Deploy.

This demo uses CSV files as its record source. Streamlit Community Cloud filesystems can be ephemeral, so CSV/SQLite edits may not survive restarts or redeploys. Use a hosted database for production data. Do not commit real customer records, credentials, or `.streamlit/secrets.toml`.

Google Sheets is not configured in this version. WhatsApp notifications use the Meta WhatsApp Cloud API (out-of-stock alerts and PDF reports); the client only needs the Python standard library, so no extra package is required. PDF export is generated in memory and does not require `wkhtmltopdf`.

## WhatsApp setup (Meta WhatsApp Cloud API)

1. Create a Meta app with the WhatsApp product and note the **Phone number ID** and a **permanent access token**.
2. Add the recipient number as a verified test/production recipient.
3. Create `.streamlit/secrets.toml` (see `.streamlit/secrets.toml.example`):

```toml
WHATSAPP_TOKEN = "your-access-token"
WHATSAPP_PHONE_NUMBER_ID = "your-phone-number-id"
WHATSAPP_RECIPIENT = "628xxxxxxxxxx"
```

On Streamlit Community Cloud, paste the same three keys into the app's **Secrets** settings. For local runs you can also export them as environment variables instead of using secrets.

Out-of-stock alerts fire automatically after a transaction that drives a product to zero stock (once per product per session). The **Stok** page has a manual restock alert button, and the admin **Export PDF** page can send `laporan.pdf` straight to WhatsApp.

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
