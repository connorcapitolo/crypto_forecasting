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

    except RecordNotFoundError:
    
        symbol_db = await dataaccess_symbols.create(name=symbol)

        return {
            "task_historical": task_h.id,
            "task_online": task.id
        }

    # Get price history
    return await dataaccess_price_history.browse(name=symbol, page_size=1000)


