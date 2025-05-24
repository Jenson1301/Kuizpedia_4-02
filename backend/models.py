from flask import current_app
from extensions import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import URLSafeTimedSerializer as Serializer
from sqlalchemy.orm import relationship

class Kuiz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    questions = db.relationship('Question', backref='kuiz', lazy=True)

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question_text = db.Column(db.String(200), nullable=False)
    options = db.Column(db.PickleType)
    answer = db.Column(db.String(100), nullable=False)
    kuiz_id = db.Column(db.Integer, db.ForeignKey('kuiz.id'), nullable=False)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String, unique=True, nullable=False)
    username = db.Column(db.String, unique=True, nullable=False)
    password_hash = db.Column(db.String, nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def verify_token(token):
        seq = Serializer(current_app.config['SECRET_KEY'])
        url = seq.loads(token, max_age = 300)
        return url['user_id']

class QuizAttempt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    kuiz_id = db.Column(db.Integer, db.ForeignKey('kuiz.id'))
    score = db.Column(db.Integer)
    total = db.Column(db.Integer)

    kuiz = db.relationship('Kuiz', backref='attempts')

class QuizAttemptDetail(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    attempt_id = db.Column(db.Integer, db.ForeignKey('quiz_attempt.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False)
    user_answer = db.Column(db.String(100))
    correct_answer = db.Column(db.String(100))
    question = db.relationship('Question')
