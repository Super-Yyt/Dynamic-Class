from functools import wraps
from flask import jsonify
from app import db
from sqlalchemy.exc import SQLAlchemyError

def handle_db_errors(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except SQLAlchemyError as e:
            db.session.rollback()
            current_app.logger.error(f"数据库错误: {str(e)}")
            return jsonify({'error': '数据库操作失败'}), 500
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"未知错误: {str(e)}")
            return jsonify({'error': '服务器内部错误'}), 500
    return decorated_function