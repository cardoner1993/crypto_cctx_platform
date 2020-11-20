import requests
from requests.exceptions import HTTPError
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt

from src import config_file
from src.utils.influxdb import InfluxDB
from src.utils.utils import build_request_url, load_config


def define_fear_greed_scope(history_format=False, start_date=None):
    if history_format and start_date is None:
        raise ValueError("If type history start date can't be None")
    elif history_format:
        if isinstance(start_date, str):
            start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
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


history_format = True
measurement = f"Fear_Greed_Index"
config = load_config(path=config_file.config_path, env='devel')
influx = InfluxDB(**config['influxdb'])
influx.create_database()

for url in ['https://api.alternative.me/fng/']:
    limit = define_fear_greed_scope(history_format=history_format, start_date="2019-10-10")
    # url = build_request_url(url, limit=limit, format='csv')
    url = build_request_url(url, limit=limit)
    dict_response = get_url_data(url)
    if dict_response is not None:
        response_df = pd.DataFrame.from_dict(dict_response['data'])
        response_df['timestamp'] = pd.to_datetime(response_df['timestamp'], unit='s')
        response_df['value'] = pd.to_numeric(response_df['value'])
        response_df = response_df.set_index('timestamp')
        # Upload the response_df to influxdb
        influx.load_dataframe(response_df, measurement, tags='', protocol='line')

        if history_format:
            fig = plt.figure(figsize=(20, 10))
            plt.plot(response_df['value'])
            fig.suptitle("Fear Greed Index", fontsize=20)
            plt.show()
