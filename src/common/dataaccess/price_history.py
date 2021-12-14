import os
from typing import Any, Dict, List

from dataaccess import utils as data_utils
from dataaccess.session import database
from dataaccess.errors import RecordNotFoundError
from log_conf import Logger

async def browse(
    *,
    name: str = None,
    page_number: int = 0,
    page_size: int = 20
) -> List[Dict[str, Any]]:
    """
    Retrieve a list of rows based on filters
    """

    select = """
        select ph.id,s.name,ph.open_time,ph.open_price,ph.high_price,ph.low_price,
        ph.close_price,ph.volume_traded,ph.close_time,
        ph.quote_asset_volume,ph.number_of_trades,
        ph.taker_buy_base_asset_volume,ph.taker_buy_quote_asset_volume
    """
    where = """
        from price_history ph 
        inner join symbols s on (ph.symbol_id = s.id)
        where 1=1
    """

    # Where
    if name is not None:
        where += " and s.name='"+name+"'"

    # order by
    order = "order by ph.close_time desc"

    # Build select query
    query = select + " " + where + " " + order + \
        data_utils.build_pagination(page_number, page_size)

    Logger.logr.info(f"query {query}")
    result = await database.fetch_all(query)

    return [prep_data(row) for row in result]

async def get_by_symbol_id(symbol_id: int, page_size=20) -> Dict[str, Any]:
    """
    Retrieve one row based by its id. Return object is a dict. 
    Raises if the record was not found.
    """

    query = """
        select ph.symbol_id,s.name,ph.open_time,ph.open_price,ph.high_price,ph.low_price,
        ph.close_price,ph.volume_traded,ph.close_time,
        ph.quote_asset_volume,ph.number_of_trades,
        ph.taker_buy_base_asset_volume,ph.taker_buy_quote_asset_volume
        from price_history ph
        inner join symbols s on (ph.symbol_id = s.id)
        where ph.symbol_id = :symbol_id
    """

    order = "order by open_time desc"

    # Build select query
    query = query + " " + order + " limit " + str(page_size)

    values = {
        "symbol_id": symbol_id
    }

    result = await database.fetch_all(query, values)

    if result is None:
        raise RecordNotFoundError(f"Could not find row with id '{id}'")

    return [prep_data(row) for row in result]


async def get(id: int, page_size=20) -> Dict[str, Any]:
    """
    Retrieve one row based by its id. Return object is a dict. 
    Raises if the record was not found.
    """

    query = """
        select ph.id,s.name,ph.open_time,ph.open_price,ph.high_price,ph.low_price,
        ph.close_price,ph.volume_traded,ph.close_time,
        ph.quote_asset_volume,ph.number_of_trades,
        ph.taker_buy_base_asset_volume,ph.taker_buy_quote_asset_volume
        from price_history ph
        inner join symbols s on (ph.symbol_id = s.id)
        where ph.id = :id
    """

    values = {
        "id": id
    }

    Logger.logr.info(f"query: {query} values: {values}")
    result = await database.fetch_one(query, values)

    if result is None:
        raise RecordNotFoundError(f"Could not find row with id '{id}'")

    return prep_data(result)


async def create(*,
                 symbol_id: int,
                 open_time: int,
                 open_price: float,
                 high_price: float,
                 low_price: float,
                 close_price: float,
                 volume_traded: float,
                 close_time: int,
                 quote_asset_volume: float,
                 number_of_trades: int,
                 taker_buy_base_asset_volume: float,
                 taker_buy_quote_asset_volume: float,
                 id: int = None) -> Dict[str, Any]:
    """
    Create a new row. Returns the created record as a dict.
    """

    # Set the values
    values = {
        "symbol_id": symbol_id,
        "open_time": open_time,
        "open_price": open_price,
        "high_price": high_price,
        "low_price": low_price,
        "close_price": close_price,
        "volume_traded": volume_traded,
        "close_time": close_time,
        "quote_asset_volume": quote_asset_volume,
        "number_of_trades": number_of_trades,
        "taker_buy_base_asset_volume": taker_buy_base_asset_volume,
        "taker_buy_quote_asset_volume": taker_buy_quote_asset_volume
    }

    # if the id was passed
    if id is not None:
        values["id"] = id

    # Generate the field and values list
    field_list = ", ".join(values.keys())
    param_list = ", ".join(":" + key for key in values.keys())

    query = f"""
        INSERT INTO price_history (
            {field_list}
        ) VALUES (
            {param_list}
        ) RETURNING *;
    """

    result = await database.fetch_one(query, values=values)

    result = prep_data(result)
    return result


async def update(id: int,
                 open_time: int,
                 open_price: float,
                 high_price: float,
                 low_price: float,
                 close_price: float,
                 volume_traded: float,
                 close_time: int,
                 quote_asset_volume: float,
                 number_of_trades: int,
                 taker_buy_base_asset_volume: float,
                 taker_buy_quote_asset_volume: float) -> Dict[str, Any]:
    """
    Updates an existing row. Keyword arguments left at None will not be
    changed in the database. Returns the updated record as a dict. Raises if
    the record was not found.
    """

    values = {
        "id": id,
        "open_time": open_time,
        "open_price": open_price,
        "high_price": high_price,
        "low_price": low_price,
        "close_price": close_price,
        "volume_traded": volume_traded,
        "close_time": close_time,
        "quote_asset_volume": quote_asset_volume,
        "number_of_trades": number_of_trades,
        "taker_buy_base_asset_volume": taker_buy_base_asset_volume,
        "taker_buy_quote_asset_volume": taker_buy_quote_asset_volume
    }

    changes: Dict[str, Any] = {
    }

    change_list = ", ".join(key + " = :" + key for key in changes.keys())
    change_list += ", updated_at = EXTRACT(EPOCH FROM clock_timestamp()) * 1000"

    Logger.logr.info(change_list)

    result = await database.fetch_one(f"""
        UPDATE price_history
        SET {change_list}
        WHERE id = :id
        RETURNING *;
    """, values={**values, **changes})

    if result is None:
        raise RecordNotFoundError(f"Could not update row with id '{id}'")

    result = prep_data(result)
    return result


def prep_data(result) -> Dict[str, Any]:
    if result is None:
        raise ValueError("Tried to prepare null result")

    result = dict(result)
    return result
