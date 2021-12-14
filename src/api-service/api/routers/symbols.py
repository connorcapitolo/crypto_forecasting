from os import name

import pandas as pd
from fastapi import APIRouter, Depends, Path, Query
from fastapi import APIRouter

from dataaccess import price_history as dataaccess_price_history
from dataaccess import top_of_book as dataaccess_top_of_book
from api.schemas import Symbol
from dataaccess import symbols as dataaccess_symbols

from api import modeling
from api.errors import AccessDeniedError
from dataaccess import symbols as dataaccess_symbols
from dataaccess import price_history as dataaccess_price_history
from dataaccess import top_of_book as dataaccess_top_of_book
from dataaccess.errors import RecordNotFoundError
from log_conf import Logger

router = APIRouter()


@router.post("/symbol")
async def symbol_create(
    symbol: Symbol
):

    symbol_db = await dataaccess_symbols.create(name=symbol.symbol)

    return symbol_db


@router.get(
    "/get_price_history"
)
async def get_price_history(
    symbol: str = Query(...,
                        description="The symbol to get price history for"),
):
    Logger.logr.info("get_price_history ...")
    Logger.logr.info(f"symbol: {symbol}")

    symbol = symbol.upper()

    # Check if we have the any price history
    try:
        symbol_db = await dataaccess_symbols.get_by_name(name=symbol)

    except RecordNotFoundError:

        symbol_db = await dataaccess_symbols.create(name=symbol)

        return {
            "symbol id": symbol_db,
        }

    # Get price history
    return await dataaccess_price_history.browse(name=symbol, page_size=1000)

    '''
    [
        {
            "id": 1290217,
            "name": "BTCUSDT",
            "open_time": 1638499800000,
            "open_price": 56375.41,
            "high_price": 56375.54,
            "low_price": 56290,
            "close_price": 56290.01,
            "volume_traded": 26.32823,
            "close_time": 1638499859999,
            "quote_asset_volume": 1483150.3295016,
            "number_of_trades": 717,
            "taker_buy_base_asset_volume": 15.68777,
            "taker_buy_quote_asset_volume": 883672.6112724
        },
        {
            "id": 1290215,
            "name": "BTCUSDT",
            "open_time": 1638499740000,
            "open_price": 56340,
            "high_price": 56385.89,
            "low_price": 56311.43,
            "close_price": 56375.42,
            "volume_traded": 26.36029,
            "close_time": 1638499799999,
            "quote_asset_volume": 1485428.8322488,
            "number_of_trades": 1070,
            "taker_buy_base_asset_volume": 11.03931,
            "taker_buy_quote_asset_volume": 622064.0144866
        },
        ...
    ]
    '''


@router.get("/get_top_of_book")
async def get_top_of_book(
    symbol: str = Query(...,
                        description="The symbol to get top of book for"),
):
    print("get_top_of_book ...")
    print("symbol:", symbol)

    symbol = symbol.upper()

    # Check if we have the any price history
    try:
        symbol_db = await dataaccess_symbols.get_by_name(name=symbol)

    except RecordNotFoundError:

        symbol_db = await dataaccess_symbols.create(name=symbol)

        return {
            "task_historical": task_h.id,
            "task_online": task.id
        }

    # Get price history
    return await dataaccess_top_of_book.browse(name=symbol, page_size=20)


@router.post("/predict")
async def prediction(data: dict):
    '''
    Performing the predictions based on the symbol (e.g. BNBBTC, BTCUSDT) passed from the frontend based on user selection.


    Args:
        data: a dictionary provided by the frontend which should contain the symbol to use for querying the database and making a prediction (e.g. BNBBTC)

    Returns:
        A json file with predictions, history, and symbol; predictions and history are each a list of dictionaries that contain keys of "close_price" and "close_time" sorted in ascending order time-wise

        Example of how to use this in FastAPI docs: {"symbol": "BNBBTC"}
    '''

    # https://stackoverflow.com/questions/55409641/asyncio-run-cannot-be-called-from-a-running-event-loop
    # this is querying the price_history table for the particular symbol
    historical_data = await modeling.get_price_history(data["symbol"], num_obs=60000)

    Logger.logr.info(
        f'Number of elements for historical data queried from price_history table: {len(historical_data)}')  # 60000
    # print(historical_data)
    '''
        [
            {
            "id": 1290223,
            "name": "BTCUSDT",
            "open_time": 1638499980000,
            "open_price": 56250.75,
            "high_price": 56255.32,
            "low_price": 56177.32,
            "close_price": 56205.08,
            "volume_traded": 21.27359,
            "close_time": 1638500039999,
            "quote_asset_volume": 1196056.4618977,
            "number_of_trades": 931,
            "taker_buy_base_asset_volume": 8.70503,
            "taker_buy_quote_asset_volume": 489425.2426668
            },
            {
            "id": 1290221,
            "name": "BTCUSDT",
            "open_time": 1638499920000,
            "open_price": 56257.21,
            "high_price": 56261.41,
            "low_price": 56225.87,
            "close_price": 56250.75,
            "volume_traded": 8.02633,
            "close_time": 1638499979999,
            "quote_asset_volume": 451422.1711997,
            "number_of_trades": 538,
            "taker_buy_base_asset_volume": 4.05697,
            "taker_buy_quote_asset_volume": 228164.2143174
            },
            ...
        ]
    '''
    # print(historical_data[0]['open_price'])  # 56250.75
    # Decimal this is a new data type that's distinct from float: https://docs.python.org/3/library/decimal.html
    # print(type(historical_data[0]['open_price']))  # <class 'decimal.Decimal'>

    df_to_predict = pd.DataFrame(historical_data)
    args_model = modeling.load_best_model(data["symbol"])

    Logger.logr.info(
        f'Shape of historical dataframe: {df_to_predict.shape}')  # (60000, 13)
    # print(df_to_predict)
    '''
           id    name      open_time  ... number_of_trades                        taker_buy_base_asset_volume                       taker_buy_quote_asset_volume
0   20055  BNBBTC  1638645780000  ...              121  63.5210000000000007958078640513122081756591796875  0.73221491999999999134018935365020297467708587...
1   20053  BNBBTC  1638645720000  ...              160  83.4789999999999992041921359486877918243408203125  0.96215735999999996153064785175956785678863525...
    '''

    # TO DO: loading the best model from GCS bucket (just using the best model we automatically have)
    # here we are loading the best model that was already locally downloaded

    # this is getting the LSTM prediction
    # by default, takes an input sequence length of 64
    lstm_predictions = modeling.generate_prediction(args_model, df_to_predict)

    Logger.logr.info(f'Number of LSTM predictions into the future: {len(lstm_predictions)}')  # 32
    # [-0.5970218  -0.5971275  -0.59694487 -0.5964275  -0.5961901  ... ]
    Logger.logr.info(f'LSTM predictions: {lstm_predictions}')

    current_close_price_timestamp = historical_data[0]["close_time"]
    predictions_to_report = []
    for p in lstm_predictions:
        dict_for_cp_ct = {}
        # ValueError: [TypeError("'numpy.float32' object is not iterable"), TypeError('vars() argument must have __dict__ attribute')]
        # can do an isinstance check e.g. isinstance(obj, decimal.Decimal)
        dict_for_cp_ct["close_price"] = float(p)
        # close_price is in terms of milliseconds, and we're getting a minute into the future
        current_close_price_timestamp += 60000
        # need to convert to float or I get an error since it's in Decimal type
        dict_for_cp_ct["close_time"] = float(current_close_price_timestamp)
        predictions_to_report.append(dict_for_cp_ct)

    # print(predictions_to_report)

    history_to_report = []
    # getting specific key value pairs from this list of dictionaries
    # now that we have 60000 observations sorted in descending order based on close_time, we only want to get the top 100 of these observations
    # reminder that historical_data is a list of dictionaries that is sorted from newest observations to oldest (based on close_time); can check this by looking at dataaccess/price_history and the browse() function
    for i, h in enumerate(historical_data):
        dict_for_cp_ct = {}
        dict_for_cp_ct["close_price"] = (h["close_price"]+h['open_price'])/2
        dict_for_cp_ct["close_time"] = h["close_time"]
        history_to_report.append(dict_for_cp_ct)

        # this handles when we get to 100 historical observations as well as not having 0 % 0
        if (i+1) % 100 == 0:
            break
    
    # want to reverse this newly created list so that we're providing it now in ascending order for the frontend (oldest observations to newest)
    history_to_report.reverse()
    # return 'predictions' and 'history' with close_price and timestamp (in terms of milliseconds, so multiply by 60000)
    # this is what will be returned to the frontend
    Logger.logr.info(f'Done')
    Logger.logr.info(f'History:\n\n {history_to_report}')
    Logger.logr.info(f'Predictions:\n\n {predictions_to_report}')
    return {
        "symbol": data["symbol"],
        "history": history_to_report,
        "prediction": predictions_to_report
    }


@router.get("/get_current_top_of_book")
async def get_current_top_of_book():
    return await dataaccess_top_of_book.get_current()
