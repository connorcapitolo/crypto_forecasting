#!/usr/bin/env python

# Libraries Import
from binance import client
from binance.client import Client
from time import sleep
import ssl
import time
import pandas as pd

from binance import ThreadedWebsocketManager

# Variables definition

api_key = 'RLis1zPSdrqFz1uP28k9aJlhElR9lJnynaCldpSNeob2PrnhnoMiGAA7drlZdpC4'
api_secret = 'hplmjruPIXcHAQSC6F4OUPwoJvXfwjTeAeqJQiKAh7xAQC9QbZSo0y3yCI4gtbOH'


def example_query_account():
    '''still not working, probably since we don't have any transactions'''
    client = Client(api_key, api_secret)
    info = client.get_account()
    permissions = info['permissions']
    balances = info['balances']

    print(info, permissions, balances)

    btc_price = client.get_symbol_ticker(symbol="BTCUSDT")
    print(btc_price['price'])


btc_price = {'error': False}


def btc_trade_history(msg):
    ''' define how to process incoming WebSocket messages '''
    print(msg)
    if msg['e'] != 'error':
        print(msg['c'])
        btc_price['last'] = msg['c']
        btc_price['bid'] = msg['b']
        btc_price['last'] = msg['a']
        btc_price['error'] = False
    else:
        btc_price['error'] = True


def example_web_socket():
    bsm = ThreadedWebsocketManager()
    bsm.start()
    bsm.start_symbol_ticker_socket(callback=btc_trade_history, symbol='BTCUSDT')
    sleep(10)
    bsm.stop()


def time_wrapper(f):
    start = time.time()
    f()
    print('Total time', time.time() - start)


def access_all_market():
    '''Obtaining of list of dictionaries for each of the 1642 coins on Binance; a dictionary is comprised of a symbol and price e.g. {'symbol': 'ETHBTC', 'price': '0.07427400'}
    '''
    client = Client(api_key, api_secret)
    prices = client.get_all_tickers()
    return prices


def order_book(coin='BTCUSDT', limit=5000):
    '''Provides a dictionary comprised of the keys 'lastUpdateID', 'bids' and 'asks' e.g. {'lastUpdateId': 13693909970, 'bids': [['47047.05000000', '0.96392000'], ['47045.62000000', '0.01432000'], ['47044.69000000', '0.03617000'], ['47044.05000000', '0.04296000'], ['47042.56000000', '0.37185000'], ['47042.55000000', '1.06245000'], ['47042.35000000', '0.00022000'], ['47041.13000000', '0.29406000'], ['47041.12000000', '0.84000000'], ['47039.99000000', '0.85948000']], 'asks': [['47047.06000000', '2.26652000'], ['47050.87000000', '0.02125000'], ['47051.00000000', '0.01060000'], ['47051.40000000', '0.04135000'], ['47052.78000000', '0.00022000'], ['47053.99000000', '0.02806000'], ['47054.00000000', '0.08000000'], ['47054.12000000', '0.01000000'], ['47054.94000000', '0.18917000'], ['47054.95000000', '0.13857000']]}'''
    client = Client(api_key, api_secret)
    depth = client.get_order_book(symbol=coin, limit=limit)
    print(depth)
    return depth


def query_data_for_long_time(coin='BTCUSDT', frequency='1w', request='candles'):
    '''
    Getting historical data for a certain coin based on a certain frequency level from the candles feature
    '''
    # error checking
    if frequency not in {'1m', '3m', '5m', '15m', '30m', '1h', '2h', '4h', '6h', '8h', '12h', '1d', '3d', '1w', '1M'}:
        raise AttributeError(
            'Invalid frequency, should be in {1m, 3m, 5m, 15m, 30m, 1h, 2h, 4h, 6h, 8h, 12h, 1d, 3d, 1w, 1M}')
    if request not in {'candles'}:
        raise AttributeError('Invalid request, should be in {candles}')
    
    client = Client(api_key, api_secret)
    timestamp = client._get_earliest_valid_timestamp(symbol='BTCUSDT', interval=frequency)
    # actual_timestamp = pd.to_timestamp() timestamp - client._get_earliest_valid_timestamp(symbol='BTCUSDT', interval=frequency)
    print('Querying {} data from _____ until present time, with a frequency update of {}'.format(request, frequency))
    if request == 'candles':
        columns = ['Open Time', 'Open Price', 'High price', 'Low Price', 'Close Price', 'Volume Traded', 'Close Time',
                   'Quote asset Volume',
                   'Number of Trades', 'Taker buy base asset volume', 'Taker buy quote asset volume', 'NA']
        start = time.time()
        bars = client.get_historical_klines(coin, frequency, timestamp, limit=1000)  # we get data from Aug 15 2017
        print('Fetched {} lines of data in {} seconds'.format(len(bars), time.time() - start))
        df = pd.DataFrame(bars, columns=columns)
    return df


if __name__ == '__main__':
    print('Executing Script:')
    # dict = order_book()
    # print(len(dict.get('bids')), dict.keys())
    # access_all_market()
    # df = query_data_for_long_time(frequency='6h')
    # print(df.memory_usage().sum())
    # print(df.head())
    # print(len(access_all_market())) # 1642
    # print(access_all_market()[0])
    # order_book(limit=10)
    

