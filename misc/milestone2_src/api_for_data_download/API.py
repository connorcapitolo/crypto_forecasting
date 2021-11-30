import time
from binance.client import Client
import pandas as pd
from _env import get_api_info



class API:
    """This class creates a connection to the API. This will allow, amongst other things, to query the historical data for a specific coin and a specific data type"""

    def __init__(self):
        self.api_key, self.api_secret = get_api_info()
        self.client = Client(self.api_key, self.api_secret)

    @staticmethod
    def time_wrapper(f):
        '''
        just used to get the execution time for the function
        '''
        try:
            start = time.time()
            f()
            print('Total time', time.time() - start)
        except ValueError:
            print('The execution of the inner function has failed')


    def access_all_market(self):
        '''Obtaining of list of dictionaries for each of the 1642 coins on Binance; a dictionary is comprised of a symbol and price e.g. {'symbol': 'ETHBTC', 'price': '0.07427400'}
        '''
        prices = self.client.get_all_tickers()
        return prices

    def access_all_coins(self):
        '''Getting a list of all 1642 symbols e.g. ['ETHBTC', ...] (see access_all_market function)'''
        return [d['symbol'] for d in self.access_all_market()]

    def query_data_for_long_time(self, coin='BTCUSDT', frequency='1m', request='candles'):
        '''
        Getting historical data for a certain coin based on a certain frequency level from the candles feature
        Return: pandas Dataframe comprised of columns with candles features and rows that are frequency of observations
        '''
        if frequency not in {'1m', '3m', '5m', '15m', '30m', '1h', '2h', '4h', '6h', '8h', '12h', '1d', '3d', '1w', '1M'}:
            raise AttributeError(
                'Invalid frequency, should be in {1m, 3m, 5m, 15m, 30m, 1h, 2h, 4h, 6h, 8h, 12h, 1d, 3d, 1w, 1M}')
        if request not in {'candles'}:
            raise AttributeError('Invalid request, should be in {candles}')
        timestamp = self.client._get_earliest_valid_timestamp(symbol='BTCUSDT', interval=frequency)

        print('Querying {} data from _____ until present time, with a frequency update of {}'.format(request, frequency))
        if request == 'candles':

            columns = ['Open Time', 'Open Price', 'High price', 'Low Price', 'Close Price', 'Volume Traded', 'Close Time',
                       'Quote asset Volume',
                       'Number of Trades', 'Taker buy base asset volume', 'Taker buy quote asset volume', 'NA']
            start = time.time()
            bars = self.client.get_historical_klines(coin, frequency, timestamp, limit=1000)  # we get data from Aug 15 2017

            print('Fetched {} lines of data in {} seconds'.format(len(bars), time.time() - start))
            df = pd.DataFrame(bars, columns=columns)

        return df

# testing API() class
if __name__=='__main__':
    start = time.time()
    # instantiate API class
    check_api_key = API()
    
    # performing loading from Binance utilizing their API
    btcusdt_df = check_api_key.query_data_for_long_time()

    # saving the Pandas dataframe to csv
    btcusdt_df.to_csv('./btcusdt_exchange.csv')
    
    print('Appears to have completed successfully.')
    end = (time.time() - start) / 60
    print(f'Total time: {end:.3f} minutes')