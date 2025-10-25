from flask import Blueprint, render_template, redirect, url_for, session, request, flash, jsonify
from extensions import db, socketio
from models.user import User
from models.class_models import Class, StudentClass, TeacherClass, ClassSubject
from utils.auth_utils import login_required, teacher_required
from utils.code_utils import generate_class_code

classes_bp = Blueprint('classes', __name__, url_prefix='/classes')

@classes_bp.route('/')
@login_required
def classes():
    user = db.session.get(User, session['user_id'])
    
    if user.role == 'teacher':
        created_classes = Class.query.filter_by(teacher_id=user.id).all()
        teacher_classes = TeacherClass.query.filter_by(teacher_id=user.id, is_approved=True).all()
        joined_classes = [tc for tc in teacher_classes]
        
        return render_template('classes.html', 
                             username=session.get('username'),
                             role=session.get('role'),
                             avatar=session.get('avatar'),
                             created_classes=created_classes,
                             joined_classes=joined_classes)
    else:
        classes = []
        return render_template('classes.html', 
                             username=session.get('username'),
                             role=session.get('role'),
                             avatar=session.get('avatar'),
                             classes=classes)

@classes_bp.route('/create', methods=['GET', 'POST'])
@login_required
@teacher_required
def create_class():
    user = db.session.get(User, session['user_id'])
    
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        
        if not name:
            flash('班级名称不能为空', 'error')
            return render_template('create_class.html')
        
        code = generate_class_code()
        while Class.query.filter_by(code=code).first():
            code = generate_class_code()
        
        new_class = Class(
            name=name,
            description=description,
            code=code,
            teacher_id=user.id
        )
        
        try:
            db.session.add(new_class)
            db.session.commit()
            flash(f'班级 "{name}" 创建成功！班级代码: {code}', 'success')
            return redirect(url_for('classes.view_class', class_id=new_class.id))
        except Exception as e:
            db.session.rollback()
            flash('创建班级时发生错误', 'error')
            return render_template('create_class.html')
    
    return render_template('create_class.html', 
                         username=session.get('username'),
                         role=session.get('role'),
                         avatar=session.get('avatar'))

@classes_bp.route('/<int:class_id>')
@login_required
def view_class(class_id):
    class_obj = Class.query.get_or_404(class_id)
    user = db.session.get(User, session['user_id'])
    
    # 检查权限：班级创建者 或 被分配了学科的授课老师
    is_owner = class_obj.teacher_id == user.id
    is_approved_teacher = TeacherClass.query.filter_by(
        class_id=class_id, 
        teacher_id=user.id, 
        is_approved=True
    ).first()
    
    has_assigned_subjects = is_approved_teacher and is_approved_teacher.assigned_subjects
    
    if not (is_owner or (is_approved_teacher and has_assigned_subjects)):
        flash('您没有权限查看这个班级', 'error')
        return redirect(url_for('classes.classes'))
    
    return render_template('view_class.html', 
                         username=session.get('username'),
                         role=session.get('role'),
                         avatar=session.get('avatar'),
                         class_obj=class_obj,
                         is_owner=is_owner)

@classes_bp.route('/join', methods=['POST'])
@login_required
@teacher_required
def join_class():
    user = db.session.get(User, session['user_id'])
    
    class_code = request.form.get('class_code')
    if not class_code:
        flash('请输入班级代码', 'error')
        return redirect(url_for('classes.classes'))
    
    class_obj = Class.query.filter_by(code=class_code).first()
    if not class_obj:
        flash('班级代码无效', 'error')
        return redirect(url_for('classes.classes'))
    
    existing_join = TeacherClass.query.filter_by(class_id=class_obj.id, teacher_id=user.id).first()
    if existing_join:
        flash('您已经加入该班级', 'info')
        return redirect(url_for('classes.classes'))
    
    teacher_class = TeacherClass(
        teacher_id=user.id,
        class_id=class_obj.id,
        is_approved=False
    )
    
    try:
        db.session.add(teacher_class)
        db.session.commit()
        flash(f'已申请加入班级 {class_obj.name}，等待班主任批准', 'success')
    except Exception as e:
        db.session.rollback()
        flash('加入班级失败', 'error')
    
    return redirect(url_for('classes.classes'))