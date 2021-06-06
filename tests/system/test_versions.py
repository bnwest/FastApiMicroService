import os
import requests

# export FASTAPI_ROOT="http://fastapi-micro-service:8000"
FASTAPI_ROOT = os.environ.get("FASTAPI_ROOT")


def test_versions():
    endpoint_url = f"{FASTAPI_ROOT}/versions"
    response = requests.get(endpoint_url)
    assert response.status_code == 200
    response_json = response.json()
    assert isinstance(response_json, dict)
    assert "python" in response_json
    assert "fastapi" in response_json
    assert "pydantic" in response_json
    assert "uvicorn" in response_json
