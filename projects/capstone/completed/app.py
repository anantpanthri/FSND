import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from auth import requires_auth
from models import db_init, db_reboot, Actor, Movie

PAGES = 10


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    db_init(app)
    # uncomment the first time
    # db_reboot()
    CORS(app)

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PATCH,POST,DELETE,OPTIONS')
        return response

    def paginate_results(request, selection):
        page = request.args.get('page', 1, type=int)
        start = (page - 1) * PAGES
        end = start + PAGES
        movie_or_actor_rows = [movie_actor.format() for movie_actor in selection]
        return movie_or_actor_rows[start:end]

    @app.route('/health', methods=['GET'])
    def get_health():
        return jsonify({
            'success': True,
            'health': "APP is up"
        })

    # ----------------------------------------------
    # Actors endpoint GET/POST/DELETE/PATCH
    # ----------------------------------------------

    @app.route('/actors', methods=['GET'])
    @requires_auth('get:actors')
    def get_actors(payload):
        actor_query = Actor.query.order_by(Actor.id).all()
        paginated_actor = paginate_results(request, actor_query)

        if len(paginated_actor) == 0:
            abort(404, {'message': 'actors not found'})

        return jsonify({
            'success': True,
            'actors': paginated_actor
        })

    @app.route('/actors', methods=['POST'])
    @requires_auth('create:actors')
    def post_actors(payload):
        body = request.get_json()
        if not body:
            abort(400, {'message': 'Invalid data.'})
        name = body.get('name', None)
        age = body.get('age', None)
        gender = body.get('gender', None)
        if not name or not age:
            abort(422, {'message': 'name or age not provided.'})
        new_actor = (Actor(
            name=name,
            age=age,
            gender=gender
        ))
        new_actor.insert()

        return jsonify({
            'success': True,
            'created': new_actor.id
        })

    @app.route('/actors/<actor_id>', methods=['DELETE'])
    @requires_auth('delete:actors')
    def delete_actors(payload, actor_id):
        if not actor_id:
            abort(400, {'message': 'no actor id provided.'})
        delete_actor = Actor.query.filter(Actor.id == actor_id).one_or_none()
        if not delete_actor:
            abort(404, {'message': 'Actor id {} not found.'.format(actor_id)})
        delete_actor.delete()

        return jsonify({
            'success': True,
            'deleted': actor_id
        })

    @app.route('/actors/<actor_id>', methods=['PATCH'])
    @requires_auth('update:actors')
    def update_actors(payload, actor_id):
        body = request.get_json()
        if not actor_id:
            abort(400, {'message': 'no actor id provided.'})
        if not body:
            abort(400, {'message': 'no body provided.'})

        update_actor = Actor.query.filter(Actor.id == actor_id).one_or_none()
        if not update_actor:
            abort(404, {'message': 'Actor id {} not found.'.format(actor_id)})

        name = body.get('name', update_actor.name)
        age = body.get('age', update_actor.age)
        gender = body.get('gender', update_actor.gender)
        update_actor.name = name
        update_actor.age = age
        update_actor.gender = gender

        update_actor.update()

        return jsonify({
            'success': True,
            'updated': update_actor.name,
            'actor': [update_actor.format()]
        })

    # ----------------------------------------------
    #  Movies endpoint GET/POST/DELETE/PATCH
    # ----------------------------------------------

    @app.route('/movies', methods=['GET'])
    @requires_auth('get:movies')
    def get_movies(payload):
        movie_query = Movie.query.order_by(Movie.id).all()
        paginated_movies = paginate_results(request, movie_query)
        if len(paginated_movies) == 0:
            abort(404, {'message': 'Movies not found.'})

        return jsonify({
            'success': True,
            'movies': paginated_movies
        })

    @app.route('/movies', methods=['POST'])
    @requires_auth('create:movies')
    def post_movies(payload):
        body = request.get_json()
        title = body.get('title', None)
        release_date = body.get('release_date', None)
        if not body or not title or not release_date:
            abort(400, {'message': 'Body or title or release_date not found.'})
        movie = (Movie(
            title=title,
            release_date=release_date
        ))
        movie.insert()
        return jsonify({
            'success': True,
            'created': movie.title
        })

    @app.route('/movies/<movie_id>', methods=['DELETE'])
    @requires_auth('delete:movies')
    def delete_movies(payload, movie_id):
        if not movie_id:
            abort(400, {'message': 'movie_id absent.'})
        movie_query = Movie.query.filter(Movie.id == movie_id).one_or_none()
        if not movie_query:
            abort(404, {'message': 'Movie id {} not found.'.format(movie_id)})
        movie_query.delete()
        return jsonify({
            'success': True,
            'deleted': movie_id
        })

    @app.route('/movies/<movie_id>', methods=['PATCH'])
    @requires_auth('update:movies')
    def update_movies(payload, movie_id):
        body = request.get_json()
        if not movie_id or not body:
            abort(400, {'message': 'movie id or body absent in request.'})
        movie_query = Movie.query.filter(Movie.id == movie_id).one_or_none()
        if not movie_query:
            abort(404, {'message': 'Movie id {} not found.'.format(movie_id)})
        title = body.get('title', movie_query.title)
        release_date = body.get('release_date', movie_query.release_date)
        movie_query.title = title
        movie_query.release_date = release_date
        movie_query.update()
        return jsonify({
            'success': True,
            'edited': movie_query.id,
            'movie': [movie_query.format()]
        })

    # ----------------------------------------------
    # Error handlers for all expected errors
    # ----------------------------------------------
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


app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
