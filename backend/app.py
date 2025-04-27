from flask import Flask
from quiz_routes import quiz

app = Flask(__name__)

# Register your blueprint
app.register_blueprint(quiz)

@app.route('/')
def home():
    return '<h1>Welcome to Kuizpedia!</h1>'

if __name__ == '__main__':
    app.run(debug=True)