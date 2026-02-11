# PANDUAN DEPLOYMENT SITUS DESA CIAWIASIH (EDISI RAILWAY)

Dokumen ini adalah panduan resmi langkah demi langkah untuk men-deploy aplikasi **Sistem Informasi Pelayanan Administrasi Desa (SIPAD)** ke layanan cloud **Railway.app**.

Kami memilih **Railway** karena mendukung **Python (Flask)** dan **MySQL** dalam satu platform yang terintegrasi, cepat, dan stabil untuk kebutuhan skripsi/proyek akhir.

---

## 🏗️ ARSITEKTUR DEPLOYMENT

1.  **GITHUB**: Sebagai tempat penyimpanan kode sumber (Source Code Management).
2.  **RAILWAY**: Sebagai penyedia layanan Cloud Hosting (PaaS) untuk menjalankan aplikasi web dan database MySQL.

---

## 🛠️ TAHAP 1: PERSIAPAN FILE PROYEK (SUDAH DILAKUKAN OTOMATIS)

Sebelum mengunggah ke internet, pastikan file konfigurasi berikut sudah ada di folder proyek Anda (Sistem Lana sudah menyiapkannya utk Anda):

1.  **`requirements.txt`**: Daftar pustaka Python, harus menyertakan `gunicorn` dan `mysqlclient`/`pymysql`.
2.  **`Procfile`**: Perintah untuk menjalankan web server. Isinya wajib: `web: gunicorn wsgi:application`.
3.  **`runtime.txt`**: Menentukan versi Python (misal: `python-3.10.12`).
4.  **`.gitignore`**: Memastikan folder sampah (`__pycache__`, `venv`) dan file rahasia (`.env`) tidak ikut terupload.

> **Status Saat Ini**: File-file di atas sudah saya siapkan di folder Anda. Anda siap lanjut ke Tahap 2.

---

## 🐙 TAHAP 2: UPLOAD KODE KE GITHUB

Anda perlu akun GitHub. Jika belum punya, daftar di [github.com](https://github.com/).

1.  **Buat Repository Baru**:

    - Login ke GitHub.
    - Klik tombol **(+)** di pojok kanan atas -> **New repository**.
    - Nama Repository: `sipad-desa-online` (atau nama lain yang Anda suka).
    - Set ke **Public** atau **Private** (bebas).
    - Klik **Create repository**.

2.  **Push Kode dari Laptop**:

    - Buka Terminal di VS Code (Ctrl + `).
    - Ketik perintah berikut satu per satu (tekan Enter setiap baris):

    ```bash
    git init
    git add .
    git commit -m "Siap deploy ke Railway"
    git branch -M main
    # GANTI URL DI BAWAH DENGAN URL REPO GITHUB ANDA SENDIRI!
    git remote add origin https://github.com/USERNAME_GITHUB/sipad-desa-online.git
    git push -u origin main
    ```

---

## 🚅 TAHAP 3: SETUP RAILWAY (APLIKASI + DATABASE)

1.  **Buat Proyek Baru**:

    - Buka [railway.app](https://railway.app/) dan login (bisa pakai akun GitHub).
    - Klik tombol **+ New Project** -> Pilih **Provision MySQL**.
    - Tunggu beberapa detik hingga kotak `MySQL` muncul.

2.  **Deploy Aplikasi Web**:

    - Di dashboard project yang sama, klik tombol **+ New** (atau klik kanan di area kosong).
    - Pilih **GitHub Repo**.
    - Cari dan pilih repo `sipad-desa-online` yang baru Anda upload.
    - Klik **Deploy Now**.

3.  **Hubungkan Aplikasi dengan Database**:
    Aplikasi akan error sebentar karena belum tahu password database-nya. Mari kita hubungkan.

    - **Ambil Data MySQL**:

      - Klik kotak **MySQL**.
      - Buka tab **Variables**.
      - Anda akan melihat daftar: `MYSQLHOST`, `MYSQLUSER`, `MYSQLPASSWORD`, `MYSQLPORT`, `MYSQLDATABASE`, `MYSQL_URL`.

    - **Masukkan ke Aplikasi**:

      - Klik kotak **Aplikasi (Repo Anda)**.
      - Buka tab **Settings** -> Scroll ke **Environment Variables**.
      - Tambahkan variabel berikut (Sesuaikan NILAI-nya dengan data dari tab MySQL tadi):

      | Variable Name (KIRI) | Value (KANAN)               | Sumber Data          |
      | :------------------- | :-------------------------- | :------------------- |
      | `MYSQL_HOST`         | (Copy dari `MYSQLHOST`)     | Tab MySQL            |
      | `MYSQL_USER`         | (Copy dari `MYSQLUSER`)     | Tab MySQL            |
      | `MYSQL_PASSWORD`     | (Copy dari `MYSQLPASSWORD`) | Tab MySQL            |
      | `MYSQL_DB`           | (Copy dari `MYSQLDATABASE`) | Tab MySQL            |
      | `MYSQL_PORT`         | (Copy dari `MYSQLPORT`)     | Tab MySQL            |
      | `SECRET_KEY`         | `rahasia_negara_123`        | Buat sendiri (bebas) |
      | `GEMINI_API_KEY`     | (API Key Google Anda)       | Dari file .env lokal |

    - Setelah disimpan, Railway otomatis akan me-restart aplikasi Anda. Tunggu hingga statusnya **Active (Hijau)**.

---

## 💾 TAHAP 4: MIGRASI DATABASE (IMPORT DATA)

Database di Railway masih kosong. Kita perlu mengirim data dari laptop ke sana. Anda bisa menggunakan **HeidiSQL** atau **MySQL Workbench**.

### OPSI A: Menggunakan HeidiSQL

1.  Buka HeidiSQL -> Klik **New**.
2.  Isi data dari Tab Variables Railway seperti biasa.
3.  Klik **Open** -> File -> Load SQL file -> Pilih `database/sid_desa.sql` -> Run.

### OPSI B: Menggunakan MySQL Workbench (Alternatif)

Jika Anda lebih suka MySQL Workbench, ikuti langkah ini:

1.  Buka **MySQL Workbench**.
2.  Klik tombol **(+)** di sebelah tulisan "MySQL Connections".
3.  Isi Form:
    - **Connection Name**: `Desa Online` (Bebas).
    - **Connection Method**: Standard (TCP/IP).
    - **Hostname**: (Copy dari `MYSQLHOST` Railway).
    - **Port**: (Copy dari `MYSQLPORT` Railway).
    - **Username**: (Copy dari `MYSQLUSER` Railway).
    - **Password**: Klik tombol **Store in Vault...** lalu paste password dar Railway.
4.  Klik **Test Connection** untuk memastikan berhasil. Jika sukses, klik **OK**.
5.  Klik kotak koneksi `Desa Online` yang baru dibuat untuk masuk.
6.  Di dalam, klik menu **File** -> **Open SQL Script...**.
7.  Pilih file `database/sid_desa.sql` dari laptop Anda.
8.  Setelah script terbuka, klik ikon **Petir (Execute)** di toolbar atas.
9.  Tunggu proses selesai. Refresh schema di panel kiri (`railway`) untuk melihat tabel.

---

## ✅ TAHAP 5: SELESAI

1.  Kembali ke Railway.
2.  Klik kotak **Aplikasi**.
3.  Di bagian atas, klik link domain yang disediakan (contoh: `sipad-desa-online.up.railway.app`).
4.  Website Desa Ciawiasih Anda sudah online! 🎉
