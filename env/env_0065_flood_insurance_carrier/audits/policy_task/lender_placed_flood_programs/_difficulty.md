# Policy-task audit — lender_placed_flood_programs / charter-global

## charter_global_frozen

- Freeze: written 2026-10-15T22:30Z (round 1), before any task GT was revealed. Auditor: independent policy-task auditor (not the instantiator).
- Hashes (sha256 prefix, rechecked against the coordinator snapshot): `forceplaced.extended.yaml` 4243fea107506081; `task_tools.py` c03b6ecef5ee83ce; masked views `0.json` d80440aaf0571963, `1.json` cec2151a3675a137.
- Entry conditions (Step 0): gate snapshot `.audit_views/policy/lender_placed_flood_programs/snapshot_r1.txt` supplied with the brief; check_extended / check_task_tools / replay --check / check_solvability / check_compute / check_grounding / check_cross_fire green; traceability misses are unlock tool-name provenance only (pre-render); validate_scenario INVALID only for `documents: 0` (pre-render). Masked views supplied with hashes. Entry conditions met.
- Read: blueprint/ (blueprint.yaml, db_schema.json, share_tools.py, products/forceplaced.yaml, and products/dwelling.yaml + nfipcom.yaml for the cross-category charters), the extended charter, task_tools.py, the two masked views, erlbench/ and the instantiate skill's check_compute.py (DSL semantics). Masked and unread: tasks/*.json, the difficulty worklog.md, every GT field. This section contains nothing derived from a revealed GT.
- DSL facts used (skills/erl-task-instantiate/scripts/check_compute.py): every SUM/COUNT/LATEST is scoped to the target program; default `date_field` is `event_date`; `within_months=N` keeps rows with `0 <= MONTHS(d, today) < N`; `MONTHS` counts whole months (day-of-month must be reached); `DAYS(a,b)=b-a`; `LATEST` keeps the first row on a date tie; `RND` is Python `round`.

### policy_conflict_scan

Six extended policies, one target tool each:

| policy | target_tool (owner) | computes | prerequisite |
|---|---|---|---|
| forceplaced_ext_placement_premium | issue_residential_certificate_c6c06832 (agent) | annual_premium | [] |
| forceplaced_ext_renewal_premium | renew_certificate_c91c4d46 (agent) | annual_premium | [] |
| forceplaced_ext_overlap_credit | cancel_certificate_on_evidence_b90eab97 (user) | credit_amount | [] |
| forceplaced_ext_credit_refund | refund_program_credit_d16acbc2 (agent) | refund_amount | overlap, renewal, placement (all value_input, state form) |
| forceplaced_ext_commercial_placement_premium | issue_commercial_certificate_61c928bb (agent) | annual_premium | [] |
| forceplaced_ext_loan_event_credit | cancel_certificate_for_loan_event_5b69d826 (user) | credit_amount | commercial placement (value_input, state form) |

- Overlapping subjects: the three premium schedules each supersede the same base premium sentence and each scopes itself by tier family and by event kind (residential new placement on the latest first-notice loan / residential renewal / commercial placement on the latest first-notice loan); the scopes are pairwise disjoint as written. Overlap credit and loan-event credit scope themselves to "the certificate named on the latest acceptable evidence" and "the certificate most recently issued" respectively, every other cancellation staying on base. No two extended policies reach different conclusions on the same write.
- Triggers / time anchors: placement and renewal are `state_due` and inherit the base 45-day notice gate, program-active gate and renewal-date rule; overlap inherits the base 30-day evidence deadline; loan-event credit is limited to a loan event reported on its effective day; refund is `on_request` on an active or suspended program. Consistent.
- Cross-category reads: placement and renewal read `dwelling_billing` (dwelling_premium_payment, 12 months); commercial placement reads `nfipcom_billing` (nfipcom_premium_payment, 12 months). Read-only; no write crosses categories.
- Scope exclusivity / completeness (from the user scenarios and the prerequisite graph only, pre-reveal): task 0 = refund root + overlap, renewal, residential placement; task 1 = loan-event root + commercial placement. Pairwise disjoint and jointly covering all six. Confirmed against `charter_scope` only after the reveal (closing checklist).
- Conflicts found: see findings P1 (undeclared overrides of `forceplaced_coverage_amount`) and P2 (unanchored prerequisite sentences/conditions).

### rule_compute_equivalence

Mechanical sweep (normalised whitespace): every `compute_basis` value of all six policies is a verbatim substring of its own rule; every sentence of each `baseline.rule` is in the rule; every `prerequisite.policy_source` is in the blocked policy's own rule. Manual sweep, binding by binding:

- Placement / commercial placement: latest FIRST_NOTICE loan and its required amount; limit = ceil to 100, cap at tier max; band ladder; owned-property / owned-building factor (12-month cross-category payments AND program months in force); experience modifier (36-month net claims over 36-month lender payments, clamp 0.85–1.25; 12–35 months claim-count rule; <12 months 1.00); retro load (`>60`, `15..60`, `<15` days lapse→first notice); repeat load (prior issue entries on the same loan); volume factor (issue entries in 12 months, residential only); result `MX(min premium, RND(rated,2))`. Every tier is a rule sentence and a branch of its `decides` binding, and vice versa. No invented basis.
- Renewal: certificate whose latest issue/renewal entry expires today; renewal-notice required amount; limit as above; zone relativity on the issue entry's zone; band; loss load (12-month net claims on the certificate vs 25% of the expiring term's limit; 2% / flat 275 / 0) added after the minimum premium and the sum rounded; term-sequence factor (renewal entries 0/1/≥2); experience and owned-property factors as above. Equivalent.
- Overlap credit: latest acceptable evidence → certificate and coverage start; current term = latest renewal entry else issue entry; current-term basis (whole / zero / pro rata); prior term = the term expiring on the current start (whole / pro rata / nothing); short-period, term and late-evidence retentions; `MX(0, RND(...))`. Equivalent. The effective-date / FLAT-vs-PRO_RATA sentence is an argument rule, not a compute binding (see O5).
- Refund: credit balance = payments + credits − charges − refunds over all entries; clearing hold (tenure <24 OR <6 payments in 12 months → whole last-month payments; 24–59 AND ≥6 → half; else 0); renewal reserve (≥3 / 1–2 / 0 renewal notices in the last month); recent-credit hold (≥5 / 2–4 / <2 credits in the last month); working balance (≥12 / 5–11 / <5 issues in 12 months); `MX(0, RND(...))`. Equivalent; rounding placement differs from the rule's sentence (O3).
- Loan-event credit: latest issue entry under the program; claim bar on that certificate's whole-life net claims; earned-premium method (<90 days: premium − max(25%, pro rata earned); 90–180 days: premium × (1 − (whole months + 1)/12); >180: pro rata); re-placement, young-program and late-placement retentions; `0 if claimnet>0 else MX(0, RND(...))`. Equivalent (wording ambiguity at exact month boundaries, O4).

No empty promise and no compute-only tier found.

### action_binding_and_uuids

- Each `(target_tool, computes)` pair is claimed by exactly one policy (table above). No tool is the target of two policies.
- uuid8s: b90eab97, c91c4d46, c6c06832, d16acbc2, 5b69d826, 61c928bb — six distinct values, no shared prefix, no sequence, no adjacent-value pattern.
- Function bodies: every task tool only creates its rows and updates `premium_balance`; none reads a tracking/evidence/certificate state, none refuses, errors or hints when a prerequisite is unmet. The tool layer judges no prerequisite.
- Docstrings: no ordering word (before/after/first) and no other tool's name — but `cancel_certificate_for_loan_event_5b69d826.certificate_number` says "as shown on the certificate's issue or renewal entry returned by the certificate lookup **or in the reply that issued it**", pointing at the issuing write of another problem (finding P3).
- No scored number appears as a docstring example; no gold leak in parameter descriptions.

### prerequisite_graph

- `prerequisite` filled on all six policies (four `[]`). Edges: credit_refund → overlap_credit, renewal_premium, placement_premium; loan_event_credit → commercial_placement_premium. Every `problem` is an extended policy id in this file, none a base policy, none self. Acyclic (depth 1).
- All four edges `form: state`, no `fallback_reason` (correct for state form). `kind: value_input` on all; `gate` names exist in the blocked compute (`g_cred`, `g_chg` ×2, `c_prem`). `resolved_by` equals each depended-on policy's `target_tool`; each `effect` is true of the tool body (credit lowers / charges raise the balance terms; the issue entry is what `c_cert` reads).
- `condition` fidelity: see P2 — two conditions are literally satisfied at the opening by an earlier tracking cycle on the same loan, and two are narrower than their sentences.
- No authoring-viewpoint phrasing ("in this task", "at the opening") in any `prerequisite` field.

### prerequisite_sentences

| edge | sentence (own rule) | connective | waited-on state | writes that can bring it about |
|---|---|---|---|---|
| refund → overlap | "The refund is not figured until the program account carries an unearned-premium credit for the certificate named on every borrower evidence on file that meets the acceptance rule." | not … until | a premium credit on the account for that certificate | cancel_certificate_on_evidence (and, by the same words, cancel_certificate_for_loan_event, whose docstring also "books the unearned-premium credit for that certificate") |
| refund → renewal | "The refund is fixed only after every certificate whose term has reached its expiration date with no acceptable borrower evidence received carries a renewal entry for the following term." | only after | a renewal entry | renew_certificate only |
| refund → placement | "The refund is fixed only after the program carries an issued certificate on every loan whose first notice is more than the borrower notice period old with no acceptable borrower evidence received and no certificate in force." | only after | an issued certificate on the loan | issue_residential_certificate (residential tier) |
| loan-event → commercial placement | "The loan-event credit is fixed only after the loan carries the certificate that its first notice made due once the borrower notice period ran with no acceptable borrower evidence received." | only after | the certificate the first notice made due | issue_commercial_certificate (commercial tier) |

- Four-point test: ordering connective present on all four; each names a record-visible state in table words with no tool, policy id, snake_case token or row id; no second wording; the depended-on rules do not restate the sentences.
- Derivation (single reading intended): sentence + records + depended-on rule → (1) the acceptable evidence rows → overlap rule's cancellation write; (2) the certificate expiring today → renewal rule's write; (3) the loan past its notice period → placement rule's write; (4) the paid-off loan's due certificate → commercial placement rule's write.
- Strength/scope defects: see P2 (unanchored in time; broader than the declared conditions).
- No base rule sentence grounds an edge; no extended rule states a cross-problem order that grounds no declared edge.

### override_declarations

Sentence-by-sentence against `base_policy_refs`:

- `forceplaced_effective_date_premium`: the premium sentence is superseded and declared by placement, renewal and commercial placement (each scoped). Backdating and term sentences followed (tools take start/expiration; scored at task level). Followed.
- `forceplaced_coverage_amount`: **not named in any overwrite**, yet handled differently by the three premium schedules (P1): (i) "The mandatory purchase amount (required_amount) is the lowest of the loan's outstanding principal balance, the tier's nfip_max_building_reference and the building's insurable value" vs placement/commercial "that loan's mandatory purchase amount is the required amount stated on that first notice" and renewal "its mandatory purchase amount for the renewed term is the required amount stated on its renewal notice" (base adds "The amount is recomputed from the balances reported at each renewal"); (ii) "under GAP_TO_MANDATORY it is the required amount less the building limit of the borrower's own policy in force; under REPLACEMENT_COST it is the insurable value" vs placement/renewal "The building limit … is that mandatory purchase amount rounded up … and capped", applied to every tier "that places residential buildings", Gap and Replacement Cost included.
- `forceplaced_notice_and_placement`: followed (45-day gate, active program, SFHA, evidence, one certificate per loan inherited).
- `forceplaced_agg_program_account`: refund overwrite declared and scoped; statement-month posting followed by all tools.
- `forceplaced_evidence_cancellation`: flat/pro-rata clause declared by the overlap policy; acceptance rule, deadline and "due even when a claim was paid" inherited. The loan-event policy additionally "overwrites" the deadline sentence with a paraphrase that changes nothing (O6).
- `forceplaced_loan_event_cancellation`: PRO_RATA clause declared and scoped; paid-claim bar carried in the extended rule; effective-date sentences followed.
- `forceplaced_renewal`: followed (renews on expiration date when no acceptable evidence and loan still serviced).

### factor_ladders

| policy | factor | effect | ladder (tiers) | multi-source | cross_difficulty | stated in rule / compute |
|---|---|---|---|---|---|---|
| placement | band_rate | parameter | 0.88 / 1.05 / tier rate | no | — | yes / yes |
| placement | reo_credit | parameter | 0.92 / 0.96 / 1.00 | yes (dwelling payments AND program tenure) | dwelling | yes / yes |
| placement | experience_mod | method | credibility formula / claim-count rule / 1.00 | no | — | yes / yes |
| placement | retro_load | parameter | 1.10 / 1.04 / 1.00 | no | — | yes / yes |
| placement | repeat_load | parameter | 1.10 / 1.05 / 1.00 | no | — | yes / yes |
| placement | volume_mod | parameter | 0.95 / 0.98 / 1.00 | no | — | yes / yes |
| renewal | zone_relativity | parameter | 1.40 / 0.90 / 1.00 | no | — | yes / yes |
| renewal | renewal_band | parameter | 0.88 / 1.05 / tier rate | no | — | yes / yes |
| renewal | loss_load | method | 2% of net / flat 275 / none | no | — | yes / yes |
| renewal | term_sequence | parameter | 1.10 / 1.05 / 1.00 | no | — | yes / yes |
| renewal | renewal_experience | method | as experience_mod | no | — | yes / yes |
| renewal | renewal_reo | parameter | 0.92 / 0.96 / 1.00 | yes | dwelling | yes / yes |
| overlap | current_term_basis | method | whole / zero / pro rata | no | — | yes / yes |
| overlap | prior_term_lookback | method | add whole / add pro rata / nothing | no | — | yes / yes |
| overlap | short_period_retention | parameter | 100 / 40 / 0 | no | — | yes / yes |
| overlap | term_retention | parameter | 50 / 25 / 0 | no | — | yes / yes |
| overlap | late_evidence_retention | parameter | 75 / 35 / 0 | no | — | yes / yes |
| refund | clearing_hold | parameter | whole / half / 0 of last-month payments | yes (tenure OR/AND payment count) | — | yes / yes |
| refund | renewal_reserve | method | sum of all / most recent only / 0 | no | — | yes / yes |
| refund | recent_credit_hold | parameter | whole / half / 0 of last-month credits | no | — | yes / yes |
| refund | working_balance | parameter | 1000 / 500 / 0 | no | — | yes / yes |
| commercial | commercial_band | parameter | 0.98 / 1.20 / tier rate | no | — | yes / yes |
| commercial | branch_credit | parameter | 0.92 / 0.96 / 1.00 | yes (nfipcom payments AND tenure) | nfipcom | yes / yes |
| commercial | commercial_experience | method | as experience_mod | no | — | yes / yes |
| commercial | commercial_retro | parameter | 1.10 / 1.04 / 1.00 | no | — | yes / yes |
| commercial | commercial_repeat | parameter | 1.10 / 1.05 / 1.00 | no | — | yes / yes |
| loan-event | earned_method | method | min-earned / monthly / pro rata | no | — | yes / yes |
| loan-event | replacement_keep | parameter | 80 / 40 / 0 | no | — | yes / yes |
| loan-event | young_program_keep | parameter | 60 / 30 / 0 | no | — | yes / yes |
| loan-event | late_placement_keep | parameter | 150 / 75 / 0 | no | — | yes / yes |

- Declared counts: placement 6 (5 param, 1 method); renewal 6 (4/2); overlap 5 (3/2); refund 4 (3/1); commercial 5 (4/1); loan-event 4 (3/1). Bindings disjoint within each policy; every `decides` is an input, never `result`; no factor reads another factor's binding or is gated through another; no result assembled inside a factor; every tier set pairwise disjoint and three tiers deep; no two tiers of a ladder share a value or method as declared.
- Per-task coverage by declaration: task 0 multi-source {reo_credit, renewal_reo, clearing_hold}, cross_difficulty {dwelling ×2}; task 1 multi-source {branch_credit}, cross_difficulty {nfipcom}. Task 1's only multi-source and only cross-difficulty factor is branch_credit.
- Labels: method labels honest (experience: formula vs count rule vs none; loss load: proportional vs flat; current-term / prior-term: whole vs pro-rata vs nothing; earned: min-earned vs monthly vs pro-rata). renewal_reserve's two non-zero tiers are the same formula over a different notice set (see F2).
- Realism of conditions and outcomes: see F2 (two ladders whose tier conditions/outcomes no lender-placed business uses; band rates inverted on tiers the schedules claim; commercial baseline charging nothing for contents on the contents tier) and observations O1, O8.

### findings

**P1 — SOURCE-POLICY RED — undeclared overrides of `forceplaced_coverage_amount` by the premium schedules.**
- Symptom: three extended rules set the mandatory purchase amount and the building limit differently from the base coverage-amount policy, and no overwrite names that policy.
- Evidence (members, all to be closed together):
  1. placement: "that loan's mandatory purchase amount is the required amount stated on that first notice" vs base "The mandatory purchase amount (required_amount) is the lowest of the loan's outstanding principal balance, the tier's nfip_max_building_reference and the building's insurable value".
  2. commercial placement: same sentence, same conflict.
  3. renewal: "its mandatory purchase amount for the renewed term is the required amount stated on its renewal notice" vs base "… The amount is recomputed from the balances reported at each renewal" (the renewal tool itself takes the balances "as the lender reports it for the new term").
  4. placement: "The building limit of a new placement is that mandatory purchase amount rounded up …" applied to every residential tier vs base "under GAP_TO_MANDATORY it is the required amount less the building limit of the borrower's own policy in force; under REPLACEMENT_COST it is the insurable value".
  5. renewal: "The renewed building limit is that mandatory purchase amount rounded up …", same conflict for the Gap and Replacement Cost tiers.
- Demonstrated consequence (same situation, two conclusions): a Residential Gap placement with required amount 150,000 and a borrower policy of 100,000 → base limit 50,000, extended limit 150,000; a residential placement whose principal amortised from 92,410 (notice) to 91,900 (reported at placement) → base limit 91,900, extended 92,500.
- Bears on: no task world numerically — task 0 (Residential Mandatory Amount; notice 92,410 = min(92,410, 250,000, 168,000); renewal notice 250,000 = min(312,480, 250,000, 305,000)) and task 1 (Commercial Building; 412,000 = min(412,000, 500,000, 590,000)) coincide. Charter-level only.
- Affected: forceplaced.extended.yaml, overwrite lists of forceplaced_ext_placement_premium, _renewal_premium, _commercial_placement_premium.

**P2 — SOURCE-POLICY RED — prerequisite sentences and conditions not anchored to the current tracking cycle, and broader than their declared conditions.**
- Members:
  1. refund → placement: sentence "… every loan whose first notice is more than the borrower notice period old with no acceptable borrower evidence received and no certificate in force" and condition "… carries a forceplaced_certificate_issued entry …" carry no time anchor. A loan with an earlier cycle (old first notice, old acceptable evidence, old issued-then-cancelled certificate) is outside the sentence under its literal reading and satisfies the condition at the opening (task 0, loan 5007762019).
  2. loan-event → commercial placement: sentence "… the loan carries the certificate that its first notice made due once the borrower notice period ran with no acceptable borrower evidence received" and condition "… carries a forceplaced_certificate_issued entry …": same defect (task 1, loan 5012240387).
  3. Base `forceplaced_notice_and_placement` "No certificate is issued when acceptable borrower evidence was received before placement" uses the same unanchored phrase; it is base and grounds no edge, but it is the eligibility sentence a reader meets on both placement writes (observation-level member, listed for completeness).
  4. refund → overlap: sentence "an unearned-premium credit for the certificate …" is satisfied by either cancellation write (both docstrings "book the unearned-premium credit for that certificate"); the condition requires a credit "referencing a cancellation entry with reason BORROWER_COVERAGE_CONFIRMED". Sentence broader than condition; two candidate writes.
  5. refund → renewal: sentence covers "every certificate whose term has reached its expiration date with no acceptable borrower evidence received"; condition adds "and no cancellation entry". A cancelled certificate past its old expiration (task 0, LP5102233) is inside the sentence, outside the condition.
  6. refund → placement: sentence also covers paid-off loans with no certificate in force (task 0, 5001187730 and 5009914023); the condition is no narrower.
- Demonstrated consequence: members 1–2 in the task files (task 0: second reading refund 2756.57 instead of 1570.42; task 1: second reading leaves no write). Members 4–6 have no consequence in either world (records exclude the second candidate), recorded for the class sweep.
- Affected: forceplaced_ext_credit_refund.prerequisite (all three edges) and rule; forceplaced_ext_loan_event_credit.prerequisite and rule.

**P3 — SOURCE-POLICY RED — tool docstring points at another problem's write.**
- `cancel_certificate_for_loan_event_5b69d826` arg `certificate_number`: "… returned by the certificate lookup or in the reply that issued it". This tells the agent that the certificate to cancel may come from an issuing call in the same conversation, the hop that the loan-event prerequisite sentence should convey alone. No other docstring has this (swept all six).
- Bears on task 1 (the only task whose tree ends in this tool).

**F1 — SOURCE-FACTOR RED — seeded cross-category rows that their owning charter cannot produce.**
- dwelling (task 0; `dwelling_premium_components`: "RESERVE_FUND_ASSESSMENT is reserve_fund_assessment_pct of the sum of the risk premium and ICC premium"; `dwelling_term_renewed`: "term_start: Start of the renewed term (the prior term end)"):
  1. Every seeded RESERVE_FUND_ASSESSMENT row is 18% of the risk premium alone (e.g. 5DW1029915 2026: 303.56 = 0.18 × 1686.44; charter gives 0.18 × (1686.44 + 30) = 308.96), so every TOTAL payment row the factor sums is 5.40 short.
  2. 5DW1028837 and 5DW1031406: `original_effective_date` 2024-02-10 / 2024-05-22, but the first billing is NEW_BUSINESS with term_start 2025-02-11 / 2025-05-23 (no 2024 term, and terms of 364 days to 2026-02-10 / 2026-05-22).
  3. 5DW1029915: RENEWAL with term_start 2026-09-28 while the 2025-10-02 term runs to 2026-10-02 and the holding shows term_start 2026-10-02.
- nfipcom (task 1; same RFA rule in nfipcom.yaml line 69):
  4. Every RFA row is 18% of risk only (511.02 = 0.18 × 2838.98).
  5. 5GP2004418: RENEWAL term_start 2025-03-03 after a term starting 2024-03-02, then 2026-03-02.
  6. 5GP2007731: RENEWAL term_start 2026-06-18 while the term started 2025-10-10 runs to 2026-10-10 (holding term_start 2026-06-18, original 2024-10-10). This 3,960.00 payment is the row that puts task 1's branch_credit on its middle tier.
- Consequences are demonstrated per task (task 1: the tier rests on member 6; task 0: tier unchanged, evidence not producible).

**F2 — SOURCE-FACTOR RED — ladder tiers whose condition or outcome no lender-placed flood business uses.**
1. refund `renewal_reserve`, tier "with 1 or 2 such notices it is the required amount on the most recently mailed renewal notice divided by 100 times the tier's building rate per 100": a reserve "for renewals about to be billed" that, with two pending renewals, reserves one and drops the other, while with three it reserves all. No carrier holding back for pending renewal billings drops one of two pending renewals; the tier split exists only to make a method ladder. It is the refund policy's only `method` factor; struck, the refund computation has 3 factors and no method.
2. loan-event `young_program_keep`: "Tidemark keeps … 60 dollars of it when the program has been in force fewer than 12 months, 30 dollars when it has been in force 12 to 35 months". The unearned premium returned on a loan payoff, transfer or map removal depends on the certificate (its premium, time in force, claims); no lender-placed carrier weighs the age of the lender's master program when settling that certificate's credit. Struck, the loan-event computation has 3 factors.
3. placement / renewal band ladders: the absolute rates 0.88 (≥200,000) and 1.05 (<100,000) apply to every residential tier. On Residential Gap (tier rate 0.85) larger amounts pay a higher rate than the middle band, and on Manufactured Home (tier rate 1.35, if "a program whose tier places residential buildings" covers it, O10) both bands are 22–35% cheaper than the standard. No task exercises these tiers.
4. commercial placement baseline and schedule: "The rated amount of a commercial placement is its building limit divided by 100 times the rate per 100" also governs the Commercial Building and Contents tier, which places a contents limit (base coverage-amount rule) but is charged nothing for it. No task exercises this tier.
- Consequence: members 1 and 2 demonstrated in task 0 and task 1 files; members 3–4 are charter-level.

**Observations (not grounds for rework on their own):**
- O1 renewal `loss_load`: for an expiring limit below 55,000 the heavy tier (2% of net) is below the light tier (flat 275) between 25% of the limit and 13,750 (e.g. limit 40,000, net 10,000 → 200; net 9,999 → 275). Not reached in task 0 (limit 250,000).
- O2 overlap: the rule does not fix whether the prior-term amount is added before or after the clamped retentions; the order matters only when the current-term credit is below the retentions while a prior-term amount exists. Not reached in task 0.
- O3 refund: the rule rounds "the program's credit balance" and states no rounding after the holds; compute rounds once at the end. In task 0 the half-cent holds (1348.525, 1798.215) sum to whole cents, so both give the same figure; the tool also rounds half-even on booking.
- O4 loan-event earned method tier 2: "whole months in force plus one … any part of a month counting as a full month" reads two ways on an exact monthiversary. Not reached in task 1 (85 days).
- O5 overlap effective date: "takes effect on the start date of the earliest term whose whole premium is credited" can give an effective date later than the start of the credited prior-term overlap (task 0: effective 2026-06-20 while premium from 2025-11-10 is credited); the FLAT_CANCEL enum text speaks only of the "current term".
- O6 loan-event's second overwrite supersedes the base evidence-deadline sentence and replaces it with a paraphrase that changes nothing; the overlap replaced_by paraphrases the base flat/pro-rata clause rather than carrying it verbatim.
- O7 ownership: both cancellation tools are `owner=user`; the blueprint difficulty summary says "The agent … cancels certificates … while the lender alone signs a program termination notice". A lender's cancellation instruction is plausible practice, but it contradicts the constitution's summary.
- O8 realism of carrier retentions on overlap credits (short-period, term, late-evidence) against the base sentence "The lender must refund to the borrower any premium it charged for the overlap period" (the lender funds the gap), and of `late_placement_keep`, which by base timing hits almost every backdated certificate (issue is always ≥46 days after a lapse-date start) and charges the lender at cancellation for Tidemark's own backdating, already priced by the placement retro load.
- O9 issue/renew docstrings call `certificate_expiration_date` "the last day of the … term"; the seed uses the anniversary, which the charter's day count (earlier date excluded, later included) makes the last counted day. One reading in practice.
- O10 "a program whose tier places residential buildings" does not say whether the Manufactured Home tier (occupancy_class MANUFACTURED) is in scope.
- O11 overlap baseline applied where the coverage start precedes the current term gives a credit above the term premium (task 0: 2,844.86 on a 1,768.95 term). Definite and wrong, as required, but not a figure any carrier would give.

## post_reveal_findings

Written after both tasks' frozen derivations were on disk and their GT revealed (2026-10-15T22:33Z). These are charter defects that surfaced in the comparison; the pre-reveal section above is unchanged.

**P4 — SOURCE-POLICY RED — the overlap effective-date sentence admits two readings.**
- Sentence (forceplaced_ext_overlap_credit.rule): "The cancellation takes effect on the start date of the earliest term whose whole premium is credited, or else on the borrower's coverage start, and the credit is booked as a flat cancellation when it takes effect on a term start date and as a pro rata cancellation otherwise."
- Reading A: among the terms credited whole, take the earliest. Reading B (task 0 GT): take the earliest credited term; its start if it is credited whole, else the coverage start. When the coverage start falls inside the prior term, the current term is credited whole and the prior term in part: A → current-term start, FLAT_CANCEL; B → coverage start, PRO_RATA_CANCEL.
- The tool's enum text supports A ("FLAT_CANCEL (the certificate is ended from the start of its current term and the credit returns premium for the whole of that term)"), and neither enum text describes B's case. This supersedes observation O5 (the blind audit took reading A).
- Bears on task 0 (T0-1: 2026-06-20 / FLAT_CANCEL vs GT 2025-11-10 / PRO_RATA_CANCEL).

**Proof-text defect (task-level, not charter):** task 0 `prerequisite_closure.no_user_hint` asserts the scenario "names no … loan"; it names two (T0-2).

## closing_checklist

Not closed. Neither task passes all four relationships (task 0: SOURCE-POLICY, SOURCE-TASK, SOURCE-FACTOR, SOURCE-CHAIN-proof-text; task 1: SOURCE-POLICY, SOURCE-FACTOR).
- Status of the items that can be stated now: the per-task files 0.md / 1.md correspond to tasks 0 / 1 and sit beside this file (revision 1, no older revisions). `charter_scope` confirms the scopes are disjoint and jointly cover all six extended policies (task 0: renewal, placement, overlap, refund; task 1: commercial placement, loan-event). The uuid8s are independent. Trees: task 0 n=3 with 3 value_input edges, task 1 n=1 with 1; each has an owner=user write; the whole-difficulty graph is acyclic. Every factor bears weight on its task's world, and every all-baseline figure differs from gold.
- Open: P1, P2, P3, P4 (charter); F1 (cross-category seed rows), F2 (unreal ladders: refund renewal_reserve and loan-event young_program_keep take their computations below the floor; band inversion and the contents-tier baseline are charter-only).
- The instantiation-stage gates were not re-run on a final form: there is no final form yet.

task0=SOURCE-POLICY+SOURCE-TASK+SOURCE-FACTOR+SOURCE-CHAIN RED task1=SOURCE-POLICY+SOURCE-FACTOR RED
charter=P1,P2,P3,P4,F1,F2

## revision_2

### charter_global_frozen (revision 2)
- Round-2 gate checked first: worklog tail `REWORK round 2: gates 7/7 green`. Snapshot run by the auditor (`/tmp/erl0065_coord/snapshot.sh lender_placed_flood_programs 2`): check_extended / task_tools / replay --check / solvability / compute / grounding / cross_fire green; traceability misses are unlock tool names only; validate INVALID only for documents: 0 (pre-render).
- Hashes: charter 4201c4e5e513489c, task_tools 5b573bc976ac2e00 (both changed from round 1, so every charter-global section was re-derived, not carried forward). Base section still verbatim equal to blueprint/products/forceplaced.yaml.
- Mechanical sweep (scratch): every compute_basis quote, every baseline.rule sentence, every prerequisite policy_source and every overwrite replaced_by is verbatim in its own rule. uuid8s unchanged and distinct. No task-tool docstring carries a reply/issuing reference or a sequence word (before / after / first / then).
- Reworker claims (worklog `## REWORK round 2 claims`) verified item by item below. They were not taken on trust.

### round-1 items (charter)

| id | round-2 state | evidence |
|---|---|---|
| P1 | **closed, one residual member (R2-1)** | Placement and commercial schedules now carry declared overwrites of `forceplaced_coverage_amount` ("The mandatory purchase amount (required_amount) is the lowest of …"). Renewal declares "The amount is recomputed from the balances reported at each renewal." All three are scoped to named tiers (Residential Mandatory Amount / Commercial Building), so the Gap and Replacement Cost limit methods no longer meet these schedules. |
| P2 | closed (all six members) | Refund edge sentences: "… a credit booked on a cancellation for confirmed borrower coverage" (= condition, loan-event write excluded); "every certificate with no cancellation entry whose latest term …"; "… a certificate issued on or after the latest first notice of every loan whose latest first notice … with no acceptable borrower evidence received since that notice" (paid-off loans literally satisfied by their own post-notice certificates). Loan-event: "… a certificate issued on or after its latest first notice … since that notice". Conditions now say "event_date on or after that notice date" and are false at both openings. Base evidence bar overwritten, scoped, in both placement schedules ("received on or after the loan's latest first notice, evidence from an earlier lapse not counting"). |
| P3 | closed | loan-event `certificate_number`: "… returned by the certificate lookup, copied character for character (verbatim)". |
| P4 | closed | "The earliest term the credit reaches is the prior term when the borrower's coverage start falls before the current term's start date and the certificate has a prior term, and the current term otherwise. The cancellation takes effect on the borrower's coverage start or, when that start falls before the start date of the earliest term the credit reaches, on that term's start date; …" — one reading for every coverage-start position (checked: before prior start → prior start, FLAT; equal to a term start → FLAT; inside a term → coverage start, PRO_RATA). Enum texts rewritten to the same rule. |
| F1 | closed | Both worlds' dwelling and nfipcom rows recomputed with their charters. RFA = 18% × (risk + ICC) on every row; TOTAL = sum of components = payment; terms start on prior term ends and NEW_BUSINESS on original effective dates; renewal increases ≤ 18% cap (detail in task files). |
| F2 | closed (all four members) | (1) renewal_reserve now: rate × sum when the average notice amount reaches the tier's minimum-premium break-even, else minimum premium per notice. This mirrors the tier's own premium floor, so it is a real method ladder. (2) young_program_keep replaced by certificate_fee_keep (fully earned fee by premium band, reads the credited certificate). (3) band ladders only price the Residential Mandatory Amount tier (rate 0.95: 0.88 / 0.95 / 1.05 monotone) and the Commercial Building tier (1.1: 0.98 / 1.1 / 1.20 monotone). (4) the Commercial Building and Contents tier is now explicitly under the base rule ("including any on the Commercial Building and Contents tier, remains under the base rule"). |
| O1–O4, O10 | closed | Graduated heavy loss load (275 + 2% of the excess over 25%) is continuous and monotone. Order sentence: "every amount added to it is added before any amount kept is taken off". Refund rounding "as the last step". Monthly wording "plus one more month for the month in progress". Tiers named. |
| O6, O7, O8, O9, O11, O13 | unchanged (observations) | as revision 1. |

### XF_recipe re-check (env_0065 audits/XF_recipe.md), whole charter
- A1–A5: each factor contributes on its own; assembly is generic ("the rated amount … is multiplied by", "holds back from the refundable credit", "every amount added … before any amount kept"). No factor reads another factor's binding (certificate_fee_keep reads its own `fk_prem` from the issue entry). Nothing is gated through another factor; no result is assembled in a factor.
- A3: non-commuting steps fixed: overlap additions before retentions; renewal loss load after the minimum premium; refund and loan-event subtractions with a final clamp commute.
- A6: labels honest; tiers distinct on their reachable domains (renewal_reserve tiers diverge whenever the average amount is below 15,789.47 on the residential tier).
- B8–B11: rule ↔ compute equal; rounding sentences at the compute's placement (refund "rounded … as the last step", overlap and loan-event retentions integer). Terms defined ("earliest term the credit reaches").
- C12–C13: latest/first-match reads scoped and probed (earlier cycle on the same loan, cancelled and paid-off certificates, voided payment, non-acceptable evidence, window edge payments). Conditions are genuinely unmet at both openings.
- D14: sibling overwrites of the premium clause name each other by tier. **Residual R2-1 below** for the coverage-amount clause.
- E15–E16: cross-category rows producible. Company schedules govern only the carrier's own lender-placed premium, credit and refund (no NFIP amount altered).
- F17: one stale proof-text sentence in task 1 (T1-R2-1, in 1.md).

### findings (revision 2)
**R2-1 — SOURCE-POLICY RED — sibling overwrites of `forceplaced_coverage_amount` do not exclude the renewal schedule (remaining P1 member, XF D14).**
- Placement replaced_by: "… a placement under the commercial placement schedule follows that schedule's own first-notice rule, and **for every other certificate the mandatory purchase amount remains the lowest of those three figures**." The commercial replaced_by has the same tail. "Every other certificate" includes a Residential Mandatory Amount renewal.
- Renewal replaced_by: "For a renewal this residential renewal schedule prices, and only for such a renewal, the mandatory purchase amount for the renewed term is the required amount stated on the certificate's renewal notice …".
- Same situation, two conclusions: a Residential Mandatory renewal whose notice (mailed 45 days earlier) states 141,950, while the lender reports a principal balance of 139,800 at renewal (the renewal tool records the balance "as the lender reports it for the new term"). The placement/commercial tails give 139,800 (limit 139,800); the renewal schedule gives 141,950 (limit 142,000).
- Bears on: no task world (task 0 renewal notice 250,000 = min(312,480.00, 250,000, 305,000)). Charter-level.

### closing_checklist (revision 2)
Not closed: task 1 carries T1-R2-1 (proof text) and the charter carries R2-1. Items stated now: per-task files 0.md / 1.md with revision_1 kept intact and revision_2 appended; scopes disjoint and complete (charter_scope: task 0 renewal / placement / overlap / refund; task 1 commercial placement / loan-event); uuid8s independent; trees n=3 (3 value_input) and n=1 (1 value_input), each with an owner=user write, graph acyclic. Every factor bears weight against an honest baseline, and every all-baseline figure differs from gold. Gates re-run on this form by the auditor: green (snapshot round 2).

VERDICT revision_2: task0=PASS task1=SOURCE-TASK RED
charter=R2-1

## revision_3

### charter_global_frozen (revision 3)
- Round-3 gate checked first: worklog tail `REWORK round 3: gates 7/7 green`. Snapshot run by the auditor (`snapshot.sh lender_placed_flood_programs 3`): instantiation gates green; traceability misses are unlock tool names only; validate INVALID only for documents: 0 (pre-render).
- Hashes: charter 5fff544986e0be03 (changed), task_tools 5b573bc976ac2e00 and both masked views unchanged from round 2.
- Mechanical sweep (scratch): base section verbatim equal to blueprint; every compute_basis quote, baseline sentence, prerequisite policy_source and overwrite replaced_by is verbatim in its own rule. Prerequisite sentences, conditions, compute, factors and docstrings are unchanged from revision 2. Re-running both tasks on the round-3 charter reproduces every revision-2 figure (scored values and every factor's baseline-substitution value).

### round-2 items
| id | state | evidence |
|---|---|---|
| R2-1 | closed | Placement coverage-amount tail: "… a placement under the commercial placement schedule follows that schedule's own first-notice rule, a renewal under the residential renewal schedule follows that schedule's renewal-notice rule, and for every other certificate …". The commercial tail is the mirror. Renewal tail: "… a placement under the residential or the commercial placement schedule takes its amount from the loan's latest first notice under that schedule, and at the renewal of every other certificate the amount is recomputed from the balances reported at that renewal." Each of the three overwrites now excludes the other two by name. |
| T1-R2-1 | closed | see 1.md revision_3. |

### whole-class sweep (XF D14, sibling overwrites): every overwrite of the charter
- `forceplaced_effective_date_premium` premium clause: placement names the Residential Mandatory renewal and the Commercial Building placement; renewal names placement under any tier; commercial names Residential Mandatory placement and renewal, and puts the contents tier under base. Closed.
- `forceplaced_coverage_amount`: three overwrites, each naming the other two (above). Closed.
- `forceplaced_notice_and_placement` evidence bar: residential and commercial placement name each other. A renewal is not a placement. Closed.
- `forceplaced_evidence_cancellation`: overlap (flat/pro-rata clause) and loan-event (deadline clause) retire different clauses, each restating the still-in-force base content for out-of-scope cases. Closed.
- `forceplaced_loan_event_cancellation` and `forceplaced_agg_program_account`: one overwrite each, scope named, base treatment restated. Closed.
- Other XF classes (A1–A7, B8–B11, C12–C13, E15–E16, F17) re-checked against the unchanged compute and seed: findings as in revision 2, no new member.

### observations carried (not grounds for rework)
O6 (paraphrased deadline restatement in the loan-event overwrite), O7 (cancellation tools owner=user vs blueprint summary wording), O8 (late_placement_keep keyed to Tidemark's own backdating), O9 (expiration "last day" wording, resolved by the day-count convention), O11 (overlap baseline above the term premium when coverage predates the current term), O13 (same-day placement on a paid-off loan, plausible only as documenting automatic coverage); certificate_fee_keep's issuance fee is not shown charged at placement.

## closing_checklist (revision 3)
- Per-task audit files 0.md and 1.md match tasks 0 and 1 one-to-one, with revisions 1–3 kept in order; each closes its revision-3 comparison with PASS.
- Coverage: all six extended policies covered. charter_scope: task 0 has renewal, placement, overlap and refund; task 1 has commercial placement and loan-event. The scopes are pairwise disjoint over whole trees. Task tools and GT closed; six independently generated, frozen uuid8s.
- Trees: task 0 has 3 prerequisite problems and 3 value_input edges; task 1 has 1 and 1. Each has an owner=user write (overlap cancellation; loan-event cancellation). The difficulty-wide prerequisite graph is acyclic.
- Factors:
  - Every computation has a self-sufficient baseline and 4–6 factors: placement 6, renewal 6, overlap 5, refund 4, commercial 5, loan-event 4. Each has ≥2 parameter and ≥1 method factors.
  - Task 0 has multi-source {reo_credit, renewal_reo, clearing_hold} and cross-difficulty {dwelling ×2} on producible rows. Task 1 has branch_credit as both its multi-source and its cross-difficulty factor, on producible nfipcom rows.
  - Every ladder has ≥3 distinct, realistic tiers stated in its rule. Every factor bears weight on its task's world, and every all-baseline figure differs from gold.
- Instantiation-stage gates re-run on the final form: round-3 snapshot green (traceability and validate only for pre-render unlock-name and documents items).

VERDICT revision_3: task0=PASS task1=PASS
charter=CLEAN

## revision_4

### charter_global_frozen (revision 4)
- Gate checked first: worklog tail `REWORK round 4: gates 7/7 green`. Snapshot round 4 run by the auditor: instantiation gates green; traceability misses are unlock tool names only; validate INVALID with documents: 36, i.e. the render set is incomplete.
- Hashes: charter 72364bc34d7911ed (changed); task_tools 5b573bc976ac2e00 and both masked views unchanged.
- Mechanical sweep: base verbatim; every compute_basis quote, baseline sentence, prerequisite policy_source and overwrite replaced_by is verbatim in its own rule. Factor counts unchanged (6/6/5/4/5/4). Both tasks reproduce every revision-3 figure.
- Scope this round: the renderer's source-scan findings (audits/render_source/lender_placed_flood_programs/render_r1.md F1–F6 and their classes), plus regression of revisions 1–3.

### renderer items (render_r1.md)

| id | state | evidence |
|---|---|---|
| F1 (overwrite retiring an in-force clause) | closed | The loan-event schedule's overwrite of the evidence-deadline clause and its rule sentence are removed; its subject is now [forceplaced_premium_credit]. Class sweep: every remaining overwrite retires a clause the schedule genuinely replaces (premium formula ×3, mandatory amount ×2 + renewal recompute ×1, evidence bar ×2, flat/pro-rata clause, PRO_RATA loan-event clause, refund-on-request clause). |
| F2 (tails deferring to a retired clause) | closed | Placement, renewal and commercial premium tails now restate the formula: "every other certificate premium remains the building limit divided by 100 times the tier's building rate per 100 plus the contents limit divided by 100 times the tier's contents rate per 100, rounded to the cent, and never less than the tier's minimum certificate premium". The refund tail now ends "in full at termination" (no deferral). Overlap, loan-event, coverage-amount and evidence-bar tails each restate their base content. Class closed. |
| F3 (record scope rule ≠ compute) | closed in the charter | Rule: "own NFIP General Property Form or RCBAP policies"; ladder text and cross_category note likewise; equal to the unfiltered XSUM. Stale proof-text member in task 1 (T1-R4-1, 1.md). |
| F4 (unstated tie rules) | **one member remains (R4-1)** | Same-day ties are now stated as "the one entered first in the program's records" for fn_loan (both placements), ev_cert, c_cert and the renewal notice. These match LATEST's strict-">" first-stored behaviour. The renewal selection does not match (R4-1). |
| F5a/b/c, absent records | closed | "when the net amount is zero or below the load is zero" = compute. Retro tiers say "from the lapse date to that notice date … or the notice is dated on or before the lapse date" → 1.00 = signed compute. "when the evidence used names no certificate, there is no certificate to cancel and the overlap credit is zero" = compute (probe: an acceptable evidence with an empty certificate as the latest gives 0, no error). No first notice / no issue entry / no renewal notice outcomes are stated. The no-renewal-notice statement opens R4-2. |
| F6 (prerequisite scope wider than the resolving schedule) | closed | Refund edge 2: "every certificate with no cancellation entry whose latest term expires today …". Edge 3: "the loan named on the program's most recently mailed first notice, once that notice is more than the borrower notice period old … carries a certificate issued on or after that notice". The conditions match verbatim in the charter and in task 0's prerequisite_closure. |

### findings (revision 4)
**R4-1 — SOURCE-POLICY RED — the renewal tie rule contradicts the compute (remaining F4 member).**
- Rule: "When more than one certificate's current term expires today, a certificate whose current term is on a renewal entry is taken before one whose current term is on its issue entry, **and among those the one entered first in the program's records is used.**"
- Compute: `rn_cert: LATEST('forceplaced_certificates', 'certificate_number', event_type='forceplaced_certificate_renewed', certificate_expiration_date=NOW)`, and `is_cert` likewise. Both use LATEST on the default `event_date`, so they pick the entry with the **latest processing date**. Only exact same-date ties fall back to first-stored.
- Probe (scratch copy of task 0's world, one row added): a second renewal entry LP5999999 expiring 2026-10-15, processed 2025-10-20, stored after LP5310427 (processed 2025-10-15). The rule takes LP5310427 (entered first); the compute takes LP5999999. The same holds for issue entries, which are routinely processed on different dates while sharing a backdated expiration.
- Members: rn_cert, is_cert. Bears on no task world (task 0 has one certificate expiring today).

**R4-2 — SOURCE-POLICY RED — the renewal premium overwrite's scope sentence is broader than the rule after the F5 change (XF D14: replaced_by must name its own scope).**
- replaced_by / rule head: "For the renewal of a certificate under a program on the Residential Mandatory Amount tier, **and only for such a renewal**, the premium for the renewed term is set by this residential renewal schedule in place of the base premium formula; … every other certificate premium remains [base formula]".
- New rule sentence: "a certificate with no renewal notice on file **is not priced by this schedule**, its renewed limit being recomputed from the balances reported at that renewal and its premium being the building limit divided by 100 times the tier's building rate per 100 …".
- Same situation, two conclusions: a Residential Mandatory Amount certificate expiring today with no renewal notice. The scope sentence (which the base document will show as the replacement of the premium formula) assigns it to the schedule, which cannot price it (no notice amount). The carve-out assigns it the base formula. The sibling coverage-amount overwrite of the same schedule is already scoped correctly ("For a renewal this residential renewal schedule prices"). The premium overwrite is not.
- Class sweep (scope sentence vs absent-record carve-out): placement ("no first notice has no placement for this schedule to price"), commercial (same), overlap ("names no certificate … credit is zero") and loan-event ("no issue entry has no certificate to credit") all fall outside their own scope sentences, so they are consistent. Single member.
- Bears on no task world (LP5310427 has renewal notices 2025-08-31 and 2026-08-31).

### XF_recipe re-check (whole charter, round 4)
A1–A7 unchanged and clean. B8: R4-1 is the only rule ↔ compute mismatch found. B9–B11 clean. C12: decoys and absent records stated, except R4-1. C13: conditions genuinely unmet at both openings. D14: R4-2. E15–E16 unchanged and clean. F17: T1-R4-1.

### closing_checklist (revision 4)
Not closed. Task 0 PASS; task 1 SOURCE-TASK RED (proof text); charter R4-1, R4-2. Everything else stated in revision 3's checklist still holds on this form (scopes, uuid8s, trees, factor floors, weight, near-misses, producible cross-category rows, gates green).

VERDICT revision_4: task0=PASS task1=SOURCE-TASK RED
charter=R4-1,R4-2

## revision_5

### charter_global_frozen (revision 5)
- Gate checked first: `REWORK round 5: gates 7/7 green`. Snapshot round 5 run by the auditor: instantiation gates green (compute suite branches 48.5 / max 69, up from the overlap guards); traceability misses are unlock tool names only; validate INVALID for documents only.
- Hashes: charter 8b9c472826221264 (changed); task_tools and masked views unchanged.
- Mechanical sweep: base verbatim; every compute_basis quote, baseline sentence, prerequisite policy_source and replaced_by is verbatim in its own rule. No rule defers to "the base rule". Factor counts 6/6/5/4/5/4. Both tasks reproduce every revision-4 figure.

### round-4 items
| id | state | evidence |
|---|---|---|
| R4-1 | closed | Rule: "… and among those the one whose entry carries the latest processing date is used, the one entered first in the program's records when processing dates tie." Equals `LATEST(... event_date)` with strict ">" on rn_cert / is_cert. The round-4 probe (second renewal entry processed 2025-10-20) now gives the same pick under rule and compute. |
| R4-2 | closed | Premium overwrite and rule head now read "For the renewal of a certificate that carries a renewal notice on file under a program on the Residential Mandatory Amount tier, and only for such a renewal …". The no-notice carve-out now falls under the restated base formula in the same tail. Class sweep: placement / commercial (no first notice), overlap (evidence names no certificate) and loan-event (no issue entry) absent-record outcomes lie outside their scope sentences. |
| T1-R4-1 | closed | see 1.md revision_5. |

### render_r1.md items stay closed
F1: the loan-event schedule's only overwrite is the PRO_RATA loan-event clause; subject [forceplaced_premium_credit]. F2: no tail defers to "the base rule"; each premium tail restates the formula. F3: "General Property Form or RCBAP" in rule, ladder and note, matching the unfiltered XSUM. F4: ties stated and equal to compute for fn_loan ×2, ev_cert, c_cert, the renewal notice and now the renewal certificate. F5: zero-or-below loss load, signed retro tier, no-certificate evidence (compute guarded), absent-record outcomes. F6: refund edges 2 and 3 narrowed as in round 4, unchanged.

### findings (revision 5)
**R5-1 — SOURCE-POLICY RED — the renewal schedule's certificate selection does not exclude a cancelled certificate (XF C12 decoy class: cancelled record).** This defect has been present since round 1 and I missed it in revisions 2–4; it is not a regression.
- Rule: "The certificate renewed is the one whose current term, as shown on its latest issue or renewal entry, expires today … among those the one whose entry carries the latest processing date is used". Compute rn_cert / is_cert: `LATEST(... certificate_expiration_date=NOW)` with no cancellation guard. A certificate cancelled mid-term (loan paid off, servicing transferred, removed from the SFHA) keeps an issue or renewal entry whose `certificate_expiration_date` is its original expiry.
- Conflicting passages in the same situation:
  - base `forceplaced_renewal`: "The certificate renews on its expiration date … when … the loan is still serviced by the lender".
  - refund prerequisite: "every certificate **with no cancellation entry** whose latest term expires today …".
  - Both exclude the cancelled certificate; the renewal schedule's selector takes it.
- Probe (scratch copy of task 0's world): add LP5999999 with a renewal entry expiring 2026-10-15 (processed 2025-10-20), a LOAN_PAID_OFF cancellation (effective 2026-09-20) and a renewal notice on file. The schedule selects LP5999999 and prices its renewal at 2,049.01. LP5310427, which the refund gate still requires, is not selected. Without a notice on file the compute errors (int(None) in r_limit).
- Members: rn_cert, is_cert (renewal schedule only). The other latest-reads are consistent with their scope sentences when the selected record is cancelled: the loan-event schedule applies only to an event reported on the most recently issued certificate, and the overlap credit's certificate is resolved through the refund's credit gate.
- Bears on no task world.

### XF_recipe re-check (round 5)
A1–A7 clean. B8: no rule ↔ compute mismatch left; the R5-1 gap is between the selector, base renewal eligibility and the refund gate. B9–B11 clean. C12: R5-1. C13 clean. D14 clean (R4-2 closed; every tail names and excludes its siblings). E15–E16 clean. F17 clean on both tasks.

### closing_checklist (revision 5)
Not closed: charter R5-1 open. Both tasks PASS on all four relationships. Every other item of the revision-3 checklist (scopes, uuid8s, trees, factor floors and weight, producible cross-category rows, gates green) still holds on this form.

VERDICT revision_5: task0=PASS task1=PASS
charter=R5-1

## revision_6

### charter_global_frozen (revision 6)
- Gate checked first: `REWORK round 6: gates 7/7 green`. Snapshot round 6 run by the auditor: instantiation gates green (compute branches 55.5 / max 78, up from the new guards); traceability misses are unlock tool names only; validate INVALID for documents only.
- Hashes: charter dd7495354e5f885f (changed); task_tools and masked views unchanged.
- Mechanical sweep: base verbatim; every compute_basis quote, baseline sentence, prerequisite policy_source and replaced_by is verbatim in its own rule. No rule defers to "the base rule". Factor counts 6/6/5/4/5/4. Both tasks reproduce every earlier figure. The refund edges in task 0's prerequisite_closure equal the charter verbatim.
- render_r1.md F1–F6 re-checked and still closed (loan-event's only overwrite is the PRO_RATA clause; premium tails restate the formula; the GP-or-RCBAP scope holds; tie rules equal compute; absent-record outcomes stated and computed; refund scopes narrowed). R4-1 and R4-2 have not regressed.
- Probes on scratch copies:
  - overlap: latest acceptable evidence naming an already-cancelled certificate → 0.
  - loan-event: latest issue entry already cancelled → 0.
  - both placements: no first notice → 0.
  - In each case the stated outcome equals the compute, and records the schedule does not select fall under the restated base treatment in its tail.

### round-5 item
**R6-1 — SOURCE-POLICY RED — R5-1 is not closed: a cancelled certificate still captures the renewal selection, and now shadows the live certificate due today.**
- What changed: rn_cert / is_cert still select among issue/renewal entries expiring today with no cancellation guard. The rule adds "When the certificate so selected carries a cancellation entry, it is not renewed: this schedule books no renewal for it and the renewal premium is zero". The refund's renewal edge now waits only on "the certificate whose latest term expires today, taken by the latest processing date … unless that certificate carries a cancellation entry …".
- Probe: task 0's world plus LP5999999, with a renewal entry expiring 2026-10-15 processed 2025-10-20 and a LOAN_PAID_OFF cancellation effective 2026-09-20.
  - The schedule selects LP5999999 (c_cancel 1) and gives 0. Because no write follows, every re-evaluation selects LP5999999 again, so live LP5310427 can never be selected.
  - The refund gate counts as satisfied: refund 5,536.04, figured without LP5310427's renewal.
- Conflicting passages in that situation:
  - base `forceplaced_renewal`: "The certificate renews on its expiration date for another certificate_term_months when no acceptable borrower evidence has been received by then and the loan is still serviced by the lender …", so LP5310427 renews today.
  - the premium overwrite: "For the renewal of a certificate under a program on the Residential Mandatory Amount tier, and only for such a renewal, the premium for the renewed term is set by this residential renewal schedule", so LP5310427's premium is this schedule's, and the base formula is excluded for it.
  - the selector: "When more than one certificate's current term expires today … the one whose entry carries the latest processing date is used … When the certificate so selected carries a cancellation entry, it is not renewed …". The schedule never reaches LP5310427.
- Result: LP5310427's renewal premium is defined by no rule. The defect is reworded (the error became a zero), not closed. It is also an outcome no carrier would publish: a live certificate's renewal skipped because a paid-off certificate on another loan carries a later processing date.
- Class sweep (selected record cancelled or absent while a live sibling exists): overlap ("a credit on any other evidence keeps the base treatment"), loan-event ("any other loan-event cancellation keeps the base treatment") and both placements ("every other certificate premium remains [formula]") define the non-selected records through their tails. Renewal is the only schedule whose scope sentence covers every renewal on the tier while its selector can reach only one. Single member.
- Bears on no task world.

### XF_recipe re-check (round 6)
A1–A7 clean. B8–B11 clean (new branches stated and computed). C12: R6-1. C13 clean on both openings. D14: R6-1 (scope sentence wider than what the selector can price). E15–E16 clean. F17 clean.

### closing_checklist (revision 6)
Not closed: charter R6-1 open. Both tasks PASS; every other revision-3 checklist item still holds on this form.

VERDICT revision_6: task0=PASS task1=PASS
charter=R6-1

## revision_7

### charter_global_frozen (revision 7)
- Gate checked first: `REWORK round 7: gates 7/7 green`. Snapshot round 7 run by the auditor: instantiation gates green; traceability misses are unlock tool names only; validate INVALID with documents: 104 (render set incomplete).
- Hashes: charter ecd4da6de009acad (changed); task_tools and masked views unchanged.
- Mechanical sweep: base verbatim; every compute_basis quote, baseline sentence, prerequisite policy_source and replaced_by is verbatim in its own rule. No deferral to "the base rule". Factor counts 6/6/5/4/5/4. Both tasks reproduce every earlier figure. render_r1 F1–F6 and R4-1 / R4-2 hold.

### R6-1 (coordinator-routed count scope): stated, computed, honest?
- **Stated:** yes. "For the renewal of a certificate under a program on the Residential Mandatory Amount tier on a day when exactly one issue or renewal entry of the program expires, and only for such a renewal …", with the tail "every other certificate premium, including each renewal on a day when two or more of the program's issue or renewal entries expire, remains [base formula]". The rule body repeats it. The refund edge now waits on "every certificate whose latest term expires today, other than one carrying a cancellation entry or one for which acceptable borrower evidence has been received".
- **Computed:** yes. `n_today = COUNT(renewed, exp=NOW) + COUNT(issued, exp=NOW)`, and `result = 0 if n_today != 1 or not cert or c_cancel > 0 else …`. Probe (task 0 plus paid-off LP5999999 expiring today): n_today = 2, the schedule gives 0, and LP5310427 now falls under the restated base formula. The shadowing is gone and every renewal has a defined premium. Mechanically, R6-1 is closed.
- **Honest:** no, recorded as R7-1.

**R7-1 — SOURCE-FACTOR RED — the count scope that decides which method prices a renewal is not a condition any lender-placed carrier weighs, and it counts cancelled certificates.**
- The scope switches a renewal between the six-factor schedule and the bare base formula according to how many of the program's issue or renewal entries happen to carry today's expiration date. That includes the entries of certificates cancelled months earlier, because n_today has no cancellation guard and the rule's words ("issue or renewal entry of the program expires") include them.
- Same certificate, same day: in task 0's world LP5310427 renews at 3,965.62 under the schedule (zone 1.40, band 0.88, loss load 275, sequence 1.05, experience 1.18874, owned-property 0.96). Add only a paid-off certificate on another loan whose old renewal entry also shows 2026-10-15, and LP5310427 renews at 2,375.00 (250,000/100 × 0.95), with every rating factor dropped.
- No carrier prices one borrower's renewal by whether an unrelated (here already cancelled) certificate shares its anniversary. In any realistically sized program two or more anniversaries fall on the same day routinely, so the schedule would rarely apply at all. Under the skill's realism test, this is a condition "no business in that line weighs for that quantity", deciding the scored method.
- This is the routed fix as written. It is reported because it fails the honesty test the coordinator asked me to apply. It is not a regression.

### second-record class (coordinator route), every read
Judged each reworker table entry against the rule:
- Placements: fn_loan is scoped by its scope sentence with a restated tail. fn_req, band_req, retro_lapse and retro_notice are loan-filtered latest notices, as stated. repeat_count counts every earlier issue on the loan, as stated. Aggregates are honest.
- Renewal: cert is resolved by the count scope (see R7-1 for its honesty). rn_req / rb_req read the latest renewal notice, else the latest entry, as stated. zone_code reads the issue entry (renewal entries carry no zone), which is honest. lc_net, lc_limit, seq_count and c_cancel are certificate-filtered.
- Overlap: ev_cert is scope-sentenced. ev_eff, le_recv and ev_cancel are certificate-filtered. The current and prior terms are read from the latest renewal entry, else the issue entry, matched by exact date. sp_orig is the original issue start ("original start date"), honest.
- Refund: aggregates only.
- **Loan-event: one member fails (R7-2).** c_cert is scope-sentenced. c_prem, c_start and c_exp come from the certificate's **issue entry** even when the certificate has since renewed.

**R7-2 — SOURCE-POLICY RED — the loan-event credit reads the issue entry's term for a renewed certificate (second-record class: issue entry vs current renewal entry).**
- Rule: "The certificate credited is the one on the issue entry with the latest processing date under the program, and its premium, start date and expiration date are read from that issue entry". Compute: c_prem / c_start / c_exp = LATEST(issued, certificate_number=c_cert).
- Base `forceplaced_loan_event_cancellation` (the clause this schedule replaces in scope) credits "the annual premium multiplied by the days from the cancellation effective date to the certificate expiration date divided by the days in the certificate term", i.e. the term in force at cancellation. The overlap schedule reads "the current term of the certificate is the term on its latest renewal entry, or on its issue entry when it has no renewal entry".
- Probe (task 1's world, LC5236617 re-dated so it is the most recently issued certificate: issued 2025-02-27 → 2026-02-27, premium 6,380.00, renewed 2026-02-27 → 2027-02-27 at 6,500.00; payoff reported today 2026-10-13):
  - The schedule applies (an event on the most recently issued certificate, reported on its effective day).
  - em_credit = 6,380 × DAYS(2026-10-13, 2026-02-27) / 365 = −3,985.32, so the credit is **0**.
  - The unearned premium of the term actually in force is 6,500 × 137/365 = 2,439.73.
- A payoff during a renewal term is ordinary. Refunding nothing because the rule looks at the expired first term is an outcome no carrier publishes, and it contradicts the base clause's "certificate expiration date" for the term in force.
- Members: c_prem, c_start, c_exp (and through them the earned-method tier and the pro rata credit). fk_prem and lp_issued read issue-specific facts by design (the fee and the processing lag of the issue), so they are honest.
- Bears on no task world (task 1's LC5456061 is issued and cancelled on the same day).

### XF_recipe re-check (round 7)
A1–A5 clean. A6/A7 and E16: R7-1. B8–B11 clean. C12: R7-2 (second record). C13, D14, E15 and F17 clean.

### closing_checklist (revision 7)
Not closed: charter R7-1, R7-2. Both tasks PASS; every other revision-3 checklist item still holds on this form.

VERDICT revision_7: task0=PASS task1=PASS
charter=R7-1,R7-2

## revision_8

### charter_global_frozen (revision 8)
- Gate checked first: `REWORK round 8: gates 7/7 green`. Snapshot round 8 run by the auditor: instantiation gates green; traceability misses are unlock tool names only; validate INVALID with documents: 104.
- Hashes: charter a9158c88d24593b5 (changed); task_tools and masked views unchanged.
- Mechanical sweep: base verbatim; every compute_basis quote, baseline sentence, prerequisite policy_source and replaced_by is verbatim in its own rule. Factor counts 6/6/5/4/5/4. Both tasks reproduce every earlier figure. render_r1 F1–F6 and R4-1 / R4-2 hold.

### round-7 items
| id | state | evidence |
|---|---|---|
| R7-1 (count-switched pricing) | the count switch is withdrawn: one pricing method, rule = compute | The scope sentence, rule and tail now name "the renewal this residential renewal schedule processes today". The selector (latest processing date, renewal entry before issue entry, first entered on a tie) equals rn_cert / is_cert. The result is the schedule premium, or 0 when the processed certificate carries a cancellation entry. The refund's renewal edge names the same certificate. |
| R7-2 (loan-event reads the issue entry's term) | closed for the credit itself; **a second-record member remains (R8-2)** | c_prem / c_start / c_exp now read the latest renewal entry, else the issue entry ("its term in force"), in rule, baseline and compute. Probe (renewed LC5236617, payoff 2026-10-13): em_credit = 2,439.73 (6,500 × 137/365), where round 7 gave 0. |

### findings (revision 8)
**R8-1 — SOURCE-POLICY RED (undeclared override of base `forceplaced_renewal`) and realism — the processed-today selector still lets one certificate, a cancelled one included, push every other certificate expiring today off renewal.** This is the R5-1 / R6-1 / R7-1 line: reworded, not closed.
- New text, in the premium overwrite's replaced_by and in the rule: "a renewal on that tier that this schedule does not process today is referred to Tidemark's renewal desk with no premium booked for it today"; "every other certificate whose current term expires today is not processed by this schedule today but referred to Tidemark's renewal desk, and nothing is booked for it today".
- Base `forceplaced_renewal` (in base_policy_refs, **not** named in any overwrite): "The certificate renews on its expiration date for another certificate_term_months when no acceptable borrower evidence has been received by then and the loan is still serviced by the lender with the building in a Special Flood Hazard Area". The new sentences stop an eligible certificate from renewing on its expiration date. That changes base renewal timing without a declared overwrite.
- Probes (scratch copies of task 0's world):
  - (a) Add paid-off LP5999999, whose renewal entry expires 2026-10-15 and was processed 2025-10-20. The schedule processes LP5999999 (cancellation entry) and books nothing. Live LP5310427 is "referred to Tidemark's renewal desk, nothing booked today". The refund's renewal edge names only the processed certificate, so it counts as satisfied and the refund is 5,536.04 without LP5310427's renewal.
  - (b) Add a live LP5999999 instead. The schedule renews it at 2,636.15, and LP5310427 is again referred with nothing booked.
  - In both, a borrower's lender-placed certificate passes its expiration with no renewal and no premium.
- Realism: lender-placed programs renew every eligible certificate on its anniversary so that the lender's protection is continuous. That is the purpose of the master policy and the base sentence above. No carrier limits a program to one renewal a day, or lets a cancelled (paid-off) certificate's stale entry take that slot. The cancelled-record capture first reported as R5-1 is still present, and its consequence has moved from an error (R5-1) to zero (R6-1) to a referral (R8-1).
- Members: the renewal selector (rn_cert / is_cert with the referral sentence) and the refund renewal edge that inherits its single-certificate scope. The other schedules give the records they do not select a defined base treatment.

**R8-2 — SOURCE-POLICY RED — late-placement retention: rule and compute disagree on a renewed certificate (R7-2 second-record class, a member created by the R7-2 change).**
- The rule redefines the certificate's "start date" as that of its term in force ("its premium, start date and expiration date are those of its term in force, read from its latest renewal entry …"). The late-placement tier still reads "when the certificate's issue entry was processed more than 60 days after its start date", and the rule's day count is "counted from the earlier date to the later date".
- Compute: `lp_keep … DAYS(c_start, lp_issued) > 60 …`, with c_start now the renewal start and the signed DAYS. For a renewed certificate the issue was processed before the renewal start, so DAYS is negative and the tier is "30 days or fewer" → 0.
- Probe (renewed LC5236617: issue term 2025-02-27, issue processed 2025-04-17, renewal 2026-02-27; payoff 2026-10-13). Three readings give three different credits:
  - Compute: 2,339.73 (lp_keep 0).
  - Rule's literal day count (unsigned): 316 days between 2025-04-17 and 2026-02-27 → 150 → 2,189.73.
  - Issue-lag reading (the retention's evident subject, issue processed 49 days after the issue term's start): 75 → 2,264.73.
- Members: lp_keep (its start date). em_credit's "in force fewer than 90 days, counted from its start date" now consistently means the term in force, so it is honest per term. fk_prem is issue-specific by design.
- Bears on no task world.

### XF_recipe re-check (round 8)
A1–A7 clean apart from R8-2's binding read. B8: R8-2. B9–B11 clean. C12: R8-1 (cancelled record captures the selection). C13 clean on both openings. D14 / check 1: R8-1 (undeclared override of `forceplaced_renewal`). E16: R8-1. F17 clean.

### closing_checklist (revision 8)
Not closed: charter R8-1, R8-2. Both tasks PASS; every other revision-3 checklist item still holds on this form.

VERDICT revision_8: task0=PASS task1=PASS
charter=R8-1,R8-2

## revision_9

### charter_global_frozen (revision 9)
- Gate checked first: `REWORK round 9: gates 7/7 green`. Snapshot round 9 run by the auditor: instantiation gates green; traceability misses are unlock tool names only; validate INVALID with documents: 104.
- Hashes: charter 9695bfbb304bf651 and task_tools 121a69cd3c01aefc changed; masked views unchanged.
- Mechanical sweep: base verbatim; every quote, baseline sentence, policy_source and replaced_by verbatim in its own rule. Factor counts: placement 6, renewal 6 (1 method), overlap 5, refund 4, commercial 5, loan-event 4.
- uuid8s unchanged. The renewal tool's new `renewal_rate_per_100` description states format only (4 dp, half-even); no example value, no sequence word.
- render_r1 F1–F6, R4-1 and R4-2 hold. The prior R5–R8 selector items are moot: there is no selection.

### round-8 items
| id | state | evidence |
|---|---|---|
| R8-1 | closed | Rule: "Every certificate of the program whose current term expires today renews today, unless it carries a cancellation entry or acceptable borrower evidence has been received for it, and all renewals booked on one day take the same program renewal rate per 100."<br>Premium overwrite: "For every certificate that renews under a program on the Residential Mandatory Amount tier … the renewed building limit divided by 100 times the program renewal rate per 100 in effect on the renewal date …".<br>The compute now yields the program rate from program-level records only, so no certificate selection exists. Base `forceplaced_renewal` timing is untouched. The refund edge covers every eligible certificate expiring today.<br>The rate's inputs (claims, lender payments, issue entries, dwelling payments) are not changed by renewal writes, so "one rate per day" holds at every handling time. The cancelled-record capture (R5-1 → R8-1) is gone. |
| R8-2 | closed | Rule, ladder and compute measure "processed … after the start date shown on that issue entry" (lp_start = issue entry's coverage_effective_date). The issue processing date is never before that start (backdated to the lapse date or started on the issue date), so the day count is non-negative and the rule's unsigned and the compute's signed counts agree. |

### new renewal factors: realism judged from scratch
- renewal_experience (method): unchanged credibility formula, honest.
- renewal_reo (owned-property account credit, dwelling cross-difficulty, multi-source): unchanged, honest.
- program_tenure (0.95 / 0.98 / 1.00 at 60 / 24 months): a loyalty or tenure account credit, plausible.
- coastal_concentration (1.10 / 1.05 / 1.00 on V/VE certificates issued in 36 months): a portfolio catastrophe-concentration load on the program rate, plausible. Observation: it counts issues, including certificates since cancelled, rather than coastal exposure in force.
- payment_record (0.98 / 0.99 / 1.00 at 10+ / 6–9 / <6 lender payments in 12 months): a regular-remitter credit, plausible enough. Observation: it counts remittances rather than timeliness, and a duplicate remittance counts.
- claim_frequency (1.08 / 1.04 / 1.00 at 5+ / 1–4 / 0 claim payments in 12 months): **R9-1**.

### findings (revision 9)
**R9-1 — SOURCE-FACTOR RED — the "claim frequency" load counts claim payment items, voided ones included, not claims.**
- Rule: "Claim frequency load: the program renewal rate per 100 is multiplied by 1.08 when 5 or more claim payments were issued under the program's certificates in the last 12 months, by 1.04 when 1 to 4 were, and by 1.00 when none was." Compute: `cf_count = COUNT(forceplaced_claims, within_months=12, event_type='forceplaced_claim_paid')`.
- A frequency load measures how many losses occurred. A flood claim routinely produces several payment items: advance, final and supplemental payments, or a check voided and reissued. Counting items prices how a claim was paid out, not how many claims there were. In task 0's world the single claim FPC5040217 contributes three items, one of them (CK5401183, 5,400.00) later voided as an overpayment. Here the tier is the same either way (1 claim or 3 items → 1.04).
- Two illustrations, from the charter's own claim mechanics: one claim paid in five installments would take the 1.08 high-frequency tier, as five separate one-payment claims would; a mistaken payment voided the next week still counts toward the load. No carrier counts payment line items, still less voided ones, as claim frequency. The condition is not one the line of business weighs for that quantity.
- Struck, the renewal keeps 5 factors (4 parameter, 1 method), still within 4–6 with ≥2 parameter and ≥1 method, so task 0's factor floor holds. The finding is charter-level and does not change task 0's verdict.
- Class sweep (claim counts used as conditions): placement / commercial exp_recent ("when any claim payment was issued … in the last 12 months") is an existence test, unaffected by item counts, so it is honest. Single member.

### XF_recipe re-check (round 9)
A1–A7 clean (rate factors multiply one generic figure; the renewal's assembly is in `result`; no factor reads another's binding). B8–B11 clean: rate rounded to 4 dp "as the last step", equal to RND(…, 4); premium from the rounded rate. C12–C13 clean. D14 clean: the renewal overwrites name every renewal on the tier and restate base for the rest. E15 clean. E16: R9-1. F17: T0-R9-1 (0.md).

### closing_checklist (revision 9)
Not closed: charter R9-1; task 0 SOURCE-TASK RED (proof text). Task 1 PASS. Trees, scopes, uuid8s, factor floors and weight, and producible cross-category rows still hold on this form, with the renewal now 6 factors and multi-source / cross-difficulty via renewal_reo.

VERDICT revision_9: task0=SOURCE-TASK RED task1=PASS
charter=R9-1

## revision_10

### charter_global_frozen (revision 10)
- Gate checked first: `REWORK round 10: gates 7/7 green`. Snapshot round 10 run by the auditor: check_extended / task_tools / replay / solvability / compute / grounding / cross_fire green; traceability misses are unlock tool names only; validate INVALID for the pre-render document set only.
- Hashes: charter 9aabf2fa3babcce6 (changed); task_tools and masked views unchanged.
- Mechanical sweep: base verbatim; every quote, baseline sentence, policy_source and replaced_by verbatim in its own rule. Factor counts 6/6/5/4/5/4. Both tasks reproduce every revision-9 figure.
- render_r1 F1–F6, R4-1, R4-2, R8-1 and R8-2 hold.

### round-9 items
| id | state | evidence |
|---|---|---|
| R9-1 | closed | Rule: "Claim frequency load: … 1.08 when 5 or more claims were reported under the program's certificates in the last 12 months, each claim counted once by its first notice of loss, by 1.04 when 1 to 4 were, and by 1.00 when none was." Ladder: "(one first notice of loss per claim)". Compute: `cf_count = COUNT(forceplaced_claims, within_months=12, event_type='forceplaced_claim_reported')`; inputs: count of claim_number on claim_reported. Rule = compute, and a reported-claim count is how a frequency load is measured. Payment items and voids no longer count (task 0: 1 claim, not 3 items). Class sweep: the experience modifiers' "any claim payment was issued" test is an existence test, so it is honest. No other claim-count condition exists. |
| T0-R9-1 | closed | see 0.md revision_10 (all three stale statements rewritten; current-design sections and non-rationale fields swept clean). |

### XF_recipe re-check (round 10)
A1–A7, B8–B11, C12–C13, D14, E15–E16 and F17 all clean on this form. Observations carried, not grounds for rework:
- O6, O7, O8, O9, O11, O13 (as in revision 3);
- certificate_fee_keep's fee is not shown charged at placement;
- coastal_concentration counts issues rather than in-force coastal exposure;
- payment_record counts remittances rather than timeliness.

## closing_checklist (revision 10)
- Per-task audit files 0.md and 1.md match tasks 0 and 1 one-to-one; revisions 1–10 are kept in order. Each closes revision 10 with PASS.
- Coverage: all six extended policies covered. charter_scope: task 0 has renewal, placement, overlap and refund; task 1 has commercial placement and loan-event. The scopes are pairwise disjoint over whole trees. Task tools and GT closed. Six independently generated, frozen uuid8s; the renewal tool's new `renewal_rate_per_100` description carries no example value and no sequence word.
- Trees:
  - task 0: 3 prerequisite problems and 3 value_input edges, with the overlap cancellation as the owner=user write.
  - task 1: 1 prerequisite and 1 value_input edge, with the loan-event cancellation as the owner=user root.
  - Every edge is unmet at the opening and bears weight (task 0 skip effects 1,615.60 / 5,536.04 / 3,713.94 vs 2,527.79; task 1 2,219.68 vs 2,814.29). The prerequisite graph is acyclic.
- Factors:
  - Each computation has a self-sufficient baseline and 4–6 factors with ≥2 parameter and ≥1 method: placement 6, renewal 6, overlap 5, refund 4, commercial 5, loan-event 4.
  - Task 0 has multi-source {reo_credit, renewal_reo, clearing_hold} and cross-difficulty {dwelling ×2}. Task 1 has branch_credit as both its multi-source and its cross-difficulty factor (nfipcom).
  - Every ladder has ≥3 distinct, realistic tiers stated in its rule. Every factor bears weight against an honest baseline, and every all-baseline figure differs from gold.
  - Cross-category rows are producible by their charters.
- Instantiation-stage gates re-run on the final form: round-10 snapshot green.

VERDICT revision_10: task0=PASS task1=PASS
charter=CLEAN

## revision_11

### charter_global_frozen (revision 11)
- Gate checked first: `REWORK round 11: gates 7/7 green`. Snapshot round 11 run by the auditor: instantiation gates green; traceability misses are unlock tool names only; validate INVALID for the pre-render document set only.
- Hashes: charter d9786e1ff14393b2 and task_tools de377c9f3a2436d6 changed; masked views unchanged.
- Mechanical sweep: base verbatim; every quote, baseline sentence, policy_source and replaced_by verbatim in its own rule. Factor counts 6/6/5/4/5/4. Six tools with uuid8s unchanged; no reply/issuing reference and no sequence word in any docstring.
- Both tasks reproduce every revision-10 figure. render_r1 F1–F6, R4-1, R4-2, R8-1, R8-2 and R9-1 hold.

### renderer round-2 items (render_r2.md)
| id | state | evidence |
|---|---|---|
| N1 (extended renewal rule vs in-force base non-renewal clauses) | closed | The rule now reads: "Every certificate of the program whose current term expires today renews today, unless it carries a cancellation entry (among them the entry for a loan paid off, a servicing transfer or a building removed from the Special Flood Hazard Area, the record that the loan is no longer serviced by the lender with the building in that area), acceptable borrower evidence has been received for it, or the program is terminated (its run-off certificates stay in force to their expiration and do not renew) …". Each base non-renewal case maps to a stated exclusion: `forceplaced_renewal`'s evidence, serviced-loan and SFHA conditions, "A certificate whose program is terminated does not renew", and `forceplaced_program_termination`'s run-off clause. Suspended programs still renew, matching base `forceplaced_agg_program_account` ("While suspended, certificates already issued stay in force and renew"). The refund edge and condition carry the same three exclusions ("under a program whose status is not terminated"), verbatim in task 0's closure. The rate compute is unchanged. |
| N2 (renew docstring claimed a stored rate) | closed | Docstring: "… reports the program renewal rate supplied in its confirmation only (the rate is not stored on any entry) …". The body uses the rate only in make_id and the reply string, which matches. Task 0's rationale line matches ("reports it in its confirmation (it is not stored on any entry)"). No other docstring changed. |
| N3 (sibling scope sentences over-claiming) | closed | Each premium overwrite now names its siblings by their own scope: the residential and commercial placement schedules each name the loan on the most recently mailed first notice of a program on its tier, and the renewal schedule names every renewal on the Residential Mandatory Amount tier. Placement tail: "every renewal on that tier is priced by the residential renewal schedule and a placement on the loan named on the most recently mailed first notice of a program on the Commercial Building tier by the commercial placement schedule". The renewal and commercial tails are the mirror. Every other certificate premium is under the restated base formula in all three, so no placement is assigned to two treatments. Same rule head sentences (verbatim check). |

### XF_recipe re-check (round 11)
A1–A7, B8–B11, C12–C13, D14 (sibling tails now exact), E15–E16 and F17 clean. Observations as in revision 10.

## closing_checklist (revision 11)
The revision-10 checklist holds unchanged on this form. Per-task files 0.md / 1.md match tasks 0 / 1, revisions 1–11 kept, each closing revision 11 with PASS. Gates were re-run by the auditor on the final form (round-11 snapshot green).

VERDICT revision_11: task0=PASS task1=PASS
charter=CLEAN

## revision_12

### charter_global_frozen (revision 12)
- Gate checked first: `REWORK round 12: gates 7/7 green`. Snapshot round 12 run by the auditor: every instantiation gate green, traceability OK, validate_scenario VALID.
- Hashes: charter 17231d6916266072 (changed); task_tools and masked views unchanged.
- Mechanical sweep:
  - base verbatim;
  - every quote, baseline sentence, policy_source and replaced_by verbatim in its own rule;
  - every overwrite's superseded_clause verbatim in its base policy's rule (12 overwrites checked);
  - factor counts 6/6/5/4/5/4.
- Both tasks reproduce every earlier figure. render_r1 F1–F6, render_r2 N1–N3, R4-1, R4-2, R8-1, R8-2 and R9-1 hold.

### KB audit source items (audits/policy_kb/lender_placed_flood_programs/kb_audit_report.md)
| id | state | evidence |
|---|---|---|
| SRC-1 (undeclared override of base `forceplaced_renewal` "the limit and premium are recomputed from the balances reported at renewal") | closed | The renewal schedule now declares that overwrite. replaced_by: "For a renewal on the Residential Mandatory Amount tier, and only for such a renewal, the renewed building limit and the premium for the renewed term are figured by this residential renewal schedule from the mandatory purchase amount it sets for the renewed term; at the renewal of every other certificate the limit and premium are recomputed from the balances reported at renewal." It is scoped, restates the in-force content, and is verbatim in the rule. It agrees with the sibling coverage-amount overwrite of the same schedule. D14 table re-checked: every base rule sentence the charter departs from has a declared, scoped overwrite. |
| SRC-2 (pro-rata statements) | closed for rule sentences; parameter remnant logged | Both base rule sentences that state pro rata are overwritten with scoped tails: the evidence-cancellation FLAT/PRO_RATA sentence (overlap) and "Each uses its tier's refund method, PRO_RATA" (loan-event). What remains is variant-parameter meanings only (`premium_proration_basis: DAILY_PRO_RATA`, "Basis for any partial-term premium or credit", and the three loan-event `*_refund_method: PRO_RATA`). These are frozen base parameters that no overwrite can address; per the coordinator brief this base-parameter-only remnant is logged by the coordinator and is recorded here as an observation, not a RED. |
| SRC-3 (refund scope sentence announced holdbacks) | closed | replaced_by and rule head now read "… the refund paid on that request is the refundable credit figured by this refund schedule; a credit balance on a terminated program is still refunded to the lender in full at termination." The words "whatever is held back stays on the account as credit" are gone from the charter and the task files. The holds are stated only in their own factor sentences. |

### XF_recipe re-check (round 12)
A1–A7, B8–B11, C12–C13, D14 (overwrite table complete), E15–E16 and F17 clean. Observations as in revision 10, plus the SRC-2 parameter remnant.

## closing_checklist (revision 12)
The revision-10 checklist holds unchanged on this form. Per-task files 0.md / 1.md match tasks 0 / 1, revisions 1–12 kept, each closing revision 12 with PASS. Gates re-run by the auditor on the final form (round-12 snapshot fully green, including traceability and validate).

VERDICT revision_12: task0=PASS task1=PASS
charter=CLEAN
