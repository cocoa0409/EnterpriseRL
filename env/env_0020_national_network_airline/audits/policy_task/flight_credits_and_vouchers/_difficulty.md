# Policy-task audit — flight_credits_and_vouchers / charter-global

## charter_global_frozen

- Auditor: independent erl-task-policy-audit agent (Claude Opus 5.5). I did not write any of the audited artifacts.
- Frozen: 2026-09-24T17:11Z. This section was written before any task's GT was revealed and contains nothing derived from a revealed GT.
- Input hashes (sha256):
  - `env/env_0020_national_network_airline/tasks/flight_credits_and_vouchers/credit.extended.yaml` = `4937630c57c1863d75dbfebe6dcd5387b504c7d714aeca0d56df9584a241b3a3` (re-hashed by me; matches the brief)
  - `env/env_0020_national_network_airline/tasks/flight_credits_and_vouchers/task_tools.py` = `da1745144706dbfec09acddfe9afe73c2daf7de275efdb2850e3c737aae6c1ab` (re-hashed; matches)
  - masked views `task_0.masked.json` = `f4c35c9c…14fa`, `task_1.masked.json` = `7b627524…975e` (re-hashed; match)
- Fields I used: the blueprint (`blueprint.yaml`, `share_tools.py`, `products/credit.yaml`; `products/loyalty.yaml` only for the variant parameters `qualifying_dollars_threshold` and `credit_service_fees_waived` and for the loyalty event/trigger definitions), the extended charter, `task_tools.py`, and the masked views (`task_index`, `frozen_time`, `user_scenario`, `initial_state`). For the meaning of the restricted compute primitives (MONTHS, DAYS, `within_months`, CFIELD first-row, RND) I read the primitive definitions in `skills/erl-task-instantiate/scripts/check_compute.py` (lines 224–395). That code holds no task value.
- Fields masked and not read: all of `evaluation_criteria`, `computations`, `charter_scope`, `required_documents`, `design_rationale`, `solvability_contract`, `prerequisite_closure`, `db_closure*`; `tasks/*/tasks/*.json`; the difficulty `worklog.md`; the scenario `worklog.md`; the shared authoring scratchpad.
- Entry conditions (Step 0): the brief includes the gate snapshot with actual output lines (EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK; traceability is deferred to the render stage by design) and the masked views with their hashes. Input is complete.

### policy_conflict_scan

**Base copy.** I loaded both files with YAML. Every top-level key of `blueprint/products/credit.yaml` (category, display_name, binding, lifecycle, accounts, parameter_schema, variants, events, measures, policies) is identical to the same key in the extended file, and lines 1–1724 of the extended file diff clean against the product file. The only addition is `extended_policies`. The base copy is verbatim.

**Extended policies (5) and their subjects:**

| policy | subject | computes | target_tool | owner | prerequisite |
|---|---|---|---|---|---|
| credit_ext_reinstated_validity | credit_reinstate | validity_months | reinstate_credit_8e2d0d7d | agent | [] |
| credit_ext_reinstatement_fee | credit_service_fee | fee_amount | pay_credit_reinstatement_fee_177d2025 | user | ← credit_ext_reinstated_validity (value_input, state form) |
| credit_ext_telephone_fee | credit_service_fee | fee_amount | charge_credit_phone_fee_f43f310b | agent | [] |
| credit_ext_extension_fee | credit_service_fee | fee_amount | pay_credit_extension_fee_5a6cc7fd | user | ← credit_ext_telephone_fee (value_input, state form) |
| credit_ext_extension_term | credit_extend | extension_months | extend_credit_f94665bb | agent | ← credit_ext_extension_fee (state_gate, state form) |

**Overlapping subjects.** Three extended policies share `credit_service_fee`. Each writes a different `fee_type` (reinstatement_fee / phone_redemption_fee / extension_fee) through a different tool, so their conclusions never land on the same entry. The base policies that also carry `credit_service_fee` (credit_redemption_rules, credit_extension, credit_reinstatement) have each had their fee-amount sentence superseded by the matching extended policy (see override_declarations).

- **Triggers and time anchors.** Reinstatement uses the base 90/30-day window counted from the day after expiry. Extension uses the base window that opens 60 days before `expiry_date`. Neither extended policy changes a window. Lateness (reinstated validity) and closeness (extension term) are measured from `expiry_date as recorded on the credit`, the same anchor the base windows use.
- **Terminal states.** Reinstatement leaves the credit active with a new expiry and one restore entry. The fee policies each add one ledger entry. The extension moves the expiry and increments the count. No two policies write the same field to different values.
- **Cross-category reads.** Every extended policy reads only loyalty (tier, qualifying dollars, enrolment, activity), ticket (source-ticket brand and route type, disruptions) and companion (active holdings). All three are categories that some difficulty in `blueprint.yaml` claims. None of these reads writes anything.
- **Waivers.** Each fee policy repeats the base waiver (`credit_service_fees_waived`). The telephone policy also repeats `online_redemption_permitted = false`. Both match the base.

**Scope exclusivity and completeness (from the charter and the two worlds, before any reveal).** My blind derivations produce two trees:
- task 0: {credit_ext_reinstatement_fee ← credit_ext_reinstated_validity}
- task 1: {credit_ext_extension_term ← credit_ext_extension_fee ← credit_ext_telephone_fee}

The two scopes are disjoint and together cover all five extended policies. The `charter_scope` field itself stays masked until the reveal, and the comparison is in each task file.

No conflict found.

### rule_compute_equivalence

I checked check 2 for each policy, binding by binding, and every binding carries a verbatim `compute_basis` quotation from its own rule. Points of note:

- **credit_ext_reinstated_validity.**
  - The ladders for standing, write-off, tenure, prior use and lateness are each stated in full in the rule and implemented branch for branch.
  - "halved and rounded up" is `(s+1)//2` and "three quarters … rounded down" is `(s*3)//4`. Both are exact for integer sums.
  - The rule's order (sum → lateness → cap) matches compute.
  - "whole calendar months" matches the MONTHS primitive.
  - `CPARAM('loyalty','qualifying_dollars_threshold')` reads the holder's own tier threshold. The rule compares a Gold member with the Gold threshold and a Silver member with the Silver threshold, so the two are equivalent.
- **credit_ext_reinstatement_fee.**
  - Basis ladder, five rates, multiplication order and a single cent rounding are all stated and implemented.
  - The waiver is `0.0 if rf_fee_waived`.
- **credit_ext_telephone_fee.**
  - Basis, four rates, rounding and the waiver (including `online_redemption_permitted`) are stated and implemented.
  - `tp_ticket_number` = LATEST call-center redemption. The rule says "worked out from that redemption, the latest call-center redemption on the credit".
- **credit_ext_extension_fee.**
  - The remaining-value definition is spelled out entry type by entry type and implemented as exactly those seven SUMs.
  - Basis, four rates and rounding are stated and implemented.
- **credit_ext_extension_term.**
  - Four additive ladders and the closeness method are stated and implemented.
  - "no more than 15 days remain" is `<= 15`, and "more than 15 but no more than 30" is `<= 30` after the first test.

Invented bases I found in compute, none of which is triggered by either task world (they are recorded as findings G-2 and G-3 below):
- (a) The cardmember rate (reinstatement fee and extension fee) uses `CFIELD('companion', …, status='active')`, which returns the **first** active companion row. The rule decides by **existence** ("holding an active … Pass …"; "holding no active companion pass but an active companion certificate …").
- (b) The telephone rule states two things: the fee is owed for "each call-center redemption that has no linked telephone fee entry", and it is "worked out from that redemption, the latest call-center redemption on the credit". This presupposes that the owing redemption is the latest one. Compute takes the latest call-center redemption without checking whether it is already linked.

### action_binding_and_uuids

- **Claims.** Each `(target_tool, computes)` pair is claimed by exactly one policy: (reinstate_credit_8e2d0d7d, validity_months), (pay_credit_reinstatement_fee_177d2025, fee_amount), (charge_credit_phone_fee_f43f310b, fee_amount), (pay_credit_extension_fee_5a6cc7fd, fee_amount), (extend_credit_f94665bb, extension_months). The three `fee_amount` claims go to three different tools.
- **UUIDs.** The five uuid8s are `8e2d0d7d`, `177d2025`, `f43f310b`, `5a6cc7fd`, `f94665bb`. They share no prefix, no suffix and no sequence, and none is reused. Nothing suggests they were batch-derived. (`177d2025` ends in digits that read like a year. I record this only as an observation. It proves nothing.)
- **Docstrings.**
  - No docstring names another tool or places its action in a sequence.
  - The only temporal words are internal to one call: "The customer then sees the credit …" in reinstate, and "previous_expiry_date (the expiry date before the call …)" in extend. Neither orders one tool against another.
  - Each docstring admits one business reading, and no docstring adds a confirmation, review or wait.
- **Tool bodies.** All five do an unconditional find → create/update, with no status, window, amount or prerequisite check. The module docstring states this.
- **Owners.** `pay_credit_reinstatement_fee` and `pay_credit_extension_fee` are `owner="user"`. The other three are `owner="agent"`.

### prerequisite_graph

- Every extended policy has `prerequisite` filled in. Two are `[]`. The three edges are listed in the policy_conflict_scan table.
- Every `problem` points at an extended policy in this file. None points at itself or at a base policy.
- The graph is two disjoint chains: validity → reinstatement fee, and telephone fee → extension fee → extension term. It is acyclic.
- **Edge credit_ext_reinstated_validity → credit_ext_reinstatement_fee.**
  - `policy_source` "The reinstatement fee is fixed only after the credit carries the restore entry that brings back the value written off at its expiry." is quoted verbatim from that policy's rule.
  - `form: state` and there is no `fallback_reason`, which is correct.
  - `kind: value_input` with `gate: rf_restored_value`, a binding that exists in its compute.
  - `resolved_by: reinstate_credit_8e2d0d7d` is the target_tool of the depended-on policy, and that tool books the `credit_reinstatement_restore` entry, which moves `rf_restored_value` off zero.
  - The `condition` adds "and the credit's status is active". The base rule already implies this ("A restore entry is booked only on a credit whose status is active"), so it is not a real strengthening.
- **Edge credit_ext_telephone_fee → credit_ext_extension_fee.**
  - `policy_source` "The extension fee is not worked out until every call-center redemption on the credit that owes a telephone fee carries its own linked telephone fee entry." is quoted verbatim.
  - `form: state`.
  - `kind: value_input` with `gate: xf_recent_fee_entries`, which exists.
  - `resolved_by` is the telephone fee policy's target_tool, and that tool creates a `credit_service_fee` entry that COUNT picks up.
  - The `condition` spells out "owes a telephone fee" exactly as the telephone rule defines it (call-center channel, online redemption permitted, tier not waived). It is neither strengthened nor weakened.
- **Edge credit_ext_extension_fee → credit_ext_extension_term.**
  - `policy_source` "For a credit whose extension fee is not waived, the new expiry date from an extension is recorded only after the credit carries an extension fee entry dated on the day of the extension." is quoted verbatim.
  - `form: state`.
  - `kind: state_gate` with `gate: credit_ledger.fee_type`. The extended policies declare no `eligibility` entries, so the gate names the ledger field that the rule sentence tests rather than an eligibility id (observation G-5).
  - `resolved_by` is the extension fee policy's target_tool.
- No `prerequisite` text is written from the authoring viewpoint ("in this task", "at the opening", "current world").

### prerequisite_sentences

I applied the four-point test to all three sentences:

| edge | ordering connective | waited-on state (record-visible) | tool / policy id / snake_case / row id | strength vs condition |
|---|---|---|---|---|
| reinstatement fee ← validity | "only after" | "the restore entry that brings back the value written off at its expiry" (ledger restore entry; the base rule calls it "one restore entry") | none | same |
| extension fee ← telephone fee | "not … until" | "every call-center redemption … that owes a telephone fee carries its own linked telephone fee entry" (the ledger's redemption_channel and related_entry_id) | none | open set stated open ("every … that owes"), matching the condition |
| extension term ← extension fee | "only after" | "an extension fee entry dated on the day of the extension", scoped "for a credit whose extension fee is not waived" | none | same, including the waiver scope |

- **Exactly one write per waited-on state.** A restore entry is written only by `reinstate_credit_8e2d0d7d`. A telephone fee entry linked to a redemption is written only by `charge_credit_phone_fee_f43f310b`. An extension fee entry is written only by `pay_credit_extension_fee_5a6cc7fd`. No other tool in this difficulty writes those `event_type`/`fee_type` pairs.
- **Reader's derivation (sentence + records + depended-on rule → action), one reading each:**
  - A restore entry is absent while the credit is expired. The base reinstatement rule says reinstatement "restores exactly the value written off at expiry in one restore entry", and the extended validity rule gives that reinstatement its term. The resolving action is therefore to reinstate the credit.
  - A call-center redemption has no linked telephone fee. The telephone rule says such a redemption "is charged a telephone fee as a separate fee entry linked to that redemption". The resolving action is therefore to charge that telephone fee.
  - No extension fee entry is dated today. The extension fee rule says it "is charged to the holder as a separate fee entry on the credit". The resolving action is therefore that the holder pays the extension fee.
- **The rules say nothing else about a dependency.**
  - The depended-on rules (validity, telephone fee, extension fee) do not restate the dependent's sentence.
  - No rule names a tool or another policy id.
  - The only cross-problem orders stated in the extended rules are the three sentences above, and each grounds a declared edge.
- **Base sentences that state a cross-problem order.** credit_reinstatement ("charged … before the credit is reinstated") and credit_extension ("charged … at the time of the extension") are both superseded by declared overwrites (below), so neither grounds or contradicts an edge. No base sentence grounds any edge.
- **Fallbacks.** No action-form edge exists, so there is no `fallback_reason` to test.

### override_declarations

I checked each extended policy sentence by sentence against its `base_policy_refs`:

- **credit_ext_reinstated_validity** (credit_reinstatement, credit_expiry).
  - The following reinstatement sentences are inherited unchanged: eligibility (permitted, count below max), the window (≤ `reinstatement_window_days_after_expiry`, counted from the day after), "restores exactly the value written off … in one restore entry", "increases reinstatement_count by one", "A restore entry is booked only on a credit whose status is active", "cannot be revived … value is lost".
  - "sets the new expiry_date to the reinstatement date plus reinstated_validity_months" is superseded and **declared**.
  - The fee sentence is handled by credit_ext_reinstatement_fee.
  - credit_expiry: all sentences are followed.
- **credit_ext_reinstatement_fee** (credit_redemption_rules, credit_extension, credit_reinstatement).
  - The base sentence "The reinstatement_fee is charged as a separate fee entry before the credit is reinstated" fixes both the amount (the flat `reinstatement_fee`) and the order. It is **declared** as `superseded_clause`.
  - The waiver clause is inherited and restated in the same words.
  - The replacement text states only the new timing. The new amount lives in the extended rule. Because the base sentence that fixed the amount is named, the amount change is covered.
- **credit_ext_telephone_fee** (credit_redemption_rules, credit_extension, credit_reinstatement).
  - "A redemption through the reservations call center carries phone_redemption_fee per ticket, charged as a separate fee entry linked to the redemption" is **declared**.
  - The "unless online_redemption_permitted is false … or … credit_service_fees_waived" clause is inherited and restated.
- **credit_ext_extension_fee** (credit_redemption_rules, credit_extension, credit_reinstatement).
  - "The extension_fee is charged as a separate fee entry at the time of the extension" is **declared**.
  - The waiver is inherited. "A credit fee entry is charged only on a credit whose status is active or expired" is inherited.
- **credit_ext_extension_term** (credit_extension).
  - The first sentence ("may be extended by extension_months") and "new expiry_date is the old expiry_date plus extension_months" are both **declared**.
  - The window sentences, "extension_count increases by one" and "never changes the face value, the traveler_name or the beneficiary_scope" are inherited.

I found none of the disguised forms:
- **Anonymous intermediates.** The telephone and extension-fee remaining-value and basis intermediates are inside declared replacements.
- **0/1 multipliers.** The `0.0 if waived` results reproduce base waivers.
- **Dropped base branches.** Every base waiver branch is kept.

No sentence in any extended rule calls base's output a wrong value.

**No undeclared override.**

### factor_ladders

| policy | factor | effect | decides | tiers (incl. fall-through) | fall-through = baseline | multi-source (non-fall-through tiers over ≥2 distinct records) | cross_difficulty |
|---|---|---|---|---|---|---|---|
| reinstated_validity | member_standing_term | parameter | rt_standing_term | 3 (8 / 7 / std) | yes (`reinstated_validity_months`) | no: tier and QD are fields of the same loyalty_holdings row; the threshold is a charter param | loyalty |
| | written_off_value_months | parameter | rt_writeoff_months | 3 (2 / 1 / 0) | yes | no | — |
| | membership_tenure_months | parameter | rt_tenure_months | 3 (2 / 1 / 0) | yes | no | loyalty |
| | prior_use_months | parameter | rt_prior_use_months | 3 (2 / 1 / 0) | yes | no | — |
| | reinstatement_lateness | method | rt_lateness_adjusted | 3 (ceil ½ / floor ¾ / identity) | yes | no | — |
| reinstatement_fee | reinstatement_fee_basis | method | rf_fee_basis | 3 (30 % of value / min(flat, 35 %) / flat) | yes (`reinstatement_fee`) | no | — |
| | reinstatement_fee_member_rate | parameter | rf_member_rate | 3 (0.70 / 0.85 / 1) | yes | **yes**: loyalty_holdings tier ∧ loyalty_activity flight accruals | loyalty |
| | reinstatement_fee_source_fare_rate | parameter | rf_brand_rate | 3 (0.80 / 0.90 / 1) | yes | no | ticket |
| | reinstatement_fee_history_rate | parameter | rf_fee_history_rate | 3 (0.80 / 0.90 / 1) | yes | no (fee and fee-refund entries, one ledger) | — |
| | reinstatement_fee_disruption_rate | parameter | rf_disruption_rate | 3 (0.75 / 0.90 / 1) | yes | no | ticket |
| | reinstatement_fee_cardmember_rate | parameter | rf_cardmember_rate | 3 (0.80 / 0.90 / 1) | yes | tier 2 is a conjunction (no active pass ∧ active cobrand certificate) over companion rows | companion |
| telephone_fee | telephone_fee_basis | method | tp_fee_basis | 3 (12 % / min(flat, 16 %) / flat) | yes (`phone_redemption_fee`) | no | — |
| | telephone_fee_member_rate | parameter | tp_member_rate | 3 (0.50 / 0.75 / 1) | yes | **yes**: tier ∧ flight accruals | loyalty |
| | telephone_fee_billing_delay_rate | parameter | tp_delay_rate | 3 (0.60 / 0.80 / 1) | yes | no | — |
| | telephone_fee_route_rate | parameter | tp_route_rate | 3 (0.60 / 0.80 / 1) | yes | no | ticket |
| | telephone_fee_card_spend_rate | parameter | tp_card_rate | 3 (0.80 / 0.90 / 1) | yes | no | loyalty |
| extension_fee | extension_fee_basis | method | xf_fee_basis | 3 (40 % / min(flat, 30 %) / flat) | yes (`extension_fee`) | no | — |
| | extension_fee_count_rate | parameter | xf_fee_count_rate | 3 (0.60 / 0.80 / 1) | yes | no | — |
| | extension_fee_member_rate | parameter | xf_member_rate | 3 (0.70 / 0.85 / 1) | yes | no (same row as member_standing_term) | loyalty |
| | extension_fee_source_fare_rate | parameter | xf_brand_rate | 3 (0.70 / 0.85 / 1) | yes | no | ticket |
| | extension_fee_cardmember_rate | parameter | xf_cardmember_rate | 3 (0.80 / 0.90 / 1) | yes | tier 2 as above | companion |
| extension_term | tenured_member_term | parameter | et_tenured_term | 3 (8 / 7 / std) | yes (`extension_months`) | **yes**: loyalty_holdings tier ∧ enrolled_date (the same row, but two conditions of distinct kinds). This is weaker than the accrual-based factors | loyalty |
| | extension_prior_use_months | parameter | et_prior_use_months | 3 (2 / 1 / 0) | yes | no | — |
| | extension_disruption_months | parameter | et_disruption_months | 3 (2 / 1 / 0) | yes | no | ticket |
| | extension_source_route_months | parameter | et_route_months | 3 (2 / 1 / 0) | yes | no | ticket |
| | extension_request_closeness | method | et_closeness_adjusted | 3 (ceil ½ / floor ¾ / identity) | yes | no | — |

- **Counts per policy.** validity 5 (4 parameter / 1 method), reinstatement fee 6 (5/1), telephone fee 5 (4/1), extension fee 5 (4/1), extension term 5 (4/1). All are within 4–6 with at least 2 parameter and at least 1 method.
- **Each factor's bindings and `decides`.** Bindings are pairwise disjoint within each policy, every `decides` is an input rather than `result`, and every declared baseline is the fall-through value.
- **Ladders.** Every ladder has three tiers that are pairwise disjoint as stated. No two tiers of one ladder select the same value or method. Every tier (condition and value/method) is stated in the rule prose and implemented in compute.
- **Method labels.**
  - The three basis factors switch between a percentage of a value, the lesser of the flat fee and a percentage, and the flat fee. These are different algorithms, so the label is honest.
  - The lateness and closeness factors switch between halving with round-up, three-quarters with round-down, and identity. The multiplier and the rounding direction both change. Because the rounding mode changes, I accept the `method` label. It is close to the line (observation G-6).
- **Cross-difficulty categories read:** loyalty, ticket, companion.
- **Realism of conditions and outcomes.**
  - Tier-and-activity discounts, source-brand discounts, controllable-disruption goodwill, cardmember discounts, value-proportional fee bases, and a shorter term for a late reinstatement or a late extension request are all treatments an airline plausibly publishes.
  - Some conditions are unusual but defensible: more redemptions earn more months, more service fees paid earn a lower rate, and a fee booked late is discounted (observation G-7).
  - One outcome is not defensible. It is finding G-1.

### findings

**G-1 — SOURCE-FACTOR RED (unreal ladder: inverted elite treatment in the fall-through). Bears on task 0 (member_standing_term) and task 1 (tenured_member_term).**
- **Symptom.** In two term ladders, the top Summit tiers fall into the fall-through and receive less than the mid tiers.
- **Evidence.**
  - `credit_ext_reinstated_validity.rule`: "The member-standing term of a reinstated credit is gold_standing_term_months for a Summit Gold member whose qualifying dollars this year have reached the qualifying_dollars_threshold of Summit Gold …, silver_standing_term_months for a Summit Silver member whose qualifying dollars this year have reached the qualifying_dollars_threshold of Summit Silver, and the standard reinstated term for every other holder." Here `gold_standing_term_months: 8`, `silver_standing_term_months: 7`, and the standard term is `reinstated_validity_months` (6 for Flight/Trip Credit, 3 for SR eCertificate).
  - `credit_ext_extension_term.rule`: "The tenured-member term of an extension is gold_tenured_term_months for a Summit Gold member … enrolled at least long_tenure_months …, silver_tenured_term_months for a Summit Silver member …, and the standard extension term for every other holder." Here `gold_tenured_term_months: 8`, `silver_tenured_term_months: 7`, and the standard term is `extension_months` (6).
- **Demonstrated consequence (the tier named).**
  - A Summit Platinum member whose qualifying dollars have reached the Platinum threshold (14,000, which is above the Gold threshold of 9,000) gets a reinstated term of 6 where a Gold member gets 8. The same holds for Summit Diamond and the invitation-only Summit Chairman.
  - A 20-year Summit Diamond member extending a credit gets 6 months where a 5-year Gold member gets 8.
  - The loyalty charter ranks these tiers above Gold (for example, `credit_service_fees_waived: true` only for Platinum, Diamond and Chairman). No network airline publishes a credit-validity benefit that gives its top elite tiers strictly less than a mid tier.
  - The fee ladders do not have this defect: their "every other customer" rate of 1 never reaches Platinum and above, because those tiers are waived outright.
- **Root cause.** The fall-through "every other holder" covers both ordinary members and the tiers above Gold.
- **Affected artifact and location.** `credit.extended.yaml` → `credit_ext_reinstated_validity.rule` / `factors[member_standing_term].ladder[2]`; `credit_ext_extension_term.rule` / `factors[tenured_member_term].ladder[2]`.
- **Counts.** Striking the two factors leaves validity with 4 factors (3 parameter / 1 method) and the extension term with 4 (3/1), so the bounds still hold. The RED stands on the ladder-realism test itself. Each task file records what it costs that task.

**G-2 — observation (latent rule/compute non-equivalence, SOURCE-POLICY class). No task world triggers it.**
- **Symptom.** The cardmember rate in `credit_ext_reinstatement_fee` and `credit_ext_extension_fee` can disagree with its rule when a customer holds more than one active companion product.
- **Evidence.**
  - The rule decides by existence: "pass_holder_rate for a customer holding an active Crestline Companion Pass … cobrand_certificate_rate for a customer holding no active companion pass but an active companion certificate issued as the co-branded card anniversary benefit".
  - Compute reads `CFIELD('companion','variant_name', status='active')` and `CFIELD('companion','issue_source', status='active')`, each of which returns the first active row only.
- **Demonstrated consequence (constructed situation).** A customer holds an active cobrand certificate stored before an active Companion Pass Annual. The rule gives 0.80. Compute gives 0.90.
- **Why no task is affected.** Both task worlds seed exactly one companion holding, so neither is affected. It is recorded so that a later world with two companion products does not inherit it silently.

**G-3 — observation (latent, SOURCE-POLICY class). No task world triggers it.**
- **Symptom.** The telephone fee rule and the extension fee prerequisite can come apart when more than one call-center redemption owes a fee.
- **Evidence.**
  - The telephone rule's owed-fee clause ("owed for each call-center redemption that has no linked telephone fee entry") and its computation clause ("worked out from that redemption, the latest call-center redemption on the credit") coincide only when the single owing redemption is the latest one.
  - `tp_ticket_number` takes the LATEST call-center redemption whether or not it is linked.
- **Demonstrated consequence (constructed situation).**
  - If an earlier call-center redemption is unlinked and the latest is already linked, the rule's own two clauses point at different redemptions, and compute prices the already-linked one.
  - With two unlinked redemptions, the extension-fee prerequisite ("every call-center redemption … that owes a telephone fee carries its own linked telephone fee entry") needs two fees, but the telephone policy prices only one.
- **Why no task is affected.** Task 1 has exactly one owing redemption, and it is the latest one.

**G-4 — observation (window convention). Bears on task 1.**
- **Symptom.** "in the last N calendar months" (flight_window_months, card_window_months, disruption_window_months, fee_window_months) is not defined in the charter prose.
- **Readings.** Compute uses a rolling whole-month window anchored at the handling date (`0 <= MONTHS(date, NOW) < N`). A reader could instead read "the last N complete calendar months".
- **Why I prefer the rolling reading.** The charter's own measures define windows as rolling spans ending on the handling date ("Rolling 365 calendar days ending on, and including, …"), and its tenure clauses count "whole calendar months before" the handling date. I therefore judge the rolling reading dominant.
- **Consequence.** Task 1's file shows what the alternative reading would give.

**G-5 — observation.** The `state_gate` edge's `gate` names a ledger field (`credit_ledger.fee_type`), not an eligibility id, because extended policies carry no `eligibility` list. The gating state is fully stated by the rule's prerequisite sentence. No consequence.

**G-6 — observation.** For `reinstatement_lateness` and `extension_request_closeness` (method), the rounding direction changes between tiers as well as the multiplier. I accept this as a change of algorithm, but it is the thinnest method distinction in the charter.

**G-7 — observation (realism, unusual but defensible).**
- Prior-use months reward credits that were redeemed more often (validity and extension term).
- The fee-history rate and the fee-count rate lower a fee because more service fees were paid before.
- The telephone billing-delay rate discounts a fee the airline booked late.

I do not call any of these a treatment no airline would publish.

**G-8 — observation (seed coherence, cross-difficulty rows).**
- **Symptom.** Both worlds seed `loyalty_flight_accrual` rows but none of the `loyalty_mqd_accrual` rows that the loyalty charter triggers from each flight accrual (`products/loyalty.yaml`, `loyalty_flight_accrual.triggers: loyalty:loyalty_mqd_accrual`). `qualifying_dollars_ytd` therefore has no activity rows behind it.
- **Why it is only an observation.** The factors that read qualifying dollars read the holding's running balance. `find_loyalty_holdings` shows it as "qualifying dollars this year", and no rule sentence directs a reader to rebuild it from activity rows. The tier is therefore the same under every reading the rules support. Each task file notes the rows.

## closing_checklist

This section was written after both reveals (first GT read at 2026-09-24T17:14:15Z). The charter-global section above was on disk at 17:12:25Z (pre-reveal sha256 `43506d3a35c24d10d5489b7e79275471e723089ec80cd42509f44fbf5d94f1a3`) and has not changed since. The "Frozen: 17:11Z" stamp in it was my estimate; the file mtime is authoritative.

**Status: NOT CLOSED.** Both tasks are SOURCE-FACTOR RED on G-1, so the difficulty does not pass the source-layer audit.

| item | state |
|---|---|
| Task files match the tasks one to one, and `_difficulty.md` sits beside them | yes: `0.md`, `1.md`. This is the first round, so there are no older revisions |
| Every comparison section carries a PASS | **no**: 0 → SOURCE-FACTOR RED, 1 → SOURCE-FACTOR RED (G-1). The other three relationships PASS in both |
| Extended policies fully covered, and scopes pairwise disjoint | yes. GT `charter_scope`: task 0 {reinstated_validity, reinstatement_fee}, task 1 {telephone_fee, extension_fee, extension_term}. That is 5 of 5 policies, and they are disjoint. The scopes match my blind trees |
| Task tools and GT closed; each uuid8 generated independently | yes (see § action_binding_and_uuids) |
| Trees: 1–3 prerequisite problems, value_input edges ≥ max(n−1, 1), a user-owned write, no cycle | task 0: n = 1, 1 value_input, user fee payment. task 1: n = 2, 1 value_input, user fee payment. The whole-difficulty graph is two disjoint chains and acyclic |
| Computations: self-sufficient baseline, 4–6 factors (≥2 parameter, ≥1 method), per task ≥1 multi-source and ≥1 cross-difficulty, every factor bears weight, baseline differs from gold | Every factor bears weight on its world and every baseline differs from gold (figures in the task files, identical to GT `factor_sensitivity`). **Fails** only on the realism of two ladders (G-1: `member_standing_term`, `tenured_member_term`). With those struck, the counts still meet the bounds |
| Instantiation-stage gates re-run on the final form | not re-run by this auditor. Per the brief, the coordinator runs gates. The snapshot in the brief is all green (traceability deferred to render) |

Open observations to carry to the next round: G-2 and G-3 (latent rule/compute gaps with multiple companion holdings or multiple unlinked call-center redemptions), G-4 (the window convention is undefined; it moves task 1's numbers under the complete-calendar-month reading), G-8 (the seeds omit the triggered mqd accrual rows), and the proof-field "multi-source" labels on same-row conjunctions.

## revision_2

### charter_global_frozen (revision_2)

- Auditor: the same independent audit agent as round 1. I have seen the round-1 GT, so this round checks closure, new defects and regressions. It is not a blind audit.
- Frozen before any round-2 task JSON was read. The file mtime is authoritative for the time.
- Input hashes (sha256, re-computed by me):
  - `credit.extended.yaml` = `3ea100e2cfe877a7b296e94bd681d42e98b94e9861ae33df8367b051521f6fc5`. This **changed** from round 1 (`4937630c…b3a3`), so every charter-global section below is re-derived in full.
  - `task_tools.py` = `da1745144706dbfec09acddfe9afe73c2daf7de275efdb2850e3c737aae6c1ab`. Unchanged; the tool-module half of § action_binding_and_uuids carries forward.
  - Masked views r2 `task_0.masked.json` = `e8fc9835…1728` and `task_1.masked.json` = `638eb812…13e`. Both match the brief.
- Masked fields and leak discipline are as in round 1. I read nothing under `tasks/*/tasks/*.json`, no worklog, and nothing in the shared scratchpad before the freeze.
- Gate snapshot: the brief reports EXTENDED / TASK TOOL CONTRACT / REPLAY / SOLVABILITY / COMPUTE / GROUNDING / SCOPE all OK (rc=0), with traceability deferred. Input is complete.

### What changed in the charter (found by reading the file, not the reworker's list)

- Base section: every top-level key still equals `blueprint/products/credit.yaml`. It is verbatim.
- `credit_ext_reinstated_validity`:
  - The member-standing ladder was rewritten. New params `upper_standing_term_months: 8` and `middle_standing_term_months: 7` replace the gold/silver params.
  - Tier 1 is "a Summit Platinum, Summit Diamond or Summit Chairman member and … a Summit Gold member whose qualifying dollars this year have reached the qualifying_dollars_threshold of Summit Gold".
  - Tier 2 is "any other Summit Gold member and … a Summit Silver member whose qualifying dollars this year have reached the qualifying_dollars_threshold of Summit Silver".
  - The fall-through is the standard term. Compute is updated to match.
- `credit_ext_extension_term`: the tenured-member ladder was rewritten the same way. Tier 1 is Platinum/Diamond/Chairman, or Gold enrolled ≥ 60 months, giving 8. Tier 2 is any other Gold, or Silver enrolled ≥ 60 months, giving 7. The fall-through is `extension_months`.
- `credit_ext_reinstatement_fee` and `credit_ext_extension_fee`:
  - The cardmember compute now uses `EXISTS('companion', variant_name=…Pass Semiannual|Annual, status='active')` and `EXISTS('companion', issue_source='cobrand_card_anniversary', status='active')`. It no longer uses first-row CFIELD.
  - Each gains a window-definition sentence.
- `credit_ext_telephone_fee`:
  - The owed-fee sentence is now "A telephone fee is owed only for the latest call-center redemption on the credit, and only while no telephone fee entry is linked to it; an earlier call-center redemption that was left unbilled when a later call-center redemption was made is no longer owed a telephone fee."
  - Compute adds `tp_redemption_entry` (LATEST call-center redemption id) and `tp_already_billed` (a COUNT of linked phone fees), and `result` is 0.0 when `tp_already_billed > 0`.
  - A window-definition sentence is added.
- `credit_ext_extension_fee.prerequisite[0].condition` now names "the latest credit_redemption entry on the credit with redemption_channel call_center …". Its `policy_source` is unchanged.
- `credit_ext_extension_term` gains a window-definition sentence for the disruption window.
- Window-definition sentence, same form in all four policies that have windows: "A <policy> window of the last so many calendar months holds the entries dated fewer than that many whole calendar months before the date <the quantity> is worked out / booked / the request date, so it rolls back from that date and is not a count of completed calendar months." Every windowed binding cites it in `compute_basis`: `rf_recent_flights`, `rf_recent_disruptions`, `tp_recent_flights`, `tp_card_accruals`, `xf_recent_fee_entries`, `et_recent_disruptions`.

### policy_conflict_scan (revision_2)

- The subjects, target tools, owners and prerequisite edges are the same as round 1.
- The narrowed telephone-fee duty conflicts with no base sentence:
  - The base per-ticket charge sentence is superseded (see override_declarations).
  - credit_fee_refunds is untouched.
  - The extension-fee prerequisite sentence ("every call-center redemption … that owes a telephone fee") is an open set. Under the new telephone rule it contains at most one redemption, and the updated `condition` names exactly that one. Sentence and condition agree.
- The window sentences give one convention to every windowed quantity, which removes G-4's second reading. MONTHS whole-month arithmetic with `0 <= m < N` is exactly "dated fewer than that many whole calendar months before".
- Scope: task 0 {reinstated_validity, reinstatement_fee} and task 1 {telephone_fee, extension_fee, extension_term}. They are disjoint and cover all five policies (re-derived blind below; confirmed against `charter_scope` after the reveal).
- No conflict found.

### rule_compute_equivalence (revision_2)

- Every compute binding of all five policies has a `compute_basis` entry quoted verbatim from its own rule. I checked this mechanically: no binding lacks a basis, and no basis is missing from its rule. The only rule sentences cited by no binding are the baseline, prerequisite, eligibility and tool-effect sentences, the same set as round 1.
- **Member-standing and tenured-member.** The tiers the new compute branches select, in order, are exactly the rule's. `CPARAM('loyalty','qualifying_dollars_threshold')` reads the holder's own tier threshold, so "Gold … Gold threshold" and "Silver … Silver threshold" are implemented faithfully.
- **Cardmember.** The EXISTS form is now an existence test, as the rule states. **G-2 is closed.**
- **Telephone.**
  - `tp_redemption_entry` and `tp_ticket_number` both take the LATEST call-center redemption.
  - `tp_already_billed > 0` gives 0.0, which implements "only while no telephone fee entry is linked to it". An earlier unbilled redemption is no longer priced, matching the new forgiveness clause.
  - **G-3 is closed.** The rule's two clauses now name the same single redemption, and compute prices that one.
  - Residual (new observation N-1 below): if two call-center redemptions share the latest `entry_date`, "the latest" does not decide between them, and LATEST keeps the first row it meets. No task world has such a tie.

### action_binding_and_uuids (revision_2)

- `task_tools.py` is unchanged, so the uuid8 and docstring conclusions carry forward from round 1.
- The `(target_tool, computes)` claims in the new yaml are identical to round 1: one policy per pair.

### prerequisite_graph (revision_2)

- The three edges are unchanged in `problem`, `kind`, `gate`, `form`, `policy_source` and `resolved_by`. Each `policy_source` is still verbatim in its blocked rule. The graph is still two acyclic chains.
- The extension-fee edge's `condition` was edited to "the latest … call_center" redemption. That is exactly what "owes a telephone fee" now means under the telephone rule, so it is neither strengthened nor weakened.
- G-5 (the state_gate names a ledger field) is unchanged and remains an observation.

### prerequisite_sentences (revision_2)

- The three sentences are unchanged and pass the four-point test as in round 1.
- Exactly one write brings each waited-on state about.
- No rule gained a tool name, a policy id, a second wording of a dependency, or a cross-problem order that grounds no edge. The new telephone and window sentences contain no ordering connective between problems.

### override_declarations (revision_2)

- The declared overwrites are the same five clauses as round 1.
- The new telephone forgiveness clause narrows the quantity governed by the base sentence "A redemption through the reservations call center carries phone_redemption_fee per ticket, charged as a separate fee entry linked to the redemption". That sentence is the one named in `superseded_clause`, so the narrowing is declared.
- The base waiver clauses are still inherited and restated.
- No undeclared override.

### factor_ladders (revision_2)

- The factor counts, labels, `decides`, binding disjointness, tier counts and fall-through = baseline are unchanged from round 1 for all 26 factors.
- **G-1 re-test.**
  - `member_standing_term` now selects, per tier: Platinum, Diamond and Chairman (any) and qualifying Gold get 8; other Gold and qualifying Silver get 7; Members and non-qualifying Silver get 6.
  - `tenured_member_term`: Platinum, Diamond and Chairman (any) and tenured Gold get 8; other Gold and tenured Silver get 7; everyone else gets 6.
  - Both are monotone in the loyalty charter's tier order. No tier receives less than a lower tier in the same situation.
  - The three values are distinct and the tiers are pairwise disjoint as stated ("any other Summit Gold member" is the complement of tier 1's Gold clause).
  - Each condition is one an airline weighs: tier, qualification this year, tenure. Each outcome is a treatment an airline would publish.
  - **G-1 is closed.**
- **Other ladders re-checked for the same inversion.** The fee member-rate ladders (reinstatement, telephone, extension) give "1 for every other customer", but that set never includes Platinum and above, because those tiers are waived outright (`credit_service_fees_waived: true`). No inversion.
- **Multi-source.** Unchanged. The tier-and-accrual member rates are genuine multi-source factors. The standing and tenure ladders remain same-row conditions.
- G-6 and G-7 are unchanged and remain observations.

### findings (revision_2)

- **G-1 — CLOSED.** Both term ladders are now monotone (see factor_ladders).
- **G-2 — CLOSED.** The cardmember rate uses existence tests.
- **G-3 — CLOSED.** Only the latest call-center redemption is owed a fee, and compute tests whether it is already linked. The two telephone clauses and the extension-fee prerequisite now agree.
- **G-4 — CLOSED.** An explicit rolling-window sentence is present in each windowed policy and cited by each windowed binding.
- **G-5, G-6, G-7 — unchanged, observations.** This matches the reworker's "accepted, no change".
- **G-8 — to be verified per task.** Both r2 worlds now seed a `loyalty_mqd_accrual` beside every `loyalty_flight_accrual` (same ticket/segment/flight_date). The 2026 sums equal `qualifying_dollars_ytd` exactly: 9,860.00 in task 0 and 5,120.00 in task 1. Closed, subject to each task file.
- **N-1 — new observation (latent, no task world triggers it).** The telephone rule's "the latest call-center redemption on the credit" is undecided when two call-center redemptions share the latest `entry_date`. Compute's LATEST keeps the first row met. This does not arise in either world (task 1's call-center redemptions are dated 2026-06-02 and 2026-09-24).
- **N-2 — new observation (realism, acceptable).** The telephone forgiveness clause ("an earlier call-center redemption that was left unbilled when a later call-center redemption was made is no longer owed a telephone fee") is a business choice: no retroactive billing once a later telephone booking has been priced. I judge it a publishable policy. It is not a factor, so it bears on no ladder test.

### closing_checklist (revision_2)

Written after both round-2 reveals (17:26:59Z). The revision_2 charter-global section above was on disk at 17:26:12Z and has not changed since.

**Status: CLOSED — PASS on the source layer.**

| item | state |
|---|---|
| Task files match the tasks one to one; old revisions kept | yes. Round 1 is untouched and revision_2 is appended in `_difficulty.md`, `0.md` and `1.md` |
| Every comparison section carries a PASS | yes: task 0 PASS, task 1 PASS (revision_2) |
| Extended policies fully covered, scopes pairwise disjoint | yes: 5 of 5, disjoint, matching r2 `charter_scope` |
| Task tools and GT closed; uuid8s independent | yes (the tool module is unchanged since round 1) |
| Trees: 1–3 prerequisites, value_input floor met, a user write, acyclic | task 0: n = 1, 1 value_input, user fee. task 1: n = 2, 1 value_input, user fee. The graph is two disjoint chains |
| Computations: self-sufficient baseline, 4–6 factors (≥2 parameter, ≥1 method), per task multi-source and cross-difficulty, realistic ladders, every factor bears weight, baseline differs from gold | yes. G-1 is closed and every sensitivity figure was re-verified on the r2 worlds |
| Gates re-run on the final form | by the coordinator (brief): all OK, traceability deferred to render. Not re-run by this auditor |

**Reconciliation of the reworker's claims list** (checked against disk, not the list):

| claim | verified state |
|---|---|
| G-1, T0-F1, T1-F1 closed | **closed** |
| G-2 changed | **closed** |
| G-3 changed | **closed** |
| G-4 with T0-O2 and T1-O1 changed | **closed** |
| G-8 with T0-O4 and T1-O4 changed | **closed** |
| T0-O1 changed | **closed** |
| T0-O3 with T1-O3 changed | **closed** |
| G-5, G-6 with T1-O2, and G-7 accepted, no change | **unchanged, as claimed** |

**New in revision_2.** Two observations, N-1 (latent same-date tie for "latest") and N-2 (the forgiveness clause is realistic). Neither is a red light.

**Regressions.** None. Every scored value and sensitivity figure of both tasks equals round 1.
