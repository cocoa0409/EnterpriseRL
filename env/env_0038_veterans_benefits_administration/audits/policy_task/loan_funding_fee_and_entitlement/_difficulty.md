# Policy-task audit — loan_funding_fee_and_entitlement / charter-global

## charter_global_frozen

- Auditor: independent erl-task-policy-audit agent (did not author any artifact of this difficulty).
- Freeze time: 2026-10-06T03:29Z (written before any task's GT was revealed; nothing in this section derives from a revealed GT).
- Freeze hashes (sha256, recomputed by the auditor, equal to MANIFEST.sha256.txt):
  - `tasks/loan_funding_fee_and_entitlement/loan.extended.yaml` d12b5cde218023b053c98ce35f665028af14715b29279faff2dde8dcc26316b0
  - `tasks/loan_funding_fee_and_entitlement/task_tools.py` efd66af92cab0e61d09dadd4a510500b010a0c93690e2757227742f327e752a9
  - masked views `task_0.view.json` 2b4c1aa8…b1c, `task_1.view.json` 40c7c759…d7c (match the manifest).
- Read for this section: `blueprint/blueprint.yaml` (difficulty block), `blueprint/products/loan.yaml`, `comp.yaml` / `debt.yaml` (variants, lifecycle, statuses only), `blueprint/db_schema.json`, `blueprint/share_tools.py`, the extended charter, `task_tools.py`, and the compute DSL semantics in `skills/erl-task-instantiate/scripts/check_compute.py` (MONTHS/DAYS/within_months/CFIELD/CPARAM/X*).
- Masked and unread: every `tasks/*.json` field other than `frozen_time`, `user_scenario`, `initial_state` (evaluation_criteria, computations, design_rationale, solvability_contract, prerequisite_closure, charter_scope, required_documents, db_closure…). No recursive search was run over `tasks/`.
- Entry conditions (Step 0): the brief supplied the gate snapshot (`/tmp/erl0038/views/policy_task/loan_funding_fee_and_entitlement/GATES.txt`: EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, CACHE-DIFF INFO, SCOPE OK; traceability deferred to step 3), the masked views and their hashes. Entry conditions complete.

### policy_conflict_scan

Base copy: every top-level key of the extended file other than `extended_policies` (category, display_name, binding, lifecycle, accounts, parameter_schema, variants, events, measures, policies) is structurally identical to `blueprint/products/loan.yaml` (checked by YAML equality) — the base copy is verbatim.

Extended policies (5), subjects, target tools, computes:

| policy | subject | target_tool (owner) | computes | prerequisite |
| --- | --- | --- | --- | --- |
| loan_ext_exempt_fee_refund | loan_funding_fee_refunded | refund_funding_fee_5c21eab8 (agent) | amount | [] |
| loan_ext_liquidated_loan_restoration | loan_entitlement_restored | apply_entitlement_restoration_1db0e5c4 (user) | entitlement_amount | ← loan_ext_exempt_fee_refund (value_input, state) |
| loan_ext_default_partial_claim | loan_partial_claim_paid | record_partial_claim_d52e4f0e (agent) | amount | [] |
| loan_ext_assumption_guaranty_in_force | loan_assumed_with_release | request_release_of_liability_741ed869 (user) | guaranty_amount | ← loan_ext_default_partial_claim (value_input, state) |
| loan_ext_substitution_restoration | loan_entitlement_restored | restore_entitlement_by_substitution_1ad1d2fb (agent) | entitlement_amount | ← loan_ext_assumption_guaranty_in_force (value_input, state) |

Overlaps: the two restoration policies share the subject `loan_entitlement_restored` but are separated by loan status (liquidated: foreclosed / compromise / deed in lieu, owner user, basis `debt_repaid_after_claim`; substitution: released by assumption, owner agent, basis `substitution_by_assuming_veteran`). No situation satisfies both triggers (a loan is either liquidated or released by assumption; lifecycle has no transition between `foreclosed` and `released_by_assumption`). No conflict between extended policies on trigger, eligibility, time anchor, parameter or terminal state was found.

Cross-category read boundaries: refund reads comp (award + decisions); liquidated restoration reads debt (Home Loan Guaranty Debt + debt payments) and comp (rating); partial claim reads comp (rating, status) and debt (Disability Compensation Overpayment); substitution reads debt (overpayment). All reads are value reads, none writes another category.

Scope claimed by the blueprint for this difficulty: event_types [loan_exemption_updated, loan_funding_fee_refunded, loan_entitlement_restored, loan_assumed_with_release, loan_partial_claim_paid, loan_servicing_updated]. The extended charter and task tools cover only four of the six (refunded, entitlement_restored ×2, assumed_with_release, partial_claim_paid). `loan_exemption_updated` and `loan_servicing_updated` have no extended policy and no task tool (observation O-1). The M=2 tasks' claimed scopes cannot be compared to `charter_scope` before reveal; from the worlds alone the natural partition is task 0 = {refund, liquidated restoration}, task 1 = {partial claim, assumption, substitution} — pairwise disjoint and jointly covering all five extended policies (to be confirmed against `charter_scope` in each task file).

### rule_compute_equivalence

Swept every compute binding against its `compute_basis` quotation and back against every rule sentence.

loan_ext_exempt_fee_refund
- fee_charged, fee_pct_due, table_fee, sc_effective, award_status, fee_returned, remit_lag, credit_years, fee_with_late, delay_credit, result: each has a verbatim rule quotation and implements it.
- **late_pct**: compute adds `fee_charged > 0` to both non-zero tiers; the rule sentence ("Where the loan's guaranty date is more than twice the remittance period after its closing date, the fee returned carries back…") carries no such condition. Invented condition, but with fee_charged = 0 the fee returned is 0 and the result is unchanged — no consequence (observation O-2).
- **credit_rate (F-3, SOURCE-POLICY, charter-global, no scored consequence in M tasks)**: `grant_notice` defaults to `'9999-12-31'` when no grant decision exists, so `MONTHS(closing, '9999-12-31') >= 60` is true and the compute selects the long-delay rate for a veteran who has a pre-closing denial and **no** grant. The rule's long-delay tier requires "the decision granting service connection was noticed at least the long-delay number of years after the closing date" — with no grant there is no such decision, and the rule gives "no rate otherwise". Same situation (denial before closing, no grant decision): rule → rate 0; compute → rate 1.0. Neither task's world exercises it (task 0 has a grant), so the defect is recorded here and no task inherits a consequence.

loan_ext_liquidated_loan_restoration
- All bindings quoted. `loss_unrecovered` tier 1 rule text "in collection, active or under a repayment plan" vs compute `active or repayment_plan`: "in collection" is not mapped to any status (`referred_to_treasury`? `on_hold`?) — ambiguous wording, not exercised by task 0 (status `repayment_plan`) (observation O-3).
- `sc_relief_pct`: the rule's fall-through is "where the veteran holds no compensation award"; an award below the lowest compensable rating (0 %) is in no rule tier, while compute gives it 0. Rule gap, not exercised (task 0 award is 10 %) (observation O-4).

loan_ext_default_partial_claim, loan_ext_assumption_guaranty_in_force, loan_ext_substitution_restoration
- Every binding quoted and implemented; tier boundaries (strict/inclusive) match the rule; no rule sentence without a binding. `days_since_first_due > 0` reads "first payment already due" as strictly before today (edge, not exercised).

Ladder ↔ rule ↔ compute: every `factors[].ladder` tier is a rule sentence and a branch of its `decides` binding, and vice versa, for all 21 declared factors (except the credit_rate default noted above).

### action_binding_and_uuids

- `(target_tool, computes)` pairs are distinct across the five policies; no tool is claimed twice.
- Docstrings: no docstring names another tool, states a sequence position or uses an ordering word between problems (grep for before/after/first/then/once/until/prior returns only rounding instructions, the refund-basis enum text and the partial claim receipt field "always active once the default is cured", which describes the tool's own effect). The partial-claim docstring states the effect "the loan is shown as current again (its default is cured)" — an effect description, legitimately how a reader resolves a state-form hop.
- No tool judges eligibility, status, timing or prior entries (module docstring and every body: create/update only). Confirmed per body: refund does not check `funding_fee_exempt`; restoration does not check status or debt; partial claim does not check `in_default`; release does not check status or buyer; substitution does not check release.
- Tool effect note (observation O-5): `apply_entitlement_restoration_1db0e5c4` hard-codes `restoration_basis="debt_repaid_after_claim"` — a basis that asserts the guaranty debt was repaid, which the extended liquidated-restoration policy no longer requires.
- uuid8s: 5c21eab8, 1db0e5c4, d52e4f0e, 741ed869, 1ad1d2fb — no shared prefix/suffix, no sequence, no copy-with-new-tail. PASS.

### prerequisite_graph

- `prerequisite` filled on all five policies (`[]` on refund and partial claim).
- Edges: liquidated_restoration → exempt_fee_refund; assumption_guaranty_in_force → default_partial_claim; substitution_restoration → assumption_guaranty_in_force. All point at extended policy ids in this file, none at a base policy or self; graph acyclic (two chains, depth 1 and 2).
- `policy_source` of each edge is verbatim the last sentence of the blocked policy's own `rule` (checked by string search).
- `form: state` on all three; no `fallback_reason` (correct for state form).
- `kind: value_input`; `gate` names a real binding of the blocked compute: `loss_unrecovered` (reads `refunds_booked`), `balance_basis` (reads status), `substitution_base` (reads status, guaranty_amount).
- `resolved_by` is the depended-on policy's `target_tool` in all three, and its body produces the state: refund creates a `loan_funding_fee_refunded` row with `source_txn_id`; partial claim creates `loan_partial_claim_paid` and sets status `active`; release sets status `released_by_assumption`, `release_of_liability=True`, `closed_date`, `guaranty_amount`.
- `condition` strength: refund edge and partial-claim edge match their sentences. Substitution edge condition adds "with the guaranty in force recorded on the loan" to a sentence that names only the release; since the only write producing the release also records the guaranty, no reader-visible difference (observation O-6). The partial-claim edge condition says "a loan_partial_claim_paid entry dated after the default was reported" while no record carries a default-report date; the sentence's "loan current again, with every reported default cured by a partial claim entry" is read off status + entry (observation O-6).
- No authoring-viewpoint phrasing in the `prerequisite` fields. PASS.

### prerequisite_sentences

Four-point test, each edge:

1. Liquidated restoration ← refund: "The entitlement restored on a liquidated loan is fixed only after the loan's money transactions carry a refund entry for every funding fee charge on a loan the record shows exempt from the funding fee." — own result ("entitlement restored … is fixed") + connective "only after" + record-visible state (money transactions carry a refund entry; record shows exempt) + no tool/policy id/snake_case. Exactly one write of this difficulty creates a funding-fee refund entry (`refund_funding_fee_5c21eab8`). Derivation: sentence → find which policy's rule produces "a refund entry" on a funding fee charge → loan_ext_exempt_fee_refund ("A funding fee refund is figured on one funding fee charge of the loan") → its own rule figures the amount. Single reading. PASS.
2. Assumption guaranty ← partial claim: "The guaranty that stays in force on an assumed loan is fixed only after the loan record shows the loan current again, with every reported default cured by a partial claim entry in its money transactions." — state form, "only after"; the only write that makes the record show current and books a partial claim entry is `record_partial_claim_d52e4f0e`. Derivation: loan in default → which rule pays a partial claim on a loan in default → loan_ext_default_partial_claim. Single reading. PASS.
3. Substitution ← release: "A seller's entitlement is not restored by substitution until the loan record shows the seller released from liability on the assumption." — state form, "not … until"; only `request_release_of_liability_741ed869` writes the release. Derivation: record not released → which rule records a release → loan_ext_assumption_guaranty_in_force ("When a veteran selling a home … asks to be released from liability, the release records the guaranty that stays in force") → its own rule figures the guaranty. Single reading. PASS.

No blocked rule carries a second wording, a tool name or another policy id; no depended-on rule restates the sentence.

Base rule sentences stating cross-problem orders: `loan_evt_default_servicing` "The servicer must consider home retention before liquidation, in this order: repayment plan, forbearance, loan modification, then a VA partial claim, then a compromise sale or deed in lieu" — an order among servicer options, none of which is a problem of this charter other than the partial claim; it grounds no edge (observation O-7: a reader could take it to mean a partial claim waits on the servicer having considered plan/forbearance/modification, which no record shows).

### override_declarations

Sentence-by-sentence against each `base_policy_refs` entry.

**loan_ext_exempt_fee_refund** (refs loan_evt_funding_fee_refund, loan_funding_fee; overwrite: "The refund equals the full fee collected on that loan" → "the refund is the sum of the fee returned with its late charge and the delay credit.")
- refund S1 "A funding fee is refunded when the loan's exemption has been recognized after closing … or the fee was collected in error." — extended tier 2 returns *nothing* where the award is terminated or service connection is effective after closing, even when the fee charged exceeds the table fee (a fee collected in error). Conflicts with S1's "or the fee was collected in error" in that situation; the replaced clause is the amount clause, which arguably carries this. Not exercised by task 0 (tier 1) → observation O-8.
- refund S2 "A refund is issued only when the loan record shows the veteran as exempt" — inherited, extended does not contradict.
- refund S3 "The refund equals the full fee collected …, is paid by VA directly to the veteran, and each funding fee charge is refunded only once." — first clause declared; rest inherited.
- refund S4 "A fee on a loan … paid off or refinanced is still refundable." — followed.
- funding_fee S1–S3 (fee formula, band, exemption) — followed (table fee uses the same formula and recorded use).
- funding_fee S4 "The lender remits the fee within funding_fee_remit_days days of closing, and a late remittance adds funding_fee_late_charge_pct percent" — extended carries back 2× that percentage when the guaranty date is > 30 days after closing; base states a single 4 % late charge on the lender. Different quantity (a charge the lender pays vs an amount returned to the veteran), so not an undeclared override of the scored quantity; recorded as a realism defect under factor_ladders.

**loan_ext_liquidated_loan_restoration** (refs loan_evt_entitlement_restoration, loan_agg_entitlement, loan_evt_liquidation_and_debt; overwrite: "Entitlement on a foreclosed loan is restored only after the resulting guaranty debt is repaid in full." → partial restoration formula)
- **F-1 (SOURCE-POLICY, undeclared override; bears on task 0)**: `loan_agg_entitlement` (listed in base_policy_refs) S1: "entitlement lost on a foreclosed loan stays in use until the resulting debt is repaid." Not named in `overwrite`. Extended: entitlement on a liquidated loan is restored now, less a hold-back, while the guaranty debt still has a balance. Same situation (foreclosed loan, Home Loan Guaranty Debt with a balance) → base: the entitlement stays in use, nothing restored until repaid; extended: a positive amount restored today. The declared overwrite removes one of the two base sentences that say this; the other remains in force and is rendered into the KB alongside.
- loan_evt_entitlement_restoration S2 "Entitlement is restored only for a loan whose status is paid_in_full, released_by_assumption or foreclosed." — followed (liquidated loans are `foreclosed`).
- S5 "Each loan's entitlement is restored only once." — followed.
- loan_agg_entitlement S2–S5 (no entitlement in use → full; remaining entitlement; guaranty bands) — not touched by this computation.
- loan_evt_liquidation_and_debt S2 "The claim paid creates a Home Loan Guaranty Debt …" — the extended reads that debt; consistent.

**loan_ext_default_partial_claim** (ref loan_evt_default_servicing; overwrite: the 30 % cap clause → "ceiling percentage plus the service-connected uplift, applied to the unpaid principal balance …")
- "A partial claim is paid only on a loan whose status is in_default." — inherited eligibility.
- "It requires at least partial_claim_min_delinquent_payments missed monthly payments" — inherited; no record counts missed payments, only status (the default report threshold of 61 days implies ≥ 2).
- "never exceeds partial_claim_max_pct_upb percent of the unpaid principal balance at the first unpaid installment" — declared.
- "bears … interest, and becomes due when the loan is paid off …" — not scored.
- The extended's sizing sentence "is paid at the largest amount the partial claim room allows" has no base counterpart (base sets only a cap) — a new rule, not an override; realism noted under factor_ladders.

**loan_ext_assumption_guaranty_in_force** (refs loan_evt_assumption, loan_agg_entitlement; overwrite: [])
- loan_evt_assumption S1–S4 (release conditions, fee, owner = seller) — followed; S5 "The veteran's entitlement stays charged after a release unless the buyer is a veteran who substitutes entitlement" — followed by this policy (it restores nothing).
- **F-2 (SOURCE-POLICY, undeclared override; bears on task 1)**: loan_agg_entitlement S5 "…and guaranty_large_loan_pct percent of a larger loan, limited to the remaining entitlement; entitlement equal to the guaranty is charged when it issues." The extended's tier 1 guaranty rate applies the large-loan percentage to the balance with no entitlement limit, so on an entitlement-limited loan the guaranty figured exceeds the entitlement charged to the loan. `overwrite: []` declares no departure. (Task 1 demonstrates the second number.)

**loan_ext_substitution_restoration** (refs loan_evt_entitlement_restoration, loan_agg_entitlement, loan_evt_assumption; overwrite: restoration S1 → substitution formula)
- **F-4 (SOURCE-POLICY, undeclared override; bears on task 1)**: loan_evt_assumption S5 "The veteran's entitlement stays charged after a release unless the buyer is a veteran who substitutes entitlement." Not named in `overwrite` (the only overwrite names loan_evt_entitlement_restoration). Base: when the buyer substitutes, the seller's entitlement does not stay charged — the whole entitlement charged to the loan is freed (equal to the extended's own baseline "the entitlement charged to the loan less the entitlement already restored"). Extended: a fraction is restored and the remainder stays charged permanently (base "Each loan's entitlement is restored only once"). Same situation, two answers.
- Side effect of the declared overwrite (observation O-9): the superseded clause is the base **trigger** sentence for both ordinary restoration (paid in full + disposal) and substitution; with it replaced by an amount formula, the ordinary paid-in-full restoration trigger is no longer stated anywhere in the merged charter. No task of this difficulty exercises ordinary restoration.

### factor_ladders

Counts per policy (label as declared; "MS" = at least one non-fall-through tier is a conjunction/disjunction over distinct records; "XD" = cross_difficulty).

| policy | factors | parameter | method | MS | XD |
| --- | --- | --- | --- | --- | --- |
| exempt_fee_refund | 4 | 2 (late_charge_carried_back, delay_credit_rate) | 2 (fee_returned_ground, delay_credit_clock) | fee_returned_ground (comp award vs loan closing), delay_credit_rate (denial row + grant row) | comp ×2 |
| liquidated_loan_restoration | 4 | 3 (hold_back_share, liquidation_seasoning_relief, service_connected_relief) | 1 (unrecovered_loss_measure) | unrecovered_loss_measure (debt status + loan refund row), hold_back_share (debt account + debt payments) | debt ×2, comp ×1 |
| default_partial_claim | 4 | 3 (repeat_claim_ceiling, service_connected_ceiling_uplift, other_debt_reduction) | 1 (partial_claim_still_owed) | partial_claim_still_owed (paid rows + repaid rows / loan field), other_debt_reduction (two debt rows) | comp, debt |
| assumption_guaranty_in_force | 4 | 3 (guaranty_band_rate, cure_carry_share, partial_claim_lien_share) | 1 (guaranty_balance_basis) | cure_carry_share, partial_claim_lien_share (loan row + txn rows) | none (task-level XD must come from sibling computations) |
| substitution_restoration | 5 | 4 | 1 (substitution_measure) | substitution_measure, repayment_credit | debt ×1 |

Formal shape: every ladder has three stated tiers, pairwise disjoint as stated, each tier in the rule and in compute, no two tiers of one ladder with the same value or method, every `decides` an input not `result`, binding sets disjoint within a policy. Labels: `method` on guaranty_balance_basis (acting base: UPB / UPB − PC / loan amount) and delay_credit_clock (counting anchor) select how the input is obtained, accepted as method; all `parameter` labels select a number. Every fall-through equals the policy baseline for that input; `baseline.rule` sentences are verbatim in the rule; `baseline.params` match the keys the baseline reads.

Substantive ladder tests (realism and universality). Findings below are charter-global; each task file demonstrates the consequence on its own world.

**F-5 (SOURCE-FACTOR, unreal ladder; bears on task 0) — late_charge_carried_back.** Its non-fall-through tiers return to the veteran a "late charge" of 4 % (guaranty date 16–30 days after closing) or 8 % (more than 30 days) of the fee. In VA practice the funding fee late charge is a charge assessed against the **lender** for late remittance (the base itself: "The lender remits the fee … and a late remittance adds funding_fee_late_charge_pct percent"); the veteran never pays it and VA has no practice of paying it, let alone twice it, to the veteran on a refund. The condition (lag between closing and the guaranty date, a lender/VA processing interval) is not something VA weighs when refunding a veteran's fee. The tier values are treatments VA would not publish.

**F-6 (SOURCE-FACTOR, unreal ladder; bears on task 0) — delay_credit_rate and delay_credit_clock.** These two factors pay the veteran an interest-like "delay credit" (1 %/yr or 0.5 %/yr × whole years) on a funding fee refund depending on whether a service-connection denial preceded closing and how long the grant took. VA pays no interest on funding fee refunds or on retroactive benefits; a refund of a funding fee is the fee paid. Both non-fall-through tiers of delay_credit_rate are treatments VA would not publish. In addition, delay_credit_clock's tiers 1 and 2 are both conditioned on "the loan carries a funding fee charge", which holds of every customer who reaches a refund write (the rule's own first sentence: "A funding fee refund is figured on one funding fee charge of the loan"; the tool requires a `source_txn_id`), so its fall-through "no years are counted" is unreachable at the write and the conjunct restates the policy's scope.

**F-7 (SOURCE-FACTOR, universal/empty tiers; bears on task 1) — assumption_guaranty_in_force.** The policy's own prerequisite sentence fixes the guaranty "only after the loan record shows the loan current again". At every lawful write the loan is therefore current (status `active`). Consequently: guaranty_balance_basis tier 2 ("the loan is in default") is empty and tier 1's conjunct "the loan record shows the loan current" is universal; cure_carry_share tier 1's conjunct "the loan record shows the loan current" is universal; partial_claim_lien_share tier 2 ("… AND the loan is in default") is empty and tier 1's conjunct "the loan is current" is universal. These tiers divide customers only for an agent who writes before resolving the prerequisite. Surviving factors of this computation after striking: guaranty_band_rate only (and see F-2) — below 4 factors and below 1 method.

**F-8 (SOURCE-FACTOR, universal/empty tiers; bears on task 1) — substitution_restoration.** The prerequisite sentence ("not restored by substitution until the loan record shows the seller released from liability on the assumption") plus the lifecycle (`released_by_assumption` has no outgoing transition; the release tool sets that status) make status `released_by_assumption` hold at every lawful write. Consequently: substitution_measure tier 2 ("the loan is still active OR in default") is empty and tier 1's conjunct "released by assumption" is universal; partial_claim_reserve tier 2 ("the loan is paid in full …") is empty and tier 1's conjunct "released by assumption" is universal; repayment_credit tier 1's conjunct "the loan is released by assumption" is universal. Surviving factors: early_assumption_retention, overpayment_reserve — below 4 and no `method`.

Factors passing the substantive tests (observations only):
- fee_returned_ground: tier 1 (service connection effective on/before closing → whole fee) matches VA practice (refund on retroactive award effective by closing); fall-through (excess over the table fee, i.e. a fee collected in error) is real. Tier 2's disjunct "award is terminated" is doubtful — exemption is fixed as of closing and VA severance is prospective — observation O-10.
- liquidated restoration factors: the conditions (debt repayment-plan currency, time since liquidation, service-connected rating, whether a refund offsets the loss) are matters VA/mortgage practice does weigh; the values are invented within a declared, non-statutory partial-restoration regime (real VA practice, which the base states, restores foreclosure entitlement only when the loss is repaid in full) — observation O-11.
- partial claim factors: conditions weighed in practice (prior partial claims, cumulative cap, other VA debts, rating); the baseline sizing "paid at the largest amount the partial claim room allows" is not how VA sizes a partial claim (it is sized to the arrearage/modification need, with 30 % of UPB as a cap) — observation O-12 (realism of the baseline; not demonstrated as a ladder defect).
- guaranty_band_rate: see F-2; the fall-through (guaranty on record as a percentage of the loan amount) is the realistic treatment.
- substitution: in real VA practice a substitution restores the seller's whole entitlement charged — exactly this policy's fall-through/baseline; every non-fall-through reduction is invented (observation O-13), and the "plus the repayment credit" term is uncapped, so the restored entitlement can in principle exceed the entitlement still charged (not exercised).

Cross-difficulty evidence: refund → comp; liquidated restoration → debt, comp; partial claim → comp, debt; substitution → debt. Each task has at least one XD factor provided its sibling computations survive; seeding is checked per task.

### findings

| id | verdict | summary | bears on |
| --- | --- | --- | --- |
| F-1 | SOURCE-POLICY RED | loan_agg_entitlement "entitlement lost on a foreclosed loan stays in use until the resulting debt is repaid" not overwritten; contradicts partial restoration | task 0 |
| F-2 | SOURCE-POLICY RED (plausible) | loan_agg_entitlement "limited to the remaining entitlement" departed from by guaranty_band_rate tier 1 with `overwrite: []` | task 1 |
| F-3 | SOURCE-POLICY RED (charter-global, no scored consequence) | credit_rate compute selects the long-delay rate when no grant exists; rule gives none | none of M |
| F-4 | SOURCE-POLICY RED | loan_evt_assumption "entitlement stays charged after a release unless the buyer … substitutes" not overwritten; contradicts partial substitution restoration | task 1 |
| F-5 | SOURCE-FACTOR RED | late_charge_carried_back: refunds a lender's late charge (×2) to the veteran | task 0 |
| F-6 | SOURCE-FACTOR RED | delay_credit_rate/delay_credit_clock: interest on a funding fee refund; clock conjunct universal | task 0 |
| F-7 | SOURCE-FACTOR RED | assumption ladders: "in default" tiers empty and "current" conjuncts universal at every lawful write | task 1 |
| F-8 | SOURCE-FACTOR RED | substitution ladders: "active/in default", "paid in full" tiers empty and "released" conjuncts universal | task 1 |

Observations O-1 … O-13 as numbered above (no demonstrated consequence; not grounds for rework on their own).

## closing_checklist

Written after both reveals (2026-10-06T03:35Z). The charter-global section above was frozen before any reveal and is unchanged.

- Audit files: `0.md`, `1.md`, `_difficulty.md` correspond one-to-one with tasks 0–1; first revision, no older revision.
- Coverage and scope: charter_scope task 0 = {loan_ext_exempt_fee_refund, loan_ext_liquidated_loan_restoration}, task 1 = {loan_ext_default_partial_claim, loan_ext_assumption_guaranty_in_force, loan_ext_substitution_restoration} — pairwise disjoint, jointly covering all five extended policies and five task tools; uuid8s independent. Event types loan_exemption_updated and loan_servicing_updated of the blueprint scope have no policy or tool (O-1).
- Problem trees: task 0 n = 1 (1 value_input), task 1 n = 2 (2 value_input); each has an owner=user write (restoration; release); difficulty graph acyclic; every edge load-bearing.
- Factors: every computation declares a self-sufficient baseline whose fall-back differs from gold and every factor bears weight numerically, **but** the substantive ladder tests fail: F-5/F-6 (refund), F-7 (guaranty in force), F-8 (substitution) and the `partial_claim_balance` stamp (task 1 partial claim).
- Policy self-consistency fails: F-1 (task 0), F-2 and F-4 (task 1); F-3 charter-global without a scored consequence.
- Gates: not re-run by the auditor (the brief's snapshot is the entry qualification; re-running is outside an audit that does not close).

**The difficulty does not pass the source-layer audit**: task 0 SOURCE-POLICY RED + SOURCE-FACTOR RED; task 1 SOURCE-POLICY RED + SOURCE-FACTOR RED. Both problem trees hold and both GTs match the blind derivations figure for figure.

## revision_2

### charter_global_frozen (revision 2)

- Auditor: same independent auditor as revision 1. Freeze time: 2026-10-06T06:02Z, before any revision-2 GT was revealed. Revision-1 text above is untouched.
- Hashes: `loan.extended.yaml` **changed** d12b5cde…b0 → 65b01e978413a4f1da0618df6fca934b1183d8884e19ce2160da514d1d167ef1; `task_tools.py` **unchanged** efd66af92cab0e61d09dadd4a510500b010a0c93690e2757227742f327e752a9. Per the re-derive rule every section that depends on the charter is re-derived in full below; `action_binding_and_uuids` depends on the tool module (unchanged) and on the `(target_tool, computes)` claims (re-checked: unchanged), so its revision-1 conclusions carry forward.
- New masked views: task_0 cfa9f263…a7499, task_1 f338d6ce…67421 (equal to the new manifest). Gate snapshot supplied (8 lines green; traceability deferred). Entry conditions complete.
- Masked/unread until the reveal: the same fields as revision 1. No search over `tasks/`. contamination_disclosure: none; the reworker's message lists item ids only, no values.

### policy_conflict_scan (r2)

Base copy still verbatim (YAML equality of every non-extended key with `blueprint/products/loan.yaml`). Same five extended policies, subjects, target tools, computes and owners. Changes: the refund now nets a debt offset out of the refund (reads debt: Home Loan Guaranty Debt, Disability Compensation Overpayment); liquidated restoration drops the comp relief and adds a liquidation-route relief read from `loan_guaranty_claim_paid.claim_basis`; partial claim's still-owed ladder replaces the recorded-balance tier with an interest tier; guaranty in force drops the band rate, the status conjuncts and the lien share, and adds early-assumption and repeat-claim shares; substitution drops the retention factor and the release conjuncts, adds a service-connected relief on the partial claim reserve, and caps the result at the entitlement still charged. No conflict between extended policies; the two restoration policies remain separated by loan status. New cross-category effect: the refund rule says VA "applies [the refund] against a VA debt", but no write in this difficulty (task or shared tool) records that application on the debt — observation N-4. The debt charter's `multi_debt_offset_order: earliest_notice_date_first` differs from the refund rule's fixed order (home loan guaranty debt first, then overpayment) where both debts exist; not exercised by either task — observation N-5.

### rule_compute_equivalence (r2)

Every binding of all five policies has a verbatim `compute_basis` quotation and implements it; swept back, no rule sentence lacks a binding. Specific checks: refund `fee_returned` (tier 1 now status-free), `offset_target`, `withholding_share`, `hardship_limit`, `withheld` (cap at the debt balance) match; liquidated `loss_unrecovered` adds the exempt-flag conjunct exactly as the rule; `liquidation_relief_pct` matches (rule has no tier for "no guaranty claim paid", compute gives 0 — observation N-7, unreachable for a liquidated loan with a claim); partial claim `claim_owed` interest tier matches; assumption `balance_basis`, `cure_share`, `assumption_share`, `repeat_share`, `result` match; substitution `substitution_base`, `pc_reserve_pct`, `reserve_relief_pct`, `credit_pct`, capped `result` match. Refund hardship ladder: the comp charter has no 0 % variant, so the "no award" fall-through gap is unreachable. Revision-1 F-3 (credit_rate default) and O-2 (late_pct) — the delay credit and late charge are removed: **closed**. O-3 ("in collection") — rule now reads "active or under a repayment plan": **closed**. O-4 (0 % award gap in restoration relief) — factor removed: **closed**.

### action_binding_and_uuids (r2)

Carried forward from revision 1 (tool module hash unchanged; `(target_tool, computes)` pairs unchanged and unique). O-5 (`restoration_basis="debt_repaid_after_claim"`) still stands and is now plainly at odds with the extended rule's new sentence "Entitlement on a liquidated loan is restored on request while its guaranty debt is still being repaid" — observation, open.

### prerequisite_graph (r2)

Same three edges, same `policy_source` sentences (still verbatim last sentences of the blocked rules), state form, value_input, gates `loss_unrecovered` / `balance_basis` / `substitution_base` exist and read the state each depended-on write changes. Acyclic. `condition` texts revised: partial-claim edge now "carries the loan_partial_claim_paid entry that cured the reported default"; substitution edge now states the guaranty as what the release records alongside. O-6 **closed**. Effects re-verified against the new compute (refund: the unpaid-out part of the fee reduces the loss; partial claim: still owed rises, basis falls by the same amount; release: measure moves from the entitlement still charged to the recorded guaranty).

### prerequisite_sentences (r2)

Unchanged sentences, unchanged single resolving writes; four-point test passes for all three as in revision 1. O-7 (base servicer-order sentence) unchanged — observation, open.

### override_declarations (r2)

- Refund: overwrite now supersedes "The refund equals the full fee collected on that loan, is paid by VA directly to the veteran" (replaced by fee returned less amount withheld). Base S1 "…or the fee was collected in error": tier 2 now applies only where the fee charged does not exceed the table fee, so an over-collected fee is never zeroed — O-8 **closed**. Remaining base sentences followed.
- Liquidated restoration: overwrite now also names loan_agg_entitlement "entitlement lost on a foreclosed loan stays in use until the resulting debt is repaid." replaced by a sentence carried verbatim in the rule. **F-1 closed.**
- Assumption: rate is now the recorded guaranty over the original loan amount, so the guaranty figured never exceeds the guaranty issued against entitlement; consistent with loan_agg_entitlement's "limited to the remaining entitlement" under `overwrite: []`. **F-2 closed.**
- Substitution: overwrite now names loan_evt_assumption "The veteran's entitlement stays charged after a release unless the buyer is a veteran who substitutes entitlement." (replacement carried in the rule). **F-4 closed.** The loan_evt_entitlement_restoration overwrite is narrowed to the substitution clause only, so the paid-in-full + disposal trigger survives — O-9 **closed**.
- Partial claim: unchanged declaration; no new conflict.

### factor_ladders (r2)

| policy | factors | parameter | method (declared) | MS | XD |
| --- | --- | --- | --- | --- | --- |
| exempt_fee_refund | 4 | 2 (refund_offset_share, refund_hardship_limit) | 2 (fee_returned_ground, refund_offset_target) | refund_offset_target tier 2 | comp, debt |
| liquidated_loan_restoration | 4 | 3 | 1 (unrecovered_loss_measure) | unrecovered_loss_measure, hold_back_share | debt |
| default_partial_claim | 4 | 3 | 1 (partial_claim_still_owed) | still_owed, other_debt_reduction | comp, debt |
| assumption_guaranty_in_force | 4 | 3 | 1 (guaranty_balance_basis) | guaranty_balance_basis tier 2 | none |
| substitution_restoration | 5 | 4 | 1 (substitution_measure) | substitution_measure tier 1, repayment_credit tier 2 | comp, debt |

Revision-1 findings:
- **F-5, F-6 closed**: late-charge and delay-credit factors removed. The new refund factors (offset against a VA debt, share by plan method, hardship limit by rating) rest on conditions VA practice weighs (VA does apply amounts it owes a veteran against debts the veteran owes it); fee_returned_ground's tier 1 and fall-through remain realistic; the "terminated" disjunct is gone — O-10 **closed**.
- **F-7 closed**: the assumption ladders no longer carry "loan current"/"in default" conditions; balance basis divides on whether a partial claim is owed, cure share on the latest claim's age, the new shares on months since closing and claim count — none holds of every customer who reaches the release or is empty there.
- **F-8 narrowed, not closed**: the "released by assumption" conjuncts and the "paid in full"/"active or in default" tiers are gone from partial_claim_reserve, repayment_credit and substitution_measure. But substitution_measure's new tier 2 "a restoration has already been booked on the loan" is empty at every lawful substitution write, and tier 1's conjunct "no restoration has yet been booked" holds of every customer who reaches it: base loan_evt_entitlement_restoration "Each loan's entitlement is restored only once." So the factor still has two live tiers (guaranty in force below entitlement still charged / otherwise). Striking it leaves the substitution computation with 4 factors and **no `method`** → SOURCE-FACTOR RED persists (R2-F8).
- O-13: result now capped at the entitlement still charged (the "plus repayment credit" overshoot is closed); the reductions remain invented relative to real VA substitution practice, which restores the whole entitlement charged — the realism observation stands, open.

New ladder findings:
- **N-1 (SOURCE-FACTOR RED; bears on task 0) — fee_returned_ground tiers 2 and 3 select the same value.** Tier 2 applies only where "the fee charged does not exceed the table fee"; on exactly that domain the fall-through "the excess of the fee charged over the table fee … never less than zero" is MX(0, fee − table) = 0 = "nothing is returned". The two tiers can never give different results: one tier written as two. The ladder has two real tiers (< 3).
- **N-2 (SOURCE-FACTOR, plausible; bears on task 0) — refund_offset_target labelled `method`.** Its tiers pick which debt balance caps the withholding (home loan guaranty debt balance / overpayment balance / 0) and feed one formula, `withheld = MN(offset_target, fee_returned × share × limit)`: a different number into the same formula (a cap), i.e. a `parameter`. With N-1 striking fee_returned_ground, the refund computation has no honest `method` and 3 factors.
- partial_claim_still_owed: the recorded-balance tier is replaced by an interest tier (1 %/yr simple, the program's partial-claim rate — realistic). The ladder no longer reads `partial_claim_balance`; whether the seed still lets that field stand in for the tier is a per-task question (task 1).
- liquidation_route_relief: deed in lieu 30 % / compromise sale 15 % / foreclosure 0 — VA does treat deed-in-lieu and compromise-sale liquidations more favourably than foreclosure (relocation assistance in the base); acceptable within the declared partial-restoration regime. O-11 (that regime departs from 38 U.S.C. 3702(b) as the base itself states it) stands as an observation.
- O-12 (partial claim sized to the full room, not the arrearage) unchanged — observation, open.

### findings (r2)

| id | r2 status | note |
| --- | --- | --- |
| F-1 | closed | declared in overwrite, replacement in rule |
| F-2 | closed | rate = recorded guaranty / loan amount |
| F-3 | closed | delay credit removed |
| F-4 | closed | declared in overwrite, replacement in rule |
| F-5 | closed | late-charge factor removed |
| F-6 | closed | delay-credit factors removed |
| F-7 | closed | status conjuncts and default tiers removed |
| F-8 | **open (narrowed)** | substitution_measure tier 2 empty / tier 1 conjunct universal under "restored only once"; substitution left without a method |
| N-1 | **new, SOURCE-FACTOR RED** | fee_returned_ground tier 2 ≡ fall-through |
| N-2 | **new, SOURCE-FACTOR (plausible)** | refund_offset_target is a parameter labelled method |
| O-2, O-3, O-4, O-6, O-8, O-9, O-10 | closed | |
| O-13 | partly closed | cap added; realism of reductions stands |
| O-1, O-5, O-7, O-11, O-12 | open (observations, no change made) | O-5 now contradicts the new liquidated-restoration sentence |
| N-4, N-5, N-7 | new observations | offset not recorded on the debt; offset order vs debt charter; no "no claim" tier |

### closing_checklist (r2)

Written after the revision-2 reveals (2026-10-06T06:06Z); the revision-2 charter-global section above was frozen before them.

- Files: `0.md`, `1.md`, `_difficulty.md`, each with `## revision_2` appended; revision-1 text untouched.
- Scope: charter_scope unchanged (task 0: refund + liquidated restoration; task 1: partial claim + guaranty in force + substitution) — disjoint, all five policies covered; tools and uuid8s unchanged.
- Trees: task 0 n = 1, task 1 n = 2, all edges value_input and load-bearing, each with an owner=user write, graph acyclic.
- Policy self-consistency: F-1, F-2, F-3, F-4 closed; no new SOURCE-POLICY defect.
- Factors: F-5, F-6, F-7 closed. **Open**: N-1 (refund fee_returned_ground tier 2 ≡ fall-through; with N-2 the refund computation keeps 3 honest factors and no method) → task 0; R2-F8 (substitution_measure tier 2 empty under "Each loan's entitlement is restored only once"; substitution keeps no method) → task 1.
- Unique solution: both GTs equal the blind derivations figure for figure; N-3 (task 1 seed field contradicting its ledger) recorded as an observation.
- Gates: snapshot supplied by the brief, not re-run by the auditor.

**The difficulty still does not pass the source-layer audit**: task 0 SOURCE-FACTOR RED, task 1 SOURCE-FACTOR RED. Every revision-1 SOURCE-POLICY RED is closed.

## revision_3

### charter_global_frozen (revision 3)

- Same independent auditor. Freeze time 2026-10-06T07:02Z, before any revision-3 GT was revealed. Revision-1 and revision-2 text above untouched.
- Hashes: `loan.extended.yaml` **changed** 65b01e97…7ef1 → afef30f14d0a3ddb78eb14a4af84c44c0b821531c64e52e894711e5bbf0a9930 → charter-global sections re-derived in full; `task_tools.py` unchanged efd66af9…52a9 → `action_binding_and_uuids` carried forward (the `(target_tool, computes)` pairs were re-checked and are unchanged). Views: task_0 cfa9f263…7499 (**unchanged** from r2), task_1 116e2899…ea38 (changed). Gate snapshot: 8 lines green, traceability deferred. Entry conditions complete.
- Masked/unread until reveal: same fields as before; no search over `tasks/`; contamination_disclosure: none (the reworker's message lists item ids only).

### policy_conflict_scan (r3)

Base copy verbatim (YAML equality). Five extended policies, same subjects, tools, computes, owners and edges. Changes since r2: **refund** rewritten — the fee returned now follows the loan's exemption flag (exempt → whole fee; otherwise excess over the table fee, the baseline), and the part applied against a home loan guaranty debt is decided by an application ceiling (plan installment × 12 / whole balance in active collection / nothing), a plan-method share, a hardship limit by rating and a new recent-offset relief (months since the last `debt_offset_collected` on the veteran's debts). The comp award's service-connection date is no longer read; the disability-compensation-overpayment target is gone. **partial claim**: still-owed ladder now interest tier first (latest claim ≥ 12 months: paid less repaid plus 1 %/yr simple interest), then paid less repaid, then paid. **substitution**: substitution_measure tier 2 is now "no entitlement was charged to the loan because it is a rate reduction refinance carrying the entitlement of the loan it replaced → guaranty in force, never more than the basic entitlement". Liquidated restoration and guaranty in force unchanged from r2 (compute identical). No conflict between extended policies. N-5 (offset order vs debt charter) is moot now that the refund applies only against a home loan guaranty debt: **closed**. N-4 (no write records the application on the debt) unchanged — observation, open.

New observation N-8: the refund baseline now says "on any other loan [not shown exempt] it is the amount by which the fee charged exceeds the fee due"; the inherited base eligibility "A refund is issued only when the loan record shows the veteran as exempt" makes that clause unreachable at any lawful refund. It is a baseline sentence, not a factor tier; no task exercises it.

### rule_compute_equivalence (r3)

Every binding of the five policies has a verbatim `compute_basis` quotation (automated check: no missing basis except the trivial intermediate `ent_open = ent_charged − ent_restored` of liquidated restoration, unchanged since r1; every quotation found verbatim in its rule); every replaced_by sentence is in its rule; every baseline sentence is in its rule; factor bindings disjoint. Swept by hand: refund `fee_returned`, `most_applied`, `applied_share`, `hardship_limit`, `offset_relief` ("an offset on the veteran's VA debts" = XLATEST over the customer's debt transactions), `applied` (cap at the most applied), `result`; partial claim `claim_owed` three tiers in rule order; substitution `substitution_base` three tiers. Match.

**Empty promise found (R3-F8, see factor_ladders):** the substitution rule promises, for a rate reduction refinance with no entitlement charged to it, a measure of "the guaranty in force on the loan record but never more than the basic entitlement", and then caps the result "never more than the entitlement still charged" — which for that very loan is the entitlement charged to it (none) less restored = 0. The promised measure can never reach the result.

### action_binding_and_uuids (r3)

Carried forward (tool hash unchanged). O-5 open (restoration tool writes basis `debt_repaid_after_claim`).

### prerequisite_graph / prerequisite_sentences (r3)

Same three edges and verbatim sentences, state form, value_input; gates exist and read what the depended-on writes change; conditions and effects re-verified against the new computes (refund effect: the part applied against the debt reduces the loss; partial claim: debt carried rises, basis falls; release: measure moves from the entitlement still charged to the recorded guaranty). Acyclic. Four-point test passes. O-7 open (observation).

### override_declarations (r3)

Refund overwrite now replaces "The refund equals the full fee collected on that loan, is paid by VA directly to the veteran" with "The refund paid to the veteran on the charge is the fee returned less the amount applied against the debt" (in the rule). Base S1 ("refunded when the loan's exemption has been recognized … or the fee was collected in error"): exempt → whole fee; collected in error → excess (baseline). Consistent. Other policies as in r2. No undeclared override found.

### factor_ladders (r3)

| policy | factors | parameter | method | MS | XD |
| --- | --- | --- | --- | --- | --- |
| exempt_fee_refund | 4 | 3 (applied_share, hardship_limit, recent_offset_relief) | 1 (refund_application_ceiling) | application ceiling tier 2 ("active collection with no repayment plan") | debt ×3, comp ×1 |
| liquidated_loan_restoration | 4 | 3 | 1 | yes | debt |
| default_partial_claim | 4 | 3 | 1 (partial_claim_still_owed) | still_owed tier 2, other_debt_reduction | comp, debt |
| assumption_guaranty_in_force | 4 | 3 | 1 | yes | none |
| substitution_restoration | 5 | 4 | 1 (substitution_measure) | substitution_measure tiers 1–2 | comp, debt |

Round-2 items:
- **N-1 closed**: fee_returned_ground is gone; the fee returned is now a baseline rule, not a factor.
- **N-2 closed (borderline)**: refund_application_ceiling's tiers compute the most applied in different ways — installment × number of installments, the whole balance read from the debt, or nothing — rather than substituting one number into one formula; accepted as `method` on the same footing as guaranty_balance_basis (acting base). Realism: VA does apply amounts owed to a veteran against VA debts; capping by plan installments and relieving recent offsets or hardship are plausible treatments.
- recent_offset_relief: three disjoint tiers on months since the last offset (< 6 / 6–23 / ≥ 24 or none); condition weighed in practice (recency of collection); near-miss available wherever plan payments (not offsets) are more recent.
- partial_claim_still_owed (new ladder): three tiers with distinct algorithms (remainder plus simple interest / remainder / paid); the program's 1 % partial-claim interest is real; no universal conjunct.
- **R2-F8 not closed → R3-F8 (SOURCE-FACTOR RED; bears on task 1).** substitution_measure's old empty tier ("a restoration has already been booked") is replaced by tier 2 "no entitlement was charged to the loan AND it is a rate reduction refinance carrying the entitlement of the loan it replaced". The tier is now reachable (an IRRRL can be assumed and its seller can ask for substitution), but its outcome can never reach the scored value: on such a loan `ent_charged` = 0, so `ent_still_charged` = 0 and `result = MN(ent_still_charged, …)` = 0 whatever the measure. Demonstrated by recomputation on task 1's post-release world with the loan recast as an IRRRL and its entitlement charge row removed: tier 2 gives measure 36000.00 → result 0.00; substituting the fall-through gives result 0.00. Tier 2 and the fall-through therefore select the same scored outcome in every world where tier 2 applies — one tier written as two — so the ladder has two effective tiers. Striking it leaves the substitution computation with 4 factors and no `method`. The same fact is a rule-level empty promise (see rule_compute_equivalence). Realism: VA practice would not restore the seller any entitlement "from" an IRRRL record either, since the entitlement stays charged on the loan the IRRRL replaced — which is exactly why the tier cannot pay out.
- O-13 (substitution reductions vs real practice, which restores the whole entitlement) — observation, open. O-11, O-12 — observations, open.

### findings (r3)

| id | r3 status | note |
| --- | --- | --- |
| N-1 | closed | factor removed |
| N-2 | closed (borderline) | ceiling tiers now differ in algorithm |
| R2-F8 / F-8 | **open → R3-F8, SOURCE-FACTOR RED** | substitution_measure tier 2 cannot change the result (cap at entitlement still charged = 0 on an IRRRL); substitution keeps no effective method |
| N-5 | closed | overpayment target removed |
| N-4, N-7, N-8 | open observations | no debt write for the application; no "no claim" tier; unreachable non-exempt refund clause |
| O-1, O-5, O-7, O-11, O-12, O-13 | open observations | unchanged |

### closing_checklist (r3)

Written after the r3 reveals (2026-10-06T07:05Z); the r3 charter-global section was frozen before them.

- Files `0.md`, `1.md`, `_difficulty.md` each carry `## revision_3`; earlier revisions untouched.
- Scope, tools, uuid8s, trees (task 0 n = 1, task 1 n = 2; all value_input, load-bearing, owner=user present, acyclic): unchanged and passing.
- Policy self-consistency: no open SOURCE-POLICY defect.
- Factors: task 0 passes (N-1, N-2 closed). **Task 1 fails on R3-F8**: substitution_measure's IRRRL tier cannot change the scored value because the restoration is capped at the entitlement still charged to the loan, which is 0 on exactly that loan. GT design_rationale asserts the opposite; recomputation refutes it.
- Unique solution: both GTs equal the blind derivations figure for figure.
- Gates: snapshot from the brief (8 green); not re-run by the auditor.

**The difficulty does not yet pass**: task 0 PASS, task 1 SOURCE-FACTOR RED (R3-F8). Open observations (not grounds for rework on their own): O-1, O-5, O-7, O-11, O-12, O-13, O-T1, O-T2, N-4, N-7, N-8.

## revision_4

### charter_global_frozen (revision 4)

- Same independent auditor. Freeze time 2026-10-06T07:23Z, before any revision-4 GT reveal; earlier revisions untouched.
- Hashes: `loan.extended.yaml` **changed** afef30f1…9930 → 1ecaebe44450466beeaec02341119d357e1ed4bfdf404d326f281102b715c5bd → charter-global sections re-derived; `task_tools.py` unchanged efd66af9…52a9 → `action_binding_and_uuids` carried forward. Views: task_0 cfa9f263…7499 and task_1 116e2899…ea38 — **both unchanged from r3**. Gate snapshot 8 green, traceability deferred. contamination_disclosure: none.

### re-derivation (r4)

- Base copy verbatim. Only `loan_ext_substitution_restoration` changed: its compute, compute_basis and rule now define the substitution measure as (1) the guaranty in force where it is below the entitlement still charged and not below the basic entitlement; (2) the basic entitlement, never more than the entitlement still charged, where the guaranty in force is below both; (3) otherwise the entitlement still charged. The other four policies' computes, factors, params, overwrites and prerequisites are identical to r3 (checked binding by binding); automated sweep again finds every compute_basis quotation verbatim in its rule, every baseline sentence in its rule, no missing basis except the trivial `ent_open` (unchanged since r1).
- policy_conflict_scan, override_declarations, prerequisite_graph, prerequisite_sentences: conclusions of r3 hold unchanged (substitution's overwrites, prerequisite sentence, condition and effect unchanged; effect re-verified: without the release the recorded guaranty equals the entitlement still charged, so the measure is the fall-through).
- rule_compute_equivalence for the new measure: rule tier 1 ↔ `guaranty < still charged and guaranty ≥ basic_entitlement → MN(still, guaranty)` (= guaranty); tier 2 ↔ `guaranty < still and guaranty < basic → MN(still, basic)`; fall-through ↔ `still`. Equivalent. The r3 empty promise (IRRRL tier nullified by the cap) is gone.

### factor_ladders (r4)

- **R3-F8 closed.** substitution_measure (method): the three tiers select different measures (recorded guaranty / basic-entitlement floor / entitlement still charged) and the new tier 2 reaches the result: on task 1's post-release world with the recorded guaranty set to 30000.00, tier 2 gives measure 36000.00 and restoration 25852.13, while the fall-through gives 69852.13. No tier is empty at a lawful write and no conjunct holds of every customer: the guaranty recorded by a release can equal the entitlement still charged (balance at or above the original amount, no partial claim, release ten years or more after closing), so the fall-through is reachable, though only in that narrow world — observation N-9. Within tier 2, where the entitlement still charged is itself below the basic entitlement, tier 2's value coincides with the fall-through's; on the rest of its domain it differs, so the tiers are distinct. Realism: a basic-entitlement floor on the measure is a recognisable VA concept (basic entitlement $36,000); acceptable within the declared substitution regime (O-13 realism remark still applies).
- The factor's declared `bindings` still list `ent_charged`, which the new decides-expression no longer reads (it reads `ent_still_charged`); harmless, binding sets remain disjoint — observation N-10.
- All other factor tables as in r3.

### findings (r4)

| id | r4 status |
| --- | --- |
| R3-F8 (and F-8 lineage) | closed |
| N-9, N-10 | new observations (narrow fall-through; stale binding name) |
| N-4, N-7, N-8, O-1, O-5, O-7, O-11, O-12, O-13 | open observations, unchanged |

### closing_checklist (r4)

Written after the r4 reveals (2026-10-06T07:26Z).

- Per-task files `0.md`, `1.md` and this file each carry `## revision_4`; revisions 1–3 untouched; every r4 comparison section carries a PASS.
- Coverage/scope: charter_scope task 0 = {refund, liquidated restoration}, task 1 = {partial claim, guaranty in force, substitution} — disjoint, all five extended policies covered; five task tools, independent frozen uuid8s (tool module unchanged since r1).
- Problem trees: task 0 one prerequisite problem (1 value_input), task 1 two (2 value_input); each tree has an owner=user write (restoration; release); the difficulty's prerequisite graph is acyclic; every edge unmet at the opening and load-bearing; no tool judges a prerequisite.
- Factors: every computation declares a self-sufficient baseline whose fall-back differs from gold and 4–5 factors (≥ 2 parameter, ≥ 1 honest method); each task has multi-source and cross-difficulty (comp, debt) factors on seeded rows; every factor bears weight on its task's world; near-misses present per computation; no empty tier, duplicated tier, universal conjunct or stamp remains.
- Unique solution: both GTs equal the blind derivations figure for figure; id-valued gold arguments all trace to earlier read outputs on replay.
- Gates: the brief's r4 snapshot (8 green, traceability deferred to step 3) is the final-form gate evidence; not re-run by the auditor.

**Source-layer audit: PASS for the difficulty (both tasks pass all four relationships).** Open observations (not grounds for rework): O-1 (two blueprint event types without policy/tool), O-5 (restoration tool writes basis `debt_repaid_after_claim` while the debt is still being repaid), O-7, O-11, O-12, O-13 (realism of the partial-restoration, partial-claim sizing and substitution-reduction regimes against real VA practice), O-T1, O-T2, N-4 (refund application against the debt is not recorded on the debt), N-7, N-8, N-9, N-10.
