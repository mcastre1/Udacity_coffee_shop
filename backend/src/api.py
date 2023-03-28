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
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
'''
with app.app_context():
    db_drop_and_create_all()

# ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks')
def get_drinks():
    try:
        selection = Drink.query.all()
        drinks = []

        for drink in selection:
            drinks.append(drink.short())

        return jsonify({'success': True,
                        'drinks': drinks})
    except BaseException:
        abort(400)


'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def get_drinks_detail(jwt):
    selection = Drink.query.all()
    drinks = []

    for drink in selection:
        drinks.append(drink.long())

    return jsonify({"success": True,
                    "drinks": drinks})


'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def create_drink(jwt):
    body = request.get_json()
    try:
        title = str(body.get('title'))
        recipe = str(body.get('recipe')).replace("'", '"')

        drink = Drink()
        drink.title = title
        drink.recipe = recipe

        drink.insert()

        # print(drink.long())

        return jsonify({"success": True,
                        "drinks": []})
    except BaseException:
        abort(400)


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


@app.route('/drinks/<int:id>', methods=["PATCH"])
@requires_auth('patch:drinks')
def update_drink(jwt, id):
    body = request.get_json()
    try:
        # Get drink to be updated
        drink = Drink.query.get(int(id))

        # if no drink is found then we return
        # not found.
        if not drink:
            abort(404)

        # collect all data to be updated
        title = str(body.get('title'))
        recipe = str(body.get('recipe')).replace("'", '"')

        # update data
        drink.title = title
        drink.recipe = recipe

        # commit
        drink.update()

        return jsonify({"success": True,
                        "drinks": []})
    except BaseException:
        abort(400)


'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks/<int:id>', methods=["DELETE"])
@requires_auth('delete:drinks')
def delete_drink(jwt, id):
    print(f'Deletion of drink with id: {id}')

    try:
        # Get drink row with id.
        drink = Drink.query.get(int(id))

        # If no row with {id} is found, abort 404
        if not drink:
            abort(404)

        # Delete and return succesfully
        drink.delete()
        return jsonify({"success": True,
                        "drinks": id})
    except BaseException:
        abort(400)


# Error Handling
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
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''

'''
@TODO implement error handler for 404
    error handler should conform to general task above
'''


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 404,
        'message': 'Not found.'
    }), 404


'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''


@app.errorhandler(AuthError)
def auth_error(error):
    return jsonify({
        "success": False,
        "error": error.status_code,
        "message": error.error['description']
    }), error.status_code
