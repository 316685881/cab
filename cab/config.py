import redis


class Config(object):
    DEBUG = True

    SECRET_KEY = 'cab'

    # 数据库配置，python3需要加pymysql
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:root@127.0.0.1:3306/cab_db'
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    # 配置redis
    REDIS_HOST = '127.0.0.1'
    REDIS_PORT = 6379

    # flask-session 配置
    SESSION_TYPE = 'redis'
    SESSION_REDIS = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT)
    SESSION_USE_SIGNER = True  # 对cookie中的session隐藏
    PERMANENT_SESSION_LIFETIME = 604800  # session有效期,单位秒,7天


# 开发配置
class DevelopmentConfig(Config):
    DEBUG = True


# 生产配置
class ProductionConfig(Config):
    pass

# 定义配置映射
config_map = {
    'develop': DevelopmentConfig,
    'product': ProductionConfig
}