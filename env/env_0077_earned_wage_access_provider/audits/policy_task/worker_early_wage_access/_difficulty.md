# Policy-task audit — worker_early_wage_access / charter-global

## revision_1

## charter_global_frozen
- Frozen 2026-10-23T00:12Z by the independent policy auditor (fresh agent, not the instantiator), before any task GT was revealed.
- Hashes: `access.extended.yaml` sha256 e9e930ee9721c9ff…; `task_tools.py` sha256 79c12bb0392abdbd… (match the coordinator snapshot /tmp/erl0077_coord/snap_worker_early_wage_access_r1.txt).
- Read: blueprint.yaml, products/access.yaml (+ card.yaml rules for cross-category realism), db_schema.json, share_tools.py signatures, the extended charter, task_tools.py, audits/render_source/XF_recipe.md, owner_ruling.md, the masked views 0/1.view.json (frozen_time, user_scenario, initial_state only).
- Masked / unread until both task derivations were frozen: tasks/*.json (evaluation_criteria, computations, charter_scope, required_documents, design_rationale, solvability_contract, prerequisite_closure, db_closure), plan.md, worklog.md. No recursive search touched tasks/*.json.
- Entry conditions (Step 0): the snapshot carries all 7 instantiation gates green (EXTENDED / TASK TOOL CONTRACT / REPLAY --check / SOLVABILITY / COMPUTE / GROUNDING / SCOPE OK) and view hashes 88049bcdd488e218 / bed5ed3de2388214 (re-hashed here, identical). Input complete.
- Base section of the extended file is semantically identical to blueprint/products/access.yaml (YAML-parsed comparison of every top-level key: all True; textual differences are line folding only).

### policy_conflict_scan
Five extended policies, one category (access):

| policy | trigger | target_tool (owner) | computes | prerequisite |
|---|---|---|---|---|
| access_ext_tier_review | state_due | record_tier_review_be8f1edd (agent) | new_variant_name | [] |
| access_ext_bank_transfer_amount | on_request | request_bank_transfer_bc93e4f0 (user) | amount | tier_review (value_input, state) |
| access_ext_bank_transfer_fee | state_due | book_bank_transfer_fee_9f154276 (agent) | amount | bank_transfer_amount (value_input, state) |
| access_ext_instant_transfer_amount | on_request | request_instant_transfer_84ad3b61 (user) | amount | [] |
| access_ext_instant_transfer_fee | state_due | book_instant_transfer_fee_f0fabb61 (agent) | amount | instant_transfer_amount (value_input, state) |

- Overlapping subjects: the two amount schedules both supersede the base "amount available" clause and the "returned or cancelled" clause; their scopes are disjoint by destination/speed (next-business-day bank account vs instant external debit card) and each tail excludes the sibling by name (C3 satisfied). The two fee schedules both supersede the listed-fee clause and the fee-cap clause, disjoint by speed/destination, tails exclude each other (C3 satisfied).
- Triggers: no tool writes an event whose base trigger fires into another category (access_transfer → card:card_load only for destination paystride_card; neither transfer tool can write that destination). E1 satisfied.
- Time anchors: tier review reads the latest period-close payday; amounts read today and next_pay_date; fees read today's highest daily_sequence transfer. Compatible.
- Cross-category read boundaries: card (account status, card_transactions loads) and loan (repaying installment on next_pay_date) declared; the employer configured cap (program_agreements.configured_cap_percent) is read only by the scope sentences of the two amount schedules (no compute read) — acceptable as scope.
- Derived task scopes (pre-reveal, from the trees the rules entail): task 0 = {tier_review, bank_transfer_amount, bank_transfer_fee}; task 1 = {instant_transfer_amount, instant_transfer_fee}. Pairwise disjoint and jointly complete over the 5 policies. Conflicts between policies: see findings P1 (fee confirmation vs. fee-after-transfer) and P3 (deduction-ceiling base).

### rule_compute_equivalence
- Scratch sweep (/tmp/audit_worker_early_wage_access_0077/scripts): every compute_basis quote is verbatim in its own rule (0 misses, all 5 policies); every overwrite superseded_clause is verbatim in its base rule and every replaced_by is verbatim in the extended rule; every baseline.rule sentence is in the rule; every prerequisite policy_source is verbatim in the blocked rule.
- Rule sentences carrying no compute_basis quotation (observations, no consequence found): the "last N months" definition sentences (tier review, bank amount, instant amount, instant fee — implemented by DSL MONTHS, which matches the stated convention exactly); the two baseline room sentences of the instant amount ("The instant percentage room is …", "The instant pay-period room is …") are implemented inside the shortfall_method bindings it_pct_room / it_period_room but quoted only through the shortfall-method sentence; the scope / prerequisite / overwrite-tail sentences (no compute expected).
- Tiers in both faces: every `factors[].ladder` tier is a rule sentence and a branch of its decides binding, and vice versa, for all 23 declared factors. Rounding: amounts "rounded down to the cent" = int(x*100+1e-7)/100; fees "rounded half up" = RND(x+1e-9,2) (run ruling); estimate method "rounded down to the cent once" = int(…+1e-7)/100. All consistent.
- Edge probes (B1/B2): no period close line → tips share 0.5, estimate method falls to recorded net, cap method biweekly (weekly branch sums pay_date=None → 0, equivalent) — rule and compute agree; no transfer today → fee compute degenerates (bf_seq/if_seq = 0, amount 0) but that world is outside the fee scope ("the fee of the plan's latest transfer of the day"); absent card → points/shares fall through; absent loan → `or 0` → no ceiling room. Tie rule for "latest transfer of the day" stated (highest daily_sequence). Observation: bank-amount loan read takes the first repaying loan (CFIELD) while base access_msr_loan_installment_due sums all repaying loans — only differs for two loans due the same payday; not demonstrable on either world.
- Observation: bank-amount rule says overtime lines count "only where overtime_included_in_accrual is true" yet overtime_share gives 0.5 on one correction regardless of the flag; every tier sets the flag true, so no producible world separates them.

### action_binding_and_uuids
- Each (target_tool, computes) is claimed by exactly one policy. Tool bodies validate format/existence only (positive amount, YYYY-MM-DD, known tier name, transfer exists on the plan); none judges a prerequisite, a scope or a policy figure. Every write tool calls ctx.create/ctx.update in its own body; no forbidden import/call; money helper is an exact Decimal ROUND_HALF_UP static method; no docstring carries an example value, an ordering word, another tool's name or a composite argument.
- uuid8s be8f1edd, bc93e4f0, 9f154276, 84ad3b61, f0fabb61: distinct, no shared prefix/suffix, no sequential pattern. No factor id is a substring of a tool name (A8). Observation: the factor id `autorecovery_share` is declared twice (bank fee and instant fee) — if any downstream check keys factor documents by bare id this collides; no consequence demonstrable at this layer.
- Owner ruling: the two owner=user tools are the worker's own transfer requests (ruling (b)); base access_evt_transfer_availability already states "An early wage transfer is booked only on the worker's own confirmation …", no base sentence assigns the act to the agent, so no scoped overwrite is required. Accepted.

### prerequisite_graph
- `prerequisite` filled on all 5 policies; edges: bank_transfer_fee → bank_transfer_amount → tier_review; instant_transfer_fee → instant_transfer_amount. Acyclic; every `problem` is an extended policy id of this file, none self/base.
- Each policy_source is verbatim in the blocked policy's own rule; form=state on all three, no fallback_reason (correct); kind=value_input with gates bt_pct, bf_amount, if_amount — all real compute bindings; resolved_by = the depended-on policy's target_tool; effect consistent (the review's tier sets the tier parameters bt_pct / rooms read; the transfer row sets bf_amount / if_amount, pay_date, position). Conditions neither strengthened nor weakened relative to the sentences; no authoring-viewpoint phrasing.

### prerequisite_sentences
1. Bank amount ← tier review: "The bank transfer amount is worked out only after the plan's level effective date falls later than the pay date of its latest period close line, where it has one." Connective "only after"; record-visible state (level effective date vs pay date of the latest period close line), no tool/id/snake_case; "where it has one" carries the no-close-line case. Exactly one write of this difficulty sets level_effective_date: the tier review (its rule: "that day is recorded as level_effective_date", the later of the day after the payday and the review day, hence always after the payday). Single reading. PASS.
2. Bank fee ← bank transfer: "The bank transfer fee is fixed only after the next-business-day bank transfer it prices stands on the plan's ledger as today's latest transfer entry." State form; only the bank-transfer request writes a next-business-day bank-account transfer. PASS.
3. Instant fee ← instant transfer: "The instant transfer fee is not fixed until the instant transfer to an external debit card it prices stands on the plan's ledger as today's latest transfer entry." State form ("not … until"); only the instant-transfer request writes an instant external-debit-card transfer. PASS.
- Depended-on rules do not restate the sentences; no rule states another cross-problem order that grounds no edge; docstrings are silent on sequence. Observation: the instant amount carries no prerequisite on the tier review although it reads the same tier parameters; on a world whose latest payday review is unrecorded the instant amount would read a stale tier with nothing on the policy surface saying so (task 1's review is recorded, so no consequence there).
- But see P1: sentences 2 and 3 contradict an in-force base sentence.

### override_declarations
Sentence-by-sentence over each base_policy_refs entry (findings only):
- access_ext_tier_review vs access_level_review: cadence/after-recoveries — follows; active-only — inherited; paused/suspended keep tier — inherited; moves-up-on-gates — superseded (declared); "at most tier_upgrade_max_steps_per_review" — follows (one tier = param 1 on every tier); "A payday with a shortfall moves the plan down …, and a write-off returns it to Starter when writeoff_resets_to_starter is true; … the downgrade prevailing" — handled differently for one case, UNDECLARED (finding P2); new-tier-applies-from — superseded (declared); no tier outside review — follows. vs access_evt_writeoff: "when writeoff_resets_to_starter is true the plan returns to Paystride Access Starter at the next level review" — same undeclared narrowing (P2).
- access_ext_bank_transfer_amount vs access_evt_transfer_availability: worker confirmation of "amount, delivery speed, destination and fee" — in force, contradicted by the fee schedules (P1); active / cutoff / business days / after-cutoff / current period — follow; amount-available — superseded; returned-or-cancelled — superseded; open-shortfall clause — not superseded, restated consistently (multiplier, zero when above limit or percentage zero); rounding / never below zero / above-available / minimum / min accrued / count limits / delivery / daily_sequence — follow or inherited. vs access_agg_combined_daily_limit: single-plan scope; returned transfers now count toward the day room — covered by the declared returned-or-cancelled overwrite. vs access_combined_deduction_ceiling: "the period's transfers plus that installment may not exceed combined_deduction_ceiling_percent_of_net of access_msr_period_accrued_net" — the bank deduction-ceiling room uses the bank accrued net instead, UNDECLARED (P3). vs access_earnings_accrual: two sentences superseded (declared); lag sentence restated equivalently for lag ∈ {0,1}; correction and period-close sentences follow. vs access_card_destination: not engaged (bank destination).
- access_ext_instant_transfer_amount: same sweep; amount-available, returned-or-cancelled and open-shortfall clauses superseded (declared); deduction ceiling scoped out; accrued net restated at recorded net with the base flags (equal to base). No undeclared departure beyond P1.
- access_ext_bank_transfer_fee / access_ext_instant_transfer_fee vs access_evt_transfer_fee: one-fee — follows; own entry / pay_date / never from amount — follows (tool bodies); listed fee — superseded; "adjustments … do not add to one another", tier benefit, fee model — in force as the scope test; fee cap — superseded; zero → no entry — follows. Observation: the instant post-allowance position subtracts only delivery_failed returns while the in-force tier-benefit test counts base access_msr_period_instant_count (all returns excluded); the two counts differ only when a period holds an instant transfer returned for another reason (not on task 1's world).

### factor_ladders
| policy | factor | effect | tiers | multi-source | cross_difficulty | structural verdict |
|---|---|---|---|---|---|---|
| tier_review | recovery_count_method | method | 3 | no | – | ok (tier 2 adds an input, fall-through adds a conditional pick) |
| tier_review | tenure_allowance | parameter | 6 | no | – | ok |
| tier_review | writeoff_allowance | parameter | 3 | no | – | ok |
| tier_review | open_shortfall_allowance | parameter | 3 | no | – | FAIL: tiers 2 and 3 select the same outcome in every world (F2) |
| bank_amount | card_wage_points | parameter | 3 | yes (account status AND loads) | card | ok |
| bank_amount | tenure_share | parameter | 3 | no | – | ok |
| bank_amount | tips_share | parameter | 3 | yes (tier flag AND lines) | – | ok |
| bank_amount | overtime_share | parameter | 3 | no | – | ok |
| bank_amount | estimate_method | method | 3 | yes | – | ok (own ratio input / tariff average / recorded net) |
| bank_amount | return_share | parameter | 3 | no | – | ok |
| bank_fee | cap_period_method | method | 3 | no | – | ok (prior-period input / day-ratio scaling / plain) |
| bank_fee | first_nbd_share | parameter | 3 | yes (ledger AND tier) | – | realism, see F3 |
| bank_fee | small_amount_share | parameter | 3 | no | – | realism, see F3 |
| bank_fee | autorecovery_share | parameter | 3 | yes (plan flag AND card) | – (reads card existence) | FAIL realism (F3, F4-blocked tier) |
| instant_amount | shortfall_method | method | 4 | yes | – | ok |
| instant_amount | push_failure_share | parameter | 3 | no | – | ok |
| instant_amount | new_destination_share | parameter | 3 | no | – | ok |
| instant_amount | velocity_share | parameter | 3 | no | – | ok |
| instant_amount | weekend_share | parameter | 3 | no | – | FAIL realism (F5) |
| instant_fee | surcharge_method | method | 3 | yes (tier AND amount) | – | FAIL label: band tables of one formula (F1) |
| instant_fee | post_allowance_share | parameter | 3 | yes | – | realism, see F3 |
| instant_fee | card_pay_share | parameter | 3 | no | card | realism, see F3 |
| instant_fee | autorecovery_share | parameter | 3 | yes | – | FAIL realism (F3, blocked tier) |
| instant_fee | payday_distance_share | parameter | 3 | no | – | realism, see F3 |

- Counts as declared: tier_review 4 (1 method, 3 parameter); bank_amount 6 (1/5); bank_fee 4 (1/3); instant_amount 5 (1/4); instant_fee 5 (1/4). Every decides is an input (not result); binding sets pairwise disjoint within each policy; every ladder stated in full in its rule. No factor reads another factor's binding (A1 table: all factor inputs are plain bindings or raw reads; assembly lives in bt_accrued/bt_pct/bt_lowest/result, bf_listed/result, it_lowest/result, if_listed/result, rv_up/rv_new).
- Counts after the structural/realism strikes below: tier_review 3 (< 4); instant_fee 0 method (< 1); bank_fee and instant_fee lose their padded shares (F3) and fall below 4; instant_amount 4 (still within bounds).
- Cross-difficulty per task: task 0 via card_wage_points (card), task 1 via card_pay_share (card). Multi-source per task: task 0 card_wage_points / first_nbd_share; task 1 post_allowance_share.

### findings
Each finding: symptom → root cause → evidence → demonstrated consequence → affected artifact.

**P1 SOURCE-POLICY RED — fee fixed only after the transfer vs. the in-force base requirement that the worker confirm the fee before the transfer is booked (undeclared departure, XF C2).** Base access_evt_transfer_availability, not superseded by any overwrite: "An early wage transfer is booked only on the worker's own confirmation of its amount, delivery speed, destination and fee." Extended bank fee: "The bank transfer fee is fixed only after the next-business-day bank transfer it prices stands on the plan's ledger as today's latest transfer entry."; extended instant fee: "The instant transfer fee is not fixed until the instant transfer to an external debit card it prices stands on the plan's ledger as today's latest transfer entry." In the same situation (before the transfer write) the base says a fee figure must exist and be confirmed, the extended says it does not exist yet; evaluating the fee schedule on the pre-transfer world gives a different figure from the one booked (demonstrated per task in 0.md / 1.md). Bears on tasks 0 and 1. Artifact: extended.yaml access_ext_bank_transfer_fee.rule / access_ext_instant_transfer_fee.rule (no overwrite naming the base sentence).

**P2 SOURCE-POLICY RED — tier review drops the base write-off reset for a write-off booked between the payday and the recording of its review (dropped branch, undeclared).** Base access_level_review: "a write-off returns it to Paystride Access Starter when writeoff_resets_to_starter is true"; base access_evt_writeoff: "when writeoff_resets_to_starter is true the plan returns to Paystride Access Starter at the next level review." Extended: "when writeoff_resets_to_starter is true and the plan's latest write-off was booked after its level_effective_date and on or before that payday, the plan returns to Paystride Access Starter". Situation: payday 2026-10-15, write-off booked 2026-10-18, review of 10-15 recorded 2026-10-21 (level_effective_date 10-21). Base: the next review after the write-off (this one) resets to Starter. Extended: 10-18 is after the payday → no reset now (and the write-off allowance treats a write-off "after the payday" as Premier Plus); at the 10-30 review 10-18 is not after level_effective_date 10-21 → no reset ever. Two different tiers. Neither superseded_clause names these sentences. No task world holds a write-off, so no task consequence. Artifact: access_ext_tier_review.rule / overwrite.

**P3 SOURCE-POLICY RED — bank deduction-ceiling room changes the base of access_combined_deduction_ceiling without an overwrite.** Base: "the period's transfers plus that installment may not exceed combined_deduction_ceiling_percent_of_net of access_msr_period_accrued_net". Extended bank amount: "the bank deduction-ceiling room is combined_deduction_ceiling_percent_of_net, divided by one hundred, times the bank accrued net, less the bank period taken, less that loan's installment_amount" — the bank accrued net carries the overtime/tips shares and the estimate method. On task 0's world with a repaying loan due 2026-10-30 the two bases are 1270.73 (base measure) vs 1212.025 (bank accrued net): the ceiling room differs by 29.35 for the same installment. Not engaged on task 0 (no loan), so charter-only. Artifact: access_ext_bank_transfer_amount.rule / overwrite list.

**P4 SOURCE-POLICY RED — assembly / overwrite sentences name factor quantities (XF A2), all members.** (a) bank amount: "points are added to the tier's access_cap_percent first" (names card_wage_points' quantity); replaced_by sentences "counts at the value the estimate method below gives" and "overtime lines count at the overtime share and card tips lines at the tips share set out below" (name estimate_method, overtime_share, tips_share inside base-clause replacements that the computation document must carry); (b) bank fee: "and the room is measured as the cap method below sets it" (names cap_period_method); (c) instant amount: replaced_by "For the instant transfer amount an open shortfall is handled by the shortfall method below" and "The shortfall method below acts on the instant percentage room and the instant pay-period room" (name shortfall_method); (d) instant fee: "Any surcharge below is added to the tier's instant_fee_external_debit_usd first" (names surcharge_method's quantity). Consequence: the computation document that must carry these sentences points the reader at a named factor document (the factor is no longer "referenced by nothing", and the baseline stops being silent about the variation); renderers cannot place them without breaking one of the two KB requirements. Tier review's allowance sentences are generic (not a member).

**F1 SOURCE-FACTOR RED — instant fee surcharge_method is mislabelled `method`.** All three tiers compute the same quantity by the same formula — a surcharge looked up from the transfer amount by band: "0.30 for every started 100.00 of the amount above 100.00" is the band table {100.01–200.00: 0.30, 200.01–300.00: 0.60, 300.01–400.00: 0.90, 400.01–500.00: 1.20}; "1.00 for 100.01 to 250.00 and 2.00 for 250.01 to 500.00" is another band table; "no surcharge" is the 5.00–100.00 band. The base charter itself types this quantity as a parameter (parameter_schema instant_fee_band_surcharge_usd: "Ladder (mapping of transfer-amount band in USD -> surcharge in USD)") and already varies it per tier. Only the numbers change → `parameter`. Consequence: the instant fee has 0 honest method factors (< 1). Bears on task 1.

**F2 SOURCE-FACTOR RED — tier review open_shortfall_allowance has two tiers with one outcome.** Tier 2 ("above zero but not above … max_open_shortfall_usd_for_continued_access holds the plan at its current tier", rv_open_allow = rv_cur) and tier 3 ("above that, only Paystride Access Starter", rv_open_allow = 1) both give rv_up ≤ rv_cur, hence rv_new = MX(rv_cur, rv_up) = rv_cur, in every producible world (the allowance never downgrades: "moves up … and in no other way"). The ladder is binary (zero-or-less vs above zero), below the three-distinct-tier floor; with it struck the tier review has 3 factors (< 4). Bears on task 0.

**F3 SOURCE-FACTOR RED (realism, XF F3/F1) — both transfer-fee schedules are padded computations of a flat service fee.** The next-business-day bank fee (0.00–1.99 by tier) and the instant external-debit fee (1.99–3.49 plus band) are flat published service fees; the extended schedules multiply them by stacked percentage "shares" (bank: first_nbd_share, small_amount_share, autorecovery_share; instant: post_allowance_share, card_pay_share, autorecovery_share, payday_distance_share) producing odd-cent fees no EWA program publishes. Specific tiers that no such business would publish: the blocked-card tier of both autorecovery_share factors ("at 90 percent [bank] / 95 percent [instant] when the worker holds no active card account but holds one whose status is blocked") — a discount for a card-recovery authorization that, by the in-force base rule, cannot be used ("A card autorecovery debit may be attempted only while the worker's Paystride Visa Payroll Card account status is active."); and the payday_distance_share (fee halved two days before payday), a dimension no fee schedule in this line publishes. Bears on tasks 0 and 1 (fee factor counts fall below 4 once the padded shares are struck).

**F5 SOURCE-FACTOR RED (realism, XF F1) — instant amount weekend_share.** "The weekend share multiplies the instant transfer amount by 80 percent when today is a Saturday, by 90 percent when today is a Sunday" — the day of the week is not a dimension on which an EWA program publishes the amount of earned wages available (the base charter's only weekend dimension is whether instant runs on weekends, weekend_instant_available), and the Saturday/Sunday asymmetry has no business basis. Bears on task 1 (Saturday world).

Observations (no RED): open-shortfall/assembly quotation gaps above; duplicate factor id `autorecovery_share`; loan CFIELD vs sum; overtime flag vs share; instant amount lacks a tier-review prerequisite; the base gate for re-running a recorded review (the tier review rule has no sentence saying a payday's review is recorded once — only the bank amount's prerequisite sentence reveals the recorded state).

## post_reveal_summary (written after both task derivations were frozen and compared)
- Both tasks' independent derivations match GT figure for figure (writes, arguments, factor sensitivities, baseline results, prerequisite closures). The REDs are defects of the charter, the seed and the realism of the schedules, not derivation mismatches.
- Scopes: task 0 = {access_ext_tier_review, access_ext_bank_transfer_amount, access_ext_bank_transfer_fee}; task 1 = {access_ext_instant_transfer_amount, access_ext_instant_transfer_fee} — matches charter_scope of both tasks; disjoint, jointly complete; difficulty-wide prerequisite graph acyclic.
- Task-level finding not visible pre-reveal from the charter alone: T1-F4 (task 1 seed: 10-16 shortfall contradicts recorded net pay 767.82, justified in GT prose by a garnishment no record holds; card ledger overdraft and balance mismatch) — see 1.md.
- closing_checklist: NOT written — the difficulty does not pass (Step 4 runs only after all four relationships PASS). Gates were not re-run by this auditor (coordinator snapshot cited).

RED ids:
- P1 (both tasks): fee fixed only after the transfer vs in-force base "booked only on the worker's own confirmation of its … fee" (undeclared departure).
- P2 (charter): tier review drops the base write-off reset for a write-off booked between the payday and the review's recording (undeclared dropped branch).
- P3 (charter): bank deduction-ceiling room uses the bank accrued net instead of access_msr_period_accrued_net (undeclared).
- P4 (both tasks): assembly / overwrite sentences name factor quantities (points, estimate method, overtime/tips share, cap method, shortfall method, surcharge).
- F1 (task 1): instant fee surcharge_method is a per-tier band table labelled `method` → 0 method factors.
- F2 (task 0): tier review open_shortfall_allowance tiers 2 and 3 have one outcome in every world → 3 factors.
- F3 (both tasks): both fee schedules are padded computations of flat service fees; blocked-card autorecovery tiers and payday-distance share are treatments no EWA program publishes.
- F5 (task 1): instant amount weekend_share is not a dimension EWA availability is priced on.
- T1-F4 (task 1): seeded 10-16 shortfall / missing payroll load / card overdraft and balance mismatch contradict the access and card charters; scored amount and fee rest on them.

VERDICT revision_1: task0=RED task1=RED charter=P1,P2,P3,P4,F1,F2,F3,F5

## revision_2

## charter_global_frozen (revision_2)
- Frozen 2026-10-23T01:17Z by the same independent auditor, before tasks/0.json or tasks/1.json of round 2 was opened. Coordinator gate snapshot: /tmp/erl0077_coord/snap_worker_early_wage_access_r2.txt (run by this auditor via snapshot.sh, execute-only): all 7 gates OK; views r2/0.view.json sha256 21328d23fa34758f…, r2/1.view.json c38f887b309a06c3…; access.extended.yaml 1e48e005ad89e834…, task_tools.py fe46c5f185402645… — both changed since revision_1, so every charter-global section below is re-derived in full (revision_1 text above is left untouched). Worklog precondition line "REWORK round 2: gates 7/7 green" confirmed; the reworker's claims were read by item id only.
- Masked until both r2 task derivations were frozen: tasks/*.json GT fields, plan.md, the worklog body beyond the claims section.
- Base section of the extended file: still semantically identical to blueprint/products/access.yaml.

### policy_conflict_scan (r2)
| policy | trigger | target_tool (owner) | computes | prerequisite |
|---|---|---|---|---|
| access_ext_tier_review | state_due | record_tier_review_be8f1edd (agent) | new_variant_name | [] |
| access_ext_bank_transfer_amount | on_request | request_bank_transfer_bc93e4f0 (user) | amount | tier_review (value_input, state) |
| access_ext_bank_transfer_fee | state_due | book_bank_transfer_fee_9f154276 (agent) | amount | bank_transfer_amount (value_input, state) |
| access_ext_missed_recovery_review | state_due | record_missed_recovery_review_3a64d9dd (agent) | new_variant_name | [] |
| access_ext_instant_transfer_amount | on_request | request_instant_transfer_84ad3b61 (user) | amount | missed_recovery_review (value_input, state) |
- The instant transfer fee schedule is gone; instant fees fall back to the base fee rule (base listed fee, tier benefit, fee model, cap), which needs no post-transfer state.
- Two policies now share subject access_level_change. Their scopes are disjoint by a record test (the latest closed payday does or does not carry a shortfall), each names the other ("a payday that carries a shortfall is reviewed under the missed-recovery review schedule instead" / "a payday that carries no shortfall is reviewed under the tier review schedule instead"), and each carries a once-per-payday sentence (closes the revision_1 observation about re-running a recorded review).
- Triggers (E1): the tools still write only bank-account / external-debit-card transfers, fees with no trigger and plan updates. Clean.
- Derived scopes (pre-reveal): task 0 = {tier_review, bank_transfer_amount, bank_transfer_fee}; task 1 = {missed_recovery_review, instant_transfer_amount}. Disjoint, jointly complete over the 5 policies.

### rule_compute_equivalence (r2)
- Sweep (scratch ev.py on the r2 file): every compute_basis quote verbatim in its rule; every compute binding has a basis; every superseded_clause verbatim in its base rule and every replaced_by verbatim in the extended rule; every baseline.rule sentence and every prerequisite policy_source verbatim in the blocked rule. 0 misses over 5 policies.
- Tiers in both faces: every declared ladder tier is a branch of its decides binding and a rule sentence, and vice versa. Exception: N2 below (a tier ladder that lives in plain bindings, outside every factor).
- Edge probes: tier review, no write-off → reset 0, write-off allowance top; no period close → tenure 0, earnings allowance from an empty sum. Missed-recovery review, no write-off → wo_days 9999 → one below. Cure method, no card → voluntary tier or nothing. pd_due 0 → share 0. Bank fee: free first transfer, 'HH:MM' > '17:00' string test (17:00 itself is not after), weekday from 2024-01-01 (a Monday). Instant: no accrued net with an advance → ratio 1. Rule and compute agree on every probe.
- Observation (P3 restatement): the bank deduction-ceiling base is worded "the period's accrued net as the base accrual rule measures it, every sync line at its recorded net_amount less the correction lines", while the compute (bt_base_accrued) drops overtime, shift-differential and tips lines whose inclusion flag is false. This follows the base accrual rule's flags, but the appositive "every sync line" reads wider. It differs only on a tips-excluded tier that has tips lines and a repaying loan; not engaged.

### action_binding_and_uuids (r2)
- (target_tool, computes) pairs are unique; the new uuid8 3a64d9dd is independent of be8f1edd, bc93e4f0, 9f154276 and 84ad3b61. Tool bodies only check format and existence; no forbidden import; no example values; no ordering words.
- Observations: (a) the record_missed_recovery_review docstring offers "Paystride Access Premier Plus" "when it stays on the top tier", but the rule never lets a missed-recovery review land higher than one tier below the current tier, so that value is unreachable; (b) the request_bank_transfer docstring says "delivered by ACH on the next business day", but a request after 17:00 is delivered a business day later under the base rule. Neither changes a scored argument.

### prerequisite_graph (r2)
- Edges: bank_fee → bank_amount → tier_review; instant_amount → missed_recovery_review. Acyclic. Every policy_source is verbatim in its own rule; form is state on all three edges with no fallback; gates bt_pct, bf_amount and it_pct_room are real bindings; resolved_by is the depended-on policy's target_tool. Conditions match their sentences, including the new shortfall / no-shortfall qualifiers.

### prerequisite_sentences (r2)
1. "The bank transfer amount is worked out only after the plan's level effective date falls later than the pay date of its latest period close line, where it has one and that payday carries no shortfall." PASS. Two tools can write level_effective_date, but by the two review rules' own scope sentences only the tier review governs a payday with no shortfall, so the hop has a single reading.
2. "The bank transfer fee is booked only after the next-business-day bank transfer it prices stands on the plan's ledger as today's latest transfer entry." PASS.
3. "The instant transfer amount is not worked out until the plan's level effective date falls after the pay date of its latest period close line, where a shortfall carries that payday." PASS. The single resolver is the missed-recovery review.
- Observation: each amount waits on only one of the two review schedules. A bank request after an unrecorded shortfall-payday review, or an instant request after an unrecorded no-shortfall review, reads the tier on file, although the other review rule calls that review owed. No ordering sentence settles which comes first. This is not engaged on either task world.

### override_declarations (r2)
- tier_review: the moves-up clause and the effective-date clause are superseded (declared). Sentence 6 (shortfall downgrade and write-off reset) is now split: shortfall paydays go to the missed-recovery schedule, which supersedes it (declared), and the write-off reset is kept as "a write-off was booked on the plan after its level_effective_date" (the "on or before that payday" limit of revision_1 is gone). The same-day case is still dropped: see P2r.
- missed_recovery_review vs access_level_review: the shortfall-downgrade sentence is superseded (declared). Its rule also states "The tier this review sets applies from the later of the day after the payday and the day the review is recorded", which departs from the base sentence "The new tier applies to transfers booked from the day after the payday, which is recorded as level_effective_date." That base sentence is named only in the sibling tier review's overwrite ("for every review under this schedule and under the missed-recovery review schedule"), not in this policy's own overwrite: see N1.
- bank_amount: the base of access_combined_deduction_ceiling is now the base accrual (P3 closed; see the restatement observation above). Other sentences as in revision_1.
- bank_fee: base access_evt_transfer_availability "booked only on the worker's own confirmation of its amount, delivery speed, destination and fee" is now honoured: "The bank transfer fee is quoted to the worker … worked out for that transfer as confirmed, the transfer counted as booked today, so the figure quoted is the figure booked." (P1 closed). The free first bank transfer and the new adjustments sit inside the superseded listed-fee clause (declared).
- instant_amount: unchanged apart from the new prerequisite sentence and the period-advance share. No undeclared departure.

### factor_ladders (r2)
| policy | factors (effect) | tiers | notes |
|---|---|---|---|
| tier_review | recovery_count_method (m), tenure_allowance (p), writeoff_allowance (p), earnings_allowance (p) | 3/6/3/6 | the open shortfall is now a plain no-upgrade gate, matching base no_open_shortfall (F2 closed); earnings allowance is a real dimension (six-month net pay) with distinct tiers |
| bank_amount | card_wage_points (p, card, multi-source), tenure_share, tips_share, overtime_share (p), estimate_method (m), return_share (p) | 3 each | the overtime share now honours its flag (revision_1 observation closed) |
| bank_fee | free_transfer_allowance (p, multi-source), settlement_timing_fee (p, multi-source), bank_band_surcharge (p), cap_period_method (m) | 3 each | additive round-figure components on a flat fee; no stacked percentages, no blocked-card tier, no payday distance (F3 closed); free_transfer_allowance reads as a free-amount threshold (none / 100.00 / unlimited), so `parameter` is honest |
| missed_recovery_review | repeat_protection, tenure_protection, writeoff_protection, payroll_continuity_protection (p), cure_protection (m, card, multi-source) | 3 each | see N2 |
| instant_amount | shortfall_method (m), push_failure_share, new_destination_share, velocity_share, period_advance_share (p) | 4/3/3/3/3 | weekend share replaced by an advance-utilisation share, a real dimension (F5 closed) |
- Counts: 4 / 6 / 4 / 5 / 5, each with at least 2 `parameter` and 1 `method`. Per task: task 0 has a multi-source factor (card_wage_points, free_transfer_allowance) and a cross-difficulty factor (card_wage_points); task 1 has both in cure_protection (card).
- No factor reads another factor's binding. Assembly sentences are generic (P4 closed): "any that adds … then any that multiplies …", "any that decides whether … then any that sets … then any amount added …", "Each allowance / protection below names the highest tier …".
- Every-world tier collapse (F2 class) swept on all ladders: none. The missed-recovery protections collapse only on Standard / Plus plans (world-dependent).

### findings (r2)
Closed from revision_1: P1, P3, P4, F1 (instant fee removed), F2, F3, F5; revision_1 observations on the duplicate factor id, the overtime flag and review re-runs are closed.

**P2r SOURCE-POLICY RED — the write-off reset still drops a same-day write-off (dropped branch; XF B1 same-day tie).** Both review schedules reset only "when writeoff_resets_to_starter is true and a write-off was booked on the plan after its level_effective_date" (rv_reset / pd_reset: rv_last_wo > level_effective_date). Base access_evt_writeoff: "the plan returns to Paystride Access Starter at the next level review". Situation: a review recorded on 2026-11-02 for payday 10-30 sets level_effective_date 2026-11-02, and a write-off is booked later the same day. Base: the next review (of 11-13) returns the plan to Starter. Extended: 11-02 is not after 11-02, so no review ever resets. The two rules give different tiers, and no rule states the tie. Charter only; neither task world holds a write-off.

**N1 SOURCE-POLICY RED — the missed-recovery review departs from a base sentence its own overwrite does not name.** Base access_level_review: "The new tier applies to transfers booked from the day after the payday, which is recorded as level_effective_date." Missed-recovery rule: "The tier this review sets applies from the later of the day after the payday and the day the review is recorded, and that day is recorded as the plan's level_effective_date." access_ext_missed_recovery_review.overwrite holds only the shortfall-downgrade clause; the replacement is declared inside the tier review's overwrite. This bears on task 1, whose scored level_effective_date depends on which clause governs (demonstrated in 1.md).

**N2 SOURCE-FACTOR RED — the missed-recovery cure ladder sits outside every factor and outside the baseline (XF A4; dishonest factor baseline).** The protection ladder "An unrecovered share of 25 percent or less lets the plan keep the tier one below its current tier, more than 25 percent up to 75 percent the tier two below, and more than 75 percent leaves only Paystride Access Starter" is computed in the plain bindings pd_share / pd_cure_allow. cure_protection declares decides = pd_collected (bindings pd_card_coll, pd_vol_coll, pd_collected) and baseline pd_collected = 0. baseline.rule states only "At a review under this schedule the plan returns to Paystride Access Starter." Substituting cure_protection's declared baseline leaves the share ladder active, and the plan still keeps a protected tier. baseline.rule, read alone, protects nothing. The factor's baseline is therefore not what baseline.rule states for the factor's effect, and the ladder sentence belongs to neither document. Bears on task 1 (demonstrated in 1.md).

## post_reveal_summary (revision_2)
- Both revision_2 derivations match GT on every write, argument, closure edge, factor sensitivity and baseline result. Scopes match charter_scope (task 0: tier review, bank amount, bank fee; task 1: missed-recovery review, instant amount); disjoint and complete; the graph is acyclic.
- Class re-sweep across the whole charter for every class raised in any revision:
  - P1 (fee confirmation): no member left.
  - P2 (dropped reset branch): the same-day tie in both review schedules (P2r).
  - P3 / N1 (undeclared base departure): only the missed-recovery effective-date clause (N1).
  - P4 / A2 (assembly sentences naming factors): none.
  - F1 (mislabel): none.
  - F2 (every-world tier collapse): none.
  - F3 (padded flat fee): none.
  - F5 (unreal dimension): none.
  - N2 / A4 (ladder outside factors): cure share ladder only.
  - T1-F4 (seed rows contradicting their charters): task 1 10-18 purchase over the daily limit only; task 0 is clean.
- closing_checklist: not written; the difficulty does not pass.

RED ids (revision_2):
- P2r (charter): the write-off reset "booked after its level_effective_date" drops a write-off booked on a review's own recording day.
- N1 (task 1): the missed-recovery review departs from the base effective-date sentence without naming it in its own overwrite.
- N2 (task 1): the missed-recovery cure share ladder sits outside every factor and the baseline, so cure's declared baseline is not what baseline.rule states.
- T1-F4r (task 1): the seeded 10-18 card purchase exceeds the Advantage daily purchase limit, and the scored amount rests on the open shortfall it creates.

VERDICT revision_2: task0=PASS task1=RED charter=P2r,N1,N2

## revision_3

## charter_global_frozen (revision_3)
- Frozen 2026-10-23T01:35Z by the same independent auditor, before the round-3 tasks/*.json were opened. Worklog precondition "REWORK round 3: gates 7/7 green" confirmed; claims read by item id only. Snapshot /tmp/erl0077_coord/snap_worker_early_wage_access_r3.txt (run by this auditor, execute-only): 7/7 OK; views r3/0 ccfe54c297cfe38b…, r3/1 329c50e319caeac5…; access.extended.yaml cc1b4da8b286e9b7…, task_tools.py 0a43b9db8bf89e5e… — both changed, so the charter-global checks are re-derived. Unchanged since revision_2: the bank fee policy (no diff). Changed: tier review, bank amount (prerequisite wording, P3 wording), missed-recovery review, instant amount (prerequisite wording, velocity share), tool docstrings. Base section is still identical to the blueprint.

### re-derived checks (revision_3)
- Sweep: every compute_basis quote is verbatim in its rule; every binding has a basis; every superseded_clause is verbatim in its base rule and every replaced_by verbatim in the extended rule; every baseline.rule sentence and every prerequisite sentence verbatim in the blocked rule. 0 misses.
- Overrides: both review schedules now declare the base effective-date sentence in their own overwrite ("from the day the review is recorded"; each tail names the sibling schedule) — N1 closed. The P3 wording is now "each sync line that rule counts", which matches the flag-filtered compute — the revision_2 observation is closed.
- Write-off reset (P2r): both schedules reset for "the plan's latest write-off … booked on or after its level_effective_date and before the day the review is recorded", and add "A write-off booked on the day a review is recorded is taken at the plan's next review" (compute: last_wo ≥ level_effective_date and last_wo < NOW). With level_effective_date = the recording day, a write-off booked later that day is ≥ that date at the next review, so it resets there. Tie stated; no reset dropped — P2r closed.
- Prerequisite sentences: bank "falls on or after the pay date of its latest period close line, where it has one and that payday carries no shortfall"; instant "is no earlier than the pay date …, where a shortfall carries that payday". Due tests: tier review "due only while … level_effective_date is earlier than that payday"; missed-recovery "owed only while … level_effective_date falls before that payday". The equality is consistent: a review recorded on its own payday sets level_effective_date = payday, which satisfies the sentence and is no longer due. Each state-form edge has a single resolver by the schedules' scope sentences. Graph acyclic; gates and resolved_by valid.
- Tools: the missed-recovery enum now says Premier Plus applies "in no situation"; the bank-transfer docstring states the after-cutoff delivery — both revision_2 observations closed. uuid8s unchanged and independent; bodies are format and existence checks only.
- Factors: tier review 4 (1 m), bank amount 6 (1 m), bank fee 4 (1 m), missed-recovery review 5 (1 m), instant amount 5 (1 m). velocity_share is now multi-source (today's instant count AND today's instant sum), with distinct tiers and an honest `parameter` label. cure_protection now decides pd_cure_allow and owns the share ladder (A4 part of N2 closed) — but see N2r.

### findings (revision_3)
Closed from revision_2: P2r, N1, N2 (A4 placement), T1-F4r (see 1.md).

**N2r SOURCE-FACTOR RED — cure_protection's fall-through tier is not its baseline.** Ladder fall-through, stated in the rule and the factor: "otherwise nothing counts as collected", and "the share then sets the tier kept: 25 percent or less one below, up to 75 percent two below, more only Starter". The declared baseline is pd_cure_allow = '1' (Starter only), matching baseline.rule "the plan returns to Paystride Access Starter". The fall-through can yield one or two tiers below (any shortfall ≤ 75 % of the amount due), which is not Starter. So "every factor's fall-through tier is that baseline" fails, and a reader who applies the factor's own fall-through gets a different allowance from the declared baseline. Bears on task 1 (demonstrated in 1.md).

**R3 SOURCE-POLICY RED — the same-day tie moved to the review due tests: a payday's review can drop out (XF B1 / P2 class).** Situation: the review of payday P0 is recorded late, on the next payday P1, before P1's period close is booked. Both schedules set level_effective_date to the recording day, so it becomes P1. After the close, the review of P1 is due only "while the plan's level_effective_date is earlier than that payday" (tier review) / "falls before that payday" (missed-recovery). P1 is not earlier than P1, so P1 is never reviewed. Meanwhile the bank sentence ("on or after") and the instant sentence ("no earlier than") read as already satisfied, so both amounts are worked out on P0's tier. Base access_level_review: "The plan tier is reviewed level_review_cadence" (each payday) — under the base, P1 is reviewed. A shortfall on P1 would never downgrade the plan, and an upgrade would never be tested. No sentence states this tie. Charter only; on both task worlds the prior review was recorded before the reviewed payday (task 0: 09-30 < 10-15; task 1: 08-21 < 10-16).

Re-sweep of every class raised in any revision, whole charter:
- P1 fee confirmation: none.
- P2 / R3 same-day ties and dropped reviews or resets: the due-test tie R3 only.
- P3 / N1 undeclared base departures: none.
- P4 assembly sentences naming factors: none.
- F1 mislabel: none.
- F2 every-world tier collapse: none.
- F3 padded flat fee: none.
- F5 unreal dimension: none (the velocity amount test is a real velocity control).
- N2 / A4 ladder outside factors: none.
- N2r fall-through ≠ baseline: cure_protection only. Checked on every other factor: each fall-through equals its baseline.
- T1-F4 seed rows vs owning charters: none (both card ledgers reconcile; task 1's largest daily purchase is 801.67, under the 4,000.00 limit, and is the worker's rent).

## post_reveal_summary (revision_3)
- Both revision_3 derivations match GT on every write, argument, closure edge, factor sensitivity and baseline result. Scopes match charter_scope; disjoint and complete; acyclic.
- closing_checklist: not written; the difficulty does not pass.

RED ids (revision_3):
- R3 (charter): with level_effective_date now the recording day and the due tests strict ("earlier than" / "falls before"), a review of the previous payday recorded on the next payday makes that payday's review never due. The amount sentences then read as satisfied, so a payday review is dropped, with no tie rule.
- N2r (task 1): cure_protection's fall-through tier (nothing collected, then the share ladder) is not its declared baseline (Starter only).

VERDICT revision_3: task0=PASS task1=RED charter=R3,N2r

## revision_4

## charter_global_frozen (revision_4)
- Frozen 2026-10-23T05:10Z before round-4 GT was opened. Worklog precondition "REWORK round 4: gates 7/7 green" confirmed; claims read by item id only. Snapshot /tmp/erl0077_coord/snap_worker_early_wage_access_r4.txt (run by this auditor): 7/7 OK; views r4/0 21328d23fa34758f… (byte-identical to r2/0), r4/1 87187a5102f1f4f5…; access.extended.yaml 9544e79669a6c6b6…, task_tools.py 630e7c57e9ec1daf… — both changed, so the charter-global checks are re-derived. The bank fee policy is unchanged. Base section still identical to the blueprint.

### re-derived checks (revision_4)
- Sweep: compute_basis verbatim in the rule, every binding has a basis, overwrites verbatim on both sides, baseline.rule and prerequisite sentences verbatim — 0 misses over 5 policies.
- Effective date and due test (R3): both schedules now record level_effective_date = the day after the payday reviewed, "whatever day the review is recorded"; a payday's review is due/owed "while the plan's level_effective_date is on or before that payday"; and "the one review of the latest closed payday covers every payday since the level_effective_date". Both schedules declare this in their own overwrites (the effective-date clause, plus the base cadence sentence "The plan tier is reviewed level_review_cadence …"). A review recorded late, even on the next payday, leaves level_effective_date before that payday, so the next review stays due. Prerequisite sentences: bank "falls after the pay date of its latest period close line, where it has one and no shortfall carries a pay date on or after the level effective date"; instant "… where a shortfall carries a pay date on or after the level effective date". These agree with the due tests at every boundary, and each state-form edge has a single resolver by the two schedules' record-test scope ("a shortfall carries a pay_date on or after the plan's level_effective_date"). R3 closed.
- Cure protection (N2r): the fall-through is now "nothing counts as collected: cured share zero, leaving only Paystride Access Starter" = baseline pd_cure_allow '1' = baseline.rule. The ladder (cured share = collected / the shortfall payday's shortfall; ≥ 50 % one below, 25–50 % two below, < 25 % Starter) lives inside the factor; compute `collected*2 >= short` / `collected*4 >= short` matches the rule. Real dimension (how much of the missed recovery was cured). N2r closed.
- Write-off reset: both schedules reset when "the plan's latest write-off was booked on or after its level_effective_date and on or before the payday reviewed"; the declared overwrite of access_evt_writeoff adds "A write-off counts at the review of the first payday on or after the day it is booked". See R4a.
- Tools: both review docstrings state the date "from which the tier applies to transfers booked on or after it (transfers already booked keep their terms)"; consistent with the rules. Bodies are format checks only; uuid8s unchanged.
- Factors: 4 / 6 / 4 / 5 / 5, each ≥ 2 parameter and 1 method; multi-source and card cross-difficulty factors in each task; every fall-through equals its baseline (re-checked on all 24 factors).

### findings (revision_4)
Closed from revision_3: R3, N2r.

**R4a SOURCE-POLICY RED — the same-day tie moved to the payday itself: a write-off booked on a payday after that payday's review is recorded is never reset (XF B1 / P2 class).** Both schedules: the reset window is [level_effective_date, payday reviewed], and "A write-off counts at the review of the first payday on or after the day it is booked". Situation (biweekly plan): the period close of payday 2026-11-13 is booked and the review of 11-13 is recorded the same day, leaving level_effective_date 2026-11-14. Later that day a write-off is booked (an employment_ended shortfall of 10-14, written off once its 30 days have passed). The first payday on or after 11-13 is 11-13, whose review is already recorded. At the review of 11-27 the write-off (11-13) is not on or after level_effective_date (11-14), so no review ever returns the plan to Starter. Base access_evt_writeoff: "when writeoff_resets_to_starter is true the plan returns to Paystride Access Starter at the next level review" (the review of 11-27). The two rules give different tiers, and no sentence states the tie. Charter only; neither task world holds a write-off.

Re-sweep of every class raised in any revision, whole charter:
- P1 fee confirmation: none.
- P2 / P2r / R3 / R4a same-day ties: R4a only. The due-test and effective-date boundaries are consistent; the reset window is clean except the payday-day write-off.
- P3 / N1 undeclared base departures: none (the cadence, effective-date and write-off clauses are each declared in both schedules' own overwrites).
- P4 assembly sentences naming factors: none.
- F1 mislabel: none.
- F2 every-world collapse: none.
- F3 padded flat fee: none.
- F5 unreal dimension: none.
- N2 / N2r: none.
- T1-F4 seed vs charter: none. Observation: task 1's level_effective_date 2026-08-22 means the no-shortfall paydays 09-04, 09-18 and 10-02 were never reviewed; the revised charter's catch-up sentence makes that state producible and the outcome unchanged (the plan stays on the top tier).

## post_reveal_summary (revision_4)
- Both revision_4 derivations match GT on every write, argument, closure edge, factor sensitivity and baseline result. Scopes match charter_scope; disjoint and complete; acyclic. Both tasks pass all four relationships on their own worlds.
- The difficulty does not close: the charter carries R4a. closing_checklist not written.

RED ids (revision_4):
- R4a (charter): a write-off booked on a payday after that payday's review is recorded falls outside every reset window (level_effective_date is the day after the payday), so no review ever returns the plan to Starter; the base resets at the next review, and no tie rule is stated.

VERDICT revision_4: task0=PASS task1=PASS charter=R4a

## revision_5

## charter_global_frozen (revision_5)
- Frozen 2026-10-23T05:17Z before round-5 GT was opened. Worklog precondition "REWORK round 5: gates 7/7 green" confirmed; claims read by item id only. Snapshot /tmp/erl0077_coord/snap_worker_early_wage_access_r5.txt (run by this auditor): 7/7 OK. Views r5/0 21328d23fa34758f… and r5/1 87187a5102f1f4f5… are byte-identical to the r4 views. task_tools.py 630e7c57e9ec1daf… is unchanged from revision_4. access.extended.yaml 2f274ae934f522c0… changed, so the charter-global checks are re-derived. Base section still identical to the blueprint.

### re-derived checks (revision_5)
- What changed (sentence diff against revision_4): only rule text, overwrite replaced_by text and two prerequisite sentences and conditions, in the tier review, missed-recovery review, bank amount and instant amount. compute, factors and baselines are byte-identical to revision_4 in all five policies, and the bank fee policy is unchanged.
- Sweep: compute_basis verbatim in the rule, every binding has a basis, overwrites verbatim on both sides, baseline.rule and prerequisite sentences verbatim — 0 misses.
- R4a: both schedules now state "Each payday is reviewed once and only after it has closed: the review of the latest closed payday is recorded no earlier than the day after that payday, once that payday's payroll settlement and any write-off booked on it are on the plan". The write-off overwrite adds "a write-off booked on a payday always standing before that payday's review is recorded". With reviews recorded on P+1 or later, and level_effective_date = P+1:
  - a write-off dated P falls in the window [previous level_effective_date, P] of P's review;
  - a write-off dated P+1 or later, before or after the review is recorded that day, is on or after P+1 and no later than the next payday P', so it falls in the window of P''s review.
  - No date falls in no window, and no same-day order matters. R4a closed. Both schedules declare the change in their own overwrites (cadence sentence and write-off sentence).
- Prerequisite sentences: bank "… falls after the pay date of its latest period close line, where it has one, that pay date is before today and no shortfall carries a pay date on or after the level effective date"; instant "… where that pay date is before today and a shortfall carries a pay date on or after the level effective date".
  - On a payday itself, when no review can yet be recorded, neither amount waits, and the tier on file applies, consistent with "transfers booked before it keep the terms in force".
  - From the day after a payday the wait is satisfiable at once by the owed review. No real-world wait.
  - Four-point test passes: state form, ordering connective, no tool names or ids, strength matches the condition. Single resolver per edge by the schedules' record-test scope.
- Factors, multi-source and cross-difficulty, every fall-through equal to its baseline: unchanged from revision_4 (re-checked).

### findings (revision_5)
Closed from revision_4: R4a.

Re-sweep of every class raised in any revision, whole charter:
- P1 fee confirmation: none.
- P2 / P2r / R3 / R4a same-day ties, dropped reviews and dropped resets: none. The due test, effective date, reset window and amount prerequisites agree at every boundary: the payday, the day after it, a review recorded late, a review recorded on the next payday, and a write-off on a payday or on the review day.
- P3 / N1 undeclared base departures: none. The new cadence wording sits inside the declared overwrite of "The plan tier is reviewed level_review_cadence, after that payday's recoveries and any shortfall are booked."
- P4 assembly sentences naming factors: none.
- F1 mislabel: none.
- F2 every-world collapse: none.
- F3 padded flat fee: none.
- F5 unreal dimension: none.
- N2 / N2r ladder placement and fall-through vs baseline: none.
- T1-F4 seed vs charter: none (the worlds are unchanged from revision_4). Observation retained: task 1's unreviewed paydays 09-04 … 10-02 are producible under the catch-up sentence.
- New this round: the "recorded no earlier than the day after that payday" sentence is not enforced by the tool. That is correct, since tools judge no policy, and both task worlds are dated after their reviewed payday (task 0: 10-21 > 10-15; task 1: 10-24 > 10-16).

## post_reveal_summary (revision_5)
- Both revision_5 derivations match GT on every write, argument, closure edge, factor sensitivity and baseline result.

## closing_checklist (revision_5)
- Per-task files 0.md and 1.md correspond one-to-one with tasks/0.json and 1.json; _difficulty.md sits alongside them. Revisions 1–5 are kept in order, and every revision_5 comparison section carries PASS.
- Coverage and scopes: the 5 extended policies are fully covered; task 0 = {tier_review, bank_transfer_amount, bank_transfer_fee}, task 1 = {missed_recovery_review, instant_transfer_amount}, pairwise disjoint over whole trees. Task tools and GT are closed. Each tool's uuid8 (be8f1edd, bc93e4f0, 9f154276, 3a64d9dd, 84ad3b61) is independent and frozen.
- Problem trees:
  - task 0: 2 prerequisite problems, 2 value_input edges, owner=user transfer;
  - task 1: 1 prerequisite problem, 1 value_input edge, owner=user transfer (root).
  - No cycle in either tree or across the difficulty.
- Computations: every computation has a self-sufficient baseline and 4–6 factors (4 / 6 / 4 / 5 / 5), each with ≥ 2 parameter and 1 method. Each task has a multi-source factor and a card cross-difficulty factor with seeded rows. Every ladder has ≥ 3 distinct tiers stated in its rule, every fall-through equals its baseline, every factor bears weight on its task's world, and each all-baseline figure differs from gold.
- Instantiation gates on the final form: /tmp/erl0077_coord/snap_worker_early_wage_access_r5.txt (coordinator snapshot script run by this auditor) — EXTENDED, TASK TOOL CONTRACT, REPLAY --check, SOLVABILITY, COMPUTE, GROUNDING, SCOPE all OK. check_traceability not run, per brief.
- Remaining observations (no RED): task 1's unreviewed paydays 09-04 … 10-02 are producible under the catch-up sentence; the bank and instant amounts each wait on only the review schedule their record test selects.

VERDICT revision_5: task0=PASS task1=PASS charter=CLEAN

## revision_6

## charter_global_frozen (revision_6)
- Written 2026-10-23T05:48Z. Worklog precondition "REWORK round 6: gates 7/7 green" confirmed; claims read by item id only. Snapshot /tmp/erl0077_coord/snap_worker_early_wage_access_r6.txt (run by this auditor): 7/7 OK. Views r6/0 21328d23fa34758f… and r6/1 87187a5102f1f4f5… are identical to r5. access.extended.yaml 2f274ae934f522c0… is unchanged from revision_5, so every charter-only section is carried forward by reference to revision_5 on that hash. task_tools.py changed (97579e29237700de…), so action_binding_and_uuids is re-derived below. Scope of this round: renderer source findings F1 and F2 of audits/render_source/worker_early_wage_access/render_r1.md, plus the XF D-class sweep over every tool.

### action_binding_and_uuids (revision_6, re-derived over every tool body and docstring)
- Renderer F1 (missed-recovery enum): the docstring now reads "\"Paystride Access Premier Plus\" in no situation, since this review never lands above the tier one below the tier held (a plan already on Paystride Access Starter stays on it), and the value is refused with an error". This matches the rule ("never higher than one tier below its current tier"; "never goes below Paystride Access Starter") and the compute pd_one = MX(1, pd_cur − 1), including the Starter case. The body refuses Premier Plus as the docstring says. CLOSED.
- Renderer F2 (bank-fee transfer type): the body now refuses a related transfer whose delivery_speed is not next_business_day or whose destination_type is not bank_account ("… no fee booked"), as the docstring and the related_entry_id argument now state. fee_type next_business_day_fee can no longer land on another kind of transfer. CLOSED.
- D-class sweep, all five tools:
  - Every docstring claim is enforced or produced by its body: positive amounts rounded half up (exact Decimal); daily_sequence a whole number ≥ 1, booleans and fractions refused; level_effective_date a real calendar date (month lengths, leap years); the tier enum; plan existence; transfer existence and type; the fields copied from the transfer.
  - Effects: the entries are booked undelivered ("for delivery" / "shows as not yet delivered"), and the instant destination is the worker's external debit card, without any "on file" claim.
  - Return sentences carry exactly the fields they promise.
  - No example values, no composite arguments, no ordering words, no other tool's name.
  - No forbidden import or call; the date check is a pure static helper.
  - Every write tool calls ctx.create / ctx.update in its own body. Names, signatures and uuid8s are unchanged and independent.
- Prerequisite judging (SOURCE-CHAIN check): no body reads a review state, a transfer limit, a shortfall or a fee figure. The new refusals check only the argument's own type and range: transfer kind, calendar validity, and the one enum value the docstring rules out.
- Observation: the missed-recovery tool's refusal of Premier Plus is a policy outcome that the docstring and rule both already publish, so it adds no information beyond the policy surface. The module header "No tool judges a policy condition" is now slightly broader than this one refusal.

### findings (revision_6)
- Renderer F1, F2: closed. No new defect.
- Re-sweep of every class raised in revisions 1–6 across the whole charter: the charter is unchanged from revision_5 (CLEAN on that hash), and the D class over the new tool module has no member.

VERDICT revision_6: task0=PASS task1=PASS charter=CLEAN

## revision_7

## charter_global_frozen (revision_7)
- Written 2026-10-23T06:26Z. Worklog precondition "REWORK round 7: gates 7/7 green" confirmed; claims read by item id only. Snapshot /tmp/erl0077_coord/snap_worker_early_wage_access_r7.txt (run by this auditor): 7/7 OK. Views r7/0 and r7/1 are identical to r5/r6. task_tools.py 97579e29… is unchanged from revision_6. access.extended.yaml changed (c18ed891ad0850fc…), so the charter-global checks are re-derived.
- Scope: KB-audit source item S1 (audits/policy_kb/worker_early_wage_access/_difficulty.md, "Source-side items"), plus a whole-charter class re-sweep.

### re-derived checks (revision_7)
- What changed (sentence diff against revision_5/6):
  - tier review: a new assembly sentence, a split recovery-count fall-through, and a matching edit to rv_count and the factor's ladder and baseline;
  - missed-recovery review: a new assembly sentence, added to its baseline.rule;
  - other three policies: unchanged.
- rv_count is numerically identical to before on every input: the old "0 if shortfalls ≥ 1 else paydays" now reads "paydays if no shortfall else 0" as the last branches.
- Sweep: compute_basis verbatim in the rule, every binding has a basis, overwrites verbatim on both sides, baseline.rule and prerequisite sentences verbatim — 0 misses.
- S1: baseline.rule of the tier review now carries "Each allowance below names the highest tier it permits; an allowance permits only Paystride Access Starter unless one of its own tiers names a higher tier for the plan, so the next tier is never within an allowance by default; a move up is by one tier and never more."
  - A reader with the computation document alone gets a definite answer: no allowance document, so no upgrade, so the plan keeps its current tier (task 0: Plus, not gold).
  - Each allowance factor's declared baseline ('1', only Starter) is now stated on the visible surface.
  - recovery_count_method's fall-through ("otherwise … count = zero: only Paystride Access Starter") equals its baseline '1'.
  - The missed-recovery schedule states the same default for protections in its baseline.rule.
  - S1 is closed.
- Fall-through equals baseline (re-checked on all 24 factors): holds.

### findings (revision_7)
**R7a SOURCE-FACTOR RED — two tiers of recovery_count_method select the same method (F2 class "no two tiers select the same value or method"; XF A6).**
- Evidence: ladder tier 1 is "at least one shortfall … every one of them carries reason_code deduction_not_taken → count = the paydays whose period close carries a pay_date in the last twelve months". Ladder tier 3 (new) is "no shortfall with a pay_date in the last twelve months stands → count = those paydays". The rule has the same pair: "the count is the number of those paydays, a deduction the employer did not take never counting against the worker" and "when no such shortfall stands, the count is the number of those paydays".
- Both tiers compute rv_count = rv_paydays_12m: the same combination of the same windowed count, with no added input or operation. They are one tier written as two, so the ladder's distinct methods are three, not four.
- Consequence: an A6 all-pairs table fails on the pair (tier 1, tier 3). The tier distinction a renderer must publish (every deduction-not-taken shortfall vs no shortfall) selects no different treatment.
- Bears on task 0 (its world takes tier 1). No scored value changes, and the factor still bears weight (baseline → Plus).
- Artifact: access_ext_tier_review.factors[recovery_count_method].ladder and the rule's recovery-count sentence. New in revision_7, introduced by the S1 rework.

Re-sweep of every class raised in revisions 1–7, whole charter:
- P1 / P2 / R3 / R4a / P3 / N1 / P4 / F1 / F3 / F5 / N2 / N2r / T1-F4 / D-class: none.
- F2 class (duplicate or collapsed tiers): R7a only. All 24 ladders were listed: every other ladder's tier values or methods are pairwise distinct, and the missed-recovery "one below / two below / Starter" ladders collapse only on low tiers, which is world-dependent.

VERDICT revision_7: task0=RED task1=PASS charter=R7a

## revision_8

## charter_global_frozen (revision_8)
- Written 2026-10-23T06:32Z. Worklog precondition "REWORK round 8: gates 7/7 green" confirmed; claims read by item id only. Snapshot /tmp/erl0077_coord/snap_worker_early_wage_access_r8.txt (run by this auditor): 7/7 OK. Views r8/0 and r8/1 are identical to r5–r7. task_tools.py 97579e29… is unchanged. access.extended.yaml changed (f005632dfe376ba9…), so the charter-global checks are re-derived.

### re-derived checks (revision_8)
- What changed (sentence diff against revision_7): only the tier review's recovery-count sentence (and its compute_basis quote), rv_count, and the recovery_count_method ladder. The other four policies are byte-identical, and the tier review's baseline.rule is unchanged, so S1 stays closed (the allowance default sentence is still there).
- R7a: the ladder now has three tiers:
  - "no shortfall … OR every such shortfall carries reason_code deduction_not_taken → count = the paydays";
  - "≥ 1 such shortfall AND none uncarried AND at least one another reason → paydays less shortfalls";
  - "otherwise → count = zero: only Paystride Access Starter".
  The rule sentence reads the same way. rv_count = paydays if dnt-count == shortfall-count (which holds for zero shortfalls) else (paydays − shortfalls if none uncarried else 0); tier 2's "at least one / another reason" is implied by failing tier 1. A grid check over all consistent inputs shows rv_count identical to revision_7 (0 differences). The three methods are pairwise distinct: tier 2 adds the shortfall count, and tier 3 is zero on a domain where the others are not. The fall-through (count 0 → Starter) equals the baseline '1'. R7a closed.
- Sweep: compute_basis verbatim in the rule, every binding has a basis, overwrites verbatim on both sides, baseline.rule and prerequisite sentences verbatim — 0 misses.

### findings (revision_8)
Closed from revision_7: R7a. S1 stays closed.

Re-sweep of every class raised in revisions 1–8, whole charter:
- P1 / P2 / R3 / R4a / P3 / N1 / P4 / F1 / F3 / F5 / N2 / N2r / T1-F4 / D-class / S1: none.
- F2 / R7a duplicate tiers: none. All 24 ladders' tier values and methods are pairwise distinct.

VERDICT revision_8: task0=PASS task1=PASS charter=CLEAN
