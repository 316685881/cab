# 图片验证码过期时间,单位s
IMAGE_CODE_REDIS_EXPIRES = 300

# 短信验证码过期时间,单位s
SMS_CODE_EXPIRES = 300

# 短信发送间隔时间,单位s
SEND_SMS_EXPIRES = 60

# 用户登录错误次数超过限制等待时间,单位s
USER_ERROR_EXPIRES = 600

# 用户登录错误最大次数
USER_ERROR_MAX_NUM = 5

# 七牛云图片存储域名
QINIU_IMAGE_STORE_DOMAIN = 'http://ptl2de8cp.bkt.clouddn.com/'

# 区域数据存在redis中 有效期
AREA_INFO_EXPIRES = 3600

# 配置数据存在redis中 有效期
FACILITY_INFO_EXPIRES = 3600

# 主页显示的房子数量
INDEX_PAGE_CAR_MAX_COUNT = 5

# 主页房子信息在redis中过期时间
INDEX_PAGE_CAR_EXPIRES = 20

# 房子评论数限制
CAR_COMMENT_MAX_COUNT = 30

# 房子详情redis中有效期
HOUER_DETAIL_INFO_EXPIRES = 30

# 每页的数据数量
PER_PAGE_COUNT = 2

# 搜索数据存储有效期
SEARCH_CARS_INFO_EXPIRES = 30

# 支付宝的沙箱网关
ALIPAY_DEV_URL = 'https://openapi.alipaydev.com/gateway.do?'

