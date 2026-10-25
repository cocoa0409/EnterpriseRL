# d2_contract_pricing_claims_and_rebates — instantiate plan (round 1, fresh relaunch, design v2)

Draw (draw_counts.py --tasks 2) — unchanged, adopted from v1:
- task 0: prerequisite_problems=2 (3 problems), factor_counts [5, 6, 4]
- task 1: prerequisite_problems=3 (4 problems), factor_counts [6, 5, 4, 5]

## DSL constraints (from v1, re-verified against check_compute.py)
- compute is scoped to ONE pricing agreement (HID); history filters are equality-only (str compare);
  windows are whole months back from NOW (0 <= MONTHS(d, NOW) < N); LATEST picks the max date_field,
  ties keep the FIRST row met (strict >) -> seeds must never tie on a LATEST read.
- no subscripts / tuples / lists: P('rebate_ladder') and P('category_discount_schedule') unusable.
- keyword filters may take bindings (dynamic anchor: rma_number=rma, sku=..., order_number=...).
- XF #12: an item/RMA computation is scoped to a case with exactly one record-visible candidate.
- Trigger ban: pricing_claim_decided outcome=approved and pricing_rebate_paid payout_method=credit_memo
  both trigger credit:credit_memo_issued -> no tool writes them. Decision tool enum = denied |
  referred_to_pricing_desk; payout tool writes check only (Strategic is the only tier offering check).
- Lifecycle writes (sign / renew / terminate) carry dates only (no DSL date arithmetic) -> not used.

## v1 -> v2 revisions (why)
- v1 task 0 "closed_agreement_forfeiture as state_gate" had no coherent world (a forfeiture zeroes the
  balance the check would pay). v2 task 0 is a FINAL SETTLEMENT of an early-terminated Strategic
  agreement: the forfeiture takes only the rebate of the period in which the termination took effect
  (declared overwrite of the base "whole unpaid balance" clause), completed-period rebate is kept and
  paid by check. Chain: payout <- forfeiture <- clawback (both value_input).
- v1 task 1 kept (substitute story) but the open-claim decision now gates the substitute's protected
  price (state_gate: an open dispute about the discontinued item's price is settled before its price
  is carried over), and the removal (discontinuation close-out) feeds the protected price (value).

## Scope split (pairwise disjoint, covers all 7 policies)
Task 0 — Strategic Supply Agreement, early-terminated 2026-09-30, final rebate settlement by check:
- root  pricing_ext_final_rebate_check    (user)  amount   factors 6   <- forfeiture (value_input)
- pre   pricing_ext_termination_forfeiture (agent) amount  factors 5   <- clawback (value_input)
- pre   pricing_ext_return_clawback       (agent) amount   factors 4
Task 1 — Category Contract, discontinued contract item, substitute overbilled (chain, all value_input):
- root  pricing_ext_substitute_claim      (user)  claim_amount        factors 5 <- protection
- pre   pricing_ext_substitute_protection (agent) contract_unit_price factors 5 <- closeout
- pre   pricing_ext_discontinued_closeout (agent) contract_unit_price factors 4 <- decision
- pre   pricing_ext_open_claim_decision   (agent) contract_unit_price factors 6
  (v2 note: the decision now feeds the close-out by value — the close-out price starts from the price the
   desk decided on the pending escalation claim — instead of gating the protection; multiset {6,5,5,4}
   = draw [6,5,4,5]. Task 0 counts: final check 6, forfeiture 5, clawback 4.)

## Status log
- [x] base copied verbatim into pricing.extended.yaml (byte-identical, cmp verified)
- [x] task 0 policies / tools / seed / GT / per-task gates green
- [x] task 1 policies / tools / seed / GT / per-task gates green
- [x] final gates (8/8 green, traceability deferred to after render), XF recipe sweep recorded in worklog.md, worklog last line

## Probe table (CFIELD / first-match / LATEST reads, decoys, absent records, None/zero-div/date edges)
(filled per policy as compute is written)

### Probe table — task 0 (run on scratch copies of the seed, /tmp/.../t0_probe.py)
| policy | read | probe (decoy / absent / edge) | result |
|---|---|---|---|
| clawback | LATEST accrual period/rate/date | no accrual rows at all | in_scope 0 -> 0.00 (no exception; rate `or 0`) |
| clawback | XLATEST received RMA | later authorization RMA-209344 (not received) present | unchanged 24.61 (event_type filter) |
| clawback | XLATEST received RMA | second receipt line on the same RMA | ret_lines 2 -> out of scope 0.00 |
| clawback | XLATEST received RMA | no receipts at all (absent) | rma None -> 0.00 |
| clawback | XLATEST shipment of returned line | extra earlier partial shipment of the same line | latest shipment still 2026-09-15 -> unchanged |
| clawback | XCOUNT receipts 12 months | extra receipt 2026-09-30 | count 5 -> frequency share 1 (rule-consistent) |
| clawback | period cap SUM | cap 18,957.75 vs 24.61 | cap does not bind |
| forfeiture | LATEST accrual / SUM by period | decoy payout 1,000 on 2026-Q3 | term_net falls by 1,000 (payouts subtracted, rule says so) |
| forfeiture | EXISTS vmi/vending | extra closed StockSmart program | unchanged (status filter) |
| forfeiture | attainment division | commitment 0.00 | attainment 0, no zero division |
| forfeiture | DAYS notice | notice date empty | extra notice 0, no exception |
| forfeiture | status scope | agreement active | 0.00 (out of scope) |
| check | CFIELD credit ar/limit | no credit account (absent) | exposure 0 -> holdback 0, no exception |
| check | XLATEST authorization | latest authorization later received | settled -> open-return holdback 0 |
| check | XLATEST authorization | no authorizations (absent) | holdback 0, no exception |
| check | XCOUNT finance charges | charge dated 2025-10-15 (12 months + 1 day) / 2025-10-31 | not counted / counted (3 -> 3 percent) |
| all | same-day ties | no two rows share a date on any LATEST/XLATEST read | n/a |

### Probe table — task 1 (scratch copies, /tmp/.../t1_probe.py)
| policy | read | probe (decoy / absent / edge) | result |
|---|---|---|---|
| decision | LATEST filed claim | a later filing that is already decided | latest filing decided -> out of scope 0.0000 (rule: the most recently filed claim, while undecided) |
| decision | LATEST item lines | claimed item has no price lines (absent) | out of scope 0.0000, no exception |
| decision | cost division | add line supplier cost 0.0000 | cost increase 0, allowance floored at 0 -> 61.2000, no zero division |
| decision | XSUM invoices | no invoices | commitment ratio 0 -> reduction 0 (61.6124) |
| close-out | LATEST decision for the item | decision only on another sku (FS-20118) | sku filter -> recent-escalation tier 59.3640 |
| close-out | LATEST decision date | decision dated before the latest price line | tier (b) 59.3640 (decision must be on/after the line) |
| close-out | XLATEST backorder / fill | latest backorder filled with the same item | not a substitute -> 0.0000 |
| close-out | XLATEST backorder | no backorders (absent) | 0.0000, no exception |
| close-out | COUNT removals | a removal already on record | out of scope 0.0000 |
| protection | COUNT/LATEST close-out | no close-out line (absent) | ending 0 -> 0.0000 |
| protection | XLATEST regular shipment | substitute has only the backorder fill | own price absent -> starts from the ending price |
| protection | EXISTS vmi | extra closed StockSmart program | unchanged (status filter) |
| claim | XSUM receipt / authorization | receipt removed, authorization kept | billed less authorized = 120 (same tier value) |
| claim | payments on invoice | payment removed | invoice not covered -> paid-invoice credit 0 |
| claim | XLATEST invoice | no invoices (absent) | out of scope 0.00 |
| claim | protection window | shipment 95 days after protection start | out of window 0.00 |
| all | same-day ties | no two rows share a date on any LATEST/XLATEST read | n/a |

## Rework round 2 — probe additions (re-run on the round-2 charter and seeds)
Task 0 (t0_probe.py, seed now with the 2026-Q2 payout made 2026-07-28): gold clawback 24.61, forfeiture 9,939.90,
check 7,823.79; every round-1 probe re-run with the same behaviour (absent receipts / accruals -> 0.00; later
authorization ignored; second receipt line -> out of scope; zero commitment -> no division; empty notice date ->
0 extra days; non-terminated -> 0.00; payout on 2026-Q3 subtracted; no credit account -> exposure 0; settled or
absent authorization -> 0; finance charge 12 months + 1 day not counted). Added:
| policy | read | probe | result |
|---|---|---|---|
| clawback | XLATEST receipt, same-date tie | second receipt dated 2026-10-07 recorded later | the first recorded (RMA-208152) stays the selected return (stated tie rule); the extra line only raises the frequency count |
| forfeiture | MONTHS tenure boundary | effective date 2024-03-30 | 30 whole months -> long tier (forfeiture 8,993.24): the stated convention decides the boundary |
| forfeiture | DAYS scope | termination effective 2026-10-01 | not before the accrual -> out of scope 0.00 |
| check | MONTHS months-left boundary | expiration 2027-03-29 | 5 whole months -> per-month method (7,923.79) |
| check | None / empty | closed date empty | months left 0, no exception |
Task 1 (t1_probe.py, PCL-210356 now filed 2026-10-13): gold 61.4594 / 59.6156 / 59.5405 / 1,727.71; round-1
probes re-run with the same behaviour. Added:
| policy | read | probe | result |
|---|---|---|---|
| decision | LATEST filing for the item | an earlier pending filing for AB-21740 | the latest filing is decided; the close-out waits only on the latest filing (quantifiers aligned) |
| decision | same-date tie | second filing same date recorded later | the first recorded is decided (stated tie rule) |
| decision | DAYS extra notice | notice exactly 30 days before effect (0 extra) | tight tier, unchanged |
| close-out | DAYS recent-escalation edge | escalation 30 days before the discontinuation, no decision | recent tier (prior price) 59.3640 |
| claim | DAYS invoice window | invoice 31 days after the ship date | out of scope 0.00 |
| claim | settlement tier 3 | discount without tax | 1 - discount rate -> 1,614.35 |

## Method-tier pairwise table (round 2; distinguishing input proves no two tiers coincide on their domain)
| policy / factor | tier A | tier B | tier C (fall-through) | distinguishing input |
|---|---|---|---|---|
| clawback / merchandise_value_basis | qty x invoiced price (opened) | credit + restocking fee (unopened with fee) | return credit | opened item with fee: 5,834.40 / 4,667.52 / 4,084.08 |
| forfeiture / commitment_attainment_relief | fixed 0.3 x net (>= 1.5) | (att - 1) x 0.6 x net ([1, 1.5)) | none | att 1.2: 0.3 vs 0.12 vs 0; the two meet only at 1.5, which belongs to A |
| check / unexpired_term_administration | flat 350.00 (>= 6 months) | 50.00 x months (1-5) | none | 3 months: 350 vs 150 vs 0; per-month tops at 250 |
| decision / increase_measure_basis | list rise (0 < list < cost) | zero (list <= 0 < cost) | cost rise | list +2.02 / cost +5.22: 2.02 vs 0 vs 5.22 |
| close-out / closeout_reference_basis | decided price | escalation's prior price | latest line price | 61.4594 vs 61.2000 vs 63.6480 |
| protection / substitute_start_basis | own price (below ending) | ending + 0.1 x gap (>= 15 % above) | ending | own 72.57, ending 59.6156: 72.57 n/a, 60.9110 vs 59.6156; own 55: 55 vs n/a vs ending |
| claim / returned_quantity_basis | billed - received | billed - authorized | billed | partial receipt 15 of 20 authorized: 125 vs 120 vs 140 |
| claim / invoice_settlement_multiplier | 1 + t - d | 1 + t | 1 - d (D: 1) | t 0.0725, d 0.01: 1.0625 / 1.0725 / 0.99 / 1 |

## Rework round 3 — probes for the newly stated branches (r3_probe.py, scratch copies)
| policy | branch | probe | result |
|---|---|---|---|
| final check | minimum tested on the rounded check | unrounded check 99.996 vs 100.00 minimum | issued 100.00 |
| clawback | zero receipt lines in the window | window forced to 0 months | first_return_share, 16.41 |
| forfeiture | fewer than one extra notice day | notice 173 days before effect | no notice relief, 10,413.23 |
| decision | adding line not a new-item line | AB-21740 added by a substitute line | out of scope 0.0000 |
| close-out | backordered item without an added price line | AB-21740 lines removed | out of scope 0.0000 |
| protection | replaced item without an added price line | same | out of scope 0.0000 |
| protection | substitute with no regular shipment | (round 1/2 probe) | ending price |
| claim | invoice covered without any customer payment | payment folded into the memo | no paid-invoice credit, 1,715.99 |
Gold unchanged: 24.61 / 9,939.90 / 7,823.79 and 61.4594 / 59.6156 / 59.5405 / 1,727.71.

## Rework round 4 (seed-only) — probe re-run on the new seeds
- t0_probe.py / t1_probe.py / r3_probe.py re-run on the round-4 seeds: every probe behaves as recorded above
  (task 0 gold 24.61 / 9,939.90 / 7,823.79 unchanged; task 1 gold 61.4594 / 59.6156 / 59.5405 unchanged,
  claim 1,732.79; the round-3 F2 probe now gives 1,721.06 and the settlement tier-3 probe 1,619.43).
| policy | read | probe | result |
|---|---|---|---|
| claim | discount line on the claimed invoice | discount 131.00 (round-1 1 percent figure) instead of the credit catch-up 88.45 | 1,727.71: the seed's discount line moves the scored claim, so it must be the credit rule's figure |
| protection / forfeiture | StockSmart status only | bins and activity removed | concession / relief unchanged (status read) — the added program rows are realism, not evidence |
| credit (both) | receivable path vs limit + tolerance | daily balance replay (arpeak.py) | task 0 peak 890,834.80 <= 1,100,000.00; task 1 peak 51,129.94 <= 126,000.00 |
