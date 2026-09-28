# Policy-task audit — companion_certificates_and_passes / charter-global

## charter_global_frozen

- auditor: independent audit agent (erl-task-policy-audit), not the author of the audited artifacts
- freeze time: 2026-09-24T17:29Z (written before any task's GT was revealed; nothing in this section derives from a revealed GT)
- frozen inputs (sha256, re-checked against the brief before reading):
  - `tasks/companion_certificates_and_passes/companion.extended.yaml` = `389c47e1d766ffc52ee89e17d7dfeff50b4cfe50be526850897173faafe1bb6c`
  - `tasks/companion_certificates_and_passes/task_tools.py` = `cf586a5bd03c8f476df9251818cd3b0723d97a371715432597228e1571d0aeb1`
- also read: `blueprint/blueprint.yaml`, `blueprint/products/companion.yaml`, `blueprint/share_tools.py`, `blueprint/db_schema.json`, `erlbench/scoring.py`, `erlbench/db.py` (hash), `erlbench/determinism.py` (make_id), and the DSL evaluator `skills/erl-task-instantiate/scripts/check_compute.py` lines 225-395 (semantics of LATEST / COUNT within_months / DAYS / MONTHS / RND / CFIELD / XSUM / XCOUNT) — read only, nothing modified.
- permitted task fields: the coordinator's masked views (`task_index`, `frozen_time`, `user_scenario`, `initial_state`), sha256 `2658c1b6…` (task 0) and `81310981…` (task 1).
- masked and not read before the freeze: `evaluation_criteria`, `computations`, `charter_scope`, `required_documents`, `design_rationale`, `solvability_contract`, `prerequisite_closure`, `db_closure*`; `tasks/*.json`; any worklog; the sibling audit directory `audits/policy_task/flight_credits_and_vouchers/` (listed by `ls` only, never opened).
- entry conditions (Step 0): gate snapshot supplied in the brief — check_extended, check_task_tools, replay_tasks, check_solvability, check_compute, check_grounding, check_cross_fire all rc=0 (check_traceability deferred to render by design); masked views supplied with hashes. Complete.

Base-copy check: `diff <(sed -n '1,1388p' companion.extended.yaml) blueprint/products/companion.yaml` differs only in the trailing banner comment lines 1385-1388 — the base section is verbatim.

The eight extended policies (id → target tool, owner, declared prerequisites):

| # | policy | target_tool | owner | prerequisite edges |
|---|---|---|---|---|
| P1 | companion_ext_cancelled_fare_refund | refund_companion_fare_charge_1d800070 | agent | [] |
| P2 | companion_ext_cancelled_surcharge_refund | refund_companion_hawaii_surcharge_2c74daac | agent | P1 (value_input, state) |
| P3 | companion_ext_cancelled_taxes_refund | refund_companion_taxes_and_fees_22c15e93 | agent | P1, P2 (value_input, state) |
| P4 | companion_ext_voluntary_reinstatement_fee | pay_companion_reinstatement_fee_0c05ba56 | user | P3 (value_input, state) |
| P5 | companion_ext_booking_companion_fare | pay_companion_fare_charge_130546ae | user | [] |
| P6 | companion_ext_booking_phone_fee | pay_companion_phone_booking_fee_ff06513e | user | P8 (value_input, state) |
| P7 | companion_ext_booking_taxes_and_fees | pay_companion_taxes_and_fees_93ccd8f8 | user | P5, P6 (value_input, state) |
| P8 | companion_ext_crestline_cancel_phone_fee_refund | refund_companion_phone_booking_fee_90a9c390 | agent | [] |

### policy_conflict_scan

- Subjects: P1/P2/P3/P8 all write `companion_fare_refund`, but each writes a distinct `charge_component` (companion_fare / hawaii_surcharge / taxes_and_fees / phone_booking_fee — hard-coded in each tool body) and names a distinct charge through `reversed_entry_id`; P4/P5/P6/P7 all write `companion_fare_charge`, each with a distinct hard-coded component (reinstatement_fee / companion_fare / phone_booking_fee / taxes_and_fees). No two policies decide the same quantity.
- Triggers: all `state_due`. P1-P4 fire on a cancelled booking (P4 only on a voluntary one: "A trip returned ... by a voluntary cancellation carries a reinstatement fee"; base: Crestline cancellation reinstated "without fee"); P5-P7 on a new booking; P8 on a Crestline-cancelled booking. P8's rule "A voluntary cancellation never returns a phone booking fee" is compatible with P6's "a fee still standing from an earlier booking covers the new fee".
- Eligibility / time anchors: all eight inherit the base `reinstate_once`, `refund_once`, `book_active`, `book_by`, `holder_membership_open` gates unchanged; no extended rule weakens one. Clock is `frozen_time` everywhere; "last 12 months counted back from the handling date" is implemented as `MONTHS(d, NOW) in [0,12)` uniformly.
- Cross-category read boundaries: only reads (loyalty holdings/activity, club holdings, ticket holdings); no extended policy writes outside `companion_ledger`.
- Terminal states: each tool creates exactly one ledger row; no status transitions are written by any task tool, so no two policies disagree on a terminal status.
- Scope: the eight policies split into two closed trees — {P1,P2,P3,P4} (cancellation settlement) and {P5,P6,P7,P8} (new-booking charges) — with no edge between the two groups. M=2, so two trees covering 4+4 policies are mutually exclusive and jointly complete *if* the tasks claim them that way (confirmed per task from the world, see 0.md / 1.md; `charter_scope` itself masked).
- Conclusion: no conflicting conclusions on overlapping subjects.

### rule_compute_equivalence

Swept each `compute` binding against its `compute_basis` quotation and each rule sentence back against compute.

- P1: `fare_charged` (LATEST companion_fare charge) ← "the amount of the most recent companion fare charge on the certificate"; `cancel_ground`/`cancel_date` ← "read from the most recent trip reinstatement"; `cancelled_travel_date` ← "the travel date of the most recent companion booking"; `notice_days = DAYS(...)` ← "reinstatement date excluded and the travel date included" (DAYS(a,b)=b−a satisfies it); `retention_core` three tiers verbatim incl. "rounded to the cent"; `bookings_on_certificate` COUNT redeem ← "counting every companion booking entry"; `membership_months` MONTHS ← "whole calendar months"; `qualifying_dollars_12m` XSUM mqd_accrual within 12 ← rule; `final_retention` single RND ← "rounded to the cent once at that point"; `result` MX(0, …) ← "never below zero". Equivalent.
- P2: all bindings quoted; `fare_refunded … or 0` supplies 0 when no fare refund exists — the rule is silent on that case (no-refund makes the share 0 and the proportional tier applies); not reachable in either task's world after its prerequisite. Equivalent otherwise.
- P3: same-entry-date conditions on surcharge charge and surcharge refund quoted; `refunds_12m` counts every `companion_fare_refund` component ← "the refund entries already recorded on the certificate"; processing tiers conjunctive with `voluntary_cancellation` ← rule. Equivalent.
- P4: `refunded_value` ← quoted; `voluntary_reinstatements` ← "the one being settled included"; `fee_core` three tiers; `booking_time_left_days = DAYS(latest reinstatement, F(book_by_date))` ← "reinstatement date excluded and the book-by date included"; relief conjunction (tier AND flights) ← rule; credits ← rule. Equivalent.
- P5: booking-ahead tiers, activity conjunctions ("who does not reach both of those higher marks" = else-branch), lounge, Crestline-reinstatement count, holder fare via `CFIELD('ticket','base_fare', status='ticketed', payment_form='credit_card') or 0` ← "a lower fare or no such ticket gives nothing". Equivalent.
- P6: `days_since_return … else window+1` ← "including one with no reinstatement on the product"; raise tiers ("the booking being charged included"); raw fee order (raise, then waiver, less credit, floor, round) ← rule; `standing_phone_fees` and `MN(raw, standing)` ← "covers the new fee up to its own amount". Equivalent.
- P7: three tax-base tiers verbatim (Hawaii tier ×hawaii_tax_share on fare+surcharge; call-center tier on fare + most recent phone fee; else fare alone); cardholder conjunction with `F('issue_source')`; rebooking count ("booking being charged included"); flyer count. Equivalent.
- P8: standing fee; claim-window tiers with the pro-rating formula verbatim; three uplifts summed once; `MN(standing, …)` ← "never more than the phone booking fees still standing". Equivalent.
- Every `factors[].ladder` tier is a sentence of its rule and a branch of its `decides` binding, and vice versa (checked for all 34 factors). No tier lives only in compute.
- **Rounding mode (finding F1 below):** every rule says only "rounded to the cent"; no rule or `compute_basis` names a rounding mode. `compute` implements it as `RND = round(float(x), 2)` (binary float, not half-up on exact decimal ties). The only rounding mode published anywhere on the policy/tool surface is in every task tool's `amount` Arg: "rounded to 2 decimal places (cents), rounding half up". On an exact half-cent intermediate the two disagree by one cent.

### action_binding_and_uuids

- `(target_tool, computes=amount)` pairs: eight distinct tools, one per policy; no tool claimed twice. Each docstring describes one business action consistent with its policy subject; owners match the rules ("the holder pays in person" → user for P4-P7; "refunded ... by the companion desk" → agent for P1-P3, P8).
- Tool bodies (`task_tools.py`): each only computes `rid`, rounds `amount`, looks up the holding and (refunds) the named charge for its ticket number, and creates one ledger row. No branch refuses, errors or hints on a missing prerequisite; no aggregation of history. The module docstring states this.
- Docstrings name no other task tool and state no position in a write sequence. Each Arg contains "as returned by the … lookup before the call" — an ordering word referring to the read lookup that supplies the id, not to another write (observation O4).
- uuid8s: 0c05ba56, 1d800070, 2c74daac, 22c15e93, 130546ae, ff06513e, 93ccd8f8, 90a9c390 — no shared prefix/suffix, no sequence, no adjacent values; independently generated on their face.

### prerequisite_graph

- `prerequisite` filled on all eight (`[]` on P1, P5, P8).
- Edges: P2→P1, P3→P1, P3→P2, P4→P3, P6→P8, P7→P5, P7→P6. Every `problem` is an extended policy id in this file; none points at a base policy or itself. Graph is acyclic (two DAGs: P1→P2→P3→P4 with P1→P3; P8→P6→P7 with P5→P7).
- Every `policy_source` is verbatim in the blocked policy's own `rule` (checked by string match for all seven).
- `form: state` on all seven; no `fallback_reason` present, none required.
- `resolved_by` is the depended-on policy's `target_tool` on all seven; each resolving write creates exactly the ledger row the gate names (component + reversed/linked charge), which changes a LATEST/SUM read in the blocked compute — so `kind: value_input` is honest and `gate` names an existing binding (`fare_refunded`, `fare_refunded_for_tax`, `surcharge_refunded_for_tax`, `refunded_value`, `standing_phone_fees`, `fare_posted_for_tax`, `phone_posted_for_tax`) on all seven.
- `condition` vs sentence: three conditions carry a date qualifier the sentence does not (observation O1). No authoring-viewpoint wording ("in this task", "at the opening") in any `prerequisite` field.

### prerequisite_sentences

For each edge: four-point test (ordering connective / record-visible state in table words / no tool, id or snake_case / strength), the single write that brings the state about, and the reader's derivation.

| edge | sentence (own rule) | connective | state named | single resolving write |
|---|---|---|---|---|
| P2→P1 | "The refund of a cancelled booking's Hawaii surcharge is fixed only after the certificate's ledger carries the refund of that booking's companion fare." | only after | ledger carries a companion fare refund of that booking | the companion-fare refund write (P1's rule: "refunded ... in one refund entry that names that companion fare charge"); no other tool writes component companion_fare refunds |
| P3→P1 | "The taxes-and-fees refund of a cancelled booking is not worked out until the certificate's ledger carries the refund of that booking's companion fare." | not until | same | P1's write |
| P3→P2 | "For a booking that carried a Hawaii surcharge, the taxes-and-fees refund is not worked out until the certificate's ledger also carries the refund of that surcharge." | not until | ledger carries the surcharge refund (scoped to surcharge bookings, closed set named by kind) | P2's write |
| P4→P3 | "The reinstatement fee for a voluntary cancellation is not fixed until the certificate's ledger carries the refund of the cancelled booking's taxes and fees." | not until | ledger carries the taxes-and-fees refund of that booking | P3's write |
| P6→P8 | "The phone booking fee of a new booking is fixed only after the certificate's ledger carries the phone booking fee refund owed on every booking of that certificate that Crestline cancelled." | only after | ledger carries the owed phone fee refund on each Crestline-cancelled booking | P8's write (the only phone_booking_fee refund writer; "owed" is decided by P8's own rule) |
| P7→P5 | "The taxes and fees of a companion booking are fixed only after the certificate's ledger carries that booking's companion fare charge." | only after | ledger carries that booking's companion fare charge | P5's write |
| P7→P6 | "For a booking made through the reservations call center, the taxes and fees are not worked out until the certificate's ledger also carries that booking's phone booking fee charge." | not until | ledger carries that booking's phone fee charge (scoped to call-center bookings) | P6's write (P6's rule: "a fee covered in full is still recorded, at zero", so the state is reachable even at 0) |

- None of the sentences names a tool, policy id, snake_case token or row id. Each depended-on rule carries its own rule and does not restate the blocking sentence. No blocked rule states a second wording of its dependency.
- Derivation (single reading each): a reader of P4 learns its fee waits on "the refund of the cancelled booking's taxes and fees"; the only rule that refunds taxes and fees is P3; P3 waits on the companion fare refund (only P1 refunds it) and, for a Hawaii booking, on the surcharge refund (only P2); P2 waits on the fare refund (P1). Likewise P7 → P5 (companion fare charge) and P6 (phone fee charge); P6 → P8 (phone fee refund on Crestline-cancelled bookings). Each hop has exactly one candidate write.
- Undeclared cross-problem orders in extended rules: none found. Base rules: `companion_booking_rules` "A pass must have a designated_companion_name before any booking when designation_required is true" states a cross-problem order (designation → booking); no declared edge rests on it and neither tree involves a pass → observation O3.

### override_declarations

Sentence-by-sentence against each `base_policy_refs` entry (quantity that is scored = the `amount` of the written row).

- `companion_refund_controls` (refs of P1, P2, P3, P8): "Each charge entry can be refunded at most once" — followed; "a refund equals the amount of the charge it names" — replaced, declared in all four `overwrite`s; "A refund is made only for a companion ticket that was cancelled or whose charge was made in error; a flown companion trip is never refunded" — followed.
- `companion_cancellation` (refs of P1-P4, P5-P8 partly): cancelled-with-holder, cutoff, keeps-book_by, Crestline-cancellation reinstatement "without fee", reinstate-once, used→active — followed. "A voluntary reinstatement carries reinstatement_fee_usd, charged as its own charge entry" — replaced by P4, declared. "On every cancellation the companion fare and taxes are refunded in the companion_fare_refund_form, one refund entry per charge entry" — form and one-entry-per-charge followed; its amount reading ("are refunded") is carried by the declared refund_controls clause (observation O2). "phone booking fees are not refunded" — replaced by P8, declared; P8's merged semantics keep "A voluntary cancellation never returns a phone booking fee".
- `companion_booking_rules` (refs of P4-P7): "The holder pays companion_base_fare_usd" — replaced by P5, declared; "the companion's taxes and fees when companion_pays_taxes is true" — replaced by P7, declared; "and phone_booking_fee_usd when booked through the call center, each as its own charge entry" — replaced by P6, declared; hawaii_surcharge_usd sentence — not governed by any extended policy (no surcharge-charge policy), followed; all eligibility sentences followed.
- `companion_designation` (refs of P4-P7): designation-change fee — not a quantity of any extended policy; followed.
- Disguised forms: no anonymous intermediate factor found (P6's standing-fee coverage is inside the declared `replaced_by`); no 0/1 multiplier on a base-fixed amount beyond P8's declared claim-window zero, which coincides with base "not refunded"; no dropped base branch. No rule calls the base output a "wrong value".
- Conclusion: every conflict is declared; merged semantics unique per quantity, subject to F1 (rounding mode) which is not a base/extended conflict.

### factor_ladders

34 factors in 8 policies. Per policy (label counts parameter/method; MS = multi-source tier beyond fall-through; XD = cross_difficulty):

| policy | factors (label) | P/M | MS factor | XD factors |
|---|---|---|---|---|
| P1 | fare_cancellation_retention (method: 30% of fare / flat $40 / none), fare_retention_booking_count (param 1.25/1.1/1), fare_retention_membership_age_waiver (param 40/20/0), fare_retention_qualifying_spend_waiver (param 30/15/0) | 3/1 | retention: voluntary ground (reinstatement row) AND notice days (reinstatement date + booking travel date) | tenure (loyalty), spend (loyalty) |
| P2 | surcharge_fare_share_method (method: proportional / less $25 / full), surcharge_repeat_refunds (param 1.5/1.2/1), surcharge_status_waiver (param 50/25/0), surcharge_advance_planning_waiver (param 20/10/0) | 3/1 | share = latest fare refund ÷ latest fare charge (two records, one condition); status tiers are disjunctions over one field | status (loyalty) |
| P3 | taxes_fare_side_share_method (method: proportional / less 7.5% tax on unrefunded / full), taxes_refund_processing_charge (param $9/$6/0), taxes_processing_lounge_waiver (param 50/25/0), taxes_processing_card_waiver (param 40/20/0) | 3/1 | processing: voluntary ground AND refund-entry count | lounge (club), card (loyalty) |
| P4 | reinstatement_fee_repeat_method (method: fee×count / 25% of value refunded / standard fee), reinstatement_fee_booking_time_left (param 0.5/0.75/1), reinstatement_fee_frequent_flyer_relief (param 50/25/0), reinstatement_fee_lounge_credit (param $15/$8/0), reinstatement_fee_card_credit (param $20/$10/0) | 4/1 | relief: Summit tier (loyalty_holdings) AND flight-accrual count (loyalty_activity) | relief (loyalty), lounge (club), card (loyalty) |
| P5 | companion_fare_booking_ahead_method (method: +$20 / ×0.9 / as published), companion_fare_activity_discount (param 12/6/0), companion_fare_lounge_credit (param $12/$6/0), companion_fare_rebooking_goodwill (param $25/$12/0), companion_fare_holder_fare_credit (param $10/$5/0) | 4/1 | activity: mqd-accrual sum AND flight-accrual count (distinct rows) | activity (loyalty), lounge (club), holder fare (ticket) |
| P6 | phone_fee_rebooking_context_method (method: ×0.5 / +$10 / as published), phone_fee_repeat_call_center (param 40/20/0), phone_fee_status_waiver (param 60/30/0), phone_fee_card_credit (param $5/$3/0) | 3/1 | rebooking context: reinstatement ground (reinstatement row) AND days to booking date (booking row) | status (loyalty), card (loyalty) |
| P7 | taxes_ticket_tax_base_method (method: 0.6×(fare+surcharge) / fare+phone fee / fare), taxes_cardholder_credit (param $12/$6/0), taxes_rebooking_credit (param $6/$3/0), taxes_frequent_flyer_credit (param $8/$4/0) | 3/1 | cardholder: issue_source (companion holding) AND card-partner miles (loyalty_activity) | cardholder (loyalty), flyer (loyalty) |
| P8 | phone_refund_claim_window_method (method: whole / pro-rated / nothing), phone_refund_status_uplift (param 20/10/0), phone_refund_membership_age_uplift (param 10/5/0), phone_refund_lounge_uplift (param 10/5/0) | 3/1 | none strictly (claim-window conjunction reads one reinstatement row + the clock) | status (loyalty), age (loyalty), lounge (club) |

- Counts: every policy has 4-6 factors, ≥2 parameter, 1 method. Every ladder has three pairwise-disjoint tiers stated in full in the rule, each drawn from the policy's own params. No two tiers of any ladder share a value or method. Every fall-through equals the factor's `baseline`, and every `baseline` equals what `baseline.rule` states for that input (P1/P2/P3: refund in full ⇒ retention 0 / share method = full; P4: `standard_fee`; P5: `product_fare`; P6: `product_phone_fee`; P7: tax on fare alone; P8: 0 as base "not refunded"). `decides` is never `result`; binding sets within each policy are disjoint.
- Labels: each `method` factor switches the operation (percentage vs flat vs none; proportional vs deduction vs full; multiply vs add vs none; a different tax base); each `parameter` factor substitutes a number into a fixed formula. Honest.
- Multi-source and cross-difficulty per tree: the P1-P4 tree has MS factors (P1 retention, P3 processing, P4 relief) and XD factors reading loyalty and club; the P5-P8 tree has MS factors (P5 activity, P6 rebooking context, P7 cardholder) and XD factors reading loyalty, club and ticket.
- Realism (charter-level; recorded as observations O5, O6 — no ladder is shown to hold of every customer or to give a treatment no carrier could publish):
  - P3 processing charge counts refund *entries* (one per charge component), so one cancellation contributes 2-3 entries, and at P3's own handling time the same cancellation's fare/surcharge refunds, already posted, count toward the tier.
  - P8 tier 2 pro-rates downward, by days elapsed since Crestline's own cancellation, a fee refund the rule says is owed for that cancellation.
- Structure only; weight is per task (0.md / 1.md `factor_weight`).

### findings

- **F1 — rounding mode unstated in the policy; compute and tool contract disagree on exact half-cent ties.** Symptom: rules say only "rounded to the cent"; `compute` rounds with binary-float `round(x, 2)`; every task tool's `amount` Arg says "rounding half up". Root cause: `compute_basis` quotes no rounding mode; the rounding point is stated but the mode is not. Evidence: e.g. P4 `adjusted_fee: "RND(fee_core * booking_time_factor * (1 - flyer_relief_pct / 100), 2)"` vs `pay_companion_reinstatement_fee_0c05ba56` Arg `amount: … rounded to 2 decimal places (cents), rounding half up`; `round(42.345, 2) == 42.34` in Python while half-up gives 42.35. Consequence: charter-global it is latent; it becomes a second defensible value only in a world whose chain hits an exact half-cent intermediate — demonstrated per task (bears on task 0 — see `0.md`; task 1's chain has no exact tie — see `1.md`). Affected: every extended policy's `compute` RND bindings; tool Arg texts.
- **O1 (observation) — three `condition`s add a date qualifier the prerequisite sentence does not carry.** P3→P1 condition "…dated on the handling date of the settlement"; P3→P2 "…recorded on the same entry date as the companion fare refund"; P4→P3 "…recorded on the handling date together with the booking's other refunds". The sentences ask only that the ledger carry the refund. The same-date requirement is real in P3's and P4's compute (same-entry-date conditions in their own rule), so the value logic is stated in the rule; no world of this difficulty separates the two readings (all resolving writes land on the handling date). No demonstrated consequence.
- **O2 (observation)** — base `companion_cancellation` "On every cancellation the companion fare and taxes are refunded in the companion_fare_refund_form" can be read as a full-amount statement; the amount is governed by refund_controls' declared-and-replaced clause, and P1/P3's rules state their retention outright. Not a second answer: the base sentence fixes form and entry count, not amount.
- **O3 (observation)** — base cross-problem order "A pass must have a designated_companion_name before any booking" grounds no edge; no task tree involves a pass.
- **O4 (observation)** — each task-tool Arg says "as returned by the … lookup before the call": an ordering word about the id-supplying read, not about another write; names no tool.
- **O5 (observation)** — P3 processing-charge ladder counts component refund entries (see factor_ladders). The line of business does weigh refund frequency; entry-level counting inflates it but divides customers (a non-Hawaii first cancellation stays on the fall-through).
- **O6 (observation)** — P8 pro-rated claim-window tier: a carrier refunding its own cancellation's fee on a declining scale is unusual, but claim windows for ancillary refunds exist; not demonstrable as a treatment no carrier would publish.
- **O7 (observation)** — P1's rule opens with the baseline sentence "…refunded in full with no cancellation retention" and then states a retention; P2/P3/P4/P5/P6/P7/P8 follow the same "baseline, then factors, then final sentence" pattern. The final sentence of each rule fixes the result, so no second answer arises within the rule; this is the design's baseline-in-rule contract.

## closing_checklist

Written after both tasks' derivations were frozen and revealed (2026-09-24T17:55Z). This section is post-reveal; nothing above it was edited after the reveal.

- Audit files: `0.md`, `1.md` correspond one-to-one with tasks 0 and 1; `_difficulty.md` alongside; first revision (no older revisions).
- Comparison verdicts: task 0 **SOURCE-TASK RED** (root cause F1: rounding mode unstated; the fee lands on an exact half-cent, 42.345, and GT's 24.34 differs from the half-up reading 24.35 that the tool contract states); task 1 **PASS**.
- Coverage and scope: charter_scope task 0 = {P1, P2, P3, P4}, task 1 = {P5, P6, P7, P8}; pairwise disjoint, jointly all eight extended policies; each scope spans its whole tree. Task tools closed over GT (each of the eight tools used once); uuid8s independent (`action_binding_and_uuids`).
- Trees: task 0 has 3 prerequisite problems with 4 value_input edges, and task 1 has 3 with 3 value_input edges. Each tree has at least one owner=user write (task 0: P4; task 1: P5, P6, P7) and no cycle. The difficulty-wide graph is two disjoint DAGs.
- Factors: 34 factors, each policy 4-6 with ≥2 parameter and 1 method. Each ladder has three tiers stated in full in its rule. Every factor bears weight on its task's world against an honest baseline, and every whole-baseline differs from gold.
- Gates: the coordinator's snapshot (check_extended, check_task_tools, replay_tasks, check_solvability, check_compute, check_grounding, check_cross_fire — all rc=0) is cited; this auditor does not run gates.
- **The difficulty does not pass the source-layer audit**: task 0's unique-solution relationship fails (SOURCE-TASK RED, root cause F1 at charter level).

## revision_2

### charter_global_frozen (revision_2)

- auditor: the same independent audit agent as round 1 (erl-task-policy-audit); re-audit of the round-1 REDs, looking for closure, new defects and regressions.
- freeze time: 2026-09-24T18:15Z. Written before either round-2 task file (`tasks/0.json`, `tasks/1.json`, both modified 18:09) was opened.
- inputs:
  - `companion.extended.yaml` sha256 `c156a2ca871e502580dbfa4647e54f4c3f60fbf3bdd4d1f4b8e8524215a17851`. This changed from round 1's `389c47e1…bb6c`, so every charter-global section is re-derived below.
  - `task_tools.py` sha256 `cf586a5b…aeb1`, unchanged.
  - masked views r2 `2658c1b6…81ca` / `81310981…2f68`, byte-identical to round 1.
- base copy: `diff <(sed -n '1,1384p' companion.extended.yaml) blueprint/products/companion.yaml` → identical.
- **What changed in the charter.** The eight rules were normalised, each by the following steps:
  - dropping the new lead sentence;
  - mapping "rounded half up to the cent" back to "rounded to the cent";
  - stripping `+ 0.0000001` from compute.

  Compared this way, the rules, `params`, `factors` (ids, effects, `decides`, `cross_difficulty`) and compute structure are the same as round 1's. The edits are exactly:
  1. every extended `rule` now opens with "Every rounding in this rule is half up to the cent, a value lying exactly on a half cent going up to the next cent.";
  2. every "rounded to the cent" in the rules, the `compute_basis` quotations, the `overwrite.replaced_by` texts, the ladder method texts and P7's `baseline.rule` now reads "rounded half up to the cent" (plain "rounded to the cent" count now 0 in all eight rules and all ladders);
  3. every `RND(x, 2)` in `compute`, and P7's factor baseline `ticket_tax`, is now `RND(x + 0.0000001, 2)` (RND count = epsilon count in every binding, checked by script);
  4. the `condition` texts of P3→P1, P3→P2 and P4→P3 lost their date qualifiers.

### policy_conflict_scan (revision_2)

Unchanged in substance from round 1 (same subjects, components, triggers, eligibility inheritance, read-only cross-category boundaries, terminal rows). The two closed trees {P1-P4} and {P5-P8} still have no edge between them. No conflict.

### rule_compute_equivalence (revision_2)

- Round-1 bindings still correspond one to one, with the same quotations.
- Rounding mode is now stated in every rule: the lead sentence covers every rounding, and each rounding point says "half up". `compute_basis` quotes the half-up wording at each stated rounding point (all `compute_basis` values verbatim in their rule, checked by script).
- The compute implements half-up as `round(float(x + 1e-7), 2)`. Checked on the round-1 tie: 75.28 × 0.75 × 0.75 = 42.345 → 42.35.
- The nudged RNDs at points the rule does not name are sums or differences of cent amounts, and the lead sentence covers them. Examples: P2 `surcharge_retention`, P4 `refunded_value` and the fee×count branch, P5 close-in `starting_fare`. The nudge cannot move an exact cent sum.
- Tool Args still say "rounding half up": the policy surface, the compute and the tool contract now agree.
- The epsilon nudge is an approximation of half-up (observation O8 below).

### action_binding_and_uuids (revision_2)

- `task_tools.py` unchanged; eight distinct `(target_tool, amount)` claims; same uuid8s.
- Round-1 conclusion carried forward on the unchanged hash.

### prerequisite_graph (revision_2)

- Same seven edges, `problem`s, gates, kinds, forms and `resolved_by`; acyclic.
- Every `policy_source` is verbatim in its rule. The new lead sentence was inserted before, not inside, any prerequisite sentence (checked by script).
- `condition`s:
  - P3→P1 now reads "…names the cancelled booking's companion fare charge."
  - P3→P2 now reads "For a booking that carried a Hawaii surcharge, the certificate's ledger carries a refund entry of component Hawaii surcharge that names that booking's Hawaii surcharge charge."
  - P4→P3 now reads "…names the cancelled booking's taxes-and-fees charge."

  Each is now exactly the strength and scope of its sentence. The same-entry-date logic still lives in P3's and P4's own value sentences, where it belongs. **O1 closed.**

### prerequisite_sentences (revision_2)

- The seven sentences are unchanged, so the round-1 four-point test and single-resolving-write derivations stand.
- No rule gained a tool name, an id, a second wording or an undeclared cross-problem order. The lead sentence states no dependency.

### override_declarations (revision_2)

- The same six `overwrite` entries apply to the same base clauses; the `replaced_by` texts now carry "rounded half up" and remain verbatim in their rules.
- Sentence-by-sentence conclusions against `companion_refund_controls`, `companion_cancellation`, `companion_booking_rules` and `companion_designation` are unchanged from round 1.
- Base provisions state no rounding mode, so stating half-up overrides no base sentence.
- O2 and O3 are unchanged.

### factor_ladders (revision_2)

- Same 34 factors, labels, ladders, tier values and `decides`.
- Where a ladder names a rounding it now says half up (P1 retention tier 1, P2 share tier 1, P3 share tier 1, P4 two-reinstatement tier, P5 early tier).
- Fall-throughs equal the baselines. P7's factor baseline carries the same epsilon as its compute, so baseline and gold round the same way.
- O5 and O6 are unchanged.

### findings (revision_2)

- **F1 — closed.** The rounding mode is now stated in every rule and quoted in `compute_basis`, implemented by compute, and in agreement with the tool Args. Task 0's demonstration is re-run in `0.md` revision_2.
- **O1 — closed** (see prerequisite_graph).
- O2, O3, O4, O5, O6 and O7 are carried forward unchanged (the underlying texts are unchanged).
- **O8 (new observation)** — the compute implements half-up as `round(float(x) + 1e-7, 2)`. It would round up a value lying within 1e-7 below a half cent, which only a non-terminating quotient can produce (P2/P3 share tiers, P8 pro-rating). No such value arises in either task's world, and the rules state the intended mode unambiguously, so the published surface and a correct half-up agree on both worlds.
- **Seed history under the revised rounding** (both tasks, recomputed by hand on each entry's own date). No historical charge or refund lands on a half-cent tie, so every seeded amount is the same under half-up as under round 1's rounding:
  - task 0: 218.10, 37.51, the 2025 refunds (218.10, 100.00, 34.21) and fee 32.00; 228.06 and 24.96;
  - task 1: 99.86, 14.50 and 21.78, and the 2026-03-05 refunds.

  Intermediates checked: 224.10, 14.3145, 3.30, 234.06, 14.7627, 111.86, 17.50, 8.577. No seed row disagrees with the revised charter.

### closing_checklist (revision_2)

Written after the revision_2 reveals (clock 18:12Z; the "18:15Z" in this revision's freeze header is a clock misstatement; the freeze preceded the reveal).

- Per-task files `0.md` and `1.md` each carry a revision_2 section with source_derivation_frozen, source_gt_comparison and findings. The round-1 text is left untouched.
- Verdicts: **task 0 PASS, task 1 PASS** on all four relationships.
- Round-1 items:
  - F1 closed; 0.md finding 1 closed; 0.md finding 2 closed; O1 closed; 1.md observation 2 addressed.
  - O2, O3, O4, O5, O6 and O7, 0.md findings 3 and 4, and 1.md observations 1 and 3 are unchanged and still observations.
  - New observations: O8 (epsilon approximation of half-up) and 0.md O-r2-1 (stale change-log line). Neither has a scored consequence.
- Coverage and scope: task 0 = P1-P4 and task 1 = P5-P8, disjoint and jointly complete. Tools are closed over GT; uuid8s unchanged and independent.
- Trees: task 0 has 3 prerequisite problems and 4 value_input edges; task 1 has 3 and 3. Each has an owner=user write. Both graphs are acyclic.
- Factors: 34, all bearing weight on their task's world against honest baselines; every whole-baseline differs from gold; multi-source and cross-difficulty factors present in both tasks.
- Gates: the coordinator's round-2 re-run (EXTENDED / TASK TOOL CONTRACT / REPLAY / SOLVABILITY / COMPUTE / GROUNDING / SCOPE, all rc=0; traceability deferred) is cited, not run by this auditor.
- **The difficulty passes the source-layer audit at revision_2.**
