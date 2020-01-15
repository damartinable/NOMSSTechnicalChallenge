from flask import request
from flask_restplus import Namespace, Resource, fields

restock_api = Namespace('restock', description='Restock order creation endpoints')

_restock = restock_api.model('Restock', {
    'product_id': fields.Integer(
        required=True,
        description="Product ID to restock"
    )
})

# this list is used to imitate a database in a very simple way. Persists until server restarted.
RESTOCK_ORDER_IDS = []

@restock_api.route('/restock')
class Restock(Resource):
    @restock_api.expect(_restock, validate=True)
    def post(self):
        data = request.get_json()
        p_id = data['product_id']

        RESTOCK_ORDER_IDS.append(p_id)

        return {
            "restock_order_created": p_id
        }

    @staticmethod
    def get():
        return {"current_restock_orders": RESTOCK_ORDER_IDS}
