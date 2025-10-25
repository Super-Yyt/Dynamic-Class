from extensions import db
from utils.time_utils import get_china_time, format_china_time

class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_size = db.Column(db.Integer, nullable=False)  # 文件大小（字节）
    file_type = db.Column(db.String(50), nullable=False)  # 文件类型扩展名
    mime_type = db.Column(db.String(100))  # MIME类型
    
    whiteboard_id = db.Column(db.Integer, db.ForeignKey('whiteboard.id'), nullable=False)
    class_id = db.Column(db.Integer, db.ForeignKey('class.id'), nullable=False)
    uploaded_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # 上传者（白板）
    
    title = db.Column(db.String(200))  # 笔记标题（可选）
    description = db.Column(db.Text)  # 笔记描述（可选）
    tags = db.Column(db.String(300))  # 标签，用逗号分隔
    
    is_public = db.Column(db.Boolean, default=True)  # 是否公开
    download_count = db.Column(db.Integer, default=0)  # 下载次数
    
    created_at = db.Column(db.DateTime, default=get_china_time)
    updated_at = db.Column(db.DateTime, default=get_china_time, onupdate=get_china_time)
    
    # 关系
    whiteboard = db.relationship('Whiteboard', backref=db.backref('notes', lazy=True))
    class_obj = db.relationship('Class', backref=db.backref('notes', lazy=True))
    uploader = db.relationship('User', foreign_keys=[uploaded_by], backref=db.backref('uploaded_notes', lazy=True))
    
    def __repr__(self):
        return f'<Note {self.original_filename}>'
    
    def to_dict(self):
        """将笔记对象转换为字典"""
        return {
            'id': self.id,
            'filename': self.filename,
            'original_filename': self.original_filename,
            'file_path': self.file_path,
            'file_url': f"/uploads/{self.class_id}/{self.file_path}",
            'file_size': self.file_size,
            'file_size_formatted': self.format_file_size(),
            'file_type': self.file_type,
            'mime_type': self.mime_type,
            'whiteboard_id': self.whiteboard_id,
            'class_id': self.class_id,
            'uploaded_by': self.uploaded_by,
            'uploader_name': self.uploader.username if self.uploader else None,
            'title': self.title or self.original_filename,
            'description': self.description,
            'tags': self.tags,
            'tags_list': self.get_tags_list(),
            'is_public': self.is_public,
            'download_count': self.download_count,
            'created_at': format_china_time(self.created_at),
            'updated_at': format_china_time(self.updated_at),
            'whiteboard_name': self.whiteboard.name if self.whiteboard else None,
            'class_name': self.class_obj.name if self.class_obj else None
        }
    
    def format_file_size(self):
        """格式化文件大小"""
        if self.file_size < 1024:
            return f"{self.file_size} B"
        elif self.file_size < 1024 * 1024:
            return f"{self.file_size / 1024:.1f} KB"
        elif self.file_size < 1024 * 1024 * 1024:
            return f"{self.file_size / (1024 * 1024):.1f} MB"
        else:
            return f"{self.file_size / (1024 * 1024 * 1024):.1f} GB"
    
    def get_tags_list(self):
        """获取标签列表"""
        if self.tags:
            return [tag.strip() for tag in self.tags.split(',') if tag.strip()]
        return []
    
    def increment_download_count(self):
        """增加下载计数"""
        self.download_count += 1
        db.session.commit()