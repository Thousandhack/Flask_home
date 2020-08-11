from home.utils.commons import login_required
from home.utils.response_code import RET
from flask import request
from flask import jsonify
from flask import g
from flask import current_app
from home.models import Order
from home.models import House
from home import db
from . import api
from datetime import datetime


@api.route("/orders")
@login_required
def save_order():
    """保存订单(生成订单接口)"""
    user_id = g.user_id

    # 获取参数
    order_data = request.get_json()
    if not order_data:
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    house_id = order_data.get("house_id")  # 预定的房屋编号
    start_date_str = order_data.get("start_date")  # 预定的起始时间
    end_date_str = order_data.get("end_date")  # 预定的结束时间

    # 参数检查
    if not all([house_id, start_date_str, end_date_str]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    # 日期检查
    try:
        # 将请求的时间参数字符串转换为datatime类型
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
        assert start_date <= end_date  # 断言，条件为false的时候触发异常
        days = (end_date - start_date).days + 1
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg="日期格式错误")
    # 查询房屋是否存在
    try:
        house = House.query.get(house_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="获取房屋信息失败")
    if not house:
        return jsonify(errno=RET.NODATA, errmsg="房屋不存在")

    # 预定的房屋是否是房东自己
    if user_id == house.user_id:
        return jsonify(errno=RET.ROLEERR, errmsg="不能预定自己的房屋")

    # 确保用户预定的时间内，房屋没有被别人预定
    try:
        # 查询时间冲突的订单数
        count = Order.query.filter(Order.house_id == house_id, Order.begin_date <= end_date,
                                   Order.end_date >= start_date).count()

    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="检查出错，请稍候重试")
    # 只要存在冲突订单就说明不能再预定了
    if count > 0:
        return jsonify(errno=RET.DATAERR, errmsg="房屋已被预定")
    # 订单总额
    amount = days * house.price

    # 保存订单数据
    order = Order(
        house_id=house_id,
        user_id=user_id,
        begin_date=start_date,
        end_date=end_date,
        days=days,
        house_price=house.price,
        amount=amount
    )

    try:
        db.session.add(Order)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="保存订单失败")
    return jsonify(errno=RET.OK, errmsg="OK", data={"order_id": order.id})


@api.route("/user/orders", methods=["GET"])
@login_required
def get_user_orders():
    """
    查询用户的订单信息
    :return:
    """
    user_id = g.user_id

    # 用户的身份，用户想要查询作为客户预定别人房子的订单，还是想要作为房东查询别人预定自己的房子的订单
    role = request.args.get("role", "")

    # 查询订单数据
    try:
        if "landlord" == role:
            # 以房东的身份查询订单
            # 先查询属于自己的房子有哪些
            houses = House.query.filter(House.user_id == user_id).all()
            houses_ids = [house.id for house in houses]
            # 再查询预订了自己房子的订单
            orders = Order.query.filter(Order.house_id.in_(houses_ids)).order_by(Order.create_time.desc()).all()
        else:
            # 以访客的身份查询订单，查询自己预定的订单
            orders = Order.query.filter(Order.user_id == user_id).order_by(Order.create_time.desc()).all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="查询订单消息失败")

    # 将订单对象转换为字典数据
    orders_dict_list = []
    if orders:
        for order in orders:
            orders_dict_list.append(order.to_dict())

    return jsonify(errno=RET.OK, errmsg="OK", data={"orders": orders_dict_list})
