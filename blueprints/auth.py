from flask import Blueprint, render_template, redirect, url_for, session, request, flash
from extensions import db, socketio
from models.user import User
from utils.casdoor_utils import get_casdoor_auth_url, get_access_token, get_user_info
from utils.time_utils import get_china_time

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login')
def login():
    if 'user_id' in session:
        return redirect(url_for('main.dashboard'))
    return render_template('login.html')

@auth_bp.route('/auth/casdoor/student')
def casdoor_login_student():
    auth_url = get_casdoor_auth_url('student')
    return redirect(auth_url)

@auth_bp.route('/auth/casdoor/teacher')
def casdoor_login_teacher():
    auth_url = get_casdoor_auth_url('teacher')
    return redirect(auth_url)

@auth_bp.route('/callback')
def callback():
    code = request.args.get('code')
    if not code:
        flash('认证失败：未收到授权码', 'error')
        return redirect(url_for('auth.login'))
    
    state = request.args.get('state')
    if not state or state != session.get('oauth_state'):
        flash('认证失败：无效的state参数', 'error')
        return redirect(url_for('auth.login'))
    
    role = session.get('login_role', 'student')
    access_token = get_access_token(code, role)
    if not access_token:
        flash('认证失败：无法获取访问令牌', 'error')
        return redirect(url_for('auth.login'))
    
    user_info = get_user_info(access_token)
    if not user_info:
        flash('认证失败：无法获取用户信息', 'error')
        return redirect(url_for('auth.login'))
    
    casdoor_id = user_info.get('sub')
    username = user_info.get('preferred_username', user_info.get('name'))
    email = user_info.get('email')
    avatar = user_info.get('picture')
    display_name = user_info.get('name', username)
    
    user = User.query.filter_by(casdoor_id=casdoor_id).first()
    if not user:
        user = User(
            casdoor_id=casdoor_id,
            username=username,
            email=email,
            avatar=avatar,
            display_name=display_name,
            role=role
        )
        db.session.add(user)
        db.session.commit()
        flash(f'账户创建成功！欢迎{"教师" if role == "teacher" else "学生"}使用班级管理系统。', 'success')
    else:
        user.email = email
        user.avatar = avatar
        user.display_name = display_name
        user.last_login = get_china_time()
        if user.role != role:
            user.role = role
            flash(f'您的角色已更新为{"教师" if role == "teacher" else "学生"}。', 'info')
        db.session.commit()
    
    session['user_id'] = user.id
    session['username'] = user.username
    session['email'] = user.email
    session['avatar'] = user.avatar
    session['role'] = user.role
    
    session.pop('oauth_state', None)
    session.pop('login_role', None)
    
    return redirect(url_for('main.dashboard'))

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('您已成功退出系统。', 'success')
    return redirect(url_for('main.index'))