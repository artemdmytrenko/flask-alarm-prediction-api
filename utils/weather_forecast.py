import requests
import os, json
from pprint import pprint
from datetime import datetime, timedelta 
from sys import argv
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.environ['WEATHER_API_KEY']
BASE_URL = os.environ['WEATHER_API_URL']
unit_group = 'metric'


# Returns the weather forecast for the following 12 hours
def get_12hr_forecast(location: str) -> list:
    
    date_start = datetime.now().replace(minute=0, second=0)
    date_end = date_start + timedelta(hours=12)
    dt_format = '%Y-%m-%dT%H:%M:%S'
    date_start, date_end = date_start.strftime(dt_format), date_end.strftime(dt_format) 

    location_variants = {'Lviv': 'Львів, Україна',
                         'Sumy': 'Суми, Україна'}
    
    if location in location_variants.keys():
        location = location_variants[location]

    api_query = f'{BASE_URL}/{location}/{date_start}/{date_end}?unitGroup={unit_group}&key={API_KEY}&contentType=json'

    response = requests.request("GET", url=api_query)
    data = {}
    if response.status_code != 200:
        data = (f'{location}: Unexpected Error Code {response.status_code}')
    else: 
        data = strip_irrelevant_data(response.json(), date_start, date_end)
    return data


# Deletes the json entries outside of the relevant 12-hour forecast timeframe
def strip_irrelevant_data(data: dict, date_start: str, date_end: str) -> list:
    
    if len(data['days']) == 1:
        data = data['days'][0]['hours'][datetime.strptime(date_start, '%Y-%m-%dT%H:%M:%S').time().hour : datetime.strptime(date_end, '%Y-%m-%dT%H:%M:%S').time().hour]  
    else:
        data = data['days'][0]['hours'][datetime.strptime(date_start, '%Y-%m-%dT%H:%M:%S').time().hour :] + data['days'][1]['hours'][: datetime.strptime(date_end, '%Y-%m-%dT%H:%M:%S').time().hour] 
    
    return data


if __name__ == "__main__":
    for region in json.loads(os.environ['regions']):
        pprint(get_12hr_forecast(region))
    
   