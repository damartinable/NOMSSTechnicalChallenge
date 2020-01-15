import json
import os

from flask import request
from flask_restplus import Namespace, Resource, fields

warehouse_api = Namespace('warehouse', description='Warehouse order fulfilment endpoint(s)')

# This allows us to validate our input for the fulfilment endpoint.
# Data must be a list of integers representing order_ids
_fulfilment = warehouse_api.model('Fulfilment', {
    'order_ids': fields.List(
        fields.Integer,
        required=True,
        description="An array of Order IDs to process orders for fulfilment and shipping."
    )
})

_check_order = warehouse_api.model("Check_Order", {
    'order_id': fields.Integer(
        required=True,
        description="A single order_id to check the status of."
    )
})

DATA = json.load(open(os.path.realpath('NOMSS/data/data.json')))
DATABASE_ORDERS = [order for order in DATA["orders"]]
DATABASE_PRODUCTS = [product for product in DATA["products"]]

@warehouse_api.route('/fulfilment')
class Fulfilment(Resource):
    @warehouse_api.expect(_fulfilment, validate=True)
    def post(self):
        # Get the order_id's from the request. We know this is a list of integers thanks to the flask_restplus
        # validation of the inputs
        request_data = request.get_json()
        order_ids = request_data["order_ids"] or []

        # A list of unfulfillable orders
        unfulfilled_orders = []

        for order_id in order_ids:
            # Attempt to process this order. If the order is fulfillable it is fulfilled, else it is appended to the
            # list of unfulfillable orders.
            if not self.process_order(order_id, DATABASE_ORDERS, DATABASE_PRODUCTS):
                unfulfilled_orders.append(order_id)

        return {
            "unfulfillable": unfulfilled_orders
        }

    def process_order(self, order_id, orders, products):
        # Check that the order exists
        this_order = next((order for order in orders if order['orderId'] == order_id), None)

        if this_order:
            print("Order found:", this_order)

            if self.check_products_and_fulfill(this_order, products):
                return True

        return False

    def check_products_and_fulfill(self, order, products):
        items = order["items"]

        for item in items:
            desired_id = item['productId']
            desired_quantity = item['quantity']

            # Retrieve this particular products details
            this_product = next((product for product in products if product['productId'] == desired_id), None)

            # If there is not enough stock for this order then the whole order is unfulfilled.
            # Return False and the order_id will be added to unfulfilled without the stock being subtracted.
            if this_product and this_product['quantityOnHand'] < desired_quantity:
                # This any products are not sufficient the order is not fulfilled and the error message is set
                order['status'] = "Error: Unfulfillable"

                return False

        # If there was sufficient stock was available for all products the order will be executed.
        # this part of the function is very similar to the above, not very DRY compliant. However it means we do not
        # need to implement any kind of pending stock changes. No decrementing/restocking occurs unless all parts of the
        # order can be fulfilled. This is to keep the design simpler since no partial orders are fulfilled.
        for fulfill_item in items:
            desired_id = fulfill_item['productId']
            desired_quantity = fulfill_item['quantity']

            # Retrieve this particular products details
            this_product = next((product for product in products if product['productId'] == desired_id), None)
            if this_product:
                this_product['quantityOnHand'] -= desired_quantity
                order['status'] = "Fulfilled"

                if this_product['quantityOnHand'] < this_product['reorderThreshold']:
                    self.restock_product(this_product)

        return True

    def restock_product(self, product):
        # Need to finalise this system.
        print("Restock me:", product['productId'])


@warehouse_api.route('/check_order')
class CheckOrder(Resource):
    @warehouse_api.expect(_check_order)
    def post(self):
        request_data = request.get_json()
        order_id = request_data["order_id"] or []

        this_order = next((order for order in DATABASE_ORDERS if order['orderId'] == order_id), None)
        order_status = 'Order does not exist'

        if this_order:
            order_status = this_order['status']

        return {
            'order_status': order_status
        }
