# Policy-task audit — parking_rate_increase_and_compliance / charter-global

## charter_global_frozen

- Auditor: independent erl-task-policy-audit agent (did not author these artifacts). Frozen 2026-10-10T19:43Z, before any task's GT was revealed. Nothing in this section is derived from a revealed GT field.
- Freeze hashes (re-computed by the auditor, equal to the coordinator's):
  - `tasks/parking_rate_increase_and_compliance/parking.extended.yaml` sha256 `5e030fe792884569e657c53bc82860c555e87792b5b19f6860ff30dd17755b69`
  - `tasks/parking_rate_increase_and_compliance/task_tools.py` sha256 `a3f2ce031f03acec984329cd93c1643b4928845201d6c6ae78b9e94919f15b84`
  - masked views `0.view.json` `e3e9a487…3044`, `1.view.json` `aa52555f…505a` (match the brief).
- Fields read: `blueprint/blueprint.yaml`, `blueprint/products/parking.yaml` (+ `autopay.yaml` retry/suspension section and `unit.yaml`/`autopay.yaml` loaded only as cross charters for the DSL), `blueprint/db_schema.json`, `blueprint/share_tools.py`, the extended charter, `task_tools.py`, the two masked views (frozen_time, user_scenario, initial_state), and the DSL primitive semantics in `skills/erl-task-instantiate/scripts/check_compute.py` (`MONTHS`, `DAYS`, `_within`, `LATEST`, `CFIELD`, `XCOUNT`, `XLATEST`) — read only, no gate executed.
- Masked / unread until every task froze: `evaluation_criteria`, `computations`, `charter_scope`, `required_documents`, `design_rationale`, `solvability_contract`, `prerequisite_closure`, `db_closure*`.
- Entry conditions (Step 0): the brief supplies the gate snapshot (EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK; traceability deferred to render; validate_scenario only `required document ... not found`) and the masked views with hashes. Input complete.

### policy_conflict_scan

Base section of the extended file is verbatim identical to `blueprint/products/parking.yaml` (key-by-key structural equality for `category, display_name, binding, lifecycle, accounts, parameter_schema, variants, events, measures, policies`; the only extra key is `extended_policies`).

Seven extended policies, seven target tools, two disjoint dependency components:

| policy | target_tool (owner) | computes | prerequisite |
| --- | --- | --- | --- |
| parking_ext_billing_error_correction (BEC) | credit_parking_billing_error_d978766a (agent) | amount | [] |
| parking_ext_late_fee_assessment (LF) | post_parking_late_fee_42918014 (agent) | amount | BEC (value_input, lf_pct) |
| parking_ext_bring_current_payment (PAY) | pay_parking_past_due_d726500b (user) | amount | LF (value_input, pay_balance); BEC (value_input, pay_balance) |
| parking_ext_retention_concession (CON) | grant_parking_retention_concession_aac1dee9 (agent) | new_rent | PAY (state_gate, balance_due) |
| parking_ext_tow_notice_fee (TF) | post_parking_tow_notice_fee_6c1b851a (agent) | amount | [] |
| parking_ext_tow_redemption_payment (RED) | pay_parking_tow_redemption_54345a56 (user) | amount | TF (value_input, pt_balance) |
| parking_ext_vehicle_swap_fee (SW) | swap_parking_vehicle_d3106476 (agent) | swap_fee | RED (state_gate, status) |

Overlapping subjects / triggers:
- LF and TF both have subject `parking_fee_charge`; distinguished by fee_type (late_fee vs tow_notice_fee) and by tool. No overlap in conclusions.
- PAY and RED both have subject `parking_payment`; their scopes are disjoint by record state: PAY "A tenant whose parking agreement is delinquent"; RED "While a notice of intent to tow stands". `delinquent` and `tow_noticed` are distinct lifecycle states, so on any one world at most one applies.
- CON (subject `parking_rate_change_notice`) and the base `parking_evt_rate_increase` share the event type; CON's declared overwrite #2 replaces the base status sentence for the concession (see override_declarations).
- Time anchors: every extended window ("last 2/3/6/12/24 months") is defined in its own rule as "entries dated less than that many whole calendar months before the handling date, whole months being counted to the same day of the later month"; consistent with base month-counting and with the DSL `_within` (0 <= MONTHS(d, NOW) < N). Day counting (`DAYS`) is calendar-day difference.
- Cross-category read boundaries: unit (status, move_in_date) for BEC/LF/PAY/CON; autopay (status, suspension_date, drafts) for LF/CON/TF/RED. All declared in `cross_category`.
- Scope exclusivity: task scopes as derived blind (task 0 = {BEC, LF, PAY, CON}; task 1 = {TF, RED, SW}) are disjoint and jointly cover all seven extended policies. (Confirmed against `charter_scope` only after the reveal, in the task files.)
- Observation (not one of the four relationships): the blueprint claim and difficulty name centre on rate increases, rescissions, compliance notices/cure/termination and move-out (`parking_rent_rate_update, parking_notice, parking_stage_advance, parking_compliance_cured, parking_moveout_*, parking_vacated, parking_refund`), yet no extended policy and no task tool writes any of those event types; the bundle exercises late fees, credits, payments, a concession, a tow fee and a vehicle swap.

### rule_compute_equivalence

Each binding's `compute_basis` is a verbatim sentence of its policy's rule (checked for all 7 policies). Sweep results:

- BEC: err_fee/rec_share/rec_rent/rec_mult/rec_cap/rec_allow/recovery/result all quoted. **Divergence B1**: rule "The billing-error correction credit is the erroneous late fee in full, as it was posted" vs compute `err_fee: LATEST('parking_ledger','amount', date_field='entry_date', event_type='parking_fee_charge', fee_type='late_fee')` — compute takes the most recent late fee on the agreement, not the fee being corrected (the tool's `reference_entry_id`). They coincide only when the erroneous fee is the latest late fee. Similarly `rec_cap` uses `COUNT(late fees in 12m) - 1` for "late fees other than the erroneous one", assuming the erroneous fee is inside the 12-month window.
- LF: **Divergence L1**: rule "Days late are counted from the date of the latest declined AutoPay draft attempt for the unpaid period's due date where the agreement's AutoPay draft for that due date was declined ...; and from the unpaid period's due date in every other case" vs compute `lf_anchor` keyed on `due_date=F('delinquent_since')` and falling back to `F('delinquent_since')` — the oldest unpaid period's due date, not the due date of the period the fee is posted for. Also the `XCOUNT/XLATEST` read is scoped to the customer, not to "the agreement's" authorization. Situation where they part: agreement delinquent since 09-08, AutoPay active, NSF declines on 09-08/09-11 and on 10-08/10-11, late fee for the 10-08 period handled 10-20: rule anchor 10-11 (days late 9−grace), compute anchor 09-11 (days late 39−grace) → different proration and fee.
- LF lf_pct, lf_standard, lf_cycle (cycle_anchor_date = delinquent_since = "the cycle ... running from the agreement's delinquency date"), lf_prorate, lf_rebate, lf_floor, result: equivalent.
- PAY: pay_next ("next rent due date is the day after the last day of the most recently charged billing period" = DAYS(NOW, latest period_end)+1), pay_defer, pay_bundle, pay_lock, result: equivalent.
- CON: con_share, con_bundle, con_autopay, con_measure (three tiers incl. the prior-share tier), con_cap, give_back, result (`int(round(x*100,6))/100` = round down to the cent, floored at con_prev): equivalent.
- TF: tf_level (`COUNT-1` = "other notices"), tf_mult, tf_tenure, tf_autopay, result: equivalent.
- RED: pt_next, pt_deposit, pt_dispatch (`tow_min_days_after_notice - DAYS(notice, NOW)` = days until earliest tow date), pt_autopay, result: equivalent.
- SW: sw_level, sw_tenure, sw_period, sw_reverify, sw_docs (`F('insurance_expiry')` evaluated before the write = vehicle being replaced), sw_record, result: equivalent.
- Charter-wide observations: (i) `MONTHS` in the DSL does not implement "or that month's last day when the day does not exist" (e.g. 01-31 → 02-28 counts 0, the rule counts 1); no task world has a start/billing day above 28. (ii) Every "rounded to the cent" is Python `round` on binary floats, the tools store "rounded half-up"; no scored value in either task lands on an exact half-cent. (iii) `CFIELD('unit', ..., status='active')` reads the first active unit; the rule does not say which unit decides when a tenant holds several active units (each task world has at most one).
- Every factor ladder tier appears both in the rule and as a branch of its `decides` binding (no tier lives in one face only).

### action_binding_and_uuids

- Each `(target_tool, computes)` pair is claimed by exactly one policy (table above); the tool module defines exactly these 7 tools.
- uuid8s: d978766a, 42918014, d726500b, aac1dee9, 6c1b851a, 54345a56, d3106476 — all distinct, no shared prefix/suffix, no sequential pattern.
- Docstrings: no tool names another tool, states a sequence position, or carries before/after/first/then/until (grep of `task_tools.py` for those words: no hit). The redemption docstring's "while a notice of intent to tow stands" describes the record state the payment is for, not an order.
- Function bodies: every tool does `ctx.find` on the agreement only to copy customer_id / balance; none checks status, balance, ledger state or existing credits/fees, none refuses or hints. The tool layer judges no prerequisite.
- Observation: `pay_parking_past_due_d726500b` lowers `balance_due` but never moves a `delinquent` agreement to `active`, while base lifecycle says "delinquent → active by system: The past-due balance is paid in full before a tow notice is sent"; after task 0's payment the record is `delinquent` with a negative balance. No scored value reads the status after that point (CON's status requirement is replaced by a balance requirement), so no consequence is demonstrable.

### prerequisite_graph

Edges (all `form: state`, no `fallback_reason`):

| # | blocked | problem | kind / gate | policy_source located verbatim in blocked rule | resolved_by = problem's target_tool |
| --- | --- | --- | --- | --- | --- |
| E1 | LF | BEC | value_input / lf_pct (exists) | yes ("A late fee for an unpaid period is not posted until each earlier late fee ... carries a billing-error correction credit on the ledger.") | yes |
| E2 | PAY | LF | value_input / pay_balance (exists) | yes ("... worked out only once a late fee stands on the ledger for every billing period whose rent remained unpaid past its grace period.") | yes |
| E3 | PAY | BEC | value_input / pay_balance | yes ("... is not fixed until every late fee posted against a period paid within its grace period carries a billing-error correction credit.") | yes |
| E4 | CON | PAY | state_gate / parking_rentals.balance_due | yes ("A retention concession is recorded only after the agreement's balance due stands at zero or below.") | yes |
| E5 | RED | TF | value_input / pt_balance (exists) | yes ("The redemption amount after a notice of intent to tow is fixed only after a tow notice fee stands on the ledger for the delinquency cycle the notice was sent for.") | yes |
| E6 | SW | RED | state_gate / parking_rentals.status | yes ("A different vehicle is not put on file until the agreement stands in active status.") | yes |

- Every policy fills `prerequisite` (`[]` for BEC and TF). Every `problem` is an extended policy id in this file, none self-referential, none a base policy. Graph: BEC→LF→PAY→CON, BEC→PAY; TF→RED→SW. Acyclic.
- `kind` matches `gate`: value_input gates are real binding names in the blocked compute; state_gate gates are record fields the sentence names.
- `condition` vs sentence strength: E1 condition says "Every late fee on the agreement whose billing period was paid within its grace period" while the sentence says "each earlier late fee"; for a late fee being posted for the current unpaid period every erroneous fee is earlier, so the two coincide in practice (observation only). Others match.
- `effect` claims are verified per task in the task files. No authoring-viewpoint phrasing ("in this task", "at the opening") in any `prerequisite` field.

### prerequisite_sentences

Four-point test, each edge:
- E1–E6 each join the blocked policy's own result to what it waits on with an ordering connective ("not ... until", "only once", "not fixed until", "only after", "only after", "not ... until").
- Each waits on a record-visible state in table words with no actor or tool: "carries a billing-error correction credit on the ledger" (parking_ledger credit_type), "a late fee stands on the ledger" (fee_type late_fee), "balance due stands at zero or below" (parking_rentals.balance_due), "a tow notice fee stands on the ledger" (fee_type tow_notice_fee), "stands in active status" (parking_rentals.status).
- None names a tool, policy id, snake_case token or row id.
- Strength/scope: closed sets named by kind ("every billing period whose rent remained unpaid past its grace period", "every late fee posted against a period paid within its grace period").
- Which write brings each state about (state-form uniqueness):
  - E1/E3 billing-error correction credit: only `credit_parking_billing_error_d978766a` writes `credit_type=billing_error_correction`. Unique.
  - E2 late fee on the ledger: only `post_parking_late_fee_42918014`. Unique.
  - E5 tow notice fee on the ledger: only `post_parking_tow_notice_fee_6c1b851a`. Unique.
  - E6 status active: only `pay_parking_tow_redemption_54345a56` writes `status`. Unique.
  - E4 balance due ≤ 0: three tools lower `balance_due` (`pay_parking_past_due`, `pay_parking_tow_redemption`, `credit_parking_billing_error`). The hop still resolves in one reading from the records: PAY's rule applies to a `delinquent` agreement, RED's to one under a standing notice of intent to tow (disjoint states), and the billing-error credit's own rule is triggered by a billing error and fixes its amount independently of the balance. Recorded as an observation, not a RED, because no world admits two defensible resolving writes; strictly, "exactly one write" is not literally met.
- Derivations (sentence + records + depended-on rule → resolving action), single reading each:
  - E1: LF sentence → find ledger late fees whose period was paid within grace (payment dated ≤ due date + grace_period_days) lacking a correction → BEC rule ("A late fee posted against a billing period whose rent was paid within its grace period is a billing error, and it is corrected with one billing-error correction credit against that fee entry") → credit tool.
  - E2: PAY sentence → find unpaid rent charges past grace with no late fee referencing them → LF rule ("A late fee is posted once for a billing period whose rent is still unpaid at the end of its grace period") → late-fee tool.
  - E3: as E1 via PAY's sentence.
  - E4: CON sentence → balance_due > 0 → for a delinquent agreement PAY rule ("A tenant whose parking agreement is delinquent may pay from their own card or bank account to bring it current") → user payment tool.
  - E5: RED sentence → no tow_notice_fee entry for the cycle of the standing intent_to_tow notice → TF rule ("When a notice of intent to tow is sent ..., a tow notice fee is posted against the oldest unpaid rent charge of the delinquency cycle") → tow-fee tool.
  - E6: SW sentence → status tow_noticed → RED rule ("... it returns the agreement to active standing") → user redemption tool.
- No blocked rule carries a second wording, tool name or other problem id; no depended-on rule restates the sentence. No extended rule states a cross-problem order that grounds no declared edge.
- Base cross-problem-order sentences (observation only, they ground no edge here): `parking_agg_multi_holding` "must resolve it before a new space is reserved"; `parking_evt_tow_process` "after the tow notice only a payment of the full balance is accepted, and it returns the agreement to active".

### override_declarations

Sentence-by-sentence against each `base_policy_refs` entry (findings only; consequences are demonstrated in the task files).

**BEC** (refs parking_evt_late_fee_and_waiver; `overwrite: []`)
- "A late fee is assessed once ... / may be posted only when ... / The late fee is the greater of ... / Fees are posted only while ... / A courtesy waiver credits one late fee in full ..." — govern the fee or the waiver, not the correction credit; followed or not applicable.
- "Grace days are calendar days starting the day after the due date, and a payment on the last grace day is on time." — followed (BEC's "paid within its grace period").
- **"A late fee posted against a period paid within grace is a billing error and is credited as billing_error_correction without using the courtesy allowance."** — governs the scored quantity (the credit amount). Base credits the late fee (amount = the fee as posted); extended credits "the erroneous late fee in full, as it was posted, plus a service-recovery amount" plus "any inconvenience allowance". Different amount, not named in any `overwrite`. **Undeclared override → finding F1.**
- "A charge already waived or corrected is not credited again." — followed.

**LF** (refs parking_evt_late_fee_and_waiver; 1 declared overwrite)
- Assessment once per period / timing / grace counting / status — followed.
- Amount sentence — declared superseded; merged semantics unique (replaced_by fixes the order: ceiling before multipliers, rebate, then floor, round at end).
- Courtesy / billing error / dedup sentences — not this write's quantity.
- Extended adds a prerequisite sentence (E1); not an override.

**PAY** (refs parking_agg_portfolio_increase_review, parking_evt_tow_process; `overwrite: []`)
- Portfolio allocation sentence — not applicable (one named agreement).
- "While delinquent, payments of any amount are accepted" — base fixes no amount for a delinquent payment; extended's quoted amount is compatible. Partial-payment parameters — compatible.
- Tow-notice payment sentence — outside PAY's scope (delinquent, no tow notice).
- No undeclared override.

**CON** (refs portfolio, rate_increase, retention_concession; 2 declared overwrites)
- Retention amount sentence — declared; merged semantics unique.
- Window, window counting, min tenure, tenure counting, once per increase, rolling 365-day count, "already in effect / move-out notice / defective increase get no concession", "never lowers the rent below the rent before the increase" — all inherited and followed (extended keeps the floor).
- Rate-increase "Increase notices go only to agreements in active status." — declared superseded by "A retention concession is recorded only after the agreement's balance due stands at zero or below." The base sentence's text governs increase notices, while its structured eligibility `increase_status` applies to every `parking_rate_change_notice`, concessions included; the declaration makes the merged rule for a concession the balance test. Unique. Observation: the declaration names a sentence whose own text speaks of increase notices, so the charter now carries no statement that increase notices themselves are limited to active agreements within this policy's reach.
- Prepay lock sentence — inherited (near-miss in task 0: completed plan).

**TF** (refs late_fee_and_waiver, tow_process; 1 declared overwrite)
- "The notice is sent by certified mail and email, posts tow_notice_fee_usd and moves the agreement to tow_noticed." — declared superseded by a fee-only sentence; the delivery method and the status move are dropped along with the fee amount (observation; no task writes a notice or a status here).
- Tow-notice timing, military protection, tow timing — inherited.

**RED** (refs portfolio, tow_process; `overwrite: []`)
- **"While delinquent, payments of any amount are accepted; after the tow notice only a payment of the full balance is accepted, and it returns the agreement to active and restores the gate code."** — governs the scored quantity (the payment that redeems after a tow notice). Base: the full balance. Extended: "only a payment of the full redemption amount ... is accepted", the redemption amount being "the balance due plus the share of the next period's rent that is collected, plus the redemption deposit, the tow dispatch cancellation hold and the AutoPay advance". A payment of exactly the balance is accepted and redeems under base and is refused under extended. Not named in any `overwrite`. **Undeclared override → finding F2.** (Base lifecycle repeats it: "tow_noticed → active: The tenant pays the full balance, including the tow notice fee, before the tow.")
- Returned-payment, partial-payment parameters — compatible.

**SW** (refs vehicle_fit, compliance, space_features; 3 declared overwrites)
- Fit sentence — declared (tenant reads type and length from the registration). Unique.
- Compliance renewal sentence — declared superseded by the swap recording sentence. Observation: the superseded sentence also carried "a cure recorded before the termination date returns a termination_noticed agreement to active", which is thereby dropped within this policy's reach.
- Swap sentence ("only on an agreement in active status, at most vehicle_swaps_per_12_months times in a rolling 365-day window ..., and each swap posts vehicle_swap_fee_usd") — declared superseded by the fee formula; the active-status condition returns as E6's sentence, but the swap-count limit (and measure `parking_msr_vehicle_swaps_365d`) is dropped. Observation (declared; no task world reaches the limit).
- "Vehicle details are changed only while ... active or termination_noticed" — inherited, compatible with E6.
- Space features — not applicable.

### factor_ladders

Counts per policy (P = parameter, M = method, X = cross_difficulty):

| policy | factors | P | M | multi-source factors (every non-fall-through tier ≥2 conditions over distinct records) | X |
| --- | --- | --- | --- | --- | --- |
| BEC | 5 | share, ceiling, allowance (3) | rent_measure, bundled_multiplier (2) | service_recovery_share (tenure ∧ payments); bundled_tenant_multiplier (active unit ∧ move-in age) | unit |
| LF | 6 | pct, rebate, floor (3) | cycle, anchor, proration (3) | lateness_clock_anchor (tier 2: no NSF decline ∧ suspended); loyal_tenant_proration; bundled_tenant_rebate | autopay, unit |
| PAY | 4 | defer, bundle, lockout (3) | next_period_collection (1) | loyal_tenant_deferral; bundled_tenant_deferral; lockout_deferral | unit |
| CON | 5 | share, bundle, autopay, cap (4) | cumulative_increase_measure (1) | tenure_and_record_share; storage_bundle_share; autopay_record_share | unit, autopay |
| TF | 4 | level, tenure, autopay (3) | unpaid_period_multiplier (1) | tenure_relief; autopay_lapse_relief | autopay |
| RED | 4 | deposit, dispatch, autopay (3) | next_period (1) | autopay_lapse_advance; tow_dispatch_cancellation (nominally — see F4) | autopay |
| SW | 6 | level, reverify, docs, record (4) | tenure_multiplier, period_timing (2) | good_record_reduction | — |

Structure checks:
- Every factor: `decides` is an input binding (never `result`), binding sets disjoint, ladder of exactly three tiers stated in the rule and implemented in `decides`; fall-through = factor `baseline` = what `baseline.rule` states for that input (BEC: share_std, monthly_rent, ×1, cap_std, 0; LF: standard pct, ×1, unpaid period's due date, full, 0, flat; PAY: 0/0/0/0; CON: standard share, 0, 0, noticed increase alone, cap_std; TF: class fee, ×1, 0, 0; RED: 0/0/0/0; SW: class fee, ×1, ×1, 0, 0, 0). Each `baseline.rule` is a sentence set of its rule, uses the keys in `baseline.params`, and is self-sufficient.
- Every task's policies carry ≥1 multi-source and ≥1 cross_difficulty factor (task 0: unit, autopay; task 1: autopay).
- **Same value in two tiers (finding F3)**: SW `swap_sequence_level` — tier 1 `K('level_repeat') = 25.0`, fall-through `P('vehicle_swap_fee_usd')` = 25.0 for 5 of 6 classes (Uncovered RV & Boat up to 30 ft, 31-45 ft, Covered up to 30 ft, 31-45 ft, Enclosed Garage); distinct only for Uncovered Car Space (15.0). All other P-vs-K ladders are distinct on every class (lf_floor 10/15 vs flat 20–35; tf_level 65/55 vs 40/50; con_share .55/.52 vs .5; sw_level tier 2 20 vs 15/25).
- **Universal condition part (finding F4)**: RED `tow_dispatch_cancellation` — tiers 1 and 2 are "the current cycle's tow notice stands and ..."; every customer who reaches the redemption write is, by RED's own scope ("While a notice of intent to tow stands"), under the current cycle's standing notice, so that part restates the scope and divides no customers. Struck, RED has 3 factors (< 4).
- **Unreachable tier (finding F5)**: CON `cumulative_increase_measure` tier 1 "the rent last changed less than 12 months before the notice date of the most recent increase". Base `parking_evt_rate_increase`: "An increase notice may also be sent only when the handling date is not earlier than the last rent change date plus rate_increase_min_interval_months", and "An increase notice that breaks any of these rules is defective"; base `parking_evt_retention_concession`: "a defective increase (which is rescinded instead) get[s] no concession". With `rate_increase_min_interval_months = 12` (5 of 6 classes) any increase that can receive a concession was noticed ≥ 12 whole months after the last rent change, so tier 1 holds for no customer reaching the CON write on those classes (reachable only on Uncovered Car Space, interval 11, at exactly 11 months). On those classes the ladder has two live tiers; struck, CON has 0 `method` factors.
- Label honesty (observation): several `method` factors select only a multiplier or a share in an otherwise fixed formula (BEC `bundled_tenant_multiplier` ×2/×1.5/×1; LF `delinquency_cycle_multiplier`; PAY `next_period_collection` and RED `redemption_next_period` 1/0.5/0 of the rent; TF `unpaid_period_multiplier`; SW `swap_tenure_multiplier`, `billing_period_timing`). The instantiation reference explicitly lists "a multiplier on an intermediate or on the result" as `method`, so this is not recorded as RED; under a stricter reading (a multiplier is a number substituted into the same formula) PAY, TF, RED and SW would carry no honest `method` factor. Genuine algorithm-changing methods: BEC `service_recovery_rent_measure`, LF `lateness_clock_anchor` and `loyal_tenant_proration`, CON `cumulative_increase_measure`.
- Realism (observations, no demonstrable consequence): SW `document_check_charge` is keyed to the insurance expiry of the vehicle being replaced, not the vehicle put on file; CON `autopay_record_share` gives a tenant whose drafts bounced a larger give-back (0.015) than a tenant with no AutoPay (0); LF `tenure_minimum_fee` sets a long-tenure floor (10) below every class's flat fee, so "minimum" lowers rather than raises; BEC can credit more than the fee it corrects (service recovery + allowance up to $25 + $25 on a $20–35 fee).

### findings

- **F1 — SOURCE-POLICY RED (undeclared override, BEC).** Symptom: two clauses fix the billing-error credit amount differently. Root cause: BEC `overwrite: []` although its rule changes the quantity governed by base `parking_evt_late_fee_and_waiver` "A late fee posted against a period paid within grace is a billing error and is credited as billing_error_correction without using the courtesy allowance." (credit = the fee) to "the erroneous late fee in full, as it was posted, plus a service-recovery amount ... plus any inconvenience allowance". Affected: `parking.extended.yaml` → `extended_policies[parking_ext_billing_error_correction].overwrite`; scored `credit_parking_billing_error_d978766a.amount` and every downstream balance-based amount. Bears on **task 0** (consequence demonstrated in `0.md`).
- **F2 — SOURCE-POLICY RED (undeclared override, RED).** Root cause: RED `overwrite: []` although its rule replaces base `parking_evt_tow_process` "after the tow notice only a payment of the full balance is accepted, and it returns the agreement to active" with "only a payment of the full redemption amount" (balance + next-period share + deposit + dispatch hold + AutoPay advance). Affected: `extended_policies[parking_ext_tow_redemption_payment].overwrite`; scored `pay_parking_tow_redemption_54345a56.amount`. Bears on **task 1**.
- **F3 — SOURCE-FACTOR RED (two tiers select the same value, charter-level).** SW `swap_sequence_level`: `level_repeat` 25.0 = `P('vehicle_swap_fee_usd')` 25.0 on classes ranks 2–6. Affected: `extended_policies[parking_ext_vehicle_swap_fee].params.level_repeat` vs `variants[*].parameters.vehicle_swap_fee_usd`. Bears structurally on **task 1**'s SW computation; on task 1's class (Uncovered Car Space, 15.0) the tiers differ, so no consequence on that world.
- **F4 — SOURCE-FACTOR RED (condition part restates scope; factor count).** RED `tow_dispatch_cancellation`. Bears on **task 1**.
- **F5 — SOURCE-FACTOR RED (unreachable tier on interval-12 classes; method count).** CON `cumulative_increase_measure`. Bears on **task 0** (Covered RV & Boat up to 30 ft, interval 12).
- **F6 — SOURCE-POLICY (rule↔compute divergence, LF `lf_anchor`, L1).** Demonstrated on a constructed situation above (two consecutive NSF-declined due dates, late fee for the later period). Recorded as RED at charter level; on both task worlds the scored late fee is for the oldest unpaid period, so no task consequence.
- **F7 — SOURCE-POLICY (rule↔compute divergence, BEC `err_fee`/`rec_cap`, B1).** Diverges whenever a later late fee exists than the one corrected. Charter-level RED; no consequence on task 0 (the corrected fee is the latest at its handling time).
- Observations (no demonstrable consequence): E4 resolvable by more than one balance-lowering tool (disambiguated by status); PAY tool leaves `delinquent` status after full payment; declared overrides in TF/SW/CON drop more than the scored quantity (delivery/status move; swap-count limit; compliance cure return); DSL month-end fallback and rounding mode; multiplier-as-method labels; realism notes above; claim/content mismatch of the difficulty.

## closing_checklist

Written 2026-10-10T19:48Z, after both reveals. The difficulty is **not closed**: REDs are outstanding in both tasks.

- Audit files: `_difficulty.md`, `0.md`, `1.md` — one per task, first revision; each has `source_derivation_frozen` (frozen before any reveal) and `source_gt_comparison`. Neither comparison carries a PASS.
- Coverage and scope: 7/7 extended policies covered; task 0 = {BEC, LF, PAY, CON}, task 1 = {TF, RED, SW} — pairwise disjoint over whole trees and equal to `charter_scope`; task tools and GT closed (every gold write uses a tool of its own scope); each uuid8 independently generated and frozen.
- Trees: task 0 — 3 prerequisite problems, 3 value_input edges, user write PAY, acyclic; task 1 — 2 prerequisite problems, 1 value_input edge, user write RED, acyclic; the difficulty's edge set is a DAG with two disjoint components. Tree relationship holds on both worlds; task 0's closure carries one false load-bearing figure (0.md T0-4).
- Factors: every computation declares 4–6 factors with ≥2 parameter / ≥1 method as labelled, and every factor bears weight against an honest baseline on its world (all substitutions and whole-baseline numbers re-derived and equal to `computations`). Not met: F3 (swap level ladder repeats a value on 5 classes), F4 (redemption dispatch factor restates scope → RED at 3 factors), F5 (concession measure tier unreachable on interval-12 classes → CON without a method factor on task 0), task 0 autopay seed contradicting the autopay charter (0.md T0-2).
- Policy self-consistency: F1 and F2 are undeclared overrides with demonstrated second answers on task 0 (30.00 / 414.00) and task 1 (287.75); F6, F7 rule↔compute divergences without consequence on these worlds.
- Gates: not re-run by this auditor (the brief's snapshot stands; `parking.extended.yaml` and `task_tools.py` hashes are unchanged at close: `5e030fe7…7b69`, `a3f2ce03…9f15b84`).

Per-task verdicts: task 0 — SOURCE-POLICY RED, SOURCE-CHAIN RED (proof figure), SOURCE-FACTOR RED, SOURCE-TASK RED. Task 1 — SOURCE-POLICY RED, SOURCE-FACTOR RED, SOURCE-TASK RED.

## revision_2

### charter_global_frozen (round 2)
- Frozen 2026-10-10T21:00Z, before either round-2 task file was opened. Nothing here derives from a round-2 GT field.
- Hashes: `parking.extended.yaml` **changed** → `0d3b2cfc1a9a2958fced529f9ffbe9aa8127b267546015fe94ae7dc18a50db8f` (charter-global sections re-derived in full); `task_tools.py` unchanged `a3f2ce03…9f15b84` (action_binding_and_uuids carried forward by hash). Base section still verbatim equal to `blueprint/products/parking.yaml` (structural comparison, all ten keys SAME).
- Views: `0.view.json` `4178608d…c7ff` (changed), `1.view.json` `aa52555f…505a` (unchanged). Masking as round 1.
- contamination_disclosure: the auditor read the round-1 GT of both tasks (after the round-1 freeze). Round-2 derivations are made from the round-2 charter and views only; where a round-2 value coincides with a round-1 gold value it also coincided with the auditor's own round-1 blind value, so no round-1 GT entered a round-2 derivation that the round-1 blind derivation had not already produced independently. The coordinator's brief lists closed item ids only, no values.

### policy_conflict_scan (round 2)
Same seven policies, tools, subjects and two dependency components as round 1; scopes unchanged. No new overlap. Round-1 conclusions stand except as listed below.

### rule_compute_equivalence (round 2)
- **F6 (LF anchor)**: rule now reads "Days late are counted from the agreement's delinquency date, the due date of the oldest unpaid period of the current delinquency cycle, unless the agreement's own AutoPay records say otherwise: where an AutoPay draft on this agreement for that due date was declined ..."; compute `lf_anchor` keys on `F('delinquent_since')` and scopes `XCOUNT/XLATEST/CFIELD` to `agreement_id=HID`. Rule and compute now agree. **Closed.**
- **F7 (BEC err_fee)**: rule now reads "billing errors are corrected on the agreement's most recently posted late fee, with one billing-error correction credit against that fee entry ... The billing-error correction credit is the most recently posted late fee in full", matching `err_fee: LATEST(... late_fee)`; `rec_cap` now counts all late fees "the corrected one included" (≤2 / 3–4 / ≥5) = compute. Rule↔compute divergence **closed**, but closed by rewriting the rule into one that conflicts with the LF and PAY prerequisite sentences → new finding **N1** below.
- CON: new AutoPay adjustment (+clean share / −lapsed reduction / 0) and `gap_short_months: 18` ("close-increase months") — rule and compute equivalent. RED `pt_dispatch`: rule now "the near-tow hold where that date is no more than the near-tow days away ... and nothing where it is further away", compute dropped the notice-count guard — equivalent within RED's scope. SW `sw_level`: class fee + repeat step / + returning step / class fee — equivalent.
- Charter-wide observations from round 1 (MONTHS month-end fallback, rounding mode, first active unit) unchanged.

### action_binding_and_uuids (round 2)
`task_tools.py` hash unchanged → round-1 section carried forward by hash. Targets and `computes` unchanged in the charter.

### prerequisite_graph / prerequisite_sentences (round 2)
Edges E1–E6 unchanged (same `problem`, `kind`, `gate`, `form`, `policy_source`, `condition`, `resolved_by`); each `policy_source` re-located verbatim in the round-2 rules. Acyclic. State-form uniqueness as round 1 (E4 observation stands). No new cross-problem order in any rule.

### override_declarations (round 2)
- **BEC**: now declares base "A late fee posted against a period paid within grace is a billing error and is credited as billing_error_correction without using the courtesy allowance." superseded by the amount sentence. **F1 closed** (merged amount unique: the corrected fee + service recovery + allowance).
- **RED**: now declares base clause "after the tow notice only a payment of the full balance is accepted, and it returns the agreement to active and restores the gate code." superseded by "only a payment of the full redemption amount ...". The first half of the base sentence ("While delinquent, payments of any amount are accepted;") stays for PAY. **F2 closed.** Observation: base lifecycle text "tow_noticed → active: The tenant pays the full balance, including the tow notice fee, before the tow." still describes redemption as paying the full balance; it is transition prose, not an acceptance rule, so no second accepted amount is fixed by it.
- **TF**: overwrite narrowed to the clause "posts tow_notice_fee_usd" (delivery method and status move retained). Observation closed.
- **SW**: compliance overwrite narrowed to "A renewed registration or insurance is recorded when the tenant states the new expiry date exactly as printed on the document" (cure-return clause retained); swap overwrite narrowed to "and each swap posts vehicle_swap_fee_usd."; the rule now states "at most the swap allowance of the space class times in any rolling 365-day window". Observations closed (T1-3's object restored).
- CON: unchanged declarations (amount; increase-status → balance gate). Round-1 observation stands.

### factor_ladders (round 2)
- **F3 closed**: `swap_sequence_level` = class fee + 10 / class fee + 5 / class fee — three distinct values on every class.
- **F4 closed**: `tow_dispatch_cancellation` tiers are now the earliest-tow-date distance alone; no part restates RED's scope. RED keeps 4 factors (single-source is permitted; RED's task still has multi-source factors elsewhere).
- **F5 closed**: `cumulative_increase_measure` tier 1 is now "less than the close-increase months (18)"; with interval 12 (or 11) a concession-eligible increase can be noticed 12–17 months after the last change, so all three tiers are reachable on every class.
- CON `autopay_record_adjustment` (renamed): +0.03 / −0.02 / 0 — distinct; conditions (authorization status and its declines / its suspension date) are ones an operator weighs; fall-through 0 = baseline.
- Counts unchanged: BEC 5 (3P/2M), LF 6 (3P/3M), PAY 4 (3P/1M), CON 5 (4P/1M), TF 4 (3P/1M), RED 4 (3P/1M), SW 6 (4P/2M). Label-honesty and realism observations from round 1 unchanged.

### findings (round 2)
- Closed: F1, F2, F3, F4, F5, F6, F7 (the divergence itself), override-scope observations (TF, compliance, swap).
- **N1 — SOURCE-POLICY RED (new, introduced by the F7 rework).** Two passages: BEC rule "A late fee posted against a billing period whose rent was paid within its grace period is a billing error; billing errors are corrected on the agreement's most recently posted late fee, with one billing-error correction credit against that fee entry" vs LF rule "A late fee for an unpaid period is not posted until each earlier late fee that was charged against a period paid within its grace period carries a billing-error correction credit on the ledger" (and PAY's "... not fixed until every late fee posted against a period paid within its grace period carries a billing-error correction credit"). Situation: late fee A posted against a June period paid within grace, then late fee B legitimately posted against an unpaid July period. BEC → the credit goes against B (the most recent late fee, itself not an error), A carries no credit; LF/PAY → A must carry a credit, so the gate never opens through BEC's write, or the agent credits A against BEC's rule. Different conclusions in the same situation; also a correction credited to a fee that is not in error. Bears on task 0 structurally; on task 0's world the erroneous fee `b6f46216` is the most recent late fee at BEC's handling time, so no consequence there.
- Carried observations: E4 several balance-lowering tools; PAY leaves status `delinquent`; multiplier/share `method` labels; unexercised claimed event types; DSL month-end/rounding; CON increase-status declaration; residual lifecycle prose for redemption (new, above).

### closing_checklist (round 2)
Written 2026-10-10T21:02Z, after both round-2 reveals.
- Audit files `_difficulty.md`, `0.md`, `1.md`, each with round-1 text untouched and a `revision_2` appended (frozen before reveal, comparison after).
- Per-task: task 0 **PASS**, task 1 **PASS** on all four relationships; every round-1 task RED (T0-1..T0-4, T1-1..T1-3) verified closed; no regression found.
- Coverage/scope: 7/7 extended policies, scopes disjoint and equal to `charter_scope`; tools and uuid8s unchanged (hash).
- Trees: task 0 n=3 with 3 value_input edges, task 1 n=2 with 1; one user write each; difficulty edge set acyclic.
- Factors: every computation 4–6 factors (≥2 P, ≥1 M as labelled), every ladder three distinct reachable tiers (F3/F5 closed), no scope-restating condition (F4 closed), each factor bears weight against an honest baseline with whole-baseline ≠ gold on both worlds; cross-difficulty rows present and consistent with their charters.
- Charter-global: F1, F2, F6, F7 closed; **N1 (new) open** — BEC's "billing errors are corrected on the agreement's most recently posted late fee" conflicts with LF/PAY's prerequisite sentences whenever the erroneous fee is not the latest late fee. No consequence on either task world, but the charter is not self-consistent; the difficulty does not close at charter level while N1 stands.
- Gates: not re-run by the auditor; coordinator's round-2 snapshot cited; final hashes `0d3b2cfc…db8f` / `a3f2ce03…9f15b84`.

## revision_3

### charter_global_frozen (round 3)
- Frozen 2026-10-10T21:38Z, before either round-3 task file was opened.
- Hashes: `parking.extended.yaml` **changed** → `e37a4a762458802d87f6c04f3bdaca83a80e12ebf8dad8609e80eb2c0f4d102f`; `task_tools.py` unchanged `a3f2ce03…9f15b84`; views unchanged (`4178608d…c7ff`, `aa52555f…505a`). Base section still structurally equal to `blueprint/products/parking.yaml`.
- Scope of the change: only `parking_ext_billing_error_correction` (BEC) moved. Every other policy was re-checked for the round-2 load-bearing text (LF anchor sentence, CON close-increase months 18 and lapsed-AutoPay reduction, TF/RED/SW narrowed overwrites, SW swap step and allowance, RED date-only dispatch tiers, all six prerequisite sentences) — all present; uniform 3-line offset after BEC; and the charter compute re-evaluated on both views (`/tmp/run_0051/audit_parking_rate_increase_and_compliance/blind_eval_r3.py`) reproduces every round-2 figure. Round-2 sections for LF, PAY, CON, TF, RED, SW, the prerequisite graph and sentences, and action binding (tools hash) carried forward.
- contamination_disclosure: round-1 and round-2 GT seen after their freezes; the brief carries item ids only. Round-3 derivation uses the round-3 charter and the unchanged views.

### BEC re-derivation (round 3)
- Rule now: "A late fee posted against a billing period whose rent was paid within its grace period is a billing error, and each such late fee is corrected with one billing-error correction credit against that fee entry, without using the courtesy allowance." The credit object is the erroneous fee itself, so it agrees with LF's "each earlier late fee that was charged against a period paid within its grace period carries a billing-error correction credit" and PAY's sentence. **N1 closed.**
- Amount basis: "The billing-error correction credit returns the agreement's standard late fee, which is the greater of the flat late fee and the standard late-fee percentage of the contracted monthly rent, the percentage amount rounded to the cent, never more than the late-fee ceiling, and adds a service-recovery amount to it." Compute `err_fee: MN(P('late_fee_max_usd'), MX(P('late_fee_flat_usd'), RND(P('late_fee_pct_of_rent') * F('monthly_rent'), 2)))` — equivalent. Same definition as LF's "standard late fee" sentence — consistent.
- Ceiling: "no more than two late fees of any kind, erroneous or not ... three or four ... five or more" = compute (≤2 / ≤4 / else). Equivalent.
- Override: declared overwrite still names the base billing-error sentence; replaced_by now says "the correction credit is the standard late fee plus ...". Merged semantics unique.
- Factors unchanged (5: 3P/2M; distinct tiers; fall-through = baseline). `baseline.rule` now carries the standard late fee + standard recovery and lists `late_fee_flat_usd, late_fee_pct_of_rent, late_fee_max_usd` in params — self-sufficient, every sentence in the rule.
- **Observation (new, no demonstrable consequence on either world):** the credit no longer equals the fee it corrects. The extended late fee can be posted below the standard fee (proration, rebate, tenure minimum 10.00) or above it (cycle multiplier ×1.25/×1.5 after the ceiling), so a correction can return more than was charged (e.g. a 16.00 fee corrected with 30.00 + recovery) or leave part of an erroneous charge standing (e.g. a 45.00 fee corrected with 30.00 + recovery ≤ 25 + allowance). No other charter sentence fixes the correction amount, so no passage conflict; recorded for the business-realism record. On task 0 the erroneous fee as posted (30.00) equals the standard fee (30.00), so either reading gives 62.05.

### findings (round 3)
- N1 closed. No new RED. Carried observations unchanged (E4 several balance-lowering tools; PAY leaves status delinquent; multiplier/share `method` labels; unexercised claimed event types; DSL month-end/rounding; CON increase-status declaration; redemption lifecycle prose) plus the correction-amount observation above.

### closing_checklist (round 3)
Written 2026-10-10T21:38Z, after both round-3 reveals.
- Audit files `_difficulty.md`, `0.md`, `1.md`; rounds 1–2 text untouched, `revision_3` appended (frozen before reveal, comparison after).
- Per-task: task 0 **PASS**, task 1 **PASS** on policy self-consistency, problem tree, factors and unique solution; no regression from round 2 (every scored value, factor figure and load-bearing figure identical).
- Charter-global: N1 **closed** (correction scope = each erroneous fee, matching the LF/PAY prerequisite sentences); F1–F7 remain closed; no open RED. Base copy verbatim; tools and uuid8s unchanged; prerequisite graph acyclic with every sentence verbatim in its blocked rule.
- Coverage/scope: 7/7 extended policies; task scopes disjoint and equal to `charter_scope`.
- Trees: task 0 n=3 / 3 value_input, task 1 n=2 / 1 value_input; one user write each.
- Factors: 4–6 per computation, ≥2 P / ≥1 M as labelled, three distinct reachable tiers per ladder, each bears weight against an honest baseline, whole-baseline ≠ gold; cross-difficulty rows present and charter-consistent.
- Open observations only (no RED): E4 several balance-lowering tools; PAY leaves status `delinquent`; multiplier/share `method` labels; unexercised claimed event types; DSL month-end/rounding; CON increase-status declaration; redemption lifecycle prose; correction credit built on the standard late fee rather than the fee as posted.
- Gates: not re-run by the auditor; coordinator's round-3 snapshot cited; final hashes `e37a4a76…102f` / `a3f2ce03…9f15b84`.
- **The difficulty passes the source-layer audit.**

## revision_4

### charter_global_frozen (round 4)
- Frozen 2026-10-10T22:37Z, before either round-4 task file was opened.
- Hashes: `parking.extended.yaml` **changed** → `a3ed90934d3db09f2ec48679fe167613aa4ec85108368b685a62cde9eeaa3290`; `task_tools.py` unchanged; views unchanged (`4178608d…c7ff`, `aa52555f…505a`). Base section structurally equal to `blueprint/products/parking.yaml`.
- Additional input read this round, at the coordinator's direction: the "Policy-side notes" paragraphs of `audits/policy_kb/parking_rate_increase_and_compliance/0.md` and `1.md` (KB-doc audit). They carry no scored value.
- contamination_disclosure: rounds 1–3 GT seen after their freezes; views unchanged, so the round-4 derivation is a re-evaluation of the changed charter on the same worlds.
- Mechanical re-checks (`/tmp/run_0051/audit_parking_rate_increase_and_compliance/struct_r4.py`): every `overwrite.superseded_clause` is a verbatim substring of its base rule; every prerequisite `policy_source` is verbatim in its blocked rule; every `compute_basis` sentence is in its rule; factor counts/labels unchanged (BEC 5, LF 6, PAY 4, CON 5, TF 4, RED 4, SW 6). Compute re-evaluated on both views (`blind_eval_r4.py`): every scored value, factor substitution, whole-baseline and load-bearing figure identical to round 3.

### changes and their checks (round 4)
- **CON overwrite[1] / KB note 0-1.** Base "Increase notices go only to agreements in active status." is now replaced by "Increase notices go only to agreements in active status; that standing requirement governs the sending of an increase notice and not the recording of a retention concession on an increase already noticed.", and the CON rule carries that sentence. The increase-notice standing rule is kept in force for increases and scoped away from concessions; the concession's own standing test stays the balance sentence (E4). Merged semantics unique; the round-1 observation ("the charter now carries no statement that increase notices themselves are limited to active agreements within this policy's reach") is **closed**. The sentence names no tool, policy id or other problem and states no cross-problem order.
- **PAY deferral wording / KB note 0-2.** "may leave the ... deferral" → "has the ... deferral left on the next statement" (loyal, bundle) and "the long-lockout deferral is left ..." (lockout); result sentence adds "each deferral being left on the next statement rather than collected". Compute unchanged; rule↔compute equivalent. Auditor's note: rounds 1–3 read the permissive tier wording together with the result sentence "less every deferral that applies" as fixing a single amount and raised no finding; the KB auditor's reading (the tenant could decline a deferral, giving a second payable amount) was a defensible second reading the earlier rounds did not record. With the mandatory wording that second reading is gone.
- **SW overwrite / KB note 1-1.** New declared overwrite: base clause "A different vehicle may be put on file only on an agreement in active status" superseded by the prerequisite sentence "A different vehicle is not put on file until the agreement stands in active status." The base sentence now splits into three clauses: active-status (superseded → E6's sentence), swap allowance (in force; also restated in the SW rule), fee (superseded). E6 is now stated once, on the blocked side. Remaining observation: base `parking_evt_vehicle_fit` "Vehicle details are changed only while the agreement is in active or termination_noticed status." (eligibility `swap_status`) still applies to every `parking_vehicle_update`; for a tow_noticed agreement it reaches the same conclusion (blocked until active), it states no cross-problem order, and the extended rule carries its own prerequisite sentence, so it is not a second wording that changes any reading.
- No other policy text changed in a way that moves a rule, factor, ladder, baseline or prerequisite.

### findings (round 4)
- No round-3 RED was open; nothing regressed; no new RED.
- KB policy-side notes 0-1, 0-2, 1-1: closed by the source changes above. Notes 0-3 (task-0 proof text) and 1-2 (tools do not block) are task-file matters — checked in `0.md`/`1.md` after the reveal. Note 0-4 (lifecycle delinquent → active) = the carried observation "PAY leaves status delinquent".
- Carried observations unchanged: E4 several balance-lowering tools; PAY leaves status delinquent; multiplier/share `method` labels; unexercised claimed event types; DSL month-end/rounding; redemption lifecycle prose; correction credit on the standard late fee; (new) base `swap_status` sentence beside E6.

### closing_checklist (round 4)
Written 2026-10-10T22:38Z, after both round-4 reveals.
- Audit files `_difficulty.md`, `0.md`, `1.md`; rounds 1–3 untouched, `revision_4` appended (frozen before reveal, comparison after).
- Per-task: task 0 **PASS**, task 1 **PASS** on all four relationships; no regression (every scored value, factor figure, baseline and load-bearing figure identical to round 3).
- KB policy-side notes: 0-1, 0-2, 1-1 closed by source changes; 0-3 closed in `tasks/0.json` (and recorded as a miss of this auditor's rounds 2–3); 0-4 and 1-2 are carried observations / correct statements.
- Charter-global: no open RED; overwrites verbatim, prerequisite sentences verbatim and stated once on the blocked side, rule↔compute equivalent, ladders distinct and reachable, baselines honest; tools/uuid8s unchanged.
- Gates: not re-run by the auditor; coordinator's round-4 snapshot cited (all OK incl. TRACEABILITY OK, validate_scenario VALID); final hashes `a3ed9093…3290` / `a3f2ce03…9f15b84`.
- **The difficulty passes the source-layer audit.**
