#from crypt import methods
import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, get_token_auth_header, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)



# ROUTES
'''
implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure

'''

@app.route('/drinks',methods = ['GET'])
def get_drinks():
    try:
        # Query all drinks
        all_drinks = Drink.query.all()
        #if all_drinks is empty throw 404
        if not all_drinks:
            abort(404)
        #
        drinks = [drink.short() for drink in all_drinks]
        return jsonify({
            'success':True,
            'drinks':drinks
         })
    except:
        abort(422)
'''
implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def get_drinks_detail(payload):
   try:
        # Query all drinks
        all_drinks = Drink.query.all()
        #if all_drinks is empty throw 404
        if not all_drinks:
            abort(404)
        #
        drinks = [drink.long() for drink in all_drinks]
        return jsonify({
            'success':True,
            'drinks':drinks
         })
   except:
        abort(422)

'''
implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route("/drinks", methods=['POST'])
@requires_auth('post:drinks')
def add_drinks(payload):
    request_body = request.get_json()
    title = request_body.get('title',None)
    recipe = request_body.get('recipe',None)

    if not title and recipe:
        abort(403)
    recipe_json = json.dumps(recipe)
    try:
        drink = Drink(title = title, recipe = recipe_json)
        drink.insert()
    except:
        abort(422)   
  
    return jsonify({
        'success':True,
        'recipe':drink.long(),
    })
    
'''
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''

@app.route('/drinks/<int:drink_id>',methods = ['PATCH'])
@requires_auth('patch:drinks')
def update_drinks(payload,drink_id):
    request_body = request.get_json()
    title = request_body.get('title',None)
    recipe = request_body.get('recipe',None)
    if not title and recipe:
        abort(403)
    recipe_json = json.dumps(recipe)
    try:
        drink = Drink.query.filter(Drink.id == drink_id).one_or_none()
        drink.title = title,
        drink.recipe = recipe_json
        updated_drinks = [drink.long()]
        return jsonify({
            'success':True,
            'drinks':update_drinks
        })  
    except:
        abort(422)     
'''
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''

@app.route('/drinks/<int:drink_id>',methods = ['DELETE'])
@requires_auth('delete:drinks' )
def delete_drink(payload,drink_id):
    try:
        drink = Drink.query.filter(Drink.id == drink_id).one_or_none()
        if not drink:
            abort(404) 
        drink.delete()
        return jsonify({
            'success':True,
            'delete':drink.id
        })
    except:
        abort(422)

# Error Handling

@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422

'''
@TODO implement error handler for 404
    error handler should conform to general task above
'''
@app.errorhandler(404)
def resource_not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404

@app.errorhandler(403)
def bad_request(error):
    return jsonify({
        "success": False,
        "error": 403,
        "message": "Bad request"
    }), 
'''
 implement error handler for AuthError
error handler should conform to general task above
'''
@app.errorhandler(AuthError)
def auth_error(error):
    return jsonify({
        'success': False,
        'error': error.status_code,
        'message': error.error['description']
    }), error.status_code





