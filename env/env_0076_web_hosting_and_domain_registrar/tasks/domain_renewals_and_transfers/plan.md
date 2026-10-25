# plan — domain_renewals_and_transfers (env_0076), M=2

Draw (draw_counts.py --tasks 2):
- task 0: prerequisite_problems=3 (4 problems), factor_counts [6,6,5,5]
- task 1: prerequisite_problems=3 (4 problems), factor_counts [6,4,4,6]

## Constraints found in Step 0 (drive the design)
- DSL history primitives are scoped to ONE domain holding; same-category cross-holding reads are impossible
  -> every value_input edge links two problems on the SAME domain holding; each task = one holding.
- Only money writes carry a policy-computed number: domain_renewal_charge (renewal / grace_renewal),
  domain_restore_charge, domain_refund. Auth codes, settings, registrant change, transfer decision carry
  no computable number (no date-add primitive) -> not used as problems.
- A full refund is a lookup (factorless) -> refund problems are over-billing corrections (refund of the
  excess of a past line over the price its charge date entitled), declared as overwrite of the base
  "full amount only" clause.
- Customer-own writes (owner=user) = the customer paying the extension years by card (a payment).
- Never pay from account credit (account trigger) and never refund to account credit.
- Identifier band: surnames/companies A–E, (512)/(416) 555-01xx, PIN 1xxxxx, card 1xxx,
  domain labels a–e, order refs HL-01xxxxxx.

## Trees (one holding per task)
task 0 — .com in renewal grace, reseller account, hosting plan on the domain
- root  MR  term extension to the registry maximum (USER pays by card)       [6]
- GR  grace-period renewal of the lapsed registry year (agent)               [6]  MR <- GR value_input (expiry, years)
- CRA correction of an over-billed auto-renew line (agent)                   [5]  GR <- CRA value_input (late-fee courtesy)
- CRM correction of an over-billed manual renewal line (agent)               [5]  MR <- CRM state_gate
task 1 — domain in redemption, business/reseller account
- root  RX  restore-order extension years (USER pays by card)                [6]
- RS  redemption restore (agent)                                             [6]  RX <- RS value_input
- CRG correction of an over-billed grace-period renewal line (agent)         [4]  RS <- CRG value_input (restore-fee courtesy)
- CRR correction of an over-billed registration line (agent)                 [4]  RX <- CRR state_gate

## Work order
1. scratch authoring scripts in /tmp/domain_renewals_and_transfers_0076/ (assemble yaml from fragments)
2. task 0: policies -> tools -> check_task_tools -> seed -> verify code -> task json -> per-task gates
3. traceability once before docs (expect only unlock misses)
4. task 1 same
5. XF_recipe sweep + worklog tables; final gate block

## FROZEN DESIGN (round 1, resumed) — supersedes the tree sketch above where they differ
Schedule elements (each policy restates its own ladder; ids per policy):
 E1 account-tier pct (account, 5 tiers)            E2 companion per-year basis (hosting; active&>=12mo -> registration_price,
 E3 mailbox credit METHOD (email; >=5 seats per-seat,   active&1mo -> transfer_in_price, else renewal_price; multi-source)
    1-4 flat, none)                                  E4 certificate credit (ssl; OV/EV hi, DV lo, none)
 E5 late reactivation fee METHOD (fault->0, <=7d flat, else per-day capped)   E6 restore fee METHOD (fault->0, <=10d min(fee,49), fee)
 E7 term credit METHOD (Y>=5 per-year, 3-4 flat, none)  E8 funding saver (old schedule; credit/card/other)
 E9 lapse saver (auto-renew on & no decline 12m / on & decline / off)  E10 win-back (reactivation line today)
 E11 ERRP notice make-good (no post-expiry notice / late / on time)
Old schedule = lines billed before 2025-12-01 (corrections, 24-month window, partial refund of excess, no expiry rollback).
task0 ashbycreative.com (.com, grace, Reseller Bronze, Corinne Ashby): GR(6:E1,E2,E3,E4,E5,E9) CRA(5:E1,E2,E3,E4,E8 on 2025-09-08 auto line)
  CRG(5:E1,E2,E3,E4,E8 on 2024-10-25 grace line) MR root user(6:E1,E2,E3,E4,E7,E10; Y=years to 10-yr limit)
  edges: GR<-CRA value(E5 fault) ; GR<-CRG state ; MR<-GR value(Y, win-back)
task1 driftwoodbakehouse.net (.net, redemption, Business Account): RS(6:E2,E3,E4,E6,E9,E11) CRT(4:E2,E3,E4,E8 transfer line)
  CRR(4:E2,E3,E4,E8 2025 restore line) RX root user(6:E2,E3,E4,E7,E9,E10)
  edges: RS<-CRR value(E6 fault) ; RS<-CRT state ; RX<-RS value

## Progress
- task 0 CLOSED: CRA 7.79 / CRG 8.79 / GR 10.39 / MR 89.72 (user); per-task gates green; traceability pre-docs = 4 unlock misses only.
- task 1 world: driftwoodbakehouse.net (.net), Desmond Brightwater, Driftwood Bakehouse Inc. (Toronto, CA), Business Account;
  transfer-in line 2024-10-23 (17.18), restore line 2025-10-27 (109.18), 2026 lapse -> redemption 2026-10-21; frozen 2026-10-22.
  expected: CRT 5.15, CRR 8.15, RS 7.03, RX 99.87 (9 years).

## ROUND 2 DESIGN (rework of audits/policy_task/domain_renewals_and_transfers r1)
- Corrections become the "Domain Care price match" (look-back refund of the difference between a 2022-01-01..2025-11-30 line
  billed under the base rules and the Domain Care price of that line): no historical price is redefined (C2); one most-recent
  line per family; gate sentences carry the exact resolver scope (C3).
- Realistic factor kit only (TIER reseller pct, BUNDLE hosting credit, PLAN hosting-plan allowance [method], VOLUME reseller
  deposits 12m, AUTOPAY auto-renew saver, TERM multi-year [method], LATE fee [method], COURTESY restore fee [method],
  ERRP notice make-good, LOCK transfer price lock [method]); mailbox/certificate/payment/retention/win-back credits removed.
- Tails restate the true rule for every other charge (C1/C5); subjects GR=[domain_grace_renew], MR/RX=[domain_expiry_update]
  so no non-conflicting gate is retired (C5a); extension years = greatest whole number within the 10-year limit (C4);
  zero-window sentence declared (C6); no ssl/email first-match reads (C7); bounded credits keep every amount positive (C8);
  every fall-through reachable in scope (C9); seeded near-misses per computation (R4).
- New refund tools (price match) replace the four overbilling tools.

## ROUND 3 DESIGN (audit revision_2: N1-N4 + owner ruling)
- Price match refund = the Domain Care credits the line earns today (hosting credit, plan allowance, volume credit, autopay
  credit, + term credit on renewal-type lines), never more than billed; no reseller discount inside it (N2); refund tails name
  the three sibling price matches (N1); each price match retires only clauses governing its own line type (N3).
- Plan allowance is an honest method in every scope: Business/Cloud plans credit the TLD's basis price less its registration_price
  (two tariff inputs), Starter/Plus/Pro a flat amount, none otherwise (N4); restore-day price lock relabelled parameter.
- Restore drops the reseller discount (autopay credit instead); volume thresholds 250 / 5,000 (O9); ladder typo fixed (O11).
- Owner ruling (b): extension payments are the holder's own checkout payment (PayPal / a card entered at checkout) stated in
  the rule; persona shows why (card on file declined / near its limit).
