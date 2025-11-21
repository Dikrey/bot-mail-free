# 🤖 Advanced Temp Mail Bot V6 (SaaS Edition)

![Python](https://img.shields.io/badge/Python-3.9%2B-blue?style=for-the-badge&logo=python)
![Telebot](https://img.shields.io/badge/Library-PyTelegramBotAPI-orange?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Active-green?style=for-the-badge)

**Telegram Bot Free Canggih untuk Layanan Email Sementara (Disposable Email) dengan Sistem Antrian & Notifikasi Real-time.**

Bot ini dirancang seperti layanan SaaS (Software as a Service) mini. Untuk membuat akun email asli (bukan sekadar forwarding), lengkap dengan sistem kuota, kode redeem, dan antrian pengguna.

---

## 🔥 Fitur Utama V6 Free 

### 1. ⏳ Smart Queue System (Sistem Antrian)
Fitur unggulan V6! Mencegah spam dan memastikan stabilitas.
- Hanya **1 User** yang bisa membuat email dalam satu waktu.
- User lain akan masuk ke **Waiting List** (Daftar Tunggu).
- Notifikasi otomatis saat giliran user tiba.
- Durasi sesi dibatasi **5 Menit** (Auto-Kick jika waktu habis).

### 2. 🔔 Auto-Forwarding Notification
Tidak perlu refresh manual!
- Bot berjalan di background (Threading) untuk memantau inbox.
- Pesan masuk langsung dikirim ke chat Telegram user secara **Real-time**.

### 3. 🛡️ Private Accounts (Mail.tm API)
- Bot melakukan Register & Login ke server Mail.tm.
- Akun bersifat **Privat** (User lain tidak bisa mengintip inbox Anda).
- Password di-generate secara acak dan aman.

### 4. 📊 Limit & Quota System
- **Kuota Harian:** User dibatasi (Default: 3 email/hari).
- **Cooldown:** Jeda waktu antar pembuatan email.
- **Reset Otomatis:** Kuota kembali penuh setiap jam 00:00.

### 5. 💎 Redeem Code System
- Admin bisa membuat Kode Promo di file `codes.json`.
- User yang kehabisan kuota bisa memasukkan kode untuk menambah limit.

### 6. 👤 Database User (JSON)
- Menyimpan data ID User, sisa kuota, dan riwayat penggunaan.

---

## 🛠️ Instalasi (Lokal)

Pastikan Anda sudah menginstal Python.

1. **Clone Repository**
   ```bash
   git clone [https://github.com/Dikrey/bot-mail.git](https://github.com/Dikrey/bot-mail.git)
   cd repo-anda


2.  **Install Library**

    ```bash
    pip install -r requirements.txt
    ```

3.  **Konfigurasi Environment**
    Buat file `.env` dan isi Token Bot Anda:

    ```env
    BOT_TOKEN=123456:ABC-DEFxxxxxxxxx
    ```

4.  **Jalankan Bot**

    ```bash
    python main_bot.py
    ```

-----

## ☁️ Cara Deploy ke Render (Gratis 24 Jam)

Bot ini sudah dilengkapi fitur **Keep-Alive** untuk hosting gratisan.

1.  **Upload ke GitHub:** Upload semua file (kecuali `.env`) ke repository GitHub Anda (Set ke Private disarankan).
2.  **Buka [Render.com](https://render.com):** Buat akun & pilih "New Web Service".
3.  **Connect GitHub:** Pilih repository bot Anda.
4.  **Setting:**
      - **Runtime:** Python 3
      - **Build Command:** `pip install -r requirements.txt`
      - **Start Command:** `python main_bot.py`
5.  **Environment Variables:**
      - Masukkan Key: `BOT_TOKEN`
      - Value: `Token_Bot_Anda`
6.  **Agar Tidak Tidur:**
      - Gunakan [UptimeRobot](https://uptimerobot.com) untuk memping URL Render Anda setiap 5 menit.

-----

## 📂 Struktur File

  - `main_bot.py`: Kode utama bot (Logika Antrian, API, Database).
  - `keep_alive.py`: Web server kecil untuk mencegah bot mati di server gratis.
  - `users_db.json`: Database pengguna (dibuat otomatis).
  - `codes.json`: Database kode redeem (dibuat otomatis).

-----

## 👑 Credits & Developer

Project ini dikembangkan dengan ❤️ oleh:

  * **Developer:** [Raihan\_official0307](https://www.tiktok.com/@raihan_official0307)
  * **Team:** Visualcodepo
  * **TikTok:** [@raihan\_official0307](https://www.tiktok.com/@raihan_official0307)
  * **Website Admin:** [Linktree Visualcodepo](https://linktr.ee/Visualcodepo)

-----

## ⚠️ Disclaimer

Bot ini dibuat untuk tujuan edukasi dan testing. Pengembang tidak bertanggung jawab atas penyalahgunaan layanan email sementara yang dihasilkan oleh bot ini.

-----

*Jangan lupa kasih ⭐ Star di repo ini jika bermanfaat\!*
*Jangan lupa Beli Versi Premium t.me/raihan_official0307\!*
