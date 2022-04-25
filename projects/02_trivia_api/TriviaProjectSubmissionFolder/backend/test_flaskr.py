import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category

from flask import Flask, request, abort, jsonify


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = 'postgresql://{}:{}@{}/{}'.format("uwyne","password1",'localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)
        # new question
        self.new_question = {
                'question': 'Test Question',
                'answer': 'Test Answer',
                'difficulty': 5,
                'category': 1,
        }

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




    def test_return_all_categories(self):
        """Test return_all_categories """
        #print("test_return_all_categories")
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['categories'])
        self.assertEqual(len(data['categories']), 6)
        self.assertIsInstance(data['categories'], dict)

    def test_return_all_questions(self):
        """
        Test return_all_questions
        """
        #print("test_return_all_questions")
        res = self.client().get('/questions?page=1')
        data = json.loads(res.data)

        # Status code
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

        # Questions
        self.assertTrue(data['questions'])
        self.assertIsInstance(data['questions'], list)
        self.assertEqual(len(data['questions']), 10)

        # Total questions
        self.assertGreater(data['total_questions'], 20)

        # Categories
        self.assertTrue(data['categories'])
        self.assertEqual(len(data['categories']), 6)
        self.assertIsInstance(data['categories'], dict)
        self.assertEqual(data['current_category'], None)

    def test_404_sent_requesting_beyond_valid_page(self):
        '''
        Test requesting beyond valid page
        '''
        #print("test_404_sent_requesting_beyond_valid_page")
        res = self.client().get('/questions?page=1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Resource not Found')
    def test_404_if_question_does_not_exist(self):
        """
        Test 404 if question does not exist for delete
        """
        #print("test_422_if_question_does_not_exist")
        res = self.client().delete('/questions/'+str(500))
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Resource not Found')

    def test_create_and_delete_question(self):
        """
        Test create_question
        """
        #print("test_create_question")
        res = self.client().post('/questions', json=self.new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertGreater(data['created'], 0)
        """
            Test delete_question
        """
        id = str(data['created'])
        #print("test_delete_question")
        res = self.client().delete('/questions/'+ id)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], int(id))

    def test_search_questions(self):
        """
        Search questions
        """
        #print("test_search_questions")
        res = self.client().post(
            '/search',
            json={'searchTerm': 'Hematology'}
        )
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertIsInstance(data['questions'], list)
        self.assertEqual(len(data['questions']), 1)
        self.assertEqual(data['total_questions'], 1)
        self.assertEqual(data['current_category'], None)








    def test_search_questions_without_results(self):
        """
        Search questions without results
        """
        #print("test_search_questions_without_results")
        res = self.client().post(
            '/search',
            json={'searchTerm': 'Test'}
        )
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertIsInstance(data['questions'], list)
        self.assertGreater(len(data['questions']), 1)
        self.assertGreater(data['total_questions'], 0)
        self.assertEqual(data['current_category'], None)

    def test_retrieve_questions_by_category(self):
        """
        Test Get retrieve_questions_by_category
        """
        #print("test_retrieve_questions_by_category")
        res = self.client().get('/categories/1/questions?page=1')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

        self.assertTrue(data['questions'])
        self.assertIsInstance(data['questions'], list)
        self.assertGreater(len(data['questions']), 3)
        self.assertGreater(data['total_questions'], 3)
        self.assertEqual(data['current_category'], 1)

    def test_404_send_category_that_does_not_exist(self):
        """
        Test Get category that does not exist
        """
        #print("test_404_send_category_that_does_not_exist")
        res = self.client().get('/categories/1000/questions?page=1')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Resource not Found')

    def test_quizzes_without_category_and_get_all_questions(self):
        """
        Test quizzes without category and get all questions
        """
        #print("test_quizzes_without_category_and_get_all_questions")
        res = self.client().post('/quizzes', json={
            'previous_questions': [],
            'quiz_category': { 'type':'All','id':0}
        })
        data = json.loads(res.data)

        # Status code
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question'])
        self.assertIsInstance(data['question'], dict)

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
