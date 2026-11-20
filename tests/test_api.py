"""API tests against the public JSONPlaceholder fake API.

JSONPlaceholder does not persist writes: POST returns 201 with a fake
id, PUT/PATCH return 200 with the sent body, DELETE returns 200.
The tests assert the documented fake-API behaviour, not real storage.

All endpoints, payloads, ids, and expected status codes come from
``test-data/posts.json`` and ``test-data/users.json`` via the
``posts_data`` / ``users_data`` fixtures in ``conftest.py``. The
base URL and timeout come from ``config/settings.py``. This file
holds test logic only: no hard-coded URL, payload, or expected value.
"""

import pytest

pytestmark = pytest.mark.api


def _url(base_url, template, **params):
    """Fill an endpoint template from test-data, e.g. '/posts/{id}'."""
    return base_url + template.format(**params)


def test_get_all_posts_returns_list(api_session, base_url, posts_data):
    response = api_session.get(_url(base_url, posts_data["endpoints"]["posts"]))
    assert response.status_code == posts_data["expected_status"]["ok"]
    posts = response.json()
    assert isinstance(posts, list)
    assert len(posts) > 0
    for post in posts[: posts_data["list_sample_size"]]:
        assert set(post.keys()) >= set(posts_data["post_required_fields"])
        assert isinstance(post["id"], int)
        assert isinstance(post["title"], str) and post["title"]


def test_get_single_post(api_session, base_url, posts_data):
    expected = posts_data["single_post"]
    response = api_session.get(
        _url(base_url, posts_data["endpoints"]["post_by_id"], id=expected["id"])
    )
    assert response.status_code == posts_data["expected_status"]["ok"]
    post = response.json()
    assert post["id"] == expected["id"]
    assert post["userId"] == expected["user_id"]
    assert isinstance(post["title"], str) and post["title"]
    assert isinstance(post["body"], str) and post["body"]


def test_create_post(api_session, base_url, posts_data, sample_post_payload):
    response = api_session.post(
        _url(base_url, posts_data["endpoints"]["posts"]), json=sample_post_payload
    )
    assert response.status_code == posts_data["expected_status"]["created"]
    created = response.json()
    assert created["title"] == sample_post_payload["title"]
    assert created["body"] == sample_post_payload["body"]
    assert created["userId"] == sample_post_payload["userId"]
    assert isinstance(created["id"], int)


def test_update_post_put(api_session, base_url, posts_data, sample_post_update):
    expected = posts_data["single_post"]
    response = api_session.put(
        _url(base_url, posts_data["endpoints"]["post_by_id"], id=expected["id"]),
        json=sample_post_update,
    )
    assert response.status_code == posts_data["expected_status"]["ok"]
    updated = response.json()
    assert updated["id"] == expected["id"]
    assert updated["title"] == sample_post_update["title"]
    assert updated["body"] == sample_post_update["body"]


def test_partial_update_post_patch(api_session, base_url, posts_data):
    expected = posts_data["single_post"]
    patch = posts_data["patch_payload"]
    response = api_session.patch(
        _url(base_url, posts_data["endpoints"]["post_by_id"], id=expected["id"]),
        json=patch,
    )
    assert response.status_code == posts_data["expected_status"]["ok"]
    patched = response.json()
    assert patched["id"] == expected["id"]
    assert patched["title"] == patch["title"]


def test_delete_post(api_session, base_url, posts_data):
    expected = posts_data["single_post"]
    response = api_session.delete(
        _url(base_url, posts_data["endpoints"]["post_by_id"], id=expected["id"])
    )
    assert response.status_code == posts_data["expected_status"]["ok"]
    assert response.json() == {}


def test_get_all_users(api_session, base_url, posts_data, users_data):
    response = api_session.get(_url(base_url, users_data["endpoints"]["users"]))
    assert response.status_code == posts_data["expected_status"]["ok"]
    users = response.json()
    assert isinstance(users, list)
    assert len(users) > 0
    for user in users[: users_data["list_sample_size"]]:
        assert set(user.keys()) >= set(users_data["user_required_fields"])
        assert "@" in user["email"]


def test_get_missing_post_returns_404(api_session, base_url, posts_data):
    response = api_session.get(
        _url(
            base_url,
            posts_data["endpoints"]["post_by_id"],
            id=posts_data["missing_post_id"],
        )
    )
    assert response.status_code == posts_data["expected_status"]["not_found"]
    assert response.json() == {}


def test_get_invalid_resource_returns_404(api_session, base_url, posts_data):
    response = api_session.get(
        _url(base_url, posts_data["endpoints"]["invalid_resource"])
    )
    assert response.status_code == posts_data["expected_status"]["not_found"]
