# Policy-task audit — travel_protection_desk / charter-global

## charter_global_frozen

- **Revision:** 1 (first audit of this difficulty; no prior revision exists).
- **Freeze time:** 2026-09-17 (UTC), before any task's `evaluation_criteria` / `computations` were read.
- **Auditor:** independent source-layer auditor; not the agent that instantiated these artifacts.
- **Frozen inputs and hashes:**
  - `env/env_0000_online_travel_agency/tasks/travel_protection_desk/care.extended.yaml` — sha256/16 `1260bf70075f429a` (3009 lines), read in full.
  - `env/env_0000_online_travel_agency/tasks/travel_protection_desk/task_tools.py` — sha256/16 `9fdcb64bfc3a9f88` (6 tools), read in full.
  - `env/env_0000_online_travel_agency/blueprint/blueprint.yaml`, `db_schema.json`, `share_tools.py`, `products/care.yaml`, and the cross-category products `club.yaml`, `bundle.yaml`, `air.yaml` (variant parameters only, as the `CPARAM`/`CFIELD` reads require).
- **Fields permitted at this stage:** the whole extended charter (`rule`, `baseline`, `compute_basis`, `compute`, `factors`, `prerequisite`, `overwrite`, `params`, `cross_category`, `inputs`), the tool contracts and runnable bodies, and each task's `frozen_time` / `user_scenario` / `initial_state` through the masked views.
- **Fields explicitly masked and not read while this section was written:** `evaluation_criteria`, `computations`, `charter_scope`, `required_documents`, `design_rationale`, `solvability_contract`, `prerequisite_closure`, `db_closure`, `db_closure_matches_initial_state` — for both tasks. Nothing in this section is derived from a revealed GT field.
- **Entry conditions (Step 0):** supplied and checked, not re-run by the auditor. The brief carried the seven instantiation-stage gate commands with their actual output lines (EXTENDED, TASK TOOL CONTRACT, REPLAY, SOLVABILITY, COMPUTE, GROUNDING, SCOPE — all OK; `check_traceability.py` correctly deferred to the render stage), and the two masked views with hashes `21c2fb233c58f943` (0) and `a5ab17b72c67be54` (1), both re-verified by the auditor. Entry conditions are **complete**. A machine green light is the qualification to enter this audit, not a proof of correctness.

### policy_conflict_scan

The structured policy in force for category `care` is the base section of `care.extended.yaml` (lines 1–1747) plus six `extended_policies` (lines 1749–3009).

**Base copy is verbatim.** `diff` of `blueprint/products/care.yaml` against lines 1–1748 of `care.extended.yaml` differs only by one trailing blank line. The base section has not been rewritten.

**Subjects, triggers and target tools.** The six extended policies partition their write surface cleanly:

| policy | subject (event) | `computes` | `target_tool` | trigger |
| --- | --- | --- | --- | --- |
| `care_ext_outstanding_loading_charge` | `care_premium_charge` | `amount_usd` | `charge_destination_loading_6e26c317` | state_due |
| `care_ext_supplier_recovery_declaration` | `care_claim_recovery` | `restored_amount_usd` | `declare_supplier_compensation_6de86425` | state_due |
| `care_ext_settled_benefit_payment` | `care_claim_payout` | `paid_amount_usd` | `settle_benefit_payment_411249ab` | state_due |
| `care_ext_declared_cost_restatement` | `care_insured_amend` | `corrected_trip_cost_usd` | `restate_declared_trip_cost_4b2fbffa` | state_due |
| `care_ext_reration_difference` | `care_premium_adjustment` | `adjustment_amount_usd` | `raise_rating_adjustment_56692b3c` | state_due |
| `care_ext_cancellation_claim_intake` | `care_claim_file` | `claimed_amount_usd` | `file_cancellation_claim_621a2df1` | on_request |

No two policies claim the same `(target_tool, computes)` pair and no two claim the same subject event. Eligibility, time anchors and terminal states do not overlap between the six.

**Cross-category read boundaries.** Declared reads are `club` (branch) for `care_ext_outstanding_loading_charge`; `air` (history) for `care_ext_supplier_recovery_declaration`; `bundle` (history) for `care_ext_declared_cost_restatement`, `care_ext_reration_difference` and `care_ext_cancellation_claim_intake`; none for `care_ext_settled_benefit_payment`. Every `CPARAM`/`CFIELD`/`XSUM`/`XCOUNT`/`XLATEST` call in the six `compute` blocks names one of those declared categories and no other. No read crosses into `stay`, `drive` or `biz`.

**Scope exclusivity and completeness of the M=2 suite.** The `prerequisite` graph falls into exactly two connected components, and each is one task's whole problem tree:

- Component A — `care_ext_settled_benefit_payment` (root) ← `care_ext_supplier_recovery_declaration`, `care_ext_outstanding_loading_charge`.
- Component B — `care_ext_cancellation_claim_intake` (root) ← `care_ext_declared_cost_restatement`, `care_ext_reration_difference`; and `care_ext_reration_difference` ← `care_ext_declared_cost_restatement`.

The two components share no policy, so the two tasks' scopes are **pairwise disjoint**, and together they cover all six extended policies, so the suite is **jointly complete**. No cross-component edge exists, so no cycle can be created by combining the two tasks.

**Conflicts found at charter level:** one, recorded as finding **F-C** below (an undeclared inheritance from `care_policy_amendment`). Two further conflicts between a `rule` sentence and its own `compute` are recorded as **F-A** and **F-B** under `rule_compute_equivalence`.

### rule_compute_equivalence

Check 2 was run sentence by sentence over all six policies, in both directions: every quantity, window, filter, tier, branch, cross-category read, acting base, grouping, cap/floor and rounding convention in `compute` was traced back to a `compute_basis` quotation and thence to a sentence of the policy's own `rule`; and every sentence of each `rule` was traced forward to a binding.

**Rounding and interval conventions.** All six policies round once, at `result`, with `RND(x, 2)`; every day count is `DAYS(a, b)` (exclusive) with an explicit `+ 1` wherever the rule says "both days counted" (`journey_days`, `days_remaining`, `cover_days_bought`). Each `+ 1` has a rule sentence behind it. `MX(0.0, …)` floors are each carried by a "never falls below nothing" sentence. No rounding point is invented and none is promised without being implemented.

**Ladders.** Every tier named in a `factors[].ladder` is a sentence of the owning `rule` and a branch of the `decides` binding, and every branch of each `decides` binding is a tier the rule states. No tier lives only in `compute`, and no tier is promised in prose without a branch. This was checked for all 27 factors across the six policies.

**Two filters in `compute` have no counterpart in any sentence of their `rule`.** These are the charter-global halves of findings **F-A** and **F-B**; their consequences are demonstrated in `1.md`.

- **F-A.** `care_ext_reration_difference`, binding `last_package_line`:
  `"last_package_line": "XLATEST('bundle','bundle_ledger_entries','posted_date', date_field='posted_date', reason_code='routine_package')"`
  Its `compute_basis` entry quotes: *"Where the linked package's ledger carries a line posted after the certificate was issued and that line was posted before the first day of the journey insured, the day the correction takes effect is the day that line posted."* The quoted sentence — and every other sentence of that `rule` — says **a line**, with no restriction to lines posted under the package's routine terms. The filter `reason_code='routine_package'` is a basis `compute` invents for itself. (The restriction appears only in `cross_category[0].note`, which is authoring metadata, not the policy surface a reader sees.) By contrast, the sibling policy `care_ext_declared_cost_restatement` **does** state the same restriction in prose — *"every line posted to the package under its routine terms"* — which shows the charter knows how to say it and did not say it here.
- **F-B.** `care_ext_declared_cost_restatement`, binding `operator_returns`:
  `"operator_returns": "XSUM('bundle','bundle_ledger_entries','amount_usd', date_field='posted_date', reason_code='price_guarantee')"`
  Its `compute_basis` entry quotes: *"The amounts the operator has already returned against the package are recognised at nothing and taken off the outlay."* Neither that sentence nor the three ladder sentences of `returned_value_recognition` restricts "the amounts the operator has already returned" to a price-guarantee line. The tier that actually fires is worded *"Where the package returns value **only as a future travel credit** and the credit standing open against it may still be redeemed after the last day of the journey insured, the amounts the operator has already returned are recognised at three quarters"* — a tier about credits, discounting a quantity from which `compute` excludes the credit. The same charter treats an open credit as returned value in prose: `care_ext_cancellation_claim_intake` says *"the value the operator has given back is the amounts returned to the traveller **together with the credit standing open**"*. Two sentences of one charter use the same idea and one `compute` excludes it.

Apart from F-A and F-B, no further binding was found whose basis is absent from its rule, and no rule sentence was found that no binding implements. Three narrower mismatches that change no value on either task's world are recorded as observations **O-1**, **O-2** and **O-3** below.

### action_binding_and_uuids

- **`(target_tool, computes)` uniqueness.** All six pairs are distinct and each is claimed by exactly one policy (table under `policy_conflict_scan`). Each policy's subject, `base_policy_refs`, target tool, docstring and terminal state admit one business reading; no confirmation step, review, wait or procedure outside the policy is added by any docstring.
- **Docstring silence about sequence.** No docstring names another tool, and none states its own action's position in a sequence. The phrase "Once the call completes, …" in all six refers to that call's own completion. Three docstrings describe the *object* by a state it already stands in — `settle_benefit_payment_411249ab` "a claim the insurer has **already** decided", `declare_supplier_compensation_6de86425` "a loss their … certificate has **already** settled", `raise_rating_adjustment_56692b3c` "against an **earlier** premium line". These identify which record the call acts on rather than order this call against another problem's write, and none names a tool or a policy. Not a defect.
- **uuid8s.** `6e26c317`, `6de86425`, `411249ab`, `4b2fbffa`, `56692b3c`, `621a2df1`. All six are distinct, none is reused, none shares a prefix with another beyond a single leading character (`6e26c317` / `6de86425` diverge at the second character), none is a sequence number or an adjacent value of another, and none is derivable from a common stem. Each is frozen with its tool in the module and in the `target_tool` of exactly one policy. **PASS.**
- **Tool bodies do not judge prerequisites.** All six function bodies were read in full. Each consists of a `ctx.make_id` (five of six), a single `ctx.create` or `ctx.update`, and a return string. There is no `if`, no `raise`, no lookup of another table, and no hint. The environment judges no prerequisite and refuses no call while one is unresolved. **PASS.**

### prerequisite_graph

Check 7 over the whole graph. Six policies; `prerequisite` is filled in on every one (`[]` on `care_ext_outstanding_loading_charge`, `care_ext_supplier_recovery_declaration`, `care_ext_declared_cost_restatement`).

| blocked policy | problem | kind | gate | form | resolved_by |
| --- | --- | --- | --- | --- | --- |
| `care_ext_settled_benefit_payment` | `care_ext_supplier_recovery_declaration` | `value_input` | `benefit_consumed` | state | `declare_supplier_compensation_6de86425` |
| `care_ext_settled_benefit_payment` | `care_ext_outstanding_loading_charge` | `state_gate` | `care_premium_entries.charge_category` | state | `charge_destination_loading_6e26c317` |
| `care_ext_reration_difference` | `care_ext_declared_cost_restatement` | `value_input` | `new_base` | state | `restate_declared_trip_cost_4b2fbffa` |
| `care_ext_cancellation_claim_intake` | `care_ext_declared_cost_restatement` | `value_input` | `unrecovered` | state | `restate_declared_trip_cost_4b2fbffa` |
| `care_ext_cancellation_claim_intake` | `care_ext_reration_difference` | `state_gate` | `care_premium_entries.charge_category` | state | `raise_rating_adjustment_56692b3c` |

- **Every `problem` points at another extended policy id in this file**, never at a base policy and never at itself. **PASS.**
- **Acyclicity.** Topological order of component A: `{outstanding_loading_charge, supplier_recovery_declaration}` → `settled_benefit_payment`. Component B: `declared_cost_restatement` → `reration_difference` → `cancellation_claim_intake`. No back edge in either; the whole difficulty's graph is a DAG. **PASS.**
- **`policy_source` verbatim locatable in the blocked policy's own `rule`.** All five quotations were located character-for-character in the `rule` string of the policy that declares the edge (not in the depended-on policy's rule, and not in `compute_basis` alone). **PASS.**
- **`form` and `fallback_reason`.** All five edges declare `form: state`; none carries a `fallback_reason`, and none is required, since no edge is in the action form. The state form has priority and is honoured throughout — there is no action-form edge in this charter to test. **PASS.**
- **`resolved_by` genuinely makes `effect` hold.** `declare_supplier_compensation_6de86425` creates a `care_claims` row with `event_type="care_claim_recovery"` and a negative `paid_amount_usd`, which is exactly the row `benefit_consumed`'s `restored_amounts` binding sums — so the value input changes. `charge_destination_loading_6e26c317` creates a `care_premium_entries` row with `charge_category="destination_loading"`, which is the state the gate names. `restate_declared_trip_cost_4b2fbffa` performs `ctx.update("care_policies", …, trip_cost_usd=…)`, which is the field `new_base` and `unrecovered` read through `F('trip_cost_usd')`. `raise_rating_adjustment_56692b3c` creates a `care_premium_entries` row with `charge_category="premium_adjustment"`, the state that gate names. **PASS.**
- **`kind` matches `gate`.** The three `value_input` edges name `benefit_consumed`, `new_base` and `unrecovered` — each is a real binding name in the blocked policy's own `compute` (verified against the binding lists). The two `state_gate` edges name `care_premium_entries.charge_category`, a real eligibility surface rather than a binding. **PASS.**
- **No authoring-viewpoint phrasing.** No `prerequisite` field contains "in this task", "at the opening", "the current world" or any equivalent. **PASS.**
- **`condition` neither strengthened nor weakened**, with one narrowing recorded as observation **O-4**.

### prerequisite_sentences

Check 6, four-point test, on each of the five edges. Each sentence is quoted from the blocked policy's own `rule`.

1. `care_ext_settled_benefit_payment` → `care_ext_supplier_recovery_declaration`
   *"The benefit a settlement pays is fixed only after the benefit the certificate records as consumed carries a restoration for every amount a supplier has paid the traveller for a loss the certificate has already settled."*
   Ordering connective **"only after"** ✔. What it waits on is a record-visible state — *the benefit the certificate records as consumed carries a restoration* — named in the words the tables and the finders use (`benefit_used`, the claim record), with no action, performer or tool ✔. No tool name, policy id, snake_case token or row id ✔. Strength matches the `condition` ✔.
   **Single-write derivation:** the only write in this difficulty that puts a restoration against a certificate's consumed benefit is `declare_supplier_compensation_6de86425` (the only one creating `event_type="care_claim_recovery"`; `settle_benefit_payment_411249ab` creates `care_claim_payout` and `file_cancellation_claim_621a2df1` creates `care_claim_file`). Reading the sentence, then the records, then `care_ext_supplier_recovery_declaration`'s own rule — *"the traveller declares what they received and that amount is restored to the benefit the certificate records as consumed"* — yields that write in exactly one reading. ✔
2. `care_ext_settled_benefit_payment` → `care_ext_outstanding_loading_charge`
   *"A settlement is paid on a certificate only after its premium lines carry every rating component the certificate's declared particulars call for."*
   **"only after"** ✔; state form, naming premium lines and rating components in table words ✔; no tool/id ✔.
   **Single-write derivation:** the reader compares the certificate's premium lines against the components the plan's rating calls for, finds the destination loading absent, and reaches `care_ext_outstanding_loading_charge`'s own rule — *"A certificate carries one destination loading line for the region it declares, and where the premium lines carry none the loading is owed and is charged as its own line"* — whose target tool is the only write creating `charge_category="destination_loading"`. One reading. ✔ (Scope narrowing recorded as **O-4**.)
3. `care_ext_reration_difference` → `care_ext_declared_cost_restatement`
   *"The difference the re-rating raises is fixed only after the certificate's declared trip cost matches the prepaid outlay standing against the journey insured on the booking the cover was bought alongside."*
   **"only after"** ✔; state form (*the certificate's declared trip cost matches the prepaid outlay*) ✔; no tool/id ✔; strength matches ✔.
   **Single-write derivation:** `restate_declared_trip_cost_4b2fbffa` is the only write in this difficulty that changes `care_policies.trip_cost_usd` (the only `ctx.update` in the module). One reading. ✔
4. `care_ext_cancellation_claim_intake` → `care_ext_declared_cost_restatement`
   *"The amount claimed is worked out only once the certificate carries the declared trip cost the journey insured actually carried."*
   **"only once"** ✔; state form ✔; no tool/id ✔. Same single write as edge 3. ✔
5. `care_ext_cancellation_claim_intake` → `care_ext_reration_difference`
   *"A claim is filed for an amount on a certificate only after its premium lines carry the re-rating its corrected particulars call for."*
   **"only after"** ✔; state form (*its premium lines carry the re-rating*) ✔; no tool/id ✔.
   **Single-write derivation:** `raise_rating_adjustment_56692b3c` is the only write creating `charge_category="premium_adjustment"`. One reading. ✔

- **No second wording, tool name or other problem's id.** Each of the three blocked rules carries its prerequisite sentence once and says nothing further about the dependency. No `rule` in this charter contains a tool name, a policy id or a snake_case token.
- **The depended-on rule does not restate the sentence.** `care_ext_supplier_recovery_declaration`, `care_ext_outstanding_loading_charge` and `care_ext_declared_cost_restatement` each carry only their own rule and say nothing about settlement, re-rating or claim filing. ✔
- **No undeclared cross-problem order in any extended rule.** Every ordering connective in the six `rule` strings was located; all five occurrences ground a declared edge, and no sixth exists.
- **Base rules stating a cross-problem order.** `care_premium_rating` says *"Where a declared particular changes after issue, the premium is re-rated from the day the change takes effect"*, an amendment→re-rating order. Task 1's tree does not rest on it: `care_ext_reration_difference` carries its own prerequisite sentence (edge 3). Per the skill this is therefore recorded as an observation, **O-5**, not a red light.

### override_declarations

Check 1's **finding half**, once, sentence by sentence against every `base_policy_refs` entry of all six extended policies. Consequences are demonstrated in the task files that carry the affected world.

| extended policy | base refs | verdict |
| --- | --- | --- |
| `care_ext_outstanding_loading_charge` | `care_premium_rating`, `care_club_and_bundle_interaction` | 2 conflicts declared; 2 observations (**O-6**, **O-7**) |
| `care_ext_supplier_recovery_declaration` | `care_subrogation`, `care_claim_settlement` | 2 conflicts declared; 1 observation (**O-8**) |
| `care_ext_settled_benefit_payment` | `care_claim_settlement`, `care_agg_benefit_coordination` | 2 conflicts declared; 1 observation (**O-9**) |
| `care_ext_declared_cost_restatement` | `care_policy_amendment`, `care_club_and_bundle_interaction` | 1 conflict declared; **1 undeclared override — F-C** |
| `care_ext_reration_difference` | `care_premium_rating` | 1 conflict declared; rest inherited without conflict |
| `care_ext_cancellation_claim_intake` | `care_claim_filing` | 1 conflict declared; rest inherited without conflict |

**F-C — undeclared override of `care_policy_amendment`'s timing bar.**
`care_ext_declared_cost_restatement` declares `base_policy_refs: [care_policy_amendment, care_club_and_bundle_interaction]` and one `overwrite` entry, naming only the base clause *"An increase in the declared trip cost is accepted only up to the plan's ceiling"*. Every other sentence of `care_policy_amendment` is therefore inherited in full. Two of them govern exactly the quantity and the moment this policy writes:

> *"A declared particular of the risk may be corrected **while the policy stands**, and the premium follows the correction from the day it takes effect."*
> *"**No amendment is accepted once the journey has begun** or once a claim has been filed, because the risk is then no longer uncertain."*

`care_ext_declared_cost_restatement`'s `subject` is `care_insured_amend` — the very event `care_policy_amendment` governs (*"The declared trip cost, the destination or the travelling party on a certificate is corrected"*) — and its target tool `restate_declared_trip_cost_4b2fbffa` performs that correction. Its own `rule` carries no sentence about when the correction may be made, and its `overwrite` does not name the timing bar. The base prohibition therefore stands, unmodified, over a write the charter requires. This is an **undeclared override**: two clauses rendered into the same documents reach opposite conclusions on the same act. Whether it hands a task a second defensible answer is a fact about a world; that demonstration is in `1.md`.

Every other base sentence was reached a conclusion on. Notably: `care_free_look`, `care_midterm_cancellation`, `care_coverage_term`, `care_claim_assessment`, `care_underwriting` and `care_agg_multi_holding` are cited by no extended policy and govern no write this suite makes, so nothing weakens them. The `overwrite: []`-equivalent cases (a `base_policy_refs` entry with no entry naming it) were held to the same sentence-by-sentence standard, not a laxer one. None of the three disguised forms — the anonymous intermediate factor, the 0/1 multiplier, the dropped branch — was found, with one qualification: `care_ext_settled_benefit_payment`'s `stated_limit` **does** drop branches of the base promise, recorded as **O-9**.

### factor_ladders

Charter-global structure only. Whether a factor bears weight is a fact about one world and lives in the task files' `factor_weight`.

| policy | factors | `parameter` | `method` | multi-source tiers | `cross_difficulty` |
| --- | --- | --- | --- | --- | --- |
| `care_ext_outstanding_loading_charge` | 4 | 3 | 1 | `protection_discount`, `loading_base_basis`, `journey_exposure_share` | `protection_discount` → **club** |
| `care_ext_supplier_recovery_declaration` | 4 | 2 | 2 | `supplier_return_scope`, `supporting_evidence_share`, `certificate_retained_share`, `restoration_bound_basis` | `supplier_return_scope`, `supporting_evidence_share` → **air** |
| `care_ext_settled_benefit_payment` | 5 | 2 | 3 | `benefit_limit_basis`, `benefit_consumed_basis`, `supporting_document_share`, `deductible_called_for_rate`, `deductible_ceiling_basis` | none |
| `care_ext_declared_cost_restatement` | 4 | 3 | 1 | `outlay_evidence_basis`, `returned_value_recognition`, `insured_party_share`, `declared_ceiling_basis` | `outlay_evidence_basis`, `returned_value_recognition`, `insured_party_share` → **bundle** |
| `care_ext_reration_difference` | 6 | 2 | 4 | `correction_effective_anchor`, `attaching_loading_basis`, `correction_evidence_share`, `charged_premium_basis`, `insured_party_uplift`, `cover_term_basis` | `correction_effective_anchor`, `correction_evidence_share` → **bundle** |
| `care_ext_cancellation_claim_intake` | 4 | 3 | 1 | `recovered_value_scope`, `open_credit_valuation`, `cancellation_promptness_share`, `returned_deposit_share` | all four → **bundle** |

- **Counts.** Every policy declares 4 to 6 factors, at least 2 labelled `parameter` and at least 1 labelled `method`. **PASS.**
- **Per-task floors.** Task 0's three computations carry a multi-source factor and a `cross_difficulty` factor reading `club` and `air`; task 1's three carry a multi-source factor and four `cross_difficulty` factors reading `bundle`. **PASS** (the seeding half is checked per task).
- **Ladder depth and disjointness.** All 27 ladders carry exactly three tiers, the fall-through counted, and each ladder's first two tiers are written as mutually exclusive conjunctions with an `otherwise` that catches the rest. No ladder overlaps as stated. **PASS.**
- **`decides` is an input, never `result`.** All 27 `decides` targets are intermediate bindings (`protection_discount_pct`, `loading_base`, `scoped_returns`, `benefit_limit`, `effective_anchor`, `notice_share`, …). None names `result`. **PASS.**
- **Binding sets disjoint within each policy.** Checked per policy; no binding appears in two factors' `bindings` lists. **PASS.**
- **Every tier stated in the `rule`, condition and outcome both, and implemented in `compute`.** Checked for all 27 (see `rule_compute_equivalence`). **PASS**, subject to **F-A** and **F-B**, where the *implementation* carries a filter the stated tier does not.
- **Labels honest.** Each `method` factor's tiers select a different algorithm (which rows are summed, which anchor date is taken, which divisor counts the term, whether adjustments join the base), not merely a different number; each `parameter` factor's tiers select a number. No `method` tier names a computation rule the charter does not state. **PASS.**
- **Distinct outcomes per ladder.** 26 of 27 ladders select three pairwise different values or methods on every plan. One does not, on some plans — **O-10**.
- **One tier condition holds of every customer who reaches its write — F-D.**
  `care_ext_settled_benefit_payment`, factor `benefit_limit_basis`, tier 1:
  *"Where the benefit allowed is one the plan states as an amount for each insured traveller **and the loss the claim arises from was suffered by one insured traveller named on the certificate**, the limit the benefit claimed carries is the plan's amount for that benefit."*
  implemented as `stated_limit if (claim_type_paid != 'trip_cancellation' and claim_insured_seq >= 1) else …`, where `claim_insured_seq = LATEST('care_claims','insured_sequence', date_field='decided_date', event_type='care_claim_decision')`.
  The second conjunct `claim_insured_seq >= 1` is true of **every** claim that can reach this write. The base charter defines `care_claim_decision.insured_sequence` as *"insured traveller claiming"*, and all three claim-writing tool contracts in `task_tools.py` require it to be *"a whole number **starting at 1**"* (`file_cancellation_claim_621a2df1`, `settle_benefit_payment_411249ab`, `declare_supplier_compensation_6de86425`). A decision row therefore always names an insured traveller at sequence 1 or above, so the conjunct divides no customers and restates the policy's scope instead. Under the skill's test — *"name a condition, or one part of a compound condition, that holds of every customer who reaches this write"* — this is a **`SOURCE-FACTOR RED`**. Its effect on a particular score is demonstrated in `0.md`.

### findings

Each finding names the tasks it bears on, so their files can pick up the demonstration rather than re-derive the finding.

#### F-A — `SOURCE-POLICY RED`: `care_ext_reration_difference` computes `last_package_line` on a filter no sentence of its rule states
- **Symptom.** The binding that fixes the day the correction takes effect reads only ledger lines carrying `reason_code='routine_package'`, while the rule sentence behind it speaks of *a line* with no restriction.
- **Root cause.** A filter present in `compute` and absent from `rule` and from `compute_basis`'s quotation: `compute` invents a basis of its own.
- **Evidence.** `care.extended.yaml`, `care_ext_reration_difference.compute[13]` = `XLATEST('bundle','bundle_ledger_entries','posted_date', date_field='posted_date', reason_code='routine_package')`; `compute_basis.last_package_line` quotes *"Where the linked package's ledger carries a line posted after the certificate was issued and that line was posted before the first day of the journey insured, the day the correction takes effect is the day that line posted."*; the sibling policy `care_ext_declared_cost_restatement` states the very restriction in prose (*"under its routine terms"*), showing the omission is not a house convention.
- **Demonstrated consequence.** Two defensible readings, two numbers — demonstrated on task 1's world in `1.md` (`127.59` against `35.73`).
- **Affected artifact.** `env/env_0000_online_travel_agency/tasks/travel_protection_desk/care.extended.yaml`, policy `care_ext_reration_difference`: `rule`, `compute_basis.last_package_line`, `compute[13]`, factor `correction_effective_anchor`. **Bears on: task 1.**

#### F-B — `SOURCE-POLICY RED`: `care_ext_declared_cost_restatement` computes `operator_returns` on a filter no sentence of its rule states
- **Symptom.** "The amounts the operator has already returned against the package" is implemented as the price-guarantee refund alone, excluding the future travel credit the operator issued — while the tier that discounts that quantity is itself conditioned on the package returning value *only as a future travel credit*.
- **Root cause.** A filter present in `compute` and absent from `rule`, `baseline.rule` and `compute_basis`'s quotation; and a tier whose condition and whose quantity are about different things.
- **Evidence.** `care_ext_declared_cost_restatement.compute[7]` = `XSUM('bundle','bundle_ledger_entries','amount_usd', date_field='posted_date', reason_code='price_guarantee')`; `compute_basis.operator_returns` quotes *"The amounts the operator has already returned against the package are recognised at nothing and taken off the outlay."*; factor `returned_value_recognition` tier 2 reads *"Where the package returns value only as a future travel credit … the amounts the operator has already returned are recognised at three quarters"*; and `care_ext_cancellation_claim_intake`'s rule, in the same charter, counts an open credit as returned value — *"the value the operator has given back is the amounts returned to the traveller together with the credit standing open"*.
- **Demonstrated consequence.** Two defensible readings, two numbers, propagating into both dependent problems — demonstrated on task 1's world in `1.md` (`18,436.50` against `12,114.00`).
- **Affected artifact.** Same file, policy `care_ext_declared_cost_restatement`: `rule`, `baseline.rule`, `compute_basis.operator_returns`, `compute[7]`, factor `returned_value_recognition`. **Bears on: task 1.**

#### F-C — `SOURCE-POLICY RED`: undeclared override of `care_policy_amendment`'s "no amendment once the journey has begun"
- **Symptom.** The base policy the extended policy cites forbids the amendment the extended policy requires, and `overwrite` does not name the forbidding sentence.
- **Root cause.** An override taken but not declared. Base and extended are rendered into the documents together, so both sentences reach the reader.
- **Evidence.** `blueprint/products/care.yaml`, `care_policy_amendment.rule`: *"No amendment is accepted once the journey has begun or once a claim has been filed"* and *"A declared particular of the risk may be corrected while the policy stands"*; `care.extended.yaml`, `care_ext_declared_cost_restatement.base_policy_refs` includes `care_policy_amendment`, `subject: [care_insured_amend]`, and `overwrite` names only *"An increase in the declared trip cost is accepted only up to the plan's ceiling"*.
- **Demonstrated consequence.** Act-now against refuse, on a certificate whose record says the journey has begun — demonstrated on task 1's world in `1.md`.
- **Affected artifact.** `care.extended.yaml`, policy `care_ext_declared_cost_restatement`: `overwrite`, `rule`. **Bears on: task 1.**

#### F-D — `SOURCE-FACTOR RED`: a conjunct of `benefit_limit_basis` tier 1 holds of every customer who reaches the write
- Set out in full under `factor_ladders` above. **Bears on: task 0.**

#### Observations (no consequence demonstrable on either task's world; not grounds for rework)

- **O-1.** `care_ext_supplier_recovery_declaration.compute[8]`: `claim_document_ref = LATEST('care_claims','supporting_document_reference', date_field='filed_date', event_type='care_claim_file', claim_type='travel_delay')`. The rule says *"the claim the certificate settled names the evidence that supports it"* — no benefit is named. The `claim_type='travel_delay'` filter is `compute`-only. On task 0's world the certificate's settled payment **is** the travel-delay one and both readings give a non-empty reference, so the tier does not move.
- **O-2.** Same policy, `compute[7]`: `supplier_notice_refs = XCOUNT('air','air_booking_events', …, charge_category='refund_payout', reason_code='involuntary_schedule_change')`. The rule says *"the supplier's return carries **the reference of a notice** the supplier issued"*; `air_booking_events` carries a `notice_reference` field that `compute` does not read, proxying it by `reason_code` instead. Both give 1 on task 0's world.
- **O-3.** `care_ext_settled_benefit_payment.compute[19]`: `term_withholdings = COUNT('care_claims', date_field='decided_date', event_type='care_claim_payout')` implements *"the certificate **has withheld deductibles** in this policy term"*. It counts payouts, not payouts from which a deductible was withheld. Equivalent on task 0's world (the single payout withheld 120.00).
- **O-4.** The prerequisite `condition` on the edge `care_ext_settled_benefit_payment` → `care_ext_outstanding_loading_charge` reads *"the certificate's premium lines carry a destination loading line for the region the certificate declares"*, narrower than its own sentence *"every rating component the certificate's declared particulars call for"*. No second reading arises, because on task 0's world only the destination loading is missing and only one write supplies it.
- **O-5.** Base `care_premium_rating` states a cross-problem order (*"Where a declared particular changes after issue, the premium is re-rated from the day the change takes effect"*). Task 1's tree does not rest on it — `care_ext_reration_difference` carries its own prerequisite sentence — so per the skill this is an observation rather than a red light.
- **O-6.** Base `care_club_and_bundle_interaction` says *"A club discount is applied to the rated premium after loadings and before the policy fee"*; `care_ext_outstanding_loading_charge` applies it to the destination-loading line alone (*"the discount acts once on the rated loading and never on any other premium line"*). The `overwrite` names only the tier-selection sentence. The extended policy computes one line, so the two readings do not produce two figures for that line.
- **O-7.** Base `care_premium_rating` says *"Where the rated premium falls below the plan's minimum premium, the minimum is charged instead"*; the extended `loading_base` fall-through uses `min_premium_usd` as the base the loading acts on, a different use of the same parameter. Not a floor on the extended result, and not exercised on task 0's world.
- **O-8.** Base `care_subrogation` says *"A recovery is applied against the payment it reverses and never against a different claim or a different policy"*; `restoration_bound_basis` tier 2 bounds the restoration by *"the total of the payments settled"*, aggregating across payments. Tier 2 does not fire on task 0's world (one settled payment).
- **O-9.** `care_ext_settled_benefit_payment.compute[2]`: `stated_limit` enumerates four benefits (`baggage_loss`, `travel_delay`, `medical_emergency`) and falls through to `P('baggage_delay_limit_usd')` for every other, while the rule promises *"the plan's amount for that benefit"* and the tool contracts admit **eleven** benefits. For a decided `evacuation` claim on TripGuard Plus the rule promises 500,000.00 and `compute` returns 500.00. Neither task's world carries such a claim, so no consequence is demonstrable here. This is the **dropped-branch** form, and it is the one place in this charter where it appears.
- **O-10.** `care_ext_settled_benefit_payment`, factor `deductible_called_for_rate`: its three tiers select `P('medical_deductible_usd')`, `P('deductible_per_claim_usd')` and `K('ceiling_reached_deductible_usd')` = 0. On TripGuard Premier, Cancel For Any Reason Elite and Annual Multi-Trip Executive all three plan parameters are `0.0`, so the ladder is written as three tiers that select one value; on those plans `deductible_per_policy_usd` is also `0.0`, so `deductible_headroom` is never above nothing and only the fall-through can ever fire. Task 0 is on TripGuard Plus (100.0 / 50.0 / 0), where the three are distinct, and no other task uses this policy, so no consequence is demonstrable.
- **O-11.** `care_ext_supplier_recovery_declaration.inputs.history` declares the `air` read with `filters: {reason_code: involuntary_schedule_change}`, while `compute` also reads `air_refund_payout` rows without that filter (`all_returns`, `recent_returns`) and counts `air_schedule_change_notice` rows. The declaration does not describe the reads. `inputs` is not the surface a solver reads, and no value moves.

## closing_checklist

**This difficulty is NOT closed out.** Step 4 permits closing only once all M tasks carry a frozen derivation and a comparison **and all four relationships PASS**. Task 1 fails two of them and task 0 fails one, so the checklist below records what holds and what does not rather than certifying the difficulty.

| Step 4 item | status |
| --- | --- |
| Per-task audit files correspond one-to-one with the tasks, `_difficulty.md` alongside them | **holds** — `0.md`, `1.md`, `_difficulty.md` in `env/env_0000_online_travel_agency/audits/policy_task/travel_protection_desk/`. Revision 1; no old revisions to preserve. |
| Every comparison section carries a PASS | **fails** — `0.md` §`source_gt_comparison` carries `SOURCE-FACTOR RED`; `1.md` carries `SOURCE-POLICY RED` and `SOURCE-TASK RED`. |
| Extended policies fully covered; M task scopes pairwise disjoint over the whole problem tree | **holds** — all six covered, the two trees share no policy (§`policy_conflict_scan`). |
| Task tools and GT closed | **holds** — six tools, each claimed by one policy, each called by exactly one task's GT; no GT write uses a tool outside its task's `charter_scope`. |
| Each task tool uses an independently generated, frozen uuid8 | **holds** — §`action_binding_and_uuids`. |
| Every tree has 1–3 prerequisite problems, ≥ max(n−1,1) `value_input` edges, ≥ 1 `owner=user` write, no cycle | **holds** — task 0: n=2, 1 `value_input`, `declare_supplier_compensation_6de86425`; task 1: n=2, 2 `value_input`, `file_cancellation_claim_621a2df1`. |
| The difficulty's `prerequisite` edges together remain a DAG, with no cycle from cross-task references | **holds** — two disjoint acyclic components, no cross-component edge. |
| Every computation declares a self-sufficient baseline giving a definite number different from gold | **holds** — 4.74 / −450.00 / 810.00 (task 0) and 17,900.00 / −419.83 / 12,484.88 (task 1), each recomputed independently by the auditor. |
| 4–6 factors per computation, ≥2 `parameter` and ≥1 `method`; ≥1 multi-source and ≥1 cross-difficulty per task | **holds** — §`factor_ladders`, and the cross-difficulty rows are seeded in both worlds (`club` + `air` for task 0, `bundle` for task 1). |
| Every ladder ≥3 tiers stated in full in its rule | **holds as prose**, **fails as implemented** on two ladders — F-A and F-B: the stated tier and the implemented tier select different rows. |
| Every ladder's tiers distinct in outcome, its conditions and outcomes ones the line of business actually holds | **fails** — F-D (a conjunct true of every customer who reaches the write); O-10 (a ladder collapsing to one value on four of seven plans, not exercised by either task). |
| Every factor proved to bear weight against an honest baseline | **holds** — 13 factors on task 0 and 14 on task 1, each moved by substituting its own baseline, every baseline traced to a `baseline.rule` sentence present in the policy's `rule`. |
| Instantiation-stage gates re-run on the final form | **done** — all seven re-run by the auditor at reveal time on unchanged artifacts (`care.extended.yaml` `1260bf70075f429a`, `task_tools.py` `9fdcb64bfc3a9f88`): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK. **All seven stay green over every finding above**, which is the expected result: the scripts prove structure, references and parsability, and cannot prove that a `rule` and its `compute` say the same thing, that an inherited base sentence does not forbid a gold write, or that a tier condition divides anyone. |

### Source-layer verdict

| relationship | task 0 | task 1 |
| --- | --- | --- |
| Policy self-consistency | PASS | **`SOURCE-POLICY RED`** (T1-1 / F-A, T1-2 / F-B, T1-3 / F-C) |
| Problem tree holds | PASS | PASS |
| Factors bear weight | **`SOURCE-FACTOR RED`** (T0-1 / F-D) | PASS |
| Unique solution | PASS | **`SOURCE-TASK RED`** (T1-1, T1-2, T1-3) |

**`travel_protection_desk` does not pass the source-layer audit.** Four red lights stand: three charter-level defects whose consequence is demonstrated on task 1's world (F-A, F-B, F-C) and one charter-level factor defect demonstrated on task 0's world (F-D). Eleven further observations (O-1 … O-11 here, O-12 and O-13 in `1.md`, T0-2 and T0-3 in `0.md`) are recorded without being grounds for rework.

Both tasks' independent derivations reproduced GT exactly — every scored parameter, every owner, every order, every terminal field, every `baseline_result` and every `factor_sensitivity` figure. The red lights are therefore not disagreements about the answer: they are places where the policy surface a solver reads admits a **second** answer that the scored one does not exclude, and one place where a published tier condition tests nothing. None is attributable to a solving agent.

## revision_provenance

Recorded after the reveal, on inspecting the repository rather than the artifacts.

A **prior revision of all three audit files exists in git `HEAD`** (commit `fffc79a`), at the same three paths. Its working-tree copies had been deleted before this audit began — the audit directory did not exist when this auditor first looked — and the files written in this round are new files at those paths, so `git status` reports them as modified rather than added. The old revision is **preserved and recoverable** through `git show HEAD:env/env_0000_online_travel_agency/audits/policy_task/travel_protection_desk/<file>`; nothing of it was read, and no old blind answer was rewritten to accommodate new GT.

**That prior revision audited different artifacts.** All four inputs have changed since `HEAD`:

| artifact | sha256/16 at `HEAD` | sha256/16 audited here |
| --- | --- | --- |
| `care.extended.yaml` | `4e2fa251fbe43224` | `1260bf70075f429a` |
| `task_tools.py` | `5690ed9da66743ce` | `9fdcb64bfc3a9f88` |
| `tasks/0.json` | `ad04f9355bbf7720` | `68282077dd86d4b6` |
| `tasks/1.json` | `9d21f108a5ce6d10` | `1b80f3991cbaf6bc` |

Both shared inputs of the charter-global section moved, and both tasks' own files moved, so the re-derivation rule requires every section — charter-global and per-task alike — to be derived in full rather than carried forward by reference. That is what was done: this round derives everything from the current artifacts and cites nothing from the earlier round. The `Revision: 1` recorded in each file's frozen header should be read as **revision 1 against the artifacts whose hashes that header names**, not as a claim that this difficulty has never been audited before.

---

# revision_2 — re-audit of the reworked charter

## charter_global_frozen (revision 2)

- **Round:** 2. **Freeze time:** 2026-09-17 (UTC), before any reworked proof field was read. **Auditor:** the same independent source-layer auditor that produced revision 1.
- **Revision 1 is untouched above.** Nothing in it has been rewritten, softened or re-scoped to accommodate the rework.

### re_derivation_basis

Hashes verified by the auditor, not taken from the brief:

| artifact | revision 1 | revision 2 | moved? |
| --- | --- | --- | --- |
| `care.extended.yaml` | `1260bf70075f429a` (195,952 B) | `af1adf1f992b18d2` (200,079 B) | **yes, +4,127 B** |
| `task_tools.py` | `9fdcb64bfc3a9f88` | `9fdcb64bfc3a9f88` | no |
| `0.masked.json` | `21c2fb233c58f943` | `21c2fb233c58f943` | no |
| `1.masked.json` | `a5ab17b72c67be54` | `a5ab17b72c67be54` | no |
| `tasks/0.json` | `68282077dd86d4b6` | `ea8ba6c41e22e0d8` | yes (proof fields only) |
| `tasks/1.json` | `1b80f3991cbaf6bc` | `f424019995f30471` | yes (proof fields only) |

One of the charter-global section's two shared inputs moved, so **every charter-global check is re-derived in full** rather than carried forward by reference. The re-derivation rule is satisfied: nothing below is inherited from revision 1 except by explicit comparison.

Independently confirmed before deriving:

- `git diff env/env_0000_online_travel_agency/blueprint/` is empty — **base is untouched**.
- The base section of `care.extended.yaml` is still verbatim identical to `blueprint/products/care.yaml` (compared directly, modulo trailing whitespace).
- For both tasks, `frozen_time`, `user_scenario` and `initial_state` in the live task file are **byte-identical** to the masked view (compared key by key with sorted JSON). The worlds genuinely stand still; only the proof fields moved.

### contamination_disclosure (revision 2)

**Round 2 is not blind in the sense round 1 was, and this is unavoidable in any re-audit.** This auditor already knows every round-1 gold figure, because revision 1 revealed and recorded them. The round-2 re-derivation below was therefore run knowing what the values were in round 1, and one of its explicit purposes was to test the reworker's claim that they are unchanged. What has *not* happened: no reworked `evaluation_criteria`, `computations`, `prerequisite_closure`, `charter_scope`, `solvability_contract` or `design_rationale` was read before this section was written to disk, and the reworker's own figures and reasoning were withheld from the brief and were never sought. Every number below was recomputed by the auditor from the reworked charter and the unchanged seeds, by evaluating each `compute` chain against `build_env` from `check_compute.py`. Round-1 figures are used only as the comparison target, never as an input to a chain.

### policy_conflict_scan (revision 2)

Six extended policies, unchanged in identity, subject, `computes`, `target_tool` and `trigger`. The `(target_tool, computes)` table of revision 1 still holds exactly. Cross-category read declarations unchanged: `club` for the loading charge, `air` for the supplier recovery, `bundle` for the three package-linked policies, none for the settlement. Every `CPARAM`/`CFIELD`/`XSUM`/`XCOUNT`/`XLATEST` call still names a declared category and no other; nothing reads `stay`, `drive` or `biz`.

Scope exclusivity and completeness unchanged: the same two disjoint components, the same six policies covered, no cross-component edge, no cycle.

**`overwrite` counts, revision 1 → revision 2:** loading charge 2 → 2, supplier recovery 2 → 2, settlement 2 → 2, **declared-cost restatement 1 → 3**, re-rating 1 → 1, claim intake 1 → 1. The only declaration that moved is the one revision 1 named in **F-C**.

### rule_compute_equivalence (revision 2)

Re-run mechanically over all six policies. Every binding of every `compute` block has a `compute_basis` entry; every `compute_basis` quotation is a **verbatim substring of its own policy's `rule`**; no `compute_basis` entry refers to a binding that does not exist; every `factors[].ladder` tier beyond the fall-through is a verbatim substring of its own rule; every `decides` target is a real binding and none is `result`; every factor's `bindings` list names only real bindings; no binding is shared between two factors of one policy; every factor's last tier is its fall-through; and every sentence of every `baseline.rule` is a verbatim substring of its policy's `rule`. **All pass, with one exception carried over from revision 1 and recorded as a new observation, O-14.**

Rounding and interval conventions are unchanged: one `RND(x, 2)` at `result` in each policy, `DAYS` with explicit `+ 1` wherever the rule says "both days counted", `MX(0.0, …)` floors each carried by a "never falls below nothing" sentence.

**The two round-1 rule/compute gaps are closed, and closed on the rule side.** Set out under `findings (revision 2)` below.

### action_binding_and_uuids (revision 2)

`task_tools.py` is byte-identical to revision 1 (`9fdcb64bfc3a9f88`), so the six tool contracts, the six function bodies and the six uuid8s stand exactly as revision 1 found them: `6e26c317`, `6de86425`, `411249ab`, `4b2fbffa`, `56692b3c`, `621a2df1` — distinct, unreused, not batch-derived, each frozen with its tool; no docstring names another tool or orders its call against another problem; no function body contains a conditional, a raise, a cross-table read or a hint. Each `(target_tool, computes)` pair is still claimed by exactly one policy. **PASS, unchanged.**

### prerequisite_graph and prerequisite_sentences (revision 2)

Re-derived in full from the reworked charter. The graph is **identical to revision 1** — the same five edges, with the same `problem`, `kind`, `gate`, `form`, `condition` and `resolved_by` on each, no `fallback_reason` anywhere because no edge is in the action form, and every `policy_source` still located character-for-character in the **blocked** policy's own `rule`. Acyclic; two components; the same topological orders.

The four-point test on each of the five sentences gives the same result as revision 1, and the single-write derivations are unaffected: `declare_supplier_compensation_6de86425` is still the only write creating `care_claim_recovery`; `charge_destination_loading_6e26c317` the only one creating `charge_category="destination_loading"`; `restate_declared_trip_cost_4b2fbffa` the only write touching `care_policies.trip_cost_usd`; `raise_rating_adjustment_56692b3c` the only one creating `charge_category="premium_adjustment"`. No depended-on rule restates a blocked rule's sentence. **PASS, unchanged.**

**No new cross-problem order was introduced.** Every ordering connective in all six reworked rules was located and classified: five ground the five declared edges, and every other occurrence is within-computation date or day-count language ("counted from the first day of the journey to its last day", "rounded … only once the discount has been taken off", "the tier held took effect on or before the day the certificate was issued", "redeemed after the last day of the journey insured"). None states an order between two problems. No rule names a tool, a policy id or any snake_case token.

### override_declarations (revision 2)

Re-run sentence by sentence against every `base_policy_refs` entry of all six policies, against the untouched base.

The three new `overwrite` entries are all on `care_ext_declared_cost_restatement`, and they name precisely the two base sentences revision 1 found inherited undeclared:

> superseded: *"No amendment is accepted once the journey has begun or once a claim has been filed, because the risk is then no longer uncertain."*
> replaced by: *"A correction the underwriting desk has approved is carried onto the certificate whenever it is found, whether or not the journey insured has begun or ended, because it restates what the journey actually carried rather than altering the risk the certificate covers."*

> superseded: *"A declared particular of the risk may be corrected while the policy stands, and the premium follows the correction from the day it takes effect."*
> replaced by: *"The correction is made on a certificate standing in any state other than cancelled, the expired state included, because an expired certificate still answers for the journey it insured."*

Both replacement sentences are the **first two sentences of the extended `rule`**, so a solver reading the policy meets them before anything else. The merged semantics are unique in each case: base forbids, extended permits, and the declaration says which sentence is displaced.

Every base sentence not hit by an `overwrite` was reached a conclusion on again. The `upgrade_approved` eligibility on `care_insured_amend` is still inherited unchanged and still bites only on upgrades, not on this correction. The remaining `care_policy_amendment` sentences (the plan's upgrade permission and window, the re-rating on adding a traveller) are inherited without conflict. `care_free_look`, `care_midterm_cancellation`, `care_coverage_term`, `care_claim_assessment`, `care_underwriting` and `care_agg_multi_holding` are still cited by no extended policy and govern no write this suite makes. Observations **O-6**, **O-7**, **O-8** stand as recorded in revision 1; **O-9** is closed.

**One consequence of the new override needs stating, and it is not a defect.** The replacement drops the *"or once a claim has been filed"* limb along with the journey limb, so a correction is now permitted after a claim is filed. Revision 1 noted that the author had leaned on that limb to argue the write order. The order does not depend on it: `care_ext_cancellation_claim_intake`'s own prerequisite sentence — *"The amount claimed is worked out only once the certificate carries the declared trip cost the journey insured actually carried"* — still forces the restatement before the filing, and the `value_input` edge still makes the two orders score differently. The topological order is unchanged and still unique.

### factor_ladders (revision 2)

**27 factors, unchanged in count and distribution:**

| policy | factors | `parameter` | `method` | `cross_difficulty` |
| --- | --- | --- | --- | --- |
| `care_ext_outstanding_loading_charge` | 4 | 3 | 1 | `protection_discount` → club |
| `care_ext_supplier_recovery_declaration` | 4 | 2 | 2 | 2 → air |
| `care_ext_settled_benefit_payment` | 5 | 2 | 3 | none |
| `care_ext_declared_cost_restatement` | 4 | 3 | 1 | 3 → bundle |
| `care_ext_reration_difference` | 6 | 2 | 4 | 2 → bundle |
| `care_ext_cancellation_claim_intake` | 4 | 3 | 1 | 4 → bundle |

Every policy still declares 4–6 factors with at least 2 `parameter` and 1 `method`; every ladder still carries exactly three tiers, the fall-through counted, stated in full in its own rule and implemented in `compute`; every `decides` is an input; every binding set is disjoint within its policy; every label is still honest. **PASS.**

**The one tautological tier condition revision 1 found is gone** (finding F-D). `claim_insured_seq` has been removed from `care_ext_settled_benefit_payment` altogether — it is no longer a binding, no longer in any `bindings` list, and no longer has a `compute_basis` entry. `benefit_limit_basis` tier 1 now reads:

> *"Where the benefit allowed is one the plan states as an amount for each insured traveller and **the certificate names more than one insured traveller**, the limit the benefit claimed carries is the plan's amount for that benefit"*

implemented as `stated_limit if (claim_type_paid != 'trip_cancellation' and F('insured_count') > 1) else …`. The new conjunct is contingent: a certificate naming a single insured traveller is an ordinary case and fails it. It therefore divides customers, which the old one could not. A weaker residual is recorded as **O-15**.

**`stated_limit` now enumerates every benefit the tool contracts admit** (finding O-9): `baggage_loss`, `baggage_delay`, `travel_delay`, `missed_connection`, `medical_emergency`, `dental_emergency`, `evacuation`, `rental_damage`, then `trip_interruption` and `cancel_for_any_reason` as shares of the declared trip cost, with `trip_cancellation` as the final share. That is all eleven `claim_type` values of `settle_benefit_payment_411249ab`, with no silent fall-back to the baggage-delay limit. The dropped branch is closed.

**O-10 stands unchanged** and is still not exercised by either task: `deductible_called_for_rate`'s three tiers still select `P('medical_deductible_usd')`, `P('deductible_per_claim_usd')` and 0, which collapse to a single value on TripGuard Premier, Cancel For Any Reason Elite and Annual Multi-Trip Executive. Task 0 remains on TripGuard Plus, where they are 100.00 / 50.00 / 0.

### numeric regression (revision 2, frozen)

Every scored value, every whole-baseline fall-back and every per-factor baseline substitution was recomputed from the reworked charter on the unchanged worlds, and compared against the figures revision 1 recorded.

- **6 scored values: all identical.** 80.97 / −510.00 / 1,410.00 (task 0, with `deductible_applied` still 30.00); 18,436.50 / 127.59 / 5,144.85 (task 1).
- **6 whole-baseline fall-backs: all identical.** 4.74 / −450.00 / 810.00; 17,900.00 / −419.83 / 12,484.88.
- **27 per-factor baseline substitutions: all identical**, factor by factor, to the figures in `0.md` and `1.md`.

**Mismatches: 0.** The reworker's claim that the rework is value-preserving is independently confirmed. Every factor therefore still bears weight against its baseline by exactly the margins revision 1 demonstrated, and every baseline still gives a definite number different from gold.

## findings (revision 2)

### Round-1 findings, verified item by item

| item | revision-1 verdict | revision-2 status | how it was closed, and where verified |
| --- | --- | --- | --- |
| **F-A / T1-1** | `SOURCE-POLICY` → `SOURCE-TASK` | **CLOSED** | Both tier sentences now say *"a line posted **under its routine terms**"*, and a new sentence excludes the two offending rows by name: *"A line the operator raised on account of a price guarantee, or on account of the journey being given up, is not a line posted under the package's routine terms, and the day such a line posted never anchors the apportionment."* `1.md` §`F-A verified closed on this world`. |
| **F-B / T1-2** | `SOURCE-POLICY` → `SOURCE-TASK` | **CLOSED** | The `reason_code='price_guarantee'` filter is gone; `operator_returns` is now `(returns_to_traveller + credits_given_back) - returns_on_surrender`, each binding carrying a rule sentence, with the exclusion stated and reasoned. `1.md` §`F-B verified closed on this world`. |
| **F-C / T1-3** | `SOURCE-POLICY` | **CLOSED** | Two new `overwrite` entries name the two inherited base sentences; the replacement sentences open the extended rule and expressly admit the expired state. The `design_rationale` card that had asserted *"the journey never began"* now states the lifecycle fact correctly. `1.md` §`F-C verified closed on this world` and §`source_gt_comparison (revision 2)`. |
| **F-D / T0-1** | `SOURCE-FACTOR` | **CLOSED** | `claim_insured_seq` removed from the charter; tier 1's conjunct is now *"the certificate names more than one insured traveller"* (`F('insured_count') > 1`), which a single-traveller certificate fails. `0.md` §`F-D verified closed on this world`. |
| **O-1** | observation | **CLOSED** | `claim_document_ref`'s `claim_type='travel_delay'` filter removed; rule reworded to *"the certificate's claim record names the evidence that supports the claim"*. |
| **O-2** | observation | **CLOSED** | Rule reworded to *"the supplier's return was raised on the supplier's own disruption"*, which is what the compute tests. |
| **O-3** | observation | **CLOSED** | Rule reworded to *"the certificate has settled a payment in this policy term"*, matching `COUNT(care_claim_payout)`. |
| **O-9** | observation | **CLOSED** | `stated_limit` now enumerates all eleven `claim_type` values, with no silent fall-back to the baggage-delay limit. |
| **O-12** | observation | **CLOSED** | Rule now fixes both tool arguments: *"The difference is raised against the base premium line of the certificate, the line the declared trip cost rates, and is raised on the certificate as a whole rather than on any one insured traveller."* |
| **O-4 – O-8, O-10, O-11, O-13, T0-2, T0-3** | observations | **stand, unchanged** | Left as recorded, as the reworker declared. None was made worse; each was re-checked against the reworked charter. |

**Method note.** Every "closed" above was verified against the artifacts, not against the reworker's account, whose figures and reasoning were withheld from the brief and never sought. For the two unique-solution findings the test applied was the one that made them red lights: not "is the compute now documented" but **"is the alternative reading now excluded by a sentence a solver actually reads"**. In both cases it is, and in both cases the repair was made on the rule side — F-A by stating the domain and naming the excluded rows, F-B by removing the filter altogether and letting the reader derive the figure by subtraction.

### Nothing regressed

Independently recomputed or re-derived, never inherited:

- **All 6 scored values, all 6 whole-baseline fall-backs and all 27 per-factor baseline substitutions are identical to revision 1** (§`numeric regression (revision 2, frozen)`; 0 mismatches).
- The **prerequisite graph is byte-identical** — same five edges, kinds, gates, forms, conditions, `resolved_by`, every `policy_source` still verbatim in the blocked rule, still acyclic, still two disjoint components matching the two task scopes.
- **`task_tools.py` is byte-identical**, so the six contracts, six bodies and six uuid8s stand as revision 1 found them; no tool body judges a prerequisite.
- The **base section is still verbatim** and `blueprint/` is untouched.
- Both **task worlds are byte-identical** to the masked views, so both personas, both seeds and every near-miss stand as revision 1 recorded them.
- **Factor structure is unchanged**: 27 factors, the same per-policy counts and labels, every ladder three tiers, every tier stated in its rule, every baseline sentence in its rule, every binding set disjoint, no `decides: result`.
- **No new cross-problem order, tool name, policy id or snake_case token** entered any rule.
- All seven instantiation-stage gates re-run by the auditor on the final form: EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK.

### New observations (revision 2)

None is a red light; none is grounds for rework.

- **O-14 — `supplier_paid` has no `compute_basis` entry.** In `care_ext_supplier_recovery_declaration`, `supplier_paid = ABS(scoped_returns)` is the one binding in the whole charter with no basis quotation. **Pre-existing, not a regression** — it was equally true in revision 1 and this auditor did not catch it then; it is recorded now for completeness. No consequence: the rule speaks of *"the amount the supplier **has paid**"*, a positive quantity, and the ledger sums are negative, so the absolute value is the rule's own sign convention rather than an invented basis.
- **O-15 — `benefit_limit_basis` tier 1 and its fall-through coincide numerically for a single-traveller certificate.** For a per-traveller benefit, tier 1 gives the plan's amount and the fall-through gives that amount times `insured_count`; where `insured_count` is 1 the fall-through gives the same figure, and where it exceeds 1 tier 1 is the branch taken. So the limit for a per-traveller benefit is the plan's per-traveller amount in every reachable world, and the tier distinction changes which branch is taken without ever changing the limit. This is **not** revision 1's finding, which was that a stated conjunct could not be false; the new conjunct can be false and does divide. No consequence is demonstrable: the fall-through is the factor's baseline, substituting it on task 0 still moves the scored value from 1,410.00 to 1,590.00, and no reachable world shows two tiers returning one figure. Recorded so a later round can decide whether the fall-through — a per-traveller limit multiplied by the party size, as the limit on one traveller's claim — is what this line of business publishes.
- **O-16 — a stale ordering justification** in `tasks/1.json` `design_rationale`. Set out in `1.md` §`findings (revision 2)`.
- **O-17 — a narrative factor card left describing the pre-rework ladder** in `tasks/0.json` `design_rationale`. Set out in `0.md` §`findings (revision 2)`.

## closing_checklist (revision 2)

Revision 1's `## closing_checklist` recorded that this difficulty was **not** closed out. It now is. That section is left standing above as written; this one supersedes it.

| Step 4 item | status |
| --- | --- |
| Per-task audit files correspond one-to-one with the tasks; `_difficulty.md` alongside them; old revisions traceable | **holds** — `0.md`, `1.md`, `_difficulty.md`; revision 1 preserved verbatim above, revision 2 appended below it; the pre-round-1 revision remains recoverable at `git show fffc79a:…`. |
| Every comparison section carries a PASS | **holds** — `0.md` §`source_gt_comparison (revision 2)` and `1.md` §`source_gt_comparison (revision 2)` both PASS on all four relationships. |
| Extended policies fully covered; M task scopes pairwise disjoint over the whole problem tree | **holds** — six policies, two disjoint components, unchanged. |
| Task tools and GT closed; each tool an independently generated, frozen uuid8 | **holds** — module byte-identical to revision 1. |
| Every tree has 1–3 prerequisite problems, ≥ max(n−1,1) `value_input` edges, ≥1 `owner=user` write, no cycle; the difficulty's edges remain a DAG | **holds** — task 0: n=2, 1 `value_input`, `declare_supplier_compensation_6de86425`; task 1: n=2, 2 `value_input`, `file_cancellation_claim_621a2df1`; no cross-component edge. |
| Every computation declares a self-sufficient baseline giving a definite number different from gold | **holds** — 4.74 / −450.00 / 810.00 and 17,900.00 / −419.83 / 12,484.88, recomputed. |
| 4–6 factors per computation, ≥2 `parameter`, ≥1 `method`; ≥1 multi-source and ≥1 cross-difficulty per task, on seeded rows | **holds** — 27 factors; `club` + `air` for task 0, `bundle` for task 1, all seeded. |
| Every ladder ≥3 tiers stated in full in its rule, and implemented as stated | **holds** — this is what F-A and F-B fixed; verified mechanically over all 27 ladders. |
| Every ladder's tiers distinct in outcome; conditions and outcomes ones the line of business actually holds | **holds for every exercised ladder.** O-10 (a ladder collapsing on four of seven plans) and O-15 (a fall-through that coincides at `insured_count` 1) remain open observations, neither exercised in a way that demonstrates a consequence. |
| Every factor proved to bear weight against an honest baseline | **holds** — 13 on task 0, 14 on task 1, by the same margins as revision 1. |
| Instantiation-stage gates re-run on the final form | **done by the auditor** — all seven OK on `af1adf1f992b18d2` / `9fdcb64bfc3a9f88`. |

### Source-layer verdict (revision 2)

| relationship | task 0 | task 1 |
| --- | --- | --- |
| Policy self-consistency | PASS | **PASS** (was `SOURCE-POLICY RED`) |
| Problem tree holds | PASS | PASS |
| Factors bear weight | **PASS** (was `SOURCE-FACTOR RED`) | PASS |
| Unique solution | PASS | **PASS** (was `SOURCE-TASK RED`) |

**`travel_protection_desk` PASSES the source-layer audit.** All four round-1 red lights are closed at their root rather than renamed, five round-1 observations are closed as well, no round-1 PASS regressed, every scored value and every baseline is unchanged, and the four new observations recorded above carry no demonstrable consequence. The difficulty is closed out.
