# Policy-task audit — financial_assistance_screening / charter-global

## revision_1

## charter_global_frozen
- Freeze time: 2026-10-20 14:22 UTC (written before any task's GT was revealed; nothing in this section derives from a revealed GT).
- Auditor: erl-task-policy-audit subagent (independent of the instantiator).
- Inputs and hashes (sha256, first 16): `assist.extended.yaml` fd8cefd9e3c56d71; `task_tools.py` 1bc59c84c3f80208; views `r1/0.view.json` ee6b7c7221d33206, `r1/1.view.json` d11a55384177479d (all match the brief).
- Entry evidence (gate snapshot supplied by the coordinator, not re-run): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK (--check), SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK. Masked views supplied with hashes. Entry conditions complete.
- Read: blueprint.yaml, db_schema.json, products/*.yaml (assist base; encounter, claim, plan, estimate charters for seeded-row judgement), share_tools.py (not needed beyond schema), assist.extended.yaml, task_tools.py, the two masked views, audits/render_source/XF_recipe.md, skills/erl-task-instantiate/scripts/check_compute.py (DSL semantics: MONTHS, XLATEST tie = first row in file order, CFIELD = first holding in file order, XSUM customer scoping).
- Masked and not read: tasks/financial_assistance_screening/tasks/*.json, worklog.md, /tmp/*_0073/, every other env/ scenario.
- Base copy check: every base key of assist.extended.yaml (category … policies) parses equal to blueprint/products/assist.yaml (mechanical dict compare: all True).
- Mechanical sweeps (scratch script under /tmp/pta_fas_audit/, own evaluator over the charter compute): every `compute_basis` quote is a whitespace-normalised substring of its rule; every `baseline.rule` sentence is in its rule; every `policy_source` is in its own rule; no compute binding lacks a basis; no factor id is a substring of a tool name; 31 factor ids, all distinct; task_tools.py has no ordering words (before/after/first/then/until/once) in any docstring.

### policy_conflict_scan
Six extended policies:

| id | target_tool (owner) | computes | prerequisite |
|---|---|---|---|
| assist_ext_supplement_debt_claim | sign_hardship_supplement_15cad132 (user) | qualifying_medical_debt_usd | [] |
| assist_ext_qualifying_debt | record_qualifying_debt_da5f54be (agent) | qualifying_medical_debt_usd | supplement (value_input, action form) |
| assist_ext_countable_assets | record_countable_assets_effcaeaa (agent) | liquid_assets_usd | [] |
| assist_ext_hardship_cap | approve_hardship_award_afb08b0b (agent) | hardship_liability_cap_usd | qualifying_debt, countable_assets (value_input, action form) |
| assist_ext_renewal_debt_claim | sign_renewal_debt_claim_3b9e07c1 (user) | qualifying_medical_debt_usd | [] |
| assist_ext_response_window | send_missing_information_notice_7f5665e5 (agent) | response_days | renewal_debt_claim (value_input, state form) |

- Overlapping subject `qualifying_medical_debt_usd` is written by three tools. Supplement and renewal claim are disjoint by rule (the supplement excludes "a renewal application (one filed while the patient holds an approved award)"); qualifying_debt applies only to "a complete application with no outside medical bills document accepted on it", so it never meets the renewal notice case (incomplete by definition). Compatible.
- Completeness: assist_ext_hardship_cap overwrites the base completeness clause for non-renewal hardship applications whose Riverbend debt (12 months before application date) exceeds the hardship share; assist_ext_response_window applies to renewals, which that overwrite keeps under base completeness by name. Compatible.
- Natural scope split implied by the trees: {hardship_cap, qualifying_debt, countable_assets, supplement} and {response_window, renewal_debt_claim}; disjoint and jointly complete. Verified against charter_scope only after reveal (task files).
- Conflicts with in-force base clauses are recorded under `override_declarations` (C1, C2, C3).

### rule_compute_equivalence
Sweep result per policy (each quantity, window, filter, tier, branch, cross read, rounding):
- supplement / renewal: liab_all, adj_all, sp_*, ct_*, appeal_*, held_*, has_bcp, bcp_notice, result — each matched by a rule sentence and implemented as stated; tie rule for the latest appeal matches XLATEST first-in-file; rounding RND matches "rounded half-up to the cent" at sp_agb, ct_part, result. Whole-month window stated ("a whole month running from a day of one month to the same day of a later month") but no month-end convention (C8).
- qualifying_debt: all seven parts implemented. Gaps: `rc_started` evaluates `DAYS(scheduled_service_date, NOW)`; for an issued recurring-course GFE with an empty scheduled_service_date (schema: "empty when unscheduled") the compute errors while the rule says "otherwise nothing is added for a recurring course" (C7). Multiple-match picks not stated in the rule: several insured out-of-pocket estimates tied to the pending account (`pend_est` takes the first in file order), several issued packages of the same variant (`pkg_id`) (C7). Window for older balances lacks the whole-month/month-end convention (C8).
- countable_assets: the rule sentence "This schedule took effect on 2025-10-01; liquid assets recorded on a case before that date stand as documented" has no compute binding and names a recording date that no field of assistance_cases holds (C4). `paid_since` = payments with MONTHS(posting, NOW) ≤ MONTHS(stmt_date, NOW) — the rule calls these "the Riverbend payments made since it", then defines them by whole-month distance; the two descriptions select different rows whenever a payment falls in the same whole-month bucket but before the acceptance date (C5). No month-end convention (C8).
- hardship_cap: every factor implemented as stated; the two overwrite sentences are gates with no compute (consistent). "A posting belongs to a span of whole months when fewer than that many whole months separate its posting date from the approval day" serves coverage_points and burden_share (C10) and carries no same-day/month-end convention (C8); the overwrite's "twelve months before the application date" window likewise (C8).
- response_window: `outside_none` counts OUTSIDE_MEDICAL_BILLS rows of any document_status; the rule says "no outside medical bills have been received" — a REQUESTED (or REJECTED-only) row is not a receipt (C6). Framing "Days are added while a payment plan is paused for the pending renewal": no record field holds a pause; tiers test only the active plan's tier (C13). `accounts` window lacks the whole-month convention (C8).

### action_binding_and_uuids
- (target_tool, computes) pairs are unique per policy (table above). Tool docstrings describe only body effects; no docstring names another tool or a sequence position; the notice tool's enum docstrings describe REQUESTED/NOT_REQUESTED per document without ordering words.
- uuid8 tails: 15cad132, da5f54be, effcaeaa, afb08b0b, 3b9e07c1, 7f5665e5 — distinct, no shared prefix, no sequence pattern. PASS.
- XF E: no datetime/time/random/uuid/secrets import (date maths in `_Calendar` static methods); every write tool calls ctx.update/create in its own body; no example values in docstrings; one enum per field; events written (assist_application_received-subject update, assist_household_updated, assist_approved + APPROVAL_LETTER notice, assist_documents_requested + MISSING_INFORMATION_NOTICE + assist_document_logged REQUESTED) have no cross-category triggers. PASS.

### prerequisite_graph
- Every policy fills `prerequisite`; edges: QD→supplement, cap→QD, cap→CA, RW→renewal. All `problem` ids are extended ids of this file, none self, graph acyclic (max depth 2).
- `policy_source` verbatim in the blocked rule (mechanical check PASS). form/fallback_reason consistent (three action edges carry fallback_reason; the state edge has none).
- `kind` value_input with `gate` bindings that exist: claimed (QD), debt_keep and asset_raise (cap), outside_add (RW). `resolved_by` equals the depended-on target_tool in all four.
- Condition strength: QD→supplement `condition` names "the debt claimed on the patient's signed hardship supplement" while the sentence waits on "the patient's signed claim of medical debt" — broader (C12).
- Observation: QD→supplement `effect` asserts the pre-supplement figure is "0.00" — a world fact (the base event stores the attested claimed debt at application), not a general statement.

### prerequisite_sentences
- QD: "The qualifying medical debt is not documented until the patient's signed claim of medical debt has been received on the case." Connective "not … until"; action form; no tool/id. Derivation: reader looks for a policy whose own rule has the patient sign a claim of medical debt → two policies do (hardship supplement; renewal's "claim of medical debt", the renewal rule's own term). The records (case not a renewal) then pick the supplement on a non-renewal case; on a complete renewal case the sentence is satisfied by the renewal claim, which the declared edge does not name (C12). Fallback test: the supplement is the only write that moves the case's qualifying medical debt before documentation; a state form ("once the case records the medical debt the patient claims", exactly the form the sibling RW edge uses) would single it out — fallback unjustified → observation O1.
- cap→QD: "The hardship liability cap is fixed only after the qualifying medical debt has been documented from Riverbend's records for the hardship test." Single reading → qualifying_debt ("Riverbend documents on the case the qualifying medical debt the hardship test uses"). Fallback justified (same field, no marker).
- cap→CA: "The hardship liability cap is not fixed until the countable liquid assets of the household have been recorded for the asset test." Single reading → countable_assets. Fallback justified.
- RW→renewal: "The missing-information notice of a renewal is sent only after the renewal case records the medical debt the renewal claims." State form; exactly one write brings it about (renewal claim; supplement excluded on renewals; QD needs a complete application). PASS.
- Depended-on rules restating the dependency: qualifying_debt opens "Before a Medical Hardship determination, Riverbend documents …" and countable_assets opens "Before a Medical Hardship determination, Riverbend records …" — the cap's own prerequisite sentences restated from the depended-on side (C11).
- No other cross-problem order in any rule.

### override_declarations
Sentence sweep against each `base_policy_refs` entry:
- supplement (refs assist_agg_multi_holding, assist_tier_determination; overwrite []): follows multi_holding (received on the open case as supporting information). Departs from tier_determination / parameter_schema: the debt window is anchored on "the signing day", the base anchors it on "months before the application date" (`hardship_debt_window_months`) — undeclared (C1).
- qualifying_debt (ref tier_determination; overwrite []): base "medical hardship applies only when qualifying_medical_debt_usd incurred in the last hardship_debt_window_months exceeds …" (schema: "documented medical bills (Riverbend and outside) incurred in the hardship debt window"). Extended adds older balances (postings outside the 12 months), care not yet rendered (scheduled single service, prepaid package, future recurring course) and anchors its window on the documentation day — undeclared (C1).
- countable_assets (ref tier_determination; overwrite []): base "where liquid_asset_test_applies is true, liquid assets do not exceed liquid_asset_limit_usd … a hardship applicant over the asset limit is denied as ASSETS_ABOVE_LIMIT", liquid assets = "cash, checking, savings, non-retirement brokerage" (parameter_schema), schema "documented liquid assets". Extended compares a figure net of four protections and a spending adjustment and overwrites the documented field with it — undeclared (C2).
- hardship_cap (5 refs; 2 overwrites): cap clause and completeness clause declared, replaced_by restates out-of-scope content and names its scope (XF D.16 PASS). award_period, medicaid_screening followed.
- renewal_debt_claim (refs multi_holding, tier_determination; overwrite []): opens the renewal case "on the household figures documented on the expiring award (its … household percent …)"; base `fpl_guideline_basis` HHS_GUIDELINE_…_IN_EFFECT_ON_APPLICATION_DATE and schema "computed by the eligibility screener on the application date" — undeclared whenever the guideline year changes (C3). Debt window anchored on the signing day (C1 member).
- response_window (refs completeness_and_documents, notices; 1 overwrite): due-date clause declared with scoped replaced_by. PASS.

### factor_ladders
| policy | factors (effect) | parameter / method | multi-source | cross_difficulty |
|---|---|---|---|---|
| supplement | selfpay_basis (method), appeal_holdout, hold_holdout, coverage_gap (parameter) | 3 / 1 | appeal_holdout, coverage_gap | encounter, claim |
| qualifying_debt | anticipated_care (method), prepaid_package, older_balance, coprovider_charges, course_planned, insurer_waiting | 5 / 1 | anticipated_care, coprovider_charges, insurer_waiting | estimate, plan, encounter |
| countable_assets | spending_since_statement (method), household_protection, retirement_protection, plan_reserve, living_reserve | 4 / 1 | household_protection, retirement_protection | encounter, claim, plan |
| hardship_cap | household_points, income_loss_points, fixed_income_points, coverage_points, burden_share (parameter), savings_increment (method) | 5 / 1 | household_points, fixed_income_points, coverage_points, burden_share, savings_increment | plan, claim, encounter |
| renewal | renewal_selfpay_basis (method) + 3 parameter | 3 / 1 | renewal_appeal_holdout, renewal_coverage_gap | encounter, claim |
| response_window | period_reach (method), outside_bills_days, plan_pause_days, treatment_days, appeal_days, account_count_days | 5 / 1 | outside_bills_days, appeal_days | encounter, plan, claim |

- Every ladder has three tiers, stated in the rule (condition and value/method), implemented in `decides`, fall-through = baseline; bindings disjoint; no `decides: result`. XF A.1 mechanical follow: no factor binding reads another factor's binding (shared plain bindings: appeal_claim/appeal_open, sp_net, ct_liab, std_cap).
- XF C.14 all-pairs for method factors: selfpay_basis (min-pick vs AGB share vs net: distinguishing input sp_net < sp_agb; adjustment rows) PASS structurally; anticipated_care (line sum vs header total vs 0: different fields) PASS structurally (label borderline, O2); spending_since_statement (floor added; payments input) PASS; savings_increment PASS; period_reach FAIL (F1).
- Realism judgements: F1–F5 below. Observations: insurer_waiting tier 2 uses Riverbend's AGB share of gross charges as the expected patient share of an insured pending account (O3); retirement/disability protections give disabled patients half the retiree amount (O4).

### findings
Each: verdict — symptom → root cause → evidence → demonstrated consequence → affected artifact/location. Tasks it bears on in brackets.

**C1 SOURCE-POLICY RED (undeclared override, debt window and incurred-debt definition)** [task 0; task 1 no scored consequence]
- Base: assist_tier_determination "medical hardship applies only when qualifying_medical_debt_usd incurred in the last hardship_debt_window_months exceeds hardship_medical_debt_income_pct of annual household income"; parameter_schema "hardship_debt_window_months: integer months before the application date over which qualifying medical debt (Riverbend and outside medical bills) is counted"; schema qualifying_medical_debt_usd "documented medical bills (Riverbend and outside) incurred in the hardship debt window".
- Extended (overwrite [] in all three): qualifying_debt "Older balances are the part of the patient's current Riverbend balances … that exceeds the liabilities less adjustments of the twelve whole months before the documentation day"; "Care already scheduled and priced on the most recent estimate is added"; "A Riverbend self-pay package the patient is paying for in advance is added"; "A recurring course of care already planned is added … when its scheduled first visit is after the documentation day"; supplement/renewal "every patient liability posted … in the twelve whole months before the signing day". Framing "adding the Riverbend medical costs that its own records show" while it also adds co-provider (not Riverbend) charges.
- Members: older_add, sched_add, pkg_add, course_add (debt not incurred in the window); supplement/renewal/QD window anchor (signing/documentation day vs application date).
- Consequence (demonstrated in 0.md): two defensible qualifying-debt figures and two caps.

**C2 SOURCE-POLICY RED (undeclared override, asset test)** [task 0]
- Base sentences quoted above (asset limit, ASSETS_ABOVE_LIMIT, liquid-asset definition). Extended countable_assets: "records on the case the countable liquid assets the asset test compares with liquid_asset_limit_usd … then every protected amount is taken off". Consequence (0.md): base reading denies, extended approves.

**C3 SOURCE-POLICY RED (undeclared override, renewal FPL percent)** [task 1, not on scored path]
- renewal rule "the renewal opens a new case … on the household figures documented on the expiring award (its household size, annual household income, household percent, liquid assets and tier)" vs base fpl_guideline_basis "IN_EFFECT_ON_APPLICATION_DATE" and schema "computed … on the application date". Task 1 seed: renewal case application 2025-11-14 carries 487.3 (2024 HHS 2-person guideline $20,440); the 2025 guideline ($21,150) gives 99,600/21,150 = 470.9.

**C4 SOURCE-POLICY RED (rule clause without compute, field the records lack; second reading)** [task 0]
- countable_assets "This schedule took effect on 2025-10-01; liquid assets recorded on a case before that date stand as documented." No binding implements it; assistance_cases holds no recording date for liquid_assets_usd. Reading A: the countable recording itself is the "recording" (applies to writes on/after 10-01). Reading B: a case whose liquid assets were recorded (documented) before 10-01 keeps them as documented. Consequence in 0.md.

**C5 SOURCE-POLICY RED (rule self-contradiction, spending window)** [task 0]
- "the Riverbend payments made since it, which are the patient payments posted on the patient's Riverbend accounts no more whole months before the recording day than the bank statement's acceptance date". "Since it" excludes payments before the acceptance date; the whole-month definition includes them when they share the acceptance date's whole-month distance. Consequence in 0.md.

**C6 SOURCE-POLICY RED (rule/compute, document status)** [charter only]
- response_window rule "When no outside medical bills have been received on the renewal case …"; compute `outside_none: COUNT(… document_type='OUTSIDE_MEDICAL_BILLS') == 0` (no status filter). On a renewal case carrying only a REQUESTED (or REJECTED) OUTSIDE_MEDICAL_BILLS row the rule adds outside_days/outside_days_far, the compute adds 0. Not reached in task 1 (no such row).

**C7 SOURCE-POLICY RED (edge inputs, XF B.6/B.7)** [charter only]
- qualifying_debt `rc_started` on an issued recurring-course GFE with empty scheduled_service_date: rule → "otherwise nothing is added for a recurring course"; compute → DAYS(None, NOW) raises. `pend_est` (several insured out-of-pocket estimates tied to the pending account) and `pkg_id` (several issued packages of one variant) take the first row in file order; the rule states no pick. Not reached in task 0.

**C8 SOURCE-POLICY RED (whole-month / month-end convention, XF B.8)** [charter only; no boundary posting in either world]
- Read sites: supplement and renewal (same-day convention stated, month-end not: a posting on the 31st against a 30-day signing month); qualifying_debt window_net ("fewer than twelve whole months separate", no whole-month definition); countable_assets paid_since; hardship_cap ct_recent / billed_recent / paid_recent and its overwrite's "twelve months before the application date"; response_window accounts ("twelve whole months before the notice date"). Compute uses MONTHS() (day-of-month comparison, month-end falls back a month).

**C9 SOURCE-POLICY RED (assembly sentences naming factor quantities, XF A.3)** [charter]
- supplement/renewal "the claim is the standard figure with its self-pay part replaced as stated, its coverage-terminated part replaced as stated, and every held-out amount taken off"; countable_assets "first brought forward to the recording day as the spending adjustment states, then every protected amount is taken off"; hardship_cap "the percentage points taken off are subtracted … first …, the kept share is then applied …, and the asset increment is added last"; response_window "the standard figure with its base days replaced as the application-period adjustment states, plus every added day count".

**C10 SOURCE-POLICY RED (one convention sentence serving several factors, XF A.4)** [charter]
- hardship_cap "A posting belongs to a span of whole months when fewer than that many whole months separate its posting date from the approval day." used by coverage_points (12 and 3 months) and burden_share (12 months).

**C11 SOURCE-POLICY RED (dependency restated in the depended-on rules)** [task 0 tree]
- qualifying_debt "Before a Medical Hardship determination, Riverbend documents …"; countable_assets "Before a Medical Hardship determination, Riverbend records …". The cap's own sentences already state both edges; the depended-on rules state the order a second time from the depended-on side, so the hop is given rather than derived.

**C12 SOURCE-POLICY RED (prerequisite sentence broader than its condition)** [charter]
- Sentence "the patient's signed claim of medical debt"; condition "the debt claimed on the patient's signed hardship supplement"; resolved_by sign_hardship_supplement_15cad132, which the supplement rule forbids on renewals. On a complete renewal case with no outside bills accepted (inside QD's scope) the sentence is satisfied by the renewal claim; the declared edge names a write that cannot run there.

**C13 SOURCE-POLICY RED (framing asserts a state no record holds, XF B.12)** [task 1]
- response_window "Days are added while a payment plan is paused for the pending renewal: when the patient's active Riverbend payment plan is …". payment_plans has no pause field or status; the tiers test only the tier. Consequence in 1.md (the seeded plan shows an installment drawn after the renewal was filed).

**F1 SOURCE-FACTOR RED (period_reach is one formula; response_window has no real method factor)** [task 1]
- Tier 1 "days left" (age ≤ notification_period_days, so days left ≥ 120); tier 2 "the larger of missing_information_response_days and the days left"; tier 3 (age > application_period_days, or none) missing_information_response_days. On tier 1's whole domain max(30, days left) = days left; on tier 3's domain days left < 0 so max(30, days left) = 30. All three tiers are max(30, 240 − age): the 120-day and 240-day boundaries select nothing. Struck, response_window keeps 5 parameter factors and 0 method.

**F2 SOURCE-FACTOR RED (plan_reserve condition no FAP weighs)** [task 0]
- countable_assets "when that plan pays by automatic payment (ACH or card), reserve_autopay_months monthly installments are protected; when it has no automatic payment, reserve_manual_months monthly installment is protected". The household's committed installments are the same whatever the payment channel; no hospital asset test protects three times as much for autopay. Struck, countable_assets keeps 4 factors (3 parameter, 1 method).

**F3 SOURCE-FACTOR RED (coprovider_charges tier 2 outcome)** [charter]
- "when an outside medical bills document has been received on the case but not accepted, the amounts-generally-billed share of those lines, agb_pct percent … is added". agb_pct is Riverbend's own AGB (501(r)(5) limit on the facility's charges); the base says co-provider charges "are billed by those groups and are outside the award" (assist_agg_award_coverage). No business values another group's bill at its own AGB because a document is unaccepted.

**F4 SOURCE-FACTOR RED (income_loss_points conditions)** [charter; task 0 takes the Hardship tier]
- "Income-loss points are taken off for an income loss shown by the patient's active Riverbend payment plan: … Riverbend Hardship Payment Plan … Riverbend Assistance-Linked Payment Plan …". plan charter: Assistance-Linked applies when "the patient holds a financial assistance award in approved status at a partial-discount tier" (no income loss); Hardship applies on income loss "or when the enrolled total exceeds hardship_balance_threshold_usd". The tier conditions do not show what the rule says they show.

**F5 SOURCE-FACTOR RED (selfpay_basis / renewal_selfpay_basis patient-wide elective condition)** [task 0 tier 2 rests on it; task 1 tier 1]
- "when no package price adjustment was posted in those months and the patient holds no account coded elective, it enters at that amounts-generally-billed share …; otherwise it enters as the self-pay part". Elective status governs whether that account's own charges are AGB-limited; one elective account anywhere (even closed, outside the window) switching every emergency and medically necessary self-pay liability to as-posted is not a treatment any 501(r) hospital publishes. Struck, supplement and renewal keep 3 factors and 0 method (below the 4 and 1 floors).

**Observations**: O1 QD→supplement action-form fallback unjustified (state form available). O2 anticipated_care `method` label borderline (tiers pick a different source amount for the same addition). O3 insurer_waiting tier 2. O4 retirement/disability amounts. O5 QD→supplement `effect` "instead of 0.00" is a world fact.

## closing_checklist
Written after both reveals (2026-10-20 14:24:44 UTC); the section above is unchanged since its pre-reveal hash b8d727895ddde05f.
- Task files 0.md and 1.md correspond one-to-one with tasks/0.json and tasks/1.json; both comparison sections are written; neither is PASS (task 0 RED, task 1 RED).
- Coverage and scope: charter_scope of task 0 = {supplement, qualifying_debt, countable_assets, hardship_cap}, task 1 = {renewal_debt_claim, response_window}. Disjoint, jointly complete; each task tool appears in exactly one scope; uuid8s independent (PASS).
- Trees: task 0 has 3 prerequisite problems, 3 value_input edges, one owner=user write; task 1 has 1 prerequisite, 1 value_input edge, one owner=user write; the difficulty's graph is acyclic (PASS).
- Factors: every declared factor bears weight on its world, and every computation's all-baseline number is definite and differs from gold (PASS). Not met: F1 (response_window left with 0 method factors), F5 (supplement and renewal left with 3 factors and 0 method), F2–F4 unreal tiers; seeded-row defects S0-1, S1-1, S1-2.
- Policy self-consistency not met: C1–C13 open.
- Instantiation-stage gates: not re-run by this auditor (the brief forbids it); difficulty not closed.
- GT agreement: every scored value in both tasks equals the auditor's frozen derivation under the instantiator's reading. The REDs are second readings, undeclared overrides, structural ladder defects and seed rows, not arithmetic.

VERDICT revision_1: task0=RED task1=RED charter=C1,C2,C3,C4,C5,C6,C7,C8,C9,C10,C11,C12,C13,F1,F2,F3,F4,F5

## revision_2

## charter_global_frozen (revision_2)
- Time: 2026-10-20 21:50 UTC. Auditor: erl-task-policy-audit subagent (same auditor as revision_1).
- Hashes: assist.extended.yaml cd63513d55afa03c (changed → every charter-global section re-derived); task_tools.py 1bc59c84c3f80208 (unchanged → `action_binding_and_uuids` of revision_1 carried forward by reference on that hash); views r2/0 8175afa479293074, r2/1 d3c5dd05f94c2fc8 (match the brief). Gate snapshot taken as entry evidence, not re-run.
- **Not blind**: the reworker's worklog (gold values included) was read before this derivation, as the coordinator allowed. Replaced factors and re-seeded rows were still derived from the rule text and records (own evaluator over the charter compute plus hand checks) before tasks/*.json was opened.
- Base copy: still dict-equal to blueprint/products/assist.yaml. Mechanical sweeps: every compute_basis quote, baseline sentence, policy_source and replaced_by is a substring of its rule; every compute binding has a basis; prerequisite gates exist (claimed, debt_keep, asset_raise, outside_add); 31 distinct factor ids, none inside a tool name; no factor binding reads another factor's binding (XF A.1, mechanical AST walk).

### round-1 items, one by one
| id | round-2 state | evidence |
|---|---|---|
| C1 | closed at the policy layer; residual moved to C15 | QD overwrite of assist_tier_determination's debt clause, scoped to the supplement, renewal-claim and documentation schedules; replaced_by restates the base for every other application and is carried verbatim in the QD rule. The supplement and renewal keep `overwrite: []`, but their counting is named in that scope (O9). |
| C2 | closed at the policy layer; residual moved to C15 | countable_assets overwrite of "where liquid_asset_test_applies is true, liquid assets do not exceed liquid_asset_limit_usd", scoped, with documented assets restated for every other application. |
| C3 | closed | renewal rule: "the household percent recomputed against the HHS poverty guideline in force on the renewal's application date"; task 1 seed shows 470.9 = 99,600 / 21,150. |
| C4 | closed | "This schedule governs a recording made on or after schedule_effective_date (2025-10-01); a recording made before that date recorded the documented liquid assets" plus `on_schedule` binding on the recording day; the second reading is gone. |
| C5 | closed | "the payments of the statement's span … (so a payment dated earlier than the acceptance date in that same whole-month span is included)". |
| C6 | closed | RW `outside_none` and QD `outside_rcv` filter document_status RECEIVED; rule says "logged as received". |
| C7 | closed | course_planned: "including when no first visit is scheduled on it" + `rc_dated` guard; package and co-provider picks within a variant: "listed first"; pend_est removed. |
| C8 | closed | Every whole-month read site states "a whole month running from a day of one month to the same day of the next month or, when the next month has no such day, to the first day of the month after it". Checked against MONTHS() on month-end pairs (01-31→03-01 = 1; 01-31→02-28 = 0; 03-31→04-30 = 0; 10-31→10-31+12 = 12): agree. |
| C9 | closed | Generic assembly sentences in all six rules (e.g. cap: "every reduction of the cap percent applies first …, the scaling of the annual household income at the resulting percent applies next …, and every addition applies last"). |
| C10 | closed | Cap coverage points and kept share each carry their own convention sentence. |
| C11 | closed | "Before a Medical Hardship determination" removed from QD and countable_assets. |
| C12 | closed as RED; residual O7 | QD edge is now state form ("documented only once the case records a medical debt the patient claims (a case showing 0.00 records none)"); condition matches. Residual: on a complete renewal case the renewal claim brings the state about but `resolved_by` names only the supplement. Per case, the records select exactly one writer, so the reader's hop is unique → observation. |
| C13 | closed | plan factor removed from RW; replaced by pending_claim_days (claim status submitted/accepted, record-visible). |
| F1 | closed | period_reach tier 1 = days left + 30 (differs from tier 2 on its own domain: 270 − age vs 240 − age); tier 2 = max(30, days left); tier 3 = 30 (tier 2 coincides only on the age > 240 part of tier 3's domain, not on "no first statement"). C14 structural test: PASS. |
| F2 | closed | plan_reserve keyed on remaining balance vs three installments; autopay no longer read. |
| F3 | closed | coprovider_procedure: co-provider lines without AGB; issued procedure → Riverbend's convening lines. |
| F4 | closed | plan_burden_points: installment as a percent of monthly income (record-visible burden). |
| F5 | closed | selfpay_basis removed; the method factor is now hold_holdout (min of disputed-line charge and held liabilities / coinsurance sum / none: adds an input and a min, PASS). Counts: supplement and renewal each 4 factors (1 method, 3 parameter). |
| O1/O5 | closed (state form; effect worded generally) | |
| O2 | open observation (anticipated_care method label borderline; C14 structural test passes) | |
| O3/O4/O6 | O3 removed; O4 amounts re-set (5,000/2,500); O6 kept (claim charter allows) | |

### new checks on replaced material (XF all points, every policy)
- gfe_dispute / renewal_gfe_dispute (parameter): No Surprises Act figures real ($400 ppdr_threshold_usd, 120 ppdr_initiation_days, estimate charter); billed = self-pay final bill less uninsured discount, expected = convening lines (matches estimate_ppdr_eligibility). Edge inputs stated (no initial bill date → 0). PASS.
- appeal_overdue (QD, parameter): 60 days = federal post-service internal appeal decision time (real); 45 is labelled Riverbend's own. Age counted from the day after filing (DAYS) as stated. PASS.
- hold_holdout (method): disputed line via the latest CHARGE_DISPUTE inquiry on the held account (tie and absent-line rules stated; compute agrees). PASS.
- pending_claim_days, plan_burden_points, plan_reserve, protections: plausible Riverbend schedules. PASS.
- Ladders: ≥3 disjoint tiers each, fall-through = baseline, stated in rule and compute. Counts: supplement 4 (1M), QD 6 (1M), countable assets 5 (1M), cap 6 (1M), renewal 4 (1M), RW 6 (1M). Multi-source and cross-difficulty present per task.

### findings (revision_2, open)
**C14 SOURCE-POLICY RED (XF D.17, rule defers to a clause its own overwrite retires)** [charter only]
- QD overwrite replaces the base debt test "for an application whose qualifying medical debt is recorded under Riverbend's hardship schedules (claimed on a hardship supplement or on a renewal's claim of medical debt, or documented under this schedule)" with "the qualifying medical debt recorded on the case, counted as those schedules state". The QD rule also says "A case with an outside medical bills document accepted is documented under the base rule."
- Take a case whose debt was claimed on a hardship supplement and which then has OUTSIDE_MEDICAL_BILLS accepted. It is in the overwrite's scope (claimed on a supplement), yet it is documented under the base rule, whose debt clause is the one retired for that scope. Reading A: the test uses the schedule-counted figure. Reading B: base documentation and the base "incurred in the last hardship_debt_window_months before the application date" test. No task world reaches this.

**C15 SOURCE-POLICY RED (XF E.24, frozen field meanings)** [task 0]
- db_schema `assistance_cases.qualifying_medical_debt_usd`: "documented medical bills (Riverbend and outside) incurred in the hardship debt window; 0.00 when not claimed". QD writes into it amounts that are not incurred or not in any window: sched_add (care scheduled 2025-11-04), pkg_add (package for 2025-11-12), course_add (course from 2025-11-03), coprovider_procedure tier 2 (procedure not yet rendered), older_add ("balances older than twelve months").
- db_schema `liquid_assets_usd`: "documented liquid assets; 0.00 when not tested". record_countable_assets writes the countable figure (documented less protections).
- The overwrites change the policy's test, not the frozen field meaning. Members: QD sched_add, pkg_add, course_add, cp_add tier 2, older_add; countable_assets result. This residual was part of round-1 C1/C2 evidence (schema quoted) and was not itemized separately then.

**F6 SOURCE-FACTOR RED (AGB valuation applied regardless of the account's classification)** [task 1]
- supplement coverage_gap and renewal_coverage_gap tier 2: "the part of them above their amounts-generally-billed share … is taken off" for every coverage-terminated liability. The AGB limit (501(r)(5)) and Riverbend's award cover only EMERGENCY / MEDICALLY_NECESSARY care (base `elective_excluded`; encounter charter gives elective care its own, smaller uninsured discount). Valuing an ELECTIVE_NON_COVERED account's debt at AGB is a treatment no 501(r) hospital publishes. This is the same per-account principle as round-1 F5, which was removed in one place but not in this one.
- Class members: coverage_gap (supplement) tier 2; renewal_coverage_gap tier 2; course_planned tier 2 (AGB share of a future course, no classification test; not demonstrable, the GFE carries no classification).

**Observations**: O2 (kept); O7 (QD state-form edge, renewal-case writer undeclared in resolved_by); O8 (task 0 member appeal pending 61 days against the claim charter's payer_appeal_decision_days 60 for Marketplace; the appeal_overdue tier rests on a payer one day late); O9 (the supplement/renewal counting departure is declared in QD's overwrite, not in their own `overwrite: []`; merged semantics unique).

## closing_checklist (revision_2)
- Task files carry revision_2; GT values of both tasks equal this round's derivation (see task files).
- Scopes unchanged and disjoint/complete; tool module unchanged (uuid8s PASS by reference); trees hold in both tasks; the difficulty's graph is acyclic.
- Every factor bears weight; every all-baseline figure is definite and differs from gold.
- Not met: C14, C15, F6 open. Difficulty not closed. Gates not re-run by this auditor.

VERDICT revision_2: task0=RED task1=RED charter=C14,C15,F6

## revision_3

## charter_global_frozen (revision_3)
- Time: 2026-10-21. Auditor: same. Hashes: assist.extended.yaml 9a5726f2c6ccb885; task_tools.py 4ad29d37c893210d (both changed → every charter-global section re-derived, including tools/uuids); views r3/0 0d267daf1aedf2a1, r3/1 cb296501263e8dc5 (match the brief). Gate snapshot taken as entry evidence, not re-run.
- **Not blind**: worklog (gold values, coordinator rulings) read first. All six policies and both worlds were still derived from rule text and records (own evaluator over the charter compute plus hand checks) before tasks/*.json was opened.
- Base copy dict-equal to blueprint. Mechanical sweeps: every compute_basis quote, baseline sentence, policy_source and replaced_by is in its rule; every binding has a basis; gates exist (claimed, documented, debt_keep, outside_add); 31 distinct factor ids, none inside a tool name; transitive factor-reads-factor walk finds none (XF A.1).
- Tools: record_countable_assets removed. New record_documented_costs_4c71e2b9 (agent; plain ctx.update of qualifying_medical_debt_usd; uuid8 distinct, not derived from a sibling). No clock/random imports; no ordering words. O13: its docstring "completes … the documentation" describes a position after another documentation step (the cap's own prerequisite sentence carries the same order).

### structure (round 3)
| policy | tool | factors (M = method) | prerequisite |
|---|---|---|---|
| supplement | sign_hardship_supplement (user) | appeal_holdout, hold_holdout M, coverage_gap, gfe_dispute | [] |
| qualifying_debt (own charges) | record_qualifying_debt | selfpay_basis M, gfe_account_basis, gfe_undisputed, unbilled_selfpay, package_rendered, course_in_progress | supplement (state) |
| other_costs_debt (new) | record_documented_costs | rendered_care M, insured_pending, coprovider_rendered, appeal_overdue, hold_restore | qualifying_debt (action, fallback justified: same field) |
| hardship_cap | approve_hardship_award | household, plan_burden, fixed_income, coverage, burden_share, savings_increment M | other_costs_debt (action, fallback justified) |
| renewal_debt_claim | sign_renewal_debt_claim (user) | 4 (hold M) | [] |
| response_window | send_missing_information_notice | 6 (period_reach M) | renewal (state) |
Graph acyclic. Prerequisite sentences pass the four-point test; single reading each. Depended-on rules do not restate the order.

### round-2 items
| id | state | evidence |
|---|---|---|
| C14 | closed | QD overwrite scope excludes cases with outside bills accepted; rule and replaced_by restate the in-force content for them ("the documented medical bills, Riverbend and outside, incurred in the last hardship_debt_window_months before the application date"). The cap completeness parenthetical points to its own restated clause. |
| C15 | closed, with one member left (F7 below) | countable-assets write removed; base asset test applies to documented assets; cap rule reads "documented liquid assets". Each qualifying-debt write stores in-window medical bills at the FAP charge basis (coordinator ruling): claimed liabilities less set-asides; own charges revalued at AGB only for emergency/medically necessary care; rendered-but-unbilled care; rendered package; course visits given; rendered single service; co-provider charges of a rendered procedure; overdue-appeal cost sharing; restored hold amounts. Sources are self-limiting in time (pending or recently completed records). |
| F6 | closed under the coordinator's route | coverage_gap / renewal_coverage_gap value at AGB only when the designated coverage-gap account is not elective; other accounts stand as posted. O10 records the residual (the BadgerCare tier also takes off only the designated account's liabilities). |
| O7, O8, O9 | carried as observations | |

### XF sweep on the new and changed material (all six policies)
- A.3 generic assembly: PASS in all six. A.1: PASS. A.5: PASS.
- **A.4 FAIL (C16)**: one convention sentence serves several factors.
  - QD: "For these adjustments, a posting belongs to those months when fewer than twelve whole months separate …; an account's self-pay bill is …; an account's unbilled charges are …; and an amounts-generally-billed share is agb_pct percent of the amount it is taken of, rounded half-up to the cent". It is used by selfpay_basis, gfe_account_basis, gfe_undisputed, unbilled_selfpay and course_in_progress.
  - other_costs: "For these additions, a posting belongs to those months …; an account's unbilled charges are …; and an amounts-generally-billed share is …". It is used by rendered_care, insured_pending, appeal_overdue and hold_restore.
  - This is the same class closed in round 2 for the cap (C10).
- **B.7 / rule–compute FAIL (C17)**:
  - QD ga_id. Rule: "self-pay good faith estimate whose service has been completed or which is closed (… within one variant the estimate listed first among the patient's estimates)". Compute takes every service_completed estimate of a variant before any closed one, regardless of listing order.
  - other_costs cp_id. Rule: "has its service completed or is in dispute (the estimate listed first when several are)". Compute takes service_completed before in_dispute.
  - other_costs ip_est. Rule: "when an insured patient out-of-pocket estimate is tied to the pending insured account, that estimate's total". No pick is stated for several; compute takes the first in file order. This is a recurrence of round-1 C7 (pend_est).
  - Neither world exercises any of these (one candidate each).
- B.6, B.8, B.9, B.10, B.11, B.12: PASS, except O12. other_costs framing lists "amounts set aside whose reason has ended", but the overdue-appeal addition is an amount whose reason has not ended (the appeal is undecided).
- C.14 method pairs: rendered_care (min of lines and AGB of unbilled charges / lines / none) PASS; selfpay_basis (min-pick / AGB share / as posted, on the designated account) PASS; others unchanged PASS.
- D: overwrites scoped, restated, no rule deferring to a retired clause. PASS. Two completeness notions coexist (O14): QD's "complete for this schedule", and the base/cap completeness that other_costs' "complete" leaves undefined. Same answer in both worlds.
- E.24 (field meanings): PASS except F7.
- F.25 seeded rows: S3-1 (task 0) and S3-2 (task 1) in task files.
- Realism (every new tier): AGB for emergency/medically necessary unbilled care, elective discount for elective, package price with the real cesarean upgrade differential, GFE-lines caps, NSA dispute figures, the ACA 60-day appeal decision time — all plausible. Failures: F7, F8.

### findings (revision_3, open)
**C16 SOURCE-POLICY RED (XF A.4)** — members as listed above (QD sentence serving 5 factors; other_costs sentence serving 4). Charter only.

**C17 SOURCE-POLICY RED (XF B.7, pick order/multi-match)** — members: QD ga_id, other_costs cp_id, other_costs ip_est. On a world where a variant holds a closed estimate listed before a completed one, the rule picks the closed one and the compute picks the completed one. Charter only.

**F7 SOURCE-FACTOR RED (insured_pending tier 2, unreal value and field meaning)** — "when none is tied to it and the account is coded emergency or medically necessary, the amounts-generally-billed share of its gross charges is added". AGB is the amount generally allowed (payer plus patient) for the care. Adding it for an insured account awaiting the payer counts the insurer's expected payment as the patient's medical bill, contrary to the frozen meaning of qualifying_medical_debt_usd and to what a hardship policy counts. Round-1 O3 is now in breach of the coordinator's binding field-meaning ruling. Not taken in task 0 (tier 1, insured estimate tied).

**F8 SOURCE-FACTOR RED (hold_restore tier 2 condition unreachable under the encounter charter)** — "when the held account is on a charge-dispute hold and the most recent charge-dispute inquiry on it … has been resolved with no change". Encounter charter encounter_billing_hold: "The hold is released when its reason is resolved …; release resets billing_hold_reason to NONE". A resolved dispute leaves no charge-dispute hold, so the tier selects nothing in any charter-consistent world; it is reached only through the seed defect S3-1 (task 0).

**Observations**: O7, O8 (task 0 appeal pending day 61 of 60, kept), O9, O10, O12, O13, O14.

## closing_checklist (revision_3)
- GT of both tasks equals this round's derivation figure for figure (task files). Scopes disjoint and complete (task 0: supplement, QD, other_costs, cap; task 1: renewal, window). Trees hold: task 0 has 3 prerequisites, 3 value_input edges and a user write; task 1 has 1, 1 and a user write. Every factor bears weight on its world.
- Not met: C16, C17, F7, F8 (charter); S3-1, S3-2 (seed rows). Difficulty not closed; gates not re-run by this auditor.

VERDICT revision_3: task0=RED task1=RED charter=C16,C17,F7,F8

## revision_4

## charter_global_frozen (revision_4)
- 2026-10-21. Gated entry: worklog tail reads `REWORK round 4: gates 7/7 green`.
- Snapshot run as instructed (`/tmp/erl0073_coord/snapshot.sh financial_assistance_screening 4`, executed only, no other contact):
  - views r4/0 befd3ba52a5f6675 and r4/1 02df780e659368fa (same masking)
  - gates 2026-10-21T06:47:29: EXTENDED OK / TASK TOOL CONTRACT OK / REPLAY OK / SOLVABILITY OK / COMPUTE OK / GROUNDING OK / SCOPE OK
  - sha256 assist.extended.yaml 96e77a673343, task_tools.py 912186a017e8, tasks/0.json e5e3be2a7c8c, tasks/1.json bf27cbd4cf3e
  - Entry conditions met.
- **Not blind**: worklog round-4 section (gold values, seed table) read first. Both worlds were still re-derived from rules and records before tasks/*.json was opened.
- Mechanical sweeps (all six policies):
  - basis quotes, baseline sentences, policy_source and replaced_by are all in their rules;
  - every binding has a basis; gates exist (claimed, documented, debt_keep, outside_add);
  - the transitive A.1 walk finds no violation;
  - 31 distinct factor ids, none inside a tool name;
  - task_tools.py has no ordering words; record_documented_costs' docstring no longer says "completes".

### round-3 items
| id | state | evidence |
|---|---|---|
| C16 | closed | No shared "For these adjustments/additions" sentence remains. QD's three windowed factors each carry their own whole-month sentence; rendered_care, appeal_overdue and hold_restore state their own unbilled-charges, rounding and window conventions. |
| C17 | closed | QD ga_id: "within one variant, an estimate whose service has been completed before a closed one; … listed first" (= compute order). cp_id: "completed before one in dispute and, among several of the same status, the estimate listed first". ip_est and sg_id: "listed first … when several are". gu_id, rc_id, pk_id and cs_id are stated. |
| F7 | closed | insured_pending tier 2 is now the point-of-service payments on the pending insured account (cost sharing collected), "never at amounts the payer is expected to pay". Real and field-meaning-consistent. |
| F8 | closed | hold_restore tier 2 is re-cut to an open charge-dispute hold on a SELF_PAY account: it adds back the uninsured-discount part of the disputed line, MN(line, held liabilities) × discounts / self-pay final bill. This matches the encounter charter (CHARGE_CORRECTION_ADJUSTMENT = credit less the discount already granted) and is reachable. Re-seated tier realism: PASS. |
| S3-1 | closed | E7 is now an ITEMIZATION_REVIEW hold (10-06, 30 days), request IN_REVIEW, itemized statement 10-09 (≤ 5 business days); line ec218082 recoded (82565, no duplicate). |
| S3-2 | closed as stated (see O15) | the coverage-gap account's PR-27 is now day 17 of 30; NH 61b6437f re-dated to day 27. |
| O12, O13, O14 | closed | other_costs framing; docstring; a single completeness meaning (the schedules gate on three named accepted documents). |
| O7–O10 | answered, kept as observations | |

### XF sweep (A1–F27, all six policies)
- A: PASS. B (6, 7, 8, 9, 10, 11, 12, 13): PASS. C.14 method pairs unchanged: PASS. D (overwrites scoped, restated, no deferral to a retired clause): PASS. E (tools, uuid8s, schema meanings): PASS.
- F (seeded rows): my own exhaustive pass over every cross-category row in both worlds.
  - Claims: allowed = expected_allowed_pct × charges where no appeal applies (58.5% Anthem, 47.5% Marketplace, 52% Quartz/NH); clean-claim days ≤ 30; PR-27 class corrections.
  - Accounts and discounts: uninsured discounts (50/45/50; elective imaging 25); bill-hold days; statement cycles stopping at plan enrollment or hold.
  - Plans: installment re-pricing; the BALANCE_WITHDRAWN_FOR_DISPUTE reduction leaves the installment unchanged (plan charter).
  - Estimates: totals = lines; insured estimate 207.10 = 20% × 47.5% × 2,180 after the met deductible; GFE issuance timing; package deposit 100%.
  - The reworker's table holds except for the two members below.

### findings (revision_4)
No charter-level RED is open. Two seeded-row members remain (task files):
- **S4-1 (task 0)**: claim d9335c73 is in appealed status with MEMBER_APPEAL_WITH_AOR (0035045c, 2025-08-21), but it now has no denial (denial_date cleared, carc NONE, no denial line on the remit) and no underpayment (allowed 4,674.00 = 47.5% × 9,840 expected). Claim charter lifecycle: adjudicated → appealed only when "Billing files an underpayment or partial-denial appeal". claim_appeal_windows counts every appeal "from the denial notice date". The appealed state is not reachable.
- **S4-2 (task 1)**: the expiring award's application row e7b0d5bd for E4 keeps charge_basis/fap_liability 289.60. E4's posted patient responsibility is now 75.00 + 292.84 = 367.84, and the base assist_charity_computation sets the insured charge basis to "the total patient responsibility posted from the payer". The worklog's "text updated" did not reach the row.
- Observation O15 (task 1): the Quartz coverage that paid E4 (service 10-20) is shown terminated before 10-28 (E6 PR-27), while the 11-09 ED claim is billed to Quartz and accepted, and the persona says "the same jobs". The timeline is possible (front-end acceptance does not verify eligibility), but the termination is unexplained.
- O8 kept (now resting on an appeal that S4-1 shows has no basis).

## closing_checklist (revision_4)
- GT of both tasks equals this round's derivation figure for figure; scopes disjoint and complete; trees hold (task 0: 3 prerequisites / 3 value_input / user write; task 1: 1 / 1 / user write); every factor bears weight; all-baseline figures definite and different from gold.
- Charter clean of open REDs. Not met: S4-1, S4-2 (seed rows). Difficulty not closed.

VERDICT revision_4: task0=RED task1=RED charter=CLEAN

## revision_5

## charter_global_frozen (revision_5)
- 2026-10-21. Gated entry: worklog tail `REWORK round 5: gates 7/7 green`.
- Snapshot (`/tmp/erl0073_coord/snapshot.sh financial_assistance_screening 5`, executed only):
  - views r5/0 ac71640ba1c6c1ce and r5/1 bf22a0ba5b7c8aed (same masking);
  - gates 2026-10-21T19:18:46: EXTENDED OK / TASK TOOL CONTRACT OK / REPLAY OK / SOLVABILITY OK / COMPUTE OK / GROUNDING OK / SCOPE OK;
  - sha256 assist.extended.yaml 96e77a673343, task_tools.py 912186a017e8, tasks/0.json 13d57dfb31da, tasks/1.json 90acac465eb2.
- **Charter and tools are byte-identical to revision_4** (96e77a673343190e / 912186a017e80672). The revision_4 charter-global sections, mechanical sweeps and XF sweep carry forward by reference on those hashes, except for the latent defect F9 below, which this round's re-seed exercises for the first time.
- **Not blind**: the worklog round-5 section was read first; both worlds were re-derived before tasks/*.json was opened.

### round-4 items
| id | state | evidence |
|---|---|---|
| S4-1 | closed | d9335c73 remit is now allowed 4,424.00 (854.40 paid + 3,000 PR-1 + 569.60 PR-2; CO-45 5,416.00; sums to 9,840), 250.00 / 5.35% below the expected 47.5% × 9,840 = 4,674.00. That is ≥ underpayment_variance_usd 25 and ≥ 2%, so the claim charter routes it to UNDERPAYMENT_APPEAL. Filed 2025-08-28 (day 8 of the 180-day Marketplace provider window); adjudicated → appealed is now a charter transition. Encounter coinsurance 569.60, balance 3,569.60; the AOR is removed (no member appeal). |
| S4-2 | closed | award row e7b0d5bd 367.84 = posted copay 75.00 + coinsurance 292.84 (insured charge basis); cap use 5,816.74 ≤ 9,960. |
| O8 | settled | no appeal in either world is past the payer's 60-day decision time (task 0 day 54, task 1 day 55). |
| O15 | settled | Records now give a consistent coverage timeline: Network Health covers the Jan visit; PR-27 on the May 14 visit; Quartz pays the Jun 10 and Oct 20 claims; PR-27 on the Oct 28 visit; the Nov 9 ED claim is billed to Security Health Plan (new member/group IDs) and accepted. This is consistent with the persona's "same jobs" (employer changed carrier). |

### findings (revision_5)
**F9 SOURCE-FACTOR RED (appeal_overdue tier 2: "overdue" before the payer's decision time)** [task 0; latent since revision_2, first exercised now]
- Rule (assist_ext_other_costs_debt): "Cost sharing held under an overdue insurer appeal is added: … when it is of any other type, its claim is the claim under appeal, and more than other_appeal_review_days have passed in the same count, only the coinsurance liabilities of the appeal window posted from that claim are added". other_appeal_review_days = 45.
- Owning claim charter, claim_appeal_windows: "The payer decides a post-service appeal within payer_appeal_decision_days" — 60 for every commercial and Marketplace class, and the charter makes no exception for provider-level appeals.
- Tier 2 therefore declares an insurer appeal "overdue", and puts its held cost sharing back into the patient's debt, while the payer is still inside its own decision time. That is a fact no record holds (XF B.12), and a treatment no hospital would publish under its own payer-contract timelines.
- Task 0: the underpayment appeal 0035045c is on day 54 of 60. Tier 2 adds 569.60 (other-costs figure 29,523.58); under the claim charter the appeal is not overdue, the tier falls through, and the figure is 28,953.98 (= the factor's baseline). The cap stays 8,514.60 (burden 25.67%, still above 25).
- Class members: appeal_overdue tier 2 only. Tier 1 uses the real 60-day federal time and the payer's 60 days, so it agrees.
- I missed this in revisions 2–4 because no world reached tier 2; it is recorded now, not raised as a regression.

**Observation O17 (task 0)**: the gold read find_claim_appeal_authorizations now returns nothing and decides nothing; appeal_type on the claim activity alone selects the tier.

## closing_checklist (revision_5)
- GT of both tasks equals this round's derivation figure for figure; scopes, trees and factor weights hold; seeded rows touched this round all conform to their owning charters.
- Open: F9 (charter; task 0). Task 1 has no open item.

VERDICT revision_5: task0=RED task1=PASS charter=F9

## revision_6

## charter_global_frozen (revision_6)
- 2026-10-21. Gated entry: worklog tail `REWORK round 6: gates 7/7 green`.
- Snapshot (`/tmp/erl0073_coord/snapshot.sh financial_assistance_screening 6`, executed only):
  - views r6/0 ac71640ba1c6c1ce and r6/1 bf22a0ba5b7c8aed — identical to r5, so both worlds are unchanged;
  - gates 2026-10-21T19:55:51: EXTENDED OK / TASK TOOL CONTRACT OK / REPLAY OK / SOLVABILITY OK / COMPUTE OK / GROUNDING OK / SCOPE OK;
  - sha256 assist.extended.yaml dc3a9282dc38 (changed), task_tools.py 912186a017e8 (unchanged), tasks/0.json a3facb85d52b (changed), tasks/1.json 90acac465eb2 (unchanged).
- Not blind: worklog round-6 section read first.
- Charter change scope: I kept no byte copy of the round-5 charter (a copy of this round's is now kept at /tmp/pta_fas_audit/assist.extended.r6.yaml for later rounds). The claim that only other_costs changed was therefore checked by behaviour, not by diff:
  - all six policies re-swept mechanically (basis quotes, baseline sentences, policy_source, A.1 walk, K params declared and used, factor ids vs tool names: all clean);
  - every policy's gold, all-baseline and per-factor sensitivity on both worlds recomputed: every figure identical to revision_5.

### round-5 items
| id | state | evidence |
|---|---|---|
| F9 | closed | appeal_overdue → appeal_held_share. Tier 1: a member appeal past "its payer's decision time for a post-service appeal (payer_appeal_decision_days of that claim's payer class under the claim charter)", read through CPARAM, so the payer's own 60 (BadgerCare 30) is used and no invented figure remains. Tier 2: an underpayment appeal or recoupment dispute, with no date test and no "overdue" wording. Tier 3: nothing. No tier calls an appeal overdue inside the payer's decision time. The Riverbend-own 45-day parameter is gone. |
| O17 | closed | find_claim_appeal_authorizations dropped from task-0 gold; steps renumbered 14 / 16 / 18 / 20 (= call indices). |

### XF sweep, touched policy (assist_ext_other_costs_debt)
- A.1–A.5: PASS. The tier-1 payer time is read from the claim charter's parameter (a record/parameter test, not "as another policy figures it").
- B.6: PASS (appeal_due and appeal_age read only when appealed). B.7: same-day appeal tie unchanged. B.8: the appeal window carries its own whole-month sentence. B.9: PASS. B.11: quotes in the rule. B.12: every read field is listed (claim variant_name added); see O18.
- B.13: tiers disjoint (member past time / underpayment or recoupment / else) and distinct in value (D + C + copay / C / 0).
- C: parameter factor; no method pair changed.
- D: no overwrite touched. E: tools unchanged; "appeal_held_share" is not inside any tool name. F: no seeded row changed.
- Realism of the re-seated factor: tier 1 is the ACA deemed-exhaustion situation at the payer's real decision time. Tier 2 counts the posted coinsurance as owed, the minimum the patient owes under any outcome of a payment-only dispute. Real, and it bears weight on task 0 (29,523.58 vs baseline 28,953.98) with no payer-late date (day 54 of 60).

### observations (revision_6)
- **O18 (wording, no scored consequence)**: tier 2's reason clause "the patient's share standing as posted whatever the payer decides" overstates the case. Coinsurance is a share of the allowed amount, so an underpayment win raises it (task 0 at the expected 4,674.00 allowed: 40% × 1,674 = 669.60 against the posted 569.60). The posted amount is a floor the patient owes in every outcome, so the added figure is right and no second reading changes it. Renderers will carry the clause verbatim.
- O7, O9, O10 carried.

## closing_checklist (revision_6)
- Per-task audit files 0.md and 1.md correspond one-to-one to the tasks, revisions 1–6 kept, and both revision_6 comparison sections are PASS.
- Coverage and scope: the six extended policies are covered once each (task 0: supplement, qualifying debt, other costs, cap; task 1: renewal claim, response window). Scopes are disjoint across whole trees. Task tools and GT are closed. uuid8s are independent and frozen (15cad132, da5f54be, 4c71e2b9, afb08b0b, 3b9e07c1, 7f5665e5).
- Trees:
  - task 0: 3 prerequisite problems, 3 value_input edges, the supplement is owner=user, acyclic;
  - task 1: 1 prerequisite, 1 value_input edge, the renewal claim is owner=user;
  - the whole graph is a DAG.
- Factors: every computation has a self-sufficient baseline and 4–6 factors (≥ 2 parameter, 1 method). Per task there is ≥ 1 multi-source and ≥ 1 cross-difficulty factor. Ladders have ≥ 3 distinct tiers stated in the rule and are realistic. Every factor bears weight on its world, and every all-baseline figure is definite and differs from gold.
- Seeded cross-category rows conform to their owning charters (exhaustive pass revision_4, touched rows re-checked revisions 5–6).
- Instantiation-stage gates on the final form: 7/7 OK per the coordinator snapshot of 2026-10-21T19:55:51 (not re-run by this auditor, per brief).
- Policy self-consistency PASS + problem tree PASS + factors PASS + unique solution PASS for both tasks: the difficulty passes the source-layer audit.

VERDICT revision_6: task0=PASS task1=PASS charter=CLEAN

## revision_7

## charter_global_frozen (revision_7)
- 2026-10-21. Gated entry: worklog tail `REWORK round 7: gates 7/7 green`.
- Snapshot (`/tmp/erl0073_coord/snapshot.sh financial_assistance_screening 7`, executed only):
  - views r7/0 ac71640ba1c6c1ce and r7/1 bf22a0ba5b7c8aed (= r5/r6; worlds unchanged);
  - gates 2026-10-21T20:21:55: EXTENDED OK / TASK TOOL CONTRACT OK / REPLAY OK / SOLVABILITY OK / COMPUTE OK / GROUNDING OK / SCOPE OK;
  - sha256 assist.extended.yaml 4fcb4279cb2d (changed); task_tools.py 912186a017e8, tasks/0.json a3facb85d52b, tasks/1.json 90acac465eb2 (all byte-identical to revision_6).
- Not blind (worklog read first).
- **Diff against my round-6 copy** (/tmp/pta_fas_audit/assist.extended.r6.yaml, parsed compare):
  - every base key and every extended key other than `rule` and `compute_basis` is identical (compute, factors, ladders, params, prerequisite, overwrite, inputs, cross_category);
  - the changed basis quotes are exactly those of the edited sentences (supplement and renewal ct_off / has_bcp; QD ub_free; other_costs appeal_add).
  - Round-7 copy kept at /tmp/pta_fas_audit/assist.extended.r7.yaml.

### text changes, each checked
| policy | old → new | judgement |
|---|---|---|
| other_costs appeal tier 2 (O18) | "the patient's share standing as posted whatever the payer decides" → "the posted coinsurance being the least the patient owes in any outcome, since an underpayment appeal can only raise the allowed amount the coinsurance is a share of and a recoupment dispute concerns only the payer's takeback" | true. An underpayment appeal never lowers the allowed amount. The claim charter: "A takeback never changes what the patient owes unless the payer re-adjudicates the claim with different patient-responsibility lines". O18 closed. |
| other_costs appeal lead | "added back where the appeal can no longer keep it from the patient" → "added back as follows" | removes an overstatement for tier 1; neutral. |
| supplement / renewal BadgerCare tier | ", those dates being billed to BadgerCare Plus" removed | removes an unsupported assertion; the tier condition (a BadgerCare Plus claim held) is unchanged. |
| QD awaiting self-pay account | ", that care being documented under its estimate" removed | removes a statement that was false for an issued, not completed, single-service estimate. |

- Re-sweep: every compute_basis quote, baseline sentence and policy_source is a substring of its rule in all six policies. No task file quotes a removed clause.
- Recompute on both worlds: every gold value, all-baseline figure and per-factor sensitivity is identical to revision_6 (task 0: 17,559.32 / 26,839.10 / 29,523.58 / 8,514.60; task 1: 6,254.58 / 155).
- The reworker's framing sweep agrees with my reading of the kept clauses. No XF point is affected; text-only changes touch no compute, assembly order, convention sentence or field meaning.

## closing_checklist (revision_7)
The revision_6 checklist carries forward unchanged: tools, tasks and worlds are byte-identical, the charter changed only in reason/participle text, and the gates are 7/7 per the coordinator snapshot of 2026-10-21T20:21:55. Open items: none. Observations O7, O9, O10 carried.

VERDICT revision_7: task0=PASS task1=PASS charter=CLEAN

## revision_8

## charter_global_frozen (revision_8)
- 2026-10-21. Gated entry: worklog tail `REWORK round 8: gates 7/7 green`.
- Snapshot (`/tmp/erl0073_coord/snapshot.sh financial_assistance_screening 8`, executed only):
  - views r8/0 ac71640ba1c6c1ce and r8/1 bf22a0ba5b7c8aed (worlds unchanged since r5);
  - gates 2026-10-21T21:22:38: EXTENDED OK / TASK TOOL CONTRACT OK / REPLAY OK / SOLVABILITY OK / COMPUTE OK / GROUNDING OK / SCOPE OK;
  - sha256 assist.extended.yaml a7a6daa29443, task_tools.py fe7e3790cf06, tasks/0.json a25ab75056a6, tasks/1.json 13af0ec7e77c (all changed).
- Not blind: worklog round-8 section and audits/render_source/financial_assistance_screening/render_r1.md read first.
- Parsed diff against my round-7 copy:
  - base keys identical; response_window unchanged.
  - supplement and renewal: hold selections moved into the hold factor's bindings; the appeal sentence moved ahead of the held-account sentence.
  - QD: rule, compute (sp_delta, new sp_gfe), bindings and ladder changed.
  - other_costs: rule, basis and hold_restore bindings/ladder changed.
  - hardship_cap: rule and basis only.
  - Copies of the round-8 charter and tools kept at /tmp/pta_fas_audit/assist.extended.r8.yaml and task_tools.r8.py.

### honest note on items I had passed
All four renderer items were present in material I passed:
- **Item 1** (held-account selection used by one factor): since revision_2. I classed held_acct as an A.2 shared selection without checking that only one factor reads it.
- **Item 2** (cap order and rounding): since revision_2. I read "the scaling … rounded" as covering the kept share and did not test it against `RND(income*cap_pct/100*debt_keep, 2)`.
- **Item 3**: the QD exclusion naming other factors since revision_3, the other-costs "claim held out" framing since revision_3. My A.1 walk was mechanical and passed because ga_acct and gu_acct were plain bindings; I did not apply A.4/A.5 to the wording.
- **Item 4** (notice tool missing the Medicaid notice flag): since revision_2, when the renewal tier became percent-pointed. I checked the tool only against the hardship tier the task uses.

### round-8 items (render_r1 1–4), each with its class swept over all six policies
| item | state | evidence |
|---|---|---|
| 1 | closed | supplement, renewal and other_costs: dispute_acct, review_acct and held_acct are now bindings of hold_holdout, renewal_hold_holdout and hold_restore; the "The held account is …" sentence sits directly before each hold sentence. **Class sweep** (my own walk of every plain binding to the factors that read it, transitively): the only plain bindings left are standard-figure or gate bindings read by `result` (liab_all, adj_all, std_claim, claimed, income_doc, complete, documented, income, std_pct, std_cap, cap_pct, on_schedule), the shared appeal selection read by two factors per policy (appeal_claim and appeal_open, A.2), and response_window base_days. base_days is the standard figure (baseline sentence) and period_reach's fall-through value. No member remains. |
| 2 | closed | Cap order sentence: "every reduction of the cap percent applies first …; the annual household income is then scaled at the resulting percent and every kept share is applied to that scaled figure, the product being rounded half-up to the cent; every addition applies last, and the cap is rounded …". This equals `RND(MX(0, RND(income*cap_pct/100*debt_keep,2) + asset_raise - std_cap), 2)`. Kept-share tiers: "heavy_keep of the scaled figure is kept … the whole scaled figure is kept". **Class sweep (order/rounding vs compute)**: supplement, renewal, QD, other_costs and window match their compute. |
| 3 | closed | QD selfpay_basis states its own record test: "When a self-pay good faith estimate … whose service has been completed, which is closed or which is in dispute is linked to the self-pay account, its bill stands as posted". sp_gfe is 9 exact CFIELD tests matching the wording, and the ladder's tier 3 names the case. ga_id/ga_acct and gu_id/gu_acct moved into their only factors. Other costs: "adding medical costs that Riverbend's records show: … cost sharing posted from a claim under appeal, and cost sharing posted on an account on a billing hold"; the appeal and hold sentences now read "Cost sharing posted from/on … is added as follows"; no sentence refers to another policy's claim. **Class sweep**: no rule sentence names another factor or another policy's figure (A.4/A.5). Transitive A.1 walk clean. |
| 4 | closed | send_missing_information_notice_7f5665e5 gains `medicaid_notice_request` (REQUESTED / NOT_REQUESTED, one enum per field). Its docstring has no example values and no ordering words, and the body logs MEDICAID_DETERMINATION_NOTICE like the other four. Every document type of every percent-pointed tier is now requestable. **Class sweep (rule-required writes vs tool capability)**: approve (cap, dates, letter language), the three debt writers and the renewal claim are all expressible. |

### other checks
- Recompute on both worlds: every gold value, all-baseline figure and per-factor sensitivity is identical to revision_7 (task 0: 17,559.32 / 26,839.10 / 29,523.58 / 8,514.60; task 1: 6,254.58 / 155).
- Gold: task 1's notice call adds `medicaid_notice_request: NOT_REQUESTED`. That is correct: Medical Hardship does not require the notice, and one is already accepted on the renewal case (1a5228f5). Task 0 and task 1 GT match my derivation item for item, with computation steps at the call indices.
- Mechanical sweeps: compute_basis quotes, baseline sentences and policy_source are present in all six rules.

### observations (revision_8)
- **O19**: the cap order sentence now names "every kept share" alongside "every reduction of the cap percent" and "every addition". I read all three as kind-level words fixing a non-commuting order (XF A.3 allows this), not as naming one factor's figure. Renderer to confirm.
- **O20**: the other-costs additions (appeal and hold cost sharing) are net-correct only because the claim schedules before it take off the same amounts under the same conditions (supplement/renewal take-offs ⊇ other-costs additions, checked tier by tier). After item 3 the rule no longer says so; it is self-contained and computes the scored figure exactly.
- **O21**: the selfpay_basis exclusion (any completed, closed or disputed self-pay GFE linked) can leave a medically necessary account linked to a non-selected GFE at its posted bill. This is the designated-account route the coordinator accepted; neither world reaches it.
- **O22**: tasks/0.json other-costs factor_trace still says "28.70 added back" where the rule now says "added". Proof text only; no figure affected.
- O7, O9, O10 carried.

## closing_checklist (revision_8)
Revision_6's checklist holds on the round-8 form: scope, trees, factors (counts unchanged, all bearing weight), seeded rows unchanged since revision_5, uuid8s unchanged (the notice tool kept its name). The tool-contract change is clean. Gates 7/7 per the coordinator snapshot of 2026-10-21T21:22:38. Open items: none.

VERDICT revision_8: task0=PASS task1=PASS charter=CLEAN

## revision_9

## charter_global_frozen (revision_9)
- 2026-10-22. Gated entry: worklog tail `REWORK round 9: gates 7/7 green`.
- Snapshot (`/tmp/erl0073_coord/snapshot.sh financial_assistance_screening 9`, executed only):
  - views r9/0 ac71640ba1c6c1ce and r9/1 bf22a0ba5b7c8aed (worlds unchanged);
  - gates 2026-10-22T00:09:16: EXTENDED OK / TASK TOOL CONTRACT OK / REPLAY OK / SOLVABILITY OK / COMPUTE OK / GROUNDING OK / SCOPE OK;
  - sha256 assist.extended.yaml b0470d6bbda6 (changed); task_tools.py fe7e3790cf06, tasks/0.json a25ab75056a6, tasks/1.json 13af0ec7e77c (byte-identical to round 8; tools also confirmed with cmp against my copy).
- Read: worklog round-9 section; the src-1 line of audits/policy_kb/financial_assistance_screening/_difficulty.md only (audits/runtime_context/ not opened); published docs/estimate, docs/claim, docs/plan and docs/encounter, to check meanings. Not blind.
- Parsed diff against /tmp/pta_fas_audit/assist.extended.r8.yaml:
  - only assist_ext_qualifying_debt changed: package_rendered gains binding pk_price; pk_add reads pk_price instead of estimate_total_usd; its reads list now has primary_service_code and service_code; one rule sentence extended with the package-price definition;
  - the other five policies and all base keys are identical.
  - Round-9 copy kept at assist.extended.r9.yaml.

### src-1
- Old: the rendered package added `estimate_total_usd`, the sum of all lines. On an Outpatient Surgery package with co-provider lines, those lines were added here and again by other_costs coprovider_rendered (tier 2, "the co-provider lines of its current version").
- New rule: "its package price is the sum of the Riverbend facility line and the Riverbend professional line that carry the principal service code on its current version, co-provider lines not being part of it". Compute pk_price = CONVENING_FACILITY + CONVENING_PROFESSIONAL lines with service_code = primary_service_code on the current version. Rule and compute agree.
- Published meaning (docs/estimate): "The surgical package price is the sum of the Riverbend facility line and the Riverbend professional line that carry the package's principal service code on the current version of the estimate; co-provider lines, implant lines and every other line of that version are not part of it"; the delivery package is defined in the same terms. Matches.
- Double count gone: co-provider lines of a surgery package are now added only by other_costs.
- **src-1 closed.** I had passed this in revisions 3–8: I read "package price" as the estimate total and did not check other_costs tier 2 against it.

### class sweep: meanings of other products' figures, all six policies, against the published docs
| figure read | where | published meaning | result |
|---|---|---|---|
| GFE expected charges / "Riverbend lines" = convening facility + professional lines of the current version | supplement/renewal gfe; QD gfe_account_basis, gfe_undisputed, course_in_progress; other_costs rendered_care | docs/estimate: "its expected charges are the sum of the Riverbend facility and Riverbend professional lines of that version" | match |
| GFE billed charges = self-pay final bill less uninsured discount | supplement/renewal gfe_dispute | docs/estimate: "Riverbend's billed charges are the self-pay final bill less the uninsured discount" | match |
| insured estimate total (patient's expected share) | other_costs insured_pending | docs/estimate: the estimate total is the sum of the version's lines; an insured estimate's lines are the patient's expected cost sharing | match |
| co-provider lines (anesthesia/pathology/radiology roles) | other_costs coprovider_rendered | docs/estimate co-provider roles | match |
| package price, upgrade differential | QD package_rendered | as above; differential = CPARAM of the tier | match (fixed this round) |
| payer post-service appeal decision days; underpayment / recoupment meaning | other_costs appeal_held_share; supplement/renewal appeal factors | docs/claim: "The payer decides a post-service appeal within the payer appeal decision period" (table: 60; BadgerCare 30); "A takeback never changes what the patient owes unless the payer re-adjudicates …" | match |
| plan installment | cap plan_burden_points | docs/plan: installment = financed amount over the term, recomputed on add-ons (monthly_payment_usd) | match |
| uninsured / elective discount percent, self-pay final bill, PACKAGE_PRICE_ADJUSTMENT, point-of-service payment | QD; other_costs | docs/encounter, including `POINT_OF_SERVICE` "when the patient pays in person at a Riverbend registration or cashier desk" | match |

No other member found.

### other checks
- Mechanical: compute_basis quotes present; every binding has a basis; transitive A.1 walk clean, all six policies.
- Recompute on both worlds: every gold value, all-baseline figure and per-factor sensitivity is identical to revision_8. Task 0's rendered package is the Imaging & Diagnostics package with one facility line of 895.00 on 72148, so pk_price = 895.00 = its total and gold does not move. Task JSON proof text ("package price 895.00 added") stays true.

### observations (revision_9)
- **O23**: the worklog says "the claim docs are unpublished, so the claim charter was used". docs/claim holds 76 published docs; the two claim meanings the charter relies on (appeal decision period, takeback) match them.
- **O24**: as the worklog notes, the rendered assist doc that states "The package price is the estimate's total" now trails the source and needs a re-render.
- O7, O9, O10, O19–O22 carried.

## closing_checklist (revision_9)
Revision_8's checklist holds: tools, tasks and worlds are byte-identical; the single charter change is rule/compute-equivalent and leaves every figure unchanged; gates 7/7 per the snapshot of 2026-10-22T00:09:16. Open items: none.

VERDICT revision_9: task0=PASS task1=PASS charter=CLEAN

## revision_10

## charter_global_frozen (revision_10)
- 2026-10-22. Gated entry: worklog tail `REWORK round 10: gates 7/7 green`. My earlier reply this round was BLOCKED because the tail was then a status line; the coordinator confirmed that reply.
- Snapshot (`/tmp/erl0073_coord/snapshot.sh financial_assistance_screening 10`, executed only):
  - views r10/0 dba85fb4203346a8 and r10/1 2cac1fa2cce847dc (both worlds changed);
  - gates 2026-10-22T02:21:46: EXTENDED OK / TASK TOOL CONTRACT OK / REPLAY OK / SOLVABILITY OK / COMPUTE OK / GROUNDING OK / SCOPE OK;
  - sha256 assist.extended.yaml c644a3689d3f (changed under the coordinator's route (a)), task_tools.py fe7e3790cf06 (unchanged), tasks/0.json d96e60e38d78, tasks/1.json 4747b19b3ade.
- Read: worklog round-10 sections; src-2..src-5 lines and xcheck_r3_encounter.md of audits/policy_kb/financial_assistance_screening (audits/runtime_context/ not opened); docs/encounter (observation-rate, day-count, length-of-stay, campus, carve-out, coverage-loss, other-losses, size bands, hardship allowance, coverage-terminated posting). **Not blind.**
- Parsed diff against /tmp/pta_fas_audit/assist.extended.r9.yaml. The base, cap and response window are unchanged. Changed:
  - supplement and renewal coverage gap: new ct_disc; ct_off on the net balance;
  - QD: selfpay_basis becomes a parameter on the net bill, sp_pkg removed; gfe_account_basis becomes the method, a min-pick of three;
  - other_costs hold_restore: the discount rate is read from the most recent self-pay final bill (dispute_fb).
  - Round-10 copy kept at assist.extended.r10.yaml.

### src items
- **src-2 / src-3 (owed encounter writes)**: seeded as posted on their own dates. My recomputation from docs/encounter:
  - T0 8bdb031d coverage-terminated discount 168.00 on 03-27: clinic 40%; others 0, size < 2500, no hardship denial; before the 04-01 statement.
  - T0 c88c4cb6 observation-rate discount 920.00 on 07-02: 0762 charges 4,840.00; plain day difference 06-26 → 06-28 = 2 (22 h ≤ 48, so the day-count clause keeps 2); day rate 1,250 + 250 (Appleton with a 0450 line); length of stay < 24 h → none; no 0350/0480 lines; (4,840 − 3,000) × 0.5 = 920.00 ≥ floor 242.00; before the 07-05 statement.
  - T1 15c52208 coverage-terminated discount 236.00 on 06-13: elective 20%; no other PR-27 existed on that date.
  - T1 bd2c77fb coverage-terminated discount 352.75 on 11-17: 40% + 2.5 for the PR-27 on 61b6437f = 42.5% of 830.00.
  - Derived plan rows and balances recompute exactly. T0 installments: 178.00 = 10,679.88/60; 193.93 = 11,247.88/58; 482.17 = 27,483.95/57; plan balance 13,119.61; E0 913.61. T1: 67.07 = 3,018.13/45; 140.63 = 6,187.56/44; plan balance 5,765.67; E0 1,585.17.
  - **No encounter write is owed at either opening**: every coverage-terminated account carries its discount before its first statement (so no service-recovery courtesy is owed); the only self-pay observation stay carries its observation-rate discount; there is no non-covered liability, full payoff or small balance.
  - **Closed.**
- **src-4**: the September MRI is re-coded 72141 (not on the Imaging & Diagnostics package schedule), so the single-service GFE type is correct. Figures unchanged. **Closed.**
- **src-5**: 03633924 is issued 2025-04-10, 1 business day after the 04-09 scheduling (service 8 business days ahead). **Closed.**
- Realism note O25: the T0 observation stay was re-dated to span 06-26 → 06-28 with 22 observation hours (worklog: "so selfpay_basis keeps bearing weight"). The stay is producible (ED level line 0450, observation following ED time), and the discount follows the published day-count rule. Recorded as engineered but legitimate.

### route (a) rule change, checked
- Coverage gap (supplement, renewal): rule "the part of that balance above the amounts-generally-billed share of those liabilities … nothing coming off a balance already at or below that share" = `MX(0, ct_liab − ct_disc − RND(ct_liab×agb))`. BadgerCare tier = `ct_liab − ct_disc`. This is real under 501(r)(5) and agrees with compute. T0 106.68 (252.00 − 145.32); T1 190.07 (477.25 − 287.18).
- QD: no tier raises a bill. selfpay is the min of bill and AGB; gfe_account_basis is MN(bill, lines, AGB) for emergency/medically necessary and MN(lines, bill) for elective; gfe_undisputed adds MN(expected, AGB) or expected, both below the billed amount whenever an estimate is in dispute (PPDR needs billed − expected ≥ 400). C.14 for gfe_account_basis: T1 vs T2 adds the AGB input (this world 581.28 vs 924.00); T2 vs T3 differ whenever the lines are below the bill. PASS.
- hold_restore: rate = discount sourced to the most recent self-pay final bill ÷ that bill (the observation-rate discount, sourced to a 0762 line, is excluded). This matches the encounter charge-correction rule. A same-day second final bill on one account cannot arise (late charges post after the final bill), so no tie rule is needed.
- XF sweep on the four touched policies:
  - A.1 (transitive walk), A.3, A.4 (each window and bill convention stated per factor), A.5: PASS.
  - B.6, B.8, B.9, B.10, B.11, B.12: PASS. C.14: PASS. D, E: PASS.
  - **Failures: F11, C18 below.**
- Factor weight (T1: baseline substituted on the task world; T2: a producible world off the taken tier). All factors bear weight:
  - T0 supplement: 17,208.92 / 16,668.02 / 16,746.00 / 30,039.32.
  - T0 QD: 27,135.70 / 27,181.82 / 17,566.30 / 26,531.10 / 25,944.10 / 26,475.80.
  - T0 other costs and cap: as revision_9.
  - T1 renewal: 6,755.08 / 6,311.42 / 6,208.65 / 8,358.58.
  - T1 window: unchanged.

### findings (revision_10)
**F11 SOURCE-FACTOR RED (selfpay_basis: two tiers select the same value)** [task 0; introduced this round]
- Ladder and rule: tier 2 "coded emergency or medically necessary and its bill is at or below its amounts-generally-billed share → the bill as posted"; tier 3 "otherwise (coded elective, linked to a … self-pay estimate, or no self-pay bill) → the bill as posted". Compute: `… else (0 if (… != 'ELECTIVE_NON_COVERED') else 0)`, the same 0 on both branches.
- The ladder has two outcomes: MN(bill, AGB) for emergency/medically necessary, the bill otherwise. That is one tier written as two, below the three-distinct-tier floor.
- QD keeps 5 other factors (method gfe_account_basis, 4 parameters), so the computation floors still hold once it is struck.

**C18 SOURCE-POLICY RED (coverage_gap / renewal_coverage_gap: ladder face not updated to the rule)** [tasks 0 and 1]
- Rule and compute now take off the net balance (liabilities less every uninsured discount on the coverage-gap account): tier 1 "all of that balance", tier 2 "the part of that balance above the amounts-generally-billed share of those liabilities".
- The `factors[].ladder` face still reads tier 1 "the coverage-gap account's coverage-terminated liabilities of the twelve months, taken off" and tier 2 "the part of those liabilities above their amounts-generally-billed share".
- Check 2 requires each ladder tier to state what the rule and the decides binding select. Here the faces disagree on the same world:
  - T0: rule 106.68 vs ladder face 274.68 (supplement 16,639.32 vs 16,471.32);
  - T1: rule 190.07 vs ladder face 542.82 (renewal claim 6,018.58 vs 5,665.83).
- Members: supplement coverage_gap tiers 1–2; renewal renewal_coverage_gap tiers 1–2.

**Observations**: O25 (above); O7, O9, O10, O19–O24 carried.

## closing_checklist (revision_10)
- GT equals my derivation in both worlds:
  - T0 16,639.32 / 26,839.10 / 29,523.58 / 8,514.60 (skips 10,199.78 / 19,323.80 / 9,276.00); dates and language unchanged.
  - T1 6,018.58 / 155.
- Trees hold. Seeded rows conform. No encounter write is owed.
- Open: F11, C18. Difficulty not closed.

VERDICT revision_10: task0=RED task1=RED charter=F11,C18

## revision_11

## charter_global_frozen (revision_11)
- 2026-10-22. Gated entry: worklog tail `REWORK round 11: gates 7/7 green`.
- Snapshot (`/tmp/erl0073_coord/snapshot.sh financial_assistance_screening 11`, executed only):
  - views r11/0 dba85fb4203346a8 and r11/1 2cac1fa2cce847dc (= r10; worlds unchanged);
  - gates 2026-10-22T02:30:06: EXTENDED OK / TASK TOOL CONTRACT OK / REPLAY OK / SOLVABILITY OK / COMPUTE OK / GROUNDING OK / SCOPE OK;
  - sha256 assist.extended.yaml 1e8fc606d8d2 (changed), task_tools.py fe7e3790cf06, tasks/0.json 30cee9510668 (text only), tasks/1.json 4747b19b3ade (unchanged).
- Not blind (worklog read first).
- Parsed diff against /tmp/pta_fas_audit/assist.extended.r10.yaml. Base, cap and response window unchanged. Changed:
  - supplement and renewal: coverage-gap ladder text only;
  - other_costs: hold_restore ladder text only;
  - QD: selfpay_basis re-cut, with new bindings ins_claim, ins_acct, ins_ok, ins_share and ins_agb, a new rule sentence for the insured account, and claim added to cross_category.
  - Round-11 copy kept at assist.extended.r11.yaml.

### round-10 items
| id | state | evidence |
|---|---|---|
| F11 | closed | selfpay_basis now has three distinct outcomes. T1: the self-pay account is coded emergency/MN with no completed, closed or disputed self-pay GFE linked → MN(bill, AGB) in place of the bill. T2: no self-pay account so qualifies, and the insured account qualifies (the account of the claim with the latest payer payment, tie = first listed; claim not appealed, account not held, coded emergency/MN) → MN(patient share of the window from that claim, AGB of gross charges). T3: nothing. Compute `sp_delta` = exactly these branches. Real under 501(r)(5): for an insured FAP-eligible patient, the amount charged is the amount personally owed, capped at AGB. T1 on task 0: baseline 27,135.70 ≠ 26,839.10. T2 producible world (my probe: E3 recoded elective) selects tier 2 on the E8 account: share 40.00 ≤ AGB 98.61, so 0 change on this world; the reworker's 200.00-share probe moves it by 101.39. QD floors: 6 factors, 5 parameter + 1 method (gfe_account_basis). |
| C18 | closed | coverage_gap / renewal_coverage_gap ladder tiers now name "the coverage-terminated balance (its coverage-terminated liabilities … less every uninsured discount … on that account)" and "the part of that balance above the amounts-generally-billed share … of those liabilities, … nothing when the balance is at or below that share". These equal `ct_off`. |

### ladder-vs-compute sweep (my own pass, all 31 factors, all six policies)
Each ladder tier was read against its `decides` expression (dump at /tmp/pta_fas_audit/ladders_r11.txt):
- supplement: appeal_holdout, hold_holdout, coverage_gap, gfe_dispute;
- QD: selfpay_basis, gfe_account_basis, gfe_undisputed, unbilled_selfpay, package_rendered, course_in_progress;
- other_costs: rendered_care, insured_pending, coprovider_rendered ("rendered" = service_completed or in_dispute, as the rule says), appeal_held_share, hold_restore (the T2 rate now worded as compute's dispute_fb);
- cap: all six;
- renewal: all four;
- response window: all six.

Every tier states the condition and value or method its branch implements, and no two tiers share a value. No member remains.

### other checks
- Mechanical: compute_basis quotes in rules; every binding has a basis; transitive A.1 walk clean; one method factor per computation; counts 4 / 6 / 5 / 6 / 4 / 6.
- XF on the touched QD policy:
  - A.4: the insured account's window, share and AGB conventions are stated once, for selfpay_basis only.
  - B.6: no payer payment → no insured account → T3.
  - B.7: payment tie stated (XLATEST first).
  - B.9: share = all liabilities posted from that claim in the window.
  - B.12, E.24: PASS.
  - Overlap: appealed claims and held accounts are excluded, so T2 never meets a supplement take-off; a claim with a payer payment carries no PR-27, so it never meets the coverage gap.
- Recompute on both worlds: every gold value, all-baseline figure and per-factor sensitivity is identical to revision_10. tasks/0.json and tasks/1.json GT match.

### observations (revision_11)
- **O27 (for the coordinator)**: selfpay_basis T2 values the insured account at AGB only "when no self-pay account so qualifies". Whether one account receives the 501(r)(5) limitation thus depends on whether another account qualifies. That is the per-account principle behind round-1 F5. I take it as within the coordinator's designated-account route (one account, picked by exact record test). If that ruling does not extend to a cross-account fallback, this is an F5-class member. Neither world exercises T2 with a share above AGB.
- O7, O9, O10, O19–O25 carried.

## closing_checklist (revision_11)
Revision_8's checklist holds on the round-11 form:
- scope, trees (T0 3/3/user, T1 1/1/user), factor floors and weights, seeded rows (unchanged since revision_10, no encounter write owed);
- gates 7/7 per the snapshot of 2026-10-22T02:30:06.

Open items: none.

VERDICT revision_11: task0=PASS task1=PASS charter=CLEAN
