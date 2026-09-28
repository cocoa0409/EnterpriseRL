# home_claim_settlement — difficulty worklog

## Step 0 draws (scripts/draw_counts.py --tasks 2)
- task 0: prerequisite_problems=1, factor_counts=[5, 5]
- task 1: prerequisite_problems=2, factor_counts=[6, 4, 4]

## Difficulty-level pre-check
- The home charter records no adjuster estimate outside the claim ledger: every replacement-cost and depreciation
  figure lives on a home_claims payment or denial entry. So every scored figure of this difficulty is a
  re-settlement of a figure already on the ledger (a supplemental payment or a reversal of a denial), never a
  first settlement whose estimate only the adjuster holds. A holdback release needs the insured's documented cost,
  which only a release entry records, so no task scores a release.
- Claimable events used: home_claim_payment (subject of every extended policy). home_claim_reported is avoided
  (its hail reporting gate binds a caller-stated claim number).
- Task 0 space: wind/hail occurrence — roof surfacing wrongly denied below a misapplied deductible (prereq) and the
  other-structures re-settlement that inherits the deductible the roof leaves unabsorbed (root, customer's own
  acceptance). Task 1 space is reserved: water perils (hidden water / mold / water backup sublimits, personal property),
  none of which task 0 touches.

## Tool uuids (uuid4().hex[:8], one call per tool)
- settle_denied_roof_surfacing_b6cb399f (task 0, agent)
- accept_structure_supplemental_c73fec14 (task 0, user)
- reserved for task 1: 028e176f, 0cacd0ff, dc7651d7

## Task 0 — closed (gates green, --task 0)
- Tree: home_ext_structure_supplemental (root, user tool accept_structure_supplemental_c73fec14, 5 factors)
  <- home_ext_roof_denial_reversal (agent tool settle_denied_roof_surfacing_b6cb399f, 5 factors), value_input via dw_abs.
- Results: roof reversal 3,530.00 (all-baseline 5,300.00); garage supplemental 15,258.00 (all-baseline 5,450.00;
  without the reversal 8,543.00).
- Fix during authoring: a module-level helper in task_tools.py was read by check_extended as an undiscoverable tool;
  inlined the claim-report lookup into both tools, re-ran replay (REPLAY OK).

## Task 1 — design (draw: 2 prerequisites, factors 6/4/4)
- Freeze burst (peril freeze) on HO-3 Premier; the July adjuster denied the in-wall dwelling damage and the mold as
  repeated seepage, and the contents payment absorbed the whole deductible.
- Root home_ext_contents_supplemental (user tool accept_contents_supplemental_dc7651d7, 6 factors)
  <- home_ext_water_denial_reversal (agent, settle_denied_water_damage_028e176f, 4 factors; value_input dw_abs)
  <- home_ext_mold_denial_reversal (agent, settle_denied_mold_remediation_0cacd0ff, 4 factors; value_input
  mold_entries). Fan-out, the two prerequisites commute. Prerequisite sentences in the negated direction.
- Cross-difficulty: LandlordGuard (dwelling) same-date freeze claim (single-event deductible credit, multi-source)
  and the LandlordGuard holding tenure (companion-line allowance).

## Task 1 — closed (gates green, --task 1)
- Results: water reversal 7,232.00 (all-baseline 3,700.00); mold reversal 8,980.00 (all-baseline 6,200.00);
  contents supplemental 5,198.00 (all-baseline 0.00; without the water reversal 1,988.00; without the mold
  reversal 4,062.00; prerequisites in swapped order 5,198.00 — they commute).

## Final difficulty-wide run (no --task)
- EXTENDED OK; TASK TOOL CONTRACT OK; REPLAY OK (0.json 10 acts, 1.json 12 acts, deterministic, non-vacuous, 0 errors);
  SOLVABILITY OK; COMPUTE OK (suite means branches=44.00, steps=11.00; history_rows_max=24; branches_max=50);
  GROUNDING OK; CACHE-DIFF INFO (no cache trap designed); SCOPE OK.
- check_traceability skipped: the published KB does not exist yet.
- Coverage: 5 extended policies, task 0 = {home_ext_roof_denial_reversal, home_ext_structure_supplemental},
  task 1 = {home_ext_water_denial_reversal, home_ext_mold_denial_reversal, home_ext_contents_supplemental}; disjoint.
- Identifier band 1: phones 216-418-7733 / 216-730-5582; mailing ZIPs 43085 / 43147; policy numbers HG5-1273-4408,
  FG-1552-0917, HG3-1609-2254, LG3-1334-8810; claim serials 1xxxxx; loan numbers 1187-440-2963 / 1402-117-6385.

## Rework round 2 (policy-task audit round 1: audits/policy_task/home_claim_settlement/)
- T0-R1 / G-6: the garage (other-structures) prerequisite sentence now waits on "the roof surfacing of the same claim carries a
  payment entry wherever that roof surfacing was denied below the deductible". Only the roof reversal writes roof surfacing
  payments, so there is one writer. Condition, effect, 0.json edge, rationale and step-3 necessity updated.
- T1-R1 / G-3 (+ SOURCE-TASK): the contents deductible now follows the base order: occurrence deductible, less the same-event
  LandlordGuard share, less the dwelling and other-structures entries. The base "One deductible applies per occurrence ...
  until used up" sentence is declared in overwrite. Base and extended readings now give the same value (0.00 on the task 1 world).
- G-4: the same-event share closes the double-deductible case; the contents rule gains the waiver sentence.
- T1-R2 / G-1: mold containment is now a genuine method (a second base, the claim's wet area, enters the formula; or a flat
  barrier charge; or the estimate as is).
- T1-R2 / G-2: drying has no peril conjunct. Access tear-out uses freeze vs sudden discharge (every tier reachable). Duct
  cleaning is keyed on wet-area extent.
- T1-R3 / G-7: the companion-line factor is removed. The 6-factor draw moves to water (plumbing code-upgrade, and the
  hazardous-material survey moved from mold). Contents has 4 factors: method, cleaning, pack-out, saturated handling.
- Observations:
  - G-5: waiver sums count payment entries that replace no denial.
  - O-4: tear-off fall-through justified in the rule.
  - O-6: haul-away is keyed on depreciation share only; contents disposal is replaced by saturated-goods handling.
  - O-8: resolved by the containment redesign.
  - O-9: prompt replacement removed.
  - O-10: water baseline sentence added and baseline.params completed.
  - O-11: mold carries no depreciation; the base holdback sentence is declared; tool docstring aligned.
  - O-12: removed/covered.
  - T0-O1: roof_settlement is seeded as roof_surfacing_schedule.
  - Roof rule scope now reads "wind or hail"; the schedule clause's replaced_by is now the schedule sentence.
- Seed task 1: report date is now 2026-01-29.
- New gold, task 1: water 8,100.00; mold 8,728.00; contents 4,772.00. Without the water reversal the contents figure is
  2,562.00; without the mold reversal it is 3,636.00. Swapped prerequisite order gives the same values.
- Task 0 gold is unchanged: 3,530.00 and 15,258.00.
- Full gate block green (see final report).

## Rework round 3 (audit revision_2: task 1 PASS; task 0 T0-R2-1 SOURCE-FACTOR RED)
- T0-R2-1: the roof basis ladder mirrored the renewal logic that sets roof_settlement, so it could be read off that
  field. The field stays base-consistent (roof_surfacing_schedule). The roof reversal now follows the declared basis
  as base does (a plain read, no longer a factor), and the stamp-keyed base clause is no longer overridden.
  Roof factors are now (5):
  - prior_unrepaired_roof (method: its tiers choose which quantities make up the deduction; answers O-3);
  - roof_code_upgrade (parameter);
  - roof_tearoff_disposal (parameter);
  - roof_matching (parameter: asphalt 10-19 years -> 5%, 20+ -> 10%; not readable from the field);
  - roof_emergency_tarp (parameter: days to first notice).
  Roof amount 3,530.00 -> 4,700.00 (all-baseline 2,520.00). The garage figure (15,258.00) and its skip value
  (8,543.00) are unchanged.
- R2-O1: the water credit and the contents same-event share count only same-date LandlordGuard freeze or
  sudden-discharge claims (compute filters on peril). Task 1 values unchanged.
- R2-O2: the garage (other-structures) policy scope is limited to wind or hail claims.
- R2-O3: the mold antimicrobial ladder is keyed on water age, not on peril. The water access fall-through is re-worded
  (the wet-area tear-out of a sudden discharge is already inside its replacement cost).
- R2-O4: the hazmat wording now says wet walls are cut out on every reversed water loss.
- R2-T1-O1: the task 1 revision note is corrected.
- Full gate block green.
