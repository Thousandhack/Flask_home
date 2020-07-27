from . import api
from home.utils.captcha.captcha import captcha
from home import redis_store, constants  # 导入redis 实例
from flask import current_app
from flask import jsonify


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
        return jsonify({"status": 500, "msg": "数据设置好状态码失败"})

    return jsonify()
