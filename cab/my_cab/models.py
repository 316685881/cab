# -*- coding:utf-8 -*-

from datetime import datetime
from . import db
from werkzeug.security import generate_password_hash, check_password_hash
from my_cab.utils.constants import QINIU_IMAGE_STORE_DOMAIN, CAR_COMMENT_MAX_COUNT


class BaseModel(object):
    """模型基类，为每个模型补充创建时间与更新时间"""

    create_time = db.Column(db.DateTime, default=datetime.now)  # 记录的创建时间
    update_time = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)  # 记录的更新时间


class User(BaseModel, db.Model):
    """用户"""

    __tablename__ = "cab_user_profile"

    id = db.Column(db.Integer, primary_key=True)  # 用户编号
    name = db.Column(db.String(32), unique=True, nullable=False)  # 用户暱称
    password_hash = db.Column(db.String(128), nullable=False)  # 加密的密码
    mobile = db.Column(db.String(11), unique=True, nullable=False)  # 手机号
    real_name = db.Column(db.String(32))  # 真实姓名
    id_card = db.Column(db.String(20))  # 身份证号
    avatar_url = db.Column(db.String(128))  # 用户头像路径
    cars = db.relationship("Car", backref="user")  # 用户发布的车辆
    orders = db.relationship("Order", backref="user")  # 用户下的订单

    # 加上property装饰器后，会把函数变为属性，属性名即为函数名
    @property
    def password(self):
        """读取属性的函数行为"""
        # print(user.password)  # 读取属性时被调用
        # 函数的返回值会作为属性值
        # return "xxxx"
        raise AttributeError("这个属性只能设置，不能读取")

    # 使用这个装饰器, 对应设置属性操作
    @password.setter
    def password(self, value):
        """
        设置属性  user.passord = "xxxxx"
        :param value: 设置属性时的数据 value就是"xxxxx", 原始的明文密码
        :return:
        """
        self.password_hash = generate_password_hash(value)

    # def generate_password_hash(self, origin_password):
    #     """对密码进行加密"""
    #     self.password_hash = generate_password_hash(origin_password)

    def check_password(self, password):
        # 验证ok,返回Ture, 否则返回False
        return check_password_hash(self.password_hash, password)


class Area(BaseModel, db.Model):
    """城区"""

    __tablename__ = "cab_area_info"

    id = db.Column(db.Integer, primary_key=True)  # 区域编号
    name = db.Column(db.String(32), nullable=False)  # 区域名字
    cars = db.relationship("Car", backref="area")  # 区域的车辆

    # 返回地区字典{id:id,name:name}
    def area_to_dict(self):
        areas_dict = {
            "area_id": self.id,
            "area_name": self.name
        }
        return areas_dict


# 车辆配置表，建立车辆与配置的多对多关系
car_facility = db.Table(
    "cab_car_facility",
    db.Column("car_id", db.Integer, db.ForeignKey("cab_car_info.id"), primary_key=True),  # 车辆编号
    db.Column("facility_id", db.Integer, db.ForeignKey("cab_facility_info.id"), primary_key=True)  # 配置编号
)


class Car(BaseModel, db.Model):
    """车辆信息"""

    __tablename__ = "cab_car_info"

    id = db.Column(db.Integer, primary_key=True)  # 车辆编号
    user_id = db.Column(db.Integer, db.ForeignKey("cab_user_profile.id"), nullable=False)  # 车主编号
    area_id = db.Column(db.Integer, db.ForeignKey("cab_area_info.id"), nullable=False)  # 归属地的区域编号
    title = db.Column(db.String(64), nullable=False)  # 标题
    price = db.Column(db.Integer, default=0)  # 单价，单位：分
    no = db.Column(db.String(32), default="")  # 车牌号
    load = db.Column(db.String(32), default="")  # 车辆载重，重量（货车），人数（小车）
    size = db.Column(db.String(32), default="")  # 车辆尺寸,长宽高
    mold = db.Column(db.String(32), default="")  # 车型，轿车、面包车、suv等
    space = db.Column(db.Integer, default=1)  # 车辆空间，体积（立方）
    disc = db.Column(db.String(512), default='')  # 车辆描述
    order_count = db.Column(db.Integer, default=0)  # 预订完成的该车辆的订单数
    index_image_url = db.Column(db.String(256), nullable=True)  # 车辆主图片的路径
    facilities = db.relationship("Facility", secondary=car_facility)  # 车辆的配置
    images = db.relationship("CarImage")  # 车辆的图片
    orders = db.relationship("Order", backref="car")  # 车辆的订单

    # 车辆基本信息转换成字典
    def to_base_dict(self):
        car_dict = {
            'car_id': self.id,
            'title': self.title,
            'price': self.price,
            'area_name': self.area.name,
            'index_image_url': QINIU_IMAGE_STORE_DOMAIN + self.index_image_url if self.index_image_url else '',
            'load': self.load,
            'order_count': self.order_count,
            'user_head': QINIU_IMAGE_STORE_DOMAIN + self.user.avatar_url if self.user.avatar_url else '',
            'ctime': self.update_time.strftime('%Y-%m-%d %H:%M:%S')
        }

        return car_dict

    # 车辆详细信息转换成字典
    def to_full_dict(self):
        car_dict = {
            'car_id': self.id,
            'user_id': self.user_id,
            'user_name': self.user.name,
            'user_head': QINIU_IMAGE_STORE_DOMAIN + self.user.avatar_url if self.user.avatar_url else '',
            'area_id': self.area_id,
            'title': self.title,
            'price': self.price,
            'load': self.load,
            'space': self.space,
            'size': self.size,
            'mold': self.mold,
            'disc': self.disc,
            'no': self.no
        }

        # 图片
        image_urls = []
        for image in self.images:
            image_urls.append(QINIU_IMAGE_STORE_DOMAIN + image.url)
        car_dict['image_urls'] = image_urls

        # 设施
        car_facilities = []
        for facility in self.facilities:
            car_facilities.append(facility.id)
        car_dict['facilities'] = car_facilities

        # 评论
        comments = []
        orders = Order.query.filter(Order.car_id == self.id, Order.status == 'COMPLETE', Order.comment.isnot(None)).\
            order_by(Order.update_time.desc()).limit(CAR_COMMENT_MAX_COUNT).all()
        for order in orders:
            comment = {
                'content': order.comment,
                'custom_name': order.user.name if order.user.name else '匿名用户',
                'ctime': order.update_time.strftime('%Y-%m-%d %H:%M:%S')
            }
            comments.append(comment)

        return car_dict


class Facility(BaseModel, db.Model):
    """配置信息"""

    __tablename__ = "cab_facility_info"

    id = db.Column(db.Integer, primary_key=True)  # 配置编号
    name = db.Column(db.String(32), nullable=False)  # 配置名字

    # 返回配置字典{id:id,name:name}
    def to_dict(self):
        facility_dict = {
            "facility_id": self.id,
            "facility_name": self.name
        }
        return facility_dict


class CarImage(BaseModel, db.Model):
    """车辆图片"""

    __tablename__ = "cab_car_image"

    id = db.Column(db.Integer, primary_key=True)
    car_id = db.Column(db.Integer, db.ForeignKey("cab_car_info.id"), nullable=False)  # 车辆编号
    url = db.Column(db.String(256), nullable=False)  # 图片的路径


class Order(BaseModel, db.Model):
    """订单"""

    __tablename__ = "cab_order_info"

    id = db.Column(db.Integer, primary_key=True)  # 订单编号
    user_id = db.Column(db.Integer, db.ForeignKey("cab_user_profile.id"), nullable=False)  # 下订单的用户编号
    car_id = db.Column(db.Integer, db.ForeignKey("cab_car_info.id"), nullable=False)  # 预订的车辆编号
    begin_date = db.Column(db.DateTime, nullable=False)  # 预订的出发时间
    end_date = db.Column(db.DateTime, nullable=False)  # 预计的到达时间  根据报读地图计算
    start_point = db.Column(db.String(256), default='')  # 出发地
    end_point = db.Column(db.String(256), default='')    # 目的地
    duration = db.Column(db.String(32), default='')
    mileage = db.Column(db.Integer, nullable=False)  # 到达时的里程数  *1000 ,单位米 根据百度地图计算
    price = db.Column(db.Integer, nullable=False)  # 每公里的单价
    amount = db.Column(db.Integer, nullable=False)  # 订单的总金额
    status = db.Column(  # 订单的状态
        db.Enum(
            "WAIT_ACCEPT",  # 待接单,
            "WAIT_PAYMENT",  # 待支付
            "PAID",  # 已支付
            "WAIT_COMMENT",  # 待评价
            "COMPLETE",  # 已完成
            "CANCELED",  # 已取消
            "REJECTED"  # 已拒单
        ),
        default="WAIT_ACCEPT", index=True)
    comment = db.Column(db.Text)  # 订单的评论信息或者拒单原因
    trade_no = db.Column(db.String(100))  # alipay交易码

    def to_dict(self):
        order_dict = {

            'order_id': self.id,
            'car_title': self.car.title,
            'price': self.car.price,
            'car_no': self.car.no,
            'car_user_phone': self.car.user.mobile,
            'user_phone': self.user.mobile,
            'ctime': datetime.strftime(self.create_time, '%Y-%m-%d %H:%M'),
            'begin_date': datetime.strftime(self.begin_date, '%Y-%m-%d %H:%M'),
            'end_date': datetime.strftime(self.end_date, '%Y-%m-%d %H:%M'),
            'start_point': self.start_point,
            'end_point': self.end_point,
            'mileage': self.mileage,
            'amount': self.amount,
            'duration': self.duration,
            'status': self.status,
            'comment': self.comment,
            'image_url': QINIU_IMAGE_STORE_DOMAIN + self.car.index_image_url,
            'trade_no': self.trade_no,

        }

        return order_dict
