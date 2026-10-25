# Policy-task audit — nfip_commercial_rcbap_claims / charter-global

## charter_global_frozen
- Frozen 2026-10-15T22:27Z, auditor: erl-task-policy-audit (independent of the instantiator), round 1.
- Input hashes (sha256 prefix, matching the coordinator gate snapshot `.audit_views/policy/nfip_commercial_rcbap_claims/snapshot_r1.txt`):
  `nfipcom.extended.yaml` 29e5089dd63cebec, `task_tools.py` fa406dde4b9985e8, masked views 0.json 6cd60824805e2618, 1.json bf739e87584dcc19.
- Permitted: blueprint/ (blueprint.yaml, db_schema.json, share_tools.py, products/nfipcom.yaml, products/bizflood.yaml), the extended charter, task_tools.py, the masked views (frozen_time, user_scenario, initial_state only).
- Masked / unread when this section was written: every tasks/*.json field (evaluation_criteria, computations, charter_scope, required_documents, design_rationale, solvability_contract, prerequisite_closure). Nothing in this section comes from a revealed GT.
- Entry conditions: gate snapshot supplied (EXTENDED / TASK TOOL CONTRACT / REPLAY / SOLVABILITY / COMPUTE / GROUNDING / SCOPE all OK; traceability misses only the unlock tool-name provenance of `issue_contents_claim_payment_a4dbf5ac`, and validate_scenario INVALID only on `documents: 0`, both pre-render as the brief states). Masked views and hashes supplied. Input complete.
- Base copy: lines 1-1358 of the extended charter are byte-identical to `blueprint/products/nfipcom.yaml` (diff empty).

### policy_conflict_scan
Six extended policies: building proof amount (`sign_building_proof_of_loss_d76eab34`, user), building payment (`issue_building_claim_payment_972d0779`), contents proof amount (`sign_contents_proof_of_loss_65413413`, user), contents payment (`issue_contents_claim_payment_a4dbf5ac`), cancellation credit (`process_cancellation_a892a1e4`), and cancellation refund (`disburse_cancellation_refund_941cdf13`).
- Subjects/triggers. The two proof-amount policies share subject `nfipcom_proof_of_loss_filed` but split by coverage_part. The two payment policies share `nfipcom_claim_paid` and also split by coverage. Credit and refund split the cancellation ledger: the risk/ICC/HFIAA credits are booked at processing, and the RFA credit plus the payout at disbursement. No two policies write the same quantity.
- Overlap conflicts found:
  - The two payment policies give contradictory priority over the same carried-alone layer (finding CG-2).
  - The credit rule conflicts with the inherited base claim bar and FULL_FROM_INCEPTION (CG-1).
- Time anchors: the proof-of-loss period is `proof_of_loss_days` (60) after date of loss in all four claim policies, consistent with base `nfipcom_proof_of_loss`.
- Cross-category reads: bizflood only (policies, changes, claims).
  - The building proof amount reads SOV building values, without a live-policy filter.
  - The payment policies read the live, non-excess BizFlood policy, its SOV, its endorsements and its adjuster location value.
  - The contents proof amount reads SOV and endorsement contents values, with no live filter, which matches its rule wording.
- Scope: the two tasks claim disjoint policy sets. Task 0 claims building proof plus building payment. Task 1 claims contents proof, contents payment, credit and refund. Together they cover all six policies. (Confirmed against charter_scope only at reveal; see task files.)

### rule_compute_equivalence
- Mechanical sweep (normalized whitespace):
  - Every `compute_basis` quote of all six policies is a verbatim substring of its own `rule`.
  - Every sentence of each `baseline.rule` is in the `rule`.
  - Every `overwrite.replaced_by` is in the `rule`.
  - Every `prerequisite.policy_source` is in the `rule`.
- Ladder sentences are present in prose for every factor, and each `decides` binding branches exactly on the stated tiers, with the gaps below.
- Gaps (compute with no rule basis, or rule tier without compute):
  - `nfipcom_ext_contents_proof_amount.cp_net` = `MN(MX(0, RND(MN(cp_measured, cp_ceiling) - cp_ded, 2)), F('contents_coverage'))`. The outer cap at the contents limit has no rule sentence: the replaced_by deliberately drops "capped at the contents limit" for sworn amounts ("contents are settled at actual cash value held to the contents value ceiling, less the contents deductible, never below zero"). See CG-3.
  - `nfipcom_ext_cancellation_refund.xr_prior` tier 2: the rule says "re-rate credits that no refund settles", but the compute `(xr_rr_prior if xr_rr_prior > 0 else 0)` carries earlier-term RERATE credits with no refund check (CG-3).
  - `bp_required` = `MN(RND(bp_rcv * pct/100, 2), ...)`. The rule states no rounding of the required insurance. There is no effect on whole-dollar values (observation O-6).
- Latest-overall reads where the rule names a narrower record. This is the decoy-guard class (CG-4).

### action_binding_and_uuids
- `(target_tool, computes)` pairs are all distinct, one per policy. Tool docstrings carry no sequence words, name no other tool, and contain no example values (so no gold leak).
- Function bodies only `find`/`create`/`update`, and none checks a prerequisite: no refusal, error or hint on an unresolved prerequisite (lines 36-48, 76-89, 115-127, 155-168, 195-219, 237-254 of task_tools.py).
- uuid8s `d76eab34`, `972d0779`, `65413413`, `a4dbf5ac`, `a892a1e4`, `941cdf13`: no shared prefix or suffix, no sequence pattern. They read as independently generated.
- Payee rule for building payments sits in the docstring enum (INSURED vs INSURED_AND_MORTGAGEE), consistent with base `nfipcom_mortgagee_rights`.

### prerequisite_graph
Edges: building_payment→building_proof_amount (value_input, gate `pb_sworn`); contents_payment→contents_proof_amount (value_input, `cy_sworn`); refund→credit (value_input, `xr_credits`); refund→contents_payment (state_gate, gate `nfipcom_claims.event_type`).
- Graph checks:
  - `prerequisite` is filled everywhere (`[]` on the two proof policies and the credit).
  - The graph is acyclic.
  - Every `problem` is an extended id.
  - `policy_source` is verbatim in its own rule.
  - Every edge has `form: state`, and none carries a `fallback_reason`.
  - `resolved_by` equals the depended-on `target_tool`.
  - Every value_input gate is a real compute binding.
- Defects:
  - The refund→contents_payment `effect` is written from one world's viewpoint (CG-9).
  - The refund→credit `condition` adds "and the policy status is cancelled with its cancellation_effective_date set", which the sentence does not carry (O-3).
  - The state_gate `gate: nfipcom_claims.event_type` is a field, not an eligibility gate id. The extended policies carry no eligibility entries (O-3).

### prerequisite_sentences
- "A building payment on a claim is not issued until the claim file carries a signed and sworn building proof of loss received after the claim's latest adjuster report that measures a building loss."
  - Four-point test: connective "not … until"; record-visible state (a BUILDING proof-of-loss row dated after the latest report with building loss above zero); no tool, id or snake_case.
  - Exactly one write brings the state about: `sign_building_proof_of_loss`. The depended-on rule does not restate the sentence.
  - Derivation: sentence → claim file → the proof-of-loss policy's rule ("A building proof of loss is the signed and sworn statement…") → the user's signing write. Single reading. PASS.
- "A contents payment on a claim is fixed only after the claim file carries a signed and sworn contents proof of loss received after the claim's latest adjuster report that measures a contents loss." Same analysis. PASS.
- "A cancellation refund is fixed only after the premium account carries the CANCELLATION credits for the risk premium, the ICC premium and the HFIAA surcharge referencing the signed cancellation request."
  - The state form holds, and the only write that books those credits is `process_cancellation`.
  - Defect: the sentence requires all three credits, but the credit tool books "a credit of zero is not booked". On a tier with no ICC premium (Non-Residential Condominium Unit: `icc_available: false`, `icc_limit: 0`), or whenever a credit computes to 0, the waited-on state can never hold, so no cancellation refund can ever be fixed (CG-10).
- "A cancellation refund is not disbursed until, for every date of loss on the policy, each coverage measured on the latest adjuster report for that date of loss carries a payment or a written denial dated after that report."
  - The state form holds.
  - In general, two writes of this difficulty bring parts of it about: building payment and contents payment. No denial tool exists in this difficulty or in share_tools, so "written denial" cannot be produced by any write.
  - The edge is bound to contents_payment only; the world decides which payment is needed. Single reading where only one coverage is outstanding (see task 1). Defect in `effect`: CG-9.
- No undeclared cross-problem order was found in any extended rule.
- Base rules carry no order sentence that grounds an edge.

### override_declarations
- `nfipcom_ext_building_proof_amount`:
  - The supersession of the base required-insurance clause is declared.
  - The deductible floor and report choice govern the sworn amount, which base never computes. Base fixes only the cap "A payment is never issued for more than the amount sworn", and it is followed.
  - Base `nfipcom_coverage_limits_deductibles` "A limit or deductible outside these bounds is written at the nearest permitted value only when the customer accepts…" governs issuance and endorsement, not loss. Followed.
- `nfipcom_ext_building_payment` and `nfipcom_ext_contents_payment`: the base "new payment" clause supersession is declared. Base mortgagee payee sentences are followed: building payee per the docstring, contents to the insured alone.
- `nfipcom_ext_contents_proof_amount`: the base contents settlement sentence supersession is declared. The compute keeps the dropped cap anyway (CG-3).
- `nfipcom_ext_cancellation_credit`: the superseded clause names only the PRO_RATA sentence, but the replaced_by and rule govern every current-term credit. Undeclared conflicts with base `nfipcom_cancellation_refund`:
  - (a) "No refund at all is due for the current term under the reasons in claim_bar_reasons when a claim with a date of loss in the current term has been paid … or is still open …; the cancellation still proceeds." The extended rule books current-term credits unconditionally ("Processing a cancellation … books, for the current term, a CANCELLATION credit for the risk premium, one for the ICC premium and one for the HFIAA surcharge").
  - (b) "FULL_FROM_INCEPTION returns every component booked on the policy, fees included". The extended rule returns only risk, ICC and HFIAA for the current term (plus RFA at disbursement), which drops the current-term Federal Policy Fee and probation surcharge (dropped branch).
  - See CG-1.
- `nfipcom_ext_cancellation_refund`: the supersession of "Each refunded component is booked … and the total is refunded" is declared. The claim-bar sentence is not named here either (CG-1).

### factor_ladders
| policy | factor | label | tiers | honest label | distinct outcomes | real |
|---|---|---|---|---|---|---|
| building_proof | bpol_report_choice | method | 3 | NO: picks which report's figure enters the same formula | yes | yes |
| building_proof | bpol_value_basis (bizflood) | parameter | 3 | yes | T2 ≡ T3 in effect (dead tier, CG-5) | T2 not real (CG-7) |
| building_proof | bpol_deductible_floor | parameter | 3 | yes | yes | yes (legacy minimum raised at renewal) |
| building_proof | bpol_prior_sworn | parameter | 3 | yes | yes | yes |
| building_payment | bpay_sworn_total | method | 3 | yes | yes | T1 condition not real (CG-7) |
| building_payment | bpay_alone_layer (bizflood) | parameter | 3 | yes | yes | GPF-real (SFIP GPF Other Insurance), not RCBAP (CG-7) |
| building_payment | bpay_contents_first | parameter | 3 | yes | yes | contradicts cpay_building_first (CG-2) |
| building_payment | bpay_other_cover (bizflood) | parameter | 3 | yes | yes | GPF-real, not RCBAP (CG-7) |
| building_payment | bpay_paid_before | parameter | 3 | yes | yes | yes |
| contents_proof | cpol_report_choice | method | 3 | NO (as bpol) | yes | yes |
| contents_proof | cpol_value_ceiling (bizflood) | parameter | 3 | yes | yes | doubtful (O-5) |
| contents_proof | cpol_deductible_floor | parameter | 3 | yes | yes | yes |
| contents_proof | cpol_prior_sworn | parameter | 3 | yes | yes | yes |
| contents_payment | cpay_sworn_total / alone_layer / building_first / other_cover / paid_before | mirror of building | 3 each | as building | as building | as building |
| credit | cxl_effective_date | method | 5 | NO: selects a date substituted into DAYS(xc_eff, term_end) | T1 ≡ T4 (both `xc_req_date`) | yes |
| credit | cxl_earned_day | method | 3 | NO: selects a number subtracted (1 / DAYS(orig, term_start) / 0) | yes | T2 only undoes cxl_effective_date T3 (CG-8) |
| credit | cxl_term_charge | parameter | 3 | yes | T1 ≡ T2 (the term's one booked RISK_PREMIUM charge, whichever occasion booked it) | — |
| credit | cxl_endorsement_return | method | 3 | yes | yes | yes |
| credit | cxl_rerate_takeback | parameter | 3 | yes | yes | yes |
| refund | rfd_rfa_basis | method | 3 | yes (T1 vs T2/T3) | T2 ≡ T3 (prorate the term's booked RFA charge) | yes |
| refund | rfd_term_balance | parameter | 3 | — | T1 ≡ T2 ≡ T3: all are `pay − chg` | — |
| refund | rfd_rerate_carry | parameter | 3 | — | T1 ≡ T2 ≡ T3: all are max(0, credits − refunded) | — |
| refund | rfd_earlier_terms | parameter | 3 | yes | yes | T2 "no such excess, but…" makes additive balances exclusive (CG-7) |
| refund | rfd_mortgagee_holdback | parameter | 3 | yes | yes | company schedule (O-4) |

- Declared counts per policy: building/contents proof have 4 factors each (1 method, 3 parameter); building/contents payment have 5 each (1 method, 4 parameter); credit has 5 (3 method, 2 parameter); refund has 5 (1 method, 4 parameter).
- Cross-difficulty factors all read `bizflood`. Note that no difficulty of this scenario claims the bizflood category (the blueprint's 5 difficulties claim dwelling, nfipcom, homeflood, excess and forceplaced): O-1.
- Multi-source factors: bpay/cpay alone_layer and other_cover qualify (every non-fall-through tier conjoins BizFlood policy, SOV, NFIP flood zone or date of loss, and BizFlood adjuster or endorsement rows); so do cpol_value_ceiling, cxl_endorsement_return and cxl_rerate_takeback.
- Counting only factors that pass the tests (struck by CG-5/6/7/8):
  - Building and contents proof keep 0 honest method factors, which fails the ≥1 method bound.
  - Credit keeps 2 (endorsement_return, rerate_takeback), which fails the ≥4 bound.
  - Refund keeps 1 (mortgagee_holdback), which fails the ≥4 bound.
  - The payment policies keep 3 or 4, depending on tier and world.

### findings
CG-1 — SOURCE-POLICY RED (undeclared override).
- Symptom: the credit rule books current-term credits for every reason, and returns only risk/ICC/HFIAA (RFA later) for the current term.
- Root cause: the overwrite names only the PRO_RATA sentence.
- Evidence: base `nfipcom_cancellation_refund` "No refund at all is due for the current term under the reasons in claim_bar_reasons when a claim with a date of loss in the current term has been paid … or is still open …" and "FULL_FROM_INCEPTION returns every component booked on the policy, fees included". Extended rule: "Processing a cancellation … books, for the current term, a CANCELLATION credit for the risk premium, one for the ICC premium and one for the HFIAA surcharge …".
- Demonstrated consequence:
  - VOLUNTARY_NOT_REQUIRED with a paid claim dated in the current term: base gives a current-term refund of 0, while the extended rule gives risk credit = premium × unearned/term > 0.
  - DUPLICATE_NFIP_POLICY: base returns the current-term Federal Policy Fee, while the extended rule never books it.
- Affected: nfipcom_ext_cancellation_credit overwrite and rule; nfipcom_ext_cancellation_refund overwrite. Bears on: no current task world (task 1 is BUILDING_SOLD, which is not claim-barred); a latent second answer for any future claim-barred or duplicate cancellation.

CG-2 — SOURCE-POLICY RED (contradictory order over one shared layer).
- Evidence: building payment "The claim's own contents come first in the part of the sworn building amount this policy carries alone: when the claim carries contents proofs of loss, that part is reduced by the contents amounts sworn on them". Contents payment "The claim's building comes first in the part of the sworn contents amount this policy carries alone: when the claim carries building proofs of loss, that part is reduced by the building amounts sworn on them".
- Both reduce one BizFlood per-location deductible layer (`pb_layer` and `cy_layer` read the same `deductible_per_location`, or the same V-zone percentage of `location_value_at_loss`) by the other coverage first. Whenever both coverages are claimed and their sum exceeds the layer, the two rules together assign less than the whole layer to the NFIP-alone part, and each rule's ordering yields a different number for the other coverage's payment.
- Demonstrated in both task worlds: task 0 gives 24,971.08 vs 41,875.70; task 1 gives 5,466.67 vs 16,866.67.
- Affected: both payment rules, `pb_carried` and `cy_carried`.

CG-3 — SOURCE-POLICY RED (compute basis absent from rule).
- (a) `cp_net` outer `MN(…, F('contents_coverage'))`. Example world: measured 120,000, ceiling 150,000 (a BizFlood value change), contents limit 100,000, deductible 5,000. The rule gives 115,000 and the compute gives 100,000.
- (b) `xr_prior` tier 2 ignores "that no refund settles". Example world: an earlier-term RERATE credit already refunded against its certificate record. The rule carries 0 and the compute carries the credit again.
- Neither member is reached by either task world.

CG-4 — SOURCE-POLICY RED (latest-overall reads without decoy guard, so rule and compute disagree).
- Demonstrated member: `pb_chg_eff`/`pb_chg_lim` (and `cy_chg_*`, `cp_chg_*`). The compute takes the latest BizFlood endorsement for the address over all dates and change types, then tests whether it took effect on or before the date of loss.
  - World: VALUE_INCREASE effective before the date of loss plus VALUE_DECREASE effective after it.
  - Compute falls to the SOV value.
  - Rule: tier 2's condition "no value change for the location took effect on or before the date of loss" is false (one did), so tier 1 applies with the pre-loss change's limit.
- Remaining members of the class:
  - `pb_locval`/`cy_locval`: no location filter. A Multi-Location BizFlood with several locations reported on the same date of loss takes the latest report of any location.
  - `bp_n_sov`/`bp_sov_value`, `pb_n_sched`/`pb_sov_value`, `cy_n_sched`/`cy_sov_cont`, `cp_sov_n`/`cp_sov_cont`: count SOV rows of any BizFlood policy, including a cancelled one at the address. The payment rules require "a live BizFlood policy … schedules".
  - Endorsement filters admit LOCATION_ADD/LOCATION_DELETE as "value change".
  - `bp_supp_rc`/`cp_supp_cont`: read only the latest SUPPLEMENTAL. An earlier post-FINAL SUPPLEMENTAL with loss > 0 is missed when the latest one measures 0.
  - `xc_n_endo`/`xc_endo_eff`: any endorsement of any term, by recorded_date, including MORTGAGEE_CHANGE. The rule's "the term's latest endorsement" also admits a no-premium MORTGAGEE_CHANGE.
  - `xc_n_ec`/`xc_ec_eff`/`xr_ec_id`: the latest certificate of any term, applied to the sum of the current term's re-rate credits.
  - `xr_n_ref_plain`: any refund with an empty reference anywhere on the policy.
- Neither task world contains a second record of these kinds (each has a single post-loss value change, a single endorsement, a single certificate), so no current task consequence.

CG-5 — SOURCE-FACTOR RED (tiers with the same outcome).
- `cxl_effective_date` T1 and T4 both select `xc_req_date` ("the event date the request names" / "that named date").
- `cxl_term_charge` T1 and T2: a term books its RISK_PREMIUM once, at NEW_BUSINESS or at RENEWAL (base `nfipcom_premium_components`), so both tiers are "the term's booked charge".
- `rfd_rfa_basis` T2 and T3: prorate the term's booked RFA charge.
- `rfd_term_balance`: compute `RND(xr_pay_term - xr_chg_term, 2) if pay < chg else (RND(xr_pay_term - xr_chg_term, 2) if pay > chg else 0)`, a single expression written as three tiers.
- `rfd_rerate_carry`: T1 (`xr_rr_term`, when refunded = 0), T2 (`xr_rr_term − xr_rr_refunded`) and T3 (0 when refunded ≥ credits) are all max(0, credits − refunded).
- `bpol_value_basis` T2 (building limit when it exceeds the policy RCV) never changes the scored value. If limit > RCV, then required = min(0.8·limit, cap) < limit and also min(0.8·RCV, cap) < limit, so `bp_coins = bp_loss` under T2 and under T3 alike.

CG-6 — SOURCE-FACTOR RED (mislabelled method).
- `bpol_report_choice`/`cpol_report_choice` choose which report's figure enters the unchanged formula.
- `cxl_effective_date` selects a date and `cxl_earned_day` selects a number. Both substitute into the same `DAYS(xc_eff, term_end) − xc_adj`.
- Consequence: the building and contents proof computations have no genuine method factor (bound ≥1 method fails), and the credit computation keeps 1.

CG-7 — SOURCE-FACTOR RED (unreal ladder conditions or outcomes).
- (a) `bpay_sworn_total`/`cpay_sworn_total` T1 make "a payment has already been issued for the same date of loss" decide whether later proofs add up, yet the proof-amount rules make every later proof incremental ("swears only the … amount not yet sworn"). With an earlier timely proof unpaid and a new incremental proof, the fall-through pays only the increment. No claims operation weighs prior payment in summing supplemental proofs.
- (b) `rfd_earlier_terms` T2 "no such excess, but the earlier terms carry re-rate credits": when both an earlier-term overpayment and an unrefunded re-rate credit exist, only the overpayment is refunded. These are additive balances, and no business drops one because the other exists.
- (c) `bpay_alone_layer`/`bpay_other_cover` and the contents mirrors apply the SFIP General Property Form other-insurance clause (primary up to the other flood policy's deductible, then pro rata by amounts of insurance) to the RCBAP tiers too. The RCBAP form's own other-insurance condition instead makes the RCBAP excess over other flood insurance in the association's name. Basis: FEMA RCBAP form, General Conditions "Other Insurance"; the coordinator may re-verify the citation.
- (d) `bpol_value_basis` T2: no adjuster takes the coverage limit as the building's replacement cost for coinsurance. It is also dead per CG-5.

CG-8 — SOURCE-FACTOR RED (factor gated through another).
- `cxl_earned_day` T2 "the days before the current term starts are taken off so that only the current term counts" exists only to cancel `cxl_effective_date` T3 (original effective date). The two read the same reason condition.
- Substituting either one alone on a duplicate or closing-did-not-occur world gives unearned days spanning every past term (for example 13 years on a 2013 policy), so the credit exceeds the term premium many times over.

CG-9 — SOURCE-POLICY RED (authoring viewpoint in prerequisite text).
- The refund→contents_payment `effect`: "The contents payment issued after the SUPPLEMENTAL report settles the only coverage that report measures, so the refund may be disbursed."
- The sentence waits on every measured coverage. Where the latest report measures building and contents, the effect's claim (contents payment unblocks the refund) contradicts the sentence (a building payment is needed too).

CG-10 — SOURCE-POLICY RED (unreachable waited-on state).
- The refund sentence requires the CANCELLATION credits "for the risk premium, the ICC premium and the HFIAA surcharge". `process_cancellation` books no credit of zero ("if amount <= 0: continue"), and the Non-Residential Condominium Unit tier has `icc_available: false`.
- On that tier, or whenever a credit computes to 0, the state never holds, so a cancellation refund can never be fixed.
- Not reached by task 1 (ICC 75).

Observations (no demonstrated consequence on the four relationships):
- O-1: `cross_difficulty: bizflood`. No difficulty claims bizflood, so the factor reads another product's base charter rather than another difficulty's.
- O-2: The seeded legacy deductibles below the current minimums (1,000 building; 500 contents) are states base `nfipcom_coverage_limits_deductibles` forbids at issuance or endorsement. They are justified only as pre-minimum legacy, and the renewal-charge condition stands in for "renewed since". Tier 2 (deductible shown as zero) is not a state base can record, since an unelected deductible takes the default.
- O-3: Refund→credit `condition` adds the status clause. The state_gate's `gate` is a field, not an eligibility gate.
- O-4: Realism, company schedule:
  - The mortgagee holdback and the claims-settled gate on a refund are company practices, not NFIP rules.
  - The ICC and HFIAA credits read only "renewal" charges, so a new-business term cancellation would credit 0 ICC/HFIAA.
  - Base requires notice to the mortgagee on a mortgage-required cancellation, but no tool or claimed event exists for it.
- O-5: `cpol_value_ceiling` holds an NFIP contents claim to another policy's SOV value or endorsement limit. The SFIP settles contents at ACV up to the NFIP limit; a limit on another policy is not a value.
- O-6: `bp_required` rounding has no rule sentence and no effect on these worlds.

## closing_checklist
Written after both reveals. The difficulty does NOT close, because the four relationships do not all PASS.
- Task files: `0.md` and `1.md` match the tasks one to one, and `_difficulty.md` sits alongside them. Round 1, no earlier revisions.
- Both comparison sections match GT figure for figure. Both carry REDs (SOURCE-FACTOR, plus SOURCE-POLICY cited from CG-2), so neither is PASS.
- Coverage and scope: the six extended policies are fully covered. The scopes are disjoint (task 0: building proof + building payment; task 1: contents proof + contents payment + credit + refund), and the tools and GT are closed.
- uuid8s are independent.
- Trees:
  - Task 0: n=1, 1 value_input edge.
  - Task 1: n=3, 2 value_input edges.
  - Each has one user write. Both are acyclic, and the difficulty-wide graph is acyclic.
- Factors: every factor bears weight on its world, and each all-baseline figure is definite and differs from gold. Failing anyway:
  - Duplicate-outcome tiers (CG-5).
  - Mislabelled methods: the proof computations have no genuine method (CG-6).
  - Unreal ladders (CG-7), including the GPF other-insurance clause applied to task 0's RCBAP.
  - Coupled factors (CG-8).
  - Task 1's shortfall tier rests on a renewal state base cannot produce (T1-2).
- Gates were not re-run on a final form: no rework has happened yet.

task0=SOURCE-FACTOR/SOURCE-POLICY RED task1=SOURCE-FACTOR/SOURCE-POLICY RED
charter=CG-1,CG-2,CG-3,CG-4,CG-5,CG-6,CG-7,CG-8,CG-9,CG-10

## revision_2

### charter_global_frozen (round 2)
- Written 2026-10-16, before either task's round-2 GT was opened.
- Gate first: `tail -1 worklog.md` reads `REWORK round 2: gates 8/8 green`.
- Snapshot run by me (`/tmp/erl0065_coord/snapshot.sh nfip_commercial_rcbap_claims 2`). All gates are OK. Traceability misses only the unlock tool-name provenance, and validate_scenario reports only `documents: 0`; both are pre-render.
- Round-2 hashes: `nfipcom.extended.yaml` 1e3e1aab81459dac; `task_tools.py` 4a691a15c27aa962; masked views 0.json 2c7ec7425105e33a and 1.json 36e6f20832fb72f6.
- Both shared inputs changed since round 1, so every charter-global section below was re-derived in full. The base section is still byte-identical to `products/nfipcom.yaml`.
- Mechanical sweep, all clean:
  - every `compute_basis` quote is verbatim in its rule;
  - every `baseline.rule` sentence is in its rule;
  - every `replaced_by` is in its rule;
  - every `policy_source` is in its rule.
- Graph: building_payment→building_proof (value_input), contents_payment→contents_proof (value_input), credit→contents_payment (state_gate, new), refund→credit (value_input). It is acyclic.
- uuid8s are unchanged and independent. Tool bodies judge no prerequisite.
- `process_cancellation` now also writes `nfipcom_mortgagee_notice`, an event type not in this difficulty's claimed event_types (see O2-2).

### round-1 RED closure (by id; class sweep included)
- **CG-1 closed.** The claim bar and the hold on cancelling while claims are open are declared overwrites, scoped to the risk credit. FULL_FROM_INCEPTION, CURRENT_TERM_FULL, PRO_RATA and the fees-earned sentence are declared overwrites in the credit and refund policies. The sibling overwrites of the same base clause each name both sides (risk credit vs the other components).
- **CG-2 closed.** One deductible layer per date of loss, split in proportion to the sworn building and contents amounts. The building and contents shares add up to exactly one layer, and no "first" order remains. A new realism defect sits in this design (R2-2).
- **CG-3 closed.**
  - The contents-limit cap is now stated in the rule and in the replaced_by.
  - The earlier-terms factor is removed.
  - The refund RFA ladder has a new rule/compute gap (R2-4).
- **CG-4 mostly closed.**
  - BizFlood reads are scoped by policy id (the latest-SOV policy, in force on the date of loss) and by location.
  - Value endorsements are limited to VALUE_INCREASE/VALUE_DECREASE.
  - The SUPPLEMENTAL read is stated as the "latest SUPPLEMENTAL".
  - The endorsement and certificate are read by billing reference id.
  - Remaining latest-record scopings are listed under R2-3.
- **CG-5 closed.**
  - The effective-date, earned-day, term-charge, term-balance and re-rate-carry factors are removed.
  - The effective date is now a plain sentence following base.
  - The refund ladders have distinct outcomes.
  - The dead limit tier is replaced by the BizFlood adjuster's value at loss.
- **CG-6 closed.**
  - Report choices are relabelled `parameter`.
  - The proof computations carry `prior_sworn` as their method: sum of earlier proofs vs payments net of voids vs none. I accept that as a change of procedure.
  - Credit methods: current-term return and endorsement return. Refund methods: ICC return and RFA return. Both are judged with the round-1 standard.
- **CG-7 closed.**
  - (a) Sworn totals no longer depend on a prior payment.
  - (b) Additive balances are removed.
  - (d) The limit-as-replacement-cost tier is replaced.
  - (c) The RCBAP other-insurance point is withdrawn. On re-examination, the clause I cited in round 1 ("excess over other insurance in the name of the condominium association") is the Dwelling Form's unit-owner provision. The RCBAP carries the same three-part other-insurance condition as the General Property Form (pro rata; primary when the other policy is excess; primary up to the other flood policy's deductible, then pro rata), which matches the rule as now written. Round-1 T0-1 is therefore withdrawn rather than "fixed".
- **CG-8 closed.** The earned-day factor is removed.
- **CG-9 closed.** The `effect` text is now general ("the coverage still outstanding on a claim's latest adjuster report").
- **CG-10 closed.** The refund now waits on "the policy shows the cancellation processed on the signed request, cancelled with its cancellation effective date set", which can be reached even when the risk credit is 0.

### factor_ladders (round 2, structure)
| policy | factors (label, tiers) | counts |
|---|---|---|
| building_proof | report_choice (param, 3), value_basis (param, bizflood, 3), deductible_floor (param, 3), prior_sworn (method, 3) | 4: 3 param, 1 method, 1 cross, 1 multi-source (value_basis) |
| building_payment | sworn_total (method, 3), alone_layer (param, bizflood, 3), contents_share (param, 4), other_cover (param, bizflood, 3), paid_before (param, 3) | 5: 4 param, 1 method, 2 cross/multi |
| contents_proof | report_choice (param), value_ceiling (param, bizflood), deductible_floor (param), prior_sworn (method), duplicate_sworn (param) | 5: 4 param, 1 method, 1 cross/multi |
| contents_payment | mirror of building_payment | 5 |
| credit | current_term_return (method), previous_term_return (param), endorsement_return (method), rerate_takeback (param) | 4: 2 param, 2 method |
| refund | icc_return (method), rfa_return (method), policy_fee_return (param), probation_return (param), excess_payment (param) | 5: 3 param, 2 method |

- No two tiers in any ladder share an outcome.
- The deductible floors pair the federal minimums: above $100,000 of building coverage, 1,250 building / 1,250 contents; at or below it, 1,000 / 1,000. That matches NFIP practice.
- Ladders still failing the realism test are listed under R2-2 and R2-3.

### findings (round 2)
**R2-1 — SOURCE-POLICY RED (prerequisite sentence narrower than its condition).**
- Sentence (credit rule): "A cancellation is not processed until every claim on the policy is closed, each coverage measured on a claim's latest adjuster report carrying a payment or a written denial dated after that report."
- Declared condition: "… has an nfipcom_claim_paid or nfipcom_claim_denied entry for that coverage, under that claim number or a duplicate claim number for the same date_of_loss …".
- The sentence never says that a payment under a duplicate number closes the claim. Read literally, a claim whose latest report sits under the duplicate first notice stays open for every coverage paid under the other number.
- The building payment rule always pays on "the policy's claim that carries its latest adjuster report", so no write in this difficulty can ever put a payment under the duplicate number. On the literal reading the cancellation can never be processed.
- Demonstrated on task 1. Affected: nfipcom_ext_cancellation_credit rule and prerequisite.

**R2-2 — SOURCE-FACTOR RED (unreal outcome: deductible layer shared with a coverage the other policy does not insure).**
- Rule: "The other flood policy's deductible is one layer for the date of loss, shared between the building and the contents in proportion to the amounts sworn for each".
- The rule applies this whatever the BizFlood tier writes. Neither `pb_layer`'s tiers nor `pb_cont` test whether the BizFlood policy covers contents.
- BizFlood "Building" (`contents_written: false`) carries no contents. The SFIP clause makes the NFIP primary up to that policy's deductible for the property both policies insure. NFIP contents are not "other-insured" there, so diluting the building's primary layer by the NFIP contents claim is a treatment no insurer applies.
- Members: `bpay_contents_share` (all non-fall-through tiers on a building-only BizFlood world). The contents mirror `cpay_building_share` has no score effect in that case: other cover is 0, so the whole contents amount is paid anyway.
- Demonstrated on task 0: 25,939.64 vs 32,325.26.

**R2-3 — SOURCE-FACTOR RED (tier conditions keyed to "the latest" record where the line weighs the record in force or all records).**
- (a) Claim bar keyed to "the policy's latest reported claim has a date of loss in the current term and has been paid" (`cxl_current_term_return` T2, `xc_ldol`/`xc_lpaid`; refund `xr_barred`, which governs the HFIAA, ICC and RFA tier-3 zeros). The FEMA bar (and base) is any claim with a date of loss in the term paid net of voids.
  - World: claim A, date of loss in the current term, paid; claim B, date of loss in the prior term, reported later.
  - Extended: no bar. Base and FEMA: bar.
  - `xc_lpaid` also sums gross payments, so a fully voided payment counts as "paid".
- (b) Value endorsements: "the latest value increase or value decrease … took effect after the date of loss, or none was endorsed → the value on its statement of values" (`bpay_other_cover`, `cpay_other_cover`, `cpol_value_ceiling`).
  - World: a VALUE_INCREASE in force on the date of loss, plus a VALUE_DECREASE effective after it.
  - The rule and compute take the original SOV value, not the limit in force on the date of loss.
- (c) Credit and refund separate only "the policy's latest premium-bearing endorsement" and "the latest re-rate credit" (`xc_endo_id`, `xc_rr_id`, `xr_endo_id`, `xr_rr_id`). A second endorsement in the same term is returned "with the term premium" (× days/term), so its charge Δ·(te−e)/T comes back as Δ·(te−e)(te−eff)/T² instead of Δ·(te−eff)/T.
- No task world contains a second such record, so there is no task consequence.

**R2-4 — SOURCE-POLICY RED (refund RFA ladder: rule and compute disagree).**
- (a) The rule says "Under a reason that bars a refund … nothing of the current term is returned". The `xr_rfa` tier-1 branch has no `xr_barred` test.
  - World: VOLUNTARY_NOT_REQUIRED, a paid claim in the term, an endorsement in the term.
  - Rule: 0 of the current term's RFA. Compute: the prorated tier-1 sum.
- (b) Compute tier 1 is guarded by `not xr_incep`, but the rule lists the endorsement/re-rate tier before "when the reason refunds from inception" with no such exclusion.
  - World: CLOSING_DID_NOT_OCCUR on a first-term policy with an endorsement.
  - Rule order gives tier 1, where the endorsement RFA × days(eff→end)/days(endo eff→end) exceeds the charge itself. Compute gives tier 2 (full less re-rate).
- No task consequence.

### observations (round 2)
- O2-1: Assembly sentences. The credit sentence "the current term's part and the earlier term's part, then the endorsement's part, then the re-rate credit taken back" and the refund sentence listing ICC, RFA, HFIAA, FPF, probation and "premium received but not owed" name quantities, but each is baseline-defined. This is a renderer-risk class (XF A.2), not shown to change any figure.
- O2-2: `process_cancellation` books `nfipcom_mortgagee_notice`, which is outside the difficulty's claimed event_types (SCOPE gate OK).
- O2-3: The proportional layer moves when later proofs arrive. In task 1, the seeded 23,102.04 building payment would now compute to 22,050.91, so the building coverage is overpaid by 1,051.13 after the new contents proof.
- O2-4: "The term before" is read as a term_start within 24 months of NOW (`within_months=24`), which holds only while the current term is under 12 months old.
- O2-5: Task 1's 325.21 renewal overpayment (bill at indicated premium, booking at capped premium) has gone unrefunded since 2026-08-24. Base says the excess is refunded, but gives no timing.

### closing_checklist (round 2)
Written after the reveal; see the task files.
- Task files: `0.md` and `1.md` match the tasks one to one; each has a revision_2 appended after its round-1 text, which is left untouched.
- Both round-2 comparisons match GT figure for figure.
- Coverage and scope: the six policies are covered, and the scopes are disjoint (task 0: building pair; task 1: contents pair + credit + refund).
- uuid8s are independent.
- Trees:
  - Task 0: n=1, 1 value_input edge.
  - Task 1: n=3, 2 value_input edges.
  - Each has one user write. The difficulty-wide graph is acyclic.
- Factors: all of them bear weight, and every all-baseline figure is definite and differs from gold.
- Not closed:
  - R2-1 (task 1).
  - R2-2 (task 0).
  - R2-3 and R2-4 (charter-only; no task consequence).
- Gates on this form were run by the coordinator snapshot (8 suites OK; traceability and validate are pre-render only).

VERDICT revision_2: task0=SOURCE-FACTOR RED task1=SOURCE-POLICY RED
charter=R2-1,R2-2,R2-3,R2-4

## revision_3

### charter_global_frozen (round 3)
- Written 2026-10-16, before either task's round-3 GT was opened.
- Gate first: `tail -1 worklog.md` reads `REWORK round 3: gates 8/8 green`.
- Snapshot run by me (`/tmp/erl0065_coord/snapshot.sh nfip_commercial_rcbap_claims 3`). All gates are OK; traceability and validate misses are pre-render only.
- Hashes:
  - Charter 6fbdcfde022a9de5 (changed, so charter-wide sections were re-derived).
  - `task_tools.py` 4a691a15c27aa962 (unchanged; tool-binding and uuid8 conclusions are carried forward on that hash).
  - Masked views: 0.json e50bf472647915da (changed); 1.json 36e6f20832fb72f6 (unchanged).
- The base section is still byte-identical.
- Mechanical sweep is clean: compute_basis, baseline, replaced_by and policy_source are all verbatim in their rules.
- Factor counts are unchanged from round 2, except `rfd_rfa_return`, which now has 4 tiers (all distinct).

### round-2 RED closure
- **R2-1 closed.** The credit's sentence is now scoped by date of loss: "…every coverage measured on the latest adjuster report for each date of loss on the policy carrying a payment or a written denial for that date of loss dated after that report". The condition and effect say the same. A payment under a duplicate number now closes that date of loss on the literal reading.
- **R2-2 closed.**
  - The layer requires the BizFlood policy to declare a building value (building payment) or a contents value (contents payment).
  - The other coverage's share counts only when the BizFlood policy declares a value for that coverage (`pb_cont`/`cy_bldg` guards).
  - The task 0 world now holds BizFlood "Building and Contents". The premium 72,035.60 = 4.4M × 0.62% × 2.6 + 60,000 × 0.71% × 2.6, consistent with the bizflood rating.
- **R2-3 partly closed.**
  - (b) Closed in rule and compute: the value endorsement used is the one in force on the date of loss.
  - (a) Narrowed but not closed (R3-2).
  - (c) Not closed, only reworded (R3-3).
- **R2-4 closed.** The RFA ladder order (inception, claim bar, endorsement/re-rate term, otherwise) is identical in rule and compute, and the claim-bar tier is explicit.

### findings (round 3)
**R3-1 — SOURCE-POLICY RED (ladder face contradicts the rule; stale proof text).**
- The rules now say tier 2 applies when "no value endorsement for that location was in force on the date of loss". The factor ladders still carry the round-2 tier 2: "that BizFlood policy … and the latest value increase or value decrease endorsed for that location took effect after the date of loss, or none was endorsed".
- Members: `bpay_other_cover` T2, `cpay_other_cover` T2, `cpol_value_ceiling` T2.
- World: a VALUE_INCREASE in force on the date of loss plus a VALUE_DECREASE effective after it.
  - The ladder's T1 (an endorsement in force) and T2 (the latest took effect after the date of loss) both hold, so the ladder's tiers overlap.
  - The rule and compute give T1.
- A factor document rendered from the ladder face would state a condition the rule no longer carries.

**R3-2 — SOURCE-FACTOR RED (R2-3a residual; claim bar still keyed to one "latest" record).**
- Rule: "nothing is returned for the current term when the latest date of loss on which a claim payment was issued falls in the current term and the payments for that date of loss, net of the payment items voided, are above zero" (`xc_ldol`/`xc_lpaid`, `xr_barred`).
- World: a VOLUNTARY_NOT_REQUIRED cancellation, with two dates of loss in the current term.
  - The earlier date of loss was paid with a net payment above zero.
  - The later date of loss's only payment was voided and not yet reissued (net 0).
- That later loss still counts as closed for the hold, since a payment row exists.
- Rule: no bar, so a pro rata current-term refund is due. Base (`nfipcom_msr_term_claims_paid` > 0) and the FEMA claim-paid bar: no current-term refund.
- No task consequence (task 1 is BUILDING_SOLD).

**R3-3 — SOURCE-FACTOR RED (R2-3c not closed: only the latest endorsement or re-rate is separated).**
- The rule now states the scope exactly ("the policy's latest premium-bearing endorsement", "the policy's latest risk premium re-rate credit", and in the refund "the policy's latest Reserve Fund Assessment booked on an endorsement or its latest one credited on a re-rate"). The outcome is unchanged.
- Example: two COVERAGE_INCREASE endorsements in one term, e1 at day 30 (Δ 365) and e2 at day 200, cancelled at day 250.
  - e1's charge of 335.00 is returned "with the term premium" at 115/365 = 105.55.
  - The pro rata return of e1 is Δ × 115/365 = 115.00.
  - The same applies to a second re-rate credit and to the RFA entries.
- No task world has a second endorsement or certificate.

### observations (round 3)
- O3-1: The task 0 association again holds the "Building and Contents" tier, whose entry gate reads "business entity owning the building and its business personal property". This fit was already flagged as doubtful in round 1; no score effect.
- O2-1 is improved: the credit's assembly sentence is now generic. O2-2 to O2-5 are unchanged.

### closing_checklist (round 3)
Written after the reveal; see the task files.
- Both tasks: round-3 comparisons match GT figure for figure, and both PASS on all four relationships.
- Scopes are disjoint and the graph is acyclic.
- Trees: task 0 has n=1 with 1 value_input edge; task 1 has n=3 with 2. Each has one user write.
- Every factor bears weight, and every all-baseline figure is definite and differs from gold.
- Charter-wide REDs still open, none with a task consequence:
  - R3-1: stale tier-2 ladder text in bpay_other_cover, cpay_other_cover and cpol_value_ceiling.
  - R3-2: the claim bar is keyed to the latest paid date of loss.
  - R3-3: only the latest endorsement or re-rate is separated in the credit and refund.
- Gates on this form: coordinator snapshot round 3 is all OK, with traceability and validate misses pre-render only.

VERDICT revision_3: task0=PASS task1=PASS
charter=R3-1,R3-2,R3-3

## revision_4

### charter_global_frozen (round 4)
- Written 2026-10-16, before the round-4 GT was opened.
- Gate first: `tail -1 worklog.md` reads `REWORK round 4: gates 8/8 green`.
- Snapshot run by me (`/tmp/erl0065_coord/snapshot.sh nfip_commercial_rcbap_claims 4`). All gates are OK. Traceability misses only unlock tool names. validate_scenario still reports INVALID, now with `documents: 36` (the KB has partly rendered); this is outside this audit.
- Hashes:
  - Charter fdadeb6760255113 (changed, so charter-wide sections were re-derived).
  - `task_tools.py` 4a691a15c27aa962 (unchanged; tool-binding and uuid8 conclusions are carried forward on that hash).
  - Masked views 0.json e50bf472647915da and 1.json 36e6f20832fb72f6 are both unchanged from round 3, so the worlds are the same.
- The base section is still byte-identical.
- Mechanical sweep is clean (compute_basis, baseline, replaced_by, policy_source).
- The edges and factor counts are unchanged from round 3.

### round-3 RED closure
- **R3-1 closed.** Tier 2 of `bpay_other_cover`, `cpay_other_cover` and `cpol_value_ceiling` now reads "no value endorsement for that location was in force on the date of loss", matching the rules.
- **R3-2 closed as worded, but replaced by a new defect (R4-1).**
  - The bar now sums net payments over "all losses dated in the current term", in rule, ladder and compute of both cancellation policies. It no longer reads a single latest record.
  - The current term is redefined to make that sum computable (R4-1).
- **R3-3 closed by scope.** The coordinator asked whether the routed overwrite's scope is stated, computed and honest.
  - Stated: yes. Both the credit and refund overwrites and rules are self-naming ("… and only while the current term and the term before it together carry at most one premium-bearing endorsement and at most one re-rate credit, each counted by its risk premium entries"). Each restates the base refund-method clause verbatim for every other case, including the fees-earned and claim-bar parts.
  - Computed: yes.
    - `xc_scope`/`xr_scope` count the ENDORSEMENT RISK_PREMIUM charges and RERATE RISK_PREMIUM credits with term_start within 24 months.
    - Out of scope, `xc_base_ret`/`xr_base_other` implement the base clause literally: from inception, every component; CURRENT_TERM_FULL, the current term in full; PRO_RATA, current-term charges × days from the effective date to term_end over term days, with fees earned and the refund equal to the total of the credits.
  - Honest: yes. Out of scope the charter defers to base text it does not alter. The cases that under-refunded in R3-3 are now outside the extended method.
  - Edge note (O4-1): the scope counts only risk-premium entries. An endorsement that books only an RFA/ICC change, with no risk entry, is not counted. In that case the refund's RFA tier, which reads "the policy's latest Reserve Fund Assessment booked on an endorsement", could still pick one of two endorsements. No world has this.

### findings (round 4)
**R4-1 — SOURCE-FACTOR RED (claim bar keyed to a month-count window that is not the policy term).**
- Rule (credit overwrite, credit rule, refund rule and `rfd_rfa_return` T2): "a loss counting in the current term when it is dated no more whole calendar months before the processing date than the current term_start is".
- Compute: `xc_ldol`/`xr_ldol` = MONTHS(term_start, NOW) + 1, used as `within_months`. With `_within` = 0 ≤ MONTHS(date_of_loss, NOW) < k, rule and compute agree.
- The window, however, is not the term. Example:
  - term_start 2026-09-15, processed 2026-10-20, so k = 2;
  - the only loss is dated 2026-08-21 (prior term), paid net above zero;
  - MONTHS(2026-08-21, 2026-10-20) = 1 < 2, so it is counted.
- Under VOLUNTARY_NOT_REQUIRED, the charter then returns nothing of the current term's risk, ICC, HFIAA or RFA.
- Base `nfipcom_cancellation_refund` (`nfipcom_msr_term_claims_paid`: date of loss from term_start inclusive to term_end exclusive) and the FEMA claim-paid bar both count only losses inside the term, so a pro rata current-term refund is due.
- A loss up to about a month before term_start is miscounted whenever the processing day of the month is on or after the term-start day. No business weighs that condition.
- Members: `xc_barred` (cxl_current_term_return T2) and `xr_barred` (`rfd_rfa_return` T2, the zero branches of the HFIAA and ICC returns, and the out-of-scope `xr_base_other`/`xc_base_ret` bar).
- No task consequence: task 1 is BUILDING_SOLD, and task 0 has no cancellation.

### observations (round 4)
- O4-1: risk-entry-only scope count (above).
- O2-1 to O2-5 and O3-1 stand. O2-4 (the 24-month term_start window for "the term before") is the same window device as R4-1. It has not been shown to misclassify a term on these worlds, because term starts are 12 months apart.

### closing_checklist (round 4)
Written after the reveal; see the task files.
- Both tasks' round-4 comparisons match GT figure for figure. Both PASS.
- Scopes are disjoint and the graph is acyclic.
- Trees: task 0 has n=1 with 1 value_input edge; task 1 has n=3 with 2. Each has one user write.
- Every factor bears weight, and every all-baseline figure is definite and differs from gold.
- R3-1 and R3-3 are closed (R3-3 by a scope that is stated, computed and honest).
- R3-2's latest-record defect is closed, but its replacement term window is R4-1 (charter-wide, no task consequence).
- Gates on this form: round-4 snapshot all OK, with traceability and validate pre-render only.

VERDICT revision_4: task0=PASS task1=PASS
charter=R4-1

## revision_5

### charter_global_frozen (round 5)
- Written 2026-10-16, before the round-5 GT was opened.
- Gate first: `tail -1 worklog.md` reads `REWORK round 5: gates 8/8 green`.
- Snapshot run by me (`/tmp/erl0065_coord/snapshot.sh nfip_commercial_rcbap_claims 5`). All gates are OK. Traceability misses only unlock tool names; validate_scenario still INVALID with `documents: 36`, which is a KB-side matter.
- Hashes:
  - Charter d43ada1b2a5d4923 (changed; the claim-bar sentences, ladders and compute of both cancellation policies were re-derived, everything else was carried forward after re-running the mechanical sweep).
  - `task_tools.py` 4a691a15c27aa962, and masked views e50bf472647915da / 36e6f20832fb72f6, all unchanged.
- The base section is byte-identical. The mechanical sweep is clean.
- The R3-1 and R3-3 closures are not regressed: the ladder text is still aligned, and the scope overwrites are unchanged.

### round-4 RED closure — R4-1 (routed by scoped self-naming overwrite)
**Stated: yes.** Credit overwrite and rule, refund rule, and the `cxl_current_term_return` T2 and `rfd_rfa_return` T2 ladders all say the same thing:
- "the one loss reported on the policy within the whole calendar months counted back from the processing date to the current term_start is dated on or after the current term_start and its claim payments, net of the payment items voided, are above zero";
- "when two or more losses are reported within those months, the base claim bar applies as written, that is: no refund at all is due for the current term … when a claim with a date of loss in the current term has been paid or is still open".

**Computed: one-loss branch yes; two-or-more branch no.**
- One loss (`xc_nwin`/`xr_nwin` = 1): `xc_d1`/`xr_d1` (the latest reported date of loss) is that loss, since every loss outside the window is older. The test DAYS(term_start, d1) ≥ 0, with the net payments on d1, is the exact term test. The R4-1 miscount is gone here.
- Two or more losses: compute does not apply the base clause the rule restates. It keeps `xc_barred = … DAYS(term_start, xc_d1) >= 0 and xc_lpaid > 0`, where `xc_lpaid` is the net payments on every loss inside the month window, so it still includes a prior-term loss that falls in the window.

**Honest: no** for the two-or-more branch. The rule promises the base clause verbatim; compute keeps the window sum. See R5-1.

### findings (round 5)
**R5-1 — SOURCE-POLICY RED (rule restates the base claim bar for two or more losses; compute keeps the window sum).**
- Setup: term_start 2026-09-15, processing 2026-10-20 (window k = 2), VOLUNTARY_NOT_REQUIRED.
  - L1 dated 2026-08-21 (prior term, inside the window), paid net 10,000.
  - L2 dated 2026-10-01 (current term), closed by a written denial (for example LOSS_BELOW_DEDUCTIBLE), with no payment.
- Rule (base as written): no claim with a date of loss in the current term was paid, and none is open, so the current-term risk, ICC, HFIAA and RFA are returned pro rata.
- Compute: `xc_nwin` = 2, `xc_d1` = 2026-10-01 ≥ term_start, `xc_lpaid` = 10,000 > 0, so `xc_barred` is true and nothing is returned.
- The same holds when L2's only payment was voided and not reissued.
- Members:
  - `xc_lpaid`/`xc_barred` in `cxl_current_term_return` T2 and in the out-of-scope `xc_base_ret`.
  - `xr_lpaid`/`xr_barred` in `rfd_rfa_return` T2, in the zero branches of the HFIAA and ICC returns, and in `xr_base_other`.
- This is the R4-1 class: the month window still decides the bar in the two-or-more branch.
- No task consequence: task 1 is BUILDING_SOLD, and task 0 has no cancellation.

### observations (round 5)
- O5-1: `xc_nwin`/`xr_nwin` count `nfipcom_claim_reported` rows, so one loss with a duplicate first notice counts as "two or more losses". On that world both branches give the same outcome, since the window holds only that one date of loss. It is wording-only unless a prior-term loss also falls in the window, which is R5-1.
- O4-1 and the earlier observations stand.

### closing_checklist (round 5)
Written after the reveal; see the task files.
- Both tasks' round-5 comparisons match GT figure for figure. Both PASS on all four relationships.
- Scopes are disjoint and the graph is acyclic.
- Trees: task 0 has n=1 with 1 value_input edge; task 1 has n=3 with 2. Each has one user write.
- Every factor bears weight against an honest baseline.
- R4-1 is closed in its one-loss scope. In the two-or-more-losses scope the rule restates the base claim bar but compute keeps the window sum: R5-1, charter-wide, no task consequence.
- Gates on this form: round-5 snapshot all OK, with traceability and validate pre-render only.

VERDICT revision_5: task0=PASS task1=PASS
charter=R5-1

## revision_6

### charter_global_frozen (round 6)
- Written 2026-10-16, before the round-6 GT was opened.
- Gate first: `tail -1 worklog.md` reads `REWORK round 6: gates 8/8 green`.
- Snapshot run by me (`/tmp/erl0065_coord/snapshot.sh nfip_commercial_rcbap_claims 6`). All gates are OK. Traceability misses only unlock tool names; validate_scenario still INVALID with `documents: 36` (KB side).
- Hashes:
  - Charter 21d6d8e6f08a9736 (changed; the claim-bar text and compute of both cancellation policies were re-derived, everything else was carried forward after the mechanical sweep).
  - `task_tools.py` 4a691a15c27aa962, and masked views e50bf472647915da / 36e6f20832fb72f6, all unchanged.
- The base section is byte-identical. The mechanical sweep is clean.
- R3-1, R3-3 and the R4-1 one-loss closure are not regressed.

### round-5 RED closure — R5-1 (routed as (a) exact where the DSL allows, else (b) residue stated as not priced)
- **The window logic.** Let m = MONTHS(term_start, NOW).
  - "After the band" (`within_months=m`): MONTHS(d, NOW) < m. Every such loss is dated after term_start, because any d before term_start has MONTHS(d, NOW) ≥ m.
  - "Band": MONTHS(d, NOW) = m. It straddles term_start.
  - Losses older than the band are all in the prior term.
- **(a) Exact where decidable: yes.** `xc_paidcur`/`xr_paidcur` with `held` false reproduce the base bar exactly (paid net of voids, date of loss on or after term_start) in every other case:
  - netin > 0: bar.
  - Band net = 0 and netin = 0: no bar.
  - No loss after the band and a single band loss: `d1` is that loss, so the date test is exact.
  - No loss after the band and two or more band losses: if the latest `d1` is before term_start, every band loss is prior-term, so no bar; if `d1` is on or after term_start with net > 0, bar.
  - I checked each case against base `nfipcom_msr_term_claims_paid`. R5-1's counterexample (paid prior-term L1 on 2026-08-21 plus denied current-term L2 on 2026-10-01, processed 2026-10-20) now gives nfin=1 for L2, netin = 0, band net 10,000 > 0, so `held` is true. That is residue, not a wrong bar, so R5-1 as written is closed.
- **(b) Residue — stated: yes; computed: yes; honest: no.**
  - Stated: the `held` predicate matches the sentence word for word ("no loss dated after the month band … carries such payments, a loss dated in that band does, and either a loss is reported after the band or two or more losses are reported in the band with the latest of them dated on or after the current term_start and carrying none").
  - Computed: in the residue, `barred` is false, so the schedule returns the current term. That matches "this schedule does not apply the claim bar to the cancellation".
  - Not honest: the same sentence continues "and the base claim bar governs it at the claims desk as written, that is: no refund at all is due for the current term … when a claim with a date of loss in the current term has been paid". This difficulty's agent is the policy and claims desk, it can read every date of loss against term_start, and its refund write is scored. In the residue, the rule therefore yields two conclusions (R6-1).

### findings (round 6)
**R6-1 — SOURCE-POLICY RED (the residue sentence gives two outcomes in the same situation).**
- Setup: term_start 2026-09-15, processing 2026-10-20 (m = 1), VOLUNTARY_NOT_REQUIRED, all claims closed.
  - Loss A dated 2026-09-18 (band; current term), paid net 10,000.
  - Loss B dated 2026-10-05 (after the band), closed by a written denial.
- Compute: netin = 0, band net = 10,000, nin = 1, so `held` is true, `barred` is false, and the current-term risk, ICC, HFIAA and RFA are returned pro rata.
- Same sentence, second clause: "the base claim bar governs it at the claims desk as written … no refund at all is due for the current term … when a claim with a date of loss in the current term has been paid". A is current-term and paid, so nothing of the current term is returned.
- A desk agent following the rule can do either:
  - disburse the schedule's figure (scored as gold); or
  - apply the base bar it is told governs, which is an unscored and different refund.
- Members, with the same text and compute in both policies:
  - `xc_held`/`xc_barred` (`cxl_current_term_return` T2 and `xc_base_ret`).
  - `xr_held`/`xr_barred` (`rfd_rfa_return` T2, the HFIAA and ICC zero branches, and `xr_base_other`).
- No task consequence: task 1 is BUILDING_SOLD, and task 0 has no cancellation.

### closing_checklist (round 6)
Written after the reveal; see the task files.
- Both tasks' round-6 comparisons match GT figure for figure. Both PASS on all four relationships.
- Scopes are disjoint and the graph is acyclic.
- Trees: task 0 has n=1 with 1 value_input edge; task 1 has n=3 with 2. Each has one user write.
- Every factor bears weight against an honest baseline.
- R5-1 is closed: the bar is exact wherever the records decide it.
- The residue routing is stated and computed but not honest: R6-1, charter-wide, no task consequence. The residue sentence both says the schedule does not apply the bar and says the base bar governs, and those give different refunds for a paid current-term loss in the band.
- Gates on this form: round-6 snapshot all OK, with traceability and validate pre-render only.

VERDICT revision_6: task0=PASS task1=PASS
charter=R6-1

## revision_7

### charter_global_frozen (round 7)
- Written 2026-10-16, before the round-7 GT was opened.
- Gate first: `tail -1 worklog.md` reads `REWORK round 7: gates 8/8 green`.
- Snapshot run by me (`/tmp/erl0065_coord/snapshot.sh nfip_commercial_rcbap_claims 7`). All gates are OK. Traceability misses only unlock tool names; validate_scenario INVALID with `documents: 104` (KB side).
- Hashes:
  - Charter a957a25921e1dac7 (changed; charter-wide sections re-derived, including the new read-sweep bindings).
  - `task_tools.py` 4a691a15c27aa962, and masked views e50bf472647915da / 36e6f20832fb72f6, all unchanged.
- The base section is byte-identical. The mechanical sweep is clean.
- Factor counts and edges are unchanged.
- New bindings checked:
  - `*_gov_type`: the governing report is also filtered by report type, which guards against two reports on the same date.
  - `*_del_eff`/`*_add_eff`/`*_deleted`: a BizFlood location deleted on or before the date of loss, and not re-added, leaves the BizFlood policy uncounted. The rule states this.
  - `xr_refd`: the premium received but not owed is reduced by refunds already disbursed beyond the non-cancellation credits. The rule states this.
  - All three match their rule sentences.

### round-6 RED closure — R6-1 (routed: residue held at zero as a declared scoped departure)
- **Stated: yes.**
  - The credit's claim-bar overwrite is self-scoped ("For the risk premium credit of a cancellation processed under this rule, and only for it, the cancellation refund's credits following the cancellation refund rule"). The refund's overwrite is scoped to "the ICC premium, Reserve Fund Assessment and HFIAA surcharge credits … for the current term, and only for those credits". Each sibling names the other's case.
  - The residue now has one outcome: "this schedule holds the current term's return: nothing of the current term is returned … which departs from the base claim bar for that case only".
  - The `cxl_current_term_return` T2 and `rfd_rfa_return` T2 ladders carry the hold.
- **Computed: yes.**
  - `held` = netin ≤ 0 and band net > 0 and not (`dpband` and (dp < term_start or net(dp) > 0)), where dp is the latest date of loss that carries a claim_paid row. That is word for word the rule's "the latest loss on which a claim payment was ever issued is dated after the band, or is dated in the band on or after the current term_start with its payments all voided".
  - `barred` = reason ∈ claim_bar_reasons and (`paidcur` or `held`). It feeds the zero branches of the risk, ICC, HFIAA and RFA returns and both base fallbacks.
  - Outside the residue the bar is exact: dp in the band before term_start puts every paid band loss in the prior term; dp in the band on or after term_start with a net payment puts a paid loss in the current term.
- **Honest: yes, as a declared, narrow departure.**
  - "the records cannot place" is defined by its own "that is when …" clause.
  - The residue needs a later loss whose payments were all voided. Where the band's paid loss is in fact current-term, the hold equals the base outcome. Where it is in fact prior-term, the hold returns less than base, and this is declared.
- **R6-1 closed.**

### findings (round 7)
**R7-1 — SOURCE-FACTOR RED (second-record member of the R2-3b class, missed in my revision_3/4 closure: "in force" read from the latest of each kind before the date filter).**
- Rules and compute (bpay_other_cover, cpay_other_cover, cpol_value_ceiling): "the value endorsement in force being, of the latest value increase and the latest value decrease endorsed for the location, the one that took effect later among those that took effect on or before the date of loss".
  - `*_inc_ok = n_inc > 0 and DAYS(latest_inc_eff, dol) >= 0` (same for decreases).
- World: SOV contents 150,000; VALUE_INCREASE A effective before the date of loss (contents 250,000); VALUE_INCREASE B effective after the date of loss (contents 300,000).
  - The latest increase is B, and it fails the date test. There is no decrease, so "no value endorsement in force" and the contents ceiling and other contents insurance read 150,000.
  - The limit actually in force on the date of loss is A's 250,000.
  - The mirror case also exists: a decrease in force before the date of loss, hidden behind a later decrease after it.
- Same class, same shape: "the named insured's BizFlood policy whose latest statement of values scheduled the building's address, counted only when it was in force on the date of loss" (`*_bz`/`bp_bz_pid` by latest SOV). If a second BizFlood policy schedules the address after the loss, the policy that was in force is dropped and the NFIP pays as if there were no other insurance.
- Members: `pb_inc_ok`/`pb_dec_ok`/`pb_chg_*`; `cy_inc_ok`/`cy_dec_ok`/`cy_chg_*`; `cp_inc_ok`/`cp_dec_ok`/`cp_chg_*`; `bp_bz_pid`, `pb_bz`, `cy_bz`, `cp_bz`.
- No task world has a second value endorsement or a second BizFlood policy, so there is no task consequence.
- I record that revision_3 declared R2-3(b) closed without catching this second-record member.

### observations (round 7)
- O7-1: The held residue (current term returned as zero where the band's paid loss is in fact prior-term) is a declared WYO departure from the FEMA claim-paid bar. It is narrow, since it needs a later all-voided payment.

### closing_checklist (round 7)
Written after the reveal; see the task files.
- Both tasks' round-7 comparisons match GT figure for figure. Both PASS on all four relationships.
- Scopes are disjoint and the graph is acyclic.
- Trees: task 0 has n=1 with 1 value_input edge; task 1 has n=3 with 2. Each has one user write.
- Every factor bears weight against an honest baseline.
- R6-1 closed: the held residue gives one stated and computed outcome and is a declared, scoped departure.
- Open: R7-1, the second-record member of the "in force on the date of loss" reads, plus the latest-SOV BizFlood-policy selection. Charter-wide, no task consequence.
- Gates on this form: round-7 snapshot all OK, with traceability and validate pre-render or KB-side only.

VERDICT revision_7: task0=PASS task1=PASS
charter=R7-1

## revision_8

### charter_global_frozen (round 8)
- Written 2026-10-16, before the round-8 GT was opened.
- Gate first: `tail -1 worklog.md` reads `REWORK round 8: gates 8/8 green`.
- Snapshot run by me (`/tmp/erl0065_coord/snapshot.sh nfip_commercial_rcbap_claims 8`). All gates are OK. Traceability misses only unlock tool names; validate_scenario INVALID with `documents: 104` (KB side).
- Hashes:
  - Charter 10484d393a21648d (changed; re-derived).
  - `task_tools.py` 4a691a15c27aa962, and masked views e50bf472647915da / 36e6f20832fb72f6, all unchanged.
- The base section is byte-identical. The mechanical sweep is clean.
- Edges and factor counts are unchanged.
- R6-1 (held residue), R3-3 (endorsement/re-rate scope) and R3-1 are not regressed.
- The refund's assembly sentence is now generic ("adds up every CANCELLATION credit referencing the signed request … and the premium received but not owed"), which improves on O2-1.

### round-7 RED closure — R7-1 and the second-record class (worklog table, read by read)
**Route (a), exact identifying filter.** Stated, computed and honest, so closed:
- Governing report: claim number + report type + event date.
- First notices: other claim numbers only.
- BizFlood adjuster value: policy + location + date of loss, latest report.
- Refund request: the request the risk CANCELLATION credit references; reason from the cancelled policy.
- BizFlood in-force dates and parameters: by policy id.
- Proofs of loss, payments and voids: aggregates or "latest" as each rule defines them.
- Term ledgers: filtered by term.

**Route (b), single-record case exact with the multi-record case defined in words.** Stated: yes. Computed: no. Honest: no.
- The four claim rules now say: "These readings by the latest record of a kind are exact where the named insured's BizFlood records … hold one statement of values, at most one value increase, at most one value decrease, at most one location deletion and at most one location re-adding; where they hold more, the BizFlood policy, its statement of values, the location's standing on it and the value endorsement … are instead the ones in force for the location on the date of loss, read from all of those records together."
- The compute carries no count guard and no in-force computation: `*_bz`, `*_inc_ok`, `*_dec_ok`, `*_chg_*`, `*_deleted` are unchanged latest-of-kind reads. In the multi-record case the rule therefore defines one value and the compute scores another.
- The worklog's own wording, "compute not priced there", appears nowhere in the rule. A reader is told the in-force value; the scorer uses latest-of-kind.
- The credit's request reading has the same shape: "the signed request being processed when it carries more" versus `xc_reason`/`xc_req_date`/`xc_received` = the latest SIGNED request by created_at. Which request is "being processed" is chosen by the agent's tool argument, not by the latest-created rule.
- **R7-1 is therefore not closed.** The realism gap became a rule/compute gap (R8-1).

### findings (round 8)
**R8-1 — SOURCE-POLICY RED (multi-record case stated in the rule, not computed).**
- Example (R7-1's world): BizFlood SOV contents 150,000; VALUE_INCREASE A effective before the loss (250,000); VALUE_INCREASE B effective after it (300,000).
  - Rule ("where they hold more … the value endorsement … in force for the location on the date of loss"): A, 250,000.
  - Compute (`cp_inc_ok` false, since the latest increase B is after the loss): SOV 150,000.
  - Both the contents ceiling and the other contents insurance take different values.
- Remaining members, one list:
  - BizFlood policy and SOV selection: `bp_bz_pid`, `bp_bz_loc`, `bp_sov_value`, `bp_bz_in`; `pb_bz`, `pb_loc`, `pb_n_sched`, `pb_sov_value`, `pb_bz_bldg`, `pb_bz_cont`; `cy_bz`, `cy_loc`, `cy_sov_cont`, `cy_bz_bldg`, `cy_bz_cont`; `cp_bz`, `cp_sov_cont`, `cp_bz_in`.
  - Value endorsements: `pb_inc_*`, `pb_dec_*`, `pb_chg_*`; `cy_inc_*`, `cy_dec_*`, `cy_chg_*`; `cp_inc_*`, `cp_dec_*`, `cp_chg_*`.
  - Location deletion and re-adding: `bp_`, `pb_`, `cy_`, `cp_` `_del_eff`, `_add_eff`, `_deleted`.
  - Credit's signed request: `xc_reason`, `xc_req_date`, `xc_received` ("the signed request being processed" vs the latest signed request).
- No task world holds a second record of any of these kinds, so there is no task consequence.

### closing_checklist (round 8)
Written after the reveal; see the task files.
- Both tasks' round-8 comparisons match GT figure for figure. Both PASS on all four relationships.
- Scopes are disjoint and the graph is acyclic.
- Trees: task 0 has n=1 with 1 value_input edge; task 1 has n=3 with 2. Each has one user write.
- Every factor bears weight against an honest baseline.
- The second-record class is closed for its route-(a) members.
- The route-(b) members are stated but not computed (R8-1). R7-1 is carried into R8-1. Charter-wide, no task consequence.
- Gates on this form: round-8 snapshot all OK, with traceability and validate pre-render or KB-side only.

VERDICT revision_8: task0=PASS task1=PASS
charter=R8-1

## revision_9

### charter_global_frozen (round 9)
- Written 2026-10-16, before the round-9 GT was opened.
- Gate first: `tail -1 worklog.md` reads `REWORK round 9: gates 8/8 green`.
- Snapshot run by me (`/tmp/erl0065_coord/snapshot.sh nfip_commercial_rcbap_claims 9`). All gates are OK. Traceability misses only unlock tool names; validate_scenario INVALID with `documents: 104` (KB side).
- Hashes:
  - Charter f69da5e2fe82f536 (changed; re-derived).
  - `task_tools.py` 4a691a15c27aa962, and masked views e50bf472647915da / 36e6f20832fb72f6, all unchanged.
- The base section is byte-identical. The mechanical sweep is clean.
- Edges and factor counts are unchanged.
- R6-1, R3-3, R3-1 and the route-(a) members of round 8 are not regressed.

### round-8 RED closure — R8-1 (words-only route withdrawn; members re-keyed exactly). Rule==compute and realism, per member
- **BizFlood policy selection** (`bp_bz_pid`, `pb_bz`, `cy_bz`, `cp_bz` = XLATEST policy id of the `bizflood_adjuster_report` rows with date_of_loss = the claim's date of loss).
  - Rule==compute: yes ("the named insured's BizFlood policy on which the latest BizFlood adjuster report for the date of loss was filed, counted only when it was in force on the date of loss …").
  - Realism: no (R9-1).
- **Location** (`*_loc`, the SOV location number for the address on that policy) and the **adjuster value** (policy + location + date of loss, latest report).
  - Rule==compute: yes. Realism: yes.
- **Deletion and re-adding reads:** dropped from rule and compute together. Rule==compute: yes.
- **Statement of values and value endorsements:** count-scoped (`*_one`: every BizFlood adjuster report for the date of loss is on that one policy, at most one SOV for the address, and, for the payments and the ceiling, at most one value increase and at most one value decrease).
  - Inside the scope, latest-of-kind is exact: a single increase or decrease is either in force on the date of loss or not.
  - Outside it, rule and compute both give nil: "no … is issued/worked out under this rule, the amount being nil, and the claim is referred to the adjuster to apportion the other insurance" (`result … if *_one else 0`; the tools take positive amounts, so nothing is written).
  - Rule==compute: yes.
  - Realism: referral to the adjuster when several other-insurance records must be reconciled is plausible. The R7-1 world now yields nil and a referral, not a wrong figure.
  - Observation: the count reads `bizflood_adjuster_report` rows for the date of loss across all the customer's BizFlood policies. A report on a different address's BizFlood policy for the same flood also takes the claim out of scope, so it is referred. Conservative; no wrong amount.
- **Credit's signed request:** the rule now states what compute reads ("the latest signed cancellation request received on the policy", withdrawn and unsigned not counting). Rule==compute: yes. Realism: acceptable.
- **R8-1 closed:** no rule now defines a value the compute does not produce.

### findings (round 9)
**R9-1 — SOURCE-FACTOR RED (other insurance keyed on the other insurer's adjuster having reported, not on the other policy covering the loss).**
- With the BizFlood policy chosen only through a `bizflood_adjuster_report` for the date of loss, an in-force, non-excess BizFlood policy that schedules the building's address but has no adjuster report yet (claim reported, not yet adjusted; or no claim filed with it) counts as no other insurance in all four claim policies.
- The SFIP other-insurance condition the rule itself cites applies when "a loss covered by this policy is also covered by other insurance", whether or not the other insurer has adjusted it.
- Example: GPF Non-Residential Building in zone AE, building limit 500,000; BizFlood Building and Contents in force, SOV building value 1,000,000, flat deductible 25,000; BizFlood claim reported, no adjuster report; sworn building amount 100,000, no contents.
  - Rule and compute: no BizFlood policy is meant, so the layer is the building limit + contents limit, the whole 100,000 is carried alone, and the payment is 100,000.
  - The cited condition: primary up to 25,000, then 75,000 × 500,000/1,500,000 = 25,000, a payment of 50,000.
- The same keying drops the SOV value basis of the building proof (tier 2) and the contents ceiling and other-cover tiers whenever no adjuster report exists.
- Members, one list:
  - `bp_bz_pid` (and through it `bp_bz_in`, `bp_sov_value`);
  - `pb_bz` (`pb_bz_primary`, `pb_n_sched`, `pb_bz_bldg`, `pb_bz_cont`, `pb_layer`, `pb_cont`, `pb_other`);
  - `cy_bz` (`cy_bz_ok`, `cy_layer`, `cy_bldg`, `cy_other`);
  - `cp_bz` (`cp_bz_in`, `cp_sov_cont`, `cp_ceiling`).
- Related member, present since round 2 and not flagged by me before: the V/VE layer tier requires the BizFlood adjuster's measured location value, so with no measurement the rule falls through to "no other flood policy's deductible applies … the whole sworn building amount is carried alone" even though the BizFlood policy is in force (`pb_layer`/`cy_layer` fall-through).
- No task world lacks the BizFlood adjuster report (both have FINAL reports for 2026-08-27 on the in-force policy), so there is no task consequence.

### closing_checklist (round 9)
Written after the reveal; see the task files.
- Both tasks' round-9 comparisons match GT figure for figure. Both PASS on all four relationships.
- Scopes are disjoint and the graph is acyclic.
- Trees: task 0 has n=1 with 1 value_input edge; task 1 has n=3 with 2. Each has one user write.
- Every factor bears weight against an honest baseline.
- R8-1 is closed: rule==compute for every re-keyed or count-scoped member, with the nil-and-refer outcome stated and computed.
- Open: R9-1. The re-keying ties the existence of other insurance to the BizFlood adjuster having reported, and the V/VE layer tier has fallen through without a measurement since round 2. Charter-wide, no task consequence.
- Gates on this form: round-9 snapshot all OK, with traceability and validate pre-render or KB-side only.

VERDICT revision_9: task0=PASS task1=PASS
charter=R9-1

## revision_10

### charter_global_frozen (round 10)
- Written 2026-10-17, before the round-10 GT was opened.
- Gate first: `tail -1 worklog.md` reads `REWORK round 10: gates 8/8 green`.
- Snapshot run by me (`/tmp/erl0065_coord/snapshot.sh nfip_commercial_rcbap_claims 10`). All gates are OK. Traceability misses only unlock tool names; validate_scenario INVALID with `documents: 104` (KB side).
- Hashes:
  - Charter 2976f9723a1818f5 (changed; re-derived).
  - `task_tools.py` 4a691a15c27aa962, and masked views e50bf472647915da / 36e6f20832fb72f6, all unchanged.
- The base section is byte-identical. The mechanical sweep is clean.
- Factor counts and edges are unchanged.
- R6-1, R3-3, R3-1, R8-1 (rule==compute; nil-and-refer scope) and the round-8 route-(a) members are not regressed.

### round-9 RED closure — R9-1
- **BizFlood policy:** re-keyed to the statement of values for the address (`*_bz`/`bp_bz_pid` = latest SOV `bizflood_policy_id` for `location_address`).
  - No adjuster report is needed.
  - "In force on the date of loss" is now defined in the rule ("on or after its effective date, before its term end and before any cancellation effective date it carries") and computed by policy id with DAYS tests on `effective_date`, `term_end` and `cancellation_effective_date`.
  - Rule==compute: yes. Realism: yes. The SFIP other-insurance condition now applies whenever an in-force BizFlood policy schedules the address.
  - R9-1's example (zone AE, no BizFlood report) now gives the flat 25,000 deductible plus pro rata: payment 50,000 rather than 100,000.
- **V/VE layer:** the location value is "the one on that policy's adjuster's latest report for the location and the date of loss and, when its adjuster has filed no report for them, the building and contents values its statement of values schedules for the location added together" (`pb_lv`/`cy_lv`).
  - The fall-through without a measurement is gone.
  - Rule==compute: yes, given non-null values.
  - Realism: the declared values are a reasonable stand-in for the location value until the loss is adjusted.
- **Scope:** "the named insured's BizFlood statements of values schedule the building's address at most once", plus at most one value increase and one value decrease, applied across all BizFlood policies, with nil and referral otherwise.
  - Rule==compute: yes.
  - Realism: conservative. A renewal-time SOV re-filing would also be referred (O10-2).
- **R9-1 closed;** the class sweep found no remaining member.

### findings (round 10)
None.

### observations (round 10)
- O10-1: `pb_lv`/`cy_lv` return 0 when `pb_bz_cont`/`cy_bz_cont` is null (e.g. a BizFlood Building-tier SOV row storing no contents value). The rule then reads "building and contents values … added together" as the building value alone, while compute uses the V-zone minimum only. The two diverge only if such a row stores null rather than 0. Not reached by either world (both tasks have a BizFlood adjuster report).
- O10-2: the one-SOV scope counts every SOV row for the address across policies, so a second SOV filed at renewal sends the claim to referral. Conservative; no wrong amount.
- Earlier observations (O2-x, O3-1, O4-1, O5-1, O7-1) stand.

### closing_checklist (round 10)
Written after the reveal; see the task files.
- Both tasks' round-10 comparisons match GT figure for figure. Both PASS on all four relationships.
- Scopes are disjoint and the graph is acyclic.
- Trees: task 0 has n=1 with 1 value_input edge; task 1 has n=3 with 2. Each has one user write.
- Every factor bears weight against an honest baseline, and every all-baseline figure is definite and differs from gold.
- Every round-1 to round-9 RED is closed:
  - CG-1 to CG-10 (round 2);
  - R2-1, R2-2, R2-4 (round 3);
  - R3-1, R3-3 (round 4);
  - R3-2 → R4-1 → R5-1 → R6-1 (round 7);
  - R7-1 → R8-1 (round 9);
  - R9-1 (round 10).
  - The CG-7c withdrawal is recorded in revision_2.
- Remaining items are observations only (O10-1, O10-2 and earlier).
- Gates on this form: round-10 snapshot all OK; traceability misses only unlock tool names, and validate_scenario's INVALID is on the KB side.

VERDICT revision_10: task0=PASS task1=PASS
charter=CLEAN

## revision_11

### charter_global_frozen (round 11)
- Written 2026-10-17, before the round-11 GT was opened.
- Gate first: `tail -1 worklog.md` reads `REWORK round 11: gates 8/8 green`.
- Snapshot run by me (`/tmp/erl0065_coord/snapshot.sh nfip_commercial_rcbap_claims 11`). All gates are OK. Traceability misses only unlock tool names; validate_scenario INVALID with `documents: 214` (KB side).
- Hashes:
  - Charter 1c045a18898dea0a (changed; re-derived).
  - `task_tools.py` 4a691a15c27aa962, and masked views e50bf472647915da / 36e6f20832fb72f6, all unchanged.
- The base section is byte-identical. The mechanical sweep is clean.
- Scratch class checker over all six policies:
  - no binding is owned by two factors;
  - no factor binding reads another factor's binding;
  - plain bindings used by exactly one factor: `pb_cn`, `cy_cn`, `xc_cur`, `xc_endo_term`. Each is a quantity its policy's baseline names (the claim the payment is issued on; the current term's risk premium; endorsement charges returned with their term premium), so none is a factor definition outside its factor.
- Factor counts: `cxl_endorsement_return` now has 4 tiers and `rfd_rfa_return` has 5. All others are unchanged.
- Earlier verdicts (CG-1 to CG-10, R2-x to R9-1) are not regressed.

### renderer findings render_r1 — closure, item by item (with class)
1. **Factor reads factor.** `pb_other` now reads the shared plain `pb_bz_bldg`/`pb_bz_primary` and no longer reads `pb_n_sched`. The checker finds no cross read anywhere in the charter. **Closed.**
2. **Claim bar vs endorsement return.**
   - `xc_endo_ret = 0 if (xc_in_cur and xc_barred) else …`. The rule's endorsement sentence and `cxl_endorsement_return` T1 ("…on or after the current term_start and the claim bar set out above applies, nothing is returned") match.
   - `xc_barred` is a plain binding shared by the current-term and endorsement factors, so neither factor is gated through the other.
   - Under the bar: `xc_cur_ret` = 0, `xc_prev_ret` = 0 (current-term cancellation) and `xc_endo_ret` = 0, so the result is MX(0, −re-rate) = 0.
   - The refund already zeroes the RFA under the bar, so both sides now agree. **Closed.**
3. **"In full" vs re-rate netting.** The rule now reads "the Reserve Fund Assessment charges of a term that began after the cancellation took effect are returned in full, less the re-rate credits booked on them", which matches `RND(xr_r_cur - xr_rc_cur, 2)`. **Closed.**
4. **Same-day increase/decrease tie.** The rule reads "an increase and a decrease taking effect the same day being settled by the one recorded later, and by the increase when both were recorded the same day" (in all 3 value-endorsement rules and their ladders). Compute adds `*_inc_rec`/`*_dec_rec` and DAYS(dec_eff, inc_eff) > 0 or (= 0 and DAYS(dec_rec, inc_rec) ≥ 0), in `pb_chg_lim`, `cp_chg_cont` and `cy_chg_cont`. **Closed.**
5. **Single-factor definitions outside their factor.**
   - `bp_bz_pid`, `bp_bz_loc` and `bp_one` are in `bpol_value_basis`. `cp_bz`, its in-force bindings and `cp_one` are in `cpol_value_ceiling`.
   - The proofs' scope is now a tier condition (more than one SOV, or for the ceiling more than one value increase or decrease, falls through to the policy's RCV or contents limit). Both results are the plain assembly.
   - The duplicates `pb_sov_value`/`cy_sov_cont` are merged into the shared `pb_bz_bldg`/`cy_bz_cont`.
   - `xc_prev`/`xr_eff_end` moved into their only factors.
   - Neither proof's plain bindings nor any baseline names BizFlood.
   - The payments' BizFlood bindings and `pb_one`/`cy_one` stay plain because each is shared by several factors and the result, not a single-factor definition.
   - **Closed; no remaining member.**
- **Non-blocking items:**
  - Endorsement or certificate effective after the cancellation date: `xr_endo_part`/`xr_rr_part` return the charge or credit in full ("or in full when … took effect after the cancellation effective date").
  - Prior-term RFA: a cancellation before term_start with no endorsement or re-rate in its term now has a tier that returns the current term in full less re-rate credits and the prior term pro rata, or in full less re-rate when on or before its start. This matches ICC and HFIAA.
  - Zero risk credit: `xr_req_id` falls back to the latest signed request, and the rule states it.
  - All three are stated, computed and realistic. **Closed.**

### findings (round 11)
None.

### observations (round 11)
- O11-1: with two or more SOVs for the address, the proofs now fall through to the policy's RCV and contents limit, ignoring a BizFlood adjuster's measured value. This is conservative: no penalty base is raised, and the ceiling is not lowered. The payments still refer the claim (nil).
- O10-1 and O10-2 and the earlier observations stand.

### closing_checklist (round 11)
Written after the reveal; see the task files.
- Both tasks' round-11 comparisons match GT figure for figure. Both PASS on all four relationships.
- Scopes are disjoint and the graph is acyclic.
- Trees: task 0 has n=1 with 1 value_input edge; task 1 has n=3 with 2. Each has one user write.
- Every factor bears weight against an honest baseline.
- render_r1 items 1–5 and the three non-blocking items are closed with their classes; the class checker finds no remaining member.
- No regression of earlier verdicts.
- Gates on this form: round-11 snapshot all OK; traceability misses only unlock tool names, and validate_scenario's INVALID is on the KB side.

VERDICT revision_11: task0=PASS task1=PASS
charter=CLEAN

## revision_12

### charter_global_frozen (round 12)
- Written 2026-10-17, before the round-12 GT was opened.
- Gate first: `tail -1 worklog.md` reads `REWORK round 12: gates 8/8 green`.
- Snapshot run by me (`/tmp/erl0065_coord/snapshot.sh nfip_commercial_rcbap_claims 12`): all gates OK, including **TRACEABILITY OK** and **validate_scenario VALID** (353 documents).
- Hashes:
  - Charter bdbbf680ba36b4b3 (changed; the refund overwrites and assembly sentence were re-derived; everything else was carried forward after the mechanical sweep and the class checker).
  - `task_tools.py` 4a691a15c27aa962, and masked views e50bf472647915da / 36e6f20832fb72f6, all unchanged.
- The base section is byte-identical.
- Mechanical sweep and class checker are clean: no cross reads, no binding with two owners.
- Factor counts are unchanged.
- Scope this round: the source side of kb-1 and src-1 of `audits/policy_kb/nfip_commercial_rcbap_claims/kb_audit_report.md`, plus regression. src-2 is out of scope (coordinator stop rule).

### kb-1 (source side) — closed
- The KB stated two retired base semantics as live: "The Federal Policy Fee and probation surcharge do not come back on a pro rata or current-term refund" and "The components a current-term-full or pro rata refund can return are the risk premium, ICC premium, Reserve Fund Assessment and HFIAA surcharge".
- On the source side both base sentences are now declared overwrites, each with a self-scoped replaced_by:
  - Refund overwrite 3 supersedes "Under CURRENT_TERM_FULL and PRO_RATA the Federal Policy Fee and probation surcharge are fully earned (fees_refundable_on_pro_rata is false)". The replacement reads: "For a cancellation refund whose current term and the term before it together carry at most one premium-bearing endorsement and at most one re-rate credit … and only for such a refund, the Federal Policy Fee and probation surcharge of a term that began after the cancellation took effect are returned in full …; for a cancellation refund whose terms carry more than one … and for every other Federal Policy Fee and probation surcharge, the base clause stands: …", restating the base sentence verbatim.
  - The four-component restriction is the PRO_RATA/CURRENT_TERM_FULL sentence superseded by refund overwrite 2 (and credit overwrite 1), with the base text restated for the multi-record case.
- The parameter sentences (`fees_refundable_on_pro_rata`, `refundable_components_partial`) are therefore covered by declared, scoped overwrites the KB can mark retired.
- What remains is KB-side and outside this audit.

### src-1 — closed
- The three refund overwrites now exclude each other by name:
  - Overwrite 1 (booking and total): "plus, for a cancellation refund whose current term and the term before it together carry at most one premium-bearing endorsement and at most one re-rate credit …, the premium received but not owed …, while a cancellation refund whose terms carry more than one … is the total of its credits alone".
  - Overwrite 3 (fees): scoped the same way.
  - Overwrite 2: names its multi-record branch as "the case the premium-received and fee sentences of this rule leave to the base clause".
- The assembly sentence adds the premium received but not owed only "where the booking sentence above adds it".
- Compute: `result = (xr_risk + xr_icc + xr_rfa + xr_hfiaa + xr_fpf + xr_prob + xr_excess) if xr_scope else (xr_risk + xr_base_other)`, with `xr_scope = xr_n_endo2 <= 1 and xr_n_rr2 <= 1`. `xr_base_other` returns fees only from inception, which matches the base clause.
- Rule==compute on both branches.
- Charter-wide, the credit's two overwrites already exclude each other and match its compute. No other unconditional-versus-scoped overwrite pair was found.

### findings (round 12)
None.

### closing_checklist (round 12)
Written after the reveal; see the task files.
- Both tasks' round-12 comparisons match GT figure for figure. Both PASS on all four relationships.
- Scopes are disjoint and the graph is acyclic.
- Trees: task 0 has n=1 with 1 value_input edge; task 1 has n=3 with 2. Each has one user write.
- Every factor bears weight against an honest baseline.
- The source side of kb-1 and src-1 are closed. src-2 is out of scope by coordinator rule.
- No regression of earlier verdicts.
- Gates on this form: round-12 snapshot all OK, including TRACEABILITY OK and validate_scenario VALID.

VERDICT revision_12: task0=PASS task1=PASS
charter=CLEAN
