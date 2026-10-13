# Policy-task audit — comp_dependents_claims_and_payments / charter-global

## charter_global_frozen

- Auditor: independent policy-task auditor (Claude agent, erl-task-policy-audit), not the instantiating agent.
- Freeze time: 2026-10-06T03:40Z (written before any task's GT was revealed; nothing in this section is derived from a revealed GT).
- Frozen inputs (sha256, re-checked against the orchestrator's MANIFEST.sha256.txt; both match):
  - `tasks/comp_dependents_claims_and_payments/comp.extended.yaml` 0e4bfa4717e41d59d3a8a34df1e80105e9721d7fd0de18815253257c43612d70
  - `tasks/comp_dependents_claims_and_payments/task_tools.py` f9f5b6f44384e2d8281d50060589ca5010bb86b98d1771b3cd31a88970d4e94b
- Read for this section: `blueprint/blueprint.yaml` (difficulty block), `blueprint/db_schema.json`, `blueprint/share_tools.py`, `blueprint/products/comp.yaml`, the cross-category charters `blueprint/products/pension.yaml` and `appeal.yaml` (only the fields the charter's cross reads name), the extended charter and the tool module, and the DSL evaluator `skills/erl-task-instantiate/scripts/check_compute.py` (MONTHS/DAYS/LATEST/within_months semantics).
- Masked and unread: every `tasks/*.json` field other than the masked views' `frozen_time`, `user_scenario`, `initial_state`; `worklog.md`; any prior audit.
- Entry conditions (Step 0): gate snapshot present at `/tmp/erl0038/views/policy_task/comp_dependents_claims_and_payments/GATES.txt` — EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, CACHE-DIFF INFO, SCOPE OK; traceability deferred to the KB step. Masked views and MANIFEST present; view hashes 7b047823… (task 0) and 1ddb70fc… (task 1) re-checked. Input complete.
- Base section: `diff` of lines 1-1508 of the extended charter against `blueprint/products/comp.yaml` differs only by one trailing blank line — the base copy is verbatim.

### policy_conflict_scan

Seven extended policies, seven distinct target tools, all `computes: gross_amount`:

| policy | target_tool (owner) | prerequisite edges |
| --- | --- | --- |
| comp_ext_returned_payment_replacement | request_payment_replacement_543b1fec (user) | [] |
| comp_ext_dependency_past_due | release_dependency_past_due_602dcd04 (agent) | [] |
| comp_ext_decision_past_due | release_decision_past_due_fbf191c5 (agent) | -> dependency_past_due (value_input, action) |
| comp_ext_pension_switch_past_due | release_switch_past_due_a8e85818 (agent) | -> replacement (value_input, state); -> dependency_past_due (value_input, action); -> decision_past_due (value_input, state) |
| comp_ext_suspension_release | resume_award_release_withheld_86166e35 (user) | [] |
| comp_ext_temporary_total_past_due | release_temporary_total_past_due_0acb107c (agent) | [] |
| comp_ext_review_restoration | release_review_restoration_92058ca9 (agent) | -> suspension_release (value_input, state); -> temporary_total_past_due (value_input, state) |

- The graph has exactly two weakly connected components: {switch, replacement, dependency, decision} and {restoration, suspension, temporary_total}. With M=2 these are the only two scopes possible; they are disjoint and jointly cover all seven policies. Which task carries which is confirmed per task from its world, not from GT.
- Overlapping subjects: five policies book `comp_retro_payment` and two policies (replacement, suspension release) touch the months of payments that came back. The interactions are stated in the rules and are coherent: the replacement rule excludes "a payment whose month a release made when a suspension ended has already paid"; the resumption months count "the payments that came back less those replaced"; the dependency release subtracts "one for each monthly payment that came back"; the decision, switch and restoration releases subtract "every replacement and ... every past-due release already on the award". No two policies claim the same (tool, quantity).
- Withholding boundary: decision, switch, suspension, temporary total and restoration scope themselves to "no direct-pay fee agreement" / "no debt in active collection"; the dependency release instead says "with nothing withheld for a fee or a debt" unconditionally (see override_declarations F-B1).
- Cross-category reads: switch reads pension (`pension_awards.termination_reason`, `pension_payments` gross/date); restoration reads appeal (`decision_reviews` outcome/received_date/prior_review_id, appeal variant `filing_window_days` = 365 for every lane). Both are declared in `cross_category` and in `inputs`.
- Base cross-problem orders that ground no declared edge (findings F-C1, F-C2 below): `comp_evt_rating_change` "Past-due benefits on a suspended award are computed but released only when the award resumes." (orders any past-due release after a resumption) and `comp_evt_payment_return` "... is reissued only after the payment account or mailing address on the award has been updated" (orders a reissue after a payment-profile update).
- Owner boundary vs the scenario constitution: `blueprint.yaml` difficulty summary says "Recording ... a reissue or a resumption is the representative's service action on a verified caller", while this charter makes both owner=user ("the replacement is requested by the veteran personally"; "A suspended award resumes once the veteran personally confirms ..."). The base rules leave the performer open, so this is not a charter conflict; recorded as observation F-O1.

### rule_compute_equivalence

Mechanical sweep (temporary script, deleted): every `compute_basis` quotation of all seven policies is a verbatim substring of its policy's `rule`; every compute binding has a basis entry; every sentence of each `baseline.rule` is a sentence of the `rule`; every ladder tier is stated in the rule and implemented as a branch of the `decides` binding. Sentence-by-sentence sweep back found the following divergences (none is taken on either task's world; each is an observation unless a task file demonstrates otherwise):

- F-E1 (all six policies that count a spouse "recorded on the award"): the rule's AA tier is "a spouse is recorded on the award and that spouse's addition is marked as needing aid and attendance", but `*_spouses_aa` counts every AA-marked spouse addition ever recorded, removed or not (e.g. `dpd_spouses_aa: COUNT(... relationship='spouse', spouse_aid_attendance=True)`). On a world where an AA spouse was removed and a non-AA spouse added, the rule gives the spouse addition alone and the compute gives spouse + AA. Compute invents a basis.
- F-E2 (same policies): "A dependent counts ... when its addition stands and no removal of that relationship has been recorded" reads as "no removal of that relationship (type)"; compute takes `added - removed` per relationship. Two spouses added and one removed: rule -> no spouse counts, compute -> one.
- F-E3 (dependency_past_due): "a school child who has reached the school-child age limit" carries no time anchor in the rule; compute anchors it at NOW (`MONTHS(dep_school_birth, NOW)`). "the date of the marriage, birth or adoption recorded for its dependents" is plural; compute takes the latest by effective date.
- F-E4 (temporary_total, restoration): "the decision recording that the prior rating resumed" is implemented as the latest `decision_outcome='rating_continued'`; that enum value (db_schema) is also the outcome of an ordinary denied increase, so a later unrelated "rating continued" decision would be taken as the end of the temporary total.
- F-E5 (restoration): "cites an earlier review it continues" is taken as sufficient regardless of timing, while appeal's `appeal_agg_continuous_pursuit` keeps the original date only when the next lane is filed within `continuous_pursuit_window_days`.

### action_binding_and_uuids

- Each `(target_tool, computes)` pair is claimed by exactly one policy. Docstrings describe one atomic write each, name no other tool, and state no position in a sequence ("Afterwards ..." describes the tool's own post-state; "after a decision review overturned that reduction" in the restoration docstring describes the business situation, not a call order) — observation only.
- uuid8s: 543b1fec, 602dcd04, fbf191c5, a8e85818, 86166e35, 0acb107c, 92058ca9 — seven distinct, no shared prefix, no sequence, no tail-variation pattern. PASS.
- No tool body validates eligibility, status, order or amount: each body only rounds the given gross and creates/updates rows (`ctx.create`, `ctx.update`), and `resume_award_release_withheld_86166e35` sets status=running unconditionally. PASS (the tool layer judges no prerequisite).

### prerequisite_graph

- Every extended policy has `prerequisite` filled (four `[]`). Every `problem` names another extended policy id; none names a base policy or itself; the graph is acyclic (dependency <- decision <- switch, dependency <- switch, replacement <- switch; suspension <- restoration, temporary_total <- restoration).
- Every `policy_source` is verbatim in its own policy's rule and absent from the depended-on policy's rule (scripted check). Every `resolved_by` equals the depended-on policy's `target_tool`. Every `gate` names a binding of the blocked policy's compute (`dpd_paid`, `sw_paid`, `rr_paid`), and each `effect` describes a real entry into that binding (the depended-on write books a `comp_payment_reissued` or `comp_retro_payment` row that `dpd_paid` / `sw_paid` / `rr_paid` sums). `kind: value_input` on all six edges matches.
- `form`: action exactly on the two edges to dependency_past_due, each with a `fallback_reason`; state on the other four. No authoring-viewpoint phrasing in any `prerequisite` field. `condition` texts match the sentences' strength (see next section). PASS.

### prerequisite_sentences

| blocked -> depended | sentence (blocked policy's own rule) | test |
| --- | --- | --- |
| decision -> dependency (action) | "The past-due for a favorable rating decision is not fixed until the past-due additions owed for dependents recorded on the award's most recent dependency claim have been released." | ordering connective "not ... until"; names the depended-on action in business words; no tool/id; strength matches condition. Fallback tested: the dependency release books `comp_retro_payment` with `decision_id=""`, the same shape as the resumption release; a state sentence ("a retroactive entry citing no decision") would also be satisfied by a resumption, so the fallback is justified. PASS |
| switch -> replacement (state) | "The pension-to-compensation release is fixed only after every monthly payment on the award that came back has a replacement standing in the award's payment history." | "only after"; record-visible state (returned row + `comp_payment_reissued` row with the same `source_payment_id`); only `request_payment_replacement_543b1fec` creates `comp_payment_reissued`. PASS |
| switch -> dependency (action) | "Before the pension-to-compensation release is fixed, the past-due additions owed for dependents recorded on the award's most recent dependency claim must have been released." | as the first row. PASS |
| switch -> decision (state) | "The pension-to-compensation release is not worked out until the award's payment history carries a past-due release citing the most recent favorable rating decision." | "not ... until"; state. Writes that can book a retro entry with a decision link: decision, switch, temporary total, restoration releases. Temporary total cites only a TT decision and restoration only a `reduction_implemented` decision, neither of which is a "favorable rating decision" in the decision rule's list (SC, increase, IU, SMC (k)); the switch release cites "the decision granting the compensation". Single write (decision past-due) in any world where the most recent favorable decision is later than the compensation grant; where the most recent favorable decision IS the compensation grant, the switch release's own write would satisfy its own prerequisite (observation F-O2, world-dependent). PASS with observation |
| restoration -> suspension (state) | "A restoration after a reduction overturned on review is not worked out until the award's status is running again." | "not ... until"; record-visible state `comp_awards.status=running`; the only tool of this difficulty that sets status is `resume_award_release_withheld_86166e35`. PASS |
| restoration -> temporary total (state) | "A restoration after a reduction overturned on review is fixed only after the award's payment history carries a past-due release citing every temporary total rating decision on the award." | "only after"; state; only the TT release cites a `temporary_total_granted` decision (the decision release's list excludes TT). PASS |

Derivation (sentence + records + depended-on rule -> resolving action), single reading each: "replacement standing" -> the replacement rule ("replaced only once, only while the award is running ... requested by the veteran personally") -> `request_payment_replacement`; "past-due release citing the most recent favorable rating decision" -> the decision past-due rule ("released once as one retroactive payment that cites that decision") -> `release_decision_past_due`; "status is running again" -> the suspension rule ("that confirmation itself resumes the award") -> `resume_award_release_withheld`; "past-due release citing every temporary total rating decision" -> the temporary total rule ("released once as one retroactive payment that cites the temporary total decision") -> `release_temporary_total_past_due`; "past-due additions ... have been released" -> the dependency rule -> `release_dependency_past_due`. No rule restates another problem's tool name, id, or the sentence of its blocked policy. No extended rule states a cross-problem order outside the six sentences, except the replacement rule's exclusion "a payment whose month a release made when a suspension ended has already paid is not replaced", which states an effect of the resumption on the replacement (an exclusion, not an order) — observation F-O3.

### override_declarations

Sentence-by-sentence against each `base_policy_refs` entry (finding only; consequences are demonstrated per task):

- replacement (refs: comp_monthly_entitlement, comp_evt_payment_return). Declared: "A reissue repeats the gross amount of the payment it replaces." Undeclared:
  - F-B4 (anonymous intermediate): base "The gross monthly entitlement for an entitlement month is the veteran-alone rate of the combined rating tier in effect for that whole month ... A dependent counts for an entitlement month when the month is on or after the payment_adjust_month of its addition and before the payment_adjust_month of its removal ... Where the incarceration adjustment applies to the month, the incarcerated rate replaces the whole computation." The replacement "covers the same entitlement month", yet pays "the entitlement the award now carries" with every standing dependent and IU read from decision history, ignoring the month's tier, the adjust months and incarceration. Diverges whenever the month's entitlement differs from the current one.
  - F-B10: the extended rule re-asserts the superseded clause unconditionally ("A replacement repeats the gross amount of the payment that came back.") and then states the conditional replacement; the specific sentence governs only by a specific-over-general reading. Observation (the framework requires the baseline sentence in the rule).
  - comp_evt_payment_return "reissued only after the payment account or mailing address on the award has been updated", "reissued only once" — inherited.
- dependency_past_due (refs: rating_change, suspension, temporary_total, retro_withholding, dependency_add), `overwrite: []`. Undeclared:
  - F-B1: comp_retro_withholding "When the veteran has a VA benefit debt in active collection, the remaining amount is applied to that debt before any release ... and only the balance is paid." vs extended "released once, as one retroactive payment with nothing withheld for a fee or a debt" (unconditional; the tool books offset 0).
  - F-B2 (0/1 multipliers): comp_monthly_entitlement counts a dependent for every month before its removal's adjust month; extended pays "nothing when the claim records a spouse whose removal is recorded" and drops the school-child addition for every month when the school child "has reached" the age limit at handling time.
  - F-B3: comp_evt_incarceration ("payments from the incarceration_reduction_start_day ... dependent and SMC (k) additions stop for the same months") vs extended "no tier at all, so that no addition is released, when the award's most recent decision is an incarceration adjustment" (all months).
  - F-B9: comp_evt_dependency_add "the first entitlement month paid at the higher rate is the month after the effective date" vs extended "the whole months elapsed from the claim's effective date to the issue date of the most recent monthly payment" — with MONTHS semantics these differ by one when the effective date is the 1st of a month.
- decision_past_due (refs incl. comp_evt_rating_change, comp_monthly_entitlement, comp_tdiu), `overwrite: []`:
  - F-B8: base "Past-due benefits ... cover every entitlement month from the first month payable under the payment schedule through the last month already paid at the old rate, and equal, for each such month, the new gross monthly entitlement minus the gross amount already paid for that month." Extended prices every standing month on the award at today's entitlement and subtracts every payment and retro release ever booked, irrespective of the decision's effective date.
  - F-B3 again: "the incarcerated rate alone ... when the most recent decision is an incarceration adjustment" for every month.
  - F-B5 (all policies with "recorded" dependents): month-blind dependent counting vs comp_monthly_entitlement's adjust-month window.
- pension_switch (refs incl. comp_excl_pension_election, comp_payment_schedule), `overwrite: []`: offsets pension paid for the overlap months — consistent with "never paid to the same veteran for the same month"; F-B3 and F-B5 apply.
- suspension_release: both conflicting comp_evt_suspension sentences are declared in `overwrite` and the merged reading is unique. PASS.
- temporary_total (refs incl. comp_temporary_total, comp_evt_rating_change), `overwrite: []`:
  - F-B6: base "minus the gross amount already paid for that month" vs extended "The monthly amount the award paid for each temporary total month is the gross of the most recent monthly payment issued on the award."
  - F-C1: comp_evt_rating_change "Past-due benefits on a suspended award are computed but released only when the award resumes." is inherited (not overwritten) and orders a TT release on a suspended award after the resumption; the TT rule carries no sentence about it and the charter declares no TT -> suspension edge.
  - F-B3 applies.
- review_restoration (refs incl. comp_evt_reduction_due_process), `overwrite: []`:
  - F-B7: "What stands paid for the restoration months is the gross of every monthly payment, replacement and past-due release issued on the award within that many whole months before today" windows by issue date, while base subtracts what was paid "for that month".
  - F-B3 applies.

### factor_ladders

Counts as declared (effect labels, `cross_difficulty`):

| policy | factors (effect) | parameter / method | multi-source | cross_difficulty |
| --- | --- | --- | --- | --- |
| replacement | replacement_basis (method), replacement_spouse (param), replacement_children (param), replacement_parents (param) | 3 / 1 | basis tier 2, children tiers, spouse tiers combine >=2 conditions | none |
| dependency | dependency_release_months (method), dependency_release_tier (method), dependency_release_spouse (param), dependency_release_children (param) | 2 / 2 | months (dates vs payment counts) | none |
| decision | decision_past_due_rate_tier (method), _spouse, _children, _parents, _smc_k (param) | 4 / 1 | rate_tier tier 1, spouse, children | none |
| switch | switch_release_rate_tier (method), switch_release_pension_offset (method), _spouse, _children, _parents, _smc_k (param) | 4 / 2 | pension_offset (pension termination reason AND pension ledger vs comp rate) | pension (pension_offset) |
| suspension | resumption_release_months (method), _spouse, _children, _parents (param) | 3 / 1 | months (returned AND replaced counts) | none |
| temporary_total | temporary_total_rate_tier (method), _spouse, _children, _parents (param) | 3 / 1 | rate_tier tier 1 | none |
| restoration | restoration_start (method), restoration_rate_tier (method), _spouse, _children, _parents, _smc_k (param) | 4 / 2 | restoration_start (review outcome, received date vs reduction notice, prior review) | appeal (restoration_start) |

Bindings are disjoint within each policy; every `decides` names an input, never `result`; every ladder has >=3 tiers stated in the rule and implemented in compute; no two tiers of one ladder select the same value or method; labels are honest (method tiers change the algorithm or the months rule; parameter tiers change a number).

Reality and scope of the ladders (judged against VA practice and the charter's own scope):

- F-A1 (unreal tier, five factors: dependency_release_tier, decision_past_due_rate_tier, switch_release_rate_tier, temporary_total_rate_tier, restoration_rate_tier): the tier "the award's most recent decision is an incarceration adjustment" selects "the incarcerated rate alone, with no dependent or SMC (k) addition" (or "no addition at all") for every month of the past-due. VA (38 CFR 3.665, and this charter's own base comp_evt_incarceration: "payments from the incarceration_reduction_start_day ... are limited", "dependent and SMC (k) additions stop for the same months", "Full payment is restored from the date of release") limits only the months from the 61st day of felony incarceration; months before it, and months after a notified release, are paid in full. No VA office prices a whole past-due span at the incarcerated rate because the latest decision on file is an incarceration adjustment. SOURCE-FACTOR RED (unreal ladder) for every factor carrying it.
- F-A2 (unreal tiers, dependency_release_spouse and dependency_release_children): "nothing when the claim records a spouse whose removal is recorded" and "one school-child addition for each school child below that limit when the claim records a school child who has reached it" zero a dependent's addition for every month of the span because of a later event. VA pays a dependent's addition for every month up to the removal's effective date (base comp_evt_dependency_remove, comp_monthly_entitlement). SOURCE-FACTOR RED (unreal ladder).
- F-A3 (scope-restating condition, temporary_total_rate_tier): every customer who reaches `release_temporary_total_past_due` holds a TT grant ("Past-due from a temporary total rating ... cites the temporary total decision"), so the conjunct "the decision history shows a temporary total rating granted" holds of every customer at this write and the fall-through ("the veteran-alone rate ... otherwise", which is also the factor's baseline and the baseline.rule's rate) is reachable for no in-scope customer; a TT past-due priced at the veteran-alone rate is not a treatment VA publishes (base comp_temporary_total: "paid at temporary_total_monthly_rate"). SOURCE-FACTOR RED.
- F-A4 (scope-restating condition and straw-man baseline, restoration_start): the rule's scope is "When a decision review overturns a reduction ...", so the conjunct "the review of the reduction decision was granted" holds of every customer at this write and the fall-through "no start date, so no restoration months" is unreachable in scope; its baseline `rr_start: "''"` is the unreachable fall-through, giving a restoration of 0 — a zero where every in-scope reading gives a figure. `baseline.rule` also never says what the start date is ("The restoration months are the whole months elapsed from the restoration's start date to today ... none when the restoration has no start date"), so it is not self-sufficient. SOURCE-FACTOR RED (unreal ladder; dishonest/incoherent baseline).
- F-A5 (scope-restating condition and unreal fall-through, switch_release_pension_offset — the charter's only pension cross-difficulty factor): the rule's scope is a veteran "receiving Veterans Pension ... granted compensation that is greater ... and the pension award is terminated by election", so "the pension award ended by election of compensation" holds of every customer at this write and the fall-through "take nothing off" is unreachable in scope; were it reached, paying compensation for months already paid as pension contradicts comp_excl_pension_election ("never paid to the same veteran for the same month"). Tier 2 ("monthly pension last paid is greater than the monthly rate") sits against the scope's "compensation that is greater". SOURCE-FACTOR RED.
- F-A6 (stamp risk, structural): `comp_awards.tdiu_granted` (db_schema: "true when individual unemployability is in effect, so the award is paid at the 100 percent rate") and `comp_awards.smc_k_count` ("number of special monthly compensation (k) awards in effect") are award fields that name the outcome of the IU tier (rate_tier factors of dependency, decision, switch) and of the SMC (k) ladders (decision, switch, restoration). Whether a seeded stamp agrees with the tier is judged per task.
- F-A7 (observation): every dependent-addition ladder (spouse / children / parents in replacement, decision, switch, suspension, temporary total, restoration) restates base comp_monthly_entitlement, which is inherited and published; the baseline "nothing" for these inputs is the computation document's silence, while the base clause in force gives the figure. Not a policy-task RED; flagged for the KB audit (a base document carries the ladder).
- F-A8 (observation): the replacement's spouse/children/parents factors decide inputs of a quantity (the recomputed entitlement) that `baseline.rule` ("A replacement repeats the gross amount of the payment that came back.") never computes; their individual weight exists only through replacement_basis's first tier.

### findings

| id | verdict | summary | bears on |
| --- | --- | --- | --- |
| F-A1 | SOURCE-FACTOR RED | incarceration tier prices every past-due month at the incarcerated rate / releases no addition — not VA practice, contradicts base comp_evt_incarceration month scoping | task 0 (dependency, decision, switch), task 1 (temporary total, restoration) |
| F-A2 | SOURCE-FACTOR RED | dependency spouse/children tier 2 zero additions for the whole span | task 0 (dependency) |
| F-A3 | SOURCE-FACTOR RED | TT rate tier's TT-granted conjunct restates scope; unreachable, unreal fall-through/baseline | task 1 |
| F-A4 | SOURCE-FACTOR RED | restoration_start granted conjunct restates scope; baseline is the unreachable zero; baseline.rule has no start date | task 1 |
| F-A5 | SOURCE-FACTOR RED | pension offset's election conjunct restates scope; fall-through unreachable and contrary to the no-dual-payment rule | task 0 |
| F-A6 | structural; verdict per task | IU / SMC (k) tiers duplicated by award stamps | task 0, task 1 |
| F-B1..F-B9 | SOURCE-POLICY finding; RED only where a task demonstrates a second answer | undeclared overrides listed above | task 0 (B1, B2, B3, B4, B5, B8, B9), task 1 (B3, B5, B6, B7) |
| F-C1 | observation unless a task's order is forced against it | base "released only when the award resumes" orders a past-due release after a resumption; no declared edge | task 1 |
| F-C2 | observation | base "reissued only after the payment account ... has been updated" orders a reissue after a profile update; no declared edge | task 0 |
| F-E1..F-E5 | observation | rule/compute divergences not taken on either world | both |
| F-O1 | observation | blueprint summary names reissue and resumption as the representative's actions; the charter makes both owner=user | both |
| F-O2 | observation | switch -> decision state sentence would be self-satisfied where the compensation grant is the most recent favorable decision | task 0 |
| F-O3 | observation | replacement exclusion after a resumption is an un-edged cross-problem relation | task 1 |
| F-B10 | observation | replacement rule re-asserts the superseded "repeats the gross" clause unconditionally | task 0 |
| F-A7, F-A8 | observation | dependent ladders restate base; replacement dependent factors act only through the basis factor | both |

## closing_checklist

Written after both reveals (2026-10-06T03:36Z). The difficulty is **not closed**: both tasks carry SOURCE-FACTOR RED, so the source-layer audit does not pass.

- Per-task files 0.md and 1.md correspond one-to-one with tasks 0 and 1; this is the first revision. Comparison sections: task 0 SOURCE-POLICY PASS / SOURCE-CHAIN PASS / SOURCE-FACTOR RED / SOURCE-TASK PASS; task 1 the same.
- Coverage and scope: the two tasks' `charter_scope` cover all seven extended policies and seven tools, pairwise disjoint (task 0: replacement, dependency, decision, switch; task 1: suspension, temporary total, restoration) — matching the two components derived pre-reveal. uuid8s independent and frozen. PASS.
- Problem trees: task 0 has 3 prerequisite problems, 4 value_input edges, one owner=user problem; task 1 has 2, 2, one owner=user; the whole graph is acyclic; the blind trees matched `prerequisite_closure` value for value. PASS.
- Factors: every declared factor bears weight on its world against its declared baseline, and every computation's all-baselines fall-back is definite and differs from gold — but the ladder tests fail: F-A1 (incarceration tier, 5 factors), F-A2 (dependency spouse/children), F-A3 (TT rate tier), F-A4 (restoration start), F-A5 (pension offset), and award stamps `tdiu_granted` / `smc_k_count` agreeing with the IU and SMC (k) tiers. After striking, the dependency, decision, switch, temporary total and restoration computations fall below 4 factors or 1 method, and neither task keeps a cross-difficulty factor. FAIL.
- Every scored write, argument, owner and order of both tasks matched the blind derivations (SOURCE-TASK PASS).
- Instantiation-stage gates: not re-run by this auditor (the skill assigns the re-run to closing on the final form; no final form exists while the REDs stand). The orchestrator's pre-audit snapshot (all green) stands as the entry record only.

## revision_2

### charter_global_frozen (revision 2)

- Written 2026-10-06 ~05:52Z, before either task's round-2 GT was opened. Round-1 text above is untouched (round-1 files hashed at 05:50:35Z: 0.md 76d7b8d2…, 1.md 65e328ab…, _difficulty.md 59dd3f56…).
- Shared inputs moved, so every charter-global section is re-derived in full: `comp.extended.yaml` 0e4bfa47… -> e7a8775d27e6fa33dbe1296313fa30ecbf46424b47ab71d06bfe57687179b3b5; `task_tools.py` f9f5b6f4… -> d75c8f7246782993a83824332985244767be9c89e15cc8dc941a3f27c0e09510 (both match the round-2 MANIFEST). Base section still verbatim with `blueprint/products/comp.yaml` (diff: one trailing blank line).
- Entry conditions: round-2 GATES.txt present, all eight green, traceability deferred; masked views task_0 df6bcec6…, task_1 75fd6fe3… re-hashed and matching. The reworker's closure claims were treated as unverified.
- Masked/unread until both task files' round-2 frozen sections are on disk: every task field other than `frozen_time`, `user_scenario`, `initial_state`.

### policy_conflict_scan (r2)

Same seven policies, tools, owners and edges as round 1; two components {switch, replacement, dependency, decision} / {restoration, suspension, temporary total}, disjoint and jointly complete. Changes: switch's scope is widened to any award "When compensation becomes payable for months before an award began running" (renamed "opening past-due release"), and it now reads debt as well as pension; the decision release now covers "favorable rating decisions ... made after the award has issued monthly payments" and cites "the most recent such decision"; the dependency release now scopes itself to "no debt in active collection"; the replacement scopes out "a month to which no incarceration adjustment applies". Every incarceration tier is gone from the extended rules (base comp_evt_incarceration is inherited untouched). Base orders F-C1 / F-C2 unchanged (observations).

### rule_compute_equivalence (r2)

Scripted again (temporary, deleted): every `compute_basis` quotation verbatim in its rule; every compute binding has a basis; every `baseline.rule` sentence is a rule sentence; every factor's bindings are disjoint and contain its `decides`. Sweep-back:
- F-E1 closed: AA now keyed on "the most recent spouse addition" (`LATEST(... spouse_aid_attendance ...)`) in all seven policies.
- F-E2 closed: "that relationship's additions on the award less its removals" now states what compute does.
- F-E3 closed: "the latest date of marriage, birth or adoption recorded on the claim" = `LATEST(qualifying_event_date)`; the age-limit tier is gone.
- F-E4 closed: the resumption decision is now "the decision on the same claim recording that the prior rating resumed" (`claim_id=tt_claim`) in temporary total and restoration.
- F-E5 closed: restoration_start now reads the continuous-pursuit window (`continuous_pursuit_window_days`, earlier review's decided date).
- New observation R2-O1 (dependency): "The months of a dependency release priced from the 100 percent tier are every month it covers when individual unemployability is granted and the whole months from its effective date ..." — "its" follows "it covers" (the release) as well as "individual unemployability"; compute reads the IU decision's effective date. The decision rule's parallel sentence and the factor wording ("its months up to the latest monthly issue") point to IU; see task 0 for the value of the other reading.

### action_binding_and_uuids (r2)

Unchanged uuid8s (543b1fec, 602dcd04, fbf191c5, a8e85818, 86166e35, 0acb107c, 92058ca9); one policy per tool; tool bodies still only round, create and (resume) update — no validation. Only docstring change: the switch tool now describes "the months before a newly payable award began running ... net of any Veterans Pension already paid", matching the widened rule. PASS.

### prerequisite_graph and prerequisite_sentences (r2)

Same six edges, kinds, forms and fallback reasons; every `policy_source` verbatim in its own rule and absent from the depended-on rule; `resolved_by` = target tool; gates bind (`dpd_paid`, `sw_paid`, `rr_paid`). The switch -> decision sentence now reads "a past-due release citing the most recent favorable rating decision made after the award's first monthly payment" — the compensation grant itself can no longer satisfy it, so F-O2 is closed; the only write that brings the state about is the decision release. Other sentences: wording "pension-to-compensation release" -> "opening past-due release"; same four-point results as round 1. PASS.

### override_declarations (r2)

Every extended policy now declares the base month-blind dependent clause it departs from ("A dependent counts for an entitlement month when ..."), and the past-due policies declare the comp_evt_rating_change per-month sentence they replace; all superseded clauses are verbatim base text (scripted). Round-1 items:
- F-B1 closed (dependency scoped to "no debt in active collection"). F-B2 closed (zero tiers removed; counting declared). F-B3 closed as stated (no extended incarceration tier remains; residual observation R2-O2: no past-due compute applies base comp_evt_incarceration's month scoping, so on a world with an incarceration adjustment the inherited base clause and the compute would diverge — neither task has one). F-B4 closed (tier-in-effect and adjust-month clauses declared; incarceration months scoped out). F-B5 closed (declared everywhere). F-B6 closed (TT paid amount is now the payments issued for the TT months, read by window). F-B7 closed (declared). F-B8 closed (declared). F-B9 closed (declared).
- New observation R2-O3: "Only the spouse and child additions recorded on the most recent dependency claim enter a dependency release." Base comp_evt_dependency_add releases past-due additions for every added dependent, parents included, and no other extended policy releases a parent's past-due addition. Undeclared narrowing (present in round 1 too, missed then); no parent is on either task's most recent dependency claim, so no consequence.
- F-B10, F-C1, F-C2, F-O1, F-O3 unchanged (observations).

### factor_ladders (r2)

| policy | factors (effect) | p / m | cross |
| --- | --- | --- | --- |
| replacement | basis (m), spouse, children, parents (p) | 3 / 1 | — |
| dependency | months (m), unemployability_months (m), spouse, children (p) | 2 / 2 | — |
| decision | unemployability_months (m), smc_k_months (m), spouse, children, parents (p) | 3 / 2 | — |
| switch | unemployability_months (m), smc_k_months (m), pension_offset (m), spouse, children, parents (p) | 3 / 3 | pension (offset; also reads debt) |
| suspension | months (m), spouse, children, parents (p) | 3 / 1 | — |
| temporary total | smc_k_months (m), spouse, children, parents (p) | 3 / 1 | — |
| restoration | start (m), full_tier_months (m), smc_k_months (m), spouse, children, parents (p) | 3 / 3 | appeal (start) |

Round-1 items:
- F-A1 closed: no incarceration tier remains.
- F-A2 closed: removal / age-limit zero tiers removed.
- F-A3 closed: the TT rate tier is gone; the TT rate is the standard method and the factor is now SMC (k) months by grant date — real, reachable tiers.
- F-A4 closed: restoration_start's ladder is "late and not continuing -> review received", "continuing a late earlier review -> earlier received", fall-through "timely or continuing a timely chain -> date the reduced rate took effect"; the baseline is that fall-through and `baseline.rule` now states it ("The restoration's start date is the date the reduced rate took effect.") — self-sufficient, real (continuous pursuit as in appeal_agg_continuous_pursuit).
- F-A5 closed: pension offset tiers are "pension paid for months the release covers and no Veterans Pension Overpayment debt -> pension x overlap", "... and such a debt -> that less what the debt collected", fall-through "no pension paid for months covered -> nothing"; with the widened scope the fall-through is reachable and real.
- F-A6: the IU and SMC (k) factors are now month-count ladders keyed on grant effective dates against the award / TT / restoration dates; `tdiu_granted` / `smc_k_count` name only "granted", not which month-count tier applies. Closed structurally; per-task check in the task files.
- **New R2-A1 (SOURCE-FACTOR RED, dependency_release_spouse and dependency_release_children):** `baseline.rule` is "The dependency release is the additions owed each month for the claim's dependents multiplied by the months it covers ..." with `params: [dependency_report_window_days]` — it never says what the additions are, so it is not self-sufficient, and its own sentence says additions ARE owed for the claim's dependents while both factors' baselines are `0`. The all-baselines fall-back of a dependency release is therefore 0 for any claim that records a spouse or child: a zero where the standard method gives a figure. Regression: round 1's baseline.rule stated the additions ("one spouse addition for each spouse ... and one child addition for each child ..., at the rates of the award's own tier").
- **New R2-A2 (SOURCE-FACTOR RED, restoration_full_tier_months):** the tier "the decision history shows individual unemployability granted and no temporary total rating => price every restoration month at the individual unemployability rate with 100 percent tier additions" ignores the IU effective date, and the TT tier prices `MN(tt_span, rr_months)` months at the TT rate whether or not the TT months fall inside the restoration span and ignores any IU months. VA pays the IU rate only for months IU is in effect and the TT rate only for the TT months (base comp_monthly_entitlement "When individual unemployability is in effect"; comp_temporary_total). The dependency, decision and switch policies of this same charter do date their IU months; restoration does not.
- F-A7, F-A8 unchanged (observations).

### findings (r2)

| id | status r2 | bears on |
| --- | --- | --- |
| F-A1, F-A2, F-A3, F-A4, F-A5 | closed | — |
| F-A6 | closed structurally; per-task confirmation in task files | both |
| F-B1–F-B9, F-E1–F-E5, F-O2 | closed | — |
| F-B10, F-C1, F-C2, F-O1, F-O3, F-A7, F-A8 | unchanged observations (no change needed agreed) | both |
| R2-A1 | **new SOURCE-FACTOR RED** (regression) | task 0 |
| R2-A2 | **new SOURCE-FACTOR RED** | task 1 |
| R2-O1, R2-O2, R2-O3 | new observations | task 0 (O1), both (O2, O3) |

### closing_checklist (revision 2)

Written after both round-2 reveals. **Not closed.**
- Task 0: SOURCE-POLICY PASS, SOURCE-CHAIN PASS, SOURCE-FACTOR RED (R2-A1), SOURCE-TASK RED (decision release span not entailed after the rework). Task 1: SOURCE-POLICY PASS, SOURCE-CHAIN PASS, SOURCE-FACTOR RED (R2-A2), SOURCE-TASK PASS.
- Verified closed: F-A1–F-A6, round-1 findings 5 (both tasks), F-B1–F-B9, F-E1–F-E5, F-O2, T0-O1, T0-O2, T0-O6, T0-O7, T1-O1, T1-O3. Agreed no change needed: F-B10, F-C1, F-C2, F-O1, F-O3, F-A7, F-A8, T0-O4, T1-O2; T0-O3 now moot; T0-O5 overtaken by the new task-0 SOURCE-TASK finding.
- Open: R2-A1 (dependency baseline, regression), R2-A2 (restoration full-tier ladder), task-0 decision-span SOURCE-TASK RED (regression); observations R2-O1, R2-O2, R2-O3, R2-T1-O1.
- Scopes disjoint and complete, uuid8s unchanged, trees and values match GT figure for figure; gates not re-run by the auditor (no final form while REDs stand).

## revision_3

### charter_global_frozen (revision 3)

- Written before either round-3 GT was opened; revisions 1–2 above untouched (hashes before this append: see 0.md / 1.md revision_3 headers).
- `comp.extended.yaml` e7a8775d… -> 4e7f3c62c085f3870102238a8d6969533b43541a8d934a47d1269c0b7f2e02ad: charter-global sections re-derived in full. `task_tools.py` d75c8f72… unchanged: the tool contract conclusions of revision 2 (uuid8s, docstrings, no validation) carry forward on that hash. Base section still verbatim. Round-3 GATES.txt all green (traceability deferred); views task_0 f2e742a1…, task_1 75fd6fe3… (task 1's view is byte-identical to round 2).
- Mechanical re-check (temporary script, deleted): every `compute_basis` quotation verbatim in its rule; every compute binding has a basis; every `baseline.rule` sentence in its rule; every `superseded_clause` verbatim in its base policy and every `replaced_by` verbatim in the extended rule; prerequisite sentences verbatim, own-rule only, `resolved_by` = target tool, gates bind; factor bindings disjoint. All pass.

### changes and conflict scan (r3)

- Every extended rule now scopes itself to months where "no incarceration adjustment applies" (replacement, dependency, decision, opening release, resumption, temporary total, restoration) — R2-O2 closed; the inherited base comp_evt_incarceration no longer meets an extended computation.
- Dependency release: covers "the award's most recent dependency claim and ... any school-attendance claim received the same day"; parents now enter ("one parent addition for each dependent parent, up to the parent maximum") — R2-O3 closed. `baseline.rule` now states the additions ("one spouse addition for each spouse, one child addition for each child and one parent addition for each dependent parent, up to the parent maximum, recorded on those claims, at the rates of the award's own tier") and the spouse/children factor baselines encode exactly that (`P('spouse_addition') * dep_spouses`, `(dep_minors + dep_schools) * P('child_under_18_addition')`, 100%-tier analogues) — self-sufficient and honest; each fall-through tier equals it. R2-A1 closed. "individual unemployability's effective date" replaces "its effective date" — R2-O1 closed.
  - New observation R3-O1: the declared replacement of the adjust-month clause is now "The additions owed each month are ... recorded on those claims", so a spouse or child removed after the claim still counts for every month of the release (removals no longer read). Declared, no ladder involved, no removal on either world — observation.
- Decision release: scope now "when a decision's effective date makes payable an entitlement month whose monthly payment had already been issued when the decision was made" (R2-T1-O1 closed: task 1's 2026-03-20 SMC (k) decision makes April payable, issued 2026-05-01, after it). New span sentence: "Its span runs from the first entitlement month made payable by the earliest such decision through the last entitlement month whose monthly payment was issued before the most recent such decision was made."
  - **R3-T1 (finding, judged per task):** "such decision" grammatically refers back to "favorable rating decisions that grant service connection, an increase, individual unemployability or SMC (k)" — the applicability clause is attached to the release ("when a decision's effective date ..."), not to "such". Where the award carries a favorable grant made before its first monthly payment (an original service-connection grant), "the earliest such decision" is that grant and the span starts at the first month it made payable. See task 0.
- Restoration: `restoration_full_tier_months` now prices "the temporary total months that fall within the restoration months" (TT months less those before the start), "the individual unemployability months that fall within the restoration months" (from IU's effective date), both, or none — date-bounded, four real tiers. R2-A2 closed.
- Unchanged: switch (opening release), replacement, resumption, temporary total (bar the incarceration scope). F-B10, F-C1, F-C2, F-O1, F-O3, F-A7, F-A8 remain observations.

### factor_ladders (r3)

| policy | factors | p / m | cross |
| --- | --- | --- | --- |
| replacement | basis (m), spouse, children, parents | 3 / 1 | — |
| dependency | months (m), unemployability_months (m), spouse, children | 2 / 2 | — |
| decision | unemployability_months (m), smc_k_months (m), spouse, children, parents | 3 / 2 | — |
| opening release | unemployability_months (m), smc_k_months (m), pension_offset (m), spouse, children, parents | 3 / 3 | pension (+debt) |
| resumption | months (m), spouse, children, parents | 3 / 1 | — |
| temporary total | smc_k_months (m), spouse, children, parents | 3 / 1 | — |
| restoration | start (m), full_tier_months (m, 4 tiers), smc_k_months (m), spouse, children, parents | 3 / 3 | appeal |

No unreal tier, no scope-restating condition, no shared-outcome tiers found; dependency_release_children's fall-through ("one child addition for each child recorded" when the claims record only minor children) is real; its baseline applies that default to every child, as `baseline.rule` states.

### findings (r3)

| id | status r3 |
| --- | --- |
| R2-A1, R2-A2, R2-O1, R2-O2, R2-O3, R2-T1-O1 | closed |
| task-0 decision-release span (r2 SOURCE-TASK) | span now stated; second reading R3-T1 judged in task 0 |
| R3-O1 | new observation (removals ignored by the dependency release) |
| R3-T1 | new; verdict in task 0 |
| round-1 closures | re-checked: no incarceration / zero / scope-restating tier reintroduced; overrides still declared; AA and counting wording still match compute — no regression |

### closing_checklist (revision 3)

Written after both round-3 reveals. **Not closed** — one red remains.
- Task 0: SOURCE-POLICY PASS, SOURCE-CHAIN PASS, SOURCE-FACTOR PASS, SOURCE-TASK RED (R3-T1: "the earliest such decision" also reads as the original service-connection grant, giving a different decision-release span). Task 1: PASS on all four.
- Verified closed this round: R2-A1, R2-A2, R2-O1, R2-O2, R2-O3, R2-T1-O1; the round-2 decision-span finding is narrowed to R3-T1. No round-1 or round-2 closure regressed.
- Scopes disjoint and complete; uuid8s and tool contract unchanged; both trees acyclic with an owner=user problem and the required value_input edges; every factor bears weight against an honest, self-sufficient baseline and every computation meets the factor bounds with multi-source and cross-difficulty factors per task.
- Open: R3-T1 (SOURCE-TASK RED, task 0). Observations: R3-O1, R3-T1-O1, F-B10, F-C1, F-C2, F-O1, F-O3, F-A7, F-A8, T0-O4, T1-O2.
- Gates not re-run by the auditor (final form not reached).

## revision_4

### charter_global_frozen (revision 4)

- Written before either round-4 GT was opened; revisions 1–3 untouched. `comp.extended.yaml` 4e7f3c62… -> e5c08e153f9b069bd879e243f9c86d17651b55f232496f4fbf69a42c9c20a8fe (charter-global re-derived); `task_tools.py` d75c8f72… unchanged (tool-contract conclusions carried forward on that hash). Both views byte-identical to round 3 (task_0 f2e742a1…, task_1 75fd6fe3…). Round-4 GATES.txt all green, traceability deferred. Base section still verbatim.
- Mechanical re-check (temporary script, deleted): compute_basis verbatim, every binding based, baseline sentences in rule, overwrite clauses verbatim on both sides, prerequisite sentences verbatim / own-rule / resolved_by / gate, disjoint factor bindings — all pass. Rule lengths, factor ladders, overwrite and compute counts of six policies are unchanged from round 3; only comp_ext_decision_past_due's rule changed, and every computation of both tasks recomputes to the same figures as round 3 (re-run below).

### change and check (r4)

- comp_ext_decision_past_due now opens: "A qualifying decision is a favorable rating decision that grants service connection, an increase, individual unemployability or SMC (k) and whose effective date makes payable an entitlement month whose monthly payment had already been issued when that decision was made; a favorable decision made before the month it first makes payable was paid is not a qualifying decision." The release "cites the most recent qualifying decision" and "Its span runs from the first entitlement month made payable by the earliest qualifying decision through the last entitlement month whose monthly payment was issued before the most recent qualifying decision was made." "such decision" no longer appears in that rule (the only remaining "such decision" is the temporary total rule's unrelated "none while no such decision is recorded"). R3-T1 closed at the charter level; per-task confirmation in 0.md.
- Consistency with the switch -> decision prerequisite sentence ("the most recent favorable rating decision made after the award's first monthly payment"): on any world where a favorable decision made after the first monthly payment qualifies, it is the decision the release cites; no new conflict.
- No other change; round-1 to round-3 closures hold. Observations R3-O1, R3-T1-O1 and the standing set unchanged (agreed no change needed).

### closing_checklist (revision 4)

Written after both round-4 reveals. **All four relationships PASS for both tasks; the source-layer audit of this difficulty passes.**
- Per-task files 0.md and 1.md correspond one-to-one with tasks 0 and 1, each carrying revisions 1–4 in order with older text untouched; every revision-4 comparison section carries PASS.
- All seven extended policies covered; the two scopes ({replacement, dependency, decision, opening release} / {resumption, temporary total, restoration}) are pairwise disjoint and jointly complete; task tools and GT are closed; seven independently generated, frozen uuid8s (unchanged since round 1).
- Task 0: 3 prerequisite problems, 4 value_input edges, owner=user replacement; task 1: 2 prerequisite problems, 2 value_input edges, owner=user resumption; the difficulty's prerequisite graph is acyclic.
- Every computation declares a self-sufficient baseline and 4–6 factors (>= 2 parameter, >= 1 method), each ladder >= 3 real, distinct tiers stated in its rule; every factor bears weight on its task's world against an honest baseline, and every all-baselines fall-back is definite and differs from gold; each task has a multi-source factor and a cross-difficulty factor on seeded rows (task 0 pension; task 1 appeal).
- Id-valued gold arguments verified on replay (no write-minted id consumed; every id returned by an earlier call).
- Remaining observations (no RED): R3-O1, R3-T1-O1, F-B10, F-C1, F-C2, F-O1, F-O3, F-A7, F-A8, T0-O4, T1-O2.
- Instantiation-stage gates on the final form: the orchestrator's round-4 snapshot (all eight green, traceability deferred to the KB step) is the record; this auditor does not run gates.
