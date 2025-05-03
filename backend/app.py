from flask import Flask, render_template, request, redirect, url_for
from quiz_routes import kuiz_bp  
from format import db, Question, Kuiz

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.kuizpedia'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Register the blueprint
app.register_blueprint(kuiz_bp)

@app.route('/')
def home():
    quizzes = Question.query.all()  # Fetch question from database
    return render_template('index.html', quizzes=quizzes)

@app.route('/add-sample-data', methods=['GET'])
def add_sample_data():
    with app.app_context():
        # Create a quiz if it doesn't exist
        existing_quiz = Kuiz.query.filter_by(name="Math Quiz").first()
        if not existing_quiz:
            existing_quiz = Kuiz(name="Math Quiz")
            db.session.add(existing_quiz)
            db.session.commit()

        # Only add questions if they don't already exist
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
        db.create_all() #ensure table is created 
        print("Tables created!") #confirms tables is created

@app.route('/submit-quiz', methods=['POST'])
def submit_quiz():
    user_answers = {}
    for quiz in Question.query.all():
        # Get the user's selected answer for each question
        selected_answer = request.form.get(f"question_{quiz.id}")
        user_answers[quiz.id] = selected_answer
        
        # You can now compare the answers and save or process the result
        if selected_answer == quiz.answer:
            print(f"Correct answer for question {quiz.id}")
        else:
            print(f"Wrong answer for question {quiz.id}")
    
    return redirect(url_for('home'))  # Redirect to the homepage 

if __name__ == '__main__':
    create_tables()
    app.run(debug=True)