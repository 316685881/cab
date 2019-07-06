from . import api
from my_cab import db, models   # 此处导入为了让视图识别models，方便迁移
import logging
from flask import current_app
from my_cab import redis_connect1




@api.route('/test', methods=['GET'])
def test():
    # 第一种方式
    # logging.debug('ddddd')
    # 第二种方式
    # current_app.logger.error('eeee')
    # r = redis_connect1.get('a')
    # print(r)
    # print(type(r))
    r = 'flask test page!'
    return r
