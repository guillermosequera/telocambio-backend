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
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'db.sqlite')
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/telocambio'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# inicio base de datos
db = SQLAlchemy(app)
migrate = Migrate(app, db)

#incio marshmallow
ma = Marshmallow(app)

#user Class/Model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(100))
    lastname = db.Column(db.String(200))
    email = db.Column(db.String(200))
    password = db.Column(db.String(200))
    role = db.Column(db.String(100))

    def __init__(self, firstname, lastname, email, password, role):
        self.firstname = firstname
        self.lastname = lastname
        self.email = email
        self.password = password
        self.role = role

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

# Esquema de usuario
class UserSchema(ma.Schema):
    class Meta:
        fields = ('id', 'firstname', 'lastname', 'email', 'password' , 'role')

# inicio Schema PRODUCTO
product_schema = ProductSchema()
products_schemas = ProductSchema(many=True)

# inicio Schema USUARIO
user_schema = UserSchema()
users_schemas = UserSchema(many=True)


# Crea un USUARIO
@app.route('/user', methods=['POST'])
def add_user():
    firstname = request.json['firstname']
    lastname = request.json['lastname']
    email = request.json['email']
    password = request.json['password']
    role = request.json['role']

    new_user = User(firstname, lastname, email, password, role)

    db.session.add(new_user)
    db.session.commit()
    dump_data = user_schema.dump(new_user)
    return dump_data

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
@app.route('/products', methods=['GET'])
def get_products():
    all_products = Product.query.all()
    result = products_schemas.dump(all_products)
    return jsonify(result)

# Obteniendo todos los usuarios
@app.route('/users', methods=['GET'])
def get_users():
    all_users = User.query.all()
    result = users_schemas.dump(all_users)
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