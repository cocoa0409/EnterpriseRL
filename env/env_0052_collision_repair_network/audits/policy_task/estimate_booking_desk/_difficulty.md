# Policy-task audit — estimate_booking_desk / charter-global

## charter_global_frozen

- Revision 1. Charter-global section last written 2026-10-11 01:53:58 UTC (file mtime), after both task derivations (`0.md`, `1.md`) were frozen and **before any task's GT was revealed**. Auditor: independent policy-task auditor.
- Freeze hashes (recomputed by the auditor, matching the brief): `tasks/estimate_booking_desk/estimate.extended.yaml` sha256 `bfe4870f0a14bad9…`; `tasks/estimate_booking_desk/task_tools.py` sha256 `199b0d6febd06c16…`.
- Read: `blueprint/blueprint.yaml` (this difficulty's claim), `blueprint/products/estimate.yaml` (diffed against the base section), `blueprint/products/{claim,warranty}.yaml` (row-consistency spot checks only), `blueprint/db_schema.json`, `blueprint/share_tools.py`, the extended charter, `task_tools.py`, the masked views, and `skills/erl-task-instantiate/scripts/check_compute.py` (DSL primitive semantics: `DAYS`, `MONTHS`, `CFIELD`, `XCOUNT`, `within_months`, `RND`).
- Masked: every task's `evaluation_criteria`, `computations`, `charter_scope`, `required_documents`, `design_rationale`, `solvability_contract`, `prerequisite_closure` and `db_closure*`. Nothing in this section derives from them.
- Entry conditions: the brief carries the gate snapshot. `check_extended`, `check_task_tools`, `replay_tasks`, `check_solvability`, `check_compute`, `check_grounding` and `check_cross_fire` are green; `check_cache_diff` is informational; `check_traceability` is deferred to KB rendering. The masked views are constructed and hashed. Input complete.
- **Read-isolation disclosure.** One `grep -rn … --include=*.py` from the repository root, meant to locate the DSL evaluator, printed matching lines from other scenarios' `task_tools.py` files (env_0005, 0021, 0025, 0028, 0030, 0040, 0041, 0049): date-helper constants and lambdas. No `.json` file was in the match domain, and no line concerns this scenario or difficulty. No conclusion here uses them.

### policy_conflict_scan

**The six extended policies**

| Policy | Subject | Target tool | Owner | Trigger | Acts on |
| --- | --- | --- | --- | --- | --- |
| storage_statement (S) | estimate_fee_charge | `post_storage_statement_c4ddc4f2` | agent | on_request | fee_type storage |
| storage_goodwill (G) | estimate_fee_waiver | `waive_storage_goodwill_2cb3c7ba` | agent | state_due | goodwill on the storage charge |
| owner_storage_share (O) | estimate_fee_payment | `pay_estimate_charge_54cbd3ef` | user | on_request | owner's payment on the storage charge |
| teardown_charge (T) | estimate_fee_charge | `post_teardown_charge_9aa30e52` | agent | state_due | fee_type teardown |
| measurement_charge (M) | estimate_fee_charge | `post_measurement_charge_e807c387` | agent | state_due | fee_type measurement |
| insurer_teardown_payment (I) | estimate_fee_payment | `remit_insurer_direct_payment_12af7a63` | user | on_request | insurer_direct on the teardown charge |

**Overlaps**
- **Subjects.** S, T and M share `estimate_fee_charge` but act on disjoint fee types. O and I share `estimate_fee_payment` but act on different charges (storage vs teardown) with different payers and methods (the owner's own method vs `insurer_direct`). No two policies decide the same quantity on the same object.
- **Eligibility and time anchors.**
  - S, T and M inherit `charge_status_allowed` from base service fees.
  - T and M anchor on the estimate written date.
  - S anchors on the statement date.
  - O and I inherit base fee settlement (one charge per payment, never above the outstanding; `insurer_direct` only on an allowed tier).
  - No contradiction between them.
- **Terminal states.** Each writes one row on `estimate_events`. None changes the booking status.
- **Cross-category reads.** The declared `cross_category` blocks match the compute calls exactly (`check_extended` is green):
  - S reads warranty (status, issued_date);
  - G reads claim_ledger (event_type);
  - T and M read claim (variant, status, delivered_date), adas (systems, status) and warranty (variant, status);
  - I reads claim and adas.
- **Implicit cross-policy reads (latent).** S's `storage_holding_rate` and O's `insurer_daily_allowance` read whether a *teardown charge* stands on the booking, and that charge is the write of T. No `prerequisite` edge declares the dependency. Neither task's world exercises it: task 0's teardown charge is seeded, and task 1 involves no storage. It is folded into finding F-1 below.
- **Scope partition (derived blind, from the trees walked in `0.md` and `1.md`).**
  - Task 0 = {O, S, G}; task 1 = {I, T, M}.
  - The two sets are pairwise disjoint, together cover all six extended policies, and each spans a full tree.
  - To be confirmed against `charter_scope` after the reveal.

### rule_compute_equivalence

Mechanically: every compute binding of all six policies has a `compute_basis` entry, every quotation is verbatim in that policy's `rule` (whitespace-normalised), and there are no orphan basis keys. Then, sentence by sentence by hand:

- **S.**
  - Day-zero convention, calendar counting, first and last billed days both included, the single rounding point and the tier defaults are all implemented.
  - The free-day calendar formulas were verified against hand counts for every written weekday:
    - Monday–Friday: `f + 2*((min(w,4)+f)//5) - max(0,w-4)`. For example, w=Sat, f=1 gives 2; w=Sun, f=1 gives 1; w=Fri, f=1 gives 3.
    - Monday–Saturday: `f + (min(w,5)+f)//6 - max(0,w-5)`. Checked the same way.
    - `written_weekday` uses `DAYS('2026-01-05', d) % 7`, and 2026-01-05 is a Monday ✓.
  - The long-stay multiple applies only after the threshold day ✓.
  - Tenure uses `CFIELD('warranty','issued_date',status='active')` at customer level, matching "an owner holding an active network workmanship warranty" ✓. Observation O-11: there is no tie-break among several active warranties.
- **G.**
  - Percentage, authority, counted-goodwill set, relief days at the tier rate, the specialised average over first-to-last billed days, and the courtesy measured in calendar days from `requested_at` (timestamp, read at `[:10]`) to `confirmed_date` are all implemented.
  - "within the last whole month before the statement date" corresponds to `within_months=1`, i.e. `0 <= MONTHS(event_date, NOW) < 1` ✓.
  - Observation O-4: the inherited base cap "never exceeds that charge's estimate_msr_charge_outstanding" is not implemented in compute.
- **O.**
  - Average day value, the responsibility anchor (three tiers), grace counted forward from the responsibility date with a weekday-aware span, review days after grace, the allowance cap on the insurer's days, the three goodwill-sharing methods, and the floor at zero and cap at outstanding are all implemented.
  - The `responsibility_weekday` arithmetic yields the responsibility date's weekday ✓.
- **T, M, I.**
  - Each base/add-on sentence maps to one binding. "fractions counted" corresponds to `measurement_amount / P('measurement_fee_usd')`.
  - "whole months" uses `MONTHS`, which decrements when the later day of month is smaller ✓.
  - The SRS, bench and zone conjunction/disjunction ladders match "exactly one of those two conditions".
- **No compute-invented basis and no empty rule promise** was found beyond O-4.

### action_binding_and_uuids

- Each `(target_tool, computes)` is claimed by exactly one policy. All six tools are distinct and all compute `amount_usd`.
- The uuid8 tails `c4ddc4f2`, `2cb3c7ba`, `54cbd3ef`, `9aa30e52`, `e807c387` and `12af7a63` share no prefix, suffix or sequential pattern, and none is reused. Consistent with independent generation.
- Docstrings: no tool names another tool, and none carries an ordering word. The only "first" is the period descriptor "first billed day". Observation O-8: `waive_storage_goodwill_2cb3c7ba` describes `charge_event_id` as "returned by the estimate booking history lookup or by the storage posting receipt", and `pay_estimate_charge_54cbd3ef` and `remit_insurer_direct_payment_12af7a63` say "from the booking history or a posting receipt". These describe where an id comes from, not a sequence.
- Owners: O and I are `owner="user"`. Every other task tool is `owner="agent"`. No function body contains a guard, an error path or a hint: each looks up the booking for `customer_id`, rounds, `make_id`s and creates one row.

### prerequisite_graph

- `prerequisite` is filled on all six policies: `[]` on S, T and M.
- The edges are G←S, O←S, O←G, I←T and I←M. Each `problem` is an extended policy id of this file, none is a base policy, and there are no self-references. The graph is acyclic: the two components are S→G→O with S→O, and T→I with M→I.
- Every `policy_source` is verbatim in the blocked policy's own `rule` and absent from the depended-on policy's rule (mechanical check).
- All five edges are `form: state`, and none carries a `fallback_reason` ✓.
- `kind` is `value_input` on all five, and each `gate` is a real compute binding of the blocked policy: `storage_charge_amount`, `statement_amount`, `goodwill_on_statement`, `teardown_outstanding` and `accepted_hours`.
- `resolved_by` equals the depended-on policy's `target_tool` on all five.
- Each `effect` is real. Skipping each resolving write on its task's world changes or voids the scored value; see `0.md` and `1.md` → `problem_chain`.
- `condition` against sentence strength:
  - G←S: the condition adds "billing the days from the day after the last free storage day through the statement date" to a sentence that says only "the storage charge it relieves stands on the booking". This is a narrowing in the field, not in the rule. Only S can write a storage charge, so the narrowing selects nothing different. Observation O-12.
  - The other four edges match.
- There is no authoring-viewpoint phrasing ("in this task", "at the opening") in any `prerequisite` field.

### prerequisite_sentences

The four-point test, edge by edge:

| Edge | Sentence (own rule) | Connective | Waited-on state (record-visible) | Tool/id/snake-case | Single writer |
| --- | --- | --- | --- | --- | --- |
| G←S | "Storage goodwill is worked out only once the storage charge it relieves stands on the booking." | only once | a storage charge on the booking (`estimate_events`, fee_type storage) | none | S only (`post_storage_statement`); no other tool writes fee_type storage |
| O←S | "The owner's payment toward a storage statement is worked out only after the booking carries a storage charge billing every day from the end of the free storage days through the statement date." | only after | storage charge with that period (period_start/end fields) | none | S only |
| O←G | "The owner's payment toward a storage statement is not fixed until that storage charge carries the storage goodwill booked on storage statements." | not … until | a goodwill waiver against that charge (`charge_event_id`, `waiver_reason` goodwill) | none | G only; no other tool of this difficulty writes a waiver |
| I←T | "The insurer's direct payment toward a teardown charge is fixed only after the teardown charge for the teardown performed stands on the booking." | only after | teardown charge on the booking | none | T only |
| I←M | "The insurer's direct payment toward a teardown charge is not worked out until the booking carries a measurement charge for every structural measurement report produced on it." | not … until | measurement charge on a measurement-producing tier | none | M only |

- **Derivation (sentence + records + depended-on rule → resolving action, single reading).**
  - "storage charge … stands" with none in the records leads to S's rule, the only rule that posts a storage charge ("posted as one storage charge dated on the statement date").
  - "carries the storage goodwill booked on storage statements" with none in the records leads to G's rule ("Every storage statement charge carries the storage goodwill … booked as one goodwill waiver against that storage charge").
  - "teardown charge … stands" with none in the records leads to T's rule ("A teardown charge posts once on the estimate written date of a booking whose tier includes a teardown").
  - "a measurement charge for every structural measurement report produced" with the tier's `measurement_report_included` true and no such charge leads to M's rule.
  - Each hop has exactly one reading.
- No blocked rule carries a second wording of its dependency, a tool name or another policy's id. No depended-on rule restates the sentence.
- No base rule sentence grounds an edge.
- Undeclared cross-problem orders stated in a rule: none stated as an order. The implicit teardown-charge read in S and O is recorded under F-1.

### override_declarations

Each `base_policy_refs` entry was read sentence by sentence; the base section is byte-identical to `blueprint/products/estimate.yaml` (diff clean).

- **S**, against `estimate_evt_storage`:
  - Declared and replaced: "Storage is billed in one storage charge on the release date … at storage_daily_rate_usd per calendar day", and "The storage_free_days run from … day zero; … last billed day is the vehicle_released_date".
  - The rate, the long-stay multiple and the free-day additions and calendar all fall under these two declared clauses, because the replaced text carried both the rate and the free-day count.
  - Inherited and respected: "only on tiers whose storage_applies is true, only while the vehicle stays … never on a booking that converts".
  - The base `formula` block (`billable_days * storage_daily_rate_usd`) is the rendered form of the superseded clause.
  - Against `estimate_evt_service_fees`, `estimate_evt_revision` and `estimate_evt_check_in_and_write`: followed. The turnaround in business days is reused only as a subtrahend; see O-6.
- **G**, against `estimate_evt_fee_settlement`:
  - Declared and replaced: the goodwill sentence (authority per booking across all charges; "a request beyond that authority is declined at the desk").
  - Inherited: one charge per waiver, never above the outstanding, no stacking beyond the outstanding. Compute does not carry the cap (O-4).
  - Against `estimate_evt_decline_and_release`: "no credit applies to a declined booking". In the base charter "credit" is the conversion credit (`*_credited_on_conversion`, "earn the estimate-fee credits", the `converted_to_repair` waiver reason), and goodwill is a distinct waiver reason. No conflict. Observation O-3.
  - Against `estimate_evt_reschedule`: no sentence governs goodwill.
- **O** (`overwrite: []`): base fee settlement fixes no payment amount, and base storage, expiry and decline say nothing of a split. Additive, with no undeclared override. Release ("only when nothing is outstanding") is untouched.
- **T** and **M**, against `estimate_evt_service_fees`: the flat-fee sentences are declared and replaced. "each once per booking", the status gate and "A tier whose fee is zero posts nothing" are inherited.
- **I** (`overwrite: []`): base fee settlement allows `insurer_direct` on an allowed tier and caps at the outstanding. I complies.
- **Disguised forms.** No anonymous intermediate factor. No 0/1 multiplier on a base-fixed amount: the long-stay multiple is ≥ 1 and covered by S's declaration. No dropped base branch. No author text calls a base output "wrong".
- **Result: no undeclared override in the charter.**

### factor_ladders

Counts per policy: factors / parameter / method / cross_difficulty. Every ladder has 3 tiers including the fall-through, and every fall-through equals the factor's `baseline`. Bindings are disjoint within each policy, every `decides` is an input rather than `result`, and every tier is stated in the rule and implemented in compute.

| Policy | Factors | Param | Method | Cross-difficulty | Multi-source factors |
| --- | --- | --- | --- | --- | --- |
| S | 6 | 5 | 1 (free_day_calendar) | owner_tenure_free_days → warranty | storage_holding_rate, free_day_calendar |
| G | 6 | 5 | 1 (counted_goodwill_window) | paying_record_pct → claim | paying_record_pct |
| O | 6 | 3 | 3 (responsibility_anchor, grace_day_calendar, goodwill_sharing) | none | removal_grace_days, insurer_daily_allowance, responsibility_anchor |
| T | 5 | 4 | 1 (teardown_base_method) | base → claim, sensor → adas, doc → warranty | recovery_addon, long_teardown_addon |
| M | 5 | 4 | 1 (measurement_base_method) | base → claim, sensor → adas, filing → warranty | bench_mounting_addon, measured_zone_addon, measurement_base_method |
| I | 4 | 3 | 1 (accepted_hours_method) | rate → claim, sensor → adas | accepted_hours_method, insurer_recovery_allowance |

- **Distinct outcomes.** Every ladder's three tiers select distinct values or methods. The closest pair is M's comparison base, 0.6 × 145 + 90 = 177 on tier 6, against the archive base, 145 + 35 = 180. They are distinct.
- **Labels.** Each `method` label changes the algorithm:
  - flat fee vs hours × rate;
  - comparison formula vs fresh measurement;
  - day calendar;
  - counting set;
  - anchor date;
  - sharing order;
  - hours reckoning.
  
  Each `parameter` label swaps a number.
- **Real-business test.** Two ladders fail it (F-1, F-2). The others are plausible for a collision network:
  - EV storage priced above standard;
  - re-inspection, late write-up and loyalty free days;
  - towed and airbag recovery;
  - warranty documentation;
  - comparison against an earlier structural measurement;
  - insurer allowances keyed to the prior repair class, calibrated sensors and tow distance;
  - goodwill keyed to paying record and statement size.
  
  Observations O-2, O-6 and O-9 note weaker conditions.

### findings

**F-1 — SOURCE-FACTOR RED (unreal ladder): the "isolation" tier of `storage_holding_rate` (S) and `insurer_daily_allowance` (O).** Bears on task 0.
- **Symptom.** Both ladders split high-voltage vehicles into "a teardown charge standing on the booking" (quarantine 85 / allowance 75) and "no teardown charge on the booking" (isolation 70 / allowance 60). The second part of that compound condition holds of every booking that can reach a storage statement, so the isolation tier never applies to any customer the policy serves.
- **Evidence.**
  - `storage_applies: true` only on Blueprint Teardown Estimate and Structural Blueprint Estimate (variants, charter lines 416 and 474). Both carry `teardown_included: true` (lines 402 and 460) with a non-zero `teardown_fee_usd` (185 and 365).
  - T's rule (state_due): "A teardown charge posts once on the estimate written date of a booking whose tier includes a teardown". Base service fees say the same, "each once per booking".
  - Storage only accrues after the estimate written date (S: "The free storage days run from the estimate written date as day zero"). It never accrues on a converted booking (`estimate_evt_storage`).
  - Charges are never deleted: payments and waivers post *out* against them, and `billing_error` "is waived down to the correct amount".
  - The rule itself justifies quarantine by "its battery system having been disturbed by the teardown", which describes every vehicle on a storage-bearing tier.
- **Demonstrated consequence.**
  - The isolation tier is reachable only in a world where the desk has not yet posted a charge that was due on the written date. That is a bookkeeping lag, not a condition a collision network weighs when pricing EV storage.
  - Each ladder therefore has two real tiers ({HV → quarantine, otherwise → standard}), below the three-tier floor.
  - In such a lagged world, posting S before T would give 70/day and after T 85/day: two terminal states with no declared edge.
- **Affected.** `extended_policies[estimate_ext_storage_statement].rule` (rate paragraph), `factors[storage_holding_rate]`, `compute.storage_day_rate`; `extended_policies[estimate_ext_owner_storage_share].rule` (allowance paragraph), `factors[insurer_daily_allowance]`, `compute.daily_storage_allowance`. The per-task consequence is in `0.md`.

**F-2 — SOURCE-FACTOR RED (unreal method tier): the "documented hours" tier of `accepted_hours_method` (I).** Bears on task 1.
- **Symptom.** When a measurement charge stands and structural damage is recorded, the insurer's accepted *teardown labor hours* become the included hours plus 1.0 h "for each multiple of the tier's measurement_fee_usd that the measurement charges on the booking amount to, fractions counted". The insurer's labor-hour acceptance is thus driven by the dollar total of a different charge.
- **Evidence.**
  - Rule paragraph "How the accepted teardown hours are reckoned …", and `compute.accepted_hours`.
  - M's own rule builds the measurement charge from add-ons that are not teardown labor: the bench mount, sensor mounting points, extra measured zones, and filing the report with a structural warranty.
  - Each of those dollars therefore raises the insurer's accepted *disassembly hours*.
- **Demonstrated consequence (task 1's world).** The filing add-on (40), zone add-on (90), bench add-on (75) and sensor-point add-on (50) together add 255/145 = 1.759 accepted teardown hours, worth 184.66 of the 1122.83 allowance. An insurer does not accept extra disassembly labor because a structural report was filed with a warranty. No insurer publishes this as its treatment of teardown labor.
- **Effect of the strike.** With that tier struck, `accepted_hours_method` has two real tiers and I has 3 surviving factors and no `method` factor, below the 4-factor and 1-method floors.
- **Affected.** `extended_policies[estimate_ext_insurer_teardown_payment].rule` (accepted-hours paragraph), `factors[accepted_hours_method]`, `compute.accepted_hours`.

**Observations** (no demonstrable consequence on either task's scored solution; not grounds for rework)
- **O-1. "A … charge standing on the booking" for a charge already settled in full.** Used in S, T, M, O and I. The charter uses "stands on the booking" for a posted charge (the tool docstrings say "one teardown charge … stands on the booking's estimate-stage fees", and the prerequisite sentences use the same phrase). The complementary tiers say "no teardown charge on the booking" or "when no tow-in charge stands on the booking". The appositives identify a past arrival or teardown. The "outstanding only" reading is weak. Alternative figures: task 0 S = 880.00; task 1 T = 1040.00, M = 357.00, P = 1008.52.
- **O-2.** `free_day_calendar` tier 2 ("a network-arranged tow … recorded as drivable") describes a vehicle the tow service is defined not to carry (`tow_in_available`: "a tow of a non-drivable vehicle"). Neither task exercises it.
- **O-3.** Base "no credit applies to a declined booking" against storage goodwill on a declined booking (task 0). "Credit" is base vocabulary for the conversion credit, so there is no second reading of weight.
- **O-4.** G's compute caps at the authority left but not at the storage charge's outstanding, a cap inherited from base fee settlement. In a world with a one-billed-day statement at 55, the figure 0.02 × 55 plus reliefs can exceed 55. Task 0 is not affected (206.60 < 1360.00).
- **O-5.** O's rule states absolutely "with no confirmed decline request the owner answers for no billed day" and also a ladder tier for "no decline request is confirmed and more than … estimate_validity_days have passed". The specific tier governs, giving a single reading. Neither task exercises the tier (task 0 has a confirmed decline).
- **O-6.** Write-up lateness is defined as calendar days less *business* days, mixing units. The definition is explicit, so there is a single reading. On task 0 it yields lateness 4 (long tier) where a business-day measure gives 2 (short tier).
- **O-7.** S fixes the first billed day at "the day after the last free storage day" whatever the earlier statements. A second statement on the same booking would re-bill days already billed. Not exercised.
- **O-8.** Docstrings point at "the storage posting receipt" or "a posting receipt" as the source of a charge id. They name no tool and carry no ordering word.
- **O-9.** G's "specialised daily rate" relief is keyed to the statement's average billed-day value, which includes the long-stay multiple. A standard-rate statement with a long stay can earn "specialised" relief. Task 0 is on the quarantine rate anyway.
- **O-10.** Implicit S/O dependency on T's charge: see F-1.
- **O-11.** `CFIELD` returns the first matching row. The rules speak of "the vehicle's closed network claim repair order", "completed … calibration order" and "active … warranty" in the singular, and S's tenure reads any active warranty of the owner, with no tie-break among several. Both task worlds seed exactly one row of each.
- **O-12.** G←S `condition` is narrower than its sentence (it adds the billed period). With a single writer this is harmless.

## closing_checklist

Written after both reveals (task 0 at 01:54:03 UTC, task 1 at 01:55:08 UTC). The charter-global section above was not edited after the reveals, apart from a timestamp correction to its own header line; that correction replaced an estimated time with the file's true pre-reveal mtime.

- **Files.** `0.md` and `1.md` correspond one to one with `tasks/0.json` and `tasks/1.json`; `_difficulty.md` sits alongside. This is revision 1, with no earlier revisions. Each comparison section carries a verdict.
- **Coverage and scope.**
  - GT `charter_scope`: task 0 = {storage_statement, storage_goodwill, owner_storage_share}; task 1 = {teardown_charge, measurement_charge, insurer_teardown_payment}. This equals the scopes derived blind.
  - Pairwise disjoint; all six extended policies covered.
  - Task tools closed (three per task, each one policy's `target_tool`). uuid8s independent (see `action_binding_and_uuids`).
- **Trees.**
  - Task 0: n = 2, three value_input edges, `owner=user` root.
  - Task 1: n = 2, two value_input edges, `owner=user` root.
  - Both acyclic. Across the difficulty the graph is two disjoint DAGs with no cross-task edge.
- **Factors.**
  - Every computation declares a self-sufficient baseline whose fallback differs from gold: 1320.00 vs 1360.00, 27.20 vs 206.60, 621.06 vs 628.40, 365.00 vs 1135.00, 145.00 vs 432.00, 384.00 vs 1122.83.
  - Every computation has 4–6 factors with at least 2 parameter and 1 method. Each task has at least 1 multi-source and 1 cross-difficulty factor, with seeded rows.
  - All 32 factors bear weight on their task's world against honest baselines.
  - **Not met:**
    - F-1: the isolation tiers of storage_holding_rate and insurer_daily_allowance are unreachable, so each of those ladders has two real tiers.
    - F-2: the documented-hours method of accepted_hours_method is not a treatment any insurer applies; with it struck, I falls below the factor and method floors.
    - T0-F1 and T1-F1: computations S (task 0), T and M (task 1) carry no exclusion-type near-miss.
- **Gates.** Not re-run by the auditor. The artifacts are unchanged since the coordinator's snapshot (`estimate.extended.yaml` `bfe4870f0a14bad9`, `task_tools.py` `199b0d6febd06c16`, rechecked at close), so that snapshot stands as the gate state of the audited form.

**Difficulty verdict: does NOT pass the source-layer audit.**
- Policy self-consistency: PASS for both tasks.
- Problem tree holds: PASS for both tasks.
- Unique solution: PASS for both tasks. Each blind derivation equals GT to the cent.
- Factors bear weight: **SOURCE-FACTOR RED** for both tasks:
  - task 0: F-1 and T0-F1;
  - task 1: F-2 and T1-F1.

## revision_2

### charter_global_frozen (revision 2)

- Written 2026-10-11 04:26 UTC. The round-2 task derivations had been computed, and their `revision_2` sections in `0.md` and `1.md` were appended immediately after this section. All of it was **before any round-2 GT was read**. Revision 1 above is left untouched.
- Inputs, recomputed by the auditor and matching the brief:
  - `estimate.extended.yaml` sha256 `c15925232e754e22…` (**changed** from `bfe4870f0a14bad9…`);
  - `task_tools.py` sha256 `199b0d6febd06c16…` (unchanged);
  - masked views `0.masked.json` `da121bd2e647b6b3…` and `1.masked.json` `da49e44981b6ee98…`.
- Because the charter changed, every charter-global section is **re-derived in full**. Only `action_binding_and_uuids` is carried forward by reference: the tool module hash is unchanged, and no `target_tool` or `computes` changed (re-verified).
- Base section: still byte-identical to round 1 (diffed against the round-1 copy) and therefore to `blueprint/products/estimate.yaml`.
- Entry conditions: the round-2 gate snapshot is in the brief (all green; traceability deferred). Input complete.
- contamination_disclosure:
  - In round 1 the auditor read both tasks' GT (`tasks/0.json` and `tasks/1.json` as they then stood). Those round-1 scored values and conventions are therefore known to the auditor. They were not used for the round-2 derivations: both seeds changed, and every round-2 figure in `0.md` and `1.md` → `revision_2` is recomputed from the round-2 masked views and the round-2 charter.
  - No round-2 task JSON has been opened at the time of writing.
  - The reworker's claims ("closed F-1, F-2, T0-F1, T1-F1; addressed O-1, O-2, O-4, O-12, O-T0-2") were not taken as evidence; each is verified below.

### policy_conflict_scan (revision 2)

- The six policies, subjects, tools, owners and triggers are unchanged; no two decide the same quantity on the same object.
- What is new is that S's rate, S's free-day calendar, O's grace and allowance ladders, T's recovery add-on, M's bench add-on and I's recovery allowance now all read "a tow-in charge having been posted on the booking". The tow-in charge is a base event (`estimate_evt_service_fees`, posted on the check-in date), not the write of any extended policy.
- **The round-1 latent undeclared S/O → T dependency (folded into F-1) is gone.** No compute of S or O reads `fee_type='teardown'` any more; this was verified by scanning the compute strings.
- Scope partition derived blind: task 0 = {O, S, G}, task 1 = {I, T, M}, unchanged. Disjoint and covering.

### rule_compute_equivalence (revision 2)

- Mechanically: every binding has a basis, every quotation is verbatim in its own rule, and there are no orphan keys (all six policies).
- By hand, the changed sentences:
  - **S, rate.** "a vehicle with high-voltage damage recorded on the booking that arrived on a network-arranged tow, a tow-in charge having been posted on the booking whether or not it has since been settled, … quarantine_rate_usd per day; a vehicle with high-voltage damage recorded on the booking and no tow-in charge ever posted on the booking … isolation_rate_usd; every other vehicle … the tier's storage_daily_rate_usd". The compute is `rate_tow_arrivals = COUNT(... fee_type='tow_in')`, which counts posted rows whatever their settlement ✓.
  - **S, calendar.** Tier 2 is now "recorded as not drivable with no tow-in charge ever posted … Monday to Saturday". The compute's second branch is `tow_in_charges == 0 and drivable == False` ✓. The Monday–Saturday formula is unchanged and was verified in round 1.
  - **G, cap.** "never more than the goodwill authority left on the booking nor more than the storage charge's outstanding amount". The new `storage_charge_outstanding` binding (amount less waivers less payments on that charge) enters `MN(...)` ✓. **O-4 closed.**
  - **O, allowance.** HV and tow-in posted → quarantine; HV and no tow-in ever → isolation; otherwise the average ✓.
  - **I, accepted hours.** "plus structural access hours equal to structural_access_hours_share of the estimate's labor hours … fractions counted" is implemented as `teardown_labor_hours_included + estimated_labor_hours * 0.02` ✓. The undocumented and no-measurement tiers are unchanged.
  - **T, M, I.** The tow wording "having been posted" and the insurer's recovery wording "none when no tow-in charge was ever posted" match `COUNT(...) >= 1` ✓.
- No compute-invented basis and no empty rule promise.

### action_binding_and_uuids (revision 2)

Carried forward by reference to revision 1. The grounds are an unchanged `task_tools.py` hash (`199b0d6febd06c16`) and an unchanged `target_tool`/`computes` on all six policies (re-verified).

### prerequisite_graph (revision 2)

- The five edges are unchanged in endpoints, kind, gate, form, `policy_source` and `resolved_by`.
- Mechanically re-verified:
  - every `policy_source` is verbatim in its own rule and absent from the depended-on rule;
  - every gate is a real binding;
  - every `resolved_by` equals the depended-on `target_tool`;
  - no `fallback_reason` (all edges are state form);
  - the graph is acyclic.
- G←S `condition` now reads "A storage charge (an estimate-stage charge of fee type storage) stands on the booking.", the same strength as its sentence. **O-12 closed.**
- I←M `effect` was rewritten to the structural-access mechanism.
- New observation **R2-O1 (I←M edge).** Under the new accepted-hours method the measurement charge's *amount* no longer enters I. Only its existence switches `accepted_hours` from the included-hours tier to the structural-access tier. The edge stays `value_input` by its gate (a real binding whose value changes: 8.086 vs 6.0 on task 1). Functionally, though, the measurement write now flips a tier rather than feeding a value. The tree's value-input floor, max(n−1,1) = 1, is still met by I←T (the teardown outstanding enters the payment). No red.

### prerequisite_sentences (revision 2)

- Unchanged sentences, so the four-point test, the single-writer analysis and the derivation in revision 1 hold verbatim.
- The rules newly carry no tool name, policy id or snake-case token outside the parameter names (mechanical scan), and no depended-on rule restates a sentence.

### override_declarations (revision 2)

- Base unchanged; `overwrite` blocks re-read.
- G's replaced_by now adds "nor more than the storage charge's outstanding amount". This restates the inherited base cap and does not conflict with it.
- S's rate and calendar changes stay inside the two declared superseded clauses of `estimate_evt_storage`. T and M are unchanged. I is still `overwrite: []`, and the new accepted-hours method governs no base quantity.
- **No undeclared override.** O-3 (base "no credit applies to a declined booking") is unchanged and remains an observation.

### factor_ladders (revision 2)

Counts are unchanged: S 6 (5 parameter/1 method), G 6 (5/1), O 6 (3/3), T 5 (4/1), M 5 (4/1), I 4 (3/1). Cross-difficulty factors are as in revision 1. Every ladder has 3 tiers with distinct outcomes, all stated in the rule and all implemented. The re-examined ladders:

- **storage_holding_rate (S) and insurer_daily_allowance (O): F-1 re-test.**
  - The compound condition is now high-voltage damage combined with whether a tow-in charge was ever posted.
  - Unlike the teardown charge, a tow-in charge is **not** universal on storage-bearing bookings. It posts only when "the vehicle arrived on a network-arranged tow" (base `estimate_evt_service_fees`).
  - Tiers 5 and 6 accept HV vehicles that are drivable or carried in (`high_voltage_damage_eligible: true`, `non_drivable_eligible: true`), so all three tiers are reachable:
    - an HV vehicle that is towed in;
    - an HV vehicle that is driven or carried in;
    - a vehicle without HV damage.
  - The business distinction is plausible: a towed, crash-disabled EV goes to a quarantine bay; a driven-in EV with HV damage goes to an isolation row; a conventional vehicle goes to the standard lot. An insurer would also allow those rates.
  - **F-1 closed.**
- **free_day_calendar (S): O-2 re-test.** Tier 2 (not drivable and not towed by the network, i.e. the owner's own carrier → Monday–Saturday) no longer contradicts the tow service's definition. The three tiers are real: network flatbed on business days; owner's carrier including Saturdays; drivable vehicles on calendar days. **O-2 closed.**
- **accepted_hours_method (I): F-2 re-test.**
  - New tier 1: the included hours plus 2% of the estimate's labor hours as "structural access hours, the access disassembly a structural repair of that size needs", when a measurement charge stands and structural damage is recorded.
  - Tier 2: the included hours plus a fixed 1.0 h when measured with no structural damage. Tier 3: the included hours.
  - Scaling teardown/access allowance with the size of the documented structural repair is a treatment an insurer can publish. Measurement-charge dollars no longer convert into labor hours.
  - The label stays honest: tier 1 is a proportional algorithm, tier 2 a fixed add, tier 3 none.
  - **F-2 closed.**
- **O-1, the "standing" reading.** Every tow-in condition now says "having been posted (whether or not it has since been settled)" or "ever posted". The second reading no longer exists. **Closed.**
- Unchanged ladders: as in revision 1. O-6 (write-up lateness mixing calendar and business days) and O-9 (specialised relief keyed to the average) are unchanged and remain observations, as the reworker states.

### findings (revision 2, pre-reveal)

- Round-1 charter-global REDs: **F-1 closed**, **F-2 closed** (see `factor_ladders (revision 2)`).
- Round-1 observations: **closed** O-1, O-2, O-4, O-12. **Unchanged** O-3, O-5, O-6, O-7, O-8, O-9, O-11. O-10 lapses with F-1.
- **New charter-global defects: none found.** New observation R2-O1 (the I←M edge is now existence-only in effect; the floor is still met).

### closing_checklist (revision 2)

Written after the round-2 reveals (2026-10-11 04:27:48 UTC). The revision-2 charter-global section above was frozen before them.

- **Files.** `0.md` and `1.md` each carry revision 1 (untouched) plus `revision_2`, frozen and then compared; `_difficulty.md` likewise. Every revision-2 comparison carries PASS.
- **Coverage and scope.** Task 0 = {S, G, O}; task 1 = {T, M, I} (GT `charter_scope` equals the blind derivation). Pairwise disjoint; all six extended policies covered. Task tools are closed; uuid8s are independent and unchanged.
- **Trees.**
  - Task 0: n = 2, three value_input edges, `owner=user` root.
  - Task 1: n = 2, two value_input edges (I←M existence-only in effect, R2-O1; the floor is met by I←T), `owner=user` root.
  - Two disjoint DAGs; no cross-task edge.
- **Factors.**
  - 32 factors, all bearing weight against honest baselines.
  - Fallbacks differ from gold: 1320.00 vs 1487.50; 29.75 vs 214.25; 636.62 vs 673.25; 365.00 vs 1075.00; 145.00 vs 410.00; 384.00 vs 979.03.
  - Each computation has 4–6 factors with at least 2 parameter and 1 method. Each task has multi-source and cross-difficulty factors with seeded rows.
  - Every computation has an exclusion-type near-miss.
  - Every ladder has 3 real, distinct tiers stated in its rule.
- **Gates.** Not re-run by the auditor. The coordinator's round-2 snapshot (all green) was taken on the audited hashes: `estimate.extended.yaml` `c15925232e754e22` and `task_tools.py` `199b0d6febd06c16`.
- **Round-1 closure.**
  - F-1, F-2, T0-F1 and T1-F1: all **closed**, each verified on the charter and on its task's world.
  - Observations: O-1, O-2, O-4 and O-12 closed; O-T0-2 closed.
  - Left as is: O-3, O-5, O-6, O-7, O-8, O-9 and O-11. All remain observations, consistent with the reworker's statement.
- **New defects:** none. **New observation:** R2-O1. **Regressions:** none. Both tasks' scored values moved with the new seeds, and the blind re-derivation matches GT to the cent.

**Difficulty verdict (revision 2): PASSES the source-layer audit.** Policy self-consistency, problem tree, factor weight and unique solution are all PASS for both tasks.
