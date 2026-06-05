from flask import Flask, render_template, request, redirect, url_for, session, flash
from datetime import datetime, date
from functools import wraps

app = Flask(__name__, template_folder='.')
app.secret_key = 'kelompok2-secret-key-2024'

# Database akun (in-memory)
ACCOUNTS = {
    'admin': {
        'username': 'admin',
        'password': 'admin123',
        'role': 'admin',
        'status': 'active',       # active | blocked | expired
        'nama': 'Administrator',
        'expired_date': None,
    },
    'user1': {
        'username': 'user1',
        'password': 'user123',
        'role': 'user',
        'status': 'active',
        'nama': 'Pria SOLO',
        'expired_date': None,
    },
    'user2': {
        'username': 'user2',
        'password': 'user456',
        'role': 'user',
        'status': 'active',
        'nama': 'Pria Antek Antek Asing',
        'expired_date': None,
    },
    'userblokir': {
        'username': 'userblokir',
        'password': 'blokir123',
        'role': 'user',
        'status': 'blocked',
        'nama': 'Joko Terblokir',
        'expired_date': None,
    },
    'userkadaluarsa': {
        'username': 'userkadaluarsa',
        'password': 'expired123',
        'role': 'user',
        'status': 'expired',
        'nama': 'Udin Kadaluarsa',
        'expired_date': '2023-01-01',
    },
}

def update_expiry_for_account(acc):
    """Periksa `expired_date` pada akun dan:
    - jika `expired_date` < hari ini -> set `status = 'expired'` (kecuali akun diblokir)
    - jika `expired_date` >= hari ini dan status saat ini 'expired' -> set `status = 'active'`
    """
    exp = acc.get('expired_date')
    if not exp:
        return
    try:
        exp_date = datetime.strptime(exp, '%Y-%m-%d').date()
    except Exception:
        return
    today = date.today()
    if exp_date < today:
        # jangan ubah status jika akun diblokir secara manual
        if acc.get('status') != 'blocked':
            acc['status'] = 'expired'
    else:
        # expired_date >= today -> jika sebelumnya 'expired', aktifkan kembali
        if acc.get('status') == 'expired':
            acc['status'] = 'active'


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

        if username in ACCOUNTS:
            acc = ACCOUNTS[username]
            # update status jika sudah melewati tanggal kadaluarsa
            update_expiry_for_account(acc)
            if acc['password'] == password:
                if acc['status'] == 'blocked':
                    error = 'Akun Anda telah diblokir. Hubungi administrator.'
                elif acc['status'] == 'expired':
                    error = 'Akun Anda telah kadaluarsa. Hubungi administrator.'
                else:
                    session['username'] = username
                    session['role'] = acc['role']
                    session['nama'] = acc['nama']
                    if acc['role'] == 'admin':
                        return redirect(url_for('admin_dashboard'))
                    return redirect(url_for('home'))
            else:
                error = 'Username atau kata sandi salah.'
        else:
            error = 'Username atau kata sandi salah.'

    return render_template('login.html', error=error)

@app.route('/home')
@login_required
def home():
    return render_template('home.html', nama=session.get('nama'))

@app.route('/admin')
@admin_required
def admin_dashboard():
    # pastikan semua akun yang memiliki expired_date diperbarui sebelum ditampilkan
    for a in ACCOUNTS.values():
        update_expiry_for_account(a)
    return render_template('admin.html', accounts=ACCOUNTS, nama=session.get('nama'))

@app.route('/admin/edit/<username>', methods=['GET', 'POST'])
@admin_required
def edit_account(username):
    if username not in ACCOUNTS:
        flash('Akun tidak ditemukan.', 'error')
        return redirect(url_for('admin_dashboard'))

    acc = ACCOUNTS[username]
    if request.method == 'POST':
        new_username = request.form.get('new_username', '').strip()
        new_password = request.form.get('new_password', '').strip()
        new_status = request.form.get('status', '').strip()
        new_nama = request.form.get('nama', '').strip()
        new_expired = request.form.get('expired_date', '').strip()

        if new_username and new_username != username:
            if new_username in ACCOUNTS:
                flash('Username sudah digunakan.', 'error')
                return render_template('edit.html', acc=acc, username=username)
            ACCOUNTS[new_username] = ACCOUNTS.pop(username)
            ACCOUNTS[new_username]['username'] = new_username
            username = new_username

        if new_password:
            ACCOUNTS[username]['password'] = new_password
        if new_status:
            ACCOUNTS[username]['status'] = new_status
        if new_nama:
            ACCOUNTS[username]['nama'] = new_nama
        ACCOUNTS[username]['expired_date'] = new_expired if new_expired else None

        flash(f'Akun "{username}" berhasil diperbarui.', 'success')
        return redirect(url_for('admin_dashboard'))

    return render_template('edit.html', acc=acc, username=username)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True, port=5000)
