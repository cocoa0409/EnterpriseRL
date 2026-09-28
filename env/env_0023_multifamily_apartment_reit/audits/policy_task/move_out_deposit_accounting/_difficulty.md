# Policy-task audit — move_out_deposit_accounting / charter-global

## charter_global_frozen

- Revision: 1 (no earlier audit of this difficulty exists; `audits/policy_task/move_out_deposit_accounting/` was created by this audit).
- Freeze time: 2026-09-24T18:18:47Z (file mtime; written before either reveal, which began at 2026-09-24T18:20:33Z). Auditor: independent policy-task auditor (not the instantiating agent).
- Frozen inputs (sha256):
  - `tasks/move_out_deposit_accounting/deposit.extended.yaml` = `26b3f78d945d8890ad23cf2b895b9dc96af42cd63aed908a27d8f5def4dcc9e2`
  - `tasks/move_out_deposit_accounting/task_tools.py` = `92f68af4b70dce083a733d6e62f409698be576e4d2bb8ef5e7d22d630136a5bc`
  - masked view `r1/0.json` = `15f424e0...cc475438`, masked view `r1/1.json` = `2321e966...cad9288` (both re-hashed by the auditor and equal to the brief).
- Read for this section: `blueprint/blueprint.yaml`, `blueprint/db_schema.json`, `blueprint/share_tools.py`, `blueprint/products/{deposit,lease,term,pet}.yaml` (deposit in full; lease/term/pet only for the parameters and rules the extended policies read), the extended charter and the tool module in full, `erlbench` compute semantics as implemented in `skills/erl-task-instantiate/scripts/check_compute.py` (`MONTHS`, `DAYS`, `_within`, `XCOUNT`, `CFIELD`, `CPARAM`, `EXISTS`, `LATEST`).
- Masked and not read: every `tasks/*.json` field other than `frozen_time`, `user_scenario`, `initial_state`; `worklog.md`; every other audit directory. Nothing in this section is derived from a revealed GT.
- Entry conditions: the coordinator's gate snapshot (check_extended, check_task_tools, replay_tasks, check_solvability, check_compute, check_grounding, check_cross_fire all rc=0; check_traceability deferred to the render stage) and the masked-view hashes were supplied. Observation: the replay excerpt quoted in the brief shows only the `1.json` row; entry is accepted on the printed `REPLAY OK`.

### policy_conflict_scan

Base section: `yaml.safe_load` of the charter's base keys (`category, display_name, binding, lifecycle, accounts, parameter_schema, variants, events, measures, policies`) equals `blueprint/products/deposit.yaml` key by key, and a textual diff of the charter up to `extended_policies:` against the product file differs only by the appended banner. The base copy is verbatim.

Extended policies (6) and their claims:

| policy | subject / computes | target_tool (owner) | who it applies to |
| --- | --- | --- | --- |
| deposit_ext_cleaning_correction_credit | deposit_balance_credit / amount | post_cleaning_correction_credit_249da733 (agent) | cleaning line under a dispute accepted for a misapplied cleaning charge |
| deposit_ext_settlement_payment | deposit_balance_payment / amount | pay_settlement_balance_cadbabf4 (user) | former resident of an account that held a cash deposit, before the due date |
| deposit_ext_carpet_depreciation_credit | deposit_balance_credit / amount | post_depreciation_correction_credit_f675d6ed (agent) | carpet replacement line, dispute accepted for misapplied depreciation |
| deposit_ext_repair_labor_credit | deposit_balance_credit / amount | post_repair_labor_credit_05a989cb (agent) | damage repair line, dispute accepted for misapplied labor |
| deposit_ext_fob_count_credit | deposit_balance_credit / amount | post_fob_count_credit_b88884f4 (agent) | unreturned-fob line, dispute accepted for a misapplied count |
| deposit_ext_guarantee_gap_payment | deposit_balance_payment / amount | pay_guarantee_gap_4e6273ca (user) | former resident of a Zero-Deposit Guarantee Plan account, before the claim |

- Overlapping subjects: the four credit policies share `deposit_balance_credit`; they are partitioned by the disputed line's `line_category` (cleaning / carpet_replacement / damage_repair / unreturned_fob), so no line is claimed by two. The two payment policies share `deposit_balance_payment`; they are partitioned by program ("an account that held a cash deposit" vs "a Zero-Deposit Guarantee Plan account"), which are complementary (the guarantee plan has `deposit_basis: guarantee`, no cash). Base `deposit_balance_and_collections` also names `deposit_balance_credit` / `deposit_balance_payment` but only for the write-off, claim and plain payment; no base sentence prices a settlement or a gap payment.
- Triggers / time anchors: the credits are `state_due` (an accepted dispute on the line); the payments are `on_request` and bounded by the due date (settlement: "before its due date"; gap: "before the guarantee is claimed", which by base is `guarantee_claim_waiting_days` after the due date). No two anchors disagree.
- Terminal states: every write is one row in `deposit_transactions`; none changes `deposit_accounts.status`. Base `deposit_disputes_and_amendment` still says "a corrected statement follows" after an accepted dispute; no tool of this difficulty writes `deposit_disposition`, and no extended rule mentions it (observation O-3).
- Cross-category read boundaries: every `cross_category` entry reads only fields that exist in `db_schema.json` and categories listed in the policy's `inputs.cross_category`; the gates confirm this and the auditor found no contrary case.
- Scopes: the two tasks' worlds are consistent with task 0 = {cleaning credit -> settlement payment} and task 1 = {carpet, repair, fob credits -> guarantee gap payment} (read off the two masked worlds: task 0 has one accepted dispute, on a cleaning line of a Standard Deposit Plan account; task 1 has three accepted disputes, on carpet/repair/fob lines of a Zero-Deposit Guarantee Plan account). These two scopes are disjoint and together cover all six extended policies. The GT-side `charter_scope` is compared after the reveal in each task file.
- Asymmetric gating (observation O-4): the settlement payment waits only on cleaning credits; the gap payment waits only on carpet, repair and fob credits. On a cash-deposit account with an accepted carpet dispute, or a guarantee account with an accepted cleaning dispute, no rule orders the payment against that credit, and the two orders give two balances. Neither task world contains such a combination, so no consequence is demonstrable here.

### rule_compute_equivalence

Mechanical sweep: every `compute_basis` quotation of every extended policy is a verbatim substring of that policy's `rule`; every sentence of every `baseline.rule` is a verbatim sentence of the `rule`; every overwrite `replaced_by` is verbatim in the extended rule and every `superseded_clause` is verbatim in the named base rule (script output recorded by the auditor; script deleted). Sentence-by-sentence semantic sweep, per policy:

- **deposit_ext_cleaning_correction_credit** — cleaning_charged (SUM of all cleaning lines, whole-unit and spot) = rule; spot_rooms = cleaning lines less whole-unit lines = "each room that carries a spot-cleaning line"; unit_rate ladder = the six floor-plan sentences; spot_rate = dog / cat-no-dog / neither; surface_share = both / one / neither; tenure_months = `MONTHS(lease.move_in_date, move_out_date)` = "full months from the lease's move-in date to its move-out date"; returns_12m = `XCOUNT(... within_months=12, date_field='payment_date', event_type='lease_payment_return')`, whose window `0 <= MONTHS(d, NOW) < 12` equals "fewer than twelve full months before the handling date"; heavy_use_charge = +2 or more / exactly +1 / none. **One gap (finding F-1): the acting base of the cleaning courtesy.** The rule defines the courtesy as "a share of the whole-unit cleaning rate that is not charged", and the whole-unit cleaning rate is the floor-plan rate ("The whole-unit cleaning rate follows the lease's floor plan: ... rate_three_bedroom for the Three-Bedroom Residence ..."); the closing sentence says "the whole-unit cleaning rate multiplied by the surfaces multiplier, then reduced by the cleaning courtesy". `compute` implements `unit_rate * surface_share * (1 - cleaning_courtesy)` — the share acting on the surface-adjusted amount. The literal rule equally supports `unit_rate * surface_share - cleaning_courtesy * unit_rate` — the share acting on the whole-unit cleaning rate as defined. No `compute_basis` quotation fixes which base the share acts on.
- **deposit_ext_settlement_payment** — billed/paid/credited/standing = the standing sentence; late_fees_24m window = "twenty-four full months before the handling date"; settlement_rate (no fee + autopay / exactly one + autopay / other); rate_step (closed & 0 / final_billing & 0 / other); allowance_ceiling on `DAYS(NOW, balance_due_date)` (>=14 / 7-13 / <7); settlement_base (accepted & statement > disposition_statement_days -> billed; accepted & within -> billed - credited; none -> standing); allowance = `MN(ceiling, RND(base * (rate + step)))`; result = standing - allowance. All equivalent.
- **deposit_ext_carpet_depreciation_credit** — carpet life (>=4 occupants / exactly 3 / fewer), animal cut (dog / cat-no-dog / none), life_used = life - cut, remaining share = max(0, life - age)/life, age band on age/life (>=0.75 / >=0.50 / younger), wear allowance (tenure >=48 & 0 late fees / exactly 1 / other), cost cap by floor plan, traffic share by room, `corrected = cost_basis * remaining * band * traffic * (1 - allowance)`. The allowance is "a share of the corrected carpet charge", so its acting base is the whole product — equivalent.
- **deposit_ext_repair_labor_credit** — labor rate (tenure & returns), billable hours (late & photos -> `int()` = rounded down; late & no photos -> `MN(hours, 2.0)`; within -> recorded), parts share by room, notice discount on `DAYS(notice_to_vacate_date of the completed term, move_out_date)`, goodwill on `DAYS(disposition_date, latest dispute created_at)`, `corrected = billable * rate * (1 - notice) + parts * share`, credit = charged - corrected + goodwill. Equivalent. Observation O-5: "the last term of the lease" is implemented as the term with `status='completed'`; equal whenever the lease has exactly one completed term (true in both worlds).
- **deposit_ext_fob_count_credit** — allotment (bought > 0 -> issued + bought; none bought -> issued; no allotment -> recorded count), countable = min(count, allotment), per-fob rate by parking product, courtesy by autopay/insurance, timing share on `DAYS(move_out, disposition)` (>25 / >20 / within), `corrected = max(0, countable * rate * share - courtesy)`. Equivalent except observation O-6: "the fobs bought" is implemented as `XCOUNT` of `key_fob_replacement_fee` lines, while the lease charter bills "one line for all fobs issued the same day" (`products/lease.yaml`, fee rule) — a line can stand for more than one fob. Not demonstrable in task 1 (the one line is 75.00 = one fob at `key_fob_replacement_fee` 75.00).
- **deposit_ext_guarantee_gap_payment** — standing; coverage multiple on the count of premium rows (>=4 / 2-3 / fewer); adult step (>=3 / 2 / 1); coverage rent (last term `month_to_month_conversion` -> `lease.monthly_rent`; `transfer` -> the transfer term's contracted rent; else the new-lease term's contracted rent); continuity share on `MONTHS(last premium, move_out)` (>=24 -> 0; 12-23 -> 0.50; <12 -> 1); shared limit (utility balance > 0 -> it; else parking balance > 0 -> it; else 0); `coverage = RND((multiple + step) * rent * share - limit)`; gap = `max(0, standing - coverage)`. Equivalent; observation O-5 applies to "the last term" here as well.

Rounding: `RND` is Python `round`, the rule says half up; every intermediate the auditor recomputed in the two worlds is away from a half-cent tie, so no consequence.

### action_binding_and_uuids

- Each `(target_tool, computes)` pair is claimed by exactly one extended policy (six policies, six distinct tools, all `computes: amount`); base policies claim none of the six tools.
- uuid8s: `249da733`, `cadbabf4`, `f675d6ed`, `05a989cb`, `b88884f4`, `4e6273ca` — pairwise distinct, no shared prefix or tail, no sequence pattern.
- Function bodies: each tool creates one `deposit_transactions` row with the values passed (credits: `deposit_balance_credit` / `dispute_credit` with `source_transaction_id`; payments: `deposit_balance_payment` / `balance_payment` with the instrument and an `LRT-` confirmation). None reads history, computes, validates, refuses, or checks a prerequisite.
- Docstrings name no other tool and no position in a sequence relative to another write. Observation O-7: the four credit docstrings each contain "after" ("lowers its balance owed after a disputed cleaning line is corrected", likewise "re-depreciated", "re-priced", "recounted"); the clause describes the credit's own occasion (the correction the credit is), not an order against another problem of the tree, so no ordering between tree nodes leaks.
- Observation O-8: the settlement rule says the resident makes the payment "in person" and the gap rule "may pay in person"; both tool docstrings say "through the resident portal". Read together, "in person" means by the resident themself (owner=user), which the tools honour; no second action reading results.

### prerequisite_graph

- `prerequisite` is filled in on all six policies: `[]` on the four credits; one edge on the settlement payment; three edges on the gap payment.
- Every `problem` names an extended policy id in this file, none names a base policy or itself; the graph (cleaning -> settlement; carpet, repair, fob -> gap) is acyclic, depth 1.
- Every `policy_source` is verbatim in its own policy's `rule` (checked mechanically).
- All four edges are `form: state`, none carries `fallback_reason` — correct.
- `kind: value_input`, `gate: credited` names a binding of the settlement compute; `gate: gap_credited` names a binding of the gap compute. Both genuinely exist and each credit row enters that SUM.
- `resolved_by` equals the depended-on policy's `target_tool` on all four edges; the tool writes a `deposit_balance_credit` row with `source_transaction_id` = the disputed line, which is exactly what the `condition` checks.
- `condition` restates the prerequisite sentence at the same strength (every accepted dispute on a line of that category -> a dispute credit whose source is that line); no authoring-viewpoint phrasing.

### prerequisite_sentences

| edge | sentence (own rule) | connective | form test |
| --- | --- | --- | --- |
| settlement <- cleaning | "A settlement payment is taken only after every cleaning line under an accepted dispute carries its dispute credit on the account." | only after | state: a dispute row with `dispute_status` accepted on a cleaning line + a dispute credit whose source line is that line — both record-visible through `find_deposit_disputes` / `find_deposit_transactions` (the latter searchable by `source_transaction_id`) |
| gap <- carpet | "The guarantee gap payment is taken only after every carpet replacement line under an accepted dispute carries its dispute credit on the account." | only after | state, same record shape |
| gap <- repair | "The guarantee gap payment is not taken until every damage repair line under an accepted dispute carries its dispute credit on the account." | not until | state, same record shape |
| gap <- fob | "Before the guarantee gap payment is taken, every unreturned-fob line under an accepted dispute must carry its dispute credit on the account." | before | state, same record shape |

- None names a tool, a policy id, a snake_case token or a row id; each is scoped "every ... line under an accepted dispute", the same scope as its `condition`.
- One write per state: the only rule that puts a dispute credit on a cleaning line is `deposit_ext_cleaning_correction_credit` ("credited against the balance owed by one dispute credit posted against the disputed cleaning line"); likewise carpet, repair and fob each have exactly one extended rule that posts a dispute credit against that line category. Base `deposit_disputes_and_amendment` also mentions a `dispute_credit`, but its "withdraws the line in full" path is superseded for these four line categories by declared overwrites, and no tool of this difficulty writes a `deposit_charge_reversal`. Single reading: prerequisite sentence -> find the accepted dispute on the line -> the extended rule whose first sentence is "A [cleaning / carpet replacement / damage repair / unreturned-fob] line under a dispute accepted ... is credited ... by one dispute credit posted against the disputed ... line" -> that policy's write.
- The depended-on rules do not restate the sentences; no rule carries a second wording of an edge.
- Cross-problem orders stated without an edge: the gap rule's "may pay in person, before the guarantee is claimed" and the settlement rule's "what the allowance leaves unpaid is written off by a small-balance write-off credit once the balance owed falls due" each place the payment against a base write (guarantee claim, small-balance write-off). Both are time-bounded by base (the claim is `guarantee_claim_waiting_days` after the due date; the write-off is "once due"), so the reverse order cannot be executed before the due date and no second terminal state exists at a pre-due handling time — observation O-9.

### override_declarations

Sentence-by-sentence against each `base_policy_refs` entry (findings only):

- **cleaning credit** vs `deposit_disputes_and_amendment`: "withdraws the line in full" — superseded, declared. "the amount that the withdrawn line had taken from the deposit is refunded, and the part that sat in the balance owed is credited by a dispute_credit" — conditioned on a withdrawn line, which no longer exists for this line category; the replaced_by routes the whole excess to one dispute credit against the balance owed. Consistent (observation O-10 in the task file where the deposit was applied as one move_out_charges group). "reopens the account ... a corrected statement follows" — inherited, no tool (O-3). "accepted only when the line breaks the itemization rule — it charges normal wear and tear, lacks required photos, misapplies depreciation or labor, or charges an item corrected after the pre-move-out inspection" — the extended grounds "cleaning charge was misapplied" and "fob count was misapplied" are not in the dash list but are breaches of the itemization rule; acceptance is already recorded in `deposit_disputes.dispute_status`, so the agent decides nothing here (observation O-11). vs `deposit_move_out_itemization`: "at cleaning_charge_by_floor_plan for the lease's floor plan" and "stains beyond normal cleaning add carpet_spot_cleaning_per_room per room" — superseded, declared. vs `deposit_balance_and_collections`: nothing it governs is changed.
- **settlement payment** (`overwrite: []`) vs `deposit_balance_and_collections`: "A balance owed is due ... and may be paid by any lease instrument" — followed. "A balance owed at or below small_balance_write_off once due is written off" — followed and relied on (the allowance ceiling never exceeds `small_balance_write_off`, so the unpaid remainder is exactly the base write-off). vs `deposit_disposition_timing`: `disposition_statement_days` is read as defined. No undeclared override.
- **carpet credit**: "withdraws the line in full" and the straight-line depreciation sentence — superseded, declared. "an item at or past its useful life is never charged" — followed (`MX(0, ...)`).
- **repair credit**: "withdraws the line in full" (with goodwill folded into the credit) and the damage_repair sentence — superseded, declared.
- **fob credit**: "withdraws the line in full" and "Unreturned fobs are quantity times unreturned_fob_charge" — superseded, declared.
- **gap payment** vs `deposit_balance_and_collections`: the coverage sentence — superseded, declared. vs `deposit_evt_funding`: "The guarantee premium is guarantee_premium_pct_of_coverage times the coverage (guarantee_coverage_rent_multiple times monthly_rent)" — defines "the coverage" for the premium, with `monthly_rent` rather than "at move-in"; not superseded, and not the quantity the gap scores (observation O-12).
- Disguised forms: the gap's premium-continuity share of 0 is a 0/1-type multiplier on the coverage, but it sits inside the declared replaced_by ("times the premium-continuity share"). No anonymous intermediate or dropped branch found.

### factor_ladders

| policy | factor | label | honest? | tiers | multi-source | cross_difficulty |
| --- | --- | --- | --- | --- | --- | --- |
| cleaning | whole_unit_rate_by_floor_plan | parameter | yes | 6 | no | lease |
| cleaning | spot_cleaning_rate_by_animal | parameter | yes | 3 | yes (dog; cat and not dog) | pet |
| cleaning | surfaces_left_in_place | method | **no** — each tier multiplies the same rate by a number (0.80 / 0.90 / 1) | 3 | yes | — |
| cleaning | tenancy_cleaning_courtesy | parameter | yes | 3 | yes (tenure and returns) | lease |
| cleaning | heavy_use_cleaning_charge | parameter | yes | 3 | yes (occupants vs floor-plan bedrooms) | lease |
| settlement | late_fee_record_rate | parameter | yes | 3 | yes (late fees and autopay) | lease |
| settlement | squared_utility_step | parameter | yes | 3 | yes (status and balance) | utility |
| settlement | early_payment_ceiling | parameter | yes | 3 | no | — |
| settlement | dispute_history_base | method | yes — each tier picks a different aggregate as the base | 3 | yes | — |
| carpet | occupancy_carpet_life | parameter | yes | 3 | no | lease |
| carpet | animal_carpet_life_cut | parameter | yes | 3 | yes | pet |
| carpet | carpet_age_band | method | **no** — each tier multiplies the remaining share by a number (0.50 / 0.75 / 1) | 3 | no | — |
| carpet | tenancy_carpet_wear_allowance | parameter | yes | 3 | yes | lease |
| carpet | like_for_like_carpet_cost | parameter | yes | 3 | no | lease |
| carpet | carpet_room_traffic | parameter | yes | 3 | no | — |
| repair | tenancy_labor_rate | parameter | yes | 3 | yes | lease |
| repair | documented_billable_hours | method | yes — floor / cap / as recorded | 3 | yes | — |
| repair | repaired_room_parts_share | parameter | yes | 3 | no | — |
| repair | notice_labor_discount | parameter | yes | 3 | no | term |
| repair | prompt_dispute_goodwill | parameter | yes | 3 | no | — |
| fob | household_fob_allotment | parameter | yes, but **third tier unreachable** | 3 stated / 2 reachable | no | lease |
| fob | parking_access_fob_charge | parameter | yes | 3 | no | parking |
| fob | good_order_fob_courtesy | parameter | yes | 3 | yes | lease |
| fob | statement_timing_fob_share | method | **no** — each tier multiplies the same charge by a number (0.50 / 0.75 / 1) | 3 | no | — |
| gap | premium_terms_multiple | parameter | yes | 3 | no | — |
| gap | co_leaseholder_step | parameter | yes | 3 | no | lease |
| gap | tenancy_end_coverage_rent | method | accepted — each tier reads the rent from a different record (lease vs transfer term vs first term) | 3 | no | term |
| gap | premium_continuity_share | parameter | yes | 3 | no | — |
| gap | shared_ledger_limit | method | accepted — each tier subtracts a different ledger's balance | 3 | partly (tier 2 is a conjunction) | utility |

Structure checks:

- Counts per policy: 5 / 4 / 6 / 5 / 4 / 5 factors (all within 4–6); `parameter` >= 2 everywhere. `decides` is never `result`; binding sets are disjoint within each policy.
- Every tier is stated in the rule (condition and value/method) and implemented as a branch of its `decides` binding; no tier lives only in `compute`. Every fall-through equals the factor's `baseline` and the baseline value named by `baseline.rule`.
- No two tiers of one ladder select the same value or method (checked value by value against `params`).
- Per task, at least one multi-source and one cross-difficulty factor exist (cleaning/settlement: courtesy, late-fee rate, utility step; carpet/repair/fob/gap: wear allowance, labor rate, fob courtesy; cross: lease, pet, utility, term, parking).
- **Finding F-2 (mislabelled method)**: `surfaces_left_in_place`, `carpet_age_band` and `statement_timing_fob_share` are labelled `method`, but each tier only substitutes a different number into one unchanged formula (`unit_rate * surface_share`, `remaining_share * age_band_factor`, `countable * rate * fob_timing_share`) — the definition of a `parameter`. Each of these is the only `method` factor of its policy, so the cleaning, carpet and fob computations have no honest `method` factor.
- **Finding F-3 (unreachable fall-through)**: `household_fob_allotment`'s third tier, "the recorded count when the floor plan carries no fob allotment", can never hold: every floor plan in `products/lease.yaml` carries `fobs_issued_at_move_in` (Studio 2, One-Bedroom 2, One-Bedroom Den 3, Two-Bedroom 4, Three-Bedroom 5, Penthouse 5), and `compute` reaches that branch only when `CPARAM('lease','fobs_issued_at_move_in')` is `None`, i.e. when the customer has no lease. The ladder has two reachable tiers, and its fall-through (the baseline) is a treatment no customer can receive.
- **Finding F-4 (straw-man baseline)**: `whole_unit_rate_by_floor_plan`'s baseline "The whole-unit cleaning rate is rate_standard" (195.00 for every floor plan) is not a standard the business uses. Larkspur's own base rule prices whole-unit cleaning by floor plan (`deposit_move_out_itemization`: "at cleaning_charge_by_floor_plan for the lease's floor plan", with `cleaning_charge_by_floor_plan` {Studio 125, One-Bedroom 150, One-Bedroom Den 165, Two-Bedroom 195, Three-Bedroom 235, Penthouse 295}). The extended `rate_*` params repeat that schedule value for value. So the "factor" is the base schedule under another name, and its baseline is a flat rate no Larkspur document applies.
- Realism of the other ladders (conditions weighed, outcomes published): occupancy- and pet-shortened carpet life, age-banded depreciation, like-for-like cost caps, room-traffic shares, tenure-based labor rates, late-itemization hour rules, notice discounts, fob allotments and garage fob pricing, statement-timing reductions, premium-count coverage, co-signer steps, tenancy-end coverage rent, premium-lapse shares and shared ledger limits are all treatments a multifamily operator or a deposit-guarantee provider could plausibly publish. No other condition holds of every customer reaching its write, and no other outcome is unreal.

### findings

- **F-1 — SOURCE-POLICY RED (rule_compute_equivalence, acting base).** Symptom: the cleaning courtesy's acting base is not fixed by the rule. Root cause: the rule says the courtesy is "a share of the whole-unit cleaning rate that is not charged", while the closing sentence applies it "then" after the surfaces multiplier; `compute` picks `unit_rate * surface_share * (1 - courtesy)`. Evidence: `deposit.extended.yaml`, policy `deposit_ext_cleaning_correction_credit`, rule sentences quoted above; `compute.corrected_cleaning`; `compute_basis.cleaning_courtesy` quotes only the ladder. Consequence: whenever the surfaces multiplier is below 1 and the courtesy is non-zero, the two readings differ. **Bears on task 0** (its file demonstrates the two values).
- **F-2 — SOURCE-FACTOR RED (mislabelled effect; no honest `method` factor).** `surfaces_left_in_place` (cleaning), `carpet_age_band` (carpet), `statement_timing_fob_share` (fob). **Bears on task 0 (cleaning) and task 1 (carpet, fob).**
- **F-3 — SOURCE-FACTOR RED (ladder with an unreachable tier).** `household_fob_allotment`. Leaving it out, the fob computation keeps 3 factors (below the floor of 4). **Bears on task 1.**
- **F-4 — SOURCE-FACTOR RED (straw-man baseline).** `whole_unit_rate_by_floor_plan`. **Bears on task 0.**
- Observations (not grounds for rework): O-3 inherited "a corrected statement follows" with no tool; O-4 asymmetric payment gating; O-5 "last term" as `status='completed'`; O-6 fobs bought counted as lines; O-7 "after" in credit docstrings; O-8 "in person" vs portal; O-9 payment-vs-base-write orders bounded by time; O-11 dispute grounds outside the base dash list; O-12 the premium's "coverage" definition in base funding.

## closing_checklist

Written after both reveals (task 0 at 2026-09-24T18:20:33Z; task 1 finished at about 18:21Z). Everything above this heading was written before any reveal.

- Per-task files: `0.md` and `1.md` correspond one-to-one with `tasks/0.json` and `tasks/1.json`. This is revision 1, with no older revisions. Both comparison sections are written, but **neither carries a full PASS**:
  - task 0: SOURCE-POLICY RED (F-1), SOURCE-FACTOR RED (F-2, F-4), SOURCE-TASK RED (F-1); problem tree PASS.
  - task 1: SOURCE-FACTOR RED (F-2, F-3); policy self-consistency, problem tree and unique solution PASS.
- Coverage and scopes: GT `charter_scope` is task 0 = {cleaning credit, settlement payment} and task 1 = {carpet, repair and fob credits, gap payment}. The two are disjoint and together cover all six extended policies and six task tools. Task tools and GT are closed (each GT write calls its scope's tools). uuid8s are independent (§ action_binding_and_uuids).
- Trees:
  - task 0: 1 prerequisite problem, 1 `value_input` edge.
  - task 1: 3 prerequisite problems, 3 `value_input` edges.
  - Each task has one `owner=user` root. The difficulty-wide `prerequisite` graph is acyclic (depth 1), and no edge crosses a task boundary.
- Factors — **not closed**:
  - F-2: the cleaning, carpet and fob computations have no honest `method` factor.
  - F-3: the fob allotment ladder has an unreachable tier, leaving 3 factors.
  - F-4: the cleaning floor-plan factor rests on a straw-man baseline.
  - Every declared factor bears weight on its task's world against its declared baseline, and every baseline alone gives a definite number that differs from gold: 100.00, 481.87, 740.00, 105.00, 0.00 and 0.00 vs the gold values.
- Unique solution — **not closed** for task 0 (F-1: 55.80/461.74 vs 60.50/457.04).
- Gates: the instantiation-stage gate snapshot supplied with the brief (all green; traceability deferred to render) is the one on the final form. The auditor did not re-run the gates, per the entry-condition rule. The artifacts were not edited by this audit, so that snapshot still describes them (charter and tool hashes unchanged at `26b3f78d…` / `92f68af4…`).

**Difficulty result: does not pass the source-layer audit.** Per-task verdicts:

- task 0: SOURCE-POLICY RED + SOURCE-FACTOR RED + SOURCE-TASK RED
- task 1: SOURCE-FACTOR RED

## revision_2

### charter_global_frozen (revision 2)

- Re-audit round 2, requested by the coordinator after the rework. The round-1 text above is left untouched.
- Inputs moved, so every charter-global section is re-derived in full:
  - `deposit.extended.yaml`: `26b3f78d…` -> `395c83176b8b429b6ac9178770e29cbc5048390e80adcb31adc0d03a7f0c808f`
  - `task_tools.py`: `92f68af4…` -> `2cec715657c5a1aad7aa65c9516d1eb3fa9d47624dc53fa235e7b0b1210746f0`
- Masked views r2 (re-hashed by the auditor, equal to the brief): `r2/0.json` `5c13648d…0944524`, `r2/1.json` `e4c62aba…3af81`.
- This section is written before any round-2 reveal. Its only sources are the charter, `blueprint/`, the tool module and the check_compute evaluator semantics. The reworker's claims were taken as item ids only and each was verified against the artifacts.
- Gate snapshot (coordinator, after rework): EXTENDED / TASK TOOL CONTRACT / REPLAY / SOLVABILITY / COMPUTE / GROUNDING / SCOPE all OK; traceability deferred. The replay excerpt again shows only the `1.json` row (observation, as in round 1).

### policy_conflict_scan (r2)

- The base section still equals `blueprint/products/deposit.yaml` key for key; the only extra key is `extended_policies`.
- The six extended policies keep the same ids, subjects, `computes` and target tools. The partitions are unchanged:
  - the four credits split by disputed line category;
  - the two payments split by program (cash deposit vs Zero-Deposit Guarantee Plan).
- Triggers, time anchors and terminal states are unchanged. Every write is still one `deposit_transactions` row.
- O-3 (inherited "a corrected statement follows", no tool) and O-4 (asymmetric payment gating) still hold unchanged. Neither is demonstrable in the r2 worlds, which keep one cleaning dispute on the cash account and three carpet/repair/fob disputes on the guarantee account. Both remain observations.

### rule_compute_equivalence (r2)

Mechanical sweep: every `compute_basis` quotation is verbatim in its rule; every compute binding has a basis; every `baseline.rule` sentence is a rule sentence; every overwrite `replaced_by` is verbatim in the extended rule and every `superseded_clause` is verbatim in the named base rule.

Semantic sweep of what changed:

- **Cleaning credit.**
  - Rule: "A long tenancy earns a cleaning courtesy, a share of the whole-unit cleaning charge as reckoned on the surfaces left in place that is not charged". Closing sentence: "the whole-unit cleaning charge less the cleaning courtesy taken on that same whole-unit cleaning charge".
  - `compute.corrected_cleaning` = `whole_unit_charge - whole_unit_charge * cleaning_courtesy + spot_rooms * spot_rate + heavy_use_charge - notice_cleaning_discount`. The courtesy's acting base is now fixed by the rule and matches compute. **F-1 closed.**
  - New binding `smaller_plan_rate` implements "the next smaller floor plan (the Studio Residence keeps its own rate)". It follows the charter's floor-plan order: Studio < One-Bedroom < One-Bedroom Den < Two-Bedroom < Three-Bedroom < Penthouse.
  - Observation O-18: the rule does not state that order. The only non-obvious step is Penthouse -> Three-Bedroom (both have 3 bedrooms). It is reachable only for a Penthouse lease; neither world has one.
  - New `notice_cleaning_discount` reads the completed last term's `notice_to_vacate_date` — equivalent to the rule.
- **Carpet credit.** The age band now selects a depreciation convention, and `compute.remaining_share` matches the rule for each tier:
  - declining: straight-line share squared;
  - whole-year: age rounded up to a multiple of 12, `((age + 11) // 12) * 12`, before the straight-line share;
  - straight-line on the recorded age.
  - Observation O-19: "rounded up to the next whole multiple" is read by compute as a ceiling, so an age already on a multiple of 12 stays put. A reader who takes "next" strictly would add 12. This matters only at an exact multiple; the disputed carpet in task 1 is 30 months.
  - The dog cut now says "as a pet or as an assistance animal", which settles O-16.
- **Fob credit.**
  - "The fobs bought being the key fob fees billed on the lease ledger divided by the floor plan's key_fob_replacement_fee" = `int(RND(XSUM(key_fob_replacement_fee amounts) / CPARAM(key_fob_replacement_fee), 0))`. This settles O-6.
  - Allotment ladder: bought -> issued + bought; none bought and a parking license held -> issued + `gate_fobs_with_license`; none bought and no license -> issued.
  - The statement-timing tier now changes how fobs are reckoned: halved and floored / one fewer, never below 0 / as counted = `reckoned_fobs`.
  - All equivalent to the rule.
- **Repair, gap and cleaning wording.** "the lease's completed last term" now names what `status='completed'` implements. O-5 settled.
- **Settlement and gap wording.** "the resident makes themself, through the resident portal" / "may pay themself, through the resident portal". O-8 settled.

### action_binding_and_uuids (r2)

- Tools, owners and uuid8s are unchanged: `249da733`, `cadbabf4`, `f675d6ed`, `05a989cb`, `b88884f4`, `4e6273ca`. They are distinct and not batch-derived.
- Function bodies still create one row with the passed values and judge nothing.
- The credit docstrings now read "lowers its balance owed on account of a disputed … line that was corrected / re-depreciated / re-priced / recounted", so "after" is gone. **O-7 settled.**
- The only remaining ordering word is "rounded half up to the cent before it is passed / paid", a rounding instruction that was also present in round 1 and involves no other write.

### prerequisite_graph and prerequisite_sentences (r2)

- The four edges are unchanged: same problems, `value_input`, gates `credited` / `gap_credited`, form `state`, same `resolved_by`. Each `policy_source` is still verbatim in its own rule.
- The graph is still acyclic, and the one-write-per-state derivation of round 1 still holds.
- O-9 (the payments placed before base time-bounded writes) still holds unchanged as an observation.

### override_declarations (r2)

- **Cleaning.** It still supersedes "withdraws the line in full", "stains beyond normal cleaning add carpet_spot_cleaning_per_room per room" and "at cleaning_charge_by_floor_plan for the lease's floor plan", each declared. The replacing closing sentence now includes the courtesy base and the notice discount.
- **Carpet.** The depreciation sentence is superseded; the replaced_by now names "under its age-band convention". Declared.
- **Fob.** "Unreturned fobs are quantity times unreturned_fob_charge" is superseded by the reckoned-fobs sentence. Declared.
- **Repair, gap and settlement.** Unchanged.
- No undeclared override was found. O-10, O-11 and O-12 are unchanged observations.

### factor_ladders (r2)

| policy | factor | label | honest? | tiers reachable | notes |
| --- | --- | --- | --- | --- | --- |
| cleaning | surfaces_left_in_place | method | **yes** — next-smaller-plan lookup vs average of two schedule entries vs own entry | 3 | replaces the round-1 multiplier; F-2 closed for cleaning |
| cleaning | spot_cleaning_rate_by_animal | parameter | yes | 3 | pet |
| cleaning | tenancy_cleaning_courtesy | parameter | yes | 3 | lease; multi-source |
| cleaning | heavy_use_cleaning_charge | parameter | yes | 3 | lease |
| cleaning | notice_cleaning_discount | parameter | yes | 3 | term (new) |
| settlement | (4 factors, unchanged) | 3 parameter + 1 method | yes | 3 each | unchanged |
| carpet | carpet_age_band | method | **yes** — declining (square) / whole-year rounding / straight-line | 3 | F-2 closed for carpet |
| carpet | other 5 | parameter | yes | 3 each | traffic_heavy now 0.88, allow_clean 0.12 |
| repair | (5 factors, unchanged) | 4 parameter + 1 method | yes | 3 each | unchanged |
| fob | household_fob_allotment | parameter | yes | 3 reachable | the dead "no fob allotment" tier is gone; F-3 closed as stated. **See N-1** |
| fob | parking_access_fob_charge | parameter | yes | 3 | parking |
| fob | good_order_fob_courtesy | parameter | yes | 3 | lease |
| fob | statement_timing_fob_reckoning | method | **yes** — halve and floor / subtract one, floored at 0 / identity | 3 | F-2 closed for fob |
| gap | (5 factors, unchanged) | 3 parameter + 2 method | accepted | 3 each | unchanged |

- **F-4 closed.** The cleaning floor-plan factor is removed. The baseline "The whole-unit cleaning charge is the floor plan's cleaning rate: rate_studio … rate_penthouse" is now the business's own base schedule (`cleaning_charge_by_floor_plan`, same values), so the baseline is honest.
- Counts: cleaning 5 (4 parameter / 1 method), settlement 4 (3/1), carpet 6 (5/1), repair 5 (4/1), fob 4 (3/1), gap 5 (3/2). Every fall-through equals its factor's baseline and the value `baseline.rule` states. No two tiers of one ladder share a value or method.
- **N-1 — new defect, SOURCE-FACTOR RED (unreal compound condition in `household_fob_allotment`).**
  - The rule itself says a gate fob is "issued with the license": `gate_fobs_with_license` gate fob per parking license.
  - Yet the ladder counts that fob only "when no fob was bought and the household held a parking license". When fobs were bought, the allotment is "the fobs issued at move-in plus the fobs bought", and the license's gate fob drops out.
  - The "no fob was bought" part of tier 2's compound condition is not something an operator weighs when deciding whether the gate fob that came with a parking license was held. Buying an extra or replacement fob on the lease ledger does not take back the license's gate fob.
  - Tier 1's outcome is therefore a count no operator would publish for a household that both bought a fob and held a license. That household holds issued + bought + the license fob.
  - Bears on task 1, whose world has exactly that combination. The demonstration is in `1.md` revision_2.

### findings (r2)

- F-1: **closed** (acting base now fixed in the rule and matched by compute).
- F-2: **closed** for cleaning, carpet and fob (each `method` factor now changes the algorithm).
- F-3: **closed** (every allotment tier is reachable). N-1 is a new defect in the same factor.
- F-4: **closed** (honest baseline equal to the base schedule).
- Observations settled: O-5, O-6, O-7, O-8, O-16 (charter wording), O-13 and O-15 (task worlds, verified in the task files).
- Observations unchanged and still accepted as observations: O-3, O-4, O-9, O-10, O-11, O-12; O-14 and O-17 are per-task.
- New observations: O-18 (floor-plan order for "next smaller"), O-19 (ceiling at an exact multiple of 12).
- **N-1: SOURCE-FACTOR RED, bears on task 1.**

### closing_checklist (revision 2)

Written after both r2 reveals (task 0 at 18:36:30Z, task 1 at 18:36:51Z). Everything in revision_2 above this heading was written before them.

- Per-task files carry a revision_2 section each; the round-1 text is preserved.
  - `0.md` revision_2: **PASS** on all four relationships.
  - `1.md` revision_2: **SOURCE-FACTOR RED (N-1)**; the other three relationships PASS.
- Round-1 REDs: F-1, F-2 (cleaning / carpet / fob), F-3 and F-4 are closed. Each closure was verified against the charter and the r2 worlds, not taken from the reworker's claim.
- Scopes: GT `charter_scope` is unchanged, disjoint, and covers all six policies and six tools. uuid8s are unchanged and independent.
- Trees: task 0 has 1 prerequisite and 1 value_input edge; task 1 has 3 and 3. Each has a user-owned root. The graph is acyclic and no edge crosses a task.
- Factors: every declared factor bears weight against an honest baseline on its task's world. Baseline-alone numbers vs gold:

  | computation | baseline alone | gold |
  | --- | --- | --- |
  | cleaning | 60.00 | 64.50 |
  | settlement | 473.26 | 453.04 |
  | carpet | 740.00 | 1238.00 |
  | repair | 105.00 | 226.50 |
  | fob | 150.00 | 145.00 |
  | gap | 0.00 | 91.34 |

  **Not closed: N-1** (fob allotment ladder, task 1).
- Gates: the coordinator's post-rework snapshot is all green (traceability deferred). The auditor did not re-run the gates and edited no artifact.

**Difficulty result (revision 2): does not yet pass the source-layer audit** — task 0 PASS; task 1 SOURCE-FACTOR RED (N-1).

## revision_3

### charter_global_frozen (revision 3)

- Round-3 re-audit. Revisions 1 and 2 above are untouched.
- Shared inputs:
  - `deposit.extended.yaml` moved: `395c8317…` -> `a21e9261988e797b1da7cc03f793bf068aed3818711f83adb3f67fd4fe7eb76f`. The charter-global sections are re-derived below.
  - `task_tools.py` is unchanged at `2cec715657c5a1aad7aa65c9516d1eb3fa9d47624dc53fa235e7b0b1210746f0`. § action_binding_and_uuids (r2) is carried forward by reference, on the ground that the tool hash is equal.
- Views: `r3/0.json` `6adae611…` and `r3/1.json` `e4c62aba…`, re-hashed by the auditor. `r3/1.json` is byte-identical to `r2/1.json`.
- Written before any round-3 reveal, from the charter, `blueprint/` and the evaluator semantics only.
- Gate snapshot (coordinator, post-rework): all green; traceability deferred.

### what moved in the charter (verified, not taken from the claims)

- The base section still equals `blueprint/products/deposit.yaml`.
- The settlement, repair and gap policies read identically to r2: same params, rule text, factors and prerequisite edges.
- Mechanical sweep, all clean:
  - every `compute_basis` quotation is verbatim in its rule;
  - every binding has a basis;
  - every `baseline.rule` sentence is a rule sentence;
  - all four prerequisite `policy_source` sentences are verbatim in their own rules;
  - every overwrite `replaced_by` / `superseded_clause` is verbatim on its side.
- **Cleaning credit.**
  - The surfaces sentence now states the order: "floor plans run, from smallest to largest, Studio Residence, One-Bedroom Residence, One-Bedroom Den Residence, Two-Bedroom Residence, Three-Bedroom Residence, Penthouse Residence, and the Studio Residence keeps its own rate".
  - `compute.smaller_plan_rate` follows exactly that order.
  - **O-18 settled.**
  - Nothing else in the policy moved.
- **Carpet credit.**
  - The whole-year convention now reads "its age being rounded up to a whole multiple of age_year_months months, an age already on a whole multiple staying as it is".
  - That is exactly the ceiling `((age + 11) // 12) * 12` in `compute.remaining_share`.
  - **O-19 settled.**
- **Fob credit.**
  - The fobs held are now one sentence with no ladder: "the floor plan's fobs issued at move-in, plus the fobs bought on the lease ledger during the tenancy … plus gate_fobs_with_license gate fob issued with a parking license when the household held one".
  - `compute.fob_allotment` = `fobs_issued + fobs_bought + (gate fob if a parking license is held)`.
  - The license's gate fob no longer depends on whether a fob was bought. **N-1 closed.**
  - The same sentence is now part of the baseline, and it describes what a household actually holds, so the baseline is honest.
  - `household_fob_allotment` is withdrawn as a factor and replaced by `tenancy_fob_forgiveness` (parameter; `forgiven_fobs`):
    - forgiven_fobs_long = 1 fob for a tenancy of at least 48 full months;
    - forgiven_fobs_mid = 0.5 of a fob for 24–47 months;
    - none below 24 months.
  - The rule states the whole ladder, including "taken off the reckoned fobs", and the closing sentence reads "the reckoned fobs less the forgiven fobs, times the per-fob charge, less the fob courtesy, never below 0".
  - The dispute ground changed from "fob count was misapplied" to "fob charge was misapplied", in the rule and in the overwrite `replaced_by` alike. The superseded base clause is still "withdraws the line in full". As in round 1 (O-11), acceptance is recorded in `deposit_disputes`, so this changes no decision.

### factor_ladders (r3, fob only; all other policies as in r2)

| factor | label | honest? | tiers | notes |
| --- | --- | --- | --- | --- |
| tenancy_fob_forgiveness | parameter | yes (a count of forgiven fobs) | 3, disjoint, all reachable | lease (move-in date) |
| parking_access_fob_charge | parameter | yes | 3 | parking |
| good_order_fob_courtesy | parameter | yes | 3 | lease |
| statement_timing_fob_reckoning | method | yes (halve and floor / subtract one / identity) | 3 | unchanged from r2 |

- Counts: 4 factors, 3 parameter and 1 method. Each fall-through equals its baseline; no two tiers share a value.
- Realism:
  - Tenancy-based forgiveness of unreturned-fob charges is a plausible retention courtesy.
  - Observation O-20: "forgiven_fobs_mid of a fob" (0.5) forgives half a fob. It is a money courtesy expressed in fob units. Unusual wording, but it still reads as a published courtesy (half the per-fob charge forgiven), so it is recorded as an observation, not a red light.
- No condition holds for every customer: tenure varies.

### findings (r3)

- **N-1: closed.**
- **O-18, O-19: settled.**
- Still observations: O-3, O-4, O-9, O-10, O-11, O-12; O-14 and O-17 are per-task.
- New: O-20 (fractional fob forgiveness wording). No new charter-level defect.

### closing_checklist (revision 3)

Written after both r3 reveals (task 0 at 18:43:02Z, task 1 at 18:43:14Z).

- **Per-task files.** `0.md` and `1.md` each carry revisions 1–3; earlier revisions are preserved. Both revision_3 comparisons carry a full **PASS**.
- **Coverage and scopes.** All six extended policies and six task tools are covered. The two scopes are disjoint (task 0 {cleaning, settlement}; task 1 {carpet, repair, fob, gap}). GT and the task tools are closed. The uuid8s are independent and unchanged.
- **Problem trees.**
  - Task 0: 1 prerequisite, 1 value_input edge.
  - Task 1: 3 prerequisites, 3 value_input edges.
  - Each root is user-owned. The difficulty-wide graph is acyclic, and no edge crosses a task.
- **Factors.**
  - Counts per computation: cleaning 5, settlement 4, carpet 6, repair 5, fob 4, gap 5.
  - Each has at least 2 `parameter` and 1 honest `method` factor. Every ladder has at least 3 reachable, disjoint tiers stated in the rule.
  - Every task has a multi-source factor (task 0: cleaning courtesy / settlement rate; task 1: carpet wear allowance / repair labor rate) and a cross-difficulty factor with seeded rows (lease, pet, term, utility, parking).
  - Every factor bears weight against an honest baseline. The baseline alone gives a definite number that differs from gold:

    | computation | baseline alone | gold |
    | --- | --- | --- |
    | cleaning | 60.00 | 64.50 |
    | settlement | 473.26 | 453.04 |
    | carpet | 740.00 | 1238.00 |
    | repair | 105.00 | 226.50 |
    | fob | 0.00 | 145.00 |
    | gap | 0.00 | 91.34 |

- **Unique solution.** Both tasks' blind derivations equal GT value for value. No second reading was found.
- **Remaining observations** (not grounds for rework): O-3, O-4, O-9, O-10, O-11, O-12, O-14, O-17, O-20.
- **Gates.** The coordinator's post-rework snapshot is all green; check_traceability is deferred to render. The auditor edited no artifact.

**Difficulty result (revision 3): passes the source-layer audit.** Task 0 PASS; task 1 PASS.
