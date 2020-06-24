import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}/{}".format('localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app) 
            # create all tables
            self.db.create_all()

        self.sample_question = {
        'question': 'What is the first and most important thing you need to set your mind to?',
        'answer': 'Thinking of a mster plan, and start your mission .. leave your residence, Thinking how you could get some dead presidents',
        'difficulty': 10,
        'category': 1
    }

    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """

    #1

    def test_get_paginated_questions(self):
        response = self.client().get('/questions')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))

    def test_404_paginated_questions_page_out_pf_bound(self):
        response = self.client().get('/questions?page=10000')
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    #2

    def test_get_categories(self):
        response = self.client().get('/categories')
        data = json.loads(response.data)
    
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_categories'])
        self.assertTrue(len(data['categories']))

    #3

    def test_get_paginated_questions_per_categories(self):
        response = self.client().get('/categories/1/questions')
        data = json.loads(response.data)
    
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))
        self.assertTrue(data['current_category'])

    def test_404_paginated_questions_per_categories_category_DNE(self):
        response = self.client().get('/categories/1000/questions')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    #4

    def test_delete_question(self):
        #in order to make sure that a question of a certain id exists when running the test
        question = Question(question=self.sample_question['question'], answer=self.sample_question['answer'],
                            category=self.sample_question['category'], difficulty=self.sample_question['difficulty'])
        question.insert()
        question_id = question.id

        response = self.client().delete(f'/questions/{question_id}')
        data = json.loads(response.data)

        question_post_delete = Question.query.filter(Question.id == question_id).one_or_none()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], question_id)
        self.assertEqual(question_post_delete, None)

    def test_422_delete_question_that_DNE(self):
        response = self.client().delete('/questions/19826')
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unable to process request')

    #5

    def test_post_new_question(self):
        response = self.client().post('/questions', json=self.sample_question)
        data = json.loads(response.data)

        created_question = Question.query.filter_by(id=data['created_with_id']).one_or_none()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['created_with_id'], created_question.id)
        self.assertIsNotNone(created_question)

    def test_422_post_question_fail(self):
        response = self.client().post('/questions', json={})
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unable to process request')

    #6

    def test_search_questions(self):
        response = self.client().post('/questions/search',json={'searchTerm': 'ali'})
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(len(data['questions']), 1)

    def test_404_search_questions_that_DNE(self):
        response = self.client().post('/questions/search',json={'searchTerm': 'اكسر الشر'})
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def test_400_search_questions_bad_input(self):
        response = self.client().post('/questions/search',json={})
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'bad request')

    #7

    def test_quiz_endpoint(self):
        response = self.client().post('/quiz',
                                      json={'previous_questions': [{"id": 16}, {"id": 17}, {"id": 18}],
                                            'quiz_category': {'type': 'Art', 'id': '2'}})
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question'])
        self.assertEqual(data['question']['category'], '2')
        self.assertNotEqual(data['question']['id'], 16)
        self.assertNotEqual(data['question']['id'], 17)
        self.assertNotEqual(data['question']['id'], 18)

    def test_422_quiz_fail(self):
        response = self.client().post('/quiz',json={'quiz_category': {'type': 'Art', 'id': '2'}})
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unable to process request')





# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()