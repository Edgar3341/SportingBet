# Single Bet Placement — Test Plan

## Scope

This test plan covers the core single pre-match football bet placement flow across the desktop web UI and supporting API.

## Preconditions

- User opens the application with a valid `user-id`.
- User has a positive EUR balance.
- Match catalogue contains upcoming football matches.
- Chrome desktop browser is used.
- User balance can be restored through `POST /api/reset-balance`.

## Specification Clarification

The specification contains a conflict regarding the minimum stake:

- Business Rules: minimum stake is €1.00
- Validation Rules: minimum stake is €1.01
- Expected UI message: “Minimum stake is €1.00”

For this test plan, €1.00 is treated as the valid minimum because it is stated in the main business rules and expected UI.

---

## TC-01 - Successfully Place a Single Bet

**Priority:** Critical

**Risk Rationale:**  
Bet placement is the product’s core revenue-generating journey. Incorrect balance deduction, payout calculation, selection data, or receipt information may result in financial loss and loss of customer trust.

### Steps

1. Open the application using a valid user ID.
2. Record the current balance.
3. Select an outcome from an upcoming football match.
4. Verify that the selected match and outcome appear in the bet slip.
5. Enter a valid stake of `€10.00`.
6. Verify the displayed potential payout.
7. Click **Place Bet**.
8. Observe the button and page state while the request is being processed.
9. Verify the success receipt.
10. Close the receipt.

### Expected Result

- Only the selected outcome is highlighted.
- The bet slip displays the correct match, selection, odds and stake.
- Potential payout equals `stake × odds`.
- The Place Bet button displays an in-progress state such as `Placing...`.
- Only one placement request is processed.
- A success receipt is displayed containing:
  - Bet ID
  - Correct home and away teams
  - Selected outcome
  - Stake
  - Odds at placement
  - Potential payout
  - Placement timestamp
- All receipt values match the values shown before placement.
- The balance decreases by exactly `€10.00`.
- Currency is consistently displayed and returned as EUR.
- Closing the receipt clears the active selection and stake.

---
## TC-02 - Validate Minimum and Maximum Stake Boundaries

**Priority:** Critical

**Risk Rationale:**  
Stake limits are financial controls. Accepting stakes outside the permitted range may expose the operator to financial, regulatory and responsible-gambling risks.

### Steps

1. Select a valid match outcome.
2. Enter `€0.99`.
3. Attempt to place the bet.
4. Enter `€1.00`.
5. Place the bet or verify that placement becomes available.
6. Reset the balance and select another valid outcome.
7. Enter `€100.00`.
8. Place the bet or verify that placement becomes available.
9. Reset the balance and select another valid outcome.
10. Enter `€100.01`.
11. Attempt to place the bet.

### Expected Result

- `€0.99` is rejected.
- A clear minimum-stake validation message is shown.
- `€1.00` is accepted as the minimum valid boundary, subject to specification confirmation.
- `€100.00` is accepted as the maximum valid boundary.
- `€100.01` is rejected.
- A clear `Maximum stake is €100.00` message is shown.
- Invalid values cannot be submitted through the UI.
- The API also rejects out-of-range values with an appropriate `422` response.
- Balance remains unchanged after rejected attempts.

---

## TC-03 - Replace the Active Selection with Another Outcome

**Priority:** High

**Risk Rationale:**  
The application supports single bets only. Retaining multiple active selections or submitting the previous selection could create an unintended accumulator or place a bet on the wrong outcome.

### Steps

1. Select the home-win outcome for one match.
2. Verify that it appears in the bet slip.
3. Select the draw outcome for the same match.
4. Verify the bet slip.
5. Select an outcome for a different match.
6. Verify the bet slip again.
7. Enter a valid stake.
8. Place the bet.

### Expected Result

- Selecting another outcome replaces the previous selection.
- Only one odds button remains selected at any time.
- The bet slip contains only the latest selected match and outcome.
- Previous selections are removed without leaving stale match, odds or payout data.
- The submitted request contains the latest:
  - `matchId`
  - `selection`
  - `stake`
- The receipt contains only the final selected match and outcome.



---

## TC-04 - Validate Stake Format, Precision and Required Input

**Priority:** High

**Risk Rationale:**  
Invalid stake formats may cause incorrect monetary calculations, rounding errors, API failures or inconsistent values between the UI and backend.

### Steps

1. Select a valid match outcome.
2. Leave the stake field empty and attempt to place the bet.
3. Enter alphabetic text such as `abc`.
4. Enter mixed input such as `10abc`.
5. Enter a negative value such as `-5`.
6. Enter zero.
7. Enter a value with more than two decimal places, such as `10.999`.
8. Enter a value containing multiple decimal separators, such as `10.2.5`.
9. Enter a valid decimal value such as `10.25`.

### Expected Result

- An empty stake cannot be submitted.
- Non-numeric, negative and zero values are rejected.
- Values with multiple decimal separators are rejected or prevented.
- Values with more than two decimal places are rejected and are not silently rounded.
- A clear validation message is displayed.
- `€10.25` is accepted.
- Potential payout is calculated using the exact accepted stake and displayed with valid currency precision.
- No invalid request is sent to the API from the UI.
- Rejected attempts do not change the balance.

---

## TC-05 - Prevent a Stake Greater Than the Available Balance

**Priority:** Critical

**Risk Rationale:**  
Allowing a user to spend more than their available balance creates direct financial exposure and may produce a negative or inconsistent account balance.

### Steps

1. Retrieve and record the current balance.
2. Select a valid match outcome.
3. Enter a stake equal to the current balance.
4. Verify whether placement is available.
5. Enter a stake `€0.01` greater than the current balance.
6. Attempt to place the bet.
7. Send the same excessive stake directly to `POST /api/place-bet`.

### Expected Result

- A stake equal to the available balance is accepted when it does not exceed the €100 per-bet maximum.
- A stake greater than the available balance is rejected.
- The UI displays a clear `Insufficient balance` message.
- The Place Bet action is blocked for an invalid stake.
- The API rejects the request using the documented validation error class.
- No bet is created.
- The balance remains unchanged and never becomes negative.
- Header and bet-slip balance values remain consistent.

---

## TC-06 - Apply Date and Odds Filters Using Inclusive Boundaries

**Priority:** High

**Risk Rationale:**  
Incorrect filtering can expose ineligible events, including past matches, or hide valid betting opportunities. This affects customer experience and may allow bets on events outside the supported pre-match scope.

### Steps

1. Open the match list with filters reset.
2. Confirm that only upcoming football matches are displayed.
3. Apply a single-day date filter matching a known event date.
4. Verify all displayed match dates.
5. Apply a date range containing known events on both the start and end dates.
6. Verify matches on both boundary dates are included.
7. Set an odds range using known minimum and maximum values.
8. Verify every displayed odds button against the selected range.
9. Enter an invalid odds range where minimum is greater than maximum.
10. Observe the displayed match count after each valid filter is applied.
11. Reset the filters.

### Expected Result

- Past events are not displayed or available for betting.
- A single-day filter displays only matches from that date.
- Date-range filtering is inclusive of both start and end dates.
- The odds filter includes odds equal to the selected minimum and maximum.
- Outcomes outside the selected odds range are not presented as matching results.
- An invalid odds range is rejected with clear feedback.
- The displayed match count reflects the actual filtered result set.
- Reset restores the full eligible match list and default filter labels.