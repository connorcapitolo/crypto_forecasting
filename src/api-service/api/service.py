import asyncio
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.staticfiles import StaticFiles

import dataaccess.session as database_session
# the build is happening at the api-service level
from api.routers import symbols

import pandas as pd

from api import model

prefix = "/v1"

# Setup FastAPI app
app = FastAPI(
    title="API Service",
    description="API Service",
    version="v1"
)

# Enable CORSMiddleware
# we want the middleware so the frontend and backend talk from different domains
app.add_middleware(
    CORSMiddleware,
    allow_credentials=False,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# Custom exception hooks
@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "message": str(exc)
        }
    )

# Application start/stop hooks

# we then perform @app.event() which will allow us to connect to the database
@app.on_event("startup")
async def startup():
    # Connect to database
    await database_session.connect()


@app.on_event("shutdown")
async def shutdown():
    # Disconnect from database
    await database_session.disconnect()

# Routes


@app.get(
    "/",
    summary="Index",
    description="Root api"
)
async def get_index():
    return {
        "message": "Welcome to the API Service"
    }


@app.post("/predict")
async def prediction(data: dict):

    lstm_prediction = model.make_prediction()

    # todo: implement historical data in below format (list of dict)
    return {
        "prediction": f'{lstm_prediction:.2f}', 
        "ticker": data["ticker"], 
        "time": data["time"],
        'history': [
            # placeholder, dummy data
            {'date': '2017-01-11', 'high': 116.510002, 'low':115.75}, 
            {'date': '2017-01-12', 'high': 116.860001, 'low':115.809998},
            {'date': '2017-01-13', 'high': 118.160004, 'low':116.470001},
            {'date': '2017-01-17', 'high': 119.43, 'low':117.940002},
            {'date': '2017-01-18', 'high': 119.379997, 'low':118.300003},
            {'date': '2017-01-19', 'high': 119.93, 'low':118.599998},
            {'date': '2017-01-20', 'high': 119.300003, 'low':118.209999},
            {'date': '2017-01-23', 'high': 119.620003, 'low':118.809998},
            {'date': '2017-01-24', 'high': 120.239998, 'low':118.220001},
            {'date': '2017-01-25', 'high': 120.239998, 'low':119.709999},
            {'date': '2017-01-26', 'high': 119.510002, 'low':115.75}, 
            {'date': '2017-01-27', 'high': 118.860001, 'low':115.809998},
            {'date': '2017-01-28', 'high': 118.160004, 'low':116.470001},
            {'date': '2017-01-29', 'high': 119.43, 'low':117.940002},
            {'date': '2017-01-30', 'high': 119.379997, 'low':118.300003},
            {'date': '2017-01-31', 'high': 119.93, 'low':118.599998},
            {'date': '2017-02-01', 'high': 119.300003, 'low':118.209999},
            {'date': '2017-02-02', 'high': 119.620003, 'low':118.809998},
            {'date': '2017-02-03', 'high': 120.239998, 'low':118.220001},
            {'date': '2017-02-04', 'high': 120.239998, 'low':119.709999}
        ]
    }

'''
@app.get(
    "/get_price_history"
)
async def get_price_history(
    symbol: str = Query(...,
                        description="The symbol to get price history for"),
):
# This is what will be used for check if a symbol is already in the table or not, pulled from routers/test.py
    print("get_price_history ...")
    print("symbol:", symbol)

    symbol = symbol.upper()

    # Check if we have the any price history
    try:
        symbol_db = await dataaccess_symbols.get_by_name(name=symbol)
        print(symbol_db)
    except RecordNotFoundError:
        # Add the pair to DB

        # task_h = run_historical.load_price_history(symbol, symbol_db['id'])
        # here, launch the script ? why not ?
        # after in order for the online fetching to pick up on it
        symbol_db = await dataaccess_symbols.create(name=symbol)

        return {
            "task_historical": task_h.id,
            "task_online": task.id
        }

    # Get price history
    return await dataaccess_price_history.browse(name=symbol)
'''

# Additional routers here (reference: https://fastapi.tiangolo.com/tutorial/bigger-applications/#the-main-fastapi)
# With app.include_router() we can add each APIRouter to the main FastAPI application; it will include all the routes from that router as part of it.
# here, we're including the APIRouters from the modules auth and auth_google, as well as the submodule routers/users
# don't have to worry about performance b/c will take microseconds and only occurs at startup
#app.include_router(test.router, prefix=prefix)
app.include_router(symbols.router, prefix=prefix)
