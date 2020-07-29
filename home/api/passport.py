from . import api
from flask import request, jsonify
from flask import current_app, session
from home.utils.response_code import RET
from home.models import User
from home import redis_store  # 导入redis 实例
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash, check_password_hash
from home import db
import re


@api.route("/users/", methods=["POST"])
def register():
    """
    注册
    请求的参数：手机号、短信验证码、密码
    参数格式：json
    :return:
    """
    # 获取请求的json数据，返回字典
    req_dict = request.get_json()
    mobile = req_dict.get("mobile")
    sms_code = req_dict.get("sms_code")
    password = req_dict.get("password")

    # 校验参数
    if not all([mobile, sms_code, password]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不完整")

    # 判断手机格式
    if not re.match(r"1[345678]\d{9}", mobile):
        # 表示格式不对
        return jsonify(errno=RET.PARAMERR, errmsg="手机格式错误")
    # 从redis中取出短信验证码
    try:
        real_sms_code = redis_store.get("sms_code_%s" % mobile)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(error=RET.DBERR, errmsg="读取真实短信验证码异常")
    # 判断短信验证码是否过期
    if real_sms_code is None:
        return jsonify(error=RET.NODATA, errmsg="短信验证码失效")
    # 删除redis中的短信验证码，防止重复使用校验
    # try:
    #     redis_store.delete("sms_code_%s" %mobile)
    # except Exception as e:
    #     current_app.logger.error(e)
    # 判断用户填写短信验证码的正确性
    # print(real_sms_code, type(real_sms_code))
    if real_sms_code.decode('utf-8') != sms_code:
        return jsonify(error=RET.DATAERR, errmsg="短信验证码错误")
    # 判断用户的手机号是否注册过
    # try:
    #     user = User.query.filter_by(mobile=mobile).first()
    # except Exception as e:
    #     current_app.logger.error(e)
    # else:
    #     if user is not  None:
    #         # 表示手机号已经存在
    #         return jsonify(errno=RET.DATAEXIST,errmsg="手机号已存在")

    # 盐值   salt

    #  注册
    #  用户1   password="123456" + "abc"   sha1   abc$hxosifodfdoshfosdhfso
    #  用户2   password="123456" + "def"   sha1   def$dfhsoicoshdoshfosidfs
    # 比较安全用sha256
    # 用户登录  password ="123456"  "abc"  sha256      sha1   hxosufodsofdihsofho

    # 保存用户的注册数据到数据库中
    user = User(name=mobile, mobile=mobile)
    # user.generate_password_hash(password)
    user.password = password  # 设置属性
    # print(user.password)  # 读取属性
    # 保存用户的注册数据到数据库中
    try:
        db.session.add(user)
        db.session.commit()
    except IntegrityError as e:
        # 出错的话就回滚
        db.session.rollback()
        # 表示手机号出现重复值
        current_app.logger.error(e)
        return jsonify(errno=RET.DATAEXIST, errmsg="手机号已存在")
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(error=RET.DBERR, errmsg="查询数据库异常")
    # 保存登录状态到session中
    session['name'] = user.name
    session['mobile'] = user.mobile
    session['user_id'] = user.id

    # 返回结果
    return jsonify(errno=RET.OK, errmsg="注册成功！")
