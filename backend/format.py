from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import URLSafeTimedSerializer as Serializer

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///kuizpedia.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy()

class Kuiz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    questions = db.relationship('Question', backref='kuiz', lazy=True)

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question_text = db.Column(db.String(200), nullable=False)
    options = db.Column(db.PickleType)  # store as list
    answer = db.Column(db.String(100), nullable=False)
    kuiz_id = db.Column(db.Integer, db.ForeignKey('kuiz.id'), nullable=False)

class User(db.Model):     #####################dk why can submit null form###################
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String, unique=True, nullable=False)
    username = db.Column(db.String, unique=True, nullable=False)
    password_hash = db.Column(db.String, nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def create_token(self):
        seq = Serializer(app.config['SECRET_KEY'])
        return seq.dumps({'user_id': self.id})
    
    @staticmethod
    def verify_token(token):
        seq = Serializer(app.config['SECRET_KEY'])
        try:
            url = seq.loads(token, max_age = 60)
        except:
            return None
        return url['user_id']