# Policy-task audit — continence_supply_program_services / charter-global

## charter_global_frozen

- Freeze time: 2026-10-15T00:16Z (written before any task's GT was revealed; nothing in this section is derived from a revealed GT).
- Auditor: independent erl-task-policy-audit agent (did not author any artifact of this difficulty).
- Hashes (sha256):
  - `tasks/continence_supply_program_services/continence.extended.yaml` b6925ede6d027aaf4b17d661d7402558b0f0dc7792cfc1a49b9987bd584b2ce6 (matches the brief)
  - `tasks/continence_supply_program_services/task_tools.py` 4c9f02d3e9c5ddbc73962491051f92f71f2f5506501885248856e39217749180 (matches the brief)
  - `blueprint/products/continence.yaml` 576db87a24def04ed90214fc7c81efe6ec1c0a6b5fa9d0e129631df7c45491a7
- Read: blueprint (blueprint.yaml scope entry, continence/ostomy/cgm charters, db_schema.json request enums, share_tools.py signatures), the extended charter, task_tools.py, the two masked views, and `skills/erl-task-instantiate/scripts/check_compute.py` (DSL semantics only: `within_months` = whole calendar months `0 <= MONTHS(d, NOW) < N`; `MONTHS` drops a partial month; `LATEST` = row with the greatest `date_field`).
- Masked / not read: every `tasks/<i>.json`, `worklog.md`, the instantiator's scratch, sibling difficulties' tasks/ directories, other scenarios, prior audits (none existed).
- Step 0 entry conditions: the brief carried the gate snapshot (EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK; TRACEABILITY NOT OK only for the unlock tool names, deferred to step 3) and the masked views with hashes; view hashes re-checked and match. Entry conditions complete. Base section of the extended charter (lines 1-1986) is byte-identical to `blueprint/products/continence.yaml` (only the separator comment block differs).

### policy_conflict_scan

Six extended policies (all base policies they cite are inherited unless named in `overwrite`):

| policy | trigger | target_tool (owner) | computes | tier | prerequisite |
| --- | --- | --- | --- | --- | --- |
| continence_ext_straight_catheter_refill | on_request | ship_catheter_refill_863073b5 (agent) | units | Original Medicare | abn_quantity_notice (value_input), hardship_waiver (state_gate) |
| continence_ext_abn_quantity_notice | on_request | sign_liability_notice_4a664827 (user) | notice_units | Original Medicare | [] |
| continence_ext_hardship_waiver | state_due | post_hardship_waiver_d1a5476f (agent) | amount | hardship-allowed tiers | [] |
| continence_ext_noncovered_catheter_charge | state_due | post_noncovered_charge_0f5c8cfb (agent) | amount | Commercial HMO | [] |
| continence_ext_returned_unit_credit | state_due | post_return_credit_03d701bf (agent) | amount | Commercial HMO | [] |
| continence_ext_payment_plan_installment | on_request | accept_payment_plan_f3b8d099 (user) | monthly_amount_usd | Commercial HMO | noncovered_catheter_charge (value_input), returned_unit_credit (value_input) |

- Overlapping subjects: hardship_waiver and returned_unit_credit both write `continence_balance_adjustment`, distinguished by `adjustment_reason` (hardship_waiver vs return_credit) and by their tools; their overwrites of `continence_evt_patient_account` each carve out the other by name ("every balance adjustment other than such a hardship waiver and a return credit ..."), so the carve-outs are mutually consistent. abn_quantity_notice (Original Medicare, ABN) and noncovered_catheter_charge (Commercial HMO, plan member waiver) both read `continence_liability_notice_signed` rows but on disjoint tiers.
- Triggers / time anchors: every policy evaluates at the call's frozen date; the three state_due policies say "posted as soon as it is found / the denial stands / the receipt stands, whatever the customer called about".
- Cross-category reads: refill reads ostomy (status, ostomy refill ship date and supply days); hardship_waiver reads ostomy (status, balance due, hardship application); noncovered charge, return credit and payment plan read cgm (hardship applications, status, balance, withdrawn payment plans). All read-only; no policy writes another category.
- Scope: the two problem trees implied by `prerequisite` are {refill, abn_quantity_notice, hardship_waiver} and {payment_plan, noncovered_charge, returned_unit_credit}: pairwise disjoint, together covering all six extended policies. (Which task claims which tree is confirmed per task from its world; charter_scope is masked.)
- Conflicts found: see findings C1, C3, C6 below.

### rule_compute_equivalence

Mechanical check (scratch script `/tmp/audit_continence_0063/scripts/`): every `compute_basis` quotation is a verbatim substring of its policy's `rule`; every `baseline.rule` sentence is a sentence of the `rule`; every `overwrite.replaced_by` is in the `rule`; every `prerequisite.policy_source` is in the blocked policy's `rule`. Manual sweep per policy:

- refill: supply span, kit room, above-allowance route, phase-in, supply start, unused-supply rate, covered units, result and their rounding (`int` = "rounded down", carry) all implemented. Gaps (observations, no task consequence shown here): `daily_rate` tier 1 tests only the newest order (`newest_order_date > prev_ship and order_qty > prev_order_qty`) where the rule says "a written order ... dated after the previous refill's ship date raises the quantity" (any such order); `prev_order_qty ... or 0` makes a program with no earlier straight-tip refill count as a quantity raise for phase-in, a case the rule does not state; `auth_days = 0` when no straight-tip grant exists (span 0, units 0), unstated.
- abn_quantity_notice: term, term start, expected denial, margin, cushion (`int` = "rounded down") implemented. Absent-record gap (observation): with no A4351 order `order_qty`/`order_through` are None and the compute fails.
- hardship_waiver: look-back (remittance = `continence_claim_adjudication`, per the event definition "one row per remittance posting"), open-amount basis, share, age addition, cap at the whole, `RND(...,2)` on the final figure only — implemented. Gap (observation): `waived_amt` subtracts `named_amt` when the named posting is inside the window, which is right only when the named posting is itself a remittance posting.
- noncovered_catheter_charge: **gap — finding C4**: the rule's scope "and that carries no supporting record" is quoted in `compute_basis.denial_code` but no binding reads a medical record; `result` tests only `denial_code == 'CO-151'`.
- returned_unit_credit: implemented (final rounding only). Unstated default (observation): `rs_days ... or 30`.
- payment_plan_installment: balance, band, extensions, tenure, down payment (`RND` nearest cent), installment (`cents` then ceiling division = "rounded up to the next cent"), floor at the tier minimum — implemented. Internal contradiction in the rule text itself: finding C6.

Rounding sentences vs RND placement: consistent in all six policies.

### action_binding_and_uuids

- Each `(target_tool, computes)` pair is claimed by exactly one policy (six distinct tools).
- uuid8s: 863073b5, 4a664827, d1a5476f, f3b8d099, 0f5c8cfb, 03d701bf — no shared prefix/suffix, no sequence, none appears in `share_tools.py`. (Sibling difficulties' tool modules are outside this audit's read domain, so cross-difficulty reuse was not checked.)
- Tool bodies (`task_tools.py`): every tool creates its row unconditionally and adjusts the program counter; none reads another row to refuse, error or hint, so no tool judges a prerequisite, eligibility or amount (module docstring says so and the bodies agree).
- Docstrings: no other tool named, no sequence position, no "before/after/first"; each ends "the customer can then be told ..." / "the notice then stands" — "then" refers to the same call's effect, not to another write (observation O5). No concrete example values in any docstring or Args description (enums list their allowed codes only; "multiple of 30" is a format rule).

### prerequisite_graph

- `prerequisite` filled on all six (`[]` on four). Edges: refill→abn_quantity_notice, refill→hardship_waiver, payment_plan→noncovered_charge, payment_plan→returned_unit_credit. Every `problem` is an extended policy id of this file, none base, none self; graph acyclic (depth 1).
- `policy_source` of each edge is verbatim in the blocked policy's `rule`; all four `form: state`, no `fallback_reason` (correct for state form).
- `kind`/`gate`: value_input gates `extra_units` (refill) and `bal` (payment plan) are real bindings; state_gate `continence_billing.adjustment_reason` names the field the refill sentence's state is read from.
- `resolved_by` = the depended-on policy's `target_tool` on all four edges.
- `condition` vs sentence: refill→abn condition is strengthened (finding C2); payment_plan→noncovered condition is broadened (finding C5); refill→hardship and payment_plan→return conditions match their sentences.
- `effect` assertions: refill→hardship effect "the past-due amount falls by the waiver" overstates — `continence_msr_past_due_amount` is floored at 0.00, so it falls by at most the past-due amount (observation O6). No authoring-viewpoint wording ("in this task", "at the opening") in any `prerequisite` text.

### prerequisite_sentences

Four-point test per edge:

1. refill→abn: "The above-allowance units ship only after a liability notice the customer signed for the straight-tip catheter, dated on or before the ship date, stands on the program." Connective "only after"; state = a signed straight-tip liability notice on the program (record words of `continence_liability_notice_signed`); no tool/policy id/snake_case. Exactly one write of the difficulty creates such a row (`sign_liability_notice_4a664827`), so the hop resolves to the abn policy uniquely. But the sentence's scope ("The above-allowance units ship only after ...") is wider than the rule's own above-allowance ladder — finding C1.
2. refill→hardship: "The refill's units are fixed only after every posting named on an approved hardship application of the program carries its hardship waiver adjustment, because the past-due test reads the balance as it stands." Connective "only after"; state form; one write creates a hardship_waiver adjustment. Derivation: approved `continence_requests` hardship row → its `continence_ledger_id` → hardship policy posts against that posting. Single reading. Observations: the hardship policy reads only the newest approved application (`LATEST` on `received_at`) while the sentence says "every posting named on an approved hardship application" (O11); the "because" clause gives a reason the refill's units do not depend on (units read no balance) (O6).
3. payment_plan→noncovered: "The installment is fixed only after every straight-tip refill whose claim line the plan denied with code CO-151 under a signed plan member waiver carries its non-covered item charge." Connective "only after"; state form; one write creates a non_covered_item charge. Condition broader than sentence — finding C5. The charge policy itself settles only "the program's latest straight-tip refill" (O11).
4. payment_plan→return: "The plan is not set up until every return receipt accepted on the program for a refill carrying a non-covered item charge has its return credit standing against that charge." Connective "not ... until"; state form; one write creates a return_credit adjustment. The return policy reads only the latest return receipt's shipment (O11).

- No rule carries a second wording of a dependency, a tool name or another problem's id; the depended-on rules (abn, hardship, charge, credit) do not restate the blocked side's sentence.
- Undeclared cross-problem order: the return-credit rule posts "against that non-covered item charge", and its allocation/price tiers read whether that charge stands; were the charge for the returned refill not yet posted, the credit would have to wait for the charge, and no edge or prerequisite sentence states that (O8; bears only on a world where the returned refill's charge is unposted).

### override_declarations

Sentence-by-sentence against each `base_policy_refs` entry (conclusions only; consequences are demonstrated in the task files):

- **refill** vs `continence_evt_refill_shipment`: supply-days sentence overridden, declared (#1); confirmation sentence "overridden" by #3 whose replaced_by restates the base rule (retires nothing, O1); active-status, grant valid on ship date, units ≤ authorized remaining, ship-lead window from previous ship date + supply days, coverage verification, shipping fees, payer billing, inpatient hold: followed (rule ends "Every eligibility ... stays in force"). vs `continence_evt_quantity_limits`: units sentence overridden, declared (#2); over-limit record / notice sentence followed by the tiers but contradicted by the prerequisite sentence (C1). vs consolidated supply, indwelling exclusion, liability notice, patient account: followed.
- **abn_quantity_notice** vs `continence_liability_notice`: signing sentence "overridden" by a replaced_by that restates it (retires nothing, O1); notice type, "claim still submitted to Medicare", "liable only for a line Medicare denies": followed. Base says the notice is signed "before the ship date" in its first sentence and "on or before the ship date" in its last; the extended policies use "on or before" (O7). vs quantity limits: followed.
- **hardship_waiver** vs `continence_evt_patient_account`: "only for postings named on a hardship application" overridden, declared (#1); "each against the one posting it adjusts and never for more than that posting's unpaid remainder" overridden, declared (#2); small-balance sentence named (#3) though it never bounded a hardship waiver (retires nothing, O1); counseling confirmation, tier allowance, "never on the customer's statement alone": followed. **Undeclared: "a payment is applied to the oldest unpaid posting first"** — the open-amount tier "those payments are first set against the waived postings" handles the same quantity (the waived postings' unpaid amount) differently and is not named in `overwrite` — finding C3. vs holds and closure: followed.
- **noncovered_catheter_charge** vs `continence_liability_notice`: cash-price sentence overridden, declared; "requires a liability notice signed on or before the ship date covering that item and at least those units; without it ... write-off": followed (waiver-cover tiers). vs denials and appeals: CO-151 appealed only with a supporting record, else non-covered — followed in the rule, not in compute (C4). vs quantity limits: followed.
- **returned_unit_credit** vs `continence_evt_patient_account`: return_credit definition overridden, declared (#1, real change: base return credit is self-pay only); #2 (hardship application) and #3 (small-balance ceiling) name base sentences that never governed a return credit (retire nothing, O1); "never for more than that posting's unpaid remainder" inherited (not overridden). vs returns: followed (unopened only, window, corrected claim for the payer part).
- **payment_plan_installment** vs `continence_evt_patient_account`: term/installment sentence overridden, declared; minimum balance, customer acceptance, whole balance: followed. vs holds and closure: followed.
- Disguised forms: no anonymous intermediate override other than C3; no 0/1 multiplier over a base-fixed amount; no base branch dropped by an extended selector.

### factor_ladders

Counts (as declared): refill 6 (2 method: sync_span_rule, supply_start_anchor; 4 parameter; cross_difficulty ostomy: sync_span_rule); abn 5 (2 method: notice_term_rule, term_count_anchor; 3 parameter; none cross); hardship 4 (1 method: open_amount_basis; 3 parameter; cross ostomy: hardship_share_rule); noncovered 4 (1 method: excess_count_basis; 3 parameter; cross cgm: assistance_freshness_rule, burden_share_rule); return 5 (1 method: return_allocation_rule; 4 parameter; cross cgm: hardship_restock_relief); plan 4 (1 method: down_payment_rule; 3 parameter; cross cgm: hardship_term_extension, down_payment_rule). Binding lists are pairwise disjoint within each policy; every `decides` is an input, none is `result`. Every ladder has three tiers, all stated in the rule with condition and value/method, all implemented as branches of the `decides` binding, fall-through = the baseline in every factor. Multi-source tiers exist in every policy (e.g. above_allowance_route, waiver_cover_rule, down_payment_rule).

Pairwise tier distinctness (distinguishing input per pair): all ladders distinct on their domain, e.g. term_count_anchor T1 vs T2 differ when the remaining days straddle a 30-day boundary (valid-through 334 days out: offset 6 → 10 blocks, offset 1 → 11 blocks); credit_price_rule T2 ("below the cash price") vs T3 (cash price) never coincide. Coincidences on part of the domain (observations, O3): increase_phase_in_rule T1 ("one block") = T2 ("blocks less one, never below one") whenever the refill has 2 blocks, all three equal at 1 block; above_allowance_route T1 = T2 whenever the notice units are not fewer than the excess.

Defects (findings below): F1 factor independence (class), F2 mislabelled method, F3 and F4 unreal ladders. Realism notes (observations, O9): hardship_share_rule T2 and burden_share_rule T1/T2 give more relief the more the customer owes on (or merely holds) the other program — a combined-burden/multi-program concession, plausible for a DME supplier's financial-assistance policy; carry_rate_rule T2 values unused straight-tip stock at the combined straight-tip + kit usage rate; shortfall_margin_rule T1 treats one customer-requested expedite in 12 months as evidence of running short. All other tier conditions and values are ones a Medicare/commercial DME supplier weighs (kit units counted against the intermittent catheter limit, over-limit records, ABN one-year span, delivery-date counting, restocking by return lateness, tenure, prior broken plan, hardship status).

### findings

**C1 — SOURCE-POLICY RED (refill: prerequisite sentence vs its own above-allowance ladder).** Symptom: two sentences of one rule settle the same units differently. Evidence: rule "The above-allowance units ship only after a liability notice the customer signed for the straight-tip catheter, dated on or before the ship date, stands on the program." vs rule "When a medical record with purpose over-limit justification has a visit date no more than the tier's over-limit record months before the ship date ... and the newest written order's quantity per 30 days is above the straight-tip room, the above-allowance units are that excess times the increase blocks." (and base quantity limits: "A quantity above the allowance is covered only when a medical record with purpose over_limit_justification is dated ...; without it the extra quantity ships only under continence_liability_notice"). Consequence: on a world with a qualifying over-limit record and no notice, tier 1 ships the excess now, the prerequisite sentence withholds it until a notice is signed (and makes the abn problem a prerequisite that the record route does not need). Affects: refill `rule`/`prerequisite[0].policy_source`. Bears on the task claiming the refill (world consequence judged there).

**C2 — SOURCE-POLICY RED (check 7: refill→abn condition strengthened).** Evidence: sentence requires only that a signed straight-tip notice dated on or before the ship date "stands on the program"; `condition` adds "and notice_units at least the above-allowance units the refill would carry"; the rule's own tier 2 handles a smaller notice ("or the units on the newest such notice when those are fewer", `MN(notice_units_on_file, ...)`). Consequence: with a smaller notice already on file, the sentence and tier 2 say the prerequisite holds (refill carries the notice's units), the declared condition says it is unmet. Affects: `continence_ext_straight_catheter_refill.prerequisite[0].condition`. Bears on the refill task (world consequence judged there).

**C3 — SOURCE-POLICY RED (undeclared override in hardship_waiver).** Evidence: base `continence_evt_patient_account` "a payment is applied to the oldest unpaid posting first" (inherited: "every other eligibility of the base patient-account rule stays in force"); extended open-amount tier "When the customer has payments posted on the program within the last 3 calendar months, those payments are first set against the waived postings, and the open amount is the waived postings' amount less those payments." The `overwrite` list names three other base sentences, not this one. Consequence: two readings of the waived postings' open amount (payments allocated oldest-first vs set against the waived postings) — demonstrated on the hardship task's world in its file. Affects: hardship_waiver `overwrite`/`rule`.

**C4 — SOURCE-POLICY RED (check 2, noncovered charge: empty promise).** Evidence: rule "...for the straight-tip intermittent catheters (A4351) of a refill whose claim line the plan denied with code CO-151 (quantity not supported) and that carries no supporting record..." (quoted in `compute_basis.denial_code`); compute has no binding reading `continence_medical_record_receipt`, and `result: RND(...) if denial_code == 'CO-151' else 0`. Consequence: on a world where a supporting over-limit record dated on or before the ship date is on file (the base appeal route), the rule says the refill is outside this policy (appeal, no charge) and compute posts a charge. Affects: noncovered `compute`. World consequence judged in the task claiming the charge.

**C5 — SOURCE-POLICY RED (check 7, payment_plan→noncovered condition broadened).** Evidence: sentence "every straight-tip refill whose claim line the plan denied with code CO-151 under a signed plan member waiver"; the charge policy charges only under a waiver "dated on or before the refill's ship date" and only for "the program's latest straight-tip refill"; `condition` reads "for which a plan member waiver is on file" (any date). Consequence: every earlier CO-151 refill shipped before any waiver satisfies the condition's antecedent while no policy can post (or would post a non-zero) charge on it, so the declared condition is never met by any write sequence. Demonstrated on the payment-plan task's world in its file. Affects: payment_plan `prerequisite[0].condition`.

**C6 — SOURCE-POLICY RED (payment plan: installment count contradicts the down-payment tier 2).** Evidence: "The term is the tier's longest plan term in months, and it is also the number of installments recorded on the plan." / "The plan is recorded as an approved payment plan request with the term as its number of installments" vs Down payment tier 2 "a tenth of the covered balance ... is set as the first installment and the rest is spread over the whole term" (`divisor: term`), i.e. term + 1 installments. Tier 1 is consistent (first installment + term − 1). Consequence: on a tier-2 world, `plan_months` is term by one sentence and term + 1 by the other. Affects: payment_plan `rule`. Bears on the payment-plan task only if its world reaches tier 2.

**F1 — SOURCE-FACTOR RED class (factor independence: a factor's tier reads another factor's binding or output; shared selections and assembled quantities inside factor bindings).** Complete member list:
- refill.above_allowance_route: `extra_units` reads `room_per30` (kit_room_rule's decides) and `phase_blocks` (increase_phase_in_rule's decides); its tier condition "the newest order above the straight-tip room" and value "the excess ... times the increase blocks" are another two factors' outputs.
- refill.increase_phase_in_rule: `phase_blocks` reads `blocks`, derived from `span_days` (sync_span_rule's decides).
- refill.carry_rate_rule: `daily_rate` reads `prev_order_qty`, a binding of increase_phase_in_rule.
- abn.notice_term_rule: `order_left_blocks` (its binding) reads `start_offset` (term_count_anchor's decides).
- abn.shortfall_margin_rule: `margin_per30` reads `order_age_days` (binding of notice_term_rule) and `order_qty` (binding of delivery_cushion_rule).
- abn.expected_denial_basis: `denied_per30` reads `order_qty` (binding of delivery_cushion_rule).
- abn.delivery_cushion_rule: holds the shared record selection `order_qty` in its bindings (read by two other factors).
- hardship.open_amount_basis: `open_amt` reads `waived_amt` (hardship_lookback_rule's decides).
- hardship.hardship_lookback_rule: `named_in6`/`named_in3` read `named_date`, a binding of posting_age_rule (which thus holds a shared selection).
- noncovered.waiver_cover_rule: `charged_units` (tier condition "covers fewer units than the units concerned" and value "every unit concerned") reads `excess_units` (excess_count_basis's decides).
- plan.plan_term_rule: holds the computation's base quantity `bal` in its bindings.
- plan.hardship_term_extension: `ext_h` reads `bal` (plan_term_rule binding).
- plan.down_payment_rule: `down` reads `bal` (plan_term_rule binding); `divisor` reads `term` = `band_months + ext_h + ext_c`, three factors' outputs assembled inside a factor binding.
- returned_unit_credit: no member (its factors read only non-factor bindings).
Consequence: each listed factor's ladder cannot be stated or applied without another factor's document, and substituting one factor's baseline moves another factor's tier or value — demonstrated per task on its own world. Affects: the `compute`/`factors` of the five policies named.

**F2 — SOURCE-FACTOR RED (mislabelled effect: noncovered.excess_count_basis).** Evidence: its ladder ("the newest kit order's quantity ... / one twelfth of the 12-month kit units ... / the refill's units alone") substitutes a kit quantity into one formula `ship_units + K × ship_days/30 − limit_units`; the identical three-tier kit ladder is labelled `parameter` in refill.kit_room_rule and abn.expected_denial_basis. Consequence: honestly labelled, the noncovered computation has no `method` factor (its other three are parameters), below the minimum of 1. Affects: noncovered `factors`. Bears on the charge task.

**F3 — SOURCE-FACTOR RED (unreal ladder: returned_unit_credit.return_allocation_rule).** Evidence: the policy's scope is a return "from a refill whose units above the plan's limit were charged to the customer as a non-covered item; the credit is posted against that non-covered item charge", so tier 1's conjunct "a non-covered item charge stands against the returned refill" holds of every customer who reaches this write and the fall-through ("Otherwise", no such charge) lies outside the policy; tier 2 ("such a charge stands but no plan member waiver ... is on file") contradicts base `continence_liability_notice` "A non_covered_item charge requires a liability notice signed on or before the ship date ...; without it the amount is Larkfield's write-off and is never billed to the customer" (on the HMO tier the notice is the plan member waiver). Consequence: on any charter-consistent world only tier 1 is reachable; the ladder has one live tier. Affects: return `rule`/`factors`. Bears on the return-credit task.

**F4 — SOURCE-FACTOR RED (unreal ladder: payment_plan.hardship_term_extension).** Evidence: tiers 1 and 2 carry the conjunct "and the covered balance is at least the tier's smallest plan balance"; the same rule says "a plan is offered only for a balance of at least the tier's smallest plan balance" (base: "for a balance of at least payment_plan_min_balance_usd"). Consequence: the conjunct holds of every customer who reaches `accept_payment_plan`; it restates scope and divides no customers (the factor is single-source, not multi-source as its evidence list claims). Affects: plan `rule`/`factors`. Bears on the payment-plan task.

Observations (no consequence demonstrated at charter level):
- O1 overwrites that retire nothing: refill overwrite #3 (confirmation — replaced_by restates the base sentence), abn overwrite #1 (signing — restated), hardship overwrite #3 (small-balance ceiling never bounded a hardship waiver), return overwrites #2 (hardship application never required for a return credit) and #3 (small-balance ceiling never bounded a return credit).
- O2 hardship.open_amount_basis is labelled `method` while its tiers subtract a different amount (payments / existing adjustment / nothing) in one formula `waived_amt − X`; this is the same-slot shape that F2 shows the charter labels `parameter` elsewhere. If judged a parameter, hardship_waiver has no method factor. Recorded as an observation because, unlike F2, the charter carries no identical ladder under the other label.
- O3 partial tier coincidences (see factor_ladders).
- O4 absent-record / first-match reads without a stated tier: refill `auth_days` with no grant; refill phase-in with no earlier refill; refill kit room when kits shipped but no kit order (`or 0`); abn with no A4351 order; hardship/charge/return reading only the newest application / refill / return receipt (O11); `CFIELD(..., status='active')` takes the first active cross program.
- O5 docstring "then" (same-call effect only).
- O6 refill hardship sentence's "because the past-due test reads the balance as it stands" — the refill's units read no balance; edge `effect` says the past-due amount "falls by the waiver" though the measure is floored at 0.00.
- O7 base liability notice "before the ship date" / "on or before the ship date".
- O8 implicit order return credit ← charge for a returned refill whose charge is unposted (no edge).
- O9 realism notes (see factor_ladders).
- O10 the plan record carries only `plan_months` and `monthly_amount_usd`; with a down payment the recorded installments times the monthly amount do not equal the covered balance (the first installment is recorded nowhere).
- O11 "every ..." in three prerequisite sentences vs `LATEST` single-record reads in the depended-on policies (hardship: newest approved application; charge: latest refill; credit: latest return receipt).

## closing_checklist

Written after both reveals (2026-10-15T00:22Z); the charter-global section above was frozen before any reveal and is unchanged.

- Files: `0.md`, `1.md` correspond one-to-one with tasks 0 and 1; `_difficulty.md` alongside; first revision (no older revisions).
- Scope (confirmed against the revealed `charter_scope`): task 0 = {straight_catheter_refill, abn_quantity_notice, hardship_waiver}, task 1 = {payment_plan_installment, noncovered_catheter_charge, returned_unit_credit}; pairwise disjoint, all six extended policies covered, three task tools each.
- Problem trees: each task has 2 prerequisite problems, ≥ 1 value_input edge (task 0: 1, task 1: 2), one owner=user write, no cycle; the difficulty's graph is acyclic. Both trees PASS.
- GT vs independent derivation: every scored value, owner and order equal in both tasks.
- Not closed. Outstanding REDs: C1, C2, C3, C4, C5, C6 (SOURCE-POLICY) and F1, F2, F3, F4 (SOURCE-FACTOR); per task: task 0 SOURCE-POLICY (C3) + SOURCE-FACTOR (F1); task 1 SOURCE-POLICY (C5) + SOURCE-FACTOR (F1, F2, F3, F4). Re-running the instantiation gates on a final form is deferred until those are resolved.

## revision_2

### charter_global_frozen (revision 2)

- Freeze time: 2026-10-15T05:10Z, before either round-2 task file was opened. Round-1 text above is untouched.
- Hashes: `continence.extended.yaml` 20abd5c2836e64655b0c686233a4e9bf5f3fe4abfcdd4c4f72262b0d1c2c060c (changed, so every charter-global section is re-derived in full below); `task_tools.py` 4c9f02d3… (unchanged, so `### action_binding_and_uuids` carries forward by reference: same six tools and uuid8s, bodies still judge nothing); base section of the extended file still byte-identical to `blueprint/products/continence.yaml` (576db87a…).
- Gate snapshot from the brief: EXTENDED / TASK TOOL CONTRACT / REPLAY --check / SOLVABILITY / COMPUTE / GROUNDING / SCOPE OK; TRACEABILITY NOT OK only on unlock tool names. Views: 0.view.json 252b812c… (unchanged), 1.view.json a4075f8e… (new); both re-hashed and matching.
- contamination_disclosure: the round-1 GT of both tasks (values and gold sequences) was read at 2026-10-15T00:20Z. Nothing derived from round-2 GT is in this section; round-2 task files had not been opened when it was written.
- Mechanical re-checks (`/tmp/audit_continence_0063/scripts/r2.py`, `trans.py`): every `compute_basis` quote, every `baseline.rule` sentence, every `replaced_by` and every `policy_source` is verbatim in its rule; transitive scan of every factor binding through plain bindings finds no factor reading another factor's binding (the only hits are the token `receipt_date` inside a string literal of `ret_ship`, a false positive).

### policy_conflict_scan (revision 2)

Same six policies, owners, tools and two trees. Changes: refill/abn/hardship/plan/credit rules gain "Records read" paragraphs; the charge policy now has a denial-route ladder (CO-151 without a supporting record / CO-197 with the drawn grant invalid or PR-204 / otherwise none) and drops the CGM burden share; the credit policy replaces its allocation ladder with a corrected-claim rule plus a restocking-form ladder; the plan replaces the down payment with a first-installment form. The two balance-adjustment policies no longer carve each other out (neither overrides a sentence that governs the other). Conflicts: N3 below.

### rule_compute_equivalence (revision 2)

- refill: record selections, absent-grant ("no supply days"), absent-earlier-refill ("no earlier order and no unused supply"), route cap, phase cap capped at the refill's blocks, assembly (`covered_units`, `excess_units`, `extra_units`, `result`) all stated and implemented; `daily_rate` tier 1 now tests the newest order exactly as the rule says (round-1 gap closed).
- abn: absent order → no units (`result ... if order_qty > 0 else 0`); horizon floor at zero; cushion rounding down. `cushion_days` re-reads the newest order inline instead of `order_qty` — same value, cosmetic.
- hardship: look-back time window vs statement batch, named posting counted once only when it is itself a remittance (`named_type`), deduction, share, cap, final rounding — implemented.
- charge: denial route, kit counting, waiver cap, assistance, final rounding — implemented, except **N2**: `rec_ok` reads only the newest over-limit record (`LATEST(... visit_date ...)` then `rec_visit <= ship_date`), while the rule says "no over-limit justification record dated on or before the refill's ship date is on file". Also (observation) `grant_ok` checks only `valid_through >= ship_date`, not `valid_from`.
- credit: corrected-claim / no-corrected-claim credited units, price, restocking form, schedule, reliefs, final rounding — implemented.
- plan: band, extensions, first-installment form (`first_inst`, `shift`), recorded installments `term - shift`, ceiling to the cent, floor — implemented. `band_count` repeats `bal`'s expression verbatim (cosmetic).
- Rounding sentences vs RND placement: consistent in all six.

### prerequisite_graph and prerequisite_sentences (revision 2)

- Edges unchanged in shape (refill→abn value_input, refill→hardship state_gate, plan→charge value_input, plan→credit value_input), all state form, acyclic, `resolved_by` = target tools.
- refill→abn: "When no over-limit justification record qualifies, the above-allowance units ship only after a liability notice the customer signed for the straight-tip catheter, dated on or before the ship date, stands on the program." Now agrees with the route-cap record tier (C1 closed); `condition` no longer adds a units floor (C2 closed).
- refill→hardship: "the posting named on the program's newest approved hardship application" — matches the hardship policy's single-record read (O11 closed); spurious "because" clause gone, `effect` states the zero floor (O6 closed).
- plan→charge: "the program's latest straight-tip refill ... whenever its claim line stands denied as a quantity above the plan's limit with no supporting record, as unauthorized with no valid grant, or as not covered, and a plan member waiver dated on or before its ship date is on file" — condition now the same single refill and the same waiver date test (C5 closed). Wording "with no valid grant" vs condition/charge rule "the grant it drew on was not valid" — see O13.
- plan→credit: "the refill named on the program's latest return receipt, when it carries a non-covered item charge" — matches the credit policy's read (O11 closed).
- Observation O12 (new): both plan gates presuppose a positive amount; where the owed charge or credit computes to 0.00 the tools (positive figures only) cannot make the state hold, so the gate is unsatisfiable. N3 shows a charter-consistent case for the credit.

### override_declarations (revision 2)

- refill #3 now really retires the base on-hand count ("the supply they hold is counted from the records ... rather than from their own count"); abn #1 now admits the customer's authorized representative (real change; CMS allows a representative to sign an ABN); hardship #3 now names "a payment is applied to the oldest unpaid posting first" (C3 closed); the no-op overwrites (hardship small-balance, credit hardship-application and small-balance) are removed (O1 closed).
- Charge vs `continence_evt_denials_and_appeals`: CO-151 route matches base ("appealed only when a medical record supporting the quantity, dated on or before the date of service, is on file") — C4 closed in the rule; PR-204 route matches base. CO-197 route ("the authorization grant the refill drew on was not valid on its ship date") differs from base ("appealed only when an authorization grant valid on the date of service is on file") only when the drawn grant is invalid but another grant is valid, a world base refill rules out ("the ship date must be on or before the valid-through date on the authorization being drawn") — observation O13: the CO-197 disjunct is dead on charter-consistent worlds.
- Credit vs `continence_evt_returns` / `continence_evt_claims`: **N3**.
- No undeclared override elsewhere; no 0/1 multiplier over a base-fixed amount (the charge route's fall-through is base's own "Larkfield absorbs").

### factor_ladders (revision 2)

| policy | factors (label) | method | cross |
| --- | --- | --- | --- |
| refill | sync_span_rule (m), kit_room_rule (p), above_allowance_route (p, now decides `route_cap`), increase_phase_in_rule (p, 1 / 2 / standard blocks), supply_start_anchor (m), carry_rate_rule (p) | 2 | ostomy |
| abn | notice_term_rule (p, 12 / 6 / standard), order_horizon_rule (m), expected_denial_basis (p), shortfall_margin_rule (p), delivery_cushion_rule (p) | 1 | — |
| hardship | hardship_lookback_rule (m: time window / statement batch / none), open_amount_basis (p: deduction), hardship_share_rule (p), posting_age_rule (p) | 1 | ostomy |
| charge | denial_route_rule (m), kit_count_rule (p), waiver_cover_rule (p), assistance_freshness_rule (p) | 1 | cgm |
| credit | credit_price_rule (p), restocking_form_rule (m: whole credit / one box / none), restocking_schedule_rule (p), hardship_restock_relief (p), tenure_restock_relief (p) | 1 | cgm |
| plan | plan_term_rule (p), hardship_term_extension (p), tenure_term_extension (p), first_installment_form (m) | 1 | cgm |

- F1 closed: shared selections and assembly moved to plain bindings; no factor binding reads another factor's binding, directly or transitively.
- F2 closed: the kit ladder is `parameter` in all three policies; the charge's method is denial_route_rule, whose tiers change the algorithm (excess over the limit / all units / none).
- F3 closed: the allocation ladder is gone; the credit's method restocking_form_rule changes the fee basis (whole credit / one 30-unit box / nothing), three reachable tiers.
- F4 closed: hardship_term_extension no longer carries the scope conjunct.
- O2 closed (open_amount_basis relabelled parameter; the look-back is now a genuine window-type method).
- Tier distinctness: all ladders distinct on their domain. Partial coincidences (observation O3, updated): phase-in T2 (2) equals T3 whenever the refill has 2 blocks (both capped to 2); order_horizon T1 and T2 can give the same whole blocks (they differ by the delivery lag only); restocking_form T1 and T2 coincide when exactly 30 units are credited.
- Realism: the charge baseline ("No unit of the refill is concerned, so Larkfield absorbs the denied line") gives 0.00 — it is base's own treatment of a denial with no customer liability, so the fall-through is real; the reader of the computation document alone gets a definite wrong answer (no charge). Observation only.

### findings (revision 2)

Round-1 status: C1, C2, C3, C4 (rule side), C5, C6, F1, F2, F3, F4 closed as described above; O1, O2, O6, O10, O11 closed; O4 mostly closed (CFIELD first-active read remains); O3 partial coincidences moved, not removed (observation); O8 remains (the credit is "not owed" while the returned refill's charge is unposted, and no edge orders credit after charge when both are owed on the same refill); O5, O7 unchanged as claimed; O9 burden-share note closed by removal.

**N2 — SOURCE-POLICY RED (check 2, charge: first-match read of the supporting record).** Rule: "When the denial is CO-151 (quantity not supported) and no over-limit justification record dated on or before the refill's ship date is on file, the units concerned are ..."; compute: `rec_visit = LATEST(... record_purpose='over_limit_justification')`, `rec_ok = rec_visit != None and ship_date != None and rec_visit <= ship_date`. Probe (`probe_n2.py`, task-1 world + records dated 2026-02-01 and 2026-09-30, ship date 2026-09-09): compute `rec_ok` False, route 1, charge 37.00; rule: a record dated on or before the ship date is on file, so the CO-151 route does not apply (base: the denial is appealed) and no charge is owed. Affects: charge `compute.rec_ok`. Bears on task 1's policy; no consequence on its world (no over-limit record seeded). New in revision 2 (residue of C4).

**N3 — SOURCE-POLICY RED (credit: the corrected-claim rule nets out every returned unit).** Rule: "When a corrected claim for the returned refill is on file, the units it withdrew from the payer are the original claim's billed amount less the corrected claim's billed amount, divided by the cash price, and the credited units are the accepted units less those withdrawn units, never below zero". Base `continence_evt_returns`: "a payer-billed shipment is then re-billed by a void claim (all units returned) or a corrected claim (some units returned)"; base `continence_evt_claims`: "A corrected claim replaces an original claim when the units, item or dates billed were wrong or some of the units were returned". On a refill billed to the payer in full (the charter's own billing: the original claim bills every unit shipped, the excess then denied CO-151), the corrected claim re-bills the units kept, so the withdrawn units equal the accepted units and the credited units are 0 on every world consistent with base. That contradicts the policy's own purpose ("the credit covers the accepted returned units this policy allocates to the customer's own purchase", posted "as soon as the receipt stands"). It also leaves the plan's credit gate unsatisfiable (O12). Probe on task 1's world with the charter-consistent corrected claim (266.40 = 144 units × 1.85): credit 0.00. The per-task consequence is demonstrated in 1.md. Affects: credit `rule` "Records read" / `compute.credited_units`. New in revision 2.

Observations (new): O12 (positive-amount presupposition of both plan gates); O13 (CO-197 disjunct dead on charter-consistent worlds; plan sentence "no valid grant" vs condition "the grant it drew on"; `grant_ok` ignores `valid_from`); O14 `sign_liability_notice_4a664827` docstring ("The customer personally signs") vs abn rule now allowing the customer's authorized representative (tool hash unchanged).

## closing_checklist (revision 2)

Written after both round-2 reveals (2026-10-15T05:12Z).

- Files: 0.md, 1.md, _difficulty.md each carry `## revision_2` appended below the untouched round-1 text.
- Scope (revealed `charter_scope`): unchanged and disjoint; all six extended policies covered.
- Trees: both still 2 prerequisites, value_input ≥ 1, one owner=user write, acyclic — PASS.
- GT equals the derivation in both tasks.
- Round-1 REDs: C1, C2, C3, C4 (rule side), C5, C6, F1, F2, F3, F4 closed.
- Not closed. Outstanding: **N2** (SOURCE-POLICY, charge first-match read of the supporting record; charter-level, no task consequence) and **N3** (SOURCE-POLICY, credit corrected-claim rule credits nothing on charter-consistent worlds; demonstrated in task 1 together with its seeded corrected claim, SOURCE-TASK). Per task: task 0 PASS; task 1 SOURCE-POLICY + SOURCE-TASK (N3).
- Gate re-run on a final form deferred until N2/N3 are resolved.

## revision_3

### charter_global_frozen (revision 3)

- Freeze time: 2026-10-15T09:09Z, before either round-3 task file was opened; earlier revisions untouched.
- Hashes: `continence.extended.yaml` 36723c68697b142f4155f098551e1c527189686f9d07581a133fe833e92ddc35 (changed → charter sections re-derived); `task_tools.py` 8cf6605b6475987c287664c734abb0d0b45d45eebf0df5c418d74dee92f14ded (changed: AST comparison shows only the `sign_liability_notice_4a664827` docstring changed; signatures, owners, bodies and uuid8s are the same, so action binding / no-tool-judges-prerequisites carry forward); base section still byte-identical to `blueprint/products/continence.yaml`. Snapshot copies of both artifacts: `/tmp/audit_continence_0063/r3/`.
- Gate snapshot from the brief: all OK except TRACEABILITY (unlock tool names only). Views: 0.view.json 252b812c… (unchanged), 1.view.json d6c9809c… (new), re-hashed and matching.
- contamination_disclosure: round-1 and round-2 GT of both tasks were read in earlier rounds; nothing from round-3 GT is used here.
- Mechanical re-checks (`r2.py`, `trans.py`): verbatim quotes, baseline sentences, replaced_by and policy_source all in their rules; no factor binding reads another factor's binding directly or transitively (the only hit is the known `receipt_date` string-literal false positive).

### changes reviewed (revision 3)

- refill, abn: rule/compute/factors unchanged from revision 2 (same line spans; spot-checked text and compute; task-0 recomputation identical).
- hardship: the "Burden share" paragraph renamed "Hardship share" and reworded to "the customer's latest ostomy hardship application" (matches `XLATEST` over the customer's ostomy requests); compute unchanged.
- charge: (a) denial route now CO-151 with **no over-limit justification record on file for the program** (`rec_count == 0`), or PR-204; otherwise no unit (record on or before the ship date → appeal; records only after the ship date → Larkfield absorbs; CO-197 → appeal, "because a refill ships only on an authorization grant valid on its ship date"). New declared overwrite of base `continence_evt_denials_and_appeals` "otherwise the denial is not appealed and is handled as a non-covered amount under continence_liability_notice" — the merged semantics are unique (record before DOS: appeal, as base; records only after DOS: absorbed; no record: non-covered). (b) New declared overwrite of base `continence_liability_notice` "A non_covered_item charge requires a liability notice signed on or before the ship date covering that item and at least those units": the current (latest) plan member waiver replaces earlier ones, the charge is owed only if it was signed on or before the ship date, and it caps the units. Rule, compute (`notice_*` LATEST by notice_date with `notice_type='plan_member_waiver'`) and ladder agree.
- credit: credited units are now "the accepted units or the customer's own units, whichever is fewer", with the stated ground "the corrected claim re-bills the payer only for the units the customer kept, so the plan's limit then falls on the kept units and the customer's own units fall one for one with the accepted returned units" — consistent with base claims/returns.
- plan: both prerequisite sentences and conditions add "whenever the ... owed comes to more than zero"; the charge sentence drops the CO-197 clause and reads "with no over-limit justification record on file ... the customer's current plan member waiver is dated on or before its ship date". Conditions match sentences word for word in substance.
- tools: signing docstring now "The customer, or the customer's authorized representative on their behalf, signs ...; no Larkfield representative signs it" — matches the abn rule.

### findings (revision 3)

- **N2 closed.** Probes (`probe_n2.py`, task-1 world): records 2026-02-01 + 2026-09-30 → `rec_count` 2, route 0, charge 0.00 (rule: a record dated on or before the ship date is on file → appeal); a record only after the ship date → route 0, charge 0.00 (rule: absorbed); waiver class — a newer 80-unit waiver dated 2026-09-20 (after the 2026-09-09 ship date) → cap 0, charge 0.00, which is what the declared "current waiver replaces every earlier waiver" sentence says. Compute and rule agree on all three decoys.
- **N3 closed (policy side).** The credited-units rule no longer nets the corrected claim; on a charter-consistent corrected claim the credit is the returned units out of the customer's own units.
- O12 closed (gates now conditioned on a positive amount); O13 closed (CO-197 dropped from the charge route and the plan sentence); O14 closed (docstring); O4 closed for the record/waiver reads (CFIELD first-active read of a cross program remains, observation).
- No new RED. Observations (new): O15 — the credit's price tier 2 divides the charge by the customer's own units; where the waiver capped the charged units below the own units, the per-unit price understates what was paid per charged unit, and credited units can exceed the units actually charged (no task world reaches it: the returned refill's charge covered all 60 own units). O16 — under the declared waiver overwrite a later waiver signed after a shipment voids the charge for that shipment even when an earlier waiver signed before it existed; declared and customer-favourable, recorded for realism only. Carried: O3 partial coincidences, O8 (credit/charge order on the same refill, no task world), O5, O7, half-cent ties in two task-0 sensitivity figures.

## closing_checklist (revision 3)

Written after both round-3 reveals (2026-10-15T09:11Z).

- Files: 0.md, 1.md and _difficulty.md each carry `## revision_3` below the untouched revision-1 and revision-2 text; per-task files correspond one-to-one with tasks 0 and 1.
- Coverage and scope: revealed `charter_scope` unchanged — task 0 {refill, abn notice, hardship waiver}, task 1 {payment plan, non-covered charge, return credit}; pairwise disjoint, all six extended policies covered; six task tools with independent, unchanged uuid8s; no tool judges a prerequisite.
- Trees: each task 2 prerequisite problems, >= 1 value_input edge (task 0: 1 + 1 state_gate; task 1: 2), one owner=user write, acyclic; difficulty graph acyclic.
- Factors: every computation 4-6 factors with >= 2 parameter and >= 1 method, honest labels, three distinct tiers stated in the rule, no factor reading another; per task >= 1 multi-source and >= 1 cross-difficulty factor on seeded rows; every factor bears weight; every full baseline gives a definite number different from gold (task 0: 594 / 120 / 172.60; task 1: 0.00 / 66.60 / 54.76).
- Unique solution: gold equals the frozen derivation in both tasks.
- All round-1 (C1-C6, F1-F4) and round-2 (N2, N3) REDs closed; no new RED. Open observations only: O3, O5, O7, O8, O15, O16, the CFIELD first-active cross read, half-cent ties in two task-0 sensitivity figures.
- Gates: the coordinator's round-3 re-run on this final form (EXTENDED / TASK TOOL CONTRACT / REPLAY --check / SOLVABILITY / COMPUTE / GROUNDING / SCOPE OK; TRACEABILITY pending only on the unlock tool names until the KB is rendered) is the gate record; the auditor did not re-run them.
- The difficulty passes the source-layer audit: policy self-consistency, problem tree, factors and unique solution all PASS for both tasks.

## revision_4

### charter_global_frozen (revision 4)

- Freeze time: 2026-10-15T12:12Z, before either task file's round-4 state was opened; earlier revisions untouched.
- Hashes: `continence.extended.yaml` 96455dead147ec45da03526e4ca65318815fc67312531d1cb4982ecb8b983f14 (changed); `task_tools.py` 8cf6605b… (byte-identical to the round-3 snapshot, so action binding and tool bodies carry forward); views 252b812c… / d6c9809c… unchanged (both worlds unchanged); base section still byte-identical to the blueprint charter. The charter was diffed line by line against the round-3 snapshot `/tmp/audit_continence_0063/r3/continence.extended.yaml` (201 diff lines); the round-4 copy is in `/tmp/audit_continence_0063/r4/`.
- Inputs read this round in addition: `audits/render_source/continence_supply_program_services/findings.md` (F-1 … F-5) and the source-side notes and E-1/E-2 entries of `audits/policy_kb/continence_supply_program_services/{0,1}.md`.
- contamination_disclosure: GT of rounds 1–3 for both tasks was read earlier; the KB-audit files quote some task values. Nothing new is derived from a round-4 task file here.
- **Audit-miss disclosure (revision 3):** revision 3 said the hardship compute was "unchanged". In fact round 3 had replaced `ostomy_balance: CFIELD('ostomy', 'patient_balance_due', status='active')` with `XSUM('ostomy', 'ostomy_programs', 'patient_balance_due', status='active')`. That was the mismatch F-5 later found, and revision 3 did not catch it, because no round-2 snapshot existed to diff against. From round 3 on, snapshots are kept and every revision diffs against the previous one.
- Mechanical re-checks (`r2.py`, `trans.py`): all quotes, baseline sentences, replaced_by and policy_source verbatim; no factor binding reads another factor's binding, directly or transitively (only the known `receipt_date` string-literal false positive).

### changes reviewed (revision 4)

| item | change | verdict |
| --- | --- | --- |
| F-1 (charge waiver-cover fall-through) | new plain binding `excess_units = MN(ship_units, MX(0, ship_units + kits_counted*ship_days/30 - limit_units))`; rule "The refill's excess over the limit is its units plus the kits counted ..., never below zero and never more than the refill's units"; denial route T1 "the units concerned are the refill's excess over the limit" | closed: units concerned ≤ refill units, so "Otherwise every unit concerned is charged" = cap `ship_units` in every case; capping the excess at the refill's own units is the realistic reading (kits cannot make more straight-tip units non-covered than shipped) |
| F-2 (withdrawn CGM plan anchor) | rule and ladder now "a payment plan request ... was received within the last 24 calendar months and now stands withdrawn" | closed: matches `XCOUNT(..., within_months=24, date_field='received_at', request_status='withdrawn')` |
| F-3 (factor wording composing another factor's output) | denial route method now "the refill's excess over the limit" (a plain quantity defined in Records read); restocking form now "withheld from the gross credit" / "from one box's worth only", both defined in a new Assembly paragraph and bound as plain `gross_credit` / `box_value` | closed: the ladders name plain assembly quantities, not another factor's tiers |
| F-5 (ostomy balance across programs) | `ostomy_balance` now `XMAX(...)` | closed: "an active Ostomy Supply Program that carries a balance due above zero" ⇔ the largest active balance > 0 |
| E-1 source side (plan overwrite) | replaced_by now "the plan runs for the term and in the monthly installments this policy states, in place of the tier's longest term, each installment at least the tier's smallest monthly installment" | closed: no longer points at the extensions; merged semantics unique |
| E-2 source side (hardship overwrite 2) | replaced_by now "the single adjustment is posted against the named posting and carries the whole waiver this policy computes, even where that is more than the named posting's unpaid remainder" | closed: no look-back/open-amount pointer; the deviation from base ("never for more than that posting's unpaid remainder") is now stated outright, which is more exact (in task 0 the named posting's oldest-first remainder is 0.00 and the waiver is 272.61) |
| baseline wording (six policies) | default-naming sentences removed from `baseline.rule`; each rule gains an Assembly paragraph stating the full combination once | closed: each baseline still yields a definite number with no factor (task 0: 594 / 120 / 172.60; task 1: 0.00 / 66.60 / 54.76), every baseline sentence is in the rule, every factor's fall-through equals what the baseline implies for its input (no above-allowance units, no margin/cushion, named posting alone at one half, no unit concerned, no restocking, longest term with no first installment), and each Standard method is the special case of its Assembly with every factor on its fall-through |

### findings (revision 4)

- No RED. Round-3 status unchanged for every other item; F-4 (refill docstring "billed to the program's payer by claim" while the body records only `billing_route='payer_claim'`) is not claimed and is recorded as observation O18: it describes the shipment's billing route, and no scored value or prerequisite rests on it.
- Observation O17 (regression of O10's closing text): the plan's Standard method lost the sentence "A first installment, when one is set, is billed on the next statement and is not one of the installments recorded on the plan." The count is still unique ("Assembly. The installments recorded on the plan are the term's months, less the one month the first-installment form takes off where it does so"), but the rule no longer says when the first installment is billed. The persona's "if the agent mentions a first installment coming on your next statement" now refers to a timing the charter does not state. No scored value or write depends on it; recorded only.
- Carried observations: O3, O5, O7, O8, O15, O16, half-cent ties in two task-0 sensitivity figures. The first-active CFIELD read is gone (no CFIELD remains in the charter).

## closing_checklist (revision 4)

Written after both round-4 reveals (2026-10-15T12:14Z).

- Files: each of 0.md, 1.md, _difficulty.md carries `## revision_4` below the untouched revisions 1-3.
- Scope, tools, uuid8s: unchanged (tools byte-identical to round 3); scopes disjoint and complete.
- Trees: unchanged and valid (2 prerequisites each, value_input >= 1, one owner=user write, acyclic).
- Factors: counts and labels unchanged (refill 6: 2 m / 4 p; abn 5: 1 / 4; hardship 4: 1 / 3; charge 4: 1 / 3; credit 5: 1 / 4; plan 4: 1 / 3); no factor reads another; every factor bears weight; baselines definite and different from gold in every computation.
- Unique solution: gold equals the derivation in both tasks; no scored value changed this round (values_changed=none confirmed).
- Render-source F-1, F-2, F-3, F-5 and KB E-1/E-2 source side closed; F-4 recorded as observation O18 (not claimed, no consequence).
- Gates: coordinator's round-4 snapshot all OK including TRACEABILITY; not re-run by the auditor.
- No RED outstanding. Open observations: O3, O5, O7, O8, O15, O16, O17, O18, half-cent ties in two task-0 sensitivity figures.
- The difficulty passes the source-layer audit at revision 4.

## revision_5

### charter_global_frozen (revision 5)

- Freeze time: 2026-10-15T16:18Z, before either task file's round-5 state was opened; earlier revisions untouched.
- Hashes: `continence.extended.yaml` 821f708feb8aa7587addc05f0de1afdbc9e2736fe2e6948f4af50bff67a8a9ad (changed; 2924 diff lines against the round-4 snapshot, so all six policies were re-read in full — snapshot `/tmp/audit_continence_0063/r5/`); `task_tools.py` 8cf6605b… (byte-identical); views unchanged; base section byte-identical to the blueprint charter.
- Inputs read: `audits/render_source/XF_recipe.md`; the revision_2 sections of `audits/policy_kb/continence_supply_program_services/{0,1}.md` (S-1, S-2, S-3).
- contamination_disclosure: earlier rounds' GT already read; nothing from a round-5 task file is used here.
- **Audit-miss disclosures.** (1) S-3: the round-4 diff dropped "Every unit concerned is charged" from the charge baseline. Revision 4 judged that baseline "definite" but did not notice that "the units charged" was then undefined in it. (2) S-2: the wording-level composition of factor sentences ("0.15 is added to the waiver share", "the restocking share is halved", "the units concerned or the waiver's units") was present from round 1. My factor-independence checks covered only compute bindings, so this went unreported. (3) S-1: the round-4 Assembly sentences named factor-only quantities, and revision 4 accepted them as "the special case of the standard method". Revision 5 checks rule wording against the XF recipe as well as compute.

### checks (revision 5)

- Mechanical (`r2.py`, `trans.py`): baseline sentences, replaced_by and policy_source verbatim in their rules; no factor binding reads another factor's binding, directly or transitively (known `receipt_date` string-literal false positive only). **One compute_basis quote fails the verbatim test (R5-1 below).** (The gate `check_extended.py` verifies baseline and overwrite sentences but not `compute_basis` quotes, so the gate stays green.)
- XF recipe, per policy (read in full):
  - refill: the standard method defines in record terms the supply days, 30-day blocks, covered limit, covered units, supply start, days left, daily rate, unused supply, the order's excess per 30 days and for the refill, and the refill's units. One generic combination sentence follows ("every replacement of a standard quantity is made first and the quantities resting on it are counted again, then every addition is made, each never more than its own limit"). Each factor sentence acts on one standard quantity: span replaces the supply days, kit room replaces the covered limit, the route adds the order's excess under its own cap, phase-in replaces the blocks the excess counts for, supply start replaces the start, rate replaces the daily rate. Compute agrees (`covered_per30`, `excess_units = (order_qty - covered_per30) * MN(phase_cap, blocks)`, `extra_units = MN(route_cap, excess_units)`).
  - abn: term blocks, order horizon, notice blocks, expected-denial quantity and notice units are defined in the standard method. Term and horizon replace; expected-denial basis replaces; margin "10 units per 30 days are added ... for each of the notice blocks"; cushion adds the expected-denial quantity × days / 30, rounded down. Compute agrees.
  - hardship: the waived amount (the named posting's amount) and the waiver share (one half) are standard. Look-back adds, deduction takes, hardship share replaces, posting age adds to the share, with the generic order "the waiver share is replaced before anything is added to it, and the share never exceeds the whole". S-2 closed in wording. Compute agrees.
  - charge: excess over the limit, units concerned (none), units charged (the units concerned, never more than the refill's units), price and charge are defined — **S-3 closed** (the baseline defines units charged). Denial route replaces units concerned; kit counting adds kits inside the excess; waiver cover replaces or limits units charged; assistance multiplies the price; generic order "replacement ... and addition first, every limit next, every change to the price last". Compute agrees.
  - credit: price, gross credit, credit and restocking basis (= gross credit) are standard. Credit price replaces the price; restocking form replaces the basis (one box's worth "that is 30 units times the price", defined inside the only factor that uses it, as recipe item 3 allows — the reworker's flagged judgement call is acceptable); both reliefs multiply the basis; the schedule withholds a fraction of the basis; generic order "replacement first, multiplication next, anything withheld last". The ladder is reordered so the fall-through is the standard basis (`restock_form` baseline 1). Compute agrees (`restock_basis = (...) * h_relief * p_relief`, `restock_charge = restock * restock_basis`).
  - plan: the term, installments recorded, amount spread and installment are standard. Term band replaces the term; both extensions add to it; the first-installment form takes from the amount spread and takes a month off the installments recorded, the first installment "billed on the next statement and not one of the installments recorded on the plan" (**O17 closed**). Compute agrees (`spread`, `installments = MX(1, term - shift)`).
  - Mechanical scan: no factor id appears in any baseline, `result` or plain-binding `compute_basis` quote.
- S-1 closed (no Assembly paragraph names a factor quantity; one generic combination sentence per policy). S-2 closed (every factor sentence acts on a standard quantity). S-3 closed.
- Baselines: definite and reachable, each different from gold (594 / 120 / 172.60 / 0.00 / 66.60 / 54.76). Every factor's fall-through is the standard quantity unchanged.

### findings (revision 5)

**R5-1 — SOURCE-POLICY RED (check 2: compute_basis quote not verbatim; hardship waiver).** `compute_basis.ostomy_active` quotes "When the customer also holds an Ostomy Supply Program in active status and the customer's latest ostomy hardship application is approved and was received within the last 12 calendar months, the waiver share is the whole of the open amount." The rule now reads "..., the waiver share is replaced by the whole." The quoted sentence is not in the rule, and it uses the retired term "open amount". Consequence: the binding `ostomy_active` carries a stated basis that cannot be found in the rule, which breaks the two-way rule ↔ compute correspondence and leaves stale wording for the KB/traceability layer. No scored value changes (the binding's expression `EXISTS('ostomy', status='active')` is right). Affects: `continence_ext_hardship_waiver.compute_basis.ostomy_active`. New in revision 5 (left over from the share rewording).

Observations (new): O19 — the hardship overwrite #3 / rule sentence still says "the open amount of the waived postings is counted by this policy's open-amount rule", while the standard method now calls it "the waived amount". It is readable through the "Open-amount deduction" heading, and no value depends on it. O20 — the refill→abn edge `effect` still speaks of "the route cap" and "the increase blocks", which are no longer rule terms. The effect itself is still true (the notice moves the added excess from 0 to 70 here). Carried: O3, O5, O7, O8, O15, O16, O18, half-cent ties.

## closing_checklist (revision 5)

Written after both round-5 reveals (2026-10-15T16:20Z).

- Files: each of 0.md, 1.md and _difficulty.md carries `## revision_5` below the untouched revisions 1-4.
- Values: every scored value unchanged (task 0: 272.61 / 811 / 362 / 60; task 1: 37.00 / 29.03 / 9 x 27.38); tools byte-identical; scopes, trees and owners unchanged.
- XF class: S-1, S-2 and S-3 closed. Each rule has a standard method in record terms and one generic combination sentence; every factor sentence acts on a standard quantity; no factor id is named in any baseline, result or plain-binding quote; no factor binding reads another factor's binding.
- Factors: counts and labels unchanged; every factor bears weight against an honest reachable baseline. The restocking-form factor-alone figure moved 29.97 -> 28.85 with its fall-through now the standard basis.
- Outstanding: **R5-1** (SOURCE-POLICY, hardship `compute_basis.ostomy_active` quote not verbatim in the rule; charter-level, no task consequence). Observations O19, O20 new; O3, O5, O7, O8, O15, O16, O18 and the half-cent ties carried; O17 closed.
- Not closed until R5-1 is fixed (a one-line quote correction; the gate `check_extended.py` does not test compute_basis quotes, so it will not catch a regression of this kind).

VERDICT revision_5: task0=PASS task1=PASS charter=R5-1

## revision_6

### entry and snapshot (revision 6)

- `tail -1 REWORK.log`: `REWORK round 6: gates green` — entry condition met.
- `/tmp/erl0063_coord/snapshot.sh continence_supply_program_services` output (executed 2026-10-15T17:01Z, copy in `/tmp/audit_continence_0063/snapshot_r6.txt`):
  - check_extended: EXTENDED OK; check_task_tools: TASK TOOL CONTRACT OK; replay_tasks: REPLAY OK; check_solvability: SOLVABILITY OK; check_compute: COMPUTE OK; check_grounding: GROUNDING OK; check_traceability: TRACEABILITY OK; check_cross_fire: SCOPE OK
  - 252b812c891c730fec0f71b59dd629b32ff6e2b320e122f73d9ad1c972486ad3 0.view.json (unchanged)
  - d6c9809c07a508a90427f44d9a3b3c0bc9652c432b92b147e35e74111e0028a1 1.view.json (unchanged)
  - 61b2f0b48030496d2f6012a081039f5be80a0fc5a9cf48e13ff4497d073072fb continence.extended.yaml (changed)
  - 8cf6605b6475987c287664c734abb0d0b45d45eebf0df5c418d74dee92f14ded task_tools.py (unchanged; byte-identical to the round-3 snapshot)
- Hashes re-checked independently; base section byte-identical to the blueprint charter. contamination_disclosure: earlier GT already read; regression re-verification.

### changes reviewed (revision 6)

Diff against the round-5 snapshot (`/tmp/audit_continence_0063/r5/` → `r6/`): four hunks only.

- **R5-1 closed.** `compute_basis.ostomy_active` now quotes "When the customer also holds an Ostomy Supply Program in active status", a verbatim substring of the hardship rule that states exactly what `EXISTS('ostomy', status='active')` tests. Sweep of every `compute_basis` quote in all six policies: 112 quotes, 0 non-verbatim.
- **O19 closed.** Hardship overwrite #3 replaced_by and the rule sentence now read "the waived amount is counted by this policy's open-amount deduction, which sets the customer's recent payments against the waived amount first; for every other purpose a payment is still applied to the oldest unpaid posting first". The terms match the standard method ("the waived amount") and the factor heading ("Open-amount deduction"); replaced_by is verbatim in the rule; the declared override of the oldest-first sentence keeps its meaning.
- **O20 closed.** The refill→abn edge `effect` now reads "With the notice on file and no qualifying over-limit record, the order's excess for the refill is added to the refill's units, never more than the notice's units, so the refill units rise by that amount instead of nothing", which uses current rule terms and is true on task 0 (+70).
- No other line changed: rule texts, compute, factors, baselines and prerequisites are otherwise identical to revision 5. Stale-term scan of the charter ("open amount", "route cap", "increase blocks", "Assembly"): none.

### checks (revision 6)

- Mechanical (`r2.py`, `trans.py`): all quotes, baseline sentences, replaced_by and policy_source verbatim; no factor binding reads another factor's binding (known string-literal false positive only).
- Values (`r2t0.py`, `r2t1.py`, `probe_n2.py`): task 0 — 272.61 / 811 / 362 (60 days), sensitivities 67.68/515.61/196.88/227.17 (172.60), 251/891/506/711/800 (120), 532/392/292/432/402/374 (594); task 1 — 37.00 / 29.03 / 9 × 27.38, sensitivities 0.00/27.75/55.50/74.00 (0.00), 64.52/28.85/29.97/28.10/28.72 (66.60), 25.00/49.28/35.20/32.86 (54.76); skip effects 292, 27.33, 29.80; decoy probes 0.00 / 0.00 / 0.00 — all identical to revision 5. Revealed task files carry the same gold steps and figures; the task-0 rationale now records that its effect/closure/dossier no longer use the retired terms.

### findings (revision 6)

- R5-1, O19, O20 closed; no new RED; nothing regressed. Open observations only: O3, O5, O7, O8, O15, O16, O18, half-cent ties in two task-0 sensitivity figures.

## closing_checklist (revision 6)

- Files: each of 0.md, 1.md and _difficulty.md carries `## revision_6` below the untouched revisions 1-5.
- Gates: coordinator snapshot above, all eight OK on this final form.
- Scope, tools, uuid8s, trees, owners, factor counts and labels unchanged from revision 5. Every factor bears weight against an honest reachable baseline. Gold equals the derivation in both tasks.
- No RED outstanding. The difficulty passes the source-layer audit at revision 6.

VERDICT revision_6: task0=PASS task1=PASS charter=CLEAN
