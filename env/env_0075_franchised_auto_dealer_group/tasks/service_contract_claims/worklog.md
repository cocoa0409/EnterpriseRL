# worklog — service_contract_claims (env_0075, vsc, M=2)

## 2026-10-22 resume (fresh relaunch after account cut)
- On disk at start: plan.md (draws recorded: t0 prereq=2 factors [5,6,4]; t1 prereq=2 factors [5,6,5]), vsc.extended.yaml, task_tools.py; scratch /tmp/service_contract_claims_0075/ has pol_t0.py, world_t0.py, t0_build.py, run_t0.py, evalc.py, ids_t0.json.
- Missing: tasks/0.json, tasks/1.json, per-task and final gates.
- Plan: adopt predecessor design; verify extended/tool gates first, then build task 0 from scratch scripts.

## Task 0 — resume fixes (before writing 0.json)
- Gates at resume: TASK TOOL CONTRACT OK; EXTENDED red only for missing tasks.
- XF review of the 3 task-0 policies -> changes (source pol_t0.py, rebuilt with build_ext.py):
  - B0 deductible ladder departs from base "once per component group repaired" for per_repair levels -> declared a 5th scoped overwrite of the base deductible clause; s6 now opens "For a line this policy reimburses, and only for such a line, ...".
  - Removed two framing clauses asserting facts no record holds (XF 11): "so refrigerant or coolant was recovered" (B0 hazwaste), "so the holder was waiting on the claim decision" (A0 start day).
  - B0 compute ignored the rule's "sold on its vehicle's purchase deal" scope -> added sold_on_deal binding into result's guard; denial reads scoped to claim_line_type component_repair.
  - A0 account tier/status and R0 plan_status read first match -> keyed on status='active' (decoy-safe for a closed second account / cancelled earlier plan).
- Seed realism (XF 20): the predecessor's Kessler Care visit 1 (2026-10-16, 938 mi after sale, 56 days) is NOT producible (maintenance_evt visit needs 4000 mi or 60 days since last visit) -> moved visit to 2026-10-20 (day 60) at 42996; request moved to 2026-10-21 (signed this morning, 08:47) certifying 42950. Re-tuned so time and mileage shares sit 0.0003 apart: every R0 factor bites (T1). Added in-force Federal Emissions Performance Warranty and expired Factory Complimentary Maintenance rows (Hyundai 2021 would carry them).
- Run (run_t0.py): B0 1667.15 (factor baselines 1720.79/1727.77/1816.15/1567.15/1638.18/1663.51; all-baseline 1797.80); A0 45.00 (90/90/225/50; 350.00); R0 3780.75 (3781.95/3777.11/3779.81/3767.02/3730.75; 3714.88). Skip B0 -> R0 3755.75 (fee 25.00 Kessler Care holder fee instead of 0.00).
- R0 rental prerequisite sentence (u2) rewritten so the wait is unmet at the opening, not vacuously true: it now names claims whose component line was paid OR denied for the waiting period on a deal-sold contract (CLM-4471208 qualifies at the opening and lacks its rental line).
- Wrote scratch t0_text_{a,b,c}.py (missing at resume) and built tasks/0.json with t0_build.py.
- Gate reds fixed: replay dangling FKs (loaner vehicle customer_id "" -> None; plan load row store_id "" -> selling store); solvability intent_source kinds (initial_state / prior_step / user_scenario) and R0 discriminator value customer_request.
- Task 0 per-task gates: EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK (cache-diff info only). XF sweep (basis/baseline verbatim, replaced_by in rule, factor-id/tool-name, factor independence, VIN check digits, frozen_time format): OK.
- Manual values gates (task 0): long/broad = 3 problems over 5 charters' records; owner=user = holder's acceptance of his own signed cancellation (in-person semantics: lifecycle active->cancelled by user); no real-world wait (repair, payment, loaner return all before the opening; claim lines are synchronous ledger writes); persona volunteers only the goal; prerequisite sentences: u1 affirmative 'only after', u2 negated 'not ... until', t1 affirmative 'only after' — each record-visible, exactly one writer each.

## Cross-task prose hygiene (applies to task 0 too)
- XF 13 sibling overwrites: B0/B1/C1 overwrite the same base claim-payment clauses and R0/R1 the same refund clauses -> every replaced_by and every rule sentence now names its own case ("For a waiting-period re-decision line", "For a maintenance re-decision line", "For a coverage re-decision line", "For a kept-vehicle refund", "For a traded-vehicle refund"); B0's hazardous-waste sentence no longer refers to "the same labor proportion" (self-contained). Task 0 rebuilt; values unchanged.

## Task 1 — authoring (pol_t1.py)
- Design moved from the predecessor sketch (see plan.md "Task 1 — design"): V1 partial recovery infeasible at 5 record-backed factors; root is a traded-vehicle refund. Tree: R1 (user, 5) -> B1 (value_input on redecided_count / fee) and R1 -> C1 (state_gate); B1, C1 independent (different ROs), so they commute.
- Tools generated (uuid4 each): reimburse_maintenance_denial_repair_6315e699, reimburse_coverage_denial_repair_73971dca, accept_traded_vehicle_cancellation_f71aca80. TASK TOOL CONTRACT OK (6 tools).
- R1: measure-day factor would feed an elapsed-rounding factor transitively (XF A.1) -> R1 carries no elapsed-rounding factor; its 5 factors are measure day (method), reading, miles start, credited days, fee.
- Task 1 world (world_t1.py): Gabriel Navarro, KS-4426107 Exclusionary on a 2020 Pilot (deal KHB-24-40517, delivered 4 days after sale at 36893), RO 446908 water pump (Silver pricing at KHB 172/h; goodwill 45.00; diag credited 50%), RO 447652 engine + brake pads (discount cap 50.00 shared, goodwill 100.00), Kessler Care Plus 6-Visit with 5 visits >= 4000 mi apart, trade deal KHB-26-41862 (appraisal 2026-09-26 at 73684, contracted 2026-09-28), request 2026-10-19 certified 73520. Lesser-of tuned: time 0.509858 vs mileage 0.509453.
- Run: C1 1080.91 (1107.57/1125.91/1166.91/1040.39/1075.96; all-baseline 1193.10); B1 6783.37 (6823.05/6883.37/6869.37/6683.37/6737.29/6778.80; 6858.40); R1 2035.27 (1990.94/2036.88/2032.98/2028.13/1985.27; 1932.19). Skip B1 -> R1 2010.27; skip C1 -> R1 unchanged, row missing; C1/B1 commute (both orders identical).
- Gate reds fixed: compute tuple syntax (`not in (None, '')`) -> explicit comparisons; B1 deductible factor declared cross_difficulty service without a service read -> ro_store moved into the factor's bindings.
- Cross-lighting check: A0's compute lacked the rule's "drove a Kessler loaner" scope -> added on_loaner guard (A0 = 0.00 in task 1's world after the repayments; B0, B1, C1 = 0.00 in the other task's world). Task 0 rebuilt; values unchanged.
- Task 0 seed note: deal KHB-26-41087 delivered 7 days after contract (past the 5-day window) — recorded in seed_consistency as a late delivery the buyer accepted (no late-delivery waiver used).

## Final suite (both tasks)
EXTENDED OK / TASK TOOL CONTRACT OK / REPLAY OK / SOLVABILITY OK / COMPUTE OK (suite means branches 97.50, steps 21.00; history_rows_max 8; branches_max 102) / GROUNDING OK / SCOPE OK. XF sweep OK (basis/baseline verbatim, replaced_by in rule, no factor id in a tool name, no factor reads another factor's binding, VIN check digits + band-4 serials, frozen_time format). Personas carry no computed figure and no prerequisite noun. check_traceability deferred to after KB render.
- Manual values gates (task 1): tree R1 <- {B1 value_input, C1 state_gate}; owner=user = the holder's acceptance of his own signed cancellation; no real-world wait (repairs, payments, trade, appraisal all before the opening; repayment lines are synchronous ledger writes); persona volunteers only the trade-in, the signed cancellation and the refund question; prerequisite sentences r1 negated ('is not computed until'), r2 affirmative ('is fixed only after'), each record-visible with exactly one writer; known residue: B1/C1 pricing ladders share the waiting-period re-decision's kinds (labor/parts/diagnostic/fee shares) because the charter prices any re-decided customer-paid line from the same store rows — each sentence names its own case.
- Scratch authoring scripts in /tmp/service_contract_claims_0075/ deleted.
REWORK round 1: gates 7/7 green

## Rework round 2 (audit revision_1: task0=RED task1=PASS charter=RED-C1..C7; task-0 F0-1, F0-2)
Plan (per item):
- RED-C1 deductible ladders (waiting, maintenance): tier 2 -> per-visit levels take the deductible less the contract deductibles the store already billed the holder on that RO; tier 3 per-group once. Both worlds stay on tier 1 (no gold change).
- RED-C2 / F0-1 kept elapsed method: condition moves to the contract form (coverage level): Exclusionary / Exclusionary Wrap whole 30-day periods (part not counted), Preferred / Select a started period counted whole, otherwise days. Task 0 (Exclusionary) -> 60 days (gold unchanged). [corrected in round 3: an earlier draft of this line named the holder's state of residence, which the DSL cannot read]
- RED-C3: six supplies/waste share factors relabelled method.
- RED-C4: re-decision scopes take the contract's latest denial of their reason (tie: first in history); diagnostic fee on exactly one concern line; maintenance proof = latest non-reinstated visit of the vehicle's active plan; plan reads keyed on status; trade deal keyed on New Vehicle Retail Purchase in closed status; RO reading = RO whose labor closed last; tie and month counting stated.
- RED-C5: every replaced_by names its siblings and restates base for every other case.
- RED-C6: refund waits restated as the exact record tests of their resolvers' scopes; rental pays at least one day where the holder was charged daily rental, and the kept wait names only such claims on levels with a rental benefit.
- RED-C7: re-decision guards add coverage switch, term, waiting period, prior authorization (labor closed on/after the claim decision), customer-pay labor present; waiting/coverage scopes limited to groups not internally lubricated.
- Tools: half-up cents helper (class static), format checks per docstring.
- Charter edits applied (scratch e_b0/e_b1/e_c1/e_a0/e_r0/e_r1.py over lib.py/edit.py): all six policies rewritten per the plan above; gold re-run unchanged on both worlds (B0 1667.15, A0 45.00, R0 3780.75; C1 1080.91, B1 6783.37, R1 2035.27; every factor_sensitivity and baseline_result figure identical). EXTENDED OK, COMPUTE OK after moving elapsed_days into the kept elapsed factor (gate needs a record read in a factor's bindings).
- Tools: class-static half-up cents helper (_Fmt.cents; no round()), format checks matching each docstring (paid lines amount > 0.00, refund >= 0.00, days >= 1, odometer >= 0, component_group / cancel_method enums, YYYY-MM-DD effective date); docstrings say "half-up to the cent" and "greater than 0.00" / "1 or more". REPLAY OK with unchanged gold.
- Task JSON proof sweep (patch_tasks.py): closure policy_source/condition re-pulled from the charter; quoted waits in necessity texts replaced (incl. a stale pre-round-1 rental quote in task 0); factor_trace lines (kept elapsed now the contract form; supplies/waste labels method; deductible near-miss); tier_taken re-pulled from the ladders; task-0 SCOPE paragraph fixed (F0-2); ROUND 2 paragraph appended to both rationales.
- Probes (probes.py, 16 decoy worlds) all agree with the round-2 rules; table in plan.md. A4 defining-sentence table generated from the charter (no sentence used by two factors). XF sweep OK; 19/19 overwrites name their scope and siblings and restate base.
- Gold: unchanged in both tasks (task 1 untouched in value; no charter fix forced a change).
- Final suite: EXTENDED OK / TASK TOOL CONTRACT OK / REPLAY OK / SOLVABILITY OK / COMPUTE OK / GROUNDING OK / SCOPE OK.
- Scratch authoring scripts in /tmp/service_contract_claims_0075/ deleted.
REWORK round 2: gates 7/7 green

## Rework round 3 (audit revision_2: task0=RED task1=RED charter=RED-C4r, RED-C5r, RED-C6r; F0-3, F1-1)
- RED-C6r.1: refund waits carve out the resolver's 0.00 cases by record tests (nil-deductible set per resolver; claims paid below the aggregate limit); in-scope lines need customer-pay labor not wholly comeback-credited (labor_charged - comeback_credit > 0 in all three re-decision guards).
- RED-C6r.2: rental and kept wait select the same claim (latest component-repair line, paid or denied, tie first listed) and the same agreement (first listed, charged daily rental); rental claim/ro reads now LATEST over component_repair lines.
- RED-C5r: rental replaced_by restates base for every rental the policy does not price.
- RED-C4r.1/.2/.3: traded measuring day and reading read the sold-or-traded refund calculation of the Kessler Care plan sold on the contract's deal (reason-keyed), tier 2 a GAP loan payoff on the waiver sold on that deal; purchase trade fields no longer read; plan reads key on purchase_deal_id; labor-closed-last tie rule stated. Task 1 world: plan KC-4431560 cancelled 2026-09-28 (request, visits_cancelled, 0.00 refund calculation at 73684); new read node find_maintenance_cancellation_requests (write steps now 16/18/20).
- Rounding: rule sentences "rounded half up to the cent"; every money RND(x + 0.000001, 2); exact-tie probe 2.475 -> 2.48.
- F0-3 / F1-1 and full proof sweep: traces (billed_deductibles), tier_taken, closure policy_source/condition/why_false, necessity quotes, seed_consistency, rationale paragraphs (ROUNDS 2-3), plan.md rows; this worklog's round-2 RED-C2 plan line corrected.
- Gold unchanged in both tasks (1667.15 / 45.00 / 3780.75; 1080.91 / 6783.37 / 2035.27), all factor and baseline figures identical; probes (plan.md round 3) agree with the rules; sweep OK.
- Final suite: EXTENDED OK / TASK TOOL CONTRACT OK / REPLAY OK / SOLVABILITY OK / COMPUTE OK / GROUNDING OK / SCOPE OK. Scratch scripts deleted.
REWORK round 3: gates 7/7 green

## Rework round 4 (audit revision_3: task0=RED task1=RED charter=RED-C6r2, RED-C9; F0-4, F1-2)
- RED-C6r2 (members a-d): the three re-decision waits now carve out only the exact 0.00 cases (deductible taken at least the line's repayable amount before the deductible; no aggregate limit left); deductible-bearing positive repayments stay inside the waits. The rental wait adds its exact 0-day case. Probe: task 0 world off the selling store -> 1567.15 owed and the waits block.
- Zero-amount ruling: the rental's one-day floor removed from rule and compute (days_paid = MN(MX(0, days_counted - free_days), ...)).
- RED-C9: every money RND is RND(x + 0.000000001, 2); 104 RND arguments over all scored, factor-sensitivity and all-baseline figures sit >= 0.000104 from a half cent; exact-tie probe 2.475 -> 2.48, near-tie 3.1449998 -> 3.14.
- F0-4 / F1-2: rationale sentences rewritten to the exact carve-out; stale epsilon / floor / max(1) proof text swept; closure policy_source, condition and why_false re-pulled; plan.md round-3 bullets marked superseded, round-4 section added.
- Gold unchanged in both tasks; all figures identical. Final suite: EXTENDED OK / TASK TOOL CONTRACT OK / REPLAY OK / SOLVABILITY OK / COMPUTE OK / GROUNDING OK / SCOPE OK. Scratch scripts deleted.
REWORK round 4: gates 7/7 green

## Rework round 5 (audit revision_4: task0=PASS task1=PASS charter=RED-C10)
- RED-C10 (4 members): the four refund waits restated in the action form with fallback_reason (a re-decision or rental benefit that owes nothing books no line, so no record state tells decided from undecided); conditions name the state the completed action leaves (a paid line where a positive amount is owed, none otherwise). No wait prices another policy's tiers; RED-C6r2 stays closed (every positive amount owed stays inside the wait); rounding and zero-amount rulings unchanged.
- Proof sweep: closure policy_source / condition / form / fallback_reason re-pulled; why_false texts, rationale problem-tree and round paragraphs, necessity quotes; plan.md round-4 bullet marked superseded, round-5 section added.
- Gold unchanged. Final suite: EXTENDED OK / TASK TOOL CONTRACT OK / REPLAY OK / SOLVABILITY OK / COMPUTE OK / GROUNDING OK / SCOPE OK. Scratch scripts deleted.
REWORK round 5: gates 7/7 green

## Rework round 6 (audit revision_5: task0=PASS task1=PASS charter=RED-C11)
- RED-C11 (4 members): each action-form wait (kept <- waiting, kept <- rental, traded <- maintenance, traded <- coverage) now carries its resolver's exact scope as plain record tests on recorded fields, with the same-day tie rule; conditions mirror the sentences and say an out-of-scope line or claim is outside the wait. Action form and fallback_reason kept; RND(x + 0.000000001, 2) and the zero-amount ruling unchanged.
- Proof sweep: closure policy_source/condition re-pulled, quoted waits replaced, rationale paragraphs updated, plan.md round-6 section.
- Gold unchanged. Final suite: EXTENDED OK / TASK TOOL CONTRACT OK / REPLAY OK / SOLVABILITY OK / COMPUTE OK / GROUNDING OK / SCOPE OK. Scratch scripts deleted.
REWORK round 6: gates 7/7 green

## Rework round 7 (audit revision_6: task0=PASS task1=PASS charter=RED-C11r)
- RED-C11r: kept <- rental wait keyed on the rental policy's own record test (claim of the latest component-repair line carrying a paid component-repair line; first-listed charged Kessler loaner; rental benefit above zero); the disjunct naming the waiting wait's line dropped, so a 0.00 waiting re-decision engages no rental wait; ordering rests on the rental policy's own state-form wait on the paid line. Class sweep: no other wait carries a disjunct beyond its resolver's scope.
- Proof sweep: rule sentence, condition, closure policy_source/condition/why_false, necessity quotes, rationale (ROUND 7 paragraph, problem-tree opening note), plan.md round-7 section.
- Gold unchanged. Final suite: EXTENDED OK / TASK TOOL CONTRACT OK / REPLAY OK / SOLVABILITY OK / COMPUTE OK / GROUNDING OK / SCOPE OK. Scratch scripts deleted.
REWORK round 7: gates 7/7 green

## Rework round 8 (audit revision_7: task0=RED task1=PASS charter=RED-C12; F0-5)
- RED-C12 / F0-5: kept <- rental keyed on record tests present at the opening (latest component-repair line's claim, paid or denied; first-listed Kessler loaner charged daily rental; rental benefit above zero), so it is engaged and unmet at task 0's opening; the rental policy's rule now settles every claim in that wait (no paid component-repair line -> settled with nothing owed, no line). Action form + fallback_reason kept. Probes: opening engaged/unmet; 0.00 waiting re-decision -> rental settled at nothing owed (one reading); after the repayment the rental owes 45.00. RED-C11/C11r stay closed.
- Proof sweep: rule sentences, condition, task-0 closure policy_source/condition/why_false, necessity quotes, rationale (ROUNDS 7-8 paragraph, problem-tree note), plan.md round-8 section.
- Gold unchanged. Final suite: EXTENDED OK / TASK TOOL CONTRACT OK / REPLAY OK / SOLVABILITY OK / COMPUTE OK / GROUNDING OK / SCOPE OK. Scratch scripts deleted.
REWORK round 8: gates 7/7 green

## Rework round 9 (renderer render_r1 F1-F5)
- F1 rental start tier 2 tests the loaner went out on the diagnosis day. F2 refund fee tiers: latest denied component-repair line, repaid later on the same claim, RO and group (COUNT kept as the gate binding). F3 already_repaid keyed on claim, RO and group in all three re-decisions. F4 plan/GAP lookups skipped for a contract sold on its own. F5 starting-odometer tiers only for sale-date terms. Class sweep also removed the untested "under an Owner Rewards ... discount" wording from labor/parts tiers.
- Gate reds hit and fixed: unknown name (already_repaid before ro/denied_group -> reordered); traded history not load-bearing / history_rows_max 6 (redecided_count back to a COUNT with the later-date test).
- Proof sweep: changed sentences replaced in both tasks' quotes, closure policy_source/condition re-pulled, tier_taken refreshed from ladders, ROUND 9 paragraph in both rationales, plan.md round-9 section with probes.
- Gold unchanged. Final suite: EXTENDED OK / TASK TOOL CONTRACT OK / REPLAY OK / SOLVABILITY OK / COMPUTE OK / GROUNDING OK / SCOPE OK. Scratch scripts deleted.
REWORK round 9: gates 7/7 green

## Rework round 10 (audit revision_9: task0=PASS task1=PASS charter=RED-R9a, RED-R9b)
- RED-R9a (2 members): "later paid" same-day convention stated in both refund fee tiers (on or after the day of the denial) and compute changed to repaid_day >= denied_day. Probe: same-day denial and repayment -> fee 0.00.
- RED-R9b (1 member): rental tier 2 names the claim's latest denial by decision date (= compute LATEST). Probe: a second denial on 09-11 starts the window 09-11.
- Proof sweep: changed sentences in quotes, fee tier_taken refreshed, ROUND 10 paragraph in both rationales, plan.md round-10 section.
- Gold unchanged. Final suite: EXTENDED OK / TASK TOOL CONTRACT OK / REPLAY OK / SOLVABILITY OK / COMPUTE OK / GROUNDING OK / SCOPE OK. Scratch scripts deleted.
REWORK round 10: gates 7/7 green

## REWORK round 11 (seed-only, SRC-1, SRC-2, SRC-3)
- SRC-1: RO 446215 authorized estimates seeded (A 1634.54 on 2026-09-09 inside the Gold 30-day window from the 2026-09-08 diagnosis, so the 149.00 diagnostic credit is producible; B 273.70 on 2026-09-12; billed = estimates). Gold read added (task 0 step 10).
- SRC-2: plan refund calculation 0.00 -> 85.95 (86.93 pro rata - 0.00 trade-up fee [Passport price posted on the effective date] - 10.98 bundle recapture + 10.00 Silver credit); refund paid 85.95 to lienholder 2026-10-06. VSC reads only the date/odometer, so no scored value moves.
- SRC-3: purchase_transactions seeded for all three deals per the published purchase rules (IN 7% / OH 6.75% tax, OH new-vehicle trade credit; doc fee KHR 233 / KHB 299; e-filing 24.00); each deal nets to 0.00 by its closing. KHB-26-41862 payoff 11842.37 -> 23618.42 (positive equity has no posting; 18.42 negative equity posted). Gold reads added; step indices shifted (task 0: 14/19/23; task 1: 18/20/22) and proof text swept.
- Same-class check: every customer-pay RO line in both worlds has an authorized estimate; all deals closed at 0.00/0.00; no other plan refund rows.
- Hashes: vsc.extended.yaml 3cfdcd5e20ef, task_tools.py 3fa9c534c04c (unchanged). Gold unchanged: 1667.15 / 45.00 / 3780.75; 1080.91 / 6783.37 / 2035.27.
REWORK round 11: gates 7/7 green