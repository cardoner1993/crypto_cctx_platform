# https://backtest-rookies.com/2018/03/08/download-cryptocurrency-data-with-ccxt/
# https://github.com/ccxt/ccxt/wiki

import ccxt
from datetime import datetime
import pandas as pd
import fire

# binance = ccxt.binance()
from utils.utils import check_if_timestamp_or_parse, get_obs_in_time_range

trading_pair = 'BTC/USD'
exchange_name = 'bitfinex'
start_time = "2020-01-01"


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
    dates, open_data, high_data, low_data, close_data = [], [], [], [], []
    for candle in candles:
        dates.append(datetime.fromtimestamp(candle[0] / 1000.0))
        open_data.append(candle[1])
        high_data.append(candle[2])
        low_data.append(candle[3])
        close_data.append(candle[4])
    candles_df = pd.DataFrame(zip(dates, open_data, high_data, low_data, close_data),
                              columns=['dates', 'open_data', 'high_data', 'low_data', 'close_data'])
    return candles_df


def get_candles_data(exchange, pair, timeframe='1m', start_time=None, end_time=None):
    limit = get_obs_in_time_range(start_time, end=end_time, format=timeframe)
    if start_time is not None:
        start_time = check_if_timestamp_or_parse(start_time)
    candles = exchange.fetch_ohlcv(pair, timeframe, since=start_time, limit=limit)
    candles_df = prepare_candles_df(candles)
    return candles_df


def get_orderbook_data(exchange, pair, limit=None):
    exchange.fetch_order_book(pair, limit=limit)


def fetch_price_tickers(exchange, pair):
    if exchange.has['fetchTicker']:
        print(exchange.fetch_ticker(pair))


if __name__ == '__main__':
    exchange = get_exchange(exchange_name)
    if check_if_pair_available(exchange, trading_pair):
        get_candles_data(exchange, trading_pair, timeframe='1h', start_time=start_time)
    # get_orderbook_data(exchange, trading_pair, limit=None)
    # fetch_price_tickers(exchange, trading_pair)
