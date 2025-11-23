import pytest


class TestSellerItems:

    def test_tc015_get_seller_items(self, api_client, unique_seller_id):
        created_ids = []
        for i in range(3):
            data = {
                "sellerID": unique_seller_id,
                "name": f"Товар {i+1}",
                "price": 1000 * (i+1),
                "statistics": {"likes": 1, "viewCount": 1, "contacts": 1}
            }
            response = api_client.create_item(data)
            assert response.status_code == 200
            
            response_data = response.json()
            item_id = response_data["status"].split(" - ")[1]
            created_ids.append(item_id)
        
        response = api_client.get_seller_items(unique_seller_id)
        
        assert response.status_code == 200, \
            f"Ожидался код 200, получен {response.status_code}"
        
        items = response.json()
        assert isinstance(items, list), "Ответ должен быть массивом"
        assert len(items) >= 3, f"Ожидалось минимум 3 объявления, получено {len(items)}"

        for item in items:
            assert item["sellerId"] == unique_seller_id
            assert all(key in item for key in ["id", "sellerId", "name", "price", "statistics", "createdAt"])

        for item_id in created_ids:
            api_client.delete_item(item_id)
    
    def test_tc016_get_seller_without_items(self, api_client):
        response = api_client.get_seller_items(999888)
        
        assert response.status_code == 200, \
            f"Ожидался код 200, получен {response.status_code}"
        
        items = response.json()
        assert isinstance(items, list), "Ответ должен быть массивом"
    
    def test_tc017_negative_seller_id(self, api_client):
        response = api_client.get_seller_items(-123)
        
        assert response.status_code in [200, 400, 404], \
            f"Ожидался код 200, 400 или 404, получен {response.status_code}"
    
    def test_tc018_invalid_seller_id_type(self, api_client):
        import requests
        base_url = api_client.base_url
        response = requests.get(f"{base_url}/api/1/abc/item")
        
        assert response.status_code in [400, 404], \
            f"Ожидался код 400 или 404, получен {response.status_code}"
    
    def test_tc019_unique_item_ids(self, api_client, unique_seller_id):
        created_ids = []
        for i in range(3):
            data = {
                "sellerID": unique_seller_id,
                "name": f"Уникальный товар {i+1}",
                "price": 2000 * (i+1),
                "statistics": {"likes": 1, "viewCount": 1, "contacts": 1}
            }
            response = api_client.create_item(data)
            assert response.status_code == 200

            response_data = response.json()
            item_id = response_data["status"].split(" - ")[1]
            created_ids.append(item_id)
        
        response = api_client.get_seller_items(unique_seller_id)
        assert response.status_code == 200
        
        items = response.json()
        item_ids = [item["id"] for item in items]
        
        assert len(item_ids) == len(set(item_ids)), \
            "Обнаружены дублирующиеся ID объявлений"
        
        for item_id in created_ids:
            api_client.delete_item(item_id)
