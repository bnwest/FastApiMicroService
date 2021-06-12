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
