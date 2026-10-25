# KB audit report — private_homeflood_rating_billing (product homeflood), round 1

Auditor: independent KB-audit subagent. Blind answers frozen before the reveal (runtime_context/private_homeflood_rating_billing/{0,1}.md, hashes in {0,1}.freeze.sha256, re-verified intact after the gt_comparison was appended). No contamination: the brief carried no scored value, and no task JSON, worklog, extended YAML, `audits/policy_task/`, `audits/render_source/` or `audits/XF_recipe.md` was opened before the freeze. DB side blind (db_query.py only).

## Entry conditions (cited from snapshot_kb1.txt, not re-run)
- Policy side: VERDICT revision_4 task0=PASS task1=PASS / charter=CLEAN.
- `[check_docs homeflood] … docs=68 … DOCS OK`; `[check_traceability post-publication] TRACEABILITY OK`; validate_scenario errors belong to other difficulties' unpublished docs.
- Runtime views 0/1.runtime.json sha256 match the snapshot.

## Per-task part verdicts
| Task | Runtime blind audit | Two-way scan | Dependency form | Blind vs GT |
|---|---|---|---|---|
| 0 (installment after renewal, open EC review) | KB-RUNTIME RED (K1) | KB-BIJECTION RED (K1) | KB-EXPLICIT RED (K1–K4) | all 4 calls, every argument identical; tree = closure (5 state hops) |
| 1 (closing payment after sale cancellation) | PASS | PASS | KB-EXPLICIT RED (K5–K7) | both calls identical; tree = closure (1 state hop) |

## KB findings
- **K1** (task 0; RUNTIME + BIJECTION + EXPLICIT) `rerated_term_premium_calculation_4fc539cc` step 3 "The product is reduced once by the credit percent applied to the term. Credits are added to one another, never multiplied, and their sum is capped …" — the source baseline has no credit step. The KB wording uses the base record quantity "credit percent applied to the term" (credits_applied_pct, 5 on this policy), not the extended rule's "every credit this rule states" (compute: vent + loss-history + layer only). Effects: (a) the baseline fall-back moves from 2138.13 to 2033.47; (b) a stacked reading (recorded 5 plus 5 + 3 + 5, capped 15 → 1343.07, credits 15) becomes available, and every downstream scored value (re-rate credit, renewal, installment) then shifts. The blind audit excluded it only by combining three retirement notices with the inference that the recorded 5 is the package credit; (c) the computation document announces that credits exist and combine.
- **K2** (task 0; EXPLICIT) `rerated_term_premium_calculation_4fc539cc` "Records read" names survey date, receipt date, base flood elevation, elevation difference and flood openings. Those are factor quantities only; the baseline elevation factor uses none of them.
- **K3** (task 0; EXPLICIT) `rerate_credit_pro_rata_amount_19e084cd` "Records read" names survey date, flood openings and the counting of certificate entries. Those are factor quantities only.
- **K4** (task 0; EXPLICIT) `installment_amount_calculation_c113831a` "Installments of the term" defines the 3/6/9-month due dates and "installments still to come". Those are factor quantities only.
- **K5** (task 1; EXPLICIT) `cancellation_credit_short_rate_c52dd777` says "the tier's annual loss-of-use charge forms part of the term premium item". That split is a factor quantity only.
- **K6** (task 1; EXPLICIT) `policy_fee_return_on_cancellation_06ee3a0c` restates the closing payment's overdue-installment-fee give-back ladder, which belongs to another problem's factor, inside a sale-cancellation factor document.
- **K7** (task 1; EXPLICIT, low) `loss_of_use_charge_return_a906136c` names the earning-basis factor and its pro-rata tier ("same earning basis", "cancelled on the pro rata basis").

## Source-side findings (not KB-translation defects)
- **S1** (undeclared override, medium) The homeflood_premium_rating clause "The total credit percent from the credit rule then reduces the result." is not in certificate_rerate.overwrite, although that rule's credit assembly and compute replace it for the re-rated premium. The KB faithfully shows the clause in force for every rating, so the visible corpus carries two credit steps for the re-rating. This is the co-root of K1.
- **S2** (realism, low) Rule text says "(the Excess Flood charter allows only one live policy on an address)" in certificate_rerate and installment_payment. "Charter" is authoring vocabulary and reaches `excess_layer_credit_dffe273e` and `excess_paid_up_installment_credit_68e377c4` verbatim.
- **S3** (rule vs record, low) EC acceptance needs Form 086-0-33, a seal and no alteration. No record field carries any of these, and the compute tests survey age only.
- **S4** (rule vs compute, low, untriggered) In autopay_fee and autopay_history, "every one … by ACH but fewer than 4" is vacuously true with zero payments, but the compute requires at least one ACH payment. The KB follows the compute ("one to three of them").
- **S5** (factor coupling, low) The sale_cancellation rule (C5 replaced_by) embeds the closing-payment overdue-fee ladder. That is what K6 renders.

## Cross-product
No hop or factor of either task rests on another product's published KB. The dwelling/excess factor rules are carried in homeflood docs with the official product names and the record fields they read. Whether the unpublished NFIP Dwelling Form / Excess Flood corpora restate anything differently cannot be checked yet: CONDITIONAL, to be re-judged by the coordinator when they publish.

## Closing checklist
- Audit files one-to-one with tasks: runtime_context/…/{0,1}.md (+ freeze hashes) and policy_kb/…/{0,1}.md — present.
- Every prerequisite sentence: verbatim, state form, blocked hub only (mechanically checked). Every task tool name appears only in its own hub. No seed figure or party name appears in any doc.
- Every declared factor ladder is complete and findable from record words (15 + 10 factors swept, all tiers).
- Not closed: K1–K7 open. check_docs and check_traceability were not re-run on a final form, because the corpus is not final.

KB VERDICT round 1: task0=KB-RUNTIME/KB-BIJECTION/KB-EXPLICIT RED task1=KB-EXPLICIT RED
kb=K1,K2,K3,K4,K5,K6,K7
src=S1,S2,S3,S4,S5

## revision_2 (round 2 re-audit, 2026-10-17)

**Gate (checked first).** `_difficulty.md` tail = `VERDICT revision_6: task0=PASS task1=PASS` / `charter=CLEAN`. The newest doc (2026-10-17 13:20:05) is newer than `homeflood.extended.yaml` (13:13:44). Both conditions are met. An earlier round-2 request was answered BLOCKED (revision_5 task0 RED, docs older than the charter).

**Gate commands, run by the auditor:**
- `check_docs.py … homeflood` → `[PASS] mechanical gates … DOCS OK`.
- `check_traceability.py …/private_homeflood_rating_billing` → 0.json 23/0 True, 1.json 15/0 True, `TRACEABILITY OK`.
- `mkruntime.py private_homeflood_rating_billing` → 0.runtime.json 19320e79…0c32, 1.runtime.json d663ff42…5c55 (unchanged since round 1).

**Method.**
- Both revision_2 blind answers were frozen (hashes appended to {0,1}.freeze.sha256) before the current source and GT were read.
- Contamination disclosed: the auditor knew the round-1 source and GT, so revision_2 is not blind. It re-derives every value from the current docs and fresh db_query.py returns; the seeds are unchanged.
- Then a full two-way re-scan against the current charter (not only the K-items) and a dependency-form re-scan of the whole corpus were done.

**Result.**
- Blind = GT on every scored argument for both tasks: 1373.62 / 13 / true, 113.35, 1256.86 / 35.00, 111.43 / 2 / ACH; 289.23, 290.84 / ACH.
- Problem trees are unchanged and all hops are state-derived.

| id | round-1 class | round-2 status |
|---|---|---|
| K1 | RUNTIME + BIJECTION + EXPLICIT | closed: credit step removed from the calculation document; the source baseline's "recorded credit percent is not carried into the re-rating" is carried; credit assembly sits in the credit factor docs |
| K2 | EXPLICIT | closed |
| K3 | EXPLICIT | closed |
| K4 | EXPLICIT | closed (moved into the two factors that read it) |
| K5 | EXPLICIT | closed |
| K6 | EXPLICIT | closed |
| K7 | EXPLICIT | closed |
| S1 | src | closed: clause 4 is now overwritten in source and marked retired for the re-rated premium in `annual_premium_rating_rule_f0aede7e` |
| S2 | src | closed: "charter" → "program" in source and KB |
| S3 | src | closed: the acceptance rule now says Tidemark records an entry only for a valid certificate; the review tests survey age |
| S4 | src | closed: "one to three" / "no payment" tiers in source = compute = KB |
| S5 | src | closed: the sale-cancellation rule no longer embeds the closing-payment ladder |

**Changes checked for regressions:**
- New factor vent_survey_addition → `mitigation_survey_addition_9b6021f6`.
- Reworked credit_start_anchor and fall_measure_source.
- New ceiling on the re-rate credit.
- New tie-break sentences.

All of these are exact translations of the current source and compute. No new defect was found and nothing regressed.

**Closing checklist (round 2).**
- Audit files are one-to-one with tasks and revision_1 text is untouched.
- Every prerequisite sentence is verbatim on its blocked side only.
- Every factor ladder is complete and findable from the records.
- No tool name, route or chain appears beyond the prerequisite sentences.
- check_docs and check_traceability were re-run on the final form and are green.
- Cross-product: no verdict rests on unpublished NFIP Dwelling Form or Excess Flood docs. Their future restatements remain CONDITIONAL for the coordinator's cross-product re-judge.

KB VERDICT round 2: task0=PASS task1=PASS
kb=CLEAN
src=NONE

## revision_3 (round 3 cross-product re-judge, 2026-10-17)

**(3) homeflood unchanged since round 2:**
- `_difficulty.md` tail is `VERDICT revision_6: task0=PASS task1=PASS` / `charter=CLEAN`.
- docs/homeflood: 68 docs, combined sha256 prefix f02ab8bb9a320f19, identical to round 2.
- The extended YAML (13:13:44), tasks (13:14:02) and task_tools.py (2026-10-15) are unchanged.
- Run by the auditor: check_docs homeflood → `DOCS OK`; check_traceability → 0.json 23/0 True, 1.json 15/0 True, `TRACEABILITY OK`.
- The runtime views and db_query.py returns are unchanged, so the revision_2 blind answers and GT comparisons stand without a new freeze.

**(1) Cross-product hops**, re-judged against the final published docs/dwelling (74), docs/excess (51) and docs/nfipcom (65):
- Every homeflood factor that reads NFIP Dwelling or Excess records uses the same link, status, designation, date and limit vocabulary as the owning product's rules: the replaced-NFIP-number link is defined identically from the dwelling side, "one live Excess policy per address" matches, and the Excess limit and attachment rules are satisfied by the seeded layer.
- No owning-product doc contradicts a homeflood reading, and no scored figure moves.
- No hop reads NFIP-commercial records.
- The round-1 CONDITIONAL is resolved: PASS.

**(2) Producibility of seeded cross-category rows (db_query.py only):**
- **Task 0, NFIP 3104558217:** producible, including the 2022-09-01 replacement cancellation on the published anchor and lead-window rules.
- **Task 1, NFIP 3127704519:** producible (loan-transaction basis, 0-day wait, 12-month term).
- **S6** (task 0, low, unscored): Excess XF-3409126 `term_premium` 1146.00 cannot come from the published Excess rules. For Excess Flood 500K at 300000 in zone AE without a certificate, every producible term premium lies in 650.00–691.25 (minimum 650; layer 465 × at most +25 % + loss-of-use 110). Its effective date 2024-03-15, 18 days after the 2024-02-26 application of a standalone policy, also violates the 30-day standard wait. The scored readings (status, address, effective on or before 2025-09-01, limit, balance) are unaffected.
- **S7** (task 0, low, unscored): NFIP condo 3118840265 has original effective 2018-03-10, 18 days after application 2018-02-20 on basis STANDARD (the rule gives 30 days → 2018-03-22). It also has `rated_icc_premium` 50.0 on Residential Condominium Unit, a tier on which ICC "attaches: No". The task reads only its status and primary-residence flag.
- **Observation (no id):** cross-category rows carry no backing ledger or request history (Excess billing, the dwelling cancellation request and credits, dwelling billing). The field-level states the tasks read are reachable under the owning rules.

**KB side:** no new defect and nothing regressed. Both tasks PASS on all three parts.

| Task | runtime | bijection | dependency form | cross-product |
|---|---|---|---|---|
| 0 | PASS | PASS | PASS | PASS (S6, S7 seed realism, unscored) |
| 1 | PASS | PASS | PASS | PASS |

KB VERDICT round 3: task0=PASS task1=PASS
kb=CLEAN
src=S6,S7

## revision_4 (round 4 seed-only confirm, 2026-10-17)

- **Gate:** `_difficulty.md` tail is `VERDICT revision_7: task0=PASS task1=PASS` / `charter=CLEAN`. Passed.
- **Freeze:** `homeflood.extended.yaml` and `task_tools.py` are byte-identical to `/tmp/erl0065_coord/seedonly_freeze.sha256` (sha256 -c OK). docs/homeflood is unchanged (68 docs, prefix f02ab8bb9a320f19), so no re-render is needed.
- **Commands, run by the auditor:**
  - mkruntime.py: 0.runtime.json 19320e79…0c32 and 1.runtime.json d663ff42…5c55, both unchanged.
  - check_docs homeflood: `DOCS OK`.
  - check_traceability: 0.json 23/0 True, 1.json 15/0 True, `TRACEABILITY OK`.
- **S6 closed (task 0):** Excess XF-3409126 now shows term_premium 650.00 (within the producible 650.00–691.25 band) and an effective date of 2024-03-27, the 30-day standalone wait after its 2024-02-26 application. The term now runs 2026-03-27 → 2027-03-27.
- **S7 closed (task 0):** NFIP condo 3118840265 now has application 2018-02-08, 30 days before its 2018-03-10 effective date on the standard basis, and an ICC premium of 0.00 on a tier without ICC.
- **Runtime path unchanged:**
  - Task 0: every homeflood and NFIP-claim row on the scored path is identical to round 2, and the changed cross-category fields leave every factor tier as before.
  - Task 1: the DB returns are byte-identical (md5 af61d326…).
  - Current GT equals the frozen round-2 blind answers: 1373.62 / 13 / true, 113.35, 1256.86 / 35.00, 111.43 / 2 / ACH; 289.23, 290.84 / ACH.
- **Result:** no new defect, nothing regressed.

KB VERDICT round 4: task0=PASS task1=PASS
kb=CLEAN
src=NONE
