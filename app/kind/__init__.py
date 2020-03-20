from flask import Blueprint
kind = Blueprint("kind", __name__)
from . import views