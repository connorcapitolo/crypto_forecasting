from tensorflow.keras.models import load_model
import numpy as np

from dataaccess import price_history as dataaccess_price_history
from dataaccess import top_of_book as dataaccess_top_of_book
from api.schemas import Symbol
from dataaccess import symbols as dataaccess_symbols
from os import name
import json
from fastapi import APIRouter, Depends, Path, Query
from api import preprocessing
from api.errors import AccessDeniedError
from dataaccess import symbols as dataaccess_symbols
from dataaccess import price_history as dataaccess_price_history
from dataaccess.errors import RecordNotFoundError

# https://stackoverflow.com/questions/15727420/using-logging-in-multiple-modules
from log_conf import Logger

# this is for downloading LSTM models from GCS
from google.cloud import storage
import os
gcp_project = os.environ["GCP_PROJECT"]
bucket_name = os.environ["GCS_BUCKET"]
# persistent_folder = "/app"
# saving our model experiments in this folder; remember that all api-service stuff is in /app folder within container
local_experiments_path = "/app/model_experiments"


def download_blob(bucket_name, source_blob_name, destination_file_name):
    """Downloads a blob from the bucket."""

    # uses the module storage_client
    # this implicitly calls to "secrets/bucket-reader.json" from the GOOGLE_APPLICATION_CREDENTIALS
    storage_client = storage.Client(project=gcp_project)

    # open the bucket
    bucket = storage_client.bucket(bucket_name)
    # looks inside the bucket
    blob = bucket.blob(source_blob_name)
    # download specific file
    blob.download_to_filename(destination_file_name)


def load_best_model(symbol: str):
    '''
    This will load the best model from GCS for the specific symbol.

    Returns:
        the .h5 LSTM model created in Tensorflow
    '''

    # What I can do here is search for the best model and then place in the higher level folder as a .h5 file
    # e.g. model_experiments/BNBBTC/best_model/
    #     - contains .index file
    #     - contains model_metrics.json

    # first search is in the best_model/; if it's not there, then search if there's any values in the main folder one step lower; if there's nothing then return an error

    '''
    gcp_model_name = 'initial_lstm.h5'
    print(f'Model to download from GCP: {gcp_model_name}')

    container_model_name = 'model.h5'
    # this is where I can create the model location in the tracker.py
    container_model_location = os.path.join(
        persistent_folder, container_model_name)
    
    download_blob(bucket_name, gcp_model_name, container_model_location)
    
    print(f'Model saved on container at {container_model_location}')
    '''

    # getting the weights
    best_model_filepath = os.path.join(
        local_experiments_path, symbol, 'best_model', 'model.index')
    # getting the json file to extrac certain values
    best_model_json_filepath = os.path.join(
        local_experiments_path, symbol, 'best_model', 'best_model_metrics.json')
    
    # load everything necessary to getting model outputs
    args_model = _load_model(best_model_filepath, best_model_json_filepath)
    

    # this is for extracting the json
    Logger.logr.info(f"Downloaded best model from api-service container location {best_model_filepath}")
    Logger.logr.info(f"Validation score was {args_model['validation_score']}")

    return args_model

def _load_model(best_model_filepath, best_model_json_filepath):
    "Will load the model from the local location and the necessary for post-processing"
    
    model =  preprocessing.create_model()
    model.load_weights(best_model_filepath)

    with open(best_model_json_filepath, 'r') as f:
        data = json.load(f)
    
    val_score = data["validation_score"]
    x_means, x_stds = np.array(data["x_mean"]), np.array(data["x_std"])
    y_mean, y_std = np.array(data["y_mean"]), np.array(data["y_std"])

    args = {"model": model, 
            "x_mean": x_means,
            "x_std": x_stds,
            "y_mean": y_mean,
            "y_std": y_std, 
            "validation_score": val_score}

    return args


def generate_prediction(arg_model, df, input_sequence_length = 64):
  '''
  Taking the passed in model and dataframe and providing future predictions

  Args:
    model: the .h5 LSTM model created in Tensorflow
    df: the historical data being used for predictions
    input_sequence_length: the length of the input seequence to use by the LSTM model for making future predictions (keeping track of the hidden state)

  Returns:
    The unstandardized predictions on a minute-by-minute basis into the future
  '''

  df = df.drop(['id', 'name'], axis = 1)
  df = df.rename(columns = {'open_time': 'Open Time', 'open_price': 'Open Price', 'high_price': 'High price', 'low_price': 'Low Price', 'close_price': 'Close Price', 'volume_traded': 'Volume Traded', 'close_time': 'Close Time', 'quote_asset_volume': 'Quote asset Volume', 'number_of_trades': 'Number of Trades', 'taker_buy_base_asset_volume': 'Taker buy base asset volume', 'taker_buy_quote_asset_volume': 'Taker buy quote asset volume'})
  x_mean, x_std = arg_model['x_mean'], arg_model['x_std']
  input_data, features_list =  preprocessing.preprocess_df(df, batch_size=128, x_mean=x_mean, x_std=x_std)
  # need to convert back from standardized to original close_price scale
  model = arg_model['model']
  Logger.logr.debug(features_list)
  last_prices_index = features_list.index('benchmark')

  Logger.logr.debug(list(input_data))
  Logger.logr.debug(list(input_data)[-1][-1][:, last_prices_index])

  predictions = model.predict(input_data)

  y_mean, y_std = arg_model['y_mean'], arg_model['y_std']
  to_return = predictions[-1] + list(input_data)[-1][-1][-1, last_prices_index]
  Logger.logr.debug(f'Unnormalized predictions {to_return}')
  prediction = to_return * y_std + y_mean

  return prediction


async def get_price_history(
    symbol: str, 
    num_obs: int = 100
):
    '''
    Method to obtain the price history by first checking if the symbol is available in the Postgres database by checking the symbols table for its existence; if it's not, the data symbol is added to the symbols table so that the worker in worker-service can extract the historical data from the Binance API

    Args:
        symbol: an exchange pair (e.g. BNBBTC, BTCUSDT, etc.)
        num_obs: the number of observations to load from the price_history database; these are the most recent values from the database

    Returns:
        a list of dictionaries (JSON format) for the previous X observations

        Example output:

        [
            {
                "id": 1228,
                "name": "BTCUSDT",
                "open_time": 1502974920000,
                "open_price": 4411,
                "high_price": 4411,
                "low_price": 4411,
                "close_price": 4411,
                "volume_traded": 0,
                "close_time": 1502974979999,
                "quote_asset_volume": 0,
                "number_of_trades": 0,
                "taker_buy_base_asset_volume": 0,
                "taker_buy_quote_asset_volume": 0
            },
            {
                "id": 163,
                "name": "BTCUSDT",
                "open_time": 1502942940000,
                "open_price": 4261.48,
                "high_price": 4261.48,
                "low_price": 4261.48,
                "close_price": 4261.48,
                "volume_traded": 0,
                "close_time": 1502942999999,
                "quote_asset_volume": 0,
                "number_of_trades": 0,
                "taker_buy_base_asset_volume": 0,
                "taker_buy_quote_asset_volume": 0
            }, ...
        ]
    '''


    # print("get_price_history ...")
    # print("symbol:", symbol)

    symbol = symbol.upper()


    # TO DO: have we handled the case where historical fetching is happening (status = 1), and someone tries to perform a prediction with this symbol?
    try:
        symbol_db = await dataaccess_symbols.get_by_name(name=symbol)

    except RecordNotFoundError:

        symbol_db = await dataaccess_symbols.create(name=symbol)

        return {
            "User requesting predictions for a symbol that does not previously exist. Fetching historical data for the symbol now": symbol_db,
        }

    # querying the price_history table here (wanting to get 100 total previous data points since we're only going back 64 anyways)
    return await dataaccess_price_history.browse(name=symbol, page_size=num_obs)



### old ###
def make_prediction() -> float:
    ''''
    This was the initial modeling used for Milestone 2 to make predictions (NO LONGER NEEDED, BUT LEAVE HERE FOR REFERENCE AND SHOWING HOW THE FRONTEND CONNECTS WITH API!)
    '''

    lstm_model = load_model('model_ex6.h5')
    x_train = np.load('x_train.npy')
    assert x_train.shape == (1, 32, 8)

    lstm_prediction = lstm_model.predict(np.expand_dims(x_train[0], axis=0))
    float_prediction = float(lstm_prediction[0][0])

    close_price_mean = 15592.779883026773
    close_price_std = 15397.688146787825

    prediction = float_prediction * close_price_std + close_price_mean

    return prediction
