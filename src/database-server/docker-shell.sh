#!/bin/bash

set -e

# Create the network if we don't have it yet
docker network inspect crypbros >/dev/null 2>&1 || docker network create crypbros

# Run Postgres DB and DBMate
docker-compose run --rm --service-ports crypbrosdb-client
