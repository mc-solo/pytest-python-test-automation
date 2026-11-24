"""API negative and schema tests against the public JSONPlaceholder fake API.

Covers what ``tests/test_api.py`` does not: invalid ids, creates with
missing required fields, wrong HTTP methods, and response-schema
validation for posts and users.

JSONPlaceholder quirks asserted here (documented fake-API behaviour,
not real storage or real validation):

- ``POST /posts`` with missing fields still returns 201: the fake API
  does not enforce required fields, so the test asserts the created
  response is missing exactly the fields that were not sent.
- ``PUT /posts/999999`` returns 404, but ``PATCH`` / ``DELETE`` on a
  missing post return 200, so only the ``PUT`` case is asserted.
- A wrong method on a valid route (``POST /posts/1``, ``PUT`` /
  ``PATCH`` / ``DELETE`` on the ``/posts`` collection) returns 404.

Endpoints, payloads, ids, and expected status codes come from
``test-data/posts.json`` and ``test-data/users.json`` via the
``posts_data`` / ``users_data`` fixtures in ``conftest.py``. The
negative cases and schema shapes come from ``test-data/negative.json``,
loaded once at module level (the same pattern as
``tests/test_utils.py``) so the cases can feed ``parametrize``.
The base URL and timeout come from ``config/settings.py``. This file
holds test logic only: no hard-coded URL, payload, or expected value.

Allure: every class carries ``@allure.feature`` / ``@allure.story``
and every request/assert block is an ``allure.step``, so
``pytest --alluredir=allure-results`` plus ``allure serve`` renders
the run grouped by feature and story.
"""

import json
from pathlib import Path

import allure
import pytest

from src.utils import is_valid_email

pytestmark = pytest.mark.api

_NEGATIVE = json.loads(
    (Path(__file__).resolve().parent.parent / "test-data" / "negative.json")
    .read_text(encoding="utf-8")
)

# Type names used in test-data/negative.json -> real Python types.
_TYPE_MAP = {"int": int, "str": str, "dict": dict}


def _url(base_url, template, **params):
    """Fill an endpoint template from test-data, e.g. '/posts/{id}'."""
    return base_url + template.format(**params)


def _assert_field_types(item, field_types, label):
    """Assert every field in ``field_types`` exists and has the right type."""
    for field, type_name in field_types.items():
        assert field in item, f"{label} is missing field {field!r}: {item}"
        assert isinstance(item[field], _TYPE_MAP[type_name]), (
            f"{label} field {field!r} should be {type_name}, "
            f"got {type(item[field]).__name__}: {item[field]!r}"
        )


def _assert_post_schema(post, posts_data):
    """A post has every required field, of the right type, non-empty text."""
    assert set(post.keys()) >= set(posts_data["post_required_fields"])
    _assert_field_types(post, _NEGATIVE["post_field_types"], f"post {post.get('id')}")
    assert post["title"].strip()
    assert post["body"].strip()


def _assert_user_schema(user, users_data):
    """A user has every required field, of the right type, and valid nested objects."""
    assert set(user.keys()) >= set(users_data["user_required_fields"])
    _assert_field_types(user, _NEGATIVE["user_field_types"], f"user {user.get('id')}")
    assert user["name"].strip()
    assert user["username"].strip()
    assert is_valid_email(user["email"]), f"user email is not valid: {user['email']!r}"
    address = user["address"]
    assert set(address.keys()) >= set(_NEGATIVE["user_address_required_fields"])
    assert set(address["geo"].keys()) >= set(
        _NEGATIVE["user_address_geo_required_fields"]
    )
    company = user["company"]
    assert set(company.keys()) >= set(_NEGATIVE["user_company_required_fields"])
    assert company["name"].strip()


@allure.feature("API negative and schema")
@allure.story("Invalid IDs")
class TestInvalidIds:
    def test_get_missing_user_returns_404(
        self, api_session, base_url, posts_data, users_data
    ):
        with allure.step("GET a user id that does not exist"):
            response = api_session.get(
                _url(
                    base_url,
                    users_data["endpoints"]["user_by_id"],
                    id=_NEGATIVE["missing_user_id"],
                )
            )
        with allure.step("Assert 404 with an empty body"):
            assert response.status_code == posts_data["expected_status"]["not_found"]
            assert response.json() == {}

    def test_get_post_with_non_numeric_id_returns_404(
        self, api_session, base_url, posts_data
    ):
        with allure.step("GET /posts with a non-numeric id"):
            response = api_session.get(
                _url(
                    base_url,
                    posts_data["endpoints"]["post_by_id"],
                    id=_NEGATIVE["non_numeric_id"],
                )
            )
        with allure.step("Assert 404 with an empty body"):
            assert response.status_code == posts_data["expected_status"]["not_found"]
            assert response.json() == {}

    def test_get_user_with_non_numeric_id_returns_404(
        self, api_session, base_url, posts_data, users_data
    ):
        with allure.step("GET /users with a non-numeric id"):
            response = api_session.get(
                _url(
                    base_url,
                    users_data["endpoints"]["user_by_id"],
                    id=_NEGATIVE["non_numeric_id"],
                )
            )
        with allure.step("Assert 404 with an empty body"):
            assert response.status_code == posts_data["expected_status"]["not_found"]
            assert response.json() == {}

    def test_put_missing_post_returns_404(self, api_session, base_url, posts_data):
        with allure.step("PUT an update to a post id that does not exist"):
            response = api_session.put(
                _url(
                    base_url,
                    posts_data["endpoints"]["post_by_id"],
                    id=posts_data["missing_post_id"],
                ),
                json=posts_data["sample_post_update"],
            )
        with allure.step("Assert 404 with an empty body"):
            assert response.status_code == posts_data["expected_status"]["not_found"]
            assert response.json() == {}


@allure.feature("API negative and schema")
@allure.story("Create with missing required fields")
class TestCreateWithMissingFields:
    @pytest.mark.parametrize(
        "payload, missing_fields",
        [
            (case["payload"], case["missing_fields"])
            for case in _NEGATIVE["incomplete_post_payloads"]
        ],
        ids=[case["case"] for case in _NEGATIVE["incomplete_post_payloads"]],
    )
    def test_create_post_with_missing_fields(
        self, api_session, base_url, posts_data, payload, missing_fields
    ):
        with allure.step(f"POST /posts with payload missing {missing_fields}"):
            response = api_session.post(
                _url(base_url, posts_data["endpoints"]["posts"]), json=payload
            )
        with allure.step(
            "Assert the fake API still returns 201 (it does not validate)"
        ):
            assert response.status_code == posts_data["expected_status"]["created"]
        with allure.step("Assert the response omits exactly the missing fields"):
            created = response.json()
            assert isinstance(created["id"], int)
            for field in missing_fields:
                assert field not in created, (
                    f"response should not contain missing field {field!r}: {created}"
                )
            for field, value in payload.items():
                assert created[field] == value


@allure.feature("API negative and schema")
@allure.story("Wrong HTTP method")
class TestWrongHttpMethod:
    @pytest.mark.parametrize(
        "method, endpoint_key, needs_id",
        [
            (case["method"], case["endpoint_key"], case["needs_id"])
            for case in _NEGATIVE["wrong_method_cases"]
        ],
        ids=[case["case"] for case in _NEGATIVE["wrong_method_cases"]],
    )
    def test_wrong_http_method_returns_404(
        self, api_session, base_url, posts_data, method, endpoint_key, needs_id
    ):
        template = posts_data["endpoints"][endpoint_key]
        params = (
            {"id": posts_data["single_post"]["id"]} if needs_id else {}
        )
        with allure.step(f"{method} {template} (wrong method for this route)"):
            response = api_session.request(
                method,
                _url(base_url, template, **params),
                json=posts_data["sample_post_payload"],
            )
        with allure.step("Assert 404 with an empty body"):
            assert response.status_code == posts_data["expected_status"]["not_found"]
            assert response.json() == {}


@allure.feature("API negative and schema")
@allure.story("Response schema")
class TestResponseSchema:
    def test_posts_list_schema(self, api_session, base_url, posts_data):
        with allure.step("GET the full posts list"):
            response = api_session.get(
                _url(base_url, posts_data["endpoints"]["posts"])
            )
            assert response.status_code == posts_data["expected_status"]["ok"]
            posts = response.json()
        with allure.step("Assert every post matches the post schema"):
            assert isinstance(posts, list)
            assert len(posts) > 0
            for post in posts:
                _assert_post_schema(post, posts_data)

    def test_single_post_schema(self, api_session, base_url, posts_data):
        expected = posts_data["single_post"]
        with allure.step("GET a single known post"):
            response = api_session.get(
                _url(
                    base_url,
                    posts_data["endpoints"]["post_by_id"],
                    id=expected["id"],
                )
            )
            assert response.status_code == posts_data["expected_status"]["ok"]
            post = response.json()
        with allure.step("Assert the post matches the schema and known values"):
            _assert_post_schema(post, posts_data)
            assert post["id"] == expected["id"]
            assert post["userId"] == expected["user_id"]

    def test_users_list_schema(self, api_session, base_url, posts_data, users_data):
        with allure.step("GET the full users list"):
            response = api_session.get(
                _url(base_url, users_data["endpoints"]["users"])
            )
            assert response.status_code == posts_data["expected_status"]["ok"]
            users = response.json()
        with allure.step(
            "Assert every user matches the user schema, including address/company"
        ):
            assert isinstance(users, list)
            assert len(users) > 0
            for user in users:
                _assert_user_schema(user, users_data)

    def test_single_user_schema(self, api_session, base_url, posts_data, users_data):
        expected = _NEGATIVE["single_user"]
        known = users_data["known_user"]
        with allure.step("GET a single known user"):
            response = api_session.get(
                _url(
                    base_url,
                    users_data["endpoints"]["user_by_id"],
                    id=expected["id"],
                )
            )
            assert response.status_code == posts_data["expected_status"]["ok"]
            user = response.json()
        with allure.step("Assert the user matches the schema and known values"):
            _assert_user_schema(user, users_data)
            assert user["id"] == expected["id"]
            assert user["name"] == known["name"]
            assert user["username"] == known["username"]
