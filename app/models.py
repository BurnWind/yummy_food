# 与当前项目相关的模型文件，即所有的实体类在此编写
from . import db


class Customer(db.Model):
    '''顾客表'''
    __tablename__ = "customer"
    id = db.Column(db.Integer, primary_key=True)
    openid = db.Column(db.String(128), nullable=False)  # 顾客微信唯一标识
    cname = db.Column(db.String(20))  # 顾客名
    image = db.Column(db.String(100), server_default="default.png")  # 头像
    phone = db.Column(db.String(15))  # 手机号
    # 增加与address的关联关系以及反向引用
    addresses = db.relationship("Address", backref="customer",
                                lazy="dynamic", cascade='all, delete', passive_deletes=True)
    # 增加与order的关联关系以及反向引用
    orders = db.relationship("Food_order", backref="customer",
                             lazy="dynamic", cascade='all, delete', passive_deletes=True)
    # 增加与cart的关联关系以及反向引用
    cart = db.relationship("Cart", backref="customer", uselist=False,
                           cascade='all, delete', passive_deletes=True)


class Address(db.Model):
    '''地址表'''
    __tablename__ = "address"
    id = db.Column(db.Integer, primary_key=True)
    receiver = db.Column(db.String(12), nullable=False)  # 收货人
    phone = db.Column(db.String(15))  # 收货人手机号
    detail_address = db.Column(db.String(128), nullable=False)  # 详细地址
    # 一(customer)对多(address)的关系
    customer_id = db.Column(db.Integer, db.ForeignKey(
        "customer.id", ondelete='CASCADE'), nullable=False)
    # 增加与order之间的关联关系以及反向引用
    orders = db.relationship("Food_order", backref="address",
                             lazy="dynamic", cascade='all, delete', passive_deletes=True)


class Seller(db.Model):
    '''店家表'''
    __tablename__ = "seller"
    id = db.Column(db.Integer, primary_key=True)
    seller_name = db.Column(db.String(40), unique=True)  # 店名
    sphone = db.Column(db.String(13), nullable=False)  # 手机号
    spwd = db.Column(db.String(128))  # 密码
    simage = db.Column(
        db.String(100), server_default="sellerimg/default.png")  # 商标
    # 增加与product之间的关联关系以及反向引用
    products = db.relationship("Product", backref="seller",
                               lazy="dynamic", cascade='all, delete', passive_deletes=True)

 # 购物车与商品关联的中间表


class Cprelate(db.Model):
    __tablename__ = "cprelate"
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey(
        "product.id", ondelete='CASCADE'))
    cart_id = db.Column(db.Integer, db.ForeignKey(
        "cart.id", ondelete='CASCADE'))
    num = db.Column(db.Integer, nullable=False)

# 商品与订单关联的中间表


class Relate(db.Model):
    __tablename__ = "relate"
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey(
        "product.id", ondelete='CASCADE'))
    order_id = db.Column(db.Integer, db.ForeignKey(
        "food_order.id", ondelete='CASCADE'))
    num = db.Column(db.Integer, nullable=False)


class Product(db.Model):
    '''商品表'''
    __tablename__ = "product"
    id = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.Float, nullable=False)  # 商品价格
    description = db.Column(db.Text, nullable=False)  # 商品描述
    total = db.Column(db.Integer, server_default="0")  # 商品数量
    remain = db.Column(db.Integer, server_default="0")  # 剩余数量
    sell_num = db.Column(db.Integer, server_default="0")  # 销售数量
    # 一(type)对多(product)的关系
    type_id = db.Column(db.Integer, db.ForeignKey(
        "type.id", ondelete='CASCADE'), nullable=False)
    # 一(seller)对多(product)的关系
    seller_id = db.Column(db.Integer, db.ForeignKey(
        "seller.id", ondelete='CASCADE'), nullable=False)
    # 增加与picture的关联关系与反向引用
    pictures = db.relationship("Picture", backref="product",
                               lazy="dynamic", cascade='all, delete', passive_deletes=True)
    # 多(cart)对多(product)的关系
    cp_carts = db.relationship("Cprelate", foreign_keys=[Cprelate.product_id],
                               backref=db.backref("products", lazy="joined"), lazy="dynamic",
                               cascade='all, delete', passive_deletes=True)
    # 多(product)对多(order)的关系
    relate_orders = db.relationship("Relate", foreign_keys=[Relate.product_id],
                                    backref=db.backref("products", lazy="joined"), lazy="dynamic",
                                    cascade='all, delete', passive_deletes=True)


class Cart(db.Model):
    """购物车表"""
    __tablename__ = "cart"
    id = db.Column(db.Integer, primary_key=True)
    # 一(cart)对一(customer)的关系
    customer_id = db.Column(db.Integer, db.ForeignKey(
        "customer.id", ondelete='CASCADE'), unique=True)
    # 多(cart)对多(product)的关系
    cp_products = db.relationship("Cprelate", foreign_keys=[Cprelate.cart_id],
                                  backref=db.backref("carts", lazy="joined"), lazy="dynamic",
                                  cascade='all, delete', passive_deletes=True)


class Food_order(db.Model):
    '''订单表'''
    __tablename__ = "food_order"
    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.DateTime, nullable=False)  # 订单时间
    price = db.Column(db.Float, nullable=False)  # 订单价格
    status = db.Column(db.Enum("daifukuan", "daifahuo",
                               "daishouhuo", "finish"), nullable=False)  # 订单状态
    # 一(customer)对多(order)的关系
    customer_id = db.Column(db.Integer, db.ForeignKey(
        "customer.id", ondelete='CASCADE'), nullable=False)
    # 一(address)对多(order)的关系
    address_id = db.Column(db.Integer, db.ForeignKey(
        "address.id", ondelete='CASCADE'), nullable=False)
    # 多(product)对多(order)的关系
    relate_products = db.relationship("Relate", foreign_keys=[Relate.order_id],
                                      backref=db.backref("food_orders", lazy="joined"), lazy="dynamic",
                                      cascade='all, delete', passive_deletes=True)


class Type(db.Model):
    '''商品类别表'''
    __tablename__ = "type"
    id = db.Column(db.Integer, primary_key=True)
    type_name = db.Column(db.String(20), nullable=False)  # 类名
    # 增加与product的关联关系与反向引用
    products = db.relationship(
        "Product", backref="type", lazy="dynamic", cascade='all, delete', passive_deletes=True)


class Picture(db.Model):
    '''图片表'''
    __tablename__ = "picture"
    id = db.Column(db.Integer, primary_key=True)
    picture_name = db.Column(db.String(50), nullable=False)  # 图片名
    # 一(product)对多(picture)的关系
    product_id = db.Column(db.Integer, db.ForeignKey(
        "product.id", ondelete='CASCADE'), nullable=False)  # 商品id
    # 一(picture_type)对多(picture)的关系
    type_id = db.Column(db.Integer, db.ForeignKey(
        "picture_type.id", ondelete='CASCADE'), nullable=False)  # 图片类别id


class Banner(db.Model):
    """banner表"""
    __tablename__ = "banner"
    id = db.Column(db.Integer, primary_key=True)
    image = db.Column(db.String(100), nullable=False)


class Picture_type(db.Model):
    """图片类别表"""
    __tablename__ = "picture_type"
    id = db.Column(db.Integer, primary_key=True)
    type_name = db.Column(db.String(20), nullable=False)
    pictures = db.relationship("Picture", backref="picture_type",
                               lazy="dynamic", cascade='all, delete', passive_deletes=True)
