from flask import Blueprint, render_template, redirect, url_for, session, request, flash, jsonify
from extensions import db
from models.user import User
from models.class_models import Class, TeacherClass
from models.note import Note
from models.whiteboard import Whiteboard
from utils.auth_utils import login_required, teacher_required

web_notes_bp = Blueprint('web_notes', __name__, url_prefix='/web/notes')

@web_notes_bp.route('/classes/<int:class_id>/notes', methods=['GET'])
@login_required
@teacher_required
def get_class_notes(class_id):
    """获取班级的所有笔记（Web端教师使用）"""
    user = db.session.get(User, session['user_id'])
    
    # 检查权限
    class_obj = Class.query.get_or_404(class_id)
    has_permission = False
    
    if class_obj.teacher_id == user.id:
        has_permission = True
    else:
        teacher_class = TeacherClass.query.filter_by(
            class_id=class_id,
            teacher_id=user.id,
            is_approved=True
        ).first()
        if teacher_class:
            has_permission = True
    
    if not has_permission:
        return jsonify({'error': '无权限访问该班级的笔记'}), 403
    
    try:
        # 获取查询参数
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        whiteboard_id = request.args.get('whiteboard_id')
        file_type = request.args.get('file_type')
        search = request.args.get('search')
        
        # 构建查询
        query = Note.query.filter_by(class_id=class_id)
        
        # 白板筛选
        if whiteboard_id:
            query = query.filter(Note.whiteboard_id == whiteboard_id)
        
        # 文件类型筛选
        if file_type:
            query = query.filter(Note.file_type == file_type.lower())
        
        # 搜索筛选
        if search:
            search_pattern = f'%{search}%'
            query = query.filter(
                db.or_(
                    Note.title.like(search_pattern),
                    Note.description.like(search_pattern),
                    Note.original_filename.like(search_pattern)
                )
            )
        
        # 分页
        pagination = query.order_by(Note.created_at.desc()).paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        notes_data = [note.to_dict() for note in pagination.items]
        
        # 获取班级的所有白板
        whiteboards = Whiteboard.query.filter_by(class_id=class_id).all()
        whiteboards_data = [{
            'id': wb.id,
            'name': wb.name
        } for wb in whiteboards]
        
        return jsonify({
            'success': True,
            'notes': notes_data,
            'whiteboards': whiteboards_data,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': pagination.total,
                'pages': pagination.pages
            }
        })
        
    except Exception as e:
        print(f"获取班级笔记失败: {str(e)}")
        return jsonify({'error': '获取班级笔记失败'}), 500

@web_notes_bp.route('/notes/<int:note_id>', methods=['DELETE'])
@login_required
@teacher_required
def delete_class_note(note_id):
    """删除班级笔记"""
    user = db.session.get(User, session['user_id'])
    
    note = Note.query.get_or_404(note_id)
    
    # 检查权限：班主任或笔记所在班级的授课教师
    has_permission = False
    
    if note.class_obj.teacher_id == user.id:
        has_permission = True
    else:
        teacher_class = TeacherClass.query.filter_by(
            class_id=note.class_id,
            teacher_id=user.id,
            is_approved=True
        ).first()
        if teacher_class:
            has_permission = True
    
    if not has_permission:
        return jsonify({'error': '无权限删除该笔记'}), 403
    
    try:
        # 构建完整文件路径
        file_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'uploads',
            str(note.class_id),
            note.file_path
        )
        
        # 删除数据库记录
        db.session.delete(note)
        db.session.commit()
        
        # 删除物理文件
        if os.path.exists(file_path):
            os.remove(file_path)
        
        return jsonify({
            'success': True,
            'message': '笔记删除成功'
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"删除笔记失败: {str(e)}")
        return jsonify({'error': '删除笔记失败'}), 500
    
@web_notes_bp.route('/notes/<int:note_id>/download')
@login_required
@teacher_required
def download_note(note_id):
    """下载笔记文件"""
    user = db.session.get(User, session['user_id'])
    
    note = Note.query.get_or_404(note_id)
    
    # 检查权限：班主任或笔记所在班级的授课教师
    has_permission = False
    
    if note.class_obj.teacher_id == user.id:
        has_permission = True
    else:
        teacher_class = TeacherClass.query.filter_by(
            class_id=note.class_id,
            teacher_id=user.id,
            is_approved=True
        ).first()
        if teacher_class:
            has_permission = True
    
    if not has_permission:
        flash('无权限下载该笔记', 'error')
        return redirect(url_for('classes.classes'))
    
    try:
        # 构建完整文件路径
        file_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'uploads',
            str(note.class_id),
            note.file_path
        )
        
        if not os.path.exists(file_path):
            flash('文件不存在', 'error')
            return redirect(url_for('web_notes.class_notes_page', class_id=note.class_id))
        
        # 增加下载计数
        note.download_count += 1
        db.session.commit()
        
        # 发送文件
        return send_file(
            file_path,
            as_attachment=True,
            download_name=note.original_filename,
            mimetype=note.mime_type
        )
        
    except Exception as e:
        print(f"下载笔记失败: {str(e)}")
        flash('下载笔记失败', 'error')
        return redirect(url_for('web_notes.class_notes_page', class_id=note.class_id))
    
@web_notes_bp.route('/classes/<int:class_id>/notes/page')
@login_required
@teacher_required
def class_notes_page(class_id):
    """班级笔记管理页面"""
    user = db.session.get(User, session['user_id'])
    
    # 检查权限
    class_obj = Class.query.get_or_404(class_id)
    has_permission = False
    
    if class_obj.teacher_id == user.id:
        has_permission = True
    else:
        teacher_class = TeacherClass.query.filter_by(
            class_id=class_id,
            teacher_id=user.id,
            is_approved=True
        ).first()
        if teacher_class:
            has_permission = True
    
    if not has_permission:
        flash('无权限访问该班级的笔记', 'error')
        return redirect(url_for('classes.classes'))
    
    # 获取班级的所有白板
    whiteboards = Whiteboard.query.filter_by(class_id=class_id).all()
    
    return render_template('class_notes.html',
                         username=session.get('username'),
                         role=session.get('role'),
                         avatar=session.get('avatar'),
                         class_obj=class_obj,
                         whiteboards=whiteboards)