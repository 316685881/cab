import logging
import redis
from flask import Flask
from config import config_map
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
from flask_wtf import CSRFProtect
from logging.handlers import RotatingFileHandler
from my_cab.utils.commons import ReConverter


# 数据库
db = SQLAlchemy()

# 定义redis链接
redis_connect = None
redis_connect1 = None


# 设置日志
logging.basicConfig(level=logging.DEBUG)  # 设置日志级别
# 设置日志记录器，指明日志路径，单个日志文件大小，最多日志文件数量
file_log_handler = RotatingFileHandler('logs/log', maxBytes=1024*1024*100, backupCount=10)
# 创建日志记录的格式
formatter = logging.Formatter('%(levelname)s %(filename)s:%(lineno)d %(message)s')
# 为记录器设置记录格式
file_log_handler.setFormatter(formatter)
# 为全局日志对象添加记录器
logging.getLogger().addHandler(file_log_handler)


def create_app(config_name):
    '''
    创建flask应用对象
    :param config_name:  str    配置模式名字    【‘develop’,'product'】
    :return:
    '''
    app = Flask(__name__)

    config_class = config_map.get(config_name)
    app.config.from_object(config_class)

    # 初始化db
    db.init_app(app)

    # 创建redis链接
    global redis_connect, redis_connect1
    redis_connect = redis.StrictRedis(host=config_class.REDIS_HOST, port=config_class.REDIS_PORT)
    # 添加decode_responses=True查询出来的就不是byte数据了,而是str
    redis_connect1 = redis.StrictRedis(host=config_class.REDIS_HOST, port=config_class.REDIS_PORT, db=8, decode_responses=True)

    # 利用flask-session，讲session保存到redis中
    Session(app)

    # 开启csrf保护
    CSRFProtect(app)

    # 在注册蓝图之前为flask添加正则转换器
    app.url_map.converters['re'] = ReConverter

    # 注册蓝图
    from my_cab import api_1_0  # 使用是导入，不然会出现循环导包
    app.register_blueprint(api_1_0.api, url_prefix='/api/v1.0')

    # 注册提供静态文件的蓝图
    from my_cab import web_static
    app.register_blueprint(web_static.web_static_blueprint)

    # 注册微信蓝图
    from my_cab import micromsg
    app.register_blueprint(micromsg.macromsg_buleprint)

    return app
