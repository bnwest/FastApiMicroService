from fastapi import FastAPI

from typing import Dict


async def read_root() -> Dict:
    return {"Hello": "World"}


def mount(app: FastAPI) -> None:
    app.get("/")(read_root)
