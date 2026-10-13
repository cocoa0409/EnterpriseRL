# Policy-task audit — folio_charges_and_adjustments / charter-global

## charter_global_frozen

- Freeze time: 2026-10-05T13:31Z (written before any task's GT was revealed; nothing in this section is derived from a revealed GT field).
- Auditor: independent policy-task auditor (erl-task-policy-audit), not the author of the artifacts.
- Frozen inputs (sha256, re-verified against `/tmp/env0036_views/folio_charges_and_adjustments/HASHES.txt`):
  - `tasks/folio_charges_and_adjustments/folio.extended.yaml` — `7b58cf68231c6412e8002fa10ccca972ebcafbb4743927a02fb5f76c9770dbb4`
  - `tasks/folio_charges_and_adjustments/task_tools.py` — `a5ad1bad92eb29910becc28bdd5cf359f55c193a35eb4075632688bc9074c68c`
- Fields read: the scenario blueprint (`blueprint.yaml`, `db_schema.json`, `share_tools.py`, `products/folio.yaml`; `products/loyalty.yaml` and `products/booking.yaml` only for the cross-category reads and seed-consistency checks), the extended charter, the task tool module.
- Fields masked / not read: every `tasks/*.json` (only the orchestrator's masked views were used), `worklog.md` of this difficulty, the scenario `worklog.md`, all other audit directories.
- Entry conditions (Step 0): the gate snapshot `/tmp/env0036_views/folio_charges_and_adjustments/GATES.txt` shows EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK; masked views + hashes are supplied. Inputs complete. A machine green light here is only the entry ticket.
- Base copy: parsed equality of every top-level key of `blueprint/products/folio.yaml` (category, display_name, binding, lifecycle, accounts, parameter_schema, variants, events, measures, policies) against the extended file — all `True`; the only extra key is `extended_policies`. The base section is verbatim.

### policy_conflict_scan

Extended policies (5), their subject, trigger, target tool, owner and computed quantity:

| policy | subject | trigger | target_tool (owner) | computes | prerequisite |
| --- | --- | --- | --- | --- | --- |
| folio_ext_breakfast_credit | folio_breakfast_benefit_credit | state_due | post_breakfast_credit_af6b7bed (agent) | credit_amount | [] |
| folio_ext_dining_allowance_carryover | folio_breakfast_benefit_credit | on_request | apply_dining_allowance_ccaea779 (user) | carry_amount | breakfast_credit (value_input, state) |
| folio_ext_self_parking_savings | folio_adjustment | state_due | correct_self_parking_29958fbc (agent) | savings_amount | [] |
| folio_ext_valet_parking_savings | folio_adjustment | state_due | correct_valet_parking_0a0ec721 (agent) | savings_amount | [] |
| folio_ext_weekly_parking_cap | folio_adjustment | on_request | elect_weekly_parking_5ade5692 (user) | excess_amount | self_parking (value_input, state), valet_parking (value_input, state) |

Overlaps examined:
- Breakfast credit vs dining carry-over share the subject `folio_breakfast_benefit_credit` and both inherit the base `folio_breakfast_benefit` eligibility (brand without complimentary breakfast, min tier, tier effective on or before the business date, no B&B/OTA, status open or reopened, desk limit). They act on different lines (breakfast line vs food_beverage line) and their only interaction is the declared value_input edge (breakfast credits of the day are deducted from the day's dining allowance). Compatible.
- Self-parking savings, valet savings and the weekly cap all write `folio_adjustment` on parking lines. Self and valet act on disjoint line sets (parking_self vs parking_valet) and neither reads the other's output; the weekly cap reads both outputs (declared edges). Shared resources: the base `desk_limit` (folio_msr_desk_adjustments counts every posting_sequence-0 adjustment and benefit credit, and all five tools write posting_sequence 0) and the base dedup `one_adjustment_per_line` (the self/valet corrections land on the most recent self/valet line, the weekly excess on the parking line of the seventh night parked). Whether either creates an order dependency or a collision is a per-world question and is checked in each task file.
- Time anchors: all five policies act on the current (in-house or open) folio; none reads `actual_check_out_date` except through the inherited base dispute/late-charge windows. No conflict.
- Cross-category read boundaries: every extended policy declares `cross_category` reads of `booking` (adults, room_type, nights, booking_channel, variant_name = rate plan) and `loyalty` (variant_name = tier, cobrand_card, elite_night_credits); every `CFIELD` in compute matches a declared read. No undeclared read.
- Terminal states: each tool books one line and lowers `balance_due`; none changes folio status. No conflicting terminal states.

Claimed-scope partition (derived from the charter's prerequisite graph alone, not from any task's `charter_scope`): the graph has exactly two connected components — {dining_allowance_carryover → breakfast_credit} and {weekly_parking_cap → self_parking_savings, weekly_parking_cap → valet_parking_savings}. With M=2, the only exclusive and jointly complete partition is one component per task. Confirmation against each task's `charter_scope` is a post-reveal item in the task files.

Blueprint scope observation: the difficulty claim lists event types `folio_reopen`, `folio_resettle`, `folio_refund`, which no extended policy and no task tool writes. This is a coverage observation about the blueprint claim, not a defect of any of the four relationships.

### rule_compute_equivalence

Every `compute_basis` quotation was machine-checked to occur verbatim in its policy's `rule` (whitespace-normalised): all present. Every `baseline.rule` sentence occurs verbatim in its `rule`: all present. Sweep per policy:

- **folio_ext_breakfast_credit.** `breakfast_day` = LATEST breakfast business_date ⇔ "the breakfast line of the most recent morning of the stay on which a breakfast was charged". `breakfast_line` = MAX amount on that day: the rule speaks of "the breakfast line" (singular); MAX is a selection the rule never states (observation O-2; no consequence where a morning carries one breakfast line). `persons_covered`, `per_person_credit` (RND(…×1.3, 2) ⇔ "multiplied by the Ambassador breakfast scale and rounded half up to the cent"), `suite_uplift`, `card_uplift`, `morning_allowance` ((pp + suite + card) × persons ⇔ "the uplifts are added per person before the multiplication and are never multiplied by the scale"), `result` = RND(MN(line, allowance), 2) ⇔ "rounded half up to the cent and only at the end". Each factor ladder tier is a rule sentence and a branch of its `decides` binding, and vice versa. Equivalent.
- **folio_ext_dining_allowance_carryover.** `dining_day`/`dining_line` ⇔ "most recent business date … largest food and beverage line of that business date". `day_breakfast_credits` = SUM of `folio_breakfast_benefit_credit` amounts at that business_date ⇔ "the elite breakfast credits standing for breakfasts of that business date, whoever posted them": the compute does not restrict to credits that name a breakfast line, and the dining carry-over tool itself books event_type `folio_breakfast_benefit_credit` (observation O-3; it would only matter for a second carry-over on the same date, which the rule's "one food and beverage line" excludes). `direct_booking` = four channels ⇔ rule's list. `dining_persons`, `daily_per_person`, `stay_uplift`, `engagement_uplift`, `day_allowance` (three branches), `remaining_allowance` = MX(0, …), `result` = RND(MN(line, remaining), 2). Every tier of the five ladders is a rule sentence and a branch. Equivalent.
- **folio_ext_self_parking_savings.** `self_lines` COUNT, `tier_pct`, `card_pct`, `engagement_pct`, `stay_pct`, `savings_pct` (sum, "added first and applied once"), `pct_savings` = lines × rate × pct / 100, `rate_multiplier` (three branches), `result` = RND(pct_savings × multiplier, 2) ⇔ "The multiplier acts on the savings after the percentage has been applied and before the final rounding." Equivalent.
- **folio_ext_valet_parking_savings.** `valet_lines`, `nightly_saving` (four branches), four bonus bindings, `result` = RND((saving + bonuses) × lines, 2) ⇔ "The bonuses are added to the nightly valet saving first, and that per-night sum is then multiplied by the number of valet lines". Equivalent.
- **folio_ext_weekly_parking_cap.** `parking_charged`, `self_corrections`, `valet_corrections` ⇔ "every self-parking and valet line less the corrections those lines already carry"; `basis_rate`, `chargeable_nights`, `nights_counted`, `maximum_discount_pct` ⇔ their ladders; `stay_maximum` = RND(basis × chargeable / 7 × nights × (1 − disc/100), 2) ⇔ "rounded half up to the cent" + "the discount acts on the stay's parking maximum after the nights are counted and before it is rounded"; `result` gates on `parked_lines >= minimum_nights_parked` while the rule says "a stay with fewer than the minimum nights parked has no excess" — lines and nights parked differ only where two vehicles are parked on one night (observation O-4; neither world has that).

No compute invents a basis; no rule makes an empty promise beyond observations O-2 to O-4.

### action_binding_and_uuids

- `(target_tool, computes)`: (post_breakfast_credit_af6b7bed, credit_amount), (apply_dining_allowance_ccaea779, carry_amount), (correct_self_parking_29958fbc, savings_amount), (correct_valet_parking_0a0ec721, savings_amount), (elect_weekly_parking_5ade5692, excess_amount) — each claimed by exactly one policy.
- uuid8s `af6b7bed`, `ccaea779`, `29958fbc`, `0a0ec721`, `5ade5692`: pairwise distinct, no shared prefix or tail, no sequential or adjacent pattern. Consistent with independent generation.
- Docstrings: no docstring names another tool or states a position in a sequence. The only ordering-word hits are "(rounded half up to the cent before booking)" (all five) and "the folio balance after the credit" (post_breakfast_credit). Both describe one call's own rounding/return value, not a cross-action order. No confirmation, review or wait is added.
- Function bodies (`task_tools.py`): each tool does `ctx.find` of the folio and related line, books one `folio_postings` row and updates `balance_due`. None checks status, eligibility, amounts or other lines, and none errors or hints when a prerequisite is unresolved. **The tool layer judges no prerequisite.**
- The reason codes the tools hard-code: breakfast credit `elite_benefit_not_applied`; dining carry-over `not_applicable` (event_type `folio_breakfast_benefit_credit`); self/valet `elite_benefit_not_applied`; weekly `incorrect_rate`. These match the `replaced_by` texts (the weekly overwrite replaces the base `incorrect_rate` clause).

### prerequisite_graph

- `prerequisite` is filled in on all five policies (`[]` on breakfast_credit, self_parking_savings, valet_parking_savings).
- Edges: dining_allowance_carryover → folio_ext_breakfast_credit; weekly_parking_cap → folio_ext_self_parking_savings; weekly_parking_cap → folio_ext_valet_parking_savings. Each `problem` is an extended policy id in this file, never a base policy and never the policy itself. The graph is acyclic (depth 1, two components).
- `policy_source` of all three edges is verbatim in its own policy's `rule` (machine-checked: `in_rule True`).
- `form: state` on all three; no `fallback_reason` on any (correct for state form).
- `gate` names an existing compute binding of the blocked policy: `day_breakfast_credits`, `self_corrections`, `valet_corrections` — all present, all `kind: value_input` (each binding is a SUM that the depended-on write changes).
- `resolved_by` equals the depended-on policy's `target_tool` on all three edges, and each such tool books exactly the row type the gate binding sums (`folio_breakfast_benefit_credit` at the breakfast's business date; `folio_adjustment` with the parking line's charge_code), so `effect` genuinely holds.
- `condition` texts are at the strength of the sentences (see next section); no authoring-viewpoint wording ("in this task", "at the opening") appears.

### prerequisite_sentences

Edge D (dining ← breakfast credit). Sentence: "The part of a day's dining allowance carried to a food and beverage line is fixed only after every breakfast line of that business date carries its elite breakfast credit."
- Ordering connective "only after"; joins this policy's own result (the carried part) to a record-visible state ("every breakfast line of that business date carries its elite breakfast credit" — a credit line naming the breakfast line, which `find_folio_postings` shows via `related_posting_id`). Names no tool, no policy id, no snake_case token, no row id. Scope: "every breakfast line of that business date" = the `condition`'s "Every folio line with charge code breakfast whose business date is the carry-over day is named by an elite breakfast credit line". Same strength.
- One write brings it about: `folio_ext_breakfast_credit`'s rule ("when the outlet did not apply it guest services posts it later … for the breakfast line of the most recent morning"). The only other tool booking `folio_breakfast_benefit_credit` is the dining carry-over itself, which its own rule and docstring direct to a food and beverage line, not a breakfast line. Single reading.
- Derivation a reader performs: read the carry-over rule → the result waits on breakfast lines of the date carrying their elite breakfast credit → read the folio lines → find which policy's rule describes posting an elite breakfast credit that the outlet missed → `folio_ext_breakfast_credit`. Unique.
- Restriction a reader must notice: `folio_ext_breakfast_credit` posts only for "the most recent morning of the stay on which a breakfast was charged"; the edge is resolvable only where that morning is also the carry-over day. Checked per world.
- The depended-on rule does not restate the sentence; the blocked rule carries no second wording, no tool name and no other problem's id.

Edge S (weekly ← self-parking). Sentence: "The weekly parking maximum of a stay is applied only after the self-parking lines of the stay carry the Ashbury Rewards parking savings they are owed."
- "only after"; state "the self-parking lines of the stay carry the Ashbury Rewards parking savings they are owed" — record-visible (an adjustment naming a self-parking line). One write: `folio_ext_self_parking_savings` ("guest services posts the self-parking savings of the stay as one correction against the most recent self-parking line"). The weekly election itself also books a `folio_adjustment` on a parking line, but with the reason "charged above the applicable rate", not the parking savings — no second candidate. Strength matches the `condition`.

Edge V (weekly ← valet). Sentence: "The weekly parking maximum of a stay is not worked out until the valet lines of the stay carry the Ashbury Rewards valet savings they are owed."
- "not … until"; state record-visible; one write: `folio_ext_valet_parking_savings`. Strength matches.

Other cross-problem order statements in rules:
- Extended rules: none beyond the three edge sentences.
- Base rules: `folio_evt_adjustment` "a settled folio is first reopened" and `folio_post_stay_correction` "Once the balance is zero the folio is settled again" state cross-problem orders. No extended edge rests on them, and both tasks' folios are `open` (checked per task). Recorded as observation O-5.

### override_declarations

Sentence-by-sentence against each `base_policy_refs` entry.

**folio_ext_breakfast_credit vs folio_breakfast_benefit**
1. "At brands where complimentary_breakfast_all_guests is false, a stay credited to an Ashbury Rewards member whose tier is elite_breakfast_min_tier or higher receives, for each breakfast line charged at the outlet during the stay, a credit of the lower of that line's amount and elite_breakfast_credit_per_person_usd times elite_breakfast_persons." — eligibility followed; the amount clause is declared superseded ("a credit of the lower of that line's amount and …") and replaced by the morning's-allowance clause. Declared.
2. "The credit names the breakfast line it offsets, at most one credit per breakfast line, and unused credit is not paid out or carried to other charges when breakfast_credit_unused_refundable is false." — followed by the breakfast credit; the carry-to-other-charges clause is declared superseded by the dining carry-over policy.
3. "The member's tier is the variant_name on the membership, and it applies to a breakfast only when the membership's tier_effective_date is on or before that breakfast's business date." — inherited, not weakened.
4. "When the tier took effect after the breakfast, guest services cannot establish the tier held that morning and refers the question to the hotel as a billing dispute." — inherited.
5. "No credit is given on Bed & Breakfast Package Rate stays … or on reservations booked through an online travel agency." — inherited.
6. "When the outlet did not apply the credit, guest services posts it later with adjustment_reason elite_benefit_not_applied, subject to the brand's desk_adjustment_limit_usd." — followed. The extended rule adds "Guest services posts a missed credit for the breakfast line of the most recent morning of the stay on which a breakfast was charged." Base entitles each breakfast line; the extended sentence limits the desk's posting to the most recent morning, and no `overwrite` names it. This is a narrowing of base 1/6 that is **not declared** (finding F-1). Its consequence exists only on a world where an earlier morning's breakfast is also uncredited; checked per task.
7. "Credits are posted only to a folio whose status is open or reopened." — inherited.

**folio_ext_dining_allowance_carryover vs folio_breakfast_benefit**
- Sentence 2's "unused credit is not paid out or carried to other charges …" — declared superseded; replaced_by "A member … may carry what remains of a day's dining allowance to one food and beverage line …". The extended rule keeps "Unused allowance is never paid out and never carried to another business date", compatible.
- Sentences 1, 3–7 apply to the carry-over through its subject `folio_breakfast_benefit_credit` (min tier, tier effective date, B&B/OTA exclusion, desk limit, open/reopened). Not weakened by extended, tool or persona.
- The base event's `meaning` ("credited against a breakfast charged at the outlet") and `grain` ("One credit per breakfast line offset") are contradicted by a carry-over credit that offsets a food_beverage line. This is an event-definition/charter wording mismatch, not a policy sentence, and is covered by the declared supersession of "carried to other charges" (observation O-6).

**folio_ext_self_parking_savings / folio_ext_valet_parking_savings vs folio_incidental_rules, folio_evt_adjustment, folio_agg_courtesy_allowance**
- `folio_incidental_rules` "Parking is charged per night a vehicle is parked at self_parking_per_night_usd or, where valet_available is true, valet_parking_per_night_usd;" — declared superseded by both (and also by the weekly cap). The replacement keeps posting at the brand rate and adds a savings correction; the three replacements address different quantities and compose without contradiction.
- `folio_evt_adjustment` "elite_benefit_not_applied: a late check-out fee that folio_late_checkout exempts is removed in full." — declared superseded by both self and valet, each with a different `replaced_by` (the parking-savings sentence). Read literally, the merged charter no longer contains the late check-out-exemption removal, although `folio_late_checkout` still exempts such fees. The override extends a closed reason list, but its declaration supersedes an unrelated base provision (finding F-2). It has a consequence only on a world with an exempt late check-out fee to remove, which neither task has (checked per task). Observation level.
- `folio_evt_adjustment` "An adjustment corrects exactly one original folio line, names it in related_posting_id and carries its charge code" — followed in form (one line named). The amount, though, is a stay-wide saving booked against one line. This conflicts only if the saving exceeds that line's amount (checked per task).
- `folio_evt_adjustment` "Each original line is adjusted at most once." and the desk-limit sentence — inherited. Checked per task.
- `folio_agg_courtesy_allowance` — governs minibar courtesy removals only; no sentence touches parking. Followed.

**folio_ext_weekly_parking_cap vs the same three**
- Parking sentence of `folio_incidental_rules` — declared superseded.
- `folio_evt_adjustment` "incorrect_rate: a room line that differs from the reservation's nightly rate is adjusted by the difference, and its room_tax line by the difference times the reservation's tax_rate_pct, rounded to the cent." — declared superseded by the weekly-excess sentence. Read literally, the merged charter loses the room-rate correction rule (finding F-2, same shape). It has a consequence only on a world with a mis-rated room line; checked per task.
- Base dedup and desk limit inherited; checked per task.

Disguised forms: no anonymous intermediate factor found (every intermediate is named in compute and quoted). No 0/1 multiplier zeroes a base quantity. No dropped base branch inside the computed quantity. No author note in the charter calls a base output a "wrong value".

### factor_ladders

Per policy (label as declared; ladder tiers including fall-through):

| policy | factor | label | decides | tiers | sources of non-fall-through tier conditions | cross_difficulty |
| --- | --- | --- | --- | --- | --- | --- |
| breakfast_credit | persons_covered_at_breakfast | parameter | persons_covered | 3 | T1 adults≥3 (booking) ∧ tier∈{Ti,Amb} (loyalty); T2 adults=1 (booking only) | booking |
| breakfast_credit | per_person_breakfast_credit | method | per_person_credit | 3 | tier (loyalty) | loyalty |
| breakfast_credit | suite_breakfast_uplift | parameter | suite_uplift | 3 | room_type (booking) | booking |
| breakfast_credit | cobrand_breakfast_uplift | parameter | card_uplift | 3 | cobrand_card (loyalty) | loyalty |
| dining_carryover | dining_allowance_method | method | day_allowance | 3 | T1 tier (loyalty) ∧ direct channel (booking); T2 tier only | loyalty |
| dining_carryover | daily_dining_amount | parameter | daily_per_person | 3 | tier (loyalty) | loyalty |
| dining_carryover | dining_persons | parameter | dining_persons | 3 | T1 adults≥3 ∧ direct; T2 adults=1 ∧ direct — both fields of the same reservation row | booking |
| dining_carryover | stay_length_dining_uplift | parameter | stay_uplift | 3 | nights (booking) | booking |
| dining_carryover | engagement_dining_uplift | parameter | engagement_uplift | 3 | elite_night_credits (loyalty) | loyalty |
| self_parking | tier_parking_saving | parameter | tier_pct | 3 | tier | loyalty |
| self_parking | card_parking_saving | parameter | card_pct | 3 | cobrand_card | loyalty |
| self_parking | engagement_parking_saving | parameter | engagement_pct | 3 | elite_night_credits | loyalty |
| self_parking | stay_length_parking_saving | parameter | stay_pct | 3 | nights | booking |
| self_parking | member_rate_multiplier | method | rate_multiplier | 3 | T1 rate plan ∧ channel=app; T2 rate plan ∧ channel≠app — same reservation row | booking |
| valet_parking | valet_saving_method | method | nightly_saving | 4 | tier | loyalty |
| valet_parking | rate_plan_valet_bonus | parameter | plan_bonus | 3 | rate plan | booking |
| valet_parking | booking_channel_valet_bonus | parameter | channel_bonus | 3 | channel | booking |
| valet_parking | engagement_valet_bonus | parameter | engagement_bonus | 3 | elite_night_credits | loyalty |
| valet_parking | stay_length_valet_bonus | parameter | stay_bonus | 3 | nights | booking |
| weekly_cap | weekly_basis_rate | method | basis_rate | 3 | tier (T2's selected rate reads the folio's line counts) | loyalty |
| weekly_cap | chargeable_nights_per_week | parameter | chargeable_nights | 3 | tier | loyalty |
| weekly_cap | nights_counted | method | nights_counted | 3 | T1 direct channel ∧ nights≥7 (same reservation row); T2 channel=GDS | booking |
| weekly_cap | rate_plan_maximum_discount | parameter | maximum_discount_pct | 3 | rate plan | booking |

Structure checks that pass for every factor: 4–6 factors per policy (4, 5, 5, 5, 4); bindings pairwise disjoint within each policy; `decides` is an input, never `result`; every ladder has ≥3 pairwise-disjoint tiers including the fall-through; every tier's condition and value or method is stated in the `rule` and implemented as a branch of the `decides` binding; every fall-through equals the factor's `baseline` and the policy's `baseline.rule`; every tier value is a charter param (`K(...)`/`P(...)`); no two tiers select the same value. Every `baseline.rule` is self-sufficient: with the records and the brand params it yields a definite number with no factor applied.

Charter-global factor findings:

- **F-3 (label honesty) — `member_rate_multiplier` labelled `method` is a parameter.** Its three tiers are "multiplied by the app member-rate multiplier" (1.5), "multiplied by the member-rate multiplier" (1.25), "not multiplied" (= ×1). Compute: `rate_multiplier: "K('app_member_rate_multiplier') if … else (K('member_rate_multiplier') if … else 1)"`, used as `RND(pct_savings * rate_multiplier, 2)`. Every tier substitutes a different number into one formula, which is the skill's named mislabel shape. With it relabelled, `folio_ext_self_parking_savings` has 5 parameter factors and **0 method factors**, below the bound of 1 `method` per computation.
- **F-4 (label honesty) — `weekly_basis_rate` labelled `method` is a parameter.** Its tiers select which rate enters `stay_maximum = basis_rate × chargeable_nights / 7 × nights_counted × (1 − disc/100)`: the self-parking rate, the valet rate, or (T2) whichever of the two serves more lines. Every outcome is a rate number in the same formula. With it relabelled, the weekly cap keeps one method factor (`nights_counted`) and 3 parameter factors.
- **F-5 (unreal ladder) — the "is for seven or more nights" conjunct of `nights_counted` T1 holds for every customer who reaches the weekly write.** The rule admits the election only for "A guest whose stay has at least the minimum nights parked" (minimum_nights_parked = 7), and a reservation's nights are never fewer than the nights parked during it. So the conjunct holds for every eligible customer and divides none. It restates the policy's scope, and T1 is in effect "booked through a direct channel" alone. (Caveat: compute gates on parking *lines*, which can exceed nights only with two vehicles on one night — O-4.) If the factor is struck out by this test, the weekly cap is left with 3 factors and 0 method factors.
- **F-6 (unreal ladder) — the "booked through a direct channel" conjunct of `dining_persons` T1 and T2 never divides the customers for whom the factor bears.** `dining_persons` enters the result only in `day_allowance`'s first branch, whose condition already requires `direct_booking` (`"(daily_per_person + …) * dining_persons if ((member_tier == 'Ashbury Rewards Titanium Elite' or …) and direct_booking) else …"`). For every customer whose score `dining_persons` can move, the conjunct is true, so the factor is in effect decided by the registered adults alone. The dining computation keeps 4 factors if it is struck (method, daily amount, stay-length, engagement), so the count bound still holds there.
- **F-7 (multi-source) — no factor in the charter is multi-source in the sense the skill defines** ("every tier other than the fall-through a conjunction or a disjunction of two or more conditions over distinct records"). Only `persons_covered_at_breakfast` T1 and `dining_allowance_method` T1 combine conditions over distinct records (booking reservation + loyalty membership), and each has a second non-fall-through tier on one record (T2 "exactly one adult"; T2 "Platinum Elite"). `dining_persons`, `member_rate_multiplier` and `nights_counted` combine two fields of the **same** reservation row, and F-5/F-6 show that one conjunct of `dining_persons` and of `nights_counted` T1 is vacuous. Under the skill's wording, neither component's computations carry a multi-source factor. (Under a looser "two distinct fields" reading, `dining_persons` and `member_rate_multiplier` would qualify; this audit applies the text as written and records the reading.)
- **F-8 (seeded cross-difficulty rows contradict the loyalty charter)** — a seed-level check that each task file demonstrates on its own rows: both worlds' memberships hold "Ashbury Rewards Titanium Elite" with `status_valid_through` 2028-02-29 and a 2026 `tier_effective_date`, while `elite_night_credits` (= the 2026 year-to-date night credits per `db_schema.json`) is below the Titanium `qualifying_nights_required: 75` of `products/loyalty.yaml`, and the effective date is neither the day the YTD reached 75 nor the March 1 reassessment (`loyalty_elite_qualification`). Demonstrated per task.

Observations on labels and realism (no RED):
- `per_person_breakfast_credit` (method): ×1.3 with rounding vs +10 vs as-is. A multiplicative scale and an additive supplement are different operations, so the label is accepted. It is borderline.
- `valet_saving_method` (method, 4 tiers): Ambassador/Titanium share one algorithm (upgrade × share, 1.0 vs 0.5) and Platinum/fall-through share another (percent of valet rate, 8 vs 4). Two real methods with tier pairs differing only by a number. Hybrid, but outcomes are distinct.
- `weekly_basis_rate` fall-through "the brand's valet rate" for every other guest: for a guest who only self-parks, the maximum is built on the valet rate and cannot bind at Grand rates (self 42 × 7 = 294 < valet-based 58 × 6/7 × 7 = 348). A weekly maximum that never applies to the ordinary self-parking guest is close to a straw-man default. It is real for valet parkers, so this stays an observation.
- `nights_counted` T2 (GDS: parking lines rounded down to whole weeks) makes nights beyond the last whole week free, and T1 counts unparked reservation nights into the maximum. Direct bookings are treated less generously than GDS bookings, the reverse of usual hotel channel practice. Recorded as an observation; the demonstrable defect of this ladder is F-5.

Counts per policy as declared → after the tests above:
- breakfast_credit: 4 (3 parameter, 1 method) → 4 (3/1). Multi-source: none fully (F-7). Cross-difficulty: booking, loyalty.
- dining_carryover: 5 (4/1) → 4 or 5 depending on F-6 (≥3/1). Multi-source: none (F-6, F-7). Cross-difficulty: booking, loyalty.
- self_parking: 5 (4/1) → 5 (5/0) under F-3. **Method bound fails.**
- valet_parking: 5 (4/1) → 5 (4/1).
- weekly_cap: 4 (2/2) → 4 (3/1) under F-4, or 3 (3/0) if F-5 strikes `nights_counted`. **Bound fails under the strict reading.**

### findings

| id | class | finding | bears on |
| --- | --- | --- | --- |
| F-1 | observation (consequence per world) | Undeclared narrowing: extended "posts a missed credit for the breakfast line of the most recent morning" vs base "for each breakfast line … receives a credit"; no `overwrite` names it | task 0 (check for an uncredited earlier morning) |
| F-2 | observation (consequence per world) | Over-broad overwrites: self/valet supersede base's late-check-out `elite_benefit_not_applied` clause, weekly supersedes base's room `incorrect_rate` clause; literally the merged charter loses both base corrections | task 0, task 1 (check for exempt late check-out or mis-rated room lines) |
| F-3 | SOURCE-FACTOR RED | `member_rate_multiplier` mislabelled method; self-parking computation has 0 method factors | task 1 |
| F-4 | SOURCE-FACTOR RED | `weekly_basis_rate` mislabelled method | task 1 |
| F-5 | SOURCE-FACTOR RED | `nights_counted` T1 conjunct "seven or more nights" holds for every eligible customer | task 1 |
| F-6 | SOURCE-FACTOR RED | `dining_persons` direct-channel conjunct never divides the customers whose score it moves | task 0 |
| F-7 | SOURCE-FACTOR RED | No multi-source factor (strict "distinct records" reading) in either component | task 0, task 1 |
| F-8 | SOURCE-FACTOR RED (demonstrated per task) | Seeded Titanium memberships contradict loyalty qualification rules | task 0, task 1 |
| O-2 | observation | `breakfast_line` MAX selection not stated in rule | — |
| O-3 | observation | `day_breakfast_credits` SUM does not restrict to credits naming breakfast lines; the carry-over tool books the same event_type | — |
| O-4 | observation | weekly eligibility "nights parked" vs compute `parked_lines` | — |
| O-5 | observation | Base rules state cross-problem orders (reopen first; resettle at zero); no edge rests on them | — |
| O-6 | observation | Base event meaning/grain of `folio_breakfast_benefit_credit` vs carry-over on a food_beverage line | — |

Charter-global relationships: **policy self-consistency (charter half): no demonstrable SOURCE-POLICY RED** (F-1, F-2 have their consequences checked per task). **Prerequisite graph and sentences: PASS.** **Action binding and uuids: PASS.** **Factor structure: SOURCE-FACTOR RED** (F-3 to F-7; F-8 per task).

## closing_checklist

Written after both reveals (2026-10-05T13:35:19Z onward). The charter-global section above was hashed at reveal (`00fdaad1…480f2c`) and is unchanged.

**The difficulty does not close.** Not every task passes all four relationships.

| item | status |
| --- | --- |
| Per-task files 0.md, 1.md one-to-one with tasks/0.json, 1.json; `_difficulty.md` alongside; first revision | yes |
| Every comparison section carries a PASS | **no** — task 0: SOURCE-FACTOR RED + SOURCE-TASK RED; task 1: SOURCE-FACTOR RED |
| Extended policies fully covered; scopes pairwise disjoint and jointly complete | yes — task 0 {breakfast_credit, dining_carryover}, task 1 {self_parking, valet_parking, weekly_cap}, matching each `charter_scope` |
| Task tools and GT closed; uuid8s independently generated and frozen | yes (§ action_binding_and_uuids) |
| Each tree has 1–3 prerequisite problems, ≥ max(n−1,1) value_input edges, ≥1 owner=user problem, no cycle; difficulty graph acyclic | yes — task 0 n=1 / 1 value_input; task 1 n=2 / 2 value_input; both roots owner=user |
| Every computation: self-sufficient baseline; 4–6 factors with ≥2 parameter and ≥1 method; per task ≥1 multi-source and ≥1 cross-difficulty; ladders ≥3 tiers stated in the rule, distinct in outcome, real in conditions and outcomes; every factor bears weight against an honest baseline; baseline ≠ gold | **no** — self-parking has 0 honest method factors (F-3); weekly basis rate mislabelled (F-4); vacuous conjuncts in `nights_counted` (F-5) and `dining_persons` (F-6); no multi-source factor in either task (F-7); seeded memberships contradict the loyalty charter (F-8). Weight, baseline honesty and baseline ≠ gold hold for all 23 declared factors and all 5 computations |
| Instantiation gates re-run on the final form | not re-run by the auditor (Step 0: the auditor cites the supplied snapshot). `folio.extended.yaml` and `task_tools.py` hashes are unchanged since the snapshot (`7b58cf68…dbb4`, `a5ad1bad…c68c`); the audit edited no artifact |

Per-task verdicts:
- Task 0 — policy self-consistency PASS; problem tree PASS; factors **SOURCE-FACTOR RED**; unique solution **SOURCE-TASK RED** (a state_due valet-savings correction is left owed by the world while the proof asserts nothing else is owed). See `0.md`.
- Task 1 — policy self-consistency PASS; problem tree PASS; factors **SOURCE-FACTOR RED**; unique solution PASS. See `1.md`.

## revision_2

### charter_global_frozen (revision_2)

- Written 2026-10-05T16:27Z onward, before any round-2 GT was read. Nothing here derives from a round-2 reveal. The round-1 text above is left untouched.
- Inputs (sha256, matching the new `/tmp/env0036_views/folio_charges_and_adjustments/HASHES.txt`):
  - `folio.extended.yaml` `6526212387d96eb28cbe04a96ad92c060c49e461e462f7cb079aec1c944b81e2` — **changed** from round 1 (`7b58cf68…`), so every charter-global section is re-derived in full below.
  - `task_tools.py` `a5ad1bad92eb29910becc28bdd5cf359f55c193a35eb4075632688bc9074c68c` — unchanged. The tool-module conclusions of round-1 § action_binding_and_uuids (uuid8s, docstrings, function bodies that judge no prerequisite) are carried forward on that hash.
- Entry conditions: the fresh gate snapshot `GATES.txt` shows all seven gates OK. Masked views are rebuilt with hashes. Base section is still verbatim (parsed equality of all ten base keys; the only extra key is `extended_policies`).
- Masked and not read: `tasks/*.json` (masked views only), all worklogs. The reworker's claims were received by item id only.

### policy_conflict_scan (revision_2)

- Subjects, triggers, target tools, owners and prerequisite edges are unchanged from round 1. There are still two components: {dining → breakfast} and {weekly → self, weekly → valet}.
- Cross-category reads: every `CFIELD` in compute matches a declared read.
  - Self-parking now reads booking `[nights, variant_name]` only; the booking channel was dropped from both rule and compute.
  - The weekly cap now reads booking `[variant_name, booking_channel]`; reservation nights were dropped from both rule and compute.
- Shared desk limit and per-line dedup: unchanged in kind; checked per world.

### rule_compute_equivalence (revision_2)

Machine check: every `compute_basis` quote and every `baseline.rule` sentence is verbatim in its rule.
- **Breakfast credit:** "the largest breakfast line of that morning when it carries several" now states `breakfast_line = MAX(...)`. **O-2 closed.**
- **Dining carry-over:** the rule now says "the elite credits already standing for that business date, that is the elite breakfast credits of that morning whoever posted them and any carry-over already applied that day". That is exactly what `SUM(... event_type='folio_breakfast_benefit_credit', business_date=dining_day)` sums, since the carry-over tool books the same event type. **O-3 closed.**
  - `dining_persons` compute no longer reads `direct_booking`; the rule says the same.
  - `day_allowance` T2 now reads `member_tier == Platinum and direct_booking`, matching "for an Ashbury Rewards Platinum Elite member whose stay was booked through a direct channel".
- **Self-parking:**
  - `combined_pct = 4 + card + engagement + stay` ⇔ "The combined saving percent is the member parking saving percent plus the card, engagement and stay-length parking savings".
  - `savings_pct` (×2 / +4 / as is) ⇔ "Tier parking benefit".
  - `rate_multiplier` (MFR ∧ Ti/Amb → 1.5; MFR ∧ Silver/Gold/Platinum → 1.25; else 1) ⇔ "Member-rate multiplier".
  - Equivalent.
- **Valet:** unchanged; equivalent.
- **Weekly cap:**
  - "the nights parked are counted as the parking lines of the stay, one line for each night the guest's vehicle was parked" now grounds `parked_lines >= minimum_nights_parked`. **O-4 closed.**
  - "The election covers the nights parked up to the moment it is made, and parking lines posted after it are charged as posted" settles the in-house timing. **Round-1 T1 tonight's-parking observation closed.**
  - `recent_service_rate`, `weekly_rate`, `full_weeks`, `remaining_nights`, `method_maximum` (three branches), `maximum_discount_pct` and `stay_maximum` (RND after the discount) are all rule sentences, and every rule tier is a branch.
  - Minor observation O-8: `recent_service_rate` resolves a same-night tie (a self and a valet line on one business date) to valet (`latest_valet_day >= latest_self_day`), and the rule does not say how a tie is broken. Neither world has a same-night tie.

### action_binding_and_uuids (revision_2)

- `(target_tool, computes)` pairs are unchanged and each is claimed once.
- Tool module unchanged (hash above). The round-1 conclusions stand: uuid8s independent, no sequencing in docstrings, no prerequisite judged in any function body.

### prerequisite_graph (revision_2)

- Unchanged edges: dining → breakfast_credit (`day_breakfast_credits`); weekly → self_parking (`self_corrections`); weekly → valet_parking (`valet_corrections`).
- All are `value_input`, form state, no fallback, and `policy_source` is verbatim in its rule (machine-checked).
- Gates exist in compute, and `resolved_by` equals the target tools. Acyclic. **PASS.**

### prerequisite_sentences (revision_2)

- The three sentences are word-identical to round 1. The round-1 four-point tests and unique-write derivations (Edges D, S, V) still hold. Nothing added to the depended-on rules restates them.
- New rule text adds no cross-problem order. In the breakfast rule, "a missed credit on an earlier morning is referred to the hotel as a billing dispute" is a referral within one problem. In the weekly rule, "parking lines posted after it are charged as posted" concerns night-audit postings, not another problem. **PASS.**

### override_declarations (revision_2)

- **F-1 closed.** `folio_ext_breakfast_credit` now declares a second overwrite naming the base sentence "When the outlet did not apply the credit, guest services posts it later with adjustment_reason elite_benefit_not_applied, subject to the brand's desk_adjustment_limit_usd." It is replaced by the most-recent-morning sentence (which keeps the reason and the desk limit and refers earlier mornings to the hotel). The narrowing is now declared, and the merged semantics are unique.
- **F-2 closed.** No extended policy now supersedes the base late-check-out `elite_benefit_not_applied` clause or the room `incorrect_rate` clause; those base corrections stand in the merged charter.
  - The only declared overwrite for the three parking policies is the `folio_incidental_rules` parking sentence. Its three `replaced_by` texts compose: posting at brand rates, two savings corrections, and the weekly election with "nights parked = parking lines".
- O-7 (new observation): the parking corrections carry base reason codes outside the cases base defines for them. Self and valet savings use `elite_benefit_not_applied` (base: late check-out fee); the weekly election tool uses `incorrect_rate` (base: room line).
  - No base sentence assigns any amount to a parking line under those reasons, so no second defensible amount exists.
  - The base "goodwill reduction without one of these reasons" sentence does not reach these entitlements, because each is a stated rule of the merged charter.
  - Observation only.
- Other base sentences: unchanged from round 1 (inherited). Dining's "carried to other charges" supersession is unchanged (declared).

### factor_ladders (revision_2)

Changed factors, with round-1 finding status:

| policy | factor | label | tiers (non-fall-through sources) | status |
| --- | --- | --- | --- | --- |
| dining | dining_allowance_method | method | T1 tier Ti/Amb (loyalty) ∧ direct channel (booking); T2 tier Platinum (loyalty) ∧ direct channel (booking) | multi-source over distinct records — **F-7 closed for the dining component** |
| dining | dining_persons | parameter | T1 adults≥3; T2 adults=1 (booking) | channel conjunct removed — **F-6 closed** |
| self | tier_parking_benefit (new) | method | T1 Amb: combined × 2; T2 Ti: combined + 4; else as is | multiplicative vs additive transformation, the same kind accepted for `per_person_breakfast_credit` in round 1 — accepted |
| self | member_rate_multiplier | parameter (relabelled) | T1 MFR (booking) ∧ Ti/Amb (loyalty); T2 MFR ∧ Silver/Gold/Platinum (loyalty) | label now honest — **F-3 closed**; multi-source over distinct records — **F-7 closed for the parking component** |
| weekly | weekly_basis_rate | parameter (relabelled) | T1 Ti/Amb → self rate; T2 Platinum → rate of the majority service; fall-through rate of the most recent night's service | label honest — **F-4 closed**; the round-1 straw-man observation on the valet-rate fall-through is closed by the new fall-through |
| weekly | nights_counted | removed | — | **F-5 closed** (the factor with the vacuous conjunct no longer exists) |
| weekly | maximum_method (new) | method | T1 Ti/Amb ∧ direct → pro-rated (weekly rate / 7 × nights parked); T2 Gold/Platinum ∧ direct → full weeks × weekly rate + remaining nights × basis, "never more than the weekly rate for the weeks rounded up"; fall-through → full weeks × weekly rate + remaining nights × basis | **new defect N-1 (below)** |

**N-1 — SOURCE-FACTOR RED (new): `maximum_method` T2 selects the same outcome as its fall-through for every possible input.**
- For a Gold Elite or Platinum Elite member, `chargeable_nights` is always the standard 6 (the chargeable-nights ladder gives 5 only to Ambassador and 5.5 only to Titanium), so `weekly_rate = basis × 6`.
- `remaining_nights` = `parked_lines − 7 × full_weeks` ∈ {0, …, 6}, so `basis × remaining_nights ≤ basis × 6 = weekly_rate`. Hence `weekly_rate × full_weeks + basis × remaining_nights ≤ weekly_rate × (full_weeks + MN(1, remaining_nights))`.
- So T2's `MN(…)` cap never binds, and T2 always equals the fall-through `weekly_rate * full_weeks + basis_rate * remaining_nights`.
- Machine check: 9 basis rates × 5 full-week counts × 7 remainders found 0 cases where T2 ≠ fall-through.
- The ladder therefore has two distinct outcomes, not three ("no two tiers … select the same value or method"; "a ladder of at least three … tiers"). One tier has been written as two.
- Under the skill's counting rule ("a rule the tests strike out is not a factor"), striking `maximum_method` leaves the weekly cap with 3 factors and **0 method**, below both the 4-factor and the 1-method bounds. If it is not struck, the weekly computation still carries a ladder that fails the distinct-outcome test.
- Affects task 1 (whose tree contains the weekly cap). Affected artifact: `folio.extended.yaml` `folio_ext_weekly_parking_cap` rule "Maximum method" sentence, compute `method_maximum`, `factors[maximum_method].ladder[1]`.

Unchanged factors (breakfast's four, dining's daily/stay/engagement, self's card/engagement/stay, all five valet factors, weekly chargeable nights and discount) carry their round-1 structural conclusions.
- `per_person_breakfast_credit` and `valet_saving_method` remain the round-1 borderline/hybrid observations.
- Every ladder has ≥3 tiers stated in the rule and implemented in compute.
- Bindings are disjoint within each policy (machine-checked: no duplicates).
- Every fall-through equals its factor baseline and the `baseline.rule`.
- All baseline rules are self-sufficient.

Counts:
- breakfast 4 (3/1)
- dining 5 (4/1)
- self 5 (4/1)
- valet 5 (4/1)
- weekly 4 declared (3/1) → 3 (3/0) after N-1
- Multi-source present in both components (dining method; self member-rate multiplier). Cross-difficulty present in both.

F-8 (seeded memberships vs loyalty charter) is a seed question and is re-checked in each task file.

### findings (revision_2)

| id | round-1 class | revision_2 status |
| --- | --- | --- |
| F-1 | observation | closed (declared overwrite) |
| F-2 | observation | closed (over-broad supersessions withdrawn); successor observation O-7 |
| F-3 | SOURCE-FACTOR RED | closed |
| F-4 | SOURCE-FACTOR RED | closed |
| F-5 | SOURCE-FACTOR RED | closed (factor removed) |
| F-6 | SOURCE-FACTOR RED | closed |
| F-7 | SOURCE-FACTOR RED | closed (both components now carry a factor whose non-fall-through tiers are conjunctions over loyalty and booking records) |
| F-8 | SOURCE-FACTOR RED | per task (see task files) |
| O-2, O-3, O-4 | observation | closed |
| O-5, O-6 | observation | unchanged |
| O-7 | — | new observation (reason codes reused on parking lines) |
| O-8 | — | new observation (same-night tie in `recent_service_rate`) |
| **N-1** | — | **new SOURCE-FACTOR RED** (`maximum_method` T2 ≡ fall-through) — bears on task 1 |

### closing_checklist (revision_2)

Written after the round-2 reveal (2026-10-05T16:30:45Z). The revision_2 charter-global section above was hashed at reveal (`9bc33188…5c5b` for the whole file at that moment) and is unchanged.

**The difficulty does not close in revision_2.**

| item | status |
| --- | --- |
| Per-task files one-to-one; revision_2 appended under each; round-1 text untouched | yes |
| Every comparison section carries a PASS | **no** — task 0 PASS on all four; task 1 factors SOURCE-FACTOR RED (N-1) |
| Policies covered; scopes disjoint and complete | yes (charter_scope of both tasks) |
| Tools/GT closed; uuid8s | yes (tool module unchanged) |
| Trees: 1–3 prerequisites, value_input floor, owner=user problem, acyclic | yes for both |
| Factors: bounds, multi-source, cross-difficulty, distinct-outcome ladders, weight, honest baselines, baseline ≠ gold | **no** — weekly cap's `maximum_method` T2 ≡ fall-through (N-1). Everything else passes, including weight and baselines for all 23 factors |
| Gates on final form | fresh snapshot supplied by the orchestrator (all seven OK); not re-run by the auditor; hashes match the snapshot |

Round-1 RED closure:
- **Closed:** F-3, F-4, F-5, F-6, F-7, F-8 and T0-F1.
- **Closed observations:** F-1, F-2, O-2, O-3, O-4, the tonight's-parking observation, and the T0 desk-limit wording.
- **New:** N-1 (SOURCE-FACTOR RED, task 1); O-7, O-8 (observations).

Per-task verdicts (revision_2):
- Task 0: PASS on all four relationships.
- Task 1: policy PASS; tree PASS; **factors SOURCE-FACTOR RED (N-1)**; unique solution PASS.

## revision_3

### charter_global_frozen (revision_3)

- Written 2026-10-05T17:43Z onward, before any round-3 GT read. Earlier revisions are untouched.
- Inputs:
  - `folio.extended.yaml` `974c8e5d4808216234b7ac95f3e51a4c06efc1ffbfb72274c2d28ac695aa0681` — changed from revision_2 (`65262123…`).
  - `task_tools.py` `a5ad1bad…c68c` — unchanged; the tool-module conclusions carry forward on that hash.
  - Views unchanged: task_0 `11d7593e…`, task_1 `f975a262…`.
- Gate snapshot: all seven OK. Base section still verbatim (parsed equality).
- Scope of the change, established from the charter itself:
  - `folio_ext_breakfast_credit`, `folio_ext_dining_allowance_carryover`, `folio_ext_self_parking_savings` and `folio_ext_valet_parking_savings` occupy the same line ranges as in revision_2 (1178, 1340, 1547, 1727) with identical params, factor sets/labels/tier counts and overwrite counts. Their revision_2 conclusions are carried forward.
  - The change is confined to `folio_ext_weekly_parking_cap` (starting at 1902), which was re-read in full.

### re-derived for folio_ext_weekly_parking_cap

- **Rule/compute equivalence.**
  - Every `compute_basis` quote and every `baseline.rule` sentence is verbatim in the rule (machine check).
  - New sentence "When the most recent night parked carries both a self-parking and a valet line, the service of that night is valet." It grounds `recent_service_rate`'s `latest_valet_day >= latest_self_day` tie-break and also appears in `baseline.rule`. **O-8 closed.**
  - `method_maximum` T2 is now `weekly_rate * full_weeks + MN(basis_rate * remaining_nights, weekly_rate / 2)` ⇔ "the remaining nights together never charged more than half the weekly rate". The ladder text matches ("capped at half the weekly rate").
- **Prerequisite edges and sentences:** unchanged and verbatim; PASS.
- **Override declarations:** unchanged (one overwrite on the incidental parking sentence). O-7 unchanged.
- **Factors.**
  - **N-1 closed.** For Gold/Platinum the weekly rate is basis × 6, so the cap `weekly_rate / 2` = basis × 3 binds whenever 4–6 nights remain beyond full weeks. Machine check over 9 basis rates × 5 full-week counts × 7 remainders: T2 ≠ fall-through in 135 of 315 cases (every case with ≥ 4 remaining nights). T2 also differs from T1 (pro-rating), so the ladder now has three distinct outcomes.
  - The cap is a structural change to the algorithm (a bounded remainder term), so the `method` label is honest. A cap of half a week on the remainder is a plausible weekly-rate practice.
  - Other weekly factors unchanged: basis rate (parameter), chargeable nights (parameter), discount (parameter). Counts: 4 factors (3 parameter, 1 method); bindings disjoint; fall-throughs equal the baselines; baseline rule self-sufficient.

### findings (revision_3)

| id | revision_3 status |
| --- | --- |
| N-1 | closed |
| O-8 | closed |
| O-7 | unchanged (observation) |
| O-5, O-6 | unchanged |
| new defects | none found |

### closing_checklist (revision_3)

Written after the round-3 reveal (2026-10-05T23:32:49Z). The revision_3 charter-global section was hashed at reveal (`36f2b6ee…9cfd`) and is unchanged.

**The difficulty closes at the source layer.**

| item | status |
| --- | --- |
| Per-task files one-to-one; revisions appended, older text untouched | yes |
| Every comparison section carries a PASS | yes — task 0 and task 1 PASS on all four relationships |
| Policies covered; scopes pairwise disjoint and jointly complete | yes |
| Tools/GT closed; uuid8s independent and frozen | yes (tool module unchanged since round 1) |
| Trees: 1–3 prerequisites, ≥ max(n−1,1) value_input, ≥1 owner=user problem, acyclic; difficulty graph acyclic | yes |
| Factors: 4–6 per computation with ≥2 parameter and ≥1 method; per task ≥1 multi-source and ≥1 cross-difficulty; ladders ≥3 distinct tiers stated in the rule; every factor bears weight against an honest baseline; each baseline definite and ≠ gold | yes |
| Gates on the final form | fresh orchestrator snapshot, all seven OK; artifact hashes match it; not re-run by the auditor (Step 0) |

Outstanding observations (no RED): O-5, O-6, O-7, T0-O1, T1-O1, and the round-1 borderline/hybrid label notes on `per_person_breakfast_credit`, `tier_parking_benefit` and `valet_saving_method`.
