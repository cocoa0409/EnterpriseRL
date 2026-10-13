# Policy-task audit — country_home_loan_servicing / charter-global

## charter_global_frozen

- Frozen: 2026-10-11T08:10Z–08:17Z (before any task GT was revealed). Auditor: independent policy-task auditor (erl-task-policy-audit), not the instantiating agent.
- Freeze hashes (re-checked with `sha256sum` against the coordinator's HASHES.txt, all equal):
  - `tasks/country_home_loan_servicing/homeloan.extended.yaml` sha256=43b443bca37c25d6855bcd14662efdb716142314f93630e1ee8dc7828bff262b
  - `tasks/country_home_loan_servicing/task_tools.py` sha256=776849404acc7293b622296bcf5357bdf91bac201c58969e417bcaea36ea8201
- What this section was built from: `blueprint/blueprint.yaml`, `blueprint/products/homeloan.yaml`, `blueprint/db_schema.json`, `blueprint/share_tools.py` (signatures only), the extended charter, `task_tools.py`, and the restricted-expression evaluator in `skills/erl-task-instantiate/scripts/check_compute.py` (used only for what `MONTHS`, `DAYS` and `within_months` mean).
- Masked, never read before the reveal: every task's `evaluation_criteria`, `computations`, `charter_scope`, `required_documents`, `design_rationale`, `solvability_contract`, `prerequisite_closure`, `db_closure*`. I also did not read other difficulties' audit files. No recursive grep touched `tasks/`.
- Base copy check: the first 1455 lines of the extended charter are byte-identical to `blueprint/products/homeloan.yaml` (python list compare, `True`).
- Gate snapshot (from the coordinator; I cite it and did not re-run it): extended / task_tools / solvability / compute / grounding / cross_fire are green. replay_tasks shows rc=1 only because of `farmland_transactions.loan_id` dangling-FK lines. I checked the coordinator's ruling. `db_schema.json` gives `loan_id` as the first key of `equipment_loans`, `farmland_loans` and `homeloan_loans` alike, and `find_farmland_transactions` filters `farmland_transactions` by its own `loan_id`. The DSL `_xrows` resolves ownership through `farmland_loans`' PK. So this is a gate artefact and not a task defect (confirmed per task in each world: the farmland_transactions rows point at the farmland_loans row).

The charter has six extended policies. The short names below are used throughout:

| id | short | target_tool (owner) | computes | prerequisite |
| --- | --- | --- | --- | --- |
| homeloan_ext_late_charge_reopened_month | P1 | assess_late_charge_eed44226 (agent) | late_charge_amount | [] |
| homeloan_ext_returned_remittance_fee | P2 | assess_returned_item_fee_25e49e31 (agent) | fee_amount | [] |
| homeloan_ext_replacement_remittance | P3 | apply_replacement_remittance_c604a214 (agent) | remittance_amount | P1 (value_input, state), P2 (value_input, state) |
| homeloan_ext_escrow_shortage_paid_at_once | P4 | pay_escrow_shortage_8ff65e44 (user) | shortage_amount | P3 (value_input, state) |
| homeloan_ext_escrow_waiver_paydown | P5 | make_principal_paydown_d2fdfc16 (user) | paydown_amount | [] |
| homeloan_ext_escrow_waiver_fee | P6 | record_escrow_waiver_439c8464 (agent) | waiver_fee | P5 (value_input, action) |

### policy_conflict_scan

- **Overlapping subjects.** Three pairs touch the same quantity:
  - P1 and P3 use the same measured-payment / P&I-share selector, in the same words.
  - P1, P3 and P5 use the same farm-standing test: "active farm real estate loan AND at least two farm principal installments paid AND no farm loan late charge in the last 24 months".
  - P2 and P6 use the same member-owner test: Class B Voting Stock active, and cash patronage paid in 15 months.

  In each pair the wording and the compute agree, so there is no cross-policy conflict.
- **P5 / P6 and the same base clause.** Both supersede the escrow-waiver LTV clause of `homeloan_escrow_waiver_rule`. P6's replacement defers to P5's limit, value and tested balance, so they are compatible. All other base waiver conditions are inherited by P6 and stay in force: request on file, outside SFHA, mortgage insurance no longer in force, at least 12 payments due since closing, no payment 30+ days late in the last 12 months, no payment past due.
- **Triggers and time anchors.**
  - P1, P2 and P3 are `state_due`; P4, P5 and P6 are `on_request`.
  - The late-charge grace boundary is inherited from base (more than 15 days, due date = day 0).
  - Most look-backs use DSL `within_months`, meaning `0 <= MONTHS(date, today) < N`.
  - Two do not: P6's "since the last payment due date" is implemented as `within_months=1` (see F-9), and P5's "next escrow analysis" is implemented as last analysis + 365 days (see F-10).
- **Terminal states.** P3 books back the reversed shares, pays fees and books any curtailment. P4 deposits the lump sum to escrow. P5 posts a curtailment. P6 sets escrow_waived, sets the monthly escrow deposit to 0, books the fee and approves the pending request. None of them conflict.
- **Cross-category reads.** P1, P3 and P5 read farmland (status, `farmland_transactions` principal payments and late charges; P5 also reads `farmland_parcels` farmstead-split releases). P2 and P6 read equity (Class B status and `equity_patronage_cash_paid`). All of these fall inside the blueprint's read-only facts for this difficulty.
- **Scope partition.** I inferred this from the graph only; `charter_scope` stays masked. The prerequisite graph has exactly two weakly connected components, {P1, P2, P3, P4} with root P4 and {P5, P6} with root P6. With M=2, the only partition that is pairwise exclusive and jointly complete is task A = {P1..P4} and task B = {P5, P6}. I verify the actual claims at the reveal in each task file.

### rule_compute_equivalence

I swept every binding's `compute_basis` quotation back against the `rule`. All quotations are verbatim sentences of their own rule. The defects found:

- **P1 `relief`.** The rule names only three cases: full relief, partial relief, and "a member with no active farm real estate loan earns no relief". The ladder's fall-through ("otherwise (no active farm real estate loan, or one without two recent paid installments)") and the compute's `else 0` also cover an *active* farm loan with fewer than two principal installments paid and no late charge in 24 months. The rule states no treatment for that case, and its opening sentence ("A member who also holds a farm real estate loan in active status ... earns relationship relief on a late charge") implies an active holder earns some relief. That tier exists in compute and ladder but not in the rule. → F-7.
- **P1 `measured` and P3 `pi_share`.** The compute adds `rev_pi > 0` to tier 1; the rule says only "differs from the principal and interest that the most recent returned remittance reversed". This is harmless because with no return, `rev_pi = 0` differs and the compute falls to the record payment, which matches the rule's intent. Observation only.
- **P2 `ret_channel`.** The rule says the look-back "depends on how the returned remittance was made". The compute instead takes the channel of the **latest scheduled principal payment on the loan** (`LATEST(... event_type='homeloan_principal_payment', payment_purpose='scheduled')`). That is the returned remittance only when no later scheduled payment exists. → F-8; the consequence is shown per task.
- **P3 `fees_carried`.** "Left a monthly payment's billed interest unpaid" is implemented as `F('accrued_interest') > 0`, i.e. any billed interest unpaid on the loan. "Less that premium" is the 12-month SUM of `lender_placed_insurance` assessments, whether or not they were later paid or waived. Observation; consequence per task.
- **P3 `esc_share`.** As stated, tiers 1 (latest analysis later than the reopened due date) and 2 (escrow waived) overlap; the compute resolves the overlap to tier 2. The tool clears `last_escrow_analysis_date` on a waiver, so the overlap cannot arise through tools. Observation.
- **P4 tax projection.** The rule says "each property tax bill ... projected at the amount of its latest bill". The compute projects one bill (`tax_last`, placed at `tax_k`), and sets "the property tax bill before it" to `tax_prior = SUM(24 months) − tax_last`, which is right only when exactly two tax bills fall in the 24 months. The homeowner's premium is handled the same way (`haz_prior`). → F-13; consequence per task.
- **P4 `haz_k`.** Rule tier 1 says the expiry "falls in one of the twelve months of the projection" (projection months 0..11 from the next due date). The compute uses `1 <= exp_k <= 12`. At `exp_k = 0` the rule's tiers 1 and 2 overlap, and at `exp_k = 12` the compute applies tier 1 where the rule does not. → F-11; consequence per task.
- **P4 `mi_left`.** The compute counts scheduled balances `B(n0+j)`, j = 0..11, with `n0 = MONTHS(opened_date, next_due_date)`. That equals the payment number of the next due date only when `opened_date` is not the 1st of a month (MONTHS drops one month when day2 < day1). → F-14; consequence per task.
- **P4 `cushion_base`.** As stated, tier 1 ("MI in force and projected for fewer than twelve months") and tier 2 ("... projected for twelve months or not at all") overlap when MI is in force but projected for 0 months. Observation; consequence per task.
- **P5 `to_post`.** The rule does not say how "its next escrow analysis" is dated. The compute uses `365 − DAYS(last_escrow_analysis_date, today)`. Base `homeloan_escrow_analysis_rule` says the analysis runs "once a year in the month of the closing anniversary". → F-10; consequence per task.
- **P6 `recent_extra`.** The rule says "since the last payment due date"; the compute uses `within_months=1`, i.e. the calendar month back from today, which includes days before the last due date. → F-9; consequence per task.
- **Everything else** (windows, rounding points, caps/floors, the order of operations in each `result`) has its verbatim basis. The baseline sentences of all six `baseline.rule`s are sentences of their own `rule` (mechanical check, no misses).

### action_binding_and_uuids

- Each of the six `(target_tool, computes)` pairs is claimed by exactly one policy, and no tool is shared.
- No tool body checks status, eligibility, ownership, timing or any prerequisite, and none returns a refusal (I read all six bodies; `_Ledger` holds helpers only).
- The docstrings name no other tool and carry no sequence words. "after the booking" / "after the deposit" describe the tool's own receipt. "In the order they were assessed" (`apply_replacement_remittance_c604a214`) orders fees inside the one write.
- Tool effect vs. policy for P3: the tool books back the interest, principal and escrow **that the return reversed on that bill**, whatever the policy's P&I-share or escrow-share tier is. It then pays unpaid fee assessments oldest first and books any remainder as a curtailment. This matters for F-4 below.
- uuid8s (eed44226, 25e49e31, c604a214, 8ff65e44, d2fdfc16, 439c8464) are pairwise distinct, share no prefix or suffix, and are not sequential. They look independently generated.

### prerequisite_graph

- `prerequisite` is filled in on all six policies (P1, P2 and P5 are `[]`).
- Edges: P3→P1, P3→P2, P4→P3, P6→P5. Every `problem` is an extended policy id of this file, none is base, none points at itself, and the graph is acyclic.
- Every `policy_source` is verbatim in the blocked policy's own rule (mechanical check, all True).
- `form` / `fallback_reason`: three state-form edges without `fallback_reason`, and one action-form edge (P6→P5) with one.
- Every `gate` is a binding of the blocked compute: P3 `fees_owed`, P4 `bal`, P6 `ltv`. All edges are `value_input`.
- `resolved_by` is the depended-on `target_tool` in each case. Each effect does what it says:
  - the late charge and the returned-payment fee raise `fees_due` (both tool bodies do `fees_due += amount`), and P3 reads `F('fees_due')`;
  - the replacement raises `escrow_balance` by the reversed escrow, and P4 reads `F('escrow_balance')`;
  - the paydown lowers `principal_balance`, and P6 `ltv` reads it once the loan is 12 or more months old.
- Conditions vs sentences:
  - P4→P3: the sentence is "no monthly payment ... stands unpaid past its due date". The `condition` restates it as "billed interest unpaid" plus "shares booked again". That is slightly narrower but points at the same handling-time state. Observation.
  - P6→P5: the sentence turns on the **tested balance** ("When the tested balance is above the escrow waiver limit"). The `condition` instead tests "the **principal balance** ... less the scheduled principal still to post". P5's tested balance adds billed interest and unpaid fees when present, so the condition is weaker than the sentence wherever such balances exist. This is an observation at charter level; I check per task whether the world puts fees or interest in the tested balance.
  - P6→P5 `effect` asserts a world-specific outcome ("falls from the band above high_band_ltv_pct into the middle band") in a general-text field. That is authoring viewpoint. Observation (F-17).

### prerequisite_sentences

- **P3 ← P1 (state).** "A replacement remittance is not figured until the ledger carries a late charge for every reopened monthly payment whose grace period has ended."
  - Connective: "not ... until". The waited-on state is a ledger row of kind "late charge" against a reopened monthly payment. It names no tool, id or snake_case token, and its scope ("every reopened monthly payment whose grace period has ended") matches the condition.
  - Exactly one write in this difficulty books a late charge (assess_late_charge_eed44226, the target of P1, whose rule "figures the late charge owed on a monthly payment that is still not paid in full after its grace period").
  - Derivation: sentence + `homeloan_transactions` (the reopened bill and the late-charge row missing against it) + P1's rule → book P1's charge first. One reading.
- **P3 ← P2 (state).** "A replacement remittance is figured only after the ledger carries a returned-payment fee for every returned remittance whose return reason calls for one."
  - Connective: "only after". The state is a returned-payment fee row. Exactly one write produces it (assess_returned_item_fee_25e49e31, target of P2).
  - "Whose return reason calls for one" leans on P2's/base's "none when the return reason is unauthorized". It is closed, and named by kind. One reading.
- **P4 ← P3 (state).** "The shortage paid at once is fixed only after no monthly payment on the loan stands unpaid past its due date."
  - Connective: "only after". The state is record-visible: monthly bills and their payments.
  - In this difficulty the only write that pays a monthly bill is apply_replacement_remittance_c604a214. P5's paydown is a curtailment, which base `homeloan_payment_application` says "never advances the next due date" and which pays no bill. So one write and one reading — provided the world's only past-due bill is one a returned remittance reopened (checked per task).
- **P6 ← P5 (action).** "When the tested balance is above the escrow waiver limit, the escrow waiver is not recorded until the member's paydown of the difference has been posted."
  - Connective: "not ... until". It names the action in business words.
  - Testing the `fallback_reason`: the state the waiver waits on (tested balance at or below the limit) can also be reached by the curtailment remainder of a replacement remittance (`apply_replacement_remittance_c604a214` books leftover money as `payment_purpose=curtailment`, the same row kind as the paydown). The state alone therefore does not single out P5's write, and the fallback is justified.
- **Depended-on rules.** None restates the blocking sentence (P1, P2, P3 and P5 rules read).
- **Docstrings.** None states sequence.
- **Second wording (observation, F-16).** P6's rule also says "A waiver requires that the loan meets the escrow waiver loan-to-value limit, with the limit, the value and the tested balance as the escrow waiver paydown rule sets them out". This is a second, state-form wording of the same P6←P5 dependency, and it names the other rule by business name. It does not conflict with the action sentence (both say the limit must be met first), so I record it as an observation.
- **Undeclared cross-problem orders.** None found in the six extended rules. The base sentence "If the reopened month is now past its grace period, its late charge is assessed under homeloan_evt_late_charge" states a consequence, not an order between problems.

### override_declarations

Sentence by sentence against each `base_policy_refs` entry:

- **P1.** `homeloan_evt_late_charge`:
  - grace sentence: followed (inherited by "the grace period ... are those of the late charge rule of the product");
  - "It applies to ... at late_charge_pct of ... monthly_pi_amount, no less than late_charge_min_usd and no more than late_charge_max_usd, rounded to cents, with source_ref_id the monthly bill": **superseded, declared**. The replacement changes the measured payment, the rate, the floor and adds relief, all of them quantities inside the named clause;
  - one-per-payment: followed;
  - no charge on escrow part / forborne month / nonaccrual: followed;
  - waiver sentences: not touched.

  `homeloan_evt_returned_payment` "If the reopened month is now past its grace period, its late charge is assessed": followed. The other refs (escrow waiver, MI, recast, insurance) govern no quantity P1 scores. No undeclared override.
- **P2.** `homeloan_evt_returned_payment` "One returned payment fee of returned_payment_fee_usd is assessed per returned remittance (booked from the principal return row) unless the return reason is unauthorized": **superseded, declared**. The size limit and the owner relief also deviate from that same clause; the clause is named, but `replaced_by` carries only the count tiers (observation, F-15). The reversal and reverse-once sentences are followed. No undeclared override.
- **P3.** `homeloan_payment_application`:
  - "Money left after every monthly payment due is paid goes to principal as a curtailment, unless the member designates it for a fee ...": **superseded, declared**;
  - "A remittance pays the oldest unpaid monthly payment first ... interest, then principal, then the escrow deposit ...": followed by the tool;
  - "a remittance smaller than a full monthly payment is not applied": **conflicts with P3's own forbearance tier** (P&I share "nothing"), which is undeclared. This only shows on a world with a running forbearance plan; see F-4.

  `homeloan_escrow_analysis_rule`: followed (an escrow deposit changes at analysis; tier 1 of `esc_share` agrees).
- **P4.** `homeloan_escrow_analysis_rule`:
  - the projection sentence (with its measure "each at the amount of the latest bill of the same kind") is **superseded, declared**, but `replaced_by` carries only the tax growth allowance. The insurance renewal allowance, the insurance due-month rule and the MI-months rule also depart from the named sentence, and their replacement text lives only in the extended rule (observation, F-15);
  - the cushion sentence: **superseded, declared**;
  - shortage / lump-sum sentence: followed;
  - "Escrow is analysed once a year in the month of the closing anniversary": P4 figures a shortage on request on any day, "on the escrow account as it stands when the member pays", over the 12 months from the next due date. The base analysis window starts at the analysis date. The superseded projection sentence covers the window. Whether the base deposit already includes a shortage spread is checked per task (observation).

  `homeloan_payment_application` "designates it ... as a lump-sum escrow shortage payment": followed.
- **P5.** `homeloan_escrow_waiver_rule` LTV clause: **superseded, declared**. The value base (split appraisal / acreage haircut), the tested balance (with interest and fees) and the seasoning margin all deviate inside that named clause; `replaced_by` carries only the limit tiers (observation, F-15). `homeloan_payment_application` "A remittance pays the oldest unpaid monthly payment first": P5 always books the paydown as a curtailment, including on its own tested-balance tier 1 ("a monthly payment is unpaid past its due date"). That conflict is undeclared but arises only on a past-due world, and base waiver conditions refuse a waiver there anyway (observation, F-18).
- **P6.** `homeloan_escrow_waiver_rule` fee clause and LTV clause: **both superseded, declared**. Request, flood, MI, seasoning, 30-day-late and past-due conditions are inherited and stay in force. No undeclared override.

### factor_ladders

Effect labels, decides, tier counts, multi-source and cross_difficulty, as declared; my structural verdicts follow.

| policy | factor | label | decides | tiers | multi-source tiers | xdiff |
| --- | --- | --- | --- | --- | --- | --- |
| P1 | measured_payment | method | measured | 3 | tier 1 (loan record + return rows + forbearance field) | – |
| P1 | late_rate | parameter | rate | 3 | no (one count) | – |
| P1 | relationship_relief | parameter | relief | 3 | yes (farm loan status + farm ledger) | farmland |
| P1 | charge_floor | parameter | floor | 3 | yes (opened_date + late-charge rows) | – |
| P2 | return_lookback | method | others | 3 | no | – |
| P2 | returned_item_fee | parameter | item_fee | 4 | partly (reason + count) | – |
| P2 | returned_item_limit | parameter | fee_limit | 3 | no | – |
| P2 | member_owner_relief | parameter | owner_relief | 3 | yes (equity holding + equity ledger) | equity |
| P3 | pi_share_carried | parameter | pi_share | 3 | tier 1 | – |
| P3 | escrow_share_carried | parameter | esc_share | 3 | tier 1 (analysis date + return due date) | – |
| P3 | fees_carried | method | fees_carried | 3 | yes | – |
| P3 | fee_carry_limit | parameter | fee_limit | 3 | yes | farmland |
| P4 | tax_growth_allowance | parameter | tax_allow | 3 | no | – |
| P4 | insurance_renewal_allowance | parameter | ins_allow | 3 | no | – |
| P4 | insurance_due_month | method | haz_k | 3 | yes (expiry on loan + escrow bills) | – |
| P4 | mortgage_insurance_months | method | mi_months | 3 | partly | – |
| P4 | cushion_base | method | cushion_base | 3 | yes | – |
| P5 | waiver_limit | parameter | limit_pct | 3 | yes (occupancy + farm ledger) | farmland |
| P5 | seasoning_margin | parameter | margin | 3 | no | – |
| P5 | waiver_value | method | value | 3 | tier 1 farm parcel / tier 2 acres | farmland |
| P5 | tested_balance | method | tested | 3 | yes | – |
| P5 | principal_to_post | method | to_post | 3 | yes | – |
| P6 | fee_rate_band | parameter | fee_rate | 3 | no | – |
| P6 | occupancy_addon | parameter | addon | 3 | same record only | – |
| P6 | member_owner_discount | parameter | owner_disc | 3 | yes | equity |
| P6 | seasoning_credit | parameter | season | 3 | yes | – |
| P6 | fee_basis | method | basis | 3 | yes | – |
| P6 | autopay_credit | parameter | autopay_credit | 3 | yes | – |

What holds:
- Every factor's `decides` is an input, not `result`, and the binding sets within each policy are disjoint.
- Every factor's fall-through tier equals its `baseline`.
- Every ladder is stated in its rule, apart from P1 relief's gap (F-7).
- Declared counts are within bounds: 4–6 factors per policy, at least 2 `parameter` and at least 1 `method` per policy as labelled.
- Per inferred task, there is at least one multi-source factor and at least one cross_difficulty factor: task A has P1 relief, P2 owner relief and P3 carry limit; task B has P5 limit and value, and P6 owner discount.

The structural defects follow.

- **F-1 (SOURCE-FACTOR RED, mislabelled effect): P2 `return_lookback` is a parameter, not a method.**
  - The tiers are "count them in the 18 / 6 / 12 months up to today". All three compute the same `COUNT(homeloan_transactions, event_type=homeloan_principal_payment_return)` and only substitute the window length (`ret_18`, `ret_6`, `ret_12`, then `− 1`). That is a threshold-like number in one formula.
  - Counting only honest labels, P2 has 0 `method` factors (returned_item_fee, returned_item_limit and member_owner_relief are all parameter), which is below the bound of 1.
  - Bears on the task whose tree contains P2.
- **F-2 (SOURCE-FACTOR RED, mislabelled effect): P1 `measured_payment` and P3 `pi_share_carried` carry the identical ladder under opposite labels.**
  - Both ladders read: "differs from the reversed P&I, no forbearance → the reversed P&I; forbearance → nothing / 0; otherwise → monthly_pi_amount on the record". P1 calls it `method`, P3 calls it `parameter`, so one label is dishonest.
  - If the selector is a parameter (it substitutes a number into `gross = measured × rate / 100`), P1 has 0 honest `method` factors.
  - If it is a method, then P3's `escrow_share_carried`, which is the same kind of selector (reversed deposit / 0 / record deposit), is a method too. P3 is then left with 1 honest `parameter` (fee_carry_limit), below the bound of 2.
  - Either way one of P1/P3 fails its bounds. Bears on the task containing P1 and P3.
- **F-3 (SOURCE-FACTOR RED, unreal ladder: the condition restates scope): P3 `fees_carried`.**
  - Both non-fall-through tiers begin "a returned remittance in the last twelve months left billed interest unpaid" (compute: `ret_12m > 0 and F('accrued_interest') > 0`).
  - P3's own scope is "a monthly payment that a returned remittance reopened". Base `homeloan_evt_returned_payment` reverses the interest row of that payment, and the `interest_accrued` account is "raised by ... returned interest payments". So every customer who reaches this write satisfies that conjunct, the ladder only separates "LPI premium assessed in 12 months: yes / no", and the fall-through "carry no fee" is unreachable for any customer in scope.
  - The ladder therefore has two real tiers, below the minimum of three. Bears on the task containing P3.
- **F-4 (SOURCE-FACTOR RED, unreal ladder): P3 `pi_share_carried`.**
  - (a) Every customer in scope has a returned remittance, so `r_pi > 0`. The fall-through (`monthly_pi_amount`) is then taken only when `monthly_pi_amount == r_pi`, and its value equals tier 1's value (the reversed P&I). Tier 1 and the fall-through select the same value over the policy's whole domain.
  - (b) Tier 2 ("a forbearance plan is running → the share is nothing") contradicts the same rule's first sentence, "the reversed interest, principal and escrow shares are booked again", and the tool body, which books the reversed interest and principal whatever the remittance.
  - Consequence: on a forbearance world the remittance figured would be smaller than the shares the tool books, and the booked amounts would exceed the remittance (`left` goes negative, so no fee and no curtailment are booked, while interest and principal are still booked in full). Base also says "a remittance smaller than a full monthly payment is not applied". No servicer publishes that treatment.
  - Bears on the task containing P3. The tier-2 half is shown only at charter level, because no task world needs to be in forbearance.
- **F-5 (SOURCE-FACTOR RED, unreal tier value): P1 `measured_payment` tier 2.**
  - "When a forbearance plan is running, the charge is measured on nothing". The `result` then raises the figure to the floor, so a late charge of exactly the floor ($10 / $12.50 / $15) is booked.
  - Base (inherited) already says "No late charge is assessed ... on a forborne month". The only month tier 2 can reach is therefore a non-forborne month that had a scheduled payment, while a plan runs. Charging a fixed floor measured on a zero payment is not a treatment a mortgage servicer publishes.
  - Bears on the task containing P1, at charter level only.
- **F-6 (SOURCE-FACTOR RED, unreal condition): P5 `principal_to_post` tier 2.**
  - "When ... its next escrow analysis is within analysis_window_days days, the principal shares of that next payment and of the one after it are taken off". The timing of the escrow analysis has no bearing on how much scheduled principal posts before a waiver.
  - The waiver tool records the waiver at once; it is not deferred to the analysis. Even on the rationale "the waiver waits for the analysis", the ladder is inverted: an analysis farther away would mean *more* payments post, yet tier 1 takes off fewer.
  - No servicer weighs escrow-analysis proximity when settling scheduled principal to post. Bears on the task containing P5.
- **Observations (not grounds for rework):**
  - P4 `mortgage_insurance_months` and `insurance_due_month` substitute a count / month index into one projection. I accept the method label because tier 2 of the former derives the count from an amortization schedule, and the latter moves the disbursement within the running balance. P4 keeps `cushion_base` as an honest method in any case.
  - P2 `return_lookback` windows by channel, and P3 `fee_carry_limit` (farm standing limits the fees carried), are unusual but not implausible for a cooperative.
  - P6 `fee_rate_band`'s "a loan open fewer than 12 months is measured on its original principal", and P5 `tested_balance` tier 1 (a payment past due), describe customers the inherited base waiver conditions exclude. Those conditions are "at least escrow_waiver_min_months_seasoning (12) monthly payments have come due since closing" and "no payment is past due" (F-18).

### findings

| id | verdict | short | bears on |
| --- | --- | --- | --- |
| F-1 | SOURCE-FACTOR RED | P2 return_lookback mislabelled method; P2 has 0 methods | task with P2 |
| F-2 | SOURCE-FACTOR RED | identical selector labelled method in P1, parameter in P3 | task with P1+P3 |
| F-3 | SOURCE-FACTOR RED | P3 fees_carried first conjunct restates scope; fall-through unreachable | task with P3 |
| F-4 | SOURCE-FACTOR RED | P3 pi_share tier 1 = fall-through value; forbearance tier contradicts own rule and tool | task with P3 |
| F-5 | SOURCE-FACTOR RED | P1 forbearance tier charges a floor measured on nothing | task with P1 |
| F-6 | SOURCE-FACTOR RED | P5 to_post tier 2 conditions on escrow-analysis proximity | task with P5 |
| F-7 | SOURCE-POLICY RED | P1 relief: active-farm, <2 paid, no late case lives in compute/ladder only | task with P1 (consequence per world) |
| F-8 | SOURCE-POLICY (per world) | P2 ret_channel reads latest scheduled payment, not the returned one | task with P2 |
| F-9 | SOURCE-POLICY (per world) | P6 recent_extra within_months=1 vs "since the last payment due date" | task with P6 |
| F-10 | SOURCE-POLICY (per world) | P5 "next escrow analysis" undefined; compute last+365 vs base anniversary month | task with P5 |
| F-11 | SOURCE-POLICY (per world) | P4 haz_k: projection months 0..11 in rule vs 1..12 in compute | task with P4 |
| F-12 | observation | P4 cushion_base tiers overlap at MI in force projected 0 months | task with P4 |
| F-13 | SOURCE-POLICY (per world) | P4 projects one tax / hazard bill; "bill before it" = 24-month sum − latest | task with P4 |
| F-14 | SOURCE-POLICY (per world) | P4 mi_left payment index off by one when opened on the 1st | task with P4 |
| F-15 | observation | replaced_by carries only part of the deviation from a named base clause (P2, P4, P5) | — |
| F-16 | observation | P6 rule carries a second, state-form wording of the P6←P5 dependency naming the other rule | task with P6 |
| F-17 | observation | P6←P5 `effect` asserts a world-specific band move in general text | task with P6 |
| F-18 | observation | P5 tested tier 1 / P6 <12-month band measure apply only to customers base excludes from a waiver | task with P5/P6 |
| F-19 | SOURCE-POLICY RED | P6 rule says a paydown "does not lower the fee", but its band reads the post-paydown principal | task with P5+P6 |

**F-19 (SOURCE-POLICY RED, the rule contradicts its own stated consequence).** I added this to the charter-global section before any reveal. It rests on the charter text alone; the per-task consequence is in the task file.
- Passage A, P6 rule: "when an extra principal payment has been posted since the last payment due date, the fee is figured on the principal balance before those extra payments, **so a paydown made to meet the limit does not lower the fee**".
- Passage B, same rule: "The fee rate depends on the loan-to-value ratio, **the principal balance** divided by the original value".
- When a paydown moves the LTV across `high_band_ltv_pct` or `mid_band_ltv_pct`, B makes the paydown lower the fee, through the band. That is exactly what the P6←P5 edge's own `effect` says it does: "the loan-to-value ratio the fee rate band reads (ltv) falls from the band above high_band_ltv_pct into the middle band".
- A reader who honours A's stated outcome measures the band on the principal before the extra payments as well. That reader gets a second fee, and the value_input edge stops bearing weight on the fee.
- The two passages reach different conclusions on the same world.

The "per world" items are RED in a task file only where that task's world actually exhibits the divergence; otherwise they stay observations there.

## closing_checklist

Written after both reveals (2026-10-11T08:18–08:19Z). Everything above this heading was frozen first (`_difficulty.md` sha256=3e8200b1… at 08:17:08Z) and has not been edited since.

- Per-task files `0.md` and `1.md` correspond one-to-one with `tasks/0.json` and `tasks/1.json`. This is the first revision, so there are no older revisions. **Not every comparison section carries a PASS:**
  - task 0: policy PASS on its world · SOURCE-CHAIN RED · SOURCE-FACTOR RED · unique solution PASS;
  - task 1: SOURCE-POLICY RED · SOURCE-CHAIN RED · SOURCE-FACTOR RED · SOURCE-TASK RED.
- Coverage and scope: met. Task 0 claims P1–P4 with tools eed44226 / 25e49e31 / c604a214 / 8ff65e44. Task 1 claims P5–P6 with tools d2fdfc16 / 439c8464. The scopes are pairwise disjoint, cover all six extended policies, and each spans the whole tree. The uuid8s are independent (§action_binding_and_uuids).
- Trees: task 0 has 3 prerequisites with 3 value_input edges; task 1 has 1 prerequisite with 1 value_input edge. Each has an `owner=user` write (pay_escrow_shortage, make_principal_paydown). The difficulty-wide graph is acyclic. Task 1's value_input edge stops bearing weight under the second reading of F-19.
- Factors: **not met.**
  - Charter structure: F-1, F-2, F-3, F-4, F-5, F-6.
  - Every declared factor does bear weight on its task's world against an honest baseline. Each baseline alone gives a definite number different from gold: 57.84, 30.00, 1787.19, 825.56, 0 and 576.12.
- Gates: not re-run by this auditor (Step 0 says the auditor cites them and does not run them). The coordinator snapshot is cited in §charter_global_frozen. The replay FK lines are confirmed as a gate artefact.
- **Status: this difficulty does not pass the source-layer audit.** The REDs to settle:
  - charter: F-1..F-7, F-19;
  - task 0: T0-F5;
  - task 1: T1-F1, T1-F3.

---

## revision_2

### charter_global_frozen (revision_2)

- Frozen 2026-10-11T11:28Z, before either round-2 task file was opened. The auditor is the same independent auditor.
- Inputs:
  - `homeloan.extended.yaml` sha256=f719490649f2c84dea36d5ad2423c30506a4c84b426af54b5810a9148683ac49. This **changed** from round 1, so the charter-global section is re-derived in full below.
  - `task_tools.py` sha256=776849404acc7293b622296bcf5357bdf91bac201c58969e417bcaea36ea8201, unchanged.
  - The blueprint files are unchanged (mtimes 2026-10-11T00:06–00:08Z, before round 1).
- Base copy: lines 1–1455 are still byte-identical to `blueprint/products/homeloan.yaml`.
- Masked fields and isolation are the same as round 1. The round-1 text above is left untouched.
- Gate snapshot (coordinator, cited not re-run): every gate is green except replay. Replay is NOT OK only on the BLUEPRINT-KNOWN `loan_id` dangling-FK lines. I re-checked the ruling: in both round-2 worlds the farmland_transactions rows carry the farmland_loans PK.
- The reworker's closure claims were taken as item ids only. Each one is verified below against the artifact itself.

### policy_conflict_scan (revision_2)

- Extended policies, ids, target tools, owners, `computes`, the prerequisite graph and the inferred scope partition are the same as in round 1.
- Shared tests are still consistent across policies:
  - the farm-standing test in P1, P3 and P5;
  - the member-owner test in P2 and P6.
- New cross-category reads, both inside the blueprint's read-only facts:
  - P2 now reads farmland `autopay_enrolled` and farm `farmland_principal_payment_return` rows;
  - P6 now reads `farmland_parcels`.
- **New overlap (observation N-4):**
  - P5's "value the limit is applied to" includes a large-homesite haircut tier;
  - P6's band "waiver value" is defined separately as "the lower of the home's original value and any appraised value recorded when the homesite was released … as a farmstead split", with no haircut;
  - for a homesite over 20 acres the two give different denominators under near-identical names.
  - Neither task world has such a homesite, so there is no task consequence.

### rule_compute_equivalence (revision_2)

The `compute_basis` sweep finds every quotation verbatim and every compute binding with a basis (mechanical check, no misses). Per item:

- **F-7 closed.** P1's relief rule now states the gap case: "any other member, including one with no active farm real estate loan and one whose active farm loan shows fewer than two farm principal installments paid and no farm loan late charge in those 24 months, has no relief". Rule, ladder and compute agree.
- **F-8 closed.**
  - P2 `ret_channel` now reads `LATEST(... event_type='homeloan_principal_payment_return')` channel.
  - The rule now says "as the channel on its return entries shows".
- **F-9 closed by removal.** P6 `recent_extra` is gone. The fee basis is now original principal for loans open under `basis_seasoning_months`.
- **F-10 closed by removal.** P5 `principal_to_post` no longer reads the escrow analysis.
- **F-11 closed.**
  - The rule now reads "the second through the twelfth month of the projection, the months being counted as whole months from the next payment due date".
  - The compute uses `1 <= exp_k <= 11`, and tier 2 uses `exp_k < 1`. The tiers are disjoint.
- **F-12 closed.** `cushion_base` tier 1 now reads "at least one and fewer than twelve months" (compute `mi_months >= 1 and mi_months < 12`), which is disjoint from tier 2's "twelve months or not at all".
- **F-13 partly closed.**
  - The "earlier bill" is now defined as the tax / premium "paid between 12 and 24 months before today" (compute: SUM 24 months − SUM 12 months), so rule and compute agree on it.
  - Still open: the projection sentence "each property tax bill … projected at the amount of its latest bill" is implemented as one projected bill.
  - On a semiannual-installment world the rule projects two bills and the compute one. This remains a per-world item; it is not triggered by either round-2 world.
- **F-14 closed by definition (observation N-5).**
  - The rule now defines "the scheduled balance on a due date being the balance after as many payments as there are whole months from the closing date to that due date", which is what `n0 = MONTHS(opened_date, nd)` does.
  - For a loan closed on the 1st this counts one payment more than has been scheduled (first due date = 1st of the second month). The definition is coherent, but it is not how a servicer counts.
  - Not triggered in either world.
- **New: farm "installments paid" (observation N-3).**
  - P1, P3 and P5 count `farmland_principal_payment` rows, including payments later reversed by a `farmland_principal_payment_return`.
  - The rules say "farm principal installments paid".
  - Consequence per world only.
- **New: P3 `fees_carried` tier 2 (observation).**
  - The rule says "the fees assessed on the loan in the month up to today, … as far as they are unpaid".
  - The compute uses `MN(fees_owed, fees_month)`, where `fees_month` is the SUM of *assessed* amounts. That is exact only when no older fee is unpaid and no recent fee is partly paid.
- **Unchanged:** all other windows, rounding points and orders of operation agree.

### action_binding_and_uuids (revision_2)

- `task_tools.py` is unchanged (same hash), so round-1 §action_binding_and_uuids carries forward on the hash.
- Each `(target_tool, computes)` pair is still claimed once.
- New P3 tier "final scheduled payment → interest billed plus the whole principal balance" against the tool body: the tool books the reversed shares, pays fees, then books the remainder as a curtailment. A final-payment remittance therefore pays off principal through the curtailment row. That is consistent with base "The final payment is the billed interest plus all principal outstanding".

### prerequisite_graph (revision_2)

- The edges are unchanged in shape (P3→P1, P3→P2, P4→P3, P6→P5), all value_input. The graph is acyclic.
- `policy_source` is verbatim in each blocked rule.
- **F-17 closed.** P6 edge `effect` is now general text: "the loan-to-value ratio the fee rate band reads (ltv) is figured on the lower principal".
- **Round-1 observation on the P6 edge condition closed.** The P6 `condition` now speaks of "the tested balance … (principal balance, plus billed interest and unpaid fees where the paydown rule adds them)", matching the sentence.

### prerequisite_sentences (revision_2)

- The four sentences are unchanged and pass the four-point test as in round 1.
- **F-16 closed.** P6's rule no longer carries the second wording "with the limit, the value and the tested balance as the escrow waiver paydown rule sets them out". The only dependency sentence is the action-form prerequisite sentence. It is also P6's second `overwrite.replaced_by` for the base LTV clause.
- No rule names a tool or a policy id. No undeclared cross-problem order: every "after", "until", "before" and "first" in the six rules was read.
- **New, charter-level (N-2b): P2's new tier 2 makes the parallel edges P3←P1 and P3←P2 order-dependent on some worlds.**
  - For a returned one-time payment (phone, online banking or mobile app), P2 counts "the late charges booked on the home loan in the twelve months up to today", and P1 books exactly such a late charge for the reopened month.
  - Booking P1 first therefore raises P2's count by one. The P3 sentences pin both fees before P3, but nothing orders P1 against P2.
  - On such a world the two orders give two fees and two replacement remittances.
  - Per-world consequence; it is shown in a task file only where the returned remittance's return entries carry one of those channels.

### override_declarations (revision_2)

- P1: the `replaced_by` now begins "first the monthly principal-and-interest payment on the loan record is multiplied by the late charge rate". The measured-payment deviation is gone. The superseded clause is still named and still covers the rate, floor and relief deviations. No undeclared override.
- P2: `replaced_by` updated (fourth-return tier). The superseded clause is named. No undeclared override.
- P3: `replaced_by` updated to the new fee-carry tiers. The forbearance tier is gone. The base sentence "a remittance smaller than a full monthly payment is not applied" no longer conflicts (round-1 note closed).
- P4: two `replaced_by`s updated. F-15 remains an observation, as the reworker states: the insurance allowance, due month and MI months still depart from the named projection sentence without their own `replaced_by`.
- P5: unchanged (F-15 observation stands).
- P6: two overwrites. The LTV clause is now replaced by the prerequisite sentence itself. The fee clause is declared. No undeclared override.

### factor_ladders (revision_2)

| policy | factor | label | tiers | verdict |
| --- | --- | --- | --- | --- |
| P1 | repeat_count_basis (new) | method | 3 | label acceptable: tier 2 changes the counting rule (subtract error-corrected waivers), tier 1 anchors the count on an event. **Tier 2 vs fall-through: see N-1** |
| P1 | late_rate / relationship_relief / charge_floor | parameter | 3 / 3 / 3 | ok; F-7 gap now stated |
| P2 | returns_counted (new, xdiff farmland) | method | 3 | label honest: three different record sets. **Tier 2 is unreal: see N-2** |
| P2 | returned_item_fee | parameter | 5 | ok |
| P2 | returned_item_limit / member_owner_relief | parameter | 3 / 3 | ok |
| P3 | pi_share_carried | parameter | 3 | **F-4 closed**: tier 1 is now keyed on the bill's `rate_applied` vs the record rate, so the fall-through (record payment) can differ from the reversed P&I (e.g. a re-amortised payment at the same rate). The forbearance tier is gone; the final-payment tier matches base |
| P3 | escrow_share_carried | parameter | 3 | ok; tier 1 now carries "escrow not waived", so the round-1 overlap is closed |
| P3 | fees_carried | method | 3 | **F-3 closed**: the conjuncts are now "return reason not unauthorized" and "another remittance returned in 12 months", which divide in-scope customers; the fall-through (unauthorized → no fee) is reachable and is the baseline |
| P3 | fee_carry_limit | parameter | 3 | ok |
| P4 | five factors | 2 parameter, 3 method | 3 each | ok (F-11, F-12 closed) |
| P5 | principal_to_post | method | 3 | **F-6 closed**: tier 2 is now "next payment is the final scheduled payment → the whole principal is taken off", a treatment a servicer would apply; the escrow-analysis condition is gone |
| P5 | other four | — | 3 each | unchanged, ok |
| P6 | fee_rate_band (now xdiff farmland) | parameter | 3 | ok |
| P6 | fee_basis | method | 3 | rewritten (original principal for loans < 60 months; escrow advance; principal). F-19 passage A is gone. Label honest (a different base quantity per tier) |
| P6 | seasoning_credit | parameter | 3 | tier 2 adds "at least twelve scheduled principal payments booked"; "in the 12 months up to today" may attach to the returned-remittance clause only (observation; the compute counts the 12 months) |
| P6 | other three | — | 3 each | ok |

Counts, labels taken as honest after the closures:

| policy | parameter | method | xdiff |
| --- | --- | --- | --- |
| P1 | 3 | 1 | farmland |
| P2 | 3 | 1 | farmland, equity |
| P3 | 3 | 1 | farmland |
| P4 | 2 | 3 | — |
| P5 | 2 | 3 | farmland ×2 |
| P6 | 5 | 1 | farmland, equity |

Multi-source factors are present in every task.

Closure of the remaining round-1 factor items:
- **F-1 closed**: `return_lookback` is gone, and `returns_counted` is an honest method.
- **F-2 closed**: P1's measured-payment selector is gone, so the opposite-label pair no longer exists.
- **F-5 closed**: the forbearance "measured on nothing" tier is gone.

New defects found in this round:

- **N-1 (SOURCE-FACTOR RED, unreal ladder: two tiers are one).**
  - P1 `repeat_count_basis` tier 2 ("no courtesy waiver in those twelve months AND a late charge waived as an error correction → count the late charges assessed in the twelve months less those waived as error corrections") and the fall-through ("count every late charge assessed in the twelve months") select the same count on the whole fall-through domain.
  - The fall-through is taken only when no error-correction waiver falls in the 12 months (compute `error_12 > 0` gates tier 2). Tier 2's own method then subtracts zero: `lates_12 − error_12 = lates_12`.
  - So the ladder is one method, "count the 12-month late charges less those waived as error corrections", written as two tiers, plus the courtesy tier. That is two distinct tiers, below the minimum of three.
  - This is the same test that made F-4(a) RED in round 1.
  - Bears on the task containing P1. P1 is the policy's only method factor.
- **N-2 (SOURCE-FACTOR RED, unreal method; and N-2b above).**
  - P2 `returns_counted` tier 2 says, in one sentence, that "only the returns that left a monthly payment drawing a late charge count, taken as the late charges booked on the home loan in the twelve months up to today".
  - The measured set is every late charge, including late charges on months that were simply paid late with no remittance returned, and the reopened month's own late charge once P1 has booked it. It is not the set the sentence names.
  - Example: a member whose phone payment was returned once and who paid two other months late without any return gets "two other returned remittances" → third_return_fee_usd. No servicer counts ordinary late payments as returned items for an NSF fee.
  - Bears on the task containing P2; it is a per-world consequence (the tier is taken only for one-time-payment channels).
- **N-3, N-4, N-5:** observations, see above.

### findings (revision_2)

| id | round-2 status | evidence |
| --- | --- | --- |
| F-1 | closed | `return_lookback` removed; `returns_counted` tiers count different record sets |
| F-2 | closed | P1 measured selector removed |
| F-3 | closed | fees_carried conjuncts now divide in-scope customers; fall-through reachable |
| F-4 | closed | pi_share keyed on bill rate vs record rate; forbearance tier removed |
| F-5 | closed | P1 forbearance tier removed |
| F-6 | closed | escrow-analysis condition replaced by final-payment tier |
| F-7 | closed | gap case stated in rule |
| F-8 | closed | channel read from return entries, rule says so |
| F-9 | closed (removed) | recent_extra gone |
| F-10 | closed (removed) | analysis read gone |
| F-11 | closed | 1..11 in rule and compute |
| F-12 | closed | tier 1 "at least one" |
| F-13 | partly closed (per world, untriggered) | "earlier bill" defined; one projected tax bill vs "each property tax bill" remains |
| F-14 | closed by definition | see N-5 |
| F-15 | observation (unchanged) | — |
| F-16 | closed | second wording removed |
| F-17 | closed | effect generalised |
| F-18 | half closed | P6 <12-month measure gone; P5 tested tier 1 (past due) still names customers the base waiver refuses (observation) |
| F-19 | closed | passage A removed; band and basis no longer contradict |
| N-1 | **SOURCE-FACTOR RED (new)** | P1 repeat_count tier 2 = fall-through |
| N-2 | **SOURCE-FACTOR RED (new)** | P2 returns_counted tier 2 proxy counts every late charge |
| N-2b | per world (new) | P1/P2 parallel order-dependent under P2 tier 2 |
| N-3 / N-4 / N-5 | observation (new) | see above |

### closing_checklist (revision_2)

Written after both round-2 reveals (2026-10-11T11:30Z). The revision_2 charter-global section above was frozen first (`_difficulty.md` sha256=e4a5adf0… at 11:29:54Z) and has not been edited since.

- Files: `0.md` and `1.md` each carry a revision_2. The round-1 text is untouched.
  - task 0: policy PASS · chain PASS · **SOURCE-FACTOR RED** (N-1, N-2) · unique solution PASS;
  - task 1: PASS on all four.
- Coverage and scope: unchanged and met. Charter scopes {P1–P4} and {P5–P6} were confirmed at reveal: pairwise disjoint, complete, uuid8s independent.
- Trees: met. Task 0 has n = 3 with 3 value_input edges; task 1 has n = 1 with 1. Both have a user write; the graph is acyclic. Every closure figure re-derives exactly. The P1/P2 order is invariant on task 0's world.
- Factors: **not met**, for N-1 (P1 `repeat_count_basis`) and N-2 (P2 `returns_counted`).
  - Every declared factor bears weight on its world against an honest baseline.
  - The baselines alone give 57.84, 30.00, 1787.19, 825.56, 0 and 576.12, all definite and all different from gold.
- Gates: cited, not re-run (coordinator round-2 snapshot). The FK lines are a gate artefact.
- Round-1 REDs: **all closed**, namely F-1–F-8, F-11, F-12, F-16, F-17 and F-19; F-9 and F-10 by removal; T0-F1–T0-F5; T1-F1–T1-F3.
- Partial and observation items: F-13 is partly closed (one projected tax bill against "each property tax bill"; untriggered). F-14 is closed by definition (N-5). F-15 is an observation. F-18 is half closed.
- **Status: the difficulty still does not pass the source-layer audit.** Two new SOURCE-FACTOR REDs were introduced by the rework: N-1 in P1 and N-2 in P2 (with the N-2b order-dependence risk). Both bear on task 0. Task 1 passes.

---

## revision_3

### charter_global_frozen (revision_3)

- Frozen 2026-10-11T12:28Z, before either round-3 task file was opened.
- Inputs:
  - `homeloan.extended.yaml` sha256=0246fd882f3156a8fce70ef3370a61c26f8f630a882123b1e4d07bb2ab1fd251, **changed**, so the charter-global section is re-derived.
  - `task_tools.py` 77684940…a8201, unchanged; round-1 §action_binding_and_uuids carries forward on the hash.
  - The blueprint is unchanged (mtimes 00:06Z).
  - Base copy lines 1–1455 are still verbatim.
- Mechanical sweep, all clean:
  - every `compute_basis` quotation is verbatim in its rule, and every compute binding has a basis;
  - every `policy_source` is verbatim;
  - every superseded clause is found in its base rule and every `replaced_by` is in the extended rule;
  - every baseline sentence is in its rule.
- Gate snapshot cited from the coordinator. The FK lines are still a gate artefact.
- The worlds are unchanged: the coordinator's view hashes equal round 2's. Earlier revisions are untouched.

### What changed in the charter and the verdict on each claimed closure

| item | round-3 text / compute | verdict |
| --- | --- | --- |
| **N-1** (P1 `repeat_count_basis` tier 2 = fall-through) | Tier 2 is now "a hardship forbearance request on the loan was approved in [the twelve months] → only the late charges assessed within the whole months since that request was registered count". The error-correction exclusion is now global: "a late charge waived as an error correction never counting because it was never owed". | **closed**: tier 2 (anchor = forbearance request date) and the fall-through (12 months) give different counts in general. **But see R3-N1**: all three tiers are now one formula with a different window start. |
| **N-2** (P2 tier 2 proxy) | Tier 2 is now "only the other one-time payments returned on the home loan in the twelve months up to today count, a returned automatic debit not counting". Compute `one_12 - 1` counts return rows with channel phone, online_banking or mobile_app. | **closed**: it counts actual returned remittances, filtered by channel. That is a different record set, so the method label is honest. |
| **N-2b** (P1/P2 order dependence) | P2 no longer reads late charges. | **closed**: neither fee policy reads the other's write. |
| **F-13** (one projected tax bill vs "each property tax bill") | The rule now says "the property tax is projected as one bill at the amount of the latest property tax bill paid from escrow and the homeowner's premium as one bill …". `baseline.rule` was updated the same way. | **closed** (rule = compute). Residual observation: on a semiannual world the "earlier bill" (tax paid 12–24 months ago) is a sum of two installments compared with one latest installment. Untriggered. |
| **F-14 / N-5** (payment number) | The rule now says "the payment being numbered as the amortization months less the whole months from that due date to the maturity date". Compute `n0 = amortization_months − MONTHS(nd, maturity_date)`. | **closed**: this is correct for any closing day. On task 0's world n0 = 360 − 276 = 84, same as before. |
| **F-18** (P5 past-due tier) | P5 `tested_balance` is now: escrow below zero → principal + fees unpaid + escrow advance; fees unpaid → principal + fees; otherwise principal. | **closed**: every tier is now reachable by a waiver-eligible customer. |
| **N-3** (reversed farm installments counted as paid) | P1, P3 and P5 rules now say "an installment whose remittance was returned not counting as paid". Compute subtracts `farmland_principal_payment_return` rows in the 24 months. | **closed** |
| **N-4** (P5 value vs P6 waiver value) | P6 now defines "the waiver value being the value the escrow waiver loan-to-value limit is applied to, namely …", including the >20-acre haircut with the same precedence. Compute `waiver_val` mirrors P5 `value`. | **closed** |
| P6 seasoning wording | "a loan open at least 24 months that in the 12 months up to today had at least twelve scheduled principal payments booked and no returned remittance". | **closed** |
| F-15 | Unchanged. | observation (unchanged) |

### New items this round

- **R3-N1 (SOURCE-FACTOR RED, mislabelled effect; a regression created by the N-1 rework).**
  - P1 `repeat_count_basis` is labelled `method`. After the rework its three tiers compute one formula, `COUNT(late_charge, within W) − COUNT(error-correction waivers, within W)`, and differ only in W:
    - tier 1: W = MONTHS(latest courtesy waiver, today);
    - tier 2: W = MONTHS(approved forbearance request, today);
    - fall-through: W = 12.
  - Evidence: compute `counted` is the same two-COUNT expression three times with `within_months=MONTHS(courtesy_last, NOW)`, `MONTHS(forb_last, NOW)` and `12`.
  - The tiers substitute a window start (a threshold) into the same count. That is the test that made F-1 RED in round 1 (`return_lookback`, windows of 18 / 6 / 12 months).
  - In round 2, tier 2 changed the counting rule itself (subtracting error corrections), which is why I accepted the label then. The round-3 rework moved that subtraction into all tiers, and only the window differences remain.
  - Counting honest labels, P1 now has **0 methods** (late_rate, relationship_relief and charge_floor are parameters), below the bound of 1.
  - Bears on task 0.
- **R3-N2 (SOURCE-POLICY, per world; observation unless triggered).**
  - P1's rule excludes "a late charge waived as an error correction".
  - The compute subtracts `COUNT(homeloan_fee_waiver, waiver_basis='error_correction')` with no `fee_code='late_charge'` filter, and counts by the waiver's date rather than the waived charge's.
  - Base `homeloan_insurance_requirement` and `homeloan_evt_late_charge` both issue `error_correction` waivers (a lender-placed premium waiver, a late-charge waiver). On a world with an error-corrected lender-placed premium in the window, the compute would lower the late-charge count where the rule does not.
  - Not triggered in task 0: there are no error-correction waivers.
- **Everything else re-checked and unchanged since round 2, passing:**
  - P3 (apart from N-3);
  - P4's due-month, MI-months and cushion-base tiers;
  - P5's limit, margin, value and to-post tiers;
  - P6's band, add-on, discount, basis and autopay tiers.
- **Prerequisite structure:** the four sentences, forms, `fallback_reason`, conditions and effects are as in round 2. The P6 condition now names "unpaid fees and any escrow advance", matching P5. No new cross-problem order. No tool names or ids in any rule.
- **Factor counts** (honest labels):

| policy | parameter | method | note |
| --- | --- | --- | --- |
| P1 | 3 | **0** | R3-N1 |
| P2 | 3 | 1 | — |
| P3 | 3 | 1 | — |
| P4 | 2 | 3 | — |
| P5 | 2 | 3 | — |
| P6 | 5 | 1 | — |

  Each task still has cross_difficulty factors and multi-source factors.

### closing_checklist (revision_3)

Written after the round-3 reveals (12:29Z). The revision_3 charter section above was frozen first (`_difficulty.md` sha256=b2a56fff… at 12:28:44Z).

- Task 0: policy PASS · chain PASS · **SOURCE-FACTOR RED** (R3-T0-F1 / R3-N1) · unique solution PASS.
- Task 1: PASS on all four.
- Round-2 REDs: N-1, N-2 and N-2b are **closed**. The claimed observation closures are **verified**: F-13, F-14 / N-5, F-18, N-3, N-4 and the seasoning wording. F-15 stays an observation.
- New: **R3-N1** (SOURCE-FACTOR RED), introduced by the N-1 rework. **R3-N2** (per world, untriggered).
- Scope, coverage, trees and the acyclic graph are unchanged and met. Every factor bears weight; every baseline gives a definite non-gold number. Gates are cited, not re-run.
- **Status: the difficulty does not yet pass.** One open RED remains: P1 `repeat_count_basis` has no method beyond window substitution, so task 0's P1 computation has 0 honest methods.

---

## revision_4

### charter_global_frozen (revision_4)

- Frozen 2026-10-11T13:07Z, before either round-4 task file was opened.
- Inputs:
  - `homeloan.extended.yaml` sha256=74708133e0e942fb4ae7bbadfa4dabbec3312ad6ecdf04962f9bec642759b9d3, **changed**;
  - `task_tools.py` 77684940…a8201, unchanged (round-1 §action_binding_and_uuids carries forward);
  - blueprint unchanged; base copy lines 1–1455 still verbatim.
- The worlds are unchanged (same view hashes as rounds 2 and 3).
- Mechanical sweep, clean: compute_basis verbatim, every binding has a basis, policy_source verbatim, overwrite clauses found, baseline sentences in their rules.
- **What changed:** only P1 `homeloan_ext_late_charge_reopened_month` (rule, compute `courtesy_12`, `error_12`, `farm_late_12` and `counted`, and `factors[0]`, now `cross_difficulty: farmland`). P2–P6 key sentences and compute bindings were spot-checked against round 3 and are unchanged. No prerequisite edge changed.

### Claimed closures

- **R3-N1 (mislabelled method): closed.** The three tiers of `repeat_count_basis` now compute different expressions, not one count with a different window:
  - tier 1: `lates_12 − error_12 − courtesy_12`;
  - tier 2: `lates_12 − error_12 + farm_late_12`;
  - fall-through: `lates_12 − error_12`.

  Tier 2 adds another product's ledger. The `method` label is honest.
- **R3-N2: closed.**
  - `error_12` now filters `fee_code='late_charge'`.
  - The rule now says "less the late charge waivers recorded on the home loan in those twelve months as error corrections", which is what the compute counts: waivers by their own date in the window.

### New item this round

- **R4-N1 (SOURCE-FACTOR RED, unreal ladder: two tiers are one; the same test as N-1 in round 2).**
  - Tier 1 ("a late charge … waived as a courtesy in those twelve months → … less the late charge waivers recorded in them as error corrections and as courtesies") and the fall-through ("the home loan late charges less those error corrections count on their own") give the same count on the whole fall-through domain.
  - The fall-through is taken only when `courtesy_12 = 0`. Tier 1's own method then subtracts zero courtesy waivers: `lates_12 − error_12 − 0 = lates_12 − error_12`.
  - "Subtract the courtesy-waived charges when there are any" is one method written as two tiers, exactly as round 2's "subtract the error-corrected charges when there are any" was (N-1).
  - What remains genuinely distinct is the subtract-waivers method and the add-the-farm-record method (tier 2). That is two tiers, below the minimum of three.
  - P1 has no other method factor, so counting only factors that pass, P1 has **0** methods.
  - Bears on task 0.
- **Observation R4-O1.**
  - Tier 2's rule text adds "the late charges assessed on that farm loan", meaning the active one.
  - The compute `XCOUNT('farmland', …, fee_code='late_charge')` counts late charges on every farm loan the member holds, active or not.
  - It diverges only for a member who has a non-active farm loan with late charges in the 12 months. Untriggered: task 0 has one active farm loan with no late charges.

### Factor counts (honest labels)

| policy | parameter | method |
| --- | --- | --- |
| P1 | 3 | **0** (R4-N1) |
| P2 | 3 | 1 |
| P3 | 3 | 1 |
| P4 | 2 | 3 |
| P5 | 2 | 3 |
| P6 | 5 | 1 |

All other structural conclusions of revision_3 stand.

### closing_checklist (revision_4)

Written after the round-4 reveals (13:08Z). The revision_4 charter section above was frozen first (`_difficulty.md` sha256=986dea98… at 13:07:38Z).

- Task 0: policy PASS · chain PASS · **SOURCE-FACTOR RED** (R4-T0-F1 / R4-N1) · unique solution PASS.
- Task 1: PASS on all four.
- Round-3 REDs: R3-N1 and R3-N2 are **closed**.
- New: **R4-N1**, SOURCE-FACTOR RED, introduced by the R3-N1 rework.
- Observations: R4-O1 (untriggered); R4-T1-O1 (`tasks/1.json` bytes changed despite the "untouched" claim; no verifiable content change).
- Scope, coverage, trees, graph, factor weight and baselines are unchanged and met. Gates are cited, not re-run.
- **Status: the difficulty does not yet pass.** One open RED remains.
  - P1 `repeat_count_basis` again has a tier whose method coincides with the fall-through wherever the fall-through applies. This is the third consecutive round with a RED on this one factor: N-1 in round 2, R3-N1 in round 3, R4-N1 now.
  - The test it keeps failing, stated as evidence and not as a fix:
    - each tier must select a counting rule that gives a different count from the fall-through's rule on worlds where the fall-through is the tier taken (R4-N1, N-1);
    - and the tiers must not differ only in a number such as a window start (R3-N1).

---

## revision_5

### charter_global_frozen (revision_5)

- Frozen 2026-10-11T13:32Z, before either round-5 task file was opened.
- Inputs:
  - `homeloan.extended.yaml` sha256=d0157f563ac23a65dada3767514e67992f3f70611fb513708aeda68b7d17ed8b, **changed**;
  - `task_tools.py` unchanged;
  - blueprint unchanged; base copy lines 1–1455 still verbatim.
- Mechanical sweep, clean: compute_basis verbatim, every binding has a basis, policy_source verbatim, every superseded clause found, every `replaced_by` in its rule, baseline sentences in their rules.
- **What changed:** only P1 `homeloan_ext_late_charge_reopened_month`. P2–P6 key sentences, compute binding counts and params were spot-checked against round 4 and are unchanged. No prerequisite edge changed.

### P1, re-derived

- **`repeat_count_basis` is removed.** The count is now a single, ladder-free input: `counted = lates_12 − waived_12`, with every late-charge waiver (courtesy or error correction) in the 12 months taken off. The rule states this in one sentence. It is now a binding of `late_rate`, not a factor.
- **New method factor `charge_measure`** (gross charge by the note the loan was closed on):
  - opened on or after 2021-01-01 → P&I on the record × rate;
  - opened 2016-01-01 to 2020-12-31 → (P&I + monthly escrow deposit on the record) × rate;
  - opened before 2016 → flat $25 whatever the rate.
- Verdict on `charge_measure`:
  - The three tiers are three different algorithms. Two of them use a different base (with or without escrow) and one ignores the rate entirely. The `method` label is honest.
  - On the fall-through's domain (pre-2016 notes) neither tier 1 nor tier 2 gives $25, so the N-1 / R4-N1 test passes.
  - The conditions (date of the note) and outcomes (escrow included on an older own-note form; a flat charge on an old form) are treatments a lender with note vintages actually carries.
  - The tiers are disjoint by opened date (compute `DAYS(opened, 2021-01-01) <= 0` / `DAYS(opened, 2016-01-01) <= 0`).
  - The fall-through equals the baseline `F('monthly_pi_amount') * rate / 100`? **No.** The baseline is tier 1 (P&I × rate), and the ladder's fall-through is the flat $25. That would make the baseline not equal the fall-through tier, which is the requirement "every factor's fall-through tier is that baseline". **See R5-N1 below.**
- **New override, declared:** base "No late charge is assessed on the escrow part, on a forborne month, or while the loan is in nonaccrual status" is superseded by "… and the escrow deposit enters the measure of a late charge only where the loan's note measures the charge on the whole monthly installment". The superseded clause is named, and the merged semantics are unique (base's "never deducted from a later regular payment" tail is still inherited).
- **Param change:** `relief_full_pct` 70 → 80. Consistent with the rule text, which only names the param.
- Counts: P1 has 3 parameters (late_rate, relationship_relief, charge_floor) and 1 method (charge_measure). cross_difficulty farmland (relief). Multi-source: relief, floor.

### Claimed closures

- **R4-N1: closed.** The factor was removed.
- **R4-O1: moot.** `farm_late_12` is gone.
- **R4-T1-O1: explained, closed.** `skills/erl-task-instantiate/scripts/replay_tasks.py` lines 296–303 pop `db_closure` / `db_closure_matches_initial_state` and rewrite each task file (`open(tp, "w").write(json.dumps(rebuilt, …))`), so every replay run re-serializes `tasks/*.json`. That accounts for the hash change with no hand edit.

### New items this round

- **R5-N1 (to be confirmed per task, SOURCE-FACTOR: the baseline is not the fall-through).**
  - The skill requires "every factor's fall-through tier is that baseline".
  - `charge_measure`'s fall-through (pre-2016 note → flat $25) differs from its `baseline` (`F('monthly_pi_amount') * rate / 100`, which is tier 1, the uniform note).
  - Whether this is a defect in substance is judged as follows. The baseline is honest: it is exactly what `baseline.rule` states ("measured on the monthly principal-and-interest payment on the loan record … late_charge_pct of that payment"). What fails is only the formal requirement that the ladder's "otherwise" be the baseline's tier.
  - The ladder is ordered newest-to-oldest, with the baseline's tier stated first and the legacy flat charge as "otherwise".
  - I record this as **SOURCE-FACTOR RED (structural)**. The bound is explicit in the skill ("a factor's fall-through tier is not the baseline" is listed under the dishonest-baseline judgement). The consequence is that a reader of the ladder sees the flat $25 as the default treatment, while the computation document (the baseline) says P&I × rate.
  - Bears on task 0.
- **Observation R5-O1.**
  - `charge_measure` tier 2 measures "the whole monthly installment on the loan record", i.e. today's P&I and today's escrow deposit.
  - On a reopened month whose installment differed (task 0: October was 1142.68 + 601.82; the record now shows 1156.80 + 630.39) the charge is measured on the current installment, not the one that was late.
  - The rule says "on the loan record" without ambiguity, so there is one reading, and the base rule likewise names the record's `monthly_pi_amount`. This is an observation on realism only.

### closing_checklist (revision_5)

Written after the round-5 reveals (13:33Z). The revision_5 charter section above was frozen first (`_difficulty.md` sha256=7fee15c2… at 13:32:33Z).

- Task 0: policy PASS · chain PASS · **SOURCE-FACTOR RED** (R5-T0-F1 / R5-N1) · unique solution PASS.
- Task 1: PASS on all four.
- Round-4 items:
  - R4-N1: **closed** (factor removed).
  - R4-O1: moot.
  - R4-T1-O1: explained by the replay gate rewriting task files.
- New:
  - **R5-N1**, SOURCE-FACTOR RED: the new `charge_measure` ladder's fall-through (flat 25.00) is not its baseline (P&I × rate, tier 1). The method itself is honest, and its three tiers are distinct and realistic.
  - R5-O1 (observation).
- Seed re-figure verified: the 10.47 late charges are consistent with the round-5 P1.
- Scope, coverage, trees, graph, factor weight and baselines are met. Every baseline gives a definite non-gold number. Gates are cited, not re-run.
- **Status: the difficulty does not yet pass.** One open RED remains: R5-N1.

---

## revision_6

### charter_global_frozen (revision_6)

- Frozen 2026-10-11T13:38Z, before either round-6 task file was opened.
- Inputs:
  - `homeloan.extended.yaml` sha256=da3bffe3f7b51399e9a86561c4adf63cfced114164684a66a787efc19cc46da8, **changed**;
  - tools unchanged; blueprint unchanged; base copy still verbatim.
- Mechanical sweep, clean: compute_basis, policy_source, overwrite clauses and baseline sentences all verbatim, and every binding has a basis.
- What changed: P1 (the `charge_measure` ladder, rule sentence and compute order) and P2 (`returned_item_fee` ladder). P3–P6 have the same rule lengths, compute counts and params as round 5. No edge changed.

### Claimed closures

- **R5-N1: closed.**
  - P1 `charge_measure` now reads: tier 1 = pre-2016 note, flat 25.00; tier 2 = 2016–2020 installment note, (P&I + escrow) × rate; **otherwise** = 2021-and-later uniform note, P&I × rate.
  - The otherwise tier equals `baseline` `F('monthly_pi_amount') * rate / 100` and `baseline.rule`.
  - The rule sentence and the compute (`K('legacy_flat_charge_usd') if legacy_days > 0 else (… if note_age_days > 0 else F('monthly_pi_amount') * rate / 100)`) follow the same order. The tiers are still disjoint and distinct, and the method label is still honest.
- **P2 `returned_item_fee` (reworker-initiated): accepted.**
  - The ladder now has 4 tiers. The former separate "unauthorized → 0" tier is folded into "otherwise (no other return counted, or a return reason of unauthorized)", valued `0 if ret_reason == 'unauthorized' else P('returned_payment_fee_usd')`, which is exactly its `baseline` and `baseline.rule`.
  - Three tiers beyond the fall-through give distinct values (45 / 40 / 35).
  - Rule and compute are unchanged.
- **Sweep of every factor of the charter (28 factors): each fall-through tier equals its `baseline` binding.** I checked them one by one: P1 ×4, P2 ×4, P3 ×4, P4 ×5, P5 ×5, P6 ×6.
- **R5-O1** stays an observation, as the reworker states.

### New items this round

None found. Factor counts are unchanged from revision_5 (P1 3 parameter / 1 method; P2–P6 as before).

### closing_checklist (revision_6)

Written after the round-6 reveals (13:38Z). The revision_6 charter section above was frozen first (`_difficulty.md` sha256=4cb7ff85… at 13:38:14Z).

- **Audit files.** `0.md`, `1.md` and `_difficulty.md` carry revisions 1–6 in order. Older text is untouched. Every revision_6 comparison carries a **PASS** on all four relationships for both tasks.
- **Coverage and scope.**
  - Task 0 claims P1–P4: `assess_late_charge_eed44226`, `assess_returned_item_fee_25e49e31`, `apply_replacement_remittance_c604a214`, `pay_escrow_shortage_8ff65e44`.
  - Task 1 claims P5–P6: `make_principal_paydown_d2fdfc16`, `record_escrow_waiver_439c8464`.
  - The scopes are pairwise disjoint, together they cover all six extended policies, and each spans the whole tree. The task tools and GT are closed. The uuid8s are independent and frozen.
- **Problem trees.**
  - Task 0 has 3 prerequisite problems and 3 value_input edges (floor 2), with a user write (P4). Task 1 has 1 prerequisite and 1 value_input edge (floor 1), with a user write (P5).
  - No cycle; the difficulty-wide graph (P3→P1, P3→P2, P4→P3, P6→P5) is acyclic.
  - Every edge is unmet at the opening and bears weight. The parallel edges P1 and P2 commute.
  - All prerequisite sentences pass the four-point test. The single action-form edge has a justified `fallback_reason`.
- **Factors.**
  - Each computation has 4–6 factors with at least 2 `parameter` and at least 1 `method`, honest labels throughout:

    | policy | parameter | method |
    | --- | --- | --- |
    | P1 | 3 | 1 |
    | P2 | 3 | 1 |
    | P3 | 3 | 1 |
    | P4 | 2 | 3 |
    | P5 | 2 | 3 |
    | P6 | 5 | 1 |

  - Each task has multi-source factors and cross-difficulty factors on seeded rows: farmland and equity in both tasks.
  - Every ladder has at least three distinct, realistic tiers stated in its rule, and every fall-through equals its baseline.
  - Every factor bears weight on its world. The baselines alone give 57.84, 30.00, 1787.19, 825.56, 0 and 576.12, each definite and each different from gold.
- **Gates.** Not re-run by this auditor (Step 0). The coordinator's snapshot on this final form is cited: EXTENDED OK / TASK TOOL CONTRACT OK / REPLAY NOT OK on the BLUEPRINT-KNOWN `loan_id` FK lines only (gate artefact, confirmed) / SOLVABILITY OK / COMPUTE OK / GROUNDING OK / CACHE-DIFF INFO / SCOPE OK. Traceability is deferred.
- **Open observations (not grounds for rework).** F-15 (`replaced_by` texts that carry only part of the deviation from a named base clause); O-1 and O-2 (task 0); R5-O1; T1-O3; and the `relief_full_pct` tuning noted in revision_5.
- **Status: this difficulty passes the source-layer policy-task audit (revision_6).**

---

## revision_7

### charter_global_frozen (revision_7)

- Frozen 2026-10-11T13:59Z, before round-7 `tasks/0.json` was opened.
- Inputs:
  - `homeloan.extended.yaml` sha256=24d84fff272f3ec571bb754faf51a25fbf6dd9a882d76192e0dde09830b58076, changed;
  - tools unchanged; worlds unchanged (same view hashes as round 6).
- **The diff is exactly the rename.**
  - The new charter contains `returned_fee_by_count` exactly once.
  - Replacing that string back with `returned_item_fee` in the raw bytes reproduces sha256 `da3bffe3f7b51399e9a86561c4adf63cfced114164684a66a787efc19cc46da8`, the round-6 charter hash, byte for byte.
  - So no rule text, ladder, compute, param, baseline, prerequisite or overwrite changed. Every revision_6 charter-global conclusion carries forward unchanged, on that hash identity.
- **Collision check.** No factor id in any of the six policies is now a substring of any of the six task-tool names (checked mechanically). The new id `returned_fee_by_count` is also distinct from the compute binding `item_fee`.
- **New defects:** none.

### closing_checklist (revision_7)

- Round 6 had no REDs.
- The round-7 change is verified to be exactly the factor-id rename, in both `homeloan.extended.yaml` and `tasks/0.json`: reverse-rename reproduces the round-6 hashes byte for byte. `tasks/1.json` is byte-identical to round 6.
- No factor id collides with a task-tool name any more.
- No regression and no new defect. Every item of the revision_6 closing checklist carries forward on these hash identities.
- Gates: cited from the coordinator's round-7 snapshot, not re-run.
- **Status: this difficulty passes the source-layer policy-task audit (revision_7).** Task 0 PASS ×4; task 1 PASS ×4.
