""" Create the flask application and register the routes"""

from flask import Flask
from .views import base_blueprint

app = Flask(__name__)

app.register_blueprint(
    base_blueprint,
    url_prefix='/api/v1'  # This api version should come from the base blueprint itself
)