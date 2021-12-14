import os
from binance.client import Client
import time
import pandas as pd
from binance.exceptions import BinanceAPIException
import binance
from log_conf import Logger


major_coins = ['BTC', 'ETH', 'BNB', 'USDT', 'BUSD', 'USD']
# api_secret = os.environ["BINANCE_SECRETS_KEY"]
# api_key = os.environ["BINANCE_API_KEY"]


class API:
    """This class creates a connection to the API. This will allow, amongst other things, to query the historical data
    for a specific coin and a specific data type"""

    def __init__(self):
        self.api_key = "RLis1zPSdrqFz1uP28k9aJlhElR9lJnynaCldpSNeob2PrnhnoMiGAA7drlZdpC4"
        self.api_secret = "hplmjruPIXcHAQSC6F4OUPwoJvXfwjTeAeqJQiKAh7xAQC9QbZSo0y3yCI4gtbOH"
        self.client = Client(self.api_key, self.api_secret)

    def _access_all_market(self):
        prices = self.client.get_all_tickers()
        return prices

    def _access_all_coins(self):
        return [d['symbol'] for d in self._access_all_market()]

    def query_data_for_long_time(self, pair='BTCUSDT', frequency='1m', request='candles', start_timestamp=None, end_timestamp=None, verbose=True):
        if frequency not in {'1m', '3m', '5m', '15m', '30m', '1h', '2h', '4h', '6h', '8h', '12h', '1d', '3d', '1w', '1M'}:
            raise AttributeError(
                'Invalid frequency, should be in {1m, 3m, 5m, 15m, 30m, 1h, 2h, 4h, 6h, 8h, 12h, 1d, 3d, 1w, 1M}')
        if request not in {'candles'}:
            raise AttributeError('Invalid request, should be in {candles}')
        if start_timestamp is None:
            start_timestamp = self.client._get_earliest_valid_timestamp(
                symbol='BTCUSDT', interval=frequency)
        if verbose:
            Logger.logr.info(f'Querying {request} data from {start_timestamp} until {end_timestamp}, with a frequency update of {frequency}')
        if request == 'candles':

            columns = ['Open Time', 'Open Price', 'High price', 'Low Price', 'Close Price', 'Volume Traded', 'Close Time',
                       'Quote asset Volume',
                       'Number of Trades', 'Taker buy base asset volume', 'Taker buy quote asset volume', 'NA']
            start = time.time()

            try:
                bars = self.client.get_historical_klines(symbol=pair.upper(
                ), interval=frequency, start_str=start_timestamp, end_str=end_timestamp, limit=1000)  # we get data from Aug 15 2017
            except BinanceAPIException:
                try:
                    bars = self.client.get_historical_klines(symbol=pair.lower(
                    ), interval=frequency, start_str=start_timestamp, end_str=end_timestamp, limit=1000)
                except BinanceAPIException:
                    raise ValueError('The pair inserted is the wrong format')
            if verbose:
                Logger.logr.info(f'Fetched {len(bars)} lines of data in {time.time() - start} seconds')
            df = pd.DataFrame(bars, columns=columns)

        return bars  # df


if __name__ == '__main__':
    api = API()
    print(api.client._get_earliest_valid_timestamp(
        symbol='BNBETH', interval='1m'))
    print(binance.client.convert_ts_str('now UTC'))
    time.sleep(60)
    print(binance.client.convert_ts_str('now UTC'))
