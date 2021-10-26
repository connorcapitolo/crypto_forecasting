import os
from typing import Any, Dict, List

from dataaccess import utils as data_utils
from dataaccess.session import database
from dataaccess.errors import RecordNotFoundError


async def browse(
    *,
    page_number: int = 0,
    page_size: int = 20
) -> List[Dict[str, Any]]:
    """
    Retrieve a list of rows based on filters
    """

    query = """
        select id,name
        from symbols
    """

    # order by

    # offset/limit
    query += data_utils.build_pagination(page_number, page_size)

    values = []

    print("query", query)
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

    print("query:", query, "values:", values)
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

    print("query:", query, "values:", values)
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


async def update(id: int) -> Dict[str, Any]:
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

    change_list = ", ".join(key + " = :" + key for key in changes.keys())
    change_list += "updated_at = EXTRACT(EPOCH FROM clock_timestamp()) * 1000"

    print(change_list)

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


async def get_inconsistent_symbols():
    result = await database.fetch_one(f"""
        SELECT id, updated_at
        FROM symbols
        WHERE updated_at < EXTRACT(EPOCH FROM clock_timestamp()) * 1000 - 60000;""")
    return result

def prep_data(result) -> Dict[str, Any]:
    if result is None:
        raise ValueError("Tried to prepare null result")

    result = dict(result)
    return result
