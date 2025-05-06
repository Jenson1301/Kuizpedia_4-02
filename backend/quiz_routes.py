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
        correct_answer = question.answer

        print(f"[DEBUG] Q{question.id}: '{question.question_text}'")
        print(f"[DEBUG] - Correct: '{correct_answer}' | User: '{user_answer}'")

        if user_answer and user_answer.strip() == correct_answer.strip():
            score += 1

    return render_template('score_result.html', score=score, total=len(all_questions))


@kuiz_bp.route('/create-question', methods=['GET'])
def create_question_form():
    return render_template('create_question.html')

@kuiz_bp.route('/create-question', methods=['POST'])
def create_question():
    question_text = request.form['question_text']
    options = request.form['options'].split(',')  # Split the comma-separated options into a list
    answer = request.form['answer']
    
    # Create a new question object
    new_question = Question(
        question_text=question_text,
        options=options,
        answer=answer,
        kuiz_id=1  
    )

    # Add the question to the session and commit it to the database
    db.session.add(new_question)
    db.session.commit()

    return redirect(url_for('home'))  # Redirect back to the home page

@kuiz_bp.route('/edit-question/<int:question_id>', methods=['GET', 'POST'])
def edit_question(question_id):
    question = Question.query.get_or_404(question_id)

    if request.method == 'POST':
        new_answer = request.form['answer']
        question.answer = new_answer
        db.session.commit()
        return redirect(url_for('home'))
    
    return render_template('edit_question.html', question=question)


@kuiz_bp.route('/delete-question/<int:question_id>', methods=['GET'])
def delete_question(question_id):
    question = Question.query.get_or_404(question_id)
    db.session.delete(question)
    db.session.commit()     
    return redirect(url_for('home'))