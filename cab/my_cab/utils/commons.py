from werkzeug.routing import BaseConverter
from flask import session, jsonify, g
from my_cab.utils import response_code
import functools
import re


# 定义正则转换器
class ReConverter(BaseConverter):
    def __init__(self, url_map, regex):
        # 调用父类的初始化方法
        super(ReConverter, self).__init__(url_map)
        # 保存正则表达式
        self.regex = regex


# 登录装饰器
def login_required(func):

    @functools.wraps(func)   # 此装饰器作用是恢复传入函数的所有状态,如func.__name__, func.__doc__等
    def inner(*args, **kwargs):
        user_id = session.get('user_id')
        if user_id is not None:
            # 如果登录了,把登录信息存入g对象中,方便传入的视图函数调用
            g.user_id = user_id
            print(*args, *kwargs)
            return func(*args, *kwargs)
        else:
            return jsonify(errno=response_code.RET.SESSIONERR, errmsg='未登录')

    return inner


# errors=['验证通过!','身份证号码位数不对!','身份证号码出生日期超出范围或含有非法字符!','身份证号码校验错误!','身份证地区非法!']
def check_id_card(id_card):
    errors = ['验证通过!', '身份证号码位数不对!', '身份证号码出生日期超出范围或含有非法字符!', '身份证号码校验错误!', '身份证地区非法!']
    area = {"11": "北京", "12": "天津", "13": "河北", "14": "山西", "15": "内蒙古", "21": "辽宁", "22": "吉林", "23": "黑龙江",
            "31": "上海",
            "32": "江苏", "33": "浙江", "34": "安徽", "35": "福建", "36": "江西", "37": "山东", "41": "河南", "42": "湖北", "43": "湖南",
            "44": "广东", "45": "广西", "46": "海南", "50": "重庆", "51": "四川", "52": "贵州", "53": "云南", "54": "西藏", "61": "陕西",
            "62": "甘肃", "63": "青海", "64": "宁夏", "65": "新疆", "71": "台湾", "81": "香港", "82": "澳门", "91": "国外"}
    id_card = str(id_card)
    id_card = id_card.strip()
    id_card_list = list(id_card)

    # 地区校验
    key = id_card[0: 2]  # TODO： cc  地区中的键是否存在
    if key in area.keys():
        if not area[id_card[0:2]]:
            return errors[4]
    else:
        return errors[4]
    # 15位身份号码检测

    if len(id_card) == 15:
        if (int(id_card[6:8]) + 1900) % 4 == 0 or (
                (int(id_card[6:8]) + 1900) % 100 == 0 and (int(id_card[6:8]) + 1900) % 4 == 0):
            ereg = re.compile(
                '[1-9][0-9]{5}[0-9]{2}((01|03|05|07|08|10|12)(0[1-9]|[1-2][0-9]|3[0-1])|(04|06|09|11)(0[1-9]|[1-2][0-9]|30)|02(0[1-9]|[1-2][0-9]))[0-9]{3}$')  # //测试出生日期的合法性
        else:
            ereg = re.compile(
                '[1-9][0-9]{5}[0-9]{2}((01|03|05|07|08|10|12)(0[1-9]|[1-2][0-9]|3[0-1])|(04|06|09|11)(0[1-9]|[1-2][0-9]|30)|02(0[1-9]|1[0-9]|2[0-8]))[0-9]{3}$')  # //测试出生日期的合法性
        if re.match(ereg, id_card):
            return errors[0]
        else:
            return errors[2]
    # 18位身份号码检测
    elif len(id_card) == 18:
        # 出生日期的合法性检查
        # 闰年月日:((01|03|05|07|08|10|12)(0[1-9]|[1-2][0-9]|3[0-1])|(04|06|09|11)(0[1-9]|[1-2][0-9]|30)|02(0[1-9]|[1-2][0-9]))
        # 平年月日:((01|03|05|07|08|10|12)(0[1-9]|[1-2][0-9]|3[0-1])|(04|06|09|11)(0[1-9]|[1-2][0-9]|30)|02(0[1-9]|1[0-9]|2[0-8]))
        if int(id_card[6:10]) % 4 == 0 or (int(id_card[6:10]) % 100 == 0 and int(id_card[6:10]) % 4 == 0):
            ereg = re.compile(
                '[1-9][0-9]{5}(19[0-9]{2}|20[0-9]{2})((01|03|05|07|08|10|12)(0[1-9]|[1-2][0-9]|3[0-1])|(04|06|09|11)(0[1-9]|[1-2][0-9]|30)|02(0[1-9]|[1-2][0-9]))[0-9]{3}[0-9Xx]$')  # //闰年出生日期的合法性正则表达式
        else:
            ereg = re.compile(
                '[1-9][0-9]{5}(19[0-9]{2}|20[0-9]{2})((01|03|05|07|08|10|12)(0[1-9]|[1-2][0-9]|3[0-1])|(04|06|09|11)(0[1-9]|[1-2][0-9]|30)|02(0[1-9]|1[0-9]|2[0-8]))[0-9]{3}[0-9Xx]$')  # //平年出生日期的合法性正则表达式
        # //测试出生日期的合法性
        if re.match(ereg, id_card):
            # //计算校验位
            s = (int(id_card_list[0]) + int(id_card_list[10])) * 7 + (int(id_card_list[1]) + int(id_card_list[11])) * 9 \
                + (int(id_card_list[2]) + int(id_card_list[12])) * 10 + (int(id_card_list[3]) + int(id_card_list[13])) * 5\
                + (int(id_card_list[4]) + int(id_card_list[14])) * 8 + (int(id_card_list[5]) + int(id_card_list[15])) * 4 \
                + (int(id_card_list[6]) + int(id_card_list[16])) * 2 + int(id_card_list[7]) * 1 + int(id_card_list[8]) * 6\
                + int(id_card_list[9]) * 3
            y = s % 11
            m = "F"
            jym = "10X98765432"
            m = jym[y]  # 判断校验位
            if m == id_card_list[17]:  # 检测ID的校验位
                return errors[0]
            else:
                return errors[3]
        else:
            return errors[2]
    else:
        return errors[1]
