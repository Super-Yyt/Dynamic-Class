from apscheduler.schedulers.background import BackgroundScheduler
from utils.time_utils import get_china_time, format_china_time
from datetime import timedelta
from flask import jsonify, request, render_template

def register_error_handlers(app):
    """注册错误处理器"""
    
    @app.errorhandler(404)
    def not_found(error):
        if request.path.startswith('/api/'):
            return jsonify({'error': '接口不存在'}), 404
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_server_error(error):
        app.logger.error(f"服务器内部错误: {str(error)}")
        if request.path.startswith('/api/'):
            return jsonify({'error': '服务器内部错误'}), 500
        return render_template('errors/500.html'), 500

    @app.errorhandler(403)
    def forbidden(error):
        if request.path.startswith('/api/'):
            return jsonify({'error': '禁止访问'}), 403
        return render_template('errors/403.html'), 403

    @app.errorhandler(401)
    def unauthorized(error):
        if request.path.startswith('/api/'):
            return jsonify({'error': '未授权'}), 401
        return render_template('errors/401.html'), 401

    @app.errorhandler(400)
    def bad_request(error):
        if request.path.startswith('/api/'):
            return jsonify({'error': '请求参数错误'}), 400
        return render_template('errors/400.html'), 400