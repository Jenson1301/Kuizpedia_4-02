from flask import Flask, render_template
from quiz_routes import kuiz_bp  

app = Flask(__name__)

# Register the blueprint
app.register_blueprint(kuiz_bp)

@app.route('/')
def home():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)