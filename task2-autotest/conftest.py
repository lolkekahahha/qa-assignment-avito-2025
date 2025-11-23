import pytest
import requests
from typing import Dict, Any


@pytest.fixture(scope="session")
def base_url():
    return "https://qa-internship.avito.com"


@pytest.fixture(scope="session")
def api_client(base_url):
    session = requests.Session()
    session.headers.update({
        "Content-Type": "application/json",
        "Accept": "application/json"
    })
    
    class APIClient:
        def __init__(self, base_url, session):
            self.base_url = base_url
            self.session = session
        
        def create_item(self, data: Dict[str, Any]) -> requests.Response:
            return self.session.post(f"{self.base_url}/api/1/item", json=data)
        
        def get_item(self, item_id: str) -> requests.Response:
            return self.session.get(f"{self.base_url}/api/1/item/{item_id}")
        
        def get_seller_items(self, seller_id: int) -> requests.Response:
            return self.session.get(f"{self.base_url}/api/1/{seller_id}/item")
        
        def get_statistic(self, item_id: str, version: int = 1) -> requests.Response:
            return self.session.get(f"{self.base_url}/api/{version}/statistic/{item_id}")
        
        def delete_item(self, item_id: str) -> requests.Response:
            return self.session.delete(f"{self.base_url}/api/2/item/{item_id}")
    
    return APIClient(base_url, session)


@pytest.fixture
def valid_item_data():
    return {
        "sellerID": 555123,
        "name": "iPhone 14 Pro Max",
        "price": 90000,
        "statistics": {
            "likes": 10,
            "viewCount": 100,
            "contacts": 5
        }
    }


@pytest.fixture
def created_item(api_client, valid_item_data):
    response = api_client.create_item(valid_item_data)
    
    if response.status_code != 200:
        yield None
        return
    
    response_data = response.json()
    status_message = response_data.get("status", "")
    
    if " - " in status_message:
        item_id = status_message.split(" - ")[1]
        
        get_response = api_client.get_item(item_id)
        if get_response.status_code == 200:
            items = get_response.json()
            item_data = items[0] if items else None
        else:
            item_data = {"id": item_id}
    else:
        item_data = None
    
    yield item_data

    if item_data and "id" in item_data:
        try:
            api_client.delete_item(item_data["id"])
        except:
            pass


@pytest.fixture
def unique_seller_id():
    import random
    return random.randint(100000, 999999)


def get_valid_statistics():
    return {
        "likes": 1,
        "viewCount": 1,
        "contacts": 1
    }
