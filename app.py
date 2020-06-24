from dotenv import load_dotenv
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    get_jwt_identity
)
from flask_bcrypt import Bcrypt
import os
import json
from flask_cors import CORS
load_dotenv()
#incio de la app

app = Flask(__name__)
CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

basedir = os.path.abspath(os.path.dirname(__file__))



#base de datos
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'db.sqlite')
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/telocambio'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'Gaq5qR6v7BMSojBSQqCs62UBxy9xiUSL15vE9T_KWaTCEziPRfe0WrFBvVZS4RTbqoEP8d0UB0EA'

jwt = JWTManager(app)
bcrypt = Bcrypt(app)

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
    email = db.Column(db.String(200), unique=True)
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
@app.route('/register', methods=['POST'])
def add_user():
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request"}), 400

    firstname = request.json['firstname']
    lastname = request.json['lastname']
    email = request.json.get('email', None)
    password = request.json.get('password', None)
    hashPassword = bcrypt.generate_password_hash(str(password), 10).decode('utf-8')
    role = request.json['role']

    if email is None:
        return 'Missing email', 400
    if password is None:
        return 'Missing password',400

        
    new_user = User(firstname, lastname, email, hashPassword, role)

    db.session.add(new_user)
    db.session.commit()
    dump_data = user_schema.dump(new_user)
    return dump_data

# Login de un USUARIO
@app.route('/login', methods=['GET','POST'])
def login_user():
    email = request.json.get('email', None)
    password = request.json.get('password', None)
    if email is None:
        return 'Missing email', 400
    if password is None:
        return 'Missing password',400
    user = User.query.filter_by(email=email).first()
    if not user:
        return 'User not found', 404

    if bcrypt.check_password_hash(user.password, str(password)):
        access_token = create_access_token(identity=user.id)
        return jsonify(access_token=access_token), 200
    else: 
        
        return 'wrong password!'

@app.route('/token', methods=['GET'])
@jwt_required
def token_user():
    current_user = get_jwt_identity()
    print(current_user)
    user = User.query.get(current_user)
    return user_schema.jsonify(user), 200

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