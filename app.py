import os
import json

from dotenv import load_dotenv
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    get_jwt_identity
)
from flask_bcrypt import Bcrypt
from flask_cors import CORS

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import email.message
import smtplib

# import boto3
# s3_client = boto3.client(
#     "s3",
#     aws_access_key_id=os.environ.get('S3_ACCESS_KEY_ID'),
#     aws_secret_access_key=os.environ.get('S3_ACCESS_SECRET_KEY')
# )

from src import models, s3handler


load_dotenv()
#incio de la app

app = Flask(__name__)
CORS(app)

# DB
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')


app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY')

jwt = JWTManager(app)
bcrypt = Bcrypt(app)

# inicio base de datos
models.db.init_app(app)
#incio marshmallow
models.ma.init_app(app)

# Envia un EMAIL
@app.route('/sendemail', methods=['POST'])
def send_email():
    emailreq = request.json.get('email', None)
    subject = request.json.get('subject', None) 
    body = request.json.get('body', None) 

    msg = email.message.Message()
    # setup the parameters of the message
    password = os.environ.get('EMAIL_PASS')
    msg['From'] = os.environ.get('EMAIL_FROM')
    msg['To'] = emailreq
    msg['Subject'] = subject
    msg.add_header('Content-Type', 'text/html')
    msg.set_payload(body)
    #create server
    server = smtplib.SMTP(host=os.environ.get('EMAIL_HOST'), port=os.environ.get('EMAIL_PORT'))
    server.starttls()
    # Login Credentials for sending the mail
    server.login(msg['From'], password)
    # send the message via the server.
    server.sendmail(msg['From'], msg['To'], msg.as_string())
    server.quit()
    return {"email": "Email exitoso"}
    
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

        
    new_user = models.User(firstname, lastname, email, hashPassword, role)

    models.db.session.add(new_user)
    models.db.session.commit()
    dump_data = models.user_schema.dump(new_user)
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
    user = models.User.query.filter_by(email=email).first()
    if not user:
        return 'User not found', 404

    if bcrypt.check_password_hash(user.password, str(password)):
        access_token = create_access_token(identity=user.id, expires_delta=False)
        return jsonify(access_token=access_token), 200
    else: 
        
        return 'wrong password!'

@app.route('/token', methods=['GET'])
@jwt_required
def token_user():
    # print(current_user)
    user = models.User.query.get(get_jwt_identity())
    return models.user_schema.jsonify(user)

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
    done = 0
    offers = 0
    user_email = request.json['user_email']
    new_product = models.Product(name, tags, shortDesc, longDesc , cover_img, gallery2, tradeBy, username, user_id, done, offers, user_email )
    # print(new_product)
    models.db.session.add(new_product)
    models.db.session.commit()
    dump_data = models.product_schema.dump(new_product)
    return dump_data

# Obteniendo todos los productos
@app.route('/products', methods=['GET'])
def get_products():
    all_products = models.Product.query.all()
    result = models.products_schemas.dump(all_products)
    return jsonify(result)


@app.route('/swap/create', methods=['POST'])
def create_swap():
    oferta_id = request.json['oferta_id']
    muestra_id = request.json['muestra_id']
    done = request.json['done']
    productswap = models.Productswap.query.filter_by(muestra_id=muestra_id).filter_by(oferta_id=oferta_id).first()
    if not productswap:
        new_productswap = models.Productswap(muestra_id, oferta_id, done)
        models.db.session.add(new_productswap)
        product = models.Product.query.get(muestra_id)
        product.offers += 1
        models.db.session.commit()

        result = models.swap_schema.dump(new_productswap)
        return result
    return 'Producto ya ofertado', 400
    
    
@app.route('/swap/<id>', methods=['GET'])
def get_swap(id):
    products = models.Productswap.query.filter_by(muestra_id=id).join(models.Product, models.Product.id == models.Productswap.oferta_id).add_columns(models.Product.id, models.Product.name, models.Product.tags, models.Product.shortDesc, models.Product.longDesc, models.Product.cover_img, models.Product.gallery, models.Product.tradeBy, models.Product.username, models.Product.done, models.Product.user_email).all()
    result = models.products_schemas.dump(products)
    return jsonify(result)

@app.route('/swap/done', methods=['POST'])
def done_swap():
    ofertaid = request.json['oferta_id']
    muestraid = request.json['muestra_id']
    done = request.json['done']
    productswap = models.Productswap.query.filter_by(muestra_id=muestraid).filter_by(oferta_id=ofertaid).first()
    productswap.done = done 
    productmuestra = models.Product.query.get(muestraid)
    if done != False:
        productmuestra.done = ofertaid  
    else:
        productmuestra.done = 0
    models.db.session.commit()

    result = models.swap_schema.dump(productswap)
    return result


# Obteniendo los productos por usuario
@app.route('/products/user/<id>', methods=['GET'])
def get_productsbyuser(id):
    user = models.User.query.get(id)
    user_products = user.products
    result = models.products_schemas.dump(user_products)
    return jsonify(result)

# Obteniendo todos los usuarios
@app.route('/users', methods=['GET'])
def get_users():
    all_users = models.User.query.all()
    result = models.users_schemas.dump(all_users)
    return jsonify(result)


# Obteniendo un producto
@app.route('/product/<id>', methods=['GET'])
def get_product(id):
    product = models.Product.query.get(id)
    return models.product_schema.jsonify(product)

# Modifica un producto
@app.route('/product/<id>', methods=['PUT'])
def update_product(id):
    product = models.Product.query.get(id)
    name = request.json['name']
    description = request.json['description']
    price = request.json['price']
    qty = request.json['qty']
    product.name = name
    product.description = description
    product.price = price
    product.qty = qty
    models.db.session.commit()
    dump_data = models.product_schema.dump(product)

    return dump_data

# Elimina un producto
@app.route('/product/<id>', methods=['DELETE'])
def delete_product(id):
    product = models.Product.query.get(id)
    models.db.session.delete(product)
    models.db.session.commit()
    return models.product_schema.jsonify(product)
 
@app.route('/', methods=['GET'])
def test():
    return 'API ONLINE'

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['fileinput']
    filename = s3handler.s3upload(file)
    return filename

#servidor
if __name__ == '_main_':
    app.run(host='http://localhost',port=3000,debug=True)