from apscheduler.schedulers.background import BackgroundScheduler
from utils.time_utils import get_china_time, format_china_time
from datetime import timedelta

class SchedulerManager:
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.app = None
    
    def init_app(self, app):
        self.app = app
        self.setup_jobs()
        if not self.scheduler.running:
            self.scheduler.start()
    
    def setup_jobs(self):
        self.scheduler.add_job(
            func=self.cleanup_offline_whiteboards,
            trigger="interval",
            minutes=1
        )
    
    def cleanup_offline_whiteboards(self):
        """清理长时间没有心跳的白板状态"""
        if not self.app:
            return
            
        with self.app.app_context():
            from extensions import db, socketio
            from models.whiteboard import Whiteboard, WhiteboardStatusHistory
            
            try:
                cutoff_time = get_china_time() - timedelta(minutes=15/60)
                offline_whiteboards = Whiteboard.query.filter(
                    Whiteboard.is_online == True,
                    Whiteboard.last_heartbeat < cutoff_time
                ).all()
                
                for whiteboard in offline_whiteboards:
                    whiteboard.is_online = False
                    db.session.commit()
                    
                    status_history = WhiteboardStatusHistory(
                        whiteboard_id=whiteboard.id,
                        is_online=False
                    )
                    db.session.add(status_history)
                    db.session.commit()
                    
                    socketio.emit('whiteboard_status_update', {
                        'whiteboard_id': whiteboard.id,
                        'is_online': False,
                        'last_heartbeat': format_china_time(whiteboard.last_heartbeat)
                    }, room=f"teacher_{whiteboard.class_obj.teacher_id}")
                    
                if offline_whiteboards:
                    self.app.logger.info(f"清理了 {len(offline_whiteboards)} 个离线白板状态")
            except Exception as e:
                self.app.logger.error(f"清理离线白板状态时出错: {str(e)}")

# 创建全局实例
scheduler_manager = SchedulerManager()

# 兼容旧代码
def init_scheduler(app):
    scheduler_manager.init_app(app)