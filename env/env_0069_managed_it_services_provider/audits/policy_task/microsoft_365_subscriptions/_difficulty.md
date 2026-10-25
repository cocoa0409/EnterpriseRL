# Policy-task audit — microsoft_365_subscriptions / charter-global

## revision_1

## charter_global_frozen
- Frozen 2026-10-18T02:00:32Z (UTC, file mtime) by the independent policy auditor (erl-task-policy-audit), round r1. Written from the charter, the schema, the shared and task tool contracts and the XF recipe only; no task JSON had been opened when this section was written.
- Hashes (re-computed with sha256sum and equal to the coordinator brief):
  - `tasks/microsoft_365_subscriptions/licensing.extended.yaml` 7ca6f8e47cc65d428f017c8b63edb7c77856cdea916edf4f13b8b72363f317cb
  - `tasks/microsoft_365_subscriptions/task_tools.py` 8af718a78a5d07da4cb13ed8b9b61f0f4ec413ef2a7c3dfacb3b4ca73896108b
  - `.audit_views/policy/microsoft_365_subscriptions/r1/0.view.json` 18f747ab5b802cca85fd1f1900dcc68299332c8241c4e5b4eb24b81101055bfc
  - `.audit_views/policy/microsoft_365_subscriptions/r1/1.view.json` 140eeade1ee30a452e2e832717f71f10a1931cc94448e3999f0745dc00e2c0b2
- Read: blueprint/ (blueprint.yaml, db_schema.json, share_tools.py, products/licensing.yaml and the managed / security / backup / timebank charters for cross-product checks), the extended charter, task_tools.py, the two masked views (frozen_time, user_scenario, initial_state), audits/render_source/XF_recipe.md, erlbench/ and the DSL evaluator `skills/erl-task-instantiate/scripts/check_compute.py` (for MONTHS/DAYS/LATEST/CFIELD/RND semantics).
- Masked and unread at this point: tasks/microsoft_365_subscriptions/tasks/*.json (evaluation_criteria, computations, charter_scope, required_documents, design_rationale, solvability_contract, prerequisite_closure, db_closure), plan.md and worklog.md of the difficulty, any earlier audit.
- Entry conditions: gate snapshot supplied (check_extended, check_task_tools, replay_tasks --check, check_solvability, check_compute, check_grounding, check_cross_fire all rc=0; check_traceability deferred until the KB is published). Masked views supplied with hashes. Entry conditions met. A green gate is the entry qualification only.
- Base copy: `diff <(sed -n 1,946p licensing.extended.yaml) blueprint/products/licensing.yaml` differs only by one trailing blank line; the base section is verbatim.

### policy_conflict_scan
Extended policies (6): P1 `licensing_ext_reduction_credit` (post_reduction_credit_23f8ed2c, agent, state_due), P2 `licensing_ext_late_charge` (assess_late_charge_e02563fc, agent, state_due), P3 `licensing_ext_payment_arrangement` (pay_arrangement_instalment_a0d5f2e9, user, on_request), P4 `licensing_ext_admin_fee` (post_admin_fee_5104ae31, agent, state_due), P5 `licensing_ext_seat_partial_charge` (post_seat_addition_charge_bba679a2, agent, state_due), P6 `licensing_ext_window_cancellation` (cancel_subscription_in_window_d46a60fb, user, on_request).
- Overlapping subjects: `licensing_refund_credit` is claimed by P1 (in-window reduction, charge_reason in_window_reduction) and P6 (whole cancellation, charge_reason cancellation). Both supersede the same base sentence of `licensing_cancellation_window` and each names the sibling's case (P1: "the cancellation of a whole subscription is refunded under its own cancellation schedule"; P6: "an in-window reduction is credited under its own reduction credit schedule"); both restate the base formula for out-of-scope subscriptions. No overlap in object. `licensing_prorated_charge` is P5's (seat additions); upgrade proration stays in base `licensing_upgrades` (no tool in this difficulty). `licensing_late_fee` P2 only (annual cycle invoices); `licensing_payment` P3 only; `licensing_admin_fee` P4 only.
- Triggers / time anchors: P2 and P4 are first-of-month assessments; P1 and P5 are state_due postings at "the posting date"/"the charge" (NOW); P3/P6 are on request. No two policies anchor the same quantity to different moments, except the base waiver sentence of `licensing_admin_fee_rules` vs P4 (finding F5).
- Eligibility: P6 inherits the base 168-hour whole-cancellation window and the signed-order-form requirement (the user tool records a signed `licensing_change_requests` row). P3 inherits the card limit ("the card payment limit of the invoice still applies"). No extended policy weakens a base eligibility.
- Terminal states: P3's terminal ledger conflicts with its own rule (finding F7). P6's tool fixes the credited invoice to the term-start cycle invoice, which conflicts with P6's own replaced_by for out-of-scope cancellations (finding F6).
- Cross-category read boundaries: reads are managed (status, variant, tier params, renewal_count, balance, billing late fees, seat ledger), security (status, identity_threat_detection), backup (status, variant, device ledger), timebank (status, hours_balance). Cross-category conclusion conflict: license-change fees in P5/P6 vs the charter's own "covered work" treatment in P1 (finding F8).
- Scope exclusivity: by the prerequisite graph the six policies split into two trees, {P3 <- P2 <- P1} and {P6 <- P4, P6 <- P5}; with M=2 these are mutually exclusive and jointly complete. (Each task's claimed scope is confirmed against `charter_scope` only after reveal, in the task files.)

### rule_compute_equivalence
Mechanical sweeps (scratch, /tmp only): every `compute_basis` quotation is verbatim in its own rule (0 misses over 6 policies); every `baseline.rule` sentence is in its rule; every factor id is absent from every tool name (XF A7 clean).
Per policy, the rule-to-compute map (both directions):
- P1: latest in-window reduction (LATEST effective_at, change_reason in_window_reduction; tie rule stated: one change per moment and reason); cycle = term start..end inclusive (`DAYS+1`); cycle amount = unit price (P1M) / 12x (P1Y annual); renewal-window test `renewal_count>=1 and red_at>=window_opened_at`; opening lag `DAYS(window_opened_at, red_at)`; credited-days ladder; change-fee ladder (CPARAM active/notice_given m365_administration_included; CFIELD active Monitor); delay goodwill `DAYS(red_at, NOW)` >30 / 8..30 / <=7; review pct by vCIO 4+/1-3 within a renewal window; `RND` once at end. Each phrase has a binding; no binding without a phrase. The fall-through for an active tier with 0 vCIO reviews (ClearPath Monitor) is reached by compute but the rule's explicit no-goodwill sentence names only "outside a renewal window" and "no active ClearPath agreement" (observation O5).
- P2: latest cycle-charge invoice; past-due balance = cycle + prorated - credits - payments on that invoice, late fees excluded; days past due = DAYS(posted, NOW) - invoice_due_days; rate ladder with the stated 12-whole-months convention, matching `MONTHS` (same day twelve months earlier gives 12, excluded); minimum ladder; share ladder (<=30 pro rata /30; >60 with no late fee: int(d/30); else 1); escalation by XCOUNT managed_late_fee 12 months; relief by payments vs 25 percent; size scale; `MX` then multipliers, `RND` once. Equivalent.
- P3: balance = F(balance_due_usd); latest cycle invoice; instalment ladder; down-payment ladder on the invoice's cycle charges; month-late SUM within 1 month; DAM via CPARAM; principal/upfront; setup fee from COUNT 24 months minus COUNT 1 month; assembly. Equivalent. No same-day tie sentence for the latest cycle charge in P3 (P2 carries it; one cycle charge per cycle start), observation only.
- P4: licenses = added - removed; coverage ladder; term 1,000+/<=31 days; volume on licenses counted; upkeep by plan param and active Sentinel ITDR; month part held_days/30, suspended 0.5, else 1; bundle by active Continuum and protected m365 users (protections less removals) vs licenses; assembly. Equivalent, except the moment at which coverage is read (finding F5).
- P5: latest seat addition; cycle and cycle amount; order-window ladder; TimeBank provisioning ladder; volume on the addition's quantity; onboarding XCOUNT 1 month; combined discount taken once; provisioning added; `RND` once. Rule-vs-compute divergence when two active TimeBank blocks exist (finding F4).
- P6: cycle and licenses held; charges billed = cycle + prorated charges whose cycle_start_date = term_start_date; refunded-days ladder; admin-fee return ladder; reversal fee by licenses cancelled (added - removed); deprovisioning per license by Continuum tier; per-change rate by number of seat additions; `MN` cap then additions and subtractions; `RND` once. Equivalent; wording note O6.
- Rounding: every rule says "rounded half up to the cent once, at the end" and compute has a single terminal `RND`. `RND` is Python `round` (half-even on the binary value); no figure in either task world lands on a half-cent tie (checked), so this is observation O4 only.

### action_binding_and_uuids
- Six `(target_tool, computes)` pairs, each claimed by exactly one policy: (post_reduction_credit_23f8ed2c, amount_usd) P1; (assess_late_charge_e02563fc, amount_usd) P2; (pay_arrangement_instalment_a0d5f2e9, amount_usd) P3; (post_admin_fee_5104ae31, amount_usd) P4; (post_seat_addition_charge_bba679a2, amount_usd) P5; (cancel_subscription_in_window_d46a60fb, refund_amount_usd) P6.
- uuid8s 23f8ed2c, e02563fc, a0d5f2e9, 5104ae31, bba679a2, d46a60fb: pairwise distinct, no shared prefix or tail, no sequence; no sign of batch derivation.
- Docstrings: no concrete example values (formats only), no other tool named, no ordering word (before/after/first) and no sequence position. The tools validate nothing about prerequisites (bodies only find the subscription, create rows and adjust balance_due_usd).
- Docstring-vs-body: the cancellation tool books the refund "against the invoice that billed the current cycle" by selecting the cycle charge whose cycle_start_date equals term_start_date, and the seat-charge tool stamps cycle_start_date = term_start_date while its docstring says "in the billing cycle the subscription is in"; both are correct only for whole-term cycles (finding F6).
- P3's tool books the whole instalment as one payment applied to the invoice; no write posts the setup fee as a charge (finding F7).

### prerequisite_graph
- `prerequisite` present on all six (P1 [], P4 [], P5 []). Edges: P2 -> P1 (value_input, gate past_due_balance), P3 -> P2 (value_input, gate month_late), P6 -> P4 (value_input, gate admin_return), P6 -> P5 (value_input, gate billed_cycle). Every `problem` is an extended policy id of this file, none self-referential, none base. Graph acyclic.
- Every `policy_source` is verbatim in its own rule (sweep: 4/4). All four are `form: state` with no `fallback_reason`. Each `gate` names a binding that exists in that policy's compute. Each `resolved_by` is the depended-on policy's target_tool.
- `condition` vs sentence: P2 edge condition ("every licensing_license_changes row with change_reason in_window_reduction ... has a licensing_billing row ... licensing_refund_credit ... in_window_reduction carrying its licensing_license_change_id") matches the sentence. P3 edge condition adds "whenever that invoice is past due beyond the grace period on the first of the month", which is the sentence's "late charge owed for the current month" spelled out, not a strengthening. P6 edges match.
- `effect` claims: P3 edge "the month's late charge raises the arrangement balance ... so the first instalment changes" is true only for a client without a dedicated-account-manager tier (with one, principal = balance - late charge cancels the late charge exactly and the setup-fee count excludes the past month), observation O1; P6/P4 effect holds only with an active ClearPath agreement; P6/P5 effect only when the cap binds (O2). Weight is judged per task.
- No authoring-viewpoint wording ("in this task", "at the opening") in any prerequisite field.

### prerequisite_sentences
Four-point test on each edge:
1. P2: "The late charge on a cycle invoice is fixed only after every in-window reduction recorded on the subscription carries its reduction credit on the billing ledger." Connective "only after"; waits on a record-visible state ("reduction credit on the billing ledger") in the ledger's and P1's own words; no tool, id or snake_case; strength "every ... recorded on the subscription" equals the condition. Writes that bring it about: only P1's tool posts a refund credit linked to an in-window reduction (the cancellation tool's credit is linked to its own removal row with charge_reason cancellation). Derivation: sentence -> ledger shows reduction 07efb06a-like rows without a linked credit -> the policy whose rule posts "the reduction credit" (P1) -> P1's write. Single reading.
2. P3: "The first instalment of a payment arrangement is not set until the late charge owed for the current month on the subscription's past-due cycle invoice stands on the billing ledger." "not ... until"; state; one writer (P2's tool is the only late-charge write). Single reading.
3. P6/a: "A cancellation refund is not fixed until the administration fee owed for every month the subscription was in force at month end stands on its billing ledger." State; one writer (P4). Single reading.
4. P6/b: "The cancellation refund is fixed only after every seat addition recorded on the subscription carries its partial-cycle charge on the billing ledger." State; one writer (P5). Single reading.
- The depended-on rules (P1, P4, P5, P2) do not restate the sentences; no rule carries a second wording, a tool name or another policy id; no rule states an undeclared cross-problem order; no base sentence is used to ground an edge.
- Charter-level caveat (O3): P1 credits and P5 charges only the latest reduction / seat addition, while P2 and P6 wait on "every" such record; a world with two pending records could not be brought to the waited-on state. Judged per task.

### override_declarations
Sentence-by-sentence over each `base_policy_refs` entry:
- P1 / `licensing_cancellation_window`: sentences 1-8 (NCE brevity, whole-cancellation window, no-source reduction window, source reduction window and quantity cap, elapsed-hour counting, window openings at purchase and 00:00 of each renewal term, after-window options) followed; the refund sentence superseded and declared (scoped, base content restated for other subscriptions, credited invoice changed from "next invoice" to "the invoice that billed the cycle"); "Licenses removed at expiry or by a renewal reduction are never refunded" followed. No undeclared departure.
- P2 / `licensing_billing_and_collections`: due date followed (days past due uses invoice_due_days); payment application and card limit followed; late-fee sentence superseded and declared (scoped to annual cycle invoices, base restated for every other invoice); suspension and reactivation followed. The catch-up share and multipliers live inside the superseded quantity.
- P3 / `licensing_billing_and_collections` (`overwrite: []`): payment application followed ("applied to the past-due cycle invoice", which the remittance names); card limit followed; the late-fee sentence is P2's; no base sentence governs arrangements, so no override is needed. The terminal-state conflict is with P3's own rule, not with base (finding F7).
- P4 / `licensing_admin_fee_rules`: sentence 1 superseded and declared; "a ClearPath Monitor agreement does not waive the fee" superseded and declared (half fee); "Expired and cancelled subscriptions carry no fee for the months after they ended" followed; the waiver sentence "no fee is posted for a month in which the client held a ClearPath agreement whose status was active or notice_given on the last day of the month ..." is not superseded but compute evaluates coverage at posting day (finding F5).
- P5 / `licensing_seat_additions`: term-end and locked price followed; status gate followed; charge sentence superseded and declared (scoped, base restated); "The initial purchase quantity is billed by the first cycle charge" followed (P5 charges change_reason seat_addition only); renewal increase sentence followed. P5 / `licensing_upgrades`: untouched, followed.
- P6 / `licensing_cancellation_window`: whole-cancellation window inherited; refund sentence superseded and declared (scoped, base restated, sibling named). P6 / `licensing_client_authorization`: signed order form and verified contact followed by the user tool; "Partial-cycle charges and refunds follow proration_basis, daily over the billing cycle" followed in form (all ladders count days over the cycle).
- Disguised forms: no anonymous intermediate (every intermediate is a named binding with a quotation), no 0/1 multiplier on a base-fixed quantity, no dropped base branch; no author note calls the base output wrong.

### factor_ladders
| Policy | Factor | Label | Tiers (fall-through last) | Multi-source | cross_difficulty |
|---|---|---|---|---|---|
| P1 | early_release_anchor | method | all cycle days / from source addition date / from reduction date | tier 1 yes (license change + subscription), tier 2 no | - |
| P1 | clearpath_change_fee | parameter | 0.00 / 10.00 / 25.00 | no | managed |
| P1 | posting_delay_goodwill | parameter | 50 / 25 / 0 | no | - |
| P1 | review_miss_goodwill | parameter | 5% / 2.5% / 0 | yes (renewal window + ClearPath tier) | managed |
| P2 | courtesy_rate | parameter | 1.0% / 1.25% / 1.5% | yes (ledger + renewal_count) | - |
| P2 | relationship_minimum | parameter | 50 / 35 / 25 | no | managed |
| P2 | first_period_accrual | method | d/30 / int(d/30) / 1 | tier 2 within one invoice | - |
| P2 | master_account_escalation | parameter | 1.5 / 1.25 / 1 | no | managed |
| P2 | good_faith_relief | parameter | 0.5 / 0.75 / 1 | no | - |
| P2 | invoice_size_scale | parameter | 0.8 / 0.9 / 1 | no | - |
| P3 | instalment_count | parameter | 6 / 4 / 3 | same agreement record | managed |
| P3 | down_payment_share | parameter | 25% / 10% / 0 | no | - |
| P3 | month_late_treatment | method | carve out, nothing up front / carve out, collected up front / whole balance | yes (licensing ledger + ClearPath tier) | managed |
| P3 | arrangement_setup | parameter | 0 / 15 / 25 | no | - |
| P4 | coverage_share | parameter | 0% / 50% / 100% | no | managed |
| P4 | commitment_term_adjust | parameter | 90% / 110% / 100% | no | - |
| P4 | tenant_volume_rate | parameter | 80% / 90% / 100% | no | - |
| P4 | security_baseline_upkeep | parameter | 0.25 / 0.50 / 0 | yes (plan param + Sentinel) | security |
| P4 | held_days_month_fraction | method | held/30 / 0.5 / 1 | no | - |
| P4 | backup_bundle_rate | parameter | 90% / 95% / 100% | yes (Continuum + license count) | backup |
| P5 | order_window_convention | method | all cycle days / 0 days / remaining days | yes (subscription + license change) | - |
| P5 | prepaid_hours_provisioning | parameter | 2 / 4 / 6 | no | timebank |
| P5 | addition_volume_discount | parameter | 5% / 2% / 0 | no | - |
| P5 | onboarded_staff_discount | parameter | 3% / 1.5% / 0 | compares two records | managed |
| P6 | prompt_cancel_anchor | method | all cycle days / from day after cancellation / from cancellation date | no | - |
| P6 | admin_fee_return | method | full / pro rata / none | yes (ClearPath + subscription age) | managed |
| P6 | order_reversal_fee | parameter | 50 / 25 / 0 | no | - |
| P6 | backup_deprovisioning | parameter | 0.50 / 1.00 / 0 | no | backup |
| P6 | seat_change_reversals | parameter | 10 each / 5 each / 0 | no | - |

- Counts: P1 4 (3p/1m), P2 6 (5p/1m), P3 4 (3p/1m), P4 6 (5p/1m), P5 4 (3p/1m), P6 5 (3p/2m). All within 4-6, at least 2 parameter and 1 method. Each tree carries multi-source and cross-difficulty factors ({P1,P2,P3}: review_miss_goodwill, courtesy_rate, month_late_treatment; managed. {P4,P5,P6}: security_baseline_upkeep, backup_bundle_rate, order_window_convention, admin_fee_return; managed, security, backup, timebank).
- Every ladder has 3 pairwise-disjoint tiers, every tier stated in its rule and implemented in its `decides` binding; no two tiers of a ladder share a value or method; `decides` is never `result`; binding sets disjoint. Every fall-through equals the baseline (`baseline.rule` and `baseline` bindings agree; each baseline.rule is self-sufficient and yields a definite number).
- Factor independence (XF A1), mechanical: following every binding each factor reads, transitively, reaches no other factor's binding in any policy; `result` (or a plain binding: P2 `monthly_charge`, P6 `licence_refund`) does the assembly. The rule-text exception is finding F2.
- Pairwise method-tier table (XF A6), distinguishing input in brackets:
  - early_release_anchor: T1 vs T3 differ in shape (credit independent of reduction date vs from it) [lag 1]; T2 vs T3 = the same proration "days from X through cycle end / cycle days" with X moved from the reduction date to the source addition date: a window-length swap (finding F3).
  - first_period_accrual: T1 d/30 vs T3 1 [d=20]; T2 int(d/30) vs T3 1 [d=65 gives 2]; T1 and T3 meet only at d=30 (single boundary point, O8).
  - month_late_treatment: carve-out with up-front collection vs carve-out without vs no carve-out change the instalment's terms, not a constant. Genuine.
  - held_days_month_fraction: T1 held/30 vs T3 1 [held 10]; T2 constant 0.5 vs T3 constant 1: a multiplier swap (finding F3).
  - order_window_convention: T1 full cycle vs T3 remaining days [lag 3]; T2 zero (deferral) vs T3 [remaining 5]. Genuine.
  - prompt_cancel_anchor: T1 full cycle vs T3 [lag 2]; T2 "from the day after the cancellation date" vs T3 "from the cancellation date" = the same proration with the window shortened by exactly one day (finding F3).
  - admin_fee_return: full vs pro rata vs none. Genuine (meet only when a renewed subscription is cancelled on its renewal day).
- Realism, tier by tier against what a Microsoft CSP reseller / MSP runs and against Microsoft's NCE terms (168-hour windows, premiums, seat caps, current-price renewal): no tier contradicts an NCE term (goodwill credits beyond Microsoft's prorated refund and reseller fees are the reseller's own pricing). relationship_minimum reproduces the ClearPath charter's own per-tier `late_fee_minimum_usd` (25 Monitor/Essentials, 35 Standard/Professional, 50 Premier/Enterprise), so it is grounded. The license-change fees in P5 and P6 contradict the "covered work" treatment of ClearPath tiers with m365_administration_included (finding F8). Lesser realism notes are observation O10.
- Structure only here; weight is per task (`factor_weight` in 0.md / 1.md).

### findings
Each finding: verdict, symptom -> root cause -> evidence -> demonstrated consequence -> location. "Bears on" names the task files that pick up the per-world demonstration.

**F1 — SOURCE-POLICY RED (XF A3, charter-level). Assembly sentences name the factor quantities, in all six policies.**
Symptom: every rule's "assembled in this order" sentence lists the factor quantities by name instead of a generic combination statement. Members (every extended policy):
- P1: "any review goodwill percentage is applied to that prorated amount; then any billing-delay goodwill is added and the license change fee is subtracted".
- P2: "the month's charge is the monthly late-charge rate applied to the past-due balance, or the late-charge minimum if greater; that month's charge is then multiplied by the share of the month charged and by the escalation, relief and size multipliers".
- P3: "the down-payment share is taken from the principal, the rest of the principal is divided by the number of instalments, and the first instalment is the down payment plus that equal share plus any late charge collected up front plus the setup fee".
- P4: "the per-license rate is admin_fee_usd multiplied by the commitment, volume and bundle percentages; any baseline upkeep amount per license is added to that rate; the resulting rate is multiplied by the licenses counted, by the share of the fee charged and by the part of the month charged".
- P5: "the addition volume and onboarding discount percentages are added together and that combined percentage is taken once off the prorated amount; then the provisioning fee per license times the licenses added is added".
- P6: "any administration fee returned is added; then the order reversal fee, the backup deprovisioning charge and the seat change reversal charges are subtracted".
Consequence: the combination sentence, which must be rendered once in the hub or the computation document, names every factor's quantity, so the computation document is no longer silent about any variation and factor documents are named from outside themselves (the XF class renderers hit after policy PASS). No scored value moves. Bears on: 0.md (P1-P3), 1.md (P4-P6) as charter-level only.

**F2 — SOURCE-FACTOR RED (XF A1/A5, charter-level). P3's down-payment factor works against "the principal", a quantity defined only inside another factor.**
Evidence: down_payment_share ladder "25 percent of the principal is due up front"; "principal" is defined only in month_late_treatment's sentences ("the principal being the arrangement balance less that late charge" / "the principal is the whole arrangement balance") and `principal` is listed in month_late_treatment's `bindings`; P3's baseline paragraph defines only "the arrangement balance". The mechanical binding check is clean (`down_pct` reads only `inv_cycle_total`), but the rule text makes the down payment act on another factor's output, and "principal" is used by two factors and defined by one.
Consequence: the down-payment factor document cannot state its effect without the month-late factor's definition. Its contribution changes with the other factor's tier (task 0 figures in 0.md). Location: P3 rule, factors down_payment_share / month_late_treatment. Bears on: 0.md.

**F3 — SOURCE-FACTOR RED (XF A6, charter-level). Three method tiers only swap a window length or a constant multiplier against the fall-through.**
- P1 early_release_anchor T2 "credited days run from the date part of that seat addition's submission moment through the last day of the cycle inclusive" vs fall-through "from the date part of the reduction's submission moment through the last day of the cycle inclusive": the same proration with the start date moved.
- P6 prompt_cancel_anchor T2 "the refunded days run from the day after the cancellation date through the last day of the cycle" vs fall-through "from the cancellation date through the last day of the cycle inclusive": the same proration, one day shorter (compute `DAYS(NOW, end)` vs `DAYS(NOW, end) + 1`).
- P4 held_days_month_fraction T2 "charged half the month" (0.5) vs fall-through "the full month" (1): a constant multiplier.
Consequence: these tiers are parameter tiers labelled method. In each factor the remaining tier (T1) is a genuine method change, so each policy still has an honest method factor and the per-task counts stand. Neither task takes any of these tiers. Bears on: no task's scored value (charter-level).

**F4 — SOURCE-POLICY RED (XF B14, charter-level). P5's TimeBank provisioning tier is a first-match read that a second active block defeats.**
Evidence: rule "with an active TimeBank block whose hours balance is 10 hours or more it is 2.00 USD; with an active TimeBank block holding fewer than 10 hours it is 4.00 USD"; compute `tb_hours: CFIELD('timebank', 'hours_balance', status='active')` returns the first active block only. The blueprint's TimeBank line itself describes clients holding several blocks ("how many blocks the client holds").
Demonstration (scratch copy of the task-1 world, a second active 10-Hour block with 3.0 hours inserted ahead of the 14.5-hour block): the rule gives 2.00 USD (an active block with at least 10 hours is held), compute gives `prov_fee` 4.00 and P5 = 265.66 instead of 257.66. Location: P5 rule/compute `tb_hours`, `prov_fee`. Task 1 has one active block, so no scored effect there.

**F5 — SOURCE-POLICY RED (XF C18, charter-level). P4 reads ClearPath coverage at the posting day, while the in-force base waiver anchors it on the last day of the month.**
Evidence: base `licensing_admin_fee_rules` (not superseded): "no fee is posted for a month in which the client held a ClearPath agreement whose status was active or notice_given on the last day of the month and whose tier has m365_administration_included true"; P4 rule "where the client holds a ClearPath agreement whose status is active or notice_given ..." and compute `CPARAM('managed', 'm365_administration_included', status='active')` evaluated at NOW (the 1st of the following month). Neither overwrite names the waiver sentence.
Consequence: an agreement whose termination takes effect on the month's last day (status notice_given on that day, moved on by the 1st) gets no fee under the base sentence and a 100 percent fee under P4's compute. Two in-force clauses decide one quantity differently. Location: P4 overwrite list / compute `cov_*`. Task 1's Monitor agreement is active on both days, so no scored effect there.

**F6 — SOURCE-POLICY RED (check 3 / XF D19, charter-level). Tool bodies hard-code the term-start cycle, which contradicts the policy for subscriptions billed by a shorter cycle.**
Evidence: `cancel_subscription_in_window_d46a60fb` takes no invoice argument and credits the cycle charge whose `cycle_start_date == term_start_date`. Yet P6's replaced_by says "the cancellation of any other subscription is still refunded ... and credited to the next invoice", and the tool's docstring says "against the invoice that billed the current cycle". For a P1Y term billed monthly, that invoice is the first month's, which is neither the current cycle's nor the next one. `post_seat_addition_charge_bba679a2` says "in the billing cycle the subscription is in" but stamps `cycle_start_date=sub["term_start_date"]`. That is false for monthly-billed P1Y/P3Y seat additions, which this tool also has to post under the base rule.
Consequence: for an out-of-scope cancellation the only write cannot reach the terminal state the charter states. No effect in either task (both subscriptions bill their whole term as one cycle).

**F7 — SOURCE-POLICY RED (terminal state; demonstrated in 0.md). P3's setup fee is booked as a payment against the invoice.**
Evidence: P3 rule "the standard arrangement setup fee of 25.00 USD is collected with the first instalment"; the first instalment is "the down payment plus that equal share plus any late charge collected up front plus the setup fee". The only write, `pay_arrangement_instalment_a0d5f2e9`, "books one payment entry applied to the invoice named and lowers the balance the client owes on the subscription by the amount paid". No write in the difficulty posts the setup fee as a charge.
Consequence: the fee the rule collects as Stratton Bay's charge is applied to the past-due invoice and lowers the client's debt by the same amount, so the terminal ledger contradicts the rule (task 0 figures in 0.md). Location: P3 rule / pay_arrangement tool contract. Bears on: 0.md.

**F8 — SOURCE-POLICY RED (XF D21 realism and cross-category consistency, charter-level). License-change fees are charged to clients whose ClearPath tier covers Microsoft 365 administration.**
Evidence: managed charter `m365_administration_included`: "Whether Microsoft 365 tenant administration (user, mailbox and license changes) is covered work". This is true on every tier except ClearPath Monitor. P1's own rule: "where the client holds a ClearPath agreement ... m365_administration_included true, the change is covered work and the fee is 0.00 USD". Yet:
- P5 prepaid_hours_provisioning charges a provisioning fee per license added (6.00, or 2.00/4.00 with TimeBank hours) with no coverage tier, so a ClearPath Standard client adding seats pays it.
- P6 seat_change_reversals charges "5.00 USD for each seat addition ... 10.00 USD for each" Partner Center change, and order_reversal_fee charges 25/50 USD for reversing an order, both regardless of coverage.
Consequence: the same work (a license change for a covered client) is fee-free in P1 and fee-bearing in P5/P6. An MSP whose agreement covers license changes would not bill per-change fees for them. Members: P5 prepaid_hours_provisioning (all tiers), P6 seat_change_reversals, P6 order_reversal_fee. Neither task has a covered client on these policies (task 1 holds ClearPath Monitor), so no scored effect.

Observations (no demonstrated consequence; not grounds for rework):
- O1: P3 edge `effect` is false for dedicated-account-manager tiers (Professional/Premier/Enterprise): principal = balance - late charge cancels the posted late charge and the setup-fee count excludes the past month, so the edge would carry no weight in such a world.
- O2: P6/P4 edge weight needs an active ClearPath agreement (admin_return is 0 otherwise); P6/P5 weight needs the cap to bind.
- O3: P2 and P6 wait on "every" in-window reduction / seat addition, while P1 and P5 write only the latest one.
- O4: `RND` is Python round (half-even on the binary value) while every rule says half up; no tie arises in either world.
- O5: P1 review goodwill: the lead clause "shows that Stratton Bay's pre-renewal license review missed licenses" is applied by compute to every renewal-window reduction. A ClearPath tier with 0 vCIO reviews is not named in the no-goodwill sentence (compute gives 0).
- O6: P6 seat_change_reversals opens "Each seat addition reversed with the cancellation" but prices "each seat addition recorded on the subscription"; the two differ for a renewed subscription with prior-term additions.
- O7: P4 coverage_share ladder text adds "AND its tier's m365_administration_included is false", which holds of every Monitor agreement and is absent from the rule.
- O8: first_period_accrual T1 meets the fall-through at d = 30 only.
- O9: P1 does not state the case of a named source addition whose record is absent (compute falls back to the standard method).
- O10: realism notes: billing-delay goodwill is unusual but plausible service recovery; P5 T1 bills seat additions for days before they existed (reseller pricing, not an NCE contradiction); the per-change rate rises with the count in seat_change_reversals.
- O11: P6 baseline "Stratton Bay's administration fee and order charges are left as billed" sits beside a cap that includes provisioning fees inside "the partial-cycle charges". The definitional sentence decides it (the cap includes them).

## closing_checklist
Written after both reveals (2026-10-18T02:02:29Z onward). Nothing above this heading was changed after a reveal; only freeze timestamps were corrected to file mtimes before the reveal.
- Per-task files: 0.md and 1.md correspond one-to-one with tasks/0.json and tasks/1.json; this file sits alongside. First round, no older revision.
- Comparison sections: every value, tree edge, load-bearing figure and factor_sensitivity / baseline_result figure matches the frozen derivations in both tasks. Neither comparison is a full PASS: task 0 carries 0-R1 (SOURCE-POLICY, F7's terminal-state consequence) and 0-R2 (SOURCE-FACTOR, XF D20); task 1 carries 1-R1 and 1-R2 (SOURCE-FACTOR, XF D20).
- Coverage and scope: charter_scope task 0 = {reduction_credit, late_charge, payment_arrangement} with their three tools; task 1 = {admin_fee, seat_partial_charge, window_cancellation} with their three tools. Pairwise disjoint and jointly complete over the six extended policies and six task tools. uuid8s independent (§ action_binding_and_uuids).
- Trees: each has 2 prerequisite problems, 2 value_input edges, one owner=user write, no cycle. The difficulty-wide graph {P3->P2->P1, P6->P4, P6->P5} is acyclic.
- Factors: 14 (task 0) and 15 (task 1) declared factors, all bearing weight against honest baselines. Whole-baseline figures are definite and differ from gold (780.56/41.55/955.47; 67.50/269.28/1773.90). Charter-level structure defects F2 and F3 stand.
- Gates: not re-run by this auditor (coordinator snapshot r1 cited in § charter_global_frozen). The difficulty does not close: the charter carries F1-F8 and both tasks carry REDs.
- Outcome: the source-layer audit does NOT pass for revision_1.

VERDICT revision_1: task0=RED:0-R1,0-R2 task1=RED:1-R1,1-R2 charter=F1,F2,F3,F4,F5,F6,F7,F8

## revision_2

## charter_global_frozen (revision_2)
- Re-audit round 2. The gate tail line was checked first: the last line of tasks/microsoft_365_subscriptions/worklog.md is exactly `REWORK round 2: gates 7/7 green` (read with `tail -1` only).
- The coordinator snapshot was executed (not read): `/tmp/erl0069_coord/snapshot.sh microsoft_365_subscriptions 2` @ 2026-10-18T03:59:26. Output:
  - check_extended, check_task_tools, replay_tasks, check_solvability, check_compute, check_grounding, check_cross_fire: all rc=0.
  - r2/0.view.json 48aa22b49cef523a5676f2ce08b3882e6c54f1500f32b8582dcb618875d53118
  - r2/1.view.json 73eabdb51a89dce5d09d342875e7ca6faec8f00bf41b10da5a59863943cdd266
  - licensing.extended.yaml f46b53eaef206ee1b5ea728b9694c06d8c5784bec4d0d9f44b1c81d45120fbe9
  - task_tools.py faef8af49769237d072f5b4419c073782c13255b65131f41c54ca57027e31591
- Both shared inputs changed against revision_1 (7ca6f8e4... / 8af718a7...), so every charter-global section below is re-derived in full; nothing is carried forward by reference.
- This section was written from the round-2 charter, the round-2 tools, the blueprint and XF_recipe.md only. The round-2 claims list in worklog.md (above its tail line) and tasks/*.json were not read before both task derivations were frozen. Base copy re-checked: verbatim, apart from the trailing blank line.

### policy_conflict_scan (r2)
- Same six policies, tools, owners and triggers as revision_1. P3's setup fee has been replaced by `front_loading`, a weighting of the first instalment's share, and P3 now states "an arrangement carries no fee".
- Overlapping subjects:
  - P1 and P6 still split `licensing_refund_credit` by object and name each other's case.
  - Each now adds a credited-invoice sentence covering every in-window reduction (P1) or every whole cancellation (P6): "credited to the invoice that billed the cycle it refunds, not to the next invoice". These sentences are declared in the replaced_by and are matched by the tools, which now take `invoice_number` and `cycle_start_date`.
- The P4 time anchor is now declared: the base waiver sentence is superseded, and the replaced_by takes coverage "as it stands on the day the fee posts, which Stratton Bay takes for the month just ended".
- Cross-category: P5 and P6 now exempt clients whose ClearPath tier covers Microsoft 365 administration from the provisioning, order-reversal and seat-change charges, consistent with P1's "covered work".
- The two trees and their scope split are unchanged.

### rule_compute_equivalence (r2)
- Mechanical sweeps (scratch): 0 compute_basis quotations missing from their rules; 0 baseline sentences missing; every compute binding has a compute_basis entry; no factor id is a substring of any tool name.
- Changed bindings, rule against compute:
  - P1 `std_prorated` / `src_charge` / `src_qty` / `prorated` match "How the prorated amount is worked out follows what the reduction releases ...", including the stated no-charge / no-record fall-back.
  - P3 `down_amt` = arrangement balance x down percentage; `late_carved` / `late_upfront`; `share_weight`. These match the rule's down-payment, late-charge-treatment, front-loading and order sentences.
  - P4 `month_part` T2 = (30 - min(DAYS(suspended_date, NOW), 30)) / 30, matching "30 less the calendar days from its suspended_date up to the posting day (never less than nothing), over 30".
  - P5 `tb_hours` = granted + rolled_in + draw_reversed - drawn - rolled_out - forfeited across all blocks (XSUM). This matches "granted, rolled in and restored less those drawn, rolled out and forfeited, across all its blocks"; draw_reversed is the TimeBank charter's "hours restored".
  - P5 `covered_work` matches the covered-work sentence.
  - P6 `refund_base` T2 = cycle amount x licenses x (MONTHS(NOW, end) + 1) / 12, gated on renewal_count >= 1 and annual billing, matching "a P1Y term billed annually that has renewed at least once ... whole months ... plus the month in progress, divided by 12".
  - P6 `covered_work` and `change_rate` (5.00 for 1-2, 4.00 for 3+) match the rule.
- Revision-1 notes resolved: P3 now carries the same-day tie sentence; P1 names the zero-vCIO case ("a client whose active ClearPath tier provides no vCIO review"); P6 seat-change wording is now "Every seat addition recorded on the subscription is reversed with the cancellation".

### action_binding_and_uuids (r2)
- Same six `(target_tool, computes)` pairs, each claimed once. uuid8s unchanged and independent.
- New arguments: `cycle_start_date` on post_reduction_credit, post_seat_addition_charge and cancel_subscription_in_window, and `invoice_number` on cancel. Their docstrings give the format only ("written YYYY-MM-DD exactly as the cycle start appears on the billing ledger"), with no example values, no ordering words and no tool names.
- The bodies now stamp the cycle and invoice named, so "in the billing cycle named" and "against the invoice and billing cycle named" are true. The tools still validate no prerequisite.

### prerequisite_graph (r2)
- Unchanged: four state-form value_input edges, acyclic, each policy_source verbatim in its own rule (sweep 4/4), gates existing, resolved_by correct.
- `effect` wordings revised. The P3 edge now holds even for a dedicated-account-manager tier, because the down payment is a percentage of the arrangement balance that the late charge raises. Probe on a scratch copy of the task-0 world switched to ClearPath Professional: 798.02 with the late charge vs 796.30 without. Observation O1 is closed. P6 effects are now qualified ("where an active ClearPath agreement is held", "wherever it binds").

### prerequisite_sentences (r2)
The four sentences are unchanged and pass the four-point test as in revision_1, each with exactly one writer. O3 (the "every" vs latest-only reach) is unchanged; it remains an observation.

### override_declarations (r2)
- P1 / P6: refund sentence superseded and scoped. The added credited-invoice sentence changes the base "credited to the next invoice" for every in-window reduction (P1) and every whole cancellation (P6), and is declared inside each replaced_by. Base content restated for out-of-scope subscriptions; siblings named.
- P2: unchanged.
- P3: `overwrite: []`. No base sentence governs arrangements. "carries no fee" adds nothing that contradicts base.
- P4: both base sentences, the posting sentence and the waiver plus Monitor sentence, are now superseded and declared. Revision-1 F5 is closed.
- P5: unchanged declaration. The covered-work exemption lies inside the superseded charge quantity.
- No undeclared departure found.

### factor_ladders (r2)
Changes from revision_1:
- P1 early_release_anchor (method; decides `prorated`): T1 cycle amount x licenses removed, no day count; T2 the source seat addition's partial-cycle charge x removed / added; T3 standard prorated amount.
- P3: arrangement_setup removed. `front_loading` (parameter): 1.5 / 1.25 / 1 shares by earlier late charges in 24 months. down_payment_share is now "percent of the arrangement balance".
- P4 held_days_month_fraction T2: the part of the 30-day month before the suspension.
- P5 prepaid_hours_provisioning: ledger hours across all blocks.
- P6 prompt_cancel_anchor T2: by the month (renewed P1Y annual). seat_change_reversals: 5.00 / 4.00 / 0.
Counts: P1 4 (3p/1m), P2 6 (5p/1m), P3 4 (3p/1m), P4 6 (5p/1m), P5 4 (3p/1m), P6 5 (3p/2m). Multi-source and cross-difficulty per tree unchanged. Every fall-through equals its baseline; no two tiers of a ladder select the same value or method as stated.

XF recipe, every point on every policy:
- A1: transitive binding walk finds no factor reaching another's binding in any policy. down_payment_share now acts on "the arrangement balance", a baseline quantity, so revision-1 F2 is closed.
- A2: shared selections (`in_renewal_window`, `covered_work`, `inv`) are plain bindings.
- A3: every combination sentence is now generic and names kinds only. For example, P1: "those that change how the prorated amount is worked out come first, percentage additions then act on that prorated amount, and fixed amounts are added or subtracted last"; P6: "amounts returned are then added and charges subtracted". Revision-1 F1 is closed in all six policies.
- A4: order fixed wherever adjustments do not commute (P1 percentage before fixed amounts; P2 replacements before multipliers; P3 set-asides before division; P4 percentages, then per-license amounts, then shares; P5 days, then discounts, then per-license amounts; P6 refund method, then cap, then additions and subtractions).
- A5: one member remains (finding G2).
- A6, pairwise tier table on reachable domains:
  - early_release_anchor: T1 vs T3 differ [lag 1]; T2 vs T3 differ (ledger charge vs day count). Revision-1 member closed.
  - held_days_month_fraction: T2 is data-derived [suspended 10 days -> 20/30] vs T3 1; it meets T3 only when suspension falls on the posting day. Revision-1 member closed.
  - first_period_accrual, month_late_treatment, order_window_convention, admin_fee_return: as in revision_1, genuine.
  - prompt_cancel_anchor: T2 coincides with T1 on its whole reachable domain (finding G1).
- A7: clean.
- B8-B10: clean.
- B11: ties stated (P3 added).
- B12: P2 and P3 month windows match MONTHS. P6 T2 states no month-end convention, but on the reachable domain MONTHS always returns 11 (see G1).
- B13: absent cases stated (P1 no-record source, P5 no hours).
- B14: P5 now aggregates across blocks; revision-1 F4 closed. Remaining CFIELD reads are on single-holding categories.
- B15: n/a.
- C16, C17: each replaced_by names its scope and the sibling.
- C18: no undeclared departure (F5 closed).
- D19: docstrings are format-only and claim no effect the body lacks; revision-1 F6 closed.
- D21 realism: revision-1 F8 closed (the covered-work exemptions match the managed charter's m365_administration_included). Front-loading and part-month-before-suspension are practices an MSP plausibly runs.

### findings (r2)
**G1 — SOURCE-FACTOR RED (XF A6, charter-level). P6 prompt_cancel_anchor T2 ("refunded by the month") equals T1 ("refunded as never used") on its whole reachable domain.**
- Evidence: T2 applies only to a renewed P1Y term billed annually cancelled more than three days after the renewal window opened. The base `cancel_in_window` gate (168 hours) confines that to 4-7 days after the term start. Term end is the day before the anniversary, so `MONTHS(NOW, term_end_date)` is always 11, and (11 + 1) / 12 = 1.
- Probe on a scratch copy of the task-1 world turned into a renewed P1Y annual subscription:
  - term start 2026-09-27 (lag 4) and 2026-09-24 (lag 7): months_left 11, refund_base / (cycle amount x licenses) = 1.0, identical to T1;
  - it differs (0.9167) only at lag 31, which the window makes unreachable.
- Consequence: two tiers of one ladder select the same refund on every input that can reach them, so T2 is T1 written twice and the ladder has two effective tiers.
- Location: P6 rule, prompt_cancel_anchor. Neither task takes T2, so no scored value moves. New in revision_2 (introduced by the F3 rework).

**G2 — SOURCE-POLICY RED (XF A5, charter-level). P1's opening lag is used only by early_release_anchor but is defined in the shared renewal-window sentence and is not among the factor's bindings.**
- Evidence: the sentence "A reduction counts as made in a renewal window when ... , and its opening lag is the calendar days from the date the window opened to the reduction's submission date". `opening_lag` is read only by `prorated` (early_release_anchor's decides binding); early_release_anchor.bindings = [src_charge, src_qty, prorated].
- Consequence: a quantity only one factor uses lives outside that factor's own sentences. A renderer placing the shared renewal-window sentence carries early_release_anchor's lag into the other factor's (review_miss_goodwill's) material. Placement-level; no scored value moves.
- The text is unchanged since revision_1. It was not raised there (auditor miss), so it is not a regression.

Observations (r2):
- O3 unchanged.
- O4 unchanged (RND half-even; no ties in either world).
- O12 (new): the covered-work exemptions in P5 and P6 are a two-way variation in a plain binding (`covered_work`), outside every factor ladder and outside baseline.rule. For a covered client, prepaid_hours_provisioning, order_reversal_fee and seat_change_reversals contribute nothing whatever their tier, so they cannot bear weight in such a world. No task here has a covered client on these policies.

## closing_checklist (revision_2)
Written after the round-2 reveals (worklog claims and tasks/*.json at 2026-10-18T04:06Z onward). Nothing in § revision_2's charter-global sections was changed after the reveal.

Revision-1 items against the round-2 claims (each verified on the artifacts, not taken from the claim):
| Item | Status | Basis |
|---|---|---|
| F1 (A3) | CLOSED | Six generic combination sentences that name kinds only (§ factor_ladders (r2)). |
| F2 (A1/A5) | CLOSED | The down payment is a percentage of the arrangement balance; "principal" is gone. |
| F3 (A6) | PARTLY CLOSED | early_release_anchor T2 and held_days T2 are genuine. prompt_cancel_anchor T2 now coincides with T1 on its reachable domain (G1). |
| F4 (B14) | CLOSED | Ledger XSUM across blocks. |
| F5 (C18) | CLOSED | Waiver sentence superseded and restated. |
| F6 (D19/check 3) | CLOSED | Tools take invoice / cycle; bodies match docstrings; the replaced_by sentences match. |
| F7 / 0-R1 | CLOSED | No fee; the terminal ledger equals the rule. |
| F8 (D21) | CLOSED | Covered-work exemptions in P5 and P6; seat-change rate falls with volume. Side effect recorded as O12. |
| 0-R2 | CLOSED | ClearPath rows priced by the managed charter. |
| 1-R1 | CLOSED | TimeBank orders, invoices, payments and ledger consistent. |
| 1-R2 | PARTLY CLOSED | Records present and priced; onboarding ticket scope contradicts the managed scope rule (1-R3). |
| O1, O5, O6, O7, O9, O11, task-1 observations (order form, Continuum term) | CLOSED | — |
| O3, O4 | OPEN (observations) | — |

- Regressions: none. Every value and figure the rework did not target is unchanged (880.25, 21.66, 3.55, 257.66, 1884.41 and all their factor and baseline figures). The two trees, the edges, the scopes, the uuid8s and the gate snapshot are unchanged, and the snapshot is green.
- New this round: G1 (introduced by the F3 rework), G2 (pre-existing, newly raised), 1-R3 (introduced by the 1-R2 seed rework), O12 (introduced by the F8 rework).
- Coverage, scope exclusivity, trees (2 prerequisites, 2 value_input edges, one user write, acyclic) and factor weight against honest baselines: hold in both tasks. Whole-baseline figures differ from gold (780.56 / 41.55 / 930.47; 67.50 / 269.28 / 1773.90).
- Gates: coordinator snapshot r2 is all green (cited above); not re-run by this auditor.
- Outcome: the difficulty does NOT pass the source-layer audit at revision_2 (task 1 RED, charter G1/G2).

VERDICT revision_2: task0=PASS task1=RED:1-R3 charter=G1,G2

## revision_3

## charter_global_frozen (revision_3)
- Gate: the last line of tasks/microsoft_365_subscriptions/worklog.md is exactly `REWORK round 3: gates 7/7 green` (read with `tail -1` only).
- Executed (not read) `/tmp/erl0069_coord/snapshot.sh microsoft_365_subscriptions 3` @ 2026-10-18T04:21:25:
  - check_extended, check_task_tools, replay_tasks, check_solvability, check_compute, check_grounding, check_cross_fire: all rc=0.
  - r3/0.view.json 58ed8adf1d02529adcbe7bf1e9cea7f90817f6cf02e3287da75c6c10858782b3
  - r3/1.view.json 315b69c6c0fc2247dde18f87eee15890e3ccf6624a34705a69e6f6ace3a34f6e
  - licensing.extended.yaml 2147440cc4f356501c43f87a07c228261af593e81ad561fbd0fc37d545832ec1 (changed from r2 f46b53ea...)
  - task_tools.py faef8af49769237d072f5b4419c073782c13255b65131f41c54ca57027e31591 (unchanged from r2)
- Consequences: the tool-module sections (action_binding_and_uuids, docstrings) carry forward from revision_2 on the unchanged hash faef8af4.... Every charter section is re-derived, because the charter hash moved.
- The round-3 claims (worklog) and tasks/*.json were not read before both task derivations were frozen. Base copy still verbatim.

### What changed in the charter (r2 -> r3, from a diff of the round-2 dump against the current file)
- P1: the opening-lag definition moved into early_release_anchor's own sentence, and `opening_lag` is now in its bindings.
- P2: days past due moved into first_period_accrual's sentence and bindings; the plain `monthly_charge` binding is folded into `result`.
- P3: the arrangement's-invoice definition moved into down_payment_share's sentence; `inv` and `down_amt` are now that factor's bindings.
- P4 / P5 / P6: factor sentences now name the result quantity ("on the administration fee", "to / on the partial-cycle charge", "deducts ... from the cancellation refund"). P5 / P6 fee sentences open "For license work not covered by ClearPath".
- P6 prompt_cancel_anchor T2 is replaced. The new T2 applies when the cancellation is more than 3 days after the window opened but no more than 3 days after the latest seat addition, and that addition carries a partial-cycle charge. The addition's licenses are then refunded as never used (its partial-cycle charge in full) and the other licenses under the standard day count.

### Re-derived sections (r3)
- policy_conflict_scan: unchanged conclusions (trees, scopes, sibling overwrites, covered-work consistency).
- rule_compute_equivalence: sweeps give 0 quote misses, 0 baseline-sentence misses and 0 bindings without basis. The new P6 `refund_base` T2 matches its sentence: cx_add_charge + cycle amount x (licenses held - added) x days / cycle when DAYS(latest addition, NOW) <= 3 and its charge > 0.
- prerequisite_graph / prerequisite_sentences: unchanged; 4/4 sources verbatim; one writer each.
- override_declarations: unchanged; no undeclared departure.
- factor_ladders: counts P1 4 (3p/1m), P2 6 (5p/1m), P3 4 (3p/1m), P4 6 (5p/1m), P5 4 (3p/1m), P6 5 (3p/2m). Fall-through equals baseline everywhere.

### XF recipe, every point (1-26) on every policy (r3)
- A1: the transitive binding walk reaches no other factor's binding (0 hits).
- A2-A4: as revision_2; clean.
- A5: G2 member resolved (opening lag is now in early_release_anchor's sentence and bindings). No other single-factor quantity sits outside its factor.
- A6 / point 23 (method-shape, all pairs; the same field's aggregates count as one input, constants ignored):
  - early_release_anchor: T1 amt x qty | T2 src_charge x qty / src_qty | T3 amt x qty x days / cycle. T1-T2: T2 adds an input (billed charge). T1-T3: T3 adds an input (days). T2-T3: different inputs. PASS.
  - first_period_accrual: T1 M x d/30 | T2 M x floor(d/30) | T3 M. T1-T2: floor. T1-T3 and T2-T3: input d. PASS.
  - month_late_treatment: T1 subtracts L from the spread | T2 adds L up front and subtracts it from the spread | T3 neither. Each pair adds an operation or input. PASS. The decides binding `late_upfront` is 0 in both T1 and T3, but T1 acts through `late_carved`, so the "nothing" clause does not bite (observation O13).
  - held_days_month_fraction: T1 held/30 | T2 (30 - min(s, 30))/30 | T3 1. Each pair adds an input or a min. PASS.
  - order_window_convention: T1 amt x qty (no day input) | T2 0 | T3 amt x qty x remaining / cycle. The "nothing" tier T2 is 0, and no other tier is 0 across its domain. PASS.
  - prompt_cancel_anchor: T1 amt x lic | T2 cx_add_charge + amt x (lic - add_qty) x days / cycle | T3 amt x lic x days / cycle. T2 adds an input (billed charge) and an operation. Probe on a scratch copy of the task-1 world with the window 5 days old and the addition 1 day old: T2 1795.04 vs T1 1971.00 vs T3 1773.90. G1 closed.
  - admin_fee_return: T1 billed | T2 billed x days / cycle | T3 0. T3 is a "nothing" tier, and T1/T2 are non-zero for an active Monitor client, so they are not 0 across their domain. PASS.
- A7: clean.
- B8-B15: clean (as revision_2, plus the new T2 above). The P6 T2 window ("no more than three calendar days after the latest seat addition") is a DAYS test matching compute.
- C16-C18: clean.
- D19: tool module unchanged; clean.
- D20 / point 25 (complete ledgers): judged per task world (see the 0.md / 1.md r3 sections). The seeded window is read per ledger, from its earliest seeded row to frozen_time.
- D21: clean.
- D22: proof text is swept after reveal.
- Point 24 (trigger rule). The tools write licensing_refund_credit (post_reduction_credit, cancel), licensing_late_fee, licensing_payment, licensing_admin_fee, licensing_prorated_charge, licensing_cancelled_in_window (status), licensing_licenses_removed (cancel) and licensing_change_requests intake. Base triggers:
  - cancelled_in_window -> licensing:licenses_removed
  - licenses_removed -> licensing:refund_credit
  - all others -> [] (refund_credit, late_fee, payment, admin_fee, prorated_charge).
  None crosses into another category. CLEAN.
- Point 26:
  - (a) Plain bindings never read factor-owned bindings. Mechanical check over every non-factor, non-result binding in all six policies: 0 hits (r2's P2 `monthly_charge` is now folded into result). CLEAN.
  - (b) No rule word refers to a field the records lack: source_change_id, suspended_date, cycle_start_date and the TimeBank ledger event types (granted / drawn / draw_reversed = "restored" / rolled_in / rolled_out / forfeited) all exist in db_schema. CLEAN.
  - (c) Each factor names the result quantity it modifies. Literal phrase test: 8 factors lack the literal result phrase (relationship_minimum, instalment_count, commitment_term_adjust, tenant_volume_rate, backup_bundle_rate, order_window_convention, prompt_cancel_anchor, admin_fee_return). Each names a component its own baseline paragraph defines inside the result: "late-charge minimum"; "instalments"; "administration rate" (the per-license admin_fee_usd); "the days charged / billed as part of the order"; "the license refund" (the baseline's "the cancellation refund is the license refund"); "Stratton Bay's administration fee ... returned" (the baseline's "administration fee is left as billed"). Judged CLEAN on that reading; the literal list is recorded as observation O14 for the coordinator.

### findings (r3)
- G1: CLOSED (new prompt_cancel_anchor T2 passes the all-pairs test; probe above).
- G2: CLOSED (opening lag in early_release_anchor's own sentence and bindings).
- No new charter-level RED.
- Observations: O3, O4 unchanged. O12 (covered-work variation outside the ladders) unchanged in compute; the factor sentences now carry "For license work not covered by ClearPath". O13 and O14 as above.

## closing_checklist (revision_3)
Written after the round-3 reveal (2026-10-18T04:25:30Z onward). The r3 charter-global sections above were unchanged after the reveal, except the O12 status line below.

| Item | Status | Basis |
|---|---|---|
| G1 (A6/23) | CLOSED | New prompt_cancel_anchor T2 adds an input (the billed seat-addition charge); probe 1795.04 vs 1971.00 vs 1773.90. |
| G2 (A5) | CLOSED | Opening lag in early_release_anchor's sentence and bindings; class swept (days past due -> first_period_accrual; arrangement's invoice -> down_payment_share). |
| 1-R3 (D20) | CLOSED | Onboarding tickets billable_out_of_scope, labor drawn from TimeBank, ledger reproduces 12.0 h. |
| XF 23 (method shape, all pairs) | CLEAN | Seven method factors, all pairs pass (§ revision_3 XF). |
| XF 24 (trigger rule) | CLEAN | Every event the tools write triggers only licensing events or none. |
| XF 25 (complete ledgers) | CLEAN in both worlds | 0.md / 1.md r3. |
| XF 26 (plain bindings, field words, result named) | CLEAN | 0 plain->factor reads; fields exist; result-quantity reading as stated (O14). |
| O12 | CLOSED | The covered-work sentence is now in baseline.rule of P5 and P6 (checked), so each baseline is complete for covered clients and the fee ladders are scoped to uncovered work. |
| O3, O4, O13, O14 | Observations | Not grounds for rework. |

- Regressions: none. All six scored values and every factor / baseline figure are identical to revision_2. Trees, edges, scopes, uuid8s and the tool module (hash unchanged) are unchanged.
- Step-4 list:
  - Per-task files correspond one-to-one with the tasks, revisions 1-3 are kept, and both comparison sections PASS.
  - The six extended policies are covered once each by disjoint scopes; tools and GT are closed; uuid8s are independent.
  - Each tree has 2 prerequisite problems, 2 value_input edges, one owner=user write and no cycle; the difficulty graph is acyclic.
  - Every computation has a self-sufficient baseline and 4-6 factors (at least 2 parameter and 1 method; each task has multi-source and cross-difficulty factors). Every ladder has 3 tiers stated in its rule, distinct in outcome and realistic. Every factor bears weight, and each whole baseline differs from gold (780.56 / 41.55 / 930.47; 67.50 / 269.28 / 1773.90).
  - Gates: coordinator snapshot r3 all green.
- Outcome: the difficulty PASSES the source-layer audit at revision_3.

VERDICT revision_3: task0=PASS task1=PASS charter=CLEAN

## revision_4

## charter_global_frozen (revision_4)
- Gate: the last line of worklog.md is exactly `REWORK round 4: gates 7/7 green` (`tail -1`).
- Executed (not read) `/tmp/erl0069_coord/snapshot.sh microsoft_365_subscriptions 4` @ 2026-10-18T10:23:10:
  - check_extended, check_task_tools, replay_tasks, check_solvability, check_compute, check_grounding, check_cross_fire: all rc=0.
  - r4/0.view.json 58ed8adf1d02529adcbe7bf1e9cea7f90817f6cf02e3287da75c6c10858782b3 and r4/1.view.json 315b69c6c0fc2247dde18f87eee15890e3ccf6624a34705a69e6f6ace3a34f6e (both identical to r3).
  - licensing.extended.yaml 7436fc6a3a760c38b86b83240b0e31d3d2dbb4b05d567e20d4743787dd71da81 (changed); task_tools.py faef8af4...e31591 (unchanged).
- The tool-module sections carry forward on the unchanged hash. The charter sections are re-derived. Both task derivations are recomputed on the r4 charter (the views are unchanged).
- RED input of this round: audits/render_source/microsoft_365_subscriptions/render_r1.md, read in full (renderer findings F1-F4, raised after my revision_3 PASS). The round-4 claims were read after this input, as instructed. tasks/*.json were not read before the task freezes below.

### Renderer findings F1-F4, verified on the artifacts (not taken from the claims)
- **F1 (B8/B13)** — P3 instalment_count.
  - Compute is now `cp_owed <= 0` and the rule says "owes nothing (a balance of zero or a credit)". For an active agreement the two tiers are exact complements (renewed >= 2 and owes <= 0, vs renewed < 2 or owes > 0).
  - Probe (scratch, task-0 world with ClearPath balance -150.00): 6 instalments, P3 = 819.68.
  - CLOSED.
- **F2 (B12)** — P5 onboarded_staff_discount.
  - The dated "less than one whole month" window is gone. The factor now uses a record test: seats the active ClearPath agreement covers beyond its contracted seats (`seat_count - contracted_seats`, 0 without an active agreement). Under the managed renewal rule that is the net staff taken on since the last renewal, because contracted_seats = seat_count at the expiring term end.
  - A negative difference falls to "none" in both rule and compute.
  - No month-end question remains. Cross-difficulty status is kept (managed).
  - CLOSED.
- **F3 (B14)** — P4 backup_bundle_rate.
  - The count is filtered to `backup_plan_id = cont_plan` (the active plan), and the rule says other plans' protections, open or closed, are not counted.
  - Probe (scratch, task-1 world plus a closed older plan listed first with 12 m365 protections): P4 = 3.55, tier unchanged.
  - CLOSED.
- **F4 (XF 26b)**:
  - (a) "shows that Stratton Bay's pre-renewal license review missed licenses" is replaced by "A reduction made in a renewal window carries Stratton Bay's pre-renewal review goodwill on the reduction credit", a condition fully decided by records.
  - (b) ", which watches the same tenant" is removed from P4.
  - CLOSED.

### Were F1-F4 members of classes this audit should have caught? Yes, all four.
- **F1:** B8/B13 (rule == compute in every case, absent and edge values). I checked the instalment ladder textually but never probed a negative balance, although the managed charter allows a credit balance.
- **F2:** B12 (month-end convention of whole-month windows). I applied B12 to the P2/P3 late-fee windows and the round-2 P6 month count, but not to the onboarding window, whose dates fall on any day.
- **F3:** B14 (decoy probing of cross-holding reads). I probed only the TimeBank first-match. I treated Continuum as a single-holding category without probing a closed prior plan, while XCOUNT spans every plan of the client.
- **F4:** XF 26b (rule words about facts no record holds).
  - (a) I first raised this as observation O5 in revision_1 and wrongly accepted it as explanatory once 26b applied (revision_3).
  - (b) I missed it.

### Remaining members of those classes, swept on the whole r4 charter
- **B8/B13 (ladder domain coverage and edge values):** every comparison in every factor binding was checked against values the owning records allow (negative, zero, absent).
  - P1 change_fee / delay / review / prorated (charge > 0 and qty > 0 stated): covered.
  - P2 courtesy (== 0 with renewed >= 2 / < 2 complementary), minimum, share, escalation, relief (payments >= 25 percent / > 0 / else), size: covered. A non-positive past-due balance only arises where the invoice is not past due, which the eligibility excludes.
  - P3 instalments (fixed), down payment, month-late (late fees are positive), front-loading: covered.
  - P4 coverage, term, volume, upkeep, month part, bundle: covered.
  - P5 days (tail <= 7), TimeBank hours (ledger sums are >= 0, "none" = 0), volume, onboarding (negative -> none): covered.
  - P6 refund (lag, add charge > 0), admin return, reversal, deprovisioning, seat changes: covered.
  - **No further member.**
- **B12 (month windows):** the only remaining `within_months` reads are P2 prior_late_12m and cp_late_12m, and P3 month_late and late_24m. All count late fees, which both charters post only on the first day of a month. MONTHS(YYYY-MM-01, any day) never takes the day2 < day1 decrement, so the whole-months convention cannot meet a month-end. No MONTHS() call remains elsewhere. **No further member.**
- **B14 (cross-holding aggregates against what the rule names):**
  - P2 cp_late_12m XCOUNT spans all ClearPath agreements, and its rule speaks client-level ("a client whose ClearPath account also ran late ... the ClearPath billing ledger"). Rule and compute agree, so not a member (observation O15: a re-signed client's closed agreement's late fees count).
  - P5 tb_hours XSUM spans all blocks, and the rule says "across all its blocks". Not a member.
  - P4 m365 (fixed).
  - Status-filtered CPARAM/CFIELD reads on managed / security / backup assume one active holding per category, as the blueprint describes.
  - **No further member.**
- **XF 26b (unrecorded facts):** phrase sweep over every rule sentence ("which ...", "shows", "watch", "already", "still in", "taken on", "for the account manager", "given up", ...). Every remaining clause is either defined by a record test in the same sentence or purely descriptive of a test that follows. Examples:
  - P5 "staff ... taken on since its last renewal" is defined as the seats beyond contracted seats.
  - P5 "still in its first cancellation window" is the stated renewal_count 0 plus <= 6-day test.
  - P4 "Plans on which Stratton Bay maintains its ... baseline" is security_baseline_policies.
  - P3 "for the account manager to settle" describes the T1 treatment, not a condition.
  - **No further member.**

### Re-derived charter sections (r4)
- Mechanical sweeps: 0 compute_basis quote misses; 0 baseline-sentence misses; 4/4 prerequisite sentences verbatim; every superseded_clause verbatim in its base rule; every binding has a basis; 0 factor-reads-factor (transitive); 0 plain-reads-factor; no factor id in a tool name. Base copy verbatim.
- Factor counts unchanged: P1 4 (3p/1m), P2 6 (5p/1m), P3 4 (3p/1m), P4 6 (5p/1m), P5 4 (3p/1m), P6 5 (3p/2m). Multi-source and cross-difficulty per tree unchanged (P5 onboarding still reads managed).
- XF 1-26: as revision_3 plus the four closures above. XF 23 all-pairs table unchanged (no method factor changed). XF 24 unchanged (tools unchanged). XF 25: both worlds unchanged from r3 and still complete.
- Graph, prerequisite sentences, override declarations and scopes: unchanged.

### findings (r4)
- No open charter finding.
- Observation O15 (P2 escalation counts all of the client's ClearPath agreements, consistent with its rule). Earlier observations O3, O4, O13, O14 unchanged.

## closing_checklist (revision_4)
Written after the round-4 reveal (2026-10-18T10:25:48Z onward). The r4 charter-global sections above were unchanged after the reveal.
- Renderer findings F1-F4 (render_r1.md): all CLOSED (verified with probes, § revision_4).
- All four were members of classes this audit should have caught (B8/B13, B12, B14, XF 26b). Sweeping each class over the whole r4 charter found no other member.
- Regressions: none. All six scored values and every factor / baseline figure are identical to revision_3. Trees, edges, scopes, the tool module (hash unchanged) and both task worlds (view hashes unchanged) are also unchanged.
- Step-4 list holds as in revision_3:
  - one-to-one files with every revision kept;
  - disjoint and complete scopes;
  - trees of 2 prerequisites, 2 value_input edges, one user write, acyclic;
  - 4-6 honest, weight-bearing factors per computation, with whole baselines different from gold;
  - coordinator snapshot r4 all green.
- Outcome: the difficulty PASSES the source-layer audit at revision_4.

VERDICT revision_4: task0=PASS task1=PASS charter=CLEAN

## revision_5

## charter_global_frozen (revision_5)
- Gate: the last line of worklog.md is exactly `REWORK round 5: gates 7/7 green` (`tail -1`).
- Executed (not read) `/tmp/erl0069_coord/snapshot.sh microsoft_365_subscriptions 5` @ 2026-10-18T11:28:36:
  - check_extended, check_task_tools, replay_tasks, check_solvability, check_compute, check_grounding, check_cross_fire: all rc=0.
  - r5/0.view.json 58ed8adf1d02529adcbe7bf1e9cea7f90817f6cf02e3287da75c6c10858782b3 and r5/1.view.json 315b69c6c0fc2247dde18f87eee15890e3ccf6624a34705a69e6f6ace3a34f6e (both unchanged since r3).
  - licensing.extended.yaml f991ee1d87fb7d5e1f7b746c675b6d6ac69e1f9b63fd2089b84e285f4ab38028 (changed); task_tools.py faef8af4...e31591 (unchanged).
- RED input read in full: audits/render_source/microsoft_365_subscriptions/render_r2.md (R2-1..R2-3, raised after my revision_4 PASS). The round-5 claims were read after it. tasks/*.json were not read before the task freezes.
- Mechanical sweeps on r5 are all clean: quotes, baseline sentences, prerequisite sentences, superseded clauses, basis coverage, factor->factor and plain->factor reads, factor ids in tool names. Counts unchanged (P1 4, P2 6, P3 4, P4 6, P5 4, P6 5).

### R2-1..R2-3, verified on the artifacts
- **R2-1** — P6 baseline.
  - The sentence naming the order reversal fee and the seat change charges is replaced by a generic scope sentence: "Stratton Bay makes no license-work charge against the cancellation refund of a client holding a ClearPath agreement ... that work being covered".
  - It names no factor quantity. The kind-level wording, like the generic combination sentences, is acceptable.
  - CLOSED.
- **R2-2** — P3 front_loading.
  - The sentence now reads "not counting those posted less than one whole month before the arrangement", which is exactly compute's within_months=1 subtraction. It no longer relies on month_late_treatment's definition.
  - Probe (scratch, arrangement on 2026-10-15 with the only late charge posted on 2026-10-01): late_24m = 0, one share, matching the rule.
  - CLOSED.
- **R2-3** — P6 backup_deprovisioning.
  - Gated on the active plan's own Microsoft 365 protections (cx_m365 >= 1, keyed on the plan id), and defined in its own sentence.
  - Probe (scratch, servers-only plan): no charge, P6 = 1914.41.
  - The servers-only case is CLOSED. The class residue is R5-4 below.

### Sweep of the four named classes on the whole r5 charter
**(1) Baseline paragraphs naming factor quantities.**
- P1 names "the standard license change fee of 25.00 USD": the standard value of change_fee, which the standard method uses.
- P5 names "the standard provisioning fee of 6.00 USD" and its covered-work exemption: a standard-method amount.
- P6 names "Stratton Bay's administration fee is left as billed" (the standard default of admin_fee_return) and the generic license-work scope sentence.
- P2, P3 and P4 name only standard-method quantities.
- **No member.**

**(2) Factor sentences relying on another factor's definition.** Each factor's sentence was read for every term it uses.
- Terms come from its own sentence, its baseline, or a shared plain sentence (A2): P1 "renewal window", P3 "arrangement balance".
- P6 deprovisioning defines its Microsoft 365 count itself rather than borrowing P4's.
- **No member.**

**(3) Framing clauses asserting untested facts.** Three members.
- **R5-1 (P5 onboarded_staff_discount).** "Licenses added for staff the client's ClearPath agreement has taken on since its last renewal take an onboarding discount": the framing asserts the added licenses are for those staff. No record links a license addition to a user. Compute only compares seat_count - contracted_seats with the licenses added. This is the same shape as round-4 F4(a).
- **R5-2 (P5 order_window_convention).** "Licenses added while the order is still in its first cancellation window are billed as part of the order:" asserts the treatment for every in-window addition. The window is 168 hours (base), but the test is "no more than six calendar days after the date the cancellation window opened".
  - Reachable counter-case: purchase 2026-09-28 14:05, seat addition 2026-10-05 09:00. That is 162.9 h, still in the first window, but lag 7. The test gives the standard method; the framing says billed as part of the order.
  - The rule contradicts itself on that input.
- **R5-4 (P6 backup_deprovisioning).** "Removing the cancelled users from the client's Continuum Microsoft 365 backup deducts a deprovisioning charge per license cancelled ... where the active Continuum plan protects at least one Microsoft 365 user": the framing asserts the cancelled users are on the backup. Compute tests only >= 1 protected user and charges every license cancelled.
  - In task 1, 30 licenses are cancelled while the plan protects 22 Microsoft 365 users, so 8 of the 30 charged licenses have no user on backup to remove.
  - This is the R2-3 defect in partial form: a charge for removal work the records show cannot occur. Consequence in 1.md.
- Swept and clean: every other factor lead-in (P1 "posted late", "follows what the reduction releases"; P2 "ran late", "paid part of the invoice", "large annual invoices"; P3 "earlier late-charge record", "larger past-due invoices"; P4 "maintains its ... baseline", "already protects", "larger subscriptions"; P6 "how promptly the subscription is given up", "every seat addition ... reversed ... as a separate Partner Center change", which is a process statement with no record-testable premise).

**(4) replaced_by tails dropping in-force content (XF C16).** **R5-3**, five members:
- **P1** drops "where refund_on_window_reduction is true" for out-of-scope reductions ("a reduction on any other subscription is still refunded ..."). That base switch condition is no longer stated anywhere.
- **P6** drops the same switch condition for out-of-scope cancellations.
- **P2** tail "every other invoice is still assessed one late fee of late_fee_pct_monthly percent ..." drops the base timing and eligibility ("On the first day of each calendar month", "still unpaid more than late_fee_grace_days calendar days after its due date"). With the base sentence marked superseded, the out-of-scope late fee has no stated assessment day or grace condition.
- **P4** (second overwrite) drops "Where admin_fee_waived_with_clearpath_admin is true". The coverage share applies unconditionally, and the base's "no fee is posted" becomes "no fee is charged" (a 0.00 posting is not excluded, while the tool requires a positive amount).
- **P5** drops, for in-scope seat additions, "later cycles include the added licenses in the cycle charge". The tail restates it only for "any other subscription".
- Both switches are true on every current plan, so no figure moves today. The members still leave base content unstated, or retired without declaration, and the KB would render the base clause dead.
- Neither task's scored value moves.

### Self-assessment
- R2-1 belongs to A3/A5 and R2-2 to B12/A5. I swept both classes in rounds 2-4 and missed these members: R2-1 sat in a baseline paragraph I accepted as scope; R2-2's window wording I accepted as "the past month".
- R2-3 belongs to the 26b / framing class I swept in round 4. I accepted the deprovisioning lead-in as descriptive.
- R5-3 is C16, which I declared clean from revision_2 on. I checked only scope naming and sibling exclusion, not that the tail restates every in-force element.

### findings (r5)
Charter RED: R5-1, R5-2, R5-3 (5 members), R5-4. Observations O3, O4, O13, O14, O15 unchanged.

## closing_checklist (revision_5)
Written after the round-5 reveal (2026-10-18T11:31:30Z onward). The r5 charter-global sections above were unchanged after the reveal.
- R2-1: CLOSED. R2-2: CLOSED. R2-3: closed for the zero-user case, with the residue recorded as R5-4.
- Regressions: none. All six scored values and every factor / baseline figure are identical to revision_4. Trees, scopes, tools and views are unchanged.
- Open:
  - **R5-1** (P5 onboarding framing).
  - **R5-2** (P5 order-window framing vs the 6-day test).
  - **R5-3** (C16 tails dropping in-force content: P1, P2, P4, P5, P6).
  - **R5-4** (P6 deprovisioning charged per license although the framing premises a removal per cancelled user on backup; bears on task 1's scored refund).
- Outcome: the difficulty does NOT pass at revision_5.

VERDICT revision_5: task0=PASS task1=RED:R5-4 charter=R5-1,R5-2,R5-3,R5-4

## revision_6

## charter_global_frozen (revision_6)
- Gate: the last line of worklog.md is exactly `REWORK round 6: gates 7/7 green` (`tail -1`).
- Executed (not read) `/tmp/erl0069_coord/snapshot.sh microsoft_365_subscriptions 6` @ 2026-10-18T11:52:41:
  - check_extended, check_task_tools, replay_tasks, check_solvability, check_compute, check_grounding, check_cross_fire: all rc=0.
  - r6/0.view.json 58ed8adf1d02529adcbe7bf1e9cea7f90817f6cf02e3287da75c6c10858782b3 and r6/1.view.json 315b69c6c0fc2247dde18f87eee15890e3ccf6624a34705a69e6f6ace3a34f6e (unchanged).
  - licensing.extended.yaml 0ab2f241f7915cbd96cd5f1ac9aad76e657b46660d448a7e97900c3f88ada2a4 (changed); task_tools.py faef8af4...e31591 (unchanged).
- Task 1 was re-derived first and frozen (1.md § revision_6), then task 0, then the claims and the GT were read.
- Mechanical sweeps all clean on r6: quotes, baseline sentences, 4/4 prerequisite sentences, every superseded_clause in its base rule, every replaced_by verbatim in its rule, basis coverage, factor->factor and plain->factor reads, factor ids in tool names. Counts unchanged (P1 4, P2 6, P3 4, P4 6, P5 4, P6 5).

### Round-5 REDs, verified on the artifacts
- **R5-1** — CLOSED. P5 onboarding sentence: "The partial-cycle charge takes an onboarding discount set by the seats the active ClearPath agreement covers beyond its contracted seats". No unrecorded premise remains.
- **R5-2** — CLOSED. P5 order window: "A seat addition on a subscription that has never renewed, submitted no more than six calendar days after the date the cancellation window opened, is billed with the order". The framing now is the test, and the 162.9 h / lag-7 case is consistently the standard method.
- **R5-3** — CLOSED. Each tail now restates its retired clause's in-force content:
  - P1 and P6 carry "where refund_on_window_reduction is true" (in scope and in the tail).
  - P2's tail carries the first-of-month day and the grace condition.
  - P4 carries "Where admin_fee_waived_with_clearpath_admin is true ... every client where admin_fee_waived_with_clearpath_admin is false, is charged the whole fee" and "no fee is posted". Compute now tests the switch: `cover_pct = 100 if P('admin_fee_waived_with_clearpath_admin') != True else ...`. A 0 result means no write, consistent with the tool's positive amount.
  - P5 carries "for the rest of the billing cycle in which it is submitted" and "later cycles include the added licenses in the cycle charge" for in-scope additions too.
- **R5-4** — CLOSED. Per-user deprovisioning count `MN(lic_held, cx_m365)`, stated in the rule. Task 1's gold moved 1884.41 -> 1892.41, matching my frozen re-derivation (1.md).

### Checks on the changes (r6)
- The deprovisioning ladder still has three tiers with distinct values (0.50 / 1.00 / 0 per user). `deprov_users` is that factor's own binding, read only by result. The "lesser of" count is a record test (plan id keyed). Baseline '0' still bears weight (1914.41 vs 1892.41).
- The four classes swept in revision_5 (baseline naming factors, borrowed definitions, untested framing, C16 tails) were re-swept on the changed sentences. No new member.
- XF 23 (no method factor changed), XF 24 (tools unchanged) and XF 25 (views unchanged): unchanged.
- **Observation O16:** coverage_share's tier conditions now conjoin `admin_fee_waived_with_clearpath_admin true`, and P1 / P6 scope on `refund_on_window_reduction true`. Both switches are true on every current plan, so the conjunct holds of every customer reaching the write. It is retained because the base clause it restates is in force (C16), not to divide customers. The tiers still divide on ClearPath coverage, so the factor stays real. Recorded as an observation, not a ladder defect.

### findings (r6)
- No open charter finding. Observations O3, O4, O13, O14, O15 and O16.

## closing_checklist (revision_6)
- R5-1, R5-2, R5-3 and R5-4 are all CLOSED.
- Regressions: none. Task 0 values and figures are identical to revision_5. Task 1 moved only where R5-4 requires (P6 1884.41 -> 1892.41, with its sensitivities and load-bearing figures), and every moved figure matches my frozen re-derivation. Trees, scopes, tools and views are unchanged.
- Step-4 list holds:
  - one-to-one files with every revision kept;
  - disjoint and complete scopes;
  - trees of 2 prerequisites, 2 value_input edges, one user write, acyclic;
  - 4-6 honest, weight-bearing factors per computation, with whole baselines different from gold (780.56 / 41.55 / 930.47; 67.50 / 269.28 / 1773.90);
  - coordinator snapshot r6 all green.
- Outcome: the difficulty PASSES the source-layer audit at revision_6.

VERDICT revision_6: task0=PASS task1=PASS charter=CLEAN

## revision_7

## charter_global_frozen (revision_7)
- Gate: the last line of worklog.md is exactly `REWORK round 7: gates 7/7 green` (`tail -1`).
- Executed (not read) `/tmp/erl0069_coord/snapshot.sh microsoft_365_subscriptions 7` @ 2026-10-18T13:32:27:
  - check_extended, check_task_tools, replay_tasks, check_solvability, check_compute, check_grounding, check_cross_fire: all rc=0.
  - r7/0.view.json 14f1e6c889521b30ab7cabfd0b29dd50bf1996e49f03b4b7668c006c72e2850e and r7/1.view.json 0e6b71b43da0ba25ea665736cfa465ebae4d1f444883473f66e44100015ad6cc (both changed: managed rows only).
  - licensing.extended.yaml cceb917a331518a71bf328e3ce4b459f5c989f1ba1a73c8cf03e65ba3b629be7 (changed); task_tools.py faef8af4...e31591 (unchanged).
- Read: the KB audit's source items (audits/policy_kb/microsoft_365_subscriptions/_difficulty.md § Source-side items), then the round-7 claims, then the published docs/managed/ hubs, baselines and factors for managed_ext_first_late_fee, managed_ext_current_month_fee and managed_ext_auto_renewal_rate. These were read as the owning charter of the cross-product rows.
- Mechanical sweeps on r7 all clean: quotes, baseline sentences, 4/4 prerequisite sentences verbatim, superseded clauses, replaced_by verbatim, basis coverage, factor->factor and plain->factor reads, factor ids in tool names. Counts unchanged.

### KB source items, verified on the artifacts
- **reduction_credit_no_floor** — CLOSED.
  - P1's combination sentence now ends "and never falls below 0.00: where the license change fee leaves nothing, no reduction credit is posted". Compute is `RND(MX(..., 0), 2)`.
  - On the KB's Business Basic P1M case: prorated 5.76 less 25.00 or 10.00 floors at 0.00, so no write; a covered client gets 5.76.
- **every_x_prerequisite_vs_latest_x_rule** — CLOSED as to scope.
  - Each edge now waits on exactly the record its depended-on rule prices: P2 on the latest in-window reduction; P6 on the latest seat addition and on the fee for the month just ended. P5 now states that a 0.00 charge is not posted.
  - The fix brings a new defect: **R7-3** below.
- **xprod_seed_managed_late_fees_t0** — the two late fees now follow the published late-fee schedule exactly, given 2604.00 invoices (0.md). The 2604.00 invoices themselves rest on a seat rate the published renewal schedule does not give on the seeded records: **R7-1**.
- **xprod_seed_managed_monthly_fees_t1** — the two fees now follow the published monthly-fee schedule exactly, given 38.50 (1.md). The 38.50 rate itself contradicts the published renewal schedule on the seeded ticket ledger: **R7-2**.
- **gold_find_customers_legal_name** — CLOSED. Both golds locate the client by a detail the caller states (phone in task 0, email in task 1).
- **cancellation_baseline_license_work_hint** — not routed by the coordinator. I accepted that sentence as generic scope in revision_5 (no factor quantity named). Observation, unchanged.

### findings (r7)
**R7-3 — SOURCE-POLICY RED (check 6 state form; XF A5 "as another policy figures it"). Three prerequisite sentences now wait on a computed amount of the depended-on policy rather than on a record-visible state.**
- P2: "The late charge on a cycle invoice is fixed only after the subscription's latest in-window reduction carries its reduction credit on the billing ledger, unless that credit comes to 0.00 and so is not posted." Condition: "... or the reduction credit schedule prices it at 0.00".
- P6 (a): "... the administration fee owed on the first day of the current month for the month just ended stands on its billing ledger, where the subscription was active or suspended at that month's end and the fee comes to more than 0.00." Condition: "... and its administration fee schedule prices that month above 0.00".
- P6 (b): "... the subscription's latest seat addition carries its partial-cycle charge on the billing ledger, unless that charge comes to 0.00 and so is not posted." Condition: "... or the partial-cycle charge schedule prices it at 0.00".
- Consequence, demonstrated on the KB's own case:
  - A Business Basic P1M client without ClearPath reduces 1 license with 24 of 30 days left. P1 floors the credit to 0.00 and posts nothing.
  - Whether the late charge may then be fixed is decided by no record. The ledger shows an in-window reduction with no credit, exactly as for a credit still owed.
  - The reader can resolve the wait only by working out P1's amount. The same holds for P6 with a 0.00 seat charge (a covered client's tail-day addition) or a 0.00 admin fee (a covered client).
  - The state form's record-visible wait, and recipe A5's ban on defining a condition "as another policy figures it", are both broken.
- Neither task world reaches a 0.00 case (880.25, 3.55 and 257.66 are all > 0), so no scored value moves. The sentences are part of the KB both tasks render. Bears on both trees, charter-level.

R7-1 (task 0) and R7-2 (task 1): cross-product seed findings, in 0.md / 1.md § revision_7.
- Class sweep (cross-product ClearPath rows against the published managed rules): every other seeded ClearPath row was recomputed.
  - Task 0: monthly fees 2026-05..10 (124.00 from the 2026 renewal, reproducible only with no tickets).
  - Task 1: prorations (base proration rule; their rate inherits R7-2), contracted_seats (renewal rule, consistent), the agreement balance.
  - Each rests on R7-1 or R7-2; no independent further member.
- The published security, backup and timebank documents carry no extended rule beyond their base charters, already checked in revision_3.

Observations O3, O4, O13, O14, O15, O16 unchanged; O17: the KB src item cancellation_baseline_license_work_hint, unrouted.

## closing_checklist (revision_7)
Written after the reveal (2026-10-18T13:38:16Z). The r7 charter section above was written before it.
- KB src items: reduction_credit_no_floor CLOSED; every_x scope CLOSED (new R7-3); xprod late fees t0 and monthly fees t1 re-priced correctly given their inputs (residues R7-1 and R7-2); gold_find_customers CLOSED.
- Regressions: none. All six scored values and every factor / baseline / load-bearing figure are identical to revision_6. Trees and scopes are unchanged.
- Open: R7-1 (task 0 seed), R7-2 (task 1 seed), R7-3 (charter, prerequisite sentences).
- Outcome: the difficulty does NOT pass at revision_7.

VERDICT revision_7: task0=RED:R7-1 task1=RED:R7-2 charter=R7-3

## revision_8

## charter_global_frozen (revision_8)
- Gate: the last line of worklog.md is exactly `REWORK round 8: gates 7/7 green` (`tail -1`; checked before the re-sent brief arrived, nothing written then).
- Executed (not read) `/tmp/erl0069_coord/snapshot.sh microsoft_365_subscriptions 8` @ 2026-10-18T16:09:15:
  - check_extended, check_task_tools, replay_tasks, check_solvability, check_compute, check_grounding, check_cross_fire: all rc=0.
  - r8/0.view.json cf5cc1365af02df287c8206d01d41b629e452ec3da253a7d3f7088442a0bfa84 and r8/1.view.json 26ad1dc0d6483f169db18e07fa90b94433a9487a1a87442a5938924a3fc3285c (ClearPath rows changed).
  - licensing.extended.yaml 28f52e477692dc28665dc88e5dc1e7d12a0ab0e3e5fe4c39becc91539503669c (changed); task_tools.py 280e4a5d6511d40d6c8a33e140280583bf08b745b1e865a01bc845878939e48f (changed: three amount docstrings).
- Read: the round-8 claims; the published docs/managed/ policies and facets used by every ClearPath row (current-month fee, first late fee, automatic renewal rate, seat changes and proration, payment application, ticket priority and scope, labor settlement, first-response credits, service levels, coverage hours).
- Mechanical sweeps on r8 all clean: quotes, baseline sentences, 4/4 prerequisite sentences verbatim, superseded clauses, replaced_by verbatim, basis coverage, factor->factor and plain->factor reads, factor ids in tool names. Counts unchanged; tool names and uuid8s unchanged.

### Round-7 REDs
- **R7-1 / R7-2** — CLOSED on the seeded ledgers. Every ClearPath row of both tasks reproduces under the published rules (exhaustive per-row check in 0.md / 1.md § revision_8). The residue is R8-2 below.
- **R7-3** — CLOSED. Every prerequisite sentence now waits only on a record-visible line:
  - P2: "the subscription's latest in-window reduction carries its reduction credit line on the billing ledger";
  - P3: unchanged, a late-fee row;
  - P6: "the administration fee line for the month just ended stands on its billing ledger, where the subscription was active or suspended at that month's end" (status and dates are on the record) and "the subscription's latest seat addition carries its partial-cycle charge line".
  - None requires computing another policy's amount. Each has one writer. The depended-on rules post the line even at 0.00, and the P4 waiver change is declared in its overwrite.

### findings (r8)
**R8-1 — SOURCE-POLICY RED (the extended charter and tools contradict the frozen constitution). The R7-3 fix posts 0.00 billing lines, which the scenario's db_schema rules out.**
- Evidence:
  - blueprint/db_schema.json `licensing_billing.amount_usd`: `{'type': 'fixed_format', 'format': 'USD, 2 decimal places, positive', 'meaning': 'absolute amount; direction fixed by event_type'}`.
  - P1 rule: "the reduction is given a reduction credit line of 0.00, no credit being due".
  - P4 (overwrite and rule): "no fee is charged and the month carries an administration fee line of 0.00".
  - P5 rule: "a partial-cycle charge that comes to 0.00 is posted as a partial-cycle charge line of 0.00".
  - Tool docstrings of post_reduction_credit_23f8ed2c, post_admin_fee_5104ae31 and post_seat_addition_charge_bba679a2: "a number of 0.00 or more ... (0.00 records a ... line with no ... due)".
- Demonstrated consequence (same situation, two conclusions):
  - Take a covered client's subscription on the 1st of a month. P4 and its tool post a licensing_admin_fee row of amount 0.00 (on a new invoice). The constitution says no licensing_billing row can carry a non-positive amount.
  - The same holds for a floored reduction credit (the KB's Business Basic P1M case) and for a covered client's tail-day seat addition.
  - The R7-3 waits in those worlds are satisfiable only by writing rows the frozen schema forbids. Either the prerequisite is unreachable under the schema, or the terminal ledger violates it.
- The audit criteria treat the constitution as fixed input. An extended artifact contradicting it is a policy-surface conflict, not a style point. The scenario-level 0.00 line is also realistic only as an audit-trail convention: P4 issues a new 0.00 invoice every month for every covered client's subscription.
- Neither task world posts a 0.00 line (880.25, 3.55 and 257.66 are all > 0), so no scored value moves. Charter-level; bears on both trees.

**R8-2 — SOURCE-FACTOR RED (XF 25 complete ledgers: look-back coverage). Exhaustive class listing over both tasks' ClearPath rows.** The per-ledger "seeded window" I adopted in revision_3 does not cover the look-backs of the published rules priced into the seeded rows. Members:
- (a) task 0, 2025-09-01 late fee: the payment count over 2024-09..2025-08 (billing seeded from 2025-07). Implied history gives 16.16, not 20.20.
- (b) task 0, the 2025-04-08 renewal rate: late fees, credits and tickets over 2024-04..2025-04 (none seeded).
- (c) task 0, the 2026-04-08 renewal rate: late fees over 2025-04..2025-06 (not seeded).
- (d) task 1, the 2026-03-01 renewal rate: late fees and credits over 2025-03..2026-02 (billing seeded from 2026-09).
- Every other ClearPath row of both tasks is either priced from in-window records or from current state, and reproduces exactly. That covers:
  - the monthly-fee credits (current holdings) and prorations (rate x days);
  - the 2026-04-01 late fee (its rate tier rests on the seeded 2025-09-01 fee; its courtesy window is seeded);
  - payments, balances, seat ledgers, ticket scopes, SLA and labor routes.
- No licensing figure depends on any member: the licensing escalation window 2025-10-01..2026-09-30 is fully seeded in task 0, and task 1's licensing factors read only tier, status and seat counts.
- Self-assessment: I should have caught this class in revision_3 (XF 25) and revision_7 (XF 20); I read the seeded window per ledger without checking each priced row's look-back.

Observations O3, O4, O13-O17 unchanged; the 0.00-line realism note is folded into R8-1.

## closing_checklist (revision_8)
Written after the reveal (2026-10-18T16:12:48Z). The r8 charter section above was written from the charter, tools, schema and docs before it.
- R7-1 and R7-2: closed on the seeded ledgers (residue R8-2). R7-3: CLOSED.
- Regressions: none. All six scored values and every factor / baseline / load-bearing figure are identical to revision_7. Trees and scopes are unchanged.
- Open: R8-1 (charter), R8-2 a / b / c (task 0), R8-2 d (task 1).
- Outcome: the difficulty does NOT pass at revision_8.

VERDICT revision_8: task0=RED:R8-2a,R8-2b,R8-2c task1=RED:R8-2d charter=R8-1

## revision_9

## charter_global_frozen (revision_9)
- Gate: the last line of worklog.md is exactly `REWORK round 9: gates 7/7 green` (`tail -1`).
- Executed (not read) `/tmp/erl0069_coord/snapshot.sh microsoft_365_subscriptions 9` @ 2026-10-18T16:39:24:
  - check_extended, check_task_tools, replay_tasks, check_solvability, check_compute, check_grounding, check_cross_fire: all rc=0.
  - r9/0.view.json 110ac033857d023241646e8d7c2d3db52091c261bd5f2c97e98c1bd60765df23 and r9/1.view.json 7f0751648c20afc5558cc7e52672b5753d91b04c67f15a2760ee6d5335fc4c12.
  - licensing.extended.yaml c402fff59052cff2dc54c9560742c01a5a8641d495473bcfbed0825225225c86; task_tools.py faef8af49769237d072f5b4419c073782c13255b65131f41c54ca57027e31591 (back to the round-7 module: every amount "a positive number").
- Read: the round-9 claims; the published docs/managed/ rules (as round 8, plus signing and onboarding).
- Mechanical sweeps on r9 all clean (quotes, baseline sentences, 4/4 prerequisite sentences verbatim, superseded / replaced_by, basis coverage, A1, plain reads, factor ids in tool names). Counts unchanged.

### Round-8 REDs
- **R8-2 a / b / c / d** — CLOSED. Exhaustive per-row check in 0.md / 1.md § revision_9: every priced ClearPath row reproduces under the published rules, and each look-back lies inside seeded records. Both agreements now start (signing, onboarding fee, baseline proration) inside the seeded ledgers.
- **R8-1** — the three tool contracts are positive again, and the three cases R8-1 named are gone:
  - P1 caps the license change fee at half the prorated amount, so the credit is always > 0.
  - P5 says "a seat addition whose charge comes to nothing carries no partial-cycle charge line".
  - P4 "no fee is posted" on the waiver.
  - The P6 waits carve those zero cases out by pure record tests: plan switch plus covered tier for the admin fee; covered tier plus a tail-day, non-order addition for the seat charge.
  - Edge probes (scratch, reasoning on the rule texts):
    - covered + waiver: P4 posts nothing and the P6 admin wait is lifted;
    - covered + tail-day addition: P5 posts nothing and the P6 seat wait is lifted;
    - any other case: the depended-on write posts a positive line and the wait is met only by that line.
  - **All four waits are pure record tests** (line presence, statuses, tier parameters, plan switch, dates).
  - **But two zero / negative cases outside those three remain: R9-2.**

### findings (r9)
**R9-1 — SOURCE-POLICY RED (XF A3 and baseline coherence). P1's new fee cap lives in the combination sentence and is missing from the standard method.**
- Evidence:
  - Rule: "... and fixed amounts are added or subtracted last, the license change fee never taking more than half the prorated amount, so every reduction carries a reduction credit above 0.00". Compute: `RND(... - MN(change_fee, prorated * K('fee_cap_share')), 2)`.
  - baseline.rule (unchanged): "The standard reduction credit is the prorated amount ... less the standard license change fee of 25.00 USD, rounded half up to the cent".
- Consequences:
  - (a) The generic combination sentence names a factor quantity (the license change fee), which is the A3 class.
  - (b) The baseline no longer states the standard method. Probe (scratch, Business Basic P1M, 1 license, 24 of 30 days, no ClearPath): baseline.rule gives 5.76 - 25.00 = **-19.24**. Compute with every factor at its baseline gives **2.88** (fee capped at 2.88). A fall-back reader computes a number the charter's own standard method does not produce.
- No effect in task 0 (fee 0.00).

**R9-2 — SOURCE-POLICY RED (R8-1 class residue: amounts the positive-only tool contracts cannot carry). Two reachable zero / negative cases have no rule.**
- **P4 administration fee for a long-suspended subscription.**
  - The rule invoices the fee "on every subscription whose status was active or suspended at the end of that month", and month part T2 is "30 less the calendar days from its suspended_date up to the posting day (never less than nothing), over 30".
  - A subscription suspended 30 or more days before the posting day (reachable: suspension comes at 45 days past due and lasts until cure) prices at 0.00. No sentence says such a fee is not posted, and post_admin_fee_5104ae31 takes only "a positive number" (schema: positive).
  - The P6 wait excludes suspended subscriptions, so no wait breaks. P4's own write in that world is undefined.
- **P6 cancellation refund with no floor.**
  - The rule subtracts the order reversal fee, the seat change charges and the deprovisioning charge from the license refund, with no floor. cancel_subscription_in_window_d46a60fb takes "a positive number".
  - Example, all reachable: Business Basic P1M, 10 licenses, renewed, 10 seat additions recorded over its life, cancelled 5 days after the renewal window opened (standard day count 26/30), no ClearPath, Continuum Backup Basic protecting 10 users.
  - License refund 7.20 x 10 x 26/30 = 62.40, less reversal 25.00, less seat changes 10 x 4.00, less deprovisioning 10 x 1.00 = **-12.60**.
  - The rule yields a negative refund the tool cannot record, and the charter says neither "no refund" nor "a charge".
- Neither task world reaches these cases (3.55 and 1892.41).

Observations O3, O4, O13-O17 unchanged.

## closing_checklist (revision_9)
Written after the reveal (2026-10-18T16:44:08Z).
- R8-2 a / b / c / d: CLOSED.
- R8-1: closed for the three named cases, with residue R9-2. Its fix introduced R9-1.
- Regressions: none. All six scored values and every factor / baseline / load-bearing figure are identical to revision_8. Trees, scopes and tool names / uuid8s are unchanged.
- Open: R9-1, R9-2 (charter-level; no scored effect in either task).
- Outcome: the difficulty does NOT pass at revision_9.

VERDICT revision_9: task0=PASS task1=PASS charter=R9-1,R9-2

## revision_10

## charter_global_frozen (revision_10)
- Gate: the last line of worklog.md is exactly `REWORK round 10: gates 7/7 green` (`tail -1`).
- Executed (not read) `/tmp/erl0069_coord/snapshot.sh microsoft_365_subscriptions 10` @ 2026-10-18T17:24:41:
  - check_extended, check_task_tools, replay_tasks, check_solvability, check_compute, check_grounding, check_cross_fire: all rc=0.
  - r10/0.view.json 110ac033857d023241646e8d7c2d3db52091c261bd5f2c97e98c1bd60765df23 and r10/1.view.json 7f0751648c20afc5558cc7e52672b5753d91b04c67f15a2760ee6d5335fc4c12 (both identical to r9).
  - licensing.extended.yaml 63b4176f029775d67d91e0b7c1d8f4969b5a2fdb66a925894b810bd1e547c9a2 (changed); task_tools.py faef8af4...e31591 (unchanged; all amounts positive).
- Read: the round-10 claims; docs/timebank/ (newly published) for the task-1 TimeBank rows.
- Mechanical sweeps: quotes, baseline sentences, 4/4 prerequisite sentences verbatim, superseded / replaced_by, basis coverage, A1 and factor ids in tool names are all clean. **Plain->factor reads: two hits (R10-1).** Counts unchanged.

### Round-9 REDs
- **R9-1** — CLOSED.
  - P1 baseline.rule now reads "less the standard license change fee of 25.00 USD, never more than half the prorated amount, so a reduction always carries a reduction credit above 0.00", with `fee_cap_share` in baseline.params.
  - The fee factor's sentence says "whichever fee applies is netted, as under the standard method, never more than half the prorated amount". The combination sentence is generic again.
  - Probe (Business Basic P1M, 1 license, 24 of 30 days, no ClearPath): baseline.rule gives 5.76 - 2.88 = 2.88, equal to compute at baseline.
- **R9-2** — CLOSED.
  - P4: "one suspended 30 or more days before the posting day has no part of the month left to charge, so no fee is posted".
  - P6: "Charges deducted from a cancellation refund never take, together, more than half of the refund they are deducted from ..., so a cancellation always carries a refund above 0.00". Compute `RND(cx_gross - MN(cx_charges, cx_gross x 0.5), 2)`.
  - Probe (scratch: Business Basic P1M, 10 licenses, renewed, 10 seat additions, lag 5, Continuum Backup Basic protecting 10, no ClearPath): refund **30.00 > 0**, instead of a negative amount.
- **Zero / negative sweep, every computation:**
  - P1 >= prorated/2 > 0.
  - P2 > 0 (share > 0 past grace, minimum > 0, multipliers > 0). An invoice whose credits leave nothing unpaid is not "still unpaid", so it is never assessed.
  - P3 > 0, with the new record-tested case "a balance no greater than that late charge leaves nothing to arrange, so no arrangement is made".
  - P4: 0 only on the waiver or a 30+ day suspension, both "no fee is posted"; neither is in P6's wait (active at month end, waiver carve-out).
  - P5: 0 only on the covered tail-day case, "carries no partial-cycle charge line", carved out of P6's wait.
  - P6 > 0 by the cap (the license refund is > 0 because a cycle charge exists and at least the cancellation day remains).
  - **No remaining member.**
- The four prerequisite waits are unchanged pure record tests.

### Cross-product rows
- TimeBank (task 1) against the published docs/timebank/ rules: ordering / price, full-payment activation, validity / expiry, remote-session draws (band, level, increment, minimum), balance and low-balance point. All rows CLEAN (1.md § revision_10).
- ClearPath, Sentinel and Continuum rows: unchanged since r9 (views identical), verified then.

### findings (r10)
**R10-1 — SOURCE-POLICY RED (XF 26a: plain bindings read factor-owned bindings). P6's new charge cap is assembled in two plain bindings that read six factor bindings.**
- Compute:
  - `cx_gross` (plain) reads `refund_base` (prompt_cancel_anchor) and `admin_return` (admin_fee_return).
  - `cx_charges` (plain) reads `reversal_fee` (order_reversal_fee), `change_rate` and `seat_changes` (seat_change_reversals), `deprov_rate` and `deprov_users` (backup_deprovisioning).
  - Mechanical plain->factor sweep: 2 bindings, 7 reads. The other five policies have 0.
- This is the class revision_3 closed by folding P2 `monthly_charge`, P4 `rate` and P6 `licence_refund` into `result`. The R9-2 fix reintroduced it in P6.
- Consequence: the assembly is no longer carried by `result` alone. Two named intermediates combine several factors' outputs, so a document rendering `cx_gross` or `cx_charges` must name the quantities of five factors (the XF A3 / 26a renderer finding).
- No scored value moves (task 1: 1892.41).
- Observation: P6's charge-cap sentence sits in the baseline paragraph and speaks of "charges deducted from a cancellation refund" generically, while the standard method has no such charges. It is kind-level wording, as accepted for the license-work scope sentence in revision_5, so not RED.

Observations O3, O4, O13-O17 unchanged.

## closing_checklist (revision_10)
Written after the reveal (2026-10-18T17:26:36Z).
- R9-1: CLOSED. R9-2: CLOSED. Zero / negative sweep: no member. TimeBank rows: CLEAN.
- Regressions: none in values. All six scored values and every factor / baseline / load-bearing figure are identical to revision_9. One structural regression class reappeared in P6 (R10-1).
- Open: R10-1 (charter-level; no scored effect).
- Outcome: the difficulty does NOT pass at revision_10.

VERDICT revision_10: task0=PASS task1=PASS charter=R10-1

## revision_11

## charter_global_frozen (revision_11)
- Gate: the last line of worklog.md is exactly `REWORK round 11: gates 7/7 green` (`tail -1`).
- Executed (not read) `/tmp/erl0069_coord/snapshot.sh microsoft_365_subscriptions 11` @ 2026-10-18T17:56:14:
  - check_extended, check_task_tools, replay_tasks, check_solvability, check_compute, check_grounding, check_cross_fire: all rc=0.
  - r11/0.view.json 110ac033857d023241646e8d7c2d3db52091c261bd5f2c97e98c1bd60765df23 and r11/1.view.json 7f0751648c20afc5558cc7e52672b5753d91b04c67f15a2760ee6d5335fc4c12 (identical to r9/r10).
  - licensing.extended.yaml fb64a29060a24388f3b57fb52a9f93996efaa672e9034c2b49857e1bebd4aaa2 (changed); task_tools.py faef8af4...e31591 (unchanged).
- Mechanical sweeps on r11 all clean: quotes, baseline sentences, 4/4 prerequisite sentences verbatim, superseded / replaced_by verbatim, basis coverage (charge_cap quotes the cap sentence verbatim), A1 transitive, **plain->factor reads 0 on all six policies**, no factor id in a tool name. Counts unchanged (P1 4, P2 6, P3 4, P4 6, P5 4, P6 5).

### Round-10 RED
- **R10-1** — CLOSED.
  - `cx_gross` and `cx_charges` are gone. P6's `result` now assembles the license refund, amounts returned, charges and cap: `RND((MN(refund_base, billed_cycle) + admin_return) - MN((0 if covered_work else reversal_fee + change_rate x seat_changes) + deprov_rate x deprov_users, (MN(refund_base, billed_cycle) + admin_return) x charge_cap), 2)`.
  - The only new plain binding, `charge_cap = K('charge_cap_share')`, reads a parameter alone.
  - The cap sentence and the combination order are unchanged.
  - Zero / negative probe (the revision_10 scratch case) is still 30.00 > 0.

### Changes and regressions
- The change is limited to P6 compute (folding) plus the charge_cap basis entry. No rule sentence that the closure depends on moved.
- All six scored values and every factor / baseline / load-bearing figure are identical to revision_10 (880.25 / 21.66 / 819.68; 3.55 / 257.66 / 1892.41).
- Seeds are identical (view hashes unchanged), so the ClearPath, Sentinel, Continuum and TimeBank verifications of revisions 9-10 stand.
- Prerequisite waits are unchanged and record-only.
- The zero / negative sweep result stands.
- No new defect found.

Observations O3, O4, O13-O17 unchanged (not grounds for rework).

## closing_checklist (revision_11)
Written after the reveal (2026-10-18T17:56:54Z).
- R10-1 CLOSED; every earlier RED (revisions 1-10) remains closed.
- Step-4 list holds:
  - per-task files one-to-one with every revision kept; disjoint and complete scopes;
  - trees of 2 prerequisites, 2 value_input edges, one user write, acyclic, with record-only waits;
  - 4-6 honest, weight-bearing factors per computation, with whole baselines different from gold (780.56 / 41.55 / 930.47; 67.50 / 269.28 / 1773.90);
  - cross-product rows consistent with the published rules of their owning products;
  - coordinator snapshot r11 all green.
- Outcome: the difficulty PASSES the source-layer audit at revision_11.

VERDICT revision_11: task0=PASS task1=PASS charter=CLEAN
