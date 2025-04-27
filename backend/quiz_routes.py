from flask import Blueprint, jsonify

quiz = Blueprint('quiz', __name__)

# Sample quiz data
quizzes = {
    1: {
        'title': 'General Knowledge Kuiz',
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

# Route to list all kuizzes
@quiz.route('/kuizzes', methods=['GET'])
def get_kuizzes():
    kuiz_titles = {kid: data['title'] for kid, data in kuizzes.items()}
    return jsonify(kuiz_titles)

# Route to get a specific kuiz
@quiz.route('/kuiz/<int:kuiz_id>', methods=['GET'])
def get_kuiz(kuiz_id):
    kuiz = kuizzes.get(kuiz_id)
    if kuiz:
        questions = [{'question': q['question'], 'options': q['options']} for q in kuiz['questions']]
        return jsonify({
            'title': kuiz['title'],
            'questions': questions
        })