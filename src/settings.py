import os
# SQLALCHEMY_DATABASE_URI= 'mysql+pymysql://root:@localhost/telocambio'
# JWT_SECRET_KEY='Gaq5qR6v7BMSojBSQqCs62UBxy9xiUSL15vE9T_KWaTCEziPRfe0WrFBvVZS4RTbqoEP8d0UB0EA'

# HEROKU
SQLALCHEMY_DATABASE_URI= os.environ.get('DATABASE_URI')
JWT_SECRET_KEY=os.environ.get('JWT_SECRET_KEY')

basedir = os.path.abspath(os.path.dirname(__file__))