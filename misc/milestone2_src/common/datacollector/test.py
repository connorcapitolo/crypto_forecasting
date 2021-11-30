import os
import asyncio
from celery.utils.log import get_task_logger

from datacollector.session import worker, async_task
from dataaccess import symbols as dataaccess_symbols

logger = get_task_logger(__name__)


async def test_worker_task_async(id):
    logger.info("Processing test_worker_task_async with id:"+str(id))

    # await asyncio.sleep(1)

    symbols = await dataaccess_symbols.browse()
    print("symbols:", symbols)


@worker.task(name="test_worker_task")
def test_worker_task(id):
    logger.info("Processing test_worker_task with id:"+str(id))

    # asyncio.run(test_worker_task_async(id))

    # return True

    loop = asyncio.get_event_loop()

    future = asyncio.wait_for(
        test_worker_task_async(id),
        timeout=None,
        loop=loop
    )

    return loop.run_until_complete(future)


@async_task
async def test_training(id):
    logger.info("Processing test_training with id:"+str(id))
    await asyncio.sleep(5)

    symbols = await dataaccess_symbols.browse()
    print("symbols:", symbols)
