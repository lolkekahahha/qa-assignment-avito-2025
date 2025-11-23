import pytest


class TestIntegration:
    
    def test_tc030_full_lifecycle(self, api_client):
        item_data = {
            "sellerID": 555300,
            "name": "Apple AirPods 3",
            "price": 15000,
            "statistics": {
                "likes": 5,
                "viewCount": 100,
                "contacts": 3
            }
        }
        
        create_response = api_client.create_item(item_data)
        assert create_response.status_code == 200, "Шаг 1: Создание не удалось"
        
        response_data = create_response.json()
        item_id = response_data["status"].split(" - ")[1]
        
        get_response = api_client.get_item(item_id)
        assert get_response.status_code == 200, "Шаг 3: Получение не удалось"
        item = get_response.json()[0]
        assert item["name"] == item_data["name"]
        assert item["price"] == item_data["price"]
        
        list_response = api_client.get_seller_items(555300)
        assert list_response.status_code == 200, "Шаг 4: Получение списка не удалось"
        items = list_response.json()
        assert any(i["id"] == item_id for i in items), "Объявление не найдено в списке"
        
        stats_response = api_client.get_statistic(item_id)
        assert stats_response.status_code == 200, "Шаг 5: Получение статистики не удалось"
        stats = stats_response.json()[0]
        assert stats["likes"] == item_data["statistics"]["likes"]
        
        delete_response = api_client.delete_item(item_id)
        assert delete_response.status_code == 200, "Шаг 6: Удаление не удалось"
        
        final_response = api_client.get_item(item_id)
        assert final_response.status_code == 404, "Шаг 7: Объявление не удалено"
    
    def test_tc031_multiple_items_one_seller(self, api_client, unique_seller_id):
        created_ids = []
        
        for i in range(1, 6):
            data = {
                "sellerID": unique_seller_id,
                "name": f"Товар {i}",
                "price": 1000 * i,
                "statistics": {"likes": 1, "viewCount": 1, "contacts": 1}
            }
            response = api_client.create_item(data)
            assert response.status_code == 200, f"Не удалось создать объявление {i}"
            
            response_data = response.json()
            item_id = response_data["status"].split(" - ")[1]
            created_ids.append(item_id)
        
        response = api_client.get_seller_items(unique_seller_id)
        assert response.status_code == 200
        
        items = response.json()
        assert len(items) >= 5, f"Ожидалось минимум 5 объявлений, получено {len(items)}"

        for item in items:
            assert item["sellerId"] == unique_seller_id

        item_ids_in_list = [item["id"] for item in items]
        for created_id in created_ids:
            assert created_id in item_ids_in_list, \
                f"Объявление {created_id} не найдено в списке"

        for item_id in created_ids:
            api_client.delete_item(item_id)
    
    def test_tc032_data_isolation(self, api_client):

        import random
        seller1 = random.randint(100000, 999999)
        seller2 = random.randint(100000, 999999)
        
        created_ids_1 = []
        created_ids_2 = []
        
        for i in range(1, 3):
            data = {
                "sellerID": seller1,
                "name": f"Продавец 1 - Товар {i}",
                "price": 1000 * i,
                "statistics": {"likes": 1, "viewCount": 1, "contacts": 1}
            }
            response = api_client.create_item(data)
            assert response.status_code == 200
            
            response_data = response.json()
            item_id = response_data["status"].split(" - ")[1]
            created_ids_1.append(item_id)
        
        for i in range(1, 3):
            data = {
                "sellerID": seller2,
                "name": f"Продавец 2 - Товар {i}",
                "price": 3000 + 1000 * i,
                "statistics": {"likes": 1, "viewCount": 1, "contacts": 1}
            }
            response = api_client.create_item(data)
            assert response.status_code == 200

            response_data = response.json()
            item_id = response_data["status"].split(" - ")[1]
            created_ids_2.append(item_id)
        
        items_1 = api_client.get_seller_items(seller1).json()
        items_2 = api_client.get_seller_items(seller2).json()
        
        ids_1 = [item["id"] for item in items_1]
        ids_2 = [item["id"] for item in items_2]

        for item_id in created_ids_1:
            assert item_id in ids_1, f"Объявление {item_id} не найдено у продавца 1"
            assert item_id not in ids_2, f"Объявление {item_id} найдено у продавца 2"

        for item_id in created_ids_2:
            assert item_id in ids_2, f"Объявление {item_id} не найдено у продавца 2"
            assert item_id not in ids_1, f"Объявление {item_id} найдено у продавца 1"
        
        for item_id in created_ids_1 + created_ids_2:
            api_client.delete_item(item_id)
    
    def test_tc033_unique_item_ids(self, api_client):
        import random
        created_ids = []

        for i in range(10):
            data = {
                "sellerID": random.randint(100000, 999999),
                "name": f"Уникальный тест {i}",
                "price": 1000 * (i + 1),
                "statistics": {"likes": 1, "viewCount": 1, "contacts": 1}
            }
            response = api_client.create_item(data)
            assert response.status_code == 200
            
            response_data = response.json()
            item_id = response_data["status"].split(" - ")[1]
            created_ids.append(item_id)
        
        assert len(created_ids) == len(set(created_ids)), \
            "Обнаружены дублирующиеся ID"
        
        assert len(set(created_ids)) == 10, \
            f"Ожидалось 10 уникальных ID, получено {len(set(created_ids))}"
        
        for item_id in created_ids:
            api_client.delete_item(item_id)
    
    def test_tc051_data_consistency_after_delete(self, api_client):
        import random
        seller_id = random.randint(100000, 999999)
        
        data = {
            "sellerID": seller_id,
            "name": "Тест согласованности",
            "price": 5000,
            "statistics": {"likes": 1, "viewCount": 1, "contacts": 1}
        }
        response = api_client.create_item(data)
        assert response.status_code == 200

        response_data = response.json()
        item_id = response_data["status"].split(" - ")[1]

        before = api_client.get_seller_items(seller_id).json()
        count_before = len([i for i in before if i["sellerId"] == seller_id])

        delete_response = api_client.delete_item(item_id)
        assert delete_response.status_code == 200

        after = api_client.get_seller_items(seller_id).json()
        count_after = len([i for i in after if i["sellerId"] == seller_id])

        assert count_after == count_before - 1, \
            "Количество объявлений должно уменьшиться на 1"

        item_ids_after = [i["id"] for i in after]
        assert item_id not in item_ids_after, \
            "Удаленное объявление все еще в списке"

        get_response = api_client.get_item(item_id)
        assert get_response.status_code == 404
        
        stats_response = api_client.get_statistic(item_id)
        assert stats_response.status_code in [200, 404], \
            f"Ожидался код 200 или 404, получен {stats_response.status_code}"
