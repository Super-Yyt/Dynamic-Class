from extensions import db
from utils.time_utils import get_china_time, format_china_time

class Announcement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    whiteboard_id = db.Column(db.Integer, db.ForeignKey('whiteboard.id'), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=get_china_time)
    is_long_term = db.Column(db.Boolean, default=False)
    
    whiteboard = db.relationship('Whiteboard', backref=db.backref('announcements', lazy=True))
    teacher = db.relationship('User', foreign_keys=[teacher_id], backref=db.backref('created_announcements', lazy=True))
    
    def __repr__(self):
        return f'<Announcement {self.title}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'whiteboard_id': self.whiteboard_id,
            'teacher_id': self.teacher_id,
            'teacher_name': self.teacher.username if self.teacher else None,
            'created_at': format_china_time(self.created_at),
            'is_long_term': self.is_long_term,
            'whiteboard_name': self.whiteboard.name if self.whiteboard else None
        }