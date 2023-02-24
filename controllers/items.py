from fastapi import FastAPI, Query
import pydantic

from typing import Optional, Dict


class Item(pydantic.BaseModel):
    name: str
    price: float
    is_offer: Optional[bool] = None


async def read_item(
    item_id: int,
    # q: Optional[str] = None,  # by default parameters are assumed to be query parameters
    q: Optional[str] = Query(None, title="q is for query parameter."),
) -> Dict:
    return {"item_id": item_id, "q": q}


async def update_item(
    item_id: int,
    item: Item
) -> Dict:
    return {"item_id": item_id, "item": item}


def mount(app: FastAPI) -> None:
    app.get("/items/{item_id}")(read_item)
    app.put("/items/{item_id}")(update_item)
