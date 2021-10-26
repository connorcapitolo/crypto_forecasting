
from celery import Celery
from celery.signals import worker_process_init, worker_process_shutdown, worker_ready, worker_shutdown
import dataaccess.session as database_session
import os
import asyncio
import functools
import nest_asyncio
nest_asyncio.apply()


REDIS_URL = os.environ["REDIS_URL"]

# Setup the celery worker
#worker = Celery('worker', broker=REDIS_URL)
worker = Celery('worker', broker=REDIS_URL, include=[
    "datacollector.test",
    "datacollector.extract_data"
])


@worker_process_init.connect
def worker_setup(*args, **kwargs):
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(database_session.connect())


@worker_process_shutdown.connect
def worker_teardown(*args, **kwargs):
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(database_session.disconnect())


@worker_ready.connect
def worker_start(sender, **k):
    print("Worker started...")
    sender.app.send_task(
        'datacollector.extract_data.start_multiple_websocket', args=[])


@worker_shutdown.connect
def worker_stop(sender, **k):
    print("Worker stoping...")
    sender.app.send_task(
        'datacollector.extract_data.stop_multiple_websocket', args=[])


def async_task(task, name="", timeout=None):
    @worker.task(name=name)
    @functools.wraps(task)
    def wrapper(*args, **kwargs):
        loop = asyncio.get_event_loop()

        future = asyncio.wait_for(
            task(*args, **kwargs),
            timeout=timeout,
            loop=loop
        )

        return loop.run_until_complete(future)

    return wrapper
