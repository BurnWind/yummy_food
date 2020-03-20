from flask import Flask, request, render_template, redirect, session, make_response
from . import seller
from .. import db
from ..models import *
from .SendTemplateSMS import sendTemplateSMS
import random
from .redis_store import pipeline,r
import json
import datetime
import os


#上传文件
def upfile(f, p):
    btime = datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")
    ext = f.filename.split(".")[-1]
    filename = btime+"."+ext
    basedir = os.path.dirname(os.path.dirname(__file__))
    upload_path = os.path.join(basedir, p, filename)
    f.save(upload_path)
    return filename 

@seller.route('/', methods=['GET', 'POST'])
@seller.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        if "sid" in session and "sphone" in session:
            print(request.cookies)
            return redirect("/index")
        else:
            if "sid" in request.cookies and "sphone" in request.cookies:
                session["sid"] = request.cookies.get("sid")
                session["sphone"] = request.cookies.get("sphone")
                return redirect("/index")
            else:
                return render_template('login.html')
    elif request.method == 'POST':
        sphone = request.form.get('sphone')
        spwd = request.form.get('spwd')
        print(sphone)
        print(spwd)
        seller = Seller.query.filter_by(sphone=sphone).first()
        if seller:
            if seller.spwd == spwd:
                session['sid'] = seller.id
                session["sphone"] = seller.sphone
                resp = make_response(redirect("/index"))
                if "rem" in request.form:
                    expire = 60*60*24*7
                    resp.set_cookie("sid", str(seller.id), max_age=expire)
                    resp.set_cookie("sphone", seller.sphone, max_age=expire)
                return resp
            else:
                return render_template("login.html", error="密码错误")
        else:
            return render_template("login.html", error1="用户名不存在")


@seller.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    elif request.method == 'POST':
        sphone = request.form.get('sphone')
        sname = request.form.get('sname')
        spwd = request.form.get('spwd')
        icode = request.form.get('icode')
        seller = Seller.query.filter_by(sphone=sphone).first()
        if seller:
            return "手机号已被注册",400
        seller = Seller.query.filter_by(seller_name=sname).first()
        if seller:
            return "该用户名已被使用",400
        if icode == r.get(sphone):
            seller = Seller(sphone=sphone, seller_name=sname, spwd=spwd)
            db.session.add(seller)
            return "注册成功"
        else:
            return "验证码错误",400

@seller.route("/get_icon", methods=["GET", "POST"])
def get_icon():
    if request.method == 'POST':
        sphone = request.form.get('sphone')
        sendcode = str(random.randint(100000, 1000000))
        result = sendTemplateSMS(sphone, [sendcode, "5"], 1)
        if result == "000000":
            with pipeline as p:
                p.set("%s" % sphone, sendcode)
                p.expire("%s" % sphone, 60)
                p.execute()
            return "发送成功"
        else:
            return "发送失败",400


 
@seller.route('/index', methods=['GET', 'POST'])
def index():
    if request.method == "GET":
        if "sid" in session:
            id = session["sid"]
            seller = Seller.query.filter_by(id=id).first()
            type = Type.query.all()
            return render_template("index.html", seller=seller, product_kind=type)
        else:
            return redirect("/login")


@seller.route("/add_product", methods=["GET", "POST"])
def add_product():
    if request.method == "POST":
        if "sid" in session:
            id = session["sid"]
            product_name = request.form.get("product_name")
            product_kind = request.form.get("product_kind")
            product_total = request.form.get("product_total")
            product_price = request.form.get("product_price")
            banner = request.files.getlist("banner")
            detail = request.files.getlist("detail")
            try:
                product = Product(price=product_price, description=product_name, 
                    seller_id=id, total=product_total, remain=product_total,
                    type_id=product_kind)
                db.session.add(product)
                db.session.commit()
                # 上传图片
                for b in banner:
                    filename = upfile(b, "static/image/product_banner/")
                    filename1 = "product_banner/" + filename  
                    picture = Picture(picture_name=filename1, product_id=product.id, type_id=1)
                    db.session.add(picture)
                for d in detail:
                    filename = upfile(d, "static/image/productimg/")
                    filename1 = "productimg/" + filename  
                    picture = Picture(picture_name=filename1, product_id=product.id, type_id=2)
                    db.session.add(picture)
                return "添加成功"
            except Exception as e:
                print(e)
                return "添加失败",500
        else:
            return redirect("/login")

@seller.route("/get_products", methods=["GET", "POST"])
def get_product():
    if request.method == "GET":
        if "sid" in session:
            id = session["sid"]
            seller = Seller.query.filter_by(id=id).first()
            dic = {}
            l = []
            try:
                for product in seller.products:
                    d = {}
                    type1 = Type.query.filter_by(id=product.type_id).first()
                    d["product_name"] = product.description
                    d["product_kind"] = type1.type_name
                    d["product_kind_id"] = type1.id
                    d["product_price"] = product.price
                    d["product_total"] = product.total
                    d["product_sellnum"] = product.sell_num
                    l.append(d)
                dic['data'] = l
                print(l)
                return json.dumps(dic)
            except Exception as e:
                print(e)
                return "error",500
        else:
            return redirect("/login")