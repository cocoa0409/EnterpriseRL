# Policy-task audit — condo_coverage_changes / charter-global

## charter_global_frozen

- Round: 1 (no earlier revision exists under `audits/policy_task/condo_coverage_changes/`).
- Freeze time: 2026-09-24T23:25Z. Auditor: independent audit agent (erl-task-policy-audit), not the instantiating agent.
- Frozen inputs, with the hashes I recomputed. They match the brief:
  - `tasks/condo_coverage_changes/condo.extended.yaml` sha256 `28ab82c1b5a7c0565b3c9207eb570fc4082aa6b7fb2fff8a7b0ed94f1509c612`
  - `tasks/condo_coverage_changes/task_tools.py` sha256 `d7bcb18b98dfac6a0d09c1a03cbe2117fc526fea4e80f06f9beb981732bb75b7`
  - Blueprint read: `blueprint.yaml`, `products/condo.yaml`, plus `products/home.yaml` and `products/flood.yaml` (only to check the seeded cross-difficulty holdings against their own charters), `db_schema.json` (the occupancy enums) and `share_tools.py`.
- Fields permitted: the charter (base and extended), the tool contracts and bodies, the blueprint, and the orchestrator's masked views (`frozen_time`, `user_scenario`, `initial_state`).
- Fields masked, and not read before this file and both task derivations were on disk: `evaluation_criteria`, `computations`, `charter_scope`, `required_documents`, `design_rationale`, `solvability_contract`, `prerequisite_closure`, `db_closure`, `db_closure_matches_initial_state`. I did not open the instantiation `worklog.md` or the scenario `worklog.md`. I ran no recursive search over `env/`.
- This section uses the charter, schema and tool contracts only. Nothing in it comes from a revealed GT.

### Entry conditions (Step 0)

- Gate snapshot supplied, 7 instantiation-stage gates, all exit 0: EXTENDED, TASK-TOOL-CONTRACT, REPLAY, SOLVABILITY, COMPUTE, GROUNDING, SCOPE. `check_traceability` is deferred until the KB is published, which is legitimate at this stage.
- Masked views supplied with hashes. I recomputed them: `0.view.json` `93eb4b92…0de0` and `1.view.json` `8072efe1…e28` both match.
- The entry conditions are complete. A green gate only qualifies the difficulty for this manual audit. It proves nothing about correctness.

### policy_conflict_scan

The structured policy consists of the verbatim base section (10 base policies) plus 4 extended policies.

- **Base copy.** I compared lines 1–1238 of the extended file with `blueprint/products/condo.yaml`. The only difference is one trailing blank line, and every top-level key parses equal. The base copy is verbatim.
- **Extended policies.** Each claims one `(target_tool, computes)` pair:
  - `condo_ext_liability_raise_charge` → `raise_liability_limit_70984c5d` (owner agent), `prorated_premium` (additional)
  - `condo_ext_unit_rental_charge` → `add_unit_rental_endorsement_60a857ee` (owner user), `prorated_premium` (additional)
  - `condo_ext_coverage_a_realignment_charge` → `raise_coverage_a_minimum_ec3d8a44` (owner agent), `prorated_premium` (additional)
  - `condo_ext_deductible_raise_credit` → `elect_deductible_raise_c9f31846` (owner user), `prorated_premium` (return)
- **Overlapping subjects.** All four extended policies replace the same base clauses of `condo_endorsements`: the effective-date clause, the annual-change clause and the proration clause. Each replacement is scoped by its own endorsement kind ("A liability raise…", "A unit rental endorsement…", "A Coverage A realignment…", "A deductible raise…"). No two extended policies govern the same endorsement kind, so no two of them compete for one quantity.
- **Triggers.** Every extended policy is `on_request`. The time anchor is uniform: "takes effect on the day the named insured requests it, and that day is before the expiration date".
- **Eligibility inherited from base and not overwritten.** These apply to every extended write:
  - `endorsable_status`: bound, in_force or pending_nonrenewal.
  - `open_claim_freeze`: "Coverage increases are not accepted while the policy has a claim that has been reported and not closed." This applies to the liability raise, the unit rental and the realignment. The deductible raise is not a coverage increase.
  - The umbrella liability floor, which only bites on a lowering and so applies to none of the four.
  - `premium_direction … none below min_premium_change`. The overwrites replace only the clause before the semicolon, so this part is inherited.
- **Terminal states.** Each tool writes one endorsement row, one declarations field (`liability_limit`, `occupancy`, `coverage_a_limit` or `deductible`), one billing row, and a `premium_balance` update. No two tools write the same declarations field.
- **Cross-category read boundaries.** Two policies read home: liability raise reads `[status, liability_limit]`, and unit rental reads `[status, occupancy]`. The realignment reads flood `[status, occupancy, original_effective_date]`. The deductible raise reads nothing outside condo. Each `cross_category` declaration matches the fields its compute actually reads (`EXISTS/CFIELD('home', …)`, `CFIELD('flood', …)`).
- **Scope partition.** The `prerequisite` graph has two connected components:
  - {liability_raise → unit_rental}
  - {coverage_a_realignment → deductible_raise}
  With M=2 and 4 policies, the only partition in which every tree is closed under its prerequisites is one component per task. The claimed scopes (`charter_scope`) are masked in this phase; I compare them per task after the reveal. The SCOPE gate reports disjoint scopes that cover all policies.
- **Result.** I found no conflict among the base and extended policies on subject, trigger, eligibility, time anchor, action parameter, terminal state or cross-category boundary.

### rule_compute_equivalence

Method: I checked mechanically that every `compute_basis` value appears verbatim in the policy's own `rule`. All of them do for all 4 policies. Every compute binding has a basis entry, and every basis entry has a binding. Then I swept back sentence by sentence, from rule to compute.

**condo_ext_liability_raise_charge**
- Step count: `steps` (1 when the limit is below the max option) ← "moves … from the lower to the higher … one step".
- Multipliers: `adjusted_step_premium = step × tenure × loss × household` ← "first multiplied together and then applied once to the tier's liability step premium, before the full-year … charge is rounded".
- Rounding: `annual_change = RND(…·steps,2)` ← "rounded half-up to the cent". `result = RND(annual_change × share,2)` ← "the full-year figure is rounded first and the share is applied to the rounded figure".
- Tenure: `MONTHS(original_effective_date, NOW)` with thresholds 120/60 ← the tenure sentence.
- Liability loss: the loss count is `COUNT(condo_claims, within_months=60, entry_date, condo_claim_payment, coverage_part ∈ {medical_payments}, {liability})` summed, thresholds ≥2/==1 ← the liability loss sentence.
- Household: `EXISTS/CFIELD('home', …, status='in_force')` with the ≥500,000 split ← the household sentence.
- Share, with three branches ← the three plan sentences. Installments billed are counted as `condo_premium_billed` with `term_effective_date = effective_date` ← "the premium installments posted with the current term's effective date".
- No tier or constant appears in compute without a rule sentence, and no rule sentence lacks a compute binding. Two sentences carry no quantity and so have no binding: the effective-day sentence (it is the `NOW` anchor) and the "depends on how the term is billed" lead-in sentence.

**condo_ext_unit_rental_charge**
- Landlord load: `landlord_liability_load = step premium if liability_limit ≥ max(options) else 0` ← the landlord load sentence.
- Multipliers: `annual_change = RND((unit_rental_annual_premium + load) × 4 multipliers,2)` ← the "Four rental multipliers adjust the sum…" sentence.
- Companion: `home_primary` is read as `CFIELD('home','occupancy', in_force) == 'primary'`, combined with the condo tenure 60 ← the companion sentence.
- Rental loss: `claim_payments_36` uses `within_months=P('claims_lookback_months')`. That parameter is 36 on every tier, so it is equivalent to the rule's literal "36 whole months". The tier split for none-and-≥36 versus none-and-<36 uses the same tenure binding.
- Returning landlord: `prior_rental_months = MONTHS(latest added eff, latest removed eff)` ← the returning-landlord sentence.
- Payment history: `late_fees_12` and `returned_12` ← the payment-history sentence and the fully-earned sentence.
- Share: `rental_share` has three branches ← the three share sentences.
- Complete in both directions.

**condo_ext_coverage_a_realignment_charge**
- Minimum: `new_minimum` selected by `master_policy_type` ← "bare-walls, single-entity or all-in minimum according to the master policy type".
- Increase: `increase_thousands = MX(0, new_minimum − coverage_a_limit)/1000` ← "number of thousands of USD by which the new Coverage A exceeds the Coverage A on the declarations".
- Multipliers: `adjusted_rate = rate × flood × claims_free × payment` ← the three-multiplier sentence. The flood, claims-free and payment ladders match their sentences.
- Share: the monthly-EFT branch is `unbilled/12`, the two-pay/quarterly branch is `MONTHS(NOW,exp)/12`, and every other case is days ← the three share sentences.
- Complete in both directions.

**condo_ext_deductible_raise_credit**
- Step credit: `step_credit` is 0.05, 0.10 or 0.07 by old deductible ← the step-credit sentence. This agrees with the base `deductible_credit_factors` differences: 0.05−0.00, 0.00−(−0.10), −0.10−(−0.17).
- The four shares, the monthly `MN(12, MONTHS+1)/12` branch and the rounding order all match their sentences.
- Observation O-1, not demonstrable in either world: the annual premium in force is computed as `annual_in_force = term_premium + SUM(… within_months=MONTHS(effective_date, NOW)+1, date_field='effective_date', premium_direction=…)`. The rule reads "every endorsement effective in the current term". The compute approximates the term with a window of whole months counted back from NOW. An endorsement effective up to about one month before the current term's effective date would fall inside this window but outside the term. No seeded row in this difficulty lies in that gap (see task 1), so no scored value is affected.

**Charter-wide observation O-2**
- Each of the four policies prorates by its own plan-dependent method:
  - monthly EFT: whole months ÷ 12 (liability), unbilled installments ÷ 12 (realignment), whole months + 1 capped at 12 ÷ 12 (deductible)
  - two-pay/quarterly: unbilled installments ÷ count (liability, rental, deductible), whole months ÷ 12 (realignment)
- Each quantity is owned by one policy, so no two clauses fight over one number. I record this as a coherence observation only.

### action_binding_and_uuids

- **Claims.** Each `(target_tool, computes)` pair is claimed by exactly one extended policy (listed under policy_conflict_scan). No base policy names a task tool.
- **UUID tails.** The tails are `70984c5d`, `60a857ee`, `ec3d8a44` and `c9f31846`. They are pairwise distinct, share no common prefix or suffix, and are not sequential or adjacent. Nothing suggests they were derived in one batch.
- **Business reading.** Each tool's docstring describes one atomic business action: the endorsement, the declarations change and the premium entry. No docstring names another tool, and no body checks eligibility, prerequisites or amounts. The module docstring says so, and the bodies do no validation: `ctx.find`, `ctx.create` and `ctx.update` only.
- **Observation O-3.** All four docstrings contain "Afterwards the declarations show …". This is a literal ordering word, but it describes the state the same call leaves behind. It does not place the action in a sequence with any other action, so there is no consequence.
- **Observation O-4.** Every tool accepts only a positive amount and always posts it. The inherited base clause "premium_direction … none below min_premium_change" has no tool path, so a charge below the tier's `min_premium_change` could not be recorded as "none". No gold figure falls below the threshold (see the task files), so there is no consequence in this difficulty.

### prerequisite_graph

Check 7 over the whole graph:
- **`prerequisite` filled in everywhere.** liability_raise `[]`, realignment `[]`, unit_rental 1 edge, deductible_raise 1 edge.
- **Edge E1** (unit_rental → liability_raise):
  - `problem` is an extended policy id in this file.
  - `kind: value_input`, gate `landlord_liability_load`, which is a real binding in unit_rental's compute.
  - `form: state` with no `fallback_reason`, which is correct for the state form.
  - `policy_source` is verbatim in unit_rental's own rule (checked mechanically).
  - `condition` ("liability_limit equals the higher of the two values in the tier's liability_limit_options") has the same strength as the sentence ("carry the higher of the tier's two personal liability limits").
  - `resolved_by: raise_liability_limit_70984c5d` is liability_raise's `target_tool`. That tool sets `condo_policies.liability_limit`, which makes the condition true and moves `landlord_liability_load` from 0 to the step premium.
- **Edge E2** (deductible_raise → coverage_a_realignment):
  - `kind: value_input`, gate `annual_in_force`, which is a real binding.
  - `form: state`.
  - `policy_source` is verbatim in deductible_raise's rule.
  - `condition` ("coverage_a_limit is at or above the tier minimum … for master_policy_type") has the same strength as the sentence ("at or above the tier's minimum for the master policy type on file").
  - `resolved_by: raise_coverage_a_minimum_ec3d8a44` is realignment's `target_tool`. That tool sets `coverage_a_limit` and writes a `coverage_a_change` endorsement with `premium_direction="additional"` effective today, so the gate holds and `annual_in_force` rises by that endorsement's `annual_premium_change`.
- **Graph shape.** Acyclic (two disjoint chains of length 1). No self-reference, and no edge points at a base policy.
- **Authoring-viewpoint phrasing.** None appears in any `prerequisite` field ("in this task", "at the opening", "current world"): I checked by eye.
- Result: PASS.

### prerequisite_sentences

Check 6, one edge at a time.

**E1: "A unit rental endorsement is not recorded until the declarations carry the higher of the tier's two personal liability limits."**
- Four-point test:
  1. Connective: "not … until" joins this policy's own result (the rental is recorded) to what it waits on.
  2. Form: state. The declarations' personal liability limit is a record-visible field (`condo_policies.liability_limit`, which `find_condo_policies` returns), and the sentence names no action and no performer.
  3. No tool, policy id, snake_case token or row id appears.
  4. Strength equals `condition`.
- Which writes can produce the waited-on state:
  - Among this difficulty's writes, only `raise_liability_limit_70984c5d` changes `liability_limit`. The other three task tools write `occupancy`, `coverage_a_limit` or `deductible`, and the shared tools have no condo write.
  - The base event `condo_endorsement_added/liability_change` has no tool in this difficulty.
  - Exactly one resolving write.
- Reader's derivation:
  1. The rental sentence says the declarations must carry the tier's higher limit.
  2. `find_condo_policies` shows the limit and tier, and the tier's `liability_limit_options` show the two limits.
  3. The only rule describing a write that moves the limit to the higher option is liability_raise S1: "A liability raise moves the personal liability limit … from the lower to the higher of the two personal liability limits the tier offers".
  4. So the resolving action is a liability raise, priced by that policy's own rule. This is a single reading.
- Rule hygiene: the rental rule has no second wording of the dependency. Its landlord-load sentence states the value consequence, not an order. It names no other problem, and the liability rule does not restate the sentence.

**E2: "The credit for a deductible raise is worked out only after the declarations show Coverage A at or above the tier's minimum for the master policy type on file."**
- Four-point test:
  1. Connective: "only after".
  2. Form: state. Coverage A on the declarations against the tier minimum for the master policy type are both on the policy record, with the minimums in the variant parameters.
  3. No tool, id or snake_case token appears.
  4. Strength equals `condition`.
- Which writes can produce the waited-on state:
  - Only `raise_coverage_a_minimum_ec3d8a44` changes `coverage_a_limit` among this difficulty's writes.
  - The "separate Coverage A change" that the realignment rule mentions has no tool in this difficulty. In any case, the owner-wants-more case is the customer's choice, not the gate.
  - Exactly one resolving write.
- Reader's derivation: the deductible sentence plus the declarations (Coverage A below the minimum for the master type) lead to realignment S1: "When the master policy type on file makes the tier's Coverage A minimum higher than the Coverage A on the declarations, a Coverage A realignment raises Coverage A to exactly that minimum". That gives the resolving action and its target value, in a single reading.
- The realignment rule does not restate the sentence.

**Undeclared cross-problem orders**
- No extended rule states an order between two problems that grounds no declared edge.
- Base rules that state an order involving these writes:
  - `condo_association_changes`: "Coverage A is raised within the association change period". This is a time window, not an order between two problems.
  - `open_claim_freeze`. This is a state gate on claims, and no claim write is part of either tree.
- No base sentence grounds an edge that a task tree rests on.
- Result: PASS for both edges.

### override_declarations

Method: I confirmed mechanically that every `superseded_clause` is a verbatim substring of the named base policy's rule, and every `replaced_by` is a verbatim sentence of the extended rule. Then I went sentence by sentence through each `base_policy_refs` entry.

**`condo_endorsements`** (base_policy_refs of all 4 policies)

| # | Base sentence (short) | liability | rental | realignment | deductible |
|---|---|---|---|---|---|
| S1 | added/removed only while bound, in force, pending nonrenewal | follows | follows | follows | follows |
| S2 | "takes effect no earlier than the date … requests it and before the expiration date" | overwritten, declared | overwritten, declared | overwritten, declared | overwritten, declared |
| S3 | LA/WB steps; "unit_rental is available only where unit_rental_allowed is true and sets occupancy to rented_to_others"; identity_fraud | n/a | follows (ext S1 restates both conditions). The new liability requirement adds a necessary condition; base "only where" states a necessary condition, not a sufficient one, so they are compatible | n/a | n/a |
| S4 | coverage_a_change keeps A in [tier min, max]; liability_change lands on an option; deductible_change lands on an option | follows (the higher option) | n/a | follows ("exactly that minimum" ≤ max) | follows ("next higher of the deductibles the tier offers") |
| S5 | sublimit fixed; included coverages never removed | n/a | n/a | n/a | n/a |
| S6 | annual change: liability step / unit_rental_annual_premium / coverage_a rate / deductible factor × term_premium | clause "liability_step_annual_premium per step …" overwritten, declared | clause "unit_rental_annual_premium;" overwritten, declared | clause "coverage_a_rate_per_1000 or … per 1,000 USD of change" overwritten, declared | clause "…term_premium multiplied by the new deductible's factor minus the old one's…" overwritten, declared (base acts on term_premium, extended on annual premium in force) |
| S7 | proration clause; "premium_direction is additional … return … none below min_premium_change" | first half overwritten, declared; direction tail inherited | same | same | same |
| S8 | open-claim freeze on coverage increases | inherited | inherited | inherited | n/a (not an increase) |
| S9 | umbrella floor on lowering | n/a | n/a | n/a | n/a |

- Base `formula.coverage_a_annual_change` implements the S6 clause that the realignment overwrote, so it falls with that clause.
- No base formula exists for the liability, rental or deductible change.

**`condo_association_changes`** (base_policy_refs of all 4 policies; it bears only on the realignment)
- A1, recording from the certificate: follows. It is not a write of this difficulty's trees.
- A2 "…must be raised … to at least the new minimum": overwritten, declared, as "exactly that minimum". The merged semantics are unique, and an owner who wants more asks for a separate change.
- A3 and A4, the association change period: inherited. They bind the realignment's timing, and each task file checks them against its own world.
- A5 (claims settled on the Coverage A in force), A6 (nonrenewal) and A7 (master deductible) govern other quantities.

**`condo_cancellation_and_reinstatement`**
- Its pro-rata cancellation sentence consumes each endorsement's signed `annual_premium_change`. The extended policies record their adjusted full-year figure as `annual_premium_change`, which does not contradict the sentence.
- The other sentences (notices, reinstatement) govern other quantities.

**`condo_bind_eligibility`** (rental and realignment)
- The Coverage A minimum table is followed by the realignment's "tier's Coverage A minimum" sentence.
- "A unit rented to others is bound only on a tier whose unit_rental_allowed is true" agrees with the rental S1.

**Disguised forms**
- Anonymous intermediate: the deductible's "annual premium in force" replaces base `term_premium`, and that replacement is declared. No other intermediate departs from base.
- 0/1 multiplier: the rental's `landlord_liability_load` adds 0 or the step premium to the base amount. This is an extended addition inside the declared replacement of "unit_rental_annual_premium;", so it is not an undeclared zeroing.
- Dropped branch: none. Every base S6 branch that is not overwritten (LA, WB, identity fraud, coverage C) has no extended selector.
- Nowhere do the authors call base output a "wrong value".

Result: no undeclared override found.

### factor_ladders

Charter-global structure only. Weight-bearing is judged in each task file.

**condo_ext_liability_raise_charge** — 4 factors: 3 `parameter`, 1 `method`. Every tier appears in the rule's prose and in compute.

| factor | effect | decides | tiers | multi-source? | cross_difficulty |
|---|---|---|---|---|---|
| liability_tenure | parameter | tenure_mult | 0.85 / 0.92 / 1.00 (≥120, 60–119, <60 months) | no (one date) | — |
| liability_loss_load | parameter | liability_loss_mult | 1.50 / 1.25 / 1.00 (≥2, 1, 0 medpay+liability payments in 60 months) | no | — |
| household_liability | parameter | household_mult | 0.80 / 0.90 / 1.00 (home in force ∧ limit ≥500k; ∧ <500k; none) | no — both conjuncts read the same `home_policies` row | home |
| liability_billing_share | method | liability_share | unbilled/count; whole months/12; days/term | yes — plan on `condo_policies` ∧ installments on `condo_billing` | — |

**condo_ext_unit_rental_charge** — 5 factors: 4 `parameter`, 1 `method`.

| factor | effect | decides | tiers | multi-source? | cross_difficulty |
|---|---|---|---|---|---|
| companion_residence | parameter | companion_mult | 0.90 / 0.95 / 1.00 | yes — home row (primary, in force) ∧ condo tenure | home |
| rental_loss_history | parameter | rental_loss_mult | 1.25 / 1.10 / 0.95 / 1.00 (4 tiers) | no (tiers 1–2 single-condition) | — |
| returning_landlord | parameter | landlord_mult | 0.90 / 0.96 / 1.00 | no (endorsement rows only) | — |
| rental_payment_history | parameter | rental_payment_mult | 1.05 / 0.97 / 1.00 | no (tier 1 single-condition) | — |
| rental_earning | method | rental_share | fully earned (1); unbilled/count; days/term | no (tier 1 single-condition) | — |

**condo_ext_coverage_a_realignment_charge** — 4 factors: 3 `parameter`, 1 `method`.

| factor | effect | decides | tiers | multi-source? | cross_difficulty |
|---|---|---|---|---|---|
| flood_companion | parameter | flood_mult | 0.93 / 0.97 / 1.00 | no — both conjuncts read the same `flood_policies` row | flood |
| realignment_claims_free | parameter | claims_free_mult | 0.90 / 0.95 / 1.00 | no | — |
| realignment_payment_record | parameter | payment_mult | 1.05 / 0.97 / 1.00 | no (tier 1 single-condition) | — |
| realignment_billing_share | method | realignment_share | unbilled/12; whole months/12; days/term | yes — plan ∧ billing rows | — |

**condo_ext_deductible_raise_credit** — 5 factors: 4 `parameter`, 1 `method`.

| factor | effect | decides | tiers | multi-source? | cross_difficulty |
|---|---|---|---|---|---|
| deductible_loss_history | parameter | claims_share | 0.60 / 0.80 / 1.00 | no | — |
| deductible_reraise | parameter | reraise_share | 0.25 / 0.50 / 1.00 | no (endorsement rows only) | — |
| deductible_tenure | parameter | tenure_share | 1.10 / 1.05 / 1.00 | no | — |
| deductible_late_payment | parameter | late_share | 0.80 / 0.90 / 1.00 | no | — |
| deductible_billing_share | method | deductible_share | (whole months+1, ≤12)/12; unbilled/count; days/term | yes — plan ∧ billing rows | — |

**Structural checks**
- Every factor has ≥3 tiers, and the tiers of each ladder are pairwise disjoint as stated.
- No two tiers of any ladder select the same value or the same method.
- Each factor's `bindings` are disjoint from every other factor's in the same policy, and every `decides` is an input, never `result`.
- Some ladders read the policy's tenure binding, which is owned by `companion_residence`: the rental_loss tier 3 and the rental_payment tier 2. That is a shared input, not a shared binding.
- Every fall-through tier equals the factor's `baseline`: `standard_mult` = 1.00, or `days_left / term_days`.
- Each policy's `baseline.rule` is made of sentences that appear verbatim in its `rule` (checked mechanically). Its `params` are the keys the baseline uses.
- Each baseline gives a definite number from the records with no factor applied, given the day of the change. The effective-day sentence is in the `rule`, not in `baseline.rule`, but "today" comes from the customer and the clock.
- Labels are honest:
  - Every `parameter` factor substitutes a number into an unchanged formula.
  - Every `method` factor switches between charter-stated algorithms: an installment ratio, a whole-month ratio (with or without the +1/cap rule), a day ratio, or "fully earned".
- Per-task floor, provided each tree is one component as the graph implies:
  - The {liability, rental} tree carries ≥1 multi-source factor (liability_billing_share, companion_residence) and ≥1 cross-difficulty factor (household_liability, companion_residence → home).
  - The {realignment, deductible} tree carries ≥1 multi-source factor (realignment_billing_share, deductible_billing_share) and ≥1 cross-difficulty factor (flood_companion → flood).
- Industry realism (an observation, not a demonstrable RED):
  - Multi-policy (home/flood companion), tenure, loss-history, late-payment/returned-payment and EFT treatments all appear in personal-lines rating.
  - Observation O-5: the `method` ladders set the premium or credit amount by installments or whole months, not by days of cover. Carriers usually prorate an endorsement by days and use installments only to spread the bill. Monthly-earning and installment-earning conventions are not unknown, however, and I cannot show that no carrier would publish them. The rental's "fully earned when a payment was returned in the last 12 months" tier bills a full year's charge for part of a term. It is an unusual treatment, but fully-earned provisions do exist. That tier is not taken in either task.
  - No tier condition holds for every customer who reaches its write. None is a restatement of scope.

### findings

- **No charter-global RED.** Policy self-consistency (checks 1, 2, 3, 6 and 7) passes over the whole charter.
- **Observations**, no demonstrated consequence (details above):
  - O-1: the deductible's annual-in-force window is approximated in compute. It bears on task 1, where no row lies in the gap.
  - O-2: plan-dependent proration methods differ across the four policies.
  - O-3: the literal "Afterwards" in the tool docstrings.
  - O-4: no tool path for `premium_direction none` below `min_premium_change`. It bears on tasks 0 and 1, where no gold figure is below the threshold.
  - O-5: the realism of the installment and month-earning methods and of the fully-earned tier.
- **Observation O-6**, bearing on task 0: the rental's landlord-load sentence ("…and nothing when they carry the lower one") gives the lower-limit branch. The E1 prerequisite sentence makes that branch unreachable at the moment the rental is recorded. As a result, the value E1 feeds into the rental is a constant set by a status flip, the tier's step premium. None of the liability raise's computed figures (its multipliers and its charges) ever reach the rental. The edge still bears weight: the value changes when the edge is skipped. The per-task criteria (≥1 `value_input` edge whose binding exists and moves) are met, so this is recorded as an observation only.

## closing_checklist

Written after both tasks' `source_gt_comparison` sections were on disk (the reveal was at 2026-09-24T23:29Z; the pre-reveal sha256 of this file was `de9a5fea468c1388bd53fbf14f3fcb1c7b85db0226b9e7874e2d3388dfd42b9f`). Nothing above this heading was written after the reveal.

**Status: the difficulty is NOT closed.** Both tasks carry a SOURCE-FACTOR RED, so the "all four relationships PASS" precondition of Step 4 is not met. The checklist items are recorded as they stand.

| item | status |
|---|---|
| Per-task files one-to-one with tasks; `_difficulty.md` alongside | `0.md` and `1.md` for tasks/0.json and 1.json; no earlier revision exists |
| Every comparison section carries PASS | **No**: 0.md is SOURCE-FACTOR RED (F0-1), 1.md is SOURCE-FACTOR RED (F1-1) |
| Extended policies fully covered; scopes pairwise disjoint over the whole tree | Yes. Task 0 `charter_scope` = {liability_raise, unit_rental} with its 2 tools. Task 1 = {coverage_a_realignment, deductible_raise} with its 2 tools. Disjoint, and the union is all 4 policies and 4 tools. Each scope equals one connected component of the prerequisite graph |
| Task tools and GT closed; uuid8s independent | Yes (§ action_binding_and_uuids); `db_closure_matches_initial_state` is true in both tasks |
| Each tree has 1–3 prerequisites, ≥max(n−1,1) value_input edges, ≥1 owner=user problem, no cycle | Yes, in both: n=1, 1 value_input edge, and the root is owner=user. The difficulty-wide graph is 2 disjoint chains, acyclic |
| Every computation: self-sufficient baseline, 4–6 factors (≥2 parameter, ≥1 method), ladders ≥3 tiers stated in the rule, per task ≥1 multi-source and ≥1 cross-difficulty, every factor bears weight, fall-back number definite and ≠ gold | Structurally yes (§ factor_ladders), and weight is borne in both tasks. The failures are the F0-1 proof figures and the F1-1 cross-difficulty holding, which contradicts the flood charter |
| Instantiation gates re-run on the final form | Not applicable: the difficulty is not closing. Per the brief, this auditor only cites the supplied snapshot and ran no gates |

Carried charter-global observations: O-1 to O-6 (§ findings). None was demonstrated to have a consequence on either task's world.

---

## revision_2

Re-audit round 2, after the rework. The round-1 text above is unchanged.

### charter_global_frozen (revision_2)

- Freeze time: 2026-09-24T23:4xZ, written before either round-2 task JSON was opened. Auditor: the same independent audit agent as round 1.
- Frozen inputs, hashes recomputed by me and matching the coordinator's brief:
  - `condo.extended.yaml` sha256 `a50069087311521dad763d872404c13b7d3bac52d39d1351afc1018028009f9e` (round 1: `28ab82c1…`)
  - `task_tools.py` sha256 `7d37dc543ea88c63e5ea70d86e0a4e82a94b96576c593083b1aba7c43948fbf6` (round 1: `d7bcb18b…`)
- Both shared inputs changed, so every charter-global section below was re-derived in full. None is carried forward by reference.
- Masking was the same as in round 1. I read no worklog, ran no recursive search, and did not touch `_orchestrator_private` beyond reading the views.
- contamination_disclosure: this auditor saw the round-1 GT of both tasks during round 1. The charter-global sections below depend only on the charter, the tools and the blueprint, so that exposure cannot shape them. The same exposure is disclosed in each task file.

**Entry conditions**
- The gate snapshot after the rework was supplied: 7 gates green, traceability deferred.
- The rebuilt views were supplied with hashes: `0.view.json` `e994d7bc…569f` and `1.view.json` `e0c98df9…6ab1`, both matching.
- Complete.

**What changed.** No round-1 copy was retained, so this is a sentence-by-sentence re-read against the round-1 text quoted in this file and in my round-1 working notes.
- Base section: still verbatim. Diffed against `products/condo.yaml`, the only difference is the trailing blank line.
- `condo.extended.yaml`: each of the 4 extended rules gains one final sentence of the form "Each rounding of the <charge> to the cent is half-up in exact decimal: a figure lying exactly halfway between two cents goes to the higher cent."
  - Each policy's `compute_basis.result` now quotes that sentence verbatim.
  - The `annual_change` and `result` bindings replaced `RND(x, 2)` with `int(round(x * 100, 6) + 0.5) / 100`.
  - Nothing else changed: `params`, `factors`, ladders, `baseline`, `overwrite`, `prerequisite`, `cross_category`, `inputs` and every other compute line are identical in substance to round 1. I checked each by printing it.
- `task_tools.py`: in each of the 4 docstrings, "Afterwards the declarations show …" became "On success the declarations show …". The function bodies are identical: no validation branch, the same writes and the same directions.

### policy_conflict_scan (revision_2)

- The added rounding sentence governs only the rounding of each policy's own charge. It agrees with the base `condo_endorsements` S7 ("rounded half-up to the cent") and narrows the tie case to half-up, which is what "half-up" already means.
- No new overlap in subject, trigger, eligibility, time anchor, parameter, terminal state or cross-category read.
- The prerequisite graph still has two components: {liability → rental} and {realignment → deductible}.
- Result: no conflict (the round-1 conclusion re-derived).

### rule_compute_equivalence (revision_2)

- Mechanical checks re-run on the new file, all true for all 4 policies:
  - every `compute_basis` value is verbatim in its own rule
  - compute keys equal basis keys
  - every `baseline.rule` sentence is in its rule
  - every overwrite `replaced_by` is in its rule, and every `superseded_clause` is in the named base rule
  - every `policy_source` is in its rule
- **New rounding binding.** For x ≥ 0, `int(round(x*100, 6) + 0.5)/100` equals exact-decimal half-up to the cent: the 6-place pre-round removes binary noise, and `+0.5` followed by truncation rounds ties up. Every charge in this charter is a positive amount (the tools take "a positive amount"), so the negative branch, where truncation would round toward zero, is never reached.
- Tie cases checked in float against exact Decimal:
  - 76.545 → 76.55, then 38.275 → 38.28
  - 91.125 → 91.13, then 45.565 → 45.57
  - every non-tie figure of both worlds agrees
- The new rule sentence is now implemented by both rounding bindings and quoted under `result`. Both directions hold.
- **O-1** (the deductible's annual-in-force window is approximated in compute): unchanged. The rework kept it, and it is still not demonstrable on either world (task 1 re-checked in its revision_2).
- **O-2** (the plan-dependent share methods differ across the four policies): unchanged. It remains an observation.

### action_binding_and_uuids (revision_2)

- The `(target_tool, computes)` claims are unchanged and unique. The uuid8s `70984c5d`, `60a857ee`, `ec3d8a44` and `c9f31846` are unchanged, independent and frozen.
- **O-3: closed.** No docstring now contains "Afterwards", "after", "before" or "first" (checked with grep). "On success the declarations show …" describes the call's own resulting state and places the action in no sequence.
- **O-4** (no tool path for `premium_direction none` below `min_premium_change`): unchanged. The bodies still always write the passed direction. It remains an observation, re-checked per task.

### prerequisite_graph (revision_2)

- Edges E1 and E2 are byte-identical to round 1 in `problem`, `kind`, `gate`, `form`, `policy_source`, `condition`, `resolved_by` and `effect`.
- The graph is acyclic, and the gates `landlord_liability_load` and `annual_in_force` still exist in compute.
- PASS.

### prerequisite_sentences (revision_2)

- The two sentences are unchanged, and each is still the only statement of its dependency.
- The added rounding sentences state no cross-problem order.
- Neither depended-on rule restates a prerequisite sentence.
- Exactly one write of the difficulty produces each waited-on state (the tool bodies are unchanged).
- PASS. The derivations written in round 1 still hold.

### override_declarations (revision_2)

- The sentence-by-sentence table of round 1 was re-checked against the new rules and holds unchanged.
- The one new sentence per policy follows base S7's "rounded half-up to the cent" and replaces no base sentence, so it needs no `overwrite` entry.
- No undeclared override.

### factor_ladders (revision_2)

- Factors, ladders, labels, `decides`, bindings, baselines and `cross_difficulty` are identical to round 1: 4, 5, 4 and 5 factors, each policy with at least 2 `parameter` and 1 `method`.
- The round-1 structural table stands:
  - multi-source: `liability_billing_share`, `companion_residence`, `realignment_billing_share` and `deductible_billing_share`
  - cross-difficulty: `household_liability` and `companion_residence` (home), `flood_companion` (flood)
- `flood_companion` and `deductible_reraise` are still not multi-source by the definition. Whether task 1's trace still claims they are (O-T1-a) is checked in `1.md` revision_2.
- **O-5** (realism of the installment and month-earning methods and of the fully-earned tier): unchanged. It remains an observation.
- **O-6** (the E1 value input is a status-driven constant, and the lower-limit load branch is unreachable at recording): the rental rule R3 and R5 are unchanged. It remains an observation.

### findings (revision_2)

- No charter-global RED.
- O-3: closed.
- O-1, O-2, O-4, O-5 and O-6: still present, still without a demonstrated consequence, and kept as observations. The rework chose to keep them. That decision is the reworker's; the observations themselves are unchanged.
- **New observation O-7:** the exact-decimal half-up sentence is in each `rule` but not in `baseline.rule`. The baseline says "rounded half-up to the cent", which already fixes the tie direction, so the baseline stays self-sufficient. There is no consequence.

### closing_checklist (revision_2)

- Written after both tasks' revision_2 `source_gt_comparison` sections were on disk.
- The pre-reveal sha256 of this file (charter-global revision_2) was `0ebe8b56a7e9b91ec2a4fb84bdd0859907fed744bb74431153e16d97d4637447`, taken at 23:39:13Z. The "23:4xZ" in the § revision_2 / charter_global_frozen header is a typo for that time.
- Nothing in the revision_2 charter-global sections above was written after the reveal.

**Status: the difficulty CLOSES.** Both tasks PASS all four relationships in revision_2.

| item | status |
|---|---|
| Per-task files one-to-one with tasks; old revision preserved | `0.md`, `1.md` and `_difficulty.md` each keep round 1 verbatim, with `## revision_2` appended |
| Every comparison section carries PASS | Yes: 0.md revision_2 PASS, 1.md revision_2 PASS |
| Extended policies fully covered; scopes pairwise disjoint | Yes: {liability_raise, unit_rental} and {coverage_a_realignment, deductible_raise}, 4 policies and 4 tools, each claimed once |
| Task tools and GT closed; uuid8s independent and frozen | Yes; `db_closure_matches_initial_state` is true in both tasks, and the uuid8s are unchanged |
| Each tree: 1–3 prerequisites, ≥max(n−1,1) value_input edges, ≥1 owner=user problem, no cycle; the difficulty graph is a DAG | Yes (n=1, 1 value_input edge, the root is owner=user in both; 2 disjoint chains) |
| Computations: self-sufficient baseline, 4–6 factors (≥2 parameter, ≥1 method), ≥3-tier ladders in the rule, per task ≥1 multi-source and ≥1 cross-difficulty with seeded and charter-consistent rows, every factor bears weight, fall-back definite and ≠ gold | Yes, in both tasks. The cross-difficulty home and flood rows are now consistent with their own charters |
| Instantiation gates on the final form | The orchestrator's post-rework snapshot is cited, 7/7 green (EXTENDED, TASK-TOOL-CONTRACT, REPLAY, SOLVABILITY, COMPUTE, GROUNDING, SCOPE), with traceability deferred until the KB is published. Per the brief, this auditor ran no gates |

**Round-1 item closure**
- **REDs:** F0-1 closed; F1-1 closed.
- **Resolved:** O-3; the home-contents observation (task 0); O-T1-a (task 1).
- **Kept as observations:** O-1, O-2, O-4, O-5 and O-6, none demonstrated to have a consequence on either world. The reworker's reasoning is recorded in each task's `design_rationale` [Revisions].
- **New observations:** O-7 (charter-global), and the placement of the flood seed-consistency proof (task 1). Neither is a RED.
