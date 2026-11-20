# pytest-python-test-automation

A small Python API + unit test project built with pytest and requests.
The API tests run against the public JSONPlaceholder fake API
(https://jsonplaceholder.typicode.com). It does not store anything, so
POST/PUT/PATCH/DELETE return simulated responses, not real saved data.

## Folder tree

```text
pytest-python-test-automation/
├── .env.example          # Safe default env keys (copy to .env)
├── ARCHITECTURE.md       # Folder purposes, data flow, how to add a test
├── conftest.py           # Fixtures: config + test-data wired into tests
├── pytest.ini            # testpaths, markers (api, unit)
├── requirements.txt      # pytest, requests, pytest-html, pytest-cov
├── config/               # settings.py: base URL + timeout from env vars
├── docs/                 # SETUP.md, TESTING.md
├── src/                  # utils.py: pure helpers under test, no network
├── test-data/            # posts.json, users.json, utils.json
└── tests/                # test_api.py (9 API), test_utils.py (21 unit)
```

See `ARCHITECTURE.md` for why each folder exists and how
config, test-data, `src/`, and `tests/` connect.

## What is covered

- `tests/test_api.py` (9 tests): GET /posts list and fields, GET /posts/1,
  POST /posts, PUT /posts/1, PATCH /posts/1, DELETE /posts/1, GET /users,
  and negative cases (GET /posts/999999 and GET /invalid, both 404).
- `tests/test_utils.py` (21 tests): unit tests for the helpers in
  `src/utils.py`: `build_post_payload`, `is_valid_email`, `format_user_name`.
  All cases are loaded from `test-data/utils.json`.
- `src/utils.py`: the helpers themselves, no network calls.
- `config/settings.py`: base URL and timeout from env vars
  (`API_BASE_URL`, `REQUEST_TIMEOUT`); the only place a URL or
  timeout default lives. `conftest.py` imports it and builds the
  `base_url` / `api_session` fixtures from it.
- `test-data/`: payloads, endpoints, expected status codes, ids,
  and unit-test cases as JSON, loaded by the tests. No URL,
  timeout, credential, or expected value is hard-coded in a test.

## Install

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Optional configuration (defaults work out of the box):

```bash
cp .env.example .env   # edit API_BASE_URL / REQUEST_TIMEOUT if needed
```

Full setup guide: `docs/SETUP.md`.

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

Coverage of `src/`:

```bash
python -m pytest --cov=src --cov-report=term-missing
```

Full testing guide: `docs/TESTING.md`.

## Result observed

Ran `.venv/bin/python -m pytest -q` on 2026-11-20 with Python 3.12.3 and
pytest 9.2.0: **30 passed in 2.26s** (9 API tests, 21 unit tests),
live against JSONPlaceholder. Coverage of `src/`: 100%.

The previous run on 2026-11-18 was 29 passed in 2.28s; the count
rose by 1 because the blank-name fallback case in `format_user_name`
is now two separate parametrized cases (empty string and
whitespace-only) instead of one test with two asserts.
No test logic changed.
