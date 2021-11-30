# Crypto Forecasting

# API For Data Download

We use this `API.py` to query the Binance database and obtain minute-by-minute information about the BTCUSDT exchange dating back to its conception in 2017
- this produces a dataset that is a total of 2,188,606 observations and 12 features; see our notebooks/initial_EDA_and_modeling.ipynb for further analysis

## Prerequisites
### Install Docker 
Install `Docker Desktop`

#### Ensure Docker Memory
- To make sure we can run multiple container go to Docker>Preferences>Resources and in "Memory" make sure you have selected > 4GB

### Install VSCode  
Follow the [instructions](https://code.visualstudio.com/download) for your operating system.  
If you already have a preferred text editor, skip this step.  

## Database Server
-  `cd database-server`
- Start docker shell `sh ./docker-shell.sh`
- Check migration status: `dbmate status`

### Create a new migration script
dbmate new base_tables

### Running Migrations
dbmate up
dbmate rollback
dbmate dump
dbmate status

## Worker Service
-  `cd worker-service`
- Create `env.dev` file with all the containers environment variables:
```
#!/bin/bash

# The name of the docker images to produce
export IMAGE_NAME="crypbros-worker-service"

export BASE_DIR=$(pwd)
export COMMON_DIR=$(dirname "$(pwd)")/common
export SECRETS_DIR=$(pwd)/../secrets/
export PERSISTENT_DIR=$(pwd)/../persistent-folder/
export DATABASE_URL="postgres://cryp:bros@crypbrosdb-server:5436/crypbrosdb"
export REDIS_URL="redis://crypbros-redis:6379/0"
export GCP_PROJECT="<YOUR PROJECT ID>"
export GCP_ZONE="us-central1-a"
export GOOGLE_APPLICATION_CREDENTIALS=/secrets/gcp-service.json
export BINANCE_API_KEY="<KEY HERE>"
export BINANCE_SECRETS_KEY="<SECRETS_KEY>"
```
- Start docker shell `sh ./docker-shell.sh`

To install a new python package use `pipenv install pandas` from the docker shell

To run development worker service run `worker` from the docker shell


## API Service
-  `cd api-service`
- Create `env.dev` file with all the containers environment variables:
```
#!/bin/bash

# The name of the docker images to produce
export IMAGE_NAME="crypbros-api-service"

export BASE_DIR=$(pwd)
export COMMON_DIR=$(dirname "$(pwd)")/common
export SECRETS_DIR=$(pwd)/../secrets/
export PERSISTENT_DIR=$(pwd)/../persistent-folder/
export DATABASE_URL="postgres://cryp:bros@crypbrosdb-server:5436/crypbrosdb"
export REDIS_URL="redis://crypbros-redis:6379/0"
export GCP_PROJECT="<YOUR PROJECT ID>"
export GCP_ZONE="us-central1-a"
export GOOGLE_APPLICATION_CREDENTIALS=/secrets/gcp-service.json
export BINANCE_API_KEY="<KEY HERE>"
export BINANCE_SECRETS_KEY="<SECRETS_KEY>"
```
- Start docker shell `sh ./docker-shell.sh`

To install a new python package use `pipenv install requests` from the docker shell

To run development api service run `uvicorn_server` from the docker shell

Test the API service by going to `http://0.0.0.0:9600/`