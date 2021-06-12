""" Small FastApi micro-service. """

# See: https://fastapi.tiangolo.com

from typing import Optional

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class Item(BaseModel):
    name: str
    price: float
    is_offer: Optional[bool] = None


@app.get("/")
async def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
async def read_item(item_id: int, q: Optional[str] = None):
    return {"item_id": item_id, "q": q}


@app.put("/items/{item_id}")
async def update_item(item_id: int, item: Item):
    return {"item_name": item.name, "item_id": item_id}


# Mine:

import platform
import fastapi
import pydantic
import uvicorn


class VersionsResult(pydantic.BaseModel):
    python: str
    fastapi: str
    pydantic: str
    uvicorn: str


async def get_versions() -> VersionsResult:
    result = VersionsResult(
        python=platform.python_version(),
        fastapi=fastapi.__version__,
        pydantic=pydantic.version.VERSION,
        uvicorn=uvicorn.__version__,
    )
    return result


def mount(app: fastapi.FastAPI) -> None:
    app.get("/versions", response_model=VersionsResult)(get_versions)


mount(app)
