# pytest-python-test-automation

A small Python API + unit test project built with pytest and requests.
The API tests run against the public JSONPlaceholder fake API
(https://jsonplaceholder.typicode.com). It does not store anything, so
POST/PUT/PATCH/DELETE return simulated responses, not real saved data.

## What is covered

- `tests/test_api.py` (9 tests): GET /posts list and fields, GET /posts/1,
  POST /posts, PUT /posts/1, PATCH /posts/1, DELETE /posts/1, GET /users,
  and negative cases (GET /posts/999999 and GET /invalid, both 404).
- `tests/test_utils.py` (20 tests): unit tests for the helpers in
  `src/utils.py`: `build_post_payload`, `is_valid_email`, `format_user_name`.
- `src/utils.py`: the helpers themselves, no network calls.
- `conftest.py`: session fixtures for the base URL and a shared requests
  Session, plus sample post payloads.

## Install

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run

```bash
python -m pytest
```

Run only the API tests or only the unit tests:

```bash
python -m pytest -m api
python -m pytest -m unit
```

HTML report:

```bash
python -m pytest --html=report.html --self-contained-html
```

## Result observed

Ran `python -m pytest -q` on 2026-11-18 with Python 3.12.3 and
pytest 9.2.0: **29 passed in 2.28s** (9 API tests, 20 unit tests).
