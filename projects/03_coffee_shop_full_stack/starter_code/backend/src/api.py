import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .auth.auth import AuthError, requires_auth

from .database.models import db_drop_and_create_all, setup_db, Drink


app = Flask(__name__)
setup_db(app)
CORS(app)

'''
 uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this function will add one
'''
db_drop_and_create_all()

# ROUTES
'''
    implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route("/drinks", methods=["GET"])
def get_drinks():
        drinkslist = Drink.query.order_by(Drink.id).all()
        count = len(drinkslist)

        if count == 0:
            abort(404)
        drinks_short = [drink.short() for drink in drinkslist]
        return jsonify({
            'success': True,
            'drinks': drinks_short
            })

'''
    implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route("/drinks-detail", methods=["GET"])
@requires_auth('get:drinks-detail')
def get_drinks_detail(jwt):
        drinkslist = Drink.query.order_by(Drink.id).all()
        count = len(drinkslist)

        if count == 0:
            abort(404)
        drinks_long = [drink.long() for drink in drinkslist]
        return jsonify({
            'success': True,
            'drinks': drinks_long
            })

'''
    implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route("/drinks", methods=["POST"])
@requires_auth('post:drinks')
def Post_drinks(jwt):
        body = request.get_json()
        title = body.get('title') or None
        recipe = body.get('recipe')
        if title is None:
            print("title is none")
            abort(400)
        try:
            drink = Drink(title=title, recipe=json.dumps(recipe))
            drink.insert()
            return jsonify({'success': True, 'drinks':[drink.long()]})
        except Exception as e:
            abort(422)



'''
    implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
@app.route("/drinks/<drink_id>", methods=["PATCH"])
@requires_auth('patch:drinks')
def Patch_drinks(*args, **kwargs):
        id = kwargs['drink_id']
        drinkObj = Drink.query.filter_by(id=id).one_or_none()
        if drinkObj is None:
            abort(404)
        body = request.get_json()
        title = body.get('title') or None
        if title is None:
            abort(400)
        if 'title' in body:
            drinkObj.title = body['title']
        if 'recipe' in body:
            drinkObj.recipe = json.dumps(body['recipe'])
        try:
            drinkObj.insert()
        except Exception as e:
            abort(400)
        drink = [drinkObj.long()]
        return jsonify({'success': True, 'drinks': drink})

'''
    implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
@app.route("/drinks/<drink_id>", methods=["DELETE"])
@requires_auth('delete:drinks')
def delete_drink(*args, **kwargs):
        id = kwargs['drink_id']
        drinkObj = Drink.query.filter_by(id=id).one_or_none()
        if drinkObj is None:
            abort(404)
        try:
            drinkObj.delete()
        except Exception as e:
            abort(422)
        return jsonify({'success': True, "delete": id})


# Error Handling
'''
              Create error handlers for all expected errors
              including 404 and 422.
'''
@app.errorhandler(400)
def bad_request_handler(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "Bad Request"
        }), 400

@app.errorhandler(404)
def not_found_handler(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "Resource not Found"
        }), 404

@app.errorhandler(422)
def can_not_process_handler(error):
        print(error)
        return jsonify({
            "success": False,
            "error": 422,
            "message": "Not Processable"
        }), 422

@app.errorhandler(500)
def internal_server_error_handler(error):
        print(error)
        return jsonify({
            "success": False,
            "error": 500,
            "message": "Internal Server Error"
        }), 500



'''
        implement error handler for AuthError
        error handler should conform to general task above
'''
@app.errorhandler(AuthError)
def handle_auth_error(ex):
        response = jsonify(ex.error)
        response.status_code = ex.status_code
        return response


if __name__ == "__main__":
    app.debug = True
    app.run()
