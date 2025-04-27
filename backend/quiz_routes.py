from flask import Blueprint, jsonify

quiz = Blueprint('quiz', __name__)

# Sample quiz data
quizzes = {
    1: {
        'title': 'General Knowledge Quiz',
        'questions': [
            {
                'question': 'What is the capital of France?',
                'options': ['Paris', 'London', 'Rome', 'Berlin'],
                'answer': 'Paris'
            },
            {
                'question': 'What is 2 + 2?',
                'options': ['3', '4', '5', '6'],
                'answer': '4'
            }
        ]
    }
}