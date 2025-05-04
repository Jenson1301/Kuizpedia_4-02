from flask import Flask, redirect, url_for, render_template, request, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from itsdangerous import URLSafeTimedSerializer as Serializer
from flask_mail import Mail, Message
import re

app = Flask(__name__)

# SET KEY
app.config['SECRET_KEY'] = 'satgi buat balik'

# MAILING SETUP
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['USERNAME'] = 'kuizpedia402@gmail.com'
app.config['PASSWORD'] = 'Kuizpedia402(MiniITProject)'
mail = Mail(app)

# SQLAlchemy SETUP
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# DATABASE
class User(db.Model):     #####################dk why can submit null form###################
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String, unique=True, nullable=False)
    username = db.Column(db.String, unique=True, nullable=False)
    password_hash = db.Column(db.String, nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def create_token(self):
        seq = Serializer(app.config['SECRET_KEY'])
        return seq.dumps({'user_id': self.id})
    
    @staticmethod
    def verify_token(token, expiration = 300):
        seq = Serializer(app.config['SECRET_KEY'])
        try:
            user_id = seq.loads(token, max_age = expiration)['user_id']
        except:
            return None
        return User.query.get(user_id)

def sendResetMail(user):
    token = User.create_token(user)
    message = Message('Kuizpedia - Password Reset Request', recipients = user, sender = 'noreply@kuizpedia.com', body = '''
{url_for(reset)}
''')

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
    render_template('signup.html') ###################################################################
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

# RESET ROUTE
@app.route('/forgot_password', methods=['GET'])
def forgot1():
    return render_template('forgot.html')

@app.route('/forgot_password', methods=['POST'])
def forgot():
    email = request.form['email']
    user = User.query.filter_by(email=email).first()
    if user:
        sendResetMail(user)
        flash('Reset request sent. Please check your email.')
        return redirect(url_for('login'))
    else:
        flash('This account was never registered. Please signup to continue.')
        return redirect(url_for('signup'))

@app.route('/reset_password/<token>', methods = ['POST'])
def reset(token):
    user = User.verify_token(token)
    if user == None:
        flash('The token is invalid or has expired. Please try again.')
        return redirect(url_for(forgot))
    if user:
        password = request.form['password']
        User.set_password(password)
        db.session.commit()
        flash('Password changed successfully. Please login.')
        return redirect(url_for('login'))
    return render_template('reset.html')

if __name__ in '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
