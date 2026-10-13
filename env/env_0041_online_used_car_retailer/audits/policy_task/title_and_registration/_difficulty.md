# Policy-task audit — title_and_registration / charter-global

## charter_global_frozen

- Freeze time: 2026-10-06T09:24:35Z (written before any task's GT was revealed; nothing in this section derives from `tasks/*.json` GT fields)
- Auditor: erl-task-policy-audit (independent auditor agent; not the instantiating agent)
- Frozen inputs (sha256, recomputed by the auditor and matching the orchestrator's SHA256SUMS):
  - `tasks/title_and_registration/title.extended.yaml` f63543884d1c010654a0094ad685aeef306906cd2722c1c24e4ebcb3d802343b
  - `tasks/title_and_registration/task_tools.py` 285b634bc521b0ce826f318d768e3b0bb2969a73176f6099cd890e41d5f680f6
  - views `task_0.view.json` 328abf1b…cc, `task_1.view.json` bb25dab2…f6 (match)
- Fields permitted: `blueprint/blueprint.yaml`, `blueprint/products/title.yaml`, `blueprint/share_tools.py`, the extended charter, `task_tools.py`, and the masked views (`frozen_time`, `user_scenario`, `initial_state`).
- Fields masked and unread at freeze: every field of `tasks/0.json` and `tasks/1.json` other than the three in the views (`evaluation_criteria`, `computations`, `charter_scope`, `required_documents`, `design_rationale`, `solvability_contract`, `prerequisite_closure`), `worklog.md`.
- Entry conditions (Step 0): gate snapshot supplied with the brief — EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK (check_traceability deferred until the KB is published). Masked views and hashes supplied. Input complete.
- Base copy check: lines 1–1012 of `title.extended.yaml` are byte-identical to `blueprint/products/title.yaml` (`diff` empty).

### policy_conflict_scan

Six extended policies, six task tools, one `(target_tool, computes)` each:

| policy | target_tool | owner | computes | prerequisite edges | `# claimed by` comment in yaml |
|---|---|---|---|---|---|
| title_ext_shortage_cure_share | pay_title_fee_shortage_f6fcb150 | user | amount | [] | task 0 |
| title_ext_extension_tag_validity | issue_title_extension_tag_53dbe274 | agent | valid_days | ← shortage_cure_share (value_input) | task 0 |
| title_ext_late_penalty_payment | pay_title_late_penalty_3594d5af | user | amount | [] | task 1 |
| title_ext_lien_correction_charges | pay_title_lien_charges_e09cfc3d | user | amount | [] | task 1 |
| title_ext_resubmission_remittance | resubmit_title_packet_8a13d7a9 | agent | remit_amount | ← late_penalty_payment, ← lien_correction_charges (both value_input) | task 1 |
| title_ext_late_penalty_reimbursement | reimburse_title_late_penalty_e7fb1913 | agent | amount | ← late_penalty_payment, ← resubmission_remittance (both value_input) | task 1 |

Scope: the two trees {extension_tag ← shortage_cure_share} and {reimbursement ← penalty_payment, resubmission ← penalty_payment + lien_charges} share no policy; together they cover all six extended policies. Mutually exclusive and jointly complete.

Overlapping subjects: all three user payment policies have subject `title_state_fee_collected` and all three book `event_type=title_state_fee_collected` rows (fee_type `registration_fee`, `not_applicable`, `lien_recording_fee`). Their triggers are disjoint by the return they follow: a fee-shortage return that states an amount (shortage_cure_share; late_penalty_payment says "A shortage the state states as an amount is not a late-registration penalty under this rule"), a fee-shortage return of 0.00 (late_penalty_payment), a lien information error return dated on or after the most recent submission (lien_correction_charges). Note shortage_cure_share does not itself exclude a 0.00 return; on such a return its formula yields 0.00, so no positive payment arises and the overlap is inert (see finding G-O2).

Cross-policy conflict found: shortage_cure_share promises a Kestrel-funded remainder "when the packet goes back"; resubmission_remittance, the only policy that sends a packet back, enumerates its remittance without it (finding G-R1).

Eligibility, time anchors and terminal states: every task tool's write is admissible under the base state gates it touches (collection on `rejected`; tag on `rejected`; resubmission rejected→submitted; reimbursement on `submitted`). The resubmission tool moves `rejected` directly to `submitted` without the base `ready_to_submit` stop (base lifecycle `rejected -> ready_to_submit -> submitted`); no scored quantity depends on it (observation G-O7).

Cross-category read boundaries: reads are from `purchase` (purchase_orders.handover_date, variant_name; purchase_transactions.payment_source/txn_date) and `delivery` (delivery_orders.last_miss_cause, original_scheduled_date), each declared in `cross_category`. No policy reads a field it does not declare.

### rule_compute_equivalence

Check 2, policy by policy. Every compute binding carries a `compute_basis` quotation; the sweep below lists only where the quotation and the expression need comment.

- **title_ext_shortage_cure_share** — `stated_shortage` (LATEST fee_shortage amount), `latest_doc_date`, `latest_remit_date` ("the date of the order's most recent remittance to the state"), both clocks, both late-day counts (`MX(0, …)` = "never below zero"), `cure_share`, `program_relief`, `returns_relief`, `result` (`RND(…,2)` at end = "rounded half up to the cent only at the end"). Three-tier `buyer_clock_start` and `kestrel_clock_start` expressions match the rule sentence by sentence (`kestrel_clock_start` tier 2 "no outside lender's proceeds were posted after that document" = `lender_postings == 0 or lender_posting_date <= latest_doc_date`). Empty promise: the rule sentence "and Kestrel funds the rest of the stated shortage itself when the packet goes back" has no implementation in this policy nor in any other (finding G-R1). Wording: the fall-through "otherwise the cure share is the whole stated shortage" calls a share an amount; compute uses `1` (observation G-O5).
- **title_ext_extension_tag_validity** — base validity, turnaround, cure, lien, handover allowances, stretch, carry-over, cap: each in rule and compute. `extension_stretch` is applied inside `int(…)` in every tier; the rule says "the stretched sum is then rounded down" — equivalent because tier 3 multiplies an integer by 1. `latest_return_code` is `LATEST(... reject_code)` by `txn_date`; the rule's "the order's most recent return" leaves same-date ties undefined (no tie on any task world that scores this policy; observation G-O8). `extension_limit` uses `K('state_max_extensions_'+state)` whose values (AZ1 TX1 GA2 FL1 NC1 OH1 PA1 CO2) equal base `title_temp_tags.params.state_temp_tag_rules[*].max_extensions`.
- **title_ext_late_penalty_payment** — penalty base (title + registration fee collected), filing date three tiers, days late (`K('dealer_deadline_days_'+state)` equal to base `title_submission.params.state_dealer_deadline_days`), rate band, lien notation, return notice, rounding at end: all matched. The window "Within the service's fee shortage collection days after such a return" is an eligibility sentence, not a compute input.
- **title_ext_lien_correction_charges** — `K('lien_fee_'+state)` equals the base schedule's `lien_recording_fee` for all eight states; lien wait start three tiers, surcharge, e-file, re-notation, rounding: matched. `baseline.params` lists only `[lien_fee_NC, lien_fee_PA, lien_fee_OH, lien_fee_FL]`, omitting the four 0.00 states (observation G-O9).
- **title_ext_resubmission_remittance** — held fees, tag lapse (uses `tags_on_order - 1` as "extension tags used"), expedite, channel (`P('county_submission_by_mail')`), courier, re-review, rounding: matched. The rule enumerates "The held fees and the four resubmission charges"; nothing for a Kestrel-funded shortage remainder (G-R1).
- **title_ext_late_penalty_reimbursement** — reimbursable penalty `MN(penalty_paid, remitted_since)`, first submission date (remitted `title_fee` row), Kestrel end date three tiers, total/lender/Kestrel penalty days, share three tiers, three additions, `MN(1, …)` cap, rounding at end: matched. The base eligibility conditions repeated in the rule (service switch, first submission missed the dealer deadline, documents within due days) are eligibility, not compute inputs.

Every `factors[].ladder` tier is a rule sentence and a branch of its `decides` binding, and vice versa. No rule/compute asymmetry other than G-R1's unimplemented promise.

### action_binding_and_uuids

- Each `(target_tool, computes)` is claimed by exactly one policy (table above).
- uuid8 tails: f6fcb150, 53dbe274, 3594d5af, e09cfc3d, 8a13d7a9, e7fb1913 — pairwise distinct, no shared prefix, no sequence pattern. PASS.
- Docstrings: none names another tool, a policy id, or a sequence position; "before the call" occurs only for the lookup that sources an id. None validates a prerequisite: every function body reads the order, books one row and updates fields unconditionally (no `if` on status, ledger contents or prior writes). PASS.

### prerequisite_graph

Check 7. `prerequisite` filled on all six (`[]` on three). Edges: E1 extension←shortage, E2 resubmission←penalty, E3 resubmission←lien, E4 reimbursement←penalty, E5 reimbursement←resubmission. Every `problem` is an extended policy id of this file, none self, none base. Acyclic (topological: shortage → extension; penalty, lien → resubmission → reimbursement; penalty → reimbursement). Every `policy_source` is verbatim in the blocked policy's own `rule` (checked string-by-string). All `form: state`, no `fallback_reason` — consistent. `resolved_by` equals the depended-on policy's `target_tool` in all five. `kind: value_input` and `gate` names a real compute binding in all five (`extension_cure_days`, `held_fees` ×2, `penalty_paid`, `remitted_since`). No authoring-viewpoint phrasing.

`condition` vs sentence:
- E1 is weaker than its sentence: the sentence waits on "the buyer's cure share of the shortage … stands collected … as its own fee entry"; the condition (and the cure-allowance rule sentence "a fee has been collected on the order on or after that return's date") accept any `title_state_fee_collected` row on/after the return — which the late-penalty and lien-charge writes also book. Observation G-O4 (not demonstrable on either world: neither world lets a second collection write precede the cure share).
- E5 adds "and the order is submitted again" to the sentence's remittance; the only write of this difficulty that books a remittance (`resubmit_title_packet_8a13d7a9`) also submits, so the two are co-extensive here. No consequence.

### prerequisite_sentences

Check 6, per edge — four-point test (ordering connective / record-visible state / no tool, id or snake_case / strength equal to condition):

- E1 "An extension tag's validity is fixed only after the buyer's cure share of the shortage stated on the order's most recent fee-shortage return stands collected on the order as its own fee entry." — "only after"; state (a collected fee entry); no tool/id; strength: see G-O4. Writes of this difficulty that bring the stated state about: only `pay_title_fee_shortage_f6fcb150` (the only write that books the buyer's share of a stated shortage). Derivation: the sentence names "the buyer's cure share of the shortage stated on the … fee-shortage return" → the only rule defining that quantity is title_ext_shortage_cure_share ("the buyer's cure share of the stated shortage is collected from the buyer as its own entry") → its target tool. One reading.
- E2 "A returned packet does not go back to the state until the late-registration penalty named on a fee-shortage return that states no amount stands collected on the order as its own fee entry." — "until"; state; clean; writer: only `pay_title_late_penalty_3594d5af`; derivation via late_penalty_payment's "the buyer pays the late-registration penalty … booked as its own entry". One reading.
- E3 "A packet returned for a lien information error goes back to the state only after the lien charges for the corrected lien stand collected on the order as a lien recording fee entry." — "only after"; state; clean; writer: only `pay_title_lien_charges_e09cfc3d` (fee_type lien_recording_fee). One reading.
- E4 "The late-penalty reimbursement is not fixed until the late-registration penalty named on the order's most recent fee-shortage return stands collected on the order as its own fee entry." — "not … until"; state; clean; writer as E2. One reading.
- E5 "The late-penalty reimbursement is booked only after the order's ledger shows a remittance to the state dated on or after its most recent fee-shortage return." — "only after"; state; clean; writer: only `resubmit_title_packet_8a13d7a9` books `title_state_fee_remitted`. One reading.

No depended-on rule restates a sentence; no rule carries a second wording, tool name or other policy id. Undeclared cross-problem order: shortage_cure_share's "Kestrel funds the rest of the stated shortage itself when the packet goes back" places the resubmission after the buyer's cure share, and base title_rejections' "fee_shortage by collecting the stated shortage, so the order returns to ready_to_submit once cured. … A cured order is resubmitted" orders the cure before resubmission; resubmission_remittance carries no prerequisite sentence on the stated-amount cure share. No task's tree rests on this order (task 0 has no resubmission; task 1's shortage states 0.00), so per the skill it is recorded inside G-R1 / as observation, not as a tree defect.

### override_declarations

Sentence-by-sentence over `base_policy_refs`:

- **shortage_cure_share** (refs: service_fees, agg_household_fees, rejections, documents, submission). Declared: title_service_fees "after a fee-shortage rejection the stated shortage is collected as its own entry within the fee shortage collection days." Followed unchanged: collection only on awaiting_documents/rejected; household no-combination; documents rules; submission rules. Handled differently but undeclared: title_rejections "lien_information_error is cured by Kestrel from the finance records and fee_shortage by collecting the stated shortage, so the order returns to ready_to_submit once cured." — the same quantity the declared clause governs (G-O1).
- **extension_tag_validity** (refs: temp_tags, rejections, submission). Declared: title_temp_tags validity sentence. Followed: tag state gate, on-or-before-expiry, lead days, documents-complete gate, extension limit, sequence. Nothing else differs.
- **late_penalty_payment** (refs: service_fees, agg_household_fees, submission, rejections, reimbursements). Declared: the same title_service_fees shortage clause (a second, different replacement of one clause — G-O2). title_rejections' "fee_shortage by collecting the stated shortage" with a stated 0.00 is not named (G-O1). title_reimbursements followed.
- **lien_correction_charges** (refs: service_fees, agg_household_fees, rejections, completion). Declared: title_service_fees "plus the lien recording fee when a lienholder is to be recorded." — an opening-time clause, replaced by a sentence about a different trigger (a lien-error return) (G-O3). title_rejections "lien_information_error is cured by Kestrel from the finance records" not named although extended now requires a buyer payment before the packet goes back (G-O1).
- **resubmission_remittance** (refs: submission, rejections, temp_tags). Declared: title_submission "Every held state fee is remitted with the submission as its own remittance entry." Followed: funded-and-insured gate, remit state, max submissions, resubmission target days.
- **late_penalty_reimbursement** (refs: reimbursements, submission, rejections, documents). Declared: title_reimbursements "A state late-registration penalty is reimbursed in full". Followed: three base eligibility conditions (restated in the replacement), once per document, max per order, state gate, documents-late switch. The extended rule's own first sentence reasserts "Kestrel reimburses the buyer's late-registration penalty in full" (its baseline sentence) next to the declared replacement "reimbursed at the reimbursed share set out below" (G-O5).

Anonymous intermediate factor / 0-1 multiplier / dropped branch: none found.

### factor_ladders

Structure only (weight is per task).

| policy | factor | label | honest? | tiers | multi-source (non-fall-through tiers) | cross_difficulty | real-ladder test |
|---|---|---|---|---|---|---|---|
| shortage_cure_share | cure_cost_allocation | method | yes (ratio vs constants) | 3 | yes (title ledger + purchase ledger + delivery) | — | pass |
| | buyer_document_clock | method | yes (anchor selection) | 3 | yes (delivery miss cause + purchase handover / delivery slot vs title opening) | declared `delivery` — delivery is claimed by no difficulty (G-O6) | pass |
| | kestrel_handling_clock | method | yes | 3 | yes (purchase posting vs title doc) | purchase | pass |
| | program_relief | parameter | yes | 3 | no | purchase | pass |
| | returns_relief | parameter | yes | 3 | no | — | pass (fall-through = one return, reachable) |
| extension_tag_validity | extension_turnaround_allowance | parameter | yes | 3 | no | — | pass |
| | extension_cure_allowance | parameter | yes | 3 | yes | — | pass |
| | extension_lien_allowance | parameter | yes | 3 | no (both purchase postings) | purchase | pass |
| | extension_handover_allowance | parameter | yes | 3 | yes (purchase handover vs title opening) | purchase | pass |
| | extension_last_tag_stretch | **method** | **no** — tiers substitute a multiplier 1.25 / 1.1 / 1 into the same `int(sum × stretch)`; compute applies the same rounding in every tier | 3 | yes | — | **mislabel (G-F1)** |
| | extension_carry_over | **method** | **no** — tiers substitute a fraction 1 / ½ / 0 of the same `current_days_left` (floor is a no-op for 1 and 0) | 3 | no | — | **mislabel (G-F1)** |
| late_penalty_payment | penalty_filing_date_rule | method | yes | 3 | yes | — | pass |
| | penalty_rate_band | parameter | yes | 3 | no | — | pass |
| | lien_notation_charge | parameter | yes | 3 | yes (order lienholder + ledger return) | — | pass |
| | return_notice_charge | parameter | yes | 3 | no | — | pass |
| lien_correction_charges | lien_wait_clock | method | yes | 3 | yes | purchase | **fail: "a lien information error return stands" holds of every customer who reaches this write (G-F2)** |
| | late_lien_surcharge | parameter | yes | 3 | no | — | pass |
| | electronic_lien_filing_charge | parameter | yes | 3 | yes | purchase | **fail: "the registration state is among the service's electronic title states" holds of every customer — every service lists all eight footprint states (G-F2)** |
| | lien_renotation_charge | parameter | yes | 3 | no | — | **fail: fall-through (no lien-error return) unreachable for any customer reaching this write; two real tiers (G-F2)** |
| resubmission_remittance | tag_lapse_clock | method | yes | 3 | yes | — | pass |
| | expedited_handling_charge | parameter | yes | 3 | no | — | pass |
| | packet_channel_charge | parameter | yes | 3 | yes | — | **fail: "the state has returned the order at least once" holds of every customer whose returned packet goes back; with the mail switch boolean the fall-through is unreachable (G-F3)** |
| | lender_courier_charge | parameter | yes | 3 | yes | purchase | pass |
| | state_re_review_charge | parameter | yes | 3 | no | — | pass |
| late_penalty_reimbursement | reimbursed_share_allocation | method | yes | 3 | yes | purchase | pass |
| | kestrel_penalty_end_rule | method | yes | 3 | yes | — | pass |
| | long_wait_addition | parameter | yes | 3 | no | — | pass |
| | program_addition | parameter | yes | 3 | no | purchase | pass |
| | prompt_documents_addition | parameter | yes | 3 | no | — | pass |

No two tiers of any ladder share a value or method. Every tier is stated in the `rule`. Every fall-through equals the factor's `baseline` and what `baseline.rule` implies for that input.

Counts after the tests (declared → surviving):
- shortage_cure_share: 5 (3 method, 2 parameter) → 5; multi-source yes; cross-difficulty purchase.
- extension_tag_validity: 6 (2 method, 4 parameter) → honest labels give 6 parameter, **0 method** (G-F1).
- late_penalty_payment: 4 (1 method, 3 parameter) → 4.
- lien_correction_charges: 4 (1 method, 3 parameter) → **1 surviving** (late_lien_surcharge) (G-F2).
- resubmission_remittance: 5 (1 method, 4 parameter) → 4 surviving (channel struck) (G-F3).
- late_penalty_reimbursement: 5 (2 method, 3 parameter) → 5.

### findings

**G-R1 — SOURCE-POLICY RED (charter-global; bears on task 0 and task 1 as the two sides; per-task consequence in their files)**
- Symptom: the shortage-cure policy promises a payment to the state that no policy makes.
- Root cause: title_ext_shortage_cure_share rule and overwrite `replaced_by`: "the buyer's cure share of the stated shortage is collected from the buyer as its own entry, and Kestrel funds the rest of the stated shortage itself when the packet goes back." title_ext_resubmission_remittance rule: "When a returned packet goes back to the state, Kestrel remits every state fee held on the order with it as one remittance entry for the total … Kestrel adds to the same remittance the resubmission charges it funds itself … The held fees and the four resubmission charges are added together and the total is rounded half up to the cent."
- Demonstrated consequence (same situation, two conclusions): an order with a stated-amount fee-shortage return on which the buyer's cure share has been collected and the packet then goes back. Reading A (shortage policy): remittance = held fees + (stated shortage − buyer's share) + charges. Reading B (resubmission policy, the scored formula of its tool): remittance = held fees + four charges. On task 0's world after its cure payment (stated 44.80, buyer share 22.85 per the 0.md derivation) the two readings differ by 21.95. The sentence is also an unimplemented rule promise (check 2) and an undeclared cross-problem order (cure share before resubmission; check 6) that grounds no edge.
- Affected: `title.extended.yaml` title_ext_shortage_cure_share.rule / overwrite[0].replaced_by; title_ext_resubmission_remittance.rule / compute.result.
- Scored-solution impact: none in this bundle (task 0 scores no resubmission; task 1's fee-shortage return states 0.00, so the "rest" is 0.00). Recorded at charter level.

**G-F1 — SOURCE-FACTOR RED (charter-global structure; bears on task 0)**
- Symptom: extension_last_tag_stretch and extension_carry_over are labelled `method` but their tiers substitute numbers into one formula.
- Evidence: stretch compute `K('stretch_last_returned') if … else (K('stretch_last_clean') if … else 1)` feeding `int((…) * extension_stretch)` in every tier; carry compute `current_days_left` / `int(current_days_left / 2)` / `0` — a fraction 1, ½, 0 of one count.
- Consequence: on honest labels the extension computation has 0 `method` factors against the required ≥1.
- Affected: `title.extended.yaml` title_ext_extension_tag_validity.factors[4], factors[5].

**G-F2 — SOURCE-FACTOR RED (charter-global structure; bears on task 1)**
- lien_wait_clock tiers 1–2 conjoin "a lien information error return stands"; the policy applies only "When the state returns a packet for a lien information error … while the state's return for a lien information error is dated on or after the order's most recent submission" — the part holds of every customer reaching the write and restates scope.
- electronic_lien_filing_charge tiers 1–2 conjoin "the registration state is among the service's electronic title states"; every one of the six services sets `electronic_title_states: [AZ, TX, GA, FL, NC, OH, PA, CO]`, which is the whole footprint (blueprint: registration outside the footprint goes to a human) — holds of every customer.
- lien_renotation_charge fall-through "nothing otherwise" (no lien-error return) is unreachable inside the policy's scope; the ladder has two real tiers.
- Consequence: surviving factors for lien_correction_charges = 1 against the 4–6 bound.

**G-F3 — SOURCE-FACTOR RED (charter-global structure; bears on task 1)**
- packet_channel_charge tiers both conjoin "the state has returned the order at least once"; the policy's scope is "When a returned packet goes back to the state" — holds of every customer; `county_submission_by_mail` is boolean, so the fall-through "nothing otherwise" is unreachable. Two real tiers.
- Surviving factors for resubmission_remittance = 4 (bound met), but the ladder test fails for this factor.

**Observations (no demonstrable consequence at charter level; per-task files test them on their worlds)**
- G-O1 Base title_rejections cure sentence ("lien_information_error is cured by Kestrel from the finance records and fee_shortage by collecting the stated shortage") is not named in any overwrite although shortage_cure_share (buyer pays a share), late_penalty_payment (buyer pays a penalty on a 0.00 shortage) and lien_correction_charges (buyer pays lien charges before the packet goes back) each handle the cure differently. The base sentence does not fix who bears the amount, so each extended reading can be reconciled with it; tested per task.
- G-O2 One base clause (title_service_fees shortage clause) is superseded twice with different replacement texts; domains separate only through late_penalty_payment's exclusion sentence; late_penalty's replacement "after such a return" dangles.
- G-O3 lien_correction_charges supersedes the opening lien-fee clause with a sentence about a different trigger; the merged text drops the opening lien fee while `parameter_schema.state_fee_components` ("lien recording added when a lienholder is recorded") and title_agg_household_fees ("lien … fees") still describe it.
- G-O4 E1 condition and the cure-allowance sentence are broader than E1's prerequisite sentence (any collected fee vs the buyer's cure share).
- G-O5 Baseline sentences kept in the rules say "in full" ("collected from the buyer in full"; "Kestrel reimburses … in full") beside factor sentences that reduce the amount; in the reimbursement policy this re-states the very base clause the overwrite declares superseded. "the cure share is the whole stated shortage" mixes share and amount.
- G-O6 buyer_document_clock declares `cross_difficulty: delivery`, but no difficulty claims `delivery` (blueprint difficulties claim purchase, tradein, finance, title, warranty). The task-level cross-difficulty requirement for task 0 is met by purchase-reading factors.
- G-O7 resubmit tool moves rejected→submitted directly, skipping base ready_to_submit; no scored effect.
- G-O8 "most recent return" ties on the same date are undefined for `latest_return_code`; no scored world has a tie on that binding.
- G-O9 lien_correction_charges `baseline.params` omits the 0.00-fee states.

## closing_checklist

Written after both reveals (task 0 at 2026-10-06T09:27:50Z, task 1 at 09:28:25Z). The difficulty does **not** pass the source-layer audit; the list records the status of each item.

- Audit files: `0.md`, `1.md` correspond one-to-one with `tasks/0.json`, `tasks/1.json`; `_difficulty.md` alongside; first revision (no older revisions). Comparison sections: task 0 — independent derivation = GT on every scored value, verdict SOURCE-CHAIN RED + SOURCE-FACTOR RED; task 1 — independent derivation = GT on every scored value, verdict SOURCE-FACTOR RED. Not all PASS.
- Coverage and scope: all six extended policies are claimed; task 0 = {shortage_cure_share, extension_tag_validity}, task 1 = {late_penalty_payment, lien_correction_charges, resubmission_remittance, late_penalty_reimbursement} (`charter_scope` of each task agrees); pairwise disjoint across the whole trees. Task tools closed over GT; six independently generated uuid8s. PASS.
- Trees: task 0 n=1 (1 value_input, 1 user write); task 1 n=3 (4 value_input, 2 user writes); both acyclic; the union graph is acyclic with no cross-task edges. Structure PASS; task 0 fails on the persona hint (T0-C1).
- Factors: each computation declares a definite baseline that differs from gold (44.80≠22.85, 30≠54, 11.37≠62.90, 21.50≠33.50, 96.40≠145.40, 62.90≠62.78) and every factor bears weight on its task's world; failures: G-F1/T0-F1 (extension computation has no honestly labelled method factor), G-F2/G-F3/T1-F1 (four ladders in task 1 that do not divide customers; lien-charge computation keeps 1 of 4 factors).
- Charter: G-R1 SOURCE-POLICY RED (shortage policy promises a Kestrel-funded remainder at resubmission that the resubmission policy's remittance omits), no scored consequence in this bundle.
- Gates: the orchestrator's final full-suite snapshot (EXTENDED / TASK TOOL CONTRACT / REPLAY / SOLVABILITY / COMPUTE / GROUNDING / SCOPE all OK; traceability deferred) is the one on record. The auditor did not re-run them (Step 0: cite, do not run); artifact hashes recomputed at close are unchanged from the brief.

Per-task verdicts:
- task 0: policy self-consistency PASS (task scope) · problem tree **SOURCE-CHAIN RED** · factors **SOURCE-FACTOR RED** · unique solution PASS.
- task 1: policy self-consistency PASS (task scope) · problem tree PASS · factors **SOURCE-FACTOR RED** · unique solution PASS.
- charter: **SOURCE-POLICY RED** (G-R1).

## revision_2

### charter_global_frozen (revision 2)

- Freeze time: 2026-10-06T10:24:45Z, before any round-2 GT was revealed. Auditor: erl-task-policy-audit (independent; same auditor as round 1).
- Inputs (sha256 recomputed; they match the orchestrator's round-2 brief): `title.extended.yaml` 52c2449e5670085498896c43de343f30e45956348a7b8f845eb21d5bda2af13b, `task_tools.py` 2736b1432dfb70423ace946297987321b5a877e0f326ec8cf1da16a40553e946, `task_0.view.json` 39c3fdc2…6828, `task_1.view.json` 9f147aa1…69d8. Both shared inputs changed, so every charter-global section is re-derived in full below; nothing is carried forward by reference.
- Base copy: lines 1–1012 still byte-identical to `blueprint/products/title.yaml`.
- Gate snapshot (round 2, from the brief): EXTENDED / TASK TOOL CONTRACT / REPLAY / SOLVABILITY / COMPUTE / GROUNDING / SCOPE all OK; traceability deferred.
- contamination_disclosure: the auditor saw the round-1 GT of both tasks (revealed in round 1 after the round-1 freeze). These are the round-1 values 22.85, 54, 62.90, 33.50, 145.40, 62.78 and their factor sensitivities. Every round-1 value had equalled the auditor's own round-1 blind figure, so that knowledge adds nothing beyond the auditor's own earlier derivation. Round-2 GT (`tasks/*.json` after rework) and `worklog.md` were not read before this freeze, and no recursive grep was run.

### policy_conflict_scan (revision 2)

Same six policies, tools, owners and `computes`; scopes unchanged and disjoint. Trigger separation between the three payment policies is now stated on both sides: shortage_cure_share applies to "a fee-shortage return that states an amount" and adds "A fee-shortage return that states no amount is not a stated shortage under this rule"; late_penalty_payment applies to "a fee-shortage return that states no amount". Lien charges unchanged in trigger.

Cross-policy check of the round-1 G-R1 pair:
- shortage_cure_share (rule and both overwrites): "the rest of the stated shortage is Kestrel's own cost".
- resubmission_remittance: "Kestrel tops up the remittance for a stated shortage: when the shortage stated on the order's most recent fee-shortage return is larger than the state fees held on the order, Kestrel adds the difference itself as its own cost." Compute `MX(0, LATEST(fee_shortage amount) - held_fees)`.
- The two agree only when the held fees are exactly the buyer's cure share. They differ in two situations the charter allows:
  1. A stated-amount shortage and a lien-error return on the same submission. A rejection is recorded on submitted or rejected orders, so two returns can follow one submission, as on task 1's world. Example: stated 44.80, buyer share 22.85, lien charges 33.50 held. The shortage policy makes 21.95 Kestrel's cost; the top-up is max(0, 44.80 − 56.35) = 0.
  2. An earlier shortage cycle already cured and remitted, followed by a later return. The "most recent fee-shortage return" is still the old one, so the top-up pays its shortfall again.

  Finding G2-R1 (SOURCE-POLICY RED, narrowed from G-R1).

### rule_compute_equivalence (revision 2)

- shortage_cure_share: unchanged compute; rule drops "in full" and adds the no-amount exclusion (an eligibility sentence; with a 0.00 return the formula gives 0 anyway). The rule's "the rest of the stated shortage is Kestrel's own cost" is now implemented only through the resubmission top-up, whose base differs (G2-R1).
- extension_tag_validity: new bindings `fee_shortage_on_latest`, `document_return_on_latest` and `latest_registration_collection` implement "looks at the returns dated on the order's most recent return date … a registration-fee entry has been collected on the order on or after that date"; same-date ties are now defined (closes G-O8). `stretched_allowances`: tier 1 `int(x) + (1 if x > int(x) else 0)` = "rounded up to the next whole day"; tier 2 `int(x)` = "rounded down"; tier 3 `allowance_sum` = "taken as it is". `extension_carry_share` 1 / 0.5 / 0 and `extension_carry_days = int(MX(0, days_left) × share)` match the rule. Matched in both directions.
- late_penalty_payment: compute unchanged; rule window now "after a fee-shortage return that states no amount". Matched.
- lien_correction_charges: `remittances_on_order` guard, e-file without the state condition, `lien_notation_correction` on `lien_fees_collected` and `lienholder`: each quoted; matched. The rule adds "Kestrel still corrects the lien data from the finance records", which carries no compute (descriptive; see G2-O2).
- resubmission_remittance: `kestrel_shortage_topup` and the new channel ladder on `lien_fee_entries`: matched; "made ready again and submitted … in the same action" matches the tool docstring (closes G-O7).
- late_penalty_reimbursement: the first sentence now defines "the standard reimbursement is that reimbursable penalty"; "in full" is gone (closes G-O5); compute unchanged.

### action_binding_and_uuids (revision 2)

Unchanged uuid8s (f6fcb150, 53dbe274, 3594d5af, e09cfc3d, 8a13d7a9, e7fb1913), one policy each. The only docstring change is the resubmit tool ("makes the returned order ready again and submits it in the same action"); it names no other tool and states no sequence. Every function body is still unconditional (no `if` on status, ledger or prior writes; the `if` lines in the tag tool are calendar arithmetic). PASS.

### prerequisite_graph and prerequisite_sentences (revision 2)

The edges E1–E5, their `policy_source` sentences (verbatim in the blocked rules), forms, kinds, gates and `resolved_by` are unchanged. The graph is acyclic.

E1's `condition` now reads "A fee-shortage return is dated on the order's most recent return date, and the order's title ledger carries a registration-fee entry collected on or after that date". It matches the cure-allowance tier 1 and the sentence's "buyer's cure share … as its own fee entry", which the shortage rule books "against the registration fee". Among this difficulty's writes only `pay_title_fee_shortage_f6fcb150` books a registration-fee entry: the penalty write books `not_applicable` and the lien write books `lien_recording_fee`. The round-1 breadth gap is closed (closes G-O4).

The other four edges are as in round 1. No new cross-problem order sentence appears in any rule. The resubmission rule's top-up sentence reads a stated shortage, but it is a value read, not an order between writes.

### override_declarations (revision 2)

- shortage_cure_share now also names title_rejections "fee_shortage by collecting the stated shortage". late_penalty_payment names the same title_rejections clause, with replacement "A shortage the state states as an amount is not a late-registration penalty under this rule". lien_correction_charges names title_rejections "lien_information_error is cured by Kestrel from the finance records". Round-1 G-O1 is closed as a declaration matter.
- Two policies still supersede each of the two shared base clauses: the title_service_fees shortage clause and the title_rejections fee_shortage clause. The replacement texts differ and are separated by stated amount versus no amount. Observation G2-O1 (round-1 G-O2 persists in this form).
- lien_correction_charges supersedes "lien_information_error is cured by Kestrel from the finance records", then restates "Kestrel still corrects the lien data from the finance records". Observation G2-O2.
- The round-1 overwrite of the opening lien-fee clause is withdrawn, so base title_service_fees "plus the lien recording fee when a lienholder is to be recorded" is again in force (closes G-O3). See G2-O3 for its bearing on task 1's seed.
- Reimbursement: the superseded "reimbursed in full" is no longer restated in the rule (closes G-O5).

### factor_ladders (revision 2)

Changes against round 1:

| policy | factor | label | honest? | tiers / real-ladder test |
|---|---|---|---|---|
| shortage_cure_share | buyer_document_clock | method | yes | pass; `cross_difficulty` now null (closes G-O6) |
| extension_tag_validity | extension_cure_allowance | parameter | yes | 3 tiers, same-date defined; pass |
| | extension_last_tag_stretch | method | **yes now**: the tiers differ in operation (×1.25 then round up; ×1.1 then round down; identity), not only in a number | pass (closes the stretch half of G-F1) |
| | extension_carry_over_share | parameter (relabelled) | yes | pass (closes the carry half of G-F1) |
| lien_correction_charges | lien_wait_clock | method | yes | **fails**, see G2-F1 |
| | electronic_lien_filing_charge | parameter | yes | 3 tiers (outside / Kestrel Finance only / none); no tier part holds for every customer; pass |
| | lien_notation_correction_charge (replaces lien_renotation_charge) | parameter | yes | 3 tiers (lien fee already collected / none collected and lienholder / no lienholder); all reachable; pass |
| resubmission_remittance | packet_channel_charge | parameter | yes | tiers mail / electronic with a lien recording fee collected / electronic without; "returned at least once" removed; fall-through reachable; pass (closes G-F3) |

Counts: shortage 5 (3m, 2p). Extension 6 (1m, 5p). Penalty 4 (1m, 3p). Lien 4 declared, 3 surviving (G2-F1). Resubmission 5 (1m, 4p). Reimbursement 5 (2m, 3p).

### findings (revision 2)

**G2-R1 — SOURCE-POLICY RED (G-R1 narrowed, not closed; bears on tasks 0 and 1 as the two sides)**
- Symptom: Kestrel's share of a stated fee shortage is defined twice, on different bases.
- Evidence: shortage_cure_share rule and overwrites: "the buyer's cure share of the stated shortage is collected from the buyer as its own entry, and the rest of the stated shortage is Kestrel's own cost". resubmission_remittance rule: "when the shortage stated on the order's most recent fee-shortage return is larger than the state fees held on the order, Kestrel adds the difference itself as its own cost"; compute `kestrel_shortage_topup: MX(0, LATEST(... fee_shortage amount) - held_fees)`.
- Demonstrated consequence: the two situations in `policy_conflict_scan (revision 2)`. With a stated 44.80, share 22.85 and lien charges 33.50 held, the shortage rule puts 21.95 on Kestrel; the resubmission formula tops up 0.00. After an earlier cured cycle, the top-up pays an old shortage again.
- Scored impact: none in this bundle. Task 0 scores no resubmission. On task 1 the only fee-shortage return states 0.00, so the top-up is 0.00 and the shortage policy does not apply.
- Affected: `title.extended.yaml` title_ext_resubmission_remittance.rule / compute.kestrel_shortage_topup; title_ext_shortage_cure_share.rule / overwrite[*].replaced_by.

**G2-F1 — SOURCE-FACTOR RED (G-F2 partly closed; lien_wait_clock still restates scope; bears on task 1)**
- Symptom: both non-fall-through tiers of lien_wait_clock conjoin "the order has a remittance", which holds of every customer who reaches this write.
- Evidence:
  - The policy applies "while the state's return for a lien information error is dated on or after the order's most recent submission", so the order has been submitted.
  - Base title_submission: "Every held state fee is remitted with the submission as its own remittance entry."
  - Every service's `state_fee_components` includes `title_fee`, and every state's schedule title fee is positive (AZ 4.00 … PA 67.00), so the first submission always books a remittance.
  - The fall-through's "or the order has no remittance" branch is unreachable.
- Consequence: lien_wait_clock fails the real-ladder test, so the lien-charge computation keeps 3 surviving factors (late_lien_surcharge, electronic_lien_filing_charge, lien_notation_correction_charge) against the bound of 4–6.
- Affected: `title.extended.yaml` title_ext_lien_correction_charges.rule (lien-wait sentence), factors[0], compute.lien_wait_start.

**Closed round-1 items, verified against the artifacts:** G-F1 (both halves), G-F2 (electronic_lien_filing_charge and the re-notation ladder; the lien_wait_clock part persists as G2-F1), G-F3, G-O1 (declarations now present), G-O3, G-O4, G-O5, G-O6, G-O7, G-O8, G-O9. G-O2 persists as G2-O1.

**Observations (revision 2)**
- G2-O1 Each of two base clauses is superseded by two policies with different replacements; the domains are separated by stated amount versus no amount.
- G2-O2 lien_correction_charges supersedes the base "cured by Kestrel from the finance records" and restates it in its own rule ("Kestrel still corrects the lien data from the finance records").
- G2-O3 With the opening lien-fee clause restored, a lienholder order in a state with a positive lien fee should show a `lien_recording_fee` collection at opening. Task 1's seed has none (NC, 21.50). The notation-correction tier "no lien recording fee was collected and the order records a lienholder … the notation is added late" is written for exactly such a missed collection, so the seed reads as a seeded Kestrel error rather than an impossible world. Tested in `1.md` revision_2.

### closing_checklist (revision 2)

Written after the round-2 reveals at 2026-10-06T10:26:18Z. The round-1 checklist above is left untouched.

- Audit files: `0.md` and `1.md` each carry a revision_2 section with a frozen derivation, a comparison and findings. Round-1 text is preserved. Every scored value and every factor sensitivity equals the auditor's frozen round-2 figures.
- Scope and tools: unchanged and closed. The six uuid8s are unchanged and independently generated.
- Trees: task 0 has n=1 (1 value_input edge, 1 user write). Task 1 has n=3 (4 value_input edges, 2 user writes). Both are acyclic and have no cross-task edges. PASS.
- Factors:
  - Every computation's baseline gives a definite number that differs from gold: 44.80 vs 22.85, 30 vs 55, 11.37 vs 62.90, 21.50 vs 33.50, 96.40 vs 145.40, 62.90 vs 62.78.
  - Every factor bears weight.
  - Remaining failure: G2-F1. lien_wait_clock restates scope, leaving the lien computation with 3 surviving factors.
- Charter: G2-R1 is SOURCE-POLICY RED. Kestrel's shortage cost is defined as "the rest of the stated shortage" in one policy and as "stated shortage − all held fees" in another. It has no scored consequence in this bundle.
- Gates: the round-2 snapshot from the brief is cited. The auditor did not re-run the gates.

Round-1 claims, checked against the artifacts:
- G-R1: narrowed, not closed → G2-R1.
- G-F1 / T0-F1: closed.
- G-F2 / T1-F1: partly closed → G2-F1.
- G-F3: closed.
- T0-C1: closed.
- G-O1, G-O3 through G-O9: closed. G-O2 persists as G2-O1.
- T0-O1, T0-O2, T1-O1, T1-O3, T1-O4: closed or moot.
- T1-O2: unchanged by choice.

New observations this round: G2-O2 and G2-O3 / T1-O5. Nothing regressed on any scored value.

Per-task verdicts (revision 2):
- task 0: self-consistency PASS · tree PASS · factors PASS · unique solution PASS → **PASS**.
- task 1: self-consistency PASS · tree PASS · factors **SOURCE-FACTOR RED** (G2-F1) · unique solution PASS.
- charter: **SOURCE-POLICY RED** (G2-R1). The difficulty does not yet pass the source-layer audit.

## revision_3

### charter_global_frozen (revision 3)

- Freeze time: 2026-10-06T10:39:16Z onward; written before any round-3 GT was revealed. Auditor: same independent auditor.
- Inputs (sha256, recomputed and matching the brief):
  - `title.extended.yaml` 36ce188b3cc124748990b12d134b99d138c3922a4cfee42332dc94ff0d4589a6 (changed)
  - `task_tools.py` 2736b1432dfb70423ace946297987321b5a877e0f326ec8cf1da16a40553e946 (unchanged since round 2)
  - views 39c3fdc2…6828 and 9f147aa1…69d8 (unchanged since round 2)
- Re-derivation scope: the charter changed, so every charter-global section is re-checked below. The tool module is unchanged, so `action_binding_and_uuids (revision 2)` is carried forward on the unchanged hash 2736b143…e946.
- Base copy: lines 1–1012 are still byte-identical to the blueprint.
- Gate snapshot (round 3, from the brief): all OK; traceability deferred.
- contamination_disclosure: the auditor has seen the round-1 and round-2 GT of both tasks, all of which equalled its own frozen figures. Round-3 `tasks/*.json` and `worklog.md` were not read before this freeze.
- Additional permitted read this round: `blueprint/products/purchase.yaml`, rules `purchase_payment_funding` and `purchase_handover_readiness`, and the purchase lifecycle. Several factors of this charter read purchase rows, so the purchase product's own rules govern whether those rows can exist.

### Changes checked (revision 3)

- **Shortage and penalty overwrites.** The two policies now supersede the title_service_fees shortage clause and the title_rejections fee_shortage clause with one identical replacement text, which the rules of both policies also carry: "the buyer pays, as its own entry, either the buyer's cure share of the stated shortage when the return states an amount or the late-registration penalty when the return states no amount; the rest of a stated shortage is Kestrel's own cost." The merged semantics are unique. **G2-O1 closed.**
- **Lien overwrite.** The replacement now says "Kestrel corrects the lien data from the finance records and the buyer pays the lien charges". The superseded clause is no longer contradicted by a restatement. **G2-O2 closed.**
- **Resubmission top-up.** The rule reads "when the order's most recent fee-shortage return states an amount and no remittance has been made since that return, Kestrel adds the rest of the stated shortage, which is the stated shortage less the buyer's cure share collected for it as a registration-fee entry on or after that return, never below zero". The compute is `MX(0, shortage_stated - cure_share_collected) if (stated_shortage_returns > 0 and (remittances_on_order == 0 or shortage_return_date > latest_remit_date)) else 0`.
  - Both round-2 counter-situations are resolved. The held lien charges no longer net against Kestrel's cost. An already-remitted shortage cycle is not topped up again.
  - This now equals the shortage policy's "rest of a stated shortage". Rule and compute match.
  - **G2-R1 closed.**
- **Lien wait clock.** The "has a remittance" guard is gone. The tiers now read: posting on or before the most recent submission → submission date; posting after the most recent submission → posting date; no outside posting → opening date. The round-2 defect (a condition every customer meets) is gone. Whether tier 2 can be reached at all is tested below; it cannot (G3-F2).
- **Unchanged since round 2, re-checked:** extension, penalty and reimbursement rules and computes; edges E1–E5 and their sentences; tools.

### Cross-product reachability of purchase-ledger tiers (new check this round)

The purchase charter, part of this scenario's constitution, constrains when an outside lender's proceeds can post:
- purchase_payment_funding: "A payment is posted only on an order whose status is contracted or cancelled" (eligibility `payment_state`, allowed [contracted, cancelled]).
- Same rule: "Outside lender proceeds must be received within the program's outside lender funding days after the purchase agreement signing date; when they are not, the order is cancelled". Funding days are 10 for Value Line through Certified Plus and 14 for Premium and Factory Certified.
- purchase_handover_readiness: "A vehicle is handed over … only when … the order balance is zero or below".
- Title side: title_submission "The packet is submitted only when the purchase order balance is zero or below". The title order opens at signing (`opened_date` = signing date).

Consequences for this charter's ladders:
1. An outside lender's posting always comes before handover and within 10–14 days of opening.
2. It always comes before the title order's first submission, which requires a funded order, and hence before every later submission.
3. The lender's penalty days, defined as days from opening to the posting less the dealer deadline days (20–30), are always 0.

**G3-F1 — SOURCE-FACTOR RED (unreachable tiers; reimbursement policy; bears on task 1)**
- reimbursed_share_allocation tiers 1 and 2 both require "the lender's penalty days are above zero". By consequence 3 no customer can meet this, so only the fall-through (share 1) is reachable. The ladder has one real tier.

**G3-F2 — SOURCE-FACTOR RED (unreachable tier; lien policy; bears on task 1; G2-F1 is replaced by a new form, not closed)**
- lien_wait_clock tier 2, "the outside lender's proceeds were posted after the most recent submission", is unreachable by consequence 2.
- The ladder has two real tiers: posted before the submission, or no outside posting.
- The same tier existed in rounds 1 and 2 as "posted after the most recent remittance". The auditor missed it in those rounds; it is recorded now and is not a regression of the artifacts.

**G3-F3 — SOURCE-FACTOR RED (seeded cross-difficulty rows contradict the purchase charter; bears on both tasks; present since round 1, missed by the auditor in rounds 1–2)**
- Task 0 seed, purchase order 1a29f9d7 (Kestrel Certified, funding days 10):
  - Signed 2026-07-29 and handed over 2026-08-09; status completed, closed 2026-08-16.
  - The outside-lender posting f4b53bdd (21,474.00) is dated 2026-08-19. That is 21 days after signing (limit 10), after handover and after closure.
  - On the handover date the order still owed 21,474.00 (charges 24,974.00 less 3,500.00 paid), contrary to handover readiness.
- Task 1 seed, purchase order fc5b5258 (Kestrel Certified Plus, funding days 10):
  - Signed 2026-07-06 and handed over 2026-07-09; closed 2026-07-16.
  - The outside-lender posting f642ab5c (25,049.00) is dated 2026-08-14. That is 39 days after signing, after handover and after closure.
  - On the handover date the order still owed 25,049.00.
- Every factor that reads the posting date rests on a row the purchase charter makes impossible. Demonstrations against each task's scored values are in `0.md` and `1.md` revision_3.

### factor_ladders (revision 3, structure delta)

| policy | factor | change | test |
|---|---|---|---|
| lien_correction_charges | lien_wait_clock | guard removed; anchor moved to the submission date | **fails**: tier 2 unreachable (G3-F2) |
| late_penalty_reimbursement | reimbursed_share_allocation | unchanged | **fails**: tiers 1–2 unreachable (G3-F1) |
| shortage_cure_share | kestrel_handling_clock | unchanged | ladder reachable (a posting before handover can follow the latest document); the seeded row fails (G3-F3) |
| all others | — | unchanged | as in revision 2 |

Surviving factor counts:
- lien charges: 3 of 4 (surcharge, e-file, notation correction), still below the bound.
- reimbursement: 4 of 5. The bound is met, but G3-F1 is a failed ladder.
- shortage: 5. Extension: 6. Penalty: 4. Resubmission: 5.

### findings (revision 3)

- Closed and verified against the artifacts: G2-R1, G2-O1, G2-O2.
- G2-F1: no longer restates scope, but it leaves an unreachable tier (G3-F2).
- G2-O3 / T1-O5: the seed is unchanged (no opening lien fee); it stays an observation with the same reasoning.
- New this round, though present in the artifacts since round 1: G3-F1, G3-F2, G3-F3.

### closing_checklist (revision 3)

Written after the round-3 reveals at 2026-10-06T10:41:49Z. Earlier checklists are left untouched.

- Audit files: `0.md` and `1.md` each carry revision_3 with a frozen derivation, a comparison and findings. Every GT value and sensitivity equals the frozen round-3 figures.
- Scope and tools: unchanged. Each uuid8 is independent.
- Trees: task 0 has n=1 and task 1 has n=3. All edges are value_input, both trees include a customer write, and both are acyclic. PASS.
- Charter: G2-R1, G2-O1 and G2-O2 are closed. No SOURCE-POLICY RED remains.
- Factors fail on three counts:
  - G3-F1: the reimbursement share ladder has an unreachable non-fall-through tier.
  - G3-F2: lien_wait_clock tier 2 is unreachable, so the lien computation keeps 3 of 4 factors.
  - G3-F3: both seeds carry an outside-lender posting that the purchase charter forbids, and the gold of task 0's cure payment and task 1's reimbursement depends on it.
  These existed since round 1 and were found by the new cross-product reachability check this round. They are not regressions of the artifacts.
- Gates: the round-3 snapshot from the brief is cited. The auditor did not re-run the gates.

Per-task verdicts (revision 3):
- task 0: self-consistency PASS · tree PASS · factors **SOURCE-FACTOR RED** (T0-F2 / G3-F3) · unique solution PASS.
- task 1: self-consistency PASS · tree PASS · factors **SOURCE-FACTOR RED** (T1-F1 → G3-F2; T1-F2 → G3-F1, G3-F3) · unique solution PASS.
- charter: no SOURCE-POLICY RED remains. The difficulty does not yet pass the source-layer audit.

## revision_4

### charter_global_frozen (revision 4)

- Freeze time: 2026-10-06T11:00:13Z onward, written before any round-4 GT was revealed. Auditor: the same independent auditor.
- Inputs (sha256, recomputed; they match the brief):
  - `title.extended.yaml` 2b26aeebc242ef722bb55d933da8c7caf427508f78f95839996f7972b34442eb (changed)
  - `task_tools.py` 2736b143…e946 (unchanged; `action_binding_and_uuids (revision 2)` is carried forward on this hash)
  - `task_0.view.json` d366bea0…58d8 and `task_1.view.json` 67411a72…2d2c (both changed: seed and persona)
- Base copy: still byte-identical to the blueprint.
- Gate snapshot (round 4, from the brief): all OK; traceability deferred.
- contamination_disclosure: the auditor has seen the round-1 to round-3 GT; every value equalled its own frozen figures. Both worlds changed materially, so each task is re-derived blind from the new views. Round-4 `tasks/*.json` and `worklog.md` were not read before this freeze.

### Charter changes checked (revision 4)

Every rule, compute and ladder was re-read. These changed:

- **extension_handover_allowance**: the thresholds are now >14 days → 3, 8–14 days → 1, within 7 days → 0, in both rule and compute. All three tiers are reachable: the purchase charter sets only a minimum signing-to-handover lead (`handover_signing_lead_days`) and no maximum. Pass.
- **lien_wait_clock**:
  - Tiers: an outside lender's proceeds were posted → most recent submission date ("because the lender's lien was on record when that packet went to the state"); Kestrel Auto Finance proceeds only → most recent lien-error return date; no lender proceeds → opening date. Rule and compute match.
  - Every tier is reachable, and no tier condition holds for every customer.
  - Under the purchase charter an outside posting precedes the submission, so the anchor no longer depends on an impossible ordering.
  - **G3-F2 closed.** Observation G4-O2: the factor reads purchase payment sources but declares `cross_difficulty: null`.
- **reimbursed_share_allocation**: the lender-delay split is replaced.
  - Tier 1: the buyer missed the first scheduled handover and the first submission came after the handover. The share is (total days late − buyer's handover delay days) / total days late.
  - Tier 2: no such missed handover, and a customer-document return. The share is (total − buyer's correction days) / total.
  - Fall-through: share 1.
  - Compute matches. It adds a `penalty_total_days > 0` guard against division by zero, which the rule does not state; observation G4-O3.
  - Both non-fall-through tiers are reachable (a delivery missed for `customer_unavailable`; a customer-document return). Neither holds for every customer. The condition reads `delivery.last_miss_cause`, while the rule says "missed the first scheduled handover"; the same convention as buyer_document_clock, observation G4-O4.
  - **G3-F1 closed.**
- **Unchanged since round 3**: the shortage, penalty and resubmission rules and computes, edges E1–E5 and their sentences, and the tools.

Counts after the tests:
- shortage 5 (3 method, 2 parameter)
- extension 6 (1 method, 5 parameter)
- penalty 4 (1 method, 3 parameter)
- lien 4 (1 method, 3 parameter), all surviving
- resubmission 5 (1 method, 4 parameter)
- reimbursement 5 (2 method, 3 parameter)

No SOURCE-POLICY or charter-level SOURCE-FACTOR finding remains.

### findings (revision 4, charter level)

- Closed and verified against the artifacts: G3-F1 and G3-F2. G3-F3 is a seed matter, verified per task in `0.md` and `1.md` revision_4.
- G2-O3 / T1-O5: task 1's new seed carries the opening lien recording fee (b4988dd5, 21.50) and its remittance. Closed.
- Observations G4-O2 to G4-O4 above. G4-O1 is in `0.md`.

### closing_checklist (revision 4)

Written after the round-4 reveals at 2026-10-06T11:02:57Z. The earlier checklists are left untouched.

- Audit files: `0.md` and `1.md` each carry revision_4, with a blind derivation from the new views frozen before the reveal, a comparison, and findings. All four relationships PASS for both tasks. Every GT value and every factor sensitivity equals the frozen figures. The revision history from rounds 1–3 is preserved.
- Coverage and scope: the six extended policies are covered by two disjoint trees. Tools and GT are closed. The six uuid8s are independent and unchanged.
- Trees:
  - Task 0: n = 1, one value_input edge, one customer write.
  - Task 1: n = 3, four value_input edges, two customer writes.
  - Both are acyclic, and the union graph is acyclic. Every edge is unmet at the opening and bears weight.
- Factors:
  - Every computation's baseline gives a definite number that differs from gold: 44.80 vs 22.85, 30 vs 59, 11.37 vs 62.90, 21.50 vs 37.50, 100.40 vs 149.40, 62.90 vs 59.83.
  - Each computation has 4–6 factors, with at least 2 parameter and 1 method.
  - Each task has at least one multi-source factor and at least one cross-difficulty factor reading purchase rows. Those rows are now consistent with the purchase charter.
  - Every ladder has at least three reachable tiers, and every factor bears weight.
- Charter: no SOURCE-POLICY RED remains.
- Gates: the round-4 snapshot from the brief is cited. The auditor did not re-run the gates.
- Open observations (not grounds for rework):
  - T1-O2: unchanged by the reworker's choice.
  - G4-O1: task 0's history shows a lien-return resubmission without the extended lien charges; sensitivity 6.72 against 22.85.
  - G4-O2: lien_wait_clock `cross_difficulty` label is null.
  - G4-O3: the reimbursed-share division guard is not stated in the rule.
  - G4-O4: "first missed handover" is read through `last_miss_cause`.

Per-task verdicts (revision 4):
- **task 0: PASS.**
- **task 1: PASS.**
- The difficulty passes the source-layer audit.
