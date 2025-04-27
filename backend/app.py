from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return '<h1>Welcome to Kuizpedia!</h1><p>Flask is running 🎉</p>'

if __name__ == '__main__':
    app.run(debug=True)