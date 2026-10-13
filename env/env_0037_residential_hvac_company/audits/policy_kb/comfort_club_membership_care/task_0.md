# Policy-KB bijection audit — comfort_club_membership_care / task 0

Scope: product `plan`, extended policies `plan_ext_covered_repair_draw` and `plan_ext_cancellation_settlement` (charter_scope of task 0), their base policies `plan_evt_repair_coverage`, `plan_evt_tuneup_allowance`, `plan_cancellation_refund`, the tier parameters they read, and the two task tools. Corpus: the 64 published plan docs (title/content view, hash e8cdd699…f86282). Written after the runtime blind answer was frozen (runtime_context/comfort_club_membership_care/task_0.md).

Entry conditions (Step 0), cited from the brief: policy-side audit PASS for both tasks; `check_docs.py … plan` -> "DOCS OK" (64 docs, 6 prerequisite edges, mechanical gates PASS, manual items open); `check_traceability.py …/comfort_club_membership_care` -> "TRACEABILITY OK (2 tasks)", 0.json 22 copied / 0 missing; runtime view and tool-shaped DB path supplied. Complete.

## source_to_kb

### plan_ext_covered_repair_draw
| Source atom | KB home | Judgement |
|---|---|---|
| Tier with covered repairs; completed call, enrolled system, agreement active; settles repair lines posted fewer than one whole month before | "Comfort Club Covered-Repair Draws on Completed Service Calls" (hub) §The rule; "Worksheet: Covered Amount and Draw…" §Lines that enter | equivalent |
| Covered lines = repair parts + repair labor, except thermostat / condensate pump replacement | Worksheet §Lines that enter | equivalent |
| Order: discounted amount (discount once), maintained amount, refrigerant × rate less allowance, less protection coverage, less deductible, round half up | Worksheet steps 1–5 + "The covered amount is rounded to the cent half up" | equivalent |
| Never-covered list with refrigerant only at the refrigerant coverage rate (replaced_by of overwrite 1) | Worksheet §Lines that enter "Never covered" | equivalent |
| Draw = lowest of covered amount, per-call cap, benefit remaining, never below zero; one draw per call naming lowest-positioned covered repair line | Worksheet §The draw; hub §The rule | equivalent |
| Baseline constants: labor as billed (1.0), maintained = discounted, cap = tier per-incident cap, refrigerant rate 0, standard deductible 50.00 | Worksheet steps 1–5 ("one times the billed amount, 1.0", "it is the discounted repair amount", "rate is zero", "standard deductible of 50.00 USD"), §The draw ("tier's covered-repair per-incident cap") | complete; product figures named (member repair discount -> "Service Call Member Benefits"; per-incident cap -> "Covered-Repair Benefit Limits") |
| Waiting period: call booked no earlier than the waiting period after the first covered-repair grant; decides whether, not how much | hub §The rule; base bulletin "Covered Repairs: Benefit Grants…" | equivalent |
| Factor `after_hours_labor_divisor` — 3 tiers: Overnight/Holiday ÷1.5; Evening/Weekend ÷1.25; other as billed; each divided amount half up | "Labor Valuation on Evening, Weekend, Overnight and Holiday Calls" | full ladder, figures stated; reachable from service-ticket `variant_name` words |
| Factor `maintenance_coverage_basis` (method) — 0 tune-ups: parts only less discount, half up, labor with member; 1: discounted − tune-up retail value, floor 0; ≥2: discounted | "Maintenance Kept and the Comfort Club Maintained Repair Amount" | full ladder; 109.00 stated; window 12 months stated |
| Factor `loyal_member_call_cap` — ≥10 terms & no draw in 24 m: +250; 5–9 & no draw: +125; else tier cap | "Per-Call Covered-Repair Cap for Long-Standing Members" | full ladder, both thresholds and figures |
| Factor `sealed_system_refrigerant_rate` — sealed task & ≥10: 1.0; sealed & <10: 0.5; none: 0; five tasks listed | "Refrigerant Coverage on Sealed-System Repairs" | full ladder; task list complete; names Repair and Emergency Service Calls |
| Factor `protection_holder_deductible` — 12-Yr Total / Total Plus: 0.00; other active: 25.00; none: standard | "Covered-Repair Deductible for Protection Contract Holders" | full ladder ("the reduced deductibles of this rule do not apply" for none = standard by entailment with the computation doc); names Harbison Protection Contracts |
| Tool contract `post_covered_repair_draw_a854dec6` (owner agent, 4 params, receipt) | hub §System entry | equivalent to schema |
| prerequisite | `[]` | no prerequisite sentence carried for this policy anywhere | consistent |

Retired surface (3 overwrites of `plan_evt_repair_coverage`): "Covered Repairs: Benefit Grants, Waiting Period, Eligible Lines and Expiry" §No longer in force lists all three (never-covered list incl. refrigerant; discount-then-warranty per line; per-line allocation draw), each written as no longer in force. Unnamed base clauses (grants, grant/draw status gates, waiting period, covered lines, exclusions, expiry) carried as in force. No undeclared retirement.

### plan_ext_cancellation_settlement
| Source atom | KB home | Judgement |
|---|---|---|
| Member's own decision; confirms pending request in person; effective/cancelled date = confirmation date; credit posted with confirmation naming the current term's dues charge | "Comfort Club Agreement Cancellation by the Member" (hub) §Terms; base "Cancellation and Refund Terms" cl.1–2 | equivalent |
| Fee: outside window and tier fee > 0.00 -> billed; otherwise none | hub §Cancellation fee; base cl.7 | equivalent |
| Monthly agreement earns no proration credit; closure of visits/benefit | hub; base cl.10–11 | equivalent |
| Order and definitions: term dues billed (posting window "elapsed + 1"), refundable dues (unused full months, step counting), visit chargeback (term visits × retail values × rate), coverage chargeback, install recapture (12 months), discount recapture (same window), credit floor 0 | "Comfort Club Cancellation Credit Worksheet" steps 1–7 | complete and in order |
| Baseline constants: visit rate 1, coverage rate 1, install and discount recapture rate 0; retail values 109.00/139.00 | Worksheet steps 3–6; "Cancellation Schedule" table | complete |
| Factor `notice_refund_basis` (method) — ≤ window: in full; > window ≤ 60 days & ≥10 terms: × days to term end / 365 half up; else unused months | "Comfort Club Refundable Dues and the Date of Notice" | full ladder; 30 days per tier, 60, 10 stated; notice = request received, day 0 = term start |
| Factor `long_tenure_visit_rate` — ≥120 m & ≥8 visits: 0.6; ≥60 m & ≥4 not both: 0.8; else 1 | "Visit Chargeback Rate for Long-Tenure Comfort Club Members" | full ladder; compound conditions intact |
| Factor `claim_history_coverage_rate` — ≥10 & no draw in 24 m outside current term: 0.25; ≥5 not meeting: 0.5; else 1 | "Coverage Chargeback Rate and Covered-Repair History" | full ladder; current-term exclusion stated |
| Factor `install_credit_recapture` — <6 m: 0.5; 6–<12 m: 0.25; none in 12 m: 0 | "Installation Credit Recapture When a Comfort Club Agreement Is Cancelled" | full ladder; names Replacement System Installations |
| Factor `member_discount_recapture` — ≥250: 1.0; ≥100 <250: 0.4; else 0; current-term window | "Member Repair Discount Recapture on Comfort Club Cancellation" | full ladder; window restated in the doc itself; names Repair and Emergency Service Calls |
| Tool contract `confirm_agreement_cancellation_08dfa488` (owner user, 5 params, effect, receipt) | hub §System entry | equivalent |

**Prerequisite (only edge)**: `plan_ext_cancellation_settlement -> plan_ext_covered_repair_draw`, form `state`.
- policy_source carried verbatim, connective "only after" intact, in the blocked policy's hub "Comfort Club Agreement Cancellation by the Member" §When the credit is fixed; plus a same-form restatement in the same doc ("Equivalently: while a completed service call … does not yet carry its covered-repair draw on the agreement, the cancellation credit is not fixed.").
- Carried in no other document (exact-string sweep of all 64 docs: one hit).
- Resolution basis: the sentence's state words ("carries its covered-repair draw on the agreement") + the draw hub ("a covered-repair draw settles a completed service call … posted as one draw for the call") + records (completed ticket 98b91f92 with repair lines posted after term start, no draw entry). Strength (hard gate on fixing the credit) and connective match. `condition` / `resolved_by` have no home in any doc (correct).
- Depended-on documents do not carry the blocked side's sentence.

Retired surface (2 overwrites of `plan_cancellation_refund`): "Cancellation and Refund Terms" cl.5 and cl.6 written "(No longer in force)" with the superseded wording; remaining clauses (decision, effective date, annual credit, window, fee outside window "(in force)", floor, posting condition, monthly, closure, payout) carried in force. No undeclared retirement.

## kb_to_source
Sentence-by-sentence read of the 13 docs above plus base docs touching their subjects:
- Every normative claim traces to the source rule, base rule, tier parameters, measures or the tool contracts. Clarifying sentences checked as same-source derivations, not additions: "The waiting period runs from the agreement's first covered-repair grant only; a later renewal grant does not restart it" (entailed by "first covered-repair grant"); "Draws charged to the current term are set aside for the 24-month test" (restates "apart from draws charged to the current term"); "The plan covers the call's covered amount, not simply what remains of the lines" (source rule verbatim).
- No added confirmation, review, notification, verification step or procedure.
- Cross-problem operational guidance ("if unmet, first call …"): none. No other problem's tool named in either hub (tool-name sweep: each task tool appears only in its own hub).
- Task opening world state written as policy fact: none (all examples are labelled hypothetical; no figure of this customer's records appears).

## bijection_verdict
**PASS.** No omission, softening, rewrite or addition found across the full domain (untriggered tiers included) of both extended policies, their base policies and the retired surface. First revision.

Policy-side notes (do not change this verdict):
- The base measure `plan_msr_term_dues_billed` defines term dues by billing_period within the term, while the extended rule defines them by the posting window "fewer whole months than elapsed + 1"; the extended rule governs and is what the KB carries.

## dependency_form
Hop marks from the blind answer: the single hop was **state-derived**; no hop pre-solved.
Sweep of the whole plan corpus:
- State-form sentence restated as an action / naming the resolving action, tool or problem: none (the hub's restatement is same-form).
- Second document stating this dependency or an order between the two problems: none. The draw docs say nothing about cancellation; the cancellation worksheet and factor docs say nothing about posting draws first.
- Aggregated tables, checklists, routes, cross-problem examples or FAQs: none.
- Titles/openings: general subjects ("Comfort Club Agreement Cancellation by the Member" names the on_request subject; "Comfort Club Covered-Repair Draws on Completed Service Calls"); none mirrors task 0's situation.
- Computation docs (worksheets) hint at no modification beyond their source baseline wording; factor docs do not name, override or point at the worksheets or other factors, and do not say which tier customers usually fall on.
- Findability: every factor doc reachable from record words (call class, task code, contract tier, consecutive_terms, enrolled date, install-ledger member installation credit, member repair discount lines).

**PASS** (no KB-EXPLICIT RED).
