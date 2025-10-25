from extensions import socketio, db
from flask import session, request
from flask_socketio import emit, join_room, leave_room
from models.user import User
from models.class_models import Class
from models.whiteboard import Whiteboard, WhiteboardStatusHistory
from models.task import Task
from utils.time_utils import get_china_time, format_china_time

@socketio.on('connect')
def handle_connect():
    try:
        board_id = request.args.get('board_id')
        secret_key = request.args.get('secret_key')
        
        if board_id and secret_key:
            whiteboard = Whiteboard.query.filter_by(board_id=board_id, secret_key=secret_key).first()
            if whiteboard:
                join_room(f"whiteboard_{whiteboard.id}")
                
                current_time = get_china_time().replace(tzinfo=None)
                whiteboard.is_online = True
                whiteboard.last_heartbeat = current_time
                db.session.commit()
                
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
                
                emit('connected', {'status': 'success', 'message': '认证成功'})
                return True
            else:
                emit('connected', {'status': 'error', 'message': '认证失败'})
                return False
        else:
            user_id = session.get('user_id')
            if user_id:
                user = db.session.get(User, user_id)
                if user and user.role == 'teacher':
                    join_room(f"teacher_{user_id}")
                    
                    classes = Class.query.filter_by(teacher_id=user_id).all()
                    for class_obj in classes:
                        for whiteboard in class_obj.whiteboards:
                            is_actually_online = False
                            if whiteboard.last_heartbeat:
                                time_diff = (get_china_time().replace(tzinfo=None) - whiteboard.last_heartbeat).total_seconds()
                                is_actually_online = time_diff < 30
                            
                            if whiteboard.is_online != is_actually_online:
                                whiteboard.is_online = is_actually_online
                                db.session.commit()
                            
                            socketio.emit('whiteboard_status_update', {
                                'whiteboard_id': whiteboard.id,
                                'is_online': whiteboard.is_online,
                                'last_heartbeat': format_china_time(whiteboard.last_heartbeat) if whiteboard.last_heartbeat else None
                            }, room=f"teacher_{user_id}")
                    
                    emit('connected', {'status': 'success', 'message': '教师端连接成功'})
                    return True
                else:
                    emit('connected', {'status': 'error', 'message': '无权限连接'})
                    return False
            else:
                emit('connected', {'status': 'error', 'message': '未登录'})
                return False
    except Exception as e:
        emit('connected', {'status': 'error', 'message': '服务器内部错误'})
        return False

@socketio.on('disconnect')
def handle_disconnect():
    try:
        board_id = request.args.get('board_id')
        if board_id:
            whiteboard = Whiteboard.query.filter_by(board_id=board_id).first()
            if whiteboard:
                whiteboard.is_online = False
                db.session.commit()
                
                status_history = WhiteboardStatusHistory(
                    whiteboard_id=whiteboard.id,
                    is_online=False
                )
                db.session.add(status_history)
                db.session.commit()
                
                socketio.emit('whiteboard_status_update', {
                    'whiteboard_id': whiteboard.id,
                    'is_online': False,
                    'last_heartbeat': format_china_time(whiteboard.last_heartbeat) if whiteboard.last_heartbeat else None
                }, room=f"teacher_{whiteboard.class_obj.teacher_id}")
    except Exception as e:
        pass

@socketio.on('heartbeat')
def handle_heartbeat(data):
    board_id = data.get('board_id')
    if board_id:
        whiteboard = Whiteboard.query.filter_by(board_id=board_id).first()
        if whiteboard:
            whiteboard.last_heartbeat = get_china_time().replace(tzinfo=None)
            db.session.commit()
            
            socketio.emit('whiteboard_status_update', {
                'whiteboard_id': whiteboard.id,
                'is_online': True,
                'last_heartbeat': format_china_time(whiteboard.last_heartbeat)
            }, room=f"teacher_{whiteboard.class_obj.teacher_id}")

@socketio.on('task_acknowledged')
def handle_task_acknowledged(data):
    task_id = data.get('task_id')
    task = Task.query.get(task_id)
    if task:
        task.is_acknowledged = True
        db.session.commit()
        
        socketio.emit('task_updated', {
            'id': task.id,
            'title': task.title,
            'is_acknowledged': task.is_acknowledged,
            'is_completed': task.is_completed
        }, room=f"teacher_{task.whiteboard.class_obj.teacher_id}")

@socketio.on('task_completed')
def handle_task_completed(data):
    task_id = data.get('task_id')
    task = Task.query.get(task_id)
    if task:
        task.is_completed = True
        db.session.commit()
        
        socketio.emit('task_updated', {
            'id': task.id,
            'title': task.title,
            'is_acknowledged': task.is_acknowledged,
            'is_completed': task.is_completed
        }, room=f"teacher_{task.whiteboard.class_obj.teacher_id}")

@socketio.on('join_teacher_room')
def handle_join_teacher_room():
    user_id = session.get('user_id')
    if user_id:
        user = db.session.get(User, user_id)
        if user and user.role == 'teacher':
            join_room(f"teacher_{user_id}")
            emit('joined_teacher_room', {'status': 'success'})
        else:
            emit('joined_teacher_room', {'status': 'error', 'message': '无权限'})
    else:
        emit('joined_teacher_room', {'status': 'error', 'message': '未登录'})