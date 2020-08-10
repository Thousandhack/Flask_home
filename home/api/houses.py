from . import api
from home.utils.commons import login_required
from home.utils import constants
from flask import session
from flask import g, current_app, jsonify, request
from home import db
from home.utils.response_code import RET
from home.utils.image_storage import storage
from home import redis_store
from home.models import User, Order
from home.models import Area, House, Facility, HouseImage
from datetime import datetime
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


@api.route("/houses/info", methods=["POST"])
@login_required
def save_house_info():
    """
    保存房屋的基本信息
    前端发送过来的json数据
    {
        "title":"",
        "price":"",
        "area_id":"1",
        "address":"",
        "room_count":"",
        "acreage":"",
        "unit":"",
        "capacity":"",
        "beds":"",
        "deposit":"",
        "min_days":"",
        "max_days":"",
        "facility":["7","8"]
    }
    首先判断提交的数据是否全部都存在
    判断金额是否正确
    判断城区是否真的存在
    判断设施是否都存在，会不会传的数据是不存在的id
    保存房屋信息
    返回房屋ID
    :return:
    """
    # 获取数据
    user_id = g.user_id
    house_data = request.get_json()

    title = house_data.get("title")  # 房屋名称标题
    price = house_data.get("price")  # 房屋单价
    area_id = house_data.get("area_id")  # 房屋所属城区的编号
    address = house_data.get("address")  # 房屋地址
    room_count = house_data.get("room_count")  # 房屋包含的房间数目
    acreage = house_data.get("acreage")  # 房屋面积
    unit = house_data.get("unit")  # 房屋布局（几室几厅)
    capacity = house_data.get("capacity")  # 房屋容纳人数
    beds = house_data.get("beds")  # 房屋卧床数目
    deposit = house_data.get("deposit")  # 押金
    min_days = house_data.get("min_days")  # 最小入住天数
    max_days = house_data.get("max_days")  # 最大入住天数

    # 校验参数
    if not all(
            [title, price, area_id, address, room_count, acreage, unit, capacity, beds, deposit, min_days, max_days]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不完整")

    # 判断金额是否正确
    try:
        price = int(float(price) * 100)
        deposit = int(float(deposit) * 100)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    # 判断城区id是否存在
    try:
        area = Area.query.get(area_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库异常")

    if area is None:
        return jsonify(errno=RET.NODATA, errmsg="城区信息有误")

    # 保存房屋信息
    # 创建一个house对象
    house = House(
        user_id=user_id,
        area_id=area_id,
        title=title,
        price=price,
        address=address,
        room_count=room_count,
        acreage=acreage,
        unit=unit,
        capacity=capacity,
        beds=beds,
        deposit=deposit,
        min_days=min_days,
        max_days=max_days
    )
    # 处理房屋的设施信息
    facility_ids = house_data.get("facility")

    # 如果用户勾选了设施信息，再保存数据库
    if facility_ids:
        # ["7","8"]
        try:
            # select  * from ih_facility_info where id in []
            facilities = Facility.query.filter(Facility.id.in_(facility_ids)).all()
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR, errmsg="数据库异常")

        if facilities:
            # 表示有合法的设施数据
            # 保存设施数据 保存多对多关系的数据
            house.facilities = facilities

    try:
        db.session.add(house)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="保存数据失败")

    # 保存数据成功
    return jsonify(errno=RET.OK, errmsg="OK", data={"house_id": house.id})


@api.route("/houses/image", methods=["POST"])
@login_required
def save_house_image():
    """保存房屋的图片
    参数 图片 房屋的id
    """
    image_file = request.files.get("house_image")
    house_id = request.form.get("house_id")

    if not all([image_file, house_id]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    # 判断house_id正确性
    try:
        house = House.query.get(house_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库异常")

    if house is None:  # if not house:
        return jsonify(errno=RET.NODATA, errmsg="房屋不存在")

    image_data = image_file.read()
    # 保存图片到七牛中
    try:
        file_name = storage(image_data)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.THIRDERR, errmsg="保存图片失败")

    # 保存图片信息到数据库中
    house_image = HouseImage(house_id=house_id, url=file_name)
    db.session.add(house_image)

    # 处理房屋的主图片
    if not house.index_image_url:
        house.index_image_url = file_name
        db.session.add(house)

    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="保存图片数据异常")

    image_url = constants.QINIU_URL_DOMAIN + file_name

    return jsonify(errno=RET.OK, errmsg="OK", data={"image_url": image_url})


@api.route("/user/houses", methods=["GET"])
@login_required
def get_user_houses():
    """
    获取房东发布的房源信息条目
    已经是postman登录的状态进行访问接口：
    http://127.0.0.1:5000/api/v1.0/user/houses
    返回信息：
            {
          "data": {
            "houses": [
              {
                "address": "测试地址111",
                "area_name": "西城区",
                "ctime": "2020-08-06",
                "house_id": 1,
                "img_url": "",
                "order_count": 0,
                "price": 39900,
                "room_count": 3,
                "title": "测试1",
                "user_avatar": ""
              }
            ]
          },
          "errmsg": "OK",
          "errno": "0"
        }
    :return:
    """
    user_id = g.user_id
    try:
        user = User.query.get(user_id)
        # 通过user中relationship的关系字段查询这个用户发布房源
        houses = user.houses
        # 另外一种方式查询
        # House.query.filter_by(user_id=user_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="获取数据失败")

    # 将查询到的房屋信息转换为字典放到列表中
    houses_list = []
    if houses:
        for house in houses:
            houses_list.append(house.to_basic_dict())

    return jsonify(errno=RET.OK, errmsg="OK", data={"houses": houses_list})


@api.route("/houses/index", methods=["GET"])
def get_house_index():
    """
    获取主页幻灯片的房屋信息接口
    访问url: http://127.0.0.1:5000/api/v1.0/houses/index
    返回数据为:
    # redis缓存中取出来的数据：
        {
            "errno"：0,
            "errmsg": "OK",
            "data":b'[
                {
                    "house_id": 1,
                    "title": "\测\试1",
                    "price": 39900,
                    "area_name": "\西\城\区",
                    "img_url": "D:\\\\pyCode\\\\flaskProject\\\\Flask_home\\\\home\\\\static\\\\images\\\\home01.jpg",
                    "room_count": 3,
                    "order_count": 5,
                    "address": "\测\试\地\址111",
                    "user_avatar": "",
                    "ctime": "2020-08-06"
                }
            ]'
        }
    # 数据库中取出来的数据：
        {
          "data": [
            {
              "address": "测试地址111",
              "area_name": "西城区",
              "ctime": "2020-08-06",
              "house_id": 1,
              "img_url": "D:\\pyCode\\flaskProject\\Flask_home\\home\\static\\images\\home01.jpg",
              "order_count": 5,
              "price": 39900,
              "room_count": 3,
              "title": "测试1",
              "user_avatar": ""
            }
          ],
          "errmsg": "OK",
          "errno": 0
        }
    :return:
    """
    # 从缓存中尝试获取数据
    try:
        ret = redis_store.get("home_page_data")

        print(ret)
    except Exception as e:
        current_app.logger.error(e)
        ret = None
    if ret:
        current_app.logger.info("hit house index of redis")
        # 因为redis 中保存的是json字符串，所以直接进行字符串拼接返回
        return '{"errno"：0,"errmsg":"OK","data":%s}' % ret, 200, {"Content-Type": "application/json"}
    else:
        try:
            # 查询数据库，返回房屋订单数目最多的5条数据
            # 根据订单的数量分组
            houses = House.query.order_by(House.order_count.desc()).limit(constants.HOME_PAGE_MAX_HOUSES)
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR, errmsg="查询数据失败")

        if not houses:
            return jsonify(errno=RET.NODATA, errmsg="查询无数据")

        house_list = []
        for house in houses:
            # 如果房屋未设置图片，则跳过（因为首页展示的需要房屋图片）
            if not house.index_image_url:
                continue
            house_list.append(house.to_basic_dict())

        # 将数据转换成json,并保存到redis缓存中
        # json_houses = json.dumps(house_list)
        # try:
        #     redis_store.setex("home_page_data", constants.HOME_PAGE_DATA_REDIS_EXPIRES, json_houses)
        # except Exception as e:
        #     current_app.logger.error(e)
        #
        # return '{"errno":0,"errmsg":"OK","data":%s}' % json_houses, 200, {"Content-Type": "application/json"}

        return jsonify(errno=0, errmsg="OK", data=house_list)


@api.route("/houses/<int:house_id>", methods=["GET"])
def get_house_detail(house_id):
    """
    获取房屋详情
    # 前端在房屋详情页面展示时，如果浏览页面的用户不是该房屋的房东，则展示预定按钮，否则展示
    # 所以需要后端返回登录用户的user_id
    # 尝试获取用户登录的信息，若登录，则返回给前端登录用户的user_id,否则返回user_id=-1

    # 就是如果访问的登录用户与房屋发布的用户一致前端就有一些不需要展示
    访问URL:  http://127.0.0.1:5000/api/v1.0/houses/1

    返回数据：
            {
            "errno": "0",
            "errmsg": "OK",
            "data": {
                "user_id": 2,
                "house": {
                    "hid": 1,
                    "user_id": 2,
                    "user_name": "18611111111",
                    "user_avatar": "",
                    "title": "测试1",
                    "price": 39900,
                    "address": "测试地址111",
                    "room_count": 3,
                    "acreage": 90,
                    "unit": "三室两厅",
                    "capacity": 6,
                    "beds": "三床",
                    "deposit": 100000,
                    "min_days": 5,
                    "max_days": 0,
                    "img_urls": [],
                    "facilities": [
                        1,
                        2,
                        5,
                        6,
                        9,
                        16
                    ],
                    "comments": []
                }
            }

    :param house_id:
    :return:
    """
    user_id = session.get("user_id", "-1")

    # 校验参数
    if not house_id:
        return jsonify(errno=RET.PARAMERR, errmsg="参数缺失")
    # 先从redis缓存中获取信息
    try:
        ret = redis_store.get("house_info_%s" % house_id)
    except Exception as e:
        current_app.logger.error(e)
        ret = None
    if ret:
        current_app.logger.info("hit house info redis")
        return '{"errno":"0","errmsg":"OK","data":{"user_id":%s,"house_info":%s}' % (user_id, ret), 200, {
            "Content-Type": "application/json"}

    # 查询数据库
    try:
        house = House.query.get(house_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="查询数据失败")
    if not house:
        return jsonify(errno=RET.NODATA, errmsg="房屋不存在")

    # 将房屋对象数据转为字典
    try:
        house_data = house.to_full_dict()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库出错")
    # 存入到redis中
    json_house = json.dumps(house_data)
    try:
        redis_store.setex("house_info_%s" % house_id, constants.HOUSE_DETAIL_REDIS_EXPIRE_SECOND, json_house)
    except Exception as e:
        current_app.logger.error(e)
    resp = '{"errno":"0","errmsg":"OK","data":{"user_id":%s,"house":%s}' % (user_id, json_house), 200, {
        "Content-Type": "application/json"}

    return resp


# @api.route("/houses")
# def get_house_list():
#     """
#     # GET  /api/v1.0/houses?sd=2020-08-07&ed=2020-08-10&aid=10&sk=new&page=1
#     获取房屋的列表信息（搜索页面）
#     # strptime 从字符串转为时间
#     # strftime 从时间转为字符串
#     # %H%M%S  时分秒
#
#     最新上线  new
#     入住最多   booking
#     价格低-高   price-inc
#     价格高-低   price-des
#
#     访问URL: http://127.0.0.1:5000/api/v1.0/houses
#     返回的结果;
#         {
#           "data": {
#             "current_page": null,
#             "houses": [
#               {
#                 "address": "测试地址 1",
#                 "area_name": "东城区",
#                 "ctime": "2020-08-06",
#                 "house_id": 1,
#                 "img_url": "",
#                 "order_count": 0,
#                 "price": 39900,
#                 "room_count": 3,
#                 "title": "测试1",
#                 "user_avatar": ""
#               }
#             ],
#             "total_page": 1
#           },
#           "errmsg": "OK",
#           "errno": "0"
#         }
#     :return:
#     """
#     start_date = request.args.get("sd", "")  # 用户想要的起始时间
#     end_date = request.args.get("ed", "")  # 用户想要的结束时间
#     area_id = request.args.get("aid", "")  # 区域编号
#     sort_key = request.args.get("sk", "")  # 排序
#     page = request.args.get("page", "")  # 页数
#     per_page = request.args.get("size", "")  # 每页数量
#
#     try:
#         if start_date:
#             start_date = datetime.strptime(start_date, "%Y-%m-%d")
#         if end_date:
#             end_date = datetime.strptime(end_date, "%Y-%m-%d")
#         print(start_date, end_date, type(start_date), end_date(end_date))
#         if start_date and end_date:
#             print("111111")
#             assert start_date <= end_date
#     except Exception as e:
#         print("dqwqeqe")
#         current_app.logger.error(e)
#         return jsonify(errno=RET.PARAMERR, errmsg="日期参数有误")
#     # 判断区域id
#     if area_id:
#         try:
#             area = Area.query.get(area_id)
#         except Exception as e:
#             current_app.logger.error(e)
#             return jsonify(errno=RET.PARAMERR, errmsg="区域参数有误")
#     # 处理页数
#     if page:
#         try:
#             page = int(page)
#         except Exception as e:
#             current_app.logger.error(e)
#             page = 1
#
#     # 处理页数
#     if per_page:
#         try:
#             per_page = int(per_page)
#         except Exception as e:
#             current_app.logger.error(e)
#             per_page = constants.HOUSE_LIST_PAGE_CAPACITY
#
#     # 使用缓存获取缓存数据,如果有相应的缓存就获取缓存的，如果没有就继续查询
#     redis_key = "house_%s_%s_%s_%s" % (start_date, end_date, area_id, sort_key)
#     try:
#         resp_json = redis_store.hget(redis_key, page)
#     except Exception as e:
#         current_app.logger.error(e)
#     else:
#         if resp_json:
#             return resp_json, 200, {"Content-Type": "application/json"}
#
#     # 过滤条件的参数容器
#     filter_params = []
#
#     # 填充过滤参数
#     # 时间条件
#     conflict_orders = None
#     print("111112222222")
#     # try:
#     if start_date and end_date:
#         # 查询冲突的订单
#         conflict_orders = Order.query.filter(Order.begin_date <= end_date, Order.end_date >= start_date).all()
#     elif start_date:
#         conflict_orders = Order.query.filter(Order.end_date >= start_date).all()
#     elif end_date:
#         conflict_orders = Order.query.filter(Order.begin_date <= end_date).all()
#
#     # except Exception as e:
#     #     current_app.logger.error(e)
#     #     return jsonify(errno=RET.DBERR, errmsg="查询数据库异常")
#     # print(conflict_orders)
#     # 从订单中获取的所有房屋id
#     if conflict_orders:
#         conflict_house_ids = [conflict_order.id for conflict_order in conflict_orders]
#     else:
#         conflict_house_ids = []
#     # 如果冲突的房屋id不为空，向查询参数中添加条件
#     if conflict_house_ids:
#         filter_params.append(House.id.notin_(conflict_house_ids))
#
#     # 区域条件
#     if area_id:
#         filter_params.append(House.area_id == area_id)
#
#     # 查询数据库
#     # 排序方式条件
#     # asc 正序   desc 倒序
#     if sort_key == "booking":  # 入住最多
#         houuse_query = House.query.filter(*filter_params).order_by(House.order_count.desc())
#     elif sort_key == "price-inc":
#         houuse_query = House.query.filter(*filter_params).orser_by(House.price.asc())
#     elif sort_key == "price-des":
#         houuse_query = House.query.filter(*filter_params).orser_by(House.price.desc())
#     else:  # 模型从新到旧 sort_key == "new":
#         houuse_query = House.query.filter(*filter_params).order_by(House.create_time.desc())
#
#     # 处理分页
#     # page 表示查询第几页数据
#     # per_page 表示每页的数据量
#     # ,error_out 表示自动的错误输出
#     try:
#         page_obj = houuse_query.paginate(page=page, per_page=per_page, error_out=False)
#     except Exception as e:
#         current_app.logger.error(e)
#         return jsonify(errno=RET.DBERR, errmsg="查询数据库异常")
#     # 获取页面数据
#     house_list = page_obj.items
#     houses = []
#     for house in house_list:
#         houses.append(house.to_basic_dict())
#
#     # 获取总页数
#     total_page = page_obj.pages
#
#     # return jsonify(errno=RET.OK, errmsg="OK", data={"total_page": total_page, "houses": houses, "current_page": page})
#     resp_dict = dict(errno=RET.OK, errmsg="OK", data={"total_page": total_page, "houses": houses, "current_page": page})
#     resp_json = json.dumps(resp_dict)
#
#     # 设置缓存数据
#     # 设置hash 的类型的redis
#     try:
#         redis_key = "house_%s_%s_%s_%s" % (start_date, end_date, area_id, sort_key)
#         # 哈希类型
#         redis_store.hset(redis_key, page, resp_json)
#         redis_store.expire(redis_key, constants.HOUES_LIST_PAGE_REDIS_CACHE_EXPIRES)
#     except Exception as e:
#         current_app.logger.error(e)
#
#     return resp_json, 200, {"Content-Type": "application/json"}
#


# GET /api/v1.0/houses?sd=2020-08-01&ed=2020-08-31&aid=10&sk=new&p=1
@api.route("/houses")
def get_house_list():
    """获取房屋的列表信息（搜索页面）"""
    start_date = request.args.get("sd", "")  # 用户想要的起始时间
    end_date = request.args.get("ed", "")  # 用户想要的结束时间
    area_id = request.args.get("aid", "")  # 区域编号
    sort_key = request.args.get("sk", "new")  # 排序关键字
    page = request.args.get("p")  # 页数

    # 处理时间
    try:
        if start_date:
            start_date = datetime.strptime(start_date, "%Y-%m-%d")

        if end_date:
            end_date = datetime.strptime(end_date, "%Y-%m-%d")

        if start_date and end_date:
            assert start_date <= end_date
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg="日期参数有误")

    # 判断区域id
    if area_id:
        try:
            area = Area.query.get(area_id)
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.PARAMERR, errmsg="区域参数有误")

    # 处理页数
    try:
        page = int(page)
    except Exception as e:
        current_app.logger.error(e)
        page = 1

    # 获取缓存数据
    redis_key = "house_%s_%s_%s_%s" % (start_date, end_date, area_id, sort_key)
    try:
        resp_json = redis_store.hget(redis_key, page)
    except Exception as e:
        current_app.logger.error(e)
    else:
        if resp_json:
            return resp_json, 200, {"Content-Type": "application/json"}

    # 过滤条件的参数列表容器
    filter_params = []

    # 填充过滤参数
    # 时间条件
    conflict_orders = None

    try:
        if start_date and end_date:
            # 查询冲突的订单
            conflict_orders = Order.query.filter(Order.begin_date <= end_date, Order.end_date >= start_date).all()
        elif start_date:
            conflict_orders = Order.query.filter(Order.end_date >= start_date).all()
        elif end_date:
            conflict_orders = Order.query.filter(Order.begin_date <= end_date).all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库异常")

    if conflict_orders:
        # 从订单中获取冲突的房屋id
        conflict_house_ids = [order.house_id for order in conflict_orders]

        # 如果冲突的房屋id不为空，向查询参数中添加条件
        if conflict_house_ids:
            filter_params.append(House.id.notin_(conflict_house_ids))

    # 区域条件
    if area_id:
        filter_params.append(House.area_id == area_id)

    # 查询数据库
    # 补充排序条件
    if sort_key == "booking":  # 入住做多
        house_query = House.query.filter(*filter_params).order_by(House.order_count.desc())
    elif sort_key == "price-inc":
        house_query = House.query.filter(*filter_params).order_by(House.price.asc())
    elif sort_key == "price-des":
        house_query = House.query.filter(*filter_params).order_by(House.price.desc())
    else:  # 新旧
        house_query = House.query.filter(*filter_params).order_by(House.create_time.desc())

    # 处理分页
    try:
        #                               当前页数          每页数据量                              自动的错误输出
        page_obj = house_query.paginate(page=page, per_page=constants.HOUSE_LIST_PAGE_CAPACITY, error_out=False)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库异常")

    # 获取页面数据
    house_li = page_obj.items
    houses = []
    for house in house_li:
        houses.append(house.to_basic_dict())

    # 获取总页数
    total_page = page_obj.pages

    resp_dict = dict(errno=RET.OK, errmsg="OK", data={"total_page": total_page, "houses": houses, "current_page": page})
    resp_json = json.dumps(resp_dict)

    # 页数大于数据的总页数才有意义，才存到缓存中去
    if page <= total_page:
        # 设置缓存数据
        redis_key = "house_%s_%s_%s_%s" % (start_date, end_date, area_id, sort_key)
        # 哈希类型
        try:
            # redis_store.hset(redis_key, page, resp_json)
            # redis_store.expire(redis_key, constants.HOUES_LIST_PAGE_REDIS_CACHE_EXPIRES)

            # 创建redis管道对象，可以一次执行多个语句
            pipeline = redis_store.pipeline()

            # 开启多个语句的记录
            pipeline.multi()

            pipeline.hset(redis_key, page, resp_json)
            pipeline.expire(redis_key, constants.HOUES_LIST_PAGE_REDIS_CACHE_EXPIRES)

            # 执行语句
            pipeline.execute()
        except Exception as e:
            current_app.logger.error(e)

    return resp_json, 200, {"Content-Type": "application/json"}