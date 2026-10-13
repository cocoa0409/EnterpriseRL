# Worklog — membership_fees_renewals_and_cardholders (category: membership, M=2)

## Step 0 — difficulty pre-check
- Read references (product_extended.yaml, task_tools.py, task.json), blueprint.yaml, products/membership.yaml, db_schema.json, share_tools.py, and the gate scripts.
- Identity: find_customers -> verify_customer_identity (K=2 of phone/email/DOB/ZIP).
- Draw (draw_counts.py --tasks 2):
  - task 0: prerequisite_problems=1, factor_counts=[4,4]
  - task 1: prerequisite_problems=3, factor_counts=[5,5,4,4]
- Headroom plan: task 0 claims the lapse -> upgrade pair (renewal of an expired membership, mid-year upgrade);
  task 1 claims the Business Plus exit chain (Plus guarantee claim, downgrade difference, removed add-on card fee, cancellation).
  Each task tool / policy is claimed once. No other renewal-of-lapse policy is created, so the state
  "membership active with a fee for its current year" is brought about by exactly one write.
- Tool suffixes (uuid4 hex[:8], one per tool): 7a245505 pay_lapsed_membership_renewal (user), 9f256f7b upgrade_membership_to_plus (agent),
  e9c317f9 confirm_plus_guarantee_claim (user), 0adda8cc refund_downgrade_difference (agent),
  e7b2031f refund_removed_addon_card_fee (agent), 5b4de829 confirm_membership_cancellation (user).
- Blueprint quirk noted: every membership_fee_refunded write inherits guarantee_claim_window / one_claim_per_year
  (action args membership_id + term_end_date) and refund_status; full_refund_window is retired by the cancellation policy's overwrite.
- FK quirk: replay gate treats "" in an FK field as dangling, so non-applicable FK fields in seed rows are null.

## Task 0 — CLOSED
- Tree: membership_ext_upgrade_fee (root, agent) <- membership_ext_lapsed_renewal_fee (user pays). value_input, state form.
- Gold: renewal_fee 53.50 (baseline 45.50), upgrade_fee 51.25 (baseline 65.00); skip-renewal -> upgrade 0.00.
- Per-task gates all OK (extended, task_tools, replay 43/43, solvability, compute, grounding, cross_fire).

## Task 1 — CLOSED
- Tree: cancellation (root, user) <- removal refund (agent, state_due); cancellation <- downgrade difference (agent, state_due) <- guarantee claim (user). 3 value_input edges, all state form.
- Gold: guarantee 23.60, downgrade 41.54, removal 47.34, cancellation 172.49; three topological orders give identical values and hash.
- Revision: cancellation expected 172.51 -> 172.49 (certificate is 29.28, not 29.26).
- Per-task gates all OK.

## Final closure
- All 6 extended policies are covered: task 0 = {lapsed_renewal_fee, upgrade_fee}, task 1 = {plus_guarantee_refund, downgrade_difference_refund, addon_removal_refund, cancellation_refund}. Scopes and tools are disjoint.
- Final gates (no --task): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK (suite branches mean 42.00, steps mean 14.50, history max 49, branches max 58), GROUNDING OK, SCOPE OK.
- CACHE-DIFF is informational only. It reads a non-existent amount_usd field, so its "true" value of 0.0 is an artifact; the seeded balances equal the ledger.
- TRACEABILITY NOT OK is expected: the published KB (docs/) is not rendered yet, so the hidden tool names have no visible source. Re-run after render.
- Temporary authoring scripts (_build_*, _verify.py, id maps) were deleted.

## Round 2 — policy-task audit rework (audits/policy_task/membership_fees_renewals_and_cardholders/)
- D1, D2: lapsed-renewal overwrite now also declares status_tier_renewal and renewal_dating "... charged that tier's annual fee".
- D3: Student discounted-term-limit conversion added to the tier the new year is held at.
- D4: cancellation overwrite declares the base after-window twelfths sentence.
- D5: guarantee overwrite declares "... the primary member may claim the difference"; the rule now states the entitlement.
- E1: anniversary test made boundary-inclusive (MONTHS(NOW, expiry) >= -anchor).
- F1: renewal_tier_fee removed as a factor (tier selection moved into baseline.rule); new factor renewal_conversion_grace_credit added. Task 0 renewal 53.50 -> 43.50, upgrade 51.25 -> 61.25.
- F2: repeat_claim_share relabelled parameter.
- F3: upgrade_fee_basis conjunct changed to "no earlier upgrade difference fee" (first upgrade).
- O5, O6, O7, O8, O9: wording fixes in the charter, docstrings and edge condition.
- Seed: task 1 automatic-renewal charges dated on the expiry date. Task 1 values unchanged.
- Gates re-run (per task and full); temporary patch scripts deleted.

## Round 3 — audit revision_2
- E2: rf_student_terms now nets out duplicate-refunded charges. A new rule sentence counts paid Student years; the base sentence "A Student Club membership also keeps its tier only while membership_msr_student_terms is below the tier's discounted_term_limit." is declared in overwrite.
- O13: the four superseded fee sentences now map to a scoping sentence. The lapsed-renewal fee replaces the plain annual fee only when an expired membership is renewed; on-time renewals, new memberships, and conversions or downgrades at on-time renewal stay on base.
- O14: task 1 rationale override list and Dashiell fee date corrected; task 0 rationale override list updated to round 3.
- Gate block re-run; temporary patch script deleted.
