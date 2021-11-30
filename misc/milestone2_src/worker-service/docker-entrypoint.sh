#!/bin/bash

echo "Container is running!!!"


worker() {
    celery -A worker.service worker --loglevel=debug -B "$@"
}

worker_production() {
    pipenv run celery -A worker.service worker --loglevel=info --concurrency=8
}


export -f worker

echo -en "\033[92m
The following commands are available:
    worker
        Run the Celery Worker Service
\033[0m
"

case "${MODE}" in
    worker)
        worker_production
        ;;
    scheduler)
        scheduler_production
        ;;
    *)
        pipenv shell
        ;;
esac
