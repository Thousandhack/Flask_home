from . import api
from home.utils.commons import login_required
from home.models import Order
from flask import g
from flask import current_app
from flask import jsonify
from home.utils.response_code import RET
from home.utils import constants
from alipay import Alipay
import os


@api.route("/orders/<int:order_id>/payment", methods=["POST"])
@login_required
def order_pay(order_id):
    """发起支付宝支付"""
    user_id = g.user_id
    # 判断订单状态
    try:
        order = Order.query.filter(Order.id == order_id, Order.user_id == user_id,
                                   Order.status == "WAIT_PAYMENT").first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库异常")

    if order is None:
        return jsonify(errno=RET.NODATA, errmsg="订单数据不存在")

    # 创建支付宝sdk的工具对象
    alipay_client = Alipay(
        appid="2016101400681751",
        app_notify_url=None,  # 默认回调地址
        app_private_key_path=os.path.join(os.path.dirname(__file__), "key/app_private_key.pem"),  # 私钥
        alipay_public_key_path=os.path.join(os.path.dirname(__file__), "key/app_public_key.pem"),
        singn_type="RSA2",
        debug=True,
    )

    # 手机网站支付
    order_string = alipay_client.api_alipay_trade_way_pay(
        out_trade_no=order.id,  # 订单编号
        total_amount=str(order.amount / 100.0),
        subject="测试订单",  # 订单标题
        return_url="http://127.0.0.1:5000/orders.html",  # 返回的链接地址
        notify_url=None  # 可选，不填则使用默认notify url
    )
    # 构建让用户跳转的支付
    pay_url = constants.ALIPAY_URL_PREFIX + order_string
    return jsonify(errno=RET.OK, errmsg="ok", data={"pay_url": pay_url})
