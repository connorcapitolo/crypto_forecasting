import os
import time
import pandas as pd
import numpy as np
#from connect_rds import RDS
from binance import AsyncClient, BinanceSocketManager
import asyncio
from binance.client import Client
from binance import ThreadedWebsocketManager
from binance.enums import *
#from _env import api_key, api_secret, major_coins
from _test.api import API

major_coins = ['BTC', 'ETH', 'BNB', 'USDT', 'BUSD', 'USD']
api_secret = os.environ["BINANCE_SECRETS_KEY"]
api_key = os.environ["BINANCE_API_KEY"]


class WebsocketCoinMultiple:

    def __init__(self, only_close=True, coins=None, data='kline', update_frequency='1m',
                 frequency_data_update='1m'):
        if coins is None:
            coins = ['BTCUSDT']
        self.coins = coins
        self.data_type = data
        self.update_frequency = update_frequency
        self.only_close = only_close
        # verify and timeout: what do we want to do about it ?
        self.binance_client = Client(api_key, api_secret)
        self.bm = None
        self.ms = None
        self.streams = None
        self.RDSs = None
        self.managerRun = False
        self.correspondence = None
        self.extracted_candles = {}
        self.frequency_data_update = frequency_data_update

    def initialize_streams(self):
        """For every pair, we check if it is the (pair1, pair2) listed on pairs of exchanges or the other way
        around, ie BNBBTC or BTCBNB. Need to review this in order to ahve a one-to-one mapping between the
        coin and the stream for a specific datatype"""

        coins_market = API().access_all_coins()
        reversed_coins = []
        initial = len(self.coins)
        if type(self.coins) != list:
            self.coins = [self.coins]
        for coin in self.coins:
            for major_coin in major_coins:
                if major_coin in coin:
                    coin_modif = coin.replace(major_coin, '')
                    if coin.startswith(coin_modif):
                        reversed_coin = major_coin + coin_modif
                    else:
                        reversed_coin = coin_modif + major_coin
                    reversed_coins.append(reversed_coin)
                    break

        self.coins += reversed_coins
        self.coins = list(set(self.coins).intersection(coins_market))[:initial]
        self.streams = [
            '{}@{}_{}'.format(coin.lower(), self.data_type, self.update_frequency) for coin in self.coins]

    def initialize_RDS(self):
        """This function is going to initialize one RDS per different coin. We will also initialize the
        different streams for the different RDSs in order to be able to efficiently push information to
        the right tables"""
        if self.streams is None:
            self.initialize_streams()

        self.RDSs = {}
        for coin in self.coins:  # we will create connections to different databases in RDS for every coin
            rds = RDS(coin)
            self.RDSs[coin] = rds
            self.RDSs[coin].create_database()

    def write(self):

        if all([len(v) for (k, v) in self.extracted_candles.items()]):  # frequency update 1
            for i, coin in enumerate(self.coins):
                candles_coin = self.extracted_candles.get(coin.lower())
                df_coin = pd.concat(candles_coin)
                print("shape:", df_coin.shape)
                print(df_coin.head())
                # try:
                #     name_table = self.streams[i].replace('@', '_')
                #     # df_coin['stream'] = name_table # removed bc inconsistencies with historical data
                #     self.RDSs[coin.upper()].add_dataset(
                #         name_datatable=name_table, df=df_coin)
                #     self.extracted_candles[coin.lower()] = []
                # except ValueError:
                #     raise ValueError('Pair not yet hosted on the database')

    def startService(self):

        if self.bm is None:
            self.bm = ThreadedWebsocketManager(
                api_key=api_key, api_secret=api_secret)
            self.bm.start()

        if self.streams is None:
            self.initialize_streams()

        # if self.RDSs is None:
        #     self.initialize_RDS()

        def on_message(message):
            preprocess_message(message)

        def preprocess_message(message):
            """We have a different structure here since the multi stream yields a different organization
            of the data in the output JSON."""

            stream = message.get('stream')
            coin = stream.split('@')[0]
            if coin not in self.extracted_candles:
                self.extracted_candles[coin] = []
            message = message.get('data')
            information_kline = message.get('k')
            is_candle_closed = information_kline.get('x')
            if is_candle_closed:
                df = pd.DataFrame({
                    'Open Time': [information_kline.get('t')],
                    'Open Price': [information_kline.get('o')],
                    'High price': [information_kline.get('h')],
                    'Low Price': [information_kline.get('l')],
                    'Close Price': [information_kline.get('c')],
                    'Volume Traded': [information_kline.get('v')],
                    'Close Time': [information_kline.get('T')],
                    'Quote asset Volume': [information_kline.get('q')],
                    'Number of Trades': [information_kline.get('n')],
                    'Taker buy base asset volume': [information_kline.get('V')],
                    'Taker buy quote asset volume': [information_kline.get('Q')],
                    'NA': [np.nan]})
                self.extracted_candles[coin].append(df)
                self.write()

        print(' We will be extracting data for the following streams {}'.format(
            self.streams))
        self.bm.start_multiplex_socket(
            streams=self.streams, callback=on_message)
        self.bm.join()

        return self.extracted_candles


if __name__ == '__main__':
    multiple_websocket = WebsocketCoinMultiple(coins=['BTCUSDT', 'BTCBNB'])
    multiple_websocket.startService()
