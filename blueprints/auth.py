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

@auth_bp.route('/auth/casdoor/developer')
def casdoor_login_developer():
    auth_url = get_casdoor_auth_url('developer')
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
    
    # 查找用户，优先通过casdoor_id，其次通过username+organization
    user = User.query.filter_by(casdoor_id=casdoor_id).first()
    
    if not user:
        # 检查相同用户名但不同组织的用户
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            # 用户名冲突，生成新的用户名
            base_username = username
            counter = 1
            while User.query.filter_by(username=username).first():
                username = f"{base_username}_{counter}"
                counter += 1
            flash(f'检测到用户名冲突，您的用户名已自动调整为: {username}', 'info')
        
        user = User(
            casdoor_id=casdoor_id,
            username=username,
            email=email,
            avatar=avatar,
            display_name=display_name,
            role=role,
            organization=role  # 使用角色作为组织标识
        )
        db.session.add(user)
        db.session.commit()
        
        role_display = {
            'student': '学生',
            'teacher': '教师', 
            'developer': '开发者'
        }.get(role, '用户')
        
        flash(f'账户创建成功！欢迎{role_display}使用班级管理系统。', 'success')
    else:
        # 更新用户信息
        user.email = email
        user.avatar = avatar
        user.display_name = display_name
        user.last_login = get_china_time()
        
        # 如果组织发生变化，更新组织信息
        if user.organization != role:
            old_org = user.organization
            user.organization = role
            user.role = role  # 同时更新角色
            
            org_display = {
                'student': '学生',
                'teacher': '教师',
                'developer': '开发者'
            }
            flash(f'您的身份已从{org_display.get(old_org, old_org)}变更为{org_display.get(role, role)}。', 'info')
        
        db.session.commit()
    
    session['user_id'] = user.id
    session['username'] = user.username
    session['email'] = user.email
    session['avatar'] = user.avatar
    session['role'] = user.role
    session['organization'] = user.organization
    
    session.pop('oauth_state', None)
    session.pop('login_role', None)
    
    return redirect(url_for('main.dashboard'))

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('您已成功退出系统。', 'success')
    return redirect(url_for('main.index'))