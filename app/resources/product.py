import json
from flask_restful import Resource, reqparse
from flask import render_template, make_response
import werkzeug
from models import ProductModel


class Product(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('file', type=werkzeug.datastructures.FileStorage, location='files')

    def __init__(self, **kwargs):
        self.logger = kwargs.get('logger')

    def get(self):
        headers = {'Content-Type': 'text/html'}
        return make_response(render_template('index.html'), 200, headers)

    def post(self):
        self.logger.info('Received an image, starting processing..')
        args = Product.parser.parse_args()
        image_file = args['file']

        self.logger.info('Running OCR..')
        items = []  # TODO: Run OCR
        self.logger.info(f'Found items: {items}')
        products = []  # TODO: Run DB Query

        return json.dumps([product.__dict__ for product in products]), 204
