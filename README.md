# 🔐 LogmatTubes - Sistem Login Berbasis Logika Matematika

Platform aplikasi web untuk manajemen akun dan login yang menerapkan konsep **pembuktian kontraposisi** dari logika matematika.

## 📚 Konsep Logika Matematika

### Pembuktian Kontraposisi untuk Login

Program ini mengimplementasikan **pembuktian kontraposisi** untuk validasi login:

**Proposisi Asli:**
```
P: (username valid) AND (password benar) AND (akun tidak diblokir)
Q: login berhasil

P → Q (Jika P maka Q)
```

**Kontraposisi (Ekivalen):**
```
¬Q → ¬P (Jika NOT Q maka NOT P)

Jika login GAGAL, maka MINIMAL SATU ini benar:
1. Username TIDAK valid, ATAU
2. Password SALAH, ATAU
3. Akun DIBLOKIR
```

Dengan menerapkan kontraposisi, alih-alih memeriksa "apakah semua kondisi valid", program memeriksa "apakah ada alasan login gagal". Ini lebih efisien dan intuitif dalam praktik.

**Fungsi Implementasi:**
```python
def check_login_failure_contrapositive(username, password):
    # Cek kondisi negasi 1: username tidak valid
    if username not in ACCOUNTS:
        return (True, 'Username atau kata sandi salah.')
    
    acc = ACCOUNTS[username]
    
    # Cek kondisi negasi 2: password salah
    if acc['password'] != password:
        return (True, 'Username atau kata sandi salah.')
    
    # Cek kondisi negasi 3: akun diblokir
    if acc['status'] == 'blocked':
        return (True, 'Akun Anda telah diblokir. Hubungi administrator.')
    
    # Jika semua kondisi negasi SALAH → login BERHASIL
    return (False, None)
```

---

## ✨ Fitur Utama

### 👤 Fitur Pengguna
- ✅ Login dengan sistem kontraposisi
- ✅ Tampilan dashboard home
- ✅ Logout
- ✅ Proteksi akses halaman dengan dekorator `@login_required`

### 👨‍💼 Fitur Admin
- ✅ Dashboard manajemen akun
- ✅ Edit profil pengguna (username, password, nama)
- ✅ Blokir/unblock akun pengguna
- ✅ Hapus akun pengguna
- ✅ Validasi logika: Admin tidak bisa memblokir dirinya sendiri
- ✅ Validasi logika: Minimal 2 admin aktif harus tersedia
- ✅ Statistik akun (total, aktif, diblokir)
- ✅ Proteksi akses dengan dekorator `@admin_required`

### 🎨 Interface
- Modern dan responsif
- Dark theme dengan aksen warna
- Notifikasi error/success
- Icons dan visual feedback yang baik

---

## 📦 Persyaratan Sistem

- **Python** 3.8 atau lebih tinggi
- **Flask** 2.0 atau lebih tinggi
- Modern web browser (Chrome, Firefox, Safari, Edge)

---

## 🚀 Instalasi

### 1. Clone Repository
```bash
git clone https://github.com/yourusername/LogmatTubes.git
cd LogmatTubes
```

### 2. Buat Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install flask
```

### 4. Jalankan Aplikasi
```bash
python app.py
```

Aplikasi akan berjalan di: **http://localhost:5000**

---

## 📖 Cara Penggunaan

### Login dengan Akun Test

| Username | Password | Role | Nama | Status |
|----------|----------|------|------|--------|
| admin | admin123 | Admin | Administrator | Aktif |
| user1 | user123 | User | OSLO | Aktif |
| user2 | user456 | User | Pria Gemoy | Aktif |
| userblokir | blokir123 | User | Joko Terblokir | **Diblokir** |

### Alur Penggunaan

1. **Halaman Login** (`/`)
   - Masukkan username dan password
   - Sistem akan memvalidasi menggunakan logika kontraposisi
   - Jika valid → redirect ke dashboard sesuai role

2. **User Dashboard** (`/home`)
   - Tampilan selamat datang
   - Informasi anggota kelompok
   - Tombol logout

3. **Admin Dashboard** (`/admin`)
   - Lihat daftar semua akun
   - Statistik akun (total, aktif, diblokir)
   - Edit/hapus akun pengguna

4. **Edit Account** (`/admin/edit/<username>`)
   - Ubah username
   - Ubah password
   - Ubah nama lengkap
   - Ubah status (aktif/diblokir)
   - Validasi ketat untuk mencegah kesalahan

---

## 📁 Struktur Folder

```
LogmatTubes/
├── app.py                 # Flask main application
├── login.html            # Halaman login
├── home.html             # Halaman home user
├── admin.html            # Halaman dashboard admin
├── edit.html             # Halaman edit akun
├── static/
│   ├── login.css         # Styling halaman login
│   ├── home.css          # Styling halaman home
│   ├── admin.css         # Styling halaman admin
│   └── edit.css          # Styling halaman edit
└── README.md             # Dokumentasi ini
```

---

## 🔒 Keamanan & Validasi

### Validasi Login (Kontraposisi)
- Username harus terdaftar di database
- Password harus cocok dengan username
- Akun harus berstatus "aktif" (tidak diblokir)

### Validasi Admin
- Hanya admin yang dapat mengakses halaman admin
- Admin tidak dapat memblokir dirinya sendiri
- Admin tidak dapat menghapus dirinya sendiri
- Minimal 2 admin aktif harus selalu tersedia di sistem

### Keamanan Session
- Session dienkripsi dengan secret key
- Login required untuk halaman protected
- Admin required untuk halaman admin

---

## 🔧 Penjelasan Teknis

### Decorator untuk Proteksi
```python
@login_required  # Memastikan user sudah login
@admin_required  # Memastikan user adalah admin
```

### Database In-Memory
Akun disimpan dalam dictionary Python (bukan database eksternal):
```python
ACCOUNTS = {
    'admin': {
        'username': 'admin',
        'password': 'admin123',
        'role': 'admin',
        'status': 'active',
        'nama': 'Administrator',
    },
    # ... akun lainnya
}
```

**Catatan:** Data hilang ketika aplikasi restart. Untuk production, gunakan database sejati (PostgreSQL, MySQL, MongoDB).

### Algoritma Kontraposisi
Program menerapkan langkah-langkah berikut:
1. **Input:** username & password
2. **Cek Negasi 1:** Apakah username TIDAK ada? → Gagal
3. **Cek Negasi 2:** Apakah password SALAH? → Gagal
4. **Cek Negasi 3:** Apakah akun DIBLOKIR? → Gagal
5. **Output:** Jika semua negasi SALAH → Login BERHASIL ✅

---

## 👥 Anggota Kelompok

| NIM | Nama |
|-----|------|
| 2510511088 | Dasril Al Rafi |
| 2510511105 | Iqbal Rizki Pratama Indra Basuki |
| 2510511100 | Pasha Romansyah |
| 2510511102 | Rayyan Muhammad Firdaus |
| 2510511073 | Samuel Christian Alexander |
| 2510511096 | Stefen Shelinten |

---

## 📝 Catatan Pengembangan

### Fitur Potensial di Masa Depan
- [ ] Database persistence (SQLite/PostgreSQL)
- [ ] Password hashing (bcrypt)
- [ ] Email verification
- [ ] Password reset
- [ ] Two-factor authentication
- [ ] Audit logging
- [ ] Role-based access control (RBAC) lebih advanced

### Batasan Saat Ini
- Data hilang saat restart aplikasi
- Password disimpan plain-text (bukan best practice)
- Tidak ada rate limiting untuk login attempts
- Interface hanya untuk web (bukan mobile app)

---