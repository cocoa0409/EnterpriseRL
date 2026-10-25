# KB audit — rebuild_contracts_and_draws (product rebuild)

## revision_1 (2026-10-25)

Per-task part verdicts:
- task 0: runtime PASS (blind = GT on every argument: 2478.65; 19956.83 with draw 3 / carrier_direct / conditional_final / ""); bijection RED (KB-B1); dependency_form PASS.
- task 1: runtime PASS (blind = GT: 423.40; 2026-10 / 78.98; ach / 6746.42); bijection PASS; dependency_form PASS.

KB RED:
- KB-B1 (KB-BIJECTION, policy rebuild_ext_final_draw, factor fd_state_retainage): docs/rebuild/texas_statutory_retention_on_final_draw_1f5a3780.json renders the fall-through tier "for every other final draw the final retainage is the tier's retainage percentage of the remainder" only as "For every other final draw the Texas retention plays no part in the final retainage." — the tier's method is not carried in the factor document. Untriggered in task 0 (tier 1 taken); no gold impact.

Source-side items (not KB defects):
- SRC-1 (RULE-2/E2 seed, task 0): claim file c38092d5 carries deductible_due 2500.00 with no deductible assessment line (claims clause: assessed once when the file opens on net-of-deductible arrangements); gold reads only the claim-file field. No gold impact.
- SRC-2 (XF A9 source wording): final-draw rule and fd_state_retainage tier 2 "the greater of that amount less the retainage withheld ... and the tier's retainage percentage of the remainder" has two groupings; compute is MX(A - X, Y) and the KB renders that reading. No gold impact.
- SRC-3 (XF D8 observation): the payoff rule books the remobilization fee and resumes work once the priced payment posts; no tool of the difficulty writes either; GT books neither. No gold impact; BLUEPRINT-KNOWN candidate.

Checks: E5 PASS both tasks; every cross-product row the gold reads priced against the published claims/water docs (only SRC-1 found); own-category seeded history reproduces under the published current rules in both tasks; no R6 factors; nothing conditional (all products published). Gates cited from kb_snapshot_r1.txt (DOCS OK, TRACEABILITY OK); not re-run by this auditor (check_traceability excluded by the brief).

KBVERDICT revision_1: task0=RED task1=PASS kb=KB-B1 src=SRC-1,SRC-2,SRC-3

## revision_2 (2026-10-25)

- Gate: policy-side `VERDICT revision_15: task0=PASS task1=PASS charter=CLEAN`; kb_snapshot_r2.txt check_docs DOCS OK, check_traceability TRACEABILITY OK, all other gates OK.
- KB-B1 closed (Texas final-draw factor doc now states the fall-through method). SRC-2 closed (source tier 2 has one grouping; doc equivalent). SRC-1 / SRC-3 coordinator-decided, not re-raised.
- Only one rebuild doc changed; no scored figure moves; seeded worlds and GT identical; other source rewordings (deductive change-order part, payoff carrier money) are already pinned to the same reading by the unchanged docs' tables and worked figures. No new defect, no regression.

KBVERDICT revision_2: task0=PASS task1=PASS kb=CLEAN src=NONE
