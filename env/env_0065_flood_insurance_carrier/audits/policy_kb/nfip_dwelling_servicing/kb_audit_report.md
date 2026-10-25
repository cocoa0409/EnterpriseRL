# KB audit report — env_0065_flood_insurance_carrier / nfip_dwelling_servicing (product dwelling)

## revision_1 (round 1, 2026-10-17)

### Entry conditions (Step 0)
- Policy-side verdict supplied: "VERDICT revision_9: task0=PASS task1=PASS / charter=CLEAN".
- Gate snapshot `.audit_views/kb/nfip_dwelling_servicing/snapshot_kb1.txt`: check_docs dwelling "DOCS OK" (74 docs: policy 17, hub 7, baseline 7, factor 37, facet 6); check_traceability "TRACEABILITY OK" (0.json 22/0, 1.json 21/0) and post-publication "TRACEABILITY OK"; validate_scenario "VALID" (10 tasks, 353 documents). Not re-run by the auditor (Step 5 re-run is due only once every part passes).
- Runtime view: 0.runtime.json sha256 2589539…9808, 1.runtime.json sha256 70a2ab5…b08b (verified). DB access only through `db_query.py` (tool-shaped); blind phase not contaminated.
- Inputs complete.

### Per-task verdicts
| Task | KB-RUNTIME (blind vs GT) | KB-BIJECTION | KB-EXPLICIT |
|---|---|---|---|
| 0 (renewal remittance ← deductible ← contents ← building) | PASS — every scored argument, date and the tool order reproduced blind | **RED — K1** | PASS |
| 1 (replacement cancellation ← signed request; ← insured increase) | PASS — every scored argument reproduced blind | PASS | PASS |

Details: `audits/runtime_context/nfip_dwelling_servicing/{0,1}.md` (blind_answer frozen, sha256 in `{0,1}.freeze.sha256`; gt_comparison appended) and `audits/policy_kb/nfip_dwelling_servicing/{0,1}.md`.

### KB defects
- **K1 — KB-BIJECTION RED (task 0 scope).** The replaced_by of overwrite 3 of `dwelling_ext_coverage_increase_charge`, `dwelling_ext_contents_increase_charge` and `dwelling_ext_deductible_decrease_charge` (base `dwelling_waiting_period`, clause "When both exceptions could apply, the one giving the earlier effective date is recorded.") is carried without its carve-out "a pending increase of the contents limit / building limit … and a pending deductible decrease … recorded for a loan transaction follow the rules written for them, a pending coverage increase the insured requested with no loan transaction follows the rules written for such requests". Affected: building_loan_increase_waiting_days_3dea5f4e, contents_loan_increase_waiting_days_4b526cce, deductible_loan_decrease_waiting_days_90f5d03d, paragraph "**Rule.**", which each read "…; every other transaction keeps the rule that when both exceptions could apply, the one giving the earlier effective date is recorded." Effect: each document assigns the earlier-date tie-break to the two sibling loan-request kinds, while their own documents say "the loan-transaction dating governs whenever it applies" — a literal conflict between documents for a loan request with a qualifying map revision whose premium arrived before the closing. Task 0's figures do not depend on it (no map revision on the policy); the bijection fails regardless. The semantics not carried: the scope carve-out of that replaced_by.

### Source-side findings (not KB-translation defects)
- **S1 — rule vs compute, line order (low; untriggered in both tasks).** `dwelling_ext_insured_increase_charge` rule and `rise_basis_rule` ladder put the EC-re-rate line before "when the request carries no full-term risk premium from the rating engine, there is no rise", so read in order a request with no engine figure and a later re-rate credit would take "the request's full-term risk premium less the risk premium booked for the term at its start"; the compute guards the figure first (`rise: … if (request_figure != None and request_figure > 0 and rerate_after_request …) else (0 if request_figure … <= 0 …)`). The three loan policies order the lines figure-first. The KB (insured_increase_rise_basis) follows the compute ("no rise arises from it under any line"), which is why it is not counted as a KB defect.

### Policy-side notes (no verdict)
- The computation documents carry the rule's generic assembly sentences ("Where more than one date applies … the latest of them", "adjustments first, then limits, then the credits booked with the remittance", "the part of the term the rules give back", "dated the latest of the dates the rules of this schedule give"). They come from the rule text, name no factor quantity, and are the scenario's XF assembly design; they do let a reader infer that modifiers exist. Recorded here, not as KB-EXPLICIT.
- Base retirements are written as "no longer in force; superseded by the current basis" while the in-force remainder (scoped "every other … keeps the base rule") lives in the overwriting hub/factor document. Faithful as carried, apart from K1.
- Realism: both worlds read as plausible WYO servicing (loan-closing endorsements paid by check before closing, EC re-rate credit held on account and set off at renewal, HFIAA primary-residence credit after a move evidenced by the sale of the HomeFlood-insured former home; backdated replacement cancellation returning the never-run current term while the ended term stays earned). No realism RED.
- Cross-product: all seven corpora on disk; other products read Dwelling records (HomeFlood occupancy/loyalty/transfer factors, Excess primary-loss surcharge, nfipcom's own cancellation/HFIAA rules) but each names its own product and none restates or contradicts a Dwelling rule used here. Coverage gap as defined by the skill: cross-product contradictions are only structurally suppressed.

### Closing checklist (Step 5)
Not closed: K1 is open. Audit files correspond one-to-one with tasks 0 and 1; first revision.

KB VERDICT round 1: task0=KB-BIJECTION RED task1=PASS
kb=K1
src=S1

## revision_2 (re-audit round 2, 2026-10-17)

### Gate and entry
- GATE FIRST: `_difficulty.md` tail "VERDICT revision_10: task0=PASS task1=PASS" / "charter=CLEAN"; newest docs/dwelling file 20:13:49Z > dwelling.extended.yaml 20:10:22Z. Passed.
- Run by the auditor: `check_docs.py env/env_0065_flood_insurance_carrier dwelling` → "[PASS] mechanical gates … DOCS OK"; `check_traceability.py env/env_0065_flood_insurance_carrier/tasks/nfip_dwelling_servicing` → "0.json 22 0 True / 1.json 21 0 True / TRACEABILITY OK"; `mkruntime.py nfip_dwelling_servicing` → 0.runtime.json sha256=258953958a86…9808, 1.runtime.json sha256=70a2ab5230a2…b08b (unchanged).
- Same DB access path; seeded worlds re-read and unchanged; GT arguments and closures unchanged.
- contamination_disclosure: round-2 blind answers are not policy-blind (source revealed in revision_1); recorded in runtime_context revision_2.

### Round-1 items
| Id | Round-1 finding | Round-2 state |
|---|---|---|
| K1 | loan waiting-days "Rule." dropped the sibling carve-out of the overwrite-3 replaced_by | **closed** — carve-out carried verbatim in all three documents |
| S1 | insured rise rule listed the EC line before the no-figure line, compute checked figure first | **closed** — rule, ladder and compute now in the same order (no figure first); KB carries it |

### Regression and cross-product sweep
All 74 dwelling documents were re-rendered; re-read in full for the task paths and re-scanned mechanically for every rule sentence, overwrite, factor tier, prerequisite sentence (each verbatim, one home), tool-name placement (each only in its own document) and retired clause (all 11 marked, remainders in force). No new defect. Cross-product on the final seven-product corpus: other products only read Dwelling records; none restates or contradicts a Dwelling rule. Base-parameter remnant: settings table cap row 18 % on every tier vs the extended 18 / 25 % residence-based cap — scoped by the computation document, not moving any scored value.

### Per-task verdicts (revision_2)
| Task | KB-RUNTIME | KB-BIJECTION | KB-EXPLICIT |
|---|---|---|---|
| 0 | PASS | PASS | PASS |
| 1 | PASS | PASS | PASS |

### Closing checklist (Step 5)
Audit files one-to-one with tasks 0 and 1, revision_1 preserved, revision_2 appended; all three parts PASS for both tasks; check_docs and check_traceability re-run on the final form (lines above). Difficulty closed.

KB VERDICT round 2: task0=PASS task1=PASS
kb=CLEAN
src=NONE
