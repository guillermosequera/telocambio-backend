from dotenv import load_dotenv
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
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
migrate = Migrate(app, db)

#incio marshmallow
ma = Marshmallow(app)

#Producto Class/Model
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=False)
    description = db.Column(db.String(200))
    price = db.Column(db.Float)
    qty = db.Column(db.Integer)
    

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
product_schema = ProductSchema()
products_schemas = ProductSchema(many=True)

# Crea un Producto

@app.route('/product', methods=['POST'])
def add_product():
    name = request.json['name']
    description = request.json['description']
    price = request.json['price']
    qty = request.json['qty']

    new_product = Product(name, description, price, qty)

    db.session.add(new_product)
    db.session.commit()
    dump_data = product_schema.dump(new_product)

    return dump_data

# Obteniendo todos los productos
@app.route('/product', methods=['GET'])
def get_products():
    all_products = Product.query.all()
    result = products_schemas.dump(all_products)
    return jsonify(result)

# Obteniendo un producto
@app.route('/product/<id>', methods=['GET'])
def get_product(id):
    product = Product.query.get(id)
    return product_schema.jsonify(product)

# Modifica un producto
@app.route('/product/<id>', methods=['PUT'])
def update_product(id):
    product = Product.query.get(id)

    name = request.json['name']
    description = request.json['description']
    price = request.json['price']
    qty = request.json['qty']

    product.name = name
    product.description = description
    product.price = price
    product.qty = qty

    
    db.session.commit()
    dump_data = product_schema.dump(product)

    return dump_data

# Elimina un producto
@app.route('/product/<id>', methods=['DELETE'])
def delete_product(id):
    product = Product.query.get(id)
    db.session.delete(product)
    db.session.commit()

    return product_schema.jsonify(product)
 



#servidor

    if __name__ == '_main_':
        app.run(host='http://localhost',port=3000,debug=True)