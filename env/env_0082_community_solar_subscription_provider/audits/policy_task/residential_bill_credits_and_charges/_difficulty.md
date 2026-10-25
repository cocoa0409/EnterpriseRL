# Policy-task audit — residential_bill_credits_and_charges / charter-global

## charter_global_frozen
- Auditor: independent policy-task auditor (erl-task-policy-audit), revision_1, written 2026-10-25 before any task GT was revealed. Nothing in this section is derived from evaluation_criteria / computations / design_rationale / closures.
- Frozen inputs (sha256 match the coordinator snapshot /tmp/erl0082_coord/snaps/residential_bill_credits_and_charges.r1.txt):
  - `tasks/residential_bill_credits_and_charges/home.extended.yaml` a45de444e5ceacfc7c33aaa007a7d255cbc6ec3704caa367789f536503feb6d9
  - `tasks/residential_bill_credits_and_charges/task_tools.py` dd809eb347fa3780f592a49d1a7fb4c00ec7f5196545c8a3d9701a941f333e7f
  - `blueprint/products/home.yaml` 76adb507…; waitlist.yaml 80037661…; access.yaml a0fd7c67… (cross-category charters read for H1)
- Entry conditions (Step 0): gate snapshot supplied with commands and output lines (EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK); masked views supplied with hashes (task0 23e012d0…, task1 9933931f…, re-verified). Complete.
- Read: blueprint.yaml, db_schema.json, share_tools.py (signatures), products/home|waitlist|access.yaml, the extended charter, task_tools.py, the two masked views, the binding coordinator files audits/render_source/{XF_recipe,realism_bar,owner_ruling}.md, and the DSL evaluator semantics in skills/erl-task-instantiate/scripts/check_compute.py (functions MONTHS/DAYS/build_env imported into a scratch evaluator at /tmp/audit_residential_bill_credits_and_charges_0082/scripts/ev.py; no gate was run).
- Masked / unread: tasks/*.json (beyond the views), worklog.md, plan.md, any other env, any sibling difficulty.
- DSL facts used (check_compute.py): `within_months=N` keeps rows with 0 <= MONTHS(date, today) < N (so a future date is excluded, a date today included); `LATEST` keeps the first row on record among equal keys (strict `>`); `CFIELD` returns the first matching holding; `SUM`/`COUNT`/`LATEST` are scoped to the holding (home_sub_id).

### policy_conflict_scan
- Base copy: lines 1–1800 of home.extended.yaml are byte-identical to blueprint/products/home.yaml (`diff` empty).
- Six extended policies: home_ext_final_balance_payment (user, pay_final_balance_42abd449), home_ext_estimated_charge (agent, bill_estimated_charge_232393a8), home_ext_overdue_late_fee (agent, assess_overdue_charge_late_fee_df41ca22), home_ext_reversed_payment_replacement (user, pay_reversed_payment_replacement_378a2026), home_ext_returned_payment_fee (agent, assess_returned_payment_fee_1f86a5ed), home_ext_reopened_late_fee (agent, assess_reopened_charge_late_fee_2381e61d).
- Overlapping subjects: home_late_fee_assessed is written by two extended policies; their scopes are partitioned by the overwrite tails (latest-invoiced actual dual charge with no returned payment for its month vs the charge of the month on the latest returned-payment line) — but the two tails do not agree on the residue (finding CG-4). home_payment_received is written by two user policies (final-balance on request vs replacement on request); the persona's ask (make good a reversed payment vs settle a closed subscription) selects one; no world forces both.
- Cross-category reads: waitlist (variant_name, status, utility_account_id) and access (status, recert_due_date) — read-only branches; no cross-category write.
- Events written by the tools: home_charge_billed, home_late_fee_assessed, home_payment_received, home_returned_fee_assessed — all inside the claimed event_types; their base `triggers` are all `[]` (F4 clean).
- Scopes of the M=2 tasks (from the views' worlds, not from charter_scope): task0 tree = final_balance ← {estimated_charge, overdue_late_fee}; task1 tree = reversed_payment_replacement ← {returned_payment_fee, reopened_late_fee}. Pairwise disjoint and jointly covering all six extended policies (re-confirmed against charter_scope only after reveal, see closing section).
- Base/extended conflicts on the same quantity: see override_declarations and CG-18.

### rule_compute_equivalence
- E5 sweep (whitespace-normalised substring test, script in scratch): every compute_basis quote of all six policies is verbatim in its rule; every compute binding has a basis entry; every baseline.rule paragraph is verbatim in its rule; every K() key used is declared, and every K() key except `due_lookback_months` (final-balance, replacement) is named in the rule.
- Floors/caps/rounding (B5/D1/D2): every MX(0,…) is stated as "never below 0.00"; RND(x+1e-9,2) placements match "rounded half up to the cent once, at the end"; late fees keep MN(max, MX(min, RND(…))). Exception: the zero-product edge of both late-fee policies (CG-9).
- Ladders: every tier named in factors[].ladder is a sentence of the rule and a branch of the `decides` binding, and vice versa — except gaps found by probes: dispute-hold residue (CG-6), two charges in one statement month (CG-5), future effective date (CG-10).
- Probe table (scratch copies; decoy / second record / absent):
  | read | decoy | second record | absent | verdict |
  |---|---|---|---|---|
  | open dispute (LATEST requests, outcome=received) | withdrawn/declined dispute excluded ✓ | two same-day disputes: first on record, rule says so ✓ | 'none' → hold 0 ✓ | dispute naming a payment / returned-payment / credit line: compute = fee-line tier, rule has no tier ✗ (CG-6) |
  | IEP waitlist (CFIELD first match) | submitted / other class / other account → no tier ✓ | second open IEP impossible (waitlist max_open_reservations_in_class 1) ✓ | 'none' ✓ | ✓ |
  | Access (EXISTS / CFIELD) | closed Access → no tier ✓ | second active Access impossible (access max_per_customer 1) ✓ | absent ✓ | plan with recert_interval_months 0 → recert_due_date empty → never the access tier (rule-consistent; realism obs O-4) |
  | overdue charge (LATEST actual dual) | later estimate / consolidated charge excluded ✓ | same-day tie: first on record, stated ✓ | 'none' → 0 ✓ | ✓ |
  | reopened charge (LATEST actual dual, billing_month = latest return month) | — | two actual charges of the same month (reversed and re-posted credit) → compute takes the later; rule is singular, no tie rule ✗ (CG-5) | 'none' → 0 ✓ | ✗ |
  | latest returned line (rf_ret_line / rf_item_id / prv_method) | — | same-day tie consistent across the three LATEST calls ✓ | no return → base 0 → no fee ✓ | ✓ |
  | latest subscriber change (cap_eff) | annual_resize / removal ignored ✓ | inc and dec same date ✓ | '0001-01-01' → tier 3 ✓ | future effective_date: MONTHS negative < 6 → tier 1/2 ✗ (CG-10) |
  | latest posted credit (rate_last_*) | reversal rows excluded ✓ | same-day tie consistent ✓ | 0 → ratio 1 ✓ | ✓ |
  | priced-on tier 2 (LATEST payment of month) | — | two post-due payments: compute adds only the latest; the rule's gloss says "the amount that was still unpaid when the charge fell due" ✗ (CG-7) | no payment → tier 3 ✓ | ✗ |

### action_binding_and_uuids
- (target_tool, computes) pairs are unique: six policies, six distinct tools, each `computes: amount`.
- uuid8 tails 42abd449, 232393a8, df41ca22, 378a2026, 1f86a5ed, 2381e61d: no shared prefix, no sequence, no adjacency — independent.
- Docstrings: no sequence position, no other tool named, no ordering word (the only "before" is the in-tool rounding sentence). No concrete example values.
- Tool bodies (G1–G5): no datetime/time/random/uuid/secrets import; rounding by a class static method `_Money.half_up`; each write tool calls ctx.create in its own body; bodies check only amount > 0 and (pay tools) method ∈ {ach, card}, both stated in the docstrings; no derived value is computed and no eligibility or prerequisite is judged; no composite string arg; no factor id is a substring of a tool name.
- Owner ruling: both user tools are holder-completed portal payments; both rules state "Meadowlark representatives never take card or bank account numbers and no payment method is held on file" (owner_ruling (b)) ✓.

### prerequisite_graph
- prerequisite filled everywhere; four edges, all `kind: value_input`, `form: state`, no fallback_reason (correct for state form): final_balance ← estimated_charge (gate fbp_chg), final_balance ← overdue_late_fee (gate fbp_fees), replacement ← returned_payment_fee (gate rpp_fees), replacement ← reopened_late_fee (gate rpp_reopened_fees). All gates are real bindings of the blocked compute; all resolved_by are the depended-on target_tools; graph acyclic; no authoring-viewpoint wording.
- Each policy_source is verbatim in the blocked policy's own rule ✓.
- `condition` vs sentence: E4's condition ("the actual dual-billed charge of the statement month named on the latest returned-payment line") is narrower than its sentence ("every charge a returned payment has reopened") — CG-11.

### prerequisite_sentences
Four-point test, each edge:
- E1 "The final-balance payment is fixed only after every statement month that ended the plan's estimate wait or more calendar days ago without a posted credit carries an estimated subscription charge, as far as the plan's run of estimates allows." — connective "only after" ✓; record-visible state (statement month, posted credit, estimated subscription charge) ✓; no tool / id / snake_case ✓; only bill_estimated_charge writes estimated charges ✓. Derivation: sentence → months without a posted credit ≥ estimate_wait_days after month end → the estimated-charge rule bills them → one reading. Not satisfiable when the estimate window holds no actual charge ("no estimate is billed") — not carved out (CG-12a).
- E2 "The final-balance payment is not fixed until the subscription's latest-invoiced actual dual-billed charge, once its late-fee grace period has passed with the charge still unpaid, carries a late fee line referring to it." — "not … until" ✓; state ✓; no tool name ✓. Two tools write late-fee lines, but the overwrite scopes assign the latest-invoiced charge to the overdue rule when its month has no returned payment (resolvable; obs O-1). Not satisfiable when the base dispute hold or the banked-share/zero-product rules forbid the fee on that very charge — not carved out (CG-12b).
- E3 "The replacement payment is fixed only after every returned payment on the subscription carries its returned-payment fee." ✓ all four points; only assess_returned_payment_fee writes that family; every plan's returned_payment_fee_usd is 20.00, so the 0.00 no-fee case is unreachable ✓.
- E4 "The replacement payment is not fixed until every charge a returned payment has reopened, once its late-fee grace period has passed with the charge unpaid, carries a late fee line referring to it." ✓ connective/state/no-tool; scope broader than condition and than the reopened rule's scope (CG-11).
- No depended-on rule restates a sentence; no rule states an undeclared cross-problem order.

### override_declarations
Sentence-by-sentence against base_policy_refs (finding half only):
- final_balance (refs payment_application, cancellation, benefit_basis; overwrite []): follows every sentence (portal-only ach/card is within payment_methods; "a balance left after closing remains due" is consistent with lines left open). New definition of the payment's billing_month ("the month of the payment") conflicts with the base event field `billing_month: statement month paid` and, through the extended unpaid definitions, with home_evt_payment_application's oldest_due_first settlement — CG-18.
- estimated_charge (refs subscription_charge, benefit_basis): overwrite 1 retires the estimates sentence and restates it with "Meadowlark bills", invoice-today, due +invoice_due_days, billing_type dual and the run percentage — declared. billing_type dual for a consolidated-billed subscription departs from the base event field "billing_type: arrangement in force" (obs O-2; base policy sentence on billing_type governs the charge of a posted credit). Overwrite 2 retires "Each posted credit statement line is priced by exactly one actual subscription charge", which does not conflict, and restates it verbatim — CG-14 (XF E2).
- overdue_late_fee / reopened_late_fee (refs late_fee, payment_application, credit_correction): both retire the fee-amount sentence; scopes self-named; tails disagree (CG-4). Inherited and not retired: "No fee is written … when the charge is fully paid or credited by the assessment date" — base settlement sense conflicts with the extended billing_month unpaid amount (CG-18). Inherited: grace, one fee per charge, dispute hold ✓.
- returned_payment_fee (ref payment_application): retires the fee sentence; scope = every residential returned-payment fee; due date and 0.00 rule restated ✓.
- reversed_payment_replacement (overwrite []): as final_balance.

### factor_ladders
Counts and labels (structure only):
| policy | factor | label | tiers | multi-source | cross-diff | B1 / label verdict | realism |
|---|---|---|---|---|---|---|---|
| final_balance | fbp_standing | method | 3 | no (one record) | – | FAIL: all tiers = MX(0, Σamount(charge+fee lines in a due_date window) + returns − payments − credits), window ∈ {all, due<today, due≤today} (CG-1) | R1/R2 ok |
| | fbp_dispute_hold | method | 3 | yes (request+ledger) | – | pass (charge tier nets month payments and adds late fees; fee tier does neither) | ok; only the latest open dispute (O-5) |
| | fbp_household_income | parameter | 3 | yes (access, waitlist) | waitlist/access | pass | R1 (LMI key); deferral of fees (O-6) |
| | fbp_open_estimates | parameter | 3 | yes (status+ledger) | – | pass | condition "latest charge is an estimate" weakly tied to the quantity (O-7) |
| estimated_charge | est_standing | method | 3 | yes | – | pass | ok |
| | est_season | parameter | 3 | yes | – | pass | R3/R6 ok |
| | est_capacity | method | 3 | yes | – | pass; negative-lag edge (CG-10) | ok |
| | est_credit_rate | method | 3 | no | – | FAIL: tiers 1+c vs 1+c/2 differ only by a constant multiplier on the same input (CG-3) | ok |
| | est_run | parameter | 3 | yes | – | pass | R6 |
| | est_lag | parameter | 3 | no | – | pass | R6 |
| overdue / reopened late fee (identical ladders) | *_priced_amount | method | 3 | yes | – | pass (tier 1 drops payments/returns; tier 2 adds the latest payment) ; gloss CG-7 | ok |
| | *_months | parameter | 3 | no | – | pass | R2 (1.5 % per month or part) |
| | *_household_income | parameter | 3 | yes | waitlist/access | pass | R1 |
| | *_repeat | parameter | 3 | no | – | pass | R6 |
| | *_size | parameter | 3 | no | – | pass | R6 (lower % for larger charges) |
| | *_banked_share | method | 3 | no | – | pass by letter (tier 2 adds two inputs) | R6 |
| returned_payment_fee | rpf_item_base | method | 3 | no | – | pass | R4-like (greater of flat and %); gloss CG-8 |
| | rpf_item_kind | parameter | 3 | no | – | pass | R1 (chargeback vs NSF) ; NY cap CG-17 |
| | rpf_reversal_time | parameter | 3 | yes | – | pass | REJECTED: invented mechanism (CG-16) |
| | rpf_repeat | parameter | 3 | no | – | pass | R6 |
| | rpf_household_income | parameter | 3 | yes | waitlist/access | pass | R1 |
| replacement | rpp_return_record | method | 3 | no | – | FAIL: tiers 1 and 3 = same expression with a different due_date window; tier 2 = tier 3 + Σamount of the same lines filtered by bill_date (CG-2) | ok |
| | rpp_dispute_hold | method | 3 | yes | – | pass | as fbp |
| | rpp_household_income | parameter | 3 | yes | waitlist/access | pass | R1 |
| | rpp_reversal_kind | parameter | 3 | no | – | pass | R6 at best (O-6) |
- Surviving counts after the B1 strikes: final_balance 3 factors (CG-1 → below the 4 floor), replacement 3 factors (CG-2 → below floor), estimated_charge 5 (CG-3 mislabel), late fees 6 / 6, returned fee 5 (4 after CG-16).
- Method pairwise tables (distinguishing input per pair): est_standing (1,2) dispute record vs error-credit sum; (1,3)/(2,3) removed record / credit input. est_capacity (1,2) post-change charges vs allocation kW; (x,3) constant. priced_amount (1,3) payments/returns dropped; (2,3) LATEST payment added; (1,2) returned amount. banked_share (2,3) banked_value/credit_value. item_base (1,3) greater-of with 10 % of item; (2,3) item amount; (1,2). dispute_hold (1,2) month payments + late fees; (x,3) constant.
- Defining-sentence ownership (A4): fbp_fees_recent / rpp_fees_recent and fbp_est_open / rpp_reopened_fees are plain bindings used only by one factor's deduction and sit outside that factor's bindings (structure obs O-8; no consequence demonstrated).

### findings
(severity: H = bears on the scored solution of a task or a gate floor; M = reachable in producible worlds; L = structural)
- CG-1 SOURCE-FACTOR RED (H) — fbp_standing is labelled method but its three tiers are the same combination of the same windowed sum (XF B1); struck, home_ext_final_balance_payment keeps 3 factors < 4. Bears on task0.
- CG-2 SOURCE-FACTOR RED (H) — rpp_return_record likewise (XF B1); replacement keeps 3 factors < 4. Bears on task1.
- CG-3 SOURCE-FACTOR RED (M) — est_credit_rate tiers 1 and 2 differ only by the constant ½ on the same relative change: a parameter labelled method (XF B1). Bears on task0's estimate.
- CG-4 SOURCE-POLICY RED (M) — sibling overwrite tails disagree (XF E3): overdue tail "the late fee on a charge whose statement month carries a returned payment is worked out by the reopened-charge late fee rule"; reopened rule covers only "the actual dual-billed charge of the statement month named on a subscription's latest returned-payment line" and sends "every other late fee" to base. A latest-invoiced charge whose month carries an older (not latest) returned payment gets the reopened rule by one tail and the base rule by the other — two fees. No task world engages it.
- CG-5 SOURCE-POLICY RED (M) — "the actual dual-billed charge of the statement month named on that returned-payment line" (reopened fee, replacement reopened fees) has no rule for two actual charges in one month, which base produces ("A corrected credit the utility posts afterwards is a new posting"); compute silently takes the later (XF B3/C2). Not engaged in task1.
- CG-6 SOURCE-POLICY RED (M) — dispute-hold ladder has no tier for an open dispute naming a payment, returned-payment or billing-credit line; compute applies the fee-line tier (MX(0, amount − credits)) (XF B3/C1). Both payment policies; not engaged.
- CG-7 SOURCE-POLICY RED (M) — priced-on tier 2: operative words "the unpaid amount plus that most recent payment" vs appositive "the amount that was still unpaid when the charge fell due"; with two post-due payments p1, p2 the first gives amount − p1, the second amount (XF C1/C6). Both late-fee policies; not engaged (one post-due payment in task0; tier 1 in task1).
- CG-8 SOURCE-POLICY RED (M) — returned fee tier 2 "it is the returned amount, so that the fee never exceeds the item" is falsified by the multipliers (card 1.25, check 1.1, repeat up to 1.5): returned card item 12.00 → compute 15.00 vs "never exceeds the item" 12.00 (XF C6). Not engaged.
- CG-9 SOURCE-POLICY RED (M) — late-fee zero-product edge: rule "the product is rounded half up to the cent once, then raised to late_fee_min_usd … ; no fee is written when the product is 0.00"; compute writes late_fee_min_usd whenever 0 < lf_raw < 0.005 (e.g. unpaid 0.20 → raw 0.003 → compute 2.00, rule "no fee") (XF B5/C1). Both late-fee policies; not engaged.
- CG-10 SOURCE-POLICY RED (M) — est_capacity: "it took effect within the estimate window when the whole months from its effective_date to today are fewer than basis_window_months" — a filed increase effective next month gives MONTHS < 0 < 6, so the compute applies the capacity tiers to a change that has not taken effect (XF C1 negative lag). Not engaged (task0 change effective 2026-07-01).
- CG-11 SOURCE-POLICY RED (M) — E4 sentence "every charge a returned payment has reopened" is broader than its condition (only the latest return's month) and than the reopened rule's own scope; an older return's reopened unpaid charge must carry a late fee for the payment to be fixed, but only the base rule (no tool) prices it (check 6/7 strength). Not engaged in task1 (the older reopened charge is paid; the July charge already carries a fee).
- CG-12 SOURCE-CHAIN RED (M) — waits not satisfiable in engaged worlds (XF F1/F2): (a) E1 when the estimate window holds no actual charge ("no estimate is billed"); (b) E2 when the latest-invoiced charge is the one under an open billing dispute (base hold, the very case the dispute-hold factor prices), when its credit is fully banked (banked-share 0), or at the zero product — no carve-out, so the final-balance payment can never be fixed. Not engaged in task0.
- CG-14 SOURCE-POLICY RED (L) — estimated_charge overwrite 2 retires a non-conflicting base clause and restates it verbatim (XF E2 "retire only clauses that actually conflict").
- CG-15 SOURCE-POLICY RED (L) — XF A8: baseline.params name keys the baseline paragraph does not state: `due_lookback_months` (final_balance, replacement), `invoice_due_days` (returned fee). No numeric consequence.
- CG-16 SOURCE-FACTOR RED (H, realism) — rpf_reversal_time: the returned-payment fee falls to 0.9 / 0.75 of itself the longer the bank or card issuer took to return the item. No business publishes a cheaper returned-payment fee for a later return (late ACH returns are unauthorized-entry claims; chargeback cost does not fall with age): an invented mechanism (realism bar: R6 does not cover invented mechanisms). Bears on task1.
- CG-17 SOURCE-FACTOR RED (M, realism/law) — rpf_item_kind check tier on the 20.00 base gives 22.00 for any returned check on a New York (NY_VDER) subscription, above the 20-dollar ceiling New York General Obligations Law § 5-328 sets for a dishonored-check charge (auditor's reading of the statute); rpf_item_base 10 % × a 350+ dollar check × 1.1 likewise exceeds Maryland's 35-dollar dishonored-check collection-fee limit (Md. Com. Law § 15-802). X4/R6 "no conflict with law". Not engaged (task1 is a card reversal).
- CG-18 SOURCE-POLICY RED (M) — two clauses on one quantity: extended unpaid amounts net "every payment recorded for its statement month (billing_month)", and the extended payment rules record a call payment "with the month of the payment as its billing month", while base keeps "No fee is written … when the charge is fully paid … by the assessment date" with payments settling "the line with the earliest due_date first" and the base event field "billing_month: statement month paid". World: a portal payment settles the latest actual charge in full before its grace ends → base: fully paid, no fee; extended overdue rule: unpaid = full amount, fee assessed. Per-task seed consequence: see each task's factor_weight (H2).
- Cross-difficulty seed class (both tasks, demonstrated per task): each world's Income-Eligible Priority Waitlist reservation requests more kW than waitlist_agg_account_headroom allows at its submission date, so the row is not a state the waitlist charter produces (XF H1) — see task files.
- Observations: O-1 two late-fee tools resolvable only through overwrite scopes; O-2 estimate billing_type dual on consolidated subscriptions; O-3 an estimated charge on a closed subscription relies on billable_status including closed (consistent); O-4 Access plans with recert_interval_months 0 and Access recert grace never reach the access tier; O-5 only the most recently received open dispute is held (DSL limit, a second open dispute is collected); O-6 fee-share and reversal-share deferrals leave fees open that the customer asked to pay — R6 at best; deductions can overlap (a recent late fee on the disputed charge is held in full and also fee-share-deducted; a reopened late fee is in both the fee-share and reversal-share sets; in the notice_given estimate tier a not-yet-due estimate outside the covered lines is deducted); O-7 fbp_open_estimates' "latest charge is an estimate" part does not say whether the deducted estimates are still unposted (est_open already nets true-ups); O-8 A4 ownership of the deduction bases.


## closing_checklist
Written after both reveals (2026-10-25 09:27 UTC); the section above stays as it was before any reveal.
- Files: _difficulty.md, 0.md, 1.md correspond to tasks 0 and 1; revision_1 only (no earlier revision existed).
- Coverage/scope: charter_scope task0 = {final_balance, estimated_charge, overdue_late_fee}, task1 = {replacement, returned_payment_fee, reopened_late_fee} — pairwise disjoint, jointly all six extended policies, equal to the trees derived blind. Task tools closed; uuid8s independent.
- Trees: each has 2 prerequisite problems, 2 value_input edges, an owner=user root, no cycle; the difficulty graph is a DAG. PASS for both tasks.
- Unique solution: both blind derivations equal GT on every write argument and every factor_sensitivity figure. PASS for both tasks.
- Factors: NOT satisfied — final_balance and replacement fall below 4 surviving factors (CG-1, CG-2); est_credit_rate mislabelled (CG-3); rpf_reversal_time rejected on realism (CG-16); in both tasks the only cross-difficulty evidence (the IEP waitlist row) is not a state the waitlist charter produces, and the priced-amount factor's weight rests on a payment attribution against home_evt_payment_application (task files F-T0-1/2, F-T1-1/2).
- Policy self-consistency: charter-global REDs CG-4..CG-12, CG-14, CG-15, CG-17, CG-18 (none changes either task's scored figures, except through the seeds flagged by CG-18).
- Instantiation gates: not re-run by this auditor (the audit edits nothing; the coordinator's round-1 snapshot is the gate record). The difficulty does not pass the source-layer audit.

VERDICT revision_1: task0=RED task1=RED charter=CG-1,CG-2,CG-3,CG-4,CG-5,CG-6,CG-7,CG-8,CG-9,CG-10,CG-11,CG-12,CG-14,CG-15,CG-16,CG-17,CG-18

## revision_2

### charter_global_frozen (revision_2)
- Re-audit round 2, 2026-10-25 ~10:10 UTC. Entry: `tail -1 worklog.md` = "REWORK round 2: gates 7/7 green" (only that line read). Snapshot rebuilt by executing `/tmp/erl0082_coord/snapshot.sh residential_bill_credits_and_charges 2` (10:05:41Z): views task0 80fdcf97…, task1 e3273036…; home.extended.yaml 214e4717… (was a45de444…), task_tools.py c8df6bb2… (was dd809eb3…); other charters unchanged; all seven gates OK.
- Both shared inputs changed → every charter-global section re-derived in full below (revision_1 text above left untouched). Read: claims file rework_r2_claims.md, realism_bar.md AMENDMENT 1, XF_recipe.md, owner_ruling.md, the revised charter/tools, the new views. Not read: worklog.md (beyond its last line), plan.md, tasks/*.json before this section and both task revision_2 derivations were on disk. **The LEVER CATALOGUE that AMENDMENT 1.2 asks auditors to check lives in worklog.md, which the coordinator's addendum forbids reading; R6 minimal-count was therefore checked against the charter itself.**
- Base copy still byte-identical to blueprint/products/home.yaml.

### charter re-derivation (revision_2)
- Policies/tools/trees unchanged in shape: final_balance ← {estimated_charge, overdue_late_fee}; replacement ← {returned_payment_fee, reopened_late_fee}; both pay tools now take `billing_month`. uuid8s unchanged; bodies still check only amount > 0 / portal method; no datetime/random imports; G1–G5 clean; F4 clean.
- E5 sweep (scratch): all compute_basis quotes verbatim; baseline paragraphs verbatim; baseline.params agree (payments [], returned fee [returned_payment_fee_usd], estimate [basis_window_months], late fees [late_fee_pct, min, max]).
- Prerequisite sentences: all four carry "wherever the <rule> writes/bills one" — connective, state, no tool name ✓; satisfiable when the resolver writes nothing ✓; E4 now names "the charge of the statement month named on the latest returned-payment line" = the reopened rule's scope ✓.
- Overwrites: payment-application order retired and restated identically in both payment policies ("for every payment … only for a payment", disputed line + its late fees settled by no payment, billing_month = statement month of the oldest open line settled) — identical sibling texts, no second reading (obs R2-O1). Late-fee tails partition identically (latest-return month's charge → reopened; other latest-invoiced actual dual charge → overdue; rest → base quoted) ✓. Estimate overwrite now dual-only, consolidated waits ✓.
- Method pairwise tables: fbp/rpp_pending_statement (1,2) open estimate of the month subtracted; (x,3) constant 0 ✓. est_reversals (1,2) charges exactly basis_window_months back taken in; (x,3) ✓. est_standing (1,2) error-credit sum vs removed record ✓. est_capacity ✓. priced_amount ✓. banked_share ✓. item_base ✓. dispute_hold (1,2) month netting + late fees; (x,3) ✓.
- Counts: final_balance 4 (2 method, 2 parameter), replacement 4 (2/2), estimate 6 (3/3), late fees 6/6 (2/4), returned fee 5 (1/4). Multi-source and cross-difficulty (waitlist) present per task ✓.

### item-by-item status of revision_1 REDs
| id | claim | auditor check | status |
|---|---|---|---|
| CG-1 | fbp_standing removed; baseline every open line; pending-statement method | baseline paragraph = pay_open; pending tiers distinct | CLOSED |
| CG-2 | rpp_return_record removed | as CG-1 | CLOSED |
| CG-3 | est_credit_rate → parameter (weights 1 / rate_weight_narrow / 0) | label now honest | CLOSED |
| CG-4 | tails partition identically | rules + overwrites read side by side (diff) | CLOSED |
| CG-5 | re-post case + tie stated | rule sentence + LATEST compute agree | CLOSED |
| CG-6 | third tier for payment/return/credit lines | probe: dispute on payment line → hold 0 | CLOSED |
| CG-7 | gloss removed | rule = compute | CLOSED |
| CG-8 | "returned amount itself" | no promise left | CLOSED |
| CG-9 | test on the rounded product | probe raw 0.0034 → no fee | CLOSED |
| CG-10 | effective_date on or before today | probe future increase → ratio 1 | CLOSED |
| CG-11 | sentence/condition = latest return month | verified | CLOSED |
| CG-12 | carve-outs | verified on all four sentences | CLOSED |
| CG-14 | disputed: one_charge_per_credit's dedup (applies_to home_charge_billed, object home_credit_id) would otherwise reach estimates, which all carry an empty credit reference | evidence checked in base eligibility one_charge_per_credit — dispute accepted | CLOSED (dispute accepted) |
| CG-15 | params fixed | verified | CLOSED |
| CG-16 | rpf_reversal_time removed; rpf_committed_term (R1 plan term) | R1 key on recorded term_months / term_end_date | CLOSED |
| CG-17 | check tier removed, check capped at plan fee (20.00), ceiling 35 | compute MN(ceiling, MN(plan fee) for check) | CLOSED |
| CG-18 | payment order overwritten, month recorded, seeds relabelled | see R2-1 | **OPEN (reduced form)** |

### findings (revision_2)
- **R2-1 = CG-18 still open — SOURCE-POLICY RED (M).** The new recording rule ("each payment line records as its billing_month the statement month of the oldest open line it settles") gives a payment that settles two statement months one month label, while every extended unpaid amount nets only "payment[s] recorded for its statement month". World: a payment settles the July charge and, in full, the August charge before August's grace ends → recorded July → overdue rule: August unpaid = full amount, fee assessed; inherited base: "No fee is written … when the charge is fully paid … by the assessment date" → no fee. Not engaged in either task world (no seeded payment spans two charge months).
- **R2-2 (new) SOURCE-POLICY RED (M) — est_reversals decoy (XF C1).** Rule: "the offset charges are left out (each such credit equals the charge it offsets, so their sum is taken off and their number is taken off the count)". Compute subtracts every reversal-correction credit posted in the window even when the charge it offsets was invoiced before the window. Probe (task0 world, offset charge fef1c1a1 moved to 2026-05-20): compute basis 113.115 → estimate 105.48; reading "only charges in the window are left out" → basis 114.899 (no subtraction). Not engaged in task0 (the offset charge is in the window).
- **R2-3 (new) SOURCE-POLICY RED (M) — reversal-share base includes a disputed fee (XF C1).** Rule: "The reopened late fees are the late fees referring to … that returned-payment line, other than a fee held for a dispute". Compute zeroes rvs_fees only when the dispute names the reopened charge; a dispute naming the reopened late fee itself puts it in the hold (fee tier) and leaves it in rvs_fees. Probe (task1 world, dispute on the reopened late fee): hold 5.72 and rvs_fees 5.72 — the same 5.72 line is deducted 1.5 times. Not engaged (task1's dispute names the September charge).
- **R2-4 (new) SOURCE-FACTOR RED (realism) — rpp_pending_statement.** For a make-good payment on an *active* subscription the rule requires the customer to pay, now, the charge for a credit that has not been invoiced yet ("so that the charge invoiced for that credit is already paid when it is billed"). A closing payoff that includes the pending final statement is real practice (fbp_pending_statement is accepted); compelling prepayment of next week's invoice inside a payment whose purpose is to replace a reversed payment is not something a provider publishes — it exists here as a mirror of the closing-account method (AMENDMENT 1.3 "change what the task tests rather than pad"). Bears on task1.
- **R2-5 (new) SOURCE-FACTOR RED (realism, AMENDMENT 1.2) — R6 late-fee factors with an unused honest lever.** Both late-fee computations carry three company-schedule factors (repeat ×1.2/×1.3, size ×0.95/×0.9, banked-share) while the R1 plan-term key (P term_months with F term_end_date — readable, varying across plans 0/36/60/120/240, and already accepted as R1 on the returned-payment fee) is used by neither. By AMENDMENT 1.2 an R6 factor with an unused honest R1–R5 lever available is RED: at least one of the three R6 factors on each late-fee computation fails. (Catalogue unreadable under the read ban; the reworker may dispute with evidence.) Bears on task0 (overdue fee) and task1 (reopened fee).
- **R2-6 (new) SOURCE-POLICY RED (M) — "oldest open line" undefined after a reversal correction of a paid charge.** In the payment-recording rule an "open line" is never defined. After a credit reversal, base offsets the original (already paid) charge with a full billing credit and bills the re-post as a new charge that no payment settles; reading A (the charter's own unpaid measure, payments recorded for the month) treats the re-post as paid by the original month's payment; reading B (settlement under the order — no payment ever settled the re-post) treats it as open and oldest. Task0's world is exactly this (May 2026: fef1c1a1 paid, credited by 513b36fb; re-post 01726bfa due 2026-08-19). Consequence demonstrated in 0.md revision_2.
- Observations: R2-O1 identical sibling payment-order overwrites; R2-O2 user pay tools' billing_month docstring lacks "as read out to the subscriber" and neither persona has a line for it (the hand-over is passive); R2-O3 R6-WAIVED: est_unpriced_line (weight 2 when the posted month replaced an estimate), rpf_repeat, fbp_open_estimates, rpp_reversal_kind — no unused honest R1–R5 lever found on those computations; R2-O4 a negative pending-statement "addition" (open estimate larger than the coming charge) reduces the payment — rule allows it, realistic as a true-up preview; O-4/O-5 carried.

### closing_checklist (revision_2)
- Written after the revision_2 reveals (10:13 UTC); files 0.md, 1.md, _difficulty.md each carry a revision_2 appended below revision_1, which is left untouched.
- Scopes disjoint and covering; trees valid (2 value_input edges each, owner=user root, DAG); tools closed; uuid8s independent.
- Unique solution: task1 PASS; task0 RED (R2-6, scored billing_month).
- Factors: counts and labels now meet the floor in every computation; RED remains on realism/lever grounds (R2-4 task1, R2-5 both tasks).
- Charter REDs open: R2-1 (CG-18 reduced form), R2-2, R2-3, R2-4, R2-5, R2-6. All other revision_1 REDs closed (CG-14 by accepted dispute).
- Gates: coordinator round-2 snapshot (7/7 OK) is the gate record; this audit edits nothing.

VERDICT revision_2: task0=RED task1=RED charter=R2-1,R2-2,R2-3,R2-4,R2-5,R2-6
