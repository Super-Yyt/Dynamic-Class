from flask import Flask
from config import Config
from extensions import db, socketio, migrate

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.config.update(
        SQLALCHEMY_ENGINE_OPTIONS={
            'pool_recycle': 300,
            'pool_pre_ping': True
        }
    )

    # 初始化扩展
    db.init_app(app)
    socketio.init_app(
        app, 
        cors_allowed_origins="*",
        logger=True,
        engineio_logger=True,
        async_mode='threading'
    )
    migrate.init_app(app, db)

    # 注册蓝图
    with app.app_context():
        from blueprints.auth import auth_bp
        from blueprints.main import main_bp
        from blueprints.classes import classes_bp
        from blueprints.whiteboards import whiteboards_bp
        from blueprints.tasks import tasks_bp
        from blueprints.assignments import assignments_bp
        from blueprints.announcements import announcements_bp
        from blueprints.api import api_bp
        from blueprints.settings import settings_bp
        from blueprints.notes import notes_bp
        from blueprints.web_notes import web_notes_bp
        from blueprints.developer import developer_bp

        app.register_blueprint(auth_bp)
        app.register_blueprint(main_bp)
        app.register_blueprint(classes_bp)
        app.register_blueprint(whiteboards_bp)
        app.register_blueprint(tasks_bp)
        app.register_blueprint(assignments_bp)
        app.register_blueprint(announcements_bp)
        app.register_blueprint(api_bp)
        app.register_blueprint(settings_bp)
        app.register_blueprint(notes_bp)
        app.register_blueprint(web_notes_bp)
        app.register_blueprint(developer_bp)

    # 初始化定时任务
    from utils.scheduler import scheduler_manager
    scheduler_manager.init_app(app)

    # 注册错误处理器
    from utils.error_handlers import register_error_handlers
    register_error_handlers(app)

    return app

app = create_app()

# 导入模型以确保它们被注册
from models import *

# 导入SocketIO事件处理
from events import socketio_events

if __name__ == '__main__':
    socketio.run(app, debug=True)