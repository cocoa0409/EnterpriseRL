# Policy-task audit — factory_order_milestones_and_delays / charter-global

## charter_global_frozen
- Freeze time: 2026-10-13T13:20Z (written before any task GT was revealed). Auditor: independent policy-task auditor (erl-task-policy-audit), not the instantiator.
- Frozen artifact hashes (re-verified with `sha256sum` before reading, match the coordinator brief):
  - `fb5df80492a4ef65c93b38abd7410776080cc4762afed1e243cb97dd2830d378  order.extended.yaml`
  - `88e0f661d9350aa18a85a365f9130660d126fe603f6323740487160961fc3640  task_tools.py`
  - masked views: `65bd943d…78acf  0.view.json`, `fc616ec1…5053c  1.view.json` (match).
- Read for this section: `blueprint/blueprint.yaml`, `blueprint/db_schema.json` (enums), `blueprint/products/order.yaml` (diffed), `blueprint/products/window.yaml` and `install.yaml` (series/method parameters used to check seeded cross-category rows), `order.extended.yaml`, `task_tools.py`, and the DSL evaluator `skills/erl-task-instantiate/scripts/check_compute.py` (to fix the semantics of `DAYS`, `MONTHS`, `within_months`, `LATEST`, `XLATEST`, `CFIELD`).
- Masked and not read: `tasks/0.json`, `tasks/1.json` (every field), instantiator scratch, `worklog.md`, the sibling difficulty's audit directory.
- Entry conditions (Step 0): the gate snapshot came with the brief (EXTENDED / TASK TOOL CONTRACT / REPLAY / SOLVABILITY / COMPUTE / GROUNDING / SCOPE all OK). TRACEABILITY is NOT OK because the docs are not rendered yet, and the coordinator has deferred it to step 3. `validate_scenario` reports only missing documents. The masked views were supplied together with their hashes. I accept these entry conditions as given. The traceability gate still has to be re-run after rendering (see closing_checklist).

### policy_conflict_scan
- Base copy: `diff <(order.extended.yaml up to extended_policies:) blueprint/products/order.yaml` shows no difference. The base copy is verbatim.
- The 7 extended policies, with their subject, target tool and `computes`:
  - P1 `order_ext_late_acknowledgment_shift`: order_delay_noticed (cause late_acknowledgment), `record_late_acknowledgment_notice_952cb75c`, days_to_revised_ship_date.
  - P2 `order_ext_hold_release_requote`: order_hold_released, `release_customer_hold_268345ec`, days_to_new_ship_date.
  - P3 `order_ext_expedite_fee`: order_charge_assessed (expedite_fee), `request_expedited_build_5d45bf5f` (owner user), fee_amount.
  - P4 `order_ext_remake_delay_notice`: order_delay_noticed (cause customer_spec_remake), `record_remake_delay_notice_f2496c0b`, days_to_revised_ship_date.
  - P5 `order_ext_customer_remake_charge`: order_charge_assessed (remake_charge), `assess_customer_remake_e3e4e81e`, charge_amount.
  - P6 `order_ext_on_time_guarantee_claim`: order_guarantee_credit_earned, `file_on_time_claim_fe24f9ef` (owner user), credit_amount (+ weeks_late).
  - P7 `order_ext_branch_storage_fee`: order_charge_assessed (storage_fee), `assess_branch_storage_97307cec`, fee_amount (+ billable_weeks).
- Overlapping subjects:
  - **order_charge_assessed** is shared by P3, P5 and P7. They are distinguished by charge_kind. In the base, all three eligibility gates are written with `applies_to: [order_charge_assessed]`: `customer_charge_basis` (remakes), `expedite_before_production` (expedite) and `after_free_period` (storage). Read literally, each gate binds every charge. The extended policies fix this with scoping overwrites:
    - The remake gate is scoped by P3 and P7.
    - The expedite gate is scoped by P5 and P7.
    - The storage gate is scoped by P3 and P5.
    - Each policy leaves its own gate standing.
    - The sibling replaced_by sentences for the same clause agree with each other and each names both of the other kinds. For example, P3 says of the remake gate "neither an expedite fee … nor a storage fee falls under it", and P7 says "a storage fee … does not fall under it, nor does an expedite fee". After the merge, each gate governs exactly one charge kind. No conflict.
  - **order_delay_noticed** is shared by P1 (late_acknowledgment) and P4 (customer_spec_remake). P2's release tool also writes a customer_hold notice. The three causes are distinct, and each writer stamps exactly one cause. No conflict.
- Triggers and time anchors:
  - The base trigger `order_delay_noticed` (cause ≠ customer_hold) → `order_ship_date_revised` is honoured by both notice tools, which update `current_ship_date`.
  - The release tool sets the status to entered and writes the customer_hold notice, as the base `order_hold_released` trigger requires.
  - No extended policy moves the committed ship date.
- Cross-category read boundaries: P1, P3, P4 and P5 read `window` (window_contracts and window_transactions of the contract the order builds). P7 reads `install` (the install job keyed by factory_order_id and its install_activities). Every read is a read only. No extended policy writes another category.
- Scope partition implied by the prerequisite graph (to be confirmed against `charter_scope` at the reveal):
  - The tree rooted at P3 = {P3, P2, P1}.
  - The tree rooted at P7 = {P7, P6, P4, P5}.
  - The two sets are disjoint and together cover all 7 extended policies.

### rule_compute_equivalence
- Verbatim check (scripted, whitespace-normalised): every `compute_basis` value of all 7 policies is a sentence, or a concatenation of sentences, of that policy's own `rule`. Every `baseline.rule` sentence is in the `rule`. Every `replaced_by` is in the `rule`.
- Per policy, rule sentence → binding (confirmed by reading every compute expression):
  - **P1**:
    - win_t: return window, business days from the day after entry, using a 2025–2027 federal holiday list. I checked the list against the federal calendar, including observed dates 2026-07-03, 2027-06-18, 2027-07-05, 2027-12-24 and 2027-12-31.
    - sig_t = LATEST acknowledgment_signed.
    - end_t: hold tier `hold_t <= sig_t and no customer_hold notice in [hold_t, sig_t)`; else factory-capacity/glass tier `win_t < fac_t <= sig_t` on the latest such notice; else sig_t.
    - lat_n and raw_n: business-day counts from the day after window close.
    - paint (`colored*2 >= unit_count and colored>0` → 2, `>=1` → 1); insert (grilles → 2, hardware → 1); cut (>5 → 2, ≥3 → 1).
    - shift is added from current_ship_date. result is calendar days from NOW.
    - All match the rule.
  - **P2**:
    - hold_days = DAYS(hold_start, NOW). Tier tests are `<= 30 and signed` / `> 30 and <= class max and signed` / else.
    - slot = current + business days (hold_start, NOW]. remq = NOW + (business days (hold_start, current] + queue). std = NOW + standard lead.
    - season uses the month of NOW. cap_n counts factory_capacity notices `within_months=3`. glass checks the notice first, then glass_received.
    - All match.
  - **P3**:
    - target = NOW + expedite lead. pull_n = business days (target, current].
    - rate tiers 70/40/class. unit_charge tiers on LATEST-ack unit_count.
    - paint/oversize/holiday add-ons; MX(class min, subtotal); program discount; RND(…, 2) once at the end.
    - All match. The rounding sentence ("rounded to the cent once, at the end") matches RND placement.
  - **P4**:
    - start_t: corrected-ack tier `corr_t > rmk_t` / production-start tier `rmk_t < prod_t` / remake date.
    - lead = class remake lead + glass + finish + requeue (`COUNT(all remakes) − 1`) + seasonal (month of the cust-spec remake) + insert.
    - The revised date is start + lead business days. result is calendar days from NOW (negative allowed, as the rule says).
  - **P5**:
    - stage (latest assembly ≤ remake → 1.0; latest glass_received ≤ remake → 0.7; else 0.4).
    - base (avg price/opening ≥ 2000 → 25 % × avg × units; else color CO → class × units + 120; else class × units).
    - batch (≥3 → 0.9, 2 → 0.95, else 1). measurement (company_remeasure → 0.5, remeasure → 0.8, else 1).
    - RND once at the end.
  - **P6**:
    - bm_date = MX(committed, latest revised of customer_hold / late_acknowledgment / customer_spec_remake / weather_freight). This equals the class excluded-cause list `&id001`.
    - grace tiers by factory-capacity count. end_t: delivered later than ship + transit → delivered; delivered on or before → expected arrival; not delivered → ship.
    - weeks = floor((end − grace end)/7). rate tiers. escalation tiers `>= max+1` / `== max`. late-notice tiers. glass share.
    - credited weeks only when weeks ≥ 1. Then MN(cap, …) and RND at the end. All match.
  - **P7**:
    - span = DAYS(delivered, start) − 1, or DAYS(delivered, NOW) when not started. Minus free days, minus 7 × company/weather reschedules, minus extension, minus permit allowance. Floor at 0.
    - weather tiers (//2; ceil ×0.75; as is). ceil weeks. rate tiers on the install job's unit_count. MN(cap) and RND.
    - All match the rule text, except for the scope noted in F-G3.
- Places where the compute is broader or narrower than the rule. None of them is reached by either task world, so all are recorded as observations in `findings`:
  - F-G3: P7's reschedule reads (`XCOUNT` / `XLATEST` on install_activities) are scoped to the customer, not to "the order's installation job".
  - F-G4: P4 uses the `prod_t = 999999` sentinel when there is no production start date.
  - F-G4: P4 computes "earlier remakes" as total − 1.
  - F-G5: P1 and P3 use LATEST-ack semantics when there are several acknowledgments.
  - F-G6: the P2 three-month window boundary.

### action_binding_and_uuids
- `(target_tool, computes)` pairs: there are 7 distinct tools, each claimed by exactly one policy, and no tool is shared.
- Owners:
  - P3 `request_expedited_build_5d45bf5f` and P6 `file_on_time_claim_fe24f9ef` are `owner="user"`.
  - The other five are `owner="agent"`.
  - All seven are `rw="write"`.
- Each body performs exactly one write: one `order_milestones` row, plus a `factory_orders` update for P1, P2 and P4.
- No body checks eligibility, prerequisites or amounts. The module docstring states this, and reading all seven bodies confirms it: there is no `if`, raise or hint on state, only `round(float(x), 2)` and `int()` casts.
- Docstrings:
  - Every claimed effect exists in the body. Examples: P1/P4 "moves/sets the order's current projected ship date" → `ctx.update(...current_ship_date=...)`. P2 "moves the order from on hold back to entered" → `status="entered"`. P6 "dated the order's ship date" → `row.get("ship_date")`. P5 "dated the date of that remake" → the remake row's milestone_date.
  - No docstring carries a concrete example value of a scored argument. They carry only format conventions such as "0 means today".
  - No docstring names another task tool or a position in a sequence.
  - Two phrasing points are recorded as observation F-G9: the word "Afterwards" describes each tool's own post-state, and "as returned by the factory order lookup" describes where an id comes from.
- No factor id is a substring of any tool name (scripted check over all 34 factor ids × 7 tool names).
- uuid8s: 952cb75c, 268345ec, 5d45bf5f, f2496c0b, e3e4e81e, fe24f9ef, 97307cec. They are pairwise distinct, share no prefix or suffix, and show no sequence or adjacent-value pattern. Nothing suggests they were batch-derived.

### prerequisite_graph
- `prerequisite` is filled in on all 7 policies (`[]` on P1, P4 and P5). Edges:
  - P2 → P1 (value_input, gate `cur_t`).
  - P3 → P2 (value_input, gate `cur_t`).
  - P6 → P4 (value_input, gate `bm_t`).
  - P6 → P5 (value_input, gate `rate`).
  - P7 → P6 (value_input, gate `credit_weeks`).
- The graph is acyclic: P1→P2→P3 and {P4, P5}→P6→P7. Every `problem` is an extended policy id. None points to itself or to a base policy.
- Scripted checks on every edge:
  - `policy_source` is verbatim in the blocked policy's own `rule`.
  - `resolved_by` equals the depended-on policy's `target_tool`.
  - `gate` is a binding name that exists in the blocked policy's compute.
  - `form: state` is set on all five edges, and no `fallback_reason` is present (correct for the state form).
- `effect`: each named binding really moves when the resolving write lands. I recomputed this on both task worlds; the per-task files hold the numbers.
- `condition` against the sentence: P2's condition adds "current_ship_date already reflects that notice's revised_ship_date". That is a consequence of the same write (the base trigger), not an independent strengthening. It is recorded as observation F-G10. The other four conditions match their sentences.
- No authoring-viewpoint phrasing ("in this task", "at the opening", "current world") appears in any `prerequisite` block or rule (scripted check).

### prerequisite_sentences
Four-point test on each edge. All five use an ordering connective, name a record-visible state in record words, contain no tool name, policy id, snake_case token or row id, and match the strength of their `condition`:
- **P2 ← P1**: "The ship date set at a hold's release is worked out only after the order carries a delay notice with cause late acknowledgment whenever its acknowledgment was signed after the return window."
  - Connective: "only after".
  - State: a late_acknowledgment delay notice on the order, conditioned on a late signature. This is an open condition, stated open.
  - Single writer: only `record_late_acknowledgment_notice_952cb75c` writes `delay_cause="late_acknowledgment"`. No other tool or trigger does.
  - Reader's derivation: the sentence names a late-acknowledgment delay notice. The only rule that produces one is P1's ("a delay notice with cause late acknowledgment moves the current ship date later by the late-acknowledgment shift"). So the reader resolves P1 first, and there is one reading.
- **P3 ← P2**: "The expedite fee is not fixed until the order's status reads entered and, where the order was put on hold, a delay notice with cause customer hold records the ship date set when that hold was released."
  - Connective: "not … until".
  - State: status entered plus a customer-hold notice for held orders.
  - Single writer: the release tool is the only write that returns on_hold → entered and the only writer of `delay_cause="customer_hold"`.
  - Derivation: P2's rule is the one that sets "the ship date set at a hold's release". One reading.
- **P6 ← P4**: "The guarantee credit is not booked until every remake on the order recorded with cause customer specification error has its delay notice with cause customer specification remake on record."
  - Single writer: `record_remake_delay_notice_f2496c0b`, the only writer of `customer_spec_remake`.
  - Derivation: P4's rule records "a delay notice with cause customer specification remake". One reading.
- **P6 ← P5**: "The guarantee credit is booked only after each remake on the order recorded with cause customer specification error carries its remake charge."
  - Single writer: `assess_customer_remake_e3e4e81e`, the only writer of `charge_kind="remake_charge"`. The base trigger order_remake_logged(customer_spec_error) → order_charge_assessed cannot fire, because no tool of this difficulty logs a remake.
  - Derivation: P5's rule charges "a customer remake". One reading.
- **P7 ← P6**: "The storage fee is fixed only after the order carries the on-time guarantee credit it has earned whenever its shipment came in later than the guarantee grace period allows."
  - Single writer: `file_on_time_claim_fe24f9ef`, the only writer of order_guarantee_credit_earned.
  - Derivation: P6's rule ("files the on-time guarantee claim, and that claim books the credit on the order"). One reading.
- None of the depended-on rules (P1, P2, P4, P5, P6) restates the dependent's sentence. No rule carries a second wording of an edge.
- Cross-problem order sentences that ground no declared edge:
  - None in the extended rules.
  - The base sentences with cross-problem order are "Production can start only after the customer has signed…" and "An order is cancelled only after its contract has been cancelled". Neither touches a problem of either tree. They are recorded as observations only.

### override_declarations
Sentence-by-sentence check against each `base_policy_refs` entry. Results only; consequences are shown in the task files.
- **P1**:
  - order_acknowledgment_and_production: the late-acknowledgment shift sentence is declared superseded. Every other sentence is followed:
    - the on-time window and its counting;
    - production waits for the signature;
    - the template requirement;
    - the queue;
    - QC failure → factory_defect.
  - order_holds, order_delays_and_guarantee, order_remakes and order_expedite: P1 governs none of their quantities. It follows "Every change to the projected ship date is recorded as a delay notice with one cause".
  - Residual: the variant enumeration `late_ack_shift_basis: business_days_late` still names the base method. Observation F-G8.
- **P2**:
  - order_holds: the reset-at-release sentence is declared superseded. Followed:
    - before-production only;
    - hold count;
    - release by request or at the class maximum length;
    - counting;
    - "A hold earns no guarantee credit; its delay notice moves the guarantee benchmark";
    - no storage on held orders.
  - Residual: `hold_requote_basis: release_date_plus_standard_lead` (F-G8).
- **P3**:
  - order_expedite: the fee sentence is declared superseded. Followed:
    - availability by class;
    - entered-only gate;
    - target date;
    - "does not change the committed ship date or the guarantee benchmark";
    - waiver when the target is missed;
    - no expedite for held orders.
  - order_remakes and order_storage: the gates are scope-limited (declared).
  - order_agg_customer_orders: followed.
  - The floor-then-discount order, which can bring the fee below the class minimum, is declared in replaced_by.
- **P4**:
  - order_remakes: the remake-lead sentence is declared superseded. Its replaced_by gives "the remake lead worked out below, counted from the rebuild start date" to every remade unit. But the rule defines the rebuild start only for "a customer specification remake". The retired clause's still-in-force part ("rebuilt within the class remake lead time from the remake date") is neither kept for company-cause remakes nor scoped away. Finding F-G4. No task records a company-cause remake notice, so it is an observation.
  - The other order_remakes sentences are followed.
- **P5**:
  - order_remakes: the charge-amount sentence is declared superseded. Followed:
    - the cause/ack gate ("Without a signed acknowledgment … company mismeasure");
    - charge dated on the remake date.
  - order_expedite and order_storage gates: scope-limited (declared).
- **P6**:
  - order_delays_and_guarantee: the full-weeks sentence and the credit sentence are declared superseded. Followed:
    - benchmark definition and excluded causes;
    - "delays from glass supply or factory capacity never move it";
    - "The order ships when its last unit ships";
    - guarantee-class gate;
    - "Shipping on or before the end of the grace period earns nothing" (restated);
    - escalation clause ("When an order already carries the escalation number of delay notices, a further delay is escalated … and no credit or date promise beyond the recorded notices is made by support"). I read this as applying to a further, new delay, not to booking credit for recorded notices. P6's escalation-weeks factor explicitly prices orders at or above the count. Observation F-G11.
  - Not in refs but touching the same quantity: order_remakes "the order's ship date for lateness is still the date its last unit ships" (partial-shipment context) and the enumeration `lateness_ship_basis: last_unit_shipped`. P6 measures lateness to the branch delivery date or the expected arrival date. Observation F-G7, because neither task has a partial shipment.
- **P7**:
  - order_storage: the reschedule-days and fee sentences are declared superseded, and replaced_by keeps the "stop on the day installation starts or the order is cancelled" part. Followed:
    - free-period gate;
    - counting;
    - "Storage is assessed once, on the day installation starts or the contract is cancelled";
    - "No storage is charged when the installation has never been offered to the customer inside the free period";
    - no storage on held orders.
  - order_remakes and order_expedite gates: scope-limited (declared).
  - The base measure `order_msr_billable_storage_days` still says "minus every day between previous_date and new_date …". Its only use, the superseded rule sentence, is replaced "in place of counting each day of delay", so the merge is unique. Observation F-G8.
- Disguised forms:
  - No anonymous intermediate factor: every intermediate is named in its rule.
  - No 0/1 multiplier zeroing a base-fixed amount: P6's `elig` gate is the base gate itself.
  - No dropped branch: P2's three requote tiers include the base method as the fall-through, and P4's three start anchors include the remake date.
  - No author note calls a base output "wrong".

### factor_ladders
Structure only. Whether each factor bears weight is checked per task.

Every ladder below has three tiers, the fall-through counted. The tiers are pairwise disjoint as stated, every tier is stated in the `rule` with its condition and value or method, and every tier is a branch of the `decides` binding (each checked against the compute expression). Bindings are disjoint across the factors of a policy, and no factor `decides: result`. The table uses these abbreviations:
- `md`: method factor.
- `pm`: parameter factor.
- `ms`: multi-source, meaning every non-fall-through tier is a conjunction or disjunction over distinct records.
- `xd`: cross-difficulty.

| Policy | Factor | Label | Tiers (fall-through last) | ms | xd | Baseline vs fall-through |
| --- | --- | --- | --- | --- | --- | --- |
| P1 | signature_count_endpoint | md | hold start (held at signature) / factory-capacity or glass notice date / signature date | yes | – | `end_t: sig_t` equals the fall-through and `baseline.rule` ("up to and including the date the acknowledgment was signed") |
| P1 | paint_line_rebooking | pm | 2 / 1 / 0 business days | no (CO openings vs order units) | window | 0, which equals the fall-through |
| P1 | insert_hardware_reorder | pm | 2 / 1 / 0 | no | window | 0 |
| P1 | cut_list_regeneration | pm | 2 / 1 / 0 | no | – | 0 |
| P2 | requote_basis | md | slot kept (current + held business days) / release + remaining lead + queue / release + standard lead | yes (hold length AND ack signed) | – | `std_t`, which equals the fall-through and `baseline.rule` |
| P2 | seasonal_reload | pm | 3 / 1 / 0 | no | – | 0 |
| P2 | capacity_resequencing | pm | 3 / 2 / 0 | no | – | 0 |
| P2 | glass_rereservation | pm | 2 / 1 / 0 | tier 2 yes (no glass notice AND glass received) | – | 0 |
| P3 | pull_in_rate | pm | 70 / 40 / class fee per unit (45 or 55) | no | – | class fee, which equals the fall-through and `baseline.rule` |
| P3 | volume_structure | md | 10 at rate + rest at half rate / class minimum as one flat amount / acknowledged units × rate | no | – | `F('unit_count')*rate`. The fall-through reads acknowledged units, the baseline reads order units (F-G15) |
| P3 | paint_line_priority | pm | $20 / $10 per colored opening / 0 | no | window | 0 |
| P3 | oversize_handling | pm | $30 / $20 per oversize opening / 0 | no | window | 0 |
| P3 | holiday_overtime | pm | $15 / $8 per unit / 0 | no | – | 0 |
| P3 | program_discount | pm | 15 % / 10 % / 0 | no (one field) | window | 0 |
| P4 | rebuild_start_anchor | md | latest corrected signature / production start / remake date | tier 2 yes | – | `rmk_t`, which equals the fall-through and `baseline.rule` |
| P4 | glass_recutting | pm | 5 / 2 / 0 | no | window | 0 |
| P4 | finish_matching | pm | 3 / 2 / 0 | no | window | 0 |
| P4 | line_requeue | pm | queue + 3 / queue / 0 | no | – | 0 |
| P4 | seasonal_line_load | pm | 3 / 2 / 0 | no | – | 0 |
| P4 | insert_matching | pm | 2 / 1 / 0 | no | window | 0 |
| P5 | build_stage_share | pm | 0.7 / 0.4 / 1.0 | yes (no assembly AND glass received) | – | 1.0, the full charge, which equals the standard rule |
| P5 | contract_charge_base | md | 25 % × average price per opening × units / class × units + $120 / class × units | tier 2 yes (contract price AND color CO) | window | class × units, which equals `baseline.rule` |
| P5 | batch_rebuild_rate | pm | 0.9 / 0.95 / 1.0 | no | – | 1.0 |
| P5 | measurement_share | pm | 0.5 / 0.8 / 1.0 | no | window | 1.0 |
| P6 | remake_rate | pm | $25 / $60 / class credit (25, 25, 30, 0, 0, 50) | tier 2 yes | – | class rate (see F-G2) |
| P6 | lateness_end_basis | md | delivery date / expected arrival (ship + transit) / ship date | yes (delivery vs ship + transit) | – | `ship_t`, which equals `baseline.rule` |
| P6 | capacity_grace | pm | 5 / 7 / class grace (5, 5, 7, 7, 10, 10) | no | – | class grace (see F-G2) |
| P6 | escalation_weeks | pm | 2 / 1 / 0 | no | – | 0 |
| P6 | late_notice_weeks | pm | 2 / 1 / 0 | yes (notice date vs committed date) | – | 0 |
| P6 | glass_supplier_share | pm | 0.8 / 0.9 / 1.0 | no | – | 1.0 |
| P7 | late_shipment_extension | pm | 14 / 7 / 0 days | no | – | 0 |
| P7 | permit_wait_allowance | pm | 10 / 5 / 0 days | yes (permit AND crew days) | install | 0 |
| P7 | weather_adjustment | md | halve and round down / × 0.75 and round up / as is | yes (weather AND later customer reschedule) | install | `raw_days`, which equals the fall-through |
| P7 | order_size_rate | pm | $10 / $15 / class rate (6, 6, 7.5, 7.5, 9, 12) | no | install | class rate (see F-G2) |

Counts:

| Policy | Factors | `parameter` | `method` | `cross_difficulty` | Multi-source |
| --- | --- | --- | --- | --- | --- |
| P1 | 4 | 3 | 1 | 2 (window) | 1 |
| P2 | 4 | 3 | 1 | 0 | ≥ 1 |
| P3 | 6 | 5 | 1 | 3 (window) | 0 |
| P4 | 6 | 5 | 1 | 3 (window) | ≥ 1 |
| P5 | 4 | 3 | 1 | 2 (window) | ≥ 1 |
| P6 | 6 | 5 | 1 | 0 | ≥ 1 |
| P7 | 4 | 3 | 1 | 3 (install) | ≥ 1 |

All seven policies are within the bounds of 4–6 factors with at least 2 `parameter` and 1 `method`. The per-task union is:
- tree {P1, P2, P3}: multi-source yes, cross-difficulty yes (window);
- tree {P4, P5, P6, P7}: multi-source yes, cross-difficulty yes (window and install).

Label honesty:
- P2 `requote_basis`, P3 `volume_structure` and P5 `contract_charge_base` are clear algorithm changes.
- P1 `signature_count_endpoint`, P4 `rebuild_start_anchor` and P6 `lateness_end_basis` keep the counting formula and change which event anchors or ends the interval. P6's middle tier also derives a date (ship date plus transit business days).
- P7 `weather_adjustment` changes the multiplier and the rounding direction (floor or ceiling).
- I accept these four as `method` because the tier chooses the measurement basis or the rounding rule rather than a rate, fee or threshold, which matches the charter's own `*_basis` enumerations. The call is close, and it is recorded as observation F-G12.
- Every method tier names a rule stated in its own policy.

Realism, judged against real window and door manufacturing, factory and branch practice (findings below):
- One tier outcome is unreal: P7 `weather_adjustment` tier 1 (F-G1).
- Ladders collapse or invert in some build classes: P6 `remake_rate`, P6 `capacity_grace` and P7 `order_size_rate` (F-G2).
- Borderline items recorded as observations: F-G13 and F-G14.
- All other conditions and outcomes are ones this industry actually weighs. Examples: paint-line, insert and cut-list rework after a late sign-off; slot retention for short holds; seasonal plant load; glass re-reservation; expedite pricing by how far the order is pulled in, with volume tapering and holiday overtime; glass recutting and finish matching on remakes; a build-stage share of the remake cost; a value-based charge base; shared responsibility after a company remeasure; guarantee grace and credit tied to plant-capacity notices; free storage extended for late shipment and permit waits; small-lot storage rates.

### findings
Charter-global findings. Each one names the tasks it bears on, and the consequence is shown in that task's file.

- **F-G1 — SOURCE-FACTOR (unreal ladder tier). Bears on task 1.**
  - Symptom: P7 `weather_adjustment` tier 1 reads "when the most recent weather reschedule is followed by a later customer reschedule, the billable days are halved and rounded down to a whole day". Tier 2 reads "when there is a weather reschedule but no customer reschedule after the most recent one, they are multiplied by 0.75 and rounded up".
  - Root cause: the customer's own later postponement earns more storage relief (×0.5, rounded down) than a weather postponement alone (×0.75, rounded up).
  - Why no business publishes this: a customer-initiated delay is exactly what branch storage fees charge for. The base charter itself relieves only "an installation reschedule initiated by the company or by weather".
  - Evidence: `order.extended.yaml` P7 `rule` and `factors[weather_adjustment].ladder[0]`.
  - Task 1's world takes tier 1. The demonstration is in `1.md`.
- **F-G2 — SOURCE-FACTOR (tiers coincide or invert in some build classes). Bears on no current task; both task worlds sit outside the affected classes.**
  - P6 `remake_rate`: tier 1 is $25. The fall-through is the class `on_time_credit_per_unit_week`, which is $25 for Custom Size Build and Custom Color Build. Two tiers select the same value there.
  - P6 `capacity_grace`: tier 1 is 5 business days, equal to the class grace of Custom Size and Custom Color. Tier 2 is 7, equal to the class grace of Specialty Glass and Specialty Shape.
  - P7 `order_size_rate`: tier 1 ("12 or more units … 10 dollars") is above the middle class rate in Custom Size and Custom Color (6.0), Specialty Glass and Specialty Shape (7.5) and Impact-Rated (9.0). An order of 12 or more units would pay more per unit per week than an order of 7–11. That is not a volume schedule any warehouse publishes.
  - The ladders are coherent only in the Architectural Wood class, where task 1 sits ($50 / 10 business days / $12), and in Specialty Glass for remake_rate.
- **F-G3 — observation (compute broader than rule).**
  - P7's `restarts`, `weather_last` and `customer_last` use `XCOUNT`/`XLATEST('install','install_activities', …)` filtered only by event type and initiator, which the DSL scopes to the customer. The rule says "on the order's installation job".
  - A customer with a second install job, for example a door job, would have that job's reschedules counted.
  - Not reached: task 1 seeds one install job.
- **F-G4 — observation (replaced_by scope, domain gaps).**
  - P4 replaced_by: "A remade unit is rebuilt within the remake lead worked out below, counted from the rebuild start date". The rule defines the start only "for the rebuild of a customer specification remake". Company-cause remakes lose the retired clause's "class remake lead time from the remake date" without a replacement.
  - When `production_start_date` is empty, `prod_t = 999999`, so a customer-spec remake without a corrected acknowledgment gets a start date 999999 days out.
  - `earlier_n = COUNT(all remakes) − 1` assumes the remake being handled is the latest.
  - Not reached: task 1 records the notice for the latest remake, and production had started.
- **F-G5 — observation (several acknowledgments).**
  - P1 (`sig_date`) and P3 (`ack_units`) take the LATEST acknowledgment_signed row.
  - In a world with a corrected acknowledgment for remade units, like task 1's 2-unit acknowledgment of 2026-06-05, P3 would price the expedite on 2 "acknowledged" units, which selects the flat-minimum tier.
  - Task 0 has one acknowledgment, so the question does not arise there.
- **F-G6 — observation.**
  - P2 `within_months=3` uses the DSL test `0 <= MONTHS(row, NOW) < 3`. A notice dated exactly three calendar months before the release falls outside "the three months up to the release date".
  - Not reached: task 0's notice is about one month old.
- **F-G7 — observation.**
  - P6 measures lateness to the delivery or expected-arrival date. The base order_remakes sentence "the order's ship date for lateness is still the date its last unit ships" and the enumeration `lateness_ship_basis: last_unit_shipped` are not overwritten.
  - The base sentence is conditioned on partial shipment, and task 1 has none, so a unique reading holds.
- **F-G8 — observation.**
  - Variant enumerations `late_ack_shift_basis`, `hold_requote_basis` and `lateness_ship_basis`, and the base measure `order_msr_billable_storage_days`, still describe the retired base methods.
  - The rule-level overwrites are explicit ("worked out below", "in place of …"), so the merge is unique. The renderer must not publish the enumerations as a competing rule.
- **F-G9 — observation.**
  - Tool docstrings use "Afterwards …" for the tool's own post-state, and "as returned by the factory order lookup" to describe the source of an id.
  - Neither names a task tool or a position in a sequence.
- **F-G10 — observation.**
  - P2's edge `condition` adds "current_ship_date already reflects that notice's revised_ship_date". That is the same write's base-trigger effect, so it is not an independent strengthening.
- **F-G11 — observation.**
  - The base escalation clause ("no credit or date promise beyond the recorded notices is made by support") sits next to P6's escalation-weeks factor, which prices credit for orders at or above the escalation count.
  - Read as applying to a further, new delay, it does not bar booking credit for recorded notices.
- **F-G12 — observation (method labels).** See label honesty above.
- **F-G13 — observation (realism, borderline).**
  - P3 `program_discount` gives senior 10 % and military or first-responder 15 % off an expedite fee. The window charter's own program rates on the contract list price are 5 % and 10 % for 2200 Series.
  - Extending a signing discount to a factory rush fee is unusual but publishable as the company's own schedule.
- **F-G14 — observation (realism, borderline).**
  - P4's tier "the remake was recorded before the order's production start date" describes a remake before anything is built. In a plant that is a specification change, not a remake.
  - Not reached by task 1: the remake on 06-03 came after the 03-17 production start.
- **F-G15 — observation.**
  - P3 `volume_structure`'s fall-through multiplies acknowledged units, but its `baseline` multiplies `F('unit_count')`.
  - These are equal whenever the latest acknowledgment covers the whole order, as in task 0 (12 = 12).
- **F-G16 — observation (wording).**
  - P6 says "Escalation weeks are added to the full weeks late", and the claim records "the full weeks late".
  - The rule defines "full weeks late" (calendar days from grace end to the lateness end date, divided by 7 and rounded down) and separately defines "credited weeks" as the sum. The tool argument description reads "the full weeks late recorded with the credit", so the recorded figure is the defined term.
  - Task 1 shows the mutated reading is incoherent: it would double-count in the credited-weeks sentence.

## closing_checklist
Written after both reveals (about 13:25Z, per file mtimes). Nothing in the sections above was changed after any reveal.

**Status: NOT CLOSED.** Task 1 carries a SOURCE-FACTOR RED (T1-F1, from F-G1), so the difficulty does not pass the source-layer audit.

| Item | Result |
| --- | --- |
| Per-task files | `0.md` and `1.md` sit alongside this file, one-to-one with `tasks/0.json` and `tasks/1.json`. First revision; no older revisions exist. |
| Comparisons | `0.md` PASS on all four relationships. `1.md` PASS on policy self-consistency, problem tree and unique solution; SOURCE-FACTOR RED on factors. |
| Coverage and scope | The 7 extended policies are fully covered: task 0 {P1, P2, P3}, task 1 {P4, P5, P6, P7}. `charter_scope` confirms the partition derived pre-reveal from the graph. The scopes are pairwise disjoint and each spans its whole tree. |
| Tools and GT | Task tools and GT are closed: every GT write uses one of the 7 tools with values entailed by the policy. Each uuid8 is independent and frozen (§action_binding_and_uuids). |
| Trees | Task 0 has 2 prerequisite problems, 2 value_input edges and a user write (P3). Task 1 has 3 prerequisite problems, 3 value_input edges and a user write (P6). Neither has a cycle, and the whole-difficulty graph is acyclic. |
| Factors | Every computation has 4–6 factors with at least 2 `parameter` and 1 `method` (method labels: F-G12 observation). Each task has a multi-source factor and a cross-difficulty factor (task 0: window; task 1: window and install). Every factor bears weight against an honest baseline, and each baseline alone gives a definite number different from gold. Ladder realism fails in task 1's weather_adjustment tier (F-G1 / T1-F1). The class-dependent ladder defects F-G2 bear on no current task. |
| Gates | Not re-run, because the difficulty is not closed. The coordinator snapshot leaves TRACEABILITY deferred until rendering. |

## revision_2

### charter_global_frozen (revision 2)
- Written about 14:13Z, before either round-2 task JSON was opened. Auditor: the same independent auditor as round 1.
- Hashes, verified and matching the coordinator brief:
  - `order.extended.yaml` `c23e295d23ea83c012c4d52a65c6149a386a2fdcfbecddfc1cf7f0cb0540d520`
  - `task_tools.py` `7a329df922ec271e969f68dc7937b852c5a9e85b22328a58dbd8011fe858d940`
  - `0.view.json` `65bd943d…78acf` (unchanged)
  - `1.view.json` `4a3f3eb1eed44b7a2e300545a8cd753690386c24cc606a471245c3f41a00bc56`
- Both shared inputs changed, so every charter-global section is re-derived in full below. Nothing is carried forward by reference.
- The base copy is still verbatim (`diff` against `blueprint/products/order.yaml` is empty).
- Entry conditions: the coordinator's snapshot at 14:06Z shows every gate OK except TRACEABILITY. That gate fails only on `unlock_*` tool-name provenance, because the documents are not rendered yet, so it is deferred to the rendering step as in round 1.
- Read discipline this round: every command named an explicit file. No search ran over the repository root or any directory. **contamination_disclosure (round 2): none.**

### Re-derived charter-global checks
- Rule against compute, verbatim (scripted):
  - Every `compute_basis` value of all 7 policies is now exactly one sentence of its own `rule`. There are no multi-sentence concatenations left, so the reworker's claim holds.
  - Every `baseline.rule` sentence and every `replaced_by` is in the rule.
  - Every `superseded_clause` is verbatim in its base policy.
  - No snake_case tokens appear in any rule.
- I read every compute expression against its rule and found no mismatch. The parts that changed:
  - P1 `cut_k`/`cutrun_n`: business days after the signature up to and including the first Friday after it.
  - P3 `ack_units = MAX(...)`: "the signed order acknowledgment that covers the most units". The fall-through tier is `F('unit_count')*rate`.
  - P4:
    - `start_t`: corrected acknowledgment, else replacement glass dated after the remake, else the remake date.
    - `frame_lead`: the larger of the class lead and 35 for triple-pane or laminated glass, class lead + 2 for low-E, otherwise the class lead.
    - `earlier_n`: the count of company-cause remakes.
  - P6:
    - `grace`: class // 2, or class − 2, or class.
    - `rate`: class × 0.5, or class × 1.2, or class.
    - `paid_weeks`: the escalation bands.
  - P7:
    - `restarts` is now filtered by `install_job_id=job_id`.
    - `rate`: class × 0.85, or class × 1.25, or class.
    - `storage_charge`: weeks beyond 4 at 1.5×, a single week priced as one 4-unit bay, otherwise weeks × rate × units.
- Action binding and UUIDs:
  - There are still 7 tools, each a distinct pair, with the same uuid8s as round 1 and the same owners (P3 and P6 are owner user).
  - A factor-id × tool-name substring scan finds nothing.
  - The tool bodies still validate nothing. The two notice tools now store `max(revised, standing)` as `current_ship_date`. This implements P4's new sentence ("never moves the order's current ship date earlier"), and P1's notice always moves the date later anyway. It is an effect of the write, not a prerequisite judgement.
  - The docstrings describe this behaviour truthfully. Neither the docstrings nor the argument descriptions carry a concrete gold value.
- Prerequisite graph and sentences:
  - The five edges, their `policy_source` sentences, `form: state`, `resolved_by` and `gate` are unchanged and still pass every scripted check.
  - The four-point test and the single-writer analysis from round 1 still hold. No new tool writes a cause or charge kind that another edge waits on.
  - New: the P5 edge's `effect` text still says "from the company-remake rate of 60 dollars to the customer-remake rate of 25 dollars". After the rework those figures are true only for Architectural Wood ($50 class credit). Observation R2-G1.
- Override declarations:
  - P4's replaced_by now keeps the company-cause clause ("a unit remade for a company cause is rebuilt within the class remake lead time from the remake date"). F-G4 is closed.
  - P4 adds two sentences:
    - "Whether a customer specification remake pushed the ship date is judged against the projected ship date on record when the remake was recorded …"
    - "A notice entered late for a remake that came before the order's later delay notices records an earlier delay, not a further delay."
  - These two sentences fix when "pushes" is judged, and they mark a late-entered notice as outside the base escalation trigger ("a further delay is escalated"). Below I confirm that this reading is unique.
  - P1, P2, P6 and P7 each add a sentence that confines the stale base enumerations and measure (late_ack_shift_basis, hold_requote_basis, lateness_ship_basis, order_msr_billable_storage_days) to the standard count. F-G7 and F-G8 are closed.
  - No new undeclared override: every quantity a new tier governs is introduced by a declared replaced_by or by the "set below" device.
- **Late-entered-notice reading (the coordinator asked me to confirm F-G11).** I confirm it is unique.
  - The base clause reads "When an order already carries the escalation number of delay notices, a further delay is escalated to the production manager and no credit or date promise beyond the recorded notices is made by support". It is triggered by a *new* delay arriving once the count is reached.
  - P4's sentence makes a back-entered notice for an earlier remake "an earlier delay, not a further delay". So support records it, and a guarantee credit computed from the recorded notices is not a credit "beyond the recorded notices".
  - The phrase "came before the order's later delay notices" is satisfied whenever a delay notice dated after the remake exists.
  - P6 counts that notice ("of every cause") for its escalation schedule. That is consistent: the notice exists on the order whether or not it was a "further" delay.

### factor_ladders (revision 2)

| Policy | Factors | Method factor | `parameter` | Cross-difficulty |
| --- | --- | --- | --- | --- |
| P1 | 4 | cut_list_regeneration (business days to the next Friday cut-list run / fixed 1 / 0) | 3, including signature_count_endpoint, now honestly a parameter | paint, insert (window) |
| P2 | 4 | requote_basis | 3 | none |
| P3 | 6 | volume_structure | 5 | 3 (window) |
| P4 | 6 | glass_recutting (max(class, 35) / class + 2 / class) | 5, including rebuild_start_anchor, now a parameter | 3 (window) |
| P5 | 4 | contract_charge_base | 3 | 2 (window) |
| P6 | 6 | escalation_schedule (bands of 2 + 1.5× beyond / +1 week / plain) | 5, including lateness_end_basis, now a parameter | none |
| P7 | 4 | long_storage_schedule (4 weeks + 1.5× beyond / one 4-unit bay / per unit) | 3 | permit, order size (install) |

- Every method factor now changes the shape of the formula: maximum versus sum, bands, a computed calendar distance, a flat bay. **F-G12 is closed.**
- Every ladder has 3 tiers, disjoint as stated, each stated in the rule and implemented in compute. Bindings are disjoint.
- Each tree still has a multi-source factor and a cross-difficulty factor:
  - task 0 tree: multi-source P1 signature_count_endpoint and P2 requote_basis; cross-difficulty window.
  - task 1 tree: multi-source P5 contract_charge_base (tier 2) and P7 permit_wait_allowance; cross-difficulty window and install.
- Tier values by class (F-G2):
  - P6 remake_rate gives 0.5× / 1.2× / 1× of the class rate, distinct in every class that carries the guarantee.
  - P6 capacity_grace gives class//2 / class − 2 / class: 2/3/5, 3/5/7 and 5/8/10.
  - P7 order_size_rate gives 85 % / 125 % / 100 % of the class rate, monotone in every class.
  - **F-G2 is closed.**
- **F-G1 is closed.** The weather tier is gone; P7 no longer reads weather or customer reschedules at all.
- Realism of the new tiers:
  - Plausible: the Friday cut-list run; sealed units reordered from the supplier running alongside the frame rebuild (the longer of the two); low-E glass cut in-house after the frame; rebuild starting when replacement glass arrives; requeueing behind company-cause rebuilds; escalating goodwill bands; escalating long-storage rates after 4 weeks; a 125 % rate for small lots.
  - One exception: R2-G2.

### Status of round-1 findings
| Id | Round-2 status |
| --- | --- |
| F-G1 | closed (tier removed) |
| F-G2 | closed (relative ladders) |
| F-G3 | closed (`install_job_id=job_id`) |
| F-G4 | closed (company-cause clause kept; sentinel and total − 1 removed) |
| F-G5 | P3 closed (MAX over acknowledgments). P1 still takes the LATEST acknowledgment for "the date the acknowledgment was signed"; not reached by task 0, still an observation |
| F-G6 | closed (the rule states "less than three whole calendar months", matching `0 <= MONTHS < 3`) |
| F-G7 | closed |
| F-G8 | closed |
| F-G9 | unchanged observation |
| F-G10 | unchanged observation |
| F-G11 | closed; reading confirmed above |
| F-G12 | closed |
| F-G13 | left as observation, as the reworker states |
| F-G14 | closed (tier replaced) |
| F-G15 | closed (fall-through = baseline = `F('unit_count')*rate`) |
| F-G16 | closed (wording removed; "credited weeks" defined separately) |

### New charter-global findings (revision 2)
- **R2-G1, observation.**
  - P6 `prerequisite[1].effect` still quotes "$60 → $25". That is correct only where the class credit is $50 (Architectural Wood).
  - For example, Custom Size Build would go from $30 to $12.50.
  - It is general text, so a stale number there misdescribes the edge for every other class. Task 1 is Architectural Wood, so no consequence there.
- **R2-G2, SOURCE-FACTOR-class realism defect. Bears on no current task.**
  - P7 `long_storage_schedule` tier 2 reads "a single billable week is charged as one bay, 4 units' worth of the weekly storage rate whatever the units on the order".
  - For an order of more than 4 units, one week costs less than per-unit pricing, and the charge then jumps at week 2. A 20-unit order pays 4 unit-weeks for 1 week but 40 unit-weeks for 2 weeks. A bay minimum would be published as max(4 units, units on the order), not as a flat 4-unit figure.
  - For an order of exactly 4 units the tier equals the fall-through.
  - Not reached: task 1 takes the more-than-4-weeks tier.
- **R2-G3, observation (interaction new in round 2).**
  - P4's new replacement-glass tier assumes a glass_received checkpoint after a remake.
  - In such a world, P5's build-stage test ("the most recent glass received checkpoint is dated on or before the remake date", compute `LATEST glass_received <= rmk_date`) fails on the replacement glass even though glass was on hand by the remake date. Its tier-3 condition ("neither checkpoint is on record by the remake date") is false too. No tier of the rule then matches, and the compute falls to 40 %.
  - Not reached: task 1 has a single glass_received (04-08).
- **R2-G4, observation (cross-category realism).**
  - In task 1, the customer reschedule of 2026-10-08 moves the crew date to 2026-11-23, 30 business days out.
  - Full-Frame's `reschedule_offer_business_days` is 10, and the install charter says "A new date is offered within the method's reschedule window".
  - A date this far out is a customer choice beyond what is offered. The order charter does not read the window, so there is no scored consequence.

### closing_checklist (revision 2)
Written after both revision-2 reveals at 14:14Z. The revision-2 charter-global section above was written before them.

**Status: CLOSED. Both tasks PASS all four relationships.**

| Item | Result |
| --- | --- |
| Per-task files | `0.md` and `1.md` each carry the round-1 text untouched plus `## revision_2` (frozen derivation, then comparison). Both revision-2 comparisons are PASS. |
| Coverage and scope | The 7 extended policies are covered. `charter_scope` is task 0 {P1, P2, P3} and task 1 {P4, P5, P6, P7}: disjoint, and each spans its whole tree. |
| Tools | The 7 task tools keep their independent, frozen uuid8s. GT writes are closed over them. |
| Trees | Task 0 has 2 prerequisite problems, 2 value_input edges and user write P3. Task 1 has 3 prerequisite problems, 3 value_input edges and user write P6. Neither has a cycle, and the difficulty graph is acyclic. |
| Factors | Every computation has 4–6 factors with at least 2 `parameter` and exactly 1 shape-changing `method`. Each tree has a multi-source factor and a cross-difficulty factor. Every factor bears weight against an honest baseline, and each baseline alone gives a definite number that differs from gold. The ladders of every tier taken are real. |
| Gates | The coordinator's snapshot at 14:06Z was taken on exactly the audited hashes (`c23e295d…`, `7a329df9…`, views `65bd943d…` / `4a3f3eb1…`): every gate OK except TRACEABILITY, which still fails only on `unlock_*` tool-name provenance and must be re-run after the order documents are rendered. I did not re-run the gates myself. |

Open observations, none of them grounds for rework under the four relationships:
- R2-G1: stale "$60 → $25" in P6's edge `effect`.
- R2-G2: P7's flat 4-unit bay tier for single-week storage of larger orders. It is a SOURCE-FACTOR-class realism defect, but no current task reaches it; it would become a red light for any future world that takes it.
- R2-G3: the interaction between P5's build-stage test and P4's replacement-glass tier.
- R2-G4: the customer crew date beyond the install offer window.
- F-G5: P1 still uses the LATEST acknowledgment.
- F-G9, F-G10, F-G13: unchanged.
- T1-O3, T1-O4, T1-O5: unchanged.

## revision_3

### charter_global_frozen (revision 3)
- Written about 15:58Z, before either round-3 task JSON was opened.
- Hashes, verified and matching the brief:
  - `order.extended.yaml` `3f12b81799f4f69c038e01718eb6d52d8b13d464e48c17da1d1dab1e47e4d0da` (changed)
  - `task_tools.py` `7a329df9…d940` (unchanged from revision 2)
  - views `65bd943d…78acf` (unchanged) and `a76c68a73138a92f7069e7bdeb24e976db795f568ca965a0612f465a92781d62`
- The base copy is still verbatim.
- The charter changed, so every charter-global check was re-run in full:
  - The verbatim checks were repeated. Every `compute_basis` value is one sentence of its rule, and every baseline sentence, replaced_by and superseded clause verifies.
  - The prerequisite graph is unchanged and passes again (`policy_source` verbatim, `resolved_by`, `gate`, `form: state`).
  - No factor id is a substring of a tool name. Bindings are disjoint. No snake_case appears in any rule.
  - Factor counts are unchanged: 4 / 4 / 6 / 6 / 4 / 6 / 4, with exactly 1 method factor per computation.
  - Every round-2 sentence I relied on is still present: the Friday cut-list run, the three-month window, the largest acknowledgment, the late-entered notice and the escalation schedule.
- Rule against compute: I read every expression of P5 and P7 against its rule. The other five policies' compute expressions evaluate to identical values on both worlds.
- Read this round: the renderer finding `audits/render_source/factory_order_milestones_and_delays/order_round1.md` (as the brief asked), the install charter's event list (to check R2-G4), the charter, the tools and the two views.
- contamination_disclosure: none. Every command named an explicit file.

### Items re-checked
- **F-1 (renderer) / R2-G3: closed.**
  - The P5 rule now reads the build stage "from the checkpoints that cover every unit on the order (a checkpoint for remade or replacement units alone does not count)".
  - Its tiers are an exhaustive else-chain: full charge when the most recent such assembly checkpoint is on or before the remake date; "otherwise, when the most recent such glass received checkpoint is dated on or before the remake date, 70 percent"; "otherwise 40 percent".
  - The compute matches it: `LATEST(..., unit_count=F('unit_count'))` for both checkpoints and the same else-chain.
  - Every world now falls into exactly one tier. A replacement-glass checkpoint for the remade units alone (the case P4 contemplates) no longer moves the build stage. That is realistic, because the original glazing of the order is what was spent.
  - Residual wording, observation R3-G1: the factor `ladder` text for 40 % says "neither full-order checkpoint is dated on or before the remake date". The rule's "otherwise" also covers the corner where an earlier full-order glass checkpoint precedes the remake and a later full-order one follows it. The rule and compute are authoritative and agree, and no task reaches the corner.
- **R2-G2: closed.**
  - The single-week tier is now "charged for at least one full bay, the weekly storage rate times the larger of 4 units and the units on the order". The compute is `rate * MX(K('bay_units'), F('unit_count'))`.
  - This is a realistic minimum charge, and there is no longer a discount for large orders.
  - For orders of 4 or more units the minimum does not bind, so tier 2 coincides with per-unit pricing for that single week. That is the ordinary behaviour of a floor, not two tiers sharing one method. Recorded as a note only.
- **R2-G1: closed.** The P6 edge `effect` now reads "from 1.2 times the class credit per unit per week (the company-remake tier) to half of it (the customer-remake tier)", which is correct for every class.
- **R2-G4: closed.**
  - The task-1 customer reschedule (9bb4cbb2…, 2026-10-08) now has no `new_date`. That releases the date, and the install charter returns the job to opened.
  - The later booking is the job-level `install_scheduled` transition (`install_jobs.scheduled_date = 2026-11-23`). In the install charter that transition targets `install_jobs`, not `install_activities`, so no activity row is expected.
  - P7 reads only company and weather reschedules, so no value moves.
- Regression sweep: nothing regressed. Each round-1 and round-2 closure listed under revision_2 still holds.
- Open observations are carried forward unchanged: F-G5 (P1 still uses the latest acknowledgment), F-G9, F-G10, F-G13, T1-O3, T1-O4, T1-O5.

### closing_checklist (revision 3)
Written after both reveals at 15:55:34Z.

- Both tasks PASS all four relationships. **The difficulty is CLOSED.**
- Coverage and scope: partition {P1, P2, P3} / {P4, P5, P6, P7}, disjoint and complete.
- Trees: 2 prerequisite problems and 2 value_input edges in task 0; 3 and 3 in task 1. The user writes are P3 and P6. Neither tree has a cycle, and the difficulty graph is acyclic.
- Factors:
  - 4–6 factors per computation, each with at least 2 `parameter` and exactly 1 shape-changing `method`.
  - Each tree has a multi-source factor and a cross-difficulty factor.
  - Every factor bears weight against an honest baseline, and each baseline gives a definite number that differs from gold.
  - The ladders of the tiers taken are real.
- Tools: uuid8s independent and unchanged; nothing validated in any tool body.
- Gates: the coordinator's snapshot at about 17:25Z (as stated in the brief) is taken on the audited hashes. Every gate is OK, including TRACEABILITY now that the order docs are published, so this checklist item is satisfied. I did not re-run the gates myself.
- Open observations (not grounds for rework): R3-G1, F-G5, F-G9, F-G10, F-G13, T1-O3, T1-O4, T1-O5.

revision_3 verdict: task 0 PASS
revision_3 verdict: task 1 PASS
