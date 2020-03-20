# 主业务逻辑中的视图和路由的定义
from flask import Flask, render_template, request, session, redirect
# 导入蓝图程序，用于构建路由
from . import user
#导入db，用于操作数据库
from .. import db
#导入实体类，用于操作数据库
from ..models import *
import requests
import json
import hashlib
import random
import datetime
from ..seller.redis_store import r
import time 

@user.route('/customer_login')
def customer_login():
    code = request.args.get('code')
    d = {
        'appid' : 'wxf474bc381e8c4fcd',
        'secret' : '25d693a6b1a51b2131f7879d8cb27e13',
        'js_code' : code,
        'grant_type' : 'authorization_code',
    }
    resp = requests.get('https://api.weixin.qq.com/sns/jscode2session', params=d)
    openid = resp.json()['openid']
    session_key = resp.json()['session_key']
    customer = Customer.query.filter_by(openid=openid).first()
    if not customer:
        customer = Customer(openid=openid)
        db.session.add(customer)
        db.session.commit()
        cart = Cart(customer_id=customer.id)
        db.session.add(cart)
    token = datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")
    token += str(random.randint(10000,100000))
    t = hashlib.md5(token.encode()).hexdigest()  
    r.set(t,customer.id, ex=60*60*24*7)
    return json.dumps({'token':t})