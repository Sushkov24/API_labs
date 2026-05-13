"""
Unit-тести для валідації структури OpenAPI специфікації (openapi.yaml).
Не потребують запущеного сервера — перевіряють лише файл специфікації.
"""
import os
import pytest
import yaml

SPEC_PATH = os.path.join(os.path.dirname(__file__), "..", "openapi.yaml")

EXPECTED_PATHS = [
    "/",
    "/auth/register",
    "/auth/login",
    "/auth/refresh",
    "/books/",
    "/books/{book_id}",
]

EXPECTED_SCHEMAS = [
    "BookCreate",
    "BookResponse",
    "PaginatedBookResponse",
    "BookStatus",
    "UserCreate",
    "Token",
    "ErrorDetail",
]


@pytest.fixture(scope="module")
def spec() -> dict:
    """Завантажує та парсить openapi.yaml."""
    with open(SPEC_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


class TestSpecTopLevel:
    def test_spec_file_exists(self):
        assert os.path.isfile(SPEC_PATH), "openapi.yaml не знайдено"

    def test_openapi_version(self, spec):
        assert "openapi" in spec
        assert spec["openapi"].startswith("3."), "Має бути OpenAPI 3.x"

    def test_info_section(self, spec):
        assert "info" in spec
        assert "title" in spec["info"]
        assert "version" in spec["info"]

    def test_servers_defined(self, spec):
        assert "servers" in spec
        assert len(spec["servers"]) >= 1
        assert "url" in spec["servers"][0]

    def test_components_exist(self, spec):
        assert "components" in spec

    def test_security_schemes_defined(self, spec):
        schemes = spec["components"].get("securitySchemes", {})
        assert "BearerAuth" in schemes
        bearer = schemes["BearerAuth"]
        assert bearer["type"] == "http"
        assert bearer["scheme"] == "bearer"

    def test_paths_exist(self, spec):
        assert "paths" in spec
        assert len(spec["paths"]) > 0


class TestSpecPaths:
    @pytest.mark.parametrize("path", EXPECTED_PATHS)
    def test_required_path_exists(self, spec, path):
        assert path in spec["paths"], f"Шлях '{path}' відсутній у специфікації"

    def test_root_get(self, spec):
        root = spec["paths"]["/"]
        assert "get" in root
        assert "200" in root["get"]["responses"]

    def test_auth_register_post(self, spec):
        op = spec["paths"]["/auth/register"]["post"]
        assert "requestBody" in op
        assert "201" in op["responses"]
        assert "400" in op["responses"]

    def test_auth_login_post(self, spec):
        op = spec["paths"]["/auth/login"]["post"]
        assert "requestBody" in op
        assert "200" in op["responses"]
        assert "401" in op["responses"]

    def test_auth_refresh_post(self, spec):
        op = spec["paths"]["/auth/refresh"]["post"]
        assert "requestBody" in op
        assert "200" in op["responses"]
        assert "401" in op["responses"]

    def test_books_get(self, spec):
        op = spec["paths"]["/books/"]["get"]
        assert "200" in op["responses"]
        assert "401" in op["responses"]
        param_names = [p["name"] for p in op.get("parameters", [])]
        assert "skip" in param_names
        assert "limit" in param_names

    def test_books_post(self, spec):
        op = spec["paths"]["/books/"]["post"]
        assert "requestBody" in op
        assert "201" in op["responses"]
        assert "401" in op["responses"]

    def test_books_get_by_id(self, spec):
        op = spec["paths"]["/books/{book_id}"]["get"]
        assert "200" in op["responses"]
        assert "404" in op["responses"]
        assert "401" in op["responses"]
        param_names = [p["name"] for p in op.get("parameters", [])]
        assert "book_id" in param_names

    def test_books_delete(self, spec):
        op = spec["paths"]["/books/{book_id}"]["delete"]
        assert "204" in op["responses"]
        assert "404" in op["responses"]
        assert "401" in op["responses"]

    def test_books_endpoints_require_auth(self, spec):
        """Усі операції з /books/ мають вимагати BearerAuth."""
        for method in ("get", "post"):
            op = spec["paths"]["/books/"][method]
            security = op.get("security", [])
            assert any("BearerAuth" in s for s in security), (
                f"/{method} /books/ повинен мати BearerAuth"
            )

    def test_auth_endpoints_no_auth_required(self, spec):
        """Ендпоінти /auth/* повинні бути публічними (security: [])."""
        for path in ("/auth/register", "/auth/login", "/auth/refresh"):
            op = list(spec["paths"][path].values())[0]
            security = op.get("security")
            assert security == [] or security is None, (
                f"{path} не повинен вимагати авторизацію"
            )


class TestSpecSchemas:
    @pytest.mark.parametrize("schema_name", EXPECTED_SCHEMAS)
    def test_schema_exists(self, spec, schema_name):
        schemas = spec["components"].get("schemas", {})
        assert schema_name in schemas, f"Схема '{schema_name}' відсутня"

    def test_book_create_required_fields(self, spec):
        schema = spec["components"]["schemas"]["BookCreate"]
        required = schema.get("required", [])
        for field in ("title", "author", "year"):
            assert field in required, f"Поле '{field}' має бути обов'язковим у BookCreate"

    def test_book_response_has_id(self, spec):
        schema = spec["components"]["schemas"]["BookResponse"]
        assert "_id" in schema.get("properties", {}), "BookResponse повинен мати поле '_id'"

    def test_book_status_enum(self, spec):
        schema = spec["components"]["schemas"]["BookStatus"]
        enum_values = schema.get("enum", [])
        assert "available" in enum_values
        assert "borrowed" in enum_values

    def test_paginated_response_fields(self, spec):
        schema = spec["components"]["schemas"]["PaginatedBookResponse"]
        props = schema.get("properties", {})
        for field in ("count", "skip", "limit", "books"):
            assert field in props, f"Поле '{field}' відсутнє у PaginatedBookResponse"

    def test_token_schema_fields(self, spec):
        schema = spec["components"]["schemas"]["Token"]
        props = schema.get("properties", {})
        assert "access_token" in props
        assert "refresh_token" in props
        assert "token_type" in props

    def test_user_create_required_fields(self, spec):
        schema = spec["components"]["schemas"]["UserCreate"]
        required = schema.get("required", [])
        assert "email" in required
        assert "password" in required

    def test_responses_have_examples(self, spec):
        """Ключові ендпоінти повинні мати examples для Prism."""
        paths_to_check = [
            ("/books/", "get", "200"),
            ("/books/", "post", "201"),
            ("/books/{book_id}", "get", "200"),
            ("/auth/login", "post", "200"),
            ("/auth/register", "post", "201"),
        ]
        for path, method, status_code in paths_to_check:
            op = spec["paths"][path][method]
            response = op["responses"][status_code]
            content = response.get("content", {})
            has_example = False
            for media_type, media in content.items():
                if "example" in media or "examples" in media:
                    has_example = True
                    break
                schema_ref = media.get("schema", {})
                if schema_ref:
                    has_example = True
                    break
            assert has_example, (
                f"{method.upper()} {path} -> {status_code}: відсутній example для Prism"
            )
