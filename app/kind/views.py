# 主业务逻辑中的视图和路由的定义
from flask import Flask, render_template, request, session, redirect
# 导入蓝图程序，用于构建路由
from . import kind
#导入db，用于操作数据库
from .. import db
#导入实体类，用于操作数据库
from ..models import *
import json

url = 'http://127.0.0.1:5000/static/image/'

@kind.route('/classification')
def get_kind():
	product_types = Type.query.all()
	classify = []
	for i in product_types:
		d = {}
		d['index'] = i.id
		d['text'] = i.type_name
		classify.append(d)
	return json.dumps(classify)


@kind.route('/classify/get_products/<int:id>')
def cget_products(id):
    product_type = Type.query.filter_by(id=id).first()
    products = product_type.products
    product = []
    for i in products:
        d = {}
        p = i.pictures.filter_by(type_id=1).first()
        d['img_url'] = url + p.picture_name
        d['text'] = i.description
        d['price'] = i.price
        d['url'] = '/pages/product_detail/product_detail?id=' + str(i.id)
        product.append(d)
    return json.dumps(product)