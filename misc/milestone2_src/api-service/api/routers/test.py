from os import name
from fastapi import APIRouter, Depends, Path, Query

from api.errors import AccessDeniedError
from datacollector import test
from dataaccess import symbols as dataaccess_symbols
from dataaccess import price_history as dataaccess_price_history
from dataaccess.errors import RecordNotFoundError
from datacollector import extract_data

router = APIRouter()


@router.get(
    "/test_route"
)
async def test_route():
    print("test_route ...")

    # Call a celery task
    task = test.test_worker_task.delay(id=1234)

    return {
        "task": task.id
    }


@router.get(
    "/add_streams"
)
async def add_streams():
    print("add_streams ...")

    # Call a celery task
    task = extract_data.add_streams.delay()

    return {
        "task": task.id
    }


@router.get(
    "/start_online"
)
async def start_online():
    print("start_online ...")

    # Call a celery task
    task = extract_data.start_multiple_websocket.delay()

    return {
        "task": task.id
    }


@router.get(
    "/add_online"
)
async def add_online():
    print("add_online ...")

    # Call a celery task
    task = extract_data.add_multiple_websocket.delay()

    return {
        "task": task.id
    }


@router.get(
    "/stop_online"
)
async def stop_online():
    print("stop_online ...")

    # Call a celery task
    task = extract_data.stop_multiple_websocket.delay()

    return {
        "task": task.id
    }


@router.get(
    "/test_training"
)
async def test_training():
    print("test_training ...")

    # Call a celery task
    task = test.test_training.delay(id=3456)

    return {
        "task": task.id
    }


@router.get(
    "/get_price_history"
)
async def get_price_history(
    symbol: str = Query(...,
                        description="The symbol to get price history for"),
):
    print("get_price_history ...")
    print("symbol:", symbol)

    symbol = symbol.upper()

    # Check if we have the any price history
    try:
        symbol_db = await dataaccess_symbols.get_by_name(name=symbol)
        print(symbol_db)
    except RecordNotFoundError:
        # Add the pair to DB
        # add the historical fetch + update every minute
        symbol_db = await dataaccess_symbols.create(name=symbol)
        
        task_h = extract_data.load_price_history.delay(symbol, symbol_db['id'])


        return {
            "task_historical": task_h.id,
            "task_online": task.id
        }

    # Get price history
    return await dataaccess_price_history.browse(name=symbol)


@router.get(
    "/load_price_history"
)
async def load_price_history(
    symbol: str = Query(...,
                        description="The symbol to get price history for"),
):
    print("load_price_history ...")
    print("symbol:", symbol)

    symbol = symbol.upper()

    # Check if we have the any price history
    try:
        symbol_db = await dataaccess_symbols.get_by_name(name=symbol)
        print(symbol_db)

        task = extract_data.load_price_history.delay(
            symbol=symbol, symbol_id=symbol_db["id"])

        return {
            "task": task.id
        }

    except RecordNotFoundError:
        return {
            "Symbol: {} does not exist..., use get price history in order to fetch historical data".format(symbol)
        }
