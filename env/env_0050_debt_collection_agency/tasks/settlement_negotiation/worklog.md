# settlement_negotiation worklog

## Rework round 2 (audit: audits/policy_task/settlement_negotiation/_difficulty.md, 0.md, 1.md)

Blueprint untouched. Every base clause that an item lands on is routed around with a declared `overwrite` in the extended charter.

### Charter findings
- **F1 (Two-Payment bundle, undeclared override).**
  - The Two-Payment bundle now applies only when both hold:
    - at least two accounts are placed under the agreement;
    - every one of them is open: validation period, active, arranged or hardship hold.
  - Any account in dispute hold, still only placed, or closed (paid in full, settled in full, returned to the client) stops the bundle.
  - Declared as a new overwrite of the base stop sentence of `settle_agg_same_client_bundle`. The new sentence also replaced the sentence-2 `replaced_by`, the rule, the baseline and the basis.
  - Compute: added `two_agreement` and `two_bundle_blocked` (EXISTS on the five blocking statuses). `two_bundle_reduction` now requires that nothing blocks the bundle.
  - Task 0 value unchanged: 204.0.
- **F2 (mislabelled method factors).**
  - Call acceptance: the window-rate factor became `tp_returned_payment_day_convention`.
    - Two or more returns: the first payment is due on the next business day after acceptance.
    - One return: a weekend due date moves back to the Friday before it.
    - None: the window stands.
  - E-sign acceptance: same structure, as `ha_returned_payment_signing_convention`.
  - Hardship extension: the hold-extension multiplier became the honest parameter factor `hx_hold_extension_history` (+4 / +2 / 0). The new method factor is `hx_payment_channel_convention`.
    - Last posted payment by ACH: a weekend due date moves back to Friday.
    - Mailed check or money order: it moves forward to Monday.
    - Otherwise: the due date stands.
  - Each method factor now changes the algorithm: which day the payment is placed on.
- **F3 (`hx_hold_tier_allowance` unreal).** Factor, rule sentence and compute binding removed. The factor count stays 6 because of the new method factor above.
- **Retuning, so every factor bears weight with the conventions active.**
  - Call acceptance: stage cuts 3 / 1.
  - E-sign: stage 12 / 8, opening 6 / 4, lapsed 6 / 3.
  - Hardship extension:
    - Standard grant 5.
    - Size and signing-window factors turned into allowances: size +3 / +2, short window +4 / +2.
    - The prose order sentence was updated.

### Charter observations
- **O1.** The acceptance and Hardship extension docstrings now say only "as returned by the settlement lookup".
- **O2.** No change needed. Neither world triggers the base plan or hold or supersede orders (single cancelled plan, ended hold, no open offers).
- **O3.** No change needed. Each world has one hold and one plan per account, so the first `CFIELD` row is the qualifying one.
- **O4.** "never less than X dollars" was replaced in all three offer rules with "an amount below X dollars is never offered under this rule". The compute floor and the `min_amount_usd` params were removed.
- **O5.** The three←two `condition` was aligned to the sentence ("balance due under 500.00").
- **O6.** The Lump-Sum return anchor now says "never fewer than zero" in the rule and the basis. Compute uses `MX(0, …)`.
- **O7.** Resolved (the target holding is the placed account). No change.
- **O8.** The age-anchor method is kept as a definitional measure choice. No change.
- **O9.** The `effect` of hardship_offer←lump was rewritten in general terms.

### Task 0
- **T0-F1 (= F2).** Fixed as above. Acceptance gold 6 → **9**: the shortened window is 11 days and ends Sunday 2026-10-18. With one return in the span it moves back to Friday 2026-10-16.
  - Verify run: result 9; factor baselines 11, 12, 13, 12; all-baseline 15.
- **T0-F2 (no near-miss in C1).** Added a 50.00 debit-card payment on the second account dated 2025-10-06. It is not after 2025-10-07, so it is outside the dormancy span. Placement raised 612.40 → 662.40 so the balance due stays 436.90. EC[5] and the trace now name the near-miss.
- **T0-F3.** Offer docstring examples changed from 46.5 / 40.0 to 62.5.
- **T0-F4.** `edges[1].why_false` and its evidence now name the expired Two-Payment offer 8123075c (closed 2026-03-13) and explain why it is not an open offer.
- **T0-O2.** `no_user_hint` rewritten to acknowledge the conditional persona line.
- **T0-O3.** EC[12] `account_id` tracing quotes the persona verbatim. EC[14] "step 11" corrected to "step 12".
- **Propagation.**
  - computations[2]: expected, trace, sensitivity, baseline_result.
  - EC[14]: args, objective, tracing.
  - solvability step-14 business_effect.
  - design_rationale cards, plus a rework section.

### Task 1
- **T1-F1 (= F2).** Fixed as above.
  - E-sign gold 18 → **17**: the adjusted window is 18 days and ends Saturday 2026-10-24, so it moves back to Friday 2026-10-23.
  - Hardship extension gold stays **14**: 15 days granted lands on Saturday 2026-11-07. The last posted payment was by ACH, so it moves back to Friday 2026-11-06, after 3 November.
  - Verify runs: e-sign 17 (factor baselines 18, 24, 22, 21, 15; all-baseline 30); extension 14 (15, 13, 13, 13, 13, 13; all-baseline 5).
  - Payment dates stay on or before the 28th: 10-23, 11-22, 12-22, and after the extension 11-06, 12-06, 01-05.
- **T1-F2 (= F3).** Hold-tier factor removed.
- **T1-F3.** Hardship offer docstring example changed from 30.0 to 62.5.
- **T1-F4.** EC[15] `account_id` tracing now states the store card's balance due of 407.00 and that it is arranged under an accepted Lump-Sum with 225.00 still to pay.
- **T1-O1.** The persona now says part of the lump sum was paid in September and one payment bounced. That matches the ledger.
- **T1-O2.** The closing trigger now requires the agent to confirm the first payment has been pushed back.
- **T1-O3.** Both payment-record rules (Lump-Sum and Hardship) now state that a payment later returned is included.
- **T1-O4.** `no_user_hint` rewritten to acknowledge the conditional lines.
- **T1-O5.** design_rationale no longer calls `lx_hardship_history` multi-source.
- **Propagation.**
  - computations[2] and [3]: expected, traces, sensitivity, baselines.
  - EC[17] and EC[19]: args, objectives, tracing.
  - prerequisite_closure flips and load-bearing text.
  - solvability business_effects for steps 17 and 19.
  - design_rationale cards, plus a rework section.

### Gates after rework
EXTENDED OK; TASK TOOL CONTRACT OK; REPLAY OK; SOLVABILITY OK; COMPUTE OK (suite means branches 96.50, steps 17.50; history_rows_max 8; branches_max 98); GROUNDING OK; CACHE-DIFF INFO; SCOPE OK. validate_scenario: only the 7 settlement_negotiation required-document errors (KB not rendered).
Scratch and authoring scripts live in /tmp/env0050_rework_settle/; nothing temporary is left in this directory.

## Rework round 3 (audit revision_2 sections of _difficulty.md, 0.md, 1.md)

Blueprint untouched. No scored value changed: task 0 is 204.0 / 739.0 / 9 and task 1 is 9 / 1384.0 / 17 / 14, re-verified on the handling-time worlds.

- **T0-R2-F1 (stale EC[10] proof text).** Two fields of `evaluation_criteria[10].argument_uniqueness_tracing` were rewritten:
  - `balance_at_offer` now reconciles 662.40 placed − 50.00 (payment of 2025-10-06) − 175.50 (charity-care credit) = 436.90.
  - `bundle_applied` now quotes the full round-2 bundle condition: at least two accounts, all open. It concludes from both accounts being active and none being in a blocking status.
- **T0-R2-O1.** design_rationale [Problem-tree card] no longer says the persona never names the second account. It now describes the conditional line, consistent with `prerequisite_closure.no_user_hint`.
- **T1-R2-O1.** `evaluation_criteria[8].necessity` no longer names the removed hold-tier factor.
- **R2-O2 (0-day window edge case).** Both acceptance conventions keep the one-return tier, which rolls a weekend due date back to the Friday before it. When that Friday would be the acceptance date itself, the date now moves forward to the Monday after it instead. Changed in each policy:
  - the rule sentence;
  - the compute binding (`tp_day_convention` / `ha_signing_convention`);
  - the compute_basis quotation;
  - the ladder method text.

  Neither world reaches the case. Task 0 rolls Sunday 2026-10-18 back to Friday 2026-10-16 (9 days). Task 1 rolls Saturday 2026-10-24 back to Friday 2026-10-23 (17 days). Verify runs reproduce the same results and factor baselines.
- **R2-O1 (closed accounts block the Two-Payment bundle).** Kept as declared. The readable records cannot count only the open accounts under an agreement: placements are counted from the ledger, and holding status can only be tested for existence. So the declared rule makes every placed account open-or-blocking. No world has a closed account under the agreement. Recorded as a known design limit.
- **R2-O3 (returned ACH payment decides the channel convention).** Kept as declared ("a payment later returned included"). Deterministic, and the figures are unchanged.
- **Proof sweep of both tasks.** I re-read every equation and date claim in `prerequisite_closure`, computations and factor traces, tracing and necessity text, solvability_contract and design_rationale against the verify output.
  - One further stale statement was found and fixed. The task 0 seed_consistency of the expired Two-Payment offer now explains its 436.90 balance with the 662.40 placement, the charity credit and the 2025-10-06 payment.
  - No other stale figure remained.
  - Each task's design_rationale gained a [Rework round 3] section.

### Gates after round 3
EXTENDED OK; TASK TOOL CONTRACT OK; REPLAY OK; SOLVABILITY OK; COMPUTE OK (suite means branches 97.50, steps 17.50; history_rows_max 8; branches_max 99); GROUNDING OK; CACHE-DIFF INFO; SCOPE OK. validate_scenario: only the 7 settlement_negotiation required-document errors (KB not rendered). No __pycache__ left; scratch in /tmp/env0050_rework_settle/.

## Rework round 4 (render-layer audits: audits/policy_kb/settlement_negotiation/0.md, 1.md; audits/runtime_context/settlement_negotiation/0.md, 1.md)

Both runtime_context files PASS with no items. The policy_kb files PASS and record source-side notes P1–P4, D1 and scan targets 1–5; each is handled below. Blueprint untouched, and task_tools.py byte-identical.

**No scored value moved.** Re-verified on the handling-time worlds:
- task 0: 204.0 / 739.0 / 9;
- task 1: 9 / 1384.0 / 17 / 14.
- All factor baselines and fall-backs are unchanged.

- **P2 / scan target 2 (weekend move where the Friday before falls before the acceptance date).** The compute already moved a weekend due date forward to Monday whenever the move back would give fewer than one day. The rule named only the case where that Friday *is* the acceptance date. A literal compute would have produced a negative window, so the rule wording was brought to the compute.
  - In both acceptance rules, "where that Friday would be the acceptance date itself" became "where that Friday would fall on or before the acceptance date".
  - The same change was made in the compute_basis quotation and the tier-2 `method` text of `tp_returned_payment_day_convention` and `ha_returned_payment_signing_convention`. The compute is unchanged.
- **Scan target 4 (Lump-Sum superseded-plan allowance, "that plan" against the compute's count over all plans).** Compute brought to the rule; rule text unchanged.
  - New binding `lx_superseded_plan_id`: the plan on the settled account whose close reason is superseded_by_settlement.
  - `lx_plan_missed` now counts missed installments with that `plan_id` only, and `lx_plan_allow` tests that plan.
  - The factor bindings and the plan `cross_category` reads and note were updated. Result 9 is unchanged: one plan, one missed installment.
- **P1 / scan target 5 (bundle "holds at least two accounts placed under the agreement" against the compute's count of placement entries).**
  - Three-Payment: compute brought to "holds"; rule text unchanged. New bindings `three_agreement` and `three_accounts_not_held`. The bundle reduction applies only when at least two placements stand under the agreement and no account under it is in dispute hold, still only placed, or closed. The rule's own scope sentence already puts those cases outside the rule.
  - Two-Payment: its rule already says "and every one of them is open", and its compute already blocks the five statuses. Only "status" was added to its declared account reads.
  - Account placement entries are "one row per placement" in the account charter, so one entry per account.
  - Result 739.0 is unchanged: both accounts are active.
- **P3 (the 100.0 authority-floor reading).** The three offer overwrites retired the whole base floor clause, including "a stage whose authority floor is 100.0 is not offered that programme". That contradicted the base parameter gloss.
  - The `superseded_clause` of the settle_offer_authority floor overwrite in `settle_ext_two_payment_bundle_offer`, `settle_ext_three_payment_offer` and `settle_ext_hardship_offer` now quotes the clause only up to "but never below the programme's approval floor for the same stage". It is still a verbatim substring of the base rule.
  - The 100.0 sentence therefore stays in force for these offers, and an Early-Out account is not offered these programmes.
  - No world account is at Early-Out, so values are unchanged.
- **D1 (computation documents' "every reduction that applies" / "any shortenings that apply").** Kept as a design note.
  - These assembly sentences are the compute_basis of the non-factor bindings and are also overwrite `replaced_by` text.
  - There is no rule-versus-compute gap, and the audit recorded the note as source-forced and not scored.
  - Rewording would change published rule and overwrite sentences for no semantic gain.
- **Scan target 3 (Lump-Sum hardship allowance reads one hold record per account).** Kept as a known limit. The readable records allow a dated status test of only one hold record per account. The store card carries exactly one hold.
- **Scan target 1 (qualifying-hold retirement) and P4.** Nothing to change. The no-op retirement for Two-/Three-Payment is scoped correctly, and the clause stays in force for the Hardship Settlement.
- **Proof sweep of both tasks**, covering prerequisite_closure, computations and factor traces, tracing and necessity text, solvability_contract, design_rationale, and every equation.
  - Task 0, EC[12] `bundle_applied`: dropped "false applies only to a lone account"; it now states both accounts are held and active.
  - Task 0, computations[0] and [1] trace bundle lines: both accounts active and held.
  - Task 0, round-3 rationale wording: brought to the round-4 Friday rule.
  - Task 1, rationale LS card: superseded-plan scope stated.
  - Task 1, computations[0] trace and EC[10] tracing: missed installment "recorded on that plan".
  - Task 1, round-3 rationale wording: brought to the round-4 Friday rule.
  - Each task's design_rationale gained a [Rework round 4] section.
  - No other stale claim found.

**Changed published text, for re-rendering `docs/settle/`:**
1. Rule of `settle_ext_three_payment_call_acceptance`, the "Three-Payment returned-payment day convention" sentence: "… moved back to the Friday before it, or forward to the Monday after it where that Friday would be the acceptance date itself; …" now reads "… where that Friday would fall on or before the acceptance date; …". Factor `tp_returned_payment_day_convention`, ladder tier 2 `method`: "… where that Friday is the acceptance date" now reads "… where that Friday falls on or before the acceptance date".
2. Rule of `settle_ext_hardship_esign_acceptance`, the "Hardship Settlement returned-payment signing convention" sentence: the same replacement. Factor `ha_returned_payment_signing_convention`, ladder tier 2 `method`: the same replacement.
3. `overwrite[settle_offer_authority floor clause].superseded_clause` in the Two-Payment, Three-Payment and Hardship offer policies: now ends at "… but never below the programme's approval floor for the same stage" (the trailing "; a stage whose authority floor is 100.0 is not offered that programme." is no longer retired).
4. `cross_category` note of `settle_ext_lump_sum_extension` (plan), only if notes are rendered: "The plan on the settled account closed as superseded by the settlement, and the missed installments recorded on that plan alone, decide the Lump-Sum superseded-plan allowance."

Prerequisite sentences, every other rule sentence, params, ladder values and tool docstrings are byte-identical.

### Gates after round 4
- EXTENDED OK
- TASK TOOL CONTRACT OK
- REPLAY OK
- SOLVABILITY OK
- COMPUTE OK (suite means branches 100.50, steps 17.50; history_rows_max 8; branches_max 101)
- GROUNDING OK
- CACHE-DIFF INFO
- SCOPE OK
- TRACEABILITY OK (0.json copied 17 missing 0; 1.json copied 23 missing 0)
- validate_scenario: VALID

No __pycache__ left; scratch is in /tmp/env0050_rework_settle/.
