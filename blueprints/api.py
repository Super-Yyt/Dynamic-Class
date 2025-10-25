from flask import Blueprint, request, jsonify
from datetime import timedelta
from extensions import db, socketio
from models.whiteboard import Whiteboard, WhiteboardStatusHistory
from models.task import Task
from models.assignment import Assignment
from models.announcement import Announcement
from utils.auth_utils import whiteboard_auth_required
from utils.time_utils import parse_china_time, format_china_time, get_china_time

api_bp = Blueprint('api', __name__, url_prefix='/api/whiteboard')

@api_bp.route('/assignments', methods=['GET'])
@whiteboard_auth_required
def get_whiteboard_assignments():
    date_str = request.args.get('date')
    subject = request.args.get('subject')
    
    query = Assignment.query.filter_by(whiteboard_id=request.whiteboard.id)
    
    if date_str:
        try:
            target_date = parse_china_time(date_str + ' 00:00:00')
            next_date = target_date + timedelta(days=1)
            
            query = query.filter(
                Assignment.due_date >= target_date,
                Assignment.due_date < next_date
            )
        except ValueError:
            return jsonify({'error': '日期格式无效，请使用YYYY-MM-DD格式'}), 400
    
    if subject:
        query = query.filter(Assignment.subject == subject)
    
    assignments = query.order_by(Assignment.created_at.desc()).all()
    
    assignments_data = []
    for assignment in assignments:
        assignments_data.append({
            'id': assignment.id,
            'title': assignment.title,
            'description': assignment.description,
            'subject': assignment.subject,
            'due_date': format_china_time(assignment.due_date),
            'created_at': format_china_time(assignment.created_at)
        })
    
    return jsonify({
        'success': True,
        'data': assignments_data,
        'count': len(assignments_data)
    })

@api_bp.route('/tasks', methods=['GET'])
@whiteboard_auth_required
def get_whiteboard_tasks():
    date_str = request.args.get('date')
    priority = request.args.get('priority')
    status = request.args.get('status')
    
    query = Task.query.filter_by(whiteboard_id=request.whiteboard.id)
    
    if date_str:
        try:
            target_date = parse_china_time(date_str + ' 00:00:00')
            next_date = target_date + timedelta(days=1)
            
            query = query.filter(
                Task.created_at >= target_date,
                Task.created_at < next_date
            )
        except ValueError:
            return jsonify({'error': '日期格式无效，请使用YYYY-MM-DD格式'}), 400
    
    if priority and priority.isdigit():
        query = query.filter(Task.priority == int(priority))
    
    if status == 'pending':
        query = query.filter(Task.is_completed == False)
    elif status == 'completed':
        query = query.filter(Task.is_completed == True)
    
    tasks = query.order_by(Task.created_at.desc()).all()
    
    tasks_data = []
    for task in tasks:
        tasks_data.append({
            'id': task.id,
            'title': task.title,
            'description': task.description,
            'priority': task.priority,
            'action_id': task.action_id,
            'due_date': format_china_time(task.due_date) if task.due_date else None,
            'is_acknowledged': task.is_acknowledged,
            'is_completed': task.is_completed,
            'created_at': format_china_time(task.created_at)
        })
    
    return jsonify({
        'success': True,
        'data': tasks_data,
        'count': len(tasks_data)
    })

@api_bp.route('/announcements', methods=['GET'])
@whiteboard_auth_required
def get_whiteboard_announcements():
    date_str = request.args.get('date')
    long_term = request.args.get('long_term')
    
    query = Announcement.query.filter_by(whiteboard_id=request.whiteboard.id)
    
    if date_str:
        try:
            target_date = parse_china_time(date_str + ' 00:00:00')
            next_date = target_date + timedelta(days=1)
            
            query = query.filter(
                Announcement.created_at >= target_date,
                Announcement.created_at < next_date
            )
        except ValueError:
            return jsonify({'error': '日期格式无效，请使用YYYY-MM-DD格式'}), 400
    
    if long_term is not None:
        if long_term.lower() == 'true':
            query = query.filter(Announcement.is_long_term == True)
        elif long_term.lower() == 'false':
            query = query.filter(Announcement.is_long_term == False)
    
    announcements = query.order_by(Announcement.created_at.desc()).all()
    
    announcements_data = []
    for announcement in announcements:
        announcements_data.append({
            'id': announcement.id,
            'title': announcement.title,
            'content': announcement.content,
            'is_long_term': announcement.is_long_term,
            'created_at': format_china_time(announcement.created_at)
        })
    
    return jsonify({
        'success': True,
        'data': announcements_data,
        'count': len(announcements_data)
    })

@api_bp.route('/all', methods=['GET'])
@whiteboard_auth_required
def get_whiteboard_all():
    date_str = request.args.get('date')
    
    tasks_query = Task.query.filter_by(whiteboard_id=request.whiteboard.id)
    announcements_query = Announcement.query.filter_by(whiteboard_id=request.whiteboard.id)
    assignments_query = Assignment.query.filter_by(whiteboard_id=request.whiteboard.id)
    
    if date_str:
        try:
            target_date = parse_china_time(date_str + ' 00:00:00')
            next_date = target_date + timedelta(days=1)
            
            tasks_query = tasks_query.filter(
                Task.created_at >= target_date,
                Task.created_at < next_date
            )
            
            announcements_query = announcements_query.filter(
                Announcement.created_at >= target_date,
                Announcement.created_at < next_date
            )
            
            assignments_query = assignments_query.filter(
                Assignment.due_date >= target_date,
                Assignment.due_date < next_date
            )
        except ValueError:
            return jsonify({'error': '日期格式无效，请使用YYYY-MM-DD格式'}), 400
    
    tasks = tasks_query.order_by(Task.created_at.desc()).all()
    announcements = announcements_query.order_by(Announcement.created_at.desc()).all()
    assignments = assignments_query.order_by(Assignment.created_at.desc()).all()
    
    tasks_data = []
    for task in tasks:
        tasks_data.append({
            'type': 'task',
            'id': task.id,
            'title': task.title,
            'description': task.description,
            'priority': task.priority,
            'action_id': task.action_id,
            'due_date': format_china_time(task.due_date) if task.due_date else None,
            'is_acknowledged': task.is_acknowledged,
            'is_completed': task.is_completed,
            'created_at': format_china_time(task.created_at)
        })
    
    announcements_data = []
    for announcement in announcements:
        announcements_data.append({
            'type': 'announcement',
            'id': announcement.id,
            'title': announcement.title,
            'content': announcement.content,
            'is_long_term': announcement.is_long_term,
            'created_at': format_china_time(announcement.created_at)
        })
    
    assignments_data = []
    for assignment in assignments:
        assignments_data.append({
            'type': 'assignment',
            'id': assignment.id,
            'title': assignment.title,
            'description': assignment.description,
            'subject': assignment.subject,
            'due_date': format_china_time(assignment.due_date),
            'created_at': format_china_time(assignment.created_at)
        })
    
    all_data = tasks_data + announcements_data + assignments_data
    all_data.sort(key=lambda x: x['created_at'], reverse=True)
    
    return jsonify({
        'success': True,
        'data': all_data,
        'count': len(all_data),
        'tasks_count': len(tasks_data),
        'announcements_count': len(announcements_data),
        'assignments_count': len(assignments_data)
    })

@api_bp.route('/tasks/<int:task_id>/acknowledge', methods=['POST'])
@whiteboard_auth_required
def acknowledge_task(task_id):
    task = Task.query.filter_by(
        id=task_id, 
        whiteboard_id=request.whiteboard.id
    ).first()
    
    if not task:
        return jsonify({'error': '任务不存在'}), 404
    
    try:
        task.is_acknowledged = True
        db.session.commit()
        
        socketio.emit('task_updated', {
            'id': task.id,
            'title': task.title,
            'is_acknowledged': task.is_acknowledged,
            'is_completed': task.is_completed
        }, room=f"teacher_{task.whiteboard.class_obj.teacher_id}")
        
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': '确认任务失败'}), 500

@api_bp.route('/tasks/<int:task_id>/complete', methods=['POST'])
@whiteboard_auth_required
def complete_task(task_id):
    task = Task.query.filter_by(
        id=task_id, 
        whiteboard_id=request.whiteboard.id
    ).first()
    
    if not task:
        return jsonify({'error': '任务不存在'}), 404
    
    try:
        task.is_acknowledged = True
        task.is_completed = True
        db.session.commit()
        
        socketio.emit('task_updated', {
            'id': task.id,
            'title': task.title,
            'is_acknowledged': task.is_acknowledged,
            'is_completed': task.is_completed
        }, room=f"teacher_{task.whiteboard.class_obj.teacher_id}")
        
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': '完成任务失败'}), 500

@api_bp.route('/heartbeat', methods=['POST'])
@whiteboard_auth_required
def whiteboard_heartbeat():
    try:
        current_time = get_china_time().replace(tzinfo=None)
        
        whiteboard = request.whiteboard
        whiteboard.last_heartbeat = current_time
        whiteboard.is_online = True
        
        status_history = WhiteboardStatusHistory(
            whiteboard_id=whiteboard.id,
            is_online=True
        )
        db.session.add(status_history)
        
        db.session.commit()
        
        socketio.emit('whiteboard_status_update', {
            'whiteboard_id': whiteboard.id,
            'is_online': True,
            'last_heartbeat': format_china_time(current_time)
        }, room=f"teacher_{whiteboard.class_obj.teacher_id}")
        
        return jsonify({'success': True, 'message': '心跳接收成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': '心跳更新失败'}), 500