import uuid
import logging
import time

from fastapi import Request, Response, FastAPI


logger = logging.getLogger(__name__)


# https://philstories.medium.com/fastapi-logging-f6237b84ea64


async def log_requests(request: Request, call_next):
    request_uid = uuid.uuid4()
    logger.info(
        f"rid={request_uid} start request path={request.url}\n"
        + f"request body is:{await request.body()}\n"
        + f"request query params:{request.query_params}\n"
        + f"request cookies:{request.cookies}"
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
