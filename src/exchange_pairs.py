# https://backtest-rookies.com/2018/03/08/download-cryptocurrency-data-with-ccxt/
# https://github.com/ccxt/ccxt/wiki
# https://buildmedia.readthedocs.org/media/pdf/ccxt/stable/ccxt.pdf

# Quandl API Key Rrt35dVRtnGjpZBJ3gFN

import ccxt
from datetime import datetime
import pandas as pd

# binance = ccxt.binance()
from src import config_file
from src.utils.influxdb import InfluxDB
from src.utils.utils import get_obs_in_time_range, load_config

# quandl.ApiConfig.api_key = "Rrt35dVRtnGjpZBJ3gFN"
# quandl.get_table('ZACKS/FC', per_end_date='2018-09-30', ticker='AAPL')

trading_pair = 'BTC/USDT'
exchange_name = 'bitfinex'  # 'bitfinex' 'binance'
start_time = "2010-01-01T00:00:00Z"
time_block = '1d'


def get_exchange(name):
    print(f"The name of the echange is {name}")
    if name in ccxt.exchanges:
        if hasattr(ccxt, name):
            return getattr(ccxt, name)()


def check_avail_echange():
    print(f"The avaiable echanges are:")
    for exchange in ccxt.exchanges:
        print(f"Exchange name: {exchange}")


def load_markets(exchange):
    print("The available market pairs are:\n")
    for item in list(exchange.load_markets().keys()):
        print(f"Pair {item}")


def check_if_pair_available(exchange, trading_pair):
    if trading_pair in list(exchange.load_markets().keys()):
        print(f"Pair {trading_pair} available")
        return True
    else:
        return False


def check_info_of_pair(exchange, trading_pair):
    print("Exchange pair info:\n")
    for key, value in exchange.markets[trading_pair].items():
        print(f" key: {key}, values: {value}")


def prepare_candles_df(candles):
    dates, open_data, high_data, low_data, close_data, volume = [], [], [], [], [], []
    for candle in candles:
        dates.append(datetime.fromtimestamp(candle[0] / 1000.0))
        open_data.append(candle[1])
        high_data.append(candle[2])
        low_data.append(candle[3])
        close_data.append(candle[4])
        volume.append(candle[5])
    candles_df = pd.DataFrame(zip(dates, open_data, high_data, low_data, close_data, volume),
                              columns=['dates', 'open_data', 'high_data', 'low_data', 'close_data', 'volume'])
    return candles_df


def get_candles_data(exchange, pair, start_time, timeframe='1m', end_time=None):
    limit = get_obs_in_time_range(start_time, end=end_time, format=timeframe)
    since = exchange.parse8601(start_time)
    candles = exchange.fetch_ohlcv(pair, timeframe, since=since, limit=limit)
    candles_df = prepare_candles_df(candles)
    # Setting index to datetime
    candles_df = candles_df.set_index('dates')
    return candles_df


def get_orderbook_data(exchange, pair, limit=None):
    exchange.fetch_order_book(pair, limit=limit)


def fetch_price_tickers(exchange, pair):
    if exchange.has['fetchTicker']:
        print(exchange.fetch_ticker(pair))


def run_exchange(exchange_name, trading_pair, start_time, time_block):
    """
    Downloads traiding_pair for an exchange and inserts the result in the influx database.
    Parameters
    ----------
    exchange_name: str. Name of the exchange
    trading_pair: str. Traiding pair. Example BTC/USDT
    start_time: str
    time_block: str. Block time to read observations.

    Returns
    -------

    """
    pair_influx_name = trading_pair.replace("/", "_")
    measurement = f"Pair_{exchange_name}_{pair_influx_name}"
    config = load_config(path=config_file.config_path, env='devel')
    influx = InfluxDB(**config['influxdb'])
    influx.create_database()
    exchange = get_exchange(exchange_name)
    if check_if_pair_available(exchange, trading_pair):
        if influx.measurement_exists(measurement):
            start_time = influx.get_last_time_measurement(measurement)
            candle_df = get_candles_data(exchange, trading_pair, start_time=start_time, timeframe=time_block)
        else:
            candle_df = get_candles_data(exchange, trading_pair, start_time=start_time, timeframe=time_block)
        if not candle_df.empty:
            print(f"Upload data to influxdb measurement {measurement}")
            influx.load_dataframe(candle_df, measurement, tags='', protocol='line')
        else:
            print("Data is up to date. Continue to next pair")
    else:
        print(f"The pair {trading_pair} is not available. Try changing the exchange")


if __name__ == '__main__':
    print(f"Start reading data for {exchange_name} and pair {trading_pair} at {datetime.utcnow()}")
    run_exchange(exchange_name, trading_pair, start_time, time_block)
    # get_orderbook_data(exchange, trading_pair, limit=None)
    # fetch_price_tickers(exchange, trading_pair)
