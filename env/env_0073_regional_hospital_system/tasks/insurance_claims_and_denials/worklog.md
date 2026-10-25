# worklog — insurance_claims_and_denials (env_0073_regional_hospital_system), M=2

Identifier band 22: phones 92055502xx; MRN RB22xxxxxx; ssn_last4 2100-2999; surnames E-H; every invented
free-form identifier carries "22" right after its alphabetic prefix / local-part initial.
Scratch: /tmp/insurance_claims_and_denials_0073/ (authoring scripts removed before finishing).

## Step 0 — difficulty pre-check (2026-10-20)

Read: skill references (product_extended.yaml, task_tools.py, task.json), XF_recipe.md (27 points; applied to
every policy below), blueprint.yaml, products/claim.yaml (+ variant table), db_schema.json, share_tools.py,
encounter/assist/plan/estimate/visit charters (structure only, for cross-difficulty evidence).

Draw (draw_counts.py --tasks 2):
- task 0: prerequisite_problems=3, factor_counts=[6, 4, 6, 5]
- task 1: prerequisite_problems=3, factor_counts=[6, 5, 4, 6]

### Blueprint constraints that shape the design (BLUEPRINT-KNOWN, routed around, never edited)

1. Numeric write fields of this category: claim_transactions.amount (but "0.00 for corrections and appeals"),
   correction_seq / appeal_level (small integers), insurance_claims.total_billed_usd / payer_balance; every date a
   tool writes is "today". So every scored 4-6-factor computation must land as a money posting on
   claim_transactions (write-off, contractual, crossover, billed/re-open, takeback). Appeals, corrections,
   member-ID updates and closures cannot carry a load-bearing multi-factor number and are NOT problems here.
2. The claimed patient acts (AOR signature, reading the card) have no numeric field. The one patient act that
   is genuinely the patient's and lands as money: the patient's in-person decision on the member-level route
   (base claim_authorized_representative: a member-level appeal "asserts the patient's own appeal rights";
   the patient may instead decline it) — once declined, the denial's last route ends and it is closed.
3. DSL scope: F/P/SUM/COUNT read only the target claim; same-category cross reads are forbidden. Hence every
   value_input edge joins two problems on ONE claim, and a 3-prerequisite tree with >= 2 value_input edges
   needs >= 3 problems on one claim.
4. check_compute rejects a pure residual ("whatever is left on the claim"): every problem's figure must be its
   own rule-computed quantity whose factors move it.
5. Events written must have no cross-category trigger: claim_patient_resp_transferred (triggers encounter
   liability) is never written. Events used: claim_denial_written_off (claimed), claim_contractual_adjustment /
   claim_secondary_crossover / claim_billed (unclaimed by the difficulty but in-category, triggers: []).

### Route chosen for task 0
A denied claim whose last route ends is closed by Riverbend's close-out procedure (extended): items another
route closes are taken off first at full charge (record-tested: take-home items, implants lacking their own
authorization, small items), each as its own write-off entry (carc = the claim's denial code, writeoff_reason =
the item's own route); then the charges still open are valued at the payer agreement and that value is written
off on the member's decision; the agreement's contractual remainder is posted by the month-end contractual close
(after frozen_time, so not yet owed — Principle E identity 3).

### Task 0 design thesis (v1, 2026-10-20)
- Surface goal (customer): Gretchen Hallstrom's insurer (Anthem PPO) denied her May knee-surgery claim as not
  medically necessary; Riverbend's two provider appeals were upheld and Riverbend mailed her an authorized-
  representative form so it could file a member-level appeal. She does not want another appeal: she wants the
  claim settled so she is not billed, and she will record that decision herself.
- Root problem (user write): the member's in-person decision closes the claim's last route — the agreement value of
  the services still open is written off as appeals exhausted (claim_denial_written_off, APPEALS_EXHAUSTED).
- Prerequisites (all on the same claim, each its own route, each booked BEFORE the root because the root values only
  what is still open): implants lacking their own authorization (NO_AUTHORIZATION_OBTAINED), separately priced
  laboratory items whose agreement value is at or below the small-denial amount (BELOW_APPEAL_THRESHOLD),
  take-home convenience items with no waiver on file (NONCOVERED_NO_WAIVER). Root's value_input: the charges each
  booked route takes off the scope the root values.
- Valuation convention (extended overwrite of claim_denial_write_off, declared): a closed denial is booked at the
  value Riverbend gives up (agreement value; self-pay value for non-covered items); the contractual remainder is
  posted by the month-end contractual close.

### Task 0 — numeric design v1 (scratch evaluator = check_compute's own DSL env)
Charge lines on the surgery account (19,099.00): OR 29882 8,240 / 29877 3,120; implants C1713 2u 2,640, C1762 2u 1,200;
anesthesia 1,480; recovery 960; pharmacy 312; supply A4649 228; take-home E0218 2u 590, A9273 9, E0114 64; labs 85025
2u 76, 80048 46, 85610 34, 81001 22, 86900 30, 86901 30, 36415 18.
Correction (supersedes the "Route chosen" paragraph above): every route's entry is booked at the value Riverbend gives
up (agreement value; published self-pay price for convenience items), never at full charge; the remainder of each
route's charges stays for the month-end contractual close.
| problem | factors (draw) | handling-time result | all-baseline | per-factor baseline results |
| unauthorized implants (NO_AUTHORIZATION_OBTAINED) | 6 | 1760.72 | 2246.40 | method 2376.40, markup 1563.60, margin 1731.60, units 1695.72, device add-on 1710.72, tissue allowance 1680.72 |
| small lab items (BELOW_APPEAL_THRESHOLD) | 5 | 53.70 | 0.00 | basis 121.50, level 35.25, units 66.13, collection 59.73, test basis 0.00 |
| convenience items (NONCOVERED_NO_WAIVER) | 4 | 277.50 | 304.00 | units 185.00, floor 283.50, self-pay value 442.50, later units 370.00 |
| member-decision close-out (APPEALS_EXHAUSTED, user, root) | 6 | 6526.57 | 8426.34 | method 5303.34, case rate 4456.57, secondary 7366.16, ancillary 8130.41, equipment 6532.04, site 7094.10 |
Root at the opening world (implant + lab entries absent): 8731.04 -> both value_input edges bear weight.
Independence discipline (XF A1/A2): every factor binding tests records/plain bindings only and emits a value or a
method code; plain bindings assemble (no factor reads another factor's binding).

## Task 0 — cards (claimed: claim_ext_unauthorized_implant_closeout, claim_ext_small_lab_item_closeout, claim_ext_noncovered_convenience_closeout, claim_ext_member_decision_closeout)

Occupied before task 0: nothing. Claimed by task 0: the four close-out routes of a final CO-50 denial (implants lacking
their own authorization, small laboratory items, take-home convenience items, member-decision close-out) and their four
write-off tools. Left for task 1: every other write operation (crossover, billed/re-open, contractual, takeback,
TIMELY_FILING_EXPIRED) and every other denial situation; task 1 must not reuse any of these four routes.

### Problem-tree card
Draw: prerequisite_problems=3, factor_counts=[6,4,6,5] -> member-decision 6, unauthorized implant 6, small lab 5,
non-covered convenience 4.
Root: claim_ext_member_decision_closeout (user tool close_denial_on_member_decision_7cc13d5d).
| edge | kind | gate | form | prerequisite sentence (root's rule) | resolved by (owner) | false at opening |
| root <- implant | value_input | implant_booked | state | "The member-decision value is fixed only after any implant lacking its own authorization carries its unauthorized-implant write-off entry on the claim." | write_off_unauthorized_implant_819e3af9 (agent) | claim X has only billed0/appeal1/appeal2 rows; implant lines C1713/C1762 on account E1 |
| root <- small lab | value_input | small_booked | state | "The member-decision value is fixed only after any laboratory item small enough to close below the appeal threshold carries its below-threshold write-off entry on the claim." | write_off_small_lab_item_1ab4cd54 (agent) | no BELOW_APPEAL_THRESHOLD row; lab lines on E1 |
| root <- convenience | state_gate | claim_transactions.writeoff_reason | state | "The member's decision is not recorded until every take-home convenience item on the account carries its non-covered write-off entry on the claim." | write_off_noncovered_convenience_item_58e216c4 (agent) | no NONCOVERED_NO_WAIVER row; E0218 on E1 |
Four-point test: each sentence has an ordering connective ("only after" x2 affirmative, "not ... until" negated — the
desk says a figure "is fixed only after" what it rests on, and a recorded decision "is not recorded until" the claim's
other routes stand); its waited-on side is a record-visible state (a write-off entry of a named kind on the claim);
no tool/policy id/code token; scope matches condition ("any implant lacking its own authorization", "any laboratory
item small enough", "every take-home convenience item"). Exactly one write of this difficulty books each entry kind
(the three tools hard-code their write-off reason). Derivation: sentence + claim activity (no such entry) + the
depended-on rule ("takes ... off the claim as one write-off entry with the write-off reason ...") -> that tool.
Topological order: implant, small lab, convenience (parallel, commuting), then root. Deletion sensitivity (sim.py on
the real tools): skip implant -> root 8593.26; skip small lab -> root 6664.35; skip convenience -> root 6526.57 but
the NONCOVERED_NO_WAIVER row (277.50) is missing and the payer balance is 277.50 higher. Permutation NC,SB,NA ->
root 6526.57 (identical). user_scenario names none of the prerequisites; tools validate nothing.

### Base-invariant card (subject claim_denial_written_off)
- claim_denial_write_off.one_write_off_per_reason (dedup): "The same denial reason is written off once per write-off
  reason on a claim." Evidence: claim X's three rows carry no write-off (carc_code/writeoff_reason empty); each gold
  write uses a distinct (CO-50, reason) pair.
- claim_timely_filing: subject includes write-offs, but its only gate (filing_limit) applies to submissions -> policy_scope.
- No time gate applies to the write-offs. The member-decision rule additionally requires status denied and highest
  appeal level filed (2) >= the PPO's appeal_levels_available (2): both true; member window (180 days from the
  2026-09-15 upheld notice) still open, which is why the patient's decision is needed.

### Business-object card
Target object: claim X (Commercial PPO, denied CO-50) for surgery account E1 (2026-05-12, Grand Chute). Correlation key:
the claim id on every write-off row (tools copy carc and customer from the claim). Rows entering aggregates: E1's 18
encounter_charge_posted lines, selected by revenue code / HCPCS. Excluded: the closed 2025-11-03 emergency account E0
and its claim Y (encounter_id / claim scoping), any non-posting encounter row (event_type filter). No existing
reversal/compensation on X.

### Capability contract cards (task tools)
All four: owner agent (three) / user (member decision); rw write; object = one insurance claim; atomic action = create
one claim_denial_written_off row (fixed write-off reason per tool, carc copied from the claim, posting today) and lower
insurance_claims.payer_balance by the amount; trigger chain: none (event triggers []); receipt = entry id, amount,
reason, denial code, new payer balance. Args: claim_id (Id), amount_usd (Fixed-format, USD 2 decimals positive).

### C14 all-pairs method-tier table (distinguishing input in brackets)
- implant valuation: cost-plus (charges / markup x (1+margin)) vs fee schedule (counted units x fee) [C1713 2u 2640: 1182.72 vs 1220.00];
  cost-plus vs percentage [adds the markup tariff and margin]; fee vs percentage [units vs charges input].
- implant units counted: billed units vs capped units MN(units, 2 x lines) [1 line 3u: 3 vs 2]; billed vs lines [2u 1 line: 2 vs 1];
  capped vs lines [1 line 3u: 2 vs 1].
- laboratory pricing basis: bundled (0) vs schedule vs percentage [schedule tariff vs charges: 85025 1u $38 -> 7.77xlevel vs 22.23].
- small-item test: per code vs scheduled-subset sum vs whole sum [two items 30+30: 60 / 0 / 0; scheduled 45 + collection 10: 45 / 45 / 0].
- convenience units: billed units vs lines vs one per billed code [E0218 2u 1 line: 2/1/1; 2 lines: 2/2/1].
- surgical pricing method: case rate vs per diem (0) vs percentage [case-rate tariff].
- ancillary treatment: bundled (0) vs anesthesia+recovery subset vs all ancillaries [pharmacy 312 present].

### Probe table (scratch copies, probe0.py)
| probe | result |
| handling-time worlds | 1760.72 / 53.70 / 277.50 / 6526.57 |
| decoy write-offs (NO_AUTH, BELOW) on claim Y, opening world | root 8731.04 = opening (scoped by claim) |
| decoy implant/lab/convenience lines on account E0 | unchanged (scoped by encounter_id) |
| encounter_charge_credited row with C1713 on E1 | unchanged (event_type filter) |
| no implant / lab / take-home lines | 0.00 each -> no entry written (rule: 0.00 writes nothing) |
| zero billed units on C1713/E0218/85025 | 1513.60 / 41.27 / 0.00, no division error (rule: per-unit 0.00) |
| emergency-classified account | implant 0.00 (emergency exemption) |
| claim not denied | 0.00 for all three routes |
| only one provider level used | root 0.00 (member gate) |

### Task 0 closure (2026-10-20)
Per-task gates (all OK): check_extended, check_task_tools, replay_tasks, check_solvability, check_compute, check_grounding,
check_cross_fire. XF sweep (xf.py) clean; probes recorded above; C14 table recorded above.
Revisions: (1) factor bindings inlined their own record reads (gate: each factor must read records) -> plain bindings
kept for assembly only; (2) compute_basis quotes made contiguous verbatim spans; (3) replaced_by sentences now restate
the retired base routes instead of deferring to them (XF D17); (4) program_unit_limit 1 -> 2 (C14 degenerate pair);
(5) ancillary program tier changed from a constant multiple of the percentage tier to an anesthesia+recovery subset
(C14); (6) empty FK strings removed from encounter rows (replay FK gate); (7) reads widened to customer scope so the
decoy rows are in the closure. Figures unchanged by every revision: 1760.72 / 53.70 / 277.50 / 6526.57.

## Task 1 — design thesis (v1)
Draw: prerequisite_problems=3, factor_counts=[6,5,4,6].
Occupied by task 0: implant/lab/take-home/member-internal-decision routes on a surgery claim. Task 1 takes a different
denial situation: an Observation Stay claim (Network Health, Commercial HMO) denied CO-50, whose two member-level
appeals were filed under a signed representative form and upheld; ACA external review is still open (4 months after
the final internal denial). Root (user): the patient declines external review -> claim_ext_external_review_decision_closeout.
Prerequisites (same claim): imaging that lacked its own authorization (cardiac/advanced imaging, NO_AUTHORIZATION_OBTAINED,
value_input), routine items bundled into the observation case posted as contractual allowance (claim_contractual_adjustment,
a write kind task 0 does not use, value_input), self-administered drugs written off as non-covered (state_gate).
BLUEPRINT-KNOWN overlap: the claim charter offers one patient money decision (forgoing a remaining member route) and five
write-off reasons; two 4-problem trees must share the write-off event. Task 1 differs in route (external review vs
internal member appeal), claim class (observation vs outpatient surgery), item classes (imaging, bundled routine items,
self-administered drugs) and every pricing term; no task-0 policy or tool is reused.

### Task 1 — design thesis v2 (final; supersedes v1 prerequisites)
v1's three route write-offs would have repeated task 0's chain (routes -> patient decision) — Principle C. v2 tree:
Network Health PAID the observation claim (payment + CO-45 + PR-3 copay; the self-administered drugs left open), then a
retrospective review denied it CO-50; Riverbend's provider reconsideration (level 1) and the member appeal under the
signed form (level 2) were upheld (2026-08-21); ACA external review is open for 4 months.
- RF (agent, 6): refund of the payment attributable to the denied services, booked as a payer recovery (claim_takeback,
  WO-72, a write kind task 0 does not use) = payment received less the retained payment for the diagnostics the payer
  keeps (echo, ECG, labs) net of the member's cost share.
- UA (agent, 5): advanced imaging (CTA + contrast) lacking its own authorization, written off (NO_AUTHORIZATION_OBTAINED);
  limited to the recovered amount (value_input UA <- RF).
- SD (agent, 4): self-administered drugs (rev 0637) written off as non-covered (state_gate into the root).
- Root (user, 6): the patient declines external review; the observation services still open are written off
  (APPEALS_EXHAUSTED), limited to the recovery less the no-authorization write-offs (value_input root <- RF), imaging left
  out once its entry stands (value_input root <- UA).
Shape: diamond (root <- UA <- RF, root <- RF) plus a state gate — different from task 0's fan.

### Task 1 — numeric design (scratch evaluator = check_compute's own DSL env; worlds from replaying the real tools)
Observation account E2 (Neenah, 2026-03-30..04-01, 10,740.00): G0378 46h 3,128; 71275 3,480; Q9967 80ml 88; 93306 2,140;
93005 2u 1 line 312; 84484 3u 288, 85025 38, 80053 84; 96365 642; pharmacy 0250 186; J1644 4u 56; J8499 (0637) 2u 42 + 1u 18;
supplies 0270 142, 0272 96. Remittance 2026-05-06: allowed 5,553.60 (52% of 10,680), payment 5,403.60, CO-45 5,126.40,
PR-3 150.00; drugs 60.00 left open (payer balance 60.00).
| problem | factors | handling-time result | all-baseline | per-factor baseline results |
| refund (claim_takeback WO-72) | 6 | 4823.37 | 3915.36 | method 4065.36, echo fee 4895.37, ECG fee 4830.37, tracings 4782.37, lab multiplier 4843.39, cost share 4673.37 |
| unauthorized imaging (NO_AUTHORIZATION_OBTAINED) | 5 | 868.67 | 1855.36 | CT method 2064.38, CTA fee 810.43, contrast handling 882.29, contrast rate 862.40, site 775.60 |
| self-administered drugs (NONCOVERED_NO_WAIVER) | 4 | 24.00 | 60.00 | method 60.00, dose price 33.00, dispensing fee 19.00, doses counted 36.00 |
| external-review close-out (APPEALS_EXHAUSTED, user, root) | 6 | 2444.20 | 2210.00 | method 1920.76, case-rate band 1274.20, heparin 2460.52, pharmacy 2540.92, supplies 2496.56, infusion 2568.04 |
Opening-world root 0.00 (no recovery); skip imaging -> root 4299.56; skip refund -> imaging 0.00 and root 0.00; skip drugs ->
root unchanged, NONCOVERED_NO_WAIVER entry missing. Final payer balance 1546.50 = contractual remainders for the month-end close.

## Task 1 — cards (claimed: claim_ext_retrospective_denial_refund, claim_ext_unauthorized_imaging_closeout, claim_ext_self_administered_drug_closeout, claim_ext_external_review_decision_closeout)
Occupied before task 1: task 0's four close-out routes and tools. Claimed by task 1: the four policies above and tools
refund_payer_recovery_9b1903be (agent), write_off_unauthorized_imaging_395b7f3f (agent),
write_off_self_administered_drugs_664aab61 (agent), close_denial_on_external_review_decision_5747d436 (user). Coverage:
all eight extended policies, scopes disjoint (check_extended final run).

### Problem-tree card
Draw: prerequisite_problems=3, factor_counts=[6,5,4,6] -> close-out 6, refund 6, imaging 5, drugs 4.
| edge | kind | gate | form | prerequisite sentence | resolved by | false at opening |
| root <- refund | value_input | recovered | state | "The external-review close-out is fixed only after the payer's recovery of its payment stands as a recovery entry on the claim." | refund_payer_recovery_9b1903be | no claim_takeback row on Z |
| root <- imaging | value_input | imaging_booked | state | "The external-review close-out is fixed only after any advanced imaging lacking its own authorization carries its no-authorization write-off entry on the claim." | write_off_unauthorized_imaging_395b7f3f | no NO_AUTHORIZATION_OBTAINED row; 71275/Q9967 on E2 |
| root <- drugs | state_gate | claim_transactions.writeoff_reason | state | "The patient's external-review decision is not recorded until every self-administered drug on the account carries its non-covered write-off entry on the claim." | write_off_self_administered_drugs_664aab61 | no NONCOVERED_NO_WAIVER row; 0637 lines on E2 |
| imaging <- refund | value_input | recovered | state | "The unauthorized-imaging value is fixed only after the payer's recovery of its payment stands as a recovery entry on the claim." | refund_payer_recovery_9b1903be | no claim_takeback row |
Value_input edges 3 >= max(3-1,1). Order: refund -> imaging -> drugs (commutes with both) -> root; permutation refund,
drugs, imaging gives root 2444.20. user_scenario names no refund, imaging, drug, authorization or write-off; tools validate nothing.

### Base-invariant card
- claim_takeback: claim_recoupment_and_overpayment (gate recoupment_dispute_window applies to RECOUPMENT_DISPUTE appeals
  only -> policy_scope); recorded against the remittance that carried the payment (tool copies EFT22648203 / 2026-05-06).
  The refund rule contradicts no base clause and overwrites nothing (XF D15).
- claim_denial_written_off: one_write_off_per_reason (dedup) — Z has no write-off row; gold pairs (CO-50, NO_AUTH),
  (CO-50, NONCOVERED), (CO-50, APPEALS_EXHAUSTED) distinct. claim_timely_filing -> policy_scope.
- Sibling overwrites of the base write-off sentence: all seven (task 0's four + imaging, drugs, close-out) name every other
  sibling route by name and restate the base routes for every other denied amount (scratch sib.py; task 0 texts updated).
- Close-out gate: status denied, appeal filings 2 >= levels 2, external review available, 2 whole months since 2026-08-21 < 4.

### Business-object card
Target object: claim Z (Commercial HMO, Network Health, denied CO-50) for observation account E2. Correlation key: claim id
on every new row. Aggregates: E2's 15 encounter_charge_posted lines (by revenue code / HCPCS); Z's payment, PR-3, appeal,
takeback and write-off rows. Excluded: clinic account E3 and its closed claim Q (encounter / claim scoping), non-posting
encounter rows (event_type filter).

### Capability contract cards
refund tool: creates one claim_takeback row (carc WO-72, trace/date copied from the claim's payment row), raises
payer_balance. Three write-off tools: one claim_denial_written_off row each (fixed reason, carc copied from the claim),
lower payer_balance. Events written and base triggers: claim_takeback triggers [], claim_denial_written_off triggers []
(XF E23). Args: claim_id (Id), amount_usd (Fixed-format). No datetime/time/random/uuid/secrets tokens (XF E18).

### C14 all-pairs method-tier table (distinguishing input)
- retained-test pricing: lesser-of (MN per test) vs fee schedule [93306 charge 500 < fee 612: 500 vs 612]; lesser-of vs
  percentage [tariff + MN vs charges x pct]; fee schedule vs percentage [tariff fees vs charges].
- ECG tracings counted: one per line vs billed units capped at 3 per line [1 line 2u: 1 vs 2]; lines vs units [same];
  capped vs units [1 line 5u: 3 vs 5].
- CT valuation: fee schedule vs lesser-of [71275 charge 600 < fee 742: 742 vs 600]; fee vs percentage; lesser-of vs percentage.
- contrast handling: per ml (units x rate) vs packaged (0) vs percentage [Q9967 80ml 88: 33.60 / 0 / 45.76].
- drug valuation: dose list vs lesser-of(charges, dose list) [charges 10 < list 24: 24 vs 10]; vs charges.
- doses counted: lines vs units capped at 2 per line [1 line 3u: 1 vs 2]; capped vs units [3 vs 2]; lines vs units.
- observation pricing: case rate (band tariff) vs hourly (MN(hours, 48) x rate) vs percentage of charges.
- general pharmacy: packaged (0) vs per-line allowance (lines x 24) vs percentage of charges.

### Probe table (scratch probe1.py) — refund / imaging / drugs / close-out
| opening world | 4823.37 / 0.00 / 24.00 / 0.00 |
| root handling-time world | 0.00 / 868.67 / 24.00 / 2444.20 |
| decoy recovery + no-auth write-off on clinic claim Q (handling world) | 0.00 / 868.67 / 24.00 / 2444.20 |
| decoy CT / self-administered drug lines on clinic account E3 (opening) | 4823.37 / 0.00 / 24.00 / 0.00 |
| charge-credit row with 71275 on E2 (opening) | 4823.37 / 0.00 / 24.00 / 0.00 |
| no imaging lines (handling world) | 0.00 / 0.00 / 24.00 / 2444.20 |
| zero billed units on J1644/96365/G0378/J8499/93005 (handling world) | 0.00 / 868.67 / 33.00 / 1697.96 |
| emergency-classified account (handling world) | 0.00 / 0.00 / 24.00 / 2444.20 |
| claim not denied (appealed) (handling world) | 0.00 / 0.00 / 24.00 / 0.00 |
| claim closed (handling world) | 0.00 / 0.00 / 0.00 / 0.00 |
| only one internal level filed (handling world) | 0.00 / 868.67 / 24.00 / 0.00 |
| only one internal level filed (opening) | 0.00 / 0.00 / 24.00 / 0.00 |
| decoy appeal filing on clinic claim Q, one filing on Z (opening) | 0.00 / 0.00 / 24.00 / 0.00 |
| denial_date empty (handling world) | 0.00 / 868.67 / 24.00 / 0.00 |
| denial 2026-06-22: 4 whole months on 2026-10-22 -> window closed | 0.00 / 868.67 / 24.00 / 0.00 |
| denial 2026-06-23: 3 whole months -> window open | 0.00 / 868.67 / 24.00 / 2444.20 |
| no payer payment (opening) | 0.00 / 0.00 / 0.00 / 0.00 |
| earlier recovery 1000.00 on Z (opening) | 3823.37 / 868.67 / 24.00 / 1000.00 |
| PPO variant (handling world) | 0.00 / 936.77 / 28.00 / 2463.24 |
| Medicare Advantage variant (handling world; no external review) | 0.00 / 1252.80 / 42.00 / 0.00 |
Readings: the handling-time refund is 0.00 once the recovery stands (idempotent); decoys on claim Q / account E3 and a
charge-credit row change nothing; zero billed units give no division error (rule: per-unit 0.00 / no observation value);
window boundary follows the stated whole-month convention; absent denial date -> 0.00.
check_cache_diff (optional diagnostic) reports seeded 60.00 vs "true" 0.00 for Z: it sums the field amount_usd, which this
scenario's claim_transactions does not have (field is amount); the ledger sum 10740.00 - 5403.60 - 5126.40 - 150.00 = 60.00.

### Task 1 closure (2026-10-20)
Per-task gates (all OK): check_extended, check_task_tools, replay_tasks, check_solvability, check_compute, check_grounding,
check_cross_fire. Revisions: (1) base_policy_refs gained claim_timely_filing (gate); (2) on_request discriminator quotes
the persona verbatim; (3) refund and close-out gates count the appeal filings on the claim (claim_msr_appeals_filed)
instead of reading appeal_level (suite history depth gate; figures unchanged); (4) task 0 overwrites and rationale now
name all six sibling routes; task 0 per-task gates re-run green after the shared charter/tool edits.
Figures unchanged by every revision: 4823.37 / 868.67 / 24.00 / 2444.20.

## Final difficulty run (2026-10-20)
Full gates without --task: check_extended, check_task_tools, replay_tasks, check_solvability, check_compute (suite
history_rows_max 10 >= 8, branches_max 332), check_grounding, check_cross_fire — all OK. XF sweep (all 8 policies) clean.
INSTANTIATE round 1: gates 7/7 green

## REWORK round 2 (2026-10-20) — audit audits/policy_task/insurance_claims_and_denials/ (0.md, 1.md, _difficulty.md read in full)
Note: the round-1 authoring scripts had been removed; scratch helpers were re-created in /tmp/insurance_claims_and_denials_0073/
and the existing row ids are carried over from tasks/*.json.

### Redesign decisions (closing whole classes)
- C8 class (invented per-item authorization; NO_AUTHORIZATION_OBTAINED on a CO-50 denial): both NO_AUTH policies
  (implants, imaging) and their tools are removed; no policy books a write-off reason the payer's denial code does not
  support. Every write-off of a CO-50 claim is one of: below-threshold small items, non-covered items without a waiver,
  appeals exhausted. The third prerequisite of each task becomes the payer refund of a post-payment denial.
- Both task claims are paid-then-denied-after-post-payment-review commercial claims; every policy's domain is
  commercial (Commercial PPO, Commercial HMO, Marketplace) — closes C9/C11 (no program tiers, no WC/Medicare member appeals).
- Domain partition by record test (closes C1, C2, C3): task 0 policies act only on claims of an Outpatient Surgery
  Account; task 1 policies act only on claims of an Observation Stay Account or an Emergency Department Visit Account.
  The two close-out roots are further split by the claim's appeal rows: the member-decision close-out requires that no
  member-level appeal (MEMBER_APPEAL_WITH_AOR) has been filed and that a level remains; the external-review close-out
  requires a filed member-level appeal and every level used (closes C10: provider reconsiderations no longer count as
  the claimant's exhausted internal appeals). Each write-off reason therefore has exactly one writer per claim.
- Factor structure (F1-F6): every computation is a sum of disjoint, named line families valued at the standard
  (expected allowed percentage of charges) plus at most one whole-value multiplier; each factor owns exactly one family
  (or the multiplier), so every factor's binding is read in the baseline (F1), no factor reads another's output (F2),
  tier conditions are payer class / campus / record history, never the policy's own scope (F3), every fall-through is
  reachable inside the domain (F4), method tiers change shape (F5, C14 table), labels follow shape (F6).

### Rework checkpoint (gates)
Charter rebuilt (8 policies), task_tools.py rebuilt (5 kept, 3 removed, 3 added), tasks/0.json and tasks/1.json rebuilt;
full gate block run without --task: all 7 OK (history_rows_max 9, branches_max 245). Rationale, probes, C14 tables and the
item-by-item response follow.

### Item-by-item response (item -> what changed -> where)
Superseded note: every section above "REWORK round 2" describes round 1; where it conflicts with this section, this section holds.
- C1 (two roots on one claim) -> roots made mutually exclusive by record tests both rules state: member-decision close-out
  requires zero MEMBER_APPEAL_WITH_AOR rows, fewer appeals than levels and an open member window; external-review close-out
  requires >= 1 MEMBER_APPEAL_WITH_AOR row and appeals >= levels; in addition the two tasks' domains are split by account
  class (Outpatient Surgery vs Observation/ED). -> claim_ext_member_decision_closeout / claim_ext_external_review_decision_closeout
  rule 'scope' + compute member_gate / review_gate; probes "member-level appeal filed" (task 0 root 0.00) and "no
  member-level appeal row" (task 1 root 0.00), cross-world probes 0.00/0.00. The coordinator line "tools refuse the other
  side's records" is NOT implemented: the skill's correctness boundary forbids tool-side refusals/backstops (tools never
  check a condition); exclusivity is carried by the rules' record tests instead.
- C2 (same-reason collisions) -> each write-off reason has exactly one writer per claim: BELOW_APPEAL_THRESHOLD (surgery
  small items vs observation small items), NONCOVERED_NO_WAIVER (convenience vs self-administered drugs), APPEALS_EXHAUSTED
  (the two roots) are split by account class (and the roots by appeal rows); NO_AUTHORIZATION_OBTAINED is no longer written.
- C3 (entry not record-distinguishable) -> the roots' value_input reads (BELOW_APPEAL_THRESHOLD count/sum, recovery sum)
  can only be produced by the same task's policy on that claim (domain split); no two policies of one domain share a reason.
- C4 (non-schedule lab codes dropped) -> class closed: every per-code rule now names its exact code list and the compute
  covers exactly that list (small-item lists; lab schedule codes; "every other charge" families valued at the standard).
- C5 (hidden revenue-code filters) -> every HCPCS read in every rule now states its revenue code ("code Q9967 under revenue
  code 0636", etc.) and the compute filters exactly that.
- C6 (root covers less than rule) -> both roots compute a remainder family (all charges minus every named family) valued
  at the standard, so every covered charge is in the compute; rule sentence 'sel2' names "everything else as the remaining charges".
- C7 (lab payability contradiction) -> no rule calls labs packaged/per-diem any more; in both tasks the diagnostic tests
  are the retained (payable) set of the refund rule and are never covered by the roots.
- C8 (invented per-item authorization; NO_AUTH on CO-50) -> both NO_AUTH policies and tools removed; replaced by the
  post-payment refund (task 0) and the observation small items (task 1); no rule asserts an authorization requirement.
- C9 (member appeal for every payer class) -> every policy's domain is commercial (PPO/HMO/Marketplace); the member-decision
  gate also tests member_appeal_window_days > 0 and the open window.
- C10 (provider reconsideration counted as claimant's appeal) -> external review requires a filed MEMBER_APPEAL_WITH_AOR;
  task 1 world has it (2026-07-09) and task 0's world has none.
- C11 (program tiers vs OPPS) -> no program tiers remain (commercial domains); packaging tiers are worded as Riverbend's
  commercial agreement terms.
- C12 (SAD domain; NONE carc) -> SAD rule restricted to Observation Stay / ED accounts (outpatient) and to denied claims, so
  the copied carc is a denial code; rule cites the Medicare Part B outpatient exclusion as the model; inpatient excluded.
- C13 (framing on no record) -> waiver test is now a record test (no NONCOVERED_SERVICE liability on the account, the release
  a signed waiver supports); "at the payer's request" removed from rules and tool docstrings.
- C14 (undeclared recoupment departure) -> both refund rules declare a scoped overwrite of "A payer takeback re-opens ...
  recorded against the remittance that carried it." naming each other; the tools copy the earliest-posted payment's trace
  and date (O4 closed: the tool sorts payments by posting date; the rule states "earliest-posted").
- C15 (state-gate sentence broader than its condition / never met below a floor) -> no price floor remains; both state-gate
  sentences now carry the depended-on rule's exact scope ("on an account that carries ... and no non-covered patient
  liability, those items carry their non-covered write-off entry"), and the convenience/SAD rules write off every listed
  item in that scope.
- F1 (factors gated through another factor's tier) -> every computation is now a sum of disjoint families plus at most one
  whole multiplier; each factor owns one family, its binding is read in the baseline (fall-through = standard); method
  tiers carry their own tariffs (e.g. the observation case-rate bands live inside the case-rate tier, binding case_rate is
  declared in that factor).
- F2 (tiers reading other factors' outputs) -> no factor is defined per another factor's counted units/values; scratch
  xf.py checks transitive reads (clean).
- F3 (conditions true for everyone in scope) -> no tier condition restates scope ("billed on a Riverbend hospital account",
  "the code is billed" removed); every non-fall-through tier rests on payer class, campus, account class, procedure billed,
  same-day / multi-day dates, contrast volume or released cost-share lines.
- F4 (unreachable fall-throughs) -> every fall-through is reachable inside the commercial domain (Marketplace claims,
  other campuses, the other account class); probes show each policy pricing Marketplace / other-campus worlds.
- F5 (method pair without distinguishing input) -> all method ladders re-checked (table below).
- F6 (mislabelled effect) -> labels follow shape: unit caps / line counts / packaging / lesser-of = method; per-unit rates and
  multipliers = parameter; the old laboratory_units_allowed is gone.
- Task 0 findings 1-7 -> 1 (C15) closed above; 2 (C8) closed; 3 (C13) closed; 4 (factor structure) closed by redesign;
  5/6 (P8 gate; level-3 AOR) closed: task 0 now has one provider level used and the representative form is for level 2 of 2;
  7 (O3) observation kept (see below).
- Task 1 findings 1-9 -> 1 (C1) closed; 2 (C7) closed; 3 (false tier_taken) closed: tier_taken labels are now generated
  from each factor's own ladder; 4 (C8) closed; 5 (C14) closed; 6 (C13) closed; 7 (factor structure) closed; 8 (unbalanced
  remittance) observation: the 0637 drugs (88.00) remain open by design and the seed check states it; 9 (C10) closed.
- Observations: O1 every binding has a compute_basis entry (pb.py asserts it); O2 state-gate edges keep a column gate (the
  waiting is the rule sentence's); O3 the contractual remainder posting stays an observation (no tool closes claims);
  O4 closed (earliest-posted payment); O5 paired tools still write identical rows but never on the same claim (domain split);
  O6 cross_difficulty is now set to encounter on every factor whose bindings read the hospital-account product (41 of 42;
  the one exception, member_cost_share_netting, reads the claim's own released cost-share lines).

### Round-2 numeric design (handling-time results; per-factor baseline results; all-baseline)
task 0:
| claim_ext_surgery_post_payment_refund | 6 factors | 11058.88 | lab_schedule_method 11002.98; blood_bank_typing_handling 11023.78; venipuncture_collection_fee 11051.85; preoperative_ecg_fee 10995.62; urinalysis_fee 11050.11; preoperative_chest_radiograph_fee 10948.10 | all-baseline 10778.04 |
| claim_ext_surgery_small_item_closeout | 5 factors | 31.90 | antiemetic_unit_rate 45.36; steroid_unit_rate 44.24; antibiotic_prophylaxis_handling 59.98; splint_pricing 38.07; iv_solution_unit_rate 45.25 | all-baseline 105.30 |
| claim_ext_noncovered_convenience_closeout | 4 factors | 313.60 | cold_therapy_unit_valuation 489.60; cold_pack_self_pay_price 316.00; support_garment_self_pay_price 320.00; insured_noncovered_discount 392.00 | all-baseline 623.00 |
| claim_ext_member_decision_closeout | 6 factors | 9117.24 | surgical_pricing_method 8733.60; implant_pricing_method 9472.72; anesthesia_unit_rate 9324.97; recovery_room_unit_rate 9348.71; ancillary_packaging 9407.86; site_of_service_factor 9910.04 | all-baseline 10672.74 |
task 1:
| claim_ext_retrospective_denial_refund | 6 factors | 4044.57 | echocardiogram_contract_fee 3543.77; ecg_tracings_counted 3963.45; retained_lab_pricing 3908.60; ct_angiography_pricing 2976.97; contrast_handling 4032.41; member_cost_share_netting 3894.57 | all-baseline 2096.92 |
| claim_ext_observation_small_item_closeout | 5 factors | 9.27 | antiemetic_unit_rate 14.72; ketorolac_handling 19.57; iv_solution_unit_rate 13.95; saline_flush_unit_rate 12.80; small_item_campus_factor 10.30 | all-baseline 36.92 |
| claim_ext_self_administered_drug_closeout | 4 factors | 26.28 | oral_drug_valuation 63.18; oral_dexamethasone_price 33.48; inhalation_unit_dose_price 35.10; sad_campus_factor 29.20 | all-baseline 88.00 |
| claim_ext_external_review_decision_closeout | 6 factors | 2321.99 | observation_pricing_method 1824.72; infusion_contract_fee 2439.64; heparin_unit_rate 2337.49; general_pharmacy_handling 2413.87; observation_supply_percentage 2371.73; observation_campus_factor 2444.20 | all-baseline 2210.00 |
task 0 skips: refund -> small 0.00, root 0.00; small -> root 9214.11; convenience -> root 9117.24 (entry missing). Final payer balance 2219.14.
task 1 skips: refund -> small 0.00, root 0.00; small -> root 2357.06; drugs -> root 2321.99 (entry missing). Final payer balance 1775.03.

### Round-2 problem-tree cards
task 0 (draw 3 / [6,4,6,5]): root claim_ext_member_decision_closeout (user, close_denial_on_member_decision_7cc13d5d) <-
claim_ext_surgery_post_payment_refund (value_input, recovered; refund_surgery_claim_payment_239964f7), <-
claim_ext_surgery_small_item_closeout (value_input, small_booked; write_off_surgery_small_items_d7ad9b50), <-
claim_ext_noncovered_convenience_closeout (state_gate; write_off_noncovered_convenience_item_58e216c4); small items <- refund
(value_input, recovered). Order: refund, small items, convenience (commutes), root.
task 1 (draw 3 / [6,5,4,6]): root claim_ext_external_review_decision_closeout (user, close_denial_on_external_review_decision_5747d436) <-
claim_ext_retrospective_denial_refund (value_input; refund_payer_recovery_9b1903be), <- claim_ext_observation_small_item_closeout
(value_input; write_off_observation_small_items_ab2aa651), <- claim_ext_self_administered_drug_closeout (state_gate;
write_off_self_administered_drugs_664aab61); small items <- refund (value_input). Order: refund, small items, drugs (commutes), root.
Value_input edges per task: 3 >= max(3-1,1). Every prerequisite sentence is state form with an ordering connective, distinct
across the eight policies (gate: identical sentences rejected).
Base-invariant: claim_takeback -> claim_recoupment_and_overpayment (gate applies to RECOUPMENT_DISPUTE appeals: policy_scope;
declared scoped overwrite of the "recorded against the remittance" sentence in both refund rules). claim_denial_written_off ->
one_write_off_per_reason (one writer per reason per claim), claim_timely_filing (submissions only: policy_scope).
Capability cards: refund tools create one claim_takeback (WO-72, earliest-posted payment's trace/date) and raise payer_balance;
write-off tools create one claim_denial_written_off (fixed reason, carc copied from the claim) and lower payer_balance;
events written: claim_takeback (triggers []), claim_denial_written_off (triggers []). No tool checks any condition.
Seed re-pricing (XF F25/F26): task 0 surgery claim remitted at 58.5% of covered charges (no patient-responsibility line; the
account closes on the remittance with nothing owed); task 1 copay ledger (liability, statement, full payment below the
250.00 prompt-pay minimum) unchanged; decoy ED (10% prompt pay, min 100) and clinic (copay at point of service) ledgers
re-checked against the encounter charter.

### Round-2 C14 all-pairs method-tier table (distinguishing input)
- lab_schedule_method / retained_lab_pricing: fee schedule vs lesser-of [code charges below units x amount x mult: 5.00 vs 19.43];
  fee schedule vs percentage [tariff amounts vs charges]; lesser-of vs percentage [adds the schedule input and MN].
- blood_bank_typing_handling / antibiotic_prophylaxis_handling / ketorolac_handling: packaged (0) vs units x fee [any billed
  unit]; packaged vs percentage [any charge]; units x fee vs percentage [tariff vs charges: 1 unit at 60.00 -> 11.50 vs 35.10].
- splint_pricing: lesser-of vs units x fee [charges 10.00 < 18.40: 10.00 vs 18.40]; units x fee vs percentage; lesser-of vs percentage.
- cold_therapy_unit_valuation / oral_drug_valuation: price list (units or lines x price) vs lesser-of(charges, list)
  [charges below the list value]; price list vs charges; lesser-of vs charges [list below charges].
- surgical_pricing_method: case rate (tariff + share of other OR) vs per-procedure fees (units x fee per code) [29882 2 units:
  6150 + .. vs 2 x 5480 + ..]; case rate vs percentage; per-procedure vs percentage.
- implant_pricing_method / ct_angiography_pricing: fee schedule vs lesser-of [charges below fee]; vs percentage.
- ancillary_packaging / general_pharmacy_handling: packaged (0) vs per-line allowance (lines x allowance) vs percentage.
- ecg_tracings_counted: one per line vs units capped per line [1 line 2 units: 1 vs 2]; lines vs units; capped vs units [1 line 5 units: 3 vs 5].
- contrast_handling: per millilitre (units x rate) vs packaged (0) vs percentage [80 ml 88.00: 33.60 / 0 / 45.76].
- observation_pricing_method: case rate by hour band (tariff) vs hourly (MN(hours, 48) x rate) vs percentage of charges
  [46 hours 3128.00: 2150.00 / 2668.00 / 1626.56].

### Round-2 probe table (scratch probe.py; values: refund / small items / non-covered / root)
| task 0 | opening world | 11058.88 / 0.00 / 313.60 / 0.00 |
| task 0 | root handling-time world | 0.00 / 31.90 / 313.60 / 9117.24 |
| task 0 | decoy recovery, small-item write-off and member appeal on the other claim (handling world) | 0.00 / 31.90 / 313.60 / 9117.24 |
| task 0 | decoy drug / convenience / small-item lines on the other account (opening) | 11058.88 / 0.00 / 313.60 / 0.00 |
| task 0 | charge-credit row on the own account (opening) | 11058.88 / 0.00 / 313.60 / 0.00 |
| task 0 | waiver-backed NONCOVERED_SERVICE liability on the account (opening) | 11058.88 / 0.00 / 0.00 / 0.00 |
| task 0 | zero billed units on every line (handling world) | 116.96 / 0.00 / 0.00 / 6532.04 |
| task 0 | claim not denied (appealed) (handling world) | 0.00 / 0.00 / 0.00 / 0.00 |
| task 0 | empty denial date (handling world) | 0.00 / 31.90 / 313.60 / 0.00 |
| task 0 | payer class Commercial PPO Claim (handling world) | 0.00 / 31.90 / 313.60 / 9117.24 |
| task 0 | payer class Commercial HMO Claim (handling world) | 0.00 / 41.94 / 394.00 / 9499.07 |
| task 0 | payer class Marketplace Exchange Plan Claim (handling world) | 0.00 / 85.50 / 620.00 / 7972.63 |
| task 0 | payer class Medicare Advantage Plan Claim (handling world) | 0.00 / 0.00 / 0.00 / 0.00 |
| task 0 | campus Riverbend Regional Medical Center - Appleton (handling world) | 0.00 / 38.07 / 393.50 / 10296.44 |
| task 0 | campus Riverbend Community Hospital - Chilton (handling world) | 0.00 / 38.07 / 395.00 / 10708.30 |
| task 0 | campus Riverbend Surgery & Imaging Center - Grand Chute (handling world) | 0.00 / 31.90 / 313.60 / 9117.24 |
| task 0 | account class Inpatient Admission (handling world) | 0.00 / 0.00 / 0.00 / 0.00 |
| task 1 | opening world | 4044.57 / 0.00 / 26.28 / 0.00 |
| task 1 | root handling-time world | 0.00 / 9.27 / 26.28 / 2321.99 |
| task 1 | decoy recovery, small-item write-off and member appeal on the other claim (handling world) | 0.00 / 9.27 / 26.28 / 2321.99 |
| task 1 | decoy drug / convenience / small-item lines on the other account (opening) | 4044.57 / 0.00 / 26.28 / 0.00 |
| task 1 | charge-credit row on the own account (opening) | 4044.57 / 0.00 / 26.28 / 0.00 |
| task 1 | waiver-backed NONCOVERED_SERVICE liability on the account (opening) | 4044.57 / 0.00 / 0.00 / 0.00 |
| task 1 | zero billed units on every line (handling world) | 1395.95 / 0.00 / 17.10 / 67.83 |
| task 1 | claim not denied (appealed) (handling world) | 0.00 / 0.00 / 0.00 / 0.00 |
| task 1 | empty denial date (handling world) | 0.00 / 9.27 / 26.28 / 0.00 |
| task 1 | payer class Commercial PPO Claim (handling world) | 0.00 / 27.76 / 68.59 / 2881.20 |
| task 1 | payer class Commercial HMO Claim (handling world) | 0.00 / 9.27 / 26.28 / 2321.99 |
| task 1 | payer class Marketplace Exchange Plan Claim (handling world) | 0.00 / 30.35 / 88.00 / 1917.81 |
| task 1 | payer class Medicare Advantage Plan Claim (handling world) | 0.00 / 0.00 / 0.00 / 0.00 |
| task 1 | campus Riverbend Regional Medical Center - Appleton (handling world) | 0.00 / 10.30 / 26.28 / 2444.20 |
| task 1 | campus Riverbend Community Hospital - Chilton (handling world) | 0.00 / 16.28 / 29.20 / 1997.59 |
| task 1 | campus Riverbend Surgery & Imaging Center - Grand Chute (handling world) | 0.00 / 15.50 / 29.20 / 1920.76 |
| task 1 | account class Inpatient Admission (handling world) | 0.00 / 0.00 / 0.00 / 0.00 |
| task 1 world | task 0 policies on task 1 root handling world | 0.00 / 0.00 / 0.00 / 0.00 |
| task 0 world | task 1 policies on task 0 root handling world | 0.00 / 0.00 / 0.00 / 0.00 |
| task 1 | denial 2026-06-22: 4 whole months -> window closed | 0.00 / 9.27 / 26.28 / 0.00 |
| task 1 | denial 2026-06-23: 3 whole months -> window open | 0.00 / 9.27 / 26.28 / 2321.99 |
| task 1 | no member-level appeal row (handling world) | 0.00 / 9.27 / 26.28 / 0.00 |
| task 0 | denial 2026-04-23: 181 days -> member window closed | 0.00 / 31.90 / 313.60 / 0.00 |
| task 0 | denial 2026-04-24: 180 days -> member window open | 0.00 / 31.90 / 313.60 / 9117.24 |
| task 0 | member-level appeal filed (handling world) | 0.00 / 31.90 / 313.60 / 0.00 |
Readings: decoys on the other claim / other account and a charge-credit row change nothing; a waiver-backed
NONCOVERED_SERVICE liability stops the non-covered write-off (and so the state gate's scope); zero units give no division
error; Medicare Advantage and Inpatient Admission worlds fall outside every domain (0.00); each task's policies are 0.00 on
the other task's world (C1/C2 exclusivity); member-window (180 days) and external-review (4 whole months) boundaries follow
the stated conventions; a filed member-level appeal switches the task-0 root off, a missing one switches the task-1 root off.
REWORK round 2: gates 7/7 green

## REWORK round 3 (2026-10-20) — audit revision_2 (0.md, 1.md, _difficulty.md read in full)
Scratch helpers re-created in /tmp/insurance_claims_and_denials_0073/; this round edits the charter as data (rule text,
compute_basis quotes, baseline and overwrite text changed together) and patches the task files from a fresh simulation
with the real tools.

### Item-by-item response (item -> what changed -> where)
- F7 (payer-class tiers on items no payer covers) -> every factor of the two non-covered rules is re-cut onto record facts of
  the items themselves:
  claim_ext_noncovered_convenience_closeout: cold_therapy_unit_valuation = dispensing site (Grand Chute take-home price list /
  hospital-campus price list lesser-of / charges); cold_pack_price_band and support_garment_price_band (renamed from
  *_self_pay_price) = the item's own charge per unit in bands; take_home_kit_share (replaces insured_noncovered_discount) =
  number of kit codes billed; the account class's own rule for insured non-covered items is applied as a stated plain factor
  (CPARAM uninsured_discount_on_noncovered_insured / uninsured_discount_pct; 1 on Outpatient Surgery Accounts).
  claim_ext_self_administered_drug_closeout: oral_drug_valuation = dispensing lines/units; oral_dexamethasone_price_band and
  inhalation_unit_dose_price_band = own charge per unit; sad_dispensing_setting_factor (replaces sad_campus_factor) = account
  class AND campus; the same account-class rule is applied (gives 0.55 on an ED account, 1 on an Observation Stay Account).
  No payer-class condition remains in either rule. Gold: 313.60 and 26.28 unchanged.
- F8 (incidental calendar-day crossing) -> class swept at every read site: claim_ext_retrospective_denial_refund
  ct_angiography_pricing now prices CT per procedure code at the with-contrast rate when contrast (Q9967) is billed with the
  scan; claim_ext_external_review_decision_closeout general_pharmacy_handling now keys on 8 or more observation hours (G0378);
  claim_ext_member_decision_closeout ancillary_packaging now keys on the campus (ambulatory surgery campus vs hospital campus)
  instead of a same-day account. No rule reads service_end_date against service_start_date any more. Gold unchanged
  (4044.57, 2321.99, 9117.24).
- C16 (packaged in one rule, valued in another) -> no small-item rule calls an item packaged: cefazolin_pricing (was
  antibiotic_prophylaxis_handling) and ketorolac_pricing (was ketorolac_handling) now value the drug at the lesser of its
  charges and units x fee / units x fee / percentage. The remaining packaging statements (typing codes in the surgery refund,
  ancillaries in the member-decision close-out, contrast in the observation refund, general pharmacy in the external-review
  close-out) each cover lines that no other rule values. Gold moves: surgery small items 31.90 -> 38.30 (cefazolin 0.00 ->
  6.40); observation small items 9.27 -> 12.33 (ketorolac 0.00 -> 3.40). The roots are unchanged (they leave passing small
  items out); their recovery limits and the final payer balances move (11020.58 / 4032.24; 2212.74 / 1771.97).
- C17 (ordering words in docstrings) -> both refund docstrings rewritten ("the payer's recovery of a payment it made on the
  claim, refunded to the payer by Riverbend"); "after the posting" removed from all eight Returns sections ("the new amount
  still expected from the payer"); no other problem's event is named; scratch sweep finds no after/before/until/then/first/
  earlier/prior/once/later/following in any docstring.
- C18 (tie rule) -> both refund overwrites now say "(the claim's earliest-posted payer payment; when several payer payments
  share that earliest posting date, the one whose remittance trace number comes first in alphabetical order)"; the tool helper
  (_Claims.oldest_payment) sorts by (posting_date, remit_trace_number) and the docstrings describe the same tie; probe below.
- Factor-id uniqueness (O9) -> antiemetic_unit_rate / iv_solution_unit_rate split into surgery_* and observation_*; every
  factor id in the charter is unique (scratch sweep); no factor id is a substring of a tool name.
- Kept as observations: O2, O3, O5, O7, O8, O10, O11, O12 (unchanged by design; no scored consequence).

### Round-3 C14 pairs for changed method factors (distinguishing input)
- cold_therapy_unit_valuation: units x takehome_E0218_asc vs lesser-of(charges, units x takehome_E0218_hosp) [charges below
  the list value]; vs charges [list differs from charges]; lesser-of vs charges [list value below charges].
- oral_drug_valuation: lines x sad_line_price vs lesser-of(charges, units x sad_unit_price) [line count vs units; MN]; vs charges.
- ct_angiography_pricing: units x cta_fee_hmo vs lesser-of(units x cta_fee_ppo, charges) [charges below fee]; vs percentage.
- general_pharmacy_handling / ancillary_packaging: packaged (0) vs lines x allowance vs percentage of charges.
- cefazolin_pricing / ketorolac_pricing: lesser-of(charges, units x fee) vs units x fee [charges below fee: 5.00 vs 6.40]; vs percentage.

### Round-3 probe table (touched reads; scratch probe3.py)
| task 0 | handling-time worlds (each policy at its own step) | 11058.88 / 38.30 / 313.60 / 9117.24 |
| task 0 | convenience at Riverbend Regional Medical Center - Appleton | 353.60 |
| task 0 | convenience at Riverbend Community Hospital - Chilton | 489.60 |
| task 0 | convenience with A9273 16.0/unit, A4467 45.0/unit (bands) | 326.40 |
| task 0 | convenience with A9273 4.0/unit, A4467 12.0/unit (bands) | 308.80 |
| task 0 | convenience with two kit codes billed (A4467 absent) | 338.40 |
| task 0 | convenience with A9273 zero units | 308.80 |
| task 0 | decoy E0218 on the other account | 313.60 |
| task 0 | account class with insured non-covered discount (out of domain) | 0.00 |
| task 0 | cefazolin charge 5.00 below 1 x 6.40 (lesser-of) | 36.90 |
| task 0 | no arthroscopy code 29881/29882 billed (cefazolin, typing fall-through) | 0.00 / 59.98 |
| task 0 | member decision at a hospital campus (ancillary fall-through for PPO) | 10612.34 |
| task 0 | member decision, HMO at a hospital campus (ancillary per line) | 10188.28 |
| task 1 | handling-time worlds (each policy at its own step) | 4044.57 / 12.33 / 26.28 / 2321.99 |
| task 1 | refund with no contrast billed (CT at percentage) | 3010.57 |
| task 1 | refund on PPO with contrast (CT lesser-of; contrast packaged) | 3863.46 |
| task 1 | refund with same-day stay (no effect on CT now) | 4044.57 |
| task 1 | close-out with 0 observation hours (pharmacy packaged only at 8+) | 371.37 |
| task 1 | close-out with 6 observation hours (pharmacy packaged only at 8+) | 1302.37 |
| task 1 | close-out with 8 observation hours (pharmacy packaged only at 8+) | 1666.49 |
| task 1 | ketorolac charge 2.00 below 1 x 3.40 (lesser-of) | 11.07 |
| task 1 | drugs on an ED account (setting 0.95; account rule 1 - 45%) | 15.26 |
| task 1 | J8499 on a single line of two units (lesser of charges and 2 x 7.00) | 21.78 |
| task 1 | J8540 at 22.0/unit (band) | 28.98 |
| task 1 | J8540 at 8.0/unit (band) | 29.88 |
| task 1 | drugs at Chilton (setting factor 1) | 29.20 |
| task 1 | decoy J8540 on the other account | 26.28 |
| task 1 | tie: two payments posted the same day; tool records against | EFT22000001 |
| cross | task 0 policies on task 1 root world | 0.00 / 0.00 / 0.00 / 0.00 |
| cross | task 1 policies on task 0 root world | 0.00 / 0.00 / 0.00 / 0.00 |
REWORK round 3: gates 7/7 green

## REWORK round 4 (2026-10-21) — audit revision_3 (0.md, 1.md, _difficulty.md read in full)
### Item-by-item response (item -> what changed -> where)
- F9 (non-monotone price bands that could value an item above its own charge) -> every band ladder on an item's own charge is
  removed; each factor of the two non-covered policies now values an item at a share (<= 1) of its own charges, a
  lesser-of against its charges, or a per-line fee inside a cap at the charges, so every value is non-decreasing in the
  unit charge and never above it:
  claim_ext_noncovered_convenience_closeout: cold_therapy_unit_valuation = lesser of charges and units x take-home price
  (Grand Chute) / lesser of charges and charges x hospital share + fee per line (hospital campus) / charges (Chilton);
  cold_pack_take_home_share (replaces cold_pack_price_band) = charges x 0.65 when the cold-therapy unit is also billed,
  x 0.80 with the garment only, x 1 alone; support_garment_take_home_share (replaces support_garment_price_band) = charges x
  0.60 on an arthroscopy account, x 0.75 with other operating-room lines, x 1 otherwise; take_home_kit_share unchanged.
  claim_ext_self_administered_drug_closeout: oral_drug_valuation now caps both price-list tiers at the charges;
  sad_campus_pharmacy_share (replaces oral_dexamethasone_price_band) = the dispensing campus's outpatient pharmacy
  self-pay share of the J8540 and J7613 charges (Neenah 0.35, Appleton 0.40, otherwise 1); sad_dispensing_fee (replaces
  inhalation_unit_dose_price_band; the lever the coordinator named) = a fee per 0637 dispensing line by the account's
  service classification (medically necessary 0.50, emergency 0.75, otherwise 0.00); the drug value is capped at the
  drugs' charges (stated sentence); sad_dispensing_setting_factor unchanged.
  Class sweep of other band ladders: the observation contrast volume threshold (contrast_min_ml) in
  claim_ext_retrospective_denial_refund is removed (contrast_handling now keys on contrast billed with computed
  tomography); the observation case-rate hour bands are monotone increasing and are now capped at the observation charges
  (lesser of case rate and charges); the remaining thresholds are route tests, not prices (small-item test at the
  small-denial amount, 8 observation hours for packaging, appeal and window gates).
- O13 (dead discount branch) -> the account-class discount clause is removed from the convenience rule (it can never apply
  on an Outpatient Surgery Account); the rule now states that the Outpatient Surgery Account class gives an insured
  patient's non-covered items no uninsured discount. In the self-administered drug rule the clause stays, live on
  Emergency Department accounts (probe: 0.55).
- Unused unit reads left by the re-cut (A9273, A4467, J8540, J7613 billed units) removed with their list-sentence words.
- Gold moves: task 0 convenience write-off 313.60 -> 312.20; task 1 self-administered drug write-off 26.28 -> 27.72. Every
  other figure unchanged (11058.88 / 38.30 / 9117.24; 4044.57 / 12.33 / 2321.99); final payer balances 2214.14 / 1770.53.
  Prerequisite tree, edges, skip figures (0.00, 9214.11, unchanged; 0.00, 2357.06, unchanged) and cross-task exclusivity
  unchanged.

### Round-4 C14 pairs for changed method factors (distinguishing input)
- cold_therapy_unit_valuation: lesser-of(charges, units x price) vs lesser-of(charges, charges x share + lines x fee)
  [units vs lines inputs; 2 lines of 1 unit at 400.00 each (800.00): 2 x 185.00 = 370.00 vs 800.00 x 0.60 + 2 x 12.00 = 504.00]; either vs charges [price below charges].
- oral_drug_valuation: lesser-of(charges, lines x price) vs lesser-of(charges, units x price) [2 lines of 1 unit vs 1 line
  of 2 units]; either vs charges.

### Round-4 probe table (scratch probe4.py): unit-charge sweeps across every former band edge, tier reachability, edges
| task 0 | E0218 charge per unit swept 0.50..400.00 across every former band edge: non-decreasing=True, never above the item charges=True | 0.5:17.00 6.0:25.80 12.0:35.40 20.0:48.20 400.0:312.20 |
| task 0 | A9273 charge per unit swept 0.50..400.00 across every former band edge: non-decreasing=True, never above the item charges=True | 0.5:307.78 6.0:310.64 12.0:313.76 20.0:317.92 400.0:515.52 |
| task 0 | A4467 charge per unit swept 0.50..400.00 across every former band edge: non-decreasing=True, never above the item charges=True | 0.5:300.92 6.0:303.56 12.0:306.44 20.0:310.28 400.0:492.68 |
| task 0 | convenience dispensed at Riverbend Regional Medical Center - Appleton (E0218 tier) | 309.00 |
| task 0 | convenience dispensed at Riverbend Community Hospital - Chilton (E0218 tier) | 488.20 |
| task 0 | no cold-therapy unit: pack share with garment (0.80), kit pair (0.90) | 19.44 |
| task 0 | cold pack alone (share 1, kit 1) | 9.00 |
| task 0 | garment with other operating-room lines, no arthroscopy (0.75) | 315.08 |
| task 0 | garment with no operating-room line (1) | 319.88 |
| task 0 | small-item test edge: J0690 charges 50.00 | 38.30 |
| task 0 | small-item test edge: J0690 charges 50.01 | 31.90 |
| task 1 | J8499 charge per unit swept 0.50..400.00 across every former band edge: non-decreasing=True, never above the item charges=True | 0.5:27.72 6.0:27.72 12.0:27.72 20.0:27.72 400.0:27.72 |
| task 1 | J8540 charge per unit swept 0.50..400.00 across every former band edge: non-decreasing=True, never above the item charges=True | 0.5:24.10 6.0:25.83 12.0:27.72 20.0:30.24 400.0:149.94 |
| task 1 | J7613 charge per unit swept 0.50..400.00 across every former band edge: non-decreasing=True, never above the item charges=True | 0.5:23.00 6.0:26.46 12.0:30.24 20.0:35.28 400.0:274.68 |
| task 1 | drugs on an ED account (setting 0.95, account rule 0.55) | 16.09 |
| task 1 | drugs, account classified EMERGENCY (dispensing fee tier) | 28.62 |
| task 1 | drugs, account classified ELECTIVE_NON_COVERED (dispensing fee tier) | 25.92 |
| task 1 | drugs dispensed at Riverbend Regional Medical Center - Appleton (campus share) | 28.98 |
| task 1 | drugs dispensed at Riverbend Community Hospital - Chilton (campus share) | 49.00 |
| task 1 | refund with contrast but no computed tomography (contrast at percentage) | 4774.41 |
| task 1 | close-out at observation-hour band edges 7/8/23/24/47/48/60 (case rate capped at the observation charges; pharmacy packaged from 8 hours) | 7h:1302.37 8h:1666.49 23h:1666.49 24h:2321.99 47h:2321.99 48h:2787.49 60h:2787.49 |
| cross | task 0 policies on task 1 root world | 0.00 / 0.00 / 0.00 / 0.00 |
| cross | task 1 policies on task 0 root world | 0.00 / 0.00 / 0.00 / 0.00 |
| gold | task 0 / task 1 handling-time values | 11058.88 / 38.30 / 312.20 / 9117.24 ; 4044.57 / 12.33 / 27.72 / 2321.99 |
REWORK round 4: gates 7/7 green

## REWORK round 5 (2026-10-21) — audit revision_4 (0.md, 1.md, _difficulty.md read in full)
### Item-by-item response (item -> what changed -> where)
- C19 (assembly order) -> claim_ext_self_administered_drug_closeout assembly sentence now fixes every kind it combines,
  exactly as compute applies them: "replacements are made first, the per-line fees are added to them, the sum is then
  multiplied by the account class's own rule ..., the product is then capped at the drugs' charges, and the total is rounded
  once" (compute: RND(MN(charges, (replacements + fees) x account factor), 2)). Class sweep of every assembly sentence: the two
  refund rules now place their floors ("the sum is taken from the payment received (never below 0.00)"; "the deduction after
  them (never below 0.00), the resulting retained payment is then taken from the payment received (never below 0.00)");
  the small-item and close-out rules already place their recovery limits; the convenience rule combines only replacements
  and one multiplier; the observation case-rate cap is internal to one replacement and stated in its own sentence.
- F10 (unreal levers) ->
  claim_ext_noncovered_convenience_closeout: cold_pack_quantity_share (replaces the co-billing cold-pack share) and
  support_garment_quantity_share (replaces the arthroscopy-keyed garment share) now follow the quantity dispensed on the
  take-home price list (pack 0.70 for 2-3 units, 0.55 for 4+; garment 0.75 for 2, 0.60 for 3+; 1 for a single unit);
  take_home_kit_share is the only factor reading the co-billing fact.
  claim_ext_self_administered_drug_closeout: sad_pharmacy_dispensing_fee is a flat fee per 0637 line by the dispensing
  pharmacy (inpatient pharmacy for an observation stay at a hospital campus 0.50, emergency department cabinet for an ED
  visit at a hospital campus 0.25, otherwise 0.00); oral_dexamethasone_quantity_share (J8540: 0.60 for 2-3 units, 0.50 for
  4+) and inhalation_unit_dose_quantity_share (J7613: 0.55 for 2-5, 0.50 for 6+) replace the campus share; the campus share
  and the dispensing-setting multiplier are removed, so campus and account class are read by one factor only. Shares are
  chosen so that value is non-decreasing in quantity as well as in unit charge (n x share_n >= (n-1) x share_(n-1)).
  Seed: quantities dispensed set on the existing lines without changing any charge (task 0 A9273 2 units, A4467 3 units;
  task 1 J8540 2 units); no other computation reads those units.
- O14 (stale binding names) -> renamed: a9273_qty_share, a4467_qty_share, kit_share (convenience); j8540_qty_share,
  j7613_qty_share, dispensing_fee_per_line, val_fee (drugs); unused plain unit reads and the old ecg_lines read removed.
- Tool rounding check -> no task-tool docstring claims half-up rounding; every amount Arg says "already rounded to the cent by
  the caller; the tool posts it exactly as given", and round(float(x), 2) returns a two-decimal input unchanged; no change.
- Gold moves: task 0 convenience write-off 312.20 -> 312.56; task 1 self-administered drug write-off 27.72 -> 37.00. Every
  other figure unchanged (11058.88 / 38.30 / 9117.24; 4044.57 / 12.33 / 2321.99); skip figures unchanged; final payer
  balances 2213.78 / 1761.25; cross-task exclusivity unchanged.

### Round-5 probe table (scratch probe5.py): F9 regression (unit-charge sweeps), quantity sweeps, tiers, caps, exclusivity
| task 0 | E0218: unit charge 0.50..400.00 non-decreasing=True, capped=True; quantity 1..8 units at its unit charge non-decreasing=True, capped=True | 1u:164.56 2u:312.56 3u:460.56 4u:608.56 5u:756.56 6u:904.56 7u:1052.56 8u:1200.56 |
| task 0 | A9273: unit charge 0.50..400.00 non-decreasing=True, capped=True; quantity 1..8 units at its unit charge non-decreasing=True, capped=True | 1u:311.12 2u:312.56 3u:315.08 4u:315.44 5u:317.42 6u:319.40 7u:321.38 8u:323.36 |
| task 0 | A4467: unit charge 0.50..400.00 non-decreasing=True, capped=True; quantity 1..8 units at its unit charge non-decreasing=True, capped=True | 1u:307.44 2u:310.64 3u:312.56 4u:316.40 5u:320.24 6u:324.08 7u:327.92 8u:331.76 |
| task 0 | kit of two codes (no cold-therapy unit): kit share 0.90 | 18.63 |
| task 1 | J8499: unit charge 0.50..400.00 non-decreasing=True, capped=True; quantity 1..8 units at its unit charge non-decreasing=True, capped=True | 1u:37.00 2u:37.00 3u:37.00 4u:37.00 5u:37.00 6u:37.00 7u:37.00 8u:37.00 |
| task 1 | J8540: unit charge 0.50..400.00 non-decreasing=True, capped=True; quantity 1..8 units at its unit charge non-decreasing=True, capped=True | 1u:35.80 2u:37.00 3u:40.60 4u:41.80 5u:44.80 6u:47.80 7u:50.80 8u:53.80 |
| task 1 | J7613: unit charge 0.50..400.00 non-decreasing=True, capped=True; quantity 1..8 units at its unit charge non-decreasing=True, capped=True | 1u:36.20 2u:37.00 3u:41.40 4u:45.80 5u:50.20 6u:52.20 7u:56.20 8u:60.20 |
| task 1 | drugs: ED account at Neenah (cabinet fee 0.25, account rule 0.55) | 19.80 |
| task 1 | drugs: observation at Chilton (no dispensing fee) | 35.00 |
| task 1 | drugs: observation at Appleton (inpatient pharmacy fee) | 37.00 |
| task 1 | tiny J8499/J7613 charges: value never above the 0637 charges | 10.47 <= 13.50 |
| cross | task 0 policies on task 1 root world | 0.00 / 0.00 / 0.00 / 0.00 |
| cross | task 1 policies on task 0 root world | 0.00 / 0.00 / 0.00 / 0.00 |
| gold | task 0 / task 1 handling-time values | 11058.88 / 38.30 / 312.56 / 9117.24 ; 4044.57 / 12.33 / 37.00 / 2321.99 |
| gold | final payer balances | 2213.78 / 1761.25 |
| gold | skip figures (root) | 0.00 / 9214.11 / 9117.24 ; 0.00 / 2357.06 / 2321.99 |
REWORK round 5: gates 7/7 green

## REWORK round 6 (2026-10-21) — audit revision_5 (0.md, 1.md, _difficulty.md read in full)
### Item-by-item response (item -> what changed -> where)
- F11 (J8499 valued higher for one dose than for two) -> claim_ext_self_administered_drug_closeout: oral_drug_valuation is
  replaced by oral_drug_quantity_share (parameter): the J8499 charges times the quantity share on the outpatient pharmacy
  self-pay list (0.45 for 3 or more units, 0.60 for 2, 1 for a single unit; n x share_n >= (n-1) x share_(n-1), so value never
  falls as doses rise). To keep a method factor, sad_pharmacy_dispensing_fee becomes a method: fee_inpatient_pharmacy per 0637
  line from the inpatient pharmacy (observation stay at a hospital campus), one fee_ed_visit per visit from the emergency
  department cabinet (ED visit at a hospital campus), no fee otherwise. Assembly sentence updated to "adds a dispensing fee;
  replacements are made first, the dispensing fee is added to them, ..." (order unchanged: replacements, fee, account-class
  multiplier, cap at the drugs' charges, rounding). Binding names follow meanings (j8499_qty_share, dispensing_fee_method).
- Class sweep (every valuation factor, both dimensions) -> the sweep found one more member of the class: fee-schedule and
  case-rate tiers in six policies could value a family above its own billed charges at very low unit charges (e.g. 36415
  at 0.50 per unit valued at 3.50). Every such family is now capped at its billed charges, stated in each assembly sentence
  ("never above that group's / that code's / the lines' billed charges (Riverbend's agreements pay the lesser of the
  scheduled amount and the billed charges)"): claim_ext_surgery_post_payment_refund, claim_ext_surgery_small_item_closeout,
  claim_ext_member_decision_closeout (task 0's policies — required by the class sweep), claim_ext_retrospective_denial_refund,
  claim_ext_observation_small_item_closeout, claim_ext_external_review_decision_closeout. No cap binds on either task world:
  every task-0 figure, factor_sensitivity and baseline_result is identical, and tasks/0.json is byte-identical (sha256
  99a085a37abb... unchanged); claim_ext_noncovered_convenience_closeout is untouched.
- Gold moves: task 1 self-administered drug write-off 37.00 -> 45.00 (J8499 27.00 + J8540 7.20 + J7613 8.80 + fee 2.00).
  Every other figure unchanged (11058.88 / 38.30 / 312.56 / 9117.24; 4044.57 / 12.33 / 2321.99); final payer balances
  2213.78 / 1753.25; cross-task exclusivity unchanged. Replay was run only with --check.

### Round-6 exhaustive sweep (scratch sweep.py): every valuation factor, each code, quantity 1-8 units on one line at the
### seeded unit charge and unit charge 0.50-400.00 at the seeded quantity, evaluated on the policy's handling-time world
| surgery_post_payment_refund | lab_schedule_method | 0300/85025 | qty non-decreasing True | unit-charge non-decreasing True | never above family charges True |
| surgery_post_payment_refund | lab_schedule_method | 0300/80048 | qty non-decreasing True | unit-charge non-decreasing True | never above family charges True |
| surgery_post_payment_refund | lab_schedule_method | 0300/85610 | qty non-decreasing True | unit-charge non-decreasing True | never above family charges True |
| surgery_post_payment_refund | blood_bank_typing_handling | 0300/86900 | qty non-decreasing True | unit-charge non-decreasing True | never above family charges True |
| surgery_post_payment_refund | blood_bank_typing_handling | 0300/86901 | qty non-decreasing True | unit-charge non-decreasing True | never above family charges True |
| surgery_post_payment_refund | venipuncture_collection_fee | 0300/36415 | qty non-decreasing True | unit-charge non-decreasing True | never above family charges True |
| surgery_post_payment_refund | preoperative_ecg_fee | 0730/93005 | qty non-decreasing True | unit-charge non-decreasing True | never above family charges True |
| surgery_post_payment_refund | urinalysis_fee | 0300/81001 | qty non-decreasing True | unit-charge non-decreasing True | never above family charges True |
| surgery_post_payment_refund | preoperative_chest_radiograph_fee | 0324/71046 | qty non-decreasing True | unit-charge non-decreasing True | never above family charges True |
| surgery_small_item_closeout | surgery_antiemetic_unit_rate | 0636/J2405 | qty non-decreasing True | unit-charge non-decreasing True | never above family charges True |
| surgery_small_item_closeout | steroid_unit_rate | 0636/J1100 | qty non-decreasing True | unit-charge non-decreasing True | never above family charges True |
| surgery_small_item_closeout | cefazolin_pricing | 0636/J0690 | qty non-decreasing True | unit-charge non-decreasing True | never above family charges True |
| surgery_small_item_closeout | splint_pricing | 0270/A4570 | qty non-decreasing True | unit-charge non-decreasing True | never above family charges True |
| surgery_small_item_closeout | surgery_iv_solution_unit_rate | 0258/J7050 | qty non-decreasing True | unit-charge non-decreasing True | never above family charges True |
| noncovered_convenience_closeout | cold_therapy_unit_valuation | 0274/E0218 | qty non-decreasing True | unit-charge non-decreasing True | never above family charges True |
| noncovered_convenience_closeout | cold_pack_quantity_share | 0274/A9273 | qty non-decreasing True | unit-charge non-decreasing True | never above family charges True |
| noncovered_convenience_closeout | support_garment_quantity_share | 0274/A4467 | qty non-decreasing True | unit-charge non-decreasing True | never above family charges True |
| member_decision_closeout | surgical_pricing_method | 0360/29882 | qty non-decreasing True | unit-charge non-decreasing True | never above family charges True |
| member_decision_closeout | surgical_pricing_method | 0360/29877 | qty non-decreasing True | unit-charge non-decreasing True | never above family charges True |
| member_decision_closeout | implant_pricing_method | 0278/C1713 | qty non-decreasing True | unit-charge non-decreasing True | never above family charges True |
| member_decision_closeout | implant_pricing_method | 0278/C1762 | qty non-decreasing True | unit-charge non-decreasing True | never above family charges True |
| member_decision_closeout | anesthesia_unit_rate | 0370/all | qty non-decreasing True | unit-charge non-decreasing True | never above family charges True |
| member_decision_closeout | recovery_room_unit_rate | 0710/all | qty non-decreasing True | unit-charge non-decreasing True | never above family charges True |
| member_decision_closeout | ancillary_packaging | 0250/all | qty non-decreasing True | unit-charge non-decreasing True | never above family charges True |
| member_decision_closeout | ancillary_packaging | 0272/A4649 | qty non-decreasing True | unit-charge non-decreasing True | never above family charges True |
| retrospective_denial_refund | echocardiogram_contract_fee | 0483/93306 | qty non-decreasing True | unit-charge non-decreasing True | never above family charges True |
| retrospective_denial_refund | ecg_tracings_counted | 0730/93005 | qty non-decreasing True | unit-charge non-decreasing True | never above family charges True |
| retrospective_denial_refund | retained_lab_pricing | 0300/84484 | qty non-decreasing True | unit-charge non-decreasing True | never above family charges True |
| retrospective_denial_refund | retained_lab_pricing | 0300/85025 | qty non-decreasing True | unit-charge non-decreasing True | never above family charges True |
| retrospective_denial_refund | retained_lab_pricing | 0300/80053 | qty non-decreasing True | unit-charge non-decreasing True | never above family charges True |
| retrospective_denial_refund | ct_angiography_pricing | 0350/71275 | qty non-decreasing True | unit-charge non-decreasing True | never above family charges True |
| retrospective_denial_refund | contrast_handling | 0636/Q9967 | qty non-decreasing True | unit-charge non-decreasing True | never above family charges True |
| observation_small_item_closeout | observation_antiemetic_unit_rate | 0636/J2405 | qty non-decreasing True | unit-charge non-decreasing True | never above family charges True |
| observation_small_item_closeout | ketorolac_pricing | 0636/J1885 | qty non-decreasing True | unit-charge non-decreasing True | never above family charges True |
| observation_small_item_closeout | observation_iv_solution_unit_rate | 0258/J7050 | qty non-decreasing True | unit-charge non-decreasing True | never above family charges True |
| observation_small_item_closeout | saline_flush_unit_rate | 0270/A4216 | qty non-decreasing True | unit-charge non-decreasing True | never above family charges True |
| self_administered_drug_closeout | oral_drug_quantity_share | 0637/J8499 | qty non-decreasing True | unit-charge non-decreasing True | never above family charges True |
| self_administered_drug_closeout | oral_dexamethasone_quantity_share | 0637/J8540 | qty non-decreasing True | unit-charge non-decreasing True | never above family charges True |
| self_administered_drug_closeout | inhalation_unit_dose_quantity_share | 0637/J7613 | qty non-decreasing True | unit-charge non-decreasing True | never above family charges True |
| self_administered_drug_closeout | sad_pharmacy_dispensing_fee | 0637/all | qty non-decreasing True | unit-charge non-decreasing True | never above family charges True |
| external_review_decision_closeout | observation_pricing_method | 0762/G0378 | qty non-decreasing True | unit-charge non-decreasing True | never above family charges True |
| external_review_decision_closeout | infusion_contract_fee | 0260/96365 | qty non-decreasing True | unit-charge non-decreasing True | never above family charges True |
| external_review_decision_closeout | heparin_unit_rate | 0636/J1644 | qty non-decreasing True | unit-charge non-decreasing True | never above family charges True |
| external_review_decision_closeout | general_pharmacy_handling | 0250/all | qty non-decreasing True | unit-charge non-decreasing True | never above family charges True |
| external_review_decision_closeout | observation_supply_percentage | 0270/all | qty non-decreasing True | unit-charge non-decreasing True | never above family charges True |
| external_review_decision_closeout | observation_supply_percentage | 0272/all | qty non-decreasing True | unit-charge non-decreasing True | never above family charges True |
### Round-6 probes
| cross | task 0 policies on task 1 root world | 0.00 / 0.00 / 0.00 / 0.00 |
| cross | task 1 policies on task 0 root world | 0.00 / 0.00 / 0.00 / 0.00 |
| task 1 | drugs: ED cabinet: one 1.00 fee per visit; account rule 0.55 | 24.20 |
| task 1 | drugs: Chilton: no dispensing fee | 43.00 |
| task 1 | drugs: Appleton inpatient pharmacy: 4 x 0.50 | 45.00 |
| gold | task 0 / task 1 handling-time values | 11058.88 / 38.30 / 312.56 / 9117.24 ; 4044.57 / 12.33 / 45.00 / 2321.99 |
| gold | final payer balances | 2213.78 / 1753.25 |
REWORK round 6: gates 7/7 green

## REWORK round 7 (2026-10-21) — audit revision_6 (0.md, 1.md, _difficulty.md read in full)
### Item-by-item response (item -> what changed -> where)
- F12 (pharmacy packaged without the case rate it packages into; case rate capped at observation charges only) ->
  claim_ext_external_review_decision_closeout: the observation case rate now packages the general pharmacy and is the
  lesser of the case rate and the billed charges of the observation AND general pharmacy lines it packages; the general
  pharmacy carries no value of its own only when that case rate is paid (case-rate method with observation hours billed),
  otherwise it is valued at the expected allowed percentage (HMO at Chilton, PPO hourly, Marketplace, no hours).
  general_pharmacy_handling (and its 8-hour test and per-line allowance) is removed; to keep six load-bearing factors the
  supply family is split: medical_surgical_supply_percentage (renamed from observation_supply_percentage, 0270 apart from the
  listed flush) and sterile_supply_percentage (new, 0272: 0.25 HMO / 0.33 PPO on an observation stay, otherwise the expected
  allowed percentage).
- Class sweep of every packaging / case-rate / cap interaction (the sweep forced changes in task 0's policies — said here):
  claim_ext_member_decision_closeout: the ancillaries (0250, 0272) are packaged only into the arthroscopy case rate that is
  paid (PPO with code 29882), and that case rate is the lesser of the rate and the billed charges of the operating-room and
  ancillary lines it packages; otherwise the ancillaries are valued at the expected allowed percentage. ancillary_packaging is
  removed; crutch_take_home_rate (new, E0114: dme_e0114_asc 31.50 for PPO at Grand Chute, dme_e0114_hosp 36.00 for HMO at a
  hospital campus, otherwise charges per unit x expected allowed percentage; capped at its charges) keeps six factors.
  claim_ext_surgery_post_payment_refund: the typing codes are packaged only when the PPO arthroscopy case rate is paid (code
  29882), no longer on any arthroscopy code (29881 alone pays no case rate). claim_ext_retrospective_denial_refund: the PPO
  with-contrast CT rate, which packages the contrast, is now the lesser of the rate and the charges of the scan and the
  contrast. No other rule packages a line.
- Gold moves: task 0 member-decision close-out 9117.24 -> 9111.77 (crutches 31.50 replace 64.00 x 58.5% = 37.44; x 0.92);
  task 1 external-review close-out 2321.99 -> 2317.43 (sterile supplies 96.00 x 0.25 replace 96.00 x 0.30). Root skip figures
  9214.11 -> 9208.65 and 2357.06 -> 2352.50; final payer balances 2219.25 / 1757.81. Every other figure unchanged (11058.88 /
  38.30 / 312.56; 4044.57 / 12.33 / 45.00); cross-task exclusivity unchanged. Replay run only with --check.

### Round-7 sweep (scratch sweep.py): every valuation factor on both axes (quantity 1-8, unit charge 0.50-400.00), the
### surgical family with and without the paid case rate, the PPO CT/contrast package, and observation hours 0-72 at 20/40/68/120
### per hour for the case-rate (HMO Neenah), percentage (HMO Chilton) and hourly (PPO) tiers
| surgery_post_payment_refund | lab_schedule_method | 0300/85025 | qty 1-8 non-decreasing True | unit charge 0.50-400 non-decreasing True | never above family charges True |
| surgery_post_payment_refund | lab_schedule_method | 0300/80048 | qty 1-8 non-decreasing True | unit charge 0.50-400 non-decreasing True | never above family charges True |
| surgery_post_payment_refund | lab_schedule_method | 0300/85610 | qty 1-8 non-decreasing True | unit charge 0.50-400 non-decreasing True | never above family charges True |
| surgery_post_payment_refund | blood_bank_typing_handling | 0300/86900 | qty 1-8 non-decreasing True | unit charge 0.50-400 non-decreasing True | never above family charges True |
| surgery_post_payment_refund | blood_bank_typing_handling | 0300/86901 | qty 1-8 non-decreasing True | unit charge 0.50-400 non-decreasing True | never above family charges True |
| surgery_post_payment_refund | venipuncture_collection_fee | 0300/36415 | qty 1-8 non-decreasing True | unit charge 0.50-400 non-decreasing True | never above family charges True |
| surgery_post_payment_refund | preoperative_ecg_fee | 0730/93005 | qty 1-8 non-decreasing True | unit charge 0.50-400 non-decreasing True | never above family charges True |
| surgery_post_payment_refund | urinalysis_fee | 0300/81001 | qty 1-8 non-decreasing True | unit charge 0.50-400 non-decreasing True | never above family charges True |
| surgery_post_payment_refund | preoperative_chest_radiograph_fee | 0324/71046 | qty 1-8 non-decreasing True | unit charge 0.50-400 non-decreasing True | never above family charges True |
| surgery_small_item_closeout | surgery_antiemetic_unit_rate | 0636/J2405 | qty 1-8 non-decreasing True | unit charge 0.50-400 non-decreasing True | never above family charges True |
| surgery_small_item_closeout | steroid_unit_rate | 0636/J1100 | qty 1-8 non-decreasing True | unit charge 0.50-400 non-decreasing True | never above family charges True |
| surgery_small_item_closeout | cefazolin_pricing | 0636/J0690 | qty 1-8 non-decreasing True | unit charge 0.50-400 non-decreasing True | never above family charges True |
| surgery_small_item_closeout | splint_pricing | 0270/A4570 | qty 1-8 non-decreasing True | unit charge 0.50-400 non-decreasing True | never above family charges True |
| surgery_small_item_closeout | surgery_iv_solution_unit_rate | 0258/J7050 | qty 1-8 non-decreasing True | unit charge 0.50-400 non-decreasing True | never above family charges True |
| noncovered_convenience_closeout | cold_therapy_unit_valuation | 0274/E0218 | qty 1-8 non-decreasing True | unit charge 0.50-400 non-decreasing True | never above family charges True |
| noncovered_convenience_closeout | cold_pack_quantity_share | 0274/A9273 | qty 1-8 non-decreasing True | unit charge 0.50-400 non-decreasing True | never above family charges True |
| noncovered_convenience_closeout | support_garment_quantity_share | 0274/A4467 | qty 1-8 non-decreasing True | unit charge 0.50-400 non-decreasing True | never above family charges True |
| member_decision_closeout | surgical_pricing_method (packages ancillaries when the case rate is paid) | 0360/all | qty 1-8 non-decreasing True | unit charge 0.50-400 non-decreasing True | never above family charges True |
| member_decision_closeout | surgical_pricing_method (packages ancillaries when the case rate is paid) | 0250/all | qty 1-8 non-decreasing True | unit charge 0.50-400 non-decreasing True | never above family charges True |
| member_decision_closeout | surgical_pricing_method (packages ancillaries when the case rate is paid) | 0272/all | qty 1-8 non-decreasing True | unit charge 0.50-400 non-decreasing True | never above family charges True |
| member_decision_closeout | implant_pricing_method | 0278/C1713 | qty 1-8 non-decreasing True | unit charge 0.50-400 non-decreasing True | never above family charges True |
| member_decision_closeout | implant_pricing_method | 0278/C1762 | qty 1-8 non-decreasing True | unit charge 0.50-400 non-decreasing True | never above family charges True |
| member_decision_closeout | anesthesia_unit_rate | 0370/all | qty 1-8 non-decreasing True | unit charge 0.50-400 non-decreasing True | never above family charges True |
| member_decision_closeout | recovery_room_unit_rate | 0710/all | qty 1-8 non-decreasing True | unit charge 0.50-400 non-decreasing True | never above family charges True |
| member_decision_closeout | crutch_take_home_rate | 0274/E0114 | qty 1-8 non-decreasing True | unit charge 0.50-400 non-decreasing True | never above family charges True |
| member_decision_closeout | surgical_pricing_method (packages ancillaries when the case rate is paid) [no 29882: case rate not paid] | 0360/all | qty 1-8 non-decreasing True | unit charge 0.50-400 non-decreasing True | never above family charges True |
| member_decision_closeout | surgical_pricing_method (packages ancillaries when the case rate is paid) [no 29882: case rate not paid] | 0250/all | qty 1-8 non-decreasing True | unit charge 0.50-400 non-decreasing True | never above family charges True |
| member_decision_closeout | surgical_pricing_method (packages ancillaries when the case rate is paid) [no 29882: case rate not paid] | 0272/all | qty 1-8 non-decreasing True | unit charge 0.50-400 non-decreasing True | never above family charges True |
| retrospective_denial_refund | echocardiogram_contract_fee | 0483/93306 | qty 1-8 non-decreasing True | unit charge 0.50-400 non-decreasing True | never above family charges True |
| retrospective_denial_refund | ecg_tracings_counted | 0730/93005 | qty 1-8 non-decreasing True | unit charge 0.50-400 non-decreasing True | never above family charges True |
| retrospective_denial_refund | retained_lab_pricing | 0300/84484 | qty 1-8 non-decreasing True | unit charge 0.50-400 non-decreasing True | never above family charges True |
| retrospective_denial_refund | retained_lab_pricing | 0300/85025 | qty 1-8 non-decreasing True | unit charge 0.50-400 non-decreasing True | never above family charges True |
| retrospective_denial_refund | retained_lab_pricing | 0300/80053 | qty 1-8 non-decreasing True | unit charge 0.50-400 non-decreasing True | never above family charges True |
| retrospective_denial_refund | ct_angiography_pricing + contrast_handling (CT rate packages contrast on PPO) | 0350/71275 | qty 1-8 non-decreasing True | unit charge 0.50-400 non-decreasing True | never above family charges True |
| retrospective_denial_refund | ct_angiography_pricing + contrast_handling (CT rate packages contrast on PPO) | 0636/Q9967 | qty 1-8 non-decreasing True | unit charge 0.50-400 non-decreasing True | never above family charges True |
| observation_small_item_closeout | observation_antiemetic_unit_rate | 0636/J2405 | qty 1-8 non-decreasing True | unit charge 0.50-400 non-decreasing True | never above family charges True |
| observation_small_item_closeout | ketorolac_pricing | 0636/J1885 | qty 1-8 non-decreasing True | unit charge 0.50-400 non-decreasing True | never above family charges True |
| observation_small_item_closeout | observation_iv_solution_unit_rate | 0258/J7050 | qty 1-8 non-decreasing True | unit charge 0.50-400 non-decreasing True | never above family charges True |
| observation_small_item_closeout | saline_flush_unit_rate | 0270/A4216 | qty 1-8 non-decreasing True | unit charge 0.50-400 non-decreasing True | never above family charges True |
| self_administered_drug_closeout | oral_drug_quantity_share | 0637/J8499 | qty 1-8 non-decreasing True | unit charge 0.50-400 non-decreasing True | never above family charges True |
| self_administered_drug_closeout | oral_dexamethasone_quantity_share | 0637/J8540 | qty 1-8 non-decreasing True | unit charge 0.50-400 non-decreasing True | never above family charges True |
| self_administered_drug_closeout | inhalation_unit_dose_quantity_share | 0637/J7613 | qty 1-8 non-decreasing True | unit charge 0.50-400 non-decreasing True | never above family charges True |
| self_administered_drug_closeout | sad_pharmacy_dispensing_fee | 0637/all | qty 1-8 non-decreasing True | unit charge 0.50-400 non-decreasing True | never above family charges True |
| external_review_decision_closeout | observation_pricing_method (packages general pharmacy when the case rate is paid) | 0762/G0378 | qty 1-8 non-decreasing True | unit charge 0.50-400 non-decreasing True | never above family charges True |
| external_review_decision_closeout | observation_pricing_method (packages general pharmacy when the case rate is paid) | 0250/all | qty 1-8 non-decreasing True | unit charge 0.50-400 non-decreasing True | never above family charges True |
| external_review_decision_closeout | infusion_contract_fee | 0260/96365 | qty 1-8 non-decreasing True | unit charge 0.50-400 non-decreasing True | never above family charges True |
| external_review_decision_closeout | heparin_unit_rate | 0636/J1644 | qty 1-8 non-decreasing True | unit charge 0.50-400 non-decreasing True | never above family charges True |
| external_review_decision_closeout | medical_surgical_supply_percentage | 0270/all | qty 1-8 non-decreasing True | unit charge 0.50-400 non-decreasing True | never above family charges True |
| external_review_decision_closeout | sterile_supply_percentage | 0272/all | qty 1-8 non-decreasing True | unit charge 0.50-400 non-decreasing True | never above family charges True |
| retrospective_denial_refund | ct_angiography_pricing + contrast_handling (CT rate packages contrast on PPO) [PPO: contrast packaged into the CT rate] | 0350/71275 | qty 1-8 non-decreasing True | unit charge 0.50-400 non-decreasing True | never above family charges True |
| retrospective_denial_refund | ct_angiography_pricing + contrast_handling (CT rate packages contrast on PPO) [PPO: contrast packaged into the CT rate] | 0636/Q9967 | qty 1-8 non-decreasing True | unit charge 0.50-400 non-decreasing True | never above family charges True |
| external_review_decision_closeout | observation hours 0-72 at 20.00/hour [HMO Neenah: case rate] | 0762/G0378 + 0250 | packaged family non-decreasing True | close-out non-decreasing True | never above packaged charges True | 0h:96.72 7h:326.00 8h:346.00 23h:646.00 24h:666.00 47h:1126.00 48h:1146.00 72h:1626.00 |
| external_review_decision_closeout | observation hours 0-72 at 40.00/hour [HMO Neenah: case rate] | 0762/G0378 + 0250 | packaged family non-decreasing True | close-out non-decreasing True | never above packaged charges True | 0h:96.72 7h:466.00 8h:506.00 23h:1106.00 24h:1146.00 47h:2066.00 48h:2106.00 72h:2640.00 |
| external_review_decision_closeout | observation hours 0-72 at 68.00/hour [HMO Neenah: case rate] | 0762/G0378 + 0250 | packaged family non-decreasing True | close-out non-decreasing True | never above packaged charges True | 0h:96.72 7h:662.00 8h:730.00 23h:1460.00 24h:1818.00 47h:2150.00 48h:2640.00 72h:2640.00 |
| external_review_decision_closeout | observation hours 0-72 at 120.00/hour [HMO Neenah: case rate] | 0762/G0378 + 0250 | packaged family non-decreasing True | close-out non-decreasing True | never above packaged charges True | 0h:96.72 7h:980.00 8h:1146.00 23h:1460.00 24h:2150.00 47h:2150.00 48h:2640.00 72h:2640.00 |
| external_review_decision_closeout | observation hours 0-72 at 20.00/hour [HMO Chilton: percentage, pharmacy valued] | 0762/G0378 + 0250 | packaged family non-decreasing True | close-out non-decreasing True | never above packaged charges True | 0h:96.72 7h:169.52 8h:179.92 23h:335.92 24h:346.32 47h:585.52 48h:595.92 72h:845.52 |
| external_review_decision_closeout | observation hours 0-72 at 40.00/hour [HMO Chilton: percentage, pharmacy valued] | 0762/G0378 + 0250 | packaged family non-decreasing True | close-out non-decreasing True | never above packaged charges True | 0h:96.72 7h:242.32 8h:263.12 23h:575.12 24h:595.92 47h:1074.32 48h:1095.12 72h:1594.32 |
| external_review_decision_closeout | observation hours 0-72 at 68.00/hour [HMO Chilton: percentage, pharmacy valued] | 0762/G0378 + 0250 | packaged family non-decreasing True | close-out non-decreasing True | never above packaged charges True | 0h:96.72 7h:344.24 8h:379.60 23h:910.00 24h:945.36 47h:1758.64 48h:1794.00 72h:2642.64 |
| external_review_decision_closeout | observation hours 0-72 at 120.00/hour [HMO Chilton: percentage, pharmacy valued] | 0762/G0378 + 0250 | packaged family non-decreasing True | close-out non-decreasing True | never above packaged charges True | 0h:96.72 7h:533.52 8h:595.92 23h:1531.92 24h:1594.32 47h:3029.52 48h:3091.92 72h:4589.52 |
| external_review_decision_closeout | observation hours 0-72 at 20.00/hour [PPO: hourly] | 0762/G0378 + 0250 | packaged family non-decreasing True | close-out non-decreasing True | never above packaged charges True | 0h:108.81 7h:248.81 8h:268.81 23h:568.81 24h:588.81 47h:1048.81 48h:1068.81 72h:1548.81 |
| external_review_decision_closeout | observation hours 0-72 at 40.00/hour [PPO: hourly] | 0762/G0378 + 0250 | packaged family non-decreasing True | close-out non-decreasing True | never above packaged charges True | 0h:108.81 7h:388.81 8h:428.81 23h:1028.81 24h:1068.81 47h:1988.81 48h:2028.81 72h:2892.81 |
| external_review_decision_closeout | observation hours 0-72 at 68.00/hour [PPO: hourly] | 0762/G0378 + 0250 | packaged family non-decreasing True | close-out non-decreasing True | never above packaged charges True | 0h:108.81 7h:514.81 8h:572.81 23h:1442.81 24h:1500.81 47h:2834.81 48h:2892.81 72h:2892.81 |
| external_review_decision_closeout | observation hours 0-72 at 120.00/hour [PPO: hourly] | 0762/G0378 + 0250 | packaged family non-decreasing True | close-out non-decreasing True | never above packaged charges True | 0h:108.81 7h:514.81 8h:572.81 23h:1442.81 24h:1500.81 47h:2834.81 48h:2892.81 72h:2892.81 |
### Round-7 probes
| cross | task 0 policies on task 1 root world | 0.00 / 0.00 / 0.00 / 0.00 |
| cross | task 1 policies on task 0 root world | 0.00 / 0.00 / 0.00 / 0.00 |
| gold | task 0 / task 1 handling-time values | 11058.88 / 38.30 / 312.56 / 9111.77 ; 4044.57 / 12.33 / 45.00 / 2317.43 |
| gold | root skip figures (refund / small items / non-covered) | 0.00 / 9208.65 / 9111.77 ; 0.00 / 2352.50 / 2317.43 |
| gold | final payer balances | 2219.25 / 1757.81 |
REWORK round 7: gates 7/7 green

## REWORK round 8 (2026-10-21) — audit revision_7 (0.md, 1.md, _difficulty.md read in full)
### Item-by-item response (item -> what changed -> where)
- F13 (CT angiography priced by the presence of a separate contrast line) -> claim_ext_retrospective_denial_refund:
  ct_angiography_pricing is replaced by ct_angiography_code_rate (parameter): 71275, whose descriptor includes contrast, is
  valued at its billed units times its per-code rate (cta_fee_hmo on HMO, cta_fee_ppo on PPO, otherwise charges per unit x the
  expected allowed percentage) whether or not a Q9967 line is billed, never above its charges plus the charges of any contrast
  the rate packages. contrast_handling now follows the payer's rule for the supply line itself: per millilitre on HMO;
  packaged into the scan's per-code rate on PPO only when a computed tomography scan is billed (the rate that packages it is
  paid); otherwise the expected allowed percentage. Binding ct_method renamed cta_rate.
- Class sweep of every code-keyed tier in the charter (a code's price switched by another separately billed line, or a
  descriptor priced inconsistently):
  | policy | tier | keyed on | verdict |
  | claim_ext_retrospective_denial_refund | CT angiography rate (71275) | another line (Q9967) | FIXED (F13): per-code rate by payer class |
  | claim_ext_retrospective_denial_refund | contrast HMO tier | another line (CT, 0350) | FIXED: per millilitre on HMO with or without a scan |
  | claim_ext_retrospective_denial_refund | contrast PPO tier | the CT scan whose rate packages it | KEPT: packaging only into a rate that is paid (round-7 rule) |
  | claim_ext_surgery_post_payment_refund | typing HMO tier | another line (29881/29882) | FIXED (task 0, forced by the sweep): per-test fee on HMO whatever the procedure |
  | claim_ext_surgery_post_payment_refund | typing PPO tier | 29882, the code whose case rate packages typing | KEPT: packaging into a paid case rate |
  | claim_ext_surgery_small_item_closeout | cefazolin (J0690) | another line (29881/29882) | FIXED (task 0, forced by the sweep): cefazolin_unit_rate (parameter), per-code rate by payer class |
  | claim_ext_member_decision_closeout | arthroscopy case rate | 29882 itself | KEPT: the code's own rate |
  | claim_ext_member_decision_closeout | ancillaries | the paid 29882 case rate | KEPT: packaging into a paid case rate |
  | claim_ext_noncovered_convenience_closeout | take_home_kit_share | which kit codes are billed together | KEPT: the kit's own bundle price (the only co-billing reader; judged real in revision_5) |
  | claim_ext_external_review_decision_closeout | general pharmacy | the paid observation case rate (G0378 hours) | KEPT: packaging into a paid case rate |
  | all other tiers | payer class, campus, account class, own units, own charges, dispensing pharmacy | no other line | none in the class |
  Descriptor check: the only with/without-contrast code in the charter is 71275 (CT angiography, contrast included), now priced
  at its per-code rate; no without-contrast code is billed or priced.
- Gold moves: none. Every figure is unchanged (11058.88 / 38.30 / 312.56 / 9111.77; 4044.57 / 12.33 / 45.00 / 2317.43);
  factor_sensitivity and baseline figures unchanged; renamed factors carry the same figures (cefazolin_unit_rate 59.98,
  ct_angiography_code_rate 2976.97). Task 0's charter text and tasks/0.json changed only in the renamed cefazolin factor, its
  tier labels and the typing HMO tier label (forced by the sweep). Replay run only with --check.

### Round-8 probes (CT/contrast joint grid, code-price independence, exclusivity)
| task 1 | refund, Commercial HMO Claim, 71275 charge 0.00, contrast 0/1/10/50/80/200 ml | refund non-increasing as contrast is added: True | 4820.17 4819.75 4815.97 4799.17 4786.57 4736.17 |
| task 1 | refund, Commercial HMO Claim, 71275 charge 500.00, contrast 0/1/10/50/80/200 ml | refund non-increasing as contrast is added: True | 4320.17 4319.75 4315.97 4299.17 4286.57 4236.17 |
| task 1 | refund, Commercial HMO Claim, 71275 charge 3480.00, contrast 0/1/10/50/80/200 ml | refund non-increasing as contrast is added: True | 4078.17 4077.75 4073.97 4057.17 4044.57 3994.17 |
| task 1 | refund, Commercial HMO Claim, 71275 charge 6000.00, contrast 0/1/10/50/80/200 ml | refund non-increasing as contrast is added: True | 4078.17 4077.75 4073.97 4057.17 4044.57 3994.17 |
| task 1 | refund, Commercial PPO Claim, 71275 charge 0.00, contrast 0/1/10/50/80/200 ml | refund non-increasing as contrast is added: True | 4661.46 4660.82 4655.03 4629.29 4609.98 4532.76 |
| task 1 | refund, Commercial PPO Claim, 71275 charge 500.00, contrast 0/1/10/50/80/200 ml | refund non-increasing as contrast is added: True | 4161.46 4160.36 4150.46 4106.46 4073.46 3941.46 |
| task 1 | refund, Commercial PPO Claim, 71275 charge 3480.00, contrast 0/1/10/50/80/200 ml | refund non-increasing as contrast is added: True | 3863.46 3863.46 3863.46 3863.46 3863.46 3863.46 |
| task 1 | refund, Commercial PPO Claim, 71275 charge 6000.00, contrast 0/1/10/50/80/200 ml | refund non-increasing as contrast is added: True | 3863.46 3863.46 3863.46 3863.46 3863.46 3863.46 |
| task 1 | refund, Marketplace Exchange Plan Claim, 71275 charge 0.00, contrast 0/1/10/50/80/200 ml | refund non-increasing as contrast is added: True | 4231.07 4230.55 4225.85 4204.95 4189.27 4126.57 |
| task 1 | refund, Marketplace Exchange Plan Claim, 71275 charge 500.00, contrast 0/1/10/50/80/200 ml | refund non-increasing as contrast is added: True | 3993.57 3993.05 3988.35 3967.45 3951.77 3889.07 |
| task 1 | refund, Marketplace Exchange Plan Claim, 71275 charge 3480.00, contrast 0/1/10/50/80/200 ml | refund non-increasing as contrast is added: True | 2578.07 2577.55 2572.85 2551.95 2536.27 2473.57 |
| task 1 | refund, Marketplace Exchange Plan Claim, 71275 charge 6000.00, contrast 0/1/10/50/80/200 ml | refund non-increasing as contrast is added: True | 1381.07 1380.55 1375.85 1354.95 1339.27 1276.57 |
| task 1 | refund Commercial HMO Claim with / without the contrast line (CT at its per-code rate either way; HMO contrast paid per ml) | | 4044.57 / 4078.17 |
| task 1 | refund Commercial PPO Claim with / without the contrast line (CT at its per-code rate either way; HMO contrast paid per ml) | | 3863.46 / 3863.46 |
| task 0 | small items Commercial PPO Claim with / without an arthroscopy line (cefazolin per-code rate either way) | | 38.30 / 38.30 |
| task 0 | small items Commercial HMO Claim with / without an arthroscopy line (cefazolin per-code rate either way) | | 42.64 / 42.64 |
| summary | refund grid flags | 0 | |
| cross | task 0 policies on task 1 root world | 0.00 / 0.00 / 0.00 / 0.00 | |
| cross | task 1 policies on task 0 root world | 0.00 / 0.00 / 0.00 / 0.00 | |
| gold | task 0 / task 1 | 11058.88 / 38.30 / 312.56 / 9111.77 ; 4044.57 / 12.33 / 45.00 / 2317.43 | |
REWORK round 8: gates 7/7 green

## REWORK round 9 (2026-10-21) — audit revision_8 (0.md, 1.md, _difficulty.md read in full)
### Item-by-item response (item -> what changed -> where)
- F14 (PPO contrast packaged into any CT line, though only 71275 has a per-code rate) -> claim_ext_retrospective_denial_refund
  contrast_handling: the PPO tier now packages the contrast only when the CT angiography (71275) is billed — the only scan
  priced at a per-code rate covering the contrast (rule: "is packaged into the CT angiography's per-code rate, and carries no
  value of its own, on a Commercial PPO claim that bills the CT angiography (71275), the only scan priced at a per-code rate
  covering the contrast"); with any other CT line, or none, the contrast is valued as its own rule says (the expected allowed
  percentage). The CT angiography's cap already includes the contrast charges exactly when this tier packages them.
- Packaging re-check (every packaging tier, condition: the absorbing line is itself priced at a rate covering the packaged item):
  | policy | packaged item | absorbing rate | condition in compute | verdict |
  | claim_ext_retrospective_denial_refund | contrast Q9967 (PPO) | 71275 per-code rate | PPO AND 71275 billed (was: any 0350 line) | FIXED |
  | claim_ext_member_decision_closeout | ancillaries 0250/0272 | arthroscopy case rate (PPO, 29882) | surgical_method == 2 (the case-rate tier itself) | holds |
  | claim_ext_surgery_post_payment_refund | typing 86900/86901 (PPO) | the same arthroscopy case rate | PPO AND 29882 billed = the case-rate tier's condition | holds |
  | claim_ext_external_review_decision_closeout | general pharmacy 0250 | observation case rate (HMO, hospital campus, hours billed) | obs_method == 2 AND obs_hours > 0 | holds |
  No other rule packages a line.
- Gold moves: none; task files untouched (tasks/0.json and tasks/1.json byte-identical), every figure unchanged
  (11058.88 / 38.30 / 312.56 / 9111.77; 4044.57 / 12.33 / 45.00 / 2317.43). Replay run only with --check.

### Round-9 probes (contrast on PPO / HMO / Marketplace with CT 71275, another CT 70450, or no CT)
| task 1 refund | Commercial PPO Claim, CT line 71275, 80 ml contrast vs no contrast | contrast retained value 0.00 | refund 3863.46 / 3863.46 |
| task 1 refund | Commercial PPO Claim, CT line 70450, 80 ml contrast vs no contrast | contrast retained value 51.48 | refund 4024.98 / 4076.46 |
| task 1 refund | Commercial PPO Claim, CT line none, 80 ml contrast vs no contrast | contrast retained value 51.48 | refund 4609.98 / 4661.46 |
| task 1 refund | Commercial HMO Claim, CT line 71275, 80 ml contrast vs no contrast | contrast retained value 33.60 | refund 4044.57 / 4078.17 |
| task 1 refund | Commercial HMO Claim, CT line 70450, 80 ml contrast vs no contrast | contrast retained value 33.60 | refund 4266.57 / 4300.17 |
| task 1 refund | Commercial HMO Claim, CT line none, 80 ml contrast vs no contrast | contrast retained value 33.60 | refund 4786.57 / 4820.17 |
| task 1 refund | Marketplace Exchange Plan Claim, CT line 71275, 80 ml contrast vs no contrast | contrast retained value 41.80 | refund 2536.27 / 2578.07 |
| task 1 refund | Marketplace Exchange Plan Claim, CT line 70450, 80 ml contrast vs no contrast | contrast retained value 41.80 | refund 3714.27 / 3756.07 |
| task 1 refund | Marketplace Exchange Plan Claim, CT line none, 80 ml contrast vs no contrast | contrast retained value 41.80 | refund 4189.27 / 4231.07 |
| gold (task files, unchanged) | 11058.88 / 38.30 / 312.56 / 9111.77 ; 4044.57 / 12.33 / 45.00 / 2317.43 | | |
REWORK round 9: gates 7/7 green

## REWORK round 10 (2026-10-21) — renderer findings audits/render_source/insurance_claims_and_denials/render_r1.md (read in full)
### Item-by-item response (item -> what changed -> where)
1. ECG per-line vs total cap; uncapped ECG value -> claim_ext_retrospective_denial_refund ecg_tracings_counted: the rule now
   states the total cap the compute applies ("no more than ecg_cap_per_line times its number of lines"); the tracing value is
   MN(ecg charges, counted x charges per counted unit x pct) — never above its charges; counted units are the billed units,
   or one for a line billed with charges but no units (baseline = charges x pct exactly).
2. CT rate depending on the contrast factor -> ct_value = MN(71275 charges, counted units x cta_rate): the CT factor reads
   only its own lines ("never above its own charges, whether or not a separate contrast line is billed"); contrast_handling
   alone decides the contrast line's value (per millilitre on HMO when millilitres are billed; no value on PPO when 71275 is
   billed; otherwise the percentage); the two are combined only by the generic assembly sentence.
3. Pre-operative tests defined twice -> claim_ext_surgery_post_payment_refund: the definition now reads "every charge under
   revenue codes 0300 (laboratory tests, blood-bank typing and specimen collection), 0730 (electrocardiogram tracings) and
   0324 (chest radiographs)", matching the reading sentence and other_retained.
4. Baseline naming factor-only quantities (all 8) -> every reading sentence in a baseline now reads the lines "by their
   charges" only; the billed units, numbers of lines and observation hours are named in the sentence of the one factor that
   uses them (lab schedule, typing, splint, ketorolac, cold-therapy unit, quantity shares, surgical and implant methods, rate
   factors, tracing count, contrast, dispensing fee, observation pricing), and their compute_basis quotes those sentences.
   The two combination sentences that named factor quantities (member-decision and external-review "the value is the ...
   plus ...") are removed; the generic assembly sentence carries the combination (recipe A3).
5. Zero/empty edges -> every per-unit rate's fall-through is now "its charges per counted unit times the expected allowed
   percentage", the family is valued at counted units times the rate (never above its charges), counted units being the
   billed units or one when a code is billed with charges but no units — so the fall-through equals the baseline's "charges x
   expected allowed percentage" at every input (18 rate factors in P1, P2, P4, P5, P6, P8; compute MX(units, 1)); the HMO
   contrast tier now applies only "on a Commercial HMO claim that bills its millilitres" (compute: Q9967 units > 0),
   otherwise the percentage.
6. Self-administered drug cap/lines and unrecorded framing -> the cap and the dispensing-line count now read only the three
   codes the rule names (J8499, J8540, J7613); the dispensing fee is worded as the record tests the compute uses ("on an
   Observation Stay Account at a hospital campus", "on an Emergency Department Visit Account at such a campus"); factor
   renamed sad_dispensing_fee, params fee_observation_line / fee_emergency_visit.
- Found during the sweep (false proof text): the tier_taken label of cold_pack_quantity_share in tasks/0.json and of the two
  J8540/J7613 quantity shares in tasks/1.json named the 4+/6+ tier although the worlds take the 2-3 / 2-5 tier; corrected
  (tasks/0.json changes only in that label — forced; no value changes).

### Class sweep (all 8 policies, one pass per class)
| class | result |
| per-line vs total caps | P5 ECG fixed; P8 obs_hour_cap is a per-stay cap and is stated so; P3 E0218 fee per line and P7 fee per line multiply the line count (no per-line cap) — none other |
| factor-to-factor dependence | P5 CT/contrast fixed; packaging in P4 (ancillaries) and P8 (pharmacy) sits inside the single factor that owns both families; P3 kit share and P7 account-class factor are whole-value multipliers in the generic assembly; scratch xf.py coupling check clean |
| definitions stated twice | P1 pre-operative tests fixed; P4/P8 exclusions match P1/P5 definitions; P2/P6 small-item test stated identically in the small-item and close-out rules; P7 drug set now matches cap and lines |
| baseline naming factor-only inputs | fixed in all 8 (item 4) |
| zero/empty edges | fixed for every rate fall-through and the HMO contrast tier (item 5); non-baseline method tiers state their own "billed units times fee" (0.00 with no units, as worded); quantity shares fall through to 1 (charges) |
| framing on unrecorded facts | P7 pharmacy/cabinet wording fixed; P5 "contrast agent billed with it" now "the contrast supply line"; no other rule refers to a fact no record holds |
- Gold moves: none (11058.88 / 38.30 / 312.56 / 9111.77; 4044.57 / 12.33 / 45.00 / 2317.43); factor_sensitivity and baseline
  figures unchanged. Replay run only with --check.

### Round-10 sweep (scratch sweep.py): monotone/cap regression and zero-unit edge
Note on "differs" rows: the convenience and self-administered drug baselines are the charges themselves (value = charges, as
stated), the dispensing fee has no baseline amount (0.00 at Chilton), and the 0270 supply family excludes the listed flush
(142.00 x pct) — each agrees with its rule.
| surgery_post_payment_refund | lab_schedule_method | quantity 1-8 non-decreasing True | unit charge 0.50-400 non-decreasing True | never above family charges True |
| surgery_post_payment_refund | blood_bank_typing_handling | quantity 1-8 non-decreasing True | unit charge 0.50-400 non-decreasing True | never above family charges True |
| surgery_post_payment_refund | venipuncture_collection_fee | quantity 1-8 non-decreasing True | unit charge 0.50-400 non-decreasing True | never above family charges True |
| surgery_post_payment_refund | preoperative_ecg_fee | quantity 1-8 non-decreasing True | unit charge 0.50-400 non-decreasing True | never above family charges True |
| surgery_post_payment_refund | urinalysis_fee | quantity 1-8 non-decreasing True | unit charge 0.50-400 non-decreasing True | never above family charges True |
| surgery_post_payment_refund | preoperative_chest_radiograph_fee | quantity 1-8 non-decreasing True | unit charge 0.50-400 non-decreasing True | never above family charges True |
| surgery_small_item_closeout | surgery_antiemetic_unit_rate | quantity 1-8 non-decreasing True | unit charge 0.50-400 non-decreasing True | never above family charges True |
| surgery_small_item_closeout | steroid_unit_rate | quantity 1-8 non-decreasing True | unit charge 0.50-400 non-decreasing True | never above family charges True |
| surgery_small_item_closeout | cefazolin_unit_rate | quantity 1-8 non-decreasing True | unit charge 0.50-400 non-decreasing True | never above family charges True |
| surgery_small_item_closeout | splint_pricing | quantity 1-8 non-decreasing True | unit charge 0.50-400 non-decreasing True | never above family charges True |
| surgery_small_item_closeout | surgery_iv_solution_unit_rate | quantity 1-8 non-decreasing True | unit charge 0.50-400 non-decreasing True | never above family charges True |
| noncovered_convenience_closeout | cold_therapy_unit_valuation | quantity 1-8 non-decreasing True | unit charge 0.50-400 non-decreasing True | never above family charges True |
| noncovered_convenience_closeout | cold_pack_quantity_share | quantity 1-8 non-decreasing True | unit charge 0.50-400 non-decreasing True | never above family charges True |
| noncovered_convenience_closeout | support_garment_quantity_share | quantity 1-8 non-decreasing True | unit charge 0.50-400 non-decreasing True | never above family charges True |
| member_decision_closeout | surgical_pricing_method | quantity 1-8 non-decreasing True | unit charge 0.50-400 non-decreasing True | never above family charges True |
| member_decision_closeout | implant_pricing_method | quantity 1-8 non-decreasing True | unit charge 0.50-400 non-decreasing True | never above family charges True |
| member_decision_closeout | anesthesia_unit_rate | quantity 1-8 non-decreasing True | unit charge 0.50-400 non-decreasing True | never above family charges True |
| member_decision_closeout | recovery_room_unit_rate | quantity 1-8 non-decreasing True | unit charge 0.50-400 non-decreasing True | never above family charges True |
| member_decision_closeout | crutch_take_home_rate | quantity 1-8 non-decreasing True | unit charge 0.50-400 non-decreasing True | never above family charges True |
| retrospective_denial_refund | echocardiogram_contract_fee | quantity 1-8 non-decreasing True | unit charge 0.50-400 non-decreasing True | never above family charges True |
| retrospective_denial_refund | ecg_tracings_counted | quantity 1-8 non-decreasing True | unit charge 0.50-400 non-decreasing True | never above family charges True |
| retrospective_denial_refund | retained_lab_pricing | quantity 1-8 non-decreasing True | unit charge 0.50-400 non-decreasing True | never above family charges True |
| retrospective_denial_refund | ct_angiography_code_rate | quantity 1-8 non-decreasing True | unit charge 0.50-400 non-decreasing True | never above family charges True |
| retrospective_denial_refund | contrast_handling | quantity 1-8 non-decreasing True | unit charge 0.50-400 non-decreasing True | never above family charges True |
| observation_small_item_closeout | observation_antiemetic_unit_rate | quantity 1-8 non-decreasing True | unit charge 0.50-400 non-decreasing True | never above family charges True |
| observation_small_item_closeout | ketorolac_pricing | quantity 1-8 non-decreasing True | unit charge 0.50-400 non-decreasing True | never above family charges True |
| observation_small_item_closeout | observation_iv_solution_unit_rate | quantity 1-8 non-decreasing True | unit charge 0.50-400 non-decreasing True | never above family charges True |
| observation_small_item_closeout | saline_flush_unit_rate | quantity 1-8 non-decreasing True | unit charge 0.50-400 non-decreasing True | never above family charges True |
| self_administered_drug_closeout | oral_drug_quantity_share | quantity 1-8 non-decreasing True | unit charge 0.50-400 non-decreasing True | never above family charges True |
| self_administered_drug_closeout | oral_dexamethasone_quantity_share | quantity 1-8 non-decreasing True | unit charge 0.50-400 non-decreasing True | never above family charges True |
| self_administered_drug_closeout | inhalation_unit_dose_quantity_share | quantity 1-8 non-decreasing True | unit charge 0.50-400 non-decreasing True | never above family charges True |
| self_administered_drug_closeout | sad_dispensing_fee | quantity 1-8 non-decreasing True | unit charge 0.50-400 non-decreasing True | never above family charges True |
| external_review_decision_closeout | observation_pricing_method | quantity 1-8 non-decreasing True | unit charge 0.50-400 non-decreasing True | never above family charges True |
| external_review_decision_closeout | infusion_contract_fee | quantity 1-8 non-decreasing True | unit charge 0.50-400 non-decreasing True | never above family charges True |
| external_review_decision_closeout | heparin_unit_rate | quantity 1-8 non-decreasing True | unit charge 0.50-400 non-decreasing True | never above family charges True |
| external_review_decision_closeout | medical_surgical_supply_percentage | quantity 1-8 non-decreasing True | unit charge 0.50-400 non-decreasing True | never above family charges True |
| external_review_decision_closeout | sterile_supply_percentage | quantity 1-8 non-decreasing True | unit charge 0.50-400 non-decreasing True | never above family charges True |
#### zero-unit edge (Marketplace at Chilton, units 0): family value vs charges x expected allowed percentage
| surgery_post_payment_refund | lab_schedule_method | 0300/85025 | value 74.10 | charges x pct 74.10 | equal |
| surgery_post_payment_refund | lab_schedule_method | 0300/80048 | value 74.10 | charges x pct 74.10 | equal |
| surgery_post_payment_refund | lab_schedule_method | 0300/85610 | value 74.10 | charges x pct 74.10 | equal |
| surgery_post_payment_refund | blood_bank_typing_handling | 0300/86900 | value 28.50 | charges x pct 28.50 | equal |
| surgery_post_payment_refund | blood_bank_typing_handling | 0300/86901 | value 28.50 | charges x pct 28.50 | equal |
| surgery_post_payment_refund | venipuncture_collection_fee | 0300/36415 | value 8.55 | charges x pct 8.55 | equal |
| surgery_post_payment_refund | preoperative_ecg_fee | 0730/93005 | value 74.10 | charges x pct 74.10 | equal |
| surgery_post_payment_refund | urinalysis_fee | 0300/81001 | value 10.45 | charges x pct 10.45 | equal |
| surgery_post_payment_refund | preoperative_chest_radiograph_fee | 0324/71046 | value 127.30 | charges x pct 127.30 | equal |
| surgery_small_item_closeout | surgery_antiemetic_unit_rate | 0636/J2405 | value 17.10 | charges x pct 17.10 | equal |
| surgery_small_item_closeout | steroid_unit_rate | 0636/J1100 | value 11.40 | charges x pct 11.40 | equal |
| surgery_small_item_closeout | cefazolin_unit_rate | 0636/J0690 | value 22.80 | charges x pct 22.80 | equal |
| surgery_small_item_closeout | splint_pricing | 0270/A4570 | value 19.95 | charges x pct 19.95 | equal |
| surgery_small_item_closeout | surgery_iv_solution_unit_rate | 0258/J7050 | value 14.25 | charges x pct 14.25 | equal |
| noncovered_convenience_closeout | cold_therapy_unit_valuation | 0274/E0218 | value 590.00 | charges x pct 0.00 | differs (see note) |
| noncovered_convenience_closeout | cold_pack_quantity_share | 0274/A9273 | value 9.00 | charges x pct 0.00 | differs (see note) |
| noncovered_convenience_closeout | support_garment_quantity_share | 0274/A4467 | value 24.00 | charges x pct 0.00 | differs (see note) |
| member_decision_closeout | surgical_pricing_method | 0360/all | value 5652.50 | charges x pct 5652.50 | equal |
| member_decision_closeout | surgical_pricing_method | 0250/all | value 5652.50 | charges x pct 5652.50 | equal |
| member_decision_closeout | surgical_pricing_method | 0272/all | value 5652.50 | charges x pct 5652.50 | equal |
| member_decision_closeout | implant_pricing_method | 0278/C1713 | value 1824.00 | charges x pct 1824.00 | equal |
| member_decision_closeout | implant_pricing_method | 0278/C1762 | value 1824.00 | charges x pct 1824.00 | equal |
| member_decision_closeout | anesthesia_unit_rate | 0370/all | value 703.00 | charges x pct 703.00 | equal |
| member_decision_closeout | recovery_room_unit_rate | 0710/all | value 456.00 | charges x pct 456.00 | equal |
| member_decision_closeout | crutch_take_home_rate | 0274/E0114 | value 30.40 | charges x pct 30.40 | equal |
| retrospective_denial_refund | echocardiogram_contract_fee | 0483/93306 | value 1016.50 | charges x pct 1016.50 | equal |
| retrospective_denial_refund | ecg_tracings_counted | 0730/93005 | value 148.20 | charges x pct 148.20 | equal |
| retrospective_denial_refund | retained_lab_pricing | 0300/84484 | value 194.75 | charges x pct 194.75 | equal |
| retrospective_denial_refund | retained_lab_pricing | 0300/85025 | value 194.75 | charges x pct 194.75 | equal |
| retrospective_denial_refund | retained_lab_pricing | 0300/80053 | value 194.75 | charges x pct 194.75 | equal |
| retrospective_denial_refund | ct_angiography_code_rate | 0350/71275 | value 1653.00 | charges x pct 1653.00 | equal |
| retrospective_denial_refund | contrast_handling | 0636/Q9967 | value 41.80 | charges x pct 41.80 | equal |
| observation_small_item_closeout | observation_antiemetic_unit_rate | 0636/J2405 | value 8.55 | charges x pct 8.55 | equal |
| observation_small_item_closeout | ketorolac_pricing | 0636/J1885 | value 10.45 | charges x pct 10.45 | equal |
| observation_small_item_closeout | observation_iv_solution_unit_rate | 0258/J7050 | value 7.12 | charges x pct 7.12 | equal |
| observation_small_item_closeout | saline_flush_unit_rate | 0270/A4216 | value 7.60 | charges x pct 7.60 | equal |
| self_administered_drug_closeout | oral_drug_quantity_share | 0637/J8499 | value 60.00 | charges x pct 0.00 | differs (see note) |
| self_administered_drug_closeout | oral_dexamethasone_quantity_share | 0637/J8540 | value 12.00 | charges x pct 0.00 | differs (see note) |
| self_administered_drug_closeout | inhalation_unit_dose_quantity_share | 0637/J7613 | value 16.00 | charges x pct 0.00 | differs (see note) |
| self_administered_drug_closeout | sad_dispensing_fee | 0637/all | value 0.00 | charges x pct 0.00 | differs (see note) |
| external_review_decision_closeout | observation_pricing_method | 0762/G0378 | value 1574.15 | charges x pct 1574.15 | equal |
| external_review_decision_closeout | observation_pricing_method | 0250/all | value 1574.15 | charges x pct 1574.15 | equal |
| external_review_decision_closeout | infusion_contract_fee | 0260/96365 | value 304.95 | charges x pct 304.95 | equal |
| external_review_decision_closeout | heparin_unit_rate | 0636/J1644 | value 26.60 | charges x pct 26.60 | equal |
| external_review_decision_closeout | medical_surgical_supply_percentage | 0270/all | value 67.45 | charges x pct 75.05 | differs (see note) |
| external_review_decision_closeout | sterile_supply_percentage | 0272/all | value 45.60 | charges x pct 45.60 | equal |
### Round-10 probes
| cross | task 0 policies on task 1 root world | 0.00 / 0.00 / 0.00 / 0.00 |
| cross | task 1 policies on task 0 root world | 0.00 / 0.00 / 0.00 / 0.00 |
| gold | task 0 / task 1 | 11058.88 / 38.30 / 312.56 / 9111.77 ; 4044.57 / 12.33 / 45.00 / 2317.43 |
REWORK round 10: gates 7/7 green

## REWORK round 11 (policy_task revision_10: F15)
Read in full: audits/policy_task/insurance_claims_and_denials/0.md, 1.md, _difficulty.md (revisions 1-10). Open item: F15 only (task0=PASS, task1=PASS).

F15 (P5 contrast packaged into a 71275 rate capped at the scan's own charges) - closed, minimal edit in P5 only:
- The CT sentence and `ct_value = MN(cta_charges, MX(cta_units, 1) * cta_rate)` are unchanged; the CT factor still reads only its own lines.
- The contrast sentence's PPO tier now reads: "on a Commercial PPO claim that bills the CT angiography (71275), whose per-code rate is the only scan rate covering the contrast, is packaged into that rate, which is compared with the charges of the scan and the contrast together, and so keeps only the part of the CT angiography's counted units times cta_fee_ppo that the CT angiography's own charges leave unused, never above the contrast's own charges (0.00 when the CT angiography's charges reach that rate)". The same text is carried verbatim in the compute_basis of contrast_units, contrast_method, contrast_value and retained_value.
- The compute's PPO branch is `MX(0, MX(cta_units, 1) * K('cta_fee_ppo') - cta_charges)` inside the existing `MN(contrast_charges, ...)`. The contrast factor reads the CTA's recorded units and charges and the contract rate cta_fee_ppo as plain inputs. It reads no factor binding (cta_rate is not read). contrast_handling's ladder tier 2 method text is updated to match.
- Joint effect: on PPO, ct_value + contrast_value = MN(scan + contrast charges, counted units x cta_fee_ppo), which is the round-9 lesser-of over everything the rate absorbs. Note on the coordinator's wording "0.00 when the rate >= scan + contrast charges": taken literally, that would drop contrast the rate does cover. When the rate is at or above the combined charges, the contract pays both, so the contrast keeps its charges; it is 0.00 exactly when the scan's own charges reach the rate.
- Ordering: the combination sentences are unchanged ("replacements are made first, each never above the billed charges of the lines it values ..."). The contrast replacement is still capped at its own charges.

Joint CT x contrast x payer grid (task 1 world, P5 compute via check_compute.build_env):
| grid | points | result |
| --- | --- | --- |
| HMO / PPO / Marketplace x 71275 {none, 0.01 ... 6000} x units {1, 2} x Q9967 {0, 1, 10, 80, 200} ml, both axes | 810 | 0 falls of ct+contrast, 0 cap breaches (contrast <= its charges, ct+contrast <= scan+contrast charges) |
| adding a 71275 line (none -> any charge, units 1/2) at fixed contrast | 216 | 0 falls |
| PPO identity ct+contrast == MN(scan+contrast, units x 798.00) with 71275 billed | 182 | 0 mismatches |

Probe table (80 ml = 88.00 contrast unless stated; refund on the task-1 world):
| payer | 71275 charge | contrast | ct_value | contrast_value | refund |
| --- | --- | --- | --- | --- | --- |
| PPO | 3480.00 | 88.00 | 798.00 | 0.00 | 3863.46 |
| PPO | 700.00 | 88.00 | 700.00 | 88.00 (r10: 0.00) | 3873.46 |
| PPO | 500.00 | 88.00 | 500.00 | 88.00 (r10: 0.00) | 4073.46 |
| PPO | 100.00 | 200 ml 220.00 | 100.00 | 220.00 | 4341.46 (no CTA: 4532.76; r10: 4561.46) |
| PPO | none | 88.00 | 0.00 | 51.48 | 4609.98 |
| PPO | none + 70450 1000.00 | 88.00 | 0.00 | 51.48 | 4024.98 |
| PPO | 3480.00 + 70450 1000.00 | 88.00 | 798.00 | 0.00 | 3278.46 |
| HMO (task 1) | 3480.00 | 88.00 | 742.00 | 33.60 | 4044.57 |
| Marketplace | 3480.00 | 88.00 | 1653.00 | 41.80 | 2536.27 |

Regression:
- P5 line sweep (every charge line of the task-1 account x HMO/PPO/Marketplace, quantity 1-8 and unit charge 0.01-8000.00): 2205 points, 0 refund rises.
- P1-P4 and P6-P8 are untouched, so their monotonicity and cap sweeps are unchanged.
- Task 1 is on the HMO per-millilitre tier: 4044.57 / 12.33 / 45.00 / 2317.43. factor_sensitivity (contrast_handling 4032.41, ct_angiography_code_rate 2976.97) and the skips are unchanged.
- Task 0: 11058.88 / 38.30 / 312.56 / 9111.77.
- No gold move. tasks/0.json and tasks/1.json are byte-identical (4e988804d476, d47d32af4fe5). task_tools.py is unchanged.
- Cross-task exclusivity is unchanged (P5's gate needs an observation/ED account).
- XF re-check on P5: A1 holds (no factor reads another factor's binding); B11 compute_basis is verbatim; C14 tier shapes are distinct (units x rate / rate remainder vs own charges / percentage); E20/E21 are untouched.
Gates (replay with --check): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK.
REWORK round 11: gates 7/7 green

## REWORK round 12 (policy_task revision_11: F16)
Read in full: audits/policy_task/insurance_claims_and_denials/0.md, 1.md, _difficulty.md (revisions 1-11). Open item: F16 only (task0=PASS, task1=PASS). I took the coordinator route as given.

F16 (CT factor and contrast factor coupled through the PPO lesser-of) - closed, in P5 only:
- ONE method factor `ct_angiography_family_pricing` (binding cta_method) now owns the whole CT-angiography family, the scan 71275 plus its contrast Q9967, on every payer. It replaces `ct_angiography_code_rate` and `contrast_handling`. Its tiers:
  - PPO with 71275 billed: MN(scan + contrast charges, counted units x cta_fee_ppo).
  - HMO: MN(scan charges, counted units x cta_fee_hmo) + MN(contrast charges, millilitres x contrast_ml_hmo), or the contrast at the expected allowed percentage when no millilitres are billed.
  - Otherwise: the family's charges x the expected allowed percentage.
  - Baseline: method 0, the family's charges x the percentage, which is the baseline rule's "charges of the diagnostic tests multiplied by the payer class's expected allowed percentage".
- No other factor reads 71275, Q9967, cta_fee_hmo, cta_fee_ppo or contrast_ml_hmo. One family sentence replaces the old CT and contrast sentences, and it states the counted-units definition once. compute_basis for cta_units, contrast_units, cta_method, ct_family_value and retained_value quotes it verbatim. The bindings cta_rate, contrast_method, ct_value and contrast_value are removed.
- The draw keeps P5 at 6 factors (task 1 draw [6, 5, 4, 6]). I added ONE lever, `diagnostic_campus_factor` (parameter, binding dx_site):
  - It is a provider-based campus differential on the sum of the retained test values: dx_site_neenah 0.95 at Riverbend Lakeshore Hospital - Neenah, dx_site_cah 1.04 at Riverbend Community Hospital - Chilton, and 1 otherwise (Appleton).
  - It is keyed on encounter_accounts.facility, with the same campus differentials as the observation close-out's campus factor.
  - The assembly sentence keeps its order and only gains the multiplier step: "replacements are made first, each never above the billed charges ..., the multiplier then applies to their sum to give the retained value, never above the charges of the diagnostic tests, the deduction after it (never below 0.00), ...".
  - Compute: retained_value = MN(diagnostic charges, (sum of family values) x dx_site).

T1 (task 1 world, one factor at its baseline; gold 4121.86):
| factor | result at baseline | moves |
| --- | --- | --- |
| echocardiogram_contract_fee | 3646.10 | yes |
| ecg_tracings_counted | 4044.80 | yes |
| retained_lab_pricing | 3992.70 | yes |
| ct_angiography_family_pricing | 3096.09 | yes |
| diagnostic_campus_factor | 4044.57 | yes |
| member_cost_share_netting | 3971.86 | yes |
All-baseline 2096.92.
T2 (diagnostic_campus_factor with every other factor at baseline):
- On the task-1 world (Neenah) it gives 2264.10 against the all-baseline 2096.92.
- On a Chilton world it gives 1963.18 against an all-baseline of 2096.92.

Grids and sweeps (P5 compute via check_compute.build_env on the task-1 world):
- CT x contrast x payer x campus grid. Inputs: HMO/PPO/Marketplace x {Neenah, Appleton, Chilton} x 71275 {none, 0.01, 50, 100, 500, 700, 741.99, 742, 797.99, 798, 798.01, 850, 1000, 3480, 6000} x units {1, 2} x Q9967 {0, 1, 10, 80, 200} ml, 1350 points. Result: 0 family-value falls, 0 refund rises on either axis, 0 cap breaches (family value <= scan + contrast charges).
- Per-line both-axes sweep. Every charge line x the same 3 payers x 3 campuses, quantity 1-8 and unit charge 0.01-8000.00: 6993 points, 0 refund rises, 0 retained values above the diagnostic charges.
- Cross-task exclusivity: P5 on task 0's claim gives 0.00. The task-0 policies are untouched.

Probe table (80 ml = 88.00 unless stated):
| payer | campus | 71275 | contrast | family value | refund |
| --- | --- | --- | --- | --- | --- |
| PPO | Neenah | 3480.00 | 88.00 | 798.00 | 3949.82 |
| PPO | Neenah | 700.00 | 88.00 | 788.00 | 3959.32 |
| PPO | Neenah | 500.00 | 88.00 | 588.00 | 4149.32 |
| PPO | Neenah | 100.00 | 200 ml 220.00 | 320.00 | 4403.92 |
| PPO | Neenah | none | 200 ml 220.00 | 128.70 | 4585.65 |
| PPO | Neenah | none + 70450 1000.00 | 88.00 | 51.48 | 4103.26 |
| HMO (task 1) | Neenah | 3480.00 | 88.00 | 775.60 | 4121.86 |
| HMO | Appleton | 3480.00 | 88.00 | 775.60 | 4044.57 |
| HMO | Chilton | 3480.00 | 88.00 | 775.60 | 3461.90 |
| Marketplace | Neenah | 3480.00 | 88.00 | 1694.80 | 2688.98 |

Gold move (task 1 only): step 8, refund_payer_recovery_9b1903be amount_usd, moved 4044.57 -> 4121.86.
- New figure: 5440.52 - (1545.9535 x 0.95 - 150.00).
- Steps 10, 12 and 14 are unchanged (12.33 / 45.00 / 2317.43); the recovery limits loosen and do not bind.
- The terminal payer_balance moved 1757.81 -> 1835.10.
- tasks/1.json was updated in place:
  - The value appears in evaluation_criteria[8] (argument and tracing), the recovery mentions in [10] and [14], solvability_contract, prerequisite_closure flips_to_true_by, and computations[1]/[3] traces (limit 4109.53).
  - computations[0] was updated: expected, factor_trace, and factor_sensitivity (the two merged entries replaced by ct_angiography_family_pricing "a Commercial HMO claim" 3096.09 and diagnostic_campus_factor "the services were at Riverbend Lakeshore Hospital - Neenah" 4044.57; the other four figures recomputed).
  - The design_rationale REFUND, FACTOR STRUCTURE, REALISM and payer-balance lines were updated.
- tasks/0.json is byte-identical (4e988804d476). task_tools.py is unchanged.
Gates (replay with --check): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK.
REWORK round 12: gates 7/7 green

## REWORK round 13 (policy_kb revision_1: src-1, src-2, src-3)
Read in full: audits/policy_kb/insurance_claims_and_denials/0.md, 1.md, _difficulty.md. kb-1..kb-4 are render-only (the renderer handles them) and are not touched here. Read for src-1: docs/encounter/insured_account_payoff_in_full, insured_payoff_amount_calculation, insured_payoff_days_to_pay_schedule, insured_payoff_paperless_allowance, insured_payoff_liability_size_points, insured_payoff_noncovered_share_points, check_in_payment_allowance_insured, insured_estimate_variance_credit, prompt_pay_terms.

src-1 (seed, task 0) - closed, seed-only:
- The ED account 33a1a49e is COMMERCIAL, so it is insured and paid off in full under the published insured payoff rule.
- I verified the price from the records:
  - Balance standing 420.00 (DEDUCTIBLE liability).
  - Emergency Department class 10%; window 30 days; minimum 100.00 met.
  - Days to pay: 12 (first statement 2025-12-08 -> payment 2025-12-20) -> +2 points.
  - Latest summary statement via PATIENT_PORTAL -> +1 point.
  - Liability total 420.00 -> none. Non-covered share 0 -> none. No point-of-service payment -> none. No linked insured estimate -> no dollar credit.
  - Result: 13% of 420.00 = 54.60 discount, payment 365.40. This matches the auditor's derivation.
- Rows changed in initial_state and db_closure:
  - encounter_transactions 6a39fe5d (encounter_payment_posted): 378.00 -> 365.40.
  - d181e508 (PROMPT_PAY_DISCOUNT, sourced to that payment): 42.00 -> 54.60.
- Dependent rows stay consistent: the account's patient_balance is 0.00 = 420.00 - 365.40 - 54.60, and it is still closed 2025-12-20. The claim 14955304 rows are unchanged (PR-1 420.00).
- solvability_contract seed_consistency[9] was re-worded to the insured payoff derivation.
- No task-0 policy reads payments or adjustments on another account, so gold is unchanged.

src-2 (seed, both tasks) - not seedable under the frozen schema and base rules. Why, exactly:
- A real 835 for these items reports them as PR-204, because each payer class carries noncovered_waiver_required: true. The items are the take-home convenience items E0218/A9273/A4467 on the PPO claim (623.00) and the self-administered drugs J8499/J8540/J7613 on the HMO claim (88.00). The RARC would be N130, consult plan benefit documents.
- Base claim_denial_routing says: "A PR-204 non-covered amount is released to the patient only when the noncovered_waiver_form signed before the service is on file (noncovered_waiver_required); without it the amount is written off as NONCOVERED_NO_WAIVER." On these worlds no waiver is on file (no non-covered-service liability), so that remittance line is posted by the NONCOVERED_NO_WAIVER write-off, which is the still-owed action tasks 0 and 1 test.
- The frozen claim_transactions model has no row that records a reported-but-unposted remittance line. The only remittance rows are:
  - claim_payment_posted (payment);
  - claim_contractual_adjustment (fields fixed to carc CO-45, and it moves the amount off the payer balance);
  - claim_patient_resp_transferred (a PR line released to the patient);
  - claim_secondary_crossover.
  Amounts are positive magnitudes; 0.00 is allowed only for corrections and appeals.
- Each way of making the seed balance breaks the task:
  - Posting the line as claim_patient_resp_transferred PR-204 (plus the encounter NONCOVERED_SERVICE liability) releases the items to the patient. That contradicts the routing sentence (no waiver), and it switches off the write-off: P3 and P7 apply only "on an account that carries ... no non-covered patient liability".
  - Posting the line as a contractual adjustment (CO-45 or CO-96) takes the amount off the payer balance before the write-off. The write-off would then double-count, leaving payer_balance -623.00 / -88.00.
  - A 0.00 marker row violates the amount format.
- So the remittance can only balance at the moment the write-off posts.
- Closest realistic seed: the current one. It reads as "835 received; its PR-204 non-covered line awaits routing, and with no waiver on file its posting is the NONCOVERED_NO_WAIVER write-off". payer_balance 623.00 / 88.00 is exactly that unposted PR-204 amount, and the other remittance lines (payment, CO-45, PR-3) balance to the rest.
- Proposals beyond this difficulty's write territory, not applied:
  - (a) A blueprint-level remittance-line event, e.g. a non-covered line reported with carc PR-204/CO-96 and remit trace/date that does not move payer_balance, or remit_trace_number/remit_date on claim_denial_written_off. Either would let the ledger show the 835 line before routing.
  - (b) Within this charter, the two non-covered write-off tools could carry carc PR-204 (the line's own code) instead of the claim's current denial code. That is a rule-plus-tool change with the same amounts; I am not applying it this round because the coordinator asked for seed-only.
- Gold unchanged.

src-3 (rule wording, P1 blood_bank_typing_handling) - closed:
- Rule sentence (and its three verbatim compute_basis copies): "The blood-bank typing codes keep no value of their own when a Commercial PPO claim bills code 29882 under revenue code 0360 (Riverbend's PPO agreements bundle pre-operative typing with that knee procedure), are valued ...". It no longer names "the arthroscopy case rate" or "the procedure that case rate pays".
- Ladder tier: when "a Commercial PPO claim AND code 29882 billed under revenue code 0360", method "bundled with that procedure under the PPO agreements: no value".
- tasks/0.json factor_sensitivity tier_taken label for this factor was updated to the new tier text (forced; label only, figure 11023.78 unchanged).
- The compute is identical (all 8 policies' compute and params are parsed-identical to round 12). A re-render of blood_bank_typing_value_on_surgery_refunds follows.

Regression:
- Touched policy P1 per-line both-axes sweep (task-0 account, PPO/HMO/Marketplace, quantity 1-8, unit charge 0.01-8000.00): 1872 points, 0 refund rises.
- Cross-task exclusivity: every task-1 policy is 0.00 on task 0's claim, and every task-0 policy is 0.00 on task 1's claim; P1 on its own world is 11058.88.
- Gold unchanged: 11058.88 / 38.30 / 312.56 / 9111.77 and 4121.86 / 12.33 / 45.00 / 2317.43.
- tasks/0.json changed only as above (src-1 seed rows, seed_consistency[9], tier label); 6769ef6a9d7a.
- tasks/1.json is byte-identical (b6a28533b8d1). task_tools.py is unchanged.
Gates (replay with --check): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK.
REWORK round 13: gates 7/7 green
