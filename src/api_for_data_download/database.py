import sqlite3 as sql
from API import query_data_for_long_time, access_all_market
import warnings

warnings.filterwarnings('ignore')


def get_all_coins():
    quote = access_all_market()
    exchanges = [d['symbol'] for d in quote]
    return exchanges


def save_df(name_df, coin='BTCUSDT', frequency_update=['1w'], data_type='candles'):
    connector = sql.connect('{}.db'.format(name_df))  # create a database
    for freq in frequency_update:
        df = query_data_for_long_time(coin=coin, frequency=freq)
        df.to_sql(name='{}_{}_{}'.format(coin, data_type, freq), con=connector,
                  if_exists='replace')  # create a table


def setup_exchange(coin):
    """This function will be used in order to extract all of the possible information we want from a specific exchange.
    For now, we will be able to extract the candles with different frequency updates, but in the future we will extract more
    information about the different exchanges. This takes into account, in particular, the order book."""
    raise NotImplementedError


def setup_database():
    exchanges = get_all_coins()
    for coin in exchanges[:2]:
        save_df(name_df='{}'.format(coin), coin=coin, frequency_update=['1w', '3d'])
    print('Done')


if __name__ == '__main__':
    print('working on it')