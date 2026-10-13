# Policy-task audit — capital_credit_retirements / charter-global

## charter_global_frozen

- Auditor: independent policy-task auditor (erl-task-policy-audit), revision 1. I did not write any of the audited artifacts.
- Frozen: 2026-10-06T18:32Z (sha256 of this file recorded at 18:32:04Z). Written before any task's GT was revealed. Nothing in this section comes from `tasks/*.json` GT fields or `worklog.md`.
- Freeze hashes (re-verified with sha256sum, and equal to `/tmp/orch43/views/capital_credit_retirements/HASHES.txt`):
  - `tasks/capital_credit_retirements/capital.extended.yaml` sha256=31d37e5b99b005fd1aef9f845ba425190e987000454130f28a661b66ed10edcd
  - `tasks/capital_credit_retirements/task_tools.py` sha256=a55b376a5b39b5f0b56341a803aa7c9caf2e4684b86be3c28ee8785efdf0cede
- Fields I was allowed to read: `blueprint/blueprint.yaml`, `blueprint/db_schema.json`, `blueprint/share_tools.py`, `blueprint/products/capital.yaml`, the whole extended charter, `task_tools.py`, the masked views (`frozen_time`, `user_scenario`, `initial_state` only), and the DSL evaluator `skills/erl-task-instantiate/scripts/check_compute.py` (`build_env`, read to learn the semantics of `LATEST`, `CFIELD`, `SUM`, `RND`, `MONTHS` and `DAYS`).
- Fields masked and not read before the freeze: `evaluation_criteria`, `computations`, `charter_scope`, `required_documents`, `design_rationale`, `solvability_contract`, `prerequisite_closure`, `tasks/capital_credit_retirements/worklog.md`, and `env/env_0043_rural_electric_cooperative/worklog.md`.
- Entry conditions (Step 0): the gate snapshot `/tmp/orch43/snap_capital_credit_retirements.txt` shows EXTENDED, TASK-TOOL-CONTRACT, REPLAY, SOLVABILITY, COMPUTE, GROUNDING and SCOPE all OK, and CACHE-DIFF as informational. The masked views and their hashes were supplied. Per the brief, check_traceability is deferred until the KB is published. The inputs are complete.
- Base copy: lines 1-925 of `capital.extended.yaml` are byte-identical to `blueprint/products/capital.yaml` (`diff` prints nothing).

### policy_conflict_scan

There are five extended policies, and every one has category `capital`:

| policy | trigger | subject | target_tool (owner) | computes |
| --- | --- | --- | --- | --- |
| capital_ext_early_retirement_booking | state_due | special_retirement, payable_accrual | book_early_retirement_114ff464 (agent) | payable_amount |
| capital_ext_early_passthrough_election | on_request | special_retirement, payable_accrual | elect_passthrough_early_retirement_2ee4171d (user) | payable_amount |
| capital_ext_estate_later_allocation | state_due | special_retirement, payable_accrual | book_estate_later_allocation_bc10e318 (agent) | payable_amount |
| capital_ext_estate_passthrough_election | on_request | special_retirement, payable_accrual | elect_estate_passthrough_retirement_e31dc75a (user) | payable_amount |
| capital_ext_check_replacement | on_request | disbursement | reissue_capital_check_624c80d7 (agent) | check_amount |

- **Overlapping subjects.** Four policies write `capital_special_retirement` and `capital_payable_accrual`. The kind of row keeps them apart, so their triggers never meet on the same row: (distribution_margin vs gt_allocation) × (discounted_early under an approved discounted early request on an inactive account vs estate under an approved estate request on a deceased member's account, for allocations booked after the approval). The early pair needs a `request_type=discounted_early_retirement`, `board_approved` request (base `capital_evt_early_retirement`: "a former member whose capital account is inactive"). The estate pair needs an approved `estate_retirement` request and an allocation booked after `board_approval_date`. No row satisfies both.
- **Eligibility and time anchors.** The extended policies inherit everything in base that no overwrite names: the early window, minimum amount and inactivity months; the estate death certificate, claim window, documents and board cycle. No extended rule weakens any of them. The clocks are frozen_time (retirement year, months elapsed, months gone, wait days, approval age, months held) and record dates (submitted/approval dates, allocation entry_date, void entry_date). They do not conflict.
- **Shared quantity across policies.** `estate_annual_cap` is read by both estate policies (`cap_room` sums every estate special retirement in the retirement year), and no order is declared between the two. Where the cap binds, booking one row first shrinks the other row's gross, so two orders give two terminal states. This is a latent conflict. It has a consequence only in a world where the cap binds (see the findings, O-3).
- **Terminal states.** Every write raises `payable_balance` or lowers it by check+fee. The check policy reads `payable_balance` after the retirement writes, and its two declared edges order that. Nothing else reads another policy's output, apart from the early pair through `rows_booked`, which is the declared edge.
- **Cross-category read boundaries.** The four retirement policies declare `service` history (`final_date`, `status`) and read it through `CFIELD('service','final_date',status='final_billed')`. The check policy declares `cross_category: []` and reads none. The declarations match the compute.
- **Scope exclusivity and completeness.** The worlds show two disjoint scopes: task 0 holds an inactive former member with an approved discounted early request (the early pair), and task 1 holds a deceased member's estate_claim_pending account (the estate pair plus check replacement). Together they cover all five extended policies, and neither world can trigger the other scope's policies (task 0 has no deceased_date; task 1 has no discounted_early request). I confirm the declared `charter_scope` against this in each task file's comparison. Observation O-6: the claimed event types `capital_estate_claim`, `capital_estate_withdraw`, `capital_check_void` and `capital_donation_election` are the subject of no extended policy and are exercised by no task's write.

### rule_compute_equivalence

My script (`/tmp/audit43cc/vq.py`, now deleted) checked these mechanically: every `compute_basis` quotation is a verbatim substring of its policy's whitespace-normalised `rule`; every `baseline.rule` sentence is in the `rule`; every overwrite `replaced_by` is in the `rule`. All true for all five policies. Bindings with no basis key are helpers or type conversions only: `allocation_year` (int of `year_text`), `months_since_2000` (date helper for `retirement_year` / `months_elapsed`), and `rate` (= base_rate + rate_adjust, the "adjusted rate" of the rule).

Sentence-by-sentence sweep:

- **Ladders.** Every factor ladder tier is a sentence of the rule and a branch of its `decides` binding, and every branch is a tier the rule states. The tier conditions, values and methods in the rule prose match `compute` one for one, including the boundaries "at least", "fewer than", "no more than" and "more than", and the fall-through.
- **E-1 (observation): row selector.** All four retirement policies pick the row with `year_text = LATEST('capital_ledger','allocation_year',date_field='entry_date', event_type='capital_allocation', allocation_source=…)`, which is the most recently booked allocation of that source. The rules state a per-row treatment: early DM "every distribution-margin allocation of the account that the general retirement resolution of the same year does not retire"; estate DM "A distribution-margin allocation booked … after the estate's retirement was approved"; and the passthrough pair "one election entry for each … allocation". On an account with two or more covered rows, compute would return the latest row's figures whichever row is booked. It does not filter on "not retired by the same-year resolution" or "booked after approval". In both task worlds exactly one row of each source is covered, and it is the latest, so this changes nothing here. It is recorded as an observation.
- **E-2 (observation): "last final-billed".** The rules say "the member's last final-billed service account". `CFIELD` returns `hs[0]`, the first matching `service_accounts` row in seed order (check_compute.py `CFIELD`), not the one with the latest final_date. Each task world seeds exactly one final_billed service account, so there is no consequence here.
- **E-3 (observation): rounding mode.** The rules say "rounded half up to the cent". `RND` is Python `round` (banker's rounding on binary floats). None of the raw values I computed in either world lands on a half-cent tie (see the task files), so there is no consequence.
- **Date semantics.** `MONTHS` counts full calendar months with a day-of-month adjustment, which matches the counting rule "full calendar months". `DAYS` is a plain day difference, which matches "the calendar days from … to …". The estate rate ladder compares `last_final_date >= year_text` as strings; this correctly implements "final billed in the allocation's own year or later" for ISO dates against a 4-digit year.
- No compute binding invents a basis beyond E-1. No rule sentence goes unimplemented. The check policy's "names the most recently voided check of the chain … and carries that payout's retirement year" is honoured by the tool body, which takes `retirement_cycle` from `original_entry_id`.

### action_binding_and_uuids

- **Uniqueness.** Each `(target_tool, computes)` pair is claimed by exactly one policy (see the table above). No base policy names a target tool.
- **Tool bodies** (`task_tools.py`). Every tool takes only identifiers and agent-supplied amounts. None reads a status, approval, prerequisite or eligibility, and none returns an error or hint. All five write unconditionally: they create ledger rows and update balances. The module docstring says: "no tool checks eligibility, status, approval, ordering or amounts".
- **Docstrings** name no other tool and carry no sequence word. The only temporal words are "on a date later than the board approval of the estate's retirement" (`book_estate_later_allocation_bc10e318`, `elect_estate_passthrough_retirement_e31dc75a`), which describe the business object, not a tool order.
- **uuid8s.** `114ff464`, `2ee4171d`, `bc10e318`, `e31dc75a`, `624c80d7`. These are pairwise distinct, share no prefix or suffix, are not sequential, and none is reused. PASS.
- **Observation O-5.** `reissue_capital_check_624c80d7` never sets `capital_request_id` on the new payout, although the base event field list says it is "The request paid, for estate and early retirements and reissues". No policy quantity reads it, so there is no scored consequence.

### prerequisite_graph

- `prerequisite` is filled in on all five policies. It is `[]` on early_booking, estate_later and estate_passthrough.
- Edges:
  1. `capital_ext_early_passthrough_election → capital_ext_early_retirement_booking`: kind value_input, gate `rows_booked` (exists in compute), form state, resolved_by `book_early_retirement_114ff464` (= the target_tool of the depended-on policy).
  2. `capital_ext_check_replacement → capital_ext_estate_later_allocation`: value_input, gate `carried` (exists; it reads `owed = F('payable_balance')`), form state, resolved_by `book_estate_later_allocation_bc10e318`.
  3. `capital_ext_check_replacement → capital_ext_estate_passthrough_election`: value_input, gate `carried`, form action with `fallback_reason`, resolved_by `elect_estate_passthrough_retirement_e31dc75a`.
- Every `problem` is an extended policy id, none is self-referencing, and none is a base id. The graph is two disjoint stars and is acyclic.
- Every `policy_source` is verbatim in its own policy's `rule` (script check: True ×3). `fallback_reason` is present exactly on the action edge.
- `effect` claims hold against the tool bodies. Booking the DM row creates a `capital_payable_accrual` with `retirement_type=discounted_early` and the request id, so `rows_booked` becomes 1 and `request_fee` becomes 0. Each estate write raises `payable_balance`, so `carried` (estate tier = `owed`) rises.
- `condition` strength:
  - Edge 1 matches its sentence.
  - Edge 2's condition says "capital_payable_accrual entry with retirement_type estate", while the sentence says "a payable entry". That is a slight narrowing, but on an estate_claim_pending account the only payable a later DM allocation can receive is the estate one (see edge 2 below). Observation O-4, no consequence.
  - Edge 3 matches.
- No authoring-viewpoint phrasing appears in any `prerequisite` field.

### prerequisite_sentences

- **Edge 1.** "A pass-through row elected under an approved discounted early retirement has its payable fixed only after the account carries the payable entry for the distribution-margin allocation that the request covers."
  - Four-point test:
    1. The connective "only after" joins this policy's result (the payable) to what it waits on.
    2. What it waits on is a record-visible state: the account's ledger carries the payable entry of the covered DM allocation. It names no action, performer or tool.
    3. It names no tool, policy id, snake_case token or row id.
    4. Its strength matches the condition (the one covered DM row's payable entry under the request).
  - Exactly one write of this difficulty brings it about: `book_early_retirement_114ff464` is the only write that creates a DM payable entry under a discounted early request. The estate DM write creates an estate-request entry on a deceased member's account, which is not "the request" here.
  - Derivation: the sentence names the state, and the records show no discounted_early payable entry. The early_booking rule ("Each covered row is booked as one special retirement entry … together with one payable entry for its payable") is the policy whose write leaves that entry. That gives one reading.
  - The depended-on rule does not restate the sentence. PASS.
- **Edge 2.** "A replacement check for an estate is fixed only after the account carries a payable entry for every distribution-margin allocation booked to it after the estate's board approval."
  - Four-point test: the connective is "only after"; the state is record-visible (payable entries for the DM allocations booked after `board_approval_date`); no tool, id or token; strength "every", which matches the condition's "Every … entry".
  - Candidate writes: `book_estate_later_allocation_bc10e318` (estate). `book_early_retirement_114ff464` also leaves DM payable entries, but its policy applies only to "a former member whose capital account is inactive" under a board-approved discounted early request (base `capital_evt_early_retirement` plus the extended booking). It cannot apply to a deceased member's estate_claim_pending account. So exactly one write of this difficulty can bring the state about.
  - Derivation: sentence → records (DM allocation entry_date > board_approval_date, no payable entry) → estate_later rule ("A distribution-margin allocation booked to a deceased member's capital account after the estate's retirement was approved is retired for the estate under the same approved request … one payable entry for its payable") → the resolving write. That gives one reading. PASS.
- **Edge 3** (action form). "A replacement check for an estate is not issued until the claimant has made the election on every pass-through allocation booked to the account after the estate's board approval."
  - The connective is "not until". The action, the claimant's election, is in plain business words. No tool, id or token. The strength is "every".
  - Fallback test: an election leaves a payable entry, but a decline leaves no record at all (the estate_passthrough rule: "a pass-through allocation the claimant does not elect stays in the general rotation"). So no record-visible state separates "decided: declined" from "never asked", and the fallback is justified.
  - Derivation: sentence → records (gt_allocation entry booked after approval, no election) → estate_passthrough rule (the claimant's own election, one entry per allocation) → hand over the user-owned election. That gives one reading. PASS.
- **Other ordering statements.** No rule states any other cross-problem order. The early_booking rule's "a wholesale-supplier pass-through allocation is retired early only on the member's own election and never as part of this booking" sets a scope boundary, not an order. The passthrough rule's fee clause "so an elected row carries it only when no payable entry of that request stands on the account yet" sits in the blocked rule and is consistent with edge 1. No base sentence grounds any edge.
- No depended-on rule names the check or the passthrough row, and the docstrings are silent about sequence.

### override_declarations

Findings only. The per-task files demonstrate (or rule out) the consequences.

- **capital_ext_early_retirement_booking / capital_ext_early_passthrough_election** against base `capital_evt_early_retirement`:
  - S1 "may ask for all of the account's unretired credits to be retired early at a discount": followed (DM by booking, GT by election; both together retire all).
  - S2 and S3 (12 full months inactive, counting rule): inherited.
  - S4 (window 09-01..10-31, minimum 100, approved with that year's resolution, rows typed discounted_early): inherited and followed.
  - S5 "Each row's payable is discounted exactly as an estate row is, but at early_retirement_discount_rate_pct.": superseded and declared in both policies. All the factor sentences (rate ladders, filing lead, horizon, compounding, full-value share, refiling fee) act on the quantity this sentence governed, and the declared replacement plus the rule are the whole extended treatment.
  - S6 "The request covers the whole account; a partial early retirement is never made.": superseded and declared in both.
  - S7 (dissolution): inherited.
  - Against `capital_evt_general_retirement`: "Where gt_retired_only_when_received is true, gt_allocation rows are retired only for years up to … gt_retired_through_year" governs general retirements only, so there is no conflict with an elected special retirement. "Each allocation year and source retired is its own row, rounded to the cent": followed.
  - Observation: the tool records `discount_amount = gross − payable`, so a refiling fee is booked inside "discount". The base field meaning ("Present-value discount kept by the cooperative") does not cover a fee. It is not scored.
- **capital_ext_estate_later_allocation** against base `capital_evt_estate_retirement`:
  - Followed or inherited: eligibility (allowed, individual/joint, authority), death certificate, joint, 36-month window and counting, documents, small-estate limit, board cycle, cap ("up to estate_annual_cap" restated).
  - The discount sentence is superseded and declared.
  - "On approval every unretired allocation … is retired": not touched. The later allocation did not exist at approval, so the extended rule adds rows and contradicts nothing.
  - Offset/payout sentence: not this policy's quantity.
- **capital_ext_estate_passthrough_election** against base `capital_evt_estate_retirement`: two clauses superseded and declared.
  - Observation O-2: the first superseded clause is the whole sentence "On approval every unretired allocation of every capital account of the deceased member is retired …, up to estate_annual_cap …, oldest allocation years first". Its `replaced_by` covers only pass-through allocations booked after approval. Read literally, the merged charter therefore loses the base statement that governs the at-approval retirement of every other row. The same base discount sentence is also superseded twice, by estate_later and by estate_passthrough, each replacement scoped to its own row kind. Neither has a scored consequence in this difficulty, because the at-approval retirement is history in task 1's seed. Recorded as an observation.
- **capital_ext_check_replacement** against `capital_agg_member_payout`, `capital_evt_checks`, `capital_evt_estate_retirement` and `capital_evt_donation`:
  - "Payouts are assembled per member, not per capital account.": superseded and declared.
  - "when offset_unpaid_balances is true it is first applied to the member's unpaid final-billed balances …": **not** superseded and not restated. The estate tier "carries the whole retired amount owed on the account" with no offset step. On a world where the deceased member has a positive final-billed balance, base (inherited) offsets first and extended carries the whole owed, so the two answers differ. Observation O-1: both task worlds seed `account_balance: 0.0` on the final_billed service account, so the consequence cannot be shown here.
  - Minimum check, check method for an estate, and active-account no-offset: inherited and followed.
  - `capital_evt_checks`: the reissue-fee sentence is superseded and declared. Void any time, void once, reissue to the address on file with `original_entry_id` = the voided payout, and escheat: inherited and followed. The mailing and records charges are new deductions on the quantity whose fee sentence was superseded.
  - `capital_evt_donation`: estate donation needs the claimant's election, and backup withholding applies only without a TIN. Inherited (see the task files for the TIN evidence).
- I found no anonymous intermediate factor, no 0/1 multiplier on a base-fixed quantity and no dropped base branch. None of the authors' text calls the base output a "wrong value".

### factor_ladders

| policy | factor | label | decides | tiers | multi-source tier(s) | cross_difficulty |
| --- | --- | --- | --- | --- | --- | --- |
| early_booking | early_rate_by_departure_and_patronage | parameter | base_rate | 3 (8.5 / 6.5 / fall-through 7.5) | both non-fall-through tiers: service final_date ∧ capital_ledger DM allocation count | service |
| early_booking | early_rate_filing_lead | parameter | rate_adjust | 3 (−0.25 / +0.5 / 0) | no | – |
| early_booking | early_horizon_count | method | horizon | 3 (fractional whole−months/12 / zero / whole) | no | – |
| early_booking | early_compounding_by_row_size | method | pv_factor | 3 (monthly / semiannual / annual) | no | – |
| early_booking | early_percentage_year_credit | parameter | full_value_share | 3 (0.25 / 0.10 / 0) | no | – |
| early_booking | early_refiling_fee | parameter | refiling_fee | 3 (10 / 5 / 0) | no | – |
| early_passthrough | passthrough_expected_rotation | parameter | rotation | 3 (0 / 27 / fall-through 22) | tier 2 disjunction (gap ≥15 ∨ no GT general retirement) | – |
| early_passthrough | passthrough_rate_by_departure_and_patronage | parameter | rate | 3 (9.0 / 7.0 / 7.5) | yes (service ∧ GT allocation count) | service |
| early_passthrough | passthrough_horizon_count | method | horizon | 3 | no | – |
| early_passthrough | passthrough_compounding_by_row_size | method | pv_factor | 3 | no | – |
| estate_later | estate_rate_by_patronage | parameter | base_rate | 3 (5.0 / 7.5 / 5.75) | yes (service final_date ∧ capital account opened_date) | service |
| estate_later | estate_rate_wait_adjustment | parameter | rate_adjust | 3 (−0.25 / +0.5 / 0) | no | – |
| estate_later | estate_horizon_transform | method | horizon | 3 (cap 20 / zero / whole) | no | – |
| estate_later | estate_compounding_by_row_size | method | pv_factor | 3 (monthly / semiannual / annual; limits 100 / 1000) | no | – |
| estate_later | estate_recent_approval_credit | parameter | full_value_share | 3 (0.2 / 0.1 / 0) | no | – |
| estate_passthrough | estate_passthrough_expected_rotation | parameter | rotation | 3 (0 / 27 / 22) | tier 2 disjunction | – |
| estate_passthrough | estate_passthrough_rate_by_patronage | parameter | base_rate | 3 (5.0 / 7.5 / 5.75) | yes | service |
| estate_passthrough | estate_passthrough_wait_adjustment | parameter | rate_adjust | 3 | no | – |
| estate_passthrough | estate_passthrough_horizon_transform | method | horizon | 3 (cap 25 / zero / whole) | no | – |
| estate_passthrough | estate_passthrough_compounding_by_row_size | method | pv_factor | 3 | no | – |
| estate_passthrough | estate_passthrough_prior_election_credit | parameter | full_value_share | 3 (0.25 / 0.10 / 0) | no | – |
| check_replacement | replacement_base_by_account_status | method | carried | 3 (whole owed / void+rest-if-small / void) | tier 2 (status ∧ rest below minimum) | – |
| check_replacement | replacement_fee_by_voids | parameter | replacement_fee | 3 (25 / 15 / 0) | no | – |
| check_replacement | replacement_mailing_charge | parameter | mailing_charge | 3 (6.95 / 3.50 / 0) | tier 2 (lost ∧ returns < 2) | – |
| check_replacement | replacement_records_charge | parameter | records_charge | 3 (5.00 / 2.50 / 0) | no | – |

- **Counts per policy** (bound 4–6, ≥2 parameter, ≥1 method):

  | policy | factors | parameter | method |
  | --- | --- | --- | --- |
  | early_booking | 6 | 4 | 2 |
  | early_passthrough | 4 | 2 | 2 |
  | estate_later | 5 | 3 | 2 |
  | estate_passthrough | 6 | 4 | 2 |
  | check_replacement | 4 | 3 | 1 |

  All within bounds. Per task, by the declared scopes:
  - task 0 (early pair): multi-source `early_rate_by_departure_and_patronage`; cross_difficulty `service` ×2.
  - task 1 (estate pair + check): multi-source `estate_rate_by_patronage`; cross_difficulty `service` ×2.

  Both meet the per-task minimum.
- **Ladder structure.**
  - Binding sets are pairwise disjoint within each policy, and every `decides` is an input, not `result`.
  - All ladders have three pairwise-disjoint tiers, and no two tiers of a ladder select the same value or method. Every tier is stated in the rule, with condition and value or method, and implemented in compute.
  - Every fall-through equals the policy's baseline for that input: `P('early_retirement_discount_rate_pct')`, `0`, `whole_years`, the annual `(1+rate/100)**(-horizon)`, `P('estate_expected_rotation_years')`, `P('estate_discount_rate_pct')`, and `void_amount`.
  - Each baseline rule is a complete, self-contained method using the declared default keys. One exception: the early passthrough baseline's "less the request's refiling fee where it is still owed" points to the fee sentence for the fee amounts, and lists `refile_fee` and `repeat_refile_fee` in `baseline.params`. This is acceptable, because the fee is part of the baseline rather than a factor.
- **Label honesty.**
  - Compounding factors change the algorithm (compounding frequency): method is honest.
  - Horizon factors change how the horizon is counted (fractional years, a cap, or none): method is acceptable.
  - `replacement_base_by_account_status` changes which quantity the face is built from (whole owed / conditional sum / void only): method is honest.
  - All parameter labels select numbers.
  - Every method tier names a computation stated in the charter's own rule.
- **Realism.** These ladders are synthetic business treatments, but each condition is a quantity a cooperative's capital credit desk could plausibly weigh: tenure, departure age, filing timing, row size, prior partial retirement, refiling history, void history, mail returns, holding time. No condition holds for every customer reaching its write. Each tier is reachable, with the exception noted under O-7.
  - O-7: in both passthrough rotation ladders, tier 1 ("a pass-through year no later than the latest pass-through year the general retirements on the account have reached … expected in zero years") cannot be reached by a row with positive gross. Base `capital_evt_general_retirement` retires gt_allocation rows "only for years up to and including the resolution's gt_retired_through_year, in full", so any GT year at or below the latest year reached has already been retired in full. The ladder keeps three distinct outcomes, but only two are live. Neither task's world takes or needs tier 1, so this is recorded as an observation.
  - O-8: weaker realism. Three tiers pay part of a row at full value for reasons unrelated to time value: `estate_recent_approval_credit`, `estate_passthrough_prior_election_credit` (whose rule premise "A claimant who already elected the estate's earlier pass-through allocations" misdescribes base, under which the earlier GT rows are retired automatically on approval; the operative tiers count entries, so the premise does not change the count), and `early_percentage_year_credit`. `replacement_records_charge` charges for the time a returned check's money sat. These are unusual but internally coherent published treatments. I cannot demonstrate that no business in the line would publish them, so they are observations.

### findings

No charter-global SOURCE-POLICY RED: no finding has a consequence demonstrable in either task world. The observations, each naming the tasks it bears on:

- **O-1** (task 1). The check policy's estate tier carries the whole owed without the inherited base offset against unpaid final-billed balances, which it neither superseded nor restated. This is latent: task 1 seeds `account_balance: 0.0`, and task 1's file confirms that there is no consequence.
- **O-2** (task 1). The estate_passthrough overwrite supersedes the whole base "On approval every unretired allocation …" sentence with a replacement scoped to later GT rows only. The base discount sentence is superseded by two policies with differently scoped replacements. No scored consequence.
- **O-3** (task 1). The two estate policies share `estate_annual_cap` (`cap_room`) with no declared order between them. Two orders give two terminal states only where the cap binds. Task 1's file shows that the cap room is ample.
- **O-4** (task 1). Edge 2's condition is narrower ("retirement_type estate") than its sentence ("a payable entry"). They are equivalent on an estate account.
- **O-5** (task 1). The reissue tool never records `capital_request_id`. Not scored.
- **O-6** (both). The claimed event types capital_estate_claim, capital_estate_withdraw, capital_check_void and capital_donation_election have no extended policy and no write in either task.
- **O-7** (both). Tier 1 of both passthrough rotation ladders is unreachable with positive gross.
- **O-8** (both). Realism doubts about the full-value-share credits and the records charge.
- **E-1 / E-2 / E-3** (both). The latest-row selector, the `CFIELD` first-match, and the `RND` rounding differ from rule wording in situations neither world exercises. Each task file confirms that there is no consequence there.

## closing_checklist

Written 2026-10-06, after both tasks were revealed and compared. Nothing above this heading was edited after the reveal.

- **Audit files.** Each task has its own audit file: `0.md` ↔ `tasks/0.json` and `1.md` ↔ `tasks/1.json`, with `_difficulty.md` alongside them. This is revision 1, so there are no older revisions. Both comparison sections carry PASS.
- **Policy coverage and scopes.**
  - Coverage is complete. `charter_scope` of task 0 = {early_retirement_booking, early_passthrough_election}; of task 1 = {estate_later_allocation, estate_passthrough_election, check_replacement}. Their union is all five extended policies.
  - The two scopes are pairwise disjoint, and each spans its whole tree.
  - Task tools and GT are closed. Each task calls only its own scope's tools, and every tool's uuid8 is independently generated and frozen (§ action_binding_and_uuids).
- **Trees.**
  - Task 0 has 1 prerequisite problem and 1 value_input edge, and its root is owner=user.
  - Task 1 has 2 prerequisite problems and 2 value_input edges, and one of them is owner=user.
  - The difficulty-wide `prerequisite` graph is two disjoint stars, so it is acyclic and no cross-task reference exists.
- **Factors.**
  - Every computation declares a self-sufficient baseline and 4–6 factors: [6, 4] in task 0 and [5, 6, 4] in task 1. Each has at least 2 parameter and at least 1 method factor.
  - Each task has a multi-source factor and a cross-difficulty factor (service, seeded).
  - Every ladder has 3 distinct tiers stated in its rule.
  - Every factor bears weight against an honest baseline, and every whole-baseline number is definite and differs from gold: 68.89 vs 91.45, 23.46 vs 12.67, 56.24 vs 93.30, 14.79 vs 22.93, 46.09 vs 137.87.
  - The realism doubts (O-7, O-8) remain observations.
- **Gates.** I did not re-run the instantiation-stage gates myself; the brief supplied them. The orchestrator's snapshot `/tmp/orch43/snap_capital_credit_retirements.txt` (mtime 18:17:53Z) was taken after the last write to `tasks/*.json` (18:17:50Z). The charter and tool hashes at close are unchanged (31d37e5b…10edcd, a55b376a…0cede), so the snapshot is on the final form: EXTENDED, TASK-TOOL-CONTRACT, REPLAY, SOLVABILITY, COMPUTE, GROUNDING and SCOPE all OK. check_traceability is deferred until the KB is published, per the brief.
- **Difficulty verdict:** source-layer audit **PASS**. Both tasks pass all four relationships, with observations only. No artifact was edited.
