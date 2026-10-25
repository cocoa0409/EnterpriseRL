# KB audit closing — insurance_claim_services / claims (revision_1, 2026-10-25)

## Entry conditions (cited, not re-run)
- Policy-side verdict: audits/policy_task/insurance_claim_services/_difficulty.md last line "VERDICT revision_8: task0=PASS task1=PASS charter=CLEAN".
- Gate snapshot .audit_views/runtime/insurance_claim_services/kb_snapshot_r1.txt (2026-10-25T04:31:27): "check_docs: DOCS OK", "check_traceability: TRACEABILITY OK", "traceability miss lines (total / mentioning unlock): 1 / 0", EXTENDED / TASK TOOL CONTRACT / REPLAY / SOLVABILITY / COMPUTE / GROUNDING / SCOPE OK; source hashes equal to the files audited (claims.extended.yaml c798ee32..., task_tools.py fa915bb8...); docs files 66. check_traceability not re-run (coordinator instruction); check_docs not re-run (corpus unchanged since the snapshot: no doc edited by this audit).
- Runtime view hashes verified: 0.runtime.json ab6e4952...529f, 1.runtime.json c565a5c4...977f. DB side blind (tool-shaped db_query only). Task-tool schemas taken from hub invocation blocks (view listed share tools only).

## Part-verdicts
| Task | Runtime blind audit | Two-way scan | Dependency form |
|---|---|---|---|
| 0 (dwelling depreciation release) | PASS (conditional CF-1) | PASS (conditional CF-1) | KB-EXPLICIT RED (KB-3) |
| 1 (final mold supplement) | PASS | KB-BIJECTION RED (KB-1, KB-2) | PASS |

## KB findings
- KB-1 — docs/claims/final_air_lines_189b4d2e.json, rule sentence: "on any other tier no such air lines are claimed" (the "such air lines" include the dehumidifier day charges). Source fall-through is the standard air treatment, the dehumidifier days billed. Untriggered branch (Spot tier); two readings.
- KB-2 — docs/claims/protocol_air_treatment_563b02f8.json, rule sentence: "on any other tier no such air treatment is priced". Source fall-through is the standard air treatment, one dehumidifier for the cap. Untriggered branch; two readings (0.00 vs rate x cap).
- KB-3 — docs/claims/regulated_ppe_line_00ddd076.json, hypothetical: "a Gray Water job with PPE billed at 143.75 and an asbestos sampling line takes 143.75" reproduces task 0's water job (Gray Water - Standard Loss, PPE 86.25 + 57.50 = 143.75, asbestos sampling billed) and its factor outcome (GT rs_ppe = 143.75).

## Conditional (not RED; re-check when the owning corpus publishes)
- CF-1 — removed_scope_inclusion reads the Standard Rebuild Agreement change order markup (20 % in blueprint rebuild.yaml) and treats an owner_upgrade change order charge as an "additive change order charge"; both are Reconstruction vocabulary/figures and no rebuild doc is published yet. Task 0's write-off (254.07) and release (1297.18) depend on it.

## Source-side items found at this layer (not KB defects)
- SRC-1 — task 0 seed, water job cb1a3090: three gold-read rows are not reproducible from the published water extended pricing (no customer-level scope stated there): HEPA line 960 sq ft / 297.60 (published final-HEPA pricing: 4020 sq ft / 1246.20), antimicrobial line 860 sq ft at 0.36 / 309.60 (published tear-out antimicrobial pricing: 1660 sq ft at 0.47 / 780.20), debris haul 1 load / 214.00 (published tear-out debris pricing: 4 loads at 267.50 / 1070.00). They feed the regulated-scope (rs_cleanup, rs_disposal), reassessment (sc_reg, sc_anti) and, through the final invoice, the release. Either the seed or the water KB's scope is off; which one is outside this audit.
- SRC-2 — task 1 seed, mold job 78c1f5e2: debris_disposal "2 load x 238.00 = 476.00" vs the published mold haul-off line (one line, qty 1 each: 1 load x 238.00 + one-trip 75.00 = 313.00); no work-plan visit supervisor-labor line (published: every protocol-tier job, 2 h x 106.90 = 213.80, dated the opened date); asbestos sampling line dated 10-08 vs the published "dated the job's opened date". Gold reads the removal family (631.52) and the labor family (supervisor labor 320.70).
- SRC-3 — tasks/0.json evaluation_criteria, find_rebuild_contracts objective: "final invoice 34135.20"; record and initial_state: 33499.20 (unscored prose).
- SRC-4 — factor-ladder text in the source names another factor / policy, which the KB must carry verbatim: cleaning_verification_labor ("whose labor the certified-renovator labor already takes"), final_regulated_lines ("as the protocol supplement prices it"). Bindings read records, not the other factor's output (XF A1 holds); wording only.

## Closing checklist
- Audit files one-to-one with tasks: runtime_context/insurance_claim_services/{0,1}.md, policy_kb/insurance_claim_services/{0,1}.md (revision_1; no earlier revision existed).
- Every prerequisite sentence (5 edges) verbatim, action form as declared, only on its blocked side; each task tool named only in its own hub.
- Every factor ladder carried in its own doc; two fall-through tiers mis-rendered (KB-1, KB-2).
- Difficulty does not close: KB-1, KB-2, KB-3 open; CF-1 pending the rebuild corpus.

KBVERDICT revision_1: task0=RED task1=RED kb=KB-1,KB-2,KB-3 src=SRC-1,SRC-2,SRC-3,SRC-4

## revision_2 (2026-10-25)
Entry: policy_task last line "VERDICT revision_9: task0=PASS task1=PASS charter=CLEAN". Runtime views regenerated by runtime_views.sh (hashes unchanged: ab6e4952...529f, c565a5c4...977f). Snapshot .audit_views/runtime/insurance_claim_services/kb_snapshot_r2.txt (2026-10-25T05:15:41): "check_docs: DOCS OK", "check_traceability: TRACEABILITY OK", miss lines 1 / 0, EXTENDED / TASK TOOL CONTRACT / REPLAY / SOLVABILITY / COMPUTE / GROUNDING / SCOPE OK; claims.extended.yaml d63115724bc1eaed372c0dbfe36066c656acc023e27fb6037b75d7262d165ed9, task_tools.py fa915bb8... (unchanged); 66 docs.

| Task | Runtime blind audit | Two-way scan | Dependency form |
|---|---|---|---|
| 0 | PASS (blind r2 = GT: 4131.55 / 1865.45 / 254.07 / 1085.18) | PASS | PASS |
| 1 | PASS (blind r2 = GT: 2457.15 / 1944.89) | PASS | PASS |

Round-1 items:
- KB-1 closed (final_air_lines fall-through now the dehumidifier day charges billed).
- KB-2 closed (protocol_air_treatment fall-through now one dehumidifier for the cap).
- KB-3 closed (regulated_ppe_line example now Black Water - Large Loss, 231.00).
- SRC-1 closed (water HEPA 4020 sq ft / 1246.20, antimicrobial 1660 sq ft at 0.47 / 780.20, debris 4 loads at 267.50 / 1070.00 = published water pricing).
- SRC-2 closed (mold asbestos sampling 590.00 = 425.00 + 165.00 insulation set, dated the opened date; work-plan visit 213.80; haul-off 313.00 qty 1 each = published mold pricing).
- SRC-3 closed (evaluation_criteria prose now "final invoice 33499.20").
- SRC-4 closed (cleaning_verification_labor no longer names the sibling factor; final_regulated_lines no longer names the protocol supplement).
New: none. Regressions: none (31 changed docs diffed; normative changes all track the source diff). Observation only: duplicated Spot example sentence in final_air_lines and protocol_air_treatment.
Conditional, unchanged: CF-1 (Standard Rebuild Agreement change order markup / "additive change order" still not in a published doc; rebuild corpus not on disk).

KBVERDICT revision_2: task0=PASS task1=PASS kb=CLEAN src=NONE

## revision_3 (2026-10-25) — cross-product re-judge, all products published
Entry: policy_task "VERDICT revision_9: task0=PASS task1=PASS charter=CLEAN". Snapshot .audit_views/runtime/insurance_claim_services/kb_snapshot_r3.txt (2026-10-25T05:49:18): "check_docs: DOCS OK", "check_traceability: TRACEABILITY OK", 1 / 0 miss lines, all other gates OK; claims.extended.yaml d63115724bc1eaed..., task_tools.py fa915bb8... (both unchanged since revision 2); docs/claims byte-identical to revision 2; tool-shaped query returns for both tasks identical to revision 2. docs/ now holds account, claims, contents, fire, mold, rebuild, water.

### (1) Conditional items
- CF-1 resolved. rebuild/change_order_terms_and_allowances: Standard Rebuild Agreement "Markup 20%"; rebuild/additive_change_order_signature: "Every change order type except deductive is additive." Task 0's write-off (254.07) and release (1085.18) are now derivable from the published corpus.

### (2) Other-product rows the gold reads, re-priced against the owning product's published docs (no effective dates in the published docs, so current rules at each posting date)
Task 0 — Reconstruction contract 7ee96f1e (Standard Rebuild Agreement, single-family, built 1974, TX), read by contract_cost_measure (draw payments), removed_scope_inclusion and code_holdback_cut_rule (change order charge and credit), contract_scope_pricing_basis (signed date), the release scope (status):
- Contract sum 31850.00 within the Standard gate (single-family, 10000.00-49999.99): consistent.
- Change order charge 151.20 (CO 2, owner_upgrade, flooring_upgrade 180 sq ft at 3.95, signed 08-07 with no other proposal awaiting): additive pricing = (3.95 - flooring allowance 3.25) x 180 = 126.00, no cleaning / fixed item (not a drywall, insulation, paint or baseboard line), tier markup 20 % -> 151.20; at or above the 150.00 minimum. Consistent.
- **SRC-5** — change order credit 255.60 (CO 1, deductive, carpet_install 180 sq ft, credit posted 2026-08-05, the only proposal awaiting signature then; CO 2 was created 08-06). Published deductive credit rules (deductive_change_order_signature scope; deductive_change_order_credit_calculation; change_processing_deduction_on_removals): change-order part 0 (no signed non-deductive carpet-install change order), contract part 180 x 1.42 (Standard carpet and pad install rate) = 255.60, then "any fixed deduction the removal carries is then subtracted": construction started 2026-06-10, on or before the signing date -> field-remeasure deduction 95.00 -> credit **160.60**, not 255.60. Gold reads it: removed_scope_inclusion (255.60 - 126.00 = 129.60 -> 34.60), and the closed contract's paid total (draw payments 33243.60 -> 33338.60; the drywall draw would be 30 % of 31840.60 = 9552.18 and the final draw 9548.42). Moves gold: write-off 254.07 -> 166.17, release 1085.18 -> 1268.08.
- **SRC-6** — permit expediting: the contract carries municipal permit fee lines for two permit types (building 412.00, electrical 96.00, both billed at cost to the contract) but one permit expediting line (building, 145.00). Published rule (permit_and_professional_fee_billing): "the company's permit expediting fee is billed once per permit type pulled" / "for each permit type the company pulls | once per permit type"; Standard expediting 145.00 (permit_and_professional_fee_schedule). A second 145.00 line (electrical) is missing, unless the electrical permit was pulled by someone other than the company, which no record shows (its fee is billed to the contract at cost). Gold reads it through the closed contract's paid total (pass-through payment 1498.00 -> 1643.00): release +145.00 (1085.18 -> 1230.18 alone; with SRC-5, 1413.08).
- Plan drawing 450.00 (permit required), lead-safe setup 395.00 (built 1974, Standard fee), permit fees at cost: consistent.
- Draws: signing 10 % of 31850.00 = 3185.00 (cap 5000.00); rough-in 30 % = 9555.00; drywall 30 % of the then current sum 31745.60 = 9523.68; final draw = remainder 31745.60 - 22263.68 = 9481.92 with nothing added or held (claim payments insured_only -> customer-funded final draw: no pass-through, deductible, depreciation, owner-item, code-item or Texas final retainage). Consistent given the seeded credit (they shift with SRC-5). Draw payments on or before each due date (base payment rule, posted in full); pass-through 1498.00 paid 10-08 within 15 final-payment days of the 09-25 invoice; closed at balance 0.00. Consistent.
Task 0 — Water job cb1a3090 (gold reads the HEPA, containment, antimicrobial, extraction, carpet, PPE, labor, debris, lead-safe, asbestos, air-mover lines, credits and the final invoice): rates and the extended-priced lines verified in revision 2; equipment days 05-05..05-09 within the Gray Standard 5-day cap; 8 air movers / 2 LGR per day (no billing rule ties billed units to the placement estimate); 4 monitoring visits (set day not billed) at 84.00; service call 219.00 business hours, arrival 74 <= 120; final invoice 10435.85 = sum of lines; payment 10106.45 = invoice - credits. Consistent. Observation: the double-keyed moisture-mapping and thermal-imaging lines contradict "billed at most once per job" but are the billing errors the duplicate_line credits correct (the claims charter's own credit reason) - accepted as the credited state.
Task 1 — Mold job 78c1f5e2 (verified in revision 2; re-checked): asbestos sampling 590.00 (425.00 + 165.00 insulation set; 17-day lead time; no PA / referral; no linked water job), work-plan visit 213.80, haul-off 313.00 (1 load x 238.00 + one trip 75.00), containment 538.00, 4 + 4 equipment days, soda 312.00, HEPA 55.68, antimicrobial 42.24, PPE 211.20, labor at 88.40 / 132.60 / 160.35. Consistent. Closed job 13b3e213 and the 1138.80 payment: read by no gold step (RULE-2 residue); spot-checked consistent.

### (3) E5 — owed-at-once writes a solver could make mid-call
- Task 0: rebuild contract closed and water job closed (status gates bar every rebuild / water write); no mold, contents, fire or account holding; claims-side writes are the tree itself. Nothing can move a scored read. Clean.
- Task 1: mold job awaiting clearance: haul-off, pre-removal sampling and work-plan lines already booked (the published booking rules owe no second line); no minimum-charge shortfall (charges above 1450.00); clearance fee arises only with a clearance result; mold payments (deposit / insured share) do not enter the final figure, which reads charge lines. Clean.

### Own-category seeded history rows the gold reads, against this difficulty's published docs
- Task 0: supplement 1 (code_upgrade, 3350.00, 06-15, naming the contract) is outside every extended scope (none prices code_upgrade) -> base rule: within the 24500.00 ordinance-or-law remainder, above the 250.00 minimum, inside the window; approval 3200.00 / 960.00 withheld is a carrier act; payments (advance 2000.00, ACV 28205.00, supplement 2500.00, insured_only) are carrier acts recorded as advised; carrier receivable 6720.00 = approvals - payments; no deductible lines (PA arrangement does not collect). Consistent.
- Task 1: supplement 1 (mold_remediation 4780.00, 07-22, naming the closed job) predates the second mold job (opened 09-21), so neither mold extended scope applied -> base rule: under the 7000.00 mold room, recorded on delivery (HDP); approval 4542.85 (less than requested) and payments are carrier acts; receivable 3710.00 consistent. Consistent.

### Verdicts
| Task | Runtime | Two-way scan | Dependency form |
|---|---|---|---|
| 0 | PASS | PASS | PASS |
| 1 | PASS | PASS | PASS |
KB: no new defect, nothing regressed (claims corpus unchanged since revision 2). Source-side: SRC-5, SRC-6 (task 0 seed rows; both move task 0 gold). Observation only: claims removed_scope_inclusion nets additive change orders at the tier markup while published rebuild pricing marks up insurance-scope / code-required change orders on claim contracts at the arrangement's overhead plus profit (equal here, untriggered).

KBVERDICT revision_3: task0=PASS task1=PASS kb=CLEAN src=SRC-5,SRC-6

## revision_4 (2026-10-25) — seed-only confirm
Entry: policy_task "VERDICT revision_10: task0=PASS task1=PASS charter=CLEAN". runtime_views.sh re-run (hashes unchanged). Snapshot kb_snapshot_r4.txt (2026-10-25T06:33:09): "check_docs: DOCS OK", "check_traceability: TRACEABILITY OK", 1 / 0 miss lines, all other gates OK; claims.extended.yaml d6311572..., task_tools.py fa915bb8... unchanged; docs/claims byte-identical to revision 3.
- SRC-5 closed: the deductive change order credit is now 160.60 (= 180 x 1.42 - 95.00 field-remeasure deduction). The drywall draw (30 % of 31840.60 = 9552.18) and the final draw (31840.60 - 22292.18 = 9548.42) follow the published draw rules.
- SRC-6 closed: an electrical permit expediting line of 145.00 (06-02) is now booked. Final invoice 33644.20 = sum of the charge lines; pass-through payment 1643.00 = 412 + 145 + 96 + 145 + 450 + 395; paid total 33483.60 = invoice - credit; closed at 0.00.
- Figures moved: write-off 254.07 -> 166.17 and release 1085.18 -> 1413.08. Both re-derived from the current docs and records, and both equal GT (fall-backs 377.81 / 3768.28 equal GT baselines). Regulated-scope, reassessment and task 1 unchanged.
- No new defect: the changed rows are consistent with the published rebuild docs; E5 unchanged (contract closed); no new figure appears in any claims worked example; evaluation prose now reads "final invoice 33644.20". Nothing regressed.

KBVERDICT revision_4: task0=PASS task1=PASS kb=CLEAN src=NONE
