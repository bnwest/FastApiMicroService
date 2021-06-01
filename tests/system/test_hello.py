import os
import requests

# export FASTAPI_ROOT="http://fastapi-micro-service:8000"
# export FASTAPI_ROOT="http://127.0.0.1:8000"
FASTAPI_ROOT = os.environ.get("FASTAPI_ROOT")


def test_hello_world():
    endpoint_url = f"{FASTAPI_ROOT}/"
    response = requests.get(endpoint_url)
    assert response.status_code == 200
    response_json = response.json()
    assert isinstance(response_json, dict)
    assert "Hello" in response_json
    assert response_json["Hello"] == "World"
