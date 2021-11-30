import os
import asyncio
from celery.utils.log import get_task_logger

import binance
from binance import ThreadedWebsocketManager
from typing import Optional, List, Dict, Callable, Any, Awaitable

from datacollector.session import worker, async_task
from dataaccess import symbols as dataaccess_symbols
from dataaccess import price_history as dataaccess_price_history
from datacollector.api import API


major_coins = ['BTC', 'ETH', 'BNB', 'USDT', 'BUSD', 'USD']
price_history_queue = []


class WebsocketCoinMultiple:

    def __init__(self, data='kline', update_frequency='1m',
                 frequency_data_update='1m'):
        self.api = API()
        self.streams = []
        self.streams2symbols = {}

        self.data_type = data
        self.update_frequency = update_frequency
        self.frequency_data_update = frequency_data_update

        self.bm = ThreadedWebsocketManager(
            api_key=self.api.api_key, api_secret=self.api.api_secret)
        self.bm.start()

    async def build_streams(self, symbols):
        """For every pair, we check if it is the (pair1, pair2) listed on pairs of exchanges or the other way
        around, ie BNBBTC or BTCBNB. Need to review this in order to ahve a one-to-one mapping between the
        coin and the stream for a specific datatype"""

        coins_market = self.api._access_all_coins()
        reversed_coins = []
        initial = len(symbols)
        coins = [symbol["name"] for symbol in symbols]

        print('Will get streams for ', coins)

        for coin in coins:
            for major_coin in major_coins:
                if major_coin in coin:
                    print(coin, major_coin)
                    coin_modif = coin.replace(major_coin, '')
                    if coin.startswith(coin_modif):
                        reversed_coin = major_coin + coin_modif
                    else:
                        reversed_coin = coin_modif + major_coin
                    reversed_coins.append(reversed_coin)
                    break

        coins += reversed_coins
        coins = list(set(coins).intersection(coins_market))[:initial]

        for coin in coins:
            stream = '{}@{}_{}'.format(coin.lower(),
                                       self.data_type, self.update_frequency)
            self.streams2symbols[stream] = coin
            self.streams.append(stream)

        return self.streams

    async def addStreams(self):
        
        def on_message(message):
            # Save the data
            data = message["data"]
            information_kline = data.get('k')
            is_candle_closed = information_kline.get('x')
            if is_candle_closed == True:
                print('Writing', data)
                price_history_dict = {
                    "symbol_id": self.streams2symbols[message["stream"]]["id"],
                    'open_time': information_kline.get('t'),
                    'open_price': float(information_kline.get('o')),
                    'high_price': float(information_kline.get('h')),
                    'low_price': float(information_kline.get('l')),
                    'close_price': float(information_kline.get('c')),
                    'volume_traded': float(information_kline.get('v')),
                    'close_time': information_kline.get('T'),
                    'quote_asset_volume': float(information_kline.get('q')),
                    'number_of_trades': information_kline.get('n'),
                    'taker_buy_base_asset_volume': float(information_kline.get('V')),
                    'taker_buy_quote_asset_volume': float(information_kline.get('Q'))
                }

                save_price_history.delay(obj=price_history_dict)
        self.bm.start_multiplex_socket(
            streams=self.streams, callback=on_message)
        self.bm.join()

    def stopService(self):
        self.bm.close_all()
        self.bm.stop()


multiple_websocket = None


@async_task
async def start_multiple_websocket():
    global multiple_websocket

    if multiple_websocket is None:
        multiple_websocket = WebsocketCoinMultiple()

    # Build the streams from symbols from DB
    streams = []
    _symbols = await dataaccess_symbols.browse()
    await multiple_websocket.build_streams(_symbols)
    
    if len(multiple_websocket.streams) == 0:
        raise ValueError('No streams')

    _missing_data_symbols = await dataaccess_symbols.get_inconsistent_symbols()
    print('Inconsistencies for the following symbols {}'.format(_missing_data_symbols))

    #await fix(_missing_data_symbols)
    await multiple_websocket.addStreams()

@async_task
async def add_streams():
    global multiple_websocket

    if multiple_websocket is None:
        multiple_websocket = WebsocketCoinMultiple()

    # Build the streams from symbols from DB
    streams = []
    symbols = await dataaccess_symbols.browse()
    print("symbols:", symbols)

    streams = await multiple_websocket.build_streams(symbols)
    print("streams:", streams)
    await multiple_websocket.addStreams(streams)


@async_task
async def save_price_history(obj):
    print(obj)
    await dataaccess_symbols.update(id=obj['symbol_id'])
    await dataaccess_price_history.create(**obj)


@async_task
async def stop_multiple_websocket():
    print("stop_multiple_websocket")
    global multiple_websocket

    if multiple_websocket is not None:
        multiple_websocket.stopService()

@async_task
async def _fix(inconsistent_symbols):
    raise NotImplementedError


@async_task
async def load_price_history(symbol, symbol_id, timestamp=None):
    print("load_price_history")

    api = API()

    if timestamp is None:
        timestamp = api.client._get_earliest_valid_timestamp(
            symbol=symbol, interval='1m')
        timestamp_end = timestamp 
        while timestamp_end < binance.client.convert_ts_str('now UTC'):
            timestamp_end += 60000 * 1000
            print('end fetch', timestamp_end)
            bars = api.query_data_for_long_time(
                pair=symbol, frequency='1m', start_timestamp=timestamp, end_timestamp=timestamp_end, verbose=False)

            for bar in bars:
                price_history_dict = {
                    "symbol_id": symbol_id,
                    'open_time': bar[0],
                    'open_price': float(bar[1]),
                    'high_price': float(bar[2]),
                    'low_price': float(bar[3]),
                    'close_price': float(bar[4]),
                    'volume_traded': float(bar[5]),
                    'close_time': bar[6],
                    'quote_asset_volume': float(bar[7]),
                    'number_of_trades': bar[8],
                    'taker_buy_base_asset_volume': float(bar[9]),
                    'taker_buy_quote_asset_volume': float(bar[10])
                }
                save_price_history.delay(obj=price_history_dict)

            timestamp = timestamp_end

    # Add new symbol to the stream
    add_streams()
