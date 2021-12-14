import os
import asyncio
from glob import glob
import json
import time

import tensorflow as tf
from google.cloud import storage

# https://stackoverflow.com/questions/15727420/using-logging-in-multiple-modules
from log_conf import Logger

# from dataaccess.session import database

gcp_project = os.environ["GCP_PROJECT"]
bucket_name = os.environ["GCS_BUCKET"]
# saving our model experiments in this folder; remember that all api-service stuff is in /app folder within container
local_experiments_path = "/app/model_experiments"

# Setup experiments folder whenever we initially create server
if not os.path.exists(local_experiments_path):
    os.mkdir(local_experiments_path)


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


def download_experiment_metrics():
    # Get all model metrics
    # download from GCP al the json files to local

    # go to GCP --> pull all the model_metrics.json files from GCS for the specific pair into the container --> search through the json files locally (within container) find the model with the best validation score, and save that "key" --> go to GCP and pull the appropriate .h5 file

    # tracker.py is pulling in the models from GCS, so model.py can really just call experiments/{sybmol_id}/ folder to get the .h5 file (can also save .json file in here too)
    # handle the edge case where there isn't a model for the pair eyt
    '''
    - Have a list of directories, one for every pair (top level)
    /BNBBTC/Model/LSTM_BNBBTC_{unique_id}/
        - inside BNBBTC: 
                  - /Data folder
                          - .csv file with the entire dataset (non persistent, pushed before model training and deleted after      model training
                  - /Model folder 
                          - list of folders, one for every model we have, for example inside
                          LSTM_BNBBTC_{unique_id}:
                                 
                                  - lstm_{symbol}.index file with the actual model
                                  - model_metrics_{symbol}.json file with hyperparameters and timestamp of the data on which it has been trained
                                        - validation score
                                        - hyperparameters
                                        - training time stamps
                                        - unique_id
                                        - symbol
                           LSTM_BNBBTC_6:
                                  - lstm_{symbol}.index file with the actual model
                                  - model_metrics_{symbol}.json file with hyperparameters and timestamp of the data on which it has been trained
                                        - validation score
                                        - hyperparameters
                                        - training time stamps
                                        - unique_id
                                        - symbol

    '''

    # we will want the pair, and then load the .h5 based on the validation score
    # bucket_name
    # example: gs://crypto-forecasting-bucket/initial_lstm.h5
    # example structure: gs://crypto-forecasting-bucket/BNBBTC/Model/LSTM_BNBBTC_{unique_id}/model_metrics.json
    # real example: gs://crypto-forecasting-bucket/BNBBTC/Model/LSTM_BNBBTC_6/model_metrics.json
    models_metrics_list = tf.io.gfile.glob(
        f"gs://{bucket_name}/*/*/*/model_metrics*.json")

    # if this changes to true, it means there's a new model that's been added

    for metrics_file in models_metrics_list:
        # will need to update this accordingly
        # real example: gs://crypto-forecasting-bucket/BNBBTC/Model/LSTM_BNBBTC_6/model_metrics.json
        path_splits = metrics_file.split("/")
        # e.g. BNBBTC
        symbol = path_splits[3]
        # e.g. LSTM_BNBBTC_6
        unique_id = path_splits[5]
        # e.g. model_metrics.json
        local_metrics_file = path_splits[-1]

        # container structure example: model_experiments/BNBBTC/LSTM_BNBBTC_{unique_id}/model_metrics_BNBBTC.json
        local_metrics_file = os.path.join(
            local_experiments_path, symbol, unique_id, local_metrics_file)

        # if there is a new model, then create a new file for it
        # if not os.path.exists(local_metrics_file):  debug David

        Logger.logr.info(f"Copying from GCS bucket location {metrics_file} and put in api-service container location {local_metrics_file}")

        # Ensure user directory exists
        os.makedirs(os.path.join(
            local_experiments_path, symbol), exist_ok=True)
        os.makedirs(os.path.join(
            local_experiments_path, symbol, unique_id), exist_ok=True)

        # doing this so that it matches what we need for download_blob
        # e.g. it's now BNBBTC/Model/LSTM_BNBBTC_{unique_id}/model_metrics.json
        metrics_file = metrics_file.replace(f"gs://{bucket_name}/", "")
        
        # Download the metric json file
        Logger.logr.debug(metrics_file)

        download_blob(bucket_name, metrics_file,
                        local_metrics_file)


    # overriding here 
    fresh_models = True

    return fresh_models


def download_best_models():

    # If we're getting to this point, it means that a new model was added, so need to go through the checks again

    # 

    # What I can do here is search for the best model and then place in the higher level folder as a .h5 file
    # e.g. model_experiments/BNBBTC/best_model/
    #     - contains .h5 file
    #     - contains model_metrics.json

    # I do one pass through where I keep track of the best model and model unique folder for each symbol
    # on the second pass, I just find the best model and download it to the appropriate folder /model_experiments/BNBBTC/best_model folder

    # can do a glob where I get all the model_metrics.json
    # if there isn't a best_model/ when I loop through then I create the folder there
    # I could create a dictionary where the key is the symbol and the values are the unique_id and the validation score
    # at the end of looping through, I then save all the necessary models


    # dictionary for tracking the best model
    best_score_dict = {}
    # example
    '''
    {
        'BNBBTC': {'validation_score': 0.5, 'unique_id': asdfljk, 'h5_file': initial_lstm.h5},
        'BTCUSDT': {...},
        ...
    }
    
    '''
    
    # container structure example: /app/model_experiments/BNBBTC/LSTM_BNBBTC_{unique_id}/model_metrics_BNBBTC.json
    # how-to: https://www.geeksforgeeks.org/how-to-use-glob-function-to-find-files-recursively-in-python/
    models_metrics_list = glob(f"{local_experiments_path}/*/*/model_metrics*.json")

    for metrics_file in models_metrics_list:
        
        Logger.logr.debug(best_score_dict)
        Logger.logr.debug(metrics_file)
        # will need to update this accordingly
        path_splits = metrics_file.split("/")
        # e.g. BNBBTC
        symbol = path_splits[3]
        # e.g. LSTM_BNBBTC_{unique_id}
        unique_id_folder = path_splits[4]

        # check if this symbol exists in dictionary yet
        if symbol not in best_score_dict:
            best_score_dict[symbol] = {}

        # the symbol in the dictionary should always exist at this point
        # e.g. LSTM_BNBBTC_{unique_id}
        # unique_folder = metrics_file[2]

        # e.g. read in JSON file
        local_metrics_file = path_splits[-1]

        # get json file
        
        with open(metrics_file) as f:
            file = json.load(f)
            Logger.logr.debug(file)
            validation_score = file['validation_score']
            unique_id = file['unique_id']
            # h5_file = file['h5_file']

            # if the information inside the best_score_dict[symbol] (e.g. best_dict_score['BNBBTC']) doesn't exist or teh validation score is greater than the current one, then update the best_model
            if 'validation_score' not in best_score_dict[symbol] or validation_score < best_score_dict[symbol]['validation_score']:
                best_score_dict[symbol]['validation_score'] = validation_score
                best_score_dict[symbol]['unique_id'] = unique_id
                best_score_dict[symbol]['unique_id_folder'] = unique_id_folder
                # best_score_dict[symbol]['h5_file'] = h5_file
                best_score_dict[symbol]['full_json'] = file


    for symbol, values in best_score_dict.items():

        # Ensure user directory exists
        os.makedirs(os.path.join(
            local_experiments_path, symbol), exist_ok=True)
        os.makedirs(os.path.join(
            local_experiments_path, symbol, 'best_model'), exist_ok=True)



        # go and download this model from GCP
        # e.g. gs://crypto-forecasting-bucket/BNBBTC/Model/LSTM_BNBBTC_6/lstm_BNBBTC.index
        unique_id_folder = values['unique_id_folder']
        # e.g. BNBBTC/Model/LSTM_BNBBTC_6/lstm_BNBBTC.index
        model_download_filepath = f'{symbol}/Model/{unique_id_folder}/lstm_{symbol}.index'

        # download h5 file to model_experiments/BNBBTC/best_model/model.index
        local_h5_filepath = os.path.join(
            local_experiments_path, symbol, 'best_model', 'model.index')
        download_blob(bucket_name, model_download_filepath, local_h5_filepath)
        
        # download full metrics to model_experiments/BNBBTC/best_model/best_model_metrics.json
        full_json_filepath = os.path.join(
            local_experiments_path, symbol, 'best_model', 'best_model_metrics.json')
        with open(full_json_filepath, "w") as f:
            f.write(json.dumps(values['full_json']))


        Logger.logr.info(
            f'Copied best model from GCP location {model_download_filepath} to api-service container location {local_h5_filepath}')


class TrackerService:
    def __init__(self):
        pass

    async def track(self):
        while True:
            # maybe stick this at the end so it automatically starts loading models
            # it may have been placed here so that uvicorn_server and everything can get set up first
            await asyncio.sleep(1200)
            Logger.logr.info(f"Completed 20 minutes sleep. Now checking if there's any new experiments to download at {round(time.time())}.")

            # Download new model metrics
            # downloading all the json metric files if they don't exist
            # fresh_experiments only needed if I want to use the tracker for downloading models
            fresh_experiments = download_experiment_metrics()

            if fresh_experiments:

                # Download leaderboard models and artifacts
                # finding the best model, and actually downloading the .h5 file
                Logger.logr.info("A new model has been detected. Updating the best models for each symbol.")

                download_best_models()
            
            else:
                Logger.logr.info("No new models detected")
