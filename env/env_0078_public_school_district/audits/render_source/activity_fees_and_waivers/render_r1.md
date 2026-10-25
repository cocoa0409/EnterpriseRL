# Renderer scan-first findings — product activity, render round 1 (renderer's final reply, extracted verbatim from its transcript by the coordinator; the harness blocked its findings file)

BLOCKED: source mismatch found. I wrote no documents and changed nothing outside /tmp.

I could not write the findings file the brief asks for: the harness refused it ("Subagents should return findings as text, not write report files"). I did not try another way of writing it, so /tmp/render_activity_0078/findings.md does not exist. The full findings are below for you to file. I also did not append the RENDER.log line, because the render never ran.

The gate was fine: `audits/policy_task/activity_fees_and_waivers/_difficulty.md` ends with `VERDICT revision_4: task0=PASS task1=PASS charter=CLEAN`.

Source: `tasks/activity_fees_and_waivers/activity.extended.yaml`. The base `blueprint/products/activity.yaml` is identical to its opening section, byte for byte.

**Checks that came back clean:**
- Every `compute_basis` quote appears word for word in its rule (all 6 policies).
- Every prerequisite `policy_source` appears word for word in its rule.
- Every `superseded_clause` appears word for word in its base clause, and every `replaced_by` appears word for word in its rule.
- Sibling overwrite tails name each other's cases.
- The rounding sentences match `RND(x+1e-9)`.
- All 6 tool docstrings match their tool bodies.

## F1 (RED, the reason I stopped): `activity_ext_arts_first_installment` — the rule's fee-net definition and the compute disagree

Rule (yaml line 1842):
> "Each fee's net is the fee less the free_meal_waiver, reduced_meal_waiver and household_cap credits posted on it;"

Compute (lines 1870–1875; the travel fee and the attire package use the same shape):
> `fi_part_entry: LATEST('activity_ledger','activity_ledger_id', date_field='posted_date', event_type='activity_fee', fee_component='participation_fee')`
> `fi_part_net: MX(0, SUM('activity_ledger','amount', date_field='posted_date', event_type='activity_fee', fee_component='participation_fee') - SUM('activity_ledger','amount', date_field='posted_date', event_type='activity_fee_credit', source_activity_ledger_id=fi_part_entry))`

They disagree in two ways:

1. **Which credits come off.** The credit SUM has no `credit_reason` filter, so it subtracts every credit posted against the fee. The credit reasons in the charter (base line 581) also include `cut_credit, cancellation_credit, withdrawal_window_credit, injury_credit, trip_cancellation_credit, equipment_returned or billing_correction`.
   - Example: a fee carrying a `billing_correction` credit. The rule leaves its net unchanged; the compute lowers it.
   - That moves `plan_total`, `plan_count`, `part_up_front` and the result.
2. **Which fee entries count.** The fee SUM adds every entry of that fee type on the participation, but credits come off only the latest entry. The rule says "each fee's net".
   - Example: two participation_fee entries, each with a waiver. The rule subtracts both waivers; the compute subtracts only the latest one's while still counting both fees.

This is recipe class B1/B2: rule and compute disagree on a decoy or edge row, and the SUM/LATEST read has no stated selection rule. The `compute_basis` for `fi_*_net` quotes the prerequisite sentences; the net definition is quoted only for the `fi_*_entry` bindings.

Fix direction, for the owner to choose: either filter the credit SUM to free_meal_waiver, reduced_meal_waiver and household_cap and net each entry separately (or state which single entry is read), or reword the rule to say what the compute does.

## F2 (low; flagged for the owner, not a stop by itself): "elementary campus" in the compute includes Sunflower Early Childhood Center

`activity_ext_uil_packet_fee` `level_amount` (line 862) and `activity_ext_uil_travel_fee` `trip_level_amount` (line 1041) count `F('campus') == 'Sunflower Early Childhood Center'` as an elementary campus. The rule says only "minus uil_elem_discount for a student at an elementary campus whose enrollment record shows grade 02 through 05".

The world text in blueprint.yaml (line 5) lists "Sunflower Early Childhood Center, five elementary schools (Alder Springs, Bluebonnet Trail, Cypress Hollow, Live Oak and Pecan Grove), ...". On that text a reader would not count Sunflower as an elementary campus. The two only differ for a grade 02–05 participation at Sunflower.

## F3 (low; flagged for the owner, not a stop by itself): the arts trip-group amount doesn't say which record's campus it reads

The `activity_ext_arts_travel_fee` rule (line 1402) says "a student at a middle school campus whose enrollment record shows grade 06 / 07 or 08". Its compute `trip_group_amount` (line 1437) tests `F('campus')`, the campus on the activity participation.

The sibling policy `activity_ext_arts_packet_fee` reads "the campus on the student's district enrollment record for the school year" (`CFIELD('enroll','campus',…)`). Read next to it, "a student at a middle school campus" can be taken to mean the enrollment record's campus. The two only differ when the participation's campus and the enrollment campus are different. The UIL policies' `level_amount` and `trip_level_amount` use the same wording and also read `F('campus')`.

Gate line: none — check_docs was not run because I stopped before rendering. Documents written: 0.
