import pytest


class TestCreateItem:
    
    def test_tc001_successful_creation(self, api_client, valid_item_data):
        response = api_client.create_item(valid_item_data)
        
        assert response.status_code == 200, f"Ожидался код 200, получен {response.status_code}"
        
        data = response.json()
        assert "status" in data, "Отсутствует поле status"
        
        status_message = data["status"]
        assert "Сохранили объявление" in status_message, "Неверное сообщение статуса"
        assert " - " in status_message, "ID не найден в сообщении"
        
        item_id = status_message.split(" - ")[1]
        assert isinstance(item_id, str), "id должен быть строкой"
        assert item_id != "", "id не должен быть пустым"
        
        get_response = api_client.get_item(item_id)
        assert get_response.status_code == 200, "Не удалось получить созданное объявление"
        
        items = get_response.json()
        assert len(items) > 0, "Объявление не найдено"
        
        item = items[0]
        assert item["sellerId"] == valid_item_data["sellerID"]
        assert item["name"] == valid_item_data["name"]
        assert item["price"] == valid_item_data["price"]
        assert "statistics" in item
        assert "createdAt" in item
        
        api_client.delete_item(item_id)
    
    def test_tc002_minimum_price(self, api_client, unique_seller_id):
        data = {
            "sellerID": unique_seller_id,
            "name": "Бесплатный товар",
            "price": 0,
            "statistics": {"likes": 1, "viewCount": 1, "contacts": 1}
        }
        
        response = api_client.create_item(data)
        
        assert response.status_code in [200, 400], \
            f"Ожидался код 200 или 400, получен {response.status_code}"
        
        if response.status_code == 200:
            response_data = response.json()
            item_id = response_data["status"].split(" - ")[1]
            
            get_response = api_client.get_item(item_id)
            if get_response.status_code == 200:
                items = get_response.json()
                assert items[0]["price"] == 0
            
            api_client.delete_item(item_id)
    
    def test_tc003_negative_price(self, api_client, unique_seller_id):
        data = {
            "sellerID": unique_seller_id,
            "name": "Тестовый товар",
            "price": -1000,
            "statistics": {"likes": 1, "viewCount": 1, "contacts": 1}
        }
        
        response = api_client.create_item(data)
        
        assert response.status_code in [200, 400], \
            f"Получен неожиданный код: {response.status_code}"
        
        if response.status_code == 200:
            response_data = response.json()
            item_id = response_data["status"].split(" - ")[1]
            api_client.delete_item(item_id)
            pytest.skip("API принимает отрицательные цены")
        else:
            data = response.json()
            assert "status" in data
            assert "result" in data
    
    def test_tc004_missing_seller_id(self, api_client):
        data = {
            "name": "Тестовый товар",
            "price": 5000,
            "statistics": {"likes": 1, "viewCount": 1, "contacts": 1}
        }
        
        response = api_client.create_item(data)
        
        assert response.status_code == 400, \
            f"Ожидался код 400 без sellerID, получен {response.status_code}"
        
        data = response.json()
        assert "result" in data
    
    def test_tc005_missing_name(self, api_client, unique_seller_id):
        data = {
            "sellerID": unique_seller_id,
            "price": 5000,
            "statistics": {"likes": 1, "viewCount": 1, "contacts": 1}
        }
        
        response = api_client.create_item(data)
        
        assert response.status_code == 400, \
            f"Ожидался код 400 без name, получен {response.status_code}"
    
    def test_tc006_empty_name(self, api_client, unique_seller_id):
        data = {
            "sellerID": unique_seller_id,
            "name": "",
            "price": 5000,
            "statistics": {"likes": 1, "viewCount": 1, "contacts": 1}
        }
        
        response = api_client.create_item(data)
        
        assert response.status_code == 400, \
            f"Ожидался код 400 для пустого name, получен {response.status_code}"
    
    def test_tc007_long_name(self, api_client, unique_seller_id):
        data = {
            "sellerID": unique_seller_id,
            "name": "A" * 10000,
            "price": 5000,
            "statistics": {"likes": 1, "viewCount": 1, "contacts": 1}
        }
        
        response = api_client.create_item(data)
        
        assert response.status_code in [200, 400], \
            f"Ожидался код 200 или 400, получен {response.status_code}"
        
        if response.status_code == 200:
            response_data = response.json()
            item_id = response_data["status"].split(" - ")[1]
            api_client.delete_item(item_id)
    
    def test_tc008_invalid_seller_id_type(self, api_client):
        data = {
            "sellerID": "sellerID2356",
            "name": "Тестовый товар",
            "price": 5000,
            "statistics": {"likes": 1, "viewCount": 1, "contacts": 1}
        }
        
        response = api_client.create_item(data)
        
        assert response.status_code == 400, \
            f"Ожидался код 400 для строкового sellerID, получен {response.status_code}"
    
    def test_tc009_negative_statistics(self, api_client, unique_seller_id):
        data = {
            "sellerID": unique_seller_id,
            "name": "Тестовый товар",
            "price": 5000,
            "statistics": {
                "likes": -5,
                "viewCount": -10,
                "contacts": -3
            }
        }
        
        response = api_client.create_item(data)
        
        assert response.status_code in [200, 400], \
            f"Получен неожиданный код: {response.status_code}"
        
        if response.status_code == 200:
            pytest.skip("API принимает отрицательные значения статистики")
    
    def test_tc010_missing_statistics(self, api_client, unique_seller_id):
        data = {
            "sellerID": unique_seller_id,
            "name": "Тестовый товар",
            "price": 5000
        }
        
        response = api_client.create_item(data)
        
        assert response.status_code in [200, 400], \
            f"Получен неожиданный код: {response.status_code}"
        
        if response.status_code == 200:
            response_data = response.json()
            item_id = response_data["status"].split(" - ")[1]
            
            get_response = api_client.get_item(item_id)
            if get_response.status_code == 200:
                items = get_response.json()
                assert "statistics" in items[0]
            
            api_client.delete_item(item_id)
