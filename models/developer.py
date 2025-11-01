from extensions import db
from utils.time_utils import get_china_time, format_china_time
import secrets

class Developer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    company = db.Column(db.String(200))
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default='active')
    created_at = db.Column(db.DateTime, default=get_china_time)
    
    user = db.relationship('User', backref=db.backref('developer_profile', lazy=True))
    apps = db.relationship('DeveloperApp', backref='developer', lazy=True)
    
    def __repr__(self):
        return f'<Developer {self.user.username}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'company': self.company,
            'description': self.description,
            'status': self.status,
            'created_at': format_china_time(self.created_at),
            'username': self.user.username if self.user else None
        }

class DeveloperApp(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    developer_id = db.Column(db.Integer, db.ForeignKey('developer.id'), nullable=False)
    app_name = db.Column(db.String(100), nullable=False)
    app_id = db.Column(db.String(50), unique=True, nullable=False)
    app_secret = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    callback_url = db.Column(db.String(200))
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    created_at = db.Column(db.DateTime, default=get_china_time)
    approved_at = db.Column(db.DateTime)
    
    def __repr__(self):
        return f'<DeveloperApp {self.app_name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'developer_id': self.developer_id,
            'app_name': self.app_name,
            'app_id': self.app_id,
            'description': self.description,
            'callback_url': self.callback_url,
            'status': self.status,
            'created_at': format_china_time(self.created_at),
            'approved_at': format_china_time(self.approved_at) if self.approved_at else None
        }
    
    @staticmethod
    def generate_app_id():
        """生成应用ID"""
        return f"app_{secrets.token_urlsafe(16)}"
    
    @staticmethod
    def generate_app_secret():
        """生成应用密钥"""
        return secrets.token_urlsafe(32)