from flask import Blueprint, request, jsonify, session
from extensions import db, socketio
from models.user import User
from models.whiteboard import Whiteboard
from models.announcement import Announcement
from utils.auth_utils import login_required, teacher_required
from utils.time_utils import format_china_time

announcements_bp = Blueprint('announcements', __name__)

@announcements_bp.route('/whiteboards/<int:whiteboard_id>/create_announcement', methods=['POST'])
@login_required
@teacher_required
def create_announcement(whiteboard_id):
    whiteboard = Whiteboard.query.get_or_404(whiteboard_id)
    user = db.session.get(User, session['user_id'])
    
    if whiteboard.class_obj.teacher_id != user.id:
        return jsonify({'error': '只有班主任可以发布公告'}), 403
    
    data = request.get_json()
    title = data.get('title')
    content = data.get('content')
    is_long_term = data.get('is_long_term', False)
    
    if not title or not content:
        return jsonify({'error': '标题和内容不能为空'}), 400
    
    announcement = Announcement(
        title=title,
        content=content,
        is_long_term=is_long_term,
        whiteboard_id=whiteboard_id,
        teacher_id=user.id
    )
    
    try:
        db.session.add(announcement)
        db.session.commit()
        
        socketio.emit('new_announcement', {
            'id': announcement.id,
            'title': announcement.title,
            'content': announcement.content,
            'is_long_term': announcement.is_long_term,
            'created_at': format_china_time(announcement.created_at),
            'teacher_name': announcement.teacher.username
        }, room=f"whiteboard_{whiteboard_id}")
        
        return jsonify({'success': True, 'announcement_id': announcement.id})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': '创建公告失败'}), 500

@announcements_bp.route('/announcements/<int:announcement_id>/delete', methods=['POST'])
@login_required
@teacher_required
def delete_announcement(announcement_id):
    announcement = Announcement.query.get_or_404(announcement_id)
    user = db.session.get(User, session['user_id'])
    
    if user.role != 'teacher' or announcement.whiteboard.class_obj.teacher_id != user.id:
        return jsonify({'error': '无权限'}), 403
    
    try:
        whiteboard_id = announcement.whiteboard_id
        db.session.delete(announcement)
        db.session.commit()
        socketio.emit('delete_announcement', {'announcement_id': announcement_id}, room=f"whiteboard_{whiteboard_id}")
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': '删除公告失败'}), 500

@announcements_bp.route('/whiteboards/<int:whiteboard_id>/announcements')
@login_required
def get_whiteboard_announcements_list(whiteboard_id):
    whiteboard = Whiteboard.query.get_or_404(whiteboard_id)
    user = db.session.get(User, session['user_id'])
    
    if user.role != 'teacher' or whiteboard.class_obj.teacher_id != user.id:
        return jsonify({'error': '无权限'}), 403
    
    try:
        announcements = Announcement.query.filter_by(whiteboard_id=whiteboard_id).order_by(Announcement.created_at.desc()).all()
        
        announcements_data = []
        for announcement in announcements:
            announcements_data.append({
                'id': announcement.id,
                'title': announcement.title,
                'content': announcement.content,
                'is_long_term': announcement.is_long_term,
                'created_at': format_china_time(announcement.created_at)
            })
        
        return jsonify({'success': True, 'announcements': announcements_data})
    except Exception as e:
        return jsonify({'error': '获取公告列表失败'}), 500