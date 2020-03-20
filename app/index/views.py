# 主业务逻辑中的视图和路由的定义
from flask import Flask, render_template, request, session, redirect
# 导入蓝图程序，用于构建路由
from . import index
#导入db，用于操作数据库
from .. import db
#导入实体类，用于操作数据库
from ..models import *
import json


path = "http://127.0.0.1:5000/static/image/"
@index.route("/homepage", methods=["GET", "POST"])
def homepage():
    banners = Banner.query.all()
    products_obj = Product.query.order_by("price desc").limit(10)
    product_list = []
    imgUrls = []
    data = {}   
    for p in products_obj:
        product = {}
        product["img_url"] = path + p.pictures[0].picture_name
        product["text"] = p.description
        product["price"] = p.price
        product["url"] = '/pages/product_detail/product_detail?id=%s' %p.id
        product_list.append(product)
    for banner in banners:
        b_path = path + banner.image
        imgUrls.append(b_path)
    data["imgUrls"] = imgUrls
    data["product"] = product_list
    return json.dumps(data)

@index.route("/product_detail", methods=["GET", "POST"])
def product_detail():
    if request.method == "GET":
        id = request.args.get("id")
        data = {}
        #商品banner图
        imgUrls = []
        #商品信息
        product = {}
        #商品详情图
        product_detail = []
        # 商家信息
        shop = {}
        #订单信息
        record=[]
        order={}
        product_obj = Product.query.filter_by(id=id).first()
        for pic in product_obj.pictures:
        	if pic.type_id == 1:
        		imgUrls.append(path+pic.picture_name)
        	elif pic.type_id == 2:
        		product_detail.append(path+pic.picture_name)
        product["title"] = product_obj.description
        product["price"] = product_obj.price
        product["sales"] = product_obj.sell_num
        product["remaining"] = product_obj.remain
        product["product_detail"] = product_detail
        seller = Seller.query.filter_by(id=product_obj.seller_id).first()
        s_path = path + seller.simage
        shop["avatar"] = s_path
        shop["shopname"] = seller.seller_name
        re_food_orders = []
        for relate_order in product_obj.relate_orders:
            re_food_orders.append(relate_order.food_orders)
        food_orders = sorted(re_food_orders, key=lambda x: x.time)
        for fo in food_orders:
            if fo.status == "finish":
                customer = Customer.query.filter_by(id=fo.customer_id).first()
                relate = Relate.query.filter_by(order_id=fo.id).first()
                order["buyer"] = customer.cname
                order["time"] = fo.time.strftime("%Y-%m-%d %H:%M:%S")
                order["num"] = relate.num
                record.append(order)
        data["imgUrls"] = imgUrls
        data["shop"] = shop
        data["record"] =record
        data["product"] = product
        return json.dumps(data)
