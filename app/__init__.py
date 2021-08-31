from flask import Flask
from flask_jwt_extended import JWTManager
from flask_pymongo import PyMongo
from dotenv import load_dotenv
from datetime import timedelta
import os

load_dotenv()

app = Flask(__name__)
app.config["MONGO_URI"] = os.getenv('MONGO_URI')
app.config["JWT_SECRET_KEY"] = 'secretkey'
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(minutes=30)
jwt = JWTManager(app)
mongo = PyMongo(app)


from .users.users import user
from .vehicle.vehicle import vehicle

app.register_blueprint(user)
app.register_blueprint(vehicle)

from app import routes