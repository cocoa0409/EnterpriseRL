# plan — hardware_procurement_orders (env_0069), M=2

## Draws (scripts/draw_counts.py --tasks 2)
- task 0: prerequisite_problems=2 (3 problems), factor_counts=[4,5,4]
- task 1: prerequisite_problems=3 (4 problems), factor_counts=[5,5,6,6]

## Design constraints found at Step 0 (why this shape)
- DSL history primitives are scoped to ONE hardware order; own-category cross reads are forbidden, so every
  value_input edge must stay inside one order; cross-order dependencies can only be state gates.
- Owner=user numeric writes in this charter: a payment amount (pure ledger reconciliation — no factor can move a
  payoff without an unbooked adjustment) or requested_qty (no policy-rich quantity). So the customer's own
  writes that carry a genuine multi-factor figure are the two signed acts whose base event declares an
  in-category trigger: the signed quote approval (triggers the deposit invoice) and the signed post-PO
  cancellation (triggers the cancellation fee). Each user tool = signed act + its declared trigger row.
- quote_issued needs a distributor cost; the only record source is an existing order, so every quote this
  difficulty issues re-quotes an existing order's line (same part, same cost, same quantity).
- Infrastructure orders always carry a deposit, so cancelling one leaves an order credit owed (state_due) that
  must be in the same tree.

## Task 0 — endpoint re-type (Standard Endpoint order -> Staged Endpoint order), 3 problems
- hardware_ext_endpoint_cancellation (user, on_request, 4 factors): client e-signs the post-PO cancellation of the
  plain laptop order; tool books the cancellation and its fee.
- hardware_ext_staged_requote (agent, on_request, 5 factors): re-quote of the cancelled order's line as a Staged
  Endpoint Order; credits the cancellation fee when re-quoted within the re-order window (value_input from C).
- hardware_ext_endpoint_approval_deposit (user, on_request, ROOT, 4 factors): client e-signs the staged quote;
  deposit invoiced (value_input from the re-quote total).
- Edges: approval <- requote (value_input), requote <- cancellation (value_input).

## Task 1 — infrastructure upgrade with deposit (Network Equipment order), 4 problems
- hardware_ext_network_cancellation (user, 5 factors): signed post-PO cancellation of the 24-port switch order + fee.
- hardware_ext_cancelled_deposit_credit (agent, state_due, 5 factors): order credit returning the paid deposit
  of the cancelled order, net of the non-refundable items the schedule retains.
- hardware_ext_lapsed_quote_reissue (agent, 6 factors): re-issue of the lapsed 48-port quote at current terms
  with the post-lapse price hold.
- hardware_ext_network_approval_deposit (user, ROOT, 6 factors): signed approval of the re-issued quote + deposit.
- Edges: approval <- reissue (value_input), approval <- deposit credit (state_gate: no live paid deposit on the
  order it replaces), deposit credit <- cancellation (value_input).

## Identifier band
phones 91955505xx; EIN4 5000-5999; PIN 5xxxxx; org names & contact surnames Q-T; persona-stated refs 50000-59999.

## Progress
- [x] T0 done (policies, tools, task 0, per-task gates green)
- [ ] policies T1  - [ ] tools T1  - [ ] task 1 json  - [ ] gates T1  - [ ] final gates

## Task 1 (revised after the target-holding gate finding) — network upgrade, 4 problems [5,5,6,6]
- Constraint: every computation's target holding must be seeded (check_compute floor reads initial_state);
  value_input edges stay within one holding. Y (48-port quote, lapsed, still quoted) and X (24-port order,
  ordered, 50% deposit paid) are both seeded.
- hardware_ext_infrastructure_cancellation_fee (user sign_infrastructure_cancellation_1779b7d3, 6 factors): fee on X.
- hardware_ext_cancelled_deposit_credit (agent post_deposit_credit_9245a342, state_due, 5): order credit returning
  X's paid deposit, by credit form (method) less bench/handling/rush/project-coordination retentions.
- hardware_ext_lapsed_quote_reissue (agent reissue_lapsed_quote_93c9a091, 5): re-dates and re-totals Y.
- hardware_ext_infrastructure_approval_deposit (user sign_build_approval_1b1ae884, ROOT, 6): approval + deposit of Y.
- Edges: approval <- reissue (value_input), approval <- deposit credit (state_gate), deposit credit <- cancellation
  (value_input via the cancellation date / fee).
- T0 overwrites to be amended so sibling overwrites name each other's scope (XF C.17).
- [x] T1 done (policies, tools, task 1, per-task gates green)  - [x] final gates 7/7 green

## Round 2 rework plan (audit revision_1: T0-F1..F4, T1-F1, T1-F2, CG-1..CG-4; XF 1-26)
- Worlds: ONE ClearPath agreement per client with a tier change on it (T0 Essentials go-live 2024-03-11 -> Professional
  eff 2025-02-01; T1 Standard go-live 2023-11-13 -> Professional eff 2024-03-01), 36-month terms (onboarding fee waived),
  go-live baseline seat change + baseline proration, every monthly fee + payment, late fees + payments, signed tier-change
  request. No security holding at all (Professional needs no Sentinel). T0 licensing: Business Premium P1Y annual with
  order form, initial-purchase licence change, two annual cycle charges + payments (admin fee waived: Professional/
  Essentials include M365 admin). T1 project: one in-progress Quick Start Project with its deposit invoice + payment.
- CG-1/realism: P1 drop tenure freight (constant freight in the >=7-day build) + new expedite forfeit (rush);
  P2 replace Sentinel EDR with Defender onboarding keyed on the M365 plan; P3 replace Sentinel relief with managed-spend
  ratio relief; P4 drop sensor rework (constant return freight in build) + tenure loyalty points; P5 rebuilt: baseline =
  deposit less full bench staging, method = bench basis (none/pro-rata/flat), params handling/expedite/coordination/
  managed goodwill all ungated with 0 fall-through; P6 re-prices the unit (markup reduction factor, tool takes unit
  price), staging multi-source (tier AND in-progress project), sensor charge removed; P7 Sentinel relief -> managed-spend
  ratio relief.
- CG-2 generic combination sentences; CG-3 project reads via EXISTS by class (largest class in progress decides);
  CG-4 P5 replaced_by names the endpoint sibling.
- Probe tables + method all-pairs tables -> worklog; proof-text sweep; gates; claims list.

## round 4 plan (CG-5, CG-6, T1-R3-F1)
- Constraint found: check_compute requires every factor's OWN bindings to call an evidence primitive (non-transitive),
  so a factor whose only read is a shared plain binding fails. Route: a selection read by several factors becomes a
  plain binding only where every reader keeps its own distinct evidence; otherwise the second reader moves to a
  distinct, realistic record so no selection is shared. Gold values must not move.
- P1: PO age stays with po_age_build only; expedite_forfeit reads the quote-approval age (rush processing starts at
  approval; base rush_fee_usd is "rush processing ahead of the queue").
- P2: licensing reads become plain b_lic_e5 / b_lic_bp_e3 stated once; autopilot keeps EXISTS(active ClearPath);
  defender adds the agreement's m365_administration_included (policy push needs tenant administration); the
  ClearPath tier stays only in tier_rush_rate; fee_credit_basis's whole-fee tier reads the 12-month late-fee count.
- P6: tier name only in reissue_markup_reduction; staging reads network_device_management_included; rush reads
  technical_account_manager / dedicated_account_manager (factor renamed reissue_account_rush).
- P7: seat_count only in infra_seat_relief; spend relief reads the latest ClearPath monthly fee (XLATEST) while an
  agreement is active.
- CG-6: P5 opening sentence loses "once the order has been cancelled after its purchase order"; sweep all rules.
- T1-R3-F1: the two 2026-09-15 strings -> 2026-09-01; mechanical date/amount/arithmetic sweep of both tasks.
