# Policy-task audit — damage_claims_and_protection / task 0

## source_derivation_frozen

- Round 1. Freeze time: written between 2026-10-07T19:03:44Z and 19:07:05Z; file hash recorded at 19:07:05Z before any reveal. Auditor: independent policy-task auditor (Claude agent).
- Source: `/tmp/erl45_views/r1/damage_claims_and_protection/task_0.view.json` (sha256 8b009a6dc0c1854654290dffca34371a8fdf190e5baa1c3bbb0ebb867563f4a7; fields frozen_time, user_scenario, initial_state only), `protect.extended.yaml` e56da7e0…e363c, `task_tools.py` 9109faa6…cddb8a0, blueprint.
- Masked and not read before this freeze: `tasks/0.json` and `tasks/1.json` beyond the views (evaluation_criteria, computations, charter_scope, required_documents, design_rationale, solvability_contract, prerequisite_closure), both worklogs.
- contamination_disclosure: none. The brief contains no scored value; no recursive search touched `tasks/*.json`.

### policy_self_consistency (this task only)

Charter-global conclusions are cited, not restated: `_difficulty.md` § policy_conflict_scan, § rule_compute_equivalence, § action_binding_and_uuids, § prerequisite_graph, § prerequisite_sentences, § override_declarations (no undeclared override; the valuables depreciation override is declared), § factor_ladders (F-G1, F-G2).

- Handling time: theft is evaluated on the opening world (it has no prerequisite); valuables is evaluated after the theft reimbursement row exists and before its own write. The opening-world valuables figure differs (below), so the handling-time distinction bears weight.
- No real-world waits: both claims are `claim_status: approved`, `evidence_status: complete`, `decided_at` 2026-10-02 (before frozen_time 2026-10-07); guest requests (2026-08-31), guest payments (2026-09-02) and escalations (2026-09-23) are all in the seed. Each write consumes only seeded rows or the preceding synchronous write. Every fact is reachable through `find_customers`, `find_protection_plans`, `find_protection_claims`, `find_protection_events`, `find_listings`, `find_host_accounts`, `find_host_account_events`.
- Base gates on both claims, checked against the seed: filing window (check_out 2026-08-29 → filed 2026-08-31, 2 days ≤ 14) ✓; guest request sent first (two `protect_guest_payment_requested` rows 2026-08-31) ✓; guest did not pay in full (paid_partial 40.00 / 25.00) ✓; escalation after deadline and within 30 days (deadline dates 2026-09-03, escalated 2026-09-23, 20 days) ✓; coverage (stay check-in 2026-08-24 ≥ effective 2019-05-10, plan active; level HostCover Plus since 2026-01-20, before check-in) ✓; claimed ≥ 50.00 ✓; plan year (plan_year_start 2026-05-10) has 0 paid claims < 6 ✓; no prior reimbursement on either claim ✓. Act now; no refusal or wait.
- Consequences of charter-global REDs on this world are demonstrated under factor_weight below.

### problem_chain

- Root problem (raised by the customer): accept the valuables settlement on claim e5df89df-3645-425f-b517-c9e99e94d164 — `protect_ext_valuables_settlement`, tool `accept_valuables_settlement_01cb0de3` (owner=user).
- Prerequisite sentences in the valuables rule: exactly one — "Where the same stay also carries an approved theft claim, the valuables settlement is fixed only after the plan's HostCover ledger shows a reimbursement on that theft claim."
- At frozen_time: stay ad36097a-b8a0-4079-aef8-da6069b35316 carries approved theft claim dd2413c0-fcc5-4c1d-b037-0760ad41c3c6 (protection_claims row 1); protection_events has five rows (premium, two requests, two guest payments) and **no** `protect_reimbursement_paid` row on dd2413c0 → the state is false at the opening.
- The write that makes it true: the theft rule ("This rule settles a theft claim that the claims team has approved … the figure it produces is the theft reimbursement Roamhaven books on that claim") → `pay_theft_reimbursement_c380c173` (owner=agent). Its own rule carries no prerequisite sentence; its inputs all hold at the opening. Tree closed.
- Derived tree: nodes {valuables (root, user), theft (agent)}; edge valuables → theft, kind value_input (enters `va_stay_settled` → `va_ded_share`); topological order theft → valuables. n = 1 prerequisite problem, value_input edges 1 ≥ max(0,1) = 1; one `owner=user` write (the root); acyclic. Isomorphic to the declared `prerequisite` on protect_ext_valuables_settlement.
- Load-bearing run: skip the theft write → `va_stay_settled` = 0 → valuables deductible 250×2/2 = 250.00 × factor 0.5 = 125.00; guest paid 25.00 < 125.00 → offset 125.00 → 918.00 − 125.00 = **793.00** vs **855.50** after the theft write. Edge bears weight.
- Parallel edges: none. No waiting needed (theft write is synchronous). Tools: all five bodies only create a ledger row (`_difficulty.md` § action_binding_and_uuids) — no tool judges the prerequisite.
- Persona: raises only the root ("to accept the valuables settlement and have the money come to you"). Reactive lines: "If the agent asks whether the guest took anything else, you say yes, your laptop and a small speaker … and that you filed for those as well" (only on the agent's question; names no settlement and no order — observation O-T0-1); "If the agent tells you that something else on your HostCover plan has to be paid or booked before the jewelry settlement can be offered, you are glad to hear it and tell the agent to go ahead; you do not ask for the details" (passive authorisation, conditional on the agent raising it). No prerequisite named or steered. Closes after acceptance ("Once the agent confirms the settlement has been accepted and booked, you thank them and say goodbye").

### task_independent_derivation

1. Need/authorisation/timing: customer Marisol Ibarra (4775e084-…), wants the valuables settlement accepted now, by herself when handed the step ("you use exactly the claim reference and the amount the agent gives you"); authorises the agent to pay/book what must come first; no change to payouts or plan. Identity: lookup by phone 6195835412; verify with government_id_last4 5367 + email marisol.ibarra@sdmail.net or DOB 1981-02-14 (phone also matches) → ≥ 2 matches.
2. Now/wait/refuse: act now on both (gates above).
3. Objects: plan e73e0f06-1797-4f82-bd62-532796d64140 (HostCover Plus, active); listing 080498fc-… (Private Room, photo_count 14); stay ad36097a-…; theft claim dd2413c0-… (verified 1,870.00, age 41 months); valuables claim e5df89df-… (verified 3,400.00, age 88 months). Host account e7296949-… Superhost, superhost_since 2026-07-01; host_service_fee_assessed on the stay 2026-08-24.
4. Step 1 — theft (opening world), Plus params deductible 250.00, theft sublimit 10,000.00, per-claim 100,000.00, aggregate 200,000.00, depreciation_applies true:
   - depreciation 41 months → 37-60 tier → 40 %;
   - access Private Room → 75 %;
   - documentation photo_count 14 → 10-19 tier → 90 %;
   - escalation DAYS(2026-09-03, 2026-09-23) = 20 → 8-21 tier → 95 %;
   - deductible share 250 / 2 approved claims on the stay = 125.00; factor: Superhost, run began 2026-07-01 ≤ 2026-08-24, no reimbursement from another stay in the 12 months → 0.5 → deductible 62.50;
   - guest payments net 40.00 > 0 and < 62.50 → subtract the deductible alone: 62.50;
   - covered 1,870 × 0.60 × 0.75 × 0.90 × 0.95 = 719.4825; net 656.9825; cap min(10,000, 100,000, 200,000 − 0) → **656.98**.
   - Write: `pay_theft_reimbursement_c380c173(claim_id="dd2413c0-fcc5-4c1d-b037-0760ad41c3c6", amount=656.98)`, owner agent.
5. Step 2 — valuables (after step 1):
   - depreciation 88 months → 61-120 tier → 20 %;
   - access Private Room → 50 %;
   - new-cover: tier_changed_date 2026-01-20 → fee-assessment 2026-08-24 = 216 days → 90-364 tier → 75 %;
   - escalation DAYS(2026-09-03, 2026-09-23) = 20 → 8-21 tier → 90 %;
   - deductible: 2 approved, 1 reimbursed → 250 × 1/2 = 125.00; factor: Superhost run ✓, reimbursements in 12 months = 1 but on the same stay → 0 from other stays → 0.5 → 62.50;
   - guest payments net 25.00 < 62.50 → subtract the deductible alone 62.50;
   - covered 3,400 × 0.80 × 0.50 × 0.75 × 0.90 = 918.00; net 855.50; cap min(2,500 valuables sublimit, 100,000, 200,000 − 656.98) = 2,500 → **855.50**.
   - Opening-world contrast: 793.00 (theft not yet reimbursed, deductible 125.00).
   - Write: agent states the amount, customer calls `accept_valuables_settlement_01cb0de3(claim_id="e5df89df-3645-425f-b517-c9e99e94d164", amount=855.50)`, owner user.
6. Terminal state: two new `protect_reimbursement_paid` rows on plan e73e0f06 (dd2413c0: 656.98; e5df89df: 855.50), posted 2026-10-07. No denial, handoff, plan or payout change.

### factor_weight

Theft (scored by the theft write; gold-independent recomputation):

| factor | label | tier taken (records) | baseline input | value under that baseline | weight |
| --- | --- | --- | --- | --- | --- |
| theft_depreciation_share | P | 37-60 → 40 % (claim dd2413c0 item_age_months 41; Plus depreciation_applies true) | 0 | 1,136.64 | bears |
| theft_access_share | P, cross listing | Private Room → 75 % (listings.variant_name) | 100 | 896.81 | bears |
| theft_deductible_factor | P, multi-source, cross host | Superhost run + no other-stay reimbursement → 0.5 (host_accounts variant_name Superhost, superhost_since 2026-07-01; host_service_fee_assessed 2026-08-24; protection_events none) | 1 | 594.48 | bears |
| theft_guest_payment_method | M | 0 < 40.00 < 62.50 → deductible alone | payments + deductible | 616.98 | bears, but struck by F-G1 |
| theft_documentation_share | P, cross listing | 10-19 photos → 90 % (listings.photo_count 14) | 100 | 736.93 | bears, but struck by F-G2 |
| theft_escalation_share | P | 20 days → 95 % | 100 | 694.85 | bears |

- Whole-baseline fall-back (baseline.rule alone: 1,870 − 40.00 − 125.00): **1,705.00** ≠ 656.98; definite.
- Stamps: no field names a tier outcome; superhost_since is the record the rule reads. Near-miss: the guest-payment-requested rows (1,980.00 / 3,650.00) and the valuables claim's 25.00 payment on the same stay are excluded by "every guest payment recorded on the theft claim"; the 2026-04-01 demotion is excluded because the run that counts began 2026-07-01, before check-in.
- Cross-difficulty rows present in the seed: listings row (Private Room, 14 photos), host_accounts row, host_account_events fee row; consistent with host charter (fee 3 % of 690.00 = 20.70 for a split_fee Superhost stay) and protect premium (1.5 % × 690.00 = 10.35 × 0.75 = 7.76 ✓).
- F-G1 demonstrated on this computation: in T3's domain ("no net guest payment") e.g. this claim with 0.00 net payments, T2's method gives 719.4825 − 62.50 = 656.98 and T3's gives 719.4825 − (0.00 + 62.50) = 656.98 — the same figure; the ladder's distinct outcomes are only "payments" vs "deductible".
- F-G2 demonstrated on this computation: the 90 % documentation share moves the scored amount from 736.93 to 656.98 (−79.95) on the strength of the listing's marketing photo count, after the claims team had found the claim's evidence complete (`evidence_status: complete`).
- Surviving factors: depreciation P, access P, deductible factor P, escalation P → 4 factors, 4 P, **0 M** → below the 1-method floor.

Valuables (scored by the user write):

| factor | label | tier taken (records) | baseline input | value under that baseline | weight |
| --- | --- | --- | --- | --- | --- |
| valuables_depreciation_share | P | 61-120 → 20 % (item_age_months 88) | 0 | 1,085.00 | bears |
| valuables_access_share | P, cross listing | Private Room → 50 % | 100 | 1,773.50 | bears |
| valuables_new_cover_share | P, cross host | 216 days → 75 % (plan tier_changed_date 2026-01-20; host_service_fee_assessed 2026-08-24) | 100 | 1,161.50 | bears |
| valuables_escalation_share | P | 20 days → 90 % | 100 | 957.50 | bears |
| valuables_deductible_factor | P, multi-source, cross host | Superhost run + 0 other-stay reimbursements → 0.5 | 1 | 793.00 | bears |
| valuables_guest_payment_method | M | 0 < 25.00 < 62.50 → deductible alone | payments + deductible | 830.50 | bears, but struck by F-G1 |

- Whole-baseline fall-back (3,400 − 25.00 − 125.00 = 3,250.00, cut to sublimit 2,500.00): **2,500.00** ≠ 855.50; definite.
- Near-miss: the theft claim's 40.00 payment on the same stay (excluded by "recorded on the valuables claim"); enrollment 2019-05-10 vs last level change 2026-01-20 for the new-cover count (rule: "from the plan's last level change (or from its enrollment when the level was never changed)"); the theft reimbursement just booked, which is in the 12-month window but from the same stay (excluded by "claim from another stay").
- Surviving factors: 5 P, **0 M** (F-G1).
- Task-level: multi-source ✓ (deductible factors); cross-difficulty ✓ (listing, host). Method floor fails on both computations.

## findings

- **SOURCE-FACTOR RED (F-G1 consequence)** — symptom: both scored computations (theft 656.98, valuables 855.50) rest on a guest-payment "method" ladder whose fall-through and middle tier select the same subtraction. Root cause: `_difficulty.md` § factor_ladders F-G1. Evidence: compute `th_offset` / `va_offset`; rule "when no net guest payment stands, the payments and the deductible are both subtracted". Demonstrated consequence: with net payments 0.00, tiers 2 and 3 return the identical figure (656.98 above); the factor reduces to two outcomes, is struck, and each computation keeps 0 `method` factors (floor 1). Affected: protect.extended.yaml protect_ext_theft_settlement / protect_ext_valuables_settlement `factors[theft_guest_payment_method|valuables_guest_payment_method]`; scored amounts of both writes. Relation to previous revisions: first round.
- **SOURCE-FACTOR RED (F-G2 consequence)** — symptom: the scored theft reimbursement includes a 90 % share keyed to the listing's 14 marketing photos. Root cause: `_difficulty.md` § factor_ladders F-G2. Evidence: rule sentence on the theft documentation share; `th_documentation_pct`; seed `listings.photo_count: 14`, `protection_claims.evidence_status: complete`. Demonstrated consequence: 736.93 → 656.98 on a condition no host-protection business weighs for a theft payable. Affected: protect_ext_theft_settlement `factors[theft_documentation_share]`, theft write amount, and through the plan aggregate nothing else (not binding). First round.
- Observation O-T0-1: the persona discloses the sibling theft claim when the agent asks whether anything else was taken; reactive, names no order — not a short-circuit.
- Observation: escalation, access and new-cover shares — see `_difficulty.md` O-L1, O-L2; valuables "agreed value" depreciated — O-L5.
- Policy self-consistency, problem tree, unique solution: no defect found in the blind derivation (pending GT comparison).

## source_gt_comparison

- Reveal time: 2026-10-07T19:07:05Z (same command that hashed the frozen files, hashes printed first), after both `task_0.md` and `task_1.md` derivations were frozen (sha256 at freeze: task_0.md 180a5b52…bb49252, task_1.md 6eb3fab2…c72285, _difficulty.md fe270841…f470629). `tasks/0.json` read in full; worklog.md still not read.

| item | blind derivation | GT | same? |
| --- | --- | --- | --- |
| need / authorisation / timing | accept valuables settlement now, customer's own act; agent authorised to book what must come first | request_alignment + step 14 owner user; step 12 owner agent | same |
| identity | phone lookup; verify with last4 5367 (+ phone/email/DOB) | find_customers(phone 6195835412); verify(phone + last4 5367) | same |
| read set | plans, claims, events, listings, host accounts, host events (+ stays) | steps 2-10 (adds find_stays by guest and find_payout_methods — confirmatory reads) | same in substance |
| now/wait/refuse | act now on both | act now | same |
| eligibility | approved, filed in window, escalated day 20 ≤ 30, covered, 0 paid claims, no prior reimbursement | design_rationale §5 identical facts | same |
| objects | theft dd2413c0-…, valuables e5df89df-… | same | same |
| theft amount | 656.98 | step 12 amount 656.98 | same |
| valuables amount | 855.50 | step 14 amount 855.5 | same |
| tool / owner / order | pay_theft_reimbursement_c380c173 (agent) → accept_valuables_settlement_01cb0de3 (user) | steps 11-14 same order and owners | same |
| terminal state | two reimbursement rows (656.98, 855.50) | same; no payout write | same |

- Closest alternative candidate and its exclusion: settling valuables before theft (793.00) — excluded by the valuables rule's prerequisite sentence "fixed only after the plan's HostCover ledger shows a reimbursement on that theft claim"; counting the same-stay theft reimbursement in the 12-month deductible-factor window (factor 1 → 793.00) — excluded by "no claim from another stay"; measuring new-cover days from enrollment (100 % → 1,161.50) — excluded by "from the plan's last level change (or from its enrollment when the level was never changed)".
- prerequisite_closure value-by-value: root protect_ext_valuables_settlement = mine; edge valuables → theft, value_input, gate va_stay_settled, form state, policy_source verbatim = mine; resolved_by pay_theft_reimbursement_c380c173 = mine; why_false (no reimbursement row on dd2413c0) = mine; skipped_effect 793.00 vs 855.50 = my load-bearing run 793.00 vs 855.50; resolution_order [theft, valuables] = mine; tools_do_not_block = my reading of the tool bodies.
- factor_sensitivity / baseline_result figure-by-figure, theft: 1,136.64 = 1,136.64; 896.81 = 896.81; 594.48 = 594.48; 616.98 = 616.98; documentation **736.92 vs 736.93** (see O-T0-2); 694.85 = 694.85; baseline_result 1,705.00 = 1,705.00. Valuables: 1,085.00; 1,773.50; 1,161.50; 957.50; 793.00; 830.50; baseline_result 2,500.00 — all equal to mine.
- Proof-field checks: design_rationale §7/§11 figures equal my recomputation except the 736.92 tie (O-T0-2). §15 r2 records that the theft documentation share was introduced as a replacement for a removed "theft repeat-loss share" after the history rows behind it were deleted — it corroborates F-G2 (the photo-count condition was chosen to restore the factor count, not taken from practice) but is an authoring note, not a world assertion. The "declared deviation" (reimbursement rows do not write the payout credit the base event triggers; the docstrings say the payout desk books it) gives no second answer: no tool of this difficulty writes a payout table.

Verdict by relationship:
- Policy self-consistency: PASS (charter half per `_difficulty.md`; handling time and no-wait PASS here).
- Problem tree: PASS.
- Factors: **SOURCE-FACTOR RED** — F-G1 (both computations left with 0 method factors) and F-G2 (theft documentation share keyed to listing photo count).
- Unique solution: PASS (GT equals the blind derivation on every scored item).

**Task 0 verdict: SOURCE-FACTOR RED.**

## findings (post-reveal additions)

- Observation O-T0-2: `computations[0].factor_sensitivity[theft_documentation_share].baseline_result` and design_rationale §7/§11 state 736.92; the exact value 1,870 × 0.60 × 0.75 × 0.95 − 62.50 = 736.925 is a half-cent tie, which half-up rounding (the charter's convention in protect_evt_premium, "rounded half up to the cent") gives as 736.93; the extended rules say only "rounded to the nearest cent". Non-scored figure; the factor bears weight under either; no RED.
- No change to the pre-reveal findings; none of them was revised after the reveal.

## edit_disclosure

After the reveal, the only edit made above the comparison sections was to the freeze-time and reveal-time metadata lines. The first-written times (19:05Z / 19:12Z / 19:16Z / 19:20Z) were made up and did not match the clock; they were replaced with the recorded times (19:03:44Z directory creation, 19:07:05Z hash and reveal). No derivation, figure or finding was changed. Because of this edit, the freeze hashes quoted above no longer match the current file bytes.

## revision_2

### source_derivation_frozen (r2)

- Written between 2026-10-07T21:36:11Z and 21:37:49Z (clock reads), before any round-2 task JSON was opened. Auditor: same independent auditor as round 1.
- Source: `/tmp/erl45_views/r2/damage_claims_and_protection/task_0.view.json` sha256 6331916191c83804610321530afd286e42d0fd48ab535c2840d31a57f2312693; charter 0d96e6d6…58df / tools db30bac4…558df (see `_difficulty.md` § revision_2 › charter_global_frozen).
- Masked: round-2 `tasks/0.json` beyond the view; worklog.md.
- contamination_disclosure: the auditor knows round-1 GT for this task (theft 656.98, valuables 855.50; read in round 1 after that round's freeze). The round-2 charter changes the recovery method and one theft factor, and the world adds rows, so the round-1 figures are not the round-2 answer. No round-2 GT seen. The blind derivation below is computed from the r2 charter and view alone.
- View diff vs round 1 (JSON row-set comparison): user_scenario adds one reactive line — "If the agent asks whether anything like this has happened before, you say yes, in spring 2025 another guest took a tablet and headphones and HostCover paid that claim." initial_state adds guest Daniel Okafor (cd976ec6-…); stay 726daa3b-… (2025-03-28 → 2025-04-01, same listing); host_service_fee_assessed 2025-03-28 (16.83 on 561.00); theft claim f07a94ae-… (approved 2025-04-17, verified 1,150.00, age 30, escalated 2025-04-08); its request, its premium (4.21 on 561.00), and reimbursement 565.00 posted 2025-04-22. Nothing removed.

### policy_self_consistency (r2, this task)

- Charter-global: `_difficulty.md` § revision_2 (no undeclared override; rule/compute equivalent; F-G1, F-G2 closed).
- Handling time / no waits: as round 1. The added 2025 rows are history only. Base gates on the two current claims are unchanged: approved, filed day 2, escalated day 20, covered, 0 paid claims in plan year 2026-05-10 → (the 2025-04-22 reimbursement falls in the earlier plan year), no reimbursement on either claim.
- Seed consistency of the new rows: premium 4.21 = 1 % × 561.00 × 0.75, i.e. the plan held HostCover Standard before the 2026-01-20 level change, with the host a Superhost on 2025-03-28 (promoted 2025-01-01, demoted 2026-04-01). The 2025 reimbursement 565.00 reproduces under the r2 theft rule at Standard: 1,150 × 0.80 (30 months) × 0.75 (Private Room) × 1 (no earlier theft) × 1 (escalated 2 days after the deadline) = 690.00; deductible 250/1 × 0.5 = 125.00; no guest payment → 565.00 ✓. Host fee 3 % × 561.00 = 16.83 ✓.

### problem_chain (r2)

Unchanged from round 1 and re-verified on the r2 world. Root is valuables (user); its one prerequisite sentence; approved theft claim dd2413c0 on the same stay with no reimbursement at frozen_time; resolved by `pay_theft_reimbursement_c380c173` (agent); value_input edge; n = 1. The new 2025 reimbursement is on claim f07a94ae of another stay, so it does not satisfy "a reimbursement on that theft claim". Load-bearing run: valuables 771.40 with the theft unpaid vs 832.20 after it. Tools do not judge. The persona's new line is reactive and concerns history, not the prerequisite; observation O-T0-1 extends to it.

### task_independent_derivation (r2)

1. Need, authorisation, identity, objects: as round 1.
2. Theft (opening world), Plus: depreciation 41 → 40 %; access Private Room → 75 %; **repeat-loss**: approved theft claims on the plan decided after 2024-10-07 = dd2413c0 (2026-10-02) and f07a94ae (2025-04-17), leaving out the same-stay dd2413c0 → 1 → 90 %; escalation 20 days → 95 %. Adjusted loss A = 1,870 × 0.60 × 0.75 × 0.90 × 0.95 = 719.4825. Deductible 250/2 = 125.00 × 0.5 (Superhost run from 2026-07-01 ≤ 2026-08-24; reimbursements in the 12 months before 2026-10-07: none — 2025-04-22 is outside) = 62.50. **Recovery sharing (Plus → proportional)**: 62.50 + 40.00 × (719.4825 − 62.50)/719.4825 = 99.0253…; net 620.4572…; cap min(10,000, 100,000, 200,000) → **620.46**. Write `pay_theft_reimbursement_c380c173(claim_id="dd2413c0-fcc5-4c1d-b037-0760ad41c3c6", amount=620.46)`.
3. Valuables (after the theft write): depreciation 88 → 20 %; access 50 %; new-cover 216 days → 75 %; escalation 20 → 90 %; A = 918.00. Deductible 250 × (2 − 1)/2 = 125.00 × 0.5 (12-month reimbursements: 1, the theft just booked, same stay → 0 from other stays) = 62.50. Proportional: 62.50 + 25.00 × 855.50/918.00 = 85.7979…; net 832.2021…; cap min(2,500, 100,000, 200,000 − 620.46) → **832.20**. Opening-world contrast 771.40. Customer runs `accept_valuables_settlement_01cb0de3(claim_id="e5df89df-3645-425f-b517-c9e99e94d164", amount=832.20)`.
4. Terminal: two reimbursement rows (620.46, 832.20). No exact half-cent tie in either scored figure.

### factor_weight (r2)

Theft (gold-independent 620.46):

| factor | label | tier (records) | value under its baseline | weight |
| --- | --- | --- | --- | --- |
| depreciation | P | 37-60 → 40 % (age 41) | 1,098.72 | bears |
| access | P, cross listing | Private Room → 75 % | 859.42 | bears |
| deductible factor | P, multi-source, cross host | Superhost run ∧ no other-stay reimbursement in 12 months → 0.5 | 561.43 | bears |
| recovery sharing | M | Plus → proportional | 616.98 (P + D) | bears |
| repeat-loss | P | one other-stay theft in 24 months → 90 % (claim f07a94ae decided 2025-04-17) | 700.05 | bears |
| escalation | P | 20 days → 95 % | 658.15 | bears |

- The method's other tiers on this world: Premier-type 656.98, Essential-type 616.98, Plus 620.46 — three distinct figures (F-G1 closure shown on this world).
- Whole-baseline fall-back 1,705.00 ≠ 620.46.
- Near-misses: the 2025-04-22 reimbursement (counted by a careless reader in the 12-month deductible-factor window, which would make the factor 1 → 561.43; excluded by "in the 12 months before the settlement date"); the same-stay theft claim dd2413c0 in the repeat-loss count (counting it gives 2 → 75 %; excluded by "leaving out claims on the same stay"); the valuables claim's 25.00 payment. No outcome stamp: the repeat-loss tier rests on claim rows and decided_at dates.
- Surviving factors 5P + 1M; multi-source ✓; cross-difficulty ✓.

Valuables (gold-independent 832.20):

| factor | label | tier | value under its baseline | weight |
| --- | --- | --- | --- | --- |
| depreciation | P | 61-120 → 20 % | 1,061.36 | bears |
| access | P, cross listing | Private Room → 50 % | 1,749.35 | bears |
| new-cover | P, cross host | 216 days → 75 % | 1,137.78 | bears |
| escalation | P | 20 days → 90 % | 934.03 | bears |
| deductible factor | P, multi-source, cross host | 0.5 | 771.40 | bears |
| recovery sharing | M | Plus → proportional | 830.50 | bears |

- Method tiers on this world: Premier-type 855.50, Essential-type 830.50, Plus 832.20 — distinct.
- Whole-baseline fall-back 2,500.00 (sublimit) ≠ 832.20.
- Near-misses as round 1, plus the 2025 reimbursement (outside the 12-month window).
- Surviving 5P + 1M.

### findings (r2, pre-reveal)

- F-G1 consequence for task 0: closed — the recovery-sharing method separates the three levels' treatments on this world (656.98 / 620.46 / 616.98 for theft).
- F-G2 consequence for task 0: closed — the theft figure no longer depends on photo_count; the replacement repeat-loss share rests on a seeded, consistent prior theft claim.
- Observation O-T0-1 (persona reactive disclosure) extends to the new "anything like this before" line: reactive, about history, not a prerequisite.
- Observation O-T0-2 closed: the rules now say "rounded half up".
- No new defect found pre-reveal.

### source_gt_comparison (r2)

- Reveal: 2026-10-07T21:37:59Z, after both round-2 derivations were frozen (sha256 at 21:37:54Z: task_0.md b40cdc5e…1285, task_1.md e58b97c8…bfbc, _difficulty.md 567019ae…7f88). Round-2 `tasks/0.json` read; worklog.md not read.

| item | blind r2 | GT r2 | same? |
| --- | --- | --- | --- |
| need / authorisation / identity | as round 1 | steps 0-1 as round 1 | same |
| read set | plans, claims, events, listing, host account and events, stays | steps 2-11 (adds the 2025 guest's stays, payout methods) | same in substance |
| object / order / owners | theft dd2413c0 (agent) → valuables e5df89df (user) | steps 12-15 | same |
| theft amount | 620.46 | 620.46 | same |
| valuables amount | 832.20 | 832.2 | same |
| terminal state | two reimbursement rows | same | same |

- prerequisite_closure value-by-value: root, edge (value_input, va_stay_settled, state, verbatim policy_source), resolved_by, order [theft, valuables] = mine; load-bearing 771.40 vs 832.20 = mine.
- factor_sensitivity figure-by-figure — theft: 1,098.72 / 859.42 / 561.43 / 616.98 / 700.05 / 658.15, baseline_result 1,705.00 — all equal. Valuables: 1,061.36 / 1,749.35 / 1,137.78 / 934.03 / 771.40 / 830.50, baseline_result 2,500.00 — all equal. The GT's stated method-tier comparison (620.46 / 656.98 / 616.98) equals mine.
- Proof-field checks: the design_rationale world assertions on the new rows (2025 claim approved 2025-04-17, reimbursed 565.00 on 2025-04-22, outside the 12-month window; same-stay claim left out of the repeat count; offset 99.0253) agree with the seed and my recomputation. The 565.00 also reproduces under the r2 theft rule at the prior level (Standard), so the seeded history does not contradict the charter.
- Closest alternatives excluded: Premier-type made-whole offset (656.98) — the plan is Plus; counting the same-stay claim in the repeat count (75 % → 501.24) — excluded by "leaving out claims on the same stay"; counting the 2025 reimbursement in the deductible factor (factor 1 → 561.43) — outside "the 12 months before the settlement date".

Round-2 verdict by relationship: policy self-consistency PASS; problem tree PASS; factors PASS (F-G1 and F-G2 closed; every factor bears weight; method floor met); unique solution PASS.

**Task 0 revision_2 verdict: PASS.**

### findings (r2, post-reveal)

- No new defect. Regression check against round 1: the problem tree, persona closure, tools and base gates are unchanged; all round-1 PASS relationships still hold.
- Observations carried: O-T0-1 (extended to the new reactive history line), O-L1, O-L2, O-L3 (softened), O-RC1-3, O-R2-1, O-R2-2. O-T0-2 closed.
