from flask import request
from flask_restplus import Namespace, Resource, fields

warehouse_api = Namespace('warehouse', description='Warehouse order fulfilment endpoint(s)')

_fulfilment = warehouse_api.model('Fulfilment', {
    'order_ids': fields.List(
        fields.Integer,
        required=True,
        description="An array of Order IDs to process orders for fulfilment and shipping."
    )
})

@warehouse_api.route('/fulfilment')
class Fulfilment(Resource):
    @warehouse_api.expect(_fulfilment, validate=True)
    def post(self):
        pass