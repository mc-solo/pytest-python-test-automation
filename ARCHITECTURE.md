# Architecture

A small Python API + unit test project built with pytest and
requests. The API tests run against the public JSONPlaceholder
fake API. It does not store anything: POST/PUT/PATCH/DELETE
return simulated responses, not real saved data.

## Folder tree

```text
pytest-python-test-automation/
├── .env.example          # Safe default env keys (copy to .env, never commit .env)
├── .gitignore            # Ignores .venv, caches, coverage, reports, .env
├── ARCHITECTURE.md       # This file
├── README.md             # Overview, setup, run commands, results
├── conftest.py           # Fixtures only: wires config + test-data into tests
├── pytest.ini            # testpaths, markers (api, unit)
├── requirements.txt      # pytest, requests, pytest-html, pytest-cov
├── config/
│   ├── __init__.py       # Re-exports Settings, get_settings, settings
│   └── settings.py       # THE ONLY place with a URL/timeout default
├── docs/
│   ├── SETUP.md          # Install, venv, configuration
│   └── TESTING.md        # What is tested, run commands, reports/coverage
├── src/
│   ├── __init__.py
│   └── utils.py          # Pure helpers under test, no network, no config
├── test-data/
│   ├── posts.json        # Post payloads, endpoints, status codes, ids
│   ├── users.json        # User endpoint, required fields, known user
│   └── utils.json        # Input/expected pairs for the unit tests
└── tests/
    ├── __init__.py
    ├── test_api.py       # 9 live API tests (marker: api)
    └── test_utils.py     # 21 unit tests (marker: unit)
```

## Why each folder exists

| Folder | Why |
| --- | --- |
| `config/` | One source of truth for environment-dependent values (base URL, timeout). Nothing else in the repo knows a URL or a timeout. Change the target API in one place. |
| `test-data/` | Expected values and payloads as data, not code. Changing an expected title, id, or status code is a JSON edit, not a test edit, and the same data can be reused by any test. |
| `src/` | The code under test. Pure helpers with no network calls, no config imports, and no test data, so unit tests stay fast and offline. |
| `tests/` | Test logic only. Tests import config (via fixtures) and test-data (via fixtures or module-level load) and assert behaviour. They contain no base URL, credential, timeout, or expected literal. |
| `docs/` | Setup and testing guides kept out of the README so the README stays a short overview. |
| `conftest.py` (root) | The wiring layer: builds the session fixture from config and loads test-data JSON into fixtures. It is the only file that touches both `config/` and `test-data/`. |

## Data flow

```text
.env / environment vars
        │
        ▼
config/settings.py  ── get_settings() ──► Settings(api_base_url, request_timeout)
        │
        ▼
conftest.py
  ├── base_url fixture ──────────────► tests (build request URLs)
  ├── api_session fixture ───────────► tests (requests Session; every call
  │                                     uses settings.request_timeout unless
  │                                     the test passes timeout= explicitly)
  ├── posts_data / users_data ───────► tests (endpoints, status codes, ids)
  └── sample_post_payload /           ► tests (payloads from test-data)
      sample_post_update
        │
        ▼
tests/test_api.py  ──► JSONPlaceholder API ──► asserts on status/body
tests/test_utils.py ──► src/utils.py (local only, no network)
        ▲
        │  input/expected pairs loaded at module level
test-data/utils.json
```

Key rule: values flow in one direction, config/test-data →
conftest → tests. `src/` never imports `config/` or `test-data/`,
and tests never define a URL, timeout, or expected value inline.

## How config, test-data, src, and tests connect

1. `config/settings.py` reads `API_BASE_URL` and
   `REQUEST_TIMEOUT` from the environment (loading `.env` first
   if present, without overriding real env vars) and exposes
   them as an immutable `Settings` dataclass via `get_settings()`.
2. `conftest.py` calls `get_settings()` once per session and
   exposes `base_url` and `api_session`. The session is a small
   `requests.Session` subclass that injects the configured
   timeout into every request.
3. `conftest.py` also loads `test-data/posts.json` and
   `test-data/users.json` into session fixtures, and derives the
   post payload fixtures from `posts.json`.
4. `tests/test_api.py` builds URLs from `base_url` + endpoint
   templates from the JSON data, and asserts status codes and
   fields from the same JSON data.
5. `tests/test_utils.py` loads `test-data/utils.json` at module
   level and parametrizes every case from it. It imports only
   `src/utils.py`, which is pure logic with no I/O.

## How to add a new test

**New API test** (e.g. `GET /comments`):

1. Add the endpoint, expected status, and any expected fields
   to `test-data/posts.json` (or a new `test-data/<name>.json`
   file, plus a matching fixture in `conftest.py`).
2. Add a test function in `tests/test_api.py` using the
   `api_session`, `base_url`, and data fixtures. Mark it with
   the module-level `pytest.mark.api` (already applied).
3. Run `python -m pytest -m api -v`.

**New unit test** (e.g. a new helper in `src/utils.py`):

1. Add the helper to `src/utils.py` (no network, no config).
2. Add input/expected cases to `test-data/utils.json`.
3. Add a parametrized test class in `tests/test_utils.py`
   reading those cases.
4. Run `python -m pytest -m unit -v`.

**New target API or timeout**: set `API_BASE_URL` /
`REQUEST_TIMEOUT` in `.env` (copied from `.env.example`) or
as environment variables. Do not edit a test or `src/`.
