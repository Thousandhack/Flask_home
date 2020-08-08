# coding:utf-8


from celery import Celery
from home.celery_tasks import config

# 创建celery实例
# 定义celery对象
celery_app = Celery("home")

# 引入配置信息
celery_app.config_from_object("home.celery_tasks.config")

# 自动搜寻异步任务，加入celery任务
celery_app.autodiscover_tasks(["home.celery_tasks.sms"])


#
# pip install eventlet

# 运行celery 命令为

