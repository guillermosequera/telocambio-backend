import os
import json

from dotenv import load_dotenv
from flask import Flask, request, jsonify, render_template
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
@app.route('/test', methods=['GET'])
def test():
    return render_template("contactform.html", content='coso del coso')


# Envia un EMAIL
@app.route('/sendemail', methods=['POST'])
def send_email():
    emailreq = request.json.get('email', None)
    subject = request.json.get('subject', None) 
    body = request.json.get('body', None) 
    template = request.json.get('template', None) 
    data = request.json.get('data', None)
    if(template == 'contactform'):
        htmlbody = render_template('contactform.html',name=data['nombre'], lastname=data['apellido'], email=data['email'], message=data['mensaje'])
    if(template == 'swapdone'):
        htmlbody = render_template('swapdone.html',oferta_name=data['oferta_name'], oferta_img=data['oferta_img'], oferta_link=data['oferta_link'], muestra_name=data['muestra_name'], muestra_img=data['muestra_img'], muestra_link=data['muestra_link'], name=data['name'], email=data['email'])
    if(template == 'swapreceive'):
        htmlbody = render_template('swapreceive.html',oferta_name=data['oferta_name'], oferta_img=data['oferta_img'], oferta_link=data['oferta_link'], muestra_name=data['muestra_name'], muestra_img=data['muestra_img'], muestra_link=data['muestra_link'], login=data['login'])
    if(template == 'swapsend'):
        htmlbody = render_template('swapsend.html',oferta_name=data['oferta_name'], oferta_img=data['oferta_img'], oferta_link=data['oferta_link'], muestra_name=data['muestra_name'], muestra_img=data['muestra_img'], muestra_link=data['muestra_link'])
    msg = email.message.Message()
    # setup the parameters of the message
    password = os.environ.get('EMAIL_PASS')
    msg['From'] = os.environ.get('EMAIL_FROM')
    msg['To'] = emailreq
    msg['Subject'] = subject
    msg.add_header('Content-Type', 'text/html')
    # htmlbody = render_template('contactform.html')
    msg.set_payload(htmlbody)
    #create server
    server = smtplib.SMTP(host=os.environ.get('EMAIL_HOST'), port=os.environ.get('EMAIL_PORT'))
    server.starttls()
    # Login Credentials for sending the mail
    server.login(msg['From'], password)
    # send the message via the server.
    server.sendmail(msg['From'], msg['To'], msg.as_string().encode("ascii", errors="ignore"))
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
    
    gallery1 = request.json.get('gallery1', '') 
    gallery2 = request.json.get('gallery2', '') 
    gallery3 = request.json.get('gallery3', '') 
    gallery4 = request.json.get('gallery4', '') 
    gallery5 = request.json.get('gallery5', '') 
    gallery6 = request.json.get('gallery6', '') 
    gallery7 = request.json.get('gallery7', '') 

    gallery = list(filter(lambda x: (x != ''), [gallery1, gallery2,gallery3,gallery4,gallery5,gallery6]))  

    galleryfinal = ','.join(map(str, gallery)) 
    
    tradeBy = request.json['tradeBy']
    username = request.json['username']
    user_id = int(request.json['user_id'])
    done = 0
    offers = 0
    user_email = request.json['user_email']
    new_product = models.Product(name, tags, shortDesc, longDesc , cover_img, galleryfinal, tradeBy, username, user_id, done, offers, user_email )
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
    product.name = request.json.get('name', product.name)
    product.tags = request.json.get('tags', product.tags)
    product.shortDesc = request.json.get('shortDesc', product.shortDesc)
    product.longDesc = request.json.get('longDesc', product.longDesc)
    product.tradeBy = request.json.get('tradeBy', product.tradeBy)
    product.cover_img = request.json.get('cover_img', product.cover_img) 
    gallery1 = request.json.get('gallery1', '') 
    gallery2 = request.json.get('gallery2', '') 
    gallery3 = request.json.get('gallery3', '') 
    gallery4 = request.json.get('gallery4', '') 
    gallery5 = request.json.get('gallery5', '') 
    gallery6 = request.json.get('gallery6', '') 
    gallery_old = product.gallery
    gallery_new = list(map( lambda x: (x != ''), [gallery1, gallery2,gallery3,gallery4,gallery5,gallery6]))
    gallery_add = gallery_old.split(',') + gallery_new
    gallery_add = list(dict.fromkeys(gallery_add))
    gallery_add = list(filter(None, gallery_add))
    galleryfinal = ','.join(list(dict.fromkeys(gallery_add)))
    product.gallery = galleryfinal
    
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
def test_home():
    return 'API ONLINE'

@app.route('/upload', methods=['POST'])
def upload():
    cover_img = request.files.get('cover_img', None)
    gallery1 = request.files.get('gallery1', None)
    gallery2 = request.files.get('gallery2', None)
    gallery3 = request.files.get('gallery3', None)
    gallery4 = request.files.get('gallery4', None)
    gallery5 = request.files.get('gallery5', None)
    gallery6 = request.files.get('gallery6', None)
    line_items=[]
    if cover_img:
        f_cover_img = s3handler.s3upload(cover_img)
        line_items.append({"cover_img": f_cover_img })
    if gallery1:
        f_gallery1 = s3handler.s3upload(gallery1)
        line_items.append({"gallery1": f_gallery1 })
    if gallery2:
        f_gallery2 = s3handler.s3upload(gallery2)
        line_items.append({"gallery2": f_gallery2 })
    if gallery3:
        f_gallery3 = s3handler.s3upload(gallery3)
        line_items.append({"gallery3": f_gallery3 })
    if gallery4:
        f_gallery4 = s3handler.s3upload(gallery4)
        line_items.append({"gallery4": f_gallery4 })
    if gallery5:
        f_gallery5 = s3handler.s3upload(gallery5)
        line_items.append({"gallery5": f_gallery5 })
    if gallery6:
        f_gallery6 = s3handler.s3upload(gallery6)
        line_items.append({"gallery6": f_gallery6 })
    return jsonify(line_items)
    # jsonify(filename1, filename2)

#servidor
if __name__ == '_main_':
    app.run(host='http://localhost',port=3000,debug=True)