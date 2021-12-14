#!/usr/bin/env bash
####### OLD RIGHT ? ####

# The name of the docker images to produce
# source: https://www.baeldung.com/linux/bash-variables-export; CS 107 Lecture 2
# the 'export' command another way of defining a variable. It creates a variable, assigns it a value, and marks it for export to all child processes created from that shell. This is an environment variable.
export IMAGE_NAME="crypbros-worker-service"
export BASE_DIR=$(pwd)
export COMMON_DIR=$(dirname "$(pwd)")/common
export DATABASE_URL="postgres://cryp:bros@crypbrosdb-server:5436/crypbrosdb"
export REDIS_URL="redis://crypbros-redis:6379/0"
export BINANCE_API_KEY=$BINANCE_API_KEY
export BINANCE_SECRET_KEY=$BINANCE_SECRET_KEY