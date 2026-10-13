# Policy-task audit — group_room_block_contracts / charter-global

## charter_global_frozen

- Frozen: 2026-10-05T16:20:31Z, before any task's GT was revealed (the multi-source cells of § factor_ladders were corrected minutes later, still before any reveal). Auditor: independent policy-task auditor (erl-task-policy-audit), not the author of the artifacts.
- Freeze hashes (match `/tmp/env0036_views/group_room_block_contracts/HASHES.txt`):
  - `tasks/group_room_block_contracts/group.extended.yaml` sha256 `3b91a10cf20203d9c4aac5f59dc106dba6a309f1b9b593585ae555b6f4767290`
  - `tasks/group_room_block_contracts/task_tools.py` sha256 `515bfd89899efe3151a48fdcc4f67b4a2824dde9c9311e21322eb728df493809`
- Read for this section: `blueprint/blueprint.yaml`, `blueprint/db_schema.json`, `blueprint/share_tools.py`, `blueprint/products/group.yaml` (and `loyalty.yaml` qualification fields only), the extended charter, the task tool module. For the semantics of the compute DSL (DAYS, MONTHS, LATEST, XSUM/XCOUNT scoping to the customer, CFIELD) the evaluator functions `build_env`/`eval_compute` of `skills/erl-task-instantiate/scripts/check_compute.py` were read; that file carries no task data.
- Masked and not read: every `tasks/*.json` field other than the three in the masked views; `worklog.md` (scenario and difficulty); sibling difficulties' tasks and audits; other scenarios.
- Entry conditions (Step 0): gate snapshot `/tmp/env0036_views/group_room_block_contracts/GATES.txt` shows EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK; masked views and hashes supplied. Complete. (check_traceability deferred to the render stage, as stated in the brief.)
- Base copy: lines 1-1250 of the extended charter are byte-identical to `blueprint/products/group.yaml` (diff shows only a trailing blank line). Verbatim.

### policy_conflict_scan

Five extended policies: `group_ext_reduction_room_nights` (implement_block_reduction_df5160bf, room_nights_removed), `group_ext_interim_deposit_amount` (pay_group_deposit_93013531, deposit_amount, owner=user), `group_ext_increase_commitment` (implement_block_increase_5576c741, committed_room_nights), `group_ext_cutoff_release_nights` (record_cutoff_release_57832b69, room_nights_released), `group_ext_cancellation_damages` (sign_group_cancellation_1ea1e1e5, damages_amount, owner=user).

- Subjects/triggers: reduction and increase share base `group_addenda` but split its subjects (`group_block_reduce` vs `group_block_increase`) and select different addendum types (`amendment_type` filter) — no overlap. Cut-off release and cancellation both create `group_cutoff_release` ledger rows but with different `entry_basis` (`cutoff_release` vs `contract_cancelled`); the cancellation's `released_nights` filter reads only `cutoff_release`, so the cancellation's own release never feeds its own damages. No conflict.
- Eligibility/state: every ext policy inherits the base state gates (definite for addenda; tentative/definite for deposits; definite/cancelled for releases; definite→cancelled for cancellation). No ext text weakens them.
- Time anchors: reduction and increase both use the "count start follows the addendum's return" ladder (identical 30/60-day bands) on the addendum `created_at`; cut-off release is dated `cutoff_date` by the tool while its inputs are read at the handling moment; cancellation reads NOW as the notice date (the rule makes the signature date the notice date). Consistent.
- Cross-category reads: loyalty (reduction courtesy, interim rewards relief, cut-off holdback, cancellation tenure), meeting (interim event relief), booking (increase uplift, cut-off reserved/staff/grace/allotment, cancellation relief/rate/exclusion). All declared in `cross_category`.
- Terminal states: no two policies write the same field in conflicting directions; held/contracted changes are additive and the cancellation zeroes `held_room_nights` after its own release.
- Scope: the dependency graph has two components — {reduction → interim} and {increase → cut-off release → cancellation, increase → cancellation}. With M=2 the natural partition is one component per task; the five policies are then jointly covered and pairwise disjoint. (Whether each task claims exactly its component is confirmed per task after the reveal, in the task files' `source_gt_comparison`.)

### rule_compute_equivalence

Swept every binding of every ext policy against its `compute_basis` quotation and back. Also evaluated each compute on both task worlds with the DSL evaluator and compared with an independent hand implementation of the rule prose (per-task files): all five agree on both worlds.

- reduction: issued_at/requested (latest signed reduction by `created_at`), count-start three bands, reduction_pct (lead days AND signing deposit dated ≤ signing_deposit_due_days after proposal), measured_nights (≤ increase_window_days after `contract_signed_date` → all increases; later → late_increase_share; none → allocation), courtesy (tier set AND ≥ min_recent_stays `stay_base` earns in 24 months), allowance `int(measured × pct/100) + courtesy`, prior_counted weight by date of latest earlier reduction vs arrival, `MX(int(allowance − prior_counted), 0)`, `MN(requested, open)`. Each is quoted in the rule; nothing in compute lacks a rule sentence.
- interim: revenue = contracted × rate; days past due = interim due date (arrival − deposit_interim_days_before_arrival) to the payment date (NOW), floor 0; load/relief bands; applicable = pct + load − reliefs; true-up three methods; single rounding at the end, floor 0. Equivalent.
- increase: count-from 0 / return_period_days / days since issue; lead share bands on rooming_list_due_days (+ near_window_days); uplift on confirmed GBR nights naming the block vs contracted before the increase; post-cut-off cut; size cut vs allocation; clamp 0–100; int. Equivalent.
- cut-off release: named GBR nights; staff rooms = confirmed non-GBR master-account rooms naming the block (counted as all master-account minus GBR master-account); one night per staff room when any GBR room is card-guaranteed; grace on cancelled GBR nights by days to arrival; holdback by card/credits; on-time allotment from latest GBR `booked_date`; recent-increase hold by gap from latest signed increase addendum `created_at` to `cutoff_date`; floor 0. Equivalent.
- cancellation: `matched_pct` and `next_pct` hard-code each block type's `cancellation_scale` instead of reading `P('cancellation_scale')`; the hard-coded values were checked against all six variants and are equal. One empty gap: the rule's "the step one longer lead than the matching step" has no referent when the matching step is the top step; compute silently takes the top step itself (e.g. Social ≥181 → 10, Wedding ≥181 → 25). This is a basis the compute supplies and the rule does not state (finding F-G1). Every other binding is quoted.
- Factor ladders vs rule vs `decides` branches: every tier named in each `factors[].ladder` is a rule sentence and a branch of its `decides` binding, and vice versa (checked all 25 factors).

### action_binding_and_uuids

- `(target_tool, computes)`: (implement_block_reduction_df5160bf, room_nights_removed), (pay_group_deposit_93013531, deposit_amount), (implement_block_increase_5576c741, committed_room_nights), (record_cutoff_release_57832b69, room_nights_released), (sign_group_cancellation_1ea1e1e5, damages_amount) — each claimed by exactly one policy.
- uuid8s `df5160bf`, `93013531`, `5576c741`, `57832b69`, `1ea1e1e5`: distinct, no shared prefix, no sequence or adjacency pattern.
- Function bodies: none checks a policy condition, refuses, errors or hints; each performs its write unconditionally (`ctx.find` of the block, `ctx.create` ledger row, `ctx.update` block). The tool layer judges no prerequisite.
- Docstrings: no docstring states a sequence position or names another task tool. Ordering words that occur ("after the entry", "after the payment", "deposit due shortly after the proposal is issued", "deposit applied after the event") describe the post-write state or business timing of a deposit, not tool order. Args reference "the group block lookup" / "the contract addendum lookup" by business name as the provenance of an id (observation O-G6; no consequence).

### prerequisite_graph

| blocked policy | problem | kind / gate | form | binding exists | resolved_by = depended target_tool |
| --- | --- | --- | --- | --- | --- |
| group_ext_interim_deposit_amount | group_ext_reduction_room_nights | value_input / revenue | state | `revenue` ✓ | implement_block_reduction_df5160bf ✓ |
| group_ext_cutoff_release_nights | group_ext_increase_commitment | value_input / held_nights | state | `held_nights` ✓ | implement_block_increase_5576c741 ✓ |
| group_ext_cancellation_damages | group_ext_increase_commitment | value_input / contracted_nights | state | `contracted_nights` ✓ | implement_block_increase_5576c741 ✓ |
| group_ext_cancellation_damages | group_ext_cutoff_release_nights | value_input / released_nights | state | `released_nights` ✓ | record_cutoff_release_57832b69 ✓ |

- `prerequisite` filled on all five (reduction and increase `[]`). Every `problem` is an ext policy id of this file, none self-referencing, none a base policy. Graph acyclic (two sources: reduction, increase).
- Every `policy_source` is verbatim in its own policy's `rule` (string-located). No `form: action`, so no `fallback_reason` is required and none is present.
- `condition` texts restate the sentences at the same strength (all signed addenda of the type named by a ledger entry; cut-off release present once the cut-off date is on or before the notice date). The cancellation's first condition names a `group_block_increase` entry where the sentence says "a ledger entry that names it" (observation O-G4: only increase/reduction entries carry `amendment_id`, and only the increase write names an increase addendum, so the two read the same).
- `effect` statements are true of the tools: the reduction tool lowers `contracted_room_nights` (→ revenue); the increase tool raises `held_room_nights` and `contracted_room_nights` (→ held_nights, contracted_nights); the release tool creates the `cutoff_release` row (→ released_nights).
- No authoring-viewpoint phrasing ("this task", "at the opening", "current world") in any `prerequisite` text.

### prerequisite_sentences

1. Interim ← reduction: "The interim deposit is worked out only after every signed room-night reduction addendum on the block is matched by a reduction entry on the block ledger that names it." Connective "only after" ✓; state named in record words (addendum status signed; reduction entry naming it via `amendment_id`) ✓; no tool/policy id/snake_case ✓; strength = condition ✓. The one write that creates a reduction entry naming an addendum is the reduction implementation; the reader reaches it from `group_ext_reduction_room_nights`'s own rule ("implemented by one reduction entry on the block ledger that names the addendum"). Single reading.
2. Cut-off ← increase: "The room nights released at the cut-off are fixed only after every signed room-night increase addendum on the block has an increase entry on the block ledger naming it." ✓ on all four points; sole writer of an increase entry is the increase implementation, reached from `group_ext_increase_commitment`'s rule ("implemented by one increase entry on the block ledger that names the addendum"). Single reading.
3. Cancellation ← increase: "Cancellation damages are not worked out until each signed increase addendum on the block is matched by a ledger entry that names it." ✓ ("not … until"); sole writer: increase implementation. Single reading (see O-G4).
4. Cancellation ← cut-off release: "Cancellation damages are fixed only after the block ledger carries the cut-off release owed for a block whose cut-off date has been reached." ✓; writers of a `group_cutoff_release` row are the release tool (basis cutoff_release) and the cancellation tool itself (basis contract_cancelled, the root's own write, which "releases every room night still held with the cancellation basis"); the cut-off release is therefore singled out, reached from `group_ext_cutoff_release_nights`'s rule ("one release entry with the cut-off basis on the block ledger, dated the block's cut-off date"). Single reading.

- No rule restates another problem's prerequisite sentence; depended-on rules (reduction, increase, cut-off) do not mention the deposit, the release or the cancellation.
- No ext rule states a cross-problem order that grounds no edge. Intra-policy orders ("Signed reduction addenda are implemented one at a time in the order they were issued"; "once guest services has quoted the amount") concern one problem. Base sentences with cross-problem order ("Where signing_requires_deposit is true, the contract becomes definite only once the signing deposit has been received"; "Deposits are applied to the master account only once the block's status is actualized") ground no edge of these trees (observation O-G7).

### override_declarations

Sentence by sentence against each `base_policy_refs` entry; criterion is the scored quantity.

- `group_ext_reduction_room_nights` vs `group_addenda`: (1) "contracted room nights … change only through an addendum … implemented once, by one block update and one ledger entry naming it" — followed. (2) "amended only while its status is definite" — followed. (3) availability/confirmed increase — not this quantity. (4) "A reduction is accepted only if all reductions … total no more than free_reduction_pct percent of the room nights contracted at signing." — handled differently (multiplied pct, increase-widened base, courtesy nights, weighted earlier reductions, partial implementation) — declared, overwrite[0]. (5)/(6) deadline and its counting — followed ("a reduction addendum signed after the free-reduction deadline is not implemented at all"). (7) keeps group rate; attrition on reduced nights — followed. (8) "Reductions beyond the allowance or after the deadline are not accepted; the shortfall … attrition" — handled differently (partial removal) — declared, overwrite[1]. (9) "No addendum is implemented twice." — followed. Merged semantics unique.
- `group_ext_interim_deposit_amount` vs `group_deposit_schedule`: "Deposits are a percentage of anticipated room revenue … rounded to the cent" — superseded, declared overwrite[2] (true-up methods, single final rounding). "the signing deposit is deposit_signing_pct percent and is due within signing_deposit_due_days of the proposal" — followed (used as the on-time test). "and the interim deposit is deposit_interim_pct percent" — superseded, declared overwrite[1] (applicable percentage). "is due deposit_interim_days_before_arrival calendar days before arrival" — followed (due date of the late load). "a block type whose percentage is 0 has no such deposit" — not contradicted for any task world (Wedding, 25%); for 0% types the loads and reliefs net through the floor at zero. "Each scheduled deposit is received once." — superseded by an interim-only once-rule, declared overwrite[0] (observation O-G3: the replacement no longer states the signing-deposit half). "received only while tentative or definite" — followed. Refund/apply/forfeit sentences — other quantities. All conflicts declared.
- `group_ext_increase_commitment` vs `group_addenda`, `overwrite: []`: no base sentence fixes how many of an increase's room nights enter `contracted_room_nights`; (1) states only the channel (a signed addendum). The schema's meaning of `contracted_room_nights` ("committed to in the signed contract and signed addenda") reads naturally as full commitment, which is exactly the policy's baseline (full_commit_pct = 100) — an agent following it lands on the baseline number, which is the factor-blindness outcome rather than a competing base clause (observation O-G2). No undeclared override.
- `group_ext_cutoff_release_nights` vs `group_cutoff`: "On the cut-off date every held room night not yet reserved … the release equals held_room_nights less the room nights reserved inside the block at that moment." — superseded, declared. "released only once the cut-off date has been reached" — followed. "made on the cut-off date itself … held for the whole of the day before" — followed by the tool dating the entry `cutoff_date`. "The release does not reduce contracted_room_nights" — followed. lapse/cancel release — not this quantity. "recorded only for definite or cancelled" — followed. The overwrite is not scoped to rooming-list blocks although the ext rule is (observation O-G5; no task world has a call-in block at cut-off).
- `group_ext_cancellation_damages` vs `group_cancellation`: written notice sentence — superseded with the user-tool signature, declared. Damages formula sentence — superseded, declared. "Days are counted as whole calendar days from the notice date to the arrival date" — followed. "the first step … applies" — superseded by tenure ladder, declared. Elimination waiver — followed ("A cancellation under the elimination waiver carries no damages"). "Deposits held are retained toward the damages under group_deposit_schedule" — not contradicted; retention is a separate write that only arises when a deposit is held. "charged only on a block whose status is cancelled, at most once" — followed by the single-write cancel+charge tool. Lapse carries no damages — n/a. No undeclared override.

No anonymous intermediate, 0/1 multiplier or dropped branch found.

### factor_ladders

| policy | factor | effect | decides | tiers | multi-source (non-fall-through tiers over distinct records) | cross_difficulty |
| --- | --- | --- | --- | --- | --- | --- |
| reduction | reduction_percentage | parameter | reduction_pct | 3 | yes (addendum date / signing-deposit ledger row) | — |
| reduction | reduction_count_start | method | reduction_lead_days | 3 | no | — |
| reduction | allowance_measure | parameter | measured_nights | 3 | yes (increase entries / block signing date) | — |
| reduction | courtesy_room_nights | parameter | courtesy_nights | 3 | yes (membership / loyalty_transactions) | loyalty |
| reduction | earlier_reduction_weight | parameter | prior_counted | 3 | no (one date condition) | — |
| interim | late_receipt_load | parameter | late_load | 3 | no | — |
| interim | event_deposit_relief | parameter | event_relief | 3 | no (two fields of one meeting contract) | — (meeting has no difficulty) |
| interim | rewards_relief | parameter | rewards_relief | 3 | no (two fields of one membership) | loyalty |
| interim | deposit_true_up | method | interim_amount | 3 | yes (reduce entries / signing-deposit row) | — |
| increase | increase_count_start | method | inc_count_from | 3 | no | — |
| increase | lead_time_share | parameter | lead_share | 3 | no | — |
| increase | rooming_list_uplift | parameter | list_uplift | 3 | no | booking |
| increase | post_cutoff_cut | parameter | cutoff_cut | 3 | no | — |
| increase | increase_size_cut | parameter | size_cut | 3 | no (one ratio condition) | — |
| cut-off | staff_room_nights | parameter | staff_nights | 3 | yes (staff rooms / card-guaranteed list rooms) | booking |
| cut-off | name_change_grace | parameter | grace_nights | 3 | no (one days-to-arrival condition) | booking |
| cut-off | late_name_holdback | method | holdback | 3 | no (two fields of one membership) | loyalty |
| cut-off | ontime_list_allotment | parameter | ontime_allotment | 3 | no (one date-span condition) | booking |
| cut-off | recent_increase_hold | parameter | increase_hold | 3 | no (one date-gap condition) | — |
| cancellation | tenure_scale_step | method | scale_pct | 3 | no (two fields of one membership) | loyalty |
| cancellation | hotel_relationship_relief | parameter | relationship_relief | 3 | no | booking |
| cancellation | breakfast_rate_basis | parameter | damages_rate | 3 | yes (block type parameter / reservations) | booking |
| cancellation | card_guaranteed_exclusion | parameter | card_exclusion | 3 | yes (card-guaranteed rooms / all list rooms) | booking |
| cancellation | release_share | parameter | release_share | 3 | yes (release entry / block cut-off date) | — |
| cancellation | late_increase_share | parameter | increase_share | 3 | yes (increase entries / allocation / cut-off) | — |

Counts per policy (as declared): reduction 5 (4 parameter, 1 method); interim 4 (3, 1); increase 5 (4, 1); cut-off 5 (4, 1); cancellation 6 (5, 1). All within 4–6.

- Bindings disjoint within each policy; no `decides` is `result`; every fall-through tier equals the factor's `baseline` and equals what `baseline.rule` states (checked each: e.g. count-start baseline = days from the implementation date; true-up baseline = applicable pct × revenue; tenure baseline = matched step).
- No two tiers of one ladder select the same value or method on the charter's stated domain, with one exception at the edge of the cancellation scale: when the matching step is the top step, `tenure_scale_step`'s three tiers all yield the top step's percentage (F-G1).
- Labels: the four `method` factors change how the quantity is computed (count anchor; true-up formula; holdback share-of-contract vs rooms-per-night; next step vs average vs matched). `deposit_true_up` tiers 2 and 3 differ only by which room nights feed the same product, tier 1 is a different formula; the label holds. All `parameter` factors substitute a number.
- Every tier is stated in the rule with its condition and its value or method (no tier lives only in `compute`).
- Realism of conditions and outcomes (judged against hotel group-sales practice):
  - Grounded in practice: lead-time-tiered free reductions; deemed counting dates tied to addendum return; partial commitment of late or post-cut-off increases; rooming-list fill; staff/master-billed rooms counted as reserved; name-change substitutions; release/resale share; room-only damages basis when breakfast is included; individually guaranteed rooms carrying their own penalties; relationship relief for repeat stays at the hotel; late-payment surcharge; event-contract deposit consolidation; cumulative deposit true-up.
  - Loyalty-standing conditions (tier with recent stays, tier with enrolment tenure) are relationship proxies a brand could codify; recorded as observation O-G1.
  - **Not weighed by the line of business:** the linked Ashbury Rewards co-brand credit card as a condition on (a) the interim group deposit percentage (`rewards_relief`: "when it is active at Ashbury Rewards Titanium Elite or Ashbury Rewards Ambassador Elite and has an Ashbury Rewards co-brand card linked … when it is active at Ashbury Rewards Gold Elite or Ashbury Rewards Platinum Elite and has a co-brand card linked") and (b) the room nights kept back from the cut-off release (`late_name_holdback`: "when it is active with the Ashbury Rewards Premier co-brand card linked and at least holdback_credits_high elite night credits this year … when it is active with either co-brand card linked and at least holdback_credits_low elite night credits this year"). A group contract's deposit schedule and its cut-off inventory release are set by the signed contract, payment history and pickup; the organiser contact's personal bank-issued co-brand card product is a consumer card benefit and plays no part in either. In `late_name_holdback` the second conjunct, the contact's personal elite night credits for the calendar year, is equally foreign to how many block rooms a hotel keeps past cut-off. This is finding F-G2.
- Counts after the tests: striking the two factors of F-G2 leaves interim with 3 factors (late_receipt_load, event_deposit_relief, deposit_true_up — below the floor of 4) and cut-off with 4 factors, none labelled `method` (below the floor of 1). The other three policies keep their declared counts.
- Per-task multi-source and cross-difficulty coverage (the two task trees): {reduction, interim} has multi-source factors (reduction_percentage, courtesy_room_nights, deposit_true_up) and cross-difficulty factors (courtesy_room_nights → loyalty; rewards_relief → loyalty). {increase, cut-off, cancellation} has multi-source factors (staff_room_nights, release_share, …) and cross-difficulty factors (booking ×7, loyalty ×2). After F-G2, each tree still holds a loyalty-reading factor (courtesy_room_nights; tenure_scale_step) and booking-reading factors.

### findings

- **F-G1 — SOURCE-POLICY observation (no task world reaches it).** Symptom: the rule's "the percentage is that of the step one longer lead than the matching step" has no referent when the notice falls on the top step; `next_pct` in compute returns the top step itself for every block type, so the tenure ladder's three tiers coincide there. Root cause: compute supplies a basis the rule does not state. Evidence: rule sentence quoted above; `next_pct` expression (e.g. `10 if scale_days >= 181` for Social, `25 if scale_days >= 181` for Wedding). Consequence: none demonstrable here — task 1's notice is 17 days from arrival (bottom step). Bears on: none of the two tasks.
- **F-G2 — SOURCE-FACTOR RED (unreal ladder condition).** Symptom: two factors decide their tier by the organiser contact's linked co-brand credit card (and, for the holdback, the contact's personal elite night credits this year). Root cause: the conditions are not ones hotel group sales weigh for a group deposit or a cut-off release. Evidence: `group_ext_interim_deposit_amount.rule` rewards-relief sentence and `factors[rewards_relief]`; `group_ext_cutoff_release_nights.rule` late-name holdback sentence and `factors[late_name_holdback]`. Consequence: the two factors do not count; the interim computation falls to 3 factors (floor 4) and the cut-off computation loses its only `method` factor (floor 1). Bears on: task 0 (rewards_relief), task 1 (late_name_holdback). The per-task files demonstrate what each costs.
- O-G1 — loyalty-tier/tenure conditions (`courtesy_room_nights`, `tenure_scale_step`) and loyalty-tier-only parts of `rewards_relief` are relationship proxies a brand could codify; personal loyalty of the contact applied to a company's contract (tour operator in task 1) is at the edge of practice. Observation.
- O-G2 — increase `overwrite: []`: the schema meaning of `contracted_room_nights` reads as full commitment, which equals the policy's baseline; no base sentence is contradicted. Observation.
- O-G3 — interim overwrite[0] replaces "Each scheduled deposit is received once." by an interim-only sentence, so the signing-deposit half of the base dedup is no longer stated by the merged text. No task world pays a signing deposit. Observation.
- O-G4 — cancellation ← increase sentence says "a ledger entry that names it", condition says a `group_block_increase` entry; equivalent on the records. Observation.
- O-G5 — cut-off overwrite supersedes the base release sentence without scoping it to rooming-list blocks, while the ext rule speaks only of rooming-list blocks; call-in blocks are left without a stated release quantity. No task world exercises it. Observation.
- O-G6 — docstrings point at "the group block lookup" / "the contract addendum lookup" as id provenance. No sequence statement. Observation.
- O-G7 — base `group_contracting` and `group_deposit_schedule` carry cross-problem orders (signing waits on the signing deposit; apply waits on actualization) that ground no edge here. Observation.
- O-G8 — reduction rule "implemented one at a time in the order they were issued, so the addendum implemented is the most recently issued reduction addendum whose status is signed" reads two ways if two signed reductions are both unimplemented (oldest-first vs latest); compute takes the latest signed and does not exclude implemented ones. Task 0 has exactly one unimplemented signed reduction, so no consequence there. Observation.
- O-G9 — the cut-off release is dated `cutoff_date` while its inputs (held nights after an increase entry dated later) are read at the handling moment, so the ledger shows a release dated before the increase it already reflects. Bookkeeping oddity; no second answer. Observation.

## closing_checklist

Written after both reveals (2026-10-05, about 16:25Z). The difficulty does **not** close: both tasks carry SOURCE-FACTOR RED from F-G2.

- Per-task files `0.md`, `1.md` correspond one-to-one with `tasks/0.json`, `tasks/1.json`; `_difficulty.md` alongside; first revision, no older revisions. Comparison sections: task 0 — SOURCE-FACTOR RED; task 1 — SOURCE-FACTOR RED (the other three relationships PASS in both).
- Coverage and scope: `charter_scope` of task 0 = {group_ext_reduction_room_nights, group_ext_interim_deposit_amount}; task 1 = {group_ext_increase_commitment, group_ext_cutoff_release_nights, group_ext_cancellation_damages}. Pairwise disjoint, jointly all five extended policies, each scope spanning its whole tree. Task tools and GT closed; uuid8s independent (see § action_binding_and_uuids).
- Trees: task 0 — 1 prerequisite problem, 1 value_input edge, user write (deposit payment), acyclic; task 1 — 2 prerequisite problems, 3 value_input edges, user write (cancellation signature), acyclic. Difficulty-wide graph is a DAG (two components, no cross-task reference).
- Factors: every declared factor bears weight on its task's world against an honest baseline, and every whole-baseline fall-back is definite and differs from gold (task files § factor_weight). **Fails** the realism test for two factors (F-G2), leaving the interim computation with 3 factors (floor 4) and the cut-off computation with no `method` factor (floor 1).
- Instantiation-stage gates re-run on the final form: not applicable — the artifacts are not in final form while F-G2 stands. The snapshot this audit entered on is `/tmp/env0036_views/group_room_block_contracts/GATES.txt` (all seven OK).

## revision_2

### charter_global_frozen (revision_2)

- Frozen: 2026-10-05, written between 23:42:28Z and 23:43:51Z, before either task's round-2 GT was read. Auditor: same independent auditor as round 1.
- Hashes: `group.extended.yaml` sha256 `c79ab9f8eead9d8ec20801c9913e3d1bfa1e0bbc712354743f93dd3c86f526b7` (**changed** from `3b91a10c…`), `task_tools.py` sha256 `515bfd89899efe3151a48fdcc4f67b4a2824dde9c9311e21322eb728df493809` (unchanged). The charter moved, so every charter-global section below is re-derived on the new text. § action_binding_and_uuids rests on the tool module, which did not change; it was re-checked against the new charter's `(target_tool, computes)` pairs.
- Entry conditions: fresh gate snapshot `/tmp/env0036_views/group_room_block_contracts/GATES.txt` shows all seven OK (traceability deferred to the render stage); rebuilt masked views and HASHES.txt supplied. Complete.
- Base copy: lines 1-1250 still byte-identical to `blueprint/products/group.yaml`.
- Masked and not read before this freeze: all GT fields of `tasks/*.json`, `worklog.md` (both modified 16:55; not opened), sibling difficulties, other scenarios. The reworker's claims came by item id only and were not used as evidence.
- What changed in the charter (located by re-reading every extended policy):
  1. `group_ext_interim_deposit_amount`: `rewards_relief` (loyalty tier + co-brand card) is removed. A new factor `reduction_exposure_load` (parameter) replaces it, with this rule sentence: "The reduction exposure load follows how far signed reductions have already shrunk the contract, counted as the room nights of the block's reduction entries against the room nights of its allocation entry: when they are at least high_exposure_pct percent of the allocation, the load is exposure_load_high_points percentage points; when they are at least low_exposure_pct percent but below high_exposure_pct percent, it is exposure_load_low_points percentage points; below low_exposure_pct percent there is no load." The applicable-percentage sentence and overwrite[1] now read "the late-receipt load, the reduction exposure load and the event-deposit relief, both loads added and the relief subtracted". Overwrite[0] now reads "each kind of scheduled deposit is received at most once on a block, so a block whose ledger already carries a receipt of the signing kind or of the interim kind takes no second receipt of that kind." The loyalty cross-category read is removed.
  2. `group_ext_cutoff_release_nights`: `late_name_holdback` (method) now takes its tier from pickup: "counted as the room nights of the organiser's confirmed Group Block Rate reservations naming the block against the contracted room nights: when they are at least strong_pickup_pct percent of the contracted room nights, the holdback is holdback_pct percent of the contracted room nights, rounded down; when they are at least fair_pickup_pct percent but below strong_pickup_pct percent, the holdback is holdback_rooms rooms for every night of the block; below fair_pickup_pct percent there is none." Its compute binding is `pickup_nights`, `cross_difficulty: booking`, and the loyalty cross-category read is removed. The overwrite is split in two: the first part now states that "a block whose attendees call in individually is outside this policy and keeps the release of every held room night not yet reserved by an attendee, made on the cut-off date", and the same scope sentence is added to the rule.
  3. `group_ext_cancellation_damages`: the first prerequisite sentence now reads "Cancellation damages are not worked out until each signed increase addendum on the block is matched by an increase entry on the block ledger that names it." A new rule sentence now quotes the `next_pct` basis: "When the matching step is the top step of the block type's cancellation_scale, no step has a longer lead and the step one longer lead is the top step itself."
  4. `group_ext_reduction_room_nights`: "Signed reduction addenda are implemented one at a time in the order they were issued, so the addendum implemented is …" now reads "The addendum implemented is the most recently issued reduction addendum whose status is signed …" (rule and compute_basis).
  5. `group_ext_increase_commitment`: unchanged.

### policy_conflict_scan (revision_2)

Same five policies, targets and computes. No new overlap: the exposure load reads only `group_block_reduce` and `group_block_allocate` rows of the block. The holdback reads the same confirmed GBR nights as `named_nights`, under a separate binding name. Cross-category reads are now loyalty (reduction courtesy, cancellation tenure), meeting (interim event relief) and booking (increase uplift, cut-off ×4, cancellation ×3), all declared. Scope partition unchanged: {reduction → interim}, {increase → cut-off → cancellation, increase → cancellation}. No conflict.

### rule_compute_equivalence (revision_2)

- Re-swept every binding of the five policies against `compute_basis` and back on the new text. New or changed bindings: `reduced_nights_total`, `exposure_base`, `exposure_load` and `applicable_pct` (interim); `pickup_nights` and `holdback` (cut-off); `next_pct` (cancellation, now quoted by the new top-step sentence). Each is quoted and implemented one-to-one.
- `matched_pct`/`next_pct` still hard-code each block type's scale. Re-checked against the six variants: equal.
- Each factor's tiers appear in the rule, in the ladder and in the `decides` branches, in both directions (25 factors).
- The charter compute was evaluated on both round-2 worlds and compared with an independent hand derivation. They agree (task files, revision_2).

### action_binding_and_uuids (revision_2)

The tool module is unchanged (hash above). The five `(target_tool, computes)` pairs are unchanged and each is claimed by exactly one policy. The uuid8s are unchanged, distinct and not patterned. No function body judges a prerequisite. Round-1 conclusion carried, re-checked.

### prerequisite_graph (revision_2)

The four edges are unchanged in problem, kind, gate, form and resolved_by. Every `policy_source` is again located verbatim in its own rule; the cancellation ← increase sentence was re-located in its new wording. Gate bindings exist (`revenue`, `held_nights`, `contracted_nights`, `released_nights`). The graph is acyclic, has no action-form edge and no authoring-viewpoint phrasing.

### prerequisite_sentences (revision_2)

- The four sentences pass the four-point test as in round 1.
- Cancellation ← increase now names "an increase entry on the block ledger". It is word-for-word as strong as its `condition` (a `group_block_increase` entry), so round-1 O-G4 is closed. Its sole writer is still the increase implementation.
- No rule restates another problem's sentence, and no new cross-problem order was introduced. The new exposure-load sentence reads reduction entries as a value; it states no order.

### override_declarations (revision_2)

- interim vs `group_deposit_schedule`: as in round 1, every conflicting base sentence is named. The once-rule replacement now keeps both deposit kinds, so round-1 O-G3 is closed. The new load changes only the applicable percentage, which overwrite[1] declares.
- cut-off vs `group_cutoff`: the base release sentence is now superseded in two named parts. The merged text gives rooming-list blocks the ext quantity and keeps the base full release for call-in blocks. Round-1 O-G5 is closed.
- cancellation vs `group_cancellation`: unchanged declarations; the new top-step sentence is ext-only and conflicts with no base sentence.
- reduction and increase: unchanged conclusions (the increase keeps round-1 O-G2).
- No undeclared override.

### factor_ladders (revision_2)

Changed rows only; all other rows as in round 1, re-checked on the new text.

| policy | factor | effect | decides | tiers | multi-source | cross_difficulty |
| --- | --- | --- | --- | --- | --- | --- |
| interim | reduction_exposure_load | parameter | exposure_load | 3 | no (one ratio condition) | — |
| cut-off | late_name_holdback | method | holdback | 3 | no (one ratio condition) | booking |

- Counts: reduction 5 (4 parameter, 1 method); interim 4 (3 parameter, 1 method); increase 5 (4, 1); cut-off 5 (4, 1); cancellation 6 (5, 1). All within 4–6, each with ≥ 2 parameter and ≥ 1 method.
- Fall-through tiers equal their baselines (exposure 0; holdback 0). Tier values differ (5 / 2.5 / 0; share of contract / rooms per night / none). Labels are honest: the holdback tiers change the algorithm; the exposure tiers change a number.
- Realism of the new conditions and outcomes:
  - A higher interim deposit for a block whose signed reductions have already shrunk it is a risk-based deposit adjustment a hotel can apply to a contracting group.
  - A post-cut-off holdback scaled to how strongly the rooming list has picked up the contract is the ordinary basis on which hotels keep a few rooms for late names.
  - Neither condition holds of every customer who reaches the write.
  - Round-1 F-G2 is closed: no factor of the charter now takes its tier from a co-brand card or from the contact's personal elite night credits.
- Round-1 O-G1 is kept as an observation: courtesy room nights and the tenure scale step still rest on loyalty tier with recent stays or enrolment tenure.
- New edge note (O-G10): with the top-step sentence added, `tenure_scale_step`'s three tiers yield the same percentage when the notice falls on the top step. The methods differ but the outcomes coincide on that sub-domain. Task 1's notice is on the bottom step, so this is an observation.
- Task-level coverage after the change:
  - {reduction, interim}: multi-source reduction_percentage, courtesy_room_nights, deposit_true_up; cross-difficulty courtesy_room_nights (loyalty).
  - {increase, cut-off, cancellation}: multi-source staff_room_nights, breakfast_rate_basis, card_guaranteed_exclusion, release_share, late_increase_share; cross-difficulty booking factors and tenure_scale_step (loyalty).

### findings (revision_2)

- F-G1 — **closed.** The top-step referent is now a rule sentence quoted by `next_pct`'s compute_basis. Residual: O-G10 (tiers coincide on the top step), not reached by any task world.
- F-G2 — **closed.** Both co-brand-card factors are gone. Their replacements (`reduction_exposure_load`; pickup-based `late_name_holdback`) pass the realism, label, ladder and count tests above. Per-task weight is demonstrated in the task files.
- O-G1 kept. O-G2 unchanged. O-G3 closed. O-G4 closed. O-G5 closed. O-G6 unchanged. O-G7 unchanged.
- O-G8 changed, residual. The ordering clause is gone, so the two-reading problem is gone. The rule and compute still choose "the most recently issued reduction addendum whose status is signed" without excluding one already named by a reduction entry. On a block whose latest signed reduction is already implemented, that sentence and "each signed addendum is implemented once" would point at an addendum with nothing left to do. Task 0's latest signed reduction is unimplemented, so there is no consequence there. The increase rule has the same shape; task 1's only signed increase is unimplemented. Observation.
- O-G9 unchanged (release dated at cut-off while reflecting a later increase entry).
- O-G10 new, observation (above).
- No new RED.

### closing_checklist (revision_2)

Written after both round-2 reveals (2026-10-05, about 23:45Z). Both tasks PASS all four relationships; the difficulty passes the source-layer audit.

- Per-task files `0.md` and `1.md` correspond one-to-one with `tasks/0.json` and `tasks/1.json`, and `_difficulty.md` sits alongside them. The round-1 text is left untouched above each `## revision_2`. Each revision_2 comparison carries a PASS.
- Coverage and scope:
  - `charter_scope`: task 0 = {reduction, interim}; task 1 = {increase, cut-off release, cancellation}.
  - The scopes are pairwise disjoint and together cover all five extended policies, each scope spanning its whole tree.
  - Task tools and GT are closed; uuid8s are independent and frozen (tool module unchanged since round 1).
- Trees:
  - Task 0: 1 prerequisite problem, 1 value_input edge, user write (deposit payment), acyclic.
  - Task 1: 2 prerequisite problems, 3 value_input edges, user write (cancellation signature), acyclic.
  - The difficulty-wide graph is a DAG.
- Factors:
  - Every computation declares a self-sufficient baseline and 4–6 factors: reduction 5, interim 4, increase 5, cut-off 5, cancellation 6, each with ≥ 2 parameter and 1 method.
  - Every ladder has 3 tiers stated in full in its rule, with distinct outcomes on the task worlds.
  - Conditions and outcomes are ones the business holds (F-G2 closed; O-G1 kept as an observation).
  - Each task has ≥ 1 multi-source and ≥ 1 cross-difficulty factor with seeded rows.
  - Every factor bears weight against an honest baseline, and every whole-baseline fall-back is definite and differs from gold.
- Instantiation-stage gates on the final form: this auditor does not run gates. The orchestrator's post-rework snapshot `/tmp/env0036_views/group_room_block_contracts/GATES.txt`, taken on the hashes audited here (charter `c79ab9f8…`, tools `515bfd89…`, views `bba22229…` / `c7c85058…`), shows EXTENDED, TASK TOOL CONTRACT, REPLAY, SOLVABILITY, COMPUTE, GROUNDING and SCOPE all OK. check_traceability is deferred to the render stage.
- Open observations carried (not grounds for rework): O-G1, O-G2, O-G6, O-G7, O-G8 (residual), O-G9, O-G10; O-T0-1, O-T0-3; O-T1-2, O-T1-3.
