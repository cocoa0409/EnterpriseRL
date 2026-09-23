# Policy-task audit — catering_order_desk / charter-global

## charter_global_frozen

- freeze time: 2026-09-22 (session clock), written **before any task's GT fields were read**.
- auditor: independent source-layer auditor (not the instantiating agent).
- frozen inputs and their hashes:
  - `sha256 cc35786a31122e98b365aaf063dd422609779f2cbfb6960c2d3b0bc3ddba25d0` — `env/env_0013_workplace_dining_and_catering_provider/tasks/catering_order_desk/catering.extended.yaml`
  - `sha256 961546e7a5513bd4198163c0972cf4adb761d752cad8d177bdc912efeaf08419` — `env/env_0013_workplace_dining_and_catering_provider/tasks/catering_order_desk/task_tools.py`
  - masked task views (built by the coordinator, verified by hash):
    `f2169ec094568815fa32c8895b3b77d5f358e7235f5706d19287f8b45dbf3a74` (0), `3b419c35753c4c9a7d5e58b9f5c700f8c3bc121eac833d5491b80e462b5c124f` (1)
- fields permitted while this section was written: `blueprint/blueprint.yaml`, `blueprint/db_schema.json`, `blueprint/share_tools.py`,
  `blueprint/products/{catering,cafe,banquet}.yaml`, the whole of `catering.extended.yaml` (base copy + `extended_policies`, including
  `rule` / `compute` / `compute_basis` / `overwrite` / `prerequisite` / `factors` / `baseline`), `task_tools.py`, and the masked views'
  `frozen_time` / `user_scenario` / `initial_state`.
- fields explicitly masked and **not read** before this file was on disk: every task's `evaluation_criteria`, `computations`,
  `design_rationale`, `solvability_contract`, `prerequisite_closure`, `charter_scope`, `required_documents`, `db_closure`.
- contamination: none. No recursive grep was run whose path scope included `tasks/*/tasks/*.json`; the only task content read came
  from the coordinator's masked views.

### entry conditions (step 0)

The brief carried the instantiation-stage gate snapshot with actual output lines for `check_extended.py`, `check_task_tools.py`,
`replay_tasks.py --check`, `check_solvability.py`, `check_compute.py`, `check_grounding.py` and `check_cross_fire.py`, all green, plus
the two masked views with hashes and the two source hashes above. `check_traceability.py` is legitimately absent (no published KB yet).
Entry conditions are **complete**; the gates were cited, not re-run. A machine green light is the qualification to enter this audit,
not evidence of correctness.

### policy_conflict_scan

Scope of the difficulty: category `catering`, four extended policies, claimed by two tasks.

| policy | subject | trigger | computes | target_tool | owner |
| --- | --- | --- | --- | --- | --- |
| `catering_ext_delivered_order_invoicing` | `catering_order_invoiced` | state_due | `invoice_amount_usd` | `raise_catering_invoice_cb57dc9d` | agent |
| `catering_ext_agreement_closure_settlement` | `catering_agreement_closed` | on_request | `closing_settlement_usd` | `confirm_agreement_closure_1e20ba9d` | user |
| `catering_ext_client_cancellation_registration` | `catering_order_cancelled` | on_request | `standing_order_value_usd` | `register_order_cancellation_69ffeeb0` | user |
| `catering_ext_cancellation_charge_assessment` | `catering_cancellation_fee_posted` | state_due | `cancellation_charge_usd` | `post_cancellation_charge_b7aa0639` | agent |

- **Base copy is verbatim compatible.** `category`, `display_name`, `binding`, `lifecycle`, `accounts`, `parameter_schema`, `variants`,
  `events`, `measures` and `policies` in `catering.extended.yaml` are semantically identical to `blueprint/products/catering.yaml`
  (checked by loading both YAMLs and comparing after whitespace normalisation — the only differences are block-vs-flow style from a
  YAML re-dump). No base sentence has been rewritten.
- **Subjects are pairwise disjoint** across the four extended policies; no two policies claim the same `(target_tool, computes)` pair
  and no two claim the same event subject.
- **Task scopes** (root + its prerequisite problem): task 0 = {`…closure_settlement`, `…delivered_order_invoicing`},
  task 1 = {`…cancellation_charge_assessment`, `…client_cancellation_registration`}. Pairwise disjoint and jointly complete over the
  four extended policies.
- **Eligibility / time anchors / terminal states**: the four policies anchor on distinct days (`the day the invoice is raised`,
  `the day it closes`, `the day notice is given` twice) and write distinct terminal states (an invoice entry + a raised receivable;
  `status=closed` + a stamped closing figure; a cancellation entry; a charge entry + a raised receivable). No two reach different
  conclusions about the same field.
- **Cross-category read boundaries**: `catering_ext_delivered_order_invoicing` and `catering_ext_agreement_closure_settlement` declare
  `cross_category: [{category: cafe, as: branch, reads: [status, variant_name]}]`; `catering_ext_client_cancellation_registration`
  declares `[{category: banquet, as: branch, reads: [status, variant_name]}]`; `catering_ext_cancellation_charge_assessment` declares
  `[]` and its `compute` performs no cross-category read. Declared reads match the reads actually performed — with the join-key
  defect recorded in finding **F-4** below.

No policy-level contradiction was found between the four extended policies themselves. The findings below are base↔extended and
rule↔compute defects.

### rule_compute_equivalence

Check 2 was run mechanically and then by hand over all four policies:

- Every `compute` binding has a `compute_basis` entry, and every `compute_basis` key is a `compute` binding
  (invoicing 21/21, closure 22/22, registration 20/20, charge 16/16; no missing, no extra).
- Every sentence quoted in each `compute_basis` value is verbatim present in that policy's `rule` (string check after whitespace
  normalisation: zero mismatches across all four policies).
- Every sentence of each policy's `baseline.rule` is verbatim present in that policy's `rule` (zero mismatches across all four).
- Every `factors[].ladder` tier was matched against the `rule` by hand. All tiers are stated in prose in their policy's `rule`
  **except one**: see finding **F-1**. Concretely, `catering_ext_cancellation_charge_assessment.factors[notice_counting_basis]`
  declares a fall-through method "the notice given is counted from the day after notice was given to the service day, at twenty-four
  hours to the day", implemented in `compute` as `RND((notice_days - 1) * 24, 2)`, and **no sentence of that policy's `rule` states it**.
- Caps, floors and rounding conventions are carried in both faces: `MX(0.0, …)` ← "and never less than nothing";
  `MN(…, P('late_fee_cap_usd'))` ← "is held to the late charge ceiling printed against the catering service level, the ceiling applying
  after the percentage has been taken"; every `RND(…, 2)` ← "rounded to two decimal places only at the end" / "and rounded to two
  decimal places".
- Sweep back: no `compute` binding introduces a window, filter, base or grouping absent from its policy's `rule`, and no `rule`
  sentence promises a quantity `compute` never produces — **except** F-1, and the minor gap recorded as observation **O-3**.

### action_binding_and_uuids

- `(target_tool, computes)` pairs: `raise_catering_invoice_cb57dc9d`/`invoice_amount_usd`,
  `confirm_agreement_closure_1e20ba9d`/`closing_settlement_usd`, `register_order_cancellation_69ffeeb0`/`standing_order_value_usd`,
  `post_cancellation_charge_b7aa0639`/`cancellation_charge_usd`. Each pair is claimed by exactly one policy; no pair is shared.
- uuid8s: `cb57dc9d`, `1e20ba9d`, `69ffeeb0`, `b7aa0639`. Four distinct 8-hex tokens with no common prefix, no shared tail, no
  ordinal or adjacent-value relation, no sign of batch derivation from a seed. Each is frozen with its tool.
- Tool bodies (`task_tools.py`) perform one atomic write each and **judge no prerequisite**: `raise_catering_invoice_cb57dc9d` creates
  the invoice row and bumps `receivable_balance_usd` unconditionally; `confirm_agreement_closure_1e20ba9d` sets `status="closed"`,
  `closed_date` and `receivable_balance_usd` unconditionally; `register_order_cancellation_69ffeeb0` creates the cancellation row
  unconditionally; `post_cancellation_charge_b7aa0639` creates the charge row and bumps the receivable unconditionally. No body reads
  a status, counts history, derives an amount, raises, refuses or hints.
- Docstrings state no position in a sequence, name no other tool, and carry no `before` / `after` / `first` ordering word about another
  problem. (`post_cancellation_charge_b7aa0639` describes its object as "a pulled catering order", which names the business object the
  charter itself names, not an ordering — recorded as observation **O-5** only.)

### prerequisite_graph

Two edges, both declared; the other two policies carry `prerequisite: []` (filled in, not omitted).

| blocked policy | problem | kind | gate | form | resolved_by |
| --- | --- | --- | --- | --- | --- |
| `catering_ext_agreement_closure_settlement` | `catering_ext_delivered_order_invoicing` | `value_input` | `invoiced_12m` | `state` | `raise_catering_invoice_cb57dc9d` |
| `catering_ext_cancellation_charge_assessment` | `catering_ext_client_cancellation_registration` | `value_input` | `cancelled_value` | `state` | `register_order_cancellation_69ffeeb0` |

- Both `problem` values point at another extended policy id in this file; neither points at a base policy or at itself.
- Graph is acyclic (two disjoint single edges; no cross-task reference, so the difficulty-wide graph is a DAG).
- `form: state` on both; neither carries `fallback_reason`, which is correct (it is required exactly on action-form edges).
- `resolved_by` equals the depended-on policy's own `target_tool` in both cases, and each genuinely brings the `effect` about:
  `raise_catering_invoice_cb57dc9d` creates the `catering_order_invoiced` row that `invoiced_12m` sums;
  `register_order_cancellation_69ffeeb0` creates the `catering_order_cancelled` row that `cancelled_value`, `notice_day`,
  `service_day` and `notice_channel` all read.
- `kind: value_input` matches `gate` in both: `invoiced_12m` is a real binding of the closure `compute`; `cancelled_value` is a real
  binding of the charge `compute`. Neither is `result`.
- `condition` is neither strengthened nor weakened relative to the quoted sentence (see `prerequisite_sentences`).
- No authoring-viewpoint phrasing ("in this task", "at the opening", "the current world") appears anywhere in either `prerequisite`
  block.

### prerequisite_sentences

**Edge A — `catering_ext_agreement_closure_settlement` ← `catering_ext_delivered_order_invoicing`**

`policy_source`: *"The closing figure is not fixed until every order delivered on the agreement carries an invoice entry."*

1. It is a verbatim sentence of the blocked policy's **own** `rule` (second sentence of `catering_ext_agreement_closure_settlement.rule`). ✔
2. Ordering connective: **"until"**, joining that policy's own result ("the closing figure") to what it waits on. ✔
3. Declared `form: state`; what it waits on — "every order delivered on the agreement carries an invoice entry" — is a record-visible
   state in the words the tables and finders use (`catering_orders` rows of the delivered and invoiced families, as
   `find_catering_orders` returns them). It names no performer, no tool, no action. ✔
4. No tool name, no policy id, no snake_case token, no row id. ✔
5. Strength and scope match `condition` ("every order on the agreement that carries a delivery entry also carries an invoice entry
   standing against the same order reference") — an open set stated open, neither widened nor narrowed. ✔
6. **Exactly one write of this difficulty brings that state about**: `raise_catering_invoice_cb57dc9d` is the only tool in
   `task_tools.py` (and the only `target_tool` in the charter) that creates a `catering_order_invoiced` row. No second candidate. ✔
7. Derivation in one reading: the sentence says the closing figure waits on delivered orders carrying invoice entries → the records
   show a delivered order with no invoice entry against its order reference → the only policy whose own `rule` describes writing an
   invoice entry for a served order is `catering_ext_delivered_order_invoicing` ("The amount invoiced for a catering order that has
   been served …") → its `target_tool` is the resolving action. Single reading. ✔
8. The blocked `rule` carries nothing else about the dependency (no second wording, no tool name, no other policy's id), and the
   depended-on `rule` does not restate the sentence. ✔

**Edge B — `catering_ext_cancellation_charge_assessment` ← `catering_ext_client_cancellation_registration`**

`policy_source`: *"The cancellation charge is fixed only after a cancellation entry stands against the order, carrying the value the
order held when notice was given."*

1. Verbatim second sentence of `catering_ext_cancellation_charge_assessment.rule`. ✔
2. Ordering connective: **"only after"**. ✔
3. `form: state`; "a cancellation entry stands against the order, carrying the value the order held when notice was given" is
   record-visible (`catering_orders` row of the cancelled family with its `amount_usd`), no performer or tool. ✔
4. No tool name / policy id / snake_case / row id. ✔
5. Matches `condition` exactly in strength and scope. ✔
6. **Exactly one write** creates a `catering_order_cancelled` row: `register_order_cancellation_69ffeeb0`. ✔
7. Single reading: sentence → the records show the order carries a placement and an amendment but no cancellation entry → the only
   policy whose own `rule` describes fixing "the value standing on a catering order at the moment the client gives notice of
   cancellation" is `catering_ext_client_cancellation_registration` → its `target_tool` resolves it. ✔
8. The blocked `rule` carries no second wording of the dependency. **But** the depended-on policy's `rule` opens with
   *"The value standing on a catering order at the moment the client gives notice of cancellation is what any later cancellation
   charge rests on …"* — a forward statement of the same cross-problem relation, with the ordering word "later", written on the
   depended-on side. Recorded as observation **O-2**.

### override_declarations

Sentence-by-sentence sweep of each extended policy against every entry of its `base_policy_refs`. "follows" = extended reaches the
same conclusion on the quantity that gets scored; "declared" = named in that policy's `overwrite`; "undeclared" = handled differently
with no `overwrite` entry.

**`catering_ext_delivered_order_invoicing`** — refs `catering_invoicing_terms`, `catering_combination_cafe_interaction`.

| base sentence | verdict |
| --- | --- |
| "How catering is invoiced follows the consolidation basis printed against the service level: a per-order basis … a weekly basis … a monthly basis …" | not named in `overwrite`; extended invoices **one served order per call** and says nothing about consolidation. Observation **O-1**. |
| "An order is only invoiced once it has been delivered …" | follows (extended reads `LATEST(… catering_order_delivered)`). |
| "The invoiced amount is the order value after the standing discount and the volume discount step the client's trailing **ninety-day** catering spend reaches, then the service charge, the delivery fee, any rush surcharge, any peak surcharge and any additional service hours, in that order." | **declared** (`overwrite[0]`). |
| "The standing discount and the volume discount are added together rather than the better of the two being taken, and neither is applied to the delivery fee, the rush surcharge or the peak surcharge." | follows (`total_discount_pct = F('standing_discount_pct') + volume_discount_pct`; the discount touches only `discounted_food`). |
| "Where the client's purchase order reference is recorded on the agreement it is quoted on every invoice …" | inherited untouched; no scored quantity. |
| "A consolidated invoice that gathers orders delivered under two different service levels is not raised …" | follows. |
| "Where the same client holds an active workplace cafe management contract whose service model permits catering out of the cafe kitchen, and the delivery site on the order is that cafe's site, the delivery fee is not charged …" | **declared** (`overwrite[1]`). |
| "Where that cafe contract does not permit catering out of its kitchen, the order is produced at the district kitchen and **the ordinary delivery fee applies however close the cafe is**." | **undeclared**: extended's `standing_round_delivery_charge` can set `delivery_fee_charged` to `0.0` or to half the printed fee for a client whose cafe does not permit catering out of its kitchen. Finding **F-3**. |
| "Where the same client holds an active private event and banquet agreement at the delivery site, an order whose guest count exceeds the largest guest count printed against the catering service level is placed as an event booking …" | inherited; not reached on either task's world. |
| "A catering agreement and an unattended micro market at the same site sit side by side without interaction …" | follows. |
| "Where the cafe contract at the delivery site stands suspended, catering out of that kitchen stops with it and orders are produced at the district kitchen at the ordinary delivery fee until service resumes." | consistent with extended's `cafe_status == 'active'` test for the concession; extended takes the concession on the service charge, base on the delivery fee — the switch is the one already declared in `overwrite[1]`. |

**`catering_ext_agreement_closure_settlement`** — ref `catering_hold_and_closure_terms`.

| base sentence | verdict |
| --- | --- |
| "A credit hold is applied by the system when exposure or arrears cross the limit …" | inherited; not reached. |
| "A hold, a reinstatement or a closure is only worked while the agreement stands active, on credit hold or closed, and never while it is still in credit review …" | follows (inherited eligibility gate `lifecycle_state`). |
| "Only the client may end a catering agreement, and **the desk records the request for the client to confirm** rather than closing the agreement on their word alone." | half-followed: the closure tool is `owner="user"`, so "only the client may end" is honoured; but no tool in this difficulty writes a `catering_change_requests` row, so "the desk records the request" is inherited and unimplementable. Observation **O-4**. |
| "Notice to end the agreement is the number of calendar days printed against the service level, and orders already accepted for service days inside the notice period are served rather than cancelled." | **declared** (`overwrite[1]`). |
| "An agreement is not closed while any order stands accepted and unserved; those orders are served or cancelled on the ordinary cancellation terms first, and the agreement closes once none remain." | not named in `overwrite`; extended says nothing about it. Inherited in full — whether it bites is a per-task fact, checked in each task's file. |
| "Where the client's annual spend for the agreement year has not reached the minimum printed against the service level, the shortfall is settled on the final invoice rather than waived at closure." | **declared** (`overwrite[0]`). |
| "A closed agreement keeps its invoices, credits and history …" | follows. |

**`catering_ext_client_cancellation_registration`** — refs `catering_cancellation_charges`, `catering_amendment_terms`, `catering_onboarding_terms`.

| base sentence | verdict |
| --- | --- |
| `catering_cancellation_charges`: "The order value the percentage is applied to is the value standing on the order at the moment notice is given, after every amendment already accepted, and never the value the order was first quoted at." | **declared** (`overwrite[0]`). |
| `catering_cancellation_charges`: "A cancellation is registered against the order on the day notice is given, and the registration may not be made later than the registration window …" | follows (`register_order_cancellation_69ffeeb0` stamps `notice_given_date = posted_date = ctx.now()`). |
| `catering_cancellation_charges`: remaining sentences (forced cancellation, delivered orders, free/within/same-day bands, repeat-cancellation) | belong to the charge policy, not to this one; judged there. |
| `catering_amendment_terms`: "A reduction in guest count inside the free reduction band … does not reprice the order; a reduction beyond that band reprices the order to the reduced count, and a reduction asked for after the deadline does not reprice it at all …" | **declared** (`overwrite[1]`). |
| `catering_amendment_terms`: "**Every amendment rewrites the order value, and the value that governs any later cancellation charge is the value on the order at the moment notice of cancellation is given.**" | **undeclared**: extended reduces that value by the total concession rate before it is written. Finding **F-2**. |
| `catering_amendment_terms`: "An order may be amended until the guest count deadline …", "An increase in guest count is accepted up to the increase ceiling …", "A change of menu package inside the dietary lead hours …", "An amendment that raises the order value is not accepted while the agreement stands on credit hold …" | inherited untouched; none is reached on this difficulty's worlds (no amendment is written by any task tool here). |
| `catering_onboarding_terms`: "The standing discount recorded on the agreement is the discount printed against the service level unless a larger one was separately negotiated and written onto the agreement, in which case the written figure governs." | **declared** (`overwrite[2]`). |
| `catering_onboarding_terms`: remaining sentences (entry gate, credit review days, signed master agreement, spend-commitment downgrade, withdrawn application) | inherited untouched; none is reached. |

**`catering_ext_cancellation_charge_assessment`** — ref `catering_cancellation_charges`.

| base sentence | verdict |
| --- | --- |
| "What a cancellation costs is set by how much notice the client gave, measured in whole hours from the day the client gives notice of the cancellation to **the service start time on the service date**." | **declared** (`overwrite[0]`). |
| "Notice at or beyond the free-cancellation hours printed against the service level carries no charge at all; notice inside that window but before the service day carries the within-notice percentage …; and notice on the service day itself carries the same-day percentage …" | follows (`notice_band_rate`). |
| "The order value the percentage is applied to is the value standing on the order at the moment notice is given …" | follows (`cancelled_value = LATEST(… catering_order_cancelled)`, which is what the registration write put there). |
| "A cancellation is registered against the order on the day notice is given, and the registration may not be made later than the registration window …" / "Elapsed hours run continuously …" | inherited; satisfied. |
| "A cancellation forced by Larkspur Table … carries no charge whatever the notice given." | inherited; not reached. |
| "Where the same agreement has already cancelled inside the chargeable window four times in the rolling twelve months, the within-notice percentage is charged even on notice that would otherwise have been free …" | **declared** (`overwrite[1]`). |
| "A cancellation charge is only raised against an order that has not been delivered …" | follows. |

### factor_ladders

Structure only. Whether a factor bears weight is a per-task fact and lives in each task's `factor_weight`.

| policy | factors | `parameter` | `method` | multi-source tiers | `cross_difficulty` |
| --- | --- | --- | --- | --- | --- |
| `…delivered_order_invoicing` | 5 | 4 (`volume_step_earned`, `kitchen_service_concession`, `rush_percentage_carried`, `standing_round_delivery_charge`) | 1 (`spend_counting_window`) | `volume_step_earned` (spend ∧ invoiced-order count), `kitchen_service_concession` (cafe status ∧ cafe model), `rush_percentage_carried` (lead time ∧ delivery count), `standing_round_delivery_charge` (delivery count ∧ delivered site) | `kitchen_service_concession` → **cafe** |
| `…agreement_closure_settlement` | 5 | 4 (`programme_spend_benchmark`, `shortfall_share_due`, `closing_late_charge_rate`, `early_exit_charge_share`) | 1 (`counted_spend_basis`) | `programme_spend_benchmark` (months in force ∧ cafe status ∧ cafe model), `shortfall_share_due` (counted spend ∧ invoiced-order count), `closing_late_charge_rate` (days since payment ∧ unsettled), `early_exit_charge_share` (days to term end ∧ counted spend), `counted_spend_basis` (cancellation charges ∧ credits) | `programme_spend_benchmark` → **cafe** |
| `…client_cancellation_registration` | 4 | 2 (`free_reduction_band_standing`, `programme_concession_taken`) | 2 (`amendment_repricing_basis`, `standing_discount_selection`) | `free_reduction_band_standing` (months in force ∧ delivery count), `amendment_repricing_basis` (reduction vs band ∧ amendment lead), `programme_concession_taken` (banquet status ∧ package size) | `programme_concession_taken` → **banquet** |
| `…cancellation_charge_assessment` | 5 | 2 (`notice_band_rate`, `delivery_record_rebate`) | 3 (`notice_counting_basis`, `cancellation_counting_window`, `repeat_cancellation_rate_basis`) | `repeat_cancellation_rate_basis` (charges raised ∧ cancellations registered), `delivery_record_rebate` (delivery count ∧ cancelled value), `cancellation_counting_window` (unsettled ∧ recent payment) | none (task 1's cross-difficulty factor comes from the registration policy) |

- Counts are inside 4–6 everywhere, with ≥2 `parameter` and ≥1 `method` in every policy.
- Per task: task 0's computations carry ≥1 multi-source factor and 1 `cross_difficulty` (cafe); task 1's carry ≥1 multi-source and
  1 `cross_difficulty` (banquet). Both satisfied.
- Binding sets are pairwise disjoint within each policy (checked binding by binding), and no `decides` names `result`.
- Every ladder has exactly three tiers, the fall-through counted, and every fall-through tier is the policy's `baseline` value for
  that binding — **except `notice_counting_basis`**, whose fall-through is `(notice_days − 1) * 24` while its policy's `baseline.rule`
  states `notice_days * 24`. Finding **F-1**.
- Labels: every `method` tier changes an algorithm, window or anchor (`spend_counting_window` = window; `counted_spend_basis` = which
  ledger families enter the sum; `amendment_repricing_basis` = which entry the value is taken from and whether it is re-derived
  per guest; `standing_discount_selection` = which of two rates is taken; `notice_counting_basis` = the day the count anchors on;
  `cancellation_counting_window` = window). Every `parameter` tier substitutes a number into an unchanged formula.
  `repeat_cancellation_rate_basis` is labelled `method` and its first tier substitutes a fixed percentage while its second changes the
  algorithm (take the higher of two) — mixed, recorded as observation **O-6**, not a red light.
- Distinct outcomes per ladder: every ladder's three tiers select three different values or methods **as written**, with one
  exception — `standing_discount_selection`, whose tier 1 ("the larger of the discount written onto the agreement and the discount
  printed against the catering service level") can never produce an outcome other than tier 2's (the written figure) or the
  fall-through's (the printed figure). Finding **F-5**.

### findings

**F-1 — `SOURCE-POLICY RED` + `SOURCE-FACTOR RED`: the `notice_counting_basis` fall-through tier exists in `compute` and in the
factor ladder but in no sentence of the `rule`, and the factor's declared `baseline` contradicts the policy's own `baseline.rule`.**
_Bears on: task 1._

- **Symptom.** `catering_ext_cancellation_charge_assessment.compute` binds
  `notice_hours: RND((notice_days + 1) * 24, 2) if notice_channel == 'account_manager' else (RND(notice_days * 24, 2) if notice_channel == 'phone' else RND((notice_days - 1) * 24, 2))`
  — three branches. Its `rule` states only two: *"The notice given is counted in whole days from the day notice was given to the service
  day, taken at twenty-four hours to the day. Where the cancellation reached Larkspur Table through the client's named account manager,
  the notice given is counted from the day before notice was given …; where the cancellation reached Larkspur Table by telephone, it is
  counted from the day notice was given."* Nothing in the rule says "from the day after notice was given". The third branch is written
  only in `factors[notice_counting_basis].ladder[2].method`.
- **Root cause.** The ladder was given a fall-through that shifts the anchor a day back, and the general sentence of the rule that was
  supposed to state it instead states the *telephone* tier's method. The rule therefore states the telephone tier twice and the
  fall-through never.
- **Evidence.** `catering.extended.yaml` — `extended_policies[3].rule` (sentences 3–4); `extended_policies[3].compute` binding
  `notice_hours`; `extended_policies[3].factors[0].ladder[2].method`; `extended_policies[3].baseline.rule` sentence 2
  ("The notice given is counted in whole days from the day notice was given to the service day, taken at twenty-four hours to the day.")
  vs `extended_policies[3].factors[0].baseline.notice_hours = RND((notice_days - 1) * 24, 2)`.
- **Consequence.** Charter-global: a tier present in `compute` and in the ladder and absent from the `rule` fails check 2 in the
  compute→rule direction, and a reader who follows only the rule computes an email or portal cancellation's notice one whole day
  longer than `compute` does. Per task: the factor's declared baseline is not what `baseline.rule` states, so the factor's weight is
  measured against a straw man — demonstrated with figures in
  `env/env_0013_workplace_dining_and_catering_provider/audits/policy_task/catering_order_desk/1.md` → `factor_weight`.
- **Affected artifact.** `tasks/catering_order_desk/catering.extended.yaml`, policy `catering_ext_cancellation_charge_assessment`:
  `rule`, `compute[notice_hours]`, `factors[notice_counting_basis]`, `baseline.rule`.

**F-2 — `SOURCE-POLICY RED`: undeclared override of `catering_amendment_terms` on the quantity `standing_order_value_usd`.**
_Bears on: task 1._

- **Symptom.** `catering_amendment_terms` (base, inherited in full) states: *"Every amendment rewrites the order value, and the value
  that governs any later cancellation charge is the value on the order at the moment notice of cancellation is given."*
  `catering_ext_client_cancellation_registration` lists `catering_amendment_terms` in `base_policy_refs`, declares two other base
  sentences in `overwrite`, and does **not** declare this one — yet its `compute` writes
  `result: RND(selected_value * (100 - total_concession_pct) / 100, 2)`, i.e. the value on the order reduced by the standing discount
  plus the programme concession.
- **Root cause.** The near-identical sentence in `catering_cancellation_charges` was declared superseded; its twin in
  `catering_amendment_terms` was not, and both are rendered into the documents together.
- **Evidence.** `catering.extended.yaml` `policies[catering_amendment_terms].rule` sentence 5;
  `extended_policies[2].base_policy_refs` (includes `catering_amendment_terms`); `extended_policies[2].overwrite` (three entries,
  none naming that sentence); `extended_policies[2].compute` bindings `selected_value`, `total_concession_pct`, `result`.
- **Consequence.** Two defensible values for the scored parameter of a gold write — demonstrated with figures in
  `…/catering_order_desk/1.md` → `policy_self_consistency`.
- **Affected artifact.** `tasks/catering_order_desk/catering.extended.yaml`, policy
  `catering_ext_client_cancellation_registration`: `overwrite`.

**F-3 — observation: undeclared conflict with `catering_combination_cafe_interaction` on the delivery charge.**
_Bears on: neither task's world; recorded for the charter._

- **Symptom.** Base: *"Where that cafe contract does not permit catering out of its kitchen, the order is produced at the district
  kitchen and the ordinary delivery fee applies however close the cafe is."* Not named in
  `catering_ext_delivered_order_invoicing.overwrite`. Extended's `standing_round_delivery_charge` sets `delivery_fee_charged` to `0.0`
  (five or more deliveries to the named site in twelve months) or to half the printed fee (two or more), irrespective of the cafe.
- **Why an observation and not a red light.** The base sentence's antecedent is false on task 0's world (the cafe at `CS-244` is a
  *Full Service Cafe*, whose `catering_from_cafe_enabled` is `true`) and vacuous on task 1's (no cafe contract seeded). No second
  defensible answer can be demonstrated on either world, so the consequence test of "Core constraints" is not met.
- **Evidence.** `catering.extended.yaml` `policies[catering_combination_cafe_interaction].rule` sentence 3;
  `extended_policies[0].overwrite` (two entries, neither naming it); `extended_policies[0].compute[delivery_fee_charged]`.

**F-4 — `SOURCE-FACTOR RED`: the banquet cross-difficulty read joins on a key whose seeded value contradicts the banquet record's
own declared format.**
_Bears on: task 1._

- **Symptom.** `catering_ext_client_cancellation_registration.compute` binds
  `banquet_status: CFIELD('banquet','status', venue_code=F('delivery_site_code'))` and
  `banquet_max_guests: CPARAM('banquet','max_guests', venue_code=F('delivery_site_code'))`, i.e. it matches a **catering
  `delivery_site_code`** against a **banquet `venue_code`**. `blueprint/db_schema.json` declares
  `catering_agreements.delivery_site_code` as `"CS- followed by 3 digits"` and `banquet_agreements.venue_code` as
  `"VN- followed by 3 digits"` — two disjoint identifier namespaces. The read can only ever match if a banquet row is seeded with a
  `CS-` value in `venue_code`, which is what task 1's seed does.
- **Root cause.** The rule's phrase "a private event and banquet agreement **at the order's delivery site**" was implemented as an
  equality between a site code and a venue code, and the seed was bent to make the equality hold.
- **Evidence.** `blueprint/db_schema.json` → `catering_agreements.delivery_site_code.format`, `banquet_agreements.venue_code.format`;
  `catering.extended.yaml` `extended_policies[2].compute` bindings `banquet_status`, `banquet_max_guests`; task 1
  `initial_state.banquet_agreements["74ce8f87-ad16-42d2-9b21-2931f5cc1391"].venue_code = "CS-271"`.
- **Consequence.** The cross-difficulty rows this factor reads are seeded in a shape the banquet product's own record contract does
  not admit; demonstrated against task 1's world in `…/catering_order_desk/1.md` → `factor_weight`.
- **Affected artifact.** `tasks/catering_order_desk/catering.extended.yaml` (`extended_policies[2].compute`) and
  `tasks/catering_order_desk/tasks/1.json` (`initial_state.banquet_agreements`).

**F-5 — `SOURCE-FACTOR RED`: `standing_discount_selection`'s tier 1 can never select an outcome distinct from tier 2 or from the
fall-through.**
_Bears on: task 1._

- **Symptom.** The ladder is: tier 1 (three or more deliveries in six months) → "the larger of the discount written onto the agreement
  and the discount printed against the catering service level" = `MX(F('standing_discount_pct'), P('standing_discount_pct'))`;
  tier 2 (one or two deliveries) → `F('standing_discount_pct')`; fall-through → `P('standing_discount_pct')`. `MX(F, P)` is by
  construction either `F` or `P`, so tier 1's outcome always coincides with tier 2's or with the fall-through's. The ladder has three
  tiers and, on every world, at most two distinct outcomes.
- **Root cause.** Tier 1 was written as a selector over the same two quantities the other two tiers already select individually,
  rather than as a third treatment.
- **Evidence.** `catering.extended.yaml` `extended_policies[2].factors[standing_discount_selection].ladder`;
  `extended_policies[2].compute[discount_pct]`; `rule` sentences beginning "The discount taken on the value standing is …" and
  "Where the agreement carried three or more deliveries in the six months ending on the day notice is given …".
- **Consequence.** Demonstrated on task 1's world (tier 1 and tier 2 both yield 6.50) in `…/catering_order_desk/1.md` →
  `factor_weight`.
- **Affected artifact.** `tasks/catering_order_desk/catering.extended.yaml`, policy
  `catering_ext_client_cancellation_registration`, factor `standing_discount_selection`.

**O-1 — observation: extended invoicing is silent about the base consolidation basis.**
`catering_invoicing_terms` prints `invoice_consolidation` per service level (`weekly` for Attended Buffet, `monthly` for Executive
Hospitality, `per_order` for the two lowest). `catering_ext_delivered_order_invoicing` invoices one served order per call and neither
follows nor declares an override of that sentence. No consequence is demonstrable on task 0 (exactly one delivered-and-uninvoiced
order exists, so a weekly invoice would carry the same figure), so this is an observation. Note in passing that task 0's seed shows
every historical order invoiced individually on an Attended Buffet agreement whose printed basis is `weekly`.

**O-2 — observation: the depended-on rule states edge B's dependency from the other side.**
`catering_ext_client_cancellation_registration.rule` sentence 1 contains "… is what any **later** cancellation charge rests on",
a forward statement of the same cross-problem order that edge B's prerequisite sentence already states on the blocked side. Check 6
requires the depended-on policy's rule not to restate the dependency. No second answer follows from it, so it is an observation here;
it will matter to the KB render, where the depended-on document would carry the ordering as well.

**O-3 — observation: `amendment_lead_hours` converts days to hours with no sentence saying so.**
`catering_ext_client_cancellation_registration.compute` binds `amendment_lead_hours: DAYS(amendment_notice_day, service_day) * 24`,
tested against `P('headcount_change_deadline_hours')`. Its `compute_basis` quotes "…that amendment was asked for no later than the
guest count deadline printed against the catering service level", which states the comparison but not the 24-hours-to-the-day
conversion. (The sibling policy states its own conversion explicitly: "taken at twenty-four hours to the day".) No consequence on
task 1's world, where the margin is 264 h against a 48 h deadline.

**O-4 — observation: an inherited base duty with no tool.**
`catering_hold_and_closure_terms`: "Only the client may end a catering agreement, and the desk records the request for the client to
confirm rather than closing the agreement on their word alone." The first half is honoured (`confirm_agreement_closure_1e20ba9d` is
`owner="user"`). The second half — recording the request — has no tool in `task_tools.py` or `share_tools.py` and no
`catering_change_requests` row in either task's seed, so it is inherited but unimplementable. It cannot produce a second scored value,
so it is not a red light.

**O-5 — observation: `post_cancellation_charge_b7aa0639`'s docstring presupposes the order was pulled.**
"Raise the charge that a pulled catering order carries" / "the pulled catering order the charge answers". This names the business
object the charter itself names and carries no `before` / `after` / `first` and no other tool's name, so it passes check 3; it is
recorded because it sits close to the line for a tool whose policy is the blocked side of edge B.

**O-6 — observation: `repeat_cancellation_rate_basis` mixes effects under a `method` label.**
Tier 1 substitutes a fixed percentage (`P('cancellation_fee_pct_within_notice')`) into an unchanged formula — a `parameter`-shaped
effect; tier 2 changes the algorithm (`MX(notice_rate_pct, half the within-notice percentage)`) — a `method`-shaped effect. The label
is defensible because tier 1 also changes *what decides* the rate (it stops reading the notice at all), and the policy's `method`
count does not depend on it (`notice_counting_basis` and `cancellation_counting_window` already supply two). Recorded, not red.

## closing_checklist

**The difficulty does not close.** Task 1 fails three of the four relationships; task 0 fails one narrowly. The checklist is recorded
in full so the state of each item is on record.

| item | state |
| --- | --- |
| per-task audit files correspond one-to-one with the tasks, `_difficulty.md` alongside them | ✔ `0.md`, `1.md`, `_difficulty.md` in `env/env_0013_workplace_dining_and_catering_provider/audits/policy_task/catering_order_desk/` |
| old revisions traceable | ✔ first revision of this audit; nothing to preserve |
| every comparison section carries a PASS | ✘ `0.md` → `source_gt_comparison` carries one `SOURCE-FACTOR RED` (T0-F1); `1.md` → `source_gt_comparison` carries `SOURCE-POLICY RED`, `SOURCE-FACTOR RED` and `SOURCE-TASK RED` |
| extended policies fully covered, task scopes pairwise disjoint over the whole problem tree | ✔ task 0 = {`…delivered_order_invoicing`, `…agreement_closure_settlement`}; task 1 = {`…client_cancellation_registration`, `…cancellation_charge_assessment`}; disjoint and jointly complete over the four |
| task tools and GT closed | ✔ four tools, two per task, each named in exactly one task's `charter_scope`; `db_closure_matches_initial_state = true` on both |
| each task tool uses an independently generated, frozen uuid8 | ✔ `cb57dc9d`, `1e20ba9d`, `69ffeeb0`, `b7aa0639` — distinct, no shared prefix or tail, no ordinal relation |
| every problem tree: 1–3 prerequisite problems, ≥ max(n−1,1) `value_input` edges, ≥1 `owner=user` problem, no cycle | ✔ both trees have one prerequisite problem, one `value_input` edge, one `owner=user` write (task 0 the root, task 1 the prerequisite), no cycle |
| the difficulty's `prerequisite` edges together form a DAG, no cross-task cycle | ✔ two disjoint single edges |
| every computation declares a self-sufficient baseline giving a definite number different from gold | ✔ 6534.99 / 36550.00 / 6080.00 / 3315.97, all definite and all different from gold |
| 4–6 factors per computation, ≥2 `parameter`, ≥1 `method` | ✔ as declared (5/5/4/5); ✘ **after** the ladder tests, task 1's registration computation drops to 3 surviving factors (F-5 strikes out `standing_discount_selection`) and its charge computation to 4 (F-1 strikes out `notice_counting_basis`) |
| per task ≥1 multi-source and ≥1 cross-difficulty factor | ✔ as declared; ✘ task 1's only cross-difficulty factor reads rows seeded against a contradicted key format (**F-4**) |
| every ladder ≥3 tiers stated in full in its rule | ✘ **F-1**: `notice_counting_basis`'s fall-through tier is stated in `compute` and in the ladder and in no sentence of the rule |
| every ladder's tiers distinct in outcome | ✘ **F-5**: `standing_discount_selection`'s tier 1 can never differ from tier 2 or the fall-through |
| every factor proved to bear weight against an honest baseline | ✘ **F-1 / T1-F1**: `notice_counting_basis` bears no weight once the baseline is read from `baseline.rule`; the other nine factors of task 0 and the other eight of task 1 all bear weight, verified figure by figure |
| instantiation-stage gates re-run on the final form | ✔ re-run 2026-09-22 against the unchanged artifacts — all green, and **none of them sees any of the findings above** |

### instantiation gates re-run (final form, unchanged artifacts)

```
check_extended.py    EXTENDED OK               (category=catering, extended_policies=4, cross-cat=3, task_tools=4, tasks=2)
check_task_tools.py  TASK TOOL CONTRACT OK     (4 tools)
check_solvability.py SOLVABILITY OK            0.json True 2 3 37 True | 1.json True 2 3 30 True
check_compute.py     COMPUTE OK                history_rows_max=42(>= 8)  branches_max=27(>= 5)
check_grounding.py   GROUNDING OK              0.json 2 2 2 11 True | 1.json 2 2 2 10 True
check_cross_fire.py  SCOPE OK                  (2 tasks, policies=4, hard-fails=0)
replay_tasks.py      REPLAY OK                 0.json 9 True True 0 39 39 True | 1.json 9 True True 0 32 32 True
```

The gates are green on the same artifacts that carry F-1 through F-5. That is the expected division of labour — the gates prove
structure, reference and parsability; they cannot read a `baseline.rule` sentence against a `factors[].baseline` binding, cannot tell
that `MX(F, P)` can never be a third outcome, cannot see that a `CS-` site code is being matched against a field declared `VN-`, and
cannot notice that a base sentence about the same scored quantity was left out of an `overwrite`.

### per-task verdicts

| task | policy self-consistency | problem tree | factors bear weight | unique solution |
| --- | --- | --- | --- | --- |
| 0 | PASS | PASS | **`SOURCE-FACTOR RED`** (T0-F1) | PASS |
| 1 | **`SOURCE-POLICY RED`** (F-1, F-2) | PASS | **`SOURCE-FACTOR RED`** (T1-F1, F-5, F-4) | **`SOURCE-TASK RED`** (F-2) |

The difficulty does not pass the source-layer audit.

---

# revision_2

Round-2 re-audit, 2026-09-22. Round 1 above is left untouched.

## charter_global_frozen (revision 2)

| input | round 1 | round 2 | re-derived? |
| --- | --- | --- | --- |
| `catering.extended.yaml` | `cc35786a…ddba25d0` | **`9cb8a5053806de2b7cdcdc1c6a13e7403db705b8c5e7dff7961d9b69d109f531`** | **CHANGED → charter-global section re-derived in full** |
| `task_tools.py` | `961546e7…efaf08419` | `961546e7a5513bd4198163c0972cf4adb761d752cad8d177bdc912efeaf08419` | UNCHANGED → `action_binding_and_uuids` carried forward by reference on the hash, with the `(target_tool, computes)` pairing re-checked because the charter moved |
| masked view `0.masked.json` | `f2169ec0…8fb45fa3a74` | `f2169ec094568815fa32c8895b3b77d5f358e7235f5706d19287f8b45dbf3a74` | UNCHANGED |
| masked view `1.masked.json` | `3b419c35…62b5c124f` | **`fcc933beeeb1debfd18ce75c4ff1eb7b2ed113b7c074075fc300da6b780b09cf`** | **CHANGED → task 1 re-derived in full on the new world** |

This round is **not blind**: round 1's GT was already revealed to this auditor, and the brief says so. The work here is verification
that each round-1 RED is genuinely closed, that the rework introduced no new defect, and that nothing previously closed regressed.
Entry conditions were supplied in full (seven gate commands with their output lines, both masked views with hashes, both source
hashes, and the statement that `git diff --stat` on `blueprint/` is empty).

**Base copy re-verified verbatim.** Both YAMLs re-loaded and compared after whitespace normalisation: `category`, `display_name`,
`binding`, `lifecycle`, `accounts`, `parameter_schema`, `variants`, `events`, `measures` and `policies` are all **SAME**. Base was
not touched, confirming the coordinator's `git diff --stat`.

## round-1 item disposition

| item | claimed | verified | verdict |
| --- | --- | --- | --- |
| **F-1** (unstated fall-through tier + contradicted baseline) | closed by giving the rule the missing fall-through and moving the world off it | yes | **CLOSED** |
| **F-2** (undeclared override of `catering_amendment_terms`) | closed by a new `overwrite` | yes | **CLOSED** |
| **F-3** (undeclared conflict on the delivery fee) | closed by a new `overwrite` | yes | **CLOSED** |
| **F-4** (banquet join against a contradicted key format) | closed at the join, seed row restored to its declared format | yes, at the `rule`/`compute`/seed level — **but the factor's ladder text was left on the old join** | **CLOSED-BUT-NEW-DEFECT (R2-F1)** |
| **F-5** (`standing_discount_selection` tier collapse) | closed by replacing the factor | yes | **CLOSED** |
| **O-1** (consolidation basis neither followed nor declared) | closed by a new `overwrite` | yes | **CLOSED** |
| **O-2** (depended-on rule restates edge B's ordering) | closed | yes | **CLOSED** |
| **O-3** (`amendment_lead_hours` conversion unstated) | closed | yes | **CLOSED** |
| **O-4, O-5, O-6** | left standing, answered in the rationale | answers present and accurate | **left standing, accepted** |

### F-1 — verified closed

`catering_ext_cancellation_charge_assessment.rule` now states three counting tiers, not two:

1. *"Where the cancellation reached Larkspur Table through the client's named account manager, the notice given is counted from the
   day before notice was given, the account manager flagging it to the kitchen a day ahead"*
2. *"where the cancellation reached Larkspur Table by email or through the client ordering portal, it is counted from the day after
   notice was given, the desk registering a written instruction on the next working day"*
3. *"The notice given is counted in whole days from the day notice was given to the service day, taken at twenty-four hours to the
   day."* — the fall-through.

`compute[notice_hours]` now reads `RND((notice_days + 1) * 24, 2) if notice_channel == 'account_manager' else (RND((notice_days - 1)
* 24, 2) if (notice_channel == 'email' or notice_channel == 'online_portal') else RND(notice_days * 24, 2))` — one branch per stated
tier, in the same correspondence. `factors[notice_counting_basis].baseline.notice_hours` is now `RND(notice_days * 24, 2)`, which is
exactly what `baseline.rule` sentence 2 states, and it is the fall-through. The ladder's three outcomes are distinct on any world
where `notice_days` is fixed: on task 1's world they are 72.0 / 24.0 / 48.0 hours. Verified by evaluating the policy on the new
world under each of the four channel values. Consequence for task 1 is in `1.md` → `revision_2`.

### F-2, F-3, O-1 — the three new `overwrite` entries, checked individually

Twelve `overwrite` entries now stand across the four extended policies (round 1: nine). Every one was checked mechanically on four
points — `base_policy` present in that policy's `base_policy_refs`; `superseded_clause` verbatim locatable in that base policy's own
`rule`; `replaced_by` verbatim locatable in **this** policy's own `rule`; and no `(base_policy, superseded_clause)` pair declared
twice, checked both within a policy and **globally across all four**. **All twelve pass on all four points; no duplicate pair.**

| new entry | base policy | superseded clause | replaced by |
| --- | --- | --- | --- |
| **F-3** — `…delivered_order_invoicing.overwrite[2]` | `catering_combination_cafe_interaction` | "Where that cafe contract does not permit catering out of its kitchen, the order is produced at the district kitchen and the ordinary delivery fee applies however close the cafe is." | the standing-round sentence of this policy's rule ("An agreement that carried five or more deliveries… carries no delivery charge at all… two or more… half the fee") |
| **O-1** — `…delivered_order_invoicing.overwrite[3]` | `catering_invoicing_terms` | "How catering is invoiced follows the consolidation basis printed against the service level: a per-order basis… a weekly basis… a monthly basis…" | "The amount invoiced for a catering order that has been served is worked out from the value the delivery entry most recently recorded on the agreement carries." |
| **F-2** — `…client_cancellation_registration.overwrite[2]` | `catering_amendment_terms` | "Every amendment rewrites the order value, and the value that governs any later cancellation charge is the value on the order at the moment notice of cancellation is given." | "The trading discount taken and the programme concession are first added into one total concession rate, and the value selected above is reduced once by that total rate; the two do not act successively, and the result is rounded to two decimal places only at the end." |

The merged semantics after each replacement are unique: in each case the base sentence is struck out wholesale and the extended rule
states the whole treatment of that quantity. The invoicing `rule` itself is unchanged — both new entries replace base sentences with
sentences already in force, which is the minimal closure. Consequences: `0.md` → `revision_2` (F-3, O-1), `1.md` → `revision_2` (F-2).

### F-5 — verified closed by replacement

`standing_discount_selection` is gone. In its place `catering_ext_client_cancellation_registration` declares
**`trading_discount_applied`** (`effect: parameter`, `decides: discount_pct`, `bindings: [delivered_6m, discount_pct]`):

| tier | condition | outcome | on task 1's world |
| --- | --- | --- | --- |
| 1 | three or more deliveries in the six months ending on the day notice is given | `F('standing_discount_pct')` — the discount written onto the agreement | **6.50** |
| 2 | at least one but fewer than three deliveries in those six months | `P('standing_discount_pct')` — the discount printed against the service level | 5.00 |
| fall-through | otherwise | no trading discount | 0.00 |

The three outcomes are **genuinely distinct** and distinct by construction rather than by coincidence: each tier selects a different
*source* (the agreement's own figure, the service level's figure, nothing), where the retired tier 1 was `MX` over the other two and
could never be a third value. On this world they are 6.50 / 5.00 / 0.00. `baseline.discount_pct` is now `0.0`, matching the
fall-through, and `baseline.rule` was changed to carry "No trading discount is taken on the value standing." — verified verbatim in
the policy's `rule`. `baseline.params` was reduced to `[headcount_reduction_free_pct]`, which is exactly what the new baseline rule
needs. The business reading holds: a discount earned by trading, at the negotiated rate for a regular account, the published rate for
an occasional one, and none for an account that has not been served in six months.

Structure after the swap: the registration computation carries **4 factors — 3 `parameter`, 1 `method`** (inside 4–6, ≥2 `parameter`,
≥1 `method`), matching its declared draw of 4. The charge computation still carries 5 (2 `parameter`, 3 `method`), matching its draw
of 5. Task 1 still carries multi-source factors (`free_reduction_band_standing`, `amendment_repricing_basis`,
`repeat_cancellation_rate_basis`, `delivery_record_rebate`, `cancellation_counting_window`) and exactly one `cross_difficulty` factor
(`programme_concession_taken` → banquet). Task 0 is unchanged at 5 + 5. Load-bearing check is in `1.md` → `revision_2`.

### F-4 — verified closed at the join and the seed, but see R2-F1

- The join is now `CFIELD('banquet','status', client_account_code=F('client_account_code'))` and
  `CPARAM('banquet','max_guests', client_account_code=F('client_account_code'))`. `blueprint/db_schema.json` declares
  `catering_agreements.client_account_code` and `banquet_agreements.client_account_code` **both** as `"CA- followed by 5 digits"` —
  one namespace, both records' own declared format.
- The seeded banquet row now carries `venue_code = "VN-318"`, back inside the `"VN- followed by 3 digits"` format its own record
  declares, and `client_account_code = "CA-22853"`, equal to the catering agreement's.
- The factor still reads a genuine **value**, not mere existence: `CPARAM` returns `max_guests = 350` from the
  "Seated Banquet Package" variant of the banquet charter, and the tier turns on `350 ≥ 200`.
- Identifier band held: phone `3125806412` (`3125…`), `CA-22853` (`CA-22`+3), `CS-271` (`CS-2`+2), surname **I**ngalls and
  organisation **H**albrook (both inside F–J); the badge band does not apply, `employee_badge_number` being empty on a client
  organisation profile. Task 0's band is unchanged (Fenwick/Greyfriar, `3125470188`, `CA-22417`, `CS-244`).
- **But** the factor's own ladder text was not moved with the rule — see **R2-F1**.

### O-2, O-3 — verified closed

- **O-2**: `catering_ext_client_cancellation_registration.rule` sentence 1 now reads *"The value standing on a catering order at the
  moment the client gives notice of cancellation is worked out afresh from the entries the order carries rather than read off the
  quotation it was first placed at."* The clause "is what any later cancellation charge rests on" is gone. A fresh ordering-cue scan
  over every sentence of all four extended rules finds **no cross-problem order anywhere except the two declared prerequisite
  sentences**; every other hit is within-computation arithmetic order ("then the service charge, then the rush surcharge…", "reduced
  once by that total rate", "the ceiling applying after the percentage has been taken").
- **O-3**: the amendment-deadline test now carries its conversion in the rule: *"…no later than the guest count deadline printed
  against the catering service level, **counted in whole days from the day the amendment was asked for to the service day and taken
  at twenty-four hours to the day**…"*, and the same words are in `overwrite[1].replaced_by`.

## re-derived charter-global checks (revision 2)

### policy_conflict_scan
Unchanged in shape: four extended policies, four distinct `(target_tool, computes)` pairs, four distinct event subjects, two tasks
with pairwise-disjoint and jointly complete scopes (`charter_scope` on both task files re-read and unchanged). The cross-category
declarations now read cafe for the two invoicing/closure policies and **banquet, joined on the client account code** for the
registration policy; the charge policy still declares `[]` and performs no cross-category read. No policy-level contradiction found.

### rule_compute_equivalence
Re-run mechanically over all four policies: every `compute` binding has a `compute_basis` entry and vice versa (21/21, 22/22, 20/20,
16/16); every `compute_basis` sentence is verbatim in its policy's `rule`; every `baseline.rule` sentence is verbatim in its policy's
`rule`. Every ladder tier was matched to the rule by hand. All tiers are now stated in prose in their policy's rule **except the two
tier conditions of `programme_concession_taken`** — see **R2-F1**. The round-1 F-1 gap is gone.

### action_binding_and_uuids
`task_tools.py` is byte-identical to round 1 (hash above), so the tool bodies, docstrings and uuid8s are carried forward by reference:
`cb57dc9d`, `1e20ba9d`, `69ffeeb0`, `b7aa0639` — distinct, no shared prefix or tail, no ordinal relation, none batch-derived; no body
judges a prerequisite. The `(target_tool, computes)` pairing was re-checked against the moved charter and is still one policy per pair.

### prerequisite_graph and prerequisite_sentences
Both edges re-checked on the new charter and both still pass every point: `policy_source` verbatim in the blocked policy's own rule;
ordering connectives "until" and "only after"; `form: state` with no `fallback_reason` (correct); `condition` neither strengthened nor
weakened; `resolved_by` equal to the depended-on policy's `target_tool`; `gate` a real binding of the blocked `compute`
(`invoiced_12m`, `cancelled_value`); no tool name, policy id, snake_case token or row id in either sentence; exactly one write of this
difficulty brings each waited-on state about; **and neither sentence is restated in the depended-on policy's rule** (O-2's closure
makes this true for edge B for the first time). Graph still acyclic, still two disjoint single edges.

### factor_ladders (revision 2)

| policy | factors | `parameter` | `method` | cross-difficulty | ladders ≥3 tiers, distinct outcomes |
| --- | --- | --- | --- | --- | --- |
| `…delivered_order_invoicing` | 5 | 4 | 1 | cafe | ✔ (unchanged from round 1) |
| `…agreement_closure_settlement` | 5 | 4 | 1 | cafe | ✔ (unchanged from round 1) |
| `…client_cancellation_registration` | 4 | 3 | 1 | banquet | ✔ outcomes; ✘ tier **conditions** of `programme_concession_taken` — **R2-F1** |
| `…cancellation_charge_assessment` | 5 | 2 | 3 | — | ✔ (`notice_counting_basis` now 72/24/48 h on task 1's world) |

Binding sets re-checked: pairwise disjoint within every policy, and no `decides: result`.

## findings (revision 2)

**R2-F1 — `SOURCE-POLICY RED` (new, introduced by the F-4 rework): `programme_concession_taken`'s ladder still states the retired
delivery-site join, while the rule, the compute and the GT trace all state the client-account-code join.**
_Bears on: task 1._

- **Symptom.** `catering.extended.yaml` → `extended_policies[catering_ext_client_cancellation_registration].factors[programme_concession_taken].ladder`:
  - tier 1 `when`: *"the client holds a private event and banquet agreement **at the order's delivery site** that stands open and whose package is written for two hundred guests or more"*
  - tier 2 `when`: *"the client holds such an agreement **at that site** that stands open and whose package is written for fewer than two hundred guests"*

  The same policy's `rule` now says: *"Where the client holds a private event and banquet agreement **billing under the same client
  account code as the catering agreement**, that agreement stands open and its package is written for two hundred guests or more, a
  programme concession of four points is taken… where the client holds such an agreement **under that account code** that stands open
  and whose package is written for fewer than two hundred guests, a programme concession of two points is taken."* `compute` joins on
  `client_account_code`; `compute_basis[banquet_status]`, `[banquet_max_guests]` and `[programme_concession_pct]` all quote the
  account-code sentence; and `tasks/1.json` → `computations[0].factor_sensitivity[3].tier_taken` also uses the account-code wording.
  The ladder is the one face left on the old join.
- **Root cause.** F-4 was closed by moving the join in the `rule`, the `compute`, the `compute_basis`, the `cross_category.note` and
  the seed, and the factor's own `ladder` text was not moved with them.
- **Evidence.** `tasks/catering_order_desk/catering.extended.yaml`, `extended_policies[2]`: `rule` (concession sentences),
  `compute[banquet_status]`, `compute[banquet_max_guests]`, `compute_basis` (three entries), `cross_category[0].note`,
  `factors[programme_concession_taken].ladder[0].when` and `[1].when`. Seed: `tasks/1.json`
  `initial_state.banquet_agreements["74ce8f87-…"]` with `client_account_code = "CA-22853"` and `venue_code = "VN-318"`;
  `initial_state.catering_agreements["a50defa9-…"]` with `client_account_code = "CA-22853"` and `delivery_site_code = "CS-271"`.
- **Demonstrated consequence.** The two faces now select **different tiers on task 1's world**. Under the rule (account code) the
  banquet agreement matches, `banquet_max_guests = 350 ≥ 200`, and the concession is 4.0 points. Under the ladder ("at the order's
  delivery site") nothing matches — the banquet agreement's venue is `VN-318` and the order's delivery site is `CS-271` — so the tier
  falls through to no concession. Recomputed on this world, the ladder reading gives `total_concession_pct = 6.5` and
  `standing_order_value_usd = ` **5329.50** instead of 5101.50, and the charge that reads it becomes
  `RND(RND(5329.50 × 32.5/100, 2) × 85/100, 2) = ` **1472.28** instead of 1409.29. Two scored parameters, two values each. This is
  check 2's "a tier present in one face and absent from the other", and it is sharper than an ordinary wording drift because the KB
  renders each declared factor's ladder into its own document: the factor document and the hub would state contradictory conditions
  for the same tier.
- **Affected artifact.** `env/env_0013_workplace_dining_and_catering_provider/tasks/catering_order_desk/catering.extended.yaml`,
  `extended_policies[catering_ext_client_cancellation_registration].factors[programme_concession_taken].ladder[0].when` and
  `.ladder[1].when`.
- **Relation to previous revisions.** New in revision 2. It did not exist in round 1, where `rule`, `compute` and `ladder` agreed on
  the delivery-site join and the defect was F-4 (the join key itself). Closing F-4 moved three faces and left the fourth behind.

**R2-O1 — observation: the banquet finder's docstring does not advertise the field the new join reads.**
`find_banquet_agreements`' docstring lists what it returns as "the event package held, the venue it is written against, the state of
the agreement, the term dates, the invoicing contact, and the client money currently held on deposit alongside the unsettled event
balance" — `client_account_code` is not among them, though `find_catering_agreements`' docstring does name "the client account code it
bills under". The value is nonetheless reachable: the finder returns the whole row (`return str(rows)`), so the account code is in the
agent's transcript. `share_tools.py` is blueprint and out of this rework's write domain, so this is recorded rather than red-lighted —
but the new join now rests on a field the tool contract does not mention.

**R2-O2 — observation: the registration and charge computations read the *latest* entry of a family on the agreement, not the order.**
Unchanged from round 1's T0-O2 in shape and extended by the new world: `placed_value`, `placed_headcount`, `service_day`,
`amended_*` and `cancelled_value` are all `LATEST(...)` over the agreement with no `order_reference` filter. On task 1's world the
target order is the most recently placed and the registration write makes its cancellation the most recent, so the readings coincide
with the intended object. Recorded because the coincidence is a property of the seed.

## per-task verdicts (revision 2)

| task | policy self-consistency | problem tree | factors bear weight | unique solution |
| --- | --- | --- | --- | --- |
| 0 | **PASS** | **PASS** | **PASS** | **PASS** |
| 1 | **`SOURCE-POLICY RED`** (R2-F1) | **PASS** | **PASS** | **`SOURCE-TASK RED`** (R2-F1's consequence) |

Task 0 closes. Task 1 does not: every round-1 defect is genuinely closed and no scored value regressed, but the F-4 rework left one
face of one ladder on the retired join, which re-opens two defensible values for both of task 1's scored parameters.

## closing_checklist (revision 2)

| item | state |
| --- | --- |
| per-task audit files one-to-one with the tasks, `_difficulty.md` alongside | ✔ |
| old revisions traceable | ✔ round 1 left untouched above; this section appended under `revision_2` |
| every comparison section carries a PASS | ✘ `1.md` → `revision_2` carries `SOURCE-POLICY RED` / `SOURCE-TASK RED` (R2-F1); `0.md` → `revision_2` is clean |
| extended policies fully covered, scopes pairwise disjoint over the whole tree | ✔ unchanged |
| task tools and GT closed; uuid8s independently generated and frozen | ✔ `task_tools.py` byte-identical to round 1 |
| trees: 1–3 prerequisite problems, ≥ max(n−1,1) `value_input` edges, ≥1 `owner=user` problem, no cycle; difficulty-wide DAG | ✔ both unchanged |
| self-sufficient baseline per computation, definite and ≠ gold | ✔ 6534.99 / 36550.00 / **6400.00** (was 6080.00) / 3315.97 |
| 4–6 factors per computation matching its draw, ≥2 `parameter`, ≥1 `method` | ✔ 5/5/4/5 against draws of [5,5] and [5,4] |
| per task ≥1 multi-source and ≥1 cross-difficulty factor | ✔ both; task 1's cross-difficulty now joins on a key both records declare identically |
| every ladder ≥3 tiers stated in full in its rule | ✘ **R2-F1** — two tier *conditions* of `programme_concession_taken` |
| every ladder's tiers distinct in outcome | ✔ F-5 closed; `notice_counting_basis` now 72/24/48 h; `trading_discount_applied` 6.50/5.00/0.00 |
| every factor bears weight against an honest baseline | ✔ all twenty factor substitutions re-run; see the two task files |
| instantiation gates re-run on the final form | ✔ supplied by the coordinator, all seven green — and again none of them sees R2-F1 |

---

# revision_3

Round-3 re-audit, 2026-09-22. Revisions 1 and 2 above are left untouched.

## charter_global_frozen (revision 3)

| input | round 2 | round 3 | re-derived? |
| --- | --- | --- | --- |
| `catering.extended.yaml` | `9cb8a505…d109f531` | **`12b0db6bd32ddf0f31cc9a772894f35fad03fc488c8cc739cba95d8bd9a7a3de`** | **CHANGED → charter-global section re-derived in full** |
| `task_tools.py` | `961546e7…efaf08419` | **`542f122fda69bd5306649bdd698a34197529c55e7cd325cb00c580376c2f1a57`** | **CHANGED → `action_binding_and_uuids` re-derived in full, tool module re-read line by line** |
| masked view `0.masked.json` | `f2169ec0…b45fa3a74` | `f2169ec094568815fa32c8895b3b77d5f358e7235f5706d19287f8b45dbf3a74` | UNCHANGED |
| masked view `1.masked.json` | `fcc933be…b780b09cf` | `fcc933beeeb1debfd18ce75c4ff1eb7b2ed113b7c074075fc300da6b780b09cf` | UNCHANGED |

Neither task's world moved. Both charter-side artifacts did, so both are re-derived. Entry conditions supplied in full, including a
`check_base_frozen` line ("BASE FROZEN OK (10 files verified by hash)") that was not in earlier rounds. **Base copy re-verified
independently** by loading both YAMLs and comparing after whitespace normalisation: all ten top-level sections **SAME**.

## round-2 item disposition

| item | claimed | verified | verdict |
| --- | --- | --- | --- |
| **R2-F1** — `programme_concession_taken`'s ladder on the retired delivery-site join | closed by lifting both tier conditions verbatim out of the rule | yes | **CLOSED** |
| **R2-O1** — the channel enum offered a competing reading | closed in the tool contract | yes | **CLOSED** |
| **R2-O2** — the banquet finder's docstring does not name the join key | not closable at source; closed as far as the domain allows | yes, and the residue is genuinely outside the write domain | **CLOSED as far as the domain allows** |
| *(self-found by the reworker's sweep)* `amendment_repricing_basis#1` missing round 2's day-count conversion | fixed | yes | **CLOSED** |

### R2-F1 — verified closed

`factors[programme_concession_taken].ladder` now reads:

- tier 0 `when`: *"the client holds a private event and banquet agreement billing under the same client account code as the catering
  agreement, that agreement stands open and its package is written for two hundred guests or more"*
- tier 1 `when`: *"the client holds such an agreement under that account code that stands open and whose package is written for fewer
  than two hundred guests"*

Both are **verbatim substrings of the policy's own `rule`** (clauses 11 and 12), tested by exact string containment after whitespace
normalisation — not by paraphrase judgement. The hub sentence and the rendered factor document therefore state the identical
condition, and the divergence that made the two faces select different tiers is gone. Consequence for task 1 is in `1.md` →
`revision_3`.

### the full-face sweep, re-run by this audit rather than accepted

The brief asked that the sweep's "0 mismatches" result not be taken on trust. It was re-run here independently and, deliberately,
**with a stricter test than substantive equivalence**: exact containment of every ladder tier condition and every prose outcome in its
own policy's `rule`. That test reports **30 non-verbatim items across the four policies**, every one of which was then adjudicated by
hand against the numbered rule clause it belongs to. The adjudication:

| policy | non-verbatim items | adjudication |
| --- | --- | --- |
| `…delivered_order_invoicing` | 14 | all anaphora or ellipsis. `volume_step_earned` #0–#2 ↔ clauses 5–7 ("those twelve months" is clause 4's "the twelve months ending on the day the invoice is raised"; clauses 6–7 elide "inside the counting window"). `spend_counting_window` #0–#2 ↔ clauses 9–10 ("on that day" = clause 9's "the day the invoice is raised"). `rush_percentage_carried` #0–#1 ↔ clauses 17–18 ("that service level" = "the catering service level"). `standing_round_delivery_charge` #0–#1 ↔ clauses 20–21, same anaphor. |
| `…agreement_closure_settlement` | 6 | all anaphora. `programme_spend_benchmark` #0–#1 outcomes ↔ clauses 4–5. `counted_spend_basis` #0 ↔ clause 7 ("those twelve months" = clause 6's). `shortfall_share_due` #0 ↔ clause 11. `closing_late_charge_rate` #1 ↔ clause 15 ("that monthly late percentage once"). `early_exit_charge_share` #1 ↔ clause 19 ("it is ended" for "the agreement is ended"). |
| `…client_cancellation_registration` | 2 | `free_reduction_band_standing` #0–#1 outcomes ↔ clauses 5–6 ("the band printed against that service level"). **`programme_concession_taken`, `amendment_repricing_basis` and `trading_discount_applied` produce no items at all — every tier condition of all three is verbatim.** |
| `…cancellation_charge_assessment` | 8 | all anaphora or ellipsis. `notice_counting_basis` #0–#2 outcomes spell out, from clause 2, the "to the service day / at twenty-four hours to the day" that clauses 3–4 leave elliptical; the counting anchors themselves match word for word. `notice_band_rate` #1 ↔ clause 7. `cancellation_counting_window` #0, #2 ↔ clauses 9 and 8. `repeat_cancellation_rate_basis` #1 ↔ clause 13. `delivery_record_rebate` #1 ↔ clause 16. |

**No substantive divergence survives anywhere.** Every difference is "that service level" for "the catering service level", "those
twelve months" for the window the preceding clause names, "it" for "the agreement", or a tier spelling out what its rule clause
elides. This is the same class of difference this audit adjudicated as acceptable in revisions 1 and 2, and it is the only class left.

The sweep also covered, independently:

- **compute_basis coverage and verbatim quotation** — all four policies: every binding has a basis entry and vice versa (21/21, 22/22,
  20/20, 16/16), and every quoted sentence is verbatim in its rule. Zero failures.
- **`baseline.rule` sentences** — every sentence of every policy's `baseline.rule` verbatim in its `rule`. Zero failures.
- **factor binding disjointness**, `decides` never `result`, every `decides` and every `baseline` key a real binding, every ladder ≥3
  tiers. Zero failures.
- **cross-category join keys against declared `reads`** — see below.

### cross-category join keys now declared (R2-O2's in-domain half)

| policy | declared `reads` | fields `compute` returns | join key `compute` matches on | key declared? |
| --- | --- | --- | --- | --- |
| `…delivered_order_invoicing` | `client_account_code`? no — `site_code`, `status`, `variant_name` | `status` (CFIELD), `catering_from_cafe_enabled` (CPARAM, via `variant_name`) | `site_code` | **yes (new)** |
| `…agreement_closure_settlement` | `site_code`, `status`, `variant_name` | `status`, `catering_from_cafe_enabled` | `site_code` | **yes (new)** |
| `…client_cancellation_registration` | `client_account_code`, `status`, `variant_name` | `status`, `max_guests` (CPARAM, via `variant_name`) | `client_account_code` | **yes (new)** |

Each declaration is **true**, not merely added: the compute matches the other product's record on that field, which is a read of it.
Both join namespaces are single: `blueprint/db_schema.json` declares `catering_agreements.delivery_site_code` and
`cafe_contracts.site_code` both as `"CS- followed by 3 digits"`, and `catering_agreements.client_account_code` and
`banquet_agreements.client_account_code` both as `"CA- followed by 5 digits"`. `reads` is consumed by no `compute` and by no gate, so
no scored quantity can move from the addition — confirmed by re-deriving all four computations (below).

### action_binding_and_uuids (re-derived; the tool module moved)

- **uuid8s unchanged**: `cb57dc9d`, `1e20ba9d`, `69ffeeb0`, `b7aa0639` — the same four frozen tokens as rounds 1 and 2, not
  regenerated. Distinct, no shared prefix or tail, no ordinal relation, none batch-derived.
- **All four function bodies are byte-identical to round 1**, verified by re-parsing the module and unparsing each function with its
  docstring stripped. Signatures unchanged. No body reads a status, counts history, derives an amount, refuses, errors or hints;
  the tool layer still judges no prerequisite.
- **One docstring changed**: `register_order_cancellation_69ffeeb0`'s `order_channel` gloss. The other three are unchanged.
- **Ordering-cue and cross-naming scan over all four docstrings**: no docstring names another tool; the only regex hit is
  "looking **after** them", a fixed phrase naming the account manager's role, not an ordering cue. No docstring states a position in
  a sequence.
- `(target_tool, computes)` still one policy per pair, four distinct pairs.

### the new `order_channel` gloss, checked on the brief's three points

> "Enum class — the route by which this cancellation instruction reached Larkspur Table, which is a fact about how the client passed
> the instruction on rather than about the medium of any one conversation. online_portal when the client entered the instruction
> themselves in the client ordering portal; account_manager when the client gave the instruction to the named catering account manager
> looking after them rather than to the client services desk; phone when the client spoke the instruction to the client services desk
> on the telephone and passed it through no one else; email when the client sent the instruction in writing to the desk's mailbox."

1. **No ordering cue, no other tool named, no policy determination stated.** It describes what the field records and nothing about
   what the field decides — it says nothing of notice counting, notice hours, free windows, rates or charges. An agent still has to
   derive from the charter that the channel moves the counting anchor.
2. **Every enum value still has an applicable situation**, and the four are now mutually exclusive rather than merely listed:
   `online_portal` (entered by the client in the portal), `account_manager` (given to the manager **rather than to the desk**),
   `phone` (spoken to the desk **and passed through no one else**), `email` (sent in writing to the desk's mailbox). The seed itself
   exercises `phone`, `email` and `account_manager` on historical rows, so none is a dead branch.
3. **It answers R2-O1 at the contract rather than leaning on the persona**: the reading this audit flagged — "the client is on the
   telephone to the desk right now, so `phone`" — is excluded by the words "passed it through no one else", which do not hold of a
   client who gave the instruction to his account manager first thing.

### prerequisite_graph and prerequisite_sentences (re-derived)

Both edges re-checked on the moved charter: `policy_source` verbatim in the blocked policy's own rule; ordering connectives "until"
and "only after"; `form: state` with no `fallback_reason`; `condition` neither strengthened nor weakened; `resolved_by` equal to the
depended-on policy's `target_tool`; `gate` a real binding of the blocked compute; neither sentence restated in the depended-on rule;
exactly one write of the difficulty brings each waited-on state about. Graph still acyclic.

### override_declarations (re-derived)

Twelve `overwrite` entries, re-tested on all four points — base policy in that policy's `base_policy_refs`, `superseded_clause`
verbatim in that base policy's `rule`, `replaced_by` verbatim in this policy's own `rule`, and no `(base_policy, superseded_clause)`
pair declared twice either within a policy or globally. **12 entries, 0 failures, 0 duplicates.**

### factor_ladders (revision 3)

| policy | factors | `parameter` | `method` | cross-difficulty | ladders |
| --- | --- | --- | --- | --- | --- |
| `…delivered_order_invoicing` | 5 | 4 | 1 | cafe | ✔ |
| `…agreement_closure_settlement` | 5 | 4 | 1 | cafe | ✔ |
| `…client_cancellation_registration` | 4 | 3 | 1 | banquet | ✔ (all three of its reworked factors now verbatim) |
| `…cancellation_charge_assessment` | 5 | 2 | 3 | — | ✔ |

Counts match each task's declared draw (`[5, 5]` for task 0, `[5, 4]` for task 1). Multi-source and cross-difficulty floors met per
task. Binding sets pairwise disjoint within every policy.

## findings (revision 3)

**No new finding.** R2-F1 is closed at the source of the divergence rather than papered over; the independent full-face sweep found
no second instance and no further drift; the tool-contract change introduces no ordering cue, no cross-naming and no policy
determination; and no scored value moved anywhere.

**R3-O1 — observation, carried not raised: the residue of R2-O2 is outside every write domain.**
`find_banquet_agreements`' docstring still does not name `client_account_code` among what it returns, and
`find_cafe_contracts`' does not name `site_code`. Both live in `blueprint/share_tools.py`, which `check_base_frozen` now verifies by
hash and which this difficulty may not touch. The values are reachable regardless — both finders return the whole row — and the
charter now declares each join key in `cross_category.reads`, so the rendered materials will state which field of the other product's
record the tier is decided from. Recorded so that a later scenario-level pass over `share_tools.py` can pick it up; it is not a defect
of this difficulty.

**R3-O2 — observation: the ladder/rule differences that remain are anaphoric only.**
Thirty tier conditions and prose outcomes across the four policies are not exact substrings of their rule, and all thirty were
adjudicated item by item against the numbered rule clause they belong to (table above). Every one is "that service level" for "the
catering service level", "those twelve months" for the window the preceding clause fixes, "it" for "the agreement", or a tier
spelling out what its clause elides. None changes a condition or an outcome. Recorded because the exact-containment test is the one
that caught R2-F1, and a future round should re-run it rather than eyeballing: the thirty benign items are the expected baseline, and
anything beyond them wants adjudicating.

## per-task verdicts (revision 3)

| task | policy self-consistency | problem tree | factors bear weight | unique solution |
| --- | --- | --- | --- | --- |
| 0 | **PASS** | **PASS** | **PASS** | **PASS** |
| 1 | **PASS** | **PASS** | **PASS** | **PASS** |

**The difficulty passes the source-layer audit.**

## closing_checklist (revision 3)

| item | state |
| --- | --- |
| per-task audit files one-to-one with the tasks, `_difficulty.md` alongside | ✔ |
| old revisions traceable | ✔ revisions 1 and 2 untouched; this appended under `revision_3` |
| every comparison section carries a PASS | ✔ `0.md` and `1.md` → `revision_3` both PASS on all four relationships |
| extended policies fully covered, scopes pairwise disjoint over the whole tree | ✔ task 0 {invoicing, closure}, task 1 {registration, charge} |
| task tools and GT closed; uuid8s independently generated and frozen | ✔ four distinct uuid8s, unchanged across three rounds; bodies byte-identical to round 1 |
| trees: 1–3 prerequisite problems, ≥ max(n−1,1) `value_input` edges, ≥1 `owner=user` problem, no cycle; difficulty-wide DAG | ✔ both trees, re-walked |
| self-sufficient baseline per computation, definite and ≠ gold | ✔ 6534.99 / 36550.00 / 6400.00 / 3315.97 against 6167.65 / 20943.77 / 5101.50 / 1409.29 |
| 4–6 factors per computation matching its draw, ≥2 `parameter`, ≥1 `method` | ✔ 5/5/4/5 against draws `[5,5]` and `[5,4]` |
| per task ≥1 multi-source and ≥1 cross-difficulty factor | ✔ both; both cross-difficulty joins inside one declared namespace and now declared in `reads` |
| every ladder ≥3 tiers stated in full in its rule | ✔ exact-containment sweep plus item-by-item adjudication of the 30 anaphoric residues |
| every ladder's tiers distinct in outcome | ✔ `notice_counting_basis` 72/24/48 h; `trading_discount_applied` 6.50/5.00/0.00; all others re-checked |
| every factor bears weight against an honest baseline | ✔ all nineteen factor substitutions re-run this round, every figure reproduced |
| instantiation gates re-run on the final form | ✔ supplied by the coordinator — seven green plus `BASE FROZEN OK (10 files verified by hash)`; none of them would have seen R2-F1, which is why the exact-containment sweep is the check that matters here |

---

# revision_4

Round-4 re-audit, 2026-09-22. Revisions 1–3 above are left untouched.

## charter_global_frozen (revision 4)

| input | round 3 | round 4 | re-derived? |
| --- | --- | --- | --- |
| `catering.extended.yaml` | `12b0db6b…d9a7a3de` | **`8d2003c3f13b6371e636ccf13518b9614385c60e7ae0354d77deca1e01c0cc99`** | **CHANGED → charter-global section re-derived in full** |
| `task_tools.py` | `542f122f…76c2f1a57` | `542f122fda69bd5306649bdd698a34197529c55e7cd325cb00c580376c2f1a57` | UNCHANGED → `action_binding_and_uuids` carried forward on the hash |
| masked view `0.masked.json` | `f2169ec0…b45fa3a74` | `f2169ec094568815fa32c8895b3b77d5f358e7235f5706d19287f8b45dbf3a74` | UNCHANGED |
| masked view `1.masked.json` | `fcc933be…b780b09cf` | `fcc933beeeb1debfd18ce75c4ff1eb7b2ed113b7c074075fc300da6b780b09cf` | UNCHANGED |

Neither world moved. Base copy re-verified independently: all ten top-level sections **SAME** against
`blueprint/products/catering.yaml`.

**Read domain extended for this round only**, as the brief directs: `docs/banquet/` and `docs/cafe/` were read, because the defect
under review is only visible in the *other* product's published words. `docs/catering/` was read once, to settle a provenance question
about the C2 decline. No other scenario and no sibling difficulty's tasks directory was touched.

## the defect under review, verified at its source

The render-layer auditor's finding is **correct, and it is a source-layer defect**. Verified against the banquet corpus directly, not
against anyone's account of it — `docs/banquet/package_capacity_and_lead_schedule_1a8137ad.json`, under "Reading of the columns":

> "The smallest guest count is the guest count the package **is written for** and the largest is the guest count the package
> **handles**."

and the schedule it glosses carries the columns `| Package | Smallest guest count | Largest guest count | …`, with
`| Seated Banquet Package | 60 | 350 | 6500 | …`.

The round-3 condition read *"whose package **is written for** two hundred guests or more"* while binding
`CPARAM('banquet','max_guests')`. In the banquet corpus's own vocabulary "written for" is the **smallest** count. A reader following
the published corpus resolves the condition against 60, not 350, finds 60 short of two hundred, and takes the two-point tier instead
of the four-point one. Quantified independently on task 1's world: the corpus reading gives a total concession of 8.5 and
**5215.50 / 1440.78** against the scored **5101.50 / 1409.29** — a different value for both scored parameters. Recorded here as
**R4-F0** for the record; it is the item the reworker's C1 closes.

Neither the source rounds nor the render gates could have caught it. It is invisible inside catering, where "written for" reads
naturally as "sized for", and invisible to a gate, which compares a ladder to its own rule and a document to its own source. It is
only visible by reading the other product's published definitions — which is what this round did.

## item disposition

| item | claimed | verified | verdict |
| --- | --- | --- | --- |
| **C1** — banquet condition phrased against the wrong column of the banquet schedule | closed at the source | yes | **CLOSED** |
| **sibling 1** — banquet agreement "stands open" | closed with it | yes | **CLOSED** |
| **sibling 2** — cafe contract "stands open" (two policies) | closed with it; claimed to have teeth | yes, and the teeth are real | **CLOSED** |
| **sibling 3** — cafe parameter in catering's idiom | closed with it | yes | **CLOSED** |
| **B3** — intermediate rounding against "rounded … only at the end" | declined, judgement | decline **agreed**; re-recorded as R4-O2 | **declined, correctly** |
| **C2** — base's notice-band order against the factor's | declined, judgement | decline **agreed** on the merits; one supporting claim is inaccurate (R4-O1); corner named precisely in R4-O3 | **declined, correctly, with a provenance error in the reasoning** |
| **B1 policy-side note** — an orphaned per-variant parameter | noted, no change | agreed it is not this difficulty's to move; see R4-O4 | **noted** |

### C1 — verified closed against the banquet corpus

The condition now reads, in both tiers and verbatim in the policy's own rule:

- tier 0: *"…that agreement stands active and **the largest guest count its package handles** reaches two hundred"*
- tier 1: *"…that stands active and **the largest guest count its package handles** falls short of two hundred"*

"the largest guest count … the package handles" is the banquet corpus's own name for the column `CPARAM('banquet','max_guests')`
reads. A reader following the published banquet schedule now lands on 350 for the Seated Banquet Package, reaches two hundred, and
takes the same tier the compute binds. The vocabularies agree in both directions: nothing in the new phrase means something else in
the banquet corpus, and nothing in the banquet corpus names `max_guests` any other way.

`compute` is unchanged (`CPARAM('banquet','max_guests', client_account_code=F('client_account_code'))`), so **the tier taken did not
move** — this is a change of words correcting a mis-statement, not a change of behaviour. Confirmed by re-derivation below.

### sibling 1 and 2 — "stands open" → "stands active", verified against both corpora

- **Banquet.** `docs/banquet/` uses "stands active" throughout and contrasts it with on hold, proposed and closed — e.g.
  *"A booking is only taken on an agreement that stands active, since an agreement on hold has had booking stopped and a proposed
  agreement has not yet been countersigned"*; *"A hold or a closure is only worked while the agreement stands active, on hold or
  closed, and never on a proposal"*. **"Open" is not a state the banquet corpus defines.**
- **Cafe.** `docs/cafe/` likewise says "stands active", contrasting with suspended, in transition out, mobilizing, proposed and
  closed — e.g. *"The change is handled only where the contract stands active or suspended"*; *"Notice is handled only on a contract
  that stands active, suspended, or already in transition out. Notice is never handled on a contract that is still proposed, still
  mobilizing…"*. Six occurrences of "stands open" do appear in `docs/cafe/`, and **every one is about a different product or object**
  — a micro market standing open, a pantry programme standing open, a dispute standing open — never a cafe contract's own state.

**The teeth are real.** The cafe lifecycle is `proposed, mobilizing, active, suspended, in_transition_out, closed`
(`blueprint/db_schema.json`). A reader taking "stands open" as "not closed" admits `mobilizing`, `suspended` and `in_transition_out`;
`compute` binds `cafe_status == 'active'` and excludes all three. The round-3 condition was therefore **broader than the compute it
implements** — the rule promising a tier the compute never produces, which is check 2's reverse direction. Worse, it collided with a
live base sentence: `catering_combination_cafe_interaction` says *"Where the cafe contract at the delivery site stands suspended,
catering out of that kitchen stops with it…"*, so a suspended cafe must not draw the kitchen concession, and "open" read as "not
closed" would have given it one. Both readings now coincide: "stands active" selects exactly `cafe_status == 'active'`, on this
difficulty's worlds and on every world the ladder admits.

### sibling 3 — the cafe parameter in the cafe corpus's words

Retired: *"whose service model **takes catering out of that kitchen**"* — a phrase with **zero occurrences in `docs/cafe/`**.
New: *"whose service model **permits catering to be ordered out of that kitchen**"*. The cafe corpus prints the parameter as
*"whether **catering may be ordered out of the cafe kitchen**"*, under the schedule column **"Catering from the cafe kitchen"**
(`docs/cafe/service_operations_schedule_5c72f887.json`), whose Full Service Cafe row reads **Yes** — matching
`blueprint/products/cafe.yaml`'s `catering_from_cafe_enabled: true` for that model, which is what `CPARAM` reads. Same reading in
both corpora, same value the compute binds.

### face sweep, re-run by this audit

Retired phrasings, counted across all four extended policies: `"is written for"` **0**, `"stands open"` **0**,
`"takes catering out of"` **0**, `"at the order's delivery site"` **0**, `"venue"` **0**. The two hazard phrases still in the file are
both inside the frozen base copy and both benign, confirmed independently: `catering_payment_terms` has a *dispute* standing open, and
`parameter_schema.min_headcount` glosses the smallest guest count as the one a service level "is written for" — which **agrees** with
the banquet convention rather than contradicting it.

The exact-containment sweep of revision 3 was re-run in full: **the same 30 anaphoric residues, no more and no fewer, and the same
items**, each already adjudicated in `# revision_3` → `### the full-face sweep…`. All three cross-difficulty factors
(`programme_concession_taken`, `kitchen_service_concession`, `programme_spend_benchmark`) produce **zero** residues — every tier
condition of all three is a verbatim substring of its own rule. `compute_basis` coverage and verbatim quotation (21/21, 22/22, 20/20,
16/16), `baseline.rule` sentences, binding disjointness, `decides` never `result`, every ladder ≥3 tiers: zero failures.
`cross_category.reads` still declares every join key and every field read. Twelve `overwrite` entries, four points each, **0 failures
and 0 duplicate pairs**. Both prerequisite edges re-pass every point.

## findings (revision 4)

**No new red light.** Four observations.

**R4-O1 — observation: the C2 decline attributes to the charter a phrase that belongs to the render.**
The rationale argues that C2 needs no change partly because *"my factor states its own test order in terms ('tested in the order set
out here'), which the render carried."* Checked: `"tested in the order set out here"` occurs **zero times** in
`catering.extended.yaml` and **once** in `docs/catering/percentage_the_notice_given_yields_b980fca9.json`. The phrase is the render
agent's framing, not the charter's. What the charter actually has is clause order in the `rule` (the service-day branch before the
free-window branch, joined by a semicolon with no precedence sentence) and tier order in the ladder. **The conclusion still holds** —
every ladder in this charter is read top-down, which is how its threshold ladders work at all ("five or more … two or more …"), so the
source is determinate by the charter's own convention — but it holds by a different route than the one claimed. Considered for a red
light as a false proof sentence of the T0-F1 class and recorded as an observation instead: it misstates where a phrase lives rather
than what a value is, the proposition it supports is true, and no task reaches the corner it defends.

**R4-O2 — observation: B3's decline is correct; the residue is recorded rather than closed.**
Verified independently rather than taken on trust. The assembly sentences say the result is "rounded to two decimal places only at the
end", while `compute` also rounds five intermediates (`discounted_food`, `service_charge`, `rush_amount`, `shortfall_due`,
`late_charge`, `gross_charge`). Both paths were computed side by side on both worlds:

| quantity | rounded intermediates | single rounding at the end |
| --- | --- | --- |
| task 0 `invoice_amount_usd` | 6167.65 | **6167.65** |
| task 0 `closing_settlement_usd` | 20943.77 | **20943.77** |
| task 1 `standing_order_value_usd` | 5101.50 | **5101.50** |
| task 1 `cancellation_charge_usd` | 1409.29 | **1409.29** |

They agree to the cent everywhere, so no consequence is demonstrable and, per "Core constraints", this is an observation and not
grounds for rework. The precise residue for the record: each intermediate's own defining sentence states no rounding point, so the
five intermediate roundings are implemented in `compute` and stated by no rule sentence; the assembly sentence's "only at the end"
governs the assembly, which is rounded once. If it is ever closed, the change belongs in the rule, not the compute — the compute's
behaviour matches what `db_schema.json` and the tool contracts say the ledger carries ("USD, 2 decimal places", "rounded half to even
at the point it is booked").

**R4-O3 — observation: C2's decline is correct; here is the corner, named exactly.**
Verified by enumerating all six service levels against all four channels and both service-day cases. Base's live sentence *"Notice at
or beyond the free-cancellation hours printed against the service level carries no charge at all"* and the extended factor's
service-day-first order disagree in **exactly one** reachable corner:

> a **Drop-Off Catering Account** (free-cancellation hours 24), notice given **on the service day** (`notice_days = 0`), through the
> **account manager** (whose tier counts from the day before, giving `notice_hours = 24`). 24 reaches the 24-hour free window, so base
> yields no percentage while the extended factor yields the same-day 75 per cent.

No other level or channel reaches it. Task 0 holds an Attended Buffet Account and never touches this policy; task 1 holds an Executive
Hospitality Catering Account (free window 72) with notice two days out. **No consequence is demonstrable on either world**, so the
decline is right on the rubric this audit applies. Recorded so that if a later task is ever seeded into a Drop-Off account cancelling
on the service day through the account manager, the closure is an `overwrite` naming that base sentence, and this is where it starts.

**R4-O4 — observation: one clause of the F-3 family is still undeclared, and the asymmetry is this audit's, not the reworker's.**
`catering_combination_cafe_interaction` carries three clauses that assert what the delivery fee is in a cafe-adjacent case. Two are now
named in `catering_ext_delivered_order_invoicing.overwrite` — `[1]` (the waiver when the cafe permits catering) and `[2]` (the
"ordinary delivery fee applies however close the cafe is" clause, which was revision 2's F-3). The third is not:

> *"Where the cafe contract at the delivery site stands suspended, catering out of that kitchen stops with it and orders are produced
> at the district kitchen **at the ordinary delivery fee** until service resumes."*

Extended's `standing_round_delivery_charge` can set `delivery_fee_charged` to `0.0` or to half the printed fee irrespective of cafe
state, including while the cafe stands suspended — the same conflict on the same scored quantity that F-3 named. It is an observation
and not a red light because the antecedent is false on task 0's world (the cafe at `CS-244` stands `active`) and vacuous on task 1's
(no cafe contract), so no second defensible answer is demonstrable. Recorded honestly as **a defect of this audit's earlier
adjudication**: revision 1's `override_declarations` table judged this clause "consistent … covered by `overwrite[1]`" while flagging
its sibling as F-3, and the two clauses are the same shape. The reworker closed what this audit named; it did not miss anything it was
told. Round 4's "stands active" fix narrows the collision — a suspended cafe now plainly draws no kitchen concession — but leaves the
delivery-fee assertion undeclared.

**R4-O5 — observation: `delivery_fee_waived_with_cafe` now backs no live clause.**
`catering_combination_cafe_interaction.params.per_tier` prints `delivery_fee_waived_with_cafe` for all six service levels, and both
clauses that used it are now retired by `overwrite[1]` and `[2]`. The parameter is therefore orphaned in the base policy. Base is
frozen and deep-equals the blueprint, so it is not this difficulty's to remove, and a per-tier parameter with no live clause produces
no scored value and no second reading — an agent cannot apply a clause that has been superseded. Agreed with the reworker that it is
not a source-layer red light, and recorded because it is a consequence of the F-3 and O-1 closures this audit asked for, and because
the render finding it feeds (B1) can only be closed with a clause that would have to come from this charter.

## per-task verdicts (revision 4)

| task | policy self-consistency | problem tree | factors bear weight | unique solution |
| --- | --- | --- | --- | --- |
| 0 | **PASS** | **PASS** | **PASS** | **PASS** |
| 1 | **PASS** | **PASS** | **PASS** | **PASS** |

**The difficulty passes the source-layer audit.** The published corpus still reflects the round-3 charter and must be re-rendered;
the four wording changes are all in prose that the render carries verbatim, so the re-render is where this fix becomes visible to a
solver.

## closing_checklist (revision 4)

| item | state |
| --- | --- |
| per-task audit files one-to-one with the tasks, `_difficulty.md` alongside | ✔ |
| old revisions traceable | ✔ revisions 1–3 untouched; this appended under `revision_4` |
| every comparison section carries a PASS | ✔ `0.md` and `1.md` → `revision_4` both PASS on all four relationships |
| extended policies fully covered, scopes pairwise disjoint over the whole tree | ✔ unchanged |
| task tools and GT closed; uuid8s independently generated and frozen | ✔ `task_tools.py` byte-identical to round 3; `cb57dc9d`, `1e20ba9d`, `69ffeeb0`, `b7aa0639` |
| trees: 1–3 prerequisite problems, ≥ max(n−1,1) `value_input` edges, ≥1 `owner=user` problem, no cycle; difficulty-wide DAG | ✔ both re-walked |
| self-sufficient baseline per computation, definite and ≠ gold | ✔ 6534.99 / 36550.00 / 6400.00 / 3315.97 |
| 4–6 factors per computation matching its draw, ≥2 `parameter`, ≥1 `method` | ✔ 5/5/4/5 against draws `[5,5]` and `[5,4]` |
| per task ≥1 multi-source and ≥1 cross-difficulty factor | ✔ both, and **every cross-product condition now reads the same way in the corpus it points at** |
| every ladder ≥3 tiers stated in full in its rule | ✔ exact-containment sweep: the same 30 anaphoric residues as revision 3, no new item |
| every ladder's tiers distinct in outcome | ✔ unchanged |
| every factor bears weight against an honest baseline | ✔ all nineteen substitutions re-run, every figure reproduced |
| instantiation gates re-run on the final form | ✔ seven green plus `BASE FROZEN OK (10 files verified by hash)`; none of them, and none of the render gates, could have seen R4-F0 — only reading the other product's published words could |
