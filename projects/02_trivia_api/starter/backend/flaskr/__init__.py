import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS, cross_origin
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

    '''
  @TODO DONE: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
    '''
  @TODO DONE: Use the after_request decorator to set Access-Control-Allow
  '''

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PATCH,POST,DELETE,OPTIONS')
        return response

    '''
  @TODO DONE: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''

    @app.route('/categories', methods=['GET'])
    @cross_origin()
    def get_categories():
        categories = Category.query.all()
        if not categories:
            abort(404)
        print([category.format() for category in categories])
        return jsonify({
            'success': True,
            'categories': [category.format() for category in categories]
        })

    def paginate(request, selection):
        page = request.args.get('page', 1, type=int)
        start = (page - 1) * QUESTIONS_PER_PAGE
        end = start + QUESTIONS_PER_PAGE
        questions = [question.format() for question in selection]
        current_questions = questions[start:end]
        return current_questions

    '''
      @TODO DONE: 
      Create an endpoint to handle GET requests for questions, 
      including pagination (every 10 questions). 
      This endpoint should return a list of questions, 
      number of total questions, current category, categories. 
    '''

    @app.route('/questions', methods=['GET'])
    def get_questions():
        question_query = Question.query.order_by(Question.id).all()
        paginated_questions = paginate(request, question_query)
        if len(paginated_questions) == 0:
            abort(404)
        categories = Category.query.all()
        return jsonify({
            'success': True,
            'questions': paginated_questions,
            'total_questions': len(question_query),
            'categories': [category.format() for category in categories],
            'current_category': 1  # should be taken from session or request form
        })

    '''
        TEST DONE: At this point, when you start the application
        you should see questions and categories generated,
        ten questions per page and pagination at the bottom of the screen for three pages.
        Clicking on the page numbers should update the questions.
    '''

    '''
    @TODO DONE: 
    Create an endpoint to DELETE question using a question ID. 

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page. 
  '''

    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        question = Question.query.filter(Question.id == question_id)
        if not question:
            abort(404)
        try:
            question.delete()
            return jsonify({
                'success': True,
                'deleted_question_id': question_id
            })
        except:
            abort(404)

    '''
      @TODO: 
      Create an endpoint to POST a new question, 
      which will require the question and answer text, 
      category, and difficulty score.
    
      TEST: When you submit a question on the "Add" tab, 
      the form will clear and the question will appear at the end of the last page
      of the questions list in the "List" tab.  
    '''

    @app.route('/questions',methods=['POST'])
    def create_search_question():
        body=request.get_json()
        if not body:
            abort(404)
        search_term=body.get('searchTerm',None)
        if search_term:
            questions = Question.query.filter(Question.question.ilike('%'+search_term+'%')).all()
            if not questions:
                abort(404)
            query_question = Question.query.order_by(Question.id).all()
            categories = Category.query.all()
            return jsonify({
                'success': True,
                'questions':  [question.format() for question in questions],
                'total_questions': len(query_question),
                'current_category' : [category.format() for category in categories]
              })

        question=body.get('question',None)
        answer=body.get('answer',None)
        category=body.get('category',None)
        difficulty=body.get('difficulty',None)

        if not question or not answer or not category or not difficulty:
            abort(404)
        try:
            question=Question(
                question=question,
                answer=answer,
                category=category,
                difficulty=difficulty
            )
            question.insert()
            question_query=Question.query.order_by(Question.id).all()
            paginated_ques=paginate(request,question_query)

            return jsonify({
                'success':True,
                'new_id':question.id,
                'questions':paginated_ques,
                'total_question':len(question_query)
            })
        except:
            abort(422)

    '''
      @TODO: 
      Create a POST endpoint to get questions based on a search term. 
      It should return any questions for whom the search term 
      is a substring of the question. 
    
      TEST: Search by any phrase. The questions list will update to include 
      only question that include that string within their question. 
      Try using the word "title" to start. 
    '''
    @app.route('/questions',methods=['POST'])
    def search_question():
        body=request.get_json()
        if not body:
            abort(404)






    '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''

    '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''

    '''
  @TODO DONE: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''

    # ----------------------------------------------------------------------------#
    # API error handler & formatter.
    # ----------------------------------------------------------------------------#

    # TODO DONE: Create error handlers for all expected errors

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "bad request"
        }), 400

    @app.errorhandler(404)
    def ressource_not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "resource not found"
        }), 404

    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({
            "success": False,
            "error": 405,
            "message": "method not allowed"
        }), 405

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "unprocessable"
        }), 422

    @app.errorhandler(500)
    def internal_server_error(error):
        return jsonify({
            "success": False,
            "error": 500,
            "message": "internal server error"
        }), 500

    return app
