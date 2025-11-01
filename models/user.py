from extensions import db
from utils.time_utils import get_china_time, format_china_time

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
            'last_login': format_china_time(self.last_login)
        }