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


def test_put_item_query():
    item_id = 42
    item = {
        "name": "John Doe",
        "price": 2.99,
        "is_offer": True,
    }
    endpoint_url = f"{FASTAPI_ROOT}/items/{item_id}"
    response = requests.put(endpoint_url, params=item)
    # PUT /items/42?name=John+Doe&price=2.99&is_offer=True
    assert response.status_code == 422  # 422
    # if parameter is not a singular type, FastApi expects a Pyndatic model in the request body.
    # if parameter is a singular type, FastApi expects a query parameter
    #   which can be made explicit via ... q: str = fastapi.Query(...)
    #   which can be overriden via     ... q: str = fastapi.Body(...)


def test_put_item_json():
    item_id = 42
    item = {
        "name": "John Doe",
        "price": 2.99,
        "is_offer": True,
    }
    endpoint_url = f"{FASTAPI_ROOT}/items/{item_id}"
    response = requests.put(endpoint_url, json=item)
    assert response.status_code == 200
    response_json = response.json()
    assert isinstance(response_json, dict)
    assert "item_id" in response_json
    assert response_json["item_id"] == item_id
    assert "item" in response_json
    assert "name" in response_json['item']
    assert response_json["item"]["name"] == item["name"]
    assert "price" in response_json['item']
    assert response_json["item"]["price"] == item["price"]
    assert "is_offer" in response_json['item']
    assert response_json["item"]["is_offer"] == item["is_offer"]


def test_put_item_json_2():
    item_id = 42
    item = {
        "name": "John Doe",
        "price": 2.99,
        "is_offer": True,
    }
    endpoint_url = f"{FASTAPI_ROOT}/items/{item_id}"
    # what you do when there are multiple input Pyndatic models ... fails for one though.
    request_payload = {
        "item": item,
        # "user": user,
    }
    response = requests.put(endpoint_url, json=request_payload)
    assert response.status_code == 422
    # FastAPi can handle the above via ... item: Item = fastapi.Body(..., embed=True)


def test_put_item_data():
    item_id = 42
    item = {
        "name": "John Doe",
        "price": 2.99,
        "is_offer": True,
    }
    endpoint_url = f"{FASTAPI_ROOT}/items/{item_id}"
    response = requests.put(endpoint_url, data=json.dumps(item))
    assert response.status_code == 200
    response_json = response.json()
    assert isinstance(response_json, dict)
    assert "item_id" in response_json
    assert response_json["item_id"] == item_id
    assert "item" in response_json
    assert "name" in response_json['item']
    assert response_json["item"]["name"] == item["name"]
    assert "price" in response_json['item']
    assert response_json["item"]["price"] == item["price"]
    assert "is_offer" in response_json['item']
    assert response_json["item"]["is_offer"] == item["is_offer"]


def test_put_item_data_2():
    item_id = 42
    item = {
        "name": "John Doe",
        "price": 2.99,
        "is_offer": True,
    }
    endpoint_url = f"{FASTAPI_ROOT}/items/{item_id}"
    # what you do when there are multiple input Pyndatic models ... fails for one though.
    request_payload = {
        "item": item
        # "user": user,
    }
    response = requests.put(endpoint_url, data=json.dumps(request_payload))
    assert response.status_code == 422
    # FastAPi can handle the above via ... item: Item = fastapi.Body(..., embed=True)
