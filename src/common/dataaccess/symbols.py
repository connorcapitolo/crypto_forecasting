import os
from typing import Any, Dict, List
from dataaccess import utils as data_utils
from dataaccess.session import database
from dataaccess.errors import RecordNotFoundError
from log_conf import Logger


async def browse(
    *,
    paginate: bool = True,
    page_number: int = 0,
    page_size: int = 20
) -> List[Dict[str, Any]]:
    """
    Retrieve a list of rows based on filters
    """

    query = """
        select id,name,status,timestamp
        from symbols
    """

    # order by

    # offset/limit
    if paginate:
        query += data_utils.build_pagination(page_number, page_size)

    values = []

    #print("query", query)
    result = await database.fetch_all(query)

    return [prep_data(row) for row in result]


async def get(id: int) -> Dict[str, Any]:
    """
    Retrieve one row based by its id. Return object is a dict. 
    Raises if the record was not found.
    """

    query = """
        select id,name from symbols where id = :id
    """

    values = {
        "id": id
    }

    Logger.logr.info(f"query: {query} values: {values}")
    result = await database.fetch_one(query, values)

    if result is None:
        raise RecordNotFoundError(f"Could not find row with id '{id}'")

    return prep_data(result)


async def get_by_name(name: str) -> Dict[str, Any]:
    """
    Retrieve one row based by its name. Return object is a dict. 
    Raises if the record was not found.
    """

    query = """
        select id,name 
        from symbols
        where 1=1
        and name = :name
    """

    values = {
        "name": name
    }

    result = await database.fetch_one(query, values)

    if result is None:
        raise RecordNotFoundError(f"Could not find row with name '{name}'")

    return prep_data(result)


async def create(*,
                 name: str,
                 id: int = None) -> Dict[str, Any]:
    """
    Create a new row. Returns the created record as a dict.
    """

    # Set the values
    values = {
        "name": name
    }

    # if the id was passed
    if id is not None:
        values["id"] = id

    # Generate the field and values list
    field_list = ", ".join(values.keys())
    param_list = ", ".join(":" + key for key in values.keys())

    result = await database.fetch_one(f"""
        INSERT INTO symbols (
            {field_list}
        ) VALUES (
            {param_list}
        ) RETURNING *;
    """, values=values)

    result = prep_data(result)
    return result


async def update(id: int, status=None, timestamp=None) -> Dict[str, Any]:
    """
    Updates an existing row. Keyword arguments left at None will not be
    changed in the database. Returns the updated record as a dict. Raises if
    the record was not found.
    """

    values = {
        "id": id
    }

    changes: Dict[str, Any] = {
    }

    if status is not None:
        changes["status"] = status

    if timestamp is not None:
        changes["timestamp"] = timestamp

    change_list = ", ".join(key + " = :" + key for key in changes.keys())

    if timestamp is None:
        change_list += ", updated_at = EXTRACT(EPOCH FROM clock_timestamp()) * 1000"
    else:
        change_list += ", updated_at = {}".format(timestamp)
     
    Logger.logr.info(change_list)

    result = await database.fetch_one(f"""
        UPDATE symbols
        SET {change_list}
        WHERE id = :id
        RETURNING *;
    """, values={**values, **changes})

    if result is None:
        raise RecordNotFoundError(f"Could not update row with id '{id}'")

    result = prep_data(result)
    return result


async def get_inconsistent_symbols(timestamp):

    messages = await database.fetch_one(f"""
        SELECT id, name, updated_at
        FROM symbols""")

    _inconsistent_symbols = []
    messages = prep_data(messages)
    # right now, only works for one element, todo: update the format when we have multiple streams

    updated_id = messages.get('updated_at')
    if updated_id is None or updated_id + 60000 < timestamp:
        _inconsistent_symbols.append(messages)
    return _inconsistent_symbols


def prep_data(result) -> Dict[str, Any]:
    if result is None:
        raise ValueError("Tried to prepare null result")

    result = dict(result)
    return result
