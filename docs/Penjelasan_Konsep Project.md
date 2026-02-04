# Dokumen Penjelasan Konsep & Teknis Project

**Sistem Informasi Pelayanan Administrasi Desa (SIPAD) - "Desa Ciawi Asih"**

Dokumen ini berisi penjelasan komprehensif mengenai arsitektur, fitur, dan konsep teknis yang diterapkan dalam pengembangan Sistem Informasi Desa Ciawiasih.

---

## 1. Latar Belakang & Filosofi Desain

Sistem ini dibangun dengan visi mewujudkan **"Desa Digital"** yang modern, transparan, dan melayani. Tidak sekadar memindahkan data dari kertas ke komputer, sistem ini dirancang untuk **memangkas birokrasi fisik** melalui layanan mandiri (self-service) yang dapat diakses warga kapan saja dan di mana saja.

### Konsep Desain: "Organic Modernism"

- **Visual**: Menggunakan tema alam (_Earth Tones_: Moss Green, Clay, Timber) dengan gaya **Glassmorphism** (transparansi kaca) yang memberikan kesan modern namun tetap hangat dan dekat dengan karakter pedesaan.
- **Responsivitas**: Dibangun dengan prinsip _Mobile-First_, memastikan seluruh fitur (termasuk dashboard admin dan chat AI) dapat diakses dengan nyaman melalui Smartphone.

---

## 2. Arsitektur Teknologi (Tech Stack)

Sistem ini dibangun menggunakan teknologi yang efisien, aman, dan _scalable_.

| Komponen              | Teknologi             | Penjelasan                                                             |
| :-------------------- | :-------------------- | :--------------------------------------------------------------------- |
| **Backend**           | Python (Flask)        | Framework web yang ringan, cepat, dan sangat fleksibel.                |
| **Database**          | MySQL                 | Penyimpanan data relasional untuk integritas data penduduk yang kuat.  |
| **Frontend**          | HTML5 + Tailwind CSS  | Styling modern tanpa perlu file CSS yang membengkak.                   |
| **Interaktivitas**    | Alpine.js             | Framework JS ringan untuk menu mobile, modal, dan logika UI sederhana. |
| **Kecerdasan Buatan** | Google Gemini (GenAI) | Otak di balik chatbot asisten desa ("LANA").                           |
| **Report Engine**     | Pandas & xhtml2pdf    | Generate laporan Excel data mentah dan PDF resmi siap cetak.           |

---

## 3. Fitur Unggulan Sistem

### A. LANA - Layanan Asisten Ciawiasih (AI Chatbot)

Bukan sekadar _template chat_, LANA adalah AI cerdas yang terintegrasi langsung dengan database desa.

- **Context-Aware**: Mengetahui profil desa, syarat surat, dan jam operasional kantor secara _real-time_.
- **Persona**: Karakter ramah, sopan, dan menggunakan Bahasa Indonesia yang mudah dipahami warga.
- **Floating Widget**: Selalu tersedia di pojok kanan bawah, siap menjawab pertanyaan warga 24/7.

### B. Layanan Surat Mandiri (Self-Service)

Memungkinkan warga mengajukan administrasi tanpa harus antri di Balai Desa.

1.  **Pengajuan Online**: Warga login, pilih jenis surat (SKTM, Domisili, Usaha, dll), isi form, kirim.
2.  **Tracking Status**: Warga bisa memantau apakah surat "Pending", "Diproses", atau "Selesai" dari dashboard mereka.
3.  **Cetak Mandiri**: Jika status "Disetujui", warga bisa langsung mencetak surat resmi (PDF) dari rumah atau HP.

### C. Manajemen Hak Akses & Peran (Role-Based Access Control)

Sistem SIPAD "Desa Ciawiasih" menerapkan pembagian hak akses yang tegas untuk menjaga keamanan dan efektivitas alur kerja. Berikut adalah rincian lengkap tugas dan fitur untuk masing-masing peran pengguna:

#### 1. Administrator (Admin IT)

Role dengan kewenangan tertinggi yang bertugas menjaga "kesehatan" dan konfigurasi sistem. Biasanya dipegang oleh Sekretaris Desa atau Petugas IT.

- **Manajemen Pengguna (User Management)**: Membuat, mengedit, dan menghapus akun pengguna sistem (Staff, Pimpinan, Warga). Mereset password jika ada pengguna yang lupa.
- **Konfigurasi Profil Desa**: Mengatur data inti desa yang akan tampil di Kop Surat (Nama Kades, NIP, Alamat, Logo).
- **Master Data**: Memiliki akses penuh (_Full Access_) untuk mengelola Database Penduduk, Kartu Keluarga, dan Jenis Surat.

#### 2. Kepala Desa (Pimpinan)

Role eksekutif yang didesain khusus untuk fungsi **Monitoring** dan **Evaluasi**. Akun ini tidak dibebani dengan tugas teknis input data.

- **Executive Dashboard**: Tampilan visual berisi grafik statistik demografi warga dan tren pelayanan surat.
- **Laporan Kinerja**: Fitur eksklusif untuk mengunduh **Laporan Kinerja Desa (PDF)** yang berisi rekapitulasi total layanan, performa staff, dan surat terlaris.
- **Pengawasan**: Memantau antrian surat yang pending atau layanan yang sering ditolak.

#### 3. Staff Desa (Operator Pelayanan)

Ujung tombak pelayanan administrasi sehari-hari. Bertugas memproses permohonan yang masuk baik secara online maupun offline.

- **Verifikasi Permohonan**: Menerima notifikasi surat masuk dari warga, memvalidasi kelengkapan data, dan memberikan status **Setujui** atau **Tolak**.
- **Manajemen Kependudukan**: Menginput data warga baru (Lahir/Pindah Datang) dan memperbarui data warga lama (Meninggal/Pindah Keluar).
- **Pencetakan Dokumen**: Mencetak surat resmi yang telah disetujui (PDF dengan Tanda Tangan & QR Code) untuk diserahkan ke warga.
- **Export Data**: Mengunduh data penduduk atau rekap surat dalam format **Excel** untuk kebutuhan arsip dan pelaporan ke kecamatan.

#### 4. Penduduk (Warga)

Pengguna layanan mandiri (_Self-Service_) yang mengakses sistem dari rumah melalui Smartphone atau Komputer.

- **Pengajuan Surat Online**: Memilih jenis layanan surat (SKTM, Domisili, Usaha, dll), mengisi formulir, dan mengirimnya tanpa perlu datang ke balai desa.
- **Tracking Status**: Memantau progres pengajuan secara _real-time_ (Pending ➝ Disetujui ➝ Selesai).
- **Unduh Dokumen**: Jika surat disetujui, warga dapat langsung mengunduh file surat (PDF) dari dashboard mereka untuk dicetak sendiri atau disimpan digital.
- **Akses AI Assistant**: Berinteraksi dengan **LANA** (Chatbot) untuk bertanya seputar persyaratan surat atau jam buka kantor desa.

---

## 4. Standarisasi Administrasi Resmi

Salah satu fokus utama pengembangan ini adalah output dokumen yang **standar pemerintah** dan profesional.

### Kop Surat Otomatis & Dinamis

Setiap hasil cetak surat atau laporan otomatis menyertakan Kop Surat resmi yang mengambil data dari database pengaturan desa (Nama Kabupaten, Kecamatan, Nama Desa, Alamat).

### Format Laporan (Reporting)

Sistem menyediakan dua format output untuk kebutuhan yang berbeda:

1.  **Format Excel (.xlsx)**
    - Ditujukan untuk **Olah Data** lanjutan oleh Staff.
    - Contoh: Rekapitulasi data penduduk, filter data penerima Bansos.
2.  **Format PDF (.pdf)**
    - Ditujukan untuk **Arsip Resmi & Cetak Fisik**.
    - Layout baku (A4/F4), rapi, terkunci (tidak bisa diedit sembarangan), dan memiliki kolom tanda tangan pejabat.

---

## 5. Keamanan Sistem (Security)

Keamanan adalah prioritas mutlak, terutama karena menyangkut NIK dan data pribadi warga.

- **Environment Variables (.env)**: Kunci rahasia (API Keys, Password Database) tidak ditulis langsung di kode, melainkan di file tersembunyi yang tidak akan ter-upload ke publik (GitHub).
- **Password Hashing**: Password pengguna dienkripsi menggunakan _Bcrypt_ sebelum disimpan ke database.
- **Session Management**: Login session yang aman untuk mencegah akses tidak sah.

---

## 6. Alur Kerja Aplikasi (Workflow)

1.  **Warga** mengakses website -> Bertanya pada AI (LANA) tentang syarat.
2.  **Warga** Login/Daftar -> Mengajukan Surat Keterangan Usaha -> Status: _Pending_.
3.  **Staff** menerima notifikasi di Dashboard -> Klik "Setujui" jika syarat lengkap.
4.  Status berubah menjadi _Selesai_ -> Nomor Surat digenerate otomatis.
5.  **Warga** atau **Staff** bisa mencetak surat dalam format PDF Resmi.
6.  **Kepala Desa** di akhir bulan mengunduh "Laporan Kinerja" untuk melihat rekapitulasi pelayanan.

---

## 7. Struktur Query Database (SQL)

Sistem menggunakan **MySQL** sebagai basis data relasional. Berikut adalah rincian query SQL utama yang digunakan dalam aplikasi, dikelompokkan berdasarkan fungsinya:

### A. Statistik & Dashboard

Query ini digunakan untuk menampilkan angka-angka di halaman depan (Home) dan Dashboard Admin/Pimpinan.

| Kegunaan                    | Contoh Syntax SQL (Simplified)                                                                                                          |
| :-------------------------- | :-------------------------------------------------------------------------------------------------------------------------------------- |
| **Total Penduduk**          | `SELECT COUNT(*) as total FROM penduduk`                                                                                                |
| **Total KK**                | `SELECT COUNT(*) as total FROM kartu_keluarga`                                                                                          |
| **Antrian Surat (Pending)** | `SELECT COUNT(*) FROM permohonan_surat WHERE status='Pending'`                                                                          |
| **Demografi Gender**        | `SELECT jenis_kelamin, COUNT(*) FROM penduduk GROUP BY jenis_kelamin`                                                                   |
| **Tren Surat Bulanan**      | `SELECT MONTH(tanggal_permohonan), COUNT(*) FROM permohonan_surat WHERE YEAR(tanggal) = YEAR(NOW()) GROUP BY MONTH(tanggal_permohonan)` |

### B. Otentikasi & Pengguna (User Management)

Menangani proses Login, Register, dan Manajemen Akun oleh Admin.

| Kegunaan             | Contoh Syntax SQL (Simplified)                                            |
| :------------------- | :------------------------------------------------------------------------ |
| **Cek Login**        | `SELECT * FROM users WHERE username = %s`                                 |
| **Daftar Akun Baru** | `INSERT INTO users (username, password, role, nik_penduduk) VALUES (...)` |
| **Update Profil**    | `UPDATE users SET username=%s, password=%s WHERE id=%s`                   |
| **Cek NIK Warga**    | `SELECT nama_lengkap FROM penduduk WHERE nik = %s` (Validasi saat Signup) |

### C. Layanan Surat Mandiri (Sisi Warga)

Query yang dieksekusi saat warga mengajukan surat atau mengecek status.

| Kegunaan             | Contoh Syntax SQL (Simplified)                                                                                            |
| :------------------- | :------------------------------------------------------------------------------------------------------------------------ |
| **Validasi Pemohon** | `SELECT * FROM penduduk WHERE nik = %s` (Memastikan NIK terdaftar)                                                        |
| **Kirim Permohonan** | `INSERT INTO permohonan_surat (nik_pemohon, jenis_surat, keperluan, status) VALUES (...)`                                 |
| **Riwayat/Tracking** | `SELECT p.*, j.nama_surat FROM permohonan_surat p JOIN jenis_surat j ON p.id_jenis_surat = j.id WHERE p.nik_pemohon = %s` |

### D. Manajemen Administrasi (Sisi Staff/Admin)

Digunakan Staff untuk memproses surat masuk dan mengelola data warga.

| Kegunaan             | Contoh Syntax SQL (Simplified)                                                                                                                             |
| :------------------- | :--------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **List Surat Masuk** | `SELECT p.*, pend.nama, j.jenis FROM permohonan_surat p JOIN penduduk pend ON ... JOIN jenis_surat j ON ... WHERE status LIKE %s ORDER BY created_at DESC` |
| **Setujui Surat**    | `UPDATE permohonan_surat SET status='Disetujui', no_surat=%s WHERE id=%s`                                                                                  |
| **Tolak Surat**      | `UPDATE permohonan_surat SET status='Ditolak' WHERE id=%s`                                                                                                 |
| **Cetak Surat**      | `SELECT * FROM permohonan_surat p JOIN penduduk pend ON ... JOIN kartu_keluarga kk ON ... WHERE p.id=%s` (Join 4 Tabel untuk data lengkap surat)           |
| **Tambah Warga**     | `INSERT INTO penduduk (nik, nama, tgl_lahir, ...) VALUES (...)`                                                                                            |
| **Tambah KK**        | `INSERT INTO kartu_keluarga (no_kk, kepala_keluarga, alamat, rt, rw) VALUES (...)`                                                                         |

### E. Laporan & Analitik (Reporting)

Query kompleks untuk menghasilkan data export Excel dan PDF Laporan Kinerja.

| Kegunaan                   | Contoh Syntax SQL (Simplified)                                                                                                           |
| :------------------------- | :--------------------------------------------------------------------------------------------------------------------------------------- |
| **Export Data Penduduk**   | `SELECT p.*, kk.no_kk FROM penduduk p LEFT JOIN kartu_keluarga kk ON p.no_kk = kk.no_kk ORDER BY nama`                                   |
| **Analisa Surat Terlaris** | `SELECT js.nama_surat, COUNT(ps.id) FROM permohonan_surat ps JOIN jenis_surat js ... GROUP BY js.nama_surat ORDER BY count DESC LIMIT 5` |
| **Breakdown Status**       | `SELECT status, COUNT(*) FROM permohonan_surat GROUP BY status`                                                                          |

### F. Pengaturan Sistem

| Kegunaan               | Contoh Syntax SQL (Simplified)                                       |
| :--------------------- | :------------------------------------------------------------------- |
| **Ambil Profil Desa**  | `SELECT * FROM profil_desa WHERE id=1`                               |
| **Update Profil Desa** | `UPDATE profil_desa SET nama_desa=%s, nama_kades=%s, ... WHERE id=1` |

---

## Kesimpulan

Sistem Informasi Desa Ciawiasih bukan sekadar website profil, melainkan sebuah **Sistem Manajemen Pelayanan Publik Terpadu**. Dengan mengintegrasikan AI, Database Digital, dan Otomasi Administrasi, sistem ini siap menjadi fondasi transformasi Desa Ciawiasih menuju Cirebon Smart Village.
