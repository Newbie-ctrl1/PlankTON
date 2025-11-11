from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import User
import re

bp = Blueprint('auth', __name__, url_prefix='/auth')

def validate_email(email):
    """Validasi format email"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    """Validasi password minimal 6 karakter"""
    return len(password) >= 6

def validate_username(username):
    """Validasi username minimal 3 karakter, hanya alphanumeric dan underscore"""
    if len(username) < 3:
        return False
    return re.match(r'^[a-zA-Z0-9_]+$', username) is not None

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        # Validasi input
        if not username:
            flash('Username tidak boleh kosong.', 'error')
            return redirect(url_for('auth.register'))
        
        if not validate_username(username):
            flash('Username minimal 3 karakter, hanya boleh huruf, angka, dan underscore.', 'error')
            return redirect(url_for('auth.register'))
        
        if not email:
            flash('Email tidak boleh kosong.', 'error')
            return redirect(url_for('auth.register'))
        
        if not validate_email(email):
            flash('Format email tidak valid.', 'error')
            return redirect(url_for('auth.register'))
        
        if not password:
            flash('Password tidak boleh kosong.', 'error')
            return redirect(url_for('auth.register'))
        
        if not validate_password(password):
            flash('Password minimal 6 karakter.', 'error')
            return redirect(url_for('auth.register'))
        
        if password != confirm_password:
            flash('Password dan konfirmasi tidak cocok.', 'error')
            return redirect(url_for('auth.register'))
        
        # Check username sudah terdaftar
        if User.query.filter_by(username=username).first():
            flash('Username sudah terdaftar.', 'error')
            return redirect(url_for('auth.register'))
        
        # Check email sudah terdaftar
        if User.query.filter_by(email=email).first():
            flash('Email sudah terdaftar.', 'error')
            return redirect(url_for('auth.register'))
        
        # Buat user baru
        user = User(username=username, email=email)
        user.set_password(password)
        
        try:
            db.session.add(user)
            db.session.commit()
            flash('Akun berhasil dibuat! Silakan login.', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback()
            flash('Terjadi kesalahan saat mendaftar. Silakan coba lagi.', 'error')
            return redirect(url_for('auth.register'))
    
    return render_template('register.html')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        if not username or not password:
            flash('Username dan password tidak boleh kosong.', 'error')
            return redirect(url_for('auth.login'))
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user, remember=request.form.get('remember', False))
            next_page = request.args.get('next')
            if next_page and next_page.startswith('/'):
                return redirect(next_page)
            return redirect(url_for('main.index'))
        else:
            flash('Username atau password salah.', 'error')
            return redirect(url_for('auth.login'))
    
    return render_template('login.html')

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Anda telah logout.', 'success')
    return redirect(url_for('auth.login'))

@bp.route('/profile')
@login_required
def profile():
    return render_template('profile.html', user=current_user)

@bp.route('/api/check-username', methods=['POST'])
def check_username():
    """API untuk check username availability"""
    data = request.get_json()
    username = data.get('username', '').strip()
    
    if not username:
        return jsonify({'available': False, 'message': 'Username tidak boleh kosong'})
    
    if not validate_username(username):
        return jsonify({'available': False, 'message': 'Username tidak valid'})
    
    existing = User.query.filter_by(username=username).first()
    if existing:
        return jsonify({'available': False, 'message': 'Username sudah digunakan'})
    
    return jsonify({'available': True, 'message': 'Username tersedia'})

@bp.route('/api/check-email', methods=['POST'])
def check_email():
    """API untuk check email availability"""
    data = request.get_json()
    email = data.get('email', '').strip()
    
    if not email:
        return jsonify({'available': False, 'message': 'Email tidak boleh kosong'})
    
    if not validate_email(email):
        return jsonify({'available': False, 'message': 'Format email tidak valid'})
    
    existing = User.query.filter_by(email=email).first()
    if existing:
        return jsonify({'available': False, 'message': 'Email sudah digunakan'})
    
    return jsonify({'available': True, 'message': 'Email tersedia'})
