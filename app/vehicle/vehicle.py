from flask import Blueprint, request, jsonify, make_response
from app import jwt, mongo

cars_collection = mongo.db.carsList
customer_vehicle_collection = mongo.db.customer_vehicles
user_collection = mongo.db.users

vehicle = Blueprint('vehicle', __name__)

@vehicle.route('/getVehicleList')
def getVehicleList():
    vehicle_list = cars_collection.find_one()
    vehicle_list.pop("_id")
    return jsonify(vehicle_list=vehicle_list, success=True), 200

@vehicle.route('/getBrands')
def getBrands():
    vehicle_list = cars_collection.find_one()
    vehicle_list.pop("_id")
    brands = [i for i in vehicle_list.keys()]
    return jsonify(brands=brands, success=True), 200
    

@vehicle.route('/getBrandList', methods=['POST'])
def getBrandList():
    if not request.is_json:
        return make_response('Missing JSON in request', 400)
    payload = request.json 
    brand = payload.get('brand')
    vehicle_list = cars_collection.find_one()
    vehicle_list.pop("_id")
    brand_list = vehicle_list[brand]
    if brand_list:
        return jsonify(brand_list=brand_list, success=True),200
    else:
        return jsonify(msg="Brand not found", success=False), 400 


# jwt required 
@vehicle.route('/addVehicle', methods=['POST'])
def addVehicle():
    if not request.is_json:
        return make_response('Missing JSON in request', 400)
    payload = request.json
    uid = payload.get("uid")
    if not uid:
        return jsonify(msg="uid missing", success=False),400
    
    carDetails = payload.get('carDetails')
    if not carDetails:
        return jsonify(msg="Car Details Missing", success=False),400
    
    brand_list = cars_collection.find_one()
    model_list = brand_list.get(carDetails.get("company"))
    if not model_list:
        return jsonify(msg="Brand not found", success=False), 400
    
    model = carDetails.get("model")
    if model not in model_list:
        return jsonify(msg="Model not found", success=False), 400
    else:
        user = user_collection.find_one({"uid": uid})
        if not user:
            return jsonify(msg="User not found", success=False), 400
        else:
            # user['carDetails'] = carDetails
            user_collection.update_one({'uid': uid}, {'$set': {'carDetails': carDetails}})
            return jsonify(msg="Vehicle details added", carDetails=carDetails), 200
    

