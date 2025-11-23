import pytest


class TestDeleteItem:
    
    def test_tc024_delete_existing_item(self, api_client, valid_item_data):
        response = api_client.create_item(valid_item_data)
        assert response.status_code == 200
        
        response_data = response.json()
        item_id = response_data["status"].split(" - ")[1]
        
        delete_response = api_client.delete_item(item_id)
        assert delete_response.status_code == 200, \
            f"Ожидался код 200 при удалении, получен {delete_response.status_code}"

        get_response = api_client.get_item(item_id)
        assert get_response.status_code == 404, \
            "Объявление должно быть удалено (404)"
    
    def test_tc025_delete_nonexistent_item(self, api_client):
        response = api_client.delete_item("00000000-0000-0000-0000-000000000000")
        
        assert response.status_code == 404, \
            f"Ожидался код 404, получен {response.status_code}"
        
        data = response.json()
        assert "status" in data
        assert "result" in data
    
    def test_tc026_delete_twice(self, api_client, valid_item_data):
        response = api_client.create_item(valid_item_data)
        assert response.status_code == 200

        response_data = response.json()
        item_id = response_data["status"].split(" - ")[1]
        
        first_delete = api_client.delete_item(item_id)
        assert first_delete.status_code == 200, \
            "Первое удаление должно быть успешным"

        second_delete = api_client.delete_item(item_id)
        assert second_delete.status_code == 404, \
            f"Ожидался код 404 при повторном удалении, получен {second_delete.status_code}"
    
    def test_tc027_delete_empty_id(self, api_client):
        response = api_client.delete_item("")
        
        assert response.status_code in [400, 404], \
            f"Ожидался код 400 или 404, получен {response.status_code}"
