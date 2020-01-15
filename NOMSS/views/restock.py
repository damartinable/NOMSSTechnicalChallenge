from flask import request
from flask_restplus import Namespace, Resource, fields

restock_api = Namespace('restock', description='Restock order creation endpoints')

_restock = restock_api.model('Restock', {
    'product_id': fields.Integer(
        required=True,
        description="Product ID to restock"
    )
})


@restock_api.route('/restock')
class Restock(Resource):
    @restock_api.expect(_restock, validate=True)
    def post(self):
        data = request.get_json()
        return {
            "restock_order_created": data['product_id']
        }
