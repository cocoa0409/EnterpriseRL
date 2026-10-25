# KB-doc policy audit — provider_network_services (product provider, "Network Participation Agreements")

## revision_1

### Entry conditions (cited from the coordinator brief; not re-run by the auditor per the binding coordinator notes)
- Policy-side verdict: `VERDICT revision_5: task0=PASS task1=PASS charter=CLEAN` (read after the blind answers were frozen).
- `check_docs.py env/env_0070_dental_and_vision_benefits_carrier provider` -> `DOCS OK`.
- `check_traceability.py …/tasks/provider_network_services` -> `0.json 20 0 True / 1.json 26 0 True / TRACEABILITY OK (non-unlock misses: 0)`.
- Instantiate gates: EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK; source sha256 prefixes 0721673c4508e267 (extended.yaml), 398bc89af826a284 (task_tools.py).
- Runtime view and DB access path provided (`.audit_views/runtime/…`, `db_query.py`); DB side queried in tool form only.
- Closing re-run of check_docs / check_traceability: not performed by this auditor (coordinator note: "Do not run check_traceability or any gate yourself"); no document changed during the audit, so the snapshot above is the final-form record.

### Per-task verdicts
| Task | Runtime blind audit | Two-way scan | Dependency form |
|---|---|---|---|
| 0 (exit settlement; 2 state-form edges) | PASS — blind 1.26 / 9906.60 / 14069.58 = GT | PASS | PASS |
| 1 (plan installment; 3-hop state-form chain) | PASS — blind 664.56 / 129.22 / 953.02 / 36.40 = GT | PASS | PASS |

Files: `audits/runtime_context/provider_network_services/{0,1}.md`, `audits/policy_kb/provider_network_services/{0,1}.md`.

### Closing checklist
- Audit files one-to-one with tasks 0 and 1; first revision, nothing overwritten.
- All normative atoms of the seven extended policies in scope and their base policies entailed by `docs/provider/`; 41 factor ladders checked tier by tier; every computation document yields a definite fall-back number (0, 9006.00, 10025.10; 801.20, 258.44, 742.28, 129.22), each different from the scored value.
- Five prerequisite sentences: each verbatim, state form, in its blocked hub only; every hop resolvable from the depended-on hub's own rule and the records.
- Cross-category factors (cap_small_practice, pl_small_practice) name Employer Group Contracts and the census record and are reachable from the group records; rendering of the BLUEPRINT-KNOWN ruling is faithful.
- No tool name, route or aggregated chain beyond the source's sentences; no example equals a scored value.

### Findings
- KB defects: none.
- KB observations (no verdict effect): O1 retired-clause phrasing "is superseded by the current basis: *<retired clause text>*" in `payment_runs_and_capitation_a7d718c3` §2, `overpayment_notices_and_recovery_b687b2dd` (two clauses), `practice_level_overpayment_offset_2fab77bd` (clauses 1–2) — the italic is the retired text yet sits where the current basis would be named; O2 adjustment-assembly bounds carried in computation documents (source assembly text, no pointer).
- Source-side: S1 — task JSONs 0 and 1, `evaluation_criteria` step `find_group_contracts` `necessity` says the small-practice factor "otherwise … falls back to the agreement's payments"; the source ladders (cap_small_practice, pl_small_practice) say otherwise "standard terms" (0). Stale prose; scored arguments unaffected.
- Coverage note: base-only provider policies with no extended claim are audited here only as base context of the claimed policies; cross-product contradictions are outside this skill's range.

KB-VERDICT revision_1: task0=PASS task1=PASS kb=CLEAN src=S1

## revision_2

- Gate: upstream tail line `VERDICT revision_6: task0=PASS task1=PASS charter=CLEAN` (as required). kb_snapshot 2026-10-19T09:43:24: DOCS OK; TRACEABILITY OK, non-unlock misses 0; all seven instantiate gates OK; src sha256 0721673c4508e267 / 398bc89af826a284.
- Round was text-only on the task JSONs. docs/provider/ (72 docs) and both sources byte-identical to revision_1; runtime views unchanged.
- S1 (stale "falls back to the agreement's payments" necessity prose in both tasks): closed — replaced with the standard-terms wording matching cap_small_practice / pl_small_practice.
- Re-verified per task: scored arguments, expected values, baselines and prerequisite edges unchanged; three-part verdicts of revision_1 stand (all PASS). No new defect, nothing regressed. Observations O1/O2 unchanged, no verdict effect.

KB-VERDICT revision_2: task0=PASS task1=PASS kb=CLEAN src=NONE

## revision_3

### Gate
- kb_snapshot 2026-10-20T03:37:38: DOCS OK; TRACEABILITY OK (0.json 20 0 True, 1.json 26 0 True; non-unlock misses 0); EXTENDED / TASK TOOL CONTRACT / REPLAY / SOLVABILITY / COMPUTE / GROUNDING / SCOPE OK; src sha256 0721673c4508e267 398bc89af826a284.
- Published: billing (52), dental (73), dhmo (18), group (15), ortho (46), provider (72, unchanged), savings (17). docs/vision/ not published.

### Exhaustive inventory of other-product rows (db_query.py, every share finder with no filter, both worlds)
- Task 0: group_contracts 1 (7bac97dc), group_eligibility_events 1 (c31c02ba). Task 1: group_contracts 1 (7e01ecf4), group_eligibility_events 1 (832ec064). Every dental, ortho, vision, billing, dhmo and savings finder returns no rows in either world. No vision rows, so nothing is vision-conditional.

### Re-derivation of each row from the published owning docs, as of its own dates
| Row | Field | Docs give | Seed | Result |
|---|---|---|---|---|
| 7bac97dc / 7e01ecf4 | segment | 2-19 contains 4 / 3 eligible (segment schedule) | Cascade Group Dental & Vision 2-19 | match |
| both | situs | WA on the situs list | WA | match |
| both | effective date | day 1 of a month; application 15 days ahead (census reported 2026-10-05 / 2026-10-20, persona "applied in October") | 2027-01-01 / 2026-12-01 | match |
| both | renewal date | first anniversary | 2028-01-01 / 2027-12-01 | match |
| both | rate-guarantee end | 12 months from effective | 2027-12-31 / 2027-11-30 | match |
| both | contribution | employer-paid, all premium; participation minimum 100 percent | employer_paid 100; census 4/4, 3/3 = 100 percent | match |
| both | waiting period | one of 0/30/60/90 | 30 | match |
| both | dental plan | Classic 1250 / Plus 1500 sold to employer groups, minimum 2 enrolled lives (dental market sheet) | 4 / 3 enrolled | match |
| both | vision | none offered -> no vision rates, no bundle discount (0 percent in 2-19 anyway) | none, 0.00 | match |
| both | status | applied until effective date with binder (underwriting guidelines) | applied, before effective date | match |
| both | census | census required to quote and issue; eligible on application = census | census present; 4 = 4, 3 = 3; effective date = contract effective date | match |
| both | dental tier rates | no published pricing basis: group rates are "quoted" and recorded on the application (underwriting guidelines §8; ortho sheet "Group rates are set by each group contract"); no dental tier ratio is published (the 1.9 / 2.0 ratios are vision-only) | 41.60/83.20/79.05/124.80; 48.25/96.50/91.70/144.75 | not re-derivable, not contradicted (observation only) |

### Members the owning docs would produce differently
- **R3-S1 (src, seed-implied record missing, both worlds, non-moving).** Billing docs ("Premium Billing Accounts — Account Status, Binder, Closure…"): "An account is opened in pending binder for a new individual application or group contract, with an arrangement whose entry condition admits the customer type and market." Each world holds an applied group contract (7bac97dc, 7e01ecf4) but `find_billing_accounts` returns no rows; the docs would produce a pending-binder Cascade Group List Bill account for each contract (entry condition: customer type "employer group", at least 2 enrolled lives). That customer type does not admit the provider_practice holder; the practice-as-group-holder premise sits under the standing BLUEPRINT-KNOWN coordinator ruling. No scored value moves: cap_small_practice / pl_small_practice read only the contract status and the latest census eligible count (tier "fewer than 5" holds either way); 9906.60, 14069.58, 36.40 and the chains above them are unchanged.
- **R3-S2 (src, own-product rows lacking their charter-implied source records, non-moving).** Provider docs ("Overpayment Notices, Lookback and Recovery Entries"): an overpayment arises "when a member claim paid to the practice is reprocessed to a lower payment, or when an orthodontic payment is reversed", and its lookback clock is "the adjudicated date of the source dental line or vision service, or the payment date of the source orthodontic payment". All nine overpayment notices in the two worlds carry no dental_claim_line_id / vision_claim_id / ortho_payment_id, and no dental, dhmo or ortho rows exist: task 0's five notices (source_product dhmo) arise from duplicate capitation remittances (original_payment_date = dates of the extra capitation entries 2026-01-22 … 2026-07-08), task 1's four from re-issued claim payment runs ("R" remittances). Under the published docs such notices have no source claim to anchor the lookback. The extended policies themselves presuppose overpayments on a capitation agreement, and the policy-side verdict passed this design, so this is recorded for completeness. No scored value moves: no scored computation reads the source claim or the lookback.

### Earlier conditional items
- None were marked conditional in revisions 1–2.

### Observations carried
- O1, O2 unchanged (no verdict effect). Group dental rates not re-derivable from published docs (table above), not a defect.

KB-VERDICT revision_3: task0=PASS task1=PASS kb=CLEAN src=R3-S1,R3-S2
