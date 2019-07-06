from . import api
from flask import request, jsonify, current_app, g, session
from my_cab.utils import response_code, image_storage, constants
from my_cab.utils.commons import login_required, check_id_card
from my_cab.models import User
from my_cab import db
from sqlalchemy.exc import IntegrityError



# 上传头像
@api.route('/user/head', methods=['POST', 'GET'])
@login_required
def upload_head():
    if request.method =='GET':
        #     页面加载是初始化头像
        # 先从session中拿头像地址
        image_url = session.get('image_url')
        if image_url is not None:
            return jsonify(errno=response_code.RET.OK, errmsg='获取头像成功', data={"image_url": image_url})
        else:

            # session中不存在,则查询数据库
            try:
                user = User.query.filter_by(id=g.user_id).first()
            except Exception as e:
                current_app.logger.error(e)
            else:
                if not user.avatar_url:
                    return jsonify(errno=response_code.RET.NODATA, errmsg='用户头像不存在')
                else:

                    image_url = constants.QINIU_IMAGE_STORE_DOMAIN + user.avatar_url

                    return jsonify(errno=response_code.RET.OK, errmsg='获取头像成功', data={"image_url": image_url})

    else:
        # 获取参数
        image_file = request.files.get('avatar')

        # 判断是否传参
        if image_file is None:
            return jsonify(errno=response_code.RET.PARAMERR, errmsg='无要上传的文件')

        image_data = image_file.read()
        try:
            image_name = image_storage.store(image_data)
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=response_code.RET.THIRDERR, errmsg='上传文件失败')

        # 把图片名存入数据库
        try:
            User.query.filter_by(id=g.user_id).update({"avatar_url": image_name})
            db.session.commit()
        except Exception as e:
            # 保存失败回滚
            db.session.rollback()
            current_app.logger.error(e)
            return jsonify(errno=response_code.RET.DBERR, errmsg='数据库异常,保存图片地址失败')

        # 拼接图片完整地址
        image_url = constants.QINIU_IMAGE_STORE_DOMAIN + image_name
        # print(image_url)
        # 设置session
        session['image_url'] = image_url
        # 保存成功,返回数据
        return jsonify(errno=response_code.RET.OK, errmsg='保存图片成功', data={"image_url": image_url})


# 更改用户名
@api.route('/user/username', methods=['POST', 'GET'])
@login_required
def update_username():
    # 更改用户初始化
    if request.method == "GET":
        return jsonify(errno=response_code.RET.OK, errmsg='获取用户名成功', data={"username": session.get('username')})
    else:
        # 获取参数
        username = request.get_json().get('username')

    #     验证参数
        if not all([username]):
            return jsonify(errno=response_code.RET.PARAMERR, errmsg='用户名为空')

    #     查询数据库,验证用户名是否已经存在
        try:
            user = User.query.filter_by(id=g.user_id)
            if user.first().name != username:
                user.update({'name': username})
                db.session.commit()
            else:
                return jsonify(errno=response_code.RET.DATAEXIST, errmsg='该用户名已经存在')
        except IntegrityError as e:
            db.session.rollback()
            current_app.logger.error(e)
            return jsonify(errno=response_code.RET.DATAEXIST, errmsg='该用户名已经存在')
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(e)
            return jsonify(errno=response_code.RET.DBERR, errmsg='数据库异常')
        session['username'] = username
        return jsonify(errno=response_code.RET.OK, errmsg='更改用户名成功')


# 实名认证
@api.route('/user/auth', methods=['POST', 'GET'])
@login_required
def user_auth():
    # 实名数据初始化
    if request.method == 'GET':
        try:
            user = User.query.filter_by(id=g.user_id).first()
        except Exception as e:
            current_app.logger.error(e)
        else:
            if not user.real_name:
                return jsonify(errno=response_code.RET.NODATA, errmsg='未实名')
            else:
                return jsonify(errno=response_code.RET.OK, errmsg='已实名',
                               data={"real_name": user.real_name, "id_card": user.id_card})
    else:

        # 获取参数
        param_json = request.get_json()
        real_name = param_json.get('real_name')
        id_card = param_json.get('id_card')
        # print(id_card)

        # 验证参数完整性
        if not all([real_name, id_card]):
            return jsonify(errno=response_code.RET.PARAMERR, errmsg='参数不完整')

        # 验证身份证
        result = check_id_card(id_card)
        if result != '验证通过!':
            return jsonify(errno=response_code.RET.PARAMERR, errmsg=result)

        # 验证通过插入数据库
        try:
            # 只能实名验证 一次,只更新真实姓名跟身份证都不存在的user
            User.query.filter_by(id=g.user_id, real_name=None, id_card=None).update({'real_name': real_name, 'id_card': id_card})
            db.session.commit()
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=response_code.RET.DBERR, errmsg='数据库异常')

        return jsonify(errno=response_code.RET.OK, errmsg='认证成功',
                       data={"real_name": real_name, "id_card": id_card})


@api.route('/user/my', methods=['GET'])
@login_required
def profile():
    username = session.get('username')
    phone = session.get('phone')
    user_head = session.get('image_url')
    return jsonify(errno=response_code.RET.OK, errmsg='获取成功', data={"username": username, "phone": phone, 'user_head':user_head})



 














