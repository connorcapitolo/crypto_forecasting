""" 
The question that remains is the way we are going to interact this online fetching with the historical fetching. 
Right now, the online fetching is being executed and we found a way to monitor the symbols database. 
"""

from datacollector.extract_data import WebsocketCoinMultiple
from dataaccess import symbols as dataaccess_symbols
from dataaccess import price_history as dataaccess_price_history
from datacollector import extract_data
from datacollector.api import API
import dataaccess.session as database
import binance
from syncer import sync
import asyncio
import nest_asyncio

nest_asyncio.apply()

################ OLD #################

class FetchingManager:

    def __init__(self, websocket: WebsocketCoinMultiple=None, symbols: list=None, lapse_checking: int=None):
        if websocket is None:
            websocket = WebsocketCoinMultiple()
        if lapse_checking is None:
            lapse_checking = 500 # we will check the symbol database for update every 30 seconds
        self.websocket = websocket
        self.global_counter = 0
        self.list_symbols = []
        self.update_frequency = lapse_checking
        self.startup = True


    def __str__(self):
        return 'Run Manager with the following symbols {}'.format(self.list_symbols)

    def build_top_of_book(self):
        top_of_book_corr = {}
        symbol_ids = self.websocket.streams2symbols.values()
        for symbol_id in symbol_ids:
            top_of_book_corr[symbol_id] = {}
        self.top_of_book = top_of_book_corr
    
    @sync
    async def monitor_online_fetch(self):
        print('Resetting')

        if self.startup is True:
            await database.connect()
            print('Startup')
            self.list_symbols = await dataaccess_symbols.browse()
            print('Working with', self.list_symbols)
            #_missing_data_symbols = asyncio.run(dataaccess_symbols.get_inconsistent_symbols(timestamp=binance.client.convert_ts_str('now UTC')))
            #asyncio.run(_fix(_missing_data_symbols))
            self.startup = False

        print('hh')
        _symbols = await (dataaccess_symbols.browse())
        print('hey')
        self.list_symbols = _symbols
        asyncio.run(self.websocket.build_streams(self.list_symbols))
        print('hey')
        self.build_top_of_book()
        print('hey2')
        self.launch_online_fetch()

    def launch_online_fetch(self):
        
        def on_message(message):
            # Save the data
            if self.global_counter == self.update_frequency:
                self.global_counter = -1
                print('Trying to reset')
                self.monitor_online_fetch()
            
            try:
                _stream = message['stream']
            except KeyError: # just a way to mention that there are Queue Overflow issues
                _stream = ''

            if _stream.endswith('@bookTicker'): # top of the book data
                # in order for it to be written at the same time
                # than the corresponding candle, we are going to store it
                # and write it when we write a candle
                data = message['data']
                symbol_id = self.websocket.streams2symbols[_stream.replace('bookTicker', 'kline_1m')]
                _top_of_book_dict = {
                    'best bid': data.get('b'),
                    'volume best bid': data.get('B'),
                    'best ask': data.get('a'),
                    'volume best ask': data.get('A')
                }
                self.top_of_book[symbol_id] = _top_of_book_dict

            elif 'kline' in _stream: # candle, aggregated data
                data = message["data"]
                information_kline = data.get('k')
                symbol_id = self.websocket.streams2symbols[_stream]
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
                        'taker_buy_quote_asset_volume': float(information_kline.get('Q'))}
                    
                    # here, we write stuff in the database
                    #save_price_history(obj=price_history_dict)
                    print('We will be writing the top of the book {}'.format(self.top_of_book))
                    print('We will also be writing the candle {}'.format(price_history_dict))
                    #save_top_of_book(obj=self.top_of_book[symbol_id])

            self.global_counter += 1

        self.websocket.streams = list(set(self.websocket.streams)) # quick fix
        self.websocket.bm.start_multiplex_socket(streams=self.websocket.streams, callback=on_message)

def save_top_of_book(obj, timestamp=None):
    asyncio.run(dataaccess_price_history.create(**obj))


def save_price_history(obj, timestamp=binance.client.convert_ts_str('now UTC')):
    asyncio.run(dataaccess_price_history.create(**obj))
    asyncio.run(dataaccess_symbols.update(id=obj['symbol_id'],timestamp=timestamp))


async def load_price_history(symbol, symbol_id, timestamp=None):
    
    api = API()
    symbol = symbol.rstrip() # clean the symbol
    
    if timestamp is None:
        timestamp = api.client._get_earliest_valid_timestamp(
            symbol=symbol, interval='1m')
    timestamp_end = timestamp 
    while timestamp_end < binance.client.convert_ts_str('now UTC'):
        timestamp_end += 60000 * 10000  # writing 10000 lines
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
            save_price_history(obj=price_history_dict, timestamp=timestamp_end)

        timestamp = timestamp_end


async def _fix(inconsistent_symbols):
    """Input format: list [(name, last updated time)]"""
    for _inconsistent_symbol in inconsistent_symbols:
        asyncio.run(load_price_history(_inconsistent_symbol['name'], _inconsistent_symbol['id'], _inconsistent_symbol['updated_at']))


def run_online_wrapper():
    try:

        print("fetch_online_data started")
        manager = FetchingManager()
        asyncio.run(manager.monitor_online_fetch())

        return manager
   
    except:
        print(traceback.format_exc())
    


#if __name__=='__main__':
    #asyncio.run(dataaccess_symbols.create(name='BNBETH')) # run only once for experiment purposes
    #manager = FetchingManager(symbols = [{'id': 1, 'name': 'BNBETH'}])
    #asyncio.run(manager.monitor_online_fetch())
    #print('hey')