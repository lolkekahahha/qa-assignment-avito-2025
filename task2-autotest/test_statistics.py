import pytest


class TestStatistics:

    def test_tc020_get_statistics(self, api_client, created_item):
        item_id = created_item["id"]
        response = api_client.get_statistic(item_id, version=1)
        
        assert response.status_code == 200, \
            f"Ожидался код 200, получен {response.status_code}"
        
        data = response.json()
        assert isinstance(data, list), "Ответ должен быть массивом"
        assert len(data) > 0, "Массив не должен быть пустым"
        
        stats = data[0]
        assert "likes" in stats
        assert "viewCount" in stats
        assert "contacts" in stats
        assert isinstance(stats["likes"], int)
        assert isinstance(stats["viewCount"], int)
        assert isinstance(stats["contacts"], int)
    
    def test_tc021_get_nonexistent_statistics(self, api_client):
        response = api_client.get_statistic("00000000-0000-0000-0000-000000000000", version=1)
        
        assert response.status_code == 404, \
            f"Ожидался код 404, получен {response.status_code}"
        
        data = response.json()
        assert "status" in data
        assert "result" in data
    
    def test_tc022_get_statistics_empty_id(self, api_client):
        response = api_client.get_statistic("", version=1)
        
        assert response.status_code in [400, 404], \
            f"Ожидался код 400 или 404, получен {response.status_code}"
    
    def test_tc023_compare_statistics_endpoints(self, api_client, created_item):
        item_id = created_item["id"]
        
        response_item = api_client.get_item(item_id)
        assert response_item.status_code == 200
        item_stats = response_item.json()[0]["statistics"]

        response_stats = api_client.get_statistic(item_id, version=1)
        assert response_stats.status_code == 200
        stats = response_stats.json()[0]

        assert item_stats["likes"] == stats["likes"], \
            "likes не совпадают между эндпоинтами"
        assert item_stats["viewCount"] == stats["viewCount"], \
            "viewCount не совпадают между эндпоинтами"
        assert item_stats["contacts"] == stats["contacts"], \
            "contacts не совпадают между эндпоинтами"
    
    def test_tc028_get_statistics_v2(self, api_client, created_item):
        item_id = created_item["id"]
        response = api_client.get_statistic(item_id, version=2)
        
        assert response.status_code in [100, 200], \
            f"Ожидался код 100 или 200, получен {response.status_code}"
        
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, list)
            if len(data) > 0:
                stats = data[0]
                assert "likes" in stats
                assert "viewCount" in stats
                assert "contacts" in stats
    
    def test_tc029_compare_v1_v2_statistics(self, api_client, created_item):
        item_id = created_item["id"]
        
        response_v1 = api_client.get_statistic(item_id, version=1)
        assert response_v1.status_code == 200
        stats_v1 = response_v1.json()[0]
        
        response_v2 = api_client.get_statistic(item_id, version=2)

        if response_v2.status_code == 200:
            stats_v2 = response_v2.json()[0]
            
            assert stats_v1["likes"] == stats_v2["likes"]
            assert stats_v1["viewCount"] == stats_v2["viewCount"]
            assert stats_v1["contacts"] == stats_v2["contacts"]
