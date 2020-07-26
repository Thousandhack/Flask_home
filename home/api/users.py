from . import api
from home import db
from home import models
from flask import current_app
@api.route("/index")
def index():
    """
    http://127.0.0.1:5000/api/v1.0/index
    :return:
    """
    # current_app.logger.error("err ssss")  # 记录日志
    return "index page"
