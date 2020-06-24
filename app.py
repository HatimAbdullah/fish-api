import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS, cross_origin
import random
from sqlalchemy import or_

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10
CATEGORIES_PER_PAGE = 5

def paginate_questions(request, questions):
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    jsonified_questions = [question.format() for question in questions]
    jsonified_paginated_questions = jsonified_questions[start:end]

    return jsonified_paginated_questions

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  
  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''

  cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''

  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PATCH,POST,DELETE,OPTIONS')
    return response


  @app.route('/')
  @cross_origin()
  def welcome():
    return jsonify({'message':'hi! this is trivia API'})

  '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''

  @app.route('/categories')
  @cross_origin()
  def get_categories():
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * CATEGORIES_PER_PAGE
    end = start + CATEGORIES_PER_PAGE
    
    categories = Category.query.all()
    
    if len(categories) == 0:
      abort(404)

    jsonified_categories = [category.format() for category in categories]

    return jsonify({
      'success':True,
      'categories' : jsonified_categories[start:end],
      'total_categories' : len(categories)
      })

  '''
  @TODO: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 
  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''

  @app.route('/questions')
  def get_questions():
    questions = Question.query.all()

    if len(questions) == 0:
      abort(404)

    jsonified_paginated_questions = paginate_questions(request,questions)

    if (len(jsonified_paginated_questions) == 0):
      abort(404)

    categories = Category.query.all()
    jsonified_categories = [category.format() for category in categories]

    return jsonify({
      'success': True,
      'questions': jsonified_paginated_questions,
      'total_questions': len(questions),
      'categories': jsonified_categories,
      'current_category': None
      })

  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 
  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''

  @app.route("/questions/<int:question_id>", methods=['DELETE'])
  def delete_question(question_id):
    try:
      question = Question.query.get(question_id)
      question.delete()
      return jsonify({
        'success': True,
        'deleted': question_id
        })
    except:
     abort(422)

  '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.
  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''

  @app.route("/questions", methods=['POST'])
  def add_question():
    question_components = request.get_json()

    if not ('question' in question_components and 'answer' in question_components and 'difficulty' in question_components and 'category' in question_components):
      abort(422)

    submitted_question = question_components.get('question')
    submitted_answer = question_components.get('answer')
    submitted_difficulty = question_components.get('difficulty')
    submitted_category = question_components.get('category')

    try:
      question = Question(question=submitted_question, answer=submitted_answer, difficulty=submitted_difficulty, category=submitted_category)
      question.insert()

      return jsonify({
        'success': True,
        'created_with_id': question.id,
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
  @app.route("/questions/search", methods=['POST'])
  def search_questions():
    search_form = request.get_json(force=True)

    if search_form is None:
      abort(400)

    term = search_form.get('searchTerm', None)

    if term is None:
      abort(400)

    results = Question.query.filter(or_(Question.question.ilike(f'%{term}%') , Question.answer.ilike(f'%{term}%'))).all()

    if len(results) == 0:
      abort(404)

    jsonified_paginated_results = paginate_questions(request,results)

    return jsonify({
      'success': True,
      'questions': jsonified_paginated_results,
      'total_questions': len(results),
      'current_category': None
      })


  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 
  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''

  @app.route('/categories/<int:category_id>/questions', methods=['GET'])
  def get_questions_of_category(category_id):

    category = Category.query.get(category_id)

    if category is None:
      abort(404)

    try:
      questions = Question.query.filter(
      Question.category == str(category.id)).all()
      jsonified_paginated_questions = paginate_questions(request,questions)

      return jsonify({
        'success': True,
        'questions': jsonified_paginated_questions,
        'total_questions': len(questions),
        'current_category': category.type
        })
    except:
     abort(404)



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

  @app.route('/quiz', methods=['POST'])
  def quiztown():

    
    private_quiz = request.get_json()

    if not ('quiz_category' in private_quiz and 'previous_questions' in private_quiz):
      abort(422)

    category = private_quiz.get('quiz_category')
    previous_questions = private_quiz.get('previous_questions')

    try:
      if (category['id'] == 0):
        questions_pool = Question.query.all()
      else:
        questions_pool = Question.query.filter_by(category=category['id']).all()

      random_question = questions_pool[random.randrange(0, len(questions_pool), 1)]

      def is_used(question):
        used = False
        for q in previous_questions:
          if (q['id'] == question.id):
            used = True

        return used

      while (is_used(random_question)):
        random_question = questions_pool[random.randrange(0, len(questions_pool), 1)]


      if (len(previous_questions) == len(questions_pool)):
        return jsonify({
          'success': True,
          'question': "null"
        })

      return jsonify({
        'success': True,
        'question': random_question.format()
        })

    except:
      abort(422)

    '''
      if category['type'] == 'click':
        remaining_questions = Question.query.filter(
        Question.id.notin_((previous_questions))).all()
      else:
        remaining_questions = Question.query.filter_by(
        category=category['id']).filter(Question.id.notin_((previous_questions))).all()
      if len(remaining_questions) == 0:
        abort(404)
    new_question = remaining_questions[random.randrange(0, len(remaining_questions))].format()
  '''
  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''

  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
      "success": False, 
      "error": 404,
      "message": "resource not found"
      }), 404

  @app.errorhandler(400)
  def not_found(error):
    return jsonify({
      "success": False, 
      "error": 400,
      "message": "bad request"
      }), 400

  @app.errorhandler(422)
  def not_found(error):
    return jsonify({
      "success": False, 
      "error": 422,
      "message": "unable to process request"
      }), 422
  
  return app
