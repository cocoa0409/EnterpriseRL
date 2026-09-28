# Policy-task audit — appointment_scheduling_and_attendance / charter-global

## charter_global_frozen

- Freeze time: 2026-09-25T04:33:04Z (revision 1), which is the file's mtime. Written before any task's GT was revealed; the reveal began at 04:35:06Z. Nothing in this section comes from a revealed GT.
- Auditor: erl-task-policy-audit run (Claude Opus 5.5 subagent). It is independent of the agent that wrote the artifacts and did not see that agent's worklog.
- Frozen inputs (sha256):
  - `tasks/appointment_scheduling_and_attendance/appointment.extended.yaml`: `cc8c3713ef9b5f4b737fa44f28b1979bca882d9856d184829251fb67763e949c`. This matches the coordinator's charter hash.
  - `tasks/appointment_scheduling_and_attendance/task_tools.py`: `dab3bbca6c0147acc0c96c8aee191d5f0f0353920c9680a65e905149e206b46a`. This matches the coordinator's hash.
  - `blueprint/products/appointment.yaml`: `62bf7a8abb49975834c1a9b738be70a4193f1d7763b212c27a4c9bccac45e017`
  - `blueprint/share_tools.py`: `a0a0f97cfe8ff283a321f98b65438df91df3a66a2b28da85db4b037977fda812`
  - `blueprint/db_schema.json`: `8c0093f9b12ee9c621328049827deee2f6f110bff3eb4909442f3b873710a85f`
- Fields read: the blueprint (`blueprint.yaml`, `db_schema.json`, `share_tools.py`, `products/appointment.yaml`, and the tier and ledger passages of `products/billing.yaml`), the extended charter, `task_tools.py`, and the two coordinator masked views (`r1/0.view.json` sha256 `3f851b06…`, `r1/1.view.json` sha256 `66747c0e…`, with frozen_time, user_scenario and initial_state only). The DSL primitive semantics were read from `skills/erl-task-instantiate/scripts/check_compute.py` (`build_env`: MONTHS, DAYS, SUM, XCOUNT and CFIELD).
- Fields masked (not read before the freeze): the whole of `tasks/*.json` (evaluation_criteria, computations, charter_scope, required_documents, design_rationale, solvability_contract, prerequisite_closure), `tasks/.../worklog.md`, the scenario `worklog.md`, and every other `audits/` subdirectory.
- Entry conditions (Step 0): the coordinator supplied a gate snapshot with all seven gates green: EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK and SCOPE OK. check_traceability was deferred until the KB is published. The masked views and their hashes were supplied. The entry conditions are complete, and they are cited here, not re-run.

### policy_conflict_scan

The charter has seven base policies copied verbatim and seven extended policies. A YAML-level equality check of every base key against `blueprint/products/appointment.yaml` came back `True` for all nine keys, and the only extra key is `extended_policies`. The seven extended policies, with the short labels used below:

| Label | Policy id | target_tool (owner) | computes | prerequisite |
| --- | --- | --- | --- | --- |
| P1 | appointment_ext_cancellation_notice_days | cancel_patient_appointment_f57629ba (agent) | cancel_timing | [] |
| P2 | appointment_ext_late_cancel_fee_prohibition | record_late_cancel_fee_prohibition_784c7051 (agent) | amount | P1 (value_input, state) |
| P3 | appointment_ext_late_cancel_deposit_refund | refund_late_cancel_deposit_f012ee38 (agent) | amount | P2 (value_input, state), P4 (state_gate, state) |
| P4 | appointment_ext_self_pay_booking_deposit | pay_booking_deposit_d4a062b3 (user) | amount | [] |
| P5 | appointment_ext_no_show_fee_prohibition | record_no_show_fee_prohibition_783ac881 (agent) | amount | [] |
| P6 | appointment_ext_missed_visit_deposit_refund | refund_missed_visit_deposit_4264223f (agent) | amount | P5 (value_input, state), P7 (state_gate, state) |
| P7 | appointment_ext_moved_visit_deposit_balance | pay_deposit_balance_07a1fa0e (user) | amount | [] |

Where the subjects overlap:
- P2 and P5 both write `appointment_fee_waived`. They split cleanly: P2 covers a late-cancelled visit and `fee_type late_cancel_fee`, P5 a no-show visit and `fee_type no_show_fee`. Both fire only when the account was on the Medicaid Managed Care Account tier on the scheduled date, which is the same trigger as base `appointment_no_show_fee` ("no no-show or late-cancellation fee is ever charged; the waiver is recorded with reason medicaid_prohibition"). They are compatible.
- P3 and P6 both write `appointment_deposit_released`. The split is late cancellation against no-show. Both supersede the same base clause of `appointment_booking_deposit` ("on a no-show or late cancellation it is forfeited toward the fee…"), and each replacement is scoped to one of the two cases, so the merged semantics are unique per case.
- P4 and P7 both write `appointment_deposit_collected`. P4 covers a visit booked on the Self-Pay Account tier whose booking deposit was not collected at booking. P7 covers a moved visit that already holds a deposit. The two scopes are disjoint in every world where both rules are read: P4 needs "not collected at booking", P7 needs "holds a booking deposit".
- Time anchors: P1 uses the handling date. P2 and P3 use `cancelled_at` for the notice and move tiers, P5 and P6 use the handling date, and P4 and P7 use the payment date (the handling date). See finding F2 for the one anchor that drifts.
- Cross-category reads: `billing` (the ledger count of `no_show_fee` and `late_cancel_fee` charges, `patient_balance` and `opened_date`) and `payplan` (`status`). Every read is declared in `cross_category`.
- Terminal states: P1 moves the appointment to cancelled with the timing class. P2 and P5 add one waiver row each. P3 and P6 add one refund row each and lower `deposit_held_usd`. P4 and P7 add one card deposit row each and raise `deposit_held_usd`. No two policies write the same field of the same row.

Task scopes, derived blind from the prerequisite graph plus the two worlds and confirmed after the reveal in each task file:
- Task 0 = {P1, P2, P3, P4}, with P3 as the root.
- Task 1 = {P5, P6, P7}, with P6 as the root.

The two scopes are pairwise disjoint and together cover all seven extended policies.

The scan found two conflicts, recorded in `findings` as F1 (undeclared overrides of the timeliness definition) and F2 (fee-history window anchor drift in P2 and P3).

### rule_compute_equivalence

Check 2 was run sentence by sentence. A scratch script confirmed that every `compute_basis` quotation is a verbatim sentence of its policy's `rule`, and that every `baseline.rule` sentence also appears verbatim in the `rule`.

- **P1.** notice_calendar_days is `DAYS(NOW, scheduled_date)`, quoting "the cancellation date not counted and the scheduled date counted" (✓). The preparation anchor has three branches (≥3 days: less the prep days; 1–2 days: less 1; none: as counted) (✓). Fee history is `XCOUNT(billing_charge_posted` × `{no_show_fee, late_cancel_fee}`, within_months 12 on `service_date)`, quoting "posted with a date of service less than 12 whole months before the cancellation date". MONTHS<12 matches "less than 12 whole months", and the anchor is NOW, which is the cancellation date because P1 is the cancellation (✓). The move rise is `reschedule_count>=1` → `DAYS(last_rescheduled_date, NOW)` with ≤30 / >30 / never (✓). The booking lead is `DAYS(booked_date, scheduled_date)` with ≥60 / 30–59 / <30 (✓). base_required_days is `(h+23)//24`, quoting "divided by 24 and rounded up" (✓). The rises are additive, and the prep reduction applies only to the days given (✓). The binding `prep_days` has no basis entry of its own, but it is only the parameter read that the notice_days_given basis quotes. This is an observation and invents no basis.
- **P2.** The 0/1 lateness switch is stated in the rule ("nothing when it is recorded with any other timing") (✓). The notice starting amount is `DAYS(cancelled_at, scheduled_date)` with ≥4 / ≤1 / 2–3 (✓). The multiplier ladder, the unpaid-balance ladder (balance >0 AND count ≥1 / balance >0 AND count 0 / none), the move ladder (`DAYS(last_rescheduled_date, cancelled_at)`), the deposit-credit ladder (≥150 / >0 / none) and the order (multiply, then add, then subtract, rounding only at the end) all match (✓). **Drift**: the rule counts fees with a service date "less than 12 whole months before the cancellation date", but compute's XCOUNT window is anchored on NOW (see F2).
- **P3.** held = collected − released (✓). waived = SUM of `appointment_fee_waived` rows with `late_cancel_fee` (✓). The five offset ladders mirror P2 word for word, with anchors on `cancelled_at` (✓). The fee is rounded before it enters the refund (✓). result = held − offsets + waived (✓). The same fee-history window drift applies (F2). `deposit_held_on_visit` has no basis key of its own, but its sentence is quoted under `deposit_collected_total`. This is an observation.
- **P4.** Multiplier ×2 / ×1.5 / ×1 (✓). Lead ≥45 → −25, <14 → +50, else 0 (✓). Balance >100 → +50, >0 → +25 (✓). Account age `DAYS(opened_date, NOW)` ≥1826 → −25, 730–1825 → −10 (✓). Order and rounding match (✓). Window anchor: the payment date, which is NOW (✓).
- **P5.** The 0/1 switch on no_show (✓). The multiplier counts only no_show and late_cancel charges, and "charges of any other kind, such as virtual-visit fees, are not counted" is implemented by the line_category filter (✓). Unpaid +20/+10 (✓). Held slot ≥90 → +25, 60–89 → +15 (✓). Deposit credit ≥200 → −20, >0 → −10 (✓). Confirmation `DAYS(confirmed_date, scheduled_date)` ≤2 → +25, >2 → +15, never → 0 (✓). Plan active → −15, delinquent/defaulted → +15 (✓). Window anchor: "the day the fee is decided", which is NOW (✓).
- **P6.** Mirrors P5 for the offset. Window anchor: "the refund date", which is NOW (✓). result = held − offsets + waived (✓).
- **P7.** held = collected − released (✓). Multiplier ×2 / ×1.5 / ×1 (✓). Move lead `DAYS(last_rescheduled_date, scheduled_date)`, falling back to `booked_date` for a visit never moved, with <14 → +50, 14–44 → +25, ≥45 → 0 (✓). Balance and age as in P4 (✓). The required deposit is rounded before `MX(0, required − held)`, quoting "nothing where that difference is zero or less" (✓).

Sweeping back from compute to rule: no compute binding brings in a basis that is absent from the rule, and no rule sentence lacks an implementation. Every factor ladder's tiers are sentences of the rule and branches of the `decides` binding, and the reverse also holds. The only exception is the anchor drift in F2.

### action_binding_and_uuids

- Each `(target_tool, computes)` pair is claimed by exactly one policy, and all seven tools are distinct.
- The uuid8 tails are `f57629ba`, `784c7051`, `f012ee38`, `d4a062b3`, `783ac881`, `4264223f` and `07a1fa0e`. They are pairwise distinct, none is a copy of another with a changed tail, and there is no sequence or common-prefix pattern. `784c…` and `783a…` share two leading hex digits. For 7 random tails, some pair sharing 2 of 256 prefixes has probability ≈8%, so this is not evidence of batch derivation.
- Each docstring describes only its own effect, and no docstring names another tool. Every write docstring carries "Afterwards …", which describes the post-call state of that same call and does not place the call in a sequence with other tools. This is an observation. `cancel_patient_appointment_f57629ba` also says "no fee, waiver or refund entry is written". That states its own non-effects and names no follow-up, and is also an observation.
- Tool bodies: none of the seven functions reads eligibility, refuses a call, or checks another problem's state. Each does `ctx.find` on the appointment only to copy customer_id, encounter and scheduled date, then writes. So the tool layer validates no prerequisite.

### prerequisite_graph

Check 7:
- **`prerequisite` present.** Every policy fills in `prerequisite`: `[]` for P1, P4, P5 and P7.
- **Edge targets.** All six `problem` values name extended ids of this file. None names a base policy or the policy itself.
- **Acyclic.** The graph has the edges P1→P2→P3, P4→P3, P5→P6 and P7→P6, and no cycle, within a task or across tasks.
- **`policy_source`.** Each is verbatim locatable in the blocked policy's own `rule` (scripted check: True ×6).
- **`form`.** All six edges are `state`, and none carries a `fallback_reason` (consistent).
- **`resolved_by`.** Each equals the depended-on policy's `target_tool`, and that tool's effect makes the stated condition hold:
  - `cancel_patient_appointment` sets status cancelled with a timing class.
  - `record_late_cancel_fee_prohibition` and `record_no_show_fee_prohibition` add the waiver row.
  - `pay_booking_deposit` and `pay_deposit_balance` add a deposit row dated today.
- **`kind` against `gate`.** The value_input gates `cancel_is_late` (P2), `fee_recorded_as_waived` (P3) and `no_show_fee_recorded_as_waived` (P6) are real compute bindings (✓). The state_gate gates `appointment_events.event_type` (P3←P4) and `appointment_events.event_date` (P6←P7) are DB fields, not eligibility gates: P3 and P6 declare no `eligibility` block. Observation: the gate metadata points at a field, but the gate is stated by the prerequisite sentence, so the agent can still discover it.
- **`condition` strength.**
  - P2←P1 adds "a cancellation timestamp" to "shows it cancelled with a timing class". The only writer sets both, so this is an observation.
  - P3←P2's condition narrows the sentence's "the decision on its late-cancellation fee" to "(a waiver entry for fee type late_cancel_fee)". A decision could also be an assessed fee, but this difficulty has no assessing tool, and on the Medicaid tier the charter permits only the waiver. Observation.
  - P6←P5 is the same as P3←P2. Observation.
  - P6←P7's sentence says "a deposit entry", while the condition says an `appointment_deposit_collected` entry. Observation.
- **Wording.** No authoring-viewpoint wording ("this task", "at the opening", "current world") appears in any `prerequisite` field (scripted check).

### prerequisite_sentences

Check 6, edge by edge:

1. **P2←P1** — "The late-cancellation fee the visit carries is fixed only after the visit's appointment record shows it cancelled with a timing class."
   - Connective: "only after".
   - State form: a record-visible state, "appointment record shows it cancelled with a timing class", naming no tool, id or snake_case token.
   - Resolving write: the only write of this difficulty that sets `status=cancelled` with a `cancel_timing` is P1's tool. Derivation: sentence → the appointment must show cancelled with a class → P1's rule is the only rule that records a cancellation's timing class → `cancel_patient_appointment`. One reading.
2. **P3←P2** — "The deposit refund on a late-cancelled visit is fixed only after the visit's fee and deposit history shows the decision on its late-cancellation fee."
   - Connective: "only after".
   - State form: fee-and-deposit history shows the decision.
   - Resolving write: the only write here that records a late-cancellation-fee decision is P2's waiver. There is no assessment tool, and on a Medicaid visit the base rule forbids a charge. One reading.
   - Observation: P3's first rule sentence restates this dependency in action form, "…is refunded to the patient, as one refund entry, once the visit's late-cancellation fee is decided." That is a second wording of the same edge. It grounds the same declared edge and reaches the same conclusion, so no consequence is demonstrable.
3. **P3←P4** — "A deposit on a late-cancelled visit is not refunded until each open visit the patient booked on the Self-Pay Account tier shows a booking deposit collected on it."
   - Connective: "not … until".
   - State form: named in table words, with no tool.
   - Resolving write: P4 applies ("a booking deposit not collected at booking stays owed while the visit is open"). P7 does not, because P7's scope is a moved visit that already "holds a booking deposit", and a visit with no deposit holds none. One reading.
4. **P6←P5** — "The deposit refund on a missed visit is fixed only after the missed visit's fee and deposit history shows the decision on its no-show fee."
   - Analogous to edge 2, with P5's waiver as the only writer.
   - The same second wording occurs in P6's first sentence ("once the missed visit's no-show fee is decided"). Observation.
5. **P6←P7** — "A deposit on a missed visit is not refunded until each open visit the patient moved shows a deposit entry dated on or after that visit's latest move."
   - State form.
   - Candidate writers: P7 and P4 both create deposit rows. For a moved visit whose booking deposit was already collected, P4's "not collected at booking stays owed" does not hold, so only P7 applies. For a moved visit with no deposit at all, P7 does not apply, and P4 applies only if the visit was booked on the Self-Pay tier. The reader resolves the hop from the records, and in no world do both candidates apply at once.
   - Observation (charter-level, no task consequence): where P7 evaluates to 0.00, or where a moved open visit holds no deposit and was booked on an insured tier, no write of this difficulty can produce the waited-on state. P6's refund is then barred indefinitely.

Other points:
- No rule names another problem's tool or policy id.
- No depended-on rule restates the blocked sentence.
- No rule states a cross-problem order beyond the declared edges and the two action-form restatements noted above.
- The base event field `appointment_cancelled.deposit_held_usd` ("…released under the deposit rules once any fee is decided") is a base sentence with an ordering. The tree's P3←P2 edge rests on its own extended sentence, so this is an observation only.
- The docstrings are silent about sequence (see above).

### override_declarations

Check 1, the finding half. Each `base_policy_refs` entry was checked sentence by sentence.

- **P1**, refs `appointment_cancellation_timing` and `appointment_reminders_and_release`.
  - s1 (cancel any time before check-in, recorded with its timing): followed.
  - s2 (timely = full elapsed hours ≥ cancel_notice_hours): **declared** overwrite.
  - s3 (clinic cancellation → clinic_initiated, no fee): followed (P1: "A cancellation made by the clinic is outside this rule").
  - s4 (late arrival → timing late): compatible; P1 gives late on the same day in any case.
  - s5 (late cancellation is charged late_cancel_fee_usd): declared by P2.
  - s6 (fee only when timing late): followed.
  - **s7, "A request to cancel less than cancel_notice_hours before the start in order to rebook is a late cancellation of this appointment followed by a new booking, never a reschedule.": NOT declared.** It still classifies lateness by hours (F1).
  - reminders_and_release: every sentence is followed.
  - Outside P1's refs, `appointment_reschedule` still gates a reschedule on "the notice for a timely cancellation still holds (at least cancel_notice_hours of full elapsed hours before the current start)". After P1, "the notice for a timely cancellation" names a different measure (F1, second instance).
- **P2**, refs `appointment_fee_waiver`, `appointment_cancellation_timing` and `appointment_no_show_fee`.
  - fee_waiver: s1 is compatible (it concerns an assessed fee). The documentation window s2 and "A fee is waived at most once" s4 are **declared**. They were superseded because base's `waive_once` dedup keys on `applies_to_event_id`, which is `""` for every at-assessment waiver, and the `documentation_window` eligibility applies to all `appointment_fee_waived`. s3, s5 and s6 are followed; the waiver is in full, not partial.
  - cancellation_timing s5: **declared**.
  - no_show_fee: the Medicaid sentence is followed (reason medicaid_prohibition, never charged), and so is precedence over first offense.
  - Anonymous intermediate: none. The fee amount's divergence from the base formula `amount: late_cancel_fee_usd` is carried by the declared s5 overwrite.
  - 0/1 multiplier: `cancel_is_late` is stated in the rule and agrees with base s6.
- **P3**, refs `appointment_booking_deposit` and `appointment_cancellation_timing`. The forfeiture/refund clause is **declared**. "A patient who gains insurance before the visit keeps the deposit…" is followed. Base `forfeited_usd = min(held, fee actually charged)` gives 0 under the prohibition, which is compatible.
- **P4**, ref `appointment_booking_deposit`. s1 is **declared**. The replacement drops "(none where it is 0.00)", and P4's result has no floor. Observation: for a Nurse Visit (self_pay_booking_deposit_usd 0.00) the formula can go negative, for example 0 − 25 (lead ≥45) − 25 (tenure) = −50. Neither task has such a visit. s2 "One deposit…" is followed ("as one deposit entry").
- **P5**, refs `appointment_fee_waiver` and `appointment_no_show_fee`. The documentation window and at-most-once sentences are **declared**. "The no-show fee is the visit type's no_show_fee_usd." is **declared**. The first-offense and Medicaid sentences are followed.
- **P6**, refs `appointment_booking_deposit` and `appointment_no_show_fee`. The forfeiture clause is **declared**.
- **P7**, refs `appointment_booking_deposit` and `appointment_reschedule`. "One deposit is collected per appointment." and "A reschedule carries the deposit to the new slot." are **declared**. Every reschedule sentence is followed.

Observation (no task consequence): P2 and P5 each supersede the base emergency-documentation window with text about at-assessment Medicaid waivers. In the merged charter, the base emergency-documentation waiver path therefore loses the sentence that bounds its window, although its counting sentence remains. Neither task involves an emergency waiver.

### factor_ladders

Structure only. Whether each factor bears weight is decided per task in each task file under `factor_weight`.

| Policy | Factor | Declared effect | Tiers (fall-through last) | Honest label? | Multi-source? | cross_difficulty |
| --- | --- | --- | --- | --- | --- | --- |
| P1 | preparation_day_anchor | method | ≥3 prep days: calendar − prep days / 1–2: calendar − 1 / none: calendar | accepted, borderline (see F3 note) | no | — |
| P1 | fee_history_notice_rise | parameter | ≥2: +2 / =1: +1 / 0 | yes | no | billing |
| P1 | patient_move_notice_rise | parameter | moved ≤30d: +2 / moved >30d: +1 / 0 | yes | no (two fields of one appointment row) | — |
| P1 | booking_lead_notice_rise | parameter | ≥60: +2 / 30–59: +1 / 0 | yes | no | — |
| P2 | notice_starting_amount | parameter | ≥4d: late−10 / ≤1d: no-show fee / late fee | yes | no | — |
| P2 | fee_history_multiplier | method | ×1.5 / ×1.25 / ×1 | **no: a rate (F3)** | no | billing |
| P2 | unpaid_balance_addition | parameter | bal>0 ∧ fees≥1: +10 / bal>0 ∧ fees=0: +5 / 0 | yes | yes (billing_accounts × billing_transactions) | billing |
| P2 | patient_move_addition | parameter | ≤30d: +10 / >30d: +5 / 0 | yes | no | — |
| P2 | deposit_holder_credit | parameter | ≥150: −10 / >0: −5 / 0 | yes | no | — |
| P3 | 5 factors mirroring P2 (refund_*) | same as P2 | same as P2 | multiplier **no (F3)** | refund_unpaid yes | billing |
| P4 | deposit_fee_history_multiplier | method | ×2 / ×1.5 / ×1 | **no: a rate (F3)** | no | billing |
| P4 | booking_lead_amount | parameter | ≥45: −25 / <14: +50 / 0 | yes | no | — |
| P4 | unpaid_balance_amount | parameter | >100: +50 / >0: +25 / 0 | yes | no (balance only) | billing |
| P4 | account_age_credit | parameter | ≥1826d: −25 / 730–1825: −10 / 0 | yes | no | billing |
| P5 | no_show_fee_history_multiplier | method | ×1.5 / ×1.25 / ×1 | **no: a rate (F3)** | no | billing |
| P5 | no_show_unpaid_balance_addition | parameter | bal>0 ∧ fees≥1: +20 / bal>0 ∧ fees=0: +10 / 0 | yes | yes | billing |
| P5 | no_show_held_slot_addition | parameter | ≥90: +25 / 60–89: +15 / 0 | yes | no | — |
| P5 | no_show_deposit_credit | parameter | ≥200: −20 / >0: −10 / 0 | yes | no | — |
| P5 | no_show_confirmed_addition | parameter | ≤2d: +25 / >2d: +15 / never: 0 | yes | no | — |
| P5 | no_show_payment_plan_adjustment | parameter | active: −15 / delinquent∨defaulted: +15 / 0 | yes | no | payplan |
| P6 | 6 factors mirroring P5 (refund_no_show_*) | same as P5 | same as P5 | multiplier **no (F3)** | refund_no_show_unpaid yes | billing, payplan |
| P7 | moved_deposit_history_multiplier | method | ×2 / ×1.5 / ×1 | **no: a rate (F3)** | no | billing |
| P7 | moved_deposit_move_lead | parameter | <14: +50 / 14–44: +25 / 0 | yes | no | — |
| P7 | moved_deposit_unpaid_balance | parameter | >100: +50 / >0: +25 / 0 | yes | no | billing |
| P7 | moved_deposit_account_age | parameter | ≥1826: −25 / 730–1825: −10 / 0 | yes | no | billing |

The structural checks:
- **Bindings and `decides`.** Every factor's `bindings` are disjoint from every other factor's, and its `decides` is an input, never `result`.
- **Ladder shape.** Every ladder has ≥3 tiers that are disjoint as stated.
- **Distinct outcomes.** No two tiers of any ladder select the same value, at the charter's parameter values: late−10 ≠ no-show fee ≠ late fee for every visit type.
- **Rule and compute.** Every tier is stated in the `rule` and implemented in `compute`.
- **Baselines.** Every fall-through equals the factor's baseline, and every `baseline` is what `baseline.rule` states for that input.

**Label honesty (F3).** All six of P2–P7's `method` factors are multiplier ladders. Each tier substitutes a different rate into the same formula `start × m`. That is the skill's own example of a mislabelled effect ("a rate"). Counting honest labels only, P2, P3, P4, P5, P6 and P7 each have **0 method factors**. P1's preparation-day anchor is accepted as a method: it changes the endpoint the notice is counted to (to the prep day, the day before, or the visit day), a counting convention. The note to F3 records that it can also be written as calendar − k.

**Realism (F4).** Some tiers are ones that no physician group applies to a missed-visit or late-cancellation fee:
- the unpaid-balance surcharge on the fee (P2, P3, P5, P6);
- the booking-deposit-size credit on the fee (P2, P3, P5, P6);
- the payment-plan-status adjustment of the no-show fee (P5, P6).

Other tiers are recorded as observations only, being unusual but not demonstrably unreal: the held-slot surcharge and the confirmation surcharge (P5, P6), the move surcharge (P2, P3), P1's three rises, and the P4 and P7 deposit ladders. Deposit sizing by fee history, balance, tenure and booking lead is plausible risk-based practice.

**Counts after the tests** (honest labels and realism both applied):

| Policy | Declared | Surviving | Parameter | Method | Verdict |
| --- | --- | --- | --- | --- | --- |
| P1 | 4 | 4 | 3 | 1 | meets the bounds |
| P2 | 5 | 3 (notice, multiplier-as-parameter, move) | 3 | 0 | below 4 in all; below 1 method |
| P3 | 5 | 3 | 3 | 0 | below 4 in all; below 1 method |
| P4 | 4 | 4 (the multiplier re-labelled parameter) | 4 | 0 | below 1 method |
| P5 | 6 | 3 (multiplier-as-parameter, held slot, confirmed) | 3 | 0 | below 4 in all; below 1 method |
| P6 | 6 | 3 | 3 | 0 | below 4 in all; below 1 method |
| P7 | 4 | 4 | 4 | 0 | below 1 method |

**Task-level multi-source.** The only multi-source factors are the unpaid-balance additions of P2, P3, P5 and P6, and all of them are struck by F4. With those struck, neither task keeps a multi-source factor. Without F4, both tasks would have one.

**Task-level cross-difficulty.** Task 0 has P1's fee_history_notice_rise (billing), which is not struck. Task 1 has P5's multiplier, which reads billing and survives as a parameter.

**Structural observation (O-SC, charter-wide).** P3's `fee_refund_offsets` is literally P2's `result` formula. P6's `no_show_fee_refund_offsets` is literally P5's. At P3's handling moment every input of that formula equals its value at P2's moment, and the same holds for P6 and P5: no write of either tree touches the billing ledger, the account, the plan, or the target visit's `cancelled_at`, reschedule fields or deposit-collected rows. So in every world of this charter, P3 = held − W + W = held whenever W is the recorded waiver, and P6 likewise. The root refund therefore equals the whole deposit held, whatever tiers the ladders select, as long as the agent's own waiver amount and refund offset agree. Each task file demonstrates this on its own world. Under the skill's substitution test, where the preceding writes are held at gold, each root factor still moves the root value, so this is recorded as an observation, not a RED.

### findings

- **F1: SOURCE-POLICY RED, charter-global. Undeclared overrides of the timeliness definition.**
  - Symptom: P1 replaces the base hours-based "timely" definition with notice days, but two base sentences still decide lateness or timely notice by full elapsed hours.
  - Root cause: P1's `overwrite` names only `appointment_cancellation_timing` s2. It leaves s7 of the same policy, which is in P1's `base_policy_refs`, and `appointment_reschedule`'s parenthetical.
  - Evidence 1: base `appointment_cancellation_timing` rule, "A request to cancel less than cancel_notice_hours before the start in order to rebook is a late cancellation of this appointment followed by a new booking, never a reschedule." Against it, P1's rule: "A patient cancellation is timely when the notice days it gives are at least the notice days the visit requires, and late otherwise."
  - Consequence 1: take a Nurse Visit (cancel_notice_hours 24, prep 0), no fee history, never moved, booked fewer than 30 days ahead. A request made at 14:00 to cancel tomorrow's 10:00 visit in order to rebook is 20 hours out. s7 says late (20 < 24 hours). P1 says timely, because notice days given = 1 ≥ required ⌈24/24⌉ = 1. Two conclusions in the same situation.
  - Evidence 2: base `appointment_reschedule`, "…while the notice for a timely cancellation still holds (at least cancel_notice_hours of full elapsed hours before the current start)".
  - Consequence 2: take task 0's own dermatology visit on 2026-09-23 10:20. There are 144 full hours to 2026-09-29 10:40, which is ≥ 48, so the parenthetical allows a reschedule. P1 classifies a cancellation at that moment as late (5 < 6; see task 0), so "the notice for a timely cancellation" no longer holds, and the move is barred.
  - Bears on: neither task's scored solution. Task 0's patient does not rebook or reschedule ("you do not want to book another dermatology visit for now"), and task 1 involves no cancellation. Each task file records this.
- **F2: SOURCE-POLICY RED, charter-global. Fee-history window anchor drift in P2 and P3 (rule/compute).**
  - Evidence: the P2 rule says "fees posted with a date of service less than 12 whole months before the cancellation date". P2's compute is `XCOUNT(…, within_months=K('lookback_months'), date_field='service_date', …)`, which `check_compute.build_env._within` anchors on `NOW` (`MONTHS(service_date, NOW) < 12`). P3 has the identical rule wording and compute.
  - Consequence: suppose a visit is cancelled on 2026-09-10 and its fee decided on 2026-09-20, and the ledger holds one late-cancel charge with service date 2025-09-15. By the rule: MONTHS(2025-09-15, 2026-09-10) = 11 < 12, so the fee counts and the multiplier is ×1.25. By the compute: MONTHS(2025-09-15, 2026-09-20) = 12, so it does not count and the multiplier is ×1.0. Two numbers.
  - Bears on: neither task. In task 0, P1, P2 and P3 are all handled on 2026-09-23, the cancellation date, so rule and compute coincide. Task 1 does not use P2 or P3.
- **F3: SOURCE-FACTOR RED. Mislabelled `method` factors; the method floor is unmet in P2, P3, P4, P5, P6 and P7.**
  - Evidence: `fee_history_multiplier` (P2), `refund_fee_history_multiplier` (P3), `deposit_fee_history_multiplier` (P4), `no_show_fee_history_multiplier` (P5), `refund_no_show_history_multiplier` (P6) and `moved_deposit_history_multiplier` (P7) are each declared `effect: method`, and each ladder is {×1.5, ×1.25, ×1.0} or {×2.0, ×1.5, ×1.0}. The compute is one formula into which the tier substitutes a rate, for example `notice_fee_start * fee_history_multiplier`. The skill names this case: "a factor labelled method whose tiers only substitute a different number into the same formula (a rate, a fee, a threshold)".
  - Consequence: re-labelled as parameter factors, these leave each of the six computations with 0 method factors, below the floor of 1.
  - Bears on: task 0 (P2, P3, P4) and task 1 (P5, P6, P7). Each task file demonstrates this against its own computations.
  - Note: P1's preparation-day anchor can also be written as `calendar − k`, k ∈ {prep days, 1, 0}. It is accepted as a method because its tiers change the day the notice is counted to, a counting convention the rule states in those words. That judgement is recorded as a borderline observation, not a pass by default.
- **F4: SOURCE-FACTOR RED. Tiers no physician group applies to a missed-visit or late-cancellation fee.**
  - Named tiers:
    - (a) "Where the financial account carries an unpaid balance above zero and shows at least 1 such fee, 10.00 dollars are added…" (P2; P3 identical; P5 and P6 with 20.00 / 10.00);
    - (b) "Where the booking deposits collected on the visit total 150.00 dollars or more, 10.00 dollars are taken off the fee…" (P2 and P3; P5 and P6 at 200.00 → −20.00 / −10.00);
    - (c) "Where the patient's payment plan is active, 15.00 dollars are taken off the no-show fee…; where … delinquent or defaulted, 15.00 dollars are added" (P5, P6).
  - Why each is unreal: a missed-appointment or late-cancellation fee in this line of business is a per-visit-type charge for the lost slot. Practices escalate it for repeat misses and relate it to how late the notice was. They do not surcharge it for an unrelated unpaid balance, do not discount it for patients who paid a larger booking deposit (the deposit exists to be forfeited toward that fee), and do not move it up or down with the status of a payment plan on other charges.
  - Consequence: the struck tiers remove the only multi-source factors of both tasks (the task-level multi-source floor fails), and they deepen the factor-count shortfall of P2, P3, P5 and P6.
  - Bears on: task 0 (P2, P3) and task 1 (P5, P6).
- **Observations (charter-global, no demonstrable consequence on either task):**
  - O-SC: self-cancelling roots (above).
  - The second wording in action form of the P3←P2 and P6←P5 dependencies in P3's and P6's first sentences.
  - State-gate `gate` metadata points at DB fields.
  - Condition and sentence strength mismatches on four edges.
  - The P6 gate can be unsatisfiable (P7 = 0, or a moved insured visit with no deposit).
  - P4 can yield a negative deposit on zero-deposit visit types.
  - P2 and P5 supersede the base emergency-documentation window more broadly than their scope requires.
  - P4 and P7 collect deposits from a patient who is on the Medicaid tier at payment time, for visits booked while self-pay. The charter permits this by booking-date tier, but it is at odds with how Medicaid-participating practices treat covered services.
  - "Afterwards" in the docstrings.
  - CFIELD reads the first payment plan only (P5, P6) where a patient could hold several.

## closing_checklist

Written after both reveals (2026-09-25T04:35Z onward). It sits below the pre-reveal charter-global section and adds nothing to it.

**The difficulty does NOT close.** The four relationships do not all PASS:

| Task | Policy self-consistency | Problem tree | Factors | Unique solution |
| --- | --- | --- | --- | --- |
| 0 | per-task PASS; charter-global SOURCE-POLICY RED (F1, F2) with no consequence on task 0 | PASS | **SOURCE-FACTOR RED** (F3: P2, P3, P4 have no honest method factor; F4: P2 and P3 below 4 factors, no multi-source factor) | PASS (every step equals GT) |
| 1 | per-task PASS; charter-global SOURCE-POLICY RED (F1, F2) with no consequence on task 1 | PASS | **SOURCE-FACTOR RED** (F3: P5, P6, P7 have no honest method factor; F4: P5 and P6 below 4 factors, no multi-source factor) | PASS (every step equals GT) |

Checklist status:
- Audit files: `0.md` and `1.md` correspond one-to-one with `tasks/0.json` and `tasks/1.json`, with this file alongside. This is revision 1, so there are no older revisions.
- Coverage and scopes: the seven extended policies are fully covered, and the scopes {P1, P2, P3, P4} and {P5, P6, P7} are pairwise disjoint (confirmed against `charter_scope`). The task tools and GT are closed, and the seven uuid8 tails are distinct.
- Problem trees:
  - Task 0: 3 prerequisites, 2 value_input edges, P4 as the user write, acyclic.
  - Task 1: 2 prerequisites, 1 value_input edge, P7 as the user write, acyclic.
  - The difficulty-wide graph is a DAG.
- Factors: not met (F3, F4). Every factor is proved to bear weight under the substitution test, and every baseline is honest and differs from gold. But six of the seven computations lack an honest method factor, four fall below four surviving factors, and neither task keeps a multi-source factor after F4.
- Gate re-run on the final form: not performed, because the difficulty does not close. The coordinator's round-1 snapshot (all green) is cited in `charter_global_frozen`.

## revision_2

### charter_global_frozen (revision 2)

- Freeze: this section was written before either revised task JSON was opened; the file mtime is the freeze time. Auditor: the same erl-task-policy-audit run (Claude Opus 5.5 subagent). The revision_1 text above is untouched.
- Why this is a full re-derivation: `appointment.extended.yaml` sha256 is now `e123f1186ef34aa40bbb6de898b6b159f1165e6b8b9d5913120f0dada2e7f170`, changed from r1's `cc8c3713…`. `task_tools.py` is unchanged at `dab3bbca…b46a`. The blueprint files (`appointment.yaml` `62bf7a8a…`, `share_tools.py` `a0a0f97c…`, `db_schema.json` `8c0093f9…`) are unchanged. Because the charter changed, every charter-global section is re-derived below and none is carried forward. The tool-contract conclusions of `### action_binding_and_uuids` are re-confirmed against the unchanged module.
- Fields read: the new charter; `task_tools.py`; the blueprint; the r2 masked views (`r2/0.view.json` `fedc2d31…`, `r2/1.view.json` `e9c4b44d…`); and, for a diff, the r1 views.
- Masked: `tasks/*.json` (r2), the worklog, and other audits.
- Entry conditions: the coordinator's r2 gate snapshot has all seven gates green (traceability deferred), and the masked views and hashes were supplied. Complete.
- The base copy is still verbatim: YAML equality holds for all 10 base keys, and the only extra key is `extended_policies`. Ids, target tools, `computes` and owners are the same seven as in r1 (P1…P7).

### policy_conflict_scan (revision 2)

- Subject overlaps (P2/P5 → `appointment_fee_waived`; P3/P6 → `appointment_deposit_released`; P4/P7 → `appointment_deposit_collected`) partition exactly as in r1. The scoping sentences and tool docstrings are unchanged.
- Time anchors now:
  - P1: handling date (= cancellation date).
  - P2: notice and move tiers anchor on `cancelled_at`; fee history on "the day the fee is decided" (NOW).
  - P3: `cancelled_at`, and fee history on "the refund date" (NOW).
  - P4: payment date.
  - P5: "the day the fee is decided"; held days and confirmation anchor on the visit's dates; hardship anchors on the scheduled date.
  - P6: the refund date.
  - P7: the payment date.
- Every rule anchor now equals its compute anchor; see rule_compute_equivalence.
- Cross-category reads:
  - billing (ledger counts, `patient_balance`, `opened_date`, `hardship_approved_pct`, `hardship_approved_through`), all declared in `cross_category`;
  - payplan `status` and `remaining_balance` (P4, P7), declared.
  - P5 and P6 no longer read payplan.
- Scopes derived blind: task 0 = {P1, P2, P3, P4}, task 1 = {P5, P6, P7}, disjoint and jointly complete. The graph shape is unchanged. Each task file confirms this after the reveal.
- New conflicts found: none. F1 and F2 status: see `### r1_findings_status`.

### rule_compute_equivalence (revision 2)

A scripted check shows every `compute_basis` quotation is a verbatim sentence of its rule, every `baseline.rule` sentence is in the rule, and every basis key names a compute binding. The only compute bindings without their own basis key are the parameter reads `prep_days` (P1), `lf_prep_days` (P2) and `rf_prep_days` (P3), which are quoted under the anchor bindings. This is an observation, carried from r1.

Sentence by sentence:

- **P1**:
  - The r1 tiers are unchanged.
  - New: confirmation rise, `DAYS(confirmed_date, NOW)`: ≤7 gives +2, >7 gives +1, never gives 0. The rule says "confirmation was given 7 days or fewer before the cancellation date" ✓.
  - The rises are summed ✓.
  - New sentences on rebooking and moving carry no computation.
- **P2**:
  - The starting amount has four tiers: counted notice ≥8 gives late fee − 15; 5–7 gives late fee − 10; calendar ≤1 gives the no-show fee; otherwise the late fee ✓.
  - The counted notice is calendar days from `cancelled_at`, reduced by the prep anchor ✓.
  - Escalation: when `ns+lc ≥ 2 ∧ ns ≥ 1` the rate is ×1.5; when `lc ≥ 1 ∨ ns ≥ 1` it is ×1.25; otherwise ×1. The window is `XCOUNT(within_months 12)` on NOW, matching the rule's "before the day the fee is decided" ✓. **The r1 drift is gone.**
  - The move addition anchors on `cancelled_at` ✓.
  - Order: raise, add, round at the end ✓.
- **P3**: mirrors P2 for "the fee the refund offsets", with the window "before the refund date" = NOW ✓. The deposit-held, waiver and result sentences are unchanged ✓.
- **P4**:
  - Rate ×2 / ×1.5 / ×1 ✓; lead ✓.
  - **New balance selection**: an active plan gives balance − plan `remaining_balance`; otherwise a hardship pct > 0 gives balance × (100 − pct)/100 rounded; otherwise the whole balance ✓.
  - Balance amount: >100 gives +50, >0 gives +25, ≤0 gives 0 ✓. Age credit ✓.
  - "none is owed where the visit type's self-pay booking deposit is 0.00 or where the figure worked out is zero or less" is implemented as `0 if P(...) <= 0 else RND(MX(0, …))` ✓.
- **P5**:
  - Escalation as in P2 ✓.
  - Held days are counted from the latest move if moved, else from confirmation if confirmed, else from booking ✓. Held addition: ≥90 gives +25, 60–89 gives +15 ✓.
  - Confirmation addition ✓. Courtesy credit on account age at NOW ✓.
  - Hardship: an approval with pct > 0 and `hardship_approved_through ≥ scheduled_date` gives the full pct; one that ended ≤90 days before the scheduled date gives pct/2; otherwise 0 ✓.
  - Order: raise, add, credit, apply hardship, round at the end ✓.
- **P6**: mirrors P5, with the refund date = NOW ✓.
- **P7**: rate ✓, move lead ✓, balance selection and amount as in P4 ✓. The account-age credit was removed from both rule and compute ✓. Required is rounded before `MX(0, required − held)` ✓.

Observation O-R2-a (no task consequence): in P4 and P7, the rule's hardship tier is "carries a financial-hardship approval above zero", and compute reads `hardship_approved_pct > 0` without checking `hardship_approved_through`. An expired approval with a stored pct would count under one reading and not under another. Neither world reaches that tier: in task 0 the pct is 0; in task 1 the plan is active, so tier 1 applies.

### action_binding_and_uuids (revision 2)

`task_tools.py` is unchanged (`dab3bbca…`), and the seven `(target_tool, computes)` pairs are unchanged and uniquely claimed. So the r1 conclusions are re-confirmed with no change:
- the uuid8s are distinct and not batch-derived;
- no docstring names another tool;
- the "Afterwards" wording remains an observation;
- no tool body validates a prerequisite.

### prerequisite_graph (revision 2)

- The six edges are the same (P1→P2, P2→P3, P4→P3, P5→P6, P7→P6), all state form, with no `fallback_reason` and no cycle.
- Each `policy_source` is verbatim in its blocked rule (scripted check: True ×6).
- value_input gates are compute bindings: P2 `lf_is_late` (renamed from `cancel_is_late`), P3 `fee_recorded_as_waived`, P6 `no_show_fee_recorded_as_waived` ✓.
- `resolved_by` values equal the depended-on target tools ✓.
- No authoring-viewpoint wording ✓.
- These r1 observations stand unchanged (the reworker left them with reasons; they are re-verified here as still no-consequence):
  - the state-gate `gate` values (`appointment_events.event_type`, `appointment_events.event_date`) are DB fields, not eligibility gates;
  - condition vs sentence strength on P2←P1 ("cancellation timestamp"), P3←P2 and P6←P5 ("decision" vs "waiver entry"), and P6←P7 ("deposit entry" vs `appointment_deposit_collected`).

### prerequisite_sentences (revision 2)

- The five prerequisite sentences are verbatim the r1 sentences, so the four-point test, the single resolving write per edge, and the derivations of r1 `### prerequisite_sentences` apply unchanged. They are re-checked against the new rules, not merely carried.
- **The r1 observation on the P3/P6 action-form restatement is closed.** P3's first sentence is now "A booking deposit held on a visit whose cancellation is recorded with timing late is refunded to the patient as one refund entry.", and P6's is "…is refunded to the patient as one refund entry." The "once … is decided" clause is gone from both. A scripted scan finds no other ordering sentence in any rule beyond the declared prerequisite sentences. The "at the moment it is decided" wording in P2 and P5 refers to their own write, not to another problem.
- P1's new sentences ("A request to cancel a visit in order to rebook it is recorded as a cancellation … followed by a new booking" and "A patient may move an open visit … only while a cancellation … recorded on the same day would be timely") state an order between a cancellation and a new booking, and a gate on reschedules. Neither names a problem of this difficulty's graph: no extended policy here books or reschedules. So they ground no undeclared edge.
- The P6 gate can still be unsatisfiable (a moved open visit with no deposit, or P7 = 0 where the gate still wants an entry). This r1 observation stands; neither world is affected.

### override_declarations (revision 2)

The sweep was repeated sentence by sentence over every `base_policy_refs` entry.

- **P1**, refs `appointment_cancellation_timing`, `appointment_reminders_and_release` and **`appointment_reschedule` (new)**:
  - s2 (hours-based timely): declared.
  - **s7 ("A request to cancel less than cancel_notice_hours before the start in order to rebook is a late cancellation …")**: now declared, replaced by "…recorded as a cancellation of this visit with the timing class this rule gives, followed by a new booking, never as a reschedule."
  - **reschedule s1 ("…while the notice for a timely cancellation still holds (at least cancel_notice_hours of full elapsed hours before the current start)…")**: now declared, replaced by "…only while a cancellation of the visit recorded on the same day would be timely under this rule…".
  - The remaining reschedule sentences are followed: limit, counting, eligibility of the new slot, clinician change, telehealth conversion with timing timely.
  - Every sentence of s1, s3–s6 and reminders is followed, as in r1.
  - Merged semantics: in the r1 Nurse example (20 h, rebook), both the replaced s7 and P1 now give **timely**. In the reschedule example on task 0's r1 world, both give "not movable". Unique.
  - Newly noticed (pre-existing in r1, missed then; observation O-R2-b): base `parameter_schema.cancel_notice_hours` still reads "Minimum full elapsed hours between the cancellation and the scheduled start for the cancellation to be timely". This is a parameter description, not a policy sentence, so `overwrite` cannot target it. Its wording is a *minimum*, a necessary condition that P1's larger requirement still satisfies (for example 8 days ≫ 48 h). It does not assert that meeting it makes a cancellation timely, so it reaches no conclusion contrary to P1. No consequence.
- **P2**: fee_waiver's documentation window and "at most once": declared, unchanged. cancellation_timing s5: declared. The Medicaid and first-offense sentences are followed. The fee amount's divergence from base `amount: late_cancel_fee_usd` is carried by the declared s5.
- **P3**: the forfeiture clause is declared. "gains insurance … keeps the deposit" is followed.
- **P4**: s1 is declared. The replacement text still omits "(none where it is 0.00)", but the P4 rule now states "none is owed where the visit type's self-pay booking deposit is 0.00 or where the figure worked out is zero or less", which agrees with base. **The r1 negative-deposit observation is closed**: result = 0 when the type's deposit ≤ 0, and otherwise floored at 0.
- **P5**: documentation window, at-most-once, and "The no-show fee is the visit type's no_show_fee_usd": declared.
- **P6**: forfeiture clause declared.
- **P7**: "One deposit…" and "A reschedule carries the deposit…": declared. The reschedule sentences in P7's refs are followed.

No undeclared override remains. The r1 observation that P2 and P5 supersede the base emergency-documentation window more broadly than their scope needs is unchanged and still has no consequence.

### factor_ladders (revision 2)

| Policy | Factor | Label | Tiers (fall-through last) | Honest? | Multi-source | cross_difficulty |
| --- | --- | --- | --- | --- | --- | --- |
| P1 | preparation_day_anchor | method | ≥3: to prep day / 1–2: to day before / none | accepted (as r1, borderline: endpoint of the count) | no | — |
| P1 | fee_history_notice_rise | parameter | ≥2: +2 / =1: +1 / 0 | yes | no | billing |
| P1 | patient_move_notice_rise | parameter | ≤30d: +2 / >30d: +1 / 0 | yes | no | — |
| P1 | booking_lead_notice_rise | parameter | ≥60: +2 / 30–59: +1 / 0 | yes | no | — |
| P1 | confirmation_notice_rise (new) | parameter | confirmed ≤7d before: +2 / >7d: +1 / never: 0 | yes | no | — |
| P2 | lf_notice_starting_amount | parameter | ≥8: late−15 / 5–7: late−10 / ≤1 cal: no-show fee / late fee | yes | no | — |
| P2 | lf_notice_preparation_anchor (new) | method | same three anchors as P1 | accepted (same shape as P1) | no | — |
| P2 | lf_attendance_escalation (was fee_history_multiplier) | **parameter** (re-labelled) | ≥2 ∧ ≥1 no-show: ×1.5 / (≥1 late-cancel ∨ ≥1 no-show): ×1.25 / ×1 | yes | yes, over no-show charge rows and late-cancel charge rows (see note) | billing |
| P2 | lf_patient_move_addition | parameter | ≤30d: +10 / >30d: +5 / 0 | yes | no | — |
| P3 | 4 factors mirroring P2 (rf_*) | same | same | yes | rf_attendance_escalation yes | billing |
| P4 | dep_fee_history_rate | **parameter** (re-labelled) | ×2 / ×1.5 / ×1 | yes | no | billing |
| P4 | booking_lead_amount | parameter | ≥45: −25 / <14: +50 / 0 | yes | no | — |
| P4 | dep_balance_selection (new) | method | active plan: balance − plan remaining / no active plan ∧ hardship > 0: balance × (1 − pct) / whole balance | **yes: selects how the counted balance is computed** | tier 1 single-source, so no | payplan (+ billing) |
| P4 | dep_unpaid_balance_amount | parameter | >100: +50 / >0: +25 / 0 | yes | no | billing |
| P4 | account_age_credit | parameter | ≥1826: −25 / 730–1825: −10 / 0 | yes | no | billing |
| P5 | nf_attendance_escalation | parameter | as P2 | yes | yes (as P2) | billing |
| P5 | nf_held_slot_addition | parameter | ≥90: +25 / 60–89: +15 / 0 | yes | no | — |
| P5 | nf_held_slot_anchor (new) | method | moved: from latest move / confirmed, not moved: from confirmation / from booking | **yes: selects the start date of the count from a different record** | no | — |
| P5 | nf_confirmed_addition | parameter | ≤2d: +25 / >2d: +15 / 0 | yes | no | — |
| P5 | nf_courtesy_credit (new) | parameter | ≥1826d: −15 / 730–1825: −10 / 0 | yes | no | billing |
| P5 | nf_hardship_reduction (new) | parameter | covers scheduled date: pct / ended ≤90d before: pct/2 / 0 | yes | two fields of one account row: not distinct records | billing |
| P6 | 6 factors mirroring P5 (rn_*) | same | same | yes | rn_attendance_escalation yes | billing |
| P7 | mv_fee_history_rate | **parameter** (re-labelled) | ×2 / ×1.5 / ×1 | yes | no | billing |
| P7 | moved_deposit_move_lead | parameter | <14: +50 / 14–44: +25 / 0 | yes | no | — |
| P7 | mv_balance_selection (new) | method | as P4 | yes | no | payplan (+ billing) |
| P7 | mv_unpaid_balance_amount | parameter | as P4 | yes | no | billing |

Structural checks:
- Bindings are disjoint within each policy; every `decides` is an input; every ladder has ≥3 tiers, disjoint as stated. P2 and P3's four-tier notice ladder is disjoint because notice ≥5 implies calendar ≥5, which excludes calendar ≤1.
- No two tiers of a ladder share an outcome at the charter's values.
- Every tier is in the rule and in compute; every fall-through is the factor's baseline and every `baseline` is what `baseline.rule` states.

Counts:

| Policy | Factors | Parameter | Method | Bounds |
| --- | --- | --- | --- | --- |
| P1 | 5 | 4 | 1 | ✓ |
| P2 | 4 | 3 | 1 | ✓ |
| P3 | 4 | 3 | 1 | ✓ |
| P4 | 5 | 4 | 1 | ✓ |
| P5 | 6 | 5 | 1 | ✓ |
| P6 | 6 | 5 | 1 | ✓ |
| P7 | 4 | 3 | 1 | ✓ |

Every computation meets the bounds.

Realism:
- **The three r1 F4 tiers are gone.** No unpaid-balance surcharge on any fee (P2, P3, P5, P6); no deposit-size credit on any fee; no payment-plan adjustment of the no-show fee (P5, P6 no longer read payplan).
- The new tiers are ones this line of business does weigh:
  - escalating the fee when a no-show is in the 12-month history;
  - a notice-graded late-cancellation fee;
  - a courtesy reduction for long-standing patients;
  - a hardship-program percentage reduction on a patient charge;
  - for deposits, discounting balances already under an active plan or hardship approval.
- The r1 observations on the held-slot and confirmation surcharges stand as observations. New observations:
  - The confirmation-rise on cancellation notice (P1) is unusual but not demonstrably unreal: after confirmation the practice stops back-filling the slot.
  - Counting held days "from the confirmation date" for a confirmed, never-moved visit (P5, P6 anchor tier 2) is an unusual measure of how long a slot was held, but it is stated plainly and not a treatment given to customers by itself.

Note on multi-source (observation O-R2-c): the escalation ladder's tier 2, "at least 1 such charge (late-cancellation or no-show)", is a disjunction over two kinds of ledger row that is equivalent to a single combined count ≥1. Its tier 1 is a genuine conjunction ("2 or more … and at least one of them a no-show fee"). Each part is one this business weighs, and the rows are distinct records (no-show charge rows vs late-cancel charge rows), so it is accepted as the tasks' multi-source factor. It is the only one in each task: P5's hardship tiers combine two fields of the same account row, and P4 and P7's balance-selection tier 1 is single-source.

### r1_findings_status

| Item | r1 | r2 status | Evidence |
| --- | --- | --- | --- |
| F1 undeclared timeliness overrides | SOURCE-POLICY RED | **closed** | P1 overwrite now names cancellation_timing s7 and reschedule s1 (verbatim in base, replacements verbatim in rule); `appointment_reschedule` added to refs. |
| F2 window anchor drift (P2, P3) | SOURCE-POLICY RED | **closed** | P2 rule "before the day the fee is decided", P3 "before the refund date"; both equal NOW, which is XCOUNT's anchor. |
| F3 mislabelled method factors | SOURCE-FACTOR RED | **closed** | Multipliers re-labelled `parameter` in all six. Genuine methods added: P2/P3 notice anchor (P1-type), P4/P7 balance selection, P5/P6 held-slot anchor. |
| F4 unreal tiers | SOURCE-FACTOR RED | **closed** | The unpaid surcharge, deposit credit and plan adjustment on fees are removed. |
| O action-form restatement (P3/P6) | observation | **closed** | "once … decided" is removed from both rules. |
| O negative deposit (P4) | observation | **closed** | Floor and 0.00-type exemption are in rule and compute. |
| O-SC self-cancelling roots | observation | stands | Structure unchanged. Each task file re-demonstrates it on the r2 world. |
| O Medicaid-deposit realism | observation | stands | P4 and P7 are still tier-agnostic at payment time. |
| O state-gate metadata / condition strength | observation | stands | Unchanged. |
| O P6 gate unsatisfiable, docstrings "Afterwards", CFIELD first plan row, over-broad documentation-window supersession | observation | stand | Unchanged. CFIELD now also feeds P4/P7 `remaining_balance`. |

### findings (revision 2)

No charter-global RED remains. The new observations are O-R2-a (the P4/P7 hardship tier does not check the approval's end date), O-R2-b (the `parameter_schema` minimum-hours wording, compatible with P1) and O-R2-c (the escalation disjunction is equivalent to a combined count). The observations carried over are listed in the table above. Whether each factor bears weight, and T0-O3/T0-O4, are decided in the task files.

### closing_checklist (revision 2)

Written after both r2 reveals (2026-09-25T04:59:42Z onward).

| Task | Policy self-consistency | Problem tree | Factors | Unique solution | Verdict |
| --- | --- | --- | --- | --- | --- |
| 0 | PASS | PASS | PASS | PASS (every step equals GT) | **PASS** |
| 1 | PASS | PASS | PASS | PASS (every step equals GT) | **PASS** |

- Audit files: `0.md` and `1.md` each carry revision 1 (untouched) and `## revision_2`, with a frozen derivation, then a comparison, then findings. This file carries revision 1 untouched plus its `## revision_2`.
- Coverage and scopes: the seven extended policies are covered, with scopes {P1, P2, P3, P4} and {P5, P6, P7}, disjoint (confirmed against `charter_scope`). The task tools are closed, and each uses an independently generated, frozen uuid8 (module unchanged).
- Problem trees:
  - Task 0: 3 prerequisites, 2 value_input edges, user write P4.
  - Task 1: 2 prerequisites, 1 value_input edge, user write P7.
  - Both acyclic, and the difficulty graph is a DAG.
- Factors: every computation has a self-sufficient baseline and 4–6 factors with ≥2 parameter and 1 honest method (P1 4+1, P2 3+1, P3 3+1, P4 4+1, P5 5+1, P6 5+1, P7 3+1). Every ladder has ≥3 distinct tiers stated in its rule. Every factor bears weight on its task's world, and every all-baseline figure differs from gold. Each task has ≥1 multi-source factor (the escalation ladder, O-R2-c) and ≥1 cross-difficulty factor (billing, plus payplan in P4 and P7).
- Gates re-run on the final form by this auditor (repository root, read-only; `replay_tasks.py --check`; the sha256 of both task JSONs and the charter was unchanged before and after):

  ```
  check_extended → EXTENDED OK
  check_task_tools → TASK TOOL CONTRACT OK
  check_solvability → SOLVABILITY OK
  check_compute → COMPUTE OK
  check_grounding → GROUNDING OK
  check_cross_fire → SCOPE OK
  replay_tasks --check → REPLAY OK
  ```

  check_traceability stays deferred to KB publication, per the coordinator.

**The difficulty passes the source-layer audit at revision 2.**

Open observations carried forward (none is a red light):
- O-SC: self-cancelling roots.
- The Medicaid-deposit realism of P4 and P7.
- State-gate metadata and condition-strength mismatches.
- The P6 gate can be unsatisfiable.
- "Afterwards" in the docstrings.
- CFIELD reads the first plan row only.
- P2 and P5 supersede the base documentation window more broadly than their scope needs.
- O-R2-a: the P4/P7 hardship tier does not check the approval's end date.
- O-R2-b: the `parameter_schema` minimum-hours wording, compatible with P1.
- O-R2-c: the escalation disjunction is equivalent to a combined count.
- T1-O4: the "97-day lead" wording in the task 1 seed note.
