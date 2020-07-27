from flask_marshmallow import Marshmallow
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
import datetime

db = SQLAlchemy()
ma = Marshmallow()

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
    done = db.Column(db.Integer, default=0)
    offers = db.Column(db.Integer)
    user_email = db.Column(db.String(600))
    swap_muestra = db.relationship('Productswap', foreign_keys='Productswap.muestra_id')
    swap_oferta = db.relationship('Productswap', foreign_keys='Productswap.oferta_id') 
    def __init__(self, name, tags, shortDesc, longDesc, cover_img, gallery, tradeBy, username, user_id, done, offers, user_email):
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
        self.user_email = user_email
        
# Esquema de producto
class ProductSchema(ma.Schema):
    class Meta:
        fields = ('id', 'name', 'tags', 'shortDesc', 'longDesc', 'cover_img', 'gallery', 'tradeBy','username', 'user_id','done','offers','user_email')

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