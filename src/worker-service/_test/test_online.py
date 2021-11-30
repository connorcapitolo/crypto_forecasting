import os
import asyncio
import traceback

import binance
from binance import ThreadedWebsocketManager

from datacollector.api import API
import dataaccess.session as database_session
from dataaccess import symbols as dataaccess_symbols

major_coins = ['BTC', 'ETH', 'BNB', 'USDT', 'BUSD', 'USD']

# Run script: python -m _test.test_online


async def run_websocket():
    print("run_websocket...")

    api = API()
    # Connect to database
    await database_session.connect()
    try:

        symbols = await dataaccess_symbols.browse()

        data_type = "kline"
        update_frequency = '1m',
        frequency_data_update = '1m'
        coins_market = api._access_all_coins()
        reversed_coins = []
        initial = len(symbols)
        coins = [symbol["name"] for symbol in symbols]

        streams = []

        for coin in coins:
            for major_coin in major_coins:
                if major_coin in coin:
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
            stream_kline = '{}@{}_{}'.format(coin.lower(),
                                             data_type, update_frequency)

            streams.append(stream_kline)

        print("streams:", streams)
        streams = ["btcusdt@kline_('1m',)"]

        def on_message(message):
            data = message["data"]
            print("data:", data)

        bm = ThreadedWebsocketManager(
            api_key=api.api_key, api_secret=api.api_secret)
        bm.start()

        bm.start_multiplex_socket(streams=streams, callback=on_message)
        bm.join()

    except Exception as e:
        print(e)
        traceback.print_exc()

    # Disconnect from database
    await database_session.disconnect()

asyncio.run(run_websocket())
