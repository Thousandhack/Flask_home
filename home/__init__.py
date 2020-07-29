from flask import Flask
from config import config_map
from flask_session import Session
from flask_wtf import CSRFProtect
from flask_sqlalchemy import SQLAlchemy
from logging.handlers import RotatingFileHandler
from home.utils.commons import ReConverter  # 前端相关
import logging
import redis

# 数据库
db = SQLAlchemy()

# 获取redis数据库连接
redis_store = None

# 为flask补充防护机制
csrf = CSRFProtect()

#
# logging.error("11")  # 错误级别
# logging.warn("222")   # 警告级别
# logging.info()  # 消息提示级别
# logging.debug()  # 调试级别

# 设置日志等级
# 日志等级信息只有在项目运行不在DEBUG 的模式下，才生效控制日志等级的写入
logging.basicConfig(level=logging.DEBUG)  # 调试debug

# 创建日志记录器，指定日志保存路径、每个日志文件得最大大小、保存的日志个数上限
file_log_handler = RotatingFileHandler("logs/home.log", maxBytes=1024 * 1024 * 100, backupCount=10)

# 创建日志记录的格式
formatter = logging.Formatter('%(levelname)s %(filename)s:%(lineno)d %(message)s')
# 为刚创建的日志记录器设置日志记录格式
file_log_handler.setFormatter(formatter)
# 为全局的日志工具对象（flask app 使用的） 添加日志器
logging.getLogger().addHandler(file_log_handler)


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
    # CSRFProtect(app)

    # 为flask 添加自定义的转换器
    app.url_map.converters["re"] = ReConverter

    # 注册蓝图
    # 特意在使用得时候再进行导入是为了避免循环导入
    from home import api
    app.register_blueprint(api.api, url_prefix="/api/v1.0")

    # 注册提供静态文件的蓝图
    from home.web_html import html
    app.register_blueprint(html)

    return app
