# Policy-task audit — membership_benefits_desk / charter-global

## charter_global_frozen

- auditor: independent source-layer auditor (erl-task-policy-audit), not the instantiating agent
- freeze time (charter-global section, written before any task's GT was revealed): 2026-09-18T09:40Z
- `membership.extended.yaml` sha256_16 = `ddf9b56fdd9c5727`
- `task_tools.py` sha256_16 = `dffb81181aa8f29b`
- fields permitted while this section was written: `blueprint/blueprint.yaml`, `blueprint/db_schema.json`,
  `blueprint/share_tools.py`, `blueprint/products/*.yaml`, the whole of `membership.extended.yaml`
  (base copy + `extended_policies`), the whole of `task_tools.py`, and each task's `frozen_time`,
  `user_scenario` and `initial_state`
- fields explicitly masked and unread while this section was written: for both tasks,
  `evaluation_criteria`, `computations`, `charter_scope`, `required_documents`, `design_rationale`,
  `solvability_contract`, `prerequisite_closure`, `db_closure`,
  `db_closure_matches_initial_state`; and every existing audit file of any other difficulty
- **entry conditions** (checked, not re-run): the instantiation-stage gate snapshot supplied with the
  brief shows `check_extended`, `check_task_tools`, `replay_tasks`, `check_solvability`,
  `check_compute`, `check_grounding` and `check_cross_fire` all green; `check_traceability` is
  deferred to the render step by design. The two masked views were supplied with their hashes
  (`0.json` masked sha256_16 `b952a65523338194`, `1.json` masked sha256_16 `b6952c137ef4755b`).
  Entry conditions are complete; no "incomplete input" finding.
- **method note, not contamination.** The two masked views were re-serialised with sorted JSON keys.
  `initial_state.purchase_orders` therefore comes back in a different key order than the source file
  carries, and `CFIELD`/`CPARAM` return `hs[0]` — the *first* matching row — so the masked copies
  evaluate task 1's cross-category order reads against the wrong purchase order. All derivations below
  were therefore run against `frozen_time` and `initial_state` read directly out of `tasks/0.json` and
  `tasks/1.json` and nothing else; both are on the permitted list. No masked field was read before the
  corresponding freeze. See finding **D8**, which is this observation turned into a defect of the
  artifact rather than of the audit.

### policy_conflict_scan

Six extended policies, each claiming one `(target_tool, computes)` pair and one disjoint scope:

| policy | trigger | subject | computes | target_tool | owner |
| --- | --- | --- | --- | --- | --- |
| `membership_ext_grace_dues_settlement` | on_request | membership_dues_payment | settlement_payment_usd | `settle_membership_dues_c8b60f0e` | user |
| `membership_ext_year_benefit_credit_grant` | state_due | membership_benefit_grant | credit_granted_usd | `grant_benefit_credit_b1d93258` | agent |
| `membership_ext_benefit_credit_application` | on_request | membership_benefit_redeem | credit_applied_usd | `apply_benefit_credit_8295b346` | agent |
| `membership_ext_purchase_points_accrual` | state_due | membership_points_accrue | points_earned | `book_purchase_points_235cc6ac` | agent |
| `membership_ext_points_expiry_sweep` | state_due | membership_points_expire | points_swept | `sweep_expired_points_bcca39ef` | agent |
| `membership_ext_points_redemption_release` | on_request | membership_points_redeem | points_redeemed | `redeem_reward_points_8621cafe` | user |

The base copy inside `membership.extended.yaml` is **verbatim identical** to
`blueprint/products/membership.yaml` on every shared top-level key (`category`, `display_name`,
`binding`, `lifecycle`, `accounts`, `parameter_schema`, `variants`, `events`, `measures`, `policies`);
verified by a key-by-key canonical-JSON comparison. No base rewrite.

Subjects are pairwise disjoint over the nine claimed `event_type`s; `membership_tier_change`,
`membership_dues_charge` and `membership_cancel` are claimed by the difficulty but carried by no
extended policy — a coverage gap of the claim, not of the six policies, and not a conflict.

The two tasks' problem trees partition the six policies **3 + 3** with no overlap:

- task 0: `membership_ext_benefit_credit_application` (root) ← `membership_ext_year_benefit_credit_grant`
  ← `membership_ext_grace_dues_settlement`
- task 1: `membership_ext_points_redemption_release` (root) ← `membership_ext_purchase_points_accrual`,
  ← `membership_ext_points_expiry_sweep`

Mutually exclusive and jointly complete over the six extended policies. ✔

Cross-category read boundaries: `credit`, `protection`, `service`, `orders`, `returns` are read; every
read is declared in that policy's `cross_category` block and every declared `reads` field exists in
`db_schema.json`. No extended policy writes outside `membership_events` / `membership_holdings`. ✔

Overlapping-subject conflicts **inside** the extended set: none — no two policies decide the same
quantity. Conflicts between extended and base are the subject of `override_declarations` below, and
two rules contradict **themselves**; those are findings D1 and D2.

### rule_compute_equivalence

Check 2 was run binding by binding over all six policies. Every binding of every policy carries a
`compute_basis` entry, and every `compute_basis` entry is a verbatim sentence (or sentence group) of
that policy's `rule`; every ladder tier named in `factors[].ladder` appears both as a `rule` sentence
and as a branch of the `decides` binding, and every branch of every `decides` binding is a tier the
rule states. No tier lives only in `compute`, and no tier lives only in the prose. ✔

Windows, caps, floors, rounding points and grouping are stated and implemented: `RND(..., 2)` at the
end only in the four money computations, `RND(..., 0)` / `int(...)` at the end only in the two points
computations, `MX(0.0, ...)` floors where the rule says "never falls below nothing", and the explicit
`The order is fixed: ...` / `The parts are combined in one sum, in this order: ...` sentences match the
arithmetic order of the `result` expression in all six. ✔

Four places where `compute` does **not** implement what the `rule` says (findings D7, D8 and two
observations O1, O2 below):

1. `membership_ext_year_benefit_credit_grant.compute.prior_same_code_grants`, and
   `membership_ext_benefit_credit_application.compute.grants_same_code_12m` /
   `redeems_same_code_12m`, hard-code `benefit_code='service_credit'` while both rules say
   "under the same named benefit" / "the same named benefit it belongs to". → **D7**.
2. every `CFIELD`/`CPARAM`/`XSUM`/`XCOUNT` call carries no correlation key to the business object the
   rule names. → **D8**.
3. `counted_entry_window`'s first tier: the rule says "the entries booked **since the day that term
   began** are counted", `compute` says `MX(1, MONTHS(F('current_term_start'), NOW) + 1)`, and
   `within_months=n` admits any row with `MONTHS(row_date, NOW) < n`, i.e. back to the *n*-th
   preceding month-day rather than to the term-start day. On task 0 the derived window is 1, which
   reaches back to 2026-08-19 rather than to 2026-09-01. → observation **O1** (no row falls in the
   band on either task's world, so no consequence is demonstrable).
4. the same approximation in `counted_prior_grant_window` (`MX(1, months_on_tier + 1)` for "since the
   day the tier now recorded took effect") and in `months_on_tier` in
   `membership_ext_points_redemption_release`. → same observation **O1**.

Sweep back for compute inventing a basis of its own: none found beyond D7/D8. Sweep back for the rule
making an empty promise: the settlement rule's late-fee sentence is an empty promise in one branch →
**D1**.

### action_binding_and_uuids

Each `(target_tool, computes)` pair is claimed by exactly one policy (table above); no pair repeats. No
policy adds a confirmation, review, wait or procedure of its own. Every tool docstring was scanned for
ordering words and for other tools' names:

- ordering-word hits: `grant_benefit_credit_b1d93258` "can **then** see the credit" (a consequence of
  the same call), `settle_membership_dues_c8b60f0e` "the **first** day of the billing period" (a date
  part), `book_purchase_points_235cc6ac` "read from that order record **before** the call" (reading a
  value, not ordering an action), `redeem_reward_points_8621cafe` "at the till there and **then**" (an
  enum gloss). None states an action's position in a sequence.
- other tools' names in a docstring: none.
✔

uuid8s, one per tool, checked individually:

`b1d93258`, `c8b60f0e`, `8295b346`, `235cc6ac`, `bcca39ef`, `8621cafe`

Eight hex digits each, no shared prefix or suffix, no sequence, no common stem with a changed tail, no
adjacency, and none reused. Independently generated and frozen. ✔

### prerequisite_graph

Four edges over six nodes; every policy has `prerequisite` filled in (`[]` on the three leaves).

| blocked policy | problem | kind | gate | form | resolved_by |
| --- | --- | --- | --- | --- | --- |
| `membership_ext_year_benefit_credit_grant` | `membership_ext_grace_dues_settlement` | value_input | `arrears_offset` | state | `settle_membership_dues_c8b60f0e` |
| `membership_ext_benefit_credit_application` | `membership_ext_year_benefit_credit_grant` | value_input | `credit_standing` | state | `grant_benefit_credit_b1d93258` |
| `membership_ext_points_redemption_release` | `membership_ext_purchase_points_accrual` | value_input | `earned_in_life` | state | `book_purchase_points_235cc6ac` |
| `membership_ext_points_redemption_release` | `membership_ext_points_expiry_sweep` | value_input | `swept_in_life` | state | `sweep_expired_points_bcca39ef` |

- every `problem` names another policy id in this file, never a base policy, never itself ✔
- acyclic: two chains, `settlement → grant → application` and `{accrual, sweep} → redemption`,
  with no edge between the two ✔ — and no cross-task reference, so the whole-difficulty graph is a DAG ✔
- `kind: value_input` on all four; each `gate` names a binding that genuinely exists in the blocked
  policy's `compute` (`arrears_offset`, `credit_standing`, `earned_in_life`, `swept_in_life`) ✔
- `resolved_by` is the depended-on policy's own `target_tool` in all four ✔
- `form: state` on all four, and no `fallback_reason` is present on any — correct, since
  `fallback_reason` is required exactly on action-form edges ✔
- no authoring-viewpoint phrasing ("in this task", "at the opening", "the current world") in any
  `prerequisite` block ✔
- `condition` neither strengthened nor weakened: **fails on two of the four edges** →
  findings **D6** (application ← grant: condition narrower than the sentence) and **D16** (redemption ←
  sweep: the condition as written is already true at task 1's opening).

### prerequisite_sentences

Four-point test on each `policy_source`; all four are verbatim sentences of the **blocked** policy's own
`rule`, quoted here from the file:

1. grant ← settlement — "The credit granted for a membership year is worked out only after the ledger
   carries a payment applied to the billing period the membership is now in."
   - ordering connective: "only after" ✔ · state form: "the ledger carries a payment applied to the
     billing period the membership is now in" names a record-visible state in the words the tables use
     (`membership_events.applied_period_start`) with no performer and no tool ✔ · no tool name, policy
     id, snake_case token or row id ✔ · strength equals the `condition` ✔
   - exactly one write of this difficulty brings that state about: only
     `settle_membership_dues_c8b60f0e` creates a `membership_dues_payment` row carrying
     `applied_period_start`. Derivation, in one reading: the sentence says the credit waits on a payment
     entry for the current billing period; `membership_dues_billing` (inherited) says dues payments are
     booked against a billing period; `membership_ext_grace_dues_settlement` is the only policy whose
     subject is `membership_dues_payment`; therefore the resolving action is that policy's write. ✔
2. application ← grant — "The credit set against a charge is worked out only after the ledger carries
   the benefit credit granted for the membership year in which that charge falls."
   - ordering connective "only after" ✔ · state form ✔ · no tool name ✔ · **strength: FAILS** — the
     sentence says "the benefit credit granted for the membership year in which that charge falls",
     which names no benefit code, while the edge's `condition` says "a benefit grant entry **under the
     same named benefit** whose grant cycle year is the membership year the charge falls in". The
     sentence is broader than the condition. → **D6**
   - one write brings it about (`grant_benefit_credit_b1d93258`) ✔
3. redemption ← accrual — "The points a redemption spends are settled only after the ledger carries an
   earning entry for every purchase already billed on the profile."
   - ordering connective "only after" ✔ · state form ✔ · no tool name ✔ · strength equals the
     `condition` ("an earning entry for every purchase already billed to the profile whose points have
     not yet been booked") ✔
   - one write brings it about (`book_purchase_points_235cc6ac`) ✔
4. redemption ← sweep — "No points are released until the balance carries the sweep owed for every
   sweep year already closed."
   - ordering connective "until" ✔ · state form ✔ · no tool name ✔ · **strength: FAILS** — the sentence
     quantifies over "**every** sweep year already closed" while the `condition` says "a sweep entry for
     **the** sweep year now closed" (singular). Worse, neither the sentence, the `rule`, the `params`
     nor any base policy ever says what a sweep year is or when one closes. → **D16**, **D17**
   - one write brings it about (`sweep_expired_points_bcca39ef`) ✔

Neither depended-on rule restates its dependant's sentence: `membership_ext_grace_dues_settlement.rule`,
`membership_ext_purchase_points_accrual.rule` and `membership_ext_points_expiry_sweep.rule` carry no
prerequisite sentence at all, and `membership_ext_year_benefit_credit_grant.rule` carries only its own
(the one it is blocked by), never the application's. ✔ No rule carries a second wording of the same
dependency, another problem's tool name, another policy's id, or an aggregated chain. ✔

Cross-problem orders stated in a rule that ground **no** declared edge:

- base `membership_dues_delinquency`: "where the tier suspends benefits in grace the member may not
  redeem points or benefit credit **until** the dues are settled". This is a base sentence stating a
  cross-problem order (settle dues → then spend benefit credit) and task 0's tree does rest on that
  order. Because the extended rules do carry prerequisite sentences of their own on both hops of that
  chain, this is recorded as an **observation (O3)** rather than a RED — but see D6: read together with
  D6 it hands task 0 a two-write path (settle, then apply) that skips the grant.
- base `membership_tier_migration`: "A membership standing in grace may be upgraded only **after** the
  outstanding dues are settled" — grounds no edge and no task's tree rests on it. Observation **O4**.

### override_declarations

Sentence-by-sentence sweep of each extended policy against each `base_policy_refs` entry. Conclusions
are reached on every base sentence; only the sentences where extended handles the scored quantity
differently are listed. Declared supersessions are marked ✔; undeclared ones become findings.

**`membership_ext_grace_dues_settlement`** vs `membership_dues_billing`, `membership_dues_delinquency`:

| base sentence | extended treatment | declared? |
| --- | --- | --- |
| delinquency: "The late fee of the tier is billed when grace begins, and it is owed whether or not the membership is later reinstated." | replaced by the repeat-late-fee schedule | ✔ named in `overwrite` |
| billing: "Dues are billed for a whole billing period at the dues figure of the tier recorded on the membership on the first day of that period…" | followed (the ledger's own `annual_dues` / `proration` rows are the dues side) | inherited, no conflict |
| billing: "Dues are billed, and payments applied, only while the membership record stands in application_received, active or grace." | carried verbatim into the extended rule's last sentence | inherited, no conflict |
| billing: "**A payment is applied to the oldest unpaid billing period first**, and any remainder to the next; a payment larger than everything outstanding leaves the surplus as unapplied credit on the membership rather than being returned." | extended's edge `condition` fixes the applied period to "the billing period the membership record is now in" | **NOT named → D3** |
| billing: "Business tiers may settle dues on invoice…; consumer tiers settle on the card on file or from store credit." | followed (the rule repeats it) | inherited |
| billing: "The enrollment fee, where the tier charges one, is billed once on the enrollment day and is never refunded on cancellation." | extended reads the *absence* of an enrollment-fee entry in a 12-month window as the discriminator of the seat charge | see **D9** |
| billing: "Dues already billed for a period the customer has used are owed in full even if the membership later lapses or is cancelled." | the grace/term settlement window drops earlier unpaid periods out of the figure while the rule calls it "the figure a member must pay to bring a Circle membership back into good standing" | observation **O5** |
| delinquency: "where the tier suspends benefits in grace the member may not redeem points or benefit credit until the dues are settled" | not addressed by any extended policy | inherited → **O3** |
| delinquency: grace-day counting, reinstatement window, reinstatement fee, max reinstatements | untouched | inherited, no conflict |

Seat charges: no base sentence of either referenced policy authorises a recurring seat charge inside a
dues settlement. `seat_addition_fee_usd` is a charter parameter ("Fee to add one further seat beyond
those included"), so the *value* is drawn from the charter, but charging it on a settlement for seats
already attached is a procedure neither base policy states. Observation **O6**, and the ladder it hangs
on is finding **D9**.

**`membership_ext_year_benefit_credit_grant`** vs `membership_benefit_grant_cycle`,
`membership_combo_protection_interaction`:

| base sentence | extended treatment | declared? |
| --- | --- | --- |
| grant_cycle: "The named benefit credits of the tier are granted once per membership year, on the activation anniversary, and the grant year is recorded so a second grant in the same year cannot be booked." | replaced by a per-member computed figure | ✔ named |
| combo: "the service credit of the tier is granted as well as the anniversary reward rather than instead of it" | replaced by the plan-backed starting figure | ✔ named |
| grant_cycle: "A membership activated part way through a year is granted the full credits of its tier for that year; credits are never prorated on the way in." | extended scales by a spend multiple and nets prior grants, but never prorates on entry | inherited, no conflict |
| grant_cycle: "An upgrade grants the difference between the new tier's credits and the credits already granted in that membership year" | extended's `counted_prior_grant_window` tier 1 implements exactly this on a tier change with a proration | inherited, consistent |
| grant_cycle: "A granted credit stays spendable for the expiry days of the tier and is then written off" | untouched | inherited |
| grant_cycle: "Nothing is granted for a membership year in which the membership was in lapsed or cancelled status on the anniversary day." | untouched; `counted_prior_grant_window` tier 2 presupposes a lapsed-then-reinstated record, which is compatible | inherited |
| combo: "The protection plan discount of the tier is applied to the plan price before the plan bonus points are worked out" | belongs to accrual, not to this policy | n/a here |
| combo: "Where the customer holds several plans the interaction is counted once per membership year, not once per plan." | extended reads one plan through `CFIELD` | see **D8** |

**`membership_ext_benefit_credit_application`** vs `membership_benefit_redemption`:

| base sentence | extended treatment | declared? |
| --- | --- | --- |
| "Where the tier allows only one credit per charge, the credit that leaves the customer paying least is applied…; where the tier is additive, credits are applied together up to the value of the charge and never beyond it." | replaced by "the smaller of the credit standing under that named benefit and the part of that charge the member is left to meet" | ✔ named |
| "**A benefit credit is spent only against a charge of the kind the benefit names**: the installation credit against installation labour, the delivery credit against a delivery charge, the haul-away credit against a haul-away charge, and **the service credit against bench or on-site repair labour**." | extended builds "the part of the charge the member is left to meet" out of **labour + parts + attendance charges** | **NOT named → D4** |
| "A benefit code that already has a redemption booked against the same charge reference is not redeemed a second time." | carried verbatim into the extended rule | inherited ✔ |
| "A credit is never spent against tax, against dues, or against the price of merchandise." | extended's base excludes tax and merchandise but includes a trip charge and parts | see **D4** |
| "Once the membership has booked as many redemptions in the membership year as the tier allows, **measured by membership_msr_benefit_redemptions_term**, further redemptions are refused until the next anniversary." | extended measures the count over "the twelve months ending on the handling day" and turns the allowance into a taper (`redemption_headroom`) instead of a refusal | **NOT named → D5** |
| "Where the charge is later reversed the credit is restored by a fresh grant carrying the same benefit code…" | untouched | inherited |

**`membership_ext_purchase_points_accrual`** vs `membership_points_accrual`,
`membership_combo_protection_interaction`:

| base sentence | extended treatment | declared? |
| --- | --- | --- |
| "Points are earned on qualifying merchandise spend, which is the merchandise total of the purchase net of tax, delivery, installation and every discount applied at the till." | TechWorks labour brought into the same spend | ✔ named |
| "The base rate of the tier … applies to all qualifying spend, and the computing, mobile and home-theatre bonus or the major appliance bonus is added on top of the base rate **for the part of the spend in that department**…" | the built rate applies to the whole of the spend | ✔ named |
| "Once the membership has earned the yearly points cap of its tier within one calendar year … read against membership_msr_points_earned_12m only for the part of the window falling inside the calendar year." | replaced by a rolling-twelve-month cap | ✔ named |
| "A protection plan bought at the same time earns the plan bonus percentage of the plan price in points, and this is booked as its own earning occasion rather than folded into the purchase." | folded into the same occasion | ✔ named |
| combo: "while the customer holds at least one protection plan standing active, the plan bonus percentage of the tier is earned on every protection plan bought in that membership year" | replaced by the premium-month / premium-window ladder on the covered item's price | ✔ named |
| "Earned points are rounded to the nearest whole point, **with a half point rounded up**." | `RND(x, 0)` is Python `round`, i.e. half-to-even | **NOT named → observation O7** (no half-point arises on task 1) |
| "Points on a purchase that is later returned are removed as a goodwill adjustment against the original purchase reference." | untouched; task 1's world carries an authorised refund on order `KES-3180-0214`, whose accrual rows are on the ledger | inherited → observation **O8** |
| "No points are earned while the membership stands in grace on a tier that suspends benefits, and none at all once it has lapsed or been cancelled." | untouched | inherited (task 1's membership is active) |
| combo: "The protection plan discount of the tier is applied to the plan price before the plan bonus points are worked out, so the discount lowers both the price and the points." | extended takes the bonus on the covered item's price with no discount applied | observation **O9** (the base sentence speaks of the plan price, which extended no longer uses) |

**`membership_ext_points_expiry_sweep`** vs `membership_points_expiry`:

| base sentence | extended treatment | declared? |
| --- | --- | --- |
| "A point stays live for the expiry months of the tier held on the day it was earned, counted from the end of the calendar month in which it was earned, and is swept off at the end of the sweep month." | replaced by a life counted back from the handling day | ✔ named |
| "The sweep takes the oldest live points first, and one sweep row is booked per sweep year…" | carried ("the oldest points having gone first"; "One sweep entry is booked for the sweep year") | inherited ✔ |
| "An expiry sweep is booked only against a membership standing in active, grace or lapsed." | untouched | inherited |
| "A lapse forfeits every live point at once…" / "Points already swept are never restored as a courtesy…" | untouched | inherited |

Neither base nor extended anywhere defines a **sweep year** or when one closes, while
`sweep_expired_points_bcca39ef` takes `expiry_cycle_year` as a scored argument. → **D17**

**`membership_ext_points_redemption_release`** vs `membership_points_redemption`:

| base sentence | extended treatment | declared? |
| --- | --- | --- |
| "Points are redeemed in whole blocks of the tier's minimum redemption block, and a balance below one block cannot be redeemed at all." | `overwrite` declares this superseded, and the replacement text ends with the same clause verbatim — the declaration reorders the arithmetic rather than changing this semantics | ✔ named (observation **O10**: an `overwrite` entry that supersedes nothing) |
| "Points are redeemed only while the membership stands active." | carried verbatim into the extended rule's last sentence | inherited ✔ |
| "The value of a redemption is the tier's value per hundred points applied to the points spent, rounded to the nearest cent." | inverted to give `spent_against_worth` | inherited, consistent |
| "A redemption may be taken as a reward certificate, as an instant discount at the till, as a donation…, or, on the tiers that allow it, as a transfer of points…" | untouched; but no enum value means "set against an outstanding order balance", which is what the extended rule's cap is | observation **O11** |
| "Points may never be redeemed against dues, and they may never be paid out as cash." | untouched; the cap is an order balance, not dues | inherited ✔ |
| "Points spent on a purchase that is then returned are restored to the balance as a fresh earning occasion…" | untouched | inherited |

### factor_ladders

Per-policy structure. "3 tiers" always means two stated tiers plus the fall-through.

| policy | factors | parameter / method | tiers each | multi-source | cross_difficulty |
| --- | --- | --- | --- | --- | --- |
| `..._grace_dues_settlement` | 5 | 4 / 1 | 3 | 5 of 5 | credit, protection |
| `..._year_benefit_credit_grant` | 6 | 4 / 2 | 3 | 6 of 6 | protection, service |
| `..._benefit_credit_application` | 6 | 3 / 3 | 3 | 6 of 6 | protection, service |
| `..._purchase_points_accrual` | 6 | 4 / 2 | 3 | 5 of 6 | orders, protection, service |
| `..._points_expiry_sweep` | 4 | 2 / 2 | 3 | 4 of 4 | credit |
| `..._points_redemption_release` | 5 | 4 / 1 | 3 | 5 of 5 | protection, returns, service |

Counts against the bounds: every policy declares 4–6 factors with at least 2 `parameter` and at least
1 `method`; every ladder has 3 tiers; each task's computations carry at least one multi-source factor
and at least one `cross_difficulty` factor, and the categories those read are seeded in both tasks'
`initial_state` (task 0: `credit_accounts`+`credit_events`, `protection_plans`+`protection_events`,
`service_agreements`+`service_events`; task 1: those plus `purchase_orders`+`order_events` and
`return_authorizations`+`return_events`). `decides` is an input binding, never `result`, in all 32
factors, and each factor's `bindings` set is disjoint from every other factor's inside its policy. ✔

Every tier is stated in the `rule` with its condition and its value/method, and implemented as a
branch of the `decides` binding; no tier is compute-only or prose-only. ✔

**Pairwise-disjoint tiers — fails on four ladders (D11).** As stated in the `rule`, tier 1 and tier 2
overlap in:

- `spend_backed_multiple` — t1 "reaches the qualifying spend figure of the tier and three or more
  earning occasions", t2 "reaches the mid spend share of the qualifying spend figure of the tier and
  two or more earning occasions". t1 ⊂ t2.
- `tenure_addition_rule` — t1 "reach the long tenure months of this schedule" (60), t2 "reach the
  middle tenure months of this schedule" (24). t1 ⊂ t2.
- `redemption_headroom` — t1 "reach the yearly redemption allowance of the tier" + "credit spent … at
  or above the install credit figure", t2 "reach the half allowance share of that allowance" +
  "… at or above the delivery credit figure". t1 ⊂ t2 on every tier where
  `install_benefit_credit_usd >= delivery_benefit_credit_usd`, which is every tier.
- `counted_prior_grant_window` — t1 "the day the tier now recorded took effect falls within the twelve
  months … and the ledger carries a proration charge booked in that window", t2 "the membership record
  carries a lapse day and its reinstatement count stands above nothing". Independent conditions that
  can both hold; not a nested threshold, so ordering does not even suggest a resolution.

The author's own drafting standard shows the exclusion was required: one policy over,
`volume_rate_uplift` writes "reaches the mid spend share of the qualifying spend figure of the tier
**but not the figure itself**" for exactly the shape `spend_backed_multiple` leaves open.

**Tier outcomes distinct** — no two tiers of any ladder select the same value or method. ✔

**Honest labels — fails on one (D12).** `spend_backed_multiple` is labelled `method`, but its three
tiers substitute 1.2 / 1.1 / 1.0 into the unchanged expression `year_credit_figure * spend_multiple`.
Nothing about how the quantity is computed changes; a number does. The identical shape in
`membership_ext_purchase_points_accrual` is labelled `parameter` (`volume_rate_uplift`, 0.5 / 0.25 / 0).
The other four `method` factors (`counted_entry_window`, `counted_prior_grant_window`,
`counted_line_window`, `labour_basis_taken`, `parts_brought_in`,
`attendance_charges_brought_in`, `discount_netted`, `point_life_window`,
`spend_set_against_aged_pool`, `live_balance_basis`) each change a window, an anchor or the expression
itself, and are honestly labelled; every `method` tier names a computation the charter states. ✔

**Conditions and outcomes that line of business actually holds — fails in three places.**

- **D9** `seat_charge_component`: the discriminator between tier 1 ("the seat addition fee … for each
  seat above the allowance") and tier 2 ("the seat addition fee … once only") is "the ledger carries no
  enrollment fee entry booked in the twelve months ending on the handling day". `enrollment_fee_usd` is
  `0.00` on five of the six Circle tiers (only Circle Business Pro charges one, at $25.00), and base
  `membership_dues_billing` says the enrollment fee "is billed once on the enrollment day" — so for any
  member enrolled more than a year ago the conjunct holds by construction. It holds of essentially
  every customer who reaches this write, it divides no one, and an enrollment fee has no business
  bearing on how many seats are attached.
- **D10** `counted_entry_window`: tier 1 is "the membership stands in grace **and** the term now being
  billed began within the twelve months ending on the handling day". `current_term_start` is by
  definition the start of the term now being billed, and every Circle term is annual or monthly, so on
  any record whose dues are billable (`application_received`, `active` or `grace` per
  `membership_dues_billing`) the second conjunct is always true. Tier 2 ("began more than twelve months
  before the handling day") is therefore unreachable, and the conjunct that makes this factor
  multi-source is vacuous.
- **D15** tiers whose outcome is money or points the customer does not owe, or a credit they do not
  hold. Each is a fall-through-adjacent tier that substitutes a nominal figure of the same kind when the
  condition the quantity is *about* does not hold:
  - `plan_premium_brought_in` t2 — "Where a plan stands active or in claim hold and no such shortfall
    stands, the monthly premium figure of that plan is added": a member fully paid up on their
    ShieldCare premium has a month's premium added to the figure they must pay to bring their
    *membership* back into good standing.
  - `store_credit_set_against_dues` t2 — "Where that credit account stands active and its store credit
    balance is below the smallest amount of store credit that account may spend at once, that smallest
    spendable amount is set against the amount": store credit the account does not hold is spent, and
    the very meaning of a minimum spend is that a balance below it cannot be spent at all.
  - `cover_already_met` t2 — "Where a plan stands active or in claim hold and no payout has been booked
    on it in that window, the deductible figure that plan carries is taken off": the deductible is what
    the *member* pays, and a plan that has paid out nothing has met nothing.
  - `points_held_for_cover` t2 / `points_held_for_work` t2 — points are held back against a deductible
    that is not outstanding and against service charges that are not outstanding.
  - `value_already_taken_as_store_credit` t2 — "Where that credit account stands active and no such
    posting stands in that window, the points set against the pool on that account are what the
    smallest amount of store credit that account may spend at once is worth at the same rate": points
    the member "has already had the value of" are deducted although they have had the value of nothing.
  - `points_held_for_returns` t1 — "Where a return authorisation … stands authorised, received or
    inspected and a refund was authorised on it in the three months ending on the handling day, the
    points held back for goods coming back are that refund taken at the base rate of the tier", under a
    framing sentence that reads "Points are then held back against money **the member already owes
    Northbeam** on other lines". An authorised refund is money Northbeam owes the member; no retailer
    withholds a member's points because it owes them a refund.

**Honest baselines — fails on two (D13, D14).** Every other factor's declared `baseline` is exactly what
its policy's `baseline.rule` states for that input, checked one by one. The two failures:

- **D13** `counted_line_window`. `baseline: {merch_window: '12'}`, and the ladder's fall-through reads
  "the merchandise lines counted are those billed in the twelve months ending on the handling day".
  But `membership_ext_purchase_points_accrual.baseline.rule` states, verbatim: "The spend the points
  are earned on is the merchandise lines billed on the order **in the month ending on the handling
  day**." A reader of the computation document alone therefore takes a one-month window — which is
  exactly what the *gold* tier of the ladder selects. The factor cannot bear weight against its own
  honest baseline.
- **D14** `membership_ext_benefit_credit_application.baseline.rule` is not self-sufficient. It keeps
  both "The part of the charge the member is left to meet **starts from the labour billed on the
  TechWorks job the charge belongs to**." and "**Where neither of those holds**, the labour taken is
  the least labour billed on that service at its labour rate." — with the two Where-clauses that
  "those" refers to stripped out. The reader has a dangling anaphor and two candidate numbers for
  `labour_taken`, and the same stripping leaves three further dangling "Where neither of those holds"
  sentences in the same document (parts, attendance, headroom).

Beyond those two, each policy's `baseline.rule` names every sentence it uses inside the policy's own
`rule`, and its `baseline.params` keys are the ones the baseline arithmetic reads. ✔

### findings

Each finding names the tasks whose files carry the demonstration.

- **D1 — SOURCE-POLICY RED. `membership_ext_grace_dues_settlement.rule` contradicts itself on the late
  fee.** Symptom: two sentences of one rule reach different conclusions in the same situation. Root
  cause: a blanket commitment was written above a ladder whose fall-through withdraws it. Evidence,
  both verbatim from `membership.extended.yaml` → `extended_policies[0].rule`: "The late fee owed for
  the billing period that has fallen overdue is then added, and it is added whether or not the ledger
  already carries an entry for it." and "Where neither of those holds, no late fee is added."
  Situation in which they disagree: a membership in grace with no dues payment booked in the counted
  window — the first sentence adds the late fee, the second adds nothing. Affected artifact:
  `membership.extended.yaml`, `extended_policies[0].rule` and `compute.late_fee_component`. Bears on:
  task 0 (does not bite at the scored moment — see `0.md`).
- **D2 — SOURCE-POLICY RED. `membership_ext_points_redemption_release.rule` contradicts itself on the
  rate at which amounts held back are converted to points.** Evidence, verbatim from
  `extended_policies[5].rule`: framing — "Points are then held back against money the member already
  owes Northbeam on other lines, **each amount held back being taken at the tier's value per hundred
  points**." ; returns tier 1 — "the points held back for goods coming back are that refund **taken at
  the base rate of the tier**." ; returns tier 2 — "the points held back for goods coming back are the
  purchase price of the returned item **taken at the base rate of the tier**." The same amount is
  converted by $1.10 per 100 points under the framing sentence and by 2.0 points per dollar under the
  tiers — a factor of 100 apart. Bears on: task 1, where the two readings give 16,900 and 25,400
  points (demonstrated in `1.md`).
- **D3 — SOURCE-POLICY RED. Undeclared override of `membership_dues_billing`'s application order.**
  Base: "A payment is applied to the oldest unpaid billing period first, and any remainder to the
  next". `membership_ext_grace_dues_settlement.overwrite` names only the late-fee clause, so this one
  is inherited in full; yet the edge it grounds fixes `applied_period_start` to "the billing period the
  membership record is now in". Bears on: task 0 (`applied_period_start` 2026-05-15 vs 2026-09-01,
  demonstrated in `0.md`).
- **D4 — SOURCE-POLICY RED. Undeclared override of `membership_benefit_redemption`'s "charge of the
  kind the benefit names".** Base: "A benefit credit is spent only against a charge of the kind the
  benefit names: … the service credit against bench or on-site repair labour." and "A credit is never
  spent against tax, against dues, or against the price of merchandise."
  `membership_ext_benefit_credit_application.overwrite` names only the stacking clause; the extended
  rule nevertheless builds the base of the credit as "the labour, the parts and the attendance charges
  are added". Bears on: task 0 (10.08 vs 75.15, demonstrated in `0.md`).
- **D5 — SOURCE-POLICY RED. Undeclared override of `membership_benefit_redemption`'s allowance
  measure.** Base: "Once the membership has booked as many redemptions in the membership year as the
  tier allows, **measured by membership_msr_benefit_redemptions_term**, further redemptions are refused
  until the next anniversary."; `measures[membership_msr_benefit_redemptions_term].window` = "the
  current membership year, from the activation anniversary on or before the handling date to the day
  before the next anniversary". Extended counts `COUNT('membership_events', within_months=12,
  event_type='membership_benefit_redeem')` and calls the result "the redemption headroom **of the
  membership year**", turning a refusal into a taper. Not named in `overwrite`. Bears on: task 0
  (93.94 vs 75.15, demonstrated in `0.md`).
- **D6 — SOURCE-POLICY RED (check 6/7). The application ← grant prerequisite sentence is broader than
  the edge's condition, and the state it names is already satisfied.** Sentence: "The credit set
  against a charge is worked out only after the ledger carries the benefit credit granted for the
  membership year in which that charge falls." Condition: "a benefit grant entry **under the same named
  benefit** whose grant cycle year is the membership year the charge falls in". The sentence names no
  benefit code, so an agent reading the rule looks for any benefit grant for the current membership
  year. Bears on: task 0, whose seed already carries two (`grant_cycle_year: "2026"`), so the
  prerequisite reads as met and the derived answer becomes 0.00 (demonstrated in `0.md`).
- **D7 — SOURCE-POLICY RED (check 2). "The same named benefit" is implemented as a constant.**
  `membership_ext_year_benefit_credit_grant.compute.prior_same_code_grants` and
  `membership_ext_benefit_credit_application.compute.grants_same_code_12m` /
  `redeems_same_code_12m` all filter `benefit_code='service_credit'`, while both rules say only "the
  same named benefit" / "the named benefit it belongs to". Neither rule anywhere says which named
  benefit the year's credit belongs to, although `benefit_code` is a scored argument of both
  `grant_benefit_credit_b1d93258` and `apply_benefit_credit_8295b346` with a six-value enum, and the
  grant's own starting-figure ladder can take the *anniversary reward* figure or a *plan deductible* —
  neither of which names `service_credit`. Bears on: task 0 (the code is recoverable only through the
  downstream policy and the charge's kind — see `0.md`).
- **D8 — SOURCE-POLICY RED (check 2). Cross-category reads carry no correlation key to the object the
  rule names.** Every `CFIELD`/`CPARAM` in this charter is called with no `**eq` filter, and the
  evaluator resolves it as `hs[0]` — the first row of that category's holding table whose
  `customer_id` matches. Every `XSUM`/`XCOUNT` aggregates **all** of the customer's rows in that
  category's event table. The rules, however, name a specific object: "the balance standing outstanding
  on **the order it is put against**", "the department of **the order**", "the merchandise lines billed
  on **the order**", "the labour billed on **the TechWorks job the charge belongs to**". On a profile
  holding two purchase orders the row taken is decided by seed key order and nothing else. Bears on:
  task 1 (demonstrated in `1.md`: re-serialising `initial_state` with sorted keys moves
  `CFIELD('orders','balance_outstanding')` from 2,480.00 to 0.00 and `CFIELD('orders','item_category')`
  from `laptop_and_tablet` to `small_appliance`, taking `points_earned` from 23,984 to 15,404 and
  `points_redeemed` from 25,400 to 0).
- **D9 — SOURCE-FACTOR RED. `seat_charge_component`'s tier discriminator holds of every customer who
  reaches the write.** Evidence and reasoning in `factor_ladders` above. Bears on: task 0.
- **D10 — SOURCE-FACTOR RED. `counted_entry_window` tier 1's second conjunct is vacuous and tier 2 is
  unreachable.** Evidence and reasoning in `factor_ladders` above. Bears on: task 0.
- **D11 — SOURCE-FACTOR RED. Four ladders whose tiers overlap as stated.** `spend_backed_multiple`,
  `tenure_addition_rule`, `redemption_headroom`, `counted_prior_grant_window`. Bears on: task 0, where
  three of the four have both tiers' conditions true at the handling moment and yield 192.90, 192.80,
  182.90 and 93.94 as further defensible values (demonstrated in `0.md`). None of task 1's fifteen
  ladders overlaps.
- **D12 — SOURCE-FACTOR RED. `spend_backed_multiple` is mislabelled `method`.** Evidence and the
  in-charter counter-example (`volume_rate_uplift`, labelled `parameter`) in `factor_ladders` above.
  Consequence: `membership_ext_year_benefit_credit_grant` declares 2 `method` factors and has 1;
  counting only factors that survive the tests, its labels are 5 `parameter` / 1 `method`. Bears on:
  task 0.
- **D13 — SOURCE-FACTOR RED. `counted_line_window`'s baseline is dishonest, and against the honest one
  the factor is decoration.** Evidence in `factor_ladders` above. Bears on: task 1.
- **D14 — SOURCE-FACTOR RED. `membership_ext_benefit_credit_application.baseline.rule` is not
  self-sufficient.** Evidence in `factor_ladders` above. Bears on: task 0 (119.00 or 177.80,
  demonstrated in `0.md`).
- **D15 — SOURCE-FACTOR RED. Seven tiers whose outcome is money, credit or points the business would
  not move in that situation.** Enumerated with verbatim quotations in `factor_ladders` above. Bears
  on: task 0 (`plan_premium_brought_in`, `store_credit_set_against_dues`, `cover_already_met`) and
  task 1 (`points_held_for_returns`, `points_held_for_cover`, `points_held_for_work`,
  `value_already_taken_as_store_credit`).
- **D16 — SOURCE-CHAIN RED. The redemption ← sweep edge's `condition` is already true at task 1's
  opening.** `condition: the membership ledger carries a sweep entry for the sweep year now closed
  against the points that have outlived their life`. On 2026-09-18 the sweep year now closed is 2025,
  and task 1's seed carries `membership_events/3883a251-c47b-44e5-98ea-37f815287717`
  (`event_type: membership_points_expire`, `expiry_cycle_year: "2025"`, `event_date: 2025-01-31`,
  `points_delta: -6000`). Demonstrated in `1.md`, together with the second horn: read at the
  sentence's own strength ("**every** sweep year already closed"), the missing years are 2020–2022 and
  2024, so the resolving write would have to be booked for one of those, not for the year gold books.
- **D17 — SOURCE-POLICY RED. Nothing in the charter says what a sweep year is or when one closes,
  although `expiry_cycle_year` is a scored argument.** `sweep_expired_points_bcca39ef` takes
  `expiry_cycle_year` ("the sweep year this forfeiture belongs to, written as the four-digit calendar
  year YYYY"); `membership_ext_points_expiry_sweep.rule` says only "One sweep entry is booked for the
  sweep year"; base `membership_points_expiry` says only "one sweep row is booked per sweep year"; and
  the `compute` produces a figure with no year in it. Bears on: task 1 (2024 / 2025 / 2026 all
  defensible — demonstrated in `1.md`).

Observations (no consequence demonstrable per the Core-constraints table; recorded, not grounds for
rework):

- **O1** `within_months=n` is a month-day count, so a window the rule anchors to a day
  (`current_term_start`, `tier_effective_date`, `activation_date`) reaches back further than the rule
  says. No row falls in the extra band on either task's world.
- **O2** `membership_ext_points_redemption_release.earned_in_life` measures a point's life as a flat
  `P('points_expiry_months')` while `membership_ext_points_expiry_sweep.point_life_months` measures it
  as that figure ±6. The two policies of one charter give the life of a point two lengths. Each rule is
  internally consistent, so nothing is undecidable.
- **O3** base `membership_dues_delinquency`: "where the tier suspends benefits in grace the member may
  not redeem points or benefit credit until the dues are settled" is a base sentence stating a
  cross-problem order on which task 0's tree rests; the extended rules carry prerequisite sentences of
  their own on both hops, so this is an observation. `benefit_suspension_on_grace` is `true` on Circle
  Total Annual.
- **O4** base `membership_tier_migration`: "A membership standing in grace may be upgraded only after
  the outstanding dues are settled" grounds no declared edge and no task's tree rests on it.
- **O5** the grace/term settlement window drops earlier unpaid periods out of a figure the rule calls
  "the figure a member must pay to bring a Circle membership back into good standing", against base
  `membership_dues_billing`: "Dues already billed for a period the customer has used are owed in full".
- **O6** no base sentence authorises a recurring seat charge inside a dues settlement.
- **O7** base "Earned points are rounded to the nearest whole point, with a half point rounded up" vs
  `RND(x, 0)` = half-to-even; not named in `overwrite`; no half-point arises on task 1.
- **O8** base "Points on a purchase that is later returned are removed as a goodwill adjustment against
  the original purchase reference" is inherited, and task 1's world triggers it (an authorised refund
  of 96.00 on `KES-3180-0214`, whose accrual rows are on the ledger), but
  `book_purchase_points_235cc6ac.points_earned` is documented as "a positive whole number of points",
  so the write base demands cannot be expressed; and base names no amount, so it is indeterminate
  anyway.
- **O9** base combo "The protection plan discount of the tier is applied to the plan price before the
  plan bonus points are worked out" is not named in `overwrite`; extended takes the bonus on the
  covered item's price instead of the plan price, so the clause arguably lapses rather than conflicts.
  Honouring it would give task 1 23,874 instead of 23,984.
- **O10** `membership_ext_points_redemption_release.overwrite[0]` declares
  "Points are redeemed in whole blocks of the tier's minimum redemption block, and a balance below one
  block cannot be redeemed at all" superseded by a replacement that repeats it verbatim.
- **O11** `redeem_reward_points_8621cafe.redemption_kind` has no enum value meaning "set against an
  outstanding order balance", which is what the extended rule's cap is; `instant_checkout_discount`
  ("the points come off a purchase at the till there and then") is the nearest.
- **O12** the settlement rule directs that store credit standing on the customer's Northbeam credit
  account "is set against the amount", but no tool of this difficulty debits
  `credit_accounts.store_credit_balance`, so the terminal state leaves the credit standing and the dues
  reduced by it.
- **O13** `settle_membership_dues_c8b60f0e` updates only `dues_outstanding`; the membership's `status`
  is left at whatever it was. Against the charter's own `lifecycle` (`from: grace, to: active, by:
  agent, means: the outstanding dues and the late fee were settled inside grace`) this is a terminal
  state the charter says should not exist. Turned into a demonstrated defect for task 0 as **T0-1** in
  `0.md`.

## closing_checklist

**Not reached.** Both tasks carry RED verdicts on all four relationships, so the difficulty does not
close out and the instantiation-stage gates were not re-run on a final form. Against Step 4's list, as
of the post-reveal pass:

- per-task audit files correspond one-to-one with the tasks (`0.md`, `1.md`) and this file sits
  alongside them; there is no previous revision to preserve; **neither comparison section carries a
  PASS** ✗
- the six extended policies are fully covered and the two tasks' scopes are pairwise disjoint over the
  whole problem tree; task tools and GT are closed; every uuid8 is independently generated and frozen ✔
- **problem trees**: each task declares 2 prerequisite problems, 2 `value_input` edges, one
  `owner=user` write and no cycle, and the whole-difficulty graph is a DAG ✔ — **but one declared edge
  per task is already satisfied at its opening** (`0.md` → T0-3, `1.md` → T1-1), and striking task 0's
  leaves that tree with no `owner=user` write at all ✗
- **computations**: every computation declares 4–6 factors with 2 `parameter` and 1 `method`, at least
  one multi-source and one cross-difficulty factor per task, three tiers per ladder stated in full in
  the rule, distinct outcomes, and every factor moves the number against its declared baseline, with the
  whole baseline giving a definite figure different from gold ✔ on the machine reading — **but four
  ladders overlap as stated (D11), one factor is mislabelled (D12), one baseline is dishonest and its
  factor then does not bear weight (D13), one `baseline.rule` is not self-sufficient (D14), two tier
  conditions hold of every customer who reaches the write (D9, D10), and seven tier outcomes are
  treatments the business would not publish (D15)** ✗
- instantiation-stage gates re-run on a final form: **not applicable** — there is no final form ✗

**Post-reveal corroboration of the pre-reveal section.** Nothing above was revised after the reveal.
Both tasks' revealed `expected`, `baseline_result` and every `factor_sensitivity[].baseline_result`
figure — 35 figures in all — match this auditor's independent recomputations exactly, and both tasks'
`prerequisite_closure` skip-run figures match value for value. Several of the pre-reveal findings are
corroborated by the revealed fields themselves rather than contradicted by them: D4 by `tasks/0.json →
design_rationale` ("a credit is spent only against a charge of the kind the benefit names … never
against tax, dues or merchandise", while `compute` adds parts and a trip charge); D8 by `tasks/1.json →
design_rationale` ("one order, one department", on a profile holding two orders in two departments);
D16 and D17 by `tasks/1.json → prerequisite_closure.edges[1].why_false`, which argues a state
("no sweep entry standing in the twelve months ending on the handling day") that appears in neither the
prerequisite sentence nor the `condition`.

Two further defects surfaced only at the reveal, both per-task and both recorded in the task files:
`tasks/1.json → evaluation_criteria[15].arguments.qualifying_spend_usd` = 4320.0 against the policy's
5,720.00 (`1.md` → T1-9), and `evaluation_criteria[19].arguments.redemption_kind` = `reward_certificate`
against a request to put the points on an open invoice (`1.md` → T1-10); plus three false arithmetic
intermediates in `tasks/1.json → design_rationale` (`1.md` → T1-13).

---

## revision_2

### revision_2_frozen

- auditor: the same independent auditor that produced revision 1, resumed with its round-1 derivations and
  evidence intact; revision 1 above is left untouched
- revision time: 2026-09-18T10:42Z
- re-derivation was **mandatory, not optional**: all four inputs moved, so no section is carried forward by
  hash.

| artifact | revision 1 | revision 2 | re-derived? |
| --- | --- | --- | --- |
| `membership.extended.yaml` | `ddf9b56fdd9c5727` | `9af67e006458c5c8` | in full |
| `task_tools.py` | `dffb81181aa8f29b` | `12c5fa8b37b418f3` | in full |
| `tasks/0.json` | `341dfd1fbab5013e` | `f477f0f62ef18b98` | in full |
| `tasks/1.json` | `aded04201af8e69b` | `5809841c6607b4e6` | in full |

- masked views supplied at `masked_view_sha256_16` `5424f1bda0480b04` (0) and `9aa0efe8286297be` (1). **The
  masking tool is fixed**: I verified that each masked view's `initial_state` is byte-identical to the source
  file's `initial_state` under `json.dumps` and preserves its key order table by table, and that
  `frozen_time` matches. Revision 1's method note therefore no longer applies; this round's derivations were
  run against `frozen_time` and `initial_state` and nothing else.
- this round is **not** a fresh blind derivation and does not claim to be. Revision 1's blind derivation is
  the baseline; this round re-derives every figure from the amended charter and checks each revision-1
  finding for genuine closure, new breakage and regression.
- gate snapshot supplied by the coordinator (`replay --check`, nothing written back); all green except
  `check_traceability`, deferred to step 3 by design. Accepted as an entry condition, not re-run.

### policy_conflict_scan (re-derived)

The base copy inside `membership.extended.yaml` is still **verbatim identical** to
`blueprint/products/membership.yaml` on all ten shared top-level keys (`category`, `display_name`,
`binding`, `lifecycle`, `accounts`, `parameter_schema`, `variants`, `events`, `measures`, `policies`) —
re-checked by canonical-JSON comparison. No base rewrite. ✔

Six extended policies, same ids, same `target_tool`s, same `computes`, same triggers. Each
`(target_tool, computes)` pair is still claimed by exactly one policy. ✔ `charter_scope` now confirms the
3 + 3 partition I derived independently: task 0 claims the benefit-credit trio, task 1 the reward-points
trio; pairwise disjoint and jointly complete over the six. ✔

Two rules contradicted **themselves** in revision 1 (D1, D2). Both are gone — see the disposition table.

### rule_compute_equivalence (re-derived)

Every binding of every policy carries a `compute_basis` entry that is a verbatim sentence group of that
policy's own `rule`; every sentence of every `baseline.rule` is verbatim present in the corresponding full
`rule` (checked mechanically on all six); every non-fall-through ladder tier is a condition the rule states
and a branch of the `decides` binding, and every branch of every `decides` binding is a tier the rule
states. No tier is compute-only or prose-only. Every ladder's tiers select **distinct** values or methods
(checked mechanically across all 32). ✔

The two revision-1 equivalence defects (D7, D8) are closed. Three residual gaps, all new and all recorded
as observations because no consequence is demonstrable on either task's world: **N3**, **N4**, **N5** below.

Revision 1's observation **O1** — `within_months=n` being a month-day count while the rule anchored a
window to a record date — is **closed**: every window in the amended charter is a fixed month count
(1, 3, 6, 12, 24, 36). `MONTHS(F(...), NOW)` survives only in `months_on_tier` and `tenure_months`, where
it is a comparand ("falls within the twelve months ending on the handling day", "reach the long tenure
months"), which is exactly what those rule sentences say. ✔

### action_binding_and_uuids (re-derived)

The six uuid8s are **unchanged and still independent**: `b1d93258`, `c8b60f0e`, `8295b346`, `235cc6ac`,
`bcca39ef`, `8621cafe` — eight hex digits each, no shared stem, no sequence, none reused. ✔

Tool bodies re-read in full. Every tool is still exactly: `ctx.find` the holding, `if not rows: return
Error`, `ctx.create` the ledger row, `ctx.update` the holding, return the receipt. One `if`, two returns,
no branch on any prerequisite, no balance check, no status check, no dedup check. **No tool judges a
prerequisite.** ✔

One tool body changed materially, and it is a fix: `settle_membership_dues_c8b60f0e` now writes
`status="active", grace_start_date=""` alongside `dues_outstanding`, and its receipt says "the membership
now reads as active". That closes **O13** and removes the mechanism of **T0-1**.

Docstrings re-scanned for ordering words and other tools' names. `settle_membership_dues_c8b60f0e` now hits
`first` ("the **first** day of the billing period") and `already` ("the payment card **already** kept on the
profile"); `redeem_reward_points_8621cafe` hits `already` ("off a charge **already** standing on the
account"). All are date parts or enum glosses; none states an action's position in a sequence and no
docstring names another tool. ✔

### prerequisite_graph (re-derived)

Still four edges over six nodes, still two chains with no edge between them, still a DAG with no
cross-task reference. Mechanically re-verified: every `problem` names another policy id in this file;
every `kind` is `value_input` and every `gate` names a binding that exists in the blocked policy's
`compute` (`dues_standing_adjustment`, `credit_standing`, `earned_in_life`, `swept_in_life`); every
`resolved_by` is the depended-on policy's own `target_tool`; every `form` is `state` and no
`fallback_reason` is present on any edge. ✔ No authoring-viewpoint phrasing. ✔

Two edges changed their gate and their condition (the settlement edge from `arrears_offset` to
`dues_standing_adjustment`, the sweep edge to the calendar-year sweep entry). **Both `condition`s are now
neither strengthened nor weakened relative to their sentences** — the defect behind D6 and D16.

### prerequisite_sentences (re-derived)

All four `policy_source` sentences are verbatim in the **blocked** policy's own rule, and none is restated
in the depended-on policy's rule (checked mechanically). Four-point test:

1. grant ← settlement — "The credit granted for a membership year is worked out only after the dues charged
   for the billing period the membership is now in stand met in full by the payments applied to that
   period." Connective "only after" ✔; state form, in the words the tables use
   (`billing_period_start`, `applied_period_start`) ✔; no tool, policy id or snake_case token ✔; strength
   equals the `condition` ✔. One write brings it about: only `settle_membership_dues_c8b60f0e` creates a
   `membership_dues_payment` row ✔.
2. application ← grant — "The credit set against a charge is worked out only after the ledger carries, for
   the membership year in which that charge falls, a grant of the very named benefit that charge's kind
   calls for." Connective "only after" ✔; state form ✔; **strength now equals the condition** ✔, because the
   sentence names the specific benefit and the same rule defines the mapping ("The named benefit a charge's
   kind calls for is the service credit where the charge is bench or on-site repair labour, …"). One write
   brings it about ✔.
3. redemption ← accrual — "The points a redemption spends are settled only after the ledger carries an
   earning entry for every purchase already billed on the profile." Unchanged from revision 1 and still
   passing ✔.
4. redemption ← sweep — "No points are released until the balance carries the sweep entry owed for the
   calendar year the handling day falls in." Connective "until" ✔; state form ✔; **strength now equals the
   condition** ✔, and the quantity is now defined: `membership_ext_points_expiry_sweep.rule` says "The sweep
   year a forfeiture belongs to is the calendar year the day it is booked falls in, and one sweep entry is
   booked for each sweep year". One write brings it about ✔.

No rule carries a second wording of a dependency, another problem's tool name or an aggregated chain. ✔

### override_declarations (re-derived)

Fourteen `overwrite` entries across the six policies (revision 1 had eleven). **Every
`superseded_clause` is a verbatim substring of the named `base_policy`'s rule** — checked mechanically,
14/14. ✔ The four undeclared overrides of revision 1 (D3, D4, D5, O7) and the two silent drops (O8, O9) are
disposed of below. Sentence-by-sentence sweep against each `base_policy_refs` entry found no new
undeclared override that bites either task; three provisions are now inherited without an extended
counterpart and none of them fires on either world — **N5**.

### factor_ladders (re-derived)

| policy | factors | parameter / method | tiers | multi-source | cross_difficulty |
| --- | --- | --- | --- | --- | --- |
| `..._grace_dues_settlement` | 5 | 4 / 1 | 3, 4, 3, 3, 3 | 5 of 5 | credit, protection, **returns** |
| `..._year_benefit_credit_grant` | 6 | 5 / 1 | 3 each | 5 of 6 | protection, service |
| `..._benefit_credit_application` | 6 | 2 / 4 | 3 each | 5 of 6 | protection, service |
| `..._purchase_points_accrual` | 6 | 4 / 2 | 3 each | 4 of 6 | orders, **returns**, service |
| `..._points_expiry_sweep` | 4 | 2 / 2 | 3 each | 4 of 4 | credit |
| `..._points_redemption_release` | 5 | 4 / 1 | 3 each | 5 of 5 | protection, returns, service |

Every policy declares 4–6 factors with at least 2 `parameter` and at least 1 `method`; every ladder has at
least three tiers; each task's computations carry at least one multi-source and at least one
`cross_difficulty` factor; every category read is seeded on both worlds. ✔

**Pairwise-disjoint tiers.** 31 of the 32 ladders are now disjoint **as stated**, by explicit exclusion
where the thresholds nest — `spend_backed_multiple` ("but not the figure itself"), `tenure_addition_rule`
("but not the long tenure months"), `redemption_headroom` ("but not the allowance itself"),
`counted_prior_grant_window` ("and the day the tier now recorded took effect falls outside the twelve
months"), `volume_rate_uplift` (unchanged) — and by disjoint status sets everywhere else. **D11 closed on
all four ladders it named.** The one residual is the new `standing_restoration_fee` — **N2**.

**Honest labels.** `spend_backed_multiple` is now `parameter`, which is what it always was. **D12 closed.**
`cover_already_met` is newly relabelled `method`, and the relabel is honest: its tiers no longer substitute
a figure (the old "deductible figure that plan carries") but change the window the payouts are summed over
— three months, twelve months, or nothing. Every `method` factor in the charter now changes a window, an
anchor or the expression; every `parameter` factor changes a number. ✔

**Conditions and outcomes that line of business actually holds.** D9, D10 and D15 are closed:

- `seat_charge_component` is **removed**, taking D9 with it, and replaced by `return_balance_brought_in`,
  whose tiers turn on a live return authorisation with a restocking fee outstanding or a refund outstanding
  — a discriminator that genuinely divides customers and genuinely bears on what a member owes. Its
  direction is now right: what the member owes is added, what is owed to the member is set against. The
  substitute factor audits clean on structure and on weight — **but the figure the seed puts in it breaks
  the returns charter, which is N1.**
- `counted_entry_window` tier 1's second conjunct is now "the ledger carries an annual dues charge booked
  in the twelve months ending on the handling day", a ledger fact that is genuinely falsifiable for a
  member in grace (one who fell into grace over an unpaid **proration** with no annual dues charge inside
  the window), not the definitional truth about `current_term_start` that D10 struck. **D10 closed.**
- all seven D15 tiers are rewritten to real debts or real windows: `plan_money_brought_in` t2 now takes an
  **unsettled** deductible; `store_credit_set_against_dues` t2 now takes only the credit posted inside its
  spendable days, which can never exceed the balance; `cover_already_met` t2 is now a twelve-month payout
  window instead of the member's own deductible; `points_held_for_cover` t2 is an **unsettled** premium;
  `points_held_for_work` t2 is labour actually charged in the month; `value_already_taken_as_store_credit`
  t2 is awards actually posted earlier on the ledger; and `points_held_for_returns` t1 is an **outstanding
  restocking fee** — money the member owes — with t2 a hold against goods in flight. **D15 closed.**

**Honest baselines.** **D13 closed**: `membership_ext_purchase_points_accrual.baseline.rule` now states
"The spend the points are earned on is the merchandise lines billed to the profile **in the twelve months
ending on the handling day**", which is what `baseline: {merch_window: '12'}` encodes, and the factor moves
the number on task 1 (18,432 → 40,832). **D14 closed**: every `baseline.rule` was re-read sentence by
sentence and the dangling-anaphora scan is clean; each now states its factor fall-throughs as standalone
declaratives ("No parts are taken", "Nothing is taken off for cover", "There is no department bonus", "No
points are held back for cover", "Nothing is set against the pool on that account", "The whole of the live
balance may be released"). The one residual is the settlement's — **N6**.

### findings (revision 2)

#### Disposition of every revision-1 item

Charter-global, in the order they were raised:

| item | reworker's claim | my verdict | grounds |
| --- | --- | --- | --- |
| **D1** late-fee self-contradiction | closed | **CLOSED** | the blanket sentence is gone; the rule now reads "A fee for putting the standing right is then taken into the figure on the schedule below." followed by three tiers and "Where none of those holds, no fee for putting the standing right is taken in." No two sentences reach different conclusions in one situation. |
| **D2** hold-back rate contradiction | closed | **CLOSED** | "base rate of the tier" occurs **0** times in `..._points_redemption_release.rule`; "value per hundred points" occurs 6. Every hold-back converts at one rate. |
| **D3 / T0-4** oldest unpaid period | fixed in the world | **CLOSED**, and by a better route than claimed | base's sentence "The money received is applied to the oldest unpaid billing period first, and any remainder to the next." is now carried **verbatim into the extended rule**, so there is nothing to override and no `overwrite` entry is needed; and the ledger was re-seeded so the oldest unpaid period *is* 2026-09-01 (2025-09-01 charged 179.99 / paid 179.99; 2026-05-15 charged 41.50 / paid 41.50; 2026-09-01 charged 179.99 / paid 60.00). Verified row by row. |
| **D4** "charge of the kind the benefit names" | closed | **CLOSED** | `..._benefit_credit_application.overwrite[1]` names the base clause verbatim and replaces it with "The part of the charge the member is left to meet is the labour taken, the parts taken and the attendance charges taken…". The mapping half of the base clause is not orphaned — the extended rule restates it. |
| **D5** allowance measure | closed | **CLOSED** | `overwrite[2]` names "…measured by membership_msr_benefit_redemptions_term…" verbatim and declares the twelve-month rolling measure. |
| **D6** sentence broader than condition | closed | **CLOSED** | the sentence now says "a grant of **the very named benefit that charge's kind calls for**"; the rule defines the mapping; and task 0's seed carries no `service_credit` grant for cycle 2026 (2026 grants are `install_credit` and `delivery_credit`; the `service_credit` grants carry cycle 2025). The edge is unmet at the sentence's own strength. |
| **D7** "same named benefit" as a constant | closed | **CLOSED** | the grant rule now says "granted once for that year under **the service credit**, the named benefit that goes toward bench and on-site repair labour", and the application rule defines the charge-kind→benefit mapping. The computes' `benefit_code='service_credit'` filters now say in code what the prose says in words. |
| **D8** keyless cross-reads | fixed, with a regression test | **CLOSED — and the regression test holds when I run it myself** | see the dedicated section below. |
| **D9** seat ladder discriminator | closed by removal + substitution | **CLOSED** on D9 itself; the substitute raises **N1** | `seat_charge_component` is gone and `household_slots_used` is now read by no binding in the charter. |
| **D10** vacuous conjunct | closed | **CLOSED** | grounds in `factor_ladders` above. |
| **D11** four overlapping ladders | closed by rewording | **CLOSED** on all four; one new instance → **N2** | grounds in `factor_ladders` above. |
| **D12** mislabelled `method` | closed by relabelling | **CLOSED** | grounds in `factor_ladders` above; the counter-relabel of `cover_already_met` is honest. |
| **D13** dishonest accrual baseline | closed | **CLOSED** | grounds in `factor_ladders` above. |
| **D14** non-self-sufficient `baseline.rule` | closed by a sweep | **CLOSED** on all six; residual → **N6** | grounds in `factor_ladders` above. |
| **D15** seven unreal tiers | closed by rewording | **CLOSED** | grounds in `factor_ladders` above. |
| **D16** sweep condition already true | closed by naming the year and re-seeding | **CLOSED** | the condition is now "a points expiry entry whose sweep year is the calendar year the handling day falls in" = 2026; the ledger carries `expiry_cycle_year` 2023 and 2025 only. Verified. |
| **D17** sweep year undefined | closed | **CLOSED** | the rule now defines it outright: "The sweep year a forfeiture belongs to is the calendar year the day it is booked falls in". |
| **O1** month-day window drift | not listed | **CLOSED** | grounds in `rule_compute_equivalence` above. |
| **O2** a point's life two lengths | argued, no change | **argued soundly; unchanged** | the sweep measures 30 months, the redemption 24. Each rule names its own quantity explicitly and neither admits a second reading, so no relationship fails. Remains an observation. |
| **O3** benefit suspension in grace | argued, no change | **now defused in substance, better than argued** | `settle_membership_dues_c8b60f0e` now writes `status="active"`, and at the application's handling moment the period's dues stand met (197.98 applied against 179.99 charged). The inherited base clause "the member may not redeem points or benefit credit until the dues are settled" is satisfied on the world rather than argued around. |
| **O4** base `membership_tier_migration` ordering | argued, no change | **argued soundly; unchanged** | grounds no edge; no task writes a tier change. |
| **O5** earlier unpaid periods dropped by the window | not listed | **CLOSED in the world** | on the new ledger every period before the current one is fully paid, so the one-month window drops nothing owing. |
| **O6** seat charge unauthorised by base | not listed | **CLOSED by removal** | |
| **O7** rounding half-up vs half-to-even | closed | **CLOSED** | `..._purchase_points_accrual.overwrite[3]` names "Earned points are rounded to the nearest whole point, with a half point rounded up." verbatim and declares "with a half point rounded to the nearest even point". |
| **O8** returned-goods goodwill adjustment inherited | not listed | **CLOSED** | `overwrite[4]` names the base clause verbatim and replaces it with "Goods that have gone back are taken off the same spend", implemented by the new `returned_goods_taken_off` factor. |
| **O9** plan discount before plan bonus | not listed | **CLOSED by removal**; residual → **N5** | the plan-bonus factor is gone from the accrual, so there is no extended counterpart to conflict with. |
| **O10** an `overwrite` that supersedes nothing | closed | **NOT CLOSED — unchanged** | `..._points_redemption_release.overwrite[0]` still declares "Points are redeemed in whole blocks of the tier's minimum redemption block, and a balance below one block cannot be redeemed at all." superseded by a replacement that ends "…brought down to whole blocks of the tier's minimum redemption block; **a balance below one block cannot be redeemed at all**" — the superseded clause repeated verbatim. It was an observation in revision 1 and remains one; the claim of closure is not borne out. |
| **O11** no enum value for an order balance | closed | **CLOSED** | `redeem_reward_points_8621cafe`'s gloss now reads "instant_checkout_discount, the points come straight off a purchase at the till **or off a charge already standing on the account**, there and then", and the rule fixes the form: "A redemption put against a charge already standing on the profile is taken as an instant discount on that charge rather than as a certificate the member spends later." |
| **O12** store credit netted with no write | argued, no change | **argued soundly; unchanged** | the difficulty claims membership event types only and has no tool that can debit `credit_accounts.store_credit_balance`; a cross-category write would breach scope exclusivity. No relationship fails. Remains an observation. |
| **O13** status not moved out of grace | not listed | **CLOSED** | the tool now writes `status="active", grace_start_date=""`. |

#### D8: the sorted-key regression test, run independently

The claim is that every order read is now a ledger aggregate over a stated window and every other
cross-read names the single record the profile holds. I checked the mechanism and then ran the test.

**Mechanism.** I enumerated every cross-category primitive in the charter. There is now **no
`CFIELD('orders', …)` and no `CPARAM('orders', …)` anywhere**: `orders` is reached only through
`XSUM('orders','order_events', …)` — `merch_month`, `payments_month`, `merch_quarter`, `merch_lines`,
`promo_credits`, `match_credits` in the accrual, and the three terms of `orders_unsettled` in the
redemption. The accrual's rule was rewritten to say what the aggregate does ("the merchandise lines billed
**to the profile**", "Discounts credited on **the profile's orders**"), and the redemption's cap is now
"what stands unsettled on **the profile's orders**, taken as the charges billed less the credits applied
and the payments taken over the twelve months ending on the handling day" — no keyless holding field. The
remaining `CFIELD`/`CPARAM` calls are on `credit`, `protection`, `service` and `returns`, and every rule
sentence that uses them now says "the X **the profile holds**" (singular); both seeds hold exactly one
credit account, one plan, one service agreement and one return authorisation.

**The test.** I re-serialised each task's `initial_state` with `sort_keys=True` — the transformation that
in revision 1 moved `points_earned` from 23,984 to 15,404 and `points_redeemed` from 25,400 to 0 — and
re-ran both full chains:

| | source key order | sorted key order | identical? |
| --- | --- | --- | --- |
| task 0 settlement / grant / application | 137.98 / 242.80 / 75.15 | 137.98 / 242.80 / 75.15 | **yes** |
| task 0 terminal (`dues_outstanding`, `benefit_credit_balance`) | 42.01, 327.80 | 42.01, 327.80 | **yes** |
| task 1 accrual / sweep / redemption | 18,432 / 9,000 / 14,800 | 18,432 / 9,000 / 14,800 | **yes** |
| task 1 terminal `points_balance` | 144,632 | 144,632 | **yes** |

**The test holds.** It is also a harder test than revision 1's world afforded: task 1 now carries **three**
purchase orders (`6d92ab22` of 2023-10-15, `47bc0957` of 2026-08-10, `56ac493d` of 2026-09-08), so the
multi-row case that broke in revision 1 is genuinely exercised, and `orders_unsettled` still resolves to
2,480.00 — the laptop order's own outstanding balance — because the twelve-month window excludes the 2023
order's rows. **D8 closed.**

#### New charter-global findings

- **N1 — SOURCE-FACTOR RED. Both tasks' seeded return authorisations carry a restocking fee that the
  returns product's own charter could not have produced, and in both tasks the figure is load-bearing.**
  - *symptom*: a cross-difficulty factor's tier is decided by a seeded figure that contradicts the charter
    of the product it is read from; an agent that reads that charter reaches a different scored number.
  - *root cause*: the D9 substitution and the D2 rewrite together moved both tasks onto a
    **schedule-derived** quantity — `return_authorizations.restocking_fee_outstanding` — where revision 1
    read either nothing (task 0 had no returns factor) or a ledger figure (`return_events.refund_amount`).
    The seed was not made to satisfy `returns_restocking_fee`.
  - *evidence*, verbatim from `blueprint/products/returns.yaml` → `returns_restocking_fee.rule`:
    "The restocking fee is the schedule's percentage of the line price, then raised to the schedule's
    minimum and cut to the schedule's cap, and rounded to the cent. … **No restocking fee is charged where
    the item is graded defective on arrival or not as described, or where the retailer shipped the wrong
    item**, because the fee pays for putting saleable stock back. … **Where the schedule waives the fee for
    a Circle member the waiver is recorded with the membership as its reason**, and the member's tier
    waiver percentage is applied to whatever fee is left where the schedule does not waive it outright."
    - task 0: `return_authorizations.30b9df11-37bb-4c7c-990c-5b041ff4425e` is on
      `Member Extended Thirty Day Return`, whose `restocking_fee_waived_for_member` is **True**, held by a
      Circle member; `purchase_price` 189.00, `restocking_fee_pct` 10, `restocking_fee_min_usd` 9.95,
      `restocking_fee_cap_usd` 149.00. The charter yields **0.00** (waived outright for a member), or
      **18.90** unwaived. Circle Total Annual's `restocking_fee_waiver_pct` is 100. The seed carries
      **45.00**, and a `returns_restocking_fee_charge` event of 45.00 with no waiver row.
    - task 1: `return_authorizations.dac9f50c-7ffb-41de-a894-f50fac949e35` is on
      `Business Contract Return Schedule` with `return_reason: "wrong_item_shipped"`. The charter yields
      **0.00** ("where the retailer shipped the wrong item"); were it chargeable it would be 12% of
      1,200.00 = **144.00**, or **72.00** after Circle Business Pro's 50 % `restocking_fee_waiver_pct`. The
      seed carries **88.00**, which is none of those.
  - *demonstrated consequence*, recomputed by me on each task's own handling-time world:
    - task 0: `return_component` 45.00 → 0.00 takes `settlement_payment_usd` from **137.98 to 92.98**, and
      that in turn moves `dues_position_12m` so that `dues_standing_adjustment` falls from the 25.00 paid-in-full
      addition to no adjustment at all, taking `credit_granted_usd` from **242.80 to 217.80**. At the
      unwaived 18.90 the figures are **111.88** and **217.80**.
    - task 1: `held_for_returns` 8,000 → 0 takes `points_redeemed` from **14,800 to 22,800**; at 72.00 it is
      **16,300**; at 144.00 it is **9,700**.
  - *affected artifact*: `tasks/0.json` →
    `initial_state.return_authorizations.30b9df11-….restocking_fee_outstanding` and
    `initial_state.return_events.c790d6e7-….restocking_fee_amount`; `tasks/1.json` →
    `initial_state.return_authorizations.dac9f50c-….restocking_fee_outstanding`,
    `initial_state.return_events.56ed4bd0-….restocking_fee_amount` and
    `initial_state.return_authorizations.dac9f50c-….return_reason`;
    `membership.extended.yaml` → `extended_policies[0].factors[return_balance_brought_in]` and
    `extended_policies[5].factors[points_held_for_returns]`
  - *relation to previous revisions*: **new in revision 2**, introduced by the fixes for D9 and D2. It is
    the same class of defect as revision 1's T0-8 (a seeded row the charter says cannot exist, load-bearing
    on a scored value), now in the returns line instead of the seat count.
- **N2 — observation. The new `standing_restoration_fee` ladder overlaps as stated, in a corner neither
  task reaches.** Tier 1 fires on "the membership record carries a lapse day and that day falls within the
  reinstatement window of the tier"; tiers 2 and 3 fire on "the membership stands in grace and …". A record
  that lapsed, was reinstated inside the window (`membership_reinstate` writes `reinstatement_count` and
  fresh term dates and does **not** clear `lapsed_date`) and then fell into grace again inside the same
  window satisfies both, and the prose does not say the first wins — only `compute`'s ternary order does.
  Task 0 has `lapsed_date: ""`, and task 1 does not use this policy, so no consequence is demonstrable and
  this is an observation rather than a repeat of D11.
- **N3 — observation. `store_credit_offset`'s window is stated per account and implemented as a
  constant.** The rule says "the store credit posted to it inside **the days that account's store credit
  stays spendable**" and the policy's `cross_category` block declares `store_credit_validity_days` among
  the fields it reads, but `compute.credit_posted_in_validity` is
  `XSUM('credit','credit_events','store_credit_amount', within_months=12, …)` and no binding reads that
  parameter. `store_credit_validity_days` is 365 on five of the six credit variants — including both tasks'
  — but **730 on `Northbeam Signature Rewards Card`**, where the rule and the compute would diverge by a
  year. No consequence on either world.
- **N4 — observation. The department bonus now reads a different object than base located it on, and the
  supersession covers it only implicitly.** Base `membership_points_accrual` ties the bonus to "the part of
  the spend in that department"; the extended rule reads "the department of **the item that agreement was
  carried out on**" — the TechWorks agreement. That base clause *is* named in `overwrite[0]`, so the
  relocation is covered, but the replacement text names no object for the department and the locator
  appears only in a separate rule sentence. On task 1 it makes no difference: the service agreement's
  `item_serial` `SN-LAP-773401` and `item_category` `laptop_and_tablet` are the laptop order's own.
- **N5 — observation. Three base provisions are now inherited with no extended counterpart, and none
  fires.** `membership_ext_purchase_points_accrual` still lists
  `membership_combo_protection_interaction` in `base_policy_refs` while all five of its `overwrite` entries
  are against `membership_points_accrual` and no binding touches the combo policy. Its live clauses — "the
  plan bonus percentage of the tier is earned on every protection plan **bought in that membership year**",
  "The protection plan discount … is applied to the plan price before the plan bonus points are worked
  out", "the interaction is counted once per membership year" — are inherited in full. I verified they do
  not fire on task 1: the plan's `purchased_date` is 2025-06-01 and the membership year now running began
  2026-03-15, so no plan was bought in it. Nothing is retired by nobody with a live consequence, which is
  the correct outcome; the stale `base_policy_refs` entry is the observation.
- **N6 — observation. The settlement's `baseline.rule` leaves four of its six terms unquantified.** It
  states the twelve-month window, the dues side, the payments side, the combination order and the rounding,
  and names "the fee for putting the standing right", "the store credit set against the amount", "what is
  owed on the plan" and "what is owed on the return" without giving any of them a default — whereas the
  other five `baseline.rule`s state every fall-through outright. The number is still **definite**, because
  the document offers no figure for those terms and the only available reading contributes nothing, giving
  110.99 against a gold of 137.98; so D14's test passes. The inconsistency with the other five documents is
  the observation.

## closing_checklist (revision 2)

**Not reached.** Both tasks carry a RED on the factors relationship and on the unique-solution
relationship, from **N1**. Against Step 4's list:

- the per-task audit files correspond one-to-one with the tasks, this file sits alongside them, and
  revision 1 is preserved verbatim above with revision 2 appended ✔; **neither task's revision-2
  comparison carries a PASS** ✗
- the six extended policies are fully covered, `charter_scope` confirms the pairwise-disjoint 3 + 3
  partition over whole problem trees, task tools and GT are closed, and every uuid8 is independently
  generated, frozen and unchanged ✔
- **problem trees**: each task declares 2 prerequisite problems, 2 `value_input` edges (floor
  max(2−1,1) = 1), one `owner=user` write and no cycle; the whole-difficulty graph is a DAG; and — the
  defect that failed both trees in revision 1 — **all four declared prerequisites are now genuinely unmet
  at `frozen_time`**, verified row by row ✔
- **computations**: every computation declares 4–6 factors with ≥2 `parameter` and ≥1 `method`, ≥1
  multi-source and ≥1 cross-difficulty per task, ladders of ≥3 tiers stated in full in the rule with
  distinct outcomes and (with N2's exception) disjoint conditions; all 32 factors move their scored number
  against an honest baseline; all six whole-baseline figures are definite and differ from gold ✔ — **but
  the returns figure two of those factors read could not have been produced by the returns charter (N1)** ✗
- instantiation-stage gates on a final form: not applicable, there is no final form ✗

**Verification of the 35 figures.** Every revealed `expected` (137.98, 242.80, 75.15, 18,432, 9,000,
14,800), every `baseline_result` (110.99, 15.00, 119.00, 20,800, 30,400, 144,600) and every one of the 32
`factor_sensitivity[].baseline_result` values matches my own independent recomputation on the amended
charter and the re-seeded worlds, figure for figure. Every `prerequisite_closure` skip-run figure matches
too (187.80, 0.00, 5,600, 43,000, 119.99, 101.50 / 221.49, 239.48, 133,232, 6,000 → 15,000, 42.01), and
task 1's two write orders give identical figures and an identical terminal balance on my own run. The two
argument defects of revision 1 are closed at the value level: `qualifying_spend_usd` is now **4608.0**,
the spend the rate actually runs on, and `redemption_kind` is now **instant_checkout_discount**.

---

## revision_3

### revision_3_frozen

- same auditor as revisions 1 and 2, resumed with those derivations intact; both are left untouched above
- revision time: 2026-09-20T (round-3 pass; an earlier attempt at this revision was cut off by an account
  rate limit before anything reached disk, so nothing partial is preserved and nothing already settled was
  re-derived)
- artifact state, all four verified against the coordinator's figures:
  `membership.extended.yaml` **`3c4209b3c0d6cd68`**, `task_tools.py` **`12c5fa8b37b418f3`**,
  `tasks/0.json` **`9548833d407f64ed`**, `tasks/1.json` **`12fcab06cac71787`**
- masked views `5b2885f8fce03c8a` / `eabb3e9b2eaca5c0`, each verified byte-identical to its source
  `initial_state` under `json.dumps` including key order, and `frozen_time` matching
- **`task_tools.py` is unchanged, established by content and not by hash alone**: I re-read all six bodies.
  Each is still `ctx.find` the holding, `if not rows: return Error`, `ctx.create` the ledger row,
  `ctx.update` the holding, return the receipt — one `if`, two returns, no branch on any prerequisite, no
  balance, status or dedup check. `settle_membership_dues_c8b60f0e` still writes
  `status="active", grace_start_date=""`. The six uuid8s are unchanged and still independent.
- not a fresh blind derivation, and not presented as one. Revision 1's blind derivation remains the
  baseline; this round re-derives every figure from the amended charter and the re-seeded worlds and rules
  on each revision-2 item.
- **The charter itself moved in only two places.** Structure is identical to revision 2 — same six
  policies, same `target_tool`s, same `computes`, same factor ids, same counts, base copy still verbatim
  identical to `blueprint/products/membership.yaml` on all ten shared keys. The two changes are the N2 fix
  and the O10 fix, both recorded below. Everything else re-verified as standing: 14 `overwrite` entries with
  every `superseded_clause` a verbatim substring of its named base rule; four `policy_source` sentences
  verbatim in the blocked rule and absent from the depended-on rule; the `prerequisite` graph still a DAG
  with four `value_input` edges, gates that exist in `compute`, correct `resolved_by`, `form: state` and no
  `fallback_reason`; every ladder tier stated in the rule and implemented in `compute`; every tier outcome
  distinct; every `baseline.rule` sentence verbatim in its full rule; docstrings silent on sequence.

### the two charter changes

- **N2 — CLOSED.** `standing_restoration_fee` is now disjoint in prose, ladder **and** compute rather than
  by the ternary's order. Tiers 2 and 3 each carry the exclusion outright: "the membership stands in grace,
  **the record carries no lapse day inside the reinstatement window of the tier**, and the ledger carries an
  earlier late fee entry…" / "…**no lapse day inside that reinstatement window**, and the ledger carries no
  earlier late fee entry…", and `compute.standing_fee` mirrors it with
  `(F('lapsed_date') == '' or DAYS(F('lapsed_date'), NOW) > P('reinstatement_window_days'))` on both
  branches. Four tiers, pairwise disjoint as stated, no reliance on evaluation order.
- **O10 — CLOSED.** `membership_ext_points_redemption_release.overwrite[0].superseded_clause` is narrowed to
  "Points are redeemed in whole blocks of the tier's minimum redemption block" — still a verbatim substring
  of the base rule — so the clause the replacement **retains** verbatim ("a balance below one block cannot be
  redeemed at all") is no longer declared superseded. The overwrite now names only the clause the policy
  actually relocates. This was the one revision-2 closure claim about the charter that had not been borne
  out, and it is now genuinely fixed.

### N1 re-checked against `blueprint/products/returns.yaml` — HOLDS on both tasks

This was the sole finding standing after revision 2, and the whole point was that a seeded value must be one
the owning charter can produce. I re-derived each figure from `returns.yaml` myself rather than checking the
reworker's arithmetic.

**Task 0** — `return_authorizations.30b9df11-…`, `Member Extended Thirty Day Return`,
`purchase_price: 29.0`, `quantity_returned: 1`, `inspection_grade: open_box_incomplete`,
`missing_accessories: "cables"`, `return_reason: did_not_fit_space`:

| quantity | what the charter yields | seed |
| --- | --- | --- |
| restocking fee charged | `max(29.00 × restocking_fee_pct 10%, restocking_fee_min_usd 9.95)` = **9.95**, under `restocking_fee_cap_usd` 149.00 | `returns_restocking_fee_charge` **9.95** ✔ |
| member waiver | `restocking_fee_waived_for_member: True` → waived outright, and "the waiver is recorded with the membership as its reason" | `returns_restocking_fee_waive` **9.95**, `fee_waiver_reason: "membership_benefit"` ✔ |
| `restocking_fee_outstanding` | 9.95 − 9.95 = **0.00** | **0.00** ✔ |
| merchandise refund | `29.00 × 1 × grade_refund_ladder[open_box_incomplete] 90% − missing_accessory_deduction_usd 15.00` = 26.10 − 15.00 = **11.10** | `returns_refund_authorize` **11.10**, `refund_outstanding` **11.10** ✔ |
| the deduction itself | `missing_accessory_deduction_usd` 15.00 | the grade record carries `deduction_amount: 15.0` ✔ |

and the surrounding logistics all satisfy the schedule: `return_window_days` 30 against purchase 2026-08-27
and request 2026-09-05; `inspection_days` 3 business days against received 2026-09-09 / inspected 2026-09-10;
`return_method: in_store_dropoff` ∈ "in-store drop-off, prepaid label or carrier pickup";
`refund_method: original_card` ∈ "the original card or store credit".

**Task 1** — `return_authorizations.dac9f50c-…`, `Business Contract Return Schedule`,
`purchase_price: 1200.0`, `quantity_returned: 1`, `inspection_grade: open_box_complete`,
`missing_accessories: "none"`, `return_reason: business_over_ordered`:

| quantity | what the charter yields | seed |
| --- | --- | --- |
| is a fee chargeable? | `business_over_ordered` is **not** one of "defective on arrival or not as described, or where the retailer shipped the wrong item", so it is — and it is a legal `return_reason` enum value | ✔ |
| restocking fee charged | `max(1200.00 × restocking_fee_pct 12%, restocking_fee_min_usd 25.00)` = **144.00**, under `restocking_fee_cap_usd` 900.00 | `returns_restocking_fee_charge` **144.00** ✔ |
| member waiver | `restocking_fee_waived_for_member: False` → not waived outright, so "the member's tier waiver percentage is applied to whatever fee is left" → Circle Business Pro `restocking_fee_waiver_pct` 50 → **72.00** waived | `returns_restocking_fee_waive` **72.00**, reason `membership_benefit` ✔ |
| `restocking_fee_outstanding` | 144.00 − 72.00 = **72.00** | **72.00** ✔ |
| merchandise refund | `1200.00 × 1 × grade_refund_ladder[open_box_complete] 100% − 0` = **1200.00** | `returns_refund_authorize` **1200.00**, `refund_outstanding` **1200.00** ✔ |

`pickup_lead_days` 5 against a collection requested 2026-08-28 and dispatched 2026-09-03 — six days' notice;
`return_method: freight_collection` ∈ "freight collection or carrier pickup";
`refund_to_original_method_required: True` with `original_payment_method` and `refund_method` both
`business_invoice_credit`; `inspection_days` 7 against received 2026-09-04 / inspected 2026-09-07.

A refund of 1,200.00 and a restocking fee of 72.00 standing **together** is not a contradiction:
`returns_refund_settlement` makes the offset its own act — "The restocking fee still outstanding is kept back
from the refund **as an offset** rather than billed separately" — `settled_date` is empty and no
`returns_refund_offset` row has been booked, so this is the legitimate intermediate state.

**On the rival reading, and on the `parameter_schema` gloss.** The claim as relayed to me was that "the
member flag governs the window rather than the fee waiver", which read against
`restocking_fee_waived_for_member` — glossed "Whether a Circle member's fee is waived on this schedule" —
would have been false. Checking the artifact rather than the relay, the worklog names a **different
parameter**, and it is right: `returns.yaml`'s `parameter_schema` carries **`member_window_extension_applies`**,
glossed verbatim "**Whether the Circle tier's window extension is added to this schedule**", and
`Business Contract Return Schedule` sets it to `False`. That is exactly the rival reading a careful reader
might take — "no member effect reaches this schedule" — and the gloss does exclude it, because the flag is
about the window and nothing else, while `returns_restocking_fee` attaches the tier waiver percentage to
"whatever fee is left where the schedule does not waive it outright" with no such condition. **The gloss
bears the weight put on it.** The two parameters are distinct and both exist.

**N1 is closed on both tasks, and closed the right way**: every figure is derived from the owning charter,
and on task 0 the charge-plus-waiver pair is seeded so that the *ledger* shows how the 0.00 arose rather than
merely asserting it.

### the four cross-difficulty sweep fixes — all HOLD against their owning charters

Each is a seeded value that only the other product's charter can adjudicate, and no gate checks any of them.
I derived each from the owning charter myself.

1. **Plan instalments taking the tier's discount before billing — HOLDS, and the asymmetry between the two
   tasks is *required*.** `protection_premium_billing`: "Where the customer holds a Circle membership whose
   tier gives a plan discount and the plan applies the membership discount, the discount is taken off the
   premium **before it is billed**, not refunded afterwards." And
   `protection_combo_membership_interaction`: "**A business fleet plan takes its pricing from the contract
   price book and no membership discount applies to it at all.**"
   - task 0: ShieldCare Total Device Protection `monthly_premium_usd` 14.99 × (1 − Circle Total Annual's
     `protection_plan_discount_pct` 15%) = 12.7415 → **12.74**, which is every seeded premium charge, every
     payment and `premium_outstanding`.
   - task 1: ShieldCare Business Fleet Protection stays at **39.00** — no discount, because the charter
     forbids one on a fleet plan. What looked like an inconsistency between the tasks is the charter being
     followed in both.
   - and the grace carve-out is respected: "Where the membership stands in grace on a tier that suspends
     benefits, the discount is not applied to a premium billed in that period". Grace began 2026-09-11 and
     the last premium charge is 2026-09-01, so no discounted charge falls inside grace.
2. **A deductible standing on a plan whose waiver-on-repair forbids one — HOLDS.**
   `protection_claim_settlement`: "The plan's deductible is billed once per approved claim, and **it is
   waived where the plan waives it on a claim settled by repair**." Both plans carry
   `deductible_waiver_on_repair: True`; task 1's claim is `approved_repair` with
   `settlement_basis: repair`, so `deductible_outstanding` must be **0.00** and no
   `protection_deductible_charge` row may stand — which is the seed, the charge row having been removed.
   Task 0 is 0.00 on the same ground.
3. **A delivery fee off the freight band with the free-delivery threshold misread — HOLDS.**
   `orders_charge_composition`: "then the delivery charge **the service's band mapping gives for the order
   value**… Delivery is free where the order value reaches the service's free delivery threshold, and
   **where the service takes the member threshold** the Circle tier's threshold replaces the service's own."
   Business Dock and Freight Delivery: `delivery_fee_bands_usd`
   `{'0.00 to 34.99': 245.0, '35.00 to 299.99': 245.0, '300.00 and above': 175.0}`,
   `free_delivery_threshold_usd` 9999.0, `member_free_delivery_applies` **False**.
   - order `47bc0957` merchandise 5,600.00 → the ≥300 band → **175.00** ✔ seeded; order `56ac493d`
     merchandise 4,800.00 → **175.00** ✔ seeded; both below 9,999 so neither is free.
   - order `6d92ab22` merchandise **79,500.00** ≥ 9,999 → delivery **free**, and no `delivery_fee` row is
     seeded on it. The threshold is exercised in both directions on one profile.
   - `member_free_delivery_applies: False` means Circle Business Pro's
     `free_standard_delivery_threshold_usd: 0.0` does **not** replace the service's own — which is precisely
     the misreading named, now corrected.
4. **A return raised and collected the same day against a schedule requiring five days' notice — HOLDS.**
   `returns_authorization_and_logistics`: "a collection needs the schedule's **lead days** of notice";
   `Business Contract Return Schedule.pickup_lead_days` = **5**. The collection was requested and authorised
   2026-08-28 and dispatched 2026-09-03 — six days. Task 0's return is an `in_store_dropoff`, so the rule
   does not bear on it.

### my own broader cross-charter seed sweep — no fifth off-charter load-bearing figure

This class has bitten this line twice and no gate covers it, so I swept every remaining cross-category
seeded quantity that any factor of either task reads, against its owning product charter:

| seeded value | owning charter | verdict |
| --- | --- | --- |
| task 0 service labour 238.00 | `base_labour_rate_usd_per_hour` 119.00 × 2.0 h, `minimum_labour_hours` 1.0 met, `labour_rounding_basis` "up to the next quarter hour" | exact ✔ |
| task 0 trip charge 49.00 | `trip_charge_usd` 49.00, and `trip_charge_waived_above_usd` 299.00 > labour 238.00 so it is correctly **not** waived | exact ✔ |
| task 0 parts 84.00 / markup | `parts_markup_pct` 25 → the application nets 84.00 / 1.25 = 67.20 | consistent ✔ |
| task 0 diagnostic fee 79.00 | `diagnostic_fee_usd` 79.00 | exact ✔ |
| task 0 `visits_remaining` 0 | `included_visits_per_term` 1, grant 1 / consume 1 | exact ✔ |
| task 0 `coverage_remaining` 3,780.00 | `coverage_limit_usd` 4,000.00 − payout 220.00; `per_claim_limit_usd` 2,000 ≥ 220; `claim_limit_count_per_term` 4 ≥ 1 | exact ✔ |
| task 0 `store_credit_balance` 15.00 | its own ledger: 35.00 posted − 35.00 spent + 15.00 posted | exact ✔ |
| task 1 service labour 1,400.00 | `base_labour_rate_usd_per_hour` 175.00 × 8.0 h | exact ✔ |
| task 1 `visits_remaining` 3 | `included_visits_per_term` 4, grant 4 / consume 1 | exact ✔ |
| task 1 `service_charges_outstanding` 180.00 | 1,400.00 labour − 1,220.00 payment | exact ✔ |
| task 1 `premium_outstanding` 39.00 | 4 charges × 39.00 − 3 payments × 39.00 | exact ✔ |
| task 1 `coverage_remaining` 45,000 | `coverage_limit_usd` 45,000 with no payout booked; a claim decided and not yet paid out is a legitimate intermediate state | exact ✔ |
| task 1 order totals 79,500 / 5,775 / 4,975 and `balance_outstanding` 2,175 | merchandise + the 175.00 band where chargeable; 4,975 − 480 discount − 2,320 payment = 2,175 | exact ✔ |

One residue, recorded as an observation and **not** load-bearing: task 0's
`purchase_orders.5e965264-….order_total` of **4,620.00** is not reconstructible from
`White Glove Delivery and Installation` (merchandise 4,200.00 + the ≥300 band 149.00 + `recycling_fee_usd`
18.00 = 4,367.00, with installation and haul-away included at zero). Task 0's three policies declare no
`orders` cross-read, seed no `order_events`, and no factor reads the field; it is visible only because
`find_purchase_orders` sits in the gold read set (**T0-10**). Recorded as **N7**.

### tier reachability

Two tiers do not fire on these worlds — `plan_money_brought_in` tier 2 (an unsettled deductible with no
premium shortfall) and `points_held_for_cover` tier 1 (an unsettled deductible) — because every claim in
both worlds is settled by repair and both plans waive the deductible on repair. Each fires on a world the
charter plainly allows: `protection_events.settlement_basis` admits `replacement`, `reimbursement` and
`buyout`, and `claim_decision` admits `approved_replacement` and `approved_reimbursement`, on none of which
`deductible_waiver_on_repair` bites. Neither is a condition the policy raises on before returning, so
neither is a dead branch. The argument is sound. ✔

### findings (revision 3)

#### Disposition of every revision-2 item

| item | reworker's claim | my verdict | grounds |
| --- | --- | --- | --- |
| **N1** off-charter restocking fees, both tasks | closed on both, figures re-derived from `returns.yaml` | **CLOSED on both tasks** | every figure derived independently above; on task 0 the ledger now shows the charge and the matching waiver rather than asserting the zero; on task 1 the reason moved off the no-fee ground and the schedule percentage with the tier waiver gives exactly 72.00 |
| **N2** `standing_restoration_fee` overlapping as stated | fixed in prose, ladder and compute | **CLOSED** | the exclusion is written into both tiers and mirrored in `compute`; no reliance on the ternary's order |
| **N3** store-credit window stated per account, implemented as 12 months | argued | **argued soundly; unchanged** | both tasks' accounts carry `store_credit_validity_days` 365, so `within_months=12` coincides exactly; the divergence survives only on `Northbeam Signature Rewards Card` at 730, which neither world holds. No relationship fails. |
| **N4** department read off the serviced item | argued | **argued soundly; unchanged** | task 1's service agreement `item_category: laptop_and_tablet` and `item_serial: SN-LAP-773401` are the laptop order's own, so the two objects still agree and no second value arises |
| **N5** combo policy in `base_policy_refs` with no overwrite | argued | **argued soundly; unchanged** | the plan's `purchased_date` is 2025-06-01 and the membership year began 2026-03-15, so the live clause ("every protection plan **bought in that membership year**") does not fire. Nothing is retired by nobody with a live consequence. |
| **N6** settlement `baseline.rule` leaves four terms unquantified | argued | **argued soundly; unchanged** | the fall-back is still definite — window 12 gives `212.49 − 101.50 = 110.99`, which is the declared `baseline_result` and differs from the gold 124.63. The inconsistency with the other five documents remains an observation. |
| **O10** an `overwrite` that supersedes nothing | fixed | **CLOSED** | the `superseded_clause` is narrowed to the clause actually relocated, and it is still verbatim in the base rule |
| **T1-8** earning entries versus the order they name | half closed, and said so | **FULLY CLOSED — better than claimed** | order `6d92ab22`'s `order_total` and its single `merchandise_line` both moved 12,000.00 → **79,500.00** (`quantity` 530 × `unit_price` 150.00), and the eight accrual rows naming it carry 12,000 + 9,500 + 6,200 + 15,000 + 7,400 + 8,400 + 11,200 + 9,800 = **79,500.00** exactly. The residual amount mismatch I recorded in revision 2 is gone. |
| **T0-7** store credit netted with no write consuming it | claim withdrawn, left open | **correctly withdrawn; still an observation, and NOT load-bearing** | `store_credit_offset` 15.00 still reduces the scored settlement while `credit_accounts.store_credit_balance` stays 15.00 afterwards, because no tool of this difficulty may write another category. It produces no second value for any scored parameter. Honest to leave it recorded. |
| **T1-15** the sweep subtracted from a balance that never held it | claim withdrawn, left open | **correctly withdrawn; still an observation, and NOT load-bearing** | `rolling_net` is still `earned_in_life(24m) − spent_in_life(24m) − swept_in_life(24m)`; the 9,000 swept comes out of the 24,000 earned 2023-11-10 (34 months, outside the window) while the new sweep row is inside it. The rule says this consistently and admits no second reading. |

#### New finding

- **N7 — observation.** Task 0's `purchase_orders.5e965264-….order_total` of 4,620.00 is not reconstructible
  from the `White Glove Delivery and Installation` parameters (4,200.00 + 149.00 + 18.00 = 4,367.00). Not
  load-bearing: task 0 declares no `orders` cross-read, seeds no `order_events`, and no factor reads it. It
  is reachable only through the superfluous `find_purchase_orders` read recorded at **T0-10**.

**No new RED, and nothing regressed.** The re-seed was substantial — the line price, the store credit, the
premium instalments, a deductible, two delivery fees, an order total and several ledger identities all moved —
and I checked the three things a re-seed most often breaks:

- **every declared prerequisite is still unmet at `frozen_time`** (all four, verified row by row: the current
  period's 179.99 against 60.00 applied; no `(service_credit, 2026)` grant; the laptop order named by no
  earning entry; no 2026 expiry entry), and the oldest unpaid billing period is still 2026-09-01, which is
  what the gold write names;
- **every edge still bears weight** (task 0: grant 242.80 against 187.80, application 75.15 against 0.00;
  task 1: redemption 23,900 against 14,900 with the accrual skipped and against 52,100 with the sweep
  skipped), and the settlement no longer floors at zero;
- **all 32 factors still move their scored number**, all six whole-baseline figures are definite and differ
  from gold, the counts stay within bounds, every computation retains a genuine near-miss, task 1's two
  leaves still commute to identical figures and an identical terminal balance, and the **D8 sorted-key
  regression test, re-run by me on the new worlds, still gives identical figures on both tasks**.

## closing_checklist (revision 3)

**The difficulty closes out.** Both tasks PASS on all four relationships. Against Step 4's list:

- the per-task audit files correspond one-to-one with the tasks, this file sits alongside them, revisions 1
  and 2 are preserved verbatim with revision 3 appended, and **both tasks' revision-3 comparison sections
  carry a PASS** ✔
- this difficulty's six extended policies are fully covered; `charter_scope` confirms the pairwise-disjoint
  3 + 3 partition over whole problem trees; task tools and GT are closed; each task tool carries an
  independently generated, frozen uuid8, unchanged across all three revisions ✔
- every task's problem tree has two prerequisite problems, two `value_input` edges against a floor of
  max(2−1, 1) = 1, at least one problem resolved by an `owner=user` tool (the settlement on task 0, the
  redemption on task 1), and no cycle; the `prerequisite` edges of the whole difficulty remain a DAG with no
  cross-task reference; and all four prerequisites are genuinely unmet at their task's `frozen_time` ✔
- every computation declares a self-sufficient baseline and four to six factors (at least 2 `parameter` and
  1 `method` each; at least one multi-source and one cross-difficulty factor per task), every ladder of at
  least three tiers stated in full in its rule, its tiers distinct in outcome and pairwise disjoint as
  stated, its conditions and outcomes ones that line of business actually holds, and every factor proved to
  bear weight on its task's world against an honest baseline, with the baseline alone giving a definite
  number different from gold ✔
- the instantiation-stage gates were re-run on this final form by the coordinator (`replay --check`, nothing
  written back) and are green, with `check_traceability` deferred to step 3 by design ✔

**Verification of the 35 figures.** Every revealed `expected` (124.63, 242.80, 75.15, 18,080, 9,000,
23,900), every `baseline_result` (110.99, 15.00, 119.00, 20,800, 30,400, 144,200) and all 32
`factor_sensitivity[].baseline_result` values match my own independent recomputation on the amended charter
and the re-seeded worlds, figure for figure. Every `prerequisite_closure` figure matches (119.99 unmet;
101.50 against 221.49; 184.63 applied against 179.99; 226.13 against 221.49; the adjustment moving from an
offset of 30.00 to an addition of 25.00; 187.80 → 242.80; running dues 179.99 → 55.36; credit standing
0.00 → 217.80; 114,800 → 132,880; releases of 14,900 and 52,100), and so does every intermediate in both
worklogs' STANDARD SOLUTION, including task 1's `4,320 − 1,200 = 3,120`, `+ 1,400 = 4,520`, `× 4.0 = 18,080`,
`132,880 − 17,000 − 15,000 = 100,880`, `50,440 − 6,545 − 3,545 − 16,364 = 23,986 → 23,900` and
`2,175.00 → 197,727`. The two scored arguments that were wrong in revision 1 remain right:
`qualifying_spend_usd` **4520.0**, the spend the rate runs on, and `redemption_kind`
**instant_checkout_discount**.

---

## revision_4

### revision_4_frozen

- same auditor as revisions 1–3, resumed with those derivations intact; all three preserved untouched above
- revision time: 2026-09-20; **narrow round**: verify that the KB-driven source fix disturbs nothing
- artifact state, all four verified against the coordinator's figures:
  `membership.extended.yaml` **`9b4f8bedf34872ef`**, `task_tools.py` **`12c5fa8b37b418f3`** (unchanged),
  `tasks/0.json` **`9ec6780883bf9f85`**, `tasks/1.json` **`f5cd18a567a27682`**
- **the seeded worlds have not moved.** Both masked views are `5b2885f8fce03c8a` / `eabb3e9b2eaca5c0`, the
  same objects I held at revision 3, and each is byte-identical to its source `initial_state` including key
  order with `frozen_time` matching. Only the charter and the proof fields moved, so revision 3's world-level
  conclusions — the four cross-charter sweep fixes, N1's figures, the seed-fidelity table, N7 — stand
  unchanged and are not re-derived.
- the render-layer reports at `env/env_0005_consumer_electronics_retailer/audits/policy_kb/membership_benefits_desk/`
  were read for this round; the blind phase is long past.

### the `baseline.params` fix — CLEAN, verified by my own mechanical derivation

The defect the render auditor found is in the charter I passed at revision 3, and it is a real miss of mine:
`baseline.params` enumerated the **factors'** constants rather than the **baseline's** own defaults, and
`check_docs.py` then forced them into the computation document, disclosing tier figures to a reader who
should have seen only the standard method.

I did not check the agent's arithmetic; I re-ran its method independently. For each policy: substitute every
factor's own `baseline` into the `compute`, take the transitive closure of the bindings still live from
`result`, and collect the `K` / `P` / `CPARAM` keys those surviving expressions read. That set is the correct
declaration.

| policy | declared now | my derivation | match |
| --- | --- | --- | --- |
| `..._grace_dues_settlement` | `[]` | `[]` | ✔ |
| `..._year_benefit_credit_grant` | `anniversary_benefit_credit_usd` | same | ✔ |
| `..._benefit_credit_application` | `[]` (plus two **other-product** reads, below) | same | ✔ |
| `..._purchase_points_accrual` | `points_per_dollar_base`, `points_cap_per_calendar_year` | same | ✔ |
| `..._points_expiry_sweep` | `points_expiry_months` | same | ✔ |
| `..._points_redemption_release` | `points_min_redemption_block`, `points_value_usd_per_100_points` | same | ✔ |

**6 declared, 6 derived, all six policies matching, nothing declared that the baseline does not read and
nothing read that is not declared.** The count reconciles: revision 3 declared 5 + 12 + 7 + 10 + 5 + 8 =
**47** keys, so **41 were removed** — the render auditor's **27** policy-level constants (its count matches
mine) plus **14 tier keys the document tables never exposed**, which a later render carrying them would have
disclosed. The agent's sweep did go beyond what the audit found, and the 14 were real.

A good illustration of what the old declaration got wrong: the sweep's `baseline.rule` mentions "the tier's
value per hundred points", but its very next sentence is the default "Nothing is set against the pool on that
account", so under the baseline that term is zero and the rate is never read — which is exactly why
`points_value_usd_per_100_points` is correctly absent from the sweep's declaration while remaining in the
redemption's, where the baseline genuinely reads it.

### self-sufficiency of all six baselines after removing 41 keys — CLEAN

This was flagged as the sharpest risk. Each `baseline.rule` was re-read sentence by sentence, every sentence
re-verified verbatim present in its full `rule`, and each recomputed:

| policy | the reader's definite fall-back | gold | differs |
| --- | --- | --- | --- |
| settlement | **110.99** (window 12: 212.49 dues less 101.50 payments) | 124.63 | ✔ |
| grant | **15.00** (40.00 anniversary reward less the 25.00 already granted in twelve months) | 242.80 | ✔ |
| application | **119.00** (`MN(217.80, 119.00)`) | 75.15 | ✔ |
| accrual | **20,800** (10,400 of lines over twelve months at the 2.0 base rate) | 18,080 | ✔ |
| sweep | **30,400** | 9,000 | ✔ |
| redemption | **144,200** | 23,900 | ✔ |

All six are definite and all six differ from gold, and each equals the declared `baseline_result` that I had
already audited. Two points worth stating rather than passing over:

- **The application's baseline legitimately reads another product's figures, and this is handled correctly.**
  Under the all-baseline substitution `labour_taken` becomes `least_labour_billed`, which reads
  `CPARAM('service','minimum_labour_hours')` and `CPARAM('service','base_labour_rate_usd_per_hour')`.
  `baseline.params` **cannot** carry those — the gate admits only this policy's `params` and this product's
  `parameter_schema` — so the baseline paragraph names them in words: "**The labour taken is the least labour
  billed on that service at its labour rate.**" With the service agreement the agent already reads and that
  service's published figures, a reader reaches a definite 1.0 × 119.00 = **119.00**. This is
  self-sufficient in the sense the standard requires — "a definite number from it **and the records**" — and
  it is the only handling available: omitting the quantity would be worse, and carrying it in
  `baseline.params` is not permitted. It is nonetheless the one baseline whose definite number depends on
  another product's published figures, and I record that as the fact it is rather than as a defect.
- **Two baseline paragraphs still name parts they do not quantify** — the settlement's four ("the fee for
  putting the standing right", "the store credit set against the amount", "what is owed on the plan", "what is
  owed on the return") and the grant's three (the spend multiple, the addition for work in hand, the addition
  for tenure). This is the pre-existing **N6** shape, unchanged: the document offers no figure for them, so the
  only available reading is that they contribute nothing, and the number stays definite. The fix makes this
  strictly better than before, because the computation document no longer prints five (settlement) and twelve
  (grant) constants that play no part in the standard method. N6 remains an observation, now a narrower one.

### the four new floor sentences — CLEAN on every test asked

| new sentence | in `rule` | in `baseline.rule` | overlaps a prerequisite sentence |
| --- | --- | --- | --- |
| accrual — "The spend the rate is applied to never falls below nothing: where the goods that have gone back come to more than the lines counted and the work brought into the spend together, the spend is nothing and no points are earned on it." | ✔ | ✔ | none |
| redemption — "A live balance worked out on this schedule never falls below nothing." | ✔ | ✔ | none |
| redemption — "The figure left when the amounts held back are taken off the share released never falls below nothing: where those amounts come to more than that share, no points stand to be released." | ✔ | ✔ | none |
| redemption — "Where the credits applied and the payments taken come to as much as the charges billed or more, nothing stands unsettled on those orders." | ✔ | ✔ | none |

- **No variation hinted.** None carries tier language, a per-tier figure, a "where the tier…" or any
  alternative basis. Each is an unconditional floor with an explanatory clause.
- **No second reading created.** Each corresponds to an actual `MX(0.0, …)` in the `compute`: the accrual's
  inner spend floor; the three live-balance readings `full_net` / `rolling_net` / `long_net`, which the single
  "on this schedule" sentence covers together; `releasable`; and `orders_unsettled`. The coordinator's note
  that I had listed four floors on the redemption policy and missed `full_net` — the baseline's own reading —
  is accepted; the new sentence covers it.
- **Containment against the four prerequisite sentences: none**, checked mechanically both ways. The nearest
  miss is worth naming: the hold-back floor ends "**no points stand to be released**" while the sweep
  prerequisite reads "**No points are released** until the balance carries the sweep entry owed for the
  calendar year the handling day falls in." They cannot be confused — only the prerequisite carries an
  ordering connective ("until") and names a record-visible state; the floor names an arithmetic condition and
  no ordering at all — so the dependency acquires no second wording.
- One micro-observation, not a defect: the accrual floor's illustrative clause says "more than **the lines
  counted** and the work brought into the spend together" while the `compute` floors the **post-discount**
  spend. Where a discount stands, a reader following only the illustrative clause could think the floor does
  not apply — but the sentence's main clause ("never falls below nothing") is unconditional and decisive, so
  the reader lands on nothing either way. Recorded as **N8**.

### the four floors deliberately left — I AGREE with all four

Manufacturing prose for a case the schedule cannot reach would be its own defect, so each was tested for
genuine unreachability rather than for unlikelihood:

1. **`premium_shortfall`** (settlement) — `MX(0.0, premium charged − premium paid)`. The binding is consumed
   only by `plan_component`, whose tier 1 test is `premium_shortfall > 0` and whose tier 2 test is
   `premium_shortfall <= 0`. A clamped zero therefore routes to tier 2 or 3 and never reaches the sum, and
   the guard is already in the prose: tier 1 reads "the premium charged on it … **is above** the premium paid
   on it in that window". **Genuinely guarded.** ✔
2. **`aged_pool`** (sweep) — `MX(0.0, earned_all − earned_in_life)`. `earned_in_life` sums the same rows as
   `earned_all` over an inner window, so it is a subset total, and every `membership_points_accrue`
   `points_delta` is positive: `book_purchase_points_235cc6ac` documents and stores a positive whole number,
   and on the two worlds the minima are **3,875** (task 0) and **11,200** (task 1), all nine and all three
   rows positive. A superset total can never fall below a subset total of non-negative terms. **Genuinely
   unreachable.** ✔
3. **the accrual result's cap headroom** — `MX(0, P('points_cap_per_calendar_year') − earned_points_12m)`.
   Already stated in prose, and stated exactly: "Once the points earned in the twelve months ending on the
   handling day **reach** the yearly points cap of the tier, **no further points are earned**, and what is
   booked never takes the membership past that cap." **Already prose-covered.** ✔
4. **the accrual result's outer floor** — `int(MX(0, MN(raw_points, headroom)))`. `raw_points` is
   non-negative because the new inner spend floor makes the spend non-negative and I verified that no tier of
   the six carries a negative `points_per_dollar_base`, department bonus or cap; the headroom is non-negative
   by (3). The minimum of two non-negatives is non-negative. **Genuinely unreachable.** ✔

### P2/P8 — a compute change, and it moved nothing

This is the one item that changed the `compute`, not merely the prose, so it was tested as a compute change.
Four tiers across `parts_brought_in` and `attendance_charges_brought_in` said "the job stands before
completion" in prose while testing `job_status != 'completed'`, which admitted `cancelled` and `no_show`.
Both sides now name the three live standings:

- `compute.parts_taken` and `compute.attendance_taken` both test
  `(job_status == 'scheduled' or job_status == 'dispatched' or job_status == 'parts_hold')` on both tiers;
- all four ladder `when` texts and the corresponding `rule` sentences read "the job stands scheduled,
  dispatched or held for parts".

**Reachable on a scorable world** ✔ — task 0's agreement stands `dispatched`, one of the three.
**Ladders still partition** ✔ — `parts_brought_in` t1 (parts ≥ the least labour billed) against t2
(0 < parts < that figure), `attendance` t1 (a trip charge stands) against t2 (no trip charge, an after-hours
surcharge stands), each now with the identical status conjunct.
**Both factors still bear weight** ✔ — `parts_taken` **67.20** and `attendance_taken` **49.00** on task 0,
unchanged, against baselines of 37.52 and 47.71.

### P4 — CLEAN

The settlement's return assembly sentence now names the slot rather than one direction: "The return
authorisation the profile holds is brought into the same settlement, **on the side the money runs**", with
the ladder stating both directions (an outstanding restocking fee brought in; an outstanding refund set
against the amount) and its fall-through ("Where neither of those holds, nothing is brought in for the
return"), and `baseline` keyed to that fall-through. The combination sentence already carried both
directions. ✔

### nothing moved

Re-derived from the amended charter on the unmoved worlds, and compared against the figures I audited at
revision 3:

| | revision 3 | revision 4 | same |
| --- | --- | --- | --- |
| task 0 scored | 124.63 / 242.80 / 75.15 | 124.63 / 242.80 / 75.15 | ✔ |
| task 1 scored | 18,080 / 9,000 / 23,900 | 18,080 / 9,000 / 23,900 | ✔ |
| task 0 whole baselines | 110.99 / 15.00 / 119.00 | identical | ✔ |
| task 1 whole baselines | 20,800 / 30,400 / 144,200 | identical | ✔ |
| all 32 `factor_sensitivity` figures | — | recomputed against GT, **32 checked, 0 mismatching** | ✔ |
| task 0 skip-runs | 187.80 / 0.00 | 187.80 / 0.00 | ✔ |
| task 1 skip-runs | 14,900 / 52,100 | 14,900 / 52,100 | ✔ |
| task 1 commutativity | identical both orders | identical both orders | ✔ |
| D8 sorted-key regression | identical | identical on both tasks | ✔ |
| all 15 gold write arguments | — | identical, including `qualifying_spend_usd` 4520.0 and `redemption_kind` instant_checkout_discount | ✔ |

The corrected factor trace is right: `dues_standing_adjustment_rule` now reads "the ledger shows **226.13**
of dues payments in the twelve-month window against 221.49 of dues charged", and 101.50 + 124.63 = 226.13. ✔

### findings (revision 4)

| item | claim | my verdict |
| --- | --- | --- |
| `baseline.params` on all six policies | 47 → 6 | **CLEAN** — my independent derivation gives the same 6 and matches every declaration; the 27 + 14 split reconciles |
| self-sufficiency of all six baselines | preserved | **CLEAN** — each still yields a definite number, each differs from gold, each equals its audited `baseline_result` |
| the application's cross-product baseline reading | named in words | **CLEAN** — the only permitted handling, and it yields a definite 119.00 from the records |
| four new floor sentences | in rule and baseline.rule, no variation, no second reading, no prerequisite overlap | **CLEAN on all four tests** |
| four floors left unstated | unreachable or already covered | **AGREE on all four**, each tested for genuine unreachability |
| P2/P8 | compute and prose aligned on three live standings | **CLEAN** — reachable, partitioning, still weight-bearing, nothing moved |
| P4 | assembly names the slot | **CLEAN** |
| P1, P3, P7, P9, P10 argued; the second cross-problem-order sentence left as inherited base law | argued | **sound** — the base sentence grounds no declared edge and both hops carry prerequisite sentences of their own (revision 1 → O3, O4) |
| factor trace stale figure | corrected to 226.13 | **CLEAN** |
| **N8** *(new, observation)* | — | the accrual floor's illustrative clause names "the lines counted" where the compute floors the post-discount spend; the unconditional main clause governs, so the reader lands on nothing either way |
| N6 | unchanged | narrower than before: the two baseline paragraphs that name unquantified parts no longer also print factor constants |
| N3, N4, N5, N7, T0-7, T0-10, T1-5, T1-7, T1-15 | unchanged observations | **unchanged**; the worlds did not move, so revision 3's grounds stand |

**No new RED. Nothing regressed.** The fix is confined to the declaration of baseline defaults, four floor
sentences, one compute predicate widened-to-correct on four tiers, one assembly sentence and one stale trace
figure; no scored value, no baseline fall-back, no factor sensitivity, no skip-run and no gold argument moved.

## closing_checklist (revision 4)

**The difficulty remains closed.** Both tasks PASS on all four relationships, and the defect the render layer
found has been fixed at its root in the charter rather than papered over in the documents. Against Step 4's
list, everything recorded at revision 3 stands, with these items re-confirmed on the amended charter:

- the per-task files correspond one-to-one with the tasks, this file sits alongside them, revisions 1–3 are
  preserved verbatim with revision 4 appended, and both tasks' revision-4 comparisons carry a PASS ✔
- scopes still pairwise disjoint 3 + 3; tools and GT still closed; the six uuid8s unchanged across four
  revisions ✔
- both problem trees unchanged: two prerequisite problems each, two `value_input` edges against a floor of 1,
  one `owner=user` write each, no cycle, all four prerequisites still unmet at `frozen_time`, all four edges
  still bearing weight ✔
- every computation still declares a self-sufficient baseline — now with an **honest** declaration of its own
  defaults — and four to six weight-bearing factors with distinct, disjoint, business-real ladders, the
  baseline alone giving a definite number different from gold ✔
- the instantiation-stage gates were re-run by the coordinator on this final form and are green, and
  **`check_traceability` now runs and passes** (0.json 26 copied / 0 missing, 1.json 27 / 0), closing the one
  gate that had been deferred since revision 1 ✔
