# mold_remediation_jobs — plan (M=2)

Draw (draw_counts.py --tasks 2):
- task 0: prerequisite_problems=2, factor_counts=[6, 6, 5]
- task 1: prerequisite_problems=1, factor_counts=[4, 4]

## Structural constraints found while reading (drive the design)
- Mold lifecycle: the only by:user step is signing (scheduled -> authorized); containment (authorized -> remediating)
  is by:system, so no agent write on the same job can follow a signing within one call.
- Compute may read only its own job + OTHER categories (check_extended rejects own-category CFIELD/XSUM), so every
  value_input edge must sit on one job.
- Customer-owned writes therefore: (a) signing + the deposit the charter groups with it (scheduled job), or
  (b) the customer's own payment on a job past containment. Flat fees (late fee, surcharge, cancellation fee) are
  not hosts for computations (XF E4).
- Agent writes legal on a scheduled job: booking, cancelling, late-cancellation fee, and (via a scoped overwrite of
  the scope-line status gate) the pre-removal asbestos sampling the base rule itself places before any removal.
- Customers are homeowners with no service agreement (XF E9 not engaged).

## Design thesis (FINAL — supersedes the draft that was here)
Task 0 [6,6,5] (fan-in, 2 value_input edges): J0 Extensive living-area job, condo, built 1948, still scheduled,
  linked to an approved claim file with a small mold sublimit and to a company water job still drying.
  - P0a mold_ext_presample_line (agent, 6) book_mold_presample_d4275783: pre-removal asbestos sampling line, dated
    the opened date, billable while scheduled (scoped overwrite of the scope status gate).
  - P0b mold_ext_workplan_line (agent, 6) book_mold_workplan_1501986a: supervisor work-plan visit line (scheduled
    supervisor hours by schedule adders), dated the opened date, billable while scheduled (scoped overwrite).
  - R0 mold_ext_signing_deposit (user, 5) sign_mold_agreement_2b99f603: customer signs + pays signing deposit in one
    act; deposit = scope deposit less coverage credit (floor 0) + lead prepay + access raise + short-notice raise +
    booked charges - customer payments.
Task 1 [4,4] (chain, 1 value_input edge): J1 Standard job, condo, cleared, Carrier Program claim (approved, O&L limit,
  program price write-off), black-water origin with early customer release.
  - P1 mold_ext_disposal_line (agent, 4) book_mold_disposal_772b05b2: bagged debris haul-off line.
  - R1 mold_ext_insured_share (user, 4) pay_mold_insured_share_5816092f: insured's own share = charges - carrier
    payable (min(mold covered net of O&L carve, allowance) + O&L carve) - company-absorbed write-offs - payments.
Factor detail lives in mold.extended.yaml and the worklog tables.
