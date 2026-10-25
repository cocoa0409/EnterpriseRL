# worklog — lab_orders_and_collection_fees (env_0081), M=2

## Step 0 — draw (draw_counts.py --tasks 2)
```
{"task": 0, "prerequisite_problems": 1, "problems": 2, "factor_counts": [4, 6]}
{"task": 1, "prerequisite_problems": 1, "problems": 2, "factor_counts": [6, 5]}
```

## Step 0 — difficulty pre-check (blueprint read: lab.yaml, db_schema, share_tools, membership/visit/sponsor rules)
- Writable lab state: lab_orders (collection_method, payment_path + membership_id/enrollment_id/coverage_id,
  requisition_expiry_date + reissue_count, status/cancelled_date) and lab_charges (lab_panel_charged,
  lab_collection_fee_charged, lab_charge_refunded). Only lab_ordered carries a trigger (lab:lab_panel_charged).
- BLUEPRINT-KNOWN gaps found (base frozen, routed inside my policies):
  1. refund_reason has no value for a collection-method change, although lab_evt_collection_fees refunds the old
     method's fee on a change.
  2. lab_evt_panel_pricing prices member_rate "for the patient's tier on the ordered_date" while a path change charges
     "on the change date"; the base does not say which date's tier prices a line posted on a path change.
- DSL limits that shape the design: no subscripts (tier/plan mappings cannot be indexed, so prices used by a rule are
  restated as this policy's params), no date arithmetic (scored values are amounts), history primitives are scoped
  to this order's own lab_charges (other lab orders of the patient cannot be counted, so the included-per-year and
  plan-year allowances are not computable here), cross reads are first-match with equality filters.
- Thin-charter finding: a single lab line has at most 1-3 base-grounded pricing dimensions (panel price by tier and
  status; collection fee by method; the path; waivers that zero the line). The draw needs 4-6 load-bearing factors per
  computation, so every computation also carries Larkspur-published schedule items in the realism bar's accepted
  shapes (R1 keyed schedules on recorded keys: shipping speed, patient location state, collection method; R2 one
  timing schedule per date dimension; R5 caps). The only realistic cross-difficulty lever on lab money is the
  membership (tier and status decide the member price, Premier waives kit/mobile fees), so each task carries one
  panel-price computation reading the membership.

## Design decisions (running)
- D1 (task 0 tree): root = the patient's own switch of an uncollected order from a patient service center draw to
  an at-home kit (owner=user, owner_ruling (a) "choosing the collection method"); prerequisite = the agent's
  correction of an order that was placed on a Larkspur at Work plan whose enrollment was not yet active on the ordered
  date (base: "The sponsor_plan path may be used only while the patient's Larkspur at Work enrollment status is active
  or on_leave"), re-pricing it on the path that applied (member_rate) and posting its panel charge. value_input edge:
  the kit charge depends on the order's payment path (a kit on a kit-waived plan's sponsor path carries no fee).
- D2 (retracted D1): the sponsor-pending story fails — a pending registration closes after 30 days
  (pending_registration_expiry_days), so the order would be fresh and every requisition-timing lever would sit on its
  fall-through; sponsor seeding (eligibility files, contributions) also adds unread rows.
- D3 design constraints learned:
  * billing-error corrections price "charged minus correct"; any adjustment common to both cancels, so a correction
    carries one load-bearing lever (the mispriced dimension) -> never use a correction as a 4-6 factor computation.
  * value links available inside lab: (a) a line's standing amount (refund -> later settlement that credits it),
    (b) the order's payment path (draw fee applicability, sponsor kit/mobile waiver), (c) the order's membership link,
    (d) requisition_expiry_date (reissue; but a reissue carries no amount).
  * the only realistic cross-difficulty lever is the membership's tier/status pricing the panel -> each task carries
    a NEW panel charge (not a correction) priced at the member price.
- D4 (task 0, FINAL): Premier Annual member; STI Screening Panel ordered at a patient service center while her
  membership was past_due (a declined dues retry, recovered later); the order was posted on self_pay at the list
  price with no membership linked (billing error: base "A membership benefit or member price may be used only while
  the patient's membership status is trialing, active or past_due", past_due qualifies). Root (owner=user): she
  switches the order to an at-home kit (privacy); the kit line is priced through the membership the order records
  (Premier kit-fee waiver, Larkspur Pharmacy shipping speeds with the Premier expedited benefit - figures reused from
  the rx charter's shipping schedule). Prerequisite (agent): the member-price correction that re-links the order to
  her membership, moves it to member_rate and refunds the panel overcharge (billing_error). value_input edge: the
  order's membership link feeds the kit line's waiver and shipping benefit. Old-method fee on a switch: credited
  against the new line (route around the missing refund reason, BLUEPRINT-KNOWN gap 1).
  Factor plan: correction (4) = member tier price [cross-diff, multi-source], earlier-refund reconciliation
  [method], specimen handling by specimen type [R1], collection route adjustment [R1]; kit switch (6) = outbound
  speed x Premier [cross-diff, multi-source], return label by specimen stability x days left, prior collection
  credit [method], credit window [R2 charge date], prior kit shipments on the order [R1 count], switch timing by
  days since ordering [R2 ordered date]. Several are Larkspur-published schedule items forced by the thin charter
  (see thin-charter finding); each is R1/R2 shaped on a recorded key.

## Task 0 — closed (per-task gates)
- Policies: lab_ext_member_rate_correction (agent, 4 factors, tool correct_member_rate_order_9be954a8) <- prerequisite of
  lab_ext_home_kit_switch_charge (owner=user, 6 factors, tool switch_order_to_home_kit_d2ed4950); frozen_time
  2026-11-07 10:20:00 EST (Saturday). Gold: refund_amount 36.00 (step 8), kit_charge 35.98 (step 10).
- Gate fixes: tuple literals rejected by the DSL (rewritten as == chains); prerequisite sentence carried code tokens
  (reworded "posted at the list price ... past due"); fixed-format precision wording; empty FK strings -> null;
  correction subject narrowed to lab_charge_refunded (the in-place path move is part of the billing-error correction,
  its path-change gates would demand enrollment/coverage arguments the correction never uses); one_refund_per_line
  binding source added to the evidence list. Per-task gates: EXTENDED/TOOLS/REPLAY/SOLVABILITY/COMPUTE/GROUNDING/SCOPE OK.

## Task 1 — design (D5)
- Patient Lucas Achterberg (Plus Annual, dedicated clinician), Philadelphia PA; Comprehensive Metabolic Panel ordered
  2026-08-10 at a patient service center on member_rate after a Primary Care Follow-Up Visit; lines priced with the
  extended published price (task 0's overwrite applies to own-category seeds). Recovering from knee surgery he asks
  for a mobile phlebotomist at home (root, owner=user). His requisition expires within the 14-day reissue window, so
  the home-visit charge waits on the reissue (prerequisite, agent; value_input through the days left on the
  requisition and the reissue count). Draw [6,5]: home-visit switch 6, reissue validity 5.
- Sibling overwrite (XF C3): task 0 and task 1 both retire lab_evt_collection_fees clauses; each tail names both
  switch cases (to an at-home kit / to mobile phlebotomy) and restates base for every other case.

## Task 1 — closed (per-task gates)
- Policies: lab_ext_requisition_reissue_validity (agent, 5 factors, reissue_requisition_d14f4a64) <- prerequisite of
  lab_ext_home_phlebotomy_switch_charge (owner=user, 6 factors, switch_order_to_home_phlebotomy_06c13f87); frozen_time
  2026-10-30 14:05:00 EDT. Gold: validity_days 49 (step 9), home_visit_charge 93.00 (step 11).
- Revision: suite needed history_rows >= 8; the order now carries its real August history (booked mobile, switched
  to a service center: mobile refund, draw fee, a duplicate draw and its billing_error refund); "standing" amounts are
  read net of the refunds booked on the order. Gold unchanged.
- Sibling overwrites (C3): task 0 and task 1 tails of lab_evt_collection_fees name both switch cases and restate base.

## Charter-wide tables
### Defining sentences (sentence -> owner -> compute line)
| sentence (abridged) | owner | compute |
|---|---|---|
| member-price correction refund = panel charge less correct price, floor 0, round once | correction baseline | charged, result |
| As standard the correct price is the panel_price | correction baseline | tier_price fall-through |
| tier price Premier/Plus/Essentials/list | membership_tier_pricing | mem_tier, tier_price |
| specimen handling per specimen / flat / 0 | specimen_handling | psc_lines, handling |
| courier by ordering-visit state | specimen_courier | visit_state, courier |
| processing by ordering-visit type | partner_lab_processing | visit_type, processing |
| qualifying membership definition | correction (plain) | mem_status..qualifies |
| switch charge = kit fee waived for recorded Premier; one sum, floor, round once | kit switch baseline | waive_*, kit_fee_due, result |
| outbound shipping by days left x recorded membership | kit_outbound_shipping | link_*, premier_benefit, days_left, outbound |
| return pack by earlier kit lines x specimen | kit_return_pack | kit_lines, return_pack |
| prior collection credit by draw age | prior_collection_credit | draw_standing, draw_date, draw_age, prior_credit |
| dispatch zone by ordering-visit state | kit_dispatch_zone | visit_state, dispatch_zone |
| older-order handling by days since ordered | older_order_handling | order_age, older_order |
| weekend dispatch by change-date weekday | weekend_dispatch | weekday_index, weekend |
| reissued validity: panel validity, whole days, floor 14, carry last | reissue baseline | base_validity, result |
| currency cut / fasting reserve / clinician extension / urgency cut / carried days | the five reissue factors | their bindings |
| home-visit charge = mobile fee waived for Premier; one sum, floor, round once | home-visit baseline | mob_*, mobile_fee_due, result |
| fasting slot / zone / notice / draw credit / serum handling / paperwork | the six home-visit factors | their bindings |
### Transitive factor reads (A1): no factor binding reads another factor's binding; plain bindings read only
  evidence (F/P/K/CFIELD/SUM...) and other plain bindings; only `result` combines factor outputs. Shared evidence is
  duplicated into separate bindings (waive_* vs link_*; slot_window/days_left/paper_window).
### A6 method tier pairs
- specimen_handling: per-specimen (count x unit) vs flat vs none — distinguishing input: specimen count multiplier / constant / none.
- prior_collection_credit: standing vs standing less (2.9% + 0.30) vs none — adds percentage and fixed operation.
- carried_over_days: all days left (floored at 0) vs half rounded down (division + floor) vs none.
- prior_draw_credit: standing vs standing less a fixed reservation floored at 0 vs none.
### A7 T1/T2 (caps/floors): result floors (MX 0 / MX 14) are guards, not factors; no factor is a min/max of bounds.
  T1 per factor = the factor_sensitivity figures in each computation (all differ from gold). T2: each additive factor
  moves its result alone with the others at baseline (all components are independent additive terms).
### B1 edge probes (by hand on compute): absent membership/visit (CFIELD None) -> fall-through tiers, no exception;
  absent draw line -> draw_date None -> age 0, standing 0 -> no credit; days left exactly 10/30/14/60 fall in the
  lower tier as the words say ("10 or fewer", "14 or fewer", "60 or fewer"); negative days left (expired) -> carried
  days floored at 0, notice short; zero standing -> no credit; amounts at x.xx5 do not occur in either world
  (35.982, 93.00, 36.00).
### B2 first-match / aggregate probes
| read | decoy / absent probe | outcome |
|---|---|---|
| CFIELD membership (patient) | second cancelled membership | not seeded; rule reads the patient's membership; single record |
| CFIELD membership by order link | order with no link | None -> no Premier benefit (the edge's point) |
| CFIELD visit by ordering_visit_id | other visit of the patient (task 1 new-patient visit) | keyed on the exact visit id, decoy ignored |
| SUM panel lines | draw line on the same order | filtered by event_type lab_panel_charged |
| SUM/LATEST draw lines | duplicate draw (task 1) | standing nets the billing_error refund; LATEST date same day |
| SUM mobile lines | refunded August mobile line | netted by cancelled_before_collection refund -> 0 standing |
| COUNT kit lines | none on order | 0 -> return pack applies |
### D4 events written and base triggers
- correct_member_rate_order: lab_orders update (path/membership), lab_charge_refunded — triggers [] .
- switch_order_to_home_kit / switch_order_to_home_phlebotomy: lab_orders update (collection_method),
  lab_collection_fee_charged — triggers [].
- reissue_requisition: lab_orders update (requisition_expiry_date, reissue_count) = lab_requisition_reissued — triggers [].
  No write lands in another category.
### B5 compute_basis verbatim sweep: scripted check (every basis quote, replaced_by, policy_source and baseline
  sentence found verbatim in its own rule after whitespace normalisation) — 0 misses on all four policies.
### Residue / decisions
- Renewal notices (membership_notices) are not seeded: no gold read touches them and the replay closure rejects
  unread rows; noted as seed residue.
- Realism risk recorded: specimen handling, courier, processing, return pack, dispatch zone, older-order handling,
  weekend dispatch, reissue levers and home-visit charges are Larkspur-published schedule items added to meet the
  drawn factor counts on a thin charter; shipping figures reuse the rx charter's Larkspur Pharmacy schedule.
- check_traceability (pre-render): only the four unlock tool names miss (expected before the KB exists); every other
  argument has a verbatim source.

## Final gates (no --task)
EXTENDED OK / TASK TOOL CONTRACT OK / REPLAY OK / SOLVABILITY OK / COMPUTE OK / GROUNDING OK / SCOPE OK
ROUND 1: gates 7/7 green
