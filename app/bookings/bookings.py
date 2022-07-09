from datetime import datetime
from bson import json_util
from flask import Blueprint, jsonify, make_response
from flask import Blueprint, request
from app import mongo
from app.utils.helper import *

bookings = Blueprint('bookings',__name__)

user_collection = mongo.db.users
parking_space_collection = mongo.db.parkingSpaces
bookings_collection = mongo.db.bookings

class Booking:
    def __init__(self,user,parking_space,selected_vehicle) -> None:
        self.bid = "B" + str(random_with_N_digits(8))
        self.uid = user.get('uid')
        self.pid = parking_space.get('pid')
        self.vehicle_name = selected_vehicle.get('company') + selected_vehicle.get('model')
        self.vehicle_registeration_no = selected_vehicle.get('registertioNo')
        self.amount_to_pay = parking_space.get('rent_per_hour')
        self.payment_status = "Pending"
        self.timestamp = datetime.now()
    
    def to_json(self):
        return {
            "bid": self.bid,
            "uid": self.uid,
            "pid": self.pid,
            "vehicle_name": self.vehicle_name,
            "amount_to_pay": self.amount_to_pay,
            "payment_status": self.payment_status,
            "timestamp": str(self.timestamp)
        }

@bookings.route('/makeBooking', methods=['POST'])
def makeBooking():
    if not request.is_json:
        return make_response("Missing JSON in request", 400)
    
    payload = request.json  
    
    params = ['uid','listingInfo','selectedVehicle']
    for param in params:
        if not param in payload.keys():
            return jsonify(msg="Missing {}".format(param), success=False), 400
    
    user = user_collection.find_one({"uid":payload.get('uid')})
    if not user:
        return jsonify(msg="User not found", success=False),400
    
    parking_space = parking_space_collection.find_one({"pid":payload.get('listingInfo').get('pid')})
    if not parking_space:
        return jsonify(msg="Invalid pid", success=False),400
    
    booking = Booking(user,parking_space,payload.get('selectedVehicle'))

    bookings_collection.insert_one(booking.to_json())
    
    return jsonify(msg="successfully booked",booking_info=booking.to_json(),success=True), 200