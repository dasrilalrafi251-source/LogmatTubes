from flask import Flask, render_template, request, redirect, url_for, session, flash
from functools import wraps

app = Flask(__name__, template_folder='.')
app.secret_key = 'kelompok2-secret-key-2024'

# Database akun (in-memory)
ACCOUNTS = {
    'admin': {
        'username': 'admin',
        'password': 'admin123',
        'role': 'admin',
        'status': 'active',       # active | blocked
        'nama': 'Administrator',
    },
    'user1': {
        'username': 'user1',
        'password': 'user123',
        'role': 'user',
        'status': 'active',
        'nama': 'OSLO',
    },
    'user2': {
        'username': 'user2',
        'password': 'user456',
        'role': 'user',
        'status': 'active',
        'nama': 'Pria Gemoy',
    },
    'userblokir': {
        'username': 'userblokir',
        'password': 'blokir123',
        'role': 'user',
        'status': 'blocked',
        'nama': 'Joko Terblokir',
    },
}

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login'))
        if session.get('role') != 'admin':
            flash('Akses ditolak. Hanya admin yang dapat mengakses halaman ini.', 'error')
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return decorated

def count_active_admins():
    """Hitung jumlah admin yang aktif (tidak diblokir)"""
    return sum(1 for acc in ACCOUNTS.values() if acc.get('role') == 'admin' and acc.get('status') == 'active')

def check_login_failure_contrapositive(username, password):
    """
    Pembuktian Kontraposisi untuk Login:
    
    P: username valid AND password benar AND akun tidak diblokir
    Q: login berhasil
    
    Proposisi Asli: P → Q (Jika P maka Q)
    Kontraposisi: ¬Q → ¬P (Jika NOT Q maka NOT P)
    
    Jika login gagal (¬Q), maka SALAH SATU ini benar (¬P):
    1. Username tidak valid, ATAU
    2. Password salah, ATAU  
    3. Akun diblokir
    
    Fungsi ini mengembalikan tuple: (login_failed, error_message)
    """
    
    # Kondisi 1: Username tidak valid (¬username_valid)
    if username not in ACCOUNTS:
        return (True, 'Username atau kata sandi salah.')
    
    acc = ACCOUNTS[username]
    
    # Kondisi 2: Password salah (¬password_correct)
    if acc['password'] != password:
        return (True, 'Username atau kata sandi salah.')
    
    # Kondisi 3: Akun diblokir (¬account_active)
    if acc['status'] == 'blocked':
        return (True, 'Akun Anda telah diblokir. Hubungi administrator.')
    
    # Jika semua kondisi negasi SALAH, maka login BERHASIL
    # (Kontraposisi terbukti: jika tidak ada alasan gagal, maka login berhasil)
    return (False, None)

@app.route('/', methods=['GET', 'POST'])
def login():
    if 'username' in session:
        if session['role'] == 'admin':
            return redirect(url_for('admin_dashboard'))
        return redirect(url_for('home'))

    error = None
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        # Gunakan logika kontraposisi untuk verifikasi login
        login_failed, error_msg = check_login_failure_contrapositive(username, password)
        
        if login_failed:
            # Login gagal: salah satu kondisi negasi terpenuhi
            error = error_msg
        else:
            # Login berhasil: tidak ada alasan gagal (kontraposisi terbukti)
            acc = ACCOUNTS[username]
            session['username'] = username
            session['role'] = acc['role']
            session['nama'] = acc['nama']
            if acc['role'] == 'admin':
                return redirect(url_for('admin_dashboard'))
            return redirect(url_for('home'))

    return render_template('login.html', error=error)

@app.route('/home')
@login_required
def home():
    return render_template('home.html', nama=session.get('nama'))

@app.route('/admin')
@admin_required
def admin_dashboard():
    return render_template('admin.html', accounts=ACCOUNTS, nama=session.get('nama'))

@app.route('/admin/edit/<username>', methods=['GET', 'POST'])
@admin_required
def edit_account(username):
    if username not in ACCOUNTS:
        flash('Akun tidak ditemukan.', 'error')
        return redirect(url_for('admin_dashboard'))

    acc = ACCOUNTS[username]
    current_admin = session.get('username')
    
    if request.method == 'POST':
        new_username = request.form.get('new_username', '').strip()
        new_password = request.form.get('new_password', '').strip()
        new_status = request.form.get('status', '').strip()
        new_nama = request.form.get('nama', '').strip()

        # Validasi: Admin tidak bisa memblokir dirinya sendiri
        if new_status == 'blocked' and username == current_admin:
            flash('Anda tidak dapat memblokir akun Anda sendiri.', 'error')
            return render_template('edit.html', acc=acc, username=username, current_admin=current_admin)
        
        # Validasi: Admin hanya bisa memblokir admin lain jika ada minimal 2 admin lain yang aktif
        if new_status == 'blocked' and acc.get('role') == 'admin' and username != current_admin:
            active_admins = count_active_admins()
            if active_admins < 3:  # Termasuk current_admin
                flash(f'Tidak bisa memblokir admin lain. Harus ada minimal 2 admin aktif lainnya. Saat ini ada {active_admins} admin aktif.', 'error')
                return render_template('edit.html', acc=acc, username=username, current_admin=current_admin)

        if new_username and new_username != username:
            if new_username in ACCOUNTS:
                flash('Username sudah digunakan.', 'error')
                return render_template('edit.html', acc=acc, username=username, current_admin=current_admin)
            ACCOUNTS[new_username] = ACCOUNTS.pop(username)
            ACCOUNTS[new_username]['username'] = new_username
            username = new_username

        if new_password:
            ACCOUNTS[username]['password'] = new_password
        if new_status:
            ACCOUNTS[username]['status'] = new_status
        if new_nama:
            ACCOUNTS[username]['nama'] = new_nama

        flash(f'Akun "{username}" berhasil diperbarui.', 'success')
        return redirect(url_for('admin_dashboard'))

    return render_template('edit.html', acc=acc, username=username, current_admin=current_admin)

@app.route('/admin/delete/<username>', methods=['POST'])
@admin_required
def delete_account(username):
    if username not in ACCOUNTS:
        flash('Akun tidak ditemukan.', 'error')
        return redirect(url_for('admin_dashboard'))
    
    current_admin = session.get('username')
    acc = ACCOUNTS[username]
    
    # Validasi: Admin tidak bisa menghapus dirinya sendiri
    if username == current_admin:
        flash('Anda tidak dapat menghapus akun Anda sendiri.', 'error')
        return redirect(url_for('admin_dashboard'))
    
    # Validasi: Admin hanya bisa hapus admin lain jika ada minimal 2 admin lain yang aktif
    if acc.get('role') == 'admin':
        active_admins = count_active_admins()
        if active_admins < 3:  # Termasuk current_admin
            flash(f'Tidak bisa menghapus admin lain. Harus ada minimal 2 admin aktif lainnya. Saat ini ada {active_admins} admin aktif.', 'error')
            return redirect(url_for('admin_dashboard'))
    
    nama_akun = acc.get('nama')
    del ACCOUNTS[username]
    flash(f'Akun "{nama_akun}" ({username}) berhasil dihapus.', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True, port=5000)
