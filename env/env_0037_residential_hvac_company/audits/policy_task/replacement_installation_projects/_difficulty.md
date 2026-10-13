# Policy-task audit — replacement_installation_projects / charter-global

## charter_global_frozen

- Auditor: independent erl-task-policy-audit agent (did not author any artifact of this difficulty).
- Freeze time: 2026-10-05T15:45Z (written before any task's GT was revealed; nothing in this section is derived from a revealed GT field).
- Frozen inputs (sha256, recomputed by the auditor and equal to the coordinator's `charter.sha256`):
  - `tasks/replacement_installation_projects/install.extended.yaml` f774f88810d5e9fee71c2cc882b11b6dd4c4ced87d7bae4f03ea65d47d0f9972
  - `tasks/replacement_installation_projects/task_tools.py` 2e979f06dfcd7e72d931b904a403c82adf8a7e298992167a665ab70d6c1b096b
  - masked views `task_0.masked.json` 4ffb5bd0…0c3e30f3c, `task_1.masked.json` 9bf93388…96c8b
- Permitted and read: `blueprint/blueprint.yaml`, `blueprint/db_schema.json`, `blueprint/share_tools.py`, `blueprint/products/install.yaml`, `blueprint/products/plan.yaml` (variant parameters and the plan_tuneup_visit / plan_visit_grant / plan_coverage_grant event definitions only), the extended charter, `task_tools.py`, the two masked views (frozen_time, user_scenario, initial_state).
- Masked and not read: every `tasks/*.json`; evaluation_criteria, computations, db_closure, charter_scope, required_documents, design_rationale, solvability_contract, prerequisite_closure; the scenario `worklog.md`; any other audits.
- Entry conditions (Step 0): gate snapshot supplied (`/tmp/erl37/gates/replacement_installation_projects.snapshot.txt`): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, CACHE-DIFF INFO, SCOPE OK; check_traceability deferred by the coordinator to the KB stage. Masked views and hashes supplied. Entry conditions complete.
- Base copy: the first 1185 lines of the extended charter are byte-identical to `blueprint/products/install.yaml` (`diff` empty).

### policy_conflict_scan

Five extended policies, each with a distinct subject/target:

| policy | subject | target_tool (owner) | computes |
| --- | --- | --- | --- |
| install_ext_line_set_change_order_charge | install_charge | bill_change_order_a6215d22 (agent) | amount |
| install_ext_progress_installment | install_payment | pay_progress_installment_728e8d1f (user) | amount |
| install_ext_member_install_credit | install_credit | post_member_install_credit_c2d484b0 (agent) | amount |
| install_ext_accessory_member_discount | install_credit | post_accessory_member_discount_3312a288 (agent) | amount |
| install_ext_contract_deposit | install_payment | pay_contract_deposit_7afff78b (user) | amount |

- Overlapping subjects: the two install_credit policies post different line_types (member_install_credit naming the contract-price charge vs accessory_member_discount naming an accessory charge) and never fight over one quantity; the two install_payment policies post different line_types (progress_payment vs deposit) and have disjoint triggers (a scheduled project ahead of installation vs a project not financed in full, at or after signing). No two policies decide the same scored quantity.
- Triggers/eligibility/time anchors: the member credit and accessory discount inherit base eligibility (active on signed_date; active on the date the accessory is added); windows are anchored on "the date of handling" in every ext rule; the member-credit tenure is anchored on signed_date. No contradiction between policies.
- Cross-category reads: service (service_lines refrigerant / repair_parts / repair_labor), plan (agreement fields, plan_billing_entries late_fee, plan_service_entries tune-up and tier_upgrade grants), finance (status, variant_name, amount_financed), filter (status). All are declared in `cross_category` of the reading policy.
- Terminal states: each write lands one ledger row and moves project_balance; no status transition is written by these tools.
- Claimed scopes (from the auditor's own walk of the two worlds, before reveal): task 0 = {install_ext_progress_installment (root), install_ext_line_set_change_order_charge}; task 1 = {install_ext_contract_deposit (root), install_ext_member_install_credit, install_ext_accessory_member_discount}. Pairwise disjoint and jointly complete over the five extended policies (to be compared with charter_scope after reveal, in the task files).

### rule_compute_equivalence

Swept every binding of every policy against its `compute_basis` quotation and back against the rule sentence by sentence.

- install_ext_line_set_change_order_charge: list price `P('line_set_change_order_usd')`; refrigerant spend `XSUM(service_lines, service_charge, line_type=refrigerant, 24 months, posted_date)` = "refrigerant charges billed on the homeowner's Harbison service calls in the co_refrig_window_months months before the date of handling"; credit ladder 750/300 → 200/100/0; discovery share from the latest confirmed change_order_approval `created_at` against the latest permit_fee `posted_date` and signed_date (60/80/100) = the rule's three clauses; member pct from plan status + consecutive_terms + tier accessory_discount_pct (+5 at ≥5 terms); promo fee from the finance account linked by install_id (approved/active; deferred 6 %, 18/36-month equal-payment 4 %); admin fee by count of change_order charges (≥2 → 95, 1 → 45, 0 → 0); order credit → MX(0) → share → member → fee → + admin → single RND. Equivalent both ways.
- install_ext_progress_installment: charges, credits, net, share ladder (15000/11000 → 50/40/30), financed exclusion (approved and amount_financed < net → amount_financed; approved and ≥ net → net; else 0), upkeep ladder, change-order points ladder, `RND((net − excl) × (share + pts)/100 × upkeep)`. Equivalent, EXCEPT the visit count (finding G3 below).
- install_ext_member_install_credit: tier credit, MONTHS(enrolled_date, signed_date) with auto_renew, systems_covered ladder, late_fee count over 12 months, tier_upgrade grants over 3/6 months, repair_parts + repair_labor charges over 12 months (gross, "counted before any member discount"), `RND((tier + tenure + systems) × standing × tier_age + repair)`. Equivalent. (`mc_recent_upgrades` filters entry_reason only, but plan_coverage_grant carries only new_term / renewal_term reasons, so only visit grants can match; no divergence.)
- install_ext_accessory_member_discount: per-tier pct + filter / point-of-sale / premium / dues points, × bundle factor, one RND. The rule is stated per accessory ("on that accessory", "the posting of the accessory charge", "the accessory charge itself"); compute binds `ad_code` and `ad_charged_date` to the LATEST accessory charge on the project (finding G4).
- install_ext_contract_deposit: net price, rate ladder, upkeep ladder, `MX(deposit_min, RND(net × pct/100 × upkeep))`, upgrade share, air-quality share, final RND. Equivalent except the visit count (G3) and the air-quality share's base (G5).
- Every factor ladder tier appears as a rule sentence and as a branch of its `decides` binding, and vice versa; no tier lives in one face only.

### action_binding_and_uuids

- Each `(target_tool, computes)` pair is claimed by exactly one policy (table above). No base policy names a task tool.
- Docstrings: each describes one atomic ledger write; none names another tool, states a position in a sequence, or carries an ordering word relative to another action (the only hits for before/after/first/then/once/already are "from then on the project's money history shows it", "once this charge is included", "already rounded to the cent" — none orders actions).
- Tool bodies (task_tools.py lines 45-61, 98-115, 151-165, 209-225, 262-279): each creates one install_ledger row and adds/subtracts the amount on install_projects.project_balance; none reads history, judges eligibility, checks a prerequisite, refuses or hints.
- uuid8 tails: a6215d22, 728e8d1f, c2d484b0, 3312a288, 7afff78b — five distinct values, no shared prefix or suffix, no sequential or adjacent pattern. PASS.

### prerequisite_graph

- `prerequisite` filled on all five: line-set `[]`, progress 1 edge, member credit `[]`, accessory discount `[]`, deposit 2 edges.
- Edges: progress → line_set_change_order_charge (value_input, gate pp_net); deposit → member_install_credit (value_input, gate dp_member_credit); deposit → accessory_member_discount (value_input, gate dp_acc_discount). Every `problem` is an extended policy id of this file, none self-referential; graph acyclic (two disjoint stars).
- `policy_source` of each edge is verbatim the last sentence (progress) and the last two sentences (deposit) of the blocked policy's own rule.
- `form: state` on all three; no `fallback_reason`, correctly absent.
- `condition`: progress — "Every install_change_requests row of request_type change_order_approval and request_status confirmed on the project has an install_ledger install_charge entry of line_type change_order carrying the same change_order_no" = the sentence's "every change order the homeowner has confirmed carries its charge on the project ledger"; deposit/member — "for a homeowner whose Comfort Club agreement was active on the contract's signed_date … carries an install_credit entry of line_type member_install_credit naming the contract-price charge" = "carries the Comfort Club member install credit owed on the contract-price charge"; deposit/accessory — "every install_charge entry of line_type accessory … for a homeowner whose agreement was active on the day it was added, has an install_credit … accessory_member_discount naming it" = "every accessory charged on the contract carries the accessory member discount owed on it". Neither strengthened nor weakened.
- `resolved_by` = the depended-on policy's `target_tool` in all three; each tool's effect (a ledger row of the waited-on line_type) makes the condition hold and changes the named gate binding (pp_net via pp_charges; dp_member_credit; dp_acc_discount). `kind: value_input` matches a binding that exists in the blocked compute in all three.
- No authoring-viewpoint wording ("in this task", "at the opening", "the current world") in any `prerequisite` field. PASS.

### prerequisite_sentences

Four-point test, each edge:

1. "The progress installment is fixed only after every change order the homeowner has confirmed carries its charge on the project ledger." — connective "only after"; waited-on state is record-visible (confirmed change_order_approval rows in install_change_requests; change_order charges in install_ledger); no tool, policy id, snake_case token or row id; scope "every change order the homeowner has confirmed" equals the condition. The only write in this difficulty that creates an install_charge of line_type change_order is bill_change_order_a6215d22, so exactly one write brings the state about. Derivation: sentence → find the confirmed approval with no charge carrying its number → the policy whose rule bills a change order (install_ext_line_set_change_order_charge, "billed as a numbered change order … charged once, under the change-order number the homeowner approved") → bill it. The resolving action is unique; the amount is that policy's only where the unbilled change order is a line set (observation G6).
2. "The contract deposit is fixed only after the project ledger carries the Comfort Club member install credit owed on the contract-price charge." — "only after"; state form; no tool or id; "owed" carries the active-on-signed_date qualification. Only post_member_install_credit_c2d484b0 writes member_install_credit. Derivation: sentence → contract-price charge with no member_install_credit naming it while the agreement is active → install_ext_member_install_credit ("posted once as a member_install_credit naming the contract-price charge") → post it. Single reading.
3. "The contract deposit is not worked out until every accessory charged on the contract carries the accessory member discount owed on it." — "not … until"; state form; only post_accessory_member_discount_3312a288 writes accessory_member_discount. Derivation: sentence → accessory charge with no accessory_member_discount naming it while the agreement is active → install_ext_accessory_member_discount → post it. Single reading.

- No rule restates another policy's prerequisite sentence; no rule carries a second wording, a tool name or another problem's id for any dependency; the depended-on rules (line-set, member credit, accessory discount) do not mention the progress installment or the deposit.
- Undeclared cross-problem orders in extended rules: none found. The line-set rule's "change-order charges already posted" and the deposit rule's reads of rebate/multi-system credits read state but state no order between problems of this difficulty.
- Base rule sentences stating a cross-problem order: install_change_orders "A change order is billed only after the homeowner has confirmed a change_order_approval request for that change order number." No task tree in this difficulty rests on it (the approval is a homeowner request with no task tool, and in both worlds the relevant approvals are already settled) → observation G8.

### override_declarations

Sentence-by-sentence against every `base_policy_refs` entry:

- line-set: install_change_orders s1 (line set at line_set_change_order_usd) — handled differently, declared in `overwrite`. s2 (billed only after confirmed approval), s3 (homeowner's decision), s4 (numbered from 1, total ≤ change_order_max_pct), s5 (no change order once installed; declined never billed) — followed / restated ("a change order the homeowner declined or withdrew is never charged"). install_contract_pricing, install_accessories_and_protection (member discount on accessories only; ext gives a member discount on the line-set CO as part of the declared replacement price, it does not touch the accessory sentence), install_cancellation_after_rescission, install_scheduling_permit (permit_fee posted at scheduling — used as the scheduling date, consistent) — followed.
- progress: install_deposit_and_payment s2 "The remaining balance is due final_payment_due_days after installed_date, and 0 means on the installation day" — handled differently, declared. Remaining sentences (financed balance paid by disbursement, homeowner pays the uncovered part, oldest charge first, close only at inspected and zero balance) — followed. install_financing_link — followed.
- member credit: install_member_credit s1 — declared. s2 (active on signed_date), s3 (once per project, not cash, reversed on cancellation), s4 (stacks independently) — followed/restated. Other refs (multi-system, accessories, rescission, cancellation, rebate, refunds) — not touched.
- accessory discount: install_accessories_and_protection clause "receives the tier's accessory_discount_pct on that accessory, posted as an accessory_member_discount naming the accessory charge and rounded to the cent half up" — declared. Remaining sentences (one charge per code, included accessory never billed, smart thermostat availability, protection upgrade) — followed.
- deposit: install_deposit_and_payment clause "takes a deposit at signing of deposit_pct of the contract price or deposit_min_usd, whichever is higher, rounded to the cent half up" — declared (replaced_by is the net-price baseline; the member-rate, upkeep and share sentences are further sentences of the same ext rule that replaced it). "A project whose approved financing covers the full contract price takes no deposit" — restated. Other sentences — not touched.
- Disguised forms: no anonymous intermediate overriding a base quantity, no 0/1 multiplier zeroing a base-fixed amount (the progress "whole net amount excluded" tier is inside the ext's own computation, consistent with base "homeowner pays any part the financing does not cover"), no dropped base branch. No artifact calls the base output "wrong".
- Finding: no undeclared override. Each ext rule opens with its baseline sentence (e.g. "the line-set change-order charge is the package's line_set_change_order_usd") and later works the same quantity out with factors; this is the baseline-plus-factors form the framework requires and is not counted as an override conflict.

### factor_ladders

| policy | factor | label | decides | tiers | multi-source (distinct records) | cross_difficulty | honest label? |
| --- | --- | --- | --- | --- | --- | --- | --- |
| line-set | refrigerant_history_credit | parameter | co_refrig_credit | 3 | no | service | yes |
| line-set | discovery_share | method | co_field_share | 3 | yes (install_change_requests.created_at × install_ledger permit_fee posted_date × signed_date) | – | **no** — 60 / 80 / 100 % substituted into the same `× share/100` |
| line-set | member_change_order_discount | parameter | co_member_pct | 3 | no (one agreement row) | plan | yes |
| line-set | promotional_financing_fee | parameter | co_fin_fee_pct | 3 | no (one account row) | finance | yes |
| line-set | change_order_admin_fee | parameter | co_admin_fee | 3 | no | – | yes |
| progress | progress_share_by_size | parameter | pp_share_pct | 3 | no | – | yes |
| progress | financed_exclusion | parameter | pp_fin_excluded | 3 | yes (finance account × install_ledger net) | finance | yes |
| progress | upkeep_factor | method | pp_upkeep | 3 | no | plan | **no** — 0.8 / 0.9 / 1.0 multiplier |
| progress | change_order_points | parameter | pp_co_points | 3 | no | – | yes |
| member | tenure_bonus | parameter | mc_tenure_bonus | 3 | yes (plan enrolled_date/auto_renew × install_projects.signed_date) | plan | yes |
| member | covered_systems_bonus | parameter | mc_systems_bonus | 3 | no | plan | yes |
| member | standing_factor | method | mc_standing | 3 | no | plan | **no** — 0.7 / 0.85 / 1.0 multiplier |
| member | tier_age_factor | method | mc_tier_age | 3 | no | plan | **no** — 0.5 / 0.75 / 1.0 multiplier |
| member | repair_to_replace_credit | parameter | mc_repair_credit | 3 | no | service | yes |
| accessory | filter_subscriber_points | parameter | ad_filter_pts | 3 | yes (filter_subscriptions.status × install_ledger accessory_code) | filter | yes |
| accessory | point_of_sale_points | parameter | ad_pos_pts | 3 | yes (signed_date × accessory posted_date) | – | yes |
| accessory | premium_accessory_points | parameter | ad_premium_pts | 3 | no | – | yes |
| accessory | prepaid_dues_points | parameter | ad_dues_pts | 3 (fall-through unreachable, G2) | no | plan | yes |
| accessory | protection_bundle_factor | method | ad_bundle | 3 | no | – | **no** — 1.5 / 1.25 / 1.0 multiplier |
| deposit | deposit_rate | parameter | dp_pct | 3 | no (status and tier of one agreement row) | plan | yes |
| deposit | seasonal_upkeep_factor | method | dp_upkeep | 3 | no | plan | **no** — 0.85 / 0.95 / 1.0 multiplier |
| deposit | protection_upgrade_share | parameter | dp_upgrade_share | 3 | no | – | yes |
| deposit | air_quality_accessory_share | parameter | dp_acc_share | 3 | no (one ledger row) | – | yes |

- Counts per policy (declared): line-set 5 (4 p / 1 m), progress 4 (3 p / 1 m), member 5 (3 p / 2 m), accessory 5 (4 p / 1 m), deposit 4 (3 p / 1 m) — all within 4-6, ≥2 parameter. After striking mislabelled `method` labels (G1): **0 honest `method` factors in every one of the five policies**.
- Bindings are disjoint within each policy; every `decides` is an input binding, never `result`.
- Every ladder has three pairwise-disjoint tiers stated in full in its rule, each tier's value drawn from the policy's params or the plan charter's tier parameters; no two tiers of one ladder select the same value.
- Every fall-through equals the declared factor baseline and equals what the policy's `baseline.rule` gives for that input (0 credits/fees/points/shares; 100 % share; factor 1.0; deposit_pct for the deposit rate; 30 % share for the progress share).
- Realism of conditions/outcomes: the conditions (refrigerant history, discovery timing, membership loyalty, promo-plan cost, change-order count, project size, financing, kept tune-ups, tenure, systems, late fees, recent tier upgrade, repair history, filter subscription, point-of-sale timing, accessory price, dues billing, protection bundle, deposit tier, special-order collection) are each ones a residential HVAC installer can plausibly weigh, except the prepaid-dues fall-through (G2).
- `baseline.params`: the accessory policy names `ad_no_bundle_factor`, which its `baseline.rule` never uses (G7, observation). The member-credit baseline names no own key (the tier's install_credit_usd is a plan parameter); acceptable.

### findings

**G1 — SOURCE-FACTOR RED: every `method` label in the charter is a numeric multiplier (mislabelled effect).**
- Symptom: each policy's sole (or both) `method` factor selects only a different constant that enters one unchanged formula.
- Root cause: the six `method` ladders are rate ladders. Evidence (compute): `co_field_share: K('co_after_schedule_share_pct') if … else (K('co_after_signing_share_pct') if … else K('co_standard_share_pct'))` then `co_after_share: co_after_credit * co_field_share / 100`; `pp_upkeep: K('pp_high_upkeep_factor') if … else (K('pp_low_upkeep_factor') …)` then `result: RND((pp_net - pp_fin_excluded) * (pp_share_pct + pp_co_points) / 100 * pp_upkeep, 2)`; `mc_standing` and `mc_tier_age` (0.7/0.85/1.0 and 0.5/0.75/1.0) enter `RND(mc_subtotal * mc_standing * mc_tier_age + mc_repair_credit, 2)`; `ad_bundle` (1.5/1.25/1.0) enters `RND(ad_charge * ad_pct / 100 * ad_bundle, 2)`; `dp_upkeep` (0.85/0.95/1.0) enters `RND(dp_net_price * dp_pct / 100 * dp_upkeep, 2)`. The rule's own wording is "is multiplied by …" in every tier.
- Demonstrated consequence: the algorithm is identical across tiers; only a number changes — the definition of a `parameter` tier. Struck, every computation of the charter has 0 `method` factors against the floor of 1.
- Affected: `extended_policies[*].factors[effect=method]` of all five policies (discovery_share, upkeep_factor, standing_factor, tier_age_factor, protection_bundle_factor, seasonal_upkeep_factor). Bears on task 0 (line-set, progress) and task 1 (member credit, accessory discount, deposit).

**G2 — SOURCE-FACTOR RED: prepaid_dues_points has an unreachable fall-through (unreal ladder).**
- Symptom: the ladder is "annual billing adds ad_annual_bonus_pts …, monthly billing adds ad_monthly_bonus_pts …, and a homeowner with no agreement adds no prepaid-dues points".
- Root cause: the same rule admits only "A Comfort Club member whose agreement is active on the date the accessory is added" to this write, and `plan_agreements.billing_frequency` is the enum {annual, monthly} (db_schema). No customer who reaches post_accessory_member_discount can sit on the fall-through.
- Demonstrated consequence: the fall-through tier, which is also the factor's baseline (`ad_dues_pts: '0'`), describes a situation no customer reaching this write can be in; the ladder has two live tiers (< 3), and its baseline is a treatment the business never gives any customer of this write.
- Affected: `install_ext_accessory_member_discount.factors[prepaid_dues_points]`, its rule sentence and `ad_dues_pts`. Bears on task 1.

**G3 — SOURCE-POLICY RED: progress installment and deposit count forfeited tune-ups as "completed".**
- Rule: progress "the Comfort Club tune-up visits completed on the homeowner's agreement in the pp_upkeep_window_months months"; deposit "counts the Comfort Club tune-up visits completed on the agreement in the dp_upkeep_window_months months".
- Compute: `pp_visits: XCOUNT('plan', 'plan_service_entries', within_months=K('pp_upkeep_window_months'), date_field='entry_date', event_type='plan_tuneup_visit')`; `dp_visits` identical with the 12-month window — no entry_reason filter.
- Plan charter (`blueprint/products/plan.yaml`, event plan_tuneup_visit): "A maintenance visit is performed, or a booked visit is forfeited because the member missed it or cancelled too late … entry_reason: completed_visit, no_show_forfeit or late_cancel_forfeit."
- Demonstrated consequence (same situation, two conclusions): a member with one completed_visit and one no_show_forfeit plan_tuneup_visit in the last 12 months — the deposit rule gives "exactly dp_one_season_visits" → × 0.95; compute counts 2 → × 0.85. Likewise for the progress installment at the 2 / 4 boundaries.
- Affected: `install_ext_progress_installment.compute.pp_visits`, `install_ext_contract_deposit.compute.dp_visits`. Bears on task 0 (progress) and task 1 (deposit); whether it changes their scored value is checked in each task file.

**G4 — SOURCE-POLICY RED: accessory member discount compute reads only the latest accessory on the project.**
- Rule (per accessory): "receives an accessory member discount on that accessory …", "count the days from the contract's signed_date to the posting of the accessory charge", "follow the accessory charge itself".
- Compute: `ad_code: LATEST('install_ledger', 'accessory_code', …, line_type='accessory')`, `ad_charged_date: LATEST(… 'posted_date' …, line_type='accessory')`, `ad_charge: SUM(… accessory_code=ad_code)`.
- Demonstrated consequence: project signed day 0 with a uv_germicidal_light charged day 0 and a whole_home_surge_protector charged day 3, active filter subscription. Discount owed on the UV light: rule → IAQ filter points (ad_iaq_filter_bonus_pts), same-day points (ad_same_day_bonus_pts), mid-premium point on 849; compute → other-accessory filter points (ad_other_filter_bonus_pts), first-week point (ad_first_week_bonus_pts) and no premium point on the surge protector's 295 charge — a different amount on a different base.
- Affected: `install_ext_accessory_member_discount.compute` (ad_code, ad_charged_date, ad_charge). Bears on task 1.

**G5 — SOURCE-POLICY RED: the deposit's air-quality share is computed on every accessory, not on each air-quality accessory.**
- Rule: "a uv_germicidal_light, media_air_cleaner or steam_humidifier charged at dp_premium_iaq_usd or more is collected at dp_premium_iaq_share_pct percent of its net charge, one charged below dp_premium_iaq_usd at dp_iaq_share_pct percent, and any other accessory, or none, adds nothing."
- Compute: `dp_acc_code: LATEST(… accessory_code …)`, `dp_acc_charge: SUM(… line_type='accessory')`, `dp_acc_discount: SUM(… 'accessory_member_discount')`, tier tested on `dp_acc_charge`.
- Demonstrated consequence: surge protector (295) charged first, then steam humidifier (2450), no member discounts. Rule: 100 % × 2450 = 2450.00 (surge protector adds nothing). Compute: latest code steam_humidifier, 2745 ≥ 1200 → 100 % × 2745 = 2745.00. Conversely, a UV light (849) charged before a surge protector gives the rule 424.50 and compute 0.
- Affected: `install_ext_contract_deposit.compute` (dp_acc_code, dp_acc_charge, dp_acc_discount, dp_acc_share). Bears on task 1.

**G6 — Observation: the progress-installment prerequisite sentence covers every confirmed change order, but the records never say what a change order is for.**
- The sentence and condition cover every confirmed change_order_approval; the declared `problem` is the line-set policy only; base install_change_orders prices duct modification per foot and "other scope at the price written on the change order". `install_change_requests` (db_schema) has only install_request_id, customer_id, install_id, request_type, change_order_no, request_status, created_at — no scope, quantity or price. The resolving tool is unique, but which policy prices the bill depends on a fact no table records. What this costs task 0 is shown in `0.md`.

**G7 — Observation:** `install_ext_accessory_member_discount.baseline.params` names `ad_no_bundle_factor`, which its `baseline.rule` ("the tier's accessory_discount_pct of the accessory charge, rounded to the cent half up") never uses. The baseline still gives a definite number, so there is no demonstrated consequence.

**G8 — Observation:** base install_change_orders states a cross-problem order ("A change order is billed only after the homeowner has confirmed a change_order_approval request for that change order number"). No tree of this difficulty rests on it as an edge; in both worlds the approvals involved are already confirmed or withdrawn at the opening.

**G9 — Observation:** the progress installment's net amount ("every charge on the project less every credit on it") and the deposit's net price (member credit, rebate, multi-system discount) also read credits posted under base policies that have no task tool and no edge. In a world where such a credit is owed but unposted, the order would matter and no sentence fixes it. Neither audited world has such a credit owed and unposted (checked per task).

## closing_checklist

Written after both tasks' frozen derivations and GT comparisons were on disk (reveal 2026-10-05T15:48:43Z). Nothing above this heading was changed after the reveal.

**Status: NOT CLOSED.** Not every task passes all four relationships.

| task | policy self-consistency | problem tree | factors | unique solution |
| --- | --- | --- | --- | --- |
| 0 (`0.md`) | SOURCE-POLICY RED (charter G3, not realised on its world) | PASS | SOURCE-FACTOR RED (G1) | SOURCE-TASK RED (T0-1: scope of CO 2 unreachable) |
| 1 (`1.md`) | SOURCE-POLICY RED (charter G3/G4/G5, not realised on its world) | PASS | SOURCE-FACTOR RED (G1, G2, T1-3) | PASS |

Checklist items:
- Audit files correspond one-to-one with tasks 0 and 1, with `_difficulty.md` alongside. This is the first revision. Not every comparison carries a PASS.
- Coverage and scopes: task 0 = {line-set, progress} and task 1 = {member credit, accessory discount, deposit}. They are pairwise disjoint and cover all five extended policies (charter_scope confirms). Task tools and GT are closed over these. Every uuid8 is independent (§ action_binding_and_uuids).
- Trees: task 0 has n = 1 with 1 value_input edge; task 1 has n = 2 with 2 value_input edges. Each tree has an owner=user root. The difficulty-wide graph is acyclic.
- Factors: every computation has a self-sufficient baseline giving a definite non-gold number, 4-6 declared factors with ≥ 2 parameter, and every factor bears weight on its world. **However, every computation has 0 honest `method` factors (G1).** The accessory discount also has an unreal ladder (G2) and no near-miss (T1-3).
- The instantiation-stage gates were not re-run by this audit. The coordinator's snapshot (all green) is the only gate evidence; the gates do not detect G1-G5 or T0-1.

## revision_2

### charter_global_frozen (revision 2)

- Auditor: the same independent erl-task-policy-audit agent as round 1.
- Freeze time: 2026-10-05T18:15Z. This section was written before either task's round-2 GT was revealed. Nothing in it derives from a round-2 GT field.
- Inputs (sha256 recomputed by the auditor and equal to `/tmp/erl37/views_r2/replacement_installation_projects/charter.sha256`):

| input | round 1 | round 2 | changed? |
| --- | --- | --- | --- |
| install.extended.yaml | f774f888… | 3b164cec51062d80a01190bdf402d9f3f186e72ee5b931472b2123fe796bb3f2 | yes |
| task_tools.py | 2e979f06… | 313977e5eee4921de203f63da380e43b392bab89a66aaf9dc192cda4e9bae06f | yes |
| task_0 masked view | 4ffb5bd0… | baaa5e77aa9335896813c3faca3c920da56bf6a261bf81b1cea412ec220489e2 | yes |
| task_1 masked view | 9bf93388… | 707524a1817a5a14ba547851f6562de4b68c667ce2c37cb07df85188a86c1b55 | yes |

  - Because both shared inputs changed, every charter-global section below is re-derived in full; nothing is carried forward by reference.
  - Blueprint files (install.yaml, plan.yaml, db_schema.json, share_tools.py) carry mtimes from before round 1. The base section of the extended charter (lines 1-1185) is still byte-identical to `blueprint/products/install.yaml`.
- Entry conditions: the round-2 gate snapshot `/tmp/erl37/gates/replacement_installation_projects.r2.snapshot.txt` shows EXTENDED, TASK TOOL CONTRACT, REPLAY, SOLVABILITY, COMPUTE, GROUNDING and SCOPE OK, plus CACHE-DIFF INFO. Masked views and hashes were supplied. Complete.
- contamination_disclosure (round 2): this auditor revealed and read the round-1 GT of both tasks (values, factor traces, design_rationale) at 2026-10-05T15:48:43Z, before this revision. That knowledge covers the round-1 worlds and conventions, not the round-2 worlds. The round-2 derivations below are recomputed from the round-2 charter and views alone, and every changed input was re-read. The disclosure is made so that the round-2 blind answers are weighed accordingly. No round-2 task JSON was opened before the freeze.

### policy_conflict_scan (r2)

- Same five extended policies, the same subjects, target tools and owners as round 1. No two policies decide one scored quantity.
- Scope ledger expected from the worlds: task 0 = {line-set (prerequisite), progress (root)}; task 1 = {member credit, accessory discount (prerequisites), deposit (root)}. Disjoint and complete.

### rule_compute_equivalence (r2)

Swept every binding of all five policies. Every `compute_basis` value is a verbatim substring of its rule (checked mechanically). Per policy:

- **Line-set.** The refrigerant-history credit is a three-way method:
  - leak-search and refrigerant both billed in the window → `co_leak_labor` = XSUM of repair_labor lines with task_code refrigerant_leak_search;
  - refrigerant billed, no leak search → `co_last_refrig` = XLATEST refrigerant line. It is unwindowed, but in this tier a windowed refrigerant charge exists, so the latest line overall lies inside the window: equivalent;
  - no refrigerant → 0.
  - The remaining bindings are unchanged from round 1. The result carries `+ 0.000001` before RND (see N4).
- **Progress.**
  - `pp_visits` now filters `entry_reason='completed_visit'`, matching "never counting a visit forfeited". **G3 closed for this policy.**
  - change_order_collection: ≥ 3 confirmed → all change_order charges; exactly 2 → the LATEST change_order charge by posted_date; fewer → 0.
  - `result = RND(MX(0, net − excl − co_full) × share/100 × upkeep + co_full)` matches "taken off … never below zero; … share applied once; … upkeep; … collected in full then added". Equivalent.
- **Member credit.** repair_to_replace is now a method:
  - high → every repair_labor line in the window (XSUM);
  - mid → `mc_last_labor` = XLATEST repair_labor line, unwindowed. A mid-tier world has repairs in the window, so the latest labor line lies inside it. The edge case of a repair with no labor line, or with two labor lines, is N3 below;
  - otherwise 0.
  - Other bindings are as in round 1. Equivalent.
- **Accessory discount.**
  - Now one discount per contract on the total of accessory charges (`ad_acc_total` SUM). IAQ presence is tested by count, and point of sale compares the same-day count with the total count.
  - Filter points: `MN(5, int(MONTHS(started, NOW)/12))` = "one percentage point for each whole year … at most ad_filter_max_pts".
  - Dues points: annual + auto_renew / annual only / else.
  - The rule is now stated per contract, so the round-1 "latest accessory only" divergence is gone. **G4 closed.**
- **Deposit.**
  - Net price = contract price + accessories − member credit − accessory discount − rebate − multi-system, as the rule states.
  - Upkeep counts only `completed_visit`, by term (annual) or by rolling 12 months (monthly). **G3 closed for this policy.**
  - The IAQ share is taken on the SUM of the uv / media / steam charges only, tiered on that same total; the rule says "the total of every uv_germicidal_light, media_air_cleaner and steam_humidifier charge". **G5 closed.**
- Every ladder tier is present in both faces.

### action_binding_and_uuids (r2)

- `(target_tool, computes)` pairs are unchanged and each is claimed once.
- Tool bodies are unchanged in substance (create one row, adjust the balance; no checks).
- Only the accessory-discount docstring changed ("covering the accessories … naming the contract's highest-priced accessory charge"). It names no other tool and states no sequence.
- uuid8 tails are unchanged and independent. PASS.

### prerequisite_graph and prerequisite_sentences (r2)

- Graph unchanged: progress → line-set; deposit → member credit; deposit → accessory discount. All value_input, all state form, acyclic. Gates (pp_net, dp_member_credit, dp_acc_discount) exist in their computes, and every `policy_source` is verbatim in its blocked rule.
- The deposit → accessory sentence is now "The contract deposit is not worked out until the accessories charged on the contract carry the accessory member discount owed on them." Its condition ("an accessory_member_discount naming its highest-priced accessory charge") is at the same scope as the new one-discount-per-contract rule. The only writer is post_accessory_member_discount_3312a288.
- The progress edge's `effect` now names pp_latest_co, which is accurate: with two confirmed approvals, the newly posted charge becomes the latest one collected in full.
- No new cross-problem order appears in any extended rule. PASS.

### override_declarations (r2)

- The line-set, progress, member-credit and deposit overwrites cover the clauses they change.
- The deposit's replaced_by now also adds accessories and subtracts the accessory discount, and this is declared.
- **New finding N1 (accessory discount; see findings):** the superseded clause covers the benefit ("receives the tier's accessory_discount_pct on that accessory, posted as … naming the accessory charge …"). It does not cover the base eligibility clause "whose agreement is active on the date the accessory is added". The extended rule rewrites that inherited clause as "active on the date **an** accessory is added" and extends the benefit to "every accessory charged on the contract".

### factor_ladders (r2)

| policy | factor | label | honest? | tiers | multi-source | cross-difficulty |
| --- | --- | --- | --- | --- | --- | --- |
| line-set | refrigerant_history_credit | method | yes: sum of leak-search labor vs a single latest refrigerant line vs none | 3 | yes (leak-search line × refrigerant line, distinct records) | service |
| line-set | discovery_share | parameter | yes (relabelled) | 3 | yes | – |
| line-set | member_change_order_discount | parameter | yes | 3 | no | plan |
| line-set | promotional_financing_fee | parameter | yes | 3 | no | finance |
| line-set | change_order_admin_fee | parameter | yes | 3 | no | – |
| progress | progress_share_by_size | parameter | yes | 3 | no | – |
| progress | financed_exclusion | parameter | yes | 3 | yes | finance |
| progress | upkeep_factor | parameter | yes (relabelled) | 3 | no | plan |
| progress | change_order_collection | method | yes: which charges leave the share base and are collected whole (all / latest / none) | 3 | yes (confirmed approvals × ledger charges) | – |
| member | tenure_bonus | parameter | yes | 3 | yes | plan |
| member | covered_systems_bonus | parameter | yes | 3 | no | plan |
| member | standing_factor | parameter | yes (relabelled) | 3 | no | plan |
| member | tier_age_factor | parameter | yes (relabelled) | 3 | no | plan |
| member | repair_to_replace_credit | method | yes: sum of window labor vs latest labor line vs none | 3 | no | service |
| accessory | filter_subscriber_points | method | yes: points computed from subscription age (capped) vs flat vs none | 3 | yes (subscription × install ledger) | filter |
| accessory | point_of_sale_points | parameter | yes | 3 | yes | – |
| accessory | premium_accessory_points | parameter | yes | 3 | no | – |
| accessory | prepaid_dues_points | parameter | yes | 3 (annual + auto_renew / annual / monthly), all reachable by eligible members | no | plan |
| accessory | protection_bundle_factor | parameter | yes (relabelled) | 3 | no | – |
| deposit | deposit_rate | parameter | yes | 3 | no | plan |
| deposit | seasonal_upkeep_factor | method | yes: visit count taken over the current term (annual), over a rolling 12 months (monthly), or not at all | 3 | no | plan |
| deposit | protection_upgrade_share | parameter | yes | 3 | no | – |
| deposit | air_quality_accessory_share | parameter | yes | 3 | no | – |

- Counts:

| policy | factors | parameter | method |
| --- | --- | --- | --- |
| line-set | 5 | 4 | 1 |
| progress | 4 | 3 | 1 |
| member credit | 5 | 4 | 1 |
| accessory discount | 5 | 4 | 1 |
| deposit | 4 | 3 | 1 |

- Each method factor selects a different algorithm, not a different constant. **G1 closed.**
- The prepaid-dues fall-through is now "monthly billing", which eligible members can hold. **G2 closed.**
- The accessory `baseline.params` is now `[]`. **G7 closed.**
- Fall-throughs equal the declared baselines and equal what each `baseline.rule` gives. No two tiers of one ladder share a value or method.
- All conditions and outcomes are ones a residential installer plausibly weighs:
  - crediting the leak search that diagnosed the failing line set;
  - collecting late change orders in full;
  - repair-to-replace labor credit;
  - subscription-age loyalty points;
  - per-term vs rolling upkeep counting.

### findings (r2)

**Round-1 items:**

| item | status in round 2 | evidence |
| --- | --- | --- |
| G1 | closed | factor_ladders (r2) |
| G2 | closed | factor_ladders (r2) |
| G3 | closed | pp_visits and dp_*_visits filter completed_visit |
| G4 | closed | per-contract rule and per-contract compute |
| G5 | closed | IAQ-only SUM and threshold |
| G7 | closed | accessory baseline.params is [] |
| G6 | open at schema level | install_change_requests still records no scope; whether task 0 now reaches CO 2's scope is judged in `0.md` revision_2 |
| G8 | unchanged observation | |
| G9 | unchanged observation | |

**N1 — SOURCE-POLICY RED (new): the accessory-discount eligibility for accessories added on different dates has two readings after the overwrite.**
- Passage A, base install_accessories_and_protection (not superseded, inherited): "A Comfort Club member whose agreement is active on the date the accessory is added …". Its structured eligibility `member_active_for_accessory_discount` is per accessory.
- Passage B, extended rule: "A Comfort Club member whose agreement is active on the date an accessory is added receives one accessory member discount covering every accessory charged on the contract … the tier's accessory_discount_pct of the accessory charges on the contract".
- Compute `ad_acc_total` sums every accessory charge with no date or status test.
- Same situation, two answers: accessory X (849) added on day 0 while the agreement is active; the agreement then lapses; accessory Y (295) is added on day 20.
  - A: only X qualifies, so the discount base is 849.
  - B and compute: active on the date an accessory (X) was added, so the discount covers every accessory and the base is 1144.
- The overwrite names only the benefit clause, so the inherited eligibility is weakened without a declaration.
- Affected: `install_ext_accessory_member_discount.rule` (first sentence), `overwrite`, `compute.ad_acc_total`.
- Bears on task 1. Whether it is realised there is judged in `1.md`.

**N2 — Observation:** progress `inputs.history` lists the plan_service_entries count without `entry_reason: completed_visit`, although compute and rule now exclude forfeits. This is metadata only; the scored compute is right.

**N3 — Observation:** the member-credit mid tier reads "the repair_labor charge of the most recent repair", while compute takes the single latest repair_labor *line* (XLATEST, unwindowed). They part ways when the most recent repair has two labor lines (same posted_date) or no labor line. The rule leaves "repair" (call or task) open, so no single contradiction can be quoted. Neither task world has such a call.

**N4 — Observation:** every compute now adds `+ 0.000001` before RND to force half-up on binary floats. The rule says "rounded to the cent half up". The two differ only for a true value within 1e-6 below a half-cent boundary, which no audited value approaches.

**N5 — Observation:** progress `pp_latest_co` is LATEST by posted_date. Two change-order charges posted on the same day leave "the most recently posted" undetermined at day granularity. In task 0 the dates differ.

### closing_checklist (r2)

Written after both round-2 frozen sections and comparisons were on disk (reveal 2026-10-05T18:16:11Z). Nothing above this heading in revision_2 was changed after the reveal.

**Status: NOT CLOSED.** One charter-global SOURCE-POLICY RED remains: N1, introduced by the G4 rework.

| task | policy self-consistency | problem tree | factors | unique solution |
| --- | --- | --- | --- | --- |
| 0 | PASS | PASS | PASS | PASS |
| 1 | SOURCE-POLICY RED (N1, charter-global; not realised on its world) | PASS | PASS | PASS |

- Round-1 REDs: all closed. G1, G2, G3, G4, G5, T0-1, T1-3 are verified closed above; G6 is resolved at task level; G7 is closed.
- Regressions: none found in values, tree or scopes.
- New defect: N1. New observations: N2-N5.
- Scopes are disjoint and complete. Trees are acyclic with the required value_input edges and owner=user roots. Every computation has 4-6 honest factors with exactly one honest method, an honest baseline, weight on its world, and a near-miss.
- Gates: only the coordinator's round-2 snapshot (all OK) was used; this audit did not re-run them.

## revision_3

### charter_global_frozen (revision 3)

- Auditor: the same agent. Freeze time: 2026-10-05T18:35Z. Written before either task's round-3 GT was revealed.
- Inputs (sha256 recomputed by the auditor; equal to `/tmp/erl37/views_r3/replacement_installation_projects/charter.sha256`):

| input | round 2 | round 3 | changed? |
| --- | --- | --- | --- |
| install.extended.yaml | 3b164cec… | 992d010ae266415ab1f59e6a058d6ca7d3690c10ed9a2d4c1fdcb54e1591deef | **yes** |
| task_tools.py | 313977e5… | 313977e5… | no |
| task_0 masked view | baaa5e77… | baaa5e77… | no |
| task_1 masked view | 707524a1… | 707524a1… | no |

- Because the charter changed, every charter-global section is re-derived. The tool contract is unchanged, so § action_binding_and_uuids (r2) carries forward on the unchanged task_tools.py hash.
- The base section (lines 1-1185) is still byte-identical to `blueprint/products/install.yaml`. Blueprint files carry pre-round-1 mtimes.
- Entry: the round-3 gate snapshot `/tmp/erl37/gates/replacement_installation_projects.r3.snapshot.txt` shows all seven gates OK plus CACHE-DIFF INFO.
- contamination_disclosure: the round-1 and round-2 GT of both tasks were read in earlier rounds. No round-3 task JSON was opened before this freeze.

### What changed (r2 → r3)

Established by diffing a structured dump of the r3 charter (rule, overwrite, prerequisite, cross_category, compute) against the r2 dump recorded in round 2, plus a fresh dump of factors, compute_basis, baseline and inputs. Only three policies changed:

1. **Progress.**
   - Collection tier 2 now reads "the change-order charge carrying the highest change-order number, which is the most recently approved one".
   - Compute: `pp_top_co_no = MAX(change_order_no)` and `pp_latest_co = SUM(amount where change_order_no = pp_top_co_no)`.
   - The factor ladder, prerequisite `effect` and `inputs` (now with `entry_reason: completed_visit` and a max on change_order_no) were updated to match.
2. **Member credit.** Mid tier now reads "the most recently posted repair_labor charge, the labor line of the latest repair". Compute is unchanged (`mc_last_labor` = XLATEST repair_labor).
3. **Accessory discount.**
   - The overwrite's superseded_clause is now the **whole** base sentence, eligibility included: "A Comfort Club member whose agreement is active on the date the accessory is added receives …".
   - replaced_by and the rule now say "active status on the date the accessory member discount is posted … a homeowner whose agreement is not in active status on that date receives none".
   - Compute adds `ad_member_status = CFIELD('plan','status')`, and the result is 0 unless the status is active. cross_category plan reads now include status.
   - The deposit → accessory edge condition now reads "… and the homeowner's Comfort Club agreement is in active status …".

### rule_compute_equivalence (r3)

- All compute_basis values are verbatim in their rules, every compute key has a basis, every baseline.rule is in its rule, and every prerequisite policy_source is in its blocked rule (checked mechanically).
- **Progress.** Base install_change_orders says "Change orders are numbered from 1 in the order approved", so the highest change_order_no is the most recently approved change order. The ledger maximum read by MAX/SUM is exactly "the change-order charge carrying the highest change-order number". Equivalent, and no longer depends on same-day posting order.
- **Member credit.** The rule now names "the most recently posted repair_labor charge", which is what XLATEST reads. Equivalent.
  - Residual: two repair_labor lines posted on the same day leave "most recently posted" undetermined at day granularity. Observation N3′, not realised in either world.
- **Accessory discount.** The eligibility date is now the posting date, i.e. the date of handling, and compute tests the agreement's current status. Equivalent.
- **Others.** Unchanged from r2 and still equivalent.

### prerequisite_graph and prerequisite_sentences (r3)

- Graph, kinds, gates and sentences are unchanged.
- The deposit → accessory condition now ties "owed" to the agreement's current active status, which matches the revised accessory rule (the discount is owed exactly when the agreement is active on the posting date).
- The progress edge `effect` matches the new collection rule.
- PASS.

### override_declarations (r3)

- Accessory: the superseded_clause now quotes the whole base sentence, including its eligibility condition. The replacement states one date (the posting date) and one consequence. Merged semantics are unique, and **no base eligibility is weakened without a declaration**.
  - The base structured gate `member_active_for_accessory_discount` (state_contract plan_agreements.status ∈ {active}, timing pre_action) agrees with a status test at the write.
- Other policies are unchanged from r2.
- PASS.

### factor_ladders (r3)

- No factor was added, removed or relabelled. Counts are unchanged (5/4/5/5/4 factors; exactly one honest method each).
- The change_order_collection method tier 2 now selects the charge by number rather than by posting date. It is still a distinct algorithm from tier 1 (sum of all) and tier 3 (none).
- The repair_to_replace method is unchanged in substance.
- PASS.

### findings (r3)

| item | status in round 3 | reason |
| --- | --- | --- |
| N1 (SOURCE-POLICY RED) | **closed** | the whole base sentence is now superseded; eligibility is restated on a single date; compute tests status |
| N2 | closed | progress inputs filter completed_visit |
| N3 | closed | rule now names the most recently posted repair_labor charge, matching compute; the same-day tie residual is observation N3′ |
| N4 | kept, observation | reworker's stated reason; no audited value lies within 1e-6 of a half-cent boundary |
| N5 | closed | collection now keyed on the highest change-order number, which the base numbering rule ties to approval order |
| G8, G9 | unchanged observations | |
| new defects | none found | |

### closing_checklist (r3)

Written after both round-3 frozen sections and comparisons were on disk (reveal 2026-10-05T18:35:19Z). Nothing above this heading in revision_3 was changed after the reveal.

**Status: CLOSED. All four relationships PASS for both tasks.**

| task | policy self-consistency | problem tree | factors | unique solution |
| --- | --- | --- | --- | --- |
| 0 | PASS | PASS | PASS | PASS |
| 1 | PASS | PASS | PASS | PASS |

- **Traceability:** audit files 0.md and 1.md correspond one-to-one with tasks 0 and 1, with `_difficulty.md` alongside. Revisions 1-3 are appended in order, and older text is untouched.
- **Coverage and scopes:**
  - task 0 = {line-set, progress};
  - task 1 = {member credit, accessory discount, deposit};
  - pairwise disjoint and complete over the five extended policies;
  - task tools and GT are closed over these scopes;
  - each task tool has an independent, frozen uuid8.
- **Trees:**
  - task 0: n = 1, one value_input edge;
  - task 1: n = 2, two value_input edges;
  - both roots are owner=user, and the difficulty-wide graph is acyclic.
- **Factors:**
  - Every computation declares a self-sufficient baseline that gives a definite number different from gold.
  - Every computation has 4-6 factors, with ≥ 2 parameter and exactly 1 honest method.
  - Each task has ≥ 1 multi-source and ≥ 1 cross-difficulty factor, read from seeded rows.
  - Every ladder has 3 distinct tiers stated in its rule and implemented in compute; every factor bears weight on its world; every computation has a near-miss.
- **Remaining observations, without demonstrated consequence:**
  - N3′: a same-day tie between repair_labor lines.
  - N4: the +1e-6 rounding epsilon; kept by the reworker with a stated reason.
  - G8 and G9.
- **Gates:** this audit did not re-run the gates. The coordinator's round-3 snapshot (all seven OK) is the gate evidence on the final form.
