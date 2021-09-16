#!/usr/bin/env python

import sqlite3 as sql
from API import query_data_for_long_time, access_all_market
import warnings

warnings.filterwarnings('ignore')


def get_all_coins():
    '''Obtaining all the 1642 coin names on Binance as a list e.g. ['ETHBTC', 'LTCBTC', 'BNBBTC'] '''
    quote = access_all_market()
    exchanges = [d['symbol'] for d in quote]
    return exchanges


def save_df(name_df, coin='BTCUSDT', frequency_update=['1w'], data_type='candles'):
    '''Create a database in SQLite 
    '''
    connector = sql.connect('{}.db'.format(name_df))  # create a database
    for freq in frequency_update:
        # get the pandas dataframe
        df = query_data_for_long_time(coin=coin, frequency=freq)
        # creating the table in SQLite from the pandas dataframe
        df.to_sql(name='{}_{}_{}'.format(coin, data_type, freq), con=connector,
                  if_exists='replace')


def setup_exchange(coin):
    """This function will be used in order to extract all of the possible information we want from a specific exchange.
    For now, we will be able to extract the candles with different frequency updates, but in the future we will extract more
    information about the different exchanges. This takes into account, in particular, the order book."""
    raise NotImplementedError


def setup_database():
    exchanges = get_all_coins()
    # print(exchanges) # ['ETHBTC', 'LTCBTC', 'BNBBTC', ...]
    for coin in exchanges[:2]:
        save_df(name_df='{}'.format(coin), coin=coin, frequency_update=['1w', '3d'])
    print('Done')

def check_db_bitcoin():
    '''since we're doing a weekly frequency, it should be a database of 214 rows'''
    save_df(name_df='{}'.format('BTCUSDT'))

if __name__ == '__main__':
    # setup_database()
    check_db_bitcoin()
