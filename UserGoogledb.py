from flask_login import UserMixin

from db import get_db


class User(UserMixin):
    def __init__(self, id_, name, email, profile_pic):
        self.id = id_
        self.name = name
        self.email = email
        self.profile_pic = profile_pic

    @staticmethod
    def get(user_id):
        db = get_db()
        user = db.execute(
            "googleId", (user_id,)
        ).fetchone()
        if not user:
            return None

        user = User(
            id_=user[0], name=user[1], email=user[2], profile_pic=user[3]
        )
        return user

    @staticmethod
    def create(id_, name, email, tokenId, profile_pic):
        db = get_db()
        db.execute(
            id = db.Column(db.Integer, primary_key=True)
            name = db.Column(db.String(100))
            lastname = db.Column(db.String(200))
            access_token = db.Column(db.String(200))
            email = db.Column(db.String(200), unique=True)
            tokenId = db.Column(db.String(200))
            role = db.Column(db.String(100))
            products = db.relationship('Product', backref='user', lazy=True)
    

    def __init__(self, firstname, lastname, email, password, role):
        self.name = firstname
        self.lastname = lastname
        self.email = email
        self.password = password
        self.role = role
        )
        db.commit()
