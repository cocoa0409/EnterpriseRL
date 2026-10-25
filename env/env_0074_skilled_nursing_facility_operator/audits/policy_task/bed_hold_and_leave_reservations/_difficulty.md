# Policy-task audit — bed_hold_and_leave_reservations / charter-global

## revision_1

## charter_global_frozen
- Frozen: between 2026-10-22 05:16:44 and 05:20:52 UTC (system clock before writing / at reveal; timestamp corrected post-hoc from an estimate, content unchanged), before any task's GT was revealed. Auditor: independent policy auditor (erl-task-policy-audit), not the instantiating agent.
- Source hashes (sha256): `bedhold.extended.yaml` adf5c3c4ff0322c7190061e809ca649cbef07c5be9057aeecf22dac7e2ccb424; `task_tools.py` 1c2088242f7f8522b31b02d8c4e485b66c734f92816b601227a38b66b65875f9 (both match the coordinator's snapshot).
- Read: blueprint.yaml, db_schema.json, share_tools.py, products/bedhold.yaml (plus products/private.yaml, medicare.yaml, medicaid.yaml for cross-category rules and tier parameters), the extended charter, task_tools.py, audits/render_source/XF_recipe.md, the two masked views (hashes 2e2f0bd1…f520, 237fc753…20f5 verified), and the DSL evaluator in skills/erl-task-instantiate/scripts/check_compute.py (to evaluate the charter's own compute on the views).
- Masked / unread at freeze: tasks/*.json, worklog.md (difficulty and scenario level), plan.md, every audits/ file other than XF_recipe.md, other scenarios.
- Entry conditions (Step 0): gate snapshot supplied (7 gates rc=0; check_traceability deferred by the coordinator), masked views and hashes supplied. Complete.
- Base copy: every top-level key of the extended file other than `extended_policies` is identical to blueprint/products/bedhold.yaml (programmatic equality check).

### policy_conflict_scan
Five extended policies:

| policy | subject / computes | target tool (owner) | scope |
| --- | --- | --- | --- |
| bedhold_ext_closing_private_days | bedhold_day_booked / day_count | book_closing_private_days_bb96678f (agent) | closing month of a Medicaid Hospital Leave Reserved Bed or Private Pay Hospital Leave Bed Hold |
| bedhold_ext_opening_extension_charge | bedhold_charge / amount | sign_opening_extension_charge_f06dae64 (user) | opening-month extension entry of a Medicaid Hospital Leave hold |
| bedhold_ext_closing_extension_charge | bedhold_charge / amount | sign_closing_extension_charge_a05fa8e4 (user) | closing-month extension entry of a Medicaid Hospital Leave hold whose leave has ended |
| bedhold_ext_skilled_hold_days | bedhold_day_booked / day_count | book_skilled_hold_days_804a4481 (agent) | closing month of a Medicare Skilled Stay Hospital Leave hold whose first month is booked |
| bedhold_ext_skilled_hold_charge | bedhold_charge / amount | sign_skilled_hold_charge_7094169f (user) | closing-month entry of a Medicare Skilled Stay Hospital Leave hold whose hold has ended |

- Overlapping subjects: the two booking policies are disjoint by tier (MA/PP hospital vs Medicare skilled hospital); the three charge policies are disjoint by entry and each overwrite of `bedhold_evt_charges` excludes its own case and both siblings' cases by name (XF 17 PASS).
- Triggers / eligibility / time anchors: all five read the same midnight-census last-held-day ladder; the three charge policies share the same notice, isolation, schedule, extended-hold, meal and program ladders with identical parameters (the restated schedule rates equal products/private.yaml `daily_rate_schedule` 2025-07-01 / 2026-07-01 for all six tiers). No two policies give different values for the same entry.
- Conflicts with base found in the scan: see findings CG-3 (late-renewal "lost days" vs base expiry) and CG-4 (closing_private_days vs base per-month booking and late-election clause). Both are undeclared overrides.
- Cross-category read boundaries: medicaid (status, eligibility_start_date), private (isolation_placement, rate_notice_delivered_date, tier params rate_change_notice_days / secure_unit / bariatric_weight_threshold_lb / beds_per_room), medicare (medicare_ledger.to_date, tier param interrupted_stay_return_days). All are read-only reads; no task tool writes another category (XF 25 PASS: the tools write bedhold_day_booked, whose base trigger lands in bedhold:bedhold_charge, and bedhold_charge, which has no trigger).
- Task scopes (pre-reveal, inferred from the views only): task 0's world is a Medicaid Hospital Leave hold (claims closing_private_days, opening_extension_charge, closing_extension_charge); task 1's world is a Medicare Skilled Stay Hospital Leave hold (claims skilled_hold_days, skilled_hold_charge). Jointly complete over the five policies and disjoint; to be confirmed against `charter_scope` at reveal.

### rule_compute_equivalence
- Every `compute_basis` quotation is verbatim in its own rule and every `baseline.rule` sentence is in the rule (scripted whitespace-normalised sweep, XF 9 PASS). Every ladder tier named in `factors[].ladder` is a rule sentence and a branch of its `decides` binding, and vice versa (manual sweep of all 25 factors).
- Rounding: the rule's "rounded half up to the cent once on the total" matches the single `RND(…, 2)` on `result` in all three charge policies (XF 10 placement PASS; RND is the DSL's float round).
- Breaks found (findings CG-1, CG-2): the "earliest delivery" of the transfer notice is computed as a per-recipient LATEST, and several LATEST record selections are reversal-blind and have no stated tie rule.
- No factor binding reads another factor's binding (scripted sweep over all five computes, XF A1 PASS); shared record selections are plain bindings (XF A2 PASS). Assembly/order sentences name adjustment kinds only (percent, credits, days not charged, days lost, cap, courtesy days) and are needed because the adjustments do not commute (XF A3/A4 PASS).

### action_binding_and_uuids
- Each (target_tool, computes) pair is claimed by exactly one policy. uuid8s bb96678f, f06dae64, a05fa8e4, 804a4481, 7094169f: pairwise distinct, no shared prefix/suffix, no sequence pattern. PASS.
- No factor id is a substring of a tool name (XF 20 PASS). No composed string arguments (XF 21 PASS). Every write tool calls ctx.create and ctx.update in its own body (XF 22 PASS). No datetime/time/random/uuid/secrets substring in task_tools.py (XF 23 PASS). Both frozen_time values use `YYYY-MM-DD HH:MM:SS TZ` (XF 24 PASS).
- Tools do not judge prerequisites: no body reads a prerequisite state or refuses (all five bodies create the row unconditionally).
- Failures: docstring ordering words / naming another action (CG-11) and docstring promises the bodies do not enforce (CG-12).

### prerequisite_graph
- `prerequisite` is present on all five policies (`[]` on closing_private_days, opening_extension_charge, skilled_hold_days).
- Edges: closing_extension_charge -> closing_private_days (value_input, gate close_days, state); closing_extension_charge -> opening_extension_charge (state_gate, gate bedhold_ledger.days_entry_id, state); skilled_hold_charge -> skilled_hold_days (value_input, gate skc_days, state). Every `problem` is another extended policy id; the graph is acyclic.
- Each `policy_source` is verbatim in the blocked policy's own rule (scripted). `form` is state on all three, no fallback_reason, correct. `resolved_by` equals the depended-on policy's target_tool. `kind` matches `gate`: close_days and skc_days are bindings of the blocked compute; days_entry_id is the charge's link field.
- No authoring-viewpoint phrasing in the prerequisite blocks.
- Observation P-1: the skilled edge's `condition` adds "whose to_date is that last held day", which the sentence ("a booked resident-private entry for the month in which the hold ended") does not say; no producible world was found where the two diverge (an October entry ending before the last held day is not producible under the base booking rule), so it is an observation.

### prerequisite_sentences
1. "The closing-month extension charge is fixed only after the reservation carries a booked resident-private entry holding every privately held day of the leave through its last held day." Connective "only after"; state form (a booked resident-private entry on the ledger, in finder words); no tool, id or snake_case; scope matches the condition. Writer: only bedhold_ext_closing_private_days books a resident-private entry for a Medicaid/Private Pay hospital leave (book_skilled_hold_days is scoped by its rule and docstring to skilled-stay reservations). Derivation: sentence + the ledger (latest resident-private entry ends before the last held day) + closing_private_days' rule ("books the privately held days of the month in which a hospital-leave hold ends") -> book that month's entry. One reading. PASS.
2. "The closing-month extension charge is not posted until each earlier resident-private entry of the leave carries its own bed-hold charge." Connective "not … until"; state form; writer for the opening-month extension entry: only bedhold_ext_opening_extension_charge. Derivation: an uncharged earlier entry on the ledger + the opening policy's rule ("the resident-private entry booked for the service month in which the hold's last payer-reserved day falls … the resident or representative signs") -> hand over that signing. PASS. Observation P-2: an earlier entry that is neither the opening-month extension entry nor the closing entry (a leave spanning three or more private months) is priced under base, and no write of this difficulty charges it, so the gate would be unresolvable inside the difficulty; not present in the task worlds.
3. "The skilled-hold closing charge is worked out only after the reservation carries a booked resident-private entry for the month in which the hold ended." Connective "only after"; state form; single writer bedhold_ext_skilled_hold_days. PASS.
- No rule carries a second wording, a tool name or another problem's id; the depended-on rules do not restate the sentences. No undeclared cross-problem order found in any rule. The docstrings are not silent about sequence (CG-11).

### override_declarations
Sentence by sentence against each `base_policy_refs` entry:
- closing_private_days (overwrite []), refs bedhold_evt_day_counting / agg_payer_day_limits / election / hold_end:
  - follows: midnight census (return day not a leave day, departure day counts), bookable states, reversal sentences, payer-day limits ("up to the per-hospitalization limit": the reserve ladder stays at or under the limit), written election required for a private hold, at most the private hold maximum per written election.
  - departs, undeclared: (a) bedhold_evt_day_counting "Held days are booked per service month and day payer at month end or when the leave ends." vs "the resident-private entry for that closing month carries the privately held days of the leave not yet booked" (the rule itself says "every other held-day booking stays under the base rule", so the author treats this booking as outside base; sibling skilled_hold_days declared the same departure) — CG-4; (b) bedhold_election "a later election holds it only from the day of election" vs the leave's privately held days counted from the departure date / end of the reserve with no late-election branch — CG-4; (c) bedhold_hold_end "A hold expires … when the private hold maximum is reached without a renewal" and bedhold_election "a private hold runs at most the private hold maximum days before it must be renewed in writing" vs the late-renewal "lost days" sentence that keeps the hold running past an unrenewed maximum — CG-3.
- opening_extension_charge / closing_extension_charge / skilled_hold_charge: overwrite of bedhold_evt_charges' pricing clause declared; replaced_by restates out-of-scope pricing but drops "whatever payer source covers the resident's stay otherwise" (CG-13). bedhold_evt_notice followed (days before the notice never charged); "Bed-hold charges for a month are billed on the statement day of the following month" vs "the signed charge is what posts": observation O-4 (the base sentence fixes billing timing, not the posted amount; no scored value differs).
- skilled_hold_days: overwrites of the booking-time sentence and the election-window sentence are declared and their replaced_by restate the out-of-scope text; the bedhold_hold_end expiry sentence is not overwritten although skilled_renewal_gap departs from it (CG-3).

### factor_ladders
| policy | factor | label | decides | tiers | multi-source | cross_difficulty | charter-global verdict |
| --- | --- | --- | --- | --- | --- | --- | --- |
| closing_private_days | ma_reserve_allowance | parameter | ma_reserve_days | 3 | yes (MA case + departure) | medicaid | baseline 0 contradicts in-force base payer-day limit (CG-9) |
| | last_held_day_rule | method | last_held_offset | 4 | no | — | shape PASS (data-selected end date); baseline contradicts base midnight census (CG-9); outcome stamped on reservation.end_date (CG-10) |
| | late_renewal_gap | parameter | renewal_lost_days | 3 | yes (elections + ledger) | — | fails T2 (CG-5); departs from base (CG-3) |
| | written_cover_cap | parameter | written_cover_days | 3 | no | — | PASS |
| opening_extension_charge | unnoticed_opening_days | parameter | open_unnoticed_days | 3 | yes (notice row + entry) | — | baseline contradicts base bedhold_evt_notice (CG-9) |
| | isolation_rate_opening | parameter | open_price_tier | 3 | yes (agreement + reservation) | private | structure PASS |
| | notice_schedule_opening | method | open_prior_rate_days | 3 | yes | private | fails method shape (CG-6) |
| | extended_hold_opening | parameter | open_hold_pct | 3 | no | — | long-hold tier unreachable (CG-7) |
| | meal_credit_opening | parameter | open_meal_credit | 3 | no | — | structure PASS (realism O-2) |
| | program_credit_opening | parameter | open_program_credit | 3 | no | private | structure PASS (realism O-2) |
| closing_extension_charge | isolation_rate_closing | parameter | close_price_tier | 3 | yes | private | PASS |
| | notice_schedule_closing | method | close_current_rate_days | 3 | yes | private | fails method shape (CG-6) |
| | extended_hold_closing | parameter | close_hold_pct | 3 | no | — | PASS |
| | meal_credit_closing | parameter | close_meal_credit | 3 | no | — | PASS (O-2) |
| | program_credit_closing | parameter | close_program_credit | 3 | no | private | PASS (O-2) |
| skilled_hold_days | written_hold_start | method | skilled_start_offset | 3 | yes (election + notice) | — | shape PASS; baseline contradicts base election clause and its own replaced_by (CG-9); reads a field the records lack (CG-14) |
| | skilled_last_held_rule | method | skilled_last_held | 4 | no | — | as last_held_day_rule (CG-9, CG-10) |
| | skilled_renewal_gap | parameter | skilled_gap_days | 3 | yes | — | fails T2 (CG-5); CG-3 |
| | skilled_cover_cap | parameter | skilled_cover_days | 3 | no | — | PASS |
| | interrupted_stay_courtesy | parameter | skilled_courtesy_days | 3 | yes (Part A ledger + departure) | medicare | unreal ladder (CG-8) |
| skilled_hold_charge | isolation_rate_skilled | parameter | skc_price_tier | 3 | yes | private | PASS |
| | notice_schedule_skilled | method | skc_current_rate_days | 3 | yes | private | fails method shape (CG-6) |
| | extended_hold_skilled | parameter | skc_hold_pct | 3 | no | — | PASS |
| | meal_credit_skilled | parameter | skc_meal_credit | 3 | no | — | PASS (O-2) |
| | program_credit_skilled | parameter | skc_program_credit | 3 | no | private | PASS (O-2) |
| | housekeeping_credit_skilled | parameter | skc_housekeeping_credit | 3 | no | private | PASS (O-2) |

Declared counts: 4 / 6 / 5 / 5 / 6 factors; every policy declares ≥2 parameter and exactly 1 or 2 method. After the charter-global strikes (CG-5, CG-6, CG-7; CG-9/CG-10 are demonstrated per task), every charge policy has 0 surviving `method` factors and both booking policies lose their method factors on their task worlds (see task files). Ladders are disjoint as stated and every value or method comes from the charter. Fall-through tiers equal the declared baselines.

### findings
Each charter-global finding names the tasks it bears on; the demonstration of its cost for a specific task is in that task's file.

**CG-1 — SOURCE-POLICY RED (rule/compute; XF 11, 12).** Symptom: "a transfer notice counts from its earliest delivery to the resident or the representative" is computed as `MN(LATEST(... delivered_to='resident'), LATEST(... delivered_to='representative'))`, i.e. the latest delivery to each recipient. Root cause: per-recipient LATEST where the rule says earliest. Members (all read sites): opening_extension_charge open_notice_to_resident / open_notice_to_representative -> open_notice_date; closing_extension_charge close_notice_to_resident / close_notice_to_representative -> transfer_notice_on_file; skilled_hold_days hold_notice_to_resident / hold_notice_to_representative -> hold_notice_first; skilled_hold_charge skc_notice_to_resident / skc_notice_to_representative -> transfer_notice_on_file. Demonstration: task 0's world plus a second transfer-notice delivery to the representative dated 2026-09-12 (producible: base "A notice of each type is recorded once per delivery time"). The rule's earliest delivery stays 2026-09-10 and the opening charge stays as on the unmodified world (7793.10). The compute moves to 2026-09-12 and gives 7050.90. Bears on: both tasks structurally. Neither scored world has a second delivery, so no scored value moves.

**CG-2 — SOURCE-POLICY RED (XF 11, 12: reversal-blind and tie-unstated selections).** Members: opening open_month (LATEST payer_reserved booked entry, reversals ignored; the rule says "the service month in which the hold's last payer-reserved day falls"), open_from / open_to (LATEST by to_date within that month); closing close_days / close_from / close_to; skilled_hold_charge skc_days / skc_from / skc_to; skilled_hold_days first_entry_from and hold_signed_at ("the written hold election"; latest by created_at, no tie rule). Demonstrations: (i) a payer-reserved booking reversed in full (base: "booked in error is reversed against its booked entry") leaves its month as open_month, although no payer-reserved day falls in it. (ii) A closing entry reversed for billing_error and rebooked with the same to_date ties on to_date. LATEST keeps whichever row was inserted first, and the rule states no tie rule. Bears on: both tasks structurally. No scored world contains such rows.

**CG-3 — SOURCE-POLICY RED (undeclared override, check 1).** Symptom: late_renewal_gap (closing_private_days) and skilled_renewal_gap (skilled_hold_days) keep a hold running after the first private period ends unrenewed, and take the "lost" days out. Quotes: base bedhold_hold_end "A hold expires when payer-covered days are used up with no private extension, …, when the private hold maximum is reached without a renewal, or for an unpaid private hold." Base bedhold_election "a private hold runs at most the private hold maximum days before it must be renewed in writing." Extended: "where two or more written private elections are on file and the latest private extension takes effect more than one day after the first period's last day, the days strictly between the period's last day and that effective date are lost to the leave". Under base the hold expires on the period's last day, so the last held day is that day. Under extended the hold continues to the return or release. Neither policy's overwrite names bedhold_hold_end or the election renewal sentence. It is also unrealistic: a lapsed bed hold does not revive with the same room. Bears on: task 0 and task 1. Both worlds have a renewal that lapsed by 3 or 2 days, and both files demonstrate the second value.

**CG-4 — SOURCE-POLICY RED (undeclared override, check 1).** closing_private_days departs without an overwrite from (a) bedhold_evt_day_counting "Held days are booked per service month and day payer at month end or when the leave ends". On a world where an earlier private month is unbooked, the closing entry carries that month's days as well, while base books them in their own service month. The sibling skilled_hold_days declared exactly this departure, and the rule's own "every other held-day booking stays under the base rule" shows the author treats this booking as outside base. It also departs from (b) bedhold_election "a later election holds it only from the day of election". Example: a Private Pay Hospital Leave hold, notice delivered on the departure day, written hold election on day 5, return on day 10. Base gives privately held days 5–9 (5 days). The extended count runs from the departure date and gives 10. Bears on: task 0 structurally only (September is booked and its extension election was timely, so task 0's value does not move).

**CG-5 — SOURCE-FACTOR RED (XF A6 T2).** late_renewal_gap and skilled_renewal_gap. With every other factor at its baseline (start at the departure date, last held day = posting date, cap = one private hold maximum period), the counted span always contains the whole first private period. That is at least private_hold_max_days = 30 days that are never in the gap, so the baseline cap binds. The gap tier could move the result only if the renewal took effect after the posting date. Base election rules make an election effective no later than its own day, so no such world is producible. No producible world exists where either factor moves the result alone. Check on task 0's world: all other factors at baseline give 8 with or without the gap factor.

**CG-6 — SOURCE-FACTOR RED (XF A7 method shape).** notice_schedule_opening, notice_schedule_closing, notice_schedule_skilled. The tier pair "no rate notice -> every day at the prior schedule's rate" and "otherwise -> every day at the current schedule's rate" is the same combination (charged days × one constant schedule rate) and differs only by a constant multiplier, so the pair fails the pairwise shape test. These are the only `method` factors of the three charge policies, so each charge policy is left with 0 method factors.

**CG-7 — SOURCE-FACTOR RED (unreachable tier).** extended_hold_opening tier "more than the long-hold threshold days" (30). The opening-month extension entry is booked for the month that contains the hold's last payer-reserved day. At least one day of that month (at most 31 days) is therefore payer-reserved, so the entry holds at most 30 privately held days and the tier never fires under the rule's own definition. It can fire only through the reversal-blind open_month read of CG-2. That leaves the ladder with 2 producible tiers.

**CG-8 — SOURCE-FACTOR RED (unreal ladder).** interrupted_stay_courtesy tier 2: "where the latest day the resident's Part A ledger books as a covered day is the day before the departure, the interrupted-stay window days are courtesy days". (i) The condition holds for every Medicare Skilled Stay hospital-leave hold that does not end with a return inside the window. Medicare's own rules close Part A booking "early at the last covered date", and a hospital transfer without return ends coverage on the day before departure ("hospital_transfer_no_return … post directly from active"). The fall-through is therefore reachable only through an incomplete Part A ledger, which XF 29 forbids, so the condition restates the tier's scope rather than dividing its customers. (ii) The value takes the window days (the departure day and the next two) off the closing month's entry. Those days lie at the start of the leave, usually in another month, and may never have been privately held. No SNF publishes a credit for days it never charged. The rule's own rationale ("comes back within Medicare's interrupted-stay window") does not apply to residents who did not come back. Bears on: task 1 (demonstrated there).

**CG-9 — SOURCE-FACTOR RED (straw-man baselines against in-force base clauses).** Each factor's tier restates a base sentence that stays in force, while its baseline contradicts that sentence. A reader of the base document therefore computes the factor's value without the factor's document.
- ma_reserve_allowance: baseline 0 vs bedhold_agg_payer_day_limits "Medicaid hospital reserved days count per hospitalization, consecutively from the departure date, up to the per-hospitalization limit".
- last_held_day_rule and skilled_last_held_rule: baseline = posting date vs bedhold_evt_day_counting "the return day never counts" and the variant parameter release_effective_basis "day_after_release = the day of release is the last held day".
- unnoticed_opening_days: baseline 0 vs bedhold_evt_notice "No day held before the transfer notice was delivered is ever charged to the resident". The sibling closing and skilled charge policies put this same rule inside their baseline.rule.
- written_hold_start: baseline = the departure date vs base "a later election holds it only from the day of election" and its own replaced_by "a written hold election signed two or more calendar days after … holds the bed only from its signing date".

Demonstrated per task.

**CG-10 — stamps (per-task demonstration).** bedhold_reservations.end_date ("last held day") records the outcome of last_held_day_rule and skilled_last_held_rule on every ended reservation. bedhold_reservations.private_hold_start_date ("first day held at the resident's expense") records the outcome of the reserve and start factors.

**CG-11 — RED (check 3; XF 19).** Docstrings carry ordering words or name another action. book_closing_private_days_bb96678f: "The new entry is then visible … and it is the entry a private bed-hold charge for that month is later signed against." book_skilled_hold_days_804a4481: "The entry then shows on the reservation's ledger … the entry a private bed-hold charge for that month is signed against." Both state a position in a sequence relative to the signing writes. Bears on both tasks.

**CG-12 — RED (XF 19, tool bodies vs docstrings).** sign_opening_extension_charge_f06dae64, sign_closing_extension_charge_a05fa8e4 and sign_skilled_hold_charge_7094169f all promise "a positive number … stored rounded half up to the cent". Their bodies store `round(float(amount), 2)`, which rounds half to even on binary floats (Python gives round(0.125, 2) = 0.12, where half up gives 0.13), and never check the sign. book_closing_private_days_bb96678f and book_skilled_hold_days_804a4481 promise YYYY-MM / YYYY-MM-DD fields "never empty" and a day count of "zero or more". Neither body enforces them. Bears on both tasks.

**CG-13 — RED (XF 15).** The replaced_by of all three `bedhold_evt_charges` overwrites (opening, closing, skilled) drops the retired clause's still-in-force words "whatever payer source covers the resident's stay otherwise" from the out-of-scope restatement. No scored value moves on either world.

**CG-14 — RED (XF 13).** skilled_hold_days' rule keys the first privately held day to the election's "signing date" ("signed two or more calendar days after …"). bedhold_elections has no signing-date field, only effective_date ("date the election takes effect") and created_at ("moment the election was logged"). The compute reads created_at. Bears on task 1, where the two fields differ (demonstrated there).

Observations (charter-global, not grounds for rework):
- O-1 (realism, scoped surfaces): the scoped schedules price different months of one hold differently. The first month of a skilled hold is priced under base (full room-tier rate, no isolation tier, no credits), and its closing month carries isolation pricing, an extended-hold percent and four credits. A published bed-hold schedule does not vary its pricing by which month of the hold an entry falls in. This comes from the accepted scoped-overwrite route (XF 31/32) and is left to the coordinator.
- O-2 (realism, credit stack): the private bed-hold schedule stacks an extended-hold discount (95 / 85 percent), a meal credit tiered by leave length (0 / 7.05 / 14.10), a specialty-program credit keyed to the private-pay agreement's tier rather than the room held, and, on the skilled closing entry only, a housekeeping credit keyed to the agreement tier's beds per room. Each could appear on a real schedule. Applying them only to scoped entries, and keying them to the agreement tier rather than the held room, is atypical.
- O-3: the transfer-notice "earliest delivery" phrase and the "the written hold election" singular have no stated tie rule (covered by CG-1 / CG-2).
- O-4: base bedhold_day_booked triggers bedhold:bedhold_charge for resident_private entries, and base bills bed-hold charges on statement day 3 of the following month. Extended posts the charge only when signed. The base text fixes timing, not amount, and no scored value differs.
- O-5: the charge tools never write the base event field daily_rate. A split prior/current daily charge cannot be expressed in one daily_rate.
- P-1, P-2: see prerequisite_graph and prerequisite_sentences.

## closing_checklist
Not closed: the four relationships do not PASS (see findings above and the task files). Gates are not re-run by this auditor.

## post_reveal_note (revision_1)
- Both tasks were revealed at 2026-10-22 05:20 UTC, after this file and both task derivations were on disk. Nothing above was edited after the reveal.
- charter_scope: task 0 claims closing_private_days, opening_extension_charge and closing_extension_charge with their three tools. Task 1 claims skilled_hold_days and skilled_hold_charge with their two tools. The scopes are pairwise disjoint and jointly complete over the five extended policies and five tools, as inferred in § policy_conflict_scan.
- Independent derivation vs GT: every scored argument and every computations figure (expected, baseline_result, factor_sensitivity) matches in both tasks.
- Why both tasks are still RED: the REDs are about the artifacts' proof and realism, not about the arithmetic.

VERDICT revision_1: task0=RED SOURCE-POLICY(CG-3 base-expiry second value),SOURCE-FACTOR(stamps end_date/private_hold_start_date,CG-9 straw-man baselines,CG-5,CG-6,CG-7,0 method after strikes,isolation tier on unproducible payer_converted room-change row),XF29 seed completeness task1=RED SOURCE-TASK(private_hold_start_date/election effective_date 09-22 vs signed 09-27),SOURCE-POLICY(CG-3),SOURCE-FACTOR(CG-8 courtesy,end_date stamp,CG-9,CG-5,CG-6,0 method after strikes),XF29 private ledger absent charter=CG-1,CG-2,CG-3,CG-4,CG-5,CG-6,CG-7,CG-8,CG-9,CG-11,CG-12,CG-13,CG-14

## revision_2

### charter_global_frozen (revision_2)
- Re-derived in full: both source hashes changed since revision_1. Written on 2026-10-22 before either task's revision-2 GT was opened. Auditor: the same independent policy auditor.
- Gate snapshot, from the coordinator's script `/tmp/erl0074_coord/snapshot.sh bed_hold_and_leave_reservations 2`, run by this auditor; it printed "snapshot … round 2 at 2026-10-22T07:45:47". All 7 gates are OK, so the input is complete:

  | gate | rc | output |
  | --- | --- | --- |
  | check_extended | 0 | EXTENDED OK |
  | check_task_tools | 0 | TASK TOOL CONTRACT OK |
  | replay_tasks --check | 0 | REPLAY OK |
  | check_solvability | 0 | SOLVABILITY OK |
  | check_compute | 0 | COMPUTE OK |
  | check_grounding | 0 | GROUNDING OK |
  | check_cross_fire | 0 | SCOPE OK |

- Source hashes printed by the script:

  | file | sha256 |
  | --- | --- |
  | task_tools.py | 0de61c60d6bad763fa66bd0a153b022d7b2ae56fffc70a739925f5a7d8cfb0a1 |
  | bedhold.extended.yaml | 0cf69a1464b5466bd49a088c96bd17580c095e6f7d577e85cdaff0f39e8e1238 |
  | task0.view.json | 0f9d9fc81a0da4ce554b0a33f16e50d6bc25a5027870c157e0d6f4b78cc00874 |
  | task1.view.json | e18b3f0fc0ec8b488d3fbce89da74a21e1b82f02e20916ed7af139db20beac5e |

- Base copy: still identical to blueprint/products/bedhold.yaml (programmatic check).
- Read for this revision:
  - the extended charter and task_tools.py in full;
  - the two rebuilt masked views;
  - XF_recipe.md;
  - the reworker's per-item report, relayed by the coordinator.
- Not read: worklog.md, plan.md, tasks/*.json.
- contamination_disclosure (applies to both task files):
  - I saw the revision-1 GT values at the round-1 reveal.
  - The relayed reworker report says "Every gold value is unchanged".
  - So the revision-2 per-task derivations are not blind as to values. They are recomputed from the revision-2 charter and views, and the comparison with GT is a check, not blind evidence.

### Status of each revision-1 RED

| id | status | evidence |
| --- | --- | --- |
| CG-1 | CLOSED | All four read sites now state the rule the compute implements: "a transfer notice counts from the earlier of its latest delivery to the resident and its latest delivery to the representative, a notice delivered again to the same person replacing the earlier delivery to that person". Probe: a second delivery to the representative dated 2026-09-12 now gives 7050.90 under both the rule and the compute. Realism note in O-6. |
| CG-2 | OPEN, members changed | See R2-1. The revision-1 members open_month and hold_signed_at are closed: open_month was removed, and hold_signed_at now rests on the rule's assertion "a reservation carries one" hold election. New reads fail the decoy probes. |
| CG-3 | OPEN, unchanged | Members: late_renewal_gap (closing_private_days) and skilled_renewal_gap (skilled_hold_days). Neither overwrite names bedhold_hold_end. The reworker reports it as not closed. |
| CG-4 (a) | CLOSED | closing_private_days now overwrites bedhold_evt_day_counting's booking sentence. Its replaced_by excludes both closing months by name, and the skilled sibling's replaced_by names the Medicaid closing month (XF 17 PASS). |
| CG-4 (b) | OPEN | See R2-2. |
| CG-5 | OPEN, unchanged | late_renewal_gap and skilled_renewal_gap. Same proof as revision 1. The skilled period is now anchored on the reservation's recorded first private day, which is never before the departure date, so the argument carries over. |
| CG-6 | CLOSED | Pairwise shapes for notice_schedule_opening, notice_schedule_closing and notice_schedule_skilled: tier 1 is a split at a later-of pick on the notice date (adds an input and a max); tier 2 has no split and uses one rate; tier 3 is a split at the fixed schedule date. Every pair differs in input or operation. The baseline is now the honest standard (split at the schedule date). |
| CG-7 | CLOSED | The opening entry is now the entry beginning on the first privately held day. A 31-day entry beginning on the 1st of a 31-day month is producible with a timely renewal, so the long-hold tier is reachable. |
| CG-8 | OPEN, unchanged | interrupted_stay_courtesy. Demonstrated again in 1.md. |
| CG-9 | OPEN, unchanged | Members: ma_reserve_allowance, last_held_day_rule, skilled_last_held_rule, unnoticed_opening_days, written_hold_start. |
| CG-10 | OPEN, aggravated | See R2-3. |
| CG-11 | OPEN, residual | See R2-4. "then" and "later" are gone; a residual ordering word remains. |
| CG-12 | CLOSED | All three sign tools round through `_BedholdFormat.half_up_cents`. It matched Decimal ROUND_HALF_UP on all 285,715 tested values from 0.000 to 1999.993, including 0.125 → 0.13, 1.005 → 1.01 and 2.675 → 2.68. Amounts ≤ 0 are refused. Both booking tools refuse malformed dates and months and negative or fractional day counts. The helper is a class static method (XF 23 PASS). Observation O-10. |
| CG-13 | CLOSED | All three charge replaced_by texts again carry "whatever payer source covers the resident's stay otherwise". |
| CG-14 | CLOSED | The rule now says "logged", which matches created_at ("moment the election was logged"), and the read is hold_logged_at. |

### New and remaining findings (revision_2)

**R2-1 — SOURCE-POLICY RED (CG-2 class, XF 11/12: decoy and tie probes on the changed selections).** All members:

- **opening_extension_charge**
  - Bindings: open_entry, open_days, open_to, open_run_days (selected by `from_date = private_hold_start_date`). open_days sums every booked resident-private row with that first day but subtracts only the reversals of the single LATEST one.
  - Rule: "the resident-private entry whose first day is the reservation's first privately held day, its days counted net of any of them reversed". It assumes one such entry and states no tie rule.
  - Probe (task 0's world, scratch copy): entry 737f39ea… booked 09-09..09-29 (21 days), reversed in full (billing_error), then rebooked 09-09..09-30 (22 days). This is base's correction route: "booked in error is reversed against its booked entry". Result: open_entry is the rebook, open_days = 43, open_run_days = 43, and the charge is 13970.55. The rebooked entry alone gives 22 days, i.e. 7793.10. No reading of the rule gives 43.
- **closing_extension_charge**
  - Bindings: close_entry, close_days, close_from, close_to ("the resident-private entry posted latest").
  - Same-day postings tie, and LATEST keeps the first inserted row. No tie rule is stated.
  - Probe: October entry booked on 10-21, reversed in full, then rebooked on 10-21 (16 days). The compute reads the reversed entry: close_days = 0 and the charge is 0.00. The corrected entry gives 5367.65.
- **skilled_hold_charge**
  - Bindings: skc_entry, skc_days, skc_from, skc_to. Same selector and same tie as closing_extension_charge, so the same probe shape applies.
- No scored world contains such rows, so no scored value moves.

**R2-2 — SOURCE-POLICY RED (CG-4 b, now a rule/compute break).** closing_private_days' rule says "A later written private election holds the bed only from its own effective date". compute_basis binds the sentence only to `renewal_effective` (the latest private_extension), and `leave_private_days` always counts from the end of the reserve.

Example world: a Medicaid hospital hold, departure on day 0, a 15-day reserve, a single private_extension effective on day 20 (late), and a return on day 26 (last held day 25):

| reading | privately held days | count |
| --- | --- | --- |
| "later" read as "late" (the rule) | days 20..25 | 6 |
| compute | from day 15: 25 − 15 + 1 | 11 |

If "later" is read as "subsequent", the policy instead departs without an overwrite from base bedhold_election "a later election holds it only from the day of election". Its only overwrite targets bedhold_evt_day_counting. Either reading is RED. The task-0 world has a timely first election, so its value does not move.

**R2-3 — SOURCE-FACTOR RED (CG-10 aggravated: the rule now reads the stamp).** Rule sentences now select by bedhold_reservations.private_hold_start_date ("first day held at the resident's expense"):
- opening_extension_charge: "the resident-private entry whose first day is the reservation's first privately held day";
- skilled_hold_days: "The hold's first private period runs … from the reservation's recorded first privately held day".

This is the very outcome that ma_reserve_allowance (departure + reserve) and written_hold_start (the logged day) claim to derive, so a reader takes both outcomes straight off the record. end_date still records the outcome of last_held_day_rule and skilled_last_held_rule. Members:

| factor | stamp field |
| --- | --- |
| ma_reserve_allowance | private_hold_start_date |
| written_hold_start | private_hold_start_date |
| last_held_day_rule | end_date |
| skilled_last_held_rule | end_date |

**R2-4 — RED (check 3 / XF 19; residual of CG-11).** The Returns sections of both booking tools still carry the ordering word "after": "held_days is the reservation's held-day total after the booking".
- book_closing_private_days_bb96678f (task_tools.py line 45)
- book_skilled_hold_days_804a4481 (task_tools.py line 143)

The rework replaced the same word in the three sign tools ("including the charge"). The phrase was already present in revision 1 and was missed there.

**R2-5 — SOURCE-FACTOR RED (XF 29 seed producibility; task 0 persists in a new form, task 1 regressed).**
- Charter limits: in products/private.yaml, `isolation_placement` is set only by the event private_room_change ("The resident moves to a room of another tier"; fields variant_name, last_room_change_date, isolation_placement "true when the center directed the move for infection control"). private_tier_placement says "Only an open, active agreement changes tier". private_agreement_open does not set isolation_placement.
- Seeded rows that violate this. Both now show isolation_placement true with no last_room_change_date:

  | task | agreement | dates |
  | --- | --- | --- |
  | task 0 | 889f897b… | admitted and converted 2026-01-05 |
  | task 1 | 553dc736… | signed 2026-06-20, admitted and converted 2026-08-29 |

  The charter can produce neither state.
- Cost: the isolation tier of all three charge computations rests on these rows (isolation_rate_opening, isolation_rate_closing, isolation_rate_skilled).
- In revision 1, task 1's row was producible (room change 2026-06-02 while active), so task 1 has regressed.

**Unchanged REDs, status above:** CG-3, CG-5, CG-8, CG-9.

### factor_ladders (revision_2)
- Declared factor counts and labels are unchanged: 4, 6, 5, 5 and 6 factors; 1, 1, 1, 2 and 1 method.
- Changed ladders:
  - The notice_schedule factors now carry the condition "agreement signed before the schedule date". The added input is agreement_signed_date. Structure PASS (CG-6 closed).
  - extended_hold_opening now reaches 3 producible tiers (CG-7 closed).
- No factor binding reads another factor's binding (scripted). Every compute_basis quote is verbatim in its rule. Every baseline sentence is in its rule. Every prerequisite policy_source is verbatim in its rule. Every replaced_by is restated in its rule. No factor id is a substring of a tool name. All of these were checked by script.
- Surviving factors after the strikes (structure, per policy):

  | policy | struck factors | surviving | surviving methods |
  | --- | --- | --- | --- |
  | closing_private_days | ma_reserve_allowance, last_held_day_rule (CG-9, R2-3); late_renewal_gap (CG-5) | written_cover_cap | 0 |
  | opening_extension_charge | unnoticed_opening_days (CG-9); isolation_rate_opening contested (R2-5) | 4 | notice_schedule_opening |
  | closing_extension_charge | isolation_rate_closing contested (R2-5) | 4 | 1 |
  | skilled_hold_days | written_hold_start (CG-9, R2-3); skilled_last_held_rule (CG-9, R2-3); skilled_renewal_gap (CG-5); interrupted_stay_courtesy (CG-8) | skilled_cover_cap | 0 |
  | skilled_hold_charge | isolation_rate_skilled contested (R2-5) | 5 | 1 |

  Both booking computations stay below the floor of 4 factors with 1 method.
- The only multi-source factors are isolation_rate_* (agreement + reservation), ma_reserve_allowance, unnoticed_opening_days, written_hold_start and the gap and courtesy factors. Every one is struck or contested, so neither task has an uncontested multi-source factor. The notice_schedule tiers are single-record (agreement plus charter parameter).

### Observations (revision_2)
- O-1 and O-2 (realism of scoped pricing and of the credit stack) are unchanged. The reworker's request to the coordinator about adding real operator schedule items concerns these and the struck factors. Choosing among the options belongs to the coordinator; this audit does not rule on it.
- O-6: treating a re-delivered transfer notice as replacing the earlier delivery to the same person is unusual. It favours the resident and conflicts with no in-force base clause ("No day held before the transfer notice was delivered is ever charged" fixes a floor only).
- O-7: skilled_hold_days' replaced_by now names two closing months ("Outside the closing month of a Medicare Skilled Stay … and the closing month of a Medicaid Hospital Leave Reserved Bed hold … for that closing month, … less the hold's courtesy days"). The referent of "that" is ambiguous, but the policy's own scope sentence confines courtesy days to the skilled tier, and no scored value can move.
- O-8: closing_extension_charge's prerequisite `effect` still says close_* read "the latest by last day", while the selector is now "posted latest". Both pick the October entry on task 0's world.
- O-9: task 1's private-pay agreement was signed 2026-06-20, 67 days before an admission that follows a qualifying hospital stay beginning 2026-08-26. That is plausible only for an elective, pre-arranged post-surgical stay. It is the fact that puts the task on notice tier 1 ("signed before the schedule date").
- O-10: `_BedholdFormat.is_date` accepts calendar-impossible days such as 2026-02-30. The format is enforced, the calendar is not.
- Docstring scope: book_closing_private_days still describes "a hospital-leave bed-hold reservation", while its policy now covers only the Medicaid Hospital Leave tier. Policy-to-tool binding is unaffected.

### post_reveal_note (revision_2)
- Both tasks were revealed at 2026-10-22 10:04:11 UTC, after every revision-2 section above had been written. Nothing above this note was edited after the reveal.
- Every scored argument and every computations figure matches the recomputation in both tasks.
- The scopes are disjoint and jointly complete, as in revision 1.
- Closed since revision 1:
  - CG-1, CG-4(a), CG-6, CG-7, CG-12, CG-13, CG-14;
  - the "then" / "later" members of CG-11;
  - task 1's revision-1 SOURCE-TASK finding;
  - the XF 29 ledger-completeness items in both tasks.
- Still open:
  - CG-2, now R2-1 with new members;
  - CG-3, CG-4(b) (now R2-2), CG-5, CG-8 and CG-9;
  - CG-10, now aggravated as R2-3.
- New this revision:
  - R2-4: a residual "after" in the docstrings, missed in revision 1;
  - R2-5: an isolation placement with no room change on both seeded private agreements; for task 1 this is a regression.

## closing_checklist (revision_2)
Not closed: the four relationships do not PASS. This revision cites the coordinator-run gate block above; it does not re-run the gates.

VERDICT revision_2: task0=RED SOURCE-POLICY(CG-3 base-expiry second value 8/2968.80),SOURCE-FACTOR(R2-3 stamps private_hold_start_date->ma_reserve_allowance & end_date->last_held_day_rule,CG-9 straw-man baselines ma_reserve_allowance/last_held_day_rule/unnoticed_opening_days,CG-5 late_renewal_gap,closing_private_days 1 factor 0 method,no uncontested multi-source,R2-5 isolation_placement without room change on 889f897b feeding isolation_rate_opening/isolation_rate_closing) task1=RED SOURCE-POLICY(CG-3 base-expiry second value 23/7716.50),SOURCE-FACTOR(CG-8 interrupted_stay_courtesy,R2-3 stamps private_hold_start_date->written_hold_start & end_date->skilled_last_held_rule,CG-9 written_hold_start/skilled_last_held_rule,CG-5 skilled_renewal_gap,skilled_hold_days 1 factor 0 method,no uncontested multi-source,R2-5 regression isolation_placement without room change on 553dc736 feeding isolation_rate_skilled) charter=R2-1(open_entry/open_days/open_to/open_run_days; close_entry/close_days/close_from/close_to; skc_entry/skc_days/skc_from/skc_to),R2-2(closing_private_days late first election rule vs compute),CG-3(late_renewal_gap,skilled_renewal_gap),CG-5(late_renewal_gap,skilled_renewal_gap),CG-8(interrupted_stay_courtesy),CG-9(ma_reserve_allowance,last_held_day_rule,skilled_last_held_rule,unnoticed_opening_days,written_hold_start),R2-3(ma_reserve_allowance,written_hold_start,last_held_day_rule,skilled_last_held_rule),R2-4(book_closing_private_days_bb96678f,book_skilled_hold_days_804a4481 "after the booking"),R2-5(889f897b,553dc736)

## revision_3

### charter_global_frozen (revision_3)
- Re-derived in full, because both source hashes changed. Written on 2026-10-22 before tasks/*.json for revision 3 were opened. Auditor: the same independent policy auditor.
- Gate snapshot: `/tmp/erl0074_coord/snapshot.sh bed_hold_and_leave_reservations 3`, run by this auditor, reported "snapshot … round 3 at 2026-10-22T10:25:55". All 7 gates passed (rc=0), so the input is complete:

  | gate | result |
  | --- | --- |
  | check_extended | EXTENDED OK |
  | check_task_tools | TASK TOOL CONTRACT OK |
  | replay_tasks --check | REPLAY OK |
  | check_solvability | SOLVABILITY OK |
  | check_compute | COMPUTE OK |
  | check_grounding | GROUNDING OK |
  | check_cross_fire | SCOPE OK |

- Source and view hashes (sha256):

  | file | sha256 |
  | --- | --- |
  | task_tools.py | c523caee0693943808e7fdad0528dd53afbc596af5fd9ddb4ac4dfaf69ca6ae0 |
  | bedhold.extended.yaml | 27cbde936d6a3adafd071c72c3b6b6eb46fbdbd29770a1166c04a33465c90955 |
  | task0.view.json | af27785ed37bd18fe4e9a13dfdf2f780d99f7ed230941102e8d94205e1672067 |
  | task1.view.json | 669215510a62582c4318fcffeadaccd9308edee13fd68e6d42412e8a2fba2cf3 |

- The base copy is still identical to blueprint/products/bedhold.yaml.
- contamination_disclosure (applies to both task files):
  - I read the "REWORK round 3" section of tasks/bed_hold_and_leave_reservations/worklog.md before this freeze, as the coordinator permitted.
  - That section states gold for task 0 (A 7736.40, B 3501.00, C 6306.05), the task-0 skip-A value 7099.35, and per-factor baseline-alone figures for both tasks.
  - The revision-3 per-task derivations below are therefore recomputations from the charter and the rebuilt views, not blind evidence.
- Design change in this revision: both booking policies and their tools are deleted. Every problem now prices a booked resident-private entry.

  | policy | tool (owner) | factors |
  | --- | --- | --- |
  | bedhold_ext_opening_extension_charge | post_opening_extension_charge_4f0e6c96 (agent) | 6 |
  | bedhold_ext_therapeutic_extension_charge | sign_therapeutic_extension_charge_a4dde64b (user) | 4 |
  | bedhold_ext_closing_extension_charge | sign_closing_extension_charge_a05fa8e4 (user) | 5 |
  | bedhold_ext_skilled_opening_charge | post_skilled_opening_charge_38373dc8 (agent) | 6 |
  | bedhold_ext_skilled_hold_charge | sign_skilled_hold_charge_7094169f (user) | 5 |

  Prerequisite edges:
  - closing → opening: value_input on ce_charged_before.
  - closing → therapeutic: state_gate.
  - skilled closing → skilled opening: value_input on sc_charged_before.

### scripted sweeps (revision_3)
- Every compute_basis quote is verbatim in its own rule.
- Every baseline sentence is in its rule.
- Every prerequisite policy_source is verbatim in the blocked rule.
- Every replaced_by is restated in its rule.
- No factor binding reads another factor's binding.
- No factor id is a substring of a tool name.
- The tool uuid8s 4f0e6c96, a4dde64b, a05fa8e4, 38373dc8 and 7094169f are distinct and show no common pattern.
- No docstring carries before / after / first / last / then / later / once / until / prior / next (grep).
- Every write tool creates and updates rows in its own body and refuses amounts ≤ 0; half-up rounding comes from the static helper.
- No datetime / time / random / uuid / secrets substring appears.
- Events written: bedhold_charge only, with no trigger (XF 25 PASS).

### Status of each revision-2 RED
| id | status | evidence |
| --- | --- | --- |
| R2-1 (CG-2 class) | CLOSED | Entries are now selected by from_date (opening) or to_date (closing) and summed net of reversals that name the entry. Base grain "bedhold_day_booked … grain: one row per reservation, service month and day payer" makes a second booked resident-private row for the same month non-producible, and the rule now states this grain. A partial-reversal probe nets correctly. |
| R2-2 (CG-4 b) | CLOSED | The booking policy is deleted. |
| CG-3 | CLOSED | The gap factors are deleted. Both worlds' renewals were logged before the first private period ended: task 0's was logged 10-05 against a period ending 10-08, task 1's 10-06 against a period ending 10-09. |
| CG-5 | CLOSED | The gap factors are deleted. |
| CG-8 | CLOSED | The courtesy factor is deleted. |
| CG-9 | PARTLY CLOSED | ma_reserve_allowance, last_held_day_rule, skilled_last_held_rule and written_hold_start are deleted. unnoticed_opening_days survives as oe_notice_days / so_notice_days (see R3-1). |
| R2-3 (CG-10) | CLOSED | No surviving factor decides a recorded quantity. private_hold_start_date is now only an entry selector, and end_date is not read. |
| R2-4 (CG-11) | CLOSED | The grep finds no ordering word. |
| R2-5 | CLOSED | The isolation factors are removed. Both agreements now carry isolation_placement false and no room change. |

### New findings (revision_3)

**R3-1 — SOURCE-POLICY RED (XF 16) and SOURCE-FACTOR RED (straw-man baseline, carrying CG-9 forward; XF 27).**

Members:
- the shared overwrite of `bedhold_evt_notice` in bedhold_ext_opening_extension_charge and bedhold_ext_skilled_opening_charge;
- the factors oe_notice_days and so_notice_days.

What the overwrite does:
- It retires the base sentence "No day held before the transfer notice was delivered is ever charged to the resident" for the two opening entries ("the days of those two entries held before the notice are set by their own schedules").
- Each schedule's own rule then restates the same treatment: "No day of the opening extension entry held before the transfer notice was delivered is charged: …", and the same for the skilled opening entry.
- The merged semantics therefore never differ from the retired clause, so the overwrite retires a clause that does not conflict (XF 16).

Its only effect is to let the baseline ("The opening extension entry's charged days are its days") charge the days held before the notice. No operator bound by the notice rule would publish that treatment; XF 27 lists bed-hold notice rules as real rules.

The three sibling schedules (therapeutic, closing, skilled closing) keep the same exclusion inside their baselines. That shows the exclusion is part of the standard method, and the opening factors are that standard rule relabelled as a factor.

**R3-2 — SOURCE-FACTOR RED (unreal ladder: credits keyed to the private-pay agreement's tier, not to the bed held).**

Members (all 10):
oe_program_credit, oe_housekeeping_credit, te_program_credit, te_housekeeping_credit, ce_program_credit, ce_housekeeping_credit, so_program_credit, so_housekeeping_credit, sc_program_credit, sc_housekeeping_credit.

The mismatch between rule rationale and key:
- The rules justify the credits by the empty bed: "Housekeeping and linen service stop for a bed left empty" and "whose program supplies stop while the resident is away".
- But the tier is read from "the tier on the resident's private-pay agreement", with fall-through "any other agreement, or none, takes no credit".
- Every private tier has 1 or 2 beds per room, so the fall-through is reached only when no current agreement exists.

Two demonstrations:
- **No agreement.** A Medicaid resident admitted directly on Medical Assistance, with no private-pay agreement, holds a one-bed Private Long-Term Care Room. The bed is equally empty, yet the resident gets no housekeeping credit. An identical resident with a payer-converted agreement gets 5.40 per day.
- **Stale agreement tier.** products/private.yaml says "Only an open, active agreement changes tier". So a payer_converted agreement keeps the tier it had at conversion even after the resident moves rooms. Example: a Semi-Private Secure Memory agreement converted at admission, with the resident later holding a Private Long-Term Care Room. That resident gets the memory-care credit (6.20) and the shared-room credit (2.70) for a non-memory one-bed room. The bed actually held is recorded on the reservation (room_tier_held) and is never read.

No operator publishes empty-bed credits keyed to paperwork rather than to the bed.

**R3-3 — SOURCE-FACTOR RED (no multi-source factor in either task).**

The skill's test: every tier beyond the fall-through must be "a conjunction or a disjunction of two or more conditions over distinct records".

Each candidate fails it:
- **Rate binding** (oe, te, ce, so, sc). Its compound tiers ("signed before the schedule date and its rate notice was delivered fewer than the rate-change notice days before …") test two fields of one record, the private agreement row, against charter constants.
- **Program-credit compute.** Its `and` tests two tier parameters of the same agreement tier.
- **Single-condition factors.** Notice days, extended hold, meal and housekeeping each have a single condition per tier.

The multi-source factors of earlier revisions (isolation tier: agreement + reservation; MA reserve: case + departure) are all removed. check_compute's gate counts distinct binding names, so it passes these. The skill's test counts records and fails them.

Bears on: task 0 and task 1.

**R3-4 — SOURCE-FACTOR RED (XF 29: the worlds assert payer holdings that are not seeded).**

- **Task 0.** The view holds no `medicaid_cases` row at all. Yet both reservations are on Medicaid tiers (entry_gate payer_class medicaid). 30 + 15 payer_reserved days are booked as Medical Assistance-paid. The private agreement aa7d4c0f… is `converted_to: medicaid` from admission.
- **Task 1.** The view holds no `medicare_coverages` or `medicare_ledger` row. Yet both reservations are on the Medicare Skilled Stay tier (payer_class medicare_part_a). Agreement 3d6d9ae3… is `converted_to: medicare_part_a`, and the persona says the resident "came … for rehabilitation". This is a regression: revision 2's world seeded the Part A episode and ledger.
- **Consequence.** find_medicaid_cases / find_medicare_coverages return "No … records" for a resident whose bed-hold tier and payer days assert that payer. That state is not producible: the private charter converts an agreement only "on the first day another payer source covers", and base pays reserved days only for an eligible payer.

**Factor counts after strikes** (struck: R3-1, R3-2):

| policy | surviving factors | count | method |
| --- | --- | --- | --- |
| opening | rate_binding, extended_hold, meal | 3 | 1 |
| therapeutic | rate_binding, meal | 2 | 1 |
| closing | rate_binding, extended_hold, meal | 3 | 1 |
| skilled opening | rate_binding, extended_hold, meal | 3 | 1 |
| skilled closing | rate_binding, extended_hold, meal | 3 | 1 |

- Every policy falls below the floor of 4 factors.
- No multi-source factor remains (R3-3).
- Every surviving factor passes T1 and T2: T1 is shown in the task files; T2 holds because each enters the result additively or multiplicatively with the other factors at baseline.
- Every rate_binding pairwise shape test passes, as in revision 2.

### Observations (revision_3)
- O-1 (persists): entries outside the five scopes, e.g. the middle month of a three-month hold, are priced under base with no credits and no percentage. The same hold is priced by two different methods.
- O-11: for the two opening entries, the "already charged" part of the extended-hold count is always 0. The opening entry is the reservation's first private entry, so no earlier charge exists on it, and the tier rests on the entry's own days.
- O-11 (cont.): the closing count uses "the days recorded on the bed-hold charges", which are the gross entry days the tools copy, including days held before the notice. The rule defines the count this way, and no tier moves on either world.
- O-12: the closing charge's gate on "every earlier therapeutic leave of the resident" blocks a hospital-leave charge on the customer signing an unrelated leave's charge.
- O-12 (cont.): a therapeutic leave with two or more private months has no tool for its non-closing entry, so the gate could not resolve inside the difficulty. Neither world has such a leave.
- O-9 persists: task 1's agreement was signed 2026-06-20 for an admission on 2026-08-29.
- O-6 persists: a re-delivered notice replaces the earlier delivery.

### post_reveal_note (revision_3)
- Revealed at 2026-10-22 10:32:17 UTC, after all revision-3 sections were on disk. Nothing above was edited after the reveal.
- Every scored argument and every computations figure matches in both tasks.
- The scopes are disjoint and jointly complete over the five policies.
- Closed since revision 2: R2-1, R2-2, R2-3, R2-4, R2-5, CG-3, CG-5 and CG-8.
- CG-9 is partly closed: four of its five members are deleted, and the fifth persists as R3-1.
- New in this revision: R3-1, R3-2, R3-3 and R3-4. R3-4 is a regression for task 1, whose Medicare rows are no longer seeded.

## closing_checklist (revision_3)
Not closed: the four relationships do not PASS. This revision cites the coordinator-run gate block above.

VERDICT revision_3: task0=RED SOURCE-POLICY(R3-1 XF16 non-conflicting retirement of bedhold_evt_notice),SOURCE-FACTOR(R3-1 oe_notice_days straw-man baseline,R3-2 oe_program_credit/oe_housekeeping_credit/te_program_credit/te_housekeeping_credit/ce_program_credit/ce_housekeeping_credit keyed to agreement tier not held bed,R3-3 no multi-source factor,surviving factors A=3 B=2 C=3 below floor 4,R3-4 no medicaid_cases row behind Medicaid tiers/MA-paid days/converted_to medicaid) task1=RED SOURCE-POLICY(R3-1 XF16),SOURCE-FACTOR(R3-1 so_notice_days straw-man baseline,R3-2 so_program_credit/so_housekeeping_credit/sc_program_credit/sc_housekeeping_credit,R3-3 no multi-source factor,surviving factors D=3 E=3 below floor 4,R3-4 regression no medicare_coverages/medicare_ledger behind Medicare Skilled Stay tier/converted_to medicare_part_a) charter=R3-1(bedhold_evt_notice overwrite shared by bedhold_ext_opening_extension_charge & bedhold_ext_skilled_opening_charge; oe_notice_days,so_notice_days),R3-2(oe_program_credit,oe_housekeeping_credit,te_program_credit,te_housekeeping_credit,ce_program_credit,ce_housekeeping_credit,so_program_credit,so_housekeeping_credit,sc_program_credit,sc_housekeeping_credit),R3-3(no factor of any of the five policies is multi-source over distinct records; rate_binding oe/te/ce/so/sc tiers read only the agreement row),R3-4(task0 medicaid holding absent; task1 medicare holding absent),factor-floor(all five policies below 4 surviving factors)

## revision_4

### charter_global_frozen (revision_4)
- **Re-derived in full** because both source hashes changed. Written 2026-10-22 before tasks/*.json for revision 4 were opened.
- **Gate snapshot** (`/tmp/erl0074_coord/snapshot.sh bed_hold_and_leave_reservations 4`, run by this auditor): "snapshot … round 4 at 2026-10-22T16:05:12". All gates rc=0, so the input is complete:

  | gate | result |
  | --- | --- |
  | check_extended | EXTENDED OK |
  | check_task_tools | TASK TOOL CONTRACT OK |
  | replay_tasks --check | REPLAY OK |
  | check_solvability | SOLVABILITY OK |
  | check_compute | COMPUTE OK |
  | check_grounding | GROUNDING OK |
  | check_cross_fire | SCOPE OK |

- **Hashes** (sha256):

  | file | sha256 |
  | --- | --- |
  | task_tools.py | e5f757531c5fc159b107f8d86582d8b8ea7ea6cb7125be45e8c9cbeaeee4fcc6 |
  | bedhold.extended.yaml | 5cf16109d33d8ef89f348619b602988995bc24e56c1e74b4af66825e9c1937f7 |
  | task0.view.json | f304943d6121b38854d2cd6e6cb7d86838563a9056a74b7351b978a06fdb7bba |
  | task1.view.json | 3999f9b5f08333f8bfaeb4ab35ed1a1ed5c394b103536c17b996bb5b6b6acb9c |

- **Base copy:** still identical to the blueprint.
- **contamination_disclosure:** I read both "REWORK round 4" sections of worklog.md before this freeze, as the coordinator permitted. They state the gold of all five computations (10191.70, 6663.30, 7859.80, 7715.10, 10696.00) and the T1/T2 tables. The per-task derivations are recomputations.
- **Coordinator decision used as the yardstick.** Allowed levers:
  1. rate-notice binding (method);
  2. a per-held-day dietary credit keyed to the held bed;
  3. a long-hold threshold counted on days already charged on earlier entries;
  4. isolation / infection-control repricing;
  5. a recorded resident-requested room move repriced from its effective date;
  6. the held room's tier when the reservation records a different tier by a recorded room change.

  Also: plain standard baselines; program and housekeeping credits struck; drawn factor counts stand.
- **Design.** Five private-pay schedules:

  | id | policy | tool | owner | factors |
  | --- | --- | --- | --- | --- |
  | A | therapeutic opening | post_therapeutic_opening_charge_70c1859c | agent | 6 |
  | B | hospital stay (single entry) | sign_hospital_stay_charge_706e62e1 | user | 4 |
  | C | therapeutic closing | sign_therapeutic_closing_charge_4fa24c1a | user | 5 |
  | D | hospital opening | post_hospital_opening_charge_f00b38a9 | agent | 6 |
  | E | hospital closing | sign_hospital_closing_charge_2a6f345f | user | 5 |

  Edges: C←A value_input (tc_charged_before); C←B state_gate; E←D value_input (hc_charged_before).

### scripted sweeps (revision_4)
All of the following pass:
- compute_basis quotes are verbatim in their own rules.
- Baseline sentences appear in the rules.
- Every prerequisite policy_source is verbatim in its rule.
- Every replaced_by is restated in its rule. The shared scope sentence is identical across all five overwrites and names all five scopes (XF 15/17).
- No factor reads another factor's binding.
- No factor id is a substring of a tool name.
- No ordering word appears in any docstring.
- No datetime / time / random / uuid / secrets substring appears.
- Every body creates and updates rows itself, refuses amounts ≤ 0, and rounds half up via the static helper.

Observation: the uuid8s 70c1859c and 706e62e1 share the prefix "70". That is consistent with chance; no batch derivation is evident.

### Status of each revision-3 RED
| id | status | evidence |
| --- | --- | --- |
| R3-1 | CLOSED | No bedhold_evt_notice overwrite remains. The notice exclusion is a baseline sentence in all five schedules. No notice factor remains. |
| R3-2 | CLOSED | Program and housekeeping credits are deleted. The only per-day credit is the dietary credit keyed to the reservation's room_tier_held. |
| R3-3 | CLOSED | Multi-source factors now exist over distinct records: isolation rate (credited private room-and-board charge × reservation room) in A, B and D; dietary credit (reservation room × entry span) in all five; room-change tier (request × agreement) in A, C, D and E. |
| R3-4 | CLOSED | No Medicaid or Medicare status is asserted. Each private ledger is seeded from admission, and account_balance equals the ledger sum in both worlds (T0 21588.00 = 6168 + 15420; T1 15890.00 = 466 + 964 + 14460). A residual completeness item is listed under R4-5. |

### New findings (revision_4)

**R4-1 — SOURCE-POLICY RED (undeclared conflict with base bedhold_hold_end and with the blueprint's out-of-scope list; realism).**

The rules of A, C, D and E state: "A room change the private-pay agreement records during the leave reprices the held bed from its effective date …". Days after the change are then priced at the agreement's new tier.

This conflicts with two in-force texts, neither overwritten:
- Base bedhold_hold_end: "A resident who returns while the hold is in force goes back to the same room, which is never assigned to anyone else during the hold."
- The blueprint difficulty summary: "requests to hold a different room than the one the resident left … are not decided by any published rule, and the only correct route for them is a POLICY_NOT_COVERED handoff."

The build also departs from the coordinator's lever (6) ("when the reservation records a different tier by a recorded room change"). Both reservations still record the room that was left (room_tier_held Private Long-Term Care Room, room 431 / 437). The tier moved to is read from the private-pay agreement.

The seeded worlds are states that base hold_end cannot produce:

| | task 0 | task 1 |
| --- | --- | --- |
| resident's status during the change | on a therapeutic leave at home | in hospital |
| request created | 09-18 | 09-17 |
| move effective | 09-21 | 09-22 |
| room held | 431 | 437 |
| returned to | room 468 (customers.room_number) | room 459 |

Members:
- rule sentences of bedhold_ext_therapeutic_opening_charge, bedhold_ext_therapeutic_closing_charge, bedhold_ext_hospital_opening_charge and bedhold_ext_hospital_closing_charge;
- factors to_room_change_days, to_room_change_tier, tc_room_change_days, tc_room_change_tier, ho_room_change_days, ho_room_change_tier, hc_room_change_days, hc_room_change_tier;
- seed rows: T0 agreement last_room_change_date 2026-09-21, request 838e90b9…, customers.room_number 468; T1 agreement last_room_change_date 2026-09-22, request af39d1b8…, customers.room_number 459.

Second values (base reading, held room's own pricing with no move): A 9118.20, C 6620.50, D 7014.00, E 9625.00. These are demonstrated in the task files.

**R4-2 — SOURCE-FACTOR RED (XF A6 T2 and XF A1/A5: the room-change factors bear weight only jointly).**

Members: to_room_change_days, to_room_change_tier, tc_room_change_days, tc_room_change_tier, ho_room_change_days, ho_room_change_tier, hc_room_change_days, hc_room_change_tier.

Test: each factor live with every other factor at baseline, on its own task world.

| factor (alone) | result | all-baseline |
| --- | --- | --- |
| to_* | 11336.00 | 11336.00 |
| tc_* | 8284.00 | 8284.00 |
| ho_* | 8720.00 | 8720.00 |
| hc_* | 12208.00 | 12208.00 |

None moves the result. This holds structurally on every world. With the tier at its baseline (the room held), moved days are priced like the other days. With the day count at its baseline (0), the tier is never applied. So the tier is gated through the day count (A5).

Every other factor of the five schedules moves the result alone (T2 table in the task files).

After the strike, the surviving factor counts are:
- A: 4 (to_rate_binding method, to_extended_hold, to_dietary_credit, to_isolation_rate)
- B: 4
- **C: 3 (tc_rate_binding, tc_extended_hold, tc_dietary_credit) — below the floor**
- D: 4
- **E: 3 — below the floor**

**R4-3 — SOURCE-POLICY RED (XF 12 decoy: two readings of the request test).**

The rule test is "the latest room change request on file naming the room change date as its requested date". The compute takes the latest room_change_request overall (`XLATEST(... 'requested_date', date_field='created_at', request_type='room_change_request')`) and then requires it to name the change date.

Decoy (task 0 scratch copy): a second room change request created 2026-10-25 for 2026-11-15.
- The rule's natural reading (the latest request that names 09-21 is still on file) leaves A at 10191.70.
- The compute falls to "any other change", giving the room held: A = 9469.70.

Members: to_req, tc_req, ho_req, hc_req.

**R4-4 — SOURCE-POLICY RED (check 6: prerequisite sentence broader than its condition).**

Sentence (rule of bedhold_ext_therapeutic_closing_charge): "The therapeutic closing charge is not posted until the resident-private entry of every earlier hospital leave of the resident carries its own bed-hold charge."

Declared condition: "… on the resident's ended Private Pay Hospital Leave Bed Hold reservations that carry a single resident-private entry …".

Counter-world: an earlier hospital leave with two private entries and an uncharged closing entry.
- Under the sentence, the gate is unmet.
- Under the condition, the gate is met.
- The resolving write would be sign_hospital_closing_charge_2a6f345f rather than sign_hospital_stay_charge_706e62e1, so the hop is not unique.

Neither scored world contains such a leave, so no scored value moves.

**R4-5 — RED (XF 29 seed producibility; not load-bearing).**

- **Private-extension renewal recorded as a second `hold` election.** Rows: T0 bedhold_elections f7265ca1… (effective 10-05, created 10-02) and T1 2fb07670… (effective 10-10, created 10-06).
  - Base records a renewal with bedhold_extension_elected ("renews a private hold", election_type private_extension).
  - bedhold_hold_elected exists only as the notice_pending → held transition.
- **No advance October room-and-board bill.** Neither private ledger has one (T0 should have issued 2026-09-25; T1 2026-09-25), nor the matching discharge_proration credit.
  - products/private.yaml private_evt_room_board_billing: "Room and board is billed per calendar month in advance … charged only while the agreement is active or notice_period".
  - Both agreements were active throughout.

No factor reads these rows.

### Observations (revision_4)
- **O-14 (realism, isolation scope).** The isolation lever exists only in the opening and single-entry schedules (A, B, D), not in the closing schedules (C, E). For a resident still under infection-control billing with no room change, one held bed is priced at the isolation billing tier in the opening month and at its own private tier in the closing month.
- **O-11 persists.** The opening schedules' "already charged" count is always 0.
- **O-1 persists.** Middle months of a hold lasting three months or more are priced under base.
- **O-15.** Task 1's requested move is into the Private Bariatric Care Room. private_tier_placement requires "a documented weight at or above the tier's bariatric weight threshold", and no record carries a weight, so producibility cannot be checked.
- **O-16.** The earlier single-entry hold charges (T0 3cbb91ad… 2026-04-25; T1 7373bd11… 2026-08-25) were posted on the 25th, not on statement day 3. Both amounts (384.00) equal the hospital-stay schedule recomputed.

### post_reveal_note (revision_4)
- The reveal ran at 2026-10-22 16:09:59 UTC, after every revision-4 section above was written. Nothing above was edited after it.
- All scored arguments and every computations figure match in both tasks.
- Scopes are disjoint and jointly complete.
- Closed: R3-1, R3-2, R3-3, R3-4.
- New: R4-1, R4-2, R4-3, R4-4, R4-5.
- What remains open is the room-change lever: its conflict with base hold_end and with the blueprint's out-of-scope list, its joint-only weight, and its request selector. Also open are one gate-sentence scope (R4-4) and seed-producibility residue (R4-5).
- Striking the room-change factors leaves C and E at 3 factors.

## closing_checklist (revision_4)
Not closed: the four relationships do not PASS. Gate block cited above.

VERDICT revision_4: task0=RED SOURCE-POLICY(R4-1 room change during leave reprices held bed vs base bedhold_hold_end same-room return & blueprint POLICY_NOT_COVERED, base reading A 9118.20/C 6620.50; R4-3 room-change request selector second reading),SOURCE-FACTOR(R4-2 to_room_change_days/to_room_change_tier/tc_room_change_days/tc_room_change_tier fail T2 alone, therapeutic closing 3 factors below floor),R4-5 seeds(second hold election f7265ca1 as renewal; no October advance room-and-board bill) task1=RED SOURCE-POLICY(R4-1 base reading D 7014.00/E 9625.00; R4-3),SOURCE-FACTOR(R4-2 ho_room_change_days/ho_room_change_tier/hc_room_change_days/hc_room_change_tier fail T2 alone, hospital closing 3 factors below floor),R4-5 seeds(second hold election 2fb07670 as renewal; no October advance room-and-board bill) charter=R4-1(rule sentences of bedhold_ext_therapeutic_opening_charge,bedhold_ext_therapeutic_closing_charge,bedhold_ext_hospital_opening_charge,bedhold_ext_hospital_closing_charge; factors to/tc/ho/hc_room_change_days and _tier; tier read from agreement not reservation),R4-2(to_room_change_days,to_room_change_tier,tc_room_change_days,tc_room_change_tier,ho_room_change_days,ho_room_change_tier,hc_room_change_days,hc_room_change_tier),R4-3(to_req,tc_req,ho_req,hc_req),R4-4(therapeutic closing state-gate sentence "every earlier hospital leave" broader than single-entry condition),R4-5(T0 f7265ca1,T1 2fb07670 renewal as hold election; T0/T1 missing 2026-10 advance room-and-board bill + credit)

## revision_5

### charter_global_frozen (revision_5)
- Re-derived in full; both source hashes changed. Written 2026-10-22, before tasks/*.json for revision 5 were opened.
- Gate snapshot (`/tmp/erl0074_coord/snapshot.sh bed_hold_and_leave_reservations 5`, run by this auditor): "snapshot … round 5 at 2026-10-22T17:35:44". All seven gates returned rc=0, so the input is complete:

  | gate | result |
  | --- | --- |
  | check_extended | EXTENDED OK |
  | check_task_tools | TASK TOOL CONTRACT OK |
  | replay_tasks --check | REPLAY OK |
  | check_solvability | SOLVABILITY OK |
  | check_compute | COMPUTE OK |
  | check_grounding | GROUNDING OK |
  | check_cross_fire | SCOPE OK |

- Hashes:

  | file | sha256 |
  | --- | --- |
  | task_tools.py | 229d8542b0ef40eb9c279b4edfec349a18d66b9623d02e90802ca4415acda37e |
  | bedhold.extended.yaml | 4718b6c866677237fc36ce57160576a6e95f721b571fa950bc0dbe4c2dfcdbda |
  | task0.view.json | 3c83586bc723d32d8ddb2c2d888e63b4cba6d1072138ed17095d35bb6a67de54 |
  | task1.view.json | 3cc05143d0144d5c46946068c43e3a174474302fa4537f13d6b6782446bf247c |

- Base copy: identical to the blueprint.
- contamination_disclosure: before this freeze I read the "REWORK round 5" section of worklog.md, which the coordinator permits. Its T1 table headings state all five gold values: 9118.20, 6663.30, 4720.20, 7715.40, 4059.90.
- Yardstick: the coordinator's round-5 route.
  - Levers: rate binding; dietary credit keyed to the held bed; isolation from the agreement's placement before the leave; a long-hold threshold on days already charged; MA reserved days; census day counting; release-effective timing.
  - The room-change levers are dropped.
  - Rounding is RND(x + 1e-9, 2). The residue is DSL-KNOWN and not a RED.
- Design. Each of the five schedules overwrites `bedhold_evt_charges`, using one shared scope sentence.

  | label | schedule | factors | tool | owner | task |
  | --- | --- | --- | --- | --- | --- |
  | A | therapeutic opening | 4 | post_therapeutic_opening_charge_78fe9a0a | agent | 0 |
  | B | private-pay single-entry hospital stay | 6 | sign_hospital_stay_charge_56dfc7d9 | user | 0 |
  | C | therapeutic closing | 5 | sign_therapeutic_closing_charge_194aeb06 | user | 0 |
  | D | Medicaid hospital opening | 5 | post_hospital_opening_charge_991dca72 | agent | 1 |
  | E | Medicaid hospital closing | 6 | sign_hospital_closing_charge_702d4c7f | user | 1 |

  Edges: C←A value_input; C←B state_gate; E←D value_input.
  The tools now take the charged day count and record it on the charge row. That row is what the downstream "days already charged" read sums.

### scripted sweeps and checks (revision_5)
- The structural sweeps pass:
  - every compute_basis quote is verbatim in its rule;
  - baseline and prerequisite sentences are in their rules;
  - replaced_by is restated in each rule, and the five replaced_by texts are identical (XF 15/17);
  - no factor reads another factor's binding;
  - no factor id is a substring of a tool name;
  - no docstring carries an ordering word;
  - no forbidden import appears (the only import is `decimal`).
- Tool bodies:
  - every body creates and updates its own rows;
  - every body refuses a non-whole day count or one below 1, and an amount ≤ 0;
  - amounts are rounded half up with Decimal.
- uuid8s 78fe9a0a, 56dfc7d9, 194aeb06, 991dca72, 702d4c7f: distinct, no common pattern.
- **T1:** recomputed on both worlds; every one of the 26 factors moves its own scored value.
- **T2:** each factor alone live, with all others at baseline. All 26 move:

  | schedule | all-baseline | factor alone live |
  | --- | --- | --- |
  | A | 11336.00 | 10946.00 / 10769.20 / 10969.40 / 10348.00 |
  | B | 10464.00 | 10104.00 / 9940.80 / 10125.60 / 9552.00 / 10028.00 / 8720.00 |
  | C | 8284.00 | 8104.00 / 7041.40 / 8016.10 / 7562.00 / 6540.00 |
  | D | 10900.00 | 10525.00 / 10355.00 / 10547.50 / 9950.00 / 9592.00 |
  | E | 7412.00 | 7157.00 / 6300.20 / 7172.30 / 6766.00 / 6976.00 / 6104.00 |

- **Method shape:** rate binding still passes pairwise.
- **Multi-source factors:** isolation (agreement × reservation room) and dietary credit (reservation room × entry span) appear in all five schedules.
- **Cross-difficulty factors:** rate binding and isolation (private) appear in all five.

### Status of each revision-4 RED
| id | status | evidence |
| --- | --- | --- |
| R4-1 | CLOSED | No room change during a leave remains in any rule, compute or seed. T0 agreement: last room change 2026-06-16, made while active and before the leave; the resident's room is 431, the held room. T1 agreement: last room change 2026-04-14, made while active; room 437 is the held room. |
| R4-2 | CLOSED | The eight room-change factors are deleted. All remaining factors pass T2 (table above). |
| R4-3 | CLOSED | The request selector is deleted. |
| R4-4 | CLOSED | The gate sentence now reads "every earlier private-pay hospital leave of the resident that carried a single resident-private entry". That is the same set as the condition and B's scope. |
| R4-5 | CLOSED | Renewals are private_extension elections (T0 04f1f8d2…, T1 5e19b421…). T0 carries the October advance bill as two rate spans issued 09-25, with matching discharge_proration credits and a return rebill. T1's agreement is converted to Medical Assistance, so no private bill is owed; its MA case, pending accruals, settlements, patient pay and payments are seeded. The earlier single-entry charge is posted on statement day 3. |

### New findings (revision_5)

**R5-1 — SOURCE-FACTOR RED: dishonest (straw-man) baselines and stamped outcomes (CG-9 / CG-10 class).**

Six factors restate base sentences that remain in force and are not overwritten. Each charge's baseline nonetheless charges the very days those sentences exclude. Members:
- **ho_reserved_days** (D).
  - Rule: "Medicaid hospital reserved days count per hospitalization, consecutively from the departure date, up to the tier's per-hospitalization limit, and are never billed to the resident".
  - Base bedhold_agg_payer_day_limits: "Medicaid hospital reserved days count per hospitalization, consecutively from the departure date, up to the per-hospitalization limit".
  - Base bedhold_evt_charges: "Payer-covered reserved days are never billed to the resident".
- **hs_return_day, hc_return_day** (B, E).
  - Rule: "The return day never counts as a leave day".
  - Base bedhold_evt_day_counting: "the return day never counts".
- **hs_after_hold_end, tc_after_hold_end, hc_after_hold_end** (B, C, E).
  - Rule: "No day after the hold ended is charged … the day of release being the last held day".
  - Base bedhold_hold_end: "stops charges after the day of release".
  - Base day_counting: "A booked day later found to fall after the return … is reversed".
  - Variant parameter release_effective_basis: "the day of release is the last held day".

A reader who has only the base documents computes each factor's value, so the factor documents are not needed. That is the skill's "dishonest baseline: … a zero where the standard method gives a figure".

The census and release factors are also read off a stamp. bedhold_reservations.end_date ("last held day") gives the return-day plus after-hold days directly:

| world / entry | end_date | entry's days after end_date | factors |
| --- | --- | --- | --- |
| T0 B | 07-26 | 5 | 1 + 4 |
| T0 C | 10-15 | 4 | after-hold |
| T1 E | 10-13 | 4 | 1 + 3 |

The coordinator's round-5 route names "MA reserved days" and "census day counting … release-effective timing" as real levers. The audit records them RED under the skill's dishonest-baseline and stamp tests, and leaves that call to the coordinator.

If they are struck, every schedule keeps exactly 4 surviving factors: A 4, B 4, C 4, D 4, E 4. Each has 1 method, at least 2 parameters, a multi-source factor and a cross-difficulty factor, so the skill's floor still holds. The drawn counts (B 6, C 5, D 5, E 6) do not.

**R5-2 — SOURCE-TASK RED (task 0) + XF 29: back-dated release.**

The records:
- Release election 28285a94… was logged 2026-10-20 09:40 with effective_date 2026-10-15.
- The reservation records release_date and end_date as 2026-10-15.
- The October entry e1427af6… was booked through 10-19, on 10-20.

Base bedhold_hold_end: "A release is the resident's or representative's own decision, needs no advance notice and stops charges after the day of release". Under that sentence, the day of release is the day the decision is made.

Base election also requires the written election: "A private hold is recorded only on the resident's or representative's written election". A release that takes effect five days before it was given leaves the 10-16..10-19 held days uncharged, although the center held the bed. No charter rule produces such a back-dated release.

The two readings:
- Release day = the day it was made (10-20): no entry day falls after it, so C = 6017.00.
- Recorded effective date (10-15): C = 4720.20.

The persona is silent on the release.

### Observations (revision_5)
- O-17: both worlds carry infection-control isolation placements lasting five to six months (T0 06-16 → November; T1 04-14 → November). They are producible, but long.
- O-11 persists: the opening schedules' "already charged" count is always 0.
- O-1 persists: the middle months of a hold lasting three or more months are priced under base.
- O-18: the T1 world's MA reserve error is plausible. The office booked only 12 payer days on the 08-25 hospitalization, which reads as if the 3-day 08-10 hospitalization had been counted against the per-hospitalization limit. Base: "a leave that runs straight … the same hospitalization; … count per hospitalization". That error is the near-miss, and the rule excludes it by its own wording ("however the entry was booked").
- O-19: `_BedholdFormat.whole_days` raises on a non-numeric string instead of returning the documented error. This is not reachable through numeric arguments.

### post_reveal_note (revision_5)
- The reveal ran at 2026-10-22 17:39:52 UTC, after every revision-5 section above had been written. None of those sections were edited afterwards.
- Every scored argument (including the new day_count) and every computations figure matches in both tasks. The scopes are disjoint and together complete.
- Closed since revision 4: R4-1, R4-2, R4-3, R4-4, R4-5.
- Open:
  - R5-1: six factors that restate in-force base rules, stamped by end_date. Their levers appear on the coordinator's route list, so this item may be waived by coordinator ruling. If they are struck, every schedule still meets the 4-factor floor.
  - R5-2: task 0's back-dated release, which allows a second reading of C.

## closing_checklist (revision_5)
Not closed: the four relationships do not all PASS (R5-1, R5-2). Gate block cited above.

VERDICT revision_5: task0=RED SOURCE-TASK(R5-2 back-dated release 28285a94 logged 10-20 effective 10-15: C 4720.20 vs 6017.00),SOURCE-FACTOR(R5-1 hs_return_day,hs_after_hold_end,tc_after_hold_end restate in-force base census/release rules with straw-man baselines and end_date stamp) task1=RED SOURCE-FACTOR(R5-1 ho_reserved_days,hc_return_day,hc_after_hold_end restate in-force base MA-reserve/census/release rules with straw-man baselines and end_date stamp) charter=R5-1(ho_reserved_days,hs_return_day,hc_return_day,hs_after_hold_end,tc_after_hold_end,hc_after_hold_end; route-listed levers, coordinator may waive; floors hold at 4 per schedule after strike),R5-2(task0 seed release election 28285a94 / reservation release_date 10-15)

## revision_6

### charter_global (revision_6)
- Gate snapshot (`/tmp/erl0074_coord/snapshot.sh bed_hold_and_leave_reservations 6`, run by this auditor): "snapshot … round 6 at 2026-10-22T17:42:08". All gates rc=0:

  | gate | result |
  | --- | --- |
  | check_extended | EXTENDED OK |
  | check_task_tools | TASK TOOL CONTRACT OK |
  | replay_tasks --check | REPLAY OK |
  | check_solvability | SOLVABILITY OK |
  | check_compute | COMPUTE OK |
  | check_grounding | GROUNDING OK |
  | check_cross_fire | SCOPE OK |

- Hashes:

  | file | sha256 | vs revision 5 |
  | --- | --- | --- |
  | task_tools.py | 788ee1d3d53d47d9fb3a7ae3d63960b1c00fefa926029e717962529a19ccd4f4 | changed |
  | bedhold.extended.yaml | 4718b6c866677237fc36ce57160576a6e95f721b571fa950bc0dbe4c2dfcdbda | unchanged |
  | task0.view.json | 5b2478a89e1bb7e47e05a3e0254df08c048111204681b46764213d6e5f2e0d4e | changed |
  | task1.view.json | 3cc05143d0144d5c46946068c43e3a174474302fa4537f13d6b6782446bf247c | unchanged |

- Carried forward by reference: the charter is unchanged, so revision 5's charter-global sections stand. These are the rule/compute sweep, the overwrites, the prerequisites, the factor ladders, T2 and the method shape.
- Tool module, re-checked:
  - The only changes are in the format helpers. `half_up_cents` now returns 0.0 for non-numeric or non-finite input, which the bodies then refuse as ≤ 0. `whole_days` now returns −1 for such input, which is refused as < 1.
  - That closes O-19.
  - No forbidden import (only `decimal`) and no ordering word in any docstring.
  - Each of the five bodies still calls ctx.create and ctx.update itself.
- contamination_disclosure:
  - I read the round-6 worklog section.
  - Gold has been known since earlier rounds.
  - The revision-6 task sections were written after tasks/*.json was opened at 17:42:39 UTC. The DSL recomputation itself ran before that.

### Status (revision_6)
| id | status | evidence |
| --- | --- | --- |
| R5-2 | CLOSED | Release logged and effective on 2026-10-15; the reservation agrees. One reading. |
| R5-1 | OPEN, carried forward unchanged | ho_reserved_days, hs_return_day, hc_return_day, hs_after_hold_end, tc_after_hold_end and hc_after_hold_end restate in-force base rules (MA reserve; return day never counts; charges stop after the day of release). Each baseline charges the excluded booked days. The reworker argues the baseline is "the base charge clause read literally". The in-force base sentences beside that clause still exclude these days, and a base reader applies them all, so the dishonest-baseline finding stands. bedhold_reservations.end_date still names the end-of-entry outcome. These levers are named on the coordinator's route: the coordinator may waive this item. If it is waived, nothing else is open. If it is struck, every schedule keeps 4 factors, which meets the skill's floor but not the draw. |

No new defect was found and nothing regressed.

## closing_checklist (revision_6)
Not closed: R5-1 remains, pending the coordinator's waiver ruling.

VERDICT revision_6: task0=RED SOURCE-FACTOR(R5-1 hs_return_day,hs_after_hold_end,tc_after_hold_end restate in-force base census/release rules with straw-man baselines and end_date stamp; coordinator-waivable) task1=RED SOURCE-FACTOR(R5-1 ho_reserved_days,hc_return_day,hc_after_hold_end restate in-force base MA-reserve/census/release rules with straw-man baselines and end_date stamp; coordinator-waivable) charter=R5-1(ho_reserved_days,hs_return_day,hc_return_day,hs_after_hold_end,tc_after_hold_end,hc_after_hold_end; route-listed levers, coordinator may waive; floors hold at 4 per schedule after strike)

## revision_7
- Gate snapshot `/tmp/erl0074_coord/snapshot.sh bed_hold_and_leave_reservations 7`, run by this auditor: "snapshot … round 7 at 2026-10-22T18:05:23". All 7 gates returned rc=0:

  | gate | result |
  | --- | --- |
  | check_extended | EXTENDED OK |
  | check_task_tools | TASK TOOL CONTRACT OK |
  | replay_tasks --check | REPLAY OK |
  | check_solvability | SOLVABILITY OK |
  | check_compute | COMPUTE OK |
  | check_grounding | GROUNDING OK |
  | check_cross_fire | SCOPE OK |

- Source and view hashes equal revision 6:

  | file | sha256 |
  | --- | --- |
  | task_tools.py | 788ee1d3d53d47d9fb3a7ae3d63960b1c00fefa926029e717962529a19ccd4f4 |
  | bedhold.extended.yaml | 4718b6c866677237fc36ce57160576a6e95f721b571fa950bc0dbe4c2dfcdbda |
  | task0.view.json | 5b2478a89e1bb7e47e05a3e0254df08c048111204681b46764213d6e5f2e0d4e |
  | task1.view.json | 3cc05143d0144d5c46946068c43e3a174474302fa4537f13d6b6782446bf247c |

  The task files are also unchanged (mtime 17:41:17 UTC; gold the same). Every revision-6 section is therefore carried forward by reference.
- **Coordinator decision recorded: R5-1 is WAIVED** and logged as BLUEPRINT-KNOWN in the coordinator worklog.
  - Waived factors: ho_reserved_days, hs_return_day, hc_return_day, hs_after_hold_end, tc_after_hold_end, hc_after_hold_end.
  - The coordinator's reasons:
    - the frozen charter is thin;
    - the drawn counts cannot be met any other way;
    - the six factors agree with the in-force base rules on every in-scope world, so they move no scored value, no GT and no unique solution.
  - The finding text of revisions 5 and 6 stands as the auditor's record. It is not counted as RED.
- R5-1 was the only open item after revision 6, so nothing else remains open.

## closing_checklist (revision_7)
- Audit files:
  - 0.md, 1.md and _difficulty.md correspond one-to-one with the tasks.
  - Revisions 1–7 are kept in order and append-only.
  - Every comparison section matches GT on every scored value.
- Coverage:
  - The five extended policies are fully covered.
  - The scopes are pairwise disjoint: task 0 has opening, hospital-stay and closing; task 1 has hospital opening and hospital closing.
  - Task tools and GT are closed.
  - The uuid8s are independent.
- Trees (all acyclic):

  | task | prerequisites | value_input | user-owned writes | load bearing |
  | --- | --- | --- | --- | --- |
  | 0 | 2 | 1 | B, C | yes (skipping A changes C) |
  | 1 | 1 | 1 | E | yes (skipping D changes E) |

  - The difficulty-wide prerequisite graph is acyclic.
- Factors:
  - Every computation has a self-sufficient baseline and 4–6 factors, each with 1 method and at least 2 parameters.
  - Each task has multi-source factors (isolation, dietary) and cross-difficulty factors (private).
  - Every factor passes T1 and T2.
  - Baselines give definite numbers that differ from gold.
  - R5-1 is under the coordinator's waiver.
- Gates: re-run on the final form by the coordinator's snapshot above, 7/7 OK.

VERDICT revision_7: task0=PASS task1=PASS charter=CLEAN

## revision_8

### Inputs
- **Gate snapshot.** I ran `/tmp/erl0074_coord/snapshot.sh bed_hold_and_leave_reservations 8`: "snapshot … round 8 at 2026-10-23T06:20:59". All gates returned rc=0:

  | Gate | Output |
  | --- | --- |
  | check_extended | EXTENDED OK |
  | check_task_tools | TASK TOOL CONTRACT OK |
  | replay_tasks --check | REPLAY OK |
  | check_solvability | SOLVABILITY OK |
  | check_compute | COMPUTE OK |
  | check_grounding | GROUNDING OK |
  | check_cross_fire | SCOPE OK |

- **Hashes.** Only the charter changed:

  | File | sha256 | vs revision 7 |
  | --- | --- | --- |
  | task_tools.py | 788ee1d3d53d47d9fb3a7ae3d63960b1c00fefa926029e717962529a19ccd4f4 | unchanged |
  | bedhold.extended.yaml | f9fc40ef629566a4d77d7457099fa5c269bdba0575adab93c0c148162cfeb2de | changed |
  | task0.view.json | 5b2478a89e1bb7e47e05a3e0254df08c048111204681b46764213d6e5f2e0d4e | unchanged |
  | task1.view.json | 3cc05143d0144d5c46946068c43e3a174474302fa4537f13d6b6782446bf247c | unchanged |

  The base copy is still identical to the blueprint.
- **Read for this round, at the coordinator's direction (disclosed):**
  - the S1–S4 entries of audits/policy_kb/bed_hold_and_leave_reservations/_kb_verdict.md;
  - the worklog section "REWORK round 7 (KB audit … S1, S2)", which is the reworker's round-8 claim set.

  Before revision 1, the brief limited audits/ reads to XF_recipe.md. This read is a later coordinator instruction.

### Verification of S1 and S2 (charter re-derived for the changed parts)

**S1 — rule ≠ compute on the isolation condition. CLOSED.** The class is swept on all five policies: to, hs, tc, ho and hc_isolation_rate.
- Each compute now adds the binding `{p}_agr_move = CFIELD('private','last_room_change_date', status=current agreement)`.
- Both isolation tiers require `{p}_agr_move and DAYS({p}_agr_move, dep) >= 0`.
- The rule sentence now states the tested condition: "the agreement's last room change, the center's infection-control move, being dated no later than the departure date". The ladder fall-through names "one recorded after the departure date". cross_category reads now include last_room_change_date.
- Decoy and absent-record probes on task 0's A (all follow the rule):

  | Probe | Expected tier | Result |
  | --- | --- | --- |
  | Move dated after departure (09-06) | own tier | 10032.10 |
  | Move on the departure date (09-05) | isolation tier ("no later than") | 9118.20 |
  | No move date recorded | own tier | 10032.10 |

**S2 — the rate-binding wording gap. CLOSED.** The class is swept on all five rate_binding factors.
- Rule and ladder tier 1 now read "… delivered fewer than the agreement's rate-change notice days before the schedule date, or on or after the schedule date". That is exactly the compute's `DAYS(schedule, notice) + N > 0`, and it agrees with the private charter's rate_effective_basis (later of the schedule date and notice + notice days).
- Probes on task 1's D:

  | Notice delivered | Days before schedule date | Branch | Result |
  | --- | --- | --- | --- |
  | 2026-07-01 | on the date | binding 08-30, every day current | 8008.00 |
  | 2026-05-02 | 60 | binding 07-01 | 8008.00 |
  | 2026-05-01 | 61 | "otherwise" split at the schedule date | 8008.00 |

  All three agree with the wording.
- The pairwise method shape is unchanged and still passes. Tier 1 keeps its later-of pick.

### Sweeps on the changed charter
All of these are clean:
- compute_basis quotes are verbatim in their rules.
- Baseline sentences appear in the rules.
- Prerequisite policy_source sentences appear in the rules.
- The shared replaced_by sentence appears in each rule.
- No factor reads another factor's binding: `{p}_agr_move` belongs to the isolation factor's own bindings.
- No factor id is a substring of a tool name.

T1 and T2 were re-run on both worlds:
- All 26 factors move their own scored value (T1).
- Every factor alone moves from the all-baseline value (T2).
- The scored figures and the factor_sensitivity figures are unchanged and equal tasks/*.json, which was modified 06:19:57 UTC and read at 06:21:48 UTC.

### Other KB source items (not in this round's scope; recorded)
- **S3.** This is the XF A3 assembly-sentence class. The hospital opening rule's order sentence names factor quantities: "as many as the larger of those held before the notice and those payer-covered". The coordinator routed S3 as a decided placement note, and the quantity it names belongs to the waived R5-1 factor ho_reserved_days. Recorded as an observation under that routing.
- **S4.** Base parameter naming. BLUEPRINT-KNOWN, coordinator.

### Status
- R5-1: waived (coordinator, revision 7).
- S1: closed.
- S2: closed.
- No regression and no new defect was found.

## closing_checklist (revision_8)
- The revision-7 checklist still holds.
- Gates were re-run on the final form by the coordinator's snapshot above: 7/7 OK.

VERDICT revision_8: task0=PASS task1=PASS charter=CLEAN

## revision_9
- **Gate snapshot.** I ran `/tmp/erl0074_coord/snapshot.sh bed_hold_and_leave_reservations 9`: "snapshot … round 9 at 2026-10-23T10:45:09". All seven gates returned rc=0:

  | gate | result |
  | --- | --- |
  | check_extended | EXTENDED OK |
  | check_task_tools | TASK TOOL CONTRACT OK |
  | replay_tasks --check | REPLAY OK |
  | check_solvability | SOLVABILITY OK |
  | check_compute | COMPUTE OK |
  | check_grounding | GROUNDING OK |
  | check_cross_fire | SCOPE OK |

- **Hashes.**

  | file | sha256 | status |
  | --- | --- | --- |
  | task_tools.py | 788ee1d3d53d47d9fb3a7ae3d63960b1c00fefa926029e717962529a19ccd4f4 | unchanged |
  | bedhold.extended.yaml | f9fc40ef629566a4d77d7457099fa5c269bdba0575adab93c0c148162cfeb2de | unchanged |
  | task0.view.json | 930104c61dc7c0136994cdd5f12e4aabed25501aa4830f1a588891b96ae806a6 | changed (seed) |
  | task1.view.json | 90f6b3692056baa864249f6bb33a22760b84f504c5be7261e18a4afa5ab5ae9e | changed (seed) |

  Because the charter and tool module are unchanged, the charter-global sections of revision 8 are carried forward by reference.
- **Read, at the coordinator's direction (disclosed):**
  - the S5/S6 entries of audits/policy_kb/bed_hold_and_leave_reservations/_kb_verdict.md;
  - the worklog section "REWORK round 8 (KB cross-product re-judge …)";
  - published docs/private: late_charge_rule, late_charge_and_collection_figures, payment_posting_and_returned_payments, agreement_closing_rule, security_deposit_terms, collection_agency_referral, payer_source_conversion_and_reversion, move_out_credits_and_refunds, room_change_credit.

### Routed items
**S5 — CLOSED (task 1).** The converted agreement stays open lawfully under the published closing rule, because the deposit applied at disposition leaves 384.00 of May owed. The bed-hold factor reads are unchanged. Class sweep: the only other seeded agreement (task 0) is active, so no other member exists.

**S6 — CLOSED (task 0).** Each payment is now applied up to its named charge's open balance. Class sweep, run over every private_payment in both worlds against its charge's open balance at the posting date: no payment exceeds that balance.

Per-charge open balances, recomputed by this auditor from the views:

| task | account_balance | past-due room-and-board balance | late charge owed |
| --- | --- | --- | --- |
| task 0 | 16716.00 (sum of open balances) | nets to 0, below the 50.00 minimum | none |
| task 1 | 384.00 (sum of open balances) | — | none while converted |

### Cross-product rows
The other products' seeded rows (private 32 + 1 in task 0; private 15 + 1, medicaid 15 + 1 + 1 in task 1) were checked against the published private and medicaid rules on spans, rates, bases, credits, payments, deposit, disposition, patient pay (1476.10 = 1724.00 − 202.90 − 45.00), accruals and settlements. No defect was found.

Observations (none required by the docs):
- Task 0 carries rebill/credit pairs that net to zero.
- Task 1 has converted_to = medicaid_pending after approval.
- Task 1 has a permitted but not required collection referral.

### Gold and scored reads
- Gold did not move. Recomputed with the charter compute on the new views: 9118.20, 6663.30, 4720.20, 7715.40, 4059.90. All 26 sensitivities and all baselines equal tasks/*.json, read 10:46:23 UTC.
- T1 and T2 still move for every factor.
- No regression.

### Status
| item | status |
| --- | --- |
| R5-1 | waived |
| S1, S2 | closed (revision 8) |
| S5, S6 | closed |
| S3 | observation, coordinator routing |
| S4 | BLUEPRINT-KNOWN |

## closing_checklist (revision_9)
- The revision 7/8 checklist still holds.
- Gates were re-run on the final form (snapshot above): 7/7 OK.

VERDICT revision_9: task0=PASS task1=PASS charter=CLEAN
