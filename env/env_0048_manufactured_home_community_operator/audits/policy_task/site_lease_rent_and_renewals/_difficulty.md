# Policy-task audit — site_lease_rent_and_renewals / charter-global

## charter_global_frozen

- Freeze time: 2026-10-08 23:15 UTC (revision 1; no earlier revision exists in this directory).
- Auditor: independent policy-task auditor (erl-task-policy-audit). Not the author of the bundle.
- Frozen inputs (sha256 re-computed by the auditor; they match the coordinator's HASHES.txt):
  - `tasks/site_lease_rent_and_renewals/lease.extended.yaml`: `1adf430e4207f2c86efb69031d8850ff087137665c661cf3206a8d36ff551a9d`
  - `tasks/site_lease_rent_and_renewals/task_tools.py`: `4cb7dbc0c2a6971c8918afd156a39becf8eb278800943dd209cc0ced8026147d`
  - Also read: `blueprint/blueprint.yaml` (difficulty entry), `blueprint/products/lease.yaml`, `blueprint/db_schema.json`, `blueprint/share_tools.py`, and the event/parameter sections of `blueprint/products/{utility,loan,rules}.yaml` (to check the cross-category rows the factors read). DSL primitive semantics read from `skills/erl-task-instantiate/scripts/check_compute.py` (MONTHS, DAYS, within_months, LATEST, CFIELD, XCOUNT, RND).
- Permitted: the charter, the tool module, the blueprint, the DSL definition. Masked and unread when this section was written: every `tasks/*/tasks/*.json` field (evaluation_criteria, computations, design_rationale, solvability_contract, prerequisite_closure, charter_scope, required_documents, db_closure*). Nothing in this section is derived from a revealed GT.
- Entry conditions (Step 0): the gate snapshot came with the brief and is on disk at `.audit_views/policy_task/site_lease_rent_and_renewals/GATES.txt` (check_extended, check_task_tools, replay_tasks, check_solvability, check_compute, check_grounding, check_cross_fire all rc=0; check_cache_diff informational; check_traceability deferred to render). Masked views with hashes came with the brief. Entry conditions are met.

### policy_conflict_scan

- Base copy: every top-level key of `blueprint/products/lease.yaml` (category ... policies) is identical to the same key in the extended file (structural compare plus a textual diff of lines 1-1544). The only extra key is `extended_policies`.
- Six extended policies, each with its own subject and target tool, no two the same:
  - `lease_ext_renewal_offer_rent`: subject lease_renewal_offer, tool `issue_renewal_offer_ab5c4495` (agent), computes new_monthly_site_rent.
  - `lease_ext_signed_renewal_rent`: subject lease_renewal, tool `sign_lease_renewal_1699e1a4` (user), computes new_monthly_site_rent.
  - `lease_ext_late_fee_assessment`: subject lease_late_fee, tool `post_late_fee_cfe97caa` (agent), computes amount.
  - `lease_ext_nonpayment_cure_period`: subject lease_nonpayment_notice, tool `serve_nonpayment_notice_fb7be621` (agent), computes cure_days.
  - `lease_ext_plan_down_payment`: subject lease_payment, tool `make_lease_payment_8919b7b0` (user), computes amount.
  - `lease_ext_plan_installments`: subject lease_repayment_agreement, tool `sign_repayment_agreement_730960e3` (user), computes installment_amount.
  All six subjects are in the blueprint difficulty's `event_types` claim.
- Overlapping subjects with base: the down-payment policy shares `lease_payment` with base `lease_evt_payment_acceptance`, and two of its sentences differ from base. Both differences are declared (see override_declarations). The late-fee, cure, offer and installment policies each overlap one base policy. Every difference that is declared is listed below, and the one that is not is finding C1.
- Time anchors: the late-fee grace ladder replaces the base counting sentence (declared). But the base eligibility `grace_period_ended.temporal_basis` still names `duration_source: variants.late_fee_grace_days` with the superseded counting_rule copied into it (observation O1). The cure-period rule's office business-day calendar contradicts the base cure-counting sentence, which is not declared (finding C1).
- Terminal states: none of the six writes changes lease status, so no terminal states conflict.
- Cross-category read boundaries: reads only (rules, loan, utility). None of the tools writes to another category.
- Scope partition: the prerequisite graph splits into two connected components: {offer -> signed renewal} and {late fee -> cure notice -> down payment -> installments; cure notice -> installments}. With M=2 these two components are the only partition that can be pairwise disjoint and jointly complete. Which component each task claims is confirmed per task from its world and persona (0.md, 1.md) and against `charter_scope` only after the reveal.

### rule_compute_equivalence

Every `compute_basis` string is a verbatim substring of its policy's `rule` (scripted check, no misses). Every `baseline.rule` sentence is a sentence of the `rule` (scripted check, no misses). Sweeping each policy sentence by sentence:

- `lease_ext_renewal_offer_rent`: equivalent, five adjustments (windowed COUNT/XCOUNT with `within_months=12`, i.e. `0 <= MONTHS(entry, NOW) < 12`), honored drafts = ach_autopay payments minus *all* lease_payment_return rows (the rule says "less the returned payments posted on the lease in the same months", which counts every return, so the two agree). Loan read through `CFIELD('loan','status')` does not filter on "home-only" (observation O2). Phase-in, rounding points and the result all agree. The two sentences on issuance (late issuance for the requested term, on-time issuance with rows per term) are not computed. They govern the write's object, and the 24-month row has no rent at all (finding C2).
- `lease_ext_signed_renewal_rent`: offered_rent/offer_date are taken as `LATEST(... offered_term_type='twelve_month')` by notice_date, with no effective_date filter. The rule's "the twelve-month renewal offer on the lease" together with the prerequisite sentence ("for the twelve-month term that begins the day after the current term end date") picks the same row once that row exists, so the two agree in practice. The market match, the early-signing credit, the utility credit, the loyalty count (lease_requests renewal_election/accepted) and the subtraction with rounding all agree.
- `lease_ext_late_fee_assessment`: sentence 1 says the fee is assessed on "the most recent billing period whose rent and occupant charges remain unpaid after its grace period". Compute binds `period`/`due_date` to `LATEST(lease_rent_charge)`, the most recent period whatever its state. These differ whenever the newest charge is still inside its grace period while an older period is unpaid (finding C3). Every other sentence agrees: unpaid amount (latest-payment form), grace ladder, rate, floor, daily charge, accrual anchor, community method, cap. The compute's community condition `DAYS(due_date, NOW) > grace_days` is the posting-time gate itself (see factor_ladders, F3).
- `lease_ext_nonpayment_cure_period`: community days, five extensions, sum and portal weekend roll all agree. For the office-channel branch the compute `7*(L//5) + L%5 + (2 if w + L%5 >= 5 else 0)`, with w = weekday of the notice (Mon=0), does not implement "office business days, Monday through Friday" when the notice date is a Saturday or Sunday (finding C4). The amount demanded is a base-form quantity (rent balance on the notice date) and is not in compute. That is correct, since `computes: cure_days`.
- `lease_ext_plan_down_payment`: covered balance = LATEST nonpayment notice amount. Down percentage ladder, three reductions, fees-up-front method, rounding of the percentage part and the result all agree. `earlier_late_fees_12m` subtracts the all-time count of the current period's late fees. This agrees with "for an earlier billing period".
- `lease_ext_plan_installments`: covered balance (LATEST notice amount), plan-length ladder, tenure months, utility months, schedule multiplier, balance left to spread (`F('rent_balance')`) and the result all agree. The quoted basis for `covered_balance` ("The plan length starts from the covered balance compared with the monthly site rent") does not itself say which notice. The selection rests on the prerequisite sentence and on the down-payment policy's definition (observation O3).
- Rounding: every compute uses `RND`, which is Python `round` on binary floats (round-half-even on the float representation), while the charter says "half up to the cent" throughout. This is a DSL-level divergence, not a charter sentence, and it is recorded as observation O4. It reaches no gold value in either world (checked per task). It does reach counterfactual factor-substitution figures (task files).

### action_binding_and_uuids

- Each `(target_tool, computes)` pair is claimed by exactly one policy (six tools, six policies). No tool is claimed twice.
- uuid8 tails: `ab5c4495`, `1699e1a4`, `cfe97caa`, `fb7be621`, `8919b7b0`, `730960e3`. They have no common prefix, no sequential or adjacent values and no shared tail with altered characters, so each reads as independently generated.
- Function bodies: each tool performs one create (plus one holding update for sign_lease_renewal, post_late_fee and make_lease_payment) with the arguments as given. None reads another table to refuse, validate or hint. No tool checks eligibility, prerequisites or amounts (the module docstring says so, and every body confirms it).
- Docstrings: none names another tool or states a position in a sequence relative to other actions. Each ends with "Afterwards the ... shows/appears ...", which describes that call's own effect. sign_repayment_agreement says "the first falling due on the first due date", an installment ordinal (observation O5).
- Business readings: each subject plus tool plus docstring admits one reading. None adds a confirmation, review or wait outside the policy.

### prerequisite_graph

| blocked policy | problem | kind | gate | form | policy_source verbatim in own rule | resolved_by = depended target_tool |
| --- | --- | --- | --- | --- | --- | --- |
| signed_renewal_rent | renewal_offer_rent | value_input | offered_rent (a compute binding) | state | yes | yes (`issue_renewal_offer_ab5c4495`) |
| nonpayment_cure_period | late_fee_assessment | state_gate | `lease_ledger.event_type` | state | yes | yes (`post_late_fee_cfe97caa`) |
| plan_down_payment | nonpayment_cure_period | value_input | covered_balance (binding) | state | yes | yes (`serve_nonpayment_notice_fb7be621`) |
| plan_installments | nonpayment_cure_period | value_input | covered_balance (binding) | state | yes | yes (`serve_nonpayment_notice_fb7be621`) |
| plan_installments | plan_down_payment | value_input | remaining_balance (binding) | state | yes | yes (`make_lease_payment_8919b7b0`) |

- `prerequisite` is filled on every policy (`[]` on offer and late fee). Every `problem` is another extended policy id in this file, never a base policy and never itself. The graph is acyclic: offer -> signed; late fee -> cure -> down -> installments, plus cure -> installments.
- `form: state` on every edge, so `fallback_reason` is correctly absent.
- `condition` against its sentence: four edges match in strength. The down-payment edge's condition adds "whose amount_demanded is the rent balance including every fee posted for that period", which the sentence does not say ("demanding that past-due balance"). It is slightly stronger, but the cure policy's own sentence (amount demanded = rent balance on the notice date, after the late-fee gate) yields the same state (observation O6).
- The state_gate edge's `gate` names a column (`lease_ledger.event_type`) rather than a declared eligibility gate. The gate exists only as the prose sentence of the cure rule (observation O7).
- `effect` texts: each `resolved_by` write produces the stated state or value. None uses authoring-viewpoint phrasing ("in this task", "at the opening").

### prerequisite_sentences

Four-point test per edge:

1. signed <- offer: "The rent written into a signed twelve-month renewal is fixed only after the notices on the lease carry a renewal offer for the twelve-month term that begins the day after the current term end date." The connective is "only after". The waited-on state is a record-visible row of the lease notices (term and effective date), with no tool, id or snake_case token. The strength matches the condition. Exactly one write of this difficulty creates a `lease_renewal_offer` row (`issue_renewal_offer`). Derivation: the reader sees no such row, looks for the policy whose rule creates renewal offers, and finds the offer policy's "An offer that fell due and was not issued is issued, on the day the omission is found, for the term the resident asks to renew on ...". One reading.
2. cure <- late fee: "A nonpayment notice is not served until the rent ledger carries the late fee owed for every billing period whose grace period has ended with its rent unpaid." The connective is "not ... until". The state is record-visible (late fee rows on the rent ledger). Clean of tool names. Exactly one write posts a `lease_late_fee` (`post_late_fee`). Derivation: unpaid periods past grace without a fee lead to the late-fee rule ("A late fee is assessed on the most recent billing period ..."). One reading.
3. down <- cure: "When a billing period's rent is unpaid long enough for a nonpayment notice to be owed, the down payment on a repayment agreement is not worked out before the notices on the lease carry a nonpayment notice demanding that past-due balance." The connective is "not ... before". The state is record-visible. Clean. Exactly one write creates a nonpayment notice (`serve_nonpayment_notice`). One reading.
4. installments <- cure: "The installments of a repayment agreement are fixed only after the notices on the lease carry the nonpayment notice whose amount demanded the agreement covers." The connective is "only after". The state is record-visible. Clean. Same single write. One reading.
5. installments <- down: "Before the installments of a repayment agreement are fixed, the rent ledger must carry the down payment received on the signing date." The connective is "Before". The state is a record-visible ledger payment dated the signing date. Clean. Exactly one write creates `lease_payment` (`make_lease_payment`). Derivation goes through the down-payment policy's rule ("starts with a down payment the resident makes on the signing date"). One reading.

No fallback reasons need testing (all edges are state form). Second wordings: the installments rule also says the covered balance "that is left after the down payment" and "The balance left to spread is the lease balance once the down payment is received". The depended-on down-payment rule opens with "A repayment agreement on a past-due lease balance starts with a down payment the resident makes on the signing date." Both restate the order already grounded by edge 5 in other words. No other problem's tool or id is named. These ground a declared edge in the same direction, so they create no undeclared dependency (observation O8). Base rule sentences stating cross-problem order ("No late fee is charged for a billing period covered by a repayment agreement whose installments are current"; nonpayment notice "unless a repayment agreement covering that balance is current") ground no edge. Both run in the same direction as the extended edges (the agreement comes last), so they do not contradict the tree (observation O9).

### override_declarations

Checked sentence by sentence against each `base_policy_refs` entry:

- `lease_ext_renewal_offer_rent` vs `lease_renewal_terms`.
  - Sentences 1, 2, 4 and 6-10 (fixed term only, active only, the twelve-month equivalent, response deadline and counting, signing as the resident's act, holdover, no renewal under notice or default) are followed or not touched.
  - Sentence 3 (75-day issuance with one row per term) and sentence 5 (the three offer formulas) are each named in `overwrite`.
  - The replacement for sentence 5 defines only the twelve-month and month-to-month offers. The replacement for sentence 3 still requires an on-time offer to carry "one row for each term the lot class makes available". The twenty-four-month offer branch that base declared is therefore dropped while its row is still required (finding C2).
  - The replacement of sentence 3 also removes the only sentence stating *when* an offer falls due. "fell due" and "on time" now rest on the `parameter_schema` meaning of renewal_offer_lead_days (observation O10).
- `lease_ext_signed_renewal_rent` vs `lease_renewal_terms`, with `overwrite: []`. Base never states the rent written into a signed renewal (it states offer rents and the holdover rent). The extended market match and credits therefore replace no base sentence. Response deadline, active status and signing as the resident's own act are inherited and consistent.
- `lease_ext_late_fee_assessment` vs `lease_evt_late_fee`. The fee formula sentence (including `lease_msr_period_rent_unpaid`) and the grace counting sentence are named. The rest is followed: assessed only after grace; no fee on zero unpaid, on fees or on prior late fees; at most one per period; on-time by entry date; none while an agreement is current. The structured base gate's `temporal_basis` still carries late_fee_grace_days (O1).
- `lease_ext_nonpayment_cure_period` vs `lease_nonpayment_process`. The amount/cure-deadline sentence is named. The base sentence "The cure period is counted in calendar days starting the day after the notice date, and a payment received on the deadline day itself is in time." is **not** named, yet the extended rule says that after an office-channel payment "the days are office business days, Monday through Friday" (finding C1). The trigger sentence is restated verbatim. Default, reinstatement and termination sentences are not touched.
- `lease_ext_plan_down_payment` vs `lease_evt_payment_acceptance` and `lease_repayment_terms`. Three sentences are named (partial payment after notice, certified funds, down-payment/installment sentence). Everything else is inherited and consistent: acceptance states, channels, posting/application order, active only, tenure, one plan per 12 months, max arrears 2.0 x rent, missed installment.
- `lease_ext_plan_installments` vs `lease_repayment_terms` and `lease_nonpayment_process`. The down/installment sentence (same base sentence as above, each policy replacing a different half) and the cure-by-payment sentence are named. The two replacements of the shared base sentence cover disjoint halves (down-payment amount vs installment count/amount), so the merged semantics are unique.
- Disguised forms: no anonymous intermediate (each deviation surfaces in a named sentence), and no 0/1 multiplier on a base amount. One dropped branch (C2). No rule calls a base output a "wrong value".

### factor_ladders

Classification line used for `effect` honesty (stated once, applied uniformly): a tier that substitutes a ladder constant into an otherwise identical formula (a rate, fee, threshold, share or count multiplier) is a `parameter`. A tier that changes the operations or the source quantity (adds or drops a term, switches the reference quantity, switches the anchor record, switches the calendar) is a `method`.

| policy | factor | label | honest? | tiers | multi-source (all non-fall-through tiers compound over distinct records) | cross_difficulty |
| --- | --- | --- | --- | --- | --- | --- |
| offer | payment_record_adjustment | parameter | yes | 3 (-0.6/-0.3/0) | no | - |
| offer | site_upkeep_adjustment | parameter | yes | 3 (-0.4/-0.2/0) | yes (rules_records + move_in_date) | rules |
| offer | returned_payment_adjustment | parameter | yes | 3 (+1.0/+0.5/0) | no | - |
| offer | autopay_draft_adjustment | parameter | yes | 3 (-0.3/-0.15/0) | no | - |
| offer | home_loan_adjustment | parameter | yes | 3 (-0.25/+0.25/0) | no (tier 2 single) | loan |
| offer | long_tenure_phase_in | method | **no**: tiers are x0.5 / x0.75 / x1 on the same `RND(dollar_increase * f, 2)` | 3 | no | - |
| signed | early_signing_credit | parameter | yes | 3 (5/2.5/0) | no | - |
| signed | utility_standing_credit | parameter | yes | 3 (2/1/0) | yes (utility_ledger + utility_accounts) | utility |
| signed | market_match | method | yes: switches the reference rent (new-resident base rent, base + margin, or the offer) | 3 | yes (offer row + tenure) | - |
| signed | renewal_loyalty_credit | parameter | yes | 3 (3/1.5/0) | no | - |
| late fee | first_lapse_rate | parameter | yes | 3 (4.5/7.0/5.0) | no | - |
| late fee | tenure_grace_length | parameter | yes | 3 (7/3/5) | no | - |
| late fee | standing_floor | parameter | yes | 3 (25/30/35) | yes (tenure + returns) | - |
| late fee | paid_share_daily_charge | parameter | yes | 3 (5/2/3) | no | - |
| late fee | accrual_end_anchor | method | yes: switches the end anchor record | 3 | partly | - |
| late fee | community_accrual_method | method | yes: adds a daily term / floor alone / percentage alone | 3 | **compound part vacuous** (F3) | - |
| cure | tenure_extension | parameter | yes | 3 (3/2/0) | no | - |
| cure | first_notice_extension | parameter | yes | 3 (3/1/0) | no (same table) | - |
| cure | partial_payment_extension | parameter | yes | 3 (2/1/0) | no | - |
| cure | steady_payer_extension | parameter | yes | 3 (2/1/0) | no | - |
| cure | utility_standing_extension | parameter | yes | 3 (2/1/0) | yes | utility |
| cure | payment_channel_calendar | method | yes: business-day calendar / weekend roll / plain calendar | 3 | no | - |
| down | standing_down_percentage | parameter | yes | 3 (20/22.5/25) | yes (tenure + agreements) | - |
| down | fees_up_front_method | method | yes: changes which charges are carved out of the percentage base | 3 | no | - |
| down | partial_payment_credit | parameter | yes | 3 (2/1/0) | no | - |
| down | prompt_arrangement_credit | parameter | yes | 3 (1/0.5/0) | no | - |
| down | first_lapse_credit | parameter | yes | 3 (1.5/0.5/0) | no | - |
| installments | covered_size_plan_length | parameter | yes | 3 (2/4/3) | no | - |
| installments | tenure_added_months | parameter | yes | 3 (2/1/0) | no | - |
| installments | utility_standing_months | parameter | yes | 3 (+1/-1/0) | yes (disjunction over ledger + balance) | utility |
| installments | payment_rhythm_schedule | method | **no**: tiers are x4 / x2 / x1 on the same `remaining / (plan_months * k)` | 3 | no | - |

- Counts: offer has 6 factors, 6 parameter after F1, and **0 genuine method**. Signed has 4 factors (3 parameter, 1 method). Late fee has 6 (4 parameter, 2 method). Cure has 6 (5 parameter, 1 method). Down payment has 5 (4 parameter, 1 method). Installments has 4 factors, 4 parameter after F2, and **0 genuine method**. Every computation keeps 4-6 factors and at least 2 parameter.
- Per component: offer + signed have multi-source factors (site_upkeep, utility_standing_credit, market_match) and cross-difficulty factors (rules, loan, utility). Late fee + cure + down + installments have multi-source factors (standing_floor, cure utility, standing_down, utility_months) and cross-difficulty factors (utility x2).
- Every ladder has 3 tiers that are pairwise disjoint as stated, every tier is stated in prose in the `rule` and implemented in the `decides` binding, no two tiers of one ladder select the same value or method, every fall-through equals the factor's `baseline`, and every `decides` is an input, never `result`. Every value comes from the policy's `params` or the lot-class parameters. Every policy `baseline.rule` is self-sufficient and every sentence of it is in the rule.
- Baseline coverage: the late-fee `baseline.rule` (percentage fee alone) contains no daily charge and no accrual days. The baselines of `paid_share_daily_charge` (3.00) and `accrual_end_anchor` (through the posting date) are stated only as their fall-through tiers, not by `baseline.rule`. Their weight therefore exists only while `community_accrual_method` selects the daily tier (observation O11).
- Business realism: most conditions and outcomes are ones this line of business weighs (good-payer and autopay discounts, NSF surcharges, long-tenure phase-ins and market caps, longer cure for long tenure, payment-channel calendars, carving fees out of a down payment). Two items are questionable but not demonstrably unreal. One is a home-loan delinquency on an affiliated lender raising the site-rent renewal increase (+0.25 pt). The other is "steady payer" counting payment instruments rather than months paid, so a resident who splits rent into two pieces reaches the full tier in six months (observation O12).

### findings

Charter-global findings. Each names the tasks it bears on. The demonstration against a world lives in the task file.

- **C1: SOURCE-POLICY RED (undeclared override).**
  - Symptom: the cure policy counts office-channel cure periods in business days.
  - Root cause: the base `lease_nonpayment_process` sentence "The cure period is counted in calendar days starting the day after the notice date, and a payment received on the deadline day itself is in time." is in force (not named in `overwrite`), while `lease_ext_nonpayment_cure_period` says "when it came through the community office (office_money_order, office_cashiers_check or office_personal_check) the days are office business days, Monday through Friday".
  - Demonstrated consequence (same situation, two conclusions): notice served on a Tuesday, latest payment by money order, lengthened period 19 days. The base sentence gives a deadline 19 calendar days later. The extended sentence gives 19 business days, i.e. 27 calendar days. Two defensible cure deadlines.
  - Affected: `lease.extended.yaml` `lease_ext_nonpayment_cure_period.overwrite` / rule sentence 11.
  - Bears on: task 1 claims the cure policy, but its latest payment is a portal payment. In that branch the extended text is "calendar days" plus a weekend roll, which the base sentence does not contradict. No consequence on task 1's world (see 1.md).
- **C2: SOURCE-POLICY RED (dropped branch / omission).**
  - The base twenty-four-month offer formula is superseded. The replacement defines only the twelve-month and month-to-month offers, yet the same policy requires "an offer issued on time carries one row for each term the lot class makes available".
  - Demonstrated consequence: an on-time offer on a Standard Multi-Section site (twenty_four_month_term_available true) must carry a twenty-four-month row whose rent no in-force sentence defines. That is no solution for that row.
  - Affected: `lease_ext_renewal_offer_rent.overwrite[0].replaced_by` and rule sentence 12.
  - Bears on: no task. Task 0 is a late issuance for the twelve-month term on a lot class without a twenty-four-month term.
- **C3: SOURCE-POLICY RED (rule/compute non-equivalence).**
  - The late-fee rule assesses "the most recent billing period whose rent and occupant charges remain unpaid after its grace period". Compute binds the period to the latest rent charge regardless.
  - Demonstrated consequence: frozen on the 3rd of a month with the prior month unpaid. The rule assesses the prior month (its charges, due date and grace). Compute reads the current month's charge, due date and grace. These give different unpaid amounts and accrual days.
  - Affected: `lease_ext_late_fee_assessment.compute.due_date/period` vs rule sentence 1.
  - Bears on: task 1 in principle. On its world the latest charge (October) is the unpaid period past grace, so the two coincide (see 1.md).
- **C4: SOURCE-POLICY RED (rule/compute non-equivalence).**
  - The office business-day branch of `cure_days` miscounts when the notice date is a weekend day.
  - Demonstrated consequence: notice on a Saturday (w=5), L=1. The rule ("office business days, Monday through Friday", counted from the day after the notice) gives the deadline on Monday, 2 days. Compute gives `7*0 + 1 + 2 = 3`, Tuesday. For a Sunday notice, compute also gives 3, against a correct 1.
  - Affected: `lease_ext_nonpayment_cure_period.compute.cure_days`.
  - Bears on: no task. Task 1's notice falls on a Tuesday and its channel is the portal.
- **F1: SOURCE-FACTOR RED (mislabelled effect).**
  - `long_tenure_phase_in` is labelled `method`, but its three tiers are `RND(dollar_increase*0.5,2)`, `RND(dollar_increase*0.75,2)` and `dollar_increase` (= `RND(dollar_increase*1,2)`): one formula with a constant share substituted.
  - Consequence: `lease_ext_renewal_offer_rent` has no genuine `method` factor, below the floor of 1 per computation.
  - Bears on: task 0.
- **F2: SOURCE-FACTOR RED (mislabelled effect).**
  - `payment_rhythm_schedule` is labelled `method`, but its tiers only substitute k in {4, 2, 1} into `remaining_balance / (plan_months * k)`. The first due date is the same in every schedule ("in every schedule the first installment is due on the rent due day of the next month"), so no scored quantity sees anything but the multiplier.
  - Consequence: `lease_ext_plan_installments` has no genuine `method` factor.
  - Bears on: task 1.
- **F3: SOURCE-FACTOR RED (unreal ladder: vacuous compound part).**
  - Tiers 1 and 2 of `community_accrual_method` read "site at ... AND rent still unpaid past the last grace day". The second part holds for every customer who reaches this write: rule sentence 1 assesses a fee only on a period that "remain[s] unpaid after its grace period", and "the fee may be posted from the day after the last grace day". In compute it is `DAYS(due_date, NOW) > grace_days`, the posting-time gate. The ladder is therefore community-only, presented as two-condition.
  - The factor still has three distinct tiers and the late-fee computation keeps another method (accrual_end_anchor).
  - Bears on: task 1.

Observations (no relationship consequence demonstrable; not grounds for rework):

- **O1:** base `grace_period_ended.temporal_basis` keeps `duration_source: variants.late_fee_grace_days` and a copy of the superseded counting sentence, while the extended grace ladder gives 7 or 3 days.
- **O2:** the loan read does not filter on a home-only variant.
- **O3:** installments `covered_balance` basis does not itself name "the most recent nonpayment notice".
- **O4:** `RND` is round-half-even on floats, against the charter's half up.
- **O5:** docstring ordering words describe own effects only.
- **O6:** the down-payment edge condition is slightly stronger than its sentence.
- **O7:** the `state_gate` gate is a column, not an eligibility id.
- **O8:** the installments <- down-payment order is restated in both rules.
- **O9:** base cross-problem order sentences run with the tree.
- **O10:** the offer due-date sentence is superseded and survives only in `parameter_schema`.
- **O11:** two late-fee factor baselines are fall-through-only.
- **O12:** the loan-delinquency and payment-count tiers are questionable on business realism but not demonstrably unreal.
- **O13:** `lease_ext_signed_renewal_rent` rule sentence 1 opens "This policy fixes ...", which is self-referential policy prose. It is not authoring viewpoint about a task, and it has no consequence.

## closing_checklist

Written 2026-10-08 after both reveals. Everything above this heading was written before any GT was opened (mtime 23:16:57 UTC; first reveal 23:19:30 UTC) and is left unchanged.

- Audit files: `0.md` and `1.md` correspond one-to-one with tasks 0 and 1, and this file sits beside them. This is revision 1; there are no older revisions. Each task file has a frozen derivation followed by a comparison section.
- Comparison results:

  | task | verdict | finding |
  | --- | --- | --- |
  | 0 | **SOURCE-FACTOR RED** | F1 |
  | 1 | **SOURCE-FACTOR RED** | F2, F3 |

  Policy self-consistency, problem tree and unique solution PASS in both tasks. Both independent derivations equal GT on every argument, owner, order and terminal state. **The difficulty does not pass the source-layer audit.**
- Coverage and scope: GT `charter_scope` gives task 0 = {renewal_offer_rent, signed_renewal_rent} and task 1 = {late_fee_assessment, nonpayment_cure_period, plan_down_payment, plan_installments}. These are pairwise disjoint and cover all six extended policies, each with its own task tool. The uuid8 tails are independent (§ action_binding_and_uuids).
- Trees:

  | task | prerequisite problems | value_input edges | customer-owned writes |
  | --- | --- | --- | --- |
  | 0 | 1 | 1 | the signature |
  | 1 | 3 | 3 | the payment and the agreement |

  Every edge is unmet at the opening and bears weight. The union graph is a DAG with no cross-task edge.
- Factors:
  - Every computation declares a self-sufficient baseline whose number differs from gold: 597.27, 588.13, 36.60, 7, 92.74 (92.73 float) and 93.51.
  - Every computation declares 4-6 factors, all bearing weight on their task's world.
  - Each task has at least 1 multi-source and at least 1 cross-difficulty factor, with seeded rows.
  - Failing: F1 (offer: 0 genuine method), F2 (installments: 0 genuine method), F3 (vacuous compound conjunct in community_accrual_method).
- Charter-global SOURCE-POLICY findings with no consequence on either world: C1 (undeclared business-day override of the base cure counting), C2 (dropped 24-month offer branch), C3 (late-fee period bound to the latest charge), C4 (weekend notice miscount in the office branch). They remain defects of the charter.
- Gates: this auditor does not run the gates. The snapshot that came with the brief (all rc=0; traceability deferred) is the one cited. No artifact was changed by this audit, so there is no new final form to re-run them on.

## revision_2

### charter_global_frozen (revision 2)

- Re-audit round 2. Started 2026-10-09 09:03 UTC. Auditor: the same independent auditor as round 1. Revision 1 above is left untouched.
- Inputs, re-hashed by the auditor and matching the coordinator's HASHES.txt:

  | input | sha256 | vs round 1 |
  | --- | --- | --- |
  | `lease.extended.yaml` | `0cc69e70f4d2edfcfbdafc01e6ad4f7071a199543835a3698f77e787052f2094` | **changed** from `1adf430e…` |
  | `task_tools.py` | `4cb7dbc0c2a6971c8918afd156a39becf8eb278800943dd209cc0ced8026147d` | unchanged |
  | `0.view.json` | `bdeb595f…` | unchanged |
  | `1.view.json` | `e6e0a5e5…` | changed |

- Because the charter hash changed, every charter-global section is **re-derived in full** below. § action_binding_and_uuids is the exception: it rests only on the unchanged tool module and the unchanged (target_tool, computes) pairs, so it is carried forward by reference on the grounds of the unchanged `task_tools.py` hash.
- Gate snapshot after rework (GATES.txt): every gate rc=0; traceability deferred. The entry conditions are met.
- Masked and unread when this section was written: the round-2 task JSONs. Nothing here derives from round-2 GT. The auditor has seen round-1 GT, and that exposure is disclosed in each task file.

### policy_conflict_scan (rev 2)

- The base copy is still identical to `blueprint/products/lease.yaml` (structural compare of every key; textual diff of lines 1-1544).
- There are still six extended policies with the same subjects, target tools and computes, so subjects do not overlap between extended policies. The scope partition is unchanged: {offer, signed} and {late fee, cure, down payment, installments}.
- Base overlaps: every deviation is now declared. The cure policy names the base counting sentence (closes C1; see override_declarations).

### rule_compute_equivalence (rev 2)

Scripted checks: every `compute_basis` string is verbatim in its rule; every `baseline.rule` sentence is in its rule; every factor's `decides` is a compute binding. All pass.

Changes since round 1, swept sentence by sentence:

- **Offer:**
  - The phase-in is removed. New sentences: "The raised rent is the twelve-month-equivalent rent plus the dollar increase.", "The standard twelve-month offer is the raised rent." and the market-position step (lesser for at least market_long_months = 120; midpoint, rounded half up, for 60-119; otherwise raised).
  - Compute `raised_rent`, `market_offer` and `result` implement these exactly. The midpoint is `RND((raised_rent + base)/2 + 0.000001, 2)`.
  - "The offer falls due renewal_offer_lead_days calendar days before the current term end date." is added. It is not computed; it governs timing (closes O10).
  - The twenty-four-month offer now has a rent: "worked out the same way with renewal_increase_pct_twenty_four_month as the standard rate in place of renewal_increase_pct_twelve_month and is then reduced by twenty_four_month_rent_discount_monthly" (closes the C2 omission).
  - "The same way" does not say whether the market-position step, which the rule phrases as fixing "the twelve-month offer", also applies to the 24-month row before the discount. That is residual observation R2-O1. Neither task issues a 24-month row.
- **Late fee:**
  - Sentence 1 now reads "A late fee is assessed on the billing period of the most recent rent charge once that period's grace period, counted from the due date of that rent charge, has ended with its rent and occupant charges unpaid; a fee owed on an earlier period is assessed on the same terms while that period's rent charge is still the most recent one." Compute `period`/`due_date` = LATEST rent charge now matches the rule, which closes the C3 non-equivalence. It also creates new finding N1 (below).
  - The community sentence now conditions on "whether the period's charges are still uncovered on the posting date, meaning that the period's rent and occupant charges less credits still exceed the latest payment received on or after the due date". The compute's `period_charges - (latest payment since due) > 0` matches it.
- **Cure:**
  - The office branch for weekend notices is now `(7 - w) + 7*((L-1)//5) + (L-1)%5`. A brute-force comparison against a day-by-day Monday-Friday count starting the day after the notice, for every weekday w in 0..6 and L in 1..44, gives 0 mismatches (closes C4).
  - New sentence: "However the cure days are counted, the count starts the day after the notice date, and a payment received on the deadline day itself is in time."
- **Installments:**
  - New sentence: "The covered balance is the amount demanded by the most recent nonpayment notice on the lease." This is now the quoted basis of `covered_balance` (closes O3).
  - The plan-length sentence is replaced: small balances get one plan month per dollars_per_plan_month (200) or part thereof, i.e. `-(-covered // 200)`; large balances get one per rent_share_per_plan_month (0.5) of the rent or part thereof; otherwise payment_plan_max_installments. The ceiling matches "or part thereof".
- **Signed:** sentence 1 now reads "The monthly site rent written into a renewal the resident signs for a twelve-month term is worked out as below; ..." (closes O13). Otherwise unchanged.
- **Down payment:** unchanged apart from rounding.
- **Rounding:** every `RND` now adds `+ 0.000001` before rounding. For the non-negative amounts here this realises half up at exact half-cent ties (for example 19.985 gives 19.99 and 92.735 gives 92.74), so the compute now agrees with "rounded half up" (closes O4 in substance). It would still mis-round a negative tie, but no rounded quantity here is negative.

### action_binding_and_uuids (rev 2)

Carried forward from revision 1: the `task_tools.py` hash is unchanged, and the six (target_tool, computes) pairs are unchanged (scripted listing).

### prerequisite_graph (rev 2)

- The five edges are unchanged: same problems, kinds, gates, forms, conditions and resolved_by.
- Each `policy_source` is still verbatim in its own rule (scripted). The graph is still acyclic.
- O6 and O7 are unchanged, as the reworker declared.

### prerequisite_sentences (rev 2)

- The five prerequisite sentences are unchanged and pass the four-point test as in revision 1.
- O8 (second wordings of the installments <- down-payment order) is unchanged.
- The new installments sentence "The covered balance is the amount demanded by the most recent nonpayment notice on the lease." states a value definition, not an order, and introduces no undeclared dependency.
- The new late-fee sentence 1 interacts with the cure sentence (N1 below).

### override_declarations (rev 2)

- Offer: two named overwrites.
  - The replacement of the base offer-formula sentence is now the 24-month/month-to-month sentence. The twelve-month formula lives in new rule sentences that state a different method from base. The overwrite names the base sentence that carried all three formulas, so the deviation is declared.
  - The dropped 24-month branch is restored (C2 closed).
- Cure: the base sentence "The cure period is counted in calendar days starting the day after the notice date, and a payment received on the deadline day itself is in time." is now named in `overwrite`, replaced by the channel-calendar sentence. The start-day and deadline-day parts are restated in the new sentence. **C1 closed.**
  - The frozen base eligibility `cure_deadline_passed.temporal_basis` still carries `unit: calendar_days` and a copy of the superseded counting sentence. This is the same shape as O1 and is recorded as O1b. It is a base-blueprint artifact and governs `lease_default`, which no task writes.
- Late fee, down payment, installments, signed: the same declarations as revision 1, all still verbatim. No undeclared override found.

### factor_ladders (rev 2)

| policy | factors (label) | genuine method | change since round 1 |
| --- | --- | --- | --- |
| offer | 5 parameter + `market_position_step` (method) | yes: the tiers select the base rent (a different source quantity), the mean of two candidates (a different operation), or the raised rent | `long_tenure_phase_in` removed. **F1 closed.** The step is multi-source (raised rent AND tenure) |
| signed | unchanged (3 parameter + market_match method) | yes | none |
| late fee | 4 parameter + accrual_end_anchor + community_accrual_method | yes | community tiers now "AND the period's charges less credits still exceed the latest payment received on or after the due date". **F3 closed** (detail below) |
| cure | 5 parameter + payment_channel_calendar | yes | none |
| down payment | 4 parameter + fees_up_front_method | yes | none |
| installments | `covered_size_plan_length` (now **method**), tenure, utility, `payment_rhythm_schedule` (now **parameter**) | yes, see below | **F2 closed** |

- **F3 detail:** the conjunct is no longer vacuous. A resident whose latest post-grace payment covers the period's charges still reaches the write, because the unpaid amount at grace end is positive, yet falls to the percentage-only tier. It reads distinct records: community from the holding, payment from the ledger.
- **Installments method:** `covered_size_plan_length` changes the operation between tiers: one counts plan months from the balance by ceiling division, the other uses a fixed standard count. Its two counting tiers use different reference quantities: a fixed dollar unit, or a share of this lease's rent. Under the classification line of revision 1 (switching operation or source quantity = method) it is a method. That two tiers share the ceiling-division shape is recorded as observation R2-O2. `payment_rhythm_schedule` is honestly labelled parameter now.
- **Counts:**
  - offer: 6 factors (5 parameter, 1 method)
  - signed: 4 factors (3 parameter, 1 method)
  - late fee: 6 factors (4 parameter, 2 method)
  - cure: 6 factors (5 parameter, 1 method)
  - down payment: 5 factors (4 parameter, 1 method)
  - installments: 4 factors (3 parameter, 1 method)

  Every computation now meets 4-6 factors with at least 2 parameter and at least 1 method.
- Multi-source and cross-difficulty factors per component are unchanged or added (the offer's market step is multi-source). Every fall-through equals its baseline, every ladder has 3 disjoint tiers, and every tier is stated in its rule.
- O11 and O12 are unchanged.

### findings (rev 2)

Status of round-1 findings, verified against the artifacts:

| id | status | basis |
| --- | --- | --- |
| C1 | **closed** | base sentence named in `overwrite`; start-day and deadline-day parts restated |
| C2 | **closed** | the 24-month row has a defined rent. Residual scope ambiguity R2-O1 (observation) |
| C3 | **closed** as a rule/compute non-equivalence | rule now says "most recent rent charge" like the compute. But see N1 |
| C4 | **closed** | brute force: 0 mismatches over 7 weekdays x 44 lengths |
| F1 | **closed** | phase-in removed; market_position_step is a genuine method |
| F2 | **closed** | rhythm relabelled parameter; covered_size_plan_length is a genuine method |
| F3 | **closed** | conjunct is now a real dividing condition on distinct records |
| O3, O4, O10, O13 | addressed as described above | |
| O1, O2, O5-O9, O11, O12 | unchanged, as declared | |

New findings:

- **N1: SOURCE-POLICY RED (new, introduced by the C3 rework). The late-fee timing sentence and the cure gate reach different conclusions when an earlier period's fee was never posted.**
  - Late-fee rule: "a fee owed on an earlier period is assessed on the same terms while that period's rent charge is still the most recent one". Once the next month's rent charge posts, an earlier period's owed fee can no longer be assessed.
  - Cure rule: "A nonpayment notice is not served until the rent ledger carries the late fee owed for every billing period whose grace period has ended with its rent unpaid."
  - Demonstrated consequence: a resident whose September rent is wholly unpaid with no September fee posted, handled on October 3 (the October charge posted October 1, still in grace).
    - Reading A: the September fee is "owed" (the late-fee rule itself calls it "a fee owed on an earlier period") but cannot be assessed. The cure gate can never be met, so no notice can be served and no notice-dependent repayment agreement can follow. No solution.
    - Reading B: a fee that can no longer be assessed is not "owed", so the gate is met and the notice is served without it.
    - The two readings give two different amounts demanded, or no write at all.
  - Affected: `lease_ext_late_fee_assessment` rule sentence 1, read against `lease_ext_nonpayment_cure_period` rule sentence 2.
  - Bears on: neither task's world. In task 1 the October charge is both the latest charge and the only unpaid-past-grace period. Recorded so that it is not regressed silently.
- R2-O1 (observation): the 24-month offer's "worked out the same way" leaves open whether the market-position step applies before the discount.
- R2-O2 (observation): two of covered_size_plan_length's tiers share a ceiling-division shape and differ in their reference quantity.
- O1b (observation): the base `cure_deadline_passed.temporal_basis` still says calendar days (frozen blueprint).
- T1 (observation, unchanged): in task 0 the signed rent still depends on the offered amount only through the "above base rent" threshold and the offer date.

### closing_checklist (revision 2)

Written 2026-10-09 after both round-2 reveals (09:08:03 UTC). The round-2 charter-global section above was written before them (mtime 09:06:59).

- Files: `0.md` and `1.md` each carry revision 1 untouched plus revision_2 (frozen derivation, then comparison). This file carries revision 1 untouched plus revision_2.
- Per-task results:

  | task | policy self-consistency | problem tree | factors | unique solution |
  | --- | --- | --- | --- | --- |
  | 0 | PASS | PASS | PASS | PASS |
  | 1 | PASS | PASS | PASS | PASS |

  Every round-1 RED is verified closed against the artifacts: C1, C2, C3, C4, F1, F2 and F3. No scored value, tree or factor figure regressed.
- Coverage: the six extended policies are covered by two pairwise-disjoint scopes (GT `charter_scope` matches). Tools and uuid8s are unchanged and independent.
- Trees:
  - task 0: 1 prerequisite, 1 value_input edge, a customer-owned write;
  - task 1: 3 prerequisites, 3 value_input edges, two customer-owned writes;
  - every edge is unmet at the opening and bears weight;
  - the union graph is a DAG.
- Factors: every computation now has 4-6 factors with at least 2 parameter and at least 1 genuine method, an honest, self-sufficient baseline that differs from gold, and every factor bearing weight. Each task has multi-source and seeded cross-difficulty factors.
- **New charter-global defect, N1 (SOURCE-POLICY RED), introduced by the C3 rework.** The late-fee rule lets an earlier period's owed fee be assessed only while that period's charge is the latest. The cure gate requires "the late fee owed for every billing period whose grace period has ended with its rent unpaid". In a world with an unposted earlier-period fee and a newer charge, these give either no solution or a notice without the fee. Neither task's world reaches it, so no task verdict changes. It remains a defect of the charter.
- Observations still open: R2-O1, R2-O2, O1, O1b, O2, O5-O9, O11, O12 and T1.
- Gates: cited from the coordinator's round-2 snapshot (all rc=0; traceability deferred). The auditor changed no artifact.
- **Outcome:** both tasks PASS all four relationships, so the difficulty passes the source-layer audit at the task level. N1 is an open charter-global SOURCE-POLICY defect that bears on no task in this bundle, and it is reported for the coordinator's decision.

## revision_3

### charter_global_frozen (revision 3)

- Re-audit round 3, started 2026-10-09 10:11 UTC by the same auditor. Revisions 1 and 2 are left untouched.
- Inputs, re-hashed by the auditor:

  | input | sha256 | vs round 2 |
  | --- | --- | --- |
  | `lease.extended.yaml` | `2105e1a03d8b95c6241747c755e31c418a7575e0543cd35543a20341f0791ba3` | **changed** from `0cc69e70…` |
  | `task_tools.py` | `4cb7dbc0…` | unchanged |
  | `0.view.json` | `bdeb595f…` | unchanged |
  | `1.view.json` | `e6e0a5e5…` | unchanged |

- Gate snapshot: every gate rc=0. Masked and unread at this writing: the round-3 task JSONs.
- How the change was located: the auditor holds no byte copy of the round-2 charter. The file still has 2659 lines, and every extended policy starts at the same line as in round 2 (1546, 1753, 1896, 2090, 2303, 2488).
  - Re-reading the late-fee and cure rules against the round-2 text quoted in this audit shows one changed sentence: late-fee rule sentence 1 now ends "..., and a late fee not assessed by the time the next rent charge falls due lapses and is no longer owed."
  - The re-run checks find nothing else changed. Every scripted check gives the same results as round 2, and every compute evaluated on both worlds gives the same values as round 2 (gold, every factor substitution, every all-baseline figure). Factor ids and labels are unchanged.
  - A textual change elsewhere that alters neither structure nor any value on these worlds cannot be excluded byte for byte without the old copy. This limitation is stated rather than assumed away.

### re-derived checks (rev 3)

- Base copy: still identical to `blueprint/products/lease.yaml`.
- Rule/compute equivalence: every `compute_basis` is still verbatim in its rule, including the late-fee `period` quote "A late fee is assessed on the billing period of the most recent rent charge". Every baseline sentence is in its rule. The lapse clause has no compute counterpart and needs none: the compute only ever assesses the latest charge's period, which the lapse clause leaves untouched.
- Overrides: the lapse clause replaces no base sentence. Base `lease_evt_late_fee` sets no assessment deadline and says nothing about older fees staying assessable. No undeclared override.
- Prerequisite sentences: all five are unchanged and verbatim in their own rules (scripted).
- Factor ladders: unchanged from revision 2. Every computation has 4-6 factors with at least 2 parameter and at least 1 genuine method, and every fall-through is its baseline.
- action_binding_and_uuids: carried forward. The tool hash and the (target_tool, computes) pairs are unchanged.

### findings (rev 3)

- **N1: closed at the rule level.**
  - The late-fee rule now settles that an earlier period's fee not assessed by the next rent due date "lapses and is no longer owed". The cure gate requires "the late fee owed for every billing period whose grace period has ended with its rent unpaid", so it no longer counts a lapsed fee.
  - In the round-2 scenario (September unpaid with no fee, handled on October 3) only reading B now remains: the September fee is not owed, the gate is met, and the notice is served without it. One reading.
  - Business realism: assessing a late fee only within the billing cycle and letting it lapse otherwise is a policy a landlord can publish. Not unreal.
- **N2: SOURCE-POLICY RED (new, residue of the N1 rework). The cure edge's declared `condition` was not updated and is now stronger than its sentence.**
  - `lease_ext_nonpayment_cure_period.prerequisite[0].condition`: "lease_ledger holds a lease_late_fee row for every billing period whose rent and occupant charges were unpaid at the end of the last grace day." It carries no lapse exclusion.
  - The prerequisite sentence, now read with the late-fee rule's lapse clause, waits only on fees still owed.
  - Demonstrated consequence (same situation as N1): September unpaid with its fee lapsed, October charge posted. The sentence is satisfied and the notice is served. The declared `condition` can never be satisfied, since no September fee row may now be posted, so the notice stays blocked forever. Two passages, two conclusions.
  - This is the check-7 shape "condition quietly strengthened by the prerequisite field". The field is part of the general text, but the rendered KB carries the sentence, not the condition.
  - Bears on: neither task's world. In task 1 October is the only unpaid-past-grace period and its fee is assessable, so the condition and the sentence agree.
- Round-2 observations still open: R2-O1, R2-O2, O1, O1b, O2, O5-O9, O11, O12 and T1. No other new defect found.

### closing_checklist (revision 3)

Written 2026-10-09 after the round-3 reveals (10:12:37 UTC). The rev-3 charter-global section was frozen before them (mtime 10:12:29).

- Per-task results:

  | task | policy self-consistency | problem tree | factors | unique solution |
  | --- | --- | --- | --- | --- |
  | 0 | PASS | PASS | PASS | PASS |
  | 1 | PASS | PASS | PASS | PASS |

  All arguments, owners, order, terminal states and factor figures equal round 2 and round-3 GT. No regression.
- Round-2 red light N1: closed at the rule level, verified against the artifact.
- **New charter-global red light N2 (SOURCE-POLICY)**, the residue of the N1 rework: the cure edge's declared `condition` still demands a late-fee row for every period unpaid at grace end, including periods whose fee has now lapsed. In a world with a lapsed earlier-period fee it would block the notice forever, while the sentence lets the notice be served. Neither task's world reaches it, so no task verdict changes.
- Coverage, scopes, tools and uuid8s, trees and factor bounds: unchanged from revision 2 and still satisfied.
- Gates: cited from the coordinator's round-3 snapshot (all rc=0). The auditor modified no artifact.
- Limitation: the round-2 charter was not available byte for byte. "Nothing else changed" rests on identical line offsets, identical structural check results and identical computed values on both worlds.
- **Outcome:** both tasks PASS all four relationships. One open charter-global defect (N2) bears on no task in this bundle and is reported for the coordinator's decision. Open observations: R2-O1, R2-O2, O1, O1b, O2, O5-O9, O11, O12 and T1.

## revision_4

### charter_global_frozen (revision 4)

- Re-audit round 4, started 2026-10-09 10:47 UTC by the same auditor. Earlier revisions are left untouched.
- Inputs, re-hashed by the auditor:

  | input | sha256 | vs round 3 |
  | --- | --- | --- |
  | `lease.extended.yaml` | `0af6fef1bf48f28c41737033fdf034875efe90cc715eccb497b14a99a8966c68` | **changed** from `2105e1a0…` |
  | `task_tools.py` | `4cb7dbc0…` | unchanged |
  | both views | `bdeb595f…`, `e6e0a5e5…` | unchanged |

- Gate snapshot: every gate rc=0. The round-4 task JSONs are unread at this writing.
- How the change was located:
  - The file still has 2659 lines, and every extended policy starts at the same line as in rounds 2 and 3.
  - The base copy is still identical to the blueprint.
  - The late-fee lapse sentence is unchanged.
  - All five prerequisite `condition` texts were printed and compared with their earlier text. The cure edge's condition is the only one changed.
  - Every scripted check gives the same results as round 3: compute_basis verbatim, baseline sentences in rule, prerequisite sources verbatim, overwrites in rule, factor ids and labels.
  - Every compute evaluated on both worlds gives the same values as round 3 (gold, every factor substitution, every all-baseline figure).
  - The limitation of revision 3 still applies: no byte copy of the previous charter is held.

### findings (rev 4)

- **N2: closed.**
  - `lease_ext_nonpayment_cure_period.prerequisite[0].condition` now reads: "lease_ledger holds a lease_late_fee row for every billing period whose rent and occupant charges were unpaid at the end of the last grace day and whose late fee is still owed, that is, has not lapsed because the next rent charge fell due before it was assessed."
  - This has the same strength and scope as the prerequisite sentence ("the late fee owed for every billing period whose grace period has ended with its rent unpaid") read with the late-fee lapse clause ("a late fee not assessed by the time the next rent charge falls due lapses and is no longer owed").
  - In the September/October scenario of N1/N2, both the condition and the sentence now let the notice be served without the lapsed fee. One conclusion.
  - kind, gate, form, resolved_by and effect are unchanged and still consistent.
- No new defect.
  - The rest of the prerequisite graph, every rule/compute correspondence, every override declaration, every factor ladder and the tool contracts are as in revision 3.
  - Open observations: R2-O1, R2-O2, O1, O1b, O2, O5-O9, O11, O12 and T1.

### closing_checklist (revision 4)

Written 2026-10-09 after the round-4 reveals (10:48:25 UTC). The rev-4 charter-global section was frozen before them (mtime 10:48:18).

- Per-task results:

  | task | policy self-consistency | problem tree | factors | unique solution |
  | --- | --- | --- | --- | --- |
  | 0 | PASS | PASS | PASS | PASS |
  | 1 | PASS | PASS | PASS | PASS |

  All scored arguments and factor figures equal round 3 and round-4 GT.
- Round-3 red light N2: closed, verified in the charter and in task 1's `prerequisite_closure`.
- No open red light remains, either per task or charter-global: C1-C4, F1-F3, N1 and N2 are all closed.
- Scopes, tools, uuid8s, trees (task 0: 1 prerequisite, 1 value_input edge; task 1: 3 prerequisites, 3 value_input edges; customer-owned writes in both; DAG) and factor bounds are all satisfied.
- Gates: cited from the coordinator's round-4 snapshot (all rc=0; traceability deferred to render). The auditor modified no artifact.
- **Outcome: the difficulty passes the source-layer audit.**
- Observations remain on record, none grounds for rework: R2-O1, R2-O2, O1, O1b, O2, O5-O9, O11, O12 and T1.
- Limitation: "nothing else changed" rests on identical line offsets, identical structural check results and identical computed values. No byte copy of the previous charter was held.
