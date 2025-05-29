from flask import Blueprint, render_template, request, redirect, url_for, jsonify, session
from extensions import db
from models import Question, Kuiz, User, QuizAttempt, QuizAttemptDetail
from sqlalchemy import or_, and_
import random  # moved import here

# Create a Blueprint for the quiz-related routes
kuiz_bp = Blueprint('kuiz', __name__)

def get_logged_in_user():
    if 'username' not in session:
        return None
    user = User.query.filter_by(username=session['username']).first()
    if not user:
        session.pop('username', None)
        return None
    return user

# Route to fetch all quiz questions from the database
@kuiz_bp.route('/quizzes', methods=['GET'])
def get_quizzes():
    user = get_logged_in_user()
    all_questions = Question.query.filter(
        or_(
            Question.visibility == 'public',
            and_(
                Question.visibility == 'personal',
                Question.user_id == user.id
            )
        )
    ).all()  # fetches all questions from the database
    
    quizzes = [
        {"id": q.id, 
         "question": q.question_text, 
         "options": q.options, 
         "answer": q.answer}
         for q in all_questions
        ]
    
    return render_template('index.html', quizzes=quizzes)

@kuiz_bp.route('/submit-quiz', methods=['POST'])
def submit_quiz():
    user = get_logged_in_user()
    if not user:
        return redirect(url_for('auth.login_get'))

    question_ids = []

    for key in request.form.keys():
        if key.startswith('question_'):
            parts = key.split('_')
            if len(parts) == 2 and parts[1].isdigit():
                question_ids.append(int(parts[1]))

    score = 0
    total = len(question_ids)
    details = []

    for qid in question_ids:
        question = Question.query.get(qid)
        user_answer = request.form.get(f"question_{qid}")
        correct_answer = question.answer
        
        if user_answer and user_answer.strip().lower() == correct_answer.strip().lower():
            score += 1

        details.append(QuizAttemptDetail(
            question_id=qid,
            user_answer=user_answer,
            correct_answer=correct_answer
        ))

    kuiz_id = None
    if details:
        question = Question.query.get(details[0].question_id)
        kuiz_id = question.kuiz_id

    attempt = QuizAttempt(
        user_id=user.id,
        kuiz_id=kuiz_id,
        score=score,
        total=total
    )
    db.session.add(attempt)
    db.session.flush()  # to get attempt.id

    for detail in details:
        detail.attempt_id = attempt.id
        db.session.add(detail)

    db.session.commit()

    return render_template('score_result.html', score=score, total=total)

@kuiz_bp.route('/create-question', methods=['GET'])
def create_question_form():
    categories = Kuiz.query.all()
    category_id = request.args.get('category_id')  
    return render_template('create_question.html', categories=categories, category_id=category_id)

@kuiz_bp.route('/create-question', methods=['POST'])
def create_question():
    user = get_logged_in_user()
    if not user:
        return redirect(url_for('auth.login_get'))

    question_text = request.form['question_text']
    options = [opt.strip() for opt in request.form['options'].split(',')]
    answer = request.form['answer']
    category_id = int(request.form['kuiz_id'])
    visibility = request.form.get('visibility')

    new_question = Question(
        question_text=question_text,
        options=options,
        answer=answer,
        kuiz_id=category_id,
        visibility = visibility,
        user_id=user.id  # Track the creator
    )

    db.session.add(new_question)
    db.session.commit()

    return redirect(url_for('kuiz.edit_category_form', category_id=category_id))

@kuiz_bp.route('/edit-question/<int:question_id>', methods=['GET', 'POST'])
def edit_question(question_id):
    question = Question.query.get_or_404(question_id)
    
    user = get_logged_in_user()
    if not user:
        return redirect(url_for('auth.login_get'))

    # Check permission
    if question.user_id != user.id:
        return render_template(
            'no_permission.html',
            message="You do not have permission to edit or delete this question.",
            back_url=url_for('kuiz.edit_category_form', category_id=question.kuiz_id)
        ), 403
    else:
        if request.method == 'POST':
            question.question_text = request.form['question_text']
            question.options = [opt.strip() for opt in request.form['options'].split(',')]
            question.answer = request.form['answer']
            question.visibility = request.form.get('visibility')
            db.session.commit()
            return redirect(url_for('kuiz.edit_category_form', category_id=question.kuiz_id))

    return render_template('edit_question.html', question=question)

@kuiz_bp.route('/delete-question/<int:question_id>', methods=['POST', 'GET'])
def delete_question(question_id):
    user = get_logged_in_user()
    if not user:
        return redirect(url_for('auth.login_get'))

    question = Question.query.get_or_404(question_id)

    if question.user_id != user.id:
        return render_template(
            'no_permission.html',
            message="You do not have permission to delete this question.",
            back_url=url_for('kuiz.edit_category_form', category_id=question.kuiz_id)
        ), 403

    category_id = question.kuiz_id  
    db.session.delete(question)
    db.session.commit()
    return redirect(url_for('kuiz.edit_category_form', category_id=category_id))

@kuiz_bp.route('/answer')
def answer():
    user = get_logged_in_user()
    if not user:
        return redirect(url_for('auth.login_get'))
    username = user.username
    categories = Kuiz.query.all()
    return render_template('answer.html', categories=categories, username=username)

@kuiz_bp.route('/quiz/<int:category_id>')
def get_quiz_by_category(category_id):
    category = Kuiz.query.get_or_404(category_id)
    questions = Question.query.filter_by(kuiz_id=category_id).all()
    return render_template('index.html', quizzes=questions)

@kuiz_bp.route('/categories')
def show_categories():
    user = get_logged_in_user()
    if not user:
        return redirect(url_for('auth.login_get'))
    username = user.username
    categories = Kuiz.query.all()
    return render_template('categories.html', categories=categories, username=username)
    
@kuiz_bp.route('/add-category', methods=['GET'])
def add_category_form():
    return render_template('add_category.html')

@kuiz_bp.route('/add-category', methods=['POST'])
def add_category():
    user = get_logged_in_user()
    if not user:
        return redirect(url_for('auth.login_get'))

    category_name = request.form['category_name']
    new_category = Kuiz(name=category_name, user_id=user.id)
    db.session.add(new_category)
    db.session.commit()
    return redirect(url_for('kuiz.show_categories'))

@kuiz_bp.route('/edit-category/<int:category_id>', methods=['GET'])
def edit_category_form(category_id):
    user = get_logged_in_user()
    if not user:
        return redirect(url_for('auth.login_get'))

    category = Kuiz.query.get_or_404(category_id)

    questions = Question.query.filter(
        or_(
            Question.visibility == 'public',
            and_(
                Question.visibility == 'personal',
                Question.user_id == user.id
            )
        )
    ).filter_by(kuiz_id=category_id).all()

    return render_template('edit_category.html', category=category, questions=questions)

@kuiz_bp.route('/edit-category/<int:category_id>', methods=['POST'])
def edit_category(category_id):
    user = get_logged_in_user()
    if not user:
        return redirect(url_for('auth.login_get'))

    category = Kuiz.query.get_or_404(category_id)

    # Update category name and commit
    category.name = request.form['category_name']
    db.session.commit()
    return redirect(url_for('kuiz.show_categories'))

@kuiz_bp.route('/delete-category/<int:category_id>', methods=['POST'])
def delete_category(category_id):
    user = get_logged_in_user()
    if not user:
        return redirect(url_for('auth.login_get'))

    category = Kuiz.query.get_or_404(category_id)

    if category.user_id != user.id:
        return render_template(
            'no_permission.html',
            message="You do not have permission to delete this category.",
            back_url=url_for('kuiz.show_categories')
        ), 403

    for question in category.questions:
        db.session.delete(question)

    db.session.delete(category)
    db.session.commit()
    return redirect(url_for('kuiz.show_categories'))

@kuiz_bp.route('/start-quiz')
def start_quiz():
    user = get_logged_in_user()
    category_id = request.args.get('category_id', type=int)
    num_questions = request.args.get('num_questions', type=int)
    timer = request.args.get('timer', type=int)

    category = Kuiz.query.get_or_404(category_id)
    questions = Question.query.filter(
        or_(
            Question.visibility == 'public',
            and_(
                Question.visibility == 'personal',
                Question.user_id == user.id
            )
        )
    ).filter_by(kuiz_id=category_id).all()

    random.shuffle(questions)

    if not num_questions or num_questions < 1 or num_questions > len(questions):
        num_questions = len(questions)

    questions = questions[:num_questions]

    if not timer or timer <= 0:
        timer = 60  # default timer 60 seconds

    return render_template('index.html', quizzes=questions, timer=timer, category=category)

@kuiz_bp.route('/choose-timer')
def choose_timer():
    category_id = request.args.get('category_id', type=int)
    category = Kuiz.query.get_or_404(category_id)

    user = get_logged_in_user()
    visible_questions = Question.query.filter(
        Question.kuiz_id == category.id,
        or_(
            Question.visibility == 'public',
            and_(
                Question.visibility == 'personal',
                Question.user_id == user.id
            )
        )
    ).all()

    return render_template('choose_timer.html', category=category, visible_questions=visible_questions)

@kuiz_bp.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return redirect(url_for('kuiz.home'))

@kuiz_bp.route('/')
def home():
    return redirect(url_for('kuiz.dashboard'))

@kuiz_bp.route('/review-attempts/<int:attempt_id>')
def review_attempt(attempt_id):
    user = get_logged_in_user()
    if not user:
        return redirect(url_for('auth.login_get'))

    attempt = QuizAttempt.query.get_or_404(attempt_id)
    details = QuizAttemptDetail.query.filter_by(attempt_id=attempt_id).all()

    return render_template('review_attempt.html', attempt=attempt, details=details)

@kuiz_bp.route('/past-attempts')
def past_attempts():
    user = get_logged_in_user()
    if not user:
        return redirect(url_for('auth.login_get'))

    attempts = QuizAttempt.query.filter_by(user_id=user.id).order_by(QuizAttempt.id.desc()).all()

    return render_template('past_attempts.html', attempts=attempts)

@kuiz_bp.route('/dashboard')
def dashboard():
    user = get_logged_in_user()
    if not user:
        return redirect(url_for('auth.login_get'))

    attempts = QuizAttempt.query.filter_by(user_id=user.id).order_by(QuizAttempt.id.desc()).all()
    
    return render_template('dashboard.html', username=user.username, attempts=attempts)

