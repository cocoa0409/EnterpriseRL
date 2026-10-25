# worklog — installment_billing_and_fees (billing), M=2

## Step 0 — difficulty pre-check
- Draw (`draw_counts.py --tasks 2`):
  - task 0: prerequisite_problems 1, factor_counts [6, 5]
  - task 1: prerequisite_problems 2, factor_counts [5, 5, 4]
- Base read: billing.yaml (14 policies), blueprint difficulty claim (14 event types). Automatic clauses that could
  ignite uncarried obligations: past_due transition (-> billing_delinquency_cured, and the owner term's notice of
  cancellation for nonpayment), returned-draft count reaching 2 (-> recurring authorization revoked + plan switch),
  fee-bearing returns across plans reaching 2 (-> certified funds flag), invoice issue date reached (-> installment
  invoice + its installment fee), late fee after grace, NSF fee on a fee-bearing return, agent-assisted fee on any
  agent_phone payment of a direct-bill plan, paid-off balance with no installment left (-> paid_in_full, unclaimed).
- Global world rules adopted for both tasks: plan never past_due; at most one returned draft in the term; at most
  one fee-bearing return in the lookback; phone payments only on Monthly EFT / Monthly Card Autopay plans
  (agent_assisted_payment_fee 0.00); no payoff; every invoice whose issue date has passed is on the plan (except
  the one a task issues).
- Events written by my tools and their base triggers (XF14): billing_installment_billed -> billing:billing_installment_fee
  (the notice tool books that fee row itself, same category); billing_installment_fee []; billing_payment_received [];
  billing_nsf_fee []; billing_late_fee []. None lands in another category.

## Scope plan (principle C)
- task 0 (2 problems): Monthly Card Autopay, GA owner term, a driver added mid-term.
  root `billing_ext_endorsement_deposit` (user payment, 6 factors) <- `billing_ext_draft_notice` (agent, 5 factors),
  value_input (the deposit is a share of the endorsement balance not yet billed on a notice).
- task 1 (3 problems): Monthly EFT, FL owner term, a returned automatic draft past the grace period.
  root `billing_ext_returned_draft_makeup` (user payment, 5) <- `billing_ext_returned_item_fee` (agent, 4)
                                                             <- `billing_ext_late_fee_schedule` (agent, 5)
- Tools: issue_draft_notice_1682239d (agent), authorize_endorsement_deposit_3483f9bd (user; its uuid was generated fresh
  for this name), charge_returned_item_fee_652d204f (agent), assess_late_fee_1fdc5cae (agent), authorize_makeup_payment_1af63ac0 (user).
  (Corrected in round 2: an earlier draft of this line named a placeholder tool that was never written anywhere.)

## Task 0 — closed (per-task gates)
- Final tool names: issue_draft_notice_1682239d (agent), authorize_endorsement_deposit_3483f9bd (user; uuid generated
  fresh for this name, replacing the unused authorize_notice_payment_f4e44772 which was never written anywhere).
- Revisions: (1) solvability red "dedup object_bindings name absent current action arguments ['related_invoice_id']"
  -> root cause: notice subject listed billing_installment_fee, whose one_fee_per_invoice gate binds an argument the
  notice tool cannot have (it creates the invoice) -> subject narrowed to billing_installment_billed (the fee row is
  that event's declared trigger, written by the same tool); billing_installment_fee_rule stays in base_policy_refs for
  the fee overwrite. (2) "caller_statement correlation group must bind caller values" on
  billing_payment_posting.customer_authorizes (its only correlation key is billing_plan_id, a uuid a caller cannot
  state) -> routed around with a declared, scoped overwrite (d_auth) restating the authorization for every other
  payment. (3) dangling FK for '' ids -> empty *_id seed fields written as null.
- Capability cards: issue_draft_notice — agent, plan, creates one installment invoice dated today + its installment
  fee charge + plan balance += fee; receipt: invoice id, fee id, installment, due date, amounts, balance.
  authorize_endorsement_deposit — user, plan, creates one payment (agent_phone channel, linked to the additional premium
  txn, no invoice) + plan balance -= amount; receipt: PMT confirmation, payment id, amount, method, date, balance.
- Gate run 1 (task 0): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK.
- Numbers: notice 326.53 (factor baselines 251.76/328.03/327.53/326.03/325.78, all-baseline 253.01);
  deposit 119.63 (74.77/104.68/112.16/112.16/112.16/112.16, all-baseline 29.91); deposit with notice skipped 112.15.

## Task 1 — closed (per-task gates)
- Scope: billing_ext_returned_item_fee (charge_returned_item_fee_652d204f, agent, 4 factors),
  billing_ext_late_fee_schedule (assess_late_fee_1fdc5cae, agent, 5), billing_ext_returned_draft_makeup
  (authorize_makeup_payment_1af63ac0, user, 5). Disjoint from task 0's policies/tools.
- World: Marisol Bautista, CPA-FL-1427736 (Minimum Limits, FL, term 1, 9 points), Monthly EFT BP-13865204; the
  2026-09-14 draft (209.93) returned 2026-09-16 account_closed; frozen 2026-09-21 10:05:00 EDT (grace ended 09-19).
- Numbers: returned-item fee 40.00 (baselines 35.00/37.50/35.00/37.50, all 25.00); late fee 9.40
  (11.00/11.40/7.90/8.40/8.90, all 10.00); makeup 510.68 (305.50/490.16/500.42/500.42/505.55, all 259.33);
  makeup without the fee 470.68, without the late fee 501.28; leaves commute (9.40 / 40.00 either order).
- Revisions: (1) check_extended red "policy_source carries code token(s) nsf_fee_return_reasons / late_fee_grace_days"
  -> prerequisite sentences reworded into business words ("a return reason that carries a returned-item fee",
  "unpaid past the end of its grace period") in rule and edge. (2) check_compute red "history is NOT load-bearing"
  for the fee and late fee -> root cause: the fee read only LATEST (not zeroed by the gate) and the late fee's
  paid/returned sums cancel -> returned amount now the SUM of returns against the original payment; the late-fee
  credit tests the COUNT of returns against the last payment. (3) replay closure mismatch (3 unread rows) -> added
  find_auto_premium_transactions and find_billing_authorizations reads, each with its necessity; steps shifted to 9/11/13.
- Capability cards: charge_returned_item_fee — agent, plan, one billing_nsf_fee row linked to the returned payment +
  balance += fee; assess_late_fee — agent, plan, one billing_late_fee row linked to the invoice + balance += fee
  (billing_invoice_id and related_invoice_id are both required by the base gates' action_bindings: after_grace binds
  billing_invoice_id, one_late_fee binds related_invoice_id; both carry the same invoice); authorize_makeup_payment —
  user, one billing_payment_received row (agent_phone, linked to the invoice the draft paid) + balance -= amount.

## Events written (XF14) — base triggers
| tool | event(s) | base triggers | lands in |
|---|---|---|---|
| issue_draft_notice_1682239d | billing_installment_billed + billing_installment_fee | -> billing:billing_installment_fee; [] | billing |
| authorize_endorsement_deposit_3483f9bd | billing_payment_received | [] | billing |
| charge_returned_item_fee_652d204f | billing_nsf_fee | [] | billing |
| assess_late_fee_1fdc5cae | billing_late_fee | [] | billing |
| authorize_makeup_payment_1af63ac0 | billing_payment_received | [] | billing |

## Probe table (XF8; scratch copies, /tmp evaluator over check_compute primitives)
| policy | probe | result |
|---|---|---|
| draft notice | absent additional premium | 251.76 (share 0) |
| draft notice | decoy AP 999 on another (expired, TX) owner term | 326.53 (excluded by auto_policy_id key) |
| draft notice | return exactly 12 months before notice date | 326.53 (not counted: MONTHS = 12) |
| draft notice | return 11 months 29 days before | 328.53 (counted: fee +1.00 instead of -1.00) |
| draft notice | plan with no owner term (out of scope) | evaluates, no error (CFIELD None guarded with `or 0`) |
| deposit | no driver-added change (vehicle endorsement) | 82.25 (age/points/window/relation guards -> 0) |
| deposit | second driver added the same date (decoy, 1960 spouse) | 119.63 (XLATEST keeps the first recorded) |
| returned-item fee | reason insufficient_funds | 35.00 |
| returned-item fee | Georgia term | 40.00 (max(30, 10.50) base) |
| returned-item fee | return on day 90 exactly | 42.50 (<= 90 tier) |
| late fee | bank_error return | 7.40 (credit 4.00) |
| late fee | no return (paid invoice; not eligible anyway) | 3.00 core 0 (eligibility excludes it) |
| makeup | insufficient_funds (account still draftable) | 305.50 (no advance core) |
| makeup | next installment already invoiced | 515.43 (its minimum due less payments) |
Zero division: the only divisions are by unbilled_count / collect_unbilled inside tiers that require >= 2 (or == 2).

## Pairwise method-tier table (XF10)
| factor | tier A | tier B | tier C | pairs |
|---|---|---|---|---|
| endorsement_spread | balance / unbilled count | whole balance | none | A-B adds an input; B,C: B > 0 on its domain -> PASS |
| deposit_core_by_installments_left | whole balance | balance / unbilled count | MN(balance, MX(pct x balance, min_deposit)) | B adds an input; C adds min/max + parameter -> PASS |
| state_returned_item_base | FL: band selected by returned amount, MX with pct x amount | GA: MX(flat, pct x amount) | plan nsf_fee | A data-selected band; B adds max + amount input -> PASS |
| unpaid_amount_core | pct x unpaid | MN(late_fee, pct x unpaid) | late_fee | B adds min + parameter; C drops the unpaid input -> PASS |
| undraftable_account_advance | next scheduled premium (schedule) | next invoice minimum due less payments (record) | none | different inputs; A,B > 0 on their domain -> PASS |

## Realism notes (honest)
- Natural/real: endorsement premium spread over unbilled installments; endorsement deposit tied to the remaining
  installments; Florida banded returned-item amounts and Georgia greater-of-flat-or-5% (mirroring those states'
  returned-check service-charge statutes, stated here as the company's own schedule); late fee as the lesser of the
  flat fee and a percentage of the unpaid installment; reduced late fee when an NSF fee already applies; advance of
  the next installment when the drafted account is closed or stopped.
- Company schedules by state / package / rated points / new-business timing / driver age, points and relationship are
  explicitly the company's own fee and deposit schedules; they are the parts most exposed to a realism audit.
- Blueprint route-arounds (base frozen): billing_payment_posting.customer_authorizes binds only billing_plan_id under
  caller authority (a caller cannot state a uuid) -> retired per payment type by two sibling overwrites that restate it
  and name each other's case; billing_late_fee_rule gates need two invoice arguments on the late fee tool.

## Final gate run (difficulty level, no --task)
EXTENDED OK; TASK TOOL CONTRACT OK; REPLAY OK; SOLVABILITY OK; COMPUTE OK (suite means branches 48.00, steps 13.50;
history_rows_max 12; branches_max 53); GROUNDING OK; SCOPE OK; CACHE-DIFF INFO (optional). check_traceability not
run: the KB is not rendered yet. erlbench validate_scenario: only "required document ... not found" (KB pending).
INSTANTIATE round 1: gates 7/7 green

## Round 2 rework (audits/policy_task/installment_billing_and_fees r1: CG-1..CG-12, task findings)
Scratch generators were rebuilt (round-1 scratch had been deleted): one module per policy, an assembler that asserts every
compute_basis quote, baseline sentence, replaced_by and policy_source is verbatim in its rule and every superseded_clause is
verbatim in its base rule, world builders that reuse the round-1 row ids, and task builders that regenerate every proof text.

Policy changes (charter-wide, whole class):
- draft notice: overwrite of billing_installment_schedule S3 declared and scoped (CG-1); state and violation-points fee
  factors struck (CG-10a, coordinator: no garaging-state/points billing fee); credit_carry (base S5: credits reduce the
  next installments nearest first) and installment_size_charge (lesser of the plan fee and a percentage on mid-size
  installments vs a percentage on small ones vs the flat fee) added; baseline now silent about credits.
- endorsement deposit: application overwrite rewritten so a deposit is a credit on the installments not yet invoiced,
  exactly what credit_carry applies on every later notice (CG-2); balance net of a credit already held (O-7); deposit
  capped at the balance, none taken on a zero balance (CG-12); core method tiers now whole / balance divided by the 2-3
  installments left (data-selected divisor) / standard pct with floor and cap (CG-8); installment count moved out of the
  baseline (CG-3); prerequisite sentence widened to "invoiced ... or covered in full by the plan's credit" (no deadlock).
- returned-item fee: the Florida/Georgia statutory amounts are now a ceiling the total can never exceed (CG-11), the
  method factor is the statutes' percentage charge for large items / the item itself for tiny items / the plan fee;
  channel, reason, new-business and package additions stay below the ceiling; non-owner wording added (CG-6).
- late fee: state and points additions struck (CG-10a); 4 factors (core, returned-payment credit, package, new business);
  object = the invoice the latest returned payment paid, else the latest invoice, same-day ties stated (CG-5, CG-7);
  floor late_fee_min so a waited-on entry is never 0.00 (XF20); non-owner wording (CG-6).
- makeup: state advance struck (CG-10b); returned_payment_recollection (re-collect only what the invoice still owes when
  the returned payment had also prepaid) added; both prerequisite sentences narrowed to the returned payment the makeup
  makes good and the invoice it had paid, which are exactly the objects the fee policies price (CG-7); next-installment
  premium kept out of the baseline, baseline.params emptied to match the baseline paragraph (CG-3, CG-9); capped at the
  account balance.
- Every combination sentence rewritten generically (CG-4); month-end convention stated once for every whole-month count (CG-5).

World changes: task 0 adds a 50.00 online payment on 2026-11-30 (a credit the notice carries) and every installment fee
follows the new schedule; task 1's installment 3 was paid by a 560.00 online bank payment from the account that was then
closed (returned 2026-09-16, account_closed), drafts 1-2 unchanged, fees follow the new schedule. Gold values moved.

Probe table (round 2, scratch copies):
| policy | probe | result |
|---|---|---|
| billing_ext_draft_notice | decoy: second (closed, prior-term) plan with invoice and return | 276.22 |
| billing_ext_draft_notice | absent: no additional premium | 201.45 |
| billing_ext_draft_notice | boundary: return exactly 12 months before (not counted) | 276.22 |
| billing_ext_draft_notice | boundary: return 11 months 29 days before (counted) | 278.22 |
| billing_ext_draft_notice | non-owner plan (out of scope; evaluates without error) | 422.9 |
| billing_ext_draft_notice | credit 450 >= scheduled premium (carry 247.01) | 79.21 |
| billing_ext_endorsement_deposit | decoy: second plan | 119.63 |
| billing_ext_endorsement_deposit | absent: no driver-added change | 82.25 |
| billing_ext_endorsement_deposit | tie: second driver added same date (first recorded kept) | 119.63 |
| billing_ext_endorsement_deposit | non-owner plan (out of scope; evaluates) | 0.0 |
| billing_ext_returned_item_fee | decoy: second plan with a later return | 39.0 |
| billing_ext_returned_item_fee | GA: ceiling max(30, 28) = 30 caps 39 | 30.0 |
| billing_ext_returned_item_fee | VA: no percentage charge, ceiling nsf_fee 25 | 25.0 |
| billing_ext_returned_item_fee | tiny item 20.00 (fee figured as 20.00 + adds, FL band 25 caps) | 25.0 |
| billing_ext_returned_item_fee | return on day 90 exactly (<= 90 tier) | 40.0 |
| billing_ext_returned_item_fee | non-owner plan (ceiling nsf_fee 25) | 25.0 |
| billing_ext_late_fee_schedule | late: bank_error return credit 1.50 | 8.62 |
| billing_ext_late_fee_schedule | late: no return (latest invoice, paid; floor 1.00) | 1.0 |
| billing_ext_late_fee_schedule | late: later invoice issued (still the returned payment's invoice) | 9.12 |
| billing_ext_late_fee_schedule | late: non-owner plan | 7.37 |
| billing_ext_returned_draft_makeup | makeup: insufficient_funds (no advance) | 298.34 |
| billing_ext_returned_draft_makeup | makeup: next installment already invoiced | 507.52 |
| billing_ext_returned_draft_makeup | makeup: returned payment paid no invoice (re-collect 0) | 39.0 |
| billing_ext_returned_draft_makeup | makeup: returned amount = invoice minimum (re-collect returned amount) | 503.52 |
| billing_ext_returned_draft_makeup | makeup: non-owner plan | 463.46 |
| billing_ext_endorsement_deposit | credit equal to the endorsement balance once notice 3 is paid | 0.0 (no deposit taken) |
| billing_ext_endorsement_deposit | credit 60 standing once notice 3 is paid | balance 89.54, deposit 71.63 |
Zero division: divisions only by unbilled counts inside tiers that require >= 2. None reads guarded (`or 0`, `!= None`).

Pairwise method-tier table (round 2):
| factor | tier A | tier B | tier C | verdict |
|---|---|---|---|---|
| endorsement_spread | balance / unbilled count | whole balance | none | A adds a data input; C is 0 only where no balance -> PASS |
| credit_carry | MN(credit, scheduled premium) | whole credit | none | A adds a min with another input -> PASS |
| installment_size_charge | pct x premium | MN(plan fee, pct x premium) | plan fee | B adds min + tariff; C drops the premium input -> PASS |
| deposit_by_installments_left | whole balance | balance / unbilled count (2 or 3, data) | MN(balance, MX(pct x balance, min_deposit)) | B data divisor; C floor and cap -> PASS |
| returned_amount_charge | the returned amount | MX(plan fee, pct x amount) | plan fee | each a different input/operation -> PASS |
| unpaid_amount_core | pct x unpaid | MN(late_fee, pct x unpaid) | late_fee | PASS |
| returned_payment_recollection | invoice minimum less payments plus returned amount | none | returned amount | different inputs -> PASS |
| undraftable_account_advance | next scheduled premium | next invoice minimum less payments | none | different inputs -> PASS |
REWORK round 2: gates 7/7 green

## Round 3 rework (audits/policy_task/installment_billing_and_fees/ revision_2)

Read 0.md, 1.md and _difficulty.md in full. Items closed one by one; base (blueprint/) untouched; all departures from base go through scoped overwrites.

### Item closures
- CG-16 (XF 23 realism bar): struck package_fee_tier, package_late_addition, package_returned_item_addition, package_makeup_advance, new_business_late_addition, new_business_return_addition, new_business_makeup_advance, points_makeup_advance and return_reason_addition; no new add-ons put in their place. To keep honest factor counts the computations changed within the claimed events, not the factor list:
  - notice: endorsement spread and credit spread both work on premium the plan carries; the installment fee became the installment-size charge (percentage of the installment premium, banded by size), the way a filed installment fee schedule works.
  - returned-item fee: amount charge (Florida/Georgia percentage charge), channel, payment plan, return history, return timing.
  - late fee: unpaid-amount core, returned-payment credit, autopay standing, payment channel.
  - makeup: re-collection and undraftable-account advance (methods) plus filing, payment-plan and returned-amount percentages of the returned amount.
- CG-17: statutory ceilings now cited only where the statute is known (Florida banded amounts or 5%, Georgia greater of 30.00 or 5%, Texas 30.00 processing fee). Virginia, Ohio, Arizona and non-owner plans carry the company's own fee with no statutory claim.
- CG-13: credit_carry struck. credit_spread has three shapes (an equal share of the credit across the unbilled installments; the credit up to the scheduled premium plus fee when only one is left; otherwise the standing balance). The departure from base S5 is declared by a scoped overwrite of billing_installment_schedule S5 for draft notices only.
- CG-14: one reading of "covered in full". The deposit says it is fixed "only after every installment whose invoice date has arrived is invoiced on the plan", and its credit is "the amount by which its account_balance falls short of the premium not yet billed on any invoice plus what its most recent installment invoice still owes".
- CG-15: the makeup tool now writes related_payment_txn_id on its payment row. The late fee object is the invoice paid by the payment most recently returned, while no payment referencing that returned payment has made it good; otherwise it is the latest installment invoice. So the late fee keys on a record tied by exact value.
- CG-3r: the makeup percentages apply to the returned amount, which is a baseline quantity. The next-installment bindings (adv_*) belong only to undraftable_account_advance, so no quantity is shared only among factors.
- CG-4r: the combination sentence is generic. Re-collection replaces the returned amount, the advance adds its figure, each other schedule adds its percentage of the returned amount, none acts on another's result, and the total is capped at the account balance and rounded once. It does not name the next installment's premium.

### Probes (scratch copies only)
| probe | task | outcome |
|---|---|---|
| decoy return on another customer's plan | 1 | fee / late / makeup unchanged (plan-scoped) |
| no authorization in force | 1 | payment-plan tiers flip (direct bill); every amount moves |
| return reason insufficient_funds | 1 | undraftable advance falls away; fee and late fee unchanged |
| garaged TX / VA / OH / AZ | 1 | plan nsf_fee used, no percentage charge; TX under its 30.00 cap; VA/OH/AZ no statutory claim |
| garaged GA | 1 | percentage charge; Georgia ceiling (greater of 30.00 or 5%) binds |
| makeup posted referencing the return, invoice 4 later unpaid (CG-15) | 1 | late object moves to invoice 4; invoice 3 is not priced again |
| extra 400.00 credit (CG-13) | 0 | equal-share credit spread per the scoped S5 overwrite; deposit credit absorbs the deposit to zero |
| no authorization in force | 0 | autopay fee standing flips; deposit unchanged |
| leaves in either order | 1 | late fee and returned-item fee commute (recorded in prerequisite_closure) |

### Pairwise method shapes (XF method-shape test)
| factor | input | operation | baseline | verdict |
|---|---|---|---|---|
| endorsement_spread | endorsement balance | split across unbilled installments | none | PASS |
| credit_spread | credit held | credit / n; MN(credit, sched + fee); standing | standing balance | three distinct shapes, PASS |
| installment_size_charge | installment premium | percentage banded by size | plan installment_fee | PASS |
| returned_amount_charge | returned amount | MX(nsf_fee, pct x amount) / amount itself | plan nsf_fee | PASS |
| unpaid_amount_core | unpaid amount | MN(late_fee, pct x unpaid) | late_fee | PASS |
| returned_payment_recollection | invoice minimum less payments plus return | replace returned amount | returned amount | PASS |
| undraftable_account_advance | next scheduled premium | add | none | PASS |

### Sweep
Proof, rationale, closure, tracing and compute_basis quotes were re-rendered from the round-3 rule text. No struck factor id, credit_carry or mk_next_sched is left in the bundle. Factor baseline lists in the rationales are written out in plain words.
REWORK round 3: gates 7/7 green

## Round 4 rework (audits/policy_task/installment_billing_and_fees/ revision_3; XF_recipe point 24)

Read 0.md, 1.md, _difficulty.md (revision_3 sections in full) and XF_recipe.md points 1-24. Base (blueprint/) untouched; every departure from base goes through a scoped overwrite that names its siblings.

### Item closures
- CG-16r / point 24: the returned-item fee and late fee policies, and their two tools, are removed. The NSF fee (25.00) and the late fee (10.00) are the plan's flat base charges, and task 1's world seeds them as system postings. Task 1 is re-treed onto three computations built from premium the plan carries, all inside the claimed events (billing_payment_received, billing_plan_switched, billing_installment_billed, billing_recurring_payment_revoked, billing_installment_fee). No fee is computed from padded keys.
  - billing_ext_returned_draft_makeup (user, 5): kept. Its fee prerequisites are gone; the fees owed are plain sums of the posted NSF and late fees.
  - billing_ext_switch_down_payment (user, 5, new; tool authorize_switch_down_payment_5d76e7dc).
    - The Six-Pay Direct Bill Plan's down payment percentage is refigured for a move off automatic draft.
    - Basis (method), by how far the term has been invoiced: as if enrolled / percentage of the scheduled premium not yet invoiced / none when one installment is left.
    - Additions on rating-plan keys:
      - a returned payment (higher down payment);
      - violation points tier;
      - liability package;
      - garaging state, under the company's own state schedule, with no statute claimed.
  - billing_ext_direct_bill_switch (agent, 4, new; tool switch_to_direct_bill_b1ddc0c4). Moves the plan to Six-Pay Direct Bill, records the revocation and issues the first invoice after the move. Its premium is the unpaid scheduled premium spread again (less the switch down payment), and it carries:
    - endorsement share (method);
    - credit carried from the makeup's advance (method);
    - direct-bill installment fee by the company's state schedule (point-24 key: state);
    - SR-22/FR-44 certificate fee (flat per form, keyed on the term's stamp).
- CG-15r: the late fee object selection no longer exists. The move's own wait is "the installment invoice that the payment most recently returned on it had paid is paid again in full". That is a record test that any cure satisfies, whether the makeup or an ordinary payment against that invoice, so it cannot go stale or deadlock (probe below).
- CG-18: there is now exactly one application of an ordinary payment on owner plans. It is declared once, as a scoped overwrite of billing_payment_posting's application sentence in billing_ext_draft_notice:
  - a payment goes to past-due invoices, then fees, then the current invoice;
  - whatever it leaves is held as a credit, which later invoices carry by their own credit schedules;
  - endorsement deposits and switch down payments are held as their own schedules state;
  - the base order is restated for other plans.
  The deposit's own application overwrite is removed, and the deposit and makeup rules now point to that single application. The notice's S5 overwrite says the same thing (a credit is carried onto later invoices by their own credit schedules, and every installment is invoiced).
- CG-19: every factor that named the certificate form from fr_filings.variant_name now keys on the term's financial_responsibility_filing stamp, read honestly as the source. This covers the notice's certificate_fee_billing (sr22_certificate_fee / fr44_certificate_fee), the makeup's filing_status_advance and the new direct_bill_certificate_fee. Only the fee timing (assessed after the latest invoice, not reversed) is read from the fr fee ledger. The cross-difficulty and multi-source floors still hold in both tasks.
- Task 0 rationale date: the certificate was requested 2026-11-25 and filed 2026-11-26, with the fee assessed 2026-11-25. The criteria objective, the tracing and the factor trace were re-worded to the stamp. Task 0's scored values are unchanged (notice 310.72, deposit 55.63).
- O-13: the certificate-fee sentences now state that a fee assessed on an invoice's own date is billed on that invoice.

### Task 1 tree (revision 4)
Root billing_ext_direct_bill_switch. It waits, by value_input and in state form, on:
- the makeup: invoice 3 must be paid again in full; the makeup's advance becomes the credit the first invoice carries;
- the switch down payment: a down payment beyond the enrollment one must stand; it is taken off the premium spread again.

The two leaves commute: the down payment reads no payment, and the makeup's balance cap is not reached in either order. Every edge bears weight: skipping either write changes the first invoice's minimum due (recorded in prerequisite_closure).

### Probes (scratch copies only)
| probe | outcome |
|---|---|
| second (expired) auto term of the customer with its own endorsement | no change: every auto read is keyed on the plan's own auto_policy_id |
| endorsement deposit row on the plan | not counted as a switch down payment; it is held as a credit and carried |
| certificate fee waived, or filing withdrawn | certificate fee falls to 0 |
| stamp fr44 / none | makeup filing advance 10% / 0; certificate fee 35.00 / 0 |
| garaging GA, TX, VA | down payment state addition 1.5 / 1.5 / 0; direct-bill fee 7.50 / 7.50 / 9.00 |
| violation points 3 / 4 / 8 | down payment addition 0 / 2.5 / 5 |
| package 50/100/50 | down payment addition 2.5 |
| no endorsement premium | endorsement share 0 |
| return older than 90 days | returned addition 2.5 |
| ordinary payment against invoice 3, no reference | the move's wait is met (no CG-15r-style stale wait) |
| one installment left / none invoiced | switch down payment 0 (not in the move's scope) / as-if-enrolled figure |

### Pairwise method shapes (new or changed methods)
| factor | tiers | verdict |
|---|---|---|
| down_basis_by_invoicing_progress | pct x scheduled premium not yet invoiced; nothing; pct x term premium less own down premium | different input in each tier: PASS |
| endorsement_respread_share | E/n (n from data); E; 0 | data divisor: PASS |
| switched_plan_credit_carry | -c/n; -min(c, respread + fee); standing balance | data divisor, min: PASS |
| returned_payment_recollection, undraftable_account_advance | unchanged from round 3 | PASS |

### Residual realism risks (declared)
- Garaging state keys two different charges: the switch down payment addition and the direct-bill installment fee. Both are items a company's state filing sets; neither claims a statute.
- The makeup still collects the next installment as an advance, because the drafted account is closed when it is taken. The move that follows carries that advance as a credit on the first invoice; nothing is lost or collected twice.

### Sweep
Every compute_basis quote, baseline sentence, replaced_by and policy_source was re-checked verbatim with a scratch script. Every superseded_clause is verbatim in its base rule. No factor id is a substring of a tool name. Task 0 and task 1 proofs, rationales, closures, tracing and factor_sensitivity tier texts were re-rendered from the round-4 rules. No returned-item fee, late fee schedule, old amount or old filing date is left in either task.
REWORK round 4: gates 7/7 green

## Round 5 rework (audits/policy_task/installment_billing_and_fees/ revision_4; XF points 25-26)

Read the revision_4 sections of _difficulty.md, 0.md and 1.md in full, and XF_recipe.md points 1-26. Base (blueprint/) untouched.

### Item closures
- CG-20: billing_ext_direct_bill_switch now overwrites base billing_returned_payments "A customer may also revoke a recurring authorization at any time; the plan then becomes the Six-Pay Direct Bill Plan for its remaining installments." The scope is an owner automatic-draft plan whose named insured asks to stop the drafts inside the move window: the revocation is recorded with the move once its waits are met. The base sentence is restated for every other customer.
- Task 1 hidden prerequisite: the persona now asks only to stop the drafts and be billed monthly, and says she does not know whether anything is owed. The makeup is found from the move's sentence (invoice 3 unpaid again after the return), so the makeup trigger is now state_due with an initial_state discriminator. request_alignment and no_user_hint were re-written.
- CG-21: the switch down payment is recorded toward the first installment not yet invoiced (the tool takes installment_number) with no invoice. The move's wait and sw_down_paid key on that exact value. An ordinary prepayment carries installment number 0 and is excluded (probe below).
- CG-22: one rule now covers invoices after the move.
  - The draft notice is scoped to Monthly EFT and Monthly Card Autopay owner plans. Its S3 and fee overwrites name "an invoice of an owner plan moved off automatic draft" as following its own schedule, which removes the XF11 carve-out its compute lacked.
  - The switch's S3, fee and billing_plan_switch overwrites cover every invoice of the moved plan. A "later invoice" sentence prices installments after the first: the premium still to bill after the move spread over the installments left, the state fee, the recorded certificate fee, and any credit carried whole.
- CG-23: the notice's installment fee is now the plan's installment_fee, unadjusted (plan and method as filed). autopay_fee_standing and installment_size_charge are removed. The switch keeps direct_bill_state_fee, a company state schedule and a point 24/25 publishable key that the auditor accepted.
- CG-24: certificate_fee_billing and direct_bill_certificate_fee are removed. Both invoices bill the fee recorded on the fr ledger as a plain binding (assessed after the latest invoice, not reversed). To keep the drawn counts on real keys, the notice gains three parameter factors and the switch one: percentages of the endorsement premium not yet billed, billed ahead on the bill being issued, under the company's own filed percentages. They are keyed on the term's certificate stamp, violation points and liability package (notice) and on the certificate stamp (switch). These are rating-plan dimensions on a premium-derived amount (point 23), and no recorded amount embeds them (point 26). What the schedules add never exceeds the endorsement premium not yet billed.
- CG-26: dn_left is removed. The installments-not-yet-invoiced count moved from the baseline paragraph into the basis factor's own sentence. A scripted unused-binding sweep is clean on all five policies.
- Seed consistency followed the fee change: task 0 invoices 1-2 fee 6.00 (Card Autopay plan fee), task 1 invoices 1-3 fee 4.00 (EFT plan fee), with drafted payments and balances recomputed.

### Probes (scratch copies only)
| probe | outcome |
|---|---|
| 100.00 online prepayment (installment 0, no invoice), makeup posted, no switch down payment | sw_down_paid 0.00; the move's wait unmet; the prepayment is carried as credit |
| task 1 stamp fr44 / none | makeup filing advance 10% / 0; first-invoice advance 10% / 0 |
| task 1 filing fee waived | certificate fee 0 on the first invoice |
| task 0 stamp fr44 / none; points 3 / 4; package Minimum / 100/300/50 | notice advance percentages move by tier |
| task 0 filing fee waived; recorded fee 35.00; fee dated the invoice day | notice bills 0; bills 35.00; bills 0 (billed on that invoice) |

### Pairwise method shapes
Unchanged method factors: endorsement_spread, credit_spread, deposit core, recollection, advance, down_basis_by_invoicing_progress, endorsement_respread_share, switched_plan_credit_carry. All PASS as tabled in rounds 3-4. The new factors are parameters.

### Sweep
Every compute_basis quote, baseline sentence, replaced_by, superseded_clause and policy_source was re-checked verbatim. No unused binding and no factor id inside a tool name. Both tasks' proofs, rationales, closures, tracing, factor traces and tier texts were re-rendered from the round-5 rules. No removed factor name or old amount is left.
REWORK round 5: gates 7/7 green

## Round 6 rework (audits/policy_task/installment_billing_and_fees/ revision_5)

Read the revision_5 sections in full. Charter-only items; both tasks had passed. Minimal edits: no scored value moved, and check_compute recomputes every expected figure unchanged.

### Item closures
- CG-27: removed the switch rule's sentence on later invoices. Later invoices of a moved plan are left to the base installment rule, restated in scope:
  - the switch's S3 overwrite now covers only the first invoice after the move;
  - its fee overwrite covers only the first invoice, and its state-fee sentence names the first invoice;
  - every replaced_by restates the base for "any other invoice, a later invoice of a moved plan included".
  The billing_plan_switch overwrite now says what later invoices bill under the base rule: the respread installment premium (scheduled premium not yet invoiced less the switch down payment, in equal shares, the last absorbing rounding), with the new plan's installment fee. The notice's sibling replaced_by sentences and its scope sentence now name "the first invoice after" a move.
- CG-28: the draft notice's S5 (credit) and payment-application overwrites are scoped to Monthly EFT and Monthly Card Autopay owner plans, the plans the notice prices. A credit still held at a move off automatic draft is carried onto the first invoice after the move by that invoice's own schedule, which is issued even when covered. Each replaced_by restates the base for every other plan, and for a moved plan after its first invoice:
  - credits reduce the next installments nearest first, and a covered installment is not invoiced;
  - payment_application_order applies, excess a credit.
  The deposit's application sentence carries the same scope: held whole as a credit on autopay plans, otherwise applied in payment_application_order as every other payment is.

### Probes
- Gate recomputation on both task worlds: notice, deposit, makeup, switch down payment and first invoice all unchanged (both task plans are EFT / Card Autopay, inside the narrowed scope).
- Scripted sweep: compute_basis quotes, baseline sentences, replaced_by, superseded_clause and policy_source all verbatim. No phrase of the removed later-invoice sentence ("premium still to bill", "every later one") remains.
- Task 0 and task 1 rationales were re-worded to the narrowed scopes.
REWORK round 6: gates 7/7 green

## Round 7 rework (audits/policy_task/installment_billing_and_fees/ revision_6)

Read the revision_6 sections in full. One charter-only item; both tasks had passed. Minimal edit, no scored value moved.

### Item closure
- CG-29: the endorsement deposit's scope sentence now covers only an owner term billed on a Monthly EFT or Monthly Card Autopay plan. Those are exactly the plans whose waited-on installment invoices the draft notice tool issues. A new sentence restates the base for every other plan: "An owner term billed on any other plan is outside this schedule: a payment toward its additional premium is taken as every other one-time payment is and applied in payment_application_order."

### Same-class check (every wait in the charter, against the plans in its policy's scope)
- Deposit -> notice ("every installment whose invoice date has arrived is invoiced"): scope is now autopay owner plans, and the notice tool issues those invoices. Closed.
- Switch -> makeup ("the installment invoice that the payment most recently returned on it had paid is paid again in full"): the switch's scope is EFT/Card owner plans inside the move window. The makeup tool posts against any owner-plan invoice. Producible.
- Switch -> switch down payment ("a payment recorded toward the first installment not yet invoiced and linked to no invoice"): the switch down payment's scope (EFT/Card owner plans moving to Six-Pay) covers the switch's scope, and inside the move window its figure is positive. Producible.
- The makeup, switch down payment and notice have no waits.

### Sweep
compute_basis quotes, baseline sentences, replaced_by and policy_source are verbatim (scripted). The task 0 rationale names the deposit's narrowed scope. The gate recomputation leaves every scored figure unchanged.
REWORK round 7: gates 7/7 green

## Round 8 rework (audits/render_source/installment_billing_and_fees/render_r1.md, pre-render scan)

Read render_r1.md in full. Minimal edits; every combination sentence keeps its order. No scored value moved: check_compute recomputes every expected figure unchanged.

### Item closures
- F1 (draft notice rounding): the combination sentence now states that the advance schedules' percentages are added together and applied once to the endorsement premium not yet billed, that advance being rounded half up to the cent once. This matches the single RND in compute. The rounding sentence now reads "Apart from the schedule's own figures (its down payment premium and scheduled installment premium), only the shares, the advance and the minimum due are rounded", which matches the RND on down_premium and scheduled_premium.
- F2 (makeup advance, returned payment linked to no invoice): the advance's no-advance tier now names that case ("when the returned payment had paid no installment invoice"), in both the rule and the factor ladder, exactly as compute prices it (0).
- F3 (deposit, what the latest invoice still owes): compute and words now both count a return. The rule reads "its minimum due less the payments posted against it plus the amount the bank returned against the most recent of those payments", and dep_latest_unpaid adds back the return of the latest payment against that invoice. This agrees with the base rule "the charges it had paid become unpaid again".
- F4 (makeup payment-plan tiers): the automatic-draft tier now requires installment_count above zero in words, ladder and compute. The Paid-in-Full Plan gets nothing whatever its authorizations, so the tiers are disjoint.
- Note (unused month definition): the whole-calendar-month sentence is removed from the draft notice, which reads no month count.

### Same-class sweep across all five policies
- Unused params, unused bindings and params not named in the rule: none (scripted).
- Overlapping tiers re-checked in every ladder; all are disjoint as stated.
- Rounding wording matches RND placement:
  - the makeup and switch down payment round once at the end, the switch down payment excepting the plan's own schedule figures;
  - the switch rounds its shares, its single advance and the minimum due, excepting the old schedule's figures;
  - the deposit rounds once at the end.
- Month-convention sentences remain only where a month count is read (deposit age, switch down payment twelve-month window).
- Edge found while probing: on a Paid-in-Full plan (installment_count 0) the makeup's schedule figure divided by zero. adv_sched is now 0 there, consistent with the rule (no installment remains, so no advance).

### Probes (scratch copies only)
| probe | outcome |
|---|---|
| task 0, the draft that paid the latest invoice returned | the latest invoice owes its minimum due again; the deposit's credit stays the credit actually held |
| task 1 plan as Paid-in-Full with live authorization | payment-plan advance 0 |
| task 1 returned payment linked to no invoice | re-collection 0, advance 0 |
| both task worlds | every scored figure unchanged |
REWORK round 8: gates 7/7 green

## Round 9 rework (audits/policy_task/installment_billing_and_fees/ revision_8, CG-30)

Read the revision_8 sections in full. Charter only; both tasks passed. Minimal edits; no scored value moved (check_compute unchanged).

### CG-30 closure
The DSL cannot aggregate every return against an invoice exactly: return rows carry only related_payment_txn_id, and eq filters cannot join over several payments. So each affected read is scoped by a stated record test, with the base restated outside the scope. Inside the scope the read is exact in rule words and compute alike.
- Endorsement deposit:
  - Covers an EFT/Card owner plan only while its most recent installment invoice has at most one payment posted against it. Outside that, the payment is taken as every other one-time payment is and applied in payment_application_order.
  - "What it still owes" now reads "its minimum due less the payment posted against it, if any, plus every amount the bank returned against that payment". The compute is unchanged: the single payment's returns, summed.
- Returned-payment makeup:
  - Covers a returned payment whose invoice, if it paid one, has no other payment posted against it, and whose plan's next installment invoice, if already issued, has at most one payment posted against it. Any other returned payment is made good as every other one-time payment is.
  - Re-collection is exact under that test, since the returned amount is the total returned against the only payment.
  - The advance's already-invoiced tier now reads "that invoice's minimum due less the payment posted against it, if any, plus every amount the bank returned against that payment", in rule, ladder and compute (returns of that payment added back).
- Direct-bill switch and switch down payment: the scope sentences, including the revocation overwrite's replaced_by, carry the same test "as the records stood when the move was asked". The switch's makeup wait is therefore always producible, and the makeup's own payment never takes the plan out of scope.

### Probes (scratch copies only)
| probe | outcome |
|---|---|
| task 1 seed: one payment on invoice 3 | in scope; re-collection 209.18 (unchanged) |
| task 1, a second payment on invoice 3 also returned (two returns) | two payments on the invoice -> outside the makeup, switch down payment and switch scopes; base application |
| task 0, the single payment on the latest invoice returned | owes its full minimum again (exact) |
| task 0, two payments on the latest invoice | outside the deposit's scope |

### Same-class sweep
- Every remaining "still owes" or standing read: the draft notice's and switch's standing balances come from account_balance, which already reflects every return, so they are exact.
- The switch's makeup wait is worded "net of returned payments" and is a state test, not a computation.
- No other policy reads an invoice's open amount.
REWORK round 9: gates 7/7 green

## Round 10 rework (audits/policy_task/installment_billing_and_fees/ revision_9, CG-30)

The round-9 record tests were stated but not computed. They are now enforced in compute:
- Deposit:
  - New plain binding dep_scope_ok: payments posted against the latest installment invoice <= 1.
  - result becomes 0 out of scope.
  - The rule's out-of-scope clause now says no endorsement deposit is figured (0.00); the payment is ordinary, for the amount the customer states.
- Makeup:
  - New plain bindings mk_scope_invoice_ok (payments on the returned payment's invoice, excluding makeups referencing it, <= 1), mk_scope_next (that invoice's next installment invoice) and mk_scope_ok (also <= 1 payment on the next invoice if issued).
  - result becomes 0 out of scope.
  - The rule states the counting convention and that no makeup is figured (0.00) outside it.

The auditor's three probes were re-run; per-probe tests and figures are in rework_r10_claims.md.
- Deposit one-of-two returned: 0.00.
- Deposit both returned: 0.00.
- Makeup with an earlier returned 50.00 on invoice 3: 0.00.

Scored worlds stay in scope:
- Task 0: notice 327.36, deposit 43.97.
- Task 1: makeup 519.36, down 153.88, first invoice 109.10.

Factor sensitivities are unchanged, and check_compute recomputes everything identically. The scripted quote/baseline/replaced_by sweep is clean.
REWORK round 10: gates 7/7 green

## Round 11 rework (audits/policy_task/installment_billing_and_fees/ revision_10)

### CG-31 (switch down payment and move: scope enforced)
- Switch down payment:
  - New plain bindings dn_ret_payment, dn_ret_invoice, dn_ret_next and dn_pay_ok carry the same record test as the makeup: the returned payment's invoice has no other payment except makeups referencing it, and the next invoice has at most one payment. Since makeups and the down payment itself are not counted, the test holds as the records stood when the move was asked.
  - dn_scope_ok also requires an EFT/Card owner plan.
  - Out of scope the figure is 0.00. New rule sentence: "When the move is asked on any other plan, or outside these limits, no switch down payment is due (the schedule's figure is 0.00)."
- Direct-bill switch:
  - The same test, plus EFT/Card owner plan and the move window (at least one invoiced, two or more not), forms sw_scope_ok.
  - Out of scope the figure is the base outcome (new binding sw_base_sched): MX(0, the installment's unchanged scheduled premium + the Six-Pay installment_fee + the standing balance).
  - New rule sentence after the two waits: "When the move is asked on any other plan or outside these limits, this schedule and neither wait above apply: the revocation is recorded under the base rule, the plan becomes the Six-Pay Direct Bill Plan for its remaining installments, and its next invoice bills, as the base installment schedule states, ...". The waits and the revocation overwrite are consistent with the computed scope.

### CG-32 (out-of-scope routing agrees with the in-force override)
The deposit's and the makeup's out-of-scope sentences now route the payment "as every other payment on its plan is":
- on a Monthly EFT or Monthly Card Autopay owner plan, to past-due invoices oldest first (fees before premium), then to unpaid late and NSF fees, then to the current invoice, with what is left held as a credit the draft notices carry (the draft notice overwrite's own words);
- on any other plan, in payment_application_order.

### Scope sweep (stated <=> enforced)
- Draft notice:
  - notice_scope_ok requires an EFT/Card owner plan.
  - Out of scope the figure is the base invoice MX(0, scheduled premium + plan installment_fee + standing balance).
  - The scope sentence now states that base for every plan it does not name.
- Deposit: dep_scope_ok also requires an EFT/Card owner plan.
- Makeup: mk_scope_ok also requires an owner plan.
- No scope sentence is left without a guard, and no guard is left without a sentence.

### Probes (scratch copies)
| probe | outcome |
|---|---|
| task 1 world with an earlier returned 50.00 on invoice 3 | makeup 0.00; switch down payment 0.00; switch base figure 458.36 = 205.18 + 9.00 + 244.18 standing |
| task 0 plan as Four-Pay | notice gives the base invoice; deposit 0.00 |
| both scored worlds | in scope everywhere; every scored value and sensitivity unchanged |
REWORK round 11: gates 7/7 green

## Round 12 rework (audits/policy_task/installment_billing_and_fees/ revision_11, bounded members 1-7)

Only the seven listed members were changed; per-member probes are in rework_r12_claims.md.
- CG-33.1: mk_made_good (a payment referencing the returned payment) takes the makeup out of scope (0.00), with a stated sentence.
- CG-33.2: the switch and draft-notice wording now covers only a move at the named insured's request. Automatic moves (returned-draft, certified-funds) are restated as base in the billing_plan_switch overwrite tail.
- CG-34.3: new draft notice fallback bindings mv_k, mv_down, mv_left, mv_n, mv_respread, fb_premium, fb_unbilled, fb_end_billed and fb_standing. On a requested move, later invoices bill the respread the switch fixed, and the standing balance is reckoned on that schedule. Stated in the notice's scope sentence. (mv_k is taken as an int so the installment filter matches exactly.)
- CG-34.4: adv_auth guards both advance tiers; the words and ladder say "while the plan still bills by automatic draft".
- CG-34.5:
  - The schedule down payment premium is down_payment_amount less the policy fee booked on the term, less the new-requirement certificate fee when the certificate was requested on or before enrollment.
  - Applied in the notice, deposit, switch down payment, switch and makeup advance.
  - Unused first-term bindings, term_number reads and baseline params were removed.
- CG-34.6: the notice fallback computes the down payment premium for a non-owner plan from the non-owner policy fee (nonowner cross category declared). No term number is read.
- CG-35.7: mk_nsf_due and mk_late_due are net of the waiver reversing that fee. Exact, since base allows one NSF fee per return and one late fee per invoice.

Gate recomputation leaves every scored value and sensitivity unchanged. The scripted quote, baseline, replaced_by and unused-binding sweep is clean.
REWORK round 12: gates 7/7 green

## Round 13 rework (bounded: CG-36)

- The status-dependent certificate lookup inside the down-payment-premium read (status='filed', requested_date, new_requirement fee) was replaced in all six places by one exact, status-independent read: every fr fee assessed on the plan's set-up date (posted_date = enrolled_date).
- The sentence wording now matches that read in every rule, compute_basis quote and baseline paragraph. The fr cross-category read lists were trimmed to match.
- Probe (task 0's plan, SR-22 later moved to cancellation_filed, with and without a set-up-day fee): the down payment premium is unchanged by the status change in all six reads.
- Gates recompute every scored value unchanged.
REWORK round 13: gates 7/7 green

## Round 14 rework (bounded: CG-37 and the billed-certificate read)

- Every certificate and filing-fee read now keys on the filing whose backing term id is the plan's own term, with no status filter. The eight places are listed in rework_r14_claims.md.
- Because several filings may rest on one term (fr_agg_backing_term), a stated and enforced record test, "the term backs at most one certificate" (XCOUNT on fr_filings), now sits in all five scopes. Outside it the base outcomes apply, with the down payment premium taken from the base down payment rule (term number read from the term the plan bills).
- Wording matches the reads in every rule, compute_basis quote and baseline. The fr read lists were updated.
- Probes (a) and (b), plus a two-certificate term, are recorded in the claims file.
- Gates recompute every scored value unchanged.
REWORK round 14: gates 7/7 green

## Round 15 rework (CG-38 + exhaustive self-audit)

- CG-38 is closed. Every down payment premium read is now the recorded down payment less the term's policy fee and the set-up-day fees of its certificates. The set-up-day fees are exact for 0 or 1 certificates on the term, and for 2 or more when the term backs every certificate the customer holds. The base-formula recomputation path is removed.
- The unresolvable residual (2+ certificates on the term while the customer holds one elsewhere) is stated and computed as no figure (0.00) under the base installment schedule.
- The exhaustive probe matrix (500 cells over the five scope dimensions) is in rework_r15_claims.md. Two further classes were found and fixed:
  - zero-installment and no-installment-left plans (division by zero): now guarded, with stated 0.00;
  - non-owner fallbacks reading owner-only records: now read the non-owner term.
- After the fixes, all 500 cells agree. Scored values and sensitivities are unchanged, and the scripted quote, baseline and replaced_by sweep is clean.
REWORK round 15: gates 7/7 green

## Round 16 rework (strictly bounded: CG-39, CG-40)

- CG-39: the residual case is now priced by the base installment schedule in the notice and the switch, not 0.00:
  - enrolled plans use the base down payment rule's down payment premium;
  - switched-in plans use the installment 1 invoice's recorded premium.
- CG-40: every base invoice the notice and switch compute now adds the term's unbilled certificate filing fee, through the in-scope read reused unchanged and keyed on the term the plan bills, owner or non-owner. The restated base sentences name it.
- The eight touched cells were re-run on consistent worlds; all agree (rework_r16_claims.md).
- Gates recompute every scored value unchanged.
REWORK round 16: gates 7/7 green

## Round 17 rework (strictly bounded: CG-41)

- The first-certificate residue is now stated in one identical sentence in the draft notice and in the switch. Their certificate-fee phrases name "the certificate recorded first", which is the compute's first-match pick in filing-record order.
- The auditor's probe agrees in both policies; see rework_r17_claims.md.
- Gates recompute every scored value unchanged.
REWORK round 17: gates 7/7 green

## Round 18 rework (strictly bounded: render_r2.md R1-R3 and note)

- R1: the overwrite tails of the notice and the switch now name the first-recorded certificate's unbilled filing fee on any other invoice, matching the scope sentences and the fallback compute.
- R2: the at-most-one-payment test in the switch down payment and the switch states the makeup exception; the unrecorded time reference is dropped.
- R3: the case of a switched-in plan with no installment 1 invoice (base percentage of the present plan) is stated in both rules.
- Note: the double comma is removed.
- The scripted quote, baseline and replaced_by sweep is clean. Gates recompute every scored value unchanged.
REWORK round 18: gates 7/7 green

## Round 19 rework (bounded: KB audit SRC-1)

- billing_ext_direct_bill_switch now carries a scoped overwrite of the base sentence "After a mid-term plan switch, invoices issued from the switch date carry the new plan's fee; invoices already issued keep theirs.":
  - the first invoice after a requested move carries the state fee schedule's fee;
  - every other post-switch invoice, a moved plan's later invoices included, carries the new plan's fee.
- Class sweep over all governing base sentences: no other undeclared departure (list in rework_r19_claims.md).
- Gates recompute every scored value unchanged.
REWORK round 19: gates 7/7 green

## Round 20 rework (bounded: CG-42)

- The base clause "No installment fee is charged ... on an installment avoided by paying the whole balance before it was invoiced" is now honored in the draft notice (all branches) and the switch (first and out-of-scope invoices). When account_balance <= 0 at the invoice, the installment/state fee is 0.00 and any certificate fee is still billed; the rule says so in one sentence per policy.
- compute_basis quotes that had picked up a following sentence were reduced to single verbatim sentences.
- Clause-by-clause sweep of every base sentence the rules touch: rework_r20_claims.md.
- Gates recompute every scored value unchanged.
REWORK round 20: gates 7/7 green
