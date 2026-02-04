try:
    import MySQLdb
except ImportError:
    import pymysql
    pymysql.install_as_MySQLdb()

from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from dotenv import load_dotenv
load_dotenv()
import requests
import json
import os
import warnings
# Suppress Google GenAI Deprecation Warning
warnings.filterwarnings("ignore", category=FutureWarning)

import google.generativeai as genai
import datetime
# Trigger Reload
from flask_mysqldb import MySQL
from config import Config
import MySQLdb.cursors

from flask_bcrypt import Bcrypt

from flask_wtf.csrf import CSRFProtect

app = Flask(__name__)
app.config.from_object(Config)

# Inisialisasi MySQL, Bcrypt, dan CSRF Protection
mysql = MySQL(app)
bcrypt = Bcrypt(app)
csrf = CSRFProtect(app)

@app.route('/')
def index():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    
    # 1. Ambil data Jenis Surat
    try:
        cursor.execute("SELECT * FROM jenis_surat")
        jenis_surat = cursor.fetchall()
    except Exception as e:
        jenis_surat = []
        print(f"Error fetching surat: {e}")
        
    # 2. Ambil Statistik Kependudukan Real-time
    try:
        cursor.execute("SELECT COUNT(*) as total FROM penduduk")
        total_penduduk = cursor.fetchone()['total']
        
        cursor.execute("SELECT COUNT(*) as total FROM kartu_keluarga")
        total_kk = cursor.fetchone()['total']
        
        cursor.execute("SELECT COUNT(*) as total FROM penduduk WHERE jenis_kelamin='L'")
        total_laki = cursor.fetchone()['total']
        
        cursor.execute("SELECT COUNT(*) as total FROM penduduk WHERE jenis_kelamin='P'")
        total_perempuan = cursor.fetchone()['total']
        
        stats = {
            'penduduk': total_penduduk,
            'kk': total_kk,
            'laki': total_laki,
            'perempuan': total_perempuan
        }
    except Exception as e:
        stats = {'penduduk': 0, 'kk': 0, 'laki': 0, 'perempuan': 0}
        print(f"Error fetching stats: {e}")
    
    return render_template('index.html', jenis_surat=jenis_surat, stats=stats)

@app.route('/ajukan-surat', methods=['POST'])
def ajukan_surat():
    # 1. Cek Login
    if 'loggedin' not in session:
        flash('Silakan login terlebih dahulu untuk mengajukan surat.', 'danger')
        return redirect(url_for('login'))

    nik = request.form['nik']
    hp = request.form['hp'] # Ambil input No HP
    id_jenis_surat = request.form['id_jenis_surat']
    keperluan = request.form['keperluan']

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    
    # 1. Validasi: Cek apakah NIK ada di database penduduk?
    cursor.execute("SELECT nama_lengkap FROM penduduk WHERE nik = %s", (nik,))
    warga = cursor.fetchone()

    if not warga:
        flash('NIK tidak ditemukan! Silakan lapor ke kantor desa jika data belum ada.', 'danger')
        return redirect(url_for('index', _anchor='layanan'))
    
    # 2. Simpan Permohonan
    try:
        cursor.execute("""
            INSERT INTO permohonan_surat (nik_pemohon, no_hp, id_jenis_surat, keperluan, status, tanggal_permohonan)
            VALUES (%s, %s, %s, %s, 'Pending', NOW())
        """, (nik, hp, id_jenis_surat, keperluan))
        mysql.connection.commit()
        
        flash(f"Sukses! Permohonan surat berhasil dikirim. Admin akan menghubungi via WA: {hp}", 'success')
    except Exception as e:
        mysql.connection.rollback()
        flash(f"Terjadi kesalahan sistem: {e}", 'danger')

    return redirect(url_for('index', _anchor='layanan'))

@app.route('/cek-status', methods=['POST'])
def cek_status():
    if 'loggedin' not in session:
        flash('Silakan login untuk melacak permohonan.', 'danger')
        return redirect(url_for('login'))

    nik = request.form['nik_cek']
    
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    
    # Cari nama warga dulu
    cursor.execute("SELECT nama_lengkap FROM penduduk WHERE nik = %s", (nik,))
    warga = cursor.fetchone()
    
    if not warga:
        flash('NIK tidak ditemukan dalam database penduduk.', 'danger')
        return redirect(url_for('index', _anchor='cek-status'))
        
    # Ambil riwayat permohonan
    cursor.execute("""
        SELECT p.*, j.nama_surat 
        FROM permohonan_surat p
        JOIN jenis_surat j ON p.id_jenis_surat = j.id
        WHERE p.nik_pemohon = %s
        ORDER BY p.tanggal_permohonan DESC
    """, (nik,))
    history = cursor.fetchall()
    
    # Kita kirim data history kembali ke index tapi dengan variabel tambahan
    # Agar index.html bisa menampilkan modal/tabel hasil
    # Namun karena struktur index diatur via render_template awal, 
    # cara termudah adalah render template index lagi dengan data tambahan.
    
    # Perlu fetch data awal index lagi (jenis surat, stats) agar tidak error
    cursor.execute("SELECT * FROM jenis_surat")
    jenis_surat = cursor.fetchall()
    
    # (Statistik singkat saja untuk mengisi kekosongan, atau panggil fungsi helper jika ada)
    # Agar simple, kita redirect dengan flash message khusus atau render ulang.
    # Render ulang adalah UX terbaik.
    
    stats = {} # Skip stats berat untuk response cepat, atau biarkan kosong jika template handle safe
    # Re-fetch stats karena index butuh
    try:
        cursor.execute("SELECT COUNT(*) as total FROM penduduk")
        stats['penduduk'] = cursor.fetchone()['total']
        cursor.execute("SELECT COUNT(*) as total FROM kartu_keluarga")
        stats['kk'] = cursor.fetchone()['total']
        cursor.execute("SELECT COUNT(*) as total FROM penduduk WHERE jenis_kelamin='L'")
        stats['laki'] = cursor.fetchone()['total']
        cursor.execute("SELECT COUNT(*) as total FROM penduduk WHERE jenis_kelamin='P'")
        stats['perempuan'] = cursor.fetchone()['total']
    except:
        stats = {'penduduk':0, 'kk':0, 'laki':0, 'perempuan':0}

    return render_template('index.html', 
                           jenis_surat=jenis_surat, 
                           stats=stats, 
                           cek_result=history, 
                           cek_warga=warga,
                           scroll_to_cek=True) # Flag untuk scroll otomatis ke bagian hasil


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if 'loggedin' in session:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        nik = request.form['nik']
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        # Validasi Input
        if password != confirm_password:
            flash('Konfirmasi password tidak sesuai!', 'danger')
            return render_template('signup.html')

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
        # 1. Cek Apakah NIK Ada di Data Penduduk?
        cursor.execute('SELECT nama_lengkap FROM penduduk WHERE nik = %s', (nik,))
        resident = cursor.fetchone()
        
        if not resident:
            flash('NIK tidak ditemukan di database kependudukan desa! Pendaftaran khusus warga Desa Ciawi Asih.', 'danger')
            return render_template('signup.html')
            
        # 2. Cek Apakah NIK Sudah Punya Akun? (One NIK One Account)
        cursor.execute('SELECT id FROM users WHERE nik_penduduk = %s', (nik,))
        existing_nik = cursor.fetchone()
        
        if existing_nik:
            flash('NIK ini sudah terdaftar sebagai akun! Silakan login atau reset password.', 'danger')
            return render_template('signup.html')

        # 3. Cek Username Kembar
        cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
        account = cursor.fetchone()
        
        if account:
            flash('Username sudah terpakai, silakan pilih yang lain.', 'danger')
        else:
            # Hash Password & Simpan (Role Default: Penduduk, plus simpan NIK)
            pw_hash = bcrypt.generate_password_hash(password).decode('utf-8')
            
            try:
                cursor.execute('INSERT INTO users (username, password, role, nik_penduduk) VALUES (%s, %s, %s, %s)', 
                              (username, pw_hash, 'penduduk', nik))
                mysql.connection.commit()
                flash(f'Pendaftaran berhasil! Halo {resident["nama_lengkap"]}, silakan login.', 'success')
                return redirect(url_for('login'))
            except Exception as e:
                flash(f'Terjadi kesalahan: {e}', 'danger')

    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'loggedin' in session:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        try:
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
            account = cursor.fetchone()
            
            if account:
                # Verifikasi Password Hash Menggunakan Bcrypt
                # Jika password di DB masih plain text (legacy), akan error / fail check
                # Maka kita cek dulu.
                
                valid_pass = False
                try:
                    if bcrypt.check_password_hash(account['password'], password):
                        valid_pass = True
                except ValueError:
                    # Fallback untuk password lama yang belum di-hash (jika ada) - HANYA UNTUK TRANSISI
                    if account['password'] == password:
                        valid_pass = True
                        
                if valid_pass:
                    session['loggedin'] = True
                    session['id'] = account['id']
                    session['username'] = account['username']
                    session['role'] = account['role']
                    session['nik'] = account.get('nik_penduduk') # Simpan NIK di session untuk auto-fill
                    flash('Login Berhasil!', 'success')
                    return redirect(url_for('dashboard'))
                else:
                    flash('Password salah!', 'danger')
            else:
                flash('Username tidak ditemukan!', 'danger')


        except Exception as e:
            # Fallback jika Database belum disetup dengan benar agar user tidak stuck
            print(f"Database Error: {e}")
            flash(f"Gagal koneksi database: {e}", 'danger')
            
            # Backdoor untuk demo jika DB error
            if username == 'admin' and password == 'admin':
                session['loggedin'] = True
                session['username'] = 'Admin (Demo Mode)'
                session['role'] = 'admin'
                return redirect(url_for('dashboard'))

    return render_template('login.html')

@app.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    if 'loggedin' in session:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        username = request.form['username']
        nik = request.form['nik']
        new_password = request.form['new_password']

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
        # 1. Cek Kecocokan Username & NIK
        cursor.execute('SELECT * FROM users WHERE username = %s AND nik_penduduk = %s', (username, nik))
        account = cursor.fetchone()

        if account:
            # 2. Update Password Baru
            pw_hash = bcrypt.generate_password_hash(new_password).decode('utf-8')
            
            try:
                cursor.execute('UPDATE users SET password = %s WHERE id = %s', (pw_hash, account['id']))
                mysql.connection.commit()
                flash('Password berhasil direset! Silakan login dengan password baru.', 'success')
                return redirect(url_for('login'))
            except Exception as e:
                flash(f'Gagal update password: {e}', 'danger')
        else:
            flash('Verifikasi Gagal! Username dan NIK tidak cocok atau tidak ditemukan.', 'danger')

    return render_template('reset_password.html')

@app.route('/dashboard')
def dashboard():
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    
    role = session.get('role')
    if role == 'admin':
        return redirect(url_for('dashboard_admin'))
    elif role == 'pimpinan':
        return redirect(url_for('dashboard_pimpinan'))
    elif role == 'staff':
        return redirect(url_for('dashboard_staff'))
    elif role == 'penduduk':
        return redirect(url_for('dashboard_warga'))
    else:
        # Fallback if unknown role
        return redirect(url_for('dashboard_admin'))

@app.route('/dashboard/admin')
def dashboard_admin():
    if 'loggedin' not in session or session.get('role') != 'admin':
        # Proteksi jika user lain coba akses URL admin manual
        if session.get('role') == 'pimpinan': return redirect(url_for('dashboard_pimpinan'))
        # dst... biarkan simple dulu
        return redirect(url_for('login'))

    if 'loggedin' not in session:
        return redirect(url_for('login'))
        
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    
    # --- Statistik Dashboard ---
    # 1. Hitung total
    cursor.execute("SELECT COUNT(*) as total FROM penduduk")
    res_warga = cursor.fetchone()
    total_warga = res_warga['total'] if res_warga else 0
    
    cursor.execute("SELECT COUNT(*) as total FROM kartu_keluarga")
    res_kk = cursor.fetchone()
    total_kk = res_kk['total'] if res_kk else 0
    
    cursor.execute("SELECT COUNT(*) as total FROM permohonan_surat WHERE status='Pending'")
    res_pending = cursor.fetchone()
    pending_surat = res_pending['total'] if res_pending else 0
    
    # 2. Data Grafik Gender
    cursor.execute("SELECT jenis_kelamin, COUNT(*) as jumlah FROM penduduk GROUP BY jenis_kelamin")
    gender_data = cursor.fetchall()
    # Format ke [L, P]
    l = 0
    p = 0
    if gender_data:
        for item in gender_data:
            if item['jenis_kelamin'] == 'L': l = item['jumlah']
            elif item['jenis_kelamin'] == 'P': p = item['jumlah']

    # 3. Data Grafik Surat Bulanan
    # Query agak kompleks dikit (Count Group By Month)
    cursor.execute("""
        SELECT MONTH(tanggal_permohonan) as bulan, COUNT(*) as total 
        FROM permohonan_surat 
        WHERE YEAR(tanggal_permohonan) = YEAR(CURDATE())
        GROUP BY MONTH(tanggal_permohonan)
    """)
    surat_data = cursor.fetchall()
    # Mapping ke array 12 bulan (Initial 0)
    surat_bulanan = [0] * 6 
    if surat_data:
        for row in surat_data:
            if 1 <= row['bulan'] <= 6:
                surat_bulanan[row['bulan']-1] = row['total']

    stats = {
        'total_warga': total_warga,
        'total_kk': total_kk,
        'pending_surat': pending_surat,
        'warga_gender': [l, p],
        'surat_bulanan': surat_bulanan
    }
    
    return render_template('dashboard/index.html', stats=stats)

@app.route('/dashboard/pimpinan')
def dashboard_pimpinan():
    if 'loggedin' not in session or session.get('role') not in ['pimpinan', 'admin']: 
        return redirect(url_for('login'))
    
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    
    # --- Statistik Dashboard Pimpinan (Mirip Admin tapi Read Only) ---
    # 1. Total Penduduk & KK
    cursor.execute("SELECT COUNT(*) as total FROM penduduk")
    res_warga = cursor.fetchone()
    total_warga = res_warga['total'] if res_warga else 0
    
    cursor.execute("SELECT COUNT(*) as total FROM kartu_keluarga")
    res_kk = cursor.fetchone()
    total_kk = res_kk['total'] if res_kk else 0
    
    # 2. Total Surat Pending (Sebagai Indikator Kinerja Staff)
    cursor.execute("SELECT COUNT(*) as total FROM permohonan_surat WHERE status='Pending'")
    res_pending = cursor.fetchone()
    pending_surat = res_pending['total'] if res_pending else 0
    
    # 3. Grafik Gender
    cursor.execute("SELECT jenis_kelamin, COUNT(*) as jumlah FROM penduduk GROUP BY jenis_kelamin")
    gender_data = cursor.fetchall()
    l, p = 0, 0
    if gender_data:
        for item in gender_data:
            if item['jenis_kelamin'] == 'L': l = item['jumlah']
            elif item['jenis_kelamin'] == 'P': p = item['jumlah']

    # 4. Grafik Surat Bulanan
    cursor.execute("""
        SELECT MONTH(tanggal_permohonan) as bulan, COUNT(*) as total 
        FROM permohonan_surat 
        WHERE YEAR(tanggal_permohonan) = YEAR(CURDATE())
        GROUP BY MONTH(tanggal_permohonan)
    """)
    surat_data = cursor.fetchall()
    surat_bulanan = [0] * 6 
    if surat_data:
        for row in surat_data:
            if 1 <= row['bulan'] <= 6:
                surat_bulanan[row['bulan']-1] = row['total']

    stats = {
        'total_warga': total_warga,
        'total_kk': total_kk,
        'pending_surat': pending_surat,
        'warga_gender': [l, p],
        'surat_bulanan': surat_bulanan
    }
    
    return render_template('dashboard/pimpinan.html', stats=stats)

@app.route('/dashboard/staff')
def dashboard_staff():
    if 'loggedin' not in session or session.get('role') != 'staff': 
        return redirect(url_for('login'))
        
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    
    # 1. Stats Harian (Operasional)
    # Pending Global (Beban Kerja)
    cursor.execute("SELECT COUNT(*) as total FROM permohonan_surat WHERE status='Pending'")
    pending_surat = cursor.fetchone()['total']
    
    # Selesai Hari Ini
    cursor.execute("SELECT COUNT(*) as total FROM permohonan_surat WHERE status='Selesai' AND DATE(tanggal_permohonan) = CURDATE()")
    selesai_hari_ini = cursor.fetchone()['total']
    
    # Ditolak Hari Ini
    cursor.execute("SELECT COUNT(*) as total FROM permohonan_surat WHERE status='Ditolak' AND DATE(tanggal_permohonan) = CURDATE()")
    ditolak_hari_ini = cursor.fetchone()['total']

    # Total Warga (Info Umum)
    cursor.execute("SELECT COUNT(*) as total FROM penduduk")
    total_warga = cursor.fetchone()['total']
    
    # 2. Grafik Mingguan (7 Hari Terakhir)
    # Query untuk mengambil jumlah surat per hari dalam 7 hari terakhir
    cursor.execute("""
        SELECT DATE(tanggal_permohonan) as tanggal_obj, COUNT(*) as total 
        FROM permohonan_surat 
        WHERE tanggal_permohonan >= DATE_SUB(CURDATE(), INTERVAL 6 DAY)
        GROUP BY DATE(tanggal_permohonan)
        ORDER BY DATE(tanggal_permohonan) ASC
    """)
    weekly_data = cursor.fetchall()
    
    # Format data untuk Chart.js (Format Python handling strict SQL mode)
    # Gunakan strftime jika objek date, atau string formatting manual jika string
    weekly_stats = []
    for r in weekly_data:
        tgl = r['tanggal_obj']
        # Handle jika driver mengembalikan string atau datetime object
        if hasattr(tgl, 'strftime'):
            fmt_date = tgl.strftime('%d %b')
        else:
             # Fallback simple string manipulation for YYYY-MM-DD
            try:
                 import datetime
                 if isinstance(tgl, str):
                     tgl_obj = datetime.datetime.strptime(tgl, '%Y-%m-%d')
                     fmt_date = tgl_obj.strftime('%d %b')
                 else:
                     fmt_date = str(tgl)
            except:
                fmt_date = str(tgl)

        weekly_stats.append({'date': fmt_date, 'total': r['total']})

    stats = {
        'pending_surat': pending_surat,
        'surat_selesai_hari_ini': selesai_hari_ini,
        'surat_ditolak_hari_ini': ditolak_hari_ini,
        'total_warga': total_warga,
        'weekly_stats': weekly_stats
    }
    
    return render_template('dashboard/staff.html', stats=stats)

@app.route('/warga')
def dashboard_warga():
    if 'loggedin' not in session: return redirect(url_for('login'))
    
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    
    # Ambil data User & NIK
    user_id = session.get('id')
    
    # 1. Cek Data Penduduk (jika ada NIK link)
    penduduk = None
    nik_linked = None
    
    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    
    if user and user.get('nik_penduduk'):
        nik_linked = user['nik_penduduk']
        cursor.execute("SELECT * FROM penduduk WHERE nik = %s", (nik_linked,))
        penduduk = cursor.fetchone()

    # 2. Ambil Riwayat Permohonan (Berdasarkan NIK linked ATAU Username jika belum link - opsi fallback)
    riwayat = []
    if nik_linked:
        cursor.execute("""
            SELECT ps.*, js.nama_surat 
            FROM permohonan_surat ps
            JOIN jenis_surat js ON ps.id_jenis_surat = js.id
            WHERE ps.nik_pemohon = %s
            ORDER BY ps.created_at DESC
        """, (nik_linked,))
        riwayat = cursor.fetchall()
        
    return render_template('dashboard/warga.html', penduduk=penduduk, riwayat=riwayat)

# --- FITUR ADMIN: MANAJEMEN SURAT ---

@app.route('/dashboard/permohonan')
def kelola_permohonan():
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    
    # Ambil parameter filter dari Query String
    search_q = request.args.get('q', '')
    filter_status = request.args.get('status', '')
    filter_jenis = request.args.get('jenis', '')

    # 1. Ambil list Jenis Surat untuk dropdown
    cursor.execute("SELECT * FROM jenis_surat")
    jenis_surat_list = cursor.fetchall()

    # 2. Build Query Dinamis
    # KEMBALI KE BASIC: Join Pending dengan Penduduk via NIK
    query = """
        SELECT p.*, pend.nama_lengkap, j.nama_surat 
        FROM permohonan_surat p
        JOIN penduduk pend ON p.nik_pemohon = pend.nik
        JOIN jenis_surat j ON p.id_jenis_surat = j.id
        WHERE 1=1
    """
    params = []

    # Filter Search (NIK / Nama)
    if search_q:
        query += " AND (pend.nama_lengkap LIKE %s OR p.nik_pemohon LIKE %s)"
        params.extend([f"%{search_q}%", f"%{search_q}%"])
    
    # Filter Status
    if filter_status:
        query += " AND p.status = %s"
        params.append(filter_status)
    
    # Filter Jenis Surat
    if filter_jenis:
        query += " AND p.id_jenis_surat = %s"
        params.append(filter_jenis)

    # Urutkan: Surat Terbaru di paling atas (Real Time)
    query += " ORDER BY p.created_at DESC"

    cursor.execute(query, tuple(params))
    permohonan = cursor.fetchall()
    
    return render_template('dashboard/permohonan.html', 
                           permohonan=permohonan, 
                           jenis_surat=jenis_surat_list,
                           q=search_q,
                           status=filter_status,
                           jenis=filter_jenis)

# --- API REALTIME STATS ---
@app.route('/api/stats')
def api_stats():
    if 'loggedin' not in session:
        return {'error': 'Unauthorized'}, 401
        
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    
    # 1. Hitung total
    cursor.execute("SELECT COUNT(*) as total FROM penduduk")
    res_warga = cursor.fetchone()
    total_warga = res_warga['total'] if res_warga else 0
    
    cursor.execute("SELECT COUNT(*) as total FROM kartu_keluarga")
    res_kk = cursor.fetchone()
    total_kk = res_kk['total'] if res_kk else 0
    
    cursor.execute("SELECT COUNT(*) as total FROM permohonan_surat WHERE status='Pending'")
    res_pending = cursor.fetchone()
    pending_surat = res_pending['total'] if res_pending else 0
    
    # 2. Data Grafik Gender
    cursor.execute("SELECT jenis_kelamin, COUNT(*) as jumlah FROM penduduk GROUP BY jenis_kelamin")
    gender_data = cursor.fetchall()
    l, p = 0, 0
    if gender_data:
        for item in gender_data:
            if item['jenis_kelamin'] == 'L': l = item['jumlah']
            elif item['jenis_kelamin'] == 'P': p = item['jumlah']

    # 3. Data Grafik Surat Bulanan
    cursor.execute("""
        SELECT MONTH(tanggal_permohonan) as bulan, COUNT(*) as total 
        FROM permohonan_surat 
        WHERE YEAR(tanggal_permohonan) = YEAR(CURDATE())
        GROUP BY MONTH(tanggal_permohonan)
    """)
    surat_data = cursor.fetchall()
    surat_bulanan = [0] * 6 
    if surat_data:
        for row in surat_data:
            if 1 <= row['bulan'] <= 6:
                surat_bulanan[row['bulan']-1] = row['total']
    # 4. Stats Operasional Harian (Untuk Dashboard Staff Real-time)
    cursor.execute("SELECT COUNT(*) as total FROM permohonan_surat WHERE status='Selesai' AND DATE(tanggal_permohonan) = CURDATE()")
    selesai_hari_ini = cursor.fetchone()['total']
    
    cursor.execute("SELECT COUNT(*) as total FROM permohonan_surat WHERE status='Ditolak' AND DATE(tanggal_permohonan) = CURDATE()")
    ditolak_hari_ini = cursor.fetchone()['total']

    return {
        'total_warga': total_warga,
        'total_kk': total_kk,
        'pending_surat': pending_surat,
        'warga_gender': [l, p],
        'surat_bulanan': surat_bulanan,
        'surat_selesai_hari_ini': selesai_hari_ini,
        'surat_ditolak_hari_ini': ditolak_hari_ini
    }

@app.route('/api/chat', methods=['POST'])
@csrf.exempt
def api_chat():
    data = request.get_json()
    user_message = data.get('message', '')
    
    if not user_message:
        return jsonify({'reply': 'Maaf, LANA tidak mendengar pertanyaan Anda.'}), 400

    # 1. Load Context dari JSON
    try:
        json_path = os.path.join(app.root_path, 'data', 'desa_context.json')
        with open(json_path, 'r', encoding='utf-8') as f:
            desa_context = json.load(f)
    except Exception as e:
        print(f"Error loading context: {e}")
        desa_context = {} # Fallback empty

    # 2. Ambil Statistik Realtime & Waktu Saat Ini
    stats_summary = "Data Statistik Terkini: "
    
    # --- Logic Waktu Indonesia & Status Kantor ---
    now = datetime.datetime.now()
    days = ['Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat', 'Sabtu', 'Minggu']
    months = ['Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni', 'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember']
    
    hari_str = days[now.weekday()]
    tgl_str = f"{now.day} {months[now.month - 1]} {now.year}"
    jam_str = now.strftime('%H:%M')
    waktu_saat_ini = f"{hari_str}, {tgl_str}, Pukul {jam_str} WIB"
    
    # 1. Logic Sapaan (Greeting)
    hour = now.hour
    if 4 <= hour < 11: sapaan_waktu = "Selamat Pagi"
    elif 11 <= hour < 15: sapaan_waktu = "Selamat Siang"
    elif 15 <= hour < 18: sapaan_waktu = "Selamat Sore"
    else: sapaan_waktu = "Selamat Malam"

    # 2. Logic Buka/Tutup (Senin-Jumat, 08:00 - 15:00)
    is_hari_kerja = 0 <= now.weekday() <= 4 
    is_jam_kerja = 8 <= hour < 15
    
    status_kantor = "BUKA" if is_hari_kerja and is_jam_kerja else "TUTUP"
    
    # 3. Logic Kapan Buka Lagi (Next Open)
    kapan_buka = ""
    if status_kantor == "TUTUP":
        if is_hari_kerja:
            if hour < 8:
                kapan_buka = "Akan buka HARI INI jam 08:00 WIB."
            else:
                # Sudah lewat jam 15:00
                if now.weekday() == 4: # Jika Jumat
                    kapan_buka = "Akan buka lagi SENIN depan jam 08:00 WIB."
                else:
                    kapan_buka = "Akan buka BESOK jam 08:00 WIB."
        else:
            # Sabtu/Minggu
            kapan_buka = "Akan buka lagi SENIN jam 08:00 WIB."
            
    info_waktu = f"WAKTU SAAT INI: {waktu_saat_ini}\nSAPAAN YANG TEPAT: {sapaan_waktu}\nSTATUS KANTOR: {status_kantor}\nINFO BUKA: {kapan_buka}"
    # ---------------------------------------------

    try:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT COUNT(*) as total FROM penduduk")
        jml_penduduk = cursor.fetchone()['total']
        
        cursor.execute("SELECT COUNT(*) as total FROM kartu_keluarga")
        jml_kk = cursor.fetchone()['total']
        
        cursor.execute("SELECT COUNT(*) as total FROM permohonan_surat WHERE status='Pending'")
        surat_pending = cursor.fetchone()['total']
        
        stats_summary += f"Total Penduduk: {jml_penduduk} Orang, Total Kepala Keluarga: {jml_kk} KK, Surat Sedang Diproses: {surat_pending}."
    except Exception as e:
        stats_summary += "Data statistik sedang tidak tersedia."

    # 3. Build System Prompt yang KETAT
    system_instruction = f"""
    Kamu adalah 'LANA', Virtual Assistant resmi untuk DEsa Ciawiasih.
    
    INSTRUKSI UTAMA:
    1. Kamu HANYA boleh menjawab pertanyaan yang berkaitan dengan Desa Ciawiasih, Pemerintahan Desa, Layanan Administrasi, dan Informasi Penduduk.
    2. Jika pengguna bertanya tentang hal di luar konteks desa (misal: "Siapa Presiden Amerika?", "Hitung 5+5", "Buatkan kode python", "resep masakan"), kamu harus MENOLAK dengan sopan dan ramah.
       Contoh penolakan: "Maaf, Lana hanya bisa membantu seputar informasi dan layanan di Desa Ciawiasih saja ya kak 😊."
    3. JANGAN PERNAH mengarang data (halusinasi). Gunakan HANYA informasi yang disediakan di KONTEKS di bawah ini. Jika info tidak ada di konteks, katakan bahwa kamu belum memiliki informasi tersebut dan sarankan hubungi kantor desa.
    4. Gaya bahasa: Ramah, melayani, menggunakan Bahasa Indonesia yang baik, sesekali gunakan emoji yang relevan.
    5. Jawab pertanyaan waktu (kapan, hari apa, jam berapa, buka/tutup) dengan mengacu pada '{info_waktu}'.

    INFO WAKTU REAL-TIME:
    {info_waktu}

    KONTEKS PENGETAHUAN (DATA DESA):
    {json.dumps(desa_context, indent=2)}

    DATA STATISTIK LIVE (SAAT INI):
    {stats_summary}

    TUGAS KAMU:
    Jawab pertanyaan user berdasarkan KONTEKS, WAKTU REAL-TIME, dan STATISTIK di atas.
    """
    
    api_key = app.config['GEMINI_API_KEY']
    
    if not api_key or 'MASUKKAN_KEY' in api_key:
         return jsonify({'reply': 'Maaf, sistem Lana belum dikonfigurasi (API Key hilang).'}), 500

    try:
        # Konfigurasi Gemini
        genai.configure(api_key=api_key)
        
        # Inisialisasi Model
        model = genai.GenerativeModel('gemini-flash-latest')
        
        # Kirim Pesan dengan Sistem Instruksi
        # Gemini Python SDK cara pakainya agak beda, kita masukkan system instruction di prompt atau logic chat
        
        chat = model.start_chat(history=[
            {"role": "user", "parts": [system_instruction]},
            {"role": "model", "parts": ["Siap, saya mengerti. Saya LANA, asisten Desa Ciawiasih. Silakan ajukan pertanyaan."]}
        ])
        
        response = chat.send_message(user_message)
        bot_reply = response.text
        
        return jsonify({'reply': bot_reply})
            
    except Exception as e:
        print(f"Gemini Error: {e}")
        return jsonify({'reply': f'Maaf, LANA sedang pusing ({str(e)}).'}), 500


@app.route('/dashboard/permohonan/setujui/<int:id>', methods=['POST'])
def setujui_surat(id):
    if 'loggedin' not in session: return redirect(url_for('login'))
    
    # Prepare Cursor
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    
    # 1. Ambil Data Pemohon Dulu (untuk Link WA)
    cursor.execute("SELECT no_hp, nik_pemohon FROM permohonan_surat WHERE id = %s", (id,))
    data = cursor.fetchone()
    
    # Generate Nomor Surat Otomatis (Format dummy: 470 / ID / DS / Tahun)
    import datetime
    tahun = datetime.date.today().year
    no_surat = f"474/{id}/DS/{tahun}"
    
    # 2. Update Status
    cursor.execute("UPDATE permohonan_surat SET status = 'Disetujui', no_surat = %s WHERE id = %s", (no_surat, id))
    mysql.connection.commit()
    
    # 3. Pesan Flash dengan Link WA
    msg = 'Surat disetujui! Nomor diterbitkan.'
    if data and data['no_hp']:
        hp = data['no_hp']
        if hp.startswith('0'): hp = '62' + hp[1:]
        wa_link = f"https://wa.me/{hp}?text=Halo%20Warga%20Ciawiasih,%20surat%20permohonan%20Anda%20telah%20DISETUJUI%20dan%20siap%20diambil."
        msg += f' <a href="{wa_link}" target="_blank" class="underline font-bold ml-1">Kirim WA ke Warga &rarr;</a>'
    
    flash(msg, 'success')
    return redirect(url_for('kelola_permohonan'))

@app.route('/dashboard/permohonan/tolak/<int:id>', methods=['POST'])
def tolak_surat(id):
    if 'loggedin' not in session: return redirect(url_for('login'))
    
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    
    # 1. Ambil Data
    cursor.execute("SELECT no_hp FROM permohonan_surat WHERE id = %s", (id,))
    data = cursor.fetchone()
    
    # 2. Update
    cursor.execute("UPDATE permohonan_surat SET status = 'Ditolak' WHERE id = %s", (id,))
    mysql.connection.commit()
    
    # 3. Pesan WA
    msg = 'Permohonan surat ditolak.'
    if data and data['no_hp']:
        hp = data['no_hp']
        if hp.startswith('0'): hp = '62' + hp[1:]
        wa_link = f"https://wa.me/{hp}?text=Halo,%20mohon%20maaf%20permohonan%20surat%20Anda%20kami%20TOLAK%20karena%20data%20belum%20lengkap.%20Silakan%20ajukan%20ulang."
        msg += f' <a href="{wa_link}" target="_blank" class="underline font-bold ml-1 text-red-800">Info ke WA &rarr;</a>'
    
    flash(msg, 'danger')
    return redirect(url_for('kelola_permohonan'))

@app.route('/dashboard/permohonan/cetak/<int:id>')
def cetak_surat(id):
    if 'loggedin' not in session: return redirect(url_for('login'))
    
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    
    # Query Data Lengkap untuk Surat (Join 4 Tabel: Permohonan -> Penduduk -> KK -> JenisSurat)
    query = """
        SELECT p.*, 
               pend.nama_lengkap, pend.tempat_lahir, pend.tanggal_lahir, pend.jenis_kelamin, 
               pend.pekerjaan, pend.agama, pend.status_perkawinan, pend.kewarganegaraan,
               kk.alamat, kk.rt, kk.rw, kk.desa_kelurahan, kk.kecamatan,
               j.nama_surat, j.kode_surat
        FROM permohonan_surat p
        JOIN penduduk pend ON p.nik_pemohon = pend.nik
        JOIN kartu_keluarga kk ON pend.no_kk = kk.no_kk
        JOIN jenis_surat j ON p.id_jenis_surat = j.id
        WHERE p.id = %s
    """
    cursor.execute(query, (id,))
    data = cursor.fetchone()
    
    if not data:
        flash('Data surat tidak ditemukan', 'danger')
        return redirect(url_for('kelola_permohonan'))
        
    # Ambil Data Profil Desa
    cursor.execute("SELECT * FROM profil_desa WHERE id=1")
    profil = cursor.fetchone()
        
    return render_template('dashboard/cetak_surat.html', data=data, profil=profil)

# --- FITUR ADMIN: MANAJEMEN PENDUDUK ---

@app.route('/dashboard/penduduk')
def kelola_penduduk():
    if 'loggedin' not in session: return redirect(url_for('login'))
    
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    # Ambil data penduduk limit 100 biar gak berat (bisa ditambah pagination nanti)
    cursor.execute("SELECT * FROM penduduk ORDER BY created_at DESC LIMIT 100")
    penduduk = cursor.fetchall()
    
    # Ambil list KK untuk dropdown tambah warga
    cursor.execute("SELECT no_kk, kepala_keluarga FROM kartu_keluarga")
    list_kk = cursor.fetchall()
    
    return render_template('dashboard/penduduk.html', penduduk=penduduk, list_kk=list_kk)

@app.route('/dashboard/penduduk/tambah', methods=['POST'])
def tambah_penduduk():
    if 'loggedin' not in session: return redirect(url_for('login'))
    
    # Ambil data dari form
    nik = request.form['nik']
    nama = request.form['nama']
    no_kk = request.form['no_kk']
    jk = request.form['jk']
    tmp_lahir = request.form['tempat_lahir']
    tgl_lahir = request.form['tanggal_lahir']
    agama = request.form['agama']
    pekerjaan = request.form['pekerjaan']
    status_kawin = request.form['status_kawin']
    
    cursor = mysql.connection.cursor()
    try:
        cursor.execute("""
            INSERT INTO penduduk (nik, no_kk, nama_lengkap, jenis_kelamin, tempat_lahir, tanggal_lahir, agama, pekerjaan, status_perkawinan)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (nik, no_kk, nama, jk, tmp_lahir, tgl_lahir, agama, pekerjaan, status_kawin))
        mysql.connection.commit()
        flash('Data penduduk berhasil ditambahkan!', 'success')
    except Exception as e:
        mysql.connection.rollback()
        flash(f'Gagal menambah data: {e}', 'danger')
        
    return redirect(url_for('kelola_penduduk'))

@app.route('/dashboard/penduduk/edit', methods=['POST'])
def edit_penduduk():
    if 'loggedin' not in session: return redirect(url_for('login'))
    
    nik_lama = request.form['nik_lama'] # Acuan WHERE
    # Data baru
    nama = request.form['nama']
    no_kk = request.form['no_kk']
    jk = request.form['jk']
    pekerjaan = request.form['pekerjaan']
    status_kawin = request.form['status_kawin']
    
    cursor = mysql.connection.cursor()
    try:
        cursor.execute("""
            UPDATE penduduk 
            SET nama_lengkap=%s, no_kk=%s, jenis_kelamin=%s, pekerjaan=%s, status_perkawinan=%s
            WHERE nik=%s
        """, (nama, no_kk, jk, pekerjaan, status_kawin, nik_lama))
        mysql.connection.commit()
        flash('Data penduduk berhasil diperbarui!', 'success')
    except Exception as e:
        flash(f'Gagal update: {e}', 'danger')
        
    return redirect(url_for('kelola_penduduk'))

@app.route('/dashboard/penduduk/hapus/<nik>', methods=['POST'])
def hapus_penduduk(nik):
    if 'loggedin' not in session: return redirect(url_for('login'))
    
    cursor = mysql.connection.cursor()
    try:
        cursor.execute("DELETE FROM penduduk WHERE nik = %s", (nik,))
        mysql.connection.commit()
        flash('Data penduduk dihapus.', 'success')
    except Exception as e:
        flash(f'Gagal hapus (mungkin data terkait surat?): {e}', 'danger')
        
    return redirect(url_for('kelola_penduduk'))

# --- FITUR ADMIN: MANAJEMEN KARTU KELUARGA (KK) ---

@app.route('/dashboard/kk')
def kelola_kk():
    if 'loggedin' not in session: return redirect(url_for('login'))
    
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM kartu_keluarga ORDER BY created_at DESC")
    kk = cursor.fetchall()
    
    return render_template('dashboard/kk.html', kk=kk)

@app.route('/dashboard/kk/tambah', methods=['POST'])
def tambah_kk():
    if 'loggedin' not in session: return redirect(url_for('login'))
    
    no_kk = request.form['no_kk']
    kepala = request.form['kepala_keluarga']
    alamat = request.form['alamat']
    rt = request.form['rt']
    rw = request.form['rw']
    kecamatan = request.form['kecamatan']
    
    cursor = mysql.connection.cursor()
    try:
        cursor.execute("""
            INSERT INTO kartu_keluarga (no_kk, kepala_keluarga, alamat, rt, rw, kecamatan)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (no_kk, kepala, alamat, rt, rw, kecamatan))
        mysql.connection.commit()
        flash('Kartu Keluarga baru berhasil ditambahkan!', 'success')
    except Exception as e:
        flash(f'Gagal tambah KK: {e}', 'danger')
        
    return redirect(url_for('kelola_kk'))

@app.route('/dashboard/kk/hapus/<no_kk>', methods=['POST'])
def hapus_kk(no_kk):
    if 'loggedin' not in session: return redirect(url_for('login'))
    
    cursor = mysql.connection.cursor()
    try:
        cursor.execute("DELETE FROM kartu_keluarga WHERE no_kk = %s", (no_kk,))
        mysql.connection.commit()
        flash('Data KK dihapus.', 'success')
    except Exception as e:
        flash(f'Gagal hapus KK (Pastikan tidak ada anggota keluarga di dalamnya): {e}', 'belum')
        
    return redirect(url_for('kelola_kk'))

# --- FITUR ADMIN: LAPORAN & REKAP ---
@app.route('/dashboard/laporan', methods=['GET'])
def laporan():
    if 'loggedin' not in session: return redirect(url_for('login'))
    
    import datetime
    sekarang = datetime.date.today()
    
    # Ambil filter dari request, atau default ke Bulan & Tahun saat ini
    bulan = request.args.get('bulan', sekarang.month)
    tahun = request.args.get('tahun', sekarang.year)
    status = request.args.get('status', '') # Filter opsional
    
    try:
        bulan = int(bulan)
        tahun = int(tahun)
    except ValueError:
        bulan = sekarang.month
        tahun = sekarang.year

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    
    # Base Query
    query = """
        SELECT p.*, pend.nama_lengkap, j.nama_surat 
        FROM permohonan_surat p
        JOIN penduduk pend ON p.nik_pemohon = pend.nik
        JOIN jenis_surat j ON p.id_jenis_surat = j.id
        WHERE MONTH(p.tanggal_permohonan) = %s 
        AND YEAR(p.tanggal_permohonan) = %s
    """
    params = [bulan, tahun]
    
    # Tambah kondisi status jika dipilih
    if status and status != 'Semua':
        query += " AND p.status = %s"
        params.append(status)
        
    query += " ORDER BY p.tanggal_permohonan DESC"
    
    cursor.execute(query, tuple(params))
    laporan_data = cursor.fetchall()

    # Tambahan: Ambil Data Profil Desa untuk Kop/TTD
    cursor.execute("SELECT * FROM profil_desa WHERE id=1")
    profil = cursor.fetchone()
        
    # Kirim data ke template
    return render_template('dashboard/laporan.html', 
                           laporan=laporan_data, 
                           pilih_bulan=bulan, 
                           pilih_tahun=tahun, 
                           pilih_status=status,
                           profil=profil)

# --- FITUR ADMIN: MANAJEMEN USER ---
@app.route('/dashboard/users')
def kelola_users():
    if 'loggedin' not in session or session.get('role') != 'admin':
        return redirect(url_for('login'))
        
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM users ORDER BY role, username")
    users = cursor.fetchall()
    
    return render_template('dashboard/users.html', users=users)

@app.route('/dashboard/users/tambah', methods=['POST'])
@csrf.exempt
def tambah_user():
    if 'loggedin' not in session or session.get('role') != 'admin': return redirect(url_for('login'))
    
    username = request.form['username']
    password = request.form['password']
    role = request.form['role']
    
    cursor = mysql.connection.cursor()
    # Cek duplikat
    cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
    if cursor.fetchone():
        flash('Username sudah ada!', 'danger')
        return redirect(url_for('kelola_users'))
        
    try:
        pw_hash = bcrypt.generate_password_hash(password).decode('utf-8')
        cursor.execute("INSERT INTO users (username, password, role) VALUES (%s, %s, %s)", (username, pw_hash, role))
        mysql.connection.commit()
        flash('User baru berhasil ditambahkan.', 'success')
    except Exception as e:
        flash(f'Gagal tambah user: {e}', 'danger')
        
    return redirect(url_for('kelola_users'))

@app.route('/dashboard/users/edit', methods=['POST'])
@csrf.exempt
def edit_user():
    if 'loggedin' not in session or session.get('role') != 'admin': return redirect(url_for('login'))
    
    id_user = request.form['id_user']
    username = request.form['username']
    role = request.form['role']
    password = request.form.get('password') # Opsional
    
    cursor = mysql.connection.cursor()
    try:
        if password and password.strip():
            # Update dengan password baru
            pw_hash = bcrypt.generate_password_hash(password).decode('utf-8')
            cursor.execute("UPDATE users SET username=%s, role=%s, password=%s WHERE id=%s", (username, role, pw_hash, id_user))
        else:
            # Update tanpa ganti password
            cursor.execute("UPDATE users SET username=%s, role=%s WHERE id=%s", (username, role, id_user))
            
        mysql.connection.commit()
        flash('Data user diperbarui.', 'success')
    except Exception as e:
        flash(f'Gagal update user: {e}', 'danger')
        
    return redirect(url_for('kelola_users'))

@app.route('/dashboard/users/hapus/<id>', methods=['POST'])
@csrf.exempt
def hapus_user(id):
    if 'loggedin' not in session or session.get('role') != 'admin': return redirect(url_for('login'))
    
    # Cegah hapus diri sendiri (meski di UI sudah dihide)
    if int(id) == session.get('id'):
        flash('Tidak bisa menghapus akun sendiri!', 'danger')
        return redirect(url_for('kelola_users'))

    cursor = mysql.connection.cursor()
    try:
        cursor.execute("DELETE FROM users WHERE id=%s", (id,))
        mysql.connection.commit()
        flash('User dihapus.', 'success')
    except Exception as e:
        flash(f'Gagal hapus user: {e}', 'danger')
        
    return redirect(url_for('kelola_users'))

@app.route('/api/laporan', methods=['GET'])
def api_laporan():
    if 'loggedin' not in session: return {'error': 'Unauthorized'}, 401
    
    import datetime
    sekarang = datetime.date.today()
    
    bulan = request.args.get('bulan', sekarang.month)
    tahun = request.args.get('tahun', sekarang.year)
    status = request.args.get('status', '')
    
    try:
        bulan = int(bulan)
        tahun = int(tahun)
    except ValueError:
        bulan = sekarang.month
        tahun = sekarang.year

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    
    query = """
        SELECT p.id, p.tanggal_permohonan, p.no_surat, p.status,
               pend.nama_lengkap, pend.nik,
               j.nama_surat 
        FROM permohonan_surat p
        JOIN penduduk pend ON p.nik_pemohon = pend.nik
        JOIN jenis_surat j ON p.id_jenis_surat = j.id
        WHERE MONTH(p.tanggal_permohonan) = %s 
        AND YEAR(p.tanggal_permohonan) = %s
    """
    params = [bulan, tahun]
    
    if status and status != 'Semua':
        query += " AND p.status = %s"
        params.append(status)
        
    query += " ORDER BY p.tanggal_permohonan DESC"
    
    cursor.execute(query, tuple(params))
    data = cursor.fetchall()
    
    # Format date object to string for JSON
    for row in data:
        row['tanggal_permohonan'] = row['tanggal_permohonan'].strftime('%d-%m-%Y')
        
    return {'data': data}

# --- FITUR ADMIN: PENGATURAN PROFIL DESA ---
@app.route('/dashboard/pengaturan', methods=['GET', 'POST'])
def pengaturan():
    if 'loggedin' not in session: return redirect(url_for('login'))
    
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    
    if request.method == 'POST':
        nama_desa = request.form['nama_desa']
        kecamatan = request.form['kecamatan']
        kabupaten = request.form['kabupaten']
        alamat_kantor = request.form['alamat_kantor']
        nama_kades = request.form['nama_kades']
        nip_kades = request.form['nip_kades']
        provinsi = request.form['provinsi']
        kode_pos = request.form['kode_pos']
        
        # Update Data (ID 1 fix)
        cursor.execute("""
            UPDATE profil_desa 
            SET nama_desa=%s, kecamatan=%s, kabupaten=%s, alamat_kantor=%s, 
                nama_kades=%s, nip_kades=%s, provinsi=%s, kode_pos=%s
            WHERE id=1
        """, (nama_desa, kecamatan, kabupaten, alamat_kantor, nama_kades, nip_kades, provinsi, kode_pos))
        mysql.connection.commit()
        flash('Pengaturan profil desa berhasil diperbarui!', 'success')
        return redirect(url_for('pengaturan'))
    
    # Ambil Data Profil
    cursor.execute("SELECT * FROM profil_desa WHERE id=1")
    profil = cursor.fetchone()
    
    return render_template('dashboard/pengaturan.html', profil=profil)

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'loggedin' not in session: return redirect(url_for('login'))
    
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    user_id = session['id']
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form.get('password')
        password_confirm = request.form.get('password_confirm')
        
        # Validasi sederhana
        if password and password != password_confirm:
            flash('Konfirmasi password baru tidak cocok!', 'danger')
            return redirect(url_for('profile'))
            
        try:
            if password:
                # Ganti Username & Password
                pw_hash = bcrypt.generate_password_hash(password).decode('utf-8')
                cursor.execute("UPDATE users SET username=%s, password=%s WHERE id=%s", (username, pw_hash, user_id))
            else:
                # Ganti Username Saja
                cursor.execute("UPDATE users SET username=%s WHERE id=%s", (username, user_id))
                
            mysql.connection.commit()
            
            # Update session username
            session['username'] = username
            flash('Profil berhasil diperbarui!', 'success')
            
        except Exception as e:
            flash(f'Gagal update profil: {e}', 'danger')
            
        return redirect(url_for('profile'))
    
    # GET Request: Ambil data user
    cursor.execute("SELECT * FROM users WHERE id=%s", (user_id,))
    user = cursor.fetchone()
    
    return render_template('dashboard/profile.html', user=user)

@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    session.pop('role', None)
    return redirect(url_for('login'))

# --- IMPORT TO SUPPORT EXPORT FEATURE ---
import pandas as pd
import io
from xhtml2pdf import pisa
from flask import make_response, send_file

@app.route('/export/penduduk/excel')
def export_penduduk_excel():
    if session.get('role') not in ['admin', 'staff', 'pimpinan']:
        flash('Akses ditolak!', 'danger')
        return redirect(url_for('login'))
        
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    query = """
        SELECT p.nik, p.nama_lengkap, p.jenis_kelamin, p.tempat_lahir, 
               p.tanggal_lahir, p.agama, p.pekerjaan, p.status_perkawinan, 
               kk.no_kk, kk.kepala_keluarga
        FROM penduduk p
        LEFT JOIN kartu_keluarga kk ON p.no_kk = kk.no_kk
        ORDER BY p.nama_lengkap ASC
    """
    cursor.execute(query)
    result = cursor.fetchall()
    
    if not result:
        flash('Tidak ada data untuk diexport.', 'danger')
        return redirect(url_for('kelola_penduduk'))
        
    # Convert to DataFrame
    df = pd.DataFrame(result)
    
    # Rename columns for nicer Excel Output
    df.rename(columns={
        'nik': 'NIK',
        'nama_lengkap': 'Nama Lengkap',
        'jenis_kelamin': 'L/P',
        'tempat_lahir': 'Tempat Lahir',
        'tanggal_lahir': 'Tgl Lahir',
        'agama': 'Agama',
        'pekerjaan': 'Pekerjaan',
        'status_perkawinan': 'Status Kawin',
        'no_kk': 'No KK',
        'kepala_keluarga': 'Kepala Keluarga'
    }, inplace=True)
    
    # Write to BytesIO buffer
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Data Penduduk')
        
    output.seek(0)
    
    return send_file(output, download_name="Data_Penduduk_Desa_Ciawiasih.xlsx", as_attachment=True, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

@app.route('/export/penduduk/pdf')
def export_penduduk_pdf():
    if session.get('role') not in ['admin', 'staff', 'pimpinan']:
        flash('Akses ditolak!', 'danger')
        return redirect(url_for('login'))
        
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    query = """
        SELECT p.nik, p.nama_lengkap, p.jenis_kelamin, p.tempat_lahir, 
               p.tanggal_lahir, p.agama, p.pekerjaan, p.status_perkawinan, 
               kk.no_kk
        FROM penduduk p
        LEFT JOIN kartu_keluarga kk ON p.no_kk = kk.no_kk
        ORDER BY p.nama_lengkap ASC
    """
    cursor.execute(query)
    data_penduduk = cursor.fetchall()
    
    # Ambil Profil Desa untuk Kop Surat
    cursor.execute("SELECT * FROM profil_desa LIMIT 1")
    profil = cursor.fetchone()

    # Simple HTML Template for PDF
    html_content = render_template('export_penduduk_pdf.html', penduduk=data_penduduk, profil=profil, tanggal=datetime.datetime.now().strftime("%d %B %Y"))
    
    # Generate PDF
    pdf_file = io.BytesIO()
    pisa_status = pisa.CreatePDF(io.BytesIO(html_content.encode("UTF-8")), dest=pdf_file)
    
    if pisa_status.err:
        return f"Terjadi kesalahan saat membuat PDF: {pisa_status.err}"
        
    pdf_file.seek(0)
    
    response = make_response(pdf_file.read())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'inline; filename=Laporan_Penduduk.pdf'
    
    return response

@app.route('/export/surat/excel')
def export_surat_excel():
    if session.get('role') not in ['admin', 'staff', 'pimpinan']:
        flash('Akses ditolak!', 'danger')
        return redirect(url_for('login'))
        
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    query = """
        SELECT ps.tanggal_permohonan, ps.no_surat, js.nama_surat, 
               p.nama_lengkap, p.nik, ps.keperluan, ps.status
        FROM permohonan_surat ps
        JOIN jenis_surat js ON ps.id_jenis_surat = js.id
        JOIN penduduk p ON ps.nik_pemohon = p.nik
        ORDER BY ps.tanggal_permohonan DESC
    """
    cursor.execute(query)
    result = cursor.fetchall()
    
    if not result:
        flash('Tidak ada data surat untuk diexport.', 'danger')
        return redirect(url_for('kelola_permohonan'))
        
    df = pd.DataFrame(result)
    df.rename(columns={
        'tanggal_permohonan': 'Tanggal',
        'no_surat': 'Nomor Surat',
        'nama_surat': 'Jenis Surat',
        'nama_lengkap': 'Nama Pemohon',
        'nik': 'NIK',
        'keperluan': 'Keperluan',
        'status': 'Status'
    }, inplace=True)
    
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Laporan Permohonan')
        
    output.seek(0)
    
    return send_file(output, download_name="Laporan_Permohonan_Surat.xlsx", as_attachment=True, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

@app.route('/export/surat/pdf')
def export_surat_pdf():
    if session.get('role') not in ['admin', 'staff', 'pimpinan']:
        flash('Akses ditolak!', 'danger')
        return redirect(url_for('login'))
        
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    query = """
        SELECT ps.tanggal_permohonan, ps.no_surat, js.nama_surat, 
               p.nama_lengkap, ps.status
        FROM permohonan_surat ps
        JOIN jenis_surat js ON ps.id_jenis_surat = js.id
        JOIN penduduk p ON ps.nik_pemohon = p.nik
        ORDER BY ps.tanggal_permohonan DESC
    """
    cursor.execute(query)
    data_surat = cursor.fetchall()
    
    cursor.execute("SELECT * FROM profil_desa LIMIT 1")
    profil = cursor.fetchone()

    # Simple HTML Template for PDF
    html_content = render_template('export_surat_pdf.html', surat=data_surat, profil=profil, tanggal=datetime.datetime.now().strftime("%d %B %Y"))
    
    pdf_file = io.BytesIO()
    pisa_status = pisa.CreatePDF(io.BytesIO(html_content.encode("UTF-8")), dest=pdf_file)
    
    if pisa_status.err:
        return f"Terjadi kesalahan saat membuat PDF: {pisa_status.err}"
        
    pdf_file.seek(0)
    
    response = make_response(pdf_file.read())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'inline; filename=Laporan_Permohonan_Surat.pdf'
    
    return response

@app.route('/export/kinerja/pdf')
def export_kinerja_pdf():
    # Hanya Pimpinan (dan Admin/Staff opsional)
    if session.get('role') not in ['pimpinan', 'admin', 'staff']:
        flash('Akses ditolak!', 'danger')
        return redirect(url_for('login'))
        
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    
    # 1. Statistik Total
    stats = {}
    cursor.execute("SELECT COUNT(*) as total FROM penduduk")
    stats['total_warga'] = cursor.fetchone()['total']
    
    cursor.execute("SELECT COUNT(*) as total FROM kartu_keluarga")
    stats['total_kk'] = cursor.fetchone()['total']
    
    cursor.execute("SELECT COUNT(*) as total FROM permohonan_surat")
    stats['total_surat'] = cursor.fetchone()['total']
    
    # 2. Performa Surat (Disetujui vs Ditolak vs Pending)
    cursor.execute("SELECT status, COUNT(*) as jumlah FROM permohonan_surat GROUP BY status")
    status_data = cursor.fetchall()
    stats['status_breakdown'] = status_data
    
    # 3. Top 5 Jenis Surat Terlaris
    cursor.execute("""
        SELECT js.nama_surat, COUNT(ps.id) as jumlah 
        FROM permohonan_surat ps
        JOIN jenis_surat js ON ps.id_jenis_surat = js.id
        GROUP BY js.nama_surat
        ORDER BY jumlah DESC
        LIMIT 5
    """)
    stats['top_surat'] = cursor.fetchall()
    
    cursor.execute("SELECT * FROM profil_desa LIMIT 1")
    profil = cursor.fetchone()

    # Simple HTML Template for PDF
    html_content = render_template('export_kinerja_pdf.html', stats=stats, profil=profil, tanggal=datetime.datetime.now().strftime("%d %B %Y"))
    
    pdf_file = io.BytesIO()
    pisa_status = pisa.CreatePDF(io.BytesIO(html_content.encode("UTF-8")), dest=pdf_file)
    
    if pisa_status.err:
        return f"Terjadi kesalahan saat membuat PDF: {pisa_status.err}"
        
    pdf_file.seek(0)
    
    response = make_response(pdf_file.read())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'inline; filename=Laporan_Kinerja_Desa.pdf'
    
    return response

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

if __name__ == '__main__':
    app.run(debug=False, port=5000)
