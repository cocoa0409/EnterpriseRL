# plan — membership_dues_and_changes (env_0081), M=2

Draws (draw_counts.py --tasks 2):
- task 0: prerequisite_problems=1, factor_counts=[5, 6]
- task 1: prerequisite_problems=3, factor_counts=[6, 5, 4, 6]  (>=2 value_input edges)

Band: phones 6175550100-6175550119, LH-8110000-LH-8110999, surnames Ravensworth/Okonkwo/Lindahl/Carrasquillo/Fairbanks/Tanabe,
employers Northgate Cabinetry Inc./Bellwether Freight LLC, ref prefix 81, house numbers 1100-1199.

DSL facts (check_compute.py): HIST primitives scoped to this membership; X* reads may target visit_appointments (holding
table counts as the category's table); eq filters only; within_months window from NOW; string date compare ok; no
subscripting; P() only for the holding's own tier (another tier's price needs K restating the catalogue figure).

## Task 0 — tree: billing-error correction (agent) -> cancellation settlement (owner=user, root)
- root A0 membership_ext_cancel_settlement (user tool cancel_membership_*): the patient's own cancellation of an
  immediate (annual) tier; the write books the cancel request (applied), status cancelled, cancelled_date and the
  refund line on the current period's line (refund consequence, owner_ruling (a)). scored refund_amount. 6 factors.
- prereq B0 membership_ext_billing_error_refund (agent tool refund_*): overcharged difference on the current
  period's dues line refunded with refund_reason billing_error. 5 factors. value_input into A0 (cash collected on the line).

## Task 1 — tree: goodwill credit + referral credit -> past-due payment (owner=user) -> upgrade (root, agent)
- G membership_ext_goodwill_credit (agent) 6 factors
- R membership_ext_referral_credit (agent) 5 factors
- P membership_ext_past_due_payment (user; PCI new card) 4 factors; value_input from G and R (open credit drawn)
- U membership_ext_upgrade_proration (agent, root) 6 factors; state+value from P (status active; the recovered
  dues line is the current period's line)

Order of work: task 0 policies -> tools -> seed -> persona -> verify -> GT -> gates; then task 1.
Scratch: /tmp/membership_dues_and_changes_0081/. Worklog: worklog.md (XF tables per policy).
