# Policy-task audit — installment_billing_and_fees / charter-global

## revision_1

## charter_global_frozen
- Frozen 2026-10-18T10:47Z, before any task's GT was revealed. Auditor: independent policy-task auditor (erl-task-policy-audit), not the instantiator.
- Hashes (match the coordinator brief):
  - `tasks/installment_billing_and_fees/billing.extended.yaml` sha256 71df1baa760af38b03bbffeda817b8cd94e2543dcde7080618c34e2d23c3d22a
  - `tasks/installment_billing_and_fees/task_tools.py` sha256 ca447e3c410ff6bc247d2bde80f3c9d731d9d57adccfa72ac5e7a09f6b793731
  - masked views `.audit_views/policy/installment_billing_and_fees/r1/0.masked.json` 863fb313…a01f0, `1.masked.json` 966e060e…a5562 (both re-hashed and matching)
- Read: `blueprint/blueprint.yaml`, `blueprint/db_schema.json`, `blueprint/share_tools.py`, `blueprint/products/billing.yaml`, `blueprint/products/auto.yaml` (the only cross category read), the extended charter, `task_tools.py`, `audits/render_source/XF_recipe.md`, the DSL primitives in `skills/erl-task-instantiate/scripts/check_compute.py` (RND/LATEST/XLATEST/MONTHS/DAYS/within_months semantics), the masked views.
- Masked, not read before the per-task freezes: `tasks/*.json` (evaluation_criteria, computations, charter_scope, required_documents, design_rationale, solvability_contract, prerequisite_closure, db_closure), `plan.md`, both `worklog.md` files, any earlier audit.
- Entry conditions: the gate snapshot came with the brief (`/tmp/erl0071_coord/snap_installment_billing_and_fees_r1.txt`, seven gates rc=0) and the masked views with hashes. Complete.
- Base copy: lines 1-2076 of the extended charter are byte-identical to `blueprint/products/billing.yaml` (`diff` empty).

### policy_conflict_scan
Extended policies (5): `billing_ext_draft_notice` (issue_draft_notice_1682239d, minimum_due, state_due, agent), `billing_ext_endorsement_deposit` (authorize_endorsement_deposit_3483f9bd, amount, on_request, user), `billing_ext_returned_item_fee` (charge_returned_item_fee_652d204f, fee_amount, state_due, agent), `billing_ext_late_fee_schedule` (assess_late_fee_1fdc5cae, fee_amount, state_due, agent), `billing_ext_returned_draft_makeup` (authorize_makeup_payment_1af63ac0, amount, on_request, user).
- Subjects: draft notice = billing_installment_billed (+ its billing_installment_fee row); deposit and makeup both = billing_payment_received but on disjoint triggers (a payment toward an endorsement's additional premium vs a payment making good a returned automatic draft); returned-item fee = billing_nsf_fee; late fee = billing_late_fee. No two policies write the same quantity for the same object.
- Sibling overwrites of `billing_payment_posting` "The customer personally authorizes each one-time payment…" (deposit and makeup) each exclude the other's case by name. Compatible.
- Conflicts found: deposit application vs draft-notice carried amount on every later notice (finding CG-2); makeup's two state gates vs the object selection of the two fee policies (CG-7); draft notice vs base installment-schedule sentence (CG-1, see override_declarations).
- Cross-category boundary: every cross read is `auto` (CFIELD on `auto_policies` keyed `auto_policy_id=F('auto_policy_id')`, XSUM/XLATEST on `auto_premium_transactions` / `auto_policy_changes` keyed by the same id). Read-only; no tool writes an auto row.
- Scope partition (pre-reveal, from the prerequisite graph alone): two components, {deposit -> draft notice} and {makeup -> returned-item fee, makeup -> late fee}. If task 0 claims the first and task 1 the second, the scopes are disjoint and jointly cover all five policies. Confirmed or refuted only in the post-reveal section.

### rule_compute_equivalence
- Sweep (scratch script, `/tmp/audit_installment_billing_and_fees_0071/`): every `compute_basis` quotation of all five policies is verbatim in its own `rule`; every sentence of each `baseline.rule` is in its `rule`; every `replaced_by` is in its `rule`. No compute binding without a quotation.
- Windows/filters: `within_months=12, date_field='posted_date'` = "fewer than twelve whole calendar months separate its posting date from the notice date" (MONTHS(posted, today) in [0,12); the tool dates the notice today). DAYS bounds: deposit window "the expiration date counted, the change date not" = DAYS(change, expiration); returned-item / makeup "the effective date not counted" = DAYS(effective, return posted). Equal.
- Rounding: every rule rounding sentence matches its RND placement (draft: down payment, scheduled premium, shares, minimum due; deposit: standard pct, core share, total once; returned-item: FL/GA pct, total once; late fee: core pct, total once, floor at 0; makeup: total once). Extra RNDs on sums of cents are no-ops. Observation O-1: the DSL's RND is Python `round` on floats, not half-up; no scored value of either world lands on a half cent (checked), so no consequence here.
- Tie rules: deposit XLATEST "of two added on the same date, the one recorded first", returned-item / makeup LATEST "of two … the same day, the one recorded first" match the strict `>` keep-first of LATEST/XLATEST. Late fee has none (CG-5).
- Rule-words vs compute mismatches: CG-6. Dead binding: `dep_unbilled` (deposit) is computed and never read; the quantity it names is used only through the factor binding `collect_unbilled` (CG-3).

### action_binding_and_uuids
- `(target_tool, computes)`: (issue_draft_notice_1682239d, minimum_due), (authorize_endorsement_deposit_3483f9bd, amount), (charge_returned_item_fee_652d204f, fee_amount), (assess_late_fee_1fdc5cae, fee_amount), (authorize_makeup_payment_1af63ac0, amount): each claimed once.
- uuid8s 1682239d, 3483f9bd, 652d204f, 1fdc5cae, 1af63ac0: no shared prefix/suffix run, no sequence, none reused in `share_tools.py` or the blueprint. Independent.
- Bodies: each tool only creates its row(s) and moves `account_balance`; none refuses, errors or hints on an unresolved prerequisite. Docstrings: no ordering word across tools ("after" occurs only in "account balance after the fee/payment"), no other tool named, no example values; every claimed effect is in the body (deposit: `source_auto_txn_id` set, `related_invoice_id=None`; makeup: linked to the invoice; draft notice: invoice + matching fee row).
- XF14 trigger rule: events written are billing_installment_billed (base trigger -> billing_installment_fee, same category; the tool writes that row itself), billing_installment_fee, billing_payment_received, billing_nsf_fee, billing_late_fee (no triggers). None lands in another category.
- XF15: no factor id is a substring of any tool name (scripted check).

### prerequisite_graph
- `prerequisite` filled on all five ([] on draft notice, returned-item fee, late fee). Edges: deposit -> draft_notice (value_input, gate `dep_endorsement_billed`, state); makeup -> returned_item_fee (value_input, gate `mk_nsf_due`, state); makeup -> late_fee_schedule (value_input, gate `mk_late_due`, state). Every `problem` is an extended id of this file, never base, never self. Acyclic.
- Each `policy_source` is verbatim in its own rule (scripted). `form: state` on all three, no `fallback_reason` (correct). `kind` value_input and each `gate` is a real binding of the blocked compute. `resolved_by` = the depended-on policy's `target_tool` and its write moves the gate binding (premium billed on invoices for the deposit; nsf/late fee rows for the makeup). `condition` texts restate the sentences at the same strength. No authoring-viewpoint wording.

### prerequisite_sentences
1. Deposit: "The endorsement deposit is fixed only after every draft notice whose issue date has arrived stands on the plan." Ordering connective "only after"; waited-on state = a record-visible invoice per installment whose issue date (due date less invoice_lead_days, base installment schedule) has arrived; no tool/id/snake token; strength = condition. Only `issue_draft_notice_1682239d` creates installment invoices. Derivation: due day + base schedule give the issue date; a missing invoice whose issue date has arrived is the gap; the draft-notice rule is the only rule describing that invoice's content; single reading. PASS.
2. Makeup: "A makeup payment for a returned automatic draft is not taken until the plan's ledger carries a returned-item fee entry for every returned payment on it whose return reason is one that carries a returned-item fee." Connective "not … until"; state = a fee row per NSF-coded return; only `charge_returned_item_fee_652d204f` writes billing_nsf_fee rows. PASS as a sentence; the object coverage gap is CG-7.
3. Makeup: "The makeup amount is fixed only after every installment invoice on the plan whose minimum due stayed unpaid past the end of its grace period carries a late fee entry." Connective "only after"; state = a late-fee row per late invoice; only `assess_late_fee_1fdc5cae` writes it. PASS as a sentence; coverage gap CG-7.
- Depended-on rules do not restate the sentences; no rule carries a second wording, a tool name or another problem's id. No undeclared cross-problem order found in any rule. Observation O-2: base `events` declare `billing_payment_returned` triggers `billing:billing_nsf_fee` on the return's posted_date; the extended returned-item fee is a `state_due` agent write. The runtime does not fire triggers, and the instantiation convention seeds state_due debts as owed, so this is not a second producer at runtime; but a reader of the base event model would expect the fee to stand from the return date.

### override_declarations
Sentence-by-sentence against each `base_policy_refs` entry.
- draft notice vs `billing_installment_fee_rule`: S1 "Each installment invoice carries the plan's installment_fee…" -> overwritten, declared, replaced_by restates the out-of-scope case (XF5a ok). S2 one fee per invoice, S3 no fee on down payment/final/renewal/no-installment/avoided, S4 plan-switch fee: followed.
- draft notice vs `billing_installment_schedule`: S1 equal split, final absorbs: followed. S2 due dates: followed. **S3 "Each invoice is issued invoice_lead_days calendar days before its due date and bills the installment premium, the plan's installment fee and every past-due amount still unpaid; its minimum_due is their sum." handled differently and not named in `overwrite`**: the extended notice bills scheduled premium + an endorsement share + adjusted fee + "the amount carried" (account balance less every unbilled premium). The rule's own sentence "a plan billing a Named Non-Owner Policy term is outside it and its invoices follow the base installment schedule unchanged" shows the author knows owner-term notices depart from that schedule. -> CG-1. S4 one invoice per installment, S5 credits nearest first, S6 PIF: followed.
- deposit vs `billing_payment_posting`: application-order sentence and authorization sentence overwritten and declared (restating out-of-scope cases, naming own scope). Single-payment cap, posting day, partial payments, personal check, agent-assisted fee sentences: inherited unchanged. vs `billing_agg_returned_payments`: all sentences inherited.
- returned-item fee vs `billing_returned_payments`: "The NSF fee is the plan's nsf_fee; returns coded bank_error or unauthorized_debit carry no fee." overwritten and declared; the other sentences (reversal, one fee per return, autopay revocation, returned down payment) inherited.
- late fee vs `billing_late_fee_rule`: `overwrite: []`. The base rule has no amount sentence (only grace, counting, max per invoice, timeliness, exclusions), so no sentence is departed from. Observation O-3: the base `parameter_schema` meaning of `late_fee` ("Late fee for an installment not paid in full within the grace period") is changed in effect by the core/credit/addition schedules; it is a parameter meaning, not a policy sentence.
- makeup vs `billing_payment_posting`: authorization sentence overwritten and declared (sibling-exclusive); application order followed ("applied in payment_application_order"). vs `billing_agg_returned_payments`: inherited.

### factor_ladders
Per policy: factor (effect; decides; tiers; multi-source?; cross_difficulty). All ladders have 3 pairwise-disjoint tiers, every tier stated in the rule and branched in compute, fall-through = baseline, no two tiers of a ladder share a value/method (checked value by value).
- draft notice (5; 4 parameter, 1 method): endorsement_spread (method; endorsement_share; MS yes: unbilled balance AND unbilled count; auto), state_fee_schedule (parameter; auto), autopay_fee_standing (parameter; MS yes: authorizations AND returns; billing), package_fee_tier (parameter; auto), violation_points_fee (parameter; auto).
- deposit (6; 5 parameter, 1 method): deposit_core_by_installments_left (method; MS yes; billing), added_driver_age_addition, added_driver_points_addition, endorsement_size_addition, coverage_window_addition, household_relationship_addition (parameter; all auto).
- returned-item fee (4; 3 parameter, 1 method): state_returned_item_base (method; auto), returned_channel_addition, return_reason_addition (parameter; billing), new_business_return_addition (parameter; MS yes: first term AND days; auto).
- late fee (5; 4 parameter, 1 method): unpaid_amount_core (method; billing), returned_draft_late_credit (parameter; MS yes; billing), state_late_addition, package_late_addition, points_late_addition (parameter; auto).
- makeup (5; 4 parameter, 1 method): undraftable_account_advance (method; MS yes: reason AND next invoice; billing), package_makeup_advance, points_makeup_advance, new_business_makeup_advance (MS yes), state_makeup_advance (parameter; auto).
- Factor independence (XF1, mechanical): no factor binding reads another factor's binding. Factor-only quantities defined by the baseline or as plain bindings: CG-3.

All-pairs method-shape table (XF10; aggregates of one field count as one input, constant multipliers ignored):

| method factor | tiers | pair | verdict | distinguishing input/operation |
| --- | --- | --- | --- | --- |
| endorsement_spread | T1 E/n (n>=2, data), T2 E, T3 0 (E<=0) | T1-T2 | PASS | data-selected divisor n (unbilled count) |
| | | T1-T3 | PASS | T3 constant zero, T1 never 0 on its domain |
| | | T2-T3 | PASS | conditional pick (clamp at 0); T2 non-zero on its domain |
| deposit_core_by_installments_left | T1 B, T2 B/n with n==2 exactly, T3 min(B, max(RND(pct·B), min_deposit)) | T1-T2 | **FAIL** | none: n is fixed at 2 on T2's domain, so T2 = 0.5·B, a constant multiple of T1's B |
| | | T1-T3 | PASS | floor and cap |
| | | T2-T3 | PASS | floor and cap |
| state_returned_item_base | T1 max(band(A), RND(5%·A)), T2 max(30, RND(5%·A)), T3 nsf_fee | T1-T2 | PASS | banded selection on A |
| | | T1-T3, T2-T3 | PASS | input A and max |
| unpaid_amount_core | T1 RND(10%·U), T2 min(late_fee, RND(4%·U)), T3 late_fee | T1-T2 | PASS | min with tariff late_fee |
| | | T1-T3, T2-T3 | PASS | T3 drops U |
| undraftable_account_advance | T1 next scheduled premium S, T2 next invoice min due less payments M, T3 0 | all | PASS | different inputs (schedule vs invoice ledger); T3 is 0, neither T1 nor T2 is 0 across its domain |

-> CG-8.

Realism per tier (XF16; the line of business is a nonstandard auto carrier's billing):
- Real or honest company schedule: state-filed installment-fee and late-fee differences by state; EFT/autopay installment-fee discount; endorsement premium spread over remaining installments (small balances billed whole); late fee as a percentage of a small unpaid amount, capped at the flat fee; FL banded returned-item charge (Fla. Stat. 68.065 / 832.08(5): $25 up to $50, $30 up to $300, $40 above, or 5% if greater) and GA greater-of $30 or 5% (O.C.G.A. 13-6-15) as statutory maxima; collecting the next installment when the drafted account is closed or stopped; endorsement deposit tiers on the added driver's risk (down payment by risk tier is common practice).
- Not real: CG-10 (violation-points-keyed billing service fees; state-keyed percentage advance on a makeup), CG-11 (company add-ons stacked on top of the FL/GA statutory maximum), CG-12 (endorsement deposit can exceed the endorsement premium it is a deposit on).
- Observations, not RED: O-4 package-keyed installment/late fees and package/points makeup advances (nonstandard carriers file limits programs with their own fee schedules; doubtful but defensible). O-5 `returned_autopay_increase` (+$1 above the standard fee for an autopay plan with a return) is unusual; carriers usually just drop the EFT discount. O-6 late-fee credit for a returned NSF draft is unusual but reads as an anti-pyramiding schedule.

### findings
Each names the tasks whose files demonstrate the consequence (task 0 = deposit tree, task 1 = makeup tree, per the pre-reveal partition).

- **CG-1 SOURCE-POLICY RED: undeclared override of billing_installment_schedule S3.** Symptom: two in-force clauses settle the draft notice's minimum due. Root cause: `billing_ext_draft_notice` lists `billing_installment_schedule` in `base_policy_refs` but its `overwrite` names only the fee sentence of `billing_installment_fee_rule`. Evidence: base "Each invoice … bills the installment premium, the plan's installment fee and every past-due amount still unpaid; its minimum_due is their sum."; extended "The draft notice bills the scheduled premium of its installment, the plan's installment_fee and the amount carried … Endorsement premium on a draft notice: … the notice adds to its premium an equal share of it …". Consequence: shown on task 0. Artifact: extended yaml `billing_ext_draft_notice.overwrite`.
- **CG-2 SOURCE-POLICY RED: deposit application vs the draft notice's amount carried.** Deposit rule: "an endorsement deposit … is applied to the endorsement premium not yet billed on a draft notice, reducing the unbilled installments nearest first". Draft-notice rule: the endorsement premium not yet billed is "every additional premium transaction booked on the owner term billed, less the endorsement premium already billed" (no deposit subtracted), and "The amount carried is the plan's account_balance less the premium not yet billed …; … negative when the plan holds a credit." After any deposit the next notice still bills its full endorsement share and takes the deposit as a carried credit, while the deposit rule has the deposit cover that share first. Probe on task 0's post-deposit world (notice 3 drafted 12-19, notice 4 on 2027-01-09): draft-notice compute 206.90; deposit rule's application gives 251.76 (premium 247.01 + fee 4.75, share 74.77 fully covered). Bears on task 0 downstream, not on its scored writes.
- **CG-3 SOURCE-POLICY RED (XF1): the baseline or a plain binding defines quantities only factors use.** Deposit: baseline.rule "The deposit counts the installments still unbilled …" -> `dep_unbilled` is dead, only factor binding `collect_unbilled` uses the count. Returned-item fee: baseline.rule "its returned amount is the total returned against that original payment" -> `fee_returned_amount` is read only by `state_fee_base`. Late fee: baseline.rule "The unpaid amount of that invoice is …" -> `core_unpaid` (a factor binding) and `late_last_payment` exist only for `unpaid_amount_core`; the standard late fee is the flat late_fee. Makeup: "The next installment's scheduled premium is …" -> `mk_next_sched`, `mk_first_term`, `mk_down_premium`, `mk_sched` feed only `advance_core` and the four percentage factors; under all baselines the term contributes 0. Bears on tasks 0 and 1.
- **CG-4 SOURCE-POLICY RED (XF2): combination sentences name factor quantities and factor order.** Deposit "the first replaces how the deposit's core amount is figured, and each of the others adds its own percentage of the endorsement balance"; returned-item "the first replaces how the fee's state base is figured, each of the others adds its own amount"; late fee "the first replaces how the fee's core is figured, each of the others adds or subtracts its own amount"; makeup "the first adds an advance whose method it sets, each of the others adds its own percentage of the next installment's scheduled premium". "core amount", "state base", "core", "advance", "percentage of …" are factor quantities, and "the first" has no referent once each factor is its own document. Draft notice's sentence names only standard parts (premium billed, installment fee): not a member. Bears on 0 and 1.
- **CG-5 SOURCE-POLICY RED (XF8): month-end convention and same-day tie not stated.** Month-end: draft notice "fewer than twelve whole calendar months separate its posting date from the notice date" and deposit "Age is counted in whole calendar months from the driver's date of birth to the change effective date" state no month-end convention, while MONTHS() counts 2026-01-31 -> 2027-02-28 as 12 (not counted) and DOB 2005-08-31 -> change 2026-02-28 as 245. Tie: late fee "the payment most recently posted against it" and "the installment invoice most recently issued on the plan (by invoice date)" state no same-day rule though LATEST keeps the first recorded. Bears on 0 (draft, deposit) and 1 (late fee).
- **CG-6 SOURCE-POLICY RED (XF9/XF11): rule words differ from compute on real domain cases.** Late fee is not scoped to owner terms, yet its state ladder lists only owner terms "garaged in" the six states, and its package and points ladders only "the owner term billed"; a plan billing a Named Non-Owner Policy term is priced 0 by compute and by no rule sentence. Returned-item new-business addition: "when the owner term billed is the first term …; on a renewal term nothing is added", silent for a non-owner plan (compute 0). Returned-item channel: "a paper item sent by mail or left at an agent office" vs compute keyed on channel only (`mail`/`agent_office`), so a returned debit-card or bank payment made at an agent office gets paper_return_add under compute and no clear tier under the words. Bears on 1.
- **CG-7 SOURCE-POLICY RED: the makeup's gates demand fee entries the fee policies cannot price.** Makeup: "… a returned-item fee entry for every returned payment on it whose return reason is one that carries a returned-item fee" and "… every installment invoice on the plan whose minimum due stayed unpaid past the end of its grace period carries a late fee entry". Returned-item fee: "The fee is figured for the returned payment most recently posted on the plan"; late fee: "figured for the installment invoice most recently issued on the plan (by invoice date) when it is the invoice the late fee rule makes late". On a plan whose earlier NSF-coded return has no fee row and whose latest return is bank_error, or whose earlier late invoice has no late fee while a later invoice has been issued, no policy prices the required entry, so the makeup can never be taken (no solution). Not present in task 1's world (one return, latest invoice is the late one); charter defect only.
- **CG-8 SOURCE-FACTOR RED (XF10): deposit_core_by_installments_left fails the method-shape pair test T1-T2** (table above). Without it the deposit computation has 0 method factors (< 1). Bears on task 0.
- **CG-9 SOURCE-FACTOR RED: incoherent makeup baseline.** `baseline.params` = installment_count, down_payment_pct_new_business, down_payment_pct_renewal; `baseline.rule` ("The returned draft is … The standard makeup payment is the returned installment still owed plus the fees owed with it") uses none of them. The keys are those of the factor-only next-installment premium (CG-3). Bears on task 1.
- **CG-10 SOURCE-FACTOR RED (realism): tiers a nonstandard auto carrier does not weigh for that quantity.** (a) violation_points_fee (installment fee +0.75/+1.50 by the term's violation points) and points_late_addition (late fee +0.50/+1.00 by points): installment and late fees are filed billing service charges, set by plan, payment method and state; driving record is rated in premium, never in a billing service charge. (b) state_makeup_advance (2.5% / 1.5% / 0 of the next installment's premium by garaging state, grouped FL+GA / TX+OH / VA+AZ): no statute in the six states asks for this, and no carrier publishes a state-keyed prepayment on a returned-draft makeup. Bears on 0 (a: draft notice) and 1 (a: late fee; b).
- **CG-11 SOURCE-FACTOR RED (realism): add-ons stacked on the FL/GA statutory maximum.** The FL and GA tiers reproduce the statutory maximum service charge (Fla. Stat. 68.065/832.08(5); O.C.G.A. 13-6-15). The rule then adds draft_return_add, paper_return_add, closed_account_add, stop_payment_add, early_term_add and first_term_add on top, so every FL/GA fee with any addition is above the ceiling the tier copies. Bears on task 1 (demonstrated there).
- **CG-12 SOURCE-FACTOR RED (realism): the endorsement deposit can exceed the endorsement balance.** Standard deposit is "never more than the endorsement balance itself", but the core tier "the core amount is the whole endorsement balance" plus any addition (up to 40% of the balance) gives a deposit above the additional premium it is a deposit toward, e.g. balance 40.00 with an under-21 added driver -> 44.00. The deposit rule applies the deposit "to the endorsement premium not yet billed", and says nothing of the excess. Task 0's world sits on the core T2 tier, where this does not arise. Charter defect.

Observations (not grounds for rework): O-1 RND is not half-up; O-2 base NSF trigger vs state_due; O-3 late_fee parameter meaning; O-4 package-keyed fees/advances and points-keyed advances/deposits; O-5 returned_autopay_increase; O-6 late-fee credit for a returned NSF draft; O-7 the deposit's endorsement balance ignores earlier deposits and reversed additional premium (`reversed_txn_id`), and a zero/negative balance gives a zero/negative deposit with no rule; O-8 lifecycle "An installment is unpaid after its due date" vs `billing_delinquency` "only when … unpaid at the end of its due date" leave a plan whose draft is returned after its due date `current` (`billing_delinquency` decides it).

## closing_checklist
Post-reveal, written after both task files carry a frozen derivation (mtimes 10:49:42Z / 10:50:27Z) and a source_gt_comparison (GT first read 10:50:38Z). The charter-global section above was frozen at 10:48:41Z (sha256 f5655e1ac289db46939f79e6cc11fee620c518be0cec5c00e5c3aa8f0e68b9a8) and is not altered.
- Per-task files: `0.md`, `1.md`, one per task, alongside this file. No earlier revision exists.
- Scope partition confirmed from `charter_scope`: task 0 = {billing_ext_draft_notice, billing_ext_endorsement_deposit} with their two tools; task 1 = {billing_ext_returned_item_fee, billing_ext_late_fee_schedule, billing_ext_returned_draft_makeup} with their three tools. Pairwise disjoint, jointly complete over the five extended policies and five task tools, each tree inside its own task's scope. uuid8s independent.
- Trees: task 0 has 1 prerequisite and 1 value_input edge; task 1 has 2 prerequisites and 2 value_input edges. Each has an owner=user root. The difficulty-wide graph is acyclic.
- Factors: every declared factor bears weight on its world, and all-baseline numbers are definite and differ from gold (253.01 / 29.91 / 25.00 / 10.00 / 259.33). Not closed:
  - CG-8: the deposit has no valid method factor.
  - CG-9: incoherent makeup baseline.
  - CG-10, CG-11, CG-12: realism.
- Policy self-consistency not closed: CG-1..CG-7.
- The difficulty does NOT pass the source-layer audit, so the closing gate re-run is not performed. The gates were green at entry (coordinator snapshot), and that does not change any verdict here.

VERDICT revision_1: task0=RED task1=RED charter=CG-1,CG-2,CG-3,CG-4,CG-5,CG-6,CG-7,CG-8,CG-9,CG-10,CG-11,CG-12

## revision_2

## charter_global_frozen (revision_2)
- Gate: `tail -1 tasks/installment_billing_and_fees/worklog.md` = `REWORK round 2: gates 7/7 green`.
- Entry evidence: `/tmp/erl0071_coord/snapshot.sh installment_billing_and_fees 2`, run 2026-10-19T07:47:42. All seven gates rc=0 (EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK).
- Hashes:
  - views r2/0 9a8cf4eb…c126, r2/1 46d8c108…68ca (re-hashed, match)
  - extended yaml 701572ae…f253
  - task_tools.py c76dc913…affd
- Both shared inputs changed against revision_1 (71df1baa… / ca447e3c…), so every charter-global section below is re-derived in full; nothing is carried forward.
- Frozen before any revision_2 GT field was read. Read: the same blueprint files, the r2 extended charter, task_tools.py, XF_recipe.md (points 1-22), `rework_r2_claims.md` (claims only), the r2 masked views. Masked: tasks/*.json, plan.md, worklog.md beyond its tail line.
- Base copy (lines 1-2076) is byte-identical to `blueprint/products/billing.yaml`.

### policy_conflict_scan (r2)
- Same five policies, tools, subjects and owners. The deposit and makeup application/authorization overwrites remain sibling-exclusive.
- Draft notice credit_carry vs base `billing_installment_schedule` S5 "Credits on the plan reduce the next installments nearest first; an installment fully covered by credit before its invoice date is not invoiced." conflict, not overwritten. -> CG-13.
- Deposit prerequisite "covered in full by the plan's credit" vs credit_carry T1. -> CG-14.
- Late-fee object selection vs any earlier return on the plan. -> CG-15.
- Deposit application ("held on the plan as a credit that reduces the installments not yet invoiced, nearest first") vs the notice's credit_carry agree whenever the credit is smaller than the next scheduled premium. Probe: task-0 world after the deposit -> notice 4 carries the whole 119.63. CG-2's revision_1 contradiction is gone, except in CG-13's case.

### rule_compute_equivalence (r2)
- Scripted sweep: every compute_basis quote, baseline sentence and replaced_by is verbatim in its own rule. Every superseded_clause is verbatim in its base rule. No unused binding.
- Rounding sentences match RND placement in all five.
- Month-end sentence ("A whole calendar month is complete only when the later date's day number is at least the earlier date's day number …") is present in the draft notice and the deposit and matches MONTHS().
- Same-day ties are stated for every LATEST/XLATEST: returned payment, late invoice and payment, driver addition.
- Non-owner outcomes are stated on every owner-keyed ladder of the late fee and the returned-item fee. The channel ladder uses the exact payment_channel values.

### action_binding_and_uuids (r2)
- Same five `(target_tool, computes)` pairs, each claimed once. uuid8s unchanged and independent.
- Bodies only create rows and move account_balance; no prerequisite is judged. No ordering word, no example value. The makeup docstring now reads "makes good a payment the bank returned", matching the widened rule.
- XF14: events written unchanged, no cross-category trigger. XF15: no factor id is a substring of any tool name.

### prerequisite_graph (r2)
- Edges unchanged in shape: deposit -> draft_notice (value_input, dep_endorsement_billed); makeup -> returned_item_fee (mk_nsf_due); makeup -> late_fee_schedule (mk_late_due). All state form, verbatim in their own rules, acyclic.
- `condition` texts restate the new sentences at the same strength. resolved_by / effect are correct.

### prerequisite_sentences (r2)
1. Deposit: "The endorsement deposit is fixed only after every installment whose invoice date has arrived is invoiced on the plan or covered in full by the plan's credit." Connective, state form and no tool: PASS. "Covered in full" admits two readings against the notice's credit_carry -> CG-14.
2. Makeup: "A makeup payment is not taken until the plan's ledger carries a returned-item fee entry for the returned payment it makes good whenever that payment's return reason is one that carries a returned-item fee." The returned-item fee prices exactly that payment (most recent return). PASS. Revision_1 CG-7 half closed.
3. Makeup: "The makeup amount is fixed only after the installment invoice the returned payment had paid carries a late fee entry whenever that invoice's minimum due stayed unpaid past the end of its grace period." The late fee prices exactly that invoice while a return stands. PASS for the makeup. Revision_1 CG-7 half closed. XF20: late fee floored at late_fee_min and returned-item fee > 0, so no zero-amount wait.

### override_declarations (r2)
- Draft notice: S3 of `billing_installment_schedule` is now overwritten (replaced_by restates the out-of-scope invoice). Revision_1 CG-1 closed. The fee sentence is overwritten as before. **S5 is not overwritten, yet credit_carry departs from it (CG-13).**
- Deposit, makeup, returned-item fee: overwrites as listed; remaining base sentences inherited.
- Late fee: `overwrite: []`; no base amount sentence (O-3 unchanged).

### factor_ladders (r2)
- draft notice (5): endorsement_spread (method, auto), credit_carry (method), autopay_fee_standing (parameter, MS), package_fee_tier (parameter, auto), installment_size_charge (method).
- deposit (6): deposit_by_installments_left (method, MS), age, points, size, window, relationship additions (parameter, auto).
- returned-item fee (5): returned_amount_charge (method, MS: state AND amount), channel, reason (parameter), new_business_return_addition (parameter, MS, auto), package_returned_item_addition (parameter, auto).
- late fee (4): unpaid_amount_core (method), returned_payment_late_credit (parameter, MS), package_late_addition (parameter, auto), new_business_late_addition (parameter, MS, auto).
- makeup (5): returned_payment_recollection (method), undraftable_account_advance (method, MS), package_makeup_advance, new_business_makeup_advance, points_makeup_advance (parameter, auto).
- Every ladder has 3 disjoint tiers stated in the rule and branched in compute. Fall-through = baseline. No two tiers share a value except credit_carry (below). No factor reads another factor's binding (scripted).
- XF1 residual: the makeup's `mk_next_sched` (with mk_first_term / mk_down_premium / mk_sched) is a quantity, not a record selection, read only by advance_core and the three percentage factors; under all baselines it contributes 0. The late fee's `late_last_payment` and `late_invoice` are shared record selections, which is allowed. Deposit, returned-item and late-fee baselines no longer define factor-only quantities. -> CG-3 residual on the makeup only.
- XF2: draft, deposit, returned-item and late-fee combination sentences are generic. The deposit's "its own percentage of the endorsement balance" names the acting base, a baseline quantity, which XF3 requires. I withdraw that phrase from revision_1's CG-4 list. The makeup's "each of the others adds its own percentage of the next installment's scheduled premium" names a factor-only quantity. -> CG-4 residual on the makeup only.

All-pairs method-shape table (r2):

| method factor | tiers | pairs | verdict |
| --- | --- | --- | --- |
| endorsement_spread | E/n (n>=2), E, 0 | all | PASS (data divisor; clamp) |
| credit_carry | carry s when c>=s, carry c when 0<c<s, carry 0 when c=0 | all | **FAIL**: compute `MN(credit_held, base_premium) if credit_held >= base_premium else (credit_held if credit_held > 0 else 0)` equals `MN(credit_held, base_premium)` for every credit_held >= 0 (credit_held = MX(0, …)). The three tiers are one method. |
| installment_size_charge | pct·s, min(fee, pct2·s), fee | all | PASS (min with tariff; constant) |
| deposit_by_installments_left | B, B/n with n in {2,3} (data-selected), min(B, max(pct·B, floor)) | all | PASS (revision_1 CG-8 closed) |
| returned_amount_charge | r, max(nsf, pct·r), nsf | all | PASS |
| unpaid_amount_core | pct·U, min(fee, pct2·U), fee | all | PASS |
| returned_payment_recollection | m − p + r, 0, r | all | PASS (adds inputs; r never 0 on its domain) |
| undraftable_account_advance | next sched, next invoice min − payments, 0 | all | PASS |

Realism, point 17 ("A company schedule is acceptable only where a real carrier publishes one for that very charge"):
- Accepted:
  - FL/GA returned-check statute ceilings (Fla. Stat. 68.065/832.08(5); O.C.G.A. 13-6-15).
  - Amount-based methods: endorsement spread, installment fee as a lesser-of percentage of a small installment, late fee as a lesser-of percentage, returned-item fee equal to a small item's face or 5% above 500 in percentage states.
  - Payment-method keys: autopay standing, returned-item channel.
  - Re-collection of a returned prepayment; next installment when the account is closed or stopped.
  - Deposit additions keyed on the added driver's class (age), points, the time left and the endorsement size, and household relationship. Re-judged under point 17: driver class and points are listed rating dimensions, and nonstandard rule manuals publish larger upfront payment for endorsements adding youthful or high-point drivers. I hold these acceptable.
- Not accepted (no carrier publishes that schedule for that very charge) -> CG-16:
  - package-keyed billing charges: package_fee_tier (installment fee), package_late_addition (late fee), package_returned_item_addition (returned-item fee), package_makeup_advance;
  - new-business-keyed charges: new_business_late_addition, new_business_return_addition, new_business_makeup_advance;
  - points_makeup_advance;
  - return_reason_addition (returned-item fee by bank return code).
  - Liability limits, term age and driving record are rated in premium; installment, late and returned-item fees are filed flat or state-capped by plan, payment method and amount; a returned-payment makeup collects what is owed (plus the next installment when the account cannot be drafted), never a percentage keyed on these.
- Statute text -> CG-17: "A returned-item fee never exceeds the service charge the garaging state's returned-check statute allows: … in any other state, and for a plan billing a non-owner term, the plan's nsf_fee." This states as law a 25.00 ceiling for Virginia, Texas, Ohio and Arizona. Texas Bus. & Com. Code §3.506 allows a processing fee up to $30, so the stated statute is invented (point 16). Side effect O-11: in those four states and on every non-owner plan the ceiling equals the standard fee, so all four additions are cancelled unless the returned amount is under nsf_fee.
- Observations kept: O-5 returned_autopay_increase; O-6 the late-fee credit for a returned payment as anti-pyramiding; O-12 an installment_size_charge plus clean-autopay reduction can go negative only on terms under about $200 on a higher package (not reachable in practice).

### findings (r2)
Revision_1 items:
- Closed: CG-1, CG-2 (except CG-13's case), CG-5, CG-6, CG-7, CG-8, CG-9, CG-11, CG-12.
- Closed as originally scoped: CG-10 (points/state fee keys struck). Its successor class is CG-16.
- CG-3: residual, makeup only.
- CG-4: residual, makeup only.

New or residual findings:
- **CG-3r SOURCE-POLICY RED (XF1):** makeup `mk_next_sched` is a quantity shared only by four factors. Bears on task 1.
- **CG-4r SOURCE-POLICY RED (XF2):** the makeup combination sentence names the factor-only "next installment's scheduled premium". Bears on task 1.
- **CG-13 SOURCE-POLICY + SOURCE-FACTOR RED, credit_carry.**
  - (a) Undeclared departure from base S5. Probe on task 0's world with a 400.00 credit: S5 leaves installment 3 uninvoiced, since the credit covers 247.01 + 74.77 + 4.44 = 326.22. credit_carry T1 issues a notice of 79.21 and keeps 152.99 of credit.
  - (b) The ladder is one formula MN(credit, scheduled premium) written as three tiers (table above).
  - (c) The baseline "bills … the standing balance when it is positive", ignoring a credit, is a reading the in-force S5 excludes. A reader applying the baseline with S5 carries the credit, so the factor's own baseline is a straw man.
  - Bears on task 0 (demonstrated there).
- **CG-14 SOURCE-POLICY RED (XF19):** the deposit sentence's "covered in full by the plan's credit" has two readings once a credit is at least the scheduled premium: premium covered (credit_carry T1's measure) or the whole notice covered (S5's measure). The reader cannot tell whether the notice must be issued before the deposit. Not reached in task 0 (credit 50.00).
- **CG-15 SOURCE-POLICY RED (XF19, stale record):** late fee "figured for the installment invoice that the payment most recently returned on the plan had paid, when a returned payment stands on the plan". Any return ever posted stands in the ledger. Probe: task 1's world after the makeup posts (209.18 on 2026-09-21) with installment 4 (due 10-14) unpaid on 2026-10-21. The rule and compute figure the late fee on cured invoice 3 (unpaid -560.00, core -56.00, floored 1.00) instead of invoice 4. Not reached in task 1's scored world.
- **CG-16 SOURCE-FACTOR RED (point 17 realism):** the nine factors listed above. Bears on task 0 (package_fee_tier) and task 1 (the other eight).
- **CG-17 SOURCE-FACTOR RED (point 16):** invented statutory ceiling for VA/TX/OH/AZ and non-owner plans. Bears on the returned-item fee policy. Not load-bearing on task 1's FL world.

## closing_checklist (revision_2)
Post-reveal. Task freezes at 07:55:30Z / 07:55:56Z, charter section at 07:55:05Z (sha256 at freeze e0fc2c3b…ceea); GT read at 07:56:02Z.
- Files: `0.md` and `1.md` carry revision_2 sections appended below revision_1, which is untouched.
- Scope (from charter_scope): unchanged and disjoint/complete (task 0: draft notice + deposit; task 1: returned-item fee + late fee + makeup). uuid8s independent.
- Trees: 1 and 2 prerequisites, all value_input, user-owned roots, acyclic.
- GT equality: every scored value and every per-factor sensitivity equals the blind derivation in both tasks.
- Revision_1 closure verified:
  - Closed: CG-1, CG-2 (except CG-13's case), CG-5, CG-6, CG-7, CG-8, CG-9, CG-10, CG-11, CG-12, task-1 proof text.
  - Residual: CG-3 and CG-4 on the makeup only.
- Regressions: none of the revision_1 closures regressed.
- New defects introduced by the rework:
  - CG-13 (credit_carry);
  - CG-14 (deposit "covered in full");
  - CG-15 (late-fee stale-return selection);
  - CG-17 (stated non-FL/GA statute).
- Under point 17: CG-16. The deposit's driver-risk additions are accepted.
- Not closed. The closing gate re-run is not performed; entry gates were 7/7 green (snapshot 2026-10-19T07:47:42).

VERDICT revision_2: task0=RED task1=RED charter=CG-3r,CG-4r,CG-13,CG-14,CG-15,CG-16,CG-17

## revision_3

## charter_global_frozen (revision_3)
- Gate: worklog tail = `REWORK round 3: gates 7/7 green`.
- Entry evidence: `/tmp/erl0071_coord/snapshot.sh installment_billing_and_fees 3`, run 2026-10-19T23:34:05. All seven gates rc=0 (EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK).
- Hashes:
  - views r3/0 cf8e1d35…ec7f, r3/1 4d50d7c5…f4ab (re-hashed, match)
  - extended yaml 063d2927…abad
  - task_tools.py 6d768d79…25c7
- Both shared inputs changed, so everything is re-derived in full. Several factors were replaced; each is audited as in a first round.
- Frozen before any revision_3 GT field was read. `rework_r3_claims.md` read (claims only). The worklog was not read beyond its tail line. The charter now also reads `blueprint/products/fr.yaml` (new fr cross reads).
- Base copy (lines 1-2076) is byte-identical to the blueprint.

### policy_conflict_scan (r3)
- Draft notice now overwrites base S5 for owner plans, declared with an out-of-scope restatement. A credit is carried "as the credit schedule below sets", and each installment is invoiced even when covered. Revision_2 CG-13(a) closed.
- **New conflict, CG-18.** An ordinary payment is still applied by `payment_application_order`, restated in the deposit's own replaced_by and in the makeup rule: "every other payment is applied in payment_application_order: past-due invoices oldest first (fees before premium), then unpaid late and NSF fees, then the current invoice, then future installments nearest first, any excess being a credit". The draft notice's credit_spread instead spreads "a credit on the plan" (any negative standing balance) equally over the unbilled installments. A prepayment that the application order puts wholly on the nearest future installment is spread by the notice. Neither text yields to the other, and the draft notice's overwrite list does not name `billing_payment_posting`.
- Deposit application ("held on the plan as a credit that its draft notices carry as their credit schedule sets") now matches credit_spread for deposits. Revision_1 CG-2 stays closed.
- Late-fee object selection: "while no payment referencing that returned payment has made it good". The makeup tool now writes `related_payment_txn_id`, so a makeup ends the selection. Any other cure leaves it stale -> CG-15r.

### rule_compute_equivalence (r3)
- Scripted sweep: every compute_basis quote, baseline sentence, replaced_by and policy_source is verbatim in its own rule. Every superseded_clause is verbatim in its base rule. No factor reads another factor's binding, and no factor id is in a tool name.
- Rounding, month-end and tie sentences are present and match compute. Fee floors are stated and computed: notice fee >= 0, returned-item fee >= min_return_fee, late fee >= late_fee_min.
- Statute: FL and GA as before; TX tx_max 30.00 matches Tex. Bus. & Com. Code §3.506(b). For VA, OH, AZ and non-owner plans the rule states "no statutory ceiling is claimed". Revision_2 CG-17 closed.

### action_binding_and_uuids (r3)
- Same five tools, uuid8s unchanged and independent. `authorize_makeup_payment_1af63ac0` gained `related_payment_txn_id`, which its rule now requires ("referencing the returned payment"); the body writes it.
- No prerequisite judged in any body; no ordering word or example value. XF14: no cross-category trigger. XF15 clean.

### prerequisite_graph / prerequisite_sentences (r3)
- Deposit: "The endorsement deposit is fixed only after every installment whose invoice date has arrived is invoiced on the plan." This agrees with the S5 overwrite (owner installments are always invoiced), so there is one reading. Revision_2 CG-14 closed.
- Makeup sentences unchanged from revision_2 (PASS); their objects match the returned-item and late-fee selections (no deadlock, XF19). XF20: both fee figures are floored above zero. Graph acyclic, fields correct.

### override_declarations (r3)
- Draft notice: S3, S5 and the fee sentence overwritten. The fee replaced_by now includes "together with any certificate filing fee they bill".
- Deposit, makeup, returned-item fee: unchanged. Late fee: `overwrite: []` (O-3).
- Undeclared departure from the in-force payment-application sentence for ordinary payments: CG-18.

### factor_ladders (r3)
Per policy (effect; cross_difficulty):
- draft notice (5): endorsement_spread (method; auto), credit_spread (method), autopay_fee_standing (parameter), installment_size_charge (method), certificate_fee_billing (parameter; fr; MS: form AND fee date after the latest invoice AND not reversed).
- deposit (6): unchanged from revision_2.
- returned-item fee (5): returned_amount_charge (method; auto), returned_channel_addition, payment_plan_return_charge, return_history_adjustment, return_timing_addition (all parameter).
- late fee (4): unpaid_amount_core (method), returned_payment_late_credit, autopay_late_standing, late_payment_channel (parameter).
- makeup (5): returned_payment_recollection (method), undraftable_account_advance (method; auto, now owning the next-installment bindings), filing_status_advance (parameter; fr), payment_plan_advance, returned_amount_advance (parameter).
- Structure: 3 disjoint tiers each, stated in the rule and branched in compute; fall-through = baseline; distinct values in every ladder.
- XF1 / XF2 closures:
  - makeup percentages now act on the returned amount, a baseline quantity;
  - the next-installment premium belongs to undraftable_account_advance;
  - revision_2 CG-3r and CG-4r closed.

Method-shape table (r3, all pairs):

| method factor | tiers | verdict |
| --- | --- | --- |
| endorsement_spread | E/n, E, 0 | PASS |
| credit_spread | -c/n (n>=2 data), -min(c, s+fee), standing balance | PASS (data divisor; min) |
| installment_size_charge | pct·s, min(fee, pct2·s), fee | PASS |
| deposit_by_installments_left | B, B/n (n in {2,3}), min(B, max(pct·B, floor)) | PASS |
| returned_amount_charge | r, max(nsf, pct·r), nsf | PASS |
| unpaid_amount_core | pct·U, min(fee, pct2·U), fee | PASS |
| returned_payment_recollection | m - p + r, 0, r | PASS |
| undraftable_account_advance | next sched, next invoice open, 0 | PASS |

Realism under point 23, applied exactly:
- Realistic:
  - Rating-plan dimensions on premium-derived amounts: the deposit additions on the endorsement premium; the makeup advances keyed on SR-22/FR-44 filer status, payment plan and returned amount, on the returned premium payment.
  - Amount-based methods.
  - The EFT/autopay installment fee (filings publish EFT installment fees).
  - The SR-22/FR-44 filing fee billed on the plan (fr_filing_fee_rule: "billed on the backing term's billing plan").
  - Real statutory caps (FL, GA, TX).
- RED (CG-16r: fees or credits keyed on dimensions no filing uses for that very charge; also XF22, because each replaces a struck factor with a new company add-on):
  - returned-item fee: returned_channel_addition, payment_plan_return_charge, return_history_adjustment, return_timing_addition;
  - late fee: returned_payment_late_credit, autopay_late_standing, late_payment_channel.
  - Filings publish one returned-payment fee (state-capped) and one late fee (often a lesser-of on the installment); none keys either on payment channel, plan, return count, return timing or return code. The reworker's claims call these "company schedule dimensions rather than premium-rating quantities".
- Observation O-5: autopay_fee_standing's "returned autopay +1.00" tier.

XF18 stamp (new members, CG-19): `auto_policies.financial_responsibility_filing` ('sr22' on both seeded owner terms, set this round) names the certificate form.
- filing_status_advance (makeup) derives exactly that tier from `fr_filings.variant_name`.
- certificate_fee_billing (draft notice) derives its FR-44 / SR-22 split from the same record.
- The stamp states the tier the factor reads from other records, and the factor is not keyed on the stamp as its source.

### findings (r3)
Revision_2 items:
- Closed: CG-3r, CG-4r, CG-13 (S5 declared; credit ladder now three methods; baseline carries the credit as the standard notice), CG-14, CG-17.
- CG-15: partly closed (makeup cure).
- CG-16: the nine revision_2 factors are removed; successor class CG-16r.
- Revision_1 closures: none regressed.

New or residual:
- **CG-15r SOURCE-POLICY RED (XF19).** The late fee still targets the last returned payment's invoice after that invoice was cured by any payment that does not reference the return. Probe: task 1's plan with invoice 3 paid online 2026-09-25 (233.18, no reference) and invoice 4 (due 10-14) unpaid on 2026-10-21. The fee is figured on cured invoice 3 (unpaid -560.00, core -56.00, floored 1.00) instead of invoice 4. Not reached in task 1's scored world.
- **CG-16r SOURCE-FACTOR RED (point 23 / XF22):** the 7 fee factors above. Bears on task 1.
- **CG-18 SOURCE-POLICY RED:** credit_spread vs the in-force payment application order for ordinary payments. Bears on task 0 (demonstrated there).
- **CG-19 SOURCE-FACTOR RED (XF18):** certificate_fee_billing and filing_status_advance. Bears on task 0 and task 1.

Observations:
- O-13: a filing fee assessed on the same day as an installment invoice is never billed ("after the plan's latest installment invoice", DAYS > 0).
- O-14: the notice posts the filing fee inside the billing_installment_fee row (declared by the fee overwrite, but the ledger labels a filing fee as an installment fee).

## closing_checklist (revision_3)
Post-reveal. Freezes: charter section 23:39:17Z (sha256 at freeze ae99d311…c4ec4), task 0 23:39:41Z, task 1 23:40:02Z. GT read 23:40:10Z.
- Files: revision_3 appended below the untouched revisions 1-2 in `_difficulty.md`, `0.md`, `1.md`.
- Scope: unchanged, disjoint and complete. uuid8s independent. Trees: 1 and 2 prerequisites, all value_input, user-owned roots, acyclic.
- GT equality: every scored value and every per-factor sensitivity equals the blind derivation in both tasks.
- Revision_2 closures verified: CG-3r, CG-4r, CG-13, CG-14, CG-17, the old CG-16 factors. CG-15 partly closed.
- Regressions: none of the revision_1 and revision_2 closures regressed.
- New in the rework:
  - CG-18 (credit schedule vs payment application order);
  - CG-19 (FR stamp, XF18);
  - CG-16r (replacement fee factors);
  - CG-15r (residual stale selection);
  - task-0 proof-text date.
- Not closed. The closing gate re-run is not performed; entry gates were 7/7 green (snapshot 2026-10-19T23:34:05).

VERDICT revision_3: task0=RED task1=RED charter=CG-15r,CG-16r,CG-18,CG-19

## revision_4

## charter_global_frozen (revision_4)
- Gate: worklog tail = `REWORK round 4: gates 7/7 green`.
- Entry evidence: `/tmp/erl0071_coord/snapshot.sh installment_billing_and_fees 4`, run 2026-10-20T05:29:44. All seven gates rc=0 (EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK).
- Hashes (re-hashed after the account cut, unchanged):
  - views r4/0 cf8e1d35…ec7f (byte-identical to r3/0), r4/1 5158526f…4f49
  - extended yaml 937006ef…398b
  - task_tools.py a34cf92e…e2a7
- Resumed after an account cut. Nothing had been appended before the cut; scratch derive4.py survived and was reused.
- Both shared inputs changed, so the charter is re-derived. The returned-item fee and late fee policies were removed and two new policies added, `billing_ext_switch_down_payment` (authorize_switch_down_payment_5d76e7dc, user) and `billing_ext_direct_bill_switch` (switch_to_direct_bill_b1ddc0c4, agent). These are audited as a first round.
- Frozen before any revision_4 GT read. `rework_r4_claims.md` read (claims only). XF points 1-26 applied; 23-26 exactly as written. Base copy byte-identical.

### policy_conflict_scan (r4)
- Five policies: draft notice, deposit (task-0 tree, unchanged factors); makeup, switch down payment, direct-bill switch (task-1 tree: switch <- makeup, switch <- down payment).
- Payment application: the draft notice now overwrites base `billing_payment_posting` "Payments are applied in payment_application_order …" for owner plans (leftover held as a credit carried by the later invoices' credit schedules; deposit and switch down payment held as their own schedules state). Revision_3 CG-18 closed. The four sibling authorization overwrites (deposit, makeup, switch down payment, base remainder) each name the others.
- **CG-20.** `billing_ext_direct_bill_switch` lists `billing_returned_payments` in base_policy_refs but does not overwrite its sentence "A customer may also revoke a recurring authorization at any time; the plan then becomes the Six-Pay Direct Bill Plan for its remaining installments." The extended rule makes the same move conditional: "A plan is moved off automatic draft only after the installment invoice that the payment most recently returned on it had paid is paid again in full." It also takes a switch down payment first ("the representative first takes the switch down payment that move requires"), and only inside a window ("the move falls when at least one installment has been invoiced and two or more are not yet invoiced"). The base sentence lets the move happen at once, with none of these.
- **CG-21 (XF19, decoy).** The switch's gate and `sw_down_paid` count "every down payment posted on the plan (installment number 0, linked to no invoice and to no endorsement) beyond the plan's down_payment_amount". An ordinary online prepayment has exactly those fields, and under the draft notice's own application overwrite it is a credit, not a down payment. Probe on task 1's plan, makeup posted, a 100.00 online prepayment, no switch down payment: the gate holds, `sw_down_paid` = 100.00, respread 155.17, first invoice 128.09.
- **CG-22.** Invoices after the first post-move invoice are priced inconsistently. The direct-bill overwrite of `billing_plan_switch` says the not-yet-invoiced premium less the switch down payment "is spread again in equal shares", and its fee overwrite says every Six-Pay owner invoice "carries an installment fee as the state fee schedule below sets it". But the only policy that issues later owner-plan invoices is the draft notice, whose compute rebuilds the schedule from the current (now Six-Pay) plan parameters and prices its own fee schedule.
  - Probe on task 1's post-gold world (move on 09-24, invoice 4 paid 10-14), installment 5's notice on 2026-10-25: base premium 197.76, endorsement share 126.78, fee 3.96, carried -206.76, minimum due 121.74.
  - The switch rule's respread is 128.23 plus endorsement share 79.51; its FL fee is 6.00.
  - Also XF11: the draft notice's rule carves Six-Pay invoices out of its fee ("carries the fee its own schedule sets"), but its compute does not.

### rule_compute_equivalence (r4)
- Scripted sweep: compute_basis quotes, baseline sentences, replaced_by and policy_source are verbatim. superseded_clauses are verbatim in base. No factor reads another factor's binding. No factor id in a tool name.
- Dead binding: `dn_left` (switch down payment) is never read. The quantity it names ("the installments not yet invoiced are installment_count less those", a baseline sentence) is used only by the basis factor's own count -> CG-26 (XF1).
- Tie, month-end and rounding sentences present and matching.

### action_binding_and_uuids (r4)
- Five `(target_tool, computes)` pairs, each claimed once. uuid8s 1682239d, 3483f9bd, 1af63ac0, 5d76e7dc, b1ddc0c4: independent.
- New bodies:
  - `authorize_switch_down_payment` posts an installment-0 payment with no invoice and no source;
  - `switch_to_direct_bill` writes a revocation, the first invoice and its fee row, and updates variant_name, payment_method_on_file and plan_switches_used.
  - Docstrings match bodies, with no ordering word and no examples. No prerequisite judged.
- XF14: billing_recurring_payment_revoked and billing_plan_switched have no triggers.
- Base `billing_plan_switch`: Monthly EFT and Card plans list the Six-Pay plan in plan_switch_targets with max 2, so the move is a permitted switch.

### prerequisite_graph / prerequisite_sentences (r4)
- Deposit -> draft notice: unchanged (PASS).
- Direct-bill switch -> makeup: "A plan is moved off automatic draft only after the installment invoice that the payment most recently returned on it had paid is paid again in full." State form, connective "only after". Only the makeup (recorded against that invoice) pays it again. PASS as a sentence; it conflicts with the base sentence (CG-20).
- Direct-bill switch -> switch down payment: "The first invoice after the move is figured only after the plan carries the switch down payment the move requires." The state is producible by the down-payment tool; inside the move window the down payment is pct x unbilled premium > 0, so there is no zero-wait (XF20). But a non-down-payment row also satisfies it (CG-21).
- Graph acyclic, fields correct, kinds value_input with real gates.

### override_declarations (r4)
- Draft notice: S3, S5, fee and payment-application sentences overwritten with sibling-exclusive scope.
- Direct-bill switch: `billing_plan_switch` "Unbilled installments keep their amounts …", S3 and the fee sentence overwritten.
- `billing_returned_payments` revocation sentence: in base_policy_refs, not overwritten, contradicted (CG-20).

### factor_ladders (r4)
- draft notice (5): endorsement_spread (M), credit_spread (M), autopay_fee_standing (P), installment_size_charge (M), certificate_fee_billing (P; keyed on the auto stamp `financial_responsibility_filing`, honestly as source: revision_3 CG-19 closed).
- deposit (6): unchanged.
- makeup (5): recollection (M), undraftable advance (M), filing_status_advance (P; now keyed on the stamp: CG-19 closed), payment_plan_advance (P), returned_amount_advance (P).
- switch down payment (5): down_basis_by_invoicing_progress (M), returned_payment / violation_points / liability_package / garaging_state additions (P; percentage points added to the down-payment percentage on premium).
- direct-bill switch (4): endorsement_respread_share (M), switched_plan_credit_carry (M), direct_bill_state_fee (P), direct_bill_certificate_fee (P).
- Method-shape pairs, new factors:
  - down_basis: p·U (no offset) / 0 / p·T - D. PASS (different input plus offset; the 0 tier is never matched by another tier's whole domain).
  - endorsement_respread_share: same shape as endorsement_spread. PASS.
  - switched_plan_credit_carry: -c/n / -(r+f) / standing balance. PASS.
  - All earlier method factors: PASS as in revision_3.
- Realism (points 23-26, exactly):
  - Accepted:
    - point 23 (rating-plan dimension on a premium-derived amount): the switch down payment's points / package / state (company schedule, stated) / payment-history additions; the makeup's filer / plan / amount advances; the deposit's additions.
    - point 24 / 25 publishable service-charge key: direct_bill_state_fee (company state schedule, stated as such).
    - point 26: the transaction's own percentages are not embedded in any recorded amount.
  - **CG-23 (point 24):** the draft notice's installment fee is a service charge. When it varies, "the only acceptable keys are … state …, certificate form and type, backing type, transmission channel …, how coverage ended" (point 25 repeats the closed list). autopay_fee_standing (EFT authorization and return history) and installment_size_charge (installment size) use keys outside that list. Point 23 names payment plan / EFT as a rating-plan dimension, but only for premium-derived amounts; the installment fee is not one, so point 24 governs.
  - **CG-24 (point 26):** certificate_fee_billing (draft notice) and direct_bill_certificate_fee (switch) output the certificate's filing fee (sr22 25.00 / fr44 35.00). That amount is already recorded on the filing ledger (`fr_filing_transactions` fr_filing_fee_assessed.amount), which the agent can read. The form ladder is embedded in a recorded amount, so the tier adds nothing a reader of the ledger does not already have. Only the billing-timing test is the policy's own.
- XF22 / point 25 "each dimension once": no dimension is charged twice within one charge.

### findings (r4)
Revision_3 items:
- Closed: CG-15r (late-fee policy removed), CG-16r (fee policies removed), CG-18, CG-19.
- Revisions 1-3 closures: none regressed.

New:
- **CG-20 SOURCE-POLICY RED:** base revocation sentence not overwritten. Bears on task 1.
- **CG-21 SOURCE-POLICY RED:** decoy prepayment satisfies the switch gate and is counted as the switch down payment. Charter only; task 1's world has no such row.
- **CG-22 SOURCE-POLICY RED:** post-move invoices priced by the draft notice against the switch's respread and state fee (also XF11). Charter only.
- **CG-23 SOURCE-FACTOR RED:** draft-notice installment-fee keys outside point 24. Bears on task 0.
- **CG-24 SOURCE-FACTOR RED:** certificate fee tiers embedded in the recorded fr fee. Bears on tasks 0 and 1.
- **CG-26 SOURCE-POLICY RED (XF1):** switch down payment `dn_left` dead and the baseline defines the installments-left count used only by the basis factor. Bears on task 1.

## closing_checklist (revision_4)
Post-reveal. Freezes: charter 07:54:28Z (sha256 at freeze 56845c5d…df4a), task 0 07:54:44Z, task 1 07:55:13Z. GT read 07:55:22Z.
- Files: revision_4 appended below revisions 1-3 (untouched) in all three files.
- Scope (from charter_scope): task 0 {draft notice, deposit}; task 1 {makeup, switch down payment, direct-bill switch}. Disjoint and complete over the five extended policies and five tools. uuid8s independent.
- Trees: 1 and 2 prerequisites, value_input, user-owned writes, acyclic.
- GT equality: every scored value and every per-factor sensitivity equals the derivation in both tasks.
- Revision_3 closures verified: CG-15r, CG-16r, CG-18, CG-19, task-0 proof-text date. Nothing earlier regressed.
- New defects:
  - CG-20 (base revocation sentence);
  - CG-21 (decoy down payment);
  - CG-22 (post-move invoicing);
  - CG-23 (installment-fee keys, point 24);
  - CG-24 (recorded certificate fee, point 26);
  - CG-26 (XF1 in the switch down payment);
  - task 1's persona naming a prerequisite.
- Not closed. The closing gate re-run is not performed; entry gates were 7/7 green (snapshot 2026-10-20T05:29:44).

VERDICT revision_4: task0=RED task1=RED charter=CG-20,CG-21,CG-22,CG-23,CG-24,CG-26

## revision_5

## charter_global_frozen (revision_5)
- Gate: worklog tail = `REWORK round 5: gates 7/7 green`.
- Entry evidence: `/tmp/erl0071_coord/snapshot.sh installment_billing_and_fees 5`, run 2026-10-20T14:46:03. All seven gates rc=0 (EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK).
- Hashes:
  - views r5/0 6c6ac020…3410, r5/1 144d89ce…738c
  - extended yaml a95834a5…06dd7
  - task_tools.py 3e96d5cc…828d
- Both shared inputs changed, so the charter is re-derived in full. Same five policies and tools; replaced factors are audited as a first round.
- Frozen before any revision_5 GT read; claims file read (claims only). XF 1-26 applied, 23-26 exactly. Base copy byte-identical.

### policy_conflict_scan (r5)
- Draft notice scope is now "a Monthly EFT or Monthly Card Autopay plan … billing an Owner Auto Policy term"; an owner plan moved to the Six-Pay plan "is billed as its own schedule states". The direct-bill switch now governs the first and every later invoice of a moved plan, with its own S3, fee, `billing_plan_switch` and revocation overwrites. Revision_4 CG-22's contradiction (the notice pricing moved plans) is gone.
- `billing_returned_payments` revocation sentence: now overwritten by the switch, scoped ("When the named insured of an Owner Auto Policy term billed by automatic draft asks to stop the drafts while at least one installment has been invoiced and two or more are not yet invoiced, and only then …; any other customer may revoke … at any time"). Revision_4 CG-20 closed.
- Switch down payment is now "recorded on the plan toward the first installment not yet invoiced (carrying that installment's number) and linked to no invoice"; the gate and `sw_down_paid` read exactly that (installment_number = invoices + 1, no invoice). Installment-0 prepayments, deposits (installment 0) and makeups (linked to an invoice) no longer qualify. Revision_4 CG-21 closed.
- **CG-28 (new; a regression from narrowing the notice's scope).** Two draft-notice overwrites still retire their base clause for every owner plan:
  - S5: "For a plan billing an Owner Auto Policy term, and only for such a plan, a credit on the plan is carried onto its later invoices as their own credit schedules set … and each installment is invoiced on its invoice date even when a credit covers it".
  - payment application: "On a plan billing an Owner Auto Policy term … whatever it leaves is held on the plan as a credit that the plan's later invoices carry as their own credit schedules set".
  The deposit also says it is "held whole on the plan as a credit that its draft notices carry". After the narrowing, only EFT/Card draft notices and moved plans have a credit schedule. An owner term billed on the Two-Pay, Four-Pay or (never-autopay) Six-Pay plan gets its invoices under the base remainder ("bills the installment premium, the plan's installment fee and every past-due amount still unpaid"). That remainder has no credit schedule, and base S5 is retired for it. A prepayment or deposit credit on such a plan is therefore carried by no rule (XF5a: the replaced_by's own-plan scope is wider than the schedules that replace it).

### rule_compute_equivalence (r5)
- Scripted sweep clean in all five policies: quotes, baseline sentences, replaced_by and policy_source verbatim; superseded_clause verbatim in base; no factor reads a factor; no factor id in a tool name; no unused binding.
- **CG-27 (XF12 / check 2, empty promise).** The switch rule prices invoices its compute never computes: "Each later invoice of the moved plan bills the premium still to bill after the move divided by the installments then left (the last installment billing all of it), with the installment fee the state fee schedule sets, the certificate filing fee as the standard first invoice bills it and every past-due amount still unpaid, any credit the plan still holds being carried whole up to what the invoice bills; the premium still to bill after the move is …". The S3 replaced_by adds "every later one invoice_lead_days calendar days before its due date, each billing what this schedule states". The policy's compute prices only the first invoice (`computes: minimum_due` of switch_to_direct_bill). No policy claims later-invoice amounts, and the draft notice now excludes moved plans, so these are words-only cases.

### action_binding_and_uuids (r5)
- Five claims, one each; uuid8s unchanged.
- `authorize_switch_down_payment_5d76e7dc` now takes `installment_number` and writes it with related_invoice_id None, matching its rule and docstring. Other bodies unchanged in effect. No prerequisite judged; no ordering word or example. XF14 clean.

### prerequisite_graph / prerequisite_sentences (r5)
- Deposit -> notice: unchanged (PASS).
- Switch -> makeup: unchanged (PASS).
- Switch -> switch down payment: "The first invoice after the move is figured only after the plan carries the switch down payment the move requires, a payment recorded toward the first installment not yet invoiced and linked to no invoice." Record test, producible only by the down-payment tool, positive inside the move window (XF20). PASS.
- Acyclic; fields correct.

### override_declarations (r5)
- Draft notice: S3, S5, fee, payment application. Switch: `billing_plan_switch`, S3, fee, revocation.
- Siblings on S3 and the fee each name the other.
- S5 / payment application: CG-28.

### factor_ladders (r5)
- draft notice (5):
  - endorsement_spread (M), credit_spread (M);
  - filer / points / package endorsement advances (P): the company's filed percentages of the endorsement premium not yet billed, added to the notice's premium, all capped together at that premium.
  - The fee is now the plan's installment_fee plus the certificate fee read from the fr ledger in the baseline. Revision_4 CG-23 and CG-24 closed for the notice.
- deposit (6), makeup (5), switch down payment (5): unchanged.
- switch (4): endorsement_respread_share (M), switched_plan_credit_carry (M), direct_bill_state_fee (P), filer_first_bill_advance (P: filed percentage of the endorsement premium left to bill). The certificate fee is now baseline, from the ledger. CG-24 closed.
- Structure, disjointness, fall-through = baseline and distinct tier values: OK. Method-shape: all PASS (unchanged method factors).
- Realism:
  - Point 23: SR-22/FR-44, points and package on premium-derived amounts (endorsement premium billed ahead). Realistic, stated as the company's filed percentages.
  - Point 24/25: direct-bill fee by the company's state schedule.
  - Point 26: no factor acts on a figure a record embeds; the recorded fr fee is now read in the baseline.
- Observation O-15 (point 25 / XF22, "each dimension once"): within the notice and the first post-move invoice, SR-22 status both brings the recorded filing fee (baseline) and keys the advance percentage. A filing fee charged for a service actually performed alongside an SR-22 premium treatment is ordinary practice, so I do not count it as one dimension charged twice.
- Observation O-16: the makeup's trigger changed to state_due for a customer-authorized payment.

### findings (r5)
- Revision_4 items closed: CG-20, CG-21, CG-22, CG-23, CG-24, CG-26.
- Nothing from rounds 1-4 regressed.
- New:
  - **CG-27 SOURCE-POLICY RED:** the switch rule's later-invoice pricing is words-only. Charter only; no scored write.
  - **CG-28 SOURCE-POLICY RED:** S5 and the payment-application overwrites retire base text for all owner plans, but only autopay notices and moved plans have a replacing credit schedule. Charter only; both task plans are in scope (Card autopay, EFT).

## closing_checklist (revision_5)
Post-reveal. Freezes: charter 14:49:19Z (sha256 at freeze f42226a9…de60), task files 14:49:52Z. GT read 14:49:59Z.
- Files: revision_5 appended below revisions 1-4 (untouched) in all three files.
- Scope: task 0 {draft notice, deposit}; task 1 {makeup, switch down payment, direct-bill switch}. Disjoint and complete over the five extended policies and five tools. uuid8s independent.
- Trees: task 0 has 1 prerequisite, task 1 has 2. All value_input, user-owned writes present, acyclic difficulty-wide.
- Factors:
  - every computation has 4-6 factors (>= 2 parameter, >= 1 method);
  - per task, multi-source and cross-difficulty present;
  - every factor bears weight against an honest baseline, and the all-baseline numbers are definite and differ from gold;
  - realism holds under points 23-26.
- GT equality: every scored value and sensitivity equals the blind derivation in both tasks.
- Revision_4 closures verified: CG-20, CG-21, CG-22, CG-23, CG-24, CG-26, task-1 persona. Nothing from rounds 1-4 regressed.
- Charter-level defects remain open:
  - CG-27 (the switch rule's later-invoice pricing has no compute and no claiming policy);
  - CG-28 (S5 and payment-application overwrites retire base text for all owner plans, but only autopay notices and moved plans carry a replacing credit schedule).
  - Neither touches a scored write. The difficulty therefore does not yet pass the source-layer audit as a charter, so the closing gate re-run is not performed. Entry gates were 7/7 green (snapshot 2026-10-20T14:46:03).

VERDICT revision_5: task0=PASS task1=PASS charter=CG-27,CG-28

## revision_6

## charter_global_frozen (revision_6)
- Gate: worklog tail = `REWORK round 6: gates 7/7 green`.
- Entry evidence: `/tmp/erl0071_coord/snapshot.sh installment_billing_and_fees 6`, run 2026-10-20T15:47:56. All seven gates rc=0 (EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK).
- Hashes:
  - views r6/0 6c6ac020…3410 and r6/1 144d89ce…738c, byte-identical to r5;
  - task_tools.py 3e96d5cc…828d, unchanged, so the action_binding_and_uuids section of revision_5 carries forward;
  - extended yaml 96b7ceac…fb3f, changed, so policy self-consistency is re-derived.
- Claims read (claims only). Base copy byte-identical.
- Scripted sweep (quotes, baseline sentences, replaced_by, superseded_clause, policy_source): clean in all five policies.
- Every compute recomputed on both worlds: identical to revision_5 in every scored value and every per-factor sensitivity (327.36 / 43.97; 519.36 / 153.88 / 109.10). The factor sections of revision_5 carry forward.

### CG-27 (revision_5) — class re-checked
- The switch's later-invoice pricing is now carried by base text, not by an uncomputed extended schedule:
  - the `billing_plan_switch` overwrite defines the respread premium ("that respread installment premium is what every later invoice of the moved plan bills as its installment premium under the base installment schedule … every later invoice carries the new plan's installment fee");
  - the S3 and fee overwrites of both the switch and the draft notice send "a later invoice of a moved plan" to the base remainder;
  - S5's remainder applies nearest-first credits "on a moved plan after its first invoice".
- No extended rule now states an amount its compute does not price; the other four rules were swept for the same class with no member. Closed.

### CG-28 (revision_5) — class re-checked
- S5 and payment-application overwrites are now scoped "For a Monthly EFT or Monthly Card Autopay plan billing an Owner Auto Policy term, and only for such a plan". Every other plan keeps base nearest-first credits and payment_application_order. A credit still held at a move is carried by the first post-move invoice's own credit schedule.
- The deposit now reads: "on a Monthly EFT or Monthly Card Autopay plan the deposit is held whole on the plan as a credit … and on any other plan it is applied in payment_application_order as every other payment is".
- The makeup's "held as a credit for the installments not yet invoiced" agrees with both regimes.
- Closed.

### New finding (introduced in round 5, missed by my revision_5)
- **CG-29 SOURCE-POLICY RED (check 6 / XF19, deadlock).** The deposit covers every owner plan ("When the named insured of an Owner Auto Policy term asks …; … on any other plan it is applied in payment_application_order"). Its gate is "The endorsement deposit is fixed only after every installment whose invoice date has arrived is invoiced on the plan.", resolved_by `issue_draft_notice_1682239d`. Since round 5 that notice is scoped to "a Monthly EFT or Monthly Card Autopay plan".
  - Members:
    1. owner terms billed on the Two-Pay, Four-Pay or never-autopay Six-Pay plan;
    2. moved plans after their first post-move invoice (later invoices go "under the base installment schedule").
  - On either kind of plan, on an invoice date whose invoice is not yet issued, no write of this difficulty brings the waited-on state about. So the deposit can never be fixed: no solution. Example: an owner term on the Four-Pay plan, installment 2's invoice date today and not issued, and the customer asks to pay toward an endorsement.
  - Not reached by task 0 (Card autopay plan).
- Nothing else changed. No closure from rounds 1-5 regressed.

## closing_checklist (revision_6)
- revision_6 appended in all three files; earlier revisions untouched.
- Scopes, trees, factors and GT equality: unchanged from revision_5 (identical worlds and values).
- Closed this round: CG-27, CG-28.
- Open: CG-29 (charter, no scored write).
- The closing gate re-run is not performed while the charter is not clean. Entry gates 7/7 green (snapshot 2026-10-20T15:47:56).

VERDICT revision_6: task0=PASS task1=PASS charter=CG-29

## revision_7

## charter_global_frozen (revision_7)
- Gate: worklog tail = `REWORK round 7: gates 7/7 green`.
- Entry evidence: `/tmp/erl0071_coord/snapshot.sh installment_billing_and_fees 7`, run 2026-10-20T16:12:43. All seven gates rc=0 (EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK).
- Hashes:
  - views r7/0 6c6ac020…3410 and r7/1 144d89ce…738c, byte-identical to r5/r6;
  - task_tools.py 3e96d5cc…828d, unchanged;
  - extended yaml b47c691a…b6af, changed.
- Base copy byte-identical. Scripted sweep (quotes, baseline sentences, replaced_by, superseded_clause, policy_source, factor ids vs tool names): clean in all five policies.
- Recomputation on both worlds: every scored value and per-factor sensitivity identical to revisions 5-6 (327.36 / 43.97; 519.36 / 153.88 / 109.10).

### CG-29 (revision_6) — class re-checked: every wait on every in-scope plan
- Deposit is now scoped "When the named insured of an Owner Auto Policy term billed on a Monthly EFT or Monthly Card Autopay plan asks …". Its rule adds "An owner term billed on any other plan is outside this schedule: a payment toward its additional premium is taken as every other one-time payment is and applied in payment_application_order."
  - Its wait ("every installment whose invoice date has arrived is invoiced on the plan") is produced by `issue_draft_notice_1682239d`, whose policy covers exactly EFT/Card owner plans. Satisfiable on every in-scope plan.
  - Both former members are now out of scope: Two-, Four- and never-autopay Six-Pay owner plans; moved plans, which are Six-Pay after the move.
- Switch -> makeup ("only after the installment invoice that the payment most recently returned on it had paid is paid again in full"): satisfiable on every EFT/Card owner plan by the makeup recorded against that invoice. It already holds when the latest return was made good.
- Switch -> switch down payment: inside the move's own window (>= 1 invoiced, >= 2 left) the down payment's basis tier gives pct x unbilled premium > 0, recorded toward the first uninvoiced installment. Satisfiable.
- Makeup and draft notice: no waits.
- Observation O-17: if the latest returned payment paid no installment invoice (e.g. a returned endorsement deposit), the switch's first wait has no invoice to be "paid again". The natural reading is that nothing waits. No artifact states the opposite, so this is recorded as an observation, not a deadlock.
- CG-29 closed. Nothing from rounds 1-6 regressed.

## closing_checklist (revision_7 — final)
- Audit files: `_difficulty.md`, `0.md`, `1.md`, one per task plus this file. Revisions 1-7 appended in order, older text untouched. Every task carries a source_gt_comparison with PASS (revisions 5-7).
- Coverage and scope: five extended policies. Task 0 = {billing_ext_draft_notice, billing_ext_endorsement_deposit}; task 1 = {billing_ext_returned_draft_makeup, billing_ext_switch_down_payment, billing_ext_direct_bill_switch}. Pairwise disjoint and jointly complete over policies and tools. Each tree lies inside its own task's scope. Task tools and GT closed. uuid8s 1682239d, 3483f9bd, 1af63ac0, 5d76e7dc, b1ddc0c4 independently generated and frozen.
- Problem trees:
  - task 0: 1 prerequisite (notice), 1 value_input edge, user-owned root deposit;
  - task 1: 2 prerequisites (makeup, switch down payment), 2 value_input edges, user-owned makeup and down payment;
  - no cycles; the difficulty-wide graph is a DAG; every wait is satisfiable on every in-scope plan (above).
- Factors:
  - counts: notice 5 (2 M / 3 P), deposit 6 (1 M / 5 P), makeup 5 (2 M / 3 P), switch down payment 5 (1 M / 4 P), first invoice 4 (2 M / 2 P);
  - multi-source and cross-difficulty factors in both tasks;
  - every ladder has 3 distinct tiers stated in its rule;
  - every factor bears weight against an honest baseline;
  - all-baseline numbers are definite and differ from gold (158.01 / 25.00; 595.00 / 37.08 / 0.00);
  - realism holds under XF 16-26.
- Gates re-run once on the final form: the round-7 snapshot above (all seven rc=0, run on the hashes listed).
- Remaining observations (not grounds for rework): O-1 RND vs half-up (no half-cent at any scored point), O-3, O-15, O-16, O-17.
- The difficulty passes the source-layer audit: policy self-consistency PASS, problem tree PASS, factors PASS, unique solution PASS, for both tasks.

VERDICT revision_7: task0=PASS task1=PASS charter=CLEAN

## revision_8

## charter_global_frozen (revision_8)
- Gate: worklog tail = `REWORK round 8: gates 7/7 green`.
- Entry evidence: `/tmp/erl0071_coord/snapshot.sh installment_billing_and_fees 8`, run 2026-10-21T00:23:54. All seven gates rc=0 (EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK).
- Hashes:
  - views r8/0 6c6ac020…3410 and r8/1 144d89ce…738c, unchanged since r5;
  - task_tools.py 3e96d5cc…828d, unchanged;
  - extended yaml 9530caec…34a1, changed.
- This round's items are the renderer's pre-render findings F1-F4 plus a note (`audits/render_source/installment_billing_and_fees/render_r1.md`).
- Auditor disclosure: all five were present in the charter my revision_7 passed as CLEAN. They are misses of my revision_7, and the revision_7 closing checklist is superseded by this revision. In particular, my revision_1 rounding check (XF6) was not re-run on the advance schedules added in round 5.
- Base copy byte-identical. Scripted sweep (quotes, baseline sentences, replaced_by, superseded_clause, policy_source): clean.
- Recomputation on both worlds: every scored value and per-factor sensitivity is unchanged (327.36 / 43.97; 519.36 / 153.88 / 109.10).

### F1 (draft notice rounding vs RND) — closed across its class
- The assembly sentence now reads "the percentages of the advance schedules are added together and applied once to the endorsement premium not yet billed, that advance being rounded half up to the cent once". This matches `RND(MX(0, endorsement_balance) * (adv_filer_pct + adv_points_pct + adv_package_pct) / 100, 2)`.
- The rounding sentence now reads "Apart from the schedule's own figures (its down payment premium and scheduled installment premium), only the shares, the advance and the minimum due are rounded". This matches every RND.
- Class sweep, every policy that adds several percentage schedules:
  - deposit: "each of the others adds its own percentage … the total … rounded … once, at the end";
  - makeup: "… its own percentage of the returned amount … rounded half up to the cent once";
  - switch down payment: percentages summed, "rounded … once, at the end";
  - switch: one advance only.
  - Each rounding sentence matches its RND. No member left.

### F2 (makeup undraftable advance, absent invoice) — closed
- The third tier now reads "when the return is coded otherwise, when the returned payment had paid no installment invoice, or when no installment remains, the makeup adds no advance", which equals compute's `adv_inst != None` guard. No other tier of the five charters reads an invoice the returned payment may lack: the re-collection tier states the no-invoice case, and the switch's first wait is O-17.

### F3 (returned payments in "still owes") — NOT closed across its class -> CG-30
- The deposit sentence now reads "what its most recent installment invoice still owes, its minimum due less the payments posted against it plus the amount the bank returned against the most recent of those payments", which equals compute. But base `billing_returned_payments` ("A returned payment reverses the original payment for its full amount …, and the charges it had paid become unpaid again") makes every returned payment against the invoice count, not only one against its most recent payment.
- Probe on task 0's post-notice world (frozen 2026-12-12; invoice 3 minimum 327.36): payment A 100.00 on 12-10, returned 12-11; payment B 227.36 on 12-12 standing. The invoice owes 100.00. Compute (and the rule's wording) give `dep_latest_unpaid` 0.00, credit 0.00, balance 134.96, deposit 107.97. The base reading gives credit 80.00, balance 54.96, deposit 43.97. Two answers.
- Same class elsewhere:
  - makeup re-collection, first tier: "its minimum due less the payments posted against it plus the returned amount". This adds back only the returned payment's own amount, not other returned payments against the same invoice.
  - makeup undraftable advance, second tier: "that invoice's minimum due less the payments posted against it". Returned payments against the next invoice are not added back.
- The draft notice, switch standing balance and switch wait ("net of returned payments") are correct.
- Members: deposit `dep_latest_unpaid`; makeup `recollect` (first tier); makeup `advance_core` (second tier). No scored world contains a second returned payment, so neither task is reached.

### F4 (makeup payment-plan tiers overlap on Paid-in-Full) — closed across its class
- Tier 2 now requires "installment_count above zero", and tier 3 reads "on the Cardinal Point Paid-in-Full Plan (installment_count zero), whatever its authorizations, nothing". This equals `plan_pct`.
- No other ladder of the charter keys on authorizations against installment_count.

### Note (unused month convention) — closed across its class
- The draft notice's month sentence is removed. The two policies that keep one read months (deposit `MONTHS()` for age; switch down payment `within_months` for returns). The makeup and switch carry none.

## closing_checklist (revision_8)
- Closed this round: F1, F2, F4, note.
- Open: CG-30, charter only. The task worlds have no second returned payment on an invoice: task 0 has none, task 1 has one return on invoice 3 and invoice 4 not invoiced.
- Both tasks unchanged from revision_7 (same worlds, same values, same factor weights), so no task regressed.
- The charter is not clean, so the closing gate re-run is not performed.

VERDICT revision_8: task0=PASS task1=PASS charter=CG-30

## revision_9

## charter_global_frozen (revision_9)
- Gate: worklog tail = `REWORK round 9: gates 7/7 green`.
- Entry evidence: `/tmp/erl0071_coord/snapshot.sh installment_billing_and_fees 9`, run 2026-10-21T01:10:43. All seven gates rc=0 (EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK).
- Hashes:
  - views r9/0 6c6ac020…3410 and r9/1 144d89ce…738c, unchanged since r5;
  - task_tools.py 3e96d5cc…828d, unchanged;
  - extended yaml b6802cea…376c, changed.
- Claims: "CG-30 closed". Base copy byte-identical. Scripted sweep clean.
- Recomputation on both worlds: every scored value and per-factor sensitivity is unchanged (327.36 / 43.97; 519.36 / 153.88 / 109.10).

### render_r1 F1-F4 and note — still closed
The F1 assembly and rounding sentences, F2's no-invoice tier, F4's installment_count condition and the removed month sentence are present unchanged and still match compute.

### CG-30 (revision_8) — NOT closed
What changed:
- Deposit wording only: "what its most recent installment invoice still owes, its minimum due less the payment posted against it, if any, plus every amount the bank returned against that payment".
- Makeup advance tier 2, wording only: "that invoice's minimum due less the payment posted against it, if any, plus every amount the bank returned against that payment"; its compute now adds back returns against the latest payment on the next invoice.
- Makeup re-collection, first tier: unchanged in both words and compute.

The new wording presupposes a single payment per invoice ("the payment posted against it"). The computes still subtract every payment posted against the invoice and add back only the returns against the latest one. Base `billing_returned_payments` still holds: "the charges it had paid become unpaid again". An invoice with two payments, one or both returned, is reachable: a partial payment that bounced, then a second payment.

Two-returns probes (scratch replay of each policy's own compute):
- Deposit, task 0's post-notice world, invoice 3 minimum 327.36, frozen 2026-12-12:
  - payment A 100.00 returned, payment B 227.36 standing. The invoice owes 100.00; compute says still owes 0.00; credit 0.00; deposit 107.97. The base reading gives credit 80.00 and deposit 43.97.
  - A and B both returned. The invoice owes 327.36; compute says 227.36; credit 0.00; deposit 107.97. Base reading: 43.97.
  - The rule's singular "the payment" names neither A nor B, so it fixes no answer either way.
- Makeup, task 1's world, plus an earlier 50.00 payment on invoice 3 (2026-09-05, returned 2026-09-08). The invoice owes 209.18; re-collection computes 209.18 - 610.00 + 560.00 = 159.18; makeup 469.36 instead of the 519.36 the base reading gives.
- The makeup advance's tier 2 has the same structure (only the latest next-invoice payment's returns added back) and the same two-payment gap.

Members open:
- deposit `dep_latest_unpaid`;
- makeup `recollect` (first tier);
- makeup `advance_core` (second tier).
Neither task's world has a second payment on an invoice, so no scored write moves.

## closing_checklist (revision_9)
- render_r1 F1, F2, F4 and the note remain closed. CG-30 remains open (charter).
- Both tasks unchanged and PASS. The charter is not clean, so the closing checklist is not re-confirmed and the gate re-run is not performed.

VERDICT revision_9: task0=PASS task1=PASS charter=CG-30

## revision_10

## charter_global_frozen (revision_10)
- Gate: worklog tail = `REWORK round 10: gates 7/7 green`.
- Entry evidence: `/tmp/erl0071_coord/snapshot.sh installment_billing_and_fees 10`, run 2026-10-21T01:35:14. All seven gates rc=0 (EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK).
- Hashes:
  - views r10/0 6c6ac020…3410 and r10/1 144d89ce…738c, unchanged since r5;
  - task_tools.py 3e96d5cc…828d, unchanged;
  - extended yaml 5f5436d5…576f4f, changed.
- Claims read. Base copy byte-identical. Scripted sweep clean.
- Recomputation on both worlds: every scored value and per-factor sensitivity is unchanged (327.36 / 43.97; 519.36 / 153.88 / 109.10). Both scored worlds are inside every new scope test (`dep_scope_ok` True, `mk_scope_ok` True).
- Applied as directed by the coordinator: a stated record-test scope that the compute enforces excludes its probe worlds from CG-30.
- Observation O-18: XF12 lists "pricing switched by an incidental COUNT" among rejected routes. The coordinator's ruling for this item governs.

### CG-30 (revision_9) — stated and enforced in its members: closed
- Deposit:
  - Rule: "This schedule covers such a plan only while its most recent installment invoice has at most one payment posted against it; … outside this schedule: no endorsement deposit is figured for it (the schedule's figure is 0.00), and a payment toward its additional premium is taken as every other one-time payment is …".
  - Compute: `dep_scope_ok: COUNT(payments on the latest invoice) <= 1`; `result: (…) if dep_scope_ok else 0`.
  - Probes:
    - A returned, B standing: scope False, 0.00.
    - A and B both returned: scope False, 0.00.
    - Control, a single payment returned: in scope, the invoice "still owes" 327.36 (exact: minimum less the one payment plus its return), credit 80.00, deposit 43.97, which equals the base reading.
- Makeup:
  - Rule: "This schedule covers a payment returned … whose installment invoice, if it had paid one, has no other payment posted against it, and whose plan's next installment invoice, if already issued, has at most one payment posted against it; … for any other returned payment no makeup is figured (the schedule's figure is 0.00) …".
  - Compute: `mk_scope_invoice_ok` and `mk_scope_next`, then `mk_scope_ok`; `result: (…) if mk_scope_ok else 0`.
  - Probe 3 (an earlier 50.00 payment on invoice 3, returned): scope False, 0.00.
  - Within scope the re-collection (first tier) and the advance (second tier) are exact, because each invoice they read carries at most the one payment they add back.
- All three CG-30 members are closed under the coordinator's criterion.

### New findings this round
- **CG-31 SOURCE-POLICY RED (scope stated, not enforced; check 2).** The same scope test was added to the words of `billing_ext_switch_down_payment` and `billing_ext_direct_bill_switch`: "and, as the records stood when the move was asked, neither the installment invoice that the payment most recently returned on the plan had paid nor its next installment invoice, if already issued, has two or more payments posted against it". Neither compute carries a scope binding or guard.
  - On probe 3's world (task 1 plan, two payments on invoice 3, both returned) the rules put the move outside both schedules: no switch down payment; the revocation falls to the restated base "any other customer may revoke … at any time".
  - Yet the computes still price it: switch down payment 153.88, first invoice 567.81. By the coordinator's own test (a compute that prices an out-of-scope world under the extended rule), these two are open.
- **CG-32 SOURCE-POLICY RED (out-of-scope restatement contradicts an in-force overwrite).** For EFT/Card owner plans, the draft notice's in-force payment-application overwrite says: "On a Monthly EFT or Monthly Card Autopay plan billing an Owner Auto Policy term, and only on such a plan, a payment is applied to past-due invoices oldest first …, then to the current invoice, and whatever it leaves is held on the plan as a credit that its draft notices … carry as their credit schedules set". The new out-of-scope sentences send the same plans' payments to the retired order instead:
  - deposit: "a payment toward its additional premium is taken as every other one-time payment is, … and applied in payment_application_order";
  - makeup: "it is made good as every other one-time payment is, … applied in payment_application_order".
  - The two texts diverge on any leftover of at least spread_min_credit with two or more installments unbilled. Example: 150.00 left after the current invoice on a card plan with 2 unbilled. payment_application_order ("future installments nearest first") puts 150.00 on the next installment; the overwrite's credit schedule carries 75.00 on each of the next two notices.
  - On plans other than EFT/Card the restatement is right; the conflict exists only on EFT/Card owner plans.

### render_r1 F1-F4 and note
Still closed; text and compute unchanged.

## closing_checklist (revision_10)
- Closed this round: CG-30 (all three members, stated and enforced).
- Open: CG-31 and CG-32 (charter). No scored write is reached: both task worlds are in scope, and neither has an out-of-scope payment.
- Both tasks unchanged and PASS. The charter is not clean, so the closing checklist is not re-confirmed.

VERDICT revision_10: task0=PASS task1=PASS charter=CG-31,CG-32

## revision_11

## charter_global_frozen (revision_11)
- Gate: worklog tail = `REWORK round 11: gates 7/7 green`.
- Entry evidence: `/tmp/erl0071_coord/snapshot.sh installment_billing_and_fees 11`, run 2026-10-21T01:52:20. All seven gates rc=0 (EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK).
- Hashes:
  - views r11/0 6c6ac020…3410 and r11/1 144d89ce…738c, unchanged since r5;
  - task_tools.py 3e96d5cc…828d, unchanged;
  - extended yaml c5a1460e…ee0c, changed.
- Base copy byte-identical. Scripted sweep clean.
- Recomputation on both worlds: every scored value and per-factor sensitivity is unchanged (327.36 / 43.97; 519.36 / 153.88 / 109.10). All scope tests are True on both scored worlds.
- As required this round, one exhaustive pass over the whole charter (all five rules read sentence by sentence against their computes and base refs), for every class raised in revisions 1-10 and XF 1-27. XF 27 (filing dimensions) has no member: no factor here is keyed on filing state, backing cancellation or lapse.

### CG-31 and CG-32 (revision_10) — closed
- CG-31:
  - The switch down payment now carries `dn_scope_ok` (EFT/Card owner plan and the two-payment test), and "When the move is asked on any other plan, or outside these limits, no switch down payment is due (the schedule's figure is 0.00)".
  - The switch carries `sw_scope_ok` (adding >= 1 invoiced and >= 2 left), with the out-of-scope branch computing S03's restated base ("that installment's scheduled premium unchanged, … direct_bill_installment_fee and the standing balance").
  - On probe 3's world both are now 0.00 / base-priced.
- CG-32: the deposit's and the makeup's out-of-scope sentences now apply payments "as every other payment on its plan is", with the EFT/Card credit rule restated for those plans and payment_application_order elsewhere. They agree with the draft notice's overwrite.

### Exhaustive pass — classes with no remaining member
- Undeclared overrides (CG-1): every base sentence in each policy's refs is followed, overwritten with a scoped restatement, or restated outside scope.
- Rule/compute basis (check 2): every compute_basis quote is verbatim.
- Assembly / factor independence / factor-only quantities (CG-3, CG-4, CG-26).
- Rounding (F1).
- Month-end and ties (CG-5).
- Words-only pricing (CG-27).
- Credit and payment-application scope (CG-28, CG-32).
- Deadlock and satisfiable waits (CG-29, XF19, XF20).
- Two-payment invoices (CG-30), within the enforced scopes.
- Plan-tier overlaps (F4).
- Absent invoice (F2).
- Method shape (XF10).
- Realism and keys (XF16-26).
- Stamps (XF18).
- Look-backs (XF21).
- Triggers (XF14).
- Names (XF15).
- Docstrings (XF7).
- Prerequisite form (check 6/7).

### Exhaustive pass — every remaining member

**CG-33 SOURCE-POLICY RED — a stated record test the compute does not enforce (class of CG-31).**

1. Makeup, S01: "When a payment so covered has not been made good and the named insured makes it good, the representative takes the makeup payment …". No binding tests for an existing makeup referencing the returned payment.
   - The first re-collection tier happens to net to 0.00 after a full makeup.
   - The third tier ("otherwise the makeup re-collects the returned amount", the usual case of a draft for exactly the invoice) does not: re-collection stays at the returned amount.
   - Probe: task 1's plan with the returned payment set to 209.18 (third tier). Makeup 470.28; after that makeup posts, scope is still True and the makeup is priced again at 343.26 (capped at the balance).

2. Switch, S04-S06: the respread and first-invoice overwrites are worded for any "move of a plan billing an Owner Auto Policy term off automatic draft to the Six-Pay Direct Bill Plan" / "the first invoice after an owner plan is moved off automatic draft". The compute scope (`sw_scope_ok`), and S00/S03, cover only a move the named insured asks for.
   - The charter's in-force base moves plans off draft without any request: `billing_returned_payments` "When billing_msr_returned_drafts_in_term reaches returned_drafts on a Monthly EFT or Monthly Card Autopay plan, the recurring authorization is revoked and the plan becomes the Cardinal Point Six-Pay Direct Bill Plan", and `billing_agg_returned_payments` "a Monthly EFT or Monthly Card Autopay plan becomes the Six-Pay Direct Bill Plan".
   - Under the wording of S04-S06, such a plan's first invoice is respread and issued "on the move's day". Under the compute and S03 it is base-priced with installments unchanged. Reachable: a Monthly EFT owner plan's second returned draft in a term.

**CG-34 SOURCE-POLICY RED — schedule figures rebuilt from the current plan's parameters or the wrong term record, against the amounts in force.**

3. Draft notice, out-of-scope branch (`RND(MX(0, base_premium + P('installment_fee') + standing_balance), 2)`), later invoices of a moved plan. S00 restates that such invoices bill "its scheduled installment premium", and the switch's S04 fixes that as "that respread installment premium is what every later invoice of the moved plan bills". The branch recomputes `base_premium` with the Six-Pay plan's down payment percentage.
   - Probe on task 1's post-gold world, installment 5 (2026-10-25): branch base_premium 197.76 (standing -254.39, minimum 0.00) against the respread premium 128.23.

4. Makeup undraftable-account advance, first tier, on a moved plan: "the makeup adds that next installment's scheduled premium (term_premium_billed less the schedule's down payment premium, divided by installment_count …)". This is computed with the current (Six-Pay) plan's percentage, against the switch's S04 respread for every later installment of the moved plan.

5. Every owner-plan schedule computed on an EFT/Card plan that was switched in from another plan. Base `billing_plan_switch`, restated in the switch's S04 for "any other switch", keeps "unbilled installments … their amounts and due dates". Six-Pay lists both monthly plans in plan_switch_targets.
   - Members:
     - draft notice (`down_premium`, `scheduled_premium`, `base_premium`, `endorsement_billed`, `standing_balance`, `credit_held`);
     - deposit (`dep_down_premium`, `dep_scheduled` and derived);
     - switch down payment (`dn_down_premium`, `dn_sched`, `dn_unbilled`);
     - switch (`sw_old_down`, `sw_old_sched`, `sw_left_premium`, `sw_base_sched`).
   - Each rebuilds the schedule from the current plan's down_payment_pct. Example with term_premium_billed 1488.00 (task 0's figure), new business: the Six-Pay schedule's installment is 238.08 (down 20%) and is kept by the switch, while the monthly plan's rebuild gives 247.01 (down 17%), and every figure derived from it moves.

6. Draft notice, out-of-scope branch, plans billing a Named Non-Owner Policy term. S00 restates "its invoices follow the base installment schedule unchanged, each billing its scheduled installment premium", and base `billing_down_payment` takes "down_pct for a new-business term or renewal_down_pct for a renewal term". The branch's `first_term` reads `CFIELD('auto','term_number', auto_policy_id=F('auto_policy_id'))`, which is None on a non-owner plan, so it always takes the renewal percentage. A first-term non-owner plan is priced with renewal_down_pct (e.g. Monthly EFT 16.6 instead of 17.0).

**CG-35 SOURCE-POLICY RED — reversed rows counted as owed (class of F3/CG-30).**

7. Makeup S04: "The fees owed with it are every NSF fee posted for the returned payment and every late fee posted for its invoice". `mk_nsf_due` and `mk_late_due` sum every posted fee, including one reversed by a waiver. Base `billing_fee_waivers`: "A waiver reverses one fee transaction for that fee's full amount and references it"; company_error, duplicate_charge and postmark_on_time waivers are available while returns exist. A plan whose late fee was waived as postmark_on_time or company_error is charged it again by the makeup.

### Open member list (bounded)
- CG-33: members 1-2.
- CG-34: members 3-6.
- CG-35: member 7.
- No other member was found in this pass.
- None is reached by a scored world: task 0 is a Card plan never switched, no returns; task 1 is an EFT plan never switched, made good once, no waivers, an asked move.

## closing_checklist (revision_11)
- Closed: CG-31, CG-32.
- Open: CG-33, CG-34, CG-35 (members 1-7, charter only).
- Both tasks unchanged and PASS. The closing checklist is not re-confirmed while the charter has open members.

VERDICT revision_11: task0=PASS task1=PASS charter=CG-33,CG-34,CG-35

## revision_12 (bounded to revision_11 members 1-7 and the lines this rework touched)

## charter_global_frozen (revision_12)
- Gate: worklog tail = `REWORK round 12: gates 7/7 green`.
- Entry evidence: `/tmp/erl0071_coord/snapshot.sh installment_billing_and_fees 12`, run 2026-10-21T02:11:34. All seven gates rc=0 (EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK).
- Hashes:
  - views r12/0 6c6ac020…3410 and r12/1 144d89ce…738c, unchanged;
  - task_tools.py 3e96d5cc…828d, unchanged;
  - extended yaml 84565d9f…9428, changed.
- Base copy byte-identical. Scripted sweep (quotes, baseline sentences, replaced_by, superseded_clause) clean. The draft notice now declares `nonowner` in cross_category.
- Recomputation on both worlds: every scored value and per-factor sensitivity is unchanged (327.36 / 43.97; 519.36 / 153.88 / 109.10). The recorded-down-payment schedule gives the same 252.96 and 210.12 down premiums as before on both worlds.

### Members 1-7 — each probed (scratch replays of the charter's compute)
1. CG-33.1, makeup made-good test. S03 now reads "A returned payment against which a payment referencing it already stands has been made good, and no makeup is figured for it (the schedule's figure is 0.00)", and `mk_made_good` sits in `mk_scope_ok`. Probe (third-tier world, returned 209.18): makeup 470.28; after it posts, 0.00. **Closed.**
2. CG-33.2, automatic moves. S04-S06 and the draft notice's siblings now say "at the named insured's request"; the `billing_plan_switch` restatement names "a plan the returned-draft or certified-funds rules move to the Six-Pay Direct Bill Plan" among "any other switch" (installments keep their amounts). Probe (plan moved by the returned-draft rule: Six-Pay, revoked, no switch down payment): `sw_scope_ok` False; notice fallback `mv_k` 0, premium 205.18, the unchanged schedule. **Closed.**
3. CG-34.3, moved plan's later invoices. The fallback now prices the respread the move fixed (`mv_k`, `mv_down`, `mv_respread`, `fb_premium`, `fb_standing`), and S00 states it. Probe (task 1's post-gold world, installment 5): fb_premium 128.23 = the switch's respread (last installment absorbs). **Closed.**
4. CG-34.4, makeup advance on a moved plan. The advance's first tier now requires "the plan still bills by automatic draft (signed authorizations outnumbering revocations)" (`adv_auth`). Probe (return on the moved plan): adv_auth False, advance 0.00. **Closed.**
5. CG-34.5, switched-in plans. Every schedule's down payment premium is now "the plan's down_payment_amount less the fully earned fees it took", in the draft notice, deposit, makeup, switch down payment and switch. Probe (card plan enrolled at a Six-Pay 20% down, down_payment_amount 322.60): notice and deposit scheduled installment 238.08, the kept Six-Pay amount. **Closed.**
6. CG-34.6, non-owner plans. The notice no longer reads an owner term number; its non-owner branch takes the down payment less `nonowner_policy_fee` from the non-owner premium ledger. Verified on the compute structure; no term-number read remains. **Closed.**
7. CG-35.7, waived fees. "less every waiver that reverses one of those fees"; `mk_nsf_due` and `mk_late_due` subtract waivers tied by `reversed_fee_txn_id`. Probe (task 1's late fee waived company_error): late fee owed 0.00, makeup 509.36. **Closed.**
- Checked and not a member: the waiver read nets only waivers of the latest-posted fee of each kind. On base-consistent worlds that is the only fee that can be reversed: one NSF fee per return, one late fee per invoice, and a duplicate_charge waiver "reverses a second charge of the same fee".

### New defect in the touched lines
**CG-36 SOURCE-POLICY RED (rule words vs compute; record selection by a status the words do not state).**
- The new down-payment-premium sentence reads, in all five rules: "the plan's down_payment_amount less the fully earned fees it took (… the certificate filing fee charged for a new requirement when the certificate on that term was requested on or before the day the plan was set up)".
- Every compute selects that certificate with `CFIELD('fr', …, status='filed')` (fee, id and requested_date). Once the certificate is no longer `filed` (released or terminated when its requirement ends, an SR-26 `cancellation_filed`, or replaced by a corrected refiling), the fee it took is no longer subtracted.
- Probe (task 0's plan with its SR-22 requested on 2026-09-15 at set-up, so down_payment_amount 302.96, then moved to `cancellation_filed`): the compute gives down premium 277.96; the rule gives 302.96 - 25.00 - 25.00 = 252.96. Every schedule figure moves (the scheduled installment would be 242.01 instead of 247.01). The same certificate while `filed` gives 252.96.
- Members: the one shared expression, in `billing_ext_draft_notice.down_premium` (owner and non-owner branches), `billing_ext_endorsement_deposit.dep_down_premium`, `billing_ext_returned_draft_makeup.adv_down`, `billing_ext_switch_down_payment.dn_down_premium`, `billing_ext_direct_bill_switch.sw_old_down`.
- Not reached by either scored world: their certificates were requested after set-up and are still filed.

## closing_checklist (revision_12)
- Closed: revision_11 members 1-7 (CG-33, CG-34, CG-35).
- Open: CG-36 (introduced by this rework's lines; one expression in five policies; charter only).
- Both tasks unchanged and PASS. The closing checklist is not re-confirmed while CG-36 is open.

VERDICT revision_12: task0=PASS task1=PASS charter=CG-36

## revision_13 (bounded to CG-36 and the lines this rework touched)

## charter_global_frozen (revision_13)
- Gate: worklog tail = `REWORK round 13: gates 7/7 green`.
- Entry evidence: `/tmp/erl0071_coord/snapshot.sh installment_billing_and_fees 13`, run 2026-10-21T05:16:08. All seven gates rc=0 (EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK).
- Hashes:
  - views r13/0 6c6ac020…3410 and r13/1 144d89ce…738c, unchanged;
  - task_tools.py 3e96d5cc…828d, unchanged;
  - extended yaml 88ac5392…efebb, changed.
- Base copy byte-identical. Scripted sweep (compute_basis quotes, baseline sentences) clean.
- Recomputation on both worlds: every scored value and per-factor sensitivity is unchanged (327.36 / 43.97; 519.36 / 153.88 / 109.10). The down premium is 252.96 on task 0.

### CG-36 — closed in all six places
- The read is now `XSUM('fr','fr_filing_transactions','amount', event_type='fr_filing_fee_assessed', posted_date=F('enrolled_date'))` in:
  - the draft notice's owner and non-owner branches;
  - deposit `dep_down_premium`;
  - makeup `adv_down`;
  - switch down payment `dn_down_premium`;
  - switch `sw_old_down`.
- The sentence in each rule is "every certificate filing fee the filing ledger shows assessed on the day the plan was set up". No status is read.
- Probe (task 0's plan, the SR-22 requested and its 25.00 fee assessed on the set-up day 2026-09-17, down_payment_amount 302.96): all five owner-plan reads give 252.96 while filed and 252.96 after the certificate moves to cancellation_filed. The revision_12 failure value 277.96 is gone.

### New defect in the touched lines
**CG-37 SOURCE-POLICY RED (second-holding decoy, XF8; departs from base `billing_down_payment` "plus every fully earned fee charged with the term (policy fee and any SR-22 or FR-44 filing fee)").**
- The new read is keyed only by the set-up date. The DSL's XSUM over the fr ledger spans every filing of the customer, and the sentence's "every certificate filing fee the filing ledger shows" is equally unscoped to the term the plan bills.
- A filing fee for a certificate backing another of the customer's terms, assessed the same day, is therefore taken off this plan's down payment premium, although fr_filing_fee_rule bills it "on the backing term's billing plan".
- Probe (task 0's plan; the same customer's second owner term AP2 with its own SR-22 FR2, fee 25.00 assessed on 2026-09-17, the plan's set-up day): all five reads give 227.96 instead of 252.96. Every schedule figure follows; the scheduled installment would be 252.01 instead of 247.01.
- Members: the same six reads as CG-36. The non-owner branch carries the same date-only key.
- Not reached by either scored world: each customer has one certificate, assessed after set-up.

## closing_checklist (revision_13)
- Closed: CG-36.
- Open: CG-37 (introduced by this round's lines; six reads; charter only).
- Both tasks unchanged and PASS. The closing checklist is not re-confirmed while CG-37 is open.

VERDICT revision_13: task0=PASS task1=PASS charter=CG-37

## revision_14 (bounded to CG-37, the same-class certificate-fee reads, and the lines this rework touched)

## charter_global_frozen (revision_14)
- Gate: worklog tail = `REWORK round 14: gates 7/7 green`.
- Entry evidence: `/tmp/erl0071_coord/snapshot.sh installment_billing_and_fees 14`, run 2026-10-21T05:31:04. All seven gates rc=0 (EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK).
- Hashes:
  - views r14/0 6c6ac020…3410 and r14/1 144d89ce…738c, unchanged;
  - task_tools.py 3e96d5cc…828d, unchanged;
  - extended yaml f62a916d…b0af5, changed.
- Base copy byte-identical. Scripted sweep (compute_basis quotes, baseline sentences) clean.
- Recomputation on both worlds: every scored value and per-factor sensitivity is unchanged (327.36 / 43.97; 519.36 / 153.88 / 109.10). Each scored term backs one certificate, so every scope test is True.

### Every certificate / filing-fee read in the charter (scripted list; none filters on status)
Each read is keyed `fr_filing_id=CFIELD('fr','fr_filing_id', auto_policy_id=F('auto_policy_id'))` (non-owner branch: `nonowner_policy_id=F('nonowner_policy_id')`), an exact backing-term tie.
1. draft notice `down_premium`, owner branch (set-up-day fee);
2. draft notice `down_premium`, non-owner branch;
3. draft notice billed certificate fee: `filing_fee_date`, `filing_reversed`, `filing_fee_amount`;
4. deposit `dep_down_premium`;
5. makeup `adv_down`;
6. switch down payment `dn_down_premium`;
7. switch `sw_old_down`;
8. switch first-invoice certificate fee: `sw_cert_date`, `sw_cert_reversed`, `sw_cert_fee`.
Plus the new scope count `XCOUNT('fr','fr_filings', auto_policy_id=…) <= 1` in all five policies' scope bindings. The `financial_responsibility_filing` stamps are term fields, unchanged.

### Probes
- (a) Second owner policy AP2 of the same customer, with its own SR-22 fee 25.00 assessed on this plan's set-up day 2026-09-17: all five owner reads 252.96 (revision_13 gave 227.96); deposit 43.97. **CG-37 closed.**
- (b) Task 0's SR-22 moved to `cancellation_filed`, fee unbilled: the notice still bills the recorded 25.00 (fee 31.00, minimum 327.36) and the down premium stays 252.96. fr_filing_fee_rule: "The fee is fully earned once the certificate is transmitted and is not returned when the backing term later cancels." **Same-class read closed.**
- (extra) Task 0's term backing a second certificate: `notice_scope_ok` False. The notice gives its base figure 133.01 (247.01 + 6.00 - 120.00); the deposit is 0.00 as stated. The new scope is stated and enforced, with base restated outside it.

### New defect in the touched lines
**CG-38 SOURCE-POLICY RED (the class of revision_11's CG-34 member 5, re-entered through the new fallback).**
- For a term backing two or more certificates, the new fallback sets the down payment premium to "the one the base down payment rule sets, term_premium_billed times the plan's down_payment_pct_new_business … or its down_payment_pct_renewal …". That uses the current plan's percentage.
- On a plan switched in from another plan, base `billing_plan_switch` (restated in the switch's S04 for "any other switch") keeps "unbilled installments … their amounts". The notice's S00 restates out-of-scope invoices as billing "its scheduled installment premium".
- Probe (task 0's card plan enrolled at a Six-Pay 20% down, down_payment_amount 322.60, its term backing two certificates): the notice fallback gives down premium 252.96, scheduled premium 247.01, invoice premium 247.01. The installment the switch kept is 238.08.
- Members:
  - draft notice `down_premium` fallback (owner branch; the non-owner branch has the same `term_number` fallback);
  - switch `sw_old_down` fallback, which feeds `sw_base_sched` / `sw_standing` in the switch's out-of-scope base invoice.
  - The deposit, makeup and switch down payment figure 0.00 outside scope and are not members.
- Not reached by either scored world: neither plan was switched in, and each term backs one certificate.

## closing_checklist (revision_14)
- Closed: CG-37 and the same-class certificate-fee reads (all eight reads tied to the term's own filing, status-independent).
- Open: CG-38 (the touched fallback; two expressions; charter only).
- Both tasks unchanged and PASS. The closing checklist is not re-confirmed while CG-38 is open.

VERDICT revision_14: task0=PASS task1=PASS charter=CG-38

## revision_15

## charter_global_frozen (revision_15)
- Gate: worklog tail = `REWORK round 15: gates 7/7 green`.
- Entry evidence: `/tmp/erl0071_coord/snapshot.sh installment_billing_and_fees 15`, run 2026-10-21T05:53:09. All seven gates rc=0 (EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK).
- Hashes:
  - views r15/0 6c6ac020…3410 and r15/1 144d89ce…738c, unchanged;
  - task_tools.py 3e96d5cc…828d, unchanged;
  - extended yaml 4af05646…9755, changed.
- Base copy byte-identical.
- Recomputation on both worlds: every scored value and per-factor sensitivity is unchanged (327.36 / 43.97; 519.36 / 153.88 / 109.10).

### CG-38 — closed
- The fallbacks no longer rebuild the down payment premium from the current plan's percentage. Every branch takes the recorded down_payment_amount less the term's own fees.
- Probe on a consistent switched-in world (task 0's card plan enrolled at the Six-Pay 20% down: down_payment_amount 322.60, kept installments 238.08 on invoices 1-2, balance 818.55):
  - the notice gives scheduled premium 238.08 and minimum due 318.43; by hand 238.08 + 74.77 + 14.58 = 327.43 premium, 6.00 + 25.00 fee, credit 120.00 / 3 carried -40.00, giving 318.43;
  - the deposit gives 43.97 (balance 54.96), equal to my hand figure.

### The reworker's probe matrix
- Independently recomputed, one representative cell per row type:
  - notice enrolled/1/owner/Card (extended);
  - notice switched/1/owner/Card (above);
  - notice non-owner/Card (consistent world: 247.01 + 6.00 - 120.00 = 133.01, matches);
  - notice 2all/Card;
  - notice 2res;
  - notice Four-Pay;
  - deposit switched-in (above);
  - makeup Paid-in-Full: 209.18 + 25.00 + 10.00 + 0 advance + 7.5% x 560.00 = 286.18, matches;
  - switch down payment switched-in: 37.5% x (1236 - 247.20 - 3 x 197.76 = 395.52) = 148.32, matches;
  - switch out-of-payment-scope base;
  - switch 2res.
- The one cell class marked impossible, switched in onto the Four-Pay Plan, is confirmed impossible: no plan's plan_switch_targets lists the Four-Pay Plan (Two-Pay and Four-Pay list only Paid-in-Full; Six-Pay, EFT and Card list Paid-in-Full and the monthly/Six-Pay plans).
- Caveat: several of the reworker's cells are built on internally inconsistent worlds (a variant swapped without re-billing invoices). I verified their formulas on consistent worlds instead; the formulas agree except for the two disagreements below.

### Every disagreement / unpriced or mispriced case found in this pass

**CG-39 SOURCE-POLICY RED — a base invoice stated but not computed.**
- Draft notice: "When the term the plan bills backs two or more certificates while the customer also holds a certificate on another term, the records do not show which of that day's filing fees the plan took, so this schedule sets no figure for the plan (0.00) and its invoices are issued under the base installment schedule."
- Switch, same wording for "that next invoice".
- Both computes return 0.00 for that invoice. No compute prices the base invoice the sentence says is still issued. For an enrolled plan the base figure needs no filing fee at all (`billing_down_payment`: "term_premium_billed multiplied by the plan's down_pct …"), so it is determinable.
- Probe (task 0's card plan, its term backing two certificates, the customer holding a third on another term): notice 0.00. The base invoice is 252.96 down -> 247.01 + 6.00 - 120.00 = 133.01.
- Probe on task 1's plan, same shape: switch 0.00 instead of a base next invoice.
- Members: `billing_ext_draft_notice.result` (2res branch, owner and non-owner) and `billing_ext_direct_bill_switch.result` (2res branch). The deposit, makeup and switch down payment setting no figure is legitimate: those payments are optional.

**CG-40 SOURCE-POLICY RED — a certificate filing fee that no invoice ever bills.**
- fr `fr_filing_fee_rule`: "The filing fee is the certificate's filing_fee, charged once when a filing is requested … and billed on the backing term's billing plan."
- Inside its scope the notice bills an unbilled fee. Every base invoice the charter computes does not:
  - the notice's out-of-scope branch, restated as "each billing its scheduled installment premium, the plan's installment_fee and the standing balance", covering non-owner plans, Two/Four/never-autopay Six-Pay owner plans, two-certificate terms, and a moved plan's later invoices;
  - the switch's out-of-scope base invoice.
- The fr fee is not posted to the billing ledger (it is not in account_balance), so a fee assessed after set-up on such a plan is billed nowhere.
- Probes, each with task 0's/task 1's 25.00 fee unbilled:
  - Four-Pay owner: notice 301.68, fee 10.00 only;
  - two certificates on the term: notice 133.01 (158.01 with the fee);
  - consistent non-owner Card plan: notice 133.01 (158.01 with the fee);
  - task 1's plan outside the switch's payment scope: base next invoice 458.36 (483.36 with the fee).
- Members: the notice `fb_premium` / `result` base branch and the switch's out-of-scope `result` branch. Non-owner SR-22 plans are the common case.

### Reworker's own fixes this round (division by zero on Paid-in-Full / no-installment plans; non-owner endorsement and fee reads in the base fallbacks)
Verified. Paid-in-Full cells give 0.00 in the notice, deposit, switch down payment and switch, as stated. The non-owner base branch reads the non-owner term (probe above).

## closing_checklist (revision_15)
- Closed: CG-38.
- Open: CG-39 and CG-40 (charter only; both are base-invoice cases). Neither task world reaches them: both are autopay plans in scope with one certificate, and their fr fees are billed by the extended notice / switch.
- Both tasks unchanged and PASS. The closing checklist is not re-confirmed.

VERDICT revision_15: task0=PASS task1=PASS charter=CG-39,CG-40

## revision_16 (strictly bounded: CG-39, CG-40, this round's touched lines, no regression)

## charter_global_frozen (revision_16)
- Gate: worklog tail = `REWORK round 16: gates 7/7 green`.
- Entry evidence: `/tmp/erl0071_coord/snapshot.sh installment_billing_and_fees 16`, run 2026-10-21T06:02:29. All seven gates rc=0 (EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK).
- Hashes:
  - views r16/0 6c6ac020…3410 and r16/1 144d89ce…738c, unchanged;
  - task_tools.py 3e96d5cc…828d, unchanged;
  - extended yaml 12d91f6a…56b7, changed.
- Recomputation on both worlds: every scored value and per-factor sensitivity is unchanged (327.36 / 43.97; 519.36 / 153.88 / 109.10). **No regression.**

### (1) CG-39 — closed
- Notice, my revision_15 world (task 0's card plan; term backing two certificates; the customer holding a third on another term): 158.01. That is the base invoice 133.01 (247.01 + 6.00 - 120.00) plus the term certificate's unbilled 25.00, now billed under CG-40.
- Switch counterpart (task 1's plan, same shape): base next invoice 483.36 = 205.18 + 9.00 + 25.00 + standing 244.18.
- Neither is 0.00 any longer. Words and compute agree.

### (2) CG-40 — closed on the four probe worlds
| probe world | expected | computed |
| --- | --- | --- |
| Four-Pay owner (my revision_15 world) | 326.68 | 326.68 |
| two certificates on the term | 158.01 | 158.01 |
| consistent non-owner Card plan | 158.01 | 158.01 |
| switch outside its payment scope | 483.36 | 483.36 |

### (3) Touched lines — one new defect
**CG-41 SOURCE-POLICY RED (CG-40's class, through the reused read on the terms the base branch now covers).**
- The base branches' new certificate-fee read reuses the in-scope `CFIELD('fr','fr_filing_id', auto_policy_id=…)`, which takes the first matching certificate. The base branch is exactly where terms backing two or more certificates now land (the notice's and switch's scopes exclude them).
- When the second certificate on the term carries the unbilled fee, or both do, the second fee is billed nowhere. That contradicts fr_filing_fee_rule ("billed on the backing term's billing plan").
- Probe (my two-certificate world, with the second certificate FR3 given its own 25.00 fee assessed 2026-12-01, unbilled): notice 158.01 with filing fee billed 25.00. The fr rule gives 50.00 owed, so 183.01. The same in the residual world (term with two certificates, a third elsewhere): 158.01 instead of 183.01.
- The reworker's claims declare this as a residual. It sits in the lines this round touched and it moves a computed amount, so it is recorded.
- Members:
  - `billing_ext_draft_notice` base-branch certificate fee (owner and non-owner keys);
  - `billing_ext_direct_bill_switch` out-of-scope certificate fee.
- Not reached by either scored world: one certificate each.

## closing_checklist (revision_16)
- Closed: CG-39, CG-40 (all four probe worlds).
- Open: CG-41 (touched lines; charter only).
- Both tasks unchanged and PASS. The closing checklist is not re-confirmed.

VERDICT revision_16: task0=PASS task1=PASS charter=CG-41

## revision_17 (strictly bounded: CG-41)

## charter_global_frozen (revision_17)
- Gate: worklog tail = `REWORK round 17: gates 7/7 green`.
- Entry evidence: `/tmp/erl0071_coord/snapshot.sh installment_billing_and_fees 17`, run 2026-10-21T06:07:14. All seven gates rc=0 (EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK).
- Hashes:
  - views r17/0 6c6ac020…3410 and r17/1 144d89ce…738c, unchanged;
  - task_tools.py 3e96d5cc…828d, unchanged;
  - extended yaml f7285e3c…e3e0, changed.
- Base copy byte-identical.
- Recomputation on both worlds: every scored value and per-factor sensitivity is unchanged (327.36 / 43.97; 519.36 / 153.88 / 109.10). **No regression.**

### CG-41 — closed under the coordinator's DSL-limit route (stated, computed referral)
- Every place that bills a certificate fee:
  - draft notice `filing_fee_date` / `filing_reversed` / `filing_fee_amount` / `filing_fee_billed`, used by the in-scope notice and every base branch, owner and non-owner keys;
  - direct-bill switch `sw_cert_date` / `sw_cert_reversed` / `sw_cert_fee`, used by the first invoice and the out-of-scope invoice.
- All of them read `CFIELD('fr','fr_filing_id', auto_policy_id=…)` (non-owner: `nonowner_policy_id=…`), the first matching filing entry with no status filter.
- Both rules now carry: "Where an invoice bills a certificate filing fee, it bills the unbilled filing fee of the certificate recorded first among the filings whose backing term is the term the plan bills (the earliest of those entries in the filing records, whatever its present status); when that term backs more than one certificate, the unbilled filing fee of any further certificate is not billed on that invoice and is referred to the filings desk." The standard sentences name "the certificate recorded first on the owner term billed".
- Probes on my two-certificate world (second certificate FR3 with its own unbilled fee):

  | probe | computed | rule |
  | --- | --- | --- |
  | notice, owner, original filing recorded first | 158.01, bills 25.00 | 25.00 billed, FR3 referred: 158.01 |
  | notice, owner, FR3 recorded first (fee 35.00) | bills 35.00, 168.01 | FR3 billed, the other referred: 168.01 |
  | notice, non-owner plan, two certificates | 158.01 | 158.01 |
  | switch out-of-scope invoice on task 1's term | 483.36, bills 25.00 | 205.18 + 9.00 + 25.00 + 244.18 = 483.36, FR3 referred |

- "Recorded first" therefore follows the compute's pick in both orders. Rule words equal compute in every billing place.
- Touched lines: no new defect affecting a value. Observation O-19: the two reworded standard sentences carry a doubled comma ("whatever its present status,,"), which is typographic only.

## closing_checklist (final, revision_17)
- **Audit files:** `_difficulty.md`, `0.md`, `1.md` correspond to the two tasks. Revisions 1-17 are appended in order with older text untouched. Every task file carries a PASS comparison or recomputation from revision_5 on (contamination disclosed on every recomputation since revision_6).
- **Coverage and scope:** five extended policies.
  - Task 0 = {billing_ext_draft_notice, billing_ext_endorsement_deposit};
  - task 1 = {billing_ext_returned_draft_makeup, billing_ext_switch_down_payment, billing_ext_direct_bill_switch}.
  - Pairwise disjoint and jointly complete over policies and the five tools. Each tree lies inside its own task's scope.
  - uuid8s 1682239d, 3483f9bd, 1af63ac0, 5d76e7dc, b1ddc0c4: independent and frozen.
  - Every scope-by-record-test is stated, compute-enforced, with base restated and computed outside it. The certificate-fee multi-certificate case is a stated, computed referral (coordinator route).
- **Problem trees:**
  - task 0: 1 prerequisite (draft notice) via 1 value_input edge; root deposit owner=user;
  - task 1: 2 prerequisites (makeup, switch down payment) via 2 value_input edges, both user-owned; root switch;
  - waits satisfiable on every in-scope plan; acyclic difficulty-wide.
- **Factors:**
  - counts: notice 5 (2 M / 3 P); deposit 6 (1 M / 5 P); makeup 5 (2 M / 3 P); switch down payment 5 (1 M / 4 P); switch 4 (2 M / 2 P);
  - multi-source and cross-difficulty factors present in both tasks;
  - ladders of 3 distinct tiers stated in their rules;
  - every factor bears weight against an honest baseline;
  - all-baseline numbers definite and different from gold (158.01 / 25.00; 595.00 / 37.08 / 0.00);
  - realism under XF 16-27 as ruled.
- **GT equality:** every scored value and per-factor sensitivity equals the derivation in both tasks (unchanged since revision_5).
- **Gates on the final form:** the round-17 snapshot above, all seven rc=0 on the listed hashes.
- **Remaining observations (not grounds for rework):** O-1 RND vs half-up (no half cent at a scored point), O-3, O-15, O-16, O-17, O-18, O-19.
- **Result:** the difficulty passes the source-layer audit: policy self-consistency PASS, problem tree PASS, factors PASS, unique solution PASS, for both tasks.

VERDICT revision_17: task0=PASS task1=PASS charter=CLEAN

## revision_18 (strictly bounded: render_r2 R1, R2, R3, double comma)

## charter_global_frozen (revision_18)
- Gate: worklog tail = `REWORK round 18: gates 7/7 green`.
- Entry evidence: `/tmp/erl0071_coord/snapshot.sh installment_billing_and_fees 18`, run 2026-10-21T06:17:30. All seven gates rc=0 (EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK).
- Hashes:
  - views r18/0 6c6ac020…3410 and r18/1 144d89ce…738c, unchanged;
  - task_tools.py 3e96d5cc…828d, unchanged;
  - extended yaml 8abc2f31…ac68f, changed.
- Base copy byte-identical. Every replaced_by is verbatim in its rule.
- Recomputation on both worlds: every scored value and per-factor sensitivity is unchanged (327.36 / 43.97; 519.36 / 153.88 / 109.10). **No regression.**
- Auditor disclosure: R1-R3 were present in the charter my revision_17 passed as CLEAN, so they are misses of my revision_17. That closing checklist is superseded by the one below.

### R1 — out-of-scope invoice vs the rules' own overwrite tails: closed
- In both the draft notice and the switch, the tail of the `billing_installment_fee_rule` overwrite now reads "any other installment invoice, a later invoice of a moved plan included, carries the plan's installment_fee unadjusted together with the unbilled filing fee of the certificate recorded first on the term the plan bills, which the filing charter bills on the backing term's plan". The tail of the `billing_installment_schedule` overwrite reads "… bills the installment premium, the plan's installment fee with that certificate filing fee, and every past-due amount still unpaid".
- The notice's scope sentence now says out-of-scope invoices follow the base installment schedule "as the overwrites above restate it".
- Compute fallbacks: `fb_premium + P('installment_fee') + filing_fee_billed + fb_standing` and `sw_base_sched + K('direct_bill_installment_fee') + sw_cert_fee + sw_standing`. The words and compute make one statement.
- Probe (consistent non-owner Card plan with an unbilled 25.00 fee): 158.01 = 247.01 + 6.00 + 25.00 - 120.00.
- The sibling overwrites in the two policies carry identical tails.

### R2 — makeup carve-out and unrecorded time reference: closed
- Both the switch down payment and the switch (twice) now read "… has two or more payments posted against it (a payment recorded against an invoice not counting when it is the returned payment itself or a makeup referencing it) …". "as the records stood when the move was asked" is gone.
- `dn_pay_ok` / `sw_pay_ok` compute exactly that record test.
- Probe (task 1 after the makeup posts on invoice 3, which then carries two payment rows): `dn_pay_ok` True, switch down payment 153.88; `sw_pay_ok` True, first invoice 109.10. These are the gold values, and the switch's makeup wait no longer conflicts with its scope test.

### R3 — switched plan with no installment 1 invoice: closed
- Both rules now state the case: "while no installment 1 invoice exists, … the base down payment rule's figure for its present plan". The compute takes the present plan's percentage when `LATEST(… installment_number=1)` is None.
- Probe (task 0's card plan with plan_switches_used 1, no invoices, the residual multi-certificate case): down premium 252.96 = 1488.00 x 17%.

### Double comma
None left (`grep -c ",,"` = 0).

### Touched lines
No new defect: tails, scope sentences, the carve-out and the R3 clause all equal compute on the probes. Nothing else changed.

## closing_checklist (final, revision_18 — supersedes revision_17's)
- **Audit files:** `_difficulty.md`, `0.md`, `1.md` correspond to the two tasks. Revisions 1-18 are appended in order with older text untouched.
- **Coverage and scope:** five extended policies split {draft notice, deposit} | {makeup, switch down payment, switch}. Pairwise disjoint and jointly complete over policies and the five independently generated tools. Every record-test scope is stated, compute-enforced, with base restated and computed outside it. The multi-certificate filing fee is a stated, computed referral.
- **Problem trees:** task 0 has 1 prerequisite and task 1 has 2, all value_input, with user-owned writes in each. Every wait is satisfiable on every in-scope plan. Acyclic.
- **Factors:**
  - 4-6 per computation (notice 5, deposit 6, makeup 5, switch down payment 5, switch 4), each with >= 1 method and >= 2 parameter;
  - multi-source and cross-difficulty present per task;
  - 3-tier ladders stated in their rules;
  - every factor bears weight against an honest baseline;
  - the all-baseline numbers differ from gold.
- **GT equality:** every scored value and per-factor sensitivity equals the derivation in both tasks.
- **Gates on the final form:** the round-18 snapshot above, all seven rc=0.
- **Observations only:** O-1, O-3, O-15, O-16, O-17, O-18. O-19 is resolved.
- **Result:** the difficulty passes the source-layer audit. Policy self-consistency PASS, problem tree PASS, factors PASS, unique solution PASS for both tasks.

VERDICT revision_18: task0=PASS task1=PASS charter=CLEAN

## revision_19 (bounded: KB audit SRC-1 and its class sweep)

## charter_global_frozen (revision_19)
- Gate: worklog tail = `REWORK round 19: gates 7/7 green`.
- Entry evidence: `/tmp/erl0071_coord/snapshot.sh installment_billing_and_fees 19`, run 2026-10-21T19:22:53. All seven gates rc=0 (EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK).
- Hashes:
  - views r19/0 6c6ac020…3410 and r19/1 144d89ce…738c, unchanged;
  - task_tools.py 3e96d5cc…828d, unchanged;
  - extended yaml 36235706…561ed, changed.
- Recomputation on both worlds: every scored value and per-factor sensitivity is unchanged (327.36 / 43.97; 519.36 / 153.88 / 109.10). **No regression.**
- Auditor disclosure: SRC-1 is a member of the undeclared-override class (check 1). My revision_11 exhaustive pass recorded that class as empty, and revisions 17-18 closed the charter as CLEAN; both missed it. The revision_18 closing checklist is superseded.

### SRC-1 — closed
- `billing_ext_direct_bill_switch` now overwrites base `billing_installment_fee_rule` "After a mid-term plan switch, invoices issued from the switch date carry the new plan's fee; invoices already issued keep theirs." The superseded_clause is verbatim in base.
- replaced_by (verbatim in the rule): "For the first invoice after an owner plan is moved off automatic draft to the Six-Pay Direct Bill Plan at the named insured's request, and only for that invoice, the fee is the one the state fee schedule below sets; after any other mid-term plan switch, and on every later invoice of a moved plan, invoices issued from the switch date carry the new plan's fee, and invoices already issued keep theirs."
- It is scoped to the switch's own case and restates base for every other invoice, consistent with the sibling fee and schedule overwrites (draft notice and switch).
- Task 1's first invoice now has one reading: FL fee 6.00 + certificate 25.00 = 31.00, minimum due 109.10. The KB's second figure 112.10 rested on the retired clause.

### Class sweep (undeclared departures from in-force base sentences) — one member remains
**CG-42 SOURCE-POLICY RED (undeclared override; check 1).**
- Base `billing_installment_fee_rule`, third sentence, is in force (not a superseded_clause anywhere): "No installment fee is charged on the down payment, on a final bill, on a renewal bill, on any plan without installments, or on an installment avoided by paying the whole balance before it was invoiced." payoff_waives_future_installment_fees is true on every plan.
- The draft notice's own S5 overwrite has an EFT/Card owner plan's installment "invoiced on its invoice date even when a credit covers it". Its notice then charges `P('installment_fee')` without exception, and nothing states the fee is charged on such an installment. The switch's first invoice is likewise "issued even when the credit covers it" and charges the state fee.
- Probe (task 0's world; the customer pays the whole balance 845.33 on 2026-12-05, before installment 3's invoice date):
  - the notice computes premium 336.36, fee 31.00 (installment fee 6.00 + certificate 25.00), carried credit -321.78, minimum due 45.58;
  - under the in-force fee sentence, no installment fee is charged on that installment: 39.58. Two answers.
- Members:
  - `billing_ext_draft_notice` (notice fee on an installment covered by a whole-balance payoff);
  - `billing_ext_direct_bill_switch` (first invoice fee in the same situation).
- The reworker's sweep confirmed "one installment fee per invoice, and none on plans without installments" but did not reach the payoff clause of the same sentence.
- The rest of the sweep agrees with my check:
  - installment schedule: equal split, due dates, one invoice per installment number, Paid-in-Full;
  - payment posting: cap, posting day, partials, personal checks, agent fee as a separate base charge;
  - certified-funds methods (inherited eligibility; the tools judge none);
  - plan switch: targets, limit, authorization, Paid-in-Full;
  - returned payments: reversal, one NSF fee, automatic moves restated.
- Not reached by either scored world: no whole-balance payoff before an invoice.

### Touched lines
The new overwrite adds no defect: the superseded_clause is verbatim, the replaced_by is in the rule, and it matches its siblings.

## closing_checklist (revision_19)
- Closed: SRC-1.
- Open: CG-42 (two members, charter only).
- Both tasks unchanged and PASS. The closing checklist is not re-confirmed while CG-42 is open.

VERDICT revision_19: task0=PASS task1=PASS charter=CG-42

## revision_20 (bounded: CG-42 and the reworker's clause-by-clause base sweep)

## charter_global_frozen (revision_20)
- Gate: worklog tail = `REWORK round 20: gates 7/7 green`.
- Entry evidence: `/tmp/erl0071_coord/snapshot.sh installment_billing_and_fees 20`, run 2026-10-21T19:48:22. All seven gates rc=0 (EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK).
- Hashes:
  - views r20/0 6c6ac020…3410 and r20/1 144d89ce…738c, unchanged;
  - task_tools.py 3e96d5cc…828d, unchanged;
  - extended yaml 7910eec5…336bc, changed.
- Every compute_basis quote is verbatim in its rule again (the reworker's quote fix; scripted check, five policies).
- Recomputation on both worlds: every scored value and per-factor sensitivity is unchanged (327.36 / 43.97; 519.36 / 153.88 / 109.10); both scored plans carry a positive balance. **No regression.**

### CG-42 — closed
- Both the draft notice and the switch now state: "No installment fee is charged on an invoice whose installment was avoided by paying the whole balance before it was invoiced (the plan's account_balance at the invoice is zero or less): the installment fee every invoice this schedule figures would carry is then 0.00, any certificate filing fee still being billed." The compute sets the installment / state fee to 0.00 on that record test.
- Probes:

  | probe | result |
  | --- | --- |
  | task 0 whole balance 845.33 paid 2026-12-05, before installment 3's invoice | notice fee 25.00 (installment fee 0.00, certificate fee billed); minimum 39.58, the in-force base reading from revision_19 |
  | same payoff on a Four-Pay plan (base branch) | 0.00 (the credit carried covers the invoice) |
  | task 1 after makeup and switch down payment, remaining balance paid, then the move | first invoice fee total 25.00 (state fee 0.00), minimum 32.95 |

- One reading in each case; words equal compute.

### Clause-by-clause base sweep — complete for the base sentences the five rules touch
- The union of the five rules' base_policy_refs is billing_agg_returned_payments, billing_installment_fee_rule, billing_installment_schedule, billing_payment_posting, billing_plan_switch, billing_returned_payments. The reworker's list covers every clause of each, plus billing_delinquency, billing_down_payment, billing_fee_waivers, billing_late_fee_rule and billing_premium_posting, which the rules read.
- I checked each clause's status against the rules:
  - Retired with scoped overwrites restating base:
    - fee rule sentences 1 and 4;
    - installment schedule S3 and S5;
    - payment posting authorization and application;
    - plan switch "unbilled installments keep their amounts … new plan's installment fee";
    - returned payments "revoke … at any time".
  - Every other clause is in force and not departed from, including the fee rule's payoff clause now honored (CG-42).
- No missing clause and no misclassified clause found.

### Touched lines
No new defect: the stated record test equals compute in both policies, and the compute_basis quotes are verbatim.

## closing_checklist (final, revision_20 — supersedes revision_18's)
- **Audit files:** `_difficulty.md`, `0.md`, `1.md` correspond to the two tasks. Revisions 1-20 are appended in order with older text untouched. Earlier misses disclosed (revisions 8, 18, 19).
- **Coverage and scope:**
  - task 0 {draft notice, deposit} | task 1 {makeup, switch down payment, switch}: disjoint and complete;
  - tools uuid8 independent;
  - every record-test scope stated, compute-enforced, base restated and computed outside it;
  - the multi-certificate fee referral stated and computed;
  - every departure from an in-force base clause declared and scoped.
- **Problem trees:** task 0 has 1 prerequisite and task 1 has 2, all value_input, with user-owned writes in each. Waits satisfiable on every in-scope plan. Acyclic.
- **Factors:**
  - 4-6 per computation with >= 1 method and >= 2 parameter;
  - multi-source and cross-difficulty factors per task;
  - 3-tier ladders stated in their rules;
  - every factor bears weight against an honest baseline;
  - all-baseline numbers differ from gold.
- **GT equality:** every scored value and per-factor sensitivity equals the derivation in both tasks.
- **Gates on the final form:** the round-20 snapshot above, all seven rc=0.
- **Observations only:** O-1, O-3, O-15, O-16, O-17, O-18.
- **Result:** the difficulty passes the source-layer audit. Policy self-consistency PASS, problem tree PASS, factors PASS, unique solution PASS for both tasks.

VERDICT revision_20: task0=PASS task1=PASS charter=CLEAN
