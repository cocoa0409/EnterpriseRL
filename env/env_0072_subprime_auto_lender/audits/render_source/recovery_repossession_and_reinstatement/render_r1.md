# render_r1 — recovery (env_0072_subprime_auto_lender) — STOP before rendering

Gate: `VERDICT revision_3: task0=PASS task1=PASS charter=CLEAN` (read, OK).
Source: tasks/recovery_repossession_and_reinstatement/recovery.extended.yaml + task_tools.py.
Nothing was written under docs/recovery/ or .doc_render_staging/recovery/.

## STOP finding S1 — a rule sentence lists the complete factor set of both expense-payment policies (XF A.3 / A.6)

Quoted text (identical in four places):

> "Storage that a borrower's own reinstatement expense payment or redemption expense payment covers is charged by the storage day rate, grace days, storage clock and keyless lot handling that the rule for that payment states; storage posted on release or sale, and storage in the expenses a reinstatement quote states, is charged at storage_fee_per_day_usd for each chargeable day (recovery_msr_chargeable_storage_days, recorded in chargeable_days)."

Locations:
- `recovery_ext_redemption_expense_payment.overwrite[3].replaced_by` (base `recovery_evt_expenses`, superseded clause "storage at storage_fee_per_day_usd for each chargeable day (recovery_msr_chargeable_storage_days, recorded in chargeable_days)") and the same sentence as `recovery_ext_redemption_expense_payment.rule` sentence 4.
- `recovery_ext_reinstatement_expense_payment.overwrite[3].replaced_by` (same base clause) and `recovery_ext_reinstatement_expense_payment.rule` sentence 4.

Defect: "the storage day rate, grace days, storage clock and keyless lot handling" names, by their business names, exactly the four declared factors of each policy (`lot_day_rate`, `lot_grace_days`, `storage_clock_start`, `keyless_lot_handling`) — a complete component inventory, and also a completion signal (four named components, nothing else). The words "keyless lot handling" are the factor id with spaces. The sentence is a non-compute rule atom of each policy, so it has no legal home:
- hub: forbidden (factor names, component inventory, completion cue);
- computation document: must be silent about variation; this sentence announces a separate day rate, grace days, clock and keyless per-day handling;
- a factor document: may not name or describe another factor;
- the base expense-schedule document: the retiring document does not carry the new basis, and there it would become a corpus-wide index of both policies' factors.
It also defines the charge "by ... that the rule for that payment states" — inside the redemption policy that defers the reinstatement-payment storage to the sibling policy (XF A.6 "as another policy figures it"; sibling scope per D.20 should be named, not deferred with an inventory).

Rendering around it (paraphrasing away the list) would change source text, so it is not done.

Suggested fix (per policy, naming its own scope and the sibling's by name, no inventory), e.g. in the redemption policy:
"Storage that the borrower's own redemption expense payment covers is charged as this rule sets out, and storage that the borrower's own reinstatement expense payment covers is charged by its own reinstatement expense payment rule; storage posted on release or sale, and storage in the expenses a reinstatement quote states, is charged at storage_fee_per_day_usd for each chargeable day (recovery_msr_chargeable_storage_days, recorded in chargeable_days)."
and the mirror in the reinstatement policy. Update `overwrite[3].replaced_by` and rule sentence 4 together in both policies so they stay verbatim (no compute_basis quotes this sentence; no compute change; no seed change).

## Scan that came back clean (no action)

- compute_basis: every quote is verbatim in its rule (all 5 policies); every prerequisite `policy_source` is verbatim in its rule; every `baseline.rule` is in its rule; every superseded_clause is in its base rule and every replaced_by in its ext rule.
- Factor independence: no factor binding reads another factor's binding in any policy; shared reads (`end_offset`, `posted_open`, `latest_sale_date`) are plain bindings. Assembly sentences of the agency fee, surrender fee, sale period and both payments are generic and fix the order.
- Rule vs compute edges checked: business-day sale-period conversion for every mailing weekday (Mon..Sun give 16,16,16,18,18,17,16 days); extended-state Monday roll; weekend clock shift (Sat 2 / Sun 1); impound clock from latest impound_lot_charges posting; grace window `<= 30` days; returned-payment look-back excludes exactly 12 months (DSL `0 <= MONTHS < 12`); fee minimums make every posted fee positive (no 0.00 prerequisite edge); `2026-01-05` is a Monday; every record word names a schema field/enum value.
- No factor id is a substring of a tool name. All five target tools are exclusive. Tool events (expense posted, notice sent, expense settled) have `triggers: []`.

## Observation (not blocking)

- `pay_redemption_recovery_expenses_4986a691` / `pay_reinstatement_recovery_expenses_82a1a2b9` docstrings say the borrower pays "through a certified payment channel"; the body records no channel (only settlement_method paid_by_borrower). It describes the payment, not a recorded effect; low risk, logged for the coordinator.

VERDICT render_r1: STOP source=S1
