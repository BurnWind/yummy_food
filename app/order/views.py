# 主业务逻辑中的视图和路由的定义
from flask import Flask, render_template, request, session, redirect
# 导入蓝图程序，用于构建路由
from . import order
# 导入db，用于操作数据库
from .. import db
# 导入实体类，用于操作数据库
from ..models import *
# 导入异步执行任务
from ..order_celery import task1
import json
from ..seller.redis_store import r
import datetime
import random

# 订单生成获取商品数据

url = 'http://127.0.0.1:5000/static/image/'
@order.route('/order/get_products', methods=['POST'])
def order_get_products():
    token = request.form.get('token')
    if not r.get(token):
        return "登录失效",403
    addresses = Customer.query.filter_by(id=r.get(token)).first().addresses.all()
    receive = {}
    if len(addresses)>0:
        address = addresses[0]
        receive["name"] = address.receiver
        receive["phone"] = address.phone
        receive["address"] = address.detail_address
    products = json.loads(request.form.get('products'))
    data = {}
    order = []
    stop = []
    p = []
    for i in products:
        pd = {}
        product = Product.query.filter_by(id=i['id']).first()
        seller = product.seller
        if seller not in stop:
            stop.append(seller)
        pd['id'] = product.id
        pd['title'] = product.description
        pd['price'] = product.price
        pd['img'] = url + product.pictures.filter_by(type_id=1).first().picture_name
        pd['seller_id'] = product.seller_id
        pd['num'] = i['num']
        p.append(pd)
    for i in stop:
        od = {}
        od['stop'] = i.seller_name
        od['products'] = []
        for j in p:
            if j['seller_id'] == i.id:
                od['products'].append(j)
        order.append(od)
    data["receive"] = receive
    data["order"] = order
    return json.dumps(data)


@order.route('/order/make', methods=['POST'])
def order_make():
    token = request.form.get('token')
    if not r.get(token):
        return '登录过期', 403
    cid = r.get(token)
    receive = json.loads(request.form.get('receive'))
    order = json.loads(request.form.get('order'))
    flag = json.loads(request.form.get('flag'))
    total = request.form.get('total')
    address = Address.query.filter_by(
        receiver=receive['name'], phone=receive['phone'], customer_id=cid, detail_address=receive['address']).first()
    if not address:
        address = Address(receiver=receive['name'], phone=receive['phone'],
                          customer_id=cid, detail_address=receive['address'])
        db.session.add(address)
        db.session.commit()
    food_order = Food_order(time=datetime.datetime.now(
    ), price=total, status='daifukuan', customer_id=cid, address_id=address.id)
    db.session.add(food_order)
    db.session.commit()
    task1. async_order(food_order, eta=datetime.datetime.utcnow()+datetime.timedelta(seconds=60))
    pid = []
    for i in order:
        for j in i["products"]:
            pid.append(j['id'])
            relate = Relate(product_id=j['id'],
                            order_id=food_order.id, num=j['num'])
            db.session.add(relate)
    if flag:
        cart = Cart.query.filter_by(customer_id=cid).first()
        for cprel in cart.cp_products:
            if cprel.product_id in pid:
                db.session.delete(cprel)
    return json.dumps({'order_id':food_order.id})


@order.route('/order/pay', methods=['POST'])
def order_pay():
    order_id = request.form.get('order_id')
    order = Food_order.query.filter_by(id=order_id).first()
    # 找到对应商家通知其发货
    # 修改各商品的销量和库存
    relate = order.relate_products
    for rel in relate:
        product = rel.products
        product.remain -= rel.num
        product.sell_num += rel.num
        db.session.add(product)
    order.status = 'daifahuo'
    db.session.add(order)
    task1. async_order(food_order, eta=datetime.datetime.utcnow()+datetime.timedelta(seconds=60))
    return '支付成功'

@order.route("/order/show", methods=["GET", "POST"])
def order_show():
    if request.method == "POST":
        token = request.form.get("token")
        bookmark = request.form.get("bookmark")
        limit_status = request.form.get("limit_status")
        if not r.get(token):
            return "登录失效",403
        cid = r.get(token)
        customer = Customer.query.filter_by(id=cid).first()
        # 所有订单
        orders = []  
        # co = sorted(customer.orders.all(), key=lambda x:x.time, reverse=True)
        if limit_status == "all":
            co = customer.orders.order_by("time desc").offset(bookmark).limit(5)
        else:
            co = customer.orders.filter_by(status=limit_status).order_by("time desc").offset(bookmark).limit(5)
        for o in co:
            # 一个订单
            food_order = {}
            # 一个订单的收货地址
            receive = {}
            # 一个订单里订单的数据
            order = []
            # 一个订单里订单的数据的一个店的商品
            store_order = {}
            # 一个订单里订单的数据的一个店的所有商品
            products = []
            #存取一个订单内所有店铺id
            store_id = []
            #订单详细信息
            for rp in o.relate_products:
                # 一个订单里订单的数据的一个店的一种商品
                product = {}
                store_id.append(rp.products.seller_id)
                for picture in rp.products.pictures:
                    if picture.type_id == 1:
                        img = url + picture.picture_name
                        break
                relate = Relate.query.filter_by(product_id=rp.products.id,order_id=o.id).first()
                # 一个订单里订单的数据的一个店的一种商品
                product["img"] = img
                product["title"] = rp.products.description
                product["price"] = rp.products.price
                product["num"] = relate.num
                product["url"] = '/pages/product_detail/product_detail?id=%d' %rp.products.id
                # 一个订单里订单的数据的一个店的所有商品
                products.append(product)
            store_id = list(set(store_id)) #去重
            for sid in store_id:
                seller = Seller.query.filter_by(id=sid).first()
                store_order["stop"] = seller.seller_name
                store_order["products"] =  products
                order.append(store_order)
            # 地址信息
            address = Address.query.filter_by(id=o.address_id).first()
            receive["name"] = address.receiver
            receive["phone"] = address.phone
            receive["address"] = address.detail_address    
            #订单号       
            order_id = datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")
            order_id += str(random.randint(10000,100000))
            # 订单状态转中文
            status = o.status
            if status == "daifukuan":
                status = "待付款"
            elif status == "daifahuo":
                status = "待发货"
            elif status == "daishouhuo":
                status = "待收货"
            elif status == "finish":
                status = "已完成"
            # 订单信息
            food_order["receive"] = receive
            food_order["order"] = order
            food_order["total"] = o.price
            food_order["status"] = status
            food_order["order_time"] = o.time.strftime("%Y-%m-%d %H:%M:%S")
            food_order["order_id"] = order_id
            food_order["id"] = o.id
            orders.append(food_order)
        return json.dumps(orders)


# orders: [
# {
#     receive: 
#     {
#         name: '哈哈哈',
#         phone: "13560000000",
#         address: "广东省广州市海珠区 侨光路8号华侨大厦B座7楼"
#     },
#     order: [
#     {
#         stop: '好好吃零食旗舰店',
#         products: [
#             {
#             img: '../../images/TB1qup4aGmWBuNjy1XaXXXCbXXa_!!0-item_pic.jpg',
#             title: '测试商品描述测试商品描述测试商品描述测试商品描述测试商品描述',
#             price: 18.90,
#             num: 2,
#             URL:'/pages/product_detail/product_detail？id='4 
#             },
#         ],
#     },
#     {
#         stop: '好好吃零食旗舰店',
#         products: [
#             {
#                 img: '../../images/TB1qup4aGmWBuNjy1XaXXXCbXXa_!!0-item_pic.jpg',
#                 title: '测试商品描述测试商品描述测试商品描述测试商品描述测试商品描述',
#                 price: 18.90,
#                 num: 2,
#             },
#         ],

#     }
#     ],
#     total: 0,
#     status: 'daifukuan',
#     order_time: '2018-07-09 14:16:24',
#     order_id: 201807,
#     id:1,

# }
# ]