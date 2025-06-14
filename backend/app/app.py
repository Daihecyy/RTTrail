"""File defining the Metadata. And the basic functions creating the database tables and calling the router"""

import logging
import uuid
from collections.abc import AsyncGenerator, Awaitable, Callable
from contextlib import asynccontextmanager
from pathlib import Path

import alembic.command as alembic_command
import alembic.config as alembic_config
import alembic.migration as alembic_migration
from fastapi import FastAPI, HTTPException, Request, Response, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.routing import APIRoute
from sqlalchemy.engine import Connection, Engine
from sqlalchemy.orm import Session

from app.api import api_router
from app.core.utils.config import Settings
from app.core.utils.log import LogConfig
from app.dependencies import (
    init_and_get_db_engine,
)
from app.types.exceptions import ContentHTTPException
from app.types.sqlalchemy import Base
from app.utils import initialization


# NOTE: We can not get loggers at the top of this file like we do in other files
# as the loggers are not yet initialized


def get_alembic_config(connection: Connection) -> alembic_config.Config:
    """
    Return the alembic configuration object in a synchronous way
    """
    alembic_cfg = alembic_config.Config("alembic.ini")
    alembic_cfg.attributes["connection"] = connection

    return alembic_cfg


def get_alembic_current_revision(connection: Connection) -> str | None:
    """
    Return the current revision of the database in a synchronous way

    NOTE: SQLAlchemy does not support `Inspection on an AsyncConnection`. If you have an AsyncConnection, the call to this method must be wrapped in a `run_sync` call to obtain a Connection.
    See https://alembic.sqlalchemy.org/en/latest/cookbook.html#programmatic-api-use-connection-sharing-with-asyncio for more information.
        Exemple usage:
        ```python
        async with engine.connect() as conn:
            await conn.run_sync(run_alembic_upgrade)
        ```
    """

    context = alembic_migration.MigrationContext.configure(connection)
    return context.get_current_revision()


def stamp_alembic_head(connection: Connection) -> None:
    """
    Stamp the database with the latest revision in a synchronous way

    NOTE: SQLAlchemy does not support `Inspection on an AsyncConnection`. If you have an AsyncConnection, the call to this method must be wrapped in a `run_sync` call to obtain a Connection.
    See https://alembic.sqlalchemy.org/en/latest/cookbook.html#programmatic-api-use-connection-sharing-with-asyncio for more information.
        Exemple usage:
        ```python
        async with engine.connect() as conn:
            await conn.run_sync(run_alembic_upgrade)
        ```
    """
    alembic_cfg = get_alembic_config(connection)
    alembic_command.stamp(alembic_cfg, "head")


def run_alembic_upgrade(connection: Connection) -> None:
    """
    Run the alembic upgrade command to upgrade the database to the latest version (`head`) in a synchronous way

    WARNING: SQLAlchemy does not support `Inspection on an AsyncConnection`. The call to Alembic must be wrapped in a `run_sync` call.
    See https://alembic.sqlalchemy.org/en/latest/cookbook.html#programmatic-api-use-connection-sharing-with-asyncio for more information.

    NOTE: SQLAlchemy does not support `Inspection on an AsyncConnection`. If you have an AsyncConnection, the call to this method must be wrapped in a `run_sync` call to obtain a Connection.
    See https://alembic.sqlalchemy.org/en/latest/cookbook.html#programmatic-api-use-connection-sharing-with-asyncio for more information.
        Exemple usage:
        ```python
        async with engine.connect() as conn:
            await conn.run_sync(run_alembic_upgrade)
        ```
    """

    alembic_cfg = get_alembic_config(connection)

    alembic_command.upgrade(alembic_cfg, "head")


def update_db_tables(
    sync_engine: Engine,
    rttrail_error_logger: logging.Logger,
    drop_db: bool = False,
) -> None:
    """
    If the database is not initialized, create the tables and stamp the database with the latest revision.
    Otherwise, run the alembic upgrade command to upgrade the database to the latest version (`head`).

    if drop_db is True, we will drop all tables before creating them again

    This method requires a synchronous engine
    """

    try:
        # We have an Engine, we want to acquire a Connection
        with sync_engine.begin() as conn:
            if drop_db:
                initialization.drop_db_sync(conn)

            alembic_current_revision = get_alembic_current_revision(conn)

            if alembic_current_revision is None:
                # We generate the database using SQLAlchemy
                # in order not to have to run all migrations one by one
                # See https://alembic.sqlalchemy.org/en/latest/cookbook.html#building-an-up-to-date-database-from-scratch
                rttrail_error_logger.info(
                    "Startup: Database tables not created yet, creating them",
                )

                # Create all tables
                Base.metadata.create_all(conn)
                # We stamp the database with the latest revision so that
                # alembic knows that the database is up to date
                stamp_alembic_head(conn)
            else:
                rttrail_error_logger.info(
                    f"Startup: Database tables already created (current revision: {alembic_current_revision}), running migrations",
                )
                run_alembic_upgrade(conn)

            rttrail_error_logger.info("Startup: Database tables updated")
    except Exception as error:
        rttrail_error_logger.fatal(
            f"Startup: Could not create tables in the database: {error}",
        )
        raise


def use_route_path_as_operation_ids(app: FastAPI) -> None:
    """
    Simplify operation IDs so that generated API clients have simpler function names.

    Theses names may be used by API clients to generate function names.
    The operation_id will have the format "method_path", like "get_users_me".

    See https://fastapi.tiangolo.com/advanced/path-operation-advanced-configuration/
    """
    for route in app.routes:
        if isinstance(route, APIRoute):
            # The operation_id should be unique.
            # It is possible to set multiple methods for the same endpoint method but it's not considered a good practice.
            method = "_".join(route.methods)
            route.operation_id = method.lower() + route.path.replace("/", "_")


def init_db(
    settings: Settings,
    rttrail_error_logger: logging.Logger,
    drop_db: bool = False,
) -> None:
    """
    Init the database by creating the tables and adding the necessary groups

    The method will use a synchronous engine to create the tables and add the groups
    """
    # Initialize the sync engine
    sync_engine = initialization.get_sync_db_engine(settings=settings)

    # Update database tables
    update_db_tables(
        sync_engine=sync_engine,
        rttrail_error_logger=rttrail_error_logger,
        drop_db=drop_db,
    )
    with Session(sync_engine) as db:
        initialization.init_superadmin(db=db)


# We wrap the application in a function to be able to pass the settings and drop_db parameters
# The drop_db parameter is used to drop the database tables before creating them again
def get_application(settings: Settings, drop_db: bool = False) -> FastAPI:
    # Initialize loggers
    LogConfig().initialize_loggers(settings=settings)

    rttrail_access_logger = logging.getLogger("rttrail.access")
    rttrail_security_logger = logging.getLogger("rttrail.security")
    rttrail_error_logger = logging.getLogger("rttrail.error")

    # Create folder for calendars if they don't already exists
    Path("data/ics/").mkdir(parents=True, exist_ok=True)
    Path("data/core/").mkdir(parents=True, exist_ok=True)

    # Creating a lifespan which will be called when the application starts then shuts down
    # https://fastapi.tiangolo.com/advanced/events/
    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncGenerator:
        yield
        rttrail_error_logger.info("Shutting down")

    # Initialize app
    app = FastAPI(
        title="rttrail",
        version=settings.RTTRAIL_VERSION,
        lifespan=lifespan,
    )
    app.include_router(api_router)
    use_route_path_as_operation_ids(app)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    if settings.RTTRAIL_INIT_DB:
        init_db(
            settings=settings,
            rttrail_error_logger=rttrail_error_logger,
            drop_db=drop_db,
        )
    else:
        rttrail_error_logger.info("Database initialization skipped")

    # We need to init the database engine to be able to use it in dependencies
    init_and_get_db_engine(settings)

    @app.middleware("http")
    async def logging_middleware(
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        """
        This middleware is called around each request.
        It logs the request and inject a unique identifier in the request that should be used to associate logs saved during the request.
        """
        # We use a middleware to log every request
        # See https://fastapi.tiangolo.com/tutorial/middleware/

        # We generate a unique identifier for the request and save it as a state.
        # This identifier will allow combining logs associated with the same request
        # https://www.starlette.io/requests/#other-state
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id

        # This should never happen, but we log it just in case
        if request.client is None:
            rttrail_security_logger.warning(
                f"Client information not available for {request.url.path}",
            )
            raise HTTPException(status_code=400, detail="No client information")

        ip_address = request.client.host
        port = request.client.port
        client_address = f"{ip_address}:{port}"

        process = True
        if process:
            response = await call_next(request)

            rttrail_access_logger.info(
                f'{client_address} - "{request.method} {request.url.path}" {response.status_code} ({request_id})',
            )
        else:
            response = Response(status_code=429, content="Too Many Requests")
        return response

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request,
        exc: RequestValidationError,
    ):
        # We use a Debug logger to log the error as personal data may be present in the request
        rttrail_error_logger.debug(
            f"Validation error: {exc.errors()} ({request.state.request_id})",
        )

        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=jsonable_encoder({"detail": exc.errors(), "body": exc.body}),
        )

    @app.exception_handler(ContentHTTPException)
    async def auth_exception_handler(
        request: Request,
        exc: ContentHTTPException,
    ):
        return JSONResponse(
            status_code=exc.status_code,
            content=jsonable_encoder(exc.content),
            headers=exc.headers,
        )

    return app
