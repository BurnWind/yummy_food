#对整个应用做初始化操作
# 主要工作：
# 1.构建Flask应用以及各种配置
# 2.构建SQLALchemy的应用

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import pymysql
pymysql.install_as_MySQLdb()

db = SQLAlchemy()
def create_app():
    app = Flask(__name__)
    app.config["DEBUG"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "mysql://root:root@localhost:3306/food"
    # 配置数据库内容在更新时自动提交
    app.config["SQLALCHEMY_COMMIT_ON_TEARDOWN"] = True
    #配置session所需要的秘钥
    app.config["SECRET_KEY"] = "sdahggsjkadhsjkdhsd"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
    #数据库的初始化
    db.init_app(app)
    from .order_celery import flask_celery
    app.register_blueprint(flask_celery)
    #将index蓝图程序与app关联到一起
    from .index import index as index_blueprint
    app.register_blueprint(index_blueprint)
    #将cart蓝图程序与app关联到一起
    from .cart import cart as cart_blueprint
    app.register_blueprint(cart_blueprint)
    #将kind蓝图程序与app关联到一起
    from .kind import kind as kind_blueprint
    app.register_blueprint(kind_blueprint)
    #将user蓝图程序与app关联到一起
    from .user import user as user_blueprint
    app.register_blueprint(user_blueprint) 
    # 将seller蓝图程序与app关联到一起
    from .seller import seller as seller_blueprint
    app.register_blueprint(seller_blueprint)
    # 将order蓝图程序与app关联到一起
    from .order import order as order_blueprint
    app.register_blueprint(order_blueprint)
    return app
