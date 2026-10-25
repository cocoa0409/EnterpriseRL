# Policy-task audit — gap_waiver_cancellations_and_claims / charter-global

## revision_1

## charter_global_frozen
- Frozen 2026-10-19T23:56Z (before any task GT was revealed), auditor: independent policy-task auditor (erl-task-policy-audit), scratch /tmp/audit_gap_0072/.
- Inputs and hashes (verified equal to the brief):
  - `tasks/gap_waiver_cancellations_and_claims/gap.extended.yaml` sha256 065279ae96178dd95309eb60fbdc95b2b2a5521f22576ccbceaaceca1e90247f
  - `tasks/gap_waiver_cancellations_and_claims/task_tools.py` sha256 ff36c895329e68f37eac5e19541ae2c04f7b3347150db626c7ab73ecc24a6af4
  - masked views `.audit_views/policy/gap_waiver_cancellations_and_claims/r1/0.json` 9cf1e3b2…c3e3, `1.json` 967070e6…2b00 (frozen_time, user_scenario, initial_state only).
- Read: blueprint.yaml, db_schema.json, share_tools.py, products/gap.yaml (+ contract.yaml, cpi.yaml, vsc.yaml for the cross-category pricing checks), the extended charter, task_tools.py, `audits/render_source/XF_recipe.md`, the DSL evaluator `skills/erl-task-instantiate/scripts/check_compute.py` (semantics of LATEST/XLATEST/CFIELD/CPARAM/MONTHS/DAYS/RND/within_months).
- Masked / not read before every task's derivation was frozen: tasks/*.json, plan.md, worklog.md (both), every evaluation_criteria / computations / charter_scope / required_documents / design_rationale / solvability_contract / prerequisite_closure field, other audits. Nothing below is derived from GT.
- Entry conditions: gate snapshot supplied with the brief (EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK (--check), SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK; traceability deferred to post-render). Masked views and hashes supplied. Entry conditions met; gates not re-run by this auditor.

### policy_conflict_scan
Base section lines 1-743 are byte-identical to `blueprint/products/gap.yaml` (`diff` clean; YAML-equal on every key). Six extended policies, all `subject: [gap_claim_opened]`, `trigger: on_request`, each writing one field of the reported claim row (`gap_activities`, event_type `gap_claim_filed`) through its own tool:

| policy | computes | tool (owner) | scope |
| --- | --- | --- | --- |
| gap_ext_premier_deductible_reimbursement (pd) | deductible_covered_usd | claim_premier_deductible_reimbursement_7815b2b6 (user) | Premier 150 |
| gap_ext_claim_starting_balance (bl) | balance_at_loss_usd | record_claim_balance_at_loss_15fb7d99 (agent) | Plus 150 + Premier 150 |
| gap_ext_premier_excluded_amounts (ep) | excluded_amounts_usd | record_premier_claim_exclusions_258c7293 (agent) | Premier 150, salvage taken/none, no prior-damage deduction |
| gap_ext_claim_worksheet_benefit (bn) | benefit_usd | record_claim_worksheet_benefit_931d4ebc (agent) | Premier 150 |
| gap_ext_plus_deductible_reimbursement (ud) | deductible_covered_usd | claim_plus_deductible_reimbursement_49e3d00f (user) | Plus 150 |
| gap_ext_plus_excluded_amounts (eu) | excluded_amounts_usd | record_plus_claim_exclusions_41771560 (agent) | Plus 150, salvage taken/none, no prior-damage deduction |

- Overlapping subjects: pd/ud and ep/eu compute the same field on disjoint plans; each sibling's rule names its own plan and excludes the sibling's plan by name (XF-20 satisfied). bl spans Plus+Premier but is the only writer of balance_at_loss_usd. No two policies reach different conclusions on one quantity for one plan.
- Triggers / terminal states: no tool writes an event with base `triggers` (tools `ctx.update` one field of an existing claim row; no gap_claim_decided / refund / cancellation row) — XF-26 clean. Terminal state of every policy = one field of the claim row; addendum status stays claim_open.
- Cross-category reads (contract, cpi, vsc) are read-only; scoped by `contract_id=F('contract_id')` and the customer.
- Task scopes (from the charter's own tree shape, to be confirmed at reveal): one tree rooted at bn (bn <- bl, bn <- ep <- pd) for a Premier claim and one rooted at eu (eu <- ud) for a Plus claim; the two trees share no policy and together cover all six extended policies.

### rule_compute_equivalence
- Every `compute_basis` quotation of all six policies was swept against its own rule (whitespace-normalised): 0 non-verbatim quotes, 0 compute bindings without a basis (XF-16 clean). Every `baseline.rule` is verbatim in its rule. Every `overwrite.replaced_by` is verbatim in its rule; every `superseded_clause` is verbatim in the cited base rule.
- Ladders: every `factors[].ladder` tier is a rule sentence and a branch of its `decides` binding, and every branch is a stated tier (checked per factor below).
- Edge inputs (XF-11/12), on the DSL as implemented in check_compute.py: `pd_unpaid/ud_unpaid/ep_unpaid/eu_unpaid/ac_unpaid` = 0 when next due is after the loss (rule: "none when the next due date is after the date of loss"); `ep_late_days` negative -> fall-through 100 % on a 0.00 part (harmless); `em_left` floored at 0 ("never below none"); `bl_std_count` 0 before the first payment; `pd_over` 0 with no CPI plan (rule silent — absent-record case lands on "not at all", observation); CFIELD('vsc', …) is first-match per contract (one service contract per contract in both worlds); XLATEST same-day ties keep the first row (no same-day ties among the rows read); `within_months=12` in ep/eu_returns is anchored at frozen_time — rule says "within the last 12 whole months" (anchor not stated; see observation O6).
- Rounding (XF-14): RND placement matches each rule's rounding sentence in all six policies (pd: after cap; bl: level installment, opening principal, final; ep/eu: VSC parts and final sum; bn: final only). RND is Python `round` (half-even on binary floats); no exact half-cent tie arises in either world (checked with Decimal half-up).
- Month counts (XF-13): every "whole months … plus one" sentence matches `MONTHS(a,b)+1` (day-of-month decrement), every "whole months from the enrollment date" matches `MONTHS(enrollment_date, loss)`.
- One genuine second reading found (bl, SCRA schedules' starting principal) — finding C8.

### action_binding_and_uuids
- Six `(target_tool, computes)` pairs, each claimed by exactly one policy.
- uuid8s 7815b2b6, 15fb7d99, 258c7293, 931d4ebc, 49e3d00f, 41771560: distinct, no shared prefix/suffix, no sequence — independently generated.
- No factor id is a substring of any tool name (XF-7 clean). No tool docstring names another tool or carries before/after/first; `record_claim_worksheet_benefit_931d4ebc` says "ahead of any claim decision" (observation O1 — no decision tool exists in this difficulty or in share_tools).
- Tool bodies validate nothing (each is a bare `ctx.update` of one field) — the tool layer judges no prerequisite.
- No concrete example values in docstrings (XF-28 clean). `claim_*_deductible_reimbursement` docstrings say the borrower is "submitting the primary insurer's settlement documents" — the body records only the amount (observation O10).

### prerequisite_graph
- `prerequisite` filled on all six (pd [], bl [], ud [] ; ep -> pd; bn -> bl, bn -> ep; eu -> ud). Every `problem` is an extended policy id of this file, none is a base policy or itself. Graph pd -> ep -> bn <- bl, ud -> eu: acyclic.
- Each `policy_source` is verbatim in its own (blocked) rule; `gate` names an existing compute binding (ep_covered, bn_balance, bn_excluded, eu_covered); `kind: value_input` and the gate binding enters that policy's result in every case.
- `form`: state for ep<-pd, bn<-bl, eu<-ud; action for bn<-ep with a `fallback_reason`.
- `resolved_by` = the depended-on policy's target_tool in all four edges; each write changes the gate binding (`effect` holds).
- No authoring-viewpoint wording in any `prerequisite` field.

### prerequisite_sentences
| edge | sentence (own rule) | form test | resolving write (single reading) |
| --- | --- | --- | --- |
| ep <- pd | "The Premier excluded total is fixed only after the claim, when its primary deductible is above 0.00, shows a deductible covered above 0.00." | ordering connective "only after"; record-visible state (claim's deductible covered > 0.00); no tool/id | the only rule that sets a deductible covered on a Premier claim is pd ("On a GAP Waiver Premier 150 claim the deductible covered is the Premier deductible reimbursement set here"). The Plus tool writes the same field but its rule and docstring are confined to Plus 150 (observation O2). No 0.00 edge: pd > 0 whenever the claim deductible > 0 (every share >= 0.5, plan max 1,000.00). |
| bn <- bl | "The worksheet benefit is not worked out until the claim carries a balance at loss above 0.00." | "not until"; state; clean | only bl sets a balance at loss; bl > 0 whenever a claim exists. |
| bn <- ep | "Before the worksheet benefit is worked out, the claim's excluded amounts are itemized under the Premier exclusion schedule." | "Before"; action form; fallback_reason tested: the field defaults to 0.00 and the Premier excluded total can legitimately total 0.00, so no record state singles the write out — fallback justified | the Premier exclusion schedule = ep ("This rule sets the Premier excluded total"). Wording "exclusion schedule" vs "excluded total" — same object; observation O3 on scope (ep is narrower: salvage/prior-damage carve-out). |
| eu <- ud | "The Plus excluded total is not fixed until a claim with a primary deductible above 0.00 shows a deductible covered above 0.00." | "not until"; state; clean | only ud sets deductible covered on a Plus claim; ud > 0 whenever deductible > 0 (plan max 500.00). |

No depended-on rule restates its dependant's sentence; no rule names another problem's tool or id; no rule states a cross-problem order beyond these four edges (bn's "ahead of any claim decision" orders against a base decision no tool performs — O1). No base sentence grounds an edge.

### override_declarations
Sentence-by-sentence against the cited base policies (gap_claim_benefit; gap_agg_contract_portfolio):
- gap_claim_benefit S1-S5 (status gate, notice period, counting, total-loss/theft wait, denial order): followed by all six (no extended policy decides a claim).
- S6 (benefit formula): split into clauses — "(deductible_reimbursement_basis …)" retired by pd and ud (each names own and sibling case, restates base for other plans); "the benefit is the scheduled balance on the date of loss (…)" retired by bl (restates base with interest for other plans); "less the portion above max_ltv_covered_pct (…)", "less the primary insurer's actual cash value, plus the deductible covered", "never below 0.00 and never above max_benefit_usd, rounded …" retired by bn (each restates base for other plans); "less every excluded_amounts item (…)" retired by ep and eu (restating base incl. salvage for other plans / salvage-retained / prior-damage claims). Declared.
- S7-S9 (credit to contract, excluded amounts stay owed, withdrawal, denial notice): followed.
- gap_agg_contract_portfolio S1 (own contract only): followed. S2 VSC refund clause: retired by ep and eu, declared. S4 (independent cancellation): followed.
- **gap_agg_contract_portfolio S3 "Force-placed insurance never counts as the borrower's primary insurance, and premiums it added to the contract balance are excluded amounts." is handled differently by ep and eu (placed-premium share 0 % / 50 % / 100 % in ep, 25 % / 75 % / 100 % in eu) and is named in neither overwrite** — finding C5.
- Every other base excluded item (past due, fees, deferrals, add-on refunds, deductible above reimbursement, CPI premiums) enters through the retired "less every excluded_amounts item" clause and is declared.

### factor_ladders
Counts as declared: pd 6 (1 method, 5 parameter), bl 4 (2 method, 2 parameter), ep 6 (2 method, 4 parameter), bn 6 (1 method, 5 parameter), ud 4 (1 method, 3 parameter), eu 6 (2 method, 4 parameter). All bindings disjoint between factors; no factor reads another factor's binding (scripted). Plain assembly bindings read factor outputs (bl_open, bl_count_used, bl_total; ep/eu *_pastdue, *_fee_part, *_deferral, *_premium; bn_cover_pct, bn_excess, bn_acv_used). Every ladder has 3 pairwise-disjoint tiers over the policy's scope; every tier is stated in the rule and implemented.

Realism verdict per factor (what a GAP waiver administrator actually weighs: scheduled balance, LTV limit, exclusions of arrears/fees/deferrals/CPI/add-on refunds, deductible reimbursement up to a cap, settlement value):

| factor | effect | verdict |
| --- | --- | --- |
| pd_proof_basis / ud_proof_basis | method | realistic (cap to the policy-on-file deductible); **shape fails T1 vs T2** (C2) |
| pd_history_share / ud_history_share | param | **unreal** (C1): lapse/placement history never scales a deductible reimbursement; primary insurance is tested only at the date of loss |
| pd_unpaid_share / ud_unpaid_share | param | **unreal** (C1): arrears are handled as excluded past-due amounts, never as a 50/80 % (40/75 %) cut of the deductible reimbursement |
| pd_in_force_share / ud_in_force_share | param | **unreal** (C1): no GAP addendum vests its deductible reimbursement by months in force (60/85 %, 50/75 %) |
| pd_requirement_share | param | **unreal outcome** (C1): a deductible above the contract's required maximum is capped/excluded above that maximum, not paid at 80/90 % of the whole |
| pd_channel_share | param | **unreal condition** (C1): the channel a proof arrived through (upload/fax/agent call/EDI) is not weighed by any GAP administrator |
| bl_first_period | param | acceptable (odd-first-period interest capitalised on a company schedule) |
| bl_due_change_count | method | acceptable; shape PASS |
| bl_courtesy_holdback | param | **unreal condition** (C1): whether an extension's fee was waived (in this world: the first extension on Tier 1/2, `extension_first_fee_waived: true`) is a servicing-fee artefact no GAP administrator weighs for the balance at loss |
| bl_capped_rate_adjustment | method | acceptable (SCRA-modified schedule); shape PASS; second reading C8 |
| ep_late_share_rule / eu_late_share_rule | param | **unreal outcomes** (C1): 50 % (ep) / 25 % and 75 % (eu) of a past-due installment excluded — no GAP worksheet excludes part of an unpaid installment |
| ep_fee_allowance / eu_fee_allowance | param | **unreal condition** (C1): returned-payment count is a loyalty-style allowance (XF-10) no GAP administrator grants against excluded fees |
| ep_deferral_relief / eu_deferral_relief | param | borderline-acceptable (limited deferral coverage exists in some programs) — observation O5 |
| ep_placed_relief / eu_placed_relief | param | **unreal outcomes** (C1) and undeclared override (C5): capitalised CPI premiums are excluded in full by real programs and by base S3 |
| ep_addon_basis / eu_addon_basis | method | realistic VSC-refund basis; **T1 and T2 select the same value on every charter-producible state** (C3) |
| ep_installment_rule / eu_installment_rule | method | realistic as a parameter; **mislabelled — every pair substitutes an installment amount into one formula** (C2) |
| bn_term_cut, bn_tier_cut | param | borderline-acceptable as a company covered-LTV grid by term and tier — observation O4 |
| bn_excess_share | method | acceptable; shape PASS |
| bn_value_floor | param | acceptable (settlement-value floor) |
| bn_notice_cut | param | **unreal outcome** (C1): a claim reported inside the 90-day notice period is never paid 5/10 % less; late notice is a timeliness test, not a percentage |
| bn_unpaid_cut | param | **unreal outcome** (C1): arrears are excluded as amounts; a further 5/10 % cut of the benefit for the same arrears is not a published GAP treatment |

Baseline realism: ep/eu baseline "installments deferred by an extension whose fee was waived are not excluded" — same fee-treatment criterion as bl_courtesy_holdback (C1 member C1-b).

All-pairs method tier tables (distinguishing input for each pair):

| factor | pair | verdict | distinguishing input |
| --- | --- | --- | --- |
| pd/ud_proof_basis | T1 MN(ded, coll) vs T3 ded | PASS (adds min with a proof field) | collision loss, ded 1,250, coll 500 -> 500 vs 1,250 |
| | T2 MN(ded, comp) vs T3 | PASS | theft, ded 500, comp 300 -> 300 vs 500 |
| | T1 vs T2 | **FAIL** — same operation MN(deducted, proof deductible); only the substituted cap number differs | none changes shape |
| bl_due_change_count | T1 M(fpd,old)+M(new,loss)+1 vs T2 M(fpd,old) | PASS (adds input/operation) | fpd 2025-02-28, old 2026-01-28, new 2026-02-10, loss 2026-08-05 -> 17 vs 11 |
| | T1 vs T3 M(fpd,loss)+1 | PASS (adds inputs) | same -> 17 vs 18 |
| | T2 vs T3 | PASS (data-selected window end) | same -> 11 vs 18 |
| bl_capped_rate_adjustment | T1 two-stage−signed vs T2 three-stage−signed | PASS (adds stage, end date, restored installment) | cap 2025-06-02 ended 2026-09-01: loss 2026-08-05 (T1) vs 2026-09-30 (T2) |
| | T1 vs T3 0 | PASS (T1 not 0 over its domain) | task-0 cap: 219.18 vs 0 |
| | T2 vs T3 | PASS | |
| bn_excess_share | T1 1 vs T2 (term−n)/term vs T3 bal/af | PASS all pairs | af 23,980, limit 22,310, n 18/72, bal 21,073.63 -> 1,670.00 / 1,252.50 / 1,467.60 |
| ep/eu_addon_basis | T1 issued vs T3 prorated | PASS | 256.17 vs 917.21 |
| | T2 formula vs T3 | PASS | 402.56 vs 822.24 |
| | T1 vs T2 | **FAIL as a ladder** — T1 reads the refund the VSC charter issued, T2 recomputes the VSC charter's own refund formula (vsc_refund: price x (1 − vsc_msr_used_ratio) − claims − fee, min refund); a total-loss cancellation refund is always priced by that formula, so the two tiers give the same value on every producible state (task-0 world: 256.17 = 256.17) | none exists among charter-producible states |
| ep/eu_installment_rule | T1 cap installment vs T2 restored vs T3 scheduled payment | **FAIL all pairs** — `unpaid x X − credit` with X substituted | none changes shape |

Surviving factors (after C1-C3 strikes): pd 0/6; ud 0/4; bl 3/4 (1 parameter); ep 1/6 (0 method); eu 1/6 (0 method); bn 4/6 (3 parameter, 1 method). Multi-source survivors: bl_due_change_count (servicing record + claim date) only; on the Plus side none survives (ud_proof_basis, ud_history_share, eu_addon_basis struck). Cross-difficulty survivors: bl_first_period, bl_due_change_count, bl_capped_rate_adjustment, ep/eu_deferral_relief, bn_term_cut, bn_tier_cut, bn_excess_share (contract).

Absent-record / decoy cases of every read (XF-12):
- LATEST claim reads (pd/bl/ep/bn/ud/eu `*_loss`, `*_type`, `bn_report`): absent claim -> None; bl returns 0.00 ("with no claim reported … 0.00"), the others would error — every task has a claim. Decoy: a withdrawn earlier claim row (task 0, 2026-03-16) is not latest; the `loss_date=` filter on SUMs keeps it out.
- XLATEST accepted proof (coll/comp/channel): absent -> None -> proof basis T3, channel "no accepted proof" 100 %; rejected proofs excluded by `proof_result='accepted'`; latest is by activity_date (as of today, not as of the loss — no post-loss proof in either world).
- XCOUNT CPI premium/notice rows: absent -> 0 -> fall-through. held_pending_proof_review premiums excluded by billing_method.
- CFIELD contract/vsc: first match per contract; absent VSC -> None -> add-on 0.00 via the `ep_vsc_price != None` guard.
- XSUM extensions by fee_treatment, XLATEST due-date change, SCRA applied/ended: absent -> 0 / None -> fall-through. A re-applied SCRA cap (applied, ended, applied) would mis-pair latest-applied with latest-ended (observation O9; no world has it).
- XCOUNT returned payments within 12 months: anchored at frozen_time (O6).

### findings
Charter-wide REDs (exhaustive member lists):

- **C1 — SOURCE-FACTOR RED, unreal ladders (XF-10).** Symptom: tiers whose condition or outcome no GAP waiver administrator publishes. Members (17 factors + 1 baseline sentence): pd_history_share, pd_unpaid_share, pd_in_force_share, pd_requirement_share, pd_channel_share; ud_history_share, ud_unpaid_share, ud_in_force_share; bl_courtesy_holdback; ep_late_share_rule, ep_fee_allowance, ep_placed_relief; eu_late_share_rule, eu_fee_allowance, eu_placed_relief; bn_notice_cut, bn_unpaid_cut; C1-b: the ep and eu baseline sentence "installments deferred by an extension whose fee was waived are not excluded". Evidence: the rule sentences quoted in factor_ladders; contract.yaml `extension_first_fee_waived` (the fee-waived criterion is a fee-schedule artefact). Affected: gap.extended.yaml rules/compute/factors of pd, ud, bl, ep, eu, bn. Bears on task 0 (pd, bl, ep, bn) and task 1 (ud, eu).
- **C2 — SOURCE-FACTOR RED, method shape / mislabel (XF-8).** Members: pd_proof_basis (T1 vs T2), ud_proof_basis (T1 vs T2), ep_installment_rule (all pairs), eu_installment_rule (all pairs). Evidence: the tier table above. Bears on both tasks.
- **C3 — SOURCE-FACTOR RED, two tiers selecting the same value.** Members: ep_addon_basis T1/T2, eu_addon_basis T1/T2. Evidence: vsc.yaml vsc_refund rule ("price_usd x (1 - vsc_msr_used_ratio), rounded half-up to the cent, less claims already paid …, less cancellation_fee_usd …; a computed refund below min_refund_usd is not issued") is exactly T2. Bears on both tasks.
- **C4 — SOURCE-FACTOR RED, factor counts after C1-C3.** pd 0, ud 0, bl 3 (1 parameter), ep 1 (no method), eu 1 (no method) against the 4-6 / 2 parameter / 1 method floor; Plus tree keeps no multi-source factor. bn alone meets the counts. Bears on both tasks.
- **C5 — SOURCE-POLICY RED, undeclared override (XF-21/22).** Base gap_agg_contract_portfolio: "Force-placed insurance never counts as the borrower's primary insurance, and premiums it added to the contract balance are excluded amounts." vs ep: "one period, the share is 0 percent; two or three periods, the share is 50 percent" and eu: "one period, the share is 25 percent; two or three periods, the share is 75 percent". Neither ep's nor eu's `overwrite` names this sentence (they retire only the VSC-refund clause of gap_agg_contract_portfolio). Members: ep, eu. Consequence demonstrated per task (both worlds carry 2 placed periods).
- **C6 — SOURCE-POLICY RED, assembly sentence naming factor quantities / one convention serving several factors (XF-3/XF-6).** Member: bl — "The adjustments combine in this order: days capitalized add to the amount financed the amount financed times the original annual percentage rate divided by 100, times those days, divided by 365, rounded half-up to the cent, giving the opening principal; installments held back come off the installments counted, never below none, and the scheduled principal is figured on the opening principal over what remains; any adjustment to the schedule is then added to the scheduled principal before the starting balance is rounded." It names three factors' quantities (bl_first_period, bl_courtesy_holdback, bl_capped_rate_adjustment) and carries the first-period factor's own capitalisation formula, so it can sit in neither the hub nor any single factor document without naming another factor. (pd, ep, eu, bn assembly sentences are generic — not members.) Bears on task 0.
- **C8 — SOURCE-POLICY RED (second reading), SCRA schedules' starting principal in bl.** "the adjustment is the principal a two-stage schedule leaves less the principal the signed schedule leaves …" and "Each stage carries forward the principal the stage before it left, by the same formula as the scheduled principal …", while "The scheduled principal is the opening principal, which is the amount financed …" and the assembly sentence makes the opening principal "the amount financed" plus the capitalised days. The first stage's (and the signed schedule's) starting principal is stated nowhere: compute uses `bl_af` (amount financed) for both; "the same formula as the scheduled principal" reads as the opening principal. Defensible only where first-period days > 0 and a cap applies — task 0. Consequence demonstrated in 0.md.

Observations (no demonstrated consequence on the scored solution):
- O1 bn rule and record_claim_worksheet_benefit docstring: "ahead of any claim decision" — an ordering phrase against a base decision no tool of this difficulty or share_tools performs.
- O2 deductible_covered_usd has two writers (Premier and Plus tools, bodies unscoped); each state-form edge resolves by plan through the depended-on rule.
- O3 bn<-ep action sentence says "itemized under the Premier exclusion schedule"; ep's scope excludes salvage-retained / prior-damage claims, for which bn's sentence names a schedule that does not apply (no world has such a claim).
- O4 bn_term_cut / bn_tier_cut: covered-LTV cut by term and credit tier at claim time — accepted as a company grid; flag if the KB audit judges it a post-sale benefit cut.
- O5 ep/eu_deferral_relief accepted as limited deferral coverage; ep/eu deferral baseline multiplies deferred installments by today's scheduled payment, not the installment actually deferred (both worlds deferred an SCRA-capped installment).
- O6 ep/eu fee part is "the fees due the contract carries" (today's fees_due, including late charges assessed after the date of loss) and the returned-payment window is anchored at today, while every other figure is anchored at the date of loss — realism note (post-loss fees are not part of a balance at loss).
- O7 neither world posts the primary insurer's settlement to the contract (payment_type insurance_settlement exists) although the settlement letter is in hand — plausible funds-in-transit state; the arrears-based factors depend on it.
- O9 SCRA latest-applied / latest-ended pairing (bl, ep, eu) mis-pairs a re-applied cap; ep/eu installment tiers T1/T2 overlap in prose for that case.
- O10 claim_*_deductible_reimbursement docstrings mention submitting settlement documents; the body records only the amount.
- O11 both worlds' VSC total-loss refunds fall outside vsc `refund_processing_days` (30) counted from the cancellation effective date (task 0: refunded 58 days after; task 1: unrefunded 59 days after); within 30 days of the processing date (closed_date) in both — real late-reported-loss lag.
- O12 ep/eu scope ("whose primary insurer took the vehicle's salvage, or had none to take, and deducted nothing for prior damage") names facts no record carries (no salvage / prior-damage field on gap_activities); considered against XF-17 and judged not a member (it conditions on a settlement-letter fact the persona supplies in both tasks and is the base charter's own excluded-item vocabulary). Flag for the KB audit.
- Cross-category seed pricing (XF-27) checked by replay: contract ledgers (both) reproduce every interest/principal row under contract_msr_accrued_interest (current apr_pct x days), the SCRA payment reduction, late charges (lesser of 5 % and 25.00), extension fees (Tier 2 first waived, Tier 3 assessed), returned-payment fees, fees_due and principal_balance; CPI rows reproduce first-period proration, backdating, notice spacing and pro-rata refunds; VSC refund (task 0) reproduces the vsc formula. No priced-row defect found.

## closing_checklist
Written after both reveals (nothing above this heading was edited after them).
- Per-task files 0.md and 1.md correspond one-to-one with tasks/0.json and tasks/1.json; both comparison sections are RED, so the difficulty is NOT closed.
- Scopes (charter_scope, revealed): task 0 = {pd, bl, ep, bn} + their four tools; task 1 = {ud, eu} + their two tools. Pairwise disjoint, jointly complete over the six extended policies; every task tool has an independent uuid8.
- Trees: task 0 has 3 prerequisite problems, 3 value_input edges, one owner=user problem, acyclic; task 1 has 1 prerequisite problem, 1 value_input edge, one owner=user problem. Whole-difficulty graph acyclic. Problem-tree relationship PASS in both tasks.
- Factors: fail (C1-C4) — only bn meets the 4-6 / 2 parameter / 1 method floor after strikes; task 1 has no surviving multi-source factor.
- Policy self-consistency: fail (C5, C6, C8). Unique solution: fail (task 0 via C5 and C8; task 1 via C5).
- Every GT value equals the charter's compute on the handling-time world (blind derivation matched all six scored arguments and all 32 sensitivities/baselines figure for figure).
- Additional per-task RED: task 1 finding 5 (VSC refund overdue under vsc refund_processing_days; design_rationale asserts the opposite).
- Instantiation gates not re-run by this auditor (coordinator snapshot cited in charter_global_frozen).

Open charter-wide RED classes for the rework, each with its complete member list in § findings: C1 (17 factors + ep/eu fee-waived deferral baseline sentence), C2 (pd_proof_basis, ud_proof_basis, ep_installment_rule, eu_installment_rule), C3 (ep_addon_basis, eu_addon_basis), C4 (pd, ud, bl, ep, eu counts; Plus tree multi-source), C5 (ep, eu vs gap_agg_contract_portfolio S3), C6 (bl assembly sentence), C8 (bl SCRA starting principal).

VERDICT revision_1: task0=RED task1=RED charter=C1,C2,C3,C4,C5,C6,C8

## revision_2

### charter_global_frozen (revision_2)
- Frozen 2026-10-20T06:21:15Z, before any round-2 GT was read. Gate snapshot (coordinator `/tmp/erl0072_coord/snapshot.sh gap_waiver_cancellations_and_claims 2`, 2026-10-20T06:13:50): check_extended EXTENDED OK; check_task_tools TASK TOOL CONTRACT OK; replay_tasks --check REPLAY OK; check_solvability SOLVABILITY OK; check_compute COMPUTE OK; check_grounding GROUNDING OK; check_cross_fire SCOPE OK. worklog tail line: "REWORK round 2: gates 7/7 green".
- Source hashes changed (gap.extended.yaml 6df228d8a37297cdd9c9983248155710d0f182307122966011a566f6791dcb02; task_tools.py e7575fc999db1ed0585685403b9ba0c2cfe88b0f9a081b621c1d19f378026f32), so every charter-global section is re-derived in full below; nothing is carried forward from revision_1.
- Views r2: 0.json cc534ea6c411fd868cdfe30952622ee93242896f9ad5123279b60cd294ca2961, 1.json 8f2bed609571ccbfcd296294965a6e03d911e29c17a829baa7bb3e43a5166333. Both worlds were rebuilt (new ids, task 0 frozen_time moved to 2026-10-05 10:40 EDT), so both tasks get fresh blind derivations.
- Also read: rework_claims_r2.md (item ids only, no values). Masked until freeze: tasks/*.json, plan.md, worklog.md (except its tail line, read as instructed).

### policy_conflict_scan (r2)
- Base section byte-identical to blueprint/products/gap.yaml (diff clean). Same six extended policies, same tools, same fields, same plan scopes; ep/eu scope no longer conditions on salvage / prior damage (O3/O12 closed) — salvage retained and prior-damage deductions are left to the decision "as the settlement documents state them" (ep/eu replaced_by), which names no record field.
- No tool writes an event with triggers; terminal state = one claim-row field per write. Trees unchanged in shape: bn <- bl, bn <- ep <- pd (Premier); eu <- ud (Plus).

### rule_compute_equivalence (r2)
- compute_basis sweep: 0 non-verbatim quotes, 0 unbased bindings, every baseline.rule and every replaced_by verbatim in its rule, every superseded_clause verbatim in its base rule (scripted).
- Edge/absent cases: pd/ud T2 "no accepted proof at all" -> MN(deducted, plan max) guarded for no tracking record; ep/eu `*_pd_inst` average guarded by unpaid >= 1; `*_pending` guarded by an accepted proof; `*_df_count` 0 deferrals -> 0; `ad_moved` negative/zero -> none; CFIELD('cpi','variant_name') absent -> "any other plan or no tracking record". Rounding placements match each rule sentence (pd/ud final; bl level installment, each capitalised interest, final; ep/eu pending share, VSC formula, signed level installment, final; bn final).
- **Same-day tie not stated (XF-12):** ep/eu placed-premium T2 uses "that latest premium's share"; the latest premium is selected `date_field='billing_period_start'` while "the billing date of the latest premium added" is `activity_date`; both worlds' placements bill two premiums on the same day (2025-11-07; 2025-10-12), and the rule never says which same-day premium is "the latest". Not taken in either world (T1 applies). Finding C10.
- ep_past_due_count day limits are vacuous: with one unpaid installment the oldest is at most 30 days past due (MONTHS(next_due, loss) = 0, due_day <= 28), with two at most 61 days (< 75); so ep's "no more than 30 days" / "no more than 75 days" never exclude anyone (eu's 20 / 60 do). Observation R2-O1.

### action_binding_and_uuids (r2)
- Six (target_tool, computes) pairs, one policy each; uuid8s unchanged and distinct (7815b2b6, 15fb7d99, 258c7293, 931d4ebc, 49e3d00f, 41771560). No factor id inside a tool name. Docstrings: no ordering words (O1 closed: "ahead of any claim decision" removed from rule and docstring), no example values, user-tool docstrings now say the call records only the amount (O10 closed). Bodies are bare `ctx.update` — no prerequisite judged by the tool layer.

### prerequisite_graph and prerequisite_sentences (r2)
- Unchanged edges and sentences (ep<-pd state, bn<-bl state, bn<-ep action with fallback_reason, eu<-ud state), each verbatim in its own rule, gates exist, resolved_by = depended-on target_tool, graph acyclic. bn<-ep condition now "as the Premier excluded total itemizes it" (matches ep's unconditioned scope). Fallback still justified (field defaults 0.00; a 0.00 total is possible). Single resolving write per edge as in revision_1 (O2 stands: both deductible tools write one field, scoped by plan in rule and docstring). No 0.00 edge (every share > 0; plan maxima > 0).

### override_declarations (r2)
- gap_claim_benefit: deductible clause retired by pd/ud (self-naming, sibling-naming tails); scheduled-balance clause by bl; LTV and ACV/deductible clauses by bn; excluded-items clause by ep/eu. bn no longer retires the floor/cap/rounding clause — and none is needed: bn's "never below 0.00 and never above the plan's max_benefit_usd, rounded half-up to the cent" equals the base clause.
- gap_agg_contract_portfolio: VSC-refund clause retired by ep/eu; **"premiums it added to the contract balance are excluded amounts" now retired by ep and eu with self-naming tails that name the sibling and restate the base for other plans — C5 closed.** "Force-placed insurance never counts as the borrower's primary insurance" stays in force and nothing contradicts it.
- No undeclared departure found in any other base sentence.

### factor_ladders (r2)
Declared: pd 6 (1 method, 5 parameter), bl 4 (2 method, 2 parameter), ep 6 (2 method, 4 parameter), bn 6 (1 method, 5 parameter), ud 4 (1 method, 3 parameter), eu 6 (2 method, 4 parameter). Bindings disjoint; no factor reads another factor's binding (scripted); every tier stated in rule and compute; 3 disjoint tiers each.

| factor | effect | realism / structure verdict |
| --- | --- | --- |
| pd_recognized_deductible, ud_recognized_deductible | method | realistic (cap to policy-on-file deductible of the paying coverage; plan's required maximum when no proof on file); shape table below |
| pd_tier_schedule, ud_tier_schedule | param | **unreal (C1)** — deductible reimbursement cut to 75/90 % (70/85 %) by the borrower's credit tier |
| pd_term_schedule | param | **unreal (C1)** — cut to 85/95 % by original term |
| pd_band_schedule, ud_band_schedule | param | **unreal (C1)** — cut to 80/90 % (75/85 %) by the CPI vehicle-value plan |
| pd_ltv_schedule | param | **unreal (C1)** — cut to 85/95 % by LTV at signing |
| pd_af_schedule, ud_af_schedule | param | **unreal (C1)** — cut to 85/95 % (80/88 %) by amount financed |
| bl_first_period, bl_added_days | param | acceptable (odd-days interest capitalised on company schedules) |
| bl_due_change_count, bl_capped_rate_adjustment | method | acceptable; C8 closed (both schedules from the amount financed, stated) |
| ep/eu_past_due_count, ep/eu_deferral_count | param | borderline-acceptable whole-installment relief (as revision_1 O5); R2-O1 vacuity |
| ep/eu_past_due_installment, ep/eu_deferral_installment | param | realistic (installment actually due/deferred under the SCRA cap); C2 closed by relabel, distinct third value |
| ep/eu_placed_premium_basis | method | realistic (premiums net of refunds); C10 tie; R2-O3 |
| ep/eu_addon_basis | method | realistic; C3 closed (issued-or-own-formula merged into one tier) |
| bn_term_cut, bn_tier_cut, bn_band_cut | param | borderline-acceptable covered-LTV grid (O4) |
| bn_excess_share | method | acceptable |
| bn_value_floor | param | acceptable |
| bn_floor_value | param | **gated through bn_value_floor (C9)** — it sets "the vehicle value the worksheet benefit's floor is figured on", a quantity the baseline does not have (baseline: "the actual cash value the worksheet benefit deducts, which is the primary insurer's actual cash value"); with bn_value_floor at its fall-through ("no floor") it has no effect on any world; the sentence "the larger of the primary insurer's actual cash value … and any floor that applies, a floor being its percent of the vehicle value it is figured on" names both factors' quantities (XF-1/5/6) |

The deductible-benefit-schedule factors are the reworker's own "BLUEPRINT-KNOWN residue" (rework_claims_r2 C1): no GAP waiver administrator pays a different share of the same plan's deductible reimbursement by credit tier, term, collateral band, LTV or amount financed — those variables price the addendum, they do not scale the insurer's deductible the plan reimburses.

All-pairs method tiers:

| factor | pair | verdict | distinguishing input |
| --- | --- | --- | --- |
| pd/ud_recognized_deductible | T1 MN(d, pick(loss type: coll / comp)) vs T2 MN(d, plan max) | PASS by XF-8 letter (T1 adds a conditional pick and the loss-type input); note both are min(d, cap) | collision, d 1,250, coll 500 vs no proof, plan max 1,000 -> 500 vs 1,000 |
| | T1 vs T3 d; T2 vs T3 | PASS | 500 vs 1,250; 1,000 vs 1,250 |
| bl_due_change_count | all pairs | PASS (as revision_1) | 17 / 11 / 18 |
| bl_capped_rate_adjustment | all pairs | PASS | live vs ended vs none |
| ep/eu_placed_premium_basis | T1 added − Σrefunds vs T3 added | PASS | 239.74 vs 261.70 |
| | T2 added − prorated latest vs T3 | PASS | proof eff 2025-11-20, no refund: 261.70 − 74.66 vs 261.70 |
| | T1 vs T2 | PASS (different inputs: refund rows vs proof date) | refund 21.96 credited vs proof eff 2025-11-20 unrefunded |
| ep/eu_addon_basis | T1 own refund vs T2 0 vs T3 prorated | PASS all pairs (no tier 0 over its whole domain except T2, and no other tier is) | 256.17 / 0.00 / 917.21 |
| bn_excess_share | all pairs | PASS | 1.0 / 0.75 / bal/af |

Surviving factors after strikes: pd 1/6 (method only); ud 1/4; bl 4/4; ep 6/6; eu 6/6; bn 5/6. Multi-source survivors: bl_due_change_count, ep/eu_past_due_count, ep/eu_placed_premium_basis, pd/ud_recognized_deductible. Cross-difficulty survivors in every policy except pd/ud parameters.

### findings (r2)
Round-1 classes: C2 closed (ep/eu installment factors are parameters; pd/ud proof basis passes XF-8 by the conditional pick); C3 closed; C5 closed; C6 closed (each bl factor sentence carries its own effect; no shared assembly sentence names factor quantities); C8 closed. **C1 open with new members; C4 open.**
- **C1 — SOURCE-FACTOR RED, unreal ladders (still open; complete member list):** pd_tier_schedule, pd_term_schedule, pd_band_schedule, pd_ltv_schedule, pd_af_schedule, ud_tier_schedule, ud_band_schedule, ud_af_schedule. All 17 revision_1 members and the fee-waived baseline sentence are gone (verified: none of their tiers remains in any rule). Bears on task 0 (pd) and task 1 (ud).
- **C4 — SOURCE-FACTOR RED, counts after strikes:** pd 1 factor (0 parameter), ud 1 factor (0 parameter) against 4-6 / 2 parameter. Every other policy meets the floor.
- **C9 — SOURCE-FACTOR / SOURCE-POLICY RED (XF-1/5/6), factor gated through another factor:** bn_floor_value is effective only through bn_value_floor's tier; member list: bn_floor_value (with its rule sentence "The vehicle value the worksheet benefit's floor is figured on follows …" and the combination sentence quoted above). No other policy has a factor acting on a quantity the baseline lacks (checked: bl capitalisations act on the opening principal, ep/eu installment and count factors on baseline counts/amounts, pd/ud shares on the baseline deductible).
- **C10 — SOURCE-POLICY RED (XF-12), same-day tie unstated:** ep_placed_premium_basis and eu_placed_premium_basis ("the billing date of the latest premium added", "that latest premium's share") with same-day premium rows in every backdated placement. No scored consequence in either world (T1 taken).
- Observations: O2, O4, O5 (now ep/eu count factors), O6 (fees due include post-loss late charges), O7 (no insurance-settlement payment posted), O8 (task-0 claim deductible 1,250 vs proof 500 vs plan max 1,000), O9 (re-applied cap pairing) carried; R2-O1 (ep day limits vacuous); R2-O2 bl_added_days and bl_due_change_count each re-read the latest due-date change, and ep/eu installment factors each re-read the SCRA records (duplicated selections, no cross-factor read — judged not an XF-2 member); R2-O3 ep/eu placed-premium T2 nets only the latest premium's share, while the CPI charter refunds every charge with days on or after the proof's effective date — where a proof's coverage starts before the latest period, T2 is not the "refunds … due" the replaced_by promises (no world reaches T2).

## closing_checklist (revision_2)
Written after the round-2 reveals; nothing in the revision_2 charter-global section was edited after them.
- Per-task files carry revision_2 sections (frozen derivation, comparison, findings); both comparisons RED -> difficulty NOT closed.
- Scopes (charter_scope): task 0 {pd, bl, ep, bn}, task 1 {ud, eu} — disjoint and complete; uuid8s independent.
- Trees: task 0 3 prerequisite problems / 3 value_input / user problem pd; task 1 1 / 1 / user problem ud; graph acyclic. PASS.
- Blind derivation matched all six scored arguments, six baseline_results and 32 per-factor sensitivities of round 2 figure for figure; no second defensible value in either task (C5, C8 closed).
- Factors: pd and ud below the 4-factor / 2-parameter floor once C1 members are struck (C4); bn_floor_value gated (C9). bl, ep, eu meet every factor requirement.
- Round-1 class status: C1 open (new members only), C2 closed, C3 closed, C4 open, C5 closed, C6 closed, C8 closed. New in round 2: C9, C10.
- Gates: coordinator snapshot 7/7 green (cited above); not re-run by this auditor.

Open charter-wide RED classes, complete member lists in § findings (r2): C1 (pd_tier_schedule, pd_term_schedule, pd_band_schedule, pd_ltv_schedule, pd_af_schedule, ud_tier_schedule, ud_band_schedule, ud_af_schedule), C4 (pd, ud), C9 (bn_floor_value), C10 (ep_placed_premium_basis, eu_placed_premium_basis same-day tie).

VERDICT revision_2: task0=RED task1=RED charter=C1,C4,C9,C10

## revision_3

### charter_global_frozen (revision_3)
- Frozen 2026-10-20T07:52:48Z, before any round-3 GT. Gate snapshot (`/tmp/erl0072_coord/snapshot.sh gap_waiver_cancellations_and_claims 3`, 2026-10-20T07:50:38): check_extended EXTENDED OK; check_task_tools TASK TOOL CONTRACT OK; replay_tasks --check REPLAY OK; check_solvability SOLVABILITY OK; check_compute COMPUTE OK; check_grounding GROUNDING OK; check_cross_fire SCOPE OK. worklog tail: "REWORK round 3: gates 7/7 green".
- Views r3: 0.json cc534ea6c411fd868cdfe30952622ee93242896f9ad5123279b60cd294ca2961, 1.json 8f2bed609571ccbfcd296294965a6e03d911e29c17a829baa7bb3e43a5166333 — byte-identical to r2 (worlds unchanged). Sources: gap.extended.yaml 08b64853a18bd8f2a2e9f585c976d1aea8d1c6ef42be7228f7cb92a0e3979e20 (changed -> every charter section re-derived below); task_tools.py e7575fc9… (unchanged since r2 -> action_binding_and_uuids carried by reference to § revision_2 on that hash). Scored values can move with the charter, so both tasks get fresh frozen derivations.
- Read rework_claims_r3.md (item ids, prose, no values). Masked until freeze: tasks/*.json, plan.md, worklog.md (tail line only).

### policy_conflict_scan / rule_compute_equivalence / prerequisites / overrides (r3, re-derived)
- Base section byte-identical to blueprint (diff clean). Six policies, same tools, scopes, fields; no triggers written.
- compute_basis sweep: 0 non-verbatim, 0 unbased; baseline.rule, replaced_by verbatim in rules; superseded clauses verbatim in base. No factor reads another factor's binding; plain bindings read factor outputs only for assembly (result / bl_open / bl_sched / bl_total / ep-eu part bindings / bn_cover_pct, bn_excess, bn_acv_used).
- Prerequisite edges, sentences, forms, gates, fallback unchanged from revision_2 and re-verified verbatim; acyclic; no 0.00 edge.
- Overwrites unchanged in scope; the capitalised-premium replaced_by now reads "net of refunds credited or, where the proof's coverage starts inside the latest billing period, due" and matches the T2 condition. No undeclared departure found (base sentence sweep repeated; bn's floor/cap/rounding equals the in-force base clause).
- **C10 closed:** every latest-read now states its tie: claims ("the one recorded first on the addendum counts"), accepted proofs, due-date change / cap-applied / cap-ended records (bl), cap and extension records (ep/eu), and the latest premium ("the force-placed premium whose billing period starts latest"; every premium read selects on billing_period_start). Each matches the DSL's strict-latest / first-row-kept behaviour. The supporting clause "a backdated placement bills two or more premiums on one day while no two premiums share a billing period" is true under cpi_evt_premium_billing (first prorated period + current period billed at placement; held premiums are excluded by billing_method).
- **R2-O1 closed:** ep past-due relief is count-only ("one, none is counted; two, one is counted; three or more, all are counted"); eu keeps 20 / 60 days (not vacuous).
- **R2-O3 closed:** placed-premium T2 now applies only when the proof's policy effective date falls inside the latest premium's billing period — exactly the case in which the CPI charter leaves a refund due on that premium alone; earlier-starting coverage falls to T3 and the rule says so.
- **O6 closed:** fee part = fees due less late charges on installments that fell due after the date of loss, never below 0.00. Compute window `MONTHS(next_due, NOW) − MONTHS(next_due, loss)` over installment_due_date. Probed: task-0 world selects 2026-08-10 / 2026-09-10 (40.53) and excludes 2026-06-10 / 2026-07-10 and the 2025 charge; task-1 world selects 2026-08-25 / 2026-09-25 (41.47). A borrower current at the loss (next due after the loss) still yields exactly the post-loss installments (MONTHS goes negative, window widens by the same amount). Edge note (observation R3-O1): a post-loss late charge already paid is still subtracted from fees due (floored at 0.00); the rule says so verbatim.

### factor_ladders (r3, re-derived)
Declared counts unchanged (pd 6, bl 4, ep 6, bn 6, ud 4, eu 6); method all-pairs tables unchanged from revision_2 (pd/ud recognized deductible PASS by conditional pick; bl two methods PASS; ep/eu placed-premium and add-on PASS; bn excess share PASS) — re-checked on the r3 compute.
- **C9 closed:** the value floor is now a baseline quantity ("the value floor percent is 66 percent and the vehicle value the floor is figured on is the vehicle's book value at origination"); bn_value_floor's fall-through is K('floor_base_pct') = 66 % = the baseline, bn_floor_value's fall-through is the book value = the baseline; each acts on a quantity the baseline has, and each moves the task-0 value alone (5,503.70 / 4,623.70 vs 5,183.70). No combination sentence names both.
- **New member of C1 (regression introduced by the C9 fix):** bn_value_floor's fall-through and the bn baseline: "24 or more, 66 percent" / "the value floor percent is 66 percent and the vehicle value the floor is figured on is the vehicle's book value at origination". A floor that stays at 66 % of the origination book value however old the vehicle is (month 24 through month 72+) replaces the primary insurer's actual cash value whenever the vehicle has lost more than a third of its origination value — the ordinary state of a 3- to 6-year-old financed car — and so cuts the benefit of an ordinary customer whose insurer paid a correct ACV. No GAP waiver publishes a non-depreciating floor on origination value as its standard treatment (revision_2's "24 or more, no floor" was the realistic fall-through). In the task-0 world itself the all-baseline reading gives floor 12,804.00 above the insurer's 12,700.00 at 18 months.
- C1 (deductible-benefit schedules) and C4 unchanged and explicitly not claimed closed by the reworker (rework_claims_r3 C1/C4: "NOT closed").

### findings (r3)
- **C1 — SOURCE-FACTOR RED (open; complete member list):** pd_tier_schedule, pd_term_schedule, pd_band_schedule, pd_ltv_schedule, pd_af_schedule, ud_tier_schedule, ud_band_schedule, ud_af_schedule; plus new member bn_value_floor fall-through / bn baseline floor default (66 % of origination book value at every age). Bears on task 0 (pd, bn) and task 1 (ud).
- **C4 — SOURCE-FACTOR RED (open):** pd 1 surviving factor, ud 1, against 4-6 / 2 parameter / 1 method. bn keeps 5 survivors with bn_value_floor struck (term, tier, band, excess_share, floor_value: 4 parameter, 1 method) and meets the floor. bl, ep, eu meet every requirement.
- Closed this round: C9, C10, R2-O1, R2-O3, O6.
- The reworker's ruling request (whether reimbursement-claim timeliness terms count as real GAP factors, and how to meet task 0's sixth Premier factor) is a design question outside this audit's remit; one fact bears on it: base gap_claim_benefit already makes "the complete claim file (required_claim_documents) … received within claim_docs_due_days after the primary insurer's settlement" a denial ground, so any reimbursement-window factor measures a quantity a base sentence already governs and would need its own declared overwrite.
- Observations carried: O2, O4, O5, O7, O8, O9, R2-O2; new R3-O1 (above).

## closing_checklist (revision_3)
- Written after the round-3 reveals; the revision_3 charter section above was not edited after them.
- Both tasks' GT matched the blind derivation on every scored argument (310.69, 21,046.18, 2,112.48, 5,183.70; 190.74, 1,592.37), every baseline_result and all 32 sensitivities. Trees PASS, unique solution PASS, policy self-consistency PASS in both tasks.
- Scopes disjoint and complete; tools and uuid8s unchanged; graph acyclic; gates 7/7 green (coordinator snapshot).
- Not closed: factors. C1 open (pd_tier_schedule, pd_term_schedule, pd_band_schedule, pd_ltv_schedule, pd_af_schedule, ud_tier_schedule, ud_band_schedule, ud_af_schedule, and new bn_value_floor fall-through / bn baseline floor default); C4 open (pd 1 survivor, ud 1 survivor). Closed this round: C9, C10, R2-O1, R2-O3, O6. No regression elsewhere.

VERDICT revision_3: task0=RED task1=RED charter=C1,C4

## revision_4

### charter_global_frozen (revision_4)
- Frozen 2026-10-20T09:53:33Z, before any round-4 GT. Gate snapshot (`/tmp/erl0072_coord/snapshot.sh gap_waiver_cancellations_and_claims 4`, 2026-10-20T09:49:02): EXTENDED OK; TASK TOOL CONTRACT OK; REPLAY OK (--check); SOLVABILITY OK; COMPUTE OK; GROUNDING OK; SCOPE OK. worklog tail: "REWORK round 4: gates 7/7 green".
- Views r4: 0.json 4420d7f1f1a8dd297d584c94b7fca300d0d94f81d45cc2ad4060569e1495d91f, 1.json 4e1d76c2cbdafd7317af006cb1a5db6a18af12e9a3c403c4c04bcb6285d243f3 (both re-seeded: claim rows, proofs, rate-cap-ended dates, coverage records and personas changed). Sources: gap.extended.yaml 6a13f6a1f809eaffe428caeb83ca3eebf94675d402df8a20e13fa504914a939b (changed -> re-derived); task_tools.py e7575fc9… (unchanged; § revision_2 action_binding_and_uuids carried by that hash). Coordinator ruling quoted in the brief (timeliness family admissible as a declared scoped overwrite; duty extension only as a company accommodation; the eight C1 fillers and the 66 % floor must go) applied below.
- Read rework_claims_r4.md (item ids, prose). Masked until freeze: tasks/*.json, plan.md, worklog.md (tail line only).

### re-derived checks (r4)
- Base byte-identical. compute_basis sweep: 0 non-verbatim, 0 unbased; baseline.rule / replaced_by verbatim; superseded clauses verbatim in gap_claim_benefit (incl. the new late_documents clause on pd and ud).
- Overwrites: pd and ud each retire "(deductible_reimbursement_basis …)" and "or when the complete claim file (required_claim_documents) is not received within claim_docs_due_days after the primary insurer's settlement (late_documents)" with self-naming tails that name the sibling and restate the late_documents denial for the claim itself on every plan (XF-19/20 satisfied). Other overwrites unchanged.
- Prerequisites: ep<-pd and eu<-ud are now action form ("The Premier excluded total is fixed only after the borrower's claim for the Premier deductible reimbursement is recorded on the claim." / "The Plus excluded total is not fixed until the borrower's claim for the Plus deductible reimbursement is recorded on the claim."), fallback_reason tested and justified (a late claim legitimately records 0.00, leaving deductible_covered_usd as it stood; no record state singles the write out). bn<-bl, bn<-ep unchanged. Graph acyclic; gates exist; verbatim.
- Ties (XF-12): every new latest-read states its tie (accepted proof, accepted proof naming an insurer, rate-cap records). C10 stays closed.
- **C1 floor member closed:** bn baseline "the value floor percent is 60 percent while the addendum has been in force fewer than 24 whole months at the date of loss and there is no floor from 24 whole months on"; bn_value_floor 80 / 70 / no floor, fall-through = baseline; C9 kept (both floor factors act on baseline quantities).
- **Eight C1 schedule shares removed** (none of their tiers remains in any rule or compute).

### factor_ladders (r4, pd and ud rebuilt; others re-checked)
pd: pd_policy_at_loss (method), pd_paying_coverage (method), pd_window_start (method), pd_window_days (parameter), pd_duty_extension (parameter), pd_closed_day (parameter). ud: ud_policy_at_loss (method), ud_window_days, ud_duty_extension, ud_closed_day (parameters). bl, ep, eu, bn as revision_3 (bn floor default changed as above).

All-pairs method tiers (XF-8: an aggregate of one field counts as one input whatever its filter; constants ignored):

| factor | pair | verdict | why |
| --- | --- | --- | --- |
| pd/ud_policy_at_loss | T1 settling insurer's latest accepted proof vs T3 latest accepted proof | **FAIL** | same field (the proof's deductible), same formula MN(claim deductible, proof deductible); only the record filter (insurer_name) differs |
| | T2 plan borrower maximum vs T3 | **FAIL** | a different number substituted into the same MN(…) |
| | T1 vs T2 | FAIL | same |
| pd_paying_coverage | T1 collision deductible vs T2 comprehensive deductible | **FAIL** | same MN(…) with the other field substituted (revision_1 C2 precedent) |
| | T3 lower of the two vs T1 / T2 | PASS | adds a min |
| pd_window_start | T1 loss date + unrecovered_theft_wait_days vs T3 loss date | **FAIL** | same input plus a constant |
| | T2 reporting date vs T3 loss date | **FAIL** | one date substituted for another in the same comparison |
| bl, ep, eu, bn methods | — | PASS (tables in § revision_2) | unchanged |

Realism (coordinator ruling: the timeliness family is admissible; its anchors and lengths are still judged):
- pd/ud_policy_at_loss tiers, pd_paying_coverage, pd/ud_duty_extension (worded as a company accommodation, not SCRA), pd/ud_closed_day (weekend roll-forward): realistic terms.
- **Unreal (C1):** the window anchored at the date of loss with 10-45 days. The reimbursement is claimed "with the primary insurer's settlement documents", and the base itself gives the claim file claim_docs_due_days (90) *after the settlement* and decides a theft only after unrecovered_theft_wait_days (30) unrecovered. Members:
  - pd baseline sentence "The claim window of the Premier deductible reimbursement opens on the date of loss, its last day is the opening date plus its window days, which are 20 calendar days, and the window is not extended" and pd_window_start's fall-through ("otherwise the date of loss"): for any theft, and for any claim settled more than 20 days after the loss, the window closes before the settlement it needs can exist.
  - pd_window_days ("more than 45 days, 10 days, so that a late-reported claim's reimbursement still closes soon after the report"): a window shortened because the claim was reported late (yet within the base's 90-day notice period) is not a published GAP term.
  - ud baseline (same 20-day date-of-loss sentence) and ud_window_days (theft 45, comprehensive 30, otherwise 20 days, all from the date of loss): a Plus theft window closes 15 days after the earliest day the GAP charter lets a theft be decided; in task 1's own timeline an ordinary (non-military) borrower who reports with the settlement, as this borrower did on 2026-10-06, has already lost the reimbursement (window closed 2026-10-05).
- **Factor independence (new class C12, XF-1/XF-2):** pd_closed_day's bindings pd_cd / pd_cd_dow read the plain binding pd_due = pd_wd + pd_dd − pd_elapsed, i.e. the outputs of pd_window_days, pd_duty_extension and pd_window_start; ud_closed_day likewise reads ud_due = ud_wd + ud_dd − ud_elapsed (ud_window_days, ud_duty_extension). Its tier (Saturday / Sunday / weekday) is decided by other factors' outputs, and a plain binding reads factor-owned bindings. Members: pd_closed_day, ud_closed_day (plain pd_due, ud_due). (Transitive scan of every other factor: clean.)

Surviving factors: pd — duty_extension only (policy_at_loss, paying_coverage, window_start struck C2; window_days C1; closed_day C12) = 1; ud — duty_extension only = 1. bl 4, ep 6, eu 6, bn 6 (bn_term/tier/band cuts remain O4 borderline).

### findings (r4)
- **C1 — SOURCE-FACTOR RED (open; members):** pd baseline window sentence, pd_window_start fall-through, pd_window_days, ud baseline window sentence, ud_window_days. (Revision_3 members — eight schedule shares and the 66 % floor — all closed.)
- **C2 — SOURCE-FACTOR RED (reopened; members):** pd_policy_at_loss, pd_paying_coverage, pd_window_start, ud_policy_at_loss.
- **C4 — SOURCE-FACTOR RED (open):** pd 1 survivor, ud 1 survivor; neither keeps a method factor.
- **C11 — SOURCE-FACTOR RED, re-seed contradicts the owning charter and the persona (XF-27):** contract_scra_rate_cap: "The cap ends the day after scra_active_duty_end_date". Task 0: customers.553cc76e scra_active_duty_end_date 2026-08-31, rate_cap_ended 5dd5070e 2026-08-20 (charter: 2026-09-01), persona "released August 20, 2026". Task 1: customers.0ecd9c06 2026-09-14, rate_cap_ended f0285d0b 2026-09-02 (charter: 2026-09-15), persona "to September 1, 2026". The duty-extension and closed-day tiers rest on the moved dates (demonstration per task).
- **C12 — SOURCE-FACTOR RED (XF-1/2):** pd_closed_day, ud_closed_day.
- Closed: C9, C10 (kept), the bn floor member of C1, the eight schedule shares.
- Observations: the reimbursement is binary on timeliness (amount or 0.00) and both worlds sit on a weekend knife-edge; O4, O5, O7, O9, R2-O2, R3-O1 carried; the duty extension counts to the rate-cap-ended effective date, which the contract charter sets one day after the duty end.

## closing_checklist (revision_4)
- Written after the round-4 reveals; the revision_4 charter section was not edited after them.
- GT matched the blind derivation on every scored argument (500.00, 21,046.18, 1,673.17, 5,373.01; 500.00, 1,533.11), every baseline_result and all 32 sensitivities. Trees PASS (edges ep<-pd, eu<-ud now action form with justified fallback); unique solution PASS; overwrites declared (late_documents departure scoped to the reimbursement, sibling-naming).
- bl, ep, eu, bn meet every factor requirement; C9 and C10 stay closed; the 66 % floor and all eight schedule shares are gone.
- Not closed — complete member lists:
  - C1: pd baseline window sentence; pd_window_start fall-through; pd_window_days; ud baseline window sentence; ud_window_days.
  - C2: pd_policy_at_loss; pd_paying_coverage; pd_window_start; ud_policy_at_loss.
  - C4: pd (1 survivor, no method); ud (1 survivor, no method).
  - C11: task 0 rate_cap_ended 5dd5070e vs customers 553cc76e and persona; task 1 rate_cap_ended f0285d0b vs customers 0ecd9c06 and persona; both design_rationale §7 cap-end assertions.
  - C12: pd_closed_day (via plain pd_due); ud_closed_day (via plain ud_due).

VERDICT revision_4: task0=RED task1=RED charter=C1,C2,C4,C11,C12

## revision_5

### charter_global_frozen (revision_5)
- Frozen 2026-10-20T11:37:48Z, before any round-5 GT. Gate snapshot (`/tmp/erl0072_coord/snapshot.sh gap_waiver_cancellations_and_claims 5`, 2026-10-20T11:35:06): EXTENDED OK; TASK TOOL CONTRACT OK; REPLAY OK (--check); SOLVABILITY OK; COMPUTE OK; GROUNDING OK; SCOPE OK. worklog tail "REWORK round 5: gates 7/7 green".
- Views r5: 0.json 3c9a689362fb25502e98a8a7c353ba05fdebb144a7ea57f83f0e1957f54839d2 (task 0: customer duty end and persona changed only), 1.json dcf33899a44b59b2b7227c5465c0cc0c752410d932f8334b8a6caf89ff39f1f2 (task 1 re-treed and re-seeded). Sources: gap.extended.yaml e0ff62e96bbd16b9094e814cdfa15fa1ed8c58959805543be02a23ec4d88a900, task_tools.py 948f6956c8c533d5952bb086c3b44167eb225e7360bee1e1cb499b412479a75a — both changed, all charter sections re-derived. rework_claims_r5.md read (ids / prose).

### re-derived checks (r5)
- Base byte-identical. Six policies: pd, bl (now Premier-only), ep, bn, **bp (new gap_ext_plus_starting_balance, record_plus_claim_balance_at_loss_c4d2a91e, agent)**, eu (record_plus_claim_exclusions_41771560 now owner=user: "The borrower confirms … the itemized excluded amounts"). ud and its tool retired; no rule or tail still refers to a Plus reimbursement schedule (pd's tails now place Plus under the base deductible clause; checked every sentence naming Plus).
- compute_basis sweep: 0 non-verbatim, 0 unbased in all six; baselines and replaced_by verbatim; bl and bp retire the same base clause with self-naming, sibling-naming tails (XF-20). Ties stated in bp as in bl (C10 kept). New uuid8 c4d2a91e distinct from the five others; no factor id in a tool name; docstrings have no ordering words or example values; bodies are bare ctx.update.
- Prerequisites: ep<-pd (action), bn<-bl (state), bn<-ep (action) unchanged; **eu<-bp new**: "The Plus excluded total is not fixed until the claim carries a starting balance above 0.00." (state, value_input, gate eu_balance); the only writer of a Plus claim's balance is bp. Graph acyclic.
- **The eu<-bp edge carries no value (new class C13, SOURCE-CHAIN):** eu_balance enters eu only as `result: MN(RND(sum of six parts, 2), eu_balance)` ("it is never more than the starting balance the claim shows"). The six parts never approach a contract's balance at loss, so the cap binds only on the unwritten 0.00. Probed on the task-1 world: written balance 18,856.42, 5,000.00, 1,533.12, 100,000.00 -> excluded total 1,533.11 every time; only a balance of 0.00 changes it. The edge is a state gate labelled value_input: the tree tests ordering, not calculation (n = 1 needs >= 1 genuine value_input edge).
- C12 / C2 / C1 / C4 on pd: pd unchanged except the duty sentence (extension counts to the rate-cap-ended date "effective the day after the duty ended"); transitive scan: pd_closed_day still reads pd_window_start / pd_window_days / pd_duty_extension outputs through pd_due; bp clean (no transitive cross-factor read).
- bp factor ladders = accepted bl ladders (first_period, added_days parameters; due_change_count, capped_rate_adjustment methods; method tables as revision_2) — PASS structurally.

### findings (r5)
- **C1 — SOURCE-FACTOR RED (open; members):** pd baseline window sentence; pd_window_start fall-through ("otherwise the date of loss"); pd_window_days. (ud members retired with ud.)
- **C2 — SOURCE-FACTOR RED (open; members):** pd_policy_at_loss; pd_paying_coverage; pd_window_start. (ud_policy_at_loss retired.)
- **C4 — SOURCE-FACTOR RED (open):** pd — 1 surviving factor (duty_extension), no method.
- **C12 — SOURCE-FACTOR RED (open; member):** pd_closed_day (via plain pd_due).
- **C11 — SOURCE-FACTOR RED (open; member changed):** task-0 members closed (customers 553cc76e scra_active_duty_end_date 2026-08-19, cap ended 2026-08-20, persona "released August 19, 2026" — consistent with contract_scra_rate_cap); task-1 cap end now 2026-09-15 = day after 2026-09-14 (closed). **New member, task 1:** due-date change e147cfee (2025-12-10) moves the next due date 2025-12-25 -> 2026-01-23, 29 days; contract_due_date_change: "it may be no more than due_date_change_max_shift_days calendar days later than the current next_due_date" and Tier 3 Advantage carries due_date_change_max_shift_days 20 — the change the contract charter would refuse. bp_added_days (tier "more than 15 days") and bp_due_change_count rest on it.
- **C13 — SOURCE-CHAIN RED (new; member):** eu<-bp value_input edge (gate eu_balance) — decorative cap, above.
- Closed: all ud members of C1/C2/C4/C11/C12 (policy retired); C11 task-0 and task-1 cap-end members.
- Observations: the excluded-total write moving to the borrower ("confirms") is a plausible acknowledgment; O4, O5, O7, O9, R2-O2, R3-O1 carried.

## closing_checklist (revision_5)
- Written after the round-5 reveals; the revision_5 charter section was not edited after them.
- GT matched every scored argument (task 0: 500.00, 21,046.18, 1,673.17, 5,373.01; task 1: 18,856.42, 1,533.11), every baseline_result and all 32 sensitivities. Scopes disjoint (task 0 {pd, bl, ep, bn}; task 1 {bp, eu}) and complete over the six policies; graph acyclic; gates 7/7 green.
- Not closed — complete member lists:
  - C1: pd baseline window sentence; pd_window_start fall-through; pd_window_days.
  - C2: pd_policy_at_loss; pd_paying_coverage; pd_window_start.
  - C4: pd (1 surviving factor, no method).
  - C11: task 1 contract_servicing_events e147cfee (due-date change shifted 29 days, Tier 3 limit 20).
  - C12: pd_closed_day (via plain pd_due).
  - C13: eu<-bp edge (decorative cap; value_input in name only).
- Closed this round: every ud member (C1/C2/C4/C11/C12), C11 cap-end members in both tasks.

VERDICT revision_5: task0=RED task1=RED charter=C1,C2,C4,C11,C12,C13

## revision_6

### charter_global_frozen (revision_6)
- Frozen 2026-10-20T19:46:04Z, before any round-6 GT. Gate snapshot (`/tmp/erl0072_coord/snapshot.sh gap_waiver_cancellations_and_claims 6`, 2026-10-20T19:42:09): EXTENDED OK; TASK TOOL CONTRACT OK; REPLAY OK (--check); SOLVABILITY OK; COMPUTE OK; GROUNDING OK; SCOPE OK. worklog tail "REWORK round 6: gates 7/7 green".
- Views r6: 0.json 3c9a689362fb25502e98a8a7c353ba05fdebb144a7ea57f83f0e1957f54839d2 (identical to r5 — task 0 world and tree unchanged; the world-type ruling was not implemented, rework_claims_r6 "Task 0 — the world-type ruling is not implemented (blocker)"), 1.json 1e8d2fd98d8199b81517d581e246273ff4133febd09ec69e58bf210717f1abdd (task 1 re-treed and re-seeded from origination). Sources gap.extended.yaml ffdb219f30acb4bacf93803f37313854716e1e7935c25cd596f0afd2bbbebe6c, task_tools.py 3f8d8ae2b37fcd807e176e9da62d23baaf9022615a6ff0bae086f61da6f2d64c — both changed, all sections re-derived.
- Cross-product seed rows were checked against the published contract and vsc documents (env/env_0072_subprime_auto_lender/docs/contract, docs/vsc — the coordinator's brief allows it; no task file of another difficulty was read). No CPI documents are published; CPI rows were checked against blueprint/products/cpi.yaml.

### re-derived checks (r6)
- Base byte-identical. Policies: pd, bl (Premier), ep, bn (task 0, unchanged); bp (Plus starting balance) and **pb = gap_ext_plus_worksheet_benefit / accept_plus_claim_benefit_e7b3150d (owner=user)** (task 1). eu and record_plus_claim_exclusions_41771560 retired; no rule or tail names them (every Plus-naming sentence re-read).
- compute_basis sweep: 0 non-verbatim, 0 unbased in all six; baselines and replaced_by verbatim; superseded clauses verbatim. pb retires four base clauses (excluded items, VSC refund, force-placed premiums, ACV / deductible covered); bn and pb tails name each other on the shared ACV clause; ep and pb tails name each other on the three shared clauses (XF-20). pb keeps the base LTV excess and the base floor/cap/rounding clause in force and restates them exactly.
- New uuid8 e7b3150d distinct; no factor id in a tool name; docstrings clean; bodies bare ctx.update.
- Prerequisites: task 0 unchanged; task 1: pb <- bp "The Plus worksheet benefit is not worked out until the claim carries a starting balance above 0.00." (state, value_input, gate eu_balance). **C13 closed:** eu_balance is the benefit's first term and the LTV-excess share: on the task-1 world a balance 100.00 lower / higher moves the benefit by exactly −100.00 / +100.00 (927.96 / 1,127.96 vs 1,027.96). Graph acyclic.
- Factor structure: pb carries the six accepted exclusion factors (4 parameter, 2 method; method tables as revision_2); bp the four accepted starting-balance factors. Transitive scan: only pd_closed_day reads other factors.

### seed check against the published contract documents (both worlds, exhaustive)
Task 1 (GA, Tier 3, signed 2023-11-24), all consistent: late charges at 4.0 % ("GA … on or after 1 July 2023") with first-delinquency reductions 50 / 25 / none and no autopay reduction (ach_self_service): 7.43, 11.15, 14.86, 23.04; extension fees 20.00 each (state deferral schedule; collections-handling 3 and 2 days -> nothing; extended-deferral 1 and 2 -> nothing; no late charge on the next-due installment; no recovery history); both extensions offered (seasoning 13 / 25 paid; spacing none / one; insurance compliant, lapse notices in the window -> one / none -> max; payment activity 6 / 6; remaining term ≥ 13; delinquency next due on/after signing); due-date change 18 days within Tier 3's 20 (5 paid, 0 days past due); SCRA cap end the day after the 2026-09-14 duty end; no return seeded; VSC DriveSure Gold refund 2,295.00 x (1 − 1001/1461) = 722.59 − 385.00 − 50.00 = 287.59, issued 25 days after the effective date; CPI placement, proration (129.95), refund 96.62 (22 / 30 days) and notices per cpi.yaml.
Task 0 (OH, Tier 2, signed 2025-01-17), **not producible under the published contract documents** (members):
1. late charge 2025-09-08 on 2025-08-28: seeded 15.53; first-delinquency 50 % (no late charge in the rolling 12 months) + autopay 10 % (6 autopay drafts) -> 6.21;
2. late charge 2026-06-21 on 2026-06-10: seeded 15.53; 25 % (one prior) + 20 % (9 autopay drafts) -> 8.54;
3. late charge 2026-07-21 on 2026-07-10: seeded 15.53; none + 10 % (8 drafts) -> 13.98;
4. late charge 2026-08-21 on 2026-08-10: seeded 15.53; none + 10 % (7 drafts) -> 13.98 on the capped installment (24.91 on the restored one);
5. late charge 2026-09-21 on 2026-09-10: seeded 25.00; none + 10 % -> 24.91;
6. returned-payment fee 2026-01-02 on the returned autopay draft: seeded 25.00; failed-payment offset "recurring autopay draft, 5.00 is taken" (restriction review 1 of 3 -> nothing, subsequent-return none, NSF reason nothing, OH no state cap) -> 20.00;
7. extension 2025-09-12: seasoning allowance zero (installments paid MONTHS(2025-02-28, 2025-08-28) = 6, fewer than 12) -> "no agreement is offered";
8. extension 2026-04-20: spacing allowance zero (latest extension 2025-09-12 is later than the 12-month mark 2025-04-18 before the 2026-04-18 signing) -> no agreement.
These rows enter task 0's scored values: fees_due 96.59 carries members 2-5 and the extension fee of member 8; on the documents' late charges alone the fee part becomes 47.52 instead of 56.06 (ep 1,664.63 instead of 1,673.17, bn 5,381.55 instead of 5,373.01); the two extensions feed ep's deferral part and ep_deferral_count's tier.

### findings (r6)
- **C1 — SOURCE-FACTOR RED (open; members):** pd baseline window sentence; pd_window_start fall-through; pd_window_days.
- **C2 — SOURCE-FACTOR RED (open; members):** pd_policy_at_loss; pd_paying_coverage; pd_window_start.
- **C4 — SOURCE-FACTOR RED (open):** pd — 1 surviving factor, no method.
- **C12 — SOURCE-FACTOR RED (open; member):** pd_closed_day.
- **C11 — SOURCE-FACTOR RED (open; members now task 0 only):** the eight task-0 rows above. Task-1 member (29-day due-date change) closed; task 1 fully consistent with the published documents.
- **C13 closed.**
- Observations: task 0's draw problem (the reworker's blocker) is a structural decision outside this audit; O4, O5, O7, O9, R2-O2, R3-O1 carried; task 1 is tree-sound with a user-owned root (borrower accepts the benefit).

## closing_checklist (revision_6)
- Written after the round-6 reveals; the revision_6 charter section was not edited after them.
- GT matched every scored argument (task 0: 500.00, 21,046.18, 1,673.17, 5,373.01; task 1: 14,142.25, 1,027.96), every baseline_result and all 32 sensitivities. Scopes disjoint and complete (task 0 {pd, bl, ep, bn}; task 1 {bp, pb}); graph acyclic; gates 7/7 green.
- Task 1 passes all four relationships (closing items: tree n = 1 with a genuine value_input edge and a user-owned root; 6 + 4 factors meeting every count; seeds consistent with the published contract and vsc documents).
- Task 0 does not close. Open classes, complete member lists:
  - C1: pd baseline window sentence; pd_window_start fall-through; pd_window_days.
  - C2: pd_policy_at_loss; pd_paying_coverage; pd_window_start.
  - C4: pd (1 surviving factor, no method).
  - C11: task-0 contract rows — late charges 2025-09-08, 2026-06-21, 2026-07-21, 2026-08-21, 2026-09-21; returned-payment fee 2026-01-02; extensions 2025-09-12 and 2026-04-20.
  - C12: pd_closed_day.
- Closed this round: C13; the task-1 C11 member.

VERDICT revision_6: task0=RED task1=PASS charter=C1,C2,C4,C11,C12

## revision_7

### charter_global_frozen (revision_7)
- Frozen 2026-10-20T20:30:16Z, before any round-7 GT. Gate snapshot (`/tmp/erl0072_coord/snapshot.sh gap_waiver_cancellations_and_claims 7`, 2026-10-20T20:26:24): EXTENDED OK; TASK TOOL CONTRACT OK; REPLAY OK (--check); SOLVABILITY OK; COMPUTE OK; GROUNDING OK; SCOPE OK. worklog tail "REWORK round 7: gates 7/7 green".
- Views r7: 0.json 01681afd008247a0ce8e2aaa35dae255b32f76b7f2b8a9cb7725a3440095a71e (task 0 re-seeded from origination — fresh blind derivation), 1.json 1e8d2fd98d8199b81517d581e246273ff4133febd09ec69e58bf210717f1abdd (identical to r6). Sources: gap.extended.yaml 518464121e9b6cab79a16cdac99094ed1e5343cee9c91871fd84aeb8c65551c0 (changed; re-derived), task_tools.py 3f8d8ae2… (unchanged since r6; § revision_6 tool checks carried by hash). Task 1 confirmed unchanged: same view, bp and pb rules and compute re-run give 14,142.25 / 1,027.96 and identical sensitivities.

### re-derived checks (r7)
- Base byte-identical; compute_basis sweep 0 non-verbatim / 0 unbased in all six; baselines, replaced_by, superseded clauses verbatim. pd's late_documents overwrite and window machinery are gone; pd keeps only the deductible-basis overwrite. ep<-pd action-form fallback now cites the void tier ("the reimbursement is 0.00 when the deductible withheld exceeds the contract's allowance on a policy never put before the company") — justified (a 0.00 reimbursement leaves deductible_covered_usd as it stood). Other edges unchanged; graph acyclic.
- **Closed:** C1 window members (no window in pd), C2 (pd_policy_at_loss and pd_paying_coverage are now parameters; pd_window_start gone), C12 (pd_closed_day gone).
- **C11 closed:** task 0 re-seeded; every contract row checked against the published contract documents — late charges 5.34 / 8.02 / 10.69 / 18.24 (5 % of the 213.77 capped installment with first-delinquency 50 / 25 / none, then 5 % of the restored 364.75; self-service payments, no autopay reduction; the 150.00 partial credit sits on the 2026-06-10 installment and arrived after its charge); extensions 2025-05-14 (13 paid -> seasoning one; insurance one (lapse notices 2024-08 in the window); activity 5; delinquency 2 days -> one; Tier 2 first fee waived) and 2026-05-18 (spacing one; 24 paid; fee 25.00, collections-handling 8 days -> nothing, extended-deferral 2 -> nothing); due-date change 2024-08-02 19 days (Tier 2 limit 20, 5 paid, current); SCRA cap end 2026-09-01 = day after 2026-08-31; no return; VSC Powertrain Plus refund 1,595.00 x (1 − 912/1096) = 267.77 − 30.00 − 75.00 = 162.77 issued 28 days after the effective date; CPI lapse/placement re-banded to Plan B on 11,800.00, proration 78.76, refund 53.23 (20 / 30 days), Keystone proof rejected_deductible_too_high (1,000 > Plan B 500) with a deficient-proof notice — all per the charters.

### factor_ladders (r7, new factors)
| factor | effect | verdict |
| --- | --- | --- |
| pd_policy_at_loss | param | realistic (settling insurer's accepted proof; else its rejected declarations; else latest accepted) |
| pd_paying_coverage | param | realistic |
| pd_contract_allowance | param | **gated (C14)** — the allowance enters only through pd_allowance_test's cap tier: with pd_allowance_test at its fall-through the factor changes nothing on any world |
| pd_allowance_test | method | **reads another factor (C14)** — compute: pd_shape tests pd_named_n, a binding of pd_policy_at_loss; rule: "when the withheld deductible is above the contract's allowance", the quantity pd_contract_allowance sets |
| bl_placed_premiums | param | **tiers are one value (C3)** — compute pp_amount = MX(0, added − refunded) if refunded > 0 else (added if added > 0 else 0), which equals MX(0, added − refunded) on every state (refunds only exist with premiums): "every premium added" on its domain is the net figure with nothing credited, "nothing" on its domain is that figure with no premium — one formula, three labels |
| bl_account_interest | method | shape PASS (T1 adds the carried unpaid interest, T2 accrual, T3 none); **T1 unreal (C1)**: the starting balance is the scheduled principal "as if every installment had been paid on its due date" in substance (signed schedule), and T1 adds the account's actual unpaid interest from missed installments — interest a borrower who had paid on schedule would not owe, and which GAP excludes as delinquency, not covers; **second reading (C15)** below |
| bn floor (36-month line) | — | acceptable (80 % / 70 % / no floor; baseline 60 % under 36 months) |

- **C15 — second reading in bl_account_interest:** "The interest accrued is the contract's principal balance times the rate in force on the date of loss … times the calendar days from that payment to the date of loss". Compute reads principal_balance_usd as it stands today (12,825.78), after the post-loss service-contract refund credit of 2026-09-02 (162.77); the balance on which interest accrued from the 2026-07-28 payment to the 2026-08-05 loss was 12,988.55. Reading B gives a starting balance of 12,446.46 instead of 12,446.25.

Surviving factors (task 0): pd 2 (policy_at_loss, paying_coverage; both parameters, no method) — C4; bl 4 (first_period, added_days, due_change_count, capped_rate_adjustment); ep 6; bn 6. Task 1 unchanged (bp 4, pb 6).

### findings (r7)
- **C1 — SOURCE-FACTOR RED (open; member):** bl_account_interest tier "latest payment on or before the loss left interest unpaid" (carried unpaid interest added to a scheduled balance). Revision_6 members (pd windows) closed.
- **C3 — SOURCE-FACTOR RED (reopened; member):** bl_placed_premiums.
- **C4 — SOURCE-FACTOR RED (open):** pd — 2 surviving factors, no method.
- **C14 — SOURCE-FACTOR RED (new; members):** pd_contract_allowance (gated through pd_allowance_test, XF-6); pd_allowance_test (reads pd_policy_at_loss's pd_named_n and, in the rule, pd_contract_allowance's quantity, XF-1). Disclosed by the reworker as "known coupling".
- **C15 — SOURCE-POLICY RED (new; member):** bl_account_interest principal-balance reading.
- Closed: C2, C11, C12, the C1 window members; C13 stays closed; task 1 unchanged.

## closing_checklist (revision_7)
- Written after the round-7 reveals; the revision_7 charter section was not edited after them.
- GT matched every scored argument (task 0: 500.00, 12,446.25, 1,084.05, 2,728.59; task 1: 14,142.25, 1,027.96), every baseline_result and all 32 sensitivities. Scopes disjoint and complete; graph acyclic; gates 7/7 green; task 1 unchanged and PASS.
- Task 0 seeds now producible under the published contract and vsc documents and the cpi charter (C11 closed); trees PASS.
- Open classes, complete member lists:
  - C1: bl_account_interest tier "latest payment on or before the loss left interest unpaid".
  - C3: bl_placed_premiums (tiers one formula).
  - C4: pd (2 surviving factors, no method).
  - C14: pd_contract_allowance (gated through pd_allowance_test); pd_allowance_test (reads pd_named_n of pd_policy_at_loss and the allowance quantity).
  - C15: bl_account_interest — "the contract's principal balance" (today vs over the accrual period).
- Closed this round: C2, C11, C12, the pd window members of C1.

VERDICT revision_7: task0=RED task1=PASS charter=C1,C3,C4,C14,C15

## revision_8

### charter_global_frozen (revision_8)
- Frozen 2026-10-20T20:56:07Z, before any round-8 GT. Gate snapshot (`/tmp/erl0072_coord/snapshot.sh gap_waiver_cancellations_and_claims 8`, 2026-10-20T20:54:18): EXTENDED OK; TASK TOOL CONTRACT OK; REPLAY OK (--check); SOLVABILITY OK; COMPUTE OK; GROUNDING OK; SCOPE OK. worklog tail "REWORK round 8: gates 7/7 green".
- Views r8 identical to r7 (0.json 01681afd…, 1.json 1e8d2fd9…). gap.extended.yaml 6f3c48504351c7db553e69ca5460a1e3a96a8a0af06b5db42dbd52bf578cf9f0 changed (pd and bl rebuilt; ep, bn, bp, pb unchanged in effect); task_tools.py 3f8d8ae2… unchanged. tasks/1.json sha256 0c1b91ea… equal to round 7; bp / pb re-run 14,142.25 / 1,027.96 — task 1 unchanged.

### re-derived checks (r8)
- Base byte-identical; compute_basis sweep 0 non-verbatim / 0 unbased; baselines, replaced_by, superseded clauses verbatim; edges unchanged; transitive cross-factor scan of all six policies: clean.
- **C14 closed:** pd_contract_allowance removed; the borrower maximum (CPARAM borrower_max_deductible_usd) is pd_allowance_test's own binding; the count of proofs naming the settling insurer (pd_named_n) is a plain binding stated once ("A proof names the insurer that settled the claim when the insurer it shows is the insurer the claim shows as the primary insurer, whatever the result of its review") and read by both pd_policy_at_loss and pd_allowance_test (XF-2 pattern). pd_allowance_test all pairs PASS (cap = MN(core, maximum); void = 0; none = core).
- **C3 closed:** bl_placed_premiums is now three distinct formulas (net of refunds credited / net of the pending prorated refund / gross), baseline gross; all pairs PASS.
- **C1 (bl member) closed:** the carried-unpaid-interest tier is gone; bl_payment_interest = per-diem from the latest payment to the loss at the rate in force, split at a rate-cap change, else none; shapes PASS (T2 adds a split). Realism: scheduled principal plus per-diem from the latest actual payment is accepted as the "interest to the date of loss" convention (observation R8-O1: for an account whose last payment is several months before the loss this accrual spans the missed installments).
- **C15 closed:** "Interest accrues on the principal in place over that period, which is the principal balance the contract carries with every service-contract refund credited for the total loss added back (those credits post after the date of loss)" — compute adds the vsc_refund ancillary credits when the service contract was cancelled for total_loss; one reading (task 0: 12,825.78 + 162.77 = 12,988.55). Observation R8-O2: other post-loss principal credits are not added back (none in either world).

### factor_ladders (r8, pd)
| factor | effect | verdict |
| --- | --- | --- |
| pd_policy_at_loss | param | realistic |
| pd_paying_coverage | param | realistic |
| pd_allowance_test | method | realistic (cap at the CPI plan's borrower maximum; void for a policy never put before the company); shape PASS |
| pd_deductible_counted | param | **unreal fall-through and straw-man baseline (C1)** |

pd_deductible_counted / pd baseline: the baseline states "The deductible the Premier reimbursement counts is the lower of the comprehensive and collision deductibles on the latest proof the tracking record shows as accepted", and the factor's fall-through repeats it for a claim "with no settlement figures yet". Under that standard a deductible is reimbursed whether or not the insurer withheld one, up to the proof's figure — the base charter's own basis is "the deductible the primary insurer actually deducted, up to deductible_reimbursement_max_usd", and no GAP administrator reimburses a deductible the settlement did not charge (the factor's own middle tier concedes it: "settlement figures and no deductible withheld, 0.00"). The record-backed term ("the deductible withheld") has been moved into a tier so that the standard method can be a figure no business uses. Members: the pd baseline sentence; pd_deductible_counted's fall-through tier.

Surviving pd factors: policy_at_loss, paying_coverage, allowance_test = 3 (2 parameter, 1 method) — **C4** below the 4-factor floor. bl 6, ep 6, bn 6, bp 4, pb 6 — all meet the floor.

### findings (r8)
- **C1 — SOURCE-FACTOR RED (open; members):** pd baseline sentence "The deductible the Premier reimbursement counts is the lower of the comprehensive and collision deductibles on the latest proof …"; pd_deductible_counted fall-through "otherwise (no settlement figures yet)". (bl_account_interest member closed.)
- **C4 — SOURCE-FACTOR RED (open):** pd — 3 surviving factors.
- Closed: C3, C14, C15, the bl member of C1. C2, C11, C12, C13 stay closed.

## closing_checklist (revision_8)
- Written after the round-8 reveals; the revision_8 charter section was not edited after them.
- GT matched every scored argument (task 0: 500.00, 12,363.73, 1,084.05, 2,646.07; task 1: 14,142.25, 1,027.96), every baseline_result and all 32 sensitivities; trees PASS; no second reading; seeds producible; scopes disjoint and complete; gates 7/7 green; task 1 unchanged and PASS.
- Open classes, complete member lists:
  - C1: pd baseline sentence "The deductible the Premier reimbursement counts is the lower of the comprehensive and collision deductibles on the latest proof the tracking record shows as accepted, and 0.00 with no accepted proof"; pd_deductible_counted fall-through tier ("otherwise (no settlement figures yet)").
  - C4: pd (3 surviving factors against the 4-factor floor).
- Closed this round: C3, C14, C15, the bl_account_interest member of C1.

VERDICT revision_8: task0=RED task1=PASS charter=C1,C4

## revision_9

### charter_global_frozen (revision_9)
- Frozen 2026-10-20T21:35:15Z, before any round-9 GT. Gate snapshot (`/tmp/erl0072_coord/snapshot.sh gap_waiver_cancellations_and_claims 9`, 2026-10-20T21:33:59): EXTENDED OK; TASK TOOL CONTRACT OK; REPLAY OK (--check); SOLVABILITY OK; COMPUTE OK; GROUNDING OK; SCOPE OK. worklog tail "REWORK round 9: gates 7/7 green".
- Views r9 identical to r7/r8 (0.json 01681afd…, 1.json 1e8d2fd9…). gap.extended.yaml 2b38fdb55c73667554fe6110bea5103d7ef6afb392a228e31086a47b85b71f1e (changed: pd only); task_tools.py 3f8d8ae2… unchanged; tasks/1.json 0c1b91ea… unchanged; bp / pb re-run 14,142.25 / 1,027.96 — task 1 unchanged.

### re-derived checks (r9)
- Base byte-identical; compute_basis sweep 0 non-verbatim / 0 unbased in all six; baselines, replaced_by, superseded clauses verbatim; edges unchanged (ep<-pd action form, fallback the void tier); transitive cross-factor scan of all six policies clean (plain bindings pd_d_coll / pd_d_comp combine the two declaration factors' outputs — assembly, XF-3).
- **C1 (pd members) closed:** the baseline is now the base's own figure with a declarations check that can only lower it: "the deductible the primary insurer actually deducted, as the claim's deductible withheld shows it, up to the plan's deductible_reimbursement_max_usd and never more than the declared deductible when that is above 0.00 … a deductible the insurer did not withhold is never reimbursed"; the standard declarations are "the latest proof the tracking record shows as accepted for the insurer of the policy on file". pd_deductible_counted removed; nothing-withheld -> 0.00 under every tier (probed).
- **C4 closed:** pd has 4 honest factors — pd_policy_at_loss (param: settling insurer / any insurer with no policy on file / policy on file), pd_proof_standing (param, cpi: settling insurer's latest proof rejected_deductible_too_high -> its declarations whatever the result; rejected otherwise -> none; else accepted, falling back to the policy on file), pd_paying_coverage (param), pd_allowance_test (method, all pairs PASS). Each acts on a baseline quantity (whose declarations / which proof / which deductible / the allowance shape); none reads another's bindings; ties stated ("the one with the latest review date, and where two were reviewed on that date the one recorded first counts"); multi-source (pd_allowance_test: withheld vs plan maximum vs proofs naming the insurer); cross-difficulty (cpi).
- Realism: all four pd factors are record-backed GAP deductible terms (policy that paid, its declarations' standing, the coverage that paid, the contract's permitted deductible). Observation R9-O1: a proof rejected for a reason other than its deductible leaves no declarations check, so the withheld deductible is reimbursed up to the plan maximum (more than an accepted proof might allow) — a defensible "unverifiable declarations are not used" term.
- XF-1…31 re-checked on all six policies: no member found.

### findings (r9)
- No open charter-wide RED. Closed: C1 (last members), C4. C2, C3, C11–C15 stay closed.
- Observations carried: O2, O4, O5, O7, O9, R2-O2, R3-O1, R8-O1, R8-O2, R9-O1.

## closing_checklist (revision_9)
- Written after the round-9 reveals; the revision_9 charter section was not edited after them.
- Per-task files 0.md / 1.md correspond one-to-one with tasks/0.json and tasks/1.json, every revision preserved; both revision_9 comparisons PASS.
- Extended policies fully covered: task 0 {gap_ext_premier_deductible_reimbursement, gap_ext_claim_starting_balance, gap_ext_premier_excluded_amounts, gap_ext_claim_worksheet_benefit}, task 1 {gap_ext_plus_starting_balance, gap_ext_plus_worksheet_benefit}; scopes pairwise disjoint; six task tools, each with an independent frozen uuid8 (7815b2b6, 15fb7d99, 258c7293, 931d4ebc, c4d2a91e, e7b3150d); GT closed over them.
- Trees: task 0 — 3 prerequisite problems, 3 value_input edges, owner=user problem (Premier reimbursement); task 1 — 1 prerequisite problem, 1 genuine value_input edge, owner=user root (borrower accepts the benefit); whole-difficulty graph acyclic.
- Factors: every computation declares a self-sufficient baseline and 4-6 factors (pd 4: 3 param / 1 method; bl 6: 2 / 4; ep 6: 4 / 2; bn 6: 5 / 1; bp 4: 2 / 2; pb 6: 4 / 2); every ladder 3 tiers stated in its rule, distinct in outcome, record-backed; each factor proved to bear weight on its task's world; all-baseline figures definite and different from gold (task 0: 250.00, 11,565.51, 2,273.74, 4,179.68; task 1: 12,808.42, 0.00); multi-source and cross-difficulty factors present in both tasks.
- Seeds producible under the published contract and vsc documents and the cpi charter in both worlds.
- Instantiation gates on the final form: coordinator snapshot round 9 — 7/7 green (cited above; check_traceability left to the post-render stage per the brief).

VERDICT revision_9: task0=PASS task1=PASS charter=CLEAN

## revision_10

### charter_global_frozen (revision_10)
- Frozen 2026-10-20T22:10:49Z, before any round-10 GT. Gate snapshot (`/tmp/erl0072_coord/snapshot.sh gap_waiver_cancellations_and_claims 10`, 2026-10-20T22:09:22): EXTENDED OK; TASK TOOL CONTRACT OK; REPLAY OK (--check); SOLVABILITY OK; COMPUTE OK; GROUNDING OK; SCOPE OK. worklog tail "REWORK round 10: gates 7/7 green".
- Views r10 identical to r9. Sources: gap.extended.yaml 8cef85fe8ec2ae10b9a8e2c72b1d81633483a674efa558aa58a406bc056fc2f6, task_tools.py b862ea9de87cb3e0651ae724ce3ffd7b2181c9a777829fdbbc374def20b29bd0 (both changed; re-derived). Read: audits/render_source/gap_waiver_cancellations_and_claims/render_r1.md (renderer stop on S1-S3 and a docstring note) and rework_claims_r10.md.
- Revision_9 missed S1-S3; recorded here as the gap in that round's sweep (sibling-tail scan did not compare the Premier LTV tail with the Plus excess sentence; the single-change accrual sentence was not probed with two changes in the window; the fee-window month-end edge was not probed).

### render items (r10)
- **S1 closed.** gap_ext_plus_worksheet_benefit now retires "less the portion above max_ltv_covered_pct (gap_msr_excess_ltv_amount)" itself ("On a Plus worksheet claim the benefit is reduced by the loan-to-value excess set here, figured on the starting balance the claim shows … a GAP Waiver Premier 150 claim is reduced by the Premier worksheet benefit's own loan-to-value excess, and a claim on any other plan is still reduced by the portion above max_ltv_covered_pct, amortized in the same proportion as the scheduled balance"); the Premier tail names the Plus case. Exhaustive sibling sweep over every base clause retired by more than one policy (scripted): scheduled-balance clause (bl, bp), excluded-items clause (ep, pb), VSC-refund clause (ep, pb), force-placed-premium clause (ep, pb), LTV clause (bn, pb), ACV / deductible-covered clause (bn, pb) — every tail names its own case, the sibling's case and the remaining plans; the deductible-basis clause is retired by pd alone and its tail keeps Plus on the base. No undeclared departure remains (D.20-22).
- **S2 closed.** Rule: "each calendar day from that payment to the date of loss accrues at the rate in force on it, which is the cap's rate on the days from the cap's effective date up to the day before its end took effect and the original annual percentage rate on every other day". Compute: capped days = DAYS(max(payment, cap start), min(cap end, loss)) when positive, APR on the rest. Probed: the renderer's witness (payment Jan 10, cap Mar 1 – Jul 1, loss Sep 1) -> 122 days at the cap, 112 at the APR, as the rule reads; single-change cases, cap ended before the payment, cap starting after the loss and a cap live throughout all give the rule's figure. Sweep of every other SCRA-window ladder (bl/bp capped-rate adjustment: live / ended / none incl. start-and-end inside the schedule; ep/pb past-due and deferral installment amounts: each tier states its cap configuration with an explicit fall-through) — none assumes a single change.
- **S3 closed.** Every policy that counts months (bl, ep, bn, bp, pb; pd counts none) now carries "Whole months from one date to a later one are the difference in calendar months between them, less one when the later date's day of the month is below the earlier date's" — exactly MONTHS(). The fee-part window is stated as computed. The renderer's month-end witness needs a 29th-31st due day, which no contract can carry (published contract documents: allowed due days "1st to 28th" at every tier), so no producible state separates the window from "fell due after the date of loss".
- **Docstring note closed.** All six amount parameters read "kept to 2 decimal places (rounded to the cent)", matching round(float(x), 2); names, owners, signatures and bodies unchanged (checked line by line).

### re-derived checks (r10)
- Base byte-identical; compute_basis sweep 0 non-verbatim / 0 unbased in all six; baselines, replaced_by, superseded clauses verbatim; edges unchanged; transitive cross-factor scan clean; uuid8s unchanged; all XF points re-checked with no member.
- Figures unchanged (task 0: 500.00 / 12,363.73 / 1,084.05 / 2,646.07; task 1: 14,142.25 / 1,027.96), every sensitivity unchanged.

### findings (r10)
- No open charter-wide RED. S1, S2, S3 and the docstring note closed.

## closing_checklist (revision_10)
- Written after the round-10 reveals; the revision_10 charter section was not edited after them.
- Render-source items S1, S2, S3 and the docstring note closed; each class swept over all six policies with no remaining member.
- All revision_9 closing items still hold (coverage, disjoint scopes, independent uuid8s, trees, factor counts and weight, honest baselines, producible seeds); figures and sensitivities unchanged; gates 7/7 green (round-10 snapshot).

VERDICT revision_10: task0=PASS task1=PASS charter=CLEAN

## revision_11

### charter_global_frozen (revision_11)
- Frozen 2026-10-21T00:28:24Z, before any round-11 GT. Gate snapshot (`/tmp/erl0072_coord/snapshot.sh gap_waiver_cancellations_and_claims 11`, 2026-10-21T00:25:07): EXTENDED OK; TASK TOOL CONTRACT OK; REPLAY OK (--check); SOLVABILITY OK; COMPUTE OK; GROUNDING OK; SCOPE OK. worklog tail "REWORK round 11: gates 7/7 green".
- Views r11: 0.json 8bdb40a3427ed25d5a69f31c3c1b674cc1f8269fa2c9539a7b9c7e1e26d718d0 (task 0: CPI record e043d3e3 status compliant -> lapse_notice, lapse_date 2026-09-18, new first_lapse_notice c409e53b 2026-09-21; nothing else), 1.json 1e8d2fd9… (unchanged). Sources: gap.extended.yaml a718751875355d3a83095d05eec2cf7ad2a4a84d6684f7c316c7469ab0b78375 (pd only), task_tools.py b862ea9d… (unchanged). tasks/1.json 0c1b91ea… unchanged. Read: audits/policy_kb/gap_waiver_cancellations_and_claims/_difficulty.md (kb_round1: P1, S1, S2), rework_claims_r11.md, published docs/cpi.
- Gap in revision_10 recorded: P1 (factor sentence referring to the insurer another factor selects; two factors reusing one naming-proof test) and S2 (CPI status after expiry) were not caught by my sweeps; S1 is not a defect (below).

### KB items (r11)
- **S1 — not a defect, closed.** gap.yaml lifecycle: claim_open -> active "by agent … The claim is withdrawn because the vehicle was repaired", event gap_claim_withdrawn targets gap_addenda (a status transition) and gap_activities' event_type enum carries no withdrawal value; so the March claim row 7297a6ca stays as filed, the addendum returns to active, and the 2026-08-19 filing on an active addendum reopens claim_open — producible as seeded.
- **S2 closed.** Buckeye policy on file expires 2026-09-18 with no accepted replacement (Keystone proof rejected 2026-04-06): docs/cpi "a policy expiration with no renewal proof" establishes the lapse; record now lapse_notice, first lapse notice 2026-09-21 (within 5 days); second notice not before 2026-10-06 and placement not before 2026-10-21, both after the frozen 2026-10-05 — correctly unseeded. No GAP computation reads the record's status or lapse notices (scripted binding scan); the policy on file (insurer, number) is unchanged, so pd's reads are unaffected. Observation R11-O1: lapse_date is set to the policy expiration date itself; the docs define it as "the first day without acceptable coverage", which reads as the day after an end-of-day expiry — no GAP figure reads it.
- **P1 closed.** pd_proof_standing now decides only "which proofs count" (any result when the settling insurer's latest proof was rejected_deductible_too_high; none when rejected otherwise; else accepted only), with no reference to another factor's insurer; the combination is one plain sentence ("The declarations the Premier deductible reimbursement reads are those on the latest proof that counts of the insurer whose declarations are read; when that insurer has no proof that counts, those on the latest accepted proof of the policy on file; when no proof counts, none are read"); pd_policy_at_loss (pd_ins_n) and pd_allowance_test (pd_put_n) each own their count of naming proofs, with the definition "A proof names the insurer that settled the claim when …" stated once as plain text. Compute matches each sentence (both branches and both fallbacks probed). Transitive scan clean.

### sweeps (r11, exhaustive over both worlds and all six policies)
- Lifecycle-record class (S1): every seeded status transition checked for a producing record or a record-less transition the charter allows — task 0: March claim withdrawal (record-less, allowed), two CPI placements cancelled by accepted proof with cancellation notices, extensions under signed requests, SCRA cap under a signed request; task 1: CPI placement cancelled with notice, extensions and SCRA under signed requests, VSC cancelled for the total loss with its refund row. None missing.
- Cross-category status class (S2): every cross-category holding's status at the frozen time checked against its charter clock — task 0: contract active (101 days past due < 120 charge-off), CPI lapse_notice (above), VSC cancelled/refunded; task 1: contract active (116 days < 120), CPI compliant (Peach State renewal in force to 2027-07-05), VSC cancelled/refunded. Published cpi docs: open-record reviews follow the base standard (re-review allowances apply only on closed records), so both worlds' acceptances/rejections, notices, premiums (78.76 / 79.85; 129.95 / 131.75) and refunds (53.23; 96.62 — clause 5's refundable-days formula from the proof's effective date) are producible.
- Factor-independence class (P1): all 32 factors re-checked for a factor sentence naming another factor's selected quantity and for shared tests: none remains (pd above; bl/bp SCRA and due-date reads are each factor's own; ep/pb cap reads are each factor's own).
- Figures unchanged (task 0: 500.00 / 12,363.73 / 1,084.05 / 2,646.07; task 1: 14,142.25 / 1,027.96); all sensitivities unchanged; base byte-identical; compute_basis, overwrites, prerequisites verbatim.

### findings (r11)
- No open charter-wide RED. P1, S2 closed; S1 not a defect.

## closing_checklist (revision_11)
- Written after the round-11 reveals; the revision_11 charter section was not edited after them.
- KB items P1 and S2 closed, S1 shown producible as seeded; lifecycle-record, cross-category-status and factor-independence classes swept over both worlds and all six policies with no remaining member.
- All revision_9/10 closing items still hold; figures and sensitivities unchanged; gates 7/7 green (round-11 snapshot).

VERDICT revision_11: task0=PASS task1=PASS charter=CLEAN

## revision_12

### charter_global_frozen (revision_12)
- Frozen 2026-10-21T00:58:57Z, before any round-12 GT. Gate snapshot (`/tmp/erl0072_coord/snapshot.sh gap_waiver_cancellations_and_claims 12`, 2026-10-21T00:57:03): EXTENDED OK; TASK TOOL CONTRACT OK; REPLAY OK (--check); SOLVABILITY OK; COMPUTE OK; GROUNDING OK; SCOPE OK. worklog tail "REWORK round 12: gates 7/7 green".
- Views r12 identical to r11. gap.extended.yaml 59514d7fed41b67cdb7a4dd3495f70fe0aac428bca18a5b3c8667b325837d177 (pd only), task_tools.py b862ea9d… unchanged, tasks/1.json 0c1b91ea… unchanged. Read: KB revision_2 (K1, S3) and rework_claims_r12.md.

### K1 / S3 (r12)
- **S3 closed:** pd_proof_standing and the round-11 combination sentence are gone; pd_policy_at_loss is one merged selection (the settling insurer's latest naming proof when accepted or rejected_deductible_too_high; none when rejected otherwise; else the policy on file's latest accepted proof = baseline). No rule sentence assembles two factors' outputs; the three bounds combine as "never more than" sentences (commutative minima). Scripted direct and transitive cross-binding scan of all six policies: clean. (K1 is a KB-document item; its source cause S3 is closed.)

### new pd factors (r12)
- pd_policy_disclosure (method) — tiers: settling insurer's latest proof reviewed on or before the loss -> "not barred"; reviewed only after it -> never more than the borrower maximum; no naming proof -> nothing (= the new baseline sentence "As the standard, a withheld deductible above the borrower maximum deductible … is not reimbursed"). Shapes PASS. Realism: accepted as a disclosure term (observation R12-O1: voiding the whole reimbursement as the standard for any deductible above the contract maximum is harsher than the common "covered up to the required maximum").
- **pd_allowance_test (method) is now gated through pd_policy_disclosure (C14, XF-1/5/6).** Its rule sentence "How the borrower maximum bounds a withheld deductible above it follows how the latest proof naming the insurer that settled the claim was reviewed …" bounds the reimbursement of a deductible that the baseline says "is not reimbursed"; it has an effect only where pd_policy_disclosure lifts that bar to "not barred" (its T1). Probes on task 0: with pd_policy_disclosure at its baseline, pd_allowance_test's cap tier and its no-bound tier both give 0.00 (and every world with withheld > maximum gives 0.00 whatever pd_allowance_test's tier); with pd_policy_disclosure at its middle tier (proof re-dated after the loss) the result is 500.00 with pd_allowance_test at its tier or at its baseline. pd_allowance_test therefore acts on no quantity the baseline defines — the C9 / C14 pattern.
- Surviving pd factors: pd_policy_at_loss, pd_paying_coverage, pd_policy_disclosure = 3 (2 parameter, 1 method) — **C4**.

### findings (r12)
- **C14 — SOURCE-FACTOR RED (reopened; member):** pd_allowance_test (gated through pd_policy_disclosure's "not barred" tier).
- **C4 — SOURCE-FACTOR RED (reopened):** pd — 3 surviving factors.
- Closed: S3 (combination sentence), P1 stays closed. No sentence in any of the six policies combines factor outputs or names another factor's quantity apart from the gating above.
- Figures unchanged (task 0: 500.00 / 12,363.73 / 1,084.05 / 2,646.07; task 1 unchanged).

## closing_checklist (revision_12)
- Written after the round-12 reveals; the revision_12 charter section was not edited after them.
- GT matched every scored argument, baseline and sensitivity in both tasks; task 1 unchanged and PASS; trees, seeds, overwrites and prerequisites as revision_11.
- Open classes, complete member lists:
  - C14: pd_allowance_test (gated through pd_policy_disclosure).
  - C4: pd (3 surviving factors: pd_policy_at_loss, pd_paying_coverage, pd_policy_disclosure).
- Closed this round: KB S3 (combination sentence).

VERDICT revision_12: task0=RED task1=PASS charter=C4,C14

## revision_13

### charter_global_frozen (revision_13)
- Frozen 2026-10-21T01:18:22Z, before any round-13 GT was read (a GT extract was written to /tmp/audit_gap_0072/gt_r13_peek_DO_NOT_USE.txt by mistake before this freeze; it was not opened until after the freeze — disclosed). Gate snapshot (`/tmp/erl0072_coord/snapshot.sh gap_waiver_cancellations_and_claims 13`, 2026-10-21T01:16:44): EXTENDED OK; TASK TOOL CONTRACT OK; REPLAY OK (--check); SOLVABILITY OK; COMPUTE OK; GROUNDING OK; SCOPE OK. worklog tail "REWORK round 13: gates 7/7 green".
- Views r13 identical to r12; gap.extended.yaml 846540be2b3a8e7e8b5f181208bf2625b1a64600085dc6cd73d876aeec5cfc9f (pd only); task_tools.py b862ea9d… and tasks/1.json 0c1b91ea… unchanged.

### pd (r13)
- Baseline softened (no standard bar): withheld deductible up to the plan maximum, never more than the declared deductible of the latest accepted proof (lower of its two). The borrower maximum and "a proof names the settling insurer" are plain sentences stated once. No sentence combines factor outputs or names another factor's selection (K1/S3 class: none); scripted cross-binding scan clean.
- Factors: pd_policy_at_loss (param), pd_paying_coverage (param), pd_allowance_test (method: cap at the borrower maximum / void for a policy never put before the company / no bound), pd_policy_disclosure (method: reviewed on or before the loss -> the insurance on file does not bound; reviewed only after -> never more than the borrower maximum; no naming proof -> never more than the policy on file's lower deductible = its baseline).
- **All-pairs inertness probe on task 0 (run here):** each factor alone at its baseline moves the result (250.00 / 250.00 / 1,000.00 / 250.00 vs 500.00); but with any single other factor at its baseline the factor is inert in 9 of the 12 ordered pairs (only pairs with pd_allowance_test at baseline let the other three move), and every factor is inert solo (each alone on the computation standard: 250.00 = the all-baseline 250.00). World-specific inertness of a lesser-of-caps term is not by itself a defect, but one member is structural:
- **pd_policy_disclosure contributes nothing on its own against the baseline on any producible world (XF-1, C14).** With the other three factors at their baselines the declarations read are the latest accepted proof, its lower deductible caps the reimbursement, and the disclosure tiers cannot move that figure: the fall-through ("never more than the lower of the comprehensive and collision deductibles on the latest accepted proof of the policy on file") is the same cap on every open tracking record (the policy on file is the latest accepted proof — the reworker's own disclosure), the first tier lifts only that duplicate cap, and the middle tier's borrower maximum is never below an accepted proof's deductibles (acceptance requires deductibles no higher than the plan's borrower maximum). Its effect therefore exists only through another factor's tier (pd_policy_at_loss reading a non-standard proof, or pd_paying_coverage raising the declared figure) — the gating class of C9 / C14. Its fall-through also states a cap that baseline.rule does not contain.
- Surviving pd factors: pd_policy_at_loss, pd_paying_coverage, pd_allowance_test = 3 — **C4**.

### findings (r13)
- **C14 — SOURCE-FACTOR RED (open; member):** pd_policy_disclosure (no solo effect against the baseline on any producible world). pd_allowance_test's revision_12 gating closed (its void and cap tiers now act on the baseline's withheld deductible).
- **C4 — SOURCE-FACTOR RED (open):** pd — 3 surviving factors.
- Other five policies and task 1 unchanged and clean.

## closing_checklist (revision_13)
- Written after the round-13 reveals; the revision_13 charter section was not edited after them.
- GT matched every scored argument, baseline and sensitivity in both tasks; task 1 unchanged and PASS; K1/S3 class clean in all six policies.
- Open classes, complete member lists:
  - C14: pd_policy_disclosure (no solo effect against the baseline; duplicates the baseline's declarations cap in its fall-through).
  - C4: pd (3 surviving factors: pd_policy_at_loss, pd_paying_coverage, pd_allowance_test).
- Closed this round: pd_allowance_test's gating through pd_policy_disclosure.

VERDICT revision_13: task0=RED task1=PASS charter=C4,C14

## revision_14

### charter_global_frozen (revision_14)
- Frozen 2026-10-21T01:25:10Z, before any round-14 GT. Gate snapshot (`/tmp/erl0072_coord/snapshot.sh gap_waiver_cancellations_and_claims 14`, 2026-10-21T01:23:39): EXTENDED OK; TASK TOOL CONTRACT OK; REPLAY OK (--check); SOLVABILITY OK; COMPUTE OK; GROUNDING OK; SCOPE OK. worklog tail "REWORK round 14: gates 7/7 green".
- Views r14 identical to r13; gap.extended.yaml 43a560911da6fbeeb99b9702128ce2c47f522d259eab69160b4788a5782dd093 (pd only); task_tools.py b862ea9d… and tasks/1.json 0c1b91ea… unchanged (bp 14,142.25 / pb 1,027.96 re-run).

### pd (r14)
- pd_policy_disclosure removed; new pd_loss_schedule (parameter, reads the claim's loss type only): collision total loss -> the plan's deductible_reimbursement_max_usd (1,000.00); unrecovered theft -> 500.00 (theft_reimbursement_max_usd); comprehensive total loss or no loss type -> 250.00 (comprehensive_reimbursement_max_usd) = the baseline sentence "As the standard, the reimbursement maximum is the figure the Harborline GAP Waiver Premier 150 deductible reimbursement schedule sets for a comprehensive loss, 250.00". It replaces a baseline quantity (the reimbursement maximum) directly; tiers distinct; values are policy params; edge (no loss type) stated. Realism: accepted — a published per-loss-type deductible schedule under the plan's 1,000.00 ceiling is a company term (observation R14-O1: lower maxima for comprehensive and theft than for collision is a plan design choice, not a common industry default). Declared under the retired deductible-basis clause; the base parameter's meaning ("Largest primary-insurance deductible the benefit also covers") still holds (collision tier = 1,000.00).
- **Acceptance tests run here:**
  - T1 (task world, one factor at its baseline): pd_policy_at_loss 250.00, pd_paying_coverage 250.00, pd_allowance_test 1,000.00, pd_loss_schedule 250.00 vs 500.00 — all move.
  - T2 (producible variant of task 0, other three at baseline, factor at its taken tier vs all-baseline): pd_loss_schedule — latest accepted proof 500 / 500 (within Plan B's 500 maximum), withheld 500.00: 500.00 vs 250.00; pd_policy_at_loss — the settling insurer's earlier accepted proof 100 / 100 with a later accepted proof of another insurer at 250: 100.00 vs 250.00; pd_paying_coverage — latest accepted proof collision 200 / comprehensive 100, collision loss: 200.00 vs 100.00; pd_allowance_test — claim's insurer never put before the company, withheld 1,000 > 500: 0.00 vs 250.00. All four pass.
  - Pair inertness on the task world itself remains (lesser-of-caps: e.g. any of three factors at baseline makes the 250.00 standard bind), but no factor is structurally inert: each has a world where it moves alone against the standard. C14 (pd_policy_disclosure) closed by removal.
- K1/S3 class: no sentence combines factor outputs or names another factor's selection; the reimbursement maximum, the declarations read, the declared deductible and the borrower maximum are each a baseline-defined or plain quantity that one factor replaces or tests. Scripted scans of all six policies: compute_basis verbatim, overwrites verbatim, no direct or transitive cross-factor read, no factor id in a tool name.
- Factor counts: pd 4 (3 parameter, 1 method), bl 6, ep 6, bn 6, bp 4, pb 6 — every policy meets the floor; multi-source and cross-difficulty present in both tasks.

### findings (r14)
- No open charter-wide RED. C14 and C4 closed.

## closing_checklist (revision_14)
- Written after the round-14 reveals; the revision_14 charter section was not edited after them.
- GT matched every scored argument (task 0: 500.00, 12,363.73, 1,084.05, 2,646.07; task 1: 14,142.25, 1,027.96), every baseline and all 32 sensitivities; trees, seeds, overwrites, prerequisites and scopes as revision_11; gates 7/7 green.
- Every reimbursement factor passes T1 and T2 (verified here); no factor reads another's binding or is structurally inert; no combination sentence; every policy meets the factor floor with honest baselines.

VERDICT revision_14: task0=PASS task1=PASS charter=CLEAN
