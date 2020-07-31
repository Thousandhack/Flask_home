# 主要是关于用户资料的
from . import api
from home.utils.commons import login_required
from flask import g, current_app, jsonify, request
from home.utils.response_code import RET
from home.utils.image_storage import storage

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

    # 调用七牛上传图片
    storage(image_data)

    #
