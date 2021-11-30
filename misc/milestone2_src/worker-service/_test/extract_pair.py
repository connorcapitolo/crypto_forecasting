from _test.api import API
import binance
#from websocket_crypto_multiple import WebsocketCoinMultiple


class Pair:
    """This class will be used in order to launch the history query for a specific pair, storing it in the right table and
    launching the websocket robot when the historical query is done in order to get the entire data for a specific pair"""

    def __init__(self, pair, frequency='1m'):
        """The constraint on this initialization is that the pair is of the form ['BTCUSDT'], ie two currencies that
        are currently being used in the Binance API"""
        if len(pair.split(' ')) > 1:
            raise ValueError('For now, we can set up pairs one by one')
        self.pair = pair.lower()
        self.frequency = frequency
        self.api = API()
        #self.websocket = WebsocketCoinMultiple(coins=pair.upper())

    def extract_historical_data(self, timestamp=None):
        # self.websocket.initialize_RDS()
        #stream = self.websocket.streams[0].replace('@', '_')
        if timestamp is None:
            timestamp = self.api.client._get_earliest_valid_timestamp(
                symbol=self.pair.upper(), interval='1m')
        timestamp_end = timestamp + 60000*1000  # 1 minute * 1000 lines
        while timestamp_end < binance.client.convert_ts_str('now UTC'):
            df = self.api.query_data_for_long_time(pair=self.pair.upper(
            ), frequency='1m', start_timestamp=timestamp, end_timestamp=timestamp_end, verbose=False)
            print(df.head())
            # self.websocket.RDSs[self.pair.upper()].add_dataset(
            #     name_datatable=stream, df=df)
            timestamp = timestamp_end
            timestamp_end += 60000 * 1000

    def extract_online_data(self):
        self.websocket.startService()


if __name__ == '__main__':
    p = Pair('bnbbtc')
    p.extract_historical_data()
    # p.extract_online_data()
