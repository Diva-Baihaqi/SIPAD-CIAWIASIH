# 🏛️ SIPAD - Sistem Informasi Pelayanan Administrasi Desa

### Digitalisasi Layanan Publik Desa Ciawiasih Menuju Desa Cerdas (Smart Village)

![Banner Utama](<picture/1.%20Publik/1.%20Halaman%20Utama%20(Landing%20Page)%20-%20Atas.png>)

**SIPAD (Sistem Informasi Pelayanan Administrasi Desa)** adalah platform _E-Government_ berbasis web yang dirancang khusus untuk mendigitalisasi birokrasi di Desa Ciawiasih. Sistem ini memangkas waktu pelayanan administrasi dari hitungan hari menjadi menit, sekaligus menghadirkan transparansi dan kemudahan akses bagi seluruh warga desa.

Dilengkapi dengan **LANA (AI Assistant)** yang siap melayani pertanyaan warga 24/7 dan integrasi **WhatsApp Gateway** untuk notifikasi real-time.

---

## 📸 Galeri Tampilan Aplikasi

### 🌍 Halaman Publik & Layanan Mandiri

Desain antarmuka yang modern, responsif, dan ramah pengguna (User Friendly).

|                                                           Halaman Utama                                                            |                                                      Layanan Mandiri                                                      |
| :--------------------------------------------------------------------------------------------------------------------------------: | :-----------------------------------------------------------------------------------------------------------------------: |
| <img src="picture/1.%20Publik/1.%20Halaman%20Utama%20(Landing%20Page)%20-%20Atas.png" width="100%"> <br> _Landing Page Informatif_ | <img src="picture/1.%20Publik/2.%20Halaman%20Utama%20-%20Bagian%20Layanan.png" width="100%"> <br> _Katalog Layanan Surat_ |

|                                                Chatbot AI (LANA)                                                |                                                          Statistik Desa                                                          |
| :-------------------------------------------------------------------------------------------------------------: | :------------------------------------------------------------------------------------------------------------------------------: |
| <img src="picture/1.%20Publik/4.%20Fitur%20Chatbot%20LANA%20AI.png" width="100%"> <br> _Asisten Virtual Cerdas_ | <img src="picture/1.%20Publik/3.%20Halaman%20Utama%20-%20Bagian%20Statistik.png" width="100%"> <br> _Transparansi Data Penduduk_ |

---

### 🔐 Portal Akses Pengguna (Multi-Role)

Sistem keamanan berjenjang untuk memastikan privasi dan integritas data.

|                                      Login Area                                       |                                      Registrasi Warga                                      |
| :-----------------------------------------------------------------------------------: | :----------------------------------------------------------------------------------------: |
| <img src="picture/1.%20Publik/5.%20Login.png" width="100%"> <br> _Gerbang Akses Aman_ | <img src="picture/1.%20Publik/6.%20Signup.png" width="100%"> <br> _Pendaftaran Akun Warga_ |

---

### 💻 Dashboard Khusus (Role Specific)

Setiap peran memiliki pandangan dashboard yang disesuaikan dengan tugas dan fungsinya.

#### 1. Dashboard Administrator (Perangkat Desa)

Pusat kendali operasional desa. Mengelola seluruh data penduduk, surat masuk, dan konfigurasi sistem.
![Admin Dashboard](<picture/3.%20Admin%20(Sekretaris%20Desa)/1.%20Dashboard%20Admin.png>)

#### 2. Dashboard Pimpinan (Kuwu/Kepala Desa)

Fokus pada pengawasan kinerja dan eksekutif summary (Laporan Kinerja).
![Kuwu Dashboard](<picture/4.%20Kuwu%20(kepala%20desa)/1.%20Dashboard%20Eksekutif.png>)
_(Note: Pastikan nama file di folder Kuwu sesuai, saya asumsikan namanya dashboard)_

#### 3. Dashboard Lulugu (Kepala Blok)

Manajemen kewilayahan untuk memverifikasi warga di tingkat blok/dusun masing-masing.
![Lulugu Dashboard](<picture/5.%20Lulugu%20(Kepala%20Dusun)/1.%20Dashboard%20RT%20(Lulugu).png>)
_(Note: Sesuaikan dengan nama file di folder Lulugu)_

#### 4. Dashboard Warga

Panel personal bagi warga untuk mengajukan surat, memantau status permohonan, dan mengelola profil.
![Warga Dashboard](<picture/2.%20Warga%20(penduduk)/1.%20Dashboard%20Warga.png>)
_(Note: Sesuaikan dengan nama file di folder Warga)_

---

## ✨ Fitur Unggulan

- **🚀 Pengajuan Surat Online**: Warga bisa request surat (SKTM, Domisili, Usaha, dll) dari rumah.
- **🤖 LANA AI Assistant**: Chatbot pintar berbasis Google Gemini AI untuk layanan tanya jawab otomatis.
- **📱 WhatsApp Notification**: Warga otomatis dapat pesan WA saat surat _Disetujui_ atau _Ditolak_.
- **📊 Real-time Dashboard**: Statistik kependudukan (Gender, Pekerjaan, Usia) yang selalu update.
- **🖨️ Auto-Generate PDF**: Surat tercetak otomatis dengan format resmi (Kop Surat & TTD) via sistem.
- **🏘️ Manajemen Kewilayahan (Blok)**: Struktur data mendukung hierarki Desa > Lulugu (Blok) > Warga.

---

## 🛠️ Stack Teknologi (Tech Stack)

Dibangun dengan fondasi teknologi yang **Cepat, Aman, dan Skalatabel**:

- **Backend**: Python 3 (Flask Framework)
- **Database**: MySQL (Relational DB)
- **Frontend**: HTML5, Tailwind CSS (Modern UI), Alpine.js (Interactivity)
- **AI Engine**: Google Gemini API (Generative AI)
- **PDF Engine**: xhtml2pdf
- **Security**: Flask-WTF (CSRF Protection), Bcrypt (Password Hashing)

---

## 🚀 Panduan Instalasi (Localhost)

Ingin menjalankan proyek ini di komputer Anda? Ikuti langkah mudah ini:

1. **Clone Repository**

   ```bash
   git clone https://github.com/Diva-Baihaqi/SIPAD.git
   cd SIPAD
   ```

2. **Install Dependencies**
   Pastikan Python sudah terinstall, lalu jalankan:

   ```bash
   pip install -r requirements.txt
   ```

3. **Konfigurasi Database**

   - Import file `database/sid_desa.sql` ke MySQL Anda.
   - Buat file `.env` (duplikat dari `.env.example`) dan sesuaikan kredensial database.

4. **Jalankan Aplikasi**
   ```bash
   python app.py
   ```
   Akses di browser: `http://localhost:5000`

---

**© 2026 Pemerintah Desa Ciawiasih**.
_Dikembangkan dengan ❤️ dan ☕ oleh Diva Baihaqi._

