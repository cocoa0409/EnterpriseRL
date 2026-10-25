# driver_card_changes — plan (env_0083, category card, M=2)

## Draw (scripts/draw_counts.py --tasks 2)
- task 0: prerequisite_problems=2, problems=3, factor_counts=[6, 6, 5]
- task 1: prerequisite_problems=1, problems=2, factor_counts=[6, 4]

## Charter reading (frozen base, card.yaml)
Priced writes of the category: card_replacement.amount (replacement fee), card_shipping_fee.amount
(paid shipping), card_fee_reversal.amount. Every other card write (lost/stolen block, cancel,
reassignment, hold, PIN reset) carries no figure, so it cannot be a problem of a tree (every problem
needs a 4–6 factor computation). by:user writes the charter grounds: the administrator's
confirmation of a lost/stolen replacement once the assignee's lost/stolen reports reached
lost_stolen_reports_per_12m_before_review (card_evt_replacement), and cancellation / driver
termination (card_driver_changes, no figure).
DSL reach: own-category history is scoped to the target card only (card_events of that card);
cross-category reads by customer (program tier / prior tier / tier_effective_on, program_charges
per-card fee rows, program_transactions on the card, dispute cases on the card).
THIN CHARTER: a single per-card flat fee carries ~2 catalogue levers (product fee by reason,
program-rank benefit). Every further factor is a keyed schedule (R1 program tier / fleet-size band,
R2 days since issue, R5 cap) declared by overwrite with figures in policy params. These are flagged
as R6 candidates for the coordinator in worklog.md (count-keeping levers).

## Policies (5) and tools
| id | owner / tool | computes | task | factors |
|---|---|---|---|---|
| card_ext_loss_replacement_confirmation | user / confirm_loss_replacement_* | replacement fee on a lost/stolen card under administrator review | T0 prereq | 6 |
| card_ext_replacement_fee_correction | agent / reverse_replacement_fee_* | part of an earlier replacement fee not owed (charged less owed) | T0 prereq | 6 |
| card_ext_overnight_shipping_fee | agent / book_card_shipping_fee_* | overnight shipping fee of a replacement | T0 root | 5 |
| card_ext_driver_reissue_confirmation | user / confirm_driver_reissue_* | name-change replacement fee when a departed driver's card is reissued to another driver | T1 root | 6 |
| card_ext_shipping_fee_correction | agent / reverse_shipping_fee_* | part of an earlier paid shipping fee not owed | T1 prereq | 4 |

## Trees
- T0 (Peachtree Courier Group LLC): driver's card stolen and blocked by the driver's own report;
  his second lost/stolen report in 12 months, so the replacement waits for the administrator's
  confirmation; administrator calls asking for the new card overnight. Root = overnight shipping
  fee; chain root <- loss replacement confirmation (user) <- replacement-fee correction (agent).
  Edges value_input via the per-card 12-month card-fee cap (fees net of reversals) and the
  replacement row the confirmation books.
- T1 (Chattahoochee HVAC Services Inc.): technician left; his name-embossed driver card must be
  reissued (name-change replacement) to the incoming technician on the administrator's own
  confirmation. Prereq = correction of an earlier paid shipping fee on that card (value_input via
  the same cap).

## Order of work
1. extended yaml base copy + T0 policies one by one; task_tools.py tool per policy; gate check_task_tools.
2. T0 seed, persona, verification script (/tmp/driver_card_changes_0083/), GT, per-task gates.
3. T1 same. 4. final 7 gates; worklog last line.
