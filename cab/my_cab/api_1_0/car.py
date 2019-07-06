from . import api
from flask import current_app, request, jsonify, g, session
from my_cab.models import User, Area, Car, Facility, CarImage, Order
from my_cab.utils.response_code import RET
from my_cab import redis_connect1, db
from my_cab.utils.constants import AREA_INFO_EXPIRES, FACILITY_INFO_EXPIRES, QINIU_IMAGE_STORE_DOMAIN, INDEX_PAGE_CAR_MAX_COUNT, \
    INDEX_PAGE_CAR_EXPIRES, HOUER_DETAIL_INFO_EXPIRES, PER_PAGE_COUNT, SEARCH_CARS_INFO_EXPIRES
from my_cab.utils.commons import login_required
from my_cab.utils import image_storage
import json
import requests
import datetime


def get_two_point_distance(start_point, end_point):
    ak = 'cod2jUKlqXUTvQwkX9Modtxd94knvWxv'

    # http: // api.map.baidu.com / geocoding / v3 /?address = 北京市海淀区上地十街10号 & output = json & ak = cod2jUKlqXUTvQwkX9Modtxd94knvWxv
    location_url = 'http://api.map.baidu.com/geocoding/v3/'
    start_params = {'address': start_point, 'output': 'json', 'ak': ak}
    end_params = {'address': end_point, 'output': 'json', 'ak': ak}
    # 获取两地经纬度
    start_dict = json.loads(requests.get(url=location_url, params=start_params).text)
    end_dict = json.loads(requests.get(url=location_url, params=end_params).text)

    start_location = None
    end_location = None

    if start_dict['status'] == 0:
        start_location = start_dict['result']['location']
    if end_dict['status'] == 0:
        end_location = end_dict['result']['location']
    # print(start_location)
    # print(end_location)

    if start_location and end_location:
        # 获取两地距离和驱车时间
        # http://api.map.baidu.com/routematrix/v2/driving?output=json&origins=40.45,116.34&destinations=40.34,116.45&tactics=11&ak=cod2jUKlqXUTvQwkX9Modtxd94knvWxv
        url = 'http://api.map.baidu.com/routematrix/v2/driving'
        params = {'output': 'json',
                  'origins': str(start_location['lat']) + ',' + str(start_location['lng']),  # 注意经纬度跟上面获取的位置是相反的
                  'destinations': str(end_location['lat']) + ',' + str(end_location['lng']),
                  'tactics': '11',
                  'ak': ak
                  }

        resp_json = requests.get(url=url, params=params).text
        resp_dict = json.loads(resp_json)
        # print(resp_dict)
        if resp_dict['status'] != 0:
            return ''

        else:

            distance = resp_dict['result'][0]['distance']['text'][0:-2]
            duration = resp_dict['result'][0]['duration']['text']
            # print(distance)
            # print(duration)
            return duration


@api.route('/car/area', methods=['GET'])
def get_areas():
    # 首先从redis中拿数据
    try:
        resp_json = redis_connect1.get('areas_info')
    except Exception as e:
        current_app.logger.error(e)
    else:
        if resp_json is not None:
            # print('area缓存数据')
            return resp_json, 200, {"Content-Type": "application/json"}

    # 查询数据库
    try:
        areas = Area.query.all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='数据库异常')

    data_list = []
    for area in areas:
        data_list.append(area.area_to_dict())

    # 设置缓存
    # 把响应结果都存入redis
    resp_dict = dict(errno=RET.OK, errmsg='查询地区数据ok', data=data_list)
    resp_json = json.dumps(resp_dict)

    try:
        redis_connect1.setex('areas_info', AREA_INFO_EXPIRES, resp_json)
    except Exception as e:
        current_app.logger.error(e)

    return resp_json, 200, {"Content-Type": "application/json"}


@api.route('/car/facilities', methods=['GET'])
def get_facilities():
    # 首先从redis中拿数据
    try:
        resp_json = redis_connect1.get('facilities')
    except Exception as e:
        current_app.logger.error(e)
    else:
        if resp_json is not None:
            # print('area缓存数据')
            return resp_json, 200, {"Content-Type": "application/json"}

    # 查询数据库
    try:
        facilities = Facility.query.all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='数据库异常')

    data_list = []
    for facility in facilities:
        data_list.append(facility.to_dict())

    # 设置缓存
    # 把响应结果都存入redis
    resp_dict = dict(errno=RET.OK, errmsg='查询配置数据ok', data=data_list)
    resp_json = json.dumps(resp_dict)

    try:
        redis_connect1.setex('facilities', FACILITY_INFO_EXPIRES, resp_json)
    except Exception as e:
        current_app.logger.error(e)

    return resp_json, 200, {"Content-Type": "application/json"}


@api.route('/car', methods=['POST'])
@login_required
def new_car():

    # 获取参数
    req_json = request.get_json()

    area_id = req_json.get('area_id')
    title = req_json.get('title')
    price = req_json.get('price')
    no = req_json.get('no')
    load = req_json.get('load')
    size = req_json.get('size')
    mold = req_json.get('mold')
    space = req_json.get('space')

    # print(req_json)
#     验证参数
    if not all([title, price, area_id, no, load, size, mold, space]):
        return jsonify(errno=RET.PARAMERR, errmsg='参数不完整')

#     验证价格是否数字,数据库中定义为整数,以分为单位
    try:
        price = int(float(price)*100)

        space = int(space)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg='价格/载重/空间参数错误')

#     验证区域id是否有效
    try:
        area = Area.query.filter_by(id=area_id).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='数据库异常')

    if area is None:
        return jsonify(errno=RET.PARAMERR, errmsg='区域参数错误')
 
#     获取车辆id
    car_id = req_json.get('car_id')
    if car_id:
        try:
            car = Car.query.filter_by(id=car_id).first()
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR, errmsg='数据库异常，查询车辆信息失败')

        if car is None:
            #     车辆不存在创建车辆对象
            car = Car(
                user_id=g.user_id,
                area_id=area_id,
                title=title,
                price=price,
                no=no,
                load=load,
                size=size,
                mold=mold,
                space=space

            )

    else:
        #     没有传入car_id创建车辆对象
        car = Car(
            user_id=g.user_id,
            area_id=area_id,
            title=title,
            price=price,
            no=no,
            load=load,
            size=size,
            mold=mold,
            space=space

        )

        try:
            db.session.add(car)
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR, errmsg='数据库异常,添加car失败')

    # update车辆参数
    car.user_id = g.user_id,
    car.area_id = area_id,
    car.title = title,
    car.price = price,
    car.no = no,
    car.load = load,
    car.size = size,
    car.mold = mold,
    car.space = space,

    #     获取车辆设施参数
    facilities_list = req_json.get('facility')
    desc = req_json.get('disc')
    if desc:
        car.disc = desc

    if facilities_list:

        try:
            facilities = Facility.query.filter(Facility.id.in_(facilities_list)).all()
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR, errmsg='数据库异常')

        else:
            if facilities:
                car.facilities = facilities

    try:

        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='数据库异常,保存失败')

    print(car_id)

    return jsonify(errno=RET.OK, errmsg='添加成功', data={'car_id': car.id})


@api.route('/car/image', methods=['POST', 'GET'])
@login_required
def upload_car_image():
    # 获取参数
    car_id = request.form.get('car_id')
    image_data = request.files.get('car_image').read()

#     验证参数完整性
    if not all([car_id, image_data]):
        return jsonify(errno=RET.PARAMERR, errmsg='参数不完整')

#     验证car_id真实性
    try:
        car = Car.query.filter_by(id=car_id).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg='数据库异常')

    if car is None:
        return jsonify(errno=RET.NODATA, errmsg='车辆参数错误')

#     上传图片
    try:
        image_name = image_storage.store(image_data)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.THIRDERR, errmsg='图片上传失败')

#     保存图片名到数据库
    car_image = CarImage(car_id=car_id, url=image_name)

    if not car.index_image_url:
        car.index_image_url = image_name

    try:
        db.session.add(car_image)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg='数据库异常,图片保存失败')

    image_url = QINIU_IMAGE_STORE_DOMAIN + image_name

    return jsonify(errno=RET.OK, errmsg='上传成功', data={'image_url': image_url})


@api.route('/user/cars', methods=['GET'])
@login_required
def get_my_cars():
    # 获取参数
    try:
        user = User.query.filter_by(id=g.user_id).first()
        cars = user.cars
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='数据库异常')

    my_cars = []
    if cars:

        for car in cars:
            my_cars.append(car.to_base_dict())

    return jsonify(errno=RET.OK, errmsg='我的房源查询成功', data={"my_cars": my_cars})


@api.route('/index', methods=['GET'])
def get_index_cars():
    # 首先从redis缓存中拿数据
    try:
        cars_json = redis_connect1.get('index_cars')
    except Exception as e:
        current_app.logger.error(e)
        cars_json = None
    # 如果redis缓存有数据
    if cars_json:
        # print('redis数据')
        return jsonify(errno=RET.OK, errmsg='查询成功', data=json.loads(cars_json))

    else:
        # redis缓存中无数据,查询数据库,查询有默认图片的5个车辆,按照订单数量降序
        try:
            cars = Car.query.order_by(Car.order_count.desc()).filter(Car.index_image_url.isnot(None))\
                .limit(INDEX_PAGE_CAR_MAX_COUNT).all()
            # cars = Car.query.all()

        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR, errmsg='数据库异常,查询失败')

        # 如果没有车辆信息
        if not cars:
            return jsonify(errno=RET.NODATA, errmsg='无数据')

        # 车辆对象转换成字典
        car_list = []
        for car in cars:
            # print(car)
            car_list.append(car.to_base_dict())

        # 字典列表转换成json数据
        cars_json = json.dumps(car_list)

        # 车辆json数据存入redis中
        try:
            redis_connect1.setex('index_cars', INDEX_PAGE_CAR_EXPIRES, cars_json)
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR, errmsg='数据库异常,保存失败')

        # return '{"errno": 0, "errmsg": "查询成功", "data":%s}'%cars_json, 200, {"Content-Type": "application/json"}  #这种方法不行
        return jsonify(errno=RET.OK, errmsg='查询成功', data=car_list)


@api.route('/car/detail/<int:car_id>', methods=['GET'])
def get_car_detail(car_id):
    # print(car_id)
    # 获取当前用户id
    user_id = session.get('user_id', '-1')

    # 先从redis获取数据
    try:
        car_json = redis_connect1.get('car_info_%s' % car_id)
    except Exception as e:
        current_app.logger.error(e)
        car_json = None

    if car_json:
        # print('detail--redis数据')
        return jsonify(errno=RET.OK, errmsg='车辆详情查询成功', data={'car': json.loads(car_json), 'user_id': user_id})

    else:
        # 查询数据库
        try:
            car = Car.query.filter_by(id=car_id).first()
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR, errmsg='数据库错误,获取数据失败')

        if car is None:
            return jsonify(errno=RET.NODATA, errmsg='无车辆信息')

        car_json = json.dumps(car.to_full_dict())

        # 缓存到redis中
        try:
            redis_connect1.setex('car_info_%s' % car_id, HOUER_DETAIL_INFO_EXPIRES, car_json)
        except Exception as e:
            current_app.logger.error(e)

        return jsonify(errno=RET.OK, errmsg='车辆详情查询成功', data={'car': car.to_full_dict(), 'user_id': user_id})

# GET /api/v1.0/cars?sd=20190628&ed=20190701&aid=1&sk=new&p=1
@api.route('/cars', methods=['GET'])
def search_cars():

    # 获取参数
    start_date = request.args.get('sd')
    start_point = request.args.get('sp')
    end_point = request.args.get('ep')

    area_id = request.args.get('aid')
    sort_key = request.args.get('sk', 'new')
    page = request.args.get('p')
    end_date = ''
    # 验证日期有效性
    try:
        # 如果传入了日期，转换成日期
        if start_date:
            start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d %H:%M')
            if start_point and end_point:
                duration = get_two_point_distance(start_point, end_point)
                # 计算结束时间
                # 拆分duration  2.7小时
                if duration[-2:] == '分钟':
                    hours = 0
                    minutes = int(duration[0:-2])
                else:
                    hours = int(duration[0:-4])
                    minutes = int((int(duration[-3]) / 10) * 60)
                end_date = start_date + datetime.timedelta(hours=hours, minutes=minutes)
            
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg='日期参数错误')
 
    # 验证区域有效性
    try:
        area = Area.query.filter_by(id=area_id).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg='区域参数错误')

    # 处理page
    if page:
        try:
            page = int(page)
        except Exception as e:
            # 如果没传入或者传入错误，让page=1
            current_app.logger.error(e)
            page = 1

    

    # 条件判断完后，先从redis拿数据
    cars_key = 'cars_info_%s%s%s%s' % (start_date, end_date, area_id, sort_key)
    try:
        resp_json = redis_connect1.hget(cars_key, page)
    except Exception as e:
        current_app.logger.error(e)
    else:
        if resp_json:
            # print('search--redis缓存')
            return resp_json, 200, {"content-Type": "application/json"}

    #     缓存没有数据
    # 根据传入的参数，组织查询条件
    # 定义查询条件list
    filter_list = []
    orders = None

    # 根据传入的日期，构造日期的查询条件
    try:
        if start_date and end_date:
            # 日期内的订单
            orders = Order.query.filter(Order.begin_date <= end_date, Order.end_date >= start_date).all()
        elif start_date:
            orders = Order.query.filter(Order.end_date >= start_date).all()
        elif end_date:
            orders = Order.query.filter(Order.begin_date >= end_date).all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='数据库异常')

    if orders:
        order_ids = [order.car_id for order in orders]
    #     排除有订单的车辆
        if order_ids:
            filter_list.append(Car.id.notin_(order_ids))

    # 构造区域条件
    if area_id:
        filter_list.append(Car.area_id == area_id)

    if sort_key == 'booking':
        cars_query = Car.query.filter(*filter_list).order_by(Car.order_count.desc())
    elif sort_key == 'price-inc':
        cars_query = Car.query.filter(*filter_list).order_by(Car.price.asc())
    elif sort_key == 'price-desc':
        cars_query = Car.query.filter(*filter_list).order_by(Car.price.desc())
    else:
        cars_query = Car.query.filter(*filter_list).order_by(Car.update_time.desc())

    #     此处才真正查询数据库，上面都是构造条件
    try:
        paginater = cars_query.paginate(page, per_page=PER_PAGE_COUNT, error_out=False)  # 自动报错设为false
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='数据库异常，查询失败')

    total_pages = paginater.pages
    # 指定page的数据
    cars = paginater.items
    cars_list = []
    for car in cars:
        cars_list.append(car.to_base_dict())

    resp_dict = dict(errno=RET.OK, errmsg='查询成功', data={'total_pages': total_pages, 'cars': cars_list, 'page': page})
    resp_json = json.dumps(resp_dict)

    # 缓存到redis
    # 采用hash存储
    cars_key = 'cars_info_%s%s%s%s' % (start_date, end_date, area_id, sort_key)
    try:
        pipeline = redis_connect1.pipeline()   # 创建管道，一次执行多条语句，避免只执行一句就没设有效期，导致数据永久有效，无法获取数据库数据
        pipeline.multi()

        redis_connect1.hset(cars_key, page, resp_json)
        redis_connect1.expire(cars_key, SEARCH_CARS_INFO_EXPIRES)

        pipeline.execute()
    except Exception as e:
        current_app.logger.error(e)

    return resp_json, 200, {"content-Type": "application/json"}




