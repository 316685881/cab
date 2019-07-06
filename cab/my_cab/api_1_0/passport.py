from . import api
from flask import request, jsonify,current_app, session
from my_cab.utils import response_code
from my_cab import redis_connect1, db
from my_cab.models import User
from sqlalchemy.exc import IntegrityError  # 导入mysql数据库唯一性的异常类
from my_cab.utils import constants
from my_cab.utils.commons import login_required


# 注册
@api.route('/user', methods=['POST'])
def register():
    # 获取参数
    parm_json = request.get_json()
    phone = parm_json.get('mobile')
    sms_code = parm_json.get('sms_code')
    password = parm_json.get('password')
    password2 = parm_json.get('password2')

    # 验证参数
    # 验证参数完整性
    if not all([phone, sms_code, password, password2]):
        return jsonify(errno=response_code.RET.PARAMERR, errmsg='参数不完整')

    # 验证两次密码是否一致
    if password2 != password:
        return jsonify(errno=response_code.RET.PARAMERR, errmsg='两次密码不一致')

    # 验证短信验证码
    # 从redis中取验证码,并验证
    try:
        real_sms_code = redis_connect1.get('sms_code_%s' % phone)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=response_code.RET.DBERR, errmsg='数据库异常,取出验证码失败')
    else:
        if real_sms_code is None:
            return jsonify(errno=response_code.RET.NODATA, errmsg='短信验证码已过期')
        if sms_code != real_sms_code:
            return jsonify(errno=response_code.RET.DATAERR, errmsg='短信验证码错误')
        else:
            print('验证码验证ok')

    # 验证密码
    # 从mysql中取出密码并验证
    # 这步可以跟添加用户合并,以为mobile已经在数据库中定义为唯一性

    # 添加用户
    user = User(name=phone, mobile=phone)
    # 在数据库模板中User类中定义一个密码生成的方法,并用@property装饰,让password成为属性
    user.password = password

    try:
        db.session.add(user)
        db.session.commit()
    except IntegrityError as e:
        # 手机号已存在的异常,数据库回滚
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(errno=response_code.RET.DATAEXIST, errmsg='此手机号已经被注册')
    except Exception as e:
        # 其他异常,数据库回滚
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(errno=response_code.RET.DBERR, errmsg='数据库异常,注册失败')

    # 保存登录状态信息到session中
    session['user_id'] = user.id
    session['username'] = user.name
    session['phone'] = user.mobile
    if user.avatar_url:
        image_url = constants.QINIU_IMAGE_STORE_DOMAIN + user.avatar_url
        session['image_url'] = image_url

    return jsonify(errno=response_code.RET.OK, errmsg='注册成功', data={"username": user.name})


# 登录
@api.route('/session', methods=['POST'])
def login():

    # 获取登录参数
    param_json = request.get_json()
    print(param_json)
    phone = param_json.get('mobile')
    password = param_json.get('password')

    # 验证参数
    if not all([phone, password]):
        return jsonify(errno=response_code.RET.PARAMERR, errmsg='登录参数不完整')

    # 验证登录错误次数,判断是否允许登录
    try:
        user_login_err_num = redis_connect1.get('user_error_%s' % phone)
    except Exception as e:
        current_app.logger.error(e)
    else:
        if user_login_err_num is not None and user_login_err_num > constants.USER_ERROR_MAX_NUM:
            return jsonify(errno=response_code.RET.REQERR,
                           errmsg='错误次数大于' + constants.USER_ERROR_MAX_NUM + '次,请' +
                                  str(int(constants.USER_ERROR_EXPIRES/60)) + '分钟后再试')

    # 验证登录
    try:
        user = User.query.filter_by(mobile=phone).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=response_code.RET.DBERR, errmsg='数据库异常,登录失败')
    else:
        # 用户不存在或者密码错误,都返回用户名或者密码错误
        if user is None or not user.check_password(password):
            try:
                # 记录错误次数在redis中,使用incr方法,添加一次自动加1,初始为1,并添加过期时间
                num = redis_connect1.incr('user_error_%s' % phone)
                redis_connect1.expire('user_error_%s' % phone, constants.USER_ERROR_EXPIRES)
            except Exception as e:
                current_app.logger.error(e)
            else:
                return jsonify(errno=response_code.RET.LOGINERR, errmsg='用户名或密码错误', data={"err_num": num})

    # 登录成功
    # 设置session保存登录状态
    session['user_id'] = user.id
    session['username'] = user.name
    session['phone'] = user.mobile
    if user.avatar_url is not None:

        image_url = constants.QINIU_IMAGE_STORE_DOMAIN + user.avatar_url
        session['image_url'] = image_url

    return jsonify(errno=response_code.RET.OK, errmsg='登录成功', data={"username": user.name})


# 检查登录状态
@api.route('/session', methods=['GET'])
def check_login():
    # 检查session中是否存在
    username = session.get('username')
    if username is not None:
        return jsonify(errno=response_code.RET.OK, errmsg='已登录', data={"username": username})
    else:
        return jsonify(errno=response_code.RET.SESSIONERR, errmsg='未登录')


# 退出
@api.route('/session', methods=['DELETE'])
@login_required
def logout():
    # flask会从session中拿csrf去校验，所以不能完全清除session，要保留csrf
    csrf_token = session.get('csrf_token')
    session.clear()
    session['csrf_token'] = csrf_token
    return jsonify(errno=response_code.RET.OK, errmsg='登出成功')
























