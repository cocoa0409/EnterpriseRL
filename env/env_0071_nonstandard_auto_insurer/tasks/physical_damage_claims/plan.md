# physical_damage_claims (category physdam) — instantiation plan, M=2

Draw (draw_counts.py --tasks 2):
- task 0: prerequisite_problems=1 (2 problems), factor_counts [5,5]
- task 1: prerequisite_problems=2 (3 problems), factor_counts [6,6,6]

Domain constraint found at Step 0: physdam numeric writes are repair payment, total loss payment,
tow/storage payment, deductible reimbursement, subrogation recovery (+ premium return via removal).
Tow/storage and subrogation amounts have no record source to compute from; a loss-payee/insured payee
split makes one side's factors decorative. Chosen 5 problems (distinct quantities, value links real):

Task 0 — repair claim, other driver at fault, partial subrogation recovery already received
  (tow + rental recovered), shop finished, repair payment not yet issued.
  - physdam_ext_repair_assignment (USER tool assign_repair_payment_*): repair payment the insured
    directs to the repair facility = latest cumulative estimate - deductible - repair payments made.
  - physdam_ext_deductible_refund (AGENT tool issue_deductible_refund_*) ROOT: deductible share of
    recoveries. Edge root -> assignment value_input (total damages paid).
Task 1 — total loss, owned vehicle, replacement vehicle already added to owner term.
  - physdam_ext_owner_settlement (USER tool accept_total_loss_settlement_*): vehicle settlement
    (tax excluded, paid separately on replacement).
  - physdam_ext_totaled_coverage_return (AGENT tool remove_totaled_coverage_*): removal of the
    totaled vehicle's coverage + premium return (refund from date of loss once settled).
    value_input on owner_settlement.
  - physdam_ext_replacement_tax (AGENT tool issue_replacement_tax_payment_*) ROOT: sales tax +
    title on the replacement; value_input on settlement (tax base), state_gate on coverage removal.

Order of work: extended.yaml base copy -> task 0 policies -> tools -> seed -> persona -> verify ->
GT -> gates; then task 1 same; final gates; worklog line.
Scratch: /tmp/physical_damage_claims_0071/ (deleted at end).

## Revision after task 0 (design of task 1)
A separate replacement-tax payment to the named insured would collide with the owner's settlement
row (physdam_total_loss_payment grain = one row per payee per claim). Task 1 instead splits the
total loss by payee under a declared company practice (vehicle value to the loss payee, who returns
any equity; tax, title and owner items to the named insured):
  - physdam_ext_lienholder_settlement (AGENT pay_loss_payee_settlement_*): vehicle value to the lienholder.
  - physdam_ext_owner_tax_title (USER accept_total_loss_settlement_6ed13516): tax/title owner payment.
  - physdam_ext_totaled_coverage_return (AGENT remove_totaled_coverage_12b8272a) ROOT.
  Chain: return -> owner payment (earning anchor) -> lienholder payment (tax base); both value_input.

## Rework round 2 plan (audit audits/policy_task/physical_damage_claims/)
Trees, tools and policy ids kept. Factor redesign per policy (class-wide fixes):
- Claim selection everywhere: highest claim number (issued in sequence) — tie-free (XF8).
- XF3: every deductible = replacement first, then additions, then subtractions, floor 0, stated once.
- XF2: generic combination sentences; XF11: every factor sentence names the result it changes.
- repair_assignment: cause deductible (FL windshield tier) / permissive surcharge / good-driver credit /
  storage days (method: towed, driven-in capped, none) / storage rate by garaging-state schedule.
  Unrepaired-damage carve-out removed (shop-repaired key RED).
- deductible_refund: repair part (M) / rental part (M: paid net, authorised-unpaid accrued, none) /
  never-refunded surcharge (P) / deductible source (P, relabelled) / tow counted at package tow limit (P).
  Installment expense removed (incidental count, XF17). Prerequisite scoped to repair claims with no
  total loss declaration (C-POL-1, XF19).
- lienholder_settlement: valuation reports (M) / market (P) / recent-purchase cap (P, relabelled) /
  unrepaired damage capped at a share of the declared ACV (M, no shop key) / total-loss cause (P) /
  permissive surcharge (P).
- owner_tax_title: tax base (M: lessor none / greater of declared ACV and recognised value) / state tax
  rate / state title fee / replacement share (monotone full/half/none) / title clearing / storage (M).
- totaled_coverage_return: return start (M: replacement date / date of loss / today) / earning basis
  (M: pro rata / flat while inspection pending / short rate) / rate method (M: per-charge re-rate,
  post-loss change refunded, added rate) / minimum-earned charge / endorsement fee by liability package /
  lienholder handling charge. Paid-claim retention and renewal-halved short rate removed.
- Seeds: full auto premium + billing ledgers + physdam/rental premium rows, read by added gold reads.

## Rework round 3 plan (audit revision_2)
Trees, tools and policy ids kept; task_tools.py unchanged.
- R2-XF2: one generic order sentence by kind of adjustment in repair, refund and loss payee (no factor named).
- R2-GATE: repair baseline storage = wait beyond the free days within the storage-day allowance; owner baseline = whole sales tax plus a nonzero storage charge; replacement_share removed, owner_storage_schedule (state storage schedule) added.
- R2-XF19: E1 carved out by a record test (latest estimate above earlier-estimate payments + larger deductible + permissive-collision surcharge); E2 carved out where the loss-payee rule leaves no value; E3 impossible to zero (owner payment never below the title fee).
- R2-XF11: return vehicle-added reads keyed on this owner term. R2-XF8: latest authorization by entry date, closing counted only when dated on/after it.
- R2-XF17: market_adjustment -> lp_renewal_credit (term number/points, task 1 world becomes renewal term 2); loss_payee_charge_ladder -> plan_minimum_earned (minimum earned as a percent of the full-term rate by payment plan). No add-on introduced.
- R2-XF18: task 0 rental not yet billed (authorised-rental tier), so the 0.00 benefits cache states no tier value.

## Rework round 4 plan (audit revision_3)
Trees, tools, policy ids and every combination sentence's order kept; task_tools.py unchanged.
- R3-XF15: E2 scope rewritten as a record test (payoff recorded; every recorded ACV and the value at binding above a quarter of the declared ACV plus the largest deductible terms), which guarantees a positive loss-payee value, so the wait stays satisfiable.
- R3-LADDER: appraisal_wait tiers glass (none) / other loss towed in (uncapped) / otherwise (allowance = baseline): three real outcomes.
- R3-XF23a: return_start's replacement tier removed; a paid total loss returns from the date of loss.
- R3-XF23b: deletion_endorsement struck with its params and sentence; minimum_earned_tenure (renewal share of the minimum-earned charge, term number) keeps the drawn count without any new charge.
- R3-XF13a: task 0 rental re-seeded with the weekly invoices (duplicate reversed); the final partial week is unbilled and the rule's paid tier adds the authorised days after the latest paid period, so the cache differs from the tier value.
- R3-XF13b: task 1 term chain from inception (Camry on term 1, Accord replacing it on its acquisition date with pro-rata premiums, renewal priced on the Accord); read-only gold step for term 1's vehicle changes.
