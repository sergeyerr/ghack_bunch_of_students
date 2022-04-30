from flask import Flask
from flask_restful import Api
import logging

from resources import Product

app = Flask(__name__,
            static_url_path='', 
            static_folder='static',
            template_folder='templates')
api = Api(app)
api.add_resource(Product, '/', resource_class_kwargs={
    'logger': logging.getLogger()
})

if __name__ == '__main__':
    app.run()
