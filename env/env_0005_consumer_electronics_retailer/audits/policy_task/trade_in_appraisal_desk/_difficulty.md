# Policy-task audit — trade_in_appraisal_desk / charter-global

## charter_global_frozen

- freeze time: 2026-09-18 09:23 UTC (pre-reveal; nothing in this section is derived from any task's masked GT)
- auditor: independent source-layer auditor (not the instantiating agent)
- artefacts frozen for this section:
  - `env/env_0005_consumer_electronics_retailer/tasks/trade_in_appraisal_desk/tradein.extended.yaml` sha256_16 = `3e2ef593a265f3af`
  - `env/env_0005_consumer_electronics_retailer/tasks/trade_in_appraisal_desk/task_tools.py` sha256_16 = `ba59e057f4f298b4`
  - `env/env_0005_consumer_electronics_retailer/blueprint/products/tradein.yaml`, `blueprint/blueprint.yaml`, `blueprint/db_schema.json`, `blueprint/share_tools.py`
  - other categories' charters read only for the cross-category reads this charter declares: `products/protection.yaml`, `products/service.yaml`, `products/orders.yaml`, `products/membership.yaml`, `products/returns.yaml`, `products/credit.yaml`
- fields permitted while this section was written: the whole base section, `extended_policies` (rule / compute / compute_basis / overwrite / prerequisite / factors / baseline / inputs / params), the tool module, the DB schema, the shared tool schemas.
- fields explicitly masked and unread while this section was written: every task's `evaluation_criteria`, `computations`, `charter_scope`, `required_documents`, `design_rationale`, `solvability_contract`, `prerequisite_closure`, `db_closure`, `db_closure_matches_initial_state`; masked views built by the invoking agent
  (`0.json` masked sha256_16 = `7a73e62e194cf379`, `1.json` masked sha256_16 = `907fcc983f4d8262`).
- entry conditions cited, not re-run: the instantiation gate snapshot supplied with the brief reports `check_extended`, `check_task_tools`, `replay_tasks`, `check_solvability`, `check_compute`, `check_grounding`, `check_cross_fire` all green; `check_traceability` is deferred to the render step by design. A machine green light is the qualification to enter this audit, not a proof of correctness.
- base-section closure verified mechanically: the extended file's text up to `extended_policies:` is byte-identical to `blueprint/products/tradein.yaml` (both 80074 bytes, no differing byte). The base copy has not been rewritten.

### policy_conflict_scan

Scope: all 14 base policies of `tradein` plus the 5 extended policies, over overlapping subjects, triggers, eligibility, time anchors, action parameters, terminal states and cross-category read boundaries.

Extended surface (5 policies, all subjects inside the claimed `event_types`):

| policy | trigger | subject | computes | target_tool | prerequisite |
| --- | --- | --- | --- | --- | --- |
| `tradein_ext_collection_handover_units` | on_request | `tradein_quote_accept` | `units_declared` | `confirm_handover_units_5801b6db` (owner=user) | — |
| `tradein_ext_collection_freight_charge` | on_request | `tradein_handling_fee_charge` | `handling_fee_amount` | `charge_collection_freight_530ef4f1` (agent) | `tradein_ext_collection_handover_units` (value_input) |
| `tradein_ext_revised_offer_amount` | state_due | `tradein_quote_revise` | `revised_amount` | `put_revised_offer_f86761c2` (agent) | — |
| `tradein_ext_batch_settlement_credit` | state_due | `tradein_agreement_credit` | `final_credit_amount` | `credit_batch_settlement_af2cb6f5` (agent) | `tradein_ext_revised_offer_amount` (value_input) |
| `tradein_ext_refresh_wave_units` | on_request | `tradein_quote_accept` | `units_declared` | `confirm_refresh_wave_units_923c3678` (owner=user) | `tradein_ext_batch_settlement_credit` (state_gate) |

Two problem trees, disjoint in policies: {handover_units, freight_charge} and {revised_offer, batch_credit, refresh_wave}. All 5 extended policies are covered, none twice — the suite is jointly complete and pairwise disjoint at the level of policy ids.

Compatible and carrying no conflict:
- Eligibility inherited from base is respected by both trees' subjects: `feeable_agreement_state` (accepted / device_received / appraised / credited) for `tradein_handling_fee_charge`; `creditable_agreement_state` (appraised / credited) for the credit; `customer_consented_handover` for `tradein_quote_accept` — the two user tools create exactly the `tradein_shipping_requests` row with `customer_consent='consented_by_customer'` that this eligibility names as its evidence.
- Time anchors: `quote_validity_days` is counted from `quote_date` in both `tradein_ext_collection_freight_charge.quote_days_run` and `tradein_ext_refresh_wave_units.quote_days_run`, matching base `tradein_quote_issue` ("counted from the day the quote was given"). `bulk_pickup_lead_days` is counted from the day of the write to `requested_collection_date` in both policies that use it, consistently.
- `member_bonus_applies=False` on both business programmes and base `tradein_combo_membership_interaction` ("A business programme takes no membership bonus at all") are not contradicted: no extended policy adds a trade-in bonus. (The membership *freight relief* of `tradein_ext_collection_freight_charge` is a different quantity — the collection charge, not the amount settled.)
- `tradein_guarantee_floor` is inert on both business programmes (`guarantee_floor_pct_of_purchase_price = 0`, `guarantee_term_months = 0`), so naming it in `tradein_ext_batch_settlement_credit.base_policy_refs` adds no conflict.
- Cross-category read boundaries are declared per policy and match the compute: protection+service (handover units), orders+membership (freight charge), protection (batch credit), returns+orders+credit (refresh wave). No compute reads a category its policy does not declare.

Conflicts found — see `findings` F1, F2, F3, F5, F6 below. Two of them are conflicts with base policies that are **not** named in any `base_policy_refs` and not superseded anywhere (`tradein_data_sanitisation`, `tradein_device_logistics` read against `tradein_ext_revised_offer_amount`), so they cannot be found by reading `overwrite` alone.

Scope exclusivity, one caveat (see F9): the two trees are disjoint by policy id, but the *discriminator* between them is only the programme's prose name. `tradein_ext_collection_freight_charge` opens "A palletised collection on a business buyback is charged to the profile when the run is booked", and its trigger is `on_request`; the Renew Bulk IT Refresh Agreement is also a business trade-in programme whose only allowed shipment method is freight collection and which carries its own `freight_fee_usd = 245.0`. Nothing in either rule says the freight charge does not apply to a refresh wave.

### rule_compute_equivalence

Check 2, swept in both directions over all 5 extended policies. Every binding of every policy has a `compute_basis` entry, and each entry is a verbatim sentence of that policy's own `rule` (checked string by string). The tier sets of every `factors[].ladder` correspond one-to-one with the ternary branches of the `decides` binding, and each tier's `when` is a sentence fragment of the rule. Rounding is stated wherever it happens ("rounded to the cent" for the three money policies, "rounded down to a whole machine" / "a whole count of machines" for the two unit policies), and the interval conventions are stated ("counted in calendar days from …" on every `DAYS(...)` binding).

Three places where the correspondence fails:

1. **Grouping of operations is not stated at all in `tradein_ext_collection_handover_units`** — F4 below. `result: int(collectable_units * run_fill_pct / 100)` applies the lift share *after* the holdbacks, and no sentence of the rule says so; the rule defines "the machines that may go" twice, once as the share of the run and once as the capped figure less the holdbacks. `compute_basis.result` quotes only the baseline sentence, which settles neither.
2. **`tradein_ext_refresh_wave_units.cover_units` — the compute's fall-through fires in a case the rule's third tier excludes** (observation O5). The rule's tiers are (i) `value_each >= cover and quote_days_run <= validity`, (ii) `schedule value > cover and value_each < cover`, (iii) "the value of the whole schedule is at or below the programme's transit cover". A world with `value_each >= cover` and `quote_days_run > validity` satisfies none of the three as written, yet the compute's `else` branch hands it tier (iii)'s value (`devices_on_schedule`). The rule therefore does not partition its own domain, and compute supplies a basis the rule does not state.
3. **`tradein_ext_refresh_wave_units.order_holdback` — the compute produces tier 2 where the rule states tier 3** (observation O6). `days_since_fulfilled: DAYS(CFIELD('orders','fulfilled_date', status='fulfilled') or NOW, NOW)` returns 0 when the profile has no fulfilled order at all, which satisfies `days_since_fulfilled <= K('recent_purchase_days')`; with `order_balance` then also 0, the compute selects `K('recent_order_holdback')` = 2. The rule says "Where no order on the profile was fulfilled within the recent purchase days, no machine is held back on that account" = 0.

### action_binding_and_uuids

- `(target_tool, computes)` pairs: `(confirm_handover_units_5801b6db, units_declared)`, `(charge_collection_freight_530ef4f1, handling_fee_amount)`, `(put_revised_offer_f86761c2, revised_amount)`, `(credit_batch_settlement_af2cb6f5, final_credit_amount)`, `(confirm_refresh_wave_units_923c3678, units_declared)`. Each pair is claimed by exactly one policy. Two distinct policies compute the binding name `units_declared`, but through different tools, so the pair is unique.
- uuid8s: `5801b6db`, `530ef4f1`, `f86761c2`, `af2cb6f5`, `923c3678`. All five distinct, no shared prefix, no sequence, no adjacent values, none a re-tail of another — each reads as independently generated and is frozen with its tool.
- No docstring names another tool, and none states its action's position in a sequence. The ordering words that do occur ("once it is on record", "until it is settled or waived", "Afterwards") each describe that tool's own effect, not a place in a chain. Acceptable.
- One substantive problem: **the two `owner=user` tools are behaviourally identical** — see F9. `confirm_handover_units_5801b6db` and `confirm_refresh_wave_units_923c3678` take the same four arguments, create a `tradein_shipping_requests` row with the same six field values (`requested_shipment_method='freight_collection'`, `customer_consent='consented_by_customer'`, `units_declared`, `requested_collection_date`, `created_at`), and return the same sentence with "Collection … on agreement" / "Wave … on schedule" swapped. Their terminal states are indistinguishable in the records.
- Tool-layer neutrality confirmed by reading every function body: none of the five validates eligibility, reads a prerequisite, refuses a call or hints. `charge_collection_freight_530ef4f1` and `credit_batch_settlement_af2cb6f5` read the agreement row only to copy `device_serial` / `variant_name` onto the event and to add to a running total.
- One incompleteness against inherited base: base `tradein_credit_issue_rules` ends "The credit expires at the end of the programme's validity days from the day it was issued, and **the expiry day is written onto the agreement when the credit is issued**". `credit_batch_settlement_af2cb6f5` writes `status`, `credited_date`, `final_credit_amount` and `credit_outstanding` and leaves `tradein_agreements.credit_expiry_date` (a real column) untouched. That base sentence is in no `overwrite`. Recorded as observation O2.

### prerequisite_graph

Check 7 over the whole graph.

- Every extended policy carries `prerequisite` explicitly; three are `[]` (`collection_handover_units`, `revised_offer_amount`) — two are `[]`, and the three edges declared are:
  - `collection_freight_charge -> collection_handover_units`, kind `value_input`, gate `consented_units`, form `state`
  - `batch_settlement_credit -> revised_offer_amount`, kind `value_input`, gate `settled_amount`, form `state`
  - `refresh_wave_units -> batch_settlement_credit`, kind `state_gate`, gate `tradein_agreements.final_credit_amount`, form `state`
- Every `problem` names a policy id in this file, none names a base policy, none names itself. The graph is two disjoint chains, both acyclic; no cross-task reference creates a cycle.
- Every `policy_source` is verbatim locatable in the **blocked** policy's own `rule` (checked by string search):
  - "The collection charge is fixed only after the machines the customer consents to hand over stand on a shipment request for a freight collection." — present in `collection_freight_charge.rule`, sentence 2.
  - "The amount credited is worked out only after the revised offer the appraisal calls for stands on the agreement's trade-in history." — present in `batch_settlement_credit.rule`, sentence 2.
  - "The machines a wave of the refresh schedule carries are settled only after every batch already appraised on the profile stands credited with the amount owed on it." — present in `refresh_wave_units.rule`, sentence 2.
- `form: state` on all three; no `fallback_reason` present anywhere, which is correct because no edge is action-form.
- `kind` matches `gate`: `consented_units` and `settled_amount` are real compute bindings of their blocked policies (`value_input` correct); `tradein_agreements.final_credit_amount` is a record field and an eligibility, not a binding of `refresh_wave_units.compute` (`state_gate` correct).
- `resolved_by` is in each case the depended-on policy's `target_tool`, and each named tool genuinely moves the gate: `confirm_handover_units_5801b6db` creates the shipping request row that `LATEST('tradein_shipping_requests','units_declared')` reads; `put_revised_offer_f86761c2` creates the `tradein_quote_revise` row that `COUNT`/`LATEST` read; `credit_batch_settlement_af2cb6f5` sets `status='credited'` and `final_credit_amount`.
- No authoring-viewpoint phrasing ("in this task", "at the opening", "the current world") appears in any `prerequisite` block.
- One `effect` text asserts a mechanism that does not exist — observation O3: the `refresh_wave_units` edge says the gate holds "because the credit the profile has been issued in the year is then complete", but no binding of `refresh_wave_units.compute` reads the credit issued in the year, and `trade_in_value_cap_per_year_usd` (400000.0) plays no part in it. The gate is a pure ordering requirement; the stated reason is not the mechanism.
- One `condition` is satisfiable by inspection without the depended-on write — F7, the sharpest finding of this audit. The `collection_freight_charge` edge's condition reads "the latest shipment request taken on the agreement for a freight collection carries the machines the customer consents to hand over on this run", and its `policy_source` sentence is purely existential ("… stand on a shipment request for a freight collection"). Nothing in it requires the request to be *this* consultation's, to be fresh, or to carry the figure the desk works out today. Whether that costs a task its problem tree is demonstrated in that task's file.

### prerequisite_sentences

Check 6, four-point test on each of the three sentences.

1. `collection_freight_charge` ← `collection_handover_units`
   - ordering connective: "only after" ✓. Joins this policy's own result ("The collection charge is fixed") to what it waits on ✓.
   - form `state`: "the machines the customer consents to hand over stand on a shipment request for a freight collection" — a record-visible state in table words (`tradein_shipping_requests`, `units_declared`, `requested_shipment_method`, `customer_consent`), no performer, no tool ✓.
   - names no tool, no policy id, no snake_case token, no row id ✓.
   - **strength/scope: fails.** The `condition` says the latest request "carries the machines the customer consents to hand over **on this run**"; the sentence says only that consented machines "stand on a shipment request". The sentence is broader than the condition, and the broader reading is the one a rollout agent reads. Exactly one write of this difficulty brings a *new* consented freight-collection request about (`confirm_handover_units_5801b6db`; `confirm_refresh_wave_units_923c3678` writes the same state but on a refresh schedule), so the hop is resolvable — but the state is one a seeded world can already carry. See F7.
2. `batch_settlement_credit` ← `revised_offer_amount`
   - "only after" ✓; state form ("the revised offer the appraisal calls for stands on the agreement's trade-in history") ✓; no tool/id ✓; scope matches the `condition` ✓. Exactly one write of this difficulty puts a revised offer on the trade-in history (`put_revised_offer_f86761c2`) ✓ single reading.
   - Derivation (sentence + records + the depended-on rule): the blocked rule says the credited amount waits on a revised offer standing on the trade-in history; the records show whether a `tradein_quote_revise` row stands on the agreement; `tradein_ext_revised_offer_amount.rule` says a revised offer is owed where an appraisal finds a batch other than the condition declared and states the figure. One reading, one resolving action.
3. `refresh_wave_units` ← `batch_settlement_credit`
   - "only after" ✓; state form ("every batch already appraised on the profile stands credited with the amount owed on it") — record-visible (`tradein_agreements.status`, `final_credit_amount`) ✓; no tool/id ✓; the `condition` restates it at the same strength ✓. Exactly one write of this difficulty sets `status='credited'` with an amount (`credit_batch_settlement_af2cb6f5`) ✓ single reading.
   - Derivation: the blocked rule says the wave's machines wait on every already-appraised batch standing credited; the records show which agreements stand appraised without a credited amount; `tradein_ext_batch_settlement_credit.rule` says an appraised batch is closed out by crediting the customer and states the figure. One reading.
- No rule restates another's dependency, no rule carries a second wording of its own edge, no depended-on rule repeats the blocked rule's sentence, and no rule states a cross-problem order that grounds no declared edge. (`tradein_ext_collection_handover_units.rule` sentence 1 — "the machines one run carries are settled with the customer before the customer consents to the handover" — is about the same policy's own write and the customer's consent, i.e. its own subject, not another problem.)
- No **base** rule sentence is used to ground an edge.

### override_declarations

Check 1's finding half, sentence by sentence against each `base_policy_refs` entry. Consequences are demonstrated in the task files.

**`tradein_ext_collection_handover_units` → base `tradein_quote_acceptance`** (5 sentences)
- S1 "A device is taken from the customer only against a shipping request standing as consented by the customer for that agreement…" — followed (the tool writes exactly that row).
- S2 identity + least age — inherited untouched; `identity_check_required = True` on both business programmes.
- S3 make/model/serial correction — inherited, inert.
- S4 linked purchase window — inherited; inert on this programme (`linked_purchase_required = False`).
- S5 "A business agreement is accepted only once the signed asset list the programme requires is on file, and the units on the list govern what may be collected." — **declared** in `overwrite` and genuinely replaced (the units now come from the batch allowance and the holdbacks). Note the declaration supersedes the whole sentence, including the asset-list gate, although the replacement speaks only to the units; recorded as observation O7.

**`tradein_ext_collection_freight_charge` → base `tradein_device_logistics`** (6 sentences)
- S1 allowed shipment method + label validity — inherited; `shipment_methods_allowed` includes freight collection on both business programmes.
- S2 `feeable_agreement_state` — inherited untouched.
- S3 first half, "The programme's handling fee is charged on a mailed-in device and is waived where the quote is at or above the programme's waiver figure" — **not** named in `overwrite`. The extended policy nonetheless charges a per-machine "handling" component (`K('short_load_handling_usd')=3.5`, `first_load_handling_usd=5.0`, `standard_handling_usd=1.75`) into the same field (`handling_fee_amount`) and the same event type (`tradein_handling_fee_charge`) for which the programme's own `handling_fee_usd = 0.0` and `handling_fee_waived_above_usd = 0.0`. Base's sentence is about a *mailed-in* device and this is a palletised collection, so the two do not strictly speak to one situation; recorded as observation O1 rather than a red light, with the alternative figure computed in `0.md`.
- S3 second half, "the freight fee is charged on a palletised collection, which needs the programme's lead days of notice" — **declared** and genuinely replaced (a collection inside the lead days is now priced with a spot premium instead of being refused).
- S4 transit cover settlement — followed, and re-used by `batch_settlement_credit`.
- S5 declined device return — inherited, inert.
- S6 "A shipment arriving with fewer units than the request declared is booked in at the units actually received, and the agreement is appraised on those." — inherited untouched here; see F3, where `tradein_ext_revised_offer_amount` prorates a second time on the same fact.

**`tradein_ext_revised_offer_amount` → base `tradein_appraisal_grading`** (7 sentences)
- S1 appraisal window + "the condition found governs the amount" — inherited.
- S2 `appraisable_agreement_state` — inherited.
- S3 "The amount the appraisal supports is the quoted amount times the percentage the programme's condition ladder gives for the condition found, rounded to the cent." — inherited; the extended policy reads `F('appraised_amount')` and says "as recorded on the agreement", which pins the input to the record rather than recomputing. Compatible only as long as the seeded `appraised_amount` is what the ladder yields for the seeded `appraised_condition`; see F8.
- S4 deduction order — inherited, inert (no deduction is recomputed).
- S5 "Where the amount the appraisal supports falls below the quote by no more than the programme's tolerance, the quote is honoured as written and no revised offer is put to the customer." — **declared** and replaced (the offer is now *put* at the standing figure instead of no offer being put).
- S6 different-model rule, S7 zero-value handling — inherited, inert.

**`tradein_ext_revised_offer_amount` → base `tradein_revision_and_decline`** (7 sentences) — `overwrite` names nothing from this policy.
- S1 "A revised offer is put to the customer within the programme's revision notice days of the appraisal, and it names the reason the offer moved." — inherited; the tool's `revision_reason` enum satisfies the second half, and the first half is a live timing constraint the tasks must respect.
- S2/S3 decision days for a decline — inherited.
- S4 "Where the programme takes silence as acceptance and the decision days run out with no answer, the revised offer is credited; where the programme does not, the device is sent back." — inherited, and in tension with `tradein_ext_batch_settlement_credit`'s "the credit is owed as soon as the amount settled stands on the records" (both business programmes have `auto_accept_on_silence = True`, `customer_decision_days` 14 and 21). Recorded as F5.
- S5 nothing charged for the appraisal on a decline — inherited, inert.
- S6 "A device already recycled or destroyed under the programme's sanitisation rules cannot be sent back, so on those programmes the revised offer is put before the data is destroyed." — inherited; see F6.
- S7 dispute window — inherited, inert.

**`tradein_ext_batch_settlement_credit` → base `tradein_credit_issue_rules`** (6 sentences)
- S1 "The credit issued is the amount finally settled with the customer, which is the appraised amount where no revision was needed and the revised amount where one was accepted." — **declared** and replaced, including the "where one was accepted" qualifier.
- S2 `creditable_agreement_state` — inherited.
- S3 allowed forms / instant discount — inherited; `instant_credit_at_till = False` on both business programmes.
- S4 promotional uplift — inherited, not used.
- S5 "A business agreement is credited by invoice credit or bank transfer only, and the credit is issued once for the batch rather than device by device." — inherited, and the extended policy's whole `interim_credit_recovery` factor presupposes a batch that already carries a credit row and is credited again. Recorded as F2 (the first half also leaves `settlement_method` a two-way choice the policy never narrows — observation O4).
- S6 credit expiry written onto the agreement — inherited, and not producible by the target tool (observation O2).

**`tradein_ext_batch_settlement_credit` → base `tradein_guarantee_floor`** (5 sentences) — all inert on a business programme (`guarantee_floor_pct_of_purchase_price = 0`). `overwrite: []` against this ref is correct.

**`tradein_ext_refresh_wave_units` → base `tradein_quote_acceptance`** (5 sentences)
- S1–S3 as above, inherited.
- S4 linked purchase window — **declared** superseded, although `linked_purchase_required = False` on this programme makes the clause inert and the replacement addresses a different subject entirely (the machines a wave carries). A declaration that disposes of a clause the extended text does not contradict; observation O8.
- S5 "A business agreement is accepted only once the signed asset list the programme requires is on file, and **the units on the list govern what may be collected**." — **NOT declared anywhere in this policy's `overwrite`**, although `business_asset_list_required = True` and the entry gate `asset_list_filed: True` hold for Renew Bulk IT Refresh Agreement, and the policy's own replacement text decides the very same quantity ("The machines a wave carries are the machines the schedule covers, capped at …, less …"). This is an undeclared override — F1.

Beyond `base_policy_refs`, two base policies conflict with the extended surface and are named in no `overwrite`: `tradein_data_sanitisation` (F6) and `tradein_device_logistics` S6 read against `tradein_ext_revised_offer_amount` (F3).

### factor_ladders

Structure only; weight is per task.

| policy | factors | parameter | method | multi-source | cross_difficulty |
| --- | --- | --- | --- | --- | --- |
| collection_handover_units | 4 | 2 (`carrier_batch_allowance`, `crew_machine_holdback`) | 2 (`claim_holdback_basis`, `run_lift_share`) | 4 | protection, service |
| collection_freight_charge | 6 | 5 | 1 (`pallet_count_basis`) | 6 | orders, membership |
| revised_offer_amount | 4 | 2 (`booked_device_share`, `offer_ageing_markdown`) | 2 (`tolerance_gap_treatment`, `offer_ageing_anchor`) | 1 (`offer_ageing_markdown`) | none |
| batch_settlement_credit | 6 | 5 | 1 (`settled_figure_basis`) | 3 | protection |
| refresh_wave_units | 4 | 3 | 1 (`transit_cover_wave_basis`) | 3 | returns, orders, credit |

Counts are inside 4–6 per policy, and each policy declares ≥2 `parameter` and ≥1 `method` as written. Bindings are disjoint within each policy, every `decides` is an input binding rather than `result`, and every ladder has three tiers stated in full in the `rule` with its condition and its value or method, each implemented as one branch of the `decides` binding. Every `method` tier names a computation the charter states.

Structural defects:

- **F10 — `settled_figure_basis` (batch_settlement_credit): tiers 2 and 3 select the same method, word for word.** Tier 2 `method: "the amount settled is the amount the appraisal supports"`, tier 3 `method: "the amount settled is the amount the appraisal supports"`. The ladder has three `when`s and two outcomes; the compute confirms it (`appraisal_amount` in both the second and the third arm of `settled_amount`). One tier has been written as two. Since this is the *only* `method` factor of `tradein_ext_batch_settlement_credit`, striking it leaves that policy with 0 `method` factors against a floor of 1.
- **F11 — `run_lift_share` (collection_handover_units) is labelled `method` but its tiers substitute a rate.** The three tiers select `spot_fill_pct=75`, `lane_fill_pct=90`, `full_fill_pct=100` into one unchanged formula `int(collectable_units * run_fill_pct / 100)`; two of the three tier texts are identical but for the share word ("taken at the spot share … rounded down to a whole machine" / "taken at the lane share … rounded down to a whole machine"). A percentage is a number, not an algorithm. Striking the label leaves `collection_handover_units` with 3 `parameter` and 1 `method`, still inside the bounds, so the consequence is the honesty of the label rather than a count breach.
- **O9 — `booked_device_share` (revised_offer_amount) is labelled `parameter` but its tiers change the formula** (`devices_booked_in/devices_declared`, then its reciprocal, then 1.0). Read as a `method`, that policy drops to 1 `parameter` against a floor of 2. Recorded as an observation because "a ratio" can be argued either way, with the count consequence stated.
- **F12 — `machine_handling_rate` (collection_freight_charge): tier 2's condition cannot hold of any customer who reaches this write, and tier 1's second conjunct holds of all of them.** The tiers turn on `requests_taken: COUNT('tradein_shipping_requests')`, agreement-scoped (`skills/erl-task-instantiate/scripts/check_compute.py:288`, `eq[holding_pk] = HID`). The policy's own prerequisite requires a consented freight-collection shipment request to stand on the agreement before the charge is fixed, and the resolving write creates one, so `requests_taken >= 1` whenever this policy is evaluated. "no shipment request has been taken on the agreement" (`first_load_handling_usd = 5.0`) is unreachable and "a shipment request has already been taken on the agreement" restates the policy's scope instead of dividing its customers.
- **F13 — `tradein_ext_refresh_wave_units.baseline` is not self-sufficient.** `baseline.rule` is "The machines a wave carries are the machines the schedule covers, capped at the machines the programme's transit cover will bear, less the machines a live return authorisation holds back, the machines a recent purchase holds back and the machines the profile's store account holds back, and the figure is a whole count of machines and never fewer than none. The value of each machine is the amount quoted on the schedule spread over the machines the schedule covers." It names four quantities and gives a default for none of them; a reader cannot reach a definite number from it and the records without opening a factor's document. `baseline.params: [recent_purchase_days, finance_hold_balance_usd]` names two factor thresholds that the baseline sentence does not use, and does not name the defaults the factor baselines actually encode (`cover_units = devices_on_schedule`, the three holdbacks = 0). Contrast the other four policies, which each state their defaults outright ("the run lifts those machines in full"; "no spot premium and no cover uplift are added, and no relief is taken off"; "the amount settled is the amount the appraisal supports, the credit already issued on the agreement is nothing, and no transit settlement, no late appraisal allowance, no protection premium and no erasure holdback are counted").
- **O10 — `tradein_ext_revised_offer_amount.baseline.params: [revision_tolerance_pct]`** names a parameter its own `baseline.rule` ("put at the amount the appraisal supports, rounded to the cent") does not use; the baseline reading needs no parameter at all.
- **O11 — realism of two ladder outcomes.**
  (a) `crew_machine_holdback` says "the machines out with the crew are held back at the full crew figure", i.e. the holdback *is* the machines out with the crew, but the figure is a flat 4 or 2 that counts nothing; the record it reads (`service_events.service_visit_consume`) is a visit count, not a machine count.
  (b) `booked_device_share` tier 2 reduces the offer by `devices_declared / devices_booked_in` when **more** machines arrive than were declared. A retailer that receives more machines than the request declared does not publish a *smaller* offer for that reason; base `tradein_device_logistics` says the agreement is appraised on the units actually received.
  (c) `member_collection_relief` compares a count of `membership_benefit_redeem` rows of any `benefit_code` with `free_haul_away_per_year`, i.e. a count of benefit redemptions against an allowance of hauls; the compute applies no `benefit_code` filter.

### findings

Each finding names the tasks it bears on; the demonstration of what it costs a task is in that task's file.

**F1 — SOURCE-POLICY RED: undeclared override of base `tradein_quote_acceptance` S5 by `tradein_ext_refresh_wave_units`.** (bears on the task whose tree is rooted at `tradein_ext_refresh_wave_units`)
- symptom: two clauses of the merged charter decide the same quantity — how many machines may be collected on a business agreement — and reach different figures.
- root cause: the `overwrite` block of `tradein_ext_refresh_wave_units` names base S4 (the linked-purchase window, inert on this programme) and not base S5, which is the sentence that actually governs the quantity.
- evidence: base `blueprint/products/tradein.yaml` `tradein_quote_acceptance.rule` last sentence — "A business agreement is accepted only once the signed asset list the programme requires is on file, and the units on the list govern what may be collected." Extended `tradein.extended.yaml:2497` `replaced_by` — "The machines a wave carries are the machines the schedule covers, capped at the machines the programme's transit cover will bear, less the machines a live return authorisation holds back, …". Programme parameters: `business_asset_list_required: True`, entry gate `asset_list_filed: True` for Renew Bulk IT Refresh Agreement.
- consequence: an agent that applies base S5 declares the units on the asset list; an agent that applies the extended rule declares the capped figure less three holdbacks. Two defensible figures for the scored `units_declared`. Demonstrated with both numbers in `1.md`.
- affected artifact: `tasks/trade_in_appraisal_desk/tradein.extended.yaml:2490-2499` (`overwrite`), and the scored parameter `units_declared`.

**F2 — SOURCE-POLICY: inherited base `tradein_credit_issue_rules` S5 ("the credit is issued once for the batch") against a second `tradein_credit_issue` row on the same batch.** (bears on the batch-credit task)
- symptom: the charter both forbids and requires a second credit row on one batch.
- root cause: `tradein_ext_batch_settlement_credit` declares only S1 superseded; its `interim_credit_recovery` factor exists precisely to net off a credit already issued on the same agreement, which presupposes crediting the batch twice.
- evidence: base "A business agreement is credited by invoice credit or bank transfer only, and the credit is issued once for the batch rather than device by device." Extended rule: "The credit already issued on the agreement is read from the trade-in history and taken off, so that a batch is never paid for twice." Tool `credit_batch_settlement_af2cb6f5` creates another `event_type="tradein_credit_issue"` row.
- consequence: on a world that already carries a `tradein_credit_issue` row for the batch, base S5 says the batch has had its one credit and extended says to issue the difference. Demonstrated in `1.md`.
- affected artifact: `tradein.extended.yaml` `tradein_ext_batch_settlement_credit.overwrite` (S5 not named), `task_tools.py:139-182`.

**F3 — SOURCE-POLICY RED: `booked_share` prorates a fact base `tradein_device_logistics` S6 has already settled.** (bears on the revised-offer task)
- symptom: the short-shipment fact is charged to the customer twice, with no override declared and with `tradein_device_logistics` not even in this policy's `base_policy_refs`.
- root cause: the deviation hides in an intermediate binding (`booked_share`) under no new parameter name — the anonymous-intermediate form of an undeclared override.
- evidence: base `tradein_device_logistics.rule` — "A shipment arriving with fewer units than the request declared is booked in at the units actually received, and the agreement is appraised on those." Extended `tradein_ext_revised_offer_amount.rule` — "Where fewer devices were booked in than the shipment request declared, the offer is taken at the share the devices booked in bear of the devices the request declared", implemented as `result: RND(MX(0, offer_before_share * booked_share * (1 - ageing_markdown_pct / 100)), 2)`.
- consequence: if the appraisal is already "on those" units received, the offer is the tolerance-treated figure; the extended rule multiplies it by `booked/declared` again. Two defensible figures, both computed in `1.md`.
- affected artifact: `tradein.extended.yaml` `tradein_ext_revised_offer_amount` (`overwrite`, `compute.booked_share`, factor `booked_device_share`).

**F4 — SOURCE-POLICY RED: `tradein_ext_collection_handover_units` does not state the grouping of its own operations, and defines its result twice.** (bears on the collection task)
- symptom: the rule yields more than one figure for the scored quantity.
- root cause: two sentences each define "the machines that may go", and no sentence orders the lift share against the holdbacks; `compute_basis.result` quotes only the baseline sentence.
- evidence: rule, paragraph 5 — "the machines that may go are taken at the spot share of the run, rounded down to a whole machine"; rule, final paragraph — "The machines that may go are the capped figure less the machines held back for a claim and the machines out with a service crew, and never fewer than none." Compute: `result: "int(collectable_units * run_fill_pct / 100)"`.
- consequence: three readings — share after holdbacks, share before holdbacks, and the final paragraph taken as the definition (no share at all). All three numbers are given in `0.md`.
- affected artifact: `tradein.extended.yaml:1683-1712` (`rule`), `compute_basis.result`.

**F5 — SOURCE-POLICY (observation-strength on these two worlds): "the credit is owed as soon as the amount settled stands on the records" against the inherited decision-days regime.** (bears on the batch-credit task)
- evidence: extended `tradein_ext_batch_settlement_credit.rule` sentence 1; base `tradein_revision_and_decline` — "A revised offer is refused by the customer only within the decision days of the programme" and "Where the programme takes silence as acceptance and the decision days run out with no answer, the revised offer is credited"; `auto_accept_on_silence: True`, `customer_decision_days: 14` (Business Asset Buyback) and `21` (Bulk IT Refresh).
- consequence: on a world where the customer has not answered the revised offer, base makes crediting due only when the decision days run out — a wait of up to 14 or 21 days — while the extended rule credits at once. Whether that bites depends on whether the persona answers in session; assessed in `1.md`.

**F6 — SOURCE-POLICY RED: base `tradein_data_sanitisation` forbids closing a business agreement out while any serial lacks an erasure certificate; `tradein_ext_batch_settlement_credit` closes it out with a per-device holdback instead.** (bears on the batch-credit task)
- symptom: the charter both forbids and prices the same act.
- root cause: base `tradein_data_sanitisation` appears in no `base_policy_refs` and in no `overwrite`, yet the extended policy's `erasure_certificate_holdback` factor is built on the case that base rules out.
- evidence: base `tradein_data_sanitisation.rule` — "Where the programme issues an erasure certificate it is issued to the customer with the reference recorded, and **a business agreement is not closed out until every serial on the asset list carries one**." `wipe_certificate_issued: True` on both business programmes. Extended rule — "Where the data on the batch stands pending and fewer erasure certificates stand recorded on the agreement than the devices booked in, the uncertified device holdback is held back for each device booked in without a certificate." Tool `credit_batch_settlement_af2cb6f5` sets `status="credited"`, which is closing out.
- consequence: on a world with fewer certificates than devices, base says the agreement may not be closed out at all today (and this difficulty exposes no tool that certifies an erasure, although `tradein_data_wipe_certify` is inside the claimed event types), while the extended policy credits and holds back. Act-now versus cannot-act. Demonstrated in `1.md`.
- affected artifact: `tradein.extended.yaml` `tradein_ext_batch_settlement_credit` (`base_policy_refs`, `overwrite`, factor `erasure_certificate_holdback`), `task_tools.py:171`.

**F7 — SOURCE-CHAIN: the `consented_units` prerequisite sentence is satisfiable by a seeded record.** (bears on the collection task)
- evidence: `policy_source` "The collection charge is fixed only after the machines the customer consents to hand over stand on a shipment request for a freight collection."; gate binding `consented_units: LATEST('tradein_shipping_requests','units_declared', date_field='created_at')`.
- consequence: any world that seeds a `tradein_shipping_requests` row with `customer_consent='consented_by_customer'` and `requested_shipment_method='freight_collection'` on the target agreement already satisfies the sentence; the gate then takes that row's `units_declared` and the customer-owned write is never needed. The row, the two figures and the collapse of the tree are shown in `0.md`.

**F8 — seed/base consistency of a recorded appraisal** (bears on the revised-offer task): base `tradein_appraisal_grading` fixes "the amount the appraisal supports" as `quoted_amount × condition ladder %`; whether a task's `appraised_amount` is a figure that ladder can produce for its `appraised_condition` is checked in that task's file.

**F9 — SOURCE-POLICY (observation-strength at charter level): the two `owner=user` writes are indistinguishable in effect, and the freight-charge policy's scope is delimited only by a programme's prose name.**
- evidence: `task_tools.py:11-51` vs `task_tools.py:185-221` — same signature, same created row, same field values; both policies carry `subject: [tradein_quote_accept]`, `computes: units_declared`, `base_policy_refs: [tradein_quote_acceptance]`. `tradein_ext_collection_freight_charge.rule` sentence 1 — "A palletised collection on a business buyback is charged to the profile when the run is booked" — with `trigger: on_request`, while Renew Bulk IT Refresh Agreement is a business trade-in programme with `shipment_methods_allowed: freight collection only` and `freight_fee_usd: 245.0`.
- consequence: the only discriminators an agent has are the words "business buyback"/"run" versus "refresh schedule"/"wave". Where a task's world holds agreements of both programmes, the tool choice and the question whether a collection charge is also due are settled by vocabulary alone. Assessed per task.

**F10, F11, F12, F13** — stated in full under `factor_ladders` above (unreal ladder with two identical tiers; a `method` label on a rate; an unreachable tier plus a scope-restating conjunct; a baseline that yields no definite number). All four are SOURCE-FACTOR REDs at charter level; F10 additionally drops its policy below the `method` floor and F13 additionally leaves `baseline.params` naming keys the baseline does not use.

**Observations** (no consequence demonstrable from the four relationships): O1 per-machine "handling" against a programme whose `handling_fee_usd` is 0.0 and whose waiver figure is 0.0; O2 `credit_expiry_date` never written although base requires it at issue; O3 the wave edge's `effect` justifies the gate by a quantity no binding reads; O4 `settlement_method` left a two-way choice by base ("invoice credit or bank transfer only") and narrowed by no policy; O5 `cover_units` tiers do not partition their domain; O6 `order_holdback` selects tier 2 where the rule states tier 3 when no fulfilled order exists; O7 the handover-units `overwrite` supersedes the asset-list gate wholesale; O8 the refresh-wave `overwrite` supersedes a clause its replacement does not contradict; O9 `booked_device_share` label; O10 `revised_offer_amount.baseline.params`; O11 three ladder-realism points.

## closing_checklist

**This difficulty does not close out.** Step 4's checklist is written below as it actually stands; the closing conditions require all four relationships to PASS on every task, and they do not.

Per-task verdicts (details in the task files):

| task | policy self-consistency | problem tree | factors bear weight | unique solution |
| --- | --- | --- | --- | --- |
| 0 | **SOURCE-POLICY RED** (0-F1) | **SOURCE-CHAIN RED** (0-F2) | **SOURCE-FACTOR RED** (0-F3, 0-F4) | **SOURCE-TASK RED** (0-F1, 0-F2) |
| 1 | **SOURCE-POLICY RED** (1-F1, 1-F2, 1-F3) | PASS | **SOURCE-FACTOR RED** (1-F6, 1-F7, 1-F8) | **SOURCE-TASK RED** (1-F1, 1-F2, 1-F3) |

What does hold:
- the audit files correspond one-to-one with the two tasks (`0.md`, `1.md`) and `_difficulty.md` sits alongside them; this is revision 1, so there is no older revision to preserve; every task file carries a frozen `source_derivation_frozen` written before any reveal and a `source_gt_comparison` written after both freezes;
- both scored solutions were reproduced independently, figure for figure: task 0's 12 and 240.00 with baselines 34 and 238.50 and ten factor sensitivities; task 1's 4299.43, 3819.43 and 5 with baselines 5100.00, 5100.00 and 46 and fourteen factor sensitivities. No arithmetic error was found anywhere in `computations`, `factor_sensitivity`, `baseline_result`, `edge_load_bearing` or `argument_uniqueness_tracing`;
- the five extended policies are fully covered by the two tasks with pairwise disjoint scopes at the level of policy ids and tools (task 0: `…handover_units`, `…freight_charge`; task 1: `…revised_offer_amount`, `…batch_settlement_credit`, `…refresh_wave_units`), and the base section is byte-identical to the blueprint product;
- the `prerequisite` edges of the whole difficulty form two disjoint chains and remain a DAG; no cross-task reference creates a cycle; each task has one to three prerequisite problems (1 and 2), at least max(n−1,1) `value_input` edges (1 and 1), and at least one problem resolved by an `owner=user` tool;
- every task tool carries an independently generated, frozen, unreused uuid8, and no tool judges an eligibility or a prerequisite;
- every one of the 24 declared factors moves its scored number on its own task's world, and every `baseline` binding is the value that factor's own baseline sentence states — the factor failures are about ladder reality, labels and one non-self-sufficient baseline, not about weight.

What blocks the close-out:
- the charter admits a second reading of a scored argument in both tasks (F1/0-F1, F1/1-F1, F3, F6, F7 with their per-task demonstrations);
- task 0's only prerequisite edge is satisfiable by a seeded record on the wording the KB will carry, which removes the tree, the `value_input` floor and the customer-owned write from that task;
- two ladders are unreal (a duplicated tier, an unreachable tier), one `method` label substitutes a rate, and one computation's baseline yields no definite number.

Instantiation-stage gates on the final form: the artefacts are byte-for-byte the ones the brief's snapshot was taken on (`tradein.extended.yaml` sha256_16 `3e2ef593a265f3af`, `task_tools.py` sha256_16 `ba59e057f4f298b4`, and the two task files' hashes as recorded in the masking report), and nothing in this audit changed them, so that snapshot — `check_extended`, `check_task_tools`, `replay_tasks`, `check_solvability`, `check_compute`, `check_grounding`, `check_cross_fire` all green, `check_traceability` deferred to the render step — stands for the final form as it is now. It is cited, not re-run: none of the findings above is of a kind those gates test, which is the point of the manual pass.

## revision_2

Re-audit of the reworked difficulty, 2026-09-18 10:18 UTC, by the auditor who produced revision 1. This is a verification round, not a fresh blind derivation: revision 1's frozen derivations and quoted evidence are the baseline, and each item below is judged against the amended artifacts.

### re_derivation_grounds

All four artifacts moved, so nothing is carried forward by hash and every charter-level conclusion below was re-derived:

| artifact | revision 1 sha256_16 | revision 2 sha256_16 |
| --- | --- | --- |
| `tradein.extended.yaml` | `3e2ef593a265f3af` | `f5d251360dc12ae0` |
| `task_tools.py` | `ba59e057f4f298b4` | `45fbe2eeaab3eb4f` |
| `tasks/0.json` | `7ad195dfff382a62` | `f9892daddb3d8f21` |
| `tasks/1.json` | `4e9fb2501c00f3b9` | `c3a4ba1339e84849` |

Gates cited from the coordinator's snapshot, not re-run: `check_extended`, `check_task_tools`, `check_solvability`, `check_compute`, `check_grounding`, `check_cross_fire` and `replay --check` all green; `check_traceability` still deferred to the render step. Base-section closure re-verified mechanically: the extended file's text up to `extended_policies:` is still byte-identical to `blueprint/products/tradein.yaml` (both 80074 bytes). The five policy ids, the five `(target_tool, computes)` pairs and the five uuid8s (`5801b6db`, `530ef4f1`, `f86761c2`, `af2cb6f5`, `923c3678`) are unchanged, still distinct and still unreused.

Factor structure after the rework (recounted): handover_units 4 (3 parameter / 1 method), freight_charge 6 (5/1), revised_offer 4 (2/2), batch_credit 6 (5/1), refresh_wave 4 (3/1). Every policy is inside 4–6 with ≥2 `parameter` and ≥1 `method`. Cross-difficulty: protection+service, orders+membership, protection, protection, returns+orders+credit.

All ten `overwrite` entries were checked mechanically against the base rules: every `superseded_clause` is a **verbatim** fragment of the cited base policy's `rule`, and every cited base policy appears in that policy's `base_policy_refs`. Every one of them names a clause that is **actually in force** on the programme concerned — the revision-1 defect of aiming an override at an inert clause is gone. Two structural improvements worth recording: the handover-units override was narrowed from the whole base sentence to "the units on the list govern what may be collected", so the asset-list gate is inherited again (closes O7); and the refresh-wave override now names that same fragment instead of the inert linked-purchase window (closes O8, and is the charter half of 1-F1).

### revision_2_item_verdicts (charter-global items)

| item (rev 1) | claim | verdict |
| --- | --- | --- |
| F1 — undeclared override of `tradein_quote_acceptance` S5 | declared correctly instead of the inert clause | **CLOSED** — verbatim, in force, aimed at the quantity |
| F2 — "credit issued once for the batch" | declared superseded | **CLOSED** |
| F3 — `booked_share` prorating a fact base settled | removed on the merits | **CLOSED** — the binding, the factor and the sentence are all gone; the shortfall is settled once, in the credit's transit settlement |
| F4 — grouping not stated (units) | ordering paragraph added, second definition deleted | **CLOSED** |
| F5 — "credit owed as soon as" vs the decision-days regime | answered, no change | **ANSWERED, still an observation** — the argument is sound on the evidence: the persona answers the revised offer in session, so no wait arises and no consequence is demonstrable |
| F6 — base `tradein_data_sanitisation` forbidding close-out | added to `base_policy_refs`, clause declared superseded | **CLOSED** |
| F7 — prerequisite sentence satisfiable by a seeded record | closed in the world | **CLOSED** — see `0.md` § revision_2 for the mechanical demonstration |
| F8 — seeded appraisal not producible by base's ladder | declared superseded | **CLOSED** |
| F9 — the two `owner=user` tools behaviourally identical | tools now differ; rules state programme and state scope | **CLOSED behaviourally** — `confirm_handover_units_5801b6db` creates the request **and** sets `tradein_agreements.shipment_method='freight_collection'`; `confirm_refresh_wave_units_923c3678` moves the schedule `quoted → accepted` with `accepted_date` **and** creates the request. Different columns, different returns, different state scopes in the docstrings ("a Renew trade-in agreement already accepted" vs "a quoted Renew refresh schedule"). The scope halves are closed too: the freight-charge rule says outright that "a collection on any other Renew programme, and a batch already booked in, carry no collection charge under this rule", and the wave rule that "a wave carries no collection charge of its own" |
| F10 — one tier written as two (`settled_figure_basis`) | three distinct outcomes | **CLOSED** — the ladder now partitions by the count of revisions standing (more than one → `MAX`, exactly one → `LATEST`, none → the appraisal), and the compute forks three ways. Observation only: tier 2 is the singleton case of tier 1 and coincides with it in value whenever it fires |
| F11 — `run_lift_share` mislabelled `method` | relabelled `parameter` | **CLOSED** — and the ladder now names a share ("the share the run lifts is the spot share") rather than redefining the result; the policy keeps one honest `method` (`claim_holdback_basis`) |
| F12 — `machine_handling_rate`'s dead tier | tier evidence replaced | **CLOSED** — the ladder now turns on whether the run finishes the batch (`machines_consented_before`), and all three tiers are reachable |
| F13 — non-self-sufficient baseline (refresh wave) | baseline now yields a definite number | **CLOSED** — `baseline.rule` states its defaults outright ("The machines the programme's transit cover will bear are the machines the schedule covers, and no machines are held back …"), `baseline.params` is now `[]`, and 46 is derivable from the sentence alone |
| O1 — per-machine handling against a programme fee of 0.00 | closed by declaring an override | **NOT CLOSED — regressed into a red light.** See finding R1 below |
| O2 — `credit_expiry_date` never written | closed | **CLOSED** — the credit tool now takes and writes `credit_expiry_date`, and the rule states how it is derived |
| O3 — the wave edge's `effect` naming a mechanism that does not exist | closed | **CLOSED** — the `effect` now says plainly that no figure moves and the edge carries the eligibility |
| O4 — `settlement_method` a two-way choice | closed | **CLOSED** — the persona now answers when the agent asks, not only after the write |
| O5 — `cover_units` tiers not partitioning | closed | **CLOSED** — four tiers, exhaustive over `value_each` vs cover, the whole schedule vs cover and the quote's age |
| O6 — `order_holdback` fall-through unreachable | closed | **CLOSED** — `days_since_fulfilled` now falls back to `'1900-01-01'`, so no fulfilled order gives the fall-through |
| O7, O8 — override aimed too wide / at an inert clause | closed | **CLOSED** (see above) |
| O9 — `booked_device_share` label | closed by deletion | **CLOSED** |
| O10 — `revised_offer.baseline.params` naming an unused key | closed | **CLOSED** — now `[]`, and the baseline needs no parameter |
| O11 — three ladder-realism points | closed | **(a) CLOSED** (the crew holdback is now named for what it is, and the persona states no machine count); **(b) CLOSED** by deleting the factor; **(c) CLOSED** in substance — the rule now says "haul-away credits", the compute filters `benefit_code='haul_away_credit'`, and a new `install_credit` redemption sits in the seed as the near-miss. Residual wording nit in R4 below |

### revision_2_findings (new this round)

**R1 — SOURCE-POLICY RED (new, task 0): the override that was meant to close O1 licenses the charge and then fixes its rate at zero.**
- symptom: one policy's `rule` gives two different sources for the per-machine handling, and the two give different charges.
- root cause: the replacement text supplied with the new `overwrite` entry names the programme's mailed-in handling fee as the rate, while the ladder that follows names three constants of its own.
- evidence, all in `tradein_ext_collection_freight_charge`: `overwrite[0].replaced_by` and the rule sentence — "The handling charged for each machine on a palletised collection is charged **whatever handling fee the programme sets for a mailed-in device**, and no waiver figure stands against it." Renew Business Asset Buyback sets `handling_fee_usd: 0.0` (and `handling_fee_waived_above_usd: 0.0`). The next sentences instead say "What it comes to follows the size of the load and whether the run finishes the batch", with `short_load_handling_usd: 3.5`, `clearing_load_handling_usd: 2.4`, `standard_handling_usd: 1.1`, and the compute uses those constants.
- demonstrated consequence: on task 0's world the ladder gives 240.00; reading the override sentence as written gives `65.00 × 2.0 + 0.00 × 12 + 85.00 + 38.00 − 55.00 = 198.00`. Revision 1 recorded 198.00 as an observation because base's sentence spoke only of a mailed-in device; the rework has moved that rival reading **inside the extended rule**, where it applies to a palletised collection directly, so it is now a conflict between two sentences of one policy about one quantity.
- affected artifact: `tasks/trade_in_appraisal_desk/tradein.extended.yaml`, `tradein_ext_collection_freight_charge.overwrite[0].replaced_by` and the corresponding rule sentence; scored argument `handling_fee_amount`.
- relation to previous revisions: revision 1 finding 0-O1 / `_difficulty.md` O1, raised as an observation, now a red light.

**R2 — SOURCE-FACTOR RED (new, task 0): the state-scope sentences added to both of task 0's policies kill a tier in each of their ladders, one of which is also the declared baseline.**
- symptom: a tier whose condition no world within the policy's own scope can satisfy — the mirror image of revision 1's F12, reintroduced elsewhere by the fix for F9.
- root cause: each policy now states that it applies only while no machines have been booked in, while a tier of its own ladder is conditioned on machines having been booked in.
- evidence:
  - `tradein_ext_collection_handover_units.rule`: "The machines of a run are settled only while the agreement is still waiting for machines to be collected **and none has been booked in on it**." Against `carrier_batch_allowance` tier 3: "otherwise, **a shipment has already been booked in on the agreement**" → `K('slot_units_full')`. Both map to the one binding `shipment_booked_in: "1 if F('device_received_date') else 0"`.
  - `tradein_ext_collection_freight_charge.rule`: "… that is while the agreement is still waiting for machines to be collected and none has been booked in on it; a collection on any other Renew programme, **and a batch already booked in, carry no collection charge under this rule**." Against `short_notice_spot_premium` tier 2: "the collection is asked for within the programme's pickup lead days **and a shipment has already been booked in on the agreement**" → `K('repeat_spot_premium_usd')`.
- demonstrated consequence: in each ladder one of three tiers can never fire, so the reachable ladder is two tiers against a floor of three, and in tiers 1 and 2 of `carrier_batch_allowance` and tier 1 of `short_notice_spot_premium` the conjunct "no shipment has been booked in on the agreement" holds of every customer who reaches the write and divides nobody. In `carrier_batch_allowance` the dead tier is the fall-through, and the fall-through is the declared baseline (`batch_allowance: K('slot_units_full')` = 40, the "full batch allowance" of `baseline.rule`) — so the baseline every document reader is meant to start from is a treatment no customer of this policy can receive. Neither dead tier changes task 0's scored figures (its world has `device_received_date` empty, so tier 1 fires in both, as gold has it): the damage is to the ladders and to the baseline, not to the numbers.
- affected artifact: `tradein.extended.yaml`, `tradein_ext_collection_handover_units.rule` + factor `carrier_batch_allowance`; `tradein_ext_collection_freight_charge.rule` + factor `short_notice_spot_premium`.
- relation to previous revisions: same class as revision 1 F12, which was red-lighted and accepted; introduced by the revision-2 fix for F9's scope half.

**R3 — SOURCE-FACTOR RED (new, task 1): the new cross-difficulty factor's middle tier needs a protection record the protection charter forbids.**
- symptom: `cover_transfer_deduction` tier 2 can only fire on a world that contradicts another product's own charter, so the reachable ladder is two tiers.
- root cause: the tier conditions a deduction on a plan that stands **active** while its cover **had already ended** before the appraisal.
- evidence: `tradein_ext_revised_offer_amount` factor `cover_transfer_deduction` tier 2 — "the profile holds a protection plan standing active on the batch whose cover may not be transferred and **whose cover had already ended when the appraisal was recorded**" → `K('expired_cover_deduction_usd')`; compute `cover_deduction` second arm requires `cover_not_travelling == 1 and cover_days_left <= 0`, where `cover_not_travelling` requires `EXISTS('protection', status='active')` and `cover_days_left = DAYS(F('appraised_date'), coverage_end_date)`. Against `blueprint/products/protection.yaml`: `protection_plan_expiry` — "A plan expires at the end of its coverage end day" — and the lifecycle transition `{from: active, to: expired, by: system, means: the coverage term ran to its end day}`. Since the appraisal date is in the past, any plan whose cover ended on or before it should stand `expired`, not `active`.
- demonstrated consequence: two reachable tiers against a floor of three. No effect on task 1's scored figure (tier 1 fires: `transferable_flag: false`, `cover_days_left = 512`).
- affected artifact: `tradein.extended.yaml`, `tradein_ext_revised_offer_amount` factor `cover_transfer_deduction` tier 2 and the `cover_deduction` binding.
- relation to previous revisions: new; this factor did not exist in revision 1 (it took the slot freed by deleting `booked_device_share`).

**R4 — observations (new this round, none load-bearing).**
- `member_collection_relief`'s ladder `when` strings still say "fewer **benefit credits** than that have been redeemed", where the amended rule and the compute both now speak of haul-away credits (`benefit_code='haul_away_credit'`); the `cross_category` note likewise still says "the benefit credits already redeemed". The compute and the rule agree, so no figure moves; only the ladder's own wording lags its rule.
- `tradein_ext_collection_freight_charge.inputs.history` still declares `{table: tradein_shipping_requests, aggregate: count, …}`, which no binding performs any more, and does not declare the `SUM` over `units_declared` that `machines_consented_before` now performs.
- `tradein_ext_refresh_wave_units.rule` says "a wave carries no collection charge of its own, the freight on a refresh schedule being carried by the schedule's own contract price book", while Renew Bulk IT Refresh Agreement carries its own `freight_fee_usd: 245.0` in the product parameters. Nothing charges it after the rework, so no figure is in doubt.
- Disclosure of a revision-1 miss, since the baseline for this round is my own earlier text: revision 1's `1.md` § factor_weight asserted that task 1's seeded protection row was "consistent with its own charter". It was not — the row carried `transferable_flag: true` while `ShieldCare Business Fleet Protection` sets `transfer_allowed: False` in `blueprint/products/protection.yaml`. The rework has incidentally corrected it (`transferable_flag: false`), which is also what makes the new cover factor bear weight. The revision-1 sentence stands uncorrected in its own section, as the append-only rule requires; this note is the correction.

### revision_2_regression_check

Re-checked, and unchanged where revision 1 had passed it:
- base section byte-identical to the blueprint product; the base copy has not been rewritten;
- every prerequisite edge's `policy_source` is still verbatim in the blocked policy's own `rule`, still state-form, still with no `fallback_reason` anywhere (correct, since no edge is action-form); the three edges still form two disjoint acyclic chains with no cross-task reference;
- `kind`/`gate` still match (`consented_units` and `settled_amount` are compute bindings; `tradein_agreements.final_credit_amount` is a record field and an eligibility);
- the M tasks' scopes are still pairwise disjoint and jointly complete over the five extended policies, and are now additionally separated by each rule naming its programme by its official name;
- no docstring names another tool or states its place in a sequence; the two new state-scope phrases in the user tools' docstrings ("already accepted", "a quoted Renew refresh schedule") describe the object's state, not a position in a chain;
- no tool judges an eligibility or a prerequisite: the two user tools are still bare `ctx.create`/`ctx.update` pairs with no conditional logic, and the credit tool's new `credit_expiry_date` is taken as an argument rather than computed for the agent.

## closing_checklist (revision_2)

**This difficulty still does not close out**, on three new findings rather than the eleven of revision 1.

| task | policy self-consistency | problem tree | factors bear weight | unique solution |
| --- | --- | --- | --- | --- |
| 0 | **SOURCE-POLICY RED** (R1) | **PASS** (was SOURCE-CHAIN RED; F7 closed) | **SOURCE-FACTOR RED** (R2) | **SOURCE-TASK RED** (R1's 198.00) |
| 1 | **PASS** | **PASS** (held) | **SOURCE-FACTOR RED** (R3) | **PASS** |

What now holds that did not: every scored argument of both tasks is uniquely entailed except task 0's collection charge; task 0's problem tree is genuinely unmet at the opening and its customer-owned write is unskippable; all 24 factors bear weight against honest baselines on their own worlds; every baseline yields a definite number different from gold (34, 230.70, 5100.00, 5100.00, 46); all ten overrides are verbatim and aimed at clauses in force; and the two customer-owned writes are behaviourally distinct.

What blocks the close-out: one policy that names two rates for one quantity (R1), and three ladders whose reachable tiers fall to two because a tier's condition cannot be satisfied inside the policy's own scope or inside another product's charter (R2 ×2, R3). Instantiation-stage gates: cited from the coordinator's snapshot on these exact hashes, all green with `check_traceability` deferred; none of R1–R3 is of a kind those gates test.

## revision_3

Re-audit, 2026-09-18 10:40 UTC, same auditor. Narrow verification round against revision 2's three findings and three nits.

### re_derivation_grounds

| artifact | revision 2 | revision 3 | treatment |
| --- | --- | --- | --- |
| `tradein.extended.yaml` | `f5d251360dc12ae0` | `d28a7b6e2cc95e38` | re-derived in full |
| `task_tools.py` | `45fbe2eeaab3eb4f` | `45fbe2eeaab3eb4f` | **carried forward by reference** — the tool-contract section (`action_binding_and_uuids`, the tool-layer neutrality checks, F9's behavioural half) rests on this file alone and it has not moved |
| masked view `0.json` | `9489e509d3f208bf` | `9489e509d3f208bf` | world-side facts carried forward |
| masked view `1.json` | `7fa92c1ce44ba777` | `7fa92c1ce44ba777` | world-side facts carried forward |

Base section re-verified byte-identical to `blueprint/products/tradein.yaml` (80074 bytes). Gates cited from the coordinator's snapshot on these hashes, all green, `check_traceability` still deferred. Re-derived from the amended charter and unchanged: the five policy ids, the five `(target_tool, computes)` pairs, factor counts 4 / 6 / 4 / 6 / 4 with ≥2 `parameter` and ≥1 `method` each, every ladder at three tiers or more (`transit_cover_wave_basis` at four), all three prerequisite edges state-form with no `fallback_reason`, each `policy_source` **still verbatim in its blocked policy's amended rule** (re-checked, since three of the five rules were edited), each `resolved_by` still the depended-on policy's `target_tool`, and no orphan `compute_basis` key in any policy.

### revision_3_item_verdicts

| item (rev 2) | verdict |
| --- | --- |
| **R1** — the 0-O1 override named a rate its own ladder contradicted | **CLOSED** |
| **R2** — the F9 scope sentences each killed a tier | **PARTIALLY CLOSED** — closed for `short_notice_spot_premium`; **not** closed for `carrier_batch_allowance`, whose middle tier is now dead for a new reason (finding **R5**) |
| **R3** — the cover factor's middle tier needed a state protection forbids | **CLOSED** |
| **R4** — three nits (ladder wording, stale `inputs`, the wave's freight sentence) | **CLOSED** (all three) |

**R1 — CLOSED.** The `replaced_by` now reads "The handling charged for each machine on a palletised collection is neither the programme's handling fee for a mailed-in device nor waived by the programme's waiver figure, and what it comes to is settled by the load alone", and the rule carries that sentence with a colon gloss that hands straight to the ladder: "… settled by the load alone: it follows the size of the load and whether the run finishes the batch …". On the coordinator's question (a) — whether a double negative really leaves exactly one sentence fixing the rate — I read every sentence of the policy that touches the per-machine handling. Three mention it: the result sentence (names the term, no rate), the baseline sentence ("the handling charged for each machine is the standard handling", the default, which is also the ladder's fall-through and therefore has to be in the rule), and the ladder paragraph (short / clearing / standard). **No sentence anywhere now points at `handling_fee_usd` as the rate**, so the 198.00 reading has nothing to rest on. Residual wording observation only: "settled by the load alone" is doing double duty — contrasting with the programme's fee, and naming the load test — and a pedantic reader could take the colon gloss as widening what precedes it. Every reading still lands on the ladder, so no figure is in doubt.

**R2 — PARTIALLY CLOSED.** Both ladders were re-based off new facts while the F9 scope sentences were kept, as claimed, and I tested reachability on constructed worlds inside each policy's own scope rather than in principle:
- `short_notice_spot_premium` (now `runs_asked_for: COUNT('tradein_shipping_requests')` against "how often the carrier has been asked to come") — **closed**. All three tiers fire and compute: two requests at four days' notice → repeat 85.00 (charge 240.00); one request at four days' notice → opening 45.00 (charge 200.00); fourteen days' notice → 0 (charge 155.00). The new conjunct is genuinely *not* guaranteed by the prerequisite: the prerequisite forces at least one request, while the tier turns on **more than one**, and the one-request world computes cleanly. The constants did swap (`spot_premium_usd` 85.0 → 45.0, `repeat_spot_premium_usd` 45.0 → 85.0), which is what preserves the scored 240.00, and the swap is the more realistic of the two orderings on this world's facts — a re-attend after a failed lift costing more than the first call-out.
- `carrier_batch_allowance` (now an unsettled-balance threshold, `restricted_balance_usd: 60.0`, plus whether a request has been taken) — **not closed.** Its fall-through, and therefore the declared baseline, is now genuinely reachable, which was the sharper half of R2: a world with 45.00 outstanding books the full allowance of 40 and the run comes to 20 machines (recomputed). But the middle tier is dead for a new reason: see R5.

**R3 — CLOSED.** The date-based condition is gone; the middle tier is now "a protection plan standing **in claim hold** on the batch whose cover may not be transferred" → `held_cover_deduction_usd: 90.0`, with a stated reason ("a plan whose own claim is still under review may yet pay out on those machines, which leaves less of the cover to lose"). `claim_hold` is in `protection`'s own lifecycle states and carries transitions in both directions, so the tier is reachable in a charter-consistent world; the three outcomes are distinct (220.00 / 90.00 / 0), and I confirmed each fires on a constructed world (revised offer 4822.40 / 4936.80 / 5016.00). For this customer the plan stands `active`, so tier 1 fires deterministically and no two tiers compete.

**R4 — CLOSED, all three.** The `member_collection_relief` ladder's `when` strings and the `cross_category` note now say "haul-away credits", matching the rule and the `benefit_code`-filtered compute. `tradein_ext_collection_freight_charge.inputs.history` now declares exactly what the compute performs — the method-filtered `latest`, the `sum` over `units_declared`, the `count`, the fee `sum` and the membership `count` with its `benefit_code` filter. The wave's freight sentence was reworded rather than deleted, and the rewording is the right one: "a wave carries no collection charge **under this rule**, the freight on a refresh schedule being **charged under the programme's own freight terms and not here**" — which no longer denies the programme's own `freight_fee_usd` while keeping F9's scope exclusion intact and in the same form as the freight-charge policy's.

### revision_3_sweep_spotcheck

The reworker reports a sweep across all five policies. Where I spot-checked it, it holds:

- **baseline versus fall-through, all 24 factors: holds.** Every factor's `baseline[decides]` is the value or method of its own last tier — `K('slot_units_full')`, `K('full_fill_pct')`, `P('freight_fee_usd')`, `K('standard_handling_usd')`, `raw_pallets`, `appraisal_amount`, `devices_on_schedule` and `0` in the remaining sixteen, each matching the prose of the fall-through tier ("no machine is held back on that account", "as they stand", "the amount the appraisal supports as it stands", "the cover bears the machines the schedule covers", "counted as none").
- **cross-product statuses against each product's own enum: holds, 9 of 9.** `service.dispatched`, `service.scheduled`, `protection.active`, `protection.claim_hold`, `returns.authorized`, `returns.received`, `credit.active`, `credit.delinquent`, `orders.fulfilled` are each in that product's `lifecycle.states`.
  **One correction to the reworker's account of its own sweep**: it says this is the check that would have caught R3. It would not. R3's forbidden state used a status that *is* in the enum (`active`) together with a date condition that protection's `protection_plan_expiry` rule and its `active → expired` transition forbid. The check that catches R3 is a tier's required cross-product state against that product's **rules and lifecycle transitions**, not against its status enum. The new tier is sound, but it is sound by a wider check than the one claimed, so the class is not yet swept by the process as described.
- **`overwrite.replaced_by` naming a rate: holds.** All ten entries re-verified verbatim against their base rules, and only one replacement contains any rate word at all — the R1 fix itself, where the words appear inside a negation that retires them.
- **pairwise rate consistency within each policy: holds.** Every one of the 42 `params` keys across the five policies is referenced by exactly one compute binding, so no quantity in any policy has two parameter sources — the R1 pattern cannot recur through a parameter.
- **the "booked in" token check: holds where it matters.** The two policies whose scope sentences say "none has been booked in" (`…handover_units`, `…freight_charge`) now have no ladder tier mentioning "booked in" at all. The phrase does occur in tiers of `…revised_offer_amount` and `…batch_settlement_credit`, which is correct: those policies act on a batch that has been received and appraised, so there is no scope contradiction to find.

### revision_3_findings

**R5 — SOURCE-FACTOR RED (new root cause; R2's `carrier_batch_allowance` half): the tier named for a first run cannot be computed on a first run, because another binding of the same policy insists a shipment request already exists.**
- symptom: one of three tiers can never be the tier that fires on any world the policy can evaluate at all.
- root cause: `carrier_batch_allowance` tier 2 requires `requests_taken < 1` — no shipment request on the agreement — while the same policy's `notice_days` reads the collection day off a shipment request on that same agreement, agreement-scoped and unfiltered.
- evidence, both in `tradein_ext_collection_handover_units`: rule — "Where those charges stand above the restricted balance and **no shipment request has yet been taken on the agreement**, the carrier books the opening batch allowance"; compute — `requests_taken: "COUNT('tradein_shipping_requests')"` and `notice_days: "DAYS(NOW, LATEST('tradein_shipping_requests','requested_collection_date', date_field='created_at'))"`, with `run_fill_pct` reading `notice_days`. `LATEST` returns `None` when the agreement carries no request, and `DAYS` raises on it.
- demonstrated consequence: I emptied `tradein_shipping_requests` for the target agreement, leaving everything else as seeded and the agreement still awaiting its machines, and evaluated the policy's own compute: `requests_taken = 0` selects the opening allowance, and the policy then raises on `notice_days` before reaching a result. So `K('slot_units_opening')` = 30 is unreachable on any scorable world, and the reachable ladder is two tiers (24 and 40) against a floor of three. The same fact has a wider consequence worth stating once: because a shipment request on this charter is created by this policy's *own* target tool, the policy is computable only from an agreement's **second** run onward, while its opening sentence — "A Renew Business Asset Buyback agreement is collected in runs, and the machines one run carries are settled with the customer before the customer consents to the handover" — reads on the first run too. In that sense the rule also makes a promise the compute cannot keep, which is the check-2 face of the same defect; I record it once, under the factors relationship, as revision 2 recorded R2.
- not affected: task 0's scored figures. Its world carries the courier request, so tier 1 fires and `units_declared` is 12 and the charge 240.00, exactly as gold has them.
- affected artifact: `tasks/trade_in_appraisal_desk/tradein.extended.yaml`, `tradein_ext_collection_handover_units` — the `batch_allowance` tier 2 sentence, the `requests_taken` binding and the `notice_days` binding.
- relation to previous revisions: this is R2's `carrier_batch_allowance` half, not closed. Revision 2's root cause (the tier conditioned on machines being booked in, which the scope sentence forbade) is genuinely gone; the tier is now dead through a different pair of bindings in the same policy.

**Observations (new this round, none load-bearing).** "Settled by the load alone" carries two jobs in one clause (R1 above). `cover_travels: "1 if CFIELD('protection','transferable_flag') == True else 0"` reads any protection holding of the profile, while the rule says "a protection plan standing active **on the batch**"; with one plan seeded, whose `covered_item_serial` is the batch's serial, the two agree on both tasks' worlds, and the narrowing is invisible only because no world here holds two plans — this predates revision 3 and was masked in revision 2 by the date conjunct that has since gone. The R3 fix also narrowed that factor's evidence to `[cross_category]` alone, dropping the date conjunct that made it multi-source; each task still carries a multi-source factor elsewhere (`offer_ageing_markdown`, `transit_shortfall_settlement`, `erasure_certificate_holdback` in task 1), so no floor is breached.

### revision_3_regression_check

Nothing regressed. Re-verified on the amended charter: the ordering paragraph and the deleted second definition of the units quantity (0-F1/F4) survive word for word; the freight-charge scope exclusion survives; the revised-offer ordering paragraph, the recorded-appraisal override and the sanitisation override survive; the credit-expiry sentence and the three-way `settled_figure_basis` ladder survive; the wave baseline's stated defaults survive. Every scored figure and every baseline recomputed identical to revision 2: `units_declared` 12, `handling_fee_amount` 240.00, `revised_amount` 4822.40, `final_credit_amount` 4342.40, `credit_expiry_date` 2026-12-17, `units_declared` 5; whole baselines 34, 230.70, 5100.00, 5100.00, 46; all 24 per-factor baselines unchanged to the cent. Every world-assertion in the amended proof fields was recomputed and holds, including the two new counterfactuals the artifact volunteers ("a first run asked for at the same notice would carry the opening spot premium of 45.00" — confirmed, 45.00; "a plan standing in claim hold would carry the held cover deduction of 90.00" — confirmed, 90.00, offer 4936.80).

## closing_checklist (revision_3)

**One finding from closing out.**

| task | policy self-consistency | problem tree | factors bear weight | unique solution |
| --- | --- | --- | --- | --- |
| 0 | **PASS** | **PASS** | **SOURCE-FACTOR RED** (R5) | **PASS** |
| 1 | **PASS** | **PASS** | **PASS** | **PASS** |

Task 1 passes all four relationships. Task 0 passes three: its charter is self-consistent, its problem tree is genuinely unmet at the opening with an unskippable customer-owned write, and both of its scored arguments are uniquely entailed — the single remaining defect is one unreachable tier in one ladder, which costs no figure on this world. Everything the closing checklist asks for now holds except that: per-task files one to one with the tasks, old revisions preserved, scopes pairwise disjoint and jointly complete, uuid8s independently generated and frozen (tool module unchanged since revision 2), trees within one to three prerequisite problems with the `value_input` floor met and an `owner=user` write in each, the whole `prerequisite` graph acyclic, every computation on a self-sufficient baseline with four to six factors and every factor bearing weight against an honest baseline, and the instantiation gates green on these exact hashes with `check_traceability` deferred to the render step.

## revision_4

Re-audit, 2026-09-18 11:00 UTC, same auditor. One finding to verify (R5), plus confirmation that nothing regressed.

### re_derivation_grounds

| artifact | revision 3 | revision 4 | treatment |
| --- | --- | --- | --- |
| `tradein.extended.yaml` | `d28a7b6e2cc95e38` | `95909f62c6bcf440` | re-derived in full |
| `task_tools.py` | `45fbe2eeaab3eb4f` | `45fbe2eeaab3eb4f` | **carried forward by hash** — the tool-contract section, the uuid8s and F9's behavioural half rest on this file alone |
| masked view `0.json` | `9489e509d3f208bf` | `9b398f590ba21852` | task 0's world re-derived |
| masked view `1.json` | `7fa92c1ce44ba777` | `7fa92c1ce44ba777` | task 1's world-side facts carried forward |

Base section re-verified byte-identical to `blueprint/products/tradein.yaml`. Gates cited from the coordinator's snapshot on these hashes, all green, `check_traceability` deferred. Re-derived on the amended charter and unchanged: all ten `overwrite` entries verbatim in their cited base rule and each cited policy in `base_policy_refs`; all three prerequisite edges state-form, no `fallback_reason`, each `policy_source` still verbatim in its blocked policy's amended rule, each `resolved_by` still the depended-on `target_tool`; factor counts 4 / 6 / 4 / 6 / 4 with ≥2 `parameter` and ≥1 `method`; every ladder at three tiers or more; `baseline` equal to its own fall-through for all 24 factors; no orphan `compute_basis` key.

### R5 — CLOSED, at the root

The fix is the one the finding named: the policy no longer reads a row its own tool creates. `run_fill_pct` now reads `quote_days_left: "DAYS(NOW, F('quote_expiry_date'))"` — an agreement field every agreement carries from the moment it is quoted — and the rule states it as "the room the run has left on the quote, counted in calendar days from the day the units are settled to the last day the quote may be accepted". I checked the charter for every remaining read of `tradein_shipping_requests`: in `tradein_ext_collection_handover_units` there is now exactly one, `requests_taken: "COUNT('tradein_shipping_requests')"`, and `COUNT` returns 0 rather than raising.

**The decisive test, run as I ran it when I found R5**: emptying the request table for the target agreement and leaving the rest of the seeded world alone, the policy now **returns**, where in revision 3 it raised. `requests_taken = 0` → the opening batch allowance of 30 → `30 − 3 − 4 = 23` → `int(23 × 0.75) = **17**` machines — the figure the reworker reported, reproduced independently. The seeded world still returns 12. So the tier that was dead is now the tier of a scorable world, and the policy is computable on a first run, which was the wider form of the defect.

### revision_4_sweep_spotcheck

**Sweep 1 — scorable-world tier reachability.** I did not accept the reported tables; I built worlds myself and required each tier both to fire and to produce a result. **44 tiers across all five policies, all 44 fire and return**: policy 1 all 12 (including the three of `carrier_batch_allowance` at 24 / 30 / 40 giving 12 / 17 / 20, and the three of `run_lift_share` at 75 / 90 / 100 giving 12 / 15 / 17 off quote expiries three, ten and twenty-five days out); policy 2 twelve (including `machine_handling_rate` at 3.50 / 2.40 / 1.10 and `short_notice_spot_premium` at 85.00 / 45.00 / 0); policy 3 ten; policy 4 twelve; policy 5 ten (including the four-tier cover ladder at 1 / 0 / 12 / 46). One tier failed my first attempt — `offer_ageing_markdown`'s middle tier — and the cause was my own world, which left the ageing anchored on the quote day; rebuilt with the receipt inside the quote's validity it fires at 6 per cent. I record that as my error, not the charter's.
- **The two dependency-constrained reads are legitimate, and for the reason claimed.** `tradein_ext_collection_freight_charge` raises if no freight-collection request stands — which is exactly what its own prerequisite forbids — and none of its tiers asks for zero requests (`short_notice_spot_premium`'s middle tier needs *no more than one*, which one satisfies; I confirmed the one-request world returns 200.00). `tradein_ext_batch_settlement_credit` raises if no request stands on the appraised batch — a world the base gates exclude, since a batch cannot stand appraised without having been booked in against a request — and all three `transit_shortfall_settlement` tiers presuppose a request rather than its absence. That is the distinction R5 turned on, and it holds: no tier of either policy asks for the absence of what its own policy needs.

**Sweep 2 — cross-product states in the rules-and-transitions form.** Holds where I checked it. Each of the nine states a ladder requires is not merely in its product's enum but has an inbound lifecycle transition and can persist at handling time: `protection.active` (in from `application_received` and from `claim_hold`), `protection.claim_hold` (in from `active` by agent, out to active / expired / cancelled — which is what makes R3's replacement tier reachable), `returns.authorized`, `returns.received`, `credit.active`, `credit.delinquent` (in from `active` by system), `service.dispatched`, `service.scheduled`, and `orders.fulfilled` (terminal, so it persists by construction).
- The observation it reports closing in passing is genuinely closed: `cover_travels` and both `EXISTS` calls of `cover_deduction` now carry `covered_item_serial=F('device_serial')`, so the compute reads the plan **on the batch** as its rule says. The scoping bites rather than being decorative — I moved the seeded plan to another serial and the deduction fell to 0 with the offer at 5016.00 — and on the seeded world the plan's serial is the batch's, so the deduction stays 220.00 and no figure moves.

### revision_4_findings

No new red light, and nothing regressed. Three observations, none demonstrating a consequence under the four relationships:

- **O-r4.1 — the run is booked for the day after the quote's last day, against the ladder's own stated reason.** Task 0's world now has `quote_expiry_date: 2026-09-21` while the collection is asked for, and consented to, on 2026-09-22; the new ladder's rationale is "because the machines must reach the retailer while the quote still stands". So the run being priced is one those machines cannot make while the quote stands, and the lifecycle's `accepted → expired` ("the accepted device never reached the retailer") is the contingency the world is heading into. Not a red light: the because-clause is a reason for why the room on the quote governs the share, not a gate; no sentence of the merged charter conditions the collection day on the quote's last day; base's expiry clauses bite on acceptance (done on 2026-09-10) and on honouring an expired quote later, neither of which is what happens today; and `requested_collection_date` is the customer's own stated argument, refused to be moved, matching the standing record. Recorded because the separation of the two dates — which is what makes the share's reading unambiguous — has this as its side effect.
- **O-r4.2 — `run_lift_share.evidence` still declares `history`.** Its bindings are now `[quote_days_left, run_fill_pct]`, and `quote_days_left` reads an agreement field against `NOW`; there is no history aggregate among them. `date` alone satisfies the requirement, so nothing breaks — the list simply lags the re-basing. The matching `inputs.history` entry *was* cleaned up (the stale `latest` on `requested_collection_date` is gone and the `count` the allowance ladder performs is declared), so this is the last trace of the same edit.
- **O-r4.3 — `transit_cover_wave_basis`'s second tier outputs a wave of no machines.** "Where the value of each machine is at or above the programme's transit cover and the quote has run longer than the programme's quote validity days, the cover bears no machine until a fresh quote is written" → `cover_units = 0` and `units_declared = 0` (confirmed on a constructed world). The remedy the tier names — a fresh quote — lies outside this policy, so in that world the scored act would be a customer consent to release nothing. Neither task reaches this tier, and the tier's outcome is a coherent business answer ("the run does not go"), so no red light.

### revision_4_regression_check

Task 0's world moved by a day, so I re-derived it from the seed: `quote_date 2026-09-07`, `quote_expiry_date 2026-09-21`, the standing courier request still asking for `2026-09-22`, and the persona still carrying the line that explains the courier booking ("it was booked as a courier collection back when there were only eighteen loose machines"). Task 1's world did not move and its charter changes were confined to the cover factor's serial scoping.

**Every scored figure and every baseline recomputed identical to revisions 2 and 3**: `units_declared` 12, `handling_fee_amount` 240.00, `revised_amount` 4822.40, `final_credit_amount` 4342.40, `credit_expiry_date` 2026-12-17, `units_declared` 5; whole baselines 34, 230.70, 5100.00, 5100.00, 46; all 24 per-factor baselines unchanged to the cent. All four revealed GT figures and every factor's `tier_taken` match my re-derivation. Task 0's `0-F2` closure is intact — skipping the customer's write still leaves the charge with nothing to read. Task 1's tree is intact — both edges unmet at `frozen_time`, the `value_input` edge still moving the credit from 4342.40 to 4620.00 when the revision is skipped. Every world-assertion in the amended proof fields recomputes true, including the one the artifact volunteers to keep the two dates apart: "The day the customer asks the collection for, 2026-09-22, is a different record and is not what this share reads."

## closing_checklist (revision_4) — THIS DIFFICULTY CLOSES OUT

| task | policy self-consistency | problem tree | factors bear weight | unique solution |
| --- | --- | --- | --- | --- |
| 0 | **PASS** | **PASS** | **PASS** | **PASS** |
| 1 | **PASS** | **PASS** | **PASS** | **PASS** |

All four relationships hold on both tasks, so the difficulty passes the source-layer audit. Against Step 4's list:

- the per-task audit files correspond one to one with the tasks, `_difficulty.md` sits alongside them, revisions 1 to 4 are preserved in order with no earlier text rewritten, and every comparison section carries its round's verdict;
- this difficulty's five extended policies are fully covered by the two tasks with pairwise disjoint scopes (task 0: `…handover_units`, `…freight_charge`; task 1: `…revised_offer_amount`, `…batch_settlement_credit`, `…refresh_wave_units`), each scope spanning its whole tree; task tools and GT are closed; and each task tool still uses an independently generated, frozen uuid8 (`5801b6db`, `530ef4f1`, `f86761c2`, `af2cb6f5`, `923c3678`), unchanged since revision 2 and confirmed by the unchanged `task_tools.py` hash;
- every task's problem tree has one to three prerequisite problems (1 and 2), at least max(n−1, 1) `value_input` edges (1 and 1), at least one problem resolved by an `owner=user` tool (`confirm_handover_units_5801b6db`; `confirm_refresh_wave_units_923c3678`), and no cycle; the difficulty's three edges together remain a directed acyclic graph, two disjoint chains, with no cycle created by cross-task reference;
- every computation declares a self-sufficient baseline yielding a definite number different from gold (34, 230.70, 5100.00, 5100.00, 46) and four to six factors — 24 in all, each with ≥2 `parameter` and ≥1 `method` per policy, at least one multi-source and at least one cross-difficulty factor per task, every ladder at three tiers or more stated in full in its own rule, every tier distinct in outcome, every tier reachable on a world that produces a result, every cross-product state a tier requires permitted by that product's own rules and transitions, and every factor proved to move its scored figure against an honest baseline on its own task's world;
- the instantiation-stage gates were re-run on this final form by the coordinator and are green (`check_extended`, `check_task_tools`, `check_solvability`, `check_compute`, `check_grounding`, `check_cross_fire`, `replay --check`), with `check_traceability` deferred to the render step by design.

Carried forward as observations rather than defects, for whoever renders the KB: `_difficulty.md` F5 (the decision-days regime, answered in revision 2), revision 3's "settled by the load alone" wording note, revision 2's `machines_consented_before` counting a stood-down request's units, and O-r4.1 to O-r4.3 above. None of them changes a scored figure, an owner, an order or a terminal state.

## revision_5

Re-audit, 2026-09-20, same auditor. A narrow round: verify that the KB-driven source fix disturbs nothing, and record two misses of my own that the render-layer audit exposed.

### re_derivation_grounds

| artifact | revision 4 | revision 5 | treatment |
| --- | --- | --- | --- |
| `tradein.extended.yaml` | `95909f62c6bcf440` | `b979d1359d4d4710` | re-derived in full |
| `task_tools.py` | `45fbe2eeaab3eb4f` | `45fbe2eeaab3eb4f` | carried forward by hash |
| masked view `0.json` | `9b398f590ba21852` | `9b398f590ba21852` | worlds carried forward |
| masked view `1.json` | `7fa92c1ce44ba777` | `7fa92c1ce44ba777` | worlds carried forward |

Base section still byte-identical to `blueprint/products/tradein.yaml`. Gates cited from the coordinator's snapshot, all green, and `check_traceability` now runs and passes (0.json 20/0, 1.json 24/0). Re-derived on the amended charter: **12** `overwrite` entries (ten as before, plus the two new business-days declarations), every one verbatim in its cited base rule with that policy in `base_policy_refs`; factor counts 4 / 6 / 4 / 6 / 4 with ≥2 `parameter` and ≥1 `method`; every ladder at three tiers or more; `baseline` equal to its own fall-through for all 24 factors; every `baseline.rule` sentence present in its own `rule`; no orphan `compute_basis` key and every `compute_basis` entry verbatim in its rule; all three prerequisite edges state-form, verbatim, with `resolved_by` still the depended-on `target_tool`.

### the `baseline.params` fix

`tradein_ext_batch_settlement_credit.baseline.params` is now `[]`, and the four constants are untouched in the policy's own `params` (`delayed_allowance_usd 60.0`, `late_allowance_usd 140.0`, `uncertified_device_holdback_usd 25.0`, `certified_device_holdback_usd 8.0`), each still sitting in a real tier of `late_appraisal_allowance` (140 / 60 / nothing) and `erasure_certificate_holdback` (25 / 8 / nothing). A declaration fix, not a repricing, as claimed.

- **The baseline is still self-sufficient.** Its paragraph fixes every slot without needing a constant: "The amount settled is the amount the appraisal supports, the credit already issued on the agreement is nothing, and no transit settlement, no late appraisal allowance, no protection premium and no erasure holdback are counted." On task 1's world that reads `5100.00 − 0 + 0 + 0 − 0 − 0 = **5100.00**`, definite, reached from the baseline paragraph alone and differing from gold 4342.40. Recomputed. Removing the keys could not have left it short of a number precisely because the two slots those keys priced are set to *nothing* by the baseline's own words — which is the same fact that made the declaration wrong.
- **No factor lost weight.** All 24 per-factor baselines recompute identical to revision 4, including the two whose constants were named: `late_appraisal_allowance` 4282.40 and `erasure_certificate_holdback` 4642.40 against gold 4342.40.

**I agree with the agent's judgement on the two survivors, and on the test that separates them.** A `baseline.params` key is legitimate exactly when the baseline's own sentences fix that quantity — which entails that the key is the fall-through value of any ladder deciding the same binding, so publishing it discloses the baseline and never the spread.
- `tradein_ext_collection_handover_units` → `[slot_units_full, full_fill_pct]`: the baseline says "capped at **the full batch allowance** the carrier books … and the run lifts those machines **in full**". Both are its own defaults (40 machines, 100 per cent), both are the fall-through tiers of `carrier_batch_allowance` and `run_lift_share`, and the tier values that differ from them (24, 30; 75, 90) are not named by the declaration. Correct as it stands.
- `tradein_ext_collection_freight_charge` → `[pallet_capacity_units, standard_handling_usd, freight_fee_usd]`: the baseline says the pallets are "the machines the customer consents to hand over divided by **the machines one pallet holds**", "the pallet rate is **the programme's freight fee**" and "the handling charged for each machine is **the standard handling**". All three are needed to reach the baseline's own number (230.70) and none carries a tier that varies from it — `pallet_capacity_units` is not a tier value at all, and the other two are fall-throughs whose rival tiers (3.50, 2.40; the arrangement's rate, that rate plus the lane opening charge) are not named. Correct as it stands.
- The four that were removed failed this test outright: the baseline counts neither an allowance nor a holdback, so 60 / 140 / 25 / 8 were never its defaults, and naming them published the two-tier shape and full value set of two live factors. **Class note for future rounds**: check `baseline.params` key by key against the baseline's own sentences, not against the policy's `params` dict — a key that no baseline sentence fixes is a disclosure of variation dressed as a default, and it is forced into the one document required to stay silent.

### the five rule-level changes

1. **Pallet rate** — the new sentence "The rate that arrangement carries is the charge for each pallet moved that the arrangement's own freight terms set, and it stands on no order of the profile; what the profile's own orders show is whether it buys under that arrangement at all" is true to the compute, which reads the rate from the orders **variant parameter** (`CPARAM('orders','freight_pallet_fee_usd', …)` = 65.00) and the order rows only through `EXISTS` to establish that the arrangement is held. Internally consistent; the ladder is unchanged.
2. **"How long the quote has run"** — now "counted in calendar days from the day the quote was given **to the day the collection charge is raised**", matching `quote_days_run: DAYS(F('quote_date'), NOW)`. This does bear on task 0 and the excluded reading is worth 14.00; see `0.md` § revision_5, where I also record that this was a miss in my own revision-4 pass.
3. **Business days against calendar days** — now declared on both policies that measure against base's figure. The superseded fragment "counted in business days from the day the device was booked in" is verbatim in base `tradein_appraisal_grading`, and it is genuinely in force: both policies compare a `DAYS(...)` calendar count against `P('appraisal_days')`. The two replacements ("…the programme's appraisal days are read against that calendar count") are each verbatim in their own rule, say the same thing, and are true to what each policy computes. Adding `tradein_appraisal_grading` to `tradein_ext_batch_settlement_credit.base_policy_refs` introduces no gate: that base policy's only eligibility, `appraisable_agreement_state`, carries `applies_to: [tradein_appraisal_record]`, and this policy's subject is `tradein_agreement_credit`. **This one was a real undeclared override that I passed in rounds 1 to 4** — see the disclosure below and the demonstration in `1.md` § revision_5.
4. **Lifecycle scope sentence** in the handover-units policy — "An agreement the customer has accepted runs out where the machines never reach the retailer, the day it runs out is written onto it, and no run is settled on it thereafter." It passes the three tests: no figure, no window, no capability; and it states no cross-problem order, because the state it names is reached by a system transition that no write of this difficulty performs, so it grounds no edge and needs none. One observation below.
5. **Half-pallet label** — the tier now reads "the whole pallets the run fills together with a further half pallet for the part, whatever the size of the part", which is what `int(raw_pallets) + 0.5` does; "nearest half pallet" no longer occurs anywhere in the charter. A genuine correction: the old label was wrong for any part above a half. It changes no figure here, and the factor's own sensitivity is unchanged at 207.50.

**Prerequisite-sentence collision scan**: I checked every sentence of all five rules against all three prerequisite sentences for exact duplication, containment and reverse containment. Each prerequisite sentence occurs exactly once in the charter, in its own blocked policy's rule; **0 collisions**. None of the five added sentences touches one.

### two misses of my own, disclosed

The baseline for a re-audit is my own earlier text, so where the render layer found something I had passed, I record it here rather than leaving it implicit.

- **The business-days mismatch (rounds 1–4).** Base `tradein_appraisal_grading` counts the programme's appraisal days in business days; `tradein_ext_batch_settlement_credit` compares a calendar count against the same figure, and no `overwrite` declared it. It was materially load-bearing on task 1: the batch was booked in on Friday 2026-09-04 and appraised on Tuesday 2026-09-15, which is 11 calendar days but **exactly 7 business days**, and the programme's `appraisal_days` is 7. So base's convention gives "recorded within the programme's appraisal days" and no allowance, against the extended policy's delayed allowance of 60.00 — two defensible credits, 4282.40 against 4342.40. My check-1 sweep in revision 1 went sentence by sentence through that base policy and did not carry the counting convention into the two extended policies that read the figure. Now declared, so the calendar reading is the one in force and the rival is excluded by a clause.
- **The unnamed far end of "how long the quote has run" (revision 4 only).** The under-specification was in the text from the start, but it was inert until revision 4 moved task 0's world: with `quote_date 2026-09-08` the rival reading gave exactly 14 days, which is not "longer than" 14, so both readings paid the standing uplift. Revision 4's world (`quote_date 2026-09-07`, collection 2026-09-22) made the two readings 11 and 15 days, and I passed that round without noticing the new consequence. Recorded as a miss in the revision-4 pass specifically, not in revisions 1 to 3.

### revision_5_findings

No new red light, nothing regressed. One new observation:

- **O-r5.1 — the new lifecycle sentence asserts a record effect the schema cannot hold.** "…the day it runs out is written onto it…" but `tradein_agreements` carries no column for it: its date columns are `quote_date`, `quote_expiry_date`, `accepted_date`, `device_received_date`, `appraised_date`, `credited_date`, `declined_date`, `returned_date`, `credit_expiry_date`, none of which is the day an accepted agreement runs out (`quote_expiry_date` is the quote's last acceptable day, fixed at quoting). The phrasing appears to be borrowed from base `tradein_credit_issue_rules`, where "the expiry day is written onto the agreement" does have a column. Not a red light: no write of this difficulty expires an agreement, neither task's world holds an expired one, and no figure, gate or terminal state turns on it. Flagged mainly for the render layer, since it is a fresh sentence that will be published and a reader may look for a field that is not there.
- Carried forward: revision 4's O-r4.1 (the run booked for the day after the quote's last day) is partly answered by change 4 — the charter now states outright what happens if the machines never arrive — but the wrinkle itself stands, since the run is still booked for 2026-09-22.

## closing_checklist (revision_5) — THE DIFFICULTY REMAINS CLOSED

| task | policy self-consistency | problem tree | factors bear weight | unique solution |
| --- | --- | --- | --- | --- |
| 0 | **PASS** | **PASS** | **PASS** | **PASS** |
| 1 | **PASS** | **PASS** | **PASS** | **PASS** |

No scored value moved: `units_declared` 12, `handling_fee_amount` 240.00, `revised_amount` 4822.40, `final_credit_amount` 4342.40, `credit_expiry_date` 2026-12-17, `units_declared` 5; whole baselines 34, 230.70, 5100.00, 5100.00, 46; all 24 per-factor baselines identical to revision 4 to the cent; all revealed GT figures and every `tier_taken` match my re-derivation. The revision-4 closing checklist stands in full, with two amendments: the charter now carries 12 declared overrides rather than 10, and `check_traceability` has run and passed rather than being deferred. The difficulty passes the source-layer audit, and it now does so with the two conflicts above declared rather than latent.
