from celery import Celery
from home.libs.yuntongxun.sms import CCP

# 定义celery 对象
celery_app = Celery("home", broker="redis://127.0.0.1:6379/2")


#
@celery_app.task
def send_sms(to, datas, tmp_id):
    """发送短信的异步任务"""
    ccp = CCP()
    ccp.send_template_sms(to, datas, tmp_id)
