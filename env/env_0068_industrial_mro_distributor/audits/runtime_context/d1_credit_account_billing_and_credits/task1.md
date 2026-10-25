# Runtime-context blind audit — d1_credit_account_billing_and_credits / task 1

## revision_1

## blind_answer

- Freeze declaration: written to disk before any source-layer artifact was opened; not edited after the reveal.
- Freeze time: 2026-10-17T23:3xZ (UTC). Auditor: fresh KB auditor.
- Visible materials: as task 0 (docs/credit 50 docs, listing hash e6336789…; task1.runtime.json sha256 079187c6…, frozen_time 2026-10-15 10:40:00 EDT; blueprint background text; share-tool docstrings; db_query.py on a fresh engine of task 1; cross-product docs vmi/vending fee schedules for seed realism only).
- Forbidden and not opened: same list as task 0. contamination_disclosure: none.

### 1. User expression and simulator role
Gail Brandt (C-163507, ZIP 43062) asks for a higher permanent credit limit, "as much as your account's buying with Corbett supports under Corbett's rules", settled on this call. If told something must be submitted from her side, she submits a permanent request for exactly the limit the representative states. Passive simulator; user executes the handed tool.

### 2. Act / wait / refuse
Act now. Account 40cc721f-a714-447d-aba6-7e663cc93b9c is active (credit_limit_review_terms: reviews taken only on active accounts); Net 45 minimum 3 months since review: last_review_date 2024-06-18 (27 whole months). On-time percentage (invoices due in the 12 months ending 2026-10-15): only INV-1621465 (due 2026-03-17, paid 2026-04-02) late -> 11/12 = 91 (12/13 = 92 if the 2025-10-15 due date is counted); either >= 85. Approved branch.

### 3. Objects
- Net 45 Business: limit 100000.00, ar 63500.00, monthly_consolidated, opened 2011-04-04 (186 whole months).
- Limit reviews: CLR-1310452 referred 2024-05-08 (29 months), CLR-1310877 approved 2024-06-18, CLR-1314209 declined 2025-08-07 (14 whole months). No undecided request.
- Returned payment RTN-1250820 2025-08-20 (13 whole months -> outside 12-month lookback).
- Disputes: DSP-140812 resolved denied 2026-04-17 (5 whole months, counted); DSP-139507 withdrawn (not counted).
- Finance charges: FC-1250930 2025-09-30 (12 whole months, not counted); FC-1260331 2026-03-31 (6, counted) -> one.
- Invoices in the last 12 whole months: 2025-10-31 .. 2026-09-30 (12 invoices, total 491530.50; 2025-09-30 is 12 whole months and excluded); twelve-month average month 40960.875; latest statement (2026-09-30) INV-1623153 63500.00 = 1.55x.
- CPA-16211 Corbett Category Contract active, commitment 75000.00.
- StockSmart VMI-16408 Weekly Service: fees 06-30 400 (3 whole months), 07-31 400 (2), 08-31 400 + par_change_fee 12.00 (1), 09-30 400 (0).
- VendPoint VP-116052 Locker 24 (ethernet): usage 08-31 812.40 (1 whole month), 09-30 750.00 (0).

### 4. Scored parameters
(a) Requested limit = supported limit (permanent_limit_request_submission: "the limit the request names is the limit the account's purchasing supports, worked out under this rule"):
- Monthly purchase base: consolidated billing, latest statement >= 1.5x average -> 63500.00 (monthly_purchase_base_by_buying_pattern) + contracted spend one eighth of 75000/12 = 781.25 (contracted_spend_in_purchase_base) = 64281.25.
- Terms coverage: (45 + 60 days for monthly consolidated)/30 = 3.5 (billing_lag_in_terms_coverage).
- Finance charge share: one charge -> 85% (finance_charge_reduction_of_supported_limit).
- Supported = 64281.25 x 3.5 x 0.85 = **191236.72** (rounded on the final figure).
(b) Decision on the new request (granted_permanent_limit):
- Step percentage used: start three quarters of 50% = 37.5 (one mark: declined decision within 24 whole months; no returned payment in 12) + 5 (account age >= 180) + 10 (last review >= 24 whole months) - 5 (exactly one denied dispute) = 47.5%.
- Step room = 100000.00 x 1.475 = 147500.00, then + StockSmart allowance 1212.00 (a fee dated two whole months before today exists -> fees of the last three whole months: 400 + 400 + 12 + 400) + VendPoint allowance 375.00 (usage <1 whole month 750.00, in 500..2999.99 -> one half) = 149087.00.
- Granted = min(191236.72, 149087.00, ceiling 499999.00) = **149087.00**; increase 49087.00 <= desk 50000.00 -> **approved_reduced**.
- Fall-back of the computation docs alone: supported 40960.875 x 2.5 = 102402.19; step room 150000.00; granted 102402.19 approved. Differs on both scored figures.

### 5. Tool sequence
1. find_customers -> verify_caller_identity(customer_id, account_number C-163507, billing_zip 43062).
2. Reads: find_credit_accounts, find_credit_transactions, find_credit_limit_reviews, find_credit_disputes, find_pricing_agreements, find_vmi_programs/find_vmi_activity, find_vending_machines/find_vending_transactions.
3. unlock_user_discoverable_tool(submit_limit_request_dcbbb504) -> customer runs (credit_account_id 40cc721f…, change_type permanent, requested_limit 191236.72) -> receipt CLR-… pending, dated 2026-10-15.
4. unlock_agent_discoverable_tool(decide_limit_request_85fdd39c) -> call (credit_account_id 40cc721f…, review_reference <the CLR- from the receipt or the review history>, decision approved_reduced, approved_limit 149087.00). Terminal: credit_limit 149087.00, last review 2026-10-15.

### 6. Problem tree
- Root (agent write): permanent limit decision.
- Hop 1 (state-derived): permanent_limit_decision: "A permanent increase is not decided until the account carries a permanent limit request with no decision recorded on it." Records: every request on the account carries a decision entry -> state not met. The write: permanent_limit_request_submission ("It is recorded with its decision marked pending"; customer's own act) found via "permanent limit request". The figure it names comes from supported_limit_figure + factors. No route or tool of the other problem is named on the decision side.
- Hop 2: identity verification (share docstring).
- Order: verify -> compute supported limit -> customer submits -> agent decides from the new request.
- Counter-proof "do only the one thing": deciding immediately is excluded (no undecided request; the granted-limit doc also says nothing is decided when the latest request already carries a decision line); deciding on an old request is excluded the same way.
- Factor findability: every factor doc names the record kind and the official product (StockSmart Vendor-Managed Inventory Program programs' program fees, VendPoint Industrial Vending Program usage, Contract Pricing Agreement commitment, finance charges, dispute resolution entries, decision entries, opened date, last credit review date, billing cycle).
- Observations for later steps: computation docs announce schedules (granted_permanent_limit §3 "Every percentage point a schedule in this rule adds to or takes from the step percentage used …"; supported_limit_figure "Combination. Every amount a schedule in this rule adds …"). Seed: par_change_fee 12.00 (qty 12) on 2026-08-31 with no vmi_bins / par change entries on the program (vmi rules: fee per par change beyond 40 included, 1.00 each on Weekly Service -> implies 52 par change entries that are not seeded); usage bills with no vend rows; usage bills only from 2026-08 although installed 2025-05-12; no order lines at all behind ~35-60k monthly order_shipment invoices.

## gt_comparison
(appended after reveal; see below)

### revision_1 gt_comparison (appended after the reveal; blind_answer above untouched)
- Freeze record: as task 0 (task1.md sha256 at freeze 01c642a5…); reveal 2026-10-17T23:18:46Z; tasks/1.json read after.
- Write actions, gold vs blind:
  - verify_caller_identity(8ed569fd…, C-163507, 43062): SAME.
  - submit_limit_request_dcbbb504(40cc721f…, permanent, 191236.72), user-owned: SAME (gold 191236.72, raw 191236.71875).
  - decide_limit_request_85fdd39c(40cc721f…, CLR-<runtime receipt>, approved_reduced, 149087.00): SAME (gold reference CLR-1052037 is created at runtime by the submit tool and is copied from the receipt/history, as the blind answer planned).
- Factor tiers: purchase base latest statement 63500.00 SAME (12 invoices 2025-10-31..2026-09-30, 491530.50); billing lag 60 days SAME; haircut 85 percent SAME; contracted spend 781.25 SAME; step start three quarters SAME; review age +10 SAME; denied dispute -5 SAME; account age +5 SAME; StockSmart allowance 1212.00 SAME (includes the 12.00 par change fee); VendPoint allowance 375.00 SAME; step room 149087.00; increase 49087.00 within desk 50000.00 SAME.
- Fall-backs: gold baseline_result 102402.19 (request figure) = blind; grant baseline_result 150000.00 (gold computes it on the gold request) vs blind fall-back 102402.19 on the fall-back request; both differ from 149087.00.
- Problem tree: gold root credit_ext_permanent_increase_grant -> credit_ext_permanent_request_figure (state form) = blind tree (hop state-derived). No hop pre-solved.
- Verdict: KB-RUNTIME PASS.


## revision_2 (re-audit after the seed-only rework; revision_1 above is left untouched)

### contamination_disclosure
Round 1 revealed the GT (old gold 149087.00). This is a fresh re-derivation from the docs and from records re-queried through db_query.py; tasks/1.json was opened only after the figures below had been computed.

### Gate and views
Same as task 0: VERDICT revision_14 CLEAN; views, docs, charter and tools unchanged.

### What the seed rework changed
- credit_transactions, credit_accounts, limit reviews, disputes, pricing, ship-to, VMI program and machine rows: unchanged.
- vmi_activity: the 12.00 par_change_fee row dated 2026-08-31 was removed. 19 monthly minimum fees now run from 2025-03 .. 2026-09; find_vmi_bins is still empty.
- Order lines: 0 -> 144 rows (72 booked / 72 shipped, Priority Ship-To). Every order is >= 100.00, so freight is free, matching invoice freight 0.00. For every invoice, merchandise = shipped + 400.00 StockSmart fee + VendPoint usage.
- vending_transactions: 102 vend rows and 17 usage bills, 2025-05 .. 2026-09. Bills equal the vends, per cost center CC-1630. There are no cellular fees (ethernet).

### Fresh working
- **Supported limit:** unchanged inputs (12 invoices 491530.50; latest 63500.00 >= 1.5x; +781.25; coverage 3.5; 85%) -> **191236.72**.
- **Grant:**
  - Step used 37.5 + 10 - 5 + 5 = 47.5% -> 147500.00.
  - StockSmart allowance: fee dated two whole months back (2026-07-31), so the fees of the last three whole months are summed: 400 + 400 + 400 = 1200.00.
  - VendPoint allowance 375.00.
  - Step room **149075.00**. min(191236.72, 149075.00, 499999.00) = 149075.00. The increase of 49075.00 is within the desk limit of 50000.00 -> **approved_reduced 149075.00**.
- **Fall-backs:** 102402.19 / 150000.00.

### gt_comparison (revision_2)
- Gold submit (…, permanent, 191236.72): SAME.
- Gold decide (…, CLR-<receipt>, approved_reduced, 149075.00): SAME.
- Factor sensitivities (stocksmart 147875.00, vendpoint 148700.00, review 139075.00, account age 144075.00) are consistent.
- **KB-RUNTIME PASS.**
- Policy-side note: the StockSmart tier now taken (billed-fee sum 1200.00) equals what the commitment-projection tier would give (3 x 400.00). The tier choice no longer moves the number; the factor still moves it against its baseline.
