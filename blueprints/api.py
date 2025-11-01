from flask import Blueprint, request, jsonify
from datetime import timedelta
from extensions import db, socketio
from models.user import User
from models.whiteboard import Whiteboard, WhiteboardStatusHistory
from models.developer import DeveloperApp
from models.task import Task
from models.assignment import Assignment
from models.announcement import Announcement
from utils.auth_utils import whiteboard_auth_required, user_token_auth_required
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

@api_bp.route('/framework/auth', methods=['POST'])
def framework_auth():
    """框架认证接口 - 使用app凭证和token获取白板密钥"""
    data = request.json
    
    app_id = data.get('app_id')
    app_secret = data.get('app_secret')
    id = data.get('id')
    token = data.get('token')
    
    if not all([app_id, app_secret, token]):
        return jsonify({'error': '缺少必要参数'}), 400
    
    # 验证开发者应用 
    app = DeveloperApp.query.filter_by(
        app_id=app_id, 
        app_secret=app_secret,
        status='approved'
    ).first()
    
    if not app:
        return jsonify({'error': '应用认证失败'}), 401
    
    # 验证白板token
    whiteboard = Whiteboard.query.filter_by(id=id, token=token, is_active=True).first()
    if not whiteboard:
        return jsonify({'error': '白板token无效'}), 401
    
    return jsonify({
        'success': True,
        'board_id': whiteboard.board_id,
        'secret_key': whiteboard.secret_key,
        'whiteboard_name': whiteboard.name,
        'class_name': whiteboard.class_obj.name if whiteboard.class_obj else None
    })

@api_bp.route('/reset-secret', methods=['POST'])
def reset_whiteboard_secret():
    data = request.json
    
    # 获取请求参数
    whiteboard_id = data.get('id')
    token = data.get('token')
    
    if not whiteboard_id or not token:
        return jsonify({'error': '缺少必要参数：id 和 token'}), 400
    
    # 验证白板是否存在且token匹配
    whiteboard = Whiteboard.query.filter_by(
        id=whiteboard_id, 
        token=token, 
        is_active=True
    ).first()
    
    if not whiteboard:
        return jsonify({'error': '白板ID或token无效'}), 401
    
    try:
        # 生成新的白板密钥
        from utils.code_utils import generate_whiteboard_credentials
        _, new_secret_key = generate_whiteboard_credentials()
        
        # 更新白板密钥
        whiteboard.secret_key = new_secret_key
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '白板密钥重置成功',
            'new_secret_key': new_secret_key,
            'whiteboard_id': whiteboard.id,
            'whiteboard_name': whiteboard.name
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': '重置密钥时发生错误'}), 500
    
@api_bp.route('/user/whiteboards', methods=['GET'])
@user_token_auth_required
def get_user_whiteboards():
    """通过用户token获取用户所有可访问的白板信息"""
    user = request.user
    
    try:
        accessible_whiteboards = user.get_accessible_whiteboards()
        
        whiteboards_data = []
        for whiteboard in accessible_whiteboards:
            whiteboards_data.append({
                'id': whiteboard.id,
                'name': whiteboard.name,
                'board_id': whiteboard.board_id,
                'secret_key': whiteboard.secret_key,
                'class_name': whiteboard.class_obj.name if whiteboard.class_obj else None,
                'class_id': whiteboard.class_id,
                'is_online': whiteboard.is_online,
                'last_heartbeat': format_china_time(whiteboard.last_heartbeat) if whiteboard.last_heartbeat else None,
                'created_at': format_china_time(whiteboard.created_at)
            })
        
        return jsonify({
            'success': True,
            'data': whiteboards_data,
            'count': len(whiteboards_data),
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email
            }
        })
    except Exception as e:
        return jsonify({'error': '获取白板信息失败'}), 500

@api_bp.route('/framework/auth-with-token', methods=['POST'])
def framework_auth_with_token():
    """框架认证接口 - 使用app凭证和用户token获取所有白板信息"""
    data = request.json
    
    app_id = data.get('app_id')
    app_secret = data.get('app_secret')
    user_token = data.get('user_token')
    
    if not all([app_id, app_secret, user_token]):
        return jsonify({'error': '缺少必要参数'}), 400
    
    # 验证开发者应用 
    app = DeveloperApp.query.filter_by(
        app_id=app_id, 
        app_secret=app_secret,
        status='approved'
    ).first()
    
    if not app:
        return jsonify({'error': '应用认证失败'}), 401
    
    # 验证用户token
    user = User.query.filter_by(user_token=user_token, role='teacher', is_active=True).first()
    if not user:
        return jsonify({'error': '用户token无效'}), 401
    
    # 获取用户所有可访问的白板
    accessible_whiteboards = user.get_accessible_whiteboards()
    
    whiteboards_data = []
    for whiteboard in accessible_whiteboards:
        whiteboards_data.append({
            'id': whiteboard.id,
            'name': whiteboard.name,
            'board_id': whiteboard.board_id,
            'secret_key': whiteboard.secret_key,
            'class_name': whiteboard.class_obj.name if whiteboard.class_obj else None,
            'class_id': whiteboard.class_id,
            'is_online': whiteboard.is_online,
            'last_heartbeat': format_china_time(whiteboard.last_heartbeat) if whiteboard.last_heartbeat else None,
            'created_at': format_china_time(whiteboard.created_at)
        })
    
    return jsonify({
        'success': True,
        'whiteboards': whiteboards_data,
        'count': len(whiteboards_data),
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email
        }
    })