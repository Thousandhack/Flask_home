from flask import Blueprint

# 创建蓝图对象
api = Blueprint("api_01", __name__)

# 导入蓝图的视图
from . import users, verify_code, passport, houses
