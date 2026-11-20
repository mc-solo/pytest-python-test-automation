# Setup

## Requirements

- Python 3.12 or newer (`python3 --version`)
- Internet access: the API tests call the public JSONPlaceholder
  fake API (`https://jsonplaceholder.typicode.com`). The unit tests
  need no network.

## Install

```bash
git clone <repo-url>
cd pytest-python-test-automation

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

On Windows, activate with `.venv\Scripts\activate`.

## Configure (optional)

Defaults work out of the box. To point the suite at a different
API base URL or change the request timeout, copy the example env
file and edit it:

```bash
cp .env.example .env
```

`.env` keys:

| Key | Default | Meaning |
| --- | --- | --- |
| `API_BASE_URL` | `https://jsonplaceholder.typicode.com` | API under test |
| `REQUEST_TIMEOUT` | `10` | Per-request timeout, in seconds |

Environment variables set in your shell always win over `.env`.
`.env` is git-ignored: never commit real credentials. See
`config/settings.py` for how values are resolved.

## Verify the install

```bash
python -m pytest -q
```

You should see all tests pass. See `docs/TESTING.md` for the
full list of run commands, markers, reports, and coverage.
