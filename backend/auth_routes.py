from flask import Blueprint, render_template, request, redirect, url_for, session, flash, current_app
from models import db, User
from flask_mail import Message
from itsdangerous import URLSafeTimedSerializer as Serializer
from extensions import mail
import re

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET'])
def login_get():
    if 'username' in session:
        redirect(url_for('kuiz.dashboard'))
    return render_template('login.html')

@auth_bp.route('/login', methods=['POST'])
def login_post():
    username = request.form['username']
    password = request.form['password']
    user = User.query.filter_by(username=username).first()
    if user:
        if user and user.check_password(password):
            session['username'] = username
            return redirect(url_for('kuiz.dashboard'))
        else:
            flash('Invalid username or password.')
            return render_template('login.html')
    else:
        flash('User not registered.')
        return render_template('login.html')

@auth_bp.route('/signup', methods=['GET'])
def signup_get():
    return render_template('signup.html')

@auth_bp.route('/signup', methods=['POST'])
def signup_post():
    email = request.form['email']
    username = request.form['username']
    password = request.form['password']
    confirmpassword = request.form['confirmpassword']

    if User.query.filter_by(email=email).first():
        flash('User already registered.')
        return redirect(url_for('auth.login_get'))

    if not re.search(r'mmu.edu.my', email):
        flash('Only MMU email addresses allowed.')
        return redirect(url_for('auth.signup_get'))

    if password != confirmpassword:
        flash('Passwords do not match.')
        return redirect(url_for('auth.signup_get'))

    new_user = User(email=email, username=username)
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()
    return redirect(url_for('auth.login_get'))

@auth_bp.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('auth.login_get'))

@auth_bp.route('/forgot_password', methods=['GET'])
def forgot_password_get():
    return render_template('forgot.html')

@auth_bp.route('/forgot_password', methods=['POST'])
def forgot_password_post():
    email = request.form['email']
    user = User.query.filter_by(email=email).first()
    if user:
        send_reset_mail(user)
        flash('Reset request sent. Check your email.')
        return redirect(url_for('auth.login_get'))
    else:
        flash('Email not registered.')
        return redirect(url_for('auth.signup_get'))

@auth_bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    user_id = User.verify_token(token)
    if not user_id:
        flash('Invalid or expired token.')
        return redirect(url_for('auth.forgot_password_get'))

    user = User.query.get(user_id)

    if request.method == 'POST':
        password = request.form['password']
        confirmpassword = request.form['confirmpassword']
        if password != confirmpassword:
            flash('Passwords do not match.')
        else:
            user.set_password(password)
            db.session.commit()
            flash('Password reset successful. Please login.')
            return redirect(url_for('auth.login_get'))

    return render_template('reset.html', token=token)

def send_reset_mail(user):
    seq = Serializer(current_app.config['SECRET_KEY'])
    token = seq.dumps({'user_id': user.id})
    reset_url = url_for('auth.reset_password', token=token, _external=True)
    msg = Message('Password Reset Request',
                  sender='kuizpedia@gmail.com',
                  recipients=[user.email])
    msg.body = f"Click the link to reset your password: {reset_url}"
    mail.send(msg)
