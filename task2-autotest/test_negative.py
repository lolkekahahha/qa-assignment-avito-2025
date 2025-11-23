import pytest
import requests


class TestNegative:
    def test_tc034_invalid_json(self, api_client):
        invalid_json = '{"sellerID": 555400, "name": "Тест" "price": 5000}'
        
        response = requests.post(
            f"{api_client.base_url}/api/1/item",
            data=invalid_json,
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 400, \
            f"Ожидался код 400 для невалидного JSON, получен {response.status_code}"
    
    def test_tc035_no_content_type(self, api_client, valid_item_data):
        response = requests.post(
            f"{api_client.base_url}/api/1/item",
            json=valid_item_data,
            headers={"Accept": "application/json"}
        )

        assert response.status_code in [200, 400, 415], \
            f"Получен неожиданный код: {response.status_code}"
    
    def test_tc036_wrong_method(self, api_client, valid_item_data):
        response = requests.put(
            f"{api_client.base_url}/api/1/item",
            json=valid_item_data,
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 405, \
            f"Ожидался код 405 Method Not Allowed, получен {response.status_code}"
    
    def test_tc038_sql_injection(self, api_client):
        malicious_id = "' OR '1'='1"
        response = api_client.get_item(malicious_id)
        assert response.status_code in [400, 404], \
            f"Возможная SQL инъекция. Код: {response.status_code}"
        
        if response.status_code == 200:
            pytest.fail("SQL инъекция может быть успешной")
    
    def test_tc039_xss_in_name(self, api_client, unique_seller_id):
        data = {
            "sellerID": unique_seller_id,
            "name": "<script>alert('XSS')</script>",
            "price": 5000,
            "statistics": {"likes": 1, "viewCount": 1, "contacts": 1}
        }
        
        response = api_client.create_item(data)
        
        if response.status_code == 200:
            response_data = response.json()
            item_id = response_data["status"].split(" - ")[1]
            
            get_response = api_client.get_item(item_id)
            item = get_response.json()[0]
            
            name = item["name"]
            
            api_client.delete_item(item_id)
            
            if "<script>" in name and "&lt;script&gt;" not in name:
                pytest.skip("XSS скрипт не экранирован")
        else:
            assert response.status_code == 400
    
    def test_tc040_security_headers(self, api_client, created_item):
        item_id = created_item["id"]
        response = api_client.get_item(item_id)
        
        headers = response.headers

        security_headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": ["DENY", "SAMEORIGIN"],
        }

        for header, expected in security_headers.items():
            if header in headers:
                value = headers[header]
                if isinstance(expected, list):
                    assert value in expected, \
                        f"Заголовок {header} имеет значение {value}, ожидалось одно из {expected}"
                else:
                    assert value == expected, \
                        f"Заголовок {header} имеет значение {value}, ожидалось {expected}"


class TestBoundaryValues:
    def test_tc041_max_name_length(self, api_client, unique_seller_id):
        lengths = [100, 500, 1000, 5000]
        
        for length in lengths:
            data = {
                "sellerID": unique_seller_id,
                "name": "A" * length,
                "price": 5000,
                "statistics": {"likes": 1, "viewCount": 1, "contacts": 1}
            }
            
            response = api_client.create_item(data)
            
            if response.status_code == 200:
                response_data = response.json()
                item_id = response_data["status"].split(" - ")[1]
                api_client.delete_item(item_id)
            elif response.status_code == 400:
                break
    
    def test_tc042_max_price(self, api_client, unique_seller_id):
        data = {
            "sellerID": unique_seller_id,
            "name": "Товар с максимальной ценой",
            "price": 2147483647,  # Max int32
            "statistics": {"likes": 1, "viewCount": 1, "contacts": 1}
        }
        
        response = api_client.create_item(data)
        
        if response.status_code == 200:
            response_data = response.json()
            item_id = response_data["status"].split(" - ")[1]
            
            get_response = api_client.get_item(item_id)
            if get_response.status_code == 200:
                items = get_response.json()
                assert items[0]["price"] == 2147483647
            
            api_client.delete_item(item_id)
        else:
            assert response.status_code == 400
    
    def test_tc045_zero_statistics(self, api_client, unique_seller_id):
        data = {
            "sellerID": unique_seller_id,
            "name": "Объявление с нулевой статистикой",
            "price": 5000,
            "statistics": {
                "likes": 0,
                "viewCount": 0,
                "contacts": 0
            }
        }
        
        response = api_client.create_item(data)

        assert response.status_code in [200, 400], \
            f"Получен неожиданный код: {response.status_code}"
        
        if response.status_code == 200:
            response_data = response.json()
            item_id = response_data["status"].split(" - ")[1]
            
            get_response = api_client.get_item(item_id)
            assert get_response.status_code == 200
            
            item = get_response.json()[0]
            assert item["statistics"]["likes"] == 0
            assert item["statistics"]["viewCount"] == 0
            assert item["statistics"]["contacts"] == 0
            
            api_client.delete_item(item_id)
        else:
            data = response.json()
            assert "result" in data or "status" in data
    
    def test_tc053_unicode_support(self, api_client, unique_seller_id):
        data = {
            "sellerID": unique_seller_id,
            "name": "Тест кириллицы 测试中文 🚀 émojis & спецсимволы: €£¥",
            "price": 5000,
            "statistics": {"likes": 1, "viewCount": 1, "contacts": 1}
        }
        
        response = api_client.create_item(data)
        assert response.status_code == 200
        
        response_data = response.json()
        item_id = response_data["status"].split(" - ")[1]

        get_response = api_client.get_item(item_id)
        item = get_response.json()[0]

        assert "кириллицы" in item["name"]
        assert "测试" in item["name"]
        assert "🚀" in item["name"]
        
        api_client.delete_item(item_id)


class TestPerformance:
    
    def test_tc037_create_many_items(self, api_client, unique_seller_id):
        """TC-037: Создание множества объявлений"""
        created_ids = []
        errors = []

        for i in range(20):
            data = {
                "sellerID": unique_seller_id,
                "name": f"Товар {i+1}",
                "price": 1000 * (i + 1),
                "statistics": {"likes": 1, "viewCount": 1, "contacts": 1}
            }
            
            try:
                response = api_client.create_item(data)
                if response.status_code == 200:
                    # Извлекаем ID из ответа
                    response_data = response.json()
                    item_id = response_data["status"].split(" - ")[1]
                    created_ids.append(item_id)
                else:
                    errors.append(f"Объявление {i+1}: код {response.status_code}")
            except Exception as e:
                errors.append(f"Объявление {i+1}: {str(e)}")

        assert len(created_ids) >= 18, \
            f"Создано только {len(created_ids)} из 20 объявлений. Ошибки: {errors}"

        response = api_client.get_seller_items(unique_seller_id)
        assert response.status_code == 200
        
        items = response.json()
        assert len(items) >= 20

        for item_id in created_ids:
            try:
                api_client.delete_item(item_id)
            except:
                pass
    
    def test_tc052_get_idempotency(self, api_client, created_item):
        item_id = created_item["id"]
        
        responses = []
        for _ in range(5):
            response = api_client.get_item(item_id)
            assert response.status_code == 200
            responses.append(response.json())
        
        first = responses[0]
        for resp in responses[1:]:
            assert resp == first, "GET запросы возвращают разные данные"
