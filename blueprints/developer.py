from flask import Blueprint, render_template, redirect, url_for, session, request, flash, jsonify
from extensions import db
from models.user import User
from models.developer import Developer, DeveloperApp
from utils.auth_utils import login_required
from utils.casdoor_utils import get_casdoor_auth_url
import secrets

developer_bp = Blueprint('developer', __name__, url_prefix='/developer')

@developer_bp.route('/')
@login_required
def developer_console():
    """开发者控制台"""
    user = db.session.get(User, session['user_id'])
    
    # 检查用户组织是否为developer
    if user.organization != 'developer':
        flash('请使用开发者账号访问开发者控制台', 'error')
        return redirect(url_for('developer.casdoor_login_developer'))
    
    # 检查用户是否已经注册开发者
    developer = Developer.query.filter_by(user_id=user.id).first()
    
    if not developer:
        # 如果用户还不是开发者，重定向到开发者注册页面
        return redirect(url_for('developer.register'))
    
    # 获取开发者的所有应用
    apps = DeveloperApp.query.filter_by(developer_id=developer.id).all()
    
    return render_template('developer/console.html',
                         username=session.get('username'),
                         role=session.get('role'),
                         avatar=session.get('avatar'),
                         developer=developer,
                         apps=apps)

@developer_bp.route('/register', methods=['GET', 'POST'])
@login_required
def register():
    """开发者注册"""
    user = db.session.get(User, session['user_id'])
    
    # 检查用户组织是否为developer
    if user.organization != 'developer':
        flash('请使用开发者账号登录后再注册开发者', 'error')
        return redirect(url_for('developer.casdoor_login_developer'))
    
    # 检查用户是否已经是开发者
    existing_developer = Developer.query.filter_by(user_id=user.id).first()
    if existing_developer:
        flash('您已经是开发者', 'info')
        return redirect(url_for('developer.developer_console'))
    
    if request.method == 'POST':
        company = request.form.get('company')
        description = request.form.get('description')
        
        if not company:
            flash('请填写公司/组织名称', 'error')
            return render_template('developer/register.html')
        
        # 创建开发者记录
        developer = Developer(
            user_id=user.id,
            company=company,
            description=description
        )
        
        try:
            db.session.add(developer)
            db.session.commit()
            flash('开发者注册成功！', 'success')
            return redirect(url_for('developer.developer_console'))
        except Exception as e:
            db.session.rollback()
            flash('注册失败，请稍后重试', 'error')
    
    return render_template('developer/register.html',
                         username=session.get('username'),
                         role=session.get('role'),
                         avatar=session.get('avatar'))

@developer_bp.route('/apps/create', methods=['GET', 'POST'])
@login_required
def create_app():
    """创建新应用"""
    user = db.session.get(User, session['user_id'])
    
    # 检查用户组织是否为developer
    if user.organization != 'developer':
        flash('请使用开发者账号访问此功能', 'error')
        return redirect(url_for('developer.casdoor_login_developer'))
    
    developer = Developer.query.filter_by(user_id=user.id).first()
    
    if not developer:
        flash('请先注册开发者账号', 'error')
        return redirect(url_for('developer.register'))
    
    if request.method == 'POST':
        app_name = request.form.get('app_name')
        description = request.form.get('description')
        callback_url = request.form.get('callback_url')
        
        if not app_name:
            flash('请填写应用名称', 'error')
            return render_template('developer/create_app.html')
        
        # 生成应用ID和密钥
        app_id = DeveloperApp.generate_app_id()
        app_secret = DeveloperApp.generate_app_secret()
        
        app = DeveloperApp(
            developer_id=developer.id,
            app_name=app_name,
            app_id=app_id,
            app_secret=app_secret,
            description=description,
            callback_url=callback_url,
            status='approved'  # 暂时设为自动批准
        )
        
        try:
            db.session.add(app)
            db.session.commit()
            
            # 显示应用凭证（只显示一次）
            flash(f'应用创建成功！请保存您的应用凭证', 'success')
            return render_template('developer/app_credentials.html',
                                 username=session.get('username'),
                                 role=session.get('role'),
                                 avatar=session.get('avatar'),
                                 app=app,
                                 app_secret=app_secret)  # 只在这里显示一次
            
        except Exception as e:
            db.session.rollback()
            flash('创建应用失败', 'error')
    
    return render_template('developer/create_app.html',
                         username=session.get('username'),
                         role=session.get('role'),
                         avatar=session.get('avatar'))

@developer_bp.route('/apps/<app_id>/reset-secret', methods=['POST'])
@login_required
def reset_app_secret(app_id):
    """重置应用密钥"""
    user = db.session.get(User, session['user_id'])
    
    # 检查用户组织是否为developer
    if user.organization != 'developer':
        return jsonify({'error': '请使用开发者账号访问此功能'}), 403
    
    developer = Developer.query.filter_by(user_id=user.id).first()
    if not developer:
        return jsonify({'error': '开发者不存在'}), 403
    
    app = DeveloperApp.query.filter_by(app_id=app_id, developer_id=developer.id).first()
    if not app:
        return jsonify({'error': '应用不存在'}), 404
    
    try:
        new_secret = DeveloperApp.generate_app_secret()
        app.app_secret = new_secret
        db.session.commit()
        
        return jsonify({
            'success': True,
            'new_secret': new_secret
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': '重置失败'}), 500

@developer_bp.route('/apps/<app_id>/delete', methods=['POST'])
@login_required
def delete_app(app_id):
    """删除应用"""
    user = db.session.get(User, session['user_id'])
    
    # 检查用户组织是否为developer
    if user.organization != 'developer':
        return jsonify({'error': '请使用开发者账号访问此功能'}), 403
    
    developer = Developer.query.filter_by(user_id=user.id).first()
    if not developer:
        return jsonify({'error': '开发者不存在'}), 403
    
    app = DeveloperApp.query.filter_by(app_id=app_id, developer_id=developer.id).first()
    if not app:
        return jsonify({'error': '应用不存在'}), 404
    
    try:
        db.session.delete(app)
        db.session.commit()
        
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': '删除失败'}), 500

@developer_bp.route('/auth/casdoor')
def casdoor_login_developer():
    """开发者Casdoor登录"""
    auth_url = get_casdoor_auth_url('developer')
    return redirect(auth_url)