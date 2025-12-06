from datetime import datetime
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.gzip import GZipMiddleware
from contextlib import asynccontextmanager
from src.database import (
    sessionmanager_local,
    Base,
)
from src.routes.base import base_route
from src.routes.employee import employee_route
from src.routes.shift import shift_route
from zoneinfo import ZoneInfo


def get_berlin_time():
    return datetime.now(ZoneInfo("Europe/Berlin"))


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    https://fastapi.tiangolo.com/advanced/events/
    """

    # Startup

    # DB - Tables
    engine = sessionmanager_local.get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    # Shutdown

    # # DB Sessions schließen
    if sessionmanager_local._engine is not None:
        await sessionmanager_local.close()


### APP INIT
app = FastAPI(lifespan=lifespan)


### MIDDLEWARE
app.add_middleware(GZipMiddleware, minimum_size=1000)


@app.middleware("http")
async def add_current_time(request: Request, call_next):
    request.state.current_time = get_berlin_time()
    response = await call_next(request)
    return response


### ROUTES
app.include_router(base_route)
app.include_router(employee_route)
app.include_router(shift_route)


### ERRORS
@app.exception_handler(404)
async def not_found_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=404,
        content={
            "detail": f"Route '{request.url.path}' existiert nicht - (Error: {exc.detail})"
        },
    )
