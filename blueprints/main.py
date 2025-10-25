from flask import Blueprint, send_from_directory, render_template, redirect, url_for, abort, session
from extensions import db, socketio
from models.user import User
from models.class_models import Class, TeacherClass
from utils.auth_utils import login_required, teacher_required
from utils.time_utils import format_china_time
import os

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

@main_bp.route('/uploads/<int:class_id>/<path:filename>')
@login_required
def serve_uploaded_file(class_id, filename):
    """提供上传文件的访问，需要班级权限验证"""
    user = db.session.get(User, session['user_id'])
    
    # 检查用户是否有权限访问该班级的文件
    has_permission = False
    
    if user.role == 'teacher':
        # 教师：检查是否是班主任或授课教师
        class_obj = Class.query.get(class_id)
        if class_obj:
            # 班主任
            if class_obj.teacher_id == user.id:
                has_permission = True
            else:
                # 授课教师
                teacher_class = TeacherClass.query.filter_by(
                    class_id=class_id, 
                    teacher_id=user.id,
                    is_approved=True
                ).first()
                if teacher_class:
                    has_permission = True
    
    # TODO: 未来添加学生权限检查
    # elif user.role == 'student':
    #     # 学生：检查是否是该班级的学生
    #     student_class = StudentClass.query.filter_by(
    #         class_id=class_id,
    #         student_id=user.id
    #     ).first()
    #     if student_class:
    #         has_permission = True
    
    if not has_permission:
        abort(403, description="您没有权限访问该班级的文件")
    
    # 构建完整的文件路径
    uploads_dir = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), 
        'uploads', 
        str(class_id)
    )
    
    file_path = os.path.join(uploads_dir, filename)
    
    # 安全检查：确保请求的文件在uploads目录内
    uploads_dir_abs = os.path.abspath(uploads_dir)
    file_path_abs = os.path.abspath(file_path)
    
    if not file_path_abs.startswith(uploads_dir_abs):
        abort(403, description="无效的文件路径")
    
    if not os.path.isfile(file_path_abs):
        abort(404, description="文件不存在")
    
    return send_from_directory(uploads_dir, filename)

@main_bp.route('/favicon.ico')
def favicon():
    return '', 204