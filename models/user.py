from extensions import db
from utils.time_utils import get_china_time, format_china_time
from .class_models import Class
import secrets

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    casdoor_id = db.Column(db.String(100), unique=True, nullable=False)
    username = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), nullable=True)
    display_name = db.Column(db.String(100))
    avatar = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=get_china_time)
    last_login = db.Column(db.DateTime)

    role = db.Column(db.String(20), default='student')  # student, teacher, developer
    is_active = db.Column(db.Boolean, default=True)
    
    organization = db.Column(db.String(50), default='student')  # student, teacher, developer
    
    user_token = db.Column(db.String(64), unique=True, nullable=True)
    token_created_at = db.Column(db.DateTime)
    
    def __repr__(self):
        return f'<User {self.username} ({self.organization})>'
    
    def to_dict(self):
        """将用户对象转换为字典"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'display_name': self.display_name,
            'avatar': self.avatar,
            'role': self.role,
            'organization': self.organization,
            'created_at': format_china_time(self.created_at),
            'last_login': format_china_time(self.last_login),
            'has_user_token': self.user_token is not None
        }
    
    def generate_user_token(self):
        """生成用户token"""
        self.user_token = secrets.token_urlsafe(48)
        self.token_created_at = get_china_time()
        return self.user_token
    
    def revoke_user_token(self):
        """撤销用户token"""
        self.user_token = None
        self.token_created_at = None
    
    def get_accessible_whiteboards(self):
        """获取用户可以访问的所有白板"""
        from models.class_models import TeacherClass
        from models.whiteboard import Whiteboard
        
        accessible_whiteboards = []
        
        # 如果是教师，获取其管理的班级的白板
        if self.role == 'teacher':
            # 获取用户创建的班级
            owned_classes = Class.query.filter_by(teacher_id=self.id).all()
            for class_obj in owned_classes:
                class_whiteboards = Whiteboard.query.filter_by(
                    class_id=class_obj.id, 
                    is_active=True
                ).all()
                accessible_whiteboards.extend(class_whiteboards)
            
            # 获取用户加入的班级
            teacher_classes = TeacherClass.query.filter_by(
                teacher_id=self.id, 
                is_approved=True
            ).all()
            for tc in teacher_classes:
                class_whiteboards = Whiteboard.query.filter_by(
                    class_id=tc.class_id, 
                    is_active=True
                ).all()
                accessible_whiteboards.extend(class_whiteboards)
        
        return accessible_whiteboards