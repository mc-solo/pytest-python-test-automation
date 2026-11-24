# Testing

## What is tested

| File | Marker | Tests | Coverage |
| --- | --- | --- | --- |
| `tests/test_api.py` | `api` | 9 | JSONPlaceholder `/posts` and `/users`: list, single item, create (POST), full update (PUT), partial update (PATCH), delete (DELETE), and negative cases (missing post and invalid resource, both 404) |
| `tests/test_api_negative.py` | `api` | 15 | API negative and schema tests: invalid ids (missing user, non-numeric post/user id, PUT to a missing post, all 404), create with missing required fields, wrong HTTP method (POST to `/posts/1`, PUT/PATCH/DELETE on the `/posts` collection, all 404), and response-schema validation for every post and user (required fields, field types, nested `address`/`company`/`geo`, valid email) |
| `tests/test_utils.py` | `unit` | 21 | Unit tests for the helpers in `src/utils.py`: `build_post_payload`, `is_valid_email`, `format_user_name`. No network. |
| `tests/test_ui_helper.py` | `utils` | 13 | Unit tests for the UI helpers in `src/ui_helper.py`: `format_post_title`, `truncate_text`, `render_post_summary`, `build_user_badge`. No network. |

Total: 58 tests (43 before, plus 15 negative/schema tests).

Note: JSONPlaceholder is a fake API that does not persist writes.
POST returns 201 with a fake id, PUT/PATCH return 200 with the
sent body, DELETE returns 200 with `{}`. The tests assert that
documented fake-API behaviour, not real storage. Two quirks the
negative tests document rather than fight: the fake API does not
validate required fields, so `POST /posts` with missing fields
still returns 201 and the response simply omits the missing
fields; and `PATCH` / `DELETE` on a missing post return 200, so
only the `PUT` to a missing post (404) is asserted.

## How to run

```bash
# Full suite (from the project root, venv activated)
python -m pytest

# Quiet summary only
python -m pytest -q

# Only the API tests, only the unit tests, or only the utils tests
# (-m api runs both test_api.py and test_api_negative.py)
python -m pytest -m api
python -m pytest -m unit
python -m pytest -m utils

# Only the negative/schema tests
python -m pytest tests/test_api_negative.py

# One file, or one test by name
python -m pytest tests/test_api.py
python -m pytest tests/test_api.py::test_create_post -v
```

## Reports and coverage

```bash
# Self-contained HTML report (git-ignored, opens in a browser)
python -m pytest --html=report.html --self-contained-html

# Allure report (needs allure-pytest, in requirements.txt, and the
# Allure commandline installed separately: https://allurereport.org)
# The negative/schema tests carry @allure.feature / @allure.story
# markers and allure.step blocks; the other tests have none yet.
python -m pytest --alluredir=allure-results
allure serve allure-results

# Coverage of src/ is on by default (see pytest.ini): terminal report
# plus a 90% fail-under threshold. For the HTML report as well:
python -m pytest --cov-report=html
```

Coverage threshold: `pytest.ini` sets `--cov-fail-under=90`, so a
run fails if `src/` coverage drops below 90%. The suite was at 100%
before the UI helper was added; the new tests keep it covered.

## Where test data lives

Expected values are not hard-coded in the tests. They live in
`test-data/*.json` and are loaded by `conftest.py` fixtures
(`posts_data`, `users_data`, `sample_post_payload`,
`sample_post_update`) or, for the unit tests, at module level in
`tests/test_utils.py`:

- `test-data/posts.json` — post payloads, endpoints, expected
  status codes, ids, required fields.
- `test-data/users.json` — user endpoint, required fields, a known
  user used by the name-format unit tests.
- `test-data/negative.json` — negative and schema cases for
  `tests/test_api_negative.py`: the missing user id, the
  non-numeric id, incomplete create payloads with the fields each
  one is missing, wrong-method cases (method plus the endpoint key
  from `posts.json`), and the post/user field-type maps plus the
  nested `address` / `geo` / `company` required fields.
- `test-data/utils.json` — input/expected pairs for
  `build_post_payload`, `is_valid_email`, `format_user_name`.
- `test-data/ui.json` — input/expected pairs for the UI helpers
  (`format_post_title`, `truncate_text`, `render_post_summary`,
  `build_user_badge`).

To change an expected value, edit the JSON file, not the test.
To point the suite at another API, set `API_BASE_URL` in `.env`
(see `docs/SETUP.md`); do not edit a URL inside a test.

## Result observed

Ran `.venv/bin/python -m pytest -q` on 2026-11-20 with
Python 3.12.3 and pytest 9.2.0: **30 passed** (9 API tests,
21 unit tests). The previous run on 2026-11-18 was 29 passed;
the count rose by 1 because the blank-name fallback case in
`format_user_name` is now two separate parametrized cases
(empty string and whitespace-only) instead of one test with
two asserts. No test logic changed.

The UI helper tests (`tests/test_ui_helper.py`, 13 tests) were
added after that run and have **not been run yet**; the total
is 43 tests on paper until the suite is run again.

The negative/schema tests (`tests/test_api_negative.py`, 15 tests)
were added after that run as well and have **not been run yet**;
the total is 58 tests on paper until the suite is run again.
