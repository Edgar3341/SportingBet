from selenium.webdriver.common.by import By


class UpcomingFootballMatchesPageLocators:
    APP_SHELL = (By.ID, "app-shell")
    HEADER_BALANCE = (By.ID, "header-balance")
    MATCH_LIST = (By.ID, "match-list")

    ODDS_BUTTON_VALUE = (By.CSS_SELECTOR, ".oddsButtonValue")

    BET_SLIP_COUNT = (By.ID, "bet-slip-count")
    BET_SELECTION_TEAMS = (By.CSS_SELECTOR, "#bet-slip .betSelectionTeams")
    BET_SELECTION_MARKET = (By.CSS_SELECTOR, "#bet-slip .betSelectionMarket")
    BET_SELECTION_ODDS = (By.CSS_SELECTOR, "#bet-slip .betSelectionOdds")
    STAKE_INPUT = (By.ID, "bet-slip-stake-input")
    POTENTIAL_PAYOUT = (By.ID, "bet-slip-potential-payout")
    PLACE_BET_BUTTON = (By.ID, "bet-slip-place-bet")

    SUCCESS_MODAL = (By.ID, "modal-success")
    SUCCESS_BET_ID = (By.ID, "modal-success-bet-id")
    SUCCESS_MATCH = (By.ID, "modal-success-match")
    SUCCESS_STAKE = (By.ID, "modal-success-stake")
    SUCCESS_ODDS = (By.ID, "modal-success-odds")
    SUCCESS_PAYOUT = (By.ID, "modal-success-payout")
    SUCCESS_CLOSE = (By.ID, "modal-success-close")

    @staticmethod
    def odds_button(match_id: str, selection: str):
        return By.ID, f"odds-{match_id}-{selection.lower()}"
