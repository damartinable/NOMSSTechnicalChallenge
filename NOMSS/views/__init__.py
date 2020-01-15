""" Base API Blueprint to which our warehouse routes are added"""
from flask_restplus import Api
from flask import Blueprint

from .warehouse import warehouse_api

base_blueprint = Blueprint('api', __name__)

base_api = Api(
    base_blueprint,
    title='NOMSS',
    version="1",
    description="New Order Management System Services"
)

base_api.add_namespace(warehouse_api)