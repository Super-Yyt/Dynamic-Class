from flask import Blueprint, request, jsonify, session
from extensions import db, socketio
from models.user import User
from models.whiteboard import Whiteboard
from models.assignment import Assignment
from models.class_models import TeacherClass, ClassSubject
from utils.auth_utils import login_required, teacher_required
from utils.time_utils import parse_china_time, format_china_time, get_china_time
from datetime import timedelta

assignments_bp = Blueprint('assignments', __name__)

@assignments_bp.route('/whiteboards/<int:whiteboard_id>/create_assignment', methods=['POST'])
@login_required
@teacher_required
def create_assignment(whiteboard_id):
    whiteboard = Whiteboard.query.get_or_404(whiteboard_id)
    user = db.session.get(User, session['user_id'])
    
    # 检查权限：班主任或授课老师
    is_class_teacher = (whiteboard.class_obj.teacher_id == user.id)
    is_teaching_teacher = False
    assigned_subjects = []
    
    if is_class_teacher:
        class_subjects = ClassSubject.query.filter_by(class_id=whiteboard.class_id).all()
        assigned_subjects = [subject.subject_name for subject in class_subjects]
    else:
        teacher_class = TeacherClass.query.filter_by(
            class_id=whiteboard.class_id, 
            teacher_id=user.id,
            is_approved=True
        ).first()
        
        if teacher_class and teacher_class.assigned_subjects:
            is_teaching_teacher = True
            assigned_subjects = teacher_class.get_assigned_subjects_list()
    
    if not is_class_teacher and not is_teaching_teacher:
        return jsonify({'error': '无权限发布作业'}), 403
    
    data = request.get_json()
    assignment_id = data.get('id')
    title = data.get('title')
    description = data.get('description')
    subject = data.get('subject')
    due_date_str = data.get('due_date')
    
    if not all([title, description, subject, due_date_str]):
        return jsonify({'error': '所有字段都必须填写'}), 400
    
    # 检查学科权限
    if subject not in assigned_subjects:
        return jsonify({'error': f'您没有权限发布{subject}学科的作业'}), 403
    
    try:
        due_date = parse_china_time(due_date_str)
    except ValueError:
        return jsonify({'error': '日期格式无效'}), 400
    
    try:
        today = get_china_time().replace(tzinfo=None)
        start_of_day = today.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = start_of_day + timedelta(days=1)
        
        existing_assignment = Assignment.query.filter(
            Assignment.whiteboard_id == whiteboard_id,
            Assignment.subject == subject,
            Assignment.created_at >= start_of_day,
            Assignment.created_at < end_of_day
        ).first()
        
        if existing_assignment:
            # 检查更新权限：班主任或作业发布者
            if existing_assignment.teacher_id != user.id and not is_class_teacher:
                return jsonify({'error': '无权限更新此作业'}), 403
                
            existing_assignment.title = title
            existing_assignment.description = description
            existing_assignment.due_date = due_date
            existing_assignment.updated_at = get_china_time().replace(tzinfo=None)
            db.session.commit()
            
            socketio.emit('update_assignment', {
                'id': existing_assignment.id,
                'title': existing_assignment.title,
                'description': existing_assignment.description,
                'subject': existing_assignment.subject,
                'due_date': format_china_time(existing_assignment.due_date),
                'updated_at': format_china_time(existing_assignment.updated_at),
                'teacher_name': existing_assignment.teacher.username
            }, room=f"whiteboard_{whiteboard_id}")
            
            return jsonify({'success': True, 'assignment_id': existing_assignment.id, 'is_update': True})
        else:
            assignment = Assignment(
                title=title,
                description=description,
                subject=subject,
                due_date=due_date,
                whiteboard_id=whiteboard_id,
                teacher_id=user.id
            )
            db.session.add(assignment)
            db.session.commit()
            
            socketio.emit('new_assignment', {
                'id': assignment.id,
                'title': assignment.title,
                'description': assignment.description,
                'subject': assignment.subject,
                'due_date': format_china_time(assignment.due_date),
                'created_at': format_china_time(assignment.created_at),
                'teacher_name': assignment.teacher.username
            }, room=f"whiteboard_{whiteboard_id}")
            
            return jsonify({'success': True, 'assignment_id': assignment.id})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': '操作失败'}), 500

@assignments_bp.route('/whiteboards/<int:whiteboard_id>/check_assignment', methods=['GET'])
@login_required
@teacher_required
def check_assignment(whiteboard_id):
    whiteboard = Whiteboard.query.get_or_404(whiteboard_id)
    user = db.session.get(User, session['user_id'])
    
    # 检查权限：班主任或授课老师
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
        return jsonify({'error': '无权限'}), 403
    
    subject = request.args.get('subject')
    
    if not subject:
        return jsonify({'error': '缺少科目参数'}), 400
    
    # 如果是授课老师，检查是否有该学科的权限
    if is_teaching_teacher and subject not in assigned_subjects:
        return jsonify({'error': f'您没有权限查看{subject}学科的作业'}), 403
    
    assignment = Assignment.query.filter_by(
        whiteboard_id=whiteboard_id,
        subject=subject
    ).order_by(Assignment.created_at.desc()).first()
    
    if assignment:
        return jsonify({
            'assignment': {
                'id': assignment.id,
                'title': assignment.title,
                'description': assignment.description,
                'subject': assignment.subject,
                'due_date': format_china_time(assignment.due_date)
            }
        })
    return jsonify({})

@assignments_bp.route('/assignments/<int:assignment_id>/delete', methods=['POST'])
@login_required
@teacher_required
def delete_assignment(assignment_id):
    assignment = Assignment.query.get_or_404(assignment_id)
    user = db.session.get(User, session['user_id'])
    
    # 检查权限：班主任或作业发布者
    if user.role != 'teacher' or (assignment.whiteboard.class_obj.teacher_id != user.id and assignment.teacher_id != user.id):
        return jsonify({'error': '无权限'}), 403
    
    try:
        whiteboard_id = assignment.whiteboard_id
        db.session.delete(assignment)
        db.session.commit()
        socketio.emit('delete_assignment', {'assignment_id': assignment_id}, room=f"whiteboard_{whiteboard_id}")
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': '删除作业失败'}), 500

@assignments_bp.route('/whiteboards/<int:whiteboard_id>/assignments')
@login_required
def get_whiteboard_assignments_list(whiteboard_id):
    whiteboard = Whiteboard.query.get_or_404(whiteboard_id)
    user = db.session.get(User, session['user_id'])
    
    # 检查权限：班主任或授课老师
    is_class_teacher = (whiteboard.class_obj.teacher_id == user.id)
    is_teaching_teacher = False
    if not is_class_teacher:
        teacher_class = TeacherClass.query.filter_by(
            class_id=whiteboard.class_id, 
            teacher_id=user.id,
            is_approved=True
        ).first()
        if teacher_class and teacher_class.assigned_subjects:
            is_teaching_teacher = True
    
    if not is_class_teacher and not is_teaching_teacher:
        return jsonify({'error': '无权限'}), 403
    
    try:
        assignments = Assignment.query.filter_by(whiteboard_id=whiteboard_id).order_by(Assignment.created_at.desc()).all()
        
        assignments_data = []
        for assignment in assignments:
            # 计算删除权限：班主任或作业发布者
            can_delete = is_class_teacher or assignment.teacher_id == user.id
            
            assignments_data.append({
                'id': assignment.id,
                'title': assignment.title,
                'description': assignment.description,
                'subject': assignment.subject,
                'due_date': format_china_time(assignment.due_date),
                'created_at': format_china_time(assignment.created_at),
                'teacher_name': assignment.teacher.username,
                'teacher_id': assignment.teacher_id,
                'can_delete': can_delete  # 添加删除权限字段
            })
        
        return jsonify({'success': True, 'assignments': assignments_data})
    except Exception as e:
        return jsonify({'error': '获取作业列表失败'}), 500