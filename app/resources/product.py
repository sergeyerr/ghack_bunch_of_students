import json
from flask_restful import Resource, reqparse
from flask import render_template, make_response
import werkzeug
from app.models import line_ocr_result, ocr_result
from app.services import OCRService, StringSearchService
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
        ocr_results = OCRService.get_ocr_results(image_file)
        full = ocr_results[0]
        y = full.bounding_box.boundary.xy[1]
        full_height = max(y) - min(y)
        line_ocrs = line_ocr_result.group_ocr_results(ocr_results[1:], full_height)
        self.logger.info(f'Found items!')
        
        for line in line_ocrs:
            top5_articles = StringSearchService.get_most_likely_articles(line.description)

        products = []  # TODO: Run DB Query

        return json.dumps([product.__dict__ for product in products])
