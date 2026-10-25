# Policy-task audit — ostomy_supply_program_services / charter-global

## charter_global_frozen
- Auditor: independent policy-task auditor (erl-task-policy-audit), revision 1. Freeze time 2026-10-15T02:17Z (written before any task GT was read).
- Inputs and hashes (verified with sha256sum before reading):
  - `tasks/ostomy_supply_program_services/ostomy.extended.yaml` de5b99e8e638bc341476d2b6965ad5c4b40deccc3f089f1bf67dc5cf0d40c123
  - `tasks/ostomy_supply_program_services/task_tools.py` b6e4229c0123246773c5a0596696158490dc019f153acd4eb0233e22cce85a8b
  - `.audit_views/policy/ostomy_supply_program_services/0.view.json` d006305f…dbdf5f, `1.view.json` c8b9e061…0ebbe5 (keys: frozen_time, user_scenario, initial_state; `_masked_keys` = design_rationale, db_closure, db_closure_matches_initial_state, solvability_contract, evaluation_criteria, computations, prerequisite_closure, charter_scope, required_documents).
  - Read as well: `blueprint/blueprint.yaml`, `blueprint/db_schema.json`, `blueprint/share_tools.py` (signatures), `blueprint/products/ostomy.yaml` (diffed against the base copy), `blueprint/products/continence.yaml` (only to check the seeded continence rows against their owning charter), and the DSL semantics of `MONTHS`/`DAYS`/`RND`/`within_months` in `skills/erl-task-instantiate/scripts/check_compute.py`.
- Not read before the freeze: `tasks/ostomy_supply_program_services/tasks/*.json`, any instantiator scratch, any other difficulty's tasks/ or audits/, any other scenario. No recursive search ran over a tasks/ directory.
- Section content comes only from the charter, the schema and the tool contracts (plus the seeded rows where a row is named as a concrete witness). Nothing here comes from a revealed GT.

### entry_conditions
- Gate snapshot came with the brief: EXTENDED, TASK TOOL CONTRACT, REPLAY --check, SOLVABILITY, COMPUTE, GROUNDING and SCOPE OK. TRACEABILITY NOT OK, with the stated reason that only the unlock tool names lack a source until the KB renders (deferred to step 3). Masked views came with hashes and match the files on disk.
- Observation E1: one instantiation gate (traceability) is not green when this audit starts. I accept the coordinator's deferral as stated. It is not a finding against the four relationships.

### policy_conflict_scan
- The base copy is verbatim: `diff <(sed -n 1,1922p ostomy.extended.yaml) blueprint/products/ostomy.yaml` differs only by a trailing blank line.
- Seven extended policies, each with its own subject, target tool and computed quantity:
  | id | subject | target_tool / computes | trigger |
  |---|---|---|---|
  | ostomy_ext_plan_denial_charge | ostomy_patient_charge (non_covered_item, MA convex over-limit) | post_plan_denial_charge_c6cdcbbb / amount | state_due |
  | ostomy_ext_hardship_waiver | ostomy_balance_adjustment (hardship_waiver) | post_hardship_waiver_31941945 / amount | state_due |
  | ostomy_ext_plan_installment | ostomy_patient_payment (payment plan request) | accept_payment_plan_7a7f8df9 (owner=user) / monthly_amount_usd (+plan_months) | on_request |
  | ostomy_ext_refill_units | ostomy_refill_shipment (A4407) | ship_ostomy_refill_57098f77 / units | on_request |
  | ostomy_ext_notice_units | ostomy_liability_notice_signed (A4407) | sign_liability_notice_87444016 (owner=user) / notice_units | on_request |
  | ostomy_ext_expedite_fee | ostomy_patient_charge (expedited_shipping, customer-requested refill) | post_expedite_charge_9c5d9761 / amount | state_due |
  | ostomy_ext_reship_correction | ostomy_balance_adjustment (billing_correction on an expedited_no_charge shipment) | post_reship_correction_64ee6975 / amount | state_due |
- Overlapping subjects: denial_charge and expedite_fee both post ostomy_patient_charge, but with disjoint charge types (non_covered_item vs expedited_shipping). hardship_waiver and reship_correction both post ostomy_balance_adjustment, but with disjoint reasons (hardship_waiver vs billing_correction), and reship_correction's second overwrite keeps the hardship gate whole for hardship waivers. I found no two policies that write the same quantity on the same object.
- Cross-category reads all go to continence: status, continence_shipments ship_date/supply_days/event_type and continence_billing amount/event_type. Each is a read only, and no policy writes continence.
- Time anchors are all `NOW` = frozen_time date, except the denial lag (ship date to denial posting), posting age (posting to application received_at), transit and confirmation lags (ship/confirm/POD dates). No policy anchors one quantity on two different clocks.
- Scopes: the prerequisite graph (below) partitions the seven policies into two trees: {refill_units ← notice_units, hardship_waiver} and {plan_installment ← plan_denial_charge, expedite_fee, reship_correction}. With M=2, these two trees are disjoint and together cover all seven policies. Which task claims which tree is checked per task, and against charter_scope after the reveal.

### rule_compute_equivalence
- Mechanical sweep (`/tmp/audit_ostomy_0063/verb.py`, whitespace-normalised substring tests): for all seven policies, every `compute_basis` value is verbatim in that policy's `rule`; every `baseline.rule` sentence is in the `rule`; every `prerequisite[].policy_source` is in the `rule`; every `overwrite[].replaced_by` is in the `rule`; every `superseded_clause` is verbatim in the named base policy's rule; and every compute binding has a `compute_basis` entry.
- Sweep back, sentence by sentence (rule → compute):
  - Every factor ladder tier is stated in prose in its rule and implemented in its `decides` binding. Every branch of each `decides` binding is a tier the rule states. I found no tier that exists only in compute.
  - Rounding placement matches the rounding sentences:
    - denial: `reduced_amount` RND, then `result` RND, matching "rounded to the cent before any credit … rounded to the cent".
    - hardship: `result` RND.
    - installment: `result` RND, and `plan_months` = floor, matching "the whole number of months at which the installment reaches that minimum".
    - refill: `extra_barriers`/`on_hand_barriers` int, matching "rounded down to a whole barrier".
    - notice: int(RND(…,6)), matching "rounded down to a whole barrier".
    - expedite, reship: RND.
    - `RND` is Python `round` (`check_compute.py:388`). The rules say only "rounded to the cent", but no figure derived in either task falls on a binary half-cent tie that would separate half-even from half-up (see the task files).
  - Gaps that are recorded:
    - **C4 (SOURCE-POLICY RED)**: the tier's A4407 allowance is a constant in compute. See findings.
    - O3: the unused-cover window boundary.
    - O4: the reship duplicate tier computes an average.
    - O5: the denial charge does not test the organization-determination denial it requires.
    - O8: cap_window says "counts" while compute sums amounts.
- Cross-category reads in compute (`EXISTS('continence', status='active')`, `XCOUNT/XSUM/XLATEST` on continence_shipments/continence_billing) match each policy's `cross_category.reads`.

### action_binding_and_uuids
- Each `(target_tool, computes)` pair is claimed by exactly one policy (the seven pairs in the table above are distinct).
- Tool bodies (`task_tools.py`) each perform one create, plus at most a running-total update on `ostomy_programs`. None refuses a call, raises, validates eligibility, aggregates history or returns a hint. The module docstring says so, and the bodies confirm it: every write is an unconditional `ctx.create`.
- Docstrings: the only "after" occurrences describe the balance or units after the write itself (lines 32, 69, 153, 229, 265), and "then shows" describes the write's own effect (lines 57, 94, 254). No docstring names another tool, a sequence position or another problem. Param descriptions carry enumerations (HCPCS item list, notice forms) and formats, but no concrete example values.
- Owners: accept_payment_plan and sign_liability_notice are `owner="user"`. The other five are `owner="agent"`.
- uuid8 tails: c6cdcbbb, 31941945, 7a7f8df9, 57098f77, 87444016, 9c5d9761, 64ee6975. These are seven distinct tails, with no shared prefix, no sequence and no adjacent values. I found no sign of batch derivation.
- Observation O2: `sign_liability_notice_87444016.notice_type` enumerates plan_member_waiver / abn_cms_r_131 / medicaid_non_covered_agreement only. ostomy_ext_notice_units is not scoped away from the Medicare Advantage tier, whose `liability_notice_type` is `organization_determination_required` and where base `ostomy_liability_notice` says "no notice can make the member liable", or from the self-pay tier ("no notice applies"). No task world is on those tiers for this tool.

### prerequisite_graph
- `prerequisite` is filled on all seven policies: `[]` on denial_charge, hardship_waiver, notice_units, expedite_fee and reship_correction.
- plan_installment → plan_denial_charge, expedite_fee, reship_correction: all `value_input`, gate `balance_due` (a real binding), form state.
- refill_units → notice_units (`value_input`, gate `extra_cover`, a real binding, form state) and → hardship_waiver (`state_gate`, form state).
- Every `problem` is an extended id of this file, never a base id and never the policy itself. The graph is two in-trees with no cycle. No `fallback_reason` appears, and none is needed (every edge is state form).
- Every `resolved_by` is the depended-on policy's `target_tool`:
  - post_plan_denial_charge, post_expedite_charge and post_reship_correction each move `ostomy_billing` running totals, and so `balance_due`.
  - sign_liability_notice creates the `ostomy_liability_notice_signed` row that `extra_cover` reads.
  - post_hardship_waiver creates the `hardship_waiver` adjustment.
- No authoring-viewpoint words ("this task", "at the opening") appear in any prerequisite field.
- Observation O6 (refill_units → hardship_waiver):
  - `gate` is the field `ostomy_programs.patient_balance_due`, not an eligibility gate. The gating quantity is `ostomy_msr_past_due_amount`.
  - `condition` appends "which brings the past-due amount below past_due_hold_min_usd". The policy_source sentence does not state this; it waits only on the waiver being posted. The added clause is a claim about the world, checked per task.

### prerequisite_sentences
Each sentence was given the four-point test: an explicit ordering connective; a record-visible state named in table/finder words; no tool, id or snake_case token; and strength equal to the condition.
1. plan_installment ← plan_denial_charge. Sentence: "A payment plan's installment is not worked out until the records carry a non-covered item charge against the most recent convex-barrier refill whose original claim the plan denied under its organization determination denial."
   - Connective "not … until". State: a non_covered_item patient charge against a named refill. Passes.
   - Only post_plan_denial_charge_c6cdcbbb writes `charge_type=non_covered_item`, so exactly one write of this difficulty brings the state about.
   - Derivation: sentence + `ostomy_billing` rows → the reader finds that the latest A4407 refill's original claim carries a denial and no non_covered_item charge → the policy whose own rule creates that charge is ostomy_ext_plan_denial_charge ("one charge is posted against that refill").
2. plan_installment ← expedite_fee. Sentence: "The plan's installment is fixed only after the program's most recent refill shipped expedited at the customer's request carries its expedited shipping charge."
   - "only after". Passes.
   - Only post_expedite_charge_9c5d9761 writes `charge_type=expedited_shipping`. ship_ostomy_refill always records `shipping_method="standard"` and posts no charge.
   - Derivation: latest refill with shipping_method expedited and no expedited_shipping charge → ostomy_ext_expedite_fee ("one charge is posted against that refill").
3. plan_installment ← reship_correction. Sentence: "A payment plan's installment is not set until the expedited shipping charge posted against the program's most recent shipment sent expedited at no charge carries its billing correction."
   - "not … until". Passes.
   - Only post_reship_correction_64ee6975 writes `adjustment_reason=billing_correction`. post_hardship_waiver writes hardship_waiver.
   - Derivation: latest expedited_no_charge shipment carrying an expedited_shipping charge without a correction → ostomy_ext_reship_correction.
4. refill_units ← notice_units. Sentence: "Where the extra barriers rest on no over-limit record, they are fixed only after the records carry a liability notice for the convex barrier signed on or after the newest written order's date."
   - "only after", with the scope "where … no over-limit record" matching extra_backing tier 1. Passes.
   - Only sign_liability_notice_87444016 (owner=user) creates `ostomy_liability_notice_signed`.
5. refill_units ← hardship_waiver. Sentence: "On a program whose past-due amount has reached the hold minimum, a refill is not shipped until the posting named on the most recently received approved hardship application carries its hardship waiver adjustment."
   - "not … until". Passes.
   - Only post_hardship_waiver_31941945 writes `hardship_waiver`.
- No rule carries a second wording of any edge, a tool name or another problem's id. No depended-on rule restates the blocked rule's sentence.
- No extended rule states a cross-problem order that grounds no edge. The "once … on file" clauses in denial_charge and expedite_fee wait on payer and shipment events, which no tool of this difficulty writes.
- Base `ostomy_liability_notice` also states "supplies it billable to the customer only after the customer signs … before the ship date". This is the same notice→refill order as edge 4, and the extended refill rule carries its own sentence, so it is an observation only (O12; see also the same-day reading there).

### override_declarations
Sentence by sentence against each `base_policy_refs` entry (only the sentences that govern a scored quantity are listed; every other sentence is followed by extended or not touched):
- ostomy_ext_plan_denial_charge vs base liability_notice: the charge-type parenthetical "non_covered_item (… charged at the Larkfield cash price of the units concerned)" is superseded and declared. The remaining sentences (OD-denial requirement on MA, the "without it … write-off" clause) are inherited and not weakened. Its replaced_by keeps the still-in-force part for every other non_covered_item charge. The other refs (quantity_limits, documentation, returns, claims, denials) only supply inputs; nothing undeclared was found.
- ostomy_ext_hardship_waiver (overwrite []) vs base patient_account: the base gates (tier allows, approved application, income check) are inherited. The base says "never for more than that posting's unpaid remainder". The extended waiver is ≤ waiver base × share ≤ the posting's amount less adjustments, and the rule asserts that payments have not reached the named posting. That assertion is a world claim, checked per task (it holds in task 0). Base claims: no conflict. No undeclared override found.
- ostomy_ext_plan_installment (overwrite []) vs base patient_account payment-plan sentence ("no more than payment_plan_max_months … of at least payment_plan_min_monthly_usd; … a request the customer accepts"): the extended rule stays inside both bounds (built months are capped at the tier maximum, and months fall to the floor at the minimum installment). Running-total definition: identical. Oldest-first payment application: not contradicted. No undeclared override found.
- ostomy_ext_refill_units: three declared overwrites:
  - supply days: declared.
  - units ("The units of each item are … or the written order's quantity when that is lower"): declared.
  - per-shipment confirmation: declared. It retires nothing (O1).
  - Undeclared: base ostomy_evt_quantity_limits also says "A quantity above the allowance is covered only when a medical record with purpose over_limit_justification … is dated no more than over_limit_record_months calendar months before the ship date; the allowance then becomes the quantity that record documents, and without it an above-allowance quantity ships only under ostomy_liability_notice at cash_price_by_item." This governs the scored `units`, and the extended rule handles it differently: a fixed "fewer than 6 whole calendar months" boundary instead of the tier's inclusive `over_limit_record_months`; "twelve 30-day blocks of the order's excess" as a cap, still multiplied by the step-up share, instead of "the allowance becomes the documented quantity". No overwrite names this sentence → **C5**.
  - Inherited unchanged: active-only, draw-on-one-grant, refill-too-early, coverage reverification, inpatient hold.
- ostomy_ext_notice_units: one declared overwrite (the customer signs personally), which retires nothing (O1). The base "on the Medicare Advantage tier no notice can make the member liable" / "On the self-pay tier no notice applies" is not overwritten, but the policy's scope is not limited to the tiers where a notice exists (O2). No task world reaches those tiers.
- ostomy_ext_expedite_fee: the declared overwrite of "Expedited shipping is provided … for expedited_shipping_fee_usd, posted as a patient charge". The base continuation "recorded as expedited_no_charge when the expedite only makes up for a delay Larkfield caused" is not superseded and stays in force; the scope restricts itself to refills "shipped expedited at the customer's own request". No undeclared override found.
- ostomy_ext_reship_correction: two declared overwrites ("never for more than that posting's unpaid remainder" for the service-recovery excess; the hardship gate kept for hardship waivers). The replaced_by keeps both still-in-force halves. No undeclared override found.

### factor_ladders
Structure only; weight is per task.
| policy | factor | label | tiers (fall-through last) | fall-through = baseline? | label honest? | multi-source (every non-fall-through tier a conjunction over distinct records)? | cross_difficulty |
|---|---|---|---|---|---|---|---|
| denial_charge | covered_count | method | PA-short grant (units×days/365, floor) / order<allowance (order×days/30) / allowance×days/30 | yes | yes (tier 1 is a different algorithm) | tier 1 grant+refill date (yes); tier 2 "no such grant" + order (yes) | — |
| | late_decision | parameter | >60 / 31–60 / ≤30 → 0.10/0.05/0 | yes | yes | no | — |
| | quantity_discount | parameter | ≥30 / 15–29 / <15 → 0.10/0.05/0 | yes | yes | no | — |
| | multiline_discount | parameter | active cont + ≥2 refills / active + <2 / else → 0.10/0.05/0 | yes | yes | yes (continence program + continence shipments) | continence |
| | tenure_courtesy | parameter | ≥36 m & no NC 24 m / 12–35 m & no NC / else → 15/5/0 | yes | yes | yes (program date + billing history) | — |
| hardship_waiver | repeat_assistance | parameter | ≥2 / 1 / 0 earlier waivers → 0.5/0.75/1.0 | yes | yes | no | — |
| | shared_need | parameter | active cont & bal≥100 / active & 0<bal<100 / else → 0.2/0.1/0 | yes | yes | yes | continence |
| | posting_age | parameter | >180 / 121–180 / ≤120 → 0.10/0.05/0 | yes | yes | yes (posting date + application date) | — |
| | supply_burden | parameter | ≥4 / 2–3 / <2 cont refills → 0.05/0.02/0 | yes | yes | no | continence |
| | payer_record_cap | parameter | ≥6 / 3–5 / <3 payments → 150/100/60 | yes | yes | no | — |
| | cap_window | **method** | enrolled ≥36 / 12–35 / <12 m → 12/18/24-month window | yes | **no**: only the window length (a number) changes inside the same SUM | no | — |
| plan_installment | pending_exclusion | method | corrected claim unremitted / first-level appeal undecided / none | yes | yes | yes (claim + remittance rows) | — |
| | balance_band | parameter | <250 / 250–499.99 / ≥500 → 3/5/tier max | yes | yes | no | — |
| | continence_term | parameter | active & bal>0 / active & bal≤0 / else → 2/1/0 | yes | yes | yes | continence |
| | assistance_term | parameter | approved/completed app 12 m / received app 12 m / else → 2/1/0 | yes | yes | no | — |
| | withdrawal_term | parameter | withdrawn ≤24 m / older only / none → 2/1/0 (subtracted) | yes | yes | no | — |
| | tenure_term | parameter | enrolled ≥60 / 36–59 / <36 m → 2/1/0 | yes | yes | no | — |
| refill_units | supply_alignment | method | cont supply end 30..std & grant ≥ std (blocks to cont end) / grant end 30..std (blocks to grant end) / std | yes | yes | tier 1 yes (continence program + continence refill + ostomy grant); tier 2 no | continence |
| | supply_start | method | lost-in-transit replacement / POD > 5 days late / ship date | yes | yes | tier 2 yes (refill + POD); tier 1 no | — |
| | usage_pace | parameter | prev refill above allowance (its rate) / order<allowance (order) / allowance | yes | yes | tier 2 yes | — |
| | step_up | parameter | order ≤60 d / 61–120 d / older → 0.5/0.75/1.0 | yes | yes | no | — |
| | extra_backing | parameter | over-limit record <6 m (12×excess) / notice ≥ order date (notice units) / 0 | yes | yes | tier 2 yes | — |
| notice_units | notice_span | method | order ≥360 d left & ≥2 refills (12) / order 30..359 d left (blocks to valid-through) / std blocks | yes | yes | tier 1 yes | — |
| | increase_blocks | **method** | order ≤60 d / 61–120 d / older → take off 1 / 0.5 / 0 blocks | yes | **no**: the tiers substitute 1, 0.5 or 0 into the same subtraction | no | — |
| | unused_cover | method | notice <12 m (deduct units − over-12 m) / 12–24 m (− over-24 m) / none | yes | yes (deduct vs not) | yes (notice + shipments) | — |
| | leakage_margin | parameter | ≥2 / 1 / 0 defect-or-damage replacements → 0.2/0.1/0 | yes | yes | no | — |
| | repeat_signer | parameter | ≥2 / 1 / 0 notices 24 m → 0.1/0.05/0 | yes | yes | no | — |
| expedite_fee | two_day_promise | **method** | ≤2 d / exactly 3 d / later or no POD → share 1 / 0.5 / 0 | **no**: the fall-through is "charge nothing" (0) but `baseline: delivery_share: K('full_share')` and baseline.rule says "The delivery share is the full share" | **no**: only the multiplier 1/0.5/0 changes | no | — |
| | first_expedite | parameter | only one / exactly two / else → 0.10/0.05/0 | yes | yes | no | — |
| | late_billing | parameter | >90 / 61–90 / ≤60 → 0.10/0.05/0 | yes | yes | no | — |
| | expedite_tenure | parameter | ≥36 / 12–35 / <12 → 0.05/0.02/0 | yes | yes | no | — |
| | continence_standing | parameter | active & bal≤0 / active & 0<bal<50 / else → 0.05/0.02/0 | yes | yes | yes | continence |
| | confirmation_delay | parameter | >10 / 6–10 / ≤5 → 0.20/0.10/0 | yes | yes | yes (confirmation + ship date) | — |
| reship_correction | error_kind | method | the only expedited charge on a no-charge shipment (whole charge) / ≥2 such charges (one charge, computed as average) / otherwise (part above the fee) | yes as written, but the fall-through is **unreachable** inside the policy's scope (C3) | yes as written | no | — |
| | recovery_tenure | parameter | ≥36 / 12–35 / <12 → 10/5/0 | yes | yes | no | — |
| | recovery_repeat | parameter | ≥2 / 1 / 0 corrections 12 m → 10/5/0 | yes | yes | no | — |
| | recovery_age | parameter | >60 / 31–60 / ≤30 → 5/2.5/0 | yes | yes | no | — |

- Declared counts per policy (factors / parameter / method): denial 5/4/1; hardship 6/5/1; installment 6/5/1; refill 5/3/2; notice 5/2/3; expedite 6/5/1; reship 4/3/1.
- Counts surviving the tests above:
  - hardship 6/5/**0** (cap_window mislabelled);
  - notice 5/3/2 (increase_blocks counts as a parameter);
  - expedite 6/6/**0** (two_day_promise mislabelled, and its fall-through is not the baseline);
  - reship **3**/3/**0** (error_kind struck as an unreal ladder);
  - denial, installment and refill unchanged and within bounds.
- Every `decides` is an input, never `result`.
- Bindings are disjoint within each policy.
- No factor binding reads another factor's binding or output. Traced transitively: refill extra_backing reads the order directly; installment pending_exclusion reads cc_/ap_ rows only; hardship cap_room combines cap_window and payer_record_cap outside both.
- Observation O9: installment `balance_band` lists `ledger_debits`/`ledger_credits` as its own bindings, yet the baseline's `balance_due` → `financed` → `result` reads those same two bindings. The baseline's core quantity is therefore assembled from bindings declared as owned by a factor. Substituting the factor's baseline (`band_months`) does not touch them, so this has no score consequence.
- No two tiers of any ladder select the same value or method.
- Realism (condition and outcome of every tier):
  - The industry-plausible ones: tenure and good-standing courtesies, payer-lag and billing-lag courtesies, multi-line discounts, total-debt and assistance plan lengthening, withdrawal shortening, on-hand deduction, delivery-date anchoring, shipment synchronisation with the continence line, documentation or notice backing of over-limit quantities, delivery-promise refunds, service-recovery credits.
  - Observation O10 (borderline realism, not demonstrable as RED):
    - refill step_up and notice increase_blocks ship or cover only half or three quarters of a newly prescribed increase for 60–120 days. A DME supplier normally ships the ordered quantity subject to payer limits.
    - expedite continence_standing reduces an ostomy expedite fee by the state of the continence account.
  - The one realism RED is error_kind (C3).

### findings
- **C1 — SOURCE-FACTOR RED (dishonest baseline: fall-through ≠ baseline)**
  - Symptom / root cause: ostomy_ext_expedite_fee.two_day_promise has a fall-through tier, "otherwise (later, or no proof of delivery) → charge nothing" (`delivery_share` 0), but its declared `baseline: delivery_share: K('full_share')`. baseline.rule states "The delivery share is the full share", which is tier 1, not the fall-through.
  - Evidence: ostomy.extended.yaml lines 3824–3843 and 3938–3941.
  - Consequence: the rule that every factor's fall-through is the baseline fails. A reader who never finds the factor document applies the full share. A customer outside the 2-day and 3-day tiers is then on a tier (0) different from the baseline (1), so the factor's "baseline" is not its fall-through.
  - Bears on: task 1 (expedite charge in its tree).
- **C2 — SOURCE-FACTOR RED (mislabelled method; class list)**
  - These factors labelled `method` only substitute a number into one formula:
    1. ostomy_ext_expedite_fee.two_day_promise: multiplier 1 / 0.5 / 0. It is the policy's only method, so expedite_fee keeps **0** honest methods (lines 3824–3843).
    2. ostomy_ext_hardship_waiver.cap_window: `within_months` 12 / 18 / 24 in the same SUM. It is the policy's only method, so hardship_waiver keeps **0** honest methods (lines 2540–2559 and the `cap_used` compute).
    3. ostomy_ext_notice_units.increase_blocks: 1 / 0.5 / 0 blocks subtracted. notice_units keeps 2 honest methods (notice_span, unused_cover), so its counts are not affected (lines 3564–3582).
  - Consequence: expedite_fee and hardship_waiver fail "at least 1 method" once the labels are honest.
  - Bears on: task 1 (member 1), task 0 (members 2 and 3).
- **C3 — SOURCE-FACTOR RED (unreal ladder) on ostomy_ext_reship_correction.error_kind**
  - Symptom / root cause: the policy is owed only when "an expedited shipping charge stands against the program's most recent shipment sent with the shipping method expedited at no charge". Every customer who reaches the write therefore has `err_charges_on_ship ≥ 1`.
    - Tier 1's condition "on a shipment sent expedited at no charge" holds of every such customer. It restates the scope.
    - The fall-through "otherwise the part of the charge above the tier's expedited shipping fee", which is also the baseline, applies to no customer who reaches the write: `corrected_part`'s third branch runs only when `nc_ship_id == None`, and then `err_id == None` and `result` = 0.
    - On a shipment Larkfield sent at no charge, a business reverses the wrongly posted charge in full. Correcting only the excess over the published fee (0.00 for a charge equal to the fee) is not a treatment it would publish.
    - Tier 2 ("one charge's amount (the duplicate)") leaves an expedited charge standing on a shipment that by definition carries none.
  - Evidence: rule lines 4007–4012; compute `corrected_part`, `result` (lines 4031–4047).
  - Consequence: error_kind is struck. reship_correction keeps 3 factors, all `parameter`, which is below "4 to 6" and "≥1 method".
  - Bears on: task 1.
- **C4 — SOURCE-POLICY RED (rule/compute non-equivalence: tier allowance hard-coded)**
  - ostomy_ext_refill_units and ostomy_ext_notice_units state "the tier's allowance" throughout (e.g. "The covered barriers are the lower of the newest written order's quantity per 30 days and the tier's allowance"; "the newest written order's quantity per 30 days less the tier's allowance"). Compute uses `K('convex_allowance_per_30')` = 20 in every place.
  - Neither policy is scoped to a tier. The A4407 allowance is 15 on the Ostomy Commercial HMO Program and 10 on the Ostomy Medicaid Program (lines 313–314, 549–550).
  - Second situation: a Medicaid program with a 20-per-30 order. The rule gives excess 10 and covered 10 per 30 days; compute gives excess 0 and covered 20.
  - Class members:
    - refill_units: `excess_per30`, `covered_barriers`, and the `on_hand_rate` tier thresholds and fall-through;
    - notice_units: `excess_per30`, `over_12m`, `over_24m`.
  - plan_denial_charge is not a member (scoped to Medicare Advantage, where the allowance is 20).
  - Bears on no current task's scored value, because both worlds are on tiers with allowance 20 (task 0 Original Medicare, task 1 Medicare Advantage).
- **C5 — SOURCE-POLICY RED (undeclared override)**
  - ostomy_ext_refill_units handles the base ostomy_evt_quantity_limits over-limit sentence differently and does not name it (quoted under override_declarations).
  - Second situation: a Commercial PPO A4407 program, order 30 per 30 signed 30 days ago, an over_limit_justification record documenting 30 dated exactly 6 months ago, 90-day supply.
    - Base: the record is within "no more than 6 months", so the allowance becomes 30 and units = 90.
    - Extended: the record is not "fewer than 6 whole calendar months" old, so with no notice the extra cover is 0 and units = 60.
    - With a 2-month-old record, base gives 90 and extended gives 60 + int(10×0.5×3) = 75.
  - Bears on no current task's scored value: in task 0 the only over-limit record is 7 months old, and both readings exclude it.
- Observations (charter-global, no demonstrated score consequence):
  - O1: two declared overwrites retire nothing: refill_units' confirmation overwrite and notice_units' signing overwrite. Their replaced_by repeats the base clause and adds "for the enrollment the representative names to them".
  - O2: notice_units is not scoped away from tiers with no signable notice, and the tool enum covers only three forms (see action_binding_and_uuids).
  - O3: unused_cover. The rule says "signed more than 12 and at most 24 months ago". Compute uses `prior_notice_months >= 12 and < 24` whole months, so a notice exactly 24 months old is tier 2 by the rule and "none" by compute.
  - O4: reship tier 2 says "one charge's amount (the duplicate)", but compute uses `err_amount / err_charges_on_ship`, an average that differs when the duplicates differ.
  - O5: plan_denial_charge's rule says "owed once the plan's organization determination denial for the convex barrier is on file …". No compute binding reads `ostomy_prior_auth_denial`, so the gate is enforced by prose only.
  - O6: see prerequisite_graph.
  - O7: base ostomy_holds_and_closure offers a hold, or a cure by "an approved payment plan", for a past-due program. refill_units' gate names only the hardship waiver. Neither difficulty has a hold tool, so I see no second scored path.
  - O8: cap_window's prose says "counts the hardship waivers posted", but compute sums their amounts. The "assistance cap room is the assistance cap less the hardship waivers already posted" fixes the amount reading.
  - O9, O10: see factor_ladders.
  - O12: base liability_notice says "signs … before the ship date", while its charge clause says "signed on or before the ship date". A same-day notice is admissible under the latter.

## closing_checklist
Written after both reveals (2026-10-15, revision 1). This section is the only post-reveal content in this file.
- Per-task files 0.md and 1.md exist one-to-one with tasks 0 and 1, beside this file. This is the first revision; there is no older one.
- Scopes (charter_scope, revealed):
  - task 0 = {hardship_waiver, notice_units, refill_units};
  - task 1 = {plan_denial_charge, expedite_fee, reship_correction, plan_installment}.
  - They are pairwise disjoint, together cover all 7 extended policies, and match the blind trees.
- Task tools and GT are closed. uuid8s are independent (§ action_binding_and_uuids).
- Trees:
  - task 0 n=2, value_input 1, owner=user notice;
  - task 1 n=3, value_input 3, owner=user plan;
  - the difficulty graph is acyclic.
- **Not closed.** Both tasks carry SOURCE-FACTOR REDs:
  - task 0 F0-1, F0-2;
  - task 1 F1-1, F1-2, F1-3.
  - The charter also carries C1–C5.
- Instantiation gates were not re-run by this auditor; the input supplied the snapshot. A re-run on the final form belongs after rework.
- No blind derivation differed from GT on any value. Every scored argument and every factor_sensitivity figure matched.

## revision_2
Re-audit round 2, written before any round-2 GT was read. The revision_1 text above is left untouched.

### charter_global_frozen (revision 2)
- Hashes (verified):
  - `ostomy.extended.yaml` be45c416849418f8b4304fba035c2f9f4ba043b4b85f3efd38ac6791f547749b (**changed**, so every charter-global section is re-derived);
  - `task_tools.py` b6e4229c0123246773c5a0596696158490dc019f153acd4eb0233e22cce85a8b (**unchanged**, so revision 1's § action_binding_and_uuids carries forward on this hash);
  - views 0 84e7d307…ec257e and 1 27f5be91…ec045f871. They mask the same keys as in round 1.
- The base copy is still verbatim (diff against `blueprint/products/ostomy.yaml`: trailing blank line only).
- The mechanical sweep (`/tmp/audit_ostomy_0063/verb.py`) is clean for all seven policies: compute_basis, baseline.rule, policy_source and replaced_by are all verbatim in each rule; every superseded_clause is verbatim in its base; every binding has a basis.
- Entry: the gate snapshot came with the brief. TRACEABILITY NOT OK only on the unlock tool names (E1 unchanged).

### round-1 RED closure (charter-global)
| id | round-1 defect | round-2 evidence | status |
|---|---|---|---|
| C1 | two_day_promise fall-through (0) ≠ baseline (full) | Ladder is now "no proof of delivery → charge nothing / more than 2 days → full less ¼ per day beyond the second, never below nothing / otherwise (within 2 days) → full". Baseline `delivery_share: K('full_share')` = fall-through. Compute `delivery_share` matches. | **closed** |
| C2-1 | two_day_promise mislabelled method | Tier 2 is now a per-day linear rule (1 − 0.25 × (days − 2)), tier 1 a constant 0 and tier 3 the constant full share, so how the share is computed changes. expedite_fee: 6 factors / 5 parameter / 1 method. | **closed** |
| C2-2 | cap_window mislabelled method | Now `effect: parameter`, deciding `window_months` (12 / 18 / 24). The method role passes to shared_need: flat 0.20 / balance ÷ 500.00 / nothing, which is a distinct algorithm. hardship: 6 / 5 / 1. | **closed** |
| C2-3 | increase_blocks mislabelled method | Now `effect: parameter`. unused_cover is also relabelled parameter. notice: 5 factors / 4 parameter / 1 method (notice_span). | **closed** |
| C3 | error_kind unreal ladder | error_kind is removed. The correction is now "the whole charge plus the service-recovery amount". Factors: recovery_tenure (p), recovery_repeat (p), recovery_age (**method**: per whole 30 days beyond 60 / once for 31–60 / nothing), reship_reason (p: lost 10.00 / damaged 5.00 / else 0). That is 4 / 3 / 1. Every fall-through is 0 = baseline, and baseline.rule ("the whole charge …; there is no service-recovery amount") is definite. | **closed** |
| C4 | allowance hard-coded 20 | Each of refill_units, notice_units and plan_denial_charge now has a `tier_allowance` binding (Medicaid 10 / HMO 15 / else 20, keyed on `variant_name`) that replaces every former `K('convex_allowance_per_30')`. Each rule carries the verbatim sentence "The tier's allowance for the convex barrier is … 20 on the Self-Pay, Commercial PPO, Medicare Advantage and Original Medicare tiers, 15 on the Commercial HMO tier and 10 on the Medicaid tier", which matches variant lines 244/313/372/431/490/549. | **closed** |
| C5 | undeclared override of the base over-limit-record sentence | A fourth refill_units overwrite now names the superseded clause verbatim ("A quantity above the allowance is covered only when … at cash_price_by_item."). Its replaced_by scopes the change to A4407 refills ("backed and stepped as this policy states, a medical record counting only while it is fewer than the tier's over-limit record months old in whole calendar months") and restates the base clause for every other refill. Compute: `record_months < P('over_limit_record_months')`, a tier parameter (0 on self-pay, so no record ever counts there). The merged semantics are unique. | **closed** |

### round-1 observations (charter-global)
- **O1 (coordinator decision: keep).** Judged on wording and scope alone:
  - Both overwrites are self-scoped ("For a convex-barrier (A4407) refill this policy handles, and only for such a refill" / "For a liability notice this policy handles, and only for such a notice").
  - Both replaced_by sentences carry the base clause in full for every other refill or notice and drop no still-in-force part.
  - The added phrase "for the enrollment the representative names to them" matches the two owner=user tools, whose `ostomy_program_id` is "as the representative reads it from the enrollment lookup and tells the customer".
  - No defect.
- O2 closed. The notice rule now says "This policy applies only on tiers whose liability notice is one the customer can sign … on the Medicare Advantage tier no notice can make the member liable and on the self-pay tier no notice applies, so no notice units are fixed there". The compute gate `signable_tier` covers the same three forms as the tool enum.
- O3 closed. Tiers are now "fewer than 12 whole calendar months" / "12 to 23 whole calendar months", identical to `< 12` / `>= 12 and < 24`.
- O4 closed: the duplicate tier is gone.
- O5 closed. `od_denials` = COUNT of A4407 `ostomy_prior_auth_denial`, and `result` is 0 when it is 0, quoting "The charge is owed once the plan's organization determination denial for the convex barrier is on file".
- O6 closed in substance. The refill → waiver `condition` now states only what the sentence states (the named posting carries a hardship_waiver adjustment). `gate` is the record field `ostomy_billing.adjustment_reason`, which is the waited-on state.
- O8 closed. The prose now says "adds up the amounts of the hardship waivers posted in the last 12 months …".
- O9 closed. balance_band now decides from its own `band_balance` binding (the same running total, computed separately). `balance_due` / `ledger_*` are no longer factor bindings.
- O7, O10 and O12 are unchanged (no claim was made on them).

### fresh scan for new defects (revision 2)
- Conflict scan: the subjects, target tools and computed quantities of the seven policies are unchanged, so the overlap analysis in revision 1 still holds. No new overlap.
- rule ↔ compute, re-swept on the changed bindings:
  - `tier_allowance` ×3.
  - `od_denials`.
  - hardship: `need_share` (tier 2 = `cont_balance / K('need_scale_balance')`, 500.00), `window_months` → `cap_used`.
  - installment: `band_balance`.
  - refill: `extra_cover` uses `P('over_limit_record_months')`. The empty-record guards (`order_qty`/`prev_*` default 0, `supply_anchor` = NOW without a previous refill) match the new sentence "A program without a written order … gets no covered or extra barriers, and a program with no earlier convex-barrier refill has no barriers still on hand".
  - notice: `signable_tier`.
  - expedite: `delivery_share` (POD absent → 0; > 2 days → MX(0, 1 − 0.25 × (days − 2)); else 1).
  - reship: `err_amount` = the named charge's amount, "where more than one stands, the most recently posted one" = `err_id` LATEST by posting_date; `age_recovery` = 2.5 × int(age/30) above 60, 2.5 for 31–60, else 0; `reason_recovery` from the latest expedited_no_charge shipment's `replacement_reason`.
  - Each matches its rule sentence, and no compute branch lacks a rule sentence.
- Rounding placement is unchanged, except that need_share is now fractional before the final RND, which the rule allows ("the waiver is rounded to the cent").
- Prerequisite graph and sentences: unchanged edges and sentences (verbatim). Only the refill → waiver `gate`/`condition` changed (see O6).
- Factor ladders (revision 2). Per policy, factors / parameter / method:
  - denial 5 / 4 / 1;
  - hardship 6 / 5 / 1;
  - installment 6 / 5 / 1;
  - refill 5 / 3 / 2;
  - notice 5 / 4 / 1;
  - expedite 6 / 5 / 1;
  - reship 4 / 3 / 1.
  - Every fall-through equals its declared baseline. No two tiers select the same value or method.
  - Realism of the new tiers: proportional need share, a per-day refund on a missed two-day promise, refusal to charge without proof of delivery, an age-scaled service-recovery credit, and a larger recovery for a lost than for a damaged package are all treatments a supplier plausibly publishes. O10 stands unchanged for step_up and continence_standing.
- New observation O13: the denial charge's `od_denials` counts any A4407 organization-determination denial on the program. It does not tie it to the denied refill's order. No task world carries an unrelated denial.

### findings (revision 2)
- No charter-global RED remains. C1–C5 are closed.

### closing_checklist (revision 2)
Written after both round-2 reveals.
- Per-task files: 0.md and 1.md each carry revision_2 with a frozen derivation and a GT comparison, and both comparisons are PASS. The revision_1 text is preserved.
- Scopes are disjoint and complete: task 0 = {hardship_waiver, notice_units, refill_units}; task 1 = {plan_denial_charge, expedite_fee, reship_correction, plan_installment}, which covers all 7 extended policies.
- Task tools are unchanged (b6e4229c…). The 7 uuid8s are independent.
- Trees:
  - task 0 has 2 prerequisites, 1 value_input and the user's notice;
  - task 1 has 3 prerequisites, 3 value_input and the user's plan;
  - the graph is acyclic.
- Every computation has 4–6 factors with ≥ 2 parameter and ≥ 1 honest method, every fall-through equal to its baseline, every factor bearing weight, and every all-baseline figure definite and different from gold.
  - Task 0 multi-source / cross-difficulty factor: shared_need, supply_alignment, supply_burden (continence).
  - Task 1: multiline_discount, continence_term, continence_standing.
- Gates: the coordinator's round-2 snapshot is all OK except TRACEABILITY, which is pending only on the unlock tool names until the KB renders. This auditor did not re-run the gates.
- Result: the difficulty passes the source-layer audit on revision 2, subject to that traceability item. No charter RED remains. The surviving observations (O7, O10, O12, O13, E1) carry no demonstrated consequence.

## revision_3
Re-audit round 3, after the KB render. Written before any round-3 GT was read. Revisions 1 and 2 are left untouched.

### charter_global_frozen (revision 3)
- Hashes (verified):
  - `ostomy.extended.yaml` 20123830a6209f84624e979502b7e93029202b87afaac2442e16364426c898a8 (**changed**, so the charter-global sections are re-derived on the changed bindings);
  - `task_tools.py` b6e4229c… (unchanged, so revision 1 § action_binding_and_uuids carries forward);
  - views 84e7d307… / 27f5be91… (unchanged).
- Inputs also read, as the coordinator permitted: `audits/render_source/ostomy_supply_program_services/findings.md` and the source-side sections of `audits/policy_kb/ostomy_supply_program_services/{0,1}.md` (R1–R6, BN1/BN2, S7, E1).
  - Those files quote task row ids and some world figures. Both tasks' GT was already revealed to me in revisions 1–2, and the views are unchanged, so this adds no new contamination. It is disclosed here.
- Base copy: still verbatim.
- Mechanical sweep (`verb.py`): clean on all seven policies.
- Gate snapshot: all OK, **including TRACEABILITY**. E1 (the traceability entry item) is therefore closed.

### closure of the KB-confirmed source items
| id | item | round-3 evidence | status |
|---|---|---|---|
| R1 | reship_correction overwrite[1] retired the hardship-waiver gate while keeping it in force | That overwrite is **removed**. The only overwrite left is "each against the one posting it adjusts and never for more than that posting's unpaid remainder". The rule no longer carries the "needs no hardship application" sentence. The base sentence "A hardship waiver is granted only … " governs hardship waivers, and this policy posts only billing_correction. | **closed** |
| R2 | withdrawal_term dated by received_at while the rule said "withdrawn in the last 24 months" | The rule now reads "a payment plan request of the program received in the last 24 months and since withdrawn … a withdrawn payment plan request received more than 24 months ago with none received in the last 24 months". This equals the compute (`date_field='received_at'`, `request_status='withdrawn'`). The rule now names a record field the rows carry. | **closed** |
| R3 | an overturning first-level decision was undefined | The rule now says "neither an upheld decision (a new denial posted against the appeal filing) nor an overturning one (a second remittance posted on the appealed claim)". New binding `ap_remits` = COUNT of remittances on the appealed claim. `left_out` requires `ap_remits < 2`. `ap_remits` is added to pending_exclusion's bindings, and its compute_basis is verbatim. | **closed** |
| R4 | refill grant not tied to the newest order | New `newest_order_id` = LATEST A4407 `ostomy_order_receipt` by order_date. `grant_id` and `grant_through` filter on `related_ostomy_order_id=newest_order_id`. Both quote "The refill draws on the authorization grant recorded on the newest written order for the convex barrier." | **closed** |
| R5 | "this refill included" not guaranteed | The rule now says "counted together with this refill even when it shipped earlier than that". `other_expedites` adds 1 when MONTHS(ex_ship_date, NOW) ≥ 12. | **closed** |
| R6 | tier scope absent from compute | denial `result`: 0 unless `F('variant_name') == 'Ostomy Medicare Advantage Program'`. hardship `result`: 0 unless `P('hardship_waiver_allowed')`. Both quote their scope sentences verbatim. | **closed** |
| S7 | the notice rule described the refill's step-up | The sentence is now "The step-up blocks shorten the part of the notice's span counted at the full excess after the newest written order raised the quantity: …". It describes only the notice's own blocks. | **closed** |
| E1 (KB) | factor doc carried a truncated overwrite-4 replaced_by pointing at "the program's convex-barrier refill rule" | The replaced_by is now self-contained: "a medical record with purpose over-limit justification backs the barriers above the allowance only while it is fewer than the tier's over-limit record months old in whole calendar months, and it backs at most twelve 30-day blocks of the order's excess instead of raising the allowance; for every other refill …". It no longer points at "this policy". The merged semantics with extra_backing tier 1 (12 × excess, `record_months < P('over_limit_record_months')`) are unique. | **closed** |
| BN1, BN2 | base wording ("before"/"on or before"; "at"/"more than") | Base, BLUEPRINT-KNOWN. They are the same as my O12, and non-bearing in both worlds (task 0's notice is signed and shipped the same day under the "on or before" eligibility; no posting is exactly 120 days old). | observation, unchanged |

### regression scan (revision 3)
- Factor tables: all seven policies have the same factors, labels, decides and tier outcomes as in revision 2.
  - Counts: denial 5/4/1, hardship 6/5/1, installment 6/5/1, refill 5/3/2, notice 5/4/1, expedite 6/5/1, reship 4/3/1.
  - Every fall-through equals its baseline.
  - Only pending_exclusion gained a binding (`ap_remits`). It reads remittance rows and no other factor's binding.
- Prerequisite edges and sentences: unchanged and verbatim.
- New and changed bindings (`newest_order_id`, `ap_remits`, the `other_expedites` term, the two `result` guards) each have a verbatim basis and introduce no branch the rule lacks.
- Observation O14 (base metadata, BLUEPRINT-level): base eligibility `hardship_approved` and `small_balance_ceiling` declare `applies_to: [ostomy_balance_adjustment]`, which structurally includes billing corrections. Their condition sentences ("A hardship waiver is granted only …", "A small-balance write-off is made only …") limit them to their own reasons. With the R1 overwrite gone, no published sentence gates a billing correction on a hardship application, so this gives no second answer.
- O13 (an organization-determination denial not tied to the denied refill's order) is unchanged. O7 and O10 are unchanged.

### findings (revision 3)
- No charter-global RED. R1–R6, S7 and E1 are closed. BN1/BN2 remain base observations.

### closing_checklist (revision 3)
Written after both round-3 reveals.
- Both task files carry a revision_3 comparison, and both are PASS. Scopes are disjoint and complete, as in revision 2. Tools are unchanged.
- Trees, factor counts, baselines and weights are unchanged from revision 2 (see the per-task files).
- Gates (coordinator's round-3 snapshot): all OK, including TRACEABILITY.
- The difficulty passes the source-layer audit.
- Open observations (not REDs): O7, O10, O12 (= BN1/BN2), O13, O14, and O-STALE (two GT tier labels carry superseded ladder wording: task 0 unused_cover, task 1 withdrawal_term).

## revision_4
Re-audit round 4 (S8 closure and the XF rewording per `audits/render_source/XF_recipe.md`). Written before any round-4 GT was read. Revisions 1–3 are left untouched.

### charter_global_frozen (revision 4)
- Hashes (verified):
  - `ostomy.extended.yaml` c169ef16ba0b815daa6628cabcf70dec675b634c3bd1dc15eb4a56159b377fd3 (changed). A frozen copy is at `/tmp/audit_ostomy_0063/ext_r4.yaml`.
  - `task_tools.py` b6e4229c… (unchanged).
  - views 84e7d307… / 27f5be91… (unchanged).
- Also read: `XF_recipe.md`, and S8 in `audits/policy_kb/ostomy_supply_program_services/0.md`.
- contamination_disclosure: GT was already known from revisions 1–3; the views are unchanged.
- Base copy: verbatim. Gate snapshot: all OK.

### compute unchanged (independent replay)
- I replayed every policy's compute with the DSL evaluator (`check_compute.build_env` / `eval_compute` / `substitute`, driven by my own script `/tmp/audit_ostomy_0063/r4/ev.py`).
- Inputs: the unchanged views, with my own handling-time rows inserted (task 0: the 100-unit notice and the 16.44 waiver; task 1: the three postings).
- Every scored value, every single-factor sensitivity and every all-baseline figure equals revision 2/3, figure for figure:
  - waiver 16.44 [25.00, 15.00, 15.19, 15.19, 0.00, 3.29], baseline 0.00;
  - notice 100 [8, 111, 115, 90, 95], baseline 30;
  - refill 45 [70, 50, 46, 55, 35], baseline 60;
  - charge 236.10 [171.00, 252.84, 269.58, 269.58, 251.10], baseline 248.00;
  - expedite 11.58 [15.44, 13.41, 13.41, 12.50, 11.94, 13.41], baseline 24.50;
  - correction 49.50 [39.50, 44.50, 44.50, 44.50], baseline 24.50;
  - plan 40.96 [53.28, 32.77, 54.61, 54.61, 32.77, 46.81], baseline 42.63.
- Every all-baseline figure is definite and differs from gold.

### rule ↔ compute after the rewording (sentence by sentence, all seven policies)
- Mechanical sweep (`verb.py`): every compute_basis quote, baseline.rule sentence, policy_source and replaced_by is verbatim in its rule; every superseded_clause is verbatim in its base.
- Standard method (baseline.rule) per policy. Each reads only records and default figures and yields a definite number:
  - **denial:** concerned = shipped − received back − allowance × days/30; charge = concerned × cash price. (Typo "The the barriers concerned", in the rule and baseline both; O15, cosmetic.)
  - **hardship:** the waiver base up to the cap room (default cap less the waivers of the last 24 months), with no share. This matches compute with every share at its baseline: MN(1, 1 + 0 + 0 + 0) = 1.
  - **installment:** the balance due over the tier's longest months, reduced at the minimum installment.
  - **refill:** covered barriers (min(order, allowance) × standard days/30) less the barriers on hand (allowance × days left from the ship-date anchor).
    - "Extra barriers" are defined as a standard quantity: order excess × standard days/30, rounded down.
    - The standard units do not use them. The extra_backing sentence adds them capped by the cover, and the step-up sentence multiplies the excess inside them.
    - compute: `extra_barriers = MN(extra_cover, int(excess × step × days/30))`, `result = covered + extra − on_hand`. With the baseline cover of 0 this equals the standard method.
    - Observation O16: a standard-method quantity the standard total does not use. This is allowed by recipe item 2, since two factors read it.
  - **notice:** excess × standard blocks, rounded down.
  - **expedite:** the tier fee.
  - **correction:** the whole charge.
- Factor sentences each state how they change the standard amount ("replace … in the barriers concerned", "comes off the cash price", "adds … to the share that multiplies the capped waiver base", "replaces the default cap / the last 24 months in the cap room", "replaces the tier's longest number of monthly installments", "lengthen/shorten the plan", "replace the tier's standard supply days", "in place of its ship date", "replaces the tier's allowance in the barriers still on hand", "multiplies the order's excess per 30 days in the extra barriers", "are added to the standard units, never more than the extra cover", "replaces the one standard supply of 30-day blocks", "taken off the 30-day blocks", "added to the excess, as a share of it", "multiplies the fee", "taken off the fee", "adds to the whole charge"). Each matches the corresponding compute branch and its position in `result`.
- Combination sentences: one per policy, generic, naming no factor quantity. The order each states matches compute:
  - denial: rates summed once, round, then deduct, then round;
  - hardship: shares summed and capped at full, multiply once, round;
  - installment: month terms combined, clamped to [1, tier max], then the minimum-installment floor; exclusions before financing;
  - refill: replacements and multipliers before units, floor 0;
  - notice: block and share changes before the round-down, deductions after;
  - expedite: share × fee × (1 − Σ rates);
  - correction: parts added, then round.
- Scan for XF (recipe item 6):
  - No non-factor compute_basis quote names a factor quantity (term scan over 35 factor names: no hit).
  - No factor binding reads another factor's binding. The single regex hit, usage_pace `prev_rate_days` on "supply_days", is the shipment record's field literal in `LATEST('ostomy_shipments','supply_days',…)`, not the supply_alignment binding: the same false positive as the KB audit's RD3.
  - Assembly bindings (`barriers_concerned`, `reduced_amount`, `assist_share`, `cap_room`, `cap_used`, `financed`, `built_months`, `covered_barriers`, `extra_barriers`, `days_left`, `on_hand_barriers`) read factor outputs, as the result must.
  - No rule defines a quantity "as another policy figures it".
- S8 **closed**. The refill rule and its baseline now say "The refill draws on the authorization grant recorded on the newest written order for the convex barrier (the program's written order for A4407 with the latest order date); where more than one grant is recorded on that order, the one with the latest decision date". This equals `newest_order_id` (LATEST by order_date) plus `grant_id` (LATEST by decision_date filtered on that order).
- Prerequisite edges, kinds and gates are unchanged, and their sentences are verbatim. Factor labels, counts and ladders are unchanged (7 policies: 5/4/1, 6/5/1, 6/5/1, 5/3/2, 5/4/1, 6/5/1, 4/3/1).
- Observation O17 (wording risk, no second answer):
  - The installment band sentence says the band "replaces the tier's longest number of monthly installments". The clamp sentence separately holds the combined number to "no more than the tier's longest number of monthly installments".
  - A reader who carries the replacement into the clamp would cap task 1 at 5 months (65.54) instead of 8.
  - The clamp sentence names the tier figure in its own words, and the band sentence applies to the standard plan length. So I read it as one meaning, with 8 as the result.

### findings (revision 4)
- No charter-global RED. S8 is closed, the XF rewording preserves meaning, and nothing regressed.
- New observations O15–O17 are cosmetic or wording risks.

### closing_checklist (revision 4)
- Both task files carry a revision_4 comparison, and both are PASS.
- Scopes, tools, trees, factor counts, baselines and sensitivities are unchanged and re-verified by replay.
- Gates: all OK (coordinator snapshot).
- Open observations (not REDs): O7, O10, O12 (BN1/BN2), O13, O14, O15 (typo "The the"), O16, O17, and O-STALE (two GT tier labels with superseded ladder wording, unchanged since revision 3).
VERDICT revision_4: task0=PASS task1=PASS charter=CLEAN
