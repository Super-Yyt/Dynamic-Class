from extensions import db
from utils.time_utils import get_china_time, format_china_time

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    class_id = db.Column(db.Integer, db.ForeignKey('class.id'), nullable=True)
    title = db.Column(db.String(200))
    content = db.Column(db.Text, nullable=False)
    message_type = db.Column(db.String(20), default='text')
    created_at = db.Column(db.DateTime, default=get_china_time)
    is_read = db.Column(db.Boolean, default=False)
    
    sender = db.relationship('User', foreign_keys=[sender_id], backref=db.backref('sent_messages', lazy=True))
    receiver = db.relationship('User', foreign_keys=[receiver_id], backref=db.backref('received_messages', lazy=True))
    class_obj = db.relationship('Class', backref=db.backref('messages', lazy=True))
    
    def __repr__(self):
        return f'<Message {self.title}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'sender_id': self.sender_id,
            'receiver_id': self.receiver_id,
            'class_id': self.class_id,
            'title': self.title,
            'content': self.content,
            'message_type': self.message_type,
            'created_at': format_china_time(self.created_at),
            'is_read': self.is_read,
            'sender_name': self.sender.username if self.sender else None,
            'receiver_name': self.receiver.username if self.receiver else None,
            'class_name': self.class_obj.name if self.class_obj else None
        }