import schedule
import logging
import time

from src.exchange_pairs import run_exchange
from src.fear_greed_index import run_fear_greed

logging.basicConfig(filename='info.log', level=logging.DEBUG,
                    format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

url = 'https://api.alternative.me/fng/'
measurement = "Fear_Greed_Index"
start_time = "2010-01-01T00:00:00Z"
exchange_name = 'bitfinex'
trading_pair = 'BTC/USDT'

schedule.every().hour.do(run_exchange, exchange_name, trading_pair, start_time, time_block='1d')
schedule.every().hour.do(run_fear_greed, url, measurement, history_format=True, start_date=start_time)

while True:
    logging.info("Running pending events")
    schedule.run_pending()
    time.sleep(1)
