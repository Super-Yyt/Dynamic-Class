from flask import Blueprint, render_template, redirect, url_for, session, request, flash, jsonify
from datetime import timedelta
from extensions import db, socketio
from models.user import User
from models.class_models import Class, TeacherClass, ClassSubject
from models.whiteboard import Whiteboard
from models.task import Task
from models.assignment import Assignment
from models.announcement import Announcement
from utils.auth_utils import login_required, teacher_required
from utils.code_utils import generate_whiteboard_credentials
from utils.time_utils import get_china_time, format_china_time, parse_china_time

whiteboards_bp = Blueprint('whiteboards', __name__, url_prefix='/whiteboards')

@whiteboards_bp.route('/<int:whiteboard_id>', methods=['GET', 'POST'])
@login_required
def view_whiteboard(whiteboard_id):
    whiteboard = Whiteboard.query.get_or_404(whiteboard_id)
    user = db.session.get(User, session['user_id'])
    
    is_class_teacher = (whiteboard.class_obj.teacher_id == user.id)
    is_teaching_teacher = False
    assigned_subjects = []
    
    if not is_class_teacher:
        teacher_class = TeacherClass.query.filter_by(
            class_id=whiteboard.class_id, 
            teacher_id=user.id,
            is_approved=True
        ).first()
        
        if teacher_class and teacher_class.assigned_subjects:
            is_teaching_teacher = True
            assigned_subjects = teacher_class.get_assigned_subjects_list()
    
    if not is_class_teacher and not is_teaching_teacher:
        flash('您没有权限查看此白板', 'error')
        return redirect(url_for('classes.classes'))
    
    class_subjects = ClassSubject.query.filter_by(class_id=whiteboard.class_id).all()
    class_subjects_list = [subject.subject_name for subject in class_subjects]
    
#    if request.method == 'POST' and 'subjects' in request.form:
#        if not is_class_teacher:
#            flash('只有班主任可以设置白板科目', 'error')
#            return redirect(url_for('whiteboards.view_whiteboard', whiteboard_id=whiteboard_id))
#        
#        subjects = request.form.get('subjects')
#        whiteboard.subjects = subjects
#        db.session.commit()
#        flash('科目设置已更新', 'success')
#        return redirect(url_for('whiteboards.view_whiteboard', whiteboard_id=whiteboard_id))
    if whiteboard.token is None:
        has_token = False
        token_value = None
    else:
        has_token = True
        token_value = whiteboard.token

    # 只在有token时生成完整URL
    if has_token:
        whiteboard_url = f"dlass://config/{whiteboard.id}/{whiteboard.board_id}?temp_secret={whiteboard.secret_key}/{token_value}"
    else:
        whiteboard_url = None
    
    tasks = Task.query.filter_by(whiteboard_id=whiteboard_id).order_by(Task.created_at.desc()).all()
    announcements = Announcement.query.filter_by(whiteboard_id=whiteboard_id).order_by(Announcement.created_at.desc()).all()
    assignments = Assignment.query.filter_by(whiteboard_id=whiteboard_id).order_by(Assignment.created_at.desc()).all()
    
    for task in tasks:
        task.created_at_str = format_china_time(task.created_at)
        if task.due_date:
            task.due_date_str = format_china_time(task.due_date)
        else:
            task.due_date_str = None
            
    for announcement in announcements:
        announcement.created_at_str = format_china_time(announcement.created_at)
        
    for assignment in assignments:
        assignment.created_at_str = format_china_time(assignment.created_at)
        assignment.due_date_str = format_china_time(assignment.due_date)
    
    whiteboard.created_at_str = format_china_time(whiteboard.created_at)
    print("白板token：", whiteboard.token)
    return render_template('view_whiteboard.html', 
                         username=session.get('username'),
                         role=session.get('role'),
                         avatar=session.get('avatar'),
                         whiteboard=whiteboard,
                         whiteboard_url=whiteboard_url,
                         has_token=has_token,
                         tasks=tasks,
                         announcements=announcements,
                         assignments=assignments,
                         now=get_china_time().replace(tzinfo=None),
                         is_class_teacher=is_class_teacher,
                         is_teaching_teacher=is_teaching_teacher,
                         assigned_subjects=assigned_subjects,
                         class_subjects_list=class_subjects_list)

@whiteboards_bp.route('/<int:whiteboard_id>/token')
@login_required
@teacher_required  
def get_whiteboard_token(whiteboard_id):
    """获取白板token（教师权限）"""
    whiteboard = Whiteboard.query.get_or_404(whiteboard_id)
    user = db.session.get(User, session['user_id'])
    
    # 验证教师权限
    if not (whiteboard.class_obj.teacher_id == user.id):
        flash('只有班主任可以查看token', 'error')
        return redirect(url_for('whiteboards.view_whiteboard', whiteboard_id=whiteboard_id))
    
    # 如果还没有token，生成一个
    if not whiteboard.token:
        whiteboard.generate_token()
        db.session.commit()
    
    return redirect(url_for('whiteboards.view_whiteboard', whiteboard_id=whiteboard_id))

@whiteboards_bp.route('/<int:whiteboard_id>/reset-token', methods=['POST'])
@login_required
@teacher_required
def reset_whiteboard_token(whiteboard_id):
    """重置白板token"""
    whiteboard = Whiteboard.query.get_or_404(whiteboard_id)
    user = db.session.get(User, session['user_id'])
    
    if not (whiteboard.class_obj.teacher_id == user.id):
        flash('只有班主任可以重置token', 'error')
        return redirect(url_for('whiteboards.view_whiteboard', whiteboard_id=whiteboard_id))
    
    whiteboard.generate_token()
    db.session.commit()
    
    flash('Token已重置成功', 'success')
    return redirect(url_for('whiteboards.get_whiteboard_token', whiteboard_id=whiteboard_id))

@whiteboards_bp.route('/classes/<int:class_id>/create', methods=['GET', 'POST'])
@login_required
@teacher_required
def create_whiteboard(class_id):
    class_obj = Class.query.get_or_404(class_id)
    user = db.session.get(User, session['user_id'])
    
    if user.role != 'teacher' or class_obj.teacher_id != user.id:
        flash('您没有权限执行此操作', 'error')
        return redirect(url_for('classes.view_class', class_id=class_id))
    
    if request.method == 'POST':
        name = request.form.get('name')
        
        if not name:
            flash('白板名称不能为空', 'error')
            return render_template('create_whiteboard.html', class_obj=class_obj)
        
        board_id, secret_key = generate_whiteboard_credentials()
        
        whiteboard = Whiteboard(
            name=name,
            board_id=board_id,
            secret_key=secret_key,
            class_id=class_id
        )
        
        try:
            db.session.add(whiteboard)
            db.session.commit()
            flash(f'白板 "{name}" 创建成功！', 'success')
            return redirect(url_for('whiteboards.view_whiteboard', whiteboard_id=whiteboard.id))
        except Exception as e:
            db.session.rollback()
            flash('创建白板时发生错误', 'error')
            return render_template('create_whiteboard.html', class_obj=class_obj)
    
    return render_template('create_whiteboard.html', 
                         username=session.get('username'),
                         role=session.get('role'),
                         avatar=session.get('avatar'),
                         class_obj=class_obj)

@whiteboards_bp.route('/<int:whiteboard_id>/status')
@login_required
def get_whiteboard_status(whiteboard_id):
    whiteboard = Whiteboard.query.get_or_404(whiteboard_id)
    user = db.session.get(User, session['user_id'])
    
    if user.role != 'teacher' or whiteboard.class_obj.teacher_id != user.id:
        return jsonify({'error': '无权限'}), 403
    
    is_actually_online = False
    if whiteboard.last_heartbeat:
        time_diff = (get_china_time().replace(tzinfo=None) - whiteboard.last_heartbeat).total_seconds()
        is_actually_online = time_diff < 30
    
    if whiteboard.is_online != is_actually_online:
        whiteboard.is_online = is_actually_online
        db.session.commit()
    
    return jsonify({
        'success': True,
        'is_online': whiteboard.is_online,
        'last_heartbeat': format_china_time(whiteboard.last_heartbeat) if whiteboard.last_heartbeat else None
    })

@whiteboards_bp.route('/<int:whiteboard_id>/history')
@login_required
def get_history(whiteboard_id):
    whiteboard = Whiteboard.query.get_or_404(whiteboard_id)
    user = db.session.get(User, session['user_id'])
    
    if user.role != 'teacher' or whiteboard.class_obj.teacher_id != user.id:
        return jsonify({'error': '无权限'}), 403
    
    date_str = request.args.get('date')
    if not date_str:
        return jsonify({'error': '需要日期参数'}), 400
    
    try:
        target_date = parse_china_time(date_str + ' 00:00:00')
        next_date = target_date + timedelta(days=1)
    except ValueError:
        return jsonify({'error': '日期格式无效'}), 400
    
    tasks = Task.query.filter(
        Task.whiteboard_id == whiteboard_id,
        Task.created_at >= target_date,
        Task.created_at < next_date
    ).all()
    
    announcements = Announcement.query.filter(
        Announcement.whiteboard_id == whiteboard_id,
        Announcement.created_at >= target_date,
        Announcement.created_at < next_date
    ).all()
    
    assignments = Assignment.query.filter(
        Assignment.whiteboard_id == whiteboard_id,
        Assignment.created_at >= target_date,
        Assignment.created_at < next_date
    ).all()
    
    history = []
    for task in tasks:
        history.append({
            'type': '任务',
            'title': task.title,
            'description': task.description,
            'created_at': format_china_time(task.created_at)
        })
    
    for announcement in announcements:
        history.append({
            'type': '公告',
            'title': announcement.title,
            'description': announcement.content[:100] + '...' if len(announcement.content) > 100 else announcement.content,
            'created_at': format_china_time(announcement.created_at)
        })
    
    for assignment in assignments:
        history.append({
            'type': '作业',
            'title': assignment.title,
            'description': f"{assignment.subject}: {assignment.description[:100]}{'...' if len(assignment.description) > 100 else ''}",
            'created_at': format_china_time(assignment.created_at)
        })
    
    history.sort(key=lambda x: x['created_at'], reverse=True)
    
    return jsonify({'success': True, 'data': history})