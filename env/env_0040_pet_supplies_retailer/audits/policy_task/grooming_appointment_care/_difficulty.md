# Policy-task audit — grooming_appointment_care / charter-global

## charter_global_frozen

- Freeze time: before 2026-10-06T06:01:41Z (reveal command), after 0.md and 1.md; before any task's GT was revealed. (Corrected after reveal: an earlier estimated timestamp in this line was wrong.) Nothing in this section is derived from `tasks/*.json`.
- Auditor: independent policy-task auditor (Claude agent, erl-task-policy-audit).
- Freeze hashes: `groom.extended.yaml` b86e734438dcaa99d73e1e4d1ed0b00167a45bf751d2eb3da494fa71f87c23d6; `task_tools.py` 9fb0a7b8289c4aa3ac1654edc68483108646893cacc23890e17db65cb491b742 (both match the orchestrator brief).
- Permitted: `blueprint/` (blueprint.yaml, db_schema.json, share_tools.py, products/groom.yaml; member/vet/autoship/order product files for variant names), `groom.extended.yaml`, `task_tools.py`, the masked views, the instantiate DSL evaluator (`skills/erl-task-instantiate/scripts/check_compute.py`) for the semantics of LATEST/COUNT/within_months/RND. Masked: `tasks/*.json` in full, worklog, prior audits.
- Entry conditions (Step 0): gate snapshot supplied (`/tmp/e40views/policy_task/grooming_appointment_care/gate_snapshot.txt`): check_extended, check_task_tools, replay_tasks, check_solvability, check_compute, check_grounding, check_cross_fire all exit 0; check_traceability deferred by the orchestrator until the KB is published (recorded, not run by the auditor). Masked views supplied with sha256 that match the files on disk. Entry conditions met.

### policy_conflict_scan

Extended policies (4): `groom_ext_pass_late_cancel_fee` (prepaid passes, subject groom_late_cancel_fee, → `charge_late_cancel_fee_38a40f67`), `groom_ext_pass_cancel_refund` (prepaid passes, groom_pass_cancel/refund, → `cancel_groom_pass_241c8b1d`), `groom_ext_club_late_cancel_charge` (club only, groom_late_cancel_fee, → `charge_club_late_cancel_73de6594`), `groom_ext_club_cancel_settlement` (club only, groom_pass_cancel/refund, → `cancel_groom_club_74a11dc2`).

- Overlapping subjects: the two late-fee policies share `groom_late_cancel_fee`, the two cancel policies share `groom_pass_cancel`/`groom_pass_refund`. Each pair is partitioned by the variant: every one of the four rules opens with a scope sentence ("This rule applies to prepaid passes (Express Bath, Bath & Tidy, Full Groom and Spa Groom passes); Groom Club Monthly follows its own rule." / "This rule applies to Groom Club Monthly only; prepaid passes follow their own rule." / the two cancel rules likewise). The six variants are covered exactly once in each pair. No overlap of trigger or object.
- Triggers / eligibility / time anchors: late fees are `state_due` on any fee-remedy cancellation lacking an entry; cancellations are `on_request`; status eligibility for cancellation (active or suspended) is inherited from base and not weakened. today = frozen_time date for every window.
- Terminal states: prepaid cancel → status cancelled, closed_on today, visits 0, refund row to original payment; club cancel → status cancelled, closed_on = expires_on, next_billing_date null, settlement row collected from card. No two policies write the same field with different values.
- Cross-category read boundaries: declared `cross_category` blocks (member branch; vet history; autoship history; order history) match the compute's CFIELD/XLATEST/XCOUNT/XSUM reads one-to-one (also gated green by check_extended).
- Scope partition of the M = 2 tasks (from the masked views alone; to be compared with `charter_scope` at reveal): task 0 is a Full Groom Pass 6-Visit world (prepaid → pass fee + pass refund); task 1 is a Groom Club Monthly world (club charge + club settlement). The two scopes are disjoint and jointly cover all four extended policies.

### rule_compute_equivalence

Swept every binding of the four computes against its `compute_basis` quotation and back over each rule sentence.

- `groom_ext_pass_late_cancel_fee`: base fee, add-on ladder (4 tiers), weekday slot (DAYS from a Saturday anchor %7: 0/1 → weekend, 6 → Friday, else 1 — checked: 2024-01-06 is a Saturday), fee basis, notice ladder (prorate / ×0.75 / whole), repeat count (no-shows + fee-remedy cancellations, `within_months` = MONTHS(d, today) in [0, 6), the evaluator's reading of "within the last repeat_window_months whole calendar months before today"), Plus relief, clinic relief (active plan; office_visit only; gap counted to the cancelled appointment date), combined relief capped at 100 applied once, one final rounding — every rule sentence has a binding and every binding a quotation. Exception: finding F1 (the add-on and the cancellation are read by LATEST, not by the booking the cancellation refers to).
- `groom_ext_pass_cancel_refund`: price, paid rate, used visits (complete/no-show/forfeit with visits_delta 1), whole months purchased_on→today, discount pct from discount_kind, three-tier used-visit valuation, expiry share on days to expires_on, redo credit, Autoship admin ladder (charged shipments, skips not counted — filter event_type autoship_shipment_charge), fees booked and fee-entry share, full-refund window (day 0, inclusive), operation order (expiry share on unused value; + redo credit; − admin; − withheld fees; one rounding; floor 0) — equivalent both ways.
- `groom_ext_club_late_cancel_charge`: visit value price_paid_usd / visits_included, notice ladder, missed-visit courtesy (forfeits + no-shows, cancellation rows not counted), tenure in days purchased_on→today, clinic relief, multiplicative chain and one rounding — equivalent, subject to F1 (the cancellation is read by LATEST).
- `groom_ext_club_cancel_settlement`: billed months (= `groom_club_billing` rows; matches "a monthly fee charged on the club after the month of joining" because `groom_pass_pricing` puts the first fee on the purchase row), ETF ladder incl. the "nothing when ≥ min term" branch, billing-notice multiplier on days to next_billing_date, three reliefs summed and capped once, charge collection share, one rounding — equivalent.
- Rounding: every rule says "rounded half up to the cent"; the compute uses `RND` = Python `round(float, 2)` (binary float, not decimal half-up). Observation O-R (see findings): it diverges only on exact half-cent ties (e.g. 115.665 → 115.66 under RND, 115.67 half-up), none of which is a gold value in either task (see task files).

### action_binding_and_uuids

- `(target_tool, computes)`: (charge_late_cancel_fee_38a40f67, amount_usd), (cancel_groom_pass_241c8b1d, refund_usd), (charge_club_late_cancel_73de6594, amount_usd), (cancel_groom_club_74a11dc2, settlement_usd) — each claimed by exactly one policy.
- Docstrings: each describes one atomic ledger change, owner and effect; none names another tool, states a position in a sequence, or carries before/after/first/then/prior (grep: only "visible at once", which is a visibility statement, not an ordering). Module docstring: "none of them checks eligibility, prerequisites or amounts" — confirmed by the bodies (find + create/update only).
- uuid8 tails 38a40f67, 241c8b1d, 73de6594, 74a11dc2: pairwise distinct, no shared prefix or sequential pattern, none reused in the base charter or share tools. Pass.
- Owners: the two cancel tools are owner=user ("Only the customer can cancel a pass" — base, inherited), the two charge tools owner=agent. Consistent with the blueprint summary ("cancelling a pass are the owner's own acts done through the hand-over tools").

### prerequisite_graph

- `prerequisite` filled on all four: the two late-fee policies `[]`; `groom_ext_pass_cancel_refund` → `groom_ext_pass_late_cancel_fee`; `groom_ext_club_cancel_settlement` → `groom_ext_club_late_cancel_charge`. Both targets are extended ids in this file, not self, not base. Graph: two disjoint edges, acyclic.
- `policy_source` verbatim in the blocked rule's own text: pass — "The refund on a cancelled pass is fixed only after every cancellation on the pass that is recorded with a fee remedy carries its late-cancellation fee entry." (present, third sentence of the rule); club — "The club cancellation settlement is not fixed until every cancellation on the club that is recorded with a fee remedy carries its club late-cancellation charge entry." (present, fourth sentence). 
- `form: state` on both, no `fallback_reason` — correct.
- `condition` ("Every groom_appointment_cancel row of the pass/club with late_cancel_remedy fee has a groom_late_cancel_fee row on the same pass/club whose original_event_id is that cancellation's original_event_id") states exactly the sentence's scope — every fee-remedy cancellation of that holding — neither stronger nor weaker.
- `resolved_by` = the depended-on policy's `target_tool` in both cases, and that tool creates exactly the `groom_late_cancel_fee` row with the booking's id as `original_event_id` (the cancellation row's `original_event_id` is also the booking id), so the condition becomes true.
- `kind: value_input`, `gate` fees_booked / charges_booked — both are bindings of the blocked compute, and `effect` ("the refund falls accordingly" / "the settlement rises accordingly") is the correct sign (fees_booked × fee_share is subtracted; charges_booked × charge_share is added).
- No authoring-viewpoint phrasing ("in this task", "at the opening") in any `prerequisite` field.

### prerequisite_sentences

Four-point test, both edges:
1. Ordering connective joining the policy's own result to what it waits on: "is fixed only after …" / "is not fixed until …" — pass.
2. What is waited on is a record-visible state in finder vocabulary: a cancellation "recorded with a fee remedy" (field late_cancel_remedy = fee on the salon history) "carries its late-cancellation fee entry" / "club late-cancellation charge entry" (salon history entry of the fee type, `find_groom_events` docstring: "late-cancellation fees and forfeits") — no action, performer or tool — pass.
3. No tool name, policy id, snake_case token or row id — pass.
4. Strength/scope equals `condition` (every such cancellation on that holding) — pass.

One write per state: for a prepaid pass, the state "late-cancellation fee entry" is brought about by `groom_ext_pass_late_cancel_fee` ("booked to the pass as a late-cancellation fee entry for the cancelled booking"); for the club, "club late-cancellation charge entry" by `groom_ext_club_late_cancel_charge` ("booked to the club as a club late-cancellation charge entry"). The other charge policy is excluded by its scope sentence in each case. (Mechanically both tools write the same event_type; see observation O-T.)

Derivation a reader performs (pass; the club is symmetrical): refund rule's sentence → look up the pass history → a cancellation with late_cancel_remedy fee and no fee entry tied to its booking → which policy books "a late-cancellation fee entry" on a prepaid pass → the pass late-fee rule, whose own trigger sentence ("The fee is owed for every cancellation recorded on the pass with a fee remedy that does not yet carry such an entry") confirms it is due → its target write. Single reading.

The rules carry nothing else about the dependency: the depended-on rules do not restate the sentence; no rule of the charter states any other cross-problem order (swept: base rules of groom_cancellation_no_show, groom_pass_cancel_refund, groom_club_monthly_billing, groom_booking_requirements, groom_satisfaction_redo, groom_pass_expiry, groom_pass_transfers contain no ordering between these problems; "A fee or forfeit is never charged twice for the same booking" is a dedup, not an order). No base sentence grounds an edge.

### override_declarations

Sentence-by-sentence against each `base_policy_refs` entry.

`groom_ext_pass_late_cancel_fee` vs `groom_cancellation_no_show`:
- "A customer may cancel or reschedule … plus a new booking." — followed (not touched).
- "A cancellation is free only if … free_cancel_notice_hours …" / "Notice is counted in full elapsed hours … exactly … is free." — followed; the extended notice ladder starts below free hours (fee-remedy cancellations only).
- "A late cancellation carries late_cancel_fee_usd, or, where late_cancel_forfeits_visit is true, forfeits one visit instead of the fee" — handled differently (computed fee) → declared in `overwrite` verbatim. Merged semantics: on prepaid passes late_cancel_forfeits_visit is false for all five variants, so the replaced clause leaves no dropped branch.
- "the remedy is recorded on the cancellation" — followed.
- No-show sentence, salon-cancellation sentence, "never charged twice" — followed (the fee is owed only for a cancellation "that does not yet carry such an entry").
- Disguised forms: no anonymous intermediate or 0/1 multiplier outside the declared fee; the clinic relief can reach 100% (fee 0.00) — that is a tier of the declared replacement, not an undeclared zeroing of a base quantity.

`groom_ext_pass_cancel_refund` vs `groom_pass_cancel_refund`:
- "Only the customer can cancel a pass." — followed (restated).
- "The pass status is active or suspended when the cancellation is requested." — not restated, inherited in full.
- Full-refund sentence — declared overwrite (same semantics, day-0 counting made explicit). Window counting sentence — followed.
- "Otherwise the refund is the price paid minus every used visit … single_visit_price_by_size_usd … minus refund_admin_fee_usd, and never below 0.00; the unused visits are removed." — handled differently (paid-rate valuation, ladders, fee withholding) → declared verbatim.
- Club sentence — not applied to prepaid passes; the rule sends the club to its own rule.
- "Refunds go to the original payment." — followed.
- Base `formula` (amount_usd = max(round(price − used × single_visit_price − admin), 0)) is the formal face of the overwritten sentence; covered by the same declaration.

`groom_ext_club_late_cancel_charge` vs `groom_cancellation_no_show`:
- Remedy sentence — declared verbatim; replaced_by keeps the forfeit for the club (late_cancel_forfeits_visit true) and adds the fee remedy only where no credited visit is held. Merged semantics unique: credited visit → forfeit; none → fee remedy + charge.
- Other sentences followed as above.

`groom_ext_club_cancel_settlement` vs `groom_pass_cancel_refund` and `groom_club_monthly_billing`:
- Full-refund sentence — declared (club never refunded in full).
- "Groom Club Monthly is not refunded for the current month: … club_cancel_effective, and a cancellation before club_min_term_months billed months … is charged club_early_termination_fee_usd." — declared verbatim; the rule restates the first two parts unchanged ("not refunded for the current month", "takes effect per club_cancel_effective") and replaces the ETF.
- "Only the customer can cancel", status sentence — followed / inherited.
- `groom_club_monthly_billing`: billing, rollover, nail trims, retry, suspension, reinstatement, automatic cancellation "without an early termination fee" — none governs a customer-requested settlement; the billed-month definition agrees with `groom_msr_billed_months` given `groom_pass_pricing` (first fee on the purchase row). Followed; `overwrite` need not name it.
- "Refunds go to the original payment" — the club settlement is a collection, not a refund (tool: "collected from the card on file"); no conflict.

No undeclared override found.

### factor_ladders

| policy | factor | label | decides (input, not result) | tiers (incl. fall-through) | multi-source | cross_difficulty |
|---|---|---|---|---|---|---|
| pass late fee | addon_part | parameter | addon_part | 4 | no | — |
| | slot_multiplier | parameter | slot_mult | 3 | no | — |
| | notice_treatment | method | after_notice | 3 | no | — |
| | repeat_multiplier | parameter | repeat_mult | 3 | no (one table, two event types) | — |
| | plus_relief | parameter | plus_pct | 3 | no | member (rewards_membership_care) |
| | clinic_relief | parameter | clinic_pct | 3 | yes (vet_plans.status AND vet_plan_events office-visit date) | vet (see O-V) |
| pass refund | used_visit_value | method | used_value | 3 | conjunction (discount_kind AND months; same holding row + clock) | — |
| | expiry_share | parameter | expiry_share | 3 | no | — |
| | redo_credit | parameter | redo_credit | 3 | no | — |
| | autoship_admin_fee | parameter | admin_withheld | 3 | no | autoship (autoship_subscription_care) |
| | fee_withholding_share | parameter | fee_share | 3 | no | — |
| club charge | club_notice_treatment | method | charge_after_notice | 3 | no | — |
| | missed_visit_courtesy | parameter | miss_share | 3 | no | — |
| | new_member_courtesy | parameter | tenure_share | 3 | no | — |
| | club_clinic_relief | parameter | club_clinic_pct | 3 | yes | vet (see O-V) |
| club settlement | etf_method | method | etf_due | 3 (+ the "≥ min term → nothing" branch of the baseline) | no | — |
| | billing_notice | parameter | billing_mult | 3 | no | — |
| | etf_plus_relief | parameter | etf_plus_pct | 3 | no | member |
| | shopper_relief | parameter | shopper_pct | 3 | yes (spend AND line count) | order (order_returns_care) |
| | usage_relief | parameter | usage_pct | 3 | no | — |
| | charge_collection_share | parameter | charge_share | 3 | no | — |

- Counts per policy: 6 (5p/1m), 5 (4p/1m), 4 (3p/1m), 6 (5p/1m) — all within 4–6 with ≥ 2 parameter and ≥ 1 method.
- Bindings pairwise disjoint within each policy; every `decides` is an intermediate.
- Every tier (condition and value/method) is stated in the rule's prose and implemented by the `decides` binding; no tier lives only in compute; every value is a declared param/K or a charter parameter.
- Distinct outcomes within each ladder (e.g. 12.5/9/5/0 for the Full Groom add-on, 1.25/1.1/1, 100/50/0, 0.5/0.75/1, 0/7.5/15, 30/15/0, 20/10/0) — no two tiers select the same value or method. (On Spa Groom passes the three add-on prices are 0.00, so the add-on tiers collapse for that variant; it is not the variant of either task — observation only.)
- Fall-through tiers equal the baseline in every factor (checked against each `baseline.rule`).
- Labels: the three `method` factors each contain at least one tier that changes the algorithm (prorate by hours not given; re-price only the most recent visit; prorate by unbilled share). `redo_credit` is labelled parameter while its top tier multiplies by the redo count — observation O-L; no effect on the bounds (the refund keeps 3+ parameter factors and its method factor either way).
- Business realism: each condition is one a salon/retailer weighs (notice, weekday slot, repeat misses, loyalty tier, recent vet visit, tenure, usage, household Autoship/order spend, discount recapture, nearness to expiry, number of fees) and none holds of every customer reaching the write. The redo credit (a refund that grows with redos received) is the least conventional; it is defensible as service recovery for visits that had to be redone, and is recorded as observation O-B rather than a red light.
- Baselines: each `baseline.rule` is a sentence of the rule, self-sufficient with the records, and its `params` name the defaults used.

### findings

F1 — SOURCE-POLICY RED (charter-global, latent; bears on no scored value of task 0 or task 1).
- Symptom: the compute of the two late-fee policies does not read "the cancelled booking" / "that cancellation" the rule names.
- Root cause: `groom_ext_pass_late_cancel_fee` compute `booked_addon: "LATEST('groom_events', 'addon_code', date_field='appointment_date', event_type='groom_appointment_book')"` takes the booking with the latest appointment date on the pass, while the rule says "The add-on part of the pass late-cancellation fee follows the add-on on the cancelled booking"; `appt_date`/`notice` (and the club's `notice`/`charged_appt_date`) take the latest fee-remedy cancellation, while the rules say the fee "is owed for every cancellation recorded on the pass with a fee remedy that does not yet carry such an entry, and it is worked out from that cancellation".
- Evidence / demonstrated consequence (constructed situation, `/tmp/e40audit_scripts/f1.py`): task 0's world plus a late reschedule — base `groom_cancellation_no_show`: "a reschedule is a cancellation of the old slot plus a new booking" — i.e. a new booking on 2026-10-02 for 2026-10-10 with add-on flea_tick_bath. Rule: the cancelled booking `925cea80-…` carries a deshedding treatment → 12.50 → fee 5.71. Compute: latest booking = the new one → 9.00 → fee 5.10. Two conclusions in the same situation. Likewise a holding with two uncharged fee-remedy cancellations: the rule owes two fees each worked from its own cancellation; the compute yields one figure from the latest; and after one fee is booked the LATEST still selects the already-charged cancellation.
- Affected: `groom.extended.yaml` `extended_policies[groom_ext_pass_late_cancel_fee].compute` (booked_addon, appt_date, notice) and `[groom_ext_club_late_cancel_charge].compute` (notice, charged_appt_date).
- Bears on: task 0 and task 1 — demonstration per task: none (each world has exactly one fee-remedy cancellation and, in task 0, the cancelled booking is the latest booking). See `0.md` / `1.md` § policy_self_consistency.

O-R — observation: rules say "rounded half up to the cent"; `RND` is binary-float `round`. Diverges only on half-cent ties; no gold value of either task is a tie (verified in the task files).

O-T — observation: `charge_late_cancel_fee_38a40f67` and `charge_club_late_cancel_73de6594` write the same `event_type` `groom_late_cancel_fee`; a record does not show which rule booked it (only the id prefix lcf_/clc_). The rules' scope sentences still single out one write per holding type, so the hop resolves; no consequence demonstrated.

O-V — observation: the factors `clinic_relief` / `club_clinic_relief` declare `cross_difficulty: vet`, but `blueprint.yaml` defines no vet difficulty (difficulties: autoship_subscription_care, pharmacy_prescription_care, grooming_appointment_care, rewards_membership_care, order_returns_care). Each task nonetheless has genuine cross-difficulty factors (task 0: member, autoship; task 1: member, order), so the bound holds.

O-L — observation: `redo_credit` labelled parameter although its "two or more" tier scales with the redo count; no bound changes.

O-B — observation: redo credit raises the refund for visits that were redone (business plausibility borderline, defensible as service recovery).

O-C — observation: the club rule says the club closes "on the last day of the current billing month"; the tool closes it on `expires_on`. On a club whose `expires_on` is the day before `next_billing_date` the two agree; `billing_month` labels on billing rows are calendar months ("2026-09"), so a calendar-month reading is also available. closed_on is a tool effect, not a scored parameter.

## post_reveal_addenda

(Written after both reveals; the charter-global section above is unchanged.)

F2 — SOURCE-POLICY RED (charter-global; upgrades pre-reveal observation O-R, whose demonstration 115.665 was already computed blind in `0.md`).
- Symptom: every extended rule says the final amount is "rounded half up to the cent"; every compute ends in `RND(…, 2)`, which the evaluator implements as Python `round(float(x), 2)` (binary float; ties resolve by representation, not half up).
- Evidence / demonstrated consequence: task 0 world, refund with the fee step skipped: exact value 115.665 → rule 115.67, compute 115.66; the same split on three factor-substituted refunds (118.165, 143.155, 109.955). Two conclusions in the same situation.
- Affected: `groom.extended.yaml` every `result` binding (`RND`), and the proof fields of task 0 generated from it (`0.md` T0-F1, T0-F2). No gold value of either task is a tie (5.712890625, 112.81, 5.85859375, 7.51333…), so no scored argument is affected.

Per-task demonstration of the charter findings: F1 — none on either world; F2 — task 0 proof fields only (see `0.md`), none on task 1.

## closing_checklist

- Per-task files `0.md`, `1.md` correspond one-to-one with `tasks/0.json`, `tasks/1.json`; `_difficulty.md` alongside; first revision, no older revisions.
- Comparison sections: task 1 PASS on all four relationships; task 0's scored solution matches blind derivation exactly but carries cent-level proof-field REDs (T0-F1 SOURCE-FACTOR, T0-F2 SOURCE-CHAIN) rooted in F2.
- Coverage: the 4 extended policies are covered; scopes disjoint (task 0: groom_ext_pass_late_cancel_fee + groom_ext_pass_cancel_refund; task 1: groom_ext_club_late_cancel_charge + groom_ext_club_cancel_settlement — `charter_scope` matches the blind partition); 4 task tools with independent uuid8s.
- Trees: each has 1 prerequisite problem, 1 value_input edge, one owner=user write; difficulty graph is two disjoint edges, acyclic.
- Factors: 4–6 per computation, ≥ 2 parameter and 1 method each; per task ≥ 1 multi-source and ≥ 1 cross-difficulty (task 0: member, autoship; task 1: member, order); all bear weight; baselines definite and ≠ gold.
- Gates: the instantiation-stage gate snapshot supplied by the orchestrator is green (check_traceability deferred until the KB is published); not re-run by the auditor (outside the audit's remit per Step 0).
- Difficulty does NOT close the source-layer audit: charter-global SOURCE-POLICY RED F1 (latent, compute reads the latest booking/cancellation instead of the cancelled one) and F2 (half-up vs float rounding), plus task 0's proof-field REDs.

## revision_2

### charter_global_frozen (revision 2)

- Freeze: written 2026-10-06 after 09:34:06Z, before `tasks/0.json` / `tasks/1.json` of round 2 were opened.
- Inputs: `groom.extended.yaml` 181202c7e642d0526059f9793dc6743e1ae43d6afa01c9eadca5eea472c5ae9e (CHANGED from b86e7344… → every charter-global section is re-derived below, not carried forward); `task_tools.py` 9fb0a7b8289c4aa3ac1654edc68483108646893cacc23890e17db65cb491b742 (unchanged → `action_binding_and_uuids` tool-side conclusions carry forward). Gate snapshot `/tmp/e40views/policy_task/grooming_appointment_care/gate_snapshot_r2.txt`: the same 7 gates exit 0 (check_compute history_rows_max now 9, was 14 — consistent with the narrower add-on read); check_traceability deferred. Rebuilt views carry the round-1 hashes (worlds unchanged).
- Contamination disclosure (round 2): the auditor saw the round-1 GT of both tasks at the round-1 reveal. A blind derivation of the scored solution is therefore not available in round 2; the round-1 blind answers in `0.md` / `1.md` stay the frozen blind evidence. Round 2 re-derives every number from the new charter on the unchanged views before opening the reworked task files.
- The reworker's claims were used only as a list of places to look; every conclusion below rests on the artifacts.
- Base copy: lines 1–1501 still byte-identical to `blueprint/products/groom.yaml` (diff empty).

### What changed in the extended section (located by reading the whole section)

1. `groom_ext_pass_late_cancel_fee` rule: new sentences "The cancellation a pass late-cancellation fee is worked out from is the most recently recorded cancellation on the pass with a fee remedy, and the cancelled booking is the booking that cancellation names; where more than one such cancellation lacks its entry, each of those fees is still worked out from that most recently recorded cancellation and the booking it names."; add-on sentence now "follows the add-on on the booking that cancellation names"; final sentence "Half up means a figure lying exactly on a half cent goes to the higher cent." Compute: new `charged_booking: LATEST(groom_events, original_event_id, cancel, remedy fee)`, `booked_addon` now filtered `groom_event_id=charged_booking`; `result` adds `K('half_up_guard')` (= 0.000001, new param). Factor `addon_part` bindings gain `charged_booking`; `clinic_relief.cross_difficulty` → null.
2. `groom_ext_pass_cancel_refund`: redo sentences rewritten ("The redo credit on a cancelled pass counts every redone visit at the per-visit paid rate times the redo share, and the redo share follows the free redos recorded on the pass: two or more redos take redo_multi_share, exactly one redo takes redo_single_share, and no redo takes a share of zero."), new param `redo_multi_share: 1`; compute `redo_share` + `redo_credit = redo_count * paid_rate * redo_share`; factor `redo_credit` now `decides: redo_share` with values redo_multi_share / redo_single_share / 0; half-up sentence and guard added.
3. `groom_ext_club_late_cancel_charge`: selection sentences added (most recently recorded fee-remedy cancellation; same multi-cancellation clause); half-up sentence + guard; `club_clinic_relief.cross_difficulty` → null.
4. `groom_ext_club_cancel_settlement`: "the club closing on its expires_on, the last day of the current billing month"; half-up sentence + guard.
Nothing else changed: params values, other rule sentences, prerequisite blocks, cross_category blocks, baselines and the other factors read identical to round 1.

### policy_conflict_scan (r2)
Unchanged in substance from round 1 (§ policy_conflict_scan above): variant partition, triggers, terminal states and cross-category boundaries are untouched by the edits. Scopes still disjoint and jointly complete.

### rule_compute_equivalence (r2)
- Cancellation/booking selection: rule now names "the most recently recorded cancellation on the pass [club] with a fee remedy" and "the booking that cancellation names"; compute `appt_date`, `notice`, `charged_booking` (and the club's `notice`, `charged_appt_date`) are LATEST by event_date (the date the cancellation is recorded) over fee-remedy cancellations, and `booked_addon` reads the booking whose id is that cancellation's original_event_id. Equivalent both ways, including the multi-cancellation clause. Round-1 constructed reschedule world (`/tmp/e40audit_scripts/r2.py`): rule → deshed booking → 5.71; compute → 5.71 (was 5.10). F1's divergence is gone.
- Rounding: rule now defines half up; compute `RND(x + 0.000001, 2)`. Checked exhaustively in exact rational arithmetic over the reachable domain of all four computes (`/tmp/e40audit_scripts/guard2.py`, `guard3.py`: every non-club variant × size × discount × used visits × valuation tier × expiry share × redo count × admin tier × fee-share parity for the refund; every base fee × add-on × slot × notice hour × repeat × relief for the pass fee; every club size × notice hour × courtesy shares × clinic tier for the club charge; every billed-month count × billing multiplier × relief step × charge-share parity for the settlement): no exact value lies within 0.000001 below a half cent except exact ties, so the guard yields exactly half-up everywhere reachable. All round-1 tie cases now resolve upward (115.665 → 115.67, 118.165 → 118.17, 143.155 → 143.16, 109.955 → 109.96). Equivalent.
- Redo: rule "redone visit at the per-visit paid rate times the redo share" with shares 1 / 0.5 / 0 ↔ `redo_count * paid_rate * redo_share`. Same values as round 1 for every redo count (2+ → count × rate; 1 → 0.5 × rate; 0 → 0). Equivalent.
- Every other binding: unchanged and equivalent as in round 1.
- Residual metadata: `inputs.history` of the pass fee still lists the add-on read as "latest addon_code over groom_appointment_book" without the booking-id filter — descriptive metadata only, not evaluated; observation O-I.

### action_binding_and_uuids (r2)
Carried forward (tool module unchanged; the four `(target_tool, computes)` claims unchanged).

### prerequisite_graph / prerequisite_sentences (r2)
Both `prerequisite` blocks are textually unchanged; the policy_source sentences are still verbatim in their rules; the new selection sentences in the depended-on rules state which cancellation a fee is worked out from and add no cross-problem order and no second wording of the prerequisite. Round-1 conclusions carry forward.

### override_declarations (r2)
The added sentences govern quantities already covered by the declared overwrites (the computed fee / charge; rounding of the declared replacement amounts; the club's closing date, which restates base "a cancellation takes effect per club_cancel_effective"). No new conflict with any base sentence: "A fee or forfeit is never charged twice for the same booking" is untouched (each fee still attaches to its own booking). No undeclared override.

### factor_ladders (r2)
- Counts unchanged: 6 (5p/1m), 5 (4p/1m), 4 (3p/1m), 6 (5p/1m).
- `redo_credit` is now an honest `parameter` (tiers select a share 1 / 0.5 / 0; the per-visit formula is the same in every tier) — distinct values, fall-through 0 = baseline.
- `clinic_relief` / `club_clinic_relief` `cross_difficulty: null`. Cross-difficulty factors remaining: plus_relief (member), autoship_admin_fee (autoship), etf_plus_relief (member), shopper_relief (order) — task 0 still has two, task 1 two. Multi-source factors unchanged (clinic reliefs, shopper relief).
- All other ladders unchanged.

### round-1 item closure (charter items)
| item | round-1 class | r2 status | evidence |
|---|---|---|---|
| F1 | SOURCE-POLICY RED (latent) | CLOSED | rule now states the selection the compute implements; reschedule world: rule 5.71 = compute 5.71 |
| F2 | SOURCE-POLICY RED | CLOSED | half up defined in every rule; guard exact over the reachable domain (exhaustive rational check) |
| O-R | observation (became F2) | CLOSED with F2 | — |
| O-V | observation | CLOSED | both clinic factors `cross_difficulty: null` |
| O-L | observation | CLOSED | `redo_credit` decides `redo_share`, a parameter |
| O-C | observation | CLOSED | rule now "closing on its expires_on, the last day of the current billing month", matching the tool's `closed_on = expires_on` |
| O-T | observation | OPEN (unchanged; tool module identical) | both charge tools still write `groom_late_cancel_fee` |
| O-B | observation | OPEN (unchanged) | redo credit still raises the refund |

### new observations (r2)
- O-M: the multi-cancellation clause ("where more than one such cancellation lacks its entry, each of those fees is still worked out from that most recently recorded cancellation and the booking it names") is now policy text: a fee for one booking is priced from another cancellation's notice, appointment date and add-on. Internally consistent and equivalent to the compute, but not a treatment a salon would publish; it is inert on both task worlds (each holds exactly one fee-remedy cancellation), so no consequence can be demonstrated against a task — observation. The phrase "most recently recorded" also leaves two fee-remedy cancellations recorded on the same date unordered (the compute takes the first stored); inert on both worlds.
- O-G: `half_up_guard: 0.000001` is a numeric implementation constant placed among each policy's business `params`; if params are rendered into the KB it would surface as a business figure. No effect on any value.
- O-I: stale `inputs.history` entry for the add-on read (see above).
- O-X: the club rule now asserts that `expires_on` is the last day of the current billing month; base `groom_pass_pricing` sets expires_on from purchase + pass_validity_months and no base club rule says expires_on rolls with billing. On task 1's world the assertion holds (expires_on 2026-10-08 = next_billing_date − 1), so no consequence.

### post_reveal_r2 (written after opening the round-2 task files)
- Task files: 0.json ad2d50d1…, 1.json 37cdb7e0…; worlds and personas identical to round 1; GT write sequences unchanged; all scored values unchanged (5.71, 112.81, 5.86, 7.51); every proof figure equals the r2 recomputation.
- Per-task closure: T0-F1 CLOSED, T0-F2 CLOSED (see `0.md` § revision_2); O0-1, O1-1 open observations (persona unchanged); O1-2 resolved by the O-C change (see `1.md` § revision_2).

### closing_checklist (r2)
- Files: `0.md`, `1.md`, `_difficulty.md`, each with round-1 text untouched and `revision_2` appended.
- Every round-1 RED is closed: F1, F2 (charter), T0-F1, T0-F2 (task 0). Claimed observation fixes verified: O-R, O-V, O-L, O-C closed. Unchanged by design and verified unchanged: O-T, O-B, O0-1, O1-1 (O1-2 resolved via O-C).
- New in r2: observations only — O-M (multi-cancellation pricing convention, inert on both worlds), O-G (`half_up_guard` placed in business params), O-I (stale `inputs.history` metadata for the add-on read), O-X (club rule asserts expires_on is the billing-month end; true on task 1). None demonstrates a consequence against either task's scored solution.
- Coverage and scopes: 4 extended policies covered, scopes disjoint; 4 tools with independent uuid8s (module unchanged).
- Trees: 1 prerequisite, 1 value_input edge, an owner=user write per task; difficulty graph acyclic.
- Factors: 4–6 per computation with ≥ 2 parameter and 1 method; per task ≥ 1 multi-source and ≥ 1 cross-difficulty (task 0: member, autoship; task 1: member, order); all bear weight against honest baselines; baselines ≠ gold.
- Gates: the orchestrator's r2 snapshot is green on all 7 (check_traceability deferred); not re-run by the auditor.
- Source-layer verdict, round 2: task 0 PASS, task 1 PASS; difficulty PASSES the policy-task audit.
