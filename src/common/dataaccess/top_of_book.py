import os
from typing import Any, Dict, List

from dataaccess import utils as data_utils
from dataaccess.session import database
from dataaccess.errors import RecordNotFoundError


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
        select top.id, top.symbol_id, top.best_bid, top.volume_best_bid,
        top.best_ask, top.volume_best_ask, top.time_reporting, top.created_at, 
        top.updated_at
            """
    where = """
        from top_of_book tob 
        inner join symbols s on (tob.symbol_id = s.id)
        where 1=1
    """

    # Where
    if name is not None:
        where += " and s.name='"+name+"'"

    # order by
    order = ""

    # Build select query
    query = select + " " + where + " " + order + \
        data_utils.build_pagination(page_number, page_size)

    print("query", query)
    result = await database.fetch_all(query)

    return [prep_data(row) for row in result]


async def get(id: int) -> Dict[str, Any]:
    """
    Retrieve one row based by its id. Return object is a dict. 
    Raises if the record was not found.
    """

    query = """
        select top.id, top.symbol_id, top.best_bid, top.volume_best_bid,
        top.best_ask, top.volume_best_ask, top.time_reporting, top.created_at, 
        top.updated_at
        from top_of_book top
        inner join symbols s on (top.pair_id = s.symbol_id)
        where top.id = :id
    """

    values = {
        "id": id
    }

    print("query:", query, "values:", values)
    result = await database.fetch_one(query, values)

    if result is None:
        raise RecordNotFoundError(f"Could not find row with id '{id}'")

    return prep_data(result)


async def create(*,
                 symbol_id: int,
                 best_bid: float, 
                 volume_best_bid: float,
                 best_ask: float, 
                 volume_best_ask: float, 
                 time_reporting: float, 
                 id: int = None) -> Dict[str, Any]:
    """
    Create a new row. Returns the created record as a dict.
    """

    # Set the values
    values = {
        "symbol_id": symbol_id,
        "best_bid": best_bid,
        "volume_best_bid": volume_best_bid,
        "best_ask": best_ask,
        "volume_best_ask": volume_best_ask,
        "time_reporting":  time_reporting
    }

    # if the id was passed
    if id is not None:
        values["id"] = id

    # Generate the field and values list
    field_list = ", ".join(values.keys())
    param_list = ", ".join(":" + key for key in values.keys())

    result = await database.fetch_one(f"""
        INSERT INTO top_of_book (
            {field_list}
        ) VALUES (
            {param_list}
        ) RETURNING *;
    """, values=values)

    result = prep_data(result)
    return result


def prep_data(result) -> Dict[str, Any]:
    if result is None:
        raise ValueError("Tried to prepare null result")

    result = dict(result)
    return result

