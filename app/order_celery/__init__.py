from celery import Celery
from flask import Blueprint
flask_celery = Blueprint("flask_celery", __name__)
celer = Celery('foodorder')
celer.config_from_object("order_celery.celeryconfig")
