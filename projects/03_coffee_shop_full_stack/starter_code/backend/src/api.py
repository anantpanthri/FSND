import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the database
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
db_drop_and_create_all()

## ROUTES
'''
@TODO DONE implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks', methods=['GET'])
def get_drinks():
    all_drinks = Drink.query.order_by(Drink.id).all()
    if not all_drinks:
        abort(404, {'message': 'no drinks found'})
    return jsonify({
        "success": True,
        "drinks": [drink.short() for drink in all_drinks]
    })


'''
@TODO DONE implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
            AUTH0 
                -Drink API add get:drinks-detail permissions
                -enable RBAC and add permission in access token
                    roles: create a new role for customers
                    users and roles: add role (cutomers) to users
    it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
    or appropriate status code indicating reason for failure
'''


@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def drinks_detail(payload):
    all_drinks = Drink.query.order_by(Drink.id).all()
    if not all_drinks:
        abort(404, {'message': 'no drinks found'})
    return jsonify({
        "success": True,
        "drinks": [drink.long() for drink in all_drinks]
    })


'''
@TODO DONE implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        AUTH0 
                -Drink API add post:drinks permissions
                -enable RBAC and add permission in access token
                    users and roles: add role (cutomers) to users
                It takes approximately 5 minutes to generate permissions     
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def create_drink(payload):
    body = request.get_json()
    drink = Drink(title=body['title'], recipe="""{}""".format(body['recipe']))
    drink.insert()
    drink.recipe = body['recipe']
    return jsonify({
        'success': True,
        'drinks': Drink.long(drink)
    })


'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks/<int:drink_id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def patch_drink(payload, drink_id):
    body = request.get_json()
    if not body:
        abort(400,
              {'message': 'Invalid JSON body.'}
              )
    drink_update = Drink.query.filter(Drink.id == drink_id).one_or_none()
    if not drink_update:
        abort(400,
              {'message': 'Id not found.'}
              )
    title = body.get('title', None)
    recipe = body.get('recipe', None)

    if title:
        drink_update.title = body['title']

    if recipe:
        drink_update.recipe = """{}""".format(body['recipe'])

    drink_update.update()

    return jsonify({
        'success': True,
        'drinks': [Drink.long(drink_update)]
    })


'''
@TODO DONE implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks/<int:drink_id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drinks(payload, drink_id):
    drink_delete_by_id = Drink.query.filter(Drink.id == drink_id).one_or_none()
    if not drink_delete_by_id:
        abort(404, {'message': 'Drink with id {} not found in database.'.format(drink_id)})
    drink_delete_by_id.delete()
    return jsonify({
        'success': True,
        'delete': drink_id
    })


############# Error Handling
'''
Example error handling for unprocessable entity
'''


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


'''
@TODO DONE implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False, 
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''


@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        "success": False,
        "error": 400,
        "message": "resource not found"
    }), 400


'''
@TODO DONE implement error handler for 404
    error handler should conform to general task above 
'''


@app.errorhandler(404)
def bad_request(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404


'''
@TODO DONE implement error handler for AuthError
    error handler should conform to general task above 
'''


@app.errorhandler(AuthError)
def authentication_failure(AuthError):
    return jsonify({
        "success": False,
        "error": AuthError.status_code,
        "message": "authentication failed"
    }), 401
