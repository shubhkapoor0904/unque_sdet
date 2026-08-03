# Test Plan — Swag Labs (SauceDemo) E-Commerce Platform

**Author:** Shubh
**Application Under Test:** https://www.saucedemo.com
**Date:** August 2026

---

## 1. Objective

Validate the core functionality, UI consistency, and error handling of the Swag Labs demo storefront across authentication, product browsing, cart, and checkout, with emphasis on uncovering the intentional defects seeded into the `problem_user` and `performance_glitch_user` accounts.

## 2. Scope

**In scope:**
- Login / authentication for all four provided user roles
- Product catalog: listing, images, descriptions, prices, sorting
- Cart: add/remove items, badge count, persistence across navigation
- Checkout: information form, order summary, tax/total calculation, order completion
- Logout and session handling

**Out of scope:**
- Backend/API testing (no exposed API)
- Payment gateway integration (checkout is simulated, no real payment)
- Load/performance testing beyond observing `performance_glitch_user` behavior
- Accessibility (WCAG) audit (noted as a future improvement, not covered here)

## 3. Types of Testing

| Type | Application |
|---|---|
| **Functional** | Login, add/remove cart items, checkout flow, sorting, logout |
| **UI / Visual** | Product images, layout consistency, button states, price formatting |
| **Negative testing** | Invalid credentials, locked-out user, empty checkout fields, non-numeric input in name/zip fields |
| **Edge cases** | Empty cart checkout, adding same item twice, removing item mid-checkout, browser back/forward navigation after logout, cart persistence across sessions |
| **Cross-browser** | Chrome, Firefox, Edge (desktop). Basic responsive check on a mobile viewport (375×812) |
| **Regression-oriented** | Re-running the same suite against all four user roles to compare behavior |

## 4. Test Environment

| Item | Detail |
|---|---|
| Browsers | Chrome (latest stable), Firefox (latest stable), Edge (latest stable) |
| OS | Windows 11 / Ubuntu 22.04 |
| Resolution | 1920×1080 (desktop), 375×812 (mobile emulation via DevTools) |
| Automation tooling | Selenium WebDriver 4.x, Python 3.11, PyTest, webdriver-manager |
| Network | Standard broadband, no throttling (except for a dedicated slow-3G run against `performance_glitch_user`) |

## 5. Test Data

| Username | Password | Expected Behavior |
|---|---|---|
| `standard_user` | `secret_sauce` | Normal, bug-free functionality — baseline for comparison |
| `locked_out_user` | `secret_sauce` | Login blocked with an explicit error message |
| `problem_user` | `secret_sauce` | Intentionally broken UI/functionality (images, forms, sorting, buttons) |
| `performance_glitch_user` | `secret_sauce` | Functionally correct but with an abnormal login delay |

Additional negative-path data: blank username/password, valid username with wrong password, SQL-injection-style strings (`' OR 1=1--`) in the login form to confirm no unexpected behavior.

## 6. Test Cases

> Full traceable set lives in `test_plan.md` (below) and is automated in `tests/`. Minimum 5 shown here; the automation suite covers a superset.

| ID | Title | Preconditions | Steps | Expected Result | Priority |
|---|---|---|---|---|---|
| TC-01 | Valid login — standard_user | On login page | 1. Enter `standard_user` / `secret_sauce` 2. Click Login | Redirected to `/inventory.html`; 6 products visible with correct images and prices | High |
| TC-02 | Locked-out user is blocked | On login page | 1. Enter `locked_out_user` / `secret_sauce` 2. Click Login | Stays on login page; error banner reads "Epic sadface: Sorry, this user has been locked out." | High |
| TC-03 | Add item to cart and complete checkout | Logged in as standard_user | 1. Add "Sauce Labs Backpack" to cart 2. Open cart 3. Click Checkout 4. Fill first/last name + zip 5. Continue 6. Finish | Cart badge shows "1"; order summary shows correct item, tax, and total; "Thank you for your order" confirmation page appears | High |
| TC-04 | Cart badge updates correctly on add/remove | Logged in as standard_user | 1. Add 2 items 2. Remove 1 from cart page | Badge decrements from 2 → 1 immediately, no stale count | Medium |
| TC-05 | Checkout blocked on missing required field | Logged in as standard_user, item in cart | 1. Go to checkout 2. Leave Last Name blank 3. Click Continue | Error: "Error: Last Name is required"; user remains on the form with First Name value retained | Medium |
| TC-06 | Sort products Z→A | Logged in as standard_user | 1. Select "Name (Z to A)" from sort dropdown | Product list re-orders alphabetically descending immediately | Medium |
| TC-07 | problem_user product images | Logged in as problem_user | 1. View inventory page | *(Bug candidate)* — verify whether product images render distinctly or are duplicated | High (bug-hunting) |
| TC-08 | performance_glitch_user login timing | On login page | 1. Enter `performance_glitch_user` / `secret_sauce` 2. Click Login 3. Measure time to `/inventory.html` render | Login should complete in a reasonable time (baseline: standard_user's login is near-instant); flag if delay exceeds ~5s | Medium |
| TC-09 | Session/back-button behavior after logout | Logged in as standard_user | 1. Log in 2. Log out via menu 3. Press browser Back button | User should be redirected to login page, not shown a cached authenticated view | High |
| TC-10 | Cart persists across page navigation | Logged in as standard_user | 1. Add item to cart 2. Navigate to product detail page and back to inventory | Cart badge count is retained | Low |

## 7. Risk Assessment

| Area | Risk Level | Rationale |
|---|---|---|
| `problem_user` catalog rendering | **High** | Site is documented to seed broken images/UI here; highest bug density |
| Checkout form validation (`problem_user`) | **High** | Text-input fields are known to misbehave for this role; directly affects revenue-critical flow |
| Cart badge state management | **Medium** | Client-side state bugs are common and easy to miss without explicit add/remove sequences |
| Sorting functionality | **Medium** | Visually subtle — a wrong sort order is easy to overlook without checking exact product order |
| Login timing (`performance_glitch_user`) | **Medium** | No hard failure, but poor UX / potential automation timeout risk if waits aren't tuned |
| Cross-browser rendering | **Low** | Site is a simple static SPA-like demo; unlikely to diverge much across major browsers |
| Session handling on logout | **Medium** | Improper back-button handling is a real-world security/UX issue pattern worth checking |

## 8. Entry / Exit Criteria

**Entry:** Site is reachable, all 4 test accounts are valid, test environment (browsers + Selenium stack) is provisioned.

**Exit:** All planned test cases executed across at least 2 browsers; all found defects logged with severity and reproduction steps; automated smoke suite (login, checkout, locked-out) passes for `standard_user` baseline.

## 9. Deliverables Summary

1. This test plan
2. `bug_report.md` — 5+ documented defects with severity/repro steps
3. Selenium/PyTest automation suite (`pages/`, `tests/`)
4. Loom walkthrough videos (test plan + automation, and manual bug discovery)
