# 定义一个正则转换器

from werkzeug.routing import BaseConverter
# g 对象用于保存装饰器的数据传到视图函数的
from flask import session, jsonify,g
from home.utils.response_code import RET
import functools

# 定义正则转换器
class ReConverter(BaseConverter):
    """"""

    def __init__(self, url_map, regex):
        # 调用父类的初始化方法
        super(ReConverter, self).__init__(url_map)

        # 保存正则表达式
        self.regex = regex


# 定义的验证登录状态的装饰器
def login_required(view_func):
    @functools.wraps(view_func)  # 会改变一些特性，可以不改变被装饰函数的函数的__name__ ,被装饰器函数的相关属性就不会改变
    def wrapper(*args, **kwargs):
        # 判断用户的登录状态
        user_id = session.get("user_id")
        # 如果用户是登录的，执行视图函数
        if user_id is not None:
            # 将user_id 保存到g对象中
            g.user_id = user_id
            return view_func(*args, **kwargs)
        else:
            # 如果未登录，返回未登录信息
            return jsonify(errno=RET.SESSIONERR, errmsg="用户未登录")

    return wrapper
