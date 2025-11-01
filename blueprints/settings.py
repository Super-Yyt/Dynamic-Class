from flask import Blueprint, render_template, redirect, url_for, session, request, flash, jsonify
from extensions import db
from models.user import User
from models.class_models import Class, TeacherClass, ClassSubject
from utils.auth_utils import login_required, teacher_required
from smtp import email_sender

settings_bp = Blueprint('settings', __name__)

@settings_bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    user = db.session.get(User, session['user_id'])
    
    # 处理表单提交
    if request.method == 'POST':
        form_type = request.form.get('form_type')
        
        if form_type == 'subjects':
            # 处理科目设置
            subjects = request.form.get('subjects', '')
            # 这里需要添加保存科目设置的逻辑
            # 例如: user.subjects = subjects
            # db.session.commit()
            # 已废弃
            flash('科目设置已更新', 'success')
            
        elif form_type == 'join_class':
            # 处理加入班级
            class_code = request.form.get('class_code', '').strip()
            if not class_code:
                flash('请输入班级代码', 'error')
                return redirect(url_for('settings.settings'))
            
            # 查找班级
            class_obj = Class.query.filter_by(code=class_code).first()
            if not class_obj:
                flash('班级代码不存在，请检查后重试', 'error')
                return redirect(url_for('settings.settings'))
            
            # 检查是否已经加入
            existing_join = TeacherClass.query.filter_by(
                teacher_id=user.id, 
                class_id=class_obj.id
            ).first()
            
            if existing_join:
                flash('您已经加入过这个班级了', 'warning')
                return redirect(url_for('settings.settings'))
            
            # 检查是否是班级创建者
            if class_obj.teacher_id == user.id:
                flash('您是这个班级的创建者，无需加入', 'info')
                return redirect(url_for('settings.settings'))
            
            # 创建教师班级关联
            teacher_class = TeacherClass(
                teacher_id=user.id,
                class_id=class_obj.id,
                is_approved=False  # 需要班级创建者批准
            )
            
            try:
                db.session.add(teacher_class)
                db.session.commit()
                flash(f'已申请加入班级: {class_obj.name}，等待创建者批准', 'success')
            except Exception as e:
                db.session.rollback()
                flash('加入班级失败，请稍后重试', 'error')
    
    # 获取用户已加入的班级
    teaching_classes = []
    if user.role == 'teacher':
        teacher_classes = TeacherClass.query.filter_by(teacher_id=user.id).all()
        for tc in teacher_classes:
            class_info = {
                'id': tc.class_obj.id,
                'name': tc.class_obj.name,
                'code': tc.class_obj.code,
                'is_approved': tc.is_approved,
                'assigned_subjects': tc.assigned_subjects or '未分配'
            }
            teaching_classes.append(class_info)
    token=user.user_token
    return render_template('settings.html',
                         username=session.get('username'),
                         role=session.get('role'),
                         avatar=session.get('avatar'),
                         user=user,
                         teaching_classes=teaching_classes,
                         token=token)

@settings_bp.route('/classes/<int:class_id>/settings')
@login_required
@teacher_required
def class_settings(class_id):
    class_obj = Class.query.get_or_404(class_id)
    user = db.session.get(User, session['user_id'])
    
    if class_obj.teacher_id != user.id:
        flash('只有班主任可以访问班级设置', 'error')
        return redirect(url_for('classes.view_class', class_id=class_id))
    
    class_subjects = ClassSubject.query.filter_by(class_id=class_id).all()
    class_subjects_str = ', '.join([subject.subject_name for subject in class_subjects])
    class_subjects_list = [subject.subject_name for subject in class_subjects]
    
    teaching_teachers = TeacherClass.query.filter_by(class_id=class_id).all()
    
    return render_template('class_settings.html',
                         username=session.get('username'),
                         role=session.get('role'),
                         avatar=session.get('avatar'),
                         class_obj=class_obj,
                         class_subjects=class_subjects_str,
                         class_subjects_list=class_subjects_list,
                         teaching_teachers=teaching_teachers)

@settings_bp.route('/classes/<int:class_id>/subjects', methods=['POST'])
@login_required
@teacher_required
def update_class_subjects(class_id):
    class_obj = Class.query.get_or_404(class_id)
    user = db.session.get(User, session['user_id'])
    
    if class_obj.teacher_id != user.id:
        flash('只有班主任可以修改班级学科', 'error')
        return redirect(url_for('settings.class_settings', class_id=class_id))
    
    subjects_str = request.form.get('subjects', '')
    
    try:
        ClassSubject.query.filter_by(class_id=class_id).delete()
        
        if subjects_str:
            subjects_list = [subject.strip() for subject in subjects_str.split(',') if subject.strip()]
            for subject_name in subjects_list:
                class_subject = ClassSubject(class_id=class_id, subject_name=subject_name)
                db.session.add(class_subject)
        
        db.session.commit()
        flash('班级学科设置已更新', 'success')
    except Exception as e:
        db.session.rollback()
        flash('更新班级学科失败', 'error')
    
    return redirect(url_for('settings.class_settings', class_id=class_id))

@settings_bp.route('/classes/<int:class_id>/invite', methods=['POST'])
@login_required
@teacher_required
def invite_teachers(class_id):
    class_obj = Class.query.get_or_404(class_id)
    user = db.session.get(User, session['user_id'])
    
    if class_obj.teacher_id != user.id:
        flash('只有班主任可以邀请老师', 'error')
        return redirect(url_for('settings.class_settings', class_id=class_id))
    
    teacher_emails_text = request.form.get('teacher_emails', '')
    teacher_emails = [email.strip() for email in teacher_emails_text.split('\n') if email.strip()]
    
    success_count = 0
    fail_count = 0
    
    for email in teacher_emails:
        try:
            teacher_user = User.query.filter_by(email=email, role='teacher').first()
            is_existing_user = teacher_user is not None
            
            if email_sender.send_invitation_email(
                email, 
                class_obj.name, 
                class_obj.code,
                user.username,
                is_existing_user
            ):
                success_count += 1
            else:
                fail_count += 1
                
        except Exception as e:
            fail_count += 1
    
    if success_count > 0:
        flash(f'成功发送 {success_count} 封邀请邮件', 'success')
    if fail_count > 0:
        flash(f'发送 {fail_count} 封邀请邮件失败', 'error')
    
    return redirect(url_for('settings.class_settings', class_id=class_id))

@settings_bp.route('/classes/<int:class_id>/teachers/<int:teacher_id>/approve', methods=['POST'])
@login_required
@teacher_required
def approve_teacher(class_id, teacher_id):
    class_obj = Class.query.get_or_404(class_id)
    user = db.session.get(User, session['user_id'])
    
    if class_obj.teacher_id != user.id:
        flash('只有班主任可以批准老师', 'error')
        return redirect(url_for('settings.class_settings', class_id=class_id))
    
    teacher_class = TeacherClass.query.filter_by(class_id=class_id, teacher_id=teacher_id).first()
    if teacher_class:
        teacher_class.is_approved = True
        db.session.commit()
        flash('老师已批准加入班级', 'success')
    
    return redirect(url_for('settings.class_settings', class_id=class_id))

@settings_bp.route('/classes/<int:class_id>/teachers/<int:teacher_id>/subjects', methods=['POST'])
@login_required
@teacher_required
def update_teacher_subjects(class_id, teacher_id):
    class_obj = Class.query.get_or_404(class_id)
    user = db.session.get(User, session['user_id'])
    
    if class_obj.teacher_id != user.id:
        flash('只有班主任可以分配学科', 'error')
        return redirect(url_for('settings.class_settings', class_id=class_id))
    
    teacher_class = TeacherClass.query.filter_by(class_id=class_id, teacher_id=teacher_id).first()
    if teacher_class and teacher_class.is_approved:
        selected_subjects = request.form.getlist('subjects')
        teacher_class.assigned_subjects = ','.join(selected_subjects)
        db.session.commit()
        flash('老师学科分配已更新', 'success')
    
    return redirect(url_for('settings.class_settings', class_id=class_id))

@settings_bp.route('/classes/<int:class_id>/teachers/<int:teacher_id>/remove', methods=['POST'])
@login_required
@teacher_required
def remove_teacher(class_id, teacher_id):
    class_obj = Class.query.get_or_404(class_id)
    user = db.session.get(User, session['user_id'])
    
    if class_obj.teacher_id != user.id:
        flash('只有班主任可以移除老师', 'error')
        return redirect(url_for('settings.class_settings', class_id=class_id))
    
    teacher_class = TeacherClass.query.filter_by(class_id=class_id, teacher_id=teacher_id).first()
    if teacher_class:
        db.session.delete(teacher_class)
        db.session.commit()
        flash('老师已从班级移除', 'success')
    
    return redirect(url_for('settings.class_settings', class_id=class_id))

# 添加退出班级的路由
@settings_bp.route('/classes/<int:class_id>/leave', methods=['POST'])
@login_required
@teacher_required
def leave_class(class_id):
    user = db.session.get(User, session['user_id'])
    
    teacher_class = TeacherClass.query.filter_by(
        class_id=class_id, 
        teacher_id=user.id
    ).first()
    
    if teacher_class:
        try:
            db.session.delete(teacher_class)
            db.session.commit()
            flash('已成功退出班级', 'success')
        except Exception as e:
            db.session.rollback()
            flash('退出班级失败', 'error')
    else:
        flash('您未加入该班级', 'warning')
    
    return redirect(url_for('settings.settings'))

@settings_bp.route('/generate-user-token', methods=['POST'])
@login_required
@teacher_required
def generate_user_token():
    """生成用户token"""
    user = db.session.get(User, session['user_id'])
    
    try:
        token = user.generate_user_token()
        db.session.commit()
        flash('用户令牌生成成功！', 'success')
    except Exception as e:
        db.session.rollback()
        flash('生成令牌失败，请稍后重试', 'error')
    
    return redirect(url_for('settings.settings'))

@settings_bp.route('/reset-user-token', methods=['POST'])
@login_required
@teacher_required
def reset_user_token():
    """重置用户token"""
    user = db.session.get(User, session['user_id'])
    
    try:
        token = user.generate_user_token()
        db.session.commit()
        flash('用户令牌已重置！', 'success')
    except Exception as e:
        db.session.rollback()
        flash('重置令牌失败，请稍后重试', 'error')
    
    return redirect(url_for('settings.settings'))

@settings_bp.route('/revoke-user-token', methods=['POST'])
@login_required
@teacher_required
def revoke_user_token():
    """撤销用户token"""
    user = db.session.get(User, session['user_id'])
    
    try:
        user.revoke_user_token()
        db.session.commit()
        flash('用户令牌已撤销', 'success')
    except Exception as e:
        db.session.rollback()
        flash('撤销令牌失败，请稍后重试', 'error')
    
    return redirect(url_for('settings.settings'))

@settings_bp.route('/api/user-token')
@login_required
@teacher_required
def get_user_token_api():
    """获取用户token的API端点"""
    user = db.session.get(User, session['user_id'])
    
    if not user.user_token:
        return jsonify({'error': '用户令牌不存在'}), 404
    
    return jsonify({
        'success': True,
        'user_token': user.user_token
    })