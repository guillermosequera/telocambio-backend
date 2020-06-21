from dotenv import load_dotenv
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from sqlalchemy import UniqueConstraint
import os
load_dotenv()
#incio de la app

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))

#base de datos
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'db.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# inicio base de datos
db = SQLAlchemy(app)

#incio marshmallow
ma = Marshmallow(app)

#Producto Class/Model
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)
    description = db.Column(db.String(200))
    price = db.Column(db.Float)
    qty = db.Column(db.Integer)

    UniqueConstraint('name')
    

    def __init__(self, name, description, price, qty):
        self.name = name
        self.description = description
        self.price = price
        self.qty = qty

# Esquema de producto
class ProductSchema(ma.Schema):
    class Meta:
        fields = ('id', 'name', 'description', 'price', 'qty')

# inicio Schema
product_schema = ProductSchema(many=True)

# Crea un Producto

@app.route('/product', methods=['POST'])
def add_product():
    name = request.json['name']
    description = request.json['description']
    price = request.json['price']
    qty = request.json['qty']

    new_product = Product (name, description, price, qty)

    db.session.add(new_product)
    db.session.commit()

    return product_schema.jsonify(new_product)
#servidor

    if __name__ == '_main_':
        app.run(host='http://localhost',port=3000,debug=True)