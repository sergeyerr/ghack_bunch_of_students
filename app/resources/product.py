import json
from flask_restful import Resource, reqparse
from flask import render_template, make_response
import werkzeug
from models import LineOCRResult
from services import OCRService, StringSearchService

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
        image_file = args['file'].read()

        self.logger.info('Running OCR..')
        ocr_results = OCRService.get_ocr_results(image_file)
        full = ocr_results[0]
        y = full.bounding_box.boundary.xy[1]
        full_height = max(y) - min(y)
        line_ocrs = LineOCRResult.group_ocr_results(ocr_results[1:], full_height)
        self.logger.info(f'Found items!')
        return StringSearchService.get_most_likely_articles(list(map(lambda l: l.expected_article_description, line_ocrs)))
        top5_articles = StringSearchService.get_most_likely_articles(list(map(lambda l: l.expected_article_description, line_ocrs)))
        results = []

        for line, top5 in zip(line_ocrs, top5_articles):
            results.append((line.full_description, top5))

        return json.dumps([{"line": r[0], "top_product_name": r[1][0].name, "top_product_total": r[1][0].total} for r in results])
