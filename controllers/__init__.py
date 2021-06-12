from fastapi import FastAPI

from .hello import mount as mount_hello
from .versions import mount as mount_versions
from .items import mount as mount_items


__all__ = ["mount_controllers"]


def mount_controllers(app: FastAPI) -> None:
    mount_hello(app)
    mount_versions(app)
    mount_items(app)
