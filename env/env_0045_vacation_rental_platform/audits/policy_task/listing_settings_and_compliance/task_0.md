# Policy-task audit — listing_settings_and_compliance / task 0

## source_derivation_frozen

- Auditor: erl-task-policy-audit (independent Claude agent). Revision 1. Freeze time: 2026-10-07T19:30Z.
- Inputs: masked view `/tmp/erl45_views/r1/listing_settings_and_compliance/task_0.view.json` (sha256 22fb96eadf5fe6cf2d0418000eedb15542733215c88a97f8b3f86a32660fd505: frozen_time, user_scenario, initial_state only), `listing.extended.yaml` (e0068140…), `task_tools.py` (376399fd…), `blueprint/` (listing, protect and host charters, schema, share_tools.py).
- Masked and unread at freeze: the full `tasks/0.json` (evaluation_criteria, computations, solvability_contract, prerequisite_closure, charter_scope, required_documents, design_rationale), both worklogs, other audits.
- contamination_disclosure: none. No search touched `tasks/*.json`; the brief carried no scored value.

### policy_self_consistency (this task only)

- Charter-global conclusions this task rests on are in `audits/policy_task/listing_settings_and_compliance/_difficulty.md`: base copy verbatim and override declarations (§override_declarations), rule/compute equivalence (§rule_compute_equivalence), tool binding and uuids (§action_binding_and_uuids), the prerequisite graph and sentences (§prerequisite_graph, §prerequisite_sentences), factor structure (§factor_ladders), and findings G-1 … G-8.
- Handling time: frozen_time 2026-09-21 10:15 MDT → day of reset/save = 2026-09-21. Pet reset and cleaning reset are each evaluated on the opening world (neither reads a field the other writes, nor any fee-change row). The short-stay ceiling is evaluated after the cleaning reset (it reads `listings.cleaning_fee`) and after the pet reset (gate), and before the host's save.
- Real-world waits: every input is a seeded record (protection_claims statuses/decisions dated ≤ 2026-06-19, the active plan's level, host_account_events Superhost assessment 2026-07-01, listing_events quality rows ≤ 2026-07-01, listings fields) or the synchronous effect of a preceding gold write in the same call. No approval, payment, batch or date advance is needed.
- Bearing of charter-global defects on this world:
  - G-1 (mislabelled method factors): this task's pet and cleaning computations are two of the four affected — demonstrated under factor_weight.
  - G-2: a literal reader of "pet_fee_max_usd … highest pet fee the host may set" would reset to 300.00 and cleaning to 300.00, which are the declared baselines; the extended rule explicitly adds allowances on top, so this is not a second defensible answer here.
  - G-3: not reached (no Pricing Assist in this task).
  - G-4: not reached (latest Superhost assessment counted 73 stays).
  - G-5: bears directly — the pet edge is the tree's state_gate (see problem_chain).

### problem_chain

Root problem: the host asks for the highest short-stay cleaning fee the carriage-house suite may carry and wants to save it herself → listing_ext_short_stay_cleaning_fee ("A host who asks for the highest short-stay cleaning fee the listing may carry has the short-stay ceiling itself saved as the short-stay cleaning fee"; space type Entire Guest Suite: `short_stay_cleaning_fee_allowed: true`, `short_stay_max_nights: 2`).

Prerequisite sentences in the root's own rule and their state at the opening:

| edge | sentence | kind | opening state (DB) | unmet? |
| --- | --- | --- | --- | --- |
| E1 → listing_ext_cleaning_fee_ceiling | "The short-stay ceiling is fixed only after the regular cleaning fee on the listing stands at or below the listing's cleaning-fee ceiling." | value_input (regular_cleaning_fee) | `listings[d230b90b…].cleaning_fee = 420.0`; cleaning-fee ceiling on 2026-09-21 = 397.50 (below) | yes, 420.00 > 397.50 |
| E2 → listing_ext_pet_fee_ceiling | "A short-stay cleaning fee is not added to a listing until the pet fee on that listing stands at or below the listing's pet-fee ceiling." | state_gate | `listings[d230b90b…].pet_fee = 380.0`; pet-fee ceiling on 2026-09-21 = 340.00 (below); `short_stay_cleaning_fee = 0.0` so the save "adds" a short-stay fee | yes, 380.00 > 340.00 |

Neither depended-on policy carries a prerequisite of its own (`prerequisite: []`). Derived tree: root short-stay ← {cleaning reset (value_input), pet reset (state_gate)}; n = 2 prerequisite problems, 1 value_input edge ≥ max(n−1,1) = 1 ✓; acyclic ✓; customer's own write: the root `save_short_stay_cleaning_fee_f18844b5` is `owner="user"` and the persona saves it at hand-over ✓.

- Topological order: {pet reset, cleaning reset} in either order, then the host's save. The two resets touch different fields, neither reads the other's field nor any `listing_fee_change_logged` row (all compute counts filter `event_type='listing_quality_reviewed'` or read protect/host rows), so both orders give one terminal state — no parallel-edge ambiguity.
- Load-bearing runs:
  - E1 skipped: short-stay ceiling = RND(420.00 × 0.866515…) = 363.94 instead of 344.44 → bears weight.
  - E2 skipped: the value is unchanged (gate edge) but the rule forbids adding the fee while 380.00 > 340.00; terminal pet_fee 380.00 vs 340.00 → the gate bears weight as a gate.
- No-wait: both resets are synchronous agent writes on seeded facts.
- Tool layer: none of the three tool bodies reads any other field, computes, or refuses (task_tools.py lines 39–57, 86–104, 136–154) ✓.
- Discoverability: both sentences are in the root rule; "cleaning-fee ceiling" and "pet-fee ceiling" are defined only by the two depended-on rules ✓.
- Customer mentions no prerequisite: persona says "you are not asking about anything else", "you don't bring up any fee yourself"; she reacts passively only if the agent explains something must be brought into line ✓.

### task_independent_derivation

1. Need / authority / timing: Teodora Lindqvist, host, wants a short-stay cleaning fee on "Highlands Carriage-House Suite w/ Patio" set as high as Roamhaven allows, to be told the exact amount and save it herself, now; not the garden room. Identity: phone 7205552417 + ID last4 2583 match `customers[a7e7a7e4…]` (2 matches) → `verify_customer_identity`. Authorisation for support resets: "go ahead and set it the way Roamhaven requires".
2. Act now: short_stay_cleaning_fee_allowed true for Entire Guest Suite; listing status listed; host account active.
3. Object: listing d230b90b-1002-415d-b193-72a01f366175 (the garden room 7f3f62b8… excluded by the persona and by title).
4. Pet-fee ceiling on 2026-09-21 (listing_ext_pet_fee_ceiling):
   - approved pet_damage claims on the listing with MONTHS(filed_at, 2026-09-21) < 12: 0c565b38 (2026-03-14) only → 1 → pet-damage claim allowance 40.00. Excluded: c05f55cf (2025-08-27, 12 whole months → near-miss), 7ae8a578 (2025-02-10), b1494371 (2024-09-20), df94d8f9 (2026-06-02, denied).
   - active plan ea9e596b… = HostCover Standard: pet_damage_sublimit_usd 2500.00 (> 1000, ≤ 2500) → 25.00; deductible_usd 250.00 (≥ 250, < 500) → 15.00.
   - total 80.00. Standing: no quality suspension in 12 months; warning 08acd299 (2026-07-01, MONTHS = 2 < 3) → × 0.50.
   - ceiling = 300.00 + 80.00 × 0.50 = **340.00**; 380.00 > 340.00 → `reset_pet_fee_f8e15273(listing_id=d230b90b…, pet_fee=340.00)`.
5. Cleaning-fee ceiling on 2026-09-21 (listing_ext_cleaning_fee_ceiling):
   - approved deep_cleaning claims < 12 months: 8182b52e (2026-01-19, verified loss 960.00) → 1 claim, loss < 1000 → 45.00. Excluded: 10524741 (2025-09-02, 12 whole months → near-miss; counting it would give 2 claims → 80.00), 260c57bc (2025-04-05).
   - Standard deep_cleaning_sublimit_usd 1000.00 (> 500, ≤ 1000) → 20.00.
   - host account f38df7ac…: Superhost, superhost_since 2023-04-01 → 41 whole months ≥ 24 → 30.00.
   - first_listed_date 2022-03-01 → 54 whole months ≥ 36 → 20.00.
   - most recent quality assessment 08acd299 (2026-07-01) review_count 17 ≥ 15 → 15.00.
   - total 130.00. Assessments < 6 months: 9b9edd43 (2026-04-01, pass), 08acd299 (2026-07-01, warning); 2d16c6fd (2026-01-01, 8 months) excluded → exactly one pass → × 0.75.
   - ceiling = 300.00 + 130.00 × 0.75 = **397.50**; 420.00 > 397.50 → `reset_cleaning_fee_77ae9a3d(listing_id=d230b90b…, cleaning_fee=397.50)`.
6. Short-stay ceiling on 2026-09-21 after both resets (listing_ext_short_stay_cleaning_fee):
   - typical-stay base: most recent host_superhost_assessed c5a75840 (2026-07-01): stays_12m 73 ≥ 10, nights_12m 264 → 0.5 + 0.5 × min(1, 2 × 73 / 264) = 0.5 + 73/264 = 0.776515…
   - damage addition: approved property_damage < 12 months: 5c90d59e (2026-05-08) → 1 → +0.05.
   - pet turnover: approved pet_damage < 24 months: 7ae8a578, c05f55cf, 0c565b38 → 3 → +0.06 (b1494371, 2024-09-20, is 24 whole months → excluded; df94d8f9 denied).
   - deep-cleaning turnover: approved deep_cleaning < 24 months: 260c57bc, 10524741, 8182b52e → 3 → +0.08.
   - guest-rating cut: warnings < 6 months: 08acd299 → 1 → −0.10.
   - share = 0.776515… + 0.19 − 0.10 = 0.866515… (≤ 1).
   - ceiling = RND(397.50 × 0.866515…) = RND(344.43977…) = **344.44**.
   - Opening-world contrast (cleaning not reset): RND(420.00 × 0.866515…) = 363.94.
7. Write sequence: verify identity (agent) → `reset_pet_fee_f8e15273(d230b90b…, 340.00)` and `reset_cleaning_fee_77ae9a3d(d230b90b…, 397.50)` (agent, either order) → agent tells the host 344.44 and hands over → `save_short_stay_cleaning_fee_f18844b5(d230b90b…, 344.44)` (user). Terminal: pet_fee 340.00, cleaning_fee 397.50, short_stay_cleaning_fee 344.44, three `listing_fee_change_logged` rows dated 2026-09-21 (pet_fee 380→340, cleaning_fee 420→397.50, short_stay_cleaning_fee 0→344.44).

**A state_due policy outside the tree is due on the same listing (finding T0-1).** listing_ext_minimum_stay_floor on 2026-09-21 for d230b90b…: party_violation strikes on host account f38df7ac… in 12 months: none → 0; approved property_damage claims < 12 months: 5c90d59e (2026-05-08) → 1 night; approved safety reinstatement: none (no reinstatement rows) → 0; party-prevention nights 1; quality assessments < 12 months: 917ed246 (2025-10-01 pass), 2d16c6fd (2026-01-01 pass), 9b9edd43 (2026-04-01 pass), 08acd299 (2026-07-01 **warning**) → "any … has outcome warning or suspension … doubled" → 2; floor = minimum_nights_floor (Entire Guest Suite) 1 + 2 = **3**. `listings[d230b90b…].minimum_nights = 2` < 3, and the rule reads "a minimum stay standing below the floor is raised to the floor exactly". The other three state_due policies are not due: suite extra-guest fee 20.00 vs ceiling RND(165/2 × (0.75 + (0.08+0.05+0.06) × 1)) = 77.55; garden room fees within their ceilings and its floor 1 = its minimum stay 1.

### factor_weight

Pet computation (handling world = opening world). Gold-candidate 340.00; full baseline (`baseline.rule` alone: "the standard pet-fee ceiling is the space type's pet_fee_max_usd") = **300.00** ≠ 340.00 ✓.

| factor | label honest? | tier taken / evidence | baseline value | scored value under baseline |
| --- | --- | --- | --- | --- |
| pet_damage_claim_allowance | parameter ✓ | "exactly one" — claim 0c565b38 (protect) | 0 | 300 + 40×0.5 = 320.00 ✓ moves |
| pet_sublimit_allowance | parameter ✓ | mid — Standard sublimit 2500 (protect level of plan ea9e596b) | 0 | 300 + 55×0.5 = 327.50 ✓ |
| pet_deductible_allowance | parameter ✓ | mid — Standard deductible 250 | 0 | 300 + 65×0.5 = 332.50 ✓ |
| pet_allowance_guest_standing | **no** — share 0/0.5/1 in one formula (G-1) | warning tier — listing_events 08acd299 | share 1 | 300 + 80 = 380.00 ✓ moves (and equals the current pet fee, so no reset would be due) |

Near-miss: c05f55cf (approved pet_damage filed 2025-08-27, 12 whole months) excluded by "fewer than twelve whole months"; df94d8f9 excluded as denied. No stamp names a tier. Surviving count: 3 parameter, **0 method** (bound ≥ 1) → SOURCE-FACTOR RED (G-1). Multi-source factors in this computation: none.

Cleaning computation. Gold-candidate 397.50; full baseline 300.00 ≠ ✓.

| factor | label honest? | tier / evidence | baseline | scored value under baseline |
| --- | --- | --- | --- | --- |
| deep_cleaning_allowance | parameter ✓ (multi-source) | one claim, loss 960 < 1000 — 8182b52e | 0 | 300 + 85×0.75 = 363.75 ✓ |
| cleaning_sublimit_allowance | parameter ✓ | mid — Standard deep-clean sublimit 1000 | 0 | 300 + 110×0.75 = 382.50 ✓ |
| superhost_cleaning_allowance | parameter ✓ | long — host Superhost since 2023-04-01 (host) | 0 | 300 + 100×0.75 = 375.00 ✓ |
| listing_tenure_allowance | parameter ✓ | long — first_listed 2022-03-01 | 0 | 382.50 ✓ |
| turnover_allowance | parameter ✓ (realism weak, G-8) | high — review_count 17 on 08acd299 | 0 | 300 + 115×0.75 = 386.25 ✓ |
| cleaning_assessment_record | **no** — share 0/0.75/1 (G-1) | one pass in 6 months | share 1 | 430.00 ✓ moves (above 420, so no reset would be due) |

Near-miss: deep_cleaning 10524741 (2025-09-02, 12 whole months) and pass 2d16c6fd (2026-01-01, 8 months) excluded by the windows. Surviving: 5 parameter, **0 method** → SOURCE-FACTOR RED (G-1). Multi-source: deep_cleaning_allowance ✓ (G-7 caveat). Cross-difficulty: protect, host ✓, rows present in the seed ✓.

Short-stay computation (handling world = after both resets). Gold-candidate 344.44; full baseline 397.50 × 0.50 = **198.75** ≠ ✓.

| factor | label honest? | tier / evidence | baseline | scored value under baseline |
| --- | --- | --- | --- | --- |
| typical_stay_base | method ✓ | ≥ 10 stays — host_account_events c5a75840 (73 stays, 264 nights) (host) | 0.5 | 397.50 × 0.59 = 234.53 (half up; 234.525) ✓ |
| damage_addition | parameter ✓ | one — 5c90d59e | 0 | 324.56 ✓ |
| pet_turnover_addition | parameter ✓ | two or more — 3 claims | 0 | 320.59 ✓ |
| deep_cleaning_turnover_addition | parameter ✓ | two or more — 3 claims | 0 | 312.64 ✓ |
| guest_rating_cut | parameter ✓ | one warning — 08acd299 | 0 | 384.19 ✓ |

Near-miss: b1494371 (pet_damage 2024-09-20, 24 whole months) and the earlier Superhost assessment abb73c45 (70 stays / 251 nights → 345.38 if read) excluded by "most recent". Surviving: 4 parameter + 1 method ✓.

Task-level: multi-source ≥ 1 (deep_cleaning_allowance) ✓; cross-difficulty ≥ 1 (protect and host rows seeded) ✓. Task verdict for factors: SOURCE-FACTOR RED through G-1 (pet and cleaning computations).

### findings (frozen, pre-reveal)

- **T0-1 — SOURCE-TASK RED (candidate; to be compared with GT).** Symptom: on the very listing being handled, listing_ext_minimum_stay_floor (state_due) is due — floor 3 against a minimum stay of 2 — and the persona authorises support to bring "something else on the suite … into line". Root cause: the seed puts the suite below its minimum-stay floor (an approved property_damage claim 5c90d59e plus a quality warning 08acd299 doubling 1 night to 2) while the task's tree does not include that policy. Second reading: the agent also calls `raise_minimum_stay_1aeaa300(d230b90b…, 3)`; terminal minimum_nights 3 (plus a minimum_nights change row) versus 2. Compounding real-world conflict: with a 3-night floor the suite cannot take the one- and two-night stays the host is pricing for (short_stay_max_nights 2), so the charter would at once mandate a stay length that makes the requested setting inapplicable. Affected: `initial_state.listings[d230b90b…].minimum_nights`, `protection_claims[5c90d59e…]`, `listing_events[08acd299…]`; user_scenario consent line; listing_ext_minimum_stay_floor.
- **T0-2 — SOURCE-FACTOR RED** via `_difficulty.md` G-1: pet and cleaning computations carry no honest method factor (demonstrated above).
- **T0-3 — observation (realism).** The seeded fee levels sit at the edge of practice: a $420 cleaning fee and a $380 pet fee on a one-bedroom, four-guest suite renting at $165 a night (2.5× and 2.3× the nightly rate). The history supports them inside the charter (pet fee 380 was within its ceiling of 410 on 2025-03-01 by the seeded claims; the HostCover reimbursements reproduce exactly from the protect charter, e.g. 700 − 420 cleaning-fee offset − 250 deductible = 30 on claim 10524741), so the settings are motivated rather than arbitrary, but a real host at this price point would not carry them.
- **T0-4 — observation.** The suite has been listed since 2022-03-01 but quality assessments are seeded only from 2025-07-01; no scored window reaches back that far, and LATEST reads 2026-07-01, so no figure moves.
- **T0-5 — observation (realism, G-5).** The pet-fee gate on the short-stay fee has no business link to it; here it forces a second, unrelated fee reset to be part of answering a short-stay question.

## source_gt_comparison

- Freeze record (correction of the header): the "Freeze time" lines in this file and in task_1.md were estimates written ahead. The actual on-disk record is: `_difficulty.md` written 2026-10-07T19:18:43Z, this file's frozen sections 19:19:54Z (sha256 386653350a5b1f1aeefb5b248a26941b3bfd088c36173c8044ddfb45cf18d638 before this append), task_1.md 19:20:47Z (sha256 b8ee3514…f01b90). GT revealed at 2026-10-07T19:20:55Z (first read of `tasks/0.json`), after both derivations were on disk. The frozen text above is unchanged.
- Need / authorisation / timing: same. GT hands the short-stay save to the host (`unlock_user_discoverable_tool` + `call_user_discoverable_tool`, owner user) and has support make the two resets.
- Read set: GT reads find_customers, verify, find_listings, find_listing_events, find_host_accounts, find_host_account_events, find_protection_plans, find_protection_claims, find_protection_events. Same as the derivation's inputs. The derivation did not need find_protection_events; claim_status on protection_claims already settles approved/denied.
- Now / wait / refuse: same (act now).
- Object: same (d230b90b…; garden room excluded).
- Parameters: pet_fee 340.0 = 340.00 ✓; cleaning_fee 397.5 = 397.50 ✓; short_stay_cleaning_fee 344.44 = 344.44 ✓.
- Tool / owner / order: same tools and owners. GT order is pet → cleaning → short-stay; the derivation allowed either order of the two resets, and the GT's `order_uniqueness` says the same.
- Terminal state: GT has pet 340.00, cleaning 397.50, short-stay 344.44 and three change rows. GT leaves `minimum_nights` at 2: there is no `raise_minimum_stay_1aeaa300` call. This confirms that finding T0-1 is outside gold.
- Problem tree vs `prerequisite_closure`, value against value:
  - root listing_ext_short_stay_cleaning_fee = same.
  - edge → cleaning: value_input, gate regular_cleaning_fee, state form = same. why_false figures 420.00 vs 397.50 = same. skipped effect 363.94 = same (derivation 363.94).
  - edge → pet: state_gate, listings.pet_fee = same. Figures 380.00 vs 340.00 = same. Skipped effect: terminal pet_fee 380.00 = same.
  - resolution_order [pet, cleaning, root] is consistent with the derivation's {pet, cleaning} → root.
- Factors vs `computations`, figure against figure:
  - pet: baseline_result 300.0 = 300.00. Sensitivity 320.0 / 327.5 / 332.5 / 380.0 = 320.00 / 327.50 / 332.50 / 380.00 ✓.
  - cleaning: 300.0 = 300.00. Sensitivity 363.75 / 382.5 / 375.0 / 382.5 / 386.25 / 430.0 = same ✓.
  - short-stay: 198.75 = 198.75. Sensitivity 234.53 / 324.56 / 320.59 / 312.64 / 384.19 = same ✓.
  - Tiers taken agree factor by factor.
- Closest alternative candidates and why they are excluded:
  - 363.94 (short-stay on the unreset cleaning fee): excluded by the root's "only after" sentence.
  - 345.38 (older Superhost assessment): excluded by "most recent".
  - Counting the 2025-08-27 / 2025-09-02 claims: excluded by "fewer than twelve whole months" (both are 12 whole months).
  - The extra minimum-stay raise to 3: **not excluded by any rule.** See T0-1.
- Proof-assertion check (design_rationale, closures, factor cards):
  - Every figure checked against the recomputation: allowance totals, shares, sensitivities, skipped effects, the 2025-03-01 pet ceiling (410.00 ≥ 380.00) and the reimbursement amounts. They agree, with two exceptions:
  - (a) `prerequisite_closure.edges[0].unresolved_at_frozen_time.why_false` says the cleaning fee "was raised to 420.00 on 2025-06-14, when two passes and a large deep-cleaning loss still stood behind it". The design_rationale [6] says the change records show "why they were valid then". In the seeded world `listing_events` holds no quality assessment before 2025-07-01. Recomputed on that world for 2025-06-14:
    - deep-cleaning 80.00 (claim 260c57bc, loss 1120)
    - sublimit 20.00
    - Superhost 30.00 (26 months)
    - tenure 20.00 (39 months)
    - turnover 0 (no assessment)
    - total 150.00
    - passes in six months 0, so the total is withdrawn and the ceiling is 300.00.
    So the 420.00 save, and the 350.00 save of 2024-05-10 (ceiling 300.00 by the same reading), are saves that listing_evt_fee_settings says "is not saved". The "two passes" the closure invokes are not records of this world. The charter's own "Every listing that is listed, snoozed or unlisted is assessed on the quality_assessment_schedule dates" requires quarterly rows from 2022-Q2 on for a listing first listed 2022-03-01, and none are seeded.
  - (b) design_rationale [13] "no second reading was found" and [12] "Base automatic clauses checked" both omit the minimum-stay floor that is due on the suite (T0-1).
- Verdict: **SOURCE-TASK RED (T0-1) + SOURCE-FACTOR RED (T0-2) + SOURCE-CHAIN RED (T0-6, proof assertion)**. Policy self-consistency for this task holds apart from the charter-global label defect. The tree itself holds: both prerequisites are genuinely unmet at the opening and both edges bear weight.

## findings

1. **T0-1 — SOURCE-TASK RED (confirmed against GT).** Two terminal states can each be defended.
   - Symptom: listing_ext_minimum_stay_floor is state_due and is due on the target listing at frozen_time (floor 3, minimum stay 2). Gold contains no minimum-stay write, yet the persona authorises support to bring "something else on the suite" into line.
   - Root cause: the seeded suite carries an approved property_damage claim (5c90d59e, 2026-05-08) and a 2026-07-01 quality warning (08acd299). Under the min-stay rule these make 1 night, doubled to 2, and the seed leaves `minimum_nights` at 2. The task's scope leaves that policy to task 1.
   - Evidence: min-stay rule "a minimum stay standing below the floor is raised to the floor exactly … when any quality assessment recorded on the listing within the last twelve months has outcome warning or suspension, the party-prevention nights are doubled". Seed rows `listings[d230b90b…].minimum_nights = 2`, `protection_claims[5c90d59e…]` approved, `listing_events[08acd299…]` warning. Persona: "go ahead and set it the way Roamhaven requires".
   - Demonstrated consequence: reading 1 is gold, with terminal minimum_nights 2 and three change rows. Reading 2 adds `raise_minimum_stay_1aeaa300(d230b90b…, 3)`, giving terminal minimum_nights 3 and a fourth change row (minimum_nights 2→3). The charter mandates reading 2 as a state_due obligation on the very object, and no rule limits it to a caller's request.
   - Real-world conflict on top: with a 3-night floor the suite can take no stay of `short_stay_max_nights` (2) nights or fewer, so the setting the host is buying would apply to no stay.
   - Affected: initial_state (listings.minimum_nights, the claim and warning rows), user_scenario consent line, evaluation_criteria (no min-stay write), design_rationale [12]/[13].
   - Previous revision: none (first audit).
2. **T0-2 — SOURCE-FACTOR RED** through `_difficulty.md` §findings G-1 (mislabelled method factors).
   - Symptom: on this world, pet_allowance_guest_standing (share 0.5 → baseline share 1 moves 340.00 to 380.00) and cleaning_assessment_record (0.75 → 1 moves 397.50 to 430.00) bear weight but are number substitutions.
   - Demonstrated consequence: counting only honest labels, the pet and cleaning computations carry 0 method factors.
   - Affected: listing.extended.yaml factors as cited, and computations[0] and [1].
   - The GT's own label argument (design_rationale [14]: "the three method factors change how a quantity is formed (allowance total withdrawn/halved/full; withdrawn/x0.75/full …)") describes the multiplier, which is the defect.
3. **T0-6 — SOURCE-CHAIN RED (proof assertion contradicted by the world).** Covered under source_gt_comparison (a).
   - Symptom: the closure grounds the opening state in a history the seed does not contain.
   - Root cause: quality assessments before 2025-07-01 are absent although the charter assesses a listed listing every quarter.
   - Evidence: why_false text quoted above. On the seeded world the cleaning-fee ceiling on 2025-06-14 is 300.00, and on 2024-05-10 it is 300.00.
   - Demonstrated consequence: two logged saves (350.00 and 420.00) exceed their day's ceiling, against "a setting outside its ceiling is not saved". The scored solution and the opening-state comparison (420.00 > 397.50) are unaffected.
   - Affected: initial_state.listing_events (missing quarterly assessments 2022-Q2 … 2025-Q1), prerequisite_closure.edges[0].why_false, design_rationale [6].
4. T0-3, T0-4 and T0-5 (observations in the frozen section) stand. T0-4 is upgraded in substance by T0-6, because the missing quality history is what leaves the logged saves without their justification.
5. Observation: GT reads find_protection_events. The policy surface does not need it (claim_status lives on protection_claims). The read is harmless.

## revision_2

### source_derivation_frozen (revision 2)

- Auditor: erl-task-policy-audit, round 2.
- This section was appended at 2026-10-07T21:18Z, before any round-2 GT was read.
- Inputs: view `/tmp/erl45_views/r2/…/task_0.view.json` (sha256 da4fb423840411cf98941f8ad501045ed33cd92e1577398357b51c314febe9f2), charter e432286d…, tools 376399fd….
- Masked: `tasks/0.json` beyond the view.
- contamination_disclosure: none. The round-1 GT of this task was read in round 1. Its values (340.00 / 397.50 / 344.44) belong to a different charter and world; none is reused, and every figure below is recomputed from the round-2 charter and view.
- View diff against round 1 (r1 vs r2 views):
  - frozen_time and user_scenario are unchanged.
  - Suite settings: nightly_rate 165 → 225, pet_fee 380 → 360, cleaning_fee 420 → 410. The fee-change rows were adjusted to match (nightly 205 → 225 on 2025-04-02, cleaning 280 → 335 on 2024-05-10, 335 → 410 on 2025-06-14, pet 300 → 360 on 2025-03-01).
  - 12 quality assessments were added (2022-07-01 not_assessed, then 2022-10-01 … 2025-04-01 all pass).
  - Claim dates moved: pet b1494371 → 2024-12-05, c05f55cf → 2025-11-10 (loss 780), 0c565b38 → 2026-04-02; deep 10524741 → 2025-11-05, 8182b52e → 2026-04-15; property 5c90d59e → 2025-07-15. Matching protection_events were updated.

### policy_self_consistency (this task, revision 2)

- Charter-global conclusions are cited from `_difficulty.md` §revision_2.
- Handling time: 2026-09-21 for every write. The two resets read neither each other's field nor any fee-change row. The short-stay ceiling is computed after both resets.
- No real-world waits: all claims are decided by 2026-05-02, and the latest assessment is 2026-07-01.
- G-3: not reached. G-5: the rule now explains the pet gate.

### problem_chain (revision 2)

| edge | kind | opening state | ceiling on 2026-09-21 | unmet? |
| --- | --- | --- | --- | --- |
| short-stay → cleaning | value_input | cleaning_fee 410.00 | 385.00 | yes |
| short-stay → pet | state_gate | pet_fee 360.00; short-stay fee 0.00 | 340.00 | yes |

- n = 2; 1 value_input ✓. The root's owner=user save is handed over ✓. The tree is acyclic.
- The two resets commute.
- Load-bearing:
  - Skipping the cleaning reset gives a short-stay ceiling of RND(410 × 0.866515…) = 355.27 instead of 333.61.
  - Skipping the pet reset leaves the gate closed and the terminal pet_fee at 360.00.
- The tools judge nothing, and the persona names no prerequisite (unchanged text).

### task_independent_derivation (revision 2)

1. Need, identity, authorisation and object are unchanged from round 1. Listing d230b90b…; verify with 7205552417 + 2583.
2. Pet-fee ceiling:
   - The assessment within 3 months is 08acd299 (2026-07-01) with 17 reviews, which is ≥ 15, so the busy look-back of 6 months applies.
   - Approved pet_damage claims within 6 months: 0c565b38 (2026-04-02, 5 months, loss 860). That gives 1 claim → 20.00, and loss 860 → 10.00.
   - Excluded: c05f55cf (2025-11-10, 10 months; near-miss, counted under the standard 12-month look-back), 7ae8a578, b1494371, and df94d8f9 (denied).
   - Standard plan pet sublimit 2500 → 10.00.
   - Ceiling 300 + 20 + 10 + 10 = **340.00**. Since 360.00 > 340.00 → `reset_pet_fee_f8e15273(d230b90b…, 340.00)`.
3. Cleaning-fee ceiling:
   - 08acd299 (warning, 2026-07-01) lies within 12 months, so the troubled look-back of 6 months applies.
   - Approved deep_cleaning claims within 6 months: 8182b52e (2026-04-15, loss 960) → 1 claim, loss < 1000 → 30.00.
   - Excluded: 10524741 (2025-11-05, 10 months; near-miss for the standard look-back) and 260c57bc (17 months).
   - Sublimit 1000 → 10.00. Deductible 250 → 10.00.
   - Superhost since 2023-04-01 is 41 months → 20.00. First listed 2022-03-01 is 54 months → 15.00.
   - Ceiling **385.00**. Since 410.00 > 385.00 → `reset_cleaning_fee_77ae9a3d(d230b90b…, 385.00)`.
4. Short-stay ceiling (after both resets):
   - Base: 0.5 + 0.5 × min(1, 2 × 73 / 264) = 0.776515… from c5a75840 (73 stays / 264 nights).
   - Damage: property_damage within 24 months is 5c90d59e (2025-07-15, 14 months) → 1 → +0.05.
   - Pet: pet_damage within 24 months is b1494371 (21 months), 7ae8a578, c05f55cf, 0c565b38 → 4 → +0.06 (df94d8f9 is denied).
   - Deep: deep_cleaning within 24 months is 260c57bc, 10524741, 8182b52e → 3 → +0.08.
   - Warnings within 6 months: 1 → −0.10.
   - Share 0.866515…; ceiling RND(385.00 × 0.866515…) = RND(333.6083) = **333.61**.
   - Contrast on the opening world: 355.27.
5. Sequence: verify identity → pet reset 340.00 and cleaning reset 385.00 (agent, either order) → hand over → host saves 333.61.
   - Terminal state: pet 340.00, cleaning 385.00, short-stay 333.61, and three change rows dated 2026-09-21.
6. Stray state_due check (round-1 T0-1):
   - Suite minimum-stay floor:
     - no party strikes;
     - no approved property_damage claim within 12 months (5c90d59e is 14 months back);
     - no safety reinstatement;
     - so 0 party-prevention nights and floor = 1, while the minimum stay is 2 → **not due**.
   - Suite extra-guest: per guest 225 / 2 = 112.50. There is no strike, so the look-back is 12 months and holds no property-damage loss. Share 0.70 + 0.05 + 0.06 = 0.81, giving a ceiling of 91.13 against a fee of 20.00 → not due.
   - Garden room (7f3f62b8…, Private Room, Essential plan):
     - pet 0.00 → not due;
     - cleaning 45.00 against a ceiling ≥ 200 → not due;
     - extra-guest 15.00 against RND(89 × (0.70 + 0.10 + 0.06)) = 76.54 → not due;
     - minimum-stay floor 1 against a minimum stay of 1 → not due.
   - No policy outside the tree is due. The round-1 second reading is gone.
7. History coherence (round-1 T0-6), recomputed on the round-2 seed with the round-2 charter at each logged save:
   - 2024-05-10, cleaning 280 → 335:
     - no troubled quarter;
     - 8 quarters in 24 months including the 2022-07-01 not_assessed → standard 12-month look-back;
     - no deep-clean claim → 0;
     - sublimit 10, deductible 10, Superhost 13 months → 10, tenure 26 months → 8;
     - ceiling 338.00 ≥ 335 ✓.
   - 2025-06-14, cleaning 335 → 410:
     - 8 all-pass quarters within 24 months → 24-month look-back;
     - 260c57bc (loss 1120 ≥ 1000) → 60;
     - sublimit 10, deductible 10, Superhost 26 months → 20, tenure 39 months → 15;
     - ceiling 415.00 ≥ 410 ✓.
   - 2025-03-01, pet 300 → 360:
     - the 2025-01-01 assessment counted 16 reviews → 6-month look-back;
     - b1494371 (approved 2024-12-20) and 7ae8a578 (approved 2025-02-27) → 50;
     - losses 540 + 720 = 1260 → 10;
     - sublimit 10;
     - ceiling 370.00 ≥ 360 ✓.
   - Reimbursements reproduce from the Standard level, each deep-clean claim offset by the cleaning fee then charged:
     - 260c57bc: 1120 − 335 − 250 = 535;
     - 10524741: 700 − 410 − 250 = 40;
     - 8182b52e: 960 − 410 − 250 = 300;
     - c05f55cf: 780 − 250 = 530;
     - 5c90d59e: 1450 × 0.8 − 250 = 910.
   - Paid claims per plan year stay ≤ 4 (2025-03-01 … 2026-02-28: 260c57bc, 5c90d59e, c05f55cf, 10524741).
   - One residue: the suite was first listed 2022-03-01, so it was listed on 2022-04-01, an assessment date, yet no 2022-04-01 row is seeded (the seeded history starts at 2022-07-01 "2022-Q2"). No scored window or history check reaches it.

### factor_weight (revision 2)

Pet (gold-candidate 340.00; full baseline 300.00):

| factor | tier / evidence | value under its baseline |
| --- | --- | --- |
| pet_claim_lookback (M) | busy, 17 reviews | look-back 12 → 2 claims → 50 and losses 1640 → 30 → 390.00 ✓ |
| pet_damage_claim_allowance (P) | one claim, 0c565b38 | 320.00 ✓ |
| pet_damage_loss_allowance (P) | low, 860 | 330.00 ✓ |
| pet_sublimit_allowance (P) | mid, Standard | 330.00 ✓ |

- Near-miss: c05f55cf is excluded only by the busy look-back.
- 1 M + 3 P ✓.

Cleaning (gold-candidate 385.00; full baseline 300.00):

| factor | tier / evidence | value under its baseline |
| --- | --- | --- |
| deep_cleaning_lookback (M) | troubled, 08acd299 warning | 12-month look-back → 2 claims → 60 → 415.00 ✓ |
| deep_cleaning_allowance (P, multi-source) | one claim < 1000, 8182b52e | 355.00 ✓ |
| cleaning_sublimit_allowance (P) | mid | 375.00 ✓ |
| cleaning_deductible_allowance (P) | mid, 250 | 375.00 ✓ |
| superhost_cleaning_allowance (P) | long, host f38df7ac… | 365.00 ✓ |
| listing_tenure_allowance (P) | long | 370.00 ✓ |

- Near-miss: 10524741 is excluded only by the troubled look-back.
- 1 M + 5 P ✓.

Short-stay (gold-candidate 333.61; full baseline 385 × 0.5 = 192.50):

| factor | value under its baseline |
| --- | --- |
| typical_stay_base | 227.15 ✓ |
| damage_addition | 314.36 ✓ |
| pet_turnover_addition | 310.51 ✓ |
| deep_cleaning_turnover_addition | 302.81 ✓ |
| guest_rating_cut | 372.11 ✓ |

- Near-miss: the older Superhost assessment abb73c45.

Task level:
- multi-source ≥ 1 (deep_cleaning_allowance) ✓;
- cross-difficulty ≥ 1 (protect claims and plan, host tier and assessment; all seeded) ✓;
- no stamp ✓.

### findings (revision 2, frozen, pre-reveal)

- **T0-1 — closed (pending GT).** The minimum-stay floor is no longer due on the suite. Moving 5c90d59e out of the 12-month window gives a floor of 1. No other state_due policy is due on either listing.
- **T0-2 — closed** via G-1 closure: the pet and cleaning computations now carry honest look-back method factors, and both bear weight.
- **T0-3 — reduced, still an observation (realism).**
  - The suite now rents at $225, with a cleaning fee of $410 (1.8× the nightly rate) and a pet fee of $360 (1.6×).
  - The resets bring them to $385 / $340.
  - That is still high for a one-bedroom suite, but the seeded deep-clean and pet-damage losses ($700–$1,120 per incident) motivate them.
- **T0-4 — largely closed.** Quality history is now seeded from 2022-07-01. One remaining gap: the 2022-04-01 assessment is absent (observation; no effect).
- **T0-5 — closed** (G-5).
- **T0-6 — closed (pending the GT text check).** Every logged save is within its day's ceiling on the round-2 seed.
- No new defect found pre-reveal.

### source_gt_comparison (revision 2)

- Reveal: round-2 `tasks/0.json` was first read at 2026-10-07T21:19:30Z. This file's revision_2 frozen section was already on disk at 21:18:48Z (sha256 of the whole file before this append: 8f960e6e2443f7564153d9a96169a49c301984c8498d3f7417f4a8643b0ef94f).
- Need, authorisation and timing; now/wait/refuse; object: same.
- Read set: same as round 1 (GT also reads find_protection_events, which is harmless).
- Writes, value against value:

  | write | GT | derivation |
  | --- | --- | --- |
  | pet_fee | 340.0 | 340.00 ✓ |
  | cleaning_fee | 385.0 | 385.00 ✓ |
  | short_stay_cleaning_fee (owner user) | 333.61 | 333.61 ✓ |

  Order: pet → cleaning → save, inside the derivation's commuting class ✓. No other write in GT, and the derivation found no other policy due ✓.
- prerequisite_closure:
  - Edges: value_input / state_gate, as derived ✓.
  - why_false: 410.00 vs 385.00 and 360.00 vs 340.00 ✓.
  - Load-bearing: 355.27 ✓; pet 360.00 terminal ✓.
  - resolution_order is consistent ✓.
- computations, figure against figure:

  | computation | baseline_result | sensitivity |
  | --- | --- | --- |
  | pet | 300.0 ✓ | 390 / 320 / 330 / 330 ✓ |
  | cleaning | 300.0 ✓ | 415 / 355 / 375 / 375 / 365 / 370 ✓ |
  | short-stay | 192.5 ✓ | 227.15 / 314.36 / 310.51 / 302.81 / 372.11 ✓ |

- Proof assertions, each recomputed:
  - The why_false history clauses (2025-06-14 ceiling 415.00 with eight all-pass quarters and a 24-month look-back; 2025-03-01 ceiling 370.00 from the 16-review assessment) match derivation item 7 ✓.
  - Rationale [6] removal figures:
    - without the warning: 7 passes, 24-month look-back, 415.00 ✓;
    - without 0c565b38: 310.00 ✓;
    - older Superhost assessment: 0.778884 ✓.
  - Rationale [12] "no other state_due obligation on either listing" ✓ (derivation item 6).
  - Rationale [6] "17 quarterly assessments 2022-Q2 … 2026-Q2" is accurate as a count. The series still omits the 2022-04-01 date on which the newly listed suite would have been assessed (observation, no effect).
- Status of round-1 items:
  - T0-1 genuinely closed (the floor is 1; the persona's consent now covers exactly the two resets).
  - T0-2 closed.
  - T0-6 closed: every logged save is within its day's ceiling, and the closure's history now matches the seed.
  - T0-5 closed.
  - T0-3 reduced (observation).
  - T0-4 residual (observation).
- Regressions: none. New defects: none.
- **Verdict revision 2: PASS.** Policy self-consistency PASS; problem tree PASS; factors bear weight PASS; unique solution PASS.

### findings (revision 2)

- Observation T0-3 (realism, reduced): suite cleaning fee $410 and pet fee $360 at a $225 nightly rate, reset to $385 / $340. These are high, but the seeded loss history motivates them.
- Observation T0-4 (residual): the 2022-04-01 quality assessment of the newly listed suite is not seeded. No scored or history check reaches it.
- Charter-global observations G-2, G-3, G-6, G-7 and R2-G-a are cited from `_difficulty.md` §revision_2.
