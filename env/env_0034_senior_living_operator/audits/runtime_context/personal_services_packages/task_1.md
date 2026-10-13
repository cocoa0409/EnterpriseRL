# Runtime-context blind audit — personal_services_packages / task 1

## revision_1

## blind_answer

### Freeze declaration and scope

- Auditor: erl-kb-doc-policy-audit sub-agent (independent of the render and policy-audit agents), round 1.
- Written: 2026-10-05 (UTC ~11:05), before any source-layer material was opened.
- Scope: difficulty `personal_services_packages`, product `services`, task index 1.
- Runtime view used: `audits/_views/runtime/personal_services_packages/task_1.runtime.json` (sha256 `afc35b645875606d13b9df0b3b739275f9734a1e1467e595b8bf229b35d886ed`, matching MANIFEST); DB access `db_query.py … 1` (sha256 `96c004f6…c6aa50`, matching).
- Visible materials read: frozen_time `2026-10-14 11:05:00 CDT`; system prompt incl. background (identical to task 0 apart from date); user_scenario; tool schemas (identical to task 0); the 49 `docs/services/` documents (title/content); KB_search / grep returns; share read-tool returns.
- Not read: as in task 0 (no extended yaml, task_tools.py, task JSON, worklogs, policy_task audits/views, doc meta, blueprint products yaml, GT, other scenarios).
- DB side: blind (tool-shaped only).

### contamination_disclosure

Same as task 0 (db_query.py code header printed; no task-JSON content seen). Clean.

### Item 1 — what the user expresses; simulator mode

Harold Brennan, the resident himself, wants his Premier package moved "to the package that fits what you actually use", "as soon as the rules allow"; he will not pick a package and will sign. Passive simulator: identifiers on request (DOB 1941-06-22, phone 4695550123; SSN4 9137 only if nothing else will do); confirms Margaret also uses the plan; mentions September away and the paused month; says "go ahead and do whatever the records need" if something must be posted first; signs exactly what is handed over. He never names a visit, missed appointment or cancellation.

### Item 2 — act / wait / refuse

Act now (one desk posting, then hand the package change over). Grounds:
- Plan `af03ebad-416b-44a1-a280-d3bb9e71666f`: `variant_name 'Personal Services Premier Package'`, `status 'active'` (package change terms 7: "only while the plan is active"), `residence_category 'independent'`, `effective_date '2021-01-01'`, `pending_variant_name 'none'`, last suspension 2026-09-01..2026-09-30.
- Move down: minimum commitment 3 months from 2021-01-01 long satisfied.
- Signed 2026-10-14 ≤ 20th → takes effect 2026-11-01 (package_fit_requests / package_change_terms).
- Signer: resident himself.

### Item 3 — objects and correlation keys

- Customer `4e38f1ce-f822-4fb1-b744-8ef42a58e173`; IL residency `0122c22a-…` `Independent Living Two-Bedroom`, `occupancy_type 'double'`, `second_occupant_name 'Margaret Brennan'`, `status 'active'`; EFA `0315ed89-…` `LifeCare Declining Balance Plan`, `status 'occupied'`; no AL residency.
- Review months for a request on 2026-10-14: postings after 2026-07-14 (2026-07-14 itself is 3 whole months → outside).
- Missed orders: SO-2605-1377 no-show 2026-05-20 (outside the review months; has entry `bf90aedb-…`); SO-2608-1080 resident cancellation received 2026-08-20 07:30 for a 2026-08-20 visit (late, has entry `3ebf597f-…` 0.5 h `late_cancellation`, posted 2026-08-21); **SO-2610-1064** errand_shopping, booked 0.75 h for 2026-10-09, `cancellation_type 'no_show'`, **no hours entry** on the ledger. SO-2610-1064 is the single object of the prerequisite.

### Item 4 — scored parameters

**(a) Hours owed for SO-2610-1064** (hours_for_late_cancelled_and_missed_visits, missed_visit_hours_owed and the factor documents):
- Band hours (day_of_cancellation_hour_bands): no-show → Premier no-show hours 1.0.
- Basis (booked_hours_and_laundry_basis): booked 0.75 < band 1.0 → basis 0.75.
- Rebooking (rebooking_after_a_missed_visit): latest booking of errand_shopping is SO-2610-1098 `booked_at '2026-10-12 09:20'` → 3 days after 2026-10-09 → 0.6.
- Pattern (recent_cancellation_record_multiplier): late-cancel/no-show hours entries in the 6 months before today's posting (2026-10-14): 2026-05-20 (4 whole months) and 2026-08-21 (1) → two → 1.2.
- Life Plan reduction (life_plan_reduction_on_missed_visit_hours): occupied EFA, LifeCare (background: "LifeCare … with lifecare benefits") → −0.20 after all multiplications.
- 0.75 × 0.6 × 1.2 = 0.54; − 0.20 = **0.34 h**; hours available 12.5 → `event_type services_hours_draw`, `amount 0.00`, `draw_basis no_show`, `billing_period 2026-10`, `order_reference SO-2610-1064`.
- No surcharge (2026-10-09 is a Friday; missed visits never carry surcharges anyway).
- Fall-back (missed_visit_hours_owed alone + the figure it names, Premier late-cancellation hours 0.5): **0.50 h** — definite and different.

**(b) Fitted package** (required_hours_and_package_fitting + factors), after the posting:
- Hours used (delivered draws/charges posted 2026-07-15..2026-10-14): 2.0 (08-06) + 2.0 (10-03) + 2.0 (10-06) + 2.0 (10-08) + 1.5 (10-13) = 9.5.
- Late-cancel/no-show (late_cancellation_hours_in_measured_use): entries in the review months 0.5 (08-21) + 0.34 (10-14) → two → add all 0.84 → 10.34. (Before the posting: one → 0.25 → 9.75.)
- Divisor (months_counted_in_the_use_average): fees posted in the review months 08-01 and 10-01 (September suspended, no package-change fee) → 2. Average 5.17.
- Trend (recent_month_use_trend): last whole month = postings after 2026-09-14: 2.0 + 2.0 + 2.0 + 1.5 + 0.34 = 7.84 ≥ 5.17 + 2.0 → +2.0.
- Headroom (home_size_and_shared_occupancy_headroom): Two-Bedroom (not Deluxe), double, second occupant named → +1.0.
- Required = 5.17 + 2.0 + 1.0 = 8.17 → lowest IL package with allotment ≥ 8.17 = **Personal Services Comfort Package** (12 h); `pending_change_date 2026-11-01`.
- Without the posting: 9.75/2 = 4.875; last month 7.5 → +2; +1 → 7.875 → 7.88 → Companion (8). The prerequisite carries weight.
- Fall-back (computation document alone): 9.5/3 = 3.17 → **Personal Services Essentials Package** — definite and different.

### Item 5 — tool sequence

1. agent `find_customers` → `verify_customer_identity` (DOB 1941-06-22, phone 4695550123; name as stated).
2. agent reads plan, ledger, orders, IL residency, EFA.
3. agent `unlock_agent_discoverable_tool("post_services_order_hours_8d682fe6")` → call `{"services_plan_id":"af03ebad-416b-44a1-a280-d3bb9e71666f","order_reference":"SO-2610-1064","draw_basis":"no_show","event_type":"services_hours_draw","billing_period":"2026-10","hours":0.34,"amount":0.00}`.
4. agent `unlock_user_discoverable_tool("sign_services_package_change_2a41e92a")`; user calls `{"services_plan_id":"af03ebad-416b-44a1-a280-d3bb9e71666f","target_variant_name":"Personal Services Comfort Package","pending_change_date":"2026-11-01"}` → `change_scheduled`.
- Terminal: one no-show hours draw of 0.34 h on SO-2610-1064 (dated today), and a scheduled change to Comfort from 2026-11-01.

### Item 6 — problem tree from the visible materials alone

Problems: P1 (root, customer's own write) move to the package that fits use; P2 (desk) post the hours owed for no-show order SO-2610-1064. P1 waits on P2; order P2 → P1.

Hop P1 → P2 — **state-derived**:
- Blocked-side sentence (package_fit_requests, "When the package is chosen"): "The package that fits the resident's use is not chosen until every service order recorded in the review months as a late cancellation or a no-show carries its hours entry for that cancellation on the plan's ledger."
- Query returns: SO-2610-1064 `cancellation_type 'no_show'` on 2026-10-09 (inside the review months) and no ledger row with that `order_reference` → state does not hold.
- Search with the sentence's words ("no-show … hours entry … ledger") returns "Posting Hours for Late-Cancelled and Missed Visits on the Personal Services Plan": "Hours owed … for a service order that was cancelled late or missed (a no-show) are posted by the Resident and Family Services desk once the cancellation or no-show is on record … Each posting is one hours entry for that cancellation on the plan's ledger", plus the agent tool. The write is found from the depended-on document and the records.
- No further hop (the posting document states no waited-on state).

### Two-way counter-proof

- Closest alternatives excluded: Companion package is excluded only once the posting and every factor are applied (8 < 8.17); Concierge/Premier are not "lowest"; 1 December is excluded by "signed on or before the … cutoff day" (14 ≤ 20); the late-cancellation band 0.5 (baseline) is excluded for a no-show by the day_of_cancellation table; SO-2610-1071 (booked 10-05) is not the latest errand booking; the 07-03/07-09/07-11 draws are outside the review months by the "same day … 3 months before … is outside" boundary.
- "Do only what the customer asked": fitting without the posting gives Companion (7.88) — excluded because the visible rule says the package "is not chosen until" every recorded no-show in the review months carries its hours entry.
- Fall-backs recorded above (0.50 h; Essentials). Factor documents reached from record words: `no_show` cancellation_type; booked 0.75 h; later errand booking; earlier `no_show`/`late_cancellation` draws; EFA `occupied` LifeCare; IL `double` + `second_occupant_name`; no September package fee; October draws. No computation document hinted that a variation exists.
- Observation for the scan: the visible tool doc says the posting is "dated today"; the trend and use-review factors therefore count the new entry — consistent across documents.

### Freeze record

blind_answer frozen at 2026-10-05T10:59:48Z UTC; sha256 of this file up to (excluding) this freeze record: `ea1b8fd7815620f0dd70d02fef981f47d82d7710b516a1d12211324127eb3958`. Source layer not yet opened.

## gt_comparison

Revealed at ~2026-10-05T11:20Z, after the freeze record above: `services.extended.yaml` (`services_ext_package_fit`, `services_ext_missed_visit_hours`, their base policies), `task_tools.py`, `tasks/1.json`. The blind_answer above is unchanged.

| Item | Blind answer | Source / GT | Same? |
|---|---|---|---|
| Act / wait / refuse | act now: post the no-show hours, then hand over the change | evaluation_criteria: posting (agent) then `sign_services_package_change_2a41e92a` (user) | same |
| Object of the prerequisite | SO-2610-1064 no-show, no hours entry | prerequisite_closure `why_false`: "Order SO-2610-1064 carries a no-show record dated 2026-10-09 … no ledger entry with order_reference SO-2610-1064 exists" | same |
| Posting call | plan `af03ebad-…`, `SO-2610-1064`, `no_show`, `services_hours_draw`, `2026-10`, 0.34, 0.00 | identical arguments (`"hours": 0.34, "amount": 0.0`) | same |
| Hours factor tiers | band 1.0 (no-show); basis 0.75 (booked < band); pattern 1.2 (two entries); rebooking 0.6 (3 days); lifecare −0.20 | factor_trace identical; `RND(MX(0, 0.75 x 1.2 x 0.6 - 0.20), 2) = 0.34` | same |
| Hours fall-back | 0.50 | `baseline_result: 0.5` | same |
| Change call | Comfort Package, `2026-11-01` | `{"target_variant_name":"Personal Services Comfort Package","pending_change_date":"2026-11-01"}` | same |
| Fit factor tiers | divisor 2; late/no-show entries two → 0.84 in full; trend 7.84 vs 5.17 → +2.0; headroom +1.0; required 8.17 | factor_trace identical; `required RND(5.17 + 1.0 + 2.0, 2) = 8.17 … Comfort` | same |
| Fit fall-back | Essentials | `baseline_result: Personal Services Essentials Package` | same |
| Problem tree | P1 waits on P2 (state form), order P2 → P1, hop state-derived | edge `services_ext_package_fit → services_ext_missed_visit_hours`, `form: state`, `gate: late_hours` | same |
| Identity | DOB + phone | verify with DOB + phone | same |

Checks for KB-RUNTIME RED: none triggered — no wait/write disagreement, no competing formula on this path, nothing explained only by hidden material, no DB/customer conflict, no added step, tool contracts match `task_tools.py`, the prerequisite sentence and the depended-on write are both visible at the same strength, no world state written as a fact, and every declared factor (5 + 4) was reached from record words with the needed tiers present.

**Verdict: KB-RUNTIME PASS** (task 1, revision 1).

## revision_2

### runtime_answer (round 2 — NOT blind)

- Written 2026-10-05 (UTC ~11:45), after re-reading the re-rendered docs and before opening the round-4 source or the new `tasks/1.json`. contamination_disclosure: not blind (round-1 reveal of source/GT; see task 0 revision_2).
- Re-derived from the new docs: missed-visit hours for SO-2610-1064 = 0.75 × 1.2 × 0.6 − 0.20 = **0.34** h (`services_hours_draw`, `no_show`, `2026-10`, 0.00); fall-back 0.50. Fit: 9.5 + 0.84 = 10.34 ÷ 2 = 5.17; last whole month 7.84 → +2.0; headroom +1.0; required 8.17 → **Personal Services Comfort Package** from **2026-11-01**; fall-back Essentials. The fitting document and hub now also state "where the required hours exceed every allotment an independent living resident is fitted to the Personal Services Concierge Package" (not triggered). The trend document now defines the last whole month on its own terms; the computation document still does not mention it. Problem tree and prerequisite carriage unchanged; hop state-derived.

round-2 answer frozen at 11:41:31 UTC; sha256 of file before this line: `bcb75faa83280c0bb4d58c65dc133099af67b10414c96b9ddc74afb2c92acec1`.

### gt_comparison (revision 2)

Revealed ~11:50Z after the round-2 freeze line. GT unchanged: posting `{"order_reference":"SO-2610-1064","draw_basis":"no_show","event_type":"services_hours_draw","billing_period":"2026-10","hours":0.34,"amount":0.0}` (baseline 0.5); change `Personal Services Comfort Package` from `2026-11-01` (baseline Essentials). All items same as the round-2 answer; problem tree unchanged (state form, state-derived). No KB-RUNTIME trigger.

**Verdict revision 2: KB-RUNTIME PASS** (not blind).

## revision_3

2026-10-05 (~12:00Z). Source yaml (mtime 11:29), `task_tools.py`, task JSONs (11:30), runtime views (`bbb86961…`, `afc35b64…`) and `db_query.py` (`96c004f6…`) are unchanged since revision 2 (mtimes and hashes re-checked). The round-3 re-render changed only worked examples (rule, ladder and invocation sections are identical to revision 2, per the content comparison recorded in policy_kb revision_3), so none of the inputs to the runtime derivation changed and the revision-2 answer and comparison stand. Not blind (as disclosed in revision 2).

**Verdict revision 3: KB-RUNTIME PASS** (not blind).
