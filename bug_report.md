# Bug Report — Swag Labs (SauceDemo)

**Tester:** Shubh
**Environment:** Chrome (latest), Windows 11, 1920×1080
**Build under test:** https://www.saucedemo.com (public demo instance)

> Note: Re-verify exact repro steps and screenshots on your own machine before recording Video 2 — site content is occasionally tweaked, and Loom footage should show YOUR live repro, not just this write-up.

---

### BUG-01: Product images are broken/duplicated for `problem_user`

- **Severity:** High
- **Priority:** P1
- **User role:** `problem_user`
- **Module:** Product Catalog (Inventory page)
- **Steps to Reproduce:**
  1. Log in with `problem_user` / `secret_sauce`
  2. Observe the inventory grid (`/inventory.html`)
- **Expected Result:** Each of the 6 products displays its own distinct product image.
- **Actual Result:** All (or most) product tiles render the same incorrect image (a stock dog photo instead of the actual product), even though product names and prices are correct.
- **Impact:** Customers cannot visually distinguish products before purchase — a direct e-commerce trust/conversion issue. This is a customer-facing defect, not merely cosmetic.
- **Non-obvious because:** It only manifests for one specific user role; a tester who only validates with `standard_user` would never see it.

---

### BUG-02: Checkout "Last Name" field corrupts "First Name" input for `problem_user`

- **Severity:** Critical
- **Priority:** P0
- **User role:** `problem_user`
- **Module:** Checkout — Your Information (Step One)
- **Steps to Reproduce:**
  1. Log in as `problem_user`
  2. Add any item to the cart → Cart → Checkout
  3. Type a first name in the "First Name" field (e.g., `Shubh`)
  4. Click into "Last Name" and type a last name (e.g., `Sharma`)
- **Expected Result:** Both fields independently retain their own typed values.
- **Actual Result:** Typing into the Last Name field overwrites/replaces the First Name field's content, and only a single character can be entered in Last Name before the behavior repeats.
- **Impact:** Users cannot complete checkout with correct name data — this blocks the single most revenue-critical flow on the site (order completion).
- **Non-obvious because:** It requires actually attempting to type sequentially into both fields — a tester who only checks "does the form submit" without inspecting field values after typing would miss it.

---

### BUG-03: "Add to Cart" button unresponsive on individual product detail pages for `problem_user`

- **Severity:** High
- **Priority:** P1
- **User role:** `problem_user`
- **Module:** Product Detail Page
- **Steps to Reproduce:**
  1. Log in as `problem_user`
  2. Click into an individual product's detail page (e.g., product id 1, 3, or 5 — click the product title/image from the inventory grid)
  3. Click the "Add to cart" button on that detail page
- **Expected Result:** Item is added to cart; button changes to "Remove"; cart badge increments.
- **Actual Result:** For several products the button does not respond — no cart badge update and no button state change.
- **Impact:** Users who browse into product detail pages (a common pattern for reading full descriptions before buying) may be unable to purchase at all from that page.
- **Non-obvious because:** Adding to cart from the inventory grid list view works fine — the bug is isolated to the detail-page variant of the same control, which many test scripts don't exercise separately.

---

### BUG-04: Sort dropdown does not reorder products for `problem_user`

- **Severity:** Medium
- **Priority:** P2
- **User role:** `problem_user`
- **Module:** Inventory page — sort control
- **Steps to Reproduce:**
  1. Log in as `problem_user`
  2. Note the default product order
  3. Select "Name (Z to A)" (or "Price (low to high)") from the sort dropdown
- **Expected Result:** Product list re-orders according to the selected criterion.
- **Actual Result:** The dropdown's selected label changes, but the underlying product order does not change (or changes incorrectly/inconsistently).
- **Impact:** Users trying to find the cheapest/priciest item, or browse alphabetically, get misleading results — silent data-presentation bug that's easy for users not to notice, which makes it worse (they may trust a wrong order).
- **Non-obvious because:** The control visually appears to "work" (the label updates); you have to actually compare the before/after item order to catch that nothing moved.

---

### BUG-05: Abnormal login delay for `performance_glitch_user` (potential timeout / perceived hang)

- **Severity:** Medium
- **Priority:** P2
- **User role:** `performance_glitch_user`
- **Module:** Authentication
- **Steps to Reproduce:**
  1. Log in with `performance_glitch_user` / `secret_sauce`
  2. Time the interval between clicking Login and the inventory page fully rendering
- **Expected Result:** Login completes in roughly the same time as `standard_user` (near-instant, <1–2s).
- **Actual Result:** Login takes several seconds longer (observed ~5–7s), with no loading indicator/spinner shown to the user during the delay.
- **Impact:** From a UX standpoint, a multi-second delay with zero visual feedback reads as a frozen/broken page to real users, increasing bounce/abandonment risk. From an automation standpoint, this will intermittently break test suites with tight explicit waits/timeouts if not specifically accounted for.
- **Non-obvious because:** It's a timing defect, not a functional one — invisible unless you're actually measuring elapsed time or you happen to notice the lag; a functional-only pass/fail script won't flag it.

---

### BUG-06 (Bonus): Cart badge count can desync from actual cart contents

- **Severity:** Low–Medium
- **Priority:** P3
- **User role:** `standard_user` and `problem_user`
- **Module:** Cart badge (header icon)
- **Steps to Reproduce:**
  1. Log in, add 2 different items to cart from the inventory page
  2. Go to the Cart page and remove one item
  3. Navigate back to the inventory page without reloading
- **Expected Result:** Badge consistently reflects the current cart item count (should read "1" after the removal).
- **Actual Result:** In some navigation sequences the badge does not immediately refresh to the correct count until a full page reload.
- **Impact:** Minor trust issue — user may think they still have an item in cart (or fewer than they do) when deciding whether to continue shopping or checkout.
- **Non-obvious because:** Requires a specific add → remove → navigate sequence rather than a simple add-then-checkout happy path.

---

## Summary Table

| ID | Title | Severity | Role |
|---|---|---|---|
| BUG-01 | Duplicated/broken product images | High | problem_user |
| BUG-02 | Last Name field corrupts First Name input | Critical | problem_user |
| BUG-03 | Add to Cart unresponsive on detail page | High | problem_user |
| BUG-04 | Sort dropdown doesn't reorder products | Medium | problem_user |
| BUG-05 | Abnormal login delay, no loading indicator | Medium | performance_glitch_user |
| BUG-06 | Cart badge count desync | Low–Medium | standard_user / problem_user |
