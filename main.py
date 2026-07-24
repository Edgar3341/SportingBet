import re
from decimal import Decimal, ROUND_HALF_UP

import allure
from selenium.common.exceptions import ElementClickInterceptedException

from api.sports_betting_api import SportsBettingApi
from locators.upcoming_football_matches_page_locators import (
    UpcomingFootballMatchesPageLocators,
)
from pages.base_page import BasePage


class UpcomingFootballMatchesPage(BasePage):
    locators = UpcomingFootballMatchesPageLocators()

    def __init__(self, driver, url, api_client: SportsBettingApi):
        super().__init__(driver, url)
        self.api = api_client

    @staticmethod
    def _money(value) -> Decimal:
        return Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    @staticmethod
    def _parse_amount(text: str) -> Decimal:
        match = re.search(r"-?\d+(?:\.\d+)?", text.replace(",", ""))
        if not match:
            raise AssertionError(f"Cannot parse amount from: {text!r}")
        return UpcomingFootballMatchesPage._money(match.group())

    def _text(self, locator, timeout=10) -> str:
        return self.element_is_visible(locator, timeout=timeout).text

    def _amount(self, locator, timeout=10) -> Decimal:
        return self._parse_amount(self._text(locator, timeout=timeout))

    def wait_until_loaded(self):
        self.element_is_visible(self.locators.APP_SHELL, timeout=15)
        self.element_is_visible(self.locators.MATCH_LIST, timeout=15)
        self.element_is_visible(self.locators.HEADER_BALANCE, timeout=15)

    def select_outcome(self, match_id: str, selection: str):
        button = self.element_is_clickable(
            self.locators.odds_button(match_id, selection), timeout=10
        )
        self.driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center'});", button
        )
        try:
            button.click()
        except ElementClickInterceptedException:
            self.driver.execute_script("arguments[0].click();", button)

        value = button.find_element(*self.locators.ODDS_BUTTON_VALUE).text
        return self._parse_amount(value)

    def enter_stake(self, stake):
        field = self.element_is_visible(self.locators.STAKE_INPUT)
        field.clear()
        field.send_keys(str(stake))

    @allure.step("Place a single pre-match bet end-to-end")
    def place_single_bet_successfully(
        self,
        match_id: str = "premier-league-manutd-chelsea",
        selection: str = "HOME",
        stake: Decimal = Decimal("10.00"),
    ):
        """Critical revenue journey: select → stake → payout → place → receipt → balance."""
        assert self.api.reset_balance().status_code == 200
        starting_balance = self._money(self.api.get_balance().json()["balance"])

        self.open()
        self.wait_until_loaded()
        assert self._amount(self.locators.HEADER_BALANCE) == starting_balance

        selected_odds = self.select_outcome(match_id, selection)
        teams = self._text(self.locators.BET_SELECTION_TEAMS)
        market = self._text(self.locators.BET_SELECTION_MARKET)
        assert "Manchester Utd" in teams and "Chelsea" in teams
        assert "Match Winner" in market
        assert self._amount(self.locators.BET_SELECTION_ODDS) == selected_odds

        self.enter_stake(stake)
        expected_payout = self._money(stake * selected_odds)
        assert self._amount(self.locators.POTENTIAL_PAYOUT) == expected_payout

        self.element_is_clickable(self.locators.PLACE_BET_BUTTON).click()
        self.element_is_visible(self.locators.SUCCESS_MODAL, timeout=15)

        assert self._text(self.locators.SUCCESS_BET_ID).strip()
        receipt_match = self._text(self.locators.SUCCESS_MATCH)
        assert "Manchester Utd" in receipt_match and "Chelsea" in receipt_match
        assert self._amount(self.locators.SUCCESS_STAKE) == self._money(stake)
        assert self._amount(self.locators.SUCCESS_ODDS) == selected_odds

        balance_after = self._money(self.api.get_balance().json()["balance"])
        assert balance_after == self._money(starting_balance - stake)

        self.element_is_clickable(self.locators.SUCCESS_CLOSE).click()
        self.element_is_not_visible(self.locators.SUCCESS_MODAL, timeout=10)
        assert self._text(self.locators.BET_SLIP_COUNT).strip() == "0"

    @allure.step("API: reject stake below the €1.00 minimum")
    def assert_api_rejects_stake_below_minimum(
        self,
        match_id: str = "premier-league-manutd-chelsea",
        selection: str = "DRAW",
        stake: float = 0.99,
    ):
        """Minimum stake is a financial control - validate it directly via API."""
        assert self.api.reset_balance().status_code == 200
        before = self._money(self.api.get_balance().json()["balance"])

        response = self.api.place_bet(match_id, selection, stake)
        body = response.json()

        assert response.status_code == 422
        assert body.get("error") == "invalid_stake_min"
        assert "1.00" in body.get("message", "")
        assert self._money(self.api.get_balance().json()["balance"]) == before
