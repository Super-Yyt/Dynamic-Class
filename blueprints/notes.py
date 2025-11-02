from flask import Blueprint, request, jsonify, send_file
import os
import mimetypes
from werkzeug.utils import secure_filename
from extensions import db
from models.whiteboard import Whiteboard
from models.class_models import Class, TeacherClass
from models.note import Note
from models.user import User
from utils.auth_utils import whiteboard_auth_required, login_required, teacher_required
from utils.time_utils import get_china_time, format_china_time

notes_bp = Blueprint('notes', __name__, url_prefix='/api/whiteboard')

# 允许上传的文件类型
ALLOWED_EXTENSIONS = {
    'png', 'jpg', 'jpeg', 'gif', 'bmp',  # 图片
    'pdf',  # PDF文档
    'txt', 'md',  # 文本文件
    'ppt', 'pptx',  # PowerPoint
    'doc', 'docx',  # Word文档
    'zip', 'rar',  # 压缩文件
    'icstk',
}

def allowed_file(filename):
    """检查文件类型是否允许"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_upload_path(whiteboard, filename):
    """生成文件保存路径"""
    current_time = get_china_time()
    
    # 基础上传目录（包含班级ID）
    base_dir = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), 
        'uploads',
        str(whiteboard.class_id)  # 按班级ID分开
    )
    
    # 按白板ID/年/月/日组织目录
    upload_path = os.path.join(
        base_dir,
        str(whiteboard.id),
        str(current_time.year),
        f"{current_time.month:02d}",
        f"{current_time.day:02d}"
    )
    
    # 确保目录存在
    os.makedirs(upload_path, exist_ok=True)
    
    # 生成安全的文件名（添加时间戳避免重名）
    name, ext = os.path.splitext(secure_filename(filename))
    timestamp = int(current_time.timestamp())
    safe_filename = f"{name}_{timestamp}{ext}"
    
    return os.path.join(upload_path, safe_filename)

@notes_bp.route('/upload_note', methods=['POST'])
@whiteboard_auth_required
def upload_note():
    """上传白板笔记文件"""
    
    # 检查是否有文件被上传
    if 'file' not in request.files:
        return jsonify({'error': '没有文件被上传'}), 400
    
    file = request.files['file']
    
    # 检查文件名是否为空
    if file.filename == '':
        return jsonify({'error': '没有选择文件'}), 400
    
    # 检查文件类型
    if not allowed_file(file.filename):
        return jsonify({
            'error': '不支持的文件类型',
            'allowed_types': list(ALLOWED_EXTENSIONS)
        }), 400
    
    # 检查文件大小（限制为10MB）
    file.seek(0, os.SEEK_END)
    file_length = file.tell()
    file.seek(0)
    
    if file_length > 10 * 1024 * 1024:  # 10MB
        return jsonify({'error': '文件大小不能超过10MB'}), 400
    
    try:
        # 生成保存路径
        save_path = get_upload_path(request.whiteboard, file.filename)
        
        # 保存文件
        file.save(save_path)
        
        # 获取相对路径用于URL访问
        base_upload_dir = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), 
            'uploads',
            str(request.whiteboard.class_id)
        )
        relative_path = os.path.relpath(save_path, base_upload_dir)
        
        # 将Windows路径分隔符转换为URL路径分隔符
        url_safe_path = relative_path.replace('\\', '/')
        
        # 构建文件URL
        file_url = f"/uploads/{request.whiteboard.class_id}/{url_safe_path}"
        
        # 获取文件信息
        file_extension = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
        mime_type = mimetypes.guess_type(file.filename)[0] or 'application/octet-stream'
        
        # 创建笔记记录
        note = Note(
            filename=os.path.basename(save_path),
            original_filename=file.filename,
            file_path=url_safe_path,
            file_size=file_length,
            file_type=file_extension,
            mime_type=mime_type,
            whiteboard_id=request.whiteboard.id,
            class_id=request.whiteboard.class_id,
            uploaded_by=request.whiteboard.class_obj.teacher_id,  # 使用班级创建者的ID
            title=request.form.get('title', ''),
            description=request.form.get('description', ''),
            tags=request.form.get('tags', '')
        )
        
        db.session.add(note)
        db.session.commit()
        
        # 记录上传日志
        print(f"白板笔记上传成功: {file.filename} -> {save_path}")
        
        return jsonify({
            'success': True,
            'message': '文件上传成功',
            'note_id': note.id,
            'filename': file.filename,
            'file_path': url_safe_path,
            'file_url': file_url,
            'file_size': file_length,
            'uploaded_at': format_china_time(get_china_time()),
            'class_id': request.whiteboard.class_id,
            'whiteboard_id': request.whiteboard.id
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"文件上传失败: {str(e)}")
        return jsonify({'error': '文件上传失败'}), 500

@notes_bp.route('/notes', methods=['GET'])
@whiteboard_auth_required
def get_notes_list():
    """获取白板笔记列表"""
    try:
        # 获取查询参数
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        file_type = request.args.get('file_type')
        tag = request.args.get('tag')
        search = request.args.get('search')
        sort_by = request.args.get('sort_by', 'created_at')
        sort_order = request.args.get('sort_order', 'desc')
        
        # 构建查询
        query = Note.query.filter_by(whiteboard_id=request.whiteboard.id)
        
        # 文件类型筛选
        if file_type:
            query = query.filter(Note.file_type == file_type.lower())
        
        # 标签筛选
        if tag:
            query = query.filter(Note.tags.like(f'%{tag}%'))
        
        # 搜索筛选（标题、描述、文件名）
        if search:
            search_pattern = f'%{search}%'
            query = query.filter(
                db.or_(
                    Note.title.like(search_pattern),
                    Note.description.like(search_pattern),
                    Note.original_filename.like(search_pattern),
                    Note.tags.like(search_pattern)
                )
            )
        
        # 排序
        if sort_by == 'filename':
            order_field = Note.original_filename
        elif sort_by == 'file_size':
            order_field = Note.file_size
        elif sort_by == 'download_count':
            order_field = Note.download_count
        else:  # 默认按创建时间
            order_field = Note.created_at
        
        if sort_order == 'asc':
            query = query.order_by(order_field.asc())
        else:
            query = query.order_by(order_field.desc())
        
        # 分页
        pagination = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        notes_data = [note.to_dict() for note in pagination.items]
        
        return jsonify({
            'success': True,
            'notes': notes_data,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': pagination.total,
                'pages': pagination.pages,
                'has_prev': pagination.has_prev,
                'has_next': pagination.has_next
            },
            'filters': {
                'file_type': file_type,
                'tag': tag,
                'search': search,
                'sort_by': sort_by,
                'sort_order': sort_order
            }
        })
        
    except Exception as e:
        print(f"获取笔记列表失败: {str(e)}")
        return jsonify({'error': '获取笔记列表失败'}), 500

@notes_bp.route('/notes/<int:note_id>', methods=['GET'])
@whiteboard_auth_required
def get_note_detail(note_id):
    """获取笔记详情"""
    try:
        note = Note.query.filter_by(
            id=note_id, 
            whiteboard_id=request.whiteboard.id
        ).first()
        
        if not note:
            return jsonify({'error': '笔记不存在'}), 404
        
        return jsonify({
            'success': True,
            'note': note.to_dict()
        })
        
    except Exception as e:
        print(f"获取笔记详情失败: {str(e)}")
        return jsonify({'error': '获取笔记详情失败'}), 500

@notes_bp.route('/notes/<int:note_id>', methods=['PUT'])
@whiteboard_auth_required
def update_note(note_id):
    """更新笔记信息（标题、描述、标签等）"""
    try:
        note = Note.query.filter_by(
            id=note_id, 
            whiteboard_id=request.whiteboard.id
        ).first()
        
        if not note:
            return jsonify({'error': '笔记不存在'}), 404
        
        data = request.get_json()
        
        # 更新字段
        if 'title' in data:
            note.title = data['title']
        if 'description' in data:
            note.description = data['description']
        if 'tags' in data:
            note.tags = data['tags']
        if 'is_public' in data:
            note.is_public = bool(data['is_public'])
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '笔记更新成功',
            'note': note.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"更新笔记失败: {str(e)}")
        return jsonify({'error': '更新笔记失败'}), 500

@notes_bp.route('/notes/<int:note_id>', methods=['DELETE'])
@whiteboard_auth_required
def delete_note(note_id):
    """删除笔记"""
    try:
        note = Note.query.filter_by(
            id=note_id, 
            whiteboard_id=request.whiteboard.id
        ).first()
        
        if not note:
            return jsonify({'error': '笔记不存在'}), 404
        
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
            print(f"已删除文件: {file_path}")
        
        return jsonify({
            'success': True,
            'message': '笔记删除成功'
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"删除笔记失败: {str(e)}")
        return jsonify({'error': '删除笔记失败'}), 500

@notes_bp.route('/notes/<int:note_id>/download', methods=['GET'])
@whiteboard_auth_required
def download_note(note_id):
    """下载笔记文件"""
    try:
        note = Note.query.filter_by(
            id=note_id, 
            whiteboard_id=request.whiteboard.id
        ).first()
        
        if not note:
            return jsonify({'error': '笔记不存在'}), 404
        
        # 构建完整文件路径
        file_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'uploads',
            str(note.class_id),
            note.file_path
        )
        
        if not os.path.exists(file_path):
            return jsonify({'error': '文件不存在'}), 404
        
        # 增加下载计数
        note.increment_download_count()
        
        # 发送文件
        return send_file(
            file_path,
            as_attachment=True,
            download_name=note.original_filename,
            mimetype=note.mime_type
        )
        
    except Exception as e:
        print(f"下载笔记失败: {str(e)}")
        return jsonify({'error': '下载笔记失败'}), 500

@notes_bp.route('/notes/stats', methods=['GET'])
@whiteboard_auth_required
def get_notes_stats():
    """获取笔记统计信息"""
    try:
        whiteboard_id = request.whiteboard.id
        
        # 总笔记数
        total_notes = Note.query.filter_by(whiteboard_id=whiteboard_id).count()
        
        # 按文件类型统计
        type_stats = db.session.query(
            Note.file_type,
            db.func.count(Note.id)
        ).filter_by(whiteboard_id=whiteboard_id).group_by(Note.file_type).all()
        
        # 总文件大小
        total_size = db.session.query(db.func.sum(Note.file_size)).filter_by(
            whiteboard_id=whiteboard_id
        ).scalar() or 0
        
        # 最近上传的笔记
        recent_notes = Note.query.filter_by(whiteboard_id=whiteboard_id).order_by(
            Note.created_at.desc()
        ).limit(5).all()
        
        return jsonify({
            'success': True,
            'stats': {
                'total_notes': total_notes,
                'total_size': total_size,
                'total_size_formatted': Note.format_file_size(Note(file_size=total_size)),
                'file_types': {file_type: count for file_type, count in type_stats},
                'recent_notes': [note.to_dict() for note in recent_notes]
            }
        })
        
    except Exception as e:
        print(f"获取笔记统计失败: {str(e)}")
        return jsonify({'error': '获取笔记统计失败'}), 500