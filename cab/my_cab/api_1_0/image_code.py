from . import api
from my_cab.utils.captcha.captcha import captcha
from my_cab import redis_connect1
from my_cab.utils import constants, response_code
from flask import current_app, jsonify, make_response


@api.route('/image_codes/<image_code_id>')
def gen_image_code(image_code_id):
    # 生成验证码信息，name 图片的内容 图片
    name, text, image_data = captcha.generate_captcha()

    # 保存到redis中
    try:
        redis_connect1.setex('image_code_%s'%image_code_id, constants.IMAGE_CODE_REDIS_EXPIRES, text)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=response_code.RET.DBERR, errmsg='保存验证码失败！')

    response = make_response(image_data)
    response.headers['Content-Type'] = 'image/jpeg'
    return response



