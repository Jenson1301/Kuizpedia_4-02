from flask import Flask
from quiz_routes import kuiz_bp  

app = Flask(__name__)

# Register the blueprint
app.register_blueprint(kuiz_bp)

@app.route('/')
def welcome():
    return 'Welcome to Kuizpedia'

if __name__ == '__main__':
    app.run(debug=True)