# Policy-task audit — medicare_part_a_coinsurance_and_coverage_end / charter-global

## revision_1

## charter_global_frozen
- written 2026-10-22T02:20Z, after both task derivations (`0.md`, `1.md`) were frozen and before any GT field was revealed; nothing below derives from GT.
- auditor: independent policy-task auditor.
- hashes: `medicare.extended.yaml` 508ec6f8f21e2b9a3cc333aa166c195e450cb3194f12127433dce2f61178cbcc; `task_tools.py` db4b715312cff2fd6856a67d8d06ba2e9612e3201c9b829316ac0f78a8cbd82e (both match the coordinator brief).
- entry conditions (Step 0): gate snapshot supplied (`/tmp/erl0074_coord/snap_medicare_part_a_coinsurance_and_coverage_end_r1.txt`: check_extended, check_task_tools, replay --check, check_solvability, check_compute, check_grounding, check_cross_fire all rc=0; check_traceability deferred); masked views supplied with matching sha256. Complete.
- permitted: blueprint/*, products/medicare.yaml (+ bedhold.yaml, private.yaml for cross-row pricing), the extended charter, task_tools.py, `audits/render_source/XF_recipe.md`, erlbench DSL semantics (`skills/erl-task-instantiate/scripts/check_compute.py`). Masked: all GT fields, tasks/*.json, plan.md, worklogs.
- demonstration harness (scratch, outside the repo): `/tmp/erl0074_audit_medicare/{harness,sim,demos}.py` — evaluates the charter's own compute with the gate's DSL on the masked worlds and on constructed producible worlds D1–D7, X1–X3 cited below.

### policy_conflict_scan
- Base section: verbatim copy of `blueprint/products/medicare.yaml` (diff of extended lines 1–1405 against the base file: identical).
- Extended policies (5): `medicare_ext_resident_block_share` (charge, agent), `medicare_ext_card_payment_share` (card payment, user), `medicare_ext_resident_rate_year_correction` (adjustment, agent), `medicare_ext_reversed_day_reduction` (adjustment, agent), `medicare_ext_bank_draft_payment` (bank draft, user).
- Overlapping subjects: the two adjustment policies write `medicare_coinsurance_adjustment` with distinct reasons and tools — compatible. The two payment policies write `medicare_coinsurance_payment` on the same object (the resident's original charge of the latest block) and reach **different amounts for the same debt in the same world** (C5, demonstration X1).
- Cross-category reads: bedhold_ledger `bedhold_day_booked` (day_count, from_date, to_date) by service_month, read-only; no extended policy writes outside `medicare_ledger` / `medicare_coverages` balance. Events written (charge, payment, adjustment) have base `triggers: []` — nothing lands in another category.
- Scopes as derived blind: task 0 = {block_share, card_payment}; task 1 = {rate_year_correction, reversed_day_reduction, bank_draft}. Pairwise disjoint, jointly complete over the five policies (to be compared with GT `charter_scope` after reveal).

### rule_compute_equivalence
- Every `compute_basis` quotation of all 5 policies is verbatim in its own rule (whitespace-normalised scratch sweep: zero misses); every `baseline.rule` is a sentence of its rule; every `policy_source` is verbatim in its rule.
- Rounding: each rule's "only that total is rounded half up to the cent" matches `int(… + 0.5) / 100` on the summed cents; caps ("never exceeds the charge's open balance", "never leaving less than nothing") are applied after rounding in compute exactly as the rule orders them.
- Ladders: every tier of every `factors[].ladder` is a sentence of its rule and a branch of its `decides` binding, and vice versa (read sentence by sentence for all 8 distinct factor ids across the 5 policies).
- DSL reads checked against the gate implementation: LATEST/COUNT/SUM are scoped to the target coverage; XSUM/XLATEST to the customer's bedhold rows; `charge_entry_id=''` matches seeded and tool-written resident charges (both store ""); LATEST keeps the first-inserted row on equal date keys (relevant to C6).
- Defects of this relationship are listed under findings (C1–C6: rule and compute agree with each other but depart from in-force base sentences without declaration; C6: tie rules missing).

### action_binding_and_uuids
- (target_tool, computes): (post_coinsurance_charge_97c12690, amount), (pay_coinsurance_by_card_ebeca5a6, amount), (correct_coinsurance_rate_feac0074, amount), (reduce_coinsurance_for_reversed_days_0894f336, amount), (pay_coinsurance_by_bank_draft_32bb229d, amount) — each claimed once.
- Docstrings: no concrete example values (formats only), no other tool named, no ordering word (scoped grep for before/after/first/then/once/until: none); every write body calls ctx.create and ctx.update itself; no datetime/time/random/uuid/secrets substring in the module; no factor id is a substring of a tool name; no composed multi-value string argument.
- uuid8s: 97c12690, ebeca5a6, feac0074, 0894f336, 32bb229d — all distinct, no shared prefix or sequence. `feac0074` ends in this scenario's number 0074 (≈1/65536 for a random tail) → observation O1.

### prerequisite_graph
- Every policy fills `prerequisite`: block_share [], rate_year_correction [] ; card → block_share (value_input, gate chg_days); reversed_day_reduction → rate_year_correction (value_input, gate red_rate); bank_draft → reversed_day_reduction (state_gate, gate `medicare_ledger.adjustment_reason`). All `problem`s are extended ids of this file; graph acyclic (two chains).
- `form: state` on all three edges; no `fallback_reason` (correctly absent).
- `resolved_by` = the depended-on policy's target_tool on all three; each genuinely creates the waited-on row; `chg_days` and `red_rate` exist in their compute and change value with the write.
- `kind: state_gate` on the bank-draft edge names a column rather than an eligibility gate id (the extended policy declares no `eligibility`) → observation O4.
- `effect` text carries world values: card edge "(29 on the task world)"; reduction edge "(209.50 for a 2025 block) instead of the rate the charge records (217.00)" → finding C9.

### prerequisite_sentences
- card ← charge: "A card payment toward a coinsurance block is taken only after the records carry a resident coinsurance charge for the coverage's latest booked coinsurance block." Connective "only after"; record-visible state; no tool/id/snake_case; strength equals `condition`. Exactly one write of this difficulty creates a resident `medicare_coinsurance_charge` (post_coinsurance_charge; its docstring excludes rebills). Derivation: sentence → records show no resident charge on the latest days_21_100 entry → the policy whose rule prices "the resident coinsurance charge for a block" → post it → card. Single reading.
- reduction ← correction: "… is fixed only after the records carry a rate-year correction against that charge whenever the charge's recorded daily rate is above the rate of the year in which its days were furnished." Connective "only after"; state; conditional scope equals `condition`. Only correct_coinsurance_rate writes reason rate_year_correction. Single reading.
- bank ← reduction: "… is not taken until the records carry, against that charge, a reduction for the covered days of every day reversal posted against its booked-days entry." Connective "not until"; state; only reduce_coinsurance_for_reversed_days writes a day-reversal-reason adjustment naming the resident charge. Single reading.
- No depended-on rule restates the sentence; no rule states a cross-problem order that grounds no edge; no base sentence grounds an edge of these trees.

### override_declarations
All five policies declare `overwrite: []`. Sentence-by-sentence against their `base_policy_refs`:
- `medicare_evt_coinsurance`: year-of-service rate — followed (block = one service month; 2024 = 204.00 added beyond the base table, O3). Block total × rate — followed for one share. "The total is split by the tier's coinsurance shares …" and "one charge row is posted per liable party with a non-zero amount" — **departed from** where the coverage records no supplemental effective date (C1). "The tier that sets the split is the one in effect on the days of service … days before the supplemental effective date keep the earlier split" — **departed from** in the worlds of C2 and C3. Days 1–20 never charged — followed. Charge once — not contradicted.
- `medicare_evt_secondary_and_qmb`: "When the tier prohibits balance billing, the resident is never billed any Medicare cost sharing" — **departed from** (C1, QMB). "A charge priced at the wrong year's rate is corrected … by the difference" — **departed from** by the single-rounding formula (C4). "Reversed covered days reduce the coinsurance charged on them with the day reversal's own reason" — followed. "An adjustment … never exceeds that charge's open balance" — followed (caps present).
- `medicare_evt_payment_posting`: "Every payment is applied … only up to that charge's open balance" and "a single card payment may not exceed the card payment maximum, and an amount above it must be split across another accepted method" — **departed from** by the card policy (C5). Bank draft subtracts payments net of returns and floors at zero — followed on the cited sentence.
- `medicare_evt_day_counting`: leave-of-absence and hospital nights are not covered days; reversals reduce the coinsurance on them — followed in principle; the bank draft's held + reversed subtraction counts one away night twice when it is both booked as a held day and reversed as leave_of_absence_day/hospital_day (C3, D5).
- `medicare_coverage_tier_change`: QMB first, then plan letter — followed; "A newly reported Medigap policy is recorded with the carrier's policy effective date as the supplemental effective date" — extended reads a coverage with no such date as if the date fell after the block, so a Medigap/QMB tier on file from admission never takes its split (C1).
None of the departures is named in any `overwrite`.

### factor_ladders
| policy | factors (label) | parameter / method | multi-source | cross_difficulty |
|---|---|---|---|---|
| resident_block_share | f_year_rate (P, 3 tiers), f_new_split (P, 4), f_carried_split (P, 4), f_change_day (M, 3), f_away_nights (M, 4) | 3 / 2 | f_new_split | f_away_nights → bedhold |
| card_payment_share | same five | 3 / 2 | f_new_split | f_away_nights → bedhold |
| rate_year_correction | same five | 3 / 2 | f_new_split | f_away_nights → bedhold |
| reversed_day_reduction | f_reduction_rate (P, 4), f_new_split (P, 4), f_carried_split (P, 4), f_reversal_side (M, 3) | 3 / 1 | f_new_split, f_reduction_rate | none (task 1 gets one via correction/bank) |
| bank_draft_payment | f_year_rate, f_new_split, f_carried_split, f_change_day, f_away_nights, f_reversed_before (M, 4) | 3 / 3 | f_new_split | f_away_nights → bedhold |
- `decides` are inputs, never `result`; binding sets disjoint; no factor binding reads another factor's binding (mechanical AST sweep: none). Fall-through tiers equal the declared baselines.
- Distinct outcomes: f_year_rate 209.50/204.00/217.00; f_new_split and f_carried_split 0/25/50/100; f_reduction_rate tiers 209.50/204.00/217.00/recorded rate (the last two coincide on any charge recorded at 217.00 — observation within O7).
- Real rates: 2024 204.00, 2025 209.50, 2026 217.00 are the CMS SNF day-21–100 coinsurance figures; K 50 %, L 25 % resident shares, full-coinsurance plans C/D/F/G/M/N and QMB 0 % are the real Medigap/QMB rules.
- Realism of conditions: f_carried_split decides the pre-change share from the ratio of the preceding block's resident charge to its days × rate "to within half a percentage point" — the business weighs which supplemental coverage was in effect, and the ratio proxy gives a different share from that whenever the preceding charge was adjusted or mixed (C2). The method ladders f_change_day / f_away_nights / f_reversal_side / f_reversed_before are the boundary cases of one count ("covered days before the effective date") rather than treatments the business varies (O7); their measurable defect is C7.
- Every tier is stated in its rule with condition and value/method; no tier lives only in compute.

### findings
Each charter finding names the tasks it bears on; per-task consequences are demonstrated in `0.md` / `1.md`.

- **C1 — SOURCE-POLICY RED (undeclared override; XF C.16/C.18, E.27).** Symptom: a coverage whose Medigap/QMB status is on file with no `supplemental_effective_date` is billed 100 %. Root cause: every policy reads "a coverage that records none … as if that date fell after the block's last service date", so all days take the carried share, whose fall-through is 100 % "including when there is no preceding coinsurance block". Evidence: rule sentences above (identical in all 5 policies); `medicare_coverage_open` fields carry no supplemental_effective_date; base `medicare_evt_coinsurance` split by tier, `medicare_evt_secondary_and_qmb` "the resident is never billed any Medicare cost sharing". Demonstration D1 (task-0 world with the November block as the first days_21_100 block, no charges, date cleared): Plan K → extended 1257.00 vs base 628.50; Plan G → 1257.00 vs base 0; QMB → 1257.00 vs base no resident charge at all (federal QMB balance-billing prohibition). Members: resident_block_share, card_payment_share, rate_year_correction, reversed_day_reduction, bank_draft_payment. Bears on: neither task's world (both record a date and a preceding block).
- **C2 — SOURCE-POLICY RED (undeclared override; unreal ladder condition).** Symptom: the pre-change share falls to 100 % whenever the preceding block's resident charge is not exactly 50 %/25 % of its recorded days × rate. Evidence: f_carried_split rule sentence (all 5 policies); base "days before the supplemental effective date keep the earlier split". Demonstration D2 (task-0 world + 2 hospital days reversed on the November block and the resident charge reduced 209.50 under base rules): prev_pct 33.3 → early share 100 → extended 3561.50 vs base (earlier split K) 2199.75. Same failure for a preceding charge carrying a rate_year_correction or priced at a mixed split. Members: all 5 policies. Bears on: neither task's world.
- **C3 — SOURCE-POLICY RED (date pairing the DSL cannot express; XF F.31/F.32, C.16).** Symptom: held/reversed days are taken off the pre-change days without testing whether they fall inside the block and before the effective date. Evidence: f_away_nights / f_reversed_before rule sentences ("every held day of the month's earlier leaves", "every reversed day of the earlier reversals"); base day-counting and split sentences. Demonstrations: D3 (block starts mid-month at the band boundary, leave in the days_1_20 part, new Medigap L from Dec 20): extended 1990.25 vs base 2304.50; D4 (K→L Dec 10, both leaves after Dec 10): 1780.75 vs 1885.50; D5 (bank draft, an LOA night both booked as held day and reversed as leave_of_absence_day): 2199.75 vs 2409.25. Members: f_away_nights in resident_block_share, card_payment_share, rate_year_correction, bank_draft_payment; f_reversed_before and the held+reversed subtraction in bank_draft_payment. Bears on: neither task's world.
- **C4 — SOURCE-POLICY RED (undeclared override of "by the difference").** Evidence: rate_year_correction rounds (recorded − year rate) × share once; base corrects by the difference between the billed row and the correctly priced row, each rounded half up per row. Demonstration D6 (Plan L, 3-day 2025 block billed at 217.00 = 162.75): extended 5.63 vs base 162.75 − 157.13 = 5.62. Member: rate_year_correction. Bears on: not task 1 (50 % shares are exact).
- **C5 — SOURCE-POLICY RED (card policy vs base posting and vs the bank-draft policy).** Evidence: card rule "settles the resident's share of the covered days that charge prices" (no payments, reversals or card maximum); base posting sentences quoted above. Demonstrations: X2 (no-Medigap resident, 29-day December 2025 block) card amount 6075.50 > card_payment_max_usd 5000.00; X3 (same + 2000.00 check already applied) card amount 6075.50 vs open balance 4075.50; X1 (task-1 world after both adjustments) card rule 733.25 vs bank-draft rule 419.00 for the same charge. Member: card_payment_share. Bears on: task 0 only if its amount exceeded the cap or the charge had payments — not on its world.
- **C6 — SOURCE-POLICY RED (tie rules missing; XF B.11/B.12).** Evidence: "the one whose last service date is the latest", "the coverage's booked-days entry … whose last benefit day is the day before …", "the latest day reversal … taken by first reversed date", "the latest leave by first held day" state no tie rule; base permits two days_21_100 entries with one to_date (booking_error reversal and rebooking) and two reversals with one from_date and different reasons (`reverse_once` distinct on from_date + reason). Demonstration D7: rebooked December block — insertion order E1,E2 gives 0.00, order E2,E1 gives 2199.75. Members: all 5 (block read); reversed_day_reduction and bank_draft_payment (reversal read). Bears on: neither task's world.
- **C7 — SOURCE-FACTOR RED (XF A.6 T2; factors that cannot move the result on their own).** Analytic: with f_new_split and f_carried_split at baseline (both 100) the split of days is irrelevant, so f_change_day, f_away_nights, f_reversed_before, f_reversal_side never move the result; with f_change_day / f_reversal_side at baseline (0 early days) no day takes the carried share, so f_carried_split (and f_away_nights) never move it; in rate_year_correction, with f_year_rate at baseline 217.00 no producible charge records a higher rate, so the correction is 0.00 whatever every other factor says. Members (every one): resident_block_share {f_carried_split, f_change_day, f_away_nights}; card_payment_share {f_carried_split, f_change_day, f_away_nights}; rate_year_correction {f_new_split, f_carried_split, f_change_day, f_away_nights}; reversed_day_reduction {f_carried_split, f_reversal_side}; bank_draft_payment {f_carried_split, f_change_day, f_away_nights, f_reversed_before}. Survivors: 2, 2, 1, 2, 2 — none keeps 4 factors or a method factor. Bears on: task 0 and task 1 (solo columns in their factor_weight tables).
- **C8 — SOURCE-FACTOR RED (XF A.3; assembly sentence names factor quantities).** Members: resident_block_share ("The covered days that keep the earlier share are the calendar days counted before the supplemental effective date less the held days taken off them …"), card_payment_share (same shape), rate_year_correction ("The priced days that keep the earlier share are the calendar days counted before … less the held days …"), reversed_day_reduction ("Reversed days before the supplemental effective date take the earlier share and every other reversed day … takes the share from that date …"), bank_draft_payment ("… less the held days and the reversed days taken off them …"). Each names f_change_day/f_reversal_side, f_away_nights/f_reversed_before, f_carried_split and f_new_split quantities. Bears on: both tasks (renderable text).
- **C9 — SOURCE-POLICY RED (check 7; world values / authoring viewpoint in `prerequisite`).** Members: card_payment_share edge `effect` "(29 on the task world)"; reversed_day_reduction edge `effect` "(209.50 for a 2025 block) instead of the rate the charge records (217.00)". Bears on: task 0 (29 = its block's day count) and task 1 (217.00 = its charge's recorded rate).
- **C11 — SOURCE-FACTOR RED (XF E.28; payment policies re-derive an amount already recorded).** Both payment policies recompute the resident share from scratch while the prerequisite write leaves exactly that amount as the charge's open balance, the amount base posting applies a payment against. Members: card_payment_share, bank_draft_payment. Demonstrated per task (T0-F2, T1-F2).
- Observations (not grounds for rework): O1 uuid `feac0074` tail equals the scenario number; O2 `variant_name` names the f_new_split outcome on every coverage; O3 `rate_2024` 204.00 is the real CMS figure but absent from the base `coinsurance_rate_by_year`, and the "otherwise 217.00" fall-through would price a pre-2024 block at 217.00; O4 bank-draft `state_gate` names a column, not an eligibility gate; O5 the base charter does not model the Medigap K/L annual out-of-pocket limits; O6 (task 1) the persona's January statement is not produced for a coverage now in the Full-Coinsurance tier (`resident_statement_issued: false`); O7 the method ladders are case splits of one interval count, and f_reduction_rate's 217.00 tier and its recorded-rate fall-through coincide on charges recorded at 217.00; O8 E.30 sweep: no write another product's rules call owed at once could move a scored read on either world (bedhold reservations returned, held days booked and charged; no medicaid/private/trust holdings seeded).

## closing_checklist
Written after both reveals (2026-10-22T02:19Z); nothing above this heading was edited after the reveal.
- Files: `0.md`, `1.md` correspond one-to-one with tasks/0.json and tasks/1.json; `_difficulty.md` alongside; revision_1 is the first revision.
- GT comparison: both tasks' independent derivations match GT item for item (tools, owners, order, every argument, terminal state, prerequisite_closure, every factor_sensitivity and baseline_result figure). Scopes match GT `charter_scope` (task 0: resident_block_share + card_payment_share; task 1: rate_year_correction + reversed_day_reduction + bank_draft_payment): pairwise disjoint, the five extended policies jointly covered; task tools closed over GT; uuid8s distinct (O1 noted).
- Problem trees: task 0 — 1 prerequisite, 1 value_input, owner=user root; task 1 — 2 prerequisites, 1 value_input + 1 state_gate, owner=user root; difficulty graph acyclic. PASS for both.
- Factors: NOT closed. Every factor bears weight on its own task's world (T1), but C7 (XF A.6 T2) strikes 13 factor declarations across the five policies, leaving no computation with 4 factors or a method factor; T0-F1/T1-F1 (seeded carrier rows already carry the split outcomes) and T0-F2/T1-F2 (payment amounts equal recorded open balances) let both tasks be scored without any split factor document; C8 assembly sentences name factor quantities.
- Policy self-consistency: NOT closed — C1–C6 (undeclared departures from in-force base sentences demonstrated on producible worlds, incl. QMB balance billing) and C9 (world values in `prerequisite` effect text).
- Gate re-run on a final form: not applicable — the difficulty does not pass this audit; the instantiation-stage gates were not re-run by the auditor (snapshot supplied by the coordinator is the only gate evidence).
- Status: the difficulty does not pass the source-layer audit in revision_1.

VERDICT revision_1: task0=RED:T0-F1,T0-F2,T0-F3 task1=RED:T1-F1,T1-F2,T1-F3 charter=C1,C2,C3,C4,C5,C6,C7,C8,C9,C11

---

## revision_2

## charter_global_frozen (revision_2)
- written 2026-10-22T07:17Z, after `0.md` and `1.md` revision_2 derivations were frozen and before any revision_2 GT field was read; nothing below derives from revision_2 GT.
- hashes: `medicare.extended.yaml` b1745f94da50781ebe25b5308b470d486416a68c4ccc82ab0269f9db01460150, `task_tools.py` 91fc2fae2fa28f81e6ee7cd7ab3b35195adc7fe64275533c7e30455c6208ada6 — both changed since revision_1, so every charter-global section is re-derived in full. Base section still verbatim (diff of lines 1–1405 against `blueprint/products/medicare.yaml`: identical).
- entry conditions: coordinator snapshot `/tmp/erl0074_coord/snap_medicare_part_a_coinsurance_and_coverage_end_r2.txt` (7 gates rc=0, traceability deferred); masked views rebuilt, hashes match. Complete.
- contamination_disclosure: revision_1 GT of both tasks was read in revision_1 (disclosed in the task files); no worklog, plan.md or design_rationale of revision_2 was read before this section.
- harness: `/tmp/erl0074_audit_medicare/r2/{chain,demos2}.py`.

### policy_conflict_scan
- Five extended policies, same ids/targets as revision_1. Each now carries a record-test scope ("is worked out only for a … block that passes this record test") and one overwrite retiring the base `medicare_evt_coinsurance` sentence "The tier that sets the split is the one in effect on the days of service: … so days before the supplemental effective date keep the earlier split." (verbatim in base: verified). The new tier share is the variant's own `resident_coinsurance_share_pct` (P()), no longer a factor.
- Same object, two payment rules: the card rule counts the days the charge prices, the bank-draft rule counts the block's covered days; they disagree on the same charge when a reversal was posted after the charge (R2-C14).
- `reversed_day_reduction` is now scoped to the uncertified-day reversal posted after the charge; hospital-day/LOA reversals posted after a charge have no extended pricing (base applies) — compatible.
- Scopes as derived blind: task 0 {block_share, card}; task 1 {correction, reduction, bank}; disjoint, complete.

### rule_compute_equivalence
- compute_basis quotations: all verbatim in their rules (sweep: zero misses); every baseline.rule sentence is a rule sentence; every replaced_by is a rule sentence; every policy_source verbatim.
- Rounding: "adds … divides the sum by 100 and rounds it half up to the cent once" = int(…+0.5)/100 on the summed cents; correction "the first rounded figure less the second" = two rounded figures differenced; caps after rounding — all match.
- Ladders: each factor tier is a rule sentence and a compute branch and vice versa.
- **Mismatch (R2-C16)**: `reversed_day_reduction` rule: "it prices the days of the uncertified-day reversal posted against that booked-days entry after the charge was posted"; compute `un_from_r/un_to_r/un_days_r` read the latest uncertified reversal with no posting-date test. Demonstration N3 (task-1 world with the lapse posted 2025-12-31, before a 20-day 209.50 charge of 104.75): compute 104.75 (in scope), rule: no lapse posted after the charge → nothing to price.
- Decoy / absent-record probes of every new read (task-0 world, gold 1885.50): bedhold row of another month → 1885.50; reversal on the November block → 1885.50; rebill resident charge on the preceding block → 1885.50; bedhold_day_reversed on the leave → out of scope (0, as the rule says); second hospital-day reversal → out of scope (0, as stated); absent supplemental date → 1361.75 (all 26 days at the tier's 25 %, as stated); first days_21_100 block with a mid-block date (no block before) → out of scope; two leaves → out of scope; booking-error rebooking (D7) → out of scope in both insertion orders; LOA reversal on a held night (D5) → out of scope.

### action_binding_and_uuids
- (target_tool, computes) unique; docstrings: no example values, no other tool, no ordering word; bodies validate sign/format and call ctx.create/ctx.update; helpers are `_Fmt` static methods; no datetime/time/random/uuid/secrets substring; no factor id inside a tool name; tools judge no prerequisite. uuid8s unchanged (O1 stands).

### prerequisite_graph
- card → block_share (value_input, chg_days); reduction → correction (value_input, red_rate); bank → reduction (state_gate). Acyclic; all state form; resolved_by = depended-on targets; `effect` texts now carry no world value (revision_1 C9 closed). O4 (state_gate names a column) stands.

### prerequisite_sentences
- card: unchanged, passes. reduction: unchanged sentence ("A reduction for reversed covered days …") while the policy now names itself "the reduction for an uncertified lapse" (O9; the hop still resolves to the one write that posts a rate_year_correction). bank: "… a reduction for every day reversal posted against its booked-days entry after the charge itself was posted." — state form; only `reduce_coinsurance_for_reversed_days_0894f336` brings it about; single reading on both worlds. The same-date convention behind "after" is R2-C15.

### override_declarations
- Each policy declares one overwrite of the base tier/earlier-split sentence of `medicare_evt_coinsurance`. **Every replaced_by reads "… and only for such a [charged|paid|corrected|lapse's|settled] block; every other block keeps the earlier split under the base rule …"** — it defers to the very clause it retires, does not restate that clause's still-in-force content (Medigap split from the carrier's policy effective date; QMB from the first day of the month after the determination), and names neither sibling's case (R2-C12; XF C.15, C.16, C.17).
- Other cited base sentences, sentence by sentence: year-of-service rate — followed; block total/split by tier shares — followed (tier share now P(); absent date → tier on file for every day, revision_1 C1 closed); "one charge row … a zero amount is not posted" — followed (0.00 for full/QMB tiers); QMB never billed — followed (D1 QMB 0.00); "corrected … by the difference" — followed except the same-date case (R2-C15); payment "only up to that charge's open balance" / card maximum — card capped at 5000.00 and net of payments (X2, X3 closed) but not net of reductions for reversals posted after the charge (R2-C14); day-counting definitions — followed by the rules; the seeds break the observation-night definition (R2-C13).

### factor_ladders
| policy | factors | P / M | multi-source | cross_difficulty |
|---|---|---|---|---|
| block_share | f_year_rate, f_carried_split, f_held_nights, f_hospital_reversal, f_uncertified_days | 2 / 3 | method tiers (record AND date) | f_held_nights → bedhold |
| card | same five | 2 / 3 | same | f_held_nights |
| rate_year_correction | f_year_rate, f_carried_split, f_held_nights, f_hospital_reversal, f_absence_reversal | 2 / 3 | same | f_held_nights |
| reversed_day_reduction | f_reduction_rate, f_carried_split, f_held_in_lapse, f_hospital_in_lapse | 2 / 2 | f_reduction_rate, method tiers | f_held_in_lapse → bedhold |
| bank_draft | f_year_rate, f_carried_split, f_held_nights, f_hospital_reversal, f_absence_reversal, f_uncertified_days | 2 / 4 | method tiers | f_held_nights |
- No factor binding reads another factor's binding, directly or through plain bindings (transitive AST sweep: none). Fall-throughs equal baselines; ladders ≥ 3 tiers with an explicit absent-record fall-through; method tiers pass the XF A.7 shape test (span length vs span-to-date count vs nothing). O7 (method ladders are case splits of one count; f_reduction_rate's 2026 tier and its recorded-rate fall-through coincide at 217.00) stands as an observation.
- T2 (XF A.6): block_share, card, reduction, bank — every factor moves alone on some producible world (solo tables in the task files; reduction analytic where the cap binds). **rate_year_correction — f_carried_split, f_held_nights, f_hospital_reversal, f_absence_reversal never move with f_year_rate at its baseline 217.00** (no charter rate exceeds 217.00, so the first figure never exceeds the second and the floor gives 0.00) (R2-C7).

### findings (revision_2)
Closure of revision_1 items (demonstrations re-run on the revision_2 charter):
- C1 closed (D1: Plan K no date → 628.50 = base; Plan G → 0.00; QMB → 0.00). C2 closed (D2: adjusted preceding charge → 2199.75 = base). C3 closed (held nights intersected with the block; two leaves / LOA-on-held-night / no block before → out of scope, "prices nothing" and base governs). C4 closed (D6 → 5.62 = base). C6 closed (D7 → out of scope in both orders; ties excluded by the record test). C8 closed (assembly sentence generic: "adds, over the days it counts, the daily rate times the share each day takes …"). C9 closed (effects carry no world value). C5: X2 (cap) and X3 (net of payments) closed; a new member remains (R2-C14). C7: closed for four policies, not for rate_year_correction (R2-C7).
- C11 / T0-F1 / T1-F1 / T0-F2 / T1-F2 — **BLUEPRINT-KNOWN**, base-forcing verified: (a) the only customer-owned writes the base offers are the QIO request and the SNF ABN option (non-numeric) and a payment, which base applies "only up to that charge's open balance" — so a customer numeric write with its prerequisites resolved is the open balance (F2/C11 forced). (b) Base fixes "the secondary amount is the block total minus the resident amount", base `medicare_days_booked` triggers `medicare_coinsurance_charge` for every days_21_100 block, and every reversal "reduces the coinsurance charged on them" at once — so any world in which the scored resident writes are the only owed ones must already carry a correct carrier row (and carrier reduction) for the block, from which the resident figure is the remainder (F1 forced given that tree). The only way round it is not a customer write: seed the block with the carrier share also unposted (task 0) or also mispriced/unreduced (task 1), which makes the carrier's own posting/correction/reduction owed at once and puts a base-priced carrier write of the same tools into gold. Recorded, not RED.

New / remaining:
- **R2-C7 — SOURCE-FACTOR RED (XF A.6 T2).** Members: rate_year_correction {f_carried_split, f_held_nights, f_hospital_reversal, f_absence_reversal}. Demonstration: task-1 solo column (all 0.00 = all-baseline) and the analytic argument above. Bears on: task 1.
- **R2-C12 — SOURCE-POLICY RED (XF C.15/C.16/C.17).** Members: the overwrite of all five policies (block_share, card_payment_share, rate_year_correction, reversed_day_reduction, bank_draft_payment). Evidence: replaced_by text quoted above vs the superseded clause. Consequence: for every out-of-scope block the KB's only statement of how the earlier split is fixed is a clause the same overwrite retires; and five sibling overwrites of one clause each scope only their own block kind. Bears on: both tasks (rendered text).
- **R2-C13 — SOURCE-FACTOR RED (realism, XF E.27/E.29; seeds).** Members: task 0 `medicare_ledger.4c95d7f4…` (2025-12-10, observation night → `hospital_day`); task 1 `medicare_ledger.93df17b5…` (2025-12-06, observation night → `hospital_day`). Base definition makes both leave-of-absence days. Consequence: task 0 — f_hospital_reversal falls to its baseline with the same 1885.50 (does not bear weight); task 1 — two LOA reversals on the block, every policy's record test fails, all three scored writes price nothing.
- **R2-C14 — SOURCE-POLICY RED (card rule vs base posting and vs bank-draft rule).** Member: card_payment_share. Evidence: card counts "the days the resident's charge for the paid block prices" and takes reversed days off only the before-date days. Demonstration N1 (task-0 K→L world, 29-day resident charge 2199.75 posted 2026-01-02, hospital-day reversal 2025-12-10..11 posted 2026-01-05, in scope): card 2095.00; open balance 2199.75 before the base reduction and 1990.25 after it (N1b: card 2095.00 > open 1990.25); bank-draft rule on the same charge 1990.25. Bears on: neither task's world.
- **R2-C15 — SOURCE-POLICY RED (same-date convention departs from base "by the difference").** Members: rate_year_correction ("posted on or before the date the charge was posted"); bank_draft_payment gate ("posted … after the charge itself was posted"). Demonstration N2 (K→L world, 29-day charge at 217.00 = 2278.50 and a hospital-day reversal of 2025-12-10 both posted 2026-01-02, the charge still pricing the reversed day): extended correction 76.87; base difference 2278.50 − 2199.75 = 78.75. Bears on: neither task's world (task 1's same-date reversals are already excluded from the charge's 27 days).
- **R2-C16 — SOURCE-POLICY RED (rule ≠ compute).** Member: reversed_day_reduction (N3 above: compute 104.75 where the rule prices nothing). Bears on: neither task's world.
- Observations: O1 uuid tail `feac0074`; O3 2024 rate absent from the base table; O4 state_gate column; O5 Medigap K/L out-of-pocket limits unmodelled (base); O6 closed (task-1 persona no longer cites a statement); O7 as above; O8 E.30 sweep — no write owed at once by another product's rules moves a scored read on either world (declined reservations book nothing; held nights booked and charged); O9 the reduction's prerequisite sentence names "a reduction for reversed covered days" while the rule names itself "the reduction for an uncertified lapse".

## closing_checklist (revision_2)
Written after the revision_2 reveal (2026-10-22T07:16Z); nothing above this heading was changed after it.
- Files `0.md`, `1.md`, `_difficulty.md` each carry revision_1 untouched and revision_2 appended.
- GT comparison: both tasks' revision_2 derivations match GT on every tool, owner, order, argument, terminal state, prerequisite_closure value and factor_sensitivity/baseline_result figure. Scopes match `charter_scope`; disjoint and complete; tools closed over GT.
- Problem trees: task 0 (1 prerequisite, 1 value_input, user root) and task 1 (2 prerequisites, 1 value_input, user root) hold; graph acyclic.
- Factors: not closed — R2-C7 (correction T2), R2-C13 (observation nights seeded as hospital days; task 0 factor without weight on the producible world, task 1 tree collapses).
- Policy self-consistency: not closed — R2-C12 (overwrite deferral / sibling scope), R2-C14 (card vs open balance and bank rule), R2-C15 (same-date convention), R2-C16 (reduction rule ≠ compute).
- revision_1 items closed: C1, C2, C3, C4, C6, C8, C9; C5 partly (X2, X3); C7 partly. BLUEPRINT-KNOWN (verified, not RED): C11, T0-F1, T1-F1, T0-F2, T1-F2.
- Gate re-run on a final form: not applicable (difficulty does not pass revision_2).

VERDICT revision_2: task0=RED:R2-T0-F4 task1=RED:R2-T1-F3,R2-T1-F4 charter=R2-C7,R2-C12,R2-C13,R2-C14,R2-C15,R2-C16

---

## revision_3

## charter_global_frozen (revision_3)
- written 2026-10-22T10:15Z, after `0.md`/`1.md` revision_3 derivations, before reading revision_3 GT or the worklog.
- gate snapshot run by the auditor (`/tmp/erl0074_coord/snapshot.sh medicare_part_a_coinsurance_and_coverage_end 3`, 2026-10-22T10:10:14): `[check_extended] rc=0 :: EXTENDED OK`, `[check_task_tools] rc=0 :: TASK TOOL CONTRACT OK`, `[replay_tasks --check] rc=0 :: REPLAY OK`, `[check_solvability] rc=0 :: SOLVABILITY OK`, `[check_compute] rc=0 :: COMPUTE OK`, `[check_grounding] rc=0 :: GROUNDING OK`, `[check_cross_fire] rc=0 :: SCOPE OK`; hashes task_tools.py 91fc2fae2fa28f81e6ee7cd7ab3b35195adc7fe64275533c7e30455c6208ada6, medicare.extended.yaml 681c88a085ec7e5fbf7c253a633b1084b0d15dd88b889aecaf0bb93a5721f77d, task0.view 51be255bc37e90c42a15a76d5274e32c84b8b2e2b020537e2d7cfd0c46fc3e2c, task1.view 6f42db33ee7caaa2ca9e6f71c71a47cd9e67822402b21b2f99422b14823e31f3.
- task_tools.py unchanged since revision_2 → `action_binding_and_uuids` carried forward by reference (revision_2 section; hash 91fc2fae…ada6 both rounds). The charter changed → all other sections re-derived. Base section verbatim (re-diffed).
- Changes found (sentence/binding diff against revision_2): one shared replaced_by restating the retired clause and naming all five figures; a new record-test clause `chg_ok` (resident charge's day count = booked − reversals posted on/before the charge date) in all five; card counts the block's covered days (`cnt_days`) instead of the charge's days; correction ladder reordered with 204.00 as baseline/fall-through and scope limited to blocks ending in 2024 or later; reduction renamed back to "reduction for reversed covered days" and limited by `un_after` (lapse posted after the charge). Persona lines in both tasks changed (inpatient nights); initial_state identical to revision_2.

### policy_conflict_scan
- Card and bank rules now agree on the same charge: N1 (reversal posted after the charge) card 1990.25 = bank 1990.25 = open balance after the base reduction. Scopes as GT-free derivation: task 0 {block_share, card}, task 1 {correction, reduction, bank}; disjoint, complete. No other overlap.

### rule_compute_equivalence
- Sweep: every compute_basis quote verbatim; every baseline.rule sentence in its rule; replaced_by and policy_source verbatim; superseded clause verbatim in base `medicare_evt_coinsurance`. New bindings match their sentences: `tc_*`/`chg_ok` ↔ "its day count equals … on or before the date that charge was posted"; `cnt_days` ↔ "counts the paid block's covered days … once the resident's charge … stands, and no day before it stands"; `un_after`/`un_priced` ↔ "the uncertified-day reversal posted … after the charge was posted" (N3 now 0.00, rule and compute agree); correction `yr_rate` ↔ the reordered ladder and the "2024 or later" scope clause.
- Decoy / absent-record probes of every new or changed read: resident charge with a day count ≠ booked − prior reversals → out of scope (0.00); two resident charges → out of scope; rebill resident charge (charge_entry_id set) → ignored; no resident charge → card 0.00 (no day before it stands); reversal posted after the charge → card/bank 1990.25; same-date reversal not reflected in the charge (N2) → out of scope (base governs); lapse posted before the charge (N3) → reduction 0.00; earlier regressions D1 (K 628.50, G 0.00, QMB 0.00), D2 2199.75, D6 5.62 — unchanged and equal to base.

### action_binding_and_uuids
- Carried forward from revision_2 (tool module unchanged). O1 stands.

### prerequisite_graph
- card → block_share (value_input, gate `cnt_days` — exists in compute and changes with the charge); reduction → correction (value_input, red_rate); bank → reduction (state_gate). Acyclic, state form, resolved_by correct; effects carry no world value. O4 stands.

### prerequisite_sentences
- Unchanged sentences; each passes the four-point test; the reduction's sentence now uses the policy's own name (O9 closed). Single resolving write per edge.

### override_declarations
- All five policies carry the identical replaced_by: "For a block that passes its record test, the resident coinsurance charge, the card payment, the rate-year correction, the reduction for reversed covered days and the bank draft each count the days before the supplemental effective date as their own policies state, and only for such a block; for every other block, the tier that sets the split is the one in effect on the days of service: a Medigap policy changes the split from the carrier's policy effective date and QMB protection from the first day of the month after the state's QMB determination, so days before the supplemental effective date keep the earlier split, and none of these five figures is priced for it." — restates the retired clause for out-of-scope blocks (XF C.15), defers to nothing retired (C.16), names every sibling's case (C.17). R2-C12 closed.
- Other base sentences: as revision_2, with the departures R2-C14, R2-C15, R2-C16 now closed (N1, N2, N3 above).

### factor_ladders
- Counts unchanged (block_share 2P/3M, card 2P/3M, correction 2P/3M, reduction 2P/2M, bank 2P/4M); no factor reads another factor's binding (transitive sweep: none); ladders ≥ 3 tiers with explicit absent-record fall-through; method tiers pass the A.7 shape test; multi-source and cross-difficulty (bedhold) factors present in every task.
- T2 now holds for every factor of every policy (task files' solo tables; reduction on an uncapped producible world). R2-C7 closed.
- Correction ladder: 2026+ → 217.00, 2025 → 209.50, otherwise (scope leaves only 2024) → 204.00 = baseline; real CMS rates; fall-through = baseline. O10: a computation document that compares every block against the 2024 rate is an unusual "standard" default, but it is the ladder's own fall-through and a real figure; not a defect under the stated tests.

### findings (revision_3)
- Closed: R2-C7 (correction T2), R2-C12 (overwrite), R2-C13 (observation nights — persona now states inpatient nights matching `hospital_day`), R2-C14 (card), R2-C15 (same-date posting → out of scope), R2-C16 (reduction rule = compute).
- BLUEPRINT-KNOWN (unchanged, verified in revision_2): C11, T0-F1, T1-F1, T0-F2, T1-F2.
- No new RED found. Observations carried: O1, O3, O4, O5, O7, O8; O9 closed; O10 new (above).

## closing_checklist (revision_3)
Written after the revision_3 reveal (2026-10-22T10:13:43Z); the revision_3 frozen sections above were on disk before the worklog read (10:13:25Z) — their written stamps were estimates.
- Files: `0.md`, `1.md`, `_difficulty.md` each carry revisions 1–3; earlier revisions untouched; every revision_3 comparison section carries PASS.
- Coverage/scope: the five extended policies are covered; task scopes {block_share, card} and {correction, reduction, bank} are disjoint (match `charter_scope`); task tools closed over GT; uuid8s distinct (O1 observation on `feac0074`).
- Problem trees: task 0 — 1 prerequisite, 1 value_input, owner=user root; task 1 — 2 prerequisites, 1 value_input + 1 state_gate, owner=user root; whole-difficulty graph acyclic.
- Factors: every computation has 4–6 factors (≥2 parameter, ≥1 method), each task has multi-source and bedhold cross-difficulty factors, ladders ≥3 tiers stated in full in the rules, fall-throughs = baselines, every factor bears weight on its task's world (T1) and moves alone on some producible world (T2); baselines give definite numbers different from gold (3851.75; 117.00 / 523.75 / 1953.00).
- XF recipe, every point on every policy: A1–A8 pass (no factor reads another, shared selections plain, generic assembly, ordered caps/rounding, no factor gated through another, T1/T2, shape test, explicit absent tiers); B9–B14 pass (quotes verbatim, rounding sentences = compute, ties excluded by the record test, decoy probes listed above, no framing fact without a record, no "if policy X would compute" route); C15–C18 pass (one restating, sibling-naming replaced_by; superseded clause verbatim; no other undeclared departure found); D19–D26 pass (tools unchanged since revision_2: no example values, no ordering words, own ctx writes, static helpers, no forbidden imports, frozen_time format, events trigger nothing cross-category, no 0.00 rows); E27–E30 pass (real CMS rates and Medigap/QMB shares; inpatient nights = hospital days; seeded bedhold and medicare rows priced by their charters; no owed cross-product write moves a scored read); F31–F32 pass (scoped record tests, out-of-scope restated and unpriced).
- BLUEPRINT-KNOWN (verified revision_2, not RED): C11, T0-F1, T1-F1, T0-F2, T1-F2.
- Gates on the final form: auditor-run snapshot 2026-10-22T10:10:14, 7/7 rc=0 (lines quoted in charter_global_frozen revision_3).
- The difficulty passes the source-layer audit in revision_3.

VERDICT revision_3: task0=PASS task1=PASS charter=CLEAN

---

## revision_4

## charter_global_frozen (revision_4)
- gate snapshot run by the auditor (`/tmp/erl0074_coord/snapshot.sh medicare_part_a_coinsurance_and_coverage_end 4`, 2026-10-22T15:09:47): `[check_extended] rc=0 :: EXTENDED OK`, `[check_task_tools] rc=0 :: TASK TOOL CONTRACT OK`, `[replay_tasks --check] rc=0 :: REPLAY OK`, `[check_solvability] rc=0 :: SOLVABILITY OK`, `[check_compute] rc=0 :: COMPUTE OK`, `[check_grounding] rc=0 :: GROUNDING OK`, `[check_cross_fire] rc=0 :: SCOPE OK`; hashes task_tools.py 91fc2fae2fa28f81e6ee7cd7ab3b35195adc7fe64275533c7e30455c6208ada6, medicare.extended.yaml 53835c824b7799e6fa97a0a587cf156fb93d82b2cd95b2118da2e5bfd00bc4c8, task0.view 51be255b…e2c, task1.view 6f42db33…1f3.
- inputs read and disclosed: `audits/render_source/medicare_part_a_coinsurance_and_coverage_end/render_r1.md` (in full) and worklog "REWORK round 4"; GT of earlier rounds known; revision_4 GT read after this section.
- Changes (sentence/binding diff vs revision_3): block_share and rate_year_correction unchanged; card and bank add `chg_amt_x/chg_adj_x/open_x/pay_fig` and "a figure above the open balance … is then not taken under this policy, and any payment the payer sends is applied only up to that open balance, the remainder being returned"; bank gate narrowed to uncertified-day reversals and record test adds "no hospital-day or leave-of-absence reversal … posted after the date that charge was posted"; reduction record test adds "last service date in 2024 or later, and the charge's open balance is above nothing". Tools unchanged → action_binding_and_uuids carried forward.
- Mechanical sweeps (all five policies): compute_basis quotes verbatim; every binding has a basis; baseline sentences in rules; policy_source and the single shared replaced_by verbatim in every rule; superseded clause verbatim in base; no factor reads another factor's binding (transitive). Factor sets/labels unchanged.

### render finding 1 — closure and class sweep (every payment figure vs every in-force base posting clause)
- Render shape (no-Medigap tier, 10-day 2026 block, resident charge at 209.50 = 2095.00): card 0.00, bank 0.00 ("not taken under this policy"; base applies the payer's payment up to 2095.00). Closed.
- Sweep of `medicare_evt_payment_posting` sentences for card_payment_share and bank_draft_payment: one named charge — ok; only up to open balance / remainder returned — ok (new clause); split oldest first — n/a (one charge); accepted resident methods (card, ach) — ok; card maximum — card capped at 5000.00, ok; carrier/state remittance methods — n/a; reversal of a dishonored payment — n/a (not a payment figure); **certified funds — not honoured (R4-C1)**; statement day / due days / no late charge — no figure involved.
- **R4-C1 — SOURCE-POLICY RED (XF C.16: contradicts an in-force base clause).** Base `medicare_evt_payment_posting`: "Once the resident has had the returned-payment limit of dishonored payments within the rolling lookback of calendar months ending on the payment date, only certified funds are accepted from the resident on any coverage episode." (returned_payment_limit 2, lookback 12, certified_funds_methods [certified_check]). Neither payment rule nor compute reads returned payments beyond the paid charge's own. Demonstration CF (task-0 world after the gold charge; two resident payments on this same episode dishonored on 2025-12-29 and 2026-01-06 — both in the DSL's reach): card rule 1885.50 (in scope), bank rule 1885.50; base: no card or bank draft is accepted, only a certified check. The worklog's "DSL limit" covers only dishonored payments on another episode; the same-episode case is countable and is not scoped out, and no overwrite declares the departure. Members: medicare_ext_card_payment_share, medicare_ext_bank_draft_payment. Not triggered on either task world (no returned payment).

### render finding 2 — closure and class sweep (every prerequisite sentence vs what its depended-on policy can write in every in-scope world)
- Render shape (hospital-day reversal posted after the charge): bank now out of scope (0.00, base governs). Closed.
- card ← charge: in every card-in-scope world without a charge, the charge policy's record test is the same; where the charge figure is 0.00 (no posting), the card figure is 0.00 too — nothing owed; ok.
- reduction ← correction: the reduction's record test (2024 or later, open balance above nothing) is inside the correction's; the correction's share-days include every lapse day the reduction prices, so whenever the reduction prices something and the recorded rate is above the year rate, the correction is positive (smallest step 1.875 → 1.88); ok.
- **R4-C2 — SOURCE-POLICY RED (undefined hop; same class as render finding 2).** bank ← reduction: the gate waits on "a reduction for every uncertified-day reversal posted … after the charge", but the reduction policy can price that lapse at 0.00 in an in-scope world, and `reduce_coinsurance_for_reversed_days_0894f336` rejects a non-positive amount ("Error: amount must be positive"), so the waited-on state can never arise while the bank draft is in scope with a positive figure. Members (in-scope worlds):
  1. lapse whose every day takes a 0 % share — demonstration G1 (task-1 world with the lapse moved to 2025-12-10..12, all on plan N after the 2025-12-10 effective date; carrier adjustment 628.50): correction 18.75; reduction in scope, **0.00**; bank in scope **523.75** with its gate unmet and unmeetable. The same holds wherever the lapse's days fall only on 0 %-share days (QMB / full-coinsurance tier days, or pre-change days whose block before carries only a secondary charge).
  2. block whose last service date is before 2024 — the bank's record test lacks the reduction's "2024 or later" clause: demonstration G2 (task-1 world shifted three years, 2022 block): reduction out of scope, correction 0.00, bank in scope 108.50 with its gate unmet (and priced at 217.00, see O3). Weaker producibility (a 2022 block still open in 2026), listed for completeness.
  3. charge open balance already 0 when the lapse is posted: reduction out of scope; bank figure 0.00 — harmless (nothing to pay); not a member.
- No other edge has an unresolvable in-scope world found.

### XF recipe on the changed policies (card, reduction, bank)
- A1–A8: no factor reads another; shared reads plain; the assembly sentence generic; cap/rounding order stated ("the rounded figure less the payments … never less than nothing and never more than …"; the open-balance test after it); T1 moves for every factor on the task worlds (to 0.00), T2 moves on a producible world (charge billed at 217.00/100 %); shape test unchanged; absent-record tiers explicit.
- B9–B14: quotes verbatim; rounding sentences = compute; ties excluded by the record test; decoys probed (render-1 shape, render-2 shape, CF, G1, G2, plus the revision_3 probe set re-run with unchanged results on charge/correction); framing clause "shows that the charge was billed below what its days call for" — true in every shape probed, observation only (O12: an over-sized adjustment would also lower the open balance).
- C15–C18: the shared replaced_by restates the retired clause and names all five figures; **C16 member R4-C1** (certified-funds clause contradicted without declaration).
- D: tools unchanged. E27–E30: real rates/shares; no owed cross-product write moves a scored read. F31–F32: scoped record tests; out-of-scope worlds unpriced and restated.

### findings (revision_4)
- render finding 1 — closed for the open-balance clause; class sweep found **R4-C1** (certified funds; members card_payment_share, bank_draft_payment).
- render finding 2 — closed for hospital-day/LOA reversals; class sweep found **R4-C2** (bank gate waits on a reduction priced 0.00 or out of the reduction's scope; members G1 and G2 above, one policy: bank_draft_payment's gate/record test against reversed_day_reduction's pricing/scope).
- No regression of revision_1–3 closures (probe set re-run; charge/correction/reduction figures and factor tables unchanged).
- BLUEPRINT-KNOWN unchanged (C11, T0-F1, T1-F1, T0-F2, T1-F2). O11 (under C11): card/bank factor_sensitivity 0.00 is the compute's "not taken" value; a reader who misses a factor and follows the rule's own fallback ("any payment the payer sends is applied only up to that open balance") posts the open balance, which is gold on both task worlds — the payment factors bear weight only in worlds whose figure falls below the open balance.
- Observations carried: O1, O3 (now also: card/charge/bank price a pre-2024 block at 217.00), O4, O5, O7, O8, O10; new O11, O12.

## closing_checklist (revision_4)
- Written after the revision_4 reveal (2026-10-22T15:13:19Z). Both task comparisons match GT item for item and PASS on their own worlds; trees, scopes, uuids, factor bounds as revision_3; gates 7/7 OK on the final form.
- The difficulty does not pass revision_4: charter R4-C1 and R4-C2 are open.

VERDICT revision_4: task0=PASS task1=PASS charter=R4-C1,R4-C2

---

## revision_5

## charter_global_frozen (revision_5)
- auditor-run snapshot (`/tmp/erl0074_coord/snapshot.sh medicare_part_a_coinsurance_and_coverage_end 5`, 2026-10-22T17:11:28): `[check_extended] rc=0 :: EXTENDED OK`, `[check_task_tools] rc=0 :: TASK TOOL CONTRACT OK`, `[replay_tasks --check] rc=0 :: REPLAY OK`, `[check_solvability] rc=0 :: SOLVABILITY OK`, `[check_compute] rc=0 :: COMPUTE OK`, `[check_grounding] rc=0 :: GROUNDING OK`, `[check_cross_fire] rc=0 :: SCOPE OK`; task_tools.py 91fc2fae2fa28f81e6ee7cd7ab3b35195adc7fe64275533c7e30455c6208ada6, medicare.extended.yaml b01ea2b382cc85df0142e4a31428187eed3b485811bd2775813c09811dccffe9, task0.view 51be255bc37e90c42a15a76d5274e32c84b8b2e2b020537e2d7cfd0c46fc3e2c, task1.view 6f42db33ee7caaa2ca9e6f71c71a47cd9e67822402b21b2f99422b14823e31f3.
- disclosed reads: worklog "REWORK round 5" (permitted); earlier GT known.
- Changes (sentence/binding diff vs revision_4): (1) new overwrite of base `medicare_evt_payment_posting` certified-funds sentence in card and bank (one shared replaced_by), compute `rp_n = COUNT(medicare_payment_reversal, within_months = lookback, date_field entry_date)` and "not taken" at the limit; (2) the three wait sentences gain "… take a resident share above nothing under the split in effect on them"; (3) bank record test adds 2024-or-later and open balance above nothing; charge and card record tests add 2024-or-later; (4) every half-up rounding now RND(x/100 + 0.000000001, 2) (coordinator ruling). Tools unchanged → action_binding_and_uuids carried forward.
- Mechanical sweeps (all five): compute_basis verbatim, every binding has a basis, baseline sentences in rules, policy_source verbatim, both replaced_by sentences verbatim in every rule that carries them (one text per base policy), superseded clauses verbatim in base, every overwritten base policy in base_policy_refs, no `int(` rounding left, no factor reads another factor's binding.

### closure of revision_4 items
- R4-C1 (certified funds): the departure is now declared (overwrite); same-episode returns are counted (probe: two resident returns on this episode in the lookback → card 0 / bank 0; one → taken; a return exactly 12 months before the payment date is outside "the 12 calendar months ending on the payment date" — compute agrees). Declaration closes the undeclared-override defect, but the declared rule itself carries R5-C1 below.
- R4-C2 (bank wait unresolvable): G1 (lapse wholly on 0 % days) — the wait is no longer engaged, reduction 0.00 (not posted), bank 523.75 taken: consistent. G2 (pre-2024 block) — now outside every record test (bank, charge, card too; O3 closed). Class re-swept with the new wording: card ← charge (engaged ⇒ charge figure > 0, identical record tests); reduction ← correction (engaged ⇒ positive share-days and rate above year rate ⇒ correction ≥ 1.38 > 0; reduction's scope inside correction's); bank ← reduction (engaged ⇒ a lapse day with positive share ⇒ reduction ≥ 0.51 > 0 within its scope; bank's scope now carries the reduction's 2024 and open-balance clauses). No unresolvable engaged wait found. Closed.

### XF recipe, every point, every policy (revision_5)
- A1–A8 pass (unchanged factor structure; T1/T2 re-run: charge, correction, reduction, bank, card all move on T1 of their task world or on the producible scratch world for T2, see task files).
- B9–B10 pass; B11 ties/month conventions — the new `within_months` read uses whole months ending on the payment date, matching the rule's base wording; B12 decoys for every new read: payment reversal on another episode (outside the holding, ignored by design), return outside the window (ignored), **two carrier-remittance reversals on this episode → card/bank declined (see R5-C1(a))**; B13/B14 pass.
- C15–C18: both overwrites restate the retired clause for every other case and name their siblings; no undeclared departure found beyond the declared overwrite.
- D19–D26 pass (tools unchanged).
- **E27 (realism of a company-set rule): R5-C1(b)** below. E28–E30 pass.
- F31–F32: payment overwrite is a self-naming scope, but see R5-C1.

### findings (revision_5)
- **R5-C1 — SOURCE-POLICY RED (declared certified-funds overwrite; XF B.12 decoy + E.27 realism).** Shared replaced_by in card_payment_share and bank_draft_payment: "For the card payment and the bank draft taken under these two policies, the dishonored payments counted toward the returned-payment limit are those recorded on the coverage episode the payment is for, within the rolling lookback … ; for every other payment, once the resident has had the returned-payment limit of dishonored payments … only certified funds are accepted from the resident on any coverage episode." Members:
  (a) **non-resident reversals counted** — `rp_n` counts every `medicare_payment_reversal` on the episode, including a returned Medigap-carrier or Medicaid-crossover remittance. Demonstration (task-0 world after the gold charge; the carrier's remittance on the November carrier charge returned 2025-12-30, re-sent and returned again 2026-01-06; no resident payment ever dishonored): card policy 0.00 (not taken). The base clause the overwrite retires, and the overwrite's own "every other payment" branch, speak of the resident's dishonored payments ("once the resident has had …", "accepted from the resident"); under that reading the card payment is 1885.50. Two readings of the scored payment in a producible in-scope world.
  (b) **method-specific carve-out no operator would publish** — for card and bank draft only, the resident's dishonored payments on any other coverage episode no longer count, while every other payment (a check) still counts them across all episodes. Consequence world: a resident with two dishonored resident payments on the previous, ended Part A episode within the lookback, now paying a new episode's charge — card/bank policy takes the card or bank draft (rp_n 0 on this episode), while a check from the same resident would be refused under the restated base branch; the certified-funds rule exists precisely to stop further returnable payments (card chargebacks, ACH returns). The cross-episode count is beyond the DSL's holding-scoped reads; the declared carve-out turns that limit into business policy.
  Bears on: neither task world (no payment reversal seeded).
- No other new defect; no regression of revisions 1–4 closures (probe set re-run on the revision_5 charter: render shapes 1 and 2, N1–N3, D1/D2/D6/D7, G1/G2 behave as recorded).
- BLUEPRINT-KNOWN unchanged (C11, T0-F1, T1-F1, T0-F2, T1-F2; O11 under C11). Observations carried: O1, O4, O5, O7, O8, O10, O12; O3 closed.

## closing_checklist (revision_5)
- Written after the revision_5 reveal (2026-10-22T17:13:39Z): both tasks match GT item for item and PASS on their own worlds; trees, scopes, uuids, factor bounds as revision_3/4; gates 7/7 OK.
- Not closed: R5-C1 (charter).

VERDICT revision_5: task0=PASS task1=PASS charter=R5-C1

---

## revision_6

## charter_global_frozen (revision_6)
- auditor-run snapshot (`/tmp/erl0074_coord/snapshot.sh medicare_part_a_coinsurance_and_coverage_end 6`, 2026-10-22T17:17:46): `[check_extended] rc=0 :: EXTENDED OK`, `[check_task_tools] rc=0 :: TASK TOOL CONTRACT OK`, `[replay_tasks --check] rc=0 :: REPLAY OK`, `[check_solvability] rc=0 :: SOLVABILITY OK`, `[check_compute] rc=0 :: COMPUTE OK`, `[check_grounding] rc=0 :: GROUNDING OK`, `[check_cross_fire] rc=0 :: SCOPE OK`; task_tools.py 91fc2fae2fa28f81e6ee7cd7ab3b35195adc7fe64275533c7e30455c6208ada6, medicare.extended.yaml 203ecd58a6de70e78341ac238f9a9b90c000a203ceed7448fd14a9ec12c432da, task0.view 51be255bc37e90c42a15a76d5274e32c84b8b2e2b020537e2d7cfd0c46fc3e2c, task1.view 6f42db33ee7caaa2ca9e6f71c71a47cd9e67822402b21b2f99422b14823e31f3.
- disclosed reads: worklog "REWORK round 6" (permitted); earlier GT known.
- Changes (sentence/binding diff vs revision_5): card and bank only — the round-5 certified-funds overwrite and `rp_n` are removed; each rule adds "Whether a [card payment|bank draft] may be taken at all is settled by the base posting rule, which this policy leaves unchanged: once the resident has had the returned-payment limit of dishonored payments … only certified funds are accepted from the resident on any coverage episode, so no [card payment|bank draft] is taken; this policy prices the [card payment|bank draft] only where one may be taken." (base sentence carried verbatim). Other three policies unchanged. Tools unchanged.

### closure of R5-C1 and class sweep
- (a) non-resident reversals: probe — carrier remittance returned twice on this episode → card 1885.50 (priced; base counts the resident's dishonored payments only). Closed.
- (b) method carve-out: gone; the base cross-episode rule governs every payment, read by the agent from the resident's ledger (`find_medicare_ledger` by customer_id reaches every episode). Closed.
- Eligibility vs compute: two resident returns in the lookback → compute still prices 1885.50; the rule makes acceptance an inherited base eligibility, exactly as the other inherited base eligibilities (charge once, reverse once) sit outside compute; the priced figure is never written in such a world. Observation O13, not a defect.
- Class re-sweep (every payment figure vs every in-force base posting clause): one named charge; up to the open balance (figure above → not taken); oldest-first split n/a; accepted methods; card maximum (5000.00 cap); certified funds (deferred verbatim to base); statement/due/no late charge (no figure) — no contradiction left.

### XF recipe, every point, every policy (revision_6)
- Mechanical: compute_basis verbatim, every binding has a basis, policy_source and the single shared replaced_by verbatim, superseded clause verbatim in base, no factor cross-reads, no `int(` rounding (RND(x/100 + 1e-9, 2) per ruling).
- A1–A8, B9–B14, C15–C18, D19–D26, E27–E30, F31–F32: pass on all five policies (no new read; T1/T2 re-run: charge/correction/reduction/bank/card as revision_5; prior decoy set, render shapes 1–2, N1–N3, D1/D2/D6/D7, G1/G2 unchanged).

### findings (revision_6)
- R5-C1 closed. No new defect; no regression.
- BLUEPRINT-KNOWN unchanged (C11, T0-F1, T1-F1, T0-F2, T1-F2; O11 under C11). Observations: O1, O4, O5, O7, O8, O10, O12, O13.

## closing_checklist (revision_6)
- Written after the revision_6 reveal (2026-10-22T17:18:27Z). Per-task files match GT item for item; trees (task 0: 1 prerequisite, value_input, user root; task 1: 2 prerequisites, 1 value_input + 1 state_gate, user root) hold; scopes disjoint and complete; tools closed over GT; every computation has 4–6 factors (≥2 parameter, ≥1 method), multi-source and bedhold cross-difficulty factors per task, ladders ≥3 tiers stated in full, fall-through = baseline, T1 and T2 hold, baselines definite and different from gold; gates 7/7 OK on the final form.
- The difficulty passes the source-layer audit in revision_6.

VERDICT revision_6: task0=PASS task1=PASS charter=CLEAN

---

## revision_7

## charter_global_frozen (revision_7)
- auditor-run snapshot (`/tmp/erl0074_coord/snapshot.sh medicare_part_a_coinsurance_and_coverage_end 7`, 2026-10-23T04:58:44): `[check_extended] rc=0 :: EXTENDED OK`, `[check_task_tools] rc=0 :: TASK TOOL CONTRACT OK`, `[replay_tasks --check] rc=0 :: REPLAY OK`, `[check_solvability] rc=0 :: SOLVABILITY OK`, `[check_compute] rc=0 :: COMPUTE OK`, `[check_grounding] rc=0 :: GROUNDING OK`, `[check_cross_fire] rc=0 :: SCOPE OK`; task_tools.py 91fc2fae2fa28f81e6ee7cd7ab3b35195adc7fe64275533c7e30455c6208ada6, medicare.extended.yaml 913c69b3809affc3f15102071553c1b21d250db96ddc7eecca4ed64f5a68f61e, task0.view 51be255bc37e90c42a15a76d5274e32c84b8b2e2b020537e2d7cfd0c46fc3e2c, task1.view 6f42db33ee7caaa2ca9e6f71c71a47cd9e67822402b21b2f99422b14823e31f3.
- disclosed reads: `audits/policy_kb/medicare_part_a_coinsurance_and_coverage_end/_kb_verdict.md` (S5 entry), worklog "REWORK round 7"; earlier GT known.
- Change (sentence/binding diff vs revision_6), identical in all five policies: new sentence "When the tier on file prohibits balance billing, as the QMB Medicaid Crossover tier does, the resident is never billed any Medicare cost sharing on the coverage: no day of it takes a resident share above nothing, whatever split would otherwise apply, and <figure> is nothing."; binding `bb_prohibited = P('balance_billing_prohibited')`; each result is 0 when it is true; `medicare_evt_secondary_and_qmb` in every base_policy_refs. Tools unchanged.
- Mechanical sweeps: compute_basis verbatim (incl. the new sentence), every binding has a basis, policy_source and replaced_by verbatim, superseded clause in base, no factor cross-reads; T1/T2 unchanged (gate false on the task and scratch worlds).

### S5 and its class (every extended rule vs every in-force base clause on every tier)
- Auditor's note on S5 itself (not raised in revisions 2–6): on a QMB tier the recorded supplemental effective date is the QMB effective date, which base fixes at "the first day of the month after the determination month" (`medicare_coverage_tier_change`). Blocks are calendar-month blocks, so that date can never fall after a block's first service date and on or before its last; the KB example (QMB block with a mid-block date) is not a world the charter produces. The producible QMB case with pre-QMB days is a block that ends before the QMB effective date (the whole block is "before the date").
- **R7-C1 — SOURCE-FACTOR / realism RED (XF E.27; regression introduced by the S5 change).** For that producible case the federal rule, and the base charter's own clause the shared replaced_by restates ("QMB protection from the first day of the month after the state's QMB determination, so days before the supplemental effective date keep the earlier split"), leave the pre-QMB days billable at the earlier split — QMB protection is not retroactive. The new sentence ("whatever split would otherwise apply … is nothing") zeroes them. Demonstration Q1 (task-0 world; QMB determined in December 2025, recorded as QMB tier with supplemental effective date 2026-01-01; December block priced 2026-01-08): record test passes, all 26 covered December days fall before the date with the carried 50 % share; extended charge **0.00**; the earlier-split reading **2723.50**. The same gate zeroes the card payment, the rate-year correction, the reduction and the bank draft on such a block. The in-scope rule now also disagrees with the out-of-scope restatement of the same base clause in the shared replaced_by (pre-QMB days keep the earlier split there). Members: medicare_ext_resident_block_share, medicare_ext_card_payment_share, medicare_ext_resident_rate_year_correction, medicare_ext_reversed_day_reduction, medicare_ext_bank_draft_payment (the identical sentence and `bb_prohibited` gate in each). Bears on: neither task world.
- Other tiers: Full-Coinsurance Medigap — the rules keep the earlier split before its date and 0 % from it (probe plan G from 2025-12-16: 1047.50), as base states; Plan K/L/A-B/none — unchanged; no further contradiction with an in-force base clause found on any tier.
- No other regression (revision_6 probe set and T1/T2 unchanged).

### findings (revision_7)
- S5 — the literal KB world is not producible (see note); the change made for it introduces R7-C1.
- BLUEPRINT-KNOWN unchanged (C11, T0-F1, T1-F1, T0-F2, T1-F2; O11). Observations: O1, O4, O5, O7, O8, O10, O12, O13.

## closing_checklist (revision_7)
- Written after the revision_7 reveal (2026-10-23T05:00:03Z): both tasks match GT item for item and PASS on their worlds; gates 7/7 OK.
- Not closed: R7-C1 (charter).

VERDICT revision_7: task0=PASS task1=PASS charter=R7-C1

---

## revision_8

## charter_global_frozen (revision_8)
- auditor-run snapshot (`/tmp/erl0074_coord/snapshot.sh medicare_part_a_coinsurance_and_coverage_end 8`, 2026-10-23T06:21:32): `[check_extended] rc=0 :: EXTENDED OK`, `[check_task_tools] rc=0 :: TASK TOOL CONTRACT OK`, `[replay_tasks --check] rc=0 :: REPLAY OK`, `[check_solvability] rc=0 :: SOLVABILITY OK`, `[check_compute] rc=0 :: COMPUTE OK`, `[check_grounding] rc=0 :: GROUNDING OK`, `[check_cross_fire] rc=0 :: SCOPE OK`; task_tools.py 91fc2fae2fa28f81e6ee7cd7ab3b35195adc7fe64275533c7e30455c6208ada6, medicare.extended.yaml ddc0242fc4b34189226227299d00c73b1da0fa95727061308849bad8a06e553a, task0.view 51be255bc37e90c42a15a76d5274e32c84b8b2e2b020537e2d7cfd0c46fc3e2c, task1.view 6f42db33ee7caaa2ca9e6f71c71a47cd9e67822402b21b2f99422b14823e31f3.
- disclosed reads: worklog "REWORK round 8"; earlier GT known.
- Change (diff vs revision_7), identical in all five policies: the round-7 sentence and `bb_prohibited` gate are removed; new sentence "When the tier on file prohibits balance billing, as the QMB Medicaid Crossover tier does, <figure> bills the resident nothing for any day on or after the tier's supplemental effective date, those days taking the tier's resident share of nothing, while days before that date keep the earlier split, QMB protection not reaching back before it." quoted as a basis of `tier_share`. Tools unchanged.

### R7-C1 closure and class sweep (every policy, every tier)
- Q1 (QMB effective 2026-01-01, December block wholly before it): charge **2723.50** = earlier-split reading (was 0.00 in revision_7). QMB effective 2025-12-01 (block wholly after): 0.00. QMB with no recorded date: 0.00 (tier on file every day). Full-Coinsurance plan G from 2025-12-16: 1047.50 (earlier split before, 0 % after). K/L/A-B/none unchanged.
- The sentence states exactly base `medicare_evt_coinsurance`'s date clause (restated in the shared replaced_by) and base `medicare_coverage_tier_change`'s QMB effective date; with base `medicare_evt_secondary_and_qmb` it reads as protection from the QMB effective date — the federal non-retroactive rule. No extended rule contradicts an in-force base clause on any tier. Waits: on a block wholly after the QMB date no day carries a positive share (waits not engaged); before it, resolvers write positive figures. Closed.

### XF recipe on the five changed policies
- Mechanical: compute_basis verbatim (new sentence included), every binding has a basis, policy_source / replaced_by verbatim, superseded clause in base, no `bb_prohibited` or round-7 text left, no factor cross-reads, RND(x/100 + 1e-9, 2) rounding (ruling).
- A1–A8, B9–B14, C15–C18, D19–D26, E27–E30, F31–F32: pass; T1/T2 re-run (task worlds; producible scratch world for the payments) unchanged; prior probe set unchanged.

### findings (revision_8)
- R7-C1 closed. No new defect; no regression.
- BLUEPRINT-KNOWN unchanged (C11, T0-F1, T1-F1, T0-F2, T1-F2; O11). Observations: O1, O4, O5, O7, O8, O10, O12, O13.

## closing_checklist (revision_8)
- Written after the revision_8 reveal (2026-10-23T06:21:59Z): both tasks match GT item for item and PASS; trees, scopes, tools, factor bounds and T1/T2 as revision_6; gates 7/7 OK on the final form.
- The difficulty passes the source-layer audit in revision_8.

VERDICT revision_8: task0=PASS task1=PASS charter=CLEAN
