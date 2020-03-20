# 主业务逻辑中的视图和路由的定义
from flask import Flask, render_template, request, session, redirect
# 导入蓝图程序，用于构建路由
from . import cart
# 导入db，用于操作数据库
from .. import db
# 导入实体类，用于操作数据库
from ..models import *
from ..seller.redis_store import r 
import json
# 返回购物车数据

path = "http://176.122.11.85:5000/static/image/"
@cart.route('/get_cart')
def get_cart():
    token = request.args.get("token")
    if not r.get(token):
        return "登录失效",403
    cid = r.get(token)
    cart = Cart.query.filter_by(customer_id=cid).first()
    cp_products = cart.cp_products.all()
    products = []
    for i in cp_products:
        products.append(i.products)
    store = []
    product = []
    for i in products:
        pd = {}
        seller = i.seller
        if seller not in store:
            store.append(seller)
        num = Cprelate.query.filter_by(
            product_id=i.id, cart_id=cart.id).first().num
        pd['id'] = i.id
        pd['store_id'] = seller.id
        pd['url'] = path + i.pictures.filter_by(type_id=1).first().picture_name
        pd['text'] = i.description
        pd['price'] = i.price
        pd['remaining'] = i.remain
        pd['product_checked'] = True
        if num == 1:
            pd['delStatus'] = 'disabled'
            pd['addStatus'] = 'normal'
        elif num == i.remain:
            pd['delStatus'] = 'normal'
            pd['addStatus'] = 'disabled'
        else:
            pd['delStatus'] = 'normal'
            pd['addStatus'] = 'normal'
        pd['quantity'] = num
        product.append(pd)

    def make_store(i):
        s = {}
        s['name'] = i.seller_name
        s['kind_checked'] = False
        s['store_id'] = i.id
        return s
    store = list(map(make_store, store))

    res = {}
    res['store'] = store
    res['product'] = product
    res["cart_id"] = cart.id
    return json.dumps(res)


@cart.route('/delete_cart', methods=['GET','POST'])
def delete_cart():
    if request.method == "POST":
        token = request.form.get("token")
        if not r.get(token):
            return "登录失效",403
        cid = r.get(token)
        pid = json.loads(request.form.get('pid'))
        cart = Cart.query.filter_by(customer_id=cid).first()
        for cprel in cart.cp_products:
            if cprel.product_id in pid:
                db.session.delete(cprel)
        return '成功删除'

@cart.route('/add_cart', methods=["GET", "POST"])
def add_cart():
    if request.method=="GET":
        sell_num = request.args.get("quantity")
        product_id = request.args.get("product_id")
        token = request.args.get("token")
        if not r.get(token):
            return "登录失效",403
        customer_id = r.get(token)
        cart = Cart.query.filter_by(customer_id=customer_id).first()
        cprelate = Cprelate.query.filter_by(cart_id=cart.id,product_id=product_id).first()
        if not cprelate:
            cprelate = Cprelate(product_id=product_id, cart_id=cart.id, num=sell_num)
        else:
            cprelate.num = sell_num
        db.session.add(cprelate)
        return "购物车加入成功"

@cart.route("/update_cart", methods=["GET", "POST"])
def update_cart():
    if request.method=="POST":
        cart_id = request.form.get("cart_id")
        products = json.loads(request.form.get("product"))
        for product in products:
            cprelate = Cprelate.query.filter_by(product_id=product['id'],cart_id=cart_id).first()
            if product["quantity"] == cprelate.num:
                return "不用更新"
            else:
                cprelate.num = product["quantity"]
                db.session.add(cprelate)
                return "更新成功"
        return "购物车为空了"