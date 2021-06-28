import os
import requests
import json


# export FASTAPI_ROOT="http://fastapi-micro-service:8000"
FASTAPI_ROOT = os.environ.get("FASTAPI_ROOT")


def test_get_items_no_query():
    item_id = 42
    endpoint_url = f"{FASTAPI_ROOT}/items/{item_id}"
    response = requests.get(endpoint_url)
    assert response.status_code == 200
    #     return {"item_id": item_id, "q": q}
    response_json = response.json()
    assert isinstance(response_json, dict)
    assert "item_id" in response_json
    assert response_json['item_id'] == item_id
    assert "q" in response_json
    assert response_json['q'] is None


def test_get_items_query_1():
    item_id = 42
    q = "NeverSendToKnowForWhomTheBellTolls"
    endpoint_url = f"{FASTAPI_ROOT}/items/{item_id}?q={q}"
    response = requests.get(endpoint_url)
    assert response.status_code == 200
    response_json = response.json()
    assert isinstance(response_json, dict)
    assert "item_id" in response_json
    assert response_json['item_id'] == item_id
    assert "q" in response_json
    assert response_json['q'] == q


def test_get_items_query_2():
    item_id = 42
    q = "NeverSendToKnowForWhomTheBellTolls"
    query_params = {'q': q}
    endpoint_url = f"{FASTAPI_ROOT}/items/{item_id}"
    response = requests.get(endpoint_url, params=query_params)
    assert response.status_code == 200
    response_json = response.json()
    assert isinstance(response_json, dict)
    assert "item_id" in response_json
    assert response_json['item_id'] == item_id
    assert "q" in response_json
    assert response_json['q'] == q


def test_get_items_json():
    item_id = 42
    q = "NeverSendToKnowForWhomTheBellTolls"
    json_params = {'q': q}
    endpoint_url = f"{FASTAPI_ROOT}/items/{item_id}"
    response = requests.get(endpoint_url, json=json_params)
    assert response.status_code == 200
    response_json = response.json()
    print(f"response json is:\n{response_json}")
    assert isinstance(response_json, dict)
    assert "item_id" in response_json
    assert response_json['item_id'] == item_id
    assert "q" in response_json
    # Flask can take a json payload on GET, while FastApi will not
    assert response_json['q'] is None


def test_get_items_data():
    item_id = 42
    q = "NeverSendToKnowForWhomTheBellTolls"
    json_params = {'q': q}
    endpoint_url = f"{FASTAPI_ROOT}/items/{item_id}"
    response = requests.get(endpoint_url, data=json.dumps(json_params))
    assert response.status_code == 200
    response_json = response.json()
    print(f"response json is:\n{response_json}")
    assert isinstance(response_json, dict)
    assert "item_id" in response_json
    assert response_json['item_id'] == item_id
    assert "q" in response_json
    # Flask can take a json payload on GET, while FastApi will not
    assert response_json['q'] is None
