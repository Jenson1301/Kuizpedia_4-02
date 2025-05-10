from flask_sqlalchemy import SQLAlchemy

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