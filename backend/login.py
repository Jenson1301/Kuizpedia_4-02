from flask import Flask, redirect, url_for, render_template, request

app = Flask(__name__)

@app.route('/login')
def login():
    return render_template('login.html')
    # opens the login page

@app.route('/')
def otherlogin():
    return redirect(url_for('login'))
    # if user enter url without /login, page still goes to /login page

if __name__ == '__main__':
    app.run(debug=True)
    # page updated automatically without need to restart after code changes
