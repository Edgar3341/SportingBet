# Single Bet Placement - Execution Results and Bug Reports

## Test Environment

- Application: Sports Betting QA Assessment App
- Platform: Desktop Web
- Browser: Latest Google Chrome
- User context: Valid `user-id` query parameter
- Test date: 23 July 2026

---

## BUG-01 - API Allows Betting When Balance Is Insufficient

**Severity:** Critical

### Reproduction Steps

1. Authenticate with a valid `user-id` (`x-user-id` header).
2. Call `POST /api/reset-balance`, then `GET /api/balance` and record the available balance.
3. Place bets until the remaining balance is low (for example `€20.00`).
4. Call `POST /api/place-bet` with a valid `matchId`, `selection`, and a `stake` greater than the remaining balance (for example `€30.00`).
5. Call `GET /api/balance` again.

### Expected Result

- The request is rejected with a clear insufficient-balance validation error.
- No bet is created.
- The account balance remains unchanged and never becomes negative.

### Actual Result

The API accepts the bet with HTTP `200` and returns a successful place-bet payload.

The persisted balance becomes negative. Example observed during automation:

- Balance before overspend: `€20.00`
- Requested stake: `€30.00`
- Response: bet placed successfully with `"balance": -10`
- `GET /api/balance` afterwards: `{"balance": -10, "currency": "EUR"}`

### Business Impact

Users can wager more money than they hold. This creates negative account balances, broken financial ledgers, settlement risk, and direct operator exposure. It is a core wallet-integrity failure.

### Evidence

Observed via direct API calls:

```json
{
  "message": "Bet placed successfully",
  "matchId": "la-liga-real-barca",
  "selection": "HOME",
  "stake": 30,
  "odds": 1.85,
  "payout": 55.5,
  "balance": -10,
  "currency": "USD"
}
```

---

## BUG-02 - Potential Payout Is Calculated Incorrectly

**Severity:** Critical

### Reproduction Steps

1. Open the application with a valid user ID.
2. Select an available match outcome with odds `3.25`.
3. Enter a stake of `€10.10`.
4. Review the potential payout in the bet slip.
5. Place the bet.
6. Review the potential payout displayed in the success receipt.

### Expected Result

The potential payout should be calculated as:

`€10.10 × 3.25 = €32.825`

The UI should display the correctly rounded currency value, for example `€32.83`, and the same value should appear in the bet slip, API response, and success receipt.

### Actual Result

The success receipt displays a potential payout of `€20.20`, which corresponds to a multiplier of `2.00` rather than the selected odds of `3.25`.

The receipt therefore contains internally inconsistent values:

- Stake: `€10.10`
- Odds: `3.25`
- Potential payout: `€20.20`


### Business Impact

Customers may receive an incorrect payout amount despite placing a bet at the displayed odds. This is a direct financial integrity issue and can result in customer loss, complaints, and regulatory exposure.

### Evidence

![Screenshot 2026-07-23 at 17.55.38.png](..%2F..%2FDownloads%2FScreenshot%202026-07-23%20at%2017.55.38.png)
![Screenshot 2026-07-23 at 17.56.07.png](..%2F..%2FDownloads%2FScreenshot%202026-07-23%20at%2017.56.07.png)


---

## BUG-03 - Balance Is Not Updated After Successful Bet Placement

**Severity:** Critical

### Reproduction Steps

1. Open the application with a valid user ID.
2. Record the current balance displayed in the header and bet slip.
3. Select a valid match outcome.
4. Enter a valid stake.
5. Place the bet successfully.
6. Close the success receipt.
7. Observe the balance displayed in the UI.
8. Refresh the page.

### Expected Result

After a successful bet:

- The stake should be deducted immediately.
- The header balance should update without a page refresh.
- The bet-slip balance should update at the same time.
- Both displayed balances should match the balance returned by `POST /api/place-bet`.

### Actual Result

The balance remains unchanged after the successful bet is placed.

The updated balance is displayed only after refreshing the page, which triggers a new `GET /api/balance` request.

### Business Impact

The customer sees stale account funds and may believe that the bet was not charged or that more funds are available than actually exist. This can cause incorrect subsequent betting decisions and inconsistent financial state across the application.

### Evidence

Observed in Chrome DevTools Network panel: the balance is refreshed only after a new `GET /api/balance` request caused by page reload.

---

## BUG-04 - API Returns USD Currency for an EUR Betting Account

**Severity:** High

### Reproduction Steps

1. Open the application with a valid user ID.
2. Select a valid match outcome.
3. Enter a valid stake.
4. Place the bet.
5. Inspect the response from `POST /api/place-bet`.

### Expected Result

The response should return:

```json
{
  "currency": "EUR"
}
```

The API currency should be consistent with the specification and the euro values displayed in the UI.

### Actual Result

The successful place-bet response returns:

```json
{
  "currency": "USD"
}
```

The UI continues to display the euro symbol.

### Business Impact

Currency inconsistency can cause incorrect transaction records, integration failures, reporting errors, and incorrect settlement or payment processing.

### Evidence

![Screenshot 2026-07-23 at 18.01.03.png](..%2F..%2FDownloads%2FScreenshot%202026-07-23%20at%2018.01.03.png)

Observed response:

```json
{
    "message": "Bet placed successfully",
    "matchId": "la-liga-real-barca",
    "selection": "HOME",
    "stake": 1,
    "odds": 1.85,
    "payout": 1.85,
    "balance": 99.4,
    "currency": "USD"
}

```

The response reports a balance of `99.40`, while the balance displayed in the UI before placement is `€110.40`.

For a `€1.00` stake, the expected resulting balance is `€109.40`, not `99.40`.

### Business Impact

The betting transaction returns an incorrect financial balance, creating a discrepancy of `€10.00`. This can lead to incorrect account state, duplicate or missing deductions, customer disputes, reconciliation failures, and regulatory risk.

### Evidence

![Screenshot 2026-07-23 at 18.02.08.png](..%2F..%2FDownloads%2FScreenshot%202026-07-23%20at%2018.02.08.png)

The screenshot shows:

- UI balance: `€110.40`
- Stake: `€1.00`
- API response balance: `99.4`
- API response currency: `USD`
---

## BUG-05 - Match Teams Are Reversed in the Success Receipt

**Severity:** High

### Reproduction Steps

1. Select an outcome for a match displayed as `Manchester Utd` vs `Chelsea`.
2. Enter a valid stake.
3. Place the bet successfully.
4. Review the match name in the success receipt.

### Expected Result

The success receipt should preserve the home-away ordering shown in the match list:

`Manchester Utd vs Chelsea`

### Actual Result

The success receipt may display the teams in reverse order, for example:

`Chelsea vs Manchester Utd`

### Business Impact

The receipt may represent the wrong event orientation, causing customer confusion and disputes over which team was selected as home or away.

### Evidence

Observed in the success receipt during execution.
![Screenshot 2026-07-23 at 18.04.25.png](..%2F..%2FDownloads%2FScreenshot%202026-07-23%20at%2018.04.25.png)

---

## BUG-06 - Past Matches Are Displayed and Available for Bet Selection

**Severity:** Critical

### Reproduction Steps

1. Open the application.
2. Review the displayed match list.
3. Identify matches labelled `PAST`.
4. Click an odds button for a past match.
5. Enter a valid stake.

### Expected Result

Only upcoming pre-match football events should be displayed.

Past matches should not be available for selection or bet placement.

### Actual Result

Matches labelled `PAST` are displayed in the main match list and their odds remain selectable.

### Business Impact

The system may allow customers to place bets on already completed or started events, creating a major integrity, settlement, and regulatory risk.

### Evidence

![Screenshot 2026-07-23 at 18.09.07.png](..%2F..%2FDownloads%2FScreenshot%202026-07-23%20at%2018.09.07.png)

---
## BUG-07 - Match Count Does Not Update After Filters Are Applied

**Severity:** Medium

### Reproduction Steps

1. Open the application and note the value displayed next to `Showing ... matches`.
2. Apply a date filter that returns only a small number of matches.
3. Observe the displayed match count.
4. Apply a restricted odds filter.
5. Observe the displayed match count again.

### Expected Result

The displayed match count should reflect the number of matches currently included in the filtered result set.

### Actual Result

The text continues to show `Showing 103 matches` regardless of the active date or odds filters and regardless of how many match cards are visible.

### Business Impact

The interface provides misleading result information and reduces customer confidence in the filtering functionality.

### Evidence

Observed across date and odds filtering scenarios.

![Screenshot 2026-07-23 at 18.11.58.png](..%2F..%2FDownloads%2FScreenshot%202026-07-23%20at%2018.11.58.png)

---

## BUG-08 - Date Filter Allows Selection of Past Dates

**Severity:** High

### Reproduction Steps

1. Open the date filter.
2. Switch to custom date selection.
3. Select a date or date range in the past.
4. Apply the filter.

### Expected Result

Because the feature supports upcoming pre-match events only, past dates should either:

- be disabled, or
- return no eligible matches with clear feedback.

Past events must not be presented as available betting opportunities.

### Actual Result

The date picker allows past dates to be selected and applied, and past matches are displayed.

### Business Impact

This exposes unsupported events and contributes to the risk of placing bets on ineligible matches.

### Evidence

Observed using the custom date picker and match list.

![Screenshot 2026-07-23 at 18.13.03.png](..%2F..%2FDownloads%2FScreenshot%202026-07-23%20at%2018.13.03.png)

---

## BUG-09 - Application Layout Is Not Responsive at Reduced Desktop Width

**Severity:** Medium

### Reproduction Steps

1. Open the application in Chrome.
2. Reduce the browser window width or open Chrome DevTools docked to the side.
3. Review the match list and bet-slip layout.

### Expected Result

The desktop layout should remain usable at common reduced desktop viewport widths.

Content should not be clipped or become inaccessible.

### Actual Result

The layout does not adapt correctly. Parts of the bet slip and page content move outside the visible viewport or become partially inaccessible.

### Business Impact

Users on smaller desktop screens, split-screen layouts, or docked browser environments may be unable to review or place bets reliably.

### Evidence

Observed while Chrome DevTools was docked to the right side.

![Screenshot 2026-07-23 at 18.13.33.png](..%2F..%2FDownloads%2FScreenshot%202026-07-23%20at%2018.13.33.png)


---

## BUG-10 - Balance Display Has No Details or Navigation Action

**Severity:** Low

### Reproduction Steps

1. Open the application.
2. Click the balance element in the header.

### Expected Result

If the balance element is designed as an interactive control, it should open balance details or transaction information. Otherwise, it should not appear interactive.

### Actual Result

The balance cannot be opened and provides no way to view account or transaction details.

### Business Impact

Customers cannot investigate their available funds or recent deductions, which is particularly problematic when the displayed balance is stale.

### Evidence

Observed during exploratory testing.

---

## BUG-11 - No Bet History or Open Bets View Is Available

**Severity:** Medium

### Reproduction Steps

1. Place a bet successfully.
2. Close the success receipt.
3. Attempt to locate the placed bet through the profile, balance, header, or main application interface.

### Expected Result

The application should provide a way to review the placed bet, or the feature specification should explicitly state that bet history is out of scope.

### Actual Result

There is no visible navigation or interface for reviewing previously placed bets after the receipt is closed.

### Business Impact

Customers cannot verify their betting activity after dismissing the receipt, which can increase support requests and disputes.

### Evidence

Observed during exploratory testing.

---

## BUG-12 - Error Modal “Rebet” Action Can Submit the Same Bet Again

**Severity:** High

### Reproduction Steps

1. Select a valid match outcome.
2. Enter a valid stake.
3. Disconnect the network or otherwise cause the request result to fail in the UI.
4. Click **Place Bet**.
5. Wait for the `Something went wrong` modal.
6. Restore connectivity.
7. Click **Rebet**.
8. Inspect network requests and balance changes.

### Expected Result

The application should safely determine whether the original request succeeded before retrying.

A retry must not create duplicate bets or deduct the stake more than once.

### Actual Result

The retry action sends another `POST /api/place-bet` request. When the original request was processed by the backend but the UI did not receive the result, using **Rebet** can create a second bet and deduct the balance again.

### Business Impact

Customers may unintentionally place duplicate bets and lose additional funds due to an ambiguous network failure.

### Evidence

Two `place-bet` requests were visible in the Chrome DevTools Network panel during error/retry testing.

![Screenshot 2026-07-23 at 18.13.33.png](..%2F..%2FDownloads%2FScreenshot%202026-07-23%20at%2018.13.33.png)
