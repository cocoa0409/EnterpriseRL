# Runtime-context blind audit — comfort_club_membership_care / task 0

## blind_answer

- Freeze time: 2026-10-05T19:04Z (written to disk before any source-layer or GT material was opened).
- Auditor: independent erl-kb-doc-policy-audit run (not the renderer, not the policy-side auditor).
- Scope: difficulty `comfort_club_membership_care`, product `plan`, task index 0.
- Visible materials used:
  - system background = `background` of `blueprint/blueprint.yaml` (only that key was printed);
  - `frozen_time` / `user_scenario` from `/tmp/erl37/kbviews/comfort_club_membership_care/task_0.runtime.json` (sha256 8b0d91ea…5baf7, matches views.sha256);
  - published plan KB, title/content only, `/tmp/erl37/kbviews/docs_visible/plan/*.json` (64 docs; sorted concatenation of all 7 products sha256 e8cdd6997a624be025c5d73e5a36acfd36a1f07ae43cba307e8324f3f0f86282, recomputed and matching the brief);
  - runtime tool schemas (`dbq.py … list`) and tool-shaped DB calls (`dbq.py comfort_club_membership_care 0 call …`) on a fresh seeded copy at the frozen time; one `kb_search`.
- Explicitly not read: `*.extended.yaml`, `task_tools.py`, `tasks/*/tasks/*.json`, raw `initial_state`, docs hidden meta, render plan, worklogs, `audits/` (incl. `audits/policy_task/`), verification scripts. No recursive grep over `env/`.
- DB side is blind: every record below came from a share/task tool return, never from `initial_state`.

### 1. What the user expresses; simulator mode
Simulator line: "I'd like to cancel my Comfort Club membership today, please, and I'd like to know what, if anything, comes back to me." She gives name + phone 6145551382, then address 1427 Northwest Blvd for identity. Target object: her Comfort Club agreement; timing: today; boundary: cancel, "not asking for anything to be moved or kept"; authorisation: "Whatever the representative needs to record on the account on Harbison's side to settle the cancellation, you tell them to go ahead." The cancellation confirmation is a user-owned tool the agent hands over; she runs it "with the reference numbers and the credit exactly as the representative gives them". Simulator is passive (conditional disclosures only: reason, payment habit, recent visits).

### 2. Act now / wait / refuse — grounds
Act now (with an agent-side write first). Grounds:
- `verify_customer_identity` with phone + street address -> "Identity verified".
- `find_plan_agreements`: Comfort Club Platinum Plus, status `active`, annual, term 2026-09-20 to 2027-09-19, consecutive_terms 11, enrolled 2016-09-20, dues_balance 565.20, repair_coverage_remaining 1500.00.
- `find_plan_change_requests`: one `cancellation` request, `pending_customer_confirmation`, created 2026-10-02T15:12:40.
- KB "Comfort Club Cancellation and Refund Terms" cl.1-2: "the agent records a cancellation request that the member confirms themselves… takes effect on the date of confirmation". A pending request already exists, so the member confirms it.
- Still active, not past due: renewal dues 565.20 posted 2026-09-20; "Dues Ledger" doc: past due only when unpaid "for **more than** the tier's payment grace days" (15), day 1 = day after posting -> 2026-10-05 is day 15, not past due.
- Notice date 2026-10-02 = day 12 from term start (day 0) -> inside the 30-day full-refund window ("Cancellation Schedule": Platinum Plus window 30, fee 0.00).

### 3. Narrowest objects and correlation keys
- agreement 5e13add3-69a7-4829-b24e-9fdd62ab6de3; request 59b44c30-6481-486f-b4c8-f9a3aefeca99.
- current term's dues charge: 0e8e75d3-8c33-4b75-862e-7b3f3b244f99 (renewal_dues 565.20, posted 2026-09-20). Excluded: additional_system_dues 156.92 posted 2026-02-17 (previous term; 7 whole months back, not "fewer than … 0 + 1").
- Service calls: 98b91f92-a2ea-4f6e-b2f9-6189c268ffef (Weekend Service Call, no_cool, booked 2026-09-26T07:52, completed 2026-09-26, equipment 9197d081 central AC — an enrolled system: it carries visit grants on the agreement); lines posted 2026-09-26, i.e. after term start 2026-09-20, and no covered-repair draw entry exists for it in `find_plan_service_entries`. Excluded: 30b8fba4 (Standard call 2026-09-03, before the current term began, and its lines are thermostat replacement — never covered).
- Lowest-positioned covered repair line on 98b91f92: line_seq 3 repair_parts txv_replace 196.00, line 6ceefbad-3bdd-4902-bc35-99c808b91a26 (line_seq 2 is an after-hours premium, not a repair line).

### 4. Scored parameters
**A. Covered-repair draw on call 98b91f92** (computation doc "Worksheet: Covered Amount and Draw for a Comfort Club Repair Call" + factor docs):
- Covered lines: repair parts 196.00 (txv_replace) + repair labor 861.25 (txv_replace); refrigerant 356.00 with member refrigerant allowance 178.00 posted; no protection contract coverage posted on the call; tier member repair discount 20% ("Service Call Member Benefits": Platinum Plus 20%).
- Labor valuation — factor "Labor Valuation on Evening, Weekend, Overnight and Holiday Calls": call class `Weekend Service Call` -> labor ÷ 1.25 = 689.00 (found from the ticket's `variant_name`).
- Discounted repair amount: (196.00 + 689.00) × (1 − 20%) = 708.00.
- Maintained repair amount — factor "Maintenance Kept and the Comfort Club Maintained Repair Amount": completed cooling/heating tune-ups dated within 12 months before 2026-10-05: only cooling 2026-05-14 (2025-05-21 is older; 2026-09-28 is whole_home and does not count) -> exactly one -> 708.00 − 109.00 = 599.00.
- Refrigerant — factor "Refrigerant Coverage on Sealed-System Repairs": TXV replacement is a listed sealed-system task; consecutive_terms 11 ≥ 10 -> rate 1.0; (356.00 − 178.00) × 1.0 = 178.00 -> 777.00.
- Protection coverage on call: none -> 777.00.
- Deductible — factor "Covered-Repair Deductible for Protection Contract Holders": `find_warranty_contracts` shows an active Harbison 2-Year Workmanship Warranty (another tier) -> 25.00 -> 752.00.
- Per-call cap — factor "Per-Call Covered-Repair Cap for Long-Standing Members": count 11 ≥ 10 and no covered-repair draw dated within 24 months (service entries show only grants and a full 1500.00 term-expiry for 2025-09-20 term) -> 750.00 + 250.00 = 1000.00.
- Draw = lowest of 752.00, 1000.00, 1500.00 remaining = **752.00**.
- Eligibility: tier carries covered repairs (1500.00/750.00/30-day waiting); agreement active; call on enrolled system; lines posted fewer than one whole month before; waiting period runs from the agreement's *first* covered-repair grant (earliest visible: 2025-09-20) — "a later renewal grant does not restart it" — so the 2026-09-20 renewal grant six days before the booking does not block.

**B. Cancellation credit** (computation doc "Comfort Club Cancellation Credit Worksheet" + factors), evaluated after the draw is on the agreement:
- Whole months elapsed since term began (2026-09-20 -> 2026-10-05): 0; window = fewer than 1 whole month back. Term dues billed = 565.20.
- Refundable dues — factor "Comfort Club Refundable Dues and the Date of Notice": notice = request received 2026-10-02 = day 12 -> within 30-day window -> term dues billed in full = 565.20 (baseline would be 565.20 × 11/12 = 518.10).
- Visit chargeback: current-term completed visits = 1 whole-home (2026-09-28) × 139.00 = 139.00; factor "Visit Chargeback Rate for Long-Tenure Comfort Club Members": enrolled 2016-09-20 -> 120 whole months; completed tune-up + whole-home visits on record = 10 -> 0.6 -> 83.40.
- Coverage chargeback: drawn in current term 752.00; factor "Coverage Chargeback Rate and Covered-Repair History": count 11 ≥ 10, no draw within 24 months outside the current term -> 0.25 -> 188.00.
- Install credit recapture — factor "Installation Credit Recapture When a Comfort Club Agreement Is Cancelled": `find_install_ledger` member_install_credit 500.00 posted 2026-02-10 = 7 whole months back -> 0.25 -> 125.00.
- Discount recapture — factor "Member Repair Discount Recapture on Comfort Club Cancellation": member_repair_discount lines posted in the current-term window (fewer than 1 whole month back): 39.20 + 172.25 = 211.45 (the 2026-09-03 discounts are one whole month back, excluded) -> ≥100 and <250 -> 0.4 -> 84.58.
- Credit = 565.20 − 83.40 − 188.00 − 125.00 − 84.58 = **84.22** (not below zero).
- Cancellation fee: notice inside window, and tier fee 0.00 -> **0.00**.
- Resulting dues balance after confirmation: 565.20 − 84.22 = 480.98 still owed (no payout; she "will watch for the statement").

Fall-back numbers (computation documents only, no factor): draw = min(1057.25 × 0.8 − 50.00 = 795.80, 750.00, 1500.00) = 750.00; credit = 518.10 − 139.00 − 750.00 − 0 − 0 -> floored 0.00. Both definite and different from 752.00 / 84.22. Every factor was reached from record words (ticket class "Weekend Service Call", task code `txv_replace`, contract variant "Harbison 2-Year Workmanship Warranty", consecutive_terms 11, enrolled_date, install-ledger `member_install_credit`, service-line `member_repair_discount`, change-request `created_at`), not from the computation documents' wording — the computation docs state baseline constants ("valued as billed (one times…)", "standard deductible of 50.00", "rate is zero", "rate is one") without signalling variations. Observation for 3b: "standard deductible" / "The plan covers the call's covered amount, not simply what remains of the lines" — judged after reveal.

### 5. Executable sequence, owners, terminal state
1. `find_customers` (agent) -> `verify_customer_identity` (agent; phone + address).
2. Look-ups: `find_plan_agreements`, `find_plan_change_requests`, `find_plan_billing_entries`, `find_plan_service_entries`, `find_service_tickets`, `find_service_lines`, `find_warranty_contracts`, `find_install_ledger` (agent).
3. `post_covered_repair_draw_a854dec6` (agent): agreement 5e13add3…, ticket 98b91f92…, source_line 6ceefbad…, draw 752.00 -> replay: status posted, remaining 748.00.
4. Quote credit 84.22 / fee 0.00 and hand over `confirm_agreement_cancellation_08dfa488` (owner user): agreement 5e13add3…, plan_request 59b44c30…, source_entry 0e8e75d3…, proration_credit 84.22, cancellation_fee 0.00 -> replay: status cancelled, cancelled_date 2026-10-05, dues_balance 480.98.
Terminal: agreement cancelled, draw on record, credit posted, 480.98 owed.

### 6. Problem tree derived from the visible materials alone
Problems: P1 = member's cancellation (root, user-owned confirm); P2 = covered-repair draw on call 98b91f92 (agent write).
Direction / order: P1 waits on P2; handle P2 then P1.
- Hop P1 <- P2 (**state-derived**): blocked-side sentence in "Comfort Club Agreement Cancellation by the Member": "The cancellation credit is fixed only after every completed service call on an enrolled system with repair lines posted since the current term began carries its covered-repair draw on the agreement." Records: ticket 98b91f92 completed 2026-09-26 on enrolled unit 9197d081, repair lines posted 2026-09-26 ≥ term start 2026-09-20; `find_plan_service_entries` has no draw for it -> state unmet. Searching "covered-repair draw" (`kb_search` top hit) finds "Comfort Club Covered-Repair Draws on Completed Service Calls": "a covered-repair draw settles a completed service call … The draw is posted as one draw for the call … recorded in the current term" — the write that makes the call "carry its covered-repair draw". The sentence names neither the tool nor the action; the reader derives it.
- P2 has no prerequisite sentence of its own in the visible draw documents; its eligibility (active, waiting period, month window) holds.

Counter-proof "do only what she asked": confirming now would cancel with no draw on the call; the visible rule says the credit is not fixed while such a call lacks its draw, and confirmation closes the benefit ("visits and covered-repair benefit still available in the term are removed as closed") while a draw is "posted only … while the agreement is active" — so the draw could never follow, and the quoted credit (272.22 without coverage chargeback) would be a non-fixed credit. Excluded by visible principles.
Closest alternatives excluded: renewal grant as waiting-period anchor (excluded by "a later renewal grant does not restart it"); pro-rated refund 518.10 (excluded by notice day 12 ≤ 30); including the 156.92 additional-system charge (excluded by the posting-window rule); including the 2026-09-03 discounts (one whole month back); base cap 750.00 (raised by tenure rule); labor at billed 861.25 (Weekend class).
Soft point (not a blocker): the visible surface does not state whether the first-ever coverage grant may predate the earliest returned grant; either way the waiting period is met.

## gt_comparison
- Reveal time: 2026-10-05T19:06Z, after the blind answer was frozen (blind-version sha256 of this file: 5191a26174275f27b6446390b6d7f54bad492925b997af5aee63cbc005189ac2, recorded 2026-10-05T19:05:30Z; the blind_answer text above is unchanged since).
- Source read: `tasks/comfort_club_membership_care/plan.extended.yaml` (base + `plan_ext_covered_repair_draw`, `plan_ext_cancellation_settlement`, overwrites), `task_tools.py` (owners/decorators), `tasks/0.json` (evaluation_criteria, computations, prerequisite_closure, charter_scope).
- contamination_disclosure: none. No source-layer or GT material was opened before the freeze; the brief carried no scored value.

| Item | Blind answer | Source / GT | Same? |
|---|---|---|---|
| Target, authorisation, owner of confirmation | member confirms own pending request; agent writes draw | trigger on_request; confirm tool owner=user; draw tool owner=agent | same |
| Act / wait / refuse | act now (draw, then member confirms) | GT writes draw then user confirm | same |
| Objects | agreement 5e13add3…, request 59b44c30…, dues charge 0e8e75d3…, ticket 98b91f92…, line 6ceefbad… | identical arguments in evaluation_criteria | same |
| draw_amount | 752.00 (fall-back 750.00) | expected 752.0, baseline_result 750.0; factor trace labor ÷1.25, maintained −109, cap +250, refrigerant 1.0, deductible 25 | same, every factor tier identical |
| proration_credit | 84.22 (fall-back 0.00) | expected 84.22, baseline 0; notice day 12 full, visit 0.6 -> 83.40, coverage 0.25 -> 188.00, install 0.25 -> 125.00, discount 0.4 -> 84.58 | same |
| cancellation_fee | 0.00 | 0.0 | same |
| Problem tree | P1 cancellation <- P2 draw, state-derived | one edge, form `state`, policy_source = the quoted sentence verbatim, resolution_order draw -> cancellation | same; hop mark consistent with declared form |
| "do only the asked thing" | excluded; would give 272.22 | edge_load_bearing: skipping gives 272.22 | same |

Tool schemas, owners and executable effects agree with the source (replayed: draw posted, remaining 748.00; confirmation cancelled, balance 480.98). No conclusion needed hidden compute, raw initial_state or GT.

**Verdict: PASS** (no KB-RUNTIME RED).
