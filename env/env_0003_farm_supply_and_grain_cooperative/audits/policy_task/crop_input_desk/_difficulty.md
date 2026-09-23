# Policy-task audit — crop_input_desk / charter-global

## charter_global_frozen

| item | value |
| --- | --- |
| auditor | independent source-layer auditor (did not write these artifacts) |
| freeze time | 2026-09-18, written before any task's GT fields were opened |
| `agronomy.extended.yaml` | sha256[:16] = `509d0471c9ee0c73` |
| `task_tools.py` | sha256[:16] = `fb62107a7cae45c5` |
| `blueprint/products/agronomy.yaml` | sha256[:16] = `66127eecc1f99b7b` |
| masked view 0.json | sha256[:16] = `a3c0c7eb8d396a72` |
| masked view 1.json | sha256[:16] = `e26b92027be00f8f` |

Fields permitted while this section was written: `blueprint/blueprint.yaml`, `blueprint/db_schema.json`,
`blueprint/share_tools.py`, `blueprint/products/*.yaml` (agronomy as the primary; grain, storage, patronage,
custom read only to check that cross-category seed rows do not contradict their own charters),
`tasks/crop_input_desk/agronomy.extended.yaml` in full, `tasks/crop_input_desk/task_tools.py` in full, and — via
the orchestrator's masked views only — each task's `frozen_time`, `user_scenario` and `initial_state`.

Fields explicitly masked and unread at freeze time: `charter_scope`, `computations`, `db_closure`,
`db_closure_matches_initial_state`, `design_rationale`, `evaluation_criteria`, `prerequisite_closure`,
`required_documents`, `solvability_contract`.

Entry conditions (Step 0): the brief supplied the instantiation-stage gate snapshot with its actual output lines
(`check_extended`, `check_task_tools`, `replay_tasks`, `check_solvability`, `check_compute`, `check_grounding`,
`check_cross_fire` — all green), the two masked views with both their own and the full task files' hashes, and the
masking division. `check_traceability` was declared deliberately unrun because the KB does not yet exist. Entry
conditions are complete; the gates were cited, not re-run.

### policy_conflict_scan

The difficulty's structured policy is the base section of `agronomy.extended.yaml` (verified **byte-for-byte
identical** to `blueprint/products/agronomy.yaml`: `category`, `display_name`, `binding`, `lifecycle`, `accounts`,
`parameter_schema`, `variants`, `events`, `measures` and `policies` all compare equal after YAML load; the only
extra top-level key is `extended_policies`) plus five extended policies.

| # | extended policy | subject | computes | target_tool | owner | `prerequisite` |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | `agronomy_ext_crop_protection_return_credit` | `agronomy_credit_memo_issued` | `credit_amount` | `issue_return_credit_6859ca91` | agent | `[]` |
| 2 | `agronomy_ext_arrears_service_charge` | `agronomy_finance_charge_assessed` | `service_charge_amount` | `assess_overdue_service_charge_aaf992aa` | agent | ← 1 (`value_input`, gate `overdue_balance`) |
| 3 | `agronomy_ext_arrears_settlement_payment` | `agronomy_payment_posted` | `payment_amount` | `post_member_arrears_payment_ad47b93a` | **user** | ← 2 (`value_input`, gate `charges_standing`) |
| 4 | `agronomy_ext_season_volume_discount` | `agronomy_discount_granted` | `discount_amount` | `grant_season_volume_discount_cc5ed557` | agent | `[]` |
| 5 | `agronomy_ext_prepay_booking_ceiling` | `agronomy_prepay_booked` | `booking_amount` | `book_prepay_commitment_189dfe27` | **user** | ← 4 (`value_input`, gate `prior_net_spend`) |

Overlapping subjects, triggers, eligibility, time anchors, action parameters, terminal states and cross-category
read boundaries:

- **Subjects are pairwise disjoint** across the five extended policies (five different event types of the agronomy
  catalogue), so no two extended policies decide the same write.
- **Triggers**: `state_due` for 1, 2 and 4; `on_request` for 3 and 5. The two `on_request` policies are exactly the
  two `owner=user` writes, which matches the base charter's division of labour ("booking prepay … and closing the
  account are the member's own acts and are handed over").
- **Time anchors**: policy 2 anchors its day count on `agronomy_accounts.past_due_since` / the latest posted charge
  / the latest posted payment; policy 3 on `past_due_since`; policy 1 on the credited line's `invoice_date`; policy
  5 on `opened_date`. No two extended policies anchor the same quantity on different events.
- **Cross-category read boundaries**: declared per policy and matched by the `compute` — policy 1 reads `custom`
  (`EXISTS('custom', …)`, `XCOUNT('custom','custom_workorders', …)`); policy 2 reads `storage`
  (`EXISTS('storage', …)`, `XCOUNT('storage','storage_charges', …)`); policy 3 reads `grain`
  (`CFIELD('grain', …)`, `XCOUNT('grain','grain_ledger', …)`) and `patronage`
  (`XCOUNT`/`XSUM('patronage','patronage_ledger', …)`); policy 4 reads `custom`; policy 5 declares
  `cross_category: []` and makes no cross-category call. Every cross-category call in a `compute` is covered by that
  policy's `cross_category` block and no block is declared without a call.
- **Terminal states**: each target tool lands exactly one ledger row on `agronomy_invoices` and mutates no holding
  status, so no two policies contend over an account's lifecycle state.
- **Claimed scopes**: derived independently from the two masked worlds (see each task file), the suite partitions as
  task 0 = {1, 2, 3} and task 1 = {4, 5}. The two scopes are **pairwise disjoint** and their union is **all five**
  extended policies; each scope spans a whole problem tree (root plus every prerequisite problem).

No conflict found in this scan.

### rule_compute_equivalence

Checked mechanically and then by hand over all five policies.

- **Every `compute` binding has a `compute_basis` entry and every `compute_basis` key is a `compute` binding** —
  no orphan either way, in all five policies.
- **Every sentence of every `compute_basis` entry appears verbatim in that policy's own `rule`** — checked by
  whitespace-normalised substring over all five policies, zero misses. So `compute` invents no basis of its own.
- **Every sentence of every `baseline.rule` appears verbatim in that policy's `rule`** — zero misses, all five.
- **Every ternary branch in `compute` is a declared factor's `decides` binding**: policy 1 has 4 (`credit_unit_price`,
  `restock_pct`, `waived_share_pct`, `handling_charge`), policy 2 has 6 (`monthly_pct`, `overdue_days`, `grace_days`,
  `clawback_share_pct`, `charge_after_relief`, `surcharge`), policy 3 has 6 (`charge_share_pct`, `reinstate_pct`,
  `age_step_pct`, `grain_share_pct`, `patronage_share_pct`, `settled_figure`), policy 4 has 4 (`volume_rate_pct`,
  `qualifying_spend`, `acre_bonus_pct`, `uplift_pct`), policy 5 has 4 (`prior_net_spend`, `ceiling_share_pct`,
  `arrears_cut_pct`, `offset_share_pct`). **No tier lives only in `compute`.**
- Windows, filters, acting bases, caps/floors and rounding points each carry a verbatim quotation: the ten/twelve/
  fourteen/twenty-six/thirty-six statement-month windows, the six-statement-month terms cut, the
  `MX(0, …)` floors on `chargeable_days`, `net_due`, `net_share_pct` and `qualifying_spend`, the
  `MX(P('finance_charge_minimum_usd'), …)` and `MX(P('prepay_minimum_usd'), …)` floors, and every `RND(…, 2)`.
- The ladders' `when`/`method` strings are *paraphrases* of the rule sentences rather than verbatim copies (e.g.
  `credit_pricing_basis` tier 3 reads "the credit is computed at the unit price the line coming back was invoiced
  at" against the rule's "The unit price the credit is computed at is the unit price the line coming back was
  invoiced at"). In every case the tier's condition **and** its value or method are stated in the rule and
  implemented in `compute`; the paraphrase is the ladder's summary of a rule sentence, not a second basis. Recorded
  as no-finding.

Two wording/scope looseness items are recorded under `findings` as observations (OBS-1, OBS-2); neither changes a
number on either task's world.

### action_binding_and_uuids

- Each `(target_tool, computes)` pair is claimed by **exactly one** policy; five tools, five distinct `computes`
  names, no reuse.
- Every task tool body was read in full. Each does exactly: `make_id` → `find("agronomy_accounts", account_id=…)`
  to pick up `customer_id` → one `ctx.create` on `agronomy_invoices` → return a confirmation sentence. **No tool
  aggregates a ledger, reads a tier table, or weighs any condition**, and none inspects another problem's state.
- Sign conventions are coherent with the base charter's `direction` declarations: credit memo `amount=-value`
  (base `direction: out`), service charge `amount=+value` (`direction: in`), payment `amount=-value` (`out`),
  volume discount `amount=-value` (`out`), prepay booking `amount=+value` (`in`, account `prepay_credit`).
- uuid8 suffixes: `6859ca91`, `aaf992aa`, `ad47b93a`, `cc5ed557`, `189dfe27`. No shared prefix, no common tail, no
  sequence, no adjacency, no hex-neighbour pattern; each is independently generated and frozen with its tool.
- Docstrings: none names another tool, none states an action's position relative to another problem's write, none
  carries a business ordering word about the problem tree. The only ordering words present are parameter-provenance
  phrases of the form "take it from the crop input account record pulled up for this member **before the call**",
  which order a *read the caller must already have done* and disclose no prerequisite. Recorded as no-finding.

### prerequisite_graph

Three edges, all `kind: value_input`:

| edge | blocked policy | depended-on | `gate` | `resolved_by` | `form` | `fallback_reason` |
| --- | --- | --- | --- | --- | --- | --- |
| A | 2 `agronomy_ext_arrears_service_charge` | 1 | `overdue_balance` | `issue_return_credit_6859ca91` | `state` | absent (correct) |
| B | 3 `agronomy_ext_arrears_settlement_payment` | 2 | `charges_standing` | `assess_overdue_service_charge_aaf992aa` | `state` | absent (correct) |
| C | 5 `agronomy_ext_prepay_booking_ceiling` | 4 | `prior_net_spend` | `grant_season_volume_discount_cc5ed557` | `state` | absent (correct) |

- Every policy fills `prerequisite` (policies 1 and 4 carry `[]`).
- Every `problem` points at another **extended** policy id in this file; none points at a base policy and none at
  itself. The graph is 1→2→3 and 4→5: **acyclic**, no cross-task reference, no cycle.
- Every `gate` names a binding that genuinely exists in the blocked policy's own `compute`: `overdue_balance` is
  binding #11 of policy 2, `charges_standing` is binding #8 of policy 3, `prior_net_spend` is binding #5 of policy
  5. `kind: value_input` therefore matches `gate` in all three (none is a status flip).
- Every `resolved_by` is the depended-on policy's `target_tool`, and each genuinely moves the named binding:
  `issue_return_credit_*` creates an `agronomy_credit_memo_issued` row with a negative `amount`, which
  `overdue_balance`'s `credits_standing` term sums; `assess_overdue_service_charge_*` creates an
  `agronomy_finance_charge_assessed` row with a positive `amount`, which is exactly what `charges_standing` sums;
  `grant_season_volume_discount_*` creates an `agronomy_discount_granted` row with a negative `amount`, which
  `prior_net_spend`'s `discounts_standing` term sums. The `effect` text of each edge describes that movement
  correctly (falls / rises / falls).
- No `condition` is quietly strengthened or weakened relative to its `policy_source`, with one scope mismatch on
  edge A recorded as OBS-3.
- No authoring-viewpoint phrasing ("in this task", "at the opening", "the current world") appears anywhere in the
  file; scanned and empty.

### prerequisite_sentences

Each `policy_source` was located verbatim in the **blocked** policy's own `rule` and put through the four-point test.

**Edge A** — in policy 2's rule: *"The service charge on a crop input account is worked out only once every credit
memo owed for product that has come back to the plant stands written against that account."*
Ordering connective: "only once" ✓. Waited-on thing: a record-visible state — credit memos standing written against
the account — in the words the tables and finders use (`agronomy_credit_memo_issued`, "crop input account"), with no
action, performer or tool ✓ (`form: state` honoured, no fallback needed or declared). Names no tool, policy id,
snake_case token or row id ✓. **Single write that brings the state about**: `issue_return_credit_6859ca91` is the
only tool in this difficulty that creates an `agronomy_credit_memo_issued` row, so the hop resolves uniquely.
Derivation a reader performs: the sentence says the charge waits on every owed credit memo standing written → the
reader queries the account's billing rows and the member's lodged agronomy requests → finds an approved, signed
`product_return` request with no credit memo posted after it → reads policy 1's own rule, which is the charter's
only rule describing the writing of a credit memo for product come back to the plant → performs that write first.
One reading only. Policy 1's rule does not restate the sentence ✓; policy 2's rule carries no second wording of the
dependency and no other problem's tool name ✓.

**Edge B** — in policy 3's rule: *"The figure that settles the arrears on a crop input account is fixed only once
that account's ledger carries the service charge due on its overdue invoices for the statement month then
running."* "only once" ✓; state form ("that account's ledger carries the service charge due …") ✓; no tool/id ✓.
`assess_overdue_service_charge_aaf992aa` is the only tool creating an `agronomy_finance_charge_assessed` row →
unique hop. Policy 2's rule does not restate it ✓.

**Edge C** — in policy 5's rule: *"The money the cooperative will take on a prepay booking is fixed only after the
account's ledger carries the volume discount earned on the input spend of the crop year just closed."* "only after"
✓; state form ✓; no tool/id ✓. `grant_season_volume_discount_cc5ed557` is the only tool creating an
`agronomy_discount_granted` row (and it stamps `discount_type="volume"`) → unique hop. Policy 4's rule does not
restate it ✓.

**No undeclared cross-problem order**: every remaining mention of another problem's output inside a rule is a
*quantity* statement, not an ordering ("every credit memo written on it … is set against that balance"; "the share
carried in of the service charges standing on the account"; "less every discount granted on the account"). None
carries an ordering connective and none grounds an undeclared edge. No **base** rule sentence is relied on to
ground any edge: all three `policy_source` quotations are sentences of the *extended* rules.

### override_declarations

Sentence-by-sentence against each `base_policy_refs` entry. Findings only; the consequence for a given world lives
in that task's file.

**Policy 1 vs `agronomy_returns_and_credits`.**
Followed: returnable-class and return-window sentence (inherited; crop protection is returnable on every programme
that carries this write, and the window is checked per task); the unopened-packaging sentence; the seed-cutoff
sentence (not engaged); the never-returnable sentence (not engaged); "A credit memo is written against the invoice
the product was billed on" (followed exactly — the tool takes `invoice_number` and `delivery_ticket_number`); the
account-already-clear sentence (not engaged).
Handled differently: *"An accepted return is credited at the price it was invoiced at, not the price of the day,
less the programme's restocking charge as a percentage of that invoiced value."* The extended prices two of its
three tiers off a different price (the most recent prepay booking's locked price; the highest crop-protection unit
price ever invoiced on the account), scales the restocking charge by a waived share, and withholds a further
handling figure. **That base sentence is named in `overwrite[0].superseded_clause`**, so the whole of it — price
basis and restocking treatment alike — is superseded. Declaration correct.

**Policy 2 vs `agronomy_finance_charge`.**
Declared: the charge-formula sentence ("The charge is the programme's monthly percentage on the unpaid balance of
that invoice, assessed once per statement month …, and where the computed charge falls under the programme's floor
the floor is assessed instead") and the per-invoice sentence ("It is assessed per invoice rather than on the account
total, so a member with three overdue invoices carries three charges and three floors"). Both are named, and the
proration by chargeable days over a thirty-day statement month, the account-wide balance and the single booked
charge all fall inside those two supersessions.
Not hit, and checked as inherited: *"A service charge is assessed on an invoice still unpaid after its grace
period, and the grace period is counted in whole calendar days from the due date of that invoice, the due date
itself counting as day zero, an invoice cleared on the final day of grace attracting nothing."* The extended does
not contradict this as an **eligibility gate** — it still requires an unpaid invoice past grace — but it
additionally reuses the same `finance_charge_grace_days` figure as a *deduction* from a day count anchored
elsewhere. Recorded as OBS-4 (no second answer follows: the gate is satisfied either way on the only task that
carries this policy).
Also inherited without conflict: "A programme with no monthly percentage assesses no service charge at all"; the
reversal sentence; the referral of goodwill waivers to the credit department.

**Policy 3 vs `agronomy_payment_application`, `agronomy_credit_standing`, `agronomy_finance_charge`.**
Declared: `agronomy_credit_standing`'s reinstatement-share sentence, named in `overwrite[0]`.
`agronomy_payment_application`, sentence by sentence: "applied to the invoices it names, and where it names none …
in the programme's allocation order" — the tool posts one payment line and names no invoice, so the programme's
`payment_allocation_order` governs downstream; no conflict with the scored quantity. "Payments may reach the
cooperative only by the methods the programme allows" — inherited and checked per task against
`payment_methods_allowed`. "A part payment on an overdue balance is accepted only at or above the programme's
minimum part payment as a share of the balance" — inherited; checked per task against the overdue balance the
extended itself defines, and clears it on the only task that carries this policy. "Payments are applied on the day
they are received" — followed (`posted_date=ctx.now()[:10]`). The settlement-proceeds sentence is not engaged.
`agronomy_finance_charge`: carrying a share of the standing service charges into a quoted settlement figure is not
a reversal, so "A service charge already assessed is reversed only where …" is not contradicted.

**Policy 4 vs `agronomy_discount_schedule`.**
Declared: the volume-discount sentence, named in `overwrite[0]`, replaced by the fourteen-statement-month,
single-account, credit-memo-net definition.
Not hit and checked: the early-pay sentence (a separate discount kind, not computed here); the stacking-basis
sentence (the programmes that can carry this write use `prepay_then_volume_additive` or `best_single_discount`; on
the only task that carries this policy the basis is additive and only one volume line is written, so no conflict);
"A discount a programme does not carry is not zero but simply not applicable" (the fall-through tier is the
programme's own `volume_discount_pct`, so a programme that carries none computes nothing); the programme-rebate
sentence — the extended's `applied_acre_bonus` reuses `program_rebate_threshold_acres` against **applied** acres
whereas the base rebate measures **enrolled** acres, which is a different quantity under a shared parameter name.
Recorded as OBS-5; the rebate itself is written by no task tool and is not a scored quantity, so no conflict on the
scored number.

**Policy 5 vs `agronomy_prepay_program`.**
Declared: the minimum-and-ceiling sentence, named in `overwrite[0]`. The extended's secured tiers (120 % and 105 %
of prior season spend) exceed the programme's catalogued `prepay_maximum_pct_of_prior_year` on the financing
programmes; that is exactly what the declared supersession licenses.
Not hit and checked: the booking-window sentence (inherited; checked per task); "The booking locks the price of the
product it names" — the task tool takes no unit price and writes none, recorded as OBS-6; the drawdown-order and
transferability sentence (the extended reads `prepay_transferable_between_categories` for its offset share, which
neither weakens nor contradicts it); the forfeiture sentence (inherited, checked per task); "Prepay is never
refunded in cash on request" (not engaged).

**No undeclared override was found.** In particular none of the three disguised forms is present: no anonymous
intermediate quietly replaces a base quantity (every intermediate is quoted back to a rule sentence), no 0/1
multiplier zeroes a base-fixed amount (the nearest candidates — `waived_share_pct`, `clawback_share_pct`,
`grain_share_pct`, `patronage_share_pct`, `offset_share_pct`, `arrears_cut_pct` — are all declared factors whose
fall-through is the baseline), and no base branch is dropped by an extended selector (each ladder's fall-through
restores the programme parameter the base names).

### factor_ladders

Structure only. 24 declared factors over five policies; counts per policy are inside the 4–6 bound and every ladder
has three pairwise-disjoint tiers with the fall-through counted.

| policy | factors | `parameter` | `method` | multi-source tiers | `cross_difficulty` |
| --- | --- | --- | --- | --- | --- |
| 1 | `restocking_rate`, `credit_pricing_basis`, `return_handling_figure`, `field_service_restocking_waiver` | 3 | 1 (`credit_pricing_basis`) | `restocking_rate`, `credit_pricing_basis`, `field_service_restocking_waiver` | `custom` (`field_service_restocking_waiver`) |
| 2 | `settled_buying_service_rate`, `overdue_clock_anchor`, `reviewed_account_grace`, `stored_grain_relief`, `discount_clawback_share`, `long_arrears_handling_sum` | 4 | 2 (`overdue_clock_anchor`, `stored_grain_relief`) | `settled_buying_service_rate`, `overdue_clock_anchor`, `reviewed_account_grace`, `stored_grain_relief`, `long_arrears_handling_sum` | `storage` (`stored_grain_relief`) |
| 3 | `settled_buying_reinstatement_share`, `committed_grain_credit_share`, `quoted_figure_rounding`, `service_charge_carry_in`, `patronage_cash_offset_share`, `arrears_age_step` | 5 | 1 (`quoted_figure_rounding`) | `settled_buying_reinstatement_share`, `committed_grain_credit_share`, `quoted_figure_rounding`, `patronage_cash_offset_share` | `grain` (`committed_grain_credit_share`), `patronage` (`patronage_cash_offset_share`) |
| 4 | `steady_buying_discount_rate`, `qualifying_spend_basis`, `applied_acre_bonus`, `settlement_record_uplift` | 3 | 1 (`qualifying_spend_basis`) | all four | `custom` (`applied_acre_bonus`) |
| 5 | `secured_buying_ceiling_share`, `prior_season_spend_basis`, `standing_prepay_offset`, `arrears_ceiling_cut` | 3 | 1 (`prior_season_spend_basis`) | `secured_buying_ceiling_share`, `prior_season_spend_basis`, `arrears_ceiling_cut` | none |

- **Binding sets are disjoint within every policy** — checked factor by factor; no binding is claimed twice.
- **`decides` is an input in every case**; no factor decides `result`.
- **No two tiers of any ladder select the same value or method** — checked ladder by ladder against the programme
  parameters each fall-through resolves to. The one place worth naming: `secured_buying_ceiling_share`'s
  fall-through is `P('prepay_maximum_pct_of_prior_year')`, which is 125 on the Early Pay Prepay programme and 100
  on the two financing programmes, against tier values of 120 and 105 — distinct on every programme that can carry
  the write.
- **Every fall-through tier is exactly the policy's `baseline` binding** — verified for all 24 factors.
- **Labels are honest**: each of the five `method` factors changes the algorithm, not a number
  (`credit_pricing_basis` swaps which price the credit is computed at; `overdue_clock_anchor` swaps the date the
  day count starts from; `stored_grain_relief` swaps the arithmetic applied to the charge; `quoted_figure_rounding`
  swaps the rounding rule; `qualifying_spend_basis` and `prior_season_spend_basis` swap which aggregate the rate
  acts on). Each `parameter` factor's tiers substitute a rate, a day count, a share or a dollar figure into an
  unchanged formula. No `method` tier names a computation rule the charter does not state.
- **Every tier's condition and outcome is grounded in the industry** with two exceptions recorded below: the
  compound conditions weigh promptness of return, season spend, payment record, delivery count, credit standing,
  perfected security interest, enrolled/applied acres, grain in store, grain still owed, patronage posted and
  prepay standing — all things a farm-supply cooperative genuinely weighs. The cross-category conditions are
  grounded in the *other* charters too (e.g. Class A patronage carries `offset_against_unpaid_balance: true` with
  `offset_priority_order: input_account_then_energy_then_feed`, and base `agronomy_agg_exposure_across_accounts`
  already grants a working allowance against open bushels).
- **One tier condition fails the "does it divide anyone" test**: `discount_clawback_share` — see RED-1 below.
- **One tier outcome and one tier parameter reuse read oddly**: `credit_pricing_basis` tier 2 and
  `return_handling_figure` — see OBS-7 and OBS-8.
- Whether each factor bears weight is a fact about one world and is recorded in each task's `factor_weight`.

### findings

**RED-1 — `SOURCE-FACTOR RED` (charter-global finding; consequence demonstrated in `0.md`).**
*Symptom.* `agronomy_ext_arrears_service_charge` / factor `discount_clawback_share`: both non-fall-through tiers
are compound, and the second conjunct of each is "and the account carries a recorded past-due date". That conjunct
is true of **every** account that can reach this policy's write, so the ladder does not divide the policy's
customers on it — it restates the policy's own scope.
*Root cause.* The conjunct was added to make the ladder read as multi-source, but the policy's scope already
entails it.
*Evidence.* Rule of `agronomy_ext_arrears_service_charge`: *"Where two or more discounts stand granted on the
account over the ten statement months before the handling date **and the account carries a recorded past-due
date**, the share added back is instead the whole of them. Where one discount stands granted on the account over
those months **and the account carries a recorded past-due date**, the share added back is instead half of them."*
`compute`: `clawback_share_pct: K('clawback_full_pct') if (discount_count >= K('repeat_discount_count') and
F('past_due_since') != '') else (…)`. Base `agronomy_credit_standing`: *"An account is flagged past due once an
invoice has stood unpaid for the programme's past-due trigger in calendar days beyond its due date … the flag comes
off only when nothing on the account is overdue."* Base `agronomy_finance_charge`: *"A service charge is assessed on
an invoice still unpaid after its grace period."* On every programme that carries a non-zero
`finance_charge_monthly_pct` — Standard 30-Day, Seasonal Terms, Full Acre, Precision Partner —
`past_due_trigger_days` is `1` while `finance_charge_grace_days` is `10`, `15`, `15` and `20`; the programmes with a
zero monthly rate (Cash Purchase, Early Pay Prepay) assess no charge at all. So an account can only reach this write
after standing past due for at least ten days, by which time `past_due_since` is necessarily recorded and, while
anything is still overdue, cannot have come off. The `compute` itself presupposes this: the fall-through tier of
`overdue_clock_anchor` evaluates `DAYS(F('past_due_since'), NOW)`, which has no value at all on a blank field.
*Demonstrated consequence.* The conjunct partitions nobody; the ladder is effectively single-condition on
`discount_count`, and the factor's multi-source appearance is bought with a conjunct that is entailed by the
policy's scope rather than read off the customer's records. Numeric consequence for the one task that carries this
policy is demonstrated in `0.md` § `factor_weight`.
*Affected artifact.* `env/env_0003_farm_supply_and_grain_cooperative/tasks/crop_input_desk/agronomy.extended.yaml`,
`extended_policies[1]` (`agronomy_ext_arrears_service_charge`) — `rule` (the two clawback sentences),
`compute[clawback_share_pct]`, `factors[discount_clawback_share].ladder`. Bears on **task 0** only.
*Relation to previous revisions.* First revision; no prior audit exists for this difficulty.

**OBS-1 — observation (rule wording): "is set against that balance" covers a term that is added.**
`agronomy_ext_arrears_service_charge`'s rule says *"Every service charge already standing on the account, every
payment posted to it, every credit memo written on it and every discount granted on it is set against that
balance, whatever the invoice it was written against."* Three of those four ledger kinds carry negative `amount`
and reduce the balance; the fourth (`agronomy_finance_charge_assessed`) carries a positive `amount` and increases
it, and `compute` adds it (`overdue_balance: RND(matured_charges + charges_standing + payments_standing +
credits_standing + discounts_standing, 2)`). The same author writes the parallel sentence in
`agronomy_ext_arrears_settlement_payment` with explicit signs ("… **less** every payment posted to the account …"
then "the settlement base is the product balance **plus** the share carried in of the service charges standing").
The compute reading is the one the base charter fixes (`agronomy_finance_charge_assessed` is declared
`account: input_receivable, direction: in`), so I do not treat the sentence as admitting a second defensible
reading, but it is the loosest sentence in the charter. Bears on task 0.

**OBS-2 — observation: "past the programme's terms" is implemented as a fixed six statement months.**
Both `agronomy_ext_arrears_service_charge` and `agronomy_ext_arrears_settlement_payment` define the matured balance
as *"everything invoiced to the account that has run past the programme's terms, which is every delivery invoiced
to it apart from those invoiced within the six statement months before the handling date"*, implemented as
`K('terms_months') = 6` for every programme. The programmes this policy can apply to carry `terms_days` of 30, 180,
300 and 330, so the appositive matches only the Seasonal Terms programme. On task 0's world (Seasonal Terms, 180
days) the two readings pick out the same four invoices and the same total, so no second number follows; on any
other programme they would diverge. Bears on task 0.

**OBS-3 — observation: edge A's `condition` is narrower than its `policy_source`.**
`policy_source` says "every credit memo owed for **product** that has come back to the plant"; `condition` says
"every credit memo owed for **crop protection product** that has come back to the plant". The sentence is therefore
broader than the edge it grounds. Because `agronomy_ext_crop_protection_return_credit` is the only extended policy
in this charter that writes a credit memo, the reader resolves both to the same write and no second reading arises.

**OBS-4 — observation: `finance_charge_grace_days` serves two different roles across base and extended.**
Base `agronomy_finance_charge` counts the grace period *from the due date of the invoice* as the gate on whether a
charge may be assessed. `agronomy_ext_arrears_service_charge` keeps that gate but additionally subtracts a "days of
grace" figure from an overdue-day count anchored on the account's past-due date, the latest posted charge or the
latest posted payment. Both readings agree that a charge is due whenever the extended policy fires; the deduction
sits inside the declared supersession of the charge-formula sentence. No second answer follows.

**OBS-5 — observation: `program_rebate_threshold_acres` measures enrolled acres in base and applied acres in
extended.** Base `agronomy_account_maintenance` / `agronomy_discount_schedule` tie the parameter to the acres the
member has **enrolled**; `agronomy_ext_season_volume_discount`'s `applied_acre_bonus` tiers on the acres the
cooperative has **applied** for them. The base programme rebate is written by no task tool and is not a scored
quantity, so no scored number is affected. Bears on task 1.

**OBS-6 — observation: the prepay booking tool writes no locked price.** Base `agronomy_prepay_program` says *"The
booking locks the price of the product it names, so the line drawn against it prices at the booked price however
the list has moved"*, and the base event `agronomy_prepay_booked` carries `unit_price` and `quantity`.
`book_prepay_commitment_189dfe27` takes only `account_id`, `order_id`, `product_name` and `booking_amount` and
writes neither, so the row it lands cannot later be priced against. Not a scored quantity on either task. Bears on
task 1.

**OBS-7 — observation: crediting a return at the highest price ever invoiced.**
`credit_pricing_basis` tier 2: *"Where no drawdown against a prepay booking stands on the account over those months
and more than one crop protection delivery has been invoiced on the account over those months, the unit price the
credit is computed at is instead the highest unit price at which crop protection has ever been invoiced on the
account."* Where the returned lot cannot be identified among several deliveries, a supplier normally credits at the
invoiced price of the line it is written against, or at the lowest of the candidates; crediting at the **highest**
price ever paid runs against the cooperative's own interest and is not an obvious published term. It is defensible
for a member-owned cooperative as a member-favourable identification rule, and the tier is distinct in outcome and
rests on seeded ledger rows, so I record it as an observation rather than a red light. Bears on task 0.

**OBS-8 — observation: the return handling figure is quoted off unrelated delivery-fee parameters.**
`return_handling_figure`'s three tiers are the programme's `split_load_fee_usd` ("charge for splitting one order
across two fields or two delivery days"), `delivery_minimum_charge_usd` ("charge on deliveries under the minimum
order") and `after_hours_delivery_fee_usd` ("charge for a delivery taken outside plant hours"). The rule names them
by those descriptions while using them as a re-shelving charge on a return, so the published text tells a member
that their return handling charge is "the programme's after-hours delivery charge". The dollar figures are
plausible as return handling and the tiers are distinct, so this is parameter reuse rather than an unreal outcome.
Bears on task 0.

**OBS-9 — observation: task 1's only cross-category factor reads a category that is no difficulty.**
`applied_acre_bonus` declares `cross_difficulty: custom`. `custom` (Custom Application and Field Services) has a
full product charter and its holdings and work orders are seeded, and `check_extended` treats any other category as
cross-difficulty; but `blueprint.yaml` declares only five difficulties (grain, storage, agronomy, patronage,
energy), so nothing in task 1 reads records belonging to another *difficulty*. Task 0 is unaffected (it reads
storage, grain and patronage). Bears on task 1.

**OBS-10 — observation: a seeded patronage ledger row does not match the patronage charter's declared rate.**
`0.json` `patronage_ledger` entry `2e37bb24-…` carries `allocation_basis: input_dollars`, `patronage_units:
200000.0`, `rate_per_unit: 0.048`, `allocated_amount: 9600.0`, `cash_portion_amount: 2880.0`. The cash split is
internally correct (Class A `cash_portion_pct: 30.0` → 9600 × 30 % = 2880), but `products/patronage.yaml` gives
Class A Voting Membership `allocation_rate_input_per_dollar_usd: 0.0180`, under which
`allocated_amount = round(200000 × 0.0180, 2) = 3600.00` and the cash portion would be 1080.00. The agronomy rule
reads the **posted** cash portion off the ledger rather than recomputing it, so the scored figure is still
determinate; the inconsistency is in a field (`rate_per_unit` / `allocated_amount`) the factor does not read. Bears
on task 0.

**OBS-11 — observation: task 0's persona premise is not entailed by the account state.** See `0.md`
§ `task_independent_derivation`; recorded there because it is judged against that task's world.

## closing_checklist

Written after both tasks' `source_gt_comparison` sections were on disk. **This difficulty is NOT closed out**: the
close-out condition is "all M tasks PASS on all four relationships", and task 0 carries a `SOURCE-FACTOR RED`
(RED-1). The checklist is recorded item by item so that what does hold is on record and what blocks is named.

| item | state |
| --- | --- |
| per-task audit files correspond one-to-one with the tasks and `_difficulty.md` sits alongside them | **holds** — `0.md`, `1.md`, `_difficulty.md` in `env/env_0003_farm_supply_and_grain_cooperative/audits/policy_task/crop_input_desk/` |
| old revisions traceable | **holds vacuously** — this is revision 1; no prior audit of this difficulty exists |
| every comparison section carries a PASS | **does not hold** — `1.md` § `source_gt_comparison` is PASS on all four; `0.md` is PASS on three and `SOURCE-FACTOR RED` on "factors bear weight" |
| this difficulty's extended policies fully covered | **holds** — task 0 claims 1, 2, 3; task 1 claims 4, 5; union = all five |
| the M tasks' scopes pairwise disjoint, each spanning a whole tree | **holds** — {1, 2, 3} ∩ {4, 5} = ∅, and each scope is exactly one root plus its prerequisite problems |
| task tools and GT closed | **holds** — five tools, five `computes` names, each claimed once; every gold argument traced to a record, a persona line or a computation whose value this audit independently reproduced |
| each task tool uses an independently generated, frozen uuid8 | **holds** — `6859ca91`, `aaf992aa`, `ad47b93a`, `cc5ed557`, `189dfe27`; no shared prefix, tail, sequence or adjacency |
| every task's tree has 1–3 prerequisite problems | **holds** — task 0: 2; task 1: 1 |
| at least max(n − 1, 1) `value_input` edges | **holds** — task 0: 2 of 2 edges, floor 1; task 1: 1 of 1, floor 1 |
| at least one problem resolved by an `owner=user` tool | **holds** — task 0 root `post_member_arrears_payment_ad47b93a`; task 1 root `book_prepay_commitment_189dfe27` |
| no cycle, and the difficulty's `prerequisite` edges together still a DAG | **holds** — 1 → 2 → 3 and 4 → 5; no cross-task reference, so the union is a DAG |
| every computation declares a self-sufficient baseline giving a definite number ≠ gold | **holds** — 12,790.68 vs 15,196.00; 3,769.67 vs 320.20; 77,433.82 vs 37,030.00; 1,295.60 vs 5,083.25; 233,385.75 vs 228,137.43 |
| 4–6 factors per computation, ≥ 2 `parameter` and ≥ 1 `method` | **holds** — 4 (3 p / 1 m), 6 (4 p / 2 m), 6 (5 p / 1 m), 4 (3 p / 1 m), 4 (3 p / 1 m) |
| per task ≥ 1 multi-source and ≥ 1 cross-difficulty factor | **holds**, with OBS-9 against task 1 (its only cross-category factor reads `custom`, a category with no difficulty of its own) |
| every ladder ≥ 3 tiers, stated in full in its rule, tiers distinct in outcome | **holds** — 24 ladders, each of three tiers, each tier's condition and outcome stated in the `rule` and implemented in `compute`, no two tiers of any ladder sharing a value or method |
| every ladder's conditions and outcomes are ones that line of business actually holds | **does not hold** — RED-1 (`discount_clawback_share`); OBS-7 and OBS-8 recorded alongside it as observations |
| every factor proved to bear weight on its task's world | **holds** — all 24 substitutions move the scored value; 22 figures in task 0 and 12 in task 1 recomputed independently and matched GT exactly |
| instantiation-stage gates re-run on the final form | **deferred** — close-out is blocked by RED-1, so the artifacts are not in final form; the entry-condition snapshot supplied with the brief (all seven gates green, `check_traceability` deliberately unrun pending the KB) is cited, not re-run |

**Difficulty verdict: does not pass the source-layer audit.** Task 1 passes on all four relationships. Task 0
passes on policy self-consistency, the problem tree and unique solution, and fails on factors bearing weight
through RED-1. Eleven observations (OBS-1 … OBS-11) are on record and are not grounds for rework.

---

# revision_2 — re-audit, charter-global

## re_audit_frozen

| item | round 1 | round 2 | re-derived? |
| --- | --- | --- | --- |
| `agronomy.extended.yaml` | `509d0471c9ee0c73` | **`b03709eb426fd7f7`** | **yes, in full** |
| `task_tools.py` | `fb62107a7cae45c5` | `fb62107a7cae45c5` (unchanged) | carried forward by reference on those two hashes |
| `tasks/0.json` | `48edcbe2ddf72740` | **`8205a9fff1926ae6`** | per-task sections re-derived in `0.md` § revision_2 |
| `tasks/1.json` | `800f8015bd108005` | **`adcb595da50cc309`** | per-task sections re-derived in `1.md` § revision_2 |
| masked view r2/0.json | `a3c0c7eb8d396a72` | **`3a5e353eeffcfe3a`** | — |
| masked view r2/1.json | `e26b92027be00f8f` | **`7463e9cb4ff4eed4`** | — |
| `blueprint/products/agronomy.yaml` | `66127eecc1f99b7b` | `66127eecc1f99b7b` (unchanged) | base section re-verified byte-for-byte |

This round is **not a blind derivation**: round 1's GT is already known to this auditor, and round 1's
`source_derivation_frozen` sections are left exactly as they stood. Nothing above this line was rewritten.
Grounds for re-deriving: the extended charter hash moved, so every charter-global section was re-derived in full
rather than carried forward; `task_tools.py` is byte-identical, so § `action_binding_and_uuids`'s conclusions about
the five function bodies, the five uuid8s and the docstrings are carried forward on the matching hash pair
`fb62107a7cae45c5` / `fb62107a7cae45c5`.

Entry conditions: the round-2 difficulty-wide gate block (seven gates green, `check_traceability` still deferred to
step 3) and the rebuilt masked views with their hashes came with the brief; cited, not re-run. All four hashes in
the brief match the files on disk, verified by `sha256sum`.

## what changed in the charter

| policy | change found | answers |
| --- | --- | --- |
| 1 `…return_credit` | none (params, rule, compute, factors, overwrite, cross_category all identical) | — |
| 2 `…arrears_service_charge` | clawback conjunct replaced; balance-sign sentence rewritten; `K('terms_months')` dropped for `P('terms_days') / K('statement_month_days')`; `baseline.params` rehomed to `terms_days`; edge A sentence narrowed to "crop protection product" | RED-1, OBS-1, OBS-2, OBS-3 |
| 3 `…arrears_settlement_payment` | same terms-cut change; `statement_month_days` added to `params` and `baseline.params` | OBS-2 |
| 4 `…season_volume_discount` | `applied_acre_bonus` (custom) replaced by `delivered_grain_bonus` (grain); `acre_bonus_*` params → `grain_bonus_*` plus `qualifying_delivery_bushels: 25000`; `cross_category` and `inputs` moved custom → grain | OBS-9 (and OBS-5 with it) |
| 5 `…prepay_booking_ceiling` | second `overwrite` entry added naming base's "The booking locks the price…" sentence, with a replacing sentence in the policy's own rule | OBS-6 |

## revision_2 — charter-global re-checks

### policy_conflict_scan (re-derived)

Base section **still byte-for-byte identical** to `blueprint/products/agronomy.yaml` (all ten top-level keys compare
equal after YAML load; `extended_policies` remains the only extra key). Subjects still pairwise disjoint; triggers
unchanged (`state_due` on 1, 2, 4; `on_request` on 3, 5); the two `on_request` policies are still exactly the two
`owner=user` writes. Task scopes re-read from `charter_scope`: task 0 = {1, 2, 3}, task 1 = {4, 5} — still pairwise
disjoint and jointly complete over all five extended policies. Cross-category read boundaries re-checked against
every `compute` call: policy 1 → `custom`, policy 2 → `storage`, policy 3 → `grain` + `patronage`, **policy 4 →
`grain` (was `custom`)**, policy 5 → none; each declared block matches its calls exactly and no block is declared
without a call.

**One new conflict found — RED-2 below.**

### rule_compute_equivalence (re-derived)

Re-run mechanically over all five policies on the new file: every `compute` binding has a `compute_basis` entry and
every `compute_basis` key is a binding (no orphans); **every sentence of every `compute_basis` entry and of every
`baseline.rule` appears verbatim in its policy's own `rule`** — zero misses; every `decides` names a real binding;
every factor's `bindings` name real bindings; binding sets remain pairwise disjoint within each policy. Ternary
count still equals factor count per policy (4, 6, 6, 4, 4), so no tier lives only in `compute`.

The two rewritten quantities check out:

- `charges_in_terms: SUM(…, within_months=P('terms_days') / K('statement_month_days'), …)` is quoted back by
  *"every delivery invoiced to it apart from those invoiced within the statement months the programme's terms
  cover, the programme's terms in days being taken over a statement month of thirty days"* — which now reads off
  the programme instead of a fixed constant. On Seasonal Terms it is 180/30 = 6, so task 0's figures are
  unchanged; on Standard 30-Day it is 1, on Full Acre 10, on Precision Partner 11. OBS-2 is properly closed and
  the sentence is now true of every programme, not one.
- `clawback_share_pct: … and overdue_balance >= P('suspension_balance_threshold_usd')` is quoted back by *"and the
  overdue balance has reached the programme's suspension threshold"*. See RED-1 CLOSED below.

### action_binding_and_uuids (carried forward)

`task_tools.py` is byte-identical (`fb62107a7cae45c5` both rounds), and the five `(target_tool, computes)` pairs are
unchanged in the new charter. Round 1's conclusions — five tools each claimed once, five independently generated
uuid8s (`6859ca91`, `aaf992aa`, `ad47b93a`, `cc5ed557`, `189dfe27`), no tool weighing a policy condition, no
docstring naming another tool or disclosing a prerequisite — are **carried forward by reference on that matching
hash pair**, not re-derived.

### prerequisite_graph and prerequisite_sentences (re-derived)

Still three edges, all `value_input`, all `form: state`, all with no `fallback_reason` (correctly absent):
2 ← 1 on `overdue_balance`, 3 ← 2 on `charges_standing`, 5 ← 4 on `prior_net_spend`. Graph still 1 → 2 → 3 and
4 → 5, acyclic, no cross-task reference. Every `policy_source` re-checked as a verbatim sentence of the **blocked**
policy's own `rule`: all three located. `resolved_by` still the depended-on policy's `target_tool` in each case, and
each still the only tool in the difficulty that creates its row type.

**OBS-3 CLOSED.** Edge A's sentence now reads *"The service charge on a crop input account is worked out only once
every credit memo owed for **crop protection product** that has come back to the plant stands written against that
account."* — verbatim in policy 2's rule, verbatim in `prerequisite[0].policy_source`, and verbatim in
`tasks/0.json` `prerequisite_closure.edges[1].policy_source`. It now carries exactly the scope its `condition`
carries; the four-point test still passes (ordering connective "only once", state form, no tool/policy id/
snake_case/row id), and the single write that brings the state about is still `issue_return_credit_6859ca91`.

No rule states a cross-problem order grounding no declared edge; no depended-on rule restates a prerequisite
sentence; no base rule sentence grounds any edge.

### override_declarations (re-derived)

Sentence-by-sentence sweep re-run against each `base_policy_refs` entry on the new file. Round 1's conclusions hold
for policies 1, 2, 3 and 4, with OBS-5 now moot (the factor that reused `program_rebate_threshold_acres` no longer
exists). Policy 5 gained a second declared override — and with it a new undeclared one.

**OBS-6 CLOSED as declared, but incompletely — see RED-2.** Policy 5 now names base `agronomy_prepay_program`'s
sentence *"The booking locks the price of the product it names, so the line drawn against it prices at the booked
price however the list has moved by delivery."* in `overwrite[1].superseded_clause` and states the replacement in
its own rule: *"A booking taken that way is a money commitment against the product the request names and locks no
unit price; the product is priced at the list in force on the day each delivery leaves the plant."* That squares
the policy with `book_prepay_commitment_189dfe27`, which writes no `unit_price`. What it does not square is the
**same provision stated a second time in a different base policy**.

### factor_ladders (re-derived)

Counts unchanged and still inside every bound: policy 1 — 4 factors (3 `parameter`, 1 `method`); policy 2 — 6
(4 / 2); policy 3 — 6 (5 / 1); policy 4 — 4 (3 / 1); policy 5 — 4 (3 / 1). All 24 ladders still have three
pairwise-disjoint tiers, every tier stated in the `rule` with its condition and its value or method and
implemented in `compute`, **every fall-through still exactly the factor's `baseline`** (re-checked mechanically,
zero mismatches), no two tiers of any ladder sharing a value or method, and every label still honest.

`cross_difficulty` declarations now read: policy 1 → `custom`, policy 2 → `storage`, policy 3 → `grain` and
`patronage`, **policy 4 → `grain`**, policy 5 → none. Per task: task 0 has four cross-category factors of which
three (`storage`, `grain`, `patronage`) read categories that own a difficulty; **task 1 now has one, and it reads
`grain`, which owns the grain_marketing_desk difficulty** — OBS-9 closed.

## revision_2 — findings

**RED-1 — CLOSED.**
The vacuous conjunct is gone. Both non-fall-through tiers of `discount_clawback_share` now read *"and the overdue
balance has reached the programme's suspension threshold"*, implemented as
`overdue_balance >= P('suspension_balance_threshold_usd')`, and the change is carried through `rule`,
`compute[clawback_share_pct]`, `compute_basis.clawback_share_pct` and `factors[discount_clawback_share].ladder`.
*Why the new conjunct genuinely divides.* Base `agronomy_credit_standing` fixes the threshold as a level an account
may or may not have reached: *"Buying is suspended when the oldest overdue invoice reaches the programme's
suspension trigger in days, or at any time once the overdue balance reaches the programme's suspension threshold,
whichever comes first; the threshold bites on its own, so a large balance one day overdue can suspend an account
that the day count alone would not."* On the four programmes that can carry this write the threshold is
25,000 / 75,000 / 150,000 / 250,000 USD, while a charge becomes due on any unpaid invoice past 10–20 days of
grace. A member 20 days past due on a 5,000 USD invoice on Seasonal Terms reaches the write and is far below the
threshold, so the ladder now separates customers on a fact read off their own ledger. Round 1's argument against
the old conjunct — that `past_due_since` is necessarily recorded before any charge can be assessed — does not
transfer to a balance level. The conjunct also remains multi-source: `discount_count` reads the discount rows and
`overdue_balance` reads the invoice, payment, credit and discount rows.
*Numbers unchanged, as claimed.* On task 0's world `overdue_balance = 103,991.02 ≥ 75,000.00` and
`discount_count = 2`, so tier 1 still fires, `clawback_share_pct` is still 100.0 and `charge_base` is still
105,956.26 — independently recomputed in `0.md` § revision_2.

**RED-2 — `SOURCE-POLICY RED` (new, introduced by the OBS-6 fix). The prepay pricing rule is now stated twice in
the charter and the two statements contradict each other.**
*Symptom.* `agronomy_ext_prepay_booking_ceiling` now declares that a prepay booking locks no price and that
deliveries against it price at the list of the day. It names, and supersedes, the sentence that says otherwise in
base `agronomy_prepay_program`. The identical provision is stated a second time in base
`agronomy_evt_invoicing`, which is **not** in the policy's `base_policy_refs` and is named in no `overwrite`, and
that sentence still says the opposite.
*Root cause.* The base charter states the prepay-pricing rule in two policies; the fix declared one of them.
*Evidence — the two passages, verbatim.*
Base, `blueprint/products/agronomy.yaml`, `policies[agronomy_evt_invoicing].rule`:
*"Product is priced at the list price in force on the day of delivery, **except where the line draws against a
prepay booking, which prices at the booked price however the list has moved**."*
Extended, `tasks/crop_input_desk/agronomy.extended.yaml`,
`extended_policies[agronomy_ext_prepay_booking_ceiling].rule`:
*"A booking taken that way is a money commitment against the product the request names and **locks no unit price;
the product is priced at the list in force on the day each delivery leaves the plant**."*
`extended_policies[agronomy_ext_prepay_booking_ceiling].base_policy_refs` = `[agronomy_prepay_program]`;
`overwrite` names two sentences, both of `agronomy_prepay_program`; `agronomy_evt_invoicing` is named nowhere.
*Demonstrated consequence.* In one and the same situation — an invoice line drawn against a prepay booking taken
under this policy — the two passages reach different conclusions: the base clause prices the line at the price the
booking locked, the extended clause prices it at the list in force on the delivery day. Both are in force, because
the base section is carried into this difficulty's charter verbatim and is rendered alongside the extended
policies; a reader who follows the base clause and a reader who follows the extended clause bill the same delivery
at two different unit prices, with no declaration anywhere telling them which governs. **This does not move a
scored number on either task**: no task in this difficulty issues an invoice against a prepay booking, and both
tasks' scored solutions still follow uniquely (verified by independent re-derivation in `0.md` and `1.md`
§ revision_2). It is a defect of the charter's self-consistency, not of either task's arithmetic.
*Affected artifact and location.*
`env/env_0003_farm_supply_and_grain_cooperative/tasks/crop_input_desk/agronomy.extended.yaml`:
`extended_policies[4]` (`agronomy_ext_prepay_booking_ceiling`) — `rule` (the locks-no-unit-price sentence),
`base_policy_refs`, `overwrite`; against the inherited base section's
`policies[agronomy_evt_invoicing].rule` in the same file (lines carrying the base copy) and in
`blueprint/products/agronomy.yaml`. Bears on **task 1**, which claims policy 5.
*Relation to previous revisions.* New in revision 2. It did not exist in revision 1: there the extended charter
said nothing about how a prepay-drawn line prices, and the two base sentences agreed with each other. Round 1's
OBS-6 asked only that the gap between the base sentence and the tool contract be faced; the fix faced one of the
two base sentences.

**RED-3 — `SOURCE-FACTOR RED` (new, introduced by the OBS-9 fix). The grain rows the new cross-difficulty factor
reads contradict the grain charter's own net-bushel rule.**
*Symptom.* `delivered_grain_bonus` decides its tier from
`XSUM('grain','grain_ledger','net_bushels', within_months=14, date_field='delivery_date',
event_type='grain_delivery_applied')`. The three `grain_delivery_applied` rows seeded into `tasks/1.json` for this
purpose carry `net_bushels` figures that the grain charter's own formula does not produce from their own
`gross_bushels` and `moisture_pct`.
*Root cause.* The rows were written to a shrink the grain charter does not define; one of them applies shrink at
the moisture base, where the charter says there is none.
*Evidence.* `blueprint/products/grain.yaml`, `policies[grain_evt_delivery_application]`:
formula `net_bushels: round(gross_bushels * (1 - shrink_pct_per_moisture_point * max(0, moisture_pct -
moisture_base_pct) / 100), 2)`, and the rule sentence *"Net bushels are gross bushels less moisture shrink:
bushels above the moisture base shrink by the shrink factor for each whole and part point above base … and grain
at or under base shrinks by nothing and is never credited back."* Basis Fixed Contract carries
`moisture_base_pct: 15.0` and `shrink_pct_per_moisture_point: 1.18`, and the rows are yellow corn, whose base is
the catalogue base of 15.0.

| seeded row | gross | moisture | seeded `net_bushels` | charter formula gives |
| --- | --- | --- | --- | --- |
| `grain_ledger.ce544fba-…` T-3061204, 2025-10-28 | 13,342.0 | 15.2 | 13,200.00 | **13,310.51** |
| `grain_ledger.d12a64e1-…` T-3062877, 2025-11-06 | 14,201.0 | 15.1 | 14,050.50 | **14,184.24** |
| `grain_ledger.f0885162-…` T-3064130, 2025-11-19 | 11,370.0 | **15.0** | 11,249.50 | **11,370.00** (at base, shrink is nil) |

*Demonstrated consequence.* The binding the ladder consumes is `delivered_bushels = 38,500.00`, where the same
three rows read through the grain charter's own rule give **38,864.75**. The third row is the plainest: it sits
exactly at the moisture base, where the grain charter states in terms that grain "shrinks by nothing", yet the
seed takes 120.5 bushels off it. The cross-difficulty evidence this factor rests on is therefore not evidence the
grain product line would have produced, which is the test that cross-difficulty factors have to meet. On this
world the tier does **not** flip — 38,500.00 and 38,864.75 are both at or above the 25,000-bushel qualifying
volume — so the scored discount stays 5,083.25; the defect is that the factor's records contradict the charter
they are supposed to come from, not that the arithmetic moves.
*Affected artifact and location.* `env/env_0003_farm_supply_and_grain_cooperative/tasks/crop_input_desk/tasks/1.json`,
`initial_state.grain_ledger.ce544fba-8d5f-4276-93a5-7da43640d984`,
`…d12a64e1-ae74-418b-98b8-e9148a9724d5` and `…f0885162-b6ba-4061-9426-84ec8c1a538b`
(`net_bushels` against `gross_bushels` / `moisture_pct`), read by
`agronomy.extended.yaml` `extended_policies[3].compute[delivered_bushels]` and
`factors[delivered_grain_bonus]`; asserted in `tasks/1.json` `computations[0].factor_trace`
("total 38,500.00 net bushels").
*Relation to previous revisions.* New in revision 2, and a regression in seed quality: the cross-category grain row
this difficulty carried in revision 1 (`tasks/0.json` `grain_ledger.fb54d3d6-…`, soybeans, 8,000.0 gross,
`moisture_pct: 12.4` against a soybean base of 13.0, `net_bushels: 8000.0`) **is** charter-consistent, and
revision 2's OBS-10 fix established the same standard for the patronage rows. The three new grain rows do not meet
it.

**Round-1 observations — state after the rework.**

| id | reworker's claim | verified state |
| --- | --- | --- |
| OBS-1 | FIXED | **CLOSED.** The sentence now reads *"That balance is reduced by every payment posted to the account, by every credit memo written on it and by every discount granted on it, whatever the invoice each was written against, and is increased by every service charge already standing on it."* Signs are explicit and match `compute[overdue_balance]`; the second reading (103,991.02 against 102,499.18) is gone. Carried into `baseline.rule` too. |
| OBS-2 | FIXED | **CLOSED.** `K('terms_months')` is gone from both policies' `params`; the cut now reads `P('terms_days') / K('statement_month_days')`, `baseline.params` names `terms_days` (policy 2) and `terms_days` + `statement_month_days` (policy 3), and the rule sentence states the division. 180/30 = 6 on Seasonal Terms, so no figure on task 0 moved. |
| OBS-3 | FIXED | **CLOSED.** Verified above in § `prerequisite_sentences`, and propagated to `tasks/0.json` `prerequisite_closure.edges[1]`. |
| OBS-4 | NO CHANGE | **Stands as an observation**, unchanged and correctly so: `finance_charge_grace_days` still serves as a gate in base and as a deduction in extended, and both readings still agree that a charge is due on task 0's world. Not grounds for rework. |
| OBS-5 | resolved via OBS-9 | **MOOT.** `applied_acre_bonus` no longer exists, so nothing reuses `program_rebate_threshold_acres` against applied acres. The base programme rebate is untouched and still unscored. |
| OBS-6 | FIXED by declaration | **Half closed — see RED-2.** The declaration against `agronomy_prepay_program` is correct and the extended rule now matches the tool. The identical base sentence in `agronomy_evt_invoicing` was not declared and now contradicts it. |
| OBS-7 | ground published | **Stands as an observation.** The rule is unchanged in substance; crediting a return at the highest crop-protection price ever invoiced is still the member-favourable reading. No number moved. |
| OBS-8 | ground published | **Stands as an observation.** The three handling-figure tiers still resolve to `split_load_fee_usd`, `delivery_minimum_charge_usd` and `after_hours_delivery_fee_usd`. No number moved. |
| OBS-9 | FIXED | **CLOSED** as to the difficulty question: task 1's cross-difficulty factor now reads `grain`, which owns the grain_marketing_desk difficulty, and the seed rows were swapped accordingly. The replacement introduced RED-3. |
| OBS-10 | FIXED | **CLOSED.** `tasks/0.json` `patronage_ledger` now carries `rate_per_unit: 0.018` — Class A Voting Membership's `allocation_rate_input_per_dollar_usd` exactly — with `patronage_units` moved 200,000.0 → 533,333.33 on both rows, so `round(533333.33 × 0.018, 2) = 9600.00` and `round(533333.33 × 0.018 × 30/100, 2) = 2880.00` reproduce the seeded `allocated_amount` and `cash_portion_amount`. The charter formula and the row now agree, and task 0's `patronage_credit` is unchanged at 2,880.00. |
| OBS-11 | FIXED | **CLOSED.** Verified in `0.md` § revision_2. |
| Task 1 weekday slip | FIXED | **CLOSED.** Both persona mentions now read "Tuesday", matching `agronomy_orders.e800110d-….requested_date = "2026-10-20"`, a Tuesday. |
| Prepay-balance stamp | NO CHANGE | **Stands as an observation**, correctly: `agronomy_accounts.5191ed92-….prepay_balance = 7665.0` is a declared current-state field of the holding that names no ladder outcome. Not grounds for rework. |

**OBS-12 — observation (new).** `tasks/0.json`'s patronage rows now carry 533,333.33 input-dollar units for fiscal
2025 on an 1,180-acre operation (≈ 452 USD/acre), against 312,289.50 of seeded fiscal-2026 spend on the same
account (≈ 265 USD/acre). Fiscal 2025 is outside the seeded invoice history so nothing contradicts anything, and
the factor reads `cash_portion_amount` rather than the units; recorded only because the OBS-10 fix chose to move
the units rather than the allocated amount.

## revision_2 — closing checklist

| item | state |
| --- | --- |
| every comparison section carries a PASS | **does not hold** — `0.md` § revision_2 is PASS on all four; `1.md` § revision_2 is `SOURCE-POLICY RED` (RED-2) and `SOURCE-FACTOR RED` (RED-3) |
| RED-1 closed | **yes** — verified above and in `0.md` § revision_2 |
| nothing regressed that round 1 passed | **one regression** — RED-3: the cross-category seed rows were charter-consistent in revision 1 and are not in revision 2 |
| no new defect | **does not hold** — RED-2 and RED-3 are both new in revision 2 |
| extended policies fully covered, scopes pairwise disjoint | holds — {1, 2, 3} and {4, 5} |
| task tools and GT closed; uuid8s independent and frozen | holds — `task_tools.py` unchanged; carried forward on the matching hash pair |
| 1–3 prerequisite problems, ≥ max(n−1,1) `value_input` edges, ≥ 1 `owner=user` problem, no cycle | holds — task 0: 2 problems, 2 edges, user root; task 1: 1 problem, 1 edge, user root |
| self-sufficient baselines giving definite numbers ≠ gold | holds — 12,790.68 / 3,769.67 / 77,433.82 / 1,295.60 / 233,385.75 against 15,196.00 / 320.20 / 37,030.00 / 5,083.25 / 228,137.43 |
| 4–6 factors, ≥ 2 `parameter`, ≥ 1 `method` per computation; ≥ 1 multi-source and ≥ 1 cross-difficulty per task | holds — and task 1's cross-difficulty factor now reads a category that owns a difficulty |
| every ladder ≥ 3 tiers stated in full, tiers distinct in outcome, conditions and outcomes ones the business holds | holds for 24 of 24 ladders; RED-1's vacuous conjunct is gone |
| every factor bears weight against an honest baseline | holds — all 24 substitutions move the scored value; all 34 figures independently recomputed and matched |
| instantiation-stage gates re-run on the final form | **deferred** — close-out is blocked by RED-2 and RED-3; the round-2 snapshot supplied with the brief is cited, not re-run |

**Difficulty verdict, revision 2: still does not pass the source-layer audit.** Task 0 now passes on all four
relationships; task 1, which passed in round 1, now carries two red lights, both introduced by the round-2 rework.

---

# revision_3 — re-audit, charter-global

## re_audit_frozen

| item | round 2 | round 3 | re-derived? |
| --- | --- | --- | --- |
| `agronomy.extended.yaml` | `b03709eb426fd7f7` | **`f06d6a864ab9b2db`** | **yes, in full** |
| `task_tools.py` | `fb62107a7cae45c5` | `fb62107a7cae45c5` (unchanged throughout) | carried forward by reference on that hash pair |
| `tasks/0.json` | `8205a9fff1926ae6` | **`f6ed40c91f7bb30b`** | per-task sections re-derived in `0.md` § revision_3 |
| `tasks/1.json` | `adcb595da50cc309` | **`5263b5d7954c8894`** | per-task sections re-derived in `1.md` § revision_3 |
| masked view 0.json | `3a5e353eeffcfe3a` | `3a5e353eeffcfe3a` (**byte-identical**) | task 0's world did not move |
| masked view 1.json | `7463e9cb4ff4eed4` | **`ed61f49c961afb61`** | task 1's world re-derived in full |
| `blueprint/products/agronomy.yaml` | `66127eecc1f99b7b` | `66127eecc1f99b7b` | base section re-verified byte-for-byte |
| `blueprint/products/grain.yaml` | — | `e10c3fdd9e03dba1`, mtime 2026-09-18 07:13 | untouched by the rework (which wrote at 09:52–09:55); used as the authority for RED-3 |

Revisions 1 and 2 are left exactly as they stand. Grounds for re-deriving: the extended charter hash moved, so every
charter-global section was re-derived in full; `task_tools.py` is byte-identical for the third round running, so
§ `action_binding_and_uuids`'s conclusions (five tools each claimed once, five independently generated uuid8s, no
tool weighing a policy condition, no docstring disclosing a prerequisite) are **carried forward by reference on the
matching hash pair**. I did not run any instantiate gate script; the round-3 snapshot supplied with the brief is
cited, and `replay_tasks.py` was deliberately not run because it writes back to the task JSONs.

Entry conditions complete: the round-3 gate block (seven gates green, `check_traceability` still deferred) and the
rebuilt masked views came with the brief, and all six hashes above were verified against the files on disk.

## what changed in round 3

| artifact | change | answers |
| --- | --- | --- |
| policy 5 `…prepay_booking_ceiling` | pricing sentence rewritten from a flat contradiction into a two-branch narrowing; `agronomy_evt_invoicing` added to `base_policy_refs`; a third `overwrite` entry naming that policy's prepay exception clause; the sentence removed from `baseline.rule` | RED-2 |
| `tasks/1.json` `grain_contracts.d090bdf7-…` | `cash_price_per_bushel` 4.42 → 4.6113 | RED-3 |
| `tasks/1.json` `grain_ledger` | 7 rows out, 10 in: three tickets' gross weights re-derived from the shrink formula (nets kept); both settlements re-struck at the contract flat price with checkoff and per-unit retain lines added; the invented freight deduction removed; the check payment moved 2025-12-22 → 2025-12-23; `price_per_bushel` and `net_amount` fields populated | RED-3 |
| policies 1–4, base section, `task_tools.py` | unchanged | — |

## revision_3 — charter-global re-checks

### policy_conflict_scan (re-derived)

Base section **still byte-for-byte identical** to `blueprint/products/agronomy.yaml` (all ten top-level keys equal
after YAML load; `extended_policies` still the only extra key). Subjects still pairwise disjoint; triggers
unchanged; scopes still task 0 = {1, 2, 3} and task 1 = {4, 5}, pairwise disjoint and jointly complete.
Cross-category read boundaries unchanged and still matching their `compute` calls exactly: 1 → `custom`,
2 → `storage`, 3 → `grain` + `patronage`, 4 → `grain`, 5 → none.

`base_policy_refs` across the suite: `agronomy_returns_and_credits` (1); `agronomy_finance_charge` (2 and 3);
`agronomy_payment_application`, `agronomy_credit_standing` (3); `agronomy_discount_schedule` (4);
`agronomy_prepay_program`, **`agronomy_evt_invoicing`** (5). The new reference collides with nothing: no other
extended policy cites `agronomy_evt_invoicing`, and the two tasks' scopes are unaffected.

**No conflict remains.** RED-2 closed — see § `findings`.

### rule_compute_equivalence (re-derived)

Re-run mechanically over all five policies on the new file: no binding without a `compute_basis` entry and no basis
key that is not a binding; **every sentence of every `compute_basis` entry and of every `baseline.rule` appears
verbatim in its own policy's `rule`** — zero misses; every `decides` and every `bindings` entry names a real
binding; binding sets pairwise disjoint within each policy; every factor's fall-through is exactly its `baseline`;
ternary count still equals factor count per policy (4, 6, 6, 4, 4). **Zero issues.**

The round-2 fixes are all still in place and were re-read on the new file: `charges_in_terms` in policies 2 and 3
is still `within_months=P('terms_days') / K('statement_month_days')`; `clawback_share_pct` in policy 2 still
carries `and overdue_balance >= P('suspension_balance_threshold_usd')`; policy 4 still declares
`delivered_grain_bonus` with `cross_difficulty: grain`, `qualifying_delivery_bushels: 25000` and the
`XSUM('grain','grain_ledger','net_bushels', …)` binding.

Policy 5's `compute` is untouched by the round-3 edit — the rewritten sentence is a normative statement about how a
later delivery prices, not an input to `booking_amount` — and it is correctly absent from `baseline.rule`, which is
the self-sufficient standard method for the scored quantity.

### action_binding_and_uuids (carried forward)

`task_tools.py` byte-identical for the third round; the five `(target_tool, computes)` pairs unchanged. Carried
forward on the matching hash pair, not re-derived.

### prerequisite_graph and prerequisite_sentences (re-derived)

Unchanged: three edges, all `value_input`, all `form: state`, all with `fallback_reason` correctly absent;
2 ← 1 on `overdue_balance`, 3 ← 2 on `charges_standing`, 5 ← 4 on `prior_net_spend`; graph 1 → 2 → 3 and 4 → 5,
acyclic. All three `policy_source` strings re-checked as verbatim sentences of the **blocked** policy's own `rule`
— all three located. Round 2's OBS-3 narrowing ("crop protection product") survives intact in the rule, in
`prerequisite[0].policy_source` and in `tasks/0.json`. Each `resolved_by` is still the only tool in the difficulty
that creates its row type.

### override_declarations (re-derived)

The sentence-by-sentence sweep was re-run against every `base_policy_refs` entry. **Every `overwrite` entry's
`superseded_clause` was verified as a verbatim substring of the named base policy's `rule`** — all eight entries
across the five policies. Rounds 1 and 2's conclusions hold unchanged for policies 1–4.

Policy 5 now carries three entries, and the third is the RED-2 fix:

- `agronomy_prepay_program` / "A booking must reach the programme's minimum…" — unchanged.
- `agronomy_prepay_program` / "The booking locks the price of the product it names…" — replacement text updated to
  the new two-branch sentence.
- **`agronomy_evt_invoicing` / "except where the line draws against a prepay booking, which prices at the booked
  price however the list has moved"** — new, verbatim in that base rule.

Naming the **clause** rather than the whole sentence is the right granularity here and is worth recording as
sound: the remainder of the base sentence, *"Product is priced at the list price in force on the day of
delivery"*, is one the extended agrees with and needs to keep in force, and superseding the whole sentence would
have withdrawn it. Also noted and correct: policy 5's rule now carries a sentence about how an
`agronomy_invoice_issued` line prices, which is `agronomy_evt_invoicing`'s subject rather than policy 5's own
(`agronomy_prepay_booked`). Reaching outside its own subject is unavoidable here — the base charter states the
prepay-pricing rule in the invoicing policy, so a policy that changes what a booking means has to declare it there
— and it is now declared through both `base_policy_refs` and `overwrite`.

**The `soil_test_before_prescription` gate is untouched**, as the reworker claimed and as I verified
mechanically: `agronomy_evt_invoicing`'s eligibility condition is *"Prescription products are not released at all
on programmes that require a current soil test until one is on file."*, and neither it nor the superseded clause
contains the other. The gate is inherited in full.

*(Recorded while running that check, pre-existing and inconsequential: policy 3's declared supersession of
`agronomy_credit_standing`'s reinstatement sentence is also the `condition` of that base policy's
`credit_department_records_reinstatement` eligibility gate, so the gate goes with the sentence. It applies to
`agronomy_account_suspended`, an event no task tool writes and no extended policy claims, and no task's account
stands in `suspended`, so nothing follows. It has been present since revision 1 — OBS-13 below.)*

### factor_ladders (re-derived)

Unchanged and all bounds met: 4 / 6 / 6 / 4 / 4 factors; 3 / 4 / 5 / 3 / 3 `parameter` and 1 / 2 / 1 / 1 / 1
`method`; 24 ladders of three pairwise-disjoint tiers each, every tier stated in the `rule` and implemented in
`compute`, every fall-through exactly the factor's `baseline`, no two tiers of any ladder sharing a value or
method, every label honest. `cross_difficulty`: 1 → `custom`, 2 → `storage`, 3 → `grain` + `patronage`,
4 → `grain`, 5 → none; per task, task 0 has four cross-category factors and task 1 has one, reading a category
that owns a difficulty.

## revision_3 — findings

**RED-2 — CLOSED.** The charter no longer states the prepay-pricing rule two ways.
*The rewritten sentence.* `agronomy_ext_prepay_booking_ceiling`'s rule now reads: *"A booking taken that way is a
money commitment against the product the request names and carries no booked unit price of its own, so a delivery
drawn against a booking that carries no booked unit price is priced at the list in force on the day it leaves the
plant, while a delivery drawn against a booking that does carry one is priced at that booked price."* Round 2's
version asserted flatly that deliveries against such a booking price at the list, which contradicted base outright.
The new version splits on a fact of the record — whether the booking row carries a `unit_price` — and preserves
base's exception on the branch where a booked price exists.
*Both base statements now declared.* `base_policy_refs` is `[agronomy_prepay_program, agronomy_evt_invoicing]`, and
`overwrite` carries three entries, the third naming `agronomy_evt_invoicing`'s clause *"except where the line draws
against a prepay booking, which prices at the booked price however the list has moved"* — verified verbatim in that
base rule. So even on the branch where the two could diverge, the divergence is declared sentence by sentence,
which is what check 1 asks for.
*Merged semantics are unique.* On the branch the extended adds — a booking carrying no `unit_price` — base's
exception has no price to point at, so it decides nothing and the extended supplies the only reading. On the branch
base already governed, the extended repeats base's answer. There is no situation left in which a reader following
the base clause and a reader following the extended clause bill the same delivery differently.
*The world exercises both branches, and agrees.* `tasks/1.json` carries `agronomy_invoices.018f885e-…`, a prepay
booking with `unit_price: 310.0`, and two drawdowns against it; under both readings those lines price at the booked
310.00. The booking `book_prepay_commitment_189dfe27` writes carries no `unit_price`, and under the extended branch
it prices at the list of the day. Both are consistent with the tool contract, which takes no price argument.
*Removed from the baseline.* The sentence no longer appears in policy 5's `baseline.rule`, which is correct: it is
a normative statement about a later invoice, not a step of the standard method for `booking_amount`, and
`baseline.rule` still yields a definite 233,385.75 on task 1's world.
*The `soil_test_before_prescription` gate stays required* — verified above in § `override_declarations`.

**RED-3 — CLOSED, and the whole reconstruction verified against `products/grain.yaml`, not just the three
tickets.** Every figure below is my own recomputation from the grain charter's formulas and the Basis Fixed
Contract's parameters.

*The three tickets.* Gross weights were re-derived so that the charter's own formula `net_bushels =
round(gross_bushels × (1 − shrink_pct_per_moisture_point × max(0, moisture_pct − moisture_base_pct) / 100), 2)`
reproduces the nets, with `shrink_pct_per_moisture_point = 1.18` and `moisture_base_pct = 15.0`:

| ticket | moisture | gross (round 2 → round 3) | charter net from the new gross | seeded net | match |
| --- | --- | --- | --- | --- | --- |
| T-3061204 | 15.2 | 13,342.00 → **13,231.23** | 13,200.00 | 13,200.00 | ✓ |
| T-3062877 | 15.1 | 14,201.00 → **14,067.10** | 14,050.50 | 14,050.50 | ✓ |
| T-3064130 | **15.0** | 11,370.00 → **11,249.50** | 11,249.50 | 11,249.50 | ✓ |

The row that made round 2's case plainest is now right: at exactly the moisture base the charter says grain
"shrinks by nothing", and gross now equals net. Nets are unchanged, so **`delivered_bushels` is still 38,500.00** —
independently recomputed through the evaluator, not read off the trace.

*Quality readings, checked rather than taken on trust.* `grain_evt_quality_discount`'s formula
`round(net_bushels × (max(0, test_weight_base_lbs − test_weight_lbs) × test_weight_discount_per_lb_usd +
max(0, foreign_material_pct − foreign_material_free_pct) × foreign_material_discount_per_pct_usd), 2)` gives
**0.00 on all three loads**: test weights 56.4 / 56.1 / 55.8 are all above the 54.0 base, foreign material
0.7 / 0.9 / 0.8 all below the 1.0 free tolerance. Damage 1.1 / 1.4 / 1.2 falls in the ladder's first band, whose
`discount_per_bushel_usd` is 0.0, and nowhere near `quality_rejection_damage_pct = 20.0`. So no quality-discount
line is owed on any ticket and none is seeded — consistent with the charter's practice of not writing nil lines.

*Freight.* `grain_evt_delivery_application`: *"Where the load is delivered to a facility other than the one the
contract calls for, the freight differential is applied against the price."* All three tickets carry
`delivery_location: "Kellerton Rail Terminal"` and the contract's `delivery_location` is the same, so **no freight
differential is owed** and round 2's invented 402.00 freight deduction is correctly gone. (It never matched
`freight_differential_per_bushel_usd = 0.045` on any bushel count either.)

*The two settlement statements.* `grain_evt_checkoff_and_retain`: *"Two withholdings attach to every settlement of
patronage-eligible bushels and are shown as their own lines."* Basis Fixed Contract is `patronage_eligible: true`,
so round 2's statements were missing both lines; round 3 adds them at the published rates.

| statement | settled bu | price | gross = bu × price | checkoff @ 0.0075 | retain @ 0.003 | net | seeded net |
| --- | --- | --- | --- | --- | --- | --- | --- |
| S-552480, 2025-12-18 | 28,500.0 | 4.6113 | **131,422.05** | **213.75** | **85.50** | **131,122.80** | 131,122.80 ✓ |
| S-552915, 2026-02-18 | 10,000.0 | 4.6113 | **46,113.00** | **75.00** | **30.00** | **46,008.00** | 46,008.00 ✓ |

Every one of those twelve figures reproduces the seed exactly. `grain_evt_settlement`'s formula
`gross_amount = round(settled_bushels × price_per_bushel, 2)` is satisfied on both; the only deduction types
present are `checkoff` and `per_unit_retain`, each carried once per statement as the rule requires; both nets are
far above `settlement_minimum_amount_usd = 25.00`; and `price_per_bushel` now equals the contract's
`cash_price_per_bushel` of 4.6113, which is *"the flat price they carry"*. The 4-decimal price matches the schema's
declared format (`USD per bushel to 4 decimal places`), and the re-struck bushel counts (13,231.23 / 14,067.10 /
11,249.50) match `bushels to 2 decimal places`.

*The reconciliation holds in three directions.* Settled bushels 28,500 + 10,000 = **38,500.00** equals the net
bushels delivered and equals the contract's `contracted_bushels`, with `open_bushels: 0` and `status: settled`.
Both settlements are drawn on bushels that were delivered and priced before the statement date (all three tickets
carry `pricing_status: "priced"` and all three precede 2025-12-18).

*And the February net still anchors the input ledger.* 46,008.00 is exactly
`agronomy_invoices.9f2ce707-…`, the payment of −46,008.00 posted 2026-02-18 by `grain_settlement_transfer` —
which is what base `agronomy_payment_application` requires of the credit-to-input-account route
(*"the whole net of that settlement lands on the account as one payment on the settlement date"*), and what
`grain_evt_settlement` requires of it (*"Choosing to credit the input account moves the whole net, not part of
it"*). The agronomy ledger was not touched in round 3, so this is a genuine cross-product reconciliation and not a
figure moved to fit.

*Settlement lead.* `grain_evt_settlement`: *"Funds are released the programme's settlement lead in business days
after the statement date, counting only days the cooperative's office is open."* `settlement_lead_days = 3`;
S-552480 is dated Thursday 2025-12-18, so three business days are Friday 19, Monday 22 and **Tuesday 23** — and
the payment row moved from 2025-12-22 (two business days) to **2025-12-23**. Correct, and a defect of round 2 that
I had not caught. `net_amount: 131122.80` is now populated on that row, a declared field of
`grain_settlement_paid` that round 2 left off.

*Nothing it moved feeds task 0.* Task 0's masked view is **byte-identical** to round 2
(`3a5e353eeffcfe3a` both rounds), so not one row of its world changed; its own grain evidence is a different
contract and a different ledger (`grain_contracts.3b00fe1f-…` at `cash_price_per_bushel: 4.58` and
`grain_ledger.fb54d3d6-…`, soybeans, which is charter-consistent at or under its 13.0 base). All 22 of task 0's
figures were nonetheless recomputed from scratch on the round-3 artifacts and are unchanged.

**OBS-12 — stands as an observation, and the "no change" is right.** My round-2 note was that 533,333.33 fiscal-2025
input-dollar units sit at ≈ 452 USD/acre against ≈ 265 USD/acre of seeded fiscal-2026 spend. The two are not the
same measure: `patronage_evt_unit_accrual` accrues input dollars *"across every input account they hold"* and
*"net of discounts"* over a fiscal year that is not seeded, whereas the 312,289.50 is one account's gross invoicing
over a ten-statement-month window. And the alternative the note implied — holding the units at 200,000 and letting
the charter rate stand — would put `cash_portion_amount` at 1,080.00, move `patronage_credit` from 2,880.00 to
1,080.00 and move task 0's scored payment from 37,030.00 to 38,830.00. Leaving it alone was the correct call; the
observation was never grounds for rework and is not now.

**OBS-13 — observation (recorded, pre-existing since revision 1, no consequence).**
`agronomy_ext_arrears_settlement_payment`'s single `overwrite` entry supersedes
`agronomy_credit_standing`'s sentence *"Buying is reinstated when the member pays at least the programme's
reinstatement share of the overdue balance, and reinstatement is recorded by the credit department rather than at
the counter, however plainly the member says the payment has been sent."*, and that same sentence is verbatim the
`condition` of that base policy's `credit_department_records_reinstatement` eligibility gate, so the gate is
superseded with it. The gate `applies_to: [agronomy_account_suspended]`, an event no task tool writes and no
extended policy claims, and neither task's account stands in `suspended` (task 0's is `past_due`, task 1's is
`active`), so nothing in either scored solution turns on it. Surfaced now only because revision 3 made me check
every `superseded_clause` against every base eligibility condition mechanically; it is the only such overlap in
the charter.

**No other new defect.** Nothing that passed in revisions 1 or 2 has regressed: the base section is still verbatim,
the tool module is untouched, the prerequisite graph and its three sentences are unchanged, all 24 ladders still
meet every bound, both tasks' scopes are still disjoint and jointly complete, and all 34 scored figures across the
two tasks are identical to the ones I derived blind in revision 1.

## revision_3 — closing checklist

All M tasks now PASS on all four relationships, so this is the real close-out.

| item | state |
| --- | --- |
| per-task audit files correspond one-to-one with the tasks and `_difficulty.md` sits alongside them | **holds** — `0.md`, `1.md`, `_difficulty.md` |
| old revisions traceable | **holds** — revisions 1, 2 and 3 appended in order, no earlier text rewritten |
| every comparison section carries a PASS | **holds** — `0.md` and `1.md` § revision_3 are both PASS on all four relationships |
| this difficulty's extended policies fully covered; the M tasks' scopes pairwise disjoint, each spanning a whole tree | **holds** — {1, 2, 3} and {4, 5}; union = all five; each scope is one root plus its prerequisite problems |
| task tools and GT closed; each tool an independently generated, frozen uuid8 | **holds** — `task_tools.py` byte-identical across all three rounds; `6859ca91`, `aaf992aa`, `ad47b93a`, `cc5ed557`, `189dfe27` |
| every tree: 1–3 prerequisite problems, ≥ max(n−1,1) `value_input` edges, ≥ 1 `owner=user` problem, no cycle; the difficulty's edges a DAG | **holds** — task 0: 2 problems, 2 `value_input` edges, user root; task 1: 1, 1, user root; union 1 → 2 → 3 and 4 → 5 is acyclic with no cross-task reference |
| every computation: self-sufficient baseline giving a definite number ≠ gold; 4–6 factors, 2 `parameter`, 1 `method`; per task ≥ 1 multi-source and ≥ 1 cross-difficulty | **holds** — baselines 12,790.68 / 3,769.67 / 77,433.82 / 1,295.60 / 233,385.75 against 15,196.00 / 320.20 / 37,030.00 / 5,083.25 / 228,137.43; counts 4 / 6 / 6 / 4 / 4; task 0 reads `custom`, `storage`, `grain`, `patronage`, task 1 reads `grain` |
| every ladder ≥ 3 tiers stated in full in its rule, tiers distinct in outcome, conditions and outcomes ones that line of business actually holds | **holds** — 24 of 24; the vacuous conjunct of revision 1 is gone and its replacement divides on a threshold the base charter publishes |
| every factor bears weight on its task's world against an honest baseline | **holds** — all 24 substitutions move the scored value; all 34 figures independently recomputed in all three rounds and matched |
| cross-difficulty evidence seeded and consistent with the other product's own charter | **holds** — `custom`, `storage`, `grain` and `patronage` rows all present; the patronage rows reconcile to Class A's declared rate and split, and the grain rows now reconcile to the shrink, quality, freight, checkoff, retain, gross, net, minimum and lead-day rules of `products/grain.yaml` |
| instantiation-stage gates re-run on the final form | **holds by citation** — the orchestrator's round-3 block (2026-09-18T09:58) postdates the last artifact write (09:55) and is therefore on the final form; not re-run by this auditor, and `replay_tasks.py` deliberately not run because it writes back to the task JSONs. `check_traceability` remains correctly deferred to step 3 |

**Difficulty verdict, revision 3: PASSES the source-layer audit.** Policy self-consistency, the problem tree, the
factors' weight and the unique solution hold for both tasks. Four observations stand on record and are not grounds
for rework: OBS-4, OBS-7, OBS-8 (charter judgement calls), OBS-12, OBS-13 and the prepay-balance stamp note.

---

# revision_4 — re-audit, charter-global

## re_audit_frozen

| item | round 3 | round 4 | re-derived? |
| --- | --- | --- | --- |
| `agronomy.extended.yaml` | `f06d6a864ab9b2db` | **`728c5cd838a8f81e`** | **yes, in full** |
| `task_tools.py` | `fb62107a7cae45c5` | `fb62107a7cae45c5` (unchanged throughout) | carried forward by reference on that hash pair |
| `tasks/0.json` | `f6ed40c91f7bb30b` | **`8a654c4cea378343`** | per-task sections re-derived in `0.md` § revision_4 |
| `tasks/1.json` | `5263b5d7954c8894` | **`b2c7e754ad868317`** | per-task sections re-derived in `1.md` § revision_4 |
| masked view 0.json | `3a5e353eeffcfe3a` | **`27434df3c514b10d`** | task 0's world moved (three renumbered rows) |
| masked view 1.json | `ed61f49c961afb61` | **`b7a0996249c8372e`** | task 1's world moved (one invoice re-priced) |
| `blueprint/products/agronomy.yaml` | `66127eecc1f99b7b` | `66127eecc1f99b7b` | base section re-verified byte-for-byte |
| `blueprint/products/grain.yaml` | `e10c3fdd9e03dba1` | `e10c3fdd9e03dba1` | untouched |

Revisions 1–3 are left exactly as they stand. Both worlds and the charter moved and scored figures moved on task
1, so **both tasks' per-task sections were re-derived in full**, not carried forward. `task_tools.py` is
byte-identical for the fourth round running, so § `action_binding_and_uuids` is carried forward on the matching
hash pair. No instantiate gate script was run; `replay_tasks.py` was deliberately not run because it writes back to
the task JSONs. The round-4 gate block, now including a green `check_traceability` against the published corpus,
came with the brief and is cited rather than re-run.

**New standard applied this round.** The render-layer audit returned KB-RUNTIME RED on both tasks for prose that
looks determinate to a reader who can see the `compute` and is not determinate to one who cannot. I have therefore
re-run this difficulty's `rule_compute_equivalence` under that stricter lens — asking of every quantity not only
"does the rule say this?" but "would the rule fix this value for a reader with no binding in front of them?" —
and recorded what it turns up, including where my own earlier rounds passed prose that does not meet it.

## revision_4 — charter-global re-checks

### policy_conflict_scan, prerequisite_graph, prerequisite_sentences, factor_ladders (re-derived)

Base section **still byte-for-byte identical** to `blueprint/products/agronomy.yaml`. Subjects, triggers, scopes
({1, 2, 3} and {4, 5}, disjoint and jointly complete) and cross-category boundaries unchanged. All three
prerequisite edges unchanged — `value_input`, `form: state`, `fallback_reason` correctly absent, each
`policy_source` verbatim in the blocked policy's own rule, graph acyclic. Factor structure unchanged: 4 / 6 / 6 /
4 / 4 factors, 3 / 4 / 5 / 3 / 3 `parameter`, 1 / 2 / 1 / 1 / 1 `method`, 24 ladders of three disjoint tiers, every
fall-through exactly its `baseline`, no two tiers sharing an outcome. The full structural sweep (bindings without a
basis, basis keys that are not bindings, basis sentences absent from the rule, baseline sentences absent from the
rule, missing `decides`, overlapping binding sets, fall-through ≠ baseline) returns **zero issues**.

### rule_compute_equivalence under the runtime lens

**The rounding mode is now fixed everywhere.** Every rounding statement in the extended charter carries its mode:
`"rounded half away from zero to two decimal places"` occurs **79 times** across rules, baselines, `compute_basis`
quotations and ladder methods, and a sweep for any rounding sentence lacking a mode returns nothing (the three
apparent hits are the word "ground", twice in the inherited base section, and the parameter name
`round_up_epsilon`). The one mode-free rounding that remains is the ceiling in `quoted_figure_rounding` — "taken up
to the next whole ten dollars at or above the net figure" — which is a ceiling and mode-independent by
construction.

**The day-count endpoint is now fixed on `restocking_rate`.** See § `findings`, task-0 item.

**Where the lens still finds under-determination** — recorded as observations because neither admits a second
defensible *value* on either task's world, and the standard for a red light is a demonstrated consequence:

- **OBS-15.** Three further day/month counts state a start endpoint and no end endpoint:
  `overdue_days` (*"counted from the date the account went past due, that date counting as day zero"*, and likewise
  from the last charge posted and the last payment posted), `arrears_days` (*"the account has stood past due for
  more than ninety days"*), `open_months` (*"the account has been open for at least thirty-six months"*) and
  `review_months` (*"the account's most recent credit review was completed inside the programme's review
  interval"*). Each ends at the handling date in `compute`. This is the same shape as the render finding, but it
  is materially weaker in one respect that decided my call: on `days_back` the record carried a **rival** endpoint
  — the return request's own date — which a reader would plausibly take and which gives a different band and a
  different credit. For these four no rival endpoint exists in the record; the handling date is the only candidate
  a reader has, and I can construct no second value. Recorded, not red-lit. If the render layer disagrees on its
  own view, that is the view that should settle it.
- **OBS-16.** `delivered_bushels` is described as *"the bushels the cooperative has taken in from them over those
  fourteen months"* and computed as `XSUM('grain','grain_ledger','net_bushels', …)`. "Taken in" does not say net or
  gross, and the ledger carries both. On task 1's world net is 38,500.00 and gross is 38,547.83, and **both clear
  the 25,000-bushel qualifying volume**, so the tier, the bonus and the scored discount are the same under either
  reading and no second value follows. It does weaken what I credited in revision 3 as a near-miss: the gross
  reading is excluded not by the agronomy rule but by the grain charter's own convention (*"Net bushels, not gross,
  are what comes off the contract's open bushels and what earns patronage"*), which is a different document.

### override_declarations — policy-side item 1 verified

The reworker's argument is **exactly right, not an evasion**, and it holds on three independent legs which I
checked separately:

1. *The gate forbids the direct route.* `check_extended`'s own contract reads: a `superseded_clause` must be
   *"a verbatim (whitespace-insensitive) substring of that base policy's **rule**"*, and the check fails with
   "superseded_clause is not a verbatim sentence of base policy" otherwise. A `formula:` block is a sibling key of
   `rule`, not a part of it, so no formula block can be named in an `overwrite` entry at all.
2. *The base copy may not be rewritten.* My own check 1 requires the base section to stay verbatim, and I verify
   it by deep equality every round — it passes again this round. Deleting or editing the two formula blocks would
   break that and is not available either.
3. *So prose in the extended policy's own rule is the only lever, and it is the lever that reaches the reader*,
   because base and extended are rendered into the KB together.

Both withdrawal sentences are present, and each describes the arithmetic it withdraws accurately enough that a
reader can identify it:

- `agronomy_ext_crop_protection_return_credit`: *"The restocking arithmetic the programme's own returns schedule
  sets out — the invoiced value multiplied by the programme's restocking percentage, with the credit being that
  value less the charge — is withdrawn together with the pricing clause it belongs to and is not applied to crop
  protection product worked out this way."* Against base `agronomy_returns_and_credits.formula`:
  `discount_amount: round(extended_amount * restocking_fee_pct / 100, 2)` and
  `amount: round(extended_amount - extended_amount * restocking_fee_pct / 100, 2)` — the description matches both
  lines.
- `agronomy_ext_arrears_service_charge`: *"The service charge arithmetic the programme's own schedule sets out —
  the monthly percentage taken on one invoice's unpaid amount, floored at the programme's minimum — is withdrawn
  together with the per-invoice clauses it belongs to and is not applied to a charge worked out this way."*
  Against base `agronomy_finance_charge.formula`:
  `finance_charge_amount: max(finance_charge_minimum_usd, round(amount * finance_charge_monthly_pct / 100, 2))` —
  matches.

Each ties the withdrawal to a clause already named in that policy's `overwrite`, so the declaration and the
withdrawal travel together. Neither sentence is in `baseline.rule`, which is right: a baseline is the standard
method for the scored quantity, not a notice about another document.

The other two base formula blocks were checked and are **not** in conflict and correctly left alone:
`agronomy_discount_schedule.formula` computes the *early pay* discount, a different discount kind from the volume
discount policy 4 supersedes; and `agronomy_evt_invoicing.formula` computes `extended_amount` on an issued
invoice, which no extended policy displaces.

### policy-side item 3 — verified

The three format examples that were also live seed rows have been renumbered on the **seed** side:
`IN-4410287 → IN-4410953`, `DT-2210554 → DT-2210731`, `PY-901772 → PY-903486`. Propagation checked by exhaustive
search of the difficulty directory: the new numbers occur 16 / 7 / 6 times across `tasks/0.json`
(`initial_state`, `evaluation_criteria` tracing, `prerequisite_closure`, `solvability_contract.seed_consistency`
and the dossier), and the old numbers survive in exactly three places, all inside `design_rationale`'s ROUND 4
worklog where it describes the fix, plus the tool docstrings in `task_tools.py` (unchanged by design — those are
the format examples, and the point of the fix is that they now collide with no live row). No scored field, no
tracing sentence and no closure field carries a stale number.

### policy-side item 2 — recorded, out of reach

`verify_member_identity` lives in `blueprint/share_tools.py`, which is part of the frozen scenario constitution and
outside both the rework's and this audit's write domain. Recorded as a scenario-wide base matter, as instructed;
it is not a finding against this difficulty. Noted alongside it: the base `formula` blocks throughout
`products/agronomy.yaml` use a bare `round(...)` with no mode, which the extended charter can no longer match in
prose now that every extended rounding names half-away-from-zero. Neither of the two surviving base formulas is
scored in this difficulty, and neither is the rework's to change.

## revision_4 — findings

**Task-0 runtime RED — CLOSED.** The `restocking_rate` ladder now names the quantity for what the compute measures
and states both endpoints. The rule reads: *"Where the delivery the product came off has stood out of the plant
for no more than seven calendar days when the credit is worked out, **counted from the date that delivery was
invoiced as day zero to the handling date**, and the member's input spend on the account over the ten statement
months before the handling date is at or above the programme's volume discount threshold, the restocking rate is
instead the prompt return rate."*, with a second tier *"…for more than seven but not more than fourteen calendar
days when the credit is worked out, **counted the same way**…"*. Both `ladder[].when` strings reproduce those
clauses word for word, and `compute_basis.days_back` quotes the first.
*The prose now fixes the compute.* `line_date = LATEST('agronomy_invoices','invoice_date', …,
product_category='crop_protection')` and `days_back = DAYS(line_date, NOW)`: the start endpoint is the crop
protection delivery's invoice date and the end endpoint is the handling date, which is exactly what the two named
endpoints say. The old wording — "the product came back within seven calendar days of the delivery it was billed
on" — named a return date the compute never reads.
*The near-miss still bites, and now it bites for the right reason.* The world still carries
`agronomy_orders.2c120cc4-…`, the approved and signed `product_return` of **2026-06-15**, three days before the
handling date. A reader who counts from it lands on the prompt tier of 4.0 % and computes a credit of
**15,513.62** instead of **15,196.00** — I ran both. The rewritten sentence excludes that reading on its own terms
by measuring the **delivery's** age, not the return's. **No figure moved**: `days_back` is still 10, still in the
second tier, and all 22 of task 0's figures are unchanged.

**Task-1 runtime RED — CLOSED, from both ends, and the "exactly one before" claim verified.**
*The mode is stated.* 79 occurrences of "rounded half away from zero to two decimal places"; zero rounding
sentences left without a mode.
*The world no longer sits on a tie.* I instrumented every `RND` call in both tasks' gold runs and compared
round-half-even against round-half-away-from-zero on the exact decimal argument. **Task 0: 17 calls, zero
disagreements. Task 1: 8 calls, zero disagreements.** Against the round-3 world there was exactly one:
`gross_ceiling = RND(prior_net_spend × net_share_pct / 100, 2)` with `prior_net_spend = 214,365.85` and
`net_share_pct = 110` gives **235,802.435** exactly — a half-cent tie, where half-away gives 235,802.44 and the
evaluator gave 235,802.43, a cent that propagated straight into `booking_amount`. On the round-4 world the same
binding is `214,364.67 × 110 / 100 = 235,801.137`, which is not a tie, and both modes give 235,801.14.
*The seed change is minimal and internally consistent.* `agronomy_invoices.bd08f020-…` (`IN-4395110`, 2024-09-18)
moves `unit_price` 862.00 → **861.98** with `extended_amount`, `amount` and `balance_after` 101,716.00 →
**101,713.64** (118 × 861.98 = 101,713.64), and its matching payment `75391f4c-…` moves −101,716.00 → −101,713.64
so the invoice still clears exactly. That invoice is 25 statement months back, so it is outside the fourteen-month
windows and inside the twenty-six-month one — which is why `discount_amount` is untouched and only the prepay
ceiling moves.
*Five figures moved, as claimed, and I reproduce every one* (see `1.md` § revision_4).

**RED-4 — `SOURCE-CHAIN RED` (new, task 1). A closure assertion states a figure the world does not produce, and
contradicts the same task file's own arithmetic.**
*Symptom.* `tasks/1.json` asserts in three places that with the prerequisite unresolved the `prior_net_spend`
binding reads **219,448.17**. The world gives **219,447.92**.
*Root cause.* The figure was carried down from revision 3's 219,449.10 by 0.93 instead of by 1.18, which is half
of the 2.36 by which the re-priced invoice moved the twenty-six-month total.
*Evidence.* `prerequisite_closure.edges[0].unresolved_at_frozen_time.why_false`: *"…the discounts standing binding
reads -1240.00 instead of -6323.25, so the prior season spend reads **219448.17** instead of 214364.67."*;
`.flips_to_true_by`: *"…the prior season spend falls from **219448.17** to 214364.67…"*;
`prerequisite_closure.edge_load_bearing[0].skipped_effect`: *"…leaves discounts_standing at -1240.00 and
prior_net_spend at **219448.17**…"*. Recomputation on the unresolved-edge world, binding by binding:
`spend_two_season = 441,375.84`, `discounts_standing = −1,240.00`,
`prior_net_spend = RND(441,375.84 / 2 + (−1,240.00), 2) = RND(220,687.92 − 1,240.00, 2) = **219,447.92**`.
*Demonstrated consequence.* The stated figure is false against the world, and the task file contradicts itself
with it: `evaluation_criteria[10].argument_uniqueness_tracing.booking_amount` states the same halving as
*"441375.84 halved to **220687.92**"*, and 220,687.92 − 1,240.00 cannot be 219,448.17. Carrying the asserted figure
forward gives `RND(219,448.17 × 1.1, 2) = 241,392.99` and a booking of **233,727.99**, which contradicts the
booking figure of **233,727.71** stated in the very same sentence. The edge's conclusion survives — 233,727.71 and
228,136.14 are both correct, the edge bears weight and the tree holds — but the proof the artifact submits for it
does not hold, and under this skill an assertion about the world in a closure field is part of the proof and is
red-lit under the relationship it supports.
*Affected artifact and location.*
`env/env_0003_farm_supply_and_grain_cooperative/tasks/crop_input_desk/tasks/1.json`:
`prerequisite_closure.edges[0].unresolved_at_frozen_time.why_false`,
`prerequisite_closure.edges[0].unresolved_at_frozen_time.flips_to_true_by`,
`prerequisite_closure.edge_load_bearing[0].skipped_effect`. Bears on **task 1** only; no scored field carries it,
and `tasks/0.json` is unaffected.
*Relation to previous revisions.* New in revision 4. Revision 3's 219,449.10 was correct for revision 3's world;
this is a transcription of the update, not a stale leftover, which is why it survived a stale-value sweep — I
found it by recomputing the binding rather than by searching for old numbers.

**OBS-14 — observation (task 0, `solvability_contract.seed_consistency`).** The note explaining the seeded
2026-04-30 service charge reads: *"Service charge assessed on 30 April 2026 against the oldest matured invoice
IN-4407955, at the programme's 1.25 percent monthly rate on the 59673.50 then standing overdue, giving 745.92…"*.
The internal arithmetic is sound (59,673.50 × 1.25 % = 745.919 → 745.92), but I cannot reconstruct 59,673.50 from
the seeded world at that date under either the base rule or the extended one. Base `agronomy_finance_charge` is
per-invoice, and 1.25 % of `IN-4407955`'s unpaid 114,560.00 is 1,432.00. The extended rule's account-wide balance
at 2026-04-30 is 198,689.50 of matured invoices less 137,050.76 of payments, 1,016.40 of credits and 1,965.24 of
discounts = **58,657.10**; 59,673.50 is exactly that figure with the 1,016.40 credit memo left out, though the
credit memo was posted on 2026-01-09 and the rule says the balance is reduced by every credit memo written on the
account. The row itself is a seeded historical fact the compute reads as data (`charges_standing`), nothing
re-derives it, and no scored value or relationship turns on the note, so it is an observation. Recorded honestly:
I did not examine `solvability_contract` in revisions 1–3, so I cannot say whether the sentence is new.

**OBS-15, OBS-16** — the two remaining under-determinations the runtime lens turns up; stated in full in
§ `rule_compute_equivalence` above.

**Nothing regressed.** Base section verbatim, tool module untouched, prerequisite graph and sentences unchanged,
all 24 ladders still meeting every bound, scopes still disjoint and complete, and every figure that was not
supposed to move did not: all 22 of task 0's and all 6 of task 1's first computation.

## revision_4 — closing checklist

**The difficulty does not close out this round.** Task 0 passes on all four relationships; task 1 carries RED-4.
Every other item of revision 3's checklist was re-verified and still holds — coverage and disjoint scopes, tool and
uuid8 closure, tree shape and the `owner=user` write in each, self-sufficient baselines giving definite numbers
different from gold (12,790.68 / 3,769.67 / 77,433.82 / 1,295.60 / 233,385.75 against 15,196.00 / 320.20 /
37,030.00 / 5,083.25 / **228,136.14**), factor counts and ladder structure, every factor bearing weight, and
cross-difficulty evidence seeded and charter-consistent. The instantiation-stage gates were re-run by the
orchestrator on the final form at 12:38 and are cited, `check_traceability` included; they do not reach an
assertion of this kind, which is what a manual audit is for.

---

# revision_5 — re-audit, charter-global

## re_audit_frozen

| item | round 4 | round 5 | re-derived? |
| --- | --- | --- | --- |
| `agronomy.extended.yaml` | `728c5cd838a8f81e` | **`e77a90eb2e24e3a5`** | **yes, in full** |
| `task_tools.py` | `fb62107a7cae45c5` | `fb62107a7cae45c5` (unchanged throughout) | carried forward by reference on that hash pair |
| `tasks/0.json` | `8a654c4cea378343` | **`624d73208f810821`** | per-task sections re-derived in `0.md` § revision_5 |
| `tasks/1.json` | `b2c7e754ad868317` | **`f6ea0ecec2ee0b13`** | per-task sections re-derived in `1.md` § revision_5 |
| masked view 0.json | `27434df3c514b10d` | **`c8568fd32492b8ff`** | world moved |
| masked view 1.json | `b7a0996249c8372e` | **`bd5be12e6cdbd284`** | world moved |
| `blueprint/products/agronomy.yaml` | `66127eecc1f99b7b` | `66127eecc1f99b7b` | base section re-verified byte-for-byte |

Revisions 1–4 are left exactly as they stand. Both worlds moved, so **both tasks' per-task sections were
re-derived in full**. No instantiate gate script was run; `replay_tasks.py` deliberately not run. The round-5 gate
block came with the brief and is cited.

## revision_5 — what moved

| artifact | change |
| --- | --- |
| charter | every interval given an end endpoint (24 occurrences of "to the handling date"); `delivered_grain_bonus`'s tier rewritten to "the **net** bushels … counted after the moisture shrink taken at unload as the scale tickets record them" |
| `tasks/0.json` world | the seeded credit memo `9fdc1729-…` moved `posted_date` 2026-01-09 → **2025-10-27**, and three `balance_after` values on the `IN-4412044` rows re-threaded down by 1,016.40 |
| `tasks/1.json` world | `IN-4408710` due 2026-07-13 → **2026-07-12** and `IN-4411355` due 2026-08-17 → **2026-08-16**; three `balance_after` values corrected |
| both proof layers | RED-4's three assertions; four `solvability_contract` notes; ROUND 5 worklog sections |

## revision_5 — charter-global re-checks

### structural sweep (re-derived)

Base section **still byte-for-byte identical** to `blueprint/products/agronomy.yaml`. The full sweep — bindings
without a `compute_basis` entry, orphan basis keys, basis sentences absent from the rule, baseline sentences absent
from the rule, missing `decides`, bindings that name nothing, fall-through ≠ baseline, overlapping binding sets,
and each `policy_source` verbatim in its blocked policy's own rule — returns **zero issues**. Subjects, triggers,
scopes ({1, 2, 3} and {4, 5}), cross-category boundaries, the three prerequisite edges, the factor counts
(4 / 6 / 6 / 4 / 4; 3 / 4 / 5 / 3 / 3 `parameter`; 1 / 2 / 1 / 1 / 1 `method`) and all 24 ladders are unchanged.

### OBS-15 — CLOSED

Every interval in the charter now names both endpoints, and the ladder `when` texts carry the same wording:

| binding | rule now reads | value |
| --- | --- | --- |
| `overdue_days` | *"counted from the date the account went past due, that date counting as day zero, **to the handling date on which the charge is worked out**"* | 49 |
| `review_months` | *"counted in whole months from the day the review completed **to the handling date**"* | 7 |
| `arrears_days` | *"counted from the date it went past due as day zero **to the handling date**"* | 102 |
| `open_months` | *"counted from the date it was opened **to the handling date**"* | 103 |

All four counts are unchanged, confirmed by my own binding dump, and the phrase "to the handling date" occurs 24
times across rules, baselines, `compute_basis` and ladder texts. Closed rather than carried, which is the right
disposition: the observation was that the prose fixed these values only for a reader who could see the binding.

### OBS-16 — CLOSED

`delivered_grain_bonus`'s tier now reads *"the **net** bushels the cooperative has taken in from them over those
fourteen months, **counted after the moisture shrink taken at unload as the scale tickets record them**"*, carried
identically into `compute_basis.delivered_bushels`, `holds_grain_contract`, `grain_bonus_pct` and both ladder
`when` strings, with `compute` unchanged at
`XSUM('grain','grain_ledger','net_bushels', …)`. The gross reading (38,547.83) is now excluded by the agronomy
rule's own words rather than by the grain charter's convention, which was the whole of the observation. One
residual, not a defect: the `cross_category[].note` annotation still reads "the bushels the cooperative has taken
in from them" without "net". That field is an authoring annotation about a cross-category read, not a normative
sentence and not a rule the reader is given; the rule, the basis and both ladder texts all say "net".

### rounding mode — one divergence found, see RED-5

79 mode-bearing rounding statements; zero rounding sentences lacking a mode; the only mode-free rounding is the
mode-independent ceiling in `quoted_figure_rounding`. But the mode is now stated in prose while the executable
`RND` is Python's `round`, which rounds half to even, and **those two differ whenever an argument lands exactly on
a half cent**. I therefore instrumented `RND` and compared half-to-even against half-away-from-zero on the exact
decimal argument of **every** call, across the gold path, each edge-unresolved world, each factor's baseline
substitution and each whole-baseline substitution, for both tasks — 217 calls in all. **One argument disagrees**,
and it is a figure the artifacts record. See § `findings`, RED-5.

This is the check the reworker's sweep cannot make by construction, and it is worth saying why: its sweep flags
"decimal literals that no recomputation produces", and 77,433.82 **is** produced by its recomputation, because its
recomputation uses the same `round` the evaluator does. A literal-matching sweep catches transcription errors like
RED-4; only a mode comparison catches a mode divergence. I missed it in revision 4 for the narrower reason that I
instrumented the gold path alone.

## revision_5 — findings

**RED-4 — CLOSED.** All three assertions now read **219447.92**, and it is the figure my own recomputation gives
from the binding on the edge-unresolved world: `spend_two_season = 441,375.84`, `discounts_standing = −1,240.00`,
`prior_net_spend = RND(441,375.84 / 2 − 1,240.00, 2) = RND(220,687.92 − 1,240.00, 2) = 219,447.92`. Locations
re-read: `prerequisite_closure.edges[0].unresolved_at_frozen_time.why_false`, `.flips_to_true_by` and
`prerequisite_closure.edge_load_bearing[0].skipped_effect`. The figure now agrees with the halving stated in
`argument_uniqueness_tracing` (441,375.84 → 220,687.92) and with the booking figures either side of it
(233,727.71 and 228,136.14), so the internal contradiction is gone. `219448.17` survives only inside
`design_rationale`, where the worklog records the fix. The reworker's stated root cause matches what I found in
revision 4.

**OBS-14 — CLOSED, and the field it exposed was swept properly.** Treating `solvability_contract` as unswept turned
up four bad notes rather than one, and all four now check out against my own recomputation:

1. *The seeded service charge.* The note no longer derives 745.92 from a balance the world does not produce. It
   now claims no derivation and states only what is checkable: `IN-4407955` was on 2026-04-30 the oldest invoice
   past the programme's terms and still unpaid, its 2026-03-07 due date is **54 days** earlier (verified: 24 days
   of March plus 30 of April), well past the 15 grace days, and 745.92 is above the 10.00 floor. It names the row
   as a historical fact of the account's past. The 59,673.50 is gone.
2. *The part payment.* Now: nothing on the account had passed its due date by 2026-02-05 — the earliest is
   `IN-4407955`, due 2026-03-07 — so base's 25 % minimum on a part payment of an **overdue** balance does not
   engage. I checked every due date on the account against that date; the note is right.
3. *The seeded credit memo.* The row moved to **2025-10-27**, day 19 of the Seasonal Terms 21-day return window
   counted from the 2025-10-08 delivery date on ticket `DT-2210731`, and the note's arithmetic reproduces base
   `agronomy_returns_and_credits` exactly: 12.00 gallons at the invoiced 96.25 is 1,155.00, less the programme's
   12.0 % restocking charge of 138.60, giving 1,016.40. Crop protection is in the programme's returnable classes
   and the note records the product as returned unopened, which the programme requires. **Verified inert**, which
   was the load-bearing claim: `prior_credits` still counts it (2025-10-27 is 7 statement months back, inside the
   ten), so the tier is unchanged at "one or two"; `credits_standing`, `product_balance` and `season_credits` are
   unwindowed or out of scope; every one of task 0's 22 figures is unchanged.
4. *Task 1's payment note and two due dates.* The payment note now reads that 12,272.69 clears `IN-4403875`
   **together with** the 115.49 service charge assessed on it — and 12,157.20 + 115.49 = 12,272.69 exactly. The
   two due dates were moved back one day so that **every** invoice on both accounts now satisfies
   `due_date = invoice_date + terms_days` exactly: I checked all nineteen invoice rows across the three accounts
   at 180 and 300 days and found no exception. **Verified inert**: no `compute` in this difficulty reads
   `due_date`, and no figure moved.

**The two seed changes were checked as whole-ledger operations, not just as dated rows.** I re-threaded both
accounts' running balances from zero and reconciled them against the holdings: task 0's Seasonal Terms account
closes at **173,003.02** against `current_balance 173,003.02`, its prepay account at **−496.00 / 12,400.00**
against `−496.00 / 12,400.00`, and task 1's account at **24,010.00 / 7,665.00** against `24,010.00 / 7,665.00`,
with **no date on either ledger failing to reconcile**. The convention is consistent throughout — `balance_after`
tracks the receivable, a prepay booking does not move it and a prepay drawdown does — and the credit memo's move
was re-threaded correctly, which is exactly what the three changed `balance_after` values on `IN-4412044` are.
Task 0's near-miss row, the approved `product_return` of 2026-06-15, is untouched, and moving the old credit memo
five months further back from it makes the edge-A evidence stronger rather than weaker; the closure's evidence
list now cites `posted_date = 2025-10-27`, with no stale 2026-01-09 anywhere outside the worklog.

**My own literal sweep found nothing.** I recomputed every binding of every computation at handling time, on each
edge-unresolved world, under each factor's baseline and under the whole baseline, and checked every decimal
literal in `computations`, `prerequisite_closure`, `evaluation_criteria` and `solvability_contract` against the
result. Every literal in both tasks is accounted for: the scored and sensitivity figures, the edge-unresolved
figures (361.10, 36,940.00, 103,618.06, 119,187.02 on task 0; 219,447.92, 220,687.92, 233,727.71 on task 1) and a
handful of legitimate stated intermediates (533.06, 1,270.50, 68,700.00, 3.15, 86,373.06, 3,335.00). Nothing
unaccounted.

**RED-5 — `SOURCE-POLICY RED` (new finding; the defect is latent from revision 1, the divergence dates from
revision 4). The stated rounding mode and the executable disagree on a figure the artifacts record.**
*Symptom.* `tasks/0.json` `computations[2].baseline_result` records **77,433.82**. A reader who follows
`agronomy_ext_arrears_settlement_payment`'s `baseline.rule` as it is now written arrives at **77,433.83**.
*Root cause.* The rules now say "rounded half away from zero to two decimal places" everywhere, but the executable
`RND` is Python's `round`, which rounds half to even. The two agree on every argument except an exact half cent,
and the whole-baseline path lands on one.
*Evidence.* Under the whole-baseline substitution the settlement base is the product balance, 103,245.10, the
share is `P('reinstatement_payment_pct') = 75.0` and the age step is nil, so `baseline.rule`'s sentence — *"The
amount sought is the settlement base multiplied by the share the member must remit and the further share added for
the age of the arrears taken together as one total share, applied once to the settlement base and **rounded half
away from zero to two decimal places**"* — gives `103,245.10 × 75 / 100 = 77,433.825` exactly, which half away
from zero is **77,433.83**. The evaluator's `RND(77433.825, 2)` returns **77,433.82**, and that is the figure
recorded. My instrumented sweep over all 217 `RND` calls in both tasks, across gold, edge-unresolved,
per-factor-baseline and whole-baseline paths, finds this one argument and no other: task 0 has exactly one
disagreement and task 1 none.
*Demonstrated consequence.* The two faces of the policy reach different conclusions on the same input: the rule
says 77,433.83 and the compute says 77,433.82. The figure is the one the KB's computation document exists to let a
solver reproduce — the definite wrong number an agent who finds no factor must arrive at — so the document and the
recorded baseline are a cent apart, and a reader who follows the published arithmetic cannot land on the recorded
value. **No scored figure moves**: the gold path has no tie, both tasks' expected values are unchanged, and every
factor still bears weight.
*Affected artifact and location.* `env/env_0003_farm_supply_and_grain_cooperative/tasks/crop_input_desk/tasks/0.json`,
`computations[2].baseline_result` (`agronomy_ext_arrears_settlement_payment`), against
`agronomy.extended.yaml` `extended_policies[2].baseline.rule` and `rule` (the amount-sought sentence and the
figure-quoted sentence) and `compute[target_amount]`. Bears on **task 0**.
*Relation to previous revisions.* The recorded 77,433.82 has stood since revision 1 and was correct while the rules
said only "rounded to two decimal places". Revision 4 fixed the mode into the prose, which is right, and in doing
so turned a silence into a disagreement. Revision 5 claims the sweep is clean; it is clean of the defect its sweep
can see. I record honestly that I missed this in revision 4 by instrumenting only the gold path.

**Nothing regressed.** Base section verbatim; tool module untouched for the fifth round; prerequisite graph,
sentences and forms unchanged; all 24 ladders meeting every bound with fall-throughs equal to their baselines;
scopes disjoint and jointly complete; and every scored figure identical to the blind derivation of revision 1
except the two that moved for cause in revisions 2–4.

## revision_5 — closing checklist

**The difficulty does not close out this round.** Task 1 passes on all four relationships; task 0 carries RED-5.
Every other item of revision 3's checklist was re-verified and holds: coverage and disjoint scopes, tool and uuid8
closure, tree shape with an `owner=user` write in each, self-sufficient baselines giving definite numbers different
from gold, factor counts and ladder structure, every factor bearing weight, cross-difficulty evidence seeded and
charter-consistent, and both ledgers reconciling to their holdings. The gates were re-run by the orchestrator on
the final form at 14:01 with `check_traceability` green and are cited; no gate compares a stated rounding mode
against an executable one, which is why this needed a manual instrumented sweep.

---

# revision_6 — re-audit, charter-global

## re_audit_frozen

| item | round 5 | round 6 | re-derived? |
| --- | --- | --- | --- |
| `agronomy.extended.yaml` | `e77a90eb2e24e3a5` | `e77a90eb2e24e3a5` — **unchanged** | **carried forward by reference on that hash pair** |
| `task_tools.py` | `fb62107a7cae45c5` | `fb62107a7cae45c5` (unchanged throughout) | carried forward by reference |
| `tasks/0.json` | `624d73208f810821` | **`84d2cebb57024e92`** | per-task sections re-derived in full in `0.md` § revision_6 |
| `tasks/1.json` | `f6ea0ecec2ee0b13` | **`c33e1aea6d8373fb`** | proof fields re-read; world byte-identical, see `1.md` § revision_6 |
| masked view 0.json | `c8568fd32492b8ff` | **`97e877b7ae0e71f2`** | world moved |
| masked view 1.json | `bd5be12e6cdbd284` | `bd5be12e6cdbd284` — **byte-identical** | world did not move |
| `blueprint/products/agronomy.yaml` | `66127eecc1f99b7b` | `66127eecc1f99b7b` | base section re-verified byte-for-byte |

Revisions 1–5 are left exactly as they stand. **The charter did not move at all this round**, so every
charter-global section — `policy_conflict_scan`, `rule_compute_equivalence`, `action_binding_and_uuids`,
`prerequisite_graph`, `prerequisite_sentences`, `override_declarations`, `factor_ladders`, and revision 5's
`OBS-15 — CLOSED` and `OBS-16 — CLOSED` — is **carried forward on the matching hash pair
`e77a90eb2e24e3a5` / `e77a90eb2e24e3a5`**, which is the rule for re-deriving: a section is re-derived only when
its shared inputs can have moved it. What moved is task 0's world, and the one charter-global conclusion that
depends on a world — the rounding-mode sweep — is re-derived below. I re-verified the base section's byte
equality independently, since that is cheap and is the premise the whole override analysis rests on.

No instantiate gate script was run; `replay_tasks.py` deliberately not run. The round-6 gate block came with the
brief and is cited.

## revision_6 — findings

**RED-5 — CLOSED, and closed by the right lever.** The fix removes the midpoint from the world rather than
unstating the mode, which is the disposition that keeps revision 4's gain: the rules still say
"rounded half away from zero to two decimal places" at all 79 places, and there is now no input on which that
differs from what the executable does.

*The mechanism, verified.* The seeded part payment `agronomy_invoices.5c289446-…` (`PY-912640`, 5 February 2026)
moves 8,000.00 → **7,999.98**, so the product balance rises by two cents to **103,245.12**. Under the
whole-baseline substitution the amount sought is `103,245.12 × 75 / 100 = 77,433.84` **exactly** — no fractional
cent at all — where it was `103,245.10 × 75 / 100 = 77,433.825`, an exact half cent. Both rounding modes now agree,
and `computations[2].baseline_result` records 77,433.84, which is what I compute from `baseline.rule`.

*The sweep, re-run independently and wider than the reworker's.* I instrumented `RND` and compared Python's
`round` against half-away-from-zero on the exact decimal argument of every call, over **64 paths and 380 calls**
across both tasks — for each policy, the gold path, the whole-baseline substitution and every factor-baseline
substitution, each evaluated on every upstream world it can be reached on (task 0: 46 paths, 302 calls; task 1:
18 paths, 78 calls). **Zero disagreements.** My revision-5 sweep on the same method found exactly one; it is gone
and nothing took its place.

*The reworker's reasoning about the lever — verified, with two corrections to the reasoning that do not touch the
fix.*

1. *That the midpoint is structural and the balance had to move* — **correct**. On the whole-baseline path the
   settlement base is the product balance (the carry-in share is nil at baseline) and the share is
   `P('reinstatement_payment_pct')`, a frozen base parameter of the Seasonal Terms programme. Neither is
   available, so the only reachable input is the balance.
2. *That the part payment is the only free money figure* — **correct**, and I checked it rather than took it.
   Every other amount on this member's books is determined: the seven invoices are quantity × unit price
   (128 × 895.00, 96 × 742.00, 134 × 96.25, 188 × 318.00, 74 × 505.00, 165 × 88.40, 30 × 62.00), the three
   discounts are percentages of their lines (1,068.48 and 896.76 at 1.5 %, 496.00 at 4 %), two payments are their
   invoices cleared exactly (71,232.00 − 1,068.48 and 59,784.00 − 896.76), the credit memo is 1,155.00 less the
   12 % restocking charge, and the prepay booking is 40 × 310.00. The only other loose figure is the seeded
   745.92 service charge, and that one is an input to both scored charges through `charges_standing`, so moving it
   would move the score. The part payment is the one figure that is free by construction — a member's partial
   remittance is not derived from anything.
3. *The bound of "roughly −0.53…+1.33"* — **correct on the basis stated, but that basis is not the operative
   envelope.** On the criterion the reworker names — the scored service charge holding while `charge_at_rate`
   stays at 570.40 — the window on the balance is 105,955.73…105,957.59 around 105,956.26, i.e. −0.53…+1.33, and I
   reproduce it. But the criterion that actually has to hold is stronger: all three scored figures unchanged **and
   every path midpoint-free**. Scanning the balance cent by cent under that criterion, the admissible set is
   **−0.50…+0.28 with gaps**, 60 admissible cents out of the 79 in that span; above +0.28 a midpoint reappears
   elsewhere (halving an odd cent in `charge_after_relief`). The chosen +0.02 sits comfortably inside both. So the
   fix is sound and the stated bound would, if relied on as the envelope, license values that reintroduce the
   defect.
4. *"Midpoint-free only when the product balance's cents are divisible by four"* — **too strong as stated.**
   Writing the balance as P cents, the amount sought is 3P/4 cents, whose fractional part is 0 when P ≡ 0,
   0.75 when P ≡ 1, **0.5 when P ≡ 2**, and 0.25 when P ≡ 3 (mod 4). So the path is midpoint-free unless
   P ≡ 2 (mod 4) — three residues out of four, not one. The old balance was 10,324,510 cents ≡ 2, the new is
   10,324,512 ≡ 0, and my cent-by-cent scan confirms admissible values at other residues. The chosen value
   satisfies the narrower claim as well as the true one, so again: right fix, imprecise reason.

*The re-threading is a whole-ledger operation, checked the way I checked revision 5's.* I re-threaded all three
accounts from zero against every `balance_after`: task 0's Seasonal Terms account closes at **173,003.04**,
its prepay account at **−496.00** receivable and **12,400.00** prepay, task 1's at **24,010.00 / 7,665.00** — each
matching its holding, with **no date on any ledger failing to reconcile**. Crucially the re-threading reached the
holding: `agronomy_accounts.0d5ab8b9-….current_balance` moved 173,003.02 → **173,003.04** along with the five
downstream `balance_after` values, which is what makes it a ledger operation rather than a row edit.

*The seed note was rewritten and the base test it turns on still holds.* The note now reads *"Part payment of
7999.98 against IN-4410953 on 5 February 2026 by check, the odd balance the member had left to send, a route the
programme allows. Nothing on the account had passed its due date by that day — the earliest, IN-4407955, fell due
on 7 March 2026 — so the programme's 25.0 percent minimum on a part payment of an overdue balance does not engage
…"*. I re-checked every due date on the account against 2026-02-05: the earliest is indeed 2026-03-07, so base
`agronomy_payment_application`'s minimum on a part payment of an **overdue** balance does not engage, exactly as
in revision 5.

*Twelve proof figures moved and nothing scored did* — reproduced. See `0.md` § revision_6 for the item-by-item
table; the two `baseline_result`s (3,769.67 → **3,769.68**; 77,433.82 → **77,433.84**), one factor sensitivity
(`quoted_figure_rounding` 37,022.99 → **37,023.00**, the other eleven of the twelve in those two computations
unchanged), and the closure intermediates each up two cents. Both edge-deletion figures (**361.10**,
**36,940.00**) and the both-edges figure (**45,300.00**) are unchanged, as claimed.

**No new defect and no regression.** Base section byte-identical; tool module untouched for the sixth round; the
charter itself unmoved, so the prerequisite graph, the three prerequisite sentences, the override declarations and
all 24 ladders stand on revision 5's verification by hash. My literal sweep over both tasks' `computations`,
`prerequisite_closure`, `evaluation_criteria` and `solvability_contract` leaves nothing unaccounted: task 0's
residue is 533.06 and 68,700.00, task 1's the five stated intermediates, all legitimate.

**What still rests on a reader seeing a binding — stated for the render layer.** Nothing in any normative sentence,
as far as this audit can find. Every interval names both endpoints (revision 5), every rounding names its mode and
no input reaches a midpoint (this revision), the bushel quantity names net and how it is netted (revision 5), the
day count on `restocking_rate` names both endpoints and the delivery it measures (revision 4), and every `LATEST`
and `MAX` names the ordering it uses — "the most recent crop protection line **invoiced**", "the day the most
recent of those charges was **posted**", "the highest unit price at which crop protection has **ever** been
invoiced". Two residuals, neither in a sentence a reader is given as policy and neither reachable on either world:

- the `cross_category[].note` annotation on `agronomy_ext_season_volume_discount` still says "the bushels the
  cooperative has taken in from them" without "net", where the rule, the `compute_basis` and both ladder `when`
  strings all say "net bushels … counted after the moisture shrink taken at unload"; the note is an authoring
  annotation about a cross-category read, not a rule;
- `booking_price` is described as "the price the most recent prepay **booking** on the account locked" without
  naming which date orders "most recent", where the compute uses `posted_date`. Each account in this difficulty
  carries exactly one prepay booking, so no ordering question arises on either world, and the tier that reads it
  does not fire in either gold run.

## revision_6 — closing checklist

All M tasks now PASS on all four relationships.

| item | state |
| --- | --- |
| per-task files one-to-one with the tasks, `_difficulty.md` alongside; old revisions traceable | **holds** — six revisions appended in order, no earlier text rewritten |
| every comparison section carries a PASS | **holds** — `0.md` and `1.md` § revision_6 are both PASS on all four |
| extended policies fully covered; scopes pairwise disjoint, each spanning a whole tree | **holds** — {1, 2, 3} and {4, 5}; union = all five |
| task tools and GT closed; each tool an independently generated, frozen uuid8 | **holds** — `task_tools.py` byte-identical across all six rounds |
| every tree: 1–3 prerequisite problems, ≥ max(n−1,1) `value_input` edges, ≥ 1 `owner=user` problem, no cycle; the difficulty's edges a DAG | **holds** — task 0: 2 problems, 2 edges, user root; task 1: 1, 1, user root; 1 → 2 → 3 and 4 → 5 |
| self-sufficient baselines giving definite numbers ≠ gold | **holds** — 12,790.68 / 3,769.68 / 77,433.84 / 1,295.60 / 233,385.75 against 15,196.00 / 320.20 / 37,030.00 / 5,083.25 / 228,136.14 |
| 4–6 factors, ≥ 2 `parameter`, ≥ 1 `method` per computation; per task ≥ 1 multi-source and ≥ 1 cross-difficulty | **holds** — 4 / 6 / 6 / 4 / 4; task 0 reads `custom`, `storage`, `grain`, `patronage`; task 1 reads `grain` |
| every ladder ≥ 3 tiers stated in full, tiers distinct in outcome, conditions and outcomes ones the business holds | **holds** — 24 of 24 |
| every factor bears weight against an honest baseline | **holds** — all 24 substitutions move the scored value, recomputed again this round |
| cross-difficulty evidence seeded and consistent with the other product's charter | **holds** — `custom`, `storage`, `grain`, `patronage`; the grain rows reconcile to `products/grain.yaml` in nine respects and the patronage rows to Class A's declared rate and split |
| every ledger reconciles to its holding | **holds** — all three accounts, no unreconciled date |
| prose determinate without the binding | **holds** — see the statement above; two non-normative residuals recorded |
| instantiation-stage gates re-run on the final form | **holds by citation** — orchestrator's round-6 block at 14:38, `check_traceability` green; not re-run by this auditor |

**Difficulty verdict, revision 6: PASSES the source-layer audit.** Observations standing and not grounds for
rework: OBS-4, OBS-7, OBS-8, OBS-12, OBS-13, the prepay-balance stamp note, and the two determinacy residuals
named above.

---

# revision_7 — re-audit, charter-global

## re_audit_frozen

| item | round 6 | round 7 | re-derived? |
| --- | --- | --- | --- |
| `agronomy.extended.yaml` | `e77a90eb2e24e3a5` | **`7e467c191418fb6a`** | **yes** — the only artifact that moved |
| `task_tools.py` | `fb62107a7cae45c5` | `fb62107a7cae45c5` (unchanged throughout) | carried forward by reference |
| masked view 0.json | `97e877b7ae0e71f2` | `97e877b7ae0e71f2` — **byte-identical** | world did not move |
| masked view 1.json | `bd5be12e6cdbd284` | `bd5be12e6cdbd284` — **byte-identical** | world did not move |
| `tasks/0.json` | `84d2cebb57024e92` | **`03c43f2e038ce2d8`** | see § `what moved` |
| `tasks/1.json` | `c33e1aea6d8373fb` | **`6f016537985e2075`** | proof fields re-read; `design_rationale` gained a ROUND 7 section |
| `blueprint/products/agronomy.yaml` | `66127eecc1f99b7b` | `66127eecc1f99b7b` | base section re-verified byte-for-byte |

Revisions 1–6 are left exactly as they stand. This round is narrow by construction: the render-layer auditor
returned PASS on all three parts for both tasks, and what was asked for is that one inference across documents be
replaced by a sentence. I have checked that sentence and re-run every standing check; I have not re-opened the
`booking_price` residual, as instructed.

**Per-field digests, recorded so a future round can diff them directly** (sha256[:16] of the canonical JSON):

| field | task 0 | task 1 |
| --- | --- | --- |
| `initial_state` (= `db_closure`) | `c69db99192585c57` | `eb4fa76d10716227` |
| `evaluation_criteria` | `8a90b3ea9a7adb7a` | `d86acbaa2eeeaaa6` |
| `computations` | `32cfe7ee0236c0ae` | `9178fd02bc116768` |
| `prerequisite_closure` | `a4dce5e1d67ded39` | `ca29389731253afa` |
| `solvability_contract` | `4419a55a5b6e5ab5` | `be09be945bf8c765` |
| `charter_scope` / `required_documents` | `024dcabdd5d7c11a` / `1efefd3c97e05f44` | `ff904b125e963169` / `16dfda8ae6b0d4dc` |
| `design_rationale` | `0c7917fb67dfe4f4` | `1f5880032c75799c` |

`db_closure` is identical to `initial_state` on both tasks and `db_closure_matches_initial_state` is `true`.

## revision_7 — what moved

One qualification, inside **exactly one policy**, `agronomy_ext_prepay_booking_ceiling`: *"less every discount
granted on the account **as a discount line of its own, which is an early pay, volume, prepay or programme rebate
discount and never the restocking charge withheld inside a credit memo**"*. I located every occurrence:

| location | occurrences |
| --- | --- |
| `rule` — the three sentences of the prior-spend ladder | 3 |
| `baseline.rule` — the fall-through sentence | 1 |
| `compute_basis` — `open_months`, `spend_recent`, `spend_two_season`, `discounts_standing` (1 each) and `prior_net_spend` (which quotes all three rule sentences) | 5 entries, 7 occurrences |
| `factors[prior_season_spend_basis].ladder` — all three `method` texts | 3 |
| **total** | **10 distinct places, 14 occurrences**, all in one policy |

No other policy carries it, and nothing else in the charter changed: 79 mode-bearing rounding statements, 24
"to the handling date" phrases, factor counts still 4 / 6 / 6 / 4 / 4 with 3 / 4 / 5 / 3 / 3 `parameter` and
1 / 2 / 1 / 1 / 1 `method`.

**`tasks/0.json`'s hash moved and I can exhibit no content change.** Its masked view is byte-identical by the
orchestrator's own hash; its `charter_scope`, `required_documents`, `evaluation_criteria`, `computations`,
`prerequisite_closure` and `solvability_contract` all reproduce field for field against my own recomputation; its
`design_rationale` ends at ROUND 6 with no round-7 entry; and the new phrase, the round-7 sweep figures and every
other round-7 signature are absent from the file entirely. I record the hash move as re-serialisation and note
plainly that I could not exhibit a content difference — the reworker's "task 0 not touched" is true of its content
as far as this audit can verify.

## revision_7 — the five things asked for

**1. The binding was checked first, and it does exclude the credit memo.** `discounts_standing` is
`SUM('agronomy_invoices','amount', event_type='agronomy_discount_granted')`. A credit memo is a row of a different
family — `agronomy_credit_memo_issued`, a distinct value of the `event_type` enum — and its 370.66 sits in the
`discount_amount` field, which this binding does not read; the binding sums `amount`. So the misreading is
excluded twice over, by row kind and by field, and the prose was moved to the binding rather than the binding to
the prose. **Had the binding admitted the credit memo the opposite fix would have been right, and it does not.**
I reproduced the misreading end to end to be sure it is the one the sentence closes:
`discounts_standing −6,323.25 − 370.66 = −6,693.91` → `prior_net_spend 213,994.01` → `gross_ceiling 235,393.41` →
booking **227,728.41**, exactly the render layer's figure, against the binding's **228,136.14**.

**2. The sentence says in business words exactly what the binding does, and introduces no new reading.**
- *"as a discount line of its own"* is the row-kind restriction, which is precisely the `event_type` filter.
- *"an early pay, volume, prepay or programme rebate discount"* is the **complete** `discount_type` enum of
  `agronomy_invoices` — `[early_pay, volume, prepay, program_rebate, none]` — minus the null value, in the enum's
  own order. This is the check that mattered: had the list omitted a kind, the sentence would be narrower than the
  binding and would itself be a fresh defect. It is not; the four kinds exhaust what a discount row can carry.
  (`none` is the value for rows carrying no discount at all, so no `agronomy_discount_granted` row can hold it.)
- *"never the restocking charge withheld inside a credit memo"* uses the **frozen base charter's own gloss** for
  that field: `agronomy_credit_memo_issued.discount_amount` is defined there as *"the restocking charge withheld
  from the credit"*, and base `agronomy_returns_and_credits` calls it *"the programme's restocking charge"*, never
  a discount. So the words are inherited, not invented.
- It adds **no window, no date field, no sign convention, no threshold and no new condition**; "every discount
  granted on the account", unwindowed, is untouched.

**3. It reaches a reader of either document.** The KB renders one computation document from the baseline and one
document per declared factor. The qualification is in `baseline.rule`, so the computation document carries it, and
in all three `method` texts of `prior_season_spend_basis`, so that factor's document carries it too — as well as in
the policy `rule` and five `compute_basis` entries. A reader who finds only the computation document and a reader
who finds only the factor document each meet it.

**4. The `compute_basis` copies are still verbatim.** I re-ran the substring check over the whole charter: every
sentence of every `compute_basis` entry and of every `baseline.rule` is still a verbatim, whitespace-insensitive
substring of its own policy's `rule` — **zero misses**, including the five entries that grew. The full structural
sweep (orphan bases, missing bindings, fall-through ≠ baseline, overlapping binding sets, prerequisite sentences)
returns **zero issues**.

**5. No scored figure moved, and nothing regressed.** Re-derived from the round-7 charter on both byte-identical
worlds: task 0 **15,196.00 / 320.20 / 37,030.00**, task 1 **5,083.25 / 228,136.14**. Whole baselines 12,790.68 /
3,769.68 / 77,433.84 / 1,295.60 / 233,385.75; all twenty factor sensitivities unchanged; edge-deletion figures
361.10, 36,940.00, 45,300.00 and 233,727.71 unchanged. Both standing sweeps re-run on my own instrumentation:
the **mode sweep over 64 paths and 380 calls returns zero disagreements** (mine is wider than the reworker's 42/220
because I evaluate each policy on every upstream world it can be reached on), and the **literal sweep leaves
nothing unaccounted** — task 0's residue is 533.06 and 68,700.00, task 1's is 3.15, 3,335.00 and 220,687.92, all
legitimate stated intermediates. Base section byte-identical; tool module untouched for the seventh round; the
prerequisite graph, its three sentences, the override declarations and all 24 ladders stand.

## revision_7 — findings

**No defect introduced and nothing regressed.** The change does what was asked and no more: one qualification, one
policy, ten places, both documents, verbatim copies intact, no binding, ladder, tier, parameter, seed row or tool
touched, and no figure moved.

**OBS-17 — observation for the render layer, not a red light and not introduced this round.** The same sentence
shape — "every discount granted on it", unqualified — still stands in the two policies task 0 claims, and their
bindings are the identical `SUM(..., event_type='agronomy_discount_granted')`. I tested the analogous misreading on
task 0's world, adding that account's seeded credit-memo `discount_amount` of 138.60 as though it were a discount:

- in `agronomy_ext_arrears_service_charge` it is **arithmetically inert**, and exactly so: `overdue_balance`
  subtracts the discounts while `charge_base` adds the clawed-back share of them back at 100 %, so a phantom
  addition cancels — `charge_base` stays 105,956.28 and the scored charge stays **320.20**. This is presumably the
  residual the render layer called inert;
- in `agronomy_ext_arrears_settlement_payment` it is **not** inert: `product_balance` 103,106.52,
  `settlement_base` 103,639.58, amount sought 57,001.77, net 36,946.77, quoted **36,950.00** against the scored
  37,030.00.

I none the less record this as an observation rather than a red light, because the second reading is not
*defensible* and the difference from policy 5 is the reason. Policy 3's own sentence already names credit memos as
a term of their own — *"less every payment posted to the account, **every credit memo written on it** and every
discount granted on it"* — so a reader who then added a figure from inside a credit memo would be counting part of
a row the same sentence has already had them subtract in full. Policy 5's sentence carried no credit-memo term at
all, which is precisely what made that one decisive. So task 0's protection is structural where task 1's is now
explicit, and the render layer, which owns document-level determinacy and has already passed both tasks, is the
right place for that asymmetry to be weighed rather than here.

**Determinacy statement, updated.** Nothing in any normative sentence of this charter rests on a reader seeing a
binding, with the two residuals previously recorded: the `cross_category[].note` annotation that omits "net" (an
authoring annotation, not policy prose) and `booking_price`'s "most recent prepay booking" not naming its ordering
date (left standing by instruction; it fires in neither task, and each account carries exactly one booking).
OBS-17 is added to that list as an asymmetry in explicitness, not as an under-determination that yields a
defensible second value.

## revision_7 — closing checklist

Unchanged from revision 6 and re-verified item by item: per-task files one-to-one with the tasks with seven
traceable revisions; both comparison sections PASS; extended policies fully covered with pairwise-disjoint scopes;
tool and uuid8 closure; both trees within bounds with an `owner=user` write each and the difficulty's edges a DAG;
self-sufficient baselines giving definite numbers different from gold; factor counts, ladder structure and every
factor bearing weight; cross-difficulty evidence seeded and charter-consistent; all three ledgers reconciling to
their holdings; prose determinate without the binding; and the instantiation-stage gates re-run on the final form
by the orchestrator at 15:46 with `check_traceability` green.

**Difficulty verdict, revision 7: PASSES the source-layer audit**, as at revision 6, with the round-7 tightening
verified and one new observation (OBS-17) recorded for the render layer.
