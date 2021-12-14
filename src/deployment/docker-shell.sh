#!/usr/bin/env bash

# exit immediately if a command exits with a non-zero status
set -e

# Define some environment variables
export IMAGE_NAME="crypto-forecasting-deployment"
export BASE_DIR=$(pwd)
export GCP_PROJECT="crypto-forecasting-app" # Change to your GCP Project
export GCP_ZONE="us-central1-a"
export GCS_BUCKET="crypto-forecasting-bucket"
export GOOGLE_APPLICATION_CREDENTIALS=/secrets/deployment.json

# Build the image based on the Dockerfile
docker build -t $IMAGE_NAME -f Dockerfile .

# Run the container
docker run --rm --name $IMAGE_NAME -ti \
-v /var/run/docker.sock:/var/run/docker.sock \
--mount type=bind,source=$BASE_DIR,target=/app \
--mount type=bind,source=$BASE_DIR/../secrets/,target=/secrets \
--mount type=bind,source=$HOME/.ssh,target=/home/app/.ssh \
--mount type=bind,source=$BASE_DIR/../api-service,target=/api-service \
--mount type=bind,source=$BASE_DIR/../common/dataaccess,target=/api-service/dataaccess \
--mount type=bind,source=$BASE_DIR/../common/datacollector,target=/api-service/datacollector \
--mount type=bind,source=$BASE_DIR/../secrets/,target=/api-service/secrets \
--mount type=bind,source=$BASE_DIR/../frontend-react,target=/frontend-react \
--mount type=bind,source=$BASE_DIR/../database-server,target=/database-server \
--mount type=bind,source=$BASE_DIR/../worker-service,target=/worker-service \
--mount type=bind,source=$BASE_DIR/../common/dataaccess,target=/worker-service/dataaccess \
--mount type=bind,source=$BASE_DIR/../common/datacollector,target=/worker-service/datacollector \
--mount type=bind,source=$BASE_DIR/../secrets/,target=/worker-service/secrets \
-e GOOGLE_APPLICATION_CREDENTIALS=$GOOGLE_APPLICATION_CREDENTIALS \
-e GCS_BUCKET=$GCS_BUCKET \
-e GCP_PROJECT=$GCP_PROJECT \
-e GCP_ZONE=$GCP_ZONE $IMAGE_NAME

