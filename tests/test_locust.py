"""
Unit-тести для locustfile.py.
Перевіряють структуру, конфігурацію та логіку задач без запуску Locust.
"""
import sys
import os
import json
import pytest
from unittest.mock import MagicMock, patch, call
from locust import HttpUser, between

# Додаємо кореневу директорію в sys.path для імпорту locustfile
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import locustfile
from locustfile import LibraryLoginUser, TEST_EMAIL, TEST_PASSWORD


class TestLocustfileConstants:
    def test_test_email_is_string(self):
        assert isinstance(TEST_EMAIL, str)

    def test_test_email_is_valid_format(self):
        assert "@" in TEST_EMAIL
        assert "." in TEST_EMAIL.split("@")[-1]

    def test_test_password_is_string(self):
        assert isinstance(TEST_PASSWORD, str)

    def test_test_password_not_empty(self):
        assert len(TEST_PASSWORD) > 0


class TestLibraryLoginUserClass:
    def test_is_subclass_of_http_user(self):
        assert issubclass(LibraryLoginUser, HttpUser)

    def test_has_wait_time(self):
        assert hasattr(LibraryLoginUser, "wait_time"), (
            "LibraryLoginUser повинен мати атрибут wait_time"
        )

    def test_wait_time_is_callable(self):
        assert callable(LibraryLoginUser.wait_time)

    def test_wait_time_returns_positive_value(self):
        mock_user = MagicMock()
        result = LibraryLoginUser.wait_time(mock_user)
        assert result > 0, "wait_time повинен повертати позитивне число"

    def test_wait_time_within_range(self):
        mock_user = MagicMock()
        for _ in range(20):
            result = LibraryLoginUser.wait_time(mock_user)
            assert 0.5 <= result <= 2.0, (
                f"wait_time={result} виходить за межі [0.5, 2.0]"
            )

    def test_has_login_task(self):
        assert hasattr(LibraryLoginUser, "login"), (
            "LibraryLoginUser повинен мати метод login"
        )

    def test_login_is_callable(self):
        assert callable(LibraryLoginUser.login)

    def test_login_is_decorated_with_task(self):
        assert hasattr(LibraryLoginUser.login, "locust_task_weight"), (
            "Метод login повинен бути декорований @task"
        )

    def test_login_task_weight_is_positive(self):
        assert LibraryLoginUser.login.locust_task_weight >= 1

    def test_has_on_start_method(self):
        assert hasattr(LibraryLoginUser, "on_start"), (
            "LibraryLoginUser повинен мати метод on_start"
        )

    def test_on_start_is_callable(self):
        assert callable(LibraryLoginUser.on_start)


class TestLoginTaskLogic:
    """Тестує логіку методу login через мок HTTP-клієнт."""

    def _make_user(self):
        """Створює екземпляр LibraryLoginUser з повністю мокнутим оточенням."""
        user = LibraryLoginUser.__new__(LibraryLoginUser)
        user.client = MagicMock()
        return user

    def _make_response(self, status_code: int, body: dict | None = None):
        """Будує мок відповіді для context manager."""
        mock_response = MagicMock()
        mock_response.status_code = status_code
        mock_response.json.return_value = body or {}
        mock_response.text = json.dumps(body or {})
        mock_response.__enter__ = MagicMock(return_value=mock_response)
        mock_response.__exit__ = MagicMock(return_value=False)
        return mock_response

    def test_login_calls_post_auth_login(self):
        user = self._make_user()
        mock_resp = self._make_response(
            200, {"access_token": "tok", "refresh_token": "ref", "token_type": "bearer"}
        )
        user.client.post.return_value = mock_resp

        user.login()

        user.client.post.assert_called_once()
        args, kwargs = user.client.post.call_args
        assert args[0] == "/auth/login"

    def test_login_sends_form_data(self):
        user = self._make_user()
        mock_resp = self._make_response(
            200, {"access_token": "tok", "refresh_token": "ref", "token_type": "bearer"}
        )
        user.client.post.return_value = mock_resp

        user.login()

        _, kwargs = user.client.post.call_args
        data = kwargs.get("data", {})
        assert data.get("username") == TEST_EMAIL
        assert data.get("password") == TEST_PASSWORD

    def test_login_uses_catch_response(self):
        user = self._make_user()
        mock_resp = self._make_response(
            200, {"access_token": "tok", "refresh_token": "ref", "token_type": "bearer"}
        )
        user.client.post.return_value = mock_resp

        user.login()

        _, kwargs = user.client.post.call_args
        assert kwargs.get("catch_response") is True

    def test_login_success_calls_response_success(self):
        user = self._make_user()
        mock_resp = self._make_response(
            200, {"access_token": "tok", "refresh_token": "ref", "token_type": "bearer"}
        )
        user.client.post.return_value = mock_resp

        user.login()

        mock_resp.success.assert_called_once()
        mock_resp.failure.assert_not_called()

    def test_login_missing_access_token_calls_failure(self):
        user = self._make_user()
        mock_resp = self._make_response(200, {"refresh_token": "ref"})
        user.client.post.return_value = mock_resp

        user.login()

        mock_resp.failure.assert_called_once()
        args, _ = mock_resp.failure.call_args
        assert "access_token" in args[0]

    def test_login_missing_refresh_token_calls_failure(self):
        user = self._make_user()
        mock_resp = self._make_response(200, {"access_token": "tok"})
        user.client.post.return_value = mock_resp

        user.login()

        mock_resp.failure.assert_called_once()
        args, _ = mock_resp.failure.call_args
        assert "refresh_token" in args[0]

    def test_login_401_calls_failure(self):
        user = self._make_user()
        mock_resp = self._make_response(401, {"detail": "Invalid credentials"})
        user.client.post.return_value = mock_resp

        user.login()

        mock_resp.failure.assert_called_once()
        args, _ = mock_resp.failure.call_args
        assert "401" in args[0]

    def test_login_422_calls_failure(self):
        user = self._make_user()
        mock_resp = self._make_response(422, {"detail": "Validation error"})
        user.client.post.return_value = mock_resp

        user.login()

        mock_resp.failure.assert_called_once()
        args, _ = mock_resp.failure.call_args
        assert "422" in args[0]

    def test_login_unexpected_status_calls_failure(self):
        user = self._make_user()
        mock_resp = self._make_response(500, {"detail": "Server error"})
        user.client.post.return_value = mock_resp

        user.login()

        mock_resp.failure.assert_called_once()
        args, _ = mock_resp.failure.call_args
        assert "500" in args[0]

    def test_login_invalid_json_calls_failure(self):
        user = self._make_user()
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.side_effect = ValueError("invalid json")
        mock_resp.__enter__ = MagicMock(return_value=mock_resp)
        mock_resp.__exit__ = MagicMock(return_value=False)
        user.client.post.return_value = mock_resp

        user.login()

        mock_resp.failure.assert_called_once()
        args, _ = mock_resp.failure.call_args
        assert "JSON" in args[0]


class TestOnStartLogic:
    def test_on_start_calls_register(self):
        """on_start має викликати /auth/register (щонайменше для першого user-а)."""
        # Скидаємо глобальний прапор перед тестом
        locustfile._user_registered = False

        user = LibraryLoginUser.__new__(LibraryLoginUser)
        user.client = MagicMock()

        user.on_start()

        user.client.post.assert_called_once()
        args, kwargs = user.client.post.call_args
        assert args[0] == "/auth/register"
        assert kwargs["json"]["email"] == TEST_EMAIL
        assert kwargs["json"]["password"] == TEST_PASSWORD

    def test_on_start_registers_only_once(self):
        """Другий виклик on_start не повинен повторно реєструвати користувача."""
        locustfile._user_registered = False

        user1 = LibraryLoginUser.__new__(LibraryLoginUser)
        user1.client = MagicMock()
        user1.on_start()

        user2 = LibraryLoginUser.__new__(LibraryLoginUser)
        user2.client = MagicMock()
        user2.on_start()

        user1.client.post.assert_called_once()
        user2.client.post.assert_not_called()
