from flask import Blueprint, current_app, make_response
from flask_wtf import csrf


# 提供静态文件的蓝图
web_static_blueprint = Blueprint('web_static', __name__)


# 通过正则匹配静态资源
@web_static_blueprint.route("/<re(r'.*'):filename>")
def get_static_file(filename):
    # 如果访问到'/',指定为’index.html‘
    if not filename:
        filename = 'index.html'

    # 如果不是访问的为网站表示’favicon。ico‘,拼接路径，否则直接返回filename
    if filename != 'favicon.ico':
        filename = 'html/' + filename

    # 在cookie中设置csrf
    response = make_response(current_app.send_static_file(filename))
    # 生成一个csrf_token
    csrf_token = csrf.generate_csrf()
    # 把生产的csrf_token添加到cookie中
    response.set_cookie('csrf_token', csrf_token)

    return response
