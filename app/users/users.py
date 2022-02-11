from sre_constants import SUCCESS
from tkinter import E
from flask import Blueprint, request, jsonify, make_response
from app import jwt, mongo
from werkzeug.security import generate_password_hash, check_password_hash
from app.utils.helper import * 
from flask_jwt_extended import create_access_token
from flask_jwt_extended import jwt_required
import datetime
import os
from werkzeug.utils import secure_filename
from firebase_admin import credentials, initialize_app, storage

cred = credentials.Certificate("garage-4a443-cebfff850cea.json")
initialize_app(cred, {'storageBucket': 'garage-4a443.appspot.com'})

user_collection = mongo.db.users
parking_space_collection = mongo.db.parkingSpaces

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
    user_collection.insert_one(user_info)
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
    

ALLOWED_IMAGE_EXTENSIONS = set(['png','jpg','jpeg','gif'])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.',1)[1].lower() in ALLOWED_IMAGE_EXTENSIONS

@user.route('/uploadImage', methods=['POST'])
def uploadImage():
    if 'file' not in request.files:
        return  make_response('Missing Files', 400)
    file = request.files['file']
    if file.filename == '':
        return make_response('Missing files', 400)
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join("image_dump",filename)
        file.save(filepath)
        bucket = storage.bucket()
        blob = bucket.blob(filepath)
        blob.upload_from_filename(filepath)
        blob.make_public()
        return jsonify(msg="Successfully uploaded image", public_url=blob.public_url), 200
    else:
        return make_response('Image type not supported', 400)



@user.route('/addParkingSpace', methods=['POST'])
def add_parking_space():
    if not request.is_json:
        return make_response('Missing JSON in request', 400)
    
    payload = request.json
  
    params = ['coords', 'images', 'addressText', 'uid', 'completeAddress']
    for param in params:
        if not param in payload.keys():
            make_response("Missing {}".format(param)), 400
    
    payload['pid'] = "PS" + str(random_with_N_digits(8))
    
    parking_space_collection.insert_one(payload)

    return make_response('Successfully added Parking Space', 200)


@user.route('/getAllParkingSpaces', methods=['GET', 'POST'])
def get_all_parking_spaces():
    if request.is_json:
        payload = request.json
        uid = payload.get("uid")
        if not uid:
            return make_response('Missing uid'), 400

        parking_spaces_list = list(parking_space_collection.find({"uid": uid}))
        for space in parking_spaces_list:
            space.pop("_id")
        
        return jsonify(parking_spaces_list=parking_spaces_list, success=True), 200

    else:
        parking_spaces_list = list(parking_space_collection.find())
        for space in parking_spaces_list:
            space.pop("_id")
        
        return jsonify(parking_spaces_list=parking_spaces_list, success=True), 200


@user.route('/getParkingSpacebyID', methods=['POST'])
def get_parking_space():
    if not request.is_json:
        return make_response('Missing JSON in request', 400)
    
    payload = request.json
    pid = payload.get("pid")
    if not pid:
        return make_response('Missing pid', 400)
    
    parking_space = parking_space_collection.find_one({"pid": pid})
    parking_space.pop("_id")

    return jsonify(parking_space=parking_space, success=True), 200


@user.route('/markParkingSpaceActive', methods=['POST'])
def mark_parking_space_active():
    if not request.is_json:
        return make_response('Missing JSON in request', 400)
    
    payload = request.json
    params = ["pid", "parking_slots", "rent_per_hour", "avilable_from", "avilable_to"]
    for param in params:
        if not param in payload.keys():
            make_response("Missing {}".format(param)), 400

   
    parking_space = parking_space_collection.find_one({"pid": payload.get("pid")})
    
    if not parking_space:
        return make_response('Invalid pid', 400)

    newValues = { "$set": {
        "parking_slots": payload.get("parking_slots"),
        "rent_per_hour": payload.get("rent_per_hour"), 
        "available_from": payload.get("available_from"),
        "available_to": payload.get("available_to"),
        "isActive": 1
    }}
    
    parking_space_collection.update_one({"pid": payload.get("pid")},newValues)

    parking_space = parking_space_collection.find_one({"pid": payload.get("pid")})
    print(parking_space)
 
    return jsonify(msg="successfull updated", pid=payload.get("pid"), success=True), 200


@user.route('/getActiveListings', methods=['GET'])
def get_active_listings():
    active_listings = list(parking_space_collection.find({"isActive": 1}))
    for listing in active_listings:
        listing.pop("_id")
    
    return jsonify(active_listings=active_listings, success=True), 200
    