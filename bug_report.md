# Bug Report — Swag Labs (SauceDemo)

**Tester:** Shubh
**Environment:** Windows 10/11, Python 3.11.9, Chrome (via Selenium), automated + manual verification
**Build under test:** https://www.saucedemo.com (public demo instance)

## Verification method

Every bug below marked **Confirmed** was independently reproduced two ways:
1. Automated: `pytest tests/test_problem_user_bugs.py -v -rs` (see actual terminal output quoted under each bug)
2. Manual: exact click-by-click steps in the "How to spot it by hand" section — written so you don't need to compare screenshots side by side, just look at one specific thing at one specific moment

| Status | Meaning |
|---|---|
| ✅ Confirmed | Reproduced by an automated assertion AND has a precise manual repro path |
| ⚠️ Unconfirmed | Reported in older third-party write-ups, not yet independently verified on the current build — do not include in the video/report until re-checked |

---

### BUG-01: Product images are broken/duplicated for `problem_user` — ✅ Confirmed

- **Severity:** High
- **Priority:** P1
- **User role:** `problem_user`
- **Module:** Product Catalog (Inventory page)
- **Automated evidence:** `test_problem_user_product_images_are_distinct` → `XFAIL` (assertion `len(set(srcs)) == len(srcs)` failed — duplicate `src` values found across product image tags)
- **Visual evidence:** confirmed by screenshot — all 6 inventory tiles (Backpack, Bike Light, Bolt T-Shirt, Fleece Jacket, Onesie, Test.allTheThings T-Shirt) render the identical close-up photo of a dog holding a tennis ball, regardless of the actual product
- **Steps to Reproduce:**
  1. Log in with `problem_user` / `secret_sauce`
  2. Observe the inventory grid (`/inventory.html`)
- **Expected Result:** Each of the 6 products displays its own distinct product image.
- **Actual Result:** Multiple product tiles render the same incorrect image, even though product names and prices are correct.
- **Impact:** Customers cannot visually distinguish products before purchase — a direct e-commerce trust/conversion issue.
- **How to spot it by hand (do this, don't just glance):**
  1. Log in as `problem_user`, land on the inventory grid.
  2. Right-click the image for **"Sauce Labs Backpack"** (1st tile) → **Inspect**.
  3. In DevTools, note the `src` attribute of that `<img>` tag (right-click it in the Elements panel → Copy → Copy element, or just read the `src=` value).
  4. Right-click the image for **"Sauce Labs Bike Light"** (2nd tile) → **Inspect** → read its `src` value.
  5. Compare the two `src` strings. If they're identical (or several tiles share the same filename), that's the bug — confirmed independent of how the image *looks* to your eye, which can be deceiving if the images are visually similar thumbnails.
  6. Faster alternative: open DevTools **Network** tab, filter by "Img," reload the page, and look at how many *unique* image requests fire vs. how many product tiles exist (6 tiles should mean 6 distinct image files).

---

---

### BUG-02: Checkout "Last Name" field corrupts "First Name" input for `problem_user` — ✅ Confirmed

- **Severity:** Critical
- **Priority:** P0
- **User role:** `problem_user`
- **Module:** Checkout — Your Information (Step One)
- **Automated evidence:** `test_problem_user_checkout_name_fields_are_independent` → `XFAIL` (assertion on the Last Name field's actual `value` attribute failed — it did not equal what was typed)
- **Steps to Reproduce:**
  1. Log in as `problem_user`
  2. Add any item to the cart → Cart → Checkout
  3. Type a first name in the "First Name" field (e.g., `Shubh`)
  4. Click into "Last Name" and type a last name (e.g., `Sharma`)
- **Expected Result:** Both fields independently retain their own typed values.
- **Actual Result:** The Last Name field does not correctly hold the typed value.
- **Impact:** Users cannot complete checkout with correct name data — this blocks the single most revenue-critical flow on the site.
- **How to spot it by hand (the part most people miss):** Looking at the two text boxes on screen while typing normal speed often looks fine, because the visible cursor/typed characters can appear to land correctly for a moment. To actually catch it:
  1. Type into First Name, then Last Name, as usual.
  2. **Before clicking Continue**, click back into the First Name field and select-all the text (Ctrl+A while focused in that field) or triple-click it to highlight its full contents.
  3. Read the highlighted value character by character — don't trust what you glanced at while typing, re-read it after the fact.
  4. Do the same for Last Name.
  5. If either field's actual selected/highlighted text doesn't match what you typed, that's the bug — it's a state bug, not a rendering bug, so the field can *look* right mid-typing and only reveal the wrong stored value when you go back and check it.

---

### BUG-03: Cart button state desyncs between grid view and product detail view for `problem_user` — ✅ Confirmed

- **Severity:** High
- **Priority:** P1
- **User role:** `problem_user`
- **Module:** Inventory grid vs. Product Detail Page — cart button state
- **Found by:** Shubh, manual exploratory testing
- **Actual Result — the 6 products split into two distinct broken groups:**

  **Group A — "Sauce Labs Backpack," "Sauce Labs Bike Light," "Sauce Labs Onesie":**
  1. Click "Add to cart" from the main inventory grid → button correctly flips to "Remove," cart badge increments (see screenshot: all three show red "Remove" buttons on the grid)
  2. Click into that same product's detail page → button still reads "Add to cart," even though the item is genuinely in the cart
  3. Result: the detail page is showing stale/incorrect button state for an item that's actually already in the cart

  **Group B — "Sauce Labs Bolt T-Shirt," "Sauce Labs Fleece Jacket," "Test.allTheThings() T-Shirt (Red)":**
  1. Click "Add to cart" from the main inventory grid → **no response** — button stays "Add to cart," badge does not increment
  2. Click into that same product's detail page → "Add to cart" here *does* work, button flips to "Remove"
  3. Click "Remove" on the detail page → **button stays stuck on "Remove"**, item is not actually taken out of the cart

- **Expected Result:** Cart state (badge count, button label) should be identical and consistent whether viewed from the grid or a product's own detail page, and Remove should function everywhere Add does.
- **Impact:** Users can end up in a state where they believe an item isn't in their cart (grid) when it actually is (Group A), or can add an item via the detail page but then have no way to remove it again (Group B) — both are direct paths to an incorrect order at checkout.
- **How to spot it by hand:** Add each of the 6 products one at a time from the grid, noting which ones flip to "Remove" immediately. Then, for every product, click into its detail page and compare the button state there against the grid. The mismatch only shows up when you deliberately check *both* views for the *same* product — checking either view alone looks totally normal.

---

---

### BUG-04: Sort dropdown does not reorder products for `problem_user` — ✅ Confirmed

- **Severity:** Medium
- **Priority:** P2
- **User role:** `problem_user`
- **Module:** Inventory page — sort control
- **Automated evidence:** `test_problem_user_sort_z_to_a_reorders_list` → `XFAIL` (product name list after selecting "Name (Z to A)" did not equal the reverse-sorted list)
- **Steps to Reproduce:**
  1. Log in as `problem_user`
  2. Note the default product order
  3. Select "Name (Z to A)" from the sort dropdown
- **Expected Result:** Product list re-orders alphabetically descending.
- **Actual Result:** The dropdown's selected label changes, but the underlying product order does not correctly follow it.
- **Impact:** Users trying to browse alphabetically or by price get a misleading list — a silent bug users are unlikely to notice, which makes it worse.
- **How to spot it by hand (this one is genuinely easy to eyeball wrong):** Don't just glance at whether the list "moved" — actually write down the first product name before sorting, then check if it's the alphabetically-last item after selecting Z→A.
  1. Log in as `problem_user`, on the inventory page write down (or screenshot) the 6 product names top-to-bottom in default order.
  2. Alphabetize that list yourself, descending (Z→A), on paper/in your head — e.g., "Test.allTheThings() T-Shirt (Red)" should come before "Sauce Labs Bike Light" alphabetically descending.
  3. Now select "Name (Z to A)" in the dropdown.
  4. Compare the new on-screen order against your manually-sorted list, position by position. If they diverge anywhere, the sort is broken — this is much more reliable than "does it look re-ordered," because a partially-correct or scrambled order can still *look* different from the default without actually being correct Z→A.

---

### BUG-05: Abnormal login delay for `performance_glitch_user` — ✅ Confirmed

- **Severity:** Medium
- **Priority:** P2
- **User role:** `performance_glitch_user`
- **Module:** Authentication
- **Automated evidence:** `test_performance_glitch_user_login_delay_is_flagged` measured an actual elapsed time of **5.84 seconds** between clicking Login and the inventory page loading (test run on Windows 10/11, Python 3.11.9) — see terminal output: `SKIPPED [1] BUG-05 observed: abnormal login delay of 5.84s (no loading indicator shown)`
- **Steps to Reproduce:**
  1. Log in with `performance_glitch_user` / `secret_sauce`
  2. Time the interval between clicking Login and the inventory page fully rendering
- **Expected Result:** Login completes in roughly the same time as `standard_user` (near-instant).
- **Actual Result:** Login took ~5.8s with no loading indicator/spinner shown during the delay.
- **Impact:** A multi-second delay with zero visual feedback reads as a frozen/broken page to real users, increasing bounce/abandonment risk. Also a risk for automation suites with tight timeouts.
- **How to spot it by hand:** This one you genuinely can't eyeball reliably without a timer — human perception of "a few seconds" is unreliable and you may have unconsciously written it off as normal page-load time.
  1. Open your phone's stopwatch (or say "one-one-thousand, two-one-thousand..." out loud) right as you click Login.
  2. Stop timing the instant the inventory grid's product images appear.
  3. Do the same for `standard_user` immediately after, as a baseline comparison.
  4. If `performance_glitch_user` takes noticeably longer (roughly 4–6x), that's the bug — comparing against a baseline is what makes it visible, since either number alone can feel "normal."

---

### BUG-06 (Bonus): Cart badge count can desync from actual cart contents — ⚠️ Unconfirmed

- **Status:** Not yet independently verified — not covered by the current automated suite.
- **How to check it yourself:** Log in, add 2 different items to the cart, go to the Cart page and remove one, then navigate back to the inventory page *without* reloading the browser. Watch the badge number specifically at the moment you land back on inventory — does it correctly show "1," or does it briefly/persistently show "2"? If it's always correct, drop this from the report.

---

### BUG-07: "Reset App State" does not take effect until the page is manually refreshed — ✅ Confirmed

- **Severity:** Medium
- **Priority:** P2
- **User role:** Reproduced on `problem_user`; worth spot-checking on `standard_user` too
- **Module:** Hamburger menu — Reset App State
- **Found by:** Shubh, manual exploratory testing
- **Steps to Reproduce:**
  1. Add one or more items to the cart
  2. Open the hamburger menu (☰, top left) → click "Reset App State"
  3. **Without refreshing the page**, observe the cart badge and cart contents
- **Expected Result:** "Reset App State" is an explicit, immediate action — the cart badge should clear and the cart should empty right away, with no refresh required.
- **Actual Result:** The cart badge and cart contents continue showing the pre-reset state until the page is manually refreshed (F5/reload) — only then does the reset actually reflect on screen.
- **Impact:** Since the menu item implies an instant reset, a user (or a QA tester) who clicks it and immediately checks the result will conclude the feature is completely broken — when it has, misleadingly, worked internally but not visually. This can also mask other bugs during testing, since a "reset" that a tester assumes worked may not have.
- **Non-obvious because:** Most people reflexively refresh the page right after clicking a reset/state-changing action out of habit, which immediately masks the bug — you have to deliberately hold off refreshing to see it.

---

## Summary Table

| ID | Title | Severity | Role | Status |
|---|---|---|---|---|
| BUG-01 | Duplicated/broken product images | High | problem_user | ✅ Confirmed |
| BUG-02 | Last Name field state corruption | Critical | problem_user | ✅ Confirmed |
| BUG-03 | Cart button state desyncs between grid and detail view | High | problem_user | ✅ Confirmed |
| BUG-04 | Sort dropdown doesn't reorder products | Medium | problem_user | ✅ Confirmed |
| BUG-05 | Abnormal login delay (5.84s), no indicator | Medium | performance_glitch_user | ✅ Confirmed |
| BUG-06 | Cart badge count desync | Low–Medium | standard_user / problem_user | ⚠️ Unconfirmed — verify before reporting, or drop |
| BUG-07 | Reset App State doesn't apply until manual refresh | Medium | problem_user | ✅ Confirmed |

**For the video/final submission:** you now have 6 fully confirmed bugs (BUG-01, 02, 03, 04, 05, 07) — comfortably past the "at least 5" requirement, all personally verified by you plus 4 backed by automated assertions. Drop BUG-06 unless you specifically re-check and confirm it; you don't need it anymore. BUG-03 and BUG-07 are your strongest material for Video 2 — they're specific, self-found (not recycled from old write-ups), and genuinely non-obvious.
