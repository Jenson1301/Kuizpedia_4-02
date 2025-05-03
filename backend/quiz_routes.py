from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from format import db, Question

# Create a Blueprint for the quiz-related routes
kuiz_bp = Blueprint('kuiz', __name__)  # This is where 'kuiz_bp' is defined.

# Route to fetch all quiz questions from the database
@kuiz_bp.route('/quizzes', methods=['GET'])
def get_quizzes():
    all_questions = Question.query.all()  # This fetches all questions from the database
    
    quizzes = [
        {"id": q.id, 
         "question": q.question_text, 
         "options": q.options, 
         "answer": q.answer}
         for q in all_questions
        ]
    
    return render_template('index.html', quizzes=quizzes)

# Route to submit the quiz answers
@kuiz_bp.route('/submit-quiz', methods=['POST'])
def submit_quiz():
    score = 0
    # Loop through each question and check if the answer is correct
    all_questions = Question.query.all()
    
    for question in all_questions:
        user_answer = request.form.get(f"question_{question.id}")
        if user_answer == question.answer:
            score += 1

    return f'Your score is: {score} out of {len(all_questions)}'