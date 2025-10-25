from extensions import db
from utils.time_utils import get_china_time, format_china_time

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    priority = db.Column(db.Integer, default=1)
    action_id = db.Column(db.Integer)
    whiteboard_id = db.Column(db.Integer, db.ForeignKey('whiteboard.id'), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    subject = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=get_china_time)
    due_date = db.Column(db.DateTime, nullable=True)
    is_completed = db.Column(db.Boolean, default=False)
    is_acknowledged = db.Column(db.Boolean, default=False)
    
    whiteboard = db.relationship('Whiteboard', backref=db.backref('tasks', lazy=True))
    teacher = db.relationship('User', foreign_keys=[teacher_id], backref=db.backref('created_tasks', lazy=True))
    
    def __repr__(self):
        return f'<Task {self.title}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'priority': self.priority,
            'action_id': self.action_id,
            'whiteboard_id': self.whiteboard_id,
            'teacher_id': self.teacher_id,
            'teacher_name': self.teacher.username if self.teacher else None,
            'subject': self.subject,
            'created_at': format_china_time(self.created_at),
            'due_date': format_china_time(self.due_date),
            'is_completed': self.is_completed,
            'is_acknowledged': self.is_acknowledged,
            'whiteboard_name': self.whiteboard.name if self.whiteboard else None
        }