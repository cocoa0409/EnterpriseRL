# Policy-task audit — season_pass_billing_desk / charter-global

## charter_global_frozen

- Freeze time: 2026-09-17T18:41Z (pre-reveal; nothing below is derived from any revealed GT field).
- Auditor: independent policy-task auditor, invoked via `erl-task-policy-audit`, not the author of these artifacts.
- Freeze hashes (sha256, first 16 hex), taken from the coordinator's masked root
  `/tmp/claude-10250/-mnt-moonfs-wangzhaoji-m4-github-enterprise-rl/1dfabe41-064c-4be8-afd1-06653cea788e/scratchpad/masked_views_coordinator/season_pass_billing_desk/`:
  - `passes.extended.yaml` — `ff7ef832d3e4eab1`
  - `task_tools.py` — `4e47d127a1d0aa96`
  - `tasks/0.json` — `a973fbe383f02ac4`, `tasks/1.json` — `757aeeb0b223366a`
  Re-checked by the auditor with `sha256sum`; all four agree with the values in the brief.
- Fields permitted at this stage: the blueprint (`blueprint.yaml`, `products/passes.yaml`, `db_schema.json`,
  `share_tools.py`), the whole of `passes.extended.yaml` and `task_tools.py`, and each task's
  `frozen_time` / `user_scenario` / `initial_state`.
- Fields explicitly masked and not read before the per-task freezes: `evaluation_criteria`,
  `computations`, `charter_scope`, `required_documents`, `design_rationale`, `solvability_contract`,
  `prerequisite_closure`, `db_closure`, `db_closure_matches_initial_state`.
- Entry conditions (Step 0): the brief supplied the instantiation-stage gate snapshot with its commands and
  actual output lines — EXTENDED, TASK-TOOL-CONTRACT, REPLAY, SOLVABILITY, COMPUTE, GROUNDING, SCOPE all
  green; TRACEABILITY is declared not-runnable before the KB render step. The masked views were built by
  whitelist and their hashes were supplied. Entry conditions are complete; the auditor did not re-run the
  gates. A machine green light qualifies for this audit; it proves nothing below.

### policy_conflict_scan

Scope of the scan: the 16 base policies of `products/passes.yaml` (`passes_agg_multi_holding` …
`passes_season_closure`) plus the 6 extended policies of `passes.extended.yaml`
(`passes_ext_arrears_recovery`, `passes_ext_reinstatement_charge`, `passes_ext_carry_forward_fee`,
`passes_ext_credit_offset`, `passes_ext_cancellation_charge`, `passes_ext_settlement_credit`).

- **Base copy is verbatim.** `head -1812 passes.extended.yaml` is byte-identical to
  `blueprint/products/passes.yaml` (`diff` empty). `extended_policies:` begins at line 1814.
- **Subjects / target tools.** Each extended policy claims a disjoint `(target_tool, computes)` pair:
  `collect_past_due_0159c539`/`presented_amount_usd`, `restore_pass_scanning_08275b43`/`restoration_charge_usd`,
  `elect_pass_carry_forward_09e30d1a`/`carry_forward_fee_usd`, `apply_pass_credit_52fe36c9`/`credit_applied_usd`,
  `give_up_season_pass_8c1a0eca`/`retained_charge_usd`, `issue_settlement_credit_d3237287`/`settlement_credit_usd`.
  No pair is claimed twice.
- **Overlapping base subject.** `passes_ext_cancellation_charge` and `passes_ext_settlement_credit` both cite
  `base_policy_refs: [passes_cancellation_refund]` and both name the *same* base sentence
  ("Inside the window the refundable amount is worked out on the tier's refund basis: …") in their `overwrite`,
  with two different `replaced_by` texts. They compute different quantities on different subjects
  (`passes_cancel` vs `passes_credit_issue`) and the first replacement explicitly says its output "is what the
  amount coming back is reduced by", so the merged semantics compose rather than contradict. Recorded as
  observation OBS-3 below, not a conflict.
- **Eligibility, time anchors, terminal states, cross-category reads.** No two policies impose contradictory
  eligibility on the same write. Every extended computation reads `insure` only through `CFIELD`/`CPARAM`/`XSUM`
  and declares it in `cross_category`; four of the six declare an `insure` read
  (`carry_forward_fee`, `credit_offset`, `cancellation_charge`, `settlement_credit`), matching the brief's
  "cross-cat=4". No policy reads a category it has not declared.
- **Task scopes.** Task 0's problem tree is
  {`passes_ext_arrears_recovery`, `passes_ext_reinstatement_charge`, `passes_ext_carry_forward_fee`};
  task 1's is {`passes_ext_credit_offset`, `passes_ext_cancellation_charge`, `passes_ext_settlement_credit`}
  (derived from each task's root request and the `prerequisite` edges, not from any masked field).
  The two sets are pairwise disjoint and jointly cover all six extended policies.

### rule_compute_equivalence

Check 2 was run sentence by sentence over all six extended policies. Every binding carries a
`compute_basis` quotation, and every quotation is verbatim in that policy's `rule`. Two defects were found;
everything else is equivalent in both directions.

**FIND-1 (SOURCE-POLICY RED) — `passes_ext_credit_offset.pot_usd`: the ladder the rule states and the
condition `compute` tests are different conditions.**

- Rule: "Where the pass account shows credit issued **under more than one reason**, the pot is instead the sum
  of every credit entry the pass account shows issued less every application already drawn against them; and
  where the pass account shows credit issued **under one reason only**, the pot is instead the sum of the
  entries issued to put a service failure right less every application already drawn."
- Compute: `pot_usd: "credit_issued_total - credit_drawn_total if error_credit > 0 else (recovery_credit - credit_drawn_total if recovery_credit > 0 else credit_on_record)"`,
  where `error_credit = SUM(... credit_reason='duplicate_charge')` and `recovery_credit = SUM(... credit_reason='service_recovery')`.
- The two faces disagree on a whole region of worlds. A pass carrying two credit entries with reasons
  `pass_cancellation` and `protection_settlement` satisfies the rule's first tier ("more than one reason") and
  must take pot = every entry issued less every application drawn; `compute` has `error_credit == 0` and
  `recovery_credit == 0`, falls through to `credit_on_record`, and returns the record's running balance instead.
  Conversely a pass carrying exactly one entry, reason `duplicate_charge`, satisfies the rule's second tier
  ("one reason only") and must take pot = the service-failure entries less applications drawn (= 0 less the
  applications drawn, i.e. a negative pot); `compute` takes the first branch and returns every entry issued
  less applications drawn.
- Root cause: the rule's tiers are stated over the *number of distinct credit reasons* on the account, while
  `compute` tests for the *presence of two particular reasons*.
- Consequence: an agent that reads the published rule and an agent that reads the implemented binding compute
  different pots on the same records. Demonstrable on any world with two non-`duplicate_charge` reasons.
- Location: `passes.extended.yaml` `passes_ext_credit_offset` — `rule` (the two "Where the pass account shows
  credit issued …" sentences), `compute[].pot_usd`, `compute_basis.pot_usd`, `factors[id=credit_pot_basis].ladder`.
- Bears on: task 1 (which claims `passes_ext_credit_offset`). Task 1's own world is checked in `1.md`.

**FIND-2 (SOURCE-POLICY RED) — the charter's day-counting convention is contradicted by `COUNT('passes_ledger',
event_type='passes_scan')`, and no `overwrite` declares the deviation.**

- Base, inherited in full and hit by no `overwrite`: `passes_access_control.rule` — "the day is counted on the
  first scan of that date and is **not counted twice however many lifts are ridden**"; and
  `measures: passes_msr_season_scan_days` — "Count of **distinct event_date values** across passes_ledger rows
  of event_type passes_scan carrying this pass_id", which `passes_cancellation_refund` cites in its
  `measures:` and uses in its formula as `day_use_deduction_usd * passes_msr_season_scan_days`.
- Extended, in the vocabulary of days: `passes_ext_cancellation_charge.rule` — "Where the pass account shows the
  holder took at least **the number of days** the charter treats as heavy use …"; `passes_ext_settlement_credit.rule`
  — "less the tier's day use deduction **for each day** the pass account shows the holder took".
- Compute in both policies counts **rows**, not days: `days_taken: "COUNT('passes_ledger', event_type='passes_scan')"`
  and `days_taken_a` / `scan_entries` identically.
- `overwrite` in `passes_ext_cancellation_charge` names only the refund-basis sentence; `passes_ext_settlement_credit`
  names only that sentence and "The refundable amount is never below zero." Neither names the day-counting
  convention or the measure. This is an **undeclared override** of the kind check 1 calls the anonymous
  intermediate factor: no new parameter name appears, the deviation hides inside an intermediate.
- Consequence: on any pass with two scans on one date the two readings give two different, equally defensible
  figures. Demonstrated against task 1's world in `1.md` (321.70 / 302.89 vs 237.20 / 463.39).
- Location: `passes.extended.yaml` `passes_ext_cancellation_charge.compute[].days_taken` and
  `passes_ext_settlement_credit.compute[].days_taken_a` / `.scan_entries`; the two `overwrite` blocks;
  `blueprint/products/passes.yaml` `passes_access_control.rule` and `measures.passes_msr_season_scan_days`.
- Bears on: task 1.

**FIND-3 (SOURCE-POLICY RED) — `passes_ext_credit_offset.rule` makes a promise `compute` does not keep.**

- Rule, final sentence, carried verbatim into `baseline.rule` as well: "A single application is never less than
  the smallest single application the tier allows."
- `baseline.params` lists `credit_minimum_redemption_usd`, so the author names the tier parameter the sentence
  refers to.
- `compute[].result: "RND(MN(MX(0, drawn_usd - retained_usd - premium_hold_usd), balance_due), 2)"` applies a
  floor of zero and a ceiling of the balance, and nowhere reads `credit_minimum_redemption_usd`. No
  `compute_basis` entry quotes the sentence.
- Root cause: a normative sentence of the rule with no binding behind it.
- Consequence: wherever the other bindings produce a figure below the tier minimum, the rule states an outcome
  and does not say which of the two available outcomes follows — raise the application to the minimum, or make
  no application at all — so the policy entails two answers and `compute` silently entails a third. It is
  a live second reading of the published terms in every world of this policy, since a reader cannot tell
  whether the sentence bites until after they have computed.
- Location: `passes.extended.yaml` `passes_ext_credit_offset.rule` (last sentence), `baseline.rule` (last
  sentence), `baseline.params`, `compute[].result`, `compute_basis` (no entry).
- Bears on: task 1.

Also checked and clean: every quantity, window, filter, tier, branch, cross-category read, acting base,
grouping, cap/floor, rounding mode and rounding point in the other five policies has a verbatim
`compute_basis` quotation and a restricted expression; the sweep back found no binding without a rule sentence
apart from the three above.

### action_binding_and_uuids

- Each `(target_tool, computes)` pair is claimed by exactly one policy (listed under `policy_conflict_scan`).
  Subject, `base_policy_refs`, target tool, docstring and terminal state admit one business reading each.
- The eight-hex tails of the six tools are `0159c539`, `08275b43`, `09e30d1a`, `52fe36c9`, `8c1a0eca`,
  `d3237287`. No tail is reused, none is another with a changed final character, and no tail is a sequence
  number or an increment of an adjacent one. Three of six begin with the digit `0` but share no further
  prefix, which is within what independent generation produces; no violation recorded.
- **OBS-1 (observation) — a tool docstring states its action's position in a sequence.**
  `issue_settlement_credit_d3237287`'s first sentence: "Issue resort credit against a season pass record for
  what comes back to the household **after the pass has been given up**." Check 3 forbids a docstring carrying
  an ordering word such as before, after or first, or stating an action's position in a sequence. The edge
  `passes_ext_settlement_credit -> passes_ext_cancellation_charge` is the very hop the task means the agent to
  derive from the prerequisite sentence and the records; the tool layer states half of it outright. No second
  answer follows from it, so it is an observation and not a red light.
  Location: `task_tools.py`, `issue_settlement_credit_d3237287` docstring, line 1 of the summary.
  Bears on: task 1.
- No docstring names another tool. The module docstring's "No tool judges eligibility, gathers history or works
  out a policy figure" is confirmed against every function body below (`prerequisite_graph`).

### prerequisite_graph

Check 7 over the whole `prerequisite` field of the charter, verified mechanically and by reading:

| blocked policy | problem | kind | gate | form | `policy_source` verbatim in own rule | restated in depended-on rule | resolved_by |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `passes_ext_reinstatement_charge` | `passes_ext_arrears_recovery` | value_input | `expired_relief_rate` | state | yes | no | `collect_past_due_0159c539` |
| `passes_ext_carry_forward_fee` | `passes_ext_reinstatement_charge` | value_input | `standing_rate` | state | yes | no | `restore_pass_scanning_08275b43` |
| `passes_ext_cancellation_charge` | `passes_ext_credit_offset` | value_input | `outstanding_rate` | state | yes | no | `apply_pass_credit_52fe36c9` |
| `passes_ext_settlement_credit` | `passes_ext_cancellation_charge` | value_input | `retained_offset_rate` | state | yes | no | `give_up_season_pass_8c1a0eca` |

- `prerequisite` is filled in on all six policies; `passes_ext_arrears_recovery` and `passes_ext_credit_offset`
  carry `[]` and are the two leaves.
- Every `problem` points at another extended policy id in this file; none points at a base policy or at itself.
- The graph is two disjoint chains, `arrears_recovery -> reinstatement_charge -> carry_forward_fee` and
  `credit_offset -> cancellation_charge -> settlement_credit`; it is acyclic, and no cross-task reference
  creates a cycle.
- `form: state` on all four edges, so `fallback_reason` is correctly absent from all four; no action-form edge
  exists to test.
- Every `gate` names a real binding of the blocked policy's own `compute` (`expired_relief_rate`,
  `standing_rate`, `outstanding_rate`, `retained_offset_rate` all appear as `compute` keys), so `kind:
  value_input` matches `gate` in all four cases; there is no `state_gate` edge to check.
- `resolved_by` is the depended-on policy's `target_tool` in all four cases, and each genuinely changes the
  binding named in `gate`, read off the tool bodies:
  - `collect_past_due_0159c539` creates a `passes_ledger` row with `event_type="passes_installment_charge"` and
    `event_date=ctx.now()[:10]`, which moves `last_settlement_on` past `last_refusal_on` and so moves
    `expired_relief_rate` off `K('expired_relief_none')`.
  - `restore_pass_scanning_08275b43` creates `event_type="passes_fee_charge"`,
    `charge_category="reinstatement_fee"` and sets `status="active"`, which raises `service_charges_standing`
    above zero and so moves `standing_rate` off `K('standing_rate_clean')`.
  - `apply_pass_credit_52fe36c9` runs `ctx.update("passes_holdings", pass_id, …, installment_balance_usd=balance)`
    with `balance = installment_balance_usd - applied`, which lowers `outstanding_share` and so moves
    `outstanding_rate`.
  - `give_up_season_pass_8c1a0eca` creates `event_type="passes_fee_charge"`,
    `charge_category="cancellation_fee"`, which raises `retained_standing` above zero and so moves
    `retained_offset_rate` off `K('offset_none')`.
- No `condition` has been strengthened or weakened relative to the sentence it comes from (compared below).
- No authoring-viewpoint phrasing ("in this task", "at the opening", "the current world") appears anywhere in
  the four `prerequisite` blocks.
- **Tool layer judges no prerequisite.** Each of the six function bodies was read in full: every one does
  `ctx.find("passes_holdings", pass_id=pass_id)`, takes `found[0] if found else {}`, arithmetic, `ctx.create`
  and `ctx.update`, and returns a confirmation string. None reads `status` to decide anything, none compares a
  date, none raises, none returns an error branch, and none emits a hint. `restore_pass_scanning_08275b43`
  writes `status="active"` unconditionally rather than testing that it was `suspended`.

### prerequisite_sentences

Check 6, four-point test on each of the four edges. All four are verbatim sentences of the **blocked** policy's
own `rule` (verified by normalised substring match), none is restated in the depended-on policy's rule, and no
rule carries a second wording, another problem's tool name, another policy's id or an aggregated chain.

1. `passes_ext_reinstatement_charge` — "The charge for restoring scanning privileges is worked out **only after**
   the pass account carries a cleared payment entry dated later than every refusal standing against the pass."
   Ordering connective "only after"; joins this policy's own result (the restoration charge) to a
   record-visible state; the state is named in the words `find_pass_account_entries` uses ("the instalments that
   cleared and the ones the payment method refused"); no tool, policy id, snake_case token or row id; scope
   matches `condition` ("a cleared scheduled-instalment entry whose date is later than the date of the most
   recent refusal standing on that pass account") exactly. **One write brings the state about**: only
   `collect_past_due_0159c539` creates a `passes_installment_charge` row; the other five tools create
   `passes_fee_charge`, `passes_credit_redeem` or `passes_credit_issue` rows. Derivation with a single reading:
   the sentence says the charge waits on a cleared payment later than every refusal → the records show the
   latest refusal and the latest cleared instalment → `passes_ext_arrears_recovery` is the only policy whose own
   rule describes taking a presentation at the desk against a pass account that has fallen behind → its write
   is the one to make first.
2. `passes_ext_carry_forward_fee` — "The fee for carrying a pass forward is worked out **only after** the pass
   record stands in the state in which it admits the holder." Ordering connective; state form; "the state in
   which it admits the holder" is the charter's own gloss on `active`
   (`passes_access_control`: "A scan admits the holder only while the pass record stands in the active state"),
   and `find_season_passes` returns "the state the pass stands in". **One write brings it about**:
   `restore_pass_scanning_08275b43` is the only tool that sets `status="active"`; the others set `deferred`,
   `cancelled`, or no status at all. Single reading: the sentence says the fee waits on the pass standing in the
   admitting state → the record shows `suspended` → `passes_ext_reinstatement_charge` is the only policy whose
   own rule describes restoring withdrawn scanning privileges.
3. `passes_ext_cancellation_charge` — "The charge retained when a pass is given up is worked out **only after**
   the pass account carries an application of resort credit against the amount it still shows to collect."
   Ordering connective; the state is a ledger entry `find_pass_account_entries` names ("the resort credit issued
   and applied"); scope matches `condition`. **One write**: `apply_pass_credit_52fe36c9` is the only tool
   creating `passes_credit_redeem`. Single reading via `passes_ext_credit_offset`, the only policy whose rule
   describes drawing resort credit down against what the account still shows to collect.
4. `passes_ext_settlement_credit` — "The resort credit issued when a pass is given up is worked out **only
   after** the pass account carries the charge retained on the pass being given up." Ordering connective; state
   form; "the charge retained on the pass being given up" narrows to the `cancellation_fee` charge, which only
   `give_up_season_pass_8c1a0eca` writes — the two other tools that create `passes_fee_charge` rows write
   `reinstatement_fee` and `deferral_fee`, neither of which is "retained on the pass being given up". Single
   reading via `passes_ext_cancellation_charge`.

- **No undeclared cross-problem order in any rule.** A sweep for ordering connectives over every sentence of the
  six extended rules returns, besides the four sentences above, only intra-computation uses ("before a third of
  the election period has run", "refusals the tier tolerates before privileges are reviewed", "the reliefs are
  first added together", "rounded to the cent only once"). None states an order between two problems.
- **OBS-2 (observation) — a base rule sentence states a cross-problem order that parallels edge 3.**
  `passes_credit_redemption` (base, inherited): "Resort credit is applied only while the pass record it sits on
  has not reached the cancelled or closed state." This orders the credit application before the surrender. Check
  6 permits it as an observation because the blocked extended rule carries a prerequisite sentence of its own
  (edge 3 above); had it not, it would be a red light. Location: `blueprint/products/passes.yaml`,
  `passes_credit_redemption.rule` and its `credit_record_state` eligibility. Bears on: task 1.

### override_declarations

Check 1's finding half, sentence by sentence against each `base_policy_refs` entry. Conclusions per policy:

- `passes_ext_arrears_recovery` vs `passes_installment_plan`: the only base sentence it handles differently is
  the division of the financed amount into instalments, and it is named verbatim in `overwrite`. Every other
  base sentence (the financed amount's construction, the stored-payment-method condition, the charge day of
  month, the first-charge lag, the day-counting convention, the `applied/pending_activation/active` state gate,
  prepayment in reverse order) is followed or untouched. Declared and clean.
- `passes_ext_reinstatement_charge` vs `passes_arrears_suspension`: the reinstatement-fee sentence is named
  verbatim and replaced. The base sentences that survive — the arrears definition, the suspension anchor and
  counting rule, the rolling-window tolerance, "a suspended pass keeps its tier, its price and its schedule",
  "privileges are restored only when the pass account records show every refused instalment settled", "each
  restoration carries its own fee" — are all consistent with the extended reliefs, which reduce a fee rather
  than remove the settlement condition. Declared and clean. Note the base clause "that fee is not charged where
  the refusal was the collective's own error" disappears in the replacement; it sits inside the named
  superseded clause, so it is declared.
- `passes_ext_carry_forward_fee` vs `passes_deferral`: the base sentence "The tier's carry-forward fee is placed
  on the pass account when the election is recorded, and that fee is not charged where the household holds a
  protection plan standing in the active or claim_open state at the moment of the election" is named verbatim,
  which is what legalises `protection_rate_in_force = 0.5` (base: not charged at all; extended: half charged) and
  `protection_rate_settled = 0.0`. Declared. The base election period, the no-days-taken condition, the
  no-repricing clause and the protection-eligible-tier clause are inherited and not contradicted.
- `passes_ext_credit_offset` vs `passes_credit_redemption`, `overwrite: []`: judged sentence by sentence.
  "Resort credit issued against a pass record is spent, not paid out" — followed. "Resort credit is applied only
  when it is applied no later than its validity period counted in calendar days from the day the credit was
  issued" — **the extended `credit_issued_total` and `recovery_credit` bindings sum every `passes_credit_issue`
  row with no date filter at all.** Where a seeded credit entry lies outside its tier's `credit_validity_days`,
  base excludes it from what may be applied and extended's pot includes it; no `overwrite` declares this.
  Recorded as **OBS-4 (observation)**: no world in either of this difficulty's two tasks contains a credit entry
  outside its validity period (task 1's two entries are dated 2026-12-28 and 2027-01-02 against
  `credit_validity_days: 365`), so no consequence can be demonstrated and it is not a red light.
  "A single application of credit must be at least the tier's minimum" — see FIND-3. "Where several credit
  entries sit on one pass, the entry closest to running out is applied first" — inherited and not contradicted;
  it is what fixes the tool's `related_event_id` and `credit_pot` arguments uniquely.
- `passes_ext_cancellation_charge` and `passes_ext_settlement_credit` vs `passes_cancellation_refund`: the
  refund-basis sentence is named by both (see OBS-3) and "The refundable amount is never below zero" by the
  second. The base window, its anchor and counting rule, the medical-claim condition, the
  not-already-cancelled dedup and "what comes back is issued as resort credit" are inherited and followed.
  **The day-counting convention that `passes_cancellation_refund` imports through
  `measures: [passes_msr_season_scan_days]` is not named by either `overwrite` and is contradicted by both
  computes — FIND-2 above.**
- No 0/1 multiplier and no dropped branch was found in any of the six. No author note calls a base output a
  "wrong value" or an "algorithm to avoid".

### factor_ladders

Structure only; whether a factor bears weight on a world lives in each task's `factor_weight`.

| policy | factors | `parameter` | `method` | cross_difficulty | multi-source tiers present |
| --- | --- | --- | --- | --- | --- |
| `passes_ext_arrears_recovery` | 5 | 2 | 3 | — | `retry_hold_over`, `late_fee_gathering` |
| `passes_ext_reinstatement_charge` | 5 | 3 | 2 | — | `expired_card_relief`, `unused_season_relief` |
| `passes_ext_carry_forward_fee` | 6 | 5 | 1 | `protection_share` → insure | `fee_base_basis` (tier 2) |
| `passes_ext_credit_offset` | 4 | 3 | 1 | `protection_premium_hold` → insure | `schedule_stage_share`, `error_credit_hold` |
| `passes_ext_cancellation_charge` | 6 | 5 | 1 | `protection_excess_relief` → insure | none |
| `passes_ext_settlement_credit` | 6 | 4 | 2 | `protection_payout_offset` → insure | `retained_charge_offset`, `credit_uplift`, `gross_back_basis` |

- Counts are within bounds everywhere: 4 to 6 factors per policy, at least 2 `parameter` and at least 1
  `method` in each. Per task (task 0 = the first three rows less `credit_offset`; see each task file) there is
  at least one multi-source factor and at least one `cross_difficulty` factor.
- Every ladder has exactly three tiers, the fall-through counted, and the tiers are pairwise disjoint as stated
  (each `compute` is a nested `A if c1 else (B if c2 else C)`, and every `c2` as written in the `rule` excludes
  `c1` either explicitly or through the word "instead").
- Every tier of every ladder is a sentence of its policy's `rule` and a branch of the named `decides` binding,
  and every branch of every `decides` binding is a tier the rule states — with the exception recorded as FIND-1,
  where `credit_pot_basis`'s ladder repeats the rule's wording while the binding tests something else.
- Every `decides` names an input, never `result`. Binding sets are disjoint across the factors of one policy in
  all six policies.
- Label honesty: each `method` factor's tiers substitute a different algorithm (a different anchor date, a
  different window, a different formula shape) and each `parameter` factor's tiers substitute a number. No
  `method` tier names a computation rule the charter nowhere states.

**FIND-4 (SOURCE-FACTOR RED) — two ladders are divided by a conjunct that holds of every customer who reaches
the write, which collapses each to a two-tier ladder and, in one case, gives two tiers the same value.**

- The conjunct: "the pass record carries the serial of media already issued" / "carries no media serial".
  - `passes_ext_carry_forward_fee.factors[id=media_reissue_component]`: tier 1 "the pass record carries the
    serial of media already issued **and** the pass has been scannable for at least the number of days the
    charter treats as settled media"; tier 2 "the pass record carries the serial of media already issued **and**
    the pass has been scannable for fewer days than that"; fall-through `K('media_none')`.
    `compute`: `media_component_usd: "P('replacement_media_fee_usd') if (F('media_serial') != '' and days_since_media_issue >= K('media_age_days')) else (RND(P('replacement_media_fee_usd') * K('media_part_share'), 2) if F('media_serial') != '' else K('media_none'))"`.
  - `passes_ext_settlement_credit.factors[id=gross_back_basis]`: tier 1 "took at least one day **and** the pass
    record carries the serial of media issued"; tier 2 "no day taken **and** the pass record carries **no** media
    serial"; fall-through "the price committed to less the tier's day use deduction for each day taken".
- Why the conjunct divides nobody: `passes_activation.rule` (base, inherited) — "Activation issues pass media,
  **writes the serial of that media to the pass record** and stamps the activation date." Both writes are
  reachable only on an activated pass: `elect_pass_carry_forward` is blocked until the record "stands in the
  state in which it admits the holder" (its own prerequisite sentence) and its `timing_rate` reads
  `F('activated_date')`; `issue_settlement_credit` follows a surrender of a pass that was active, and
  `remaining_share` likewise reads `F('activated_date')`. A pass that has never been activated carries no
  `activated_date` for either formula to anchor on. So `F('media_serial') != ''` is true of every customer who
  reaches either write.
- Consequences, both demonstrable:
  1. `media_reissue_component`'s fall-through tier can never fire, so the ladder is two tiers, not three,
     against the required minimum of three.
  2. `gross_back_basis`'s tier 2 can never fire, and in the only region where its non-media conjunct is
     satisfiable (`scan_entries == 0`) tier 2's value and the fall-through's value are **the same number** —
     "the price committed to in full" and "the price committed to less the day use deduction for each of zero
     days taken" are both `price_paid_usd`. Two tiers of one ladder select the same value, which is the
     unreal-ladder failure, and the ladder is again effectively two tiers.
- Root cause: a record field that is a consequence of the write's own eligibility has been used as a tier
  condition.
- Location: `passes.extended.yaml`, `passes_ext_carry_forward_fee.factors[media_reissue_component].ladder` and
  `compute[].media_component_usd`; `passes_ext_settlement_credit.factors[gross_back_basis].ladder` and
  `compute[].gross_back_usd`; against `blueprint/products/passes.yaml` `passes_activation.rule`.
- Bears on: task 0 (`media_reissue_component`) and task 1 (`gross_back_basis`).

**OBS-5 (observation) — a business-realism doubt about `media_reissue_component`'s outcomes.** The tiers add the
tier's *replacement* media fee to a carry-forward election on a pass whose media is neither lost, stolen nor
broken. The base rule that owns that fee, `passes_transfer_and_media`, reserves it for exactly those cases:
"Lost, stolen or broken media is replaced at the tier's replacement fee". Recorded as an observation because the
outcome is a charge a resort could defensibly publish for reissuing media on a carried-forward pass; the
demonstrable defect is FIND-4, not this.

**OBS-6 (observation) — four ladder `value` entries state a share where the rule and `compute` state an
amount.** `passes_ext_credit_offset.error_credit_hold` tier 2 `value: "K('error_retained_share')"` (= 0.5) and
`protection_premium_hold` tier 2 `value: "K('premium_hold_share')"`; `passes_ext_cancellation_charge.days_taken_component`
tier 2 `value: "K('light_use_share')"` and `protection_excess_relief` tier 2 `value: "K('relief_part_share')"`.
In each case the rule says "half of that error credit", "half the premium still to be collected", "half the
tier's day use deduction", "half that excess", and `compute` multiplies accordingly; only the ladder's `value`
field names the bare share. The tier-1 entries of the same ladders are written the other way ("the whole of the
error credit standing"). No second answer follows, so this is an observation.

**OBS-7 (observation) — `within_months=3` is not the charter's rolling review window.** Every binding that the
rules call "the rolling review window" is implemented as `within_months=3`
(`refusals_window`, `expired_refusals`, `refusals_recent`, and the `within_months=3` late-fee sums). The charter
defines that window once, in `passes_msr_declines_rolling_90d`: "The 90 calendar days ending on the handling
date inclusive, rolling", and `passes_arrears_suspension` cites it in `measures:`. Three calendar months as the
evaluator counts them (`0 <= MONTHS(row_date, NOW) < 3`) is 91 or 92 days depending on the handling date, so the
two windows differ at their far edge. No seeded row in either task falls in the gap (task 0's earliest decline is
2026-10-15 against a handling date of 2026-12-18; task 1 has no declines at all), so no consequence can be
demonstrated and this is not a red light.

**OBS-8 (observation) — `passes_ext_arrears_recovery.unsettled_reconciliation` tiers 1 and 2 coincide in value
over a whole region.** Where `cleared_count == 0`, tier 1 gives `MX(0, due_count - 0) = due_count` and tier 2
gives `due_count`; the two differ only in which disjoint refusal-count region they apply to. As stated the two
methods are different ("the instalments that have fallen due less the cleared instalments, never below zero" vs
"every instalment that has fallen due"), so this is not the same-outcome failure, but a reader on such a world
cannot tell the tiers apart by the number they produce.

**OBS-9 (observation) — `remaining_share_basis`'s second tier cannot reach the scored figure.**
`passes_ext_settlement_credit`'s `remaining_share` is consumed only inside `gross_back_usd`'s tier 1, which
itself requires `scan_entries >= 1`. `remaining_share_basis`'s tier 2 fires only when no day was taken
(`days_taken_a == 0`), i.e. exactly when `gross_back_usd` does not read `remaining_share` at all. The tier
decides the binding it names, so it is not a dead ladder, but it can never move the scored number.

### findings

| id | verdict | subject | tasks it bears on |
| --- | --- | --- | --- |
| FIND-1 | SOURCE-POLICY RED | `passes_ext_credit_offset.pot_usd`: rule tiers ("number of reasons") ≠ compute tiers ("presence of two particular reasons") | 1 |
| FIND-2 | SOURCE-POLICY RED | undeclared override of the charter's distinct-date day counting by `COUNT(passes_scan)` | 1 |
| FIND-3 | SOURCE-POLICY RED | `passes_ext_credit_offset` rule's tier-minimum sentence has no binding and no basis entry | 1 |
| FIND-4 | SOURCE-FACTOR RED | `media_reissue_component` and `gross_back_basis` divided by a conjunct true of every customer who reaches the write | 0, 1 |
| OBS-1 | observation | `issue_settlement_credit_d3237287` docstring states its position after the surrender | 1 |
| OBS-2 | observation | base `passes_credit_redemption` states a cross-problem order paralleling edge 3 | 1 |
| OBS-3 | observation | two extended policies name the same base sentence in `overwrite` with different replacements | 1 |
| OBS-4 | observation | credit-validity filter of the base rule absent from the extended pot bindings | 1 |
| OBS-5 | observation | replacement media fee added to a carry-forward with no media replaced | 0 |
| OBS-6 | observation | four ladder `value` entries name a share where rule and compute give an amount | 0, 1 |
| OBS-7 | observation | `within_months=3` vs the charter's 90-day rolling review window | 0 |
| OBS-8 | observation | `unsettled_reconciliation` tiers 1 and 2 coincide in value where `cleared_count == 0` | 0 |
| OBS-9 | observation | `remaining_share_basis` tier 2 can never move the scored figure | 1 |

## closing_checklist

Written after both tasks' `source_derivation_frozen` and `source_gt_comparison` sections were complete.
**This difficulty does not close.** Step 4's close-out applies only when all four relationships PASS on every
task; task 1 carries a SOURCE-POLICY, a SOURCE-CHAIN, a SOURCE-FACTOR and a SOURCE-TASK red light, and task 0
carries a SOURCE-FACTOR red light. The checklist is recorded below with each item settled either way, so that a
later revision can see exactly what already holds.

| item | status |
| --- | --- |
| Per-task audit files correspond one-to-one with the tasks; `_difficulty.md` sits alongside them | **holds** — `0.md`, `1.md`, `_difficulty.md` in `env/env_0004_ski_resort_operator/audits/policy_task/season_pass_billing_desk/` |
| Old revisions traceable | **holds** — first revision of this difficulty; nothing overwritten. The one arithmetic slip the auditor made in a frozen section (task 1, `remaining_share_basis` counterfactual, 129.53 for 129.52) is corrected in that file's `source_gt_comparison` and the frozen text is left as written |
| Every comparison section carries a PASS | **does not hold** — task 0: 3 of 4 PASS; task 1: 0 of 4 PASS |
| This difficulty's extended policies fully covered | **holds** — all six, three per task |
| The M tasks' scopes pairwise disjoint over the whole problem tree | **holds** — {arrears_recovery, reinstatement_charge, carry_forward_fee} vs {credit_offset, cancellation_charge, settlement_credit}; no shared policy, tool or base lineage |
| Task tools and GT closed | **holds** — six tools, each the `target_tool` of exactly one policy, each called exactly once in exactly one task's gold |
| Each task tool uses an independently generated, frozen uuid8 | **holds** — see `### action_binding_and_uuids` |
| Every tree has 1–3 prerequisite problems, ≥ max(n−1,1) `value_input` edges, ≥1 `owner=user` problem, no cycle | **holds structurally** — both trees are chains with n=2 and two `value_input` edges; task 0's user write is `elect_pass_carry_forward_09e30d1a`, task 1's is `give_up_season_pass_8c1a0eca`. **Task 1's tree nonetheless fails the relationship**, because the customer raises one of its two prerequisite problems (`1.md` F1-1) |
| The difficulty's `prerequisite` edges together are a DAG | **holds** — two disjoint chains, no cross-task reference |
| Every computation declares a self-sufficient baseline giving a definite number different from gold | **holds** — 844.65 / 49.00 / 129.00 and 260.00 / 150.00 / 714.68, all recomputed independently and all ≠ gold |
| 4–6 factors per computation, ≥2 `parameter`, ≥1 `method`; per task ≥1 multi-source and ≥1 cross-difficulty | **holds** — 5/5/6 and 4/6/6; task 0 has four multi-source factors and one cross-difficulty factor, task 1 four and three |
| Every ladder ≥3 tiers, stated in full in its rule, tiers distinct in outcome, conditions and outcomes ones the line of business actually holds | **does not hold** — FIND-4: `media_reissue_component` and `gross_back_basis` each have only two reachable tiers, and `gross_back_basis`'s tier 2 duplicates its fall-through's value |
| Every factor bears weight on its task's world against an honest baseline | **holds** — all 32 declared factors across the two tasks were substituted and recomputed independently; every one moves the scored figure, and every declared `baseline` is what that policy's `baseline.rule` states for that input |
| Instantiation-stage gates re-run once on the final form | **not run** — Step 4's re-run belongs to close-out, which is not reached. The entry snapshot supplied with the brief is cited in `charter_global_frozen` and was not re-run by the auditor |

### verdict

| task | policy self-consistency | problem tree | factors bear weight | unique solution |
| --- | --- | --- | --- | --- |
| 0 | PASS | PASS | **SOURCE-FACTOR RED** | PASS |
| 1 | **SOURCE-POLICY RED** | **SOURCE-CHAIN RED** | **SOURCE-FACTOR RED** | **SOURCE-TASK RED** |

The difficulty does not pass the source-layer audit. Four charter-global red lights (FIND-1 … FIND-4), one
task-level chain red light (`1.md` F1-1) and one task-level unique-solution red light (`1.md` F1-2) stand, with
nine charter-global observations and ten task-level observations recorded alongside them. No artifact was
edited, and no fix was designed or arranged.

---

# revision_2 — charter-global

## charter_global_frozen (revision 2)

- Freeze time: 2026-09-17T19:20Z (pre-reveal of round-2 GT; nothing in this section is derived from a revealed
  round-2 GT field).
- Auditor: same independent policy-task auditor as revision 1. Round-1 text above is untouched.
- **Re-derivation grounds.** Per the skill's re-derivation rule the hashes were compared against the round
  that produced each charter-global section:

  | artifact | revision 1 | revision 2 | disposition |
  | --- | --- | --- | --- |
  | `passes.extended.yaml` | `ff7ef832d3e4eab1` | `b0cc15a959d0d6fe` | **changed → every charter-global section re-derived in full** |
  | `task_tools.py` | `4e47d127a1d0aa96` | `b23dd81fd7f00617` | **changed → re-derived in full** |
  | `tasks/0.json` (masked) | `a973fbe383f02ac4` | `a973fbe383f02ac4` | unchanged |
  | `tasks/1.json` (masked) | `757aeeb0b223366a` | `952b0ce752708798` | changed |

  Hashes re-checked by the auditor with `sha256sum` against the rebuilt masked root; all four agree with the
  coordinator's brief.
- Entry conditions: the coordinator supplied the re-run gate snapshot on the reworked form (EXTENDED,
  TASK-TOOL-CONTRACT, REPLAY, SOLVABILITY, COMPUTE, GROUNDING, SCOPE all OK; TRACEABILITY unchanged
  pre-render). Not re-run by the auditor. `replay_tasks.py` was not invoked at all, so nothing was written
  back into the task files.
- `contamination_disclosure`: none. Both tasks' revision-2 derivations were frozen before any round-2 masked
  field was read. The auditor has of course seen round-1 GT; this round is therefore explicitly **not** a blind
  audit, and its question is narrower: is each round-1 RED genuinely closed, has the rework introduced a new
  defect, has anything previously passed regressed.

### policy_conflict_scan (revision 2)

- Base copy still verbatim: `head -1812` of the reworked `passes.extended.yaml` is byte-identical to
  `blueprint/products/passes.yaml` (`diff` empty). The file is reformatted (sequence items now at column 0,
  hence the hash change in untouched regions) and grew from 3052 to 3698 lines.
- Same six extended policies, same ids, same `(target_tool, computes)` pairs, each claimed once. Same six
  tools, same uuid8s, same owners (`elect_pass_carry_forward_09e30d1a` and `give_up_season_pass_8c1a0eca`
  `owner="user"`).
- Cross-category reads: still exactly four policies declaring `insure`, each matching what its `compute` reads.
- Task scopes still disjoint and jointly complete over the six policies.

### rule_compute_equivalence (revision 2)

**FIND-1 — CLOSED, and closed in substance.** `passes_ext_credit_offset.rule` now reads: "Where the pass
account shows **credit issued to put a billing error right**, the pot is instead the sum of every credit entry
the pass account shows issued less every application already drawn against them, since a record whose running
figure has had to be corrected is no longer the authority on what stands; and where the pass account shows
**no credit issued to put a billing error right but does show credit issued to put a service failure right**,
the pot is instead the sum of the entries issued to put a service failure right less every application already
drawn." The binding is unchanged —
`pot_usd: "credit_issued_total - credit_drawn_total if error_credit > 0 else (recovery_credit - credit_drawn_total if recovery_credit > 0 else credit_on_record)"`
— and the rule's tiers are now the conditions the binding tests, reason for reason. The round-1 counterexamples
no longer divide the two faces: a pass with `pass_cancellation` + `protection_settlement` credits now takes the
rule's fall-through, exactly as the binding does. The `credit_pot_basis` ladder carries the same two conditions.
Fall-through reachable (any credit reason other than those two, or none). **Verified, not merely reworded.**

**FIND-2 — CLOSED, and the "routed around rather than overridden" claim holds on inspection.** The check the
coordinator asked for is whether either policy still depends on the inherited day-counting sentences. It does
not:

- A sweep of all six extended `rule` texts for `day(s) the pass account shows | already scanned | taken | used`,
  `for each day`, `days the holder` returns **no match**. The phrase "days taken" has been removed from the
  charter's extended layer entirely.
- `passes_ext_cancellation_charge` now says: "Nothing further is retained for the **lift scans** the pass
  account shows. Where the pass account shows at least the number of **lift scan entries** the charter treats as
  heavy use, the tier's day use deduction is retained once in addition; and where it shows at least one **lift
  scan entry** but fewer than that number, half the tier's day use deduction is retained in addition." The
  binding is `scans_taken: "COUNT('passes_ledger', event_type='passes_scan')"` — a count of entries, which is
  exactly what the rule now names. Params renamed accordingly (`heavy_use_days` → `heavy_use_scans`,
  `days_component_none` → `scan_component_none`, `settled_media_days` → `settled_record_days`), and the factor
  is renamed `days_taken_component` → `scan_component`.
- `passes_ext_settlement_credit` removes the per-day multiplication altogether. Its second `overwrite` now
  replaces the base refund-basis sentence with "…the gross amount is instead the price committed to less the
  tier's day use deduction **taken once**, and never below zero", and the `use_rate` ladder (`days_taken_share`
  → `scan_share`) tiers on "lift scan entries". `gross_back_usd` no longer multiplies by any count.
- The base sentence that the round-1 bindings contradicted — `passes_access_control`'s "the day is counted on
  the first scan of that date and is not counted twice however many lifts are ridden" — governs how a *day* is
  counted. Neither reworked policy computes a quantity in days, so neither contradicts it. The base measure
  `passes_msr_season_scan_days` reaches these policies only through `passes_cancellation_refund`'s refund-basis
  sentence, and that sentence is named in both policies' `overwrite` and replaced. No `overwrite` entry is
  therefore required, and the round-1 undeclared override is gone rather than renamed.

**FIND-3 — CLOSED.** `passes_ext_credit_offset.rule` now ends: "Where the figure those deductions leave falls
below the smallest single application the tier allows, **no application is made at all and the whole of the pot
stays on the pass record**", and the binding implements it:
`net_application_usd: "RND(MN(MX(0, drawn_usd - retained_usd - premium_hold_usd), balance_due), 2)"` then
`result: "net_application_usd if net_application_usd >= P('credit_minimum_redemption_usd') else 0"`. The
sentence is carried into `baseline.rule` and `credit_minimum_redemption_usd` is named in `baseline.params`. The
round-1 second reading is resolved in favour of one of the two candidates, and the rule says which. **Closed.**

Everything else in the six policies was re-swept sentence by sentence against `compute_basis` and `compute`;
no new binding without a rule sentence and no new rule sentence without a binding was found.

### action_binding_and_uuids (revision 2)

- The six uuid8s are unchanged and still independently generated, unreused, non-sequential:
  `0159c539`, `08275b43`, `09e30d1a`, `52fe36c9`, `8c1a0eca`, `d3237287`.
- **OBS-1 — CLOSED.** `issue_settlement_credit_d3237287`'s summary now reads "Issue resort credit against a
  season pass record **for what the collective returns to the household on that pass**", where revision 1 read
  "…for what comes back to the household **after the pass has been given up**". A mechanical sweep of all six
  docstrings for `before | after | first | then | once | prior to | next` now returns only occurrences inside
  `Returns:` blocks describing a balance "afterwards", plus "so the guest sees both numbers fall at once" and
  "sees the charge on their next statement" — none states an action's position in a sequence, and none names
  another tool.
- Tool bodies re-read by AST: each is `ctx.find` → `found[0] if found else {}` → arithmetic → `ctx.create` →
  `ctx.update` → return. No `raise`, no error branch, no conditional on `status` or on any ledger row. The tool
  layer still judges no prerequisite.

### prerequisite_graph and prerequisite_sentences (revision 2)

Re-derived in full; **unchanged from revision 1 and still sound.** The four edges, their `kind`, `gate`, `form`,
`condition`, `policy_source` and `resolved_by` are identical, every `policy_source` is still verbatim in the
blocked policy's own `rule`, none is restated in the depended-on rule, every `gate` still names a real binding
of the blocked policy's `compute`, and the graph is still two disjoint acyclic chains. A fresh ordering-word
sweep over all six rules finds the same four "only after" sentences and no cross-problem order that grounds no
edge. The `resolved_by` effects were re-confirmed against the reworked tool bodies. See revision 1's
`### prerequisite_graph` and `### prerequisite_sentences` for the full four-point derivations, which this
revision reproduces rather than revises.

### override_declarations (revision 2)

- `passes_ext_cancellation_charge` and `passes_ext_settlement_credit`: the refund-basis sentence is still named
  by both (revision 1's OBS-3), and both `replaced_by` texts were rewritten to match the new scan-entry
  vocabulary. The round-1 undeclared override (FIND-2) is gone by removal of the dependence, not by a new
  `overwrite` entry — which is the legitimate route.
- `passes_ext_carry_forward_fee`: `overwrite` unchanged; `replaced_by` updated to say "the allowance and the
  **schedule carry component** are settled against it".
- `passes_ext_credit_offset` still carries `overwrite: []`, and the sentence-by-sentence sweep against
  `passes_credit_redemption` now finds the tier-minimum sentence honoured (FIND-3 closed). OBS-4 (the
  credit-validity filter absent from the pot bindings) stands unchanged and was, per the coordinator's note,
  recorded with reasons rather than reworked; the auditor's view is that this disposition is **right**: no
  world in either task carries a credit entry outside its validity period, so no consequence is demonstrable,
  and the skill forbids red-lighting what cannot be demonstrated.

### factor_ladders (revision 2)

| policy | factors | `parameter` | `method` | tiers each | cross_difficulty |
| --- | --- | --- | --- | --- | --- |
| `passes_ext_arrears_recovery` | 5 | 2 | 3 | 3 | — |
| `passes_ext_reinstatement_charge` | 5 | 3 | 2 | 3 | — |
| `passes_ext_carry_forward_fee` | 6 | 5 | 1 | 3 | `protection_share` → insure |
| `passes_ext_credit_offset` | 4 | 3 | 1 | 3 | `protection_premium_hold` → insure |
| `passes_ext_cancellation_charge` | 6 | 5 | 1 | 3 | `protection_excess_relief` → insure |
| `passes_ext_settlement_credit` | 6 | 4 | 2 | 3 | `protection_payout_offset` → insure |

Counts, labels and tier counts all within bounds, as in revision 1.

**FIND-4 — CLOSED on both limbs, and closed by removing the inert conjunct rather than by rewording it.**

- `passes_ext_carry_forward_fee`: `media_reissue_component` is **gone**. In its place
  `schedule_carry_component` (`parameter`, `decides: schedule_component_usd`), tiering on the instalment
  schedule: "Where the pass account shows an amount placed on it to be collected by instalments and the amount
  still to be collected is at least half of that amount, the schedule carry component the charter sets is
  added, because the plan runs on into the season the pass is carried to; and where … less than half of it,
  half the schedule carry component is added", fall-through "No component is added for carrying an open
  instalment schedule into the following season". Binding:
  `schedule_component_usd: "K('schedule_component_full') if (plan_amount_carried > 0 and outstanding_share_carried >= K('schedule_share_threshold')) else (K('schedule_component_part') if (plan_amount_carried > 0 and outstanding_share_carried < K('schedule_share_threshold')) else K('schedule_component_none'))"`.
  **All three tiers reachable**: the fall-through fires on a pass paid in full, which carries no
  `passes_plan_open` row and which base `passes_pricing` expressly allows ("the remainder is either taken in
  full or financed"). No conjunct is true of every customer who reaches the write. The parameters
  `media_age_days`, `media_part_share`, `media_none` and the use of `replacement_media_fee_usd` are all gone,
  which also **closes OBS-5** (the replacement media fee charged where no media is replaced) by removal.
- `passes_ext_settlement_credit`: `gross_back_basis`'s media conjunct is **gone**. The ladder is now
  tier 1 "the tier's refund basis is the pro rata basis and the pass account shows at least one lift scan
  entry" → price × the share still to come; tier 2 "the tier's refund basis is the day use basis" → price less
  the day use deduction taken once; fall-through → the price committed to in full. **All three reachable**,
  verified against the charter's variant table: `refund_basis` is `price_paid_less_day_use` on the Four-Day
  Flex, Midweek, Local and Summit tiers and `pro_rata_by_operating_days` on Summit Plus, Collective Unlimited
  and Collective Elite, so tier 2 has four tiers of customers; the fall-through fires on a pro-rata tier with
  no scan entry. No two tiers select the same value (price × share, price − deduction, price in full, with
  `day_use_deduction_usd` non-zero on every variant — 109.00 to 199.00).

**OBS-6 — CLOSED.** The four ladder `value` entries that named a bare share now name the amount: "half of the
error credit standing", "half of the premium still to be collected on that plan", "half the tier's day use
deduction is retained in addition" (in the rule; the ladder reads "half the tier's day use deduction"), "half
that excess", "half the schedule carry component the charter sets".

**OBS-7 — CLOSED.** A sweep for "rolling review window" across the whole extended layer now returns **nothing**.
Every ladder and every rule sentence that used to say it now says "the three whole months ending on the handling
date", which is exactly what `within_months=3` computes (`0 <= MONTHS(row_date, NOW) < 3`). The charter's
90-day measure `passes_msr_declines_rolling_90d` is no longer invoked by any extended rule.

**OBS-8 — standing, and the disposition is right.** `unsettled_reconciliation`'s first two tiers still coincide
in value wherever `cleared_count == 0`. As stated the two methods differ, so this is not the same-outcome
failure, and no number moves on either task's world; recording it with reasons rather than reworking it is
correct.

**OBS-9 — NOT CLOSED; the dead tier has been replaced by a tier that is dead across the whole charter.**
`remaining_share_basis`'s middle tier used to read "the pass account shows no day taken at all → the share still
to come is the whole", which could never move the score because `gross_back_usd` read `remaining_share` only on
a branch requiring at least one scan. It now reads "**the pass became scannable on or before the day the season
opened and the tier admits the holder on fewer days than the season runs** → the share still to come is the
days from the handling date to the season's last day set against **the number of operating days the tier admits
the holder on**", implemented as
`season_left_a / P('operating_days_included') if P('operating_days_included') < season_span else season_left_a / season_span`.
`remaining_share` is still consumed by exactly one branch — `gross_back_usd`'s tier 1 — and that branch now
requires `P('refund_basis') == 'pro_rata_by_operating_days'`. Against the charter's variant table:

| tier | `operating_days_included` | `season_span` | `refund_basis` |
| --- | --- | --- | --- |
| Four-Day Flex | 4 | 149 | price_paid_less_day_use |
| Midweek | 107 | 149 | price_paid_less_day_use |
| Local / Summit | 150 | 149 | price_paid_less_day_use |
| Summit Plus / Collective Unlimited / Collective Elite | 150 | 149 | pro_rata_by_operating_days |

The only variants with `operating_days_included < season_span` are Four-Day Flex and Midweek, and both are
`price_paid_less_day_use`, so on either of them `gross_back_usd` takes its own tier 2 and never reads
`remaining_share` at all. The new middle tier therefore cannot move a scored figure **on any variant this
charter sells** — a strictly wider dead zone than the tier it replaced, which was dead only where no scan stood.
Recorded as an observation because the factor still bears weight through its tier 1 and no number is wrong; but
the reworker's claim that OBS-9 is closed does not hold. (Had the tier been reachable, its outcome would also
have been extraordinary: a Four-Day Flex holder cancelling with 102 days left would take
`remaining_share = 102/4 = 25.5` and a gross amount of 25.5 times the price committed to, with no cap anywhere
in `result`.)

### new findings introduced by the rework (revision 2)

**N-1 (observation) — `passes_ext_settlement_credit.baseline.params` names a key its `baseline.rule` no longer
uses.** `baseline.params: [use_rate_none, offset_none, payout_none, uplift_none, **day_use_deduction_usd**]`,
while `baseline.rule` now reads in full "The gross amount coming back is the price committed to on the pass
record." — the day use deduction appears nowhere in it. The other four keys each answer a sentence of the
baseline rule. This is the shape the skill lists under an incoherent baseline ("its default keys are not the
ones `baseline.params` names"); it is recorded as an observation because the baseline still yields a definite
number different from gold on the one world that uses it, so no consequence can be demonstrated.
Location: `passes.extended.yaml`, `passes_ext_settlement_credit.baseline.params`.

**N-2 (observation) — the whole-computation baseline of `passes_ext_settlement_credit` is now a full refund.**
Substituting every factor's baseline gives `price_paid_usd` itself: on task 1, **1728.68**, where revision 1
gave 714.68. The baseline still passes the stated tests — self-sufficient, definite, and ≠ gold 302.89 — and as
a *tier* the fall-through is defensible (a pro-rata pass never scanned is returned in full). As the *standard
method* a reader computes with no factor applied, though, it says the collective hands back one hundred per
cent of the price on every surrender, which is not what the base charter itself describes
(`passes_cancellation_refund`: price paid less the cancellation fee less the day-use deduction). Recorded as an
observation: it is a consequence of closing FIND-4, and it is a granularity judgement rather than a
demonstrable second answer.

**N-3 (observation) — the reworked `passes_ext_credit_offset` can now compute a scored value the task tool's
contract will not accept, and which would leave a declared prerequisite permanently unmet.** `result` is now
`… else 0`, and the rule says "no application is made at all". But `apply_pass_credit_52fe36c9`'s `Args` block
still says of `credit_applied_usd`: "a **positive** figure booked exactly as given." A world on the new
fall-through would force a choice between calling the tool with a value its contract excludes and making no
call at all — and making no call leaves `passes_ext_cancellation_charge`'s gate ("The pass account carries an
entry applying resort credit against the amount the account still shows to collect") unsatisfiable, so the
whole downstream tree would have no solution. Neither task's world reaches that branch (task 1's application is
127.57 against a 50.00 tier minimum), so no consequence is demonstrable here and this is an observation.
Location: `passes.extended.yaml` `passes_ext_credit_offset.compute[].result` and `rule` (last sentence);
`task_tools.py` `apply_pass_credit_52fe36c9` docstring, `credit_applied_usd`.

**N-4 (observation) — the quantity the two reworked ladders divide on is turnstile reads, while the outcome
they select is still denominated per day.** `scan_component` and `scan_share` now tier on "lift scan entries",
and `gross_back_basis` tier 2 and `scan_component`'s outcomes are both amounts of `day_use_deduction_usd`,
whose `parameter_schema` entry reads "Amount in USD deducted from the refundable amount **for each day already
scanned** on this pass." A holder who rode six lifts on one day and a holder who skied six separate days are
now treated alike, on a charter that elsewhere defines a season's use in days (`passes_msr_season_scan_days`)
and states that a day is counted once however many lifts are ridden. This is internally consistent — which is
why it is not the round-1 red light — but it is a division a ski business does not make when settling a
refund, and the auditor records it so the disposition is visible rather than silent. It is graded an
observation, not a red light, because the charter now says what it computes and the disagreement is one of
granularity, which the skill expressly excludes from red lights.

**N-5 (observation) — the tier tolerance is applied over a window its own definition does not use.** The
reworked rules count refusals over "the three whole months ending on the handling date" and compare that count
against "the number of refusals the tier tolerates before privileges are reviewed", i.e.
`max_declines_before_suspension`, whose `parameter_schema` entry is "Number of declined instalments on this
pass **in the rolling review window** that brings the pass into suspension review". The window used and the
window the threshold is defined over are now different. No figure moves on either task (task 0's five refusals
fall inside both windows; task 1 has none), so this is an observation.
Location: `passes_ext_arrears_recovery` and `passes_ext_reinstatement_charge`, every tier naming that tolerance.

### findings (revision 2, charter-global)

| id | round-1 status | revision-2 verdict |
| --- | --- | --- |
| FIND-1 | SOURCE-POLICY RED | **CLOSED** — rule tiers rewritten to the conditions the binding tests |
| FIND-2 | SOURCE-POLICY RED | **CLOSED** — both policies routed off the day-counting convention; dependence removed, not renamed |
| FIND-3 | SOURCE-POLICY RED | **CLOSED** — floor implemented and the outcome named in the rule |
| FIND-4 | SOURCE-FACTOR RED | **CLOSED** — inert conjunct removed from both ladders; all tiers now reachable |
| OBS-1 | observation | **CLOSED** |
| OBS-5 | observation | **CLOSED** (factor removed) |
| OBS-6 | observation | **CLOSED** |
| OBS-7 | observation | **CLOSED** |
| OBS-2, OBS-3, OBS-4, OBS-8 | observation | standing; recorded-with-reasons disposition judged **right** |
| OBS-9 | observation | **NOT CLOSED** — replacement tier is dead across every variant of the charter |
| N-1 … N-5 | — | new observations introduced by or surviving the rework |

## closing_checklist (revision 2)

Written after both tasks' revision-2 `source_derivation_frozen` and `source_gt_comparison` sections were
complete. **The difficulty still does not close**, on one narrow red light in task 1.

| item | status |
| --- | --- |
| Per-task audit files one-to-one with the tasks; `_difficulty.md` alongside | holds |
| Old revisions traceable | holds — revision-1 text is untouched above; revision 2 is appended, and the revision-1 arithmetic slip the auditor disclosed is left standing with its correction |
| Every comparison section carries a PASS | **does not hold** — task 0: 4 of 4 PASS; task 1: 3 of 4 PASS |
| Extended policies fully covered; scopes pairwise disjoint | holds — unchanged |
| Task tools and GT closed; uuid8s independently generated and frozen | holds — the six uuid8s are unchanged |
| Trees: 1–3 prerequisite problems, ≥ max(n−1,1) `value_input` edges, ≥1 `owner=user` problem, no cycle; whole-difficulty DAG | holds — and task 1's tree now holds in substance as well, the customer raising only the root |
| Self-sufficient baseline per computation, definite and ≠ gold | holds — 844.65 / 49.00 / 129.00 and 260.00 / 150.00 / 1728.68, all independently recomputed (see N-1 and N-2 for two observations about the last of these) |
| 4–6 factors, ≥2 `parameter`, ≥1 `method`; per task ≥1 multi-source and ≥1 cross-difficulty | holds — 5/5/6 and 4/6/6; task 0 now carries five multi-source factors and task 1 four; cross-difficulty 1 and 3 |
| Every ladder ≥3 tiers, stated in full in its rule, tiers distinct in outcome, conditions and outcomes ones the line of business holds | **holds for reachability** — FIND-4 is closed on both limbs and every ladder now has three reachable tiers. Two residual observations: OBS-9/F1-13 (a tier that cannot reach the scored figure on any variant) and N-4 (division by turnstile reads) |
| Every factor bears weight against an honest baseline | holds — all 32 factors across the two tasks were re-substituted and recomputed; every one moves its scored figure |
| Instantiation-stage gates re-run on the final form | supplied by the coordinator and cited; not re-run by the auditor. `replay_tasks.py` was not invoked, so no `db_closure` was written back |

### verdict (revision 2)

| task | policy self-consistency | problem tree | factors bear weight | unique solution |
| --- | --- | --- | --- | --- |
| 0 | PASS | PASS | PASS *(was SOURCE-FACTOR RED)* | PASS |
| 1 | PASS *(was SOURCE-POLICY RED)* | PASS *(was SOURCE-CHAIN RED)* | PASS *(was SOURCE-FACTOR RED)* | **SOURCE-TASK RED** |

### round-1 findings, item by item

| id | round-1 verdict | revision-2 disposition | genuinely closed? |
| --- | --- | --- | --- |
| FIND-1 | SOURCE-POLICY RED | rule tiers rewritten to the conditions the binding tests; counterexample worlds no longer divide the faces | **yes** |
| FIND-2 / F1-2 | SOURCE-POLICY + SOURCE-TASK RED | both policies re-expressed over lift scan entries; no extended sentence is denominated in days; the base day-counting sentences are no longer depended on, so no `overwrite` is owed. The reworker's "routed around, not overridden" claim was tested against the artifact and **holds** | **yes** in the charter; its wording survives in two task-file proof fields (F1-11, F1-12, F0-7, F1-14) |
| FIND-3 / F1-5 | SOURCE-POLICY RED | floor implemented and the outcome named in the rule and the baseline | **yes** (see N-3 for a new consequence) |
| FIND-4 / F0-1 / F1-3 | SOURCE-FACTOR RED | the inert media conjunct removed from both ladders, replaced by the instalment schedule and by the tier's refund basis; all tiers reachable, verified against the variant table | **yes** |
| F1-1 | SOURCE-CHAIN RED | persona rewritten: the root alone is raised, the surrender sits behind an agent-triggered branch, the hand-over line generalised, `no_user_hint` rewritten and true | **yes** |
| OBS-1, OBS-5, OBS-6, OBS-7 | observations | closed | yes |
| OBS-2, OBS-3, OBS-4, OBS-8, OBS-10/F1-6 | observations | recorded with reasons, not reworked | **disposition judged right** in each case: none can be shown to move a figure on either world, and the skill forbids red-lighting what cannot be demonstrated |
| OBS-9 / F1-9 | observation | claimed closed; **it is not** — the dead tier was replaced by one dead across every variant the charter sells | **no** |

### what the rework introduced or left behind

| id | grade | subject |
| --- | --- | --- |
| **F1-11** | **SOURCE-TASK RED** | task 1's `argument_uniqueness_tracing.settlement_credit_usd` still asserts "six days taken" (false — the world shows five days and six entries) and grounds the gross-amount branch on a media serial the policy no longer tests |
| F0-6 | observation | task 0's `evaluation_criteria[2].necessity` justifies a read by "the media component", a factor the rework deleted |
| F0-7, F1-14 | observation | six `factor_sensitivity.tier_taken` strings, plus two necessity/tracing sentences, still carry superseded ladder wording ("the rolling review window", "credit issued under more than one reason"); all true of their worlds, none locatable in the reworked ladders |
| F1-12 | observation | task 1's `evaluation_criteria[3].necessity`: "the scans are the days taken" |
| F1-13 | observation | `remaining_share_basis`'s middle tier dead across the whole charter |
| F1-15 | observation | task 1's second computation lost its near-miss, which the F1-2 fix converted into a counted entry |
| N-1 … N-5 | observations | stale `baseline.params` key; a whole-computation baseline that is now a full refund; a computable `result` of 0 that the tool contract excludes and that would strand a declared gate; ladders dividing on turnstile reads while their outcomes are denominated per day; a tier tolerance applied over a window its own definition does not use |

Five of the six round-1 red lights are genuinely closed, and closed in substance rather than in wording: each
was re-tested against the reworked artifact rather than against the reworker's account, and the one claim most
at risk of being true in wording and false in substance — that FIND-2 was routed around rather than overridden
— was checked by sweeping every extended rule for day-denominated language and by confirming that the base
sentences are no longer in play. Task 0's moved gold was re-derived independently, longhand and by evaluator,
before the reveal: 52.38, matching GT, with all six sensitivities and both edge counterfactuals moving
coherently with it. Task 1's three figures were likewise re-derived and are unchanged. What blocks closure is
narrow and is not an arithmetic error: the proof field that establishes task 1's last argument as uniquely
entailed still reasons from a false statement of the world and from a condition the charter has deleted. No
artifact was edited, and no fix was designed or arranged.

---

# revision_3 — charter-global

## charter_global_frozen (revision 3)

- Freeze time: 2026-09-17T19:48Z, before any round-3 GT field was read.
- Auditor: same independent auditor. Revisions 1 and 2 above are untouched.
- **Re-derivation grounds.** Both charter artifacts changed again, so every charter-global section is
  re-derived in full rather than carried forward:

  | artifact | r1 | r2 | r3 | disposition |
  | --- | --- | --- | --- | --- |
  | `passes.extended.yaml` | `ff7ef832d3e4eab1` | `b0cc15a959d0d6fe` | `bc07fb1db5948419` | **changed → re-derived** |
  | `task_tools.py` | `4e47d127a1d0aa96` | `b23dd81fd7f00617` | `380e2735b696d2c2` | **changed → re-derived** |
  | `tasks/0.json` (masked) | `a973fbe383f02ac4` | same | `a973fbe383f02ac4` | unchanged in all three rounds |
  | `tasks/1.json` (masked) | `757aeeb0b223366a` | `952b0ce752708798` | `6a926aaae28f6f4b` | changed |

  Re-checked with `sha256sum`; all four agree with the brief. `passes.extended.yaml` is 3709 lines (r2: 3698).
- Entry conditions: the coordinator's re-run gate snapshot on the reworked form is cited, not re-run.
- `contamination_disclosure`: none for round 3; the round is explicitly not blind and is scoped to closure,
  new defects and regression.

### policy_conflict_scan (revision 3)

Base copy still verbatim (`head -1812` byte-identical to `blueprint/products/passes.yaml`). Same six policies,
same ids, same `(target_tool, computes)` pairs each claimed once, same six tools with the same uuid8s and the
same owners. Cross-category still exactly four `insure` readers. Task scopes still disjoint and jointly
complete.

**Unchanged from revision 2 in substance**: `passes_ext_arrears_recovery`, `passes_ext_reinstatement_charge`
and `passes_ext_carry_forward_fee` — their `compute` blocks are identical binding for binding, which is why
task 0's three figures cannot have moved except through `passes_ext_carry_forward_fee`, and that is unchanged
too. **Changed**: `passes_ext_credit_offset` (the `result` fallback) and `passes_ext_settlement_credit`
(`remaining_share` and `gross_back_usd` and the baseline).

### action_binding_and_uuids (revision 3)

- uuid8s unchanged: `0159c539`, `08275b43`, `09e30d1a`, `52fe36c9`, `8c1a0eca`, `d3237287`.
- Docstrings re-swept by AST for `before | after | first | prior to` outside `Returns:` blocks: **zero**
  ordering sentences in all six. OBS-1 stays closed.
- Tool bodies re-read by AST: 8–9 statements each, no `raise`, no error branch, no conditional beyond
  `found[0] if found else {}`. The tool layer still judges no prerequisite.
- **One contract changed**: `apply_pass_credit_52fe36c9`'s `credit_applied_usd` now reads "in USD to 2 decimal
  places, **never negative** and booked exactly as given", where revision 2 read "a **positive** figure booked
  exactly as given". This is half of the N-3 fix and is verified below.

### prerequisite_graph and prerequisite_sentences (revision 3)

Re-derived in full; **unchanged and still sound.** Same four `value_input` edges, same gates
(`expired_relief_rate`, `standing_rate`, `outstanding_rate`, `retained_offset_rate`), all `form: state`, every
`policy_source` still verbatim in the blocked policy's own rule and absent from the depended-on rule, every
gate still a real binding, graph still two disjoint acyclic chains, `resolved_by` effects re-confirmed against
the tool bodies. The full four-point derivations stand at revision 1.

### override_declarations and the superseded-phrase sweep (revision 3)

The reworker claims a mechanical sweep rather than spot fixes. **The charter half of that claim holds.**
Counting occurrences of the seven superseded phrases in `passes.extended.yaml`:

| phrase | occurrences in the file | where |
| --- | --- | --- |
| "days taken" | 0 | — |
| "media serial" | 0 | — |
| "under more than one reason" | 0 | — |
| "media component" | 0 | — |
| "no application is made at all" | 0 | — |
| "rolling review window" | 1 | **line 59**, the base `parameter_schema` entry for `max_declines_before_suspension` — inherited base text, correctly untouched |
| "day use basis" | 3 | legitimate: the charter's own `refund_basis` vocabulary, now used deliberately in `gross_back_basis` and in the two `overwrite` superseded clauses |

`extended_policies:` begins at line 1814, so the extended layer is clean of all seven. OBS-2, OBS-3, OBS-4 and
OBS-8 stand untouched, as agreed in revision 2, and that disposition remains right.

### factor_ladders (revision 3)

Counts unchanged and within bounds: 5 / 5 / 6 / 4 / 6 / 6 factors, each with ≥2 `parameter` and ≥1 `method`,
every ladder three tiers, one `cross_difficulty` factor in each of the four `insure`-reading policies.

**OBS-9 / F1-13 — GENUINELY CLOSED, and closed by the two-part structural fix rather than by a reworded tier.**
I rejected the round-2 closure claim on a reachability argument over the whole variant table, so I re-ran the
same argument on the new form rather than on any synthetic world.

The fix has two limbs, and both are present:
1. `gross_back_usd`'s **fall-through now multiplies by the share**:
   `else RND(MX(0, F('price_paid_usd') * remaining_share - P('day_use_deduction_usd')), 2)` — in revision 2 it
   was `RND(MX(0, F('price_paid_usd') - P('day_use_deduction_usd')), 2)`, which read no share at all. The
   fall-through is the branch every `price_paid_less_day_use` variant takes.
2. `remaining_share`'s first tier is redrawn from activation timing to the day block:
   `MX(0, (P('operating_days_included') - scans_counted) / P('operating_days_included')) if P('operating_days_included') < season_span else …`

Reachability and load-bearing, re-derived against the charter's whole variant table (`season_span` is 149 for
every tier, all seven sharing 2026-11-20 → 2027-04-18):

| variant | `operating_days_included` | `remaining_share` tier | `refund_basis` | `gross_back_usd` branch | does that branch read `remaining_share`? |
| --- | --- | --- | --- | --- | --- |
| Four-Day Flex | 4 | **tier 1** | price_paid_less_day_use | fall-through | **yes** |
| Midweek | 107 | **tier 1** | price_paid_less_day_use | fall-through | **yes** |
| Local | 150 | tier 2 / fall-through | price_paid_less_day_use | fall-through | yes |
| Summit | 150 | tier 2 / fall-through | price_paid_less_day_use | fall-through | yes |
| Summit Plus | 150 | tier 2 / fall-through | pro_rata_by_operating_days | tier 1 when ≥1 scan | yes |
| Collective Unlimited | 150 | tier 2 / fall-through | pro_rata_by_operating_days | tier 1 when ≥1 scan | yes |
| Collective Elite | 150 | tier 2 / fall-through | pro_rata_by_operating_days | tier 1 when ≥1 scan | yes |

In revision 2 the only variants that could reach `remaining_share`'s middle tier were exactly the variants whose
`gross_back_usd` branch never read `remaining_share`, which is why the tier was dead charter-wide. That
coincidence is now broken from both ends: the tier that fires on Flex and Midweek is read by the branch those
two variants take. **All three tiers of `remaining_share_basis` are now reachable and capable of moving the
scored figure.** Closed.

`gross_back_basis`'s own three tiers are likewise all reachable and distinct in outcome: pro rata with ≥1 scan
→ price × share; pro rata with no scan → price in full; otherwise → price × share less the day use deduction
taken once. No two coincide, since `day_use_deduction_usd` is 109.00–199.00 on every variant and is nowhere
zero.

**N-1 — CLOSED.** `passes_ext_settlement_credit.baseline.rule` now reads "The gross amount coming back is the
price committed to on the pass record **multiplied by the share of the season still to come, less the tier's
day use deduction taken once**, and never below zero", so `day_use_deduction_usd` in `baseline.params` is the
key a sentence of the baseline uses. Every one of the five keys now answers a sentence.

**N-2 — CLOSED.** The whole-computation baseline is no longer a full refund. Recomputed independently on
task 1's world: `remaining_share` 102/149 = 0.684564, gross `MX(0, 1728.68 × 0.684564 − 169.00)` = 1014.39,
`use_rate` 1.0, no offsets, `uplift` 1.0 → **1014.39**, against revision 2's 1728.68. It is self-sufficient,
definite, ≠ gold 302.89, and now resembles the base charter's own refund basis rather than handing the price
back whole.

**N-4, N-5 — recorded with reasons rather than changed; the disposition is right.** Neither moves a figure on
either world, and the skill forbids red-lighting what cannot be demonstrated. N-4 (ladders dividing on
turnstile reads while their outcomes are denominated per day) remains a granularity judgement about an
internally consistent charter. N-5 (`max_declines_before_suspension` applied over three whole months while its
`parameter_schema` defines it "in the rolling review window") is now the sole surviving occurrence of that
phrase, at line 59 of the inherited base, and is untouchable without editing the blueprint.

### new findings introduced by the rework (revision 3)

**M-1 (SOURCE-POLICY RED) — the new `remaining_share` tier computes a count of days by subtracting a count of
lift-scan entries, so rule and compute reach different conclusions in the same situation. This is FIND-2's
shape regressing into a binding written to close OBS-9.**

- Rule, verbatim: "Where the tier admits the holder on fewer days than the season runs, that share is instead
  **the days the tier admits the holder on that the pass account shows unused**, set against the days the tier
  admits the holder on, and never below zero". The `remaining_share_basis` ladder repeats it word for word.
- Compute, verbatim: `MX(0, (P('operating_days_included') - scans_counted) / P('operating_days_included'))`,
  where `scans_counted: "COUNT('passes_ledger', event_type='passes_scan')"` — a count of **rows**, which the
  rest of this same policy calls "lift scan entries" throughout (`scan_share`: "at least the number of **lift
  scan entries** the charter treats as heavy use").
- The situation that divides them: a Granite Ridge Four-Day Flex Pass (`operating_days_included: 4`,
  `day_use_deduction_usd: 139.00`, `refund_basis: price_paid_less_day_use`, `pass_price_usd: 419.00`) whose
  holder skied **two days** and rode **three lifts on each**, giving six `passes_scan` rows on two distinct
  dates. The charter's own inherited sentence fixes the day count:
  `blueprint/products/passes.yaml` `passes_access_control.rule` — "the day is counted on the first scan of that
  date and is not counted twice however many lifts are ridden" — and `passes_msr_season_scan_days` — "Count of
  distinct event_date values".
  - By the rule: days unused = 4 − 2 = 2, share = 2/4 = **0.5**, gross = `MX(0, 419.00 × 0.5 − 139.00)` =
    **70.50**.
  - By the binding: `MX(0, (4 − 6)/4)` = **0**, gross = `MX(0, 419.00 × 0 − 139.00)` = **0.00**.
- Root cause: a day-denominated quantity implemented from an entry count, in the one tier where the two are
  subtracted from one another rather than merely compared against a threshold. Where N-4 is a granularity
  judgement about a comparison, this is an arithmetic contradiction: the numerator mixes units.
- Demonstrated consequence: two passages of the artifact reach different conclusions in the same situation, and
  the merged semantics are not unique — the demonstration standard the Core-constraints table sets for policy
  self-consistency. A second consequence follows for the ladder's realism: on the binding's reading, any
  Four-Day Flex holder who rides more than four lifts in the season — an ordinary single day out, against a
  `daily_scan_limit` of 14 — is returned nothing at all.
- Affected artifact and location: `passes.extended.yaml`, `passes_ext_settlement_credit` —
  `rule` (the "Where the tier admits the holder on fewer days than the season runs…" sentence),
  `compute[].remaining_share`, `compute_basis.remaining_share`,
  `factors[id=remaining_share_basis].ladder` tier 1.
- Bears on: neither task's world reaches it (task 1's pass is Collective Unlimited at 150 operating days, so it
  takes tier 2; task 0 does not claim this policy), so it is charter-global and demonstrated by quotation, as
  FIND-1 was in revision 1.

**M-2 (SOURCE-POLICY RED) — the new tier-minimum fallback has no zero floor, so `passes_ext_credit_offset` can
compute a negative scored value, which its own rule and the tool contract both forbid.**

- Rule, two sentences of the same paragraph: "the result is **never below zero**, never more than the amount the
  pass account still shows to collect, and is rounded to the cent once at the end. Where the figure those
  deductions leave falls below the smallest single application the tier allows, the application is raised to
  that smallest single application, and **where the pot itself or the amount the pass account still shows to
  collect is smaller than that, the smaller of those two is applied instead**."
- Compute: `result: "net_application_usd if net_application_usd >= P('credit_minimum_redemption_usd') else RND(MN(MN(pot_usd, balance_due), P('credit_minimum_redemption_usd')), 2)"`.
  `net_application_usd` carries `MX(0, …)`; the fallback branch carries none.
- A negative pot is reachable under the charter as it now stands. `pot_usd`'s second tier is
  `recovery_credit - credit_drawn_total` — the service-failure entries less **every** application already drawn,
  which is what revision 2's FIND-1 fix made the rule say explicitly. A pass carrying a 100.00
  `service_recovery` credit and a 200.00 `pass_cancellation` credit, with 250.00 of applications already drawn,
  has `error_credit` 0 and `recovery_credit` 100 > 0, so `pot_usd` = 100.00 − 250.00 = **−150.00**. Each
  ingredient is ordinary: base `passes_cancellation_refund` issues `pass_cancellation` credit and base
  `passes_credit_redemption` permits applying credit to part of a charge.
- Traced through the binding: `drawn_usd` −150.00, `net_application_usd` `RND(MN(MX(0, −150), 1000), 2)` = 0.00,
  0.00 < 50.00 → fallback `RND(MN(MN(−150.00, 1000.00), 50.00), 2)` = **−150.00**.
- Demonstrated consequence: either the rule contradicts itself — sentence A says never below zero, sentence B
  says apply the pot — or, on the reading that keeps sentence A in force, the binding diverges from the rule.
  Both readings are a failure of policy self-consistency, and the value produced also violates
  `apply_pass_credit_52fe36c9`'s own `credit_applied_usd` contract, "never negative".
- Affected artifact and location: `passes.extended.yaml`, `passes_ext_credit_offset` — `rule` (the last two
  sentences), `baseline.rule` (the same two sentences), `compute[].result`; and `task_tools.py`,
  `apply_pass_credit_52fe36c9`, `credit_applied_usd`.
- Relation to previous revisions: introduced by the N-3 fix. Revision 2's `result` was
  `… else 0`, which the `MX(0, …)` inside `net_application_usd` could not make negative.

**N-3 — CLOSED on the defect as raised, notwithstanding M-2.** Revision 2's complaint was that a *positive*
pot whose deductions ate it produced 0, a figure the tool contract ("a positive figure") excluded and which
would have left the downstream gate unsatisfiable. Reachable range re-derived independently:

| situation | pot | result |
| --- | --- | --- |
| task 1's world | 305.00 | 127.57 |
| deductions exceed the minimum's remainder | 100.00 | **50.00** (raised to the tier minimum) |
| pot smaller than the minimum | 10.00 | 10.00 |
| pot genuinely zero | 0.00 | 0.00 |
| nothing left to collect | 305.00, balance 0 | 0.00 |

Zero is now reachable only where the pot or the balance is itself zero — a case in which a zero-value
`passes_credit_redeem` row is the honest record and the downstream gate ("the pass account carries an entry
applying resort credit") is still satisfied. Together with the contract's change from "a positive figure" to
"never negative", both halves of N-3 are answered. M-2 is a different defect in the same replacement code.

### findings (revision 3, charter-global)

| id | round-2 status | revision-3 verdict |
| --- | --- | --- |
| OBS-9 / F1-13 | observation, NOT closed in r2 | **CLOSED** — two-limbed structural fix verified across the whole variant table |
| N-1 | observation | **CLOSED** |
| N-2 | observation | **CLOSED** |
| N-3 | observation | **CLOSED** as raised (see M-2) |
| N-4, N-5 | observations | standing; disposition **right** |
| OBS-2, OBS-3, OBS-4, OBS-8 | observations | standing, untouched, disposition right |
| **M-1** | — | **SOURCE-POLICY RED** — days minus scan entries in `remaining_share`'s new first tier |
| **M-2** | — | **SOURCE-POLICY RED** — no zero floor on the new tier-minimum fallback |

## closing_checklist (revision 3)

**The difficulty still does not close**, on two charter-global red lights raised this round. Both tasks now
pass all four relationships on their own worlds; what blocks closure is the charter's behaviour outside them.

| item | status |
| --- | --- |
| Per-task files one-to-one; `_difficulty.md` alongside; revisions 1–3 all preserved | holds |
| Every comparison section carries a PASS | **holds per task** — task 0: 4 of 4; task 1: 4 of 4 |
| Extended policies covered; scopes disjoint; tools and GT closed; uuid8s frozen and unreused | holds |
| Trees: 1–3 prerequisite problems, ≥ max(n−1,1) `value_input` edges, ≥1 `owner=user` problem, DAG | holds |
| Self-sufficient baseline per computation, definite and ≠ gold | holds — 844.65 / 49.00 / 129.00 and 260.00 / 150.00 / 1014.39, all independently recomputed |
| 4–6 factors, ≥2 `parameter`, ≥1 `method`; per task ≥1 multi-source and ≥1 cross-difficulty | holds |
| Every ladder ≥3 **reachable** tiers, tiers distinct in outcome | holds — OBS-9's charter-wide dead tier is closed |
| Every factor bears weight against an honest baseline | holds — all 32 re-substituted and recomputed |
| Every computation has a near-miss | holds — task 1's computation 2 has one again (see `1.md` F1-15) |
| Rule ↔ compute equivalence in both directions | **does not hold** — M-1 and M-2 |
| Gates re-run on the final form | cited from the coordinator; the auditor additionally ran `replay_tasks.py --check` only: `0.json 12 acts clos=21/21 match=True`, `1.json 13 acts clos=17/17 match=True`. Nothing was written back |

### verdict (revision 3)

| task | policy self-consistency | problem tree | factors bear weight | unique solution |
| --- | --- | --- | --- | --- |
| 0 | PASS | PASS | PASS | PASS |
| 1 | PASS *(on this world; M-1 and M-2 are not reached here)* | PASS | PASS | PASS *(was SOURCE-TASK RED)* |

### round-2 findings, item by item

| id | round-2 verdict | revision-3 disposition | genuinely closed? |
| --- | --- | --- | --- |
| **F1-11** | SOURCE-TASK RED, the sole blocker | tracing rewritten; checked link by link against the policy, not merely for the absence of "days taken" — every branch it selects is pinned by a condition the policy tests, every intermediate matches my independent derivation, and the chain reaches 302.89 by construction | **yes** |
| **OBS-9 / F1-13** | observation, closure claim rejected in r2 | two-limbed structural fix: the gross fall-through now multiplies by the share, and the share's first tier is redrawn over the day block. Re-checked across the whole variant table, as in r2, rather than on the synthetic world offered — the r2 coincidence that made the tier dead is broken from both ends | **yes** |
| **F1-15** | observation | a withdrawn `refund_review` seeded at 2027-01-04; it is a near-miss for `window_position_share`'s anchor date, moving the tier from 1.5 to 1.0 and the figure from 321.70 to 245.80 if mistaken for the window anchor. **My frozen round-3 assessment rejected this on too strict a test and is corrected in `1.md`, not rewritten** | **yes** |
| **N-1** | observation | `baseline.rule` now uses `day_use_deduction_usd`; all five `baseline.params` keys answer a sentence | **yes** |
| **N-2** | observation | whole-computation baseline 1728.68 → 1014.39, no longer a full refund, still definite and ≠ gold | **yes** |
| **N-3** | observation | reachable range re-derived: a positive pot now floors at the tier minimum, zero only where the pot or balance is itself zero, and the contract now reads "never negative" | **yes** as raised — but see M-2 |
| F0-6, F0-7, F1-12, F1-14 | observations | claimed closed by mechanical sweep; **the claim was checked**: 0 `tier_taken` mismatches across all 32 factors in both tasks, and every residual phrase hit is inside `design_rationale` quoting old text while narrating the fix | **yes** |
| N-4, N-5 | observations | recorded with reasons | disposition **right** |
| OBS-2, OBS-3, OBS-4, OBS-8, OBS-10/F1-6 | observations | untouched | disposition **right** |

### what this round introduced

| id | grade | subject |
| --- | --- | --- |
| **M-1** | **SOURCE-POLICY RED** | `passes_ext_settlement_credit.remaining_share` tier 1 computes "the days … unused" as `operating_days_included − scans_counted`, subtracting lift-scan entries from days. On a Four-Day Flex pass skied two days with three lifts each, the rule gives a share of 0.5 and a gross of 70.50; the binding gives 0 and 0.00. This is FIND-2's shape regressing into the binding written to close OBS-9 |
| **M-2** | **SOURCE-POLICY RED** | `passes_ext_credit_offset.result`'s new tier-minimum fallback carries no zero floor, so a pot of −150.00 — reachable, since the second pot tier subtracts every application drawn from the service-failure entries alone — yields −150.00, against the rule's own "the result is never below zero" and the tool's "never negative" |
| F1-16 | observation | a `design_rationale` paragraph in task 1 quotes a rule sentence this round has since replaced |

Every round-2 finding is genuinely closed, including the two the auditor had to test hardest: F1-11's tracing
was verified as a proof rather than as a word list, and OBS-9's fix was re-checked across the seven-variant
table rather than on the world offered. Both halves of the reworker's headline claim hold — two baselines moved
and no scored value moved — each re-derived independently before the reveal. The index shift from 7/9/11 to
8/10/12 in task 1 is carried consistently through `computations[].step`, `gold_actions[].step` and all three
`prior_step` references, and `replay_tasks.py --check` closes 17/17 against the new 13-act sequence, so the
broad regression surface the shift opened is clean.

What blocks closure is new. Two of the three replacement bindings written this round are not equivalent to the
rules they implement: one reintroduces, inside a subtraction, exactly the days-versus-entries confusion that
FIND-2 spent two rounds removing, and the other drops a floor its own rule states twice. Neither is reachable
on either task's seeded world, which is why both tasks pass, and neither is an arithmetic error in any scored
value — all six remain exactly as derived. No artifact was edited, and no fix was designed or arranged.

---

# revision_4 — charter-global

## charter_global_frozen (revision 4)

- Freeze time: 2026-09-17T20:12Z, before any round-4 GT field was read.
- Auditor: same independent auditor. Revisions 1–3 above are untouched.
- **Re-derivation grounds.** Both charter artifacts changed again, so every charter-global section is
  re-derived in full:

  | artifact | r1 | r2 | r3 | r4 | disposition |
  | --- | --- | --- | --- | --- | --- |
  | `passes.extended.yaml` | `ff7ef832…` | `b0cc15a9…` | `bc07fb1d…` | `63be714e15174763` | **changed → re-derived** |
  | `task_tools.py` | `4e47d127…` | `b23dd81f…` | `380e2735…` | `713cdaae1952451d` | **changed → re-derived** |
  | `tasks/0.json` (masked) | `a973fbe383f02ac4` in all four rounds | | | | unchanged |
  | `tasks/1.json` (masked) | `757aeeb0…` | `952b0ce7…` | `6a926aaae28f6f4b` | `6a926aaae28f6f4b` | **unchanged from r3 — the worlds did not move** |

  Re-checked with `sha256sum`; all four agree with the brief. The extended file is 3716 lines (r3: 3709).
- Base copy still verbatim: `head -1812` byte-identical to `blueprint/products/passes.yaml`.
- Entry conditions: the coordinator's re-run gate snapshot is cited, not re-run. `replay_tasks.py --check` only.
- `contamination_disclosure`: none for round 4; the round is not blind and is scoped to closure, new defects
  and regression.

### policy_conflict_scan and prerequisite structure (revision 4)

Same six policies, same ids, same `(target_tool, computes)` pairs each claimed once, same six tools with the
same uuid8s and owners, same four `insure` readers, same disjoint and jointly complete task scopes. The four
`value_input` edges, their gates, forms, conditions, `policy_source` sentences and `resolved_by` tools are
**unchanged and still sound**; a fresh verbatim check confirms every `policy_source` is a sentence of the
blocked policy's own rule and is absent from the depended-on rule. Tool bodies re-read by AST: 8–9 statements
each, no `raise`, no error branch, no conditional beyond `found[0] if found else {}`.

Only two policies changed: `passes_ext_settlement_credit` (`remaining_share`) and `passes_ext_credit_offset`
(`result`). No binding was added or removed in either — the same 17 and 16 binding names respectively — so the
shape change behind the gate's branch count moving 49 → 51 on `1.json` is confined to those two expressions.

### the entry/day arithmetic sweep, run independently (revision 4)

The reworker claims a charter-wide mechanical sweep. **I ran my own** rather than accept it. Method: classify
every binding whose expression is a scan-entry count, then search every expression of every policy for one of
those binding names appearing in an arithmetic context (`+ - * /`) alongside any day quantity (`DAYS(`,
`operating_days_included`, `season_start_date`, `season_end_date`, `season_span`, `season_left`, `held_span`,
`days_*`).

| scan-entry binding | policy | used in |
| --- | --- | --- |
| `scan_count` | `passes_ext_reinstatement_charge` | `unused_relief_rate` |
| `scans_taken` | `passes_ext_cancellation_charge` | `scan_component_usd` |
| `scans_counted` | `passes_ext_settlement_credit` | `use_rate` only — **no longer in `remaining_share`** |
| `scan_entries` | `passes_ext_settlement_credit` | `gross_back_usd`'s branch guard |

**Arithmetic mixes charter-wide: 0.** M-1's shape is gone everywhere, not merely at the site where it was
found. In revision 3 `remaining_share` read
`MX(0, (P('operating_days_included') - scans_counted) / P('operating_days_included'))`; it now reads
`K('whole_share') if P('operating_days_included') * K('day_block_quarter') < season_span else (…)`, which
contains no scan count at all.

**The one comparison site, inspected.** A search for ladder conditions in which a day-word and a scan-entry
count meet in a single sentence returns exactly one factor, `passes_ext_reinstatement_charge.unused_season_relief`,
in both of its non-fall-through tiers: "the pass account shows **no scan at all** and the pass has been
**scannable for at least / fewer days than the number of days** the charter treats as a long unused stretch",
implemented as `scan_count == 0 and days_scannable >= K('long_unused_days')`. The two sides are separately
bound and separately compared — `scan_count` against 0, `days_scannable` against 45 — and are never combined.
It is also unit-safe on its own terms: zero scan entries and zero scan days are the same condition, so no
entries-versus-days confusion can arise at that comparison. **Sound.**

### M-1 — CLOSED, and the substitute tier judged on its own merits (revision 4)

The subtraction is removed rather than reworded. The new tier reads: "Where the tier admits the holder on
**fewer days than a quarter of the days the season runs**, that share is instead **the whole**, because a pass
sold as a block of days is not used up by the calendar and what the holder has taken is settled by the day use
deduction rather than by the time remaining", implemented as
`P('operating_days_included') * K('day_block_quarter') < season_span` with `day_block_quarter: 4` and
`whole_share: 1.0`. Both sides are day quantities; nothing is derived from an entry count.

**Reachability re-derived across the whole variant table** (as in revisions 2 and 3, and on the charter rather
than on any world offered; `season_span` is 149 for every tier, so the threshold is 149/4 = 37.25 days):

| variant | `operating_days_included` | `od × 4 < 149` | `remaining_share` tier | `refund_basis` | `gross_back_usd` branch | reads the share? |
| --- | --- | --- | --- | --- | --- | --- |
| Four-Day Flex | 4 | **true** | **tier 1 (whole)** | price_paid_less_day_use | fall-through | **yes** |
| Midweek | 107 | false | tier 2 / fall-through | price_paid_less_day_use | fall-through | yes |
| Local | 150 | false | tier 2 / fall-through | price_paid_less_day_use | fall-through | yes |
| Summit | 150 | false | tier 2 / fall-through | price_paid_less_day_use | fall-through | yes |
| Summit Plus | 150 | false | tier 2 / fall-through | pro_rata | tier 1 when ≥1 scan | yes |
| Collective Unlimited | 150 | false | tier 2 / fall-through | pro_rata | tier 1 when ≥1 scan | yes |
| Collective Elite | 150 | false | tier 2 / fall-through | pro_rata | tier 1 when ≥1 scan | yes |

The author's report is confirmed: Four-Day Flex still fires on tier 1 and Midweek now falls to a different
tier. **The tier is not emptied** — it is reachable on one variant and it is load-bearing there, which is the
test OBS-9 turns on. On a Four-Day Flex pass (`pass_price_usd` 419.00, `day_use_deduction_usd` 139.00) the tier
gives `gross = MX(0, 419.00 × 1.0 − 139.00)` = **280.00**, against **147.83** if the fall-through share
(102/149 on a comparable date) applied — so substituting the tier changes the figure substantially.
All three tiers are reachable and outcome-distinct: the whole; the days remaining over the days held; the days
remaining over the season. **OBS-9 stays closed under the substitute tier.**

**N-6 (observation, new) — the substitute tier's stated reason is not carried out by the arithmetic, and the
outcome it produces is generous past what that line of business publishes.** The rule justifies taking the
share as the whole "because a pass sold as a block of days is not used up by the calendar and **what the holder
has taken is settled by the day use deduction** rather than by the time remaining". But the day use deduction
is taken **once** in `gross_back_usd`'s fall-through, not per day, so it settles nothing about what the holder
has taken: on a Four-Day Flex pass the gross is 280.00 whether the holder took none of the four days or all
four. The only thing that varies with use is the 0.9 / 0.95 scan share, so a holder who consumed the entire
block is returned `280.00 × 0.9` = **252.00 of 419.00 (60%)** against **280.00 (67%)** for a holder who took
nothing — a 28.00 spread for consuming the whole product. For comparison, the base sentence both policies
supersede, `passes_cancellation_refund`'s day-use basis ("the price committed to, less the tier's cancellation
fee, less the tier's day use deduction **for each day already scanned**"), would return this holder nothing at
all. The override is declared, so this is not an undeclared drift; it is recorded as an observation because it
is a realism and justification judgement rather than a contradiction yielding two numbers — the same grade this
audit gave N-4. It is the cost of the M-1 fix and did not exist in revision 3, where the tier did scale with
use (wrongly, through entries).

### M-2 — CLOSED, with the reachable range of all six `result` expressions re-derived (revision 4)

The fallback now carries the floor: `result: "net_application_usd if net_application_usd >= P('credit_minimum_redemption_usd') else RND(MX(0, MN(MN(pot_usd, balance_due), P('credit_minimum_redemption_usd'))), 2)"`,
and the rule states it — "; **that figure too is never below zero**" — in both `rule` and `baseline.rule`.
Re-running revision 3's counterexample: pot −150.00, balance 1000.00, minimum 50.00 →
`MN(MN(−150, 1000), 50)` = −150 → `MX(0, −150)` = **0.00**, where revision 3 returned −150.00.

Range check over **all six** `result` expressions against their tools' `never negative` contracts:

| policy | `result` | floored? | can it go below zero? |
| --- | --- | --- | --- |
| `passes_ext_arrears_recovery` | `RND(principal_due + fee_component, 2)` | no explicit `MX(0,…)` | **no** — `principal_due` is `RND(MX(0, …) × instalment_amount, 2)` and `fee_component` is a sum of late fees times a share in {0, 0.5, 1.0}; both summands are non-negative |
| `passes_ext_reinstatement_charge` | `RND(MX(0, …), 2)` | yes | no |
| `passes_ext_carry_forward_fee` | `RND(MX(0, …), 2)` | yes | no |
| `passes_ext_credit_offset` | main branch guarded by `>= minimum`; fallback `RND(MX(0, …), 2)` | yes, both branches | no |
| `passes_ext_cancellation_charge` | `RND(MX(0, …), 2)` | yes | no |
| `passes_ext_settlement_credit` | `RND(MX(0, …), 2)` | yes | no |

All six are non-negative on their whole reachable range, and all six tool contracts now read "never negative".
**Closed.**

**The docstring change did not weaken a contract that was doing real work.** `collect_past_due_0159c539`'s
`presented_amount_usd` moved from "always a positive figure and never rounded to whole dollars" to "**never
negative** and never rounded to whole dollars". What was lost is only the exclusion of exactly 0.00; what was
kept is the whole of the four-way parameter typing — "Fixed-format class", "in USD to 2 decimal places",
"never rounded to whole dollars", "the collection is booked at exactly this figure". And the relaxation is
**warranted rather than convenient**: `presented_amount_usd` can reach 0.00 under the policy, because
`held_over_count` equals `unsettled_count` on `retry_hold_over`'s first tier (giving `principal_due` 0) while
`fee_share` is `K('fee_share_none')` = 0.0 below two refusals (giving `fee_component` 0). Under the old
wording the tool contract would have forbidden a figure the policy can produce — the same defect family as
M-2. All six amount arguments now carry the identical "never negative" phrasing, so the module is internally
consistent. No gold call sits near the boundary (226.93, 44.10, 52.38, 127.57, 321.70, 302.89), so no
disambiguation is lost on either task.

### locatability and factor structure (revision 4)

Counts unchanged and within bounds: 5 / 5 / 6 / 4 / 6 / 6 factors, ≥2 `parameter` and ≥1 `method` each, every
ladder three tiers, one `cross_difficulty` factor in each of the four `insure` readers.

I re-ran the locatability sweep myself over all 32 factors and every quotation field. **Every `compute_basis`
entry, every `baseline.rule` sentence, every `overwrite.superseded_clause` (against its base policy), every
`overwrite.replaced_by` and every `policy_source` is verbatim present where it must be, and no `policy_source`
is restated in the depended-on rule — zero failures.** A naive exact-prefix match on ladder `when` clauses
reports 13 apparent misses; all 13 were inspected by hand and are the rule stating the tier elliptically
("…but fewer than **that number**", "…before two thirds of **that period**", "…where those records show **such
a plan** standing in force or with a claim open", "…the account shows **nothing left to collect**"). Each is
the same condition in ordinary English, and the pattern is unchanged from rounds 1–3. Not a finding.

### findings (revision 4, charter-global)

| id | round-3 status | revision-4 verdict |
| --- | --- | --- |
| **M-1** | SOURCE-POLICY RED | **CLOSED** — subtraction removed, not reworded; 0 arithmetic mixes charter-wide on my own sweep; substitute tier reachable, load-bearing and outcome-distinct |
| **M-2** | SOURCE-POLICY RED | **CLOSED** — both branches floored, floor stated in rule and baseline, range re-derived over all six `result` expressions; the docstring relaxation is warranted and loses no working constraint |
| OBS-9 / F1-13 | closed in r3 | **stays closed** under the substitute tier, re-checked across the variant table |
| N-4, N-5 | observations | standing; disposition right |
| OBS-2, OBS-3, OBS-4, OBS-8, OBS-10 | observations | standing, untouched, disposition right |
| **N-6** | — | **observation, new** — the substitute tier's justification clause is not honoured by the arithmetic, and a fully used Four-Day Flex pass is returned 60% of its price |

## closing_checklist (revision 4)

**The difficulty closes on the four relationships.** Both tasks pass all four, on their own worlds and on the
charter, and no red light remains open at either level.

| item | status |
| --- | --- |
| Per-task files one-to-one; `_difficulty.md` alongside; revisions 1–4 all preserved, older text untouched | holds |
| Every comparison section carries a PASS | **holds** — task 0: 4 of 4; task 1: 4 of 4 |
| Extended policies fully covered; task scopes pairwise disjoint over the whole tree; tools and GT closed | holds |
| Each task tool uses an independently generated, frozen, unreused uuid8 | holds — unchanged through four rounds |
| Trees: 1–3 prerequisite problems, ≥ max(n−1,1) `value_input` edges, ≥1 `owner=user` problem, whole-difficulty DAG | holds — two chains of two edges, both `value_input`, both bearing weight |
| Customer raises only the root; no prerequisite hinted; personas close where gold closes | holds |
| Self-sufficient baseline per computation, definite and ≠ gold | holds — 844.65 / 49.00 / 129.00 and 260.00 / 150.00 / 1014.39, all independently recomputed |
| 4–6 factors, ≥2 `parameter`, ≥1 `method`; per task ≥1 multi-source and ≥1 cross-difficulty | holds — 5/5/6 and 4/6/6; task 0 five multi-source and one cross-difficulty, task 1 four and three |
| Every ladder ≥3 reachable, outcome-distinct tiers, stated in full in its rule | holds — re-derived across the seven-variant table this round |
| Every factor bears weight against an honest baseline | holds — all 32 re-substituted and recomputed |
| Every computation has a near-miss | holds |
| Rule ↔ compute equivalence in both directions | **holds** — M-1 and M-2 closed; my own sweep finds 0 entry/day arithmetic mixes and 0 quotation-locatability failures |
| Gates re-run on the final form | cited from the coordinator; the auditor additionally ran `replay_tasks.py --check` only: `0.json 12 acts clos=21/21`, `1.json 13 acts clos=17/17`, both `match=True`. Nothing written back |

### verdict (revision 4)

| task | policy self-consistency | problem tree | factors bear weight | unique solution |
| --- | --- | --- | --- | --- |
| 0 | PASS | PASS | PASS | PASS |
| 1 | PASS | PASS | PASS | PASS |

**"Policy self-consistency PASS + problem tree holds PASS + factors bear weight PASS + unique solution PASS"
holds for both tasks, so this difficulty passes the source-layer audit.** Nine observations remain on record;
none is a ground for rework, and each is recorded with its evidence and its disposition.

### round-3 findings, item by item

| id | round-3 verdict | revision-4 disposition | genuinely closed? |
| --- | --- | --- | --- |
| **M-1** | SOURCE-POLICY RED | the subtraction is **removed**, not reworded: `remaining_share` no longer reads any scan count. My own charter-wide sweep — classify every scan-entry binding, then search every expression for one of them in arithmetic alongside a day quantity — returns **0 mixes**. The one comparison site where a day-word and an entry count meet (`unused_season_relief`) was inspected: separately bound, separately compared, never combined, and unit-safe because zero entries and zero days coincide | **yes** |
| **M-2** | SOURCE-POLICY RED | both branches floored, the floor stated in `rule` and `baseline.rule`, the round-3 counterexample now returning 0.00 instead of −150.00; reachable range re-derived over **all six** `result` expressions, all non-negative, all six contracts now "never negative"; the `collect_past_due` docstring relaxation verified as **warranted**, since that policy can itself reach 0.00, with every parameter-typing clause retained | **yes** |
| OBS-9 / F1-13 | closed in r3 | **stays closed** under the substitute tier: re-checked across the whole variant table rather than on the world offered. Four-Day Flex fires tier 1 and Midweek falls to tier 2, as reported; the tier is reachable on one variant and load-bearing there (gross 280.00 against 147.83), so it is not the emptied tier OBS-9 was about | yes |
| F1-16 | observation | **NOT closed** — the `design_rationale` paragraph still quotes, in the present tense, a rule sentence superseded twice since | **no** |
| N-4, N-5 | observations | recorded with reasons | disposition **right** |
| OBS-2, OBS-3, OBS-4, OBS-8, OBS-10 | observations | untouched | disposition **right** |

### what this round introduced

| id | grade | subject |
| --- | --- | --- |
| **N-6** | observation | the substitute day-block tier's stated reason — "what the holder has taken is settled by the day use deduction" — is not carried out, because that deduction is taken once rather than per day: a Four-Day Flex holder who took none of the four days is returned 280.00 and one who took all four 252.00, of a 419.00 price, where the superseded base sentence would have returned nothing. Recorded as an observation, at the grade this audit gave N-4, because it is a realism and justification judgement rather than a contradiction yielding two numbers |

Both round-3 red lights are genuinely closed, and both were closed by removing the defective construct rather
than by rewording it — the subtraction is gone from the charter entirely, and the missing floor is present in
the binding, the rule and the baseline alike. Each of the reworker's three mechanical claims was re-run by the
auditor rather than accepted: the entry/day sweep (0 mixes, one comparison inspected), the six-`result` range
check (all non-negative, contracts aligned), and the locatability sweep (every `compute_basis`, `baseline.rule`,
`overwrite` and `policy_source` quotation verbatim; 0 `tier_taken` mismatches across all 32 factors; the 13
apparent ladder misses inspected by hand and found to be the rule stating its tiers elliptically). The
"nothing moved" assertion holds in full — all six scored values, all thirty-two sensitivities, all six
baselines and all four counterfactuals were re-derived from scratch and are unchanged, notwithstanding the
compute shape change the branch count 49 → 51 records. One closure claim does not hold, F1-16, and it is an
observation about a worklog paragraph rather than about the policy or the scored solution.

No artifact was edited, and no fix was designed or arranged.

---

# revision_5 — charter-global

## audit_method_defect (revision 5)

This revision opens with a defect of **this audit**, not of the artifacts. The render-layer auditor derived
`settlement_credit_usd` = 302.90 from the published documents where the source scored 302.89, and observed that
my round-4 verdict reported an independent derivation of every scored value — which could not have landed on
302.89, because the charter's prose entails 302.90. The observation is correct, I accept it, and the root cause
is as follows.

**What I actually did.** From revision 1 onward my "independent derivation" was produced by a small evaluator
that read `passes.extended.yaml`, took each entry of a policy's `compute` block, and `eval`'d the expression in
a sandbox with `P`/`F`/`K`/`SUM`/`COUNT`/`LATEST`/`RND` bound. It was independent of the **task file** — it
never read `computations` or `evaluation_criteria`, which is why the freeze-then-reveal discipline held and why
it caught real defects in rounds 1–4. But it was **not independent of the `compute` block**: it executed it.
The longhand arithmetic I wrote into the reports reproduced the same structure — revision 1 records
"`RND(1366.86 × 0.9, 2)` = 1230.17", which takes the intermediate rounding from the expression rather than from
the sentence. A derivation that uses the compute as its oracle cannot test the compute.

**Why check 2 did not catch it.** Revision 1's `rule_compute_equivalence` section says the sweep covered
"every quantity, history window, filter, tier, branch, cross-category read, acting base, grouping of
operations, cap/floor, **rounding mode, rounding point** and interval counting convention". What the sweep
mechanically performed was (a) verbatim locatability of every `compute_basis` quotation inside the `rule`, and
(b) condition-by-condition matching of ladder tiers against branches. Neither tests **where** an expression
rounds against where its sentence says it rounds: a sentence and an expression can both be present, mutually
quoted, and still disagree about rounding placement. So "rounding point" was named as checked and was never
actually tested. That is the precise overclaim — the audit reported a property its method did not establish,
and it stood through four revisions.

**Where the overclaim sits on record.** Every `task_independent_derivation` and `source_gt_comparison` section
in revisions 1–4 of both `0.md` and `1.md` that asserts a figure was "re-derived from scratch" or "recomputed
independently". Those sections are left exactly as written, per the rule that an earlier answer is never
rewritten; this note is the correction, and each task file carries a pointer to it.

**What the method missed and what it did not.** The failure is specific to rounding placement. The checks that
did not route through the compute worked: the problem-tree walk from the rule sentences, the persona and
authorisation checks, the ladder-reachability derivations across the variant table (which caught OBS-9 twice,
including a false closure claim), and the two round-3 red lights — M-1 was found precisely by computing a
Four-Day Flex share from the *rule sentence* (0.5, gross 70.50) against the *binding* (0, gross 0.00), and M-2
by tracing a negative pot through the expression against the rule's "never below zero". Those were prose-versus-
compute comparisons and they succeeded. What was missing was making that comparison a standing test over every
arithmetic step rather than something done ad hoc where a sentence happened to look suspicious.

**The corrected method, used from this revision on.** For every scored parameter, derive the value from the
rule sentences alone with exact arithmetic, rounding only where a sentence states rounding, and only then
compare with the compute. Its results for this round are in `prose_derivation` below.

## charter_global_frozen (revision 5)

- Freeze time: 2026-09-17T21:48Z, before any round-5 GT field was read.
- Re-derivation grounds: `passes.extended.yaml` `63be714e15174763` → **`b20108d965c56d57`** (changed, so every
  charter-global section is re-derived); `task_tools.py` `713cdaae1952451d` (**unchanged** from round 4, so the
  tool-module conclusions of revision 4 — uuid8s, ordering-word sweep, inert bodies, the six "never negative"
  contracts — are carried forward by reference on those two hashes); `tasks/0.json` `a973fbe383f02ac4` and
  `tasks/1.json` `6a926aaae28f6f4b`, both unchanged from rounds 3 and 4, so neither world moved.
- Base copy still verbatim: `head -1812` byte-identical to `blueprint/products/passes.yaml`.
- Inputs this round additionally include the render-layer reports, which the coordinator permits:
  `env/env_0004_ski_resort_operator/audits/policy_kb/season_pass_billing_desk/1.md` and
  `audits/runtime_context/season_pass_billing_desk/1.md`.
- `contamination_disclosure`: none for round 5.

## prose_derivation (revision 5)

All six scored parameters derived from the rule sentences with exact decimal arithmetic, rounding **only**
where a sentence states it. This is the test that was missing in rounds 1–4.

| task / step | rounding the sentences state | prose-derived exact value | prose value at the cent | compute now gives |
| --- | --- | --- | --- | --- |
| 0 / 7 `presented_amount_usd` | instalment amount "rounded to the cent"; the product "rounded to the cent"; the fee component "rounded to the cent"; the total "rounded to the cent" | 168.93 + 58.00 | **226.93** | 226.93 |
| 0 / 9 `restoration_charge_usd` | base: none stated; result "rounded to the cent only once the reduction has been taken" | 98.00 × (1 − 0.55) = 44.1000 | **44.10** | 44.10 |
| 0 / 11 `carry_forward_fee_usd` | fee base: none stated; fee "rounded to the cent only once, on that final figure" | fee base 123.8580 → 52.375685 | **52.38** | 52.38 |
| 1 / 8 `credit_applied_usd` | "the pot taken at the share drawn and rounded to the cent"; "rounded to the cent once at the end" | 228.75 → 127.57 | **127.57** | 127.57 |
| 1 / 10 `retained_charge_usd` | charge base and scan component: none stated; "rounded to the cent once at the end" | charge base 138.00 → 321.7000 | **321.70** | 321.70 |
| 1 / 12 `settlement_credit_usd` | gross, scan share, offsets and uplift: none stated; "rounded to the cent once at the end" | 1728.68 × 102/129 = 1366.86325581…; × 0.9 − 941.70 = 288.47693023…; × 1.05 = **302.90077674…** | **302.90** | **302.90** |

**Prose and compute agree on every one.** The single figure that moved, 302.89 → 302.90, is the one the
render-layer audit named, and it moved to the value the prose always entailed. The derivation is robust to the
one place a reader might round differently: taking the gross as the computation document states it, 1366.86,
gives `(1366.86 × 0.9 − 941.70) × 1.05` = 302.89770 → **302.90** as well, so a document reader and a compute
runner land on the same cent whether or not they carry the gross exactly.

## rule_compute_equivalence (revision 5)

### the rounding change itself

`passes_ext_settlement_credit` now reads
`gross_back_usd: "F('price_paid_usd') * remaining_share if … else (F('price_paid_usd') if … else MX(0, F('price_paid_usd') * remaining_share - P('day_use_deduction_usd')))"`
and
`net_back_usd: "gross_back_usd * use_rate - retained_standing * retained_offset_rate - protection_payout * payout_offset_rate"`,
with the single `result: "RND(MX(0, net_back_usd * uplift_rate), 2)"`. Four roundings have become one, which is
what the rule and `compute_basis['result']` have said throughout: "it is rounded to the cent once at the end
and is never below zero". `gross_back_basis`'s baseline lost its `RND` with them and now reads
`MX(0, F('price_paid_usd') * remaining_share - P('day_use_deduction_usd'))`. **The author moved the compute to
the published prose rather than the prose to the compute**, which is the direction that leaves the rendered
corpus faithful; the KB text is untouched and still says the same thing.

### the charter-wide sweep, re-run by me

I enumerated every `RND` in the extended layer and matched each against the `compute_basis` sentence for its
own binding.

- **11 `RND` occurrences remain** in `compute`, in: `arrears_recovery.instalment_amount`, `.principal_due`,
  `.fee_component`, `.result`; `reinstatement_charge.result`; `carry_forward_fee.result`;
  `credit_offset.drawn_usd`, `.net_application_usd`, `.result`; `cancellation_charge.result`;
  `settlement_credit.result`.
- **Exactly one** has a basis sentence without a rounding word — `passes_ext_credit_offset.result`, whose
  `compute_basis` quotes only the fallback sentence ("Where the figure those deductions leave falls below the
  smallest single application…"). The author's claim is confirmed, and so is its harmlessness, for two
  independent reasons. First, the rule's immediately preceding sentence — "the result is never below zero,
  never more than the amount the pass account still shows to collect, and **is rounded to the cent once at the
  end**" — governs this binding, so the rounding is licensed by the policy even though the quoted fragment
  omits it. Second, the argument is cent-clean by construction: it is
  `MX(0, MN(MN(pot_usd, balance_due), P('credit_minimum_redemption_usd')))`, where
  `credit_minimum_redemption_usd` is a charter constant (25.00 or 50.00), `balance_due` is a 2-decimal holdings
  field, and `pot_usd` is in every branch either a 2-decimal holdings field or a difference of `SUM`s that the
  evaluator already returns rounded to 2. A min/max of cent-clean values is cent-clean, so the `RND` is a
  no-op and cannot diverge from the prose.
- **Zero `RND` remains in any factor baseline** across all 32 factors, so the three baseline strips are done
  and no fourth was missed.
- Every `baseline.rule` still carries its rounding sentence, in all six policies.

### the converse sweep, which the author did not claim

Stripping rounding tests one direction only. I also ran the converse — bindings whose sentence **does** state
rounding while the expression carries **no** `RND` — and found two, both benign:

- `passes_ext_arrears_recovery.plan_amount` is the bare ledger read `LATEST('passes_ledger','amount_usd', …)`;
  its basis sentence describes the *instalment* amount ("divided by the number of instalments the schedule
  holds, rounded to the cent"), and that rounding lands on `instalment_amount`, which does carry `RND`. The
  sentence is shared between two bindings and is honoured by the right one.
- `passes_ext_settlement_credit.net_back_usd` quotes the sentence ending "rounded to the cent once at the end",
  and the rounding lands on `result`. That is precisely the fix, not a gap.

**Equivalence therefore holds in both directions.** Every place the prose states a rounding, the compute
performs it exactly once and in the stated place; every place the prose is silent, the compute is exact.

### the eight stripped bindings, each checked against its own sentence

`reinstatement_charge.charge_base_usd`, `carry_forward_fee.fee_base_usd`,
`cancellation_charge.charge_base_usd`, `cancellation_charge.scan_component_usd`,
`settlement_credit.gross_back_usd`, `settlement_credit.net_back_usd`, `credit_offset.retained_usd`,
`credit_offset.premium_hold_usd` — all now exact, and none of the eight appears in the converse sweep, i.e.
**no sentence of any of the eight states a rounding that has been removed**. Each strip is licensed.
`passes_ext_carry_forward_fee.fee_base_usd` now yields 123.858 on task 0's world, as the prose entails
("one tenth of the price committed to on the pass record", with no rounding stated).

### what "moved nothing else" can and cannot mean

The author reports that no strip moved a figure except the one the audit named. On the two seeded worlds I
confirm that independently, below and in each task file. Charter-wide the claim cannot be established by
either of us, and it should not be read as reassurance: a strip is a **correction**, so wherever it would move
a figure on some other world, that world's old figure was the wrong one. The property that matters and that I
did establish is the one in `rule_compute_equivalence` above — prose and compute now agree everywhere,
including on rounding placement.

## half_cent_ties (revision 5)

The author claims no rounding reachable on either task lands on a half cent. This matters because the
evaluator's `round` is Python's half-to-even, so a tie would silently depend on a convention no sentence
states, and the coordinator reports a sibling difficulty closing a defect of exactly that kind.

I instrumented the `RND` binding in my own evaluator to record every argument, then ran, on both tasks: the
three scored results per task, every one of the 32 single-factor baseline substitutions, both whole-computation
baselines, and the counterfactual replays behind all four edge figures. **75 `RND` invocations were recorded.
None has an argument on an exact half cent, and none within 1e-6 of one.** The half-to-even convention is
never consulted on either task, so no scored value, baseline, sensitivity or counterfactual depends on it. The
claim is verified.

## other charter-global checks (revision 5)

- `days_component_none` — **corrected**. The string occurs **zero** times in the 3716-line charter, and
  `passes_ext_cancellation_charge.factors[scan_component].ladder[2].value` now reads `K('scan_component_none')`,
  matching the policy's declared `params`, its `compute`, its `compute_basis` and the factor's own `baseline`.
  The render-layer auditor graded this documentary and did not treat it as a scored defect; that grade was
  right, and the face is now consistent anyway.
- Factor structure unchanged and within bounds: 5 / 5 / 6 / 4 / 6 / 6 factors, ≥2 `parameter` and ≥1 `method`
  each, every ladder three reachable tiers, one `cross_difficulty` factor in each of the four `insure` readers.
- Prerequisite graph, prerequisite sentences, scopes, overwrite declarations and the entry/day arithmetic
  sweep (0 mixes) re-run and **unchanged from revision 4**.
- Tool module byte-identical to round 4; revision 4's conclusions on it stand on the hash
  `713cdaae1952451d`.

## findings (revision 5, charter-global)

| id | status |
| --- | --- |
| **AUDIT-1** | **defect of this audit**, recorded above: revisions 1–4 reported a rounding-placement check that the method never performed, because the derivation executed the `compute` it was meant to test |
| **R-1** (the render-layer finding) | **CLOSED** — compute moved to the published prose; prose-derived 302.90 now equals the compute; the corpus stays faithful and needs no re-render on this account |
| `days_component_none` | **CLOSED** |
| N-4, N-5, N-6 | standing observations; disposition right |
| OBS-2, OBS-3, OBS-4, OBS-8, OBS-10 | standing observations, untouched |
| M-1, M-2, OBS-9, F1-11, F1-13, F1-15, N-1, N-2, N-3 | closed in earlier revisions; re-checked this round and **not regressed** |
| F1-16 | **still not closed** — see `1.md` revision 5 |

## closing_checklist (revision 5)

**The source change is correct and the difficulty closes on the four relationships.** The render-layer RED is
answered at its root, not papered over: the compute was moved to the published prose, so the corpus stays
faithful and the product may re-render on this account.

| item | status |
| --- | --- |
| Per-task files one-to-one; revisions 1–5 all preserved, older text untouched | holds |
| Every comparison section carries a PASS | holds — task 0: 4 of 4; task 1: 4 of 4 |
| Extended policies covered; scopes disjoint; tools and GT closed; uuid8s frozen | holds — tool module byte-identical to round 4 |
| Trees: 1–3 prerequisite problems, ≥ max(n−1,1) `value_input` edges, ≥1 `owner=user` problem, DAG | holds |
| Customer raises only the root; personas close where gold closes | holds |
| Self-sufficient baseline per computation, definite and ≠ gold | holds — 844.65 / 49.00 / 129.00 and 260.00 / 150.00 / 1014.39 |
| 4–6 factors, ≥2 `parameter`, ≥1 `method`; per task ≥1 multi-source and ≥1 cross-difficulty | holds |
| Every ladder ≥3 reachable, outcome-distinct tiers | holds |
| Every factor bears weight against an honest baseline | holds — all 32 re-substituted |
| Every computation has a near-miss | holds |
| **Rule ↔ compute equivalence, including rounding placement** | **holds, and this time it was tested**: 11 surviving `RND`s each matched to a licensing sentence, the converse sweep run, zero `RND` left in any factor baseline, and all six scored values derived from the prose with exact arithmetic |
| Half-cent ties | none reachable — 75 instrumented `RND` invocations across both tasks, zero on a tie |
| Gates re-run | cited from the coordinator; the auditor additionally ran `replay_tasks.py --check`: `0.json clos=21/21`, `1.json clos=17/17`, both `match=True`. Nothing written back |

### verdict (revision 5)

| task | policy self-consistency | problem tree | factors bear weight | unique solution |
| --- | --- | --- | --- | --- |
| 0 | PASS | PASS | PASS | PASS |
| 1 | PASS | PASS | PASS | PASS |

### the round-5 items, one by one

| item | disposition |
| --- | --- |
| **R-1** — prose/compute rounding drift giving 302.90 from the documents against 302.89 scored | **CLOSED**. The compute now rounds once at the end, as the rule and `compute_basis['result']` always said. My own prose-derivation, frozen before the reveal, gives 302.90077… → **302.90**, matching the new gold and the render-layer figure. The fix direction keeps the published corpus faithful |
| the charter-wide `RND` sweep | **verified independently**: exactly one surviving `RND` lacks a rounding word in its own quoted basis, and it is licensed by the rule's preceding sentence and is a no-op on cent-clean inputs. All eight named strips are licensed by sentences that state no rounding. I also ran the **converse** sweep, which the author did not claim, and found only two apparent gaps, both benign |
| "no strip moved a figure except the one the audit named" | **true of every scored value, and incomplete on intermediates**. On task 1 the four sensitivities that moved are exactly the four sharing the corrected chain. On task 0 `fee_base_usd` moved from 123.86 to 123.858, and three of task 0's proof fields still walk the old chain — recorded as **F0-8**, an observation, since 52.38 is right under both |
| half-cent ties | **verified independently** — 75 instrumented roundings, zero ties, so the half-to-even convention is never consulted on either task |
| `days_component_none` | **CLOSED** — zero occurrences; the fall-through now reads `K('scan_component_none')` |
| task 0 | its compute **was** touched by the sweep (two bindings), its figures were not, and its proof prose was not re-derived with it (F0-8) |
| F1-16 | not claimed this round; **still open** as an observation |

### what this round found about the audit itself

The one substantive thing this round adds beyond confirming the fix is **AUDIT-1**, recorded in full at
`## audit_method_defect (revision 5)`: revisions 1–4 reported a rounding-placement check that the method never
performed, because the "independent derivation" executed the very `compute` it was meant to test, and check 2's
sweep tested quotation-locatability and condition-matching rather than where an expression rounds against where
its sentence says it rounds. That is why a one-cent prose/compute divergence survived four revisions here and
was caught at the render layer instead. The earlier text is left standing; this revision carries the corrected,
prose-first derivation of all six scored values, and the corrected method is now a standing test rather than
something applied where a sentence happened to look suspicious.

One observation is added this round (**F0-8**) and one remains open from earlier (**F1-16**); neither is a
ground for rework, neither touches a scored value, and neither bears on the published documents. Nine
observations stand in total across the five revisions, each with its evidence and disposition on record.

No artifact was edited, and no fix was designed or arranged.
