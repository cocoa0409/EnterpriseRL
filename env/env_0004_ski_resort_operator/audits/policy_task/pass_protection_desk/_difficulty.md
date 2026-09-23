# Policy-task audit — pass_protection_desk / charter-global

## charter_global_frozen

- auditor: independent policy-task auditor (not the instantiating agent)
- freeze time (charter-global section): 2026-09-17, written before any task's masked GT fields were read
- frozen inputs and their hashes (sha256, full):
  - `env/env_0004_ski_resort_operator/tasks/pass_protection_desk/insure.extended.yaml`
    `25e173ac54fb5be11864e84951af639a628ac8d62ab65bba10fa94de47991e2a`
  - `env/env_0004_ski_resort_operator/tasks/pass_protection_desk/task_tools.py`
    `5c1c7fa98aafd4699d88971c1d991c16032335329ad467dbc3f20fcf57c2c59c`
  - masked task views (whitelist `frozen_time` / `user_scenario` / `initial_state` only):
    `tasks/0.json` `f735e128fa6195bb…`, `tasks/1.json` `e157ea3f171501cb…`
- fields permitted for this section: the whole extended charter (base copy + `extended_policies`),
  the whole of `task_tools.py`, `blueprint/blueprint.yaml`, `blueprint/db_schema.json`,
  `blueprint/share_tools.py`, `blueprint/products/*.yaml`, and `erlbench/`.
- fields explicitly masked and NOT read while this section was written: every task's
  `evaluation_criteria`, `computations`, `charter_scope`, `required_documents`,
  `design_rationale`, `solvability_contract`, `prerequisite_closure`,
  `db_closure`, `db_closure_matches_initial_state`.
- entry conditions (Step 0): the instantiation-stage gate snapshot was supplied with the brief and
  is green on EXTENDED, TASK-TOOL-CONTRACT, REPLAY, SOLVABILITY, COMPUTE, GROUNDING and SCOPE;
  TRACEABILITY is declared not-runnable at this stage because it depends on the not-yet-rendered KB.
  The masked views were constructed by the coordinator by whitelist and their hashes were re-checked
  against the files on disk and match. Entry conditions are complete; the gates were not re-run here.

### policy_conflict_scan

Complete structured policy in force for this category = the verbatim base section of
`blueprint/products/insure.yaml` + the five `extended_policies`. The base copy in
`insure.extended.yaml` lines 1–1170 is byte-for-byte identical to
`blueprint/products/insure.yaml` (verified by `diff`; the only difference is one trailing newline at
line 1171). The base copy has not been rewritten.

Overlapping-subject scan across base and extended:

| subject | base policy | extended policy | conclusion |
| --- | --- | --- | --- |
| `insure_amend` | `insure_eligibility_and_quote` | `insure_ext_amendment_reprice` | one extended owner; conflict declared (see `override_declarations` A1) |
| `insure_premium_charge` | `insure_premium_terms` | `insure_ext_premium_presentation` | one extended owner; conflict declared (C1) |
| `insure_claim_payment` | `insure_claim_assessment` | `insure_ext_claim_settlement` | one extended owner; conflict declared (B1); one undeclared refinement (OBS-4) |
| `insure_fee_charge` | `insure_lapse_and_reinstatement`, `insure_cancellation` | `insure_ext_giveup_charge` | one extended owner; **one undeclared conflict, F-RED-1** |
| `insure_cancel` | `insure_cancellation` | `insure_ext_giveup_settlement` | one extended owner; **one undeclared conflict, F-RED-2** |
| `insure_quote`, `insure_coverage_load`, `insure_activate`, `insure_claim_open`, `insure_document_receive`, `insure_lapse`, `insure_reinstate`, `insure_expire`, `insure_resume`, `insure_close` | base only | — | no extended policy claims them; base stands unmodified |

Triggers: `state_due` on `insure_ext_amendment_reprice` and `insure_ext_premium_presentation`,
`on_request` on the other three. No two extended policies share a `(target_tool, computes)` pair.

Time anchors across the charter are mutually consistent: every calendar-day count uses the base
counting rule (anchor day = day zero, inclusive boundary); `frozen_time` is the only clock;
`season_start_date`/`season_end_date` are tier parameters and identical (2026-11-20 / 2027-04-18)
across all six plan tiers.

Cross-category read boundary: every extended policy declares `cross_category: [{category: passes}]`
and reads nothing else. `blueprint.yaml` gives this difficulty `categories: [insure]`, and reading
the customer's own `passes` records is the declared cross-category read; no lodging, lessons,
rentals, tickets or dining table is read anywhere in the charter. Consistent.

Terminal states: `confirm_plan_giveup_9d16ef5f` is the only tool that moves `insure_holdings.status`
(to `cancelled`); the other four leave status untouched. No two policies claim the same terminal
state transition.

Claimed task scopes (derived from the computations each task's world can support, the `charter_scope`
field being masked at freeze time; confirmed at reveal in each task file):
- task 0 → {`insure_ext_claim_settlement` (root), `insure_ext_amendment_reprice`}
- task 1 → {`insure_ext_giveup_settlement` (root), `insure_ext_premium_presentation`,
  `insure_ext_giveup_charge`}
Pairwise disjoint; union = all five extended policies; jointly complete. PASS.

### rule_compute_equivalence

Check 2 was run sentence by sentence over all five extended policies in both directions. Every
quantity, window, filter, tier, branch, cross-category read, acting base, grouping, cap/floor and
rounding point carries a `compute_basis` quotation that is verbatim locatable in that policy's own
`rule`, and every `compute_basis` key is a binding that exists in `compute`. Every tier named in a
`factors[].ladder` is a sentence of the `rule` and a branch of the `decides` binding, and every
branch of each `decides` binding is a tier the rule states — no tier lives only in `compute`, and no
tier is promised in prose without an implementation. Rounding: every policy rounds at the point its
rule names (`RND(..., 2)`), and `insure_ext_amendment_reprice` and
`insure_ext_giveup_settlement` both state and implement "rounded to the cent at the end and at no
earlier step" / "worked out first and in full".

Four sweep-back divergences are recorded; none of them changes a scored value on either task's world
(the per-task demonstrations are in `0.md` / `1.md`), so all four are observations, not red lights:

- **OBS-1 — a binding that does not implement the sentence it cites.**
  `insure_ext_giveup_settlement.compute` binds
  `claim_papers_filed: "COUNT('insure_ledger', event_type='insure_document_receive')"`, and its
  `compute_basis` cites *"It is instead the day the household gives the plan up where no claim has
  been made on the plan in the season and the plan's record carries no day on which cover was
  closed"*. Counting papers received is not the same predicate as "no claim has been made": a plan
  standing in `claim_open` with `claim_opened_date` set and no paper yet lodged satisfies the compute
  branch and fails the rule's. Location: `insure.extended.yaml` `insure_ext_giveup_settlement`,
  binding `claim_papers_filed` and factor `giveup_anchor` tier 1.
- **OBS-2 — the headline sentence and `result` disagree about what is subtracted from what.**
  Rule sentence 1: *"What the plan's premium account is left standing at when a household gives the
  plan up is what stands unpaid on that account after the unearned premium has been set against
  it"*; `compute.result` = `MX(0.0, RND(set_against - unearned_premium, 2))`. On the fall-through
  tier of `offset_reach` (`set_against = 0.0`) the sentence reads as
  `account_unpaid − unearned_premium` and the compute gives `0 − unearned_premium → 0`. The
  `offset_reach` tier-2 clause *"the premium standing unpaid being left on the schedule it rides
  on"* is what makes the compute reading defensible, but the headline sentence is never narrowed to
  match it. Note also that `compute_basis.account_unpaid` cites that same headline sentence for a
  binding that is only "what stands unpaid" and carries none of the "after the unearned premium has
  been set against it" clause.
- **OBS-3 — a rule sentence with no compute counterpart (empty promise).**
  `insure_ext_amendment_reprice.rule` closes with *"A household that holds no pass of its own for
  the season has nothing this rule can be worked out on, and no plan of theirs is repriced."* No
  binding implements it and no `compute_basis` key cites it; it is a scope statement carried in the
  rule text only.
- **OBS-4 — the base `formula` block behind a superseded sentence is itself not named.**
  Base `insure_claim_assessment.formula` binds
  `benefit_pct: "medical_benefit_pct if claim_reason in [...] else (job_loss_benefit_pct if
  claim_reason == 'job_loss' else ...)"` — the share is picked from `claim_reason` alone.
  `insure_ext_claim_settlement` picks it from `claim_reason` **and** an accepted paper
  (*"where a letter from the former employer stands accepted on the claim and the claim is made on
  loss of employment"*). The `overwrite` names the base prose sentence *"The amount allowed is the
  plan's benefit share for the event claimed on…"*, which fairly covers the prose, but not the
  `formula` block that is the sharper statement of the same quantity. On a job-loss claim with no
  accepted employer letter the two give different shares.

### action_binding_and_uuids

Check 3, once over the charter and the one tool module.

| policy | `computes` | `target_tool` | owner | claimed by |
| --- | --- | --- | --- | --- |
| `insure_ext_amendment_reprice` | `repriced_premium_usd` | `confirm_plan_value_amendment_50d33fe4` | user | 1 policy |
| `insure_ext_claim_settlement` | `payout_amount_usd` | `settle_protection_claim_ed51c2df` | agent | 1 policy |
| `insure_ext_premium_presentation` | `premium_amount_usd` | `present_plan_premium_8deb00b0` | agent | 1 policy |
| `insure_ext_giveup_charge` | `fee_amount_usd` | `raise_plan_giveup_charge_59dbe3e5` | agent | 1 policy |
| `insure_ext_giveup_settlement` | `closing_premium_balance_usd` | `confirm_plan_giveup_9d16ef5f` | user | 1 policy |

Each `(target_tool, computes)` pair is claimed by exactly one policy. Each policy's subject, base
refs, target tool, docstring and terminal state admit one business reading. No tool docstring adds a
confirmation, review or wait outside its policy.

uuid8s: `50d33fe4`, `ed51c2df`, `8deb00b0`, `59dbe3e5`, `9d16ef5f`. All five are distinct, share no
prefix or tail, form no sequence, and none looks derived from a common stem or an adjacent value.
Each appears exactly once in the module and once as a `target_tool`. PASS.

- **OBS-5 — a docstring carrying an ordering word.**
  `confirm_plan_value_amendment_50d33fe4` closes: *"…and the desk works every later figure out from
  them."* "later" is an ordering word and it tells the reader that this write precedes the figures
  that follow it, which is the prerequisite edge `insure_ext_claim_settlement → insure_ext_amendment_reprice`
  restated on the tool surface. It names no other tool and no policy id. Lesser instances:
  `raise_plan_giveup_charge_59dbe3e5` — *"so that it stands on the plan's protection account and can
  be settled with everything else owed on it"*; `confirm_plan_giveup_9d16ef5f` — *"once everything
  owed and everything unearned have answered each other"* (within the same call).

### prerequisite_graph

Check 7 over the whole graph. `prerequisite` is filled in on all five policies
(`[]` on `insure_ext_amendment_reprice`, `insure_ext_premium_presentation`,
`insure_ext_giveup_charge`).

| blocked policy | problem | kind | gate | form | resolved_by | acyclic |
| --- | --- | --- | --- | --- | --- | --- |
| `insure_ext_claim_settlement` | `insure_ext_amendment_reprice` | `value_input` | `covered_value` | state | `confirm_plan_value_amendment_50d33fe4` | yes |
| `insure_ext_giveup_settlement` | `insure_ext_premium_presentation` | `value_input` | `premium_raised` | state | `present_plan_premium_8deb00b0` | yes |
| `insure_ext_giveup_settlement` | `insure_ext_giveup_charge` | `value_input` | `fees_standing` | state | `raise_plan_giveup_charge_59dbe3e5` | yes |

- Every `problem` points at another extended policy id in this file; none points at a base policy or
  at itself. The edge set `{settlement→reprice, giveup→presentation, giveup→charge}` has no cycle,
  and no cycle is created across the two tasks either.
- Every `policy_source` is verbatim locatable in the **blocked** policy's own `rule` (quoted in
  `prerequisite_sentences` below).
- `form` is `state` on all three; `fallback_reason` is absent on all three, which is correct, since
  it is required exactly on action-form edges.
- `condition` on each edge names the handling-time state the sentence derives and is neither
  strengthened nor weakened: `covered_value` ↔ "the covered value carried on the plan equals the
  price the covered holding's own record shows"; `premium_raised` ↔ "the protection account carries
  a premium entry for every presentation that has fallen due"; `fees_standing` ↔ "the protection
  account carries the charge the plan owes for being given up". No authoring-viewpoint phrasing
  ("in this task", "at the opening", "the current world") appears anywhere in the three
  `prerequisite` blocks.
- `resolved_by` is the depended-on policy's own `target_tool` in all three cases, and each genuinely
  moves the binding named in `effect`: `confirm_plan_value_amendment_50d33fe4` rewrites
  `insure_holdings.covered_value_usd` (the `covered_value` binding);
  `present_plan_premium_8deb00b0` creates an `insure_premium_charge` row (the `premium_raised`
  binding is `SUM('insure_ledger','amount_usd', event_type='insure_premium_charge')`);
  `raise_plan_giveup_charge_59dbe3e5` creates an `insure_fee_charge` row (the `fees_standing`
  binding is `SUM('insure_ledger','amount_usd', event_type='insure_fee_charge')`).
- `kind` matches `gate` on all three: each `gate` names a binding that genuinely exists in the
  blocked policy's `compute` (`covered_value`, `premium_raised`, `fees_standing`), so `value_input`
  is the honest label in each case and no edge is a status flip dressed as a value.

PASS.

### prerequisite_sentences

Check 6, four-point test on each of the three edges.

**E1 — `insure_ext_claim_settlement` waits on `insure_ext_amendment_reprice`.**
Sentence (verbatim, `insure_ext_claim_settlement.rule` sentence 2): *"What a claim pays is worked
out only after the value the plan carries as covered stands at the price the covered holding's own
record shows, since what is paid is measured against the value the plan covers."*
(1) ordering connective: "only after". (2) form: **state** — "the value the plan carries as covered
stands at the price the covered holding's own record shows" names a record-visible state in the
words `find_protection_plans` and `find_season_passes` use (the covered value on the plan; the price
on the pass record), with no action, performer or tool. (3) names no tool, no policy id, no
snake_case token, no row id. (4) strength and scope match `condition` exactly — both are the plain
equality of the two figures, neither broader nor narrower.
One write of this difficulty brings that state about: `confirm_plan_value_amendment_50d33fe4` is the
only tool in the module that writes `covered_value_usd`. No second candidate, so the hop resolves.
Derivation the reader performs: the sentence says the payout waits on the covered value equalling
the pass record's price → `find_protection_plans` gives `covered_value_usd`, `find_season_passes`
gives `price_paid_usd` → they differ → `insure_ext_amendment_reprice.rule` is the only rule in the
charter that describes bringing the covered value onto that price (*"The premium on a plan whose
covered value is brought onto the price the covered holding's own record shows is worked out afresh
and replaces the premium frozen on the plan"*) → its `target_tool` is the write, and it is the
household's own. One reading only.
`insure_ext_claim_settlement.rule` carries no second wording of this dependency, no tool name and no
other policy's id; `insure_ext_amendment_reprice.rule` does not restate the sentence.

**E2 — `insure_ext_giveup_settlement` waits on `insure_ext_premium_presentation`.**
Sentence (verbatim, `insure_ext_giveup_settlement.rule` sentence 2): *"What the plan's premium
account is left standing at is worked out only after every instalment of premium that has fallen due
on the plan stands raised on the protection account."*
(1) "only after". (2) state form — "every instalment of premium that has fallen due … stands raised
on the protection account" is a record-visible state in the words
`find_protection_account_entries` uses. (3) no tool, id or token. (4) matches `condition`.
`present_plan_premium_8deb00b0` is the only write that creates an `insure_premium_charge` row; no
second candidate. Derivation: compare the presentations fallen due on the covered holding's schedule
(`find_pass_account_entries`, `passes_installment_charge` rows) against the premium entries on the
protection account → they are short → `insure_ext_premium_presentation.rule` is the only rule
describing raising premium for presentations fallen due and unraised → its tool is the write.

**E3 — `insure_ext_giveup_settlement` waits on `insure_ext_giveup_charge`.**
Sentence (verbatim, `insure_ext_giveup_settlement.rule` sentence 3): *"What the plan's premium
account is left standing at is settled only once the charge the plan owes for being given up stands
raised on the protection account."*
(1) "only once". (2) state form. (3) clean. (4) matches `condition`.
`raise_plan_giveup_charge_59dbe3e5` is the only write that creates an `insure_fee_charge` row;
`insure_ext_giveup_charge` is the only rule describing that charge. One reading.

State-form priority is honoured on all three edges (no `fallback_reason` is claimed anywhere, so
there is no action-form fallback to test). No `rule` in the charter states a cross-problem order
that grounds no declared edge: the only ordering connectives in the five extended rules are the
three sentences above plus intra-computation orderings ("The share is taken of the value at risk
first…", "The charge is the greater … taken before anything is allowed against it", "The unearned
premium is worked out first and in full, and only then set against what is unpaid"), each of which
orders steps inside one calculation and not two problems. No **base** rule sentence grounds any
edge. No docstring states a position in a sequence beyond OBS-5 above.

PASS.

### override_declarations

Check 1's finding half, run once, sentence by sentence against each policy's `base_policy_refs`.

**A. `insure_ext_amendment_reprice` — base refs `insure_eligibility_and_quote`, `insure_premium_terms`.**
- A1 *"Where the plan allows it, the holding covered or the person a payout would be made to may be
  changed against the plan's amendment fee, and a change to a holding of a higher value reprices the
  premium from the date of the change rather than from the start of cover."* — handled differently;
  **declared** in `overwrite[0]`.
- A2 *"A plan priced on the value covered charges its rate of the covered value, then is brought up
  … the bounds are applied after the rate, never before."* — handled differently (rate is loaded /
  relieved); **declared** in `overwrite[1]`.
- A3 *"The quote is worked out from the covered value, which is the price committed to on the
  covered holding as the collective's records show it … and that value must fall between the plan's
  smallest and largest covered values."* — followed as to the source of the value; the
  min/max-covered-value bound is **not re-checked** after the reprice. Not a conflict on any
  reachable world of this difficulty (see OBS-6), inherited otherwise.
- A4 *"A flat plan charges its stated premium whatever the covered value."* — followed: for
  `Season Pass Protection Basic` (`premium_rate_pct` 0.00, min = max = 39.00) the extended
  `priced_premium = MN(39, MX(39, value × rate/100)) = 39.00` on every world. No conflict.
- A5 *"The result is rounded to the cent and frozen on the plan record."* — followed.
- A6 *"A premium is raised only while the plan record stands in the quoted, active, claim_open or
  claim_settled state."* — inherited unmodified.
- A7 *"An instalment of premium that goes unpaid past the plan's grace period stops cover; premium
  already paid is not returned when cover stops."* — inherited unmodified.
- A8 the purchase-window, calendar-day-counting and age-range sentences — inherited unmodified
  (they govern `insure_quote`, which this policy does not claim).
  Conclusion: every conflict named. **PASS.**
- **OBS-6 (dropped branch).** A1's replacement drops the amendment fee entirely: base charges the
  plan's `amendment_fee_usd` (20.00 on Plus and Premier, 0.00 on Concierge) for a change, and no
  extended selector ever produces it, nor does any task tool raise it. The drop is inside a declared
  override, so it is legal; it is recorded because it is the "dropped branch" shape the check names.
- **OBS-7.** A3 is not re-applied after the reprice: `priced_premium` bounds the *premium*
  (`premium_minimum_usd`/`premium_maximum_usd`) but nothing bounds the new *covered value* against
  `min_covered_value_usd`/`max_covered_value_usd`. On a pass whose recorded price has been moved
  above the plan's `max_covered_value_usd`, base says the plan may not stand at that value and
  extended reprices anyway. Not reachable on either task's world (see `0.md`).

**B. `insure_ext_claim_settlement` — base refs `insure_claim_assessment`, `insure_claim_intake`, `insure_cover_start`.**
- B1 *"The amount allowed is the plan's benefit share for the event claimed on, taken of the covered
  value, less the plan's excess, and then brought down to the plan's per-claim cap; it is never below
  zero and never more than the benefit left on the plan."* — handled differently (value at risk
  replaces covered value; credits and arrears are also set against); **declared** in `overwrite[0]`,
  and the cap and benefit-left ceiling are restored verbatim in the extended rule's penultimate
  sentence.
- B2 *"A claim made on an event the plan excludes is refused whatever the circumstances, and an
  exclusion always beats a cover…"* — followed; restated inside the extended rule's last sentence
  (*"A claim made on a peril the plan names as excluded is refused whatever this rule would otherwise
  work out, and nothing is paid on it."*). No conflict.
- B3 *"A medical claim is allowed only where a doctor has certified the insured unfit to ski for at
  least the plan's threshold in consecutive days, and a closure claim only where the mountain was
  shut for at least the plan's threshold…"* — inherited unmodified.
- B4 *"The payout is made only while the plan record stands in the claim_open or claim_settled
  state…"* — inherited unmodified.
- B5 *"A plan that has already met its allowance of claims for the season entertains no further
  claim…"* — inherited unmodified.
- B6 *"The payout goes out by the plan's payout method and never in cash at the desk."* — inherited;
  the tool's `payout_method` argument takes the tier's `payout_method`.
- B7 (`insure_claim_intake`) the notice period, submission period, and *"Whether the papers are
  complete is answered by the collective's own record of what has been received…"* — inherited; the
  extended rule's document tiers rest on `document_status = accepted` on the collective's own ledger
  rows, which follows B7 rather than contradicting it.
- B8 (`insure_cover_start`) the waiting period, the pre-existing exclusion and the benefit load —
  inherited unmodified; `benefit_left` is computed from the loaded-cover ledger, which is what
  `insure_cover_start` says the load is.
  Conclusion: every prose conflict named; the one gap is the base **formula** block (OBS-4). **PASS
  with observation.**

**C. `insure_ext_premium_presentation` — base ref `insure_premium_terms`.**
- C1 *"a plan collected alongside the covered holding's instalments divides the premium over the
  instalments still to fall on that holding and is presented with them."* — handled differently;
  **declared** in `overwrite[0]`.
- C2 *"A plan collected in a single payment takes the whole premium when the plan is taken"* — NOT
  named in the `overwrite` (the superseded clause begins at "a plan collected alongside…"). Extended's
  `instalment_measure` fall-through-adjacent tier 2 gives *"one instalment is the whole premium still
  to be collected"*, and `presentations_due` can multiply it: on a single-payment plan written over a
  financed holding, `presented_count = MX(1, holding_charged − premium_raised_count)` can exceed 1,
  so the amount presented is a whole-premium multiple. Recorded as **OBS-8**, not a red light: no
  world of this difficulty instantiates it (the only task that uses this policy carries
  `premium_payment_schedule = with_holding_instalments`), so no second defensible number can be
  demonstrated.
- C3 *"A premium is raised only while the plan record stands in the quoted, active, claim_open or
  claim_settled state."* — inherited unmodified.
- C4 *"The premium is worked out on the plan's basis … rounded to the cent and frozen on the plan
  record."* — followed: extended presents instalments **of** the frozen `premium_usd`, never
  recomputes it.
- C5 *"An instalment of premium that goes unpaid past the plan's grace period stops cover…"* —
  inherited unmodified.
  Conclusion: **PASS with observation (OBS-8).**

**D. `insure_ext_giveup_charge` — base refs `insure_lapse_and_reinstatement`, `insure_cancellation`.**
- D1 *"The plan's cancellation fee is retained from whatever comes back."* — handled differently;
  **declared** in `overwrite[0]`.
- D2 *"The premium comes back in full only where the plan is given up no later than the free look
  period counted in calendar days from the day the plan was taken."* — **conflicted and NOT named in
  this policy's `overwrite`.** See **F-RED-1**.
- D3 *"A plan fee is raised only while the plan record stands in the quoted, active, claim_open,
  claim_settled, lapsed or cancelled state."* — inherited unmodified.
- D4 the lapse / grace / reinstatement-window sentences — inherited unmodified; this policy raises
  no reinstatement fee.
- D5 *"Cover ends on the day the cancellation is recorded…"* — inherited (restated by the sibling
  policy, not by this one).
  Conclusion: **one undeclared override, F-RED-1.**

**E. `insure_ext_giveup_settlement` — base ref `insure_cancellation`.**
- E1 *"The premium comes back in full only where the plan is given up no later than the free look
  period…"* — **declared** in `overwrite[0]`.
- E2 *"After the free look period the plan's cancellation basis decides what comes back: on the pro
  rata basis … on the no refund basis nothing comes back at all."* — **declared** in `overwrite[1]`.
- E3 *"A household may give a plan up at any time."* — followed.
- E4 *"The plan's cancellation fee is retained from whatever comes back."* — handled by the sibling
  policy `insure_ext_giveup_charge`, whose `overwrite` names it (D1). Consistent across the two.
- E5 *"A plan on which a claim has already been paid is never refunded any premium, whatever its
  basis, because the cover has already answered for itself."* — **conflicted and NOT named in this
  policy's `overwrite`.** See **F-RED-2**.
- E6 *"Cover ends on the day the cancellation is recorded and not on the day the household says they
  stopped wanting it."* — followed and restated verbatim as the extended rule's last sentence.
- E7 the calendar-day counting rule — followed verbatim inside E1's replacement.
  Conclusion: **one undeclared override, F-RED-2.**

### factor_ladders

Charter-global structure of the factors. Counts per policy; ladders all have exactly three tiers,
the fall-through counted; every tier's condition is stated in the `rule` with its value or method,
and every tier is a branch of the `decides` binding.

| policy | factors | `parameter` | `method` | binding sets disjoint | `decides` is an input (never `result`) | multi-source factors | `cross_difficulty` |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `insure_ext_amendment_reprice` | 6 | 4 (`rate_standing`, `age_adjustment`, `household_adjustment`, `standing_adjustment`) | 2 (`change_anchor`, `difference_spread`) | yes | yes | `rate_standing`, `change_anchor` | all 6 → `passes` |
| `insure_ext_claim_settlement` | 6 | 3 (`peril_share`, `credit_offset`, `holding_arrears_offset`) | 3 (`measuring_day`, `spread_span`, `value_at_risk_measure`) | yes | yes | `peril_share`, `value_at_risk_measure`, `spread_span` | 4 → `passes` |
| `insure_ext_premium_presentation` | 4 | 3 (`collectible_basis`, `schedule_remaining`, `presentations_due`) | 1 (`instalment_measure`) | yes | yes | `collectible_basis`, `schedule_remaining` | `schedule_remaining` → `passes` |
| `insure_ext_giveup_charge` | 4 | 3 (`fee_scale`, `minimum_earned`, `charge_relief`) | 1 (`term_anchor`) | yes | yes | `minimum_earned` | `term_anchor`, `charge_relief` → `passes` |
| `insure_ext_giveup_settlement` | 5 | 2 (`return_basis`, `return_allowance`) | 3 (`giveup_anchor`, `unearned_measure`, `offset_reach`) | yes | yes | `return_basis`, `return_allowance` | `unearned_measure`, `offset_reach` → `passes` |

Every policy declares 4–6 factors with at least 2 `parameter` and at least 1 `method`. Per task, at
least one multi-source and at least one `cross_difficulty` factor is present (task 0 →
`rate_standing` and six passes-reading factors; task 1 → `schedule_remaining` and five
passes-reading factors).

Label honesty: every `method` tier changes the algorithm rather than substituting a number —
`change_anchor` / `term_anchor` / `giveup_anchor` / `measuring_day` select which **anchor date** a
span is measured from; `difference_spread` / `unearned_measure` / `instalment_measure` /
`spread_span` / `value_at_risk_measure` select between a **day-proration**, an **instalment share**
and a **whole-amount** rule; `offset_reach` selects **which ledger families** enter the offset.
Every `parameter` tier substitutes a number (a rate, a step, a share, a count, an amount). No
`method` tier names a computation rule the charter does not state.

Tier distinctness: no two tiers of any ladder, the fall-through included, select the same value or
method on a tier where the ladder is live. Two value-collision cases exist but are unreachable:
`peril_share` gives `job_loss_benefit_pct = relocation_benefit_pct = 0.00` on
`Season Pass Protection Basic` and on `Collective Trip Protection Standard`, but both of those tiers
name `job_loss` and `relocation` in `excluded_perils`, so a claim that would select either tier is
refused by B2 before the share is taken; recorded as **OBS-9**.

Condition realism: every condition a tier states divides the customers who reach that write and is
one this line of business genuinely weighs — arrears on the financed holding, a claim-free season,
the age band the pass is priced in, how many passes the household opened, whether the pass is a
renewal or a carry-forward, whether an upgrade was charged, whether a paper is accepted, whether the
pass has been scanned, whether credit has been issued, whether the holding has been given up,
whether the plan is inside its free look, whether cover has run past its waiting period. None of them
holds of every customer who reaches the write.

**F-RED-3 (unreal ladder outcome)** is recorded below: one `method` tier of
`insure_ext_claim_settlement.spread_span` produces an outcome this line of business would not
publish. Whether each factor **bears weight** is a fact about one world and lives in `0.md` /
`1.md` under `factor_weight`.

- **OBS-10 — `cross_category.reads` mislabels three tier parameters as record columns.**
  `insure_ext_claim_settlement.cross_category[0].reads` lists
  `passes_holdings.operating_days_included`, `passes_holdings.day_use_deduction_usd`, and
  `insure_ext_amendment_reprice` / `insure_ext_premium_presentation` /
  `insure_ext_giveup_settlement` list `passes_holdings.installment_count`. None of the three is a
  column of `passes_holdings` (`blueprint/db_schema.json` → `passes_holdings` has 22 columns and
  none of these); all three are per-tier parameters of `blueprint/products/passes.yaml`, which is
  why the compute reads them with `CPARAM(...)` and not `CFIELD(...)`.

### findings

**F-RED-1 — `SOURCE-POLICY RED` (undeclared override), charter-global.**
- *Symptom.* A plan given up inside its free look period is charged a give-up charge greater than
  zero, while the base charter says the premium comes back in full and the extended sibling policy
  declares that base sentence superseded only as to the premium, never as to a charge.
- *Root cause.* `insure_ext_giveup_charge` introduces a floor (`minimum_earned`) that conflicts with
  a base sentence its own `overwrite` does not name. Its `overwrite` names only *"The plan's
  cancellation fee is retained from whatever comes back."*
- *Evidence (the two passages, verbatim).*
  Base `blueprint/products/insure.yaml` → `insure_cancellation.rule`: *"The premium comes back in
  full only where the plan is given up no later than the free look period counted in calendar days
  from the day the plan was taken."*
  Extended `insure.extended.yaml` → `insure_ext_giveup_charge.rule`: *"The collective keeps a least
  amount on a plan given up, which is nothing. It is instead the minimum earned share this rule sets
  of the premium frozen on the plan where the plan is priced on the value covered and cover has run
  past the plan's waiting period; … The charge is the greater of the part of the fee the charge
  stands at and the least amount the collective keeps…"*
- *Demonstrated consequence (same situation, two conclusions).* Take a
  `Season Pass Protection Premier` plan (`premium_basis = percent_of_covered_value`,
  `free_look_days = 14`, `waiting_period_days = 7`, `cancellation_fee_usd = 35.00`,
  `premium_usd = 225.17`) given up on day 10 after it was taken, with the covered holding standing
  active and no premium payment matched. Extended: `fee_share = 0.0` (inside free look),
  `minimum_kept = RND(225.17 × 10.00 / 100, 2) = 22.52`, `charge_allowance = 0.0`, so
  `result = MX(0.0, RND(MX(RND(35.00 × 0.0, 2), 22.52) − 0.0, 2)) = 22.52`. Base: the plan is inside
  its free look, so the premium comes back in full and the cancellation fee — the only charge base
  names — is superseded, giving `0.00`. Two defensible numbers, 22.52 and 0.00, from the same world.
- *Affected artifact and location.* `env/env_0004_ski_resort_operator/tasks/pass_protection_desk/insure.extended.yaml`,
  `insure_ext_giveup_charge` → `overwrite` (missing entry for the base sentence above), `rule`
  (the "least amount the collective keeps" sentences), `params.minimum_earned_share_pct`,
  `compute.minimum_kept` and `compute.result`, factor `minimum_earned`.
- *Bears on.* Task 1 (`insure_ext_giveup_charge` is in its tree). The per-task demonstration and
  the reason it does not move task 1's scored value are in
  `env/env_0004_ski_resort_operator/audits/policy_task/pass_protection_desk/1.md`.
- *Relation to previous revisions.* None; first revision.

**F-RED-2 — `SOURCE-POLICY RED` (undeclared override), charter-global.**
- *Symptom.* On a plan with a paid claim, the base charter returns no premium at all and the
  extended charter returns half of the unearned premium; neither the base sentence nor the conflict
  is named anywhere in `insure_ext_giveup_settlement.overwrite`.
- *Root cause.* The `return_allowance` factor's tier 2 creates a half-return branch on exactly the
  case base forecloses.
- *Evidence (the two passages, verbatim).*
  Base `insure_cancellation.rule`: *"A plan on which a claim has already been paid is never refunded
  any premium, whatever its basis, because the cover has already answered for itself."*
  Extended `insure_ext_giveup_settlement.rule`: *"The share of the unearned premium the plan returns
  is nothing. It is instead the whole of it where the plan returns premium on a pro rata basis and
  no payout stands on the plan for the season; it is instead half of it where the plan returns
  premium on a pro rata basis and a payout stands on the plan for the season; and it is nothing in
  every other case."*
  `insure_ext_giveup_settlement.overwrite` names only *"The premium comes back in full only where
  the plan is given up no later than the free look period…"* and *"After the free look period the
  plan's cancellation basis decides what comes back: …"*. Neither is the sentence above.
- *Demonstrated consequence.* Take any `pro_rata_by_days` plan (Plus, Premier, Elite, Concierge) on
  which one `insure_claim_payment` row stands, given up with half its term still to come and
  `return_base` = R. Extended: `return_share = 0.5`, so `unearned_premium = RND(R × 0.5 × 0.5, 2)`,
  a strictly positive return set against what is unpaid. Base: *"never refunded any premium,
  whatever its basis"* → `unearned_premium = 0.00` and the whole unpaid balance stands. For
  R = 225.17 and a half-term, extended returns 56.29 and base returns 0.00 — the closing balance
  differs by 56.29 on one and the same world.
- *Affected artifact and location.* `insure.extended.yaml`, `insure_ext_giveup_settlement` →
  `overwrite` (missing entry), `rule` (the "share of the unearned premium the plan returns"
  sentences), `compute.return_share`, `compute.unearned_premium`, factor `return_allowance` tier 2.
- *Bears on.* Task 1. Whether it moves task 1's scored value is demonstrated in `1.md`.
- *Relation to previous revisions.* None; first revision.

**F-RED-3 — `SOURCE-FACTOR RED` (unreal ladder outcome), charter-global.**
- *Symptom.* One `method` tier of `insure_ext_claim_settlement.spread_span` puts a count of
  *operating days the pass admits the holder on* into the denominator of a ratio whose numerator is
  a count of *calendar days of the season still to come*. On every pass tier whose operating-day
  allowance is below the 149-day season the resulting "value at risk" exceeds the whole value the
  plan covers — a proportion greater than one.
- *Root cause.* A unit mismatch inside a single tier: the rule fixes the numerator as calendar days
  (*"the days of the season still to come, counted from the day the claim is measured from to the
  day cover is due to end"*) while letting the denominator be an operating-day allowance.
- *Evidence.* `insure_ext_claim_settlement.rule`: *"Where the covered holding's account carries
  scans in the season and cover began on or before the day the season opened, the value at risk is
  instead the value the plan covers in proportion to the days of the season still to come, counted
  from the day the claim is measured from to the day cover is due to end, over the days the value is
  spread across"*; and *"The days the value is spread across are the operating days the covered
  holding's own tier includes where cover began on or before the day the season opened and that tier
  includes operating days"*. `compute.value_at_risk` implements it as
  `RND(covered_value * MX(0, DAYS(claim_anchor_date, F('expiry_date'))) / span_days, 2)` with
  `span_days = pass_operating_days`. Tier table: `blueprint/products/passes.yaml`
  `operating_days_included` = 4 (Four-Day Flex), 107 (Midweek), 150 (all five others); season
  2026-11-20 → 2027-04-18 = 149 calendar days.
- *Demonstrated consequence (a tier outcome no such business would publish).* A
  `Granite Ridge Four-Day Flex Pass` (`pass_price_usd` 419.00, `operating_days_included` 4) is inside
  `Season Pass Protection Basic`'s covered-value band (379.00–1149.00), so the tier is reachable.
  With cover beginning on the season's opening day, one scan on the account and the claim measured
  from 2027-01-09 (99 calendar days to 2027-04-18), the value at risk is
  `RND(419.00 × 99 / 4, 2) = 10,370.25` — **24.75× the price of the pass the plan covers**. A
  `Granite Ridge Midweek Pass` (629.00, 107 operating days) measured from the season's first day
  gives `RND(629.00 × 149 / 107, 2) = 875.90`, **139% of the pass price**. No pass-protection
  business publishes a "proportion of the season still to come" that exceeds the whole value
  covered; the base charter's own ceiling is `benefit_limit_pct` ≤ 100.00 of the covered value.
  (The per-claim cap masks the number downstream on the small tiers; it does not make the tier's
  stated method one a business would publish, and on the Midweek case the cap does not bind.)
- *Affected artifact and location.* `insure.extended.yaml`, `insure_ext_claim_settlement` →
  `rule` (the two sentences above), `compute.span_days`, `compute.value_at_risk`,
  factors `spread_span` tier 1 and `value_at_risk_measure` tier 1.
- *Bears on.* Task 0. Whether it moves task 0's scored value is demonstrated in `0.md`.
- *Relation to previous revisions.* None; first revision.

**Observations (charter-global, no consequence demonstrable):** OBS-1 … OBS-10 above, each
recorded in the section whose check surfaced it. They are not grounds for rework.

## closing_checklist

Written after both tasks reached a frozen `source_derivation_frozen` and a `source_gt_comparison`
carrying PASS. This section sits below the charter-global section because it is the one
difficulty-level conclusion reached **after** the reveals; nothing in it was written back into the
pre-reveal section above.

- **Files correspond one-to-one with the tasks.**
  `env/env_0004_ski_resort_operator/audits/policy_task/pass_protection_desk/` holds `_difficulty.md`,
  `0.md` and `1.md` against `tasks/0.json` and `tasks/1.json` (M = 2). This is revision 1, so there
  is no older revision to preserve; any re-audit appends under `## revision_2` and leaves this text
  untouched. Both comparison sections carry PASS.
- **Extended policies fully covered; task scopes pairwise disjoint.**
  Five extended policies. `tasks/0.json.charter_scope.extended_policies` =
  {`insure_ext_amendment_reprice`, `insure_ext_claim_settlement`};
  `tasks/1.json.charter_scope.extended_policies` = {`insure_ext_giveup_charge`,
  `insure_ext_premium_presentation`, `insure_ext_giveup_settlement`}. Intersection empty, union all
  five. Each scope spans a whole problem tree — its root problem and every prerequisite problem — so
  no tree is split across tasks.
- **Task tools and GT closed.** Five task tools, each named by exactly one policy's `target_tool`
  and called in exactly the task whose scope claims that policy: task 0 calls
  `confirm_plan_value_amendment_50d33fe4` and `settle_protection_claim_ed51c2df`; task 1 calls
  `raise_plan_giveup_charge_59dbe3e5`, `present_plan_premium_8deb00b0` and
  `confirm_plan_giveup_9d16ef5f`. No task calls a tool outside its scope and no tool is unused.
- **uuid8s independently generated and frozen.** `50d33fe4`, `ed51c2df`, `8deb00b0`, `59dbe3e5`,
  `9d16ef5f` — pairwise distinct, no shared prefix or tail, no sequence, no common stem; each
  appears once in `task_tools.py` and once as a `target_tool`. (Re-checked in
  `### action_binding_and_uuids`.)
- **Problem trees.** Task 0: 1 prerequisite problem, 1 `value_input` edge (floor max(1−1,1) = 1),
  the prerequisite resolved by the `owner="user"` tool `confirm_plan_value_amendment_50d33fe4`, no
  cycle. Task 1: 2 prerequisite problems, 2 `value_input` edges (floor max(2−1,1) = 1), the root
  itself resolved by the `owner="user"` tool `confirm_plan_giveup_9d16ef5f`, no cycle. Each tree
  sits within 1–3 prerequisite problems. The `prerequisite` edges of the whole difficulty —
  `claim_settlement → amendment_reprice`, `giveup_settlement → premium_presentation`,
  `giveup_settlement → giveup_charge` — remain a directed acyclic graph, and no cycle is created by
  any cross-task reference, since the two tasks' scopes share no policy.
- **Computations, baselines and factors.** Five computations across the two tasks; every one
  declares a `baseline` whose `rule` yields a definite number that differs from gold (122.14 vs
  117.46; 919.20 vs 541.60; 11.26 vs 81.06; 35.00 vs 13.77; 0.00 vs 49.20 — the last recorded as
  OBS-12.T1 for being world-independent). Factor counts 6 / 6 / 4 / 4 / 5, each within 4–6, each
  with at least 2 `parameter` and at least 1 `method`; per task at least one multi-source factor
  (`rate_standing`; `schedule_remaining`) and at least one `cross_difficulty` factor reading seeded
  `passes` records. Every ladder has three pairwise-disjoint tiers stated in full in its own rule.
  All 25 declared factors were proved to bear weight on their own task's world against an honest
  baseline, by substitution and recomputation (`0.md` and `1.md` → `factor_weight`). Tier outcomes
  are distinct everywhere the ladder is live; the exceptions are recorded as OBS-9 (unreachable
  collisions) and **F-RED-3** (a tier method the line of business would not publish).
- **Instantiation-stage gates re-run on the final form** (all from the repository root, against
  `env/env_0004_ski_resort_operator/tasks/pass_protection_desk`):
  `check_extended` EXTENDED OK · `check_task_tools` TASK TOOL CONTRACT OK ·
  `replay_tasks` REPLAY OK (0.json 10 acts / 33 closure rows matched; 1.json 12 acts / 25 matched) ·
  `check_solvability` SOLVABILITY OK · `check_compute` COMPUTE OK (branches 50 / 52, steps 10 / 12,
  suite means 51.00 and 11.00) · `check_grounding` GROUNDING OK · `check_cross_fire` SCOPE OK ·
  `check_cache_diff` INFO only. `check_traceability` remains NOT OK, and its five misses are exactly
  the five hidden task-tool names; `env/env_0004_ski_resort_operator/kb` does not exist yet, so the published
  KB that the render step writes from each policy's `target_tool` cannot supply them. This is the
  declared pre-render state and not a finding of this audit.

### difficulty verdict

**Policy self-consistency: NOT PASS at the charter — two undeclared overrides, F-RED-1 and
F-RED-2.** Both are charter-global: each is a base sentence a policy conflicts with and does not
name in its own `overwrite`, and each was demonstrated by quoting the two passages and computing the
two conclusions they reach in one and the same situation drawn from the charter's own tier tables.
Neither moves a scored value on either task's world, and each task file records that fact against its
own world.

**Factors bear weight: NOT PASS at the charter — F-RED-3**, an unreal ladder outcome in
`insure_ext_claim_settlement.spread_span` tier 1, demonstrated from the charter's own
`operating_days_included` table against the 149-day season. Every declared factor of every
computation was separately proved to bear weight on its own task's world.

**Per task, all four relationships PASS**: `0.md` → PASS on policy self-consistency (this task), the
problem tree, factor weight and unique solution; `1.md` → PASS on all four. Both independent
derivations reproduced GT figure for figure, tier for tier, argument for argument, with no
contamination on either task.

So the difficulty does **not** clear the source-layer audit as it stands: the four relationships hold
per task, but the charter carries two undeclared overrides and one unreal ladder outcome, each with
its consequence demonstrated. Ten observations (OBS-1 … OBS-10) and three task-level observations
(OBS-0.T0, OBS-11.T0, OBS-12.T1) are recorded and are not grounds for rework. No problem found here
is attributed to a solving agent, and no fix is designed or arranged by this audit.

---

# revision_2

Re-audit round 2. Revision 1 above is preserved unaltered; nothing in it has been rewritten to
accommodate the rework.

## charter_global_frozen (revision 2)

- auditor: same independent policy-task auditor; round 2 is **not blind** — this auditor saw this
  difficulty's GT at the end of round 1, and says so rather than claiming a blindness it does not
  have. What is frozen below was nevertheless derived and written to disk **before** any field of
  the reworked `tasks/*.json` outside the whitelist was read this round.
- freeze time (this section): 2026-09-17, round 2.
- **Re-derivation grounds (the skill's hash rule).** Round 1 produced the charter-global sections
  from `insure.extended.yaml` sha256:16 `25e173ac54fb5be1` and `task_tools.py` sha256:16
  `5c1c7fa98aafd469`. Round 2's are `15021b061f1b681f` and `21f93863911cf2f0`. **Both have moved**,
  so every charter-global section is **re-derived in full** below rather than carried forward by
  reference. Masked task views: `tasks/0.json` `f735e128fa6195bb` → `55176cc8d273c2db` (**moved**);
  `tasks/1.json` `e157ea3f171501cb` → `e157ea3f171501cb` (**unchanged**, byte-identical).
  All four hashes were re-computed off the rebuilt masked root and match the brief.
- entry conditions: the coordinator's re-run gate snapshot came with the brief and is green on
  EXTENDED, TASK-TOOL-CONTRACT, REPLAY, SOLVABILITY, COMPUTE, GROUNDING, SCOPE; TRACEABILITY is the
  unchanged pre-render state. Masked views rebuilt by the same mechanical whitelist. Complete.
- fields masked and not read before this freeze: the same nine keys as round 1.

### base copy (re-checked)

`diff` of `insure.extended.yaml` lines 1–1170 against `blueprint/products/insure.yaml` is empty.
The base copy has **not** been rewritten by the rework — the whole of the base section, including
`variants[].parameters` and `parameter_schema`, stands exactly as the scenario constitution has it.
This matters for **R2-RED-1** below.

### what the rework changed (full inventory, derived by reading both artifacts)

| policy | changed |
| --- | --- |
| `insure_ext_amendment_reprice` | rule gains the covered-value bound sentence; the trailing "A household that holds no pass of its own…" sentence is **removed**; `new_covered_value` split into `holding_price` + a bounded `new_covered_value`; `baseline.rule` gains the bound sentence and `baseline.params` gains `min_covered_value_usd`, `max_covered_value_usd`; `cross_category.reads` drops `passes_ledger.credit_reason` and de-prefixes `installment_count` |
| `insure_ext_claim_settlement` | **second `overwrite` entry added**, naming base *"A complete claim is assessed against the plan's list of covered events."*; `value_at_risk` tier 1 gains an `MN(covered_value, …)` **ceiling** and the rule gains "and never more than the value the plan covers"; `span_days` **restructured** — the operating-day tier is gone, replaced by season-days / cover-days / claimable-days, and `pass_operating_days` is no longer read at all; new bindings `claimable_days`, `assessed_from_paper`, `excluded_claim`; `result` gains the exclusion branch; `spread_span` becomes `cross_difficulty: null`; `reads` de-prefixes `day_use_deduction_usd` and drops `operating_days_included` |
| `insure_ext_premium_presentation` | `presented_count` tiers 1 and 2 gain the `with_holding_instalments` conjunct, in rule and compute; `reads` de-prefixes `installment_count` |
| `insure_ext_giveup_charge` | `minimum_kept` tiers 1 and 2 gain the **"given up after its free look period has run out"** conjunct, in rule and compute; the rule's fall-through spells out "a plan given up inside its free look period included, so that nothing at all is charged on a plan given up inside that period" |
| `insure_ext_giveup_settlement` | `return_share` tiers 1 and 2 gain the **`payouts_standing == 0`** conjunct and split on a new `term_run_share` into a whole return and a **short-rate** return (`short_rate_return_share_pct: 90.00`); the fall-through spells out "a plan on which a payout stands for the season included"; headline sentence rewritten to "what the unearned premium is set against, less that unearned premium"; new sentence defining what stands unpaid; `giveup_day` tier 1 gains `F('claim_opened_date') == ''` and the rule gains "no paper stands filed against one"; `offset_reach` restructured (default = charges standing; new cancelled-holding tier); `baseline.rule` gains the unpaid-account and free-look sentences and `set_against` defaults to `fees_standing`; `baseline.params` = `[free_look_days]` |
| `task_tools.py` | every ordering word removed from every docstring; the five uuid8s, owners, signatures and bodies are otherwise unchanged |
| `tasks/0.json` (masked part) | `user_scenario` only — `initial_state` is content-identical to round 1 (same 1 customer, 2 passes, 18 pass-ledger rows, 1 plan, 11 protection-ledger rows, same values) and `frozen_time` is unchanged |

### policy_conflict_scan (re-derived)

Subject ownership, triggers, time anchors, terminal states and the cross-category read boundary are
**unchanged from revision 1** and were re-checked line by line: one extended owner per subject, no
two policies sharing a `(target_tool, computes)` pair, one clock, `passes` the only category read,
`confirm_plan_giveup_9d16ef5f` still the only writer of `insure_holdings.status`. Task scopes are
still disjoint and jointly complete over the five policies.

**One conflict is new and is a regression**, recorded as **R2-RED-1** in `### findings (revision 2)`:
`insure_ext_claim_settlement` now supersedes base `insure_claim_assessment`'s covered-events
sentence and puts nothing in its place, so the merged charter pays a claim on a peril the plan's own
`covered_perils` list does not contain.

### rule_compute_equivalence (re-derived)

Swept sentence by sentence in both directions over all five reworked policies. Every quantity,
window, filter, tier, branch, cross-category read, acting base, grouping, cap/floor and rounding
point has a `compute_basis` quotation verbatim locatable in its own `rule`, and every
`compute_basis` key is a binding that exists in `compute`. The new bindings all carry a basis:
`holding_price` / `new_covered_value` ← the covered-value bound sentence; `claimable_days` ←
"they are the days from the day the plan's waiting period ended to the day cover is due to end in
every other case"; `assessed_from_paper` ← "The payout is recorded against the paper it was assessed
from, which is the last paper accepted on the claim."; `excluded_claim` ← "A claim made on a peril
the plan names as excluded is refused whatever this rule would otherwise work out, and nothing is
paid on it."; `term_run_share` ← "The part of the term that has run is measured from the day cover
began to the day the plan is given up, against the days from the day cover began to the day cover is
due to end."; `account_unpaid` ← its own new sentence.

Every tier of every one of the 25 ladders is stated in its own rule with its condition and its value
or method, and every branch of every `decides` binding is a tier the rule states. This was
re-verified tier by tier on all the tiers the rework touched (`spread_span` ×3, `minimum_earned` ×2,
`return_allowance` ×2, `offset_reach` ×3, `presentations_due` ×2, `giveup_anchor` ×1,
`value_at_risk_measure` tier 1).

Round-1 observations in this section, re-checked against the artifact:

- **OBS-1 — CLOSED.** `giveup_day` is now
  `NOW if (claim_papers_filed == 0 and F('claim_opened_date') == '' and closed_on_record == '')`,
  and the rule reads "…where no claim has been made on the plan in the season, no paper stands filed
  against one and the plan's record carries no day on which cover was closed". The predicate the
  compute tests is now the predicate the sentence states — a plan standing in `claim_open` with no
  paper lodged no longer satisfies the branch. Closed in the compute, not only in the wording.
- **OBS-2 — CLOSED.** The headline sentence now reads "…is what the unearned premium is set against,
  less that unearned premium", which is exactly `result = MX(0.0, RND(set_against −
  unearned_premium, 2))`; and a separate new sentence gives `account_unpaid` its own basis ("What
  stands unpaid on the protection account is the premium raised on the plan and the charges raised
  on it, less the payments matched to premium entries, and it is never below zero"). The two
  readings that round 1 could not tell apart are now one reading.
- **OBS-3 — CLOSED.** The unimplemented sentence "A household that holds no pass of its own for the
  season has nothing this rule can be worked out on, and no plan of theirs is repriced." is gone
  from `insure_ext_amendment_reprice.rule`. No rule sentence of the charter now lacks a compute
  counterpart. (Round 1 missed a second instance of the same shape:
  `insure_ext_claim_settlement`'s "A claim made on a peril the plan names as excluded is refused…"
  had no binding either. The rework has implemented it as `excluded_claim`, so that one is closed
  too — but the overwrite entry it arrived with is **R2-RED-1**.)
- **OBS-4 — NOT CLOSED; the attempted closure is itself the new red light.** See **R2-RED-1**.

### action_binding_and_uuids (re-derived)

Unchanged and still correct: the same five `(target_tool, computes)` pairs, each claimed by exactly
one policy; the same five uuid8s `50d33fe4`, `ed51c2df`, `8deb00b0`, `59dbe3e5`, `9d16ef5f`,
pairwise distinct, sharing no prefix or tail, forming no sequence, each appearing once in the module
and once as a `target_tool`. No tool adds a confirmation, review or wait outside its policy.

- **OBS-5 — CLOSED.** A scan of `task_tools.py` for `later`, `before`, `after`, `first`, `once`,
  `then`, `next` returns **no match anywhere in the file**. The sentence "…and the desk works every
  later figure out from them." has been removed from
  `confirm_plan_value_amendment_50d33fe4`, and the softer instances on
  `raise_plan_giveup_charge_59dbe3e5` and `confirm_plan_giveup_9d16ef5f` are gone as well. No
  docstring now states an action's position in a sequence.

### prerequisite_graph and prerequisite_sentences (re-derived)

All three edges are **unchanged in every field**, and each was re-tested from scratch:
`claim_settlement → amendment_reprice` (`value_input`, gate `covered_value`),
`giveup_settlement → premium_presentation` (`value_input`, gate `premium_raised`),
`giveup_settlement → giveup_charge` (`value_input`, gate `fees_standing`). For each:
`policy_source` is a verbatim sentence of the **blocked** policy's own rule (checked
programmatically after whitespace normalisation: all three `True`); `form: state` with no
`fallback_reason`, which is correct; an explicit ordering connective ("only after", "only after",
"only once"); no tool name, policy id, snake_case token or row id; `condition` neither strengthened
nor weakened; `resolved_by` is the depended-on policy's own `target_tool` and still the **only**
write in the module that brings the waited-on state about; `kind` matches `gate`, each gate naming a
binding that exists in the blocked policy's compute. None of the three sentences is restated in the
depended-on policy's rule (checked programmatically: all three `False`). The graph is still acyclic
and still crosses no task boundary.

The rework did not introduce any new cross-problem ordering language: the only ordering connectives
in the five rules remain the three prerequisite sentences plus intra-computation orderings. No base
rule sentence grounds any edge.

### override_declarations (re-derived, sentence by sentence)

Blocks A, C, D, E were re-swept in full against their `base_policy_refs`; block B is where the
regression is.

- **A — `insure_ext_amendment_reprice`: PASS.** A1 and A2 declared as before. **A3 is now followed
  rather than departed from**: the rule gains "The price the covered holding's record shows stands
  as the new covered value only where it falls between the plan's smallest and largest covered
  values; where it falls outside them the value the plan already covers stands and the premium is
  worked out on that instead", and `new_covered_value` implements it. A4–A8 inherited as before.
  **OBS-7 CLOSED.**
- **B — `insure_ext_claim_settlement`: NOT PASS.** `overwrite[0]` unchanged and correct.
  `overwrite[1]` is new and is **R2-RED-1**. B3–B8 still inherited unmodified.
- **C — `insure_ext_premium_presentation`: PASS.** C1 declared as before. **C2 is now followed**:
  `presented_count` tiers 1 and 2 both carry the `with_holding_instalments` conjunct in rule and
  compute, so a single-payment plan presents exactly one instalment and the whole-premium multiple
  round 1 recorded is unreachable. **OBS-8 CLOSED.** C3–C5 inherited.
- **D — `insure_ext_giveup_charge`: PASS.** D1 declared as before. **D2 is now obeyed rather than
  overridden** — see **F-RED-1 disposition** below. D3–D5 inherited.
- **E — `insure_ext_giveup_settlement`: PASS.** E1 and E2 declared as before. **E5 is now obeyed
  rather than overridden** — see **F-RED-2 disposition** below. E3, E4, E6, E7 inherited.
- **OBS-6 — answered with reasoning, and the reasoning is right.** The amendment fee that base A1
  charges is dropped inside a *declared* override, which check 1 makes legal; writing a fee sentence
  into the extended rule while no task tool of this difficulty raises a fee would create exactly the
  unimplemented-promise shape that OBS-3 was raised for and that the rework has just removed. The
  disposition is accepted. Recorded, closed as an observation, no rework owed.

### factor_ladders (re-derived)

| policy | factors | `parameter` | `method` | tiers each | `cross_difficulty` | vs revision 1 |
| --- | --- | --- | --- | --- | --- | --- |
| `insure_ext_amendment_reprice` | 6 | 4 | 2 | 3 | 6 → `passes` | unchanged |
| `insure_ext_claim_settlement` | 6 | 3 | 3 | 3 | 3 → `passes` (was 4; `spread_span` no longer reads `passes`) | ladder of `spread_span` and tier 1 of `value_at_risk_measure` rewritten |
| `insure_ext_premium_presentation` | 4 | 3 | 1 | 3 | 1 → `passes` | `presentations_due` tiers narrowed |
| `insure_ext_giveup_charge` | 4 | 3 | 1 | 3 | 2 → `passes` | `minimum_earned` tiers narrowed |
| `insure_ext_giveup_settlement` | 5 | 2 | 3 | 3 | 2 → `passes` | `return_allowance` and `offset_reach` ladders rewritten |

Every policy still declares 4–6 factors with ≥ 2 `parameter` and ≥ 1 `method`; every ladder still
has exactly three tiers; per task there is still ≥ 1 multi-source factor (`rate_standing` for task
0, `schedule_remaining` for task 1 — both untouched) and ≥ 1 `cross_difficulty` factor. Labels are
still honest: the rewritten `method` tiers select **which span a proportion is taken over**
(`spread_span`), **which algorithm measures the value at risk** (`value_at_risk_measure`) and
**which ledger families are in reach** (`offset_reach`); the rewritten `parameter` tiers select
numbers (0.0 / 0.5 / 1.0 and 1.0 / 0.9 / 0.0).

- **OBS-9 — CLOSED, and provably so.** Round 1 recorded that `peril_share` selects
  `job_loss_benefit_pct = relocation_benefit_pct = 0.00` on `Season Pass Protection Basic` and
  `Collective Trip Protection Standard`. Both perils are in both tiers' `excluded_perils`, and the
  rework's new `excluded_claim` binding now refuses such a claim outright
  (`result: "0.0 if excluded_claim == 1 else …"`), so neither colliding tier can decide a scored
  number on any world. Verified by computation: an SPP-Basic plan with `claim_reason = job_loss`
  now returns 0.00 whatever `peril_share` selects.
- **OBS-10 — CLOSED.** All five `cross_category.reads` lists now prefix only genuine
  `passes_holdings` / `passes_ledger` columns and carry the three tier parameters
  (`installment_count` ×3, `day_use_deduction_usd`) bare, without a table prefix.
  `operating_days_included` has left the charter entirely. Each prefixed entry was re-checked
  against `blueprint/db_schema.json` and is a real column.
- **F-RED-3's structural half — CLOSED.** `spread_span`'s ladder no longer contains a tier that
  divides a calendar-day numerator by an operating-day allowance. Its three tiers are now
  season-days, cover-days and claimable-days, all of them counts of calendar days, and the factor no
  longer reads `passes` at all. See the disposition below for the numeric proof.

### findings (revision 2)

#### Dispositions of the revision-1 red lights

**F-RED-1 — CLOSED, in the compute and not merely in the wording.**
The fix is a conjunct, not a sentence: `minimum_kept` now reads
`… if (P('premium_basis') == 'percent_of_covered_value' and free_look_days_used > P('free_look_days')
and waiting_days_run > 0) else (… if (P('premium_basis') == 'percent_of_covered_value' and
free_look_days_used > P('free_look_days')) else 0.0)` — the free-look conjunct is carried on **both**
non-zero tiers, so neither can fire inside the free look. The rule states it and states the
consequence outright: "…and it is nothing in every other case, a plan given up inside its free look
period included, so that nothing at all is charged on a plan given up inside that period."
Re-derived on **round 1's own worked case** — `Season Pass Protection Premier`, given up on day 10,
`premium_usd` 225.17, holding active, one premium payment matched — the charge is now **0.00**
(round 1: 22.52), with `fee_share = 0.0` and `minimum_kept = 0.0`. Base's conclusion for that case
is 0.00. The two now agree.
Swept across days since taken 0, 5, 10, 14, 15, 20 against `free_look_days = 14`: **0.00, 0.00,
0.00, 0.00, 13.77, 13.77** — zero throughout the free look, inclusive of the boundary day, exactly
as base's "no later than the free look period" requires, and nonzero only after it.
Tested on two cases of the auditor's own choosing that could have leaked a charge past the floor:
inside the free look with the **covered holding cancelled** (so `charge_allowance` = the whole
35.00 fee) → **0.00**; inside the free look on a **flat-premium** plan (`Season Pass Protection
Basic`, `free_look_days` 10, day 5) → **0.00**. No path charges a plan inside its free look.

**F-RED-2 — CLOSED, in the compute and not merely in the wording.**
`return_share` now reads
`1.0 if (P('cancellation_refund_basis') == 'pro_rata_by_days' and payouts_standing == 0 and
term_run_share > 0.5) else (K('short_rate_return_share_pct') / 100 if
(P('cancellation_refund_basis') == 'pro_rata_by_days' and payouts_standing == 0) else 0.0)` — the
`payouts_standing == 0` conjunct is carried on **both** non-zero tiers, so a plan with a payout
falls through to 0.0. The rule states it and names the case: "…and it is nothing in every other
case, a plan on which a payout stands for the season included, since the cover has already answered
for itself."
Re-derived on **round 1's own worked case** — a `pro_rata_by_days` plan with one
`insure_claim_payment` standing — `return_share = 0.0` and `unearned_premium = 0.00`, so the closing
balance is the whole of what is set against, **139.87**, and no premium comes back. That is exactly
base's "never refunded any premium, whatever its basis". Round 1 returned half.
Swept on payouts standing 0 / 1 / 2 → `return_share` 1.0 / 0.0 / 0.0. Cross-checked on a
`no_refund` plan (`Season Pass Protection Basic`) with and without a payout → 0.0 in both, which is
base's no-refund basis. The new short-rate tier was exercised on a world of the auditor's own
choosing (the same plan given up on 2026-12-20, inside the first half of its term):
`term_run_share = 0.2013`, `return_share = 0.9`. Three distinct outcomes, 1.0 / 0.9 / 0.0, and a
short-rate cancellation penalty is what that line of business actually does.

**F-RED-3 — CLOSED, and closed twice over.** The unit mismatch is removed at the root and a ceiling
is added behind it.
*Root fix.* `span_days` no longer has an operating-day tier. Its three tiers are now
`season_days` (cover from on or before the season's opening day, waiting period ending after cover
began), `DAYS(effective_date, expiry_date)` (cover beginning after the season opened) and
`claimable_days = MX(1, DAYS(waiting_period_end_date, expiry_date))` otherwise — three counts of
calendar days. `pass_operating_days` is gone from the compute, `operating_days_included` is gone
from `cross_category.reads`, and `spread_span` is now `cross_difficulty: null`.
*Ceiling.* `value_at_risk` tier 1 is now `MN(covered_value, RND(covered_value × MX(0,
DAYS(claim_anchor_date, expiry_date)) / span_days, 2))`, and the rule carries "and never more than
the value the plan covers".
Re-derived on **round 1's own two worked cases**:
- `Granite Ridge Four-Day Flex Pass`, 419.00, `Season Pass Protection Basic`, cover from the
  season's opening day, scans on the account, claim measured 2027-01-09 → value at risk **278.40**,
  **0.664×** the covered value. Round 1: 10,370.25, 24.75×.
- `Granite Ridge Midweek Pass`, 629.00, claim anchored on the day cover began → value at risk
  **629.00**, **1.000×** — exactly the covered value, not above it. Round 1: 875.90, 139%.
*Can any tier still exceed the value covered?* No, and this was checked three ways. By inspection:
tier 1 is clamped by `MN(covered_value, …)`; tier 2 is `MX(0.0, RND(covered_value −
day_use_deduction × scan_days, 2))`, which only subtracts; the fall-through is `covered_value`
itself. By sweep: four pass tiers (Four-Day Flex, Midweek, Local, Collective Elite) × four
cover-start/waiting-period configurations gave a worst `value_at_risk / covered_value` of
**0.6644**. And the ceiling is **load-bearing rather than dead code**: on a world where cover begins
before the season opens (`effective_date` 2026-11-01, `waiting_period_end_date` 2026-11-11) and the
claim is anchored on an accepted paper of 2026-11-03, the raw proportion is
`DAYS(2026-11-03, 2027-04-18) = 166` over `span_days = 149`, i.e. 1.114, and the ceiling clamps the
value at risk to exactly the covered value, 1149.00.

#### New red light introduced by the rework

**R2-RED-1 — `SOURCE-POLICY RED` (a base provision suppressed by an override whose replacement
does not replace it), charter-global. New in revision 2; a regression of ground revision 1 passed.**

- *Symptom.* The merged charter now pays a claim on a peril the plan's own `covered_perils` list
  does not contain. Round 1's merged charter refused it.
- *Root cause.* In closing OBS-4, `insure_ext_claim_settlement` added a second `overwrite` entry
  that names the wrong base sentence. It declares superseded base `insure_claim_assessment`'s
  *"A complete claim is assessed against the plan's list of covered events."* — the only prose
  carrier of the cover-list gate — and supplies as `replaced_by` a passage about **which share is
  taken**, which speaks to a different subject and reinstates nothing. The cover-list gate is
  therefore governed by nothing, and the only refusal the extended policy implements is
  `excluded_claim`, which tests `excluded_perils` alone. (OBS-4's actual subject — that the base
  picks the share from `claim_reason` alone where extended also requires an accepted paper — was
  already inside `overwrite[0]`'s superseded clause, *"The amount allowed is the plan's benefit
  share **for the event claimed on**…"*, so the prose half of OBS-4 needed no second entry.)
- *Evidence (the two passages, verbatim).*
  Base, `blueprint/products/insure.yaml` → `parameter_schema`, **not superseded by any overwrite and
  present verbatim in the extended file's base copy**: `covered_perils: "List of the events this
  plan pays out on."` For `Season Pass Protection Plus`, `covered_perils:
  ["medical_injury", "medical_illness", "job_loss"]`.
  Extended, `insure.extended.yaml` → `insure_ext_claim_settlement`:
  `excluded_claim: "1 if F('claim_reason') in P('excluded_perils') else 0"` and
  `result: "0.0 if excluded_claim == 1 else RND(MN(P('per_claim_cap_usd'), MN(benefit_left,
  gross_allowed)), 2)"`, with the share falling through to *"it is the plan's medical share in every
  other case"*.
  Base sentence 2 of `insure_claim_assessment`, also not superseded, presupposes the list the first
  sentence supplied: *"…an exclusion always beats a cover…"*.
- *Demonstrated consequence (same situation, two conclusions).* Five of the six plan tiers have
  perils in neither list. Take `Season Pass Protection Plus` with `claim_reason = bereavement`
  (a value of `insure_holdings.claim_reason`, of `insure_ledger.claim_reason` and of the
  `settle_protection_claim_ed51c2df` `claim_reason` enum), covered value 1879.00, an accepted claim
  form, no scans on the covered pass. Extended: `excluded_claim = 0`,
  `benefit_share_pct = medical_benefit_pct = 80.00`, `value_at_risk = 1879.00`, and the claim
  **pays 919.20**. Base: bereavement is not among the events this plan pays out on, so it **pays
  0.00**. The same holds for `mountain_closure` and `travel_disruption` on that tier, each paying
  919.20 where base pays nothing; perils in neither list exist on Basic, Plus, Premier, Trip
  Standard and Trip Elite.
- *Affected artifact and location.*
  `env/env_0004_ski_resort_operator/tasks/pass_protection_desk/insure.extended.yaml` →
  `insure_ext_claim_settlement` → `overwrite[1]` (`superseded_clause` / `replaced_by`), `rule`
  (which states no cover-list gate), `compute.excluded_claim` and `compute.result`.
- *Bears on.* Task 0 (`insure_ext_claim_settlement` is its root problem). Its consequence on task
  0's own world is demonstrated in `0.md` → `revision_2` → `policy_self_consistency`.
- *Relation to previous revisions.* New. Revision 1 recorded base sentence 1 as inherited and the
  merged semantics as refusing such a claim; revision 1's OBS-4 asked for the share conflict to be
  named, not for the cover-list gate to be removed.

#### Observations disposed of this round

| item | claimed | verdict |
| --- | --- | --- |
| OBS-1 | closed | **closed** — compute predicate now matches the sentence |
| OBS-2 | closed | **closed** — headline sentence and `result` now one reading; `account_unpaid` given its own basis |
| OBS-3 | closed | **closed** — sentence removed; and the second instance round 1 missed is now implemented as `excluded_claim` |
| OBS-4 | closed as far as base states it in prose | **NOT closed; the attempt is R2-RED-1.** The prose OBS-4 named was already covered by `overwrite[0]`; the entry added names a different sentence and suppresses a gate that was not in conflict |
| OBS-5 | closed | **closed** — no ordering word anywhere in `task_tools.py` |
| OBS-6 | answered with reasoning | **accepted** — the override is declared, and a fee sentence with no tool to raise it would recreate OBS-3 |
| OBS-7 | closed | **closed** — covered-value bound stated in the rule and in `baseline`, implemented in `new_covered_value` |
| OBS-8 | closed | **closed** — `presented_count` tiers carry the schedule conjunct; the whole-premium multiple is unreachable |
| OBS-9 | closed | **closed** — both colliding tiers now sit behind `excluded_claim`, verified by computation |
| OBS-10 | closed | **closed** — tier parameters de-prefixed, `operating_days_included` gone, every prefixed entry a real column |
| OBS-0.T0 | closed | **closed** — see `0.md` revision_2 |
| OBS-11.T0 | closed | **closed** — see `0.md` revision_2 |
| OBS-12.T1 | closed | **closed** — see `1.md` revision_2 |

#### New observation

- **OBS-13 (revision 2) — `assessed_from_paper` breaks ties by iteration order.**
  `LATEST('insure_ledger', 'insure_event_id', event_type='insure_document_receive',
  document_status='accepted')` orders on `event_date` and keeps the first row that strictly beats
  the running best, so where two accepted papers share the latest date the row returned is decided
  by dictionary iteration order rather than by the rule, whose sentence — *"The payout is recorded
  against the paper it was assessed from, which is the last paper accepted on the claim"* — names no
  tie-break. *Demonstrated consequence:* none on either task; task 0's three accepted papers fall on
  three distinct dates (2027-01-06, 2027-01-07, 2027-01-09) and task 1 has no papers at all.
  Recorded as an observation. Location: `insure.extended.yaml` `insure_ext_claim_settlement` →
  `compute.assessed_from_paper` and the rule sentence it cites.

## closing_checklist (revision 2)

Written after both tasks reached a frozen `source_derivation_frozen (revision 2)` and a
`source_gt_comparison (revision 2)`.

- **Files and revisions.** `_difficulty.md`, `0.md`, `1.md` against `tasks/0.json` and
  `tasks/1.json`. Revision 1 is preserved verbatim in all three; revision 2 is appended below it and
  nothing in revision 1 was rewritten to accommodate what the rework or the round-1 reveal made
  known. Both round-2 comparison sections carry PASS.
- **Scopes.** Unchanged and re-checked against the reworked `charter_scope`: task 0 =
  {`insure_ext_amendment_reprice`, `insure_ext_claim_settlement`}, task 1 =
  {`insure_ext_giveup_charge`, `insure_ext_premium_presentation`, `insure_ext_giveup_settlement`}.
  Pairwise disjoint, union all five, each spanning a whole tree.
- **Task tools and uuid8s.** The same five tools, the same five owners, the same five uuid8s
  (`50d33fe4`, `ed51c2df`, `8deb00b0`, `59dbe3e5`, `9d16ef5f`) — distinct, unreused, not
  batch-derived. Only the docstrings changed, and only to remove ordering words.
- **Problem trees.** Unchanged: task 0 has 1 prerequisite problem and 1 `value_input` edge with the
  prerequisite resolved by an `owner="user"` tool; task 1 has 2 prerequisite problems, 2
  `value_input` edges and a root resolved by an `owner="user"` tool; both within 1–3 prerequisite
  problems, both meeting the max(n−1,1) floor, no cycle, and the difficulty's three edges still a
  DAG with no cross-task cycle. Every edge re-proved load-bearing by recomputation
  (0: 207.90 vs 547.42; 1: 0.00 and 35.43 vs 49.20), and task 1's two parallel edges re-proved
  commutative in both directions on the reworked charter.
- **Computations, baselines and factors.** Five computations, 25 declared factors, every ladder
  three pairwise-disjoint tiers stated in full in its own rule. Counts unchanged: 6/6/4/4/5 factors,
  each with ≥ 2 `parameter` and ≥ 1 `method`; ≥ 1 multi-source and ≥ 1 `cross_difficulty` factor per
  task. **All 25 re-tested by substitution and all 25 still bear weight** against an honest
  baseline. Every whole-computation baseline gives a definite non-gold number, and the one that was
  a world-independent constant is no longer: 122.14 / 919.20 / 35.00 / 11.26 / **13.77** (was 0.00).
- **Scored values.** Task 0: repricing **117.46 unchanged**, payout **541.60 → 547.42**, and the
  movement was re-derived independently and shown to be exactly `span_days` 150 → 149. Task 1:
  **13.77 / 81.06 / 49.20 all unchanged**, each re-derived binding by binding.
- **Gates re-run on the reworked form**, from the repository root against
  `env/env_0004_ski_resort_operator/tasks/pass_protection_desk`: `check_extended` EXTENDED OK ·
  `check_task_tools` TASK TOOL CONTRACT OK · `replay_tasks --check` REPLAY OK (0.json 10 acts,
  33/33; 1.json 12 acts, 25/25) · `check_solvability` SOLVABILITY OK · `check_compute` COMPUTE OK
  (branches 55 / 53, suite mean 54.00; steps 10 / 12) · `check_grounding` GROUNDING OK ·
  `check_cross_fire` SCOPE OK. `check_traceability` remains NOT OK with the same five misses — the
  hidden task-tool names — and `env/env_0004_ski_resort_operator/kb` still does not exist, so this is the
  unchanged pre-render state and not a finding.

### difficulty verdict (revision 2)

**The three revision-1 red lights are genuinely closed, each in the compute and not merely in the
wording, and each verified on revision 1's own worked case plus cases of this auditor's choosing:**

- **F-RED-1 CLOSED** — the free-look conjunct sits on **both** non-zero tiers of `minimum_kept`.
  Revision 1's case now gives 0.00 where it gave 22.52; a sweep over days 0, 5, 10, 14, 15, 20
  gives 0.00 throughout the period and 13.77 only after it; and the two leak paths this auditor
  tried (inside the free look with the holding cancelled, and on a flat-premium tier) both give 0.00.
- **F-RED-2 CLOSED** — the `payouts_standing == 0` conjunct sits on **both** non-zero tiers of
  `return_share`. Revision 1's case now returns nothing and leaves the whole 139.87 standing, which
  is base's conclusion; verified on 0, 1 and 2 payouts and on a `no_refund` tier.
- **F-RED-3 CLOSED, twice over** — the operating-day denominator is gone from the charter entirely
  and a `MN(covered_value, …)` ceiling stands behind it. Revision 1's two cases fall from 24.75× and
  139% of the covered value to 0.664× and exactly 1.000×; a sweep over four pass tiers × four
  cover-start configurations tops out at 0.6644; and the ceiling is load-bearing rather than dead
  code, clamping at exactly the covered value on a world where cover begins before the season opens.

**Nothing that revision 1 passed has regressed on either task's four relationships.** Both problem
trees, all five computations' factor structures, all 25 factor weights, both tasks' unique
solutions, the prerequisite graph, the action bindings, the uuid8s and the base copy were all
re-derived from scratch and all hold. Nine of revision 1's thirteen observations are closed, one
(OBS-6) is answered with reasoning this auditor accepts, and the three task-level ones are closed.

**But the difficulty still does not clear the source-layer audit, on two counts, both new:**

- **R2-RED-1 · `SOURCE-POLICY`** — closing OBS-4 named the wrong base sentence. The second
  `overwrite` entry on `insure_ext_claim_settlement` supersedes base's *"A complete claim is
  assessed against the plan's list of covered events."* and puts a passage about **shares** in its
  place, so the cover-list gate is now governed by nothing and the merged charter pays the medical
  share on a peril the plan's own `covered_perils` does not contain. Demonstrated on
  `Season Pass Protection Plus` with `claim_reason = bereavement`: extended pays 919.20, base pays
  nothing; five of six plan tiers have perils in neither list. Inert on both tasks' worlds.
- **R2-RED-2 · `SOURCE-CHAIN`** — task 0's `prerequisite_closure.edge_load_bearing[0]` asserts the
  value at risk falls to **763.32** when the prerequisite is skipped; recomputed on that same world
  it is **763.43**. The relationship it supports still holds — the edge genuinely bears weight,
  207.90 against 547.42 — so the defect is in the evidence, not the conclusion, and no scored value
  moves. Revision 1 checked this field value-against-value and found it correct; the rework moved
  the figure and mis-stated it.

Two new observations are recorded and are not grounds for rework: **OBS-13**
(`assessed_from_paper`'s `LATEST` has no tie-break, inert on both worlds) and **OBS-14** (two of
task 1's `factor_sensitivity[].tier_taken` strings still quote the pre-rework ladder wording, inert
on all four relationships).

No problem found here is attributed to a solving agent, and no fix is designed or arranged by this
audit.

---

# revision_3

Re-audit round 3. Revisions 1 and 2 above are preserved unaltered.

## charter_global_frozen (revision 3)

- auditor: same auditor; **not blind**, and says so.
- freeze time (this section): 2026-09-17, round 3. Written and saved to disk before any masked field
  of either reworked task file was read this round.
- **Re-derivation grounds.** Revision 2's charter-global sections were produced from
  `insure.extended.yaml` sha256:16 `15021b061f1b681f` and `task_tools.py` `21f93863911cf2f0`.
  Round 3's are **`c1f771c61dce6a38`** (moved) and `21f93863911cf2f0` (**unchanged**). One of the two
  has moved, so every charter-global section is **re-derived in full**. Where a conclusion rests only
  on the tool module — the uuid8s, the owners, the docstrings' silence about sequence — it is
  re-derived against a file that is byte-identical to the one revision 2 cleared, and that identity
  is recorded as the grounds. Masked task views: `tasks/0.json` `55176cc8d273c2db` and
  `tasks/1.json` `e157ea3f171501cb`, **both byte-identical to round 2**, so neither world moved.
  All four hashes re-computed off the rebuilt masked root and matching the brief.
- entry conditions: the coordinator's re-run gate snapshot came with the brief and is green
  throughout except the unchanged pre-render TRACEABILITY. Masked views rebuilt by the same
  mechanical whitelist. Complete.

### integrity of the earlier revisions

The brief reports that revision 2's OBS-4 paragraph was edited to point forward. **No such edit was
made, and no edit of any kind was made to this audit's files.** All three are byte-for-byte as this
auditor left them at the end of round 2: `_difficulty.md` 83002 bytes / 1051 lines, `0.md` 76421 /
980, `1.md` 78055 / 994, with mtimes of 19:34, 19:33 and 19:33 on 2026-09-17 — this auditor's own
writes — and no occurrence anywhere of "revision_3", "revision 3", "see revision" or any forward
pointer. Revision 2's two OBS-4 passages still read exactly as written:
*"**OBS-4 — NOT CLOSED; the attempted closure is itself the new red light.** See **R2-RED-1**."*
and the table row *"**NOT closed; the attempt is R2-RED-1.** …"*.

**That is the correct state and this auditor would not have accepted the edit had it been made.**
An earlier revision records what was true of the artifact at that revision, and revision 2's OBS-4
paragraph is an accurate record of the artifact as it then stood. The skill's rule — *"an old blind
answer must never be rewritten to accommodate new GT"* — applies with equal force to rewriting an
old finding to accommodate a later fix. The forward pointer belongs in revision 3, which is where it
is: **OBS-4 is now closed, by the withdrawal of the entry that R2-RED-1 was raised against; see
`### findings (revision 3)` below.** Revisions 1 and 2 stand as they were.

### base copy (re-checked)

`diff` of `insure.extended.yaml` lines 1–1170 against `blueprint/products/insure.yaml` is empty.
The base copy still has not been rewritten. `insure_claim_assessment`'s first sentence —
*"A complete claim is assessed against the plan's list of covered events."* — is present in it and
is **no longer named by any `overwrite` anywhere in the charter**, so it is inherited unmodified
again. This is the fact R2-RED-1 turned on.

### what the rework changed (full inventory)

Confined to one policy. `insure_ext_amendment_reprice`, `insure_ext_premium_presentation`,
`insure_ext_giveup_charge`, `insure_ext_giveup_settlement` and `task_tools.py` are unchanged.

| artifact | changed |
| --- | --- |
| `insure_ext_claim_settlement.overwrite` | **the second entry is withdrawn.** One entry remains, the original and legitimate one naming *"The amount allowed is the plan's benefit share for the event claimed on…"*. The charter now has 5 overwrite entries in total (was 6) |
| `insure_ext_claim_settlement.rule` | the closing sentences replaced. Was: *"A claim made on a peril the plan names as excluded is refused whatever this rule would otherwise work out, and nothing is paid on it."* Now: *"Nothing is paid on a claim made on a peril the plan does not cover, the events a plan pays out on being the ones its own list of covered perils names. A claim made on a peril the plan names as excluded is refused whatever this rule would otherwise work out, and nothing is paid on it, so that an exclusion beats a cover wherever a peril stands in both lists."* |
| `insure_ext_claim_settlement.rule` | the `assessed_from_paper` sentence expanded from *"…which is the last paper accepted on the claim"* to the four-limb sentence quoted under **OBS-13** below |
| `insure_ext_claim_settlement.compute` | new binding `peril_covered`; new binding `paper_for_peril`; `assessed_from_paper` rewritten as a fall-back over it; `result` guard widened from `excluded_claim == 1` to `(peril_covered == 0 or excluded_claim == 1)` |
| `insure_ext_claim_settlement.compute_basis` | `peril_covered` and `paper_for_peril` added; `excluded_claim`, `assessed_from_paper` and `result` re-quoted against the new sentences |

No `factors`, no `baseline`, no `prerequisite`, no `cross_category` and no `params` block changed
anywhere in the charter.

### policy_conflict_scan (re-derived)

Subject ownership, triggers, time anchors, terminal states, the cross-category read boundary and the
disjointness of the two task scopes are unchanged and were re-checked. **The conflict revision 2
recorded is gone**: `insure_claim_payment`'s extended owner no longer supersedes any base sentence
beyond the one it legitimately replaces, and the merged charter agrees with base on every
plan-tier × peril pair (the sweep is under `### findings (revision 3)` → R2-RED-1). No new
overlapping-subject conflict was introduced.

### rule_compute_equivalence (re-derived)

Swept in both directions over all five policies. Every quantity, window, filter, tier, branch,
cross-category read, acting base, grouping, cap/floor and rounding point still carries a
`compute_basis` quotation verbatim locatable in its own rule, and every `compute_basis` key is a
binding that exists in `compute`. The two new bindings are both properly based: `peril_covered` ←
*"Nothing is paid on a claim made on a peril the plan does not cover, the events a plan pays out on
being the ones its own list of covered perils names."*; `paper_for_peril` ← the first three limbs of
the expanded assessed-from sentence; `assessed_from_paper` ← its fourth limb. No rule sentence of
the charter now lacks a compute counterpart, and no compute binding invents a basis.

**The restored gate carries the gate rather than describing it.** *"Nothing is paid on a claim made
on a peril the plan does not cover"* is normative on its face — it states the outcome (nothing is
paid) under a stated condition (the peril is not one the plan covers) — and the trailing clause
*"the events a plan pays out on being the ones its own list of covered perils names"* fixes what
"does not cover" refers to, namely the tier's `covered_perils`. It is implemented by
`peril_covered` and consumed by `result`, which returns `0.0` when it is 0. A reader of that
sentence alone reaches "a claim on an uncovered peril pays nothing" without needing any other.

- **OBS-3's shape, re-checked charter-wide: still clean.** Every sentence of every extended rule has
  a binding behind it. One clause is worth recording and is **not** an instance of it — see OBS-15.

### action_binding_and_uuids (re-derived)

`task_tools.py` is byte-identical to the module revision 2 cleared
(`21f93863911cf2f00e627e798422b1b318e4910184aabeff29f03463afa0a10d`), which is the grounds for the
tool-side half. Re-derived against it and against the moved charter: the same five
`(target_tool, computes)` pairs, each claimed by exactly one policy; the same five uuid8s
`50d33fe4`, `ed51c2df`, `8deb00b0`, `59dbe3e5`, `9d16ef5f`, pairwise distinct, sharing no prefix or
tail, forming no sequence; no ordering word anywhere in the module; no docstring adding a
confirmation, review or wait outside its policy. PASS.

### prerequisite_graph and prerequisite_sentences (re-derived)

All three edges unchanged in every field and re-tested from scratch: each `policy_source` verbatim
in the blocked policy's own rule, `form: state` with no `fallback_reason`, an explicit ordering
connective, no tool name or token, `condition` neither strengthened nor weakened, `resolved_by` the
depended-on policy's own `target_tool` and still the only write that brings the waited-on state
about, `kind` matching `gate`, and none of the three sentences restated in the depended-on rule. The
graph is acyclic and crosses no task boundary. The rework added no cross-problem ordering language:
`insure_ext_claim_settlement`'s new sentences are about which perils pay and which paper a payout is
recorded against, neither of which orders two problems. PASS.

### override_declarations (re-derived, sentence by sentence)

Blocks A, C, D, E are unchanged from revision 2 and were re-swept: **all PASS**, with A3 followed,
C2 followed, D2 obeyed and E5 obeyed as revision 2 recorded.

**B — `insure_ext_claim_settlement`: now PASS.** The single remaining `overwrite` entry names
*"The amount allowed is the plan's benefit share for the event claimed on, taken of the covered
value, less the plan's excess, and then brought down to the plan's per-claim cap; it is never below
zero and never more than the benefit left on the plan."* and replaces it with the value-at-risk
formulation, restoring the cap and the benefit-left ceiling later in the extended rule. Every other
sentence of `insure_claim_assessment` is inherited unmodified, including B-sentence-1
(*"A complete claim is assessed against the plan's list of covered events."*) and B2
(*"A claim made on an event the plan excludes is refused whatever the circumstances, and an exclusion
always beats a cover…"*), and the extended rule now implements both rather than displacing either.
B3–B8 inherited as before. **OBS-4 is closed by this withdrawal**: the base `formula` block that
OBS-4 named is the implementation of the prose sentence inside the remaining entry's superseded
clause, so no second entry is owed, and none is now claimed.

### factor_ladders (re-derived)

Unchanged in every respect from revision 2 — no `factors` block anywhere in the charter moved.
6 / 6 / 4 / 4 / 5 factors; 4+2, 3+3, 3+1, 3+1, 2+3 `parameter`/`method`; three pairwise-disjoint
tiers each, every tier stated in its own rule with its condition and its value or method and
implemented as a branch of its `decides` binding; ≥ 1 multi-source and ≥ 1 `cross_difficulty` factor
per task; labels honest. Whether each bears weight is re-proved per task in `0.md` and `1.md`.

OBS-9's closure is unaffected and is now slightly better grounded: the `peril_share` collisions on
`Season Pass Protection Basic` and `Collective Trip Protection Standard` sit behind **two** guards
rather than one, since `job_loss` and `relocation` are absent from those tiers' `covered_perils` as
well as present in their `excluded_perils`.

### findings (revision 3)

#### Dispositions of the revision-2 findings

**R2-RED-1 — CLOSED, at the source rather than by rewording, and confirmed by this auditor's own
sweep over the whole domain.**
Three things had to be true and all three are:
1. *The wrong entry is withdrawn.* `insure_ext_claim_settlement.overwrite` now holds **one** entry,
   the legitimate one. The charter has 5 overwrite entries where revision 2 had 6. Base's
   *"A complete claim is assessed against the plan's list of covered events."* is named by nothing
   and is inherited unmodified — verified by `diff` against the blueprint and by searching every
   `superseded_clause` in the file.
2. *The gate is restored in the policy's own rule, carrying rather than describing.* The rule now
   states *"Nothing is paid on a claim made on a peril the plan does not cover, the events a plan
   pays out on being the ones its own list of covered perils names."* — normative on its face, and
   `compute_basis.peril_covered` cites exactly it.
3. *The compute implements it.* `peril_covered: "1 if F('claim_reason') in P('covered_perils') else
   0"` stands beside `excluded_claim`, and `result: "0.0 if (peril_covered == 0 or excluded_claim ==
   1) else RND(MN(P('per_claim_cap_usd'), MN(benefit_left, gross_allowed)), 2)"`.

*The sweep, run by this auditor rather than taken on the author's count.* All six plan tiers × all
seven peril values of `insure_holdings.claim_reason` = **42 pairs**, each evaluated by running the
extended compute on a world built from task 0's seed with the tier and the peril substituted, the
covered value clamped into that tier's band and the scans removed so the value at risk is the whole
covered value, and compared against base's conclusion (pays iff the peril is in `covered_perils` and
not in `excluded_perils`). Result: **42 pairs swept, 0 disagreements.** The count of perils standing
in neither list is **11**, which matches the author's figure exactly; every one of the eleven now
pays 0.00 under extended, as base requires. Revision 2's worked case is among them —
`Season Pass Protection Plus` with `claim_reason = bereavement` now pays **0.00** where revision 2
paid 919.20.

**R2-RED-2 — CLOSED, and closed at the source rather than by transcription.**
The figure is re-derived here independently, by replaying task 0 with the prerequisite write skipped
on this auditor's own evaluator: `covered_value = 1149.00`, `claim_anchor_date = 2027-01-09`,
`span_days = 149`, `DAYS(2027-01-09, 2027-04-18) = 99`,
`value_at_risk = MN(1149.00, RND(1149.00 × 99 / 149, 2)) = **763.43**`,
`gross_allowed = **207.90**`, `result = **207.90**`, against 547.42 with the write performed — a gap
of **339.52**. The three surrounding figures are unchanged and correct. Whether GT now carries
763.43 is compared item by item in `0.md` → `source_gt_comparison (revision 3)`.

**OBS-13 — CLOSED, and no limb of the new sentence is dead.**
The rule now reads: *"The payout is recorded against the paper it was assessed from, which is the
last paper accepted on the claim that evidences the peril claimed on — the letter from the former
employer on a claim made on loss of employment, the proof of a permanent move on a claim made on a
permanent move, and the doctor's certificate in every other case — and where two such papers were
accepted on the same day it is the first of them the record holds; where the claim carries no
accepted paper of that kind at all, it is the last paper accepted on the claim."* It is implemented
by `paper_for_peril` (the three-way peril→paper selection, each limb a `LATEST` over that document
type) and `assessed_from_paper` (the fall-back).

Each limb was exercised on a constructed world and each resolves to exactly one entry:

| limb | world | resolves to |
| --- | --- | --- |
| peril → employer letter | `job_loss`, accepted claim form + accepted employer letter | the employer letter |
| peril → proof of a permanent move | `relocation`, accepted claim form + accepted proof | the proof |
| peril → doctor's certificate | `medical_injury`, accepted claim form + accepted certificate | the certificate |
| latest of several of that kind | two accepted employer letters, 2027-01-05 and 2027-01-09 | the 2027-01-09 one |
| **same-day tie** | two accepted employer letters both 2027-01-09 | **the first the record holds** |
| **no paper of that kind** | `job_loss`, accepted claim form + accepted certificate, no employer letter | the last paper accepted on the claim |

No limb is dead and none is ambiguous. The same-day limb is the one that needed checking hardest,
and it behaves as written: `LATEST` keeps the first row that strictly beats the running best, so
among rows sharing the latest date it returns the first the record holds, which is what the sentence
now says. The tie-break is therefore determinate for a reader who reads the ledger in the order the
finder returns it, where revision 2's wording left it unstated.
One residual edge, recorded here rather than as a finding because base forecloses it and it has no
consequence: where a claim carries **no** accepted paper at all, the fourth limb has nothing to fall
back on and `assessed_from_paper` is `None`. Base `insure_claim_intake` makes the collective's own
record of completeness the gate on assessment (`insure_holdings.documents_complete`), so a payout on
a claim with no accepted paper does not arise, and neither task reaches it.

**OBS-14** is a per-task fact about `computations[].factor_sensitivity[].tier_taken` and is disposed
of in `1.md` → `revision_3`, where all 25 strings across both tasks are checked against their
factor's current ladder.

**OBS-6** is left as it is, per revision 2's acceptance. Nothing this round bears on it.

#### New observation

- **OBS-15 (revision 3) — `excluded_claim` can no longer decide any outcome the charter admits, and
  the clause that motivates it describes a configuration no tier has.**
  With `peril_covered` now guarding `result`, `excluded_claim` changes the outcome only where a
  peril stands in a tier's `excluded_perils` **and** in its `covered_perils`. Checked across all six
  tiers: **no tier has any peril in both lists**, so `excluded_claim == 1` implies
  `peril_covered == 0` on every world, and the `or excluded_claim == 1` disjunct never alters
  `result`. The rule's trailing clause *"so that an exclusion beats a cover wherever a peril stands
  in both lists"* accordingly names a configuration the charter's own tier tables never produce.
  *Demonstrated consequence:* **none.** This is deliberately **not** recorded as the OBS-3
  empty-promise shape, and not as a red light, for two reasons. The sentence is not unimplemented —
  `excluded_claim` exists, is based on it, and feeds `result`. And it is the faithful implementation
  of a **base** sentence that is inherited unmodified, `insure_claim_assessment`'s *"A claim made on
  an event the plan excludes is refused whatever the circumstances, and an exclusion always beats a
  cover, so a plan that covers loss of employment but excludes a voluntary resignation refuses a
  claim on a resignation."* Honouring an inherited base provision that the current tier tables
  happen never to exercise is correct behaviour, not a defect; it is recorded only because the
  coordinator asked for dead limbs and this is the nearest thing to one.
  *Location:* `insure.extended.yaml` → `insure_ext_claim_settlement` → `rule` (closing sentence),
  `compute.excluded_claim`, `compute.result`.

## closing_checklist (revision 3)

Written after both tasks reached a frozen `source_derivation_frozen (revision 3)` and a
`source_gt_comparison (revision 3)` carrying PASS.

- **Files and revisions.** `_difficulty.md`, `0.md`, `1.md` against `tasks/0.json` and
  `tasks/1.json`. Revisions 1 and 2 are preserved verbatim in all three — verified by byte size,
  line count and mtime before anything was appended, and no forward pointer or other edit was found
  in either (see `### integrity of the earlier revisions`). Revision 3 is appended below them. All
  three round-3 comparison sections carry PASS.
- **Scopes.** Unchanged: task 0 = {`insure_ext_amendment_reprice`, `insure_ext_claim_settlement`},
  task 1 = {`insure_ext_giveup_charge`, `insure_ext_premium_presentation`,
  `insure_ext_giveup_settlement`}. Pairwise disjoint, union all five, each spanning a whole tree.
- **Task tools and uuid8s.** `task_tools.py` is byte-identical to the module cleared in revision 2:
  five tools, five owners, five distinct uuid8s, no ordering word anywhere.
- **Problem trees.** Unchanged and re-walked: task 0, 1 prerequisite problem, 1 `value_input` edge,
  the prerequisite the customer's own write; task 1, 2 prerequisite problems, 2 `value_input` edges,
  the root the customer's own write; both within 1–3, both meeting the max(n−1,1) floor, no cycle,
  the difficulty's three edges still a DAG. Every edge re-proved load-bearing
  (0: 207.90 vs 547.42; 1: 0.00 and 35.43 vs 49.20) and task 1's parallel edges re-proved
  commutative in both directions.
- **Computations, baselines and factors.** No `factors` or `baseline` block moved this round.
  25 declared factors, every ladder three pairwise-disjoint tiers stated in full in its own rule;
  counts 6/6/4/4/5 with ≥ 2 `parameter` and ≥ 1 `method` each; ≥ 1 multi-source and ≥ 1
  `cross_difficulty` per task. **All 25 re-tested by substitution and all 25 still bear weight.**
  Whole-computation baselines 122.14 / 919.20 / 35.00 / 11.26 / 13.77, each definite and non-gold.
- **Scored values.** **None moved.** Task 0: 117.46 and 547.42. Task 1: 13.77, 81.06 and 49.20.
  All five re-derived binding by binding on this auditor's own evaluator.
- **Gates re-run on the reworked form**: `check_extended` EXTENDED OK · `check_task_tools` TASK TOOL
  CONTRACT OK · `replay_tasks --check` REPLAY OK (33/33 and 25/25) · `check_solvability`
  SOLVABILITY OK · `check_compute` COMPUTE OK · `check_grounding` GROUNDING OK · `check_cross_fire`
  SCOPE OK. `check_traceability` remains NOT OK with the same five misses — the hidden task-tool
  names — and `env/env_0004_ski_resort_operator/kb` still does not exist, so this is the unchanged pre-render
  state and not a finding.

### difficulty verdict (revision 3)

**Both revision-2 findings are genuinely closed, and both were verified by running the check the
author's claim invited rather than by accepting its count.**

- **R2-RED-1 CLOSED.** The offending `overwrite` entry is withdrawn (the charter now carries 5
  entries, not 6), base's *"A complete claim is assessed against the plan's list of covered
  events."* is named by nothing and inherited unmodified, the gate is restored in the policy's own
  rule by a sentence that **carries** it — *"Nothing is paid on a claim made on a peril the plan
  does not cover…"* — and `peril_covered` stands beside `excluded_claim` in `result`. This
  auditor's own sweep of **all six plan tiers × all seven perils = 42 pairs** found **0
  disagreements** with base, and **11** perils standing in neither list, matching the author's
  figure. Revision 2's worked case, `Season Pass Protection Plus` with `bereavement`, now pays
  **0.00** where it paid 919.20.
- **R2-RED-2 CLOSED.** GT now carries **763.43**, which is what this auditor's own replay of task 0
  with the prerequisite write skipped yields; the surrounding figures (1248.46, 207.90, 547.42,
  339.52) are unchanged and correct.
- **OBS-13 CLOSED.** The expanded sentence resolves to exactly one entry on task 0 and **no limb is
  dead**: all four — peril→paper for each of the three perils, latest of several, the same-day
  tie-break, and the fall-back where no paper of that kind was accepted — were exercised on
  constructed worlds and each returns a single entry.
- **OBS-14 CLOSED.** 25 of 25 `tier_taken` strings across both tasks match a tier of their factor's
  current ladder.
- **OBS-6** left as it is, per revision 2's acceptance.

**Nothing regressed.** Rounds 1 and 2's closures were re-verified on the round-3 charter rather than
assumed: F-RED-1 gives 0.00 throughout the free look and 13.77 after it; F-RED-2 returns nothing
whenever a payout stands; F-RED-3's ceiling holds at a worst ratio of 0.6644 over a 20-case sweep
and still binds where cover begins before the season opens. All four per-task relationships PASS on
both tasks, and all five scored values are unchanged.

**Two observations are recorded this round and neither is grounds for rework:**

- **OBS-15** — `excluded_claim` can no longer decide any outcome the charter admits, since no tier
  has a peril in both its lists. It is nevertheless the faithful implementation of an inherited base
  sentence, is properly based and consumed, and is therefore not the empty-promise shape.
- **OBS-16** — the figure sweep's **completeness** claim is confirmed (this auditor's own sweep over
  the same four field families found **0 unaccounted-for figures** across both tasks, 35 distinct
  decimals on task 0 and 24 on task 1, every one recomputing exactly), but its **classification**
  claim undercounts: the author names one exception per task, where three on task 0 (339.52, 42.77,
  873.92) and one on task 1 (17.50, beside the integer 69 the author names) are not any single
  binding value, tier parameter or seed field. No figure is wrong; only the count of exceptions is.

**With no red light outstanding at the charter or in either task, this difficulty now clears the
source-layer audit: policy self-consistency PASS + problem tree holds PASS + factors bear weight
PASS + unique solution PASS, on both tasks and on the shared charter.** The one gate that is not
green, TRACEABILITY, is the declared pre-render state and is outside this audit's remit. No problem
found across the three rounds was attributed to a solving agent, and this audit designed and
arranged no fix.
