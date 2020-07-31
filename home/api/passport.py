from . import api
from flask import request, jsonify
from flask import current_app, session
from home.utils.response_code import RET
from home.utils import constants
from home.models import User
from home import redis_store  # 导入redis 实例
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash, check_password_hash
from home import db
import re


@api.route("/users", methods=["POST"])
def register():
    """
    注册
    http://127.0.0.1:5000/api/v1.0/users/
    请求的参数：手机号、短信验证码、密码
    参数格式：json
    {
        "mobile":"18611111111",
        "sms_code":"404989",
        "password":"123456"
        }
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


@api.route("/sessions", methods=["POST"])
def login():
    """
    用户登录
    参数：手机号，密码
    在同个地方登录超过5次后10分钟内不能再次登录
    接口测试：
    访问URL:
        http://127.0.0.1:5000/api/v1.0/sessions/
        {
            "mobile":"18611111111",
            "password":"1238456"
        }
    :return:
    """
    # 获取参数
    req_dict = request.get_json()
    mobile = req_dict.get("mobile")
    password = req_dict.get("password")
    # 校验参数
    # 参数完整的校验
    if not all([mobile, password]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不完整")

    # 判断手机号
    if not re.match(r"1[345678]\d{9}", mobile):
        # 表示格式不对
        return jsonify(errno=RET.PARAMERR, errmsg="手机格式错误")
    # 密码错误次数的限制
    # 判断错误次数是否超过限制，如果超过限制，如果超过限制，则返回
    #
    # request.remote_addr
    user_ip = request.remote_addr
    try:
        access_nums = redis_store.get("access_nums_%s" % user_ip)
    except Exception as e:
        current_app.logger.error(e)
    else:
        print(access_nums)
        if access_nums is not None and int(access_nums) >= constants.LOGIN_ERROR_MAX_TIMES:
            return jsonify(errno=RET.REQERR, eermsg="错误次数过多，请稍后重试")
    # 从数据库中根据手机号查询用户的数据对象
    print("111111111111")
    try:
        user = User.query.filter_by(mobile=mobile).first()
        print(user, type(user))
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="获取用户信息失败！")

    # 用数据库的密码与用户填写的密码进行对比验证
    print(user)
    print(user.check_password(password))
    if user is None or not user.check_password(password):
        try:
            redis_store.incr("access_nums_%s" % user_ip)
            redis_store.expire("access_nums_%s" % user_ip, constants.LOGIN_ERROR_FORBIN_TIME)
            return jsonify(errno=RET.DATAERR, errmsg="用户名或密码错误！")
        except Exception as e:
            current_app.logger.error(e)
    # 保存登录状态到session中
    session['name'] = user.name
    session['mobile'] = user.mobile
    session['user_id'] = user.id

    # 返回结果
    return jsonify(errno=RET.OK, errmsg="登录成功！")


@api.route("/session", methods=["GET"])
def check_login():
    """检查登录状态"""
    name = session.get("name")
    # 如果session中数据name名字存在，这表示用户登录，否则未登录
    if name is not None:
        return jsonify(errno=RET.OK, errmsg="true", data={"name": name})
    else:
        return jsonify(errno=RET.SESSIONERR, errmsg="false")


@api.route("/session", methods=["DELETE"])
def logout():
    """登出"""
    # 清除session数据
    session.clear()
    return jsonify(errno=RET.OK, errmsg="ok")
