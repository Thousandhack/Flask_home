from . import api
from home.utils.commons import login_required
from home.utils import constants
from flask import g, current_app, jsonify, request
from home import db
from home.utils.response_code import RET
from home import redis_store
from home.models import User
from home.models import Area
import json


@api.route("/areas")
def get_area_info():
    """
    获取城区信息
    访问信息：
    http://127.0.0.1:5000/api/v1.0/areas
    :return:
    """
    # 尝试redis中获取数据
    try:
        resp_json = redis_store.get("area_info")
    except Exception as e:
        current_app.logger.error(e)
    else:
        if resp_json is not None:
            # redis 有缓存数据
            current_app.logger.info("hit data redis")
            return resp_json, 200, {"Content-type": "application/json"}
    # 如果没有缓存数据就去查数据库
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

    # 将数据转换为json字符串
    resp_dict = dict(errno=RET.OK, errmsg="OK", data=area_dict_list)
    # resp_json
    resp_json = json.dumps(resp_dict)
    # 将数据保存到redis中
    try:
        redis_store.setex("area_info", constants.AREA_INFO_REDIS_CACHE_EXPIRES, resp_json)

    except Exception as e:
        current_app.logger.error(e)
    return resp_json, 200, {"Content-type": "application/json"}
    # return jsonify(errno=RET.OK, errmsg="OK", data=area_dict_list)
