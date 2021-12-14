import os
import traceback
import asyncio
import functools
import multiprocessing
from queue import Queue
import time
from binance import ThreadedWebsocketManager, client

import dataaccess.session as database_session
from dataaccess import symbols as dataaccess_symbols
from run_historical import fetch_price_history
from dataaccess import top_of_book as dataaccess_top_of_book
from dataaccess import price_history as dataaccess_price_history
from run_online import save_top_of_book, save_price_history
from collections import Mapping
from log_conf import Logger


api_secret = os.environ["BINANCE_SECRETS_KEY"]
# api_secret = "azp8fSpTRWcA0XQ56SCdIKU150Csi70VA77dks0t6au3GcDP4h5KWiwXA8pd3dHg"
# api_key = "XjnjQlvDeaZxjMeGrN3r8Sja7tnKftpGhnAcs6JA7Jw1ZnBte6ZyR8DkkbZ0zSmu"
api_key = os.environ["BINANCE_API_KEY"]
NUM_PROCESSES = multiprocessing.cpu_count() - 1  # 4
print("NUM_PROCESSES:", NUM_PROCESSES)
if NUM_PROCESSES == 0:
    NUM_PROCESSES = 1


class App:
    """
    App Worker class.
    """

    def __init__(self):
        """
        Args:
        """
        self.symbols = {}
        self.history_stream = {}
        self.live_stream = {}
        self.stream2id = {}
        self.symbol2id = {}
        self.respin = False
        self.live_stream_data_queue = Queue(0)
        self.processor = multiprocessing.Pool(NUM_PROCESSES)
        self.twm = ThreadedWebsocketManager(
            api_key=api_key, api_secret=api_secret)
        self.streams = []
        self.stream_name = ""
        # Initialise twm internal loop
        self.twm.start()

    def build_top_of_book(self):
        top_of_book_corr = {}
        for symbol_id in self.live_stream:
            top_of_book_corr[symbol_id] = []
        self.top_of_book = top_of_book_corr

    def fetch_online(self, streams):

        def handle_socket_message(message):

            try:
                _stream = message['stream']
                symbol_id = self.stream2id[_stream]

                if _stream.endswith('@bookTicker'):
                    data = message['data']
                    _top_of_book_dict = {
                        'best_bid': data.get('b'),
                        'volume_best_bid': data.get('B'),
                        'best_ask': data.get('a'),
                        'volume_best_ask': data.get('A')
                    }
                    self.top_of_book[symbol_id] = _top_of_book_dict

                else:
                    data = message["data"]
                    information_kline = data.get('k')
                    is_candle_closed = information_kline.get('x')

                    if is_candle_closed == True:
                        price_history_dict = {
                            'symbol_id': symbol_id,
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
                        Logger.logr.debug(
                            f'We are still fetching the top of the book {self.top_of_book}')
                        Logger.logr.debug(
                            f'We are still fetching the candle {price_history_dict}')

                        self.live_stream_data_queue.put(price_history_dict)
                        self.live_stream_data_queue.put(
                            self.top_of_book[symbol_id])

            except Exception as e:
                Logger.logr.error(e)
                Logger.logr.error("Exception OverFlow Error", exc_info=1)
                Logger.logr.info("Setting respin to True")
                self.respin = True
                _stream = ''

        Logger.logr.info(f"Starting online fetch with streams: {streams}")
        self.stream_name = self.twm.start_multiplex_socket(
            callback=handle_socket_message, streams=streams)
        Logger.logr.info(vars(self.twm))
        Logger.logr.info(f"Stream Name: {self.stream_name}")

        # Join the main thread
        # self.twm.join()

    def restart_online(self, streams):
        Logger.logr.info(self.stream_name)
        Logger.logr.info(vars(self.twm))

        if self.stream_name != "":
            self.twm.stop()
            self.twm = ThreadedWebsocketManager(api_key=api_key, api_secret=api_secret)
            time.sleep(5)
            self.twm.start()
            time.sleep(5)

        Logger.logr.info('Stopping and restarting the ThreadWebsocketManager')
        Logger.logr.info(vars(self.twm))
        self.build_top_of_book()
        self.fetch_online(streams=streams)

    async def save_price_online(self):
        l = []
        while self.live_stream_data_queue.empty() == False:
            l.append(self.live_stream_data_queue.get())

        seen = set()  # https://stackoverflow.com/questions/9427163/remove-duplicate-dict-in-list-in-python
        l_wo_duplicates = []
        for d in l:
            # https://stackoverflow.com/questions/25231989/how-to-check-if-a-variable-is-a-dictionary-in-python
            if isinstance(d, Mapping):
                t = tuple(d.items())
                if t not in seen:
                    seen.add(t)
                    l_wo_duplicates.append(d)

        for price_history_dict in l_wo_duplicates:
            try:
                symbol_id = price_history_dict["symbol_id"]
                timestamp_end = price_history_dict["close_time"]
                await dataaccess_price_history.create(**price_history_dict)
                await dataaccess_symbols.update(id=symbol_id, timestamp=timestamp_end)

            except:
                price_history_dict['symbol_id'] = symbol_id
                price_history_dict['time_reporting'] = timestamp_end
                await dataaccess_top_of_book.create(**price_history_dict)
                # await dataaccess_top_of_book.update(id=symbol_id, timestamp=timestamp_end)

    async def run(self):
        Logger.logr.info("Running")
        # Connect to database
        previous_streams = []
        await database_session.connect()
        result = await dataaccess_symbols.browse()

        if len(result) == 0:

            # in this spot, we are manually adding files to the database
            # be careful, as it can cause issues if you manually add more symbols than the number of worker processes
            # note that for debugging purposes, it's easiest to work with only two of the five symbols
            await dataaccess_symbols.create(name='BNBBTC')
            await dataaccess_symbols.create(name='BTCUSDT')
            await dataaccess_symbols.create(name='ETHBTC')
            await dataaccess_symbols.create(name='BNBUSDT')
            # await dataaccess_symbols.create(name='ETHUSDT')

        try:
            def history_callback(result):
                Logger.logr.info(f"history_callback: {result}")
                self.symbols[result['symbol_id']
                             ]["current_status"] = "completed"

            # Start Live Stream
            # print("Starting the Live stream")
            # streams = ['bnbbtc@kline_1m']
            # res = self.processor.apply_async(
            #     self.fetch_online(streams=streams))

            while True:
                # Get symbols from database
                # Run this loop so if any new symbol is added we pick it up
                symbols = await dataaccess_symbols.browse(paginate=False)

                # Add the symbols to the local list
                for symbol in symbols:
                    if symbol["id"] not in self.symbols:
                        symbol["current_status"] = "created"
                        self.symbols[symbol["id"]] = symbol

                        # Add symbols to history fetch queue
                        self.history_stream[symbol["id"]] = symbol
                    else:
                        # Update the timestamp the symbol was last updated/fetched
                        self.symbols[symbol["id"]
                                     ]["timestamp"] = symbol["timestamp"]
                    self.symbol2id[symbol["name"]] = symbol["id"]

                # Iterate through the symbol list to fetch history and make sure
                # All symbols have price history up to data
                for id, symbol in self.symbols.items():

                    # Fetch history
                    # First we need to pull historical data since we were down to catch up
                    if symbol["current_status"] == "created":
                        Logger.logr.info(f"Fetching history for {symbol}")
                        symbol["current_status"] = "running"

                        # Call fetch_price_history in a separate process
                        res = self.processor.apply_async(
                            fetch_price_history, (symbol["name"], id, symbol["timestamp"],), callback=history_callback)
                        symbol["status"] = 1
                        await dataaccess_symbols.update(id=id, status=1)

                    elif symbol["current_status"] == "completed":

                        await dataaccess_symbols.update(id=id, status=2)
                        # Remove item from history
                        self.history_stream.pop(id)

                        # Since we are all caught up, go to live stream now
                        symbol["current_status"] = "live"
                        symbol["status"] = 2
                        # Add symbols to live stream
                        self.live_stream[id] = symbol

                Logger.logr.debug(f"Live stream:, {self.live_stream}")
                Logger.logr.debug(f"History stream:, {self.history_stream}")
                Logger.logr.debug(f"Symbols:, {self.symbols}")

                # Update live stream : Call Live stream here
                streams = []
                for id, symbol in self.symbols.items():
                    if symbol["current_status"] == "live":
                        streams.append(symbol["name"].lower()+"@kline_1m")
                        streams.append(symbol["name"].lower()+"@bookTicker")
                        self.stream2id[symbol["name"].lower()+"@kline_1m"] = id
                        self.stream2id[symbol["name"].lower() +
                                       "@bookTicker"] = id
                        symbol["current_status"] = "stream"

                streams = set(streams + previous_streams)

                if len(streams) > len(previous_streams):  # new symbol was added
                    Logger.logr.info("Start/Restart Live stream...")
                    res = self.processor.apply_async(
                        self.restart_online(streams=streams))

                # for id, symbol in self.symbols.items():
                #     if symbol["current_status"] == "stream":  # running live
                #         # down
                #         # running live but timestamp hasn't been updated for 8 minutes, then we need to spin this up again and get price history
                #         if symbol["timestamp"] + 80000 < client.convert_ts_str('now UTC'):
                #             print('The process is down for', symbol)
                #             res = self.processor.apply_async(
                #                 fetch_price_history, (symbol["name"], id, symbol["timestamp"],), callback=history_callback)
                #             # self.respin = True

                if self.respin:
                    Logger.logr.info(
                        "The process was down, restart Live stream...")
                    res = self.processor.apply_async(
                        self.restart_online(streams=streams))

                    self.respin = False

                previous_streams = list(streams)

                await self.save_price_online()
                # Wait
                await asyncio.sleep(30)
        except:
            Logger.logr.error(
                "Exception has occured in the global loop", exc_info=1)

        # Disconnect from database
        await database_session.disconnect()


# Worker Service
app = App()

# Note: worker must be run as module, not script
# Catch all errors and log them
try:
    Logger.logr.info(
        f"Starting Worker Service with NUM_PROCESSES: {NUM_PROCESSES}")

    # Run the app
    asyncio.run(app.run())

except:
    print(traceback.format_exc())
