
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
@app.route('/drinks', methods=['GET'])
def get_drinks():
    drink = Drink.query.all()
    drinks = [drink.short() for drink in drink]
    
    if len(drinks) == 0:
        abort(404)
    
    return jsonify({
        "success": True,
        "drinks": drinks
    })

'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def get_drinks_detail(permission, payload):
    drink_detail = Drink.query.all()
    drinks = [drink.long() for drink in drink_detail]

    if len(drinks) == 0:
        abort(404)

    return jsonify({
        "success": True,
        "drinks": drinks
    })

'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/create', methods=['POST'])
@requires_auth('post:drinks')
def new_drink(permission, payload):
        body = request.get_json()
        title = body.get('title', None)
        recipe = body.get('recipe', None)
        try:
            if recipe is None:
               abort(422)
            recipe_drink = json.dumps(recipe)
            new_drink = Drink(title=title, recipe=recipe_drink)
            new_drink.insert()

            return jsonify({
                "success": True,
                "created": [new_drink.long()]
            })
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
@app.route('/drinks/<int:drink_id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink(drink_id, permission, payload):
    body = request.get_json()
    try:
        body = request.get_json()
        drink = Drink.query.get(drink_id)
        
        if drink is None:
            abort(404)
            
        update_title = body.get('title', None)
        update_recipe = body.get('recipe', None)
        
        if 'title' in body:
            drink.title = update_title
    
        if 'recipe' in body and update_recipe is not None:
            drink.recipe = json.dumps(update_recipe)
    
        drink.update()
        
        return jsonify({
            "success": True,
            "drinks": [drink.long()]
        })
        
    except:
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
@app.route('/drinks/<int:drink_id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(drink_id, permission, payload):
        try:
            drink = Drink.query.filter_by(id=drink_id).one_or_none()
            if drink is None:
                abort(404)
            drink.delete()
            
            return jsonify({
                "success": True,
                "deleted": drink.id
            })
        except:
            abort(422)

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
@app.errorhandler(400)
def Bad_request(error):
    return jsonify({
        "success": False,
        "error": 400,
        "message": "bad request"
    }), 400

@app.errorhandler(401)
def Not_authorized(error):
    return jsonify({
        "success": False,
        "error": 401,
        "message": "not Authorized"
    }), 401

@app.errorhandler(403)
def Prohibited(error):
    return jsonify({
        "success": False,
        "error": 403,
        "message": "prohibited"
    }), 403

@app.errorhandler(500)
def internal_server_error(error):
    return jsonify({
        "success": False,
        "error": 500,
        "message": "internal server error"
    }), 500


'''
@TODO implement error handler for 404
    error handler should conform to general task above
'''
@app.errorhandler(404)
def Not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "not found"
    }), 404


'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''
@app.errorhandler(422)
def Auth_error(error):
    return jsonify({
        "success": False,
         "error": error.status_code,
        "message": error.error.get('description')
    }), error.status_code
