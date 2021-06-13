import logging

from fastapi import Request, Response, FastAPI
from fastapi.responses import JSONResponse


logger = logging.getLogger(__name__)


async def log_exceptions(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception as exc:
        logger.exception(
            f"Encountered unexpected error: {type(exc).__name__}",
            exc_info=True,
        )
        content = {"message": "Internal Server Error"}
        return JSONResponse(status_code=500, content=content)


def add_log_exceptions(app: FastAPI):
    app.middleware("http")(log_exceptions)
