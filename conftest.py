import sys
from pathlib import Path

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

ROOT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT_DIR))

from api.sports_betting_api import SportsBettingApi
from config import BASE_URL, USER_ID
from main import UpcomingFootballMatchesPage


@pytest.fixture(scope="session")
def base_url():
    assert BASE_URL, "Set BASE_URL in .env"
    return BASE_URL.rstrip("/")


@pytest.fixture(scope="session")
def user_id():
    assert USER_ID, "Set user_id in .env"
    return USER_ID


@pytest.fixture
def api_client(user_id, base_url):
    return SportsBettingApi(user_id=user_id, base_url=base_url)


@pytest.fixture
def driver():
    options = Options()
    options.add_argument("--window-size=1440,900")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),options=options,)
    yield driver
    driver.quit()


@pytest.fixture
def user_login(driver, api_client, user_id, base_url):
    """Authenticate via API, then open the UI with ?user-id=."""
    assert api_client.get_balance().status_code == 200

    page = UpcomingFootballMatchesPage(
        driver,f"{base_url}/?user-id={user_id}",api_client=api_client,)
    page.open()
    page.wait_until_loaded()
    yield page
