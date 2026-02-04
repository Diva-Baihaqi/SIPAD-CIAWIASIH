# PANDUAN DEPLOYMENT APLIKASI DESA CIAWIASIH

# (Edisi Pengguna Laragon & phpMyAdmin)

Dokumen ini adalah panduan langkah demi langkah untuk menaruh website Anda di internet secara GRATIS selamanya.

---

## 🏗️ PETA CITA-CITA

Kita akan menggunakan dua layanan gratis terbaik:

1. **RENDER.COM** (Rumah Website) -> Menggantikan Folder `www` & Terminal di laptop.
2. **AIVEN.IO** (Gudang Data) -> Menggantikan Database MySQL di laptop.

---

## 🛠️ TAHAP 1: PERSIAPAN DATABASE ONLINE (AIVEN)

Kita siapkan dulu tempat penyimpanan datanya di internet.

1. Buka [https://aiven.io/](https://aiven.io/)
2. Daftar akun (Sign Up) -> Pilih **Free Plan**.
3. **Buat Database Baru**:
   - Klik **Create Service**.
   - Pilih tipe: **MySQL**.
   - Cloud Provider: Pilih **Google Cloud** (Cari lokasi **Jakarta** atau **Singapore** yang ada label "Free Tier").
   - Service Name: `db-desa-ciawiasih` (bebas).
   - Klik **Create Service**.
4. **Simpan Kunci Rahasia**:
   - Tunggu bola status jadi **Hijau (Running)**.
   - Di menu Overview, cari **Connection Details**.
   - Salin data ini ke Notepad:
     - **Host**: (Contoh: `mysql-abc.aivencloud.com`)
     - **Port**: (Contoh: `13579`) <- _JANGAN TERLEWAT_
     - **User**: (Biasanya `avnadmin`)
     - **Password**: (Klik tombol mata/reveal)
     - **Database Name**: (Biasanya `defaultdb`)

---

## 📤 TAHAP 2: MIGRASI DATA (DARI PHPMYADMIN KE AIVEN)

Ini langkah memindahkan data warga dari laptop ke internet.

**Langkah A: Ambil Data dari phpMyAdmin (Export)**

1. Buka browser -> `localhost/phpmyadmin`.
2. Klik database `sid_desa`.
3. Klik menu **Export** di bagian atas.
4. Klik tombol **Go**.
5. Anda akan mendownload file bernama `sid_desa.sql`. Simpan file ini.

**Langkah B: Upload ke Aiven (Import)**
_Karena phpMyAdmin hanya untuk lokal, kita perlu alat bantu untuk akses server luar. Laragon sudah menyediakannya._

1. Buka aplikasi **Laragon**.
2. Klik tombol **Database** (Ini akan membuka aplikasi HeidiSQL).
3. Di pojok kiri bawah, klik **New** (Buat sesi baru).
4. Masukkan data dari **Aiven** (Tahap 1):
   - **Hostname / IP**: (Isi Host dari Aiven)
   - **User**: (Isi User dari Aiven)
   - **Password**: (Isi Password dari Aiven)
   - **Port**: (Isi Port dari Aiven)
5. Klik **Open**.
6. Jika berhasil masuk, Anda akan melihat database `defaultdb` di kiri.
7. Klik menu **File** -> **Load SQL file...**
8. Pilih file `sid_desa.sql` yang tadi didownload dari phpMyAdmin.
9. Tekan **F9** atau tombol **Run/Play** (Segitiga Biru) untuk menjalankan.
10. Selesai! Data Anda sekarang sudah ada di internet.

---

## 🐙 TAHAP 3: UPLOAD KODE KE GITHUB

1. Buka [GitHub.com](https://github.com/) -> Buat **New Repository** (Misal: `desa-online`).
2. Buka Terminal VS Code (Ctrl + `).
3. Jalankan perintah ini satu per satu:

   ```bash
   git init
   git add .
   git commit -m "Upload pertama"
   git branch -M main
   # Ganti URL di bawah dengan URL GitHub Anda sendiri!
   git remote add origin https://github.com/USERNAME_ANDA/desa-online.git
   git push -u origin main
   ```

---

## 🚀 TAHAP 4: PELUNCURAN (RENDER)

1. Buka [dashboard.render.com](https://dashboard.render.com/).
2. Klik **New +** -> **Web Service**.
3. Pilih **Build and deploy from a Git repository**.
4. Sambungkan GitHub Anda, pilih repo `desa-online`.
5. Isi Settingan:

   - **Name**: `desa-ciawiasih` (Nama website)
   - **Region**: Singapore
   - **Branch**: `main`
   - **Runtime**: **Python 3**
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn wsgi:application`
   - **Instance Type**: **Free**

6. **Environment Variables (Wajib!)**
   Klik **Advanced** -> **Add Environment Variable**. Masukkan kunci-kunci ini (sesuai data Aiven):

   | Key (Nama Kiri)  | Value (Isi Kanan)                          |
   | :--------------- | :----------------------------------------- |
   | `MYSQL_HOST`     | (Host Aiven)                               |
   | `MYSQL_USER`     | (User Aiven)                               |
   | `MYSQL_PASSWORD` | (Password Aiven)                           |
   | `MYSQL_DB`       | `defaultdb`                                |
   | `MYSQL_PORT`     | (Port Aiven, contoh: 12345)                |
   | `SECRET_KEY`     | (Isi kode acak panjang dari terminal tadi) |
   | `GEMINI_API_KEY` | (Isi API Key AI Lana Anda)                 |

7. Klik **Create Web Service**.

Tunggu 2-3 menit. Jika sukses, status jadi **Live**.
Selamat! Website desa Anda sudah online.
