from functools import wraps
from flask import session, redirect, url_for, flash, request, jsonify
from extensions import db
from models.user import User
from models.whiteboard import Whiteboard

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def teacher_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        user = db.session.get(User, session['user_id'])
        if user.role != 'teacher':
            flash('只有教师可以访问此页面', 'error')
            return redirect(url_for('main.dashboard'))
        return f(*args, **kwargs)
    return decorated_function

def whiteboard_auth_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        board_id = request.headers.get('X-Board-ID')
        secret_key = request.headers.get('X-Secret-Key')
        user_token = request.headers.get('X-User-Token')
        
        # 优先使用用户token认证
        if user_token:
            user = User.query.filter_by(user_token=user_token, role='teacher', is_active=True).first()
            if not user:
                return jsonify({'error': '用户token无效'}), 401
            
            request.user = user
            # 用户token认证通过，允许访问所有白板
            return f(*args, **kwargs)
        
        if not board_id or not secret_key:
            return jsonify({'error': '需要提供白板ID和密钥或用户token'}), 401
        
        whiteboard = Whiteboard.query.filter_by(
            board_id=board_id, 
            secret_key=secret_key,
            is_active=True
        ).first()
        
        if not whiteboard:
            return jsonify({'error': '认证失败'}), 401
        
        request.whiteboard = whiteboard
        return f(*args, **kwargs)
    return decorated_function

def user_token_auth_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_token = request.headers.get('X-User-Token')
        
        if not user_token:
            return jsonify({'error': '需要提供用户token'}), 401
        
        user = User.query.filter_by(user_token=user_token, role='teacher', is_active=True).first()
        if not user:
            return jsonify({'error': '用户token无效'}), 401
        
        request.user = user
        return f(*args, **kwargs)
    return decorated_function