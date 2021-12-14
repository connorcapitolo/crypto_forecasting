from time import time
import binance
import asyncio
import traceback

import dataaccess.session as database_session
from dataaccess import symbols as dataaccess_symbols
from dataaccess import price_history as dataaccess_price_history
from datacollector.api import API


def fetch_price_history(symbol, symbol_id, timestamp=None):
    try:
        print("fetch_price_history")

        asyncio.run(fetch_price_history_async(
            symbol, symbol_id, timestamp=timestamp))

        return {"symbol_id": symbol_id, "status": "success"}
    except:
        print("Error in fetch_price_history...")
        print(traceback.format_exc())
        return {"symbol_id": symbol_id, "status": "failure"}


async def fetch_price_history_async(symbol, symbol_id, timestamp=None):
    print("fetch_price_history_async")
    # Connect to database
    await database_session.connect()

    api = API()
    symbol = symbol.rstrip()  # clean the symbol

    if timestamp is None:
        timestamp = api.client._get_earliest_valid_timestamp(
            symbol=symbol, interval='1m')
        # timestamp = binance.client.convert_ts_str('now UTC') - 60000 * 100000 # want 100000 lines
    timestamp_end = timestamp
    while timestamp_end < binance.client.convert_ts_str('now UTC'):
        timestamp_end += 60000 * 10000  # writing 10000 lines
        print("==============================================")
        print('Fetch timestamps:', symbol, timestamp, timestamp_end)
        print("==============================================")
        bars = api.query_data_for_long_time(
            pair=symbol, frequency='1m', start_timestamp=timestamp, end_timestamp=timestamp_end, verbose=True)

        print("len(bars):", len(bars))
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

            # Save the data
            await dataaccess_price_history.create(**price_history_dict)

        # Update the endtimestamp to db
        await dataaccess_symbols.update(id=symbol_id, timestamp=timestamp_end)

        timestamp = timestamp_end

    # Disconnect from database
    await database_session.disconnect()


def save_price_online(price_history_dict):
    try:
        print("save_price_online")

        asyncio.run(save_price_online_async(price_history_dict))

        return price_history_dict["id"]

    except:
        print(traceback.format_exc())


async def save_price_online_async(price_history_dict):
    print("save_price_online_async")
    # Connect to database
    await database_session.connect()

    symbol_id = price_history_dict["id"]
    timestamp_end = price_history_dict["close_time"]

    # Save the data
    await dataaccess_price_history.create(**price_history_dict)

    # Update the endtimestamp to db
    await dataaccess_symbols.update(id=symbol_id, timestamp=timestamp_end)

    # Disconnect from database
    await database_session.disconnect()
