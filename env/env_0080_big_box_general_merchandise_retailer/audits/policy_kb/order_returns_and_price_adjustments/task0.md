# Policy-KB bijection audit — order_returns_and_price_adjustments / task 0

## revision_1

Auditor: fresh KB auditor (brief kb_d4). Source: order.extended.yaml sha256 6aec2c3b…, task_tools.py 351e913f…; docs/order 56 files, tree hash 4246d2268df53b62. Entry conditions (from my own run of kb_snapshot.sh): `DOCS OK`; post-publication `TRACEABILITY OK` (0.json copied 22 missing 0; 1.json copied 15 missing 0); EXTENDED / TASK TOOL CONTRACT / REPLAY / SOLVABILITY / COMPUTE / GROUNDING / SCOPE OK; policy side `VERDICT revision_6: task0=PASS task1=PASS charter=CLEAN`. Inputs complete.

Policies in scope: order_ext_late_change_fee (root), order_ext_missed_appointment_credit, order_ext_replacement_haul_away_credit, order_ext_late_fee_goodwill_refund; base order_fulfilment_and_cancellation, order_evt_fees, order_agg_multi_holding, order_refund_tender; parameter_schema / SLID variant; task-tool contracts of the four tools.

## source_to_kb

### order_ext_late_change_fee
| Source atom | KB home | Judgement |
|---|---|---|
| overwrite 1 superseded clause (fulfilment: "A large-item delivery may be rescheduled before the cutoff …") | fulfilment_pickup_and_cancellation_rules "Large-item reschedules" — quoted and "no longer in force" | retired surface correct |
| overwrite 1 replaced_by ("may be rescheduled … down to the scheduled day itself … this sentence covers reschedules only …") | large_item_appointment_changes ¶2 verbatim | equal |
| overwrite 2 superseded clause (order_evt_fees: "… canceled or rescheduled within cancel_cutoff_hours …") | order_fee_rules "Retired clauses" bullet 1 | retired surface correct |
| overwrite 2 replaced_by ("For a customer's reschedule … still carries the program's late cancellation fee") | large_item_appointment_changes ¶3 verbatim | equal |
| booking: new date, count +1, fee type late_cancellation, waiver none; no-fee reschedule books no row | hub "What a reschedule records" ("a fee of the late cancellation type with no waiver source"; "books no fee row") | equal |
| tender sentence, handoff "as POLICY_NOT_COVERED" | hub "Tender" ("handed over with the reason policy not covered") | equal at entailment — the transfer tool's enum has exactly POLICY_NOT_COVERED / CUSTOMER_REQUESTED and its description ("when no Northgate policy allows the request to be resolved in this conversation") maps the business words uniquely. Renderer departure 1 judged acceptable. |
| customer's own decision, recorded and confirmed | hub "What a reschedule records" | equal |
| free-reschedule test; "already on the order … before this request" | late_change_fee_computation §1 + table | equal |
| day count convention | computation §2 | equal |
| **baseline.rule** "The standard late-change notice charge is the program's late cancellation fee, and the standard late-change fee is that notice charge, rounded half up to the cent." | computation §3: "The late-change notice charge is the program's late cancellation fee, and the late-change fee is that notice charge, rounded half up to the cent." | **changed** — see bijection_verdict B1 |
| result (adds every charge/surcharge, takes off every courtesy reduction, RND half up, ≥ 0) | computation §3 second sentence | equal (the source's "the schedules below … standing in place of its standard value" pointer is rightly not rendered in the computation document) |
| factor notice_charge_step (scheduled day → delivery fee standing; ≥2 days → none; otherwise LCF) | short_notice_delivery_change_charge (3 tiers, "less refunds of it") | all tiers equal |
| factor earlier_fee_surcharge (≥ LCF 20; >0 <LCF 10; else 0) | repeat_late_change_surcharge (49.00 stated; boundaries 48.99/0.01/0.00) | all tiers equal |
| factor crew_charge_step (standing & scheduled day → standing; standing & earlier → fee for one item; else none) | haul_away_crew_rebooking_charge (25.00 stated) | all tiers equal |
| factor installation_surcharge (≥2 → 20; 1 → 10; else 0) | appliance_installation_rebooking_surcharge | all tiers equal |
| factor own_requests_surcharge (≥2 above free → 15; exactly 1 → 5; else 0) | repeated_reschedule_request_surcharge (free = 2 stated) | all tiers equal |
| factor northgate_move_courtesy (≥2 → 30; 1 → 15; else 0) with moves = count − confirmed requests | northgate_moved_appointment_courtesy | all tiers equal |
| product figures: late_cancel_fee 49.00, haul_away_fee 25.00, free reschedules 2 | fulfilment_fee_schedule, pickup_hold_and_order_changes_table, and restated in the factor documents | named and findable |
| **prerequisite 1** (state) "… the late-change fee is fixed only after the records carry the missed-appointment credit owed on a large-item delivery fee charged above zero for an order on which Northgate itself moved an appointment." | hub "When the late-change fee is fixed" bullet 1, verbatim; in no other document (grep over docs/*) | form, connective ("fixed only after") and strength intact. Resolution basis: missed_delivery_appointment_credit entitlement ("is owed a missed-appointment credit on that fee, booked as one refund of that fee with reason fee refund") + records (fee 49.00, count 5 vs 3 confirmed requests, no refund row). |
| **prerequisite 2** (state) "… is not fixed until the records carry the replacement haul-away credit owed …" | hub bullet 2, verbatim; nowhere else | intact. Basis: replacement_haul_away_credit entitlement + plan_settle_claim 2026-10-06 reimbursement, major_appliances; haul-away 50.00, no refund. |
| **prerequisite 3** (state) "… before the late-change fee is fixed, the records must carry the late-change goodwill refund owed on the latest late-change fee row …" | hub bullet 3, verbatim; nowhere else | intact. Basis: late_change_fee_goodwill_refund entitlement + 79.00 row 2026-10-19, moves 2, no refund. |
| `condition` / `resolved_by` / `effect` | nowhere | correct (authoring fields) |
| tool contract (order_id, new_scheduled_date YYYY-MM-DD, fee ≥ 0 2 dp; refusal on tender; returns) | hub invocation block | equal to task_tools.py and runtime schema |

### order_ext_missed_appointment_credit
Overwrites: order_evt_fees "A fee is refunded only as stated …" → order_fee_rules retired bullet 2; replaced_by → missed_delivery_appointment_credit "Fee refunds on such an order" sentence 1, verbatim. Fulfilment "The fulfilment fee is refunded …" → fulfilment doc "Fulfilment fee" retired; replaced_by → same hub paragraph, sentence 2, verbatim. Entitlement, definition of a Northgate move, tender → hub. baseline.rule "The standard missed-appointment credit is one fifth …" → missed_appointment_credit_amount "Clause", complete with "standard". Assembly and cap → same doc. Factors, every tier: northgate_moves_extra (40/20/0) → repeated_northgate_moves_extra; waiting_extra (≥14 → 10, 7–13 → 5, else 0; "scheduled date the order carries when the credit is worked out") → delivery_wait_length_extra; haul_crew_extra (5/2/0, before benefits ÷ 25.00) → haul_away_items_credit_extra; order_value_extra (≥2000 → 5, 1000–<2000 → 2, else 0) → order_value_credit_extra; own_requests_extra (≤2 → 10, 3 → 5, ≥4 → 0) → reschedule_allowance_credit_extra; appliance_flat_amount (5.00 × units / 7.50 / 0) → major_appliance_missed_delivery_amount. Tool contract → hub invocation. PASS.

### order_ext_replacement_haul_away_credit
Overwrite → fee rules retired bullet 2; replaced_by → replacement_haul_away_credit "Fee refunds on such an order", verbatim. Entitlement, tender → hub. Settlement read with tie rule, owed-nothing cases, day count → replacement_haul_away_credit_amount §1–2. baseline.rule "The standard replacement haul-away credit is one quarter …" → §3, complete. Assembly (credited haul-away × percentage, cap at standing) → §3. Factors: settlement_timing_extra (0–30 → 40, 31–60 → 20, else 0) → settlement_recency_haul_away_extra; replaced_item_kind_extra (major appliance 20, furniture/fitness 10, else 0) → replaced_item_kind_haul_away_extra; settled_value_extra (≥1000 → 10, 500–<1000 → 5, else 0) → settled_claim_value_haul_away_extra; credited_haul_basis (≥2 & ≥2 → fee × lesser count; exactly 1 & ≥2 → one item fee; otherwise the haul-away charge) → credited_haul_away_for_same_day_settlements. Every plan-side factor names "Northgate Protect Protection Plans (administered by Keystone Protection Services)" and the record kinds read (most recent claim settlement, its date, covered item category, settlement amount). PASS.

### order_ext_late_fee_goodwill_refund
Overwrite → fee rules retired bullet 2; replaced_by → late_change_fee_goodwill_refund "Fee refunds on such an order", verbatim. Entitlement, tender → hub. Which-fee rule, baseline.rule "The standard late-change goodwill refund is one quarter …" (complete), assembly and cap → late_change_goodwill_refund_amount. Northgate-move count → goodwill_share_for_northgate_moves (and missed-appointment hub definition). Factors: goodwill_moves_extra (50/25/0) → goodwill_share_for_northgate_moves; fee_recency_extra (≤7 → 25, 8–30 → 10, else 0) → recent_late_change_fee_goodwill_extra; goodwill_crew_extra (10/5/0) → haul_away_crew_goodwill_extra; installation_standby_amount (2.50 × units / 4.00 / 0) → installation_crew_standby_amount. PASS.

### Base policies governing the subjects
order_fulfilment_and_cancellation → fulfilment_pickup_and_cancellation_rules (holds, cancellation, placed-only with system-record authority, missing/damaged, returned status; two retired clauses marked) + pickup_hold_and_order_changes_table (per-program figures). order_evt_fees → order_fee_rules (charging, waiver tie order, subtotal definition, haul-away per item, delivery conditions, two retired clauses) + fulfilment_fee_schedule. order_agg_multi_holding → orders_held_side_by_side. order_refund_tender → refund_tender_order_of_restoration. All in-force clauses carried as in force; nothing retired that the source did not retire.

## kb_to_source

Sentence-by-sentence scan of the 56 order documents for normative claims without a source: none found. Derived restatements checked and admitted: the system-record authority sentences ("read from the order's status in the system record … not from the customer's account") come from the eligibility evidence_contract authority; the cancellation status table is the cancel_allowed_statuses list; the "Points of judgement" / hypothetical rows are arithmetic or boundary consequences of the stated rules; "Input | Read from" table of the missed-appointment amount doc restates compute_basis. No confirmation, review, notification or step added.

Prerequisite-side specific checks: (1) cross-problem operational guidance — none (no "first call …", no tool of another problem in any blocked-side document; each tool name appears exactly once, in its own invocation block). (2) A task's opening world written as policy fact — none (no document states this customer's reschedule count, settlement, fee or refund state; worked figures are hypothetical and none equals a scored value: 41.85, 22.50, 72.15, 39.65 appear in no document or schema).

Renderer departure 2 (stale base descriptions kept verbatim): pickup_hold_and_order_changes_table "Cutoff hours: hours before the scheduled delivery date before which a large-item order can be canceled or rescheduled without a fee" and "Free reschedules: the number of delivery reschedules made before the cutoff that carry no fee" are the verbatim parameter_schema descriptions of cancel_cutoff_hours_before_scheduled and large_item_reschedules_free. The KB is right to carry base text as written and may not retire it on its own; **no KB defect**. Its substance is a source-layer note — see `src` below.

## bijection_verdict

**KB-BIJECTION RED** — one item.

- **B1 (kb=late_change_baseline_qualifier)** — symptom: the baseline rule of order_ext_late_change_fee is not carried complete; the default became an unconditional statement. Root cause: both occurrences of "standard" in baseline.rule were dropped. Evidence: source `baseline.rule` / rule text "The standard late-change notice charge is the program's late cancellation fee, and the standard late-change fee is that notice charge, rounded half up to the cent." vs docs/order/late_change_fee_computation_642f339e.json §3 "The late-change notice charge is the program's late cancellation fee, and the late-change fee is that notice charge, rounded half up to the cent. The late-change fee is the total of the late-change notice charge and every other late-change charge and surcharge on the reschedule, less every late-change courtesy reduction on it". As rendered, the same paragraph gives the late-change fee two definitions ("is that notice charge" / "is the total of …"), and the notice charge is stated without qualification as the late cancellation fee while short_notice_delivery_change_charge sets it to the standing delivery fee on the scheduled day and to nothing two or more days ahead. The source's default, which yields to a schedule, now reads at a stronger strength. The other five computation documents keep "standard" in their baseline sentence ("the standard missed-appointment credit is one fifth", "the standard replacement haul-away credit is one quarter", "the standard late-change goodwill refund is one quarter", "the standard late-express credit is half", "the standard changed-mind refund … less a standard restocking fee"). Affected: docs/order/late_change_fee_computation_642f339e.json, "**3. Amount.**", first sentence. Effect in this task: none on the numbers — the blind audit applied the short-notice tier and reached 39.65 — so this is not a KB-RUNTIME RED; it is a strength change on the visible surface.
- Observation, not RED: the assembly sentences of several computation documents write the default as an apposition ("The credited haul-away, which is the haul-away charge on the order", "the late-express lateness rate of one half") where the source adds "or the amount/rate a schedule below sets in its place". Dropping that pointer is what the discrete topology requires of a computation document, and every factor document says the schedule "sets" its value, so I do not count these as changed meaning.

Previous revisions: none (first KB audit of this difficulty).

## dependency_form

- Prerequisite sentences: the three state-form sentences stand verbatim in the blocked hub (large_item_appointment_changes, "When the late-change fee is fixed"), in no other document; none is restated in action form, none names a tool, performer or document. Listing the three as bullets under a heading is how the source sets them out, all on the blocked side. That is the source's own form and not an aggregated chain.
- Tool names: each of the six tools appears only in its own invocation block.
- No route, ordered step list, dependency table, roadmap, wrong-vs-right contrast or FAQ walking across problems in any order document. The "Fee refunds on such an order" sentences are the overwrites' replaced_by text; they name other fees only to fence the scope and state no dependency.
- Titles and openings name general subjects ("Scheduled Large-Item Delivery Appointment Changes", "Missed-Appointment Credit on Northgate Scheduled Large-Item Delivery", "Replacement Haul-Away Credit for Northgate Protect Settlements", "Late-Change Goodwill Refund — …", factor titles by schedule subject). None mirrors this task's situation.
- Findability: the depended-on hubs are reached through the sentences' own nouns (missed-appointment credit, replacement haul-away credit, late-change goodwill refund) and through record words (fee types large_item_delivery / haul_away / late_cancellation; plan_settle_claim). No phrasing has to be borrowed from the blocked document.
- Factor documents: none says which tier a customer falls on, none names or points at the computation document or at another factor, none writes this task's rows in as fact. The computation documents carry no "unless otherwise provided", exception list or pointer; their generic assembly words ("every other late-change charge and surcharge", "every extra percentage on the order") are the source's result sentence.
- Verdict: **PASS** (no KB-EXPLICIT RED). Blind-audit hop marks: H1, H2, H3 all state-derived.

## src (policy-side notes, do not change this skill's verdict)

- **src=schema_cutoff_free_desc** — the base parameter_schema still describes `cancel_cutoff_hours_before_scheduled` as "Hours before the scheduled delivery date before which a large-item order can be canceled or rescheduled without a fee" and `large_item_reschedules_free` as "Number of delivery reschedules made before the cutoff that carry no fee". Meanwhile order_ext_late_change_fee's in-force rule (its replaced_by, and the free-reschedule test) says free reschedules are those "made two or more days ahead" and that "every other reschedule carries the late-change fee". The overwrites retired the two rule clauses, but these descriptions are still in force and conflict on untriggered branches: (a) a reschedule requested before the 48-hour cutoff once the confirmed requests have reached the 2 free reschedules — "without a fee" per the description, the late-change fee per the rule; (b) a request two calendar days ahead but less than 48 hours before the scheduled date — free per the rule, not "before the cutoff" per the description. Its nature: an undeclared conflict between an extended rule and in-force base vocabulary, which the KB carries faithfully (pickup_hold_and_order_changes_table, "Meaning of each column, as published"). This task is not affected: the request falls on the scheduled day and 3 requests ≥ 2 free.

## revision_2

Gate snapshot (kb_snapshot.sh, executed only, 2026-10-25T00:08:38Z): `DOCS OK`; `TRACEABILITY OK` (0.json 22/0 True, 1.json 15/0 True); EXTENDED / TASK TOOL CONTRACT / REPLAY / SOLVABILITY / COMPUTE / GROUNDING / SCOPE OK; source hashes unchanged (6aec2c3b…, 351e913f…); docs/order tree hash 7f236facbf67bf41. RENDER.log tail: `RENDER round 2: DOCS OK`.

### source_to_kb (delta)
- **B1 closed.** late_change_fee_computation_642f339e §3 now carries baseline.rule verbatim: "The standard late-change notice charge is the program's late cancellation fee, and the standard late-change fee is that notice charge, rounded half up to the cent." The result sentence that follows is unchanged. The rest of the document is identical to round 1: §1, §2, the free-reschedule table and the worked figure.
- **Renderer addition** to pickup_hold_and_order_changes_table, "Rule in force for Northgate Scheduled Large-Item Delivery reschedules and cancellations". Each sentence against the source:
  1. "A Scheduled Large-Item Delivery appointment may be rescheduled by the customer at any time down to the scheduled day itself, whatever tender paid the order: the program's free reschedules made two or more days ahead carry no fee, and every other reschedule carries the late-change fee." This is the late_change_fee overwrite-1 replaced_by, minus "this rule sets" and the tail "; this sentence covers reschedules only, and a cancellation stays under the cancellation rules." Dropping the tail changes nothing here, because the paragraph's third sentence states the cancellation case separately. The full sentence, fence included, remains in the hub.
  2. "A reschedule requested two or more calendar days ahead … is a free reschedule and carries no late-change fee; every other reschedule carries the late-change fee." This is the rule's free-reschedule sentence, verbatim.
  3. "A large-item order canceled within the cutoff hours of its scheduled date, beyond the free reschedules, still carries the program's late cancellation fee." This is the tail of the overwrite-2 replaced_by, verbatim.
  The paragraph adds no condition, figure, step or exception. It contains no prerequisite sentence and names no tool, other problem or route. The verbatim base column descriptions stay as published and are not marked retired, so the KB does not legislate. Exact and additive-free: **PASS**.

### kb_to_source (delta)
- No new normative claim without a source. No changed document contains a scored value.
- Observation, not RED: the new paragraph was inserted between the "Free reschedules" and "Report days" bullets. "Report days: …" now sits under the "Rule in force" paragraph, cut off from the "Meaning of each column, as published" list. Its wording is generic ("calendar days after fulfilment …") and the per-program figures stay in the table, so its meaning does not change. It is a layout slip only.

### bijection_verdict
**PASS.** B1 is closed; nothing new and no regression (54 documents unchanged).

### dependency_form
**PASS.** The changed documents carry no prerequisite sentence, no tool name, route or chain. The prerequisite sentences stand as in revision_1, verbatim in the blocked hubs only.

### src
- src=schema_cutoff_free_desc: unchanged in substance. The coordinator has logged it as BLUEPRINT-KNOWN (a frozen base parameter description that no task reaches).

## revision_3

Cross-product re-judge (coordinator round 3). Gate snapshot (kb_snapshot.sh, executed only, 2026-10-25T04:51:56Z): `DOCS OK`; `TRACEABILITY OK` (0.json 22/0 True, 1.json 15/0 True); 7/7 instantiate gates OK; source hashes unchanged (6aec2c3b…, 351e913f…); docs/order tree hash 7f236facbf67bf41, unchanged since revision_2. Published corpora read: docs/plan (62), docs/membership (73), docs/gift (19), docs/market (63), docs/card (53).

### (1) Conditional readings, resolved
- Plan-side reads: the owed test (the "replaced or reimbursed" settlement, 0–90 days, a category the order carries) and the factors (kind, settled value, timing, credited haul-away). They use the published plan vocabulary: plan_settle_claim with settlement_method repair / replacement / reimbursement_egift_card, the covered item category and the settlement amount. No contradiction between docs/order and docs/plan.
- Card: the order documents' Northgate Card readings (§3 window extension, cardholder discount, card free-shipping benefit) are not engaged; the customer has no card account (find_card_holdings: none). Membership: none held, and membership benefits never apply to Scheduled Large-Item Delivery, both in docs/order (fee schedule) and in docs/membership ("delivery benefits never apply to scheduled large-item delivery"). Consistent.
- Nothing is conditional any more. **KB side: CLEAN** (no cross-product KB defect).

### (2) Re-pricing of every other-product row seeded in this world (as of each row's date, under the published rules of its product)
Rows (find_plan_holdings / find_plan_events, plan 54d266b0…; Standard 3-Year on the 2024 order line 4d97c8a1… Frostline refrigerator, net 849.99 (selling 899.99 less promo 50.00), fulfilled 2024-03-22, 12-month manufacturer warranty):

| Row | Seeded | Published rule gives | Verdict |
|---|---|---|---|
| plan_charge 2024-03-15, one_time_price | 109.00, external card | "Northgate Protect Plan Price Schedule": band $750.00–$999.99, Standard 3-Year $109.00; bought on the order date, inside the 30-day window ("Terms of Purchase" §2) | producible |
| plan holding dates | coverage 2024-03-22 → 2027-03-22 | "Coverage Start, Term and Expiry": fulfilment date + 36 months | producible |
| plan_register_item 2024-03-22 | amount 0.00 | "Covered Item Registration …": a single-item plan's item "is registered on the plan with its registered limit of liability"; the tool refuses a non-positive amount ("Error: amount_usd must be a positive amount"). Registered limit = starting price 899.99 ("Valuation Standard: … Promoted …": a line with an item promotion starts from the selling price per unit before promotions) + 49.00 ("Delivery Charges Counted …": Scheduled Large-Item Delivery, large-item delivery 49.00 + haul-away 0.00, whole share ÷ 1 merchandise line) + accessory 0 + competitor match 0 = **948.99** | **not producible** (src=t0_plan_registration) |
| plan_file_claim 2025-06-17, decide 2025-06-18 approved, fee 0.00 | — | filed inside 30 days of the 2025-06-15 incident; decided within 3 business days; incident after the warranty end 2025-03-22; Standard 3-Year fee band $0.00 ("Service Fee Bands"); the decision rule (earlier approvals settled) is met | producible |
| plan_settle_claim 2025-06-20, repair | **186.40** | "Keystone Settlement Authority Schedule": mechanical failure flat charge 199.00 → in-home item "the greater of the flat repair charge … and the in-home minimum charge of $249.00" ("Repair Charge for Portable Devices and In-Home Items") = 249.00; + service-call in-home trip 65.00; + item-age allowance 30.00 (450 days from coverage start 2024-03-22 to incident 2025-06-15, the 270–729 tier); + parts allowance 0 (registered limit < 1000.00); + inspection 0 (plan bought before fulfilment); + label 0 (in-home) = **344.00**; capped at the remaining share; 344.00 ≤ 80% × 849.99 = 679.99 and no earlier repairs → repair at 344.00. Under the seeded 0.00 registration the remaining share would be 0.00, so 186.40 is not reachable on either reading | **not producible** (src=t0_plan_settlement_rows) |
| plan_file_claim 2026-10-01, decide 2026-10-02 approved, fee 0.00 | — | inside the term and the filing window; fee band $0.00; the 2025 approval carries a settlement | producible |
| plan_settle_claim 2026-10-06, **reimbursement_egift_card 663.59** | method and amount | Same schedule: 249.00 + 65.00 + 60.00 (921 days, the 730+ tier) + 0 + 0 + 0 = **374.00** ≤ 679.99, and the earlier same-type repairs (1) have not reached the repair count 3 → §5 "otherwise it is settled by repair at the authorized repair value". A reimbursement is reachable only where the claim is settled by replacement and no like item is available ("Settlement of Approved Northgate Protect Claims"), and the published rules never settle this claim by replacement. Its amount, "net price minus all earlier settlements" = 849.99 − 186.40 = 663.59, also rests on the non-producible 186.40 (it would be 505.99 after a 344.00 repair) | **not producible; gold-bearing** (src=t0_plan_settlement_rows) |
| plan holding status fulfilled, closed 2026-10-06, liability_remaining 0.00 | — | follows only from the non-producible reimbursement and the 0.00 registration; under the published rules the plan stays active with remaining limit 948.99 − 344.00 − 374.00 = 230.99 | **not producible** (consequential) |
| gift: Northgate eGift Card of 663.59 on 2026-10-06 | absent (find_gift_holdings: none) | "a Northgate eGift Card for a protection plan claim reimbursement, at the exact … reimbursement amount" | accepted residue (unread row; gold does not read gift) |

Why the gold depends on these rows: the 2026-10-06 row is the settlement read by order_ext_replacement_haul_away_credit. Its method decides the owed test ("A settlement by repair … owe[s] no replacement haul-away credit") and therefore prerequisite edge H2. Its date, category and amount set the timing (40%), kind (20%) and value (5%) tiers and the credited-haul-away count. Under the published plan rules this settlement is a repair, so the haul-away credit is owed nothing. Edge H2 would then not engage, the crew charge would read the full 50.00 haul-away, and the scored late-change fee would move. The 22.50 credit itself would not be owed. The 2025 repair amount does not touch a scored read here (only the latest settlement is read), but it sets the reimbursement amount 663.59.

### (3) Owed-at-once writes of other products that could move a scored read
- Plan: no claim is pending, the plan is fulfilled, and no food-loss claim exists. No published plan rule makes a settlement or cancellation refund owed at once. The only other plan write a solver might take as owed is the registration (the seeded row is 0.00). It would book a plan_register_item row, and the order reads filter plan_settle_claim, so no scored read moves.
- Gift: issuing the missing eGift card would write gift rows, which no order computation reads.
- Membership and card: none held.
- Verdict: none moves a scored read.

### bijection_verdict / dependency_form (revision_3)
**PASS / PASS.** No KB defect; the docs are unchanged since revision_2.

### src
- src=schema_cutoff_free_desc: BLUEPRINT-KNOWN (unchanged).
- **src=t0_plan_settlement_rows**: the 2026-10-06 plan_settle_claim (reimbursement_egift_card, 663.59) and the 2025-06-20 repair (186.40) are not what the published plan rules produce (repair at 374.00, repair at 344.00). The 2026 row is gold-bearing for this task: it is the settlement read by H2's owed test and by the three plan-side haul-away factors.
- **src=t0_plan_registration**: the plan_register_item row at 0.00 and the holding's liability_remaining 0.00 are not producible. The published registration carries the registered limit 948.99, and the published rules leave the remaining limit at 230.99 with the plan active.

## revision_4

KB confirm after a seed-only round. kb_snapshot.sh (executed only): DOCS OK; TRACEABILITY OK (0.json 22/0, 1.json 15/0); 7/7 instantiate gates OK; source hashes unchanged (6aec2c3b…, 351e913f…); docs/order tree hash 7f236facbf67bf41, unchanged. Charter, tools and docs are unchanged, so bijection and dependency_form are unchanged: **PASS / PASS**.

### Changed rows re-priced against the published docs (as of each row's date)
| Row | Seeded | Published rule | Verdict |
|---|---|---|---|
| order 9b7fd990… line 1 (2024-03-15) | 1799.99 = 1899.99 − 100.00 promo; delivery 49.00; amount paid 1848.99 | order line pricing and fee schedule (Scheduled Large-Item Delivery 49.00) | producible |
| plan_charge 2024-03-15 | 199.00 | "Plan Price Schedule": $1,500.00–$1,999.99 band, Standard 3-Year $199.00 | producible |
| plan_register_item 2024-03-22 | 1948.99 | "Valuation Standard" (promoted line → selling price 1899.99) + "Delivery Charges Counted" (49.00 ÷ 1 line) + accessory 0 + competitor match 0 | producible (closes t0_plan_registration) |
| repair 2025-04-25 (incident 2025-04-20, filed 04-22, approved 04-23) | 374.00 | in-home 249.00 + trip 65.00 + age 30.00 (394 days) + parts 30.00 (registered 1948.99, in the 1000–<2000 band) + inspection 0 (plan bought before fulfilment) + label 0; ≤ remaining share 1948.99; ≤ 80% × 1799.99 = 1439.99; outside the warranty (ended 2025-03-22); not authorized on the approval day | producible |
| repair 2025-11-14 (incident 11-10, filed 11-11, approved 11-12) | 374.00 | same terms, age 30.00 (598 days); 1 earlier repair < 3 | producible |
| repair 2026-05-18 (incident 05-12, filed 05-13, approved 05-14) | 404.00 | 249.00 + 65.00 + 60.00 (781 days) + 30.00; 2 earlier repairs < 3 | producible |
| settlement 2026-10-06 (incident 09-29, filed 10-01, approved 10-02) | reimbursement_egift_card 647.99 | Authority Schedule §5: same-type repairs already booked (3) have reached the repair count of 3 → settled by replacement whatever the value. With no like item available it is reimbursed on a Northgate eGift Card at "net price minus all earlier settlements" = 1799.99 − 1152.00 = 647.99 ("Settlement Terms") | producible (closes t0_plan_settlement_rows) |
| plan holding | fulfilled, closed 2026-10-06, liability remaining 149.00 | a reimbursement ends the single-item plan; 1948.99 − 1152.00 − 647.99 = 149.00 | producible |
| decisions | approved, service fee 0.00 | Standard 3-Year fee band $0.00; each earlier approval settled before the next decision | producible |
| gift eGift card 647.99 | absent | — | accepted residue (unread) |

- The reason "that model was discontinued" (no like item) is not record-visible, but the published rule leaves it to the administrator and only the reimbursement it produces is recorded. This is acceptable.
- (3) Owed-at-once writes: no change from revision_3. The plan is fulfilled and no claim is pending.
- src: t0_plan_registration **closed**; t0_plan_settlement_rows **closed**; schema_cutoff_free_desc BLUEPRINT-KNOWN, unchanged.
