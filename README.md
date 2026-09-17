# double-booked

[![Tests](https://github.com/LSaiko/double-booked/actions/workflows/tests.yml/badge.svg)](https://github.com/LSaiko/double-booked/actions/workflows/tests.yml)

Hybrid API + UI test automation for [automationintesting.online](https://automationintesting.online)
(restful-booker-platform), using Python, `requests`, Selenium and pytest.

```
double-booked/
├── api/booking_client.py        # requests wrapper: create/get/update/delete bookings
├── pages/
│   ├── base_page.py             # open / find / click / type helpers
│   ├── home_page.py             # room list, "Book now"
│   ├── booking_page.py          # reservation form → confirmation
│   └── admin_page.py            # admin login + Report calendar
├── tests/
│   ├── api/test_booking_api.py          # pure API: CRUD, invalid payloads
│   ├── ui/test_booking_ui.py            # pure Selenium: home → form → confirmation
│   └── integration/test_api_ui_sync.py  # API writes ↔ UI reads, and vice versa
├── conftest.py                  # `driver` (function) + `api_client` (session) fixtures
├── config.py                    # BASE_URL, admin creds, HEADLESS (env-overridable)
└── requirements.txt
```

## Run

```bash
pip install -r requirements.txt
pytest                      # everything
pytest -m api               # ~5s, no browser
pytest -m ui
pytest -m integration
HEADLESS=0 pytest -m ui     # watch the browser
```

Chrome must be installed; Selenium Manager fetches the driver automatically.

## Reports and screenshots

Every run writes a self-contained HTML report to `reports/report.html` (configured in `pytest.ini`).
When a UI or integration test fails, the `driver` fixture saves the browser state to
`screenshots/<test_name>.png` before quitting. Both folders are gitignored.

## CI

[`tests.yml`](.github/workflows/tests.yml) runs on every push and pull request, plus a daily cron
(the target is a public demo that resets itself, so a nightly run catches upstream changes):

1. **api** — `pytest -m api`, ~15s, no browser.
2. **ui** — `pytest -m "ui or integration"` on `ubuntu-latest` (Chrome preinstalled). Runs only if
   `api` passes; no point launching browsers against a dead backend.

Each job uploads its report as an artifact (`api-report`, `ui-report`); the UI one also includes
any failure screenshots. Find them on the run's summary page under *Artifacts*.

## Architecture

Three layers, each with a single job:

| Layer | Talks to | Used by |
|---|---|---|
| `api/BookingClient` | REST API over HTTP (`requests.Session`, logs in once, carries the auth cookie) | API tests, integration tests, **and UI tests for setup/teardown** |
| `pages/*` | The browser via Selenium (Page Object Model: locators + actions, no assertions) | UI tests, integration tests |
| `tests/*` | Both of the above | — |

`conftest.py` exposes both entry points as fixtures: `driver` is function-scoped (fresh browser per test,
no state bleed), `api_client` is session-scoped (one login, reused everywhere, cheap). The `booking`
fixture creates a booking via the API and deletes it after the test, so UI/integration tests never
have to click their way into a precondition.

## Why test at both layers

API and UI tests fail for different reasons, so each catches bugs the other cannot see:

- **API tests** hit the contract directly: status codes, validation rules (`Firstname should not be
  blank`, phone length), 404 on unknown ids, 202 on delete. They are fast and deterministic, so they
  can run on every commit and pin down *server-side* regressions precisely — a broken validator, a
  wrong status code, a field dropped from the response. A UI test would only see "something went
  wrong" and be slow about it.
- **UI tests** catch what the API can't: the form posts the wrong field, the date picker sends
  off-by-one dates, the confirmation renders the wrong text, a button is unclickable behind the
  navbar. The backend can be perfect and users still can't book a room.
- **Integration tests** check that the two layers agree. A booking created through the API must show
  up in the admin Report calendar with the right name and room; a booking made in the browser must be
  readable through the API with the exact dates chosen; a deletion through the API must remove it from
  the UI. These catch *serialisation and mapping* bugs between front and back end — the class of defect
  where both halves pass their own tests and the product is still broken.

Using the API for setup/teardown inside UI tests is the practical payoff of the hybrid: tests stay
independent, run faster, and clean up after themselves on a shared demo site.

## Contributing

1. Fork, branch from `main`, and run `pytest` before opening a PR — CI runs the same command.
2. Keep the layers honest: locators and browser actions live in `pages/`, HTTP calls in
   `api/booking_client.py`, assertions only in `tests/`.
3. New tests get the matching marker (`api`, `ui`, `integration`) so they land in the right CI job.
4. Any booking a test creates must be deleted by the same test or its fixture — the site is shared.
5. Found a site quirk? Add it to the section below with the workaround.

This project follows the [Contributor Covenant](CODE_OF_CONDUCT.md).

## Notes on the target site

- `PUT /booking/{id}` returns 409 if the dates are unchanged (it conflicts with itself), so the
  update test always moves the dates.
- The site is a shared public demo; tests pick random future dates to avoid clashing with other
  people's bookings.
