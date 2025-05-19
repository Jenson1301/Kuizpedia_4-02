from flask import Flask
from models import Kuiz, Question, User
from quiz_routes import kuiz_bp
from auth_routes import auth_bp
from extensions import db, mail

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///kuizpedia.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'satgi buat balik'

# Configure mail
app.config.update(
    MAIL_SERVER='smtp.example.com',
    MAIL_PORT=587,
    MAIL_USE_TLS=True,
    MAIL_USERNAME='your_email@example.com',
    MAIL_PASSWORD='your_password'
)

db.init_app(app)
mail.init_app(app)

app.register_blueprint(auth_bp)
app.register_blueprint(kuiz_bp)

from flask import session

@app.context_processor
def inject_username():
    username = session.get('username')
    return dict(username=username)

@app.route('/add-sample-data', methods=['GET'])
def add_sample_data():
    with app.app_context():
        existing_quiz = Kuiz.query.filter_by(name="Math Quiz").first()
        if not existing_quiz:
            existing_quiz = Kuiz(name="Math Quiz")
            db.session.add(existing_quiz)
            db.session.commit()

        if not Question.query.first():
            q1 = Question(
                question_text="What is 2 + 2?",
                options=["3", "4", "5", "6"],
                answer="4",
                kuiz_id=existing_quiz.id
            )
            q2 = Question(
                question_text="What is 10 - 3?",
                options=["7", "6", "5", "8"],
                answer="7",
                kuiz_id=existing_quiz.id
            )
            db.session.add_all([q1, q2])
            db.session.commit()
            return "Sample data added!"
        else:
            return "Sample data already exists."

def create_tables():
    with app.app_context():
        db.create_all()
        print("Tables created!")

if __name__ == '__main__':
    create_tables()
    app.run(debug=True)