# coding:utf-8

from home.celery_tasks.main import celery_app
from home.libs.yuntongxun.sms import CCP


#
# @celery_app.task
# def send_sms(to, datas, temp_id):
#     """发送短信的异步任务"""
#     pass


@celery_app.task
def send_sms(to, datas, temp_id):
    """发送短信的异步任务"""
    ccp = CCP()
    try:
        result = ccp.send_template_sms(to, datas, temp_id)
    except Exception as e:
        result = -2
    return result
