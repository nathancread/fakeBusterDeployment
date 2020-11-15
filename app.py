from flask import Flask, request, Response, jsonify
from flask_cors import CORS
from datetime import datetime
import os

##TODO
    #firebase setup
    #heroku setup

# Initialize the Flask application
app = Flask(__name__)
CORS(app)



@app.route('/test', methods=['GET'])
def test():
    return jsonify({"success": True}), 200

#start flask app
if __name__ == '__main__':
    app.run()
#host="localhost", port=5000
