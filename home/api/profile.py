# 主要是关于用户资料的
from . import api
from home.utils.commons import login_required
from home.utils import constants
from flask import g, current_app, jsonify, request, session
from home import db
from home.utils.response_code import RET
from home.utils.image_storage import storage
from home.models import User


@api.route("/users/avatar", methods=["POST"])
@login_required
def set_user_avatar():
    """
    设置用户的头像
    参数： 图片(多媒体表单格式)  用户id(g.user_id)
    装饰器的代码已经将user_id 保存到g对象中，所以视图中可以直接读取
    :return:
    """
    user_id = g.user_id
    # 获取图片
    image_file = request.files.get("avatar")

    if image_file is None:
        return jsonify(errno=RET.PARAMERR, errmsg="未上传图片")
    image_data = image_file.read()

    # 调用七牛上传图片，返回文件名
    try:
        file_name = storage(image_data)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.THIRDERR, errmsg="上传图片失败")

    # 保存文件名到数据库中
    try:
        User.query.filter_by(id=user_id).update({"avatar_url": file_name})
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="保存图片信息失败")

    avatar_url = constants.QINIU_URL_DOMAIN + file_name
    # 保存成功返回
    return jsonify(errno=RET.OK, errmsg="保存成功", data={"avatar_url": avatar_url})


@api.route("/users/name", methods=["PUT"])
@login_required
def change_user_name():
    """修改用户名"""
    # 使用了login_required装饰器后，可以从g对象中获取用户user_id
    user_id = g.user_id

    # 获取用户想要设置的用户名
    req_data = request.get_json()
    if not req_data:
        return jsonify(errno=RET.PARAMERR, errmsg="参数不完整")
    name = req_data.get("name")
    if not name:
        return jsonify(errno=RET.PARAMERR, errmsg="名字不能为空")

    # 保存用户昵称name,并同时name重复（利用数据库的唯一索引）
    try:
        # 注意这边的用户名设置为唯一
        User.query.filter_by(id=user_id).update({"name": name})
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.OK, errmsg="设置用户错误")

    # 修改session数据中的name字段
    session['name'] = name
    return jsonify(errno=RET.OK, errmsg="OK", data={"name": name})
