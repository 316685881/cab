# -*- coding: utf-8 -*-
# flake8: noqa
from qiniu import Auth, put_data


# 需要填写你的 Access Key 和 Secret Key
access_key = '8yXO0ZE0XN2hxjUvnQvbJWyraR921NhILuNpkca7'
secret_key = 'bB7jwkOrSJRWpQpo3ETzdbieNYTLmQEaEnL3hmeY'

# 构建鉴权对象
q = Auth(access_key, secret_key)

# 上传的空间名称
bucket_name = 'tenant'


# 上传方法
def store(file_data):

    # 生成上传 Token，可以指定过期时间等
    token = q.upload_token(bucket_name, None, 3600)

    ret, info = put_data(token, None, file_data)
    # print(type(info.status_code))
    # print(ret)

    if info.status_code == 200:
        return ret.get('key')
    else:
        raise Exception('上传图片失败')
