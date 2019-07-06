from . import api
from flask import request, jsonify, current_app
from my_cab.utils import response_code
from my_cab import redis_connect1
from my_cab.models import User
from my_cab.libs.ronglianyun.SendTemplateSMS import CCP
from my_cab.utils.constants import SMS_CODE_EXPIRES, SEND_SMS_EXPIRES
from my_cab.tasks import celery_tasks

import random


# 发送短信验证码
# 发送短信验证码的url: '/api/v1.0/sms/<phone>?image_code=xxx&image_code_id=xxx'
@api.route("/sms/<re(r'1[345678]\d{9}'):phone>")
def send_sms(phone):
    # 验证图片验证码
    # 获取前段传来的验证码及id
    image_code = request.args.get('image_code')
    image_code_id = request.args.get('image_code_id')
    print('get: ' + image_code)

    # 验证参数完整性
    # 参数不完整
    if not all([image_code, image_code_id]):
        return jsonify(errno=response_code.RET.PARAMERR, errmsg='验证码参数不完整')

    # 参数完整,验证图片验证码
    # 从数据库中获取验证码
    try:
        real_image_code = redis_connect1.get('image_code_%s'%image_code_id)
        # print(real_image_code)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=response_code.RET.DBERR, errmsg='验证码已过期')

    # 如果验证码为空
    if real_image_code is None:
        return jsonify(errno=response_code.RET.NODATA, errmsg='验证码已过期')

    # 删除验证码,防止一个验证码用两次
    try:
        redis_connect1.delete('image_code_%s' % image_code_id)
    except Exception as e:
        current_app.logger.error(e)

    print('redis: ' + real_image_code)
    if image_code.upper() != real_image_code.upper():
        # print(image_code+'--'+real_image_code)
        return jsonify(errno=response_code.RET.PARAMERR, errmsg='图片验证码错误')

    else:
        print('图片验证码ok')

#   此时验证码验证通过,发送短信验证码
#     判断60s内是否发过短信
    try:
        send_flag = redis_connect1.get('send_phone_%s' % phone)
    except Exception as e:
        current_app.logger.error(e)
    else:
        if send_flag is not None:
            return jsonify(errno=response_code.RET.REQERR, errmsg='操作频繁,请稍后再试')

#
#   判断手机号是否注册过
    try:
        user = User.query.filter_by(mobile=phone).first()
    except Exception as e:
        current_app.logger.error(e)
    else:
        if user is not None:
            return jsonify(errno=response_code.RET.DATAEXIST, errmsg='此手机号已经注册')


    # 发送短信
    # 构造参数
    # 随机生产一个整数,不满6位则在前面补0
    sms_code = '%06d'%random.randint(0, 999999)
    # 保存短信验证码信息到redis中
    try:
        redis_connect1.setex('sms_code_%s' % phone, SMS_CODE_EXPIRES, sms_code)
        redis_connect1.setex('send_phone_%s' % phone, SEND_SMS_EXPIRES, 1)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=response_code.RET.DBERR, errmsg='保存短信验证码失败')

    data = [sms_code, int(SMS_CODE_EXPIRES/60)]

    # 原始发送短信代码****************************
    ccp = CCP()
    try:
        result = ccp.send_template_sms(phone, data, 1)
        # print(type(result))
        print(result)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=response_code.RET.THIRDERR, errmsg='短信发送异常')
    else:

        if result.get('statusCode') == '000000':
            return jsonify(errno=response_code.RET.OK, errmsg='短信已发送')
        else:
            return jsonify(errno=response_code.RET.THIRDERR, errmsg='短信发送失败')


# #   使用celery发送短信******************************
#     celery_tasks.send_sms.delay(phone, data, 1)

    return jsonify(errno=response_code.RET.OK, errmsg='短信已发送')


