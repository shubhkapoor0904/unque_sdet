# SauceDemo QA & Automation — Shubh

Test plan, bug reports, and Selenium/PyTest automation for https://www.saucedemo.com, built for the SDET/QA interview assignment.

## Repo structure

```
saucedemo-qa/
├── test_plan.md              # Full test plan (scope, test data, test cases, risk assessment)
├── bug_report.md             # 6 documented defects with severity + repro steps
├── requirements.txt
├── pytest.ini
├── pages/                    # Page Object Model
│   ├── base_page.py
│   ├── login_page.py
│   ├── inventory_page.py
│   ├── cart_page.py
│   └── checkout_page.py
└── tests/
    ├── conftest.py            # WebDriver fixture (Chrome, headless by default)
    ├── test_login.py          # Critical flow: valid login + locked-out user + negative cases
    ├── test_e2e_checkout.py   # Critical flow: add to cart -> checkout -> order confirmation
    └── test_problem_user_bugs.py  # Automated regression checks for logged bugs (problem_user, performance_glitch_user)
```

## Why this structure (Page Object Model)

Each page of the app (`login`, `inventory`, `cart`, `checkout`) has its own class holding **locators** and **actions**. Tests only call high-level actions (`login_page.login(...)`, `cart_page.start_checkout()`), never touch raw selectors. This means:
- If SauceDemo changes an element ID, only one file (`pages/*.py`) needs updating, not every test.
- Selectors use stable attributes (`id`, `data-test`, `class`) that SauceDemo exposes specifically for automation, not brittle XPath/text matches.
- Tests read like plain-English steps, making them easy to review and extend.

## Setup

Requires Python 3.9+ and Google Chrome installed locally.

```bash
git clone <this-repo-url>
cd saucedemo-qa
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

`webdriver-manager` automatically downloads the correct ChromeDriver for your installed Chrome version — no manual driver setup needed.

## Running the tests

Run everything:
```bash
pytest
```

Run a single critical-flow file:
```bash
pytest tests/test_login.py
pytest tests/test_e2e_checkout.py
pytest tests/test_problem_user_bugs.py
```

Generate an HTML report (useful for the video walkthrough):
```bash
pytest --html=report.html --self-contained-html
```

Watch the browser instead of running headless: open `tests/conftest.py` and comment out the `--headless=new` line, then re-run.

## What's covered

| File | Critical flow |
|---|---|
| `test_login.py` | Login with valid credentials (`standard_user`); login with `locked_out_user` produces the correct error message; 3 additional negative-path parametrized cases (blank fields, bad password) |
| `test_e2e_checkout.py` | Full add-to-cart → checkout → order-confirmation happy path, plus a validation check that checkout is correctly blocked when a required field is missing |
| `test_problem_user_bugs.py` | Automated, repeatable checks for the 3 most testable bugs from `bug_report.md` (broken images, corrupted checkout fields, broken sort) using `@pytest.mark.xfail` so the suite documents *known* failures rather than reporting false red builds; also times `performance_glitch_user`'s login and flags it if abnormally slow |

## Notes for reviewers

- Tests run headless by default for CI-friendliness; toggle to headed mode as described above to visually confirm behavior for the video demo.
- `test_problem_user_bugs.py` intentionally targets the intentional bugs seeded into `problem_user` — these are marked `xfail` (expected failure) so a CI run stays green while still proving, on every run, that the automation *can detect* the defects. Removing the `xfail` marker turns these into live regression alarms once/if the bugs are ever fixed.
- Selectors avoid the site's dynamic/duplicated CSS class suffixes and instead rely on `id` and `data-test` attributes, which SauceDemo maintains specifically to keep automation stable across UI-only changes.
