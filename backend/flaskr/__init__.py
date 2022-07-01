import json
import numbers
import os
from tkinter.messagebox import ABORT
from unicodedata import category
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from sqlalchemy import func

from models import setup_db, Question, Category,db

QUESTIONS_PER_PAGE = 10

def paginate_questions(request, selection):
    page = request.args.get("page", 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    current_question = questions[start:end]

    return current_question

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    """
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    CORS(app)

    """
    @TODO: Use the after_request decorator to set Access-Control-Allow
    """
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        response.headers.add('Access-Control-Allow-Headers', 'GET, POST, PATCH, DELETE, OPTIONS')
        return response

    """
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    """
    @app.route('/categories')
    def get_categories():
        categories = Category.query.all()

        category_dict = {}
        
        for category in categories:
            category_dict[category.id] = category.type
        
        # return category data to view
        return jsonify({
            'success': True,
            'categories': category_dict,
            'total_categories': len(categories)
        })

    """
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """
    @app.route('/questions')
    def get_questions():
        questions = Question.query.all()
        current_question = paginate_questions(request, questions)
        categories = Category.query.order_by(Category.id).all()
        # filtered_questions = Question.query.filter(Question.category == Category.type).all()

        # print("categories:", categories)
        # print("questionss:", filtered_questions)


        if len(questions) == 0:
            abort(404)

        category_dict = {}
        
        for category in categories:
            category_dict[category.id] = category.type

        return jsonify(
            {
                'success' : True,
                'questions' : current_question,
                'totalQuestions': len(questions),
                'categories': category_dict,
                "currentCategory":category_dict[category.id]
            }
        )


    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.


    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """
    @app.route("/questions/<int:question_id>", methods=["DELETE"])
    def del_question(question_id):
        try:
            question = Question.query.get(question_id)

            if question is None:
                abort(422)

            question.delete()
            questions = Question.query.all()
            current_questions = paginate_questions(request, questions)

            return jsonify(
                {
                    'success': True,
                    'deleted': question_id,
                    'current_questions': current_questions,
                    'questions': len(questions),
                }
            )

        except:
            abort(404)


    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """
    @app.route('/question', methods=['POST'])
    def add_question():
        body = request.get_json()
        new_question = body.get("question")
        new_answer = body.get("answer")
        new_category = body.get("category")
        new_difficulty = body.get("difficulty")
        try:
            question = Question(question=new_question,answer=new_answer,category=new_category,difficulty=new_difficulty)
            question.insert()

            questions = Question.query.all()
            current_questions = paginate_questions(request, questions)

            return jsonify(
                {
                    "success": True,
                    'current_questions': current_questions,
                    'question_added' : question.id,
                    'total_questions': len(questions)
                }
            )

        except:
            abort(400)
    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.
    


    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """
    @app.route('/questions', methods=['POST'])
    def search_questions():
        try:
            body = request.get_json()
            search_term = body.get('searchTerm')
            search = "%{}%".format(search_term.replace(" ", "\ "))
            
        
            search_results = Question.query.filter(Question.question.match(search)).all()
            
            questions = []
            for result in search_results:
                questions.append(
                    result.format()
                )

            return jsonify({
                'success': True,
                'questions': questions,
                'total_questions': len(search_results),
            })
        except:
            abort(404)


    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """
    @app.route('/categories/<int:category_id>/questions')
    def category_questions(category_id):
        try:
            questions = Question.query.filter(Question.category == str(category_id)).order_by(Question.question).all()
            current_questions = paginate_questions(request, questions)
            category = Category.query.filter(Category.id == category_id).first()

            return jsonify({
                'success':True,
                'questions': current_questions,
                'total_questions': len(questions),
                'current_category': category.type
            })

        except:
            abort(404)

    """
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """
    @app.route('/quizzes', methods=['POST'])
    def play_quizzes():
        try:
            body = request.get_json()
            category = body.get('quiz_category')
            question = body.get('previous_questions')

            if category['type'] == 'play':
                all_questions = Question.query.all()
            else:
                all_questions = Question.query.filter_by(category=category['id']).all()

            next_questions = []
            for ques in all_questions:
                # print(ques.id)
                    if ques.id not in question:
                        next_questions.append(ques)
                        
            if len(next_questions) == 0:
                abort(400)
            else:
                random_questions = random.sample(next_questions,len(next_questions))

            next_question = random_questions[0].format()
        

            return jsonify({
                'success': True,
                'question': next_question,
                'category': next_question.get('category')
            })
        except:
            abort(422)
    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """
    @app.errorhandler(404)
    def not_found(error):
        return jsonify(
            {
                'success':False,
                'error': 404,
                'message': 'resource not found'
            }
        ), 404

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify(
            {
                'success':False,
                'error': 422,
                'message': 'unprocessable'
            }
        ), 422

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify(
            {
                'success':False,
                'error': 400,
                'message': 'bad request'
            }
        ), 400


    return app

