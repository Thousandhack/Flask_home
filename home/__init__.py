from flask import Flask
from config import config_map
from flask_session import Session
from flask_wtf import CSRFProtect
from flask_sqlalchemy import SQLAlchemy

import redis

# 数据库
db = SQLAlchemy()

# 获取redis数据库连接
redis_store = None


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

    # 初始化redis
    # 变量通过类的继承获取的
    global redis_store
    redis_store = redis.StrictRedis(host=config_class.REDIS_HOST, port=config_class.REDIS_PORT, db=0,
                                    password=config_class.REDIS_PASSWORD)

    # 利用flask-session，将session数据保存到redis中
    Session(app)

    # 为flask 补充csrf 防护  以钩子的方式
    CSRFProtect(app)

    # 注册蓝图
    # 特意在使用得时候再进行导入是为了避免循环导入
    from home import api
    app.register_blueprint(api.api, url_prefix="/api/v1.0")

    return app
