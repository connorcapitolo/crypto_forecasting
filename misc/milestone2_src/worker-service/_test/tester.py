import asyncio
import traceback

from datacollector import extract_data
import dataaccess.session as database_session


async def run_multiple_websocket():
    print("run_multiple_websocket...")

    # Connect to database
    await database_session.connect()
    try:

        await extract_data.start_multiple_websocket()

    except Exception as e:
        print(e)
        traceback.print_exc()

    # Disconnect from database
    await database_session.disconnect()

asyncio.run(run_multiple_websocket())


# import binance

# from _test.api import API
# from _test.websocket_crypto_multiple import WebsocketCoinMultiple


# def get_history():
#     print("Testing Binance API History")

#     pair = "bnbbtc"

#     print("Getting data for", pair)

#     api = API()
#     timestamp = api.client._get_earliest_valid_timestamp(
#         symbol=pair.upper(), interval='1m')
#     print("timestamp", timestamp)

#     timestamp_end = timestamp + 60000*1000  # 1 minute * 1000 lines
#     df = api.query_data_for_long_time(pair=pair.upper(
#     ), frequency='1m', start_timestamp=timestamp, end_timestamp=timestamp_end, verbose=False)

#     print(df.head())


# def get_live():
#     print("Testing Binance API Live")

#     pair = "bnbbtc"
#     print("Getting data for", pair)

#     api = API()

#     websocket = WebsocketCoinMultiple(coins=[pair.upper()])

#     # Extract online data
#     websocket.startService()


# def get_api_detail():
#     print("Testing Binance API")

#     api = API()
#     # prices = api.access_all_market()
#     # print("prices:", prices)

#     coins_market = api.access_all_coins()
#     print("coins_market:", coins_market)


# # get_history()
# get_api_detail()
