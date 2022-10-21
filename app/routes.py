from app import app
from flask import request, jsonify, make_response

@app.route("/")
def index():
    return "Hello World"
