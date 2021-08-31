from flask import Blueprint, request, jsonify, make_response
from app import jwt, mongo
from werkzeug.security import generate_password_hash, check_password_hash
from app.utils.helper import * 
from flask_jwt_extended import create_access_token
from flask_jwt_extended import jwt_required
import datetime

user_collection = mongo.db.users

user = Blueprint('user', __name__)

@user.route('/register', methods=['POST'])
def register():
    if not request.is_json:
        return make_response('Missing JSON in request', 401)
    
    payload = request.json
    email = payload.get("email")

    user = user_collection.find_one({"email": email})
    if user:
        return make_response('email already registerd', 409)
    
    user = user_collection.find_one({"phoneNo": payload.get('phoneNo')})
    if user:
        return make_response('Phone number alredy registerd', 409)
    
    user_info = {}
    fields = ['email', 'name', 'phoneNo', 'password']
    for field in fields:
        user_info[field] = payload.get(field)
    
    if payload.get('password'):
        user_info['password'] = generate_password_hash(payload.get('password'))
        user_info['isEmailVerified'] = False
        user_info['isGoogle'] = False
    else:
        user_info['isEmailVerified'] = True
        user_info['isGoogle'] = True
    
    user_info['uid'] = "U" + str(random_with_N_digits(10))
    user_info['isPhoneVerified'] = False

    access_token = create_access_token(identity=user_info['uid'])
    user_collection.insert(user_info)
    user_data = user_info
    user_data.pop("_id")

    return jsonify(msg='User is registered', access_token=access_token, user=user_data,success="True"), 201


@user.route('/login', methods=['POST'])
def login():
    if not request.is_json:
        return make_response('Missing JSON in request', 400)
    
    payload = request.json
    print(payload)
    email = payload.get('email')
    password = payload.get('password')

    user = user_collection.find_one({"email": email})

    if not user:
        return make_response('User not found', 400)

    if user.get('password'):
        if check_password_hash(user.get('password'), password):
            access_token = create_access_token(identity=user.get('uid'))
            user.pop("_id")
            return jsonify(msg='Login successful', access_token=access_token, user=user, success="True"), 200

        else:
            return make_response('Wrong credentials', 400)
    else:
        return make_response('Login using Google', 400)
    


