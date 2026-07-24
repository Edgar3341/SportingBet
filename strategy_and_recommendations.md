# Strategy and Recommendations

## Why these 2 automated tests

Automation effort was focused on the highest financial and product risk, not on coverage volume.

### 1. E2E UI — successfully place a single pre-match bet (TC-01)

This is the core revenue journey: select outcome → enter stake → confirm payout → place bet → receipt → balance deduction.

It protects the path customers and the business depend on every day. Failures here mean wrong tickets, wrong balances, or lost trust. The test also cross-checks the UI against the API balance, so UI and backend stay aligned on money movement.

### 2. API — reject stake below the €1.00 minimum

Stake limits are hard financial controls. Validating the minimum directly via `POST /api/place-bet` is fast, stable, and independent of UI flakiness. It catches backend rule regressions early and confirms that rejected stakes do not change the balance.

These two tests give one critical end-to-end signal and one precise business-rule signal — the best return for a small automation set.

---

## What stayed manual (and why)

The following stayed manual because they are either exploratory, unstable to automate early, or better judged by a human once:

| Area | Why manual for now |
| --- | --- |
| Full stake boundary matrix (max €100, UI messages, €1.00 vs €1.01 conflict) | Spec is inconsistent; needs product clarification before locking assertions |
| Selection replacement / single-bet only behaviour | Important, but secondary to first successful placement; more UI state combinations |
| Stake format / precision edge cases | High assertion noise; better as targeted API/UI cases after core path is green |
| Insufficient balance in UI | Critical defect already found via API (negative balance). Manual/exploratory follow-up until the wallet rule is fixed |
| Filters (date/odds), past matches, match count | Important catalogue integrity issues, but outside the core place-bet revenue path for this automation slice |
| Layout / responsiveness, Rebet retry races | Visual and timing-sensitive; expensive and flaky as first automation targets |
| Receipt payout / team-order / currency bugs | Already documented with evidence; better tracked as defect verification after fixes than as broad suite noise |

Manual exploratory testing remains valuable for UX judgment, timing races, and newly discovered edge cases around known defects.

---

## Recommendations if this project scales

### 1. CI/CD pipeline (Docker + headless + quality gates)

Run automation on every PR and on a schedule:

- **Containerise** the suite (Python + Chrome/Chromium + Chromedriver) so local and CI use the same image.
- Run UI tests in **headless Chrome** (`--headless=new`) in CI; keep headed mode for local debugging only.
- Pipeline stages example:
  1. Install dependencies
  2. Static checks: `ruff`/`flake8`, formatting, optional **typecheck** (`mypy` / `pyright`)
  3. Smoke: API auth + balance
  4. pytest (API + E2E headless)
  5. Publish Allure report
- Fail the build on lint/type errors and on test failures — catch broken imports, bad types, and regressions before merge.

**Cron / scheduled jobs**

- Nightly full regression against the QA environment.
- Optional daytime smoke (e.g. every 1–2 hours) for place-bet + min-stake API only.
- Use a dedicated CI `user-id` so scheduled runs do not collide with explorers.

### 2. Secrets, reports, and notifications

- Store `BASE_URL`, `user_id`, and any future credentials in **[Infisical](https://infisical.com/)** (or equivalent), not in git. Inject them into CI/Docker at runtime. Infisical fits well for env sync across local, CI, and staging.
- Generate **Allure** on every run; publish HTML as a CI artifact.
- Keep report history for about **30 days** (artifact retention or an Allure server / static hosting bucket with lifecycle policy).
- On failure (and optionally on nightly summary), send a short alert to **Slack** (or Teams/email): job link, failed tests, Allure URL, environment.

### 3. Test layers, data strategy, and spec clarity

- Grow by layers, not only more UI tests:
  - **API contract / business rules** first (stake min/max, insufficient balance, currency, payout math)
  - **Critical E2E** journeys second
  - UI edge cases and filters later
- **Data strategy:** reset balance before money tests; isolate users per pipeline; prefer stable match IDs or seed data; avoid depending on “first card in the list”.
- **Spec clarifications** before expanding automation:
  - Minimum stake €1.00 vs €1.01
  - Expected API error for insufficient balance (today the API accepts overspend and can go negative — must be fixed and then locked by an automated API test)
  - Currency must be EUR end-to-end
  - Receipt must use `stake × odds` and correct home/away order

---

## Suggested near-term automation backlog (after fixes)

1. API: reject stake greater than available balance (currently broken — critical).
2. API: max stake `€100.01` → `422`.
3. E2E or API: payout = `stake × odds` on place-bet response / receipt after BUG-02 is fixed.
4. API: `currency` is always `EUR` after BUG-04 is fixed.

These give the strongest next risk reduction once the known wallet and receipt defects are addressed.
