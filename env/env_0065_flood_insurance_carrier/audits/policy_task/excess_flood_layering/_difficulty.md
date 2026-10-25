# Policy-task audit — excess_flood_layering / charter-global

## charter_global_frozen
- Revision: 1. Written 2026-10-15T22:27Z, before any task GT was revealed; nothing below is derived from a revealed GT.
- Auditor: independent policy-task auditor (erl-task-policy-audit), not the instantiating agent.
- Frozen inputs (sha256 prefix, recomputed by the auditor and matching the coordinator snapshot):
  - `tasks/excess_flood_layering/excess.extended.yaml` ae9a39e8268addb7
  - `tasks/excess_flood_layering/task_tools.py` 8c315e853830b65a
  - masked views `.audit_views/policy/excess_flood_layering/0.json` 15dffa70d227654d, `1.json` eda41b7bf1af1b6b
- Fields read: `blueprint/` (blueprint.yaml, db_schema.json, share_tools.py, products/excess.yaml, homeflood.yaml and dwelling.yaml for cross-category variants and states), the extended charter, task_tools.py, the masked views (frozen_time, user_scenario, initial_state only), the DSL evaluator in `skills/erl-task-instantiate/scripts/check_compute.py` (`build_env`: SUM/COUNT/LATEST are scoped to the target holding, X* to the customer, CFIELD/CPARAM return the first matching holding, MONTHS counts whole months).
- Fields masked and not read: everything in `tasks/excess_flood_layering/tasks/*.json` besides the masked views (evaluation_criteria, computations, charter_scope, required_documents, design_rationale, solvability_contract, prerequisite_closure). `tasks/excess_flood_layering/worklog.md` and the scenario `worklog.md` were not read.
- Entry conditions (Step 0): the gate snapshot (`snapshot_r1.txt`) is supplied. check_extended, check_task_tools, replay --check, check_solvability, check_compute, check_grounding and check_cross_fire are green. The only traceability miss is the unlock tool-name provenance of `sign_excess_limit_increase_cddf0413`, and validate_scenario reports `documents: 0`. Both are pre-render and expected. The masked views and their hashes are supplied. Input is complete.
- Base copy: lines 1–1052 of the extended file are byte-identical to `blueprint/products/excess.yaml`; the diff shows only the trailing blank line.

### policy_conflict_scan
The charter has four extended policies:
- P1 `excess_ext_renewal_term_premium` (book_excess_renewal_30706efc, agent, computes term_premium)
- P2 `excess_ext_limit_increase_premium` (sign_excess_limit_increase_cddf0413, user, computes additional_premium)
- P3 `excess_ext_sale_cancellation_return` (sign_excess_sale_cancellation_a26754a5, user, computes returned_premium)
- P4 `excess_ext_loss_of_use_payment` (pay_excess_loss_of_use_f5cb8480, agent, computes payment_amount)

- **Subjects and triggers.** P1 is triggered on excess_term_renewed (state_due), P2 on a LIMIT_INCREASE endorsement (on_request, to-value only), P3 on excess_policy_cancelled for a sale (on_request), and P4 on an LOU excess_claim_paid (state_due). No two policies write the same event.
- **Shared quantities.**
  - P1 sets `term_premium` for a renewal term, and P2 then re-sets it to "the full-term premium as endorsed". These are compatible because P2 reads the booked TERM_PREMIUM item of the current term.
  - P3 reads `F('term_premium')`. After a P2 increase that is the endorsed figure, which is consistent with the base endorsement rule.
  - P1 tenure (`renewals_booked`) and P3 `renewals_on_policy` use an identical filter. P3 `sale_closing` and P4 `sale_closing` use the identical expression.
- **Time anchors.**
  - P1 counts loss months to "the renewal is booked" (NOW) and early days to "the current term end".
  - P2 measures signing days against the term carried on the record.
  - P3 measures from the request date and the HomeFlood cancellation date.
  - P4 measures from the date of loss to the latest report and NOW.
  - None of these collide.
- **Cross-category read boundaries.** dwelling is read by P1 and P2, homeflood by P1 (existence), P3 and P4. All of these are declared in `cross_category`. P4 also filters homeflood on `cancellation_reason` and `status` without listing them under reads (observation O-9).
- **Credit interplay.** P1's last sentence (an overpaid renewal stays as a credit for that term) and P2's last sentence (a credit on the current term that covers the increase counts as full payment) read the same balance in the same direction. There is no conflict, and base `excess_premium_rating` ("never moved to another policy") is respected.
- **Scope exclusivity.** The two prerequisite edges are P2←P1 and P3←P4, which gives two disjoint trees {P1,P2} and {P3,P4}. With M=2 the claimed scopes can be pairwise exclusive and jointly complete. Which task claims which tree is confirmed in the task files after the reveal. The task worlds are consistent with task 0 = {P2 root, P1} and task 1 = {P3 root, P4}.
- **Conflicts found.** Two undeclared overrides (F-4 and F-5 below) and one class of rule/compute scope divergence (F-6). No other cross-policy conflict.

### rule_compute_equivalence
- **Mechanical sweep** (script in auditor scratch, normalised whitespace):
  - Every `compute_basis` quotation of all four policies is a verbatim substring of its own rule.
  - Every compute binding has a basis entry, and every basis entry names a binding.
  - Every sentence of each `baseline.rule` occurs in the rule.
  - Every `replaced_by` is verbatim in the rule.
  - Both prerequisite `policy_source` sentences are verbatim in the rule.
- **Back-sweep, rule to compute, per policy:**
  - P1: the scheduled layer, zone ladder (the full table restated as K constants, same values as the base `zone_factor_table`), elevation multiplier with the NFIP fallback, five percentage ladders summed once into `net_adjust_pct`, applied after the elevation multiplier and never on the LOU charge, RND once and MX floor. The rounding sentence ("rounded to the cent once ... never less than the tier's minimum premium") matches `MX(floor, RND(adjusted+lou,2))`. The overpayment-credit sentence is carried by the tool's balance update, not by compute, which is correct for a ledger effect.
  - P2: top limit, added limit, the three-way layer-rate method, relativity, three surcharges summed into one loading, the charged-share ladder and RND once at the end. All multiplicative, so the order commutes. "The full-term premium as endorsed" (scored argument `revised_term_premium`) is stated in the rule ("term premium before the increase plus the additional premium before the charged share ... rounded to the cent") but has no compute binding. This is an observation (O-1): the formula is complete in prose, and no second reading was found.
  - P3: earned days with the backdating ladder, removed days, unexpired days, the floor-share ladder, `MN` cap, retention and early charge subtracted after the cap, `MX(0)` and RND once. The rule's order ("every number of days ... removed before the returned premium is figured, and every retention or charge ... subtracted from the returned premium") matches the compute.
  - P4: the order of shares/cuts multiplied, then deductions, then the cap, then prior payments, then interest/allowance added last, is stated and matches. Interest is on "the new loss-of-use payment" (`lou_due`).
- **Ladders, rule against compute.** Every tier named in `factors[].ladder` is a rule sentence and a branch of its `decides` binding, and no compute branch is missing from the rule. No tier lives in only one face.
- **Divergences.** Filters the rule states but the compute does not implement are recorded as F-6 (class list there). The paid-claim bar's netting of voids is recorded as F-5.

### action_binding_and_uuids
- **Bindings.** The four `(target_tool, computes)` pairs are each claimed by exactly one policy. The docstrings describe one action each, add no confirmation, review or wait, name no other tool, and carry no ordering word (before/after/first). The phrases "whose renewal has been paid and whose underlying primary flood policy is on file" and "a credit already standing on the policy is set against them" describe the object's state, not a sequence.
- **UUIDs.** 30706efc, cddf0413, f5cb8480 and a26754a5 are pairwise unrelated hex with no shared prefix, sequence or adjacency. They are accepted as independently generated and frozen with each tool.
- **Docstring leaks.** No docstring or argument description carries an example value. The only figure is the base policy fee of 150.00, which comes from the charter.
- **Tool bodies.** No tool checks a prerequisite.
  - `book_excess_renewal` books from `term_end` whatever the record shows.
  - `sign_excess_limit_increase` checks only that the id exists.
  - `pay_excess_loss_of_use` checks only the policy id and copies date_of_loss from the first-notice row.
  - `sign_excess_sale_cancellation` checks only the id.
- **Shared tools.** `share_tools.py` has only reads plus `verify_customer_identity` and `transfer_to_human_agent`. No shared write can change an excess term or create an LOU payment.

### prerequisite_graph
- **Coverage.** `prerequisite` is filled in on all four policies: P1 `[]`, P4 `[]`, and one edge each on P2 and P3.
- **Edge E1, P2 → P1.**
  - kind value_input, gate `charged_share` (an existing binding), form state, no fallback_reason, resolved_by `book_excess_renewal_30706efc` (P1's target_tool).
  - `policy_source` is verbatim in P2's own rule.
  - The condition adds "and the TERM_PREMIUM item of that term stands on excess_billing", which the sentence does not state (observation O-2). It has no consequence, because the one write that carries the term also books that item.
  - The effect is real: booking moves `term_start`/`term_end` and posts the TERM_PREMIUM read by `booked_term_premium`.
- **Edge E2, P3 → P4.**
  - kind value_input, gate `retention_share` (exists), form state, no fallback_reason, resolved_by `pay_excess_loss_of_use_f5cb8480` (P4's target_tool).
  - `policy_source` is verbatim in P3's rule.
  - The condition says "dated on or after that report" where the sentence says "issued after that report" (observation O-3). It is a same-day boundary only, with no consequence in either world.
  - The effect is real: the new LOU payment row moves `latest_lou_payment`.
- **Graph shape.** Acyclic: two disjoint chains of length one. No authoring-viewpoint wording ("in this task", "at the opening") appears in any prerequisite field.

### prerequisite_sentences
**E1** — "The additional premium for a limit increase is figured only once the policy record carries the term in which the increase takes effect, from that term's start to its end."
- Four-point test:
  - (1) Ordering connective "only once" joins P2's result to the waited-on state.
  - (2) State form: what it waits on is a record-visible state (the term dates on the policy record) with no action, performer or tool.
  - (3) No tool, policy id, snake_case token or row id.
  - (4) The strength matches the condition up to O-2.
- Exactly one write of this difficulty changes the policy record's term: `book_excess_renewal_30706efc` (P1). P2's own tool, P3, P4 and the shared writes do not.
- Derivation: the record shows a term already ended, or not containing the day the increase takes effect. P1's rule says a renewal paid by the current term end, with underlying declarations on file, "is booked as the next term, starting on the day the current term ends and running one calendar year". That is the only rule that produces a new term on the record, so this is a single reading.
- P1's rule does not restate the sentence.
- Observation O-4: the sentence does not say whether "to its end" includes the end day. The prerequisite condition uses an exclusive end, and the base measure `excess_msr_term_claims_paid` reads term_end as exclusive.

**E2** — "The returned premium on a sale cancellation is not fixed until every claim on the policy whose latest adjuster report documents more loss of use than has been paid carries a loss-of-use payment issued after that report."
- Four-point test:
  - Connective "not fixed until".
  - State form: an LOU payment row dated after the report, which is record-visible.
  - No tool or id.
  - Scope stated as "every claim on the policy".
- Exactly one write produces an excess LOU payment row: `pay_excess_loss_of_use_f5cb8480` (P4).
- Derivation: the latest report shows LOU incurred above LOU paid. P4's rule says "A loss-of-use payment on an Excess Flood claim falls due once an adjuster report documents loss of use beyond what has been paid", so this is a single reading.
- P4's rule does not restate the sentence.

**Other rules.**
- No rule states a cross-problem order that grounds no declared edge.
- P3's "where the Tidemark HomeFlood policy on the same home has been cancelled for that sale" and P1's "whose full payment ... was received on or before the current term end" are scope or eligibility states of other records that are already true at the openings, not undeclared problem orders.
- No base sentence grounds either edge.

### override_declarations
The verdict per base sentence in each `base_policy_refs` entry, plus base sentences outside the refs that govern a scored quantity.

**P1** (refs: excess_agg_underlying_requirement, excess_premium_rating, excess_renewal)
- underlying_requirement: followed. The bind/renew evidence sentence is restated as "declarations ... showing it in force on the renewal date on file". The attachment and no-drop-down sentences are untouched.
- premium_rating:
  - The annual-premium sentence is superseded and declared, and `replaced_by` names its own scope ("For a renewal term booked under this rule, and only for such a term ... every other term premium remains under the base rating rule").
  - The fee, tax/stamping, four-item booking, payment-in-full and payment-application sentences are followed (tool).
  - An item of 0.00 is not booked, which matches the seeded history.
- renewal:
  - The offer sentence is followed: the rule calls the offer "a quotation on the schedule, not the booked figure", which is consistent because the base never makes the offer the booked premium.
  - The bound-by-term-end sentence is followed.
  - The non-renewal notice sentence is untouched.
- Disguised forms: no anonymous intermediate, 0/1 multiplier or dropped branch. The NFIP-certificate fallback for the elevation multiplier deviates from base "when an accepted Elevation Certificate on file shows ...", and that sentence is inside the superseded clause, so it is declared.

**P2** (refs: excess_limits_eligibility, excess_waiting_period, excess_endorsements)
- limits_eligibility: followed. The top limit respects the increment, the tier maximum and the RCV cap. The EC/V-zone gates are inherited.
- waiting_period: the first sentence is superseded and declared, with own scope named. The concurrent-purchase, decrease and "loss before ... not covered" sentences are inherited.
- endorsements: the status sentence is followed, the re-rate/pro-rata sentence is superseded and declared, and the minimum-earned/policy-fee sentence is followed.

**P3** (ref: excess_cancellation_refund)
- Three superseded clauses, each declared with its own scope: the signed request/status sentence, the PROPERTY_SOLD date, and the pro-rata-with-minimum-earned sentence.
- Followed: fee fully earned, taxes returned, CANCELLATION credit and refund.
- **Not declared:** the paid-claim bar is handled differently (F-5).

**P4** (ref: excess_claim_settlement)
- The LOU sentence is superseded and declared, with own scope.
- The building/contents sentences are untouched.
- The "new payment = payable less already paid net of voids ... issued only when positive" sentence is followed for `lou_due`. Interest and allowance are added after it, covered by "with the additions this rule sets out".
- The `replaced_by` says "less the loss of use the underlying Tidemark policy paid where this rule says so", while the rule's second offset tier subtracts the HomeFlood tier's limit, not a paid amount (observation O-5: wording only, the rule sentence is unambiguous).
- **Not declared**, from a base policy outside the refs: excess_claim_intake_pol "Payment is due within claim_payment_days calendar days after the later of the agreed proof of loss and the underlying settlement record." P4 sets a different due date for an LOU payment (F-4).

### factor_ladders
Counts are per policy. M = method, Pm = parameter, ms = multi-source (every non-fall-through tier is a conjunction or disjunction over distinct records), xd = reads another difficulty.

**P1: 6 factors** (5 Pm, 1 M)
- `renewal_loss_history` Pm, 3 tiers, ms (NFIP payments × excess payments), xd dwelling. **Ladder unreal (F-1).**
- `tidemark_account_relationship` Pm, 3 tiers. Tier 1 is single-source (HomeFlood active), tier 2 is a conjunction (no HF active ∧ NFIP in force), so not ms by the definition. xd homeflood/dwelling. Real.
- `residence_designation` Pm, 3 tiers, xd dwelling. Real: it mirrors the NFIP primary/non-primary distinction.
- `tenure_on_layer` Pm, 3 tiers (≥5 / 2–4 / <2). Real.
- `payment_ahead_of_term_end` Pm, 3 tiers (≥30 / 10–29 / fewer or none). Real as a company schedule. Its fall-through's "no payment" part is unreachable under P1's own scope, but the "fewer than 10 days" part keeps it a genuine tier.
- `certificate_source` M, 3 tiers. Own EC whole-foot / NFIP applied EC (LFE−BFE, age ≤ max at receipt) / none → 1. An honest method: the source and the algorithm of the elevation difference change. xd dwelling.
- Tiers within each ladder are disjoint and select distinct values. `residence_designation` −3 and `tenure_on_layer` −3 are different factors, which is allowed.

**P2: 6 factors** (4 Pm, 2 M)
- `signing_window` M, 3 tiers (flat whole term / deferred, share 0 / share from end of waiting). Honest method.
- `rate_derivation` M, 3 tiers (schedule × zone / booked less LOU × dwelling share / booked less LOU). Honest method.
- `layer_position` Pm, 3 tiers (0.8 / 0.9 / 1.0). It reads the sum of two records, but a sum is not a conjunction or disjunction, so it is not ms.
- `primary_loss_recency` Pm, 3 tiers, xd dwelling.
- `repeat_increase` Pm, 3 tiers.
- `zone_of_record_surcharge` Pm, 3 tiers, xd dwelling. The zone read is a fallback across two records (NFIP in force, else the policy record). This is arguably a disjunction over distinct records, but the compute forks only on `zone_read`.
- Realism:
  - Observation O-6: `signing_window` tier 1 makes a flood limit increase effective retroactively to the term start when signed up to 30 days after it, with no statement of no known loss. This mirrors the NFIP renewal-cycle convention, so it is not proven unreal, but it is an adverse-selection concern for a carrier whose base allows no renewal grace.
  - Observation O-7: the zone surcharge partly double-counts the zone factor already inside the layer rate.
- No two tiers in a ladder share a value or method.

**P3: 5 factors** (3 Pm, 2 M)
- `backdating_limit` M, 3 tiers. The anchor date changes (closing / request−30 / request).
- `unexpired_cutoff` M, 3 tiers. Declared expiry / HomeFlood term end / none. xd homeflood at tier 2 only.
- `sale_minimum_waiver` Pm, 3 tiers. **One compound part holds of every customer reaching the write (F-3).**
- `use_charge_retention` Pm, 3 tiers (1 / 0.5 / 0). Observation O-8: the tier keys on when the latest LOU payment was issued, not on a loss in the term, with an unbounded look-back for the half tier. This is a weak business rationale, but "LOU charge earned once LOU is paid" is a recognisable fully-earned convention, so it is not proven unreal.
- `early_cancellation_charge` Pm, 3 tiers (100 / 50 / 0). Real.

**P4: 6 factors** (3 Pm, 3 M)
- `comparable_housing_share` Pm, 3 tiers. Real (a comparable-housing cap).
- `displacement_period_end` M, 3 tiers, ms (HomeFlood sale record × excess report date). Real.
- `primary_lou_offset` M, 3 tiers, ms (underlying type × HomeFlood claim file), xd homeflood. Observation O-10: tier 1 (subtract what was paid) lets the excess drop down when the primary paid below its limit, which is in tension with base no-drop-down practice. The rule's "claim file of the insured" scope belongs to F-6.
- `relocation_allowance` Pm, 3 tiers, ms, xd homeflood. **Ladder unreal (F-2).**
- `interest_due_anchor` M, 3 tiers. Its tier 1 contradicts the base due date (F-4).
- `claim_age_rate` Pm, 3 tiers (10 / 8 / 0 %). Observation O-11: an interest rate keyed to the age of the loss, rather than to lateness, is unusual, but it is a company schedule.

**Baselines**
- All four `baseline.rule` texts are complete standard methods whose sentences are all in the rule.
- Each factor's fall-through equals its baseline binding:
  - P1: 0 %, and the policy-record-EC-only multiplier.
  - P2: the standard-waiting share, booked less LOU over the limit, relativity 1, and 0 %.
  - P3: earned to the closing date, 0 removed days, the tier minimum earned share, retention 0, charge 0.
  - P4: share 1, fraction 1, offset 0, allowance 0, days late 0, rate 0.

**Totals**
- P1: 6 factors (2 Pm ✓, 1 M ✓); ms 1 (struck by F-1); xd dwelling and homeflood.
- P2: 6 factors (4 Pm, 2 M); no factor is ms by the strict definition.
- P3: 5 factors (3 Pm, 2 M); the one compound factor is hollowed by F-3; xd homeflood.
- P4: 6 factors (3 Pm, 3 M); ms are `displacement_period_end` and `primary_lou_offset`; xd homeflood.
- Counted after striking F-1, F-2 and F-3:
  - P1: 5 factors (4 Pm, 1 M). Within bounds, but no ms factor remains on the {P1,P2} tree.
  - P3: 4 factors (2 Pm, 2 M). Within bounds.
  - P4: 5 factors (2 Pm, 3 M). Within bounds.

### findings
**F-1 — SOURCE-FACTOR RED (unreal ladder): P1 `renewal_loss_history`**
- Symptom: the fall-through "otherwise there is no loss-history adjustment" covers a policy whose own excess layer paid a claim within 36 months, whenever no Tidemark NFIP payment stands beside it. That is always the case when the primary is private (HomeFlood or another carrier). A loss confined to the primary draws +10 %.
- Evidence: P1 rule, "where the NFIP policy carries one and this excess policy carries none it is a surcharge of 10 percent, and otherwise there is no loss-history adjustment"; compute `loss_history_pct`.
- Demonstrated consequence: the tier value 0 % is what the ladder gives an excess policy that just paid its own layer, which no excess underwriter publishes. The seeded world of task 1 shows it:
  - Policy EXF-4472019 paid 265,000.00 building (`excess_claims` 964cde48, 2026-02-18) and LOU (dc29091e, 23cd6e23).
  - Its 2026-07-01 renewal is booked at 1,855.60 (`excess_billing` 59012e6b).
  - That figure is exactly P1's formula with 0 % loss history, −7 % HomeFlood account credit, −3 % tenure and −2 % early pay: 2,200 × 1.0 × 0.85 × 0.88 + 210 = 1,855.60. In other words, a discount after a quarter-million-dollar layer loss.
- Bears on: task 0, whose computation uses this ladder and whose only strictly multi-source factor it is.

**F-2 — SOURCE-FACTOR RED (unreal ladder): P4 `relocation_allowance`**
- Symptom: an LOU (additional living expense) claim payment is increased by 2,500 / 1,250 when the insured holds an active Tidemark HomeFlood policy on another home that took effect within 30 / 90 days of the sale closing.
- Evidence: P4 rule, "A relocation allowance of 2,500 is added where the insured holds an active Tidemark HomeFlood policy on another home ..."; compute `relocation_allowance`.
- Demonstrated consequence: these tier values are cash paid on a flood claim conditioned on buying another policy from the same insurer. That is not a loss-of-use expense, and it is the kind of inducement state unfair-trade-practice and anti-rebating statutes prohibit. No flood carrier publishes it.
- Bears on: task 1 (its gold LOU payment).

**F-3 — SOURCE-FACTOR RED (condition universal to the write): P3 `sale_minimum_waiver`**
- Symptom: tiers 1 and 2 require "the Tidemark HomeFlood policy on the home was cancelled for the sale". P3's own scope sentence admits only such customers: "A cancellation ... because the insured home was sold, where the Tidemark HomeFlood policy on the same home has been cancelled for that sale, is signed by the named insured, and its returned premium is figured under this rule". `sale_closing` is itself read from that cancelled HomeFlood.
- Demonstrated consequence: that compound part holds of every customer who reaches this write. The "multi-source" and "cross-difficulty homeflood" character of the factor is hollow, and the ladder is a one-source renewal count (≥3 / 1–2 / 0). The "HomeFlood not cancelled for the sale" branch of the fall-through is unreachable.
- Bears on: task 1.

**F-4 — SOURCE-POLICY RED (undeclared override): P4 due date**
- Base `excess_claim_intake_pol`: "Payment is due within claim_payment_days calendar days after the later of the agreed proof of loss and the underlying settlement record."
- P4 rule: "where the latest adjuster report is a SUPPLEMENTAL report the payment is due the tier's claim-payment days after that report; where it is a FINAL report and a proof of loss for loss of use is on file, the payment is due the tier's claim-payment days after the later of that proof of loss and the report; otherwise no interest runs."
- The two set different due dates for the same LOU payment. P4's `base_policy_refs`/`overwrite` name only `excess_claim_settlement`, so the base sentence stays in force and is rendered with P4.
- Bears on: task 1, where days late and interest are scored inside `payment_amount` (demonstration in 1.md).

**F-5 — SOURCE-POLICY RED (undeclared override): P3 paid-claim bar**
- Base `excess_cancellation_refund`: "When no_refund_after_paid_claim is true and a claim with a date of loss in the term has a net payment above zero (excess_msr_term_claims_paid above zero), nothing is returned."
- P3 rule: "Where a claim with a date of loss on or after the term start carries a claim payment, nothing is returned." P3's compute is `latest_paid_loss_date` over `excess_claim_paid` rows with voids ignored.
- Same situation, different conclusions: a claim with a current-term date of loss whose only payment was voided in full returns premium under base (net 0) and nothing under P3. None of P3's three `overwrite` entries names this sentence.
- Bears on: no task world here; task 1 has no excess voids and its loss predates the term. Charter defect.

**F-6 — SOURCE-POLICY RED (rule/compute scope divergence; decoy-guard class)**
In each case the rule confines a read to the same home, the same claim or the policy in question, and the compute does not.

Rule says "on the home", compute is customer-wide:
- (a) P1 `primary_paid_recent`: `XCOUNT('dwelling','dwelling_claims',...)` counts every Tidemark NFIP policy of the customer, but the rule says "the Tidemark NFIP Dwelling Form policy on the home".
- (b) P1 `nfip_cert_lowest`, `nfip_cert_bfe`, `nfip_cert_age_months` (four XLATESTs): customer-wide, but the rule says "on the same home". The four separate XLATESTs can also mix two certificates sharing a recorded_date.
- (c) P2 `last_primary_payment`: customer-wide, but the rule says "on the Tidemark NFIP Dwelling Form policy on the home".

Rule is itself unconfined (realism):
- (d) P4 `homeflood_lou_paid`: rule and compute agree on "the Tidemark HomeFlood claim file of the insured", so LOU paid on another home or another loss would be offset. The rule itself is unconfined.

Rule says "of the claim", compute is policy-wide:
- (e) P4 `date_of_loss`, `report_incurred`, `report_date`, `report_kind`, `lou_proof_date`, `prior_lou_paid`: policy-wide LATEST/SUM, but the rule says "the latest adjuster report of the claim" and "already issued on the claim". A second claim on the policy changes every one of them.

First-match reads (CFIELD/CPARAM return the first matching holding):
- (f) P3 `primary_cancel_reason` and `homeflood_term_end`: `CFIELD` by address only, with no status/reason filter. A second HomeFlood row at the address (an earlier expired or otherwise-cancelled policy) is first-match. `removed_days` tier 2 then also applies whenever the underlying is any private primary and any HomeFlood row exists at the address, although the rule requires "the underlying is a Tidemark HomeFlood policy".
- (g) P4 `homeflood_lou_limit`: `CPARAM` by address only, first match.
- (h) P4 `other_home_address` and `other_home_start`: the first active HomeFlood of the customer. A customer with two active HomeFlood policies on other homes gets an arbitrary one. The rule is existential over "an active ... policy on another home".

- Demonstration: a customer with a second Tidemark NFIP policy on another home paid within 12 months reaches tier "20 %" in P2 and "10 % or 25 %" in P1 under the compute, but "nothing" under the rule. The same pattern holds for each member.
- Bears on: no seeded decoy in either task world. Charter defect.

**Observations** (no consequence demonstrated)
- O-1 to O-11 are as cited above.
- O-12: P1 rule names both "the elevation multiplier" (baseline, one without a policy-record certificate) and "the renewal elevation multiplier" (NFIP fallback), while the assembly sentence uses "the elevation multiplier". "Instead" makes the override readable, but the two names drift.

## closing_checklist
Not closed. See `## closing_status` appended after the reveals.

## closing_status
Written after both reveals (2026-10-15T22:31Z). The charter-global section above was written before them and is unchanged.

The difficulty is **not closed**. Not every task file carries PASS on all four relationships:
- `0.md`: SOURCE-FACTOR RED (consequence of F-1).
- `1.md`: SOURCE-POLICY RED (F-4) and SOURCE-FACTOR RED (F-2, F-3).

Checklist state:
- Audit files correspond one-to-one with tasks 0 and 1, and `_difficulty.md` sits alongside them. This is revision 1.
- Scopes are pairwise disjoint and jointly complete:
  - task 0 = {excess_ext_renewal_term_premium, excess_ext_limit_increase_premium}
  - task 1 = {excess_ext_loss_of_use_payment, excess_ext_sale_cancellation_return}
  - The tools are disjoint, and each has an independent frozen uuid8.
- Trees: each has 1 prerequisite problem, 1 value_input edge and an owner=user root, with no cycle. The difficulty graph is a DAG.
- Factors:
  - Every factor bears weight on its task's world.
  - Every baseline is honest and gives a definite number different from gold (1,795.00 / 186.36 / 70,530.00 / 1,391.70).
  - Ladders F-1 and F-2 are unreal. F-3 carries a universal conjunct.
  - Task 0 has no surviving multi-source factor.
- Gates were not re-run on a final form, because there is no final form yet.

The six charter-wide REDs to be closed are F-1, F-2, F-3, F-4, F-5 and F-6. Observations O-1 to O-12 are not grounds for rework.


**timestamp_correction (appended after the reveal; frozen text left untouched):** the freeze times in the header (22:27Z / 22:33Z / 22:37Z) were estimated by hand and are wrong. The wall clock read 2026-10-15T22:26:55Z when the audit directory was created. It read 22:30:27Z when the sha256 of all three frozen files was taken (`_difficulty.md` d1aa30823f9f8d92, `0.md` 562375c60711c6bf, `1.md` 80619080327d210c). The GT of both tasks was first opened in the command that followed that hash. So the order was: all three files written and frozen, then hashed, then the reveal. The blind derivations stand.

task0=SOURCE-FACTOR RED task1=SOURCE-POLICY+SOURCE-FACTOR RED
charter=F-1,F-2,F-3,F-4,F-5,F-6

## revision_2

### charter_global_frozen (revision_2)
- Re-audit round 2. This section was written before any round-2 GT was read. Revision 1 above is left untouched.
- Gate first: the last line of `tasks/excess_flood_layering/worklog.md` reads `REWORK round 2: gates 8/8 green`.
- `/tmp/erl0065_coord/snapshot.sh excess_flood_layering 2` (2026-10-15T22:56:34Z):
  - extended, task_tools, replay, solvability, compute, grounding and cross_fire are all OK.
  - Traceability misses only the unlock tool name (pre-render). validate_scenario reports `documents: 0` (pre-render).
- Hashes:
  - `excess.extended.yaml` **bb356cf43c4ccb9b** (changed from ae9a39e8268addb7), so every charter-global section is re-derived in full below.
  - `task_tools.py` 8c315e853830b65a (unchanged), so **action_binding_and_uuids is carried forward from revision 1 on the unchanged hash**.
  - Masked views: 0.json 50c0850f9e0df46e, 1.json eda41b7bf1af1b6b → 3a5b25febd25f08b. Both changed.
- Base copy: lines 1–1052 are still byte-identical to `blueprint/products/excess.yaml`.
- Read: the charter, task_tools.py, the masked views, blueprint/ (homeflood.yaml settlement rule), the `## REWORK round 2 claims` section of the worklog (item ids and claims only), and `audits/XF_recipe.md`.
- Mechanical sweep (scratch script):
  - All `compute_basis` quotations are verbatim in their rules. No binding lacks a basis entry, and no basis entry is orphaned.
  - Every baseline sentence is in its rule.
  - Every `replaced_by` is verbatim in its rule (P1 1, P2 2, P3 4, P4 2).
  - Both prerequisite sources are verbatim, in state form.
  - No factor binding is shared between two factors.
- contamination_disclosure: I read the round-1 GT of both tasks during revision 1, after the revision-1 freeze. Its figures agreed with my revision-1 blind derivation. The revision-2 derivations below are recomputed from the revised charter and worlds. Every round-2 scored figure differs from round 1 (the worlds and charter changed), so nothing could be copied, but the shape of the gold sequence (reads, unlock/call pairs) is known from round 1.

### closure of round-1 REDs

**F-1 — closed.**
- P1's ladder is now:
  - +25 % where "at least one layer payment or two or more primary payments stand";
  - +10 % where "no layer payment and exactly one primary payment stands";
  - else 0.
- Primary payments are confined to "building payments on the claim file of the NFIP policy of the home or dwelling payments on the claim file of the HomeFlood policy of the home". A layer loss now draws the highest surcharge, and a private primary's losses are counted.
- Multi-source: tier 1 is a disjunction and tier 2 a conjunction over distinct records.
- The seeded task-1 renewal history was re-derived under it (1.md).

**F-2 — closed.**
- The relocation allowance is removed.
- The new `loss_severity_allowance` (2,500 / 1,000 / 0 by the FINAL whole dwelling loss as a share of RCV: ≥40 % / 20–40 % / below) is a scheduled moving-and-storage allowance inside the LOU payable. It is capped and netted against payments already issued. Realistic: ALE moving and storage on a severe loss.

**F-3 — closed.**
- `tenure_minimum_waiver`:
  - 0 for ≥3 renewals and no layer claim payment in 12 months;
  - 10 % for ≥3 renewals with such a payment;
  - else the tier minimum.
- No conjunct is universal to P3's scope. It is multi-source (billing renewals × claim file).

**F-4 — closed.**
- `excess_claim_intake_pol` was added to P4's refs. The due-date sentence is declared superseded, with a scoped `replaced_by` ("For a loss-of-use payment figured under this rule, and only for such a payment ... building and personal property payments remain under the base due-date sentence").

**F-5 — closed as a declaration.**
- The base bar sentence is declared superseded with a scoped `replaced_by`. The compute now nets voids on the latest-DOL paid claim.
- Residual observation O-13: the new rule reads only "the paid claim with the latest date of loss". A current-term claim paid earlier escapes the bar when a later current-term claim's only payment was voided. This is declared, a rare edge, and not a factor ladder.

**F-6 — class closed.** Member by member:
- (a), (b) — "the NFIP policy of the home". The plain shared binding `home_nfip_id` (dwelling in force at the address) filters every X read; `home_homeflood_id` is likewise plain.
- (c) — P2 `last_primary_payment` uses `dwelling_policy_id=home_nfip_id`.
- (d) — the HomeFlood offset is filtered to `underlying_claim_no`.
- (e) — `claim_in_hand` (the claim carrying the latest adjuster report) filters every P4 claim read. The rule defines it: "The claim is the claim of the policy that carries the latest adjuster report".
- (f) — `homeflood_term_end` reads by `policy_number=F('underlying_policy_number')`, matching the rule's "the underlying policy number on the policy record is that of a Tidemark HomeFlood policy". `primary_cancel_reason` is removed.
- (g) — `CPARAM` reads by policy number.
- (h) — removed with F-2.
- Remaining reads swept: `sale_closing` (address + PROPERTY_SOLD), `declared_expiry`, `underlying_dwelling_limit`, `booked_term_premium`, `latest_lou_payment`, `layer_payments_recent`, `latest_loss_in_file`, `renewal_paid_on`. Each reads what its rule names. Residual tie-edges are observation O-14: `latest_paid_claim` on equal dates of loss, and the four certificate XLATESTs on an equal recorded_date.

**Observations claimed fixed (verified).**
- O-2 / O-4: the E1 sentence now reads "from that term's start up to, but not including, its end", and the condition matches without the extra billing conjunct.
- O-3: the E2 condition now says "dated after that report".
- O-5: `replaced_by` names "the underlying offset this rule sets".
- O-6: the flat window now also requires "no claim on the policy having a date of loss on or after the term start". This addresses the adverse-selection concern.
- O-9: the reads lists are complete.
- O-12: the single name "the elevation multiplier" is used throughout.
- O-1, O-7, O-8 and O-11 are unchanged, as observations.

### re-derived charter-global checks (revision_2)

**policy_conflict_scan**
- Unchanged in shape: four policies, four tools, disjoint triggers.
- New shared reads:
  - P3 `layer_payments_recent` counts every `excess_claim_paid`, including the payment P4 writes. The two read the same ledger in the same direction, so there is no conflict.
  - The P3 and P4 `sale_closing` expressions are still identical.
- Scope partition {P1,P2} / {P3,P4} still holds.

**rule_compute_equivalence**
- The mechanical sweep is clean, as above.
- Back-sweep:
  - P1: the loss ladder matches the rule. Building/dwelling coverage filters are stated in the rule ("building payments ... dwelling payments").
  - P2: `charged_share` tier 1 adds `latest_loss_in_file`, as stated.
  - P3: the floor ladder, paid-claim bar netting and HomeFlood term-end read match the rule.
  - P4: order fixed — "shares/cuts multiply; deductions then subtracted, never below nothing; every allowance then added; the limit then caps; payments already issued subtracted after the cap; interest added last". This equals `MN(lou_limit, MX(0, …−offset)+allowance) − prior`, then interest.
- Rounding is unchanged and no tie occurs on either world.

**prerequisite_graph / prerequisite_sentences**
- E1 and E2 are still state form and verbatim. Each condition now equals its sentence. Each is still resolved by exactly one write (book_excess_renewal / pay_excess_loss_of_use).
- Acyclic. No authoring-viewpoint wording.

**override_declarations**
- P1 and P2: as in revision 1. P2's `replaced_by` now carries the claim-file clause and names its scope.
- P3: four declared overwrites, each scoped and naming "every other cancellation remains under the base cancellation rule".
- P4: two declared overwrites. No undeclared departure was found in a sentence-by-sentence pass over excess_claim_settlement, excess_claim_intake_pol and excess_cancellation_refund.

**factor_ladders**
- P1: 6 factors (5 Pm, 1 M). `renewal_loss_history` is multi-source and realistic.
  - Observation O-15: the tiers count primary *payments*, not claims. This mirrors the NFIP repetitive-loss "two or more claim payments" convention, so it is not unreal, but a supplemental building payment on one claim reaches tier 1.
- P2: 6 factors (4 Pm, 2 M). Unchanged except signing_window tier 1.
- P3: 5 factors (3 Pm, 2 M). `tenure_minimum_waiver` is multi-source.
- P4: 6 factors (3 Pm, 3 M). **`primary_lou_offset` tiers 1 and 2 coincide (N-1, below).** The others are real.
  - Observation O-16: `displacement_period_end` and `backdating_limit` decide their tiers from the HomeFlood sale record but are labelled `cross_difficulty: null`.

### findings (revision_2)

**N-1 — SOURCE-FACTOR RED (two tiers select the same value): P4 `primary_lou_offset`**
- New in round 2, introduced by the O-10 rework.
- Rule: "where that HomeFlood policy's loss-of-use payments on the underlying claim number recorded at first notice of the claim, net of voided payments, are at or above the loss-of-use limit of its tier, the offset is those payments; where they are below that limit, the offset is that limit".
- Compute: `(homeflood_lou_paid if homeflood_lou_paid >= homeflood_lou_limit else homeflood_lou_limit)`, which is max(paid, limit).
- The HomeFlood base settlement rule (`blueprint/products/homeflood.yaml`) pays "Loss of use ... as incurred up to loss_of_use_limit", with each new payment the payable "less what has already been paid net of voids on that claim and coverage". So net LOU paid on one claim never exceeds the limit that governed the claim. Tier 1 is reachable only at paid = limit, where it selects the limit, which is tier 2's value.
- The only way tier 1 yields a different figure is when the HomeFlood's current tier limit, which is what `CPARAM` reads, falls below what was paid under its tier at the date of loss. That is a tier change after the loss, which reads a limit that did not govern the claim.
- Demonstrated: in task 1, paid 50,000 = HomeFlood Premier limit 50,000. Tier 1 is taken and gives 50,000, and tier 2 gives 50,000. The ladder has two real outcomes (limit / 0), not three, and its `method` split between "subtract those payments" and "subtract the limit" is the same figure.
- Bears on: task 1.

task-level verdicts follow under `## closing_status (revision_2)` after the reveal.

## closing_status (revision_2)
Written after the round-2 reveals (2026-10-15T23:02Z). The revision_2 charter-global section above was frozen before them (hash 7dfcf04801cc3483).

Round-1 REDs:
- F-1, F-2, F-3, F-4 and F-6: closed, each across its whole class. Remaining members listed: none. Tie-edges are observation O-14.
- F-5: closed as a declared override (residual observation O-13).

Regressions: none. Task 0's figures moved only with its world (payment date) and charter (loss ladder). Task 1's moved with its world (2,500 payment, renewal 2,323.10) and charter (allowance, waiver). Every new figure is re-derived and agrees with GT.

New: **N-1** (P4 `primary_lou_offset` tiers 1 and 2 coincide on every charter-producible world). Introduced by the O-10 rework.

XF_recipe classes re-checked:
- A1–7: N-1 is the only failure (A6).
- B8–11: clean.
- C12: clean, with probes where seeded.
- C13: E1/E2 sentence = condition, unmet at the opening.
- D14: every overwrite is scoped.
- E15: seeds re-derive under their charters.
- E16: realism. Observations O-15 and O-16 only.
- F17: one stale proof sentence, the N-1 pairwise row in task 1's design_rationale.

The difficulty is not closed. Task 1 still carries a SOURCE-FACTOR RED.

VERDICT revision_2: task0=PASS task1=SOURCE-FACTOR RED
charter=N-1

## revision_3

### charter_global_frozen (revision_3)
- Re-audit round 3. Written before any round-3 GT was read. Revisions 1 and 2 are left untouched.
- Gate first: the worklog's last line reads `REWORK round 3: gates 8/8 green`.
- `snapshot.sh excess_flood_layering 3` (2026-10-16T05:57:50Z): all gates OK. The only misses are pre-render: the unlock tool-name traceability miss and validate_scenario `documents: 0`.
- Hashes:
  - Charter **bd3760f5cd646ac6** (changed from bb356cf43c4ccb9b).
  - task_tools 8c315e853830b65a (unchanged, so action_binding_and_uuids carries forward).
  - Masked views: 0.json 50c0850f9e0df46e (unchanged, so task 0's world is the round-2 world); 1.json **06efc2524908538c** (changed).
- Base copy: still byte-identical.
- Read: the charter, the masked views, the `## REWORK round 3 claims` section (item ids only), and `audits/XF_recipe.md`.
- contamination_disclosure: round-1 and round-2 GT of both tasks were read in earlier revisions, after their freezes. The round-3 figures below are recomputed with the charter's compute on the round-3 masked views.

### re-derived charter-global checks (revision_3)
**Scope of change.**
- P1 to P3 start at the same lines as in round 2 (1055 / 1520 / 1965) and end at 2339.
- P4 (from 2340) is 24 lines shorter.
- P1 to P3 recompute to the identical round-2 figures and sensitivities on task 0's unchanged world.

**Mechanical sweep (scratch script).**
- All `compute_basis` quotations of all four policies are verbatim in their rules. No binding lacks a basis entry, and none is orphaned.
- Every baseline sentence is in its rule.
- Every `replaced_by` is verbatim (1 / 2 / 4 / 2).
- Prerequisite sources E1 and E2 are verbatim, in state form, with conditions equal to their sentences (as in round 2).

**P4 offset (the N-1 subject).**
- Rule: "The underlying offset keeps the excess layer above the primary policy's own loss-of-use cover: where the underlying policy number on the policy record is that of a Tidemark HomeFlood policy, the offset is the loss-of-use limit of that HomeFlood policy's tier; where the underlying is a private primary policy of another carrier, the offset is 10 percent of the underlying dwelling limit on the policy record; and otherwise, for an underlying NFIP Dwelling Form policy, which carries no loss-of-use cover, there is no underlying offset and loss of use is paid from the first dollar."
- Compute: `homeflood_lou_limit if homeflood_lou_limit != None else ((F('underlying_building_limit') * K('other_carrier_lou_share')) if F('underlying_type') == 'PRIVATE_PRIMARY' else 0)`, with `homeflood_lou_limit = CPARAM('homeflood','loss_of_use_limit', policy_number=F('underlying_policy_number'))`.
- Rule and compute are equivalent, and the ladder's three methods are each stated.
- Realism: the excess attaches above the primary's own ALE cover. The other-carrier tier is a deemed underlying ALE (10 % of the dwelling limit, since the declarations on file carry no ALE limit). NFIP carries no ALE, which is true of the SFIP Dwelling Form. Realistic.
- **N-1 closed.** The three tiers select distinct values on charter-producible worlds. The tier-1 limit runs 10,000 to 100,000 for dwelling-eligible HomeFlood tiers. Tier 2 is 10 % of an underlying dwelling limit, which is at least 250,000 by the attachment minimum, so at least 25,000. Tier 3 is 0. The overlap observation is O-17.
- `cross_category` now reads only HomeFlood holding fields (policy_number, address, cancellation reason/date, LOU limit). The reads list is complete.

**Class sweep (XF A6, tiers coinciding on the reachable domain), whole charter.**
- P1: loss 25/10/0; account −7/−4/0; occupancy +12/−3/0; tenure −6/−3/0; early −4/−2/0; certificate own-EC / NFIP-EC / 1. All distinct.
- P2: signing 1 / 0 / standard share; rate derivation three formulas on disjoint conditions (contents present vs absent); relativity 0.8/0.9/1; recency 20/10/0; repeat 15/7.5/0; zone 15/5/0. All distinct.
- P3: backdating three anchors; cutoff declarations / HomeFlood record / none (tier 2 reachable when the declarations on file are stale against the HomeFlood record); waiver 0/10 %/tier minimum; retention 1/0.5/0; charge 100/50/0. All distinct.
- P4: housing share 0.8/0.9/1; period sale / max-months / none; offset as above; allowance 2,500/1,000/0; interest anchor three anchors; rate 10/8/0. All distinct.
- **Remaining members: none.**
- O-17 (observation, partial value overlap, not a coinciding tier): a HomeFlood Essential underlying (LOU limit 0) gives tier 1 the value 0, the same as tier 3. That is coherent, because Essential carries no LOU cover, and holds for one variant only, not across the domain.

**Other XF classes (round-2 conclusions re-verified for P4; unchanged for P1–P3).**
- A2/A3 assembly and order sentence are unchanged and generic.
- A4/A5: no factor reads another factor's binding. `homeflood_lou_limit` is the factor's own binding, and `claim_in_hand` is plain.
- B8–B11: clean.
- C12: all P4 reads are confined to `claim_in_hand`. The offset reads by the underlying policy number.
- D14: overwrites unchanged and scoped. The settlement `replaced_by` says "less the underlying offset this rule sets", consistent with the new ladder.
- E16: realistic.
- F17: verified after the reveal (task files).

**Counts.** P4 has 6 factors (3 Pm, 3 M), all real. The P1–P3 counts are as in revision 2.

### findings (revision_3)
- N-1: **closed** (not reworded; the method set changed).
- No new charter-wide RED.
- Observations: O-17 (above) and O-18 (task 1 seed, see 1.md).

## closing_checklist (revision_3)
Written after the round-3 reveals (2026-10-16T06:00Z). The revision_3 charter-global section was frozen before them (e57abb5084498ea8).

- **Audit files.** `0.md` and `1.md` correspond one-to-one with the tasks, alongside `_difficulty.md`. Revisions 1, 2 and 3 are preserved and appended in order. Each file's revision_3 comparison carries PASS on all four relationships.
- **Coverage and scopes.**
  - All four extended policies are covered.
  - Scopes are pairwise disjoint: task 0 = {renewal, increase}, task 1 = {LOU payment, sale cancellation}, each tree including its root and its prerequisite.
  - Task tools and GT are closed.
  - The four uuid8s (30706efc, cddf0413, f5cb8480, a26754a5) are independent and frozen.
- **Trees.**
  - Each tree has 1 prerequisite problem, 1 value_input edge, an owner=user root and no cycle.
  - The difficulty graph (P2←P1, P3←P4) is a DAG with no cross-task reference.
  - Both edges are unmet at the opening and bear weight (0.00 vs 175.93; 1,669.79 vs 1,588.38).
- **Factors.**
  - P1 has 6, P2 6, P3 5 and P4 6 factors, each with ≥2 parameter and ≥1 method factors.
  - Every ladder has 3 distinct tiers stated in full in its rule, with conditions and outcomes a flood carrier holds.
  - Every factor bears weight against an honest baseline. The all-baseline figures (1,795.00 / 182.56 / 68,030.00 / 1,742.32) are definite and differ from gold.
  - Per task: multi-source ✓ (task 0 `renewal_loss_history`; task 1 `displacement_period_end`, `tenure_minimum_waiver`). Cross-difficulty ✓ (task 0 dwelling; task 1 homeflood).
- **Gates.** Re-run on the final form by `snapshot.sh excess_flood_layering 3` (2026-10-16T05:57:50Z): extended, task_tools, replay, solvability, compute, grounding and cross_fire are all OK. Traceability (unlock tool name) and validate_scenario (`documents: 0`) are pre-render only.
- **Round-2 RED N-1 / T1-4:** closed. No new defect. No regression: every figure that did not move with an intended change is identical.
- **Observations carried** (not grounds for rework): O-1, O-7, O-8, O-11, O-13 to O-18.

The difficulty passes the source-layer audit.

VERDICT revision_3: task0=PASS task1=PASS
charter=CLEAN

## revision_4

### charter_global_frozen (revision_4)
- Re-audit round 4. Written before any round-4 GT was read. Revisions 1 to 3 are left untouched.
- Gate first: the worklog reads `REWORK round 4: gates 8/8 green`.
- `snapshot.sh excess_flood_layering 4` (2026-10-16T14:13:20Z): all gates OK. Traceability misses only the unlock tool name. validate_scenario reports `documents: 36`, with the KB rendering under way.
- Hashes:
  - Charter **e9fa3167629d1c0d** (changed from bd3760f5).
  - task_tools 8c315e853830b65a (unchanged, so action_binding_and_uuids carries forward).
  - Masked views 0.json 50c0850f9e0df46e and 1.json 06efc2524908538c, both **unchanged** since round 3.
- Base copy: byte-identical.
- Also read, as the brief requires: `audits/render_source/excess_flood_layering/render_r1.md`, the renderer's source scan. It carries charter quotations only, no scored value.
- **Disclosure of my own misses.** My revision_3 passed the charter while the renderer later found defects that were already present then:
  - F1: interest factors zeroing each other.
  - F2/F3: "more than N months/years" against the whole-month count.
  - F4: an absent-declarations reading.
  - F5: a tier blocked by its own prerequisite. I had recorded it only as O-4 / O-19-style notes.
  - F6: an undefined term.
  - F7: `replaced_by` tails that did not restate the retired base content (I checked scope naming only).
  - N1/N2.
  
  This is a regression of my own verdict, recorded here. Revision 4 re-checks each class charter-wide with scripts and constructed probes.
- contamination_disclosure: GT of rounds 1–3 was read in earlier revisions after their freezes. The round-4 figures below are recomputed from the round-4 charter compute on the unchanged views.

### verification of the renderer's findings (revision_4)
**Mechanical sweep**
- `compute_basis` is verbatim in its rule for all four policies. No missing or orphaned basis.
- Every baseline sentence is in its rule.
- Every `replaced_by` is verbatim (1 / 2 / 4 / 2).
- Prerequisite sources are verbatim.
- No binding is shared between two factors.

**F1 — closed. Class: none remaining.**
- The baseline now states standard interest: "the yearly interest rate being 8 percent", with the due date "the tier's claim-payment days after the later of the latest proof of loss on the claim and the underlying settlement record of the claim".
- `claim_age_rate` now has tiers 10 / 9 / 8, and `interest_due_anchor` has the SUPPLEMENTAL / FINAL-with-proof / base anchors.
- On task 1 each factor alone changes the result: 12,610.27 and 11,891.35 against 11,898.50.
- Class sweep of every multiplied pair: P1 `adjusted_layer` (baselines 1 and 0 inside 1+…), P2 `full_term_charge`, P3 `lou_retained` (retention baseline 0, but `unexpired_cutoff` and `backdating_limit` still act alone through `returned_core`), P4 `lou_payable`. No factor is zeroed by another.

**F2 — closed. F3 — closed. Class: none remaining.**
- "the displacement months exceed the tier's maximum months" and "counted in whole months (twelve for each year)" now match MONTHS.
- Every other month or year comparison is stated in whole months (P1 loss window, P2 recency and repeat, P3 payment window, P4 claim age).
- The sale tier now requires the closing to fall on or after the loss, which the compute implements.

**F4 — closed. Class: none remaining.**
- The fallbacks are stated: the underlying dwelling limit on the record, and the term premium on the record.
- Absent-record reads swept charter-wide. Each absent case is stated in its rule: renewal payment, certificate, NFIP payment, NFIP zone, claims, declarations, HomeFlood term end, LOU payment, paid claim, FINAL report, proofs and settlement, HomeFlood tier.

**F5 — NOT fully closed. Remaining member: R4-3.**

**F6 — "scheduled ... charges" is now defined (closed). Remaining member of the undefined-term class: R4-2.**

**F7 — closed. Class: none remaining.**
- Every `replaced_by` now restates the retired base content for out-of-scope cases:
  - P1: base rating.
  - P2: waiting, and endorsement pro-rata.
  - P3: signed request, settlement-statement date, pro rata with minimum earned, paid-claim bar.
  - P4: due date for building and contents payments. The settlement tail says it covers every LOU payment.

**N2 — partly closed. Remaining member: R4-1.**

**N1 — the listed bindings were moved. Remaining members: R4-4.**

**Tie-break — closed.** Every rule ends with "Where two entries on a file share the date this rule reads them by, the one entered on the file first is read". That matches LATEST, which keeps the first-entered row on equal keys.

### findings (revision_4)
**R4-1 — SOURCE-POLICY RED (N2 class, remaining member): P1 void netting counted by the void's own date**
- Rule: "a payment later voided is taken off the count by its void".
- Compute: in-window paid rows **minus in-window void rows**, for both `primary_paid_recent` and `layer_paid_recent`.
- A void dated inside the 36-month window takes one payment off even when the payment it voids lies outside the window.
- Probe (task 0's world plus three dwelling rows on 7f147d3a, BUILDING, claim 4023-1001-9999):
  - paid 2023-10-10 (36 whole months before 2026-10-14, outside);
  - void 2023-10-20 (inside);
  - reissue 2023-10-20 (inside).
- Rule reading: the reissue plus 0f85493d are two unvoided primary payments, so +25 % and a renewal of **1,705.45**.
- Compute: 3 − 1 − … gives 1, so +10 % and **1,503.36**.

**R4-2 — SOURCE-POLICY RED (F6 class, remaining member; rule condition absent from compute): P4 interest anchor qualifier**
- Rule: "For a loss-of-use payment documented on a later report, the due date is instead the tier's claim-payment days after the latest adjuster report where that report is a SUPPLEMENTAL report, and ... where the latest report is a FINAL report and such a proof of loss is on file."
- "a later report" is undefined (later than the proof of loss and settlement record? than the first report? than the last payment?), and `days_late` ignores the qualifier entirely.
- Second reading: "later" means later than the base anchor (the preceding sentence). Take a SUPPLEMENTAL report dated before the underlying settlement record:
  - rule: the base due date (settlement + 30);
  - compute: report + 30.
  - The interest differs.
- Task 1 is not affected: its report (2026-09-04) postdates both anchors, so both readings agree.

**R4-3 — SOURCE-POLICY RED (F5 class, remaining member): the P2 short-term tier against E1**
- Tier: "for an increase signed when fewer than 60 days of the term remain, the increase takes effect after the standard waiting period and is charged a minimum share of 60 days over the days of the term".
- E1: "The additional premium for a limit increase is figured only once the policy record carries the term in which the increase takes effect, from that term's start up to, but not including, its end."
- With fewer than 30 days left, the waiting period ends after the term end, so E1 blocks the figure until the next term is on record. On that term, 60 days no longer remain and another tier applies. The tier's stated treatment can never apply on 0–29 days, yet the compute charges it.
- Probe: record term to 2026-11-03, signed 2026-10-14, 20 days left. The compute gives **32.50** (share 60/398), effective 2026-11-13, which is outside the recorded term that E1 requires.
- The same collision is present on task 0's opening world: 35.44 for an increase effective 2026-11-13 on a term ended 2026-10-01. E1 resolves it there (see 0.md).

**R4-4 — SOURCE-POLICY RED (N1 class, remaining members): plain bindings read by a single factor (P4)**
- `report_kind` is read only by `interest_due_anchor` (`days_late`).
- `displacement_months` is read only by `displacement_period_end` (`period_fraction`). `monthly_ratio_pct` recomputes `MX(1, MONTHS(...))` inline instead of reading it.
- Found by script over every plain binding of the charter. No other member.
- No scored figure moves.

**No other new defect.**
- XF A2–A7, B8–B11 (except R4-2), C12–C13 and D14 re-checked.
- E15: task 1's seeded LOU history re-derives under the round-4 interest baseline: 2,500 / 14,710 / 14,760, each with 0 days late.
- E16: realism. The 9 % middle rate and the base-anchor interest are company schedule.

## closing_status (revision_4)
Written after the round-4 reveals (2026-10-16T14:18Z). The revision_4 charter section above was frozen before them (0c508340881015d5).

**Correction to the frozen R4-1 probe line** (arithmetic typo; the frozen text is left untouched). The compute counts:
- 2 in-window BUILDING payments: the reissue of 2023-10-20 and 0f85493d of 2024-11-20;
- less 1 in-window void (2023-10-20);
- giving 1, hence +10 % and 1,503.36.

The paid row of 2023-10-10 is outside the window. The rule reading gives 2 and +25 %, hence 1,705.45. Both figures were produced by the charter's compute on the probe world.

**Status**
- Both tasks pass all four relationships. GT equals the blind derivation figure for figure, and nothing regressed in either task.
- Renderer findings F1, F2, F3, F4, F7 and the tie-break are closed, each across its class.
- F5, F6, N1 and N2 each keep one remaining member: R4-3, R4-2, R4-4 and R4-1 respectively.
- The brief requires remaining members of the renderer's classes to be reported as RED, so the charter is not clean.
- The difficulty is not closed; the closing checklist waits on these four.

VERDICT revision_4: task0=PASS task1=PASS
charter=R4-1,R4-2,R4-3,R4-4

## revision_5

### charter_global_frozen (revision_5)
- Re-audit round 5. Written before any round-5 GT was read. Revisions 1 to 4 are left untouched.
- Gate first: the worklog reads `REWORK round 5: gates 8/8 green`.
- `snapshot.sh excess_flood_layering 5`: all gates OK. Traceability misses only the unlock tool name. validate reports `documents: 36`.
- Hashes:
  - Charter **ca5001c2d9937429** (changed from e9fa3167).
  - task_tools 8c315e853830b65a (unchanged, carried forward).
  - Views 0.json 50c0850f9e0df46e and 1.json 06efc2524908538c (unchanged).
- Base copy: byte-identical.
- contamination_disclosure: the GT of rounds 1–4 was read in earlier revisions after their freezes. The round-5 figures are recomputed from the round-5 compute.

### round-4 REDs (revision_5)
**R4-1 — closed.**
- The rule now states the netting the compute performs: "each void of a claim payment posted in that same window takes one payment off the count".
- That is rule = compute for primary and layer payments alike.
- On the revision-4 probe world (a void of 2023-10-20 for a payment of 2023-10-10), the rule now also gives 1 payment and +10 %.

**R4-2 — closed.**
- The qualifier is gone. The rule reads: "The due date is instead the tier's claim-payment days after the latest adjuster report where that report is a SUPPLEMENTAL report, and ... where the latest report is a FINAL report and such a proof of loss is on file."
- That equals `days_late` and the ladder.

**R4-4 — closed.**
- A script over every plain binding of all four policies finds none read by exactly one factor.
- `report_kind` and `displacement_months` are now in their factors. `lou_charge` in P2 is now inside `rate_derivation`.
- No binding is shared between two factors.

**R4-3 — not closed at the boundary. See R5-1.**
- For fewer than 30 days left, the rule now says "nothing where that period ends on or after the term end, the increase then belonging to the next term".
  - That agrees with E1: the current term carries no charge, and the increase is figured on the next term once it is booked.
  - It is not a charge that E1 blocks.
  - The compute uses `MX(0, days_left − 30) / term_days`.

### render_r1 items stay closed (revision_5)
- F1: on task 1, interest_due_anchor 12,610.27 and claim_age_rate 11,891.35, each alone against 11,898.50.
- F2: the whole-month displacement sentence and the closing on or after the loss are both present.
- F3: "counted in whole months (twelve for each year)" is present.
- F4: both absent-record fallbacks are present.
- F6: the scheduled charges are defined.
- F7: every `replaced_by` restates the retired base content (all verbatim in the rules: P1 1, P2 2, P3 4, P4 2).
- N1: the script finds none.
- N2: stated as computed.
- Tie-break: extended to "or two policy records answer the same description, the one entered first is read", which matches CFIELD/CPARAM first-match.
- F5: see R5-1.
- Mechanical sweep: `compute_basis`, baseline and prerequisite text all verbatim; no orphans; all ladders have 3 tiers; counts unchanged (P1 6, P2 6, P3 5, P4 6).

### findings (revision_5)
**R5-1 — SOURCE-POLICY RED (F5 / R4-3 class, remaining boundary member): P2 short-term tier at exactly 30 days left**
- Tier: "for an increase signed when at least 30 but fewer than 60 days of the term remain, the increase takes effect after the standard waiting period and is charged a minimum share of 60 days over the days of the term". Compute: `(K('deferral_days') / term_days) if (days_left >= P('standard_waiting_days') and days_left < K('deferral_days'))`.
- With exactly 30 days left, the increase takes effect "at 12:01 a.m. on the day the tier's standard waiting period in calendar days after the signed request". That day **is** the term end.
- E1 says the additional premium is figured only once the policy record carries the term in which the increase takes effect, "from that term's start up to, but not including, its end". So the term end falls outside the recorded term and the figure cannot be made on it.
- The rule's own "otherwise" clause agrees: "nothing where that period ends on or after the term end, the increase then belonging to the next term".
- Probe (task 0's world, term end set to 2026-11-13, NOW 2026-10-14):
  - days_left 30;
  - the compute charges a share of 60/365, giving **35.44**, effective 2026-11-13, which is the term end;
  - by E1 and the "on or after the term end" clause the share is nothing and the increase belongs to the next term.
- Two passages give two conclusions in the same situation. With 31 days left (31.63, effective inside the term) and 29 days left (0.00) the passages agree.
- The rework's claim "(waiting period still ending inside the recorded term)" is false at 30.

**No other new defect.**
- XF A1–A7, B8–B11, C12, C13, D14, E15, E16 and F17 were re-checked with the scripts and probes above.
- Task 1's seeded LOU history still re-derives (2,500 / 14,710 / 14,760).

## closing_status (revision_5)
Written after the round-5 reveals (2026-10-16T15:24Z). The revision_5 charter section was frozen before them (8e271409cce06749).

- Both tasks pass all four relationships. GT equals the blind derivation figure for figure, with no regression. Task 0's skipped-renewal contrast moved from 35.44 back to 0.00, as the round-5 charter intends, and agrees with E1.
- R4-1, R4-2 and R4-4 are closed. R4-3 is closed for 0–29 and 31–59 days left.
- One boundary member of the same class remains: **R5-1**, at exactly 30 days left.
- Every render_r1 item stays closed.
- The difficulty is not closed while R5-1 stands.

VERDICT revision_5: task0=PASS task1=PASS
charter=R5-1

## revision_6

### charter_global_frozen (revision_6)
- Re-audit round 6. Written before any round-6 GT was read. Earlier revisions are left untouched.
- Gate first: `REWORK round 6: gates 8/8 green`.
- `snapshot.sh excess_flood_layering 6`: all gates OK. Traceability misses only the unlock tool name. validate reports `documents: 104`.
- Hashes:
  - Charter **02bbe3b323436230** (changed from ca5001c2).
  - task_tools 8c315e853830b65a (unchanged).
  - Views 0.json 50c0850f9e0df46e and 1.json 06efc2524908538c (unchanged).
- Base copy: byte-identical.
- contamination_disclosure: as in earlier revisions. The figures are recomputed from the round-6 compute.

### R5-1 (revision_6) — rule and compute closed, ladder not
- Rule: "for an increase signed when more than 30 but fewer than 60 days of the term remain ... is charged a minimum share of 60 days". The "otherwise" clause: "nothing where that period ends on or after the term end, the increase then belonging to the next term".
- Compute: `days_left > P('standard_waiting_days') and days_left < K('deferral_days')`.
- Probes on task 0's world (term end moved, NOW 2026-10-14):
  - 29 days left: 0.00;
  - **30 days left: 0.00** (in round 5 this was 35.44);
  - 31 days left: 31.63.
  - Rule, compute and E1 now agree.
- **But the `signing_window` ladder still reads "the increase is signed when at least 30 but fewer than 60 days of the term remain"** (see R6-1). The worklog claims the fix was made "in rule, ladder and compute".

### same-kind class (revision_6) — closed
Every read the reworker lists was checked against the compute.

**P1**
- `home_nfip_id` / `home_homeflood_id` use CFIELD by `policy_number=F('underlying_policy_number')` plus in_force / active.
- The account EXISTS and the occupancy CFIELD use the same key.
- The rule redefines "The NFIP policy of the home is the Tidemark NFIP Dwelling Form policy in force whose policy number is the underlying policy number on the policy record, and the HomeFlood policy of the home is the active Tidemark HomeFlood policy whose policy number is that underlying policy number". The account and occupancy sentences and the ladders now use those defined names.
- Certificates and claim counts are keyed by those ids. The renewal payment is keyed by term_start.
- Renewal and layer counts are policy-wide, as the rule says.

**P2**
- `home_nfip_id` and `nfip_zone` are keyed by the underlying policy number.
- The declarations are keyed by `underlying_policy_number` ("latest declarations received for the underlying policy number on the policy record").
- `booked_term_premium` is "the latest term premium item booked for the current term".

**P3**
- `sale_closing` is keyed by policy number plus PROPERTY_SOLD. The scope sentence is restated to "the Tidemark HomeFlood policy whose policy number is the underlying policy number".
- The declarations and the HomeFlood term end are keyed by policy number. The paid-claim bar is keyed by claim_number.

**P4**
- Every claim read is keyed by `claim_in_hand`. `sale_closing` is keyed as in P3. The LOU limit is read by policy number.

**Decoy probe (mine).** I added a second in-force NFIP policy at 418 Surfsong Rd with another number, zone VE and non-primary, entered first. The renewal stays at 1,503.36.

**Remaining members: none.**

### sweeps (revision_6)
- `compute_basis`, baseline, `replaced_by` (1 / 2 / 4 / 2) and prerequisite sources are all verbatim. No orphans. No binding is shared between factors.
- N1 script: no plain binding is read by a single factor.
- A ladder-against-rule phrase script (comparison word plus number) flags only `signing_window` "at least 30" (R6-1). The backdating ladder's "more than 90" is the rule's "received later" after "31 to 90 days", which is equivalent, and the compute uses `> 90`.
- Every render_r1 item and every earlier RED stays closed: F1–F4, F6, F7, N1, N2, tie-break, R4-1, R4-2, R4-4.
- Task 1's seed history still gives 2,500 / 14,710 / 14,760.

### findings (revision_6)
**R6-1 — SOURCE-POLICY RED (R5-1 class, remaining member; a ladder tier absent from the rule/compute face)**
- `factors[signing_window].ladder[1].when` says "the increase is signed when at least 30 but fewer than 60 days of the term remain". The rule and compute say "more than 30" / `days_left > 30`.
- At exactly 30 days left:
  - ladder face: the 60-day minimum share, which would be 35.44 on the probe;
  - rule, compute and E1: nothing, 0.00.
- The tier sets in the ladder and in the rule/compute differ. The factor document is rendered from that ladder.

## closing_status (revision_6)
Written after the round-6 reveals (2026-10-16T16:33Z). The revision_6 charter section was frozen before them (862662a9d0b96398).

- Both tasks pass all four relationships. GT equals the blind derivation figure for figure, with no regression.
- The same-kind class is closed charter-wide.
- R5-1 is closed in the rule and compute. One member remains: **R6-1**, the `signing_window` ladder text "at least 30" against the rule/compute "more than 30".
- Every render_r1 item and every earlier RED stays closed.
- The difficulty is not closed while R6-1 stands.

VERDICT revision_6: task0=PASS task1=PASS
charter=R6-1

## revision_7

### charter_global_frozen (revision_7)
- Re-audit round 7. Written before any round-7 GT was read. Earlier revisions are left untouched.
- Gate first: `REWORK round 7: gates 8/8 green`.
- `snapshot.sh excess_flood_layering 7`: all gates OK. Traceability misses only the unlock tool name. validate reports `documents: 104`.
- Hashes:
  - Charter **c114c4ae6417b15d** (changed from 02bbe3b3).
  - task_tools 8c315e853830b65a (unchanged).
  - Views 0.json 50c0850f9e0df46e and 1.json 06efc2524908538c (unchanged).
- Base copy: byte-identical.
- contamination_disclosure: as in earlier revisions. The figures are recomputed from the round-7 compute.

### R6-1 (revision_7) — closed
- `signing_window.ladder[1].when` now reads "the increase is signed when more than 30 but fewer than 60 days of the term remain". That is the same tier set as the rule ("more than 30 but fewer than 60 days of the term remain") and the compute (`days_left > 30 and days_left < 60`).
- Probes on task 0's world (term end moved, NOW 2026-10-14):
  - 29 days left: 0.00;
  - 30 days left: 0.00;
  - 31 days left: 31.63.
  - Rule, ladder, compute and E1 agree.
- Class sweep (ladder comparison phrases against the rule, all four policies): the only hit is the backdating "more than 90 days". It is equivalent wording: the rule says "31 to 90 days ... received later", and the compute uses `> 90`.

### sweeps (revision_7)
- `compute_basis`, baseline, `replaced_by` (1 / 2 / 4 / 2) and prerequisite sources are all verbatim. No orphans. No shared or single-factor plain bindings. All ladders have 3 tiers.
- The same-kind decoy probe (a second in-force NFIP policy at the address, another number, VE, non-primary, entered first) still leaves the renewal at 1,503.36.
- Every render_r1 item and every earlier RED stays closed: F1–F4, F6, F7, N1, N2, tie-break, R4-1, R4-2, R4-4, R5-1 and the same-kind class.
- Task 1's seed history still gives 2,500 / 14,710 / 14,760.

### findings (revision_7)
**R7-1 — SOURCE-FACTOR RED (unreal ladder; P2 `signing_window` short-term tier is not a minimum)**
- Present since round 4. **My revisions 4–6 missed it.**
- Rule: "for an increase signed when more than 30 but fewer than 60 days of the term remain, the increase takes effect after the standard waiting period and is charged a minimum share of 60 days over the days of the term; any other increase takes the share of the term counted from the end of the standard waiting period".
- With 60–89 days left, the "otherwise" tier charges 30–59 days, which is less than the 60-day "minimum" charged to an increase signed with only 31–59 days left. The charge falls as the remaining term grows across the 59/60 boundary.
- Probe on task 0's world with the same increase:
  - 59 days left: **29.60** (60 days charged);
  - 60 days left: **14.77** (30 days charged).
- No carrier publishes a minimum endorsement charge that binds only when fewer days remain and is undercut by the next tier. The tier condition ("fewer than 60 days remain") is not the quantity a minimum weighs (the days charged after the waiting period).
- Bears on: no task world here. Task 0 takes the flat tier after the renewal and the "nothing" clause on the opening world.

## closing_status (revision_7)
Written after the round-7 reveals (2026-10-16T16:55Z). The revision_7 charter section was frozen before them (8702e829210a9311).

- Both tasks pass all four relationships. GT equals the blind derivation figure for figure, with no regression.
- R6-1 is closed.
- Every render_r1 item and every earlier RED stays closed.
- One new charter RED: **R7-1**. The short-term tier's "minimum share of 60 days" is undercut by the next tier: 59 days left gives 29.60, while 60 days left gives 14.77. It has been present since round 4, and I missed it in revisions 4–6.
- The difficulty is not closed while R7-1 stands.

VERDICT revision_7: task0=PASS task1=PASS
charter=R7-1

## revision_8

### charter_global_frozen (revision_8)
- Re-audit round 8. Written before any round-8 GT was read. Earlier revisions are left untouched.
- Gate first: `REWORK round 8: gates 8/8 green`.
- `snapshot.sh excess_flood_layering 8`: all gates OK. Traceability misses only the unlock tool name. validate reports `documents: 104`.
- Hashes:
  - Charter **8b94d61670c1a143** (changed from c114c4ae).
  - task_tools 8c315e853830b65a (unchanged).
  - Views 0.json 50c0850f9e0df46e and 1.json 06efc2524908538c (unchanged).
- Base copy: byte-identical.
- contamination_disclosure: as in earlier revisions. The figures are recomputed from the round-8 compute.

### R7-1 (revision_8) — closed
- Rule: "any other increase takes effect after the standard waiting period and, where that period ends before the term end, is charged the share of the term counted from the end of that period, never less than a minimum share of 60 days over the days of the term; where that period ends on or after the term end the share is nothing, the increase then belonging to the next term."
- Compute: `(MX(K('deferral_days'), days_left - P('standard_waiting_days')) / term_days) if days_left > P('standard_waiting_days') else 0`.
- The `signing_window` ladder now has three tiers: flat / waiting-period share floored at 60 days / otherwise nothing. Its baseline is the unchanged `MX(0, days_left − 30) / term_days`, which is the fall-through value on the fall-through's domain.
- Rule, ladder and compute state the same tier set.
- Monotonicity scan (task 0's world, 25 to 129 days left, one probe per day): the days charged never fall as the remaining term grows.
  - 0 days at 25–30 days left;
  - 60 days at 31–90;
  - 61 at 91;
  - 90 at 120.
- The 59/60 discontinuity of revision 7 (60 days charged against 30) is gone.
- Class check: the other stated minimums (P1 "never less than the tier's minimum premium" as an `MX` floor on every tier; P3 "never more than the term premium less the minimum earned share" as an `MN` cap on every tier) bind on all tiers. **Remaining members: none.**
- The fall-through "nothing ... belonging to the next term" agrees with E1, as concluded in revision 5. It is the opening-world contrast of task 0.

### sweeps (revision_8)
- `compute_basis`, baseline, `replaced_by` (1 / 2 / 4 / 2) and prerequisite sources are all verbatim. No orphans. No shared or single-factor plain bindings. All ladders have 3 tiers.
- Ladder-against-rule phrases: only the equivalent backdating "more than 90".
- The same-kind decoy probe leaves the renewal at 1,503.36.
- Every render_r1 item and every earlier RED stays closed: F1–F7, N1, N2, tie-break, R4-1 to R4-4, R5-1, R6-1 and the same-kind class.
- Task 1's seed history still gives 2,500 / 14,710 / 14,760.

### findings (revision_8)
- R7-1 closed.
- No new defect.

## closing_checklist (revision_8)
Written after the round-8 reveals (2026-10-17T13:13Z). The revision_8 charter section was frozen before them (d4bb393ba647ec34).

- **Audit files.** `0.md` and `1.md` correspond one-to-one with the tasks, alongside `_difficulty.md`. Revisions 1 to 8 are preserved in order. Each file's revision_8 comparison carries PASS on all four relationships.
- **Coverage and scopes.**
  - All four extended policies are covered.
  - Scopes are pairwise disjoint: task 0 = {renewal, increase}, task 1 = {LOU payment, sale cancellation}.
  - Tools and GT are closed.
  - The uuid8s 30706efc, cddf0413, f5cb8480 and a26754a5 are independent and frozen.
- **Trees.**
  - Each tree has 1 prerequisite problem, 1 value_input edge, an owner=user root and no cycle.
  - The difficulty graph (P2←P1, P3←P4) is a DAG.
  - Both edges are unmet at the opening and bear weight (0.00 vs 175.93; 1,669.79 vs 1,588.38).
- **Factors.**
  - P1 has 6, P2 6, P3 5 and P4 6 factors, each with ≥2 parameter and ≥1 method factors.
  - Every ladder has 3 distinct tiers stated in full in its rule, and the ladder face equals the rule and compute.
  - Every factor bears weight against an honest baseline. The all-baseline figures (1,795.00 / 182.56 / 71,459.46 / 1,742.32) are definite and differ from gold.
  - Per task: multi-source ✓ and cross-difficulty ✓ (task 0 dwelling; task 1 homeflood).
- **Gates.** Re-run on the final form by `snapshot.sh excess_flood_layering 8`: extended, task_tools, replay, solvability, compute, grounding and cross_fire are all OK. Traceability misses only the unlock tool name.
- **Closed.** Every render_r1 item and every RED of revisions 1–7 (F-1 to F-6, N-1, R4-1 to R4-4, R5-1, R6-1, R7-1) and the same-kind class are closed. No regression.
- **Observations carried** (not grounds for rework): O-1, O-7, O-8, O-11, O-13 to O-18.

The difficulty passes the source-layer audit.

VERDICT revision_8: task0=PASS task1=PASS
charter=CLEAN

## revision_9

### charter_global_frozen (revision_9)
- Re-audit round 9. Written before any round-9 GT was read. Earlier revisions are left untouched.
- Gate first: `REWORK round 9: gates 8/8 green`.
- `snapshot.sh excess_flood_layering 9`: all gates OK, **including traceability** (KB published). validate reports `documents: 155`.
- Hashes:
  - Charter **1a06fa0f8f9beb85** (changed from 8b94d616).
  - task_tools 8c315e853830b65a (unchanged).
  - Views 0.json 50c0850f9e0df46e and 1.json 06efc2524908538c (unchanged).
- Base copy: byte-identical.
- Also read, as the brief requires: the SRC-1/SRC-2 and Observations sections of `audits/policy_kb/excess_flood_layering/kb_audit_report.md`. They carry no scored value I had not already derived. SRC-1 is out of scope (base, BLUEPRINT-KNOWN).
- contamination_disclosure: as in earlier revisions.

### SRC-2 (revision_9) — closed
- Old: "only their claim files and certificates are read". This contradicted the account (status) and occupancy (designation) reads.
- New: "of these two policies only their status, the NFIP policy's primary-residence designation, their claim payments and voided payments and the NFIP policy's applied Elevation Certificates are read".
- Checked against P1's compute reads of those two policies: the id by policy number plus status (`home_nfip_id`, `home_homeflood_id`, EXISTS), `primary_residence`, paid and voided BUILDING/DWELLING claim rows, and applied `dwelling_ec_received` rows. Rule and compute now agree.
- Class sweep: every rule sentence of the four policies that limits or describes reads was listed by script. The only other limiting sentence is P4's "every claim figure this rule reads is read from that claim's own entries". It holds: every claim read is keyed by `claim_in_hand`, and the HomeFlood tier limit and sale record are not claim figures. **Remaining members: none.**
- The KB documents that carry the old sentence (account relationship, loss history) need a re-render. That is a render matter, outside this audit's write domain.

### sweeps (revision_9)
- `compute_basis`, baseline, `replaced_by` (1 / 2 / 4 / 2) and prerequisite sources are all verbatim. No orphans. No shared or single-factor plain bindings. All ladders have 3 tiers.
- Ladder-against-rule phrases: only the equivalent backdating "more than 90".
- Increase charge monotone over 25–129 days left. The same-kind decoy leaves the renewal at 1,503.36. The task-1 seed history still gives 2,500 / 14,710 / 14,760.
- Every render_r1 item and every earlier RED (F-1 to F-6, N-1, R4-1 to R4-4, R5-1, R6-1, R7-1) and the same-kind class stay closed.
- The compute is unchanged in effect: every figure and sensitivity equals revision 8.

### findings (revision_9)
- SRC-2 closed.
- No new defect.
- Observation O-19 (from the KB report, confirmed): task 1's all-baseline cancellation figure is an exact half-cent tie (2,323.10 × 0.75 = 1,742.325). Float gives 1,742.32; a decimal half-up gives 1,742.33. It is not a scored value, and both differ from gold 1,588.38. No scored value sits on a tie.

## closing_checklist (revision_9)
Written after the round-9 reveals (2026-10-17T14:55Z). The revision_9 charter section was frozen before them (37498c7e7896fc99).

- **Audit files.** `0.md` and `1.md` correspond one-to-one with the tasks, alongside `_difficulty.md`. Revisions 1 to 9 are preserved in order. Each revision_9 comparison carries PASS on all four relationships.
- **Coverage and scopes.**
  - All four extended policies are covered.
  - Scopes are pairwise disjoint: task 0 = {renewal, increase}, task 1 = {LOU payment, sale cancellation}.
  - Tools and GT are closed. The uuid8s are independent and frozen.
- **Trees.**
  - Each tree has 1 prerequisite, 1 value_input edge, an owner=user root and no cycle. The difficulty graph is a DAG.
  - Both edges are unmet at the opening and bear weight (0.00 vs 175.93; 1,669.79 vs 1,588.38).
- **Factors.**
  - P1 6, P2 6, P3 5 and P4 6 factors, each with ≥2 parameter and ≥1 method factors.
  - Every ladder has 3 distinct tiers, with the ladder face equal to the rule and compute.
  - Every factor bears weight against an honest baseline. The all-baseline figures (1,795.00 / 182.56 / 71,459.46 / 1,742.32) are definite and differ from gold.
  - Multi-source ✓ and cross-difficulty ✓ per task.
- **Gates.** Re-run on the final form by `snapshot.sh excess_flood_layering 9`: extended, task_tools, replay, solvability, compute, grounding, cross_fire and traceability are all OK.
- **Closed.**
  - SRC-2 (KB audit) is closed. SRC-1 is base and out of scope.
  - Every render_r1 item and every earlier RED stays closed. No regression.
- **Observations carried:** O-1, O-7, O-8, O-11, O-13 to O-19.

The difficulty passes the source-layer audit.

VERDICT revision_9: task0=PASS task1=PASS
charter=CLEAN

## revision_10

### charter_global_frozen (revision_10) — seed-only round
- Re-audit round 10, a seed-only rework. Written before any round-10 GT was read. Earlier revisions are left untouched.
- Gate first: `REWORK round 10: gates 8/8 green`.
- `snapshot.sh excess_flood_layering 10`: every gate OK, including traceability. **validate_scenario VALID** (`documents: 353`).
- Hashes:
  - Charter 1a06fa0f8f9beb85… and task_tools 8c315e853830b65a… are **byte-identical** to `/tmp/erl0065_coord/seedonly_freeze.sha256` (full sha256 compared: 1a06fa0f8f9beb85f646729616318d3f4da599cf6cc9868b6443e344273a7664 and 8c315e853830b65afc3288f2e2c736961621cd2037b00d8f3e361329ce21413e).
  - So every charter-global section of revision 9 carries forward on the unchanged hashes.
  - Views changed: 0.json **df2423eac88a2f5d**, 1.json **6d9d1bdb43314954**.
- Also read, as the brief requires: SRC-3 in `audits/policy_kb/excess_flood_layering/kb_audit_report.md` (revision_3 section), and the published `docs/homeflood/` documents for the producibility check. The base `blueprint/products/homeflood.yaml` and `dwelling.yaml` were also used.
- contamination_disclosure: as in earlier revisions.

### SRC-3 closure and producibility of the new rows (revision_10)

**SRC-3.1 — closed.** Task 1, the HomeFlood cancellation of HFL-4825561.
- A signed request is now seeded: fcfbdab7, CANCELLATION / PROPERTY_SOLD / SETTLEMENT_STATEMENT / effective 2026-08-28 / SIGNED, created 2026-09-03 (the policy's closed_date).
- The credit is a CANCELLATION credit of 17.50 referenced to that request, refunded 17.50 to the INSURED (premium payor INSURED) on 2026-09-08.
- Re-derived under the published credit rule (`cancellation_credit_short_rate`, `cancellation_earning_basis`, `paid_claim_share_of_return`, `loss_of_use_charge_return`, `policy_fee_return_on_cancellation`, `cancellation_exit_fee`):
  - Property sold with a settlement statement, so the earning basis is pro rata: 2,494.68 × 301/365.
  - Net claim payments for the 2025-10-03 loss (11 whole months before processing on 2026-09-03) are 1,230,000, which is at least 25 % of 1,250,000. So the premium return share is nothing, and the LOU return is nothing (LOU money paid).
  - Policy-fee return: 64 days after the term start, with 9 whole months left, so 17.50.
  - Exit fee: 62 whole months in force, so none.
  - Credit **17.50** ✓.
- Producible.

**HomeFlood premiums — producible.**
- Premier rate manual: (1,000,000/100 × 0.49 + 250,000/100 × 0.61) × AE 1.0 × elevation +3 0.45 × deductible 5,000 0.85 = 2,457.5625. Then:
  - 0 % credit plus 160 gives 2,617.56 (2021 new business and 2022 renewal).
  - 5 % package credit gives 2,494.68 (2023; excess bound 2022-07-01).
  - Package plus claims-free, 10 %, gives 2,371.81 (2024, 2025).
  - Claims-free lost after the 2025-10-03 loss, 5 %, gives 2,494.68 (2026; record `credits_applied_pct` 5).
- Renewals are booked at the offer premium (`renewal_term_premium_figure`). No published renewal credit applies: loyalty is 59 whole months at the 2026-06-20 booking; there is no NFIP policy for household; payment 5 days early for early-renewal; checks, not ACH, for autopay; no notices for the nonpayment surcharge.
- The certificate entry c5437dbd (received 2021-06-11, before the 2021-06-25 effective date, +3 ft, applied) is consistent with an issue at the +3 row.
- New home HFL-4917380 (Plus): (6,000 × 0.46 + 1,500 × 0.58) × X 0.35 × no-EC non-SFHA 1.0 × deductible 2,500 0.92 + 95 = **1,263.86** ✓. Fee 35, escrow payment 1,298.86, LOAN_CLOSING effective on the closing date ✓.

**SRC-3.2 — closed.** HomeFlood claim HFC-4402173 is seeded and producible under `homeflood_claim_settlement`.
- Dwelling limit 1,000,000 < 80 % of 3,100,000, so the dwelling is taken at ACV: FINAL report 1,086,400 − 5,000 deductible = 1,081,400, capped at **1,000,000** ✓.
- Personal property at Premier replacement cost: **180,000** ✓ (the deductible is absorbed by the dwelling).
- LOU: 28,400 paid as incurred after the FINAL report. The SUPPLEMENTAL report (71,900) gives min(50,000, 71,900) − 28,400 = **21,600** ✓.
- The proofs of loss of 2025-11-28 fall 56 days after the loss (≤ 60) ✓. The payments of 2025-12-19 fall within 30 days of the agreed proofs ✓. Payee INSURED with no mortgagee ✓.
- The excess file's underlying settlement record 480ad3f6 now reads 1,000,000 / 180,000, which agrees. No computation reads it.

**SRC-3.3 — closed.** Task 0, the NFIP ledger of 7f147d3a.
- Components each term: risk, ICC, RFA at 18 % of (risk + ICC) (for example (2,240 + 75) × 0.18 = 416.70; (1,842 + 63) × 0.18 = 342.90), HFIAA 25 (primary residence), federal fee 50.
- Escrow disbursement payments.
- Renewals within the 18 % annual cap: 2,240 → 2,310 → 1,655 (after the certificate) → … → 1,842.
- Certificate 779b635e (applied, re-rated risk 1,620 / ICC 63, lower) gives RERATE credits from 2021-03-02 over 74 of 365 days: risk 139.89, ICC 2.43, RFA 25.62. Total refund 167.94 to LENDER_ESCROW ✓.
- Certificate 890ee57c (re-rated 2,295, higher) is unapplied ✓.
- The policy record's rated 1,842 / 63 / 50 equal the 2026 items.
- Producible.

### regression (revision_10)
- The charter and tools are unchanged, so every charter-global conclusion of revision 9 stands.
- On the new worlds the round-9 figures recompute exactly:
  - task 0: renewal 1,503.36, increase 175.93 / 1,679.29 / 2026-10-01 / 1,450,000, opening 0.00, same sensitivities;
  - task 1: LOU 11,898.50, cancellation 2026-09-15 / 1,588.38, opening 1,669.79, same sensitivities.
- Seeded excess histories still re-derive: LOU 2,500 / 14,710 / 14,760; the 2026-07-01 excess renewal 2,323.10, with the new HomeFlood DWELLING payment as one primary payment, a layer payment, and a net +13 %.
- No new row is read by any computation, and none creates a decoy for an existing read (every read is keyed by policy number or claim number since round 6).
- Personas unchanged.

### findings (revision_10)
- SRC-3 (1–3) closed.
- No new defect.
- O-18 (partial HomeFlood history) is superseded and closed.

## closing_checklist (revision_10)
Written after the round-10 reveals (2026-10-17T20:48Z). The revision_10 section was frozen before them (44f09575a62098c1).

- **Audit files.** `0.md` and `1.md` correspond one-to-one with the tasks, alongside `_difficulty.md`. Revisions 1 to 10 are preserved in order. Each revision_10 comparison carries PASS on all four relationships.
- **Seed-only round.**
  - The charter and task_tools.py are byte-identical to the coordinator's freeze.
  - No scored value moved: 1,503.36, 175.93, 1,679.29, 2026-10-01, 1,450,000; 11,898.50, 2026-09-15, 1,588.38.
  - Every new seeded row (HomeFlood request, ledger, claim file and new-home first term; NFIP ledger, re-rate credits and certificate figures) re-derives under its owning product's published rules.
  - SRC-3.1, SRC-3.2 and SRC-3.3 are closed.
- **Scopes, trees and factors** are unchanged from revision 9, and all hold: disjoint scopes; 1 value_input edge per tree, unmet at the opening and bearing weight; P1 6 / P2 6 / P3 5 / P4 6 factors on honest baselines.
- **Gates.** `snapshot.sh excess_flood_layering 10`: every gate OK, including traceability, and validate_scenario VALID.
- **Closed.** Every earlier RED and every render_r1 / KB-audit SRC-2 and SRC-3 item stays closed. No regression.
- **Observations carried:** O-1, O-7, O-8, O-11, O-13 to O-17, O-19, O-20. O-18 is closed by SRC-3.

The difficulty passes the source-layer audit.

VERDICT revision_10: task0=PASS task1=PASS
charter=CLEAN
