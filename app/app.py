from flask import Flask
from flask_restful import Api
import logging

from resources import Product

app = Flask(__name__)
api = Api(app)
api.add_resource(Product, '/', resource_class_kwargs={
    'logger': logging.getLogger()
})

if __name__ == '__main__':
    app.run()
