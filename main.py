""" Small FastApi micro-service. """

# See:
#      https://fastapi.tiangolo.com
#      https://fastapi.tiangolo.com/tutorial/

import logging
import logging_tree

from fastapi import FastAPI

import middleware
import controllers

DEFAULT_LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stderr",
        },
    },
    "loggers": {
        "": {"level": "INFO", "handlers": ["console"]},
    },
}

logging.config.dictConfig(DEFAULT_LOGGING)

FASTAPI_ENV = os.environ.get("FASTAPI_ENV", "production")

if FASTAPI_ENV == "development":
    # to see the current log config:
    logging_tree.printout()

app = FastAPI()

middleware.add_log_requests(app)
middleware.add_log_exceptions(app)

controllers.mount_controllers(app)
