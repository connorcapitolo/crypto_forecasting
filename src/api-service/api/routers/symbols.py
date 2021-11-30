from fastapi import APIRouter

from api.schemas import Symbol
from dataaccess import symbols as dataaccess_symbols

router = APIRouter()


@router.post("/symbol")
async def symbol_create(
    symbol: Symbol
):

    symbol_db = await dataaccess_symbols.create(name=symbol.symbol)

    return symbol_db
