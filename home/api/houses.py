from . import api
from home.utils.commons import login_required
from home.utils import constants
from flask import g, current_app, jsonify, request
from home import db
from home.utils.response_code import RET
from home.utils.image_storage import storage
from home.models import User
from home.models import Area


@api.route("/areas")
def get_area_info():
    """
    获取城区信息
    访问信息：
    http://127.0.0.1:5000/api/v1.0/areas
    :return:
    """
    # 查询数据库，读取城区信息
    try:
        area_list = Area.query.all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库异常")
    area_dict_list = []
    # 将对象转成字典
    for area in area_list:
        area_dict_list.append(area.to_dict())

    return jsonify(errno=RET.OK, errmsg="OK", data=area_dict_list)
