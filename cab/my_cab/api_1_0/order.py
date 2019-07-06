from . import api
from flask import current_app, g, request, jsonify
from my_cab.utils.commons import login_required
from my_cab.utils.response_code import RET
import datetime
from my_cab.models import Car, Order
from my_cab import db
from alipay import AliPay
import os
import json
import requests
from my_cab.utils.constants import ALIPAY_DEV_URL


@api.route('/order', methods=["POST"])
@login_required
def gen_order():
    # 获取参数
    user_id = g.user_id
    req_json = request.get_json()
    begin_date = req_json.get('begin_date')
    start_point = req_json.get('start_point')
    end_point = req_json.get('end_point')
    duration = req_json.get('duration')
    mileage = req_json.get('mileage')
    amount = req_json.get('amount')
    car_id = req_json.get('car_id')

    if not req_json:
        return jsonify(errno=RET.PARAMERR, errmsg='未传参')

    if not all([begin_date, start_point, end_point, duration, mileage, amount, car_id]):
        return jsonify(errno=RET.PARAMERR, errmsg='参数不完整')

    try:
        begin_date = datetime.datetime.strptime(begin_date, "%Y-%m-%d %H:%M")
        
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg='日期参数格式错误')

    try:
        car = Car.query.filter_by(id=car_id).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='数据库异常')

    if car is None:
        return jsonify(errno=RET.NODATA, errmsg='车辆不存在')

    # 判断当前用户是不是车主 
    if user_id == car.user_id:
        return jsonify(errno=RET.ROLEERR, errmsg='不能预定自己的车辆')

    # 计算结束时间
    # 拆分duration  2.7小时
    if duration[-2:] == '分钟':
        hours = 0
        minutes = int(duration[0:-2])
    else:
        hours = int(duration[0:-4])
        minutes = int((int(duration[-3])/10)*60)
    end_date = begin_date + datetime.timedelta(hours=hours, minutes=minutes)

    # 查询车辆是否被预定了
    try:
        count = Order.query.filter(Car.id == car_id, Order.end_date >= begin_date, Order.begin_date <= end_date).count()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='数据库异常,是否被预定查询失败')

    if count > 0:
        return jsonify(errno=RET.DATAEXIST, errmsg='此车辆已被预定了')

    order = Order(
        user_id=user_id,
        car_id=car_id,
        begin_date=begin_date,
        end_date=end_date,
        start_point=start_point,
        end_point=end_point,
        duration=duration,
        mileage=float(mileage)*1000,
        price=car.price,
        amount=int(amount)*100,
        status="WAIT_ACCEPT"

    )

    try:
        db.session.add(order)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='数据库异常,保存订单失败')

    return jsonify(errno=RET.OK, errmsg='保存订单成功', data={'order_id': order.id})


@api.route('order/distance', methods=['GET'])
# @login_required
def get_two_point_distance():
    # 获取两地参数
    start_point = request.args.get('start_point')
    end_point = request.args.get('end_point')
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
            return jsonify(errno=RET.THIRDERR, errmsg='获取失败')

        else:

            distance = resp_dict['result'][0]['distance']['text'][0:-2]
            duration = resp_dict['result'][0]['duration']['text']
            # print(distance)
            # print(duration)

            return jsonify(errno=RET.OK, errmsg='获取成功', data={'distance': distance, 'duration': duration})


@api.route('/order/booking/<int:car_id>', methods=['GET'])
# @login_required    #登录验证 获取不到参数。,url里参数传不下来
def booking_car(car_id):
    # print(car_id)

    try:

        # print(type(car_id))
        car = Car.query.filter_by(id=car_id).first()
        # print(car)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='数据库异常,获取车辆信息失败')

    if car is None:
        return jsonify(errno=RET.NODATA, errmsg='车辆不存在')

    return jsonify(errno=RET.OK, errmsg='查询车辆成功', data={'car': car.to_base_dict()})


@api.route('/user/orders', methods=['GET'])
@login_required
def get_orders():
    user_id = g.user_id

    # 获取想要以顾客还是车主的身份查询订单的flag
    role = request.args.get('role', '')

    # 以车主身份查询订单
    try:
        if role == 'role':
            cars = Car.query.filter(Car.user_id == user_id).all()
            car_ids = [car.id for car in cars]
            orders = Order.query.filter(Order.car_id.in_(car_ids)).order_by(Order.create_time.desc()).all()

        else:
            orders = Order.query.filter_by(user_id=user_id).order_by(Order.create_time.desc()).all()

    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='数据库异常,获取订单信息失败')

    order_dict_list = []
    if orders:
        for order in orders:
            order_dict_list.append(order.to_dict())

    if order_dict_list:

        return jsonify(errno=RET.OK, errmsg='获取订单数据ok', data={'orders': order_dict_list})
    else:
        return jsonify(errno=RET.OK, errmsg='没有订单', data={'orders': ''})


@api.route('/order/status', methods=["PUT"])
@login_required
def accept_reject_order():
    user_id = g.user_id

    req_json = request.get_json()

    if not req_json:
        return jsonify(errno=RET.PARAMERR, errmsg='没有参数')

    action = req_json.get('action')
    order_id = req_json.get('order_id')

    if not all([action, order_id]):
        return jsonify(errno=RET.PARAMERR, errmsg='参数不完整')

    if action not in ('accept', 'reject'):
        return jsonify(errno=RET.PARAMERR, errmsg='参数错误')

    try:
        order = Order.query.filter(Order.id == order_id, Order.status == 'WAIT_ACCEPT').first()
        car = order.car
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='数据库异常')

    if order is None and car.user_id != user_id:
        return jsonify(errno=RET.DBERR, errmsg='非法操作')

    if action == 'accept':
        order.status = 'WAIT_PAYMENT'

    if action == 'reject':
        order.status = 'REJECTED'
        order.comment = req_json.get('reject_reason')
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='数据库异常')

    return jsonify(errno=RET.OK, errmsg='操作成功')


@api.route('/order/payment', methods=['POST'])
@login_required
def order_pay():
    user_id = g.user_id

    req_json = request.get_json()
    if not req_json:
        return jsonify(errno=RET.PARAMERR, errmsg='没有传参')

    order_id = req_json.get('order_id')
    if not all([order_id]):
        return jsonify(errno=RET.PARAMERR, errmsg='参数不全')

    try:
        order = Order.query.filter(Order.id == order_id, Order.user_id == user_id, Order.status == 'WAIT_PAYMENT').first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='数据库异常')

    if not order:
        return jsonify(errno=RET.DBERR, errmsg='订单无效')

#     利用第三方sdk构造支付链接
    alipay_client = AliPay(
        appid='2016092500592996',
        app_notify_url=None,
        app_private_key_path=os.path.join(os.path.dirname(__file__) + '/keys/app_private_key.pem'),
        alipay_public_key_path=os.path.join(os.path.dirname(__file__) + '/keys/alipay_public_key.pem'),
        sign_type='RSA2',
        debug=True
    )

    pay_string = alipay_client.api_alipay_trade_wap_pay(
        out_trade_no=order_id,
        total_amount=str(order.amount/100.0),
        subject='用车订单：%s' % order_id,
        return_url='http://192.168.199.197:5000/payresult.html',
        notify_url=None
    )

    pay_url = ALIPAY_DEV_URL + pay_string

    return jsonify(errno=RET.OK, errmsg='构造支付url成功', data={'pay_url': pay_url})


@api.route('/order/payment', methods=['PUT'])
@login_required
def pay_result_update_order():
    # 获取传来的form参数，并变成字典
    result_dict = request.form.to_dict()
    # 取出sign值，并在result_dict中删掉
    sign = result_dict.pop('sign')
    alipay_client = AliPay(
        appid='2016092500592996',
        app_notify_url=None,
        app_private_key_path=os.path.join(os.path.dirname(__file__) + '/keys/app_private_key.pem'),
        alipay_public_key_path=os.path.join(os.path.dirname(__file__) + '/keys/alipay_public_key.pem'),
        sign_type='RSA2',
        debug=True
    )

    pay_flag = alipay_client.verify(result_dict, sign)

    if pay_flag:
        order_id = result_dict.get('out_trade_no')
        trade_no = result_dict.get('trade_no')

        try:
            order = Order.query.filter_by(id=order_id).first()
            order.status = 'WAIT_COMMENT'
            order.trade_no = trade_no
            order.car.order_count += 1
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR, errmsg='付款失败')

    return jsonify(errno=RET.OK, errmsg='付款成功')


@api.route('/order/comment', methods=['PUT'])
@login_required
def update_order_comment():
    user_id = g.user_id
    req_json = request.get_json()

    if not req_json:
        return jsonify(errno=RET.PARAMERR, errmsg='没有传参')

    order_id = req_json.get('order_id')
    comment = req_json.get('comment')

    if not all([order_id, comment]):
        return jsonify(errno=RET.PARAMERR, errmsg='参数不全')

    try:
        order = Order.query.filter(Order.id == order_id, Order.user_id == user_id, Order.status == 'WAIT_COMMENT').first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='数据库异常')

    if not order:
        return jsonify(errno=RET.NODATA, errmsg='订单不存在，评论失败')

    try:
        order.status = 'COMPLETE'
        order.comment = comment
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='数据库异常')

    return jsonify(errno=RET.OK, errmsg='评论成功')
