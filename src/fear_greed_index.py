import requests
from requests.exceptions import HTTPError
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt

from src import config_file
from src.utils.influxdb import InfluxDB
from src.utils.utils import build_request_url, load_config, parsing_dtime, parsing_dtime_options


def define_fear_greed_scope(history_format=False, start_date=None):
    if history_format and start_date is None:
        raise ValueError("If type history start date can't be None")
    elif history_format:
        if isinstance(start_date, str):
            start_date = parsing_dtime(start_date, parsing_dtime_options).date()
        limit = (datetime.utcnow().date() - start_date).days
    else:
        limit = 1
    return limit


def get_url_data(url):
    try:
        response = requests.get(url)
        # If the response was successful, no Exception will be raised
        response.raise_for_status()
        dict_response = response.json()
        return dict_response
    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')
        return None
    except Exception as err:
        print(f'Other error occurred: {err}')
        return None


def run_fear_greed(url, measurement, history_format, start_date):
    print(f"Start process for {measurement}")
    if influx.measurement_exists(measurement):
        start_date = influx.get_last_time_measurement(measurement)
        limit = define_fear_greed_scope(history_format=history_format, start_date=start_date)
    else:
        limit = define_fear_greed_scope(history_format=history_format, start_date=start_date)
    # url = build_request_url(url, limit=limit, format='csv')
    if limit == 0:
        print("Data is up to date for Fear and Greed index")
    else:
        print("Getting and inserting Fear and Greed index into influxdb")
        url_request = build_request_url(url, limit=limit)
        dict_response = get_url_data(url_request)
        if dict_response is not None:
            response_df = pd.DataFrame.from_dict(dict_response['data'])
            response_df['timestamp'] = pd.to_datetime(response_df['timestamp'], unit='s')
            response_df['value'] = pd.to_numeric(response_df['value'])
            response_df = response_df.set_index('timestamp')
            # Upload the response_df to influxdb
            influx.load_dataframe(response_df, measurement, tag_columns=['value_classification'], protocol='line')


start_date = "2010-01-01"
history_format = True
measurement = f"Fear_Greed_Index"
config = load_config(path=config_file.config_path, env='devel')
influx = InfluxDB(**config['influxdb'])
influx.create_database()

if __name__ == '__main__':
    for url in ['https://api.alternative.me/fng/']:
        run_fear_greed(url, measurement, history_format, start_date)
