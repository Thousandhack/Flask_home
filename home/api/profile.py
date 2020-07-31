# 主要是关于用户资料的
from . import api
from home.utils.commons import lo


@api.route("/users/avatar", methods=["POST"])
def set_user_avatar():
    """
    设置用户的头像
    :return:
    """
    pass
