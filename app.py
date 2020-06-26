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
import settings
import json
import datetime
from flask_cors import CORS

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import email.message
import smtplib

#email


load_dotenv()
#incio de la app

app = Flask(__name__)
CORS(app)
# app.config['CORS_HEADERS'] = 'Content-Type'

basedir = os.path.abspath(os.path.dirname(__file__))


# SQlite
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'db.sqlite')

# MYSQL LOCAL
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/telocambio'

# HEROKU POSTGRESS
app.config['SQLALCHEMY_DATABASE_URI'] = "postgres://mzjzfmbvieoopk:47d4d3d8426745473cccf8acf4305dbcd2c4b46b157a37954c2a6d82a2480810@ec2-34-233-226-84.compute-1.amazonaws.com:5432/d602ph6akhserd"

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'Gaq5qR6v7BMSojBSQqCs62UBxy9xiUSL15vE9T_KWaTCEziPRfe0WrFBvVZS4RTbqoEP8d0UB0EA'


jwt = JWTManager(app)
bcrypt = Bcrypt(app)

# inicio base de datos
db = SQLAlchemy(app)
migrate = Migrate(app, db)

#incio marshmallow
ma = Marshmallow(app)

class Productswap(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    oferta_id = db.Column(db.Integer, db.ForeignKey('product.id'),nullable=False)
    muestra_id = db.Column(db.Integer, db.ForeignKey('product.id'),nullable=False) 
    done = db.Column(db.Boolean, default=False)
    date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    def __init__(self, muestra_id, oferta_id, done ):
        self.muestra_id = muestra_id
        self.oferta_id = oferta_id
        self.done = done

#user Class/Model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(100))
    lastname = db.Column(db.String(200))
    email = db.Column(db.String(200), unique=True)
    password = db.Column(db.String(200))
    role = db.Column(db.String(100))
    products = db.relationship('Product', backref='user', lazy=True)
    

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
    tags = db.Column(db.String(200))
    shortDesc = db.Column(db.String(600))
    longDesc = db.Column(db.String(1000))
    cover_img = db.Column(db.String(600))
    gallery = db.Column(db.String(600))
    tradeBy = db.Column(db.String(600))
    username = db.Column(db.String(600))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'),nullable=False)
    done = db.Column(db.Boolean, default=False)
    offers = db.Column(db.Integer)
    swap_muestra = db.relationship('Productswap', foreign_keys='Productswap.muestra_id')
    swap_oferta = db.relationship('Productswap', foreign_keys='Productswap.oferta_id') 

    def __init__(self, name, tags, shortDesc, longDesc, cover_img, gallery, tradeBy, username, user_id, done, offers):
        self.name = name
        self.tags = tags
        self.shortDesc = shortDesc
        self.longDesc = longDesc
        self.cover_img = cover_img
        self.gallery = gallery
        self.tradeBy = tradeBy
        self.username = username
        self.user_id = user_id
        self.done = done
        self.offers = offers
        




# Esquema de producto
class ProductSchema(ma.Schema):
    class Meta:
        fields = ('id', 'name', 'tags', 'shortDesc', 'longDesc', 'cover_img', 'gallery', 'tradeBy','username', 'user_id','done','offers')

# Esquema de usuario
class UserSchema(ma.Schema):
    class Meta:
        fields = ('id', 'firstname', 'lastname', 'email', 'password' , 'role')

# Esquema de swap
class SwapSchema(ma.Schema):
    class Meta:
        fields = ('id', 'oferta_id', 'muestra_id', 'done', 'date')


# inicio Schema PRODUCTO
swap_schema = SwapSchema()
swap_schemas = SwapSchema(many=True)

# inicio Schema PRODUCTO
product_schema = ProductSchema()
products_schemas = ProductSchema(many=True)

# inicio Schema USUARIO
user_schema = UserSchema()
users_schemas = UserSchema(many=True)


# Envia un EMAIL
@app.route('/sendemail', methods=['POST'])
def send_email():
    emailreq = request.json.get('email', None)
    subject = request.json.get('subject', None) 
    body = request.json.get('body', None) 

    msg = email.message.Message()
    # msg = MIMEMultipart()
    # message = "Thank you"
    
    # setup the parameters of the message
    password = "15j!y#58zIR["
    msg['From'] = 'base@dekaz.pro'
    msg['To'] = emailreq
    msg['Subject'] = subject
    msg.add_header('Content-Type', 'text/html')
    msg.set_payload(body)
    
    #create server
    server = smtplib.SMTP(host='mail.dekaz.pro', port=2525)
    server.starttls()
    # Login Credentials for sending the mail
    server.login(msg['From'], password)
    # send the message via the server.
    server.sendmail(msg['From'], msg['To'], msg.as_string())
    server.quit()
    print("successfully sent email to %s:" % (msg['To']))

    return "successfully sent email to %s:" % (msg['To'])
    
# Crea un USUARIO
@app.route('/register', methods=['POST'])
def add_user():
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request"}), 400

    firstname = request.json.get('firstname', None)
    lastname = request.json.get('lastname', None) 
    email = request.json.get('email', None)
    password = request.json.get('password', None)
    hashPassword = bcrypt.generate_password_hash(str(password), 10).decode('utf-8')
    # role = request.json['role']
    role = 'user'

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
@app.route('/login', methods=['POST'])
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
    # print(current_user)
    user = User.query.get(get_jwt_identity())
    return user_schema.jsonify(user)

# Crea un Producto
@app.route('/product', methods=['POST'])
def add_product():
    name = request.json['name']
    tags = request.json['tags']
    shortDesc = request.json['shortDesc']
    longDesc = request.json['longDesc']
    cover_img = request.json['cover_img']
    
    gallery1 = request.json['gallery1']
    gallery2 = request.json['gallery2']
    gallery3 = request.json['gallery3']
    gallery4 = request.json['gallery4']
    gallery5 = request.json['gallery5']
    gallery6 = request.json['gallery6']
    gallery7 = request.json.get('gallery7', None) 

    gallery = list(filter(lambda x: (x != ''), [gallery1, gallery2,gallery3,gallery4,gallery5,gallery6]))  

    gallery2 = ','.join(map(str, gallery)) 
    
    tradeBy = request.json['tradeBy']
    username = request.json['username']
    user_id = int(request.json['user_id'])
    done = False
    offers = 0
    # fields = ('id', 'name', 'tags', 'shortDesc', 'longDesc', 'cover_img', 'gallery', 'tradeBy','username', 'user_id','done')
    new_product = Product(name, tags, shortDesc, longDesc , cover_img, gallery2, tradeBy, username, user_id, done, offers )
    print(new_product)
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


@app.route('/swap/create', methods=['POST'])
def create_swap():
    oferta_id = request.json['oferta_id']
    muestra_id = request.json['muestra_id']
    done = request.json['done']
    productswap = Productswap.query.filter_by(muestra_id=muestra_id).filter_by(oferta_id=oferta_id).first()
    if not productswap:
        new_productswap = Productswap(muestra_id, oferta_id, done)
        db.session.add(new_productswap)
        product = Product.query.get(muestra_id)
        product.offers += 1
        db.session.commit()

        result = swap_schema.dump(new_productswap)
        return result
    return 'Producto ya ofertado', 400
    
    
@app.route('/swap/<id>', methods=['GET'])
def get_swap(id):
    products = Productswap.query.filter_by(muestra_id=id).join(Product, Product.id == Productswap.oferta_id).add_columns(Product.id, Product.name, Product.tags, Product.shortDesc, Product.longDesc, Product.cover_img, Product.gallery, Product.tradeBy, Product.username, Product.done).all()
    result = products_schemas.dump(products)
    return jsonify(result)

@app.route('/swap/done', methods=['POST'])
def done_swap():
    ofertaid = request.json['oferta_id']
    muestraid = request.json['muestra_id']
    done = request.json['done']
    productswap = Productswap.query.filter_by(muestra_id=muestraid).filter_by(oferta_id=ofertaid).first()
    productswap.done = done 
    db.session.commit()

    result = swap_schema.dump(productswap)
    return result


# Obteniendo los productos por usuario
@app.route('/products/user/<id>', methods=['GET'])
def get_productsbyuser(id):
    user = User.query.get(id)
    user_products = user.products
    result = products_schemas.dump(user_products)
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
 
@app.route('/', methods=['GET'])
def test():
    return 'API ONLINE'


#servidor

    if __name__ == '_main_':
        app.run(host='http://localhost',port=3000,debug=True)