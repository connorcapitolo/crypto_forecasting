import asyncio
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.staticfiles import StaticFiles

import dataaccess.session as database_session
# the build is happening at the api-service level
from api.routers import symbols
from api.tracker import TrackerService

# https: // stackoverflow.com/questions/15727420/using-logging-in-multiple-modules
from log_conf import Logger

# Initialize Tracker Service
tracker_service = TrackerService()

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
    # start tracking models
    asyncio.create_task(tracker_service.track())
    Logger.logr.info("Starting tracker service")


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
    

# Additional routers here (reference: https://fastapi.tiangolo.com/tutorial/bigger-applications/#the-main-fastapi)
# With app.include_router() we can add each APIRouter to the main FastAPI application; it will include all the routes from that router as part of it.
# here, we're including the APIRouters from the modules auth and auth_google, as well as the submodule routers/users
# don't have to worry about performance b/c will take microseconds and only occurs at startup
#app.include_router(test.router, prefix=prefix)
app.include_router(symbols.router, prefix=prefix)
