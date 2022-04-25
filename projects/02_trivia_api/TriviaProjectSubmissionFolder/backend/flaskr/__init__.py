import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
import logging

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def paginate_questions(request, selection):
    page = request.args.get("page",1,type=int)
    start=(page-1)*QUESTIONS_PER_PAGE
    end = start+QUESTIONS_PER_PAGE
    questions =[question.format() for question in selection]
    current_questions = questions[start:end]
    return current_questions

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    '''
    Set up CORS. Allow '*' for origins. Delete the sample route
    '''
    cors = CORS(app, resources={r"/": {"origins": "*"}})

    # CORS Headers
    '''
    Use the after_request decorator to set Access-Control-Allow
    '''
    @app.after_request
    def after_request(response):
        response.headers.add(
            "Access-Control-Allow-Headers", "Content-Type,Authorization,true"
        )
        response.headers.add(
            "Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS"
        )
        return response


    '''
    Create an endpoint to handle GET requests
    for all available categories.
    '''
    @app.route("/categories", methods=["GET"])
    def return_all_categories():
        categories = Category.query.order_by(Category.id).all()
        if len(categories) == 0:
            abort(404)
        return jsonify({
          'success': True,
          'categories': {
            category.id: category.type for category in categories
          }
        })


    '''
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    '''
    @app.route("/questions", methods=["GET"])
    def return_all_questions():
        questions = Question.query.order_by(Question.id).all()
        count = len(questions)
        paginated_question = paginate_questions(request,questions)
        categories = Category.query.order_by(Category.id).all()
        categories_formatted = {
          category.id: category.type for category in categories
        }
        if len(paginated_question) == 0:
            abort(404)
        if len(categories_formatted) == 0:
            abort(404)
        return jsonify({
          'success': True,
          'questions': paginated_question,
          'total_questions': count,
          'categories': categories_formatted,
          'current_category': None,
        })

    '''
            Create an endpoint to DELETE question using a question ID.

            TEST: When you click the trash icon next to a question, the question will be removed.
            This removal will persist in the database and when you refresh the page.
    '''

    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):

            question = Question.query.filter(Question.id == question_id).one_or_none()
            if question is None:
                abort(404)
            else:
                try:
                    question.delete()
                    return jsonify({
                        'success': True,
                        'deleted': question_id,
                        })
                except Exception:
                    abort(422)

    '''
            Create an endpoint to POST a new question,
            which will require the question and answer text,
            category, and difficulty score.

            TEST: When you submit a question on the "Add" tab,
            the form will clear and the question will appear at the end of the last page
            of the questions list in the "List" tab.
    '''
    @app.route('/questions', methods=['POST'])
    def create_question():
        body = request.get_json()
        question = body.get('question', None)
        answer = body.get('answer', None)
        difficulty = body.get('difficulty', None)
        category = body.get('category', None)
        try:
            question = Question(question=question,answer=answer,difficulty=difficulty,category=category)
            question.insert()
            return jsonify({
              'success': True,
              'created': question.id,
            })
        except Exception:
            abort(422)

    '''
            Create a POST endpoint to get questions based on a search term.
            It should return any questions for whom the search term
            is a substring of the question.

            TEST: Search by any phrase. The questions list will update to include
            only question that include that string within their question.
            Try using the word "title" to start.
    '''
    @app.route('/search', methods=['POST'])
    def search_question():
        body = request.get_json()
        search = body.get('searchTerm', None)
        questions = Question.query.order_by(Question.id).filter(Question.question.ilike('%{}%'.format(search)))
        questions_formatted = [
          question.format() for question in questions
        ]
        if len(questions_formatted) == 0:
            abort(404)
        return jsonify({
           'success': True,
           'questions': questions_formatted,
           'total_questions': len(questions_formatted),
           'current_category': None,
        })

    '''
              Create a GET endpoint to get questions based on category.
              TEST: In the "List" tab / main screen, clicking on one of the
              categories in the left column will cause only questions of that
              category to be shown.
    '''
    @app.route('/categories/<int:category_id>/questions', methods=['GET'])
    def retrieve_questions_by_category(category_id):
        questions = Question.query.order_by(Question.id).filter(Question.category == category_id).all()
        count = len(questions)
        paginated_question = paginate_questions(request,questions)
        if len(paginated_question) == 0:
            abort(404)
        else:
            return jsonify({
              'success': True,
              'questions': paginated_question,
              'total_questions': count,
              'current_category': category_id
            })

    '''
              Create a POST endpoint to get questions to play the quiz.
              This endpoint should take category and previous question parameters
              and return a random questions within the given category,
              if provided, and that is not one of the previous questions.

              TEST: In the "Play" tab, after a user selects "All" or a category,
              one question at a time is displayed, the user is allowed to answer
              and shown whether they were correct or not.
    '''
    @app.route('/quizzes', methods=['POST'])
    def retrieve_quizzes():
        try:
            questions = []
            body = request.get_json()
            #app.logger.info(body)
            quiz_category = body.get('quiz_category', None)
            previous_ids = body.get('previous_questions', None)
            category_id = quiz_category.get('id')
            if category_id ==0:
                questions = Question.query.all()
            else:
                questions = Question.query.filter(Question.category == category_id).all()
            question_ids = [question.id for question in questions]

            #print("questions are \n"+questions, flush=True)
            #print("question_ids are "+question_ids+" \n ******************************* \n", flush=True)

            ids = question_ids
            for id in question_ids:
                if id in previous_ids:
                    ids.remove(id)

            if len(ids) == 0:
                return jsonify({
                  'success': False,
                  'question': None
                })
            else:
                question = None
                while question is None:
                    random_id = random.choice(ids)
                    #app.logger.info(random_id)
                    #app.logger.info(ids)
                    question = Question.query.filter(Question.id == random_id).one_or_none()
                    #app.logger.info(question.format())
                if question is None:
                    return jsonify({
                      'success': False,
                      'question': None
                    })
                return jsonify({
                  'success': True,
                  'question': question.format()
                })

        except Exception:
            abort(422)

    '''
              Create error handlers for all expected errors
              including 404 and 422.
    '''
    @app.errorhandler(400)
    def bad_request_handler(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "Bad Request"
        }), 400

    @app.errorhandler(404)
    def not_found_handler(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "Resource not Found"
        }), 404

    @app.errorhandler(422)
    def can_not_process_handler(error):
        print(error)
        return jsonify({
            "success": False,
            "error": 422,
            "message": "Not Processable"
        }), 422

    @app.errorhandler(500)
    def internal_server_error_handler(error):
        print(error)
        return jsonify({
            "success": False,
            "error": 500,
            "message": "Internal Server Error"
        }), 500

    return app
