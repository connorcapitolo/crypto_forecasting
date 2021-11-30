import os
import traceback
import asyncio
import functools
import multiprocessing
from queue import Queue
from binance import ThreadedWebsocketManager

import dataaccess.session as database_session
from dataaccess import symbols as dataaccess_symbols
from dataaccess import price_history as dataaccess_price_history
from run_historical import fetch_price_history

api_secret = os.environ["BINANCE_SECRETS_KEY"]
api_key = os.environ["BINANCE_API_KEY"]
NUM_PROCESSES = multiprocessing.cpu_count() - 1


# Execute with: python -m worker.service2

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
        self.symbol2id = {}
        # Initial queue
        self.live_stream_data_queue = Queue(0)
        self.processor = multiprocessing.Pool(NUM_PROCESSES)
        self.twm = ThreadedWebsocketManager(
            api_key=api_key, api_secret=api_secret)
        self.streams = []
        self.stream_name = ""
        # Initialise twm internal loop
        self.twm.start()

    def fetch_online(self, streams):

        def handle_socket_message(message):

            # print(msg)
            # Save the data
            # check if candle or top of the book data
            data = message["data"]
            information_kline = data.get('k')
            is_candle_closed = information_kline.get('x')
            if is_candle_closed == True:
                print('Candle Closed Data', data)
                symbol = information_kline.get('s')
                price_history_dict = {
                    'symbol_id': self.symbol2id[symbol],
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
                print(price_history_dict)

                # Save data to database
                # save_price_online(price_history_dict)
                # res = self.processor.apply_async(
                #     save_price_online, (price_history_dict),)
                # print("Pool Result:", res)

                # Put the online data into queue to be saved
                self.live_stream_data_queue.put(price_history_dict)

        #streams = ['bnbbtc@kline_1m']
        print("streams:", streams)
        self.stream_name = self.twm.start_multiplex_socket(
            callback=handle_socket_message, streams=streams)
        print("Stream Name:", self.stream_name)

        # Join the main thread
        # self.twm.join()

    def restart_online(self, streams):

        if self.stream_name != "":
            self.twm.stop()

        self.fetch_online(streams=streams)

    async def save_price_online(self):
        while self.live_stream_data_queue.empty() == False:
            price_history_dict = self.live_stream_data_queue.get()

            symbol_id = price_history_dict["symbol_id"]
            timestamp_end = price_history_dict["close_time"]

            # Save the data
            await dataaccess_price_history.create(**price_history_dict)

            # Update the endtimestamp to db
            await dataaccess_symbols.update(id=symbol_id, timestamp=timestamp_end)

    async def run(self):
        print("Running")
        # Connect to database
        await database_session.connect()

        try:
            def history_callback(result):
                print("history_callback results:", result)
                symbol_id = result["symbol_id"]
                status = result["status"]
                if status == "success":
                    self.history_stream[symbol_id]["current_status"] = "completed"
                else:
                    # The hostory process errored out, so we need ot restart the process
                    self.history_stream[symbol_id]["current_status"] = "created"
                    self.symbols[symbol_id]["current_status"] = "created"

            # Run the symbols retrive and check for historcal/live pull endlessley
            while True:
                # Get symbols from database
                # Run this loop so if any new symbol is added we pick it up
                symbols = await dataaccess_symbols.browse(paginate=False)
                print("Symbols:", symbols)

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

                    # Set symbol to id
                    self.symbol2id[symbol["name"]] = symbol["id"]

                # Iterate through the symbol list to fetch history and make sure
                # All symbols have price history up to data
                for id, symbol in self.symbols.items():

                    # Fetch history
                    # First we need to pull historical data since we were down to catch up
                    if symbol["current_status"] == "created":
                        print("Fetching history for", symbol)
                        symbol["current_status"] = "running"

                        # Call fetch_price_history in a separate process
                        res = self.processor.apply_async(
                            fetch_price_history, (symbol["name"], id, symbol["timestamp"],), callback=history_callback)
                        print("Pool Result:", res)
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

                print("Live stream:", self.live_stream)
                print("History stream:", self.history_stream)
                print("Symbols:", self.symbols)

                # Update live stream : Call Live stream here
                restart_streams = False
                for id, symbol in self.symbols.items():
                    if symbol["current_status"] == "live":
                        self.streams.append(symbol["name"].lower()+"@kline_1m")
                        symbol["current_status"] = "stream"
                        restart_streams = True

                if restart_streams:
                    print("Start/Restart Live stream...")
                    # res = self.processor.apply_async(
                    #     self.restart_online(streams=self.streams))
                    self.restart_online(streams=self.streams)

                # Save any pending live stream data
                await self.save_price_online()

                # Wait
                await asyncio.sleep(30)
        except:
            print("=========================")
            print("Error in App.. Exiting...")
            print(traceback.format_exc())

        # Disconnect from database
        await database_session.disconnect()


# Worker Service
app = App()

# Note: worker must be run as module, not script
# Catch all errors and log them
try:
    print("Starting Worker Service with NUM_PROCESSES:", NUM_PROCESSES)

    # Run the app
    asyncio.run(app.run())

except:
    print(traceback.format_exc())
