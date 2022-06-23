import os
import unittest
import json
 

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia"
        self.database_path = "postgresql://{}:{}@{}/{}".format(
            "postgres", "hemid8th", "localhost:5432", self.database_name
        )
        setup_db(self.app, self.database_path)
        self.new_question = {"question":"does this work?","answer":"i dont know","category":"4","difficulty":2}
        self.search = {"searchTerm": "title"}
        # binds the app to the current context
        # with self.app.app_context():
        #     self.db = SQLAlchemy()
        #     self.db.init_app(self.app)
        #     # create all tables
        #     self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    def test_get_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(len(data['categories']),6)

    def test_get_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code,200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions']) 

    # def test_del_question(self):
    #     res = self.client().delete("/questions/22")
    #     data = json.loads(res.data)
        
    #     question = Question.query.get(22)
    
    #     self.assertEqual(res.status_code,200)
    #     self.assertEqual(data['success'],True)
        
    #     self.assertEqual(data['deleted'],22)
    #     self.assertEqual(question,None)    

    def test_del_question_does_not_exist(self):
        res = self.client().delete("/questions/100")
        data = json.loads(res.data)
        
        question = Question.query.get(100)

        self.assertEqual(res.status_code,404)
        self.assertEqual(data['success'],False)
        self.assertEqual(data['message'],"resource not found")  

    def test_create_new_question(self):
        res = self.client().post('/question', json=self.new_question)
        data = json.loads(res.data)

        print(data)
        self.assertEqual(res.status_code,200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'])

    def test_create_new_question_error(self):
        res = self.client().post('/question/100', json=self.new_question)
        data = json.loads(res.data)

        # print(data)
        self.assertEqual(res.status_code,404)
        self.assertEqual(data['success'], False)
        self.assertTrue(data['message'], "method not found")

    def test_create_new_question(self):
        res = self.client().post('/questions/search', json=self.search)
        data = json.loads(res.data)

        # print(data)

        self.assertEqual(res.status_code,200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'])


    
# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()