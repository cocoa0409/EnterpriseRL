# Runtime-context blind audit — personal_services_packages / task 0

## revision_1

## blind_answer

### Freeze declaration and scope

- Auditor: erl-kb-doc-policy-audit sub-agent (independent of the render and policy-audit agents), round 1.
- Written: 2026-10-05 (UTC ~10:58), before any source-layer material was opened.
- Scope: difficulty `personal_services_packages`, product `services`, task index 0.
- Runtime view used: `audits/_views/runtime/personal_services_packages/task_0.runtime.json` (sha256 `bbb869613babea798ca98180a680a90feeb439779375150411d52f35b47a9785`, re-hashed and matching MANIFEST); DB access `audits/_access/db_query.py` (sha256 `96c004f6a2c6561216f70c7f914cdf2c403e974524c96f040519f169b8aa6c50`, matching).
- Visible materials read: frozen_time `2026-10-05 10:20:00 CDT`; the agent system prompt incl. company background; the user_scenario script; agent/user tool schemas; title/content of all 49 docs in `docs/services/` (meta never printed); KB_search / grep returns (which also surface other products' docs, read only as search returns, not as criteria); share read-tool returns through db_query.py.
- Explicitly not read: `*.extended.yaml`, `task_tools.py`, `tasks/*/tasks/*.json`, worklogs, `audits/policy_task/`, `audits/_views/policy_task/`, doc meta, blueprint products yaml, any GT / verification script, any other scenario.
- DB side: blind (tool-shaped calls through Engine.call only; raw initial_state never opened).

### contamination_disclosure

None of scored content. To learn the CLI, the first ~30 lines of `db_query.py` were printed: its docstring plus code that opens `tasks/<difficulty>/tasks/<idx>.json`; no task-JSON content was displayed. The brief contained no scored value. Blind audit treated as clean.

### Item 1 — what the user expresses; simulator mode

- Target: the resident's personal services package (simulator: "put her personal services package on hold starting as soon as Larkspur allows, and for as long as her package allows"). Timing: earliest allowed. Boundary: longest allowed hold, no months in mind ("you will take whatever the longest hold is"). Authorisation: caller is Karen Whitfield-Ames, "durable power of attorney"; she "expect[s] to sign the hold yourself as her agent if the desk sends it to you".
- The simulator is passive: gives identifiers only when asked (DOB 1937-11-03, SSN4 8724, phones), answers "yes, well over that" to the two-week absence question, "sometime in the spring" on return, agrees "please go ahead" if something "has to be corrected or credited before the hold can be worked out", and executes the handed-over tool with exactly the values given. It never names a charge or visit ("you never name any charge or visit on her account").

### Item 2 — act / wait / refuse at the frozen moment, and eligibility grounds

Act now (one desk correction, then hand the suspension over for signing). Visible grounds:
- Profile `find_customers`: `representative_name 'Karen Whitfield-Ames'`, `representative_authority 'durable_poa'`. Suspension tool doc: "the customer themselves — the resident or the resident's financial agent — runs it".
- Plan `find_services_plans`: `variant_name 'Personal Services Companion Package'`, `status 'active'`, `residence_category 'assisted'`, last suspension `suspension_start_date '2026-03-01'`, `suspension_end_date '2026-04-30'`.
- Grounds (package_suspension_terms term 1): "away from the community for at least the tier's minimum absence days, for a hospital, rehabilitation or extended family stay" — AL residency `status 'on_leave'`, `absence_start_date '2026-09-24'`, `absence_reason 'rehab_facility'`; simulator confirms well over two weeks; minimum absence 14 days (suspension_allowance table).
- Notice (term 2/3, 7 calendar days): a request today for November is in time.
- Pay-As-You-Go has nothing to suspend — not this plan.

### Item 3 — narrowest objects and correlation keys

- Customer `7fa85340-bdaa-4db8-8d81-ce0b4145edf5`; plan `df70605f-04c3-4f42-9b1d-889d1b3aeb30`; AL residency `3080556d-…` (admission_source `larkspur_independent`); closed IL residency `91a77fcc-…` (`move_in_date '2019-09-03'`); EFA `147cb91a-…` `variant_name 'LifeChoice 50% Refundable Plan'`, `status 'occupied'`.
- Hourly charges on the plan (`event_type services_hourly_charge`):
  - `6b6ff846-…` 44.00, 1.0 h, 2026-07-29, SO-2607-0677 — already carries `services_credit` `5ff3de24-…` 44.00 `credit_reason 'service_dispute'` `source_entry_id 6b6ff846-…` (posted 2026-08-03). Excluded (already credited for that reason; disputes doc clause 5).
  - `0cf232c7-66ac-4b99-98ba-3eb66cdc9088` 88.00, 2.0 h, posted 2026-09-21, billing 2026-09, SO-2609-0389. The order: companion_visit booked 2.0 h on Saturday 2026-09-19, `actual_minutes 70`; the order also drew 0.5 h (`4bf2aa6c-…`). Billed 2.5 h for 70 delivered minutes, no credit references it, 14 days after posting (within the 60-day window). This is the single object of the prerequisite.
- Other rows considered and excluded: SO-2609-0241 double draw (second draw already restored, `759e9bed-…`); SO-2609-0436 resident cancellation received 2026-09-24 for a 2026-09-26 visit (2 calendar days → "owes no hours and is not posted"; not an hourly charge, irrelevant to the suspension's prerequisite); a la carte transport 74.10 (24 mi × 3.25 = 78.00 less 5% = 74.10, correct).

### Item 4 — scored parameters

**(a) Correction credit on `0cf232c7-…`** (overbilled_visit_charge_corrections + visit_charge_re_rating and the factor documents reached from the records):
- Billed minutes (billed_time_for_short_and_long_visits): delivered 70 < booked 120 → "rounded down to a whole number of 15-minute increments" → 60 min = 1.00 h; companion visit minimum 1.0 h (visit_time_measurement) not binding.
- Date surcharge (re_rated_visit_date_surcharges): 2026-09-19 is a Saturday, not on the 2026 holiday list → Companion weekend 25% → ×1.25. Reached from the order's `scheduled_date`.
- Illness relief (illness_relief_on_shortened_visits): ended short (70 < 120); AL residency `absence_reason 'rehab_facility'`, `absence_start_date '2026-09-24'` = 5 days after the visit → "more than 3 and no more than 7" → ×0.8. Reached from the AL residency record (another product's record).
- Billable hours: 1.00 × 1.25 × 0.8 = 1.00 (rounded only after the multiplications).
- Hours covering (hours_covering_a_re_rated_visit): billing month 2026-09 has month-end expiry `e397f9df-…` 0.25 h (`expiry_basis 'month_end'`) → drew 0.5 + expired 0.25 = 0.75 (the 0.25 restore in September is not added because an expiry exists). Reached from the ledger's expiry row.
- Rate (life_plan_hourly_rate_for_re_rated_visits): occupied EFA; "LifeChoice … on a fee-for-service basis" (company background in the system prompt) → Companion fee-for-service rate 42.00. Reached from the EFA record (another product).
- Re-rated charge: (1.00 − 0.75) = 0.25 h × 42.00 = 10.50.
- Goodwill (goodwill_on_repeat_service_disputes): service dispute credits in the 12-month look-back before 2026-10-05: exactly one (`5ff3de24-…`, 2026-08-03) → 10.00.
- Credit: 88.00 − 10.50 + 10.00 = 87.50, within the 88.00 cap → **87.50 USD**, `credit_reason service_dispute`, `billing_period 2026-09`, `source_entry_id 0cf232c7-66ac-4b99-98ba-3eb66cdc9088`.
- Fall-back (computation document alone, package figures it names: increment 15, companion minimum 1.0, Companion rate 44.00): 70 → 75 min = 1.25 h; covering 0.5; (0.75 × 44.00) = 33.00; credit 88.00 − 33.00 = **55.00** — definite and different.

**(b) Suspension** (suspension_length_calculation + factor documents):
- First month: request 2026-10-05; 1 November is 27 days later (≥ 7) → `first_suspended_month 2026-11-01`.
- Baseline months: Companion maximum 2 per rolling 12 (suspension_allowance table) less months counted for the most recent suspension (Mar–Apr 2026, 2 months; whole months 2026-04-30 → 2026-10-05 = 5; 12 − 5 = 7; min(2, 7) = 2) → 2 − 2 = 0. Fall-back answer = **0 months**.
- Hospital/rehab (hospital_and_rehabilitation_absence_months): AL residency `status 'on_leave'`, `absence_reason 'rehab_facility'` → +2.
- Time in force (counting_time_in_force + long_standing_plan_months): AL `admission_source 'larkspur_independent'` and IL `move_in_date '2019-09-03'` on record → whole months 2019-09-03 → 2026-10-05 = 85 → "48 or more" → +2 (the plan-effective count would be 31 → +1).
- Account standing (account_standing_and_suspension_length), read after the correction: charges 4 × 359.00 + 44.00 + 88.00 + 74.10 = 1642.10; payments 3 × 359.00 + credits 44.00 + 87.50 = 1208.50; balance 433.60; less the 2026-10-01 package fee 359.00 → past due 74.60 → "above zero but below 100.00" → −1. (Before the correction: 521.10 − 359.00 = 162.10 → −2.)
- Months: 0 + 2 + 2 − 1 = **3**; suspension 2026-11-01 to 2027-01-31.

### Item 5 — tool sequence, owners, terminal state

1. agent `find_customers` (name "Eleanor Whitfield") → agent `verify_customer_identity` (customer_id, DOB 1937-11-03, SSN4 8724, phone 4695550142 as stated).
2. agent reads: `find_services_plans`, `find_services_ledger`, `find_services_orders`, `find_assisted_residencies`, `find_independent_residencies`, `find_entrance_agreements`.
3. agent `unlock_agent_discoverable_tool("post_services_visit_credit_5ef485c2")` → `call_agent_discoverable_tool` with `{"services_plan_id":"df70605f-04c3-4f42-9b1d-889d1b3aeb30","source_entry_id":"0cf232c7-66ac-4b99-98ba-3eb66cdc9088","credit_reason":"service_dispute","billing_period":"2026-09","amount":87.50}`.
4. agent `unlock_user_discoverable_tool("sign_services_suspension_89d6021d")`; user (Karen, durable POA) `call_user_discoverable_tool` with `{"services_plan_id":"df70605f-04c3-4f42-9b1d-889d1b3aeb30","first_suspended_month":"2026-11-01","suspended_months":3}` → `suspension_signed`, start 2026-11-01, end 2027-01-31.
- Backward dependency: step 4's month count depends on step 3's credit (via account standing). Terminal: one service_dispute credit on `0cf232c7-…`, one signed 3-month suspension from November.

### Item 6 — problem tree derived from the visible materials alone

Problems: P1 (root, customer's own write) suspend the package for the longest allowed period; P2 (desk) correct the overbilled hourly charge `0cf232c7-…` with a service dispute credit. Direction P1 waits on P2. Order P2 → P1.

Hop P1 → P2 — **state-derived**:
- Blocked-side sentence (package_suspension_requests, "When the number of months is fixed"): "The number of months a suspension may run is fixed only after every hourly charge on the plan that its visit record shows billed on more time than was delivered carries a service dispute credit referencing it."
- Query returns: the only uncredited hourly charge is `0cf232c7-…` (2.0 h charged + 0.5 h drawn on an order with `actual_minutes 70`) → the state does not hold.
- Search with the sentence's words ("hourly charge … billed more time than delivered … service dispute credit") returns "Hourly Visit Charge Corrections — Personal Services Plan Desk Guidance", which says such a charge "is corrected by the Resident and Family Services desk whenever it is found within the package's dispute window … posted as one service dispute credit referencing that hourly charge" and gives the agent-side tool. The write that brings the state about is found from the depended-on document and the records; nothing on the blocked side names it.
- No further hop: the correction document states no waited-on state of its own.

### Two-way counter-proof

- Closest alternatives excluded: first month October is excluded by "the first calendar month whose first day is at least the package's suspension notice days after the request is signed"; the July hourly charge is excluded by its existing service_dispute credit and "each entry is credited at most once for each credit reason"; the plan-effective time-in-force count (31 → +1) is excluded by counting_time_in_force's first row (admission from a Larkspur IL residency with move-in on record); the September restore is excluded by "the expired hours only; the restored hours are added only where no hours expired"; the package rate 44.00 is excluded by the EFA record + background ("LifeChoice … fee-for-service").
- "Do only what the customer asked": signing a suspension with the months computed from today's ledger (past due 162.10 → −2 → 0+2+2−2 = 2 months) is excluded because the visible rule says the number of months "is fixed only after" every such charge carries the credit; a 2-month suspension would be a number fixed while the state does not hold.
- Fall-back numbers recorded above (credit 55.00; months 0). Every factor document was reached from record words (Saturday `scheduled_date`; `rehab_facility`/`on_leave`; `larkspur_independent` + IL `move_in_date`; `month_end` expiry; EFA `occupied` LifeChoice; earlier `service_dispute` credit; `actual_minutes` < booked; ledger balance) — KB_search with those words returns the factor document in the top results. No computation document hinted that a variation exists.
- Notes for the scan (observations only, not conclusions): long_standing_plan_months says "The months counted toward time in force are, as the standard, the whole months since the plan's effective date" — wording that signals another counting exists (to be checked against the source in Step 3b). The rendering of the LifeChoice/LifeCare contract type rests on the company background, not on a services doc.

### Freeze record

blind_answer frozen at 2026-10-05T10:59:48Z UTC; sha256 of this file up to (excluding) this freeze record: `669f776ac5705011950e829ddf2203d859a213a6066ad64dd80e9c1dddfb92a5`. Source layer not yet opened.

## gt_comparison

Revealed at ~2026-10-05T11:20Z, after the freeze record above: `services.extended.yaml` (extended policies `services_ext_suspension_months`, `services_ext_short_visit_credit`, their base policies), `task_tools.py`, `tasks/0.json` (`evaluation_criteria`, `computations`, `prerequisite_closure`). The blind_answer above is unchanged.

| Item | Blind answer | Source / GT | Same? |
|---|---|---|---|
| Act / wait / refuse | act now: one desk credit, then hand over the suspension | evaluation_criteria: credit (agent) then `sign_services_suspension_89d6021d` (user) | same |
| Object of the prerequisite | hourly charge `0cf232c7-…` (SO-2609-0389, 88.00, 70 of 120 min) | prerequisite_closure `why_false`: "The 2026-09-21 hourly charge of 88.00 … 70 of 120 booked minutes delivered, and no ledger entry references it" | same |
| Credit call | plan `df70605f-…`, source `0cf232c7-…`, `service_dispute`, `2026-09`, 87.50 | `{"services_plan_id":"df70605f-…","source_entry_id":"0cf232c7-…","credit_reason":"service_dispute","billing_period":"2026-09","amount":87.5}` | same |
| Credit factor tiers | billed minutes round-down 60; weekend 25%; illness 0.8; covering 0.75 (expiry); fee-for-service 42.00; goodwill 10.00 | factor_trace: identical tiers; plumbing `RND(1.00 x 1.25 x 0.8,2)=1.00 … 0.25 x 42.00 = 10.50 … 87.50` | same |
| Credit fall-back | 55.00 | `baseline_result: 55.0` | same |
| Suspension call | `2026-11-01`, 3 months | `{"first_suspended_month":"2026-11-01","suspended_months":3}` | same |
| Suspension factor tiers | on leave +2; time in force 85 months (IL move-in) +2; past due 74.60 → −1; counted prior 2 | factor_trace identical; `result = MX(0, 2 + 2 + 2 - 1 - 2) = 3` | same |
| Suspension fall-back | 0 | `baseline_result: 0` | same |
| Problem tree | P1 waits on P2 (state form), order P2 → P1, hop state-derived | prerequisite edge `services_ext_suspension_months → services_ext_short_visit_credit`, `form: state`, `gate: past_due` | same |
| Identity | DOB + SSN4 (+ phone if stated) | verify with DOB + SSN4 | same in substance |

Checks for KB-RUNTIME RED:
- waiting/refusing vs writing: none — the visible KB writes directly, as the source does.
- two equally reasonable formulas/objects/actions: none on this task's path. (A domain-level divergence in how the suspension months floor at zero is recorded in the policy_kb file as KB-BIJECTION RED; this task's branch, max − counted = 0 and total 3, is not affected.)
- explanation needing hidden compute/GT/raw state: none; every value was derived from visible text and tool returns.
- DB vs customer conflict: none (the simulator's "a few extra charges … still unpaid" matches the ledger).
- added calculation/confirmation/step: none found on this path.
- tool schema/owner/effect disagreement: none (`task_tools.py` signatures and docstrings match the two invocation blocks).
- prerequisite carriage: the sentence stands verbatim in the blocked hub; the depended-on hub describes, in the words the sentence uses ("service dispute credit referencing that hourly charge"), the write that produces the state; strength (hard gate, "fixed only after") matches.
- world state written into a document as a fact: none.
- factor findability: every one of the 4 + 6 declared factors was reached from record words; every ladder tier needed was present.

**Verdict: KB-RUNTIME PASS** (task 0, revision 1).

## revision_2

### runtime_answer (round 2 — NOT blind)

- Written 2026-10-05 (UTC ~11:45), after re-reading the re-rendered `docs/services` (49 docs; `long_standing_plan_months_75df9d81.json` gone, `share_of_the_previous_suspension_70f12af8.json` new) and before opening the round-4 `services.extended.yaml` or the new `tasks/0.json`.
- contamination_disclosure: **not blind.** Round 1 revealed the round-3 source, the task-0 GT and `task_tools.py` to this auditor, and the coordinator's brief says that the task-0 scored value changed (the value itself was not given). This derivation uses only the new docs and the same tool-shaped DB returns (runtime view and `db_query.py` hashes unchanged: `bbb86961…`, `96c004f6…`), but it cannot certify that the new docs are sufficient for a reader without prior knowledge.

Re-derived from the new docs:
- Credit on `0cf232c7-66ac-4b99-98ba-3eb66cdc9088`: unchanged derivation (billed minutes 60; Saturday +25%; illness 0.8; covering 0.75; rate 42.00 — the rate document now says outright "fee-for-service contract (any LifeChoice plan)"; goodwill 10.00) → **87.50**, `service_dispute`, `2026-09`. Fall-back 55.00.
- Suspension, computation document `suspension_length_calculation_14825d7c.json`: "one total: the package's maximum … which is the starting allowance and not a ceiling, plus the months added for the plan's time in force, less the months counted for the plan's most recent recorded suspension … never below zero, the floor being applied once to the final number". Fall-back: 2 + 1 (31 whole months since effective 2024-03-01) − 2 (March–April 2026, 5 months ago) = **1**.
- Factors reached from the records:
  - `counting_time_in_force_dded501d.json`: `admission_source 'larkspur_independent'` + IL `move_in_date '2019-09-03'` → 85 whole months → +2 (ladder in the computation document).
  - `hospital_and_rehabilitation_absence_months_e38583b8.json`: on leave, rehab → +2 "to the total months".
  - `account_standing_and_suspension_length_1f654a81.json`: past due after the credit 74.60 → −1 "from the total months".
  - `share_of_the_previous_suspension_70f12af8.json`: the March–April 2026 suspension did not lie within the recorded rehab absence (absence starts 2026-09-24); it ended 5 ≥ 3 whole months ago → 0.5 × 2 = 1 counted.
- Total: 2 + 2 + 2 − 1 − 1 = **4** months from **2026-11-01** (Nov 2026–Feb 2027, end 2027-02-28). Floor not binding.
- Problem tree unchanged: the suspension hub still carries the state-form prerequisite verbatim; the correction hub supplies the write; hop state-derived.

round-2 answer frozen at 11:41:31 UTC; sha256 of file before this line: `991b43dbc0b80142969fcfc91fff89c2a2b40bdee8ef2353ebc440cd73428f4b`.

### gt_comparison (revision 2)

Revealed ~11:50Z after the round-2 freeze line: round-4 `services.extended.yaml` (mtime 11:29), `tasks/0.json` (11:30); `task_tools.py` unchanged (06:54).

| Item | Round-2 answer | GT | Same? |
|---|---|---|---|
| Credit | `0cf232c7-…`, service_dispute, 2026-09, 87.50; fall-back 55.00 | `amount 87.5`; `baseline_result 55.0` | same |
| Suspension | 2026-11-01, 4 months; fall-back 1 | `first_suspended_month 2026-11-01`, `suspended_months 4`; `baseline_result 1`; plumbing `MX(0, 2 + 2 + 2 - 1 - 1) = 4` | same |
| Factor tiers | time in force 85 → +2; on leave → +2; past due 74.60 → −1; earlier suspension 0.5 share → 1 counted | factor_trace identical (`previous_suspension_share … 5 whole months … share 0.5`) | same |
| Problem tree | P1 waits on P2, state form, state-derived | edge unchanged (`form: state`, `gate: past_due`) | same |

KB-RUNTIME checks: none triggered (the floor is now stated once on the total; every factor reached from the records; tool contracts unchanged). Caveat: the round-2 derivation is not blind (see revision_2 disclosure).

**Verdict revision 2: KB-RUNTIME PASS** (not blind).

## revision_3

2026-10-05 (~12:00Z). Source yaml (mtime 11:29), `task_tools.py`, task JSONs (11:30), runtime views (`bbb86961…`, `afc35b64…`) and `db_query.py` (`96c004f6…`) are unchanged since revision 2 (mtimes and hashes re-checked). The round-3 re-render changed only worked examples (rule, ladder and invocation sections are identical to revision 2, per the content comparison recorded in policy_kb revision_3), so none of the inputs to the runtime derivation changed and the revision-2 answer and comparison stand. Not blind (as disclosed in revision 2).

**Verdict revision 3: KB-RUNTIME PASS** (not blind).
