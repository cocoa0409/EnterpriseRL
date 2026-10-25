# Policy-task audit — d1_credit_account_billing_and_credits / charter-global

## revision_1

## charter_global_frozen

- Auditor: independent policy-task auditor (erl-task-policy-audit), not the instantiating agent. Freeze time 2026-10-16T23:37Z (written before any task GT was revealed; nothing in this section derives from a revealed GT).
- Freeze hashes (sha256, verified on disk against the brief before reading):
  - `tasks/d1_credit_account_billing_and_credits/credit.extended.yaml` 1976aeda1ceac6eff28cb78fadaae71601102bda1bd3339717f20edaf33dccd6
  - `tasks/d1_credit_account_billing_and_credits/task_tools.py` d4acab30c2c2b622b7c9e2382df1537cef4c9e9a8134618df924cf848974707a
- Fields read: `blueprint/blueprint.yaml`, `blueprint/db_schema.json`, `blueprint/share_tools.py` (signatures), `blueprint/products/{credit,pricing,order,vmi,vending}.yaml` (base charters and tier parameters), this difficulty's extended charter and tool module, `audits/render_source/XF_recipe.md`, the DSL evaluator semantics in `skills/erl-task-instantiate/scripts/check_compute.py` (MONTHS / within_months / LATEST / RND definitions only — gate tooling, no task content).
- Fields masked / unread at this freeze: every `tasks/*.json`, `plan.md`, `worklog.md`; `_masked_keys` of both views (design_rationale, db_closure, db_closure_matches_initial_state, solvability_contract, evaluation_criteria, computations, prerequisite_closure, charter_scope, required_documents).
- Gate snapshot cited from the brief (`.audit_views/policy/d1_credit_account_billing_and_credits/r1/gates.txt`): EXTENDED OK / TASK TOOL CONTRACT OK / REPLAY OK / SOLVABILITY OK / COMPUTE OK / GROUNDING OK / SCOPE OK; check_traceability deferred until KB publish (coordinator-confirmed only unlock tool-name misses). Entry conditions complete.
- Base copy: `diff` of extended lines 1–1051 against `blueprint/products/credit.yaml` differs only by the 4-line extended banner comment → base section verbatim.

Policy short names used below: **P1** `credit_ext_window_discount_catchup` (book_cash_discount_2280b564, agent), **P2** `credit_ext_backorder_room_payment` (pay_by_bank_debit_4d9f44ce, user), **P3** `credit_ext_permanent_request_figure` (submit_limit_request_dcbbb504, user), **P4** `credit_ext_permanent_increase_grant` (decide_limit_request_85fdd39c, agent).

### policy_conflict_scan

- Subjects / targets: P1 `credit_cash_discount_taken`; P2 `credit_payment_received`; P3 `credit_limit_review_requested`; P4 `credit_limit_review_decided`, `credit_limit_changed`. No two extended policies write the same event or tool. Base `credit_evt_cash_discount` (subject incl. `credit_payment_received`) and `credit_evt_payment_methods` overlap P2's subject but govern discount eligibility and acceptance, not a payment amount — compatible.
- Triggers / eligibility inherited: P1 inherits `paid_inside_discount_window`; P2 inherits payment-method acceptance (ACH debit always accepted; certified-funds rule does not bar ACH); P3/P4 inherit `active_account_only` and `review_interval_elapsed` (base `credit_limit_review` S1–S3) and the desk-authority sentence S5 (see override_declarations F-C4).
- Time anchors: P1 latest payment / invoice date; P2 "today" (tool posts `ctx.now()`); P3 request "today"; P4 decision "today". No future-dated anchors.
- Cross-category read boundaries: P1 pricing (agreement dates/tier); P2 order (order_lines backorder rows), vmi (active program tier), pricing (active agreement commitment), vending (active machine); P3 pricing (active agreement tier/commitment); P4 vmi (active program go-live + vmi_activity fee rows), vending (active machine model). All read-only.
- Terminal states: P1 ar_balance −discount; P2 ar_balance −payment (ON-ACCOUNT); P3 pending request row; P4 decision row (+ credit_limit/last_review_date when approved).
- Claimed scopes of the M=2 tasks: inferred from the views alone (task0 persona = room payment → P2 root with P1 as its declared prerequisite; task1 to be confirmed in its own file). The two prerequisite components {P2,P1} and {P4,P3} are disjoint and jointly cover all four extended policies; confirmation against `charter_scope` is post-reveal (closing_checklist).

### rule_compute_equivalence

Mechanical sweep (scratch, normalised whitespace): every `compute_basis` quote of P1–P4 is a verbatim substring of its rule (0 misses); every `baseline.rule` sentence is in its rule; every binding has a basis entry and vice versa (P1 23/23, P2 20/20, P3 14/14, P4 19/19); no binding is claimed by two factors. Every factor ladder tier is stated in prose in the rule and implemented as a branch of its `decides` binding. Failures found by the sentence-by-sentence sweep:

- **F-C1 (XF9 tie, RED)** P1 rule: "when more than one payment entry carries that latest received date, the catch-up is not made under this rule." Compute `pay_ref`/`inv` = `LATEST(...)` (check_compute.py `LATEST`: strict `>`, first row in table order wins a tie) and `result` has no tie branch — on a tie the compute returns a positive discount for one arbitrary entry while the rule says no line is booked. A payment covering several invoices posts one row per invoice on one date (base event grain), so the tie domain is ordinary.
- **F-C2 (XF9 tie, RED)** Rules that select "the invoice with the latest invoice date" / "the permanent limit request with the latest request date" state no tie-break while compute takes LATEST's table-order pick: P2 `inv_tax_last`/`inv_merch_last` ("the ratio of the sales tax to the merchandise subtotal of the invoice with the latest invoice date"), P3 `latest_inv` ("whose invoice with the latest invoice date totals at least one and a half times…"), P4 `req_ref`/`req` ("the permanent limit request with the latest request date on the account"). Per-shipment billing posts several invoices on one date routinely; on such a world each of these has a second reading (which same-date row).
- **F-C3 (XF9 month-end, RED)** Every whole-month count in P1–P4 ("dated less than twelve whole months before today", "opened less than ten whole years", "at least twelve whole months ago", "the whole months open", "went live three or more whole months", "installed more than its model's ramp-up months in whole months", "twenty-four or more whole months", "eighty-four to one hundred seventy-nine whole months", "one hundred eighty or more whole months", "in the last twelve whole months", "in the last three whole months", "less than twenty-four whole months", "less than the tier's returned-payment lookback in whole months") states no month-end convention, while compute uses `MONTHS()` (day-of-month comparison, no clamp) and the in-force base charter states the opposite convention for its own month counts ("when the target month has no such day the boundary is the last day of that month", base `credit_limit_review` S3, `credit_evt_payment_methods` S5). Demonstration on the charter domain: start date 2026-03-31, today 2026-09-30 → base clamp convention: +6 months lands on the missing 2026-09-31, clamped to 2026-09-30 ≤ today → 6 whole months; `MONTHS('2026-03-31','2026-09-30')` = 6 − 1 (30 < 31) = 5. A P4 review-age or P3 open-months boundary at 6/12/24 months flips tier on such dates. Whether this reaches either task's world is decided per task (frozen day-of-month 14 → no clamp case at NOW; see task files).
- **F-C4 (XF7 rounding, RED)** P1 rule: "rounded to the nearest cent only on that final figure", yet compute rounds two intermediates: `left_open: RND(...)` and `full_rate_disc: RND(inv_merch * P('cash_discount_pct') / 100, 2)`; the threshold "the tier's prompt-payment discount percentage of the invoice's merchandise subtotal" is compared unrounded by the rule and rounded by the compute. Domain demonstration: merchandise 1,234.50 at 1.0 % → rule threshold 12.345; compute 12.35 (Python round on the float); a payment leaving exactly 12.35 open is "more than" the threshold under the rule (pro rata / nothing) and "not more" under the compute (whole share).
- **F-C5 (XF10 filter, RED)** P3 rule tier: "forty for an account billed per shipment **on paper delivery** that was charged paper invoice fees in the last twelve whole months"; compute `lag_days` tests only `F('billing_cycle') == 'per_shipment' and paper_fees12 > 0` — the `invoice_delivery == 'paper'` condition is absent. Domain demonstration: per-shipment account that switched paper→email this year (fees still inside 12 months) → rule 30 days, compute 40 days.
- **F-C6 (XF12 cross-record window, RED)** P1 contract share: "nothing when the invoice … is dated while a Contract Pricing Agreement on a tier listed … is in force … an agreement is in force from its effective date through its closed date, or through its expiration date". The rule quantifies over every agreement of the customer and windows the invoice's date against each agreement's dates; compute reads `CFIELD('pricing', …)` with **no filter** (first pricing row of the customer, check_compute.py `CFIELD` → `hs[0]`). A customer with an expired/terminated agreement followed by a new one (pricing charter allows a new proposal once the earlier is no longer proposed/active/renewal_pending) has two candidates; compute reads whichever is first. Not scoped to a single candidate by any overwrite.
- **F-C7 (rule ambiguity on multiple holdings, RED)** P4 StockSmart and VendPoint allowances ("for a customer whose active StockSmart program went live…", "for a customer whose active VendPoint machine is a Smart Crib 300 or a Carousel 90 …") carry no single-holding scope (P2 has one: "A customer holding more than one active StockSmart program or more than one active VendPoint machine is quoted outside this rule."; P4 has none), while compute reads `CFIELD(..., status='active')` = first active row and `XSUM` over all the customer's programs' fee rows. The blueprint's typical customer holds "one or two VendPoint machines"; with two active machines the rule gives one allowance per machine, or one for "the" machine (which?), compute gives the first row's model only.
- Observation (not RED): P1's window gate ("A payment received inside the discount window…") and "carries no discount line" gate are eligibility conditions not implemented in `result` (compute yields a positive figure outside the window); they are write gates inherited from base `paid_inside_discount_window`, so they decide whether to write, not the value.
- Observation: `RND` is Python `round` (binary float, half-even at exact halves) while every tool contract says "rounded half up to the cent"; a .xx5 figure can land a cent apart. Checked per task on the scored figures.

### action_binding_and_uuids

- `(target_tool, computes)`: (book_cash_discount_2280b564, discount_amount) P1; (pay_by_bank_debit_4d9f44ce, payment_amount) P2; (submit_limit_request_dcbbb504, requested_limit) P3; (decide_limit_request_85fdd39c, approved_limit) P4 — each claimed once; no base policy names a target tool.
- uuid8s 2280b564 / 4d9f44ce / dcbbb504 / 85fdd39c: pairwise distinct, no shared prefix/suffix, no sequence pattern → independently generated.
- Tool bodies: none refuses, errors or hints on status, timing or a prerequisite (module docstring and every body checked: book → create + ar_balance −amount; pay → create ON-ACCOUNT ach_debit + ar_balance −amount; submit → create pending row; decide → create decision row, update limit/last_review_date only for approved/approved_reduced). Docstring claims all exist in bodies (XF8). No concrete example value in any docstring or param description (formats/prefixes only) (XF8 clean).
- **F-C8 (check 3, RED)** `submit_limit_request_dcbbb504` docstring: "the request stands pending **until** Corbett decides it" — an ordering word in a docstring that states the request's position before a decision by another party (the P4←P3 hop), outside P4's prerequisite sentence. Observation (same family, not counted): `decide_limit_request_85fdd39c` summary "Record Corbett's decision on a **pending** permanent credit limit request" restates P4's waited-on state in the contract.
- Other docstrings: no before/after/first/then, no other tool named.

### prerequisite_graph

- `prerequisite` filled on all four: P1 `[]`, P3 `[]`, P2 → P1 (value_input, gate `recv`, form state), P4 → P3 (value_input, gate `req`, form state). Both `problem` ids are extended policies of this file, neither self, graph {P2→P1, P4→P3} acyclic.
- `policy_source` verbatim in own rule: P2 "The room payment is worked out only after every payment received inside its invoice's discount window carries a discount line on that invoice." (rule sentence 2); P4 "A permanent increase is not decided until the account carries a permanent limit request with no decision recorded on it." (rule sentence 1). Both found by the mechanical sweep.
- `form: state`, no `fallback_reason` on either (correct). `kind: value_input`, gates `recv` (P2 compute `recv: F('ar_balance')`) and `req` (P4 compute `req`) exist.
- `condition` vs sentence: P2 condition "Every credit_payment_received entry … whose received date falls no later than the tier's cash discount days after the date of the invoice it is applied to has a credit_cash_discount_taken entry applied to that same invoice." = the sentence's scope ("every payment received inside its invoice's discount window"); P4 condition = sentence. Neither strengthened nor weakened.
- `resolved_by`/`effect`: book_cash_discount reduces `ar_balance` (body: `balance = ar_balance − amount`) → `recv` falls — genuine. submit creates a pending permanent row with `requested_limit` → `req` non-zero — genuine.
- No authoring-viewpoint phrasing in either `prerequisite` block.

### prerequisite_sentences

- P2 edge: connective "only after"; waited-on = record-visible state (a discount line on the invoice a payment is applied to); no tool, policy id, snake_case token or row id; state form. Exactly one write of this difficulty creates a `credit_cash_discount_taken` row: book_cash_discount_2280b564 (P1). Derivation: sentence → records (payments whose received date ≤ invoice date + cash_discount_days lacking a discount line) → the only policy whose rule books a discount line is P1 ("Corbett books that discount as a catch-up discount line when the account's most recent payment earned it and the invoice that payment is applied to carries no discount line") → book that line. Single reading **provided** the only unmet payment is the account's latest payment. Charter-level observation (per-task demonstration where exercised): the sentence's scope is every in-window payment, while P1 can only ever book the latest payment's line, and some in-window payments earn nothing (contract share nothing on an excluded-tier invoice; a short payment on a non-partial tier; a 0-day tier where a same-day payment is "no later than 0 days after") — on such worlds no write of this difficulty can make P2's state hold.
- P4 edge: connective "not until"; waited-on = a permanent request row with no decision row; state form; the only write creating a `credit_limit_review_requested` row is submit_limit_request_dcbbb504 (P3, owner user) → P3's rule "A customer asking Corbett for a higher permanent credit limit submits its own permanent limit request, and the limit the request names is … worked out under this rule." Single reading.
- Neither rule carries a second wording, tool name or other problem id about its dependency; neither depended-on rule (P1, P3) restates the sentence. Docstrings: see F-C8.
- No other cross-problem order in P1–P4 rules. Base sentences stating cross-problem order (`credit_account_closure` "first receives the refund … first pays it"; `credit_hold_and_collections` "released only after the payments that cure it have been posted") ground no edge of these trees.

### override_declarations

Sentence-by-sentence against each `base_policy_refs` entry (S-numbers = sentence order of the base rule):

- **P1 vs credit_evt_cash_discount.** S1 (cash_discount_pct on merchandise, never freight/tax) — overwritten, genuine conflict, `replaced_by` scoped "for every payment" (no out-of-scope remainder needed). S2 window, S3 counting — followed. **S4** "Only payment of the full remaining invoice balance (less the discount) earns the discount, except that on a tier whose cash_discount_partial_payment is true a partial payment inside the window earns the discount pro rata…" — **handled differently, undeclared (F-C9, XF5 RED)**: P1 decides full vs short payment against "the tier's prompt-payment discount percentage of the invoice's merchandise subtotal" (the full-rate discount), not against "the discount" the payment actually earns; wherever a share or a basis factor lowers the earned discount, a payment that deducted the full-rate discount has (base) short-paid → nothing (non-partial tier) / pro rata (partial tier), while P1 gives the whole share. S5 "No discount is earned on an invoice billed under a Contract Pricing Agreement whose tier is listed … and whose status is active on the invoice date" — **handled differently, undeclared (F-C10, XF5 RED)**: P1 replaces "status active on the invoice date" by a date window on the agreement's *current-term* `effective_date` (schema: "First day of the current term") .. closed/expiration date; an invoice dated in a prior term of a since-renewed excluded-tier agreement was billed while the agreement was active (base → no discount) but lies before the current effective date (P1 → whole rate); conversely an invoice dated in a renewal window (status renewal_pending, pricing lifecycle "active → renewal_pending … before the expiration date") is not under an *active* agreement (base exclusion silent) while P1 zeroes it. S6 (0-day tier; short-pay stays open) — followed.
- **P2 vs credit_evt_cash_discount / credit_evt_payment_methods / credit_hold_and_collections**, `overwrite: []`. No base sentence governs a payment amount; ACH debit accepted (payment_methods S1), card/check sentences not reached, "a payment without remittance detail is held unapplied…" matches the ON-ACCOUNT effect. Hold S1 over_limit test (limit × (1+over_limit_tolerance_pct)) is a different quantity from P2's room ceiling — no fight over the scored number; observation: when P2's tolerance used exceeds the tier's tolerance (+5/+2 contract points), a room payment computed under P2 leaves the account above the base over-limit hold threshold once the backorders ship (per-task check against the persona's "nothing gets held").
- **P3 vs credit_limit_review**, `overwrite: []`. Base never fixes the figure a customer requests; S1 (active only) inherited. No conflict.
- **P4 vs credit_limit_review.** S1, S2 (min months since review), S3 counting — inherited. S4 overwritten, genuine conflict, `replaced_by` restates approval test, caps and approved/approved_reduced, scope "for every permanent request". **S5** "When the increase granted (approved limit minus current limit) exceeds limit_increase_desk_approval_usd the request is decided referred_to_committee with approved limit 0.00 and the limit is unchanged." — in force, **dropped branch (F-C11, check 1 RED)**: P4 `result: MN(req, step_room, P('credit_limit_ceiling_usd'))` never produces 0.00, so on any world where the capped grant exceeds the tier's desk authority the in-force base clause gives `referred_to_committee` / 0.00 and P4's compute gives the capped limit. Likewise the on-time-percentage decline branch of the replaced_by text ("approved when … at least the tier's minimum") has no branch in compute (no 0.00 for a declined request) and the base `review_interval_elapsed` eligibility is not reflected — these two are eligibility outcomes; S5 is a value outcome on the scored quantity. S6 temporary (not reached), S7 timing, S8 effect — followed (tool body).

### factor_ladders

| policy | factor | label | decides | tiers | multi-source | cross_difficulty | verdict |
|---|---|---|---|---|---|---|---|
| P1 | earning_share_by_payment_coverage | method | earn_share | 3 | yes (open-balance rows ∧ tier param, both non-fall-through tiers) | — | **mislabelled (XF11)**: the three tiers set the multiplier `earn_share` ∈ {payment/invoice total, 0, 1} in the single formula disc_merch × earn_share × rate — "a swapped multiplier", not a change of formula shape |
| P1 | payment_record_share_of_rate | parameter | record_share | 3 (0/50/100) | no | — | ok |
| P1 | contract_share_of_rate | parameter | contract_share | 3 (0/75/100) | no | pricing | ok as ladder; see F-C6, F-C10 |
| P1 | discountable_merchandise_basis | method | disc_merch | 3 | no | — | **mislabelled + coincident (XF11)**: tiers are merch − X with X ∈ {disputed amount, return credits, 0}; on the fall-through's reachable domain (no open dispute, no return credit) tier 2's method gives merch − 0 = the fall-through's method |
| P2 | tolerance_share_by_tenure_and_returns | parameter | tol_share | 3 (0/50/100) | yes (opened_date ∧/∨ returned-payment rows) | — | ok |
| P2 | backorder_sales_tax_grossup | method | bo_counted | 3 | yes (billing_cycle ∧ invoice tax rows) | — | **mislabelled + coincident (XF11)**: tiers 1 and 2 are bo_open × (1 + r) with r taken from the latest invoice vs the 12-month aggregate (swapped window); the fall-through's domain is "no sales tax billed in the last twelve months", where tier 2's method gives bo_open × (1 + 0/merch12) = bo_open — coincides with the fall-through |
| P2 | stocksmart_month_end_billing | parameter | vmi_bill | 3 | no | vmi | ok (realism observation below) |
| P2 | contract_tolerance_points | parameter | tol_points | 3 (5/2/0) | no | pricing | ok |
| P2 | vendpoint_month_end_billing | parameter | vend_bill | 3 | no | vending | ok |
| P3 | purchase_base_measure | method | month_base | 3 | no (tier 2 is a single condition) | — | **partly a window swap (XF11)**: tier 1 (single latest invoice) is a different shape; tier 2 "invoice totals posted since opening divided by the whole months open" vs fall-through "invoice totals of the last twelve whole months divided by twelve" is Σ/n with a swapped window/divisor (for an account open < 12 months the two sums are the same rows) |
| P3 | billing_lag_days | parameter | lag_days | 3 (60/40/30) | no (tier 2 compound but tier 1 single) | — | ok as ladder; F-C5 compute omission |
| P3 | finance_charge_haircut | parameter | haircut | 3 (70/85/100) | no | — | ok |
| P3 | contracted_spend_support | parameter | support | 3 (25/12.5/0 %) | no | pricing | ok |
| P4 | step_start_by_payment_and_review_marks | parameter | step_start | 3 (25/35/tier max) | yes | — | **unreal on two terms tiers (F-C12)**: on Net 10 Starter and Net 30 Standard `limit_increase_max_step_pct` = 25, so the "both marks" tier (25 %) selects the same value as the fall-through (25 %) and the "one mark" tier (35 %) gives a marked account a *larger* step than a clean account — no credit desk penalises a clean record relative to a returned-payment/declined-request record |
| P4 | review_age_points | parameter | review_pts | 3 (+10/+5/0) | no | — | ok |
| P4 | denied_dispute_deduction | parameter | dispute_ded | 3 (−10/−5/0) | no | — | ok |
| P4 | account_age_points | parameter | tenure_pts | 3 (+5/+2/0) | no | — | ok |
| P4 | stocksmart_program_allowance | method | vmi_allow | 3 | no | vmi | ok: Σ billed fees (history aggregate) vs 3 × tariff fee vs none are distinct shapes; F-C7 multiplicity |
| P4 | vendpoint_model_allowance | parameter | vend_allow | 3 (full/half/none) | no | vending | ok; F-C7 multiplicity |

- Counts declared → surviving honest labels: P1 4 factors (2 parameter, 2 method declared; **0 honest method**) → fails "≥1 method"; P2 5 (4 parameter, 1 method declared; **0 honest method**) → fails; P3 4 (3 parameter, 1 method; the method factor has one honest shape-changing tier and one window-swap pair — XF11 member); P4 6 (5 parameter, 1 method honest). Multi-source per likely task: {P1,P2}: P1 earning share, P2 tolerance share (both survive as ladders; P1's as a parameter, not a method); {P3,P4}: P4 step_start. Cross-difficulty per likely task: {P1,P2}: pricing (P1), vmi/pricing/vending (P2); {P3,P4}: pricing (P3), vmi/vending (P4).
- XF1 independence (mechanical read-graph): no factor binding reads another factor's binding in P1–P4; assembly only in plain bindings (P1 `disc_rate`, `result`; P2 `tol_used`, `room_ceiling`, `result`; P3 `coverage`, `result`; P4 `step_used`, `step_room`, `result`). XF2: the generic combination sentences ("Every share of the discount rate this rule sets multiplies…", "Every amount a schedule in this rule adds is added…", "Every percentage point a schedule in this rule adds to or takes from…") name no factor quantity. XF3: P2 share-then-points order fixed by "The share of the tier's over-limit tolerance percentage that enters the tolerance percentage used"; P3 additions to the base before multiplication; P4 points before the increase, amounts after rounding — all fixed. XF4: no "as another policy figures it" phrase.
- Realism (observations unless a task world exercises them): P1 subtracts an open dispute's amount from the *merchandise* subtotal whatever the dispute reason, including `freight_billed_in_error` (a freight dispute does not lower the merchandise a cash discount is earned on); P2 reserves the StockSmart "monthly minimum fee" for every non-Onsite program although the vmi charter charges that fee only for a month whose program spend is below `min_monthly_program_spend_usd`; P2 counts VendPoint ramp-up as "installed more than its model's ramp-up months in whole months" while the vending charter counts "full calendar months after the installation month"; P3's run-rate tier takes a single latest invoice as a month's purchases, which is a month only under monthly consolidated billing (per-shipment: one shipment).

### findings

| id | class | policies | summary | bears on |
|---|---|---|---|---|
| F-C1 | XF9 tie / SOURCE-POLICY RED | P1 | stated tie rule ("catch-up is not made") absent from compute | task with P1 |
| F-C2 | XF9 tie / SOURCE-POLICY RED | P2, P3, P4 | "latest invoice" / "latest request" with no tie-break; LATEST table-order pick | both tasks (per-world demonstration) |
| F-C3 | XF9 month-end / SOURCE-POLICY RED | P1–P4 (all whole-month counts listed) | no month-end convention; MONTHS() differs from the base's own clamp convention | both (per-world) |
| F-C4 | XF7 rounding / SOURCE-POLICY RED | P1 | intermediate RND on threshold vs "only on that final figure" | task with P1 |
| F-C5 | XF10 filter / SOURCE-POLICY RED | P3 | "on paper delivery" missing from compute | task with P3 |
| F-C6 | XF12 cross-record window / SOURCE-POLICY RED | P1 | agreement-in-force windowing over all agreements; compute reads first pricing row | task with P1 |
| F-C7 | multiplicity / SOURCE-POLICY RED | P4 | no single-holding scope for StockSmart/VendPoint allowances | task with P4 |
| F-C8 | check 3 / SOURCE-POLICY RED | P3 tool | ordering word "until" in submit docstring | task with P3/P4 |
| F-C9 | XF5 undeclared departure / SOURCE-POLICY RED | P1 | base S4 full-balance-less-the-discount test replaced by full-rate threshold, undeclared | task with P1 |
| F-C10 | XF5 undeclared departure / SOURCE-POLICY RED | P1 | base S5 "status active on the invoice date" replaced by current-term date window, undeclared | task with P1 |
| F-C11 | check 1 dropped branch / SOURCE-POLICY RED | P4 | in-force base S5 referral (0.00) never produced by compute | task with P4 |
| F-C12 | unreal ladder / SOURCE-FACTOR RED | P4 | step_start ladder coincides/inverts on 25 %-step tiers | task with P4 (if on those tiers; charter-level regardless) |
| F-C13 | XF11 method / SOURCE-FACTOR RED | P1 (earning share, discountable merchandise), P2 (sales-tax gross-up), P3 (purchase base tier 2 vs fall-through) | method tiers swap a multiplier / subtrahend / window; P1 and P2 have no honest method factor | both tasks |

XF-class completeness lists (every member in the charter, so one rework can close each class):
- XF9 ties: P1 pay_ref/inv (stated, unimplemented); P2 inv_tax_last + inv_merch_last; P3 latest_inv; P4 req_ref + req. (P1 inv_date is filtered to one document — not a member.)
- XF9 month-end: P1 fc12; P2 opened_m, ret_n, tax12/merch12 window, vend_bill ramp test; P3 purch12/merch window, open_m (both tiers), paper_fees12, fc12; P4 ret12, dec24, rev_m, denied12, open_m, vmi_live, vmi_allow window.
- XF7 rounding: P1 left_open, full_rate_disc. (P2, P3, P4 RND placement matches their rounding sentences.)
- XF10 filters: P3 lag_days (paper delivery). No other stated filter missing; no compute filter unstated.
- XF11 method: P1 earning_share_by_payment_coverage, P1 discountable_merchandise_basis, P2 backorder_sales_tax_grossup, P3 purchase_base_measure (tier 2 vs fall-through). P4 stocksmart_program_allowance passes.
- XF12 / multiplicity: P1 contract share (all agreements); P4 vmi_allow/vmi_live, vend_allow (multiple active holdings). P2 is scoped.
- XF5 overwrites: P1 base S4, P1 base S5 (undeclared departures); P4 base S5 (dropped branch, in force).

## closing_checklist

Written after both task derivations were frozen (0.md 23:43Z, 1.md 23:46Z) and both GTs revealed (23:46–23:47Z). The section above was not edited after the reveals.

- Per-task files `0.md`, `1.md` correspond one-to-one with `tasks/0.json`, `tasks/1.json`; this file sits alongside; revision_1 is the first revision. Comparison sections: **neither carries a PASS** (task0: SOURCE-CHAIN, SOURCE-FACTOR, SOURCE-TASK; task1: SOURCE-POLICY, SOURCE-CHAIN, SOURCE-FACTOR). Scored values in both tasks equal the independent derivation (134.93, 2,382.95; 191,236.72, 146,587.00 approved_reduced).
- Coverage / scope: `charter_scope` task0 = {P1, P2}, task1 = {P3, P4} — pairwise disjoint over whole trees, jointly cover the four extended policies; task tools closed per task; uuid8s independent (§ action_binding_and_uuids).
- Trees: task0 P2←P1, task1 P4←P3; each one prerequisite, one value_input edge, one owner=user write (P2 pay; P3 submit), acyclic; the difficulty graph {P2→P1, P4→P3} is a DAG with no cross-task edge. Both trees hold on the DB; persona steering (T0-2, T1-2) is the open chain defect.
- Factors: every computation has 4–6 factors, a self-sufficient baseline (fall-backs 612.50, 0.00, 102,402.19, 150,000.00, all ≠ gold), every factor bears weight on its world, multi-source and cross-difficulty present per task — but P1 and P2 have no honest `method` factor and P3's method factor has a window-swap pair (F-C13); P4 step_start ladder unreal on 25 %-step tiers (F-C12); both tasks carry a near-miss on a non-producible seed row (T0-1, T1-1).
- Instantiation-stage gates: not re-run by this auditor (Step 0); cited from the coordinator snapshot `.audit_views/policy/d1_credit_account_billing_and_credits/r1/gates.txt` (all seven OK). Machine green does not cover F-C1 … F-C13.
- Open charter REDs: F-C1, F-C2, F-C3, F-C4, F-C5, F-C6, F-C7, F-C8, F-C9, F-C10, F-C11 (SOURCE-POLICY), F-C12, F-C13 (SOURCE-FACTOR).

VERDICT revision_1: task0=RED SOURCE-CHAIN,SOURCE-FACTOR,SOURCE-TASK task1=RED SOURCE-POLICY,SOURCE-CHAIN,SOURCE-FACTOR charter=F-C1,F-C2,F-C3,F-C4,F-C5,F-C6,F-C7,F-C8,F-C9,F-C10,F-C11,F-C12,F-C13

## revision_2

## charter_global_frozen (revision_2)

- Auditor: same independent auditor. Freeze 2026-10-17 (written before any revision_2 GT reveal; `tasks/*.json`, `plan.md`, `worklog.md` not opened in this round before the task freezes).
- Hashes verified on disk against the brief: `credit.extended.yaml` e5361f70c404ff254ab698545b60fe9e22533b0371ed6b5436205109ac1ae4c0 (r1 1976aeda… — changed), `task_tools.py` ab50360b67d2245646232e2c55422e4f5e2d2e65a588289e31e45c85c03ec2e6 (r1 d4acab30… — changed) → every charter-global section below is re-derived in full, not carried forward. Gate snapshot `.audit_views/policy/d1_credit_account_billing_and_credits/r2/gates.txt`: seven OK. Base section still verbatim (diff of lines 1–1047 vs `blueprint/products/credit.yaml` empty); blueprint files' mtimes unchanged since 2026-10-16 16:28Z.
- Old revision_1 text above left untouched.

### policy_conflict_scan (r2)

Subjects, targets, owners, cross-category read sets and terminal states as in revision_1, with these changes: P1 now reads pricing `status` (live = active or renewal_pending); P2 now reads `vmi_activity` (monthly minimum fee rows) and `vending_transactions` (usage bills); P2 caps the tolerance used at the tier's over-limit tolerance; P4 now carries the desk-authority referral and a multiple-holding scope. No two extended policies write one event/tool. Scope components {P1,P2} / {P3,P4} disjoint and complete (confirmed post-reveal).

### rule_compute_equivalence (r2)

Mechanical sweep: all `compute_basis` quotes verbatim in their rules (P1 27/27, P2 24/24, P3 14/14, P4 22/22); every baseline.rule sentence in its rule; no binding claimed by two factors; no factor binding reads another factor's binding (read-graph); RND only on P1/P2/P3 `result` and P4 `step_room`, matching each rounding sentence. Status of revision_1 items:

- F-C1 **closed**: P1 rule "when more than one payment entry carries that latest received date, no catch-up discount is booked under this rule and the catch-up figure is nothing" ↔ `pay_ties` / `result: 0 if (pay_ties > 1 …)`.
- F-C2 **closed**: P2 "of all invoices dated on the latest invoice date" ↔ `tax_last_day`/`merch_last_day` sums by date; P3 "latest statement, meaning the invoice totals posted on the latest invoice date" ↔ `latest_stmt`; P4 "or when more than one permanent request carries that latest request date, nothing is decided" ↔ `req_ties`.
- F-C3 **closed**: P1–P4 each carry "Whole months between a date and today are the difference in calendar months, less one when today's day of the month is earlier than that date's day of the month, with no move of a month-end date to a shorter month's last day." = `MONTHS()`; `within_months` = MONTHS < N (and ≥ 0).
- F-C4 **closed**: P1 "compared without rounding"; `left_open`, `full_rate_disc` unrounded.
- F-C5 **closed**: P3 `lag_days` now tests `F('invoice_delivery') == 'paper'`.
- F-C6 **closed**: P1 reads only the customer's live agreement (status active or renewal_pending); the pricing charter allows at most one agreement in {proposed, active, renewal_pending} ("A new proposal is not issued while the customer has an agreement whose status is proposed, active or renewal_pending") → one candidate.
- F-C7 **closed**: P4 "A customer holding more than one active StockSmart program or more than one active VendPoint machine is decided outside this rule."
- **F-C14 (XF10, NEW, SOURCE-POLICY RED).** P2 rule: "it is the usage billed **on the machine** in the last three whole months divided by three" and "the tier's monthly minimum fee for a customer whose **active program** … was charged a monthly minimum fee dated less than one whole month before today"; compute `vend_usage3: XSUM('vending','vending_transactions','extended_amount', within_months=…, event_type='vending_usage_billed')` and `vmi_min_fees: XCOUNT('vmi','vmi_activity', within_months=1, …, fee_type='monthly_minimum_fee')` sum/count over **every** machine/program of the customer (check_compute.py `_xrows`: customer_id match or any owned holding). The single-active scope sentence does not exclude removed/suspended machines or closed/paused programs. Domain demonstration: one active machine plus a machine removed in August that billed 900.00 usage in August → rule 3-month average of the active machine; compute adds 300.00. Members of the class: P2 `vend_usage3`, P2 `vmi_min_fees` (P4 `vmi_allow` says "the customer's StockSmart programs" — consistent, not a member).
- Observation (kept from r1): P1's window / "no discount line" gates and P4's on-time decline and "decided outside this rule" scope are write gates without a compute branch.

### action_binding_and_uuids (r2)

- `(target_tool, computes)` and uuid8s unchanged (2280b564, 4d9f44ce, dcbbb504, 85fdd39c); bodies unchanged; no body checks status, timing or prerequisite.
- F-C8 **closed**: submit docstring now "the request is recorded with its decision marked pending and changes nothing on the account itself" (no "until"); decide summary no longer says "pending". Grep for until/before/after/first/then over the module: no hit. No example values (XF8 clean).

### prerequisite_graph / prerequisite_sentences (r2)

Unchanged edges (P2→P1 value_input `recv`, state; P4→P3 value_input `req`, state); `policy_source` verbatim in own rules; acyclic; resolved_by/effect genuine; no second wording; docstrings now silent. r1 observation on P2's sentence scope (every in-window payment vs P1's latest-payment write) unchanged — observation.

### override_declarations (r2)

- P1 S1 overwritten (unchanged). **F-C9 closed**: base S4 now overwritten — "A payment that leaves open on its invoice no more than the tier's prompt-payment discount percentage of that invoice's merchandise subtotal counts as payment of the full remaining balance, and for every payment the merchandise it pays for is set by the payment allocation of this rule …" (scope "for every payment"; genuine conflict; S6 short-pay sentence still consistent — the unearned remainder stays open).
- **F-C10 closed as an undeclared departure** (base S5 now overwritten, scope "for every payment"), but see **F-C15** below.
- **F-C11 closed**: P4 rule "When the increase granted, the granted limit less the current credit limit, exceeds the tier's desk approval amount, the request is decided referred to committee, the granted figure is nothing and the limit is unchanged." ↔ `result: 0 if (granted - F('credit_limit')) > P('limit_increase_desk_approval_usd') else granted` — same as base S5.
- P2 `overwrite: []`: new cap "the tolerance percentage used never exceeds the tier's over-limit tolerance percentage" keeps the room ceiling at or below the base over-limit threshold — closes the r1 observation.
- **F-C15 (NEW finding on the S5 overwrite, SOURCE-POLICY RED).** `replaced_by` / rule: "… only when the invoice is dated inside that agreement's current term, from its effective date through its closed date or, with no closed date, its expiration date; an invoice dated outside that term, or a customer with no live agreement, **carries no contract share**." and later "The contract share of the discount rate is nothing when the live agreement is on a tier listed …, three quarters when …, and the whole rate otherwise." (a) Second reading: "carries no contract share" read against the defined quantity "the contract share of the discount rate is nothing …" gives a contract share of nothing → discount 0.00 for every customer with no live agreement or an out-of-term invoice, while compute (`contract_share` → `K('whole_share')`) gives the whole rate; domain: any customer without a live Contract Pricing Agreement whose latest payment earned a discount. (b) Realism: `effective_date` is "First day of the current term" (schema), so an invoice billed at net prices in the prior term of a since-renewed Net-Price / Cost-Plus / Strategic agreement is "outside that term" and earns the whole cash discount — the opposite of the base reason the clause retires ("because those prices are already net"); no distributor gives a prompt-pay discount on a net-priced invoice because the contract was renewed afterwards.
- P4 S4 overwrite unchanged and genuine.

### factor_ladders (r2)

| policy | factor | label | tiers | multi-source | xd | r2 verdict |
|---|---|---|---|---|---|---|
| P1 | payment_allocation_to_merchandise | method | freight-and-tax-first allocation, floored / nothing / whole subtotal | yes | — | honest: tier 1 is a sequential allocation with a floor on payment, freight and tax (not a multiplier); distinguishing inputs exist pairwise |
| P1 | payment_record_share_of_rate | parameter | 0 / 50 / 100 | no | — | ok ("charged" replaces "carrying" — r1 wording observation closed) |
| P1 | contract_share_of_rate | parameter | 0 / 75 / 100 | no | pricing | ladder ok; F-C15 |
| P1 | discountable_merchandise_deduction | parameter (relabelled) | merch − goods-dispute amount / merch − returns / merch | yes (tier 2) | — | honest as parameter; goods-reason filter closes the r1 freight-dispute realism observation |
| P2 | tolerance_share_by_tenure_and_returns | parameter | 0 / 50 / 100 | yes | — | ok |
| P2 | backorder_sales_tax_ratio | parameter (relabelled) | same-date ratio / 12-month ratio / zero | yes | — | honest as parameter |
| P2 | stocksmart_month_end_billing | parameter | onsite fee / minimum fee if charged in the last month / nothing | yes (tier 2) | vmi | ok; closes r1 realism observation; F-C14 |
| P2 | contract_tolerance_points | parameter | 5 / 2 / 0 | no | pricing | ok (subject to the new cap) |
| P2 | vendpoint_month_end_billing | method | 3-month usage average (+cellular) / cellular tariff / nothing | no | vending | honest (history aggregate vs flat tariff); F-C14. Observation: a machine inside ramp-up still bills its usage under `vending_evt_usage_billing`; tier 2 counts only the cellular fee for it |
| P3 | purchase_base_measure | method | run rate / blend of statement and average / average (consolidated only) | yes | — | honest: single statement, two-term average, twelve-month average; r1 window-swap pair removed |
| P3 | billing_lag_days | parameter | 60 / 40 / 30 | no | — | ok (F-C5 closed) |
| P3 | finance_charge_haircut | parameter | 70 / 85 / 100 | no | — | ok |
| P3 | contracted_spend_support | parameter | 1/4 / 1/8 / 0 | no | pricing | ok |
| P4 | step_start_by_payment_and_review_marks | parameter | ½ / ¾ / whole of tier max step | yes | — | **F-C12 closed**: monotone and distinct on every tier (25 % tiers: 12.5 / 18.75 / 25) |
| P4 | review_age_points, denied_dispute_deduction, account_age_points | parameter | as r1 | no | — | ok |
| P4 | stocksmart_program_allowance | method | as r1 | no | vmi | ok |
| P4 | vendpoint_model_allowance | parameter | as r1 | no | vending | ok |

- Counts: P1 4 (3 p, 1 m), P2 5 (4 p, 1 m), P3 4 (3 p, 1 m), P4 6 (5 p, 1 m) — each ≥ 2 parameter and ≥ 1 honest method. **F-C13 closed.** XF1–XF4 clean (read-graph; generic assembly sentences; P2 order "added … and … never exceeds" fixes points-then-cap; no "as another policy figures it").

### findings (r2)

| id | status r2 | note |
|---|---|---|
| F-C1 … F-C13 | closed | evidence above |
| F-C14 | **NEW — SOURCE-POLICY RED (XF10)** | P2 `vend_usage3`, `vmi_min_fees` read every holding of the customer; rule reads the active machine / active program |
| F-C15 | **NEW — SOURCE-POLICY RED (XF5 replaced_by + second reading + realism)** | P1 S5 overwrite: "carries no contract share" (zero vs whole), and current-term boundary grants a cash discount on prior-term net-priced invoices |

XF-class completeness (r2): XF10 members = P2 vend_usage3, P2 vmi_min_fees (only). XF5 members = P1 S5 overwrite `replaced_by` (only; P1 S1/S4, P4 S4 clean). Classes XF1–XF4, XF6–XF9, XF11, XF12 have no remaining member; XF13 is judged per task world.

## closing_checklist (revision_2)

Written after both r2 task derivations were frozen (02:21Z) and both r2 GTs revealed (02:22Z); the revision_2 charter-global section above was written before the reveals and not edited after.

- Files: `0.md`, `1.md` each carry revision_1 (untouched) and revision_2; this file likewise. Comparison r2: task0 RED (SOURCE-FACTOR, T0-4), task1 PASS; scored values equal the independent r2 derivation (128.08, 2,550.42; 191,236.72, 149,087.00 approved_reduced).
- Round-1 REDs: F-C1 … F-C13 closed; T0-1, T0-2, T0-3, T1-1, T1-2, T1-3 closed. Regressions: none found. New: F-C14 (XF10), F-C15 (XF5 / second reading / realism) at charter level; T0-4 (XF13) in task0.
- Scope: task0 {P1, P2} + {book, pay}; task1 {P3, P4} + {submit, decide} — disjoint, jointly complete; uuid8s unchanged and independent.
- Trees: one prerequisite each, value_input, one owner=user write each, difficulty graph acyclic, no cross-task edge; personas raise only the root.
- Factors: every computation 4–6 factors, ≥ 2 parameter, ≥ 1 honest method; multi-source and cross-difficulty per task; every factor bears weight against an honest baseline; all-baseline figures 612.50 / 0.00 / 102,402.19 / 150,000.00 ≠ gold.
- Gates: cited from `.audit_views/policy/d1_credit_account_billing_and_credits/r2/gates.txt` (seven OK), not re-run by this auditor.
- Open charter REDs: F-C14, F-C15.

VERDICT revision_2: task0=RED SOURCE-FACTOR task1=PASS charter=F-C14,F-C15

## revision_3

## charter_global_frozen (revision_3)

- Entry: worklog tail `REWORK round 3: gates 7/7 green`; `/tmp/erl0068_coord/snapshot.sh d1_credit_account_billing_and_credits 3` executed (not read) → `.audit_views/policy/d1_credit_account_billing_and_credits/r3/gates.txt` EXTENDED / TASK TOOL CONTRACT / REPLAY / SOLVABILITY / COMPUTE / GROUNDING / SCOPE all OK. Hashes: `credit.extended.yaml` 83721d9f10463e3d3da3b6c3d357a41c50aa3f8740189a36d028054ad07acfd3 (r2 e5361f70… — changed); `task_tools.py` ab50360b67d2245646232e2c55422e4f5e2d2e65a588289e31e45c85c03ec2e6 (= r2); views r3/task0 eafac132c7a8efc90e6f20f3409c042c252d573c15e57b1f2d3532ffa7c21b49 (changed), r3/task1 b8e570719ddedae846229c8d38fd9a9fd4e2334b8f74400900dfd9dcea29637d (= r2, byte-identical).
- Base section still verbatim; blueprint unchanged (mtimes 2026-10-16).
- **contamination_disclosure (process, no GT):** while checking which policies changed I printed the first five lines of the worklog's "Rework round 3" section (its F-C14 member list and the two filter bindings) before the task freezes. They carry no scored value, parameter or GT sequence, and restate what the charter itself shows; no other worklog/plan/tasks content was read before the freezes.
- Carry-forward: `task_tools.py` unchanged → § action_binding_and_uuids (r2) carried forward by reference. P3 and P4 re-read in full: rule, compute, params and factors identical to the r2 text audited in § revision_2 → their r2 conclusions carried forward. P1 and P2 changed → re-derived below.

### rule_compute_equivalence / XF sweep (r3, P1 and P2)

- Mechanical: basis quotes verbatim (P1, P2), baseline sentences present, binding/basis keys equal, no factor binding reads another factor's binding (new plain `pa_out_of_scope` reads `pa_eff`/`inv_date` — a plain gate, not a factor; the new `vmi_prog`/`vend_mach` belong to their own factors). RND only on `result`.
- **F-C14 closed.** P2 rule "was itself, that active program and no other, charged a monthly minimum fee …" ↔ `vmi_min_fees … vmi_program_id=vmi_prog` (`vmi_prog = CFIELD('vmi','vmi_program_id', status='active')`); "the usage billed on that active machine alone, never on another of the customer's machines" ↔ `vend_usage3 … vending_machine_id=vend_mach`. `_xrows` applies the extra equality filter on the row field — both tables carry those columns. No other cross-holding history read in P1/P2 (P4 `vmi_allow` reads "the customer's StockSmart programs", consistent, carried).
- **F-C15 closed as stated.** S5 `replaced_by`/rule now: "… for an invoice dated inside that agreement's current term, from its effective date through its expiration date; a customer whose pricing records hold no agreement other than a proposed or withdrawn one has the whole rate as its contract share; and when the customer holds an expired or terminated agreement, or the invoice is dated before the current effective date of its live agreement, no catch-up discount is booked under this rule and the catch-up figure is nothing." — "carries no contract share" gone (no second reading; no-agreement → whole = `contract_share` fall-through); prior-term invoices no longer earn a discount (`pa_out_of_scope` → `result` 0). Compute ↔ rule: `pa_out_of_scope: EXISTS expired or EXISTS terminated or DAYS(pa_eff, inv_date) < 0` ✓; `pa_end` = expiration date ✓.
- XF1–XF13 re-applied to P1/P2: XF1 ✓; XF2 ✓ (generic assembly sentences unchanged); XF3 ✓; XF4 ✓; XF5 — see F-C17; XF6 ✓; XF7 ✓; XF8 (tools unchanged) ✓; XF9 ties/month-end/absent/zero-division ✓ (new branch guarded on `inv_date and pa_eff`); XF10 ✓ (F-C14 closed, no new member); XF11 ✓ (labels unchanged from r2); XF12 ✓ (one live agreement; out-of-term cases scoped); XF13 per task.

### override_declarations / prerequisite (r3)

- **F-C17 (NEW in r3, SOURCE-POLICY RED — realism of the S5 replacement, XF5 class).** The new branch "when the customer holds an expired or terminated agreement … no catch-up discount is booked under this rule and the catch-up figure is nothing" withholds an earned prompt-payment discount from every customer whose pricing history merely contains an ended agreement, whatever the agreement's tier and whether or not the invoice was billed under it. Domain demonstration: Net 30 Preferred account (1 %, 10 days), a Corbett Category Contract that expired 2025-06-30 and no live agreement, invoice at list price dated 2026-09-30 paid in full on 2026-10-08 → the retired base clauses gave the full 1 % discount (no excluded tier active on the invoice date) and P1's own ladder gives "the whole rate"; the new branch gives nothing. The same holds for a customer with an expired agreement *and* a live Category Contract on a current-term invoice. No distributor publishes "an expired pricing contract forfeits the cash discount on later invoices"; the business reason of the retired clause ("those prices are already net") concerns only invoices billed at net prices.
- **F-C16 (SOURCE-POLICY RED, check 6/7 — escalated in r3).** P2's waited-on state "every payment received inside its invoice's discount window carries a discount line on that invoice" (condition: every in-window `credit_payment_received` has a `credit_cash_discount_taken` on that invoice) is stronger than the value dependency the edge declares ("The catch-up discount line lowers the account's receivable balance by the catch-up discount"): wherever the depended-on rule fixes the catch-up at nothing, no write of this difficulty can create the line (P1: "no catch-up discount is booked"; tool contract "positive"), so the room payment can never be worked out although the receivable it reads is already final. Demonstration: an in-window latest payment on an account with two finance charges dated < 12 whole months (record share nothing) → P1 discount 0 → P2 blocked. Members (complete list): (i) P1 record share nothing (two or more finance charges); (ii) contract share nothing (live excluded-tier agreement, invoice in term); (iii) non-partial tier short payment (merchandise paid for nothing); (iv) invoice with no merchandise; (v) same-date tie on the latest payment; (vi) **new in r3:** customer holding an expired/terminated agreement; (vii) **new in r3:** invoice dated before the live agreement's current effective date; (viii) any in-window payment that is not the account's latest payment (P1 only books the latest); (ix) a tier with `cash_discount_days` 0 where a payment is received on the invoice date ("no later than 0 days after"). Relation: recorded as an observation in r1/r2 § prerequisite_sentences (members i–v, viii, ix); the r3 rework widened it with (vi)–(vii); it is a defect of the edge's condition/sentence, demonstrable as a no-route outcome, so it is recorded RED now.
- P1 S1/S4 overwrites and P4 S4 unchanged (carried). P2 `overwrite: []` unchanged.

### factor_ladders (r3)

P1 and P2 factor sets, labels and ladders unchanged from r2 except the contract-share fall-through wording ("otherwise (no agreement other than a proposed or withdrawn one, or a live agreement on another tier)") and the holding filters inside the StockSmart/VendPoint factors — r2 verdicts carried. P3/P4 carried. Counts unchanged; F-C12/F-C13 remain closed.

### findings (r3)

| id | status | class |
|---|---|---|
| F-C14 | closed | XF10 |
| F-C15 | closed | XF5 / second reading |
| F-C16 | **open — RED** (escalated; members i–ix above) | check 6/7 prerequisite condition |
| F-C17 | **open — RED** (new from the F-C15 fix) | XF5 replacement realism |

## closing_checklist (revision_3)

Written after both r3 freezes (13:35Z) and reveals (13:36Z); the revision_3 charter-global section was written before the reveals and not edited after.

- r2 REDs: F-C14 closed, F-C15 closed (its stated second reading and prior-term realism), T0-4 closed. Regressions: none (scored values 128.08 / 2,550.42 / 191,236.72 / 149,087.00 approved_reduced and every sensitivity unchanged; r1/r2-closed items still closed).
- New / escalated: F-C17 (new — the F-C15 replacement withholds an earned discount from any customer holding an ended agreement); F-C16 (the P2 prerequisite condition demands a discount line wherever P1 fixes the catch-up at nothing — recorded as an observation in r1/r2, widened by r3, now RED with its full member list in § override_declarations / prerequisite (r3)).
- Tasks: both PASS on all four relationships on their own worlds; scopes disjoint and complete; trees hold; factors bear weight with ≥1 honest method per computation.
- Gates cited from `r3/gates.txt` (seven OK), not re-run by the auditor.
- XF classes with remaining members: XF5 → F-C17 (P1 S5 replacement branch "expired or terminated agreement … nothing"; sole member — P1 S1/S4 and P4 S4 replacements clean). Prerequisite-condition class (check 6/7) → F-C16 members (i)–(ix). All other XF classes: no remaining member.

VERDICT revision_3: task0=PASS task1=PASS charter=F-C16,F-C17

## revision_4

## charter_global_frozen (revision_4)

- Entry: worklog tail `REWORK round 4: gates 7/7 green` (only that line read); `/tmp/erl0068_coord/snapshot.sh d1_credit_account_billing_and_credits 4` executed (not read) → `r4/gates.txt` seven OK. Hashes: `credit.extended.yaml` 05220986bbb4c11a32c3715da5ac836ca684482a6208c994ee129e6a79432583 (r3 83721d9f… — changed); `task_tools.py` ab50360b… (= r2/r3); r4 views task0 eafac132… (= r3), task1 b8e57071… (= r2/r3). Base section verbatim; blueprint unchanged.
- No worklog, plan or task JSON read before the freezes this round. contamination_disclosure: none.
- Carry-forward: per-policy content digests (sha256 of the policy mapping, first 12 hex) — P3 `4e9f747c8dd9` and P4 `40c322518502` equal to r3 → their r2/r3 conclusions carried; tools unchanged → § action_binding_and_uuids (r2) carried. P1 (`d9cff794926e`, r3 `b79d664ecb99`) and P2 (`ebb50b768d29`, r3 `06f8611172c7`) changed → re-derived.

### P1 / P2 sweep (r4)

- Mechanical: basis quotes verbatim; baseline sentences present; keys equal; three P1 overwrites quote base verbatim with `replaced_by` in rule; P2 prerequisite `policy_source` verbatim in its rule; no factor binding reads another factor's binding; RND only on `result`. P2 rule otherwise unchanged (F-C14 filters, cap, multiplicity scope, same-date ratio all still present).
- XF1–XF4, XF6–XF8, XF10, XF11 clean. XF9: new `pa_prop`/`ended_net` guarded on absent dates. XF12: ended agreements read by (tier, status) with the scope "A customer whose pricing records hold more than one expired or terminated agreement of the same tier and status is worked out outside this rule." → one candidate per read. XF5: see F-C18.

### status of revision_3 REDs

- **F-C17 closed.** The blanket branch "when the customer holds an expired or terminated agreement … the catch-up figure is nothing" is gone; an ended agreement now matters only for invoices dated inside its own term on an excluded tier (`ended_net`), and the Net 30 Preferred / expired-Category demonstration of r3 now earns the whole rate.
- **F-C16 closed.** P2's sentence is now "The room payment is worked out only after the account's most recent payment carries a discount line on the invoice it is applied to, wherever a catch-up discount above nothing is owed for that payment under the prompt-payment discount rule; where none is owed, the room payment waits on no discount line." Members (i)–(vii) and (ix) now wait on no line; (viii) non-latest payments are no longer in scope; the remaining waited-on state is exactly what P1's write creates. Connective "only after"; record-visible state; no tool, id or token; condition (prerequisite field) states the same scope. Observation: the applicability clause ("wherever a catch-up discount above nothing is owed … under the prompt-payment discount rule") is decided by computing the depended-on rule rather than by a record; the reader must evaluate that rule anyway to find the resolving write, so the single reading holds.

### new finding

- **F-C18 (SOURCE-POLICY RED, XF5 replacement / realism of the net-priced window).** New S5 `replaced_by`: an invoice is net-priced when dated "inside the current term of the customer's live Contract Pricing Agreement on a tier listed …, or on or after that live agreement's proposal date and before its current effective date, or from the effective date through the closed date of an expired or terminated agreement on such a tier". Against the pricing charter (`pricing_agreement_eligibility`: "the agreement takes effect on the signature date"; `pricing_agreement_signed.effective_date` "First day the agreement pricing applies"; renewals move `effective_date` but not `proposed_date`):
  - (a) the proposal-to-effective window flags as net-priced invoices billed **before the agreement ever took effect**, i.e. at Account Price Schedule prices. Demonstration: Net 30 Preferred account, Corbett Net-Price Contract proposed 2026-09-01, signed/effective 2026-10-01 (first term), invoice dated 2026-09-30 paid in full 2026-10-08 → retired base S5: agreement not active on the invoice date → 1 % discount earned; P1 r4: "on or after that live agreement's proposal date and before its current effective date" → net-priced → nothing. No distributor withholds a prompt-pay discount on a list-priced invoice because a contract was proposed earlier.
  - (b) for an ended agreement only its **last** term (current `effective_date` through `closed_date`) counts, so a net-priced invoice from an earlier term of a renewed-then-expired/terminated Net-Price, Cost-Plus or Strategic agreement is "not net-priced" and earns the whole rate — the prior-term defect of r2 F-C15(b), closed for live agreements by the proposal-date reach, survives for ended ones.
  - Members of the class (complete): P1 `pa_prior_net` lower bound (proposal date); P1 `ended_net` lower bound (last-term effective date). No other policy windows agreement terms.

## closing_checklist (revision_4)

Written after both r4 freezes and the reveal (14:15Z); the revision_4 charter-global section was written before the reveal and not edited after.

- r3 REDs: F-C16 closed, F-C17 closed. Regressions: none (scored values 128.08 / 2,550.42 / 191,236.72 / 149,087.00 approved_reduced and all sensitivities unchanged; every earlier-closed item still closed).
- New: F-C18 — the S5 replacement's net-priced window (a) reaches back to the live agreement's proposal date, flagging pre-effective list-priced invoices, and (b) covers only an ended agreement's last term. The reworker's own description ("on or after that live agreement's proposal date and before its current effective date (its earlier terms)") confirms the proposal-date bound was meant to reach earlier terms; it also captures the pre-signature window, which `pricing_agreement_eligibility` places before the agreement takes effect.
- Tasks: both PASS on all four relationships; scopes disjoint and complete; trees hold; factors bear weight.
- Gates cited from `r4/gates.txt` (seven OK), not re-run.
- XF classes with remaining members: XF5 → F-C18 members P1 `pa_prior_net` (proposal-date lower bound) and P1 `ended_net` (last-term lower bound). All other classes: none.

VERDICT revision_4: task0=PASS task1=PASS charter=F-C18

## revision_5

## charter_global_frozen (revision_5)

- Entry: worklog tail `REWORK round 5: gates 7/7 green` (only that line read); `/tmp/erl0068_coord/snapshot.sh d1_credit_account_billing_and_credits 5` executed (not read) → `r5/gates.txt` seven OK. Hashes: `credit.extended.yaml` 707504c6789af00a1ebaf89f65d6afc73c04679e9f96fe8067a798e910605ccf (changed); `task_tools.py` ab50360b… (unchanged); views task0 eafac132… and task1 b8e57071… (both unchanged since r3/r2). Base verbatim; blueprint unchanged. contamination_disclosure: none (no worklog/plan/task JSON before the freezes).
- Carry-forward by per-policy digest: P2 `ebb50b768d29`, P3 `4e9f747c8dd9`, P4 `40c322518502` = r4 → carried; tools → carried. P1 `bc424901088f` (r4 `d9cff794926e`) → re-derived.

### P1 (r5)

- Mechanical: basis quotes verbatim; baseline sentences present; overwrites quote base and sit in the rule; keys equal; no factor binding reads another factor's binding (new `pa_prop`, `pa_prior_unknown`, `ended_prior_unknown` are plain gates); RND only on `result`. XF1–XF4, XF6–XF11 clean; XF9 guards on absent dates present; XF12 per-(tier, status) reads with the duplicate scope sentence kept.
- Change: the proposal-date reach is removed; new rule sentence "The records keep only an agreement's latest term, so when an invoice is dated before the effective date of that latest term of a live, expired or terminated agreement on such a tier and the agreement was renewed, meaning more days than the tier's proposal validity separate its proposal date from that effective date, the invoice may belong to an earlier term and is worked out outside this rule, with a catch-up figure of nothing; when those dates are no further apart than the proposal validity, the latest term is the first and an earlier invoice was billed before signing." ↔ `pa_prior_unknown`, `ended_prior_unknown` → `result` 0. Sound against the pricing charter (signature no later than `proposal_validity_days` after the proposal; "the agreement takes effect on the signature date"; a renewal moves `effective_date` a full term later).

### status of revision_4 RED F-C18

- Member (a) **closed**: a first-term agreement's pre-signature invoice is "not net-priced … including one dated before an agreement took effect" → keeps its contract share (r4 demonstration: Net-Price proposed 2026-09-01, effective 2026-10-01, invoice 2026-09-30 → whole rate, discount earned).
- Member (b) **closed in outcome**: an invoice before the latest term of a renewed (live or ended) excluded-tier agreement no longer earns the whole rate (catch-up nothing).
- **Remaining member (c), F-C18 stays open (missed in my r4 member list — recorded here as such).** P1 reads the agreement's *current* `variant_name`, but `pricing_tier_changed` moves a live agreement to another tier mid-term "at an anniversary commitment review or by a signed amendment" and "a tier change never restarts the term" (`pricing_commitment_review`), with no tier-change date in the records. An invoice billed before the change carries the old tier's prices. Demonstration: Net-Price Contract effective 2025-07-01, downgraded to Category Contract at the 2026-07-01 anniversary; consolidated invoice 2026-06-30 (billed at net prices) paid in full 2026-07-08 → P1: live Category Contract in current term → three quarters → discount earned on a net-priced invoice; reverse case (Category upgraded to Net-Price by amendment) withholds an earned discount. The retired base clause turned on the tier "active on the invoice date"; no scope sentence routes this case outside the rule.

### new finding

- **F-C19 (SOURCE-POLICY RED, XF5 — replaced_by contradicts the new scope sentence).** The S5 `replaced_by` (rule sentence 4) ends "… and every invoice that is not net-priced, including one dated before an agreement took effect, keeps the contract share set out in this rule", while its own net-priced list covers only the live agreement's current term and an ended agreement's latest term. The new sentence 9 sends an earlier-term invoice of a renewed agreement "outside this rule, with a catch-up figure of nothing". Same situation, two conclusions: renewed live Net-Price Contract proposed 2023-05-01, current term effective 2025-07-01, invoice 2025-06-30 paid 2025-07-08 as the latest payment → sentence 4: not net-priced (outside the current term, no ended agreement) → keeps the contract share → whole rate; sentence 9: outside this rule → nothing (compute: nothing). The replaced_by neither names this scope-out nor excludes the case, against XF5 ("Its replaced_by restates the still-in-force content of the retired clause for every out-of-scope case and names its own scope"). Sole member.

### findings (r5)

| id | status | members remaining |
|---|---|---|
| F-C18 | open — RED (XF5 / realism of the net-priced window) | (c) mid-term tier change: P1 `pa_tier` (current tier) used for invoices billed before a `pricing_tier_changed` |
| F-C19 | new — RED (XF5 replaced_by scope) | P1 S5 replaced_by "every invoice that is not net-priced … keeps the contract share" vs rule sentence 9 |

## closing_checklist (revision_5)

Written after both r5 freezes and the reveal; the revision_5 charter section was written before the reveal and not edited after. The worklog's round-5 notes (read after the reveal) state the scope sentence and the replaced_by change as described above; they do not address a mid-term tier change, and they state "The S5 replaced_by has one reading", which the F-C19 demonstration contradicts.

- r4 RED F-C18: members (a) pre-signature window and (b) ended/renewed earlier terms closed; member (c) mid-term tier change remains (missed in my r4 list — this audit's omission, not a regression). New F-C19 (replaced_by "every invoice that is not net-priced … keeps the contract share" vs the new out-of-rule sentence). Regressions: none (scored values 128.08 / 2,550.42 / 191,236.72 / 149,087.00 approved_reduced and all sensitivities unchanged; every other earlier-closed item still closed).
- Tasks: both PASS on all four relationships; scopes disjoint and complete; trees hold; factors bear weight.
- Gates cited from `r5/gates.txt` (seven OK), not re-run.
- XF5 class — all remaining members in one place: (1) F-C18(c) P1 `pa_tier` / `contract_share` read the current tier for invoices billed before a `pricing_tier_changed` (both directions: downgrade grants a discount on a net-priced invoice; upgrade withholds an earned one); (2) F-C19 P1 S5 `replaced_by` (rule sentence 4) closing clause vs rule sentence 9. No other XF class has a remaining member.

VERDICT revision_5: task0=PASS task1=PASS charter=F-C18,F-C19

## revision_6

## charter_global_frozen (revision_6)

- Entry: worklog tail `REWORK round 6: gates 7/7 green` (only that line read); `/tmp/erl0068_coord/snapshot.sh d1_credit_account_billing_and_credits 6` executed (not read) → `r6/gates.txt` seven OK. Hashes: `credit.extended.yaml` ce7d2352f045c0ee9128aad5bda423ce4d1d12b25ad4df5dee14a218e9175323 (changed); `task_tools.py` ab50360b… (unchanged); views task0 eafac132…, task1 b8e57071… (unchanged). Base verbatim; blueprint unchanged. contamination_disclosure: none.
- Carry-forward by per-policy digest: P2 `ebb50b768d29`, P3 `4e9f747c8dd9`, P4 `40c322518502` = r5 → carried; tools carried. P1 `9858449e48cd` (r5 `bc424901088f`) → re-derived.
- Coordinator ruling applied (scenario worklog BLUEPRINT-KNOWN): the mid-term tier-change case is shared by frozen base `credit_evt_cash_discount` S5, which reads the agreement's recorded tier and status; an extended rule adopting base's reading, or leaving such invoices under base verbatim, is not an extended-layer defect.

### P1 (r6)

- Change: all three overwrites are now scoped — each `replaced_by` reads "For a payment on an invoice within this rule's scope …; every other invoice remains under the base cash-discount rule, …" and restates the base content (S1: percentage on merchandise; S4: full balance less the discount / pro rata on a partial-payment tier; S5: no discount under an excluded-tier agreement active on the invoice date). New scope sentence: "This rule covers only an invoice dated inside the current term of the customer's single Contract Pricing Agreement, from its effective date through its closed date or, with no closed date, its expiration date, and an invoice of a customer with no agreement on record; every other invoice remains under the base cash-discount rule." The proposal-validity / renewal sentence and the ended-agreement limbs are gone; contract share follows "the tier recorded on the customer's agreement".
- Mechanical: basis quotes verbatim; baseline sentences present; overwrites quote base and sit in the rule; keys equal; no factor binding reads another's; RND only on `result`. XF1–XF4, XF6–XF9, XF11, XF13 clean.

### status of revision_5 REDs

- **F-C18 closed** (under the ruling): in scope, the contract share reads the agreement's recorded tier, which is base S5's own reading; every out-of-scope invoice (prior terms, pre-signature, ended agreements) is left under base S5 verbatim. The extended layer adds no reading of the tier beyond base's.
- **F-C19 closed**: the conflicting pair ("every invoice that is not net-priced … keeps the contract share" vs the out-of-rule renewal sentence) is gone; the S5 replacement and the scope sentence now say the same thing (in-term → this rule; every other invoice → base).

### new / reopened findings

- **F-C6 reopened (XF12, regression).** Compute reads `pa_tier: CFIELD('pricing','variant_name')`, `pa_eff`, `pa_end` with **no status filter** (check_compute.py `CFIELD` → the customer's first pricing row); r2–r5 read the live agreement by status. The pricing charter allows several rows for one customer (a new proposal once no agreement is proposed, active or renewal_pending; ended rows stay). The rule says "the customer's single Contract Pricing Agreement" without saying what a customer with an ended row plus a live one is. Demonstration: an expired Net-Price row (closed 2025-06-30) stored first and a live Category Contract (effective 2025-07-01); invoice 2026-09-30 → compute reads the expired row → not in force → whole rate, while the live Category Contract's term covers the invoice → three quarters (if "single" means the live one) or base rule (if two rows put the customer out of scope).
- **F-C20 (NEW, SOURCE-POLICY RED — XF10 scope not in compute + second reading of the out-of-scope outcome).** The scope sentence ("This rule covers only …; every other invoice remains under the base cash-discount rule") has no branch in compute — `result` applies P1's formula (record share, allocation, contract share, deduction) to every invoice — and the rule does not say what P1 books for an out-of-scope invoice: sentence 1 books "that discount", i.e. "the prompt-payment discount set out in this rule", as the catch-up line. Same situation, three readings: Net 45 Business (1 %, 10 days, partial allowed), the customer's only agreement a Category Contract closed 2026-06-30, invoice 2026-09-30 merchandise 10,000.00, no freight or tax, paid 10,000.00 in full on 2026-10-08, one finance charge in the last twelve months → (A) out of scope, no catch-up under this rule → nothing, and P2's sentence ("wherever a catch-up discount above nothing is owed … under the prompt-payment discount rule") waits on no line; (B) the base rule's discount is owed and booked as the catch-up → 1 % × 10,000.00 = 100.00; (C) compute → 10,000.00 × 1 % × ½ = 50.00. The P2 room payment then differs by 0 / 100.00 / 50.00. Members (complete): every out-of-scope class the sentence names — invoice before the single agreement's effective date (pre-signature or earlier term), invoice after an ended agreement's closed date, a customer with more than one agreement row (overlaps F-C6).

### findings (r6)

| id | status | class |
|---|---|---|
| F-C18 | closed (ruling) | XF5 |
| F-C19 | closed | XF5 |
| F-C6 | **reopened — RED** | XF12 (P1 `pa_tier`, `pa_eff`, `pa_end` unfiltered) |
| F-C20 | **new — RED** | XF10 + second reading (P1 scope sentence vs `result`; out-of-scope catch-up outcome; P2 interplay) |

## closing_checklist (revision_6)

Written after both r6 freezes and the reveal; the revision_6 charter section was written before the reveal and not edited after. The worklog's round-6 notes (read after the reveal) say "The scope works as a write gate … outside it no catch-up line is booked under this rule, so P2's sentence waits on no line" and "the contract factor reads the single agreement (CFIELD with no status filter …)". The first is reading (A) of F-C20, but it is stated only in the worklog. The policy surface (rule, compute) does not carry it, and compute yields reading (C). The second confirms the F-C6 read.

- r5 REDs: F-C18 closed (under the coordinator's BLUEPRINT-KNOWN ruling), F-C19 closed. Regression: F-C6 (XF12) reopened by removing the status filter. New: F-C20 (scope sentence without a compute branch; the out-of-scope catch-up outcome is undetermined across rule / base / compute). Scored values and all sensitivities unchanged; every other earlier-closed item still closed.
- Tasks: both PASS on all four relationships.
- Gates cited from `r6/gates.txt` (seven OK), not re-run.
- Remaining members, all classes in one place:
  - XF12: P1 `pa_tier`, `pa_eff`, `pa_end`, which read the first pricing row (F-C6).
  - XF10 / second reading: the P1 scope sentence vs `result`. This covers every out-of-scope class: an invoice before the single agreement's effective date, an invoice after an ended agreement's closed date, and a customer with more than one agreement row. It also covers P2's "catch-up … owed under the prompt-payment discount rule" for those invoices (F-C20).
  - No other class has a remaining member.

VERDICT revision_6: task0=PASS task1=PASS charter=F-C6,F-C20

## revision_7

## charter_global_frozen (revision_7)

- Entry: worklog tail `REWORK round 7: gates 7/7 green` (only that line read); `/tmp/erl0068_coord/snapshot.sh d1_credit_account_billing_and_credits 7` executed (not read) → `r7/gates.txt` seven OK. Hashes: `credit.extended.yaml` a5696b40b5dbc87b621304d03b16af861748a51b429dd59c47e13f5fb0c45343 (changed); `task_tools.py` ab50360b… (unchanged); views task0 eafac132…, task1 b8e57071… (unchanged). Base verbatim; blueprint unchanged. contamination_disclosure: none.
- Per-policy digests: P3 `4e9f747c8dd9` = r6 → carried. P1 `86e1a0089031`, P2 `717141fe7be5`, P4 `eff04f4656f7` changed → re-derived. Tools carried.
- Renderer-class sweeps (XF 1, 2, 3, 9, 10, 12) run on all four policies, as asked.

### changes read

- P1: scope sentence now "This rule covers only an invoice dated inside the current term, from its effective date through its expiration date, of the customer's live Contract Pricing Agreement, meaning its one agreement whose status is active or renewal pending; for every other invoice, including any invoice of a customer with no live agreement or with more than one, the catch-up line carries exactly the base cash-discount rule's figure: the tier's prompt-payment discount percentage of the invoice's merchandise subtotal when the payment leaves open no more than that discount, that figure in the proportion of the payment to the invoice total for a payment leaving more open on a tier allowing partial-payment discounts, and nothing for such a payment on any other tier or for an invoice dated from the effective date through the closed date of an expired or terminated agreement on a cash-discount-excluded pricing tier, rounded to the nearest cent." ↔ `live_n`, `in_scope`, `base_excluded`, `base_share`, `base_figure`, `result: … if in_scope else base_figure`. Contract reads filtered by status again; S5 `replaced_by` reads "the tier recorded on the customer's live agreement".
- P2 (rule sentence 11) / P4 (rule sentence 12): the rule-only multiplicity scopes are replaced by "When the customer's active StockSmart programs are on more than one tier, or its active VendPoint machines are of more than one model, the StockSmart and VendPoint billing still to post are both counted as nothing [P4: neither allowance is added to the step room]; when several active programs share one tier, or several active machines share one model, the one the customer's records list first is read." ↔ plain `multi_holdings` gating `vmi_bill + vend_bill` (P2) / both allowances (P4).

### status of revision_6 REDs

- **F-C6 closed** for the live agreement: `pa_tier`/`pa_eff`/`pa_end` read status active or renewal_pending, `live_n == 1` in scope.
- **F-C20 closed**: out-of-scope invoices now have a stated figure, and compute branches to it.

### new findings (sweeps included)

- **F-C21 (SOURCE-POLICY RED, XF5: an internal conflict of the same shape as F-C19).** Rule sentence 4 (the S5 `replaced_by`) leaves "every other invoice … under the base cash-discount rule, under which no discount is earned on an invoice billed under an agreement on such a tier whose status is active on the invoice date". Sentence 8 gives every out-of-scope invoice "exactly the base cash-discount rule's figure". But its only exclusion is an invoice inside an **ended** excluded-tier agreement's last term. Demonstration: a renewed live Corbett Net-Price Contract whose current term is effective 2025-07-01; invoice 2025-06-30, billed under the same agreement while active, paid in full 2025-07-08 as the latest payment.
  - Sentence 4 / base S5: no discount.
  - Sentence 8 and compute: `base_excluded` is false, so `base_figure` = 1 % of merchandise.

  Sentence 8 is a paraphrase of the base clause that departs from base S5's own reading (recorded tier and status: active, Net-Price). It is not that clause verbatim, so the extended layer again introduces a reading beyond base's. Sole member.
- **F-C6 class, remaining member (XF12).** Sentence 8 excludes "an invoice dated from the effective date through the closed date of an expired or terminated agreement on a cash-discount-excluded pricing tier", which covers every such agreement. `base_excluded` instead reads one row per (tier, status) via `CFIELD(…, status='expired', variant_name=…)`, i.e. the first match. The r4 duplicate-agreement scope sentence is gone. A customer with two expired Net-Price rows is judged on whichever is listed first. Recorded as **F-C6b**.
- **F-C22 (SOURCE-FACTOR RED: XF1/XF2 factor independence, plus realism) — new in r7.** P2 sentence 11 and P4 sentence 12 zero the StockSmart **and** the VendPoint contribution together when either holding set is mixed. Two consequences follow:
  - Independence: the VendPoint factor's contribution is gated by StockSmart records, and vice versa ("No factor is gated through another factor").
  - Realism: the blueprint's typical customer holds "one or two VendPoint machines", so two machines of different models are ordinary. For such a customer every month-end program bill is counted as nothing (P2) and no program allowance is given (P4). For several same-model machines, only the first-listed machine's usage is counted. More holdings means more billing still to post, so no credit desk would reserve less, or nothing, for them.

  Members:
  - P2 `multi_holdings` gating `vmi_bill + vend_bill`;
  - P2 "the one the customer's records list first is read" (`vmi_prog` / `vend_mach` first row);
  - P4 `multi_holdings` gating `vmi_allow + vend_allow`;
  - P4 first-listed read (`vmi_live` / `vend_model`).

  Domain demonstration (P2): one StockSmart Weekly program plus Coil 40 and Locker 24 machines → StockSmart 400.00 and VendPoint usage both count as nothing.
- Sweep results otherwise:
  - XF1: no factor binding reads another's.
  - XF2: generic assembly sentences unchanged; `disc_rate`, `tol_used`, `step_used`, `step_room` are plain.
  - XF3: order fixed.
  - XF9: ties, month convention and absent/zero guards present. "The one the customer's records list first" is a stated row order (the find tools' listing order); it falls under F-C22, not as a tie defect.
  - XF10: stated filters match compute, except F-C6b.
  - XF12: F-C6b.
  - P3 (carried) clean on all six points.

### findings (r7)

| id | status | class |
|---|---|---|
| F-C6 | closed (live agreement) | XF12 |
| F-C6b | **open — RED** | XF12 (P1 `base_excluded` ended-agreement first match) |
| F-C20 | closed | XF10 |
| F-C21 | **new — RED** | XF5 internal conflict (P1 sentence 4 vs sentence 8) |
| F-C22 | **new — RED** | XF1/XF2 + realism (P2/P4 joint multiplicity zeroing; first-listed read) |

## closing_checklist (revision_7)

Written after both r7 freezes and the reveal; the revision_7 charter section was written before the reveal and not edited after. The worklog's round-7 notes, read after the reveal, bear on both new findings:
- Its probe "an invoice before the live term … gives 371.07 (base figure)" is the F-C21 behaviour. The compute gives the full base figure to a pre-term invoice whatever the live agreement's tier. Sentence 4's restated base S5 withholds it under an excluded tier.
- Its note "The DSL has no holding-count primitive, so this is the exact computable rule" confirms that the F-C22 outcome was chosen for computability rather than as a business treatment.

- r6 REDs: F-C6 closed for the live agreement (one member remains, F-C6b, on ended-agreement reads); F-C20 closed. New: F-C21, F-C22. Regressions: none in scored values (128.08 / 2,550.42 / 191,236.72 / 149,087.00 approved_reduced) or sensitivities. F-C6b is the r4 duplicate-ended-agreement scope dropped in this round.
- Tasks: both PASS on all four relationships.
- Gates cited from `r7/gates.txt` (seven OK), not re-run.
- Remaining members, all classes in one place:
  - XF5: P1 sentence 8's out-of-scope exclusion (ended agreements only) vs sentence 4's restated base S5 (an agreement active on the invoice date) (F-C21).
  - XF12: P1 `base_excluded` first match per (tier, status) for ended agreements (F-C6b).
  - XF1/XF2 + realism: P2 `multi_holdings` → `vmi_bill + vend_bill`; P2 first-listed program/machine read; P4 `multi_holdings` → `vmi_allow + vend_allow`; P4 first-listed read (F-C22).
  - No other class has a remaining member.

VERDICT revision_7: task0=PASS task1=PASS charter=F-C6b,F-C21,F-C22

## revision_8

## charter_global_frozen (revision_8)

- Entry: worklog tail `REWORK round 8: gates 7/7 green` (only that line read); `/tmp/erl0068_coord/snapshot.sh d1_credit_account_billing_and_credits 8` executed (not read) → `r8/gates.txt` seven OK. Hashes: `credit.extended.yaml` 02a603f01751a399a9f20f2dda5ec0276d5fe020f836f6ab9efcd1cbd7d41926 (changed); `task_tools.py` ab50360b… (unchanged); views task0 eafac132… (unchanged), task1 e542c81670459a27f6cf4c7cbf8b98d747e5cdacf49b8a8ef8a4ab336c541795 (changed: two `vending_usage_billed` rows added for Locker 24 VP-116052 — 2026-08-31 812.40, 2026-09-30 750.00). Base verbatim; blueprint unchanged. contamination_disclosure: none.
- Per-policy digests: P3 `4e9f747c8dd9` unchanged → carried; P1 `fdb12daf3d7c`, P2 `199a816c411f`, P4 `d91292bb2ae3` changed → re-derived; tools carried. Coordinator note applied: the single live agreement is read by base's own recorded tier/status (BLUEPRINT-KNOWN), and summing StockSmart/VendPoint billing over every holding from event rows is the intended business treatment.

### status of revision_7 REDs

- **F-C21 closed.** Sentence 8's out-of-scope exclusion now reads "… nothing … for an invoice billed under an agreement on a cash-discount-excluded pricing tier whose status is active on the invoice date, which the records show as the customer's live agreement recorded on such a tier with status active, the only agreement status and tier the records hold". This is base S5's own wording, read through the recorded status. ↔ `base_excluded: EXISTS('pricing', status='active') and CFIELD('pricing','variant_name', status='active') in P('cash_discount_excluded_pricing_tiers')`. Sentence 4's restated base S5 and sentence 8 now give the same answer. Example: a renewed live Net-Price contract with an earlier-term invoice → nothing under both. No reading beyond base's.
- **F-C6b closed.** No ended-agreement row is read any more; the only pricing reads are the live agreement's (status-filtered) and the existence of an active one.
- **F-C22 closed** in both of its parts:
  - P2 sentences 8/10 and P4 sentences 9/12 now aggregate "across all the customer's StockSmart programs" / "all the customer's VendPoint machines" from `vmi_activity` / `vending_transactions` rows (`XSUM` with no holding filter, matching the rule's "all").
  - No StockSmart record gates the VendPoint figure or vice versa.
  - There is no first-listed read, and the joint zeroing is gone.

### renderer-class sweeps (XF 1, 2, 3, 9, 10, 12) on all four policies

- XF1: mechanical read-graph clean in P1–P4.
- XF2: assembly lives in plain `disc_rate`, `tol_used`, `step_used`, `step_room` and `result`; generic sentences unchanged.
- XF3: order fixed.
- XF9:
  - "dated less than one whole month before today" = `within_months=1`;
  - "a program fee is dated two whole months before today" = `XCOUNT(within 3) − XCOUNT(within 2)` (MONTHS == 2);
  - month convention sentence present;
  - absent rows give 0;
  - tie rules kept.
- XF10: P2 tier 1 "onsite management fees plus the monthly minimum fees charged in that month" ↔ `vmi_onsite1 + vmi_min1`; P2 cellular "charged on them dated less than one whole month" ↔ `vend_cell1`; P4 thresholds ↔ `vend_full_usage` 3,000.
- XF12: aggregates only; no cross-record windowing.
- Mechanical basis / baseline / overwrite / prerequisite quotes all verbatim; RND as stated.

### new finding

- **F-C23 (SOURCE-FACTOR RED, XF11 / unreal ladder): the rebuilt holding factors are one formula written as tiers.**
  - P2 `vendpoint_month_end_billing` (method): tier 1 "that usage divided by three plus the cellular data fees charged … less than one whole month" (`vend_usage3/3 + vend_cell1`); tier 2 "those cellular data fees alone" (when `vend_usage3` = 0); fall-through nothing (both 0). On tier 2's whole domain tier 1's method gives 0/3 + cell = tier 2's figure, and on the fall-through's domain it gives 0. All three tiers are `vend_usage3/3 + vend_cell1`, so the method tiers coincide on their reachable domains. P2's only `method` factor is therefore not honest, and P2 falls below "≥ 1 method".
  - P2 `stocksmart_month_end_billing` (parameter): tier 1 "those onsite management fees plus the monthly minimum fees charged in that month"; tier 2 "those monthly minimum fees" (onsite = 0); fall-through nothing (both 0). These are one sum, `vmi_onsite1 + vmi_min1`, in every tier, so tiers 1 and 2 select the same quantity: an unreal ladder (no tier divides customers).
  - P4 `stocksmart_program_allowance` (method): the fall-through "nothing" has the domain "no fee two whole months back and no fee in the last month"; there tier 2's method "three times the fees billed in that month" gives 3 × 0 = 0. The fall-through coincides with tier 2 on its whole domain, the same pattern red-lit in r1 for P1 `discountable_merchandise_basis`. Tiers 1 and 2 remain distinct shapes (history sum vs one-month projection).
  - Domain demonstrations need no special world: any customer, for each of the three formulas above.
  - Members (complete): P2 `vend_bill`, P2 `vmi_bill`, P4 `vmi_allow` (fall-through). P4 `vend_allow` (whole / half / nothing at the 3,000.00 threshold) is a genuine parameter ladder; P1 and P3 factors unchanged and honest.

### findings (r8)

| id | status | class |
|---|---|---|
| F-C6b | closed | XF12 |
| F-C21 | closed | XF5 |
| F-C22 | closed | XF1/XF2 + realism |
| F-C23 | **new — RED** | XF11 / unreal ladder (P2 `vend_bill`, P2 `vmi_bill`, P4 `vmi_allow` fall-through) |

## closing_checklist (revision_8)

Written after both r8 freezes and the reveal. The revision_8 charter section was written before the reveal and not edited after. The worklog's round-8 notes (read after the reveal) describe the same aggregates. They do not test the tiers pairwise.

- r7 REDs: F-C6b, F-C21, F-C22 closed. Regressions: none in scored values (128.08 / 2,550.42 / 191,236.72 / 149,087.00 approved_reduced) or sensitivities. New: F-C23 (rebuilt holding factors). Task 1 seed addition is producible.
- Tasks: both RED SOURCE-FACTOR, through F-C23 alone; chain, policy and task relationships PASS.
- Gates cited from `r8/gates.txt` (seven OK), not re-run.
- Remaining members, all classes in one place:
  - XF11 / unreal ladder: P2 `vendpoint_month_end_billing` (tiers 1–3 one expression); P2 `stocksmart_month_end_billing` (tiers 1–3 one sum); P4 `stocksmart_program_allowance` (fall-through = tier 2 at zero).
  - XF1, XF2, XF3, XF9, XF10, XF12: no member in P1–P4.

VERDICT revision_8: task0=RED SOURCE-FACTOR task1=RED SOURCE-FACTOR charter=F-C23

## revision_9

## charter_global_frozen (revision_9)

- Entry: worklog tail `REWORK round 9: gates 7/7 green` (only that line read); `/tmp/erl0068_coord/snapshot.sh d1_credit_account_billing_and_credits 9` executed (not read) → `r9/gates.txt` seven OK. Hashes: `credit.extended.yaml` c4ddf7ca9afeaf35cfa32a981e0fc16f58629392d093ea17e305e8231a100b89 (changed); `task_tools.py` ab50360b… (unchanged); views task0 eafac132…, task1 e542c816… (both byte-identical to r8). Base verbatim; blueprint unchanged. contamination_disclosure: none.
- Per-policy digests: P1 `fdb12daf3d7c` and P3 `4e9f747c8dd9` = r8 → carried; P2 `1a5df14e9bb1`, P4 `c01582268061` changed → re-derived; tools carried.

### P2 / P4 holding factors (r9) and XF11 pairwise test

- **P2 `stocksmart_month_end_billing` (parameter)** — "a share of the recurring program fees, meaning the monthly minimum and onsite management fees, charged across all the customer's StockSmart programs less than one whole month before today: the whole of them when such fees were charged in each of the months less than one whole month, one whole month and two whole months before today, one half of them when such fees were charged in exactly two of those three months, and one quarter of them otherwise". The tiers select distinct shares (100 / 50 / 25 %) of one base, and the condition (recurrence over three months) is what a desk weighs for a fee charged only in low-spend months. **Member closed.**
- **P2 `vendpoint_month_end_billing` (method)** — four tiers:
  - trend: latest month + rise, when rising over three months;
  - three-month average;
  - latest month carrying usage, for history within two months;
  - nothing, when no usage in three months.

  The three formula tiers are distinct shapes with distinguishing inputs; e.g. rising 100/200/300 gives trend 400 against average 200. The fall-through ("nothing") is distinguished from the others by a cellular fee charged with no usage: they give that fee, the fall-through gives 0. **Member closed.** Rule ↔ compute checked: `vend_has2 > 0 and vend_u2 > 0 and vend_u1 > vend_u2 and vend_u0 > vend_u1`; `vend_usage3 / 3`; `vend_u0 if vend_u0 > 0 else vend_u1`. Realism observation: a cellular machine with no usage in three months still bills its cellular fee, which the fall-through counts as nothing.
- **P4 `stocksmart_program_allowance` (method)** — tier 1 "when program fees were billed across those programs in the last three whole months, the allowance is the program fees billed in that time"; tier 2 "when none was billed in that time but the customer has an active StockSmart program, it is three times the largest monthly minimum fee among the customer's active StockSmart programs"; fall-through "nothing when the customer has no active StockSmart program and no program fee was billed in the last three whole months". The r8 pair (fall-through vs tier 2) is now distinct, since tier 2's input (an active program's tier fee) does not exist on the fall-through's domain. But the fall-through's condition includes "no program fee was billed in the last three whole months", which is exactly the zero input of tier 1's method. Tier 1 (`vmi_fee3`) evaluated on the fall-through's whole domain gives 0 = "nothing", so the fall-through coincides with tier 1 on its reachable domain. This is the same pattern red-lit in r1 (P1 discountable merchandise), r2 (P2 gross-up) and r8 (this factor's tier 2). **F-C23 member remains (moved from tier 2 to tier 1).**
- **P4 `vendpoint_model_allowance` (parameter)** — whole / one half / one quarter of last month's usage at the 3,000 / 500 thresholds; distinct values; ok.

### renderer-class sweeps (XF 1, 2, 3, 9, 10, 11, 12) on all four policies

- XF1: mechanical read-graph clean in P1–P4.
- XF2/XF3: assembly plain and generic; order fixed.
- XF9: "each of the months less than one whole month, one whole month and two whole months before today" ↔ `c1`, `c2 − c1`, `c3 − c2` and `u0`, `u1`, `u2`; month convention stated; empty windows give 0; ties unchanged.
- XF10: stated filters (recurring = minimum + onsite; cellular fees on the machines; active programs' largest minimum fee via per-tier `EXISTS`/`CPARAM`) match compute.
- XF11: P1, P3, P4 tier pairs other than the member above are distinct (P1 allocation, P3 run-rate/blend/average, P2 VendPoint as above). The member is P4 `stocksmart_program_allowance`, fall-through vs tier 1.
- XF12: aggregates only.
- Basis / baseline / overwrite / prerequisite quotes verbatim; RND as stated.

### findings (r9)

| id | status | members remaining |
|---|---|---|
| F-C23 | **open — RED** (XF11) | P4 `stocksmart_program_allowance`: fall-through "nothing" coincides with tier 1 "the program fees billed in that time" on the fall-through's whole domain (no fee billed) |

## closing_checklist (revision_9)

Written after both r9 freezes and the reveal; the revision_9 charter section was written before the reveal and not edited after. The worklog's round-9 notes (read after the reveal) say "pairwise table (six pairs) … in plan.md". They redesign the r8 pair (fall-through vs tier 2). They do not cover the fall-through vs tier 1 pair, whose zero input is written into the fall-through's own condition.

- r8 RED F-C23: P2 `vendpoint_month_end_billing` closed; P2 `stocksmart_month_end_billing` closed; P4 `stocksmart_program_allowance` not closed (the coincidence moved from tier 2 to tier 1). Regressions: none (scored values 128.08 / 2,550.42 / 191,236.72 / 149,087.00 approved_reduced and every sensitivity unchanged).
- Tasks: task0 PASS on all four; task1 RED SOURCE-FACTOR (F-C23) only.
- Gates cited from `r9/gates.txt` (seven OK), not re-run.
- Remaining members, all classes in one place: XF11 → P4 `stocksmart_program_allowance` fall-through ≡ tier 1 at zero fees. XF1, XF2, XF3, XF9, XF10, XF12: no member in P1–P4.

VERDICT revision_9: task0=PASS task1=RED SOURCE-FACTOR charter=F-C23

## revision_10

## charter_global_frozen (revision_10)

- Entry: worklog tail `REWORK round 10: gates 7/7 green` (only that line read); `/tmp/erl0068_coord/snapshot.sh d1_credit_account_billing_and_credits 10` executed (not read) → `r10/gates.txt` seven OK. Hashes: `credit.extended.yaml` ce9862572670ea24ac003ccc28d7023b876e55e1595f4c5dc4f57e077660e30f (changed); `task_tools.py` ab50360b… (unchanged); views task0 eafac132…, task1 e542c816… (byte-identical to r9). Base verbatim; blueprint unchanged. contamination_disclosure: none.
- Per-policy digests: P1 `fdb12daf3d7c`, P2 `1a5df14e9bb1`, P3 `4e9f747c8dd9` = r9 → carried; P4 `42ef3b0828bb` changed (StockSmart allowance only) → re-derived; tools carried.

### P4 `stocksmart_program_allowance` (r10)

- Rule sentence 9: "… when program fees were billed across those programs in the last three whole months, the allowance is the program fees billed in that time; when none was billed in that time but the customer has an active StockSmart program, it is three times the largest monthly minimum fee among the customer's active StockSmart programs; and when none was billed in that time and the customer has no active StockSmart program, it is one month's minimum commitment, the largest monthly minimum fee among the customer's enrolled, paused or terminating StockSmart programs, which is nothing when the customer has none of those." ↔ `vmi_allow: vmi_fee3 if vmi_n3 > 0 else (3 × vmi_minfee if vmi_minfee > 0 else vmi_idlefee)`. `vmi_idlefee` = max of `monthly_minimum_fee_usd` over the per-tier `CPARAM`s for status enrolled / paused / terminating (18 reads, all six tiers × three statuses). Every StockSmart tier's minimum fee is above 0, so `vmi_minfee > 0` ⇔ "has an active program".
- Sweeps on P4 (XF 1, 2, 3, 9, 10, 12): basis / baseline / overwrite / prerequisite quotes verbatim; keys equal; no factor binding reads another's; RND only `step_room`; window "last three whole months" = `within_months=3`; stated status filters = compute; aggregates only. Clean.
- **XF11 pairwise:**
  - tier 1 (fee-history sum) vs fall-through: the fall-through's domain still has zero fees, but it now gives the idle program's fee wherever an enrolled, paused or terminating program exists. That is a distinguishing input, so the r9 coincidence is **closed**.
  - tier 1 vs tier 2: history sum vs tariff, distinct.
  - **tier 2 vs fall-through**: "three times the largest monthly minimum fee among the … active … programs" vs "the largest monthly minimum fee among the … enrolled, paused or terminating … programs". Both are k × the largest tier minimum fee over a status-filtered set of programs, with k = 3 vs 1. That is the same formula with a swapped multiplier and a swapped record filter. XF11 names this shape as not a method change ("not a swapped multiplier or window length"), as red-lit in r1 for P3 purchase base (Σ/n vs Σ/12). **F-C23 member remains (now tier 2 vs fall-through).**
- Realism of the new tier: reserving one month's minimum commitment for an enrolled programme that is about to go live, or a terminating one, is a treatment a credit desk can publish. For a paused programme the vmi charter prorates the minimum away for paused days where `pause_minimum_waived` is true, so the reserve over-states (observation).

### findings (r10)

| id | status | members remaining |
|---|---|---|
| F-C23 | **open — RED** (XF11) | P4 `stocksmart_program_allowance`: tier 2 (3 × max active minimum fee) vs fall-through (1 × max idle minimum fee) — swapped multiplier and record filter |

## closing_checklist (revision_10)

Written after the r10 freezes and reveal; the revision_10 charter section was written before the reveal and not edited after. The worklog's round-10 notes, read after the reveal, table a numeric pairwise test: "B vs C 1,200 vs 150 / 0 vs 400". It shows tier 2 and the fall-through give different numbers. It does not address the XF11 clause that a swapped multiplier is not a change of shape, and tier 2 and the fall-through are the same expression (k × largest minimum fee over a status-filtered set) with k = 3 vs 1.

- r9 member (fall-through ≡ tier 1 at zero) closed. Remaining F-C23 member: P4 tier 2 vs fall-through, a swapped multiplier and filter. Regressions: none (128.08 / 2,550.42 / 191,236.72 / 149,087.00 approved_reduced; sensitivities unchanged).
- Tasks: task0 PASS; task1 RED SOURCE-FACTOR (F-C23) only.
- Gates cited from `r10/gates.txt` (seven OK), not re-run.
- Remaining members, all classes in one place: XF11 → P4 `stocksmart_program_allowance` tier 2 / fall-through. XF1, XF2, XF3, XF9, XF10, XF12: no member. Realism observation: the paused-programme reserve against `pause_minimum_waived`.

VERDICT revision_10: task0=PASS task1=RED SOURCE-FACTOR charter=F-C23

## revision_11

## charter_global_frozen (revision_11)

- Entry: worklog tail `REWORK round 11: gates 7/7 green` (only that line read); `/tmp/erl0068_coord/snapshot.sh d1_credit_account_billing_and_credits 11` executed (not read) → `r11/gates.txt` seven OK. Hashes: `credit.extended.yaml` 3e1ad05dd5f438cbd622bca6eabec4e175137e285e5cc77bd65bf8a83a004dbc (changed); `task_tools.py` ab50360b… (unchanged); views task0 eafac132…, task1 e542c816… (byte-identical to r10). Base verbatim; blueprint unchanged. contamination_disclosure: none.
- Per-policy digests: P1 `fdb12daf3d7c`, P2 `1a5df14e9bb1`, P3 `4e9f747c8dd9` = r10 → carried; P4 `5c60131ed177` changed (StockSmart allowance) → re-derived; tools carried.

### P4 `stocksmart_program_allowance` (r11) and XF 1, 2, 3, 9, 10, 12

- Rule sentence 9: tier A "when a program fee is dated two whole months before today, the allowance is the program fees billed across those programs in the last three whole months"; tier B "when none is dated that far back but program fees were billed less than two whole months before today, it is the fees billed in that time plus one month's minimum commitment, the largest monthly minimum fee among the customer's active StockSmart programs"; tier C "when no program fee was billed in the last three whole months, it is the minimum commitment for those three months, three times that largest monthly minimum fee, which is nothing when the customer has no active StockSmart program". ↔ `vmi_allow: vmi_fee3 if vmi_m2 > 0 else (vmi_fee2 + vmi_minfee if vmi_n2 > 0 else 3 × vmi_minfee)` (`vmi_m2` = rows at exactly two whole months; `vmi_n2` = rows within two). Tiers are exhaustive and disjoint.
- Sweeps on P4: quotes verbatim; keys equal; no factor-reads-factor; RND only `step_room`; windows ("dated two whole months", "less than two whole months", "the last three whole months") = compute; aggregates only. XF 1, 2, 3, 9, 10, 12 clean.
- Realism: established billing → billed history; new billing → billed so far plus a month of commitment; no billing → three months of commitment. A credit desk can publish all three.

### shape test on every pair of every method factor (all four policies, at once)

Test applied, stated so it can be re-run: normalise each tier's expression by
- treating every aggregate of one field as the same input whatever its fixed window or record filter;
- ignoring constant multipliers, weights and addends (signs included).

A pair **fails** when the two normalised expressions have the same input kinds and the same operations. In other words, they are fixed-coefficient combinations of the same windowed sums: XF11's "swapped multiplier or window length".

A pair **passes** when one tier uses an input kind or an operation the other lacks. Operations include a floor/max, a conditional selection, a data-selected window (rows dated on the latest date carrying rows) and a tariff parameter.

"Nothing" tiers are judged by the domain-coincidence test (r8/r9): fail only if another tier's formula equals 0 on the nothing-tier's whole domain.

| policy / factor | pair | normalised shapes | result |
|---|---|---|---|
| P1 allocation | T1 vs T3 | MX(0, payment − freight − tax) vs merchandise field | pass |
| | T2 (nothing) vs T1, T3 | T1 = payment − freight − tax ≠ 0 and T3 = merchandise ≠ 0 on T2's domain | pass |
| P2 VendPoint | T1 trend vs **T2 average** | u0 + (u0 − u1) + cell vs (u0 + u1 + u2)/3 + cell. Both are fixed-coefficient combinations of the same monthly usage sums over fixed windows, plus the same cellular sum | **fail** |
| | T1 vs T3, T2 vs T3 | T3 = usage of the latest month carrying usage (conditional selection) + cell | pass |
| | T4 (nothing) vs others | others = cellular fees on T4's domain; a cellular fee with no usage distinguishes | pass |
| P3 purchase base | T1 vs T3 | latest statement (data-selected window) vs Σ12m / 12 | pass |
| | T1 vs T2, T2 vs T3 | T2 = ½ latest statement + ½ Σ12m/12 adds an input kind to each | pass |
| P4 StockSmart allowance | A vs B | Σ fees vs Σ fees + max tariff of active programs | pass |
| | A vs C | Σ fees vs tariff | pass |
| | B vs C | Σ fees + tariff vs tariff. On C's domain B = 1 × tariff vs C = 3 × tariff, differing whenever an active programme exists | pass |

- **F-C23: the P4 member is closed.** The r10 pair (3 × max active vs 1 × max idle) is gone. A, B and C pass pairwise, with a distinguishing input on every domain.
- **F-C23: one remaining member, P2 `vendpoint_month_end_billing` T1 (trend) vs T2 (three-month average).** Under XF11's letter these are the same formula: weighted monthly usage over two vs three fixed months. Disclosure: I accepted this factor in r9 on a value test ("rising 100/200/300 gives trend 400 against average 200"). That is not the structural test XF11 states. The miss is this audit's, not a regression by the rework. P2 therefore carries no `method` factor whose every pair changes shape.
- This list is complete for all four policies' method factors; no other pair fails the stated test.

### findings (r11)

| id | status | members remaining |
|---|---|---|
| F-C23 | **open — RED** (XF11) | P2 `vendpoint_month_end_billing` T1 trend projection vs T2 three-month average (only member) |

## closing_checklist (revision_11)

Written after the r11 freezes and reveal; the revision_11 charter section was written before the reveal and not edited after. The worklog's round-11 notes, read after the reveal, state the same structural criterion ("every pair differs in operation structure … not in a multiplier, window, constant or status filter") and apply it to P4 only.

- r10 RED: F-C23's P4 member closed. Regressions: none (128.08 / 2,550.42 / 191,236.72 / 149,087.00 approved_reduced; all sensitivities unchanged).
- Shape test run once on every pair of every method factor in P1–P4, with the test stated. One remaining member, P2 VendPoint trend vs three-month average, an audit-side late find withdrawn from my r9 PASS.
- Tasks: task0 RED SOURCE-FACTOR (via that P2 member); task1 PASS on all four relationships.
- Gates cited from `r11/gates.txt` (seven OK), not re-run.
- Remaining members, all classes in one place:
  - XF11: P2 `vendpoint_month_end_billing` T1 vs T2 (sole member).
  - XF1, XF2, XF3, XF9, XF10, XF12: no member in P1–P4.

VERDICT revision_11: task0=RED SOURCE-FACTOR task1=PASS charter=F-C23

## revision_12

## charter_global_frozen (revision_12)

- Entry: worklog tail `REWORK round 12: gates 7/7 green` (only that line read); `/tmp/erl0068_coord/snapshot.sh d1_credit_account_billing_and_credits 12` executed (not read) → `r12/gates.txt` seven OK. Hashes: `credit.extended.yaml` 3ca9936cf73f27f61e8d0e4947f4cbb2c97f18d597bea3fb085fde6012202f08 (changed); `task_tools.py` ab50360b… (unchanged); views task0 eafac132…, task1 e542c816… (byte-identical to r11). Base verbatim; blueprint unchanged. contamination_disclosure: none.
- Per-policy digests: P1 `fdb12daf3d7c`, P3 `4e9f747c8dd9`, P4 `5c60131ed177` = r11 → carried (with the r11 all-pairs table for their method factors). P2 `39818efd2626` changed (VendPoint billing only) → re-derived; tools carried.

### P2 `vendpoint_month_end_billing` (r12)

- Changed tier T1 (rule sentence 10): "the larger of the latest month's usage plus its rise over the month before and the largest monthly minimum usage among the customer's active VendPoint machines" (rising usage) ↔ `MX(vend_u0 + (vend_u0 - vend_u1), vend_floor) + vend_cell1`, with `vend_floor` = max of `min_monthly_usage_usd` over the per-model `CPARAM(status='active')` reads. T2 (three-month average), T3 (latest month carrying usage) and T4 (nothing) unchanged.
- Structural rule of r11, every pair of this factor:
  - T1 vs T2: T1 = max(trend, tariff floor), a max operation and a tariff input that T2 (Σ usage / 3) lacks → **pass** (the r11 member is closed).
  - T1 vs T3: max + tariff vs conditional selection → pass.
  - T2 vs T3: average vs selection → pass (as r11).
  - T4 (nothing) vs T1/T2/T3: on T4's domain the others give the cellular fee (T1 also the floor when an active machine exists) → distinguishing input → pass.
- XF 1, 2, 3, 9, 10, 12 on P2:
  - basis / baseline / prerequisite quotes verbatim; keys equal;
  - no factor binding reads another's; RND only `result`;
  - windows ("less than one whole month", "one whole month", "two whole months", "the last three whole months") = compute; stated filters (active machines' model minimum, cellular fee type) = compute;
  - aggregates only; assembly and order unchanged.
  - Clean.
- Realism (observation): flooring a rising machine's projection at its model minimum reserves the minimum even though a month below it bills net usage plus a shortfall fee of 15–20 % of the gap (`vending_evt_fees`). This is a conservative reserve for a ramping machine, consistent with the r1 observation on the same quantity.

### findings (r12)

| id | status |
|---|---|
| F-C23 | **closed** (last member P2 T1 vs T2 now passes the structural rule; all method-factor pairs in P1–P4 pass) |

## closing_checklist (revision_12)

Written after the r12 freezes and reveal; the revision_12 charter section was written before the reveal and not edited after.

- r11 RED F-C23 (last member) closed; every method-factor pair in P1–P4 now passes the r11 structural rule (r11 table for P1, P3, P4; r12 table for P2). Regressions: none. Scored values 128.08 / 2,550.42 / 191,236.72 / 149,087.00 approved_reduced and every sensitivity are unchanged since r4.
- Coverage and scope: {P1, P2} task0, {P3, P4} task1, disjoint and complete. Tools unchanged since r2: uuid8s independent, no docstring ordering words or example values, no body judges a prerequisite.
- Trees: each has one prerequisite on a value_input edge and one owner=user write; the graph is acyclic; both prerequisites are unmet at opening and bear weight.
- Factors: every computation has 4–6 factors, ≥ 2 parameter, ≥ 1 honest method; each task has multi-source and cross-difficulty factors; every factor bears weight against an honest baseline; all-baseline fall-backs 612.50 / 0.00 / 102,402.19 / 150,000.00 ≠ gold. Seeds of other categories are producible under their charters.
- Gates cited from `r12/gates.txt` (seven OK), not re-run.
- Open observations (not RED): truncated StockSmart/VendPoint history before mid-2026; ship-to `open_backorder_value` equals the baseline quantity; payments applied to charges carry `applied_invoice_number`; the floored-trend reserve for a ramping VendPoint machine; P1's window/no-line gates and P4's on-time decline carried as write gates without a compute branch; BLUEPRINT-KNOWN base S5 reading of recorded tier/status.
- Remaining XF members: none in classes 1–13.

VERDICT revision_12: task0=PASS task1=PASS charter=CLEAN

## revision_13

## charter_global_frozen (revision_13)

- Entry: worklog tail `REWORK round 13: gates 7/7 green` (only that line read); `/tmp/erl0068_coord/snapshot.sh d1_credit_account_billing_and_credits 13` executed (not read) → `r13/gates.txt` seven OK. Hashes: `credit.extended.yaml` 96e73223486d52f398523fadf46d37bf27385b494b6cb6aa8ee1bfa773ef14a2 (changed); `task_tools.py` ab50360b… (unchanged); views task0 eafac132…, task1 e542c816… (byte-identical to r12). Base verbatim; blueprint unchanged. contamination_disclosure: none.
- Input added this round: `audits/render_source/d1_credit_account_billing_and_credits/render_r1.md` (renderer source-scan, read in full). Its two findings are treated as REDs of one class (XF 1/2: a plain binding reading a factor-owned intermediate binding; a shared record selection held inside a factor).
  - **R1-1:** P1 `in_scope` (plain) reads `pa_in_force`, owned by `contract_share_of_rate`, so every other P1 factor is gated through the contract factor.
  - **R1-2:** P1 `base_share` (plain) reads `left_open`, `full_rate_disc`, `pay_amt`, `inv_total`, owned by `payment_allocation_to_merchandise`, and "left open" is defined only inside that factor's ladder sentence.
- Per-policy digests: P2 `39818efd2626`, P3 `4e9f747c8dd9`, P4 `5c60131ed177` = r12 → carried; P1 `8101072e5dda` (r12 `fdb12daf3d7c`) changed.

### coverage by earlier revisions (disclosure)

Not covered — an audit miss. From r1 on, my mechanical XF1 sweep tested only factor → other-factor reads. Plain bindings reading factor-owned intermediates were judged acceptable in so many words:
- r3: "`pa_out_of_scope` reads `pa_eff`/`inv_date` — a plain gate, not a factor".
- r5: "`pa_prop`, `pa_prior_unknown`, `ended_prior_unknown` are plain gates".
- r7/r8: `in_scope`, `base_excluded` and `base_share` were read without testing their sources.

XF2's "A record selection several parts share is a plain non-factor binding stated once in the rule … No factor is gated through another factor" covers exactly these. Both R1 findings were present in every revision from r7 (R1-1, R1-2) and, in other forms, from r3.

### diff check (P1) — only ownership and sentence placement changed

- Compute: every one of P1's 32 bindings compared, expression by expression and in order, against the r12 text recorded in this audit (scratch `/tmp/audit_d1_credit_account_billing_and_credits_0068/ref_p1_r12.py`). **No expression differs, no binding added or removed, order unchanged.** Compute digests for P2/P3/P4 also unchanged.
- Ownership: `payment_allocation_to_merchandise` now owns `inv_freight_tax`, `paid_merch` (r12: also `pay_amt`, `inv_total`, `applied_out`, `returned_in`, `left_open`, `full_rate_disc`); `contract_share_of_rate` owns `pa_tier`, `contract_share` (r12: also `inv_date`, `pa_eff`, `pa_end`, `pa_in_force`). The moved bindings are plain. Every plain binding moved has more than one reader: `pay_amt`, `inv_total`, `left_open`, `full_rate_disc` feed `paid_merch` and `base_share`; `pa_in_force` feeds `contract_share` and `in_scope`; `inv_date`/`pa_eff`/`pa_end` feed `pa_in_force`.
- Rule: two plain sentences now stand alone.
  - New sentence 2: "The payment amount is the amount of the payment concerned applied to the invoice concerned, and the invoice total is the total of the invoice concerned."
  - Sentence 11: "What is left open on the invoice is the invoice total less every payment, credit memo, discount line and write-off applied to it, plus every returned payment reversed on it, compared without rounding with the tier's prompt-payment discount percentage of the invoice's merchandise subtotal."
  - The allocation ladder follows as its own sentence 12. Meaning is unchanged; the r12 colon join is split. The `compute_basis` quotes of the moved bindings point at sentences 2, 9 (scope) and 11.

### class sweep (XF 1/2 plain-reads-factor) on all four policies, and XF 1, 2, 3, 9, 10, 11, 12 on P1

- Mechanical over P1–P4:
  - no factor binding reads another factor's binding;
  - **no plain binding reads a factor-owned binding other than a factor's `decides` output**, which plain assembly (`disc_rate`, `tol_used`, `step_used`, `step_room`, `result`) may combine;
  - no plain binding is used by one factor alone, except P3 `avg12`, which is the baseline's own monthly purchase base (`baseline` substitutes `month_base: avg12`), so it is shared with the baseline and correctly plain.
- **R1-1 and R1-2 closed as a class** (no remaining member in P1–P4).
- P1 re-sweep:
  - basis quotes, baseline sentences and overwrite clauses verbatim; keys equal; RND on `base_figure`/`result` as stated;
  - XF3 order unchanged;
  - XF9/XF10/XF12 rest on unchanged expressions;
  - XF11 allocation pairs unchanged (r11 table stands).
  - Clean.

### findings (r13)

| id | status |
|---|---|
| R1-1 (render_r1 finding 1) | closed |
| R1-2 (render_r1 finding 2) | closed |
| class XF 1/2 plain-reads-factor | no remaining member in P1–P4 |

## closing_checklist (revision_13)

Written after the r13 freezes and reveal; the revision_13 charter section was written before the reveal and not edited after.

- render_r1 findings R1-1 and R1-2: closed as a class. They had not been covered by revisions 1–12 (disclosed above).
- Diff: compute expressions unchanged (32/32 in P1; P2–P4 compute digests unchanged). Only binding ownership and sentence placement changed.
- Regressions: none. Scored values 128.08 / 2,550.42 / 191,236.72 / 149,087.00 approved_reduced and all sensitivities are unchanged.
- Step 4 checklist as revision_12, with the plain-reads-factor class added to the swept classes: no remaining member.
- Gates cited from `r13/gates.txt` (seven OK), not re-run.
- Remaining XF members: none in classes 1–13 (XF1/XF2 now include plain-reads-factor-intermediate). The observations listed in revision_12 still stand.

VERDICT revision_13: task0=PASS task1=PASS charter=CLEAN

## revision_14

## charter_global_frozen (revision_14)

- Entry: worklog tail `REWORK round 14: gates 7/7 green` (only that line read); `/tmp/erl0068_coord/snapshot.sh d1_credit_account_billing_and_credits 14` executed (not read) → `r14/gates.txt` seven OK. Hashes: `credit.extended.yaml` 96e73223486d52f398523fadf46d37bf27385b494b6cb6aa8ee1bfa773ef14a2 = r13 ✓; `task_tools.py` ab50360b67d2245646232e2c55422e4f5e2d2e65a588289e31e45c85c03ec2e6 = r13 ✓ → every charter-global section (revision_13 and the sections it carries) is carried forward by reference, grounded on those two unchanged hashes. Views changed: task0 381c0f5e4e862429c64823eafc97a084cfbe7e7c7be3dc27fedd937bbefb2727, task1 d246a88b194d80cd14559184f45e43e0a74bd3759a0ebd24ac82b0350a31e852 (seed-only rework). Base verbatim; blueprint unchanged.
- Seed rules checked against the base charters (`blueprint/products/{order,vending,vmi}.yaml`). The published docs cross-checked for the same figures are:
  - `docs/order/freight_minimum_order_schedule_916d944b.json`;
  - `docs/order/freight_charges_and_order_service_fees_524ec06a.json`;
  - `docs/order/return_authorization_and_credit_terms_c9ddcf36.json`;
  - `docs/vending/minimum_usage_schedule_76c179e0.json`;
  - `docs/vending/program_fee_rules_ffd563a2.json`;
  - `docs/vmi/program_fee_rules_ec6b27c5.json`.

  Figures agree, including the freight schedule's per-level consolidated-daily-shipment flag.
- contamination_disclosure: none. The KB-audit verdict naming SRC-2/3/4 is read only after the freezes.

## closing_checklist (revision_14)

Written after both r14 freezes and the reveal. The KB-audit verdict (`audits/policy_kb/d1_credit_account_billing_and_credits/_verdict.md`) was read after the reveal. Its SRC items are checked against the r14 views:
- **SRC-2 closed** (StockSmart `par_change_fee` 12.00 removed; the August statement reconciles without it).
- **SRC-3 closed** (`order_returns` RMA-1529966 / RMA-1530418 seeded as Corbett-error returns credited in full, timely).
- **SRC-4 closed** (vend rows behind every usage bill; usage bills and cellular fees from installation; StockSmart minimum fees from go-live; order lines and freight fees behind every consolidated statement).

In addition:
- **No longer standing:** two revision_1–13 observations, the truncated StockSmart/VendPoint history and the freight not backed by order fees.
- **Not seed items, unchanged:** SRC-5 and SRC-6 (wording; rendered verbatim). SRC-6 is the BLUEPRINT-KNOWN record reading.

- Charter and tools unchanged (hashes above), so charter-global conclusions carry from revision_13: CLEAN.
- Tasks: both PASS on all four relationships on the r14 worlds. Every added row is producible; no added row lights a state_due obligation or leaves a write due on the call day; the personas still match; trees and every factor bear weight; fall-backs differ from gold.
- **Gold moves (seed-driven, verified):** task0 room payment 2,550.42 → 2,619.61; task1 grant 149,087.00 → 149,075.00. Unchanged: discount 128.08; request 191,236.72.
- Gates cited from `r14/gates.txt` (seven OK), not re-run.

VERDICT revision_14: task0=PASS task1=PASS charter=CLEAN
