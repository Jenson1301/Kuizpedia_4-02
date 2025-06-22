from flask import current_app
from extensions import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import URLSafeTimedSerializer as Serializer

class Kuiz(db.Model):
    __tablename__ = 'kuiz'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    user_id = db.Column(
        db.Integer, 
        db.ForeignKey('user.id', name='fk_kuiz_user_id'), 
        nullable=False
    )

    questions = db.relationship('Question', backref='kuiz', lazy=True)

class Question(db.Model):
    __tablename__ = 'question'

    id = db.Column(db.Integer, primary_key=True)
    question_text = db.Column(db.String(200), nullable=False)
    options = db.Column(db.PickleType)
    answer = db.Column(db.String(100), nullable=False)
    visibility = db.Column(db.String, nullable=False)
    report_count = db.Column(db.Integer, nullable=False)
    
    kuiz_id = db.Column(
        db.Integer,
        db.ForeignKey('kuiz.id', name='fk_question_kuiz_id'),
        nullable=False
    )
    user_id = db.Column(
        db.Integer,
        db.ForeignKey('user.id', name='fk_question_user_id'),
        nullable=False
    )

    user = db.relationship('User', backref='questions')

class User(db.Model, UserMixin):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String, unique=True, nullable=False)
    username = db.Column(db.String, unique=True, nullable=False)
    password_hash = db.Column(db.String, nullable=False)

    kuizzes = db.relationship('Kuiz', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    @staticmethod
    def verify_token(token):
        seq = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = seq.loads(token, max_age = 300)
            return data['user_id']
        except:
            return None


class QuizAttempt(db.Model):
    __tablename__ = 'quiz_attempt'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey('user.id', name='fk_quizattempt_user_id')
    )
    kuiz_id = db.Column(
        db.Integer,
        db.ForeignKey('kuiz.id', name='fk_quizattempt_kuiz_id')
    )
    score = db.Column(db.Integer)
    total = db.Column(db.Integer)

    kuiz = db.relationship('Kuiz', backref='attempts')


class QuizAttemptDetail(db.Model):
    __tablename__ = 'quiz_attempt_detail'

    id = db.Column(db.Integer, primary_key=True)
    attempt_id = db.Column(
        db.Integer,
        db.ForeignKey('quiz_attempt.id', name='fk_attemptdetail_attempt_id'),
        nullable=False
    )
    question_id = db.Column(
        db.Integer,
        db.ForeignKey('question.id', name='fk_attemptdetail_question_id'),
        nullable=False
    )
    user_answer = db.Column(db.String(100))
    correct_answer = db.Column(db.String(100))

    question = db.relationship('Question')
