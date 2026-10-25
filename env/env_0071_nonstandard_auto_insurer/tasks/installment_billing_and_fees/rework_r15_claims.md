# Rework round 15 claims

Closed:
- CG-38: the out-of-scope fallbacks no longer rebuild the down payment premium from the current plan's percentage.
  - Draft notice, owner and non-owner branches, and the switch's old-schedule fallback all take the down payment premium from the plan's own recorded down payment, less the fees it took: the policy fee of the term it bills, and the set-up-day filing fees of that term's certificates. A plan switched in from another plan therefore keeps the installment amounts the base switch rule keeps.
  - Set-up-day filing fees are read exactly when the term backs zero or one certificate, or when it backs every certificate the customer holds (the customer's set-up-day fees then all belong to it).
  - The one case the records cannot resolve is two or more certificates on the term while the customer also holds one elsewhere. That case is stated and computed as outside the schedules: no figure (0.00), invoices issued under the base installment schedule.
- Further disagreements the matrix found and fixed this round:
  - Paid-in-Full and no-installment-left plans: division by zero in the notice, deposit, switch down payment and switch. Now guarded, and stated as no installment invoice, no figure (0.00).
  - Non-owner plans in the notice and switch base fallbacks: the endorsement premium and fees are now read from the non-owner term; the nonowner category is declared.

## Probe matrix (scratch copies)
Dimensions:
- enrolled on this plan vs switched in from another (down payment set at the Six-Pay 20%, plan_switches_used 1);
- certificates on the term:
  - 0;
  - 1, fee after set-up;
  - 1, fee on the set-up day (1s);
  - 2, all on the term (2all);
  - 2 on the term plus one on another term (2res);
- owner vs non-owner plan;
- inside vs outside the at-most-one-payment scope (a second payment on the read invoice);
- autopay plan (Card for task 0's world, EFT for task 1's) vs Four-Pay vs Paid-in-Full.

Skipped as impossible: switched in onto the Four-Pay Plan (no plan lists it in plan_switch_targets).

Worlds: task 0 for the draft notice and deposit; task 1 for the makeup, switch down payment and switch.

"By hand" method:
- The governing rule was coded independently: scope tests, the true set-up fees from a full join of fee rows to the term's filings, the base fallback (scheduled premium + plan fee + standing, with zero cases) and the out-of-scope 0.00.
- Extended in-scope cells are the extended compute with the down payment premium replaced by the hand-joined true figure.

Result: 500 cells, 500 agree.

### draft_notice
| enrolled | certs | holder | payment scope | plan | governing | computed | by hand | |
|---|---|---|---|---|---|---|---|---|
| enrolled | 0 | owner | in | Monthly Card Autopay | extended | 302.36 | 302.36 | agree |
| enrolled | 0 | owner | in | Four-Pay | base | 301.68 | 301.68 | agree |
| enrolled | 0 | owner | in | Paid-in-Full | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 0 | owner | out | Monthly Card Autopay | extended | 302.36 | 302.36 | agree |
| enrolled | 0 | owner | out | Four-Pay | base | 301.68 | 301.68 | agree |
| enrolled | 0 | owner | out | Paid-in-Full | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 0 | non-owner | in | Monthly Card Autopay | base | 297.32 | 297.32 | agree |
| enrolled | 0 | non-owner | in | Four-Pay | base | 465.99 | 465.99 | agree |
| enrolled | 0 | non-owner | in | Paid-in-Full | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 0 | non-owner | out | Monthly Card Autopay | base | 297.32 | 297.32 | agree |
| enrolled | 0 | non-owner | out | Four-Pay | base | 465.99 | 465.99 | agree |
| enrolled | 0 | non-owner | out | Paid-in-Full | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 1 | owner | in | Monthly Card Autopay | extended | 327.36 | 327.36 | agree |
| enrolled | 1 | owner | in | Four-Pay | base | 301.68 | 301.68 | agree |
| enrolled | 1 | owner | in | Paid-in-Full | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 1 | owner | out | Monthly Card Autopay | extended | 327.36 | 327.36 | agree |
| enrolled | 1 | owner | out | Four-Pay | base | 301.68 | 301.68 | agree |
| enrolled | 1 | owner | out | Paid-in-Full | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 1 | non-owner | in | Monthly Card Autopay | base | 297.32 | 297.32 | agree |
| enrolled | 1 | non-owner | in | Four-Pay | base | 465.99 | 465.99 | agree |
| enrolled | 1 | non-owner | in | Paid-in-Full | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 1 | non-owner | out | Monthly Card Autopay | base | 297.32 | 297.32 | agree |
| enrolled | 1 | non-owner | out | Four-Pay | base | 465.99 | 465.99 | agree |
| enrolled | 1 | non-owner | out | Paid-in-Full | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 1s | owner | in | Monthly Card Autopay | extended | 302.36 | 302.36 | agree |
| enrolled | 1s | owner | in | Four-Pay | base | 301.68 | 301.68 | agree |
| enrolled | 1s | owner | in | Paid-in-Full | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 1s | owner | out | Monthly Card Autopay | extended | 302.36 | 302.36 | agree |
| enrolled | 1s | owner | out | Four-Pay | base | 301.68 | 301.68 | agree |
| enrolled | 1s | owner | out | Paid-in-Full | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 1s | non-owner | in | Monthly Card Autopay | base | 297.32 | 297.32 | agree |
| enrolled | 1s | non-owner | in | Four-Pay | base | 465.99 | 465.99 | agree |
| enrolled | 1s | non-owner | in | Paid-in-Full | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 1s | non-owner | out | Monthly Card Autopay | base | 297.32 | 297.32 | agree |
| enrolled | 1s | non-owner | out | Four-Pay | base | 465.99 | 465.99 | agree |
| enrolled | 1s | non-owner | out | Paid-in-Full | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 2all | owner | in | Monthly Card Autopay | base | 133.01 | 133.01 | agree |
| enrolled | 2all | owner | in | Four-Pay | base | 301.68 | 301.68 | agree |
| enrolled | 2all | owner | in | Paid-in-Full | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 2all | owner | out | Monthly Card Autopay | base | 133.01 | 133.01 | agree |
| enrolled | 2all | owner | out | Four-Pay | base | 301.68 | 301.68 | agree |
| enrolled | 2all | owner | out | Paid-in-Full | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 2all | non-owner | in | Monthly Card Autopay | base | 297.32 | 297.32 | agree |
| enrolled | 2all | non-owner | in | Four-Pay | base | 465.99 | 465.99 | agree |
| enrolled | 2all | non-owner | in | Paid-in-Full | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 2all | non-owner | out | Monthly Card Autopay | base | 297.32 | 297.32 | agree |
| enrolled | 2all | non-owner | out | Four-Pay | base | 465.99 | 465.99 | agree |
| enrolled | 2all | non-owner | out | Paid-in-Full | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 2res | owner | in | Monthly Card Autopay | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 2res | owner | in | Four-Pay | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 2res | owner | in | Paid-in-Full | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 2res | owner | out | Monthly Card Autopay | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 2res | owner | out | Four-Pay | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 2res | owner | out | Paid-in-Full | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 2res | non-owner | in | Monthly Card Autopay | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 2res | non-owner | in | Four-Pay | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 2res | non-owner | in | Paid-in-Full | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 2res | non-owner | out | Monthly Card Autopay | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 2res | non-owner | out | Four-Pay | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 2res | non-owner | out | Paid-in-Full | none (0.00) | 0.00 | 0.00 | agree |
| switched | 0 | owner | in | Monthly Card Autopay | extended | 250.96 | 250.96 | agree |
| switched | 0 | owner | in | Paid-in-Full | none (0.00) | 0.00 | 0.00 | agree |
| switched | 0 | owner | out | Monthly Card Autopay | extended | 250.96 | 250.96 | agree |
| switched | 0 | owner | out | Paid-in-Full | none (0.00) | 0.00 | 0.00 | agree |
| switched | 0 | non-owner | in | Monthly Card Autopay | base | 333.03 | 333.03 | agree |
| switched | 0 | non-owner | in | Paid-in-Full | none (0.00) | 0.00 | 0.00 | agree |
| switched | 0 | non-owner | out | Monthly Card Autopay | base | 333.03 | 333.03 | agree |
| switched | 0 | non-owner | out | Paid-in-Full | none (0.00) | 0.00 | 0.00 | agree |
| switched | 1 | owner | in | Monthly Card Autopay | extended | 275.96 | 275.96 | agree |
| switched | 1 | owner | in | Paid-in-Full | none (0.00) | 0.00 | 0.00 | agree |
| switched | 1 | owner | out | Monthly Card Autopay | extended | 275.96 | 275.96 | agree |
| switched | 1 | owner | out | Paid-in-Full | none (0.00) | 0.00 | 0.00 | agree |
| switched | 1 | non-owner | in | Monthly Card Autopay | base | 333.03 | 333.03 | agree |
| switched | 1 | non-owner | in | Paid-in-Full | none (0.00) | 0.00 | 0.00 | agree |
| switched | 1 | non-owner | out | Monthly Card Autopay | base | 333.03 | 333.03 | agree |
| switched | 1 | non-owner | out | Paid-in-Full | none (0.00) | 0.00 | 0.00 | agree |
| switched | 1s | owner | in | Monthly Card Autopay | extended | 250.96 | 250.96 | agree |
| switched | 1s | owner | in | Paid-in-Full | none (0.00) | 0.00 | 0.00 | agree |
| switched | 1s | owner | out | Monthly Card Autopay | extended | 250.96 | 250.96 | agree |
| switched | 1s | owner | out | Paid-in-Full | none (0.00) | 0.00 | 0.00 | agree |
| switched | 1s | non-owner | in | Monthly Card Autopay | base | 333.03 | 333.03 | agree |
| switched | 1s | non-owner | in | Paid-in-Full | none (0.00) | 0.00 | 0.00 | agree |
| switched | 1s | non-owner | out | Monthly Card Autopay | base | 333.03 | 333.03 | agree |
| switched | 1s | non-owner | out | Paid-in-Full | none (0.00) | 0.00 | 0.00 | agree |
| switched | 2all | owner | in | Monthly Card Autopay | base | 168.72 | 168.72 | agree |
| switched | 2all | owner | in | Paid-in-Full | none (0.00) | 0.00 | 0.00 | agree |
| switched | 2all | owner | out | Monthly Card Autopay | base | 168.72 | 168.72 | agree |
| switched | 2all | owner | out | Paid-in-Full | none (0.00) | 0.00 | 0.00 | agree |
| switched | 2all | non-owner | in | Monthly Card Autopay | base | 333.03 | 333.03 | agree |
| switched | 2all | non-owner | in | Paid-in-Full | none (0.00) | 0.00 | 0.00 | agree |
| switched | 2all | non-owner | out | Monthly Card Autopay | base | 333.03 | 333.03 | agree |
| switched | 2all | non-owner | out | Paid-in-Full | none (0.00) | 0.00 | 0.00 | agree |
| switched | 2res | owner | in | Monthly Card Autopay | none (0.00) | 0.00 | 0.00 | agree |
| switched | 2res | owner | in | Paid-in-Full | none (0.00) | 0.00 | 0.00 | agree |
| switched | 2res | owner | out | Monthly Card Autopay | none (0.00) | 0.00 | 0.00 | agree |
| switched | 2res | owner | out | Paid-in-Full | none (0.00) | 0.00 | 0.00 | agree |
| switched | 2res | non-owner | in | Monthly Card Autopay | none (0.00) | 0.00 | 0.00 | agree |
| switched | 2res | non-owner | in | Paid-in-Full | none (0.00) | 0.00 | 0.00 | agree |
| switched | 2res | non-owner | out | Monthly Card Autopay | none (0.00) | 0.00 | 0.00 | agree |
| switched | 2res | non-owner | out | Paid-in-Full | none (0.00) | 0.00 | 0.00 | agree |

### endorsement_deposit
| enrolled | certs | holder | payment scope | plan | governing | computed | by hand | |
|---|---|---|---|---|---|---|---|---|
| enrolled | 0 | owner | in | Monthly Card Autopay | extended | 66.06 | 66.06 | agree |
| enrolled | 0 | owner | in | Four-Pay | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 0 | owner | in | Paid-in-Full | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 0 | owner | out | Monthly Card Autopay | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 0 | owner | out | Four-Pay | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 0 | owner | out | Paid-in-Full | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 0 | non-owner | in | Monthly Card Autopay | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 0 | non-owner | in | Four-Pay | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 0 | non-owner | in | Paid-in-Full | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 0 | non-owner | out | Monthly Card Autopay | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 0 | non-owner | out | Four-Pay | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 0 | non-owner | out | Paid-in-Full | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 1 | owner | in | Monthly Card Autopay | extended | 66.06 | 66.06 | agree |
| enrolled | 1 | owner | in | Four-Pay | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 1 | owner | in | Paid-in-Full | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 1 | owner | out | Monthly Card Autopay | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 1 | owner | out | Four-Pay | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 1 | owner | out | Paid-in-Full | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 1 | non-owner | in | Monthly Card Autopay | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 1 | non-owner | in | Four-Pay | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 1 | non-owner | in | Paid-in-Full | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 1 | non-owner | out | Monthly Card Autopay | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 1 | non-owner | out | Four-Pay | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 1 | non-owner | out | Paid-in-Full | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 1s | owner | in | Monthly Card Autopay | extended | 66.06 | 66.06 | agree |
| enrolled | 1s | owner | in | Four-Pay | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 1s | owner | in | Paid-in-Full | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 1s | owner | out | Monthly Card Autopay | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 1s | owner | out | Four-Pay | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 1s | owner | out | Paid-in-Full | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 1s | non-owner | in | Monthly Card Autopay | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 1s | non-owner | in | Four-Pay | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 1s | non-owner | in | Paid-in-Full | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 1s | non-owner | out | Monthly Card Autopay | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 1s | non-owner | out | Four-Pay | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 1s | non-owner | out | Paid-in-Full | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 2all | owner | in | Monthly Card Autopay | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 2all | owner | in | Four-Pay | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 2all | owner | in | Paid-in-Full | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 2all | owner | out | Monthly Card Autopay | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 2all | owner | out | Four-Pay | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 2all | owner | out | Paid-in-Full | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 2all | non-owner | in | Monthly Card Autopay | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 2all | non-owner | in | Four-Pay | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 2all | non-owner | in | Paid-in-Full | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 2all | non-owner | out | Monthly Card Autopay | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 2all | non-owner | out | Four-Pay | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 2all | non-owner | out | Paid-in-Full | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 2res | owner | in | Monthly Card Autopay | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 2res | owner | in | Four-Pay | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 2res | owner | in | Paid-in-Full | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 2res | owner | out | Monthly Card Autopay | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 2res | owner | out | Four-Pay | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 2res | owner | out | Paid-in-Full | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 2res | non-owner | in | Monthly Card Autopay | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 2res | non-owner | in | Four-Pay | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 2res | non-owner | in | Paid-in-Full | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 2res | non-owner | out | Monthly Card Autopay | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 2res | non-owner | out | Four-Pay | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 2res | non-owner | out | Paid-in-Full | none (0.00) | 0.00 | 0.00 | agree |
| switched | 0 | owner | in | Monthly Card Autopay | extended | 83.03 | 83.03 | agree |
| switched | 0 | owner | in | Paid-in-Full | none (0.00) | 0.00 | 0.00 | agree |
| switched | 0 | owner | out | Monthly Card Autopay | none (0.00) | 0.00 | 0.00 | agree |
| switched | 0 | owner | out | Paid-in-Full | none (0.00) | 0.00 | 0.00 | agree |
| switched | 0 | non-owner | in | Monthly Card Autopay | none (0.00) | 0.00 | 0.00 | agree |
| switched | 0 | non-owner | in | Paid-in-Full | none (0.00) | 0.00 | 0.00 | agree |
| switched | 0 | non-owner | out | Monthly Card Autopay | none (0.00) | 0.00 | 0.00 | agree |
| switched | 0 | non-owner | out | Paid-in-Full | none (0.00) | 0.00 | 0.00 | agree |
| switched | 1 | owner | in | Monthly Card Autopay | extended | 83.03 | 83.03 | agree |
| switched | 1 | owner | in | Paid-in-Full | none (0.00) | 0.00 | 0.00 | agree |
| switched | 1 | owner | out | Monthly Card Autopay | none (0.00) | 0.00 | 0.00 | agree |
| switched | 1 | owner | out | Paid-in-Full | none (0.00) | 0.00 | 0.00 | agree |
| switched | 1 | non-owner | in | Monthly Card Autopay | none (0.00) | 0.00 | 0.00 | agree |
| switched | 1 | non-owner | in | Paid-in-Full | none (0.00) | 0.00 | 0.00 | agree |
| switched | 1 | non-owner | out | Monthly Card Autopay | none (0.00) | 0.00 | 0.00 | agree |
| switched | 1 | non-owner | out | Paid-in-Full | none (0.00) | 0.00 | 0.00 | agree |
| switched | 1s | owner | in | Monthly Card Autopay | extended | 83.03 | 83.03 | agree |
| switched | 1s | owner | in | Paid-in-Full | none (0.00) | 0.00 | 0.00 | agree |
| switched | 1s | owner | out | Monthly Card Autopay | none (0.00) | 0.00 | 0.00 | agree |
| switched | 1s | owner | out | Paid-in-Full | none (0.00) | 0.00 | 0.00 | agree |
| switched | 1s | non-owner | in | Monthly Card Autopay | none (0.00) | 0.00 | 0.00 | agree |
| switched | 1s | non-owner | in | Paid-in-Full | none (0.00) | 0.00 | 0.00 | agree |
| switched | 1s | non-owner | out | Monthly Card Autopay | none (0.00) | 0.00 | 0.00 | agree |
| switched | 1s | non-owner | out | Paid-in-Full | none (0.00) | 0.00 | 0.00 | agree |
| switched | 2all | owner | in | Monthly Card Autopay | none (0.00) | 0.00 | 0.00 | agree |
| switched | 2all | owner | in | Paid-in-Full | none (0.00) | 0.00 | 0.00 | agree |
| switched | 2all | owner | out | Monthly Card Autopay | none (0.00) | 0.00 | 0.00 | agree |
| switched | 2all | owner | out | Paid-in-Full | none (0.00) | 0.00 | 0.00 | agree |
| switched | 2all | non-owner | in | Monthly Card Autopay | none (0.00) | 0.00 | 0.00 | agree |
| switched | 2all | non-owner | in | Paid-in-Full | none (0.00) | 0.00 | 0.00 | agree |
| switched | 2all | non-owner | out | Monthly Card Autopay | none (0.00) | 0.00 | 0.00 | agree |
| switched | 2all | non-owner | out | Paid-in-Full | none (0.00) | 0.00 | 0.00 | agree |
| switched | 2res | owner | in | Monthly Card Autopay | none (0.00) | 0.00 | 0.00 | agree |
| switched | 2res | owner | in | Paid-in-Full | none (0.00) | 0.00 | 0.00 | agree |
| switched | 2res | owner | out | Monthly Card Autopay | none (0.00) | 0.00 | 0.00 | agree |
| switched | 2res | owner | out | Paid-in-Full | none (0.00) | 0.00 | 0.00 | agree |
| switched | 2res | non-owner | in | Monthly Card Autopay | none (0.00) | 0.00 | 0.00 | agree |
| switched | 2res | non-owner | in | Paid-in-Full | none (0.00) | 0.00 | 0.00 | agree |
| switched | 2res | non-owner | out | Monthly Card Autopay | none (0.00) | 0.00 | 0.00 | agree |
| switched | 2res | non-owner | out | Paid-in-Full | none (0.00) | 0.00 | 0.00 | agree |

### returned_draft_makeup
| enrolled | certs | holder | payment scope | plan | governing | computed | by hand | |
|---|---|---|---|---|---|---|---|---|
| enrolled | 0 | owner | in | Monthly EFT | extended | 519.36 | 519.36 | agree |
| enrolled | 0 | owner | in | Four-Pay | extended | 314.18 | 314.18 | agree |
| enrolled | 0 | owner | in | Paid-in-Full | extended | 286.18 | 286.18 | agree |
| enrolled | 0 | owner | out | Monthly EFT | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 0 | owner | out | Four-Pay | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 0 | owner | out | Paid-in-Full | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 0 | non-owner | in | Monthly EFT | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 0 | non-owner | in | Four-Pay | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 0 | non-owner | in | Paid-in-Full | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 0 | non-owner | out | Monthly EFT | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 0 | non-owner | out | Four-Pay | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 0 | non-owner | out | Paid-in-Full | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 1 | owner | in | Monthly EFT | extended | 519.36 | 519.36 | agree |
| enrolled | 1 | owner | in | Four-Pay | extended | 314.18 | 314.18 | agree |
| enrolled | 1 | owner | in | Paid-in-Full | extended | 286.18 | 286.18 | agree |
| enrolled | 1 | owner | out | Monthly EFT | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 1 | owner | out | Four-Pay | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 1 | owner | out | Paid-in-Full | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 1 | non-owner | in | Monthly EFT | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 1 | non-owner | in | Four-Pay | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 1 | non-owner | in | Paid-in-Full | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 1 | non-owner | out | Monthly EFT | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 1 | non-owner | out | Four-Pay | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 1 | non-owner | out | Paid-in-Full | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 1s | owner | in | Monthly EFT | extended | 519.36 | 519.36 | agree |
| enrolled | 1s | owner | in | Four-Pay | extended | 314.18 | 314.18 | agree |
| enrolled | 1s | owner | in | Paid-in-Full | extended | 286.18 | 286.18 | agree |
| enrolled | 1s | owner | out | Monthly EFT | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 1s | owner | out | Four-Pay | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 1s | owner | out | Paid-in-Full | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 1s | non-owner | in | Monthly EFT | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 1s | non-owner | in | Four-Pay | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 1s | non-owner | in | Paid-in-Full | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 1s | non-owner | out | Monthly EFT | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 1s | non-owner | out | Four-Pay | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 1s | non-owner | out | Paid-in-Full | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 2all | owner | in | Monthly EFT | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 2all | owner | in | Four-Pay | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 2all | owner | in | Paid-in-Full | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 2all | owner | out | Monthly EFT | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 2all | owner | out | Four-Pay | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 2all | owner | out | Paid-in-Full | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 2all | non-owner | in | Monthly EFT | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 2all | non-owner | in | Four-Pay | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 2all | non-owner | in | Paid-in-Full | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 2all | non-owner | out | Monthly EFT | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 2all | non-owner | out | Four-Pay | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 2all | non-owner | out | Paid-in-Full | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 2res | owner | in | Monthly EFT | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 2res | owner | in | Four-Pay | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 2res | owner | in | Paid-in-Full | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 2res | owner | out | Monthly EFT | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 2res | owner | out | Four-Pay | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 2res | owner | out | Paid-in-Full | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 2res | non-owner | in | Monthly EFT | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 2res | non-owner | in | Four-Pay | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 2res | non-owner | in | Paid-in-Full | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 2res | non-owner | out | Monthly EFT | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 2res | non-owner | out | Four-Pay | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 2res | non-owner | out | Paid-in-Full | none (0.00) | 0.00 | 0.00 | agree |
| switched | 0 | owner | in | Monthly EFT | extended | 511.94 | 511.94 | agree |
| switched | 0 | owner | in | Paid-in-Full | extended | 286.18 | 286.18 | agree |
| switched | 0 | owner | out | Monthly EFT | none (0.00) | 0.00 | 0.00 | agree |
| switched | 0 | owner | out | Paid-in-Full | none (0.00) | 0.00 | 0.00 | agree |
| switched | 0 | non-owner | in | Monthly EFT | none (0.00) | 0.00 | 0.00 | agree |
| switched | 0 | non-owner | in | Paid-in-Full | none (0.00) | 0.00 | 0.00 | agree |
| switched | 0 | non-owner | out | Monthly EFT | none (0.00) | 0.00 | 0.00 | agree |
| switched | 0 | non-owner | out | Paid-in-Full | none (0.00) | 0.00 | 0.00 | agree |
| switched | 1 | owner | in | Monthly EFT | extended | 511.94 | 511.94 | agree |
| switched | 1 | owner | in | Paid-in-Full | extended | 286.18 | 286.18 | agree |
| switched | 1 | owner | out | Monthly EFT | none (0.00) | 0.00 | 0.00 | agree |
| switched | 1 | owner | out | Paid-in-Full | none (0.00) | 0.00 | 0.00 | agree |
| switched | 1 | non-owner | in | Monthly EFT | none (0.00) | 0.00 | 0.00 | agree |
| switched | 1 | non-owner | in | Paid-in-Full | none (0.00) | 0.00 | 0.00 | agree |
| switched | 1 | non-owner | out | Monthly EFT | none (0.00) | 0.00 | 0.00 | agree |
| switched | 1 | non-owner | out | Paid-in-Full | none (0.00) | 0.00 | 0.00 | agree |
| switched | 1s | owner | in | Monthly EFT | extended | 511.94 | 511.94 | agree |
| switched | 1s | owner | in | Paid-in-Full | extended | 286.18 | 286.18 | agree |
| switched | 1s | owner | out | Monthly EFT | none (0.00) | 0.00 | 0.00 | agree |
| switched | 1s | owner | out | Paid-in-Full | none (0.00) | 0.00 | 0.00 | agree |
| switched | 1s | non-owner | in | Monthly EFT | none (0.00) | 0.00 | 0.00 | agree |
| switched | 1s | non-owner | in | Paid-in-Full | none (0.00) | 0.00 | 0.00 | agree |
| switched | 1s | non-owner | out | Monthly EFT | none (0.00) | 0.00 | 0.00 | agree |
| switched | 1s | non-owner | out | Paid-in-Full | none (0.00) | 0.00 | 0.00 | agree |
| switched | 2all | owner | in | Monthly EFT | none (0.00) | 0.00 | 0.00 | agree |
| switched | 2all | owner | in | Paid-in-Full | none (0.00) | 0.00 | 0.00 | agree |
| switched | 2all | owner | out | Monthly EFT | none (0.00) | 0.00 | 0.00 | agree |
| switched | 2all | owner | out | Paid-in-Full | none (0.00) | 0.00 | 0.00 | agree |
| switched | 2all | non-owner | in | Monthly EFT | none (0.00) | 0.00 | 0.00 | agree |
| switched | 2all | non-owner | in | Paid-in-Full | none (0.00) | 0.00 | 0.00 | agree |
| switched | 2all | non-owner | out | Monthly EFT | none (0.00) | 0.00 | 0.00 | agree |
| switched | 2all | non-owner | out | Paid-in-Full | none (0.00) | 0.00 | 0.00 | agree |
| switched | 2res | owner | in | Monthly EFT | none (0.00) | 0.00 | 0.00 | agree |
| switched | 2res | owner | in | Paid-in-Full | none (0.00) | 0.00 | 0.00 | agree |
| switched | 2res | owner | out | Monthly EFT | none (0.00) | 0.00 | 0.00 | agree |
| switched | 2res | owner | out | Paid-in-Full | none (0.00) | 0.00 | 0.00 | agree |
| switched | 2res | non-owner | in | Monthly EFT | none (0.00) | 0.00 | 0.00 | agree |
| switched | 2res | non-owner | in | Paid-in-Full | none (0.00) | 0.00 | 0.00 | agree |
| switched | 2res | non-owner | out | Monthly EFT | none (0.00) | 0.00 | 0.00 | agree |
| switched | 2res | non-owner | out | Paid-in-Full | none (0.00) | 0.00 | 0.00 | agree |

### switch_down_payment
| enrolled | certs | holder | payment scope | plan | governing | computed | by hand | |
|---|---|---|---|---|---|---|---|---|
| enrolled | 0 | owner | in | Monthly EFT | extended | 153.88 | 153.88 | agree |
| enrolled | 0 | owner | in | Four-Pay | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 0 | owner | in | Paid-in-Full | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 0 | owner | out | Monthly EFT | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 0 | owner | out | Four-Pay | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 0 | owner | out | Paid-in-Full | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 0 | non-owner | in | Monthly EFT | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 0 | non-owner | in | Four-Pay | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 0 | non-owner | in | Paid-in-Full | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 0 | non-owner | out | Monthly EFT | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 0 | non-owner | out | Four-Pay | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 0 | non-owner | out | Paid-in-Full | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 1 | owner | in | Monthly EFT | extended | 153.88 | 153.88 | agree |
| enrolled | 1 | owner | in | Four-Pay | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 1 | owner | in | Paid-in-Full | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 1 | owner | out | Monthly EFT | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 1 | owner | out | Four-Pay | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 1 | owner | out | Paid-in-Full | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 1 | non-owner | in | Monthly EFT | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 1 | non-owner | in | Four-Pay | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 1 | non-owner | in | Paid-in-Full | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 1 | non-owner | out | Monthly EFT | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 1 | non-owner | out | Four-Pay | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 1 | non-owner | out | Paid-in-Full | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 1s | owner | in | Monthly EFT | extended | 153.88 | 153.88 | agree |
| enrolled | 1s | owner | in | Four-Pay | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 1s | owner | in | Paid-in-Full | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 1s | owner | out | Monthly EFT | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 1s | owner | out | Four-Pay | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 1s | owner | out | Paid-in-Full | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 1s | non-owner | in | Monthly EFT | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 1s | non-owner | in | Four-Pay | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 1s | non-owner | in | Paid-in-Full | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 1s | non-owner | out | Monthly EFT | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 1s | non-owner | out | Four-Pay | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 1s | non-owner | out | Paid-in-Full | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 2all | owner | in | Monthly EFT | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 2all | owner | in | Four-Pay | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 2all | owner | in | Paid-in-Full | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 2all | owner | out | Monthly EFT | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 2all | owner | out | Four-Pay | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 2all | owner | out | Paid-in-Full | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 2all | non-owner | in | Monthly EFT | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 2all | non-owner | in | Four-Pay | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 2all | non-owner | in | Paid-in-Full | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 2all | non-owner | out | Monthly EFT | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 2all | non-owner | out | Four-Pay | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 2all | non-owner | out | Paid-in-Full | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 2res | owner | in | Monthly EFT | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 2res | owner | in | Four-Pay | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 2res | owner | in | Paid-in-Full | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 2res | owner | out | Monthly EFT | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 2res | owner | out | Four-Pay | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 2res | owner | out | Paid-in-Full | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 2res | non-owner | in | Monthly EFT | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 2res | non-owner | in | Four-Pay | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 2res | non-owner | in | Paid-in-Full | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 2res | non-owner | out | Monthly EFT | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 2res | non-owner | out | Four-Pay | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 2res | non-owner | out | Paid-in-Full | none (0.00) | 0.00 | 0.00 | agree |
| switched | 0 | owner | in | Monthly EFT | extended | 148.32 | 148.32 | agree |
| switched | 0 | owner | in | Paid-in-Full | none (0.00) | 0.00 | 0.00 | agree |
| switched | 0 | owner | out | Monthly EFT | none (0.00) | 0.00 | 0.00 | agree |
| switched | 0 | owner | out | Paid-in-Full | none (0.00) | 0.00 | 0.00 | agree |
| switched | 0 | non-owner | in | Monthly EFT | none (0.00) | 0.00 | 0.00 | agree |
| switched | 0 | non-owner | in | Paid-in-Full | none (0.00) | 0.00 | 0.00 | agree |
| switched | 0 | non-owner | out | Monthly EFT | none (0.00) | 0.00 | 0.00 | agree |
| switched | 0 | non-owner | out | Paid-in-Full | none (0.00) | 0.00 | 0.00 | agree |
| switched | 1 | owner | in | Monthly EFT | extended | 148.32 | 148.32 | agree |
| switched | 1 | owner | in | Paid-in-Full | none (0.00) | 0.00 | 0.00 | agree |
| switched | 1 | owner | out | Monthly EFT | none (0.00) | 0.00 | 0.00 | agree |
| switched | 1 | owner | out | Paid-in-Full | none (0.00) | 0.00 | 0.00 | agree |
| switched | 1 | non-owner | in | Monthly EFT | none (0.00) | 0.00 | 0.00 | agree |
| switched | 1 | non-owner | in | Paid-in-Full | none (0.00) | 0.00 | 0.00 | agree |
| switched | 1 | non-owner | out | Monthly EFT | none (0.00) | 0.00 | 0.00 | agree |
| switched | 1 | non-owner | out | Paid-in-Full | none (0.00) | 0.00 | 0.00 | agree |
| switched | 1s | owner | in | Monthly EFT | extended | 148.32 | 148.32 | agree |
| switched | 1s | owner | in | Paid-in-Full | none (0.00) | 0.00 | 0.00 | agree |
| switched | 1s | owner | out | Monthly EFT | none (0.00) | 0.00 | 0.00 | agree |
| switched | 1s | owner | out | Paid-in-Full | none (0.00) | 0.00 | 0.00 | agree |
| switched | 1s | non-owner | in | Monthly EFT | none (0.00) | 0.00 | 0.00 | agree |
| switched | 1s | non-owner | in | Paid-in-Full | none (0.00) | 0.00 | 0.00 | agree |
| switched | 1s | non-owner | out | Monthly EFT | none (0.00) | 0.00 | 0.00 | agree |
| switched | 1s | non-owner | out | Paid-in-Full | none (0.00) | 0.00 | 0.00 | agree |
| switched | 2all | owner | in | Monthly EFT | none (0.00) | 0.00 | 0.00 | agree |
| switched | 2all | owner | in | Paid-in-Full | none (0.00) | 0.00 | 0.00 | agree |
| switched | 2all | owner | out | Monthly EFT | none (0.00) | 0.00 | 0.00 | agree |
| switched | 2all | owner | out | Paid-in-Full | none (0.00) | 0.00 | 0.00 | agree |
| switched | 2all | non-owner | in | Monthly EFT | none (0.00) | 0.00 | 0.00 | agree |
| switched | 2all | non-owner | in | Paid-in-Full | none (0.00) | 0.00 | 0.00 | agree |
| switched | 2all | non-owner | out | Monthly EFT | none (0.00) | 0.00 | 0.00 | agree |
| switched | 2all | non-owner | out | Paid-in-Full | none (0.00) | 0.00 | 0.00 | agree |
| switched | 2res | owner | in | Monthly EFT | none (0.00) | 0.00 | 0.00 | agree |
| switched | 2res | owner | in | Paid-in-Full | none (0.00) | 0.00 | 0.00 | agree |
| switched | 2res | owner | out | Monthly EFT | none (0.00) | 0.00 | 0.00 | agree |
| switched | 2res | owner | out | Paid-in-Full | none (0.00) | 0.00 | 0.00 | agree |
| switched | 2res | non-owner | in | Monthly EFT | none (0.00) | 0.00 | 0.00 | agree |
| switched | 2res | non-owner | in | Paid-in-Full | none (0.00) | 0.00 | 0.00 | agree |
| switched | 2res | non-owner | out | Monthly EFT | none (0.00) | 0.00 | 0.00 | agree |
| switched | 2res | non-owner | out | Paid-in-Full | none (0.00) | 0.00 | 0.00 | agree |

### direct_bill_switch
| enrolled | certs | holder | payment scope | plan | governing | computed | by hand | |
|---|---|---|---|---|---|---|---|---|
| enrolled | 0 | owner | in | Monthly EFT | extended | 542.81 | 542.81 | agree |
| enrolled | 0 | owner | in | Four-Pay | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 0 | owner | in | Paid-in-Full | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 0 | owner | out | Monthly EFT | base | 458.36 | 458.36 | agree |
| enrolled | 0 | owner | out | Four-Pay | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 0 | owner | out | Paid-in-Full | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 0 | non-owner | in | Monthly EFT | base | 557.38 | 557.38 | agree |
| enrolled | 0 | non-owner | in | Four-Pay | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 0 | non-owner | in | Paid-in-Full | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 0 | non-owner | out | Monthly EFT | base | 557.38 | 557.38 | agree |
| enrolled | 0 | non-owner | out | Four-Pay | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 0 | non-owner | out | Paid-in-Full | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 1 | owner | in | Monthly EFT | extended | 567.81 | 567.81 | agree |
| enrolled | 1 | owner | in | Four-Pay | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 1 | owner | in | Paid-in-Full | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 1 | owner | out | Monthly EFT | base | 458.36 | 458.36 | agree |
| enrolled | 1 | owner | out | Four-Pay | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 1 | owner | out | Paid-in-Full | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 1 | non-owner | in | Monthly EFT | base | 557.38 | 557.38 | agree |
| enrolled | 1 | non-owner | in | Four-Pay | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 1 | non-owner | in | Paid-in-Full | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 1 | non-owner | out | Monthly EFT | base | 557.38 | 557.38 | agree |
| enrolled | 1 | non-owner | out | Four-Pay | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 1 | non-owner | out | Paid-in-Full | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 1s | owner | in | Monthly EFT | extended | 542.81 | 542.81 | agree |
| enrolled | 1s | owner | in | Four-Pay | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 1s | owner | in | Paid-in-Full | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 1s | owner | out | Monthly EFT | base | 458.36 | 458.36 | agree |
| enrolled | 1s | owner | out | Four-Pay | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 1s | owner | out | Paid-in-Full | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 1s | non-owner | in | Monthly EFT | base | 557.38 | 557.38 | agree |
| enrolled | 1s | non-owner | in | Four-Pay | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 1s | non-owner | in | Paid-in-Full | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 1s | non-owner | out | Monthly EFT | base | 557.38 | 557.38 | agree |
| enrolled | 1s | non-owner | out | Four-Pay | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 1s | non-owner | out | Paid-in-Full | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 2all | owner | in | Monthly EFT | base | 458.36 | 458.36 | agree |
| enrolled | 2all | owner | in | Four-Pay | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 2all | owner | in | Paid-in-Full | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 2all | owner | out | Monthly EFT | base | 458.36 | 458.36 | agree |
| enrolled | 2all | owner | out | Four-Pay | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 2all | owner | out | Paid-in-Full | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 2all | non-owner | in | Monthly EFT | base | 557.38 | 557.38 | agree |
| enrolled | 2all | non-owner | in | Four-Pay | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 2all | non-owner | in | Paid-in-Full | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 2all | non-owner | out | Monthly EFT | base | 557.38 | 557.38 | agree |
| enrolled | 2all | non-owner | out | Four-Pay | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 2all | non-owner | out | Paid-in-Full | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 2res | owner | in | Monthly EFT | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 2res | owner | in | Four-Pay | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 2res | owner | in | Paid-in-Full | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 2res | owner | out | Monthly EFT | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 2res | owner | out | Four-Pay | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 2res | owner | out | Paid-in-Full | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 2res | non-owner | in | Monthly EFT | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 2res | non-owner | in | Four-Pay | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 2res | non-owner | in | Paid-in-Full | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 2res | non-owner | out | Monthly EFT | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 2res | non-owner | out | Four-Pay | none (0.00) | 0.00 | 0.00 | agree |
| enrolled | 2res | non-owner | out | Paid-in-Full | none (0.00) | 0.00 | 0.00 | agree |
| switched | 0 | owner | in | Monthly EFT | extended | 560.24 | 560.24 | agree |
| switched | 0 | owner | in | Paid-in-Full | none (0.00) | 0.00 | 0.00 | agree |
| switched | 0 | owner | out | Monthly EFT | base | 488.02 | 488.02 | agree |
| switched | 0 | owner | out | Paid-in-Full | none (0.00) | 0.00 | 0.00 | agree |
| switched | 0 | non-owner | in | Monthly EFT | base | 587.04 | 587.04 | agree |
| switched | 0 | non-owner | in | Paid-in-Full | none (0.00) | 0.00 | 0.00 | agree |
| switched | 0 | non-owner | out | Monthly EFT | base | 587.04 | 587.04 | agree |
| switched | 0 | non-owner | out | Paid-in-Full | none (0.00) | 0.00 | 0.00 | agree |
| switched | 1 | owner | in | Monthly EFT | extended | 585.24 | 585.24 | agree |
| switched | 1 | owner | in | Paid-in-Full | none (0.00) | 0.00 | 0.00 | agree |
| switched | 1 | owner | out | Monthly EFT | base | 488.02 | 488.02 | agree |
| switched | 1 | owner | out | Paid-in-Full | none (0.00) | 0.00 | 0.00 | agree |
| switched | 1 | non-owner | in | Monthly EFT | base | 587.04 | 587.04 | agree |
| switched | 1 | non-owner | in | Paid-in-Full | none (0.00) | 0.00 | 0.00 | agree |
| switched | 1 | non-owner | out | Monthly EFT | base | 587.04 | 587.04 | agree |
| switched | 1 | non-owner | out | Paid-in-Full | none (0.00) | 0.00 | 0.00 | agree |
| switched | 1s | owner | in | Monthly EFT | extended | 560.24 | 560.24 | agree |
| switched | 1s | owner | in | Paid-in-Full | none (0.00) | 0.00 | 0.00 | agree |
| switched | 1s | owner | out | Monthly EFT | base | 488.02 | 488.02 | agree |
| switched | 1s | owner | out | Paid-in-Full | none (0.00) | 0.00 | 0.00 | agree |
| switched | 1s | non-owner | in | Monthly EFT | base | 587.04 | 587.04 | agree |
| switched | 1s | non-owner | in | Paid-in-Full | none (0.00) | 0.00 | 0.00 | agree |
| switched | 1s | non-owner | out | Monthly EFT | base | 587.04 | 587.04 | agree |
| switched | 1s | non-owner | out | Paid-in-Full | none (0.00) | 0.00 | 0.00 | agree |
| switched | 2all | owner | in | Monthly EFT | base | 488.02 | 488.02 | agree |
| switched | 2all | owner | in | Paid-in-Full | none (0.00) | 0.00 | 0.00 | agree |
| switched | 2all | owner | out | Monthly EFT | base | 488.02 | 488.02 | agree |
| switched | 2all | owner | out | Paid-in-Full | none (0.00) | 0.00 | 0.00 | agree |
| switched | 2all | non-owner | in | Monthly EFT | base | 587.04 | 587.04 | agree |
| switched | 2all | non-owner | in | Paid-in-Full | none (0.00) | 0.00 | 0.00 | agree |
| switched | 2all | non-owner | out | Monthly EFT | base | 587.04 | 587.04 | agree |
| switched | 2all | non-owner | out | Paid-in-Full | none (0.00) | 0.00 | 0.00 | agree |
| switched | 2res | owner | in | Monthly EFT | none (0.00) | 0.00 | 0.00 | agree |
| switched | 2res | owner | in | Paid-in-Full | none (0.00) | 0.00 | 0.00 | agree |
| switched | 2res | owner | out | Monthly EFT | none (0.00) | 0.00 | 0.00 | agree |
| switched | 2res | owner | out | Paid-in-Full | none (0.00) | 0.00 | 0.00 | agree |
| switched | 2res | non-owner | in | Monthly EFT | none (0.00) | 0.00 | 0.00 | agree |
| switched | 2res | non-owner | in | Paid-in-Full | none (0.00) | 0.00 | 0.00 | agree |
| switched | 2res | non-owner | out | Monthly EFT | none (0.00) | 0.00 | 0.00 | agree |
| switched | 2res | non-owner | out | Paid-in-Full | none (0.00) | 0.00 | 0.00 | agree |

Scored values unchanged. Carried, not regressed: every item closed in rounds 1-14.
