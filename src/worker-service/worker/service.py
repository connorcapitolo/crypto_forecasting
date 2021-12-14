import os
import traceback
import asyncio
import functools
import multiprocessing
from binance import ThreadedWebsocketManager

import binance # you'll modify these dependencies
from run_online import run_online_wrapper

import dataaccess.session as database_session
from dataaccess import symbols as dataaccess_symbols
from datacollector.api import API
from run_historical import fetch_price_history

NUM_PROCESSES = multiprocessing.cpu_count() - 1



class App:
    """
    App Worker class.
    """

    def __init__(self):
        """
        Args:
        """
        self.symbols = {}
        self.current_symbols = []
        self.history_stream = {}
        self.live_stream = {}
        self.history_processor = multiprocessing.Pool(NUM_PROCESSES)

        # self.api = API()
        # self.bm = ThreadedWebsocketManager(
        #     api_key=self.api.api_key, api_secret=self.api.api_secret)

        self.run_live=False
        self.processor = multiprocessing.Pool(NUM_PROCESSES)

    async def run(self):
        print("Running")
        # Connect to database

        await database_session.connect()
        # symbol_db = await dataaccess_symbols.create(name='BNBUSDT')  # just to reproduce what would happen on the api side, run only once
        current_symbols = await(dataaccess_symbols.browse(paginate=False))
        self.symbols = {s['id']: s for s in current_symbols}
        
        def online_callback(result):
            print("online_callback")
            print(result)


        try:
            def history_callback(result):
                print("history_callback")
                print(result)
                self.history_stream[result]["current_status"] = "completed"

            while True:
                # Get symbols from database
                symbols = await dataaccess_symbols.browse(paginate=False)
                #print("Symbols in the database:", symbols)
                #print('vs current symbols:', self.current_symbols)

                # Add the symbols to the local list
                for symbol in symbols:
                    if symbol["id"] not in self.symbols:
                        # a symbol is in the symbols db but not yet in our current queue
                        symbol["current_status"] = "created"
                        self.symbols[symbol["id"]] = symbol

                        # Add symbols to history fetch queue
                        self.history_stream[symbol["id"]] = symbol
                    else:
                        
                        # self.symbols[symbol["id"]]["timestamp"] = symbol["timestamp"]
                        self.symbols[symbol["id"]]["timestamp"] = binance.client.convert_ts_str('now UTC') 
                        if 'current_status' not in symbol:
                            self.symbols[symbol["id"]]['current_status'] = "completed" # to fix, status _tofix
                
                for id, symbol in self.symbols.items():

                    # Fetch history
                    # First we need to pull historical data since we were down to catch up
                    # then, how are we going to _fix, we could add those with the timestamp if they were already here ? 
                    if symbol["current_status"] == "created":
                        print("Fetching history for", symbol)
                        symbol["current_status"] = "running"

                        # Call fetch_price_history in a separate process
                        res = self.history_processor.apply_async(
                            fetch_price_history, (symbol["name"], id, symbol["timestamp"],), callback=history_callback)
                        symbol["status"] = 1
                        # this means we are currently updating it
                        await dataaccess_symbols.update(id=id, status=1)

                    elif symbol["current_status"] == "completed":

                        await dataaccess_symbols.update(id=id, status=2)
                        # Remove item from history
                        if id in self.history_stream:
                            self.history_stream.pop(id)

                        # Since we are all caught up, go to live stream now
                        symbol["current_status"] = "live"
                        symbol["status"] = 2
                        # Add symbols to live stream
                        self.live_stream[id] = symbol

                # Update live stream : Call FetchingManager(...) here

                if self.run_live == False:
                    # only need to fork once the live fetching
                    print("Live stream:", self.live_stream)
                    self.run_live = True
                    res = self.processor.apply_async(run_online_wrapper, (), callback=online_callback)
                
                print("History stream:", self.history_stream)
                print("Symbols:", self.symbols)

                # Wait
                await asyncio.sleep(30)
        except:
            print(traceback.format_exc())  # print the error message, to do when you do not know which type of exception is thrown

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
