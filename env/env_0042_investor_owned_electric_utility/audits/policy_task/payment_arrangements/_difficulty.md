# Policy-task audit — payment_arrangements / charter-global

## charter_global_frozen

- Freeze time: 2026-10-07T21:29:00Z (file mtime; written before any task's GT was revealed; contains nothing derived from a revealed GT).
- Auditor: independent policy-task auditor (erl-task-policy-audit), revision_1.
- Frozen inputs (sha256, matching MANIFEST.txt):
  - `tasks/payment_arrangements/arrangement.extended.yaml` 5a3b48e0ce382027266294bc47fef2a725eaec9277f43395118819acbb68ec43
  - `tasks/payment_arrangements/task_tools.py` 6582fcc4dd84a8fb19b9bb25239daa12af85e1dcb96727ef5a43235ca5c33fd1
- Also read: `blueprint/blueprint.yaml`, `blueprint/db_schema.json`, `blueprint/share_tools.py`, `blueprint/products/arrangement.yaml` (the base section of the extended charter is byte-identical to it: `diff` of lines 1-1204 against the product file shows only the trailing blank line).
- Fields permitted: the charter, the tool module, the schema/share tools. Masked (not opened): `tasks/payment_arrangements/tasks/*.json` and every GT field in them. The DSL interpreter (gate scripts under `skills/`) was not read; compute expressions are judged against the rule prose.
- Entry conditions (Step 0): the coordinator supplied the gate snapshot (check_extended EXTENDED OK; check_task_tools TASK TOOL CONTRACT OK; replay_tasks REPLAY OK; check_solvability SOLVABILITY OK; check_compute COMPUTE OK, history_rows_max=25, branches_max=85; check_grounding GROUNDING OK; check_cache_diff INFO; check_cross_fire SCOPE OK; check_traceability deferred because the KB is unpublished) and the masked views with hashes. Hashes re-computed by this auditor match MANIFEST.txt. Entry conditions met.

### policy_conflict_scan

Extended policies (6) and their claims:

| policy | subject | target_tool (owner) | computes | prerequisite |
| --- | --- | --- | --- | --- |
| arrangement_ext_reinstatement_redeferral | arrangement_reinstatement | reinstate_arrangement_7e9638f2 (agent) | redeferred_amount | [] |
| arrangement_ext_renegotiated_installment | arrangement_renegotiation | renegotiate_arrangement_installments_743d0532 (user) | installment_amount | -> redeferral (value_input, unbilled_balance) |
| arrangement_ext_program_bill_shortfall | arrangement_missed_installment | record_missed_program_bill_7606bb4e (agent) | amount | [] |
| arrangement_ext_catch_up_forgiveness | arrangement_forgiveness | post_arrangement_forgiveness_78b684e3 (agent) | amount | -> shortfall (value_input, lateness_cut) |
| arrangement_ext_winter_plan_reinstatement | arrangement_reinstatement | reinstate_winter_protection_plan_6f5d50f4 (agent) | redeferred_amount | [] |
| arrangement_ext_extension_amount | arrangement_enrollment | accept_payment_extension_fc63ed0e (user) | extended_amount | -> catch-up (value_input, forgiven_half_year); -> winter (value_input, default_share) |

- Overlapping subjects: two policies govern `arrangement_reinstatement`. They are separated by object: redeferral is scoped "A defaulted Standard Deferred Payment Agreement or Extended Deferred Payment Agreement"; winter by "A defaulted Winter Protection Plan". The variants are disjoint, and so are the tool docstrings ("deferred payment agreement (Standard or Extended)" against "Winter Protection Plan"). No overlap.
- Triggers / eligibility / time anchors: every extended rule says it keeps the base window, count and lockout gates ("the reinstatement window, the number of reinstatements allowed and the requirement that the request fall inside the window are unchanged"; "the base rules on cure periods, counting misses and default are unchanged"; "the base rules on posting each installment once and on the customer cap are unchanged"; "the base eligibility, one-open-plan, lockout and single-installment rules are unchanged").
- One real conflict found on a time anchor, the posting day of a catch-up forgiveness. See finding F1 below.
- One real conflict found on the amount booked at reinstatement (base activation rule against both reinstatement extensions). See finding F2.
- Cross-category reads: service (difficulty service_billing_and_collections), deposit (difficulty security_deposits), plus medical and budget, which are categories that no difficulty of this scenario claims (blueprint `difficulties[*].claim.categories` = service, arrangement, deposit, meter, nem).
- Scope of the claim: the blueprint claims event_types [arrangement_enrollment, arrangement_reinstatement, arrangement_renegotiation, arrangement_account_transfer, arrangement_arrears_deferral]. The extended charter also writes `arrangement_missed_installment` (shortfall) and `arrangement_forgiveness` (catch-up), which are in category `arrangement` but missing from that event_types list. This is an observation (O1): no other difficulty claims them, and check_cross_fire reports SCOPE OK.
- Task scopes: task 0 = {renegotiated_installment (root), reinstatement_redeferral}; task 1 = {extension_amount (root), catch_up_forgiveness, program_bill_shortfall, winter_plan_reinstatement}. These are disjoint and together cover all 6 extended policies. (They are derived from the prerequisite graph and the masked views; the `charter_scope` fields are compared after the reveal.)

### rule_compute_equivalence

Check 2, run over every extended policy, both directions:

- redeferral: every binding has a verbatim `compute_basis` sentence in the rule. Every ladder (missed share 3+/2/<2, review window 6/9/12, nsf 2+/1/0, late 6+/3-5/<3, hardship both/one/neither, assistance 2+/1/0) is stated in the rule and implemented branch for branch. MX(0, ·) is "a combined share below zero counts as zero"; RND(·,2) is "rounded half-up to the cent". PASS.
- renegotiated_installment: the ceiling is the sum of 5 terms and is stated; `installments_used` is 3-tier and stated; `result` uses floor-to-cent ("rounded down to the cent"). PASS for equivalence. The schedule this produces is incoherent; see F5.
- program_bill_shortfall: obligation 3-tier, re-base window 3-tier, agency credit 3-tier and payment credit 3-tier are all stated. "the agreement's balance at booking" maps to `service_accounts.account_balance`; "earlier" agency payment = count in window less count on booking day. PASS.
- catch_up_forgiveness: all five ladders and the clamp "held between zero and one" (MN(1, MX(0, ·))) are stated. `forgiveness_room` sums forgiveness rows with no stated scope. The rule says "the forgiveness already posted", while the base cap (`arrangement_agg_forgiveness_cap`) is per customer across all agreements. That is observation O2; it has no consequence where the customer has one Arrearage Management Program plan.
- winter_plan_reinstatement: PASS.
- extension_amount: compute invents a 240-month bound (`ledger_months: 240`, `within_months=K('ledger_months')` on bills, charges and credits) that no rule sentence states. The rule and the baseline read "its bills whose due date falls on or before the enrollment date plus its posted charges, less its payments and credits", with no bound. This is observation O3: a basis invented by compute, with consequence only on an agreement holding rows older than 20 years. Every other binding has its sentence. PASS otherwise.

### action_binding_and_uuids

- `(target_tool, computes)` pairs are all distinct: 6 tools for 6 policies, and none is claimed twice.
- Docstrings: none names another tool, none states a sequence position, and none uses before/after/first as an ordering of actions ("1 = first" is an ordinal of installment numbers). "today" fixes the record date, not an order. No confirmation, review or wait outside the policy is added. `accept_payment_extension_fc63ed0e` creates the plan in `pending_down_payment` with `down_payment_due_date=today` even when the part due now is 0.00. That departs from base activation ("A plan with no down payment (zero or waived) is activated on its enrollment date"), but it is a tool effect on an unscored field: observation O4. The tool has no parameter for the customer-chosen extended due date that the base terms rule requires ("the extended due date, which is chosen by the customer and lies no more than extension_max_days calendar days after the enrollment date"): observation O5.
- Tool effects judge no prerequisite. Every body is an unconditional `ctx.update`/`ctx.create`. There is no status check, no window check and no error path (read: task_tools.py lines for all six functions).
- uuid8s: 7e9638f2, 743d0532, fc63ed0e, 78b684e3, 7606bb4e, 6f5d50f4. No shared prefix or suffix, no sequence and no adjacency, and none appears twice. PASS.
- Neither reinstatement tool books an `arrangement_arrears_deferral` row with `deferral_kind reinstatement`, although the base events (`arrangement_reinstatement` triggers `arrangement_arrears_deferral`) and `arrangement_msr_reinstatements` rely on one. After a reinstatement made through these tools, the reinstatement count measure still reads 0. This is observation O6 (unscored in both tasks).

### prerequisite_graph

Check 7:

- Every extended policy carries `prerequisite` (`[]` for redeferral, shortfall and winter).
- Edges: renegotiation->redeferral; catch-up->shortfall; extension->catch-up; extension->winter. Every `problem` is an extended policy id of this file, none points at itself, and none points at a base policy. The graph is acyclic (longest path extension->catch-up->shortfall).
- `policy_source` is found verbatim in the blocked rule for all 4 edges. Renegotiation rule: "Where the plan has defaulted, its new regular installment is worked out only after ...". Catch-up rule: "A catch-up forgiveness is not posted until ...". Extension rule: "The amount carried by a payment extension is fixed only after ..." and "... is not worked out until ...".
- `form: state` on all 4 edges, and no `fallback_reason`. Consistent.
- `resolved_by` equals the depended-on policy's `target_tool` on all 4 edges. Each `gate` is a binding of the blocked compute (`unbilled_balance`, `lateness_cut`, `forgiven_half_year`, `default_share`), and kind `value_input` matches.
- Wording of `condition` against `policy_source`: the renegotiation sentence says "with the balance returned at its default booked back under it as its remaining balance", while the condition says "a remaining_balance equal to the reinstatement re-deferral". The re-deferral is by rule a fraction of the returned balance ("rather than the whole returned balance"). The sentence is looser than the condition, but the reinstatement rule settles which balance is booked, so this is observation O7.
- Authoring-viewpoint text in the general `prerequisite` fields (observation O8). Several `effect` strings assert one world's outcome. Extension->winter: "default_share moves from the default_share_high tier ... to the default_share tier carried by the recent balance-return entry alone". Catch-up->shortfall: "lateness_cut moves from zero ... to the tier for a bill paid in full within catch_up_days days of the entry". Extension->catch-up: "adds a forgiveness entry dated the enrollment day". The last of these also contradicts the catch-up rule's own posting day (F1).

### prerequisite_sentences

Check 6, four-point test per edge:

| edge | connective | waited-on state (record-visible) | tool/id/snake_case? | strength vs condition | single write that brings it about |
| --- | --- | --- | --- | --- | --- |
| renegotiation -> redeferral | "only after" | plan "stands in active status again with the balance returned at its default booked back under it as its remaining balance" (`arrangement_plans.status`, `remaining_balance`) | none | slightly looser (O7) | redeferral reinstatement. The winter reinstatement cannot reach a renegotiable plan, because Winter Protection Plan has `renegotiation_allowed_count: 0` |
| catch-up -> shortfall | "not posted until" | plan "carries a missed-installment entry for the program bill" (`arrangement_ledger.event_type`) | none | equal | shortfall (`record_missed_program_bill_7606bb4e` is the only writer of missed entries) |
| extension -> catch-up | "fixed only after" | "every program bill ... paid in full carries the forgiveness entry owed for it" (`arrangement_ledger` forgiveness rows) | none | equal, but "owed" is timing-dependent (F1) | catch-up (only writer of forgiveness rows) |
| extension -> winter | "not worked out until" | "every Winter Protection Plan ... that defaulted and has had its missed installments and good-faith payment paid inside its reinstatement window stands active again" (`arrangement_plans.status`) | none | equal | winter reinstatement. The redeferral tool's docstring and rule exclude Winter plans |

- Derivations. Renegotiation: reading the sentence and the plan row (defaulted, remaining 0.00) leads to the redeferral rule, which says "On reinstatement the plan returns to active ... the balance booked back under the plan is the reinstatement re-deferral", and from there to reinstate_arrangement. Catch-up: the sentence plus a ledger with no missed row for the bill leads to the shortfall rule ("is booked as a missed-installment entry ... on the day after the cure period ends"), and from there to record_missed_program_bill. Extension: the first sentence plus a paid program bill with no forgiveness row leads to the catch-up rule and post_arrangement_forgiveness. The second sentence plus a defaulted Winter plan leads to the winter rule and reinstate_winter_protection_plan. Each has a single reading, except for the timing of "owed" in task 1 (F1).
- No rule carries a second wording, tool name or policy id. No depended-on rule restates the sentence.
- Cross-problem orders in base rules that ground no edge (observation O9): `arrangement_agg_multi_holding` says "A defaulted plan that is still inside its reinstatement window therefore blocks a new plan on that agreement until the window ends or the plan is reinstated". `arrangement_agg_forgiveness_cap` says "may be placed in a separate repayment plan only after the program plan ends". Neither grounds any task's tree. In task 1 the Payment Extension is on a different agreement from the defaulted Winter plan, so the one-open-plan block does not apply.

### override_declarations

Check 1, sentence by sentence against each `base_policy_refs` entry, plus base sentences elsewhere in the charter that govern the same scored quantity:

- redeferral against `arrangement_reinstatement_rule`. Count gate, window, counting and "cannot be reinstated stays defaulted" are followed. The "Before reinstatement ... paid" sentence is replaced and declared. The "On reinstatement ... returned balance is deferred into the plan again" sentence is replaced and declared.
- redeferral against `arrangement_default_and_cure` ("not removed from the count, except through reinstatement"): followed.
- Undeclared: `arrangement_activation_rule` (not in `base_policy_refs`, not in `overwrite`) says "On activation, and again on reinstatement, the deferred amount (or on reinstatement the remaining unbilled plan balance) is booked into the plan and credited off the service agreement's collectible balance". On reinstatement this books the whole remaining unbilled balance, which equals the returned balance, while the extension books "the reinstatement re-deferral rather than the whole returned balance". This is **F2**.
- winter against `arrangement_reinstatement_rule`: same as redeferral, both replacements declared. Same undeclared conflict with `arrangement_activation_rule` (**F2**).
- renegotiation against `arrangement_renegotiation_rule`. The ceiling and divisor sentence is replaced and declared; "new count is chosen by the customer" is replaced and declared. The count gate and the active/no-missed gate are followed. "Renegotiation never changes the deferred amount or re-ages any missed installment" is followed in the deferred amount. The `installments_used` tiers stop counting missed installments as used (see F5), but whether that is "re-aging" has no settled reading, so it is not recorded as a conflict here.
- shortfall against `arrangement_default_and_cure`. The "installment is paid when ... less a shortfall of no more than installment_tolerance_usd" sentence is replaced and declared. Cure period, the current-bill sentence and default are followed. The base event glossary (`arrangement_missed_installment.amount`: "Unpaid amount of the installment or current bill") is not a policy sentence, and the extension resets that amount. This is observation O10, with the second value being the baseline value.
- catch-up against `arrangement_amp_forgiveness`. The "The forgiveness is forgiveness_share_per_installment ... posted under forgiveness_posting_rule" sentence is replaced and declared.
- **Undeclared**: the base sentence "where forgiveness_catch_up_allowed is true, withheld forgiveness is posted once that bill is paid in full, as long as the plan is still active and no default has occurred" stays in force. The extended rule sets a different day: "the catch-up forgiveness is posted on the day after the bill is paid in full". This is **F1**. The cap sentence is followed ("never more than the customer's remaining forgiveness room").
- extension against `arrangement_terms_calculation`. The eligible-balance sentence and the down-payment sentence are replaced and declared. The deferred-amount, single-installment and extended-due-date sentences are followed. The income-waiver sentence does not bite, because the Payment Extension has `down_payment_waived_income_qualified: false`.
- extension against `arrangement_enrollment_eligibility`. "The eligible balance, under the plan's eligible_balance_basis, must lie between min_past_due_usd and max_past_due_usd" still reads the base basis (past_due_balance), while the balance placed under the plan is now the extension base. The gate and the placed amount can therefore read two different balances. This is observation O11, with consequence only when one side crosses 25.00/1500.00.
- extension against `arrangement_agg_multi_holding`, `arrangement_agg_forgiveness_cap` and `arrangement_program_interactions`: followed.

### factor_ladders

Structure only. Whether each factor bears weight is decided in each task's `factor_weight`.

| policy | factor | label | tiers | multi-source | cross_difficulty (declared) | structural verdict |
| --- | --- | --- | --- | --- | --- | --- |
| redeferral | missed_installment_share | parameter | 3+ / ==2 / <2 | no | null | **fall-through unreachable** (F3) |
| redeferral | restoration_review_window | method | 6 / 9 / 12 months | yes (start_date x returned-payment charges) | service | **mislabelled: number, not method** (F4) |
| redeferral | returned_payment_share | parameter | 2+ / 1 / 0 | no | service | ok |
| redeferral | late_charge_share | parameter | 6+ / 3-5 / <3 | no | service | ok |
| redeferral | hardship_relief | parameter | both / one / neither | yes (medical x budget) | medical (no difficulty claims it; O12) | ok |
| redeferral | assistance_relief | parameter | 2+ / 1 / 0 | no | service | ok |
| renegotiation | winter_stretch | parameter | med / std / 0 | yes (space_heating x bill season x medical) | service | ok |
| renegotiation | tenure_months | parameter | 180+ / 120-179 / less | no | service | ok |
| renegotiation | deposit_months | parameter | >=300 / >0 / none | no | deposit | ok |
| renegotiation | history_cut | parameter | nsf / >=3 late / 0 | yes (returned-payment x late charges) | service | ok |
| renegotiation | default_cut | parameter | 6m / 12m / none | no | null | ok |
| renegotiation | installments_used | method | billed-missed / billed-min(missed,1) / billed | yes (agency x autopay x ledger) | service | genuine method, but **its non-fallthrough tiers give a schedule that the charter's own numbering cannot carry** (F5) |
| shortfall | program_obligation | method | budget installment / average of actual bills / current charges | yes | service | ok (genuine method) |
| shortfall | rebase_window | method | 12 / 3 / 6 months | yes (space_heating x enrolled date) | service | mislabelled (F4); the policy still has 1 honest method |
| shortfall | agency_credit_share | parameter | 1.0 / 0.5 / 0 | yes (agency payment x missed entries) | service | **partial-credit tier unreal** (F6) |
| shortfall | payment_credit_share | parameter | cash 1.0 / card-online 0.5 / 0 | no | service | **card-online half-credit tier unreal** (F6) |
| catch-up | lateness_cut | parameter | >30d / <=30d / no missed entry | yes (ledger x payment date) | null | ok |
| catch-up | catch_up_review_window | method | 6 / 9 / 12 months | yes | service | **mislabelled** (F4); the policy has 0 honest methods |
| catch-up | late_charge_cut | parameter | 3+ / 1-2 / 0 | no | service | ok |
| catch-up | progress_credit | parameter | >=0.9n / >=0.5n / less | no | null | ok |
| catch-up | autopay_credit | parameter | 5+ / 1-4 / 0 | no | service | ok |
| winter | winter_missed_share | parameter | 3+ / ==2 / <2 | no | null | **fall-through unreachable** (F3) |
| winter | winter_review_window | method | 6 / 9 / 12 months | yes | service | **mislabelled** (F4); the policy has 0 honest methods |
| winter | winter_returned_share | parameter | 2+ / 1 / 0 | no | service | ok |
| winter | deposit_relief_share | parameter | >=200 / >0 / none | no | deposit | ok |
| extension | extension_base | method | whole balance / written-notice amount / past-due balance | yes (final vs written notices) | service | ok (genuine method) |
| extension | default_share | parameter | 0.30 / 0.15 / 0 | yes (winter status x missed entries x default entries) | null | ok. Restricting the high tier to Winter plans is odd but not shown to be unreal (O13) |
| extension | forgiveness_relief | parameter | 6+ / 4-5 / <4 | no | null | ok |
| extension | returned_payment_share | parameter | 2+ / 1 / 0 | no | service | ok |
| extension | tenure_relief | parameter | 180+ / 60-179 / less | no | service | ok |
| extension | assistance_relief | parameter | 2+ / 1 / 0 | no | service | ok |

- Every ladder is stated in full in its `rule`, with condition and value or method for every tier, and is implemented in `compute`. No tier lives only in compute. Every fall-through equals the policy's `baseline` (zero shares, standard windows, standard obligation, standard base, billed installments counted as used).
- Each baseline is self-sufficient: every `baseline.rule` sentence is in the `rule`, and `baseline.params` names the default keys. Exception: extension `params: [ledger_months]` names the 240-month bound that the rule never states (O3).
- Counts after the tests: redeferral 6 declared, 1 struck (F3), 0 honest method (F4) → **fails the method floor**. Renegotiation 6 / 5 parameter / 1 method → passes count. Shortfall 4 / 1 honest method (+1 mislabelled) → passes count. Catch-up 5 / 0 honest method → **fails**. Winter 4 declared, 1 struck (F3) → 3 factors, 0 honest method → **fails** count and method. Extension 6 / 5 parameter / 1 method → passes.

### findings

- **F1: SOURCE-POLICY RED (catch-up posting day: base "once paid" against extended "day after paid"). Bears on task 1.**
  - Symptom: two charter sentences fix different posting days for the same catch-up forgiveness.
  - Root cause: the overwrite on `arrangement_amp_forgiveness` names only "The forgiveness is forgiveness_share_per_installment of the scheduled installment and is posted under forgiveness_posting_rule". The base sentence "withheld forgiveness is posted once that bill is paid in full" is left in force, while the extended rule says "the catch-up forgiveness is posted on the day after the bill is paid in full".
  - Evidence: arrangement.extended.yaml lines 1049-1051 (base) and 1957-1959 (extended).
  - Consequence: where the bill is paid in full on the handling day, one sentence posts the forgiveness today and the other posts it tomorrow. The `prerequisite[0].effect` of the extension ("adds a forgiveness entry dated the enrollment day") takes the base reading, against the extended rule's own text. The consequence is demonstrated in task 1's file.
- **F2: SOURCE-POLICY RED (undeclared override of `arrangement_activation_rule` on the amount booked at reinstatement). Bears on task 0 (redeferral) and task 1 (winter).**
  - Base sentence: "On activation, and again on reinstatement, the deferred amount (or on reinstatement the remaining unbilled plan balance) is booked into the plan".
  - Both reinstatement extensions book a reduced re-deferral. Neither lists `arrangement_activation_rule` in `base_policy_refs` or `overwrite`.
  - Consequence: the remaining unbilled plan balance is the returned balance, so a second defensible reinstatement amount exists. Demonstrated per task.
- **F3: SOURCE-FACTOR RED (unreal ladder: unreachable fall-through) for `missed_installment_share` (redeferral) and `winter_missed_share` (winter).**
  - Both ladders pay zero when the plan "carries fewer than two" missed-installment entries.
  - Standard and Extended DPAs and the Winter Protection Plan all carry `missed_installments_to_default: 2`, and a plan reaches `defaulted` only when "arrangement_msr_open_missed reaches missed_installments_to_default" (`arrangement_default_and_cure`). Every plan these writes reach (scope: "A defaulted Standard Deferred Payment Agreement or Extended Deferred Payment Agreement"; "A defaulted Winter Protection Plan") therefore carries at least two entries.
  - So "two or more missed entries" holds of every customer who reaches the write. The fall-through tier, and with it the factor's baseline value 0, is a treatment no customer in that situation can receive, and the ladder has two live tiers.
  - Demonstrated on task 0 (redeferral) and task 1 (winter).
- **F4: SOURCE-FACTOR RED (mislabelled effect) for `restoration_review_window`, `catch_up_review_window`, `winter_review_window`, and also `rebase_window`.**
  - Each is labelled `method`, but its tiers bind one number (`K('window_clean_months')`/`K('window_nsf_months')`/`K('window_standard_months')` = 6/9/12, and so on) into the same `XCOUNT(..., within_months=<months>, ...)` expression. The algorithm is identical across tiers; only the lookback number changes. This is the "substitute a different number into the same formula" case.
  - Struck as methods, the redeferral, catch-up and winter policies each keep 0 `method` factors, below the floor of 1.
  - The shortfall keeps `program_obligation` as an honest method, so for it this is an observation.
  - Bears on task 0 (redeferral) and task 1 (catch-up, winter).
- **F5: SOURCE-FACTOR RED (unreal method tiers) for `installments_used` (renegotiation). Bears on task 0.**
  - The tiers "installments billed less every installment recorded as missed" and "less one" make "installments remaining" (= new total − used) larger than the installment numbers still unbilled (= new total − billed).
  - The base billing rule keeps "numbered from 1 in billing order and continuing after a reinstatement or renegotiation. Each installment number is billed once". The tool and schema keep "installment_count: Total number of installments, counting those already billed".
  - The regular installment is therefore sized for more payments than the plan has numbers left, and the final number carries the gap. Demonstrated with figures in task 0.
- **F6: SOURCE-FACTOR RED (unreal tier values) for `payment_credit_share` (card/online 0.5) and `agency_credit_share` (partial 0.5) in the shortfall. Bears on task 1.**
  - A payment the customer posted on the booking day is recognised at half its amount, depending on the channel (card or online bank transfer) or on a mixture of history conditions.
  - A regulated utility recognises a posted payment either at face value or not at all (the base rule's standard: "payments posted on the booking day come after the cure period"). No such business publishes "a card payment counts for half".
- Observations O1-O13 as cited above. None demonstrates a consequence on its own.

## closing_checklist

Written after both reveals (2026-10-07T21:31Z onward). It sits below the pre-reveal charter-global section, which was not edited after the reveal; only its freeze-time line was corrected to the file mtime.

| Step 4 item | status |
| --- | --- |
| per-task files 1:1 with tasks; `_difficulty.md` alongside; every comparison section carries a PASS | files `0.md` and `1.md` exist with frozen + comparison sections. **Not all PASS**: task 0 is SOURCE-POLICY RED and SOURCE-FACTOR RED; task 1 is SOURCE-POLICY, SOURCE-CHAIN, SOURCE-FACTOR and SOURCE-TASK RED |
| extended policies fully covered; scopes pairwise disjoint; task tools and GT closed; uuid8s independent | yes. task 0 = {redeferral, renegotiation}; task 1 = {shortfall, catch-up, winter, extension}. This equals each task's `charter_scope` and `required_documents`. 6 tools, 6 distinct uuid8s |
| every tree has 1-3 prerequisites, ≥ max(n−1,1) value_input, one owner=user write, no cycle; the difficulty-wide graph is acyclic | task 0: n=1, 1 value_input, user root. task 1: n=3, 3 value_input, user root. Difficulty graph acyclic. **Task 1 tree fails the no-wait test** (catch-up posts 2026-08-12 by its own rule) |
| every computation: self-sufficient baseline, 4-6 factors (2 parameter, 1 method), every ladder ≥ 3 real tiers, every factor weight-bearing against an honest baseline, fall-back ≠ gold | all factors bear weight numerically and every fall-back differs from gold (both tasks). **Fails**: redeferral, catch-up and winter have no honest method (F4); the missed-share ladders have unreachable fall-throughs (F3); `installments_used` (F5) and the shortfall credit shares (F6) are unreal tiers; the renegotiation computation has no genuine near-miss (task 0) |
| instantiation-stage gates re-run on the final form | not re-run by this auditor (an audit runs no gates). The coordinator's pre-audit snapshot is cited in `charter_global_frozen`. The artifacts are unchanged since: hashes re-verified against MANIFEST.txt at freeze time |

**Difficulty result: the source-layer audit does not pass.**

- Charter-global defects F1-F6 are listed under `### findings` above.
- Per-task consequences are demonstrated in `0.md` and `1.md`.
- Every scored figure of both tasks was reproduced independently: task 0 278.49 / 11 / 30.94; task 1 30.59 / 49.71 / 145.31 / 188.78 / 7.55 / 181.23. Every `factor_sensitivity` and `baseline_result` figure agrees with the auditor's.
- The defects lie in the charter (undeclared overrides, labels, ladder realism) and in the task 1 timing, not in the arithmetic.

---

## revision_2

### charter_global_frozen (revision_2)

- Written before any round-2 GT was opened. The round-1 text above is left untouched.
- Inputs re-hashed and matching the round-2 MANIFEST.txt:
  - `arrangement.extended.yaml` a7b58959717d292c344d6faa1e0790b2813e33aa812b0023e5f2010a45fcc0e9 (**changed**, so this section is re-derived in full)
  - `task_tools.py` 6582fcc4dd84a8fb19b9bb25239daa12af85e1dcb96727ef5a43235ca5c33fd1 (unchanged, so the round-1 `action_binding_and_uuids` section is carried forward by reference)
- The base section (lines 1-1204) is still byte-identical to `blueprint/products/arrangement.yaml`.
- Also read: `blueprint/products/service.yaml` for Schedule RS `late_payment_grace_days: 5`, which the new catch-up lateness anchor reads through `CPARAM`.
- **contamination_disclosure (revision_2):** the auditor read the round-1 GT of both tasks during round 1 (recorded above). This round's derivations are recomputed from the new charter and the new views. They are independent of round-2 GT, but not of round-1 GT.

### Round-1 RED closure check (charter-global)

| round-1 item | change in charter | verdict |
| --- | --- | --- |
| F1 catch-up posting day | Catch-up rule now reads "the withheld forgiveness is posted as a catch-up once that bill is paid in full, on the day it is paid in full ... the base rules on when catch-up is posted ... are unchanged". This agrees with base `arrangement_amp_forgiveness` "posted once that bill is paid in full". | **closed** |
| F2 activation-rule override | Both reinstatement policies add `arrangement_activation_rule` to `base_policy_refs` and `overwrite`. Each superseded clause is a verbatim prefix of base lines 833-835. Each replacement is scoped "For a reinstated deferred payment agreement" or "For a reinstated winter plan", and the same sentence is carried in both rules. | **closed** |
| F3 unreachable missed-share fall-through | Both ladders now count missed entries posted on the plan "within the miss_lookback_months (6) months before the request". A plan defaults on its 2nd open miss, but the first may lie more than 6 months back, so the "fewer than two" tier (exactly one) is reachable and is not a straw man. | **closed** |
| F4 window factors mislabelled | `restoration_review_window`, `winter_review_window` and `rebase_window` are relabelled `parameter`. The catch-up window factor is removed (fixed 6-month late-charge window). New `method` factors: `hardship_treatment` (redeferral: drop the missed share / halve / as is), `deposit_treatment` (winter: drop the returned-payment share / ×0.75 / as is) and `lateness_anchor` (catch-up: count days late from cure end / rate-schedule grace end / due date). The first two change the algorithm. `lateness_anchor` changes the reference event drawn from two different products' parameters; it is accepted as a method (observation R2-O1: its tiers act as an offset). | **closed** |
| F5 renegotiation schedule | The new total count is "the renegotiation ceiling plus the billed installments not counted as used", and the installments remaining are "the new total installment count less the installments already billed ... so every remaining installment has its own installment number". The divisor equals the unbilled numbers. | **closed** |
| F6 half-credit tiers | `card_credit` and `agency_credit_partial` are gone. Booking-day payments now count in full or not at all, decided by a "posting grace" in days (pay station 1, mailed check 2, agency 3/1/0), and "a card or online payment posted on the booking day ... never counts". | **closed as stated; it introduces R2-F1** |
| O2, O3, O7, O8, O11, O12 | Catch-up room is now "on the plan" with a stated reason. The 240-month bound is now in the extension rule and baseline. The renegotiation sentence now names "its reinstatement re-deferral". The `effect` texts are generalised. The extension eligibility override is declared. `hardship_treatment.cross_difficulty` is null. | closed |
| O1, O4, O5, O6, O9, O10, O13, O14 | unchanged artifacts (tool module, blueprint claim, base text) | remain observations |

### New charter-global findings (revision_2)

- **R2-F1: SOURCE-FACTOR RED (unreal ladder: one tier written as two) for `agency_grace` and `customer_posting_grace` (shortfall).**
  - The grace values are days (agency 3 / 1 / 0; customer 1 / 2 / 0), but the rule consumes them only as "a grace of at least one day covers the booking day and a grace of zero covers nothing after the cure period". The only payments ever tested are those "posted on the booking day", which is the first day after the last cure day.
  - Compute agrees: `booking_day_credit` tests only `agency_grace_days >= 1` and `customer_grace_days >= 1`, and the customer branch adds `pay_station_on_booking_day + mailed_check_on_booking_day` whichever of its two non-zero tiers fired.
  - Demonstration: swap `agency_grace_long_days` (3) with `agency_grace_short_days` (1), or `pay_station_grace_days` (1) with `mailed_check_grace_days` (2), and every world's missed amount is unchanged.
  - Each ladder therefore has two live outcomes (counts in full / does not count). Struck under the ladder test, the shortfall keeps 2 factors (`program_obligation` method, `rebase_window` parameter), below the floor of 4 factors and 2 `parameter`.
  - Bears on task 1.
- R2-O1: `lateness_anchor` is accepted as `method`. Its three anchors are distinct business events (the plan's cure end, the rate schedule's late-payment grace end, the due date), but numerically each tier subtracts a different offset from the same day count.
- R2-O2: the extension eligibility replacement reads "For a payment extension, the extension base must lie between ...". The extension base is defined only for extensions on notice-pending agreements ("extensions on other agreements follow the base terms"). The sentence is wider than the rule's scope, but there is no consequence on any task world.
- No new undeclared override found. Sentence sweep:
  - redeferral against reinstatement_rule, default_and_cure and activation_rule
  - winter against reinstatement_rule and activation_rule
  - renegotiation against renegotiation_rule
  - shortfall against default_and_cure (cure, counting and default unchanged)
  - catch-up against amp_forgiveness (posting now agrees) and agg_forgiveness_cap ("never more than the remaining forgiveness room")
  - extension against its five refs
- No rule/compute inequivalence found. Every new binding (`plan_missed_entries` window, `combined_*`, `restoration_share`, `winter_good_faith_share`, `new_total_count`, `lateness_days`, `agency_grace_days`, `customer_grace_days`, `booking_day_credit`) has its verbatim `compute_basis` sentence.
- Prerequisite graph and sentences: same 4 edges, still acyclic, still state form. The renegotiation `policy_source` was updated in the rule and the field identically.

### factor_ladders (revision_2 counts)

| policy | factors | parameter | honest method | multi-source | cross-difficulty | structural verdict |
| --- | --- | --- | --- | --- | --- | --- |
| redeferral | 6 | 5 | 1 (hardship_treatment) | window, hardship | service | pass |
| renegotiation | 6 | 5 | 1 (installments_used) | winter_stretch, history_cut, installments_used | service, deposit | pass |
| shortfall | 4 | 3 | 1 (program_obligation) | program_obligation, agency_grace | service | **fails after R2-F1 strikes 2** |
| catch-up | 5 | 4 | 1 (lateness_anchor) | lateness_anchor | service | pass |
| winter | 4 | 3 | 1 (deposit_treatment) | window | service, deposit | pass |
| extension | 6 | 5 | 1 (extension_base) | default_share | service | pass |

### closing_checklist (revision_2)

Written after the round-2 reveal.

- Per-task files carry revision_2 frozen and comparison sections. Old revisions are untouched. Comparisons: both tasks reproduce every GT figure exactly.
- Scopes are unchanged and disjoint, and cover all 6 policies. Tools and uuid8s are unchanged.
- Trees: task 0 n = 1 and task 1 n = 3, all value_input, user roots, acyclic, no waits. Both PASS.
- Factors:
  - redeferral, renegotiation, catch-up, winter and extension pass structure and weight.
  - **shortfall fails** (R2-F1: decorative day values; 2 surviving factors).
  - The task 0 renegotiation computation still lacks a load-bearing near-miss (0.md R2-#1).
- Gates: the coordinator's round-2 snapshot (all OK; check_traceability deferred) is cited, not re-run.
- **Difficulty result (revision_2): does not pass.** All round-1 SOURCE-POLICY, SOURCE-CHAIN and SOURCE-TASK REDs are closed. SOURCE-FACTOR REDs remain on both tasks: the task 0 near-miss (carried over) and the task 1 shortfall grace ladders (new).

---

## revision_3

### charter_global_frozen (revision_3)

- Written before any round-3 GT was opened. Revisions 1-2 above are untouched.
- Inputs re-hashed, matching the round-3 MANIFEST.txt:
  - `arrangement.extended.yaml` f7b0f4773a0643b7bd24fb50e31b98b89f13b72827c63608216402deb95a867c (**changed**)
  - `task_tools.py` 6582fcc4… (unchanged; the tool section is carried forward by reference)
- Base section still byte-identical to the product file.
- Scope of the charter change, located by the auditor:
  - Only `arrangement_ext_program_bill_shortfall` changed. It grew by 15 lines, and every later policy shifted by exactly +15 lines (catch-up 1942→1957, winter 2166→2181, extension 2359→2374; file 2647→2662).
  - The redeferral and renegotiation blocks keep their round-2 line ranges.
  - All six policies' `params`, factor ids, labels and `prerequisite` edges are identical to round 2 except the shortfall's.
  - The other five policies' charter-global conclusions in revision_2 are therefore carried forward. The shortfall is re-derived in full below.
- Also read: `blueprint/products/service.yaml`. Schedule RS has `returned_payment_restriction_count: 2` and `returned_payment_restriction_months: 12`, and the service base rule says check and bank-draft payments are refused after that count. This grounds the new customer-recognition tiers.
- contamination_disclosure: the auditor read the round-1 and round-2 GT of both tasks in earlier rounds.

### Shortfall re-derivation (revision_3)

- **Override.** The `arrangement_default_and_cure` tolerance sentence is replaced by "a payment posted on the booking day counts toward it only where this rule recognises it". Declared. Cure, counting and default are unchanged. No undeclared override.
- **Rule/compute equivalence.** Every binding has its verbatim `compute_basis`:
  - `customer_booking_credit` implements the 3-tier prose: pay-station + mailed check / pay-station only / 0, keyed on returned-payment charges within the rate schedule's `returned_payment_restriction_months` against `returned_payment_restriction_count`. Both values are read with `CPARAM` from the service product.
  - `agency_window_months` (12 / 6 / 0) and `agency_earlier` (count in window less the booking-day count) implement "an earlier payment ... within the agency pledge window before booking, the booking-day payment itself left out".
  - "A card, online or autopay payment ... is never recognised" matches compute, which sums only `authorized_pay_station_cash` and `mail_check`.
  - PASS.
- **Factor ladders:**
  - `program_obligation` (method): unchanged, PASS.
  - `rebase_window` (parameter): unchanged, PASS.
  - `customer_payment_recognition` (labelled parameter): its three tiers select three different payment sets. They are distinct whenever a booking-day mailed check exists, and they are grounded in the service base rule's returned-payment restriction. Its tiers change which records enter the sum, not a constant. A `method` label would fit at least as well (observation R3-O1). Either way the policy keeps ≥ 2 parameter and ≥ 1 method.
  - `agency_pledge_window` (parameter): 12 / 6 / 0 months. The tiers are distinct whenever the earlier agency payment lies 6-12 months back. Multi-source (missed entries × start date). PASS.
  - Count: 4 factors, 3 parameter + 1 method (or 2 + 2 under R3-O1). Multi-source: program_obligation and agency_pledge_window. Cross-difficulty: service. PASS.
- **R2-F1 (decorative day values): closed.** No ladder value is consumed only through a threshold any more. Every non-fall-through tier selects a different recognised amount or window.

### New findings (revision_3)

- None RED.
- R3-O1 (label of `customer_payment_recognition`) is an observation.
- R2-O1 and R2-O2 are unchanged observations.

### closing_checklist (revision_3)

Written after the round-3 reveal (2026-10-08T00:33:27Z).

- Per-task files carry revision_3 frozen and comparison sections. Revisions 1-2 are untouched. Both comparisons are PASS on every relationship, and every GT figure, factor sensitivity and baseline result is reproduced exactly.
- The 6 extended policies are covered by the 2 disjoint task scopes. Tools and uuid8s are unchanged and independent.
- Trees:
  - task 0: n = 1, 1 value_input
  - task 1: n = 3, 3 value_input
  - user-owned roots, acyclic difficulty graph, every edge unmet at the opening and weight-bearing, no real-world waits, tools judge nothing
- Every computation has a self-sufficient baseline and 4-6 factors with at least 2 parameter and 1 method. Every ladder has three real, distinct tiers stated in its rule. Every factor bears weight against an honest baseline, and every all-baseline fall-back differs from gold.
  - Each task has at least 1 multi-source and 1 cross-difficulty (service, deposit) factor with seeded rows.
  - Each computation has a load-bearing near-miss.
- Gates: the coordinator's round-3 snapshot (all OK; check_traceability deferred until the KB is published) is cited, not re-run by the auditor.
- Open observations (not grounds for rework): O1, O4, O5, O6, O9, O10, O13, O14, R2-O1, R2-O2, R3-O1.
- **Difficulty result (revision_3): PASS on all four relationships for both tasks.**

---

## revision_4

### charter_global_frozen (revision_4)

- Written before the round-4 task files were opened. Revisions 1-3 are untouched.
- Inputs:
  - `arrangement.extended.yaml` sha256 52a874ccb4103fed… (**changed**)
  - `task_tools.py` 6582fcc4… (unchanged)
  - both views byte-identical to round 3 (`cmp` against `round3/`)
- Base section still a byte-identical prefix of `blueprint/products/arrangement.yaml`.
- Read this round, per the brief: `audits/policy_kb/payment_arrangements/1.md` (D2, P7-P10). These are render-layer reports, not GT.

### What changed and whether it holds

- **P7 / D2 conflict (shortfall "customer payments" against compute summing every booking-day payment): closed.**
  - The rule, the baseline and `compute_basis` (`payments_on_booking_day`, `cure_end_balance`) now read "its balance at booking plus every payment posted to it on the booking day, an energy assistance agency's included".
  - This equals `payments_on_booking_day = XSUM(service_credits, amount, event_type='service_payment', posting_date=NOW)`. No channel filter in compute, none in prose.
  - The term "customer booking-day payments" is now used only for the recognised pay-station and mailed-check set. That use is unambiguous and also equals compute.
- **Catch-up paid-in-full date.** The rule now reads "the posting date of the latest payment posted to the agreement", which equals `paid_in_full_date = XLATEST(service_credits, posting_date, event_type='service_payment')`. Agreement closed.
- **P8, widened replacements.** Each `replaced_by` now restates the base clause for cases outside its policy's scope. Verified sentence by sentence:
  - every `superseded_clause` is still verbatim in its base policy
  - every `replaced_by` is verbatim in its own rule
  - every `compute_basis` and `baseline.rule` sentence is verbatim in the rule (scripted check)

| policy | restated outside-scope clause | conflict check |
| --- | --- | --- |
| redeferral / winter → activation_rule | Both: "On activation the deferred amount is booked into the plan and credited off the service agreement's collectible balance." Then each names its own reinstatement case (deferred payment agreement → reinstatement re-deferral; winter plan → winter re-deferral). | The two replacements of the same base clause carry the identical activation sentence and have disjoint reinstatement scopes. Every variant with `reinstatement_allowed_count > 0` (Standard DPA, Extended DPA, Winter) is covered. The base remainder "; a deferral is booked only on a plan in active status" is left in force. No conflict. |
| shortfall → default_and_cure | "Any other installment, and the current charges of any other bill carrying an installment, are paid when payments ... cover them, less a shortfall of no more than installment_tolerance_usd, by the end of their cure period." | Equals the base tolerance sentence plus the base "current charges ... treated the same way" sentence, which stays in force. Every variant has `current_bill_payment_required: true`, so the unconditioned restatement cannot diverge. Program bills are excluded by "other". No conflict. |
| catch-up → amp_forgiveness | "An installment forgiven because the current charges of its bill were paid in full by that bill's due date is forgiven at forgiveness_share_per_installment ... and posted under forgiveness_posting_rule." | Restores the on-time path exactly. The catch-up path is separate, and "each installment once" is untouched. No conflict. |
| extension → terms_calculation (×2), enrollment_eligibility | "For every plan other than a Payment Extension on a residential agreement whose status is disconnection notice pending", followed by the base eligible-balance, range and down-payment text verbatim. For the in-scope Payment Extension the range now applies to the extension base (closes R2-O2). | No conflict on the scoped sentences. Observation **R4-O1**: the opening sentence of the first replacement, "The balance placed under a payment extension is the extension base.", is unscoped. For a Payment Extension on an *active* agreement that still carries a delivered notice (e.g. a rescinded one), it would point at the notice amount while the scoped restatement points at the past-due balance. No task world contains such an agreement (task 1's other agreements are active with no notices, so both readings give the past-due balance). Not demonstrable here, so an observation. |

- **P4 / P10.** The restoration and good-faith payments are now defined as the remainder: "the returned balance less the (winter) re-deferral, so that the two together make up the returned balance to the cent". They are used only as payment thresholds. The definitions are consistent with the rounded re-deferral.
- **Compute unchanged.** All six policies' `compute`, `params`, `factors` and `prerequisite` were printed and checked expression by expression against the revision_2/3 reads. They are identical; the change is prose only. The prerequisite `policy_source` sentences are still verbatim in their blocked rules. The graph is unchanged.
- Previously open observations: R2-O1 and R3-O1 unchanged. R2-O2 closed. O4, O5 and O6 unchanged (tool module unchanged). The redeferral's reinstatement_rule replacement still reads "the plan" rather than "the deferred payment agreement". It is scoped by its rule's opening sentence, and the winter replacement names its own case, so this is unchanged since round 2 and remains an observation (R4-O2).
- **No new RED.**

### closing_checklist (revision_4)

Written after the round-4 reveal (2026-10-08T02:26:35Z).

- Per-task files carry revision_4 frozen and comparison sections. Revisions 1-3 are untouched.
- Every relationship is PASS for both tasks. Every gold argument, factor sensitivity, baseline result and skip value reproduces exactly and is unchanged from round 3.
- Coverage, disjoint scopes, tools and uuid8s: unchanged.
- Trees: unchanged.
- Factor structure: unchanged and passing. No compute changed.
- Gates: the coordinator's round-4 snapshot, all OK including check_traceability, is cited.
- Open observations (no consequence on any task world): O1, O4, O5, O6, O9, O10, O13, O14, R2-O1, R3-O1, R4-O1, R4-O2.
- **Difficulty result (revision_4): PASS for both tasks.** The render-layer conflict reported by the policy-KB audit (D2/P7) is closed at the source.
