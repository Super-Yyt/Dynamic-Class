from extensions import db
from utils.time_utils import get_china_time, format_china_time

class SystemSetting(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False)
    value = db.Column(db.Text)
    description = db.Column(db.String(200))
    updated_at = db.Column(db.DateTime, default=get_china_time, onupdate=get_china_time)
    
    def __repr__(self):
        return f'<SystemSetting {self.key}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'key': self.key,
            'value': self.value,
            'description': self.description,
            'updated_at': format_china_time(self.updated_at)
        }