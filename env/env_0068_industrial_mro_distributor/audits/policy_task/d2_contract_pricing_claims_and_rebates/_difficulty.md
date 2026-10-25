# Policy-task audit — d2_contract_pricing_claims_and_rebates / charter-global

## revision_1

## charter_global_frozen
- Freeze time: 2026-10-16T23:46Z (written before any task's GT was revealed; nothing in this section derives from a revealed GT).
- Auditor: erl-task-policy-audit agent (independent of the instantiator).
- Frozen inputs (sha256, paths relative to env/env_0068_industrial_mro_distributor/):
  - `84cc274862d36ff4260297699028d7838541bfa11d238aa113b4f3eb5056a2fc  tasks/d2_contract_pricing_claims_and_rebates/pricing.extended.yaml`
  - `063dbb2aa6bc4517c78e58187d79247d1a0f936e9341492e3ce2220037efeb96  tasks/d2_contract_pricing_claims_and_rebates/task_tools.py`
  - masked views `.audit_views/policy/d2_contract_pricing_claims_and_rebates/r1/task0.view.json` (d09770e6…20ef) and `task1.view.json` (a8f924ab…6c41); hashes re-computed and matching the brief.
- Read: blueprint/ (blueprint.yaml, db_schema.json, share_tools.py, products/pricing.yaml, order.yaml, credit.yaml, vending.yaml excerpts), the extended charter, task_tools.py, the two masked views, audits/render_source/XF_recipe.md.
- Masked / unread until every derivation was frozen: tasks/<i>.json (evaluation_criteria, computations, solvability_contract, prerequisite_closure, charter_scope, required_documents, design_rationale, db_closure), plan.md, worklog.md.
- Entry conditions: gate snapshot supplied with the brief and saved at `.audit_views/policy/d2_contract_pricing_claims_and_rebates/r1/gates.txt` (EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK); masked views supplied with hashes. Inputs complete.
- Base copy: `diff` of the extended file's base section against `blueprint/products/pricing.yaml` differs only by the trailing header comment line `# ---- extended policies (d2_…) ----` — base copy verbatim.
- DSL semantics used (MONTHS = whole months, minus one when the end day-of-month is earlier; `within_months=N` keeps rows with 0 <= MONTHS(row date, NOW) < N; LATEST/XLATEST keep the first row met on a same-date tie (strict `>`); RND = Python round) were read from `skills/erl-task-instantiate/scripts/check_compute.py` lines 224-395 — a generic script outside the brief's listed read domain that carries no task data; disclosed here as a read-domain deviation, not GT contact.

### policy_conflict_scan
Seven extended policies, two prerequisite components (derived from the `prerequisite` graph alone):
- Component A (rebate ledger): `pricing_ext_return_clawback` (agent, `book_rebate_return_clawback_ccd0c1e2`) -> `pricing_ext_termination_forfeiture` (agent, `book_termination_rebate_forfeiture_47cc59ce`) -> `pricing_ext_final_rebate_check` (user, `request_final_rebate_check_d4aa8dfe`).
- Component B (contract item / claims): `pricing_ext_open_claim_decision` (agent, `decide_pending_price_claim_4f6327a3`) -> `pricing_ext_discontinued_closeout` (agent, `close_out_discontinued_item_dd8bcab8`) -> `pricing_ext_substitute_protection` (agent, `protect_substitute_price_656c6d72`) -> `pricing_ext_substitute_claim` (user, `file_contract_price_claim_992a36b2`).
- The two components share no policy, no tool and no ledger row type (A writes `pricing_rebates`; B writes `pricing_claims` and `pricing_items`), so two tasks claiming one component each are pairwise disjoint and jointly cover all seven extended policies. (The tasks' own `charter_scope` is masked; this is checked against it in the closing checklist.)
- Overlapping subjects: clawback and forfeiture both write `pricing_rebate_reversed`; they are told apart by `source_reference` (RMA number vs agreement number) and both scopes are self-naming; no conflict. Closeout, protection and substitute claim all select "the latest backorder on the customer's ship-tos" and its fill; the selections are identical expressions, no conflict.
- Conflicts found (each written up under findings): CG-1 (open-claim rule vs in-force `pricing_price_basis` / `pricing_evt_price_claim`), CG-2 (closeout rule vs protection rule on the protected price), CG-3 (closeout gap sentence vs open-claim overwrite on "the item's latest contract unit price").
- Cross-category read boundaries: every cross read is declared in `cross_category` and reaches only the customer's own rows through share finders (find_order_lines / find_order_returns / find_credit_accounts / find_credit_transactions / find_vmi_programs / find_vending_machines). No write touches another category.

### rule_compute_equivalence
- Scratch sweep `/tmp/audit_d2_contract_pricing_claims_and_rebates_0068/scripts/sweep.py`: every `compute_basis` quotation of all seven policies is verbatim in its rule (XF6 clean); every `baseline.rule` sentence is a sentence of its rule; every `prerequisite.policy_source` is verbatim in its own rule.
- Every factor ladder tier is a rule sentence and a branch of its `decides` binding, and vice versa (checked by reading each ladder against its binding; no tier lives only in compute).
- Defects of this check, each a finding below: rounding placement (CG-4, XF7), whole-month and tie conventions (CG-5, XF9), filters the rule states but the compute omits or vice versa (CG-9, XF10), a plain binding only one factor uses (CG-8, XF1), assembly sentences that name factor quantities (CG-7, XF2).
- Other sweeps: no factor binding reads another factor's binding (mechanical); order of non-commuting steps is fixed in every rule (cap-then-reductions in open claim; shares-then-cap in clawback; reliefs/holdbacks/concessions summed and applied once; settlement multiplier before credits in the substitute claim) — XF3 clean; no rule defines a quantity "as another policy figures it" (XF4 clean — the final-check prerequisite sentence names "the termination period", defined only in the forfeiture rule, but it names a waited-on record, not a computed quantity; observation O-4); XF12 not triggered (every two-date DAYS test is on single selected records).

### action_binding_and_uuids
- (target_tool, computes) pairs: each of the seven tools is claimed by exactly one policy; no share tool writes pricing rows (share_tools.py writes only identity verifications and handoffs).
- uuid8 tails ccd0c1e2, 47cc59ce, d4aa8dfe, 4f6327a3, dd8bcab8, 656c6d72, 992a36b2: no shared prefix, no sequence, no reuse.
- Docstrings: no tool names another tool, states a position in a sequence or carries an ordering word (the three "once the … is booked/recorded" phrases describe the returned balance, not an order). No docstring or Arg carries a concrete example value (XF8 clean). Every effect a docstring claims is in the body (checked tool by tool). No tool body validates any prerequisite (no reads of rebate ledger, claims or item lines beyond copying the current line's attributes) — the tool layer judges nothing.
- Owners: two `owner=user` tools (final rebate check, contract price claim), one per component.

### prerequisite_graph
| edge | kind / gate | form | policy_source locatable | resolved_by = depended-on target_tool | gate binding exists |
|---|---|---|---|---|---|
| forfeiture <- return_clawback | value_input / term_net | state | yes (rule s3) | yes | yes |
| final_rebate_check <- forfeiture | value_input / bal | state | yes (rule s3) | yes | yes |
| closeout <- open_claim_decision | value_input / ref_price | state | yes (rule s4) | yes | yes |
| protection <- closeout | value_input / ending | state | yes (rule s4) | yes | yes |
| substitute_claim <- protection | value_input / prot_price | state | yes (rule s3) | yes | yes |
- `prerequisite: []` on return_clawback and open_claim_decision. Every `problem` is an extended id of this file, none is base, none self. Graph is two chains — acyclic. No `fallback_reason` (no action-form edge). Conditions restate the sentences at the same strength; no authoring-viewpoint phrasing.

### prerequisite_sentences
- Four-point test, all five edges: ordering connective present ("only after", "not issued until", "only after", "not set until", "only after"); each waits on a record-visible state (clawback entry on the rebate ledger; forfeiture entry; a decision on every pending claim; the close-out line; the protection line); none names a tool, policy id, snake_case token or row id; strength matches `condition`.
- Exactly one write brings each state about (share tools write nothing here): clawback entry <- book_rebate_return_clawback; forfeiture entry <- book_termination_rebate_forfeiture; claim decision <- decide_pending_price_claim; close-out line <- close_out_discontinued_item; protection line <- protect_substitute_price.
- Derivations (sentence + records + depended-on rule -> resolving action): forfeiture: returns received after the termination period's accrual whose line shipped in that period -> the clawback rule "books the rebate clawback for one return" -> clawback write. Final check: "forfeiture entry for the termination period" -> forfeiture rule -> forfeiture write. Closeout: pending claims on the item -> open-claim rule "decides the price claim most recently filed … while no decision has been recorded" -> decision write. Protection: "close-out line of the discontinued item" -> closeout rule "The close-out is a removal line …" -> close-out write. Substitute claim: "the substitute's protection line" -> protection rule "adds the price protection line …" -> protection write. One reading each.
- The depended-on rules carry no restatement of a prerequisite sentence, with one exception: the closeout rule's second sentence ends "that is the price a protection of the substitute carries", a statement about its dependent's quantity in the depended-on rule — finding CG-2.
- Observation O-5: the closeout edge's state ("every price claim pending on that item carries a decision") has a write only for decisions the open-claim rule makes (denied / referred); for a pending claim "the desk could approve" the rule sends it to the base claim rule, and no tool of this difficulty records an approved decision. Not reached on this difficulty's worlds.

### override_declarations
Sentence-by-sentence against each `base_policy_refs` entry (s = sentence order in the base rule):
- return_clawback vs pricing_evt_rebate: s5 (clawback) retired, replaced_by restates it for every other return and names own scope; s1-s4, s6 followed. Clean.
- termination_forfeiture vs pricing_evt_rebate: s6 retired with scoped restatement; vs pricing_renewal_and_termination: s1-s7 followed (no conflict). Clean.
- final_rebate_check vs pricing_evt_rebate: s4 (payout) retired with scoped restatement; the min-payout carry-forward is restated in the rule. Clean.
- open_claim_decision vs pricing_evt_escalation: s5 (escalation size) retired with scoped restatement; s1-s4, s6, s7 followed. vs pricing_evt_price_claim: s6 decision ladder followed in shape (referred / denied, claim amount 0.00), "a claim the desk could approve is decided under the base claim rule". **Undeclared:** the rule fixes "the unit price the agreement sets for the claimed line" at the reviewed price, while in-force `pricing_price_basis` s1 (not in base_policy_refs, no overwrite) fixes the price of a billed line at "the item's contract unit price from the latest pricing_items line for that sku effective on or before the ship date", and `pricing_evt_price_claim` s1/s5 measure the claim against "the price pricing_price_basis sets" — finding CG-1.
- discontinued_closeout vs pricing_evt_contract_items: s6 (removal notice) retired with scoped restatement; s7 (substitute protection) is retired by the sibling protection policy, not here, and the closeout rule's "that is the price a protection of the substitute carries" re-asserts the retired s7 content for the protected substitute — finding CG-2. vs pricing_price_basis: followed (a removal ends the contract basis).
- substitute_protection vs pricing_evt_contract_items: s7 and s2 retired with scoped restatements; s1, s4, s5 inherited (live agreement, usage and max-items gates hold on task worlds — checked per task). vs pricing_price_basis: followed. No sibling retires the same clause (XF5 sibling rule not triggered).
- substitute_claim vs pricing_evt_price_claim: s5 (claim amount) retired with scoped restatement; s1-s4, s6-s8 inherited.
- 0/1 multiplier and dropped-branch scan: the `in_scope` multipliers zero only out-of-scope cases the rules name ("… is not booked / closed out / protected / claimed under it"); no base branch is silently dropped.

### factor_ladders
| policy | factor | effect | tiers | multi-source | cross_difficulty |
|---|---|---|---|---|---|
| return_clawback | merchandise_value_basis | method | 3 | no | order |
| | return_reason_share | parameter | 4 | no | order |
| | credit_size_share | parameter | 3 | no | order |
| | return_frequency_share | parameter | 3 | no | order |
| termination_forfeiture | commitment_attainment_relief | method | 3 | no | – |
| | tenure_relief_share | parameter | 3 | no | – |
| | extra_notice_relief | parameter | 3 | no | – |
| | kept_program_relief | parameter | 3 | yes (vmi and/or vending holdings) | vmi (+vending) |
| | period_alignment_relief | parameter | 3 | no | – |
| final_rebate_check | returns_reserve_holdback | parameter | 3 | conjunction over one row set | order |
| | credit_exposure_holdback | parameter | 3 | no | credit |
| | payment_terms_holdback | parameter | 3 | no | credit |
| | unexpired_term_administration | method | 3 | no | – |
| | open_authorization_holdback | parameter | 3 | yes (authorization + absence of settlement rows) | order |
| | returned_payment_holdback | parameter | 3 | no | credit |
| open_claim_decision | increase_measure_basis | method | 3 | yes (add line vs escalation line) | – |
| | shipped_volume_reduction / commitment_reduction / notice_margin_reduction / contract_breadth_reduction / escalation_load_reduction | parameter | 3 each | no | order / credit / – / – / – |
| discontinued_closeout | closeout_reference_basis | method | 3 | yes (claims, item lines, backorder fill) | – |
| | discontinued_usage_concession / stranded_order_concession / substitute_gap_concession | parameter | 3 each | no | order |
| substitute_protection | substitute_start_basis | method | 3 | no | order |
| | substitute_adoption_concession / kept_program_concession / prompt_payment_concession / agreement_tenure_concession | parameter | 3 each | programs: yes | order / vmi / credit / – |
| substitute_claim | returned_quantity_basis | method | 3 | no | order |
| | invoice_settlement_multiplier | method | 4 | yes (invoice row + discount row) | credit |
| | repeat_overbilling_credit / paid_invoice_credit / prompt_claim_credit | parameter | 3 each | paid: yes | – / credit / – |
- Counts per policy (4..6, >=2 parameter, >=1 method): 4/5/6/6/4/5/5 factors; all bounds met. Each `decides` is an input, not `result`; binding sets disjoint; fall-through tier = baseline in every factor.
- No two tiers of any ladder select the same value or method; every ladder's tiers are pairwise disjoint as stated.
- Method honesty and XF11 pairwise distinguishing inputs: merchandise value (qty x invoiced price / credit + restocking fee / credit — distinguished by an opened item, whose credit carries the opened-item percentage, e.g. task0's RMA-208152: 5834.40 vs 4667.52 vs 4084.08); commitment relief (fixed share / sliding share / none — differ for any attainment in [1,1.5)); administration (flat / per month — differ for 1..5 months); settlement multiplier (four formulas, distinct whenever tax and discount are nonzero); start basis (own price / ending + share of gap / ending). Three method factors select a basis rather than a formula shape — increase_measure_basis (list series / zero / cost series), closeout_reference_basis (decided / pre-escalation / current price), returned_quantity_basis (billed less received / less authorized / billed; tiers 1 and 2 coincide whenever the full authorized quantity is received, distinguished only by a partial receipt) — judged honest basis selections, recorded as observation O-1.
- Realism of conditions and outcomes: one tier outcome is not what the business does — the settlement multiplier's first tier (finding CG-6). Doubtful but not demonstrable: the prompt-claim credit (O-2) and the protection's tenure anchored on the proposal date (O-3). Every other tier condition is one an MRO distributor weighs (return reason and size, return frequency, commitment attainment, tenure, notice, kept programs, receivable exposure, finance charges, returned payments, open RMAs, unexpired term, volume, breadth, escalation load, stranded backorders, substitute price gap, adoption, prompt payment) and none holds for every customer reaching its write.

### findings
Each finding names the tasks whose files demonstrate its consequence. Tasks are referred to by component (A = rebate chain, B = claims chain); the per-task files map them to task ids.

**CG-1 SOURCE-POLICY RED — undeclared override (XF5).** Symptom: two in-force passages give the claimed line two prices. Evidence: open_claim_decision rule s1 "it records on the decision the unit price the agreement sets for the claimed line as this rule reviews that escalation", s5 "The unit price the agreement sets for the claimed line is the escalation line's prior unit price raised by the reviewed escalation allowance"; base `pricing_price_basis` s1 "The price of a billed line is … the item's contract unit price from the latest pricing_items line for that sku effective on or before the ship date"; base `pricing_evt_price_claim` s1 "billed above the price pricing_price_basis sets", s5 "the unit price the agreement sets for the line's ship date". The only overwrite retires `pricing_evt_escalation` s5 (how an escalation is sized); `pricing_price_basis` is not in base_policy_refs and is not overwritten. Root cause: the extended rule replaces the price of a recorded line without retiring the base clause that reads it off the record. Consequence: on a claim within scope the base clauses give the recorded escalation price (and a denied decision), the extended rule a reviewed price — demonstrated in component B's task file. Affected: open_claim_decision `overwrite`/`base_policy_refs`, rule s1/s5; scored decision price and every value downstream.

**CG-2 SOURCE-POLICY RED — extended rule vs extended rule, and a dependency statement in the depended-on rule.** Evidence: discontinued_closeout rule s2 "records, as the contract unit price that ends, the close-out price this rule works out; that is the price a protection of the substitute carries"; substitute_protection rule s5-s11: the protected price starts from that ending price, may start instead from the substitute's own price or from the ending price plus gap_share of the difference, and is reduced by four concessions. Same situation (the protected substitute), two prices. The clause also restates, in the depended-on rule, what the dependent problem's result is (check 6: the depended-on rule does not speak to the dependency). Consequence: demonstrated in component B's task file. Affected: closeout rule s2; protection and substitute-claim scored values.

**CG-3 SOURCE-POLICY RED — second reading of the gap reference.** Evidence: closeout rule s9 "how far the substitute's unit price on its latest regular shipment stands above the discontinued item's latest contract unit price" (binding `latest_price` = contract unit price on the latest price line); the baseline sentence instead says "the contract unit price on the discontinued item's latest price line"; the open-claim overwrite declares "the price the agreement sets is the reviewed escalated price" for exactly this escalation, and that decision row is the latest record carrying a contract unit price for the item. A reader may take the item's latest contract unit price to be the reviewed price. Consequence: demonstrated in component B's task file. Affected: closeout rule s9, factor substitute_gap_concession.

**CG-4 SOURCE-POLICY RED — rounding placement (XF7), whole class.** Every extended rule states an intermediate rounding in its baseline chain and then "rounded … once, on the final figure": return_clawback s6 ("…divided by 100, rounded half up to the cent") + s11; termination_forfeiture s5 + s11; final_rebate_check s4 + s13; open_claim_decision s5 + s12; discontinued_closeout s5 + s10; substitute_protection s5 + s11; substitute_claim s6 + s12. The compute rounds only at `result`. Whether the shares/reliefs/holdbacks act on the rounded or unrounded intermediate is a second reading wherever the intermediate is not already at the rounding precision. Consequence demonstrated on component A (clawback); on the other members the intermediate is already at precision on these worlds (net rebate, balance, a 4-decimal price, a cents product), so no number moves there.

**CG-5 SOURCE-POLICY RED — whole-month and tie conventions (XF9), whole class.** (a) termination_forfeiture s7 "the whole months from the agreement effective date to the termination effective date" states no counting convention, while the base charter counts a term inclusively (pricing_agreement_eligibility s5: a term "ends agreement_term_months calendar months later, on the day before the same calendar day"), under which an agreement in force from the 1st of a month to the last day of a month 30 months later has run 30 months, and MONTHS() gives 29. Consequence demonstrated on component A. Other members, same missing convention, no number moves on these worlds: final_rebate_check s10 (months of term remaining, MONTHS(closed, expiration)); substitute_protection s10 (months from proposal date); every "less than N whole months before the handling date" window — clawback frequency (12), forfeiture attainment (12), final reserve (3) / terms (12) / returned payments (12), open-claim volume / commitment / load (12), closeout usage (12), protection adoption (3) / prompt payment (12). (b) Same-day ties: no rule states which row wins a same-date tie for "most recently received return", "latest rebate accrual", "most recently authorized return", "latest backorder", "latest regular shipment", "most recent invoice", "claim most recently filed", "latest price line" (the DSL keeps the first-iterated row); no tie occurs on these worlds.

**CG-6 SOURCE-FACTOR RED — unreal method tier (realism).** substitute_claim s8 / factor invoice_settlement_multiplier tier 1: "an invoice that carried sales tax and earned a discount takes one plus the tax rate times one less the discount rate". The scenario's own credit charter (credit_evt_cash_discount s1) grants the cash discount "on the merchandise subtotal of the invoice it pays, never on freight or sales tax", so what the customer actually paid on an overbilled amount X is X(1 + t − d); the product form also discounts the tax (X·t·d too little). A distributor refunding an overbilling refunds the overcharge plus its tax less the discount earned on the overcharge, not a discount on tax. Consequence demonstrated on component B. Affected: rule s8, compute `settle_mult`.

**CG-7 SOURCE-POLICY RED — assembly sentences name factor quantities (XF2), whole class.** substitute_claim s12 "the overbilling per unit times the claim quantity, times the settlement multiplier, plus the credits …" (the settlement multiplier exists only as a factor); discontinued_closeout s10 and substitute_protection s11 "taken off the starting price once" (the starting price is defined only by the method factor's sentence; the baseline defines the close-out / protected price directly). The other five assembly sentences name only baseline quantities. No per-task number moves; recipe class.

**CG-8 SOURCE-POLICY RED — plain binding only one factor uses (XF1).** substitute_claim `ship_order`, `ship_line` are declared plain, quoted from the factor sentence "Where a return receipt for the shipment's order line is on record,", and read only by `rcv_qty`/`auth_qty` of returned_quantity_basis; the baseline never uses them. No per-task number moves; recipe class.

**CG-9 SOURCE-POLICY RED — rule/compute filter mismatch (XF10), whole class.** substitute_claim s1 "when that shipment is billed on the customer's most recent invoice" — the compute tests only the invoice date window (no shipment-to-invoice link); open_claim_decision `add_cost`/`add_list` filter `change_reason='new_item'`, which the rule ("the line that added the item") does not state. No per-task number moves on these worlds; recipe class.

Observations (no demonstrable consequence): O-1 basis-selection method factors (see factor_ladders); O-2 the prompt-claim credit (substitute_claim s11) pays a bonus for filing early — doubtful as a published MRO treatment, not demonstrable; O-3 protection tenure counted from the proposal date (s10), not from the effective date or customer_since — no tier change on these worlds; O-4 the final-check prerequisite sentence relies on "the termination period", defined in the forfeiture rule; O-5 no write exists for a pending claim the desk could approve; O-6 the clawback compute floors at 0 (`MX(0, …)`) without a rule sentence (reachable only when the period's net is negative); O-7 decide_pending_price_claim's `outcome` description lists "or the overbilling is below the tier's smallest claim" under denied, a branch the extended rule sends to the base rule.

## closing_checklist
Written after both tasks' derivations were frozen and both GT reveals compared (2026-10-17). The difficulty does **not** pass the source-layer audit: open REDs remain.
- Audit files: `0.md`, `1.md` one per task, `_difficulty.md` alongside; revision_1 is the first revision. Comparison sections: task 0 and task 1 match gold on every write, owner, order, parameter, tree edge and factor figure, but neither carries a PASS (see their verdict lines).
- Coverage and scopes: task 0 `charter_scope` = {final_rebate_check, termination_forfeiture, return_clawback}; task 1 = {substitute_claim, substitute_protection, discontinued_closeout, open_claim_decision} — the two components of § policy_conflict_scan, pairwise disjoint, jointly all seven extended policies; task tools closed; uuid8s independent (§ action_binding_and_uuids).
- Trees: task 0 two prerequisites / two value_input edges; task 1 three prerequisites / three value_input edges; each has an owner=user root; the difficulty's graph is two disjoint chains, acyclic.
- Factors: every computation declares a self-sufficient baseline and 4-6 factors (>=2 parameter, >=1 method); every factor bears weight on its world and every whole-baseline figure differs from gold (per-task factor_weight, matched figure-for-figure against factor_sensitivity); each task has a multi-source and a cross-difficulty factor. One ladder tier is unreal (CG-6).
- Gates: not re-run by the auditor (brief: the coordinator supplies the gate snapshot). The audited artifacts are unchanged since the snapshot (pricing.extended.yaml 84cc2748…, task_tools.py 063dbb2a…, re-hashed at close), so `.audit_views/…/r1/gates.txt` still describes the final form.
- Open charter REDs, each closed by one rework of its whole class as listed under § findings: CG-1 (XF5, one member), CG-2 (one member), CG-3 (one member), CG-4 (XF7, seven members), CG-5 (XF9, month-count members and tie members listed), CG-6 (realism, one member), CG-7 (XF2, three members), CG-8 (XF1, one member), CG-9 (XF10, two members).

VERDICT revision_1: task0=RED(SOURCE-POLICY:CG-4,CG-5) task1=RED(SOURCE-POLICY:CG-1,CG-2,CG-3;SOURCE-FACTOR:CG-6) charter=CG-1,CG-2,CG-3,CG-4,CG-5,CG-6,CG-7,CG-8,CG-9

## revision_2

## charter_global_frozen (revision_2)
- Freeze time: 2026-10-17, before any round-2 GT was read. Auditor: erl-task-policy-audit agent (same auditor as revision_1).
- Entry gate: `tail -1 tasks/d2_contract_pricing_claims_and_rebates/worklog.md` = `REWORK round 2: gates 8/8 green` (only that line read). `/tmp/erl0068_coord/snapshot.sh d2_contract_pricing_claims_and_rebates 2` executed (not read): gates EXTENDED / TASK TOOL CONTRACT / REPLAY / SOLVABILITY / COMPUTE / GROUNDING / SCOPE all OK (`.audit_views/policy/d2_contract_pricing_claims_and_rebates/r2/gates.txt`). Inputs complete.
- Hashes (round-2 entry input): pricing.extended.yaml `c19bb902c70d273a7bc32e6567033ed30baf5db824965d2d2c35497715bbaa7a` (changed from 84cc2748…, so every charter-global section is re-derived below); task_tools.py `063dbb2aa6bc4517c78e58187d79247d1a0f936e9341492e3ce2220037efeb96` (unchanged — § action_binding_and_uuids of revision_1 carried forward on that ground); r2/task0.view.json `0e76b34b8d54e87966496ed50292d04c01cb48082e1ad9f4014949f0e3e20257`, r2/task1.view.json `4d55979cc84f94841b0752a7ebf7eb46db143f5c8ed3560f6c49880770c45cbc`.
- Base copy: diff against blueprint/products/pricing.yaml still differs only by the header comment — verbatim.
- contamination_disclosure (revision_2): the auditor read round-1 GT (tasks/<i>.json) after the revision_1 freeze, so the round-1 gold values are known to it. Round-2 derivations rest on the r2 charter and r2 views alone; the r2 task JSONs were not opened before the freezes below. No other GT contact.

### changes found (charter r1 -> r2, by reading the r2 charter)
- Every extended rule gains one conventions sentence (whole months = MONTHS() definition; calendar days count the later date not the earlier; latest = latest date, same-date ties -> the record recorded first; the substitute claim carries only the day and tie parts — it counts no months).
- Every rule now carries one rounding sentence ("rounded … once, on the final figure") and its assembly sentence names the order (shares / reliefs / holdbacks / reductions / concessions / multiplier and credits applied "before that floor / that rounding").
- open_claim_decision: new overwrite of `pricing_price_basis` s1 (scoped to "the claimed line of an escalation this policy reviews on a pending claim", restating s1 for every other line), base_policy_refs + pricing_price_basis; scope now "for the item of the latest backorder on the customer's ship-tos, the price claim most recently filed … for that item"; "(its new-item line)" added; denied branch adds "or the overbilling is below the tier's price_claim_min_usd".
- discontinued_closeout: "that is the price a protection of the substitute carries" deleted; prerequisite sentence now "fixed only after the price claim most recently filed on that item carries a decision"; method tiers say "the close-out price is instead …"; gap reference now "the contract unit price on the discontinued item's latest price line"; assembly "taken off the close-out price once".
- substitute_protection: method tiers "the protected price is instead …"; assembly "taken off the protected price once".
- substitute_claim: scope now "the contract price claim the customer files, on the customer's most recent invoice, for the latest regular shipment …, when that invoice is dated on the shipment's ship date or within invoice_window_days days after it"; settlement tier 1 "one plus the tax rate less the discount rate, the discount having been earned on the merchandise only"; `ship_order`/`ship_line` moved into returned_quantity_basis bindings; assembly "The multiplier this policy sets multiplies the unrounded claim amount, and every credit this policy sets adds its percent of that same unrounded claim amount".
- termination_forfeiture: prerequisite sentence now "…a clawback entry for the customer's most recently received return whenever that return is of termination-period merchandise received after the termination period's accrual"; replaced_by "stays on the rebate ledger unforfeited".
- final_rebate_check: prerequisite sentence now "…the forfeiture entry for the rebate period in which the termination took effect"; exposure sentence "(a customer holds one)".

### policy_conflict_scan / rule_compute_equivalence / prerequisite_graph / prerequisite_sentences / override_declarations / factor_ladders (re-derived)
- Components and disjointness unchanged (two chains, seven policies). No extended-vs-extended or extended-vs-base conflict remains: open-claim vs pricing_price_basis now declared (one overwrite of that clause, no sibling); closeout no longer states the protected price; the gap reference names a record field.
- XF6 sweep (`scripts/sweep.py` on the r2 file): every compute_basis quote verbatim in its rule; every baseline sentence in its rule; every policy_source verbatim. Every ladder tier is in its rule and its binding. No factor reads another factor's binding; the only plain bindings consumed by a single factor are baseline fall-through quantities (ret_credit, cost_pct, ending, billed_qty) that the baseline itself uses.
- Prerequisite graph: same five state-form value_input edges, gates exist, acyclic, conditions restate the new sentences at the same strength (forfeiture: "When the customer's most recently received return was received after …"; closeout: "The pricing_claim_filed line most recently filed … for the discontinued item number …"). Four-point test passes on all five; exactly one write per waited-on state; no depended-on rule speaks to its dependent.
- Override declarations: as revision_1 plus the open-claim overwrite of pricing_price_basis s1 — scoped, restating, no deferral to a retired clause ("a claim the desk could approve is decided under the base claim rule" defers to pricing_evt_price_claim, which no extended overwrite retires).
- Factor ladders: factor sets, effects, tier counts and bindings unchanged except settle_mult tier 1 and the returned_quantity_basis binding set; counts 4/5/6/6/4/5/5, bounds met; no two tiers coincide (settlement: 1+t−d / 1+t / 1−d / 1, distinct whenever t, d > 0).

### XF_recipe re-check (every point, every extended policy)
1 factor independence — clean (mechanical). 2 assembly — clean: all seven assembly sentences name only baseline quantities or "the … this policy sets". 3 order — clean: every non-commuting step ordered in its rule. 4 no "as another policy figures it" — clean (final-check prerequisite now names "the rebate period in which the termination took effect"). 5 overwrites — clean (see above). 6 quotes verbatim — clean. 7 rounding — clean: one rounding sentence per rule, matching RND at `result`. 8 docstrings — clean (tools unchanged; decide tool's denied description now matches the extended denied branch). 9 edges — clean: whole months, calendar days and same-date ties stated in every rule that uses them; absent-record and zero-division branches guarded and stated. 10 filters — clean: the substitute claim no longer asserts an unchecked invoice link; the new-item filter is stated. 11 method tiers — no coincidence on reachable domains (pairwise table of revision_1 stands; settlement tiers distinct). 12 cross-record windows — not triggered. 13 seeded rows of other categories — re-checked per task (no change to order/credit/vmi/vending rows on either world).

### round-1 RED closure
| id | class | r2 status | evidence |
|---|---|---|---|
| CG-1 | XF5 undeclared override | closed | open_claim overwrite of pricing_price_basis s1, scoped and restating |
| CG-2 | rule vs rule | closed | closeout s2 ends at "the close-out price this rule works out" |
| CG-3 | second reading of gap reference | closed | closeout gap sentence names "the contract unit price on the discontinued item's latest price line" |
| CG-4 | XF7 rounding (7 members) | closed, all 7 | one rounding sentence per rule; assembly sentences fix "before that rounding" |
| CG-5 | XF9 conventions (all members) | closed, all members | conventions sentence in every rule; tenure now defined as MONTHS() |
| CG-6 | unreal method tier | closed | settlement tier 1 = 1 + t − d, stated as discount on merchandise only |
| CG-7 | XF2 (3 members) | closed, all 3 | "the multiplier this policy sets"; "taken off the close-out price / protected price" |
| CG-8 | XF1 | closed | ship_order/ship_line in returned_quantity_basis bindings |
| CG-9 | XF10 (2 members) | closed, both | claim scope reworded to the date test; "(its new-item line)" stated |

### findings (revision_2)
No open SOURCE-POLICY or SOURCE-FACTOR finding at charter level. Observations carried or new: O-1 (basis-selection method factors) and O-2 (prompt-claim credit realism doubt) and O-3 (protection tenure from the proposal date) carried, unchanged text in r2; O-4, O-5, O-6, O-7 closed by the rework. New O-8: open_claim_decision's scope now depends on the claimed item being "the item of the latest backorder on the customer's ship-tos" — a pricing desk does not condition an escalation review on backorder recency; a pending escalation claim on any other item falls to the base rules. Not reached on these worlds, no number moves. New O-9: the forfeiture now waits only on the most recent return's clawback; an older termination-period return received after the accrual would be clawed back under the base clause with no ordering stated. Not reached on these worlds.

## closing_checklist (revision_2)
Written after both revision_2 derivations were frozen and both round-2 reveals compared (2026-10-17).
- Audit files `0.md`, `1.md`, `_difficulty.md`; revision_1 text untouched, revision_2 appended to each; both revision_2 comparison sections carry PASS on all four relationships.
- Scopes: task 0 = {final_rebate_check, termination_forfeiture, return_clawback}, task 1 = {substitute_claim, substitute_protection, discontinued_closeout, open_claim_decision}: pairwise disjoint, jointly all seven extended policies; task tools closed; uuid8s independent (tools unchanged).
- Trees: task 0 two prerequisites / two value_input edges, task 1 three / three; owner=user root in each; difficulty graph two disjoint acyclic chains.
- Factors: 4-6 per computation, >=2 parameter and >=1 method each, multi-source and cross-difficulty per task, every ladder >=3 distinct tiers stated in its rule; every factor bears weight against an honest baseline, and every whole-baseline figure is definite and differs from gold (per-task factor_weight, matched against factor_sensitivity).
- XF_recipe: all 13 points re-checked on all seven policies — no member open (§ XF_recipe re-check).
- Round-1 REDs CG-1..CG-9, T0-1, T0-2, T1-1..T1-4: all closed; nothing regressed; no new RED. Open observations O-1, O-2, O-3, O-8, O-9 (no demonstrable consequence).
- Gates: round-2 snapshot (`r2/gates.txt`) all OK on the hashed final form; not re-run by the auditor.

VERDICT revision_2: task0=PASS task1=PASS charter=CLEAN

## revision_3

## charter_global_frozen (revision_3)
- Freeze time: 2026-10-17, before any round-3 GT was read. Auditor: same.
- Entry gate: `tail -1 …/worklog.md` = `REWORK round 3: gates 8/8 green` (only that line read). `/tmp/erl0068_coord/snapshot.sh d2_contract_pricing_claims_and_rebates 3` executed (not read): all seven gate lines OK (`.audit_views/policy/d2_contract_pricing_claims_and_rebates/r3/gates.txt`). Inputs complete.
- Hashes: pricing.extended.yaml `70d9fe4e6f18bfdaffd6475d80fa377d25e79ad26913115a60341387f8d8cc1c` (changed from c19bb902… -> charter-global sections re-derived); task_tools.py `063dbb2a…7efeb96` (unchanged -> § action_binding_and_uuids carried forward on that ground); r3/task0.view.json `0e76b34b8d54e87966496ed50292d04c01cb48082e1ad9f4014949f0e3e20257` and r3/task1.view.json `4d55979cc84f94841b0752a7ebf7eb46db143f5c8ed3560f6c49880770c45cbc` — byte-identical to the r2 views, so the worlds and personas are unchanged.
- Additional input read in full: `audits/render_source/d2_contract_pricing_claims_and_rebates/render_r1.md` (renderer source-scan items F1-F6 against charter c19bb902…). It carries rule/compute quotations only, no scored value.
- contamination_disclosure: round-1 and round-2 GT of both tasks are known to the auditor from earlier reveals; round-3 derivations rest on the r3 charter and r3 views. A copy of the r3 charter is kept at `/tmp/audit_d2_contract_pricing_claims_and_rebates_0068/r3/charter.yaml` for later diffs.

### changes found (charter r2 -> r3)
- final_rebate_check `result`: minimum now tested on `RND(check_amt, 2)`.
- substitute_claim s11: adds "or covered without any customer payment on it, takes no credit".
- open_claim_decision: new plain binding `new_item_lines = COUNT(pricing_items, sku, change_reason='new_item')`; `in_scope` requires `item_lines == 2 and new_item_lines == 1`; decision sentence now "when the overbilling, which is the claimed quantity times the difference between the billed unit price and that unit price, exceeds …".
- return_clawback s12 and ladder: "one such line or none carries first_return_share".
- discontinued_closeout s1 / `bo_added`: "when the agreement carries an added price line for that item"; substitute_protection s1 / `bo_item_added`: "(one for which the agreement carries an added price line)"; protection s7 and ladder: "the product of gap_share and the difference", "otherwise, or where the substitute has no regular shipment, it is the ending price".
- termination_forfeiture unchanged; all factor sets, effects, params and prerequisite edges unchanged.

### F1-F6 verification (each as a class across all seven policies)
| item | class | r3 status | class sweep (all seven policies) | covered earlier? |
|---|---|---|---|---|
| F1 | XF7 — rounding placement against a threshold test | closed: `RND(check_amt,2) >= min`, matching "floor, then rounding, then minimum" | no other threshold is tested after a rounding the rule orders: clawback cap/floor precede the single RND (rule s7, s13); forfeiture floor precedes RND; open claim's outcome is not computed and compares against the rounded price; close-out/protection carry no post-rounding test; claim floor is on the per-unit difference | **No.** I noticed the unrounded minimum test while working revision_2 and dismissed it as negligible without recording it. This was a miss: XF7 is a recipe class. |
| F2 | XF9 — a case the compute's else-branch assigns that no rule tier names | closed: s11 names "covered without any customer payment" | every fall-through of all 35 ladders names its residual case in the rule ("every other reason", "fewer", "none", "neither", "a lower share, or no credit limit on record", "any other reason, a settled return or no authorized return", "less, or an agreement with no commitment", "in every other case", "otherwise, or where the substitute has no regular shipment", "an earlier termination", "no remaining month", "any other invoice") | **No.** |
| F3 | XF10 — scope the rule states vs scope the compute applies | closed: `new_item_lines == 1` with `item_lines == 2` | scope checks re-matched rule-to-compute for all seven `in_scope` bindings (clawback, forfeiture, final check, open claim, close-out, protection, claim): every stated condition computed, every computed condition stated | **Partly.** Revision_1 CG-9 recorded the unstated `change_reason='new_item'` filter. Revision_2 judged CG-9 closed by "(its new-item line)" without re-checking that `item_lines == 2` let a non-new-item adding line through. Miss. |
| F4 | XF9/XF2 — arithmetic wording with two groupings | closed: "the claimed quantity times the difference between …" | other mixed times/less/plus phrasings re-read: protection s7 now "the ending price plus the product of gap_share and the difference"; settlement "one plus the tax rate less the discount rate" (both groupings equal); notice "calendar days … less the tier's … days" (single reading); sliding relief and open-return figures are pure products; the claim's base restatement keeps base punctuation (verbatim base) | **No.** |
| F5 | XF9 — zero-count branch the rule leaves without a tier | closed: "one such line or none" | every count ladder starting at "one" names its zero case: reserve ("anything less"), terms / returned payments / load / stranded / adoption / prompt payment / repeat claims ("none") | **No.** |
| F6 | XF10 — scope the rule states vs scope the compute applies (latent) | closed: `bo_added >= 1` (close-out) and `bo_item_added >= 1` (protection) | swept with F3 above | **No.** I noted the missing contract-item check while working revision_1 and judged it harmless without recording it. Miss. |

### re-derived charter-global checks (revision_3)
- XF6 sweep (`scripts/sweep.py`): every compute_basis quote verbatim, every baseline sentence in its rule, every policy_source verbatim; the three new bindings carry verbatim quotes. No factor reads another factor's binding; the new bindings are plain scope bindings used only by `in_scope`; single-factor plain bindings remain the baseline fall-through quantities only.
- XF recipe, every point, every policy: 1, 2, 3, 4, 5, 6, 8, 11, 12 clean (unchanged content or re-swept as above); 7 clean (F1 class closed); 9 clean (F2, F4, F5 classes closed; conventions sentences unchanged); 10 clean (F3, F6 class closed); 13 — worlds unchanged since r2, re-check of revision_2 stands.
- Prerequisite graph and sentences unchanged; the new close-out / protection scope conditions do not alter any waited-on state or its single resolving write. Override declarations unchanged. Factor ladders: only the frequency tier text ("or none") and the protection method wording changed; counts and bounds as revision_2.

### findings (revision_3)
- No open charter RED. F1-F6 closed as classes; round-2 status (no RED) not regressed. Observations O-1, O-2, O-3, O-8, O-9 carried unchanged.

## closing_checklist (revision_3)
Written after both revision_3 derivations were frozen and both round-3 reveals compared (2026-10-17).
- Files `0.md`, `1.md`, `_difficulty.md` each carry revision_1, revision_2 and revision_3; earlier text untouched; both revision_3 comparisons PASS on all four relationships.
- Scopes, trees, owner=user roots, acyclic graph, factor counts and weights, honest baselines: as the revision_2 checklist, re-confirmed on the r3 charter (no edge, factor, param or tool changed; worlds identical to r2).
- Renderer items F1-F6 closed as classes (§ F1-F6 verification). Earlier coverage: none of F1, F2, F4, F5 or F6 was recorded in revision_1 or revision_2, and F3 was only partly covered (CG-9's filter member). F1 and F6 were noticed in working and dismissed unrecorded — audit misses.
- XF_recipe: all 13 points clean on all seven policies; no open member of any class.
- Gates: round-3 snapshot (`r3/gates.txt`) all OK on the hashed final form; not re-run by the auditor.

VERDICT revision_3: task0=PASS task1=PASS charter=CLEAN

## revision_4

## charter_global_frozen (revision_4)
- Freeze time: 2026-10-18, before any round-4 GT and before reading the KB verdict file. Auditor: same.
- Entry gate: `tail -1 …/worklog.md` = `REWORK round 4: gates 8/8 green`. `/tmp/erl0068_coord/snapshot.sh d2_contract_pricing_claims_and_rebates 4` executed (not read): all seven gate lines OK (`r4/gates.txt`).
- Hashes: pricing.extended.yaml `70d9fe4e6f18bfdaffd6475d80fa377d25e79ad26913115a60341387f8d8cc1c` and task_tools.py `063dbb2aa6bc4517c78e58187d79247d1a0f936e9341492e3ce2220037efeb96` — both unchanged since revision_3, so every charter-global section (incl. the XF_recipe re-check and F1-F6 verification) is carried forward by reference to `## revision_3` on these two hashes. r4/task0.view.json `6e4f4d31a7f0e664546e8e8dee04683201e18f3a75533138fd2188f7947465a3`, r4/task1.view.json `a9e5199b38d06cf0393c13cbc98f6eac2bf4873b399b7ef0acef2dced069f9ca` (both changed: seed-only rework).
- Additional read domain this round (coordinator-directed): published product KB under `docs/credit/` (prompt_payment_cash_discount_terms, contract_pricing_tier_and_discount_rate, disputed_and_returned_merchandise_in_discounts) and blueprint vmi/vending/credit charters for seed producibility.
- contamination_disclosure: round-1..3 GT known to the auditor; no round-4 GT seen before the per-task freezes.

### seed-row producibility (cross-product rows changed or added in r4)
- Task 0 credit: INV-2250930 now part-paid 408,020.00 on 2025-11-24 and the 21,480.00 rest paid 2026-01-08. So FC-2251231 = 1% x 21,480.00 = 214.80 (Net 60 Corporate: 1.0%/month, 15-day grace; due 2025-11-29, so the balance is eligible at 2025-12-31 and not at 2025-11-30). FC-2251231 was paid by check 2026-02-24 and returned 2026-03-02 (RTN-2260302), with one $25 returned-payment fee (RPF-2260302); both were re-paid by wire on 2026-03-06. Payments within the 3 certified-funds months after the return are all wires (03-27, 04-24, 05-26). No finance charge accrues on a finance charge. INV-2260131 is now paid by wire on 2026-03-27 with no return. No cash discounts (Strategic tier excluded). Producible.
- Task 0 VMI: program now StockSmart Monthly Service, go-live 2023-05-19 (13 business days after enrolment; limit 15), 76 bins set at go-live (entry gate >= 75). One scheduled visit a month, Sep 2025 - Sep 2026; each visit's three deliveries billed the same day; freight included. Monthly spend 2055.18-2102.32 is >= the 2000.00 minimum, so no minimum fee is due in any month, and none for October (month not ended). Producible; no write due on the call day.
- Task 0 vending: Coil 40 (removed 2025-11-14) usage bills 2025-09/10/11 of 1486.20 / 1412.75 / 1318.40 are all >= the 1250.00 minimum (no shortfall fee due), and removal followed the 30-day notice. Producible.
- Task 1 credit: every discount on an invoice dated inside the current Category Contract term (from 2026-02-01) is 3/4 x 1.0% x (merchandise less applied return credits), per published `contract_pricing_tier_and_discount_rate` and `disputed_and_returned_merchandise_in_discounts`; invoices dated before 2026-02-01 keep 1.0% of merchandise. All 12 invoices recompute exactly (e.g. INV-2260930: (13099.80 − 1306.26) x 0.75% = 88.45; INV-2260430: (6904.70 − 612.00) x 0.75% = 47.20). Each is paid in full within 10 days (amount − memo − discount). Producible.
- Task 1 VMI: Monthly Service, go-live 2024-05-24 (14 business days), 76 bins, monthly spend 2091.63-2116.67 >= 2000.00. Replenishment lines are priced at the agreement's contract prices (FS-20118 0.395, SP-22140 4.98, JN-23127 9.05). No fee due. Producible.
- Task 1 vending: Locker 12 installed_date now 2023-02-24 (requested 2023-02-13); removed after its 30-day notice. Producible.
- No added row lights a state_due obligation either task fails to carry: no unbilled delivery, no unassessed fee, no unpaid invoice, no open dispute.

### findings (revision_4, charter level)
- No open charter RED (charter unchanged). New observation O-10: the substitute claim's settlement multiplier takes "its discount rate being the prompt-payment cash discount earned on it over its merchandise subtotal". Under the published credit KB the discount is now earned on merchandise less return credits, so this average rate (88.45 / 13099.80 = 0.675%) is below the 0.75% the claimed units actually earned. The rule is explicit (one reading) and an average-rate convention is a plausible published simplification. On task 1 it moves the claim by 1.17 (1732.79 by the rule vs 1731.62 at the units' own rate). Recorded for the coordinator; not demonstrable as a treatment no distributor publishes.

### KB re-judge items SRC-1..SRC-4 (read after both freezes; `audits/policy_kb/d2_contract_pricing_claims_and_rebates/_verdict.md`)
| item | r4 status | earlier policy-task coverage |
|---|---|---|
| SRC-1 task 1 discounts vs published credit catch-up rule | closed (all 12 invoices recompute; payments cover) | not covered — I checked the discounts against the base credit charter only, not d1's published extended rule |
| SRC-2 task 0 receivable over credit limit Nov-Dec 2025 | closed (peak 890,834.80 <= 1,000,000.00; no hold trigger reached) | not covered — I checked the current receivable and finance-charge legality, not the receivable history against the limit |
| SRC-3 StockSmart go-live business days (both tasks) | closed (13 and 14 vs 15) | not covered |
| SRC-4 VendPoint installation lead (task 1) | closed (<= 9 vs 10) | not covered |

## closing_checklist (revision_4)
- Files carry revision_1..revision_4; earlier text untouched; both revision_4 comparisons PASS on all four relationships.
- Charter and tools unchanged since revision_3, so scopes, prerequisite graph, factor structure and the XF_recipe re-check carry forward by hash. The new seed rows are producible by their owning products' published rules; none leaves a write due on the call day; personas still match; both trees and all 35 factors bear weight on the r4 worlds; scored values match gold (task 1's claim moved 1727.71 -> 1732.79 through the seeded discount).
- Gates: round-4 snapshot all OK; not re-run by the auditor.
- Open observations: O-1, O-2, O-3, O-8, O-9, O-10.

VERDICT revision_4: task0=PASS task1=PASS charter=CLEAN
