from flask import Flask
from config import config_map
from flask_sqlalchemy import SQLAlchemy

# 数据库
db = SQLAlchemy()


# 工厂模式
def create_app(config_name):
    """
    创建flask 的应用app对象
    :param config_name: str  配置模式的模式("develop","product")
    :return:
    """
    app = Flask(__name__)
    config_class = config_map.get(config_name)
    app.config.from_object(config_class)

    # 使用app 初始化db
    db.init_app(app)

    return app
