# Policy-task audit — supplemental_benefit_allowance_desk / charter-global

## charter_global_frozen

- Freeze time: 2026-09-21T13:45+00:00 (written in full before any task's `evaluation_criteria` /
  `computations` / closure fields were opened).
- Auditor: independent source-layer auditor (erl-task-policy-audit), no part in authoring these artifacts.
- Frozen inputs and hashes (sha256[:16]):
  - `env/env_0006_medicare_advantage_plan_sponsor/tasks/supplemental_benefit_allowance_desk/allowance.extended.yaml` = `99fb47acb2fbefc4`
  - `env/env_0006_medicare_advantage_plan_sponsor/tasks/supplemental_benefit_allowance_desk/task_tools.py` = `c42fd880ced790d6`
  - masked view `_masked_views/0.masked.json` = `bf2c0aed945b6580`
  - masked view `_masked_views/1.masked.json` = `8d28a8d06684c1a7`
- Also read: `blueprint/blueprint.yaml`, `blueprint/db_schema.json`, `blueprint/share_tools.py`,
  `blueprint/products/allowance.yaml`, and — for the cross-category reads the charter itself declares —
  `blueprint/products/advantage.yaml` and `blueprint/products/osb.yaml`. `erlbench/` and
  `skills/erl-task-instantiate/scripts/check_compute.py` were read for the exact semantics of the
  restricted compute primitives (`MONTHS`, `DAYS`, `within_months`, `RND`, `LATEST`, `CPARAM`, `XSUM`, `XCOUNT`).
- Fields explicitly masked and not read while this file was written: `evaluation_criteria`,
  `computations` (including `expected`, `factor_trace`, `factor_sensitivity`, `baseline_result`,
  `step`/`arg`), `charter_scope`, `required_documents`, `design_rationale`, `solvability_contract`,
  `prerequisite_closure`, `db_closure`, `db_closure_matches_initial_state`.
- Nothing in this file is derived from a revealed GT. It was complete on disk before either task file was opened.

### Entry conditions (Step 0)

The brief carried the instantiation gate snapshot with actual output lines
(`check_extended`, `check_task_tools`, `replay_tasks`, `check_solvability`, `check_compute`,
`check_grounding`, `check_cross_fire` — all green; `check_traceability` deferred to the render step,
`check_cache_diff` informational). Masked views were supplied with hashes, which match the files on
disk. Entry conditions are complete; the gates were cited, not re-run. A green gate is the
qualification to enter this audit, not evidence that the policy is self-consistent or that it entails
one answer.

### policy_conflict_scan

The base section of `allowance.extended.yaml` (lines 1–1743) is byte-for-byte identical to
`blueprint/products/allowance.yaml` (verified by `diff`; the only addition is the
`# extended_policies` separator comment at lines 1744–1746). The base copy has not been rewritten.

Overlapping-subject scan across the 11 base policies and the 6 extended policies:

| Subject | Base owner | Extended owner | Verdict |
| --- | --- | --- | --- |
| `allowance_program_created` | `allowance_agg_multi_holding`, `allowance_programme_opening`, `allowance_health_plan_tier_interaction` | none | no extended claim; no conflict |
| `allowance_card_activation` | `allowance_card_activation_and_replacement` | `allowance_ext_card_in_use_first_load` | compatible; the extended policy quantifies the first load, the base fixes the window and the member-only act |
| `allowance_quarterly_load` / `allowance_bonus_load` | `allowance_load_schedule`, `allowance_agg_combined_annual_cap` | `allowance_ext_schedule_catch_up_load` (`allowance_bonus_load`) | one declared override, see `override_declarations` |
| `allowance_purchase` | `allowance_eligible_spending` | none | no extended claim |
| `allowance_purchase_refund` | `allowance_purchase_dispute_and_refund` | `allowance_ext_dvh_recovery_credit` | see finding F-2 |
| `allowance_period_expiry` | `allowance_rollover_and_expiry` | `allowance_ext_period_end_expiry` | one declared override |
| `allowance_program_closure` / `allowance_balance_forfeiture` | `allowance_closure_and_forfeiture` | `allowance_ext_closing_balance_forfeiture` | one declared override |
| `allowance_catalog_order_cancelled` | `allowance_catalog_ordering` | `allowance_ext_standing_order_refund` | see finding F-1 (undeclared) |
| `allowance_dormancy_flagged` / `allowance_reactivation` / suspension / release | `allowance_dormancy_and_card_security` | none | no extended claim |

Eligibility gates, time anchors and terminal states carry no mutual contradiction across the base
set: each base gate names a distinct table/field pair, the three `time` gates
(`activation_window_open`, `benefit_period_ended`, `dispute_window_open`, `cancellation_window_open`)
anchor on different events and do not overlap in subject, and the two `dedup` gates
(`no_duplicate_programme`, `card_programmes_mutually_exclusive`) partition by `variant_name` and do
not disagree.

Cross-category read boundaries: the charter declares `osb` and `advantage` reads only, in
`allowance_ext_dvh_recovery_credit` (`osb` history + `advantage` branch),
`allowance_ext_card_in_use_first_load` (`advantage` branch) and
`allowance_ext_schedule_catch_up_load` (`advantage` history). Every declared field exists on the
named table or in the named product's `parameters` (`osb_benefit_claims.rider_paid_amount`,
`.allowed_amount`, `.claim_status`, `.processed_date`; `advantage.dental_allowance_annual`,
`advantage.otc_allowance_quarterly`, `advantage_enrollments.coverage_effective_date`,
`advantage_premium_ledger.event_type`/`.posted_date`). No undeclared category is read in any
`compute`.

Scope exclusivity of the two tasks: the `prerequisite` graph partitions the six extended policies
into exactly two connected components —
{`allowance_ext_closing_balance_forfeiture` ← `allowance_ext_dvh_recovery_credit`,
`allowance_ext_period_end_expiry`, `allowance_ext_standing_order_refund`} and
{`allowance_ext_schedule_catch_up_load` ← `allowance_ext_card_in_use_first_load`}. The components are
vertex-disjoint and jointly cover all six policies and all six task tools, so the two tasks' scopes
(each spanning a whole tree) are pairwise disjoint and jointly complete. PASS.

### rule_compute_equivalence

Check 2, run over every extended policy. For each policy every `compute` binding carries a
`compute_basis` entry, and every `compute_basis` string is a verbatim sentence of that policy's own
`rule` (checked string-by-string). Each declared factor's ladder is stated as a sentence of the
`rule` and implemented as the ternary chain of its `decides` binding, tier for tier, with the
fall-through of the chain equal to the factor's `baseline` — verified for all 29 factors. No tier
appears in one face and not the other.

Two defects found:

1. **`allowance_ext_standing_order_refund` implements elapsed hours as calendar days × 24.**
   The rule promises a deadline "counted from the time it was placed", and the inherited base
   counting rule (`allowance_catalog_ordering` → `cancellation_window_open` → `temporal_basis.counting_rule`)
   says verbatim: *"Hours are counted as full 24-hour periods from the moment the order was placed, a
   request made exactly on the deadline is in time, and **calendar days are never used in place of
   hours**."* The compute is `order_days: "DAYS(LATEST('allowance_catalog_orders','order_date', …) or NOW, NOW)"`
   followed by `order_hours: "order_days * K('hours_in_a_day')"` — hours derived from calendar days,
   which that sentence forbids. `allowance_catalog_orders.order_date` carries a date only
   (`db_schema.json`), so the moment the rule anchors on is not in the record at all. Recorded as
   finding **F-1**; the consequence is demonstrated in `0.md`.
2. **`allowance_ext_card_in_use_first_load` and `allowance_ext_schedule_catch_up_load` have an empty
   `compute_basis`.** Both policies carry `compute_basis:` with no mapping at all (lines 2606 and
   2802 of `allowance.extended.yaml`), while every other extended policy maps each binding to its
   rule sentence. The rule/compute correspondence for 18 of the charter's bindings is therefore
   asserted nowhere. Recorded as finding **F-6** (observation: the bindings do in fact each
   correspond to a rule sentence on inspection, so no second reading follows from it).

Otherwise every quantity, window, filter, tier, branch, cross-category read, acting base, cap/floor,
rounding mode and rounding point has a verbatim `compute_basis` quotation and a restricted
implementation, and the sweep back finds no basis invented in `compute` and no empty promise in a
`rule`.

### action_binding_and_uuids

Six task tools, six extended policies, one `(target_tool, computes)` pair each — no tool and no
`computes` name is claimed twice:

| Policy | `computes` | `target_tool` | owner |
| --- | --- | --- | --- |
| `allowance_ext_dvh_recovery_credit` | `credit_amount` | `post_dispute_credit_634307a6` | agent |
| `allowance_ext_period_end_expiry` | `expiry_amount` | `post_period_expiry_1d3932f1` | agent |
| `allowance_ext_standing_order_refund` | `refund_amount` | `cancel_catalog_order_88277d51` | agent |
| `allowance_ext_closing_balance_forfeiture` | `forfeited_balance` | `close_allowance_programme_5a9eaadb` | user |
| `allowance_ext_card_in_use_first_load` | `first_load_amount` | `activate_allowance_card_a5740baf` | user |
| `allowance_ext_schedule_catch_up_load` | `catch_up_amount` | `post_catch_up_load_838eeda2` | agent |

uuid8s: `634307a6`, `1d3932f1`, `88277d51`, `5a9eaadb`, `a5740baf`, `838eeda2`. All eight
hexadecimal characters, all six pairwise distinct, no shared prefix or suffix, no sequence, no
adjacent values, none a re-tailed copy of another. Independently generated and frozen. PASS.

Docstrings: none names another tool, none states a position in a sequence, none carries "before",
"after" or "first" as an ordering claim about another act. One borderline phrase is recorded as
finding **F-7** (`post_catch_up_load_838eeda2`, `source_ledger_entry_id`: "…or by the confirmation of
the load that created it", which points at the return of a preceding write).

### prerequisite_graph

Check 7 over the whole graph. Four edges are declared, all on two policies; the other four policies
carry `prerequisite: []` explicitly.

| Blocked policy | `problem` | `kind` | `gate` | `form` | `resolved_by` |
| --- | --- | --- | --- | --- | --- |
| `allowance_ext_closing_balance_forfeiture` | `allowance_ext_dvh_recovery_credit` | `value_input` | `ledger_credits` | `state` | `post_dispute_credit_634307a6` |
| `allowance_ext_closing_balance_forfeiture` | `allowance_ext_period_end_expiry` | `value_input` | `already_off` | `state` | `post_period_expiry_1d3932f1` |
| `allowance_ext_closing_balance_forfeiture` | `allowance_ext_standing_order_refund` | `value_input` | `ledger_credits` | `state` | `cancel_catalog_order_88277d51` |
| `allowance_ext_schedule_catch_up_load` | `allowance_ext_card_in_use_first_load` | `value_input` | `loads_made` | `state` | `activate_allowance_card_a5740baf` |

- Every `problem` points at another extended policy id in this file; none points at a base policy or
  at itself. The graph is a DAG (two disjoint trees, no back-edge, no cross-task reference). PASS.
- Every `policy_source` is verbatim locatable in the **blocked** policy's own `rule` — each of the
  four sentences was matched character-for-character inside the `rule` block of
  `allowance_ext_closing_balance_forfeiture` / `allowance_ext_schedule_catch_up_load`. PASS.
- `form: state` on all four; no `fallback_reason` is present on any, which is correct because none is
  action-form. The state form is honoured throughout — no edge takes the action-form fallback, so
  there is no `fallback_reason` to test. PASS.
- `kind: value_input` matches `gate` in all four cases: `ledger_credits`, `already_off` and
  `loads_made` all exist as named bindings in the blocked policy's own `compute`. No `state_gate` is
  declared. PASS.
- `resolved_by` is the depended-on policy's own `target_tool` in all four cases, and each tool's body
  genuinely moves the named binding (`post_dispute_credit` creates an `allowance_purchase_refund`
  row → `ledger_credits`; `post_period_expiry` creates an `allowance_period_expiry` row →
  `expiries_taken` → `already_off`; `cancel_catalog_order` creates an `allowance_purchase_refund`
  row → `ledger_credits`; `activate_allowance_card` creates an `allowance_quarterly_load` row →
  `loads_posted` → `loads_made`). PASS.
- `condition` neither strengthens nor weakens the prerequisite sentence on three of the four edges.
  On the `allowance_ext_period_end_expiry` edge the sentence and the condition quantify over *every*
  allowance whose benefit period has closed, while the depended-on policy computes exactly one dying
  period; recorded as finding **F-5**.
- No authoring-viewpoint phrasing ("in this task", "at the opening", "the current world") appears in
  any `prerequisite` field. PASS.
- One `effect` string misstates the direction of its own edge; recorded as finding **F-8**,
  demonstrated in `1.md`.

### prerequisite_sentences

Check 6, the four-point test on each of the four edges.

**E1 — closure ← dvh recovery credit.** Sentence: *"The balance given up on the closing day is not
fixed until every card transaction the plan has decided in the member's favour carries on the card
the money it owes back."* (1) Ordering connective: "not … until" ✓. (2) State form: what it waits on
is "carries on the card the money it owes back", a credit entry standing against that transaction on
`allowance_card_ledger` — record-visible, no performer, no action verb attributed to anyone ✓, but
the qualifier "the plan has decided in the member's favour" names no field the tables carry
(`allowance_benefit_requests.intake_status` runs `recorded` / `awaiting_member_signature` /
`under_review`, never "decided"); recorded as finding **F-3**. (3) No tool name, policy id,
snake_case token or row id ✓. (4) Strength: the `condition` matches the sentence ✓.
Single-write test: two writes of this difficulty create an `allowance_purchase_refund` row
(`post_dispute_credit_634307a6` and `cancel_catalog_order_88277d51`), but only the first produces a
credit that *names a card transaction*; `cancel_catalog_order` relates to an order. A reader
comparing the two depended-on rules resolves the hop to `allowance_ext_dvh_recovery_credit` in one
reading. Derivation: sentence → "a card transaction carries the money it owes back" → search the
extended rules for the one that puts money back against a transaction → `allowance_ext_dvh_recovery_credit`
("where another payer has since met a cost the card has already paid, the money is put back on the
card") → its own rule gives the amount → `post_dispute_credit_634307a6`. One reading. PASS with F-3.

**E2 — closure ← period-end expiry.** Sentence: *"The balance given up on the closing day is worked
out only after every allowance whose benefit period has closed stands taken back on the card."*
(1) "only after" ✓. (2) "stands taken back on the card" = an `allowance_period_expiry` entry on the
ledger, record-visible, no performer ✓. (3) no tool/id/token ✓. (4) The sentence and `condition` are
strictly broader than what the depended-on policy computes — finding **F-5**. Single-write test:
`post_period_expiry_1d3932f1` is the only write in this difficulty producing an
`allowance_period_expiry` row ✓. Derivation: sentence → "an allowance taken back" → the only extended
rule about taking an allowance back at period end → `allowance_ext_period_end_expiry` →
`post_period_expiry_1d3932f1`. One reading. PASS with F-5.

**E3 — closure ← standing catalogue order.** Sentence: *"The balance given up on the closing day is
not worked out before the card shows no catalogue order left standing to be sent."* (1) "not …
before" ✓. (2) "no catalogue order left standing to be sent" = `allowance_catalog_orders.order_status`
at `placed`, record-visible, in the tables' own words ✓. (3) clean ✓. (4) matches `condition` ✓.
Single-write test: `cancel_catalog_order_88277d51` is the only write that moves an order off
`placed`; this difficulty has no despatch write ✓. One reading. PASS.

**E4 — catch-up ← card in use.** Sentence: *"The allowance owed for the benefit periods already gone
is not made available before the card stands in use on the programme record."* (1) "not … before" ✓.
(2) "the card stands in use on the programme record" = `allowance_programs.status` at `active` with
`card_activated_date` set, record-visible ✓. (3) clean ✓. (4) `condition` ("The programme record
shows the card in use, carrying the day the member brought it into use") matches ✓. Single-write
test: `activate_allowance_card_a5740baf` is the only write of this difficulty that sets
`card_activated_date`; `post_period_expiry` and the credits do not touch programme status. ✓
One reading. PASS.

No blocked rule carries a second wording of its own dependency, no other problem's tool name, policy
id or route, and no aggregated chain. The depended-on rules do not restate the blocked sentence
(checked: neither `allowance_ext_dvh_recovery_credit`, `allowance_ext_period_end_expiry`,
`allowance_ext_standing_order_refund` nor `allowance_ext_card_in_use_first_load` mentions closure or
catch-up). No base rule states a cross-problem order that grounds one of these edges. PASS.

### override_declarations

Check 1's finding half, once over all six extended policies, sentence by sentence against each
`base_policy_refs` entry.

- **`allowance_ext_dvh_recovery_credit`** (`overwrite: []`; refs `allowance_purchase_dispute_and_refund`,
  `allowance_health_plan_tier_interaction`). Base sentence by sentence: the dispute window sentence,
  the "only the member may say that a purchase was not theirs" sentence, the provisional-credit and
  resolution-days sentences, "A retailer's own refund … is not a dispute", and "A refund always goes
  back to the card it was spent from and into the benefit period the purchase belonged to" — the
  extended policy follows the last of these verbatim in its own words and is silent on the rest,
  which are inherited. `allowance_health_plan_tier_interaction`'s "A member who holds an optional
  supplemental benefit rider may use the card toward what the rider did not pay … but never toward a
  cost the rider has already met" is the quantity the extended policy implements. One residual
  exposure is recorded as finding **F-2**: the extended lookback ladder can reach four whole months
  while the inherited `dispute_window_open` gate caps a credit at the tier's dispute window
  (60/75/90 days), so on a tier whose window is shorter than the lookback the two clauses can select
  different sets of chargeable transactions. `overwrite: []` is defensible only because no tier makes
  that reachable: the four-month tier requires a 90-day window and the three-month tier a 75-day
  window, so the lookback never outruns the window by more than a few days. No task in this
  difficulty puts a transaction in that gap (checked in both task files), so no consequence is
  demonstrable and F-2 is an observation.
- **`allowance_ext_period_end_expiry`** (one declared `overwrite` on `allowance_rollover_and_expiry`).
  The superseded clause is quoted verbatim from the base rule and the replacement is stated. The
  remaining base sentences — the expiry-day counting rule, "Money is always spent oldest load first",
  "Nothing carries past the last day of the benefit year on any tier", the correcting-load rule — are
  untouched and inherited. The extended ladder adds a condition the base does not carry ("the member
  made at least one settled purchase from the card in that period" gating rollover); it sits inside
  the clause the `overwrite` supersedes, so it is declared. Observation **F-9** on whether that
  condition is one the line of business weighs.
- **`allowance_ext_standing_order_refund`** (`overwrite: []`; ref `allowance_catalog_ordering`). Two
  base sentences are handled differently by the extended policy and neither is named in `overwrite`:
  (a) *"After that deadline the order may still be cancelled while it has not shipped, but the
  delivery charge is not returned, because the plan has already paid for the despatch"* versus the
  extended ladder's second tier, which returns the tier's standard delivery charge after the
  deadline on a standard-service order — finding **F-4**; (b) the elapsed-hours counting rule versus
  `order_hours = order_days * 24` — finding **F-1**.
- **`allowance_ext_closing_balance_forfeiture`** (one declared `overwrite` on
  `allowance_closure_and_forfeiture`). The superseded clause is quoted verbatim and replaced; the
  reserve for unsettled transactions that the replacement introduces is the machine face of the base
  sentence "Purchases made before the closing day are honoured even where they settle after it", so
  the two agree rather than conflict. Remaining base sentences (closure authority, no cash payout, the
  correcting load for an erroneous closure) are inherited untouched. No undeclared override.
- **`allowance_ext_card_in_use_first_load`** (`overwrite: []`; ref
  `allowance_card_activation_and_replacement`). The base sentences govern the activation window, the
  member-only act, the replacement fee and the statement-delivery change; none fixes a first-load
  amount, so the extended policy adds a quantity rather than overriding one. The base sentence "the
  allowance itself is never lost for want of activation" is consistent with the catch-up policy. No
  undeclared override.
- **`allowance_ext_schedule_catch_up_load`** (one declared `overwrite` on `allowance_load_schedule`;
  ref also `allowance_agg_combined_annual_cap`). The superseded clause is quoted verbatim and
  replaced. Base's "A member whose profile carries a qualifying chronic condition takes the tier's
  chronic condition bonus once in the benefit year" and "No load is made after the programme has
  closed" are inherited untouched. Against `allowance_agg_combined_annual_cap`, the extended ceiling
  is the tier's own `annual_allowance_amount`, which is at or below the combined cap of 1400.0 on
  every tier, so the base cap is never breached. No undeclared override.

The three disguised forms were searched for specifically. **The anonymous intermediate factor is
present** — F-1 is exactly that shape: the deviation lives in the intermediate `order_hours` with no
new parameter name. No 0/1 multiplier was found on an amount base. No dropped branch was found: for
every base branch (rollover permitted / not, prorating / whole-period, activation required / not) the
extended selectors can produce both sides on some tier.

### factor_ladders

Structure only; weight is per task.

| Policy | factors | `parameter` | `method` | multi-source tiers | `cross_difficulty` |
| --- | --- | --- | --- | --- | --- |
| `allowance_ext_dvh_recovery_credit` | 5 | 2 | 3 | `recovery_lookback`, `recovery_other_payer`, `recovery_member_share` | `osb` ×2 |
| `allowance_ext_period_end_expiry` | 6 | 2 | 4 | `expiry_period_count`, `expiry_allowance_life`, `expiry_carry_base`, `expiry_carry_share` | none |
| `allowance_ext_standing_order_refund` | 4 | 3 | 1 | `order_items_read`, `order_delivery_charge` | none |
| `allowance_ext_closing_balance_forfeiture` | 4 | 2 | 2 | `closing_standing_balance_basis`, `closing_unsettled_reserve` | none |
| `allowance_ext_card_in_use_first_load` | 4 | 2 | 2 | `first_load_period_allowance`, `first_load_share_basis`, `first_load_ceiling` | `advantage` ×1 |
| `allowance_ext_schedule_catch_up_load` | 6 | 3 | 3 | `catch_up_periods_counted`, `catch_up_year_ceiling` | `advantage` ×3 |

Every policy declares 4 to 6 factors with at least 2 `parameter` and at least 1 `method`. Every
ladder has exactly three tiers, the fall-through counted, and the tiers of each ladder are pairwise
disjoint as stated (checked by reading each ternary chain: the second tier is evaluated only when the
first is false, and the stated conditions of the first two tiers are mutually exclusive in each case
— `>= 90` before `>= 75`, "carries a refused transaction" before "carries no refused transaction",
`forfeits_taken > 0` gated behind `forfeits_taken == 0`, and so on). Every tier's condition and
outcome is stated in the policy's own `rule` and implemented in `compute`; no tier lives only in
`compute`, and no compute branch is missing from the rule. `decides` is an input binding in every
case, never `result`. Binding sets are disjoint across the factors of each policy.

Effect labels are honest: every `method` tier selects a different way of computing the quantity
(which window, which rows are counted, which anchor, which base the share is measured on), and every
`parameter` tier selects a figure. `closing_day_anchor` is labelled `method` and selects which date
anchors the balance — an anchor choice, which the charter's own families treat as a method rather
than a number. Each `method` tier names a rule the charter states.

**Two structural defects in the ladders are recorded here.**

- **F-10 — five of the six baselines are degenerate.** A policy's `baseline` must be a complete
  standard method from which a reader computes a definite number with no factor applied. In five of
  the six policies the baseline sets the dominant term of the final quantity to nothing, so the
  number it yields is **0.00 on every world**, independent of the records, and each rule reads that
  zero as *not performing the scored write at all*:

  | Policy | Baseline sentence that collapses the result | Rule's reading of 0.00 |
  | --- | --- | --- |
  | `allowance_ext_dvh_recovery_credit` | "What the member was left to bear is taken as the whole of what the card was charged at those providers." | "where it comes to nothing no entry is made" |
  | `allowance_ext_period_end_expiry` | "The benefit periods of the benefit year are counted as a single period, so that none has passed by the time the amount taken back is worked out." | no period is dying, nothing is taken back |
  | `allowance_ext_standing_order_refund` | "The value of the items is taken as nothing. … The ceiling on what may go back is taken as nothing." | "where it comes to nothing no order is stopped" |
  | `allowance_ext_card_in_use_first_load` | "The allowance a benefit period carries is taken as nothing. The share … is taken as nothing. The ceiling … is taken as nothing." | "where it comes to nothing no load is made" |
  | `allowance_ext_schedule_catch_up_load` | "The ceiling on the benefit year is taken as what has already been made available, so that nothing further is owed." | nothing further is owed |

  Each is a straw man of the kind the standard names — a zero where the standard method plainly
  gives a figure. An allowance card's standard first load is the tier's `quarterly_allowance_amount`
  (a number the charter publishes for all six tiers); a cancelled catalogue order's standard refund
  is the order's own `order_total` (a field the order record carries); a period-end expiry policy
  whose baseline asserts that no benefit period has passed denies its own trigger. Only
  `allowance_ext_closing_balance_forfeiture` has an honest baseline ("What is still standing on the
  card is taken as the balance the card record shows"), which yields a record-dependent figure.
  Consequences are demonstrated per task in `0.md` and `1.md`.

- **F-11 — `baseline.params` names keys the `baseline.rule` does not use.** In all six policies
  `baseline.params` lists the parameters the *factors* read rather than the defaults the baseline
  method needs. Worked examples: `allowance_ext_standing_order_refund` lists
  `[hours_in_a_day, catalog_shipping_fee, expedited_shipping_fee, catalog_cancellation_window_hours]`
  while its baseline says in terms "The delivery charge the order carried is taken as nothing, and no
  part of a delivery charge is returned", so it reads none of the three fee/window parameters and
  never compares against a deadline; `allowance_ext_period_end_expiry` lists six keys
  (`quarter_months`, `month_months`, `year_months`, `rollover_cap_percent`, `rollover_permitted`,
  `benefit_period_basis`) while its baseline counts the year as one period and carries nothing
  forward, reading none of them. The default keys a reader would need are therefore not the ones
  `baseline.params` names.

- **F-12 — fall-through tiers that fire for customers the business does serve, with an outcome no
  such business gives.** Three fall-throughs are reachable by ordinary customers and pay them
  nothing:
  - `first_load_share_basis` (`allowance_ext_card_in_use_first_load`): tier 1 requires
    `prorates_first_load and months_into_opening_period >= 1`, tier 2 requires `not prorates_first_load`.
    A member on a prorating tier (Plus, Premier, Dual Complete, Chronic Care Plus) whose programme
    opens on the first day of a benefit period has `months_into_opening_period == 0` and falls
    through to "no share is owed" — a first load of 0.00 for the member who joined on the very first
    day of the quarter, who is precisely the member entitled to the whole period load.
  - `first_load_period_allowance` fall-through ("the card hangs on no medical plan in force →
    nothing") and `first_load_ceiling` fall-through (`annual_allowance_amount <= 0` → "nothing"):
    neither condition can hold of any customer who reaches this write, because base
    `allowance_programme_opening` forbids a programme without an in-force medical plan and all six
    card tiers publish an `annual_allowance_amount` of 180.0 or more. They restate the policy's scope
    rather than dividing its customers, and both are the baseline the factor is measured against.
  - `order_charge_ceiling` fall-through ("the catalogue has taken no transaction from the card →
    nothing"): a member who cancels within the window before the catalogue transaction has settled
    gets a ceiling of 0.00 and therefore nothing back, against base's own "every penny, including the
    delivery charge, goes back on the card".

- **F-13 — `order_delivery_returned` tiers 2 and 3 select the same value on four of the six tiers.**
  Tier 2 is "the standard delivery charge the card's tier makes", tier 3 is "no part of the delivery
  charge". `catalog_shipping_fee` is 0.0 on Plus, Premier, Dual Complete and Chronic Care Plus, so on
  those four tiers the two outcomes are identical and the ladder has two distinct outcomes rather
  than three. (On Core, 4.95, and Select, 3.95, they differ.)

### findings

Each finding names the tasks it bears on; those task files carry the demonstration.

**F-1 — `SOURCE-POLICY RED` — elapsed hours computed from calendar days.** *Symptom:* a
cancellation deadline the charter defines in hours is evaluated from a date-only field.
*Root cause:* `allowance_ext_standing_order_refund.compute` derives `order_hours` from
`DAYS(order_date, NOW) * 24`, while the inherited base counting rule forbids exactly that and
`allowance_catalog_orders.order_date` carries no time of day. *Evidence:* base
`allowance_catalog_ordering` → `cancellation_window_open` → `temporal_basis.counting_rule`:
"Hours are counted as full 24-hour periods from the moment the order was placed … and calendar days
are never used in place of hours"; extended compute bindings `order_days` and `order_hours`;
`overwrite: []`. *Consequence:* demonstrated in `0.md` — two defensible refunds (56.45 and 46.50) and
two defensible closing forfeitures (189.10 and 179.15). *Artifact:* `allowance.extended.yaml`
`allowance_ext_standing_order_refund` (`compute`, `overwrite`). *Bears on:* task 0.

**F-2 — observation — extended lookback may outrun the inherited dispute window.** *Symptom:* a
credit computed over a four-month stretch is gated by a base rule that caps a credit at the tier's
dispute window. *Evidence:* base `dispute_window_open` condition vs
`allowance_ext_dvh_recovery_credit` `lookback_long_months: 4`; `overwrite: []`. *Consequence:* not
demonstrable — the ladder pairs the four-month tier with a 90-day window and the three-month tier
with a 75-day window, and neither task seeds a transaction in the gap. *Bears on:* neither task's
score.

**F-3 — observation — "the plan has decided in the member's favour" is not a record-visible state.**
*Symptom:* the E1 prerequisite sentence identifies the waited-on transactions by a status no table
carries. *Evidence:* `allowance_benefit_requests.intake_status` in `db_schema.json` takes `recorded`,
`awaiting_member_signature`, `under_review`; the extended rule of the depended-on policy never uses
the words "decided in the member's favour", framing the credit instead as "where another payer has
since met a cost the card has already paid". *Consequence:* the hop still resolves in one reading via
the depended-on rule, so no second answer follows; the reader must cross to a policy whose own
vocabulary differs from the sentence that points at it. *Bears on:* task 0.

**F-4 — observation — undeclared deviation on the post-deadline delivery charge.** *Symptom:* base
says the delivery charge is not returned after the deadline; extended returns the tier's standard
delivery charge after the deadline on a standard-service order. *Evidence:* base
`allowance_catalog_ordering` rule, sentence 5; `allowance_ext_standing_order_refund` rule, the
`order_delivery_returned` ladder tier 2; `overwrite: []`. *Consequence:* not demonstrable in this
difficulty — task 0's tier (Plus) has `catalog_shipping_fee: 0.0`, so both readings give 0.00, and
task 1 has no catalogue order. *Bears on:* task 0 (no scored difference).

**F-5 — observation — the expiry prerequisite quantifies more broadly than the policy computes.**
*Symptom:* "every allowance whose benefit period has closed" versus a computation that identifies
exactly one dying period. *Evidence:* E2 `policy_source` and `condition`;
`allowance_ext_period_end_expiry` `dying_index: "current_index - life_periods - 1"`. *Consequence:*
demonstrated in `0.md` — on task 0's world the second closed period's expiry computes to 0.00, so the
broader reading adds no scored write; the sentence and the computation nonetheless do not agree in
general. *Bears on:* task 0.

**F-6 — observation — two extended policies carry an empty `compute_basis`.** *Evidence:*
`allowance_ext_card_in_use_first_load` and `allowance_ext_schedule_catch_up_load`, `compute_basis:`
with no mapping. *Consequence:* the two-way correspondence is asserted for none of their 18 bindings;
on inspection each binding does correspond to a rule sentence, so no second reading follows.
*Bears on:* task 1.

**F-7 — observation — a docstring points at the return of a preceding write.** *Evidence:*
`post_catch_up_load_838eeda2`, `source_ledger_entry_id`: "as it is returned by a lookup of that
card's own entries **or by the confirmation of the load that created it**". *Consequence:* it names
no tool and states no order in words, but it tells a reader that a load-creating call may already
have happened in this call, which is the very ordering task 1's single prerequisite edge exists to
make the agent derive. *Bears on:* task 1.

**F-8 — observation — an edge's declared `effect` misstates its own direction.** *Evidence:* E4
`effect`: "What has already been made available rises …, and the last benefit period that has fallen
due becomes the current one, lowering the allowance still owed." *Consequence:* demonstrated in
`1.md` — resolving the prerequisite moves the catch-up from 0.00 to 408.34, i.e. raises it. Recorded
as an observation rather than a red light because the clause admits a narrow reading in which
"lowering" attaches only to the first conjunct, which is true of that term taken alone.
*Bears on:* task 1.

**F-9 — observation — rollover conditioned on having made a purchase.** *Evidence:*
`expiry_carry_share` tiers 1 and 2 both require "the member made at least one settled purchase from
the card in that period", a condition base `allowance_rollover_and_expiry` does not carry.
*Consequence:* a Plus member who spends nothing in a period loses the whole allowance while one who
spends a penny carries half of it; the condition sits inside the declared `overwrite`, so it is
declared, but whether a Medicare plan conditions rollover on card use is doubtful.
*Bears on:* task 0.

**F-10 — `SOURCE-FACTOR RED` — five of six baselines are degenerate straw men.** Detail and table in
`factor_ladders` above. *Consequence:* demonstrated per task in `0.md` (three computations whose whole
baseline is 0.00, each of which the rule reads as "make no entry") and `1.md` (both computations).
*Bears on:* both tasks.

**F-11 — observation — `baseline.params` names keys the baseline does not read.** Detail in
`factor_ladders`. *Bears on:* both tasks.

**F-12 — `SOURCE-FACTOR RED` — unreal fall-through tiers.** Detail in `factor_ladders`.
*Consequence:* `first_load_period_allowance` and `first_load_ceiling` have fall-throughs that no
customer reaching that write can satisfy, so the factor divides nothing and its ladder is exercised
only against the unreachable default; `first_load_share_basis`'s fall-through fires for a real
customer (a prorating tier opening on a period's first day) and pays them nothing.
*Bears on:* task 1.

**F-13 — observation — `order_delivery_returned` collapses to two outcomes on four of six tiers.**
Detail in `factor_ladders`. *Bears on:* task 0 (Plus, where tiers 2 and 3 coincide at 0.00).

## closing_checklist

Written after both tasks' GT was revealed and both comparison sections were complete
(2026-09-21T14:14+00:00). This section is the only part of this file reached after a reveal; the
charter-global section above was complete on disk beforehand and has not been touched since.

**The difficulty does not close out.** Closing requires policy self-consistency, the problem tree,
the factors' weight and the unique solution all to PASS on every task. Of the eight verdicts —
four relationships on each of the two tasks — **two pass and six are red**: task 0 passes on the
problem tree alone, task 1 on policy self-consistency alone. Both tasks are red on the factors and
on the unique solution.

| | task 0 | task 1 |
| --- | --- | --- |
| Policy self-consistency | **`SOURCE-POLICY RED`** (T0-1 / F-1) | PASS |
| The problem tree holds | PASS | **`SOURCE-CHAIN RED`** (T1-1) |
| Factors bear weight | **`SOURCE-FACTOR RED`** (T0-2, T0-3) | **`SOURCE-FACTOR RED`** (T1-3, T1-4) |
| Unique solution | **`SOURCE-TASK RED`** on `refund_amount` / `forfeited_balance` (T0-1) | **`SOURCE-TASK RED`** on the catch-up's `benefit_period` (T1-2) |

Blocking items, one line each:

1. **T0-1 / F-1** — `allowance_ext_standing_order_refund` computes elapsed hours as calendar days ×
   24, which the inherited base counting rule forbids in terms, against a date-only `order_date`:
   `refund_amount` is 56.45 or 46.50 and `forfeited_balance` 189.10 or 179.15.
2. **T0-2** — `osb_benefit_claims["68a3f885-…"]` pays 220.00 of a 240.00 basic-restorative claim on a
   rider whose own charter caps it at 0.80 × (240.00 − 50.00) = 152.00; on charter-consistent figures
   the scored credit is 7.00, not 75.00.
3. **T1-1** — task 1's caller asks for the prerequisite outright in his opening sentence, so the one
   edge the tree exists to test is not discovered from the policy.
4. **T1-2** — no sentence of the charter fixes the benefit period the catch-up load is placed in;
   GT's uniqueness argument quotes a principle that appears nowhere in the charter, and the other two
   period-carrying writes of this very difficulty follow the opposite convention.
5. **T1-3 / F-12** — task 1's only cross-difficulty factor on the first-load computation has two
   reachable tiers that both select 175.00 on this world and a fall-through no customer reaching that
   write can be on; forcing the card's own tier gives 58.33, identical to gold.
6. **F-10 / T0-3 / T1-4** — five of the six extended policies carry a baseline whose result is a
   constant 0.00 on every world, which each policy's own rule reads as an instruction to make no
   entry, and which the tools reject as a non-positive amount.
7. **T0-4 / T1-4** — three of this difficulty's six computations carry no near-miss record
   (task 0's `refund_amount`; both of task 1's).

**The items that do pass, recorded for the next revision.**

- The per-task audit files correspond one-to-one with `tasks/0.json` and `tasks/1.json`;
  `_difficulty.md` sits alongside them; this is revision 1, so there is no older revision to trace.
  Both comparison sections are written and both carry an explicit verdict.
- Coverage and exclusivity: the two tasks' `charter_scope` entries, read after the reveal, are
  exactly the two components this file derived from the `prerequisite` graph before the reveal —
  task 0 claims `{dvh_recovery_credit, period_end_expiry, standing_order_refund,
  closing_balance_forfeiture}` with their four tools, task 1 claims
  `{card_in_use_first_load, schedule_catch_up_load}` with their two. Pairwise disjoint, jointly
  complete over all six extended policies and all six task tools, each scope spanning a whole tree.
- Task tools and GT are closed: every write GT calls exists in `task_tools.py`, every argument it
  passes is either a seeded row's field, a tier parameter, a value the persona states, or the return
  of a preceding gold write (`alw_f202f25395d1` in task 1). Each tool's uuid8 is independently
  generated and frozen — `634307a6`, `1d3932f1`, `88277d51`, `5a9eaadb`, `a5740baf`, `838eeda2`.
- Problem trees: task 0 has three prerequisite problems and three `value_input` edges (floor 2);
  task 1 has one and one (floor 1). Both have at least one problem resolved by an `owner=user` tool
  (`close_allowance_programme_5a9eaadb`; `activate_allowance_card_a5740baf`). No cycle in either, and
  the difficulty's four edges together remain a DAG with no cross-task reference.
- Every computation declares 4 to 6 factors with at least 2 `parameter` and 1 `method`, every ladder
  has three tiers stated in full in its rule, and **every one of the 29 factors bears weight against
  its declared baseline on its task's world** — verified by independent recomputation, and every
  figure agrees with the task files' own `factor_sensitivity` and `baseline_result` (19 factors and
  four baselines on task 0, ten factors and two baselines on task 1). What fails is not the weight
  test but the honesty of the baselines (F-10), the reality of some fall-throughs (F-12) and the
  absence of near-misses.
- Both independent derivations reproduced GT exactly on every scored amount, object, owner, order and
  terminal state — 75.00 / 62.65 / 56.45 / 189.10 and 58.33 / 408.34 — with the single exception of
  the catch-up's `benefit_period`, which this audit could not entail from the charter at all (T1-2).
  The red lights above are defects of the artifacts, not disagreements about the answer.

**Instantiation-stage gates re-run on the final form (2026-09-21T14:13+00:00, artifacts unchanged
since the freeze):** `check_extended` EXTENDED OK; `check_task_tools` TASK TOOL CONTRACT OK;
`replay_tasks` REPLAY OK (0.json 17 acts / 25 rows / match True; 1.json 10 acts / 14 rows / match
True); `check_solvability` SOLVABILITY OK; `check_compute` COMPUTE OK (branches 46.00, steps 13.50);
`check_grounding` GROUNDING OK; `check_cross_fire` SCOPE OK. `check_traceability` still cannot run —
it reads the published KB, which the render step produces later. Every gate is green, and every red
light above sits in the space no gate inspects.

### write-domain disclosure

This audit's own writes are the three files in
`env/env_0006_medicare_advantage_plan_sponsor/audits/policy_task/supplemental_benefit_allowance_desk/`
and nothing else. One side effect must be recorded: `replay_tasks.py` is not a read-only gate — at
line 303 it rewrites the task JSON it replays
(`open(tp, "w").write(json.dumps(rebuilt, …))`). Running it as Step 4 requires therefore rewrote
`tasks/supplemental_benefit_allowance_desk/tasks/0.json` and `1.json`. The rewrite was checked: the
two files come back byte-different but **semantically identical** — the same top-level keys and,
inside `db_closure`, the same row set with the same field values, differing only in the order the
rows are serialised in. Verified by comparing both files parsed and normalised with `sort_keys`:
no key and no value differs. The frozen charter hashes are unchanged after the run —
`allowance.extended.yaml` = `99fb47acb2fbefc4`, `task_tools.py` = `c42fd880ced790d6` — so every
conclusion above stands against the artifacts as frozen. No blueprint, task, skill or `erlbench`
file was edited by this auditor.

---

# revision_2

Revision 1 above is preserved unaltered. This revision re-derives the charter-global section **in
full**, because every source hash moved.

## charter_global_frozen (revision 2)

- Freeze time: 2026-09-21T14:41+00:00, written before either reworked task file was opened.
- Auditor: the same independent source-layer auditor as revision 1.
- Carry-forward rule applied and **declined**: both shared inputs changed, so nothing is carried by
  reference and every charter-global check below is re-derived.

| artifact | revision 1 | revision 2 |
| --- | --- | --- |
| `allowance.extended.yaml` | `99fb47acb2fbefc4` | `0d6c248b2469e392` — CHANGED (2930 → 3538 lines) |
| `task_tools.py` | `c42fd880ced790d6` | `bdab0227bf9b9260` — CHANGED |
| `_masked_views/0.masked.json` | `bf2c0aed945b6580` | `5da8ae7f52d00552` — CHANGED |
| `_masked_views/1.masked.json` | `8d28a8d06684c1a7` | `669e6e494cd6fe49` — CHANGED |

- **Not a blind audit, and not presented as one.** This auditor saw revision 1's GT. The round-2
  derivations were nevertheless produced from the charter and the masked worlds alone, and frozen to
  disk before either reworked `tasks/*.json` was opened; the values are new on both tasks, so no
  round-1 figure could stand in for one. Where a round-2 conclusion could have been steered by
  knowing round-1 GT, it is marked.
- Fields masked and not read while this section was written: the same list as revision 1.

### policy_conflict_scan (revision 2)

Base copy re-diffed against `blueprint/products/allowance.yaml`: still **byte-for-byte identical**
over lines 1–1743, the only addition being the `# extended_policies` separator. The base has not been
rewritten.

Same six extended policies, same six task tools, same two-component `prerequisite` graph, so the
scope partition of revision 1 stands: task 0's tree {`dvh_recovery_credit`, `period_end_expiry`,
`standing_order_refund`} → `closing_balance_forfeiture`, task 1's {`card_in_use_first_load`} →
`schedule_catch_up_load`. Pairwise disjoint, jointly complete. PASS.

Subject overlap re-checked across all 17 policies: unchanged from revision 1 and still free of
mutual contradiction. The `overwrite` count rose from 3 to 6.

### rule_compute_equivalence (revision 2)

Re-run over all six policies, binding by binding.

- **Every binding now carries a `compute_basis` entry** — 17/17, 27/27, 13/13, 21/21, 16/16, 25/25 —
  and **every `compute_basis` string is verbatim present in its own policy's `rule`** (checked by
  string containment after whitespace normalisation). **F-6 is closed**: the two policies that
  carried an empty `compute_basis` in revision 1 now map all 41 of their bindings.
- Every `baseline.rule` sentence is present in the policy's `rule` (checked sentence by sentence
  across all six; no misses).
- Two defects remain or are new:

**N-2 (new) — a cross-category field declared but never read, and a tier condition the compute does
not test.** `allowance_ext_schedule_catch_up_load.cross_category` declares
`advantage.coverage_end_date`, and its `note` says the plan's ended cover decides the ceiling tier.
No binding of that policy reads it: the only `advantage` reads are
`CFIELD('advantage','coverage_effective_date')`, `CPARAM('advantage','otc_allowance_quarterly')`,
`EXISTS('advantage', status='active')` and `XCOUNT('advantage','advantage_premium_ledger', …)`. The
ladder states tier 2 of `catch_up_year_ceiling` as "the card's tier sets a yearly allowance and the
medical plan carrying the card **has ended part way through the benefit year**", but `year_ceiling`
implements that branch as the `else` of `plan_in_force` together with `plan_charged_months >= 1` —
so a plan that is merely not `active` for any other reason takes the tier without its cover having
ended, and a plan whose cover ended is recognised only through not being active. The sibling policy
`allowance_ext_card_in_use_first_load` **does** wire the same field in
(`plan_end_day: CFIELD('advantage','coverage_end_date')`, used in `period_allowance`'s second tier),
which is what shows this to be a declaration left behind rather than a deliberate omission. This is
the field-level gap the brief's first lead predicted: `check_extended` prints "cross-category reads
declared exactly" and PASSES. Not demonstrable on either task's world (both plans are `active`, so
tier 1 is taken) — recorded as an **observation**.

**N-1 (new) — a dead binding carrying a factor's declared evidence.** In
`allowance_ext_period_end_expiry`, `carry_base` is
`period_loads if (period_load_count >= 1 and period_settled >= period_loads / 2) else (unspent if (period_load_count >= 1 and period_purchase_count >= 0) else 0.0)`.
`period_purchase_count` is a `COUNT`, so `period_purchase_count >= 0` is **true on every world**; the
conjunct can never be false and the rule states no condition corresponding to it. Yet the factor
`expiry_carry_base` declares `bindings: [period_purchase_count, carry_base]` — naming as its sole
evidence the one quantity that decides nothing, and naming none of `period_load_count`,
`period_settled` or `period_loads`, which are what its two stated tiers actually rest on. Verified by
substitution: forcing `period_purchase_count` to 0, 1, 5 and 999 leaves the scored expiry at
**53.65** in every case. Revision 1's binding for this factor was `period_transactions`, used in a
real test (`period_transactions >= 1`); the rework replaced the condition with `period_load_count`
and left the old binding slot filled by a tautology. This is the brief's second lead exactly.
No number is wrong as a result — recorded as an **observation**, with the note that the factor's
declared machine face misdescribes what its tier rests on.

### action_binding_and_uuids (revision 2)

Six policies, six tools, one `(target_tool, computes)` pair each; no tool and no `computes` name
claimed twice. uuid8s unchanged and re-checked: `634307a6`, `1d3932f1`, `88277d51`, `5a9eaadb`,
`a5740baf`, `838eeda2` — eight hex characters each, pairwise distinct, no shared prefix or tail, no
sequence. PASS.

Tool bodies re-read in full: not one of the six inspects programme status, order status, ledger
history or an intake before acting, and not one returns an error or a hint. The tool layer still
judges no prerequisite. PASS.

**F-7 is closed.** `post_catch_up_load_838eeda2`'s `source_ledger_entry_id` now reads "as it is
returned by a lookup of that card's own entries" — the clause "or by the confirmation of the load
that created it", which pointed at a preceding write's return, is gone. No docstring names another
tool, states a position in a sequence, or carries an ordering word as a claim about another act.

### prerequisite_graph and prerequisite_sentences (revision 2)

Same four edges, same kinds, gates, forms and `resolved_by`. Graph still acyclic, still two disjoint
trees, still no cross-task reference. All four `policy_source` strings re-checked **verbatim against
the blocked policy's own `rule`** — all four locate. No depended-on rule restates its blocked
sentence. `form: state` on all four with no `fallback_reason`, correctly.

Two sentences were rewritten, and both round-1 findings against them are closed:

**F-3 closed.** E1 now reads: *"The balance given up on the closing day is not fixed until every card
transaction **at a dental, vision or hearing provider that the member's other cover has since paid
its part of** carries on the card the money it owes back."* The old qualifier "the plan has decided
in the member's favour" — a status no table carries — is gone. The new one names two things the
records do carry: the transaction's `merchant_category` and the rider's own paid claim. It also
separates the hop cleanly from `cancel_catalog_order_88277d51`, whose credit relates to an order and
not to a card transaction at a provider. Single-write test passes; the derivation has one reading.

**F-5 closed.** E2 now reads: *"…worked out only after **the allowance of the benefit period whose
life has ended** stands taken back on the card."* Singular, and it matches what the depended-on
policy computes — exactly one dying period. The round-1 mismatch between a universal quantifier and a
single-period computation is gone.

**F-8 closed.** E4's `effect` now ends "…so that the allowance still owed **rises** from nothing to
what the schedule owed less that first load", which agrees with the recomputation (0.00 → 583.34).

### override_declarations (revision 2)

Six `overwrite` entries across three policies, up from three. **Every `superseded_clause` was matched
verbatim against the base charter** — against base rules, base eligibility `condition` strings and
base `temporal_basis.counting_rule` strings — and all six locate in the base policy they name.

**F-1 / T0-1 closed at the charter level.** `allowance_ext_standing_order_refund` now declares both
halves of the deviation the round-1 audit found undeclared:
1. superseding *"The member asks for the order to be cancelled no later than the cancellation
   deadline counted from the time the order was placed."* with *"The member asks for the order to be
   stopped on the day it was placed, before it has been despatched."*
2. superseding *"Hours are counted as full 24-hour periods from the moment the order was placed, a
   request made exactly on the deadline is in time, and calendar days are never used in place of
   hours."* with *"The day the order was placed is read from the order's own record, which carries
   that day and no time of day, so the deadline is settled in whole days and never in hours."*

The replacement is coherent with the record: `allowance_catalog_orders.order_date` is a date-only
column, and the rule now asks only whether the request falls on that date. `order_hours` and
`K('hours_in_a_day')` are gone from the compute; the test is `order_days == K('same_day')` with
`same_day: 0`. The round-1 contradiction — a rule demanding a moment the record cannot supply, and a
compute taking calendar days in defiance of a sentence forbidding exactly that — no longer exists.
**F-4 closed with it**: the extended ladder's second tier is now "the member asks after the day it
was placed and it has not been despatched → the value of the items alone comes back, the plan having
already paid for the despatch", which agrees with base's "the delivery charge is not returned" rather
than contradicting it.

**T1-6 closed.** `allowance_ext_schedule_catch_up_load` now declares an `overwrite` on
`allowance_programme_opening`, superseding *"The programme runs for the benefit year of the health
plan that carries it, starts on the health plan's coverage effective date, and can never start before
it."* with a sentence licensing a programme opened later than the plan's cover start. The seeded
late-opening programme is no longer a world the charter forbids.

**F-9 closed.** `expiry_carry_share`'s tiers no longer require "the member made at least one settled
purchase from the card in that period"; they now turn on whether an allowance was loaded for the
period, which is not a condition base declines to weigh.

Sentence-by-sentence sweep against each `base_policy_refs` entry found no **new** undeclared
override. Two items are recorded:

**N-7 — observation — an `overwrite` on a base policy the extended policy does not reference.**
`allowance_ext_schedule_catch_up_load.base_policy_refs` is
`[allowance_load_schedule, allowance_agg_combined_annual_cap]`, yet one of its two `overwrite`
entries names `allowance_programme_opening`. Declaring the override is the right move; leaving the
overridden core out of `base_policy_refs` means the two fields disagree about which base cores this
policy rests on.

**N-8 — observation — the larger of the plan's and the card's quarterly allowance.**
`allowance_ext_card_in_use_first_load` and `allowance_ext_schedule_catch_up_load` both take
`period_rate = plan_rate if plan_rate > card_rate else card_rate`. Base
`allowance_health_plan_tier_interaction` says "the tier of the medical plan **fixes** … what the
quarterly allowance is", which would make the plan's figure govern whether or not it is the larger.
Neither policy lists that base core in `base_policy_refs` and neither declares an override. Not
demonstrable: on task 1's world the plan's 250.00 exceeds the card's 175.00, so both readings agree,
and task 0's tree does not reach either policy.

### factor_ladders (revision 2)

| Policy | factors | `parameter` | `method` | `cross_difficulty` | change from revision 1 |
| --- | --- | --- | --- | --- | --- |
| `allowance_ext_dvh_recovery_credit` | 5 | 2 | 3 | `osb` ×2 | fall-throughs of `recovery_lookback`, `recovery_member_share`, `recovery_credit_basis` rewritten |
| `allowance_ext_period_end_expiry` | 6 | 3 | 3 | none | `expiry_period_count` replaced by `expiry_period_allowance` |
| `allowance_ext_standing_order_refund` | 4 | 2 | 2 | none | `order_money_back` replaces `order_delivery_returned`; fall-throughs rewritten |
| `allowance_ext_closing_balance_forfeiture` | 4 | 2 | 2 | none | unchanged |
| `allowance_ext_card_in_use_first_load` | 4 | 2 | 2 | `advantage` ×1 | `first_load_ceiling` replaced by `first_load_period_months`; two ladders rewritten |
| `allowance_ext_schedule_catch_up_load` | 6 | 3 | 3 | `advantage` ×3 | fall-throughs rewritten |

All six still declare 4–6 factors with ≥ 2 `parameter` and ≥ 1 `method`; every ladder still has three
tiers, stated in full in the rule and implemented in `compute`, with the fall-through equal to the
factor's `baseline`; `decides` is an input binding in every case. Effect labels re-checked and honest.

**F-10 substantially closed, with one exception.** Revision 1 found five of six baselines collapsing
to a constant 0.00 that each rule read as "make no entry". Recomputed on the round-2 worlds, the
whole-baseline fall-backs are now:

| policy | rev 1 | rev 2 | is it the standard method? |
| --- | --- | --- | --- |
| `dvh_recovery_credit` | 0.00 | **165.00** | yes — credit back the whole year-to-date charge at DVH providers, no other payer assumed; record-dependent |
| `period_end_expiry` | 0.00 | **21.40** | yes — one period's allowance less what was posted against it; record-dependent |
| `standing_order_refund` | 0.00 | **8.00** | **no — see N-4** |
| `closing_balance_forfeiture` | 153.75 | **83.55** | yes — the balance the card record shows (unchanged, still honest) |
| `card_in_use_first_load` | 0.00 | **175.00** | yes — the card's own tier quarterly allowance, a figure the charter publishes |
| `schedule_catch_up_load` | 0.00 | **250.00** | yes, marginally — one benefit period's allowance as the year's ceiling |

Five of six now yield a real, bookable, record-dependent figure that a reader could write into the
tool, and each follows from its own `baseline.rule` read alone. This was the round-1 blocking defect
and it is genuinely repaired for those five.

**N-4 (new) — `allowance_ext_standing_order_refund`'s baseline is a non-zero number that is not the
standard method.** Its `baseline.rule` says *"The value of the items is taken as the smallest order
the card's tier will process"*, so `items_back` defaults to `P('catalog_order_minimum')` — 8.00 on the
Plus tier — and the whole baseline comes to 8.00 against a gold refund of 56.45. The order record
plainly carries `order_total: "46.50"`; reading it is tier 1 of `order_items_read`, i.e. a factor.
The standard method for refunding a cancelled catalogue order is the order's own total — base
`allowance_catalog_ordering` states the plan's own default in terms: "Where the plan cannot fill an
item the whole order is cancelled and **every penny, including the delivery charge, goes back on the
card**." A default that returns the catalogue's minimum order size instead of what the order cost is
not a treatment any plan publishes; it is a figure chosen so that the baseline is not zero. Recorded
as **`SOURCE-FACTOR RED`**, demonstrated against task 0's world in `0.md`.

**F-12 closed.** All three unreal fall-throughs of revision 1 are gone:
`first_load_share_basis`'s fall-through is now "otherwise → the share owed is the whole of that
period's allowance" (revision 1 paid a prorating-tier member opening on a period's first day
nothing — recomputed on the round-2 charter, that member now receives the whole period allowance);
`first_load_ceiling`, whose fall-through no customer could reach, has been removed from the charter
altogether; and `order_charge_ceiling`'s fall-through is now "the value of the items" rather than
"nothing", so a member who cancels before any catalogue transaction has settled is no longer capped
at zero. `first_load_period_allowance`'s fall-through is now "the card's own tier quarterly
allowance", a tier every cardholder can be on.

**F-11 NOT closed — the reworker's claim does not hold.** `baseline.params` is still, in all six
policies, a list of the parameters the *factors* read rather than the defaults the baseline method
uses. Checked one by one against each `baseline.rule`:

| policy | `baseline.params` | not read by the baseline |
| --- | --- | --- |
| `dvh_recovery_credit` | `year_to_date_months`, `purchase_dispute_window_days`, `dental_vision_hearing_eligible` | the latter two — the baseline fixes the stretch at year-to-date so it never compares the dispute window, and fixes the money going back as the whole charge so it never consults eligibility |
| `period_end_expiry` | 5 keys | `year_months` (the baseline counts only quarters and months) |
| `standing_order_refund` | `same_day`, `catalog_order_minimum` | `same_day` — the baseline takes "the value of the items alone", so it never tests the day |
| `closing_balance_forfeiture` | `minimum_giveup`, `merchant_refund_posting_days` | the latter — the baseline keeps nothing back, so it never compares an age |
| `card_in_use_first_load` | `month_months`, `quarterly_allowance_amount`, `enrollment_proration_basis` | `enrollment_proration_basis` — the baseline takes the whole period allowance, so it never consults the proration basis |
| `schedule_catch_up_load` | 5 keys | `quarter_months`, `year_months`, `annual_allowance_amount` — the baseline counts in months and takes one period's allowance as the year ceiling |

Recorded as an **observation**, as in revision 1, but explicitly **not closed**.

**F-13 not closed, and widened by the rework.** The reworker records this as unchanged by judgement,
arguing that two tiers agreeing in amount on tiers whose published standard-delivery fee is zero is
the charter's data rather than a collapsed ladder. That argument is acceptable for an observation and
was how revision 1 graded it. What the rework also did, however, is **remove the guard that kept the
two tiers apart**: revision 1's `delivery_paid` selected the standard fee only under
`standard_orders >= 1 and P('catalog_shipping_fee') > 0`, so tier 2 could fire only when its outcome
differed from tier 3's; revision 2 replaced that guard with `P('catalog_ordering_available')`, which
is true on all six tiers. Tier 2 now fires for a standard order on Plus, Premier, Dual Complete and
Chronic Care Plus and returns 0.00 — the same outcome as the fall-through. The overlap is wider than
it was. No consequence on either task's world (task 0's order is expedited, task 1 has no order), so
it stays an **observation**.

**N-6 (new) — observation — `order_charge_ceiling`'s two non-fall-through tiers select the same value
on task 0's world.** Tier 1 (more than one catalogue transaction → the largest) gives 56.45 and tier
2 (exactly one → that transaction) gives 56.45; substituting either into the computation leaves the
refund at 56.45. Only the baseline moves it. Demonstrated in `0.md`.

### findings (revision 2)

Round-1 findings, verified item by item against the reworked artifacts:

| round-1 item | claimed | verdict |
| --- | --- | --- |
| T0-1 / F-1 | closed | **closed** — two verbatim overwrites; hours arithmetic removed |
| T0-2 | closed | **closed** — see `0.md`, figures recomputed from the osb charter |
| T1-1 | closed | **closed** — see `1.md`, persona opening verified |
| T1-2 | closed | **closed** — the rule now states where the catch-up load is placed |
| T1-3 / F-12 | closed | **closed** — see `1.md`; F-12's three unreal fall-throughs all gone |
| F-10 / T0-3 / T1-4 | closed | **closed for five of six baselines**; N-4 is the exception |
| T0-4 / T1-4 (near-miss) | closed | **closed**, with a caveat recorded in `0.md` |
| F-3, F-4, F-5, F-6, F-7, F-8, F-9, T0-5, T0-6, T1-5, T1-6 | closed | **all closed**, verified above |
| F-11 | closed | **NOT closed** — still wrong in all six policies |
| F-13 | unchanged by judgement | judgement accepted as an observation, but the rework **widened** the overlap |

New this round: **N-1** (dead binding carrying a factor's declared evidence), **N-2** (cross-category
field declared but not read; tier condition the compute does not test), **N-4**
(`SOURCE-FACTOR RED` — a baseline that is not the standard method), **N-6** (a ceiling ladder whose
two tiers agree on task 0's world), **N-7** (`overwrite` on an unreferenced base core), **N-8** (the
larger of plan and card quarterly allowance against base's "the plan tier fixes it"), and **N-3**,
**N-5** — both per-task, demonstrated in `0.md` and `1.md`.

## closing_checklist (revision 2)

Written after both tasks' round-2 GT was revealed and both comparison sections were complete
(2026-09-21T15:02+00:00). The charter-global section of `revision_2` above was complete on disk
before either reveal and has not been altered since; one grading decided there is revisited below,
on threshold grounds rather than on anything GT showed.

**The difficulty now closes out.** All eight verdicts pass — four relationships on each of the two
tasks — against two of eight in revision 1.

| | task 0 (rev 1 → rev 2) | task 1 (rev 1 → rev 2) |
| --- | --- | --- |
| Policy self-consistency | `SOURCE-POLICY RED` → **PASS** | PASS → **PASS** |
| The problem tree holds | PASS → **PASS** | `SOURCE-CHAIN RED` → **PASS** |
| Factors bear weight | `SOURCE-FACTOR RED` → **PASS** | `SOURCE-FACTOR RED` → **PASS** |
| Unique solution | `SOURCE-TASK RED` → **PASS** | `SOURCE-TASK RED` → **PASS** |

**Every revision-1 blocking item verified closed against the artifacts, not against the reworker's
account.** T0-1/F-1 (two verbatim overwrites; the hour arithmetic removed and the deadline settled in
whole days, with the delivered July order keeping the question live rather than vacuous); T0-2 (the
`osb` claims now reproduce exactly from the rider's 80% coinsurance and 50.00 deductible, 80.00 and
192.00, summing to the rider's own `annual_maximum_used` of 272.00); T1-1 (the persona's opening is
one request with an explicit disclaimer, and every mention of the activation is gated behind the
representative); T1-2 (the placement of the catch-up load is now a sentence of the policy's own
rule); T1-3/F-12 (the plan tier change makes the cross-difficulty read worth 25.00 of the scored
figure, the tier condition is distinct by construction, and nothing was stranded by the change);
F-10 (five of six baselines now yield real bookable figures); T0-4/T1-4 (near-misses that change the
answer when wrongly counted, and GT requires the agent to read the 2025 card and exclude it).
Fourteen revision-1 observations were also verified closed. **Nothing that passed in revision 1 has
regressed**: task 0's problem tree and task 1's policy self-consistency were re-derived in full on
the new worlds and both still hold.

**One pre-reveal grading revisited.** `revision_2` → `factor_ladders` records **N-4** — the
`standing_order_refund` baseline defaulting the item value to the tier's minimum order size (8.00
against a gold refund of 56.45, on an order whose record carries 46.50) — as `SOURCE-FACTOR RED`.
On applying the red-light table item by item it does not reach that threshold: the baseline **is**
what its own `baseline.rule` states, every sentence of that rule is in the `rule`, it is
self-sufficient, its figure is definite and differs from gold, and the fall-through tier is
defensible in its own domain because it fires only when no order stands, in which case
`order_money_back`'s fall-through zeroes the result anyway. **N-4 is therefore an observation**, and
the coordinator's concern about non-zero numbers chosen to clear the gate is recorded as met in five
of six policies and answered on the merits in the sixth. This downgrade was decided against the
standard, not against GT, whose `baseline_result` of 8.0 matches this audit's own figure.

**Items open at close, all observations, none blocking:**

- **F-11 — not closed**, contrary to the reworker's claim: `baseline.params` still names parameters
  the `baseline.rule` does not read, in all six policies (table in `revision_2` → `factor_ladders`).
- **F-13 — not closed and widened**: removing the `P('catalog_shipping_fee') > 0` guard lets
  `order_delivery_charge`'s second tier fire on the four tiers whose standard fee is zero, where it
  returns the same 0.00 as the fall-through. The reworker's judgement that this is the charter's data
  is acceptable for an observation; the rework nonetheless made the overlap wider rather than leaving
  it alone.
- **N-1** — `period_purchase_count` is a dead binding (`>= 0` is true on every world; forcing it to
  0, 1, 5 or 999 leaves task 0's expiry at 53.65), and `expiry_carry_base` names it as its sole
  evidence while naming none of the three bindings its stated tiers rest on.
- **N-2** — `advantage.coverage_end_date` declared in the catch-up's cross-category reads and never
  read; its ceiling ladder's second tier is stated as the plan's cover having ended and implemented
  as the plan not being active.
- **N-4**, **N-6** (task 0's ceiling ladder tiers agreeing at 56.45), **N-7** (an `overwrite` on a
  base core absent from `base_policy_refs`), **N-8** (the larger of plan and card quarterly allowance
  against base's "the plan tier fixes it"), **N-3** (the expiry's single `source_ledger_entry_id`
  entailed through a base sentence and the seed's own link rather than through the extended rule),
  **N-5** (below).
- **N-5 — observation — the new near-miss programme's plan reference.** Task 1's added 2025 Core
  programme `a0b47dba-…` carries `linked_plan_reference: "cc7a06ec-…"`, an enrollment whose
  `coverage_effective_date` is 2026-05-01 — ten months after that programme's
  `program_start_date` of 2025-07-01. Base `allowance_programme_opening` says a programme "can never
  start before" its health plan's coverage effective date, and the new `overwrite` licenses only the
  opposite direction (a programme opened *later* than the plan's cover start). The persona says that
  card "finished with the old plan", implying a different enrollment, and none is seeded. No
  computation reads that programme, so there is no scored consequence; it is a record the charter
  would not have produced, added while closing T1-4.

**Closing checks.**

- The per-task audit files correspond one-to-one with the tasks; `_difficulty.md` sits alongside
  them; revision 1 is preserved intact in all three files and revision 2 is appended below it; both
  comparison sections carry an explicit PASS.
- Coverage and exclusivity re-derived on the reworked charter: the two `charter_scope` entries match
  the two components of the `prerequisite` graph exactly, are pairwise disjoint, and jointly cover
  all six extended policies and all six task tools, each scope spanning a whole tree.
- Task tools and GT are closed; every uuid8 is unchanged, independently generated and frozen —
  `634307a6`, `1d3932f1`, `88277d51`, `5a9eaadb`, `a5740baf`, `838eeda2`.
- Problem trees: task 0 has three prerequisite problems and three `value_input` edges (floor 2);
  task 1 has one and one (floor 1); each has at least one problem resolved by an `owner=user` tool;
  the difficulty's four edges remain a DAG with no cross-task reference.
- Every computation declares a self-sufficient baseline and 4–6 factors with ≥ 2 `parameter` and
  ≥ 1 `method`; every ladder has three tiers stated in full in its rule; **all 29 factors bear weight
  on their task's world**, verified by independent recomputation, and every figure agrees with the
  task files' own `factor_sensitivity` and `baseline_result` — 19 factors and four baselines on task
  0, ten factors and two baselines on task 1.
- Both independent derivations reproduced GT exactly on every scored amount, object, owner, order and
  terminal state — 47.00 / 53.65 / 56.45 / 118.90 and 83.33 / 583.34 — with no exception this round.

**Instantiation-stage gates re-run on the final form (2026-09-21T15:00+00:00):** `check_extended`
EXTENDED OK; `check_task_tools` TASK TOOL CONTRACT OK; `replay_tasks` REPLAY OK (0.json 17 acts,
30/30 rows, match True; 1.json 12 acts, 20/20 rows, match True); `check_solvability` SOLVABILITY OK;
`check_compute` COMPUTE OK (history_rows_max 38, branches_max 60); `check_grounding` GROUNDING OK;
`check_cross_fire` SCOPE OK. `check_traceability` remains deferred to the KB render.

**Write-domain disclosure (revision 2).** As in revision 1, `replay_tasks.py` rewrites the task JSON
it replays (line 303), so the required gate re-run rewrote
`tasks/supplemental_benefit_allowance_desk/tasks/0.json` and `1.json`. Both files were copied before
the run and compared after: parsed and normalised with `sort_keys`, **both are semantically
identical** — no key and no value differs. Nothing else outside
`audits/policy_task/supplemental_benefit_allowance_desk/` was written, and no blueprint, task, skill
or `erlbench` file was edited by this auditor.

---

# revision_3

Revisions 1 and 2 above are preserved unaltered.

## scope and carry-forward decision

- Time: 2026-09-21T15:24+00:00. Auditor: the same independent source-layer auditor.
- This is a **regression check on a narrow cleanup round, not a re-opening**. The 8/8 PASS recorded
  in `revision_2` → `closing_checklist` is the standing verdict; the question here is only whether
  the cleanup broke anything.

| artifact | round 2 | round 3 |
| --- | --- | --- |
| `allowance.extended.yaml` | `0d6c248b2469e392` | `c3f352b8ef09af65` — **CHANGED** (3538 → 3528 lines) |
| `task_tools.py` | `bdab0227bf9b9260` | `bdab0227bf9b9260` — unchanged |
| `_masked_views/0.masked.json` | `5da8ae7f52d00552` | `5da8ae7f52d00552` — unchanged |
| `_masked_views/1.masked.json` | `669e6e494cd6fe49` | `669e6e494cd6fe49` — unchanged |

**What was re-derived and what was carried forward, and on what grounds.** The charter moved, so
under the carry-forward rule the charter-global section is not eligible to be carried by reference
and **every charter-global check was re-run mechanically against the new file**: the base-copy diff,
`compute_basis` completeness and verbatim correspondence (119 bindings), every `baseline.rule`
sentence against its `rule`, all six `overwrite` quotations against the base charter, all four
prerequisite sentences against their blocked rules and against the depended-on rules, factor counts,
effect labels, tier counts, binding-set disjointness, and cross-category declarations **in both
directions**. What is carried forward by reference, on the grounds that its inputs are byte-identical:
the two worlds and both personas (masked views unchanged), and therefore every conclusion in
`revision_2` that rests on the world rather than the charter — the problem-tree walks, the near-miss
analysis, the persona checks and the object identification. The per-task numeric conclusions were
**not** carried forward; they were recomputed from scratch, because recomputation is the actual
instrument of a regression check and is cheap.

## regression result

**Nothing regressed. Every figure is identical to revision 2.** Recomputed independently against the
unchanged worlds:

| computation | gold (r2 → r3) | whole baseline (r2 → r3) | 29 factor sensitivities |
| --- | --- | --- | --- |
| `credit_amount` | 47.00 → **47.00** | 165.00 → **165.00** | 5.00, 89.00, 0.00, 95.00, 95.00 — identical |
| `expiry_amount` | 53.65 → **53.65** | 21.40 → **21.40** | 0.00, 48.65, 44.65, 47.43, 107.30, 107.30 — identical |
| `refund_amount` | 56.45 → **56.45** | 8.00 → **8.00** | 17.95, 46.50, 46.50, 46.50 — identical |
| `forfeited_balance` | 118.90 → **118.90** | 83.55 → **83.55** | 58.90, 172.55, 143.55, 143.55 — identical |
| `first_load_amount` | 83.33 → **83.33** | 175.00 → **175.00** | 250.00, 250.00, 58.33, 250.00 — identical |
| `catch_up_amount` | 583.34 → **583.34** | 250.00 → **250.00** | 616.67, 333.34, 616.67, 333.34, 666.67, 166.67 — identical |

Task 0's three edge weights come back **71.90 / 172.55 / 62.45** and its opening-world contrast
**69.10**; task 1's skip-the-activation figure comes back **0.00**. Factor ids, counts and effect
labels are unchanged in all six policies (5/6/4/4/4/6, each 4–6 with ≥ 2 `parameter` and ≥ 1
`method`, every ladder still three tiers). The `prerequisite` graph is identical edge for edge —
same four edges, same `kind`, `gate`, `form` and `resolved_by`. The base copy is still byte-for-byte
identical to `blueprint/products/allowance.yaml`. `task_tools.py` is unchanged, so the six uuid8s and
the finding that no tool judges a prerequisite carry forward untouched.

**The two relationships the brief singled out still hold.** Task 0's problem tree: the worlds and the
persona are byte-identical, the three prerequisite sentences are still verbatim in the root's own
rule, the graph is unchanged, and all three edges still bear weight at the same figures — it holds.
Task 1's policy self-consistency: `compute_basis` is complete and verbatim for both of its policies,
its overwrite quotations still locate verbatim, and the N-2 cleanup removed an inconsistency rather
than adding one — it holds.

## the four cleanup items, verified against the artifacts

**N-1 — CLOSED, verified by re-running the round-2 instrument.** `period_purchase_count` is gone from
the charter. `carry_base` is now
`period_loads if (period_load_count >= 1 and period_settled_for_base >= period_loads / 2) else (unspent if (period_load_count >= 1 and period_settled_for_base < period_loads / 2) else 0.0)`,
where `period_settled_for_base` is a real `SUM` of the dying period's settled purchases, and
`expiry_carry_base.bindings` is now `[period_settled_for_base, carry_base]` — the quantity its two
stated tiers actually rest on. The round-2 test is re-run below, and the binding is live: it flips
the scored expiry at exactly the threshold the rule names, `period_loads / 2 = 72.50`.

| forced `period_settled_for_base` | 0 | 1 | 5 | 50.15 | 72.49 | 72.50 | 100 | 999 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| scored expiry | 53.65 | 53.65 | 53.65 | 53.65 | 53.65 | **34.80** | **34.80** | **34.80** |

In round 2 every one of those values returned 53.65. The reworker's reported figures (0/1/5 → 53.65,
999 → 34.80) are reproduced, and the threshold was located independently rather than taken on
report. The second tier's condition is now stated rather than tautological: "an allowance was loaded
for that period and the member spent **less than half** of it from the card in that period", which is
the exact complement of tier 1 and matches the rule.

**F-13 — CLOSED, and the widening is undone.** The guard is restored in the compute
(`P('catalog_shipping_fee') > 0`) **and** the ladder's second tier is reworded to state it: "an order
stands that was sent by the standard service **and the card's tier makes a charge for standard
delivery**". The round-2 wording ("the card is one that offers catalogue ordering"), which let tier 2
fire on the four tiers whose standard fee is zero and return the same 0.00 as the fall-through, is
gone from the rule prose as well as from the compute. Tier 2 can now fire only where its outcome
differs from the fall-through, so the ladder has three distinct outcomes wherever tier 2 is
reachable, and on the four zero-fee tiers it correctly has two reachable tiers rather than two tiers
with one outcome. Restoring the guard stranded nothing: Core (4.95) and Select (3.95) still reach
tier 2, and task 0's order is expedited, so tier 1 is taken and the refund is unchanged at 56.45.
This is better than the round-2 state in both faces — in round 1 the compute carried a guard the rule
did not state; now the two agree.

**F-11 — CLOSED in all six policies.** `baseline.params` was trimmed to exactly the keys each
`baseline.rule` reads, and the result matches the table this audit derived in `revision_2` →
`factor_ladders` key for key:

| policy | round 2 | round 3 | this audit's round-2 finding |
| --- | --- | --- | --- |
| `dvh_recovery_credit` | 3 keys | `[year_to_date_months]` | the other two were not read ✓ |
| `period_end_expiry` | 5 keys | `[quarter_months, month_months, quarterly_allowance_amount, benefit_period_basis]` | `year_months` was not read ✓ |
| `standing_order_refund` | 2 keys | `[catalog_order_minimum]` | `same_day` was not read ✓ |
| `closing_balance_forfeiture` | 2 keys | `[minimum_giveup]` | `merchant_refund_posting_days` was not read ✓ |
| `card_in_use_first_load` | 3 keys | `[month_months, quarterly_allowance_amount]` | `enrollment_proration_basis` was not read ✓ |
| `schedule_catch_up_load` | 5 keys | `[month_months, quarterly_allowance_amount]` | the other three were not read ✓ |

Each trimmed list was re-derived from the `baseline.rule` text rather than checked against the
round-2 table alone: the dvh baseline fixes its stretch at year-to-date and its outcome at the whole
charge, so it consults neither the dispute window nor the eligibility flag; the expiry baseline
counts only quarters and months; the order baseline takes the items alone, so it never tests the day;
the closing baseline keeps nothing back, so it never compares an age; the first-load baseline takes
the whole period allowance, so it never consults the proration basis; the catch-up baseline counts in
months and caps at one period's allowance, so it reads neither the quarter length nor the annual
allowance. All six are right.

**N-2 — CLOSED, both halves.** The catch-up's declared `advantage` reads are now
`[status, otc_allowance_quarterly, coverage_effective_date, advantage_premium_ledger.event_type, advantage_premium_ledger.posted_date]`
— `coverage_end_date`, which no binding read, has been dropped. The ladder tier it was supposed to
serve is reworded from "the medical plan carrying the card **has ended part way through the benefit
year**" to "the medical plan carrying the card **is no longer in force**", which is what
`year_ceiling` actually tests (the `else` of `plan_in_force`), so the rule and the compute now agree.
The `note` on the cross-category block was carried through with it ("…decide the ceiling tier where
that plan is no longer in force") — no leftover. The sibling policy
`allowance_ext_card_in_use_first_load` was correctly left alone: it still declares `coverage_end_date`
and still reads it, in `plan_end_day: CFIELD('advantage','coverage_end_date')`, which feeds the
second tier of `period_allowance`. Re-checked mechanically in both directions across all four
cross-category blocks: **no field is declared without being read, and none is read without being
declared.**

## one item closed that the reworker did not claim

**N-7 — CLOSED, unclaimed.** The reworker listed N-7 among the items left alone. It is not:
`allowance_ext_schedule_catch_up_load.base_policy_refs` is now
`[allowance_load_schedule, allowance_agg_combined_annual_cap, allowance_programme_opening]`, so the
base core its second `overwrite` names is no longer absent from its declared refs, which was the
whole of N-7. Recorded because this audit verifies against the artifacts rather than the account, and
a discrepancy in the harmless direction is still a discrepancy. The consequence of adding that core
was checked rather than assumed: every other sentence of `allowance_programme_opening` (the in-force
plan at opening, the entry-gate standing, the card's production and delivery, the no-allowance tier,
the later-confirmed chronic condition) is either followed by the catch-up policy or untouched by it,
and only the conflicting sentence is overridden — so widening `base_policy_refs` introduced no new
undeclared override.

## items still open, all observations, none blocking

**N-3, N-4, N-5, N-6, N-8** were verified textually and numerically **untouched**, as the reworker
states, and remain open exactly as `revision_2` recorded them:

- **N-3** — the expiry's `source_ledger_entry_id` when the dying period carries two loads: the rule
  still says nothing about which entry the expiry names; the entailment still runs through base
  `allowance_load_schedule`'s correcting-load sentence plus the seed's own link.
- **N-4** — the `standing_order_refund` baseline still defaults the item value to the tier's minimum
  order size; `baseline.params` is now `[catalog_order_minimum]`, which is the key it does read, so
  the F-11 half is closed while the substance of N-4 stands. Recomputed: the whole baseline is still
  **8.00** against a gold 56.45. **It remains an observation, not a red light** — the grading in
  `revision_2` → `closing_checklist` was decided against the red-light table and nothing this round
  disturbs it. This is noted because the reworker raised it as an open `SOURCE-FACTOR RED`, reading
  the pre-reveal text in `revision_2` → `factor_ladders` rather than the reconsideration that
  follows it; the two sections are not in conflict, the later one governs.
- **N-5** — the 2025 near-miss programme's `linked_plan_reference` still points at an enrollment whose
  cover began ten months after that programme started. The worlds are byte-identical, so this is
  necessarily unchanged; it has no scored consequence.
- **N-6** — `order_charge_ceiling`'s two non-fall-through tiers still both give 56.45 on task 0's
  world; re-substituted this round, both return **56.45**.
- **N-8** — `period_rate` still takes the larger of the plan's and the card's quarterly allowance
  without declaring it against base `allowance_health_plan_tier_interaction`; not demonstrable on
  either world.

One new note, minor: closing N-1 introduced `period_settled_for_base`, a second binding with the same
`SUM` expression as `period_settled`. The duplication is how the two factors' binding sets are kept
disjoint — `period_settled` belongs to `expiry_spend_counted` and `period_settled_for_base` to
`expiry_carry_base` — so it is the right shape rather than a defect, and it is recorded only so that
a later reader does not mistake it for an accident.

## verdict (revision 3)

**The 8/8 PASS stands.** All four relationships hold on both tasks, unchanged from revision 2:

| | task 0 | task 1 |
| --- | --- | --- |
| Policy self-consistency | **PASS** | **PASS** |
| The problem tree holds | **PASS** | **PASS** |
| Factors bear weight | **PASS** | **PASS** |
| Unique solution | **PASS** | **PASS** |

Four round-2 observations (F-11, F-13, N-1, N-2) are closed and a fifth (N-7) is closed unclaimed;
six remain open as observations, none of them blocking; nothing regressed and no new defect was
found.

**Gates re-run on the final form (2026-09-21T15:22+00:00):** `check_extended` EXTENDED OK;
`check_task_tools` TASK TOOL CONTRACT OK; `check_solvability` SOLVABILITY OK; `check_compute`
COMPUTE OK; `check_grounding` GROUNDING OK; `check_cross_fire` SCOPE OK. `check_traceability` remains
deferred to the KB render.

**Write-domain disclosure (revision 3).** `replay_tasks.py` was **deliberately skipped** this round,
per the coordinator's note that it rebuilds `db_closure` from a set iteration and is byte-unstable;
its round-3 result is cited from the coordinator's own run (REPLAY OK, 0.json 17 acts 30/30, 1.json
12 acts 20/20). Confirmed after the gate run that all four source hashes are still pinned —
`allowance.extended.yaml` `c3f352b8ef09af65`, `task_tools.py` `bdab0227bf9b9260`, and both task JSON
files byte-unchanged. **Unlike revisions 1 and 2, this round wrote nothing whatsoever outside
`audits/policy_task/supplemental_benefit_allowance_desk/`.**
