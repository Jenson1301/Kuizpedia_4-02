from flask import Flask, render_template, request, redirect, url_for
from format import db, Question, Kuiz, app

db.init_app(app)

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
                kuiz_id=existing_quiz
            )
            q2 = Question(
                question_text="What is 10 - 3?",
                options=["7", "6", "5", "8"],
                answer="7",
                kuiz_id=existing_quiz
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

if __name__ == '__main__':
    create_tables()
    app.run(debug=True)