import datetime as dt
import pandas as pd
import scipy.sparse as sp
import numpy as np
import pickle 
import requests
import json
import os
from dotenv import load_dotenv
from datetime import datetime, time
from bs4 import BeautifulSoup
from utils.csv_to_vec import csv_to_vec
from utils.weather_forecast import get_12hr_forecast
from utils.prepare_report import transform 

load_dotenv()

model = pickle.load(open(os.path.relpath(r'../models/2__passive_agressive_classifier__v2.pkl'), 'rb'))
tfidf_transformer = pickle.load(open(os.path.relpath(r'../models/tfidf_transformer.pkl'), 'rb'))
cv = pickle.load(open(os.path.relpath(r'../models/cv.pkl'), 'rb'))

def predict(loc: str):

    df_weather = pd.DataFrame(get_12hr_forecast(loc))

    exclude = {
        'datetime',
        'datetimeEpoch',
        'feelslike',
        'preciptype',
        'conditions',
        'solarenergy',
        'icon',
        'stations',
        'source',
    }

    exclude_2 = {
        'sunriseEpoch',
        'sunrise',
        'sunsetEpoch',
        'sunset',
        'moonphase',
    }

    df_time = df_weather['datetime']
    df_weather = df_weather.drop(columns=exclude)
    try:
        df_weather = df_weather.drop(columns=exclude_2)
    except KeyError:
        pass

    df_weather = df_weather.fillna(method='ffill')
    df_weather = sp.csr_matrix(df_weather.values.astype(float))

    delta = 1 if datetime.now().hour in range(12, 23) else 2
    report_date = dt.datetime.now() - dt.timedelta(days=delta)
    report_date = report_date.strftime('%B-%e-%Y').replace(' ', '').lower()

    base_url = 'https://www.understandingwar.org/backgrounder/russian-offensive-campaign-assessment'
    isw_data = requests.get(f'{base_url}-{report_date}').text

    soup = BeautifulSoup(isw_data, 'html.parser')
    report = transform(soup)

    cv_vector = cv.transform([report])
    tfidf_vector = tfidf_transformer.transform(cv_vector) 
    tfidf_mat = tfidf_vector
    for i in range(11):
        tfidf_mat = sp.vstack((tfidf_mat, tfidf_vector), format='csr')

    X = sp.hstack((df_weather, tfidf_mat), format='csr')        

    prediction = model.predict(X)
    endpoint = {}

    for i in range(12):
        time_obj = datetime.strptime(df_time.values[i], '%H:%M:%S')
        endpoint[str(time_obj.strftime('%I %p'))] = str(prediction[i])
    
    return endpoint


def predict_all():

    now = datetime.now().replace(minute=0, second=0)
    format = '%m/%d/%Y, %H:%M:%S'

    endpoint = {'last_model_train_time': '04/23/2023, 05:45:31',
                'last_prediction_time': now.strftime(format),
                'region_forecasts': {}
                }
    
    for region in json.loads(os.environ['regions']):
        prediction = predict(region)
        endpoint['region_forecasts'][region] = prediction
    
    return endpoint