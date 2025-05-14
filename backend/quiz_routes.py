from flask import Blueprint, render_template, request, redirect, url_for, jsonify, session
from format import db, Question, Kuiz

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
    categories = Kuiz.query.all()
    return render_template('create_question.html', categories=categories)

@kuiz_bp.route('/create-question', methods=['POST'])
def create_question():
    question_text = request.form['question_text']
    options = request.form['options'].split(',')
    answer = request.form['answer']
    category_id = request.form['kuiz_id']  

    new_question = Question(
        question_text=question_text,
        options=options,
        answer=answer,
        kuiz_id=category_id
    )

    db.session.add(new_question)
    db.session.commit()

    return redirect(url_for('home'))

@kuiz_bp.route('/edit-question/<int:question_id>', methods=['GET', 'POST'])
def edit_question(question_id):
    question = Question.query.get_or_404(question_id)

    if request.method == 'POST':
        question.question_text = request.form['question_text']
        question.options = request.form['options'].split(',')
        question.answer = request.form['answer']
        db.session.commit()
        return redirect(url_for('kuiz.edit_category_form', category_id=question.kuiz_id))

    return render_template('edit_question.html', question=question)


@kuiz_bp.route('/delete-question/<int:question_id>', methods=['GET'])
def delete_question(question_id):
    question = Question.query.get_or_404(question_id)
    db.session.delete(question)
    db.session.commit()     
    return redirect(url_for('home'))

@kuiz_bp.route('/quiz/<int:category_id>')
def get_quiz_by_category(category_id):
    category = Kuiz.query.get_or_404(category_id)
    questions = Question.query.filter_by(kuiz_id=category_id).all()
    return render_template('index.html', quizzes=questions)

@kuiz_bp.route('/categories')
def show_categories():
    categories = Kuiz.query.all()
    return render_template('categories.html', categories=categories, username=session['username'])

@kuiz_bp.route('/add-category', methods=['GET'])
def add_category_form():
    return render_template('add_category.html')

@kuiz_bp.route('/add-category', methods=['POST'])
def add_category():
    category_name = request.form['category_name']
    new_category = Kuiz(name=category_name)
    db.session.add(new_category)
    db.session.commit()
    return redirect(url_for('kuiz.show_categories'))

@kuiz_bp.route('/edit-category/<int:category_id>', methods=['GET'])
def edit_category_form(category_id):
    category = Kuiz.query.get_or_404(category_id)
    questions = Question.query.filter_by(kuiz_id=category_id).all()
    return render_template('edit_category.html', category=category, questions=questions)

@kuiz_bp.route('/edit-category/<int:category_id>', methods=['POST'])
def edit_category(category_id):
    category = Kuiz.query.get_or_404(category_id)
    category.name = request.form['category_name']
    db.session.commit()
    return redirect(url_for('kuiz.show_categories'))

@kuiz_bp.route('/delete-category/<int:category_id>', methods=['GET'])
def delete_category(category_id):
    category = Kuiz.query.get_or_404(category_id)
    Question.query.filter_by(kuiz_id=category.id).delete()
    db.session.delete(category)
    db.session.commit()
    return redirect(url_for('kuiz.show_categories'))

@kuiz_bp.route('/start-quiz')
def start_quiz():
    category_id = request.args.get('category_id', type=int)
    timer = request.args.get('timer', type=int)  

    category = Kuiz.query.get_or_404(category_id)
    questions = Question.query.filter_by(kuiz_id=category_id).all()
    
    return render_template('index.html', quizzes=questions, timer=timer)

@kuiz_bp.route('/choose-timer')
def choose_timer():
    category_id = request.args.get('category_id', type=int)
    category = Kuiz.query.get_or_404(category_id)  
    return render_template('choose_timer.html', category=category)