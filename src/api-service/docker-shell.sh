#!/bin/bash

# exit immediately if a command exits with a non-zero status
set -e

# Read the settings file
# I think we should stick this in a ./env.dev file
# I also think this should be 'export BINANCE_API_KEY=$(BINANCE_API_KEY)' so that it isn't hard-coded in and other people can utilize their own APIs
#source ./env.dev
export IMAGE_NAME="crypbros-api-service"
export BASE_DIR=$(pwd)
export COMMON_DIR=$(dirname "$(pwd)")/common
export SECRETS_DIR=$(pwd)/../secrets/
export DATABASE_URL="postgres://cryp:bros@crypbrosdb-server:5436/crypbrosdb"
export REDIS_URL="redis://crypbros-redis:6379/0" # useful ? 
export BINANCE_API_KEY="RLis1zPSdrqFz1uP28k9aJlhElR9lJnynaCldpSNeob2PrnhnoMiGAA7drlZdpC4"
export BINANCE_SECRETS_KEY="hplmjruPIXcHAQSC6F4OUPwoJvXfwjTeAeqJQiKAh7xAQC9QbZSo0y3yCI4gtbOH"

export GCP_PROJECT="crypto-forecasting-app"
export GCP_ZONE="us-central1-a"
export GCS_BUCKET="crypto-forecasting-bucket"
export GOOGLE_APPLICATION_CREDENTIALS=/secrets/bucket-reader.json


# Create the network if we don't have it yet
docker network inspect crypbros >/dev/null 2>&1 || docker network create crypbros

# build the image based on the Dockerfile
docker build -t $IMAGE_NAME -f Dockerfile .

# create the container
docker run --rm --name $IMAGE_NAME -ti \
--mount type=bind,source="$BASE_DIR",target=/app \
--mount type=bind,source="$COMMON_DIR/dataaccess",target=/app/dataaccess \
--mount type=bind,source="$COMMON_DIR/datacollector",target=/app/datacollector \
--mount type=bind,source="$SECRETS_DIR",target=/secrets \
-p 9600:9000 \
-e DEV=1 \
-e DATABASE_URL=$DATABASE_URL \
-e GOOGLE_APPLICATION_CREDENTIALS=$GOOGLE_APPLICATION_CREDENTIALS \
-e GCP_PROJECT=$GCP_PROJECT \
-e GCP_ZONE=$GCP_ZONE \
-e GCS_BUCKET=$GCS_BUCKET \
-e REDIS_URL=$REDIS_URL \
-e BINANCE_API_KEY=$BINANCE_API_KEY \
-e BINANCE_SECRET_KEY=$BINANCE_SECRET_KEY \
--network crypbros $IMAGE_NAME