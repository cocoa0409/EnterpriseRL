# KB-doc policy audit — env_0065_flood_insurance_carrier / lender_placed_flood_programs (product forceplaced), round 1

Auditor: independent KB-audit agent, 2026-10-17. Skill: erl-kb-doc-policy-audit. Brief: /tmp/erl0065_coord/kbaudit_forceplaced_r1.txt.

## Entry conditions (cited, not re-run)
- Policy-side verdict: `VERDICT revision_11: task0=PASS task1=PASS / charter=CLEAN`.
- Gate snapshot `.audit_views/kb/lender_placed_flood_programs/snapshot_kb1.txt` (2026-10-17T18:50:42Z): `[check_docs forceplaced] ... docs=59 roles={'policy': 10, 'facet': 7, 'factor': 30, 'baseline': 6, 'hub': 6} ... DOCS OK`; `[check_traceability post-publication] TRACEABILITY OK`; extended / task-tool / replay / solvability / compute / grounding / cross-fire OK. `[validate_scenario] INVALID` is attributed by the snapshot to the unpublished dwelling docs ("required document not found" lines filtered); not a defect of this difficulty.
- Runtime views 0.runtime.json sha256 6a803e59…6395 and 1.runtime.json sha256 ab37f8bf…f8aa0, hashes re-verified. DB access: db_query.py only (blind on the DB side for both tasks).
- Isolation: blind answers frozen (0.md sha256 2cdd560d…4d79, 1.md sha256 f8116e96…fd09) before reading extended.yaml / task_tools.py / tasks/*.json / worklog / audits. No other scenario or sibling tasks directory read. No contamination.

## Per-task part verdicts
| Task | Runtime blind audit | Two-way scan | Dependency form | Files |
|---|---|---|---|---|
| 0 (refund of program credit balance; tree: overlap cancellation [user], renewal, residential placement -> refund) | PASS — blind 2,710.40 / 1.2033, 3,008.25 / 1,186.15 / 2,527.79 equal GT; every hop state-derived | PASS | PASS | runtime_context/lender_placed_flood_programs/0.md, policy_kb/lender_placed_flood_programs/0.md |
| 1 (loan-event cancellation on payoff; tree: commercial placement -> cancellation [user]) | PASS — blind 4,105.72 / 2,814.29 equal GT; hop state-derived | PASS | PASS | runtime_context/lender_placed_flood_programs/1.md, policy_kb/lender_placed_flood_programs/1.md |

Fall-back numbers (computation doc only, records as found) are definite and differ from the answers: task 0 refund 8,236.03, overlap 2,844.86, renewal 0.9500 / 2,375.00, placement 878.75; task 1 premium 4,532.00, credit 3,149.59.

## KB defects
None. kb=CLEAN.

Non-RED KB observations (no action implied):
- KO-1 The overlap schedule's effective-date / FLAT vs PRO_RATA booking rule (a rule sentence, not a factor ladder) is carried only in the Prior-Term Lookback factor doc ("Effective date and booking"). Entailment intact; findable through the doc title "... and Effective Date of Overlap Cancellations" and the hub scope "the credit and its effective date are figured by this overlap schedule".
- KO-2 The three overlap retention docs carry the source's order sentence ("taken off the overlap credit only once every amount added to the credit has been added"). It is the source's own non-commuting order rule and names no other doc.
- KO-3 Cross-product: owned-property factors (task 0) rest on Dwelling billing rows read via share tools; no figure depends on the unpublished Dwelling docs. Re-judge after dwelling renders for wording consistency only; no CONDITIONAL figure.

## Source-side findings (not KB-translation defects; verdicts above unchanged)
- SRC-1 (medium; no effect on task 0's numbers) Undeclared override: base `forceplaced_renewal` clause "the limit and premium are recomputed from the balances reported at renewal" is not named in any `overwrite` of `forceplaced_ext_renewal_premium`, which retires only the parallel `forceplaced_coverage_amount` clause ("The amount is recomputed from the balances reported at each renewal.") and sets the RMA renewal amount from the renewal notice. The KB faithfully renders both: Certificate Renewal Conditions states the base clause in force, Residential Renewal Schedule §2 states the renewal-notice rule. For an RMA renewal whose renewal-notice amount differs from the lowest of the balances reported at renewal, the visible corpus carries two in-force amounts. In task 0 both give 250,000.
- SRC-2 (low) Variant parameters stated as universal and contradicted by extended methods without a declared override: `premium_proration_basis: DAILY_PRO_RATA` ("Basis for any partial-term premium or credit") is rendered "Any partial-term premium or credit is figured on a daily pro rata basis" (Rate and Term Schedule); `loan_payoff_refund_method / servicing_transfer_refund_method / sfha_removal_refund_method: PRO_RATA` are rendered "The three loan-event credit methods are all pro rata on every tier" (Evidence and Credit Terms). `forceplaced_ext_loan_event_credit`'s earned-premium method (minimum one quarter earned under 90 days; monthly 90–180 days) and the overlap schedule's whole-term / lookback credits are not daily pro rata. The overwrite retires the base clause but not the parameter statements. Task 1 sits on the under-90-day tier; the scoped factor doc decides it, but the general statement remains in force on the visible surface.
- SRC-3 (low, advisory) The refund overwrite's replaced_by (carried verbatim in the hub scope, as required) says "and whatever is held back stays on the account as credit", telling the hub reader that holdbacks exist before any record leads to them. The computation doc itself is silent.
- Realism observations (no id): task 1's tree places a new certificate, backdated to the 2026-07-20 lapse, on a loan already paid off that morning, and then cancels it for the payoff. This is plausible as lender-placed cover for the lapse–payoff gap. The placement schedules price only "the loan named on the first notice with the latest notice date among the program's first notices", which is a scoping artifact. Neither is a defect of the KB.

## Difficulty closing checklist
- [x] One runtime_context and one policy_kb file per task, revision_1, blind_answer frozen before gt_comparison.
- [x] Every normative atom of forceplaced_ext_{credit_refund, overlap_credit, renewal_premium, placement_premium, commercial_placement_premium, loan_event_credit}, their base refs and variant tables entailed by docs/forceplaced; retired surfaces carried as retired with scope; no claim from outside the source.
- [x] Four prerequisite sentences (three on credit_refund, one on loan_event_credit) verbatim, state form, only in the blocked policy's hub; every hop resolvable from sentence + depended-on rule + records.
- [x] Every declared factor's ladder (4 + 5 + 6 + 6 + 5 + 4 = 30 factor docs) complete and exact in its own doc, findable from record words, referenced by nothing.
- [x] No other problem's tool name, route or aggregated chain anywhere.
- [x] check_docs / check_traceability lines on record (snapshot above; the auditor does not run them).

KB VERDICT round 1: task0=PASS task1=PASS
kb=CLEAN
src=SRC-1,SRC-2,SRC-3

## revision_2 (re-audit, 2026-10-17)

### Gate (checked first)
- `audits/policy_task/lender_placed_flood_programs/_difficulty.md` tail reads `VERDICT revision_12: task0=PASS task1=PASS` / `charter=CLEAN`.
- Newest docs/forceplaced file is 19:47:23Z, newer than forceplaced.extended.yaml at 19:41:42Z.
- Both conditions are met.

### Gates run by this auditor
- `check_docs.py env/env_0065_flood_insurance_carrier forceplaced`: `[PASS] mechanical gates: ... every prerequisite sentence carried verbatim on its blocked side, no tool-name pointers or route scaffolding` / `DOCS OK`. There are 4 prerequisite edges and 6 task tools.
- `check_traceability.py env/env_0065_flood_insurance_carrier/tasks/lender_placed_flood_programs`: `0.json 28 0 True`, `1.json 20 0 True`, `TRACEABILITY OK`.
- `mkruntime.py lender_placed_flood_programs`: 0.runtime.json sha256 6a803e59…6395 and 1.runtime.json sha256 ab37f8bf…f8aa0. Both are unchanged from round 1.

### Round-1 items
| Item | Round 1 | Round 2 |
|---|---|---|
| KB REDs | none (kb=CLEAN) | none; nothing regressed |
| SRC-1 (undeclared override of the base renewal clause) | open | **closed**. A new overwrite was added (base forceplaced_renewal). Certificate Renewal Conditions marks the clause retired with scope. Renewal Reference §2a carries the replaced_by. |
| SRC-2 (pro-rata parameters vs earned-premium / overlap methods) | open | **remnant, parameter-only**. The parameter values are unchanged. The visible surface now qualifies them with "Scoped exceptions" lines in Rate and Term Schedule and Evidence and Credit Terms, and the round-1 derivation "all pro rata" is gone. It moves no scored value. It is out of scope under the coordinator's BLUEPRINT-KNOWN rule. |
| SRC-3 (refund hub announcing holdbacks) | open | **closed**. "whatever is held back stays on the account as credit" is removed from the replaced_by and from the hub. |
| KO-1, KO-2 | observations | unchanged; non-RED |

### Lossless translation of the current charter
The whole re-rendered corpus (59 docs) was re-read against revision_12. It is still a lossless translation of the current charter:
- every rule, overwrite, baseline, factor ladder, prerequisite sentence and tool contract has an equivalent home;
- no additions;
- no scored value or world identifier appears in any doc of any product;
- prerequisite sentences appear only on their blocked side.

New content checked:
- "Terms of the schedule" definitions: rendered parameter_schema descriptions.
- "Scoped exceptions" bullets: same-source scope restatements.
- §2a of the Renewal Reference.

Cosmetic only: one bullet in the Rate and Term Schedule opens in lower case.

### Cross-product re-judge on the final corpus (all seven products published)
- Task 0, owned-property factors: Dwelling billing is 9 premium-payment rows and no refunds, giving 7,850.00 in the window, multiplier 0.96.
- Task 1, owned-building factor: NFIP commercial billing gives 11,140.00, multiplier 0.96.
- No Dwelling or NFIP-commercial document redefines these payments or how they are dated.
- No other product's document mentions lender-placed programs.
- No CONDITIONAL figure remains.

### Per-task part verdicts (revision_2)
| Task | Runtime | Two-way scan | Dependency form |
|---|---|---|---|
| 0 | PASS (figures unchanged and equal to GT) | PASS | PASS |
| 1 | PASS (figures unchanged and equal to GT) | PASS | PASS |

contamination_disclosure: the revision_2 runtime re-derivation was done by the round-1 auditor, who had already seen the round-1 source and GT. It confirms the visible support for each revision_1 hop and figure; it is not an independent blind audit.

KB VERDICT round 2: task0=PASS task1=PASS
kb=CLEAN
src=NONE
