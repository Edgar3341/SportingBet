import requests

from config import BASE_URL, DEFAULT_TIMEOUT, USER_ID_HEADER


class SportsBettingApi:
    """HTTP client for Sports Betting API. Auth: x-user-id header."""

    def __init__(self, user_id: str, base_url: str | None = None):
        self.base_url = (base_url or BASE_URL or "").rstrip("/")
        if not self.base_url:
            raise ValueError("BASE_URL is missing. Set it in the .env file.")
        if not user_id:
            raise ValueError("user_id is required.")

        self.session = requests.Session()
        self.session.headers.update(
            {
                USER_ID_HEADER: user_id,
                "Accept": "application/json",
            }
        )

    def get_matches(self) -> requests.Response:
        return self.session.get(f"{self.base_url}/api/matches", timeout=DEFAULT_TIMEOUT)

    def get_balance(self) -> requests.Response:
        return self.session.get(f"{self.base_url}/api/balance", timeout=DEFAULT_TIMEOUT)

    def reset_balance(self) -> requests.Response:
        return self.session.post(
            f"{self.base_url}/api/reset-balance", timeout=DEFAULT_TIMEOUT
        )

    def place_bet(self, match_id: str, selection: str, stake: float) -> requests.Response:
        return self.session.post(
            f"{self.base_url}/api/place-bet",
            json={"matchId": match_id, "selection": selection, "stake": stake},
            timeout=DEFAULT_TIMEOUT,
        )
