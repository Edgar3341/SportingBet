import allure


@allure.title("Successfully place a single pre-match football bet")
def test_place_single_bet_successfully(user_login):
    user_login.place_single_bet_successfully()


@allure.title("API rejects stake below the €1.00 minimum")
def test_api_rejects_stake_below_minimum(user_login):
    user_login.assert_api_rejects_stake_below_minimum()
