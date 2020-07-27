import redis


class Config(object):
    """配置信息"""
    SECRET_KEY = "D391E2Ncoienw8d32nlhdeDFDFE4RBT"

    # 数据库
    # 数据库类型：// 登录账号：登录密码@数据库主机IP：数据库访问端口/数据库名称?charset=utf8
    SQLALCHEMY_DATABASE_URI = "mysql://root:123456@127.0.0.1:3306/home?charset=utf8"

    # 动态追踪修改设置，如未设置只会提示警告（工作中不要打开）
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    # redis 配置项
    REDIS_HOST = "127.0.0.1"
    REDIS_PORT = 6379
    REDIS_PASSWORD = "aaa"

    # session 配置 REDIS 数据库也可以配置其他服务器上的配置可以与下面redis配置相同
    SESSION_TYPE = "redis"
    SESSION_REDIS = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=0, password=REDIS_PASSWORD)  #
    SESSION_USE_SINER = True  # 对cookie中session_id进行隐藏处理
    PERMANENT_SESSION_LIFETIME = 86400  # session 数据有效期，单位秒


class DevelopmentConfig(Config):
    """开发模式的配置信息"""
    DEBUG = True


class ProductionConfig(Config):
    """生产环境配置信息"""
    pass


config_map = {
    "develop": DevelopmentConfig,
    "product": ProductionConfig
}
