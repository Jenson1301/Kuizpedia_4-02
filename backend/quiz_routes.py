from flask import Blueprint, jsonify

# Create a Blueprint for the quiz-related routes
kuiz_bp = Blueprint('kuiz', __name__)  # This is where 'kuiz_bp' is defined.

# Sample Data (same as before)
quizzes = [
    {
        "id": 1,
        "name": "Math Quiz",
        "questions": [
            {"question": "What is 2 + 2?", "options": ["3", "4", "5", "6"], "answer": "4"},
            {"question": "What is 10 - 3?", "options": ["7", "6", "5", "8"], "answer": "7"}
        ]
    },
    {
        "id": 2,
        "name": "Science Quiz",
        "questions": [
            {"question": "What is the chemical symbol for water?", "options": ["H2O", "O2", "CO2", "N2"], "answer": "H2O"},
            {"question": "What planet is known as the Red Planet?", "options": ["Earth", "Mars", "Venus", "Jupiter"], "answer": "Mars"}
        ]
    }
]

# Define routes for the quiz data
@kuiz_bp.route('/quizzes', methods=['GET'])
def get_quizzes():
    return jsonify([quiz["name"] for quiz in quizzes])

@kuiz_bp.route('/quiz/<int:quiz_id>', methods=['GET'])
def get_quiz(quiz_id):
    quiz = next((quiz for quiz in quizzes if quiz["id"] == quiz_id), None)
    if quiz:
        return jsonify(quiz)
    else:
        return jsonify({"message": "Quiz not found"}), 404