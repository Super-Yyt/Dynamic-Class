from extensions import db
from utils.time_utils import get_china_time, format_china_time

class Class(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    code = db.Column(db.String(10), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=get_china_time)
    teacher_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    teacher = db.relationship('User', backref=db.backref('classes_taught', lazy=True))
    
    def __repr__(self):
        return f'<Class {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'code': self.code,
            'created_at': format_china_time(self.created_at),
            'teacher_id': self.teacher_id,
            'teacher_name': self.teacher.username if self.teacher else None
        }

class StudentClass(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    class_id = db.Column(db.Integer, db.ForeignKey('class.id'), nullable=False)
    joined_at = db.Column(db.DateTime, default=get_china_time)
    
    student = db.relationship('User', backref=db.backref('enrolled_classes', lazy=True))
    class_obj = db.relationship('Class', backref=db.backref('enrolled_students', lazy=True))
    
    def __repr__(self):
        return f'<StudentClass student:{self.student_id} class:{self.class_id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'class_id': self.class_id,
            'joined_at': format_china_time(self.joined_at),
            'student_name': self.student.username if self.student else None,
            'class_name': self.class_obj.name if self.class_obj else None
        }

class TeacherClass(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    class_id = db.Column(db.Integer, db.ForeignKey('class.id'), nullable=False)
    assigned_subjects = db.Column(db.String(500))
    is_approved = db.Column(db.Boolean, default=False)
    joined_at = db.Column(db.DateTime, default=get_china_time)
    
    teacher = db.relationship('User', backref=db.backref('teaching_classes', lazy=True))
    class_obj = db.relationship('Class', backref=db.backref('teaching_teachers', lazy=True))
    
    def __repr__(self):
        return f'<TeacherClass teacher:{self.teacher_id} class:{self.class_id}>'
    
    def get_assigned_subjects_list(self):
        if self.assigned_subjects:
            return [subject.strip() for subject in self.assigned_subjects.split(',')]
        return []

class ClassSubject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    class_id = db.Column(db.Integer, db.ForeignKey('class.id'), nullable=False)
    subject_name = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=get_china_time)
    
    class_obj = db.relationship('Class', backref=db.backref('subjects', lazy=True, cascade='all, delete-orphan'))
    
    def __repr__(self):
        return f'<ClassSubject {self.subject_name}>'