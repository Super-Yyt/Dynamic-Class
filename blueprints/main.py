from flask import Blueprint, render_template, redirect, url_for, session
from extensions import db, socketio
from models.user import User
from utils.time_utils import format_china_time

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('main.dashboard'))
    return render_template('index.html')

@main_bp.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    user = db.session.get(User, session['user_id'])
    last_login_str = format_china_time(user.last_login) if user.last_login else '首次登录'
    
    return render_template('dashboard.html', 
                         username=session.get('username'),
                         role=session.get('role'),
                         avatar=session.get('avatar'),
                         last_login=last_login_str)

@main_bp.route('/favicon.ico')
def favicon():
    return '', 204