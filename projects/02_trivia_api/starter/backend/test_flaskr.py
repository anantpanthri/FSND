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

    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """

    def test_endpoint_unavailable(self):
        """Test endpoint which does not exist """
        res = self.client().get('/categorical_questions')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['error'], 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def test_get_questions_categories(self):
        """Test endpoints questions and categories which exist """
        res = self.client().get('/questions')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(len(data['questions']) > 0)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['categories']) > 0)
        self.assertTrue(data['total_questions'] > 0)
        self.assertIsNotNone(data['current_category'])

    def test_paginate(self):
        """Test helper function paginate"""
        res = self.client().get('/questions')
        data = json.loads(res.data)
        self.assertTrue(len(data['questions']) == 10)
        self.assertTrue(data['total_questions'] > len(data['questions']))

    def test_delete_question(self):
        """TESTS POSTS AND DELETE"""
        post_question = {
            'question': 'Dummy Question',
            'answer': 'Yes indeed',
            'category': '2',
            'difficulty': 3
        }
        res = self.client().post('/questions', json=post_question)
        data = json.loads(res.data)
        question_id = data['new_id']
        # DELETE the newly created question
        res = self.client().delete('/questions/{}'.format(question_id))
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertEqual(data['deleted_question_id'], question_id)

    def test_create_search_question(self):
        """TESTS SEARCH QUESTIONS"""
        json_search_term = {
            'searchTerm': 'dummy',
        }
        res = self.client().post('/questions', json=json_search_term)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertTrue(len(data['questions']) > 0)
        self.assertTrue(data['total_questions'] > 0)

    def test_get_questions_from_categories(self):
        """TESTS QUESTIONS From categories"""
        category_id = 1
        res = self.client().get('/categories/{}/questions'.format(category_id))
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertTrue(len(data['questions']) > 0)
        self.assertTrue(data['total_questions'] > 0)

    def test_play_quiz_with_category(self):
        json_play_quizz = {
            'previous_questions' : [2, 3],
            'quiz_category' : {
                'type' : 'Science',
                'id' : '1'
                }
        }
        res = self.client().post('/quizzes', json = json_play_quizz)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertTrue(data['question']['question'])
        self.assertTrue(data['question']['id'] not in json_play_quizz['previous_questions'])

    def test_play_quiz_without_category(self):
        json_play_quizz = {
            'previous_questions' : [1, 2, 5]
        }
        res = self.client().post('/quizzes', json = json_play_quizz)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertTrue(data['question']['question'])
        # Also check if returned question is NOT in previous question
        self.assertTrue(data['question']['id'] not in json_play_quizz['previous_questions'])

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
