# worklog — lease_end_servicing (env_0066_captive_auto_finance_company), M=2

Scratch: /tmp/lease_end_servicing_0066/ (src/*.yaml policy sources, t*_state.json seeds, persona and rationale texts).
Per-task dossiers live in tasks/0.json and tasks/1.json `design_rationale`.

## Draw (scripts/draw_counts.py --tasks 2)
- task 0: prerequisite_problems 1, factor_counts [4, 5]
- task 1: prerequisite_problems 1, factor_counts [6, 6]

## Route-around (frozen base)
The lessee-owned acts the blueprint lists (turn-in, early return, purchase signing, dealer authorization,
inspection dispute) carry no figure of their own in the schema: an end-of-term payment equals the stored
end_of_term_balance, and a buyout equals the honoured quote. Both user problems are therefore Kestrel written
schedules on the claimed event lease_end_of_term_payment, each declared as an overwrite with a scoped
replaced_by that names its own case and the sibling's case:
- lease_ext_charge_off_hold (task 0, user): hold payment that keeps an unpaid end-of-term balance from charge-off.
- lease_ext_end_installment_plan (task 1, user): first installment of a lease-end installment plan.
Agent problems: lease_ext_wear_forgiveness (task 0; loyalty contract signed after billing) and
lease_ext_excess_mileage (task 1; extended lease, mileage not yet billed).

## Problem trees
- task 0: lease_ext_charge_off_hold <- lease_ext_wear_forgiveness (value_input, state form, affirmative
  "only after"). Gold: waiver 925.00, hold payment 712.08 (skip waiver -> 924.83).
- task 1: lease_ext_end_installment_plan <- lease_ext_excess_mileage (value_input, state form, negated
  "not ... until"). Gold: mileage charge 1445.32 (6284 miles), first installment 901.77 (skip charge -> 741.18).

## Factor-independence table (each factor reads only its own evidence bindings)
- wear_forgiveness: brand_return_cap (retail/balloon date+dpd), punctual_addition (late-charge count),
  forgiving_scope (advance-inspection date, wear-item sums), tenure_addition (paid-in-full retail payments),
  low_mileage_addition (odometer/allowance, mileage-charge count). Assembly: forgiveness_allowance (sum), result.
- charge_off_hold: stage_rate (invoice date), relationship_relief (retail/balloon/preowned dpd), returned_relief
  (returned-payment count), hold_shape (ledger balance, total payment). Assembly: hold_rate, result.
- excess_mileage: allowance_convention (dates, extension), brand_miles (retail/balloon/preowned dates+dpd),
  autopay_buffer (autopay count), rate_schedule (months run, allowance), clean_return_miles (wear charges/items),
  care_holder_miles (Care financing). Assembly: charged_miles, result.
- end_installment_plan: punctuality_installments (late charges), relationship_installments (retail/balloon/
  preowned dpd), completion_installments (monthly payments), tenure_installments (paid-in-full balloon),
  first_shape (invoice date, total payment), setup_fee (returned payments). Assembly: installments, result.

## Edge probes (scratch, check_compute evaluator)
task 0: no retail -> 225.00/no relief; retail dpd 12 -> 675.00; retail 95 days after turn-in -> 425.00; retail
pending_funding -> 425.00; no advance inspection -> 625.00; no invoice -> early stage (guarded). task 1: no
pre-owned -> 1790.32; Care cash -> 1560.32; Care cancelled -> 1675.32; no balloon -> tenure 0; pre-owned dpd 8 ->
no credit; no extension -> standard allowance; early termination -> whole months; under allowance -> 0.00; no
invoice -> equal share. Known DSL first-match limit: CFIELD reads the first active contract of a product; each
world seeds exactly one active contract per product read.

## compute_basis sweep
Scratch script: every compute_basis quote of all four policies is verbatim in its own rule — 0 misses.

## Full gate block (round 1)
- check_extended: EXTENDED OK
- check_task_tools: TASK TOOL CONTRACT OK
- replay_tasks: REPLAY OK (0.json 13 acts, 1.json 14 acts, deterministic, non-vacuous)
- check_solvability: SOLVABILITY OK
- check_compute: COMPUTE OK (suite means branches 34.50, steps 13.50; history max 73; branches max 37)
- check_grounding: GROUNDING OK
- check_cross_fire: SCOPE OK
- check_cache_diff: INFO only (no cache trap used)
- check_traceability: 4 misses, all unlock tool_name provenance (KB not yet rendered) — expected at this stage
- erlbench validate: only "required document not found" / "tool not mentioned in KB" (KB not yet rendered)
ROUND 1: gates 7/7 green

## REWORK round 2 closure (audit: audits/policy_task/lease_end_servicing/{_difficulty,0,1}.md)
- F-C1 -> lease_ext_wear_forgiveness brand_return_cap tier 2 is now halfway between the tier's wear_forgiveness_cap and loyalty_wear_forgiveness_cap (strictly between the other two tiers on every tier sheet); param past_due_return_cap removed.
- F-C2 -> lease_ext_end_installment_plan first_shape re-cut by plan balance: balance above the large-plan count of monthly payments -> one total_monthly_payment down plus the rest over the installments; balance no more than one monthly payment -> the whole balance; otherwise balance over installments (never above the balance; no enrolment-lateness surcharge).
- F-C3 -> lease_ext_excess_mileage allowance tiers disjoint as stated (pull-ahead/early termination first, then "any other lease" turned in mid-extension), with month and day counting conventions stated to match MONTHS()/DAYS().
- F-C4 -> hold and plan scopes made exclusive and record-distinguishable: plan open while the invoice due date has not come or passed no more than 30 days earlier with no end-of-term payment since the invoice; hold only more than 30 days past due with no payment since; each charge-off overwrite tail names the sibling case without mutual deferral.
- F-C5 (and class) -> wear forgiveness low-mileage addition reads odometer vs allowance only (no read of the mileage charge); the hold reads the invoiced balance (charges billed on the invoice date), so a charge billed in the contact cannot move it; the plan balance excludes waivers, so a forgiveness waiver cannot move it. Each payment program depends only on its declared prerequisite.
- F-C6 -> every read of another product states the first-listed reading in its rule; wear-item reads are restricted to the turn-in_final report (tie: first recorded) and an item adjusted on dispute moves the forgiveness scope to the whole charge (removals netted in the clean-return count); autopay and completion counts are net of returned payments, stated in the rules.
- T0-1 -> with F-C4 the plan is out of scope on task 0's world (59 days past due), so the hold is the only answer to the persona's ask; persona letter removed (O-T0-1).
- T0-2 -> wear forgiveness keeps 5 genuine factors (brand_return_cap, punctual_addition, forgiving_scope [method], tenure_addition, low_mileage_addition) after F-C1/F-C5 fixes.
- T1-1 -> allowance_convention (F-C3 fixed) and first_shape (F-C2 fixed) are again sound method factors.
- O-C1 -> a zero wear forgiveness books no waiver; the hold's edge condition names a waiver only for a positive amount.
- O-C2 (realism of credit schedules) -> kept as published Kestrel schedules; noted in rationales.
- O-C3 -> covered by the F-C5 class fix above.
- O-C4 (stale writes) -> task 1 dates shifted (turn-in 2026-09-17, billing/invoice 2026-10-02, mileage held 12 days); task 0 forgiveness owed only since the retail contract signed 2026-09-25.
- O-C5 ($0.00 mileage reading) -> rule: when the miles charged are zero no charge is billed; tool docs a positive amount.
- O-T1-1 (invoice for a charge billed during the call) -> declared overwrite: an excess mileage charge billed under the rule carries no separate invoice and falls due end_of_term_payment_days after billing unless a plan governs.
- O-T1-2 -> removed with the F-C2 re-cut. O-T1-3 -> F-C4. O-T1-4 -> day-method allowance kept as published convention (noted).
- Seed realism sweep -> retail/balloon/pre-owned APRs read from their tier rate sheets and payments re-amortized; balloon amounts = tier balloon % of MSRP; pre-owned first payment not yet due (0 payments, 0 dpd); Care Gold term/miles/price within its sheet; lease figures re-derived from tier sheets.
- Tools -> docstrings: no "then"/"toward"; plan tool describes only the payment it posts; mileage amount positive.

## XF recipe check (per policy x point; Y = applied/verified)
| point | wear_forgiveness | charge_off_hold | excess_mileage | end_installment_plan |
|---|---|---|---|---|
| 1 assembly sentence generic, once | Y | Y | Y | Y |
| 2 non-commuting order fixed (replace, add, compare / subtract relief before applying) | Y | Y | Y | Y (installments added before division, fee last) |
| 3 factor independence (transitive, scripted) | Y | Y (invoice_date plain shared) | Y | Y |
| 4 ownership | Y | Y | Y | Y |
| 5 compute_basis verbatim (scripted: 0 misses) | Y 24 | Y 14 | Y 25 | Y 17 |
| 6 ties stated (latest advance date; turn-in report first recorded; latest invoice) | Y | Y | Y | Y (scope) |
| 7 counting conventions (DAYS window, lead days, MONTHS) | Y | Y | Y | n/a (no date arithmetic in compute) |
| 8 every branch both ways (absent report/contract/invoice, zero) | Y | Y (out of scope stated) | Y | Y (out of scope stated) |
| 9 base clauses: scoped replaced_by, siblings named | Y | Y | Y | Y |
| 10 rounding sentence = RND placement | Y | Y | Y | Y |
| 11 tools: only real effects, no examples, no ordering words | Y | Y | Y | Y |
| 12 proof text re-synced (rationale, closure, traces, persona) | Y | Y | Y | Y |

## Factor-independence table (scripted, transitive reads outside own bindings)
- wear_forgiveness: brand_return_cap none; punctual_addition none; forgiving_scope wear_charge (plain); tenure_addition none; low_mileage_addition none.
- charge_off_hold: stage_rate invoice_date (plain); relationship_relief none; returned_relief none; hold_shape invoice_date (plain).
- excess_mileage: all six none. end_installment_plan: all six none.

## Pairwise method-tier table
- forgiving_scope: (a) advance 43 days or adjusted item -> 2425.00 forgivable; (b) advance 10 days -> 1525.00; (c) none -> 625.00 (task 0 charges).
- hold_shape: (a) balance 1370.00 -> 712.08 shape; (b) balance 400.00 -> 400.00; (c) balance 900.00 -> 207.00 at rate 0.23.
- allowance_convention: (a) whole months 37 -> 37000; (b) by day 1129 days -> 37117; (c) standard 38000 (task 1 dates).
- first_shape: (a) 1863.09 -> 826.82; (b) 600.00 -> 600.00; (c) 1000.00 -> 111.11 over 9.

## Decoy / absent-record probe table (round 2, scratch probe)
- task 0: decoy active retail listed first (outside window, dpd 5) -> WF 425.00, hold relief 0 (rule reads the first listed); advance-report tire item -> WF unchanged (turn-in report only); dispute adjustment present -> whole-charge scope; excess mileage charge posted in the contact -> hold unchanged (invoiced balance), WF unchanged; waiver posted -> plan unchanged; no other products -> WF 225.00; no inspections -> no item left out; no invoice -> hold out of scope (compute evaluates, no crash).
- task 1: dispute adjustment without an assessed missing item -> count floored at 0; extra returned payment -> autopay 32 (>= 24), completion 37; waiver posted -> plan unchanged; no other products -> XM 2043.09; no inspections -> clean tier unchanged.

## Full gate block (round 2)
- check_extended: EXTENDED OK
- check_task_tools: TASK TOOL CONTRACT OK
- replay_tasks: REPLAY OK (0.json 13 acts, 1.json 14 acts)
- check_solvability: SOLVABILITY OK
- check_compute: COMPUTE OK (suite means branches 34.50, steps 13.50; history max 74; branches max 37)
- check_grounding: GROUNDING OK
- check_cross_fire: SCOPE OK
- check_cache_diff: INFO only
- check_traceability: 4 misses, all unlock tool_name provenance (KB not yet rendered)
REWORK round 2: gates 7/7 green

## REWORK round 3 closure (audit revision_2: R2-1, R2-2, R2-3, O2-T1-1, O2-T0-1)
- R2-1 -> lease_ext_wear_forgiveness: the dispute-gated scope factor (forgiving_scope) is removed. Its replacement method factor forgiveness_basis is (a) per item: advance inspection performed and more than the per-item threshold of excess items on the turn-in_final report; each item forgiven up to the per-item limit, together within the charge and the total limit. (b) Share of the charge: no advance inspection. (c) Aggregate: the standard case. Excess items are counted net of items removed on dispute. Every scheduled wear charge exceeds the per-item limit, so "each item up to the limit" is exactly count x limit. The baseline is now the aggregate standard method; repair_lead_days is removed and per_item_limit, per_item_threshold and forgiveness_share are added. Task 0's tree and edge are unchanged; its scored figures and the downstream hold figure were recomputed.
- R2-2 -> lease_ext_end_installment_plan replaced_by (both overwrites) now names the mileage case: for every other balance the charges are due end_of_term_payment_days after the invoice, except an excess mileage charge billed without an invoice, which falls due as the excess mileage rule states. The mileage rule's own sentence is unchanged and names the plan case, so one due date applies to each case.
- R2-3 -> plan scope now counts days since the due date exactly as the hold rule does (from the day after the due date through today; a due date not yet passed counts zero). Plan: no more than 30 days. Hold: more than 30. No gap or overlap.
- O2-T1-1 -> every rounding sentence in all four policies now reads "rounded to the nearest cent with a half cent rounded up". Every RND adds the param half_cent_guard (0.000001) so a binary half cent rounds up. Task 1's non-scored sensitivity figures moved to 843.02 / 966.55; no scored value moved.
- O2-T0-1 -> both design_rationale headers say "current through rework round 3". Task 0's rationale was rewritten to the current artifacts, with a revision-history paragraph.

## XF recipe check, round 3 (per policy x point)
| point | wear_forgiveness | charge_off_hold | excess_mileage | end_installment_plan |
|---|---|---|---|---|
| 1 assembly sentence generic, once | Y | Y | Y | Y |
| 2 order fixed (cap+additions = total limit, then basis; reliefs before rate; credits before comparison; installments before division, fee last) | Y | Y | Y | Y |
| 3 independence (scripted, transitive) | Y | Y | Y | Y |
| 4 ownership | Y | Y | Y | Y |
| 5 compute_basis verbatim (scripted) | Y 21/0 | Y 14/0 | Y 25/0 | Y 17/0 |
| 6 ties (latest dates; turn-in report first recorded) | Y | Y | Y | Y |
| 7 counting conventions | Y | Y | Y | Y (scope day count = hold's) |
| 8 every branch both ways | Y | Y | Y | Y |
| 9 base clauses scoped, siblings named (incl. the mileage due-date case) | Y | Y | Y | Y |
| 10 rounding sentence = RND placement (half cent up, guard) | Y | Y | Y | Y |
| 11 tools | Y | Y | Y | Y |
| 12 proof text re-synced | Y | Y | Y | Y |

## Factor-independence table, round 3 (scripted, transitive reads outside own bindings)
- wear_forgiveness: brand_return_cap none; punctual_addition none; forgiveness_basis wear_charge (plain); tenure_addition none; low_mileage_addition none.
- charge_off_hold: stage_rate invoice_date (plain); relationship_relief none; returned_relief none; hold_shape invoice_date (plain).
- excess_mileage: all six none. end_installment_plan: all six none.

## Pairwise method-tier table, round 3
- forgiveness_basis (charge 2425.00, limit 925.00, 9 items): (a) per item 900.00 vs (c) aggregate 925.00. With charge 1000.00: (b) share 500.00 vs (c) 925.00, and (a) per item 900.00 vs (b) 500.00.
- hold_shape: (a) 1395.00 -> 717.83; (b) 400.00 -> 400.00; (c) 900.00 -> 207.00.
- allowance_convention: (a) 37000; (b) 37117; (c) 38000.
- first_shape: (a) 1863.09 -> 826.82; (b) 600.00 -> 600.00; (c) 1000.00 -> 111.11.

## Decoy / absent-record probe table, round 3
- task 0, wear forgiveness:
  - no retail -> 225.00
  - retail 12 days past due -> 675.00 (halfway cap)
  - retail dated 95 days after turn-in -> 425.00
  - retail pending_funding -> 425.00
  - decoy active retail listed first, outside the window -> 425.00 (first-listed read stated in the rule)
  - no advance inspection -> 925.00 (share basis)
  - no inspections -> 925.00
  - four items removed on dispute -> 925.00 (5 counted, aggregate)
  - an item recorded on the advance report -> 900.00 (not counted)
  - a mileage charge posted during the contact -> unchanged
- task 0, hold payment:
  - a mileage charge posted during the contact -> unchanged
  - no invoice -> outside the hold scope; compute evaluates
- task 1, excess mileage:
  - no other products -> 2043.09
  - decoy active pre-owned listed first, outside the window -> 1813.09
  - Care paid in cash -> 1583.09
  - Care cancelled -> 1698.09
  - one returned payment -> 1468.09
  - pull-ahead mid-extension -> 1495.00
  - under the allowance -> 0.00 (no charge billed)
- task 1, installment plan:
  - a waiver posted during the contact -> 826.82 (unchanged)
  - one returned payment -> 858.02
  - no balloon -> 863.83

## Full gate block (round 3)
- check_extended: EXTENDED OK
- check_task_tools: TASK TOOL CONTRACT OK
- replay_tasks: REPLAY OK (0.json 13 acts, 1.json 14 acts)
- check_solvability: SOLVABILITY OK
- check_compute: COMPUTE OK (suite means branches 35.00, steps 13.50; history max 74; branches max 37)
- check_grounding: GROUNDING OK
- check_cross_fire: SCOPE OK
- check_cache_diff: INFO only
- check_traceability: 4 misses, all unlock tool_name provenance (KB not yet rendered)
REWORK round 3: gates 7/7 green

## REWORK round 4 closure (renderer stop report audits/render_source/lease_end_servicing/render_r1.md)
- Mismatch 1 (qualifying account number tie) -> lease_ext_wear_forgiveness rule: when the cap is the loyalty cap or the halfway cap, the waiver carries the account_number of the contract that meets that cap's conditions. An active new-vehicle retail contract takes precedence over an active balloon contract when both meet them. At the fall-through cap the qualifying account number is left empty. Task 0's argument (the only active retail contract, loyalty tier) is unchanged and its tracing now quotes the new sentence.
- Mismatch 2 (rule vs docstring) -> post_wear_forgiveness_925a15e3 qualifying_account_number now reads "the qualifying account number the wear forgiveness rule names for this waiver ... or an empty string when the rule names none". Rule and docstring now say the same thing for every tier.
- Mismatch 3 (retired clause conditioned an in-force waiver) -> overwrite[1] superseded_clause narrowed to "loyalty_wear_forgiveness_cap replaces wear_forgiveness_cap". "When the loyalty condition is met" stays in force for the loyalty disposition waiver.
- Mismatch 4 (replaced_by deferring to the retired clause), swept across every overwrite:
  - Hold tail now ends "... is charged off."
  - Plan tails (both overwrites) now end "... is charged off."
  - Mileage invoice tail now reads "an end-of-term invoice is mailed when any other end-of-term charge is billed".
  - Mileage scope tail now reads "every other end-of-term charge keeps the amount the base rule gives it" (amounts only; no retired clause).
  - The wear forgiveness scope tail names only unretired base clauses (the wear charge, the disposition fee and its loyalty waiver).
  - No replaced_by contains "as the base rule states".
- Placement note -> end_balance (hold) and plan_balance (plan) are now plain standard-method bindings, matching where baseline.rule defines them. hold_shape and first_shape keep their own ledger reading (shape_balance / shape_plan_balance) for their tier tests and use the plain balance for the amounts. No figure moved.
- Policy revision_3 PASS kept: no ladder, factor, edge, scope, seed or scored value changed.

## XF recipe check, round 4: unchanged from round 3 (all Y), re-verified:
- point 5: compute_basis sweep 21/15/25/18 quotes, 0 misses;
- point 9: every replaced_by restates its retired clause for out-of-scope cases, names its sibling's case, and defers to no clause it retires;
- point 11: docstring and rule agree on the qualifying account number;
- point 3: independence re-scripted (hold_shape reads plain end_balance and invoice_date; first_shape reads plain plan_balance; all other factors read only their own bindings).

## Pairwise method-tier and probe tables, round 4
Figures are unchanged from round 3 (the edits are textual and binding placement only); check_compute recomputed every expected, factor_sensitivity and baseline_result figure unchanged.

## Full gate block (round 4)
- check_extended: EXTENDED OK
- check_task_tools: TASK TOOL CONTRACT OK
- replay_tasks: REPLAY OK (0.json 13 acts, 1.json 14 acts)
- check_solvability: SOLVABILITY OK
- check_compute: COMPUTE OK (suite means branches 35.00, steps 13.50; history max 74; branches max 37)
- check_grounding: GROUNDING OK
- check_cross_fire: SCOPE OK
- check_cache_diff: INFO only
- check_traceability: 4 misses, all unlock tool_name provenance (KB not yet rendered)
REWORK round 4: gates 7/7 green

## REWORK round 5 closure (audit revision_4: R4-1, proof text only)
- R4-1 member 1 -> task 0 design_rationale [Route-around, declared] now quotes the narrowed retired clause "loyalty_wear_forgiveness_cap replaces wear_forgiveness_cap" and notes that "When the loyalty condition is met" stays in force for the loyalty disposition waiver. The hold tail is restated as in the charter, with no "stays under the base rule".
- R4-1 members 2-3 -> both design_rationale headers read "current through rework round 5".
- Sweep (scripted over every string field of both tasks except initial_state): no other text made stale by round 4. The task 1 route-around paragraph was re-synced to the restated plan, invoice and scope tails. Tracing, closure, plumbing and trace arithmetic are unchanged and recompute.
- lease.extended.yaml and task_tools.py untouched (sha256 7e29b687e1161ed2... and 03a0ed5a4a388aa1... unchanged from round 4); no scored value, factor, edge, scope or seed changed. XF table, independence, pairwise and probe tables are as recorded for round 4.

## Full gate block (round 5)
- check_extended: EXTENDED OK
- check_task_tools: TASK TOOL CONTRACT OK
- replay_tasks: REPLAY OK
- check_solvability: SOLVABILITY OK
- check_compute: COMPUTE OK (suite means branches 35.00, steps 13.50; history max 74; branches max 37)
- check_grounding: GROUNDING OK
- check_cross_fire: SCOPE OK
- check_cache_diff: INFO only
- check_traceability: 4 misses, all unlock tool_name provenance (KB not yet rendered)
REWORK round 5: gates 7/7 green

## REWORK round 6 closure (KB audit source items, audits/policy_kb/lease_end_servicing/)
- SRC-1 -> lease_ext_charge_off_hold rule and baseline.rule: the invoiced balance now subtracts "every end-of-term charge waiver, security deposit application and end-of-term payment posted on the lease, a waiver of a term fee such as a late charge not being taken off". That is exactly what end_balance and shape_balance subtract (lease_end_charge_waiver, lease_security_deposit_applied, lease_end_of_term_payment). The compute_basis quotes were updated with the sentence.
- Class sweep found no other mismatch (every "every/any/all ... waiver/payment/charge/fee" phrase in all four rules was checked against its compute):
  - The plan balance subtracts only the deposit applied and end-of-term payments, and states that waivers are not taken off.
  - Wear forgiveness reads only the excess wear charge.
  - The mileage credits count lease_payment rows filtered as stated, and returned payments on the lease.
- SRC-2 (base parameter glosses; BLUEPRINT-KNOWN, base untouched) -> lease_ext_wear_forgiveness rule now states "The tier's wear_forgiveness_cap and loyalty_wear_forgiveness_cap enter wear forgiveness only as this cap schedule assigns them; meeting the loyalty condition alone does not put the loyalty cap in place."
- No compute, factor, edge, scope, tool, seed or scored value changed. Both rationale headers now say "current through rework round 6", with a round-6 note. XF points re-checked: 5 (quote sweep, 0 misses), 8 and 9 unchanged; independence, pairwise and probe tables as recorded in round 4.

## Full gate block (round 6)
- check_extended: EXTENDED OK
- check_task_tools: TASK TOOL CONTRACT OK
- replay_tasks: REPLAY OK
- check_solvability: SOLVABILITY OK
- check_compute: COMPUTE OK (suite means branches 35.00, steps 13.50; history max 74; branches max 37)
- check_grounding: GROUNDING OK
- check_cross_fire: SCOPE OK
- check_traceability: TRACEABILITY OK (KB now published)
- check_cache_diff: INFO only
REWORK round 6: gates 8/8 green
