from flask_script import Manager
from home import create_app, db
# 数据表迁移的执行者和解析人员
from flask_migrate import Migrate, MigrateCommand

# 创建falsk 应用对象
app = create_app("develop")
manager = Manager(app)

Migrate(app, db)
manager.add_command("db",MigrateCommand)

if __name__ == "__main__":
    """
    运行项目
    python manage.py runserver
    """
    manager.run()
