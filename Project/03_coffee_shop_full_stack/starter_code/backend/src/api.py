from crypt import methods
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
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks-detail', methods=['GET'])
def get_drinks_detail():
    try:
        all_drinks_detail = Drink.query.all()
        if not all_drinks_detail:
            abort(404)
        drinks = [drink.long() for drink in all_drinks_detail]
        return jsonify({
            'success':True,
            'drinks':drinks           
        })
    except:
        abort(422)

'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks',methods=['POST'])
def create_drinks():
    try:
        request = request.get_json()
        drinks = Drink.query.all()
        if request:
            title = request['title']
            recipe = json.dumps(request['recipe'])
            drink = Drink(title, recipe)
            drink.insert()
            return jsonify({
                'success':True,
                'drinks':drink.long()
            })
        else:
            abort(403)
    except:
        abort(422)

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
@app.route('/drinks/<drink_id:int>',methods = ['PATCH'])
def update_drinks(drink_id):
    try:
        body = request.get_json()
        if not body:
            abort(403)

        drink = Drink.query.filter_by(id == drink_id).one_or_none()

        if not drink:
            abort(404)
        
        title = request
        
        if body['title'] and body['recipe']:
            drink.title = body.title
            drink.recipe = json.dump(body['recipe'])
        
        return jsonify({
            'success':True,
            'drinks':drink.long(),

        },200)
    except:
        abort(422)
        




    




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
@app.route('/drinks/<drink_id:int>',methods = ['DELETE'])
def delete_drink(drink_id):
    try:
        drink = Drink.query.filter_by(id==drink_id).one_or_none()
        if not drink:
            abort(404)
        
        drink.delete()
        return jsonify({
            'success':True,
            'delete':drink.id
        })
    except:
        abort(422)

        
    pass


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
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''
