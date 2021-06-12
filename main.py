""" Small FastApi micro-service. """

# See: https://fastapi.tiangolo.com

from fastapi import FastAPI

from controllers import mount_controllers


app = FastAPI()

mount_controllers(app)
