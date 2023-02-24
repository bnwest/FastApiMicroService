import uuid
import logging
import time

from fastapi import Request, Response, FastAPI


logger = logging.getLogger(__name__)


# https://philstories.medium.com/fastapi-logging-f6237b84ea64


async def log_requests(request: Request, call_next):
    # https://github.com/tiangolo/fastapi/issues/394
    # the call to "await request.body()" is a problem.
    # the call to log the body works, but the later call
    # to get the body in the endpoint handler hangs.
    # "consuming the body inside of middleware is broadly discouraged by starlette"

    request_uid = uuid.uuid4()
    logger.info(
        f"rid={request_uid} start request",
        extra={
            "url": str(request.url),
            # "body": await request.body(),
            # starlette.datastructures.QueryParams which is ImmutableMultiDict
            # where each key in the ImmutableMultiDict can reference more than one value
            "query_params": {
                key: request.query_params.getlist(key)
                for key in request.query_params.keys()
            },
            "cookies": request.cookies,  # Dict[str, str]
        },
    )
    start_time = time.time()

    response: Response = await call_next(request)

    process_time = (time.time() - start_time) * 1000
    formatted_process_time = "{0:.2f}".format(process_time)
    # response's json is hidden within an async_generator object
    logger.info(
        f"rid={request_uid} completed_in={formatted_process_time}ms status_code={response.status_code}"
    )

    return response


def add_log_requests(app: FastAPI):
    app.middleware("http")(log_requests)
