from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO
from flask_migrate import Migrate
from apscheduler.schedulers.background import BackgroundScheduler

# 初始化扩展
db = SQLAlchemy()
socketio = SocketIO()
migrate = Migrate()
scheduler = BackgroundScheduler()