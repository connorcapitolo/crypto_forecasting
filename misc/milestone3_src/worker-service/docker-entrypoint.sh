#!/bin/bash

echo "Container is running!!!"


worker() {
    python -m worker.service_david
}

worker_production() {
    pipenv run python -m worker.service_david
}


export -f worker
export -f worker_production
# pipenv install binance
echo -en "\033[92m
The following commands are available:
    worker
        Run the Worker Service
\033[0m
"

if [ "${DEV}" = 1 ]; then
  pipenv shell
else
  worker_production
fi
