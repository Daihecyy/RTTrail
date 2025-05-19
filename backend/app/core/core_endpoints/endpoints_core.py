import logging
from os import path
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse

from app.core.core_endpoints import schemas_core
from app.core.utils.config import Settings
from app.dependencies import (
    get_settings,
)
from app.types.module import CoreModule

router = APIRouter(tags=["Core"])

core_module = CoreModule(
    root="",
    tag="Core",
    router=router,
)

rttrail_error_logger = logging.getLogger("rttrail.error")


@router.get(
    "/information",
    response_model=schemas_core.CoreInformation,
    status_code=200,
)
async def read_information(
    settings: Settings = Depends(get_settings),
):
    """
    Return information about rttrail. This endpoint can be used to check if the API is up.
    """

    return schemas_core.CoreInformation(
        ready=True,
        version=settings.RTTRAIL_VERSION,
    )


@router.get(
    "/privacy",
    response_class=FileResponse,
    status_code=200,
)
async def read_privacy():
    """
    Return RTTrail privacy
    """
    # TODO
    return FileResponse("assets/privacy.txt")


@router.get(
    "/terms-and-conditions",
    response_class=FileResponse,
    status_code=200,
)
async def read_terms_and_conditions():
    """
    Return RTTrail terms and conditions pages
    """
    # TODO
    return FileResponse("assets/terms-and-conditions.txt")


@router.get(
    "/support",
    response_class=FileResponse,
    status_code=200,
)
async def read_support():
    """
    Return RTTrail terms and conditions pages
    """
    # TODO
    return FileResponse("assets/support.txt")


@router.get(
    "/security.txt",
    response_class=FileResponse,
    status_code=200,
)
async def read_security_txt():
    """
    Return RTTrail security.txt file
    """
    # TODO
    return FileResponse("assets/security.txt")


@router.get(
    "/.well-known/security.txt",
    response_class=FileResponse,
    status_code=200,
)
async def read_wellknown_security_txt():
    """
    Return RTTrail security.txt file
    """
    # TODO
    return FileResponse("assets/security.txt")


@router.get(
    "/robots.txt",
    response_class=FileResponse,
    status_code=200,
)
async def read_robots_txt():
    """
    Return RTTrail robots.txt file
    """
    # TODO
    return FileResponse("assets/robots.txt")


@router.get(
    "/style/{file}.css",
    response_class=FileResponse,
    status_code=200,
)
async def get_style_file(
    file: str,
):
    """
    Return a style file from the assets folder
    """
    css_dir = "assets/style/"
    css_path = f"{css_dir}{file}.css"

    # Security check (even if FastAPI parsing of path parameters does not allow path traversal)
    if path.commonprefix(
        (path.realpath(css_path), path.realpath(css_dir)),
    ) != path.realpath(css_dir):
        raise HTTPException(status_code=404, detail="File not found")

    if not Path(css_path).is_file():
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(css_path)


@router.get(
    "/favicon.ico",
    response_class=FileResponse,
    status_code=200,
)
async def get_favicon():
    return FileResponse("assets/images/favicon.ico")
