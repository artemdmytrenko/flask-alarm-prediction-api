from flask import Flask, jsonify, request
from datetime import datetime
from flask_cors import CORS
from apscheduler.schedulers.background import BackgroundScheduler
from pymongo import MongoClient
from utils.predict import predict_all
import os 
import json
import pytz
from dotenv import load_dotenv
from bson.json_util import dumps
from werkzeug.exceptions import Unauthorized


app = Flask(__name__)
cors = CORS(app)
cors.init_app(app)
load_dotenv()
API_TOKEN = os.environ['API_TOKEN']
regions = json.loads(os.environ['regions'])


URI = os.environ['MONGODB_URI']
client = MongoClient(URI, connect=False, connectTimeoutMS=5000, serverSelectionTimeoutMS=5000, tlsAllowInvalidCertificates=True)
db = client.get_database('alarms')
collection = db['hourly_predictions']


def schedule_predictions():
    prediction = predict_all()
    collection.insert_one(prediction)

scheduler = BackgroundScheduler()
scheduler.add_job(func=schedule_predictions, trigger='cron', minute=0)
scheduler.start()


@app.route("/")
def root():
    return f"<p>Go to <strong>/api/v1/alarms?location=(region name or 'all')</strong> for alarm predictions</p>"


@app.route("/api/v1/alarms", methods=['GET'])
def alarms_page():
    
    auth = request.headers.get('Authorization')
    
    if auth != API_TOKEN:
        raise Unauthorized()

    args = request.args 
    location = args.get('location')
    kyiv_time = pytz.timezone('Europe/Kiev')
    dt = datetime.now().astimezone(kyiv_time).replace(minute=0, second=0)
    format = '%m/%d/%Y, %H:%M:%S'

    cursor = collection.find_one({
        'last_prediction_time': dt.strftime(format)})
    
    if location == 'all':
        return dumps(cursor)
    elif location.capitalize() in regions:
        region_prediction = cursor['region_forecasts'][location]

        return dumps({
            'last_model_train_time': '04/23/2023, 05:45:31',
            'last_prediction_time': dt.strftime(format),
            location: region_prediction})
    else: 
        return jsonify({'Response Status Code': 400,
                'Error Message': 'Bad Request'})

if __name__ == '__main__':
    app.run(ssl_context='adhoc')
