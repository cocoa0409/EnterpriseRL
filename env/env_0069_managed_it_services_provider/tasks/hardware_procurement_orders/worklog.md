# worklog hardware_procurement_orders
- draws: t0 prereq=2 factors=[4,5,4]; t1 prereq=3 factors=[5,5,6,6]
- plan.md written (design + constraints)
- T0 policies appended (C_end, Q_retype, D_end)
- symptom: check_compute cross-category floor looks up the target holding in initial_state; the approval targeted an order created by the re-quote -> red. root cause: target holdings must pre-exist. change: the staged alternative quote is seeded (issued with the plain quote); the agent's write REVISES it (computation still targets the cancelled order whose fee it credits). tool renamed to revise_staged_quote_eb003c71.
- T0 gates: extended/tools/replay/solvability/compute/grounding/cross_fire run (see below)
- T0 closed: all per-task gates green; rationale written
- T1 design written to plan.md (network upgrade tree)
- T1 written (policies, tools, seed, contract, rationale); per-task gates green
INSTANTIATE round 1: gates 7/7 green
- round 2 started: plan appended to plan.md
- round 2: policies P1-P7 rewritten (CG-1..4, realism replacements, security removed); reissue tool takes unit_price_usd

## round 2 — probe table (XF 11/13/14; scratch copies of initial_state, value of the policy on that copy)
| probe | rule tier exercised | scratch result |
|---|---|---|
| T0 P1 base | seeded world | 543.07 |
| T0 P1 decoy closed Premier agreement listed first | CFIELD status=active excludes the closed agreement -> same tier as base | 543.07 |
| T0 P1 absent ClearPath agreement | no active agreement -> fall-through rate / COGS build / no relief | 641.84 |
| T0 P3 base (opening, staged quote 5393.40) | seeded world | 1667.83 |
| T0 P3 decoy closed agreement with seat rate 300 x 99 | CFIELD status=active excludes the closed agreement -> same tier as base | 1667.83 |
| T0 P3 absent agreement (COGS build, spend 0) | no active agreement -> fall-through tiers | 4320.0 |
| T0 P2 absent licensing (staging 95, Defender 15) | no Intune/Defender plan -> imaging 95 and hardening 15 | 5368.4 |
| T1 P7 base (opening, quote 8720.60) | seeded world | 4103.26 |
| T1 P7 second in-progress project, Standard Project, listed first | EXISTS by class: largest class (Standard Project) decides, order-independent | 3860.24 |
| T1 P7 absent project | no in-progress engagement -> project fall-through / no-project staging tier | 4265.27 |
| T1 P7 decoy closed agreement | CFIELD status=active excludes the closed agreement -> same tier as base | 4103.26 |
| T1 P6 base (opening) | seeded world | 8586.26 |
| T1 P6 absent agreement | no active agreement -> fall-through tiers | 9037.58 |
| T1 P6 absent project | no in-progress engagement -> project fall-through / no-project staging tier | 8661.26 |
| T1 P4 base | seeded world | 718.97 |
| T1 P4 second in-progress Standard Project | EXISTS by class: largest class (Standard Project) decides, order-independent | 664.05 |
| T1 P5 opening (not cancelled: 0 bench days) | order not yet cancelled counts 0 bench days -> no bench retention | 2421.06 |
| T1 P5 absent agreement | no active agreement -> fall-through tiers | 2353.56 |
Same-date ties: no LATEST or first-match read remains; the only CFIELD reads are on the client's single ClearPath agreement filtered status=active (managed_agg_multi_holding: one agreement at a time), and project reads are EXISTS by class, so two engagements on the same date cannot change a tier. MONTHS month-end: every go-live is on day 11-13, so the 'day number reached' convention and MONTHS() agree; late fees sit at 4-13 months, none on the 12-month boundary except the deliberate T0 near-miss 2025-10-01 (exactly 12 whole months, excluded by both readings).

## round 2 — method all-pairs tables (XF 23)
- P1 po_age_build: admin x units | pct x total + freight x units | pct x total. admin vs pct: different input (units vs total) PASS; admin vs pct+freight PASS; pct+freight vs pct: adds an input PASS.
- P2 fee_credit_basis: -fee | -min(fee, cap x units) | 0. full vs capped: adds a min PASS; 0 vs others: others >0 whenever a fee exists PASS.
- P3 tenure_deposit_build / P7 infra_relationship_build: cost x units | services + pct x equipment | pct x total. cost vs others: different input PASS; services+pct vs pct x total: adds the services input in full PASS.
- P4 bench_stage_build: admin x units | pct x total + freight x units | pct x total — as P1, PASS.
- P5 bench_retention_basis: 0 | staging x units x days / 14 | staging x units. pro-rata adds the days input PASS; 0 vs others: others >0 for any staging charge PASS.
- P6 lapse_charge_basis: per-unit x units | pct x units x cost | 0. per-unit vs pct: adds the cost input PASS; 0 vs others PASS.

## round 2 — trigger rule (XF 24)
- sign_order_cancellation_55862425 / sign_infrastructure_cancellation_1779b7d3: hardware_order_cancelled (trigger hardware:hardware_cancellation_fee when after_po) + hardware_cancellation_fee (no triggers) — in category.
- revise_staged_quote_eb003c71 / reissue_lapsed_quote_93c9a091: hardware_quote_issued revision (no triggers).
- sign_quote_approval_0590c0d2 / sign_build_approval_1b1ae884: hardware_quote_approved (trigger hardware:hardware_deposit_invoice when deposit_required) + hardware_deposit_invoice (no triggers) — in category.
- post_deposit_credit_9245a342: hardware_order_credit (no triggers). No tool writes an event whose trigger lands in another category.

## round 2 claims
- T0-F1 / T1-F1: each client holds one ClearPath agreement; the tier move is a signed tier change on it (managed_service_requests, tier_change_effective_date), priced with managed.yaml (36-month discounts, go-live baseline proration, every monthly fee, late fees at 1.5% with the tier minimum); all dependent values recomputed (T0 543.07 / 5080.40 / 1258.06; T1 718.97 / 2110.35 / 8586.26 / 3968.92).
- T0-F2 / T0-F3 / XF 22: skip effects recomputed by check_compute's value_input run and restated; scope and every proof text rewritten for revision 2 (stale-figure sweep of 0.json and 1.json found none).
- T0-F4 / T1-F2 / XF 20, 25: complete ledgers (managed seats, billing, requests; licensing order form, licence change, cycle charges and payments; project deposit invoice and payment before kickoff); the Sentinel holdings and the closed decoy agreement/project were removed; the closed monitor order carries its final invoice and payment; client_since equals the first ClearPath signing.
- CG-1: no factor is gated behind a method tier's non-default branch — freight and return freight are constants of the build, every P5 retention/goodwill acts on the baseline credit with a zero fall-through, and P5's baseline defines the bench retention the method varies.
- CG-2: every combination sentence is generic (no factor quantity named), with the order fixed where it matters.
- CG-3: project reads use EXISTS by class with the stated rule 'the largest class among them deciding'; probe with two in-progress engagements confirms order independence.
- CG-4: the deposit-credit overwrite names the endpoint schedule as its sibling.
- Realism: tenure-freight, Sentinel deposit relief, Sentinel rework, the re-issue sensor charge and the carried lapsed price were replaced by rush expedite forfeit, managed-spend relief, Defender onboarding by Microsoft 365 plan, a re-issue markup re-pricing factor and a single bench retention (no double charge of bench time).
- Final gates: EXTENDED OK; TASK TOOL CONTRACT OK; REPLAY OK; SOLVABILITY OK; COMPUTE OK (history_rows_max=8, branches_max=98); GROUNDING OK; SCOPE OK.
REWORK round 2: gates 7/7 green
- round 3: CG-2 combination sentences of P4, P5, P7 rewritten generically

## round 3 — combination-sentence sweep (XF 3/4), every policy
| policy | combination sentence (verbatim) | names a factor quantity? |
|---|---|---|
| P1 endpoint cancellation fee | "the percentage and the way the fee is built are settled first, and any fixed charge is then added to the built fee." | no (baseline percentage, build, generic fixed charge) |
| P2 staged re-quote | "every charge of the re-quote is figured and summed first, and any credit is deducted from that sum last." | no (generic charge/credit categories) |
| P3 endpoint deposit | "the deposit-required test on the quote total comes first and no adjustment changes it; the deposit percentage is then settled; and the way the deposit is built from that percentage and the quote comes last." | no |
| P4 infrastructure fee | "the fee percentage is settled first; the fee is then built from that percentage, the quote total and the units ordered; and the built fee never exceeds the deposit paid on the order, the sum of the payments on its ledger counted up to the deposit invoiced." | no ("tier rate"/"point adjustment" removed; the cap is a plain non-factor rule) |
| P5 deposit credit | "the bench retention is settled first, every other adjustment is then applied to the deposit paid, and the credit is never less than zero." | no ("goodwill amount" removed; bench retention is the baseline's quantity) |
| P6 lapsed re-issue | "the unit is re-priced first, every charge is then figured, and the units at the re-priced unit and the charges are summed last." | no |
| P7 infrastructure deposit | "the deposit percentage is settled first; the way the deposit is built from that percentage and the quote comes last." | no ("deposit share"/"point adjustment" removed) |
Order stays fixed in every sentence; compute_basis `result` entries updated verbatim; scratch quote sweep clean.

## round 3 — near-miss probes (scratch copies, value of the policy on that copy)
| policy / probe | rule reading | careless reading |
|---|---|---|
| P6 lapse clock (HQ-053084 dated 2026-09-01) | from last valid day 2026-09-15: 24 days -> 1.5% tier, 8586.26 | from quote date: 38 days -> per-unit tier, 8660.60 |
| P6 tenure (tier change effective 2024-11-01) | from go-live 2023-11-13: 34 months -> 20.00, 8586.26 | from tier change: 23 months -> 35.00, 8601.26 |
| P4 tenure loyalty (same record) | 34 months -> -0.5 pts, 718.97 | 23 months -> none, 746.42 |
| P5 handling retention (same record) | 34 months -> half, 2110.35 | 23 months -> full, 2092.85 |
| P2 Defender tier (expired E5 pilot) | active plans only -> Business Premium tier, 5080.40 | expired E5 counted -> 0/unit, 5048.40 |
Observation O11 (746.425 shown as 746.42): the compute DSL's RND uses binary float rounding; the figure is a sensitivity value, not a gold argument, and every gold argument sits clear of a half-cent.

## round 3 claims
- CG-2: P4, P5, P7 combination sentences rewritten without any factor quantity (and their `result` bases); all seven sentences swept above.
- T1-R2-F1: task 1 now carries two P6 near-misses priced per their charters — the 48-port quote dated 2026-09-01 (lapse clock: quote date vs last valid day) and the ClearPath tier change re-dated to 2024-11-01 with its signed request and the Standard months 2023-12..2024-10 re-billed at 3214.08 and paid (tenure: tier change vs go-live); named in factor_trace, design_rationale (NEAR-MISS CARD) and prerequisite_closure; gold unchanged (718.97 / 2110.35 / 8586.26 / 3968.92).
- P2 observation: task 0 gains an expired Microsoft 365 E5 (no Teams) pilot with its order form, licence purchase and expiry rows and its paid cycle charge, a Defender-tier near-miss excluded by "active"; gold unchanged (543.07 / 5080.40 / 1258.06).
- No regression: task 0 values, trees, tools unchanged; gates EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK (88/88, 87/87), SOLVABILITY OK, COMPUTE OK (history_rows_max=8, branches_max=98), GROUNDING OK, SCOPE OK.
REWORK round 3: gates 7/7 green
- round 4 started: plan appended to plan.md (CG-5, CG-6, T1-R3-F1)
- symptom: making every shared selection a plain binding leaves po_age_build, expedite_forfeit, tier_rush_rate, defender_onboarding_rate, reissue_markup_reduction, reissue_tier_rush and infra_seat_relief with no evidence primitive in their own bindings -> check_compute red ("none of its bindings reads history, a date span or another category"; the check is not transitive through plain bindings). root cause: these factors' only record read was the shared selection. change: a selection read by several factors is a plain binding stated once where every reader keeps its own distinct read (P2 licensing); elsewhere the second reader moves to a distinct, realistic record so the selection has one reader (P1, P2 tier, P6, P7). Gold, seeds and baselines unchanged.

## round 4 — selection map after the change (XF 1/2/26; mechanical: every evidence call per binding, owner = factor or PLAIN)
| policy | shared before | after |
|---|---|---|
| P1 endpoint fee | DAYS(order_placed_date, NOW) in po_age_build and expedite_forfeit | po_age_build only; expedite_forfeit reads DAYS(approved_date, NOW) ("rush processing … starts on the day its quote is approved") |
| P2 staged re-quote | EXISTS licensing BP/E3/E5 in autopilot and defender; CFIELD tier in rush and credit | plain b_lic_e5, b_lic_bp_e3, stated once ("For a staged re-quote, the client's Microsoft 365 plan is read once …"); autopilot also reads EXISTS(active ClearPath); defender also reads CPARAM m365_administration_included; tier only in tier_rush_rate; fee_credit_basis whole-fee tier reads the 12-month ClearPath late-fee count |
| P6 lapsed re-issue | CFIELD tier in reduction, staging, rush | tier only in reissue_markup_reduction; staging reads CPARAM network_device_management_included (with EXISTS project); rush reads CPARAM technical_account_manager / dedicated_account_manager (factor renamed reissue_account_rush) |
| P7 infrastructure deposit | CFIELD seat_count in spend relief and seat relief | seat_count only in infra_seat_relief; spend relief reads XLATEST(managed_billing amount_usd, managed_monthly_fee) while EXISTS(active ClearPath) |
Mechanical result: no evidence call has two factor owners in any policy; no plain binding reads a factor binding (XF 26); no factor reads another factor's binding (XF 1). Plain bindings: P2 b_lic_e5, b_lic_bp_e3, b_cancel_fee, b_rush_quoted, b_units, b_unit_price; others unchanged. Field reads F('quote_total_usd') (P3, P7) and F('order_placed_date') (P5, two different spans) were listed clean by the audit and are unchanged.
Realism of the new reads: rush_fee_usd is base "rush processing ahead of the queue", which starts at approval; MDE P2 onboarding is pushed by policy only where Stratton Bay administers the tenant (m365_administration_included); network equipment is staged from managed templates where firewall/switch/wireless changes are covered work; a named technical account manager books a rush allocation, a client success manager reduces it; spend relief reads the monthly fee actually billed (3821.85 = 141.55 x 27, so XF 25 holds); good standing (no late fee in 12 months) earns the whole-fee credit.

## round 4 — probes (handling-time world, scratch copies, value of the policy)
| probe | result |
|---|---|
| T0 P1 base | 543.07 |
| T0 P1 quote approved on the cancellation day (PO date unchanged) -> half expedite | 505.57 |
| T0 P1 PO placed on the cancellation day, approval 2026-09-28 -> admin build, expedite whole | 180.00 |
| T0 P2 base | 5080.40 |
| T0 P2 2026-06-01 late fee removed (2025-10-01 one is 12 whole months old, excluded) -> whole-fee credit | 4637.33 |
| T0 P2 absent licensing -> imaging 95, hardening 15 | 5268.40 |
| T0 P2 E5 pilot active, Professional covers tenant administration -> 0/unit (near-miss value) | 5048.40 |
| T0 P2 E5 active, agreement on ClearPath Monitor (no tenant administration) -> 8/unit, Monitor rush 150 | 5155.40 |
| T0 P2 agreement closed | 5225.40 |
| T1 P6 base | 8586.26 |
| T1 P6 on ClearPath Enterprise (technical account manager) | 8370.38 |
| T1 P6 on ClearPath Essentials (network devices covered, no client success manager) | 8872.58 |
| T1 P6 on ClearPath Monitor (no coverage, no manager) | 9022.58 |
| T1 P6 decoy closed Enterprise agreement listed first (status=active excludes it) | 8586.26 |
| T1 P6 no active agreement | 9037.58 |
| T1 P7 base | 3968.92 |
| T1 P7 latest monthly fee 5000.00 (>= half the quote total) | 3725.90 |
| T1 P7 an earlier monthly fee 5000.00, latest unchanged (latest decides) | 3968.92 |
| T1 P7 agreement closed, its monthly fees still on the ledger (EXISTS active gates the read) | 7044.00 |
Method all-pairs (XF 23): fee_credit_basis keeps its three methods (-fee | -min(fee, cap x units) | 0); only the whole-fee tier's condition changed; table of round 2 holds. Other changed factors are parameter factors.

## round 4 — dependency-wording sweep (skill check 6), every rule
Scan of every rule sentence for once/until/only after/after/before/prior to/first/already/then/cancelled/carries outside the declared prerequisite sentences: P5 opening sentence now "…Server & Storage Build Order cancelled after its purchase order; the credit is booked on the cancelled order against its deposit invoice, …" (no ordering connective tied to the result). Remaining hits are scope ("after the order's purchase order was placed and before it shipped", "cancelled after its purchase order"), rounding ("once, on the final amount"), month convention ("only once the day …"), assembly order (first/then/last), windows ("fewer than twelve whole months before"), the P1 rush sentence's "starts on the day its quote is approved" (a fact about rush work, not a problem dependency) and P6 "when the quote carries rush". P2, P3, P5, P7 prerequisite sentences are each the only statement of their dependency.

## round 4 — proof-text sweep (XF 22), both tasks, mechanical
- T1-R3-F1 fixed: prerequisite_closure.edges[0].unresolved_at_frozen_time.evidence[0] now "…733bb021-1c05-415b-a9e3-7f4934f37ac2.quote_date = 2026-09-01"; solvability_contract.gold_actions[2].stage_provenance.fact now "…dated 2026-09-01."; the 1.json design_rationale factor card "lapse_charge_basis 10 days" (stale since the quote was re-dated) now "24 days".
- Date sweep (every YYYY-MM-DD in every string outside initial_state, mapped to the seed fields carrying it): task 0 179 tokens, all seed dates except 2026-10-07 (frozen day), 2026-10-21/2026-10-22 (revised quote day 14 / 15); task 1 190 tokens, all seed dates except 2026-10-09 (frozen day), 2026-09-15 (quote_date 2026-09-01 + 14, the last valid day, 4 uses), 2026-10-23/2026-10-24 (re-issued quote day 14 / 15). Each date was read against its context (go-live, tier change, PO, approval, quote date, late fees, E5 expiry 2025-06-02 / licences removed 2025-06-03, payments, kickoff): no mismatch.
- Amount sweep (every decimal amount): task 0 112 tokens, task 1 131 tokens; unmatched-to-seed/params/gold ones are derived figures, all factor baselines among them equal the gate-verified factor_sensitivity / computations baseline_result values and appear in both rationale and factor_trace; arithmetic chains (a op b … = c) evaluated: task 0 26, task 1 28, all correct (6 regex partial-chain artefacts checked by hand: 395.072+148=543.072, 443.072+100=543.072, 242.00+1016.064, 1.5% x 7044.00=105.66, 8100.60+485.66=8586.26, 485.66+3483.258).
- Changed-factor proof text rewritten in both tasks (factor_trace, factor_sensitivity tier_taken, argument_uniqueness_tracing, read-node objectives/necessities, design_rationale factor cards); gold arguments, initial_state, baselines and tool order compared with the round-3 copies: identical.

## round 4 claims
- CG-5: no record selection is bound by two factors in any policy. P2's licensing plan reads are the plain bindings b_lic_e5 / b_lic_bp_e3 stated once in the rule; P1 PO age, P2 ClearPath tier, P6 ClearPath tier and P7 seat_count each have one reader, the other readers now resting on distinct records (approval age, late-fee count, tenant-administration coverage, network-device coverage, account managers, latest monthly fee). XF 26 re-checked mechanically: no plain binding reads a factor binding.
- CG-6: P5's action-form second wording removed; its declared prerequisite sentence is the only statement of the P5->P4 dependency; sweep of all seven rules found no other duplicate or weaker restatement.
- T1-R3-F1: both stale 2026-09-15 sentences corrected to 2026-09-01, the stale "10 days" rationale card corrected to 24 days; mechanical date/amount/arithmetic sweep of both tasks recorded above.
- No regression: every combination sentence unchanged and in order; gold 543.07 / 5080.40 / 1258.06 and 718.97 / 2110.35 / 8586.26 / 3968.92, seeds, trees and tools unchanged; factor counts [4,5,4] / [5,5,6,6] unchanged.
- Final gates: EXTENDED OK; TASK TOOL CONTRACT OK; REPLAY OK (88/88, 87/87); SOLVABILITY OK; COMPUTE OK (history_rows_max=8, branches_max=98); GROUNDING OK; SCOPE OK.
REWORK round 4: gates 7/7 green
- round 5 started: render_r1.md findings 1-3 (renderer scan-first STOP); edits are rule text only, compute untouched
- round 5 edits:
  - F1: P6 staging sentence and its b_ri_project basis drop "whose network design the bench configures from"; the rule now tests exactly what compute tests, an in-progress project engagement.
  - F2: P2 security-preparation lead is now "follows the client's Microsoft 365 plans, an E5 plan deciding when the client holds both an E5 plan and a Premium or E3 plan" (rule and f_edr_per_unit basis).
  - F3: both deposit overwrites' replaced_by and their rule copies end "…approved within the client's credit limit follows the [sibling] deposit schedule; and every other order, including any order whose approval would take the client over its credit limit, keeps the deposit of the base rule: a required deposit of deposit_pct percent of the quote total, or 100 percent of the quote total whatever deposit_pct and deposit_threshold_usd say when the approval would take the client over its credit limit, invoiced on approval, rounded half up to the cent and due on receipt (deposit_due)."
- round 5 XF 26 sweep: every whose/that/which/who/where/being clause in all seven rules listed and read against the records. The only other qualifier asserting a fact the records lack was P5's "…or Strategic Program, whose coordination is billed through that project" (no record links coordination billing to a project); it was removed, so the sentence ends at the class list. The rest are record-backed (status, tier, tenant-administration coverage, account managers, go-live, credit limit, validity, rush_available) or non-restrictive descriptions of the work a tier pays for (P2 "whose Defender onboarding package the bench applies to each unit", "whose units the bench hardens by hand"; P6 "who books the rush allocation with the distributor directly"). None of these filters a tier.
- round 5 no-regression: compute of all seven policies identical to round 4; every compute_basis result (combination sentence) identical; no task proof text quoted the edited phrases (grep), so gold and proof text are unchanged.

## round 5 claims
- 1: the P6 staging rule no longer qualifies the engagement, so rule and compute agree on every client; the cross_category note already read this way.
- 2: the P2 security-preparation lead is client-level and states E5 precedence, matching f_edr_per_unit; the tier sentences are unchanged.
- 3: both deposit tails restate the in-force base content for out-of-scope orders (invoiced on approval, rounded half up to the cent, due on receipt) and state the over-limit 100 percent prepayment explicitly. Each tail names its sibling's within-limit scope (XF 16/17).
- Gates: EXTENDED OK; TASK TOOL CONTRACT OK; REPLAY OK (88/88, 87/87); SOLVABILITY OK; COMPUTE OK (history_rows_max=8, branches_max=98); GROUNDING OK; SCOPE OK.
REWORK round 5: gates 7/7 green
- round 6 started (seed-only): KB audit revision_2 src=S1,S2. hardware.extended.yaml and task_tools.py left untouched; only tasks/0.json and tasks/1.json edited, initial_state and db_closure identically.

## round 6 — cross-product seed table (rows re-judged against docs/managed, docs/licensing, docs/project and blueprint/products)
| task | row(s) | published rule | before | after |
|---|---|---|---|---|
| 0 | ClearPath monthly fee 2026-10-01 INV-310217 (current service month) + agreement balance_due | monthly_fee_invoice_for_the_current_month scope -> seat-pricing schedule; monthly_seat_amount (19 billed, floor 18); monthly_fee_csp_licensing_terms (19 active Business Premium >= 19 seats -> 1.5% off); no Sentinel/Continuum/F3/servers, < 40 seats | 2689.45 | 2649.11 |
| 0 | late fee 2025-10-01 INV-310119 / payment 2025-10-08 | monthly_late_fee_assessment scope (only unpaid invoice); balance band 2689.45; rate 1.0% (no late fee in 12 months, 11 payments); 25% recent-payment courtesy (payment 2025-09-20); minimum 10.00 (18 months); no relationship courtesy | 40.34 / 2729.79 | 13.84 / 2703.29 |
| 0 | late fee 2026-06-01 INV-310175 / payment 2026-06-10 | same; rate 1.5% (2025-10-01 fee in window); 25% courtesy (2026-05-20); minimum 5.00 (26 months) | 40.34 / 2729.79 | 20.75 / 2710.20 |
| 1 | late fee 2025-09-01 INV-311141 / payment 2025-09-05 | same; balance 3821.85; rate 1.0% (11 payments); 25% courtesy; minimum 10.00 (21 months) | 57.33 / 3879.18 | 18.08 / 3839.93 |
| 1 | late fee 2026-02-01 INV-311176 / payment 2026-02-09 | rate 1.5%; 25% courtesy (2026-01-20); minimum 5.00 (26 months) | 57.33 / 3879.18 | 27.12 / 3848.97 |
| 1 | late fee 2026-07-01 INV-311211 / payment 2026-07-08 | rate 1.5%; 25% courtesy (2026-06-20); minimum 5.00 (31 months) | 57.33 / 3879.18 | 27.12 / 3848.97 |
| 1 | ClearPath monthly fee 2026-10-01 INV-311246 | current-month schedule: no Business Premium/F3/Sentinel/Continuum/servers, 27 < 40 seats, floor 25 -> no credit or charge | 3821.85 | unchanged |
| 0, 1 | every other ClearPath row: rates and term discounts, onboarding waiver, term dates, prorations (1099.70, 1928.45), tier changes and effective dates, pre-current-month fees, late-fee timing | rate_card_and_term_discounts, signing_rate_and_onboarding_fee, seat_ledger_changes_and_proration, tier_change_terms, monthly_seat_fee_terms, billing_and_collections_schedule | consistent | unchanged |
| 0 | Microsoft 365 Business Premium (22.00 x 12 x 19 = 5016.00 per cycle, renewal 2026-03-03) and E5 pilot (54.75 x 12 x 2 = 1314.00, expired, licences removed 2025-06-03); no admin-fee rows (ClearPath covers M365 administration) | csp_price_list_and_billing_terms, renewal_and_expiry_terms, licensing_ext_admin_fee hub; annual invoices paid within terms, so licensing_ext_late_charge does not apply | consistent | unchanged |
| 1 | Quick Start Project fixed fee 7800.00, deposit 3900.00 at signature 2026-08-24 | deposit_invoice_at_signature: a fixed-fee SOW keeps the class deposit percentage (50%) of the original contract value; the time-and-materials factors do not apply | consistent | unchanged |
Mechanical checks:
- Every late fee was recomputed from the ledger: scope, band, rate, 12-month counts, 1- and 3-month payment windows, and the tenure minimum. All five match the new amounts.
- Every managed invoice nets to zero except the open October fee, which equals the agreement balance (T0 2649.11, T1 3821.85).
- db_closure == initial_state in both tasks.
Scored impact: none. The hardware factors count late-fee entries by posting date (dates unchanged). P3 spend relief reads seat rate x seat count; P7 reads the T1 October fee, which is unchanged. Gold arguments and computations are identical to round 5. Proof text: the two design_rationale ledger cards were rewritten with the new figures. A grep finds no 40.34 / 57.33 / 2729.79 / 3879.18 / "minimum 35" anywhere outside the seed. The 2689.45 left in the T0 proof text is P3's seat rate x seat count, which is unchanged.

## round 6 claims
- S1: task 0's current-month ClearPath fee INV-310217 is 2649.11 (2689.45 less the 1.5% CSP licensing credit), and the agreement balance_due matches it.
- S2: all five seeded ClearPath late fees (T0 13.84, 20.75; T1 18.08, 27.12, 27.12) and the payments that settle them (2703.29, 2710.20; 3839.93, 3848.97, 3848.97) are what the published late-fee schedule produces; every ledger reconciles.
- No other cross-product row departs from its owning product's published rules (table above). Gold 543.07 / 5080.40 / 1258.06 and 718.97 / 2110.35 / 8586.26 / 3968.92 are unchanged.
- hardware.extended.yaml sha256 4c40c1e11afdb94b… and task_tools.py 565f6102036cdea8… are unchanged.
- Gates: EXTENDED OK; TASK TOOL CONTRACT OK; REPLAY OK (88/88, 87/87; --check OK); SOLVABILITY OK; COMPUTE OK (history_rows_max=8, branches_max=98); GROUNDING OK; SCOPE OK.
REWORK round 6: gates 7/7 green
- round 7 started (seed-only): T0-R6-F1. hardware.extended.yaml and task_tools.py untouched; only tasks/0.json changed (initial_state and db_closure identically). Task 1 already matches the published rules row for row, so its file is byte-identical.
- round 7 rule inventory (docs/managed): every published managed policy whose scope a seeded ClearPath row can fall in, read on the posting-day clock (today = the row's posting date):
  - current-month fee schedule (managed_ext_current_month_fee) -> every monthly fee;
  - late-fee schedule (managed_ext_first_late_fee) -> every late fee;
  - base seat-ledger proration -> go-live prorations;
  - base tier change: both tier changes are Essentials->Professional / Standard->Professional, outside the Essentials->Standard upgrade schedule;
  - payment application -> payments;
  - suspension: no invoice reached 60 days past due.
  - Not applicable, no seeded rows: renewal-rate schedule (no renewal yet: T0 term ends 2027-03-10, T1 2026-11-12, renewal_count 0), after-hours/onsite labor (no labor lines, no tickets), reinstatement, exit fee, service credits.
- round 7 change, task 0 (posting-day clock): the 18 monthly fees 2025-04..2026-09 go 2689.45 -> 2649.11. The 19 active Business Premium licences, purchased 2025-03-03, against 19 seats give 1.5% CSP credit; the 2025-02 and 2025-03 fees, posted before the purchase, stay 2689.45. The 16 ordinary payments go 2689.45 -> 2649.11. The late fees are recomputed on the 2649.11 balance: 2025-10-01 13.84 -> 13.68 (payment 2703.29 -> 2662.79), 2026-06-01 20.75 -> 20.53 (payment 2710.20 -> 2669.64).

## round 7 — every ClearPath row of both tasks vs the published managed rules (mechanical; expected = independent re-pricing, posting-day clock)
| task | posted | type | invoice | seeded | published rule gives | basis | check |
|---|---|---|---|---|---|---|---|
| 0.json | 2024-04-01 | monthly_fee | INV-310007 | 1623.36 | 1623.36 | Essentials 85.44x19 | ok |
| 0.json | 2024-04-01 | proration_charge | INV-310007 | 1099.7 | 1099.7 | 1623.36 x 21/31 | ok |
| 0.json | 2024-04-20 | payment | INV-310007 | 2723.06 | 2723.06 | settles invoice in full | ok |
| 0.json | 2024-05-01 | monthly_fee | INV-310014 | 1623.36 | 1623.36 | Essentials 85.44x19 | ok |
| 0.json | 2024-05-20 | payment | INV-310014 | 1623.36 | 1623.36 | settles invoice in full | ok |
| 0.json | 2024-06-01 | monthly_fee | INV-310021 | 1623.36 | 1623.36 | Essentials 85.44x19 | ok |
| 0.json | 2024-06-20 | payment | INV-310021 | 1623.36 | 1623.36 | settles invoice in full | ok |
| 0.json | 2024-07-01 | monthly_fee | INV-310028 | 1623.36 | 1623.36 | Essentials 85.44x19 | ok |
| 0.json | 2024-07-20 | payment | INV-310028 | 1623.36 | 1623.36 | settles invoice in full | ok |
| 0.json | 2024-08-01 | monthly_fee | INV-310035 | 1623.36 | 1623.36 | Essentials 85.44x19 | ok |
| 0.json | 2024-08-20 | payment | INV-310035 | 1623.36 | 1623.36 | settles invoice in full | ok |
| 0.json | 2024-09-01 | monthly_fee | INV-310042 | 1623.36 | 1623.36 | Essentials 85.44x19 | ok |
| 0.json | 2024-09-20 | payment | INV-310042 | 1623.36 | 1623.36 | settles invoice in full | ok |
| 0.json | 2024-10-01 | monthly_fee | INV-310049 | 1623.36 | 1623.36 | Essentials 85.44x19 | ok |
| 0.json | 2024-10-20 | payment | INV-310049 | 1623.36 | 1623.36 | settles invoice in full | ok |
| 0.json | 2024-11-01 | monthly_fee | INV-310056 | 1623.36 | 1623.36 | Essentials 85.44x19 | ok |
| 0.json | 2024-11-20 | payment | INV-310056 | 1623.36 | 1623.36 | settles invoice in full | ok |
| 0.json | 2024-12-01 | monthly_fee | INV-310063 | 1623.36 | 1623.36 | Essentials 85.44x19 | ok |
| 0.json | 2024-12-20 | payment | INV-310063 | 1623.36 | 1623.36 | settles invoice in full | ok |
| 0.json | 2025-01-01 | monthly_fee | INV-310070 | 1623.36 | 1623.36 | Essentials 85.44x19 | ok |
| 0.json | 2025-01-20 | payment | INV-310070 | 1623.36 | 1623.36 | settles invoice in full | ok |
| 0.json | 2025-02-01 | monthly_fee | INV-310077 | 2689.45 | 2689.45 | Professional 141.55x19 | ok |
| 0.json | 2025-02-20 | payment | INV-310077 | 2689.45 | 2689.45 | settles invoice in full | ok |
| 0.json | 2025-03-01 | monthly_fee | INV-310084 | 2689.45 | 2689.45 | Professional 141.55x19 | ok |
| 0.json | 2025-03-20 | payment | INV-310084 | 2689.45 | 2689.45 | settles invoice in full | ok |
| 0.json | 2025-04-01 | monthly_fee | INV-310091 | 2649.11 | 2649.11 | Professional 141.55x19 less CSP 1.5% | ok |
| 0.json | 2025-04-20 | payment | INV-310091 | 2649.11 | 2649.11 | settles invoice in full | ok |
| 0.json | 2025-05-01 | monthly_fee | INV-310098 | 2649.11 | 2649.11 | Professional 141.55x19 less CSP 1.5% | ok |
| 0.json | 2025-05-20 | payment | INV-310098 | 2649.11 | 2649.11 | settles invoice in full | ok |
| 0.json | 2025-06-01 | monthly_fee | INV-310105 | 2649.11 | 2649.11 | Professional 141.55x19 less CSP 1.5% | ok |
| 0.json | 2025-06-20 | payment | INV-310105 | 2649.11 | 2649.11 | settles invoice in full | ok |
| 0.json | 2025-07-01 | monthly_fee | INV-310112 | 2649.11 | 2649.11 | Professional 141.55x19 less CSP 1.5% | ok |
| 0.json | 2025-07-20 | payment | INV-310112 | 2649.11 | 2649.11 | settles invoice in full | ok |
| 0.json | 2025-08-01 | monthly_fee | INV-310119 | 2649.11 | 2649.11 | Professional 141.55x19 less CSP 1.5% | ok |
| 0.json | 2025-09-01 | monthly_fee | INV-310126 | 2649.11 | 2649.11 | Professional 141.55x19 less CSP 1.5% | ok |
| 0.json | 2025-09-20 | payment | INV-310126 | 2649.11 | 2649.11 | settles invoice in full | ok |
| 0.json | 2025-10-01 | late_fee | INV-310119 | 13.68 | 13.68 | bal 2649.11 rate 1.0 red 25 min 10 | ok |
| 0.json | 2025-10-01 | monthly_fee | INV-310133 | 2649.11 | 2649.11 | Professional 141.55x19 less CSP 1.5% | ok |
| 0.json | 2025-10-08 | payment | INV-310119 | 2662.79 | 2662.79 | settles invoice in full | ok |
| 0.json | 2025-10-20 | payment | INV-310133 | 2649.11 | 2649.11 | settles invoice in full | ok |
| 0.json | 2025-11-01 | monthly_fee | INV-310140 | 2649.11 | 2649.11 | Professional 141.55x19 less CSP 1.5% | ok |
| 0.json | 2025-11-20 | payment | INV-310140 | 2649.11 | 2649.11 | settles invoice in full | ok |
| 0.json | 2025-12-01 | monthly_fee | INV-310147 | 2649.11 | 2649.11 | Professional 141.55x19 less CSP 1.5% | ok |
| 0.json | 2025-12-20 | payment | INV-310147 | 2649.11 | 2649.11 | settles invoice in full | ok |
| 0.json | 2026-01-01 | monthly_fee | INV-310154 | 2649.11 | 2649.11 | Professional 141.55x19 less CSP 1.5% | ok |
| 0.json | 2026-01-20 | payment | INV-310154 | 2649.11 | 2649.11 | settles invoice in full | ok |
| 0.json | 2026-02-01 | monthly_fee | INV-310161 | 2649.11 | 2649.11 | Professional 141.55x19 less CSP 1.5% | ok |
| 0.json | 2026-02-20 | payment | INV-310161 | 2649.11 | 2649.11 | settles invoice in full | ok |
| 0.json | 2026-03-01 | monthly_fee | INV-310168 | 2649.11 | 2649.11 | Professional 141.55x19 less CSP 1.5% | ok |
| 0.json | 2026-03-20 | payment | INV-310168 | 2649.11 | 2649.11 | settles invoice in full | ok |
| 0.json | 2026-04-01 | monthly_fee | INV-310175 | 2649.11 | 2649.11 | Professional 141.55x19 less CSP 1.5% | ok |
| 0.json | 2026-05-01 | monthly_fee | INV-310182 | 2649.11 | 2649.11 | Professional 141.55x19 less CSP 1.5% | ok |
| 0.json | 2026-05-20 | payment | INV-310182 | 2649.11 | 2649.11 | settles invoice in full | ok |
| 0.json | 2026-06-01 | late_fee | INV-310175 | 20.53 | 20.53 | bal 2649.11 rate 1.5 red 25 min 5 | ok |
| 0.json | 2026-06-01 | monthly_fee | INV-310189 | 2649.11 | 2649.11 | Professional 141.55x19 less CSP 1.5% | ok |
| 0.json | 2026-06-10 | payment | INV-310175 | 2669.64 | 2669.64 | settles invoice in full | ok |
| 0.json | 2026-06-20 | payment | INV-310189 | 2649.11 | 2649.11 | settles invoice in full | ok |
| 0.json | 2026-07-01 | monthly_fee | INV-310196 | 2649.11 | 2649.11 | Professional 141.55x19 less CSP 1.5% | ok |
| 0.json | 2026-07-20 | payment | INV-310196 | 2649.11 | 2649.11 | settles invoice in full | ok |
| 0.json | 2026-08-01 | monthly_fee | INV-310203 | 2649.11 | 2649.11 | Professional 141.55x19 less CSP 1.5% | ok |
| 0.json | 2026-08-20 | payment | INV-310203 | 2649.11 | 2649.11 | settles invoice in full | ok |
| 0.json | 2026-09-01 | monthly_fee | INV-310210 | 2649.11 | 2649.11 | Professional 141.55x19 less CSP 1.5% | ok |
| 0.json | 2026-09-20 | payment | INV-310210 | 2649.11 | 2649.11 | settles invoice in full | ok |
| 0.json | 2026-10-01 | monthly_fee | INV-310217 | 2649.11 | 2649.11 | Professional 141.55x19 less CSP 1.5% | ok |
| 0.json | balance | agreement |  | 2649.11 | 2649.11 | ledger net | ok |
| 1.json | 2023-12-01 | monthly_fee | INV-311008 | 3214.08 | 3214.08 | Standard 119.04x27 | ok |
| 1.json | 2023-12-01 | proration_charge | INV-311008 | 1928.45 | 1928.45 | 3214.08 x 18/30 | ok |
| 1.json | 2023-12-20 | payment | INV-311008 | 5142.53 | 5142.53 | settles invoice in full | ok |
| 1.json | 2024-01-01 | monthly_fee | INV-311015 | 3214.08 | 3214.08 | Standard 119.04x27 | ok |
| 1.json | 2024-01-20 | payment | INV-311015 | 3214.08 | 3214.08 | settles invoice in full | ok |
| 1.json | 2024-02-01 | monthly_fee | INV-311022 | 3214.08 | 3214.08 | Standard 119.04x27 | ok |
| 1.json | 2024-02-20 | payment | INV-311022 | 3214.08 | 3214.08 | settles invoice in full | ok |
| 1.json | 2024-03-01 | monthly_fee | INV-311029 | 3214.08 | 3214.08 | Standard 119.04x27 | ok |
| 1.json | 2024-03-20 | payment | INV-311029 | 3214.08 | 3214.08 | settles invoice in full | ok |
| 1.json | 2024-04-01 | monthly_fee | INV-311036 | 3214.08 | 3214.08 | Standard 119.04x27 | ok |
| 1.json | 2024-04-20 | payment | INV-311036 | 3214.08 | 3214.08 | settles invoice in full | ok |
| 1.json | 2024-05-01 | monthly_fee | INV-311043 | 3214.08 | 3214.08 | Standard 119.04x27 | ok |
| 1.json | 2024-05-20 | payment | INV-311043 | 3214.08 | 3214.08 | settles invoice in full | ok |
| 1.json | 2024-06-01 | monthly_fee | INV-311050 | 3214.08 | 3214.08 | Standard 119.04x27 | ok |
| 1.json | 2024-06-20 | payment | INV-311050 | 3214.08 | 3214.08 | settles invoice in full | ok |
| 1.json | 2024-07-01 | monthly_fee | INV-311057 | 3214.08 | 3214.08 | Standard 119.04x27 | ok |
| 1.json | 2024-07-20 | payment | INV-311057 | 3214.08 | 3214.08 | settles invoice in full | ok |
| 1.json | 2024-08-01 | monthly_fee | INV-311064 | 3214.08 | 3214.08 | Standard 119.04x27 | ok |
| 1.json | 2024-08-20 | payment | INV-311064 | 3214.08 | 3214.08 | settles invoice in full | ok |
| 1.json | 2024-09-01 | monthly_fee | INV-311071 | 3214.08 | 3214.08 | Standard 119.04x27 | ok |
| 1.json | 2024-09-20 | payment | INV-311071 | 3214.08 | 3214.08 | settles invoice in full | ok |
| 1.json | 2024-10-01 | monthly_fee | INV-311078 | 3214.08 | 3214.08 | Standard 119.04x27 | ok |
| 1.json | 2024-10-20 | payment | INV-311078 | 3214.08 | 3214.08 | settles invoice in full | ok |
| 1.json | 2024-11-01 | monthly_fee | INV-311085 | 3821.85 | 3821.85 | Professional 141.55x27 | ok |
| 1.json | 2024-11-20 | payment | INV-311085 | 3821.85 | 3821.85 | settles invoice in full | ok |
| 1.json | 2024-12-01 | monthly_fee | INV-311092 | 3821.85 | 3821.85 | Professional 141.55x27 | ok |
| 1.json | 2024-12-20 | payment | INV-311092 | 3821.85 | 3821.85 | settles invoice in full | ok |
| 1.json | 2025-01-01 | monthly_fee | INV-311099 | 3821.85 | 3821.85 | Professional 141.55x27 | ok |
| 1.json | 2025-01-20 | payment | INV-311099 | 3821.85 | 3821.85 | settles invoice in full | ok |
| 1.json | 2025-02-01 | monthly_fee | INV-311106 | 3821.85 | 3821.85 | Professional 141.55x27 | ok |
| 1.json | 2025-02-20 | payment | INV-311106 | 3821.85 | 3821.85 | settles invoice in full | ok |
| 1.json | 2025-03-01 | monthly_fee | INV-311113 | 3821.85 | 3821.85 | Professional 141.55x27 | ok |
| 1.json | 2025-03-20 | payment | INV-311113 | 3821.85 | 3821.85 | settles invoice in full | ok |
| 1.json | 2025-04-01 | monthly_fee | INV-311120 | 3821.85 | 3821.85 | Professional 141.55x27 | ok |
| 1.json | 2025-04-20 | payment | INV-311120 | 3821.85 | 3821.85 | settles invoice in full | ok |
| 1.json | 2025-05-01 | monthly_fee | INV-311127 | 3821.85 | 3821.85 | Professional 141.55x27 | ok |
| 1.json | 2025-05-20 | payment | INV-311127 | 3821.85 | 3821.85 | settles invoice in full | ok |
| 1.json | 2025-06-01 | monthly_fee | INV-311134 | 3821.85 | 3821.85 | Professional 141.55x27 | ok |
| 1.json | 2025-06-20 | payment | INV-311134 | 3821.85 | 3821.85 | settles invoice in full | ok |
| 1.json | 2025-07-01 | monthly_fee | INV-311141 | 3821.85 | 3821.85 | Professional 141.55x27 | ok |
| 1.json | 2025-08-01 | monthly_fee | INV-311148 | 3821.85 | 3821.85 | Professional 141.55x27 | ok |
| 1.json | 2025-08-20 | payment | INV-311148 | 3821.85 | 3821.85 | settles invoice in full | ok |
| 1.json | 2025-09-01 | late_fee | INV-311141 | 18.08 | 18.08 | bal 3821.85 rate 1.0 red 25 min 10 | ok |
| 1.json | 2025-09-01 | monthly_fee | INV-311155 | 3821.85 | 3821.85 | Professional 141.55x27 | ok |
| 1.json | 2025-09-05 | payment | INV-311141 | 3839.93 | 3839.93 | settles invoice in full | ok |
| 1.json | 2025-09-20 | payment | INV-311155 | 3821.85 | 3821.85 | settles invoice in full | ok |
| 1.json | 2025-10-01 | monthly_fee | INV-311162 | 3821.85 | 3821.85 | Professional 141.55x27 | ok |
| 1.json | 2025-10-20 | payment | INV-311162 | 3821.85 | 3821.85 | settles invoice in full | ok |
| 1.json | 2025-11-01 | monthly_fee | INV-311169 | 3821.85 | 3821.85 | Professional 141.55x27 | ok |
| 1.json | 2025-11-20 | payment | INV-311169 | 3821.85 | 3821.85 | settles invoice in full | ok |
| 1.json | 2025-12-01 | monthly_fee | INV-311176 | 3821.85 | 3821.85 | Professional 141.55x27 | ok |
| 1.json | 2026-01-01 | monthly_fee | INV-311183 | 3821.85 | 3821.85 | Professional 141.55x27 | ok |
| 1.json | 2026-01-20 | payment | INV-311183 | 3821.85 | 3821.85 | settles invoice in full | ok |
| 1.json | 2026-02-01 | late_fee | INV-311176 | 27.12 | 27.12 | bal 3821.85 rate 1.5 red 25 min 5 | ok |
| 1.json | 2026-02-01 | monthly_fee | INV-311190 | 3821.85 | 3821.85 | Professional 141.55x27 | ok |
| 1.json | 2026-02-09 | payment | INV-311176 | 3848.97 | 3848.97 | settles invoice in full | ok |
| 1.json | 2026-02-20 | payment | INV-311190 | 3821.85 | 3821.85 | settles invoice in full | ok |
| 1.json | 2026-03-01 | monthly_fee | INV-311197 | 3821.85 | 3821.85 | Professional 141.55x27 | ok |
| 1.json | 2026-03-20 | payment | INV-311197 | 3821.85 | 3821.85 | settles invoice in full | ok |
| 1.json | 2026-04-01 | monthly_fee | INV-311204 | 3821.85 | 3821.85 | Professional 141.55x27 | ok |
| 1.json | 2026-04-20 | payment | INV-311204 | 3821.85 | 3821.85 | settles invoice in full | ok |
| 1.json | 2026-05-01 | monthly_fee | INV-311211 | 3821.85 | 3821.85 | Professional 141.55x27 | ok |
| 1.json | 2026-06-01 | monthly_fee | INV-311218 | 3821.85 | 3821.85 | Professional 141.55x27 | ok |
| 1.json | 2026-06-20 | payment | INV-311218 | 3821.85 | 3821.85 | settles invoice in full | ok |
| 1.json | 2026-07-01 | late_fee | INV-311211 | 27.12 | 27.12 | bal 3821.85 rate 1.5 red 25 min 5 | ok |
| 1.json | 2026-07-01 | monthly_fee | INV-311225 | 3821.85 | 3821.85 | Professional 141.55x27 | ok |
| 1.json | 2026-07-08 | payment | INV-311211 | 3848.97 | 3848.97 | settles invoice in full | ok |
| 1.json | 2026-07-20 | payment | INV-311225 | 3821.85 | 3821.85 | settles invoice in full | ok |
| 1.json | 2026-08-01 | monthly_fee | INV-311232 | 3821.85 | 3821.85 | Professional 141.55x27 | ok |
| 1.json | 2026-08-20 | payment | INV-311232 | 3821.85 | 3821.85 | settles invoice in full | ok |
| 1.json | 2026-09-01 | monthly_fee | INV-311239 | 3821.85 | 3821.85 | Professional 141.55x27 | ok |
| 1.json | 2026-09-20 | payment | INV-311239 | 3821.85 | 3821.85 | settles invoice in full | ok |
| 1.json | 2026-10-01 | monthly_fee | INV-311246 | 3821.85 | 3821.85 | Professional 141.55x27 | ok |
| 1.json | balance | agreement |  | 3821.85 | 3821.85 | ledger net | ok |
Result: 139 rows, 0 mismatches. That is every monthly fee, proration, late fee and payment, plus both agreement balances: T0 2649.11 = open INV-310217; T1 3821.85 = open INV-311246.
Scored impact: none. Hardware factors in task 0 count late-fee entries by date (unchanged), and P3 spend relief reads seat_rate x seat_count by its rule (unchanged, 2689.45). Gold arguments and computations are identical to round 6. Proof text: task 0's design_rationale ledger card was rewritten for the posting-day fees, the 13.68 / 20.53 late fees and the 2662.79 / 2669.64 payments. 13.84 / 2703.29 / 20.75 / 2710.20 no longer appear outside the seed. The 2689.45 that remains in proof text is P3's seat_rate x seat_count, or the 2025-02/03 fees.

## round 7 claims
- T0-R6-F1: every ClearPath monthly fee of task 0 is priced as of its own posting day under the published current-month schedule: 2649.11 from 2025-04, 2689.45 before the Business Premium purchase. Late fees (13.68, 20.53), payments and the balance follow, and every invoice reconciles.
- Exhaustive: all 139 ClearPath rows of both tasks equal what the published managed rules produce (table above). Task 1 needed no change.
- No regression: gold 543.07 / 5080.40 / 1258.06 and 718.97 / 2110.35 / 8586.26 / 3968.92 are unchanged. hardware.extended.yaml sha256 4c40c1e11afdb94b… and task_tools.py 565f6102036cdea8… are unchanged.
- Gates: EXTENDED OK; TASK TOOL CONTRACT OK; REPLAY OK (88/88, 87/87; --check OK); SOLVABILITY OK; COMPUTE OK (history_rows_max=8, branches_max=98); GROUNDING OK; SCOPE OK.
REWORK round 7: gates 7/7 green
