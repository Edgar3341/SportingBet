# Sports Betting QA Automation

Python + Selenium + requests automation for the
[Sports Betting QA Assessment App](https://qae-assignment-tau.vercel.app/?user-id=%3Cyour-user-id%3E).

## Stack

- Python 3
- Selenium WebDriver (latest Chrome)
- `requests` for API checks
- pytest + Allure

## Project structure

```text
SportsBetting/
├── api/
│   └── sports_betting_api.py   # API client
├── locators/                   # Page locators
├── pages/                      # Base page helpers
├── upcoming_football_match_page_tests/
│   └── test_priority.py        # Two high-value tests
├── conftest.py                 # Chrome + login fixtures
├── main.py                     # Page object + test journeys
├── config.py                   # Loads .env (BASE_URL, user_id)
├── requirements.txt
└── .env
```

## Setup

1. Install Python 3.10+.
2. Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

3. Create `.env` in the project root:

```env
BASE_URL=url-here
user_id=your-user-id-here
```

Both values are required. `config.py` reads them from `.env`.

4. Install Google Chrome (desktop) and [Allure Commandline](https://docs.qameta.io/allure/) if you want HTML reports.

## Authentication

UI login URL:

`{BASE_URL}/?user-id={user_id}`

API auth header:

`x-user-id: {user_id}`

The `user_login` fixture:

1. Calls `GET /api/balance` to verify API auth
2. Opens Chrome on the authenticated UI URL

## Run tests

```bash
source .venv/bin/activate
pytest -v --alluredir=allure-results
```

Run a single test:

```bash
pytest upcoming_football_match_page_tests/test_priority.py::test_place_single_bet_successfully
pytest upcoming_football_match_page_tests/test_priority.py::test_api_rejects_stake_below_minimum
```

## Allure report

```bash
pytest -v --alluredir=allure-results
allure serve allure-results
```

## Tests included

1. **E2E UI** — place a single pre-match bet (selection → stake → payout → receipt → API balance).
2. **API** — reject stake below the €1.00 minimum (`422 invalid_stake_min`) and keep balance unchanged.
