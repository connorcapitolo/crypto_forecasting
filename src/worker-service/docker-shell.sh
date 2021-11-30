#!/bin/bash

set -e

# Read the settings file
#source ./env.dev
export IMAGE_NAME="crypbros-worker-service"
export BASE_DIR=$(pwd)
export COMMON_DIR=$(dirname "$(pwd)")/common
export DATABASE_URL="postgres://cryp:bros@crypbrosdb-server:5436/crypbrosdb"
export BINANCE_API_KEY="RLis1zPSdrqFz1uP28k9aJlhElR9lJnynaCldpSNeob2PrnhnoMiGAA7drlZdpC4"
export BINANCE_SECRETS_KEY="hplmjruPIXcHAQSC6F4OUPwoJvXfwjTeAeqJQiKAh7xAQC9QbZSo0y3yCI4gtbOH"

# Create the network if we don't have it yet
docker network inspect crypbros >/dev/null 2>&1 || docker network create crypbros

# Build Image
docker build -t $IMAGE_NAME -f Dockerfile .

# Run Container
docker run --rm --name $IMAGE_NAME -ti \
--mount type=bind,source="$BASE_DIR",target=/app \
--mount type=bind,source="$COMMON_DIR/dataaccess",target=/app/dataaccess \
--mount type=bind,source="$COMMON_DIR/datacollector",target=/app/datacollector \
-e DEV=1 \
-e DATABASE_URL=$DATABASE_URL \
-e GOOGLE_APPLICATION_CREDENTIALS=$GOOGLE_APPLICATION_CREDENTIALS \
-e GCP_PROJECT=$GCP_PROJECT \
-e GCP_ZONE=$GCP_ZONE \
-e BINANCE_API_KEY=$BINANCE_API_KEY \
-e BINANCE_SECRETS_KEY=$BINANCE_SECRETS_KEY \
--network crypbros $IMAGE_NAME