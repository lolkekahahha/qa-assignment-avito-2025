# Автотесты API 

Набор автоматизированных тестов для проверки REST API сервиса объявлений.
## Требования

- Python 3.10 или выше
- pip (менеджер пакетов Python)
- Доступ к интернету (для обращения к API)

## Установка

### 1. Клонируйте репозиторий или скачайте файлы проекта

```bash
cd task2-autotest
```

### 2. Установите зависимости

```bash
pip install -r requirements.txt
```

**Содержимое requirements.txt:**
```
pytest==7.4.3
requests==2.31.0
pytest-html==4.1.1
pytest-xdist==3.5.0
```

### 3. Проверьте установку

```bash
pytest --version
```

Должно вывести версию pytest (например, `pytest 7.4.3`).

## Запуск тестов

### Базовый запуск всех тестов

```bash
pytest -v
```

### Запуск с подробным выводом

```bash
pytest -v -s
```

### Запуск конкретного файла с тестами

```bash
pytest test_create_item.py -v
```

### Запуск конкретного теста

```bash
pytest test_create_item.py::TestCreateItem::test_tc001_successful_creation -v
```

### Запуск тестов по категориям

```bash
# Только тесты создания объявлений
pytest test_create_item.py -v

# Только тесты удаления
pytest test_delete_item.py -v

# Только интеграционные тесты
pytest test_integration.py -v

# Только негативные тесты
pytest test_negative.py -v
```

### Параллельный запуск

```bash
pytest -v -n 4
```

где `4` - количество параллельных процессов

### Генерация HTML отчета

```bash
pytest -v --html=report.html --self-contained-html
```

После выполнения откройте файл `report.html` в браузере.

### Запуск с остановкой на первой ошибке

```bash
pytest -v -x
```

### Запуск только упавших тестов

```bash
pytest -v --lf
```

## Структура проекта

```
task2-autotest/
├── conftest.py                 # Фикстуры и конфигурация pytest
├── pytest.ini                  # Настройки pytest
├── requirements.txt            # Зависимости проекта
├── README.md                   # Документация (этот файл)
├── BUGS.md                     # Описание найденных багов
├── swagger.yaml                # Спецификация API
├── postman_collection.json     # Postman коллекция
│
├── test_create_item.py         # Тесты создания объявлений (10 тестов)
├── test_get_item.py            # Тесты получения объявлений (4 теста)
├── test_delete_item.py         # Тесты удаления объявлений (4 теста)
├── test_seller_items.py        # Тесты получения объявлений продавца (5 тестов)
├── test_statistics.py          # Тесты статистики (6 тестов)
├── test_integration.py         # Интеграционные тесты (5 тестов)
└── test_negative.py            # Негативные тесты и граничные значения (12 тестов)
```

## Описание тестов

### test_create_item.py - Создание объявлений (10 тестов)

| Тест                                | Описание                                         |
| ----------------------------------- | ------------------------------------------------ |
| `test_tc001_successful_creation`    | Успешное создание объявления с валидными данными |
| `test_tc002_minimum_price`          | Создание объявления с минимальной ценой (0)      |
| `test_tc003_negative_price`         | Проверка отклонения отрицательной цены           |
| `test_tc004_missing_seller_id`      | Проверка обязательности поля sellerID            |
| `test_tc005_missing_name`           | Проверка обязательности поля name                |
| `test_tc006_empty_name`             | Проверка отклонения пустого name                 |
| `test_tc007_long_name`              | Проверка длинного названия (10000 символов)      |
| `test_tc008_invalid_seller_id_type` | Проверка типа данных для sellerID                |
| `test_tc009_negative_statistics`    | Проверка отклонения отрицательной статистики     |
| `test_tc010_missing_statistics`     | Проверка поведения при отсутствии statistics     |

### test_get_item.py - Получение объявлений (4 теста)

| Тест | Описание |
|------|----------|
| `test_tc011_get_existing_item` | Получение существующего объявления |
| `test_tc012_get_nonexistent_item` | Получение несуществующего объявления (404) |
| `test_tc013_get_empty_id` | Получение с пустым ID |
| `test_tc014_get_invalid_id_format` | Получение с невалидным форматом ID |

### test_delete_item.py - Удаление объявлений (4 теста)

| Тест | Описание |
|------|----------|
| `test_tc024_delete_existing_item` | Успешное удаление существующего объявления |
| `test_tc025_delete_nonexistent_item` | Удаление несуществующего объявления (404) |
| `test_tc026_delete_twice` | Повторное удаление уже удаленного объявления |
| `test_tc027_delete_empty_id` | Удаление с пустым ID |

### test_seller_items.py - Объявления продавца (5 тестов)

| Тест | Описание |
|------|----------|
| `test_tc015_get_seller_items` | Получение всех объявлений продавца |
| `test_tc016_get_seller_without_items` | Получение для продавца без объявлений |
| `test_tc017_negative_seller_id` | Проверка отрицательного sellerID |
| `test_tc018_invalid_seller_id_type` | Проверка невалидного типа sellerID |
| `test_tc019_unique_item_ids` | Проверка уникальности ID в списке |

### test_statistics.py - Статистика (6 тестов)

| Тест | Описание |
|------|----------|
| `test_tc020_get_statistics` | Получение статистики существующего объявления |
| `test_tc021_get_nonexistent_statistics` | Получение статистики несуществующего объявления |
| `test_tc022_get_statistics_empty_id` | Получение статистики с пустым ID |
| `test_tc023_compare_statistics_endpoints` | Сравнение статистики из разных эндпоинтов |
| `test_tc028_get_statistics_v2` | Получение статистики через API v2 |
| `test_tc029_compare_v1_v2_statistics` | Сравнение статистики между v1 и v2 |

### test_integration.py - Интеграционные тесты (5 тестов)

| Тест | Описание |
|------|----------|
| `test_tc030_full_lifecycle` | Полный жизненный цикл объявления |
| `test_tc031_multiple_items_one_seller` | Создание нескольких объявлений одним продавцом |
| `test_tc032_data_isolation` | Изоляция данных разных продавцов |
| `test_tc033_unique_item_ids` | Уникальность ID объявлений |
| `test_tc051_data_consistency_after_delete` | Согласованность данных после удаления |

### test_negative.py - Негативные тесты (12 тестов)

#### Негативные сценарии (6 тестов)

| Тест                          | Описание                           |
| ----------------------------- | ---------------------------------- |
| `test_tc034_invalid_json`     | Отправка невалидного JSON          |
| `test_tc035_no_content_type`  | Запрос без Content-Type            |
| `test_tc036_wrong_method`     | Запрос с некорректным HTTP методом |
| `test_tc038_sql_injection`    | Проверка на SQL инъекции           |
| `test_tc039_xss_in_name`      | Проверка на XSS уязвимости         |
| `test_tc040_security_headers` | Проверка заголовков безопасности   |

#### Граничные значения (4 теста)

| Тест | Описание |
|------|----------|
| `test_tc041_max_name_length` | Максимальная длина названия |
| `test_tc042_max_price` | Максимальное значение цены |
| `test_tc045_zero_statistics` | Нулевые значения статистики |
| `test_tc053_unicode_support` | Поддержка Unicode символов |

#### Производительность (2 теста)

| Тест | Описание |
|------|----------|
| `test_tc037_create_many_items` | Создание множества объявлений |
| `test_tc052_get_idempotency` | Идемпотентность GET запросов |

### Тесты, помеченные как SKIPPED

Три теста помечены как `SKIPPED`, так как они выявляют известные баги API:

1. **test_tc003_negative_price** - API принимает отрицательные цены
2. **test_tc009_negative_statistics** - API принимает отрицательную статистику
3. **test_tc039_xss_in_name** - XSS скрипт не экранируется

Эти тесты работают корректно и документируют реальные проблемы в API.

## Конфигурация

### conftest.py

Содержит фикстуры для тестов:

- `base_url` - базовый URL API
- `api_client` - HTTP клиент с методами для работы с API
- `valid_item_data` - валидные данные для создания объявления
- `created_item` - фикстура для создания и автоматической очистки объявления
- `unique_seller_id` - генератор уникальных ID продавцов

### pytest.ini

Настройки pytest:

```ini
[pytest]
markers =
    smoke: Smoke tests
    regression: Regression tests
    integration: Integration tests
```

## API Endpoints

### Базовый URL
```
https://qa-internship.avito.com
```

### Эндпоинты

| Метод | Путь | Описание |
|-------|------|----------|
| POST | `/api/1/item` | Создать объявление |
| GET | `/api/1/item/{id}` | Получить объявление по ID |
| GET | `/api/1/{sellerID}/item` | Получить все объявления продавца |
| GET | `/api/1/statistic/{id}` | Получить статистику v1 |
| GET | `/api/2/statistic/{id}` | Получить статистику v2 |
| DELETE | `/api/2/item/{id}` | Удалить объявление |
