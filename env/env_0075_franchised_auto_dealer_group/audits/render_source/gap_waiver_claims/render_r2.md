# gap render scan round 2 (env_0075, D=gap_waiver_claims) - STOPPED before writing any doc
Gate: VERDICT revision_7: task0=PASS task1=PASS charter=CLEAN. Sweep: every compute_basis quote, replaced_by, prerequisite sentence and baseline sentence is verbatim in its rule; every superseded clause is verbatim in its base policy; compute_basis keys equal compute bindings; no binding claimed by two factors.

## Round-1 findings: all closed
A1 closed (result gated on replacement_vehicle_credit_usd > 0; rule "A waiver whose replacement_vehicle_credit_usd is 0.00 receives no replacement vehicle credit").
A2 closed (line_loss_date now reads the paid GAP balance line only, matching "the loss date of the paid line").
A3 closed ("both the months it was in force and its unused months").
A4 closed (loan-to-value ladder now reads "the recorded cap amount, ... rounded half up to the cent").
A5 closed (stale ladder now "the date its refund was last paid to the lienholder ... the earlier of those dates").
A6 closed (courtesy ladder "or no completed cancellation request is on file, no courtesy credit is added"; compute gated on COUNT completed > 0).
B1 closed (framing clause removed; ladder names customer_request or vehicle_sold_or_traded).
C1-C7 closed (all overwrite and assembly sentences now generic: "the ladders of this rule select", "every amount a ladder adds ...").
D1-D4 closed (late_pay_credit, recorded_stamp, request_reason, unused_months/unused_share, term_months, settlement_date, recorded_cap_amount, line_paid_date, line_loss_date, credit_age, signed_date moved into their factors; deferred now plain; negative equity now read from the claim line).
E1, E2 closed.

## New finding (present in round 1 too; missed then)
N1 gap_ext_addon_overpayment_recovery, fee add-back: rule vs compute at the no-lienholder-refund edge.
Rule: "Fee add-back ladder for an overpayment reversal: where both the plan and the service contract were cancelled on or after the loss date for the reason customer_request or vehicle_sold_or_traded, the plan's cancellation_fee_usd and the contract's cancellation_fee_usd are added to the counted refunds; where only one of them was, that product's cancellation_fee_usd is added; where neither was, nothing is added."
Compute fee_addback: CPARAM(maintenance fee) only "if (plan_refund > 0 and DAYS(line_loss_date, plan_closed) >= 0 and (plan_reason == ...))", and the vsc fee only "if (contract_refund > 0 and ...)", where plan_refund / contract_refund are the refunds PAID TO THE LIENHOLDER; plan_reason is also read only from a maintenance_refund_paid ledger entry.
Probe: the Kessler Care plan is cancelled after the loss for customer_request and its refund computes 0.00 (no refund paid entry), or its refund is paid to the customer; the Kessler Shield contract is cancelled after the loss for customer_request with its refund paid to the lienholder. Rule: both fees are added. Compute: only the contract's fee.
Fix direction: either state in the ladder that a product's fee is added only where that product's refund was paid to the lienholder (and read its reason from its cancellation record), or drop the refund>0 gate in compute and read the plan's reason from its completed cancellation request.
