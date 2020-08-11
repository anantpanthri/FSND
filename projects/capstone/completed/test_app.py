import os
import unittest
from datetime import date

from flask_sqlalchemy import SQLAlchemy
import json
from app import create_app
from config import tokens
from models import db_init, db_reboot

assistant_header = {
    'Authorization': tokens['casting_assistant']
}

director_header = {
    'Authorization': tokens['casting_director']
}

producer_header = {
    'Authorization': tokens['executive_producer']
}


class CastingAgencyTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "casting_agency"
        self.database_path = "postgres://{}/{}".format('localhost:5432', self.database_name)
        db_init(self.app)
        db_reboot()
        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    def tearDown(self):
        """Executed after reach test"""
        pass

    # ---------------------
    # POST /actors
    # ---------------------

    def test_create_actor(self):
        """Director creates actor"""
        new_actor = {
            'name': 'Andy',
            'age': 29
        }
        result = self.client().post('/actors', json=new_actor, headers=director_header)
        data = json.loads(result.data)
        self.assertEqual(result.status_code, 200)
        self.assertTrue(data['success'])
        self.assertEqual(data['created'], 4)

    def test_authorization_error_new_actor(self):
        """Test Authorization error"""
        new_actor = {
            'name': 'Andy',
            'age': 29
        }
        result = self.client().post('/actors', json=new_actor)
        data = json.loads(result.data)
        self.assertEqual(result.status_code, 401)
        self.assertFalse(data['success'])

    # -------------
    # GET /actors
    # -------------

    def test_get_actors(self):
        """GET actors."""
        result = self.client().get('/actors?page=1', headers=assistant_header)
        data = json.loads(result.data)
        self.assertEqual(result.status_code, 200)
        self.assertTrue(data['success'])
        self.assertTrue(len(data['actors']) > 0)

    def test_404_errors(self):
        """actors not existing."""
        result = self.client().get('/actors?page=99999', headers=assistant_header)
        data = json.loads(result.data)
        self.assertEqual(result.status_code, 404)
        self.assertFalse(data['success'])

    # ----------------------
    # DELETE /actors
    # ----------------------

    def test_delete_error(self):
        """DELETE no Authorization"""
        result = self.client().delete('/actors/1')
        data = json.loads(result.data)
        self.assertEqual(result.status_code, 401)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], 'authentication failed')

    def test_no_permission(self):
        """DELETE no permissions"""
        result = self.client().delete('/actors/1', headers=assistant_header)
        data = json.loads(result.data)
        self.assertEqual(result.status_code, 401)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], 'authentication failed')

    def test_delete_actor(self):
        """Test DELETE """
        res = self.client().delete('/actors/1', headers=director_header)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertEqual(data['deleted'], '1')

    def test_error_delete(self):
        """DELETE actor not in database"""
        res = self.client().delete('/actors/9999', headers=director_header)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertFalse(data['success'])

    # ---------------
    # PATCH /actors
    # ---------------
    def test_400_error(self):
        """PATCH with no body"""

        result = self.client().patch('/actors/9999', headers=director_header)
        data = json.loads(result.data)
        self.assertEqual(result.status_code, 400)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], 'bad request')

    def test_update_actor(self):
        """PATCH actors"""
        actor_update = {
            'age': 30
        }
        result = self.client().patch('/actors/1', json=actor_update, headers=director_header)
        data = json.loads(result.data)
        self.assertEqual(result.status_code, 200)
        self.assertTrue(data['success'])
        self.assertTrue(len(data['actor']) > 0)

    # -----------------------
    # POST /movies
    # -----------------------

    def test_create_movie(self):
        """POST new movie."""

        json_create_movie = {
            'title': 'Do Little',
            'release_date': date.today()
        }

        result = self.client().post('/movies', json=json_create_movie, headers=producer_header)
        data = json.loads(result.data)
        self.assertEqual(result.status_code, 200)
        self.assertTrue(data['success'])

    def test_error_movie(self):
        """Error new movie."""
        movie_no_name = {
            'release_date': date.today()
        }
        result = self.client().post('/movies', json=movie_no_name, headers=producer_header)
        data = json.loads(result.data)
        self.assertEqual(result.status_code, 400)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], 'bad request')

    # -----------------------
    # GET /movies
    # -----------------------

    def test_get_movies(self):
        """GET movies."""
        result = self.client().get('/movies?page=1', headers=assistant_header)
        data = json.loads(result.data)
        self.assertEqual(result.status_code, 200)
        self.assertTrue(data['success'])
        self.assertTrue(len(data['movies']) > 0)

    def test_error_401__movies(self):
        """GET movies no Authorization"""
        result = self.client().get('/movies?page=1')
        data = json.loads(result.data)
        self.assertEqual(result.status_code, 401)
        self.assertFalse(data['success'])

    def test_error_movies_404(self):
        """Error GET movies."""
        result = self.client().get('/movies?page=9999', headers=assistant_header)
        data = json.loads(result.data)
        self.assertEqual(result.status_code, 404)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], 'resource not found')

    # -------------------------
    # DELETE /movies
    # -------------------------

    def test_delete_movie(self):
        """DELETE movie"""
        result = self.client().delete('/movies/1', headers=producer_header)
        data = json.loads(result.data)
        self.assertEqual(result.status_code, 200)
        self.assertTrue(data['success'])
        self.assertEqual(data['deleted'], '1')

    def test_401_delete_movie(self):
        """DELETE movie no Authorization"""
        result = self.client().delete('/movies/1')
        data = json.loads(result.data)
        self.assertEqual(result.status_code, 401)
        self.assertFalse(data['success'])

    # -------------------------
    # PATCH /movies
    # -------------------------

    def test_update_movie(self):
        """PATCH existing movies"""
        movie = {
            'release_date': date.today()
        }
        result = self.client().patch('/movies/1', json=movie, headers=producer_header)
        data = json.loads(result.data)
        self.assertEqual(result.status_code, 200)
        self.assertTrue(data['success'])
        self.assertTrue(len(data['movie']) > 0)

    def test_404_update_movie(self):
        """PATCH with non valid id"""
        movie = {
            'release_date': date.today()
        }
        result = self.client().patch('/movies/9999', json=movie, headers=producer_header)
        data = json.loads(result.data)

        self.assertEqual(result.status_code, 404)
        self.assertFalse(data['success'])

    def test_400_update_movie(self):
        """PATCH with no body"""
        result = self.client().patch('/movies/1', headers=producer_header)
        data = json.loads(result.data)
        self.assertEqual(result.status_code, 400)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], 'bad request')


if __name__ == "__main__":
    unittest.main()
