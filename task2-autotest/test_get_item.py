import pytest


class TestGetItem:    
    def test_tc011_get_existing_item(self, api_client, created_item):
        item_id = created_item["id"]
        response = api_client.get_item(item_id)
        
        assert response.status_code == 200, \
            f"Ожидался код 200, получен {response.status_code}"
        
        data = response.json()
        assert isinstance(data, list), "Ответ должен быть массивом"
        assert len(data) > 0, "Массив не должен быть пустым"
        
        item = data[0]
        assert item["id"] == item_id
        assert "sellerId" in item
        assert "name" in item
        assert "price" in item
        assert "statistics" in item
        assert "createdAt" in item
    
    def test_tc012_get_nonexistent_item(self, api_client):
        response = api_client.get_item("00000000-0000-0000-0000-000000000000")
        
        assert response.status_code == 404, \
            f"Ожидался код 404, получен {response.status_code}"
        
        data = response.json()
        assert "status" in data
        assert "result" in data
    
    def test_tc013_get_empty_id(self, api_client):
        response = api_client.get_item("")
        
        assert response.status_code in [400, 404], \
            f"Ожидался код 400 или 404, получен {response.status_code}"
    
    def test_tc014_get_invalid_id_format(self, api_client):
        response = api_client.get_item("@@invalid@@id@@")
        
        assert response.status_code in [400, 404], \
            f"Ожидался код 400 или 404, получен {response.status_code}"
