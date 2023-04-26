from flask import Flask, jsonify, request
from datetime import datetime
from flask_cors import CORS
from apscheduler.schedulers.background import BackgroundScheduler
from pymongo import MongoClient
from utils.predict import predict_all
import os 
import json
from dotenv import load_dotenv
from bson.json_util import dumps


app = Flask(__name__)
cors = CORS(app)

load_dotenv()
regions = json.loads(os.environ['regions'])


URI = os.environ['MONGODB_URI']
client = MongoClient(URI, tlsAllowInvalidCertificates=True)
db = client.get_database('alarms')
collection = db['hourly_predictions']


def schedule_predictions():
    prediction = predict_all()
    collection.insert_one(prediction)

scheduler = BackgroundScheduler()
scheduler.add_job(func=schedule_predictions, trigger='cron', minute=0)
scheduler.start()


@app.route("/api/v1/alarms", methods=['GET'])
def alarms_page():
    args = request.args 
    location = args.get('location')
    dt = datetime.now().replace(minute=0, second=0)
    format = '%m/%d/%Y, %H:%M:%S'

    cursor = collection.find_one({
        'last_prediction_time': dt.strftime(format)})
    
    if location == 'all':
        return dumps(cursor)
    elif location in regions:
        region_prediction = cursor['region_forecasts'][location]

        return dumps({
            'last_model_train_time': '04/23/2023, 05:45:31',
            'last_prediction_time': dt.strftime(format),
            location: region_prediction})
    else: 
        return jsonify({'Response Status Code': 400,
                'Error Message': 'Bad Request'})



if __name__ == '__main__':
    cors.init_app(app)
    app.run(debug=False, use_reloader=False)
