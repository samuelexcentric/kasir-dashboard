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

You need three values from Meta. Steps change occasionally, but the current flow is:

### Step 1 - Create the app

1. Open https://developers.facebook.com/apps and sign in with a Facebook account.
2. **Create app** -> use case **Other** -> app type **Business**.
3. In the app dashboard, find the **WhatsApp** product and click **Set up**.
4. Meta provisions a free **test sender number** you can use immediately.

### Step 2 - Copy the Phone number ID

In **WhatsApp -> API Setup**, look at the **From** dropdown. Below it is a numeric **Phone number ID** (about 15-17 digits). Copy that value.

> Common mistake: this is **not** your phone number. It is an internal Meta ID.

### Step 3 - Add the recipient number

Still on **API Setup**, under **To** add the WhatsApp number that should receive alerts. While the app is in test mode only numbers you add here can receive messages.

### Step 4 - Get an access token

- **Quick test:** click **Generate access token** on the API Setup page. It starts with `EAA` but **expires after 24 hours** - fine for a first test, not for production.
- **Production (recommended):** create a permanent System User token:
  1. Open https://business.facebook.com/settings -> **Users -> System users**.
  2. **Add** a system user, role **Admin**.
  3. Select it -> **Assign assets**: your app (Full control) and your WhatsApp account (Full control).
  4. **Generate new token**, set expiry **Never**, and grant `whatsapp_business_messaging` and `whatsapp_business_management`.
  5. Copy the token.

### Step 5 - Verify locally before deploying

Put the three values in `.streamlit/secrets.toml` (copy from `.streamlit/secrets.toml.example`), then run:

```bash
python check_whatsapp.py              # shows which values are set (masked)
python check_whatsapp.py --send-test  # sends a real test text message
python check_whatsapp.py --send-pdf   # sends a sample report PDF
```

```toml
whatsapp_token = "your-access-token"
whatsapp_phone_number_id = "your-phone-number-id"
whatsapp_recipient = "628xxxxxxxxxx"
```

Note: `st.secrets` is case-sensitive and the code reads these lowercase names. Environment variables use the uppercase form (`WHATSAPP_TOKEN`, ...); only the secrets file uses lowercase.

### Step 6 - Add the secrets to Streamlit Cloud

Open your app on share.streamlit.io -> **Settings -> Secrets** and paste the same three lines. Save; the app restarts and WhatsApp turns on. Secrets live only on Streamlit's servers and are never committed to Git.

Low-stock alerts fire automatically on every dashboard load once a product's stock drops to 20 or below (configurable via `STOK_MENIPIS_THRESHOLD`), whichever way it changed - a sale on the Kasir page or a direct edit of `data/produk.csv`. Each product is alerted once until its stock recovers above the threshold. The **Stok** page has a manual restock alert button and an admin stock-edit form, and the admin **Export PDF** page can send `laporan.pdf` straight to WhatsApp. If the secrets are missing the app still runs; the WhatsApp buttons just explain that setup is incomplete.

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
