from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user

bp = Blueprint('main', __name__)

@bp.route('/')
def landing():
    """Landing page - redirect to chat if already logged in"""
    if current_user.is_authenticated:
        return redirect(url_for('main.chat'))
    return render_template('landing.html')

@bp.route('/chat')
@login_required
def chat():
    return render_template('index.html')

@bp.route('/history')
@login_required
def history():
    return render_template('history.html')
