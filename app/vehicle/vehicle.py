from flask import Blueprint, request, jsonify, make_response
from app import jwt, mongo

cars_collection = mongo.db.carsList

vehicle = Blueprint('vehicle', __name__)

@vehicle.route('/getVehicleList')
def getVehicleList():
    vehicle_list = cars_collection.find_one()
    vehicle_list.pop("_id")
    return jsonify(vehicle_list=vehicle_list, success=True), 200

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
        return jsonify("Brand not found", success=False), 400