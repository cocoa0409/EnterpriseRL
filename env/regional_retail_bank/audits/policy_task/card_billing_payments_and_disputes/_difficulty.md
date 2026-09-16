# Policy-task audit — card_billing_payments_and_disputes / charter-global

## charter_global_frozen

- freeze time (UTC): 2026-09-16 09:13:04 (hashes taken), section written before any task's `evaluation_criteria` / `computations` were read.
- `env/regional_retail_bank/tasks/card_billing_payments_and_disputes/card.extended.yaml`
  sha256 `52c5124dc141f8797773ff2b39a500859117336ab1cfe1ee1e73c647e4f4df45`
- `env/regional_retail_bank/tasks/card_billing_payments_and_disputes/task_tools.py`
  sha256 `d326ce40b5b1e3893b7d771856f5c5e6077ebf419d73bd1d218598d6d7a88792`
- `env/regional_retail_bank/blueprint/products/card.yaml`
  sha256 `24ae13549122ccbae7d04336dcbc97d7ed134773de02ce3daaaa6896c638ef78`
- auditor: independent source-layer auditor (not the instantiating agent).
- Fields permitted for this section: `blueprint.yaml`, `db_schema.json`, `share_tools.py`, `blueprint/products/*.yaml`, the whole of `card.extended.yaml`, `task_tools.py`, `erlbench/`, and the instantiation-gate snapshot supplied with the brief.
- Fields explicitly masked at the time this section was written: `evaluation_criteria`, `computations`, `charter_scope`, `required_documents`, `design_rationale`, `solvability_contract`, `prerequisite_closure`, `db_closure`, `db_closure_matches_initial_state` for both tasks, and every sibling difficulty's audit output.

### entry_conditions (step 0)

The brief supplied all three required items and they check out:

- the instantiation-stage gate snapshot with its actual output lines (EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK). Cited, not re-run.
- the masked views and their hashes. I re-hashed both and they match the brief:
  `0.json` = `901447f2a71f1eb4468b2f1acdc2e9ae1d07fccb5a27da74e688643c437e51b8`,
  `1.json` = `931ad11b84d8c34fe67d6da650052a68b915140ddc80d8a605604d34a07f71dd`.
  Each masked view carries exactly `frozen_time`, `user_scenario`, `initial_state` (verified by listing the top-level keys).
- `check_traceability.py` is scheduled for the render stage by design; this is not recorded as incomplete input.

No incomplete-input finding.

### policy_conflict_scan

Base copy: `sed -n '1,1524p' card.extended.yaml` is byte-identical to `blueprint/products/card.yaml` (diff reports only a trailing blank line at 1525 before `extended_policies:`). The base section has not been rewritten.

Five extended policies, each with a distinct subject, trigger, target tool and computed quantity:

| policy | subject | computes | target tool | prerequisite |
| --- | --- | --- | --- | --- |
| `card_ext_late_fee_correction` | `card_fee_reversal` | `correction_amount` | `reverse_card_late_fee_4ff0f41c` | [] |
| `card_ext_rewards_statement_credit` | `card_rewards_redeem` | `points_redeemed` | `redeem_card_points_9bfb7edb` | → `card_ext_late_fee_correction` |
| `card_ext_dispute_provisional_credit` | `card_dispute_credit` | `provisional_credit_amount` | `post_card_dispute_credit_83d80881` | [] |
| `card_ext_dispute_rebill_recovery` | `card_dispute_rebill` | `rebill_amount` | `rebill_card_dispute_credit_f8e84f35` | [] |
| `card_ext_autopay_fixed_amount` | `card_set_autopay` | `autopay_amount` | `set_card_autopay_amount_b2f02f74` | → `card_ext_dispute_provisional_credit`, → `card_ext_dispute_rebill_recovery` |

Overlapping-subject check. Two policies share `base_policy_refs: [card_evt_billing_disputes]`
(`card_ext_dispute_provisional_credit`, `card_ext_dispute_rebill_recovery`), but they act on
disjoint ledger events (`card_dispute_credit` vs `card_dispute_rebill`), on disjoint dispute
statuses (`submitted` vs `resolved_cardholder_liable`) and supersede different base sentences.
No overlap. No two policies claim the same quantity, terminal state or cross-category read boundary.

Time anchors: every extended policy anchors on `NOW` (frozen date) through `MONTHS(F('opened_date'), NOW)`
and on `posted_date` / `notice_date` windows. No two policies anchor the same quantity on different clocks.

Cross-category read boundaries: all cross reads go through `CFIELD` / `EXISTS` / `XSUM` / `XCOUNT`
on `checking`, `savings`, `cd`. No extended policy writes outside `card`.

Task scopes (derived independently from the two `prerequisite` trees, not from `charter_scope`, which is masked):
- tree A = { `card_ext_rewards_statement_credit` (root), `card_ext_late_fee_correction` }
- tree B = { `card_ext_autopay_fixed_amount` (root), `card_ext_dispute_provisional_credit`, `card_ext_dispute_rebill_recovery` }

The two sets are pairwise disjoint and their union is all five extended policies: **mutually exclusive and jointly complete**.

**policy_conflict_scan: PASS.**

### rule_compute_equivalence

Check 2 run over all five policies, binding by binding, in both directions.

Forward (compute → rule): every one of the 5 policies supplies a `compute_basis` entry for every
`compute` binding, and I checked each quotation is a verbatim substring of that policy's own `rule`.
Every quantity, window, filter, tier, branch, cross-category read, acting base, grouping, cap/floor
and rounding convention in the compute has a rule sentence behind it.

Backward (rule → compute): every normative sentence of each `rule` is implemented. In particular
every declared factor's ladder tier is both a rule sentence and a branch of the `decides` binding,
and every branch of each `decides` binding is a tier the rule states — checked for all 25 factors.
No tier lives only in `compute`; no tier is promised only in prose.

Ladder disjointness as stated, checked per policy:
- the checking-tier ladders (`credited_share`, `covered_share`, `credited_proportion`, `coverage_share`)
  each have tier 1 = {Premier, Private Client} ∧ payments ≥ n, tier 2 = active checking ∧ ¬{Premier, Private Client} ∧ payments ≥ n,
  tier 3 = otherwise. Disjoint as stated, and the compute's nested conditional reproduces exactly that
  (`checking_tier != None and checking_tier != 'Premier Checking' and checking_tier != 'Private Client Checking'`).
- the deposit/fee ladders: `>= high ∧ fees == 0`, `>= high ∧ fees > 0`, otherwise. Disjoint.
- the balance/count ladders (savings, cd): `>= threshold ∧ count >= n`, `has_X ∧ < threshold ∧ count >= n`, otherwise. Disjoint.
- the seasoning ladders: `months >= n ∧ p`, `months >= n ∧ ¬p`, otherwise. Disjoint.

Residual observations (no rule/compute gap demonstrated; recorded, not red):

- **OBS-C1 — `RND` is Python `round`, which is banker's rounding, while every rule sentence says
  "rounded half-up".** `skills/erl-task-instantiate/scripts/check_compute.py:381`:
  `"RND": lambda x, n=2: round(float(x), n)`. The two differ only on an exact half. Neither task's
  world produces an exact half at any `RND` call (checked: 23.400000000000002, 11.2, 12.6, 976.075,
  275.93, 1068.3435, 32988.0, 41235.0), so no scored value moves. Framework-level; recorded as an
  observation, not a red light.
- **OBS-C2 — `float(int(x))` implements "reduced to the whole dollar below it".** For a negative
  argument this truncates toward zero (i.e. upward), not to the dollar below. It appears in
  `card_ext_late_fee_correction.rounded_correction`, `card_ext_dispute_provisional_credit.rounded_credit`,
  `card_ext_dispute_rebill_recovery.rounded_rebill` and `card_ext_autopay_fixed_amount.rounded_amount`.
  Only `rounded_rebill` can see a negative argument (`at_risk * rebilled_share - interest_relief`).
  Neither task takes that tier with a negative argument, so nothing moves. Observation.
- **OBS-C3 — binding name `interest_max_6m` carries a window its expression does not have.**
  `card.extended.yaml`, `card_ext_dispute_rebill_recovery.compute`:
  `interest_max_6m: "MAX('card_transactions','amount', event_type='card_interest_charge')"` — no
  `within_months`. The rule sentence it implements is "the largest single interest charge **ever**
  billed to the card account", and `compute_basis.interest_max_6m` quotes exactly that, so rule and
  compute agree; only the binding's name misleads. Observation.
- **OBS-C4 — a misfiled `compute_basis` citation.** `card_ext_rewards_statement_credit.compute_basis.reversals_1m`
  quotes the policy's **prerequisite sentence** ("The number of points a statement-credit redemption
  uses is fixed only after every late payment fee entry standing on the card account carries a
  matching reversal entry in the ledger") instead of the sentence that defines the quantity
  ("...less the fee reversals credited to it in the last month..."). The defining sentence is present
  in the rule and is cited for `fees_1m` and `interest_1m`, so there is no rule/compute gap — the
  citation is simply filed against the wrong binding. Observation.

**rule_compute_equivalence: PASS** (four observations, no red).

### action_binding_and_uuids

Each `(target_tool, computes)` pair is claimed by exactly one policy (table in `policy_conflict_scan`);
all five pairs are distinct on both components.

Tool module: `task_tools.py`, five tools.

| tool | uuid8 | owner | rw |
| --- | --- | --- | --- |
| `reverse_card_late_fee_4ff0f41c` | `4ff0f41c` | agent | write |
| `redeem_card_points_9bfb7edb` | `9bfb7edb` | user | write |
| `post_card_dispute_credit_83d80881` | `83d80881` | agent | write |
| `rebill_card_dispute_credit_f8e84f35` | `f8e84f35` | agent | write |
| `set_card_autopay_amount_b2f02f74` | `b2f02f74` | user | write |

Each uuid8 is 8 hex characters, all five are distinct, none shares a prefix or suffix with another,
none is a sequence number and none is derivable from a neighbour by an increment. No reuse, no
batch derivation.

Docstrings: none names another tool, none states a position in a cross-problem sequence, none carries
a business confirmation, review, wait or procedure that the policy does not have.

- **OBS-C5 — the ordering phrase "before the call" in `Args` entries.** Every `Id class` argument
  line ends "…read it from the <X> lookup for this cardholder before the call" (e.g.
  `task_tools.py`, `reverse_card_late_fee_4ff0f41c`, `card_account_id`). The word "before" is an
  ordering connective, but its scope is how to source that argument's value from a *read* lookup,
  not the write's position relative to another problem's write; it names no tool and no policy.
  Recorded as an observation.

**action_binding_and_uuids: PASS** (one observation).

### prerequisite_graph

Check 7 over the whole graph. `prerequisite` is filled in on all five policies
(`[]` on `card_ext_late_fee_correction`, `card_ext_dispute_provisional_credit`,
`card_ext_dispute_rebill_recovery`; one edge on `card_ext_rewards_statement_credit`;
two edges on `card_ext_autopay_fixed_amount`).

Three edges:

| # | blocked policy | depended-on problem | kind | gate | form | resolved_by |
| --- | --- | --- | --- | --- | --- | --- |
| E1 | `card_ext_rewards_statement_credit` | `card_ext_late_fee_correction` | `value_input` | `settlement_target` | `state` | `reverse_card_late_fee_4ff0f41c` |
| E2 | `card_ext_autopay_fixed_amount` | `card_ext_dispute_provisional_credit` | `value_input` | `payable_balance` | `state` | `post_card_dispute_credit_83d80881` |
| E3 | `card_ext_autopay_fixed_amount` | `card_ext_dispute_rebill_recovery` | `payable_balance` → `value_input` | `payable_balance` | `state` | `rebill_card_dispute_credit_f8e84f35` |

- every `problem` names another **extended** policy id in this file; none names a base policy and
  none names itself.
- the graph is acyclic: E1 out of `card_ext_rewards_statement_credit`, E2/E3 out of
  `card_ext_autopay_fixed_amount`, and the three depended-on policies have `prerequisite: []`.
  No cross-task reference exists, so the difficulty-wide graph is a DAG of depth 1.
- each `policy_source` is verbatim locatable in the **blocked** policy's own `rule` — I matched each
  as a substring, modulo the YAML folded-scalar line wrapping.
- `form: state` on all three; no `fallback_reason` appears anywhere, which is correct because no edge
  is declared in the action form.
- `condition` restates the handling-time state check at exactly the strength of the sentence
  (E1: every `late_payment` fee entry named as the source item of a fee reversal entry;
  E2: every `submitted` dispute named by a `dispute_provisional` dispute-credit entry;
  E3: every `resolved_cardholder_liable` dispute's temporary credit named as source item of a rebill
  entry). No quiet strengthening or weakening.
- `resolved_by` genuinely makes the gate hold: `reverse_card_late_fee_4ff0f41c` creates the
  `card_fee_reversal` row with `fee_code="late_payment"` and `source_item_id` = the fee
  (`task_tools.py`); `post_card_dispute_credit_83d80881` creates the `card_dispute_credit` row with
  `adjustment_reason="dispute_provisional"` and the dispute id; `rebill_card_dispute_credit_f8e84f35`
  creates the `card_dispute_rebill` row with the temporary credit as `source_item_id`.
- `kind: value_input` on all three, and each `gate` names a binding that genuinely exists in the
  blocked policy's `compute`: `settlement_target` in `card_ext_rewards_statement_credit`,
  `payable_balance` in `card_ext_autopay_fixed_amount`. Whether each edge moves the value is a
  per-task fact and is demonstrated in `0.md` / `1.md`.
- no authoring-viewpoint phrasing ("in this task", "at the opening", "the current world") appears in
  any `prerequisite` field.

**prerequisite_graph: PASS.**

### prerequisite_sentences

Check 6, four-point test on each of the three sentences.

**E1** — `card_ext_rewards_statement_credit.rule`:
> "The number of points a statement-credit redemption uses is fixed only after every late payment fee entry standing on the card account carries a matching reversal entry in the ledger."

1. joins this policy's own result ("the number of points a statement-credit redemption uses") to what
   it waits on with an explicit ordering connective — **"only after"**. ✓
2. state form: "every late payment fee entry standing on the card account carries a matching reversal
   entry in the ledger" is a record-visible state in the words the tables and finders use
   (`find_card_transactions` describes "fees … reversals"); no action, no performer, no tool. ✓
3. names no tool, no policy id, no snake_case token, no row id. ✓
4. exactly the strength of the `condition` (both quantify over *every* late-payment fee entry on the
   account). ✓

One write of this difficulty brings that state about: `reverse_card_late_fee_4ff0f41c` is the only tool
in `task_tools.py` that creates a `card_fee_reversal` row (the other four create `card_rewards_redeem`,
`card_dispute_credit`, `card_dispute_rebill`, and update `card_accounts`). Unique. ✓

Derivation to a single reading: the sentence says the point count waits on every late-payment fee
carrying a reversal; the records show which fees do not; `card_ext_late_fee_correction.rule` says the
unallowed part of a billed late payment fee "is credited back as one reversal entry carrying that late
payment fee as its source item". That is the only rule in the charter that describes writing a reversal
entry against a late payment fee, so the hop resolves in one way. ✓

**E2** — `card_ext_autopay_fixed_amount.rule`:
> "The fixed monthly amount of a standing automatic payment instruction is settled only after every billing dispute standing in submitted status on the card account carries its temporary credit entry in the ledger."

Ordering connective "only after" ✓; state form, record-visible ("billing dispute standing in submitted
status", "temporary credit entry in the ledger"), no action/performer/tool ✓; no tool name, policy id,
snake_case or row id ✓; same strength as the `condition` ✓. Unique bringing-about write:
`post_card_dispute_credit_83d80881` is the only tool creating a `card_dispute_credit` row. ✓
`card_ext_dispute_provisional_credit.rule` is the only rule describing the posting of a temporary
credit on a submitted dispute — single reading. ✓

**E3** — `card_ext_autopay_fixed_amount.rule`:
> "That amount is settled only once no temporary credit remains outstanding on a billing dispute the card account records as resolved against the cardholder."

Ordering connective "only once" ✓; state form ("no temporary credit remains outstanding on a billing
dispute … resolved against the cardholder") ✓; no tool/policy id/snake_case/row id ✓; same strength as
the `condition` ✓. Unique bringing-about write: `rebill_card_dispute_credit_f8e84f35` is the only tool
creating a `card_dispute_rebill` row ✓. `card_ext_dispute_rebill_recovery.rule` is the only rule
describing the rebill of an outstanding temporary credit — single reading ✓.

Nothing else about these dependencies is written anywhere: none of the three blocked rules carries a
second wording, a tool name or another problem's id for the same dependency; and none of the three
depended-on rules restates the prerequisite sentence (checked by substring search over each rule).

Cross-problem orders stated in a rule that ground no declared edge: none found in the five extended
rules. The base rules state no cross-problem order that any tree rests on.

**prerequisite_sentences: PASS.**

### override_declarations

Check 1's finding half, sentence by sentence against each `base_policy_refs` entry. Findings only —
the demonstration of consequence, where any, lives in the task files.

**`card_ext_late_fee_correction` → `card_evt_fee_reversal`.** `overwrite` declares one sentence:
"A fee is reversed in full, never in part, as one card_fee_reversal row whose source_item_id is the fee."
Working through the remaining base sentences:
- "A bank_error reversal applies to any fee billed contrary to this charter, such as … it has no limit."
  — the extended correction is written with `adjustment_reason="bank_error"` (`task_tools.py`) and its
  rule grounds itself in "the charter does not allow the bank to keep all of it". The base list is
  open ("such as"), and "it has no limit" is inherited and honoured (the extended rule has no count gate).
  Followed, not overridden.
- "A courtesy_waiver reversal applies only to a late_payment fee." / the `late_fee_courtesy_waivers_365d`
  count gate / the `late_fee_courtesy_min_prior_on_time` gate / "The account must be active or suspended
  when a courtesy reversal is granted." — all four govern `courtesy_waiver` reversals only. The extended
  reversal is `bank_error`. Inherited unchanged; not engaged.
- "A fee can be reversed at most once." — inherited. See OBS-C6.
- "When a dispute is resolved for the cardholder, fees billed on the disputed charge are reversed with
  adjustment_reason dispute_final." — different occasion; untouched.

- **OBS-C6 — the extended fee selector does not exclude an already-reversed fee.**
  `card_ext_late_fee_correction.rule`: "The fee as billed is the amount of the most recent late payment
  fee entry posted to the card account, selected by posted date", implemented as
  `LATEST('card_transactions','amount', date_field='posted_date', event_type='card_fee', fee_code='late_payment')`.
  If the most recent late payment fee already carried a reversal, the extended rule would still compute
  a correction on it while base's `reverse_once` dedup gate forbids writing it. Neither task's world
  puts the most recent late fee in that state (task 0's `fe3f9bf7` is unreversed; task 1 does not use
  this policy), so no second defensible answer is demonstrable on either world. Observation, not a red.

**`card_ext_rewards_statement_credit` → `card_evt_rewards`.** `overwrite` declares the whole redemption
sentence ("Points are redeemed only in whole points, at least rewards_redemption_minimum_points per
redemption, by one of rewards_redemption_types … rounded half-up to the cent."). Remaining base sentences:
- "Only tiers whose rewards_program is not none earn points." — inherited, engaged as a precondition.
- the earning / clawback sentences — untouched.
- "Redemption is allowed only while the account is active." — inherited and not weakened.
- "All unredeemed points are forfeited when … it closes" — different occasion; untouched.
The two clauses inside the superseded sentence that the extended rule keeps alive — whole points, and
the tier's redemption minimum — are restored explicitly ("Where the point count so obtained is below the
tier's own redemption minimum, no statement-credit redemption is made and nothing is posted"), so the
declaration does not silently drop them.

- **OBS-C7 — the task tool does not fire the base event trigger the redemption carries.**
  `blueprint/products/card.yaml`, event `card_rewards_redeem`, `triggers: - event: "card:card_rewards_credit"
  when: {redemption_type: statement_credit} …`, and `card_rewards_credit` "lowers the card balance".
  `redeem_card_points_9bfb7edb` writes only the `card_rewards_redeem` row (with `amount=""`) and updates
  `rewards_balance`; it writes no `card_rewards_credit` row and does not change `current_balance`. The
  docstring is candid about this ("the statement credit follows on the card"). This changes the terminal
  balance but not the computed `points_redeemed`, and the base trigger is a world-generation rule rather
  than a rule the agent applies. Observation.

**`card_ext_dispute_provisional_credit` → `card_evt_billing_disputes`.** `overwrite` declares the
temporary-credit sentence ("A temporary credit of the claimed amount, never more than the charge, is
posted as a card_dispute_credit with adjustment_reason dispute_provisional on the day a qualifying
dispute is registered."). Remaining base sentences:
- the registration sentence, the notice window and its counting rule — inherited unchanged.
- "Only a dispute whose dispute_status is submitted can receive a temporary credit." — inherited; the
  extended rule restates the same restriction in its own words ("still stands in submitted status") and
  does not weaken it.
- "Each dispute receives at most one temporary credit." — inherited, not weakened.
- "While a dispute is open, the disputed amount is not counted toward the minimum payment and no late
  fee or interest accrues on it." — see OBS-C8.
- the rebill and merchant-credit sentences — belong to the other extended policy.

- **OBS-C8 — base's "not counted toward the minimum payment" and the extended payable balance.**
  `card_evt_billing_disputes` excludes an open dispute's amount from the minimum payment, while
  `card_ext_autopay_fixed_amount.payable_balance` counts the disputed purchase in full among the charges
  and nets only the computed temporary credit. The base sentence is about the *minimum payment*, which
  the autopay fixed amount is not, so the two do not decide the same quantity and this is not read as
  an undeclared override. Observation.

**`card_ext_dispute_rebill_recovery` → `card_evt_billing_disputes`.** `overwrite` declares the rebill
sentence ("A temporary credit may be rebilled only when the dispute's dispute_status is
resolved_cardholder_liable or withdrawn, for the full temporary credit, with the temporary credit as
source_item_id."). The status gate and the `source_item_id` requirement survive in the extended rule and
in the tool; the two things the declaration replaces are "for the full temporary credit" (now a computed
share) and the basis (now "the amount at risk" = the dispute's recorded claim). Both are inside the
declared sentence. The remaining base sentences (registration, notice window, one temporary credit,
merchant-credit resolution) are inherited unchanged.

**`card_ext_autopay_fixed_amount` → `card_evt_payments`.** `overwrite` declares the fragment "for the
minimum due, the statement balance, or a fixed amount but never more than the statement balance".
Remaining base sentences:
- payment crediting cutoff, weekend/holiday rule, minimum-payment formula, CARD Act allocation order,
  credit balance refund — none of them decides `autopay_amount`; untouched.
- "The autopay source account must be a checking account of the same customer in active status." —
  inherited, not weakened; it is a live gate on the target tool's `autopay_source_account_id`.
- "Setting up or changing autopay is the cardholder's own instruction; cancelling takes effect for due
  dates at least autopay_change_lead_days calendar days after the change is recorded." — inherited; the
  target tool is `owner="user"`, consistent with it.
The cap moves from the statement balance to the payable balance, which is exactly what the declared
fragment replaces.

**No undeclared override found.** Every conflict between base and extended is named in that policy's
`overwrite` by the base sentence it replaces, and the merged semantics after each replacement is unique.
None of the three disguised forms is present: no anonymous intermediate (every extended intermediate is
introduced by a rule sentence of its own), no 0/1 multiplier applied to a base-fixed amount, and no
dropped base branch (every base branch that the extended selector can reach is still reachable).

**override_declarations: PASS** (three observations).

### factor_ladders

Charter-global structure of the factors. 25 factors across five policies.

| policy | factors | parameter | method | multi-source | cross-difficulty (categories) |
| --- | --- | --- | --- | --- | --- |
| `card_ext_late_fee_correction` | 4 | 2 | 2 | 4 | 4 (checking ×3, savings ×1) |
| `card_ext_rewards_statement_credit` | 4 | 2 | 2 | 4 | 3 (checking ×2, savings ×1) |
| `card_ext_dispute_provisional_credit` | 5 | 2 | 3 | 5 | 4 (checking ×2, savings ×1, cd ×1) |
| `card_ext_dispute_rebill_recovery` | 5 | 2 | 3 | 5 | 3 (cd ×1, savings ×1, checking ×1) |
| `card_ext_autopay_fixed_amount` | 6 | 4 | 2 | 6 | 3 (checking ×2, savings ×1, cd ×1) |

Every policy is inside the 4–6 bound, and every policy meets ≥2 `parameter`, ≥2 `method`,
≥2 multi-source and ≥2 `cross_difficulty`.

`decides` is an input binding in every case, never `result`:
`credited_share`, `relationship_addition`, `raw_correction`, `rounded_correction`;
`settlement_target`, `covered_share`, `point_value`, `rounded_points`;
`credited_proportion`, `proportion_base`, `offset_amount`, `uplift`, `rounded_credit`;
`rebilled_share`, `relief_share`, `open_interest`, `raw_rebill`, `rounded_rebill`;
`coverage_share`, `coverage_base`, `spread_cycles`, `carryover_addition`, `spread_amount`, `rounded_amount`.

Binding sets are disjoint within each policy: no binding appears in two factors' `bindings` lists of the
same policy (checked per policy; the shared upstream reads such as `checking_deposits_6m` appear in
exactly one factor's `bindings` in each policy).

Tier counts: every one of the 25 ladders has exactly three tiers, the fall-through counted, and each is
pairwise disjoint as stated (see `rule_compute_equivalence` for the disjointness argument by shape).

Every tier beyond the fall-through is multi-source: each is a conjunction of two conditions resting on
distinct records (a holding field plus a ledger aggregate, or two ledger aggregates over distinct rows).
Counted per policy above.

Every tier is stated in the `rule` with its condition and its value or method, and implemented in
`compute`; no tier lives only in one face.

Label honesty, checked one by one:
- every `parameter` factor's tiers substitute a different number into the same expression
  (`credited_share`, `relationship_addition`, `covered_share`, `point_value`, `credited_proportion`,
  `uplift`, `rebilled_share`, `relief_share`, `coverage_share`, `spread_cycles`, `carryover_addition`);
- every `method` factor's tiers change the algorithm — the window the aggregate is drawn from
  (`settlement_window_convention`, `open_interest_aggregation`), the base the share acts on
  (`proportion_base_convention`, `coverage_base_convention`), which rows are aggregated
  (`merchant_offset_selection`), the order the addition enters (`addition_entry_point`,
  `addition_entry_order`), the moment the cap bites (`ceiling_moment`), or the rounding convention
  (`correction_rounding_convention`, `point_count_rounding`, `credit_rounding_convention`,
  `rebill_rounding_convention`, `instalment_rounding_convention`);
- no `method` tier names a computation rule the charter nowhere states: each is quoted verbatim from
  its own policy's `rule`.

Cross-difficulty categories read: `checking` (holding `variant_name`, `ledger_balance`, `status`, and
`checking_transactions` deposits and fees), `savings` (holding `current_balance`, `status`, and
`savings_transactions` deposits, withdrawals and interest credits), `cd` (holding `principal_balance`,
`status`, and `cd_transactions` interest payouts). Every one of these is a real table and column of
`db_schema.json` and a real event type of the corresponding blueprint product.

Whether each factor **bears weight** rests on one world and is decided in `0.md` / `1.md` under
`factor_weight`; nothing about weight is concluded here.

**factor_ladders: PASS** (structure).

### findings

Charter-global findings, one by one. All six are observations; no charter-global red light.

| id | verdict | subject | bears on |
| --- | --- | --- | --- |
| OBS-C1 | observation | `RND` is banker's rounding while every rule says "half-up" | tasks 0 and 1 (no value moves) |
| OBS-C2 | observation | `float(int(x))` is truncation, not floor, on a negative argument | task 1 (`rounded_rebill`; tier not taken) |
| OBS-C3 | observation | binding named `interest_max_6m` has no window | task 1 |
| OBS-C4 | observation | `compute_basis.reversals_1m` cites the prerequisite sentence, not the defining sentence | task 0 |
| OBS-C5 | observation | "before the call" in every `Args` entry of `task_tools.py` | tasks 0 and 1 |
| OBS-C6 | observation | the extended late-fee selector does not exclude an already-reversed fee | task 0 (state not reached) |
| OBS-C7 | observation | `redeem_card_points_9bfb7edb` fires no `card_rewards_credit` and leaves `current_balance` unchanged | task 0 |
| OBS-C8 | observation | base's minimum-payment exclusion for an open dispute vs the extended payable balance | task 1 |

**Charter-global verdict: policy self-consistency holds at the charter level. No `SOURCE-POLICY RED`.**

## closing_checklist

Written after both tasks' `source_derivation_frozen` and `source_gt_comparison` were on disk. This is
the one difficulty-level conclusion reached **after** the reveals; the charter-global section above
remains pre-reveal by construction and was not touched.

**The difficulty does not close.** Step 4 requires all four relationships to PASS on every task; two
red lights stand. The checklist is recorded in full so that what does hold is on record.

| item | state |
| --- | --- |
| per-task audit files correspond one-to-one with the tasks, `_difficulty.md` alongside them | **yes** — `0.md`, `1.md`, `_difficulty.md` in `env/regional_retail_bank/audits/policy_task/card_billing_payments_and_disputes/` |
| old revisions traceable | **n/a** — first revision of this difficulty; nothing overwritten |
| every comparison section carries a PASS | **no** — `0.md` carries SOURCE-FACTOR RED; `1.md` carries SOURCE-FACTOR RED and SOURCE-TASK RED |
| extended policies fully covered | **yes** — all five are claimed: task 0 takes `card_ext_late_fee_correction` + `card_ext_rewards_statement_credit`, task 1 takes `card_ext_dispute_provisional_credit` + `card_ext_dispute_rebill_recovery` + `card_ext_autopay_fixed_amount` |
| the M tasks' scopes pairwise disjoint, each spanning the whole tree | **yes** — the two `charter_scope.extended_policies` sets are disjoint and each is exactly its task's root plus all of its prerequisite problems |
| task tools and GT closed | **yes** — the five tools are partitioned 2 / 3 across the two tasks, and every gold write calls a tool of that task's own `charter_scope.task_tools` |
| each task tool uses an independently generated, frozen uuid8 | **yes** — see § `action_binding_and_uuids` |
| every tree has 1–3 prerequisite problems | **yes** — task 0 has 1, task 1 has 2 |
| at least max(n−1, 1) `value_input` edges | **yes** — task 0: 1 of 1 required; task 1: 2 of 1 required |
| at least one problem resolved by an `owner=user` tool | **yes** — task 0 `redeem_card_points_9bfb7edb`, task 1 `set_card_autopay_amount_b2f02f74` |
| no cycle, including across tasks | **yes** — three edges, all from a root to a leaf; no cross-task reference exists |
| every computation declares a self-sufficient baseline giving a definite number different from gold | **yes** — 11.20 vs 23.00; 4144 vs 33000; 898.80 vs 976.00; 480.00 vs 276.00; 3502.96 vs 1068.00 |
| 4–6 factors per computation, ≥2 of each effect, ≥2 multi-source, ≥2 cross-difficulty | **yes** — see § `factor_ladders`; counts 4/4/5/5/6 |
| every ladder of at least three tiers stated in full in its rule | **yes** — all 25 ladders |
| every factor proved to bear weight on its task's world against an honest baseline | **yes numerically** — all 25 move their task's scored value, and every `baseline` is exactly what that policy's `baseline.rule` states for that input — **but** two factors take their tier on records the policy in force forbids (FIND-0-1, FIND-1-1), which is what the two SOURCE-FACTOR reds record |
| instantiation-stage gates re-run once on the final form | **not done, and out of scope for this audit** — the brief directs this auditor to cite the supplied snapshot and not to run the gates; the artifacts are in any case not in final form while the reds stand |

### blocking findings

| finding | task | verdict | one-line consequence |
| --- | --- | --- | --- |
| FIND-0-1 | 0 | SOURCE-FACTOR RED | a `checking_fee` row whose `posted_date` the checking charter forbids is what keeps `settlement_window_convention` on its first tier; on the charter-required date the scored `points_redeemed` is 18500, not 33000 |
| FIND-1-1 | 1 | SOURCE-FACTOR RED | `dispute_uplift_ladder`'s tier rests on a `card_disputes` row whose notice predates the disputed charge's statement by 234 days; without it `provisional_credit_amount` is 1001.00 and `autopay_amount` 1065.00 |
| FIND-1-2 | 1 | SOURCE-TASK RED | `rebill_amount` rests on a claim of 640.00 against a 268.00 charge, credited on a dispute noticed 53 days outside the 60-day window; applying the base cap the rebill overwrite never supersedes gives 0.00 and an autopay of 1027.00 |

### what does hold

Both tasks' independent derivations reproduced GT **exactly** — every parameter, tool, owner, order,
terminal state, baseline figure and per-factor sensitivity figure, with no discrepancy anywhere. The
charter is self-consistent, all three prerequisite edges are genuinely unmet at the opening and all
three bear weight, every tree carries a customer's own write, and no tool judges a prerequisite. The
three reds are all defects of the seeded worlds against products of this scenario's own blueprint; none
is attributable to a solving agent, and none is a defect of the extended policy text.

---

## revision_2

Re-audit round 2, UTC 2026-09-16 09:51. Revision 1 above is left exactly as written.

### re-derivation grounds

| shared input | round-1 sha256 | round-2 sha256 | moved? |
| --- | --- | --- | --- |
| `card.extended.yaml` | `52c5124d…f4df45` | `52c5124dc141f8797773ff2b39a500859117336ab1cfe1ee1e73c647e4f4df45` | **no** |
| `task_tools.py` | `d326ce40…d7a88792` | `d326ce40b5b1e3893b7d771856f5c5e6077ebf419d73bd1d218598d6d7a88792` | **no** |
| `blueprint/products/card.yaml` | `24ae1354…c638ef78` | `24ae13549122ccbae7d04336dcbc97d7ed134773de02ce3daaaa6896c638ef78` | **no** |

Both shared objects are byte-identical to the round that produced the charter-global section, so
§ `policy_conflict_scan`, § `rule_compute_equivalence`, § `action_binding_and_uuids`,
§ `prerequisite_graph`, § `prerequisite_sentences`, § `override_declarations` and § `factor_ladders`
are **carried forward by reference**, with those two hashes as the grounds. They were not re-derived.
The eight charter-global observations OBS-C1 … OBS-C8 stand unchanged.

All three round-1 reds were seed-versus-charter defects and all three fixes are edits to the seeded
worlds, so everything re-derived this round is per-task. The blueprint products the fixes are judged
against were also re-hashed and are unmoved:
`checking.yaml` `635b57c4…166046`, `savings.yaml` `8f308ff1…0100a40a`, `cd.yaml` `7a14550e…044aa8`.

### rebuilt masked views

Re-hashed against the brief and matching: `0.json` `2f47b371266d206dbdd6cd255478448e312a7da1a6bd195af3a3e8fc9c336e10`,
`1.json` `bf0402a18093aea98d8436547f1ddc5712e1d69637989fa277f3bf68a021d831`. Both carry exactly
`frozen_time`, `user_scenario`, `initial_state`. Both worlds were re-read in full; no round-1 reading
was carried forward unchecked. `frozen_time` is unmoved on both tasks (2026-03-17 10:40:00 EST;
2026-05-21 14:05:00 EDT).

**A caution for anyone re-checking this round against revision 1: task 1's `card_transactions` row ids
were permuted wholesale by the regeneration.** `bd3e87da…` is now a 402.00 dining purchase of
2024-09-18 where in round 1 it was a 1480.00 purchase of 2025-06-14; `93820e2b…` is now the 8400.00
purchase where it was the 268.00 one; `9d3720f2…` is now a merchant credit where it was the 640.00
dispute credit; `21b8bc3f…` is now the 1284.00 purchase where it was the 212.75 one. Every row
identified in revision 1 by id must be re-identified by content. This round did so.

### what actually changed in the two worlds

Established row by row against revision 1's recorded contents, not from the reworker's account.

**Task 0 — one deletion, nothing else.** `checking_transactions` 7 → 6 rows: the
`monthly_maintenance` `checking_fee` of 12.00 posted 2025-09-11 is gone. The six direct deposits of
2180.00 are unchanged in date and amount. `card_transactions` is unchanged at 69 rows (fingerprint of
every (posted_date, event_type, amount, reward_points, fee_code) tuple recomputed; the two
`late_payment` fees of 2024-08-08 and 2026-03-08 and the single reversal of 2024-08-20 naming the
former are all still there). `card_accounts`, `savings_accounts`, `savings_transactions` and
`customers` are unchanged field for field. `user_scenario` is unchanged in substance.

**Task 1 — one addition, one deletion, three repointings, and the arithmetic they imply.**
- `card_transactions` 59 → 61: one new `card_purchase` of **402.00** posted 2024-09-18
  (`statement_date` 2024-10-12, `merchant_category` dining) and its paired `card_rewards_earn` of
  **1206** points. Every other ledger row is unchanged in date, type and amount.
- `checking_transactions` 7 → 6: the `monthly_maintenance` fee of 15.00 posted 2025-11-19 is gone;
  the six deposits of 2460.00 are unchanged.
- all three `card_disputes` rows keep their status, claim and notice date, and all three now name a
  different `disputed_txn_id`; the 640.00 temporary credit's `source_item_id` moved with its dispute.
- `card_accounts` moved only by the consequences of the new purchase: `current_balance`
  7705.92 → 8107.92 (+402.00), `last_statement_balance` 8405.92 → 8807.92 (+402.00),
  `minimum_payment_due` 84.06 → 88.08 (= max(35.00, 1% of 8807.92), recomputed and correct),
  `rewards_balance` 54369 → 55575 (+1206).
- `savings_*`, `cd_*`, `customers` and `user_scenario` unchanged.

Nothing else rode along. This was confirmed twice over: by the row-level comparison above, and by
recomputing **every binding of every one of the five computations** on the new worlds and accounting
for each one that moved.

### the fixes tested on the charter, not accepted on assertion

**The deletion argument (FIND-0-1, FIND-1-3), tested independently.** The reworker argues from a
further clause of `checking_evt_maintenance_and_statement_fees` that no monthly maintenance fee is
assessable on either account at any amount or date. That argument holds:

- Premier Checking's waiver parameters (`blueprint/products/checking.yaml`) are
  `waiver_min_daily_balance 10000.00`, `waiver_direct_deposit_total not_offered`,
  **`waiver_relationship_balance 25000.00`**, `waiver_debit_purchase_count not_offered`,
  `waiver_age_under not_offered`, `waiver_age_at_least not_offered`,
  `waiver_military_active_duty true`, `waiver_employee true`.
- the rule: "The waivers are alternatives and **any single one suffices**… A waiver whose parameter is
  not_offered cannot be used."
- `checking_agg_relationship_balance` / `checking_msr_relationship_balance`: "Sum over the customer's
  holdings of: ledger_balance of each checking account not closed or charged_off …, current_balance of
  each savings account not closed, principal_balance of each certificate not closed"; "For the
  maintenance fee waiver the measurement date is the statement cycle closing date."
- task 0: 6240.18 + 31480.55 = **37720.73** ≥ 25000.00. Task 1: 8904.62 + 46215.80 + 25000.00 =
  **80120.42** ≥ 25000.00. Both clear the threshold by a wide margin at every cycle close in the seeded
  span (working the savings balance backwards through its own deposits and interest credits keeps
  task 0 above 34000 even at the earliest cycle in the window).
- neither customer is `active_duty` or `active_employee`, so the two boolean waivers are irrelevant;
  the relationship-balance waiver alone decides it.
- the paper statement fee is not an alternative source of a `checking_fee` row here: Premier Checking's
  `paper_statement_fee` is 0.00 and both accounts' `statement_delivery` is `electronic`.

So zero `checking_fee` rows is the world the checking charter yields on both accounts, and deleting the
row — rather than re-dating it to the cycle closing date — is the repair the charter actually
supports. Re-dating would have been wrong.

**The reworker's claim that task 0's scored value is unchanged "not because I preserved it but because
that is what the charter-consistent world yields" is verified and correct.** `checking_fees_6m` was 0
in round 1 and is 0 now, but for a different and now legitimate reason: in round 1 a fee row existed
and was excluded only by an arithmetic accident of a `posted_date` the charter forbids; now no such row
can exist at all. The tier `settlement_window_convention` takes is produced by the rule applied to a
charter-consistent world.

### per-item verdicts

| item | round-1 verdict | claim | round-2 verdict |
| --- | --- | --- | --- |
| FIND-0-1 | SOURCE-FACTOR RED | closed by deletion | **CLOSED** |
| FIND-1-1 | SOURCE-FACTOR RED | closed by seeding a new charge; root value moved | **CLOSED** |
| FIND-1-2 | SOURCE-TASK RED | closed by repointing; second reading vanishes | **CLOSED** |
| FIND-1-3 | observation | closed by the same argument as FIND-0-1 | **CLOSED** |
| FIND-0-4 | observation | corrected | **CLOSED** |
| FIND-0-3 | observation | not actionable (a gate requires it) | **claim upheld; observation remains open** |
| FIND-0-2 | observation | recorded, not actioned | **remains open** |
| FIND-1-4 | observation | recorded, not actioned | **remains open** |
| FIND-1-5 | observation | recorded, not actioned | **remains open** |
| OBS-C1 … OBS-C8 | observations | unchanged | **unchanged, still open** |
| — | — | — | **OBS-R2-1 new** (see task files) |

The per-item evidence for FIND-0-1 / FIND-0-2 / FIND-0-3 / FIND-0-4 is in `0.md` § `revision_2`, and
for FIND-1-1 / FIND-1-2 / FIND-1-3 / FIND-1-4 / FIND-1-5 in `1.md` § `revision_2`.

**FIND-0-3, claim tested and upheld.** `skills/erl-task-instantiate/scripts/check_solvability.py`
lines 968–976 hard-fail when `base_preconditions` does not *exactly* match every subject-scoped
eligibility gate of every base policy governing the write subject — `missing=` and `extra=` are both
failures. `retired_gates_of` (line 55) drops a gate only when an `overwrite`'s `superseded_clause`
quotes that gate's condition sentence; `card_ext_late_fee_correction.overwrite` quotes the amount
clause, which is no gate's condition, so all four `card_evt_fee_reversal` gates must be listed. The
task cannot omit the three courtesy gates without failing the gate block. The observation is therefore
**not actionable at the task level** and its proper addressee is the base charter's gate scoping —
`courtesy_count`, `prior_on_time` and `account_open_for_courtesy` carry
`applies_to: [card_fee_reversal]`, which does not distinguish a `courtesy_waiver` reversal from a
`bank_error` one, although the rule sentences that introduce them speak only of courtesy reversals.
It moves no scored value and stays an observation.

### regression sweep

- **Charter:** unmoved (hashes above). No policy, tool, uuid8, prerequisite edge, prerequisite sentence,
  override declaration or factor ladder changed.
- **Scopes:** still pairwise disjoint and jointly complete — `charter_scope.extended_policies` is
  `[card_ext_late_fee_correction, card_ext_rewards_statement_credit]` for task 0 and
  `[card_ext_dispute_provisional_credit, card_ext_dispute_rebill_recovery, card_ext_autopay_fixed_amount]`
  for task 1, exactly as in round 1.
- **Problem trees:** both intact and both still unmet at the opening — task 0's 2026-03-08 late payment
  fee still carries no reversal; task 1's submitted dispute still carries no temporary credit and the
  ledger still holds no `card_dispute_rebill` row at all.
- **Load-bearing edges:** all three still move their root's scored value (task 0: 33000 vs 35000;
  task 1: 1129.00 vs 1275.00 skipping the credit, vs 1087.00 skipping the rebill, vs 1234.00 skipping
  both).
- **Customer's own writes:** both present and unmoved — `redeem_card_points_9bfb7edb` (task 0) and
  `set_card_autopay_amount_b2f02f74` (task 1), both `owner="user"` in the unmoved tool module.
- **Order independence (task 1):** re-verified by running both orders — writing the rebill first still
  yields a provisional credit of 976.00, and writing the credit first still yields a rebill of 276.00.
- **Factors:** all 25 still bear weight on their task's world against the same honest baselines; every
  count still inside 4–6 with ≥2 of each effect, ≥2 multi-source and ≥2 cross-difficulty.
- **Personas:** unchanged in substance on both tasks; each still raises only the root problem, names no
  prerequisite, and closes where `evaluation_criteria` closes.
- **Gate-snapshot movements accounted for:** task 0's replay closure 84 → 83 is the one deleted
  checking row; task 1's 83 → 84 and seed rows 60 → 62 are the one deleted checking row against the two
  added card rows; history depth 98 → 99 is the added card ledger row. Each movement is the claimed
  edit and nothing more.

**No regression found.**

## closing_checklist — revision_2

| item | state |
| --- | --- |
| per-task audit files correspond one-to-one with the tasks, `_difficulty.md` alongside them | yes |
| old revisions traceable | **yes** — revision 1 is preserved verbatim in all three files; revision 2 is appended below it |
| every comparison section carries a PASS | **yes** — `0.md` and `1.md` both PASS on all four relationships in revision 2 |
| extended policies fully covered; scopes pairwise disjoint, each spanning the whole tree | yes |
| task tools and GT closed; each uuid8 independently generated and frozen | yes (charter unmoved) |
| every tree has 1–3 prerequisite problems and ≥ max(n−1,1) `value_input` edges | yes — task 0: 1 problem, 1 edge; task 1: 2 problems, 2 edges |
| at least one problem resolved by an `owner=user` tool; no cycle, including across tasks | yes |
| every computation declares a self-sufficient baseline giving a definite number different from gold | yes — 11.20 vs 23.00; 4144 vs 33000; 898.80 vs 976.00; 480.00 vs 276.00; 3703.96 vs 1129.00 |
| 4–6 factors per computation, ≥2 of each effect, ≥2 multi-source, ≥2 cross-difficulty; every ladder ≥3 tiers stated in full | yes |
| every factor bears weight against an honest baseline, on a world the charter can produce | **yes** — this is what revision 1's two SOURCE-FACTOR reds denied and what the fixes restore |
| every computation retains a genuine near-miss | yes, with one qualification recorded as OBS-R2-1 |
| instantiation-stage gates re-run once on the final form | supplied with the brief and cited; all seven green after the rework. Not re-run by this auditor, per the brief |

### the difficulty closes out

All four relationships now PASS on both tasks:

| relationship | task 0 | task 1 |
| --- | --- | --- |
| policy self-consistency | PASS | PASS |
| the problem tree holds | PASS | PASS |
| factors bear weight | **PASS** (was SOURCE-FACTOR RED) | **PASS** (was SOURCE-FACTOR RED) |
| policy ↔ task unique solution | PASS | **PASS** (was SOURCE-TASK RED) |

**`card_billing_payments_and_disputes` passes the source-layer audit.** Six observations remain open
(OBS-C1 … OBS-C8 charter-global, FIND-0-2, FIND-0-3, FIND-1-4, FIND-1-5 and the new OBS-R2-1); none is
grounds for rework, and each is recorded with the recomputation showing it moves no scored value.
