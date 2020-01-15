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

# Temporarily adding the data.json content for ease of development
DATA = {
  "products": [
    {
      "productId": 1,
      "description": "Small Widget",
      "quantityOnHand": 50,
      "reorderThreshold": 10,
      "reorderAmount": 50,
      "deliveryLeadTime": 5
    },
    {
      "productId": 2,
      "description": "Medium Widget",
      "quantityOnHand": 10,
      "reorderThreshold": 10,
      "reorderAmount": 10,
      "deliveryLeadTime": 5
    },
    {
      "productId": 3,
      "description": "Large Widget",
      "quantityOnHand": 0,
      "reorderThreshold": 10,
      "reorderAmount": 20,
      "deliveryLeadTime": 5
    }
  ],
  "orders": [
    {
      "orderId": 1122,
      "status": "Pending",
      "dateCreated": "2018-05-09 10:59",
      "items": [
        {
          "orderId": 1122,
          "productId": 1,
          "quantity": 4,
          "costPerItem": 10.45
        },
        {
          "orderId": 1122,
          "productId": 2,
          "quantity": 7,
          "costPerItem": 20.95
        }
      ]
    },
    {
      "orderId": 1123,
      "status": "Pending",
      "dateCreated": "2018-05-09 14:21",
      "items": [
        {
          "orderId": 1123,
          "productId": 1,
          "quantity": 4,
          "costPerItem": 10.45
        },
        {
          "orderId": 1123,
          "productId": 2,
          "quantity": 3,
          "costPerItem": 20.95
        },
        {
          "orderId": 1123,
          "productId": 3,
          "quantity": 5,
          "costPerItem": 20.95
        }
      ]
    },
    {
      "orderId": 1124,
      "status": "Pending",
      "dateCreated": "2018-05-09 14:22",
      "items": [
        {
          "orderId": 1124,
          "productId": 1,
          "quantity": 1,
          "costPerItem": 10.45
        },
        {
          "orderId": 1124,
          "productId": 2,
          "quantity": 3,
          "costPerItem": 20.95
        }
      ]
    },
    {
      "orderId": 1125,
      "status": "Pending",
      "dateCreated": "2018-05-09 14:22",
      "items": [
        {
          "orderId": 1125,
          "productId": 1,
          "quantity": 6,
          "costPerItem": 10.45
        },
        {
          "orderId": 1125,
          "productId": 2,
          "quantity": 8,
          "costPerItem": 20.95
        },
        {
          "orderId": 1125,
          "productId": 3,
          "quantity": 3,
          "costPerItem": 20.95
        }
      ]
    }
  ]
}


@warehouse_api.route('/fulfilment')
class Fulfilment(Resource):
    @warehouse_api.expect(_fulfilment, validate=True)
    def post(self):
        # Creating the orders and products per request. Further development would see
        # this become part of a proper database system
        database_orders = [order for order in DATA["orders"]]
        database_products = [product for product in DATA["products"]]

        # Get the order_id's from the request. We know this is a list of integers thanks to the flask_restplus
        # validation of the inputs
        request_data = request.get_json()
        order_ids = request_data["order_ids"] or []

        # A list of unfulfillable orders
        unfulfilled_orders = []

        for order_id in order_ids:
            # Attempt to process this order. If return value is False the order_id could not be fulfilled
            # and it is appended to the unfulfilled orders list
            if not self.process_order_id(order_id, database_orders, database_products):
                unfulfilled_orders.append(order_id)

        return {
            "unfulfillable": unfulfilled_orders
        }

    def process_order_id(self, order_id, orders, products):
        # Check that the order exists
        this_order = next((order for order in orders if order['orderId'] == order_id), None)

        if this_order:
            print("Order found:", this_order)

            if self.all_products_available(this_order, products):
                return True

        return False

    def all_products_available(self, order, products):
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
        return True


@warehouse_api.route('/check_order')
class CheckOrder(Resource):
    @warehouse_api.expect(_check_order)
    def post(self):
        database_orders = [order for order in DATA["orders"]]

        request_data = request.get_json()
        order_id = request_data["order_id"] or []

        this_order = next((order for order in database_orders if order['orderId'] == order_id), None)
        order_status = 'Order does not exist'

        if this_order:
            order_status = this_order['status']

        return {
            'order_status': order_status
        }
