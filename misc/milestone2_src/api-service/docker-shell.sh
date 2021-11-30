#!/bin/bash

# exit immediately if a command exits with a non-zero status
set -e

# Read the settings file
#source ./env.dev
export IMAGE_NAME="crypbros-worker-service"
export BASE_DIR=$(pwd)
export COMMON_DIR=$(dirname "$(pwd)")/common
export DATABASE_URL="postgres://cryp:bros@crypbrosdb-server:5436/crypbrosdb"
export REDIS_URL="redis://crypbros-redis:6379/0"
export BINANCE_API_KEY="RLis1zPSdrqFz1uP28k9aJlhElR9lJnynaCldpSNeob2PrnhnoMiGAA7drlZdpC4"
export BINANCE_SECRETS_KEY="hplmjruPIXcHAQSC6F4OUPwoJvXfwjTeAeqJQiKAh7xAQC9QbZSo0y3yCI4gtbOH"


# Create the network if we don't have it yet
docker network inspect crypbros >/dev/null 2>&1 || docker network create crypbros

# build the image based on the Dockerfile
docker build -t $IMAGE_NAME -f Dockerfile .

# create the container
docker run --rm --name $IMAGE_NAME -ti \
--mount type=bind,source="$BASE_DIR",target=/app \
--mount type=bind,source="$COMMON_DIR/dataaccess",target=/app/dataaccess \
--mount type=bind,source="$COMMON_DIR/datacollector",target=/app/datacollector \
-p 9600:9000 \
-e DEV=1 \
-e DATABASE_URL=$DATABASE_URL \
-e GOOGLE_APPLICATION_CREDENTIALS=$GOOGLE_APPLICATION_CREDENTIALS \
-e GCP_PROJECT=$GCP_PROJECT \
-e GCP_ZONE=$GCP_ZONE \
-e REDIS_URL=$REDIS_URL \
--network crypbros $IMAGE_NAME