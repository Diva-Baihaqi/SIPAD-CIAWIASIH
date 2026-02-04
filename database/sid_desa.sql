CREATE DATABASE IF NOT EXISTS sid_desa;

USE sid_desa;

-- Tabel Users (Admin & Perangkat Desa)
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL, -- Akan di-hash
    role ENUM('admin', 'kades', 'staff') DEFAULT 'staff',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabel Kartu Keluarga
CREATE TABLE IF NOT EXISTS kartu_keluarga (
    no_kk VARCHAR(16) PRIMARY KEY,
    kepala_keluarga VARCHAR(100) NOT NULL,
    alamat TEXT NOT NULL,
    rt VARCHAR(3),
    rw VARCHAR(3),
    desa_kelurahan VARCHAR(50) DEFAULT 'Desa Sukamaju',
    kecamatan VARCHAR(50) DEFAULT 'Kecamatan Cerdas',
    kabupaten_kota VARCHAR(50) DEFAULT 'Kabupaten Maju',
    provinsi VARCHAR(50) DEFAULT 'Jawa Barat',
    kode_pos VARCHAR(5),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabel Penduduk
CREATE TABLE IF NOT EXISTS penduduk (
    nik VARCHAR(16) PRIMARY KEY,
    no_kk VARCHAR(16),
    nama_lengkap VARCHAR(100) NOT NULL,
    tempat_lahir VARCHAR(50),
    tanggal_lahir DATE,
    jenis_kelamin ENUM('L', 'P'),
    agama VARCHAR(20),
    pendidikan VARCHAR(50),
    pekerjaan VARCHAR(50),
    status_perkawinan ENUM(
        'Belum Kawin',
        'Kawin',
        'Cerai Hidup',
        'Cerai Mati'
    ),
    status_hubungan_dalam_keluarga ENUM(
        'Kepala Keluarga',
        'Suami',
        'Istri',
        'Anak',
        'Menantu',
        'Cucu',
        'Orangtua',
        'Mertua',
        'Famili Lain',
        'Pembantu'
    ),
    kewarganegaraan VARCHAR(3) DEFAULT 'WNI',
    nama_ayah VARCHAR(100),
    nama_ibu VARCHAR(100),
    status_penduduk ENUM(
        'Hidup',
        'Meninggal',
        'Pindah'
    ) DEFAULT 'Hidup',
    foto VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (no_kk) REFERENCES kartu_keluarga (no_kk) ON DELETE SET NULL
);

-- Tabel Jenis Surat
CREATE TABLE IF NOT EXISTS jenis_surat (
    id INT AUTO_INCREMENT PRIMARY KEY,
    kode_surat VARCHAR(20),
    nama_surat VARCHAR(100) NOT NULL,
    template_file VARCHAR(100)
);

-- Tabel Permohonan Surat
-- Tabel Permohonan Surat
CREATE TABLE IF NOT EXISTS permohonan_surat (
    id INT AUTO_INCREMENT PRIMARY KEY,
    no_surat VARCHAR(50),
    nik_pemohon VARCHAR(16) NULL,
    nama_pemohon VARCHAR(100), -- Diisi manual jika NIK null atau tidak match
    no_hp VARCHAR(20), -- Untuk konfirmasi via WA
    id_jenis_surat INT,
    tanggal_permohonan DATE DEFAULT(CURRENT_DATE),
    keperluan TEXT,
    status ENUM(
        'Pending',
        'Disetujui',
        'Ditolak'
    ) DEFAULT 'Pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_jenis_surat) REFERENCES jenis_surat (id)
);

-- Dummy Data untuk Login (Password: admin123)
-- MD5 dari 'admin123' adalah '0192023a7bbd73250516f069df18b500' (Hanya contoh, nanti pakai hash aman di Python)
INSERT IGNORE INTO
    users (username, password, role)
VALUES (
        'admin',
        '0192023a7bbd73250516f069df18b500',
        'admin'
    );