# plan / worklog — finch_circle_rewards (env_0061), M=2 — state after rework r2
draw: t0 prerequisite_problems=1 factor_counts [6,6]; t1 prerequisite_problems=2 factor_counts [5,6,6]
policies / tools:
 T0 root loyalty_ext_missing_points_credit (USER file_missing_points_claim_8cff3bd6) <- loyalty_ext_card_floor_tier (AGENT apply_card_status_floor_f82dd75f), value_input earn_rate
 T1 root loyalty_ext_courtesy_note_reissue (USER request_courtesy_note_reissue_8b12a7a8) <- loyalty_ext_return_points_deduction (AGENT book_return_points_deduction_52e06983, value_input return_pct)
                                                                                     <- loyalty_ext_note_reinstatement (AGENT reinstate_returned_note_1c0adac4, state_gate)
factors (r2):
 M (r4): event_day_anchor[M, decides bonus event indicator], late_event_share (from purchase date), price_type_share, card_bonus_rate, financing_share, card_standing_share; overwrites: base missing-points credit + base request sentence (most recent unlinked kept purchase) + two base earning sentences (purchase/event; card bonus), scoped to the claimed unit
 F (r4): goodwill_anchor[M: goodwill scale on days from enrolment / review date / opened date], card_spend_allowance (net of credits), allowance_standing (late-fee count), tailoring_allowance, bridal_allowance (active Wedding Registry), apparel_allowance; floor tier credit = base map plumbing
 R: refund_basis[M], card_basis[M], event_clawback (return reason), exchange_relief, frequency_cushion, balance_relief (unit's earned points vs balance); refund destination/tax plain reads
 N: share_basis[M], fee_share (over refunded merchandise before the fee), expired_original, return_speed, cardmember_uplift
 C: tier_days, card_days, lapse_cut, registry_days (Wedding only), shopping_days, return_share_rule[M, decides halving/reduction/standard method]; result binding assembles; overwrites: reissue eligibility (most recently lapsed note) + courtesy expiry
worlds (r2):
 T0 Marisol Vance (r3): card opened as Mastercard, mid-year upgrade to Platinum Mastercard after a 2025 pre-enrolment charge crossed the threshold; monthly statements all paid in full (no interest/fees); enrolled in February at Member (missed floor = state_due prerequisite); YTD qualifying spend below Silver; unlinked mattress order (pillow returned); Wedding Registry
 T1 Theodore Lindqvist: Gold, Store Card Plus (annual-review date); espresso return with charter-formula restocking fee, reason wrong size or fit; replacement purchase; lapsed conversion note; Wedding Registry
rule (r4): no factor reads another factor's binding (checked transitively); every result binding assembles the factor quantities as its result sentence; each baseline carries the result sentence plus defaults.
status: full gate block green, traceability OK against the rendered KB (r4). Audit items closed per rework_r2/r3/r4_claims.md.
scratch: /tmp/finch_circle_rewards_0061/ (removed at finish)
## REWORK r3 (audit revision_2: task 0 seed RED + R2-O1..O4)
- T0 card re-laid by simulating card charter: single 2025-09-05 handbag crosses Plat MC threshold -> mid-year upgrade, status_review_date within 3 business days; pre-enrolment coat Nov 2025; monthly statements on closing day with charter minimums, every statement paid in full by due date (no interest/late fee); mattress order still deferred_interest_12.
- T0 loyalty: YTD qualifying spend kept below Silver threshold (knife set price lowered); Member at enrolment documented as the missed floor (state_due owed, the task's prerequisite).
- R2-O1 hyphen folds (rewrap with break_on_hyphens=False everywhere); R2-O2 drop unreachable floor_credit guard; R2-O3 declare most-recent-unlinked narrowing as scoped overwrite of loyalty_missing_points request sentence.
- add find_card_statements read in T0 (steps shift +1).
## REWORK r4 (render_r1_loyalty: factor independence, result assembly, rounding sentence)
- M: dated day folded into event_day_anchor (method, decides bonus event indicator); late_event_share keyed on days from purchase date; new price_type_share (mattress -> clearance); event multiplier plain; result assembles all; baseline carries combination + defaults.
- F: delay anchor + goodwill merged (goodwill_anchor, method); new apparel_allowance (order); result assembles all.
- R: refund_dest/refund_tax plain; balance_relief keyed on unit's earned points vs balance; full combination in result; replaced_by rounding wording fixed.
- N: result already assembles; baseline gets combination sentence.
- C: return_share_rule decides share_mode; result assembles day count + mode.
- T1 values must not move; T0 values move (re-derive).
