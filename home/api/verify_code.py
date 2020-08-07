from . import api
from home.utils.captcha.captcha import captcha
from home.utils import constants
from home.utils.response_code import RET
from home import redis_store  # 导入redis 实例
from home import db
from home.libs.yuntongxun.sms import CCP
from home.celery_tasks.sms.tasks import send_sms
from home.models import User
from flask import current_app
from flask import make_response
from flask import request
from flask import jsonify
import random


@api.route("/image_codes/<image_code_id>")
def get_iamge_code(image_code_id):
    """
    获取图片验证码
    : params image_code_id:图片 验证码
    :return: 正常返回验证码图片 异常：返回json错误信息
    """
    # 业务逻辑处理
    # 生成验证码图片与编号保存到redis中
    # 名字 真实文本，图片数据
    name, text, image_data = captcha.generate_captcha()
    # 将验证码真实值与编号保存到redis中,设置有效期
    # redis:字符串，列表，哈希，set
    # “key”:"***"
    # redis命令设置图片验证码键值对
    # 设置键值对

    # 选用字符串类型
    # "image_code_编号1":"真实值"
    # redis_store.set("image_code_%s" % image_code_id, text)
    # # 设置过期时间
    # redis_store.setexpire("image_code_%s" % image_code_id, constants.IMAGE_CODE_REDIS_EXPIRES)
    # 设置值同时设置有效期
    try:
        redis_store.setex("image_code_%s" % image_code_id, constants.IMAGE_CODE_REDIS_EXPIRES, text)
    except Exception as e:
        # 记录日志
        current_app.logger.error()
        return jsonify({"status": RET.DATAERR, "msg": "设置状态码信息失败"})
    # 返回图片数据
    resp = make_response(image_data)
    resp.headers["Content-Type"] = "image/jpg"
    return resp


# GET /api/v1.0/sms_codes/<mobile>?image_code=xxxx&image_code_id=xxxx
@api.route("/sms_codes/<re(r'1[34578]\d{9}'):mobile>")
def get_sms_code(mobile):
    """
    获取短信验证码
    验证URL: http://127.0.0.1:5000/api/v1.0/sms_codes/18666951518?image_code=QNCV&image_code_id=11a98b32-6fb6-401d-b0d1-1b28f8566070
    验证步骤，首先在首页刷新图片验证码，然后获取image_code_id 和图片验证码
    在用postman向服务端发起get请求
    :return:
    """
    # 获取参数
    image_code = request.args.get("image_code")
    image_code_id = request.args.get("image_code_id")
    # 校验
    if not all([image_code, image_code_id]):
        # 表示参数不完整
        return jsonify(errno=RET.PARAMERR, errmsg="请求参数错误！")
    # 业务逻辑处理
    # 从redis中取出真实的图片验证码
    try:
        real_image_code = redis_store.get("image_code_%s" % image_code_id)
    except Exception as e:
        current_app.logger.error(e)
        # {"status": RET.DATAERR, "msg": "redis数据库异常"}
        return jsonify(errno=RET.DATAERR, errmsg="redis数据库异常")
    if real_image_code is None:
        # 表示图片验证码没有或者过期
        return jsonify(errno=RET.NODATA, errmsg="图片验证失效")

    # 删除图片验证码防止用户使用同一图片验证多次
    # try:
    #     redis_store.delete("image_code_%s" % image_code_id)
    # except Exception as e:
    #     current_app.logger.error(e)

    if real_image_code.lower() == image_code.lower():
        # 表示用户填写错误
        return jsonify(errno=RET.DATAERR, errmsg="图片验证码错误")
    # 判断手机号请求验证码60秒内，不接受处理
    try:
        send_flag = redis_store.get("send_sms_code_%s" % mobile)
    except Exception as e:
        current_app.logger.error(e)
    else:
        if send_flag is not None:
            # 表示在60秒之前有过发送的记录
            return jsonify(errno=RET.REQERR, errmsg="请求过于频繁，请一分钟后重试！")

    # 判断手机号是否存在，根据此结果是否产生短信验证码
    # db.session(User)
    try:
        user = User.query.filter_by(mobile=mobile).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DATAERR, errmsg="mysql数据库异常")
    if user is not None:
        # 表示手机号已存在
        return jsonify(errno=RET.DATAEXIST, errmsg="手机号已存在")
    # 返回值
    sms_code = "%06d" % random.randint(0, 999999)
    # 保存真实短信验证码
    try:
        redis_store.setex("sms_code_%s" % mobile, constants.SMS_CODE_REDIS_EXPIRES, sms_code)
        redis_store.setex("send_sms_code_%s" % mobile, constants.SEND_SMS_CODE_INTERVAL, 1)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DATAERR, errmsg="短信验证码异常")

    # 发送短信
    # try:
    #     ccp = CCP()
    #     result = ccp.send_template_sms(mobile, [sms_code, int(constants.SMS_CODE_REDIS_EXPIRES / 60)], 1)
    # except Exception as e:
    #     current_app.logger(e)
    #     return jsonify(errno=RET.THIRDERR, errmsg="发送异常！")

    # 使用异步的方式放松短信
    # 使用celery异步发送短信，delay函数调用后立即返回
    # sms_code.delay(mobile,[sms_code, int(constants.SMS_CODE_REDIS_EXPIRES / 60)], 1)

    # # 发送短信
    # # 使用celery异步发送短信, delay函数调用后立即返回（非阻塞）
    # send_sms.delay(mobile, [sms_code, int(constants.SMS_CODE_REDIS_EXPIRES/60)], 1)

    # # 返回异步任务的对象
    result_obj = send_sms.delay(mobile, [sms_code, int(constants.SMS_CODE_REDIS_EXPIRES / 60)], 1)
    print("hhhhh")
    print("123")
    print(result_obj)
    print(result_obj.id)
    print("23333")
    #
    # # 通过异步任务对象的get方法获取异步任务的结果, 默认get方法是阻塞的
    ret = result_obj.get()
    print("ret=%s" % ret)
    result = ret
    print("1111111111")

    # if result == 0:
    #     # 返回值
    #     return jsonify(errno=RET.OK, errmsg="发送成功，%s" % sms_code)
    # else:
    #     return jsonify(errno=RET.THIRDERR, errmsg="发送失败！")

    return jsonify(errno=RET.OK, errmsg="发送成功，%s" % sms_code)
