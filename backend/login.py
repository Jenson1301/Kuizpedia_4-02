from flask import Flask, redirect, url_for, render_template, request, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
import re

app = Flask(__name__)
app.secret_key = 'satgi buat balik'

# CONFIGURE SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# DATABASE
class User(db.Model):     #####################dk why can submit null form###################
    email = db.Column(db.String, primary_key=True, unique=True, nullable=False)
    username = db.Column(db.String, unique=True, nullable=False)
    password_hash = db.Column(db.String, nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# HOME ROUTE
@app.route('/')
def home():
    if 'username' in session:
        return redirect(url_for('dashboard'))
    else:
        return redirect(url_for('login'))

# LOGIN ROUTE
@app.route('/login', methods=["GET"])
def login1():
    return render_template('login.html')

@app.route('/login', methods=["POST"])
def login():
    username = request.form['username']
    password = request.form['password']
    user = User.query.filter_by(username=username).first()
    if user:
        if user and user.check_password(password):
            session['username'] = username
            return redirect(url_for('dashboard'))
        else:
            flash('Wrong username or password.')
            return render_template('login.html')
    else:
        flash('Please sign up to continue.')
        return redirect(url_for('signup'))

# SIGNUP ROUTE
@app.route('/signup', methods=['GET'])
def signup1():
    return render_template('signup.html')

@app.route('/signup', methods=["POST"])
def signup():
    render_template('signup.html')
    email = request.form['email']
    username = request.form['username']
    password = request.form['password']
    confirmpassword = request.form['confirmpassword']
    user = User.query.filter_by(email=email).first()
    if user:
        flash('User already registered.')
        return redirect(url_for('login'))
    else:
        check = re.search(r'mmu.edu.my', email)
        if check:
            if confirmpassword != password:
                flash('Passwords do not match.')
                return redirect(url_for('signup'))
            else:
                new_user = User(username=username, email=email)
                new_user.set_password(password)
                db.session.add(new_user)
                db.session.commit()
                return redirect(url_for('login'))
        else:
            flash('Only email addresses with the MMU domain can use this app.')
            return redirect(url_for('login'))

# DASHBOARD ROUTE
@app.route('/dashboard')
def dashboard():
    if 'username' in session:
        return render_template('dashboard.html', username=session['username'])
    return redirect(url_for('home'))

# LOGOUT ROUTE
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('home'))


if __name__ in '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
