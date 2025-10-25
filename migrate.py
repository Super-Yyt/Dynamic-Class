import os
import sys
from flask_migrate import Migrate, migrate, upgrade, init, downgrade

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db

def init_migration():
    """初始化迁移环境"""
    with app.app_context():
        init()
        print("迁移环境初始化完成")

def create_migration(message="auto migration"):
    """创建新的迁移"""
    with app.app_context():
        migrate(message=message)
        print(f"迁移文件已创建: {message}")

def apply_migration():
    """应用迁移到数据库"""
    with app.app_context():
        upgrade()
        print("迁移已应用到数据库")

def rollback_migration():
    """回滚迁移"""
    with app.app_context():
        downgrade()
        print("迁移已回滚")

def show_status():
    """显示当前迁移状态"""
    with app.app_context():
        from flask_migrate import current, history
        print("当前迁移状态:")
        print("Current:", current())
        print("History:")
        for h in history():
            print(f"  {h}")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("用法:")
        print("  python migrate.py init      # 初始化迁移环境")
        print("  python migrate.py create    # 创建迁移文件")
        print("  python migrate.py apply     # 应用迁移")
        print("  python migrate.py rollback  # 回滚迁移")
        print("  python migrate.py status    # 查看状态")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == 'init':
        init_migration()
    elif command == 'create':
        message = sys.argv[2] if len(sys.argv) > 2 else "auto migration"
        create_migration(message)
    elif command == 'apply':
        apply_migration()
    elif command == 'rollback':
        rollback_migration()
    elif command == 'status':
        show_status()
    else:
        print(f"未知命令: {command}")
        sys.exit(1)