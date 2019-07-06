from flask import Blueprint, request, make_response, abort, jsonify
from my_cab.utils.response_code import RET
import hashlib
import xmltodict
import time


TOKEN = 'python'

macromsg_buleprint = Blueprint('macromsg', __name__)


@macromsg_buleprint.route('/hello')
def hello_world():

    return jsonify(errno=RET.OK, errmsg='hello--macromsg')


@macromsg_buleprint.route('/micromsg5000', methods=['GET', 'POST'])
def micromsg_handler():
    timestamp = request.args.get('timestamp')
    nonce = request.args.get('nonce')
    str_list = [TOKEN, timestamp, nonce]
    str_list.sort()
    list_str = ''.join(str_list)
    new_signature = hashlib.sha1(list_str.encode('utf-8')).hexdigest()   # hashlib.sha1得到的是对象，需要通过hexdigest取内容
    if new_signature != request.args.get('signature'):
        abort(403)
    else:
        if request.method == 'GET':
            echostr = request.args.get('echostr')
            if not echostr:
                abort(400)
            return make_response(echostr)
        elif request.method == 'POST':
            xml_str = request.data
            if not xml_str:
                abort(400)
            xml_dict = xmltodict.parse(xml_str).get('xml')
            msg_type = xml_dict.get('MsgType')
            from_user = xml_dict.get('ToUserName')
            to_user = xml_dict.get('FromUserName')
            # 文本消息
            if msg_type == 'text':
                content = xml_dict.get('Content')
                response_dict = {
                    'xml': {
                        'ToUserName': to_user,
                        'FromUserName': from_user,
                        'CreateTime': int(time.time()),
                        'MsgType': 'text',
                        'Content': content
                    }
                }

                response_xml = xmltodict.unparse(response_dict)
            # 图片消息
            elif msg_type == 'image':
                pic_url = xml_dict.get('PicUrl')
                # MediaId = xml_dict.get('MediaId')
                # MsgId = xml_dict.get('MsgId')
                response_dict = {
                    'xml': {
                        'ToUserName': to_user,
                        'FromUserName': from_user,
                        'CreateTime': int(time.time()),
                        'MsgType': 'text',
                        'PicUrl': pic_url,
                        'Content': '收到图片:'+pic_url

                    }
                }
                print(response_dict)
                response_xml = xmltodict.unparse(response_dict)
            # 音频消息
            elif msg_type == 'voice':
                MediaId = xml_dict.get('MediaId')
                Format = xml_dict.get('Format')

                response_dict = {
                    'xml': {
                        'ToUserName': to_user,
                        'FromUserName': from_user,
                        'CreateTime': int(time.time()),
                        'MsgType': 'voice',
                        'Format': Format,
                        'MediaId': MediaId
                    }
                }
                response_xml = xmltodict.unparse(response_dict)
            # 视频消息
            elif msg_type == 'video':
                MediaId = xml_dict.get('MediaId')
                ThumbMediaId = xml_dict.get('ThumbMediaId')

                response_dict = {
                    'xml': {
                        'ToUserName': to_user,
                        'FromUserName': from_user,
                        'CreateTime': int(time.time()),
                        'MsgType': 'video',
                        'ThumbMediaId': ThumbMediaId,
                        'MediaId': MediaId
                    }
                }
                response_xml = xmltodict.unparse(response_dict)

            # 短视频消息
            elif msg_type =='shortvideo':
                MediaId = xml_dict.get('MediaId')
                ThumbMediaId = xml_dict.get('ThumbMediaId')

                response_dict = {
                    'xml': {
                        'ToUserName': to_user,
                        'FromUserName': from_user,
                        'CreateTime': int(time.time()),
                        'MsgType': 'shortvideo',
                        'ThumbMediaId': ThumbMediaId,
                        'MediaId': MediaId
                    }
                }
                response_xml = xmltodict.unparse(response_dict)

            # 位置消息
            elif msg_type == 'location':
                Location_X = xml_dict.get('Location_X')
                Location_Y = xml_dict.get('Location_Y')
                Scale = xml_dict.get('Scale')
                Label = xml_dict.get('Label')

                response_dict = {
                    'xml': {
                        'ToUserName': to_user,
                        'FromUserName': from_user,
                        'CreateTime': int(time.time()),
                        'MsgType': 'location',
                        'Location_X': Location_X,
                        'Location_Y': Location_Y,
                        'Scale': Scale,
                        'Label': Label
                    }
                }
                response_xml = xmltodict.unparse(response_dict)

            elif msg_type == 'link':
                Title = xml_dict.get('Title')
                Description = xml_dict.get('Description')
                Url = xml_dict.get('Url')

                response_dict = {
                    'xml': {
                        'ToUserName': to_user,
                        'FromUserName': from_user,
                        'CreateTime': int(time.time()),
                        'MsgType': 'link',
                        'Title': Title,
                        'Description': Description,
                        'Url': Url

                    }
                }
                response_xml = xmltodict.unparse(response_dict)

            else:
                response_dict = {
                    'xml': {
                        'ToUserName': to_user,
                        'FromUserName': from_user,
                        'CreateTime': int(time.time()),
                        'MsgType': 'text',
                        'Content': '你的消息已收到，但我不知道怎么回答[捂脸]'
                    }
                }
                response_xml = xmltodict.unparse(response_dict)
            return make_response(response_xml)
