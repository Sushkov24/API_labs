"""
Навантажувальний тест для POST /auth/login ендпоінта бібліотечного API.
Ендпоінт обрано без Rate Limiter (lab9).

Запуск через Docker:
    docker-compose up locust

Або локально:
    locust -f locustfile.py --host=http://localhost:8000

Web UI: http://localhost:8089
"""
from locust import HttpUser, task, between, events

# Тестові облікові дані — єдиний акаунт, що використовується всіма віртуальними
# користувачами. Реєструється одного разу при старті першого user-а.
TEST_EMAIL = "loadtest@library.com"
TEST_PASSWORD = "LoadTest_Password_2024!"

_user_registered = False  # глобальний прапор щоб реєструвати акаунт лише раз


class LibraryLoginUser(HttpUser):
    """
    Симулює користувача, що багаторазово авторизується через POST /auth/login.

    Параметри навантаження (задаються у Web UI або CLI):
        --users        — кількість одночасних користувачів
        --spawn-rate   — швидкість появи нових (users/sec)
    """

    wait_time = between(0.5, 2)  # пауза між запитами від 0.5 до 2 секунд

    def on_start(self):
        """Виконується один раз при старті кожного віртуального користувача."""
        global _user_registered
        if not _user_registered:
            _user_registered = True
            self.client.post(
                "/auth/register",
                json={"email": TEST_EMAIL, "password": TEST_PASSWORD},
                name="[setup] POST /auth/register",
            )

    @task
    def login(self):
        """
        Основна задача — POST /auth/login.

        Перевіряє:
          - HTTP 200 у відповідь
          - Наявність access_token у тілі відповіді
          - Наявність refresh_token у тілі відповіді
        """
        with self.client.post(
            "/auth/login",
            data={
                "username": TEST_EMAIL,
                "password": TEST_PASSWORD,
            },
            catch_response=True,
            name="POST /auth/login",
        ) as response:
            if response.status_code == 200:
                try:
                    data = response.json()
                    if "access_token" not in data:
                        response.failure("Відповідь не містить access_token")
                    elif "refresh_token" not in data:
                        response.failure("Відповідь не містить refresh_token")
                    else:
                        response.success()
                except Exception as e:
                    response.failure(f"Помилка парсингу JSON: {e}")
            elif response.status_code == 401:
                response.failure(f"Невірні облікові дані (401): {response.text}")
            elif response.status_code == 422:
                response.failure(f"Помилка валідації (422): {response.text}")
            else:
                response.failure(
                    f"Несподіваний статус {response.status_code}: {response.text}"
                )
