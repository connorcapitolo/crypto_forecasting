from time import time
import pandas as pd
import binance
import asyncio
import traceback
from google.cloud import storage
import os
import dataaccess.session as database_session
from dataaccess import symbols as dataaccess_symbols
from dataaccess import price_history as dataaccess_price_history
from datacollector.api import API
from log_conf import Logger

# necessary to connect to GCS bucket, add stuff in the dockerfile 

gcp_project = os.environ["GCP_PROJECT"]
bucket_name = os.environ["GCS_BUCKET"]


def fetch_price_history(symbol, symbol_id, timestamp=None):
    try:
        Logger.logr.info("fetch_price_history")

        asyncio.run(fetch_price_history_async(
            symbol, symbol_id, timestamp=timestamp))

        return {"symbol_id": symbol_id, "status": "success"}
    except:

        Logger.logr.ERROR("Error in fetch_price_history...")
        Logger.logr.ERROR(exc_info=1)
        return {"symbol_id": symbol_id, "status": "failure"}


async def fetch_price_history_async(symbol, symbol_id, timestamp=None):
    Logger.logr.info("fetch_price_history_async")
    # Connect to database
    await database_session.connect()

    api = API()
    symbol = symbol.rstrip()  # clean the symbol

    if timestamp is None:
        timestamp = api.client._get_earliest_valid_timestamp(
            symbol=symbol, interval='1m')
        # for 'now - 60000 * n', n is the number of lines to fetch
        timestamp = max(binance.client.convert_ts_str('now UTC') - 60000 * 1000000, timestamp) # want 1000000 lines for full production deployment
    timestamp_end = timestamp


    # this is where we are constantly fetching from Binance API to get historical data!

    # by uncommenting the two lines below (and commenting out the other while loop on the third line), only fetch 10000 obs. (have to be careful with this debugging as modeling and frontend can't be viewed well with these)
    # stop = timestamp
    # while timestamp_end < stop+60000*5000:
    while timestamp_end < binance.client.convert_ts_str('now UTC'):
        
        timestamp_end += 60000 * 10000  # writing 10000 lines
        Logger.logr.info("==============================================")
        Logger.logr.info(f'Fetch timestamps: {symbol, timestamp, timestamp_end}')
        Logger.logr.info("==============================================")
        bars = api.query_data_for_long_time(
            pair=symbol, frequency='1m', start_timestamp=timestamp, end_timestamp=timestamp_end, verbose=True)

        Logger.logr.info(f"len(bars): {len(bars)}")
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

    Logger.logr.info('Finished Fetching historical data, pushing the data to GCS...')
    list_dictionnary = await dataaccess_price_history.get_by_symbol_id(symbol_id, page_size=1000000)

    df = await create_df(list_dictionnary)

    await push_GCS(df, symbol)

    # Disconnect from database
    await database_session.disconnect()


def upload_blob(bucket_name, filename, destination_file_name):
    """Uploads a blob to the bucket."""

    # uses the module storage_client
    # this implicitly calls to "secrets/bucket-reader.json" from the GOOGLE_APPLICATION_CREDENTIALS
    storage_client = storage.Client(project=gcp_project)

    # open the bucket
    bucket = storage_client.bucket(bucket_name)

    # looks inside the bucket
    blob = bucket.blob(destination_file_name)

    # upload specific file
    blob.upload_from_filename(filename)


async def push_GCS(df, symbol):
    """
    - inside BNBBTC: 
                  - /Data folder
                          - .csv file with the entire dataset (non persistent, pushed before model training and deleted after model training
    """
    Logger.logr.info('Pushing the .csv file to GCS bucket')
    filename = f'{symbol}_temporary.csv'
    df.to_csv(filename, index=False)
    symbol = symbol.upper() # should not have any effect
    destination_path = f'{symbol}/Data/{filename}'
    upload_blob(bucket_name, filename, destination_path)
    os.remove(filename)
    Logger.logr.info('Pushed the .csv file to GCS bucket! Switching to Live Stream')


async def create_df(list_dictionnary):
    dict_output = {k: [] for k in list(list_dictionnary[0].keys())}

    for output in list_dictionnary:
        # output is a dictionary
        for key in output:
            dict_output[key].append(output.get(key))

    return pd.DataFrame(dict_output)


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
